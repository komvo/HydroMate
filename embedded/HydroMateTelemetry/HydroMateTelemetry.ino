#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>
#include <math.h>
#include <time.h>
#include "sensor_config.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

// Derived from Documentos PDC/tests/PruebaSensores1.ino. No actuator outputs.
constexpr uint8_t TEMP_PIN = 4, FLOAT_PIN = 27;
constexpr float PH_M = -5.579f, PH_B = 14.066f;
constexpr unsigned long SAMPLE_MS = 30000, RETRY_MS = 5000;
constexpr uint64_t RANGE_SIZE = 100;
OneWire oneWire(TEMP_PIN);
DallasTemperature temperatureSensor(&oneWire);
BH1750 lightSensor;
Adafruit_ADS1115 ads;
Preferences storage;
WiFiClient plain;
WiFiClientSecure secure;
PubSubClient mqtt;
bool adsReady = false, lightReady = false, halted = false;
uint64_t nextSequence = 0, limitSequence = 0, pendingSequence = 0;
String pending, telemetryTopic, ackTopic;
unsigned long lastSample = 0, lastRetry = 0, lastConnect = 0;
unsigned long lastWifiRetry = 0;
int lastWifiStatus = -1;

void halt(const char* reason) {
  halted = true;
  Serial.printf("HALT: %s. Revisar antes de reiniciar.\n", reason);
}

bool reserveRange() {
  uint64_t start = storage.getULong64("limit", 1);
  if (start == 0 || start > 9223372036854775807ULL - RANGE_SIZE) return false;
  uint64_t end = start + RANGE_SIZE;
  if (storage.putULong64("limit", end) != sizeof(uint64_t)) return false;
  nextSequence = start;
  limitSequence = end;
  return true;
}

void received(char* topic, byte* data, unsigned int length) {
  if (String(topic) != ackTopic || pending.isEmpty()) return;
  JsonDocument ack;
  if (deserializeJson(ack, data, length) || !ack["sequence"].is<uint64_t>()) return;
  if (ack["sequence"].as<uint64_t>() != pendingSequence) return;
  const char* status = ack["status"] | "";
  if (strcmp(status, "stored") == 0) {
    // Remove only after API persistence confirmation. Re-delivery remains identical.
    if (!storage.remove("pending")) { halt("No se pudo retirar pendiente de NVS"); return; }
    Serial.printf("STORED sequence=%llu uptime_ms=%lu\n", pendingSequence, millis());
    pending = "";
  } else if (strcmp(status, "rejected") == 0 || strcmp(status, "conflict") == 0) {
    halt("API rechazo/conflicto: pendiente conservado, no renumerar");
  }
}

void sample() {
  temperatureSensor.requestTemperatures();
  float temp = temperatureSensor.getTempCByIndex(0);
  float lux = lightReady ? lightSensor.readLightLevel() : -1;
  float voltage = NAN;
  if (adsReady) {
    ads.setGain(GAIN_TWOTHIRDS);
    ads.readADC_SingleEnded(0);
    float sum = 0;
    for (int i=0; i<10; i++) {
      sum += ads.computeVolts(ads.readADC_SingleEnded(0));
      delay(10);
    }
    voltage = sum / 10.0f;
  }
  float ph = PH_M * voltage + PH_B;
  bool water = digitalRead(FLOAT_PIN) == LOW;
  bool tempValid = isfinite(temp) && temp != DEVICE_DISCONNECTED_C && temp >= 0 && temp <= 50;
  bool lightValid = isfinite(lux) && lux >= 0 && lux <= 100000;
  bool phValid = isfinite(ph) && ph >= 0 && ph <= 14 && isfinite(voltage) && voltage > 0.05f && voltage < 3.3f;
  float tds = NAN;
  bool tdsValid = false;
  if (HYDROMATE_TDS_SENSOR_ENABLED && adsReady && tempValid) {
    float raw = ads.computeVolts(ads.readADC_SingleEnded(HYDROMATE_TDS_ADC_CHANNEL));
    if (isfinite(raw) && raw > 0.05f && raw < 2.3f) {
      float compensated = raw / (1.0f + 0.02f * (temp - 25.0f));
      tds = (133.42f * powf(compensated, 3) - 255.86f * powf(compensated, 2) + 857.39f * compensated) * 0.5f * HYDROMATE_TDS_CALIBRATION_FACTOR;
      tdsValid = isfinite(tds) && tds >= 0 && tds <= 1000;
    }
  }
  if (!tempValid || !lightValid || !phValid) Serial.println("SENSOR_INVALID: muestra parcial; campos afectados null, nunca cero inventado");
  if (nextSequence >= limitSequence && !reserveRange()) { halt("No se pudo reservar secuencia"); return; }
  pendingSequence = nextSequence++;
  JsonDocument doc;
  doc["message_version"] = 3;
  doc["device_id"] = DEVICE_ID;
  doc["sequence"] = pendingSequence;
  doc["reason"].to<JsonArray>().add("periodic_poc");
  doc["water_present"] = water;
  auto sources = doc["sources"].to<JsonObject>();
  auto sensor = [&](const char* key, float value, bool valid, bool available) {
    if (valid) doc[key] = round(static_cast<double>(value)*100.0)/100.0;
    else doc[key] = nullptr;
    sources[key] = valid ? "real" : (available ? "invalid" : "unavailable");
  };
  sensor("temperature_c", temp, tempValid, true);
  sensor("light_lux", lux, lightValid, lightReady);
  sensor("ph", ph, phValid, adsReady);
  sensor("tds_ppm", tds, tdsValid, HYDROMATE_TDS_SENSOR_ENABLED);
  sources["water_present"] = "real";
  doc["ec_us_cm"] = nullptr; // No independent EC probe/driver selected; do not infer EC from ppm.
  sources["ec_us_cm"] = "unavailable";
  time_t acquired = time(nullptr);
  if (acquired >= 1704067200) {
    struct tm utc;
    gmtime_r(&acquired, &utc);
    char timestamp[21];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &utc);
    doc["captured_at"] = timestamp;
  } else doc["captured_at"] = nullptr;
  serializeJson(doc, pending);
  if (storage.putString("pending", pending) != pending.length()) { halt("No se pudo guardar pendiente"); return; }
  Serial.printf("SAMPLE sequence=%llu uptime_ms=%lu\n",pendingSequence,millis());
  Serial.println(pending);
  lastRetry = millis() - RETRY_MS;
}

void setup() {
  Serial.begin(115200);
  pinMode(FLOAT_PIN, INPUT_PULLUP);
  Wire.begin(21,22);
  temperatureSensor.begin();
  lightReady = lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  adsReady = ads.begin(0x48, &Wire);
  if (!storage.begin("hmtelemetry", false)) { halt("NVS no disponible"); return; }
  if (!reserveRange()) { halt("Reserva NVS fallida"); return; }
  pending = storage.getString("pending", "");
  if (!pending.isEmpty()) {
    JsonDocument old;
    if (deserializeJson(old, pending) || !old["sequence"].is<uint64_t>() ||
        strcmp(old["device_id"] | "", DEVICE_ID) != 0) { halt("Pendiente corrupto o identidad cambiada"); return; }
    pendingSequence = old["sequence"].as<uint64_t>();
    Serial.printf("RESTORED sequence=%llu; pendiente original conservado\n", pendingSequence);
    Serial.println(pending);
  }
  telemetryTopic = String("hydromate/") + DEVICE_ID + "/telemetry";
  ackTopic = String("hydromate/") + DEVICE_ID + "/ack";
  if (!strlen(WIFI_SSID) || !strlen(MQTT_HOST)) { halt("Completar secrets.h privado"); return; }
  if (MQTT_TLS) {
    if (MQTT_PORT != 8884) { halt("Produccion MQTT TLS requiere puerto 8884"); return; }
    if (!strlen(MQTT_ROOT_CA)) { halt("Falta CA TLS; no se usa conexion insegura"); return; }
    secure.setCACert(MQTT_ROOT_CA);
    mqtt.setClient(secure);
  } else {
    IPAddress address;
    bool parsed = address.fromString(MQTT_HOST);
    bool privateLan = parsed && (address[0] == 10 || (address[0] == 172 && address[1] >= 16 && address[1] <= 31) || (address[0] == 192 && address[1] == 168));
    if (!HYDROMATE_ALLOW_PLAIN_LAN || !privateLan) { halt("MQTT plano solo banco LAN privado con opt-in; nube requiere TLS"); return; }
    mqtt.setClient(plain);
  }
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(received);
  mqtt.setBufferSize(2048);
  mqtt.setSocketTimeout(3);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org");
  lastSample = millis() - SAMPLE_MS;
  lastConnect = millis() - RETRY_MS;
  Serial.println("Telemetria v3: sensores reales, ausencia/invalidez null; TDS opcional; sin actuadores; 30 s.");
}

void loop() {
  if (halted) { delay(50); return; }
  unsigned long now = millis();
  int wifiStatus = WiFi.status();
  if (wifiStatus != lastWifiStatus) {
    Serial.printf("WIFI_STATUS code=%d uptime_ms=%lu\n", wifiStatus, now);
    lastWifiStatus = wifiStatus;
  }
  if (wifiStatus != WL_CONNECTED && now-lastWifiRetry >= 30000) {
    lastWifiRetry = now;
    WiFi.reconnect();
    Serial.println("WIFI_RETRY");
  }
  bool clockReady = !MQTT_TLS || time(nullptr) >= 1704067200;
  if (WiFi.status() == WL_CONNECTED && !mqtt.connected() && now-lastConnect >= RETRY_MS && clockReady) {
    lastConnect = now;
    String clientId = String("hm-") + DEVICE_ID;
    if (mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
      mqtt.subscribe(ackTopic.c_str(), 1);
      lastRetry = millis() - RETRY_MS;
      Serial.println("MQTT_CONNECTED");
    } else Serial.printf("MQTT_FAIL code=%d\n", mqtt.state());
  }
  mqtt.loop();
  if (pending.isEmpty() && clockReady && now-lastSample >= SAMPLE_MS) { lastSample = now; sample(); }
  if (!pending.isEmpty() && mqtt.connected() && now-lastRetry >= RETRY_MS) {
    lastRetry = now;
    bool sent = mqtt.publish(telemetryTopic.c_str(), pending.c_str(), false);
    Serial.printf("SEND sequence=%llu accepted=%d uptime_ms=%lu\n", pendingSequence, sent, millis());
  }
  delay(10);
}

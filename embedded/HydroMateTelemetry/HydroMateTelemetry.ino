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
#include "telemetry_sensors.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

// Derived from Documentos PDC/tests/PruebaSensores1.ino. No actuator outputs.
constexpr uint8_t TEMP_PIN = 4, FLOAT_PIN = 27;
constexpr float PH_M = -5.579f, PH_B = 14.066f;
constexpr unsigned long SAMPLE_MS = HYDROMATE_PERIODIC_MS, RETRY_MS = 5000;
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
String pending, telemetryTopic, ackTopic, commandTopic;
String sampleRequestId, lastRequestId;
time_t sampleRequestExpires = 0;
unsigned long requestStarted = 0, conversionStarted = 0, lastSensorPoll = 0;
unsigned long waterCandidateSince = 0;
bool converting = false, waterCandidate = false, waterStable = false, haveSnapshot = false;
bool haveBaseline = false;
float latestTemperature = NAN;
unsigned eventChanges = 0;
hydromate::Snapshot current, baseline;
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
  if (String(topic) == commandTopic) {
    if (length>512 || !MQTT_TLS && !HYDROMATE_ALLOW_PLAIN_LAN) return;
    JsonDocument command;
    if (deserializeJson(command,data,length) || strcmp(command["action"] | "","measure")) return;
    const char* id=command["request_id"] | "";
    if (strlen(id)!=36 || !command["expires_at"].is<int64_t>()) return;
    for (size_t i=0;i<36;i++) {
      bool dash=i==8 || i==13 || i==18 || i==23;
      if (dash ? id[i]!='-' : !isxdigit(static_cast<unsigned char>(id[i]))) return;
    }
    time_t expires=command["expires_at"].as<int64_t>(), now=time(nullptr);
    if (expires<=now || expires>now+35 || lastRequestId==id || sampleRequestId==id) return;
    sampleRequestId=id; sampleRequestExpires=expires; requestStarted=millis();
    temperatureSensor.requestTemperatures(); conversionStarted=requestStarted; converting=true;
    lastRetry=millis()-RETRY_MS;
    Serial.println("SAMPLE_REQUEST received; awaiting fresh sensor acquisition");
    return;
  }
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

float readVoltage(uint8_t channel, adsGain_t gain) {
  if (!adsReady) return NAN;
  ads.setGain(gain);
  ads.readADC_SingleEnded(channel); // Discard first conversion after mux/gain switch.
  float readings[9];
  for (int i=0;i<9;i++) readings[i]=ads.computeVolts(ads.readADC_SingleEnded(channel));
  return hydromate::median(readings,9);
}

void updateTemperature(unsigned long now) {
  if (converting && now-conversionStarted>=200) {
    float temp=temperatureSensor.getTempCByIndex(0);
    latestTemperature=isfinite(temp) && temp!=DEVICE_DISCONNECTED_C && temp>=0 && temp<=50 ? temp : NAN;
    converting=false;
  }
  if (!converting && now-conversionStarted>=1000) {
    temperatureSensor.requestTemperatures(); conversionStarted=now; converting=true;
  }
}

void readSensors() {
  Wire.beginTransmission(0x48);
  bool adcPresent=Wire.endTransmission()==0;
  if (adcPresent && !adsReady) adsReady=ads.begin(0x48,&Wire);
  if (!adcPresent) adsReady=false;
  current.temperature=latestTemperature;
  float lux=lightReady ? lightSensor.readLightLevel() : NAN;
  current.light=isfinite(lux) && lux>=0 && lux<=100000 ? lux : NAN;
  float voltage=readVoltage(0,GAIN_TWOTHIRDS), ph=PH_M*voltage+PH_B;
  current.ph=isfinite(voltage) && voltage>0.05f && voltage<3.3f && ph>=0 && ph<=14 ? ph : NAN;
  float tdsVoltage=HYDROMATE_TDS_SENSOR_ENABLED ? readVoltage(HYDROMATE_TDS_ADC_CHANNEL,GAIN_ONE) : NAN;
  float compensation=isfinite(current.temperature) ? current.temperature : HYDROMATE_TDS_REFERENCE_TEMPERATURE_C;
  current.tds=hydromate::tdsFromVoltage(tdsVoltage,compensation,HYDROMATE_TDS_CALIBRATION_FACTOR);
  current.water=waterStable;
  haveSnapshot=true;
  if (haveBaseline) {
    hydromate::Thresholds limits;
    limits.light=HYDROMATE_LIGHT_CHANGE_LUX; limits.lightRelative=HYDROMATE_LIGHT_CHANGE_RATIO;
    limits.ph=HYDROMATE_PH_CHANGE; limits.temperature=HYDROMATE_TEMPERATURE_CHANGE_C;
    limits.tds=HYDROMATE_TDS_CHANGE_PPM; limits.tdsRelative=HYDROMATE_TDS_CHANGE_RATIO;
    eventChanges|=hydromate::changes(baseline,current,limits);
  }
}

void sample(const char* mode, unsigned changes, const String& requestId) {
  bool tempValid=isfinite(current.temperature), lightValid=isfinite(current.light);
  bool phValid=isfinite(current.ph), tdsValid=isfinite(current.tds);
  if (!tempValid || !lightValid || !phValid || HYDROMATE_TDS_SENSOR_ENABLED && !tdsValid)
    Serial.println("SENSOR_INVALID: muestra parcial; campos afectados null, nunca cero inventado");
  if (tdsValid && !tempValid) Serial.println("TDS_REFERENCE_TEMP c=25.00; sin compensacion termica medida");
  if (nextSequence >= limitSequence && !reserveRange()) { halt("No se pudo reservar secuencia"); return; }
  pendingSequence = nextSequence++;
  JsonDocument doc;
  doc["message_version"] = 3;
  doc["device_id"] = DEVICE_ID;
  doc["sequence"] = pendingSequence;
  auto reasons=doc["reason"].to<JsonArray>();
  reasons.add(mode);
  if (!requestId.isEmpty()) reasons.add(String("request:")+requestId);
  if (changes & hydromate::WATER) reasons.add("water_change");
  if (changes & hydromate::LIGHT) reasons.add("light_change");
  if (changes & hydromate::PH) reasons.add("ph_change");
  if (changes & hydromate::TEMPERATURE) reasons.add("temperature_change");
  if (changes & hydromate::TDS) reasons.add("tds_change");
  if (changes & hydromate::SENSOR_STATE) reasons.add("sensor_state_change");
  doc["water_present"] = current.water;
  auto sources = doc["sources"].to<JsonObject>();
  auto sensor = [&](const char* key, float value, bool valid, bool available) {
    if (valid) doc[key] = round(static_cast<double>(value)*100.0)/100.0;
    else doc[key] = nullptr;
    sources[key] = valid ? "real" : (available ? "invalid" : "unavailable");
  };
  sensor("temperature_c", current.temperature, tempValid, true);
  sensor("light_lux", current.light, lightValid, lightReady);
  sensor("ph", current.ph, phValid, adsReady);
  sensor("tds_ppm", current.tds, tdsValid, HYDROMATE_TDS_SENSOR_ENABLED);
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
  if (!requestId.isEmpty()) {
    if (storage.putString("lastreq",requestId)!=requestId.length()) { halt("No se pudo guardar solicitud NVS"); return; }
    lastRequestId=requestId;
  }
  baseline=current; haveBaseline=true; eventChanges=0; lastSample=millis();
  Serial.printf("SAMPLE sequence=%llu uptime_ms=%lu\n",pendingSequence,millis());
  Serial.println(pending);
  lastRetry = millis() - RETRY_MS;
}

void setup() {
  Serial.begin(115200);
  pinMode(FLOAT_PIN, INPUT_PULLUP);
  Wire.begin(21,22);
  temperatureSensor.begin();
  temperatureSensor.setResolution(10);
  temperatureSensor.setWaitForConversion(false);
  temperatureSensor.requestTemperatures(); converting=true; conversionStarted=millis();
  Serial.printf("SENSORS ds18b20_count=%u gpio=4; TDS ADS1115 A%u\n",temperatureSensor.getDeviceCount(),HYDROMATE_TDS_ADC_CHANNEL);
  waterCandidate=waterStable=digitalRead(FLOAT_PIN)==LOW;
  waterCandidateSince=millis();
  lightReady = lightSensor.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  adsReady = ads.begin(0x48, &Wire);
  if (!storage.begin("hmtelemetry", false)) { halt("NVS no disponible"); return; }
  if (!reserveRange()) { halt("Reserva NVS fallida"); return; }
  pending = storage.getString("pending", "");
  lastRequestId=storage.getString("lastreq", "");
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
  commandTopic=String("hydromate/")+DEVICE_ID+"/commands/measure";
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
  Serial.println("Telemetria v3: TDS A1, cambios y solicitudes; respaldo 30s; sin actuadores.");
}

void loop() {
  if (halted) { delay(50); return; }
  unsigned long now = millis();
  bool rawWater=digitalRead(FLOAT_PIN)==LOW;
  if (rawWater!=waterCandidate) { waterCandidate=rawWater; waterCandidateSince=now; }
  if (now-waterCandidateSince>=HYDROMATE_WATER_DEBOUNCE_MS) waterStable=waterCandidate;
  updateTemperature(now);
  if (!haveSnapshot || now-lastSensorPoll>=HYDROMATE_SENSOR_POLL_MS) {
    lastSensorPoll=now; readSensors();
  }
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
      mqtt.subscribe(commandTopic.c_str(), 1);
      lastRetry = millis() - RETRY_MS;
      Serial.println("MQTT_CONNECTED");
    } else Serial.printf("MQTT_FAIL code=%d\n", mqtt.state());
  }
  mqtt.loop();
  now=millis();
  updateTemperature(now);
  if (!sampleRequestId.isEmpty() && time(nullptr)>=sampleRequestExpires) {
    sampleRequestId=""; Serial.println("SAMPLE_REQUEST expired; no fabricated response");
  }
  if (pending.isEmpty() && clockReady && haveSnapshot) {
    if (!sampleRequestId.isEmpty()) {
      if (now-requestStarted>=200) {
        readSensors(); sample("requested",eventChanges,sampleRequestId); sampleRequestId="";
      }
    } else if (!haveBaseline || now-lastSample>=SAMPLE_MS ||
               eventChanges && now-lastSample>=HYDROMATE_EVENT_MIN_INTERVAL_MS) {
      sample(!haveBaseline ? "startup" : eventChanges ? "sensor_change" : "periodic_poc",eventChanges,String());
    }
  }
  if (!pending.isEmpty() && mqtt.connected() && now-lastRetry >= RETRY_MS) {
    lastRetry = now;
    bool sent = mqtt.publish(telemetryTopic.c_str(), pending.c_str(), false);
    Serial.printf("SEND sequence=%llu accepted=%d uptime_ms=%lu\n", pendingSequence, sent, millis());
  }
  delay(10);
}

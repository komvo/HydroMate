// Firmware DIDÁCTICO para la simulación en Proteus (ATmega328P a 3.3 V / 8 MHz).
// No es el firmware del proyecto (embedded/) ni el controlador final: sustituye al
// ESP32, que Proteus 8.13 no simula, para demostrar lectura de sensores y
// enclavamientos de seguridad locales. Sin red, sin MQTT, sin calibración nueva.
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>

// Equivalencia ESP32 -> ATmega328P (ver PROPUESTA.md / reporte).
constexpr uint8_t TEMP_PIN = 4;      // GPIO4  DS18B20
constexpr uint8_t LEVEL_PIN = 7;     // GPIO27 flotador, LOW = agua
constexpr uint8_t PUMP_N = 9;        // GPIO25 bomba, salida activa en bajo
constexpr uint8_t DOSE_A_N = 10;     // GPIO13
constexpr uint8_t DOSE_B_N = 11;     // GPIO14
constexpr uint8_t PH_UP_N = 5;       // GPIO18
constexpr uint8_t PH_DOWN_N = 6;     // GPIO19
constexpr uint8_t ALARM_PIN = 8;     // GPIO23, activa en alto
// Órdenes simuladas con interruptores a GND (en el sistema real llegan por MQTT).
constexpr uint8_t ORD_PUMP = A0, ORD_A = A1, ORD_B = A2, ORD_UP = A3, ORD_DOWN = 12;

constexpr float PH_M = -5.579f, PH_B = 14.066f;   // constantes históricas
constexpr unsigned long DOSE_MAX_MS = 5000UL;     // tiempo máximo por orden (supuesto)
constexpr unsigned long REPORT_MS = 1000UL;

OneWire oneWire(TEMP_PIN);
DallasTemperature temperatureSensor(&oneWire);
Adafruit_ADS1015 ads;  // modelo Proteus ADS1015: mismo mapa I2C que ADS1115, 12 bits
bool adsReady = false;

// Misma función de transferencia SEN0244 y límites que embedded/telemetry_sensors.h.
float tdsFromVoltage(float volts, float temperature) {
  if (!isfinite(volts) || volts < 0 || volts > 2.3f || !isfinite(temperature) ||
      temperature < 0 || temperature > 50) return NAN;
  float v = volts / (1.0f + 0.02f * (temperature - 25.0f));
  float ppm = ((133.42f * v - 255.86f) * v + 857.39f) * v * 0.5f;
  return ppm >= 0 && ppm <= 1000 ? ppm : NAN;
}

float readVoltage(uint8_t channel, adsGain_t gain) {
  if (!adsReady) return NAN;
  ads.setGain(gain);
  ads.readADC_SingleEnded(channel);  // descarta la primera conversión tras cambiar mux
  return ads.computeVolts(ads.readADC_SingleEnded(channel));
}

bool ordered(uint8_t pin) { return digitalRead(pin) == LOW; }
void drive(uint8_t pinN, bool on) { digitalWrite(pinN, on ? LOW : HIGH); }

struct DoseChannel { uint8_t order, out; const char* name; unsigned long since; bool locked; };
DoseChannel doses[] = {{ORD_A, DOSE_A_N, "A", 0, false}, {ORD_B, DOSE_B_N, "B", 0, false},
                       {ORD_UP, PH_UP_N, "UP", 0, false}, {ORD_DOWN, PH_DOWN_N, "DOWN", 0, false}};
bool doseOn[4];
unsigned long lastReport = 0;

void setup() {
  // Salidas en APAGADO antes de habilitarlas; las pull-ups externas cubren el reinicio.
  const uint8_t outputs[] = {PUMP_N, DOSE_A_N, DOSE_B_N, PH_UP_N, PH_DOWN_N};
  for (uint8_t pin : outputs) {
    digitalWrite(pin, HIGH);
    pinMode(pin, OUTPUT);
  }
  pinMode(ALARM_PIN, OUTPUT);
  digitalWrite(ALARM_PIN, LOW);
  pinMode(LEVEL_PIN, INPUT_PULLUP);
  const uint8_t orders[] = {ORD_PUMP, ORD_A, ORD_B, ORD_UP, ORD_DOWN};
  for (uint8_t pin : orders) pinMode(pin, INPUT_PULLUP);
  Serial.begin(9600);
  temperatureSensor.begin();
  temperatureSensor.setResolution(10);
  adsReady = ads.begin(0x48);
  Serial.println(F("HydroMate Proteus - firmware didactico (no es el controlador final)"));
  Serial.print(F("ADS1015 0x48: ")); Serial.println(adsReady ? F("OK") : F("NO RESPONDE"));
}

void loop() {
  temperatureSensor.requestTemperatures();
  float temperature = temperatureSensor.getTempCByIndex(0);
  bool tempValid = temperature != DEVICE_DISCONNECTED_C && temperature > -55 && temperature < 125;
  float phVolts = readVoltage(0, GAIN_TWOTHIRDS), ph = PH_M * phVolts + PH_B;
  bool phValid = isfinite(phVolts) && phVolts > 0.05f && phVolts < 3.3f && ph >= 0 && ph <= 14;
  float tdsVolts = readVoltage(1, GAIN_ONE);
  float tds = tdsFromVoltage(tdsVolts, tempValid ? temperature : 25.0f);
  bool tdsValid = isfinite(tds);
  bool water = digitalRead(LEVEL_PIN) == LOW;

  bool pump = water && ordered(ORD_PUMP);
  unsigned long now = millis();
  uint8_t requests = 0;
  for (auto& d : doses) {
    if (!ordered(d.order)) { d.locked = false; d.since = 0; continue; }
    requests++;
    if (!d.since) d.since = now;
    if (now - d.since >= DOSE_MAX_MS) d.locked = true;  // exige soltar la orden
  }
  bool conflict = requests > 1;  // una sola dosificación a la vez; incluye UP+DOWN
  for (uint8_t i = 0; i < 4; i++) {
    const DoseChannel& d = doses[i];
    bool sensorOk = i < 2 ? tdsValid : phValid;
    doseOn[i] = ordered(d.order) && !d.locked && !conflict && pump && sensorOk;
    drive(d.out, doseOn[i]);
  }
  drive(PUMP_N, pump);
  bool alarm = !water || !phValid || !tdsValid || !tempValid || conflict;
  digitalWrite(ALARM_PIN, alarm);

  if (now - lastReport >= REPORT_MS) {
    lastReport = now;
    Serial.print(F("T=")); tempValid ? Serial.print(temperature, 1) : Serial.print(F("INVALIDA"));
    Serial.print(F(" pH=")); phValid ? Serial.print(ph, 2) : Serial.print(F("INVALIDO"));
    Serial.print(F(" (")); Serial.print(phVolts, 3); Serial.print(F(" V)"));
    Serial.print(F(" TDS=")); tdsValid ? Serial.print(tds, 0) : Serial.print(F("INVALIDO"));
    Serial.print(F(" (")); Serial.print(tdsVolts, 3); Serial.print(F(" V)"));
    if (!tempValid) Serial.print(F(" ref25C"));
    Serial.print(F(" NIVEL=")); Serial.print(water ? F("OK") : F("BAJO"));
    Serial.print(F(" BOMBA=")); Serial.print(pump ? F("ON") : F("OFF"));
    for (uint8_t i = 0; i < 4; i++) {
      Serial.print(' '); Serial.print(doses[i].name); Serial.print('=');
      Serial.print(doseOn[i] ? F("ON") : doses[i].locked ? F("TMAX") : F("OFF"));
    }
    if (conflict) Serial.print(F(" CONFLICTO"));
    Serial.print(F(" ALARMA=")); Serial.println(alarm ? F("SI") : F("NO"));
  }
}

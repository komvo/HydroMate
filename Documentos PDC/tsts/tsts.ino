#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>

// =====================================
// PINES
// =====================================

#define ONE_WIRE_BUS 4
#define FLOAT_PIN 27

#define SDA_PIN 21
#define SCL_PIN 22

// =====================================
// OBJETOS
// =====================================

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

BH1750 lightMeter;
Adafruit_ADS1115 ads;

// =====================================
// CALIBRACION PH
// =====================================

// Calibracion obtenida experimentalmente:
// pH 6.86 -> 1.2916 V
// pH 4.01 -> 1.8024 V

const float PH_M = -5.579;
const float PH_B = 14.066;

// =====================================
// LECTURA PROMEDIO PH
// =====================================

float leerVoltajePH() {

  ads.setGain(GAIN_TWOTHIRDS);

  // Lectura de descarte despues de cambiar ganancia
  ads.readADC_SingleEnded(0);
  delay(10);

  float suma = 0;

  for (int i = 0; i < 10; i++) {

    int16_t adc = ads.readADC_SingleEnded(0);

    suma += ads.computeVolts(adc);

    delay(10);
  }

  return suma / 10.0;
}

// =====================================
// LECTURA PROMEDIO TDS
// =====================================

float leerVoltajeTDS() {

  // Ganancia alta para la señal pequeña del TDS
  ads.setGain(GAIN_SIXTEEN);

  // Lectura de descarte
  ads.readADC_SingleEnded(3);
  delay(10);

  float suma = 0;

  for (int i = 0; i < 20; i++) {

    int16_t adc = ads.readADC_SingleEnded(3);

    suma += ads.computeVolts(adc);

    delay(10);
  }

  return suma / 20.0;
}

// =====================================
// CALCULO TDS
// =====================================

float calcularTDS(float voltaje, float temperatura) {

  // Compensacion aproximada por temperatura
  // referencia: 25 C

  float compensationCoefficient =
      1.0 + 0.02 * (temperatura - 25.0);

  float compensationVoltage =
      voltaje / compensationCoefficient;

  // Formula comun para SEN0244 / TDS Meter V1.0

  float tds =
      (133.42 * compensationVoltage * compensationVoltage * compensationVoltage
      - 255.86 * compensationVoltage * compensationVoltage
      + 857.39 * compensationVoltage)
      * 0.5;

  if (tds < 0) {
    tds = 0;
  }

  return tds;
}

// =====================================
// SETUP
// =====================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("========================================");
  Serial.println("          HYDROMATE - SENSORES");
  Serial.println("========================================");

  // I2C
  Wire.begin(SDA_PIN, SCL_PIN);

  // DS18B20
  sensors.begin();

  Serial.print("DS18B20 encontrados: ");
  Serial.println(sensors.getDeviceCount());

  // Flotador
  pinMode(FLOAT_PIN, INPUT_PULLUP);

  // BH1750
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 detectado correctamente.");
  } else {
    Serial.println("ERROR: No se detecto BH1750.");
  }

  // ADS1115
  if (ads.begin(0x48, &Wire)) {
    Serial.println("ADS1115 detectado correctamente.");
  } else {
    Serial.println("ERROR: No se detecto ADS1115.");
  }

  Serial.println();
  Serial.println("A0 -> pH");
  Serial.println("A1 -> TDS");
  Serial.println();
}

// =====================================
// LOOP
// =====================================

void loop() {

  // =====================================
  // TEMPERATURA
  // =====================================

  sensors.requestTemperatures();

  float temperatura =
      sensors.getTempCByIndex(0);

  bool temperaturaValida =
      temperatura != DEVICE_DISCONNECTED_C;

  // Si no hay DS18B20, usar 25 C
  // solo para evitar romper el calculo

  float temperaturaTDS =
      temperaturaValida ? temperatura : 25.0;

  // =====================================
  // ILUMINACION
  // =====================================

  float lux =
      lightMeter.readLightLevel();

  // =====================================
  // NIVEL
  // =====================================

  int estadoFlotador =
      digitalRead(FLOAT_PIN);

  // En tu sensor:
  // LOW = agua detectada

  bool hayAgua =
      (estadoFlotador == LOW);

  // =====================================
  // PH
  // =====================================

  float voltajePH =
      leerVoltajePH();

  float ph =
      (PH_M * voltajePH) + PH_B;

  // =====================================
  // TDS
  // =====================================

  float voltajeTDS =
      leerVoltajeTDS();

  float tds =
      calcularTDS(
        voltajeTDS,
        temperaturaTDS
      );

  // =====================================
  // MOSTRAR RESULTADOS
  // =====================================

  Serial.println("----------------------------------------");

  // Temperatura
  Serial.print("Temperatura: ");

  if (temperaturaValida) {

    Serial.print(temperatura, 2);
    Serial.println(" C");

  } else {

    Serial.println("ERROR - DS18B20 no detectado");
  }

  // Luz
  Serial.print("Iluminacion: ");

  if (lux >= 0) {

    Serial.print(lux, 2);
    Serial.println(" lux");

  } else {

    Serial.println("ERROR");
  }

  // Nivel
  Serial.print("Nivel de agua: ");

  if (hayAgua) {

    Serial.println("AGUA DETECTADA");

  } else {

    Serial.println("NIVEL BAJO / SIN AGUA");
  }

  // PH
  Serial.println();

  Serial.print("pH: ");
  Serial.println(ph, 2);

  Serial.print("Voltaje pH: ");
  Serial.print(voltajePH, 4);
  Serial.println(" V");

  // TDS
  Serial.println();

  Serial.print("TDS: ");
  Serial.print(tds, 0);
  Serial.println(" ppm");

  Serial.print("Voltaje TDS: ");
  Serial.print(voltajeTDS, 5);
  Serial.println(" V");

  Serial.print("Temperatura usada para TDS: ");
  Serial.print(temperaturaTDS, 2);
  Serial.println(" C");

  Serial.println("----------------------------------------");
  Serial.println();

  delay(2000);
}
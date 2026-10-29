# Conexiones documentadas y flujo

Referencia: sketch original y bitácora física previa del 05/10; no es una nueva
medición eléctrica realizada en esta etapa.

| Elemento | Señal ESP32 | Dato |
|---|---|---|
| DS18B20 | GPIO 4, pull-up 4.7 kΩ documentado | °C |
| BH1750 | SDA 21, SCL 22, I2C | lux |
| ADS1115 | SDA 21, SCL 22, dirección 0x48 | Convierte tensión pH en A0 |
| Módulo pH | PO → ADS1115 A0 | pH = -5.579 × V + 14.066 |
| Flotador | GPIO 27, INPUT_PULLUP | LOW: agua; HIGH: bajo/sin agua |
| TDS defectuoso | No utilizado por firmware nuevo | 650 ppm simulado |

Confirmar alimentación, masa común y límites eléctricos en montaje; esta tabla
no autoriza conectar 5 V a un GPIO ni sustituye esquema eléctrico. Sin bombas.
Fuente editable: [flujo-local.mmd](flujo-local.mmd). Ensayo observado inicia en
PC sintética; recorrido físico ESP32 → Wi-Fi → broker → integrador → API → BD →
Android aún necesita prueba.

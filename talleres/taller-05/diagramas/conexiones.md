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
| TDS ausente/defectuoso | Driver opcional deshabilitado | v3: null/unavailable; no valor fijo |
| EC sin sensor seleccionado | Sin conexión adicional | null/unavailable, independiente de TDS |

Confirmar alimentación, masa común y límites eléctricos en montaje; esta tabla
no autoriza conectar 5 V a un GPIO ni sustituye esquema eléctrico. Sin bombas.
Fuente editable: [flujo-local.mmd](flujo-local.mmd). Ensayo observado inicia en
PC sintética o ESP32; recorrido físico ESP32 → Wi-Fi → broker → integrador → API
→ BD → Android comprobado localmente el 07/10 en pruebas/. Despliegue y ensayo
en nube pendientes. Las conexiones eléctricas se apoyan en la bitácora, sin nueva
medición eléctrica en esta revisión.

Actualización 14/10: firmware v3 cargado; muestra física nueva consultada en
Android con fecha, pH/temperatura/lux/flotador y TDS no disponible. JSON v3
transmite null y origen ante ausencia/invalidez. Captura de diez adquisiciones y
tiempo se registran en pruebas/, sin afirmar calibración nueva ni nube.

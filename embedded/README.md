# Firmware de telemetría del Taller 5

`HydroMateTelemetry/HydroMateTelemetry.ino` adapta el sketch original de sensores,
que permanece intacto en `Documentos PDC/tests/PruebaSensores1.ino`.
Solo adquisición y transmisión; no conecta ni gobierna salidas de bombas.

- DS18B20 GPIO 4, flotador GPIO 27 (LOW = agua).
- I2C SDA 21 / SCL 22: BH1750 y ADS1115 0x48; pH en A0.
- pH conserva M=-5.579 y B=14.066 de la prueba previa; no es nueva calibración.
- TDS fijo 650 ppm **simulado**, declarado en `sources.tds_ppm`.
- JSON v2 cada 30 s en banco; si hay pendiente no toma otra muestra para envío.
- NVS reserva secuencias por bloques de 100 y guarda un objeto pendiente antes de
  publicar. Reintenta ese mismo objeto cada 5 s hasta ACK `stored` del integrador.
- `rejected`/`conflict` detienen envío y conservan pendiente para diagnóstico.
- Sensores fuera de rango/detectados como inválidos bloquean la muestra completa;
  no se sustituyen por cero. Flotador no permite detectar por software un cable roto.
- Estado Wi-Fi se registra como código numérico sin imprimir credenciales; si no
  conecta, reintenta cada 30 s. El ESP32 requiere una red compatible con 2.4 GHz.
- No borrar NVS ni cambiar DEVICE_ID con mensajes pendientes sin reconciliar la
  identidad. Si se borra toda NVS, usar identidad nueva o reconciliar con la BD.

Dependencias observadas: ESP32 core 3.3.11; BH1750 1.3.0, OneWire 2.3.8,
DallasTemperature 4.0.6, Adafruit ADS1X15 2.6.2, BusIO 1.17.4.
Agregadas solo en `.local/arduino-libraries`: PubSubClient 2.8, ArduinoJson 7.4.2.
Fuentes de esos ZIP: [PubSubClient v2.8](https://github.com/knolleary/pubsubclient/tree/v2.8)
y [ArduinoJson v7.4.2](https://github.com/bblanchon/ArduinoJson/tree/v7.4.2).
Integrador: [documentación oficial Paho](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html).

Copiar `secrets.example.h` a `secrets.h`, excluido de Git. Configurar Wi-Fi y broker.
MQTT sin TLS es únicamente la etapa de banco LAN; para nube usar MQTT_TLS=true,
puerto TLS, CA válida, reloj sincronizado y credenciales/ACL del despliegue real.
No se usa `setInsecure()` ni hay fallback de TLS a conexión sin cifrado.

Compilar desde raíz, con Arduino CLI incluido en Arduino IDE:

```powershell
$cli = "$env:LOCALAPPDATA/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe"
& $cli compile --config-file C:/Hydromate/.local/arduino-cli.yaml --jobs 2 --fqbn esp32:esp32:esp32 --libraries C:/Hydromate/.local/arduino-libraries --build-path C:/Hydromate/.local/firmware-build C:/Hydromate/embedded/HydroMateTelemetry
& $cli board list
# Verificar puerto antes de cargar; COM3 es detección actual, no constante universal.
& $cli upload --config-file C:/Hydromate/.local/arduino-cli.yaml --fqbn esp32:esp32:esp32 --port COM3 --input-dir C:/Hydromate/.local/firmware-build C:/Hydromate/embedded/HydroMateTelemetry
& $cli monitor --port COM3 --config baudrate=115200
```

Estado de carga/ejecución física y límites de evidencia: `docs/STATUS.md`.
La configuración aislada conserva `directories.data` en Arduino15 instalado y
usa `.local/arduino-user` como sketchbook; las cinco bibliotecas de sensores se
copiaron desde la instalación existente a `.local/arduino-libraries`, sin cambiar
sus fuentes originales. Evita buscar todo el sketchbook OneDrive en cada build.
Esto no implementa el controlador final: las esperas de sensores/red se deben
separar de las tareas de seguridad antes de añadir actuadores.

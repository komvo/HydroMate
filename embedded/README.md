# Firmware de telemetría — incremento21/10/2026

embedded/HydroMateTelemetry implementa v3: DS18B20, BH1750, flotador y pH ADS1115;
TDS Meter V1.0/Gravity analógico habilitado en ADS1115 A1; EC independiente sin driver.
Ausencia/invalidez transmite null y origen; no TDS simulado de sustitución.
Conserva identidad, pendiente NVS, secuencias y ACK después de persistencia.
Copiar secrets.example.h como secrets.h privado: Wi-Fi, MQTT_HOST público
hydromate-kevin.duckdns.org, MQTT_PORT8884, cuenta MQTT, TLStrue y CA raíz emisora.
No setInsecure; espera NTP y valida CA/hostname. Compilar sin
HYDROMATE_ALLOW_PLAIN_LAN; el opt-in solo habilita banco RFC1918. Desarrollo y
configuración privada actuales permanecen independientes, sin carga automática.
Guía ../docs/PUBLIC_ACCESS.md y ../docs/INTEGRATION.md; contrato v3 en docs.

## Adquisición y envío

`HydroMateTelemetry/HydroMateTelemetry.ino` adapta el sketch original de sensores,
que permanece intacto en `Documentos PDC/tests/PruebaSensores1.ino`.
Además de adquirir y transmitir, gobierna **solo la bomba de recirculación y la alarma**. No maneja los canales de dosificación A/B/pH Up/pH Down.

## Salida: bomba de recirculación

Cableado igual al de la práctica Proteus (`Documentos PDC/T9_anexos/`):
- **GPIO25 (`BOMBA_N`), activo en bajo**, con pull-up de 10 kΩ a 3V3 → 74HCT02 a 5 V,
  `NOR(NIVEL, BOMBA_N)` → R de compuerta 100 Ω + pull-down de 10 kΩ → MOSFET → bomba 24 V,
  con diodo flyback y fusible retardado.
- **GPIO23: alarma, activa en alto** (LED con 680 Ω).
- El flotador (GPIO27) entra al ESP32 y a la NOR. **Sin agua, el hardware bloquea la bomba
  aunque falle el firmware.**

Lógica (`pump_control.h`, probada en PC con `scripts/tests/pump_control_test.cpp`):
- La bomba arranca solo después de confirmar agua durante 5 s, también tras un reinicio o al
  recuperar el nivel.
- Funciona de forma continua mientras haya agua. El ciclo ON/OFF se activa con
  `HYDROMATE_PUMP_OFF_MS > 0`. Son valores de banco, no un riego definido.
- Al perder el agua se apaga de inmediato (sin esperar el antirrebote).
- La alarma se enciende con nivel bajo, con temperatura/pH/TDS inválidos o con `HALT`.
- La tarea FreeRTOS `safety` es la dueña de los pines. Corre cada 20 ms con prioridad mayor que
  `loop()`, así que las esperas de Wi-Fi/TLS/MQTT no retrasan el corte. Si no se puede crear, los
  pines quedan en apagado.
- Serie: `PUMP state=RUNNING|WAITING_RESTART|BLOCKED_LOW_LEVEL|CYCLE_OFF alarm=0|1`.

**Límites:**
- No hay orden remota de bomba: la decisión es local y MQTT solo pide mediciones.
- El estado de la bomba no viaja en la telemetría v3; incluirlo requiere cambiar el contrato.
- `HYDROMATE_PUMP_ENABLED 0` deja la salida siempre apagada.
- La corriente de arranque real de la bomba sigue sin medirse.

- DS18B20 GPIO 4, flotador GPIO 27 (LOW = agua).
- I2C SDA21/SCL22: BH1750 y ADS1115 0x48; pH A0 y TDS A1.
- pH conserva M=-5.579 y B=14.066 de la prueba previa; no es nueva calibración.
- TDS: mediana de nueve tensiones, [fórmula SEN0244 del fabricante](https://wiki.dfrobot.com/sen0244) y factor configurable;
  compensación DS18B20 cuando válido. Si falta temperatura, referencia25°C,
  identificada en Android sin inventar una temperatura medida. EC no se deriva.
- JSON v3: respaldo cada30s y envío por cambios filtrados. sensor_config.h fija
  adquisición500ms, antirrebote del flotador150ms y separación mínima750ms.
  Umbrales de cambio: luz50lux o30% (ruido mínimo5lux), pH0.20, temperatura1°C,
  TDS50ppm o20% (ruido mínimo10ppm). No son límites de cultivo.
- DS18B20 se convierte asincrónicamente a10bits; diagnóstico SENSORS anuncia
  cantidad detectada en GPIO4. Si es inválido, temperature_c queda null.
- NVS reserva secuencias por bloques de 100 y guarda un objeto pendiente antes de
  publicar. Reintenta ese mismo objeto cada 5 s hasta ACK `stored` del integrador.
- `rejected`/`conflict` detienen envío y conservan pendiente para diagnóstico.
- Sensores inválidos transmiten null/invalid; los demás continúan. Cero es válido
  para TDS si la conversión física está dentro de rango. Flotador no permite
  detectar por software un cable roto.
- MQTT recibe exclusivamente solicitudes de adquisición en
  hydromate/hydromate-01/commands/measure, con UUID/plazo; deduplica y vence de forma
  segura, sin actuar salidas. reason incluye request:UUID en la muestra solicitada.
  Un pendiente original conserva prioridad e identidad; eventos sin red se agregan
  para enviar el estado reciente, no un historial ilimitado de transiciones.
- Estado Wi-Fi se registra como código numérico sin imprimir credenciales; si no
  conecta, reintenta cada 30 s. El ESP32 requiere una red compatible con 2.4 GHz.
- No borrar NVS ni cambiar DEVICE_ID con mensajes pendientes sin reconciliar la
  identidad. Si se borra toda NVS, usar identidad nueva o reconciliar con la BD.

Dependencias observadas: ESP32 core 3.3.11; BH1750 1.3.0, OneWire 2.3.8,
DallasTemperature 4.0.6, Adafruit ADS1X15 2.6.2, BusIO 1.17.4.
CLI aislado: PubSubClient 2.8 y ArduinoJson 7.4.2 en `.local/arduino-libraries`.
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
Esto no implementa el controlador final. La bomba ya corre en una tarea de seguridad
separada de las esperas de sensores y red; la dosificación, cuando se agregue, debe seguir
el mismo criterio e incluir límites de dosis, exclusión Up/Down y tiempos máximos.


### Arduino IDE: ArduinoJson.h no encontrado

El IDE utiliza su sketchbook (en esta PC OneDrive/Documents/Arduino), mientras
la compilación CLI aislada usa .local/arduino-libraries. Para reutilizar las dos
bibliotecas MQTT/JSON ya descargadas en el IDE, desde la raíz:

```powershell
& scripts/install_arduino_ide_libraries.ps1
```

Si el IDE usa otro sketchbook, pasar -SketchbookPath con esa ruta. El script
copia únicamente dependencias ausentes y conserva las existentes. Si el IDE
seguía abierto y no detecta la biblioteca nueva, guardar y volver a abrirlo.
Seleccionar ESP32 Dev Module y el puerto detectado, no asumir COM3 universal.
Para MQTT TLS, MQTT_ROOT_CA debe contener el PEM real con BEGIN/END CERTIFICATE,
no una descripción, ruta ni enlace. Wi-Fi/cuenta/CA permanecen en secrets.h
ignorado por Git. No borrar NVS ni cargar con opt-in MQTT plano para producción.

# Integración ESP32 → Android

Acceso público preparado: [PUBLIC_ACCESS](PUBLIC_ACCESS.md), HTTPS9443 propio y
MQTT TLS8884, variable única HYDROMATE_APP_URL. Configuración/validación externas
por administrador; esta tarea no accede al VPS.

Flujo físico comprobado21/10/2026:14 muestras nuevas consecutivas confirmadas y
mostradas en Inicio/Historial Android por HTTPS. Evidencia en
evidence/public-flow-esp32-android-2026-10-21.json. Esa prueba precede al incremento
TDS/cambios/solicitudes, cuya validación física se registra por separado en STATUS.
`127.0.0.1:8081` en la VPS es loopback de la VPS: no sirve como URL del teléfono.
Esta tarea no accede al servidor ni modifica recursos externos.

## Componentes implementados

| Tramo | Archivo / comportamiento |
|---|---|
| Entrada física | `embedded/HydroMateTelemetry/HydroMateTelemetry.ino`: DS18B20 GPIO4, BH1750 I2C21/22, flotador GPIO27 y pH ADS1115 A0 |
| Procesamiento | Medianas de tensiones y fórmula pH previa; TDS A1, límites de rango, dos decimales; invalidez null con origen |
| Transporte | Telemetry/ack y commands/measure; respaldo30s, cambios filtrados y solicitud UUID; NVS/ACK; TLS con CA y NTP |
| Integrador | `scripts/mqtt_bridge.py`: bandeja SQLite durable, POST, reintento de timeout/5xx; confirma persistencia, no solo entrega MQTT |
| Validación / registro | `StoreMeasurementRequest.php`, `MeasurementController.php` y migraciones: v1/v2 compatibles, v3 parcial, id y secuencia única, fecha de recepción y adquisición opcional |
| Consultas | Historial, última fila y estado de antigüedad en `docs/API.md`; filtro `real_only=1` |
| Android | `Telemetry.kt`, `ConnectionStore.kt`, Inicio/Historial/Conexión: HTTPS producción separado, valores reales, null, error HTTP, ausencia y telemetría antigua |
| TDS / EC | TDS real ADS1115 A1; sin DS18 válido se informa referencia25°C/no compensado. EC null hasta disponer de driver independiente |

No se controla ningún actuador. Aplazamiento comunicado por el usuario; anexar
la autorización docente a la evidencia académica. No hay nueva calibración.

## Valores que proporciona el administrador posteriormente

Compartir direcciones públicas no sensibles; introducir secretos solo en sus
archivos privados, nunca en chat, Git ni capturas públicas.

1. URL base **HTTPS** de la API, sin `/api`, certificado válido y alcance del
   GET para Android. El POST debe quedar accesible únicamente al bridge/red
   autorizada, porque aún no hay autenticación completa de dispositivos.
   El endpoint debe provisionarse sin modificar configuración `chitiito-*`.
2. Hostname público de Mosquitto y puerto MQTT TLS propio (8884 recomendado),
   certificado cuyo nombre coincida y CA de confianza. Publicación y acceso
   autorizados los resuelve el administrador fuera de esta tarea.
3. Cuenta privada `hydromate-device`, permiso de publicación solo del tópico
   `hydromate/hydromate-01/telemetry` y lectura de su ACK; cuenta privada
   `hydromate-bridge` con ACL existentes. Contraseñas se guardan en passwd
   privado del broker y en el entorno privado/firmware correspondiente.
4. `.env` exclusivamente en VPS con los nombres de `.env.example`:
   `HYDROMATE_APP_KEY` (clave Laravel existente/generada allí),
   `HYDROMATE_POSTGRES_PASSWORD` (administrador BD),
   `HYDROMATE_DB_PASSWORD` (rol aplicación) y
   `HYDROMATE_MQTT_BRIDGE_PASSWORD`. Las dos claves BD corresponden a roles
   distintos; no cambiar las de una BD ya inicializada solo editando `.env`.
5. Carpeta privada indicada por `HYDROMATE_MQTT_SECRETS_DIR` con `passwd`,
   `fullchain.pem`, `privkey.pem`, permisos adecuados. Detalles: PRODUCTION.md.

La configuración aislada actual no cambia: proyecto `hydromate`, API host8081,
PostgreSQL interno sin puerto publicado, TLS8884, listener MQTT1884 interno;
sin puertos80/443/8883, host network, volúmenes ajenos ni operaciones globales.
Android no se ejecuta en VPS.

## Arranque de producción por el ejecutor existente

Desde el checkout, el administrador utiliza su entorno privado:

```bash
docker compose -p hydromate --env-file /etc/hydromate/.env -f compose.production.yml --profile mqtt build api bridge
docker compose -p hydromate --env-file /etc/hydromate/.env -f compose.production.yml --profile mqtt up -d --wait
docker compose -p hydromate --env-file /etc/hydromate/.env -f compose.production.yml exec -T api php artisan migrate --force
```

También puede utilizar `deployment/deploy.sh`; ver PRODUCTION.md. No ejecutar
pruebas sintéticas con la identidad física contra producción. No usar prune,
reinicios globales, down -v ni reiniciar proyectos ajenos. Migración v3 preserva
filas anteriores; revisar copia de seguridad antes de aplicarla. No hay downgrade
automático de v3: podría destruir valores null de mediciones reales.

## Firmware de producción

Copiar `embedded/HydroMateTelemetry/secrets.example.h` a `secrets.h` privado.
Configurar `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_HOST`, `MQTT_PORT`, `MQTT_USER`,
`MQTT_PASSWORD`, `MQTT_TLS=true`, `MQTT_ROOT_CA` y `DEVICE_ID="hydromate-01"`.
No activar `HYDROMATE_ALLOW_PLAIN_LAN` para Internet. TLS espera reloj NTP;
sin Wi-Fi conserva pendiente y reintenta, sin renumerarla ni sustituir sensores.
Compilación/cableado: embedded/README.md y diagrama de Taller5.

## Android: desarrollo y producción

En debug, Conexión → Entorno permite dos perfiles separados. Desarrollo conserva
el banco `http://127.0.0.1:8000` por USB reverse y la demo marcada explícitamente.
Producción exige URL HTTPS, dispositivo hydromate-01 y no ofrece demo. Guardar
la conexión y actualizar Inicio; Historial muestra filas almacenadas. TDS real de
A1 aparece en ppm; si es ausente/inválido se muestra «TDS no disponible», no cero.
EC aparece si llega una lectura válida. Refrescar solicita adquisición nueva;
las vistas abiertas consultan automáticamente cada2s sin pedir más adquisiciones.
Una adquisición antigua recibida ahora se conserva antigua.

Release permite solo producción. La URL puede introducirse en Conexión o
compilarse una vez mediante la variable de entorno `HYDROMATE_APP_URL`:

```powershell
$env:JAVA_HOME='C:/Program Files/Android/Android Studio/jbr'
$env:HYDROMATE_APP_URL='https://hydromate-kevin.duckdns.org:9443'
& mobile/gradlew.bat -p mobile assembleRelease
```

El dominio anterior es un ejemplo, no un servicio de HydroMate. URL centralizada
en BuildConfig/perfil, sin claves de BD/broker en Android. Firma de distribución
definitiva permanece fuera de esta PoC; no se versiona ningún keystore.

## Validación reproducible y límites

- Backend, desde `hydromate-backend`: PHP instalado → `vendor/bin/phpunit
  --testdox`. Las pruebas usan exclusivamente SQLite en memoria.
- Bridge: Python del entorno MQTT → `-m unittest discover -s scripts -p
  test_bridge.py -v`; verifica fechas, null y rechazo de transporte público plano.
- Android: `mobile/gradlew.bat -p mobile assembleDebug testDebugUnitTest
  lintDebug assembleRelease --console=plain`.
- Pipeline sintético **solo en banco aislado**: configurar credenciales de
  prueba en variables `MQTT_USERNAME`/`MQTT_PASSWORD`, ejecutar
  `scripts/test_mqtt_flow.py --host localhost --port 8884 --ca <CA-de-prueba>
  --api http://127.0.0.1:8081 --device hydromate-01 --response-output
  .local/integration-api-response.json --output <reporte.json>`.
  La identidad física aquí solo funciona en el proyecto local
  **hydromate-validation** con valores ficticios/ACL de ensayo. El script marca
  todos los valores presentes como simulados y verifica diez registros, ACK,
  duplicado, conflicto, 422 y GET. Nunca acredita sensores.
- Fijar `HYDROMATE_TEST_RESPONSE` a la respuesta exportada y repetir
  `testDebugUnitTest --rerun-tasks`: Android comprueba esas diez filas y rechaza
  mostrarlas en producción. Es lectura del resultado real del pipeline.
- Fijar además `HYDROMATE_TEST_PHYSICAL_RESPONSE` a un GET `real_only=1` exportado
  del banco físico: Android aplica el parser de producción a datos físicos v3,
  incluidos valores invalid/null legítimos, sin exigir que todos los sensores
  sean válidos en cada fila. Es prueba del JSON, no del transporte HTTPS público.
- Ensayo físico de banco: `scripts/capture_sensor_flow.py --port COM3
  --device hydromate-01 --api http://127.0.0.1:8000 --fresh-only --target 10
  --duration 420 --output <reporte.json>`; puerto según detección real.
  Compara JSON serial/ACK con GET. No mide por sí solo sensor→pantalla.

## Evidencias de esta rama

Pruebas reproducibles y alcance en docs/evidence/public-rootless-readiness-2026-10-14.json.
Las pruebas físicas/de taller preparadas anteriormente se conservan privadamente
fuera de este diff; esta rama no reorganiza ni cambia talleres. No acreditar nube
con ensayos locales. Para cerrar el recorrido público: provisionar certificados,
configuración privada, diez adquisiciones nuevas con capture_sensor_flow, Android
producción desde red externa y verificación HTTPS/MQTT TLS según PUBLIC_ACCESS.md.

# Integración ESP32 → Android

Acceso público preparado: [PUBLIC_ACCESS](PUBLIC_ACCESS.md), HTTPS8443 propio y
MQTT TLS8884, variable única HYDROMATE_APP_URL. Configuración/validación externas
por administrador; esta tarea no accede al VPS.

Actualizado 14/10/2026. Código preparado para ESP32 → MQTT/TLS → Mosquitto →
bridge → Laravel → PostgreSQL → Android por HTTPS. El taller solo podrá cerrarse
cuando exista evidencia de este recorrido físico con el backend desplegado.
`127.0.0.1:8081` en la VPS es loopback de la VPS: no sirve como URL del teléfono.
Esta tarea no accede al servidor ni modifica recursos externos.

## Componentes implementados

| Tramo | Archivo / comportamiento |
|---|---|
| Entrada física | `embedded/HydroMateTelemetry/HydroMateTelemetry.ino`: DS18B20 GPIO4, BH1750 I2C21/22, flotador GPIO27 y pH ADS1115 A0 |
| Procesamiento | Promedio de diez tensiones de pH y ecuación de la prueba previa; límites de rango, redondeo a dos decimales; ausencia/invalidez null con origen |
| Transporte | Tópicos `hydromate/hydromate-01/telemetry` y `/ack`; 30 s, reserva de secuencias y pendiente NVS; nube TLS con CA y NTP, sin fallback inseguro |
| Integrador | `scripts/mqtt_bridge.py`: bandeja SQLite durable, POST, reintento de timeout/5xx; confirma persistencia, no solo entrega MQTT |
| Validación / registro | `StoreMeasurementRequest.php`, `MeasurementController.php` y migraciones: v1/v2 compatibles, v3 parcial, id y secuencia única, fecha de recepción y adquisición opcional |
| Consultas | Historial, última fila y estado de antigüedad en `docs/API.md`; filtro `real_only=1` |
| Android | `Telemetry.kt`, `ConnectionStore.kt`, Inicio/Historial/Conexión: HTTPS producción separado, valores reales, null, error HTTP, ausencia y telemetría antigua |
| TDS / EC | TDS deshabilitado por defecto, driver opcional ADS1115; EC null hasta seleccionar driver independiente. Ningún 650 fijo de sustitución |

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
la conexión y actualizar Inicio; Historial muestra filas almacenadas. TDS ausente
se muestra «TDS no disponible», no cero. EC aparece si llega una lectura válida.
Una adquisición antigua recibida ahora se conserva antigua.

Release permite solo producción. La URL puede introducirse en Conexión o
compilarse una vez mediante la variable de entorno `HYDROMATE_APP_URL`:

```powershell
$env:JAVA_HOME='C:/Program Files/Android/Android Studio/jbr'
$env:HYDROMATE_APP_URL='https://hydromate.example.com:8443'
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

Resultado del pipeline TLS sintético: diez filas verificadas y pruebas de fallo
pasadas en `talleres/taller-05/pruebas/integracion-v3-sintetica-2026-10-14.json`.
Recuperación local v3 tras caída de API y reinicio del bridge pasa en
`integracion-v3-recuperacion-local-2026-10-14.json`; bandeja pendiente observada,
ACK stored y fila GET idéntica. Resumen de compilaciones/pruebas/hashes:
`integracion-v3-verificacion-2026-10-14.json` en esa carpeta. Los 90 registros
históricos de desarrollo permanecen sin cambios, además de las nuevas filas físicas.
Primer ensayo físico v3 registrado en
`talleres/taller-05/pruebas/integracion-v3-fisica-fallo-regla-lan-2026-10-14.json`:
Wi-Fi conectado, pendiente NVS conservada y MQTT -2, sin diez nuevas entregas.
La IP Wi-Fi de la PC cambió; el usuario corrigió la regla local HydroMate1884
como administrador y la sesión verificó su nueva dirección. Para futuras
correcciones de esa misma regla de banco, ejecutar como administrador:

```powershell
& 'C:/Hydromate/scripts/enable_mqtt_lan.ps1'
```

El script modifica únicamente la regla de banco HydroMate1884 para Mosquitto,
IP Wi-Fi actual, LocalSubnet y perfil Private; no cambia perfiles de red globales
ni reglas ajenas, y rechaza una regla que no coincida. Repetición guardada en
`integracion-v3-fisica-local-2026-10-14.json`: diez adquisiciones nuevas1501–1510,
todas comparadas JSON serial/ACK/API; cuatro variables reales y TDS/EC null.
Pendiente1201 recuperada idéntica tras el fallo, en archivo separado; temperatura
null/invalid conservada correctamente, no se cuenta como adquisición nueva.

Inicio Android muestra fecha y valores físicos nuevos, con TDS no disponible;
Historial abierto manualmente muestra gráfica de pH y lista de20 registros;
la fila visible1701 coincide con API en fecha/pH/temperatura y TDS null.
Captura y `android-v3-historial-verificacion-2026-10-14.json` en pruebas/;
es el snapshot de la última consulta, sin afirmar polling automático.
capturas y video12s en pruebas/. Medición de una muestra1701:
`latencia-v3-android-local-2026-10-14.json`, 7571.19ms desde fin de adquisición
hasta pantalla verificada, incluidos Wi-Fi/arranque/ADB. No es latencia de polling
ni nube. Mediana fin adquisición→ACK en las diez muestras:404.5ms.
Desarrollo conserva filas v2 con TDS simulado histórico; por eso el aviso de
variables simuladas puede persistir aunque la fila nueva v3 no tenga simulación.
Producción usa real_only=1 y no muestra esas filas. No hay nueva calibración.

Pendiente para Taller5: URL pública HTTPS, MQTT TLS público y certificados;
configuración privada por administrador, diez adquisiciones físicas en nube,
Android con esa URL, fallo/reconexión y tiempo sensor→pantalla aproximado del
recorrido desplegado, video breve conjunto y constancia del actuador aplazado.
Ni el pipeline sintético ni una captura local sustituyen esas evidencias.

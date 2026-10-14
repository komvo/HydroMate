# Acceso público de HydroMate

Hostname confirmado: `hydromate-kevin.duckdns.org`. API Android:
`https://hydromate-kevin.duckdns.org:8443`; MQTT TLS: mismo hostname, puerto8884.
La tarea prepara el repositorio; no accede a la VPS ni acredita una prueba remota.
Docker rootless pertenece a `deploy-hydromate`. API8081 sigue en loopback,
PostgreSQL sin puerto publicado y MQTT1884 solo en la red propia de contenedores.

Mosquitto usa imagen propia `hydromate-mosquitto`, basada en2.0.22. Dockerfile en
deployment/mosquitto incorpora configuración/ACL con dueño1883:1883; no se montan
archivos individuales desde el host. Único bind del broker: secretos read-only.
El hook construye broker/bridge en cada despliegue MQTT para aplicar cambios de
configuración. No incorpora certificados ni passwd a la imagen.

## Configuración única

Conservar las claves y contraseñas existentes en `/etc/hydromate/.env`, sin rotarlas.
Completar la plantilla raíz `.env.example` con estos nombres:

```dotenv
HYDROMATE_APP_KEY=
HYDROMATE_POSTGRES_PASSWORD=
HYDROMATE_DB_PASSWORD=
HYDROMATE_DB_DATABASE=hydromate
HYDROMATE_DB_USERNAME=hydromate
HYDROMATE_IMAGE_TAG=production
HYDROMATE_APP_URL=https://hydromate-kevin.duckdns.org:8443
HYDROMATE_HTTPS_BIND_ADDRESS=0.0.0.0
HYDROMATE_HTTPS_SECRETS_DIR=/etc/hydromate/https
HYDROMATE_MQTT_BIND_ADDRESS=0.0.0.0
HYDROMATE_MQTT_SECRETS_DIR=/etc/hydromate/mqtt
HYDROMATE_MQTT_BRIDGE_PASSWORD=
```

Las cuatro líneas sensibles vacías se rellenan privadamente. No copiar el .env
al PC, imprimir Compose resuelto ni ejecutar `source` sobre ese archivo.
`HYDROMATE_APP_URL` es la única variable de URL de producción para Laravel y la
compilación Android. Si no se exporta en el PC, Gradle lee solo esa línea pública
de `.env.example`, nunca el .env privado. Desarrollo conserva URL/preferencias
independientes; Producción exige HTTPS y datos reales, sin demo/fallback.

## Archivos privados obligatorios

| Directorio | Archivos regulares (copias, sin enlaces simbólicos) |
|---|---|
| `/etc/hydromate/https` | `fullchain.pem`, `privkey.pem` |
| `/etc/hydromate/mqtt` | `fullchain.pem`, `privkey.pem`, `passwd` |

El certificado debe incluir el hostname y ser de confianza pública, con sus
intermediarios. Puede copiarse el mismo certificado propio en ambas carpetas.
Obtenerlo/renovarlo mediante DNS-01 en el sistema administrado de certificados;
no necesita publicar80/443. Configurar DNS A hacia la VPS y no anunciar un AAAA
sin conectividad IPv6 comprobada. [DNS-01 de Let's Encrypt](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge).

`passwd` contiene hashes para `hydromate-device` y `hydromate-bridge`. La contraseña
del bridge coincide con HYDROMATE_MQTT_BRIDGE_PASSWORD; la del dispositivo existe
solo en firmware privado. Conservar cuentas actuales. Aplicar primero la propiedad
deploy-hydromate descrita en la sección siguiente. Si passwd no existe, desde
el checkout y como deploy-hydromate, crearlo interactivamente:

```bash
. deployment/require-rootless.sh
if [ ! -e /etc/hydromate/mqtt/passwd ]; then
  docker run --rm -it --network none --user 0:0 --entrypoint mosquitto_passwd --mount type=bind,source=/etc/hydromate/mqtt,target=/secrets eclipse-mosquitto:2 -c /secrets/passwd hydromate-device
  docker run --rm -it --network none --user 0:0 --entrypoint mosquitto_passwd --mount type=bind,source=/etc/hydromate/mqtt,target=/secrets eclipse-mosquitto:2 /secrets/passwd hydromate-bridge
fi
```

Nunca usar -b ni volver a crear un passwd funcional con -c. Si existe pero falta
una cuenta, añadir únicamente esa cuenta con el segundo comando, sin -c.

## Permisos rootless y primer arranque

El administrador debe dejar estas rutas y sus archivos a nombre de
`deploy-hydromate:deploy-hydromate`, con acceso de ese usuario al directorio padre.
Solo si los archivos existentes pertenecen a root, el administrador ejecuta:

```bash
sudo chown deploy-hydromate:deploy-hydromate /etc/hydromate /etc/hydromate/.env /etc/hydromate/https /etc/hydromate/mqtt /etc/hydromate/https/fullchain.pem /etc/hydromate/https/privkey.pem /etc/hydromate/mqtt/fullchain.pem /etc/hydromate/mqtt/privkey.pem
sudo chmod 750 /etc/hydromate /etc/hydromate/https /etc/hydromate/mqtt
sudo chmod 600 /etc/hydromate/.env /etc/hydromate/https/fullchain.pem /etc/hydromate/https/privkey.pem /etc/hydromate/mqtt/fullchain.pem /etc/hydromate/mqtt/privkey.pem
if [ -f /etc/hydromate/mqtt/passwd ]; then
  sudo chown deploy-hydromate:deploy-hydromate /etc/hydromate/mqtt/passwd
  sudo chmod 600 /etc/hydromate/mqtt/passwd
fi
```

Después, **como deploy-hydromate**, desde el checkout de la versión aprobada:

```bash
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
unset DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH
sh deployment/prepare-rootless-secrets.sh
chmod 600 /etc/hydromate/.env
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env --profile mqtt --profile public config --quiet
sh deployment/deploy.sh /etc/hydromate/.env --mqtt --public
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env --profile mqtt --profile public ps
curl --fail http://127.0.0.1:8081/up
curl --fail https://hydromate-kevin.duckdns.org:8443/up
```

Los tres scripts rechazan otra cuenta o un daemon que no sea rootless y fijan
el socket local del usuario. No usar sudo docker. prepare-rootless-secrets cambia
solo permisos de las cinco rutas de archivos anteriores y sus dos directorios:
propietario0/grupo101 para HTTPS, propietario0/grupo1883 para MQTT **dentro del
namespace**; directorios750/archivos640. El UID0 se traduce al usuario deploy del
host; los grupos se traducen automáticamente. No hacer chown root:101 o root:1883
en el host. [Mapeo oficial de Docker rootless](https://docs.docker.com/engine/security/rootless/uid-gid-mapping/).

El propietario deploy puede renovar los archivos. Si se reemplazan, volver a
aplicar los permisos y recargar únicamente estos dos servicios desde el hook:

```bash
sh deployment/prepare-rootless-secrets.sh
sh deployment/reload-certificates.sh /etc/hydromate/.env
```

deploy.sh ya ejecuta migrate --force después de iniciar API/DB. No cambia redes
externas ni servicios80/443/8883. Nginx GET/HEAD público; POST público403 y bridge
POST interno. Autorizar una sola vez TCP8443/8884 en Ubuntu/OVH mediante el
administrador; si UFW ya está activo: `sudo ufw allow 8443/tcp` y
`sudo ufw allow 8884/tcp`. No habilitar/resetear firewall para este paso.

## Android y ESP32

Android espera la URL base anterior **sin /api**. Se puede seleccionar Producción
e introducirla en Conexión en el debug instalado, sin USB. Para compilar en el PC:

```powershell
$env:JAVA_HOME='C:/Program Files/Android/Android Studio/jbr'
$env:HYDROMATE_APP_URL='https://hydromate-kevin.duckdns.org:8443'
& mobile/gradlew.bat -p mobile assembleDebug assembleRelease
```

Release necesita firma privada de distribución para instalarse. Certificado
público válido; la app no incluye la CA de ensayo ni cambios de confianza TLS.

ESP32: editar únicamente `embedded/HydroMateTelemetry/secrets.h` ignorado por Git.
WIFI_SSID/WIFI_PASSWORD propios; DEVICE_ID=hydromate-01,
MQTT_HOST=hydromate-kevin.duckdns.org (sin esquema), MQTT_PORT=8884,
MQTT_USER=hydromate-device, MQTT_PASSWORD privado, MQTT_TLS=true y MQTT_ROOT_CA
como PEM de la CA raíz emisora (pública, nunca la clave privada). Compilar/cargar
sin HYDROMATE_ALLOW_PLAIN_LAN. No setInsecure: verifica CA/hostname, espera reloj
NTP y rechaza otro puerto TLS. No borrar NVS ni cambiar identidad.

## Validación final desde el PC/red externa

```powershell
$env:HYDROMATE_APP_URL='https://hydromate-kevin.duckdns.org:8443'
$taskMqttHost=([Uri]$env:HYDROMATE_APP_URL).DnsSafeHost
curl.exe --fail "$env:HYDROMATE_APP_URL/up"
& .local/mqtt-venv/Scripts/python.exe scripts/verify_public_access.py --api "$env:HYDROMATE_APP_URL" --mqtt-host $taskMqttHost --min-real-records 0 --output .local/public-preflight.json
& .local/mqtt-venv/Scripts/python.exe scripts/capture_sensor_flow.py --port COM3 --device hydromate-01 --api "$env:HYDROMATE_APP_URL" --fresh-only --target 10 --duration 420 --output .local/final-vps-physical.json
& .local/mqtt-venv/Scripts/python.exe scripts/verify_public_access.py --api "$env:HYDROMATE_APP_URL" --mqtt-host $taskMqttHost --min-real-records 10 --output .local/final-public-verification.json
```

Verificar COM3 antes de capturar. El ESP necesita USB para registrar SAMPLE/SEND/
STORED; el teléfono puede usar datos móviles. verify_public_access verifica cadena
TLS/hostname y GET, pero su socket MQTT no autentica ni publica. La captura compara
diez nuevas adquisiciones con GET de la API. En Android Producción, Inicio e
Historial deben mostrar los mismos valores/fecha, TDS ausente y estado reciente.
Registrar tiempo sensor→pantalla y un fallo/reintento propio; grabar evidencia.

## Alcance de las pruebas

Pruebas locales aisladas: Laravel, bridge, Compose, MQTT TLS→PostgreSQL→GET,
HTTPS8443 y cliente Kotlin por HTTPS con CA exclusiva de tests. No se debilita TLS
en APK. Docker Desktop local no demuestra el namespace del daemon rootless de la
VPS: allí son obligatorios el script de permisos y el ensayo físico anterior.
Hostname y usuario rootless confirmados por el usuario; conectividad pública y
lecturas nuevas en nube pendientes del administrador. No acceso remoto realizado.

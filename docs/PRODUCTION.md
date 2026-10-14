# Publicación vigente: HTTPS8443 / MQTT TLS8884 / Docker rootless

Seguir primero [PUBLIC_ACCESS](PUBLIC_ACCESS.md) para hostname confirmado,
certificados, cuentas MQTT y permisos rootless. Ejecutar como deploy-hydromate:

```bash
. deployment/require-rootless.sh
sh deployment/prepare-rootless-secrets.sh
sh deployment/deploy.sh /etc/hydromate/.env --mqtt --public
```

HYDROMATE_APP_URL=https://hydromate-kevin.duckdns.org:8443; rutas privadas
/etc/hydromate/https y /etc/hydromate/mqtt. El hook ya migra --force. Las variables
sensibles actuales se conservan. No sudo docker. Los comandos base de la referencia
siguiente solo son aplicables en el daemon rootless validado; para publicación
usar ambos perfiles. No se accede a la VPS desde esta tarea.

## Referencia original preservada

# Producción HydroMate en VPS compartida

Esta configuración prepara el repositorio para el ejecutor automático existente
que descarga `main` con acceso Git de solo lectura. No contiene acceso SSH,
credenciales de producción ni cambios al otro proyecto. Todos los recursos
`chitiito-*` son intocables: contenedores, redes, volúmenes y configuraciones.

## Componentes y aislamiento

| Servicio | Función | Puertos / persistencia |
|---|---|---|
| api | Laravel con PHP 8.4 y Apache, proceso www-data; webroot únicamente public | Host **127.0.0.1:8081** → contenedor 8080; volumen hydromate_api_storage |
| db | PostgreSQL 16; rol de aplicación propietario de su BD, sin superusuario | **Sin puerto publicado**; red interna hydromate_database; volumen hydromate_postgres_data |
| mosquitto (perfil mqtt) | Broker propio autenticado, ACL y MQTT TLS para ESP32 | Host **127.0.0.1:8884** por defecto; 1884 solo dentro de red Docker; volumen hydromate_mqtt_data |
| bridge (perfil mqtt) | Paho recibe telemetría, guarda bandeja y POST a Laravel; ACK tras persistir | Sin puertos publicados; volumen hydromate_bridge_state |

Los nombres son exclusivos bajo `-p hydromate`; no hay `container_name`, redes
externas, volúmenes compartidos, modo host ni socket Docker montado. La API usa
también hydromate_application; db solo usa la red interna. Mosquitto/bridge no
acceden a PostgreSQL. Android se ejecuta en el teléfono, nunca en la VPS.

No se usan ni publican 80, 443 o 8883. Antes del primer despliegue, el administrador
debe confirmar que 8081/8884 están libres; si hay conflicto, no detener ningún
servicio para liberar puertos. Revisar una modificación específica de HydroMate.

El binding loopback evita publicar la API actual sin protección. Para Android
remoto se necesita un endpoint HTTPS protegido administrado por separado
(por ejemplo, un puerto dedicado como 8443), que reenvíe a 127.0.0.1:8081.
No modificar el proxy/configuración/red de chitiito para conseguirlo. No se
incluye autenticación completa de usuarios ni se afirma que esté implementada.

## Archivos privados que aporta el administrador

Crear **únicamente en la VPS** `/etc/hydromate/.env` a partir de la plantilla
raíz `.env.example`, con permisos restringidos y lectura para el ejecutor. Puede
estar fuera del checkout de solo lectura. No copiar `hydromate-backend/.env`
de desarrollo ni enviar secretos al chat/Git. La plantilla del backend conserva
su uso local; la plantilla raíz configura Compose para producción.

Variables indispensables:

- `HYDROMATE_APP_KEY`: clave Laravel base64 válida de 32 bytes; crear una vez y
  conservarla en actualizaciones. No regenerarla en cada arranque/despliegue.
- `HYDROMATE_POSTGRES_PASSWORD`: contraseña exclusiva del administrador PostgreSQL.
- `HYDROMATE_DB_PASSWORD`: contraseña diferente para el rol de la aplicación.
- `HYDROMATE_DB_DATABASE` y `HYDROMATE_DB_USERNAME`: nombres propios, por defecto
  hydromate; el usuario de aplicación no puede ser postgres.
- `HYDROMATE_APP_URL`: URL base del acceso previsto; localhost:8081 sirve para
  revisión inicial del administrador y no es URL Android remota.
- `HYDROMATE_IMAGE_TAG`: production por defecto; puede ser el SHA entregado por
  el ejecutor para identificar cada imagen. No modifica nombres de recursos.

Compose rechaza las tres variables obligatorias vacías antes de iniciar. No
usar `docker compose config` sin `--quiet` en logs públicos: muestra valores
resueltos de entorno. El Dockerfile excluye .env, vendor local, logs, respaldos
y cachés; instala dependencias del composer.lock sin paquetes de desarrollo.

El rol app se crea solo al inicializar un **volumen vacío nuevo**. Cambiar la
contraseña en .env no rota una cuenta ya existente; esa operación debe coordinarla
el administrador sin borrar el volumen. El volumen nuevo de producción no importa
automáticamente los datos de la PC; la migración de registros requiere respaldo
y procedimiento propios, no copiar volúmenes compartidos.

## Ejecución de producción

Desde la raíz del checkout en la VPS, usando siempre el proyecto explícito:

```bash
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env config --quiet
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env build --pull api
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env up -d --wait --wait-timeout 180 db api
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env exec -T api php artisan migrate --force --no-interaction
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env ps
```

`migrate --force` aplica las migraciones existentes, incluidas las de telemetría
v1/v2 y el esquema inicial Laravel. No ejecuta seeders, no vacía tablas y no
implementa por sí solo autenticación. Las migraciones se ejecutan una vez por
despliegue, después de arrancar db/api; no durante build ni concurrentemente en
cada entrada del contenedor. Respaldar antes de actualizar una BD con información.

El healthcheck verifica HTTP `/up`, arranque Laravel y `SELECT 1` de la conexión
app. No escribe datos; puede pasar antes de crear measurements. Después de
migrar verificar también el endpoint API:

```bash
curl --fail http://127.0.0.1:8081/up
curl --fail 'http://127.0.0.1:8081/api/measurements?device_id=hydromate-01&limit=20'
```

Una lista vacía en instalación nueva es válida; una prueba de viabilidad requiere
posteriormente muestras físicas nuevas. Los logs de Laravel van a stderr y los
logs Docker tienen rotación por servicio. Desarrollo local en 127.0.0.1:8000 y
contenedor histórico hydromate-postgres permanecen separados de este Compose.
API y bridge utilizan el init de Docker para recibir señales y recolectar procesos
secundarios. La API se detiene con SIGTERM; Apache también limita a cinco segundos
una parada gradual solicitada explícitamente por el operador.

## Hook para el despliegue automático desde main

El sistema existente actualiza el checkout; después invoca:

```bash
sh deployment/deploy.sh /etc/hydromate/.env
# Cuando los archivos privados MQTT ya estén provisionados:
sh deployment/deploy.sh /etc/hydromate/.env --mqtt
```

El hook no hace git push/pull, no escribe el checkout ni solicita SSH. Construye
imágenes, inicia/actualiza **solo los servicios nombrados de hydromate**, espera
salud y aplica migraciones. El ejecutor debe serializar despliegues de HydroMate
para evitar migraciones concurrentes. Requiere Docker Compose v2 con `--wait`.
La lectura Git es distinta del permiso para operar Docker; el administrador
configura ese permiso en su ejecutor existente, no en este repositorio.

No se incluye un workflow GitHub que necesite secretos SSH. Los comandos anteriores
son la interfaz para la automatización ya prevista. La actualización puede tener
una ventana breve entre recreación API y migración; no promete cero interrupciones.
La imagen anterior y los respaldos deben conservarse para recuperación controlada;
la migración v2 no admite rollback destructivo automático.

## MQTT opcional siguiendo la arquitectura del ESP32

El administrador crea una carpeta **exclusiva HydroMate** fuera de Git y configura
`HYDROMATE_MQTT_SECRETS_DIR` con su ruta absoluta. Debe contener:

- `passwd`: hashes Mosquitto para hydromate-device y hydromate-bridge.
- `fullchain.pem` y `privkey.pem`: certificado y llave TLS del hostname MQTT propio.

Los archivos deben ser legibles por el usuario del contenedor Mosquitto y la llave
no debe ser pública. No compartir carpeta/certificados/configuraciones con chitiito.
`deployment/secrets/` está ignorada si se usa la ruta relativa sugerida; la ruta
privada no se crea automáticamente cuando falta. El broker no arranca sin sus
archivos; el bridge rechaza contraseña vacía al entrar.

Configurar `HYDROMATE_MQTT_BRIDGE_PASSWORD` igual a la cuenta del passwd. La ACL
incluida permite al dispositivo solo telemetry/ack de hydromate-01 y al bridge
los tópicos HydroMate. No usar cuentas ni tópicos del otro proyecto. La inclusión
de otra torre requiere su propia identidad/cuenta y ACL revisada.

```bash
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env --profile mqtt build --pull mosquitto bridge
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env --profile mqtt up -d --wait mosquitto bridge
```

Para recibir al ESP32 por Internet, el administrador autoriza y configura el
binding de HydroMate (`HYDROMATE_MQTT_BIND_ADDRESS`, por ejemplo 0.0.0.0), acceso
de red a **8884** y certificado válido; no cambiar 8883 ni reglas/configuraciones
del otro proyecto. El listener 1884 no se publica: comunicación interna
broker→bridge autenticada en red privada propia. El tramo ESP32→VPS utiliza TLS.

En firmware privado: hostname del broker, puerto 8884, MQTT_TLS=true, CA que valide
su certificado y cuenta propia. No usar setInsecure ni trasladar el MQTT plano LAN
a Internet. El bridge usa API interna http://api:8080, sin entrar a BD. Conserva
bandeja y confirma stored después de INSERT; no se implementan actuadores nuevos.
Healthcheck Mosquitto comprueba listener interno; no sustituye ensayo TLS/ACL/ACK.

Android: conexión real a la URL HTTPS protegida y device_id hydromate-01. Su APK
y código no se incluyen en ninguna imagen del servidor. Demostración debug no
sustituye consulta de datos físicos.

## Operaciones permitidas y validación

Consultar únicamente el proyecto:

```bash
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env logs --tail 100 api db
docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env --profile mqtt logs --tail 100 bridge mosquitto
```

No usar prune, reiniciar Docker globalmente, borrar volúmenes, ejecutar
migrate:fresh/reset ni operar recursos chitiito para solucionar fallos HydroMate.
Si se requiere detener HydroMate, nombrar servicios propios con `compose stop`;
conservar datos y respaldos. No publicar logs con secretos o datos ajenos.

La verificación local de política es `python scripts/verify_production_compose.py`:
usa valores ficticios, analiza Compose y no inicia servicios. La validación real
del contenedor debe comprobar build, healthcheck, migraciones, POST válido/422,
consulta y persistencia, en un proyecto de ensayo separado. Los resultados
observados se registran en STATUS; no equivalen a despliegue en VPS.

Validación del 14/10/2026: build API/bridge, healthcheck, migrate --force (y
repetición sin cambios), smoke HTTP, diez MQTT TLS sintéticos y recuperación de
pendiente tras corte pasan en hydromate-validation. Rol app no superusuario y
UID33 verificados; la imagen no contiene .env ni PHPUnit. Filas locales de
desarrollo permanecen idénticas. Ensayo detenido conservando volúmenes.
Evidencias: [resumen](evidence/production-stack-2026-10-14.json),
[HTTP](evidence/production-http-2026-10-14.json) y
[MQTT TLS](evidence/production-mqtt-tls-2026-10-14.json).
Repetición previa al commit: [revisión](evidence/production-review-2026-10-14.json)
y [nuevo smoke HTTP](evidence/production-review-http-2026-10-14.json), ambos pasan.

Referencias: [imagen oficial PHP](https://hub.docker.com/_/php),
[despliegue Laravel](https://laravel.com/framework/docs/deployment) y
[redes internas Compose](https://docs.docker.com/reference/compose-file/networks/).

# Taller 5 — procedimiento local reproducible

Fecha de trabajo: 7 de octubre de 2026. Este documento explica el incremento,
los comandos y cómo verificarlo. Consultar STATUS para distinguir pasos probados
de pasos pendientes. No es todavía la aprobación de viabilidad en nube.

## 1. Entender qué hay en cada carpeta

| Ruta desde C:\Hydromate | Qué contiene y para qué sirve |
|---|---|
| hydromate-backend/ | Laravel: recibe y valida mediciones, guarda en PostgreSQL y responde consultas |
| mobile/ | Android Kotlin: consulta API y dibuja última medición/historial; nunca entra a la BD |
| embedded/HydroMateTelemetry/ | Firmware nuevo del ESP32: sensores, JSON, Wi-Fi, MQTT, secuencia y reintentos |
| scripts/mqtt_bridge.py | Integrador: escucha MQTT y hace POST a Laravel |
| scripts/test_mqtt_flow.py | Productor sintético para probar red/API/BD antes de usar hardware |
| scripts/start_local.ps1 | Arranque de procesos locales existentes sin borrar/recrear datos |
| docs/ | Contexto, decisiones, arquitectura, API y contrato vigente |
| talleres/taller-05/ | Evidencias y reporte técnico de esta entrega |
| Documentos PDC/tests/PruebaSensores1.ino | Prueba histórica de sensores, conservada sin cambiar |
| .local/ | Herramientas portátiles, logs, backup y bandeja privada; no se sube a GitHub |

Un repositorio almacena código/documentos. Los procesos que arrancas ejecutan ese
código. GitHub no ejecuta automáticamente tu API, broker ni base de datos.

## 2. Comprender el recorrido de una medición

El ESP32 lee temperatura/pH/lux/flotador y genera un JSON. TDS se fija en 650 y
su origen dice simulated. Wi-Fi transporta ese JSON al broker Mosquitto. El broker
lo entrega al integrador suscrito; no valida rangos de pH ni guarda el historial
académico. El integrador conserva una copia pendiente y hace POST a Laravel.

Laravel aplica las reglas del contrato. Si el dato es válido, inserta una fila
en PostgreSQL y devuelve HTTP 201. Entonces el integrador publica un ACK stored.
El ESP32 retira su pendiente solamente al recibir ese ACK. Android consulta GET
y muestra la fila almacenada. Una publicación MQTT por sí sola no prueba INSERT.

La SQLite del integrador es una bandeja de entrega local, no otra BD del producto;
el historial que consume Android sigue siendo PostgreSQL.

Puertos: API 8000 en loopback; PostgreSQL 5432 conserva configuración anterior;
broker nuevo 1884 autenticado en loopback/IP Wi-Fi; Mosquitto anterior 1883 intacto.
127.0.0.1 significa «este equipo»: el ESP32 debe usar la IP de la PC (actualmente
192.168.1.6). En Android usamos adb reverse para que el localhost del teléfono
llegue al localhost de la PC por USB, sin exponer Laravel a la red.

## 3. Arrancar PostgreSQL sin perder datos

Abrir Docker Desktop. En PowerShell:

```powershell
Set-Location C:\Hydromate
git status --short
docker ps -a --format '{{.Names}}|{{.Image}}|{{.Status}}'
docker inspect hydromate-postgres --format '{{json .Mounts}}'
docker start hydromate-postgres
```

Se comprobó volumen persistente montado en /var/lib/postgresql/data. No usar
docker rm, compose down -v ni migrate:fresh: borrarían contenedor/volumen/datos.
Antes de ampliar esquema se ejecutó pg_dump en formato custom dentro del
contenedor y se copió a `.local/backups/hydromate-before-v2-2026-10-07.dump`.
No publicar ese backup: puede contener datos privados. Procedimiento usado:

```powershell
docker exec hydromate-postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" -Fc -f /tmp/hydromate-before-v2.dump'
docker cp hydromate-postgres:/tmp/hydromate-before-v2.dump C:/Hydromate/.local/backups/hydromate-before-v2-2026-10-07.dump
```

En un respaldo posterior usar nombres con otra fecha/hora para conservar éste.

## 4. Ampliar el contrato y la tabla

v1 representaba luz/nivel en porcentajes. No convertimos lux a porcentaje ni
flotador a litros inventados. v2 agrega `message_version`, `light_lux`,
`water_present` y `sources` y permite null en los campos históricos solo a nivel
de esquema. La validación sigue exigiendo el conjunto correspondiente a v1/v2.
Origen de cada sensor: real o simulated; el productor declara ese origen.

La migración es una receta versionada para modificar la estructura de la BD.
El modelo Measurement indica campos asignables y cómo serializar números,
booleanos y JSON. StoreMeasurementRequest valida; MeasurementController hace
INSERT/GET. Son responsabilidades distintas, dentro del mismo backend.

```powershell
Set-Location C:\Hydromate\hydromate-backend
& C:\Hydromate\.local\php\php.exe artisan migrate:status
& C:\Hydromate\.local\php\php.exe artisan migrate --path=database/migrations/2026_10_07_000001_add_physical_telemetry_to_measurements.php --force
& C:\Hydromate\.local\php\php.exe artisan route:list --path=api
& C:\Hydromate\.local\php\php.exe vendor/bin/phpunit --testdox
```

Se aplicó únicamente esa migración, sin instalar autenticación completa ni la
migración Sanctum histórica pendiente. Repetirla ya aplicada no cambia filas.
19 pruebas/118 assertions pasan en SQLite :memory:, protegida contra reset de
PostgreSQL. No ejecutar rollback de v2: exige migración explícita de sus filas.

## 5. Arrancar Laravel y comprobar HTTP

```powershell
Set-Location C:\Hydromate\hydromate-backend
& C:\Hydromate\.local\php\php.exe artisan serve --host=127.0.0.1 --port=8000 --no-reload
```

Dejar esa consola abierta. Si el servidor ya existe, no arrancar otro en 8000.
Otra consola puede consultar:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/measurements?device_id=hydromate-01&limit=20'
Set-Location C:\Hydromate
python hydromate-backend/tests/smoke_api.py --output talleres/taller-05/pruebas/http-nueva-ejecucion.json
```

HTTP 201 significa nueva fila; 409 identidad duplicada; 422 campos incorrectos.
GET de torre sin filas devuelve [] y latest devuelve 404. Smoke deja 11 filas
sintéticas test-api-*; no elimina mediciones ni representa sensores físicos.

## 6. Preparar Mosquitto e integrador

Mosquitto ya estaba instalado en `C:\Program Files (x86)\Mosquitto`. Se dejó
intacto su servicio 1883 y se inició una instancia de banco 1884. Configuración
privada en `.local/mqtt/mosquitto.conf`, contraseñas hasheadas y ACL en esa carpeta.
Las tres cuentas locales son device (su torre), bridge (telemetría/ACK) y test.
Los secretos originales están solo en users.json privado y secrets.h ignorado.
No usar estas contraseñas de banco en el VPS.

Primera preparación reproducible: `scripts/setup_mqtt_local.ps1 -PcIp 192.168.1.6`
(usar IP real de esa PC). Genera usuarios aleatorios, hashes, ACL, listeners y
plantilla privada; se niega a regenerar secretos existentes. En esta PC ya está
configurado: al repetir conserva lo que existe. No abre firewall ni arranca servicios.

Se creó un entorno Python aislado para evitar instalar paquetes globalmente:

```powershell
Set-Location C:\Hydromate
python -m venv .local/mqtt-venv
& .local/mqtt-venv/Scripts/python.exe -m pip install -r scripts/requirements-mqtt.txt
```

Si el entorno ya existe, reutilizarlo. Arranque reproducible de los servicios
preparados en esta PC:

```powershell
& C:\Hydromate\scripts\start_local.ps1 -WithLanMqtt
```

No regenera contraseñas, no aplica migraciones ni cambia firewall. Guarda logs y
PID en .local. Después de reiniciar Windows comprobar procesos/puertos y logs.
Si la IP Wi-Fi cambió, actualizar listener/configuración privada/firmware/regla;
no asumir que 192.168.1.6 será permanente.

La prueba autenticada usa la cuenta de pruebas sin imprimir la contraseña:

```powershell
Set-Location C:\Hydromate
$taskUsers = Get-Content .local/mqtt/users.json -Raw | ConvertFrom-Json
$env:MQTT_USERNAME = 'hydromate-test'
$env:MQTT_PASSWORD = $taskUsers.'hydromate-test'
& .local/mqtt-venv/Scripts/python.exe scripts/test_mqtt_flow.py --port 1884 --output talleres/taller-05/pruebas/mqtt-nueva-ejecucion.json
Remove-Item Env:MQTT_PASSWORD
Remove-Item Env:MQTT_USERNAME
```

Diez publicaciones sintéticas se guardaron, mismo mensaje se confirmó sin
duplicar, conflicto se detectó y pH=50 se rechazó sin INSERT. JSON de evidencia
incluye tiempos PC→ACK de persistencia; no son tiempo sensor→pantalla.

## 7. Permitir conexión del ESP32 en tu red doméstica

El usuario autorizó red doméstica privada y MQTT solo desde subred local. La
primera ejecución falló por falta de elevación. Abrir PowerShell como administrador:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Hydromate\scripts\enable_mqtt_lan.ps1
```

El bypass es solo de esa ejecución, no cambio permanente de política. El script
cambia Wi-Fi a Private y agrega regla 1884, IP local actual, LocalSubnet y ejecutable
Mosquitto. No abre router, no permite perfil Public ni expone la API a Internet.
Ambos equipos deben compartir red; aislamiento entre clientes puede impedirles
comunicarse. El ESP32 requiere Wi-Fi compatible con su hardware (banda 2.4 GHz).
La PC puede permanecer en 5 GHz si el router une ambas bandas en la misma LAN.
Cambiar secrets.h requiere recompilar y volver a cargar; el archivo no actualiza
por sí solo un ESP32 que ya está ejecutando un binario anterior.

## 8. Compilar y cargar firmware

Ver embedded/README.md para comando exacto. Se reutiliza core ESP32 3.3.11 y las
bibliotecas de sensores instaladas. PubSubClient 2.8 y ArduinoJson 7.4.2 se
descargaron de sus repositorios oficiales en ZIP y se extrajeron solo en
.local/arduino-libraries. Para reproducir en otra PC instalar esas versiones,
no copiar contraseñas ni respaldos de .local.

Para la configuración aislada que reutiliza core instalado y bibliotecas de
sensores, ejecutar `scripts/prepare_arduino_local.ps1`. Copia solo fuentes necesarias
desde el sketchbook conocido de OneDrive, sin cambiarlo; genera el YAML local.
La compilación usa --config-file y --jobs 2 (ver embedded/README.md). Si otra PC
usa otro sketchbook, ajustar esa ruta, no instalar versiones diferentes por azar.

secrets.example.h es plantilla pública; secrets.h es la configuración privada.
Completar WIFI_SSID/WIFI_PASSWORD allí. DEVICE_ID conserva identidad de torre.
No imprimir ese archivo ni subir el binario de firmware con secretos a GitHub.
Compilar no carga la placa; upload sí reemplaza el programa que ejecuta.

Diagnóstico serie del core actual: WIFI_STATUS code=3 indica conexión Wi-Fi;
1 significa red no disponible, 4 conexión fallida y 6 desconectado. Son estados,
no una identificación inequívoca de la causa. WIFI_RETRY reintenta cada 30 s;
MQTT_CONNECTED confirma el siguiente tramo. STORED confirma persistencia por API.
RESTORED muestra el JSON pendiente recuperado de NVS, sin cambiar su secuencia;
no representa una nueva adquisición ni sirve para medir su latencia de adquisición.

Firmware procesa pH promediando diez conversiones y usa la calibración previa.
Rechaza sensores detectados inválidos. TDS es fijo y se marca simulado. No mueve
bombas. Persiste secuencia/pendiente para reintentar exactamente el mismo objeto.
Ensayos de reinicio y fallos eléctricos son verificaciones pendientes hasta
observarlas; compilar no demuestra funcionamiento del hardware.

## 9. Compilar Android y consultar desde el teléfono

```powershell
Set-Location C:\Hydromate\mobile
$env:JAVA_HOME='C:/Program Files/Android/Android Studio/jbr'
./gradlew.bat assembleDebug testDebugUnitTest lintDebug --console=plain
$adb="$env:LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"
& $adb devices
& $adb install -r app/build/outputs/apk/debug/app-debug.apk
& $adb reverse tcp:8000 tcp:8000
& $adb shell am start -n com.hydromate.mobile/.MainActivity
```

En Más → conexión, servidor http://127.0.0.1:8000 y torre hydromate-01 cuando haya
datos físicos. Para verificar software antes, usar test-mqtt-1d947c343a: contiene
diez filas sintéticas y debe anunciar Datos de prueba. Salir de Demostración antes
de consultar API real. En Inicio/Historial comprobar lux, estado del flotador,
TDS simulado y hora de recepción. Actualizar manualmente: no hay polling automático.
La gráfica de luz no mezcla porcentajes históricos con lux.

Se observó BUILD SUCCESSFUL y APK instalada. La primera inspección visual encontró
teléfono bloqueado; no se afirma QA visual de lecturas mientras no se vea la app.
Después de desbloquear, `hydromate-01` mostró correctamente «Sin lecturas para esta
torre». MIUI bloqueó inyección de toques por USB; la configuración se hizo manualmente.
No cambiar preferencias a escondidas: guardar configuración desde la pantalla.

## 10. Evidenciar hardware y preparar nube

Con monitor serie registrar adquisición, publicación y STORED de al menos diez
secuencias. Consultar API para esas mismas secuencias, verlas en Android y grabar
video corto. Cambiar iluminación/flotador para demostrar que son entradas reales.

Captura automática usada en esta etapa (cerrar otros monitores serie antes):

```powershell
Set-Location C:\Hydromate
& .local/mqtt-venv/Scripts/python.exe -m pip install -r scripts/requirements-hardware.txt
& .local/mqtt-venv/Scripts/python.exe scripts/capture_sensor_flow.py --port COM3 --device hydromate-01 --output talleres/taller-05/pruebas/esp32-nueva-ejecucion.json
```

Conserva muestras JSON, intentos y ACK, y verifica campos/secuencias contra API.
Abrir puerto serie puede reiniciar ESP32; la reserva/persistencia evita reutilizar
secuencia. Para evidencia de otra ejecución usar otro nombre de archivo.
Registrar éxito/fallo por intento; conservar pH inválido/caída de conexión y su
corrección. Para latencia sensor→frontend usar cronómetro/video o correlación de
secuencia desde SAMPLE hasta actualización visible; no confundir con tiempo HTTP.

Resultados locales observados: diez mensajes 101 y 401–409 verificados contra API;
BH1750 1.67–185 lux y ambos estados del flotador. Inicio/Historial muestran datos
del ESP32. El pH inicial inválido se corrigió revisando alimentación/conexión;
la red original exclusiva de 5 GHz se sustituyó por una compatible con 2.4 GHz.

Para repetir la aproximación de tiempo (teléfono desbloqueado, Inicio y zona horaria
igual a la PC; cerrar otros monitores serie):

```powershell
$adb="$env:LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"
& .local/mqtt-venv/Scripts/python.exe scripts/measure_android_latency.py --port COM3 --adb $adb --output talleres/taller-05/pruebas/latencia-nueva.json
```

El script observa SAMPLE/STORED nuevos, consulta la secuencia por API, reinicia
solo HydroMate y comprueba su fecha en la jerarquía de la interfaz. Resultado de
una repetición: 8.24 s desde fin de adquisición hasta verificación. Incluye
arranque de app/ADB; no es benchmark de actualización automática. Primer intento
falló al extraer XML, conservado; se añadieron reintentos de inspección.

Para el corte controlado se detuvo solo el broker 1884 identificado por su PID y
ejecutable, se abrió captura serial y se restableció con start_local.ps1
-WithLanMqtt. Se observaron MQTT_FAIL, conservación de 901, reenvío idéntico y
STORED; 901/902 coinciden con API. No se detuvo el Mosquitto previo de 1883 ni
se borraron datos. Repetir con otro archivo y restaurar servicio al terminar.

Video local disponible en pruebas/android-consulta-local-2026-10-07.mp4: grabación
real por adb screenrecord, transición Historial → reapertura de HydroMate → carga
→ datos de API. Duración efectiva 10.06 s. No muestra el montaje ni la nube.
Se revisaron fotogramas con FFmpeg, obtenido mediante imageio-ffmpeg 0.6.0 solo
en la venv privada; esa herramienta no es dependencia del firmware/backend.
Grabar el video final incluyendo montaje y backend desplegado posteriormente.

Después contratar/provisionar VPS: instalar runtime PHP compatible con composer.lock,
web server, PostgreSQL, Mosquitto e integrador; separar datos y permisos del compañero,
configurar HTTPS/MQTT TLS/protección de API, migrar datos con respaldo y cambiar
direcciones privadas en ESP32/Android. Repetir diez muestras y fallos en nube.
Git clone descarga código; .env, secrets, certificados y datos se configuran aparte.
No subir .local completa ni el servidor artisan de desarrollo como servicio final.

La entrega necesita además reporte PDF técnico revisado, video, esquema/consulta,
capturas, evidencia del backend desplegado, cronograma, presupuesto y riesgos.
Si control remoto sigue siendo central, comando físico seguro o aplazamiento
autorizado por docente; no sustituirlo por una orden simulada en Android.

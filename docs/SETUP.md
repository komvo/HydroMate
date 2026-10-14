# Arranque local comprobado — 2026-10-07

HTTPS público propio8443 y MQTT TLS8884: [PUBLIC_ACCESS](PUBLIC_ACCESS.md).
Es un perfil de producción opt-in; no modifica el banco local ni recursos ajenos.

## Producción preparada sin acceso VPS — 2026-10-14

Guía vigente: [PRODUCTION](PRODUCTION.md); `compose.production.yml` en raíz y
Dockerfile en hydromate-backend. Ejecutar siempre
`docker compose -p hydromate -f compose.production.yml --env-file /etc/hydromate/.env ...`.
Hook del ejecutor existente: `sh deployment/deploy.sh /etc/hydromate/.env [--mqtt]`.
El usuario de Git solo descarga main; el ejecutor debe tener permiso Docker
configurado por administrador. Secretos fuera del checkout, solo VPS; plantilla
raíz .env.example vacía en valores sensibles. Sin cambios al .env de desarrollo.
API loopback 8081, BD interna sin publicar5432, perfil opcional MQTT TLS8884.
No usar puertos reservados80/443/8883 ni tocar recursos/configuración chitiito-*.
La sección de acceso SSH anterior queda reemplazada para esta tarea por el
empaquetado local y la ejecución automatizada descrita, sin solicitar credenciales.

## Recuperación observada 14/10/2026

Docker Desktop 4.62.0 no arrancó por sockets temporales inaccesibles en
`%LOCALAPPDATA%/Docker/run/dockerInference` y
`%LOCALAPPDATA%/docker-secrets-engine/engine.sock`. Tras cerrar procesos verificados,
conservar ambas carpetas temporales y recrearlas juntas, el engine respondió.
No usar Reset to factory defaults como reparación: el usuario comunica haberlo
pulsado; se comprobó después persistencia del contenedor/volumen y registros.
Copia privada del disco detenido en .local/backups/docker-recovery-2026-10-14;
carpetas de sockets anteriores conservadas fuera del repositorio. Este procedimiento
no es una receta de borrado general ni exige restablecer la configuración.

Se ejecutó `scripts/start_local.ps1` sin -WithLanMqtt: PostgreSQL y Laravel
loopback disponibles; GET conserva registros históricos y esquema v2 exportado.
MQTT/bridge LAN y hardware no se revalidaron en este arranque. Para nube seguir
`../talleres/taller-05/despliegue-vps.md`; necesita inventario/acceso SSH propios.

## Actualización Taller 5 — 2026-10-07

Guía detallada: ../talleres/taller-05/procedimiento-local.md. API/PostgreSQL
arrancados; respaldo antes de migración v2 en .local/backups (privado). Migración
aditiva ejecutada únicamente por --path; Sanctum sigue pendiente.
`scripts/start_local.ps1 -WithLanMqtt` reutiliza configuración y procesos de banco.
Broker autenticado separado 1884, configuración/ACL/usuarios en .local/mqtt;
bridge con .local/mqtt-venv (Paho 2.1.0) y bandeja SQLite privada.
Red Wi-Fi doméstica privada autorizada; regla solo 1884/Private/LocalSubnet.
El script de regla necesita PowerShell administrador: scripts/enable_mqtt_lan.ps1.
Firmware y dependencias: embedded/README.md; secretos privados en secrets.h.
No migrar estas credenciales ni artisan serve como servicio final de nube.

## PostgreSQL
Abrir Docker Desktop y comprobar el contenedor existente hydromate-postgres.
No recrear ni borrar contenedor/volúmenes. Acceso Docker recuperado; PostgreSQL
16.15 usa volumen local anónimo en /var/lib/postgresql/data (evidence/docker-mounts-step2.json).
Conservar ese volumen y adjuntarlo explícitamente si algún día se recrea el contenedor.
Desde PowerShell del usuario comprobar persistencia:
```powershell
docker inspect hydromate-postgres --format '{{json .Mounts}}'
```
Si está detenido y existe: docker start hydromate-postgres. Confirmar que el
directorio de datos está montado; si no, planificar backup y migración segura.

## PHP y backend
Se agregó PHP 8.4.26 portátil a C:\Hydromate\.local\php. Fuente/hash en source.json.
Extensiones habilitadas incluyen pdo_pgsql, pdo_sqlite, mbstring y openssl.
No cambia PATH global ni Herd. Dependencias instaladas requieren PHP >=8.4.1.
Comandos comprobados:
```powershell
Set-Location C:\Hydromate\hydromate-backend
& C:\Hydromate\.local\php\php.exe artisan --version
& C:\Hydromate\.local\php\php.exe artisan migrate:status
& C:\Hydromate\.local\php\php.exe artisan route:list --path=api
& C:\Hydromate\.local\php\php.exe artisan serve --host=127.0.0.1 --port=8000 --no-reload
```
Comprobar primero si el puerto ya está ocupado: se dejó un servidor iniciado.
Logs del proceso iniciado por el agente: .local/backend-server.out.log y .err.log.
URL API: http://127.0.0.1:8000/api/measurements. La raíz conserva bienvenida Laravel.
No cambiar .env ni publicar credenciales. No se ejecutó ninguna migración nueva;
Sanctum pendiente deliberadamente. No usar migrate:fresh/refresh/reset.

## Pruebas
```powershell
& C:\Hydromate\.local\php\php.exe vendor\bin\phpunit --testdox
python tests\smoke_api.py --output ..\docs\evidence\nueva-prueba-http.json
```
PHPUnit usa SQLite :memory: y tiene guardia para no resetear PostgreSQL.
Smoke usa servidor activo y deja 11 lecturas sintéticas por ejecución bajo un
device_id único test-api-*. No elimina registros. Cada ejecución usa otro archivo
de evidencia para conservar resultados anteriores.
Composer comprobado: PHP portátil + C:\ProgramData\ComposerSetup\bin\composer.phar.
No hace falta reinstalar vendor. El cliente Python de auditoría PostgreSQL está
aislado en .local/python-packages; la API no depende de él.

## Después
Android será el primer frontend. Configuración LAN y teléfono se abordarán allí;
este paso solo escucha en loopback. No hay comandos de Wokwi/bridge requeridos.

## Android mínimo ya construido
Abrir C:\Hydromate\mobile en Android Studio. Guía completa: ../mobile/README.md.
Desde esa carpeta: JAVA_HOME al jbr de Android Studio; gradlew.bat assembleDebug
testDebugUnitTest lintDebug. Para ejecutar también la prueba de consulta real,
definir HYDROMATE_TEST_API=http://127.0.0.1:8000 antes de Gradle (prueba opt-in).
Con teléfono autorizado por USB, instalar APK y ejecutar adb reverse tcp:8000
tcp:8000. App: servidor http://127.0.0.1:8000 y dispositivo test-api-0865fd385681.
El enlace USB no está activo hasta conectar el teléfono y ejecutar reverse.
APK mínimo Android 8.0; versión de desarrollo, no publicación de tienda.

Android Aero Eco 0.4 conserva este arranque. Antes de crear el enlace USB comprobar
también `adb reverse --list`. Demostración offline opcional: Más →
Demostración → elegir escenario; salir explícitamente para consultar API real.
Solo existe en debug y no requiere backend. Receta de validación/capturas:
AERO_ACCEPTANCE.md. `scripts/verify_eco.py` desde raíz recoge evidencia
después de Gradle; usar los argumentos de esa receta para el incremento actual,
sin sobrescribir informes históricos. No sustituye pruebas visuales Android.

Revisión visual 0.4: capture_eco_review.py abre una Activity aislada solo debug;
receta y límites en AERO_ACCEPTANCE.md. No modifica ajustes del teléfono.
Observado el 04/10: USB autorizado/reverse preparado, Docker daemon no activo;
arrancar y comprobar servicios existentes antes de afirmar conexión a PostgreSQL.

0.6.0-garden conserva el mismo arranque. El capturador requiere pantalla
desbloqueada; la Activity debug mantiene retrato y pantalla encendida mientras
está visible, sin ajustes globales. Indicar `--output docs/evidence/garden-light-2026-10-04`
al capturar. Verificador: argumentos `--build-log`, `--baseline`, `--evidence-dir`
y `--report` completos en AERO_ACCEPTANCE.md. Evidencia previa conservada.
Más → Apariencia → Usar Jardín claro evita la variante nocturna del sistema;
seleccionado en este teléfono para atender la petición de fondo mucho más claro.
## Integración actual v3

Configuración ESP32 MQTT/TLS, perfiles Android y ensayo completo:
[INTEGRATION](INTEGRATION.md). Producción conserva Compose aislado de
[PRODUCTION](PRODUCTION.md). Aplicar migración
`2026_10_14_000001_add_partial_telemetry_v3.php` con `php artisan migrate --force`
después de respaldo y arranque; no usar migrate:fresh/reset. Los pasos locales
anteriores siguen vigentes, con firmware v3 y TDS null en lugar de fijo simulado.

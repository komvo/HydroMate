# Arranque y validación por entorno

Revisión: 27/10/2026. Estado actual en [STATUS](STATUS.md); lo documentado no
significa que procesos o dispositivos sigan conectados.

## Herramientas y configuración

Trabajar desde `C:\Hydromate`. Reutilizar herramientas instaladas y consultar sus
versiones. `.local/`, vendor, SDK y secretos no aparecen al clonar: comprobar su
existencia antes de usarlos. Preparar dependencias solo si la tarea lo requiere.

- Backend: [README](../hydromate-backend/README.md), composer.json/lock.
  PHP portátil conocido: `.local/php/php.exe`.
- Android: [README](../mobile/README.md), wrapper Gradle/JBR de Android Studio.
  Una variable pública de producción: `HYDROMATE_APP_URL`; `.env.example` raíz
  contiene el valor público predeterminado.
- Firmware: [README](../embedded/README.md), core/bibliotecas allí indicados.
  `secrets.h` es privado; no sobrescribirlo al copiar ejemplos.
- Python MQTT: requirements del proyecto y `.local/mqtt-venv/` si existe.
  SQLite del bridge es una bandeja privada, no la base de negocio.

No mostrar secretos ni cambiar credenciales a partir de ejemplos. Desarrollo y
producción permanecen separados.

## Pruebas offline: sin VPS ni hardware

PHPUnit usa SQLite en memoria según `hydromate-backend/phpunit.xml`; verificar
esa configuración antes de ejecutarlo. Desde la raíz, con vendor instalado:

```powershell
Push-Location .\hydromate-backend
try { & ..\.local\php\php.exe vendor\bin\phpunit --testdox }
finally { Pop-Location }
```

Pruebas Python del bridge y validación de puertos públicos:

```powershell
& .\.local\mqtt-venv\Scripts\python.exe -m unittest discover -s scripts -p test_bridge.py
& .\.local\mqtt-venv\Scripts\python.exe -m unittest discover -s scripts -p test_public_access.py
```

`test_deployment.py` depende del entorno/shell: registrar skips, que no acreditan
compatibilidad rootless. `verify_production_compose.py` valida Compose con sus
fixtures; nunca volcar el entorno real de producción.
Pruebas C++: `scripts/tests/telemetry_sensors_test.cpp` y `pump_control_test.cpp`
(en esta PC: `C:\MinGW\bin\g++ -std=c++11`); usar compilador disponible
conforme a embedded/README, sin instalar uno para esta revisión.

Android, si el JBR está instalado en esa ruta:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
& .\mobile\gradlew.bat -p mobile :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:assembleRelease --console=plain
```

Comprobar la salida de cada comando. El wrapper puede descargar dependencias;
un fallo de red no demuestra aceptación. Pruebas JVM no necesitan teléfono.
Un APK release sin firma no acredita instalación ni firma de distribución.
Los ensayos optativos contra API deben configurarse expresamente.

## Banco local y hardware

Inspeccionar procesos, puertos, contenedores y persistencia antes de arrancar.
PostgreSQL de banco conocido: `hydromate-postgres`; conservar su volumen, nunca
recrearlo para resolver un error. Leer `scripts/start_local.ps1` y las guías
embedded/mobile antes de ejecutarlos. Banco: Laravel HTTP8000 y MQTT1884 local.

`tests/smoke_api.py` del backend escribe datos sintéticos: solo banco autorizado,
con identidad de prueba; nunca identidad física en producción. No usar
migrate:fresh/refresh/reset ni borrar volúmenes. Revisar respaldo antes de migrar
datos persistentes.

USB ESP32 sirve para flasheo/serie; detectar puerto actual, no asumir COM3.
Cerrar Monitor Serie/Plotter antes de ocuparlo. Hotspot en 2.4 GHz. USB Android
solo para instalación, ADB/captura; uso normal por Internet. No flashear ni instalar
por una tarea exclusivamente documental.

Seguir [INTEGRATION](INTEGRATION.md) para evidencia nueva fechada: adquisición,
ACK de persistencia, GET de la misma secuencia y pantalla. Un socket abierto o
GET antiguo no demuestran el flujo completo. Distinguir sensor→backend de
sensor→pantalla y registrar fuentes/campos null.

## Producción: instrucciones para el administrador

Guías vigentes: [PUBLIC_ACCESS](PUBLIC_ACCESS.md) y [PRODUCTION](PRODUCTION.md).
Android:
`https://hydromate-kevin.duckdns.org:9443`; MQTT TLS mismo hostname:8884.
API loopback8081, MQTT1884 y BD5432 internos no son direcciones públicas del teléfono.

Solo el administrador, como `deploy-hydromate`, en el checkout real de la VPS,
con Docker rootless y archivos privados ya provisionados, utiliza:

```sh
sh deployment/deploy.sh /etc/hydromate/.env --mqtt --public
```

El script localiza su raíz. Para comandos manuales, `HM_REPO` debe contener el
checkout existente, no un directorio supuesto en `~`:

```sh
docker compose -p hydromate -f "$HM_REPO/compose.production.yml" --env-file /etc/hydromate/.env --profile mqtt --profile public ps
```

El despliegue incluye `php artisan migrate --force`; no implica permiso para
operarlo desde este chat. No operar puertos80/443/8443/8883, Docker global,
AppArmor del host ni recursos ajenos. Nunca down -v/prune. Validación TLS pública
y transmisión requieren pedido pertinente; pruebas offline no las sustituyen.

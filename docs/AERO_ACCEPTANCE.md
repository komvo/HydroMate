# Aceptación HydroMate Jardín de cristal — 2026-10-04

Android 0.6.0-garden compilado e instalado por USB. Fondo botánico claro y
recuadros verdes translúcidos revisados en vistas nativas del teléfono.
La aceptación de interacción y accesibilidad sigue siendo parcial.

## Resultados observados

- Gradle: testDebugUnitTest, lintDebug, assembleDebug y assembleRelease correctos.
  17 pruebas JVM correctas y 1 GET opt-in omitido; cero fallos. Docker no tenía
  daemon disponible; el GET exitoso del 03/10 es evidencia histórica.
- Lint: cero errores y tres avisos: OldTargetApi, NewerVersionAvailable de JSON
  de tests y DiscouragedApi por orientación fija exclusiva de revisión debug.
- Release sin fixtures, VisualCheckActivity ni permiso de tráfico cleartext.
- Telemetry, RequestFence, ConnectionStore, proveedores y pruebas coinciden con
  el respaldo previo. MainActivity y ReadingState conservan su contenido previo
  al jardín. Backend, BD y firmware no se modificaron.
- Recursos locales: 16 PNG y un fondo JPEG; procedencia y hashes en recursos.json.
  Cultivo/emblema original y cuatro variantes de barra conservados. Recarga y
  TDS renovados; pH mantiene matraz. Sin descargas remotas en ejecución.
- 28 comprobaciones de contraste de texto diurno/nocturno sobre composiciones
  alfa de gradientes, placas y reflejos. Fondo botánico acotado conservadoramente
  entre negro/blanco bajo su velo. Mínimo calculado: **4.639:1**. Corregido el rojo
  de error y recapturado su estado; no equivale a certificar accesibilidad.

Resultado: [android-garden-2026-10-04.json](evidence/android-garden-2026-10-04.json).
Log: ../.local/garden-validation.log. Respaldo: ../.local/backups/android-crystal-nav-2026-10-04.
Sin Git; revisión local contra respaldo. Evidencias anteriores conservadas.

## Revisión en teléfono

2207117BPG, Android 13/API 33, 1080×2400 px, densidad 440, fuente de sistema 1,
navegación de tres botones. Instalación con install -r conserva configuración.
La apariencia guardada era sistema y activaba noche. Por la petición actual se
seleccionó la opción existente Jardín claro (mode=aero) solo en esta app debug,
con respaldo de la preferencia en .local/appearance-before-light-request.xml.
No se tocaron conexión/datos ni ajustes globales. MainActivity se abrió y capturó
con apariencia clara, servidor no disponible y valores ausentes:
[captura real](evidence/garden-light-2026-10-04/home-real-final.png).
No se afirma conexión exitosa con API, sensores o ESP32.

26 capturas y auditorías en evidence/garden-light-2026-10-04:

| Revisión | Resultado |
|---|---|
| Inicio 320/360/412 dp × fuente 1/1.3/2 | 9 composiciones sin recortes; reflujo a una columna |
| Inicio 393 dp | Jardín claro, follaje visible a través de tarjetas, ejemplo identificado |
| Carga, vacío, error, antigua, sensor ausente, una lectura | 6 estados; ausencias sin valores inventados |
| Historial, Cultivo, Control y Más | Sistema visual coherente en cinco destinos |
| Final de scroll de Inicio, Historial y Más | Contenido por encima de la barra |
| Noche | Verde profundo opcional, texto y arte legibles |
| Más y Control 320 dp/fuente 2 | Texto refluye; EditText conserva scroll horizontal nativo |
| Auditorías nativas | Cero recortes detectados; objetivos táctiles ≥48 dp |

[Inicio claro](evidence/garden-light-2026-10-04/home-demo-393.png).
Las auditorías usan getLineMax y excluyen scroll horizontal intencional de EditText.
La Activity aislada muestra “Prueba visual · datos simulados”, sin red, preferencias
ni órdenes. Ancho/fuente son locales; fija retrato y mantiene pantalla encendida
solo mientras está visible. No modifica ajustes globales. No representa varios
teléfonos físicos ni interacción de MainActivity. Se respetaron los bloqueos de
INJECT_EVENTS y WRITE_SETTINGS; no se automatizaron toques.

## Pendientes

- TalkBack, recorrido de foco y teclado externo.
- Edición con teclado abierto y conservación de borradores al navegar/girar.
- Giro físico final, gestos de sistema y actualizar arrastrando.
- Cambio real de torre/fuente durante petición en Activity; RequestFence sí tiene pruebas JVM.
- Arrancar servicios existentes y repetir GET por USB, sin recrear ni borrar datos.

## Reproducir

En mobile/:
```powershell
$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:assembleRelease --console=plain |
    Tee-Object -FilePath C:\Hydromate\.local\garden-validation.log
```

HYDROMATE_TEST_API solo cuando esté disponible el backend existente; usa GET.
Desde raíz, teléfono desbloqueado y USB autorizado; sustituir RUTA_ADB/SERIAL:
```powershell
python scripts/capture_eco_review.py --adb RUTA_ADB --serial SERIAL --set home --output docs/evidence/garden-light-2026-10-04
python scripts/capture_eco_review.py --adb RUTA_ADB --serial SERIAL --set screens --output docs/evidence/garden-light-2026-10-04
python scripts/capture_eco_review.py --adb RUTA_ADB --serial SERIAL --set matrix --output docs/evidence/garden-light-2026-10-04
python scripts/verify_eco.py --build-log .local/garden-validation.log --baseline .local/backups/android-crystal-nav-2026-10-04/mobile/src --evidence-dir docs/evidence/garden-light-2026-10-04 --report docs/evidence/android-garden-2026-10-04.json
```

El verificador recoge evidencias, no ejecuta la revisión visual. Para otra etapa,
elegir rutas nuevas. Para volver a la app: adb -s SERIAL shell am start -f 0x10008000
-n com.hydromate.mobile/.MainActivity. La demo normal continúa explícita solo debug
en Más → Demostración; release no contiene esa función y no está publicado.

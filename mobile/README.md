# HydroMate Android — 0.6.0 Jardín de cristal

Cliente Kotlin nativo de Laravel. Consulta hasta 20 recepciones por torre;
Android no accede directamente a PostgreSQL, MQTT ni actuadores.

## Dirección vigente

Frutiger Aero/Eco según los dos MD solicitados el 04/10: fondo vegetal luminoso, cristal verde claro translúcido, botones
convexos, emblema botánico húmedo y cinco destinos: Inicio, Historial, Cultivo,
Control, Más. Vistas programáticas Android, Canvas, dieciséis PNG locales con alfa y un fondo JPEG optimizado.
Sin Compose, WebView, motor 3D ni dependencias nuevas.

- Inicio: emblema/torre compactos, un aviso de consulta, cuatro instrumentos y nivel.
- Historial: puntos aislados y lista de recepciones, fechas y unidades.
- Cultivo y Control: perfiles/integración pendientes explícitos; sin órdenes.
- Más: conexión, diagnóstico plegable, apariencia y créditos.
- Pantallas estrechas/texto grande: una columna, menos decoración y reflujo.
- Jardín con paneles claros inicial; se respeta la elección guardada de seguir sistema.

Diseño y recursos: ../docs/AERO_DESIGN.md, ../docs/recursos.json y
../THIRD_PARTY_NOTICES. El emblema, las ilustraciones y el fondo son originales generados con IA,
con una misma referencia de material/luz; el manifiesto incluye todos los prompts.
Solo Inicio, Historial, Control y Más de la barra usan cuatro variantes de cristal
con menos detalle. Cultivo y los iconos de las pantallas conservan los originales.
Recarga usa una flecha circular y TDS un vaso con minerales, distinto del matraz
de pH. Superficies y puntos perlados son gráficos nativos propios. Los PNG Fluent
anteriores se retiraron; se conserva su aviso MIT histórico.

## Datos y demostración

No cambió la lógica funcional en este incremento: recepción no equivale a
captura; luz/nivel son porcentajes relativos, sin rangos agronómicos configurados.
Servidor disponible no confirma ESP32 ni sensores. Valores ausentes: raya.
Contrato v1 estricto y protección de respuestas tardías conservados.

Debug: Más → Demostración → Lecturas de ejemplo. Marca permanente
“Demostración · datos simulados”; nunca se activa por un fallo. Escenarios de
carga, vacío, error, antigua, sensor ausente (rechazo v1) y una/20 lecturas.
No guarda mediciones ni envía órdenes. Salir con “Conexión real”.

VisualCheckActivity es una revisión **adicional solo debug**, iniciada de forma
explícita por el script capture_eco_review.py. Recibe ancho/fuente/pantalla y
renderiza las mismas vistas con marca de prueba. No usa repositorio ni
preferencias y no cambia ajustes globales. Sirve para composición, no para
certificar interacción real, teclado, TalkBack o red. Ambas demos quedan fuera
de release.

## Compilar y verificar

Versiones conservadas: AGP 9.3.1, Gradle 9.5.0, JBR 25 de Android Studio,
compile SDK 37, target 35, min 26. Desde mobile/:

```powershell
$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:assembleRelease --console=plain |
    Tee-Object -FilePath C:\Hydromate\.local\garden-validation.log
```

HYDROMATE_TEST_API=http://127.0.0.1:8000 activa la prueba GET solo cuando los
servicios existentes están disponibles. Sin variable, se omite expresamente.
Después de capturas: usar verify_eco.py con las rutas de evidencia 0.6 para
conservar los resultados previos. Receta completa
y límites: ../docs/AERO_ACCEPTANCE.md. verify_aero.py corresponde a 0.3.

APK: app/build/outputs/apk/debug/app-debug.apk. Release se compila sin firmar
para validar exclusión de fixtures y HTTP; no es una publicación de tienda.

## Teléfono por USB

Arrancar servicios según ../docs/SETUP.md y conectar/autorizar teléfono.
Con ADB instalado y el serial obtenido de devices:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices
& $adb -s SERIAL install -r C:\Hydromate\mobile\app\build\outputs\apk\debug\app-debug.apk
& $adb -s SERIAL reverse tcp:8000 tcp:8000
& $adb -s SERIAL shell am start -f 0x10008000 -n com.hydromate.mobile/.MainActivity
```

Servidor USB: http://127.0.0.1:8000. Identificador sintético existente:
test-api-0865fd385681. Reverse no publica la API ni modifica firewall; comprobar
de nuevo tras desconectar. Emulador habitual: 10.0.2.2:8000. Wi-Fi/LAN requieren
una etapa explícita; el backend actual escucha solo loopback.

## Resultado del 04/10

17 tests JVM correctos y 1 integración omitida (Docker daemon no disponible).
Debug/release compilados, lint 0 errores/3 avisos (incluido retrato del visor debug). Instalado por USB en
Android 13. 26 revisiones de composición nativa: cinco pantallas, estados,
320/360/412 dp, fuentes 1/1.3/2, final de scroll y noche; sin recortes detectados.

Pendientes manuales: teclado/edición, giro final, gestos, TalkBack/foco,
lifecycle completo y GET real por USB. La revisión aislada no acredita esos
resultados. Evidencia: ../docs/evidence/android-garden-2026-10-04.json.

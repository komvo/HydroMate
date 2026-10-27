# Estado actual — 2026-10-21

## Corrección del presupuesto T5 — 2026-10-21

Importes actualizados por confirmación del responsable: compras anteriores
$2,055.94; electrónica pagada $1,168.00; segundo TDS $270.00; total $3,493.94;
máximo vigente $6,000.00; disponible $2,506.06. Desglose electrónico $1,174.23,
diferencia $6.23 respecto de lo pagado, sin causa informada. Sustituye cifras
preliminares del T5; no altera documentos históricos. Nombres de compra PH014 y
MOSFET dual Noyito no demuestran equivalencia con PH-4502C/D4184.
Versión actual renombrada por el responsable en Documentos PDC/
T5_PDC_1288703.docx y PDF,17 páginas. Copia de entrega,
generador e índice de presupuesto actualizados conservando las otras ediciones.

## Taller 8 revisado y acotado — 2026-10-21

Partiendo del Word corregido por el usuario: Documentos PDC/
T8_PDC_1288703.docx y PDF,15 páginas. Tres diagramas (arquitectura y
despliegue combinados, hardware y módulos), tablas de interfaces y trazabilidad
de los16 mínimos. Se retiran bitácora, ADR repetidos y ejemplos extensos; se
expresan decisiones con justificación y referencias oficiales, sin atribuir
implementación a auth/FCM/BLE/actuadores. Original del usuario preservado.
Revisión visual completa y comprobación de cobertura; D61 registra continuidad.

## Talleres 5 y 8 con formato académico — 2026-10-21

Copias Word/PDF en Documentos PDC/T5_PDC_1288703 y T8_PDC_1288703.
Formato tomado de T7: portada institucional, borde verde, Arial, tablas y pie
por taller. T5 conserva evidencias y fotos del 21/10 (18 páginas); T8 conserva
el contenido y corte de diseño del 14/10 (43 páginas), con láminas horizontales
amplias para diagramas y matrices. Exportados con Word y revisados como imágenes.
Originales preservados; adaptación de presentación, sin cambios de implementación.

## Documento de evidencias del Taller 5 — 2026-10-21

Entrega organizada en talleres/taller-05/entrega-2026-10-21/: Word de17 páginas
revisadas mediante exportación Word16 y rasterizador empaquetado; seis figuras
(dos diagramas, Inicio/Historial nuevos y dos fotos físicas aportadas), video30s
de producción, consultas HTTPS200 y20 registros reales. Matriz de requisitos,
cronograma al2/12, presupuesto preliminar con cargos por conciliar y ocho riesgos.
Fuentes históricas y límites local/nube explícitos; sin afirmar calibración ni
actuadores probados. Sin modificaciones de código o configuración ni acceso SSH.
Seguimiento operativo privado, fuera del reporte/anexos: .local/seguimiento/
refresco-medicion-2026-10-21.md. Por instrucción del usuario no se diagnostica ahora.

## Flujo físico público comprobado — 2026-10-21

Red privada corregida y firmware cargado en COM3 con hash verificado, NVS
conservada. Usuario sincronizó cuentas MQTT en su VPS; bridge conectado y
suscrito según logs aportados. Observación local ESP32: MQTT TLS8884 conectado,
14 muestras nuevas consecutivas4201–4214 con ACK STORED y pendiente1801 también
confirmada. Cero publish fallidos y cero fallos MQTT después de conectar;
un rechazo previo a sincronizar cuenta. SAMPLE→STORED258–577ms (media409ms),
sin incluir frontend. Android Producción/HTTPS9443/hydromate-01: Inicio e
Historial muestran pH/lux/flotador; segunda consulta cambia fecha/valores.
Evidencia public-flow-esp32-android-2026-10-21.json y PNG en docs/evidence/.
Temperatura invalid/null; TDS/EC unavailable en esa prueba. Calibración pH no
revalidada. Sin acceso SSH/VPS del asistente; operaciones remotas hechas por usuario.

Usuario confirma reemplazo TDS funcionando en ADS1115 A1 y DS18B20 GPIO4.
Temperatura recuperada: GET público de secuencia4408 muestra23.5°C/origen real.
La evidencia anterior se conserva tal como ocurrió.

## TDS, eventos y refresco con adquisición — incremento21/10

Implementado: TDS A1 con mediana/compensación DS18B20; eventos configurables de
luz/nivel/pH/temperatura/TDS, respaldo30s y pendiente NVS intacto hasta ACK.
Solicitud Android→POST HTTPS→caché UUID30s→bridge→commands/measure→ESP32→v3
correlacionada→PostgreSQL. Vistas Android visibles consultan cada2s; botón pide
adquisición nueva y distingue caducidad/API antigua. D60 y PUBLIC_ACCESS.md.

Observado localmente: PHP29/194, Python10/10 incluyendo guardas rootless; pruebas
C++ de conversión/mediana/eventos. Android debug/release y lint pasan; JVM33
pruebas,31 ejecutadas sin fallos y2 opt-in omitidas; incluye HTTPS con CA de test,
respuesta del pipeline MQTT y TDS con temperatura válida/ausente. Nueva APK debug
instalada por USB conservando configuración. Docker aislado hydromate-validation:
solicitud HTTPS→comando MQTT TLS no retenido→productor simulado→bridge→PostgreSQL
→GET correlacionado pasa; registro anterior no satisface, caducidad sin respuesta
y límites públicos403/404/422 comprobados. Regresión MQTT TLS10 transmisiones,
duplicado/conflicto/inválido pasa. Solo fixtures locales; ensayo detenido sin
borrar volúmenes. Esa prueba local no acredita recepción física pública.

Firmware compilado (1076345bytes,82%; RAM50812bytes,15%) y cargado en COM3 con
hash verificado, NVS conservada. Captura física4601–4604: cuatro muestras nuevas,
cuatro STORED, coincidencia completa con GET público; TDS770.32–771.05ppm y
temperatura23.50°C real. Cambios del flotador generan water_change antes de30s.
Usuario cubre/destapa BH1750: API guarda light_change hasta13.33lux y recuperación.
Android Historial observado muestra fila4718: TDS768.76ppm/23.50°C,01:16:39 local.
Evidencia JSON/PNG: docs/evidence/tds-events-2026-10-21.json y
tds-android-history-2026-10-21.png. Sin calibración ni latencia hasta pantalla medida.

Responsable informa posteriormente que desplegó la actualización y el botón
solicita lecturas; es confirmación del usuario, sin nueva validación de esa función
en esta etapa documental. Seguimiento reservado en la ruta privada indicada arriba.
Operación remota del administrador, sin SSH del asistente.
Rama autorizada del incremento de código: codex/tds-events-refresh.

## Producción preparada para ejecutor externo — 2026-10-14

- Petición posterior sustituye acceso SSH: preparar únicamente repositorio para
  despliegue automático de main; no pedir secretos ni entrar al VPS. Todos los
  recursos/configuraciones chitiito-* intocables. D55 y PRODUCTION.md.
- Dockerfile backend multietapa: PHP8.4/Apache en8080, www-data, dependencias
  composer.lock sin dev; .env/cachés/logs excluidos del contexto. Healthcheck
  /up + SELECT1 sin escribir datos. Binario Composer y PHPUnit fuera de imagen
  final; dependencias instaladas en etapa separada.
- compose.production.yml, proyecto hydromate: API127.0.0.1:8081, PostgreSQL16
  en red interna sin publicar5432; rol app no superusuario. Redes/volúmenes
  exclusivos con prefijo propio, sin host network ni enlaces a chitiito.
  Perfil mqtt opcional: Mosquitto autenticado/TLS8884,1884 solo interno;
  bridge Paho existente con bandeja persistente propia. Android fuera de VPS.
- Plantilla raíz .env.example sin secretos; .env real solo VPS. Archivo externo
  /etc/hydromate/.env para checkout de solo lectura; hook deployment/deploy.sh
  usa siempre -p hydromate, build/up de servicios propios y migrate --force.
  Sin workflow SSH, cambios de firewall ni servicios80/443/8883.
- Observado localmente: ambas imágenes construidas; entorno **hydromate-validation**
  con volúmenes separados y valores ficticios. API/BD saludables, migraciones
  completas aplicadas y segunda ejecución «Nothing to migrate». UID33 en API,
  sin .env/PHPUnit en imagen; rol DB hydromate sin superuser/createdb/createrole.
- PHPUnit existente:19 tests/118 assertions pasan. Smoke HTTP existente en
  puerto8081 pasa (11 filas sintéticas,201/422/409/GET). Diez publicaciones
  sintéticas por TLS8884 pasan y coinciden campo por campo con API; reenvío
  idéntico sin duplicado, conflicto e inválido detectados. MQTT anónimo rechazado;
  conexión sin confiar en CA de prueba rechazada. Certificado efímero localhost
  y cuentas ficticias solo en .local, no certificados/secretos de producción.
- Corte solo API de ensayo: secuencia12 conservada pending en SQLite; después
  de stop/start de API/bridge/BD propia se recuperó y se verificó por GET.
  Filas sintéticas HTTP también conservadas tras reinicio. Consulta local8000
  preserva exactamente90 filas históricas; no se modificó .env/backend local.
  Entorno de ensayo detenido al terminar, contenedores/volúmenes conservados.
- Revisión de parada: API/bridge inicialmente agotaban timeout (137). Se añadió
  init a ambos, SIGTERM para API y límite Apache de parada gradual; imagen/API
  revalidada y ensayo final detenido sin kill forzado (API0, bridge143).
- Evidencia: docs/evidence/production-stack-2026-10-14.json,
  production-http-2026-10-14.json y production-mqtt-tls-2026-10-14.json.
  Verificador de aislamiento: scripts/verify_production_compose.py, usa fixtures
  y no inicia servicios. Shell/PHP y git diff --check pasan.
- Revisión previa al commit: ambas imágenes reconstruidas, PHPUnit19/118,
  aislamiento Compose, migrate --force sin pendientes, smoke HTTP y diez nuevos
  mensajes MQTT TLS sintéticos pasan; reenvío/conflicto/inválido comprobados.
  Desarrollo conserva sus90 filas idénticas. Evidencia adicional:
  production-review-2026-10-14.json y production-review-http-2026-10-14.json.
  Rama nueva codex/production-shared-vps; publicación autorizada sin merge a main.
- Pendiente fuera de esta tarea: administrador provisiona configuración privada,
  certificados y endpoint HTTPS protegido independiente, conecta ejecutor de main,
  despliega y repite pruebas físicas/nube. No afirmar VPS desplegada. Los cambios
  de producción se revisan para commit/push autorizado en rama nueva, sin merge
  a main. Las modificaciones previas ajenas a producción se conservan locales.

## Taller 5 — implementación local del 2026-10-07

- Usuario solicita ejecutar local paso a paso y explicar cómo replicarlo. Guía:
  `talleres/taller-05/procedimiento-local.md`; plan/presupuesto/diez riesgos en
  `plan-accion.md`. PDF técnico local provisional generado y
  renderizado/revisado; no es reporte final ni evidencia de nube.
- PostgreSQL existente arrancado, volumen conservado y backup privado previo
  a migración. v2 aditiva aplicada únicamente por --path; Sanctum sigue pendiente.
  Esquema real exportado por solo lectura en pruebas/esquema-postgresql-2026-10-07.json.
- Contrato v2 implementado: lux, flotador booleano y origen por variable; v1
  compatible/preservado en TELEMETRY_CONTRACT_V1.md. TDS del firmware fijo 650
  ppm simulado; temperatura/pH/lux/flotador se leen físicamente al ejecutar placa.
- Bridge Python/Paho con bandeja SQLite privada, reintentos y ACK después de
  persistencia. Broker separado autenticado 1884 y ACL; 1883 previo intacto.
  Tres ensayos de diez transmisiones sintéticas pasan (incluye posterior a
  reinicio Docker), inválido 422 y conflicto/repetición sin sobrescribir.
  Primera prueba fallida conservada; no cuenta como prueba física.
- Laravel 13.33.0/PHP 8.4.26: 19 pruebas/118 assertions en memoria pasan. Android
  assembleDebug/testDebugUnitTest/lintDebug pasan: 20 tests; APK actual reinstalada
  por USB/reverse. `hydromate-01` configurado manualmente; estados carga/sin datos
  y posteriormente lecturas físicas observados. Captura pública de Inicio conserva
  pH/temperatura/lux/flotador y TDS simulado. MIUI bloquea input tap; navegación manual.
- Usuario autorizó red doméstica Private y regla MQTT 1884/Private/LocalSubnet.
  Requirió ejecución administrativa; ruta de programa corregida tras error
  0x80070057, perfil/regla posteriormente verificados. Sin cambios del router.
- Docker dio error interno/timeout PostgreSQL durante compilación; reinicio
  normal Desktop y arranque del contenedor existente recuperaron pg_isready,
  consulta de esquema y ensayo MQTT. No se borraron/recrearon datos/volúmenes.
- ESP32 detectado COM3. Firmware nuevo en embedded/HydroMateTelemetry, sin
  actuadores; original PruebaSensores1 intacto. Primera compilación pasó (79 %
  programa/14 % RAM). Configuración privada completada; compilación final y carga
  COM3 realizadas. pH inicialmente ~0.035 V: usuario corrigió conexión/alimentación;
  después se capturó muestra 101 (28.56 °C, 30 lux, pH 10.54, flotador false,
  TDS 650 simulado). No equivale a calibración. Ensayo físico de 421 s no recibió
  ACK ni encontró registros por API; evidencia fallida conservada. El
  usuario detectó SSID exclusivo de 5 GHz y cambió secrets.h a 2.4 GHz;
  recompilado/cargado: 1 037 864 bytes programa/49 040 RAM. Ensayo 2.4 GHz pasa:
  secuencias 101, 401–409 verificadas campo por campo contra API. Pendiente 101
  recuperado tras reinicio y confirmado; no se borró NVS. Luz 1.67–185 lux y ambos
  estados del flotador observados tras intervención física del usuario. JSON fuente:
  pruebas/esp32-fisico-24ghz-2026-10-07.json. No es calibración de sensores.
- Historial Android observado con gráfica y registros físicos; capturas en pruebas/.
  Aproximación fin de adquisición–interfaz: 8.24 s en una muestra (incluye abrir
  app/inspección ADB). Primer intento falló al extraer UI; repetición conservada.
  Corte broker 1884: fallos MQTT, pendiente 901 conservado y entregado al recuperar;
  901/902 verificados por API. Servicios restablecidos, datos conservados.
- Video local Android de 10.06 s: consulta real/reapertura, fotogramas revisados.
  No muestra montaje/nube. Evidencia en pruebas/android-consulta-local-2026-10-07.mp4.
- Pendientes de cierre: video final conjunto del montaje; VPS contratado/desplegado con
  TLS/HTTPS/API protegida, repetición en nube, decisión docente sobre actuador y
  reporte final. No afirmar Taller 5 completo todavía.

Esta sección sustituye los pendientes de implementación de la revisión anterior;
las notas siguientes se conservan como historial del mismo día.

## Taller de viabilidad pendiente — revisión del 2026-10-07

- Renombre solicitado: `Documentos PDC/tsts/tsts.ino` pasa a
  `Documentos PDC/tests/PruebaSensores1.ino`. Contenido idéntico comprobado por
  SHA-256; referencias actualizadas. No se modificó ni ejecutó el firmware.

- Limpieza de documentación GitHub solicitada después de la subida: retirar de
  la versión actual las tres carpetas y los 18 archivos señalados en capturas.
  Originales conservados localmente y excluidos de Git; talleres y sketch `tsts`
  conservados. Se actualizaron política, README y referencias de bitácora sin
  cambiar sus resultados registrados ni reescribir el historial anterior.

- Aclaración posterior del usuario: usar temperatura, pH, luz y flotador reales,
  más TDS simulado identificado por variable; reemplaza la propuesta inicial de
  una sola temperatura. No implementado. BH1750 debe conservar lux y flotador
  nivel discreto; v1 necesita evolución antes de integrar esos datos.
- Sketch original de pruebas: `Documentos PDC/tests/PruebaSensores1.ino`.
  Conexión vigente confirmada21/10: TDS en ADS1115 A1. El firmware de telemetría
  y documentación operativa usan esa entrada.
- OVHcloud VPS-1 compartido con un proyecto similar aceptado para preparar la
  PoC. Sin compra/despliegue comprobados; separar aplicaciones/datos/permisos.
- Usuario solicita primero repositorio GitHub en `komvo`, con documentos,
  código y pruebas; autoriza posteriormente que sea público. Git local inicializado,
  README/política preparados y remoto https://github.com/komvo/HydroMate creado.
  Versión inicial subida y verificada contra GitHub: 540 archivos, `main`;
  commits originales conservados. Transferencia completa requirió lotes por
  errores HTTP 408, sin borrar archivos ni reescribir el historial original.
  Secretos y archivos locales excluidos; `.env.example` sin contraseñas asignadas.
- Requisito docente comunicado por usuario: talleres organizados en GitHub,
  preferentemente PDF; desde Taller 5, reportes técnicos con código, capturas,
  errores/resultados, diagramas y archivos utilizados. `talleres/` contiene copias
  verificadas por hash de los PDF existentes T1–T4/T6/T7 y estructura técnica T5.
  No se afirma revisión/aprobación de T6/T7 ni reporte final/pruebas completas T5.

- Usuario confirma entrega vencida el 16 de septiembre; fecha final del proyecto
  todavía sin definir. El 30/11 es referencia histórica, no cierre confirmado.
- Revisada la bitácora del 05/10 en `Documentos PDC/`: ESP32 DevKit V1,
  DS18B20 (GPIO 4), BH1750, flotador (GPIO 27), ADS1115 y pH funcionales según
  pruebas registradas. I2C en GPIO 21/22; pH en A0, calibración de dos puntos
  documentada. Usuario confirma sensores conectados y probados salvo TDS.
- TDS Meter V1.0 con señal baja/no confiable: reemplazo seleccionado en bitácora;
  no afirmar compra/recepción del reemplazo ni usar sus ppm como medición válida.
  Bomba/D4184/potencia figuran pendientes de integración en esa fuente.
- No se repitieron ensayos físicos ni pruebas de red en esta revisión. Falta
  demostrar ESP32 real → backend en nube → PostgreSQL → Android, diez envíos,
  fallos/tiempos, Git y paquete de evidencias. Contrato/API/BD/Android v1 exigen
  todas las variables: necesitan evolución compatible para una sola lectura real.
- Plan propuesto para revisión: usar primero temperatura; no depender del TDS
  ni de integración de potencia. MQTT/TLS sigue como arquitectura seleccionada.
  No se implementó/desplegó el plan. Aplazar comando físico requiere autorización
  docente; recepción tardía y nueva fecha de entrega todavía por acordar.

Fuente local: `Documentos PDC/HydroMate_Bitacora_Pruebas_Sensores_Diagnostico_TDS_05-10-2026.docx`.
Retirada de la versión actual de GitHub por solicitud del usuario; copia local conservada.

## Reporte en Word — 2026-10-06

- Reporte de seis páginas: [estado del proyecto](../reports/HydroMate_Estado_Actual_2026-10-06.docx).
  Resume avances, evidencia con fecha, aceptación Android, hardware, ahorro,
  nube y próximos pasos. No modifica código, datos ni decisiones técnicas.
- Elaborado con las pruebas registradas del 30/09, 03/10 y 04/10; no se repitieron
  pruebas de backend/Android ni ensayos físicos para elaborar este reporte.

## Ahorro energético y procesos — documentación del 2026-10-04

- Usuario confirma ESP32 con fuente y control de bombas. Dirección D44–D47 en
  [ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md): controlador disponible,
  modem-sleep y frecuencia dinámica por etapas; sin reiniciar cada 5 s ni deep
  sleep durante operación normal. Sueño ligero condicionado a pruebas físicas.
- Propuesta de banco: adquirir cada 5 s, publicar cada 300 s estable, 30 s en
  pruebas con vencimiento y avisos por cambios/fallos. Seguridad independiente;
  tiempos admisibles, calibración y límites físicos todavía pendientes.
- Identificadas 14 mejoras priorizadas de firmware, contrato, red, consultas,
  Android, despliegue y energía total. No implementadas por esta documentación.
  El contrato v1 necesita evolución antes de sensores parciales, eventos o cola
  tardía: no admite hora de adquisición ni magnitudes reales de flotador/BH1750.
- Cálculos y enlaces verificados; 300 s implica 90 % menos mensajes rutinarios
  que 30 s, no 90 % de ahorro eléctrico. Sin medidas de consumo ni pruebas físicas.
- Render + Aiven es candidato para API/BD de prueba, no contratación/despliegue.
  MQTT/bridge y protección de acceso siguen pendientes. Ningún servicio expuesto.
- Evidencia: evidence/energy-review-2026-10-04.json. Respaldo documental:
  .local/backups/energy-docs-2026-10-04. Código y datos conservados; sin Git.

## Android Jardín de cristal 0.6 — incremento del 2026-10-04

- Dirección vigente D43: fondo botánico mucho más claro y paneles verdes
  translúcidos, con hojas visibles detrás del cristal. Cinco pestañas y estilo
  Frutiger Aero/Eco. Cuatro variantes de iconos solo para la barra; Cultivo
  conserva el emblema original. Recarga nueva y pH/TDS diferenciados.
- API, contrato, firmware y lógica de datos conservados. Sin rangos, perfiles ni
  estados físicos inventados. Demo explícita solo debug, nunca fallback.
- Instalado en teléfono 2207117BPG/Android 13 por USB. MainActivity abierta y
  estado de fallo real de consulta capturado. Preferencia de apariencia del
  teléfono cambiada de sistema a Jardín claro por la petición actual; sin
  cambios globales. Respaldo: .local/appearance-before-light-request.xml.
- 26 revisiones nativas de composición con Activity debug aislada: 320/360/412 dp,
  fuentes 1/1.3/2, cinco pantallas, estados, fin de scroll y noche. Sin recortes
  detectados ni objetivos táctiles menores de 48 dp. No son pruebas de interacción
  con red ni varios teléfonos. Capturas en evidence/garden-light-2026-10-04.
  Revisión debug vertical y encendida mientras está visible, sin ajustes globales.
- Debug/release compilan. 17 pruebas JVM correctas, 1 GET opt-in omitido; lint
  0 errores y 3 avisos: target, JSON de tests y orientación de revisión debug.
  Release sin fixtures/Activity de revisión/HTTP. 28 comprobaciones de contraste,
  mínimo calculado 4.639:1.
- Docker daemon no disponible el 04/10. Laravel se inició en 127.0.0.1:8000 y ADB
  reverse se preparó; no se comprobó GET exitoso con PostgreSQL ese día. No se
  borraron datos, recrearon contenedores ni modificaron firewall/credenciales.
- APK: mobile/app/build/outputs/apk/debug/app-debug.apk (0.6.0-garden).
  Evidencia: evidence/android-garden-2026-10-04.json. Diseño, procedencia y aceptación:
  AERO_DESIGN.md, recursos.json y AERO_ACCEPTANCE.md.
- Pendiente: TalkBack/foco, teclado/edición, giro físico final, gestos, lifecycle
  completo y GET real por USB. Android bloquea toques/cambios globales por ADB;
  no se alteraron esos permisos.
- Respaldo: .local/backups/android-crystal-nav-2026-10-04. Las capturas eco,
  crystal, readable y garden oscuro se conservan como históricas. Sin Git; comparación local de
  cambios, sin commit/push. Conviene inicializar Git antes del próximo incremento.

## Base comprobada e historial

Prioridad vigente: PostgreSQL → Laravel API → Android mínimo → ESP32 físico.
Wokwi/Blade reemplazados; no iniciar perfiles/autenticación/actuadores por estética.

- 30/09: API Laravel/PostgreSQL, identidad por torre, validación v1 y UNIQUE de
  device_id/sequence probados. Datos sintéticos existentes conservados:
  test-api-0865fd385681. 17 pruebas backend/104 assertions en SQLite aislada.
- Volumen PostgreSQL anónimo confirmado en su etapa; reutilizarlo si se recrea
  explícitamente el contenedor. No se probó recreación ni se autoriza borrar datos.
- 03/10: Android 0.2 y luego 0.3 Aero. En esa fecha, 18 pruebas JVM con GET real
  correctas, sin teléfono para QA visual. Es evidencia histórica, no nueva.
  Dirección visual 0.3 reemplazada por D36/D37; comportamiento D33/D34 vigente.
- Evidencias anteriores: android-aero-2026-10-03.json, android-ux-2026-10-03.json,
  backend-step1-http.json y postgres-step1.json. Estado previo archivado en
  evidence/STATUS-2026-10-03.md; decisiones no borradas.

## Siguiente paso

Completar las pruebas manuales Android pendientes y comprobar servicios existentes.
Antes de sensores/firmware, confirmar hardware y plazos de seguridad, y diseñar la
evolución compatible de TELEMETRY_CONTRACT descrita en ENERGY_OPTIMIZATION.
Implementar/medir el ahorro por etapas; no afirmar sensores calibrados, comandos
físicos ni consumo reducido sin prueba. Si se prepara nube, resolver acceso y
MQTT/bridge sin asumir que un web service gratuito cubre el sistema completo.


## Reconciliación pública/rootless — 2026-10-14

Rama codex/public-rootless-hydromate reconciliada con origin/main; sin merge a main.
Se restauran íntegramente talleres/PDFs/evidencias originales y rutas de contexto
originales en docs; sin .project ni reorganización documental. Cambios limitados
al acceso HTTPS8443/MQTT TLS8884/rootless y dependencia funcional v3.
Hostname confirmado hydromate-kevin.duckdns.org; cuenta deploy-hydromate.
Guía PUBLIC_ACCESS.md. Pruebas públicas físicas/VPS pendientes, sin SSH/secretos.
La información anterior es histórica; el contrato v3 sustituye TDS simulado por
null/origen, producción Android HTTPS/real_only y configuración separada.

Validación repetida después de reconciliar:25 PHPUnit/157 assertions,28 Android
sin omitidas,6 Python,Compose,MQTT TLS diez mensajes,smokeHTTP/HTTPS y firmware
pasan. Debug/release/lint pasan;3 avisos existentes,0 errores. CA/hostname
incorrectos rechazados y POST público403. Conservados556 archivos de main y382
activos protegidos; originales completos de10 documentos preservados. Cero
eliminaciones/renombres netos; sin conflictos Git ni acceso VPS. Registro en
evidence/public-rootless-readiness-2026-10-14.json.

## Imagen Mosquitto propia para rootless — 2026-10-14

Diagnóstico VPS comunicado por usuario: bind mounts individuales de conf/ACL
impiden abrir configuración, aunque son legibles por1883. Se sustituyen por
COPY en imagen hydromate-mosquitto basada2.0.22, ambos archivos1883:1883/640.
UID/GID de ejecución1883; único bind secretos read-only, volumen mqtt_data intacto.
Hook --mqtt construye broker y bridge. No cambian ACL, certificados ni passwords.
Observado local: build, arranque directo mosquitto -c config -v, Compose saludable,
lectura/propiedad conf/ACL, escritura en volumen existente, política Compose,
6 pruebas Python y10 mensajes MQTT TLS→bridge→PostgreSQL→GET/HTTPS pasan.
Pruebas con secretos ficticios previos compatibles; sin datos físicos nuevos,
sin VPS ni certificación del namespace remoto. Rama codex/mosquitto-baked-config.

## HTTPS público9443 — 2026-10-14

Por puerto8443 ocupado confirmado por usuario, HTTPS propio cambia exclusivamente
a9443 (host/listener/healthcheck/Nginx). URL definitiva
https://hydromate-kevin.duckdns.org:9443; MQTT8884/1884, rootless y aislamiento
intactos. Mosquitto mantiene binario propio /usr/local/bin/hydromate-mosquitto.
APP_URL de despliegue exige9443; preflight y Compose rechazan8443. Android toma
la URL única de .env.example, sin URL duplicada en código; perfil guardado anterior
se actualiza manualmente en Conexión/Producción. Guía PUBLIC_ACCESS.md.
Observado local:25 PHPUnit/157 assertions,29 Android sin omitidas,8 Python,
debug/release/lint (3 avisos existentes),10 mensajes MQTT TLS y GET HTTPS9443
pasan. Gate PHP acepta9443/rechaza8443/443/ruta; CA ajena/hostname erróneo y POST
público rechazados. Primera ejecución con compilación simultánea tuvo timeouts;
repetición pasó. No se modifican JSON de evidencia histórica del puerto anterior.
Sin VPS, reglas remotas ni pruebas físicas nuevas. Rama codex/https-9443.

## Arduino IDE y carga de telemetría TLS — 2026-10-14

ArduinoJson7.4.2 estaba en las bibliotecas CLI aisladas pero faltaba en el
sketchbook del IDE. Copiada allí desde la instalación local; helper idempotente
scripts/install_arduino_ide_libraries.ps1 y procedimiento en embedded/README.md.
CA privada inicialmente no era PEM: configuradas raíces públicas oficiales
ISRG Root X1/X2 en secrets.h ignorado, conservando las credenciales MQTT.
Compilación ESP32 Dev Module/core3.3.11 correcta (1069905 bytes,81%; RAM15%);
carga COM3 verificada por hash, sin erase/NVS ni actuadores. Primer monitoreo95s:
Wi-Fi no encuentra SSID, sin conexión MQTT ni muestras confirmadas. Usuario
corrigió Wi-Fi localmente; segunda compilación/carga verificadas (1069889 bytes).
Configuración incorporada contrastada con header generado y binario; red nueva
todavía no encontrada por ESP32. Comprobación de red2.4GHz física pendiente.
Repetición95s tras usuario activar/corregir red: sigue WL_NO_SSID_AVAIL,
cero conexiones MQTT y cero confirmaciones STORED. Android Inicio sigue sin
lecturas para esta torre. Firmware coincide con Wi-Fi privado actual.
Diagnóstico USB del teléfono: hotspot activo a5240MHz (5GHz), incompatible
con radio2.4GHz del ESP32. Solicitado cambio de banda del hotspot, sin tocar
SSID/password ni firmware. Guardado2.4GHz aún mantenía AP activo5GHz; tras
reinicio manual del hotspot, frecuencia2412MHz y ESP32 WL_CONNECTED observados.
MQTT TLS alcanza broker, pero CONNECT rechazado con código5 (no autorizado).
MQTT_USER coincide con cuenta prevista hydromate-device; password privado
no vacío ni igual a plantilla. Pendiente contrastar autenticación con passwd
del broker, sin solicitar secretos ni cambiar cuentas/remoto. Sin STORED aún.
Usuario corrigió MQTT_PASSWORD en secrets.h privado; recompilación y carga
COM3 verificadas. Usuario/password contrastados con binario, sin escapes
desconocidos. Wi-Fi2412MHz y CA/puerto TLS preservados; broker aún responde
CONNECT5. Pendiente administrador comprobar cuenta montada y logs de Mosquitto
mediante comandos de solo lectura del proyecto hydromate. No cambiar passwords
ni desactivar autenticación como solución; todavía sin STORED/lecturas nuevas.
Última observación180s tras carga:35 rechazos MQTT5, cero conexiones aceptadas
y cero STORED; puerto serie liberado al terminar.
Android observado en Producción indica servidor disponible en última consulta;
eso aún no demuestra recepción de nuevas mediciones del ESP32 en la nube.
No acceso SSH/VPS, secretos versionados ni cambios de infraestructura.


## Taller de arquitectura integral — 2026-10-14

Entregable documental en reports/arquitectura-integral-2026-10-14/: DOCX/PDF de
41 páginas, 12 diagramas SVG/PNG, 14 ADR, 17 tablas, 26 requisitos trazados y 10
mensajes ilustrativos. Originales académicos conservados; referencias técnicas
consultadas. D59 ratifica responsabilidades/contratos existentes y etiqueta
propuestas de control, seguridad modular y dominio futuro. Física dosificación,
TDS, pines/voltajes/cierres/tiempos siguen pendientes de validación.
Render observado mediante Word 16 + rasterizador; páginas revisadas, JSON completo
por página, SVG válidos y propuesta de pines sin colisiones. qa.json conserva
límites/hashes; sin pruebas físicas/backend/VPS nuevas ni commit/push. Se incorpora
la carga v3 y monitoreo fallido 14/10 registrados por otro incremento, sin afirmar
recepción en nube. No se modifican sus cambios de firmware/librerías/credenciales.

## Rediseño Android Jardín líquido — 27/10/2026

D63 implementado en `mobile/` (solo UI): vidrio esmerilado sobre el fondo botánico,
barra flotante y nuevas pantallas. Build debug/release, lint y JVM (33; 4 opt-in
omitidas) correctos. Instalado por USB y revisado con 26 capturas nativas sin
recortes ni objetivos <48 dp tras cuatro correcciones; commit local sin push.
Pendientes en [AERO_ACCEPTANCE](AERO_ACCEPTANCE.md).

## Historial e Inicio comprensibles (D64) — 27/10/2026

Análisis en [UX_ANALYSIS](UX_ANALYSIS.md). Gráfica de línea con huecos, inspección
táctil, resumen y tabla en Historial; minigráficas, cambios y guía en Inicio.
Build debug/release y lint correctos; JVM 39 (35 ejecutadas, 4 opt-in omitidas).
Revisado en teléfono: 26 capturas sin recortes tras seis correcciones;
arrastre, diálogos y TalkBack sin verificar (AERO_ACCEPTANCE).
Commit local sin push.

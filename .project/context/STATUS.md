# Estado actual — 2026-10-14

## Publicación definitiva preparada — 14/10

Hostname confirmado hydromate-kevin.duckdns.org, HTTPS8443/MQTT TLS8884.
Usuario deploy-hydromate/Docker rootless: scripts con guard de cuenta/socket/daemon
y permisos certificados mediante namespace; no GID del host supuesto.
Plantilla privada en /etc/hydromate/.env y certificados /etc/hydromate/https,mqtt.
Gradle usa URL pública de plantilla salvo HYDROMATE_APP_URL explícita.
Guía exacta docs/PUBLIC_ACCESS.md. Sin acceso VPS ni nuevos secretos/firmware
físico; prueba pública/Android real pendiente. Commit/push a rama autorizados.
Rama de entrega: codex/public-rootless-hydromate, sin merge a main.
Repetición local:25 PHPUnit/157 assertions,3 bridge,3 guards rootless y28 Android
sin omitidas; debug/release/lint pasan (3 avisos existentes). Diez mensajes MQTT
TLS→bridge→PostgreSQL y smokeHTTP/HTTPS pasan. CA ajena/hostname incorrecto
rechazados; POST público403. Primer intento bajo compilación concurrente produjo
timeouts, preservados en .local; repetición pasa. Firmware producción con
plantilla privada ficticia/TLS y sin opt-in LAN compila:712869B programa/43228B
RAM; no cargado. Namespace VPS no ensayado. Evidencia local en
docs/evidence/public-rootless-readiness-2026-10-14.json.

## Integración vigente v3 — 14/10

- Acceso público preparado posteriormente: perfil public con Nginx rootless101
  exclusivo HTTPS8443, GET/HEAD API y POST externo403. API8081 loopback, BD interna,
  MQTT8884 TLS sin cambios de puertos80/443/8883. Recursos ajenos intactos.
  HYDROMATE_APP_URL es ahora única variable URL API/compilación Android; sustituye
  propiedad Gradle hydromate.productionUrl. Valores privados solo VPS/firmware.
  DNS-01/certificados propios/renovación con hook de recarga exclusiva; guía
  docs/PUBLIC_ACCESS.md. Dominio confirmado posteriormente; conectividad pública pendiente del admin.
  Ensayo local aislado pasa: GET HTTPS, CA inválida rechazada, POST403, recarga
  proxy/MQTT; 28 tests Android sin omitidas, incluidos HTTPS real en JVM y JSON
  de fixture física reproducida (no nueva transmisión). APK sin CA de ensayo.
  Firmware compila con guard8884 para TLS; no carga nueva ni teléfono requerido.

- Contrato v3 compatible con v1/v2: valores/origen por sensor, TDS/EC null,
  adquisición UTC opcional, filtro real_only y estado no_data/recent/stale.
- Android 0.7.0 debug/release compila, lint y 27 pruebas JVM pasan, incluidas
  consulta local y respuesta exportada del pipeline MQTT. Instalada por USB;
  desarrollo conservado. Producción exige HTTPS/filtrado, sin demo ni fallback,
  URL centralizada y perfiles separados. Inicio v3 físico observado el 14/10:
  temperatura/pH/lux/flotador, fecha y TDS no disponible. Historial abierto por
  usuario: gráfica pH y lista20 registros observadas; fecha/pH/temperatura/TDS
  de fila1701 comparados con API. Captura y verificación JSON guardadas.
- PHPUnit:25 tests/157 assertions, SQLite en memoria; tres tests bridge pasan.
  Imágenes/migración v3 probadas en hydromate-validation: diez mensajes simulados
  MQTT TLS→bridge→Laravel→PostgreSQL→GET; duplicado, conflicto y 422 correctos.
  Filtro/estado comprobados sobre PostgreSQL. Smoke v1/política Compose pasan.
  Recuperación v3 tras caída API/reinicio bridge también pasa; informe
  talleres/taller-05/pruebas/integracion-v3-verificacion-2026-10-14.json.
- BD de desarrollo respaldada antes de migración, sin borrar filas. Firmware
  v3 compilado/cargado COM3, NVS preservada. Primer ensayo falla -2 por IP vieja
  en regla HydroMate1884; usuario la corrigió como administrador el 14/10.
  Repetición pasa: diez adquisiciones NUEVAS1501–1510, cero fallos de envío,
  cada JSON serial/ACK comparado con API. Cuatro variables reales, TDS/EC null.
  Pendiente1201 recuperada idéntica tras corregir regla; temperatura null/invalid
  legítima conservada y aceptada por Android, no cuenta como adquisición nueva.
  Fin adquisición→ACK mediana404.5ms (primer envío3509ms incluye Wi-Fi inicial).
  Fin adquisición→pantalla verificada7571.19ms, muestra1701; incluye arranque de
  app/ADB, no benchmark de polling ni nube. Capturas y video12s reales guardados.
  Captura fallida conservada: integracion-v3-fisica-fallo-regla-lan-2026-10-14.json.
  Verificadas sin cambios las 90 filas históricas de desarrollo. Lint sin errores,
  tres avisos existentes. Comparación física/local probada; nube sigue pendiente.
- Guía docs/INTEGRATION.md. Sin SSH/VPS ni solicitud de secretos. HTTPS/MQTT TLS
  públicos pendientes: loopback VPS no sirve para teléfono. Recursos ajenos
  intactos. Pruebas locales/simuladas no acreditan nube.
- Seis copias PDF exactas retiradas con respaldo/hashes; originales intactos,
  enlaces en talleres/README. Contexto movido a .project/context; guías públicas
  en docs. Atribuciones/decisiones/evidencias históricas preservadas.
  Sin commit/push nuevo.

Los estados siguientes son históricos y no sustituyen este incremento.

## Revisión posterior de cierre Taller 5 — 2026-10-14

- Usuario cree haber desplegado; no hay URL pública/evidencia nueva de nube en
  repo revisado. No se certifica despliegue ni cierre del taller todavía.
- Remoto main=dccfc99 incorpora PR1/producción67da210; árbol coincide. Consulta
  remota/fetch de lectura, sin merge/push ni SSH por esta revisión.
- ESP32 COM3 y teléfono ADB presentes. Preferencias Android leídas sin cambios:
  http://127.0.0.1:8000, hydromate-01; frontend sigue configurado para desarrollo
  local. No captura serie, carga de firmware ni nueva medición física ejecutadas.
- Revisión punto por punto: talleres/taller-05/revision-cierre-2026-10-14.md.
  Material local suficiente para preparar ensayo; faltan URL y recorrido físico
  en nube, diez nuevas muestras, Android remoto, tiempo/fallo y video conjunto.
  Cronograma/presupuesto preliminar/diez riesgos presentes; autorización del
  aplazamiento de actuador comunicada por usuario, anexar constancia al reporte.

Siguiente paso vigente: comprobar URL pública sin solicitar secretos ni SSH;
después demostrar recorrido físico desplegado. Los estados históricos siguientes
no acreditan por sí mismos pruebas nuevas ni alojamiento en nube.

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

## Revisión de viabilidad y recuperación Docker — 2026-10-14

- Usuario solicita cumplimiento mínimo punto por punto y guía VPS. Matriz:
  `talleres/taller-05/cumplimiento-2026-10-14.md`; guía `despliegue-vps.md`.
  Fuentes recientes T6 actualizado/T7/bitácora sensores y planes de compras
  revisados sin modificar originales. Plan semanal hasta **02/12/2026**, fecha
  final confirmada; historia de compras/ejecución separada de trabajo futuro.
- Usuario confirma VPS OVHcloud Ubuntu prestado ($0), ya aloja otro proyecto;
  falta acceso SSH/inventario y despliegue HydroMate. Prefiere introducir
  credenciales en terminal. Se abrió terminal; intento con correo del panel
  todavía no acredita acceso al servidor. Faltan IP pública y usuario SSH real.
- Aplazamiento de actuador comunicado por usuario; anexar autorización docente
  y justificación de seguridad para taller. No se implementó comando físico.
- Docker 4.62.0 falló primero en `dockerInference` y después `engine.sock`:
  sockets temporales NTFS inaccesibles. Usuario comunica posible Reset to factory
  defaults; log registra reset de aplicación. Se inspeccionaron procesos/rutas,
  cerró Desktop fallido y conservaron carpetas temporales de ambos componentes
  antes de recrearlas juntas. No se eliminaron contenedores/volúmenes por el agente.
- Copia privada del disco Docker detenido: `.local/backups/docker-recovery-2026-10-14/docker_data.vhdx`,
  17,603,493,888 bytes, copia completada; no se probó restauración de ese disco.
  Respaldo PostgreSQL previo a v2 permanece con cabecera PGDMP, 19,852 bytes;
  no contiene por sí solo evidencia de lecturas físicas posteriores a la migración.
- Docker recuperado: contenedor/volumen original hydromate-postgres presentes,
  PostgreSQL arrancado mediante script existente; API Laravel loopback disponible.
  GET devuelve 90 filas históricas de hydromate-01, con origen declarado cuatro
  reales/TDS simulado; se verificó presencia de 101, 401–409, 701, 901/902. Consulta
  inválida limit=101 →422. No se insertaron nuevas muestras para esa comprobación.
  Evidencia: pruebas/persistencia-local-2026-10-14.json y esquema-postgresql-2026-10-14.json.
- PHPUnit observado hoy: **19 pruebas/118 assertions**, PHP 8.4.26, SQLite aislada.
  No prueba de nube. Primer intento con artisan desde raíz falló por ruta de
  PHPUnit; ejecución desde backend con vendor/bin/phpunit pasó.
- Captura serie agrega `--fresh-only`: cuenta solo SAMPLE nuevo y excluye RESTORED,
  conservando eventos. Cuatro comprobaciones con serie/API simuladas pasan;
  resultado en pruebas/verificacion-captura-2026-10-14.json. No ensayo físico nuevo.
  Diez entregas previas incluyen una recuperada + nueve nuevas; repetir diez nuevas
  consecutivas en nube para interpretación estricta del requisito.
- ESP32 no detectado por puerto serie en esta revisión; teléfono ADB apareció y
  luego dejó de estar disponible. Sin nueva captura/instalación/QA física hoy.
- README e índices corregidos; Git sin commit/push. T6_act DOCX/PDF preexistentes
  sin seguimiento conservados intactos; nuevos documentos no publicados.

Siguiente paso vigente: acceso SSH privado e inventario Ubuntu compartido;
preparar servicios HydroMate propios, HTTPS/MQTT TLS/protección de API, repetir
diez adquisiciones nuevas, fallos/latencia/Android y video conjunto. No afirmar
Taller 5 completo hasta cerrar nube y evidencias. Conciliar presupuesto electrónico
y cargos históricos; VPS prestado no garantiza alojamiento indefinido.

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
- Sketch localizado y revisado: `Documentos PDC/tests/PruebaSensores1.ino`; conserva pruebas
  locales, sin Wi-Fi/MQTT. Anuncia TDS en A1 pero lee A3: discrepancia histórica
  pendiente de resolver al integrar reemplazo; no se modificó el original.
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

- Reporte de seis páginas: [estado del proyecto](../../reports/HydroMate_Estado_Actual_2026-10-06.docx).
  Resume avances, evidencia con fecha, aceptación Android, hardware, ahorro,
  nube y próximos pasos. No modifica código, datos ni decisiones técnicas.
- Elaborado con las pruebas registradas del 30/09, 03/10 y 04/10; no se repitieron
  pruebas de backend/Android ni ensayos físicos para elaborar este reporte.

## Ahorro energético y procesos — documentación del 2026-10-04

- Usuario confirma ESP32 con fuente y control de bombas. Dirección D44–D47 en
  [ENERGY_OPTIMIZATION.md](../../docs/ENERGY_OPTIMIZATION.md): controlador disponible,
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

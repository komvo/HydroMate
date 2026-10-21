# Incremento público/rootless vigente — 2026-10-14

ESP32 hydromate-01 → MQTT TLS8884 → Mosquitto → bridge POST privado → Laravel
→ PostgreSQL interno → GET HTTPS9443 → Android producción. El hostname es
hydromate-kevin.duckdns.org. API conserva loopback8081. Docker rootless pertenece
a deploy-hydromate; certificados montados desde /etc/hydromate/{https,mqtt}.
Nginx propio sin privilegios permite GET/HEAD y un POST público limitado a
solicitar adquisición; bloquea la inserción externa de mediciones. Los scripts
validan cuenta/socket/daemon y preparan permisos de certificados dentro del
namespace. Sin cambios80/443/8883 ni red host. HYDROMATE_APP_URL es única variable
URL producción; perfiles Android separados, sin demo/fallback en producción.
Contrato v3 admite null/origen por sensor, TDS real opcional y EC independiente;
antigüedad usa adquisición/recepción. No hay comandos de actuadores.
Guías: PUBLIC_ACCESS.md, INTEGRATION.md, TELEMETRY_CONTRACT.md.
Pruebas locales no acreditan el despliegue ni el namespace rootless de la VPS.

Incremento21/10 (D60): TDS analógico en ADS1115 A1 y temperatura GPIO4; envío por
cambio de sensor además del respaldo30s. Android solicita una adquisición mediante
POST de cuerpo vacío; Laravel conserva un UUID efímero en su caché de archivos.
El bridge consulta una ruta interna y publica commands/measure por el broker ya
existente. ESP32 adquiere y responde mediante telemetría v3 con request:<UUID>.
Laravel solo confirma tras persistencia correlacionada en PostgreSQL. No nuevas
tablas, servicios ni comandos de actuación. Poll de vistas Android cada2s en
primer plano. Las pruebas físicas previas no prueban este incremento nuevo.

## Arquitectura anterior preservada

# Arquitectura vigente

Fecha: 2026-10-07. Distinguir diseño seleccionado de implementación comprobada.

## Empaquetado de producción — 2026-10-14

`compose.production.yml`, proyecto explícito **hydromate**, prepara API
Apache/PHP 8.4 (www-data, public como webroot), PostgreSQL 16 interno con rol
app no superusuario y perfil mqtt opcional con Mosquitto/bridge existente.
API publicada solo en 127.0.0.1:8081; MQTT TLS 8884, listener 1884 interno sin
publicación. No usar 80/443/8883, network_mode host ni recursos chitiito-*.
Red hydromate_database interna solo para db/api; hydromate_application conecta
API/broker/bridge. Volúmenes exclusivos: postgres_data, api_storage, mqtt_data y
bridge_state con prefijo de proyecto. Android sigue en teléfono por HTTPS; ESP32
por MQTT/TLS, sin introducir comandos físicos ni modificar contratos v1/v2.
La API loopback requiere endpoint HTTPS protegido independiente para Android
remoto; no modificar el proxy/configuración de chitiito. Secretos solo en VPS.
Preparación para ejecutor de main con checkout Git de solo lectura; hook
`deployment/deploy.sh` construye/inicia servicios propios y migra explícitamente.
Guía y límites: PRODUCTION.md. No acceso SSH ni despliegue VPS en esta tarea.
Las notas locales/históricas siguientes se conservan como antecedentes.

## Incremento local del Taller 5 — 2026-10-07

Productor PC sintético → Mosquitto → bridge Python con bandeja SQLite → Laravel
→ PostgreSQL probado con diez mensajes, inválido y conflicto. Broker separado
1884 autenticado, ACL por cuenta y listener loopback/IP Wi-Fi; 1883 conservado.
Android reconoce v1/v2 y muestra lux, flotador y TDS simulado. Firmware ESP32
cargado con reserva de secuencias y un pendiente NVS; diez entregas físicas
comparadas contra API y recuperación de pendiente tras reinicio observadas.
Inicio Android muestra datos reales y TDS simulado; evidencia actual en STATUS.
Laravel permanece loopback; Android usa USB reverse. MQTT sin TLS se limita al
banco doméstico autorizado. Nube HTTPS/MQTT TLS y protección de API pendientes.
v2 agrega light_lux, water_present, sources y message_version sin borrar v1.
Detalle vigente en TELEMETRY_CONTRACT.md; v1 preservado en TELEMETRY_CONTRACT_V1.md.
Los párrafos siguientes describen el diseño/estado anterior y se sustituyen en
estos puntos por este incremento, sin afirmar pruebas físicas todavía pendientes.

## Incremento seleccionado
Datos sintéticos identificados → POST Laravel → PostgreSQL → GET Laravel →
Android mínimo (implementado e instalado; QA manual parcial). Posteriormente ESP32 físico → MQTT →
integración/bridge → misma API. Wokwi y dashboard Blade no son requisitos actuales.
API y BD probadas; cliente Kotlin probado por HTTP desde JVM. Ejecución Android
en teléfono parcialmente observada; integración de sensores físicos pendiente.

## Producto objetivo
Sensores/actuadores ↔ ESP32 ↔ MQTT/TLS ↔ Mosquitto ↔ Laravel ↔ PostgreSQL.
Android ↔ HTTPS/REST ↔ Laravel. BLE para provisionamiento; FCM para notificaciones.
Laravel coordina y conserva información. ESP32 decide seguridad crítica local.
El bridge podrá sustituirse por una integración MQTT gestionada; no decidir ahora
la tecnología de ese proceso. No crear infraestructura final por anticipado.

## Control y ahorro — dirección documentada 2026-10-04

ESP32 con fuente y control de bombas confirmado por el usuario. Diseño pendiente
de firmware: seguridad/control, adquisición y red separados; sin espera de red
en el camino crítico. Medición inicial propuesta de 5 s, publicación estable de
300 s y prueba temporal de 30 s; interbloqueos con plazo propio aún por determinar.
Modem-sleep/frecuencia dinámica por etapas; sueño ligero automático condicionado a
despertar/pines/plazos verificados. Sin deep sleep durante operación normal.
La bandeja durable y ACK posterior al INSERT se implementaron en banco el 07/10;
recuperación física/reinicio/corte de energía todavía por verificar.

Antes de sensores reales o cola tardía ampliar el contrato de forma compatible:
calidad/ausencias, nivel discreto, magnitud de luz, eventos y tiempo de adquisición.
v1 permanece compatible y v2 implementa lux/flotador/origen. [ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md) contiene
invariantes, comparaciones de energía, mejoras por capa y pruebas para habilitarlas.
Render + Aiven es solo candidato para API/BD; MQTT/bridge requiere evaluación aparte.

## Contrato existente
POST `/api/measurements`; GET `/api/measurements?limit=20` (1–100);
GET `/api/measurements/latest` (404 si no hay datos).
Campos: device_id (string ≤64), sequence (entero ≥1), sample_number opcional,
reason (array opcional), temperature_c (0–50), light_pct y water_level_pct (0–100),
light_state (BAJA/MEDIA/ALTA), water_level_state (VACIO/MEDIO/LLENO), ph (0–14),
tds_ppm (0–1000). Rangos actuales de PoC, no recomendaciones agronómicas.
Tabla prevista: measurements, id, campos anteriores, created_at/updated_at;
índice único (device_id, sequence). Timestamps asignados por Laravel.

El controlador devuelve 201 al crear, 409 al violar el índice único y 422
en validación. GET soporta filtro opcional device_id; latest sin datos es 404.
Orden estable created_at DESC, id DESC. La app debe enviar device_id para evitar
mezclar torres. Limit fuera de 1–100 devuelve 422, sin truncamiento silencioso.
reason: lista opcional de hasta 10 cadenas de máximo 64 caracteres; enteros
sequence/sample_number positivos y dentro de bigint PostgreSQL.
Contrato y ejemplos: API.md. Verificación observada: STATUS y evidence/.

## Pendientes de diseño acotados
- Verificar físicamente secuencia persistente por rangos (D19), pendiente y reinicio;
  implementados en firmware nuevo, sin resultado físico afirmado aquí.
- Verificar recuperación de bandeja/reintentos ante cortes; implementación local nueva.
- Canales de dosificación abstractos; driver físico por elegir.
- Sin implementación de comandos, usuarios/grupos/perfiles en esta fase.

Referencia vigente: TELEMETRY_CONTRACT.md (v2 y compatibilidad v1).

## Cliente Android 0.2 — base histórica, actualizada abajo por 0.3
MainActivity coordina navegación, lifecycle y preferencias de conexión. Pantallas
separadas en ui/dashboard, history, cultivation, control y settings; componentes
comunes y estados de consulta en ui/. TelemetryRepository
consulta HTTP fuera del hilo UI con límites de tamaño/tiempo y sin redirecciones.
Telemetry valida URL y parsea el contrato; rechaza registros de otra torre.
GET historial filtrado proporciona última lectura e historial en una sola respuesta,
evitando mezclar instantáneas. Sin caché de lecturas ni tareas permanentes; giro
conserva configuración y vuelve a consultar (un error se conserva hasta reintento).
Consulta inicial y actualización manual por icono/gesto, sin polling. Al salir de
Activity se invalida/cancela el trabajo pendiente y se descartan resultados tardíos.
Debug permite HTTP; release HTTPS.
Long para secuencia, Double para variables; Instant para fecha recibida y zona
del teléfono para mostrarla. No se infiere conexión del sensor desde un GET exitoso.
Historial con gráfica Canvas por recepción; temas según sistema y sensores en una
o dos columnas según tamaño/texto. Antigüedad optativa configurable (0 desactivada),
sin umbral de firmware supuesto. Sin endpoints nuevos, cambios de BD ni librerías
de producción. Cultivo/control/BLE/alertas se muestran como pendientes; no ejecutan
acciones ni afirman estados físicos. Respuesta incompleta se rechaza entera conforme
al contrato v1. Vacío no distingue torre inexistente de torre sin mediciones.

## Cliente Android 0.3 Aero — base previa, presentación reemplazada por 0.4
Se conservan Activity/vistas, GET filtrado, executor y ausencia de caché/polling.
Cuatro destinos más Equipo secundario. AeroArtwork/Components reciben tokens y
dibujan materiales nativos; las pantallas reciben ReadingState y acciones locales.
RequestFence emite tickets por identidad/generación y decide si aceptar un
resultado; se revoca al cambiar configuración, fuente o abandonar Activity.
ConnectionStore guarda nombre/umbral por servidor/torre, nunca lecturas.

PreviewSupport está separado por source set: debug devuelve fixtures/estados
deterministas, release devuelve nulo y ninguna opción. Elegir demo invalida la
petición real; no hay fallback automático ni publicaciones. La marca de fuente
vive fuera del scroll. No hay cambios de servidor, tablas o contrato.
La validación del cliente aplica explícitamente los rangos v1/estados/secuencia
además de identidad/campos/fecha; una fila inválida rechaza la respuesta completa.
Tema Aero Día inicial mediante contexto Android, con opción sistema heredada.
Lecturas relativas y todas las limitaciones físicas anteriores siguen vigentes.

## Cliente Android 0.6 Jardín de cristal — vigente, 2026-10-04

Cinco destinos visibles. AeroBottomNavigation recibe destino/callback y produce
la barra nativa compartida. AeroIcons mapea cada símbolo a resource y, solo para
la barra, navigationResource. Inicio/Historial/Control/Más usan cuatro variantes
PNG con menos detalle a 36 dp; Cultivo conserva el original a 34 dp. Components
siempre usa la ilustración original en las pantallas, sin selección por tamaño.
Los PNG locales tienen alfa, sin tintes ni carga remota. Sustituyen los dibujos
GlassIconDrawable de 0.4; no hay cambios de estado o lecturas.
hero_hydromate_glass.png es identidad y launcher, sin significado de telemetría.
AeroSurface mantiene superficies verdes en Canvas con alfa 110 y placa 68
de día (180/130 de noche).
AeroSky decodifica el fondo botánico local una vez, lo encuadra y aplica un velo
menta claro de día, oscuro de noche. Encabezados usan tokens específicos para texto sobre el fondo.
Recarga y TDS reciben símbolos propios; no hay cambios al significado de datos.
MainActivity conserva navegación/datos/lifecycle; la configuración de barras
visuales se aplica tras crear la ventana.

VisualCheckActivity (src/debug) recibe ancho, fuente, destino y escenario por
Intent; produce vistas de los mismos componentes y un informe de composición.
No instancia repositorio ni almacén de configuración. src/release no incluye
esta Activity ni fixtures. La Activity de revisión fija retrato y mantiene la
pantalla activa solo mientras es visible; no altera ajustes globales. Es evidencia
visual, no integración E2E ni prueba del giro de MainActivity.

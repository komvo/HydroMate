# Arquitectura vigente

Fecha: 2026-09-30. Distinguir diseño seleccionado de implementación comprobada.

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
La cola durable, confirmación posterior al INSERT y recuperación no están implementadas.

Antes de sensores reales o cola tardía ampliar el contrato de forma compatible:
calidad/ausencias, nivel discreto, magnitud de luz, eventos y tiempo de adquisición.
v1 permanece sin cambios. [ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md) contiene
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
- Implementar en firmware sequence persistente por rangos (D19); contrato definido,
  comportamiento ante reinicio todavía sin implementar ni probar.
- Definir reintentos del bridge y comportamiento ante respuesta perdida.
- Canales de dosificación abstractos; driver físico por elegir.
- Sin implementación de comandos, usuarios/grupos/perfiles en esta fase.

Referencia de mensaje canónico: TELEMETRY_CONTRACT.md (v1 documental).

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

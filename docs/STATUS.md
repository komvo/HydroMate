# Estado actual de HydroMate

Consolidación documental: 27/10/2026. Últimas evidencias físicas: 21/10/2026.
La consolidación no repitió ensayos de hardware ni consultó la VPS.

## Implementación y evidencia

- Flujo ESP32 → MQTT TLS8884 → Mosquitto/bridge → Laravel/PostgreSQL → Android
  HTTPS9443 observado. Identidad `hydromate-01`.
- Ensayo de 14 adquisiciones4201–4214:14 STORED, cero publicaciones fallidas
  después de conectar; rechazo previo de autenticación documentado. Tiempo
  SAMPLE→STORED258–577ms, media409ms; no incluye Android.
- Integración posterior4601–4604: TDS770.32–771.05ppm y23.50°C reales;
  coincidencia con GET público y cambios de luz/nivel. No acredita calibración.
- Android Inicio/Historial muestran lecturas y fecha. Última captura de historial
  del incremento:4718, TDS768.76ppm/23.50°C. Capturas del reporte también conservan
  otras secuencias/horas; no deben mezclarse como una única medición.
- Fuentes: `evidence/public-flow-esp32-android-2026-10-21.json` y
  `evidence/tds-events-2026-10-21.json`, PNG y anexos del Taller5.

## Incremento vigente

TDS A1 con mediana de 9 conversiones y compensación DS18B20. Si temperatura es
inválida, referencia 25°C etiquetada; temperatura sigue null/invalid. EC permanece
null/unavailable. Cambios significativos envían eventos; respaldo 30 s, adquisición
500ms, flotador150ms y mínimo750ms entre muestras, según sensor_config.h.
Un pendiente NVS conserva identidad/contenido hasta ACK stored.

Refrescar: POST público acotado → UUID30s en caché → bridge → commands/measure →
ESP32 → telemetría v3 correlacionada → persistencia. Vistas visibles consultan2s.
Ensayo local aislado verificado; despliegue y solicitud física confirmados.

## Pruebas registradas el 21/10

PHP 29 pruebas/194 comprobaciones; Python 10/10 en entorno configurado, pruebas C++
de conversión/mediana/eventos. Android debug/release y lint pasaron; JVM 33,
31 ejecutadas y 2 opt-in omitidas. Pipeline local MQTT TLS→bridge→PostgreSQL→GET,
10 mensajes y casos inválido/duplicado/conflicto comprobados con fixtures.
Son resultados fechados; elegir y ejecutar nuevamente lo pertinente al modificar
código. SETUP distingue dependencias, opt-in y efectos de cada prueba.

## Arquitectura seleccionada e implementación incompleta

D65 (28/10): el firmware gobierna la **bomba de recirculación** con decisión local.
- Pines: GPIO25 activo en bajo, interbloqueado por hardware con el flotador mediante
  una NOR 74HCT02; alarma en GPIO23.
- Comportamiento: arranca 5 s después de confirmar agua, se apaga de inmediato con
  nivel bajo y una tarea de seguridad es la dueña de los pines.
- Comprobado: compila y la lógica pasa la prueba C++ en PC.
- Prueba física P7: realizada el 28/10 con este firmware y el circuito de
  Proteus. No hay foto, video ni registro serie, y la corriente de arranque no
  se midió.

Los cuatro canales A/B/Up/Down, la seguridad de dosificación y el cierre sin energía
siguen por implementar con validación física. No están completos usuarios/Sanctum, avisos/FCM, BLE,
perfiles ni control remoto de actuadores. D61 conserva Arduino-ESP32 modular;
no obliga a migrar a ESP-IDF. Control hm-control-1 es diseño; measure ya existe.

## Entregas y presupuesto

- `Documentos PDC/T5_PDC_1288703.docx` y PDF:17 páginas, presupuesto corregido.
- `Documentos PDC/T8_PDC_1288703.docx` y PDF:15 páginas; decisiones y 16 mínimos.
- `T6_PDC_1288703_act` es referencia de requisitos actualizada; los anteriores
  y el informe ampliado de 41 páginas son antecedentes, no versiones vigentes.
- Fuentes/anexos T5: `talleres/taller-05/entrega-2026-10-21/` desde la raíz.
- Compras anteriores $2,055.94 + electrónica pagada $1,168 + segundo TDS $270 =
  $3,493.94 MXN. Máximo $6,000; disponible $2,506.06. Desglose electrónico $1,174.23:
  diferencia $6.23 sin motivo identificado. VPS prestada $0.
- Entrega final del proyecto: 2/12/2026. Cronograma es planificación, no ejecución.

## Git y siguiente acción

Rama de trabajo: `talleres-5-8-documentacion`. Verificar el estado real con Git;
un push no implica despliegue en vivo.


## Validación de esta consolidación — 27/10/2026

Se actualizaron contexto, arquitectura, guías de arranque/Git y referencias de
API/integración.
Pruebas ejecutadas: Python bridge 5/5 y validación de puertos públicos 2/2,
sin contactar la VPS. 34 enlaces locales comprobados sin destinos ausentes y diff sin errores; no se repiten pruebas
PHP/Android, flasheo ni hardware porque no cambia código o configuración.
Los Word/PDF académicos permanecen sin modificaciones. No commit/push/merge.


## Rediseño Android Jardín líquido — 27/10/2026

D63 implementado en `mobile/` (solo UI): vidrio esmerilado sobre el fondo botánico,
barra flotante y nuevas pantallas. Build debug/release, lint y JVM (33; 4 opt-in
omitidas) correctos. Instalado por USB y revisado con 26 capturas nativas sin
recortes ni objetivos <48 dp tras cuatro correcciones; commit local sin push.
Pendientes en [AERO_ACCEPTANCE](AERO_ACCEPTANCE.md).

## Historial e Inicio comprensibles — 27/10/2026

Análisis en [UX_ANALYSIS](UX_ANALYSIS.md). Gráfica de línea con huecos, inspección
táctil, resumen y tabla en Historial; minigráficas, cambios y guía en Inicio.
Build debug/release y lint correctos; JVM 39 (35 ejecutadas, 4 opt-in omitidas).
Revisado en teléfono: 26 capturas sin recortes tras seis correcciones;
arrastre, diálogos y TalkBack sin verificar (AERO_ACCEPTANCE).

## Entrega inicial de software integrado — 28/10/2026

Documento nuevo `Documentos PDC/Software_integrado_PDC_1288703.docx` y PDF;
fuentes en `talleres/software-integrado/`, resumen en SOFTWARE_INTEGRATION.md.
Completa diagramas de módulos/modelo/bosquejo, diccionario de veinte columnas,
pseudocódigo de tres procesos y plan de siete pruebas, sin modificar T5/T8.
Pruebas repetidas el 27/10: ESP32 compilado (82% flash/15% RAM), PHPUnit 29/194,
Python 10/10, Android 39 (35 ejecutadas/4 omitidas), lint y debug/release correctos;
aislamiento Compose validado con fixtures. Sin flasheo, nueva adquisición ni VPS.
Actuación sigue abierta o condicionada a autorización docente de esta etapa.
Ver límites físicos/manuales en el informe. Sin commit, push, merge ni despliegue.
Documento final de 12 páginas revisado visualmente completo; 9 enlaces locales
comprobados y formatos de URL/fecha verificados.

Prueba del 28/10: tras reiniciar el ESP32, siguió
funcionando sin conexión y al recuperarla llegaron las mediciones más recientes
sin duplicarse. Word/PDF y plan P4/P6 se actualizan como comprobados; no se
acredita reinicio del bridge.
La evidencia real anterior de Android conserva su fecha. Registro en
`talleres/software-integrado/entrega-2026-10-28/confirmacion-pruebas-2026-10-28.json`.

## Diseño 3D paramétrico — 28/10/2026

Modelado en CadQuery (`cad/`, entorno local `cad/.venv`), resumen en
`docs/DESIGN_3D.md`: CTRL-01 (caja sellada), POWER-01 (torre vertical para la
fuente medida 197×130×40), puertos PG9,
AQUA-01 (portasondas + cápsula), LEVEL-01, LIGHT-01, placas de riel y probetas.
Verificado: sólidos válidos, todas las piezas caben en la K1C, STL/STEP/PNG
generados por `build.py`. No verificado: impresión, ajuste, estanqueidad,
temperatura de la fuente. Placas pH/TDS y fuente medidas a mano
(aprox.), igual que sondas y cables; resto de vendedor. Depósito 580×480, cuerpo 330
(aprox.); plano de barrenos y ubicación de módulos generado; POWER fuera de la caja. Nivel con flotador horizontal
en soporte colgado del tubo. Pendiente: rosca del flotador y PCB de luces. DOSE-01 no modelado (decisión pendiente).

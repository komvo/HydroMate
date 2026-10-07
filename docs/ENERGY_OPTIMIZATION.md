# HydroMate — ahorro energético y optimización segura

Fecha: 2026-10-04. Alcance: diseño y plan de validación, **no firmware implementado ni ahorro medido**.
El usuario confirma alimentación mediante fuente y un ESP32 que leerá sensores y controlará bombas.
Referencias internas: [criterios](../AGENTS.md), [arquitectura](ARCHITECTURE.md),
[contrato v1](TELEMETRY_CONTRACT.md), [estado ejecutable](STATUS.md), decisiones D44–D47.

La dirección seleccionada es mantener disponible el controlador, separar seguridad,
medición y comunicaciones, y reducir primero radio, trabajo innecesario y transmisiones.
No apagar/reiniciar el ESP32 cada cinco segundos. Deep sleep queda fuera de la operación
normal de esta torre. El mínimo consumo seguro se determinará comparando mediciones:
no existe evidencia para afirmar que una configuración concreta sea el mínimo absoluto.

## 1. Qué está confirmado y qué falta

| Estado | Evidencia o alcance |
|---|---|
| Confirmado por usuario | Fuente de corriente; lectura de sensores y control de bombas. Interés en lecturas cada 5 s y pruebas con envíos aproximadamente cada 30 s. |
| Implementado | Laravel/PostgreSQL y Android; consulta inicial/manual, límite de 20 lecturas en app, deduplicación por torre/secuencia. No hay conexión física de sensores comprobada. |
| Seleccionado como dirección | Seguridad local independiente de Internet; MQTT/TLS → Mosquitto → integración → API; modos de ahorro graduales y reversibles. |
| Propuesto para ensayo | Lectura ambiental cada 5 s; telemetría estable cada 300 s; modo de prueba de 30 s con vencimiento; eventos prioritarios. |
| Pendiente | Modelo/revisión de placa, pines, drivers, alimentación real, sensores instalados/calibrados, firmware/SDK y mecanismo de dosificación. No existe embedded/ en esta revisión. |
| No decidido | Umbrales agronómicos, límites físicos de dosis, tiempo de reacción admisible, horario de riego, autonomía sin red, retención de históricos o proveedor contratado. |

La arquitectura de canales nutrient_a/nutrient_b/ph_up/ph_down sigue vigente; no se
presupone que los cuatro sean bombas peristálticas. Esta documentación no habilita
dosificación, comandos remotos ni cambios de calendario de riego.

## 2. Condiciones que todo ahorro debe conservar

| Condición | Regla de diseño y aceptación |
|---|---|
| Nivel bajo o nivel desconocido | Impedir marcha en seco y dosificación que requiera circulación. Entrada supervisada y, si el hardware lo permite, interbloqueo eléctrico independiente. Cable abierto debe llevar a fallo seguro; un único flotador no acredita detección de todo fallo mecánico. |
| Sensor inválido, antiguo o desconectado | Invalidar las decisiones que dependen de él. Un valor anterior o cero no reemplaza una medida válida. El filtro no debe ocultar el fallo. |
| Límites y mezcla | Tiempos máximos, límites de dosis por canal/ventana, exclusión pH Up/Down y mezcla se ejecutan localmente. No se suspenden para comunicar o ahorrar. |
| Arranque, brownout o watchdog | Salidas en estado seguro también antes de ejecutar firmware; verificar polaridad/driver y resistencias externas. No reanudar una dosis interrumpida automáticamente. Recuperación de riego solo tras comprobaciones definidas. |
| Red o nube caídas | No bloquear control; tampoco ordenar parar una recirculación segura solo por pérdida de red. Prohibir nuevas acciones remotas caducadas o sin validación local. |
| Saturación de CPU, memoria o cola | Preservar recursos y plazos de seguridad; degradar primero historial/comunicación. Registrar pérdida de telemetría sin presentarla como entrega. |
| Ahorro y comandos | Una orden futura no puede desactivar protecciones ni saltar límites. No considerar MQTT conectado como prueba de sensor sano. |

Antes de habilitar actuadores definir B_trip, el tiempo máximo admisible desde el fallo
físico hasta el estado seguro. Debe cumplirse en el peor caso observado:
`detección + antirrebote + despertar + ejecución + respuesta del driver <= B_trip`.
El valor lo determinan bomba, hidráulica, sensor y riesgo; **no se fija en 5 s por conveniencia**.
La vigilancia del nivel usa un camino independiente de las lecturas ambientales y de la red.
Si no se ha definido/verificado B_trip, se ensaya con cargas de prueba, sin automatizar químicos.

## 3. Escalera de ahorro del controlador

| Paso | Configuración candidata | Condición para conservarla |
|---|---|---|
| E0: referencia | ESP32 alimentado, control no bloqueante, conexión MQTT/TLS persistente; sin sueño automático. | Medir consumo, precisión, errores y reacción con el mismo escenario que los candidatos. |
| E1: primer candidato | Modem-sleep de Wi-Fi; tareas esperando temporizadores/notificaciones en lugar de bucles ocupados. Bluetooth apagado fuera del futuro aprovisionamiento. | Sin pérdidas inaceptables, reconexiones excesivas ni incumplimiento de B_trip. |
| E2: frecuencia dinámica | Permitir al SDK bajar frecuencia entre trabajos; mantener restricciones de reloj mientras un periférico las necesite. | Verificar tiempos de bus, conversión, PWM/driver y comunicaciones en la placa/SDK exactos. No fijar una frecuencia mínima arbitraria. |
| E3: sueño ligero automático | Solo después de E1/E2, con fuentes de despertar verificadas y sin actuación que dependa de CPU/periféricos suspendidos. | Inicialmente prohibido durante actuación, dosificación, mezcla y fallos. Si la recirculación continua no permite dormir con seguridad, permanecer en E1/E2. |
| Deep sleep / cortar alimentación | Excluido durante operación normal del controlador de bombas. | Evaluación futura únicamente para un nodo de sensado separado o equipo fuera de servicio, con otra protección independiente; no se implementa aquí. |

Espressif documenta que el sueño profundo y el sueño ligero explícito interrumpen Wi-Fi;
modem-sleep y sueño ligero automático permiten mantener la asociación. Esto no garantiza
que la sesión MQTT sobreviva a cualquier fallo: se debe observar y recuperar. [Modos de sueño](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html).

En ESP-IDF, DFS ajusta relojes según la actividad; los bloqueos de gestión de energía
permiten impedir sueño ligero o exigir frecuencia mientras se usa un periférico.
Una interrupción GPIO ordinaria no sustituye a una fuente de despertar compatible.
El sueño automático requiere soporte/configuración del SDK; no mezclar su temporizador
con un despertar manual cada 5 s. [Gestión de energía](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/power_management.html).
Las API citadas son referencias, no elección de framework ni confirmación de compatibilidad de la placa.

Separar tareas de seguridad/control, adquisición y red. Los temporizadores usan tiempo
monótono, resistente a cambios de hora; considerar desbordamiento si se usa contador de 32 bits.
La seguridad no espera un mutex de red, escritura flash, DNS ni conversión bloqueante.
La prioridad de una tarea no basta: ciertas operaciones de flash pueden detener cachés
e interrupciones. Probar B_trip durante escritura/borrado y revisar código/datos críticos
en RAM según el SoC/SDK; si no se garantiza el plazo, impedir esa operación con actuadores
habilitados o usar protección independiente. [Restricciones de flash en ESP32](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32/api-reference/storage/spi_flash_concurrency.html).
El watchdog se alimenta por progreso comprobado de las tareas críticas, no desde una
tarea independiente que pueda ocultar su bloqueo. Verificar que la configuración produzca
la reacción deseada; un watchdog no reemplaza el interbloqueo ni arregla un driver atascado.
[Watchdogs de ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/wdts.html).

## 4. Lecturas y envíos con propósito

Parámetros de arranque para banco, no límites físicos aprobados:

| Proceso | Propuesta | Resultado |
|---|---|---|
| Seguridad/actuadores | Según B_trip y máquina de estados local; prioridad superior a red. | Estado seguro y transiciones verificables. |
| Adquisición ambiental | Cada 5 s inicialmente, sin apagar el controlador. Cada sensor tiene timeout/edad máxima propios. | Instantánea válida o fallo explícito; sample_number aumenta con adquisiciones según contrato. |
| Estado estable | Una instantánea actual válida cada 300 s. | Historial básico y señal periódica de actividad; no transmite cada muestra de 5 s. |
| Cambio significativo | Evento al superar delta/histéresis verificados con el ruido real. | Información útil sin tormentas por oscilación. Deltas antiguos de Wokwi no son criterios de cultivo. |
| Prueba intensiva | Cada 30 s, por ejemplo durante 15 min, con vencimiento local y regreso a 300 s. | Observar ajustes sin dejar el modo rápido activo indefinidamente. |
| Fallo/alarma | Acción local inmediata y primer aviso prioritario cuando sea posible. | El aviso no condiciona la protección. Repeticiones espaciadas y transición de recuperación explícita. |

No fusionar un episodio de fallo y su recuperación como si nunca hubiese ocurrido.
La confirmación de estabilidad usada para ahorrar mensajes no debe retrasar el disparo local.
Los temporizadores de eventos/prueba no crean envíos periódicos duplicados en el mismo instante.
Propuesta: una instantánea puede incluir varios reason; una alarma con sensor ausente necesita
el canal de estado futuro descrito abajo, no valores de relleno.

Los módulos analógicos de pH/TDS permanecen alimentados inicialmente: antes de cortarles
corriente, identificar el modelo y medir estabilización, deriva y efecto sobre calibración.
El DS18B20 puede necesitar hasta 750 ms por conversión de 12 bits: iniciar, ceder CPU y
leer cuando termine, comprobando validez/CRC y timeout. [Datasheet DS18B20](https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf).
Si se instala ADS1115, ensayar conversiones single-shot y su retorno a power-down;
no adquirir continuamente a máxima tasa sin necesidad. Verificar canal, tiempo de conversión
y ruido antes de filtrar. [Datasheet ADS1115, §7.4](https://www.ti.com/lit/ds/symlink/ads1115.pdf).
No reducir resolución, alimentación o potencia de radio por intuición: comparar error,
reintentos y energía total. Una señal Wi-Fi peor puede anular el ahorro por transmisión.

### Entrega y memoria

1. Mantener MQTT/TLS abierto mientras sea útil; no reconstruir Wi-Fi/TLS en cada lectura.
   Keepalive, detección de desconexión y latencia se prueban con router/broker reales.
   Los paquetes keepalive del broker no tienen por qué producir consultas a PostgreSQL.
2. Construir un mensaje con todos los campos válidos; asignar sequence una vez y hacer
   inmutable su contenido. Nunca renumerar un reintento ni mutarlo mientras está pendiente.
3. Publicación en tarea de red, cola acotada y sin bloquear control. En ESP-MQTT, enqueue
   separa el envío del contexto llamante; hay que limitar su outbox y comprobar errores.
   QoS 1 admite reentregas; no demuestra que Laravel guardó la fila. [ESP-MQTT](https://docs.espressif.com/projects/esp-mqtt/en/latest/esp32/index.html).
4. Respetar v1: 201 confirma; 409 solo confirma reentrega si se conoce identidad de contenido;
   422 requiere corrección, no reintento ciego. Añadir posteriormente confirmación de
   aplicación por torre/secuencia desde la integración, después de persistir en PostgreSQL.
5. Propuesta de recuperación de red: espera creciente 2, 4, 8… hasta 300 s, con variación
   aleatoria acotada; una sola política coordinada con reintentos del cliente MQTT/bridge.
   El evento crítico tiene prioridad, pero no crea un bucle de conexión que monopolice CPU.
6. RAM acotada para muestras/filtrado; propuestas de capacidad se calculan con duración
   de corte tolerada y memoria real. Cola durable para mensajes/eventos que deban sobrevivir
   a un reinicio, con checksum/recuperación y prueba de corte de energía. El outbox en RAM
   por sí solo no ofrece esa garantía.
7. Al llenarse: rechazar nuevas muestras rutinarias con contador de pérdida y reservar
   espacio para transiciones críticas. No sobrescribir silenciosamente mensajes pendientes
   ni alterar su contenido. Si se agota también la reserva crítica, señalar degradación
   local y bloquear nuevas dosis automáticas hasta reconciliar el estado; preservar seguridad.
8. Conservar reserva persistente de secuencias D19. NVS sirve para configuración y rangos,
   no para escribir cada lectura de 5 s. Una operación interrumpida puede perder el dato
   que estaba escribiendo; comprobar commit antes de usar el rango y ensayar recuperación.
   La reserva de secuencia no sustituye la persistencia de límites de dosis/estado incierto:
   tras reinicio impedir dosificar hasta reconciliarlos. [NVS](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/storage/nvs_flash.html).

### Límite del contrato actual

v1 exige todos los sensores, usa nivel/luz relativos y fecha de recepción. No admite
lotes, calidad por sensor, measured_at ni eventos independientes. Antes de conectar
flotador/BH1750, enviar alarmas de sensor ausente o recuperar cola tardía para supervisión
real, diseñar una ampliación compatible: nivel discreto, magnitud real de luz,
datos parciales con calidad, eventos y hora de adquisición con estado del reloj.
Si no hay UTC fiable, conservar tiempo monótono/identidad de arranque y marcar la hora
desconocida; no inventarla. No mezclar lecturas antiguas con nuevas para completar v1.

Los promedios/mínimos/máximos de una ventana deben tener su intervalo y número de muestras;
no publicarlos como una lectura instantánea. Enviar seis muestras juntas ahorra conexiones,
pero no reduce filas si se guardan las seis. Cualquier retención/agregación es evolución
explícita, sin borrar históricos existentes ni ocultar extremos o fallos.

## 5. Otros procesos que se pueden mejorar

Revisión focalizada de código, sin ejecutar una nueva auditoría global. P0 = requisito
antes de exposición/actuación; P1 = primer incremento de ahorro; P2 = optimización condicionada
a medición; P3 = evolución. Todo lo siguiente está pendiente salvo donde dice existente.

| ID / prioridad | Hallazgo y ubicación | Mejora candidata y cómo decidir |
|---|---|---|
| O01 / P0 | Firmware/seguridad física todavía pendientes; no existe embedded/. | Primero máquina de estados, salidas seguras e interbloqueos; medir B_trip bajo carga antes de ahorro profundo. |
| O02 / P0 | API v1 no expresa sensor ausente, nivel discreto ni hora de captura. TELEMETRY_CONTRACT.md. | Evolución compatible de calidad/tiempo/eventos antes de telemetría física o cola tardía; casos de fallo explícitos. |
| O03 / P0 | routes/api.php publica GET/POST sin autenticación. | Acceso mínimo autenticado, autorización por torre, credenciales separadas productor/consulta, límites de peticiones y TLS antes de nube. No implica construir perfiles sociales/autenticación completa ahora. |
| O04 / P1 | Tráfico planteado cada 30 s incluso sin cambios. | Instantáneas a 300 s + cambios/alarma + prueba temporal. Medir mensajes y error de representación; no llamar ahorro eléctrico al 90 % menos mensajes. |
| O05 / P1 | No hay política implementada de cola/reintentos. | Cola acotada, prioridad y entrega confirmada; una caída larga no puede causar RAM creciente, flash continua o avalancha al volver. |
| O06 / P1 | Esperas/periféricos aún por implementar. | Modem-sleep, esperas que cedan CPU, conversiones asíncronas, logs por transición; medir Wh y latencias con misma carga. |
| O07 / P2 | MeasurementController filtra device_id y ordena created_at/id; migración solo tiene UNIQUE(device_id, sequence) además de PK. | Evaluar índice (device_id, created_at DESC, id DESC) con EXPLAIN y datos representativos. Conservar UNIQUE. Medir lectura, escritura y tamaño; no añadirlo si no mejora el caso real. |
| O08 / P2 | La API limita resultados a 100 y Android solicita 20: protecciones existentes. | Conservar esos límites; si hace falta más historia, paginación por cursor y consultas por rango, no descargar todo ni elevar límites sin medir. |
| O09 / conservar | Android consulta al abrir/actualizar, reutiliza la respuesta para Inicio/Historial y evita solicitudes simultáneas en Loading. | Mantener sin polling de fondo. Medir consultas por sesión antes de introducir caché, ETag o modo en vivo; invalidar siempre por servidor/torre/fuente. |
| O10 / P2 | Telemetry.kt: timeouts de conexión/lectura de 8 s; finally desconecta. MainActivity cancela Future y descarta respuestas obsoletas. | Probar cancelación efectiva del socket, arranque frío y cambio de torre. Reintento limitado con estado visible; evitar espera larga indiscriminada y peticiones superpuestas. |
| O11 / P2 | Recursos gráficos locales y estáticos; AeroSky decodifica por contenedor; pantalla encendida solo en revisión debug. | Perfilar asignaciones/redibujados antes de caché adicional. Mantener transparencia/Aero aceptados; no simplificar iconos ni cambiar el fondo por ahorro supuesto. |
| O12 / P1 | Configuración local y despliegue productivo son contextos distintos. | Preparar runtime PHP compatible, APP_DEBUG=false, secretos fuera de repo, configuración optimizada, logs acotados y backups restaurables. No desplegar artisan serve como servidor definitivo. |
| O13 / P2 | Tabla crece con cada lectura; consumo/tamaño en nube no medidos. | Medir tamaño total incl. índices y tasa real de crecimiento; proponer exportación/retención con aprobación antes de eliminar nada. No introducir particiones/Redis/colas de servidor sin necesidad. |
| O14 / P2 | Fuente, bomba de 25 W nominales, pérdidas hidráulicas y regulación aún sin medición conjunta. | Medir energía a entrada, caudal a altura real y calentamiento del driver. Ajustar dimensionamiento solo con resultados; no reducir riego, mezcla o protección para cumplir una cuota. |

Un B-tree compatible puede evitar ordenar todo el conjunto cuando se pide ORDER BY/LIMIT,
pero un índice añade almacenamiento y trabajo en escrituras. O07 es una hipótesis a medir,
no un resultado de rendimiento. [PostgreSQL: índices y ordenación](https://www.postgresql.org/docs/current/indexes-ordering.html).

## 6. Cálculos reproducibles y nube

Una torre, 30 días, un mensaje que contiene todos los sensores; sin eventos/reintentos:

| Cadencia de publicación | Mensajes/día | Mensajes/30 días | Contenido a 500 bytes/mensaje, MB decimales |
|---|---:|---:|---:|
| 5 s | 17 280 | 518 400 | 259.20 |
| 30 s | 2 880 | 86 400 | 43.20 |
| 60 s | 1 440 | 43 200 | 21.60 |
| 300 s | 288 | 8 640 | 4.32 |
| 900 s | 96 | 2 880 | 1.44 |

Fórmulas: mensajes = 86 400 × días / segundos; contenido MB = mensajes × bytes / 1 000 000.
500 bytes es una hipótesis ilustrativa, no captura de red. JSON de ejemplo valid.json
compactado en esta revisión: 225 bytes. TLS, MQTT, HTTP, respuestas, keepalive, consultas
Android y reintentos se contabilizan aparte. Tamaño JSON no equivale a tamaño PostgreSQL.
300 s reduce mensajes rutinarios 90 % respecto a 30 s; no acredita 90 % de ahorro en energía,
factura, tráfico total o almacenamiento de un histórico agregado con otras políticas.

En Neon Free, 100 CU-h/mes permiten 400 h a 0.25 CU; 30 días siempre activo a esa capacidad
son 180 CU-h. Enviar cada 30/60 s evita que duerma; incluso 300 s no garantiza superar su
ventana de inactividad. El número de INSERT no es la única causa de consumo.
[Cuota de Neon](https://neon.com/blog/neon-free-plan-1-gb-per-project),
[suspensión por inactividad](https://neon.com/docs/manage/endpoints/).

Para pruebas, Render + Aiven sigue siendo candidato, no servicio contratado. Aiven Free:
1 CPU, 1 GB RAM, 1 GB disco y 20 conexiones máximas; sin límite temporal, sin SLA, puede
apagar servicios sin actividad continuada. Limitar conexiones entre API/integración y medir
datos/índices. [Aiven Free](https://aiven.io/docs/products/postgresql/concepts/pg-free-tier).
Render Free duerme tras 15 min sin tráfico y puede tardar alrededor de un minuto en arrancar;
750 horas mensuales compartidas, disco efímero y cuotas de tráfico/build. Puede suspender
tráfico saliente elevado hacia servicios externos. No guardar la BD/cola durable en su disco
efímero ni generar pings artificiales para evitar suspensión. [Render Free](https://render.com/docs/free).
Mosquitto y el bridge necesitan ejecución apropiada y persistencia separadamente evaluadas:
un web service gratuito para Laravel no acredita alojamiento del flujo MQTT completo.
No se contrata, expone ni modifica ningún servicio en este incremento.

Energía eléctrica: `kWh = potencia media medida en W × horas / 1000`.
Ejemplo aritmético, no consumo observado: 25 W constantes durante 30 días equivalen a
18 kWh; ahorrar 1 W constante equivale a 0.72 kWh/mes. La bomba está seleccionada como
25 W nominales, pero su consumo real y horas activas no se conocen. Medir todo el sistema
en la entrada y, si hay instrumental adecuado, controlador/sensores por separado.
No inferir ahorro de una fuente nueva, PWM, menor caudal o ciclos de apagado sin comprobar
compatibilidad del motor, hidráulica y necesidades del cultivo. No se autorizan compras.

## 7. Validación para escoger el modo de menor consumo seguro

Registrar primero placa/revisión, SDK, alimentación, drivers/pines, sensores, calibración,
B_trip, edad máxima por sensor, límites por canal y tiempos de mezcla. Si un dato falta,
marcar pendiente; no rellenarlo con los rangos de validación de la API.

Comparar E0/E1/E2 y, solo tras cumplir condiciones, E3: misma placa, fuente, sensores,
router, distancia, carga, duración y programa de actuación. Al menos tres ejecuciones
comparables por candidato como propuesta de banco; después una prueba prolongada
representativa. No confundir promedios/p95 con un plazo de seguridad: registrar el máximo
y analizar los casos no cubiertos. Repetir sin JTAG si se ensaya watchdog, pues la depuración
puede alterar su funcionamiento. [Advertencia de Espressif](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/wdts.html).

| Ensayo | Aceptación requerida |
|---|---|
| Arranque/reinicio/corte durante actuación | Sin pulso de salida indebido; sin reanudación automática de dosis; estado local reconciliado. |
| Nivel bajo/desconexión/rebote, con CPU y red ocupadas | Acción segura dentro de B_trip; antirrebote sin ocultar el fallo. |
| Sensor desconectado, congelado o conversión que no termina | Timeout/edad detectados; acciones dependientes inhibidas; ningún valor inventado. |
| Up/Down simultáneos, orden repetida, exceso de tiempo/cantidad | Exclusión y límites locales efectivos; las futuras órdenes no se repiten por reconexión. |
| Sueño ligero solicitado durante dosis/mezcla o salida activa no validada | Bloqueado; sin cambio accidental de pin/PWM. |
| Fallo durante sueño permitido | Fuente de despertar compatible y reacción medida; si falla, E3 se descarta. |
| Wi-Fi/broker/API fuera de servicio y recuperación | Control disponible, reintentos acotados, recuperación sin tormenta ni afirmación falsa de persistencia. |
| Respuesta perdida, 409 y reinicio de secuencia | Misma identidad/contenido en reintento; deduplicación; conflicto no equivalente separado. |
| Corte durante commit/cola llena/flash inválida | Sin identidad reutilizada; pérdidas contabilizadas; límites de dosis no reiniciados para permitir sobredosificar. |
| Nivel bajo durante escritura/borrado flash | B_trip respetado por el camino de protección; no asumir que la prioridad RTOS evita la pausa de caché. |
| Cambio de reloj y entrega tardía | Duraciones locales correctas; recepción distinta de adquisición; no mostrar cola vieja como lectura fresca. |
| API lenta y app en segundo plano/cambio de torre | Respuestas obsoletas descartadas; cancelación y reintentos sin trabajo de fondo innecesario. |
| Comparación de consumo | Menor Wh fuera de incertidumbre del instrumento, sin empeorar seguridad, precisión ni entrega acordada. Si no mejora, revertir ese ahorro. |

Evidencia futura por ensayo: fecha, configuración/firmware, escenario y fallos inyectados,
duración, instrumento/incertidumbre, Wh, corriente media/picos, máximo de reacción,
error de medida, muestras válidas/invalidas, mensajes/intentos/bytes, reconexiones,
profundidad/pérdidas de cola, escrituras flash y resultado. Medir consumo de logging/
instrumentación o mantenerlo idéntico en todas las comparaciones. Una prueba favorable
no certifica protección contra todos los fallos ni autoriza dosificación no calibrada.

## 8. Orden del siguiente trabajo

1. Confirmar hardware y seguridad local; cerrar B_trip, salida segura y validez física.
2. Diseñar ampliación compatible de contrato para sensores reales, eventos y tiempo.
3. Implementar adquisición/control y medir E0; introducir E1/E2 de uno en uno.
4. Añadir telemetría adaptativa, identidad/cola/confirmación y recuperación verificadas.
5. Preparar acceso mínimo y despliegue de prueba; observar cuotas y rendimiento antes
   de O07/O10/O13 o contratar infraestructura. Evaluar MQTT/bridge explícitamente.
6. Evaluar E3 únicamente si aporta ahorro medible y supera todos sus ensayos.

Este orden no inicia autenticación completa, perfiles sociales, automatización física,
nuevas tablas o despliegue por sí mismo. Fuente y control de bombas son requisitos del
usuario; los intervalos y modos aquí indicados son dirección de diseño para validar.

Revisión documental actual: fuentes oficiales consultadas el 04/10/2026, cálculos
reproducidos y comparación de hashes del código. Resultados en
[energy-review-2026-10-04.json](evidence/energy-review-2026-10-04.json).
No se ejecutaron pruebas de consumo, sensores, actuadores, nube o SQL de rendimiento.

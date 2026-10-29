# Decisiones

Fecha de consolidación: 2026-09-30. Las decisiones históricas no se borran:
añadir reemplazo explícito cuando cambien.

| ID | Fecha / fuente | Decisión y razón | Estado |
|---|---|---|---|
| D01 | 30/09; T6 23/09 | ESP32 + MQTT/TLS + Mosquitto + Laravel + PostgreSQL + Android REST. Separar control local y servicios remotos. | Confirmada, arquitectura objetivo |
| D02 | 30/09 | Completar PoC Wokwi→MQTT→Python→Laravel→BD→frontend antes de funciones avanzadas. Reduce alcance del incremento. | Reemplazada por D13 |
| D03 | 30/09 | Broker público, bridge Python, MicroPython, Blade y posible deep sleep son recursos de PoC. No describirlos como producto final. | Ruta anterior; Wokwi/Blade reemplazados por D13 |
| D04 | 30/09; T6 | Seguridad crítica en ESP32, independiente de Internet; orden remota rechazable. | Confirmada |
| D05 | 22/09, planeación; 30/09 | Dosificación como canales A/B/Up/Down; mecanismo pendiente (incluye gravedad/servo/pinch). Evita acoplar negocio a una bomba concreta. | Confirmada abstracción; pendiente mecanismo |
| D06 | Código auditado 30/09 | Conservar measurements y UNIQUE(device_id, sequence); corregir incrementalmente. No reemplazar esquema existente. | Confirmada para PoC; reinicio de secuencia pendiente |
| D07 | Plan interno 22/09 | Basic UNO debía completarse antes de depender de Smart. | Reemplazada solo como prioridad de esta sesión por D02; conservar línea Basic física |
| D08 | T4 16/09; T6 23/09 | Referencia antigua $6,000 reemplazada por techo documental $5,000 de T6. No equivale a saldo ni autoriza compras. | Vigente documental; gasto real pendiente de conciliar |
| D09 | Fuentes del 22/09 | $1,472.25 vs $1,872.74 y estados de bomba/LECA incompatibles; no fusionarlos como hechos. | Pendiente conciliación |
| D10 | 30/09 | Seis documentos compactos en docs/ son el contexto principal; los originales solo se consultan para dudas puntuales. | Confirmada |
| D11 | Auditoría 30/09 | No recrear PostgreSQL ni afirmar pruebas hasta comprobar acceso, versión, volumen y datos. | Confirmada |
| D12 | 30/09 | No instalar Laravel Boost; basta la documentación propia del proyecto. | Confirmada |

No se decidieron hardware final de dosificación, VPS, credenciales, estrategia
final de MQTT, versión/lenguaje de app existente ni compras nuevas.

## Actualización del paso 1 — 2026-09-30
- D13 — Confirmada: PostgreSQL → API → Android mínimo → ESP32 físico.
  Reemplaza D02 y la prioridad Wokwi/Blade de D03. Sensores físicos próximos;
  usar datos sintéticos para avanzar backend/app sin depender de ellos.
- D14 — Implementada: deduplicación atómica por UNIQUE existente y traducción de
  su excepción a 409; filtro opcional device_id, orden created_at/id descendente.
  GET sin filtro conserva consulta general por compatibilidad; app debe filtrarlo.
- D15 — Implementada: query limit inválido devuelve 422 (antes se truncaba a 1–100).
  reason es lista de hasta 10 cadenas de 64 caracteres; enteros limitados a bigint.
- D16 — Temporal: PHP portátil 8.4.26 en .local/php, descargado de windows.php.net
  con SHA-256 comprobado. Resuelve acceso bloqueado a Herd sin instalar globalmente.
- D17 — Confirmada: pruebas automatizadas solo SQLite en memoria con guardia
  explícita; smoke HTTP usa PostgreSQL y conserva registros sintéticos identificados.
  No se aplicó la migración Sanctum pendiente porque autenticación está diferida.

## Paso 2 — contrato de datos, 2026-09-30
- D18 — Seleccionada: contrato v1 documentado sobre el esquema existente; números
  canónicos, unidades explícitas y fixtures sintéticos. No se amplió el esquema.
- D19 — Seleccionada para firmware: sequence persistente por torre, reservas de
  rangos antes de emitir, huecos permitidos; reintento con mismo contenido/clave.
  Implementación y pruebas de recuperación de firmware aún pendientes.
- D20 — Vigente en v1: datos completos obligatorios; sensor ausente produce 422.
  Telemetría parcial, calidad, nivel discreto y magnitud real de luz requieren
  evolución explícita antes de integrar sensores; no sustituir por ceros.
- D21 — Comprobada: PostgreSQL monta volumen Docker local anónimo en
  /var/lib/postgresql/data. Conservar/reutilizar ese volumen al recrear contenedor;
  no asumir que un contenedor nuevo lo adjunta automáticamente. No se reinició.

## Android mínimo — 2026-09-30
- D22 — Implementada: proyecto nuevo mobile/ Kotlin, tras no encontrar HydroMate
  en raíz ni AndroidStudioProjects. No se modificaron proyectos académicos existentes.
- D23 — Implementada: vistas Android nativas y cliente HttpURLConnection, sin
  dependencias de UI/red adicionales para esta pantalla; lógica HTTP separada.
- D24 — Temporal: APK debug con HTTP para API local y USB/adb reverse; release
  no permite cleartext. Target 35, min 26, compile 37; no listo para tienda.
- D25 — Implementada: mostrar recepción y etiqueta test-, consultar historial por
  torre; no presentar sensores como conectados ni datos sintéticos como físicos.
- D26 — Pendiente: prueba en teléfono (sin ADB conectado). Compilación y pruebas
  JVM/HTTP correctas no sustituyen esa comprobación.

## Android UX/UI — 2026-10-03
- D27 — Evolución visual/funcional: navegación Inicio, Historial,
  Cultivo, Control, Más; preparar futuras funciones sin implementarlas ni cambiar API.
- D28 — Implementada: conservar vistas nativas y cliente común; pantallas/componentes
  separados, temas del sistema y gráfica Canvas sobre las 20 recepciones existentes.
  Sin Compose ni nuevas dependencias de producción.
- D29 — Implementada: separar consulta al servidor de comunicación de torre. No inferir
  salud, rangos agronómicos, identidad registrada ni actuadores desde telemetría.
  Antigüedad visual optativa, configurable y desactivada inicialmente.
- D30 — Implementada: consulta inicial y gesto/icono, protección contra simultaneidad,
  cancelación/invalidez al salir de Activity; errores amigables con detalles en Más.
  Validación visual y de gestos/lifecycle en teléfono sigue pendiente (D26).

## Android Aero — 2026-10-03
- D31 — Reemplazada visualmente y en navegación por D36: según el documento de diseño, Aero Día es dirección vigente; reemplaza tema
  automático como inicial de D28 y cinco destinos de D27. Inicio/Historial/
  Cultivo/Ajustes; Equipo secundario. Se conserva opción sistema reversible.
- D32 — Recursos reemplazados por D37; implementada en 0.3: materiales y torre originales en Canvas/drawables;
  Fluent Emoji 3D MIT offline, catálogo/hashes/licencia incluidos. Sin nuevas
  dependencias, fotografías externas ni fuentes redistribuidas.
- D33 — Implementada: demo determinista solo debug, opt-in y marca fija. Sin
  fallback de error, escrituras ni órdenes. Ausencia de sensor sigue rechazando
  la respuesta completa v1. Se añaden límites/estados/secuencia en validación.
- D34 — Implementada: nombres/umbrales por servidor y torre, formularios
  conservados e invalidación por generación/identidad al cambiar fuente o torre.
  No es propiedad/autenticación de torres ni caché de mediciones.
- D35 — Referencia visual, no hardware confirmado: tres niveles/seis sitios en
  el esquema pedido. Fuente física del 24/09 no localizada; D05 continúa vigente.
  La aceptación visual real sigue pendiente; ver AERO_ACCEPTANCE.md y evidencia.

## Android Aero Eco — 2026-10-04
- D36 — A partir de dos guías de diseño (Aero Cristal y Eco 90s): nueva dirección principal,
  cristal con espesor/reflejo, planta natural y portal ecológico luminoso.
  Restablece cinco destinos: Inicio, Historial, Cultivo, Control, Más.
  Reemplaza el acabado y navegación D31; conserva Día inicial y opción sistema.
- D37 — Implementada en 0.4; la parte de iconos queda reemplazada por D39:
  emblema generado con herramienta de imagen y editado, iconos nativos propios;
  reemplazan PNG Fluent de D32 y esquema visual de D35, sin decidir hardware.
  Procedencia y hashes en recursos.json; aviso MIT histórico conservado.
- D38 — Implementada solo debug: revisión visual nativa con configuración local
  de ancho/fuente, sin red/persistencia/órdenes y con marca fija. No sustituye
  MainActivity ni acredita gestos, TalkBack o conectividad física.
  D26 pasa de instalación pendiente a instalación comprobada y QA parcial.

- D39 — Elevar todos los gráficos al nivel del emblema. Implementada
  en 0.5: diez iconos originales prerenderizados de cristal, alfa real y 256 px,
  generados por separado con referencia común; reemplazan iconos Canvas de D37.
  Emblema conservado y reutilizado en launcher adaptativo; biseles, burbujas y
  puntos de Historial refinados con Canvas. Sin motor 3D, dependencias ni cambios
  funcionales. Procedencia y hashes en recursos.json.

- D40 — Propuesta intermedia retirada y reemplazada por D41: el detalle y color fotográficos se
  confunden al reducirlos. Reemplaza el uso indiscriminado de PNG pequeños de D39
  por dos escalas ópticas: hasta 54 dp, símbolos Canvas claros con luz amplia y
  colores controlados; ilustraciones grandes conservan cristal/hojas detallados.
  Barra 36 dp, instrumentos 38 dp. Sin cambios de datos o estados.

- D41 — Ajuste final: solo ajustar los cuatro iconos de navegación
  distintos de Cultivo. Restaurar Cultivo y todos los gráficos de las pantallas.
  Implementada: cuatro variantes PNG con volumen cristalino y menos ruido
  interno; 36 dp. Cultivo original 34 dp. Se elimina la sustitución automática
  por glifos nativos de D40. La simplificación debe conservar riqueza material.

- D42 — 04/10: cambiar recarga, distinguir pH/TDS y orientar el fondo a
  plantas con verde oscuro y cristal verde claro. Implementada en 0.6: fondo
  botánico local con velo de contraste, paneles verde claro translúcidos, textos
  externos claros; recarga con una flecha circular, TDS con vaso/minerales y pH
  mantiene matraz. Reemplaza la paleta celeste principal de D36, conserva Aero/Eco
  y las cuatro variantes de navegación D41. No cambia lógica, datos o hardware.

- D43 — Corrección: fondo demasiado oscuro. Vigente en 0.6: jardín
  mucho más claro con velo menta luminoso, texto oscuro y paneles realmente
  translúcidos (base alfa 110/255, placa 68/255). De noche base 180, placa 130.
  Reemplaza el oscurecimiento diurno de D42; conserva hojas, pH/TDS diferenciados,
  recarga y variantes de navegación. No cambia datos ni lógica.

## Energía, telemetría y procesos — 2026-10-04

- D44 — Confirmado: ESP32 alimentado por fuente de corriente, lector
  de sensores y controlador de bombas. El ahorro debe mantener seguridad local
  D04, identidad por torre y abstracción A/B/Up/Down D05. No cambia hardware comprado.
- D45 — Dirección documentada solicitada, pendiente de implementación/pruebas:
  controlador disponible sin reinicios cada 5 s; modem-sleep, esperas no bloqueantes
  y frecuencia dinámica por etapas. Deep sleep queda excluido de operación normal;
  sustituye su posible traslado desde la PoC histórica D03. Sueño ligero automático
  solo tras validar despertar, pines y reacción; inicialmente bloqueado con actuación,
  dosificación, mezcla o fallo. No se afirma mínimo energético sin comparar medidas.
- D46 — Propuesta de banco, no cadencia física aprobada: medir cada 5 s, transmitir
  cada 300 s estable, 30 s en prueba temporal y avisar por eventos; seguridad tiene
  su propio plazo. v1 D18/D20 sigue vigente: calidad parcial, eventos, unidades
  reales, lotes/hora de captura y confirmación de aplicación requieren evolución
  compatible antes de usarlos. No añadir datos de relleno ni simular entrega.
- D47 — Plan de optimización, no cambios implementados: ENERGY_OPTIMIZATION.md
  prioriza 14 mejoras y ensayos de aceptación. Conservar deduplicación D19 y medir
  antes de índices, retención o ahorro de hardware. Render + Aiven es candidato
  de prueba; sin proveedor contratado ni solución MQTT completa seleccionada.
  No exponer API sin acceso autorizado ni eliminar datos para encajar en una cuota.

## Preparación del taller 5 y repositorio — 2026-10-07

- D48 — PoC con temperatura, pH, iluminación y flotador físicos, TDS
  simulado identificado por variable. Reemplaza la propuesta inicial de solo
  temperatura para el taller; no modifica todavía v1. Lux/nivel discreto deben
  representarse sin porcentajes inventados y TDS simulado no autoriza dosificación.
- D49 — Se acepta OVHcloud VPS-1 compartido con un proyecto similar para
  preparar alojamiento de la PoC. Separar código, datos, credenciales y permisos;
  verificar recursos con ambos proyectos. No afirma contratación/despliegue ni
  selecciona infraestructura definitiva; reemplaza Render+Aiven como candidato
  preferido para este taller, conservando D47 como antecedente.
- D50 — Repositorio GitHub en `komvo` para documentos, pruebas
  y código, antes del taller. Propuesta privada reemplazada por autorización
  explícita posterior de visibilidad pública; documentos originales incluidos,
  secretos/dependencias/cachés/compilaciones excluidos. Autoriza crear y subir la
  versión inicial; sincronización futura requiere commits/push y no implica
  acceso de escritura del compañero.
- D51 — Requisito docente: carpeta de talleres en GitHub,
  preferentemente PDF; reportes técnicos desde T5 con código, capturas,
  errores/resultados, diagramas y archivos utilizados. Conservar fuentes y
  originales; generar reporte final con evidencia observada, sin completar
  resultados pendientes por simulación o inventar aprobación de entregables.
- D52 — Retirar las tres carpetas y los 18 archivos de
  Documentos PDC señalados en capturas. Reemplaza la inclusión exhaustiva de D50:
  conservar originales locales mediante exclusión de Git, publicar solo las
  fuentes de talleres seleccionadas y sketch tsts; no reescribir historial.

## D53 — Incremento local Taller 5 (2026-10-07)

Se implementa primero el flujo local completo y se
documenta procedimiento reproducible. Telemetría v2 conserva lux reales y nivel
booleano, agrega origen por variable y mantiene v1 compatible. TDS simulado fijo
650 ppm, explícito desde firmware hasta Android; no se usa para dosificación.
Bridge Python/Paho con bandeja SQLite privada y ACK después de persistencia.
Firmware de banco separado del sketch histórico, sin actuadores, NVS para
reserva de secuencia y un pendiente. MQTT sin TLS solamente en banco doméstico
autorizado; VPS requiere TLS/HTTPS, API protegida y separación del compañero.
Se autorizó perfil doméstico privado/regla 1884 local; configuración previa
Mosquitto 1883 y PostgreSQL conservada. Pruebas físicas/nube según STATUS.

## D55 — Producción aislada y despliegue externo desde main (2026-10-14)

La tarea se limita a preparar repositorio, sin acceso SSH ni
solicitar credenciales. Sustituye la propuesta previa de acceso interactivo: ejecutor
existente despliega main con lectura Git; se entrega hook de operación Docker
propia, no workflow con secretos SSH. chitiito-* (incluidas redes/volúmenes/config)
intocable. Proyecto Docker hydromate, API inicialmente 8081 loopback, PostgreSQL
interno y MQTT TLS opcional8884 (1884 únicamente interno). No80/443/8883, host
network ni volúmenes compartidos. .env real solo VPS, configuración por entorno;
migraciones explícitas después del arranque. Entorno local permanece separado.
Sin autenticación completa nueva, Android en VPS ni firmware/actuadores nuevos.
Endpoint HTTPS protegido independiente y certificados deben provisionarlos fuera
de esta tarea; no alterar proxy de chitiito. Detalles en PRODUCTION.md.


## D56 — Publicación aislada y reconciliación de alcance (2026-10-14)

HTTPS8443/MQTT TLS8884 en hostname
hydromate-kevin.duckdns.org, Docker rootless deploy-hydromate, sin SSH ni secretos.
Certificados privados /etc/hydromate/{https,mqtt}; guard de cuenta/socket/daemon
con permisos mediante namespace. URL única HYDROMATE_APP_URL para Laravel/Android.
Integración v3 admite sensores null y TDS/EC ausentes, sin simulaciones producción.
Conservar main íntegro: contexto mantiene rutas docs, talleres/PDFs/evidencias
originales idénticos. No reorganización ni limpieza de duplicados en esta rama.
Sustituye cualquier traslado a .project propuesto en el commit anterior; alcance
reconciliado antes de merge. Antecedentes de main permanecen sin eliminar.

## D57 — Configuración Mosquitto incorporada en imagen (2026-10-14)

Tras el diagnóstico se sustituyen únicamente bind mounts
individuales conf/ACL por COPY --chown1883:1883/--chmod640 durante build de imagen
basada eclipse-mosquitto:2.0.22. Dockerfile termina USER1883:1883. Secretos siguen
externos/read-only y mqtt_data conserva su nombre/persistencia. Sustituye el
empaquetado anterior de configuración montada, sin cambiar arquitectura/tópicos,
TLS8884, listener privado1884, certificados ni contraseñas. Build automatizado
incluye Mosquitto para evitar configuración antigua en imagen cacheada.
Validación local directa/integración TLS; ninguna operación VPS realizada.

## D58 — HTTPS9443 sustituye8443 (2026-10-14)

Se confirma 8443 ocupado por proyecto ajeno, intocable. Se sustituye el puerto
HTTPS de D56 por9443 en Compose/Nginx/gate/plantilla/validadores y documentación.
URL única HYDROMATE_APP_URL=https://hydromate-kevin.duckdns.org:9443; Android
compila ese default y conserva desarrollo independiente. MQTT permanece8884,
listener privado1884, binario propio de Mosquitto1883:1883 y misma persistencia.
No cambios80/443/8443/8883, reglas globales, certificados/secretos ni arquitectura.
Registros históricos8443 se conservan como tales. Validación local no acredita
conectividad VPS. Administrador actualiza solo APP_URL y acceso TCP9443.

## D59 — Base documental de arquitectura integral (2026-10-14)

Se congela la arquitectura principal en un taller académico.
Se consolidan ESP32/control local, Mosquitto MQTT/TLS, consumidor Paho con
bandeja, Laravel/PostgreSQL y Android HTTPS; se preservan v3, identidad
device_id/sequence y tópicos actuales. Base1.0 con14 ADR,12 figuras y trazabilidad:
reports/arquitectura-integral-2026-10-14/. Ratifica decisiones existentes, sin
implementar módulos de control ni migraciones futuras. hm-control-1, nuevas
rutas/tópicos, firmware modular y GPIO de actuación son propuestas etiquetadas.
Cuatro canales A/B/Up/Down conservan mecanismo físico pendiente; límites,
calibraciones, cierre sin energía y tiempos deben validarse antes de habilitarlos.
No reemplaza evidencia histórica ni acredita recepción ESP32→VPS o despliegue
completo. Cambios posteriores mediante ADR sucesor y revisión de contratos.

## D60 — TDS real, eventos y adquisición solicitada (2026-10-21)

Se confirma reemplazo TDS analógico conectado a ADS1115 A1 y DS18B20 GPIO4.
Se reemplaza la deshabilitación previa: mediana de9 conversiones, transferencia
del módulo y compensación con temperatura medida. Si falta temperatura, referencia
25°C identificada en Android; nunca inventar temperatura ni EC. Sin calibración
acreditada. El ESP32 detecta cambios con umbrales configurables, antirrebote y
respaldo30s; conserva el pendiente original hasta ACK de persistencia.

Refrescar debe adquirir y no limitarse a consultar la BD. POST público limitado
para torre conocida, cuerpo vacío y12/min; UUID de30s en caché file existente,
sin migración. El bridge consulta solo por red interna y publica comando measure
QoS1 no retenido; ESP32 valida UUID/caducidad y responde por telemetría v3. Se
confirma únicamente tras guardar una adquisición correlacionada. Sin actuadores,
auth completa ni microservicio nuevo. Android consulta automáticamente cada2s
solo en vistas visibles. Requiere desplegar API/bridge/ACL/Nginx y actualizar
firmware/app; pruebas locales no equivalen a aceptación física pública.

## D61 — T8 acotado y decisiones de continuidad (2026-10-21)

Se concentra el diseño de D59 en los mínimos del taller;
la versión corregida a mano se conserva y la revisión queda en Documentos
PDC/T8_PDC_1288703.docx y PDF. Sustituye para esta entrega el informe
ampliado de D59; el original permanece como antecedente, sin borrar su historial.
Se ratifican ESP32/MQTT TLS/bridge/Laravel/PostgreSQL/Android HTTPS, pines reales
A0 pH/A1 TDS y despliegue rootless9443/8884. Sanctum, FCM y BLE se expresan como
decisiones de diseño para usuarios, avisos y alta Wi-Fi, no como implementación.
Se elige conservar Arduino-ESP32 y modularizar con tareas FreeRTOS donde proceda,
en lugar de la preferencia de migrar a ESP-IDF del informe ampliado: reutiliza el
firmware probado y el core ya admite tareas. Fuentes oficiales citadas en el T8.
Control hm-control-1 conserva su envoltorio separado de telemetría v3; ningún
contrato ejecutable ni componente cambia en esta revisión documental.


## D62 — Documentación vigente (2026-10-27)

Se consolida la documentación en STATUS → PROJECT_CONTEXT → ARCHITECTURE; SETUP y
REPOSITORY describen el estado actual. Se distinguen evidencia observada, diseño
seleccionado y pruebas pendientes. No cambia arquitectura, contrato ni implementación.
Push, merge y despliegue son pasos distintos.


## D63 — Rediseño visual Android «Jardín líquido» (2026-10-27)

Rediseño total que conserva Frutiger Aero y lo ecológico
pero deja el aspecto de web de los 90, tomando como referencia los materiales de
cristal de Apple (Liquid Glass). Reemplaza la dirección visual D43;
mantiene emblema, iconos PNG, fondo botánico y variantes D41.
Vidrio nativo con muestreo de una copia desenfocada del fondo local, barra flotante
en cápsula y listas agrupadas. Sin dependencias, datos, contrato ni lógica nuevos.
Revisado en teléfono el 27/10; detalle en AERO_DESIGN y AERO_ACCEPTANCE.

## D64 — Historial e Inicio orientados a comprensión (2026-10-27)

Análisis UX/UI y mejoras para entender el sistema y el
historial (UX_ANALYSIS.md). Reemplaza los puntos aislados de D43/D63 por línea con
área, eje Y dinámico, promedio, inspección táctil y **cortes visibles** cuando un
intervalo supera 3× la mediana. Así no se dibuja continuidad sobre recepciones faltantes.
Inicio añade minigráficas, cambio frente a la lectura anterior en color neutro (sin
rangos no se califica), precisión por métrica, estado relativo y guía «Entender
HydroMate». Tabla de recepciones con detalle por fila. Sin cambios de API/contrato;
selector de periodos y rangos por cultivo quedan como recomendaciones.

## D65 — Primera salida física: bomba de recirculación local (2026-10-28)

Para la entrega de software integrado se implementa en
`embedded/` la salida tal como se armó en la práctica Proteus. Su alcance es solo la
bomba de recirculación (GPIO25, activo en bajo, NOR 74HCT02 con el flotador) y la
alarma (GPIO23).
- La decisión es local: la bomba arranca 5 s después de confirmar agua, corre de forma
  continua y se apaga de inmediato con nivel bajo.
- Una tarea FreeRTOS de seguridad, separada de las esperas de red, es la dueña de los pines.
- El interbloqueo físico por nivel no depende del firmware.

Sin orden remota, sin dosificación y sin cambios de contrato ni API. Reemplaza
parcialmente la nota «no hay salidas de actuadores» de STATUS; el aplazamiento docente
de la actuación (T5) queda superado para la bomba. Los valores son de banco, no un
riego definido. Prueba física realizada el 28/10, sin registro gráfico.

## D66 — Ecosistema 3D paramétrico en CadQuery (2026-10-28)

Propuesta pendiente de validación física.
- CAD como código (CadQuery 2.8, venv local) con medidas únicas en `cad/hydromate_cad/params.py`.
- Envolventes superelipse; junta TPU con tornillos M3 en pétalos exteriores desde abajo;
  tapas sin barrenos impresas boca abajo.
- ~~Fuente dentro de CTRL-01 en cámara inferior ventilada~~ reemplazado el mismo día:
  la fuente medida (197×130×40) no cabe acostada en la K1C; va en POWER-01, torre
  vertical ventilada en el mismo riel. Alternativa: caja eléctrica comercial.
- Montaje: placas planas en la pared exterior (el borde de la tapa no se usa: rompería el
  sello); POWER-01 fuera de la caja, ≥10 cm sobre el piso.
- Puertos con prensaestopas PG9 (comprados) + pigtail al conector automotriz de 14 vías;
  pH por pasacables TPU partido por su BNC.
- Montaje universal por riel cola de milano; AQUA propone un cable de 7–8 hilos al
  principal (reversible en `HUB_FRONT_PORTS`).
- Dosificación: frascos comprados + bastidor impreso; se recomienda peristáltica sobre
  gravedad/pinch. No decidido.

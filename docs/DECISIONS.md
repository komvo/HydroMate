# Decisiones

Fecha de consolidación: 2026-09-30. Las decisiones históricas no se borran:
añadir reemplazo explícito cuando cambien.

| ID | Fecha / fuente | Decisión y razón | Estado |
|---|---|---|---|
| D01 | 30/09, usuario; T6 23/09 | ESP32 + MQTT/TLS + Mosquitto + Laravel + PostgreSQL + Android REST. Separar control local y servicios remotos. | Confirmada, arquitectura objetivo |
| D02 | 30/09, usuario | Completar PoC Wokwi→MQTT→Python→Laravel→BD→frontend antes de funciones avanzadas. Reduce alcance del incremento. | Reemplazada por D13 |
| D03 | 30/09, usuario | Broker público, bridge Python, MicroPython, Blade y posible deep sleep son recursos de PoC. No describirlos como producto final. | Ruta anterior; Wokwi/Blade reemplazados por D13 |
| D04 | 30/09, usuario; T6 | Seguridad crítica en ESP32, independiente de Internet; orden remota rechazable. | Confirmada |
| D05 | 22/09, planeación; 30/09, usuario | Dosificación como canales A/B/Up/Down; mecanismo pendiente (incluye gravedad/servo/pinch). Evita acoplar negocio a una bomba concreta. | Confirmada abstracción; pendiente mecanismo |
| D06 | Código auditado 30/09 | Conservar measurements y UNIQUE(device_id, sequence); corregir incrementalmente. No reemplazar esquema existente. | Confirmada para PoC; reinicio de secuencia pendiente |
| D07 | Plan interno 22/09 | Basic UNO debía completarse antes de depender de Smart. | Reemplazada solo como prioridad de esta sesión por D02; conservar línea Basic física |
| D08 | T4 16/09; T6 23/09 | Referencia antigua $6,000 reemplazada por techo documental $5,000 de T6. No equivale a saldo ni autoriza compras. | Vigente documental; gasto real pendiente de conciliar |
| D09 | Fuentes del 22/09 | $1,472.25 vs $1,872.74 y estados de bomba/LECA incompatibles; no fusionarlos como hechos. | Pendiente conciliación |
| D10 | 30/09, usuario | AGENTS raíz y seis documentos compactos son contexto principal; originales solo para consultas focalizadas. | Confirmada |
| D11 | Auditoría 30/09 | No recrear PostgreSQL ni afirmar pruebas hasta comprobar acceso, versión, volumen y datos. | Confirmada |
| D12 | 30/09, consolidación | Sustituir AGENTS genérico de bootstrap por enlace al contexto real; no instalar Boost solo para inicializar instrucciones. Conservar copia del archivo anterior. | Confirmada para este incremento |

No se decidieron hardware final de dosificación, VPS, credenciales, estrategia
final de MQTT, versión/lenguaje de app existente ni compras nuevas.

## Actualización del paso 1 — 2026-09-30
- D13 — Confirmada por usuario: PostgreSQL → API → Android mínimo → ESP32 físico.
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
- D27 — Usuario solicita evolución visual/funcional: navegación Inicio, Historial,
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
- D31 — Reemplazada visualmente y en navegación por D36; usuario, prompt del DOCX: Aero Día es dirección vigente; reemplaza tema
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
- D36 — Usuario, dos MD de Aero Cristal + Eco 90s: nueva dirección principal,
  cristal con espesor/reflejo, planta natural y portal ecológico luminoso.
  Restablece cinco destinos: Inicio, Historial, Cultivo, Control, Más.
  Reemplaza el acabado y navegación D31; conserva Día inicial y opción sistema.
- D37 — Implementada en 0.4; la parte de iconos queda reemplazada por D39:
  emblema original generado con IA, iconos nativos propios;
  reemplazan PNG Fluent de D32 y esquema visual de D35, sin decidir hardware.
  Fuentes/prompt/hashes en recursos.json; aviso MIT histórico conservado.
- D38 — Implementada solo debug: revisión visual nativa con configuración local
  de ancho/fuente, sin red/persistencia/órdenes y con marca fija. No sustituye
  MainActivity ni acredita gestos, TalkBack o conectividad física.
  D26 pasa de instalación pendiente a instalación comprobada y QA parcial.

- D39 — Usuario pide elevar todos los gráficos al nivel del emblema. Implementada
  en 0.5: diez iconos originales prerenderizados de cristal, alfa real y 256 px,
  generados por separado con referencia común; reemplazan iconos Canvas de D37.
  Emblema conservado y reutilizado en launcher adaptativo; biseles, burbujas y
  puntos de Historial refinados con Canvas. Sin motor 3D, dependencias ni cambios
  funcionales. Prompts, procedencia y hashes en recursos.json.

- D40 — Propuesta intermedia retirada y reemplazada por D41: el detalle y color fotográficos se
  confunden al reducirlos. Reemplaza el uso indiscriminado de PNG pequeños de D39
  por dos escalas ópticas: hasta 54 dp, símbolos Canvas claros con luz amplia y
  colores controlados; ilustraciones grandes conservan cristal/hojas detallados.
  Barra 36 dp, instrumentos 38 dp. Sin cambios de datos o estados.

- D41 — Aclaración final del usuario: solo ajustar los cuatro iconos de navegación
  distintos de Cultivo. Restaurar Cultivo y todos los gráficos de las pantallas.
  Implementada: cuatro variantes PNG con volumen cristalino y menos ruido
  interno; 36 dp. Cultivo original 34 dp. Se elimina la sustitución automática
  por glifos nativos de D40. La simplificación debe conservar riqueza material.

- D42 — Usuario, 04/10: cambiar recarga, distinguir pH/TDS y orientar el fondo a
  plantas con verde oscuro y cristal verde claro. Implementada en 0.6: fondo
  botánico local con velo de contraste, paneles verde claro translúcidos, textos
  externos claros; recarga con una flecha circular, TDS con vaso/minerales y pH
  mantiene matraz. Reemplaza la paleta celeste principal de D36, conserva Aero/Eco
  y las cuatro variantes de navegación D41. No cambia lógica, datos o hardware.

- D43 — Corrección del usuario: fondo demasiado oscuro. Vigente en 0.6: jardín
  mucho más claro con velo menta luminoso, texto oscuro y paneles realmente
  translúcidos (base alfa 110/255, placa 68/255). De noche base 180, placa 130.
  Reemplaza el oscurecimiento diurno de D42; conserva hojas, pH/TDS diferenciados,
  recarga y variantes de navegación. No cambia datos ni lógica.

## Energía, telemetría y procesos — 2026-10-04

- D44 — Confirmado por usuario: ESP32 alimentado por fuente de corriente, lector
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

- D48 — Usuario: PoC con temperatura, pH, iluminación y flotador físicos, TDS
  simulado identificado por variable. Reemplaza la propuesta inicial de solo
  temperatura para el taller; no modifica todavía v1. Lux/nivel discreto deben
  representarse sin porcentajes inventados y TDS simulado no autoriza dosificación.
- D49 — Usuario acepta OVHcloud VPS-1 compartido con un proyecto similar para
  preparar alojamiento de la PoC. Separar código, datos, credenciales y permisos;
  verificar recursos con ambos proyectos. No afirma contratación/despliegue ni
  selecciona infraestructura definitiva; reemplaza Render+Aiven como candidato
  preferido para este taller, conservando D47 como antecedente.
- D50 — Usuario solicita repositorio GitHub en `komvo` para documentos, pruebas
  y código, antes del taller. Propuesta privada reemplazada por autorización
  explícita posterior de visibilidad pública; documentos originales incluidos,
  secretos/dependencias/cachés/compilaciones excluidos. Autoriza crear y subir la
  versión inicial; sincronización futura requiere commits/push y no implica
  acceso de escritura del compañero.

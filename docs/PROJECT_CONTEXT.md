# Contexto del proyecto

Consolidado: 2026-09-30. Fuentes: instrucciones actuales del usuario, código local
y documentos enumerados abajo. Estado ejecutable: ver STATUS.

HydroMate automatiza y monitorea hidroponía vertical. Primera unidad física:
torre recirculante de al menos seis plantas; evolución a múltiples torres por
cuenta, perfiles, historial, alertas y configuración remota.
El ESP32 controla localmente; Laravel procesa funciones no críticas y expone API;
PostgreSQL persiste; Android consume REST. Mosquitto es el broker definitivo.

## Incremento vigente
Actualización 07/10: usuario solicita ejecutar primero local y documentar pasos.
Contratos v1/v2 compatibles, Android lux/flotador/origen e integrador Paho con
bandeja y ACK implementados; firmware nuevo cargado y diez entregas verificadas. Cuatro
variables físicas y TDS simulado; hardware disponible según bitácora 05/10.
Ensayos/resultados actuales en STATUS; comentarios anteriores se conservan
como historial. VPS compartido aceptado como candidato, no contratado/desplegado.

El usuario eliminó Wokwi como requisito y eligió Android mínimo como primer
frontend. Primero base de datos y API probadas con datos sintéticos; después app
en teléfono; finalmente conectar el armado ESP32 real mediante MQTT/integración.
No construir panel Blade por separado. Backend probado y volumen Docker confirmado.
Paso 2: mensaje documentado en TELEMETRY_CONTRACT.md; firmware aún pendiente. Los datos de prueba no son
mediciones físicas ni calibración química.

## Hardware y restricciones
Seleccionados/contemplados, no necesariamente comprados ni probados: ESP32,
DS18B20, flotador, PH-4502C o equivalente, SEN0244, BH1750/GY-302, ADS1115;
INA219/INA226 opcional sujeto a compatibilidad. Bomba seleccionada 24 V, 25 W,
1000–1200 L/h nominales; no equivalen a caudal medido. D4184 para conmutación DC.
Sensores/actuadores no se alimentan desde GPIO. Cuatro canales de dosificación:
nutrient_a, nutrient_b, ph_up, ph_down. Mecanismo final pendiente de validación.
Seguridad local y estado seguro prevalecen sobre cualquier orden remota.

Base física descrita el 22/09: depósito 51 L, PVC azul 6 pulgadas, subida 3/4,
aproximadamente 1.30 m visibles; apoyo de torre en fondo y tapa como guía lateral.
No hay mediciones físicas auditadas en esta sesión.

## Fuentes y discrepancias que no deben reinvestigarse sin motivo
- `Documentos PDC/T6_PDC_1288703.docx`: fecha interna 23/09/2026, archivo modificado
  30/09. RF/RNF, restricciones, arquitectura; presupuesto máximo escrito $5,000 MXN.
- `Documentos PDC/Planeacion_integral_HydroMate_contexto_actualizado_22-09-2026.docx`:
  diseño físico, alternativas de dosificación, pago/envío de bomba por confirmar;
  gasto mínimo escrito $1,472.25 MXN, cargos por conciliar.
- `Documentos PDC/Plan_trabajo_HydroMate_sep_nov_2026.docx`: fecha interna 22/09,
  periodo 28/09–30/11; separa Basic (UNO/C++, sin red) y Smart (ESP32);
  registra $1,872.74 MXN e incluye bomba/LECA. No reconciliado con la fuente anterior.
- `Documentos PDC/T4_PDC_128870.docx`: alternativas del 16/09; contiene referencias
  anteriores de presupuesto y alcance (incluido $6,000). T6 es posterior.
- Instrucciones del usuario del 30/09: priorizar PoC Smart y diferir funciones
  avanzadas. Actualizan la prioridad del plan Basic sin borrar esa línea histórica.

No inferir vigencia solo por fecha del filesystem o por carpetas de versiones.
No afirmar compras recibidas ni presupuesto disponible sin conciliación.
Los documentos EC0935 son evidencia documental, no prueba automática de ejecución.

## Evolución, fuera de la PoC
Android preferentemente Kotlin si no existe trabajo previo; BLE para Wi-Fi;
Sanctum previsto, FCM futuro; propiedad/vinculación, grupos lógicos sin perder
identidad, perfiles versionados y clonables, comandos con ID/ack/estado.
Los perfiles y comandos nunca pueden desactivar protecciones locales.

Android implementado en mobile/ (Kotlin). Rediseño solicitado el 03/10: versión 0.2
con cinco secciones, temas del sistema, gráfico de historial, configuración separada
y actualización inicial/manual. Cultivo y control son preparación visual pendiente,
sin endpoints ni acciones. Sigue pendiente instalar/probar UI en teléfono.
Guía: mobile/README.md; decisiones D27–D30. Prioridad ESP32 después de esa prueba.

Actualización posterior del 03/10: el prompt de rediseño Frutiger Aero reemplaza
la dirección visual 0.2 por 0.3. Día inicial, cuatro pestañas y Equipo secundario;
demo exclusiva debug, offline y explícita. AERO_DESIGN/AERO_ACCEPTANCE recogen
alcance y pendientes; decisiones D31–D35. Compilación/JVM comprobadas, UI en
Android todavía pendiente. No se confirmó la planeación física del 24/09 citada
por el DOCX: torre dibujada de tres niveles/seis sitios es referencia del encargo,
no cambio confirmado de dimensiones, actuadores o compras.

Actualización 04/10: dirección visual Aero Eco 0.4 de los dos MD del usuario.
Cinco destinos, cristal/agua/hoja natural e iconos originales. D36–D38 reemplazan
la presentación de 0.3, sin cambios al contrato/lógica. Instalación USB y 26
revisiones nativas de composición observadas; QA manual e integración real
pendientes según AERO_ACCEPTANCE. Docker no disponible en esta sesión.

Refinamiento posterior 04/10, vigente: 0.6.0-garden y D39–D43. Ilustraciones de
cristal detalladas; únicamente cuatro iconos de barra tienen variantes de menor
ruido, Cultivo conserva su emblema. Recarga renovada y pH/TDS diferenciados.
La primera variante de jardín oscuro fue reemplazada a petición del usuario por
fondo botánico muy claro y tarjetas verdes translúcidas. Sin cambios funcionales.
Instalada por USB, seleccionada la apariencia clara en el teléfono; evidencia
android-garden-2026-10-04.json y capturas garden-light-2026-10-04. AERO_ACCEPTANCE
distingue revisión visual de pendientes.

Actualización de energía 04/10: el usuario confirma ESP32 con fuente de corriente,
leyendo sensores y controlando bombas. Solicita documentar máximo ahorro seguro y
otras optimizaciones. ENERGY_OPTIMIZATION.md fija dirección de diseño D44–D47:
controlador disponible, adquisición/red separadas, radio y frecuencia optimizados
primero; sueño ligero condicionado y deep sleep excluido en operación normal.
Cadencias 5 s/300 s y prueba 30 s son propuestas por validar, no firmware ejecutado.
Nube gratuita evaluada, no contratada; MQTT/bridge y seguridad de acceso pendientes.

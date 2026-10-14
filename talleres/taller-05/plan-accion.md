# Plan de cierre del Taller 5 y semanas posteriores

Actualizado 14/10/2026. Entrega final confirmada por el usuario: **2 de diciembre
de 2026**. Sustituye el cierre histórico del 30/11 y el calendario sin fecha
confirmada. Taller 5 pendiente de cierre; su entrega original fue el 16/09.
VPS Ubuntu prestado disponible sin costo para el proyecto; ya aloja otro sistema.

## Evolución documentada y trabajo realizado

Las fechas siguientes son cortes documentales o pruebas observadas, no fechas
exactas de cada pedido cuando no existe comprobante. Los originales se conservan.

| Periodo / corte | Avance registrado | Fuente y límite |
|---|---|---|
| Agosto–primera mitad de septiembre | Definición del problema, selección de hidroponía vertical y comparación de arquitectura/componentes. | Talleres T1–T4 y planeaciones históricas; no acredita construcción completa. |
| 20/09 | Compras de depósito, distribuidor, semillas, hidráulica y lámpara; pedidos de bomba y LECA/net pots. | Planeación de compras 20/09: pagos y materiales; entregas de pedidos todavía en camino. |
| 22/09 | PVC de 6 pulgadas comprado por $400; estructura revisada para apoyo al fondo del depósito de 51 L. Se identifican pagos rechazados/reembolsos. | Planeación consolidada 22/09; bomba/LECA pendientes de conciliación. No equivale a torre hidráulica probada. |
| 28–30/09 | Plan de trabajo Basic/Smart y presupuesto; prioridad cambia a PostgreSQL → Laravel → Android → ESP32. API, identidad y datos sintéticos probados. | Plan sep–nov y STATUS/DECISIONS. El plan Basic primero queda como antecedente, reemplazado en prioridad. |
| 03–04/10 | Android compilado/instalado, Inicio/Historial y refinamiento visual; documentación del ahorro seguro. | Evidencias de software/Android en docs/evidence; no demuestra ahorro medido. |
| 05/10 | ESP32, DS18B20, BH1750, flotador, ADS1115 y pH probados; calibración inicial de pH documentada; TDS diagnosticado no confiable y reemplazo elegido. | Bitácora de sensores 05/10; no confirma compra/recepción del nuevo TDS. |
| 07/10 | Contrato v2, bridge durable, firmware de telemetría, diez entregas físicas a PostgreSQL local, Android real, corte/recuperación y aproximación de 8.24 s. | Evidencia talleres/taller-05/pruebas. Una entrega recuperada + nueve adquisiciones nuevas; nube pendiente. |
| 14/10 | Fecha final 02/12 y VPS prestado Ubuntu confirmados; aplazamiento del actuador comunicado por usuario. Revisión de cumplimiento/despliegue y documentación. | Confirmación del usuario; no se acredita despliegue por disponer de servidor. Adjuntar autorización docente. |

## Semanas restantes

Este calendario es planeado desde el corte del 14/10; no presenta tareas futuras
como realizadas. Continúa el trabajo existente con ESP32 y Android, sin rehacer
el proyecto Basic ni agregar funciones avanzadas al cierre de viabilidad.

| Periodo | Trabajo previsto | Evidencia / criterio de cierre |
|---|---|---|
| 14–18 octubre | Recuperar arranque local; revisar acceso/inventario VPS y convivencia con proyecto alojado; preparar despliegue propio y certificados. | API/BD local verificadas; inventario, respaldo y configuración de despliegue revisada. |
| 19–25 octubre | Backend/PostgreSQL/MQTT/bridge en VPS, HTTPS/TLS y protección mínima de acceso; conectar ESP32 y Android; repetir ensayo. | Diez adquisiciones físicas nuevas consecutivas, éxitos/fallos, consulta, tiempo y capturas en nube; video y cierre T5. |
| 26 octubre–1 noviembre | Revisar montaje y sensores; gestionar reemplazo TDS y conciliar gastos; pruebas hidráulicas si montaje disponible. | Lecturas/referencias y fallos documentados; recepción real del reemplazo solo cuando ocurra; prueba de fugas/retorno. |
| 2–8 noviembre | Firmware local seguro para bomba/iluminación: nivel bajo, sensor inválido, timeout y reinicio seguro; definir canales de dosificación. | Pruebas de salidas de banco con agua/carga segura y bloqueos comprobados. No dosificación con TDS simulado. |
| 9–15 noviembre | Prototipo alfa: comando remoto básico, identificación y confirmación del resultado con segunda validación local. | Frontend → backend → ESP32 → salida, rechazo por nivel bajo y duplicado; evidencia para levantar aplazamiento. |
| 16–22 noviembre | Integrar torre y canales disponibles; calibrar dosis con agua, mezcla/relectura y límites; ensayos de estabilidad/cortes. | Ensayos registrados y alcance físicamente validado. Bloquear funciones químicas sin sensor/actuador confiable. |
| 23–29 noviembre | Prueba integrada prolongada, errores Android/red, presupuesto final y documentación; preparar presentación/video. | Matriz de aceptación con resultados auténticos; esquema, código y evidencias completos. |
| 30 noviembre–1 diciembre | Margen de correcciones y ensayo de entrega; respaldo y revisión de secretos antes de publicar. | Demostración repetible y paquete final revisado. |
| 2 diciembre | Entrega final del proyecto. | Presentación y evidencia del alcance validado; pendientes identificados y aceptación docente. |

Si sensor/repuesto se retrasa, conservar monitoreo y bloquear la función que
depende de él. El alcance final de T6/T7 es más amplio que la PoC: autenticación,
perfiles, FCM y provisión BLE requieren priorización posterior; no se dan por
terminados ni se incorporan automáticamente a este incremento.

## Secuencia de cierre de la viabilidad

| Orden | Trabajo | Criterio para avanzar | Estimación / estado |
|---|---|---|---|
| 1 | Conservar datos, arrancar PostgreSQL y API | Respaldo + respuestas HTTP comprobadas | Realizado local |
| 2 | Contrato físico v2 y Android | Lux/flotador/origen; validación y compatibilidad v1 | Implementado; tests pasan |
| 3 | Mosquitto + integrador | Diez mensajes PC, ACK tras INSERT, inválido y duplicado | Realizado sintético local |
| 4 | Firmware ESP32 y montaje | Compilar/cargar; sensores reales y TDS simulado explícito | Realizado; pH/Wi-Fi corregidos |
| 5 | Diez envíos físicos + fallos + Android | Mismas secuencias en monitor, BD y app; tiempo sensor–pantalla | Realizado local: diez entregas, Inicio/Historial, corte y aproximación 8.24 s |
| 6 | Documentar aplazamiento del actuador | Usuario comunica autorización; adjuntar evidencia docente y justificación técnica | Aplazado para alfa, sin prueba física afirmada |
| 7 | Provisionar HydroMate en VPS prestado | Acceso y separación de proyectos, backup, HTTPS/MQTT TLS y API protegida | VPS disponible según usuario; despliegue pendiente |
| 8 | Repetir ensayo en nube | Diez registros físicos, latencia, inválido/reconexión, captura despliegue | Una sesión |
| 9 | Cerrar paquete T5 | PDF técnico revisado, video, código, capturas, errores, diagramas y README | Una sesión |
| 10 | Revisión final y entrega | Lista de requisitos completa y aceptación docente | Fecha acordada |

La tabla semanal anterior reemplaza esta planeación relativa; las tareas de
seguridad y control pertenecen a etapas posteriores al cierre de T5.

## Presupuesto preliminar

| Concepto | Situación | Importe pendiente |
|---|---|---|
| ESP32 y sensores actuales | Disponibles según usuario; TDS defectuoso | Documentar costo ya pagado, no volver a presupuestar como compra nueva |
| Reemplazo TDS | Pendiente; no bloquea PoC con simulación identificada | Solicitar cotización real |
| VPS OVHcloud Ubuntu compartido | Prestado; ya aloja proyecto del compañero | $0 para HydroMate según usuario el 14/10; no asumir renovación gratuita indefinida |
| Reparto VPS | Sin pago comunicado | No presupuestar 50/50 ni contratación propia |
| Dominio | Definir al desplegar TLS | Cotizar o usar alternativa válida disponible; sin compra automática |
| Bibliotecas/runtime local | Herramientas ya disponibles, sin compra adicional realizada | Sin costo de contratación observado en esta etapa |
| Cableado/repuestos/contingencia | Revisar inventario físico | Cotizar faltantes y reservar margen acordado |

No hay total confiable hasta conciliar costos y cotizaciones. Diferenciar gasto
real, estimación y compra pendiente en el reporte.

### Base histórica de costos

| Concepto | Importe MXN | Estado documental |
|---|---|---|
| Depósito 51 L | 389.00 | Comprado según planeación 22/09 |
| Maceta distribuidor | 105.00 | Comprada según planeación 22/09 |
| Semillas | 208.00 | Compradas según planeación 22/09 |
| Manguera/PVC/adaptadores | 126.94 | Comprados según planeación 22/09 |
| Lámpara cultivo | 243.31 | Pagada, en camino en el corte 22/09 |
| PVC 6 pulgadas | 400.00 | Comprado según planeación 22/09 |
| Subtotal confirmado en ese corte | **1,472.25** | Histórico, no total actual de todo el proyecto |
| Bomba | 242.10 | Pago/envío por conciliar en 22/09; plan posterior la incluye |
| LECA | 158.39 | Plan sep–nov la incluye tras descontar net pots de $188; cargo/recepción por conciliar |
| Total del plan sep–nov | **1,872.74** | 1,472.25 + 242.10 + 158.39; no adoptarlo como gasto comprobado sin conciliación |
| ESP32, sensores, fuente/driver y reemplazo TDS | Por conciliar/cotizar | Hardware disponible en cortes posteriores, sin importes nuevos comprobados |
| VPS prestado | **0.00** | Costo comunicado 14/10 |

T6 actualizado fija máximo de $5,000 MXN; reemplaza referencias históricas de
$6,000. El margen actual no puede calcularse sin integrar costos de electrónica
y compras posteriores. El presupuesto es preliminar y mantiene trazabilidad.

## Matriz de riesgos

| Riesgo | Impacto | Prevención | Contingencia |
|---|---|---|---|
| TDS defectuoso/simulado confundido con real | Evidencia inválida y decisiones erróneas | Etiquetar por variable en JSON/BD/app y reporte | Reemplazar/calibrar después; no controlar dosis con TDS simulado |
| Wi-Fi/firewall/aislamiento de clientes | ESP32 no llega al broker | Red de confianza, permiso limitado, verificar IP/banda y broker | Diagnóstico por capa; conservar pendiente; ensayo controlado en red compatible |
| Reinicio/reenvío reutiliza secuencia | Duplicados/conflictos | Reserva NVS y pendiente estable; índice único y comparación | Detener conflicto; reconciliar identidad sin borrar BD |
| Datos/servicios mezclados con compañero | Acceso cruzado/pérdida de datos | BD, cuentas, tópicos/ACL y configuraciones separados | Restaurar backup propio y revocar acceso afectado |
| Credenciales publicadas | Acceso no autorizado | .env/secrets/.local ignorados; revisar diff y capturas | Rotar secreto filtrado; no basta eliminar archivo del último commit |
| Sensor inválido o pH deriva | Valores engañosos | Validación explícita, revisión de conexiones y calibración documentada | Bloquear muestra; reparar/recalibrar, sin inventar valores |
| Lectura en cola llega tarde | App parece actual con dato viejo | Etiqueta «recibido» y documentar límite de tiempo de adquisición | Añadir adquisición/antigüedad antes de operación final |
| Pérdida de acceso al VPS prestado / retraso de nube | Taller incompleto aunque local funcione | Acordar disponibilidad hasta 02/12, acceso propio y respaldo | Recuperar en alojamiento autorizado; no presentar prueba local como nube |
| Actuador sin seguridad | Daño físico/dosificación accidental | PoC actual sin bombas; definir interbloqueos antes de control | Comando de banco seguro o aplazamiento docente autorizado |
| Cortes de energía/espacio en bandeja | Pérdida o atraso de transmisión | Backup, NVS, bandeja persistente y monitoreo | Recuperar servicios y misma identidad; evaluar retención/límites de disco |

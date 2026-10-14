# Plan de cierre del Taller 5 y semanas posteriores

Fecha final del proyecto no confirmada. Entrega T5 vencida desde 16/09. Calendario
relativo por sesiones; no presentar 30/11 como fecha aprobada. Duraciones estimadas
suponen disponibilidad del hardware, red, VPS y revisión docente.

| Orden | Trabajo | Criterio para avanzar | Estimación / estado |
|---|---|---|---|
| 1 | Conservar datos, arrancar PostgreSQL y API | Respaldo + respuestas HTTP comprobadas | Realizado local |
| 2 | Contrato físico v2 y Android | Lux/flotador/origen; validación y compatibilidad v1 | Implementado; tests pasan |
| 3 | Mosquitto + integrador | Diez mensajes PC, ACK tras INSERT, inválido y duplicado | Realizado sintético local |
| 4 | Firmware ESP32 y montaje | Compilar/cargar; sensores reales y TDS simulado explícito | Realizado; pH/Wi-Fi corregidos |
| 5 | Diez envíos físicos + fallos + Android | Mismas secuencias en monitor, BD y app; tiempo sensor–pantalla | Realizado local: diez entregas, Inicio/Historial, corte y aproximación 8.24 s |
| 6 | Revisar requisito actuador con docente | Comando físico seguro o autorización escrita de aplazamiento | En paralelo; pendiente |
| 7 | Contratar/provisionar VPS compartido | Acceso y separación de proyectos, backup, HTTPS/MQTT TLS y API protegida | Una o dos sesiones tras contratación |
| 8 | Repetir ensayo en nube | Diez registros físicos, latencia, inválido/reconexión, captura despliegue | Una sesión |
| 9 | Cerrar paquete T5 | PDF técnico revisado, video, código, capturas, errores, diagramas y README | Una sesión |
| 10 | Revisión final y entrega | Lista de requisitos completa y aceptación docente | Fecha acordada |

Después de T5: semana 1 validar sensores/calibración y fallos; semana 2 firmware
de seguridad y canales de actuador; semana 3 ensayo de control autorizado e
integración; semana 4 estabilidad, consumo y documentación. Es una propuesta,
ajustable a semanas realmente disponibles; no iniciar automatización avanzada
antes de definir límites, interbloqueos y aceptación.

## Presupuesto preliminar

| Concepto | Situación | Importe pendiente |
|---|---|---|
| ESP32 y sensores actuales | Disponibles según usuario; TDS defectuoso | Documentar costo ya pagado, no volver a presupuestar como compra nueva |
| Reemplazo TDS | Pendiente; no bloquea PoC con simulación identificada | Solicitar cotización real |
| VPS OVHcloud VPS-1 compartido | No se ha comprobado contratación | Usuario recuerda alrededor de 90 MXN; verificar moneda, periodo, impuestos y renovación |
| Reparto VPS | Dos proyectos | 50/50 solo si lo acuerdan; no afirmar 45 MXN sin factura/precio confirmado |
| Dominio | Definir al desplegar TLS | Cotizar o usar alternativa válida disponible; sin compra automática |
| Bibliotecas/runtime local | Herramientas ya disponibles, sin compra adicional realizada | Sin costo de contratación observado en esta etapa |
| Cableado/repuestos/contingencia | Revisar inventario físico | Cotizar faltantes y reservar margen acordado |

No hay total confiable hasta conciliar costos y cotizaciones. Diferenciar gasto
real, estimación y compra pendiente en el reporte.

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
| Falta VPS/fecha docente | Taller incompleto aunque local funcione | Resolver contratación y entrega con docente en paralelo | Solicitar ventana acordada; no presentar prueba local como nube |
| Actuador sin seguridad | Daño físico/dosificación accidental | PoC actual sin bombas; definir interbloqueos antes de control | Comando de banco seguro o aplazamiento docente autorizado |
| Cortes de energía/espacio en bandeja | Pérdida o atraso de transmisión | Backup, NVS, bandeja persistente y monitoreo | Recuperar servicios y misma identidad; evaluar retención/límites de disco |

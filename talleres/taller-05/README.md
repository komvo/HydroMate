# Taller 5 Prueba de viabilidad

Estado al 7 de octubre de 2026: entrega pendiente desde el 16 de septiembre.
Este índice organiza materiales; todavía no es el reporte final ni acredita el
recorrido físico completo. Fecha final del proyecto sin confirmar.

## Alcance acordado

Temperatura, pH, iluminación en lux y flotador físicos; TDS simulado identificado
por variable. ESP32 → MQTT/TLS → Mosquitto → integración → Laravel en nube →
PostgreSQL → Android HTTPS. Adaptación de contrato e integración pendientes.
OVHcloud VPS-1 compartido es opción aceptada; no se afirma que esté contratado.

## Material disponible

| Material | Archivo fuente | Alcance de la evidencia |
|---|---|---|
| Sketch de sensores | [tsts.ino](../../Documentos%20PDC/tsts/tsts.ino) | Lectura local; sin publicación MQTT |
| Bitácora física | [DOCX](../../Documentos%20PDC/HydroMate_Bitacora_Pruebas_Sensores_Diagnostico_TDS_05-10-2026.docx) | Sensores funcionales y diagnóstico TDS registrados |
| Backend y pruebas | [Laravel](../../hydromate-backend/) | Código y tests existentes |
| Contrato actual | [Telemetría v1](../../docs/TELEMETRY_CONTRACT.md) | Requiere evolución; no acepta magnitudes parciales actuales |
| API local | [Evidencia HTTP](../../docs/evidence/backend-step1-http.json) | Prueba histórica sintética; no es sensor ni nube |
| BD local | [Evidencia PostgreSQL](../../docs/evidence/postgres-step1.json) | Prueba histórica local |
| Android y pruebas | [Proyecto Kotlin](../../mobile/) | App instalada; integración final pendiente |
| Revisión Android | [Resultado del 04/10](../../docs/evidence/android-garden-2026-10-04.json) | Composición y compilación; no acredita conexión con sensores |
| Capturas Android | [Carpeta](../../docs/evidence/garden-light-2026-10-04/) | Incluye vistas de prueba simuladas y estado real de error |
| Arquitectura | [Documento](../../docs/ARCHITECTURE.md) | Diseño y pendientes; diagrama implementado por producir |

## Organización de la entrega técnica

- `reporte.pdf`: por generar cuando existan pruebas observadas y revisión visual.
- `codigo/`: índice de las versiones utilizadas; código fuente en sus rutas originales.
- `pruebas/`: capturas, registros y tiempos de las pruebas del taller.
- `errores-resultados/`: bitácora con fallos, diagnóstico, corrección y repetición.
- `diagramas/`: conexión física y flujo realmente implementado, con fuente editable.

## Criterios pendientes

- Backend desplegado y acceso HTTPS/MQTT/TLS comprobado.
- Diez transmisiones consecutivas y diez registros con variables físicas.
- Registro de éxitos/fallos y tiempo aproximado sensor–frontend.
- Dato inválido y pérdida temporal de conexión con resultados observados.
- Android mostrando origen por variable, última recepción e historial.
- Evidencia de despliegue, esquema de BD, consulta y video de funcionamiento.
- Presupuesto conciliado, cronograma relativo y al menos cinco riesgos.
- Comando físico básico o aplazamiento autorizado por el docente.

No incluir contraseñas, tokens, datos del proyecto del compañero ni pantallas
con credenciales. Conservar errores auténticos y documentar sus limitaciones.

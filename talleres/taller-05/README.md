# Taller 5 Prueba de viabilidad

Estado al 7 de octubre de 2026: entrega pendiente desde el 16 de septiembre.
Este índice organiza materiales. El recorrido físico local pasó diez entregas;
todavía no es el reporte final ni acredita despliegue en nube. Fecha final sin confirmar.

## Alcance acordado

Temperatura, pH, iluminación en lux y flotador físicos; TDS simulado identificado
por variable. ESP32 → MQTT/TLS → Mosquitto → integración → Laravel en nube →
PostgreSQL → Android HTTPS en nube. Contrato v2 y bridge local implementados;
ensayos sintéticos y diez entregas del ESP32 pasan. Nube y cierre según STATUS.
OVHcloud VPS-1 compartido es opción aceptada; no se afirma que esté contratado.

## Material disponible

| Material | Archivo fuente | Alcance de la evidencia |
|---|---|---|
| Sketch de sensores | [PruebaSensores1.ino](../../Documentos%20PDC/tests/PruebaSensores1.ino) | Lectura local; sin publicación MQTT |
| Bitácora física | Referencia local, retirada de GitHub por solicitud del usuario | Sensores funcionales y diagnóstico TDS registrados; resumen en STATUS |
| Backend y pruebas | [Laravel](../../hydromate-backend/) | Código y tests existentes |
| Contrato actual | [Telemetría v2](../../docs/TELEMETRY_CONTRACT.md) | Lux, flotador y origen; v1 preservado compatible |
| API local | [Evidencia HTTP](../../docs/evidence/backend-step1-http.json) | Prueba histórica sintética; no es sensor ni nube |
| BD local | [Evidencia PostgreSQL](../../docs/evidence/postgres-step1.json) | Prueba histórica local |
| Android y pruebas | [Proyecto Kotlin](../../mobile/) | App instalada; integración final pendiente |
| Revisión Android | [Resultado del 04/10](../../docs/evidence/android-garden-2026-10-04.json) | Composición y compilación; no acredita conexión con sensores |
| Capturas Android | [Carpeta](../../docs/evidence/garden-light-2026-10-04/) | Incluye vistas de prueba simuladas y estado real de error |
| Arquitectura | [Documento](../../docs/ARCHITECTURE.md) | Diseño y pendientes; diagrama implementado por producir |

## Organización de la entrega técnica

- [Procedimiento local paso a paso](procedimiento-local.md): estructura, comandos y conceptos.
- [Plan de acción, presupuesto y riesgos](plan-accion.md): secuencia y criterios de cierre.
- [Bitácora de errores/resultados](errores-resultados/bitacora-2026-10-07.md): ensayos auténticos y límites.
- [Firmware nuevo](../../embedded/README.md), [integrador](../../scripts/mqtt_bridge.py) y pruebas en `pruebas/`.

- [Reporte técnico local provisional](reporte-tecnico-local.pdf): pruebas y capturas
  con pruebas de software y límites; no sustituye el reporte final de nube.
- `reporte.pdf` final: por generar cuando exista recorrido físico/nube y revisión.
- `codigo/`: índice de las versiones utilizadas; código fuente en sus rutas originales.
- `pruebas/`: capturas, registros y tiempos de las pruebas del taller.
- `errores-resultados/`: bitácora con fallos, diagnóstico, corrección y repetición.
- `diagramas/`: conexión física y flujo realmente implementado, con fuente editable.

## Criterios pendientes

- Backend desplegado y acceso HTTPS/MQTT/TLS comprobado.
- Repetir en nube las diez transmisiones físicas ya verificadas localmente.
- Repetir en nube la aproximación de tiempo sensor–frontend local (8.24 s, incluye ADB).
- Repetir corte/reconexión en nube; pH inválido/red 5 GHz/corte local documentados.
- Repetir aceptación Android con backend en nube; Inicio/Historial reales capturados.
- Evidencia de despliegue, esquema de BD, consulta y video de funcionamiento.
- Presupuesto conciliado, cronograma relativo y al menos cinco riesgos.
- Comando físico básico o aplazamiento autorizado por el docente.

No incluir contraseñas, tokens, datos del proyecto del compañero ni pantallas
con credenciales. Conservar errores auténticos y documentar sus limitaciones.

# HydroMate — instrucciones permanentes

## Recuperación rápida del contexto
Leer primero este archivo, `docs/STATUS.md`, `docs/PROJECT_CONTEXT.md` y
`docs/DECISIONS.md`. Consultar `docs/ARCHITECTURE.md` para arquitectura y contratos.
Leer únicamente el código y documentos relacionados con la tarea actual.
No repetir auditorías completas salvo solicitud explícita o evidencia de contexto
desactualizado. Los documentos académicos en `Documentos PDC/` son referencias:
consultarlos por dudas, contradicciones, decisiones por verificar o trabajo sobre
ese documento. No modificarlos sin solicitud explícita.

## Prioridad y alcance
Prioridad actual (cambio del usuario el 30/09): PostgreSQL → Laravel API → app
Android mínima → ESP32 físico. Wokwi no es necesario; no crear dashboard Blade
como frontend paralelo. Usar lecturas sintéticas identificadas hasta tener sensores.
Backend/BD probados y contrato en docs/TELEMETRY_CONTRACT.md. Android en mobile/
compilado e instalado por USB; QA manual e integración real parcialmente pendientes. No iniciar
funciones avanzadas.
No iniciar Android completo, autenticación completa, perfiles sociales, grupos,
Firebase, VPS definitivo o automatización de actuadores por iniciativa propia.
Mantenerlos como evolución, sin crear anticipadamente todas las tablas.

## Coherencia técnica
- Dirección visual Android vigente: `docs/AERO_DESIGN.md`; aceptación y pruebas
  pendientes en `docs/AERO_ACCEPTANCE.md`. Mantener demo aislada en debug,
  explícitamente marcada, sin fallback automático ni órdenes simuladas.
- Arquitectura seleccionada: ESP32, MQTT/TLS, Mosquitto, Laravel, PostgreSQL,
  Android nativo por HTTPS/REST. Android nunca accede directamente a la BD.
- PoC anterior Wokwi/Blade reemplazada en prioridad; MQTT/bridge se abordarán al conectar ESP32 físico.
- Conservar identidad de cada torre; la PoC puede usar solo una.
- Seguridad crítica local en ESP32: nivel bajo, sensores inválidos, límites de
  dosis, mezcla, exclusión pH Up/Down, tiempos máximos y reinicio seguro.
- Dosificación física pendiente: abstraer canales A/B/pH Up/pH Down;
  no asumir que todos usan bombas peristálticas.
- No trasladar deep sleep de la demostración a un controlador final sin analizar
  seguridad y recepción de comandos.
- Ahorro y optimización: `docs/ENERGY_OPTIMIZATION.md`. Fuente de corriente y
  control de bombas confirmados; estrategia documentada, aún sin firmware ni
  consumo medido. Sin deep sleep normal; sueño ligero solo tras validar seguridad.
- Distinguir confirmado, seleccionado, simulado, planeado, pendiente y mejora
  futura. No inventar resultados, calibraciones, compras ni mediciones.

## Trabajo seguro y eficiente
Revisar Git antes de cambios relevantes; respetar cambios existentes. No reset
destructivo, clean, reescritura de historial ni push sin autorización explícita.
Si no hay Git, recomendar inicializarlo; no fingir un diff de repositorio.
Inspeccionar servicios y persistencia antes de cambiar contenedores. Nunca borrar
datos, tablas ni contenedores para solucionar problemas sin confirmación.
No cambiar credenciales, firewall/router, exponer servicios, generar costos o
enviar información privada a terceros sin autorización.
Usar .env y ejemplos sin secretos; nunca imprimir ni versionar credenciales.
No instalar software global innecesario. Detectar versiones reales y reutilizar
herramientas instaladas. No instalar Boost u otras herramientas solo por una
plantilla de inicialización; justificar su necesidad para el incremento.

## Validación y cierre
Diagnosticar por capa, reproducir, aplicar cambio mínimo y volver a probar.
Priorizar código claro, validación explícita y manejo de errores. No agregar
microservicios, Redis, Kubernetes o colas sin necesidad actual.
Una tarea termina con ejecución/prueba observada cuando sea posible, revisión de
cambios y contexto actualizado. Separar prueba realizada de prueba pendiente.
Actualizar STATUS al cerrar una etapa; DECISIONS si cambia una decisión;
ARCHITECTURE si cambia el diseño; SETUP si cambia el arranque.
Mantenerlos compactos. Marcar decisiones reemplazadas, nunca borrarlas en silencio.
Explicar brevemente conceptos nuevos: qué son, para qué sirven, dónde están,
qué reciben y qué producen; evitar clases largas.

## Rutas
Raíz: `C:\Hydromate`; backend: `hydromate-backend/`.
Firmware futuro: `embedded/`; Android futuro: `mobile/`; integración: `scripts/`.
Consultar STATUS: una ruta prevista no significa que exista.
Si se abre directamente el backend, su AGENTS remite a estos mismos documentos.

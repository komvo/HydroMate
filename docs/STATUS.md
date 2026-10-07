# Estado actual — 2026-10-07

## Taller de viabilidad pendiente — revisión del 2026-10-07

- Aclaración posterior del usuario: usar temperatura, pH, luz y flotador reales,
  más TDS simulado identificado por variable; reemplaza la propuesta inicial de
  una sola temperatura. No implementado. BH1750 debe conservar lux y flotador
  nivel discreto; v1 necesita evolución antes de integrar esos datos.
- Sketch localizado y revisado: `Documentos PDC/tsts/tsts.ino`; conserva pruebas
  locales, sin Wi-Fi/MQTT. Anuncia TDS en A1 pero lee A3: discrepancia histórica
  pendiente de resolver al integrar reemplazo; no se modificó el original.
- OVHcloud VPS-1 compartido con un proyecto similar aceptado para preparar la
  PoC. Sin compra/despliegue comprobados; separar aplicaciones/datos/permisos.
- Usuario solicita primero repositorio GitHub en `komvo`, con documentos,
  código y pruebas; autoriza posteriormente que sea público. Git local inicializado,
  README/política preparados y remoto https://github.com/komvo/HydroMate creado.
  Push inicial pendiente de revisión final; secretos y archivos locales excluidos.
- Requisito docente comunicado por usuario: talleres organizados en GitHub,
  preferentemente PDF; desde Taller 5, reportes técnicos con código, capturas,
  errores/resultados, diagramas y archivos utilizados. `talleres/` contiene copias
  verificadas por hash de los PDF existentes T1–T4/T6/T7 y estructura técnica T5.
  No se afirma revisión/aprobación de T6/T7 ni reporte final/pruebas completas T5.

- Usuario confirma entrega vencida el 16 de septiembre; fecha final del proyecto
  todavía sin definir. El 30/11 es referencia histórica, no cierre confirmado.
- Revisada la bitácora del 05/10 en `Documentos PDC/`: ESP32 DevKit V1,
  DS18B20 (GPIO 4), BH1750, flotador (GPIO 27), ADS1115 y pH funcionales según
  pruebas registradas. I2C en GPIO 21/22; pH en A0, calibración de dos puntos
  documentada. Usuario confirma sensores conectados y probados salvo TDS.
- TDS Meter V1.0 con señal baja/no confiable: reemplazo seleccionado en bitácora;
  no afirmar compra/recepción del reemplazo ni usar sus ppm como medición válida.
  Bomba/D4184/potencia figuran pendientes de integración en esa fuente.
- No se repitieron ensayos físicos ni pruebas de red en esta revisión. Falta
  demostrar ESP32 real → backend en nube → PostgreSQL → Android, diez envíos,
  fallos/tiempos, Git y paquete de evidencias. Contrato/API/BD/Android v1 exigen
  todas las variables: necesitan evolución compatible para una sola lectura real.
- Plan propuesto para revisión: usar primero temperatura; no depender del TDS
  ni de integración de potencia. MQTT/TLS sigue como arquitectura seleccionada.
  No se implementó/desplegó el plan. Aplazar comando físico requiere autorización
  docente; recepción tardía y nueva fecha de entrega todavía por acordar.

Fuente: [bitácora de sensores](../Documentos%20PDC/HydroMate_Bitacora_Pruebas_Sensores_Diagnostico_TDS_05-10-2026.docx).

## Reporte en Word — 2026-10-06

- Reporte de seis páginas: [estado del proyecto](../reports/HydroMate_Estado_Actual_2026-10-06.docx).
  Resume avances, evidencia con fecha, aceptación Android, hardware, ahorro,
  nube y próximos pasos. No modifica código, datos ni decisiones técnicas.
- Elaborado con las pruebas registradas del 30/09, 03/10 y 04/10; no se repitieron
  pruebas de backend/Android ni ensayos físicos para elaborar este reporte.

## Ahorro energético y procesos — documentación del 2026-10-04

- Usuario confirma ESP32 con fuente y control de bombas. Dirección D44–D47 en
  [ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md): controlador disponible,
  modem-sleep y frecuencia dinámica por etapas; sin reiniciar cada 5 s ni deep
  sleep durante operación normal. Sueño ligero condicionado a pruebas físicas.
- Propuesta de banco: adquirir cada 5 s, publicar cada 300 s estable, 30 s en
  pruebas con vencimiento y avisos por cambios/fallos. Seguridad independiente;
  tiempos admisibles, calibración y límites físicos todavía pendientes.
- Identificadas 14 mejoras priorizadas de firmware, contrato, red, consultas,
  Android, despliegue y energía total. No implementadas por esta documentación.
  El contrato v1 necesita evolución antes de sensores parciales, eventos o cola
  tardía: no admite hora de adquisición ni magnitudes reales de flotador/BH1750.
- Cálculos y enlaces verificados; 300 s implica 90 % menos mensajes rutinarios
  que 30 s, no 90 % de ahorro eléctrico. Sin medidas de consumo ni pruebas físicas.
- Render + Aiven es candidato para API/BD de prueba, no contratación/despliegue.
  MQTT/bridge y protección de acceso siguen pendientes. Ningún servicio expuesto.
- Evidencia: evidence/energy-review-2026-10-04.json. Respaldo documental:
  .local/backups/energy-docs-2026-10-04. Código y datos conservados; sin Git.

## Android Jardín de cristal 0.6 — incremento del 2026-10-04

- Dirección vigente D43: fondo botánico mucho más claro y paneles verdes
  translúcidos, con hojas visibles detrás del cristal. Cinco pestañas y estilo
  Frutiger Aero/Eco. Cuatro variantes de iconos solo para la barra; Cultivo
  conserva el emblema original. Recarga nueva y pH/TDS diferenciados.
- API, contrato, firmware y lógica de datos conservados. Sin rangos, perfiles ni
  estados físicos inventados. Demo explícita solo debug, nunca fallback.
- Instalado en teléfono 2207117BPG/Android 13 por USB. MainActivity abierta y
  estado de fallo real de consulta capturado. Preferencia de apariencia del
  teléfono cambiada de sistema a Jardín claro por la petición actual; sin
  cambios globales. Respaldo: .local/appearance-before-light-request.xml.
- 26 revisiones nativas de composición con Activity debug aislada: 320/360/412 dp,
  fuentes 1/1.3/2, cinco pantallas, estados, fin de scroll y noche. Sin recortes
  detectados ni objetivos táctiles menores de 48 dp. No son pruebas de interacción
  con red ni varios teléfonos. Capturas en evidence/garden-light-2026-10-04.
  Revisión debug vertical y encendida mientras está visible, sin ajustes globales.
- Debug/release compilan. 17 pruebas JVM correctas, 1 GET opt-in omitido; lint
  0 errores y 3 avisos: target, JSON de tests y orientación de revisión debug.
  Release sin fixtures/Activity de revisión/HTTP. 28 comprobaciones de contraste,
  mínimo calculado 4.639:1.
- Docker daemon no disponible el 04/10. Laravel se inició en 127.0.0.1:8000 y ADB
  reverse se preparó; no se comprobó GET exitoso con PostgreSQL ese día. No se
  borraron datos, recrearon contenedores ni modificaron firewall/credenciales.
- APK: mobile/app/build/outputs/apk/debug/app-debug.apk (0.6.0-garden).
  Evidencia: evidence/android-garden-2026-10-04.json. Diseño, procedencia y aceptación:
  AERO_DESIGN.md, recursos.json y AERO_ACCEPTANCE.md.
- Pendiente: TalkBack/foco, teclado/edición, giro físico final, gestos, lifecycle
  completo y GET real por USB. Android bloquea toques/cambios globales por ADB;
  no se alteraron esos permisos.
- Respaldo: .local/backups/android-crystal-nav-2026-10-04. Las capturas eco,
  crystal, readable y garden oscuro se conservan como históricas. Sin Git; comparación local de
  cambios, sin commit/push. Conviene inicializar Git antes del próximo incremento.

## Base comprobada e historial

Prioridad vigente: PostgreSQL → Laravel API → Android mínimo → ESP32 físico.
Wokwi/Blade reemplazados; no iniciar perfiles/autenticación/actuadores por estética.

- 30/09: API Laravel/PostgreSQL, identidad por torre, validación v1 y UNIQUE de
  device_id/sequence probados. Datos sintéticos existentes conservados:
  test-api-0865fd385681. 17 pruebas backend/104 assertions en SQLite aislada.
- Volumen PostgreSQL anónimo confirmado en su etapa; reutilizarlo si se recrea
  explícitamente el contenedor. No se probó recreación ni se autoriza borrar datos.
- 03/10: Android 0.2 y luego 0.3 Aero. En esa fecha, 18 pruebas JVM con GET real
  correctas, sin teléfono para QA visual. Es evidencia histórica, no nueva.
  Dirección visual 0.3 reemplazada por D36/D37; comportamiento D33/D34 vigente.
- Evidencias anteriores: android-aero-2026-10-03.json, android-ux-2026-10-03.json,
  backend-step1-http.json y postgres-step1.json. Estado previo archivado en
  evidence/STATUS-2026-10-03.md; decisiones no borradas.

## Siguiente paso

Completar las pruebas manuales Android pendientes y comprobar servicios existentes.
Antes de sensores/firmware, confirmar hardware y plazos de seguridad, y diseñar la
evolución compatible de TELEMETRY_CONTRACT descrita en ENERGY_OPTIMIZATION.
Implementar/medir el ahorro por etapas; no afirmar sensores calibrados, comandos
físicos ni consumo reducido sin prueba. Si se prepara nube, resolver acceso y
MQTT/bridge sin asumir que un web service gratuito cubre el sistema completo.

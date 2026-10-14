# Verificación de la prueba de viabilidad

Actualización: [integración vigente](../../docs/INTEGRATION.md). v3 implementada;
25 pruebas backend, 27 Android, tres bridge, smoke v1 y diez MQTT TLS simulados
pasan localmente. Tras corregir regla LAN, diez adquisiciones físicas nuevas
1501–1510 verificadas contra API, Inicio real observado y tiempo aproximado7.57s.
Fallo anterior, pendiente recuperada, capturas y video12s conservados.
Historial real también observado: gráfica pH, lista20 registros y comparación
de fila visible1701 con API; captura/verificación en pruebas/.
TDS actual null/no disponible; el fijo
simulado de las pruebas del 7/10 es histórico. Nube todavía sin verificar.
La matriz siguiente conserva evidencias previas y pendientes del taller.

Revisión posterior al despliegue comunicado: [revisión de cierre](revision-cierre-2026-10-14.md).
Producción ya incorporada al remoto main; servidor todavía sin URL verificada.
ESP32/teléfono detectados, Android sigue en http://127.0.0.1:8000. Las evidencias
de nube pendientes no se consideran completadas por la incorporación del código.

Corte: 14 de octubre de 2026. El flujo físico local tiene evidencia del 7 de
octubre. La entrega completa todavía requiere backend en nube, repetición del
recorrido físico contra ese backend y video conjunto. No se cuentan lecturas
sintéticas como mediciones reales. El TDS es simulado y aparece identificado.

Las rutas de la tabla son relativas a la raíz del repositorio. «Local probado»
se refiere a evidencia histórica observada; no significa nueva adquisición hoy.
Hoy se recuperó Docker, arrancó PostgreSQL/API y reconsultaron 90 filas históricas
de hydromate-01, conservando secuencias de pruebas físicas previas. Evidencia nueva:
`pruebas/persistencia-local-2026-10-14.json` y
`pruebas/esquema-postgresql-2026-10-14.json`. Backend: 19 tests/118 assertions pasan
en SQLite aislada. No se observó nueva medición física ni acceso VPS.

## Flujo mínimo

Sensor físico → ESP32 → Wi-Fi/MQTT → Mosquitto → integrador Python → API Laravel
→ PostgreSQL → API GET → Android. Actualmente el servidor está en la PC y Android
lo consulta por USB. El VPS Ubuntu prestado aloja otro proyecto; su despliegue de
HydroMate no está comprobado. Docker local no demuestra alojamiento en nube.

## Sistema embebido

| Requisito | Cómo y dónde se cumple | Estado / cierre necesario |
|---|---|---|
| Sensor o entrada física real | `embedded/HydroMateTelemetry/HydroMateTelemetry.ino`, función `sample()`: DS18B20 GPIO4, BH1750 I2C21/22, pH por ADS1115 A0, flotador GPIO27. `pruebas/esp32-fisico-24ghz-2026-10-07.json` compara muestras serie y API. | Local probado; repetir en nube. |
| Procesamiento básico | `sample()` promedia diez conversiones de pH, aplica `pH=-5.579×V+14.066`, redondea, convierte flotador a booleano y rechaza sensores inválidos. | Implementado y ejecutado localmente; no acredita nueva calibración. |
| Internet | `setup()/loop()`: Wi-Fi con reconexión y MQTT. Se observó Wi-Fi 2.4 GHz y broker LAN. | LAN probada; falta publicación por Internet a VPS con TLS. |
| Enviar un tipo de dato | JSON v2 al tópico `hydromate/hydromate-01/telemetry`; `scripts/mqtt_bridge.py` traduce a POST de API. | Local probado. MQTT es la operación equivalente admitida. |
| Identificar mediciones | `device_id`, `sequence` persistente por rangos NVS; `created_at` UTC asignado por Laravel. | Local probado; secuencia puede tener saltos por reinicio, sin perder identidad. |

## Backend

| Requisito | Cómo y dónde se cumple | Estado / cierre necesario |
|---|---|---|
| Despliegue temporal en nube | VPS OVHcloud Ubuntu prestado, compartido; despliegue comunicado tentativamente. | Sin verificar: obtener URL pública y evidencia propia, sin solicitar secretos ni acceder por SSH. |
| Recibir dato del embebido | `scripts/mqtt_bridge.py` recibe MQTT, guarda bandeja privada SQLite y llama `POST /api/measurements`. `hydromate-backend/routes/api.php`. | Local probado; bandeja no sustituye BD principal. |
| Validar campos indispensables | `hydromate-backend/app/Http/Requests/StoreMeasurementRequest.php`: identidad, secuencia, versión, variables, rangos, booleano y origen. | Verificado en tests y ensayos locales. |
| Registrar en BD | `MeasurementController::store()` y `app/Models/Measurement.php`, PostgreSQL `measurements`. | Local probado, índice único por dispositivo/secuencia. |
| Consulta frontend | `GET /api/measurements?device_id=hydromate-01&limit=20` y `/api/measurements/latest?device_id=hydromate-01`. | Local probado; Android debe cambiar a URL HTTPS de VPS. |
| Respuesta comprensible válida | HTTP 201, `status:ok`, «Medicion registrada correctamente» y registro. | Local probado. |
| Respuesta incorrecta | HTTP 422 con errores por campo; 409 «Medicion duplicada»; latest sin datos 404 «No hay mediciones». | Local probado; repetir 422 y comprobar que no hay INSERT en nube. |

## Base de datos

| Requisito | Cómo y dónde se cumple | Estado / cierre necesario |
|---|---|---|
| Una tabla | `measurements`, migración `2026_09_23_205121_create_measurements_table.php` y evolución `2026_10_07_000001_add_physical_telemetry_to_measurements.php`. | Local aplicada; esquema exportado en `pruebas/esquema-postgresql-2026-10-07.json`. |
| Identificador | `id` y UNIQUE `(device_id, sequence)`. | Local probado. |
| Variable y valor | `temperature_c`, `light_lux`, `water_present`, `ph`, `tds_ppm` y `sources`. | Local probado; modelo ancho válido para PoC, sin exigir tabla variable/valor aparte. |
| Unidad cuando corresponde | °C, lux y ppm definidos por nombres y `docs/TELEMETRY_CONTRACT.md`; pH y flotador sin unidad. | Contrato y Android conservan unidades. |
| Fecha y hora | `created_at/updated_at` UTC del servidor; Android presenta zona local. | Local probado; es recepción, no adquisición. |
| Diez registros reales | Diez entregas verificadas: 101 y 401–409, cuatro variables reales y TDS simulado por fila. | Evidencia local; 101 recuperada y nueve adquisiciones nuevas. Obtener diez nuevas en nube. |
| Consulta | SQL en `talleres/taller-05/pruebas/consulta.md`; GET filtrado usado por Android. | Local probado; conservar consulta y resultado de VPS. |

## Frontend

| Requisito | Cómo y dónde se cumple | Estado / cierre necesario |
|---|---|---|
| Una pantalla funcional | `mobile/`, `MainActivity.kt`, `ui/dashboard/DashboardScreen.kt`. APK instalada en ensayo previo. | Local probado; teléfono detectado en revisión posterior, configurado todavía con URL local. |
| Comunicación real backend | `Telemetry.kt`, `TelemetryRepository.load()` consulta HTTP; `MainActivity` coordina carga. | Local probado por USB, pendiente HTTPS VPS. |
| Último dato y fecha | Inicio usa última fila ordenada por recepción; fecha «Recibido». Captura `pruebas/android-sensores-reales-2026-10-07.png`. | Local probado. |
| Lista o gráfica almacenada | `ui/history/HistoryScreen.kt`: registros y gráfica; `pruebas/android-historial-real-2026-10-07.png`. | Local probado. |
| Carga, ausencia y error | `ui/ReadingState.kt`: Loading/Empty/Failed; Inicio/Historial los renderizan y permiten reintentar. | Implementado; evidencias locales y pruebas de software. Repetir con nube. |
| App funcional, sin sustitución estática | Salir de Demostración; conexión real, torre `hydromate-01`, actualizar Inicio e Historial y variar luz/flotador. | Demo debug no cuenta; capturas acompañan ejecución, no la sustituyen. |

## Actuadores y pruebas

| Requisito | Evidencia / procedimiento | Estado / cierre necesario |
|---|---|---|
| Comando básico a salida o aplazamiento | Firmware de telemetría sin actuadores y Control Android marcado pendiente. Usuario comunica aplazamiento autorizado el 14/10. | Aplazado para alfa; adjuntar confirmación docente y razón técnica: validar salidas e interbloqueos locales antes del control remoto. ACK de telemetría no es comando de actuador. |
| Diez transmisiones consecutivas | `pruebas/esp32-fisico-24ghz-2026-10-07.json`: diez entregas con comparación campo por campo, una recuperada y nueve nuevas. | Parcial frente a interpretación estricta; repetir diez muestras nuevas consecutivas en nube, sin reinicio entre ellas. |
| Éxitos y fallos | Captura serie registra SAMPLE/SEND/STORED/MQTT_FAIL; ensayos fallidos conservados en `pruebas/esp32-fisico-2026-10-07.json`. | Local probado; contar intentos por secuencia, sin tratar publish aceptado como INSERT. |
| Tiempo sensor–frontend | `pruebas/latencia-android-reintento-2026-10-07.json`: 8241.77 ms adquisición terminada→interfaz verificada, una muestra, incluye arranque/ADB. | Aproximación local; repetir contra nube, no presentarla como latencia pura ni tiempo de adquisición completo. |
| Dato incorrecto o pérdida temporal | pH=50 rechazado en ensayo sintético; corte broker físico en `pruebas/esp32-reconexion-2026-10-07.json`, 901 conservada y 901/902 comprobadas. | Local probado; repetir prueba controlada solo sobre servicios HydroMate de VPS. |
| Problemas y correcciones | `errores-resultados/bitacora-2026-10-07.md`: alimentación/conexión pH, Wi-Fi 5 GHz→2.4 GHz, Docker y extracción de UI. | Documentado; añadir incidentes actuales y de nube. |

## Evidencias y planeación

| Entregable | Ubicación / contenido | Estado / cierre necesario |
|---|---|---|
| Código fuente inicial | `embedded/`, `scripts/mqtt_bridge.py`, `hydromate-backend/`, `mobile/`. | Existe en Git. |
| Diagrama conexión y flujo implementado | `diagramas/conexiones.md`, `diagramas/flujo-local.mmd`, `diagramas/README.md`. | Local documentado; diagrama nube se produce al validar despliegue real. |
| Video breve funcionando | `pruebas/android-consulta-local-2026-10-07.mp4`, 10.06 s, Android consultando API local. | Parcial: falta video que muestre montaje y flujo nube; puede grabarse cámara + pantalla. |
| Backend desplegado | URL HTTPS, verificación de servicio y petición de extremo a extremo. | Pendiente, no sustituir por pantalla Docker local. |
| Estructura BD | Migraciones y `pruebas/esquema-postgresql-2026-10-07.json`. | Existe; exportar también esquema aplicado en VPS. |
| Frontend con datos reales | Capturas Inicio/Historial y video local citados. | Existe local; demostrar mismos registros recibidos en VPS. |
| Git con README | Repositorio local y README raíz; remoto `komvo/HydroMate`, producción67da210 incorporada a main por PR1. | Existe; nuevas revisiones/planeación local aún no publicadas. |
| Cronograma semanas restantes | `plan-accion.md`, historial y semanas hasta 02/12/2026. | Actualizado según fuentes; trabajo futuro marcado planeado. |
| Presupuesto preliminar | `plan-accion.md`: costos históricos separados, VPS prestado $0 y pendientes por cotizar. | Existe preliminar; no equivale a conciliación final de compras. |
| Cinco riesgos con acciones | `plan-accion.md`: diez riesgos con prevención y contingencia. | Cumple documentalmente. |

## Demostración para cerrar el taller

1. Iniciar servicios propios en VPS; comprobar TLS, HTTPS y protección de ingreso.
2. Configurar firmware privado hacia broker VPS y Android hacia API HTTPS.
3. Capturar diez muestras **nuevas** del ESP32; conservar intentos y confirmación de
   cada secuencia. Variar luz/flotador durante el ensayo para evidenciar entrada física.
4. Comprobar esas mismas secuencias/valores con API y consulta SQL; contar diez
   filas con variables reales. TDS permanece simulado y visible como tal.
5. Abrir Inicio/Historial en teléfono; mostrar fecha y valores coincidentes;
   medir aproximadamente SAMPLE→dato visible, indicando método y sobrecarga.
6. Probar dato inválido en identidad de pruebas y/o pérdida controlada del enlace
   propio, registrar fallo/reintento y restablecimiento. No detener servicios ajenos.
7. Grabar video conjunto, guardar evidencia HTTPS/esquema/consulta, anexar
   autorización docente de actuador y cerrar reporte técnico.

No se exige completar autenticación de usuarios, perfiles, todas las pantallas,
calibración definitiva o pruebas unitarias formales para este taller. Proteger
el ingreso público de la PoC sigue siendo necesario antes de exponerla a Internet.

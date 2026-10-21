# Incremento vigente: API pública — 2026-10-14

HTTPS9443 permite consultas GET/HEAD y la solicitud limitada de adquisición
descrita abajo. POST /api/measurements permanece interno para el bridge.
Guía [PUBLIC_ACCESS](PUBLIC_ACCESS.md). La referencia histórica se conserva abajo.

## Solicitar una medición nueva — incremento21/10/2026

- POST /api/devices/{device_id}/measurement-requests con cuerpo {}:202 con id UUID,
  state=pending y expires_at. Solo torres ya registradas, máximo12 solicitudes/min;
  clics concurrentes reutilizan una solicitud pendiente. No acepta acciones ni
  parámetros de actuadores. 404 torre desconocida,422 cuerpo incorrecto,429 límite.
- GET /api/measurement-requests/{UUID}: pending, stored o expired; stored incluye
  la measurement correlacionada. Nunca sustituye una respuesta pendiente por
  una lectura anterior. Plazo30s; metadata efímera90s en caché de archivos existente.
- GET /api/internal/measurement-requests: exclusivo de la red privada; el bridge
  consulta solicitudes y las publica por MQTT. No expuesto por Nginx público.

Este incremento conserva lecturas públicas y limita la nueva escritura a pedir
adquisiciones; no incorpora autenticación completa ni comandos genéricos.
Android consulta automáticamente lecturas en primer plano cada2s. Su botón de
refresco crea solicitud, espera medición correlacionada y luego consulta historial.

## Actualización de integración — 14/10/2026

Vigente [contrato v3](TELEMETRY_CONTRACT.md): seis variables con origen explícito,
valores null para ausencia/invalidez, EC independiente y hora de adquisición UTC.
v1/v2 siguen aceptadas. `real_only=1` filtra simulaciones en historial/última/estado;
`sequence=N` permite recuperar una fila exacta por identidad.
`GET /api/devices/{device_id}/status` devuelve no_data/recent/stale y fechas;
no representa una prueba de conexión MQTT. Historial incluye cabecera
`X-HydroMate-Freshness-Seconds` (120 por defecto), usada por Android para
evaluar antigüedad sin ocultar una adquisición vieja recibida recientemente.
Todos los sensores se consultan en una misma fila; no se requieren endpoints
separados por temperatura/pH/nivel/luz/TDS/EC. Detalles y pruebas reproducibles:
[INTEGRATION](INTEGRATION.md).

# API de telemetría para el primer cliente Android

Base de desarrollo: http://127.0.0.1:8000. JSON; enviar Accept: application/json.
Android usará posteriormente la dirección LAN de la PC, no su propio localhost.
Sin autenticación por ahora: no exponer a Internet. Filtro no equivale a autorización.

## Registrar
Actualización 07/10: también acepta v2 físico en los mismos endpoints. Ver
TELEMETRY_CONTRACT.md: message_version=2 entero JSON, lux, water_present booleano
y sources por variable. Campos antiguos se conservan para v1 y quedan null en
filas v2. No mezclar porcentajes y lux en el mismo POST.

POST /api/measurements con Content-Type: application/json:
```json
{"device_id":"hydromate-01","sequence":1,"sample_number":1,"reason":["startup"],"temperature_c":24.3,"light_pct":65.2,"light_state":"MEDIA","water_level_pct":82.4,"water_level_state":"LLENO","ph":6.2,"tds_ppm":650}
```
201: objeto {status, message, measurement}. 409: medición duplicada, sin modificar
la original. 422: {message, errors}, indicando campos inválidos.
No reutilizar device_id + sequence para una lectura distinta.

## Consultar
- GET /api/measurements?device_id=hydromate-01&limit=20: array JSON, más reciente
  primero; [] si no hay filas. Limit 1–100, predeterminado 20; inválido devuelve 422.
- GET /api/measurements/latest?device_id=hydromate-01: objeto de medición;
  404 con {status:"error",message:"No hay mediciones"} si aún no existe.
Sin filtro se consultan todas las torres: Android debe enviar device_id.
Las mediciones incluyen id, campos del POST y created_at/updated_at del servidor.
Orden de consulta: created_at e id descendentes; no depende del valor sequence.
Los campos físicos obligatorios conservan rangos de ARCHITECTURE, aún de prototipo.

## Datos de prueba actuales
Dispositivo test-api-0865fd385681; 11 lecturas sintéticas. No son sensores reales.
No usar este dispositivo como identidad del ESP32 físico.

## Contrato del productor
Ver TELEMETRY_CONTRACT.md para unidades, reintentos, secuencia persistente, sensores
ausentes y tiempo de recepción. Ejemplos ejecutables: tests/Fixtures/telemetry
dentro del backend. No se añadieron campos ni cambiaron endpoints en el paso 2.

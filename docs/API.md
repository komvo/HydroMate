# API de telemetría para el primer cliente Android

Base de desarrollo: http://127.0.0.1:8000. JSON; enviar Accept: application/json.
Android usará posteriormente la dirección LAN de la PC, no su propio localhost.
Sin autenticación por ahora: no exponer a Internet. Filtro no equivale a autorización.

## Registrar
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

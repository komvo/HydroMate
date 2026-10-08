# Consultar registros de la PoC

Android utiliza API, no SQL directo:

```text
GET /api/measurements?device_id=hydromate-01&limit=20
GET /api/measurements/latest?device_id=hydromate-01
```

Consulta SQL equivalente para revisión técnica con acceso autorizado a PostgreSQL:

```sql
SELECT id, device_id, sequence, temperature_c, light_lux, water_present,
       ph, tds_ppm, sources, created_at
FROM measurements
WHERE device_id = 'hydromate-01'
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

La tabla tiene id y una pareja única device_id/sequence. Las unidades están en
los nombres/contrato: °C, lux, pH, ppm; flotador booleano sin unidad. created_at
es fecha/hora de recepción UTC. sources diferencia real/simulated por variable.
Schema JSON adjunto se exporta por consulta de solo lectura, sin filas ni secretos.
Filas `test-mqtt-*` de ensayos PC son sintéticas; no cuentan como diez reales.

# Telemetría v2 física — 2026-10-07

v2 implementada en Laravel/PostgreSQL/Android e integrador local. Firmware
preparado; ejecución física según STATUS. Contrato v1 preservado en
[TELEMETRY_CONTRACT_V1.md](TELEMETRY_CONTRACT_V1.md) y aceptado sin `message_version`.
Los endpoints e índice único `(device_id, sequence)` no cambian.

## Mensaje v2

```json
{"message_version":2,"device_id":"hydromate-01","sequence":1,"reason":["periodic_poc"],"temperature_c":24.3,"light_lux":450.5,"water_present":true,"ph":6.2,"tds_ppm":650,"sources":{"temperature_c":"real","light_lux":"real","water_present":"real","ph":"real","tds_ppm":"simulated"}}
```

Este ejemplo describe el formato; sus números no acreditan mediciones físicas.

| Campo | Validación / significado |
|---|---|
| message_version | Entero JSON 2 obligatorio para v2; no cadena "2" |
| device_id | Identidad estable, string no vacío de hasta 64; MQTT restringe a letras/dígitos/_/- |
| sequence | Entero positivo hasta bigint; misma adquisición pendiente conserva objeto y secuencia |
| reason / sample_number | Opcionales; límites heredados v1 |
| temperature_c | Número 0–50 °C |
| light_lux | Número 0–100 000 lux; no PAR ni porcentaje |
| water_present | Booleano JSON; false es nivel bajo válido, no dato faltante |
| ph | Número 0–14, sin unidad |
| tds_ppm | Número 0–1000 ppm; no EC |
| sources | Cinco claves de sensores exactas; cada una `real` o `simulated` |

v2 exige los cinco valores y su origen. Sensor inválido/null bloquea registro;
firmware no sustituye por cero ni publica una lectura antigua como nueva.
No enviar porcentajes/estados v1 junto a v2. Campos antiguos quedan null en BD
para v2; v1 conserva sus valores y tiene campos nuevos null.
Estos límites son del prototipo, no objetivos de cultivo ni prueba de autenticidad.
El origen lo declara el productor; la API no comprueba físicamente el sensor.

## MQTT y confirmación de persistencia

- Telemetría: `hydromate/{device_id}/telemetry`, JSON UTF-8, no retained.
- ACK: `hydromate/{device_id}/ack`, `{"sequence":1,"status":"stored"}`.
- Estados ACK: stored, rejected, conflict. Solo stored permite retirar pendiente.
- PubSubClient publica QoS 0 y reintenta idéntico objeto cada 5 s; ACK de aplicación
  confirma persistencia y es distinto del ACK de transporte MQTT.
- Bridge Paho suscribe QoS 1, confirma transporte después de guardar bandeja
  SQLite local y procesa POST sin acceder directamente a PostgreSQL.
- API 201 → stored; 422/otros 4xx → rejected; timeout/conexión/5xx → pendiente,
  reintentos con espera creciente hasta 30 s. No renumera ni altera el payload.
- 409 → stored solo si consulta y verifica igualdad de todos los campos enviados.
  Búsqueda limitada a 100 recepciones; si no prueba igualdad marca conflict para
  revisión. Mismo identificador con otro contenido no sobrescribe la bandeja.
- Firmware conserva una muestra pendiente en NVS y reserva bloques de 100 antes
  de usar secuencias. Reiniciar salta el bloque; huecos permitidos.
- Si se borra NVS, reconciliar identidad/secuencia antes de reutilizar torre.
- Bandeja bridge persiste tras reinicio. Límites/retención por espacio y pruebas
  de corte eléctrico/reinicio físico todavía pendientes.

## Tiempo, cadencia y etiquetas

Laravel asigna created_at/updated_at en UTC: recepción, no adquisición. Android
muestra fecha local, última recepción e historial. No se afirma "en vivo".
PoC toma una muestra cada 30 s cuando no hay pendiente; con red caída conserva
una sola lectura, no un historial completo durante el corte. Entrega tardía puede
mostrar una muestra vieja con recepción nueva: limitación explícita. Resolver
hora de adquisición/antigüedad de cola antes del controlador final.

TDS fijo 650 ppm simulado, identificado en Android. Ensayos PC usan `test-*`,
synthetic_test y TODOS los sources simulated. No son filas de sensores físicos.

## Red de banco y nube

Banco: API 127.0.0.1:8000; teléfono por adb reverse; broker autenticado 1884
en loopback e IP Wi-Fi. MQTT LAN sin TLS es excepción acotada de banco. Mosquitto
anterior 1883 conservado. BD local no cambia exposición previa.
Nube pendiente: HTTPS, MQTT/TLS y ACL por torre, API protegida, credenciales/datos
separados del compañero. Firmware incluye TLS con CA, sin fallback inseguro.

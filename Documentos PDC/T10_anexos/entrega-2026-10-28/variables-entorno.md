# Variables de configuración

Nombres de .env.example raíz; valores y reglas no sensibles en la plantilla y docs/PUBLIC_ACCESS.md. El env real permanece en /etc/hydromate/.env y no se copia al teléfono ni a Git.

- `HYDROMATE_APP_KEY`
- `HYDROMATE_POSTGRES_PASSWORD`
- `HYDROMATE_DB_PASSWORD`
- `HYDROMATE_DB_DATABASE`
- `HYDROMATE_DB_USERNAME`
- `HYDROMATE_APP_URL`
- `HYDROMATE_IMAGE_TAG`
- `HYDROMATE_HTTPS_SECRETS_DIR`
- `HYDROMATE_HTTPS_BIND_ADDRESS`
- `HYDROMATE_MQTT_SECRETS_DIR`
- `HYDROMATE_MQTT_BRIDGE_PASSWORD`
- `HYDROMATE_MQTT_BIND_ADDRESS`

Firmware privado: WIFI_SSID, WIFI_PASSWORD, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_TLS, MQTT_ROOT_CA, DEVICE_ID. Usar el secrets.example.h como referencia, sin sobrescribir secrets.h vigente.
Android: HYDROMATE_APP_URL, HTTPS público9443 sin /api; desarrollo separado.
Backend: TELEMETRY_FRESHNESS_SECONDS en su plantilla/configuración; default120s. No rotar contraseñas o APP_KEY para completar una plantilla.

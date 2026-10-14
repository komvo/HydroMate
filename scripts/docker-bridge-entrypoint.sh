#!/bin/sh
set -eu
if [ -z "${MQTT_PASSWORD:-}" ]; then
    echo 'Provide the HydroMate bridge MQTT password at runtime.' >&2
    exit 1
fi
exec "$@"

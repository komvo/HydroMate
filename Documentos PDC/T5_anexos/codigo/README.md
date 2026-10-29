# Código utilizado

Base actual: [sketch de sensores](../../../Documentos%20PDC/tests/PruebaSensores1.ino),
[backend](../../../hydromate-backend/) y [Android](../../../mobile/).
El primer commit conserva esta base; registrar el commit exacto que se pruebe
al cerrar el taller. Incremento local nuevo:

- [Firmware MQTT v2](../../../embedded/HydroMateTelemetry/HydroMateTelemetry.ino).
- [Guía de firmware](../../../embedded/README.md), con versiones y comandos.
- [Integrador MQTT a HTTP](../../../scripts/mqtt_bridge.py).
- [Ensayo MQTT sintético](../../../scripts/test_mqtt_flow.py).
- [Captura serial y comprobación API](../../../scripts/capture_sensor_flow.py).
- [Contrato v2 compatible](../../../docs/TELEMETRY_CONTRACT.md).

El sketch original no se modificó. Binarios de firmware con secretos, secrets.h,
.env, bandeja, contraseñas y backups permanecen fuera de GitHub.

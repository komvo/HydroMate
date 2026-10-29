# HydroMate

Monitoreo y diseño de control local para hidroponía vertical. ESP32 con sensores
reales → MQTT/TLS → Mosquitto/bridge → Laravel → PostgreSQL → Android por HTTPS.
Repositorio público: https://github.com/komvo/HydroMate.

## Documentación

[Estado actual](docs/STATUS.md)

- Implementado: temperatura, pH, luz, flotador y TDS real; telemetría v3,
  reintentos/ACK, historial y adquisición solicitada desde Android.
- Diseñado, sin implementación completa: usuarios/Sanctum, avisos/FCM,
  aprovisionamiento BLE, perfiles y control seguro de actuadores.
- Producción: `https://hydromate-kevin.duckdns.org:9443`; MQTT TLS
  `hydromate-kevin.duckdns.org:8884`; dispositivo `hydromate-01`.

## Mapa de trabajo

| Ruta | Uso |
|---|---|
| hydromate-backend/ | Laravel, validación, migraciones y pruebas |
| embedded/HydroMateTelemetry/ | Firmware físico y ejemplo de configuración privada |
| mobile/ | Android Kotlin nativo, Inicio/Historial y conexión por entorno |
| scripts/ | Bridge MQTT y herramientas de pruebas/captura |
| deployment/ y compose.production.yml | Empaquetado rootless y despliegue HydroMate |
| Documentos PDC/ | Entregas de talleres |


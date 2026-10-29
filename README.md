# HydroMate

Monitoreo y diseño de control local para hidroponía vertical. ESP32 con sensores
reales → MQTT/TLS → Mosquitto/bridge → Laravel → PostgreSQL → Android por HTTPS.
Repositorio público: https://github.com/komvo/HydroMate.

## Documentación

[Estado actual](docs/STATUS.md) y [contexto del proyecto](docs/PROJECT_CONTEXT.md).
Las últimas pruebas físicas documentadas son del 21/10/2026; no garantizan que el
servidor esté disponible en este momento.

- Implementado: temperatura, pH, luz, flotador y TDS real; telemetría v3,
  reintentos/ACK, historial y adquisición solicitada desde Android.
- Diseñado, sin implementación completa: usuarios/Sanctum, avisos/FCM,
  aprovisionamiento BLE, perfiles y control seguro de actuadores.
- Producción: `https://hydromate-kevin.duckdns.org:9443`; MQTT TLS
  `hydromate-kevin.duckdns.org:8884`; dispositivo `hydromate-01`.
- Talleres5/8 y presupuesto actual en `Documentos PDC/`; fuentes y evidencias
  en `talleres/taller-05/entrega-2026-10-21/`. Entrega final del proyecto: 2/12/2026.

## Mapa de trabajo

| Ruta | Uso |
|---|---|
| hydromate-backend/ | Laravel, validación, migraciones y pruebas |
| embedded/HydroMateTelemetry/ | Firmware físico y ejemplo de configuración privada |
| mobile/ | Android Kotlin nativo, Inicio/Historial y conexión por entorno |
| scripts/ | Bridge MQTT y herramientas de pruebas/captura |
| deployment/ y compose.production.yml | Empaquetado rootless y despliegue HydroMate |
| docs/ | Contratos, decisiones, operación y evidencia fechada |
| Documentos PDC/ | Entregas académicas vigentes y referencias seleccionadas |
| reports/ | Informes; identificar su fecha antes de tratarlos como actuales |

## Cambiar comprobar y publicar

[SETUP](docs/SETUP.md): desarrollo y selección de pruebas.
[REPOSITORY](docs/REPOSITORY.md): ramas, revisión, commit y push.
[ARCHITECTURE](docs/ARCHITECTURE.md), [API](docs/API.md) y
[contrato](docs/TELEMETRY_CONTRACT.md): interfaces que deben conservarse.
[PUBLIC_ACCESS](docs/PUBLIC_ACCESS.md) y [PRODUCTION](docs/PRODUCTION.md):
operación del servidor; las credenciales nunca se versionan.

No publicar secretos, `.local/`, respaldos operativos ni datos ajenos. No borrar
volúmenes ni operar recursos `chitiito-*`. Subir una rama no autoriza merge ni
confirma despliegue. Producción nunca sustituye fallos por datos demo.

[THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) y [recursos](docs/recursos.json)
documentan procedencia; no se atribuye una licencia global a todos los materiales.

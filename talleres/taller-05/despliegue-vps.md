# Despliegue temporal de HydroMate en VPS compartida

La preparación de producción se entrega al ejecutor automático de main, sin
acceso SSH ni solicitud de secretos en esta tarea. Seguir la
[guía de producción](../../docs/PRODUCTION.md) y compose.production.yml,
siempre con el proyecto explícito `-p hydromate`.

API en 127.0.0.1:8081, PostgreSQL interno y MQTT TLS opcional en8884.
Todos los recursos y configuraciones chitiito-* son intocables. El administrador
provisiona .env/certificados solo en VPS y el endpoint HTTPS independiente.
El empaquetado está probado localmente; no acredita despliegue ni ensayo físico en nube.

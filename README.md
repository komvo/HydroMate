# HydroMate

Prototipo de monitoreo y control local para hidroponía vertical.
Repositorio: [komvo/HydroMate](https://github.com/komvo/HydroMate).
Entrega final: 2 de diciembre de 2026.

## Integración actual — 14/10/2026

ESP32 → MQTT/TLS → Mosquitto → bridge → Laravel → PostgreSQL → Android HTTPS.
Código v3 implementado con temperatura, luz, flotador y pH; TDS opcional y EC
independiente aceptan ausencia sin valores inventados. Android tiene perfiles
separados de desarrollo y producción, sin datos demo en producción.

Backend y Android pasan sus pruebas. Pipeline MQTT TLS probado **localmente**
con diez mensajes simulados, duplicado, conflicto, dato inválido y GET.
Firmware v3 compilado/cargado; diez adquisiciones nuevas1501–1510 verificadas
localmente contra API. Android muestra lectura real, fecha y TDS no disponible;
capturas/video conservados. Tiempo aproximado7.57s hasta pantalla, con arranque
de app/ADB; no es latencia de nube. [Resultados](talleres/taller-05/pruebas/README.md).
Las pruebas del 7/10 quedan como antecedentes, con TDS simulado identificado.

Producción Docker preparada y aislada: API loopback8081, PostgreSQL interno y
MQTT TLS8884. VPS Ubuntu OVHcloud prestada ($0 según usuario), compartida;
esta tarea no accede al servidor ni toca recursos `chitiito-*`.
Faltan dirección pública HTTPS, MQTT TLS accesible y evidencia física desplegada.
`127.0.0.1:8081` de la VPS no es la dirección pública para Android.

## Código y documentación

| Ruta | Contenido |
|---|---|
| `embedded/` | Firmware ESP32 y plantilla privada sin secretos |
| `hydromate-backend/` | API Laravel, migraciones y pruebas |
| `mobile/` | Android nativo y pruebas; no se ejecuta en VPS |
| `scripts/` | Integrador MQTT, arranque y validación |
| `deployment/` | Configuración aislada de PostgreSQL/Mosquitto y hook de despliegue |
| `docs/` | Guías, arquitectura, contratos y evidencia técnica |
| `Documentos PDC/` | Originales académicos y sketch histórico de sensores |
| `talleres/` | Índice de originales y material único de Taller5 |
| `reports/` | Informes del proyecto |

Empezar por [integración ESP32–Android](docs/INTEGRATION.md) y
[documentación técnica](docs/README.md). Ver [API](docs/API.md),
[contrato de telemetría](docs/TELEMETRY_CONTRACT.md),
[producción](docs/PRODUCTION.md) y [Android](mobile/README.md).

Último acceso preparado: [HTTPS público8443 y MQTT TLS8884](docs/PUBLIC_ACCESS.md),
con variable URL única HYDROMATE_APP_URL, certificados propios y validación final.
Pruebas HTTPS locales/Kotlin pasan; dominio y confirmación desde Internet pendientes.

## Taller5

[Índice técnico](talleres/taller-05/README.md),
[matriz de cumplimiento](talleres/taller-05/cumplimiento-2026-10-14.md),
[cronograma, presupuesto y riesgos](talleres/taller-05/plan-accion.md).
Pendiente la demostración física en nube, diez adquisiciones, Android remoto,
tiempo/fallo y video conjunto. Actuador aplazado según comunicación del usuario;
anexar constancia docente. No presentar simulaciones como mediciones físicas.

Secretos/configuración privada fuera de Git; originales y evidencia histórica
se conservan. Notas de continuidad separadas de entregables técnicos.
Ver [política del repositorio](docs/REPOSITORY.md) y [avisos de recursos](THIRD_PARTY_NOTICES).

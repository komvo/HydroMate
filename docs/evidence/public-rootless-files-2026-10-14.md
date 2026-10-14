# Archivos del incremento público/rootless reconciliado

Diff neto contra origin/main. Únicamente configuración pública, firmware,
Android, backend/bridge, validación y documentación técnica necesaria.
Sin eliminaciones ni renombrados; talleres/PDFs/evidencias existentes y rutas
de contexto originales se conservan. A=añadido, M=modificado.

```text
M	.env.example
M	README.md
M	compose.production.yml
M	deployment/deploy.sh
A	deployment/https/default.conf
A	deployment/prepare-rootless-secrets.sh
A	deployment/reload-certificates.sh
A	deployment/require-rootless.sh
M	docs/API.md
M	docs/ARCHITECTURE.md
M	docs/DECISIONS.md
A	docs/INTEGRATION.md
M	docs/PRODUCTION.md
A	docs/PUBLIC_ACCESS.md
M	docs/SETUP.md
M	docs/STATUS.md
M	docs/TELEMETRY_CONTRACT.md
A	docs/evidence/public-access-local-2026-10-14.json
A	docs/evidence/public-rootless-files-2026-10-14.md
A	docs/evidence/public-rootless-readiness-2026-10-14.json
M	embedded/HydroMateTelemetry/HydroMateTelemetry.ino
M	embedded/HydroMateTelemetry/secrets.example.h
A	embedded/HydroMateTelemetry/sensor_config.h
M	embedded/README.md
M	hydromate-backend/app/Http/Controllers/Api/MeasurementController.php
M	hydromate-backend/app/Http/Requests/StoreMeasurementRequest.php
M	hydromate-backend/app/Models/Measurement.php
A	hydromate-backend/config/telemetry.php
A	hydromate-backend/database/migrations/2026_10_14_000001_add_partial_telemetry_v3.php
M	hydromate-backend/routes/api.php
A	hydromate-backend/tests/Feature/PartialTelemetryTest.php
M	mobile/README.md
M	mobile/app/build.gradle.kts
A	mobile/app/src/main/java/com/hydromate/mobile/ConnectionEnvironment.kt
M	mobile/app/src/main/java/com/hydromate/mobile/ConnectionStore.kt
M	mobile/app/src/main/java/com/hydromate/mobile/MainActivity.kt
M	mobile/app/src/main/java/com/hydromate/mobile/Telemetry.kt
M	mobile/app/src/main/java/com/hydromate/mobile/ui/ReadingState.kt
M	mobile/app/src/main/java/com/hydromate/mobile/ui/dashboard/DashboardScreen.kt
M	mobile/app/src/main/java/com/hydromate/mobile/ui/history/HistoryScreen.kt
M	mobile/app/src/main/java/com/hydromate/mobile/ui/settings/SettingsScreen.kt
A	mobile/app/src/test/java/com/hydromate/mobile/PartialTelemetryTest.kt
M	mobile/app/src/test/java/com/hydromate/mobile/RepositoryTest.kt
M	mobile/app/src/test/java/com/hydromate/mobile/TelemetryTest.kt
M	scripts/capture_sensor_flow.py
M	scripts/mqtt_bridge.py
A	scripts/test_bridge.py
A	scripts/test_deployment.py
M	scripts/test_mqtt_flow.py
M	scripts/verify_production_compose.py
A	scripts/verify_public_access.py
```

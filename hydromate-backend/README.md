# HydroMate · API

API REST en Laravel 13 (PHP 8.3) que recibe la telemetría del ESP32 a través del
bridge MQTT, la guarda en PostgreSQL y la entrega a la app Android.

## Rutas principales

| Método | Ruta | Uso |
|---|---|---|
| POST | `/api/devices/{deviceId}/measurement-requests` | Solicitar una medición nueva desde la app |
| GET | `/api/measurement-requests/{requestId}` | Consultar el estado de esa solicitud |
| GET | `/api/devices/{deviceId}/status` | Última lectura y estado del dispositivo |

Contrato completo en [`docs/API.md`](../docs/API.md) y
[`docs/TELEMETRY_CONTRACT.md`](../docs/TELEMETRY_CONTRACT.md).

## Desarrollo

```bash
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan test
```

Pruebas en `tests/Feature`: ingesta de mediciones, telemetría parcial y
solicitudes de medición. Arranque local y producción: [`docs/SETUP.md`](../docs/SETUP.md).

#!/bin/sh
set -eu
if [ "${APP_ENV:-}" != production ] || [ "${APP_DEBUG:-false}" != false ]; then
    echo 'Production image requires APP_ENV=production and APP_DEBUG=false.' >&2
    exit 1
fi
if [ -z "${APP_KEY:-}" ]; then
    echo 'APP_KEY must be provided at runtime.' >&2
    exit 1
fi
# Rebuild per-container cache from runtime variables, never from build secrets.
php artisan config:cache --no-interaction
exec "$@"

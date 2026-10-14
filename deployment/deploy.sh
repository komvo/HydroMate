#!/bin/sh
# Invoked by the existing main deployment executor, on the VPS only.
set -eu
taskRepoRoot=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
taskEnvFile=${1:-/etc/hydromate/.env}
taskMqtt=${2:-}
case "$taskMqtt" in
    ''|--mqtt) ;;
    *) echo 'Usage: sh deployment/deploy.sh /etc/hydromate/.env [--mqtt]' >&2; exit 1 ;;
esac
if [ ! -f "$taskEnvFile" ]; then
    echo 'Administrator must provision the private HydroMate environment file.' >&2
    exit 1
fi
compose() {
    docker compose -p hydromate -f "$taskRepoRoot/compose.production.yml" --env-file "$taskEnvFile" "$@"
}
compose config --quiet
compose build --pull api
compose up -d --wait --wait-timeout 180 db api
# Never migrate in image build or concurrent container startup.
compose exec -T api php artisan migrate --force --no-interaction
compose exec -T api php /usr/local/bin/hydromate-healthcheck.php
if [ "$taskMqtt" = --mqtt ]; then
    compose --profile mqtt build --pull bridge
    compose --profile mqtt up -d --wait --wait-timeout 180 mosquitto bridge
fi
compose ps

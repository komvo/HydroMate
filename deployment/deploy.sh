#!/bin/sh
# Invoked by the existing main deployment executor, on the VPS only.
set -eu
taskRepoRoot=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
. "$taskRepoRoot/deployment/require-rootless.sh"
taskEnvFile=${1:-/etc/hydromate/.env}
taskMqtt=${2:-}
taskPublic=${3:-}
case "$taskMqtt" in
    ''|--mqtt) ;;
    *) echo 'Usage: sh deployment/deploy.sh /etc/hydromate/.env [--mqtt] [--public]' >&2; exit 1 ;;
esac
case "$taskPublic" in
    ''|--public) ;;
    *) echo 'Third argument must be --public or empty.' >&2; exit 1 ;;
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
    compose --profile mqtt build --pull mosquitto bridge
    compose --profile mqtt up -d --wait --wait-timeout 180 mosquitto bridge
fi
if [ "$taskPublic" = --public ]; then
    compose exec -T api php -r '$u=parse_url(getenv("APP_URL")); if (!$u || ($u["scheme"] ?? "") !== "https" || empty($u["host"]) || ($u["port"] ?? 443) !== 8443 || !empty($u["path"]) || isset($u["user"]) || isset($u["query"]) || isset($u["fragment"])) { fwrite(STDERR, "Set HYDROMATE_APP_URL to an HTTPS base on port 8443, without /api or credentials.\n"); exit(1); }'
    compose --profile public up -d --wait --wait-timeout 180 https
fi
compose ps

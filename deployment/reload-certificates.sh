#!/bin/sh
# Run by the administrator's existing DNS-01 renewal hook, HydroMate only.
set -eu
taskRepoRoot=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
. "$taskRepoRoot/deployment/require-rootless.sh"
taskEnvFile=${1:-/etc/hydromate/.env}
compose() {
    docker compose -p hydromate -f "$taskRepoRoot/compose.production.yml" --env-file "$taskEnvFile" "$@"
}
compose --profile public exec -T https nginx -t
compose --profile public exec -T https nginx -s reload
compose --profile mqtt kill -s HUP mosquitto

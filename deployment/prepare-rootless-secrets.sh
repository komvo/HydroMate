#!/bin/sh
# Permissions only; never reads, creates or prints certificate/password contents.
set -eu
taskRepoRoot=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
. "$taskRepoRoot/deployment/require-rootless.sh"
for taskDirectory in /etc/hydromate/https /etc/hydromate/mqtt; do
    test -d "$taskDirectory" && test ! -L "$taskDirectory" && test -w "$taskDirectory" || {
        echo "Administrator must grant deploy-hydromate ownership of $taskDirectory." >&2
        exit 1
    }
done
# UID 0 here maps to deploy-hydromate on the host. Service groups are mapped by
# Docker, not guessed as host GID 101/1883. The host owner can still renew files.
docker run --rm --network none --user 0:0 --entrypoint sh \
    --mount type=bind,source=/etc/hydromate/https,target=/tls \
    nginxinc/nginx-unprivileged:stable-alpine -eu -c '
    for f in fullchain.pem privkey.pem; do
        test -f "/tls/$f" && test ! -L "/tls/$f"
    done
    chown 0:101 /tls /tls/fullchain.pem /tls/privkey.pem
    chmod 750 /tls
    chmod 640 /tls/fullchain.pem /tls/privkey.pem
    '
docker run --rm --network none --user 0:0 --entrypoint sh \
    --mount type=bind,source=/etc/hydromate/mqtt,target=/tls \
    eclipse-mosquitto:2 -eu -c '
    for f in fullchain.pem privkey.pem passwd; do
        test -f "/tls/$f" && test ! -L "/tls/$f"
    done
    chown 0:1883 /tls /tls/fullchain.pem /tls/privkey.pem /tls/passwd
    chmod 750 /tls
    chmod 640 /tls/fullchain.pem /tls/privkey.pem /tls/passwd
    '

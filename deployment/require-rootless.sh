#!/bin/sh
# Source before any Docker mutation. Only this account's local rootless daemon.
if [ "$(id -un)" != deploy-hydromate ]; then
    echo 'Run as deploy-hydromate, without sudo docker.' >&2
    exit 1
fi
DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
export DOCKER_HOST
unset DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH
taskDockerSecurity=$(docker info --format '{{json .SecurityOptions}}') || exit 1
case "$taskDockerSecurity" in
    *'"name=rootless"'*) ;;
    *) echo 'Refusing deployment: the selected Docker daemon is not rootless.' >&2; exit 1 ;;
esac
unset taskDockerSecurity

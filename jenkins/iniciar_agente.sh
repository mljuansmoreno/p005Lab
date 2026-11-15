#!/usr/bin/env bash
set -euo pipefail
umask 077

trabajo="${RUTA_CI_AGENTE_DIR:-/var/tmp/ruta-estadistica-agente}"
jenkins="http://127.0.0.1:9090"
mkdir -m 700 -p "$trabajo"
cd "$trabajo"
if [[ ! -f conexion.secreto ]] || [[ "$(stat -c %a conexion.secreto)" != 600 ]]; then
  echo 'Guarde el secreto del nodo como conexion.secreto con modo 0600 en el directorio del agente.' >&2
  exit 1
fi

curl --noproxy '*' --fail --silent --show-error --max-time 30 \
  "$jenkins/jnlpJars/agent.jar" --output agent.jar
# El workspace queda bajo un directorio privado. Docker debe copiar fuentes legibles por UID 1654.
umask 022
exec java -jar agent.jar -url "$jenkins/" -name linux-docker \
  -secret @conexion.secreto -webSocket -workDir "$trabajo"

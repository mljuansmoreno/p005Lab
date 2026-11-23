#!/usr/bin/env bash
set -euo pipefail

[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_OS:-}" == Linux ]]
[[ "${GITHUB_REF:-}" == refs/heads/main ]]
[[ "$(git rev-parse HEAD)" == "$GITHUB_SHA" ]]
export PATH="${JAVA_HOME_21_X64:?Se requiere Java 21}/bin:$PATH"

numero=$((10000 + 100 * GITHUB_RUN_NUMBER + GITHUB_RUN_ATTEMPT))
controlador="ruta-estadistica-jenkins-alojado-$numero"
agente="/var/tmp/ruta-estadistica-agente"
privado="$(mktemp -d "${RUNNER_TEMP:?}/ruta-jenkins.XXXXXXXX")"
pid_agente=''
contenedor_creado=false
agente_creado=false
limpiar() {
  if [[ -n "$pid_agente" ]]; then
    kill "$pid_agente" 2>/dev/null || true
    wait "$pid_agente" 2>/dev/null || true
  fi
  if "$contenedor_creado"; then
    docker rm -fv "$controlador" >/dev/null 2>&1 || true
  fi
  if "$agente_creado"; then
    rm -f -- "$agente/conexion.secreto"
  fi
  rm -f -- "$privado/gitleaks" "$privado/gitleaks.tar.gz" "$privado/api" "$privado/netrc" "$privado/github"
}
trap limpiar EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

(umask 027; printf %s "${RUTA_CI_GITHUB_LECTURA:?Falta la credencial del checkout}" > "$privado/github")
unset RUTA_CI_GITHUB_LECTURA
docker build --tag ruta-estadistica-jenkins-alojado jenkins
docker run -d --name "$controlador" --publish 127.0.0.1:9090:8080 \
  --group-add "$(id -g)" --mount "type=bind,source=$privado/github,target=/run/secrets/github-lectura,readonly" \
  --cap-drop ALL --security-opt no-new-privileges --memory 1g --pids-limit 256 \
  --env 'JAVA_OPTS=-Djenkins.install.runSetupWizard=false -Xms128m -Xmx512m' \
  --env "RUTA_CI_EVENTO=$GITHUB_EVENT_NAME" --env "RUTA_CI_NUMERO_ALOJADO=$numero" \
  --mount "type=bind,source=$PWD/jenkins/alojado.groovy,target=/usr/share/jenkins/ref/init.groovy.d/alojado.groovy,readonly" \
  --mount "type=bind,source=$PWD/jenkins/trabajo-main.xml,target=/opt/ruta-ci/trabajo-main.xml,readonly" \
  ruta-estadistica-jenkins-alojado >/dev/null
contenedor_creado=true

echo 'Esperando al controlador Jenkins.'
for ((intento=0; intento<60; intento++)); do
  if docker exec "$controlador" test -s /var/jenkins_home/arranque-alojado/api; then
    break
  fi
  sleep 3
done
umask 077
mkdir -m 700 -- "$agente"
agente_creado=true
docker exec "$controlador" cat /var/jenkins_home/arranque-alojado/api > "$privado/api"
docker exec "$controlador" cat /var/jenkins_home/arranque-alojado/agente > "$agente/conexion.secreto"
IFS=: read -r usuario token < <(cat "$privado/api"; printf '\n')
printf 'machine 127.0.0.1 login %s password %s\n' "$usuario" "$token" > "$privado/netrc"
unset token

RUTA_CI_AGENTE_NETRC="$privado/netrc" bash jenkins/iniciar_agente.sh > "$privado/agente.log" 2>&1 &
pid_agente=$!
opciones=()
if [[ "${RUTA_CI_ALOJADO_SIN_CACHE:-false}" == true ]]; then
  opciones+=(--sin-cache)
fi
source guiones/ci/herramientas.sh
obtener_gitleaks_ci "$privado"
RUTA_CI_GITLEAKS_CONSOLA="$privado/gitleaks" python3 jenkins/recolectar_alojado.py "$privado/api" "$numero" "$GITHUB_SHA" "${opciones[@]}"
if [[ "${RUTA_CI_CAPTURAS:-false}" == true ]]; then
  node jenkins/capturar_alojado.mjs "$privado/api" "$numero" "$GITHUB_SHA"
fi

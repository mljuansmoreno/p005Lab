#!/usr/bin/env bash
set -euo pipefail

accion="${1:?Indique la comprobación Compose}"
web="http://127.0.0.1:${RUTA_ESTADISTICA_PUERTO_WEB:-8080}"
http() {
  curl --noproxy '*' --fail --silent --show-error --max-time 5 "$@"
}

case "$accion" in
  configuracion)
    docker compose config --quiet
    docker compose config --format json |
      jq -e --arg puerto "${RUTA_ESTADISTICA_PUERTO_WEB:-8080}" '
        (.services | keys) == ["aplicacion", "motor"] and
        (.networks | keys) == ["analisis", "entrada"] and
        .networks.analisis.driver == "bridge" and .networks.analisis.internal and
        (.services.motor.networks | keys) == ["analisis"] and
        (.services.aplicacion.networks | keys) == ["analisis", "entrada"] and
        (.services.motor.ports | length) == 0 and
        (.services.aplicacion.ports | length) == 1 and
        .services.aplicacion.ports[0].host_ip == "127.0.0.1" and
        .services.aplicacion.ports[0].target == 8080 and
        (.services.aplicacion.ports[0].published | tostring) == $puerto and
        .services.aplicacion.environment.RUTA_ESTADISTICA_MOTOR_URL == "http://motor:8787" and
        all(.services[];
          .read_only and (.cap_drop | index("ALL")) != null and
          (.security_opt | any(startswith("no-new-privileges"))) and
          ([.secrets[].source] == ["motor"])) and
        (.services.motor.tmpfs | any(startswith("/tmp:")))
      '
    ;;
  red)
    proyecto="${COMPOSE_PROJECT_NAME:-ruta-estadistica-demo}"
    aplicacion="$(docker compose ps --format '{{.Name}}' aplicacion)"
    motor="$(docker compose ps --format '{{.Name}}' motor)"
    test -n "$aplicacion" && test -n "$motor" || exit 1
    docker network inspect "${proyecto}_analisis" |
      jq -er --arg aplicacion "$aplicacion" --arg motor "$motor" '
        .[0] | select(.Driver == "bridge" and .Internal and
          ([.Containers[].Name] | sort) == ([$aplicacion, $motor] | sort)) |
        "\(.Name) (\(.Driver))", (.Containers[] | "\(.Name) \(.IPv4Address)")
      '
    docker inspect "$motor" --format '{{json .HostConfig.PortBindings}}' |
      jq -e 'length == 0'
    docker compose port aplicacion 8080 | grep -Fx "127.0.0.1:${RUTA_ESTADISTICA_PUERTO_WEB:-8080}"
    ;;
  aislamiento)
    aplicacion="$(docker compose ps -q aplicacion)"
    motor="$(docker compose ps -q motor)"
    docker inspect "$aplicacion" "$motor" |
      jq -e '
        if length == 2 and all(.[];
          .Config.User == "1654:1654" and .State.Health.Status == "healthy" and
          .HostConfig.ReadonlyRootfs and (.HostConfig.Privileged | not) and
          (.HostConfig.CapDrop | map(ascii_downcase) | index("all")) != null and
          (.HostConfig.SecurityOpt | any(startswith("no-new-privileges"))) and
          .HostConfig.Memory > 0 and .HostConfig.PidsLimit > 0 and
          .HostConfig.LogConfig.Type == "local" and
          ([.Mounts[] | select(.Destination == "/run/secrets/motor" and (.RW | not))] | length) == 1 and
          all(.Mounts[]; .Destination != "/var/run/docker.sock")
        ) then
          {servicios: [.[] | {servicio: .Config.Labels["com.docker.compose.service"],
            usuario: .Config.User, salud: .State.Health.Status, raiz_solo_lectura: .HostConfig.ReadonlyRootfs,
            memoria_limite: .HostConfig.Memory, procesos_limite: .HostConfig.PidsLimit,
            registro: .HostConfig.LogConfig.Type, secreto_solo_lectura: true}]}
        else error("No se cumplen los controles de aislamiento de ambos servicios") end
      '
    ;;
  acceso)
    http "$web/salud" | jq -e '.estado == "activo"'
    http "$web/" | grep -F 'action="/analizar"' > /dev/null
    ;;
  autenticacion)
    http "$web/listo" | jq -e '.listo == true'
    docker compose exec -T aplicacion python - <<'PY'
from http.client import HTTPConnection
cliente = HTTPConnection("motor", 8787, timeout=5)
try:
    cliente.request("GET", "/salud")
    estado = cliente.getresponse().status
finally:
    cliente.close()
if estado != 403:
    raise SystemExit(f"Se esperaba HTTP 403 sin credencial; respuesta: {estado}")
print("Motor: HTTP 403 sin credencial; sonda autenticada correcta.")
PY
    ;;
  calcular)
    docker compose exec -T aplicacion python probar_compose.py
    ;;
  recuperar)
    anterior="$(docker compose ps -q motor)"
    test -n "$anterior"
    docker compose stop motor
    http "$web/salud" | jq -e '.estado == "activo"'
    codigo="$(curl --noproxy '*' --silent --show-error --max-time 5 \
      --output /dev/null --write-out '%{http_code}' "$web/listo")"
    test "$codigo" = 503
    printf 'Disponibilidad con motor detenido: HTTP %s\n' "$codigo"
    docker compose up -d --no-deps --force-recreate --wait --wait-timeout "${RUTA_CI_ESPERA_SALUD:-90}" motor
    nuevo="$(docker compose ps -q motor)"
    test -n "$nuevo"
    test "$anterior" != "$nuevo"
    http "$web/listo" | jq -e '.listo == true'
    docker compose exec -T aplicacion python probar_compose.py
    ;;
  r)
    docker compose exec -T motor Rscript --version
    docker compose exec -T -e R_LIBS_USER=/aplicacion/runtime/biblioteca motor \
      Rscript --vanilla /aplicacion/motor_r/rutaanalitica/tests/verificar.R
    printf "Suite de rutaanalitica ejecutada correctamente.\n"
    ;;
  *)
    printf 'Comprobación Compose desconocida: %s\n' "$accion" >&2
    exit 2
    ;;
esac

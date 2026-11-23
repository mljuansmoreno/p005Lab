#!/usr/bin/env bash
# Mantiene un paquete comprobado por herramienta y extrae cada binario en el temporal del build.

huella_ci() {
  printf '%s  %s\n' "$1" "$2" | sha256sum --check --status
}

obtener_herramienta_ci() (
  set -euo pipefail
  local herramienta="$1" url="$2" huella="$3" destino="$4"
  local paquete="$destino/$herramienta.tar.gz"
  local cache="${RUTA_CI_CACHE_HERRAMIENTAS:-}" copia=''

  if [[ -n "$cache" ]] && ! mkdir -p -m 700 -- "$cache"; then
    cache=''
  fi
  if [[ -n "$cache" && -f "$cache/$herramienta.tar.gz" ]] &&
     cp -- "$cache/$herramienta.tar.gz" "$paquete" &&
     huella_ci "$huella" "$paquete"; then
    tar -xzf "$paquete" -C "$destino" -- "$herramienta"
    return
  fi

  curl --fail --silent --show-error --location --retry 3 \
    --connect-timeout 15 --max-time 180 "$url" --output "$paquete" || return
  huella_ci "$huella" "$paquete" || return
  tar -xzf "$paquete" -C "$destino" -- "$herramienta" || return

  if [[ -n "$cache" ]]; then
    trap 'if [[ -n "$copia" ]]; then rm -f -- "$copia"; fi' EXIT
    if ! copia="$(mktemp "$cache/.$herramienta.XXXXXXXX")" ||
       ! cp -- "$paquete" "$copia" ||
       ! mv -fT -- "$copia" "$cache/$herramienta.tar.gz"; then
      printf 'No se pudo actualizar la cachÃ© de %s. Se usarÃ¡ la descarga verificada.\n' "$herramienta" >&2
    fi
  fi
)

obtener_gitleaks_ci() {
  obtener_herramienta_ci gitleaks \
    https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
    551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb "$1"
}

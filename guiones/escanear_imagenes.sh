#!/usr/bin/env bash
set -euo pipefail

evidencias="$1"
temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT

instalar() {
  local herramienta="$1" url="$2" huella="$3"
  curl --fail --silent --show-error --location --retry 3 \
    --connect-timeout 15 --max-time 180 "$url" --output "$temporal/paquete.tar.gz"
  printf '%s  %s\n' "$huella" "$temporal/paquete.tar.gz" | sha256sum --check --status
  tar -xzf "$temporal/paquete.tar.gz" -C "$temporal" -- "$herramienta"
}

instalar syft \
  https://github.com/anchore/syft/releases/download/v1.57.1/syft_1.57.1_linux_amd64.tar.gz \
  bf52519eb57f675d47c07d43213cb6dff6449f3d6d1147ff6701ed91f44eef0c
instalar grype \
  https://github.com/anchore/grype/releases/download/v0.121.3/grype_0.121.3_linux_amd64.tar.gz \
  e9da18cc1429e786722e32161288103600efffd8e483c90761f90485bd1bec85

"$temporal/grype" db update
base_avisos="$("$temporal/grype" db status -o json | jq -er 'select(.valid) | .built | strings')"
export GRYPE_DB_AUTO_UPDATE=false
for servicio in aplicacion motor; do
  imagen="$(docker compose images -q "$servicio")"
  test -n "$imagen"
  "$temporal/syft" "docker:$imagen" -o cyclonedx-json > "$temporal/sbom.json"
  jq -e '.components | length > 0' "$temporal/sbom.json" > /dev/null
  "$temporal/grype" "sbom:$temporal/sbom.json" -o json > "$temporal/grype.json"
  jq --arg imagen "$imagen" --arg base "$base_avisos" '
    if (.matches | type) != "array" then
      error("Informe de Grype incompleto")
    else
      ([.matches[] | .vulnerability.severity | ascii_downcase]) as $severidades |
      {imagen: $imagen, base_avisos: $base,
       altas: ($severidades | map(select(. == "high")) | length),
       criticas: ($severidades | map(select(. == "critical")) | length),
       pendientes: [.matches[] | select(.vulnerability.severity | ascii_downcase | IN("high", "critical")) |
         {aviso: .vulnerability.id, paquete: .artifact.name, instalada: .artifact.version,
          corregidas: .vulnerability.fix.versions}]}
    end
  ' "$temporal/grype.json" | tee "$evidencias/seguridad-$servicio.json"
done

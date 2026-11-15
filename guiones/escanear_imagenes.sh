#!/usr/bin/env bash
set -euo pipefail

evidencias="$1"
temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT

source "$(dirname -- "${BASH_SOURCE[0]}")/ci/herramientas.sh"

obtener_herramienta_ci syft \
  https://github.com/anchore/syft/releases/download/v1.57.1/syft_1.57.1_linux_amd64.tar.gz \
  bf52519eb57f675d47c07d43213cb6dff6449f3d6d1147ff6701ed91f44eef0c "$temporal"
obtener_herramienta_ci grype \
  https://github.com/anchore/grype/releases/download/v0.121.3/grype_0.121.3_linux_amd64.tar.gz \
  e9da18cc1429e786722e32161288103600efffd8e483c90761f90485bd1bec85 "$temporal"

"$temporal/grype" db update
base_avisos="$("$temporal/grype" db status -o json | jq -er 'select(.valid) | .built | strings')"
export GRYPE_DB_AUTO_UPDATE=false
for servicio in aplicacion motor; do
  referencia="$(docker compose images -q "$servicio")"
  test -n "$referencia"
  # Docker save requiere el prefijo cuando Compose devuelve los 64 hexadecimales.
  if [[ "$referencia" =~ ^[0-9a-f]{64}$ ]]; then
    referencia="sha256:$referencia"
  fi
  imagen="$(docker image inspect --format '{{.Id}}' "$referencia")"
  [[ "$imagen" =~ ^sha256:[0-9a-f]{64}$ ]]
  "$temporal/syft" "docker:$imagen" -o cyclonedx-json > "$temporal/sbom.json"
  componentes="$(jq -er 'select(.bomFormat == "CycloneDX") | .components |
    select(type == "array" and length > 0) | length' "$temporal/sbom.json")"
  huella="$(sha256sum "$temporal/sbom.json")"
  "$temporal/grype" "sbom:$temporal/sbom.json" -o json > "$temporal/grype.json"
  jq --arg imagen "$imagen" --arg base "$base_avisos" \
     --arg huella "${huella%% *}" --argjson componentes "$componentes" '
    if (.matches | type) != "array" then
      error("Informe de Grype incompleto")
    else
      ([.matches[] | .vulnerability.severity | ascii_downcase]) as $severidades |
      {imagen: $imagen, base_avisos: $base,
       sbom: {formato: "CycloneDX", sha256: $huella, componentes: $componentes},
       altas: ($severidades | map(select(. == "high")) | length),
       criticas: ($severidades | map(select(. == "critical")) | length),
       pendientes: [.matches[] | select(.vulnerability.severity | ascii_downcase | IN("high", "critical")) |
         {aviso: .vulnerability.id, paquete: .artifact.name, instalada: .artifact.version,
          corregidas: .vulnerability.fix.versions}]}
    end
  ' "$temporal/grype.json" | tee "$evidencias/seguridad-$servicio.json"
done

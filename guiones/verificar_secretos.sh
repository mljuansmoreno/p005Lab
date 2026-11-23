#!/usr/bin/env bash
set -euo pipefail

temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT
source "$(dirname -- "${BASH_SOURCE[0]}")/ci/herramientas.sh"

obtener_gitleaks_ci "$temporal"

python3 guiones/ci/escanear_secretos.py "$temporal/gitleaks"

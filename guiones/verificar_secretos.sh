#!/usr/bin/env bash
set -euo pipefail

temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT
source "$(dirname -- "${BASH_SOURCE[0]}")/ci/herramientas.sh"

obtener_herramienta_ci gitleaks \
  https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
  551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb "$temporal"

python3 guiones/ci/escanear_secretos.py "$temporal/gitleaks"

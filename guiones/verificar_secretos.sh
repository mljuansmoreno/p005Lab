#!/usr/bin/env bash
set -euo pipefail

temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT
paquete="$temporal/gitleaks.tar.gz"
curl --fail --silent --show-error --location --retry 3 --connect-timeout 15 \
  --max-time 180 https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
  --output "$paquete"
printf '%s  %s\n' '551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb' "$paquete" \
  | sha256sum --check --status
tar -xzf "$paquete" -C "$temporal" -- gitleaks

"$temporal/gitleaks" dir --no-banner --redact=100 --max-archive-depth=2 --max-decode-depth=2 .

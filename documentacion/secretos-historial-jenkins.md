# Revisión del hallazgo de secretos en el historial

El control `git-historial-secretos` de la auditoría del 16 de noviembre detectó coincidencias. Se repitió con Gitleaks 8.30.1 sobre todas las refs locales disponibles en `1da71972ecea1768d7609238eb26b5fb81a1ec4b`, conservando las reglas originales y usando `--redact=100`. [Registro de la auditoría inicial](informes/revisiones-seguridad/2026-11-16/git-historial-secretos.json).

Las 23 coincidencias de `generic-api-key` se concentran en `jenkins/plugins.txt` en un único commit. Las líneas tenían el formato público `plugin:versión`. Se cotejó cada pareja con el inventario actual y las 23 coincidieron exactamente. El resultado es **falso positivo** para esas líneas. No hay rotación pendiente a raíz de estas coincidencias. [Resultado redactado](evidencias-jenkins/secretos-historial.json) · [Inventario vigente](../jenkins/plugins.txt).

Para reproducir la verificación con el binario 8.30.1, ejecute `gitleaks git --no-banner --redact=100 --log-opts=--all --exit-code=17 .`. El anexo conserva regla, archivo, SHA y líneas. El pipeline mantiene el [escaneo de fuentes y comprimidos](../guiones/verificar_secretos.sh).

La comprobación posterior del 22 de noviembre registró resultado correcto en la revisión `154c56ea844e60da671beae146b736fe11df982a`. Las exclusiones identifican cada coincidencia por commit, archivo, regla y línea. El inventario adjunta las versiones públicas cotejadas. [Control del 22 de noviembre](informes/revisiones-seguridad/2026-11-22/git-historial-secretos.json) · [Huellas individuales](../.gitleaksignore) · [Versiones contrastadas](../jenkins/versiones-publicas-verificadas.json).

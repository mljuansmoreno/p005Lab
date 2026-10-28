$ErrorActionPreference = 'Stop'
$env:RUTA_ESTADISTICA_ARCHIVO_SECRETO = (Join-Path $env:LOCALAPPDATA 'RutaEstadistica/motor.secreto').Replace('\', '/')
& docker compose -f "$(Split-Path $PSScriptRoot)/contenedores/compose.yaml" stop motor
if ($LASTEXITCODE) { throw 'DOCKER_DETENCION_FALLIDA' }

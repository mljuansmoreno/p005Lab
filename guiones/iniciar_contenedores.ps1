param([switch]$Construir)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$directorio = Join-Path $env:LOCALAPPDATA 'RutaEstadistica'
New-Item -ItemType Directory -Force $directorio | Out-Null
$secreto = Join-Path $directorio 'motor.secreto'
if (-not (Test-Path $secreto)) {
    [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(48)) | Set-Content $secreto -NoNewline
    # La credencial es local; no se incluye en argumentos de procesos ni en el repositorio.
    $identidad = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls $secreto /inheritance:r /grant:r "${identidad}:(R,W)" | Out-Null
    if ($LASTEXITCODE) { throw 'MOTOR_SECRETO_PERMISOS_INVALIDOS' }
}
$env:RUTA_ESTADISTICA_ARCHIVO_SECRETO = $secreto.Replace('\', '/')
& docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE) { throw 'DOCKER_NO_DISPONIBLE' }
if ($Construir) { & docker compose -f "$raiz/contenedores/compose.yaml" build motor; if ($LASTEXITCODE) { throw 'DOCKER_COMPILACION_FALLIDA' } }
& docker compose -f "$raiz/contenedores/compose.yaml" up -d motor
if ($LASTEXITCODE) { throw 'DOCKER_INICIO_FALLIDO' }

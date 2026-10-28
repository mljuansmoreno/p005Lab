param([switch]$Publicar)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$dotnet = if (Test-Path "$raiz/.herramientas/dotnet/dotnet.exe") { "$raiz/.herramientas/dotnet/dotnet.exe" } else { 'dotnet' }
if ($Publicar) {
    & $dotnet publish "$raiz/codigo/RutaEstadistica.Escritorio" -c Release -p:Platform=x64 -o "$raiz/salidas/aplicacion"
    if ($LASTEXITCODE) { throw 'COMPILACION_FALLIDA' }
    if (-not (Test-Path "$raiz/salidas/recursos/runtime/R/bin/Rscript.exe")) { throw 'MOTOR_NO_DISPONIBLE: ejecute preparar_desarrollo.ps1.' }
    Copy-Item "$raiz/salidas/recursos/*" "$raiz/salidas/aplicacion" -Recurse -Force
    & $dotnet publish "$raiz/codigo/RutaEstadistica.ServidorMcp" -c Release -r win-x64 --self-contained true -o "$raiz/salidas/aplicacion/integracion"
    if ($LASTEXITCODE) { throw 'COMPILACION_MCP_FALLIDA' }
} else {
    & $dotnet build "$raiz/codigo/RutaEstadistica.Escritorio" -c Release -p:Platform=x64
    if ($LASTEXITCODE) { throw 'COMPILACION_FALLIDA' }
}

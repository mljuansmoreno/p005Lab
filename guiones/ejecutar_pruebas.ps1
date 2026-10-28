param([string]$RutaR = 'C:/Program Files/R/R-4.5.2')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:LANG = 'Spanish_Colombia.utf8'
$env:R_LIBS_USER = "$raiz/.dependencias/R/biblioteca"
$dotnet = if (Test-Path "$raiz/.herramientas/dotnet/dotnet.exe") { "$raiz/.herramientas/dotnet/dotnet.exe" } else { 'dotnet' }
& "$RutaR/bin/Rscript.exe" --vanilla "$raiz/motor_r/rutaanalitica/tests/verificar.R"
if ($LASTEXITCODE) { throw 'PRUEBAS_NUMERICAS_FALLIDAS' }
& $dotnet run --project "$raiz/pruebas/RutaEstadistica.PruebasUnitarias" -c Release -- "$raiz/salidas/recursos"
if ($LASTEXITCODE) { throw 'PRUEBAS_INTEGRACION_FALLIDAS' }
& "$PSScriptRoot/verificar_documentacion.ps1"
& "$PSScriptRoot/auditar_nombres.ps1"

param([string]$Dotnet = 'dotnet', [string]$Herramienta = 'dotnet-coverage', [string]$Recursos)
$ErrorActionPreference = 'Stop'
$raiz = (Resolve-Path "$PSScriptRoot/../..").Path
if (-not $Recursos) { $Recursos = "$raiz/salidas/recursos" }
$salida = New-Item -ItemType Directory -Force "$raiz/salidas/qa/cobertura"
& $Dotnet build "$raiz/pruebas/RutaEstadistica.PruebasUnitarias" -c Release --no-restore
if ($LASTEXITCODE) { throw 'Falló la compilación del arnés .NET' }
$arnes = "$raiz/pruebas/RutaEstadistica.PruebasUnitarias/bin/Release/net10.0/RutaEstadistica.PruebasUnitarias.dll"
$informe = Join-Path $salida.FullName 'dotnet.xml'
$env:DOTNET_COVERAGE_TELEMETRY_OPTOUT = '1'
& $Herramienta collect --settings "$PSScriptRoot/cobertura_dotnet.config" -f cobertura -o $informe $Dotnet $arnes $Recursos
if ($LASTEXITCODE) { throw 'Falló la ejecución instrumentada de .NET' }
[xml]$xml = Get-Content -LiteralPath $informe -Raw
$paquetes = @($xml.coverage.packages.package.name)
if (-not $paquetes.Count -or $paquetes -contains 'RutaEstadistica.PruebasUnitarias' -or
    $paquetes -notcontains 'RutaEstadistica.Infraestructura') { throw 'Alcance de cobertura .NET inesperado' }

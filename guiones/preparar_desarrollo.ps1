param([string]$RutaR = 'C:/Program Files/R/R-4.5.2', [switch]$AdquirirJson)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$dependencias = Join-Path $raiz '.dependencias'
$biblioteca = Join-Path $dependencias 'R/biblioteca'
New-Item -ItemType Directory -Force $biblioteca | Out-Null
if (-not (Test-Path "$RutaR/bin/Rscript.exe")) { throw 'MOTOR_NO_DISPONIBLE: indique -RutaR con R 4.5.2 para Windows x64.' }
$env:LANG = 'Spanish_Colombia.utf8'
$env:R_LIBS_USER = $biblioteca
if ($AdquirirJson) {
    $archivo = Join-Path $dependencias 'jsonlite_2.0.0.zip'
    Invoke-WebRequest 'https://cran.r-project.org/bin/windows/contrib/4.5/jsonlite_2.0.0.zip' -OutFile $archivo
    & "$RutaR/bin/Rscript.exe" --vanilla -e 'argumentos <- commandArgs(TRUE); install.packages(argumentos[1], repos=NULL, lib=argumentos[2])' $archivo $biblioteca
    if ($LASTEXITCODE) { throw 'DEPENDENCIA_INSTALACION_FALLIDA' }
}
& "$RutaR/bin/R.exe" CMD INSTALL "--library=$biblioteca" "$raiz/motor_r/rutaanalitica"
if ($LASTEXITCODE) { throw 'MOTOR_PAQUETE_NO_DISPONIBLE' }
$recursos = Join-Path $raiz 'salidas/recursos'
New-Item -ItemType Directory -Force "$recursos/runtime/R", "$recursos/runtime/biblioteca", "$recursos/motor_r" | Out-Null
Copy-Item -Path "$RutaR/*" -Destination "$recursos/runtime/R" -Recurse -Force
Copy-Item -Path "$biblioteca/*" -Destination "$recursos/runtime/biblioteca" -Recurse -Force
Copy-Item "$raiz/motor_r/trabajador.R" "$recursos/motor_r/trabajador.R" -Force
Get-ChildItem "$recursos/runtime" -File -Recurse | ForEach-Object { [pscustomobject]@{ archivo = [IO.Path]::GetRelativePath($recursos, $_.FullName); sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() } } | ConvertTo-Json -Depth 4 | Set-Content "$recursos/integridad.json" -Encoding utf8
Write-Output "Recursos nativos preparados en $recursos"

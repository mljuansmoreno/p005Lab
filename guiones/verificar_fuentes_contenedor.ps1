$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$registro = Get-Content "$raiz/contenedores/bases.lock.json" -Raw | ConvertFrom-Json
$definicion = Get-Content "$raiz/contenedores/Dockerfile" -Raw
foreach ($par in @(@('sdk','IMAGEN_SDK'), @('motor_r','IMAGEN_R'))) {
    $base = $registro.($par[0])
    if ($base.resumen -notmatch '^sha256:[a-f0-9]{64}$') { throw 'IMAGEN_RESUMEN_INVALIDO' }
    $coincidencia = [regex]::Match($definicion, "(?m)^ARG $($par[1])=(.+)$")
    if (-not $coincidencia.Success -or $coincidencia.Groups[1].Value.Trim() -cne "$($base.imagen)@$($base.resumen)") { throw 'IMAGEN_RESUMEN_NO_COINCIDE' }
}
$fuente = Join-Path $raiz 'distribucion/fuentes/jsonlite_2.0.0.tar.gz'
$huella = (Get-FileHash -LiteralPath $fuente -Algorithm SHA256).Hash.ToLowerInvariant()
if ($huella -cne $registro.jsonlite.sha256 -or -not $definicion.Contains($huella)) { throw 'FUENTE_RESUMEN_NO_COINCIDE' }
Write-Output 'VERIFICADO: digests declarados y fuente jsonlite coherentes con el registro. No acredita construcción ni ejecución Docker.'

param([string]$Nombre = 'RutaEstadistica.Pruebas', [string]$Editor = 'CN=DesarrolloLocal', [string]$Version = '0.1.0.0', [switch]$Tienda)
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
if ($Tienda -and ($Nombre -eq 'RutaEstadistica.Pruebas' -or $Editor -eq 'CN=DesarrolloLocal')) { throw 'TIENDA_IDENTIDAD_NO_CONFIGURADA: indique identidad y editor de Partner Center.' }
if ($Nombre -notmatch '^[A-Za-z0-9.-]{3,50}$' -or $Version -notmatch '^\d+\.\d+\.\d+\.\d+$') { throw 'PAQUETE_IDENTIDAD_INVALIDA' }
$aplicacion = Join-Path $raiz 'salidas/aplicacion'
foreach ($archivo in @('RutaEstadistica.Escritorio.exe','runtime/R/bin/Rscript.exe','integracion/RutaEstadistica.ServidorMcp.exe')) { if (-not (Test-Path "$aplicacion/$archivo")) { throw "PAQUETE_RECURSO_AUSENTE: $archivo" } }
$makeappx = 'C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64/makeappx.exe'
if (-not (Test-Path $makeappx)) { throw 'PAQUETE_SDK_NO_DISPONIBLE' }
New-Item -ItemType Directory -Force "$aplicacion/recursos", "$raiz/salidas/paquetes" | Out-Null
Add-Type -AssemblyName System.Drawing
foreach ($tamano in @(44, 150, 50)) {
    $imagen = [Drawing.Bitmap]::new($tamano,$tamano); $lienzo = [Drawing.Graphics]::FromImage($imagen)
    $lienzo.Clear([Drawing.Color]::FromArgb(29,91,85))
    $pincel = [Drawing.SolidBrush]::new([Drawing.Color]::White)
    for ($indice = 0; $indice -lt 3; $indice++) { $alto = [int]($tamano * (0.25 + $indice * 0.15)); $lienzo.FillRectangle($pincel,[int]($tamano * (0.18 + 0.23 * $indice)),[int]($tamano * 0.8 - $alto),[int]($tamano * 0.15),$alto) }
    $imagen.Save("$aplicacion/recursos/icono$($tamano).png",[Drawing.Imaging.ImageFormat]::Png)
    $pincel.Dispose(); $lienzo.Dispose(); $imagen.Dispose()
}
[xml]$manifiesto = Get-Content "$raiz/empaquetado/Package.appxmanifest" -Raw
$manifiesto.Package.Identity.Name = $Nombre; $manifiesto.Package.Identity.Publisher = $Editor; $manifiesto.Package.Identity.Version = $Version
$manifiesto.Save("$aplicacion/AppxManifest.xml")
$destino = "$raiz/salidas/paquetes/RutaEstadistica_$Version`_x64_sin_firma.msix"
& $makeappx pack /d $aplicacion /p $destino /o
if ($LASTEXITCODE) { throw 'PAQUETE_VALIDACION_FALLIDA' }
Get-FileHash $destino -Algorithm SHA256 | Format-List
Write-Output 'Paquete SIN FIRMA generado. No acredita instalación, certificación ni aprobación de la Tienda.'

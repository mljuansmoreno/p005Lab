$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$requeridos = @('manual_usuario','arquitectura','mapa_codigo','recorrido_completo','instalacion_desarrollo','motor_r_y_metodos','datos_y_persistencia','contratos_y_api','docker','mcp','depuracion','errores_y_soluciones','observabilidad','pruebas_y_calidad','seguridad_y_privacidad','empaquetado_y_publicacion','lista_publicacion_tienda','versiones_y_compatibilidad','convenciones_y_excepciones','guia_mantenimiento','limitaciones_y_pendientes','licencias_y_dependencias','estado_entrega','continuidad')
$errores = [Collections.Generic.List[string]]::new()
foreach ($nombre in $requeridos) { if (-not (Test-Path "$raiz/documentacion/$nombre.md")) { $errores.Add("Falta documentacion/$nombre.md") } }
foreach ($archivo in Get-ChildItem "$raiz/documentacion" -Filter '*.md' -Recurse) {
    $texto = Get-Content $archivo.FullName -Raw
    if ($texto -match '(?im)^#+\s*(TODO|TBD|Lorem ipsum)') { $errores.Add("Encabezado vacío en $($archivo.Name)") }
    foreach ($enlace in [regex]::Matches($texto, '\[[^\]]*\]\(([^)]+)\)')) {
        $destino = $enlace.Groups[1].Value.Split('#')[0]
        if ($destino -and $destino -notmatch '^[a-z]+:' -and -not (Test-Path (Join-Path $archivo.DirectoryName ([Uri]::UnescapeDataString($destino))))) { $errores.Add("Enlace roto en $($archivo.Name): $destino") }
    }
}
$catalogo = Get-Content "$raiz/documentacion/errores_y_soluciones.md" -Raw
foreach ($archivo in Get-ChildItem "$raiz/codigo","$raiz/motor_r" -File -Recurse | Where-Object { $_.Extension -in '.cs','.R' -and $_.FullName -notmatch '[\\/](bin|obj)[\\/]' }) {
    foreach ($codigo in [regex]::Matches((Get-Content $archivo.FullName -Raw), '"([A-Z]{2,}(?:_[A-Z]+)+)"')) {
        $valor = $codigo.Groups[1].Value
        if ($valor -notmatch '^(R_|RUTA_|LC_)' -and $catalogo -notmatch [regex]::Escape($valor)) { $errores.Add("Código sin catálogo: $valor") }
    }
}
if (-not (Select-String "$raiz/documentacion/estado_entrega.md" -Pattern 'Implementación.*Verificación' -Quiet)) { $errores.Add('Falta matriz de implementación y verificación') }
if ($errores.Count) { $errores | Write-Output; throw 'DOCUMENTACION_INCOMPLETA' }
Write-Output 'VERIFICADO: archivos requeridos, enlaces locales, encabezados, códigos y matriz. La exactitud de la prosa requiere revisión humana.'

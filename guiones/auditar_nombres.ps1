$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot
$glosario = Get-Content "$raiz/documentacion/glosario_nombres.json" -Raw | ConvertFrom-Json
$conocidos = [Collections.Generic.HashSet[string]]::new([string[]]$glosario.identificadores, [StringComparer]::Ordinal)
$hallazgos = [Collections.Generic.List[object]]::new()
foreach ($archivo in Get-ChildItem "$raiz/codigo","$raiz/motor_r" -Recurse -File | Where-Object { $_.Extension -in '.cs','.R' -and $_.FullName -notmatch '[\\/](bin|obj)[\\/]' }) {
    $texto = Get-Content $archivo.FullName -Raw
    foreach ($coincidencia in [regex]::Matches($texto, '(?:\b(?:class|record|interface|enum|var)\s+|^\s*)([A-Za-z_][A-Za-z0-9_]*)\s*(?:<-|[=(])', [Text.RegularExpressions.RegexOptions]::Multiline)) {
        $nombre = $coincidencia.Groups[1].Value
        if (-not $conocidos.Contains($nombre)) { $hallazgos.Add([pscustomobject]@{ archivo = [IO.Path]::GetRelativePath($raiz, $archivo.FullName); identificador = $nombre; estado = 'REQUIERE_REVISION' }) }
    }
    if ($texto -match '\b(DataService|ProjectManager|AnalysisResult|filePath|isLoading|handleSubmit)\b') { throw "NOMBRE_INGLES_NO_ADMITIDO: $($archivo.Name)" }
}
New-Item -ItemType Directory -Force "$raiz/salidas/informes" | Out-Null
ConvertTo-Json -InputObject @($hallazgos) -Depth 4 | Set-Content "$raiz/salidas/informes/auditoria_nombres.json" -Encoding utf8
Write-Output "Auditoría heurística: $($hallazgos.Count) nombres desconocidos requieren revisión. No certifica corrección lingüística."
if ($hallazgos.Count) { throw 'NOMBRES_REQUIEREN_REVISION' }

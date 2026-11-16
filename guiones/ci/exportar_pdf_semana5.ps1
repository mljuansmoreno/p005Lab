[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RutaDocx,
    [string]$Destino
)

$ErrorActionPreference = 'Stop'
$entrada = (Resolve-Path -LiteralPath $RutaDocx).Path
if ([IO.Path]::GetExtension($entrada) -ne '.docx') {
    throw 'La entrada debe ser un documento DOCX.'
}

$pdf = if ($Destino) {
    $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destino)
} else {
    [IO.Path]::ChangeExtension($entrada, '.pdf')
}
if ([IO.Path]::GetExtension($pdf) -ne '.pdf') {
    throw 'El destino debe tener extensión PDF.'
}

$word = New-Object -ComObject Word.Application
try {
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $documento = $word.Documents.Open($entrada, $false, $true)
    try {
        $documento.ExportAsFixedFormat($pdf, 17)
    } finally {
        $documento.Close(0)
    }
} finally {
    $word.Quit(0)
}

Write-Output $pdf

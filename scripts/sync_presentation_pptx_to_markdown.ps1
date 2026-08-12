param(
    [string]$InputPath = "docs/presentacion_proceso_interno_sentadilla_v4.pptx",
    [string]$OutputPath = "docs/markdown-snapshots/presentacion_proceso_interno_sentadilla_v4.md"
)

$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$resolvedInput = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $InputPath))
$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $OutputPath))

if (-not (Test-Path -LiteralPath $resolvedInput -PathType Leaf)) {
    throw "No se encontro la presentacion de entrada: $resolvedInput"
}

$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$temporaryOutput = "$resolvedOutput.tmp"

try {
    & npx --yes '@firecrawl/anydoc' $resolvedInput -o $temporaryOutput
    if ($LASTEXITCODE -ne 0) {
        throw "AnyDoc termino con el codigo $LASTEXITCODE."
    }

    $markdown = [System.IO.File]::ReadAllText($temporaryOutput, [System.Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($markdown)) {
        throw "La conversion produjo un archivo vacio."
    }

    if ($markdown.Contains([char]0xFFFD) -or $markdown.Contains([char]0x00C3) -or $markdown.Contains([char]0x00C2)) {
        throw "La validacion detecto caracteres compatibles con una codificacion danada."
    }

    Move-Item -Force -LiteralPath $temporaryOutput -Destination $resolvedOutput

    $headingCount = ([regex]::Matches($markdown, "(?m)^#{1,6}\s")).Count
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedInput).Hash
    $outputHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutput).Hash

    Write-Host "Instantanea Markdown actualizada correctamente."
    Write-Host "Entrada: $resolvedInput"
    Write-Host "Salida:  $resolvedOutput"
    Write-Host "Caracteres: $($markdown.Length) | Encabezados: $headingCount"
    Write-Host "SHA256 PPTX: $sourceHash"
    Write-Host "SHA256 MD:   $outputHash"
}
finally {
    if (Test-Path -LiteralPath $temporaryOutput) {
        Remove-Item -Force -LiteralPath $temporaryOutput
    }
}

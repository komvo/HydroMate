param([string]$SketchbookPath = '')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
if (!$SketchbookPath) {
    $SketchbookPath = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Arduino'
}
$taskLibraryRoot = Join-Path $SketchbookPath 'libraries'
$taskLibraries = @(
    @{ Name='ArduinoJson'; Source='ArduinoJson-7.4.2'; Header='src/ArduinoJson.h' },
    @{ Name='PubSubClient'; Source='pubsubclient-2.8'; Header='src/PubSubClient.h' }
)
foreach ($taskLibrary in $taskLibraries) {
    $taskTarget = Join-Path $taskLibraryRoot $taskLibrary.Name
    if (Test-Path -LiteralPath (Join-Path $taskTarget $taskLibrary.Header)) {
        Write-Host "$($taskLibrary.Name) ya disponible en el sketchbook del IDE."
        continue
    }
    if (Test-Path -LiteralPath $taskTarget) {
        throw "El destino $taskTarget existe pero falta el header; revisar sin sobrescribir."
    }
    $taskSource = Join-Path $taskRoot ".local/arduino-libraries/$($taskLibrary.Source)"
    if (!(Test-Path -LiteralPath (Join-Path $taskSource $taskLibrary.Header))) {
        throw "Falta la copia local de $($taskLibrary.Name); consultar embedded/README.md."
    }
    New-Item -ItemType Directory -Force -Path $taskLibraryRoot | Out-Null
    Copy-Item -LiteralPath $taskSource -Destination $taskTarget -Recurse
    Write-Host "$($taskLibrary.Name) instalada desde la copia local existente."
}

# Reutiliza core/bibliotecas existentes sin modificar la instalacion Arduino.
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$taskSourceRoot=Join-Path $env:USERPROFILE 'OneDrive/Documents/Arduino/libraries'
$taskLocalLibraries=Join-Path $taskRoot '.local/arduino-libraries'
foreach ($taskLibrary in @('BH1750','OneWire','DallasTemperature','Adafruit_ADS1X15','Adafruit_BusIO')) {
    $taskSource=Join-Path $taskSourceRoot $taskLibrary
    if (!(Test-Path $taskSource)) { throw "Biblioteca no encontrada: $taskLibrary. Ajustar ruta de sketchbook." }
    $taskTarget=Join-Path $taskLocalLibraries $taskLibrary
    New-Item -ItemType Directory -Force $taskTarget | Out-Null
    Get-ChildItem -LiteralPath $taskSource -File | Where-Object { $_.Extension -in @('.h','.cpp','.c','.S') -or $_.Name -eq 'library.properties' } | Copy-Item -Destination $taskTarget
    foreach ($taskSub in @('src','utility','util')) {
        $taskSourceSub=Join-Path $taskSource $taskSub
        if (Test-Path $taskSourceSub) { Copy-Item -LiteralPath $taskSourceSub -Destination $taskTarget -Recurse -Force }
    }
}
New-Item -ItemType Directory -Force (Join-Path $taskRoot '.local/arduino-user') | Out-Null
$taskData=($env:LOCALAPPDATA -replace '\\','/')+'/Arduino15'
$taskUser=($taskRoot -replace '\\','/')+'/.local/arduino-user'
@"
directories:
  data: $taskData
  user: $taskUser
  downloads: $taskData/staging
"@ | Set-Content (Join-Path $taskRoot '.local/arduino-cli.yaml')
Write-Host 'Configuracion local preparada. PubSubClient 2.8 y ArduinoJson 7.4.2 deben estar en .local/arduino-libraries.'

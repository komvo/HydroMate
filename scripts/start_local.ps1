param([switch]$WithLanMqtt)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
Set-Location $taskRoot

function Start-HydroProcess($Exe, $Arguments, $Directory, $LogBase) {
    $taskPidFile = "$LogBase.pid"
    if (Test-Path $taskPidFile) {
        $taskPid = [int](Get-Content $taskPidFile)
        $taskExisting = Get-CimInstance Win32_Process -Filter "ProcessId=$taskPid" -ErrorAction SilentlyContinue
        if ($taskExisting) {
            if ($taskExisting.ExecutablePath -ine [System.IO.Path]::GetFullPath($Exe)) {
                throw "El PID guardado pertenece a otro programa. Revisar $taskPidFile sin detener ese proceso."
            }
            Write-Host "Proceso existente: $LogBase (PID $taskPid)"
            return
        }
    }
    $taskProcess = Start-Process -FilePath $Exe -ArgumentList $Arguments -WorkingDirectory $Directory -WindowStyle Hidden -RedirectStandardOutput "$LogBase.out.log" -RedirectStandardError "$LogBase.err.log" -PassThru
    $taskProcess.Id | Set-Content $taskPidFile
    Write-Host "Iniciado: $LogBase (PID $($taskProcess.Id))"
}

# Reuse existing PostgreSQL and its volume; never create/reset a database here.
$taskMounts = docker inspect hydromate-postgres --format '{{json .Mounts}}' | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or !($taskMounts | Where-Object Destination -eq '/var/lib/postgresql/data')) {
    throw 'No se encontro el contenedor/volumen esperado. Revisar antes de continuar.'
}
docker start hydromate-postgres | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL no pudo arrancar.' }
$taskReady = $false
for ($taskAttempt=0; $taskAttempt -lt 20; $taskAttempt++) {
    docker exec hydromate-postgres pg_isready *> $null
    if ($LASTEXITCODE -eq 0) { $taskReady=$true; break }
    Start-Sleep -Milliseconds 500
}
if (!$taskReady) { throw 'PostgreSQL aun no acepta conexiones; revisar logs, sin recrear datos.' }
if (!(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-HydroProcess "$taskRoot/.local/php/php.exe" @('artisan','serve','--host=127.0.0.1','--port=8000','--no-reload') "$taskRoot/hydromate-backend" "$taskRoot/.local/backend-server"
} else { Write-Host 'Puerto 8000 ocupado: verificar que responde la API de HydroMate.' }

if ($WithLanMqtt) {
    if (!(Test-Path '.local/mqtt/mosquitto.conf') -or !(Test-Path '.local/mqtt/users.json')) {
        throw 'Falta configuracion privada MQTT. Seguir procedimiento-local.md.'
    }
    Start-HydroProcess 'C:/Program Files (x86)/Mosquitto/mosquitto.exe' @('-c',"$taskRoot/.local/mqtt/mosquitto.conf") $taskRoot "$taskRoot/.local/mqtt/broker"
    $taskUsers = Get-Content '.local/mqtt/users.json' -Raw | ConvertFrom-Json
    $taskOldUser = $env:MQTT_USERNAME
    $taskOldPassword = $env:MQTT_PASSWORD
    try {
        $env:MQTT_USERNAME = 'hydromate-bridge'
        $env:MQTT_PASSWORD = $taskUsers.'hydromate-bridge'
        Start-HydroProcess "$taskRoot/.local/mqtt-venv/Scripts/python.exe" @('-u','scripts/mqtt_bridge.py','--port','1884','--client-id','hydromate-lan-bridge','--state','.local/mqtt/lan-inbox.sqlite') $taskRoot "$taskRoot/.local/mqtt/bridge"
    } finally {
        $env:MQTT_USERNAME = $taskOldUser
        $env:MQTT_PASSWORD = $taskOldPassword
    }
}
Write-Host 'API: http://127.0.0.1:8000/api/measurements'
Write-Host 'Telefono USB: adb reverse tcp:8000 tcp:8000; no requiere exponer Laravel en LAN.'

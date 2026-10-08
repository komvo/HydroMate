param([string]$PcIp)
# Primera preparacion del banco; nunca regenera credenciales existentes.
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
Set-Location $taskRoot
$taskMqttDir=Join-Path $taskRoot '.local/mqtt'
if (Test-Path (Join-Path $taskMqttDir 'users.json')) {
    if (!(Test-Path (Join-Path $taskMqttDir 'mosquitto.conf'))) { throw 'Configuracion parcial: revisar manualmente sin regenerar secretos.' }
    Write-Host 'MQTT ya configurado; se conservan credenciales y configuracion.'
    return
}
$taskPrivateHeader=Join-Path $taskRoot 'embedded/HydroMateTelemetry/secrets.h'
if (Test-Path $taskPrivateHeader) { throw 'Existe secrets.h sin broker registrado: reconciliar configuracion, no sobrescribir.' }
if (!$PcIp) { $PcIp=(Get-NetIPAddress -InterfaceAlias Wi-Fi -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.*' }).IPAddress }
$taskParsed=[System.Net.IPAddress]::Parse($PcIp)
$taskBytes=$taskParsed.GetAddressBytes()
if ($taskBytes.Length -ne 4 -or !($taskBytes[0] -eq 10 -or ($taskBytes[0] -eq 172 -and $taskBytes[1] -ge 16 -and $taskBytes[1] -le 31) -or ($taskBytes[0] -eq 192 -and $taskBytes[1] -eq 168))) { throw 'Usar una IPv4 privada local.' }
if (!(Get-NetIPAddress -IPAddress $PcIp -ErrorAction SilentlyContinue)) { throw 'La IP no pertenece a esta PC.' }
$taskMosquitto='C:\Program Files (x86)\Mosquitto'
if (!(Test-Path (Join-Path $taskMosquitto 'mosquitto_passwd.exe'))) { throw 'Mosquitto no encontrado; ajustar ruta de instalacion.' }
New-Item -ItemType Directory -Force $taskMqttDir | Out-Null
$taskUsers=@{}
$taskRng=[System.Security.Cryptography.RandomNumberGenerator]::Create()
foreach ($taskUser in @('hydromate-device','hydromate-bridge','hydromate-test')) {
    $taskRandom=New-Object byte[] 24
    $taskRng.GetBytes($taskRandom)
    $taskUsers[$taskUser]=[BitConverter]::ToString($taskRandom).Replace('-','').ToLowerInvariant()
}
$taskRng.Dispose()
$taskUsers | ConvertTo-Json | Set-Content (Join-Path $taskMqttDir 'users.json')
$taskPasswordFile=Join-Path $taskMqttDir 'passwords'
$taskFirst=$true
foreach ($taskUser in @('hydromate-device','hydromate-bridge','hydromate-test')) {
    if ($taskFirst) { & "$taskMosquitto/mosquitto_passwd.exe" -b -c $taskPasswordFile $taskUser $taskUsers[$taskUser] }
    else { & "$taskMosquitto/mosquitto_passwd.exe" -b $taskPasswordFile $taskUser $taskUsers[$taskUser] }
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar password_file; revisar archivos privados.' }
    $taskFirst=$false
}
@'
user hydromate-device
topic write hydromate/hydromate-01/telemetry
topic read hydromate/hydromate-01/ack
user hydromate-bridge
topic read hydromate/+/telemetry
topic write hydromate/+/ack
user hydromate-test
topic readwrite hydromate/+/#
'@ | Set-Content (Join-Path $taskMqttDir 'acl')
$taskMqttPath=$taskMqttDir -replace '\\','/'
@"
listener 1884 127.0.0.1
listener 1884 $PcIp
allow_anonymous false
password_file $taskMqttPath/passwords
acl_file $taskMqttPath/acl
persistence true
persistence_location $taskMqttPath/
log_dest stdout
"@ | Set-Content (Join-Path $taskMqttDir 'mosquitto.conf')
$taskTemplate=Get-Content 'embedded/HydroMateTelemetry/secrets.example.h' -Raw
$taskTemplate=$taskTemplate.Replace('192.168.1.100',$PcIp).Replace('constexpr char MQTT_PASSWORD[] = "";',('constexpr char MQTT_PASSWORD[] = "'+$taskUsers['hydromate-device']+'";'))
[System.IO.File]::WriteAllText($taskPrivateHeader,$taskTemplate)
Write-Host 'Banco creado. Completar Wi-Fi en secrets.h privado; no imprimir ni publicar contraseñas.'
Write-Host 'No se cambia firewall/router ni se arranca Mosquitto desde este script.'

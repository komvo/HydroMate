# Ejecutar en PowerShell como administrador. Alcance autorizado: red Wi-Fi doméstica.
$ErrorActionPreference = 'Stop'
$taskIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$taskPrincipal = [Security.Principal.WindowsPrincipal]::new($taskIdentity)
if (!$taskPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Abrir PowerShell como administrador y ejecutar este archivo.'
}
$taskIp = (Get-NetIPAddress -InterfaceAlias Wi-Fi -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.*' }).IPAddress
if ($taskIp -ne '192.168.1.6') { throw 'La IP cambio. Actualizar broker/secrets/regla antes de continuar.' }
Set-NetConnectionProfile -InterfaceAlias Wi-Fi -NetworkCategory Private
if (!(Get-NetFirewallRule -Name HydroMate-MQTT-LAN -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name HydroMate-MQTT-LAN -DisplayName 'HydroMate MQTT banco LAN 1884' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 1884 -LocalAddress $taskIp -RemoteAddress LocalSubnet -Profile Private -Program 'C:\Program Files (x86)\Mosquitto\mosquitto.exe' | Out-Null
}
Get-NetConnectionProfile -InterfaceAlias Wi-Fi | Select-Object InterfaceAlias,NetworkCategory
Get-NetFirewallRule -Name HydroMate-MQTT-LAN | Select-Object Name,Enabled,Profile

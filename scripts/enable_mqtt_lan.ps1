# Ejecutar en PowerShell como administrador. Alcance autorizado: red Wi-Fi doméstica.
$ErrorActionPreference = 'Stop'
$taskIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$taskPrincipal = [Security.Principal.WindowsPrincipal]::new($taskIdentity)
if (!$taskPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Abrir PowerShell como administrador y ejecutar este archivo.'
}
$taskIp = (Get-NetIPAddress -InterfaceAlias Wi-Fi -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.*' }).IPAddress
if (@($taskIp).Count -ne 1 -or $taskIp -notmatch '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)') {
    throw 'Se requiere una sola direccion Wi-Fi IPv4 de banco privado RFC1918.'
}
if ((Get-NetConnectionProfile -InterfaceAlias Wi-Fi).NetworkCategory -ne 'Private') {
    throw 'La red no es Private. Verificar que sea la red domestica autorizada; este script no cambia perfiles globales.'
}
$taskRule = Get-NetFirewallRule -Name HydroMate-MQTT-LAN -ErrorAction SilentlyContinue
if ($taskRule) {
    $taskPort = $taskRule | Get-NetFirewallPortFilter
    $taskProgram = $taskRule | Get-NetFirewallApplicationFilter
    if ($taskPort.LocalPort -ne '1884' -or $taskPort.Protocol -ne 'TCP' -or
        $taskProgram.Program -ine 'C:\Program Files (x86)\Mosquitto\mosquitto.exe' -or
        $taskRule.Profile -ne 'Private' -or $taskRule.Action -ne 'Allow') {
        throw 'La regla HydroMate existente no coincide con el banco esperado; no se modifica.'
    }
    $taskRule | Get-NetFirewallAddressFilter | Set-NetFirewallAddressFilter -LocalAddress $taskIp -RemoteAddress LocalSubnet | Out-Null
}
if (!(Get-NetFirewallRule -Name HydroMate-MQTT-LAN -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name HydroMate-MQTT-LAN -DisplayName 'HydroMate MQTT banco LAN 1884' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 1884 -LocalAddress $taskIp -RemoteAddress LocalSubnet -Profile Private -Program 'C:\Program Files (x86)\Mosquitto\mosquitto.exe' | Out-Null
}
Get-NetConnectionProfile -InterfaceAlias Wi-Fi | Select-Object InterfaceAlias,NetworkCategory
Get-NetFirewallRule -Name HydroMate-MQTT-LAN | Select-Object Name,Enabled,Profile

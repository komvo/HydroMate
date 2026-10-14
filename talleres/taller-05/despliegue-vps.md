# Despliegue temporal de HydroMate en VPS compartida

**Procedimiento de acceso anterior reemplazado el 14/10/2026 por petición del
usuario:** esta tarea no tendrá SSH ni solicitará credenciales. El repositorio
se prepara para el ejecutor automático de main. Seguir [PRODUCTION](../../docs/PRODUCTION.md)
y `compose.production.yml`, siempre -p hydromate; recursos ajenos fuera de alcance.
Publicación vigente: [PUBLIC_ACCESS](../../docs/PUBLIC_ACCESS.md), hostname
hydromate-kevin.duckdns.org, HTTPS8443/MQTT TLS8884, deploy-hydromate/rootless.
No aplicar el inventario ni la propuesta de proxy compartido del antecedente.
Los pasos de acceso siguientes se conservan únicamente como antecedente.

Estado al 14/10/2026: usuario confirma OVHcloud, Ubuntu y alojamiento prestado
sin costo; el proyecto del compañero ya está alojado. HydroMate todavía no tiene
despliegue verificado. La versión exacta de Ubuntu y los servicios deben revisarse
antes de decidir instrucciones de instalación.

## Entrar desde Windows

No requiere instalar una aplicación. El panel OVHcloud se abre en navegador y
PowerShell ya dispone de OpenSSH. En panel, seleccionar VPS y localizar IPv4/IP
principal. El correo/contraseña del panel no son necesariamente usuario/contraseña
SSH. Obtener del administrador el acceso Ubuntu que corresponde a HydroMate.

```powershell
ssh USUARIO_SSH@IP_PUBLICA
```

Sustituir ambos nombres por los datos reales, sin introducir la contraseña en el
comando. Verificar huella en la primera conexión. Cuando aparezca `password:`,
escribir contraseña en terminal y Enter: no aparecen caracteres. Un prompt de
Ubuntu confirma inicio de sesión; `PS C:\Hydromate>` sigue siendo la PC.
No enviar contraseñas ni llaves al chat o al repositorio.

Si se escribió un correo como comando o como destino SSH, pulsar Ctrl+C y corregir.
`Permission denied` implica acceso rechazado; `Connection timed out` indica que
no se alcanzó el servicio, sin identificar por sí solo la causa. No modificar el
firewall compartido para resolverlo sin revisar acceso con su administrador.

## Inspección inicial sin cambios

En la sesión SSH ejecutar por separado:

```bash
cat /etc/os-release
id -un
uname -m
free -h
df -h /
ss -lnt
systemctl is-active nginx apache2 postgresql mosquitto docker
php -v
python3 --version
docker --version
```

La ausencia de un programa no autoriza instalarlo aún. Si Docker ya existe y el
usuario tiene permisos, listar solo nombres/estado/puertos, sin inspeccionar
variables del compañero:

```bash
docker ps --format '{{.Names}} {{.Status}} {{.Ports}}'
```

Conservar salida pertinente en privado; compartir versión Ubuntu, recursos,
puertos y nombres de servicios útiles. No imprimir `.env`, historial de comandos,
contraseñas, configuración privada ni datos de otras aplicaciones.

## Preparación después del inventario

| Capa | Trabajo mínimo | Cómo verificar |
|---|---|---|
| Separación | Directorio, cuenta, base y permisos propios; revisar disponibilidad de recursos y puertos. Reutilizar proxy existente si procede. | Aplicación del compañero responde antes/después; acceso cruzado impedido. |
| Runtime/API | PHP compatible con `composer.lock` (local 8.4.26; SETUP registra requisito >=8.4.1), extensiones y Composer; servidor web con raíz `hydromate-backend/public`. | `composer check-platform-reqs --no-dev`, servicio y `/up`, API responde JSON. |
| Configuración | `.env` privado, APP_DEBUG=false, clave propia y PostgreSQL propio. No copiar `.local` completa. | Configuración fuera de webroot y acceso restringido; errores sin trazas públicas. |
| PostgreSQL | Base/rol exclusivo y persistencia, respaldo previo si existe información propia. Aplicar solo las dos migraciones `measurements` necesarias por `--path`; no ejecutar fresh/reset. | Esquema v2 y UNIQUE; INSERT/SELECT; datos tras reinicio de servicio propio. |
| HTTPS | Dominio/subdominio disponible y certificado válido; acceso Android por HTTPS. Coordinar proxy compartido y puertos existentes. | Certificado/hostname verificados desde teléfono. No usar aceptación de certificado inválido. |
| Ingreso/API | Proteger escritura del bridge; no dejar POST abierto al público. Lectura protegida con mecanismo compatible con Android antes de exponer datos. | Solicitud sin autorización rechazada y cliente autorizado funcional. Implementación aún pendiente; no confundir Sanctum instalado con autenticación terminada. |
| MQTT | Mosquitto TLS, usuario por dispositivo y bridge, ACL para tópicos propios, certificado/CA válidos. PostgreSQL y API interna del bridge sin publicación innecesaria. | ESP32 conecta validando CA/hostname, publica y recibe `stored` tras INSERT. |
| Bridge | `scripts/mqtt_bridge.py` en venv con Paho, bandeja SQLite privada persistente; servicio propio con reinicio y logs. `--api`, `--host`, `--port`, `--ca` según instalación. | Una muestra MQTT produce fila en PostgreSQL; caída propia/reconexión conserva pendiente. |
| ESP32 | Editar `secrets.h` privado: broker real, MQTT_TLS=true, puerto TLS, CA, Wi-Fi y cuenta propia. Compilar y cargar. | Monitor serie Wi-Fi/MQTT/SAMPLE/STORED; diez nuevas secuencias. |
| Android | Más → conexión real → URL base `https://DOMINIO` y torre `hydromate-01`; salir de demo. | Inicio e Historial coinciden con datos de VPS; también carga/vacío/error. |

No instalar otro servidor en 80/443 a ciegas ni reiniciar/borrar contenedores del
compañero. Las configuraciones ejecutables se preparan al conocer el inventario;
esta guía es el procedimiento de trabajo, no evidencia de despliegue.

## Evidencia final

Guardar URL HTTPS de API, revisión del servicio propio, esquema y consulta con
diez filas físicas nuevas, registro de intentos/fallos, tiempo aproximado y
capturas Android. Video de 1–2 minutos sugerido: montaje real, cambio luz/flotador,
publicación, registro/API de VPS y actualización en Android. El video local
anterior no muestra nube. Usar nombres de archivos nuevos para conservar historia.

Desde la PC, una vez conectada la placa y validada la API HTTPS, capturar las diez
adquisiciones nuevas (sustituir puerto y dominio):

```powershell
& .local/mqtt-venv/Scripts/python.exe scripts/capture_sensor_flow.py --port COM3 --api https://DOMINIO --fresh-only --target 10 --duration 600 --output talleres/taller-05/pruebas/esp32-nube-nueva-ejecucion.json
```

`--fresh-only` excluye el pendiente RESTORED del conteo, pero conserva su evento
y confirmación. No borrar NVS para obtener secuencias consecutivas. El ensayo
requiere acceso de consulta compatible con el mecanismo de protección finalmente
configurado; la captura no demuestra por sí sola visualización en Android.

## Referencias técnicas

- [Despliegue Laravel](https://laravel.com/framework/docs/deployment): webroot public, permisos y configuración de producción.
- [Acceso SSH OVHcloud](https://support.us.ovhcloud.com/hc/en-us/articles/360000416484-How-to-get-started-with-SSH-connections): acceso al servidor desde OpenSSH y usuarios según sistema.

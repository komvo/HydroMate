# Arquitectura vigente de HydroMate

Consolidación documental 27/10/2026. Implementación y pruebas fechadas en STATUS.
Diseño académico vigente: [T8 Word](../Documentos%20PDC/T8_PDC_1288703.docx)
y [PDF](../Documentos%20PDC/T8_PDC_1288703.pdf). Decisiones: DECISIONS.md.

## Flujo implementado

Sensores → ESP32 → MQTT TLS8884 → Mosquitto → bridge Python/Paho → POST interno
Laravel → PostgreSQL → GET HTTPS9443 → Android. El bridge conserva bandeja SQLite;
no escribe directamente en PostgreSQL. Solo confirma stored tras persistencia o
comparación de un duplicado idéntico. MQTT QoS no sustituye esa confirmación.

ESP32 usa contrato v3, secuencia por torre, fecha de adquisición opcional y origen
por variable. Guarda un pendiente NVS; reenvía idéntico hasta stored. Sensores
inválidos/ausentes producen null, no cero ni valores simulados. TDS real A1;
EC independiente sin implementación. Detalles exactos: TELEMETRY_CONTRACT.md.

## Adquisición solicitada

Android crea UUID por POST limitado; Laravel guarda metadata efímera en caché de
archivos; bridge consulta ruta interna y publica commands/measure QoS1/no retained.
ESP32 valida UUID/vigencia, adquiere y responde por telemetría v3 con request:UUID.
Laravel solo satisface con adquisición correlacionada y persistida. No hay tablas
ni microservicios nuevos. GET automático cada 2 s solo en vistas Android visibles.
API.md describe rutas/estados; las limitaciones operativas no se infieren del diseño.

## Despliegue y separación

Docker rootless propio: Nginx público9443 → API8080, host loopback8081;
Mosquitto TLS8884 y listener1884 interno; PostgreSQL16 interno5432.
Red database interna solo para API/BD; application para API/broker/bridge/HTTPS.
Volúmenes propios de PostgreSQL, storage API, MQTT y bandeja bridge. No red host.
Android corre en teléfono; ESP32 por Wi-Fi2.4GHz. URL pública única mediante
HYDROMATE_APP_URL, perfiles desarrollo/producción separados, sin fallback demo.
Mosquitto2.0.22 usa imagen propia con configuración/ACL incorporadas, USER1883:1883
y binario /usr/local/bin/hydromate-mosquitto; secretos externos read-only.
PUBLIC_ACCESS.md y PRODUCTION.md contienen operación, certificados y guardas.

## Diseño seleccionado sin implementación completa

ESP32: control y seguridad locales, cuatro canales A/B/Up/Down, mezcla, límites,
reinicio seguro y cierre físico. No hay salidas de actuadores en el sketch actual.
Arduino-ESP32 se conserva y modulariza; tareas FreeRTOS cuando corresponda.
Laravel: usuarios/Sanctum y Policies por torre, perfiles, comandos y alertas.
FCM: entrega de avisos generados por Laravel; no mueve la BD a Firebase.
BLE: alta Wi-Fi con sesión segura; no camino alternativo de actuación.
hm-control-1: contrato de diseño separado, no endpoint implementado de actuación.

Los grupos no deben fusionar identidad de torres. No crear anticipadamente todas
las tablas de dominio ni declarar protecciones probadas sin ensayo físico.
Cualquier cambio a esta arquitectura se justifica en DECISIONS y en los contratos
correspondientes, conservando la decisión anterior como antecedente.

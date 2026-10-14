# Pruebas del Taller 5

Incremento 14/10 v3: `integracion-v3-sintetica-2026-10-14.json` verifica diez
mensajes MQTT TLS en Docker local aislado, duplicado, conflicto, 422 y GET;
TDS/EC null. `integracion-v1-http-2026-10-14.json` comprueba compatibilidad HTTP.
Android interpreta la respuesta exportada en prueba JVM, sin contarla como
física. Firmware cargado; usuario corrigió regla LAN como administrador.
Repetición `integracion-v3-fisica-local-2026-10-14.json` pasa diez adquisiciones
nuevas1501–1510, comparadas serial/ACK/API, cuatro variables reales y TDS/EC null.
`integracion-v3-recuperacion-fisica-2026-10-14.json` verifica pendiente1201 intacta
después del fallo; temperatura invalid/null legítima, no es adquisición nueva.
`latencia-v3-android-local-2026-10-14.json` verifica muestra1701 en pantalla:
7.57s desde fin de adquisición, incluidos Wi-Fi, arranque/ADB. Mediana hasta ACK
de las diez muestras404.5ms. No representa nube, polling ni calibración.
Capturas `android-v3-real-local*-2026-10-14.png` y video12s
`android-v3-real-local-2026-10-14.mp4` muestran Inicio real del banco.
Historial real observado tras toque manual del usuario:
`android-v3-historial-real-2026-10-14.png` y
`android-v3-historial-verificacion-2026-10-14.json`. Gráfica pH y lista20 registros;
fila visible1701 comparada en fecha/pH/temperatura/TDS con API. Snapshot de última
consulta, no transmisión continua de pantalla ni nube.
La marca de variables simuladas en desarrollo incluye TDS histórico de v2;
la lectura nueva mostrada es v3 con TDS no disponible. Producción filtra esas
filas históricas con `real_only=1`. No se borran ni reclasifican evidencias viejas.

`integracion-v3-recuperacion-local-2026-10-14.json`: pendiente durable sobrevive
API caída y reinicio de bridge; ACK/GET verificados, datos simulados.
`integracion-v3-verificacion-2026-10-14.json`: 25 pruebas backend/157 assertions,
27 Android sin omitidas, tres bridge, compilación/instalación y hashes; 90 filas
históricas conservadas. `integracion-v3-fisica-fallo-regla-lan-2026-10-14.json`
conserva el fallo físico actual, no se considera éxito ni evidencia de nube.

Guardar aquí las nuevas capturas y registros de las pruebas del taller.
Existe evidencia del recorrido físico local del 07/10. El recorrido con backend
en nube todavía está pendiente. Las pruebas históricas iniciales permanecen en
`docs/evidence/`; esta carpeta conserva el incremento físico del taller.

Cada prueba debe registrar fecha, configuración/commit, secuencia, origen de
variables, resultado esperado/observado, respuesta, registro de BD y tiempo.

Ensayos del 07/10: HTTP v1, MQTT sintético (incluye primer fallo), MQTT autenticado,
repetición tras reinicio Docker, validación backend/Android y esquema PostgreSQL.
Leer el campo scope y synthetic: diez filas PC no equivalen a diez lecturas reales.
`esp32-fisico-2026-10-07.json` conserva la primera captura física fallida:
una muestra serial y ninguna entrega confirmada. El usuario detectó que el SSID
original solo admitía 5 GHz y cambió el archivo privado a una red de 2.4 GHz.
Una repetición debe guardarse en otro archivo; no sobrescribir este resultado.
Repetición `esp32-fisico-24ghz-2026-10-07.json`: passed=true, diez mensajes
físicos verificados contra API; cuatro variables reales y TDS simulado. Cambio
de iluminación/flotador observado. Captura Android en
`android-sensores-reales-2026-10-07.png`; no contiene lecturas sintéticas de PC.
`android-historial-real-2026-10-07.png` y `android-consulta-local-2026-10-07.mp4`
completan evidencia de frontend local. Latencia: primer fallo y repetición 8.24 s
en archivos separados; incluye arranque/inspección ADB. Corte broker:
`esp32-reconexion-2026-10-07.json`, 901/902 verificadas y pendiente conservado.

Revisión 14/10: `verificacion-captura-2026-10-14.json` verifica solo software con
serie/API simuladas: modo --fresh-only excluye recuperadas, cuenta adquisición
nueva, mantiene compatibilidad y rechaza diferencia entre muestra/fila. No cuenta
como ensayo físico. Las diez entregas previas incluyen una restaurada + nueve
nuevas; para nube se solicitarán diez adquisiciones nuevas sin borrar NVS.

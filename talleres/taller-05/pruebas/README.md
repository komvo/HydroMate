# Pruebas del Taller 5

Guardar aquí las nuevas capturas y registros de las pruebas del taller.
Todavía no hay evidencia del recorrido físico completo. Las pruebas históricas
se enlazan desde el índice principal y permanecen en `docs/evidence/`.

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

# Alcance actualizado — backend antes de hardware

El usuario reemplazó la ruta Wokwi/Blade por API + PostgreSQL + Android mínimo,
y posteriormente ESP32 físico. No ejecutar la ruta histórica como requisito.
Paso 1 probado: 15 tests/79 assertions; smoke HTTP real con 11 filas sintéticas,
422 inválido, 409 duplicado, consultas por dispositivo y 404 sin datos.
Evidencias en docs/evidence; faltan volumen Docker, Android y sensores físicos.
No se realizaron pruebas de desconexión/recuperación de sensores ni calibración.

---
## Referencia histórica de la PoC anterior (reemplazada en prioridad)

# Prueba de concepto — plan reproducible pendiente de ejecución

Objetivo: cerrar Wokwi → MQTT → bridge → Laravel → PostgreSQL → API → frontend.
Estado actual y bloqueos: STATUS. No hay resultados de pruebas end-to-end aún.

## Entrada declarada
MicroPython/Wokwi: DS18B20 temperatura; entrada analógica luz; slider nivel;
potenciómetros pH y TDS. Lectura aproximada cada 30 s, publicación cada 5 min o
cambio significativo. sequence identifica transmisión; sample_number lectura;
reason explica envío. Parámetros de simulación descritos: ΔT 2 °C, luz 25%,
pH 0.5, TDS 150 ppm, cambio de estado de nivel. Verificar fuentes reales antes
de implementarlos; no son umbrales agronómicos definitivos.

Actualización 04/10: no trasladar el posible deep sleep de esta demostración al
controlador de bombas. Dirección vigente de energía y nuevos intervalos propuestos:
[ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md), D44–D47. Esta sección sigue siendo histórica.

```json
{"device_id":"hydromate-01","sequence":1,"sample_number":1,"reason":["startup"],"temperature_c":24.3,"light_pct":65.2,"light_state":"MEDIA","water_level_pct":82.4,"water_level_state":"LLENO","ph":6.2,"tds_ppm":650}
```

El bridge suscribe MQTT y envía ese JSON al POST de Laravel. Registrar dispositivo,
sequence, hora, evento, HTTP, resultado y latencia de la petición; nunca secretos.
No confundir latencia HTTP del bridge con latencia total sensor→pantalla.

## Casos de aceptación
| Caso | Acción | Resultado requerido |
|---|---|---|
| Válidos | 10 mensajes con secuencias nuevas para dispositivo de prueba | 10 respuestas 201, 10 filas verificadas, historial y última medición visibles |
| Inválido | ph=50 con secuencia nueva | 422 comprensible, ninguna fila nueva |
| Duplicado | Repetir device_id + sequence confirmado | 409, conteo sin cambio; cubrir carrera concurrente |
| Fallo temporal | Detener solo proceso Laravel de prueba o bridge propio | Error/timeout registrado; no declarar entrega exitosa |
| Recuperación | Restablecer proceso y reenviar según política | Recupera envío, no duplica registro ante respuesta perdida |
| UI vacía/error | Dispositivo sin datos y API inaccesible | Estados claros de vacío/carga/error, no datos inventados |
| Persistencia | Tras verificar volumen y coordinar reinicio del servicio | Registros confirmados siguen presentes |

Separar device_id de prueba del dispositivo real. Consultar secuencias existentes
antes de enviar. No limpiar measurements para facilitar la demostración.
Conservar evidencias en docs/evidence/: fecha, secuencia, status, latencia, resultado
de BD, logs y capturas. Identificar siempre sensor simulado vs servicio real.

Entregables por cerrar: código, README específico, diagrama, evidencias, problemas
encontrados, cronograma, presupuesto y matriz de riesgos. Los documentos existentes
apoyan los últimos tres; no inventar costos ni resultados. Confirmar criterio
académico de simulación frente al requisito original de entrada física.

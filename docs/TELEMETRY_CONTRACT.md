# Contrato de telemetría v1 — 2026-09-30

Formato canónico del productor y referencia para la app. Compatible con el esquema
existente; no cambia tablas ni endpoints. v1 es versión documental, no un campo
message_version aceptado/persistido actualmente. Implementación firmware pendiente.

## Flujo y representación
ESP32 físico → MQTT → integración/bridge → POST /api/measurements → PostgreSQL.
Android consulta GET /api/measurements y /api/measurements/latest con device_id.
Por ahora solo hay pruebas HTTP, sin firmware ni MQTT conectado. El bridge deberá
conservar el objeto original: no renumerar, cambiar unidad ni completar sensores.
JSON UTF-8, valores numéricos como números (no cadenas), decimales con punto.
Content-Type y Accept: application/json. No incluir credenciales en la telemetría.

| Campo | Tipo canónico / unidad | Obligatorio y límites actuales |
|---|---|---|
| device_id | string, identidad estable de la torre | Sí, no vacío, ≤64 caracteres |
| sequence | entero, identificador del mensaje | Sí, 1–9223372036854775807 |
| sample_number | entero, contador de adquisición | No; null o entero positivo hasta bigint |
| reason | lista de cadenas, motivos de transmisión | No; null o hasta 10 cadenas no vacías de ≤64 caracteres |
| temperature_c | número, °C | Sí, 0–50 |
| light_pct | número, porcentaje relativo | Sí, 0–100; NO lux ni PAR |
| light_state | string | Sí: BAJA, MEDIA, ALTA |
| water_level_pct | número, porcentaje relativo | Sí, 0–100; NO litros |
| water_level_state | string | Sí: VACIO, MEDIO, LLENO |
| ph | número, pH sin unidad | Sí, 0–14 |
| tds_ppm | número, ppm | Sí, 0–1000; NO EC en mS/cm |

Estos rangos son validación del prototipo, no objetivos del cultivo. No recortar
un valor real fuera de rango para conseguir un 201. Si el sensor necesita otro
rango, acordar cambio de contrato y probarlo antes de conectarlo.
Enviar como máximo dos decimales para evitar redondeo implícito del almacenamiento.
El servidor acepta algunas coerciones numéricas heredadas; el productor no debe
depender de ellas. Android debe tolerar enteros o decimales para campos numéricos
y usar Long para id/sequence/sample_number, no Int de 32 bits.

## Identidad y datos sintéticos
Asignar a cada torre un device_id estable, por ejemplo hydromate-01, antes de su
primera transmisión. No cambiarlo al reiniciar; no es un token ni autentica nada.
Reservar el prefijo test- y reason=["synthetic_test"] para datos de prueba.
Fixtures en hydromate-backend/tests/Fixtures/telemetry son exclusivamente sintéticas.
La API actual no impone esa convención ni valida autenticidad; la app mostrará
"Datos de prueba" para esos dispositivos y permitirá seleccionar el dispositivo.

## Secuencia, reinicios y entrega (regla seleccionada; firmware aún pendiente)
Una adquisición que genere mensaje nuevo recibe una sequence nueva. Un reintento
conserva device_id, sequence y todos los valores originales. sample_number cuenta
adquisiciones y no se usa para deduplicar; puede reiniciarse o no enviarse.
Se permiten huecos en sequence. El contador de transmisión no vuelve a 1 tras
reiniciar el mismo dispositivo. Para firmware: reservar rangos en almacenamiento
persistente antes de usarlos; al reiniciar saltar el rango previamente reservado.
Ejemplo conceptual: guardar próximo límite 101 antes de emitir 1–100; después de
reinicio reservar el siguiente rango y emitir desde 101. Tamaño, escritura atómica
y cola persistente deben implementarse/probarse en firmware, no se afirman hechos.
Si no puede guardar la reserva, no publicar con identidad/secuencia reutilizadas.
Si se borra la memoria persistente, detener envío y reconciliar el contador antes
de retomar esa identidad. No usar millis() ni hora del reloj como contador persistente.

| Resultado HTTP | Interpretación del productor/bridge |
|---|---|
| 201 | Persistencia confirmada; retirar ese mensaje de pendientes |
| 409 | La pareja ya existe; no crear otra sequence para evadir el conflicto |
| 422 | Error de contrato; registrar error, corregir origen, no reintentar ciegamente |
| timeout / conexión / 5xx | Resultado incierto; reintentar MISMO objeto con espera creciente acotada |

Un 409 no demuestra igualdad del contenido. Solo puede tratarse como reentrega
confirmada cuando se sabe que el objeto es idéntico a un envío previo; en otro
caso registrar conflicto y detener esa entrega para revisión. La API conserva la
primera fila y no sobrescribe sus valores. QoS MQTT por sí solo no confirma INSERT.
Política de cola, duración/retención y calendario de reintentos: próximo incremento
de integración, no implementados por este documento.

## Sensores desconectados o todavía no instalados
v1 actual exige todos los valores físicos. null, campo omitido o fuera de rango
produce 422 y no guarda una medición parcial. No reutilizar una lectura antigua
como nueva ni sustituir por 0. Un cero solo significa una lectura real válida.
El flotador físico no mide porcentaje de llenado y BH1750 entrega otra magnitud:
no atribuirles resolución/calibración que no tienen. Antes de conectar hardware,
definir representación de nivel discreto y luz real. Mantener esos cambios y
telemetría parcial/quality como evolución explícita, no conversiones inventadas.
La app puede desarrollarse ahora con fixtures completos e identificados.

## Tiempo y visualización
created_at/updated_at los asigna Laravel: son hora de recepción/persistencia, no
hora de adquisición. Las respuestas JSON usan fecha ISO-8601; Android la convierte
a zona local. No enviar timestamp/measured_at esperando que hoy se almacenen.
Con una cola y entrega tardía, latest significa última recepción, no lectura más
reciente tomada. No etiquetar datos como "en vivo" solo porque el GET respondió.
Mostrar "Recibido a...", identificación de torre y estado sin datos/errores.
La cadencia y el umbral de dato antiguo se decidirán con firmware; no confundir
respuesta API saludable con sensor o dispositivo conectado.

Propuesta de ensayo documentada el 04/10 en [ENERGY_OPTIMIZATION.md](ENERGY_OPTIMIZATION.md):
adquisición 5 s, publicación estable 300 s y prueba temporal 30 s, más eventos.
No cambia este contrato ni impone tiempos físicos. Medidas parciales, alarmas sin
valores completos, lotes y hora de adquisición requieren ampliación explícita.
La integración de cola tardía deberá resolver su antigüedad antes de presentarla
como estado actual; no sustituir campos ausentes ni convertir agregados en muestras.

## Ejemplos y comprobación
- valid.json → 201; repetir → 409.
- invalid-ph.json (pH 50) → 422.
- unavailable-sensor.json (pH null) → 422, sin inventar lectura.
Estos fixtures se prueban mediante PHPUnit en SQLite en memoria, sin tocar
PostgreSQL real. El contrato de respuesta REST está en API.md.

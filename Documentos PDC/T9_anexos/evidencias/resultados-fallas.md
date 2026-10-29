# Resultados de fallas (observados en Proteus 8.13, 28/10/2026)

Condiciones comunes: MCU a 16 MHz (`firmware-sim/build-16mhz`), F2 = 4 A como ajuste temporal (el modelo FUSE de Proteus no tiene retardo), SW1 (orden de bomba) cerrado y SW6 (flotador) cerrado = agua, salvo que se indique otra cosa.

## F7 — pH Up y pH Down ordenados a la vez
- Configuración: SW3 (ORD_UP) y SW4 (ORD_DN) cerrados (STATE=1).
- Terminal (t ≈ 2.08 s): `T=23.5 pH=7.09 (1.251 V) TDS=773 (1.788 V) NIVEL=OK BOMBA=ON A=OFF B=OFF UP=OFF DOWN=OFF CONFLICTO ALARMA=SI`.
- Sondas en las compuertas de Q4 (UP) y Q5 (DOWN): ≈ 0 V (del orden de 1e-10 V); ninguno de los dos se activa (`F7_parcial_UP_DOWN_gates.jpg`).
- Captura: `F7_conflicto_UP_DOWN.jpg`.
- Nota: el interbloqueo UP/DOWN lo hace solo el firmware; la compuerta 74HCT02 solo interbloquea con NIVEL.

## F2 — Sensor fuera de rango (pH a 5 V)
- Configuración: RV1 (sensor pH equivalente) al 100 % → 5 V antes de R1 (1 kΩ); clamp D2 BAT54 hacia +3V3. SW3/SW4 ya abiertos.
- Terminal (t ≈ 2.48 s): `T=23.5 pH=INVALIDO (3.486 V) TDS=773 (1.788 V) NIVEL=OK BOMBA=ON ... ALARMA=SI` (dos lecturas iguales).
- Sonda en AIN0 del ADS1015: ≈ 3.49 V (el clamp limita la entrada a ≈ VDD + Vf del BAT54; no llega a 5 V). La hoja de datos del ADS1115 indica VDD + 0.3 V como máximo absoluto; 3.49 V lo supera por ≈ 0.19 V, pero la corriente queda limitada por R1 (≈ (5 − 3.49)/1 kΩ ≈ 1.5 mA, cálculo). Observación de diseño: un clamp Schottky de menor Vf o un divisor como el de TDS dejaría margen.
- El firmware marca el pH como inválido (fuera de 0.05–3.3 V), no inventa un valor y enciende la alarma.
- Captura: `F2_pH_5V_clamp_invalido.jpg`.

## F4 — Reinicio del microcontrolador
- Intento 1: SW7 lleva RST (PC6) a GND (STATE=1). La sonda en RST marca ≈ 3.6 µV, pero el modelo ATmega328P de Proteus **sigue ejecutando** el firmware (la terminal imprime el banner). No sirvió para demostrar el reset: es una limitación del modelo o de la configuración, no un resultado del circuito. Captura: `F4a_RST_0V_modelo_sigue_ejecutando.jpg`.
- Intento 2 (descartado): excluir el MCU de la simulación también elimina el riel +3V3, que en esta simulación lo crea el pin oculto VCC del MCU. Las pull-ups quedan sin alimentación, la salida NOR sube a ≈ 2.5 V (Vgate 2.47 V) y la bomba gira. Es un artefacto del modelo, no un resultado válido. Captura: `F4b_MCU_excluido_sin_riel_3V3_bomba_ON.jpg`.
- Intento 3 (equivalente usado): firmware mínimo `setup(){} loop(){}`, que no configura ningún pin; todos quedan como entradas de alta impedancia, igual que durante el reset de un AVR. Con SW1 (orden de bomba) y SW6 (agua) cerrados: salida NOR ≈ 0 V (4.9e-14 V), Vgate ≈ 0 V (−1e-12 V), Vdrenador = 23.87 V; la bomba no gira. Las pull-ups de 10 kΩ mantienen BOMBA_N en alto, así que la NOR entrega 0 y el pull-down de 10 kΩ mantiene el IRLZ44N apagado. Captura: `F4_pines_alta_impedancia_bomba_OFF.jpg`.
- Pendiente físico: medir el comportamiento real del ESP32 durante el arranque (los GPIO tienen estados de arranque propios).

## F5 — Sin diodo flyback (D6 excluido)
- Configuración: D6 excluido de la simulación; ADS1015 excluido para que la simulación corra rápida (pH/TDS aparecen como INVALIDO/nan, sin relación con esta prueba). En la sonda VD_BOMBA se definió un *Real Time Breakpoint* analógico: detener si VD > 30 V, armado a partir de t = 0.5 s. La bomba arranca con SW1 cerrado; en t ≈ 2.17 s se abre SW1 durante la simulación.
- Observado sin D6: el breakpoint se disparó en t = 2.17337 s con **VD = 44.48 V** (Vgate = 2.23 V, bajando). El drenador superó los 24 V de alimentación al cortar la bomba. El valor es el del instante del disparo, no el pico máximo; el pico no se midió. A t = 2.445 s, VD = 11.5 V y Vgate ≈ 0 V, con el motor girando por inercia. Capturas: `F5a_sin_flyback_pico_VD_44V.jpg`, `F5b_sin_flyback_despues.jpg`.
- Comparación con D6 incluido (mismo procedimiento): la bomba se apaga (BOMBA=OFF) y el breakpoint de 30 V **no se dispara**; a t = 2.176 s, VD = 14.4 V. Captura: `F5c_con_flyback_sin_pico.jpg`.
- No se usó la pantalla del osciloscopio para esta falla: el disparo de un DSO en tiempo real no es práctico con la simulación tan lenta. El breakpoint analógico registra el cruce de umbral con su valor exacto.
- Limitación: el modelo MOTOR-DC (7.7 Ω, 10 mH) no representa la bomba brushless real, que tiene su propia electrónica, y no se modela la avalancha del IRLZ44N.

## Estado final del proyecto (tras las fallas)
- Valores normales restaurados: F2 = 2 A; SW1 a SW5 abiertos (STATE=0); SW6 cerrado (STATE=1, con agua); SW7 abierto; RV1 POS=25.4 (1.251 V) y RV2 POS=80 (1.788 V); D6 y ADS1015 incluidos en la simulación; breakpoint de VD_BOMBA desactivado; firmware `build-16mhz`.
- Al simular con F2 = 2 A y la bomba ordenada, el fusible se funde en el arranque, porque el modelo no tiene retardo (ver N3a).
- Esquemático exportado a `Documentos PDC/T9_anexos/hydromate-esquematico.pdf` (las 2 hojas, en color).

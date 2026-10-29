# Práctica Proteus — propuesta de circuito y simulaciones

Estado: **propuesta** (27/10/2026). No hay archivo Proteus, simulación ni medición
realizada. Valores marcados como *estimado* o *supuesto* deben confirmarse antes
de entregar; ningún resultado de esta hoja es observado.

## 0. Datos de partida

| Tipo | Dato | Fuente |
|---|---|---|
| Confirmado | ESP32 DevKit; DS18B20 GPIO4; flotador GPIO27 `INPUT_PULLUP`, LOW = agua; I²C SDA21/SCL22; ADS1115 0x48 (pH A0 ±6.144 V, TDS A1 ±4.096 V); BH1750 | `embedded/HydroMateTelemetry/` |
| Confirmado | TDS SEN0244 0–2.3 V (firmware rechaza >2.3 V o >1000 ppm); pH `= −5.579·V + 14.066`, válido 0.05–3.3 V (constantes históricas, sin calibración nueva) | firmware |
| Confirmado (compra) | Fuente 24 V/5 A, 2× XL4015, MOSFET dual Noyito, pH PH014, flotador, bomba 24 V/25 W | presupuesto T5 |
| Preliminar | Bomba GPIO25, iluminación 26, A/B 13/14, pH Up/Down 18/19, alarma 23, TDS enable 32 | diagramas 14/10 |
| Pendiente | Salidas de los XL4015; alimentación 3.3/5 V de módulos; pull-up del DS18B20; mecanismo de dosificación; corriente de arranque de la bomba | — |

**Antes de dibujar:** confirmar los cinco pendientes. Mientras tanto se usa el
*supuesto* XL4015 #1 = 5 V lógica; XL4015 #2 = reserva para dosificación.

## 1. Estructura del esquemático (hojas)

Usar etiquetas de red (`+24V`, `+5V`, `+3V3`, `GND_P`, `GND_L`, `SDA`, `SCL`,
`PH_A0`, `TDS_A1`, `T_1W`, `NIVEL`, `BOMBA_EN`, …) y conectores J1…Jn con el
mismo nombre que el cableado físico. Cada componente con referencia y valor.

### Hoja 1 — Alimentación y protecciones
`J1 24 V` → **F1** fusible principal → **D1** protección de polaridad (Schottky
o P-MOSFET) → **TVS1** en el bus 24 V → **C bulk** (470 µF/35 V) →
- **U1 XL4015 → +5 V** (ESP32 VIN, módulos sensores si se confirman a 5 V).
- **U2 XL4015 → V_DOS** (tensión de dosificación pendiente; si no se define, se
  deja documentada y sin carga).
- **+3V3**: regulador LDO del DevKit (AMS1117-3.3 o equivalente en Proteus).

Puntos de prueba TP1 (+24 V), TP2 (+5 V), TP3 (+3V3), con voltímetro DC y
amperímetro en serie en cada rama.

### Hoja 2 — Etapa lógica
ESP32 no simulable de forma nativa (verificar versión instalada). Propuesta:
- **Microcontrolador sustituto** ATmega328P/Arduino alimentado a **3.3 V** para
  conservar niveles lógicos del ESP32, con un firmware *didáctico de simulación*
  (no es el firmware del proyecto ni el controlador final): lee sensores, envía
  valores por TERMINAL VIRTUAL y aplica el interbloqueo de nivel bajo.
- Tabla de equivalencia de pines ESP32 ↔ sustituto en la hoja.
- Si el equipo prefiere no programar: ESP32 como bloque (símbolo) y las salidas
  manejadas con LOGICSTATE/generadores; se pierde la demostración de lógica.

### Hoja 3 — Entradas (sensores)
| Ref. | Elemento | Modelo en Proteus | Acondicionamiento propuesto |
|---|---|---|---|
| U3 | ADS1115 | modelo si existe; si no, ADC del sustituto (documentar 10 vs 16 bits) | pull-ups I²C 4.7 kΩ a +3V3 (revisar si los módulos ya los traen) |
| SEN1 | Módulo TDS V1.0 | **dispositivo propio** (VCC, GND, A) con potenciómetro/fuente 0–2.3 V | R serie 1 kΩ + clamp Schottky a VDD del ADS1115 |
| SEN2 | Sonda pH + PH014 | **dispositivo propio** (V+, G, Po) con potenciómetro | igual que TDS; crítico si el módulo va a 5 V y el ADS1115 a 3.3 V |
| SEN3 | DS18B20 | modelo nativo | pull-up 4.7 kΩ a +3V3 |
| SW1 | Flotador | interruptor a GND | pull-up (interna o 10 kΩ externa) + 100 nF opcional |
| U4 | BH1750 | modelo si existe; si no, se omite y se documenta | en bus I²C |

### Hoja 4 — Salidas y potencia
| Canal | Driver en Proteus (equivalente de D4184 del Noyito) | Protección |
|---|---|---|
| Bomba recirculación 24 V/25 W (GPIO25 prel.) | MOSFET logic-level (p. ej. IRLZ44N) | R gate 100 Ω, pull-down 10 kΩ, diodo flyback, F2 |
| A / B / pH Up / pH Down | mismo driver, **carga genérica** (mecanismo pendiente) | igual; interbloqueo Up/Down |
| Alarma (GPIO23 prel.) | transistor NPN + buzzer/LED | R base |
| Interbloqueo de nivel | flotador en serie con la habilitación de la bomba (compuerta AND o transistor) | independiente del firmware |

## 2. Cálculos a incluir (estimados, no mediciones)

**Consumo lógico en +5 V** (valores típicos de hoja de datos; PH014 sin hoja → supuesto):
| Carga | Típico | Diseño |
|---|---|---|
| ESP32 Wi-Fi | 80–120 mA (picos TX ~250–500 mA) | 500 mA |
| TDS SEN0244 | 3–6 mA | 6 mA |
| pH PH014 (supuesto) | ~10 mA | 20 mA |
| ADS1115, BH1750, DS18B20 | <2 mA | 2 mA |
| LEDs/alarma | ~5 mA | 20 mA |
| **Total** | ~0.2 A | **≈0.55 A → 2.75 W** |

En 24 V con η≈85 %: 2.75 / 0.85 / 24 ≈ **0.13 A**.

**Bomba:** 25 W / 24 V ≈ **1.04 A** nominal. Arranque *supuesto* 3× ≈ 3.1 A
(no medido; el motor de Proteus servirá como estimación, no como dato).

**Capacidad de fuente:** régimen bomba + lógica ≈ 1.2 A; usando 80 % de 5 A = 4 A
quedan ≈ 2.8 A para dosificación (una salida a la vez) y transitorios. Recalcular
cuando se conozca el actuador de dosificación.

**Justificaciones:**
- Buck en lugar de lineal: 24→5 V a 0.55 A disiparía (24−5)·0.55 ≈ **10.5 W** en
  un regulador lineal; un buck ≈85 % pierde ≈0.5 W.
- XL4015: Vout = 1.25·(1 + R2/R1); 5 V → R2/R1 = 3 (p. ej. 1 kΩ/3 kΩ o trimmer).
- LDO 3.3 V: (5−3.3)·0.3 A ≈ 0.5 W, aceptable.
- Gate 100 Ω limita pico de carga; pull-down 10 kΩ asegura bomba **apagada
  durante reinicio** (GPIO flotante).
- Pull-ups 4.7 kΩ para 1-Wire e I²C (valores estándar de hoja de datos).
- LED: R = (3.3 − 2.0) / 2 mA ≈ 680 Ω.
- Fusibles (propuesta): F1 3.15 A retardado; F2 2 A retardado en rama bomba.
- R serie 1 kΩ + clamp en entradas del ADS1115: límite VDD + 0.3 V de su hoja.

## 3. Simulaciones

Instrumentos: voltímetro/amperímetro DC, osciloscopio, TERMINAL VIRTUAL,
analizador I²C (si hay ADS1115/BH1750), gráfica analógica para transitorios.

### Funcionamiento normal
| ID | Escenario | Medición esperada a reportar |
|---|---|---|
| N1 | Alimentación con carga de diseño | +24/+5/+3V3 y corriente por rama |
| N2 | Sensores en valores reales de referencia: pH 1.27 V (≈7), TDS 1.78 V (≈770 ppm a 23.5 °C, lectura real del 21/10), DS18B20 23.5 °C, flotador con agua | valores en terminal; tensión en A0/A1 |
| N3 | Bomba encendida | Vgate, Vdrenador y ≈1.04 A en osciloscopio/amperímetro |

### Condición límite o falla (elegir al menos una; recomendadas F1 y F2)
| ID | Falla | Qué debe demostrarse |
|---|---|---|
| **F1** | Nivel bajo (flotador abierto) con bomba ordenada | bomba inhibida por firmware **y** por interbloqueo físico |
| **F2** | Sensor fuera de rango / desconectado (TDS >2.3 V o 0 V; pH a 5 V) | clamp protege el ADS1115; lectura marcada inválida, sin dato inventado |
| F3 | Rotor bloqueado / sobrecorriente | corriente sube y el fusible abre |
| F4 | Reinicio del microcontrolador | pull-down mantiene bomba apagada |
| F5 | Sin diodo flyback | pico en drenador visto en osciloscopio |
| F6 | Caída de 24 V | margen del buck y punto de pérdida de +5 V |
| F7 | pH Up y Down ordenados a la vez | solo uno se activa |

## 4. Diferencias simulación vs. circuito físico (base para el reporte)
- Sondas TDS/pH reemplazadas por tensiones; no hay química, deriva ni ruido real.
- ESP32 reemplazado por sustituto o bloque: otra CPU, ADC y temporización; sin Wi-Fi/MQTT.
- ADS1115/BH1750 posiblemente sin modelo.
- XL4015 y D4184 modelados con equivalentes; la bomba con motor DC o carga R-L
  aunque sea brushless con electrónica interna.
- Corriente de arranque, eficiencia y consumo no medidos físicamente.
- Nube, backend, BD y Android fuera de alcance (permitido por la práctica).

## 5. Entregables y reparto sugerido
1. `hydromate.pdsprj` (editable) y PDF del esquemático por hoja.
2. Dispositivos propios TDS/pH guardados en la librería del proyecto.
3. Firmware didáctico de simulación (si se usa sustituto), separado de `embedded/`.
4. Capturas de N1–N3 y de las fallas elegidas con instrumentos visibles.
5. Reporte: cálculos, justificaciones, lista de componentes, resultados y §4.

Sugerencia: persona 1 hojas 1 y 4 + cálculos; persona 2 hoja 3 + dispositivos
propios; persona 3 hoja 2 + firmware didáctico; todos, simulaciones y reporte.

## 6. Verificar en la versión de Proteus instalada
ESP32, ADS1115, BH1750, XL4015/LM2596, AMS1117, FUSE animado, MOTOR-DC con
parámetros, IRLZ44N, generador de archivo (para repetir datos reales de TDS).

# Práctica Proteus — circuito electrónico y simulación de HydroMate

Proteus 8.13 Professional. Proyecto editable: [`proteus/hydromate.pdsprj`](proteus/hydromate.pdsprj)
(2 hojas). Esquemático en PDF: [`hydromate-esquematico.pdf`](hydromate-esquematico.pdf).
Capturas: [`evidencias/`](evidencias/). Propuesta de diseño: [`PROPUESTA.md`](PROPUESTA.md).

Autor: Kevin Osmar Valdez Meza · Revisión 1.0.

Todos los resultados de este documento se **observaron en simulación**; no hay mediciones del
circuito físico. Los valores marcados como *supuesto* deben confirmarse con el hardware.

**Cómo leer los entregables.** El PDF documenta **solo el circuito**. Fuera de una simulación, los
instrumentos virtuales que aparecen en él muestran `+88.8`, que es su marcador y no una medición.
Los **resultados** son las capturas de `evidencias/`, tomadas con la simulación en marcha, y las
tablas de la §5.

## 1. Cumplimiento de requisitos

| Requisito | Dónde |
|---|---|
| Archivo editable / PDF | `proteus/hydromate.pdsprj`, `hydromate-esquematico.pdf` (solo el circuito) |
| Componentes, señales y conectores identificados | etiquetas de red (§2) y lista (§4) |
| Etapa de alimentación, etapa lógica, E/S críticas, protecciones | §2 |
| Consumo estimado y capacidad de la fuente | §3.1 |
| Justificación de resistencias, reguladores y convertidores | §3.2 |
| Lista actualizada de componentes | §4 |
| Simulación normal / condición límite o falla | §5 |
| Instrumentos virtuales | voltímetros y amperímetros DC, osciloscopio, terminal virtual, depurador I²C |
| Explicación de resultados / diferencias con el circuito físico | §5, §6 |

## 2. Estructura del circuito

**Hoja 1 — alimentación, lógica y sensores**
- **Alimentación.** Fuente de 24 V (equivalente de la fuente de 24 V / 5 A) → F1 de 3.15 A → D1 10TQ045
  (Schottky, protección contra polaridad invertida) → zener 1N4751A de 30 V (función de TVS) → C de 470 µF.
  El riel +5V representa al XL4015 #1. Una fuente de 12 V representa al XL4015 #2, que alimenta la
  dosificación (*supuesto*). U3 LM1117-3.3 entrega `3V3_LDO`.
- **Separación de las redes `+3V3` y `3V3_LDO` (solo en la simulación).** Proteus crea `+3V3` como
  un riel ideal a partir del pin VCC oculto del ATmega328P; ese riel alimenta el MCU, las
  pull-ups de las salidas y los clamps de las entradas analógicas. El LM1117 entrega `3V3_LDO` sobre una carga de prueba de 11 Ω, con la que se
  comprobó su regulación (3.30 V en N1). Al principio las dos redes estaban unidas y la simulación se
  detenía en ≈ 1 s, porque una fuente ideal y la salida de un regulador quedaban en paralelo; por eso
  se separaron. En consecuencia, **el dibujo no demuestra que el LM1117 alimente toda la lógica**:
  solo verifica el regulador por separado. En el circuito físico hay una sola red de 3.3 V, salida
  del regulador del DevKit ESP32, que alimenta toda la lógica. El consumo de la lógica (§3.1) se
  calculó y no se midió.
- **Lógica.** ATmega328P con el firmware didáctico `firmware-sim/` (sustituye al ESP32). La terminal virtual
  va conectada a TX a 9600 baudios.
- **Sensores.**
  - ADS1015 en 0x48 (equivalente del ADS1115), con pull-ups I²C de 4.7 kΩ.
  - **pH** en A0: RV1 (0–5 V) → 1 kΩ en serie → clamp BAT54.
  - **TDS** en A1: RV2 → divisor de 4.3 kΩ / 3.6 kΩ → 1 kΩ en serie → BAT54.
  - DS18B20 (`T_1W`) con pull-up de 4.7 kΩ.
- **Alarma.** LED con resistencia de 680 Ω. Reinicio con SW7 y R30 de 10 kΩ.

**Hoja 2 — salidas y potencia**

Hay cinco canales: bomba, A, B, pH Up y pH Down. Cada uno tiene:
- salida del MCU activa en bajo, con pull-up de 10 kΩ;
- una compuerta 74HCT02 (U7 A–D, U8 A) cuya otra entrada es `NIVEL`;
- resistencia de compuerta de 100 Ω y pull-down de 10 kΩ;
- MOSFET IRLZ44N;
- diodo de rueda libre 1N4007.

Cargas: la bomba M1 es un MOTOR-DC de 24 V protegido por F2; los canales de dosificación usan cargas
de 24 Ω a 12 V (*supuesto*). Las órdenes se dan con interruptores SW-SPST y el flotador es otro
SW-SPST conectado a GND.

**Equivalencias señaladas sobre el dibujo**

| En el esquemático | Representa |
|---|---|
| RV1 | sonda de pH + módulo PH014 |
| RV2 (+ divisor) | módulo TDS Meter V1.0 / SEN0244 |
| ATmega328P | ESP32 DevKit |
| ADS1015 | ADS1115 |
| riel +5V | XL4015 #1 |
| fuente de 12 V | XL4015 #2 (*supuesto*) |
| MOTOR-DC M1 / resistencias de 24 Ω | bomba de 24 V / 25 W / mecanismos de dosificación |
| SW1–SW5 / SW6 | órdenes MQTT / flotador |

**Señales principales**

| Señal | Origen → destino | Equivalente en el ESP32 |
|---|---|---|
| `T_1W` | DS18B20 → PD4 | GPIO4 |
| `NIVEL` | flotador → PD7 y entradas del 74HCT02 (LOW = agua) | GPIO27 |
| `SDA`/`SCL` | ADS1015 ↔ PC4/PC5 | GPIO21/22 |
| `PH_A0`, `TDS_A1` | módulos → ADS1015 A0/A1 | ADS1115 A0/A1 |
| `BOMBA_N`, `A_N`, `B_N`, `UP_N`, `DOWN_N` | PB1, PB2, PB3, PD5, PD6 → 74HCT02 | GPIO25, 13, 14, 18, 19 (preliminares) |
| `ALARMA` | PB0 → LED | GPIO23 (preliminar) |
| Órdenes | SW → PC0–PC3, PB4 | por MQTT en el sistema real |

**Interbloqueo físico.** Cada compuerta calcula `Gate = NOR(NIVEL, ORDEN_N)`, así que el MOSFET solo
conduce cuando hay agua **y** el MCU da la orden. Si falta agua, el canal se apaga aunque el firmware
falle. Mientras el MCU se reinicia, sus pines quedan en alta impedancia; la pull-up deja `ORDEN_N` en
alto y el canal queda apagado. El 74HCT02 (umbrales TTL, VIH = 2 V) acepta la lógica de 3.3 V y
entrega 5 V a la compuerta, con lo que también funciona como adaptador de nivel.

## 3. Cálculos y justificación

### 3.1 Consumo y capacidad de la fuente (estimados)

Las corrientes del lado lógico son típicas de hoja de datos. La del PH014 es un *supuesto*, porque no
hay hoja de datos.

| Carga | Diseño |
|---|---|
| ESP32 con Wi-Fi (picos de TX) | 500 mA |
| TDS SEN0244 / pH PH014 / ADS1115 + BH1750 + DS18B20 / LED y alarma | 6 / 20 / 2 / 20 mA |
| **Total lógico a 5 V** | **≈ 0.55 A ≈ 2.75 W** → 2.75 / 0.85 / 24 ≈ **0.13 A en 24 V** |
| Bomba de 25 W | 25 / 24 = 1.04 A nominal; **1.02–1.03 A observados** en simulación |
| Arranque de la bomba (*supuesto* 3×) | ≈ 3.1 A (modelo: 24 V / 7.7 Ω) |
| Un canal de dosificación (*supuesto*: 12 V sobre 24 Ω) | 0.5 A a 12 V ≈ 0.29 A en 24 V |

Régimen con la bomba y una dosificación: ≈ 1.03 + 0.13 + 0.29 ≈ **1.45 A**. Esto es el 29 % de la
fuente de 5 A, y el 36 % del 80 % utilizable (4 A). En el arranque (≈ 3.1 + 0.42 ≈ 3.5 A) la carga
sigue por debajo de 4 A. Conclusión: la fuente de 24 V / 5 A es suficiente, con la condición de
dosificar un solo canal a la vez, que es lo que impone el firmware.

### 3.2 Justificación de componentes

- **Buck (XL4015) en lugar de un regulador lineal:** bajar de 24 a 5 V con 0.55 A disiparía
  (24 − 5) · 0.55 ≈ **10.5 W** en un lineal. Un buck con η ≈ 85 % pierde ≈ 0.5 W. Ajuste del XL4015:
  Vout = 1.25 · (1 + R2/R1); para 5 V, R2/R1 = 3.
- **LM1117-3.3:** (5 − 3.3) · 0.3 A ≈ 0.5 W, admisible. En la simulación entrega 3.30 V (N1).
- **D1 10TQ045 (Schottky):** protege contra polaridad invertida con una caída menor que la de un
  diodo de silicio.
- **1N4751A (30 V):** limita sobretensiones del bus de 24 V. En el circuito físico iría un TVS
  (p. ej. de la serie SMBJ); Proteus no trae un TVS con modelo de simulación.
- **F1 de 3.15 A retardado:** está por encima del régimen (≈ 1.45 A) y tolera el arranque (≈ 3.5 A).
- **F2 de 2 A retardado:** protege la rama de la bomba (1.04 A nominales). El fusible de Proteus no
  tiene retardo y se funde en el arranque (N3a); ver §6.
- **Compuerta del MOSFET, 100 Ω / 10 kΩ:** los 100 Ω limitan el pico de carga de la compuerta. Los
  10 kΩ la mantienen en 0 V si queda flotante (reinicio o cable suelto).
- **IRLZ44N:** es de nivel lógico. Observado: Vgs = 4.95 V, Vds = 0.022 V a 1.03 A, de donde
  Rds ≈ 21 mΩ y P ≈ 23 mW. No necesita disipador.
- **1N4007:** descarga la energía inductiva al apagar la carga (ver F5).
- **Pull-ups de 10 kΩ en las salidas del MCU:** fijan el estado de apagado mientras el MCU se reinicia.
- **Pull-ups de 4.7 kΩ (I²C y 1-Wire):** son los valores típicos de las hojas de datos.
- **1 kΩ en serie + BAT54 en las entradas analógicas:** el ADS1115 no admite más de VDD + 0.3 V. Si el
  módulo de pH va alimentado a 5 V, la resistencia limita la corriente del clamp. F2 mostró que el
  BAT54 por sí solo deja ≈ 3.49 V; ver la corrección propuesta en §5.
- **Divisor TDS de 4.3 kΩ / 3.6 kΩ:** 5 · 3.6 / 7.9 ≈ 2.28 V, dentro del rango de 0 a 2.3 V del SEN0244.
  Es un valor de diseño.
- **LED de alarma con 680 Ω:** (3.3 − 2.2) / 680 ≈ 1.6 mA.

## 4. Lista de componentes (simulación ↔ circuito físico)

| Función | En Proteus | Componente físico | Cant. |
|---|---|---|---|
| Fuente | pila de 24 V | fuente de 24 V / 5 A (comprada) | 1 |
| Convertidores | riel +5V y pila de 12 V | XL4015 (comprados) | 2 |
| Regulador de 3.3 V | LM1117DT-3.3 | regulador del DevKit ESP32 | 1 |
| Protección de entrada | FUSE 3.15 A, 10TQ045, 1N4751A, 470 µF | fusible retardado, Schottky, TVS, electrolítico | 1 c/u |
| Controlador | ATmega328P | ESP32 DevKit | 1 |
| ADC | ADS1015 | ADS1115 (comprado) | 1 |
| Sondas | POT-HG (RV1, RV2) + resistencias | pH PH014, TDS Meter V1.0 | 2 |
| Temperatura | DS18B20 | kit DS18B20 (comprado) | 1 |
| Nivel | SW-SPST | flotador (comprado) | 1 |
| Protección de entradas | BAT54 + 1 kΩ | igual | 2 |
| Lógica de interbloqueo | 74HCT02 | igual (propuesto) | 2 |
| Drivers | IRLZ44N + 100 Ω + 10 kΩ + 1N4007 | módulo MOSFET dual Noyito (D4184) u otro driver | 5 canales |
| Bomba | MOTOR-DC de 24 V | bomba de 24 V / 25 W (seleccionada) | 1 |
| Dosificación | resistencias de 24 Ω | mecanismo A/B/Up/Down **pendiente** | 4 |
| Alarma / reinicio | LED-RED + 680 Ω; SW + 10 kΩ | igual | 1 |
| Órdenes | SW-SPST | órdenes por MQTT | 5 |
| Luz | — | BH1750 (sin modelo; queda fuera de la simulación) | 1 |

## 5. Resultados de la simulación

### Funcionamiento normal
| ID | Condición | Observado | Captura |
|---|---|---|---|
| N1 | Alimentación con la bomba apagada | +24V = 23.9 V; +5V = 5.00 V; 3V3_LDO = 3.30 V | `N1_voltajes_bomba_off.jpg` |
| N2 | pH a 1.251 V, TDS a 1.788 V, 23.5 °C, con agua | Terminal: T=23.5 pH=7.09 TDS=773 ppm NIVEL=OK ALARMA=NO | `N2_terminal_sensores.jpg` |
| N3 | Bomba ordenada (F2 provisional de 4 A) | I = 1.02–1.03 A; Vgate = 4.95 V; Vdrenador = 0.022 V | `N3b_…`, `N3c_…` |

**Explicación.**
- **N1:** los rieles están dentro de su nominal. La caída de 0.1 V en el de 24 V sale de D1 y del
  modelo de la fuente.
- **N2:** reproduce la lectura real del 21/10 (≈ 770 ppm a 23.5 °C), con las mismas fórmulas que
  el firmware real. El pH de 7.09 sale de las constantes históricas; no es una calibración.
- **N3:** confirma que el MOSFET satura por completo con la compuerta a 5 V.

### Condiciones límite y fallas
| ID | Falla | Observado | Captura |
|---|---|---|---|
| N3a | Arranque de la bomba con F2 de 2 A sin retardo | F2 se funde en el arranque; I = 0 A | `N3a_F2_2A_fundido_arranque.jpg` |
| F1 | Nivel bajo con la bomba ordenada | NIVEL=BAJO, BOMBA=OFF; salida NOR ≈ 0 V; Vgate ≈ 0 V; Vdrenador = 23.9 V; I = 0 A | `F1_nivel_bajo_bomba_inhibida.jpg` |
| F2 | Sonda de pH a 5 V (fuera de rango) | AIN0 ≈ 3.49 V (limitado por el clamp); terminal: pH=INVALIDO (3.486 V), ALARMA=SI | `F2_pH_5V_clamp_invalido.jpg` |
| F4 | MCU con los pines en alta impedancia (equivale al reinicio) | Salida NOR ≈ 0 V; Vgate ≈ 0 V; Vdrenador = 23.87 V; bomba apagada aunque SW1 y SW6 estén cerrados | `F4_pines_alta_impedancia_bomba_OFF.jpg` |
| F5 | Corte de la bomba sin diodo flyback (D6 excluido) | Un breakpoint analógico en VD > 30 V se disparó a t = 2.173 s con **VD = 44.48 V** (no es el pico máximo). Con D6 no se dispara: VD = 14.4 V | `F5a_…`, `F5b_…`, `F5c_con_flyback_sin_pico.jpg` |
| F7 | pH Up y pH Down ordenados a la vez | Terminal: UP=OFF DOWN=OFF CONFLICTO ALARMA=SI; compuertas de Q4 y Q5 ≈ 0 V | `F7_conflicto_UP_DOWN.jpg`, `F7_parcial_…` |

El detalle de cada prueba y los intentos descartados están en
[`evidencias/resultados-fallas.md`](evidencias/resultados-fallas.md).

**Explicación.**
- **F1:** la bomba se bloquea dos veces, por firmware y por el NOR del 74HCT02. El bloqueo físico no
  depende del MCU.
- **N3a:** muestra que la corriente de arranque supera el valor del fusible. Por eso el fusible
  físico debe ser retardado y por eso hace falta medir la corriente de arranque real.
- **F2:** el firmware descarta la lectura en lugar de inventar un valor, y R1 limita la corriente del
  clamp a ≈ (5 − 3.49) / 1 kΩ ≈ 1.5 mA. **Hallazgo de diseño:** 3.49 V supera en ≈ 0.19 V el máximo
  absoluto del ADS1115 (VDD + 0.3 V). Antes del montaje físico conviene alimentar el módulo de pH
  a 3.3 V, añadir un divisor como el de TDS o usar un clamp de menor Vf.
- **F4:** el modelo ATmega328P de Proteus sigue ejecutando el programa con RST a 0 V (captura
  `F4a_…`). Por eso el reinicio se representó con un firmware mínimo (`setup(){} loop(){}`) que deja
  todos los pines como entradas, igual que un AVR durante el reset. Las pull-ups y la NOR mantienen
  apagada la bomba. Al excluir el MCU también desaparece el riel de 3.3 V que genera (captura
  `F4b_…`), así que ese intento se descartó por ser un artefacto del modelo. Falta comprobar en el
  ESP32 real los estados de sus GPIO durante el arranque.
- **F5:** sin el diodo, la energía de la inductancia del motor eleva el drenador por encima de la
  alimentación (≥ 44 V), lo que pone en riesgo al MOSFET. Con el diodo, el pico no llega a 30 V.
  Se usó un breakpoint analógico en lugar de la pantalla del osciloscopio porque la simulación es
  demasiado lenta para disparar el osciloscopio en tiempo real. El modelo no incluye la avalancha
  del IRLZ44N.
- **F7:** el bloqueo de pH Up/Down es solo por firmware; el 74HCT02 únicamente bloquea por nivel.
  Una mejora futura sería añadir un bloqueo físico entre esos dos canales.

## 6. Diferencias entre la simulación y el circuito físico

- **Controlador:** el ESP32 se sustituye por un ATmega328P, que ejecuta un firmware didáctico (no es
  el controlador final). No hay Wi-Fi ni MQTT, y las órdenes se dan con interruptores. Para que el
  modelo DS18B20 responda, la simulación corre a **16 MHz** (`firmware-sim/build-16mhz/`), lo que
  está fuera de especificación para un ATmega a 3.3 V; el ESP32 real funciona a 3.3 V.
- **DS18B20:** el modelo de Proteus no responde a 3.3 V, así que se alimenta (con su pull-up) a 5 V.
  En el circuito físico va a 3.3 V, compatible con el ESP32. Cerca de la mitad de las lecturas
  simuladas salen `T=INVALIDA`; el firmware activa la alarma y compensa el TDS con la referencia
  de 25 °C.
- **Sondas de pH y TDS:** se representan con tensiones ajustables. No hay química, deriva, ruido,
  temperatura de la solución ni calibración.
- **ADC:** el ADS1015 (12 bits) sustituye al ADS1115 (16 bits); el registro I²C es el mismo.
  El BH1750 no tiene modelo.
- **Alimentación:** los XL4015 son fuentes ideales, sin rizado, conmutación ni eficiencia real. El
  riel +5V se usa directamente: con la pila U1 en paralelo aparecía el error «singular matrix».
  La lógica se alimenta del riel ideal `+3V3` y no de `3V3_LDO` (ver §2); en el circuito físico,
  el regulador alimenta toda la lógica.
- **Protecciones:** como TVS se usa un zener 1N4751A. El fusible no modela el retardo, por eso F2 se
  funde en el arranque.
- **Bomba y drivers:** la bomba es un MOTOR-DC genérico (7.7 Ω, arranque *supuesto* de 3×), mientras
  que la real es brushless con electrónica interna. Los D4184 del Noyito se representan con IRLZ44N.
  La dosificación son cargas resistivas, porque su mecanismo está pendiente.
- **Interruptores:** no se accionaron durante la simulación. Cada caso se fijó con `STATE` y se
  corrió por separado.
- **Fuera de alcance:** nube, backend, base de datos y Android (lo permite la práctica). Las fallas de
  comunicación se probarán en la integración de software.

## 7. Archivos

- `proteus/hydromate.pdsprj` — proyecto. Los respaldos automáticos y los archivos de espacio de
  trabajo de Proteus no se versionan.
- `firmware-sim/HydroMateProteusSim/` — fuente del firmware didáctico. `build-16mhz/` contiene el
  `.hex` que se carga en la simulación. La compilación de 8 MHz se genera en `build/`, que no se
  versiona.
- `evidencias/` — capturas de Proteus; `resultados-fallas.md` contiene las notas de las fallas.
- `T9_PDC_1288703.pdf` — reporte de 27 páginas. Contiene: cumplimiento de requisitos; cada
  parte del esquemático con recortes señalados y el componente físico que representa; cálculos y
  justificación; lista de componentes; las simulaciones con sus capturas y la explicación de cada
  resultado; y las diferencias con el circuito físico.

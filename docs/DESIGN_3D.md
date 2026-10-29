# Diseño 3D modular HydroMate

Revisión 28/10/2026. Estado: **modelado paramétrico generado y verificado en
CAD; ninguna pieza impresa ni probada físicamente.** Fuente: `cad/`. Base
documental: `HydroMate_Dossier_Integral_Diseno_3D_28-10-2026.docx`.

## Módulos

| Módulo | Piezas (`cad/out/stl`) | Función |
|---|---|---|
| CTRL-01 principal | `hub_body`, `hub_lid`, `hub_gasket`, `hub_usb_plug`, `hub_mount_*` | ESP32, ADS1115, XL4015, 3× D4184, distribución y todos los puertos; caja sellada |
| POWER-01 fuente | `power_body`, `power_cap`, `power_mount_flat` | Torre vertical ventilada para la fuente 24 V 197×130×40; CA y 24 V salen por el piso |
| AQUA-01 agua | `aqua_holder`, `aqua_grommet_*`, `aqua_pod_*`, `aqua_ph_split_grommet`, `aqua_cable_sleeve`, `aqua_mount_flat` | Portasondas pH/TDS/temperatura sobre la tapa + cápsula con PH-4502C, placa TDS y adaptador DS18B20 |
| LEVEL-01 nivel | `level_top`, `level_bracket` + tubo PVC 3/4" | Brida sobre la tapa (barreno 30 mm), tubo PVC y soporte inferior con placa vertical donde se atornilla el **flotador horizontal** (barreno 22.2 mm, supuesto 1/2" NPT: medir rosca). El brazo queda hacia afuera y el cable sube por el tubo. Con la caja de 33 cm + tapa, el tubo mide ~262 mm y el eje del flotador queda a ~7.5 cm del fondo. No se perfora la pared del depósito bajo el agua |
| LIGHT-01 luces | `light_pod_*` | Cápsula pequeña para la interfaz del botón de la lámpara (PCB por medir) |
| TEMP-A exterior | — (usar modelo descargado) | DS18B20 Solar Shield V2 (Thingiverse 2553127, CC BY): `Base_front/Rear`, `Cap`, `Wall_Mount` |
| LUX | — (usar modelo descargado) | BH1750 housing (Thingiverse 5818208, CC BY): `Base` + `Dome`, domo blanco/translúcido |
| DOSE-01 | pendiente de decisión | Ver sección Dosificación |
| Probetas | `coupon_fit`, `coupon_rail` | Imprimir primero: riel, barreno PG9, insertos 3.9/4.0/4.2, ranura de junta |

Todas las piezas caben en la K1C (220×220×250); las mayores son `hub_body`
(~197×153 mm) y `power_body` (234 mm de alto, vertical). `build.py` detiene la entrega si una pieza no cabe o el
sólido es inválido.

## Arquitectura física

- **Fuente separada (cambio 28/10)**: la fuente real mide 197×130×40 mm; con
  paredes y bornes necesita ~225 mm acostada y no cabe en la K1C. Va en
  POWER-01, torre vertical: el aire entra abajo (frente y costados, sobre los
  bornes), sube a lo largo de la fuente y sale bajo un capuchón con falda
  (chimenea sin goteo directo). No es hermética a propósito. Además separa la
  corriente de pared del agua y de los sensores. Verificar con el fabricante
  que la fuente admite montaje vertical; a carga alta puede requerir reducir
  la potencia.
- **CTRL-01** es una sola caja sellada: zona analógica a la izquierda,
  potencia a la derecha y un nervio bajo entre ambas; los 24 V entran por el
  piso junto al bus de distribución.
- **Puertos**: señales al frente (AQUA, NIV, LUX, TEX, AUX), potencia en el
  extremo derecho (BOMBA, LUZ, DOSIS), 24 V por el piso y USB del ESP32 a la
  izquierda con tapón TPU. Todos con **PG9 IP68 (cable 4–8 mm, ya comprados)**,
  barreno 15.5 mm y separación de 26 mm para girar la llave. El conector
  automotriz de 14 vías es cable-a-cable: cada cable sale por PG9 y termina en
  un pigtail corto con el conector; las cavidades sin usar llevan tapón ciego.
  Excepción: la sonda de pH entra con su BNC por un pasacables TPU partido
  (Ø16.5); alternativa: pasamuros BNC hembra-hembra. Los cables de sonda miden
  3–4 mm, por debajo del mínimo del PG9 (4 mm): llevan `aqua_cable_sleeve`,
  funda TPU partida que los lleva a 5.5 mm dentro del prensaestopas.
- **AQUA** propone **un solo cable de 7–8 hilos** al principal (5 V, 3.3 V,
  GND, PO pH, señal TDS, TDS conmutado, DATA DS18B20) en vez de tres
  conectores. Es una propuesta: si se mantienen conectores separados, cambiar
  `HUB_FRONT_PORTS` en `params.py`.
- **Depósito** (medido, aprox.): 580×480 mm, cuerpo de 330 mm
  y tapa de 10 mm, esquinas redondeadas, torre de 6" al centro y una pinza de
  cierre al centro de cada lado. La tapa asienta en un borde de 10×10 mm que
  **no** se usa para colgar: un gancho quedaría entre la tapa y el sello.
- **Dónde va cada módulo** (plano `cad/out/preview/lid_layout.png`):
  portasondas (barreno Ø51, centro +175/−95 mm desde el centro de la tapa) y
  nivel (Ø30, centro −185/−100) en la tapa, a 63 y 98 mm libres de la torre.
  AQUA y CTRL-01 con placa plana (VHB o tornillo + arandela ancha) en la
  pared frontal, sin tapar las pinzas: AQUA a la derecha, 20 mm bajo el borde;
  CTRL-01 a la izquierda, con su parte superior ≥75 mm bajo el borde para
  dejar libre la palanca. **POWER-01 va fuera de la caja** (muro o soporte,
  ≥10 cm sobre el piso): en 330 mm de pared no le queda espacio para los
  cables bajo las pinzas, y lo que lleva corriente de pared no debe quedar a ras
  del suelo si el depósito fuga. Al abrir la tapa, los cables de sonda
  (largos) dan la holgura. Se supone la torre
  centrada; si no lo está, conservar las mismas holguras.
- **Montaje universal**: todos los módulos llevan atrás una ranura hembra
  cola de milano (14→20 mm, 5 mm) abierta hacia abajo; se cuelgan deslizando
  sobre una placa con rieles macho. Se usan placas planas; el gancho
  (`hook=True`) queda disponible en código, sin uso en este depósito.
- **Portasondas "nenúfar"**: placa Ø104 que bloquea la luz del agujero
  (menos algas), collar centrador en el agujero de la tapa, tres fundas
  paralelas unidas por un alma triangular y arandelas TPU partidas que
  permiten ajustar la profundidad de cada sonda.

## Principios de diseño aplicados

| Principio | Dónde |
|---|---|
| Lenguaje orgánico con sentido | Contorno superelipse (guijarro), tapas chaflán+redondeo, tornillos en "pétalos", nervaduras de hoja, portasondas nenúfar |
| Sellado: tornillos fuera de la junta | Junta TPU en ranura; M3 desde abajo en pétalos exteriores; tapa sin barrenos visibles |
| Agua: goteo hacia afuera | Puertos al frente con bucle de goteo, falda que cubre ventilas, sin aberturas hacia arriba |
| Separación eléctrica | CA ventilada abajo / DC sellada arriba; analógico separado de potencia |
| A prueba de errores (poka-yoke) | Lados distintos por tipo de puerto, etiquetas grabadas, AQUA PG9 y pH Ø16 de tamaño distinto |
| Tolerancia a variantes | Cunas perimetrales con puentes para cintillo, sin depender de barrenos (vendedores reportan 51–62 mm para XL4015) |
| Mantenimiento con una herramienta | Solo tornillos M3 + insertos térmicos; tapas removibles sin desconectar; módulos deslizan a una mano |
| Ergonomía de mano | Separación de 24 mm entre puertos (dedos/llave), tapón USB con lengüeta |
| Diseño para impresión | Sin soportes: voladizos ≤45°, conos bajo pétalos, tapas impresas boca abajo; holgura 0.3 mm; probetas antes de piezas grandes |
| Ecología | Desarmable y reparable (sin pegamento), módulos reemplazables, material mínimo, probetas pequeñas para no desperdiciar piezas grandes |

## Medidas: estado

Referencias (vendedor/modelo descargado), no medidas propias:
ESP32 DevKit V1 30 pines 51.5×28.3; ADS1115 28.3×17.8; XL4015 hasta 62×26.3
(variantes 51×26.3×14 y 54×23); D4184 15 A 34×17×12; adaptador DS18B20
23×20.5; flotador M10; PG9 rosca 15.2 mm.

Medidas propias (28/10, aproximadas): fuente 197×130×40, bornes abajo en
una cara corta, sin ventilador; placa pH 42×33, componentes 12.5 mm de alto,
BNC sobresale 17 mm y pines 5 mm (el BNC mira a los puertos); placa TDS 42×32,
conectores de 5 mm de alto, centrados en los lados cortos y sobresaliendo
10 mm y 8 mm; sondas pH Ø12 y TDS Ø13 (parte ancha); cables de sonda 3–4 mm.
Agujero del portasondas fijado por diseño: sierra copa 2" (51 mm).
Modelos enviados: válvula pinch base 40×45.5, disco Ø30 (SG90, tubo PTFE
6 mm); BH1750 base 79×40×18, domo Ø40×24; Solar Shield V2 Ø46×~79 total;
caja ESP32 externa 65×54.5 (confirma placa ~51×28).

**Medir antes de imprimir finales**: rosca y tuerca del flotador horizontal
(`HFLOAT_HOLE`, supuesto 22.2 mm) y PCB de la interfaz LIGHT-01 (cuando se
defina el circuito del botón). Al perforar, confirmar el diámetro
de la torre (168 hidráulico o 160 sanitario) y su posición en la tapa.

## Dosificación (DOSE-01): recomendación

No imprimir depósitos (PETG poroso con químicos). Comprar frascos HDPE/PP
rectangulares de 250 mL (p. ej. Nalgene 2018-0250 ~61×61×146) e imprimir solo
un bastidor. Entre gravedad+válvula pinch y bomba peristáltica, se recomienda
**peristáltica**: queda cerrada sin energía por diseño (el rodillo aprieta la
manguera), la dosis depende del tiempo y no de la altura de líquido, y usa los
MOSFET existentes. La válvula pinch descargada (CC BY-NC, uso no comercial)
solo es aceptable con resorte normalmente cerrado y calibración por nivel.
Decisión pendiente; no se modeló todavía.

## Impresión inicial sugerida

PETG 0.20 mm, 5 perímetros, 35–40 % giroide; TPU 95A a 20–30 mm/s para
juntas y arandelas. Orden: `coupon_fit` + `coupon_rail` → ajustar `TOL`,
`INSERT_D`, `PORT_D` → `aqua_holder` y arandelas con sondas reales → cápsulas →
principal y POWER. Probar estanqueidad con cajas vacías; ninguna pieza es IP65 por sí
misma. Vigilar la temperatura de la fuente en POWER (PETG ~70 °C de
deformación) durante 1–2 h a carga real antes de cerrar.

## Fuentes consultadas

Dimensiones de vendedores: [Handson XL4015](https://www.handsontec.com/dataspecs/module/XL4015-5A-PS.pdf),
[Sigmanortec D4184](https://sigmanortec.ro/en/dual-power-mosfet-module-15a-400w),
[Thinkrobotics PH-4502C](https://thinkrobotics.com/products/ph4502c-ph-meter),
[Tinkered ESP32 DevKit V1](https://tinkered.ai/components/esp32-devkit-v1),
[GX16 Probots](https://probots.co.in/gx16-2-pin-aviation-connector-panel-mount.html),
[flotador M10](https://www.walmart.com/ip/351874475). Modelos Thingiverse
5367793, 5818208, 2553127 y 4771598 (licencias en cada ZIP).

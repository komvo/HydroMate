"""Parámetros únicos del ecosistema 3D HydroMate (mm).

Estados: CONF = medido/confirmado, REF = referencia de vendedor o modelo
descargado, MEDIR = supuesto que debe validarse con calibrador antes de imprimir
la pieza final. Cambiar aquí y reconstruir con build.py; ninguna otra pieza
debe tener números de componentes escritos a mano.
"""

# --- Impresora y material (Creality K1C, PETG/TPU) -------------------------
BED = (220.0, 220.0, 250.0)   # volumen nominal K1C
WALL = 3.0                    # pared PETG general
FLOOR = 3.0
TOL = 0.3                     # holgura deslizante por lado
N_SHAPE = 4.0                 # exponente de la superelipse: 2 = elipse, 4 = "squircle"

# Inserto roscado M3 por calor (hueco PETG) y tornillos M3 de cierre.
INSERT_D, INSERT_DEPTH = 4.0, 6.0
M3_CLEAR, M3_HEAD_D, M3_HEAD_H = 3.4, 6.5, 2.2

# Junta TPU 95A en ranura: sobresale ~25 % para compresión.
GROOVE_W, GROOVE_D = 2.2, 1.8
GASKET_W, GASKET_H = 1.8, 2.4

# Puertos: prensaestopas PG9 IP68 (cable 4–8 mm, ya comprados)
# con pigtail corto al conector automotriz sellado de 14 vías (cable a cable).
PORT_D = 15.5          # REF PG9: rosca 15.2 mm
PORT_BOSS_D = 23.5
PORT_PITCH = 26.0      # deja girar la llave de la tuerca PG9 (~19–20 mm)
PORT_AC_D = PORT_D
PORT_GX16_D = 16.2     # REF barreno GX16 16 mm

# Riel universal cola de milano: misma interfaz para todos los módulos.
DOVE_W_ROOT, DOVE_W_TIP, DOVE_H = 14.0, 20.0, 5.0

# --- Componentes (largo, ancho, alto) --------------------------------------
COMP = {
    # Fuente medida 28/10 (aprox.): largo x ancho x espesor.
    "psu":     ((197.0, 130.0, 40.0), "CONF"),
    "esp32":   ((51.5, 28.3, 13.0), "REF"),    # DevKit V1 30 pines; alto con pines
    "ads1115": ((28.3, 17.8, 8.0), "REF"),
    "xl4015":  ((62.0, 26.3, 16.0), "REF"),    # envolvente de variantes 51–62 mm
    "d4184":   ((34.0, 17.0, 12.0), "REF"),    # 15 A/400 W doble MOSFET
    "bus":     ((32.0, 28.0, 16.0), "REF"),    # 2x WAGO 221-415 / portafusible
    # Medidas 28/10: pH 42x33, alto total 16 con BNC;
    # TDS 42x32, conectores de 5 mm de alto.
    "ph4502c": ((42.0, 33.0, 16.0), "CONF"),
    "tds":     ((42.0, 32.0, 8.0), "CONF"),    # G2GKJ1022
    "ds_adapt": ((23.0, 20.5, 10.0), "REF"),
    "light_if": ((40.0, 30.0, 15.0), "MEDIR"),  # interfaz pulsador LIGHT-01
}
# Salientes centrados en los lados cortos (lado A, lado B), mm, medidos 28/10.
# TDS: conector grande 10, corto 8. pH: BNC 17, pines 5; componentes 12.5 alto.
OVERHANG = {"tds": (10.0, 8.0), "ph4502c": (17.0, 5.0)}

N_MOSFET = 3   # bomba 24 V, luces, reserva

# Puertos del módulo principal: (etiqueta tapa, diámetro). AQUA agrupa pH, TDS
# y temperatura del agua en un cable de 7–8 hilos; si se prefieren conectores
# separados, reemplazar "AQUA" por "pH", "TDS", "TAG".
HUB_FRONT_PORTS = [("AQUA", PORT_AC_D), ("NIV", PORT_D), ("LUX", PORT_D),
                   ("TEX", PORT_D), ("AUX", PORT_D)]
# Entrada de 24 V desde POWER-01: por el piso, hacia abajo (bucle de goteo).
HUB_SIDE_PORTS = [("BOMBA", PORT_D), ("LUZ", PORT_D), ("DOSIS", PORT_D)]

# Sondas sumergidas (diámetro del cuerpo que pasa por la funda).
PROBE_D = {"ph": (12.0, "CONF"), "tds": (13.0, "CONF"), "temp": (6.0, "REF")}
CABLE_D = 3.5          # cables de sonda 3–4 mm (medido); menor que el mínimo PG9
GROMMET_T = 1.6        # espesor TPU entre sonda y funda

# --- Instalación en el depósito ---------------------------------------------
LID_HOLE_D = (51.0, "DISEÑO")  # sierra copa 2 in en la tapa del depósito
LID_T = (2.0, "DISEÑO")        # collar centrador; no crítico si la tapa es más gruesa
# Depósito 51 L medido 28/10 (aprox.), esquinas redondeadas.
# El borde donde asienta la tapa (10 alto x 10 fondo) NO se usa para colgar:
# un gancho rompería el sello. Los módulos van con placa plana en la pared.
# Alto = cuerpo 330 + tapa 10 (piso → cara superior de la tapa). Pinzas de
# cierre al centro de los 4 lados: dejar libre ±CLIP_HALF y CLIP_DROP bajo el borde.
DEPOT = ((580.0, 480.0, 340.0), "CONF")
CLIP_HALF, CLIP_DROP = 70.0, 70.0
RIM_T = (5.0, "N/A")           # solo para la placa con gancho (no recomendada)
TOWER_OD = (168.0, "REF")      # PVC 6 in; 160 si es sanitario: medir al perforar
LEVEL_FROM_FLOOR = 75.0        # nivel mínimo a 5–10 cm del fondo
PIPE_OD = (26.7, "REF")        # PVC 3/4 in cédula 40 para el tallo de nivel
LEVEL_HOLE_D = 30.0            # broca/sierra copa para el tubo en la tapa
# Flotador HORIZONTAL (montaje lateral, brazo que sube/baja).
# Rosca típica 1/2 NPT → barreno ~22 mm; algunos son M12. Medir rosca y tuerca.
HFLOAT_HOLE = (22.2, "MEDIR")
HFLOAT_AXIS = 22.0             # eje del flotador sobre el fondo del soporte


def level_pipe_len():
    """Largo del tubo PVC: de la cara superior de la tapa al piso del casquillo inferior."""
    return DEPOT[0][2] + 24 - (LEVEL_FROM_FLOOR - HFLOAT_AXIS + 49)


def size(key):
    return COMP[key][0]


def pending():
    """Lista de supuestos que deben medirse antes de imprimir finales."""
    out = [f"COMP.{k} {v[0]}" for k, v in COMP.items() if v[1] == "MEDIR"]
    out += [f"PROBE_D.{k} {v[0]}" for k, v in PROBE_D.items() if v[1] == "MEDIR"]
    for name in ("HFLOAT_HOLE",):
        val = globals()[name]
        if val[1] == "MEDIR":
            out.append(f"{name} {val[0]}")
    return out

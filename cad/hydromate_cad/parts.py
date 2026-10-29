"""Piezas simples: portasondas, placas de montaje, nivel, arandelas y probetas."""
import math

import cadquery as cq

from . import common as C
from . import params as P

# --- AQUA-01: portasondas "nenúfar" -----------------------------------------
PAD_D, PAD_T = 104.0, 4.0
SLEEVE_WALL, SLEEVE_UP, SLEEVE_DOWN = 2.4, 10.0, 45.0
PROBE_ORDER = (("ph", 90), ("tds", 210), ("temp", 330))   # ángulos en planta


def _bore(key):
    return P.PROBE_D[key][0] + 2 * P.GROMMET_T + 0.3


# radio mínimo para que las tres fundas no choquen (a 120°)
PROBE_R = max(_bore(k) + 2 * SLEEVE_WALL for k in P.PROBE_D) / math.sqrt(3) + 0.8


def probe_holder():
    """Se apoya sobre la tapa del depósito; la placa bloquea la luz (algas).

    z=0 es la cara superior de la tapa del depósito.
    """
    hole_d, lid_t = P.LID_HOLE_D[0], P.LID_T[0]
    pad = cq.Workplane("XY").circle(PAD_D / 2).extrude(PAD_T)
    # muesca de nenúfar orientada hacia la cápsula AQUA (frente, -Y)
    notch = (cq.Workplane("XY").polyline([(0, -PAD_D * 0.18), (-9, -PAD_D), (9, -PAD_D)])
             .close().extrude(PAD_T + 1))
    pad = C.safe_fillet(pad.cut(notch), ">Z", 1.5)
    out = pad.union(cq.Workplane("XY").workplane(offset=-lid_t)
                    .circle(hole_d / 2 - 0.4).circle(hole_d / 2 - 2.4).extrude(lid_t))
    centers = []
    for key, ang in PROBE_ORDER:
        x, y = PROBE_R * math.cos(math.radians(ang)), PROBE_R * math.sin(math.radians(ang))
        centers.append((key, x, y))
        od = _bore(key) + 2 * SLEEVE_WALL
        sl = cq.Workplane("XY").workplane(offset=-SLEEVE_DOWN).center(x, y).circle(od / 2) \
            .extrude(SLEEVE_DOWN + PAD_T + SLEEVE_UP)
        out = out.union(C.safe_fillet(sl, ">Z", 1.0))
    # alma triangular que mantiene las fundas paralelas bajo la tapa
    tri = [(x, y) for _, x, y in centers]
    web = cq.Workplane("XY").workplane(offset=-SLEEVE_DOWN).polyline(tri).close() \
        .extrude(SLEEVE_DOWN - lid_t)
    out = out.union(web)
    for key, x, y in centers:
        b = _bore(key)
        out = out.cut(cq.Workplane("XY").workplane(offset=-SLEEVE_DOWN - 1).center(x, y)
                      .circle(b / 2).extrude(SLEEVE_DOWN + PAD_T + SLEEVE_UP + 2))
        out = out.cut(cq.Workplane("XY").workplane(offset=PAD_T + SLEEVE_UP - 1.6).center(x, y)
                      .circle(b / 2 + 2.2).extrude(2))
    # nervaduras radiales grabadas y tres barrenos M3 opcionales a la tapa
    for ang in (30, 150, 270):
        a = math.radians(ang)
        cx, cy = 36 * math.cos(a), 36 * math.sin(a)
        out = out.cut(cq.Workplane("XY").workplane(offset=PAD_T - 0.6).center(cx, cy)
                      .slot2D(22, 1.4, ang).extrude(1))
        hx, hy = 46 * math.cos(a + 0.5), 46 * math.sin(a + 0.5)
        out = out.cut(cq.Workplane("XY").center(hx, hy).circle(P.M3_CLEAR / 2).extrude(PAD_T + 1))
    return out


def probe_grommet(key, split=True):
    """Arandela TPU: interferencia 0.2 mm por lado sobre la sonda."""
    d = P.PROBE_D[key][0]
    od = _bore(key) - 0.2
    g = cq.Workplane("XY").circle(od / 2).extrude(14)
    g = g.union(cq.Workplane("XY").workplane(offset=14).circle(od / 2 + 2.0).extrude(1.5))
    g = g.cut(cq.Workplane("XY").workplane(offset=-1).circle(d / 2 - 0.2).extrude(18))
    if split:
        g = g.cut(cq.Workplane("XY").box(0.8, od, 40).translate((0, od / 2, 0)))
    return g


# --- Montaje universal --------------------------------------------------------
PLATE_T = 4.0


def mount_plate(width, height, rail_xs, rail_len, hook=False, screws=True):
    """Placa con rieles macho. Cara trasera (y=PLATE_T) contra el depósito.

    hook=True agrega un gancho que monta sobre un labio de espesor RIM_T;
    hook=False deja la cara trasera plana para cinta VHB o tornillos.
    """
    out = cq.Workplane("XY").box(width, PLATE_T, height, centered=(True, False, False))
    out = C.safe_fillet(out, "|Y", 6.0)
    for x in rail_xs:
        out = out.union(C.dovetail(rail_len).translate((x, 0.01, 1.0)))
        # chaflán de entrada en la punta superior del riel
        out = out.cut(cq.Workplane("XY").box(30, 12, 2).rotate((0, 0, 0), (1, 0, 0), 45)
                      .translate((x, -6, 1.0 + rail_len)))
    if hook:
        rim = P.RIM_T[0] + 0.4
        out = out.union(cq.Workplane("XY").box(width * 0.6, PLATE_T + rim + 3, 4,
                                               centered=(True, False, False))
                        .translate((0, 0, height)))
        out = out.union(cq.Workplane("XY").box(width * 0.6, 3, 18, centered=(True, False, False))
                        .translate((0, PLATE_T + rim, height - 14)))
    if screws:
        for x in (-width / 2 + 10, width / 2 - 10):
            for z in (10, height - 10):
                out = out.cut(cq.Workplane("XZ").center(x, z).circle(2.25).extrude(-20, both=True))
    return out


# --- LEVEL-01: tallo de nivel con tubo PVC 3/4 in -------------------------------
SOCKET = 24.0


def level_top():
    """Brida sobre la tapa con casquillo para el tubo; el cable sale por arriba.

    Cortar el tubo a: altura interior del depósito − LEVEL_FROM_FLOOR − 10.
    """
    od = P.PIPE_OD[0] + 0.4
    out = cq.Workplane("XY").circle(P.LEVEL_HOLE_D / 2 + 13).extrude(4)
    out = C.safe_fillet(out, ">Z", 1.5)
    out = out.union(cq.Workplane("XY").circle(od / 2 + 3).extrude(SOCKET + 3))
    out = out.cut(cq.Workplane("XY").workplane(offset=-1).circle(od / 2).extrude(SOCKET + 1))
    # tapa superior con salida de cable por pasacables TPU
    out = out.cut(cq.Workplane("XY").workplane(offset=SOCKET - 1).circle(4.5).extrude(10))
    for ang in (0, 120, 240):
        a = math.radians(ang + 60)
        r = P.LEVEL_HOLE_D / 2 + 7
        out = out.cut(cq.Workplane("XY").center(r * math.cos(a), r * math.sin(a))
                      .circle(P.M3_CLEAR / 2).extrude(5))
    return out


def level_bracket():
    """Soporte inferior: casquillo para el tubo y placa vertical del flotador.

    El flotador horizontal atraviesa la placa (tuerca del otro lado); el brazo
    queda hacia +X y el cable sube al tubo por un barreno del piso del casquillo.
    Imprimir con la boca del casquillo sobre la cama (placa hacia arriba).
    """
    od = P.PIPE_OD[0] + 0.4
    plate_h, floor_t, w = 45.0, 4.0, od + 6
    hole = P.HFLOAT_HOLE[0]
    out = cq.Workplane("XY").box(4, w - 1, plate_h, centered=(True, True, False))
    out = out.union(cq.Workplane("XY").workplane(offset=plate_h).circle(od / 2 + 3)
                    .extrude(floor_t + SOCKET))
    out = out.cut(cq.Workplane("XY").workplane(offset=plate_h + floor_t).circle(od / 2)
                  .extrude(SOCKET + 1))
    out = out.cut(cq.Workplane("XY").workplane(offset=plate_h - 1).center(-8, 0).circle(4)
                  .extrude(floor_t + 2))
    # barreno en gota: imprime sin soporte con el casquillo sobre la cama
    r = hole / 2
    drop = (cq.Workplane("YZ").center(0, P.HFLOAT_AXIS).circle(r).extrude(10, both=True)
            .union(cq.Workplane("YZ").polyline([(-r * 0.707, P.HFLOAT_AXIS - r * 0.707),
                                                (r * 0.707, P.HFLOAT_AXIS - r * 0.707),
                                                (0, P.HFLOAT_AXIS - r * 1.414)])
                   .close().extrude(10, both=True)))
    return out.cut(drop)


def cable_sleeve(length=16.0, od=5.5):
    """Funda TPU partida: lleva cables de 3–4 mm al rango de sellado del PG9."""
    g = cq.Workplane("XY").circle(od / 2).circle(P.CABLE_D / 2 - 0.25).extrude(length)
    return g.cut(cq.Workplane("XY").box(0.6, od, length * 3).translate((0, od / 2, 0)))


# --- Probetas de ajuste antes de imprimir piezas grandes ----------------------
def coupon_fit():
    """Ranura hembra, puerto PG7, insertos 3.9/4.0/4.2 y tramo de ranura de junta."""
    out = cq.Workplane("XY").box(70, 30, 14, centered=(True, False, False))
    slot = C.dovetail(30.02, P.TOL).rotate((0, 0, 0), (1, 0, 0), 90)
    out = out.cut(slot.translate((-18, 30.01, 14.01)))
    out = out.cut(cq.Workplane("XY").center(8, 15).circle(P.PORT_D / 2).extrude(20))
    for i, d in enumerate((3.9, 4.0, 4.2)):
        out = out.cut(cq.Workplane("XY").workplane(offset=14 - P.INSERT_DEPTH)
                      .center(25, 6 + 9 * i).circle(d / 2).extrude(10))
    return out.cut(cq.Workplane("XY").workplane(offset=14 - P.GROOVE_D)
                   .center(-31, 15).rect(P.GROOVE_W, 26).extrude(5))


def coupon_rail():
    rail = C.dovetail(28).rotate((0, 0, 0), (1, 0, 0), -90).translate((0, -14, PLATE_T - 0.01))
    return cq.Workplane("XY").box(30, 30, PLATE_T, centered=(True, True, False)).union(rail)

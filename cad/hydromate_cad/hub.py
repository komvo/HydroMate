"""CTRL-01: módulo principal sellado (sin fuente; la fuente va en POWER-01).

body : bandeja electrónica; zona analógica a la izquierda, potencia a la
       derecha con un nervio bajo entre ambas. 24 V entra por el piso.
lid  : domo con junta TPU, etiquetas de puertos y nervaduras de hoja.
Origen: centro del piso. Frente = -Y, pared del depósito = +Y.
"""
import cadquery as cq

from . import common as C
from . import enclosure as E
from . import params as P

CONTENT = (172.0, 104.0)
AI, BI = C.fit_se(*CONTENT, k=1.09)
AD, BD = AI + P.WALL, BI + P.WALL
H_BODY = 42.0
H_LID = 22.0
PETALS = (35, 145, 215, 325)
SLOT_XS = (-45.0, 45.0)
PAD_H = H_BODY - 8
PORT_Z = P.FLOOR + 17
ESP_Y = 14.0
DC_XY = (-14.0, 12.0)     # entrada 24 V junto al bus de distribución


def _front_xs():
    n = len(P.HUB_FRONT_PORTS)
    return [(i - (n - 1) / 2) * P.PORT_PITCH for i in range(n)]


def _side_ys():
    n = len(P.HUB_SIDE_PORTS)
    return [(i - (n - 1) / 2) * P.PORT_PITCH - 6 for i in range(n)]


def _layout():
    xi = AD - P.WALL
    lay = [("esp32", (-xi + 34, ESP_Y), 0), ("ads1115", (-xi + 30, -30), 0),
           ("bus", (-8, 44), 0), ("xl4015", (45, 40), 0)]
    for i in range(P.N_MOSFET):
        lay.append(("d4184", (8 + 24 * i, -22), 90))
    return lay


def body():
    W = P.WALL
    out = E.body(AD, BD, H_BODY, PETALS)
    out, _ = E.rear_slots(out, BD, SLOT_XS, 0, PAD_H, 130)
    z = P.FLOOR - 0.01
    for key, xy, rot in _layout():
        out = out.union(C.board_cradle(P.size(key), xy, z, rot))
        L = P.size(key)[0] if rot == 0 else P.size(key)[1]
        for sx in (-1, 1):
            out = out.union(C.zip_arch(xy[0] + sx * (L / 2 + 6), xy[1], z, along="y"))
    rib = cq.Workplane("XY").box(2.4, 2 * BD - 40, 10, centered=(True, True, False))
    rib = rib.cut(cq.Workplane("XY").box(4, 14, 10, centered=(True, True, False)).translate((0, 0, 4)))
    out = out.union(rib.translate((-36, 0, z)))
    # señales al frente, potencia en +X, USB en -X, 24 V por el piso
    for (_, d), x in zip(P.HUB_FRONT_PORTS, _front_xs()):
        boss, hole = C.wall_port(AD, BD, "-y", x, PORT_Z, d)
        out = out.union(boss).cut(hole)
    for (_, d), y in zip(P.HUB_SIDE_PORTS, _side_ys()):
        boss, hole = C.wall_port(AD, BD, "+x", y, PORT_Z, d)
        out = out.union(boss).cut(hole)
    xu = C.se_x(AD, BD, ESP_Y)
    out = out.cut(cq.Workplane("YZ").workplane(offset=-xu).center(ESP_Y, P.FLOOR + 8.5)
                  .slot2D(14, 9, 0).extrude(W + 10, both=True))
    boss, hole = C.port_boss("z", (DC_XY[0], DC_XY[1], 0), P.PORT_D, P.FLOOR + 4, P.PORT_BOSS_D)
    return out.union(boss).cut(hole)


def lid():
    labels = [(name, x, -C.se_y(AD, BD, x) + 20)
              for (name, _), x in zip(P.HUB_FRONT_PORTS, _front_xs())]
    part = E.lid(AD, BD, H_LID, PETALS, labels,
                 veins=dict(center=(-8, 8), length=100, scale=1.2),
                 title=("HydroMate", 0, BD - 22, 8))
    for (name, _), y in zip(P.HUB_SIDE_PORTS, _side_ys()):
        part = part.cut(C.engrave(name, H_LID, C.se_x(AD, BD, y) - 20, y, size=4.5, angle=90))
    return part


def gasket():
    return E.gasket(AD, BD)


def usb_plug():
    """Tapón TPU para el acceso USB del ESP32."""
    plug = cq.Workplane("YZ").slot2D(13.6, 8.6, 0).extrude(6)
    plug = plug.union(cq.Workplane("YZ").workplane(offset=-2).slot2D(19, 13, 0).extrude(2))
    tab = cq.Workplane("YZ").workplane(offset=-2).center(0, -9).rect(8, 8).extrude(2)
    return plug.union(tab)

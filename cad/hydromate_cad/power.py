"""POWER-01: torre ventilada para la fuente 24 V (197x130x40) en vertical.

Acostada no cabe en la K1C; vertical forma una chimenea a lo largo de la
fuente: aire entra abajo (frente y costados), sale arriba bajo la falda del
capuchón. Bornes abajo: los cables de CA y 24 V salen por el piso con bucle de
goteo. No es hermética a propósito; ubicarla lejos de salpicaduras.
Armado: cablear la fuente afuera, pasar cables por los PG9 del piso y bajar
la fuente desde arriba. Fuente sin ventilador: convección.
Origen: centro del piso. Frente = -Y, pared del depósito = +Y.
"""
import cadquery as cq

from . import common as C
from . import enclosure as E
from . import params as P

PSU_L, PSU_W, PSU_T = P.size("psu")      # largo (vertical), ancho (X), espesor (Y)
TERM = 40.0                              # bornes (cara corta, abajo) y curvatura de cables
AI, BI = C.fit_se(PSU_W + 4, PSU_T + 4 + 2 * 2.5, k=1.08)
A, B = AI + P.WALL, BI + P.WALL
H = P.FLOOR + TERM + PSU_L + 4
SK, SKIRT, CAP_H = 5.0, 14.0, 14.0       # holgura de salida de aire, falda, capuchón
PAD_H = H - SKIRT - 4
SLOT_XS = (-35.0, 35.0)
SCREW_Z = H - 7.0


def _front_only(wp):
    return wp.intersect(cq.Workplane("XY").box(4 * A, 2 * B, 2 * H, centered=(True, False, True))
                        .translate((0, -2 * B, 0)))


def body():
    W = P.WALL
    out = C.safe_fillet(C.se_solid(A, B, H), "<Z", 5.0)
    out = out.cut(C.se_solid(A, B, H, -W, P.FLOOR))
    out, _ = E.rear_slots(out, B, SLOT_XS, 0, PAD_H, 110)
    z0 = P.FLOOR + TERM
    # columnas bajo las esquinas de la fuente
    for sx in (-1, 1):
        for sy in (-1, 1):
            out = out.union(cq.Workplane("XY").box(10, 8, TERM, centered=(True, True, False))
                            .translate((sx * (PSU_W / 2 - 6), sy * (PSU_T / 2 - 5), P.FLOOR)))
    # guías verticales laterales (holgura 0.5 por lado)
    for sx in (-1, 1):
        for y in (-PSU_T / 4, PSU_T / 4):
            xw = C.se_x(A, B, y) - W
            g = PSU_W / 2 + 0.5
            out = out.union(cq.Workplane("XY").box(xw - g + 1, 3, PSU_L - 10, centered=(False, True, False))
                            .translate((g if sx > 0 else -xw - 1, y, z0 + 5)))
    # insertos horizontales para el capuchón
    for sx in (-1, 1):
        xw = C.se_x(A, B, 0) - W
        out = out.union(cq.Workplane("XY").box(8, 10, 9).translate((sx * (xw - 3), 0, SCREW_Z)))
        out = out.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            P.INSERT_D / 2, W + 7, cq.Vector(sx * (xw + W + 0.5), 0, SCREW_Z), cq.Vector(-sx, 0, 0))))
    # entrada de aire: granos verticales al frente y costados, sobre los bornes
    for x in range(-48, 49, 16):
        out = out.cut(_front_only(cq.Workplane("XZ").center(x, z0 + 22)
                                  .slot2D(26, 4, 90).extrude(B + 5, both=True)))
    for y in (0.0,):
        out = out.cut(cq.Workplane("YZ").center(y, z0 + 22).slot2D(26, 4, 90)
                      .extrude(A + 5, both=True))
    # salida de aire bajo la falda del capuchón (frente, fondo y costados)
    for x in range(-50, 51, 20):
        out = out.cut(cq.Workplane("XZ").center(x, H - 9).slot2D(14, 4, 0)
                      .extrude(B + 6, both=True))
    # CA (PG9) y salida 24 V (PG9) por el piso
    for x in (-35.0, 35.0):
        boss, hole = C.port_boss("z", (x, 0, 0), P.PORT_D, P.FLOOR + 4, P.PORT_BOSS_D)
        out = out.union(boss).cut(hole)
    return out


def cap():
    """Capuchón contra goteo; el aire sale por la holgura SK bajo la falda."""
    a, b = A + SK, B + SK
    out = C.se_solid(a, b, CAP_H)
    out = out.faces(">Z").edges().chamfer(8.0)
    out = C.safe_fillet(out, ">Z", 3.0)
    out = out.union(C.se_band(a, b, 0, -2.0, SKIRT, -SKIRT))
    out = out.cut(C.se_solid(a, b, CAP_H - 2.5, -2.0, -0.01)
                  .faces(">Z").edges().chamfer(6.0))
    # topes que apoyan en el borde de la torre y dejan pasar el aire
    for x in (-A * 0.6, 0.0, A * 0.6):
        for sy in (-1, 1):
            out = out.union(cq.Workplane("XY").box(10, SK + 4, 2.01, centered=(True, True, False))
                            .translate((x, sy * (C.se_y(A, B, x) + 0.5), 0)))
    for sx in (-1, 1):
        out = out.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            P.M3_CLEAR / 2, 14, cq.Vector(sx * (a + 2), 0, SCREW_Z - H), cq.Vector(-sx, 0, 0))))
    out = out.cut(C.leaf_veins(CAP_H, center=(-6, 0), length=A * 1.2, scale=0.8))
    return out.cut(C.engrave("24 V", CAP_H, A * 0.55, 0, size=6))

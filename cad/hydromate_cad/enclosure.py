"""Envolvente sellada reutilizable: cuerpo, tapa domo, junta y pétalos.

Los tornillos van en "pétalos" exteriores, fuera de la línea de junta, para
que ningún barreno conecte el exterior con el interior sellado.
"""
import cadquery as cq

from . import common as C
from . import params as P

RIM_IN = 6.0       # reborde interior que soporta la junta
PETAL_D, PETAL_OFF = 10.0, 4.0


def _petal_xy(a, b, deg):
    return C.se_at(a + PETAL_OFF, b + PETAL_OFF, deg)


def body(a, b, h, petals, bottom_r=4.0):
    """Cuerpo abierto arriba; piso en z=0..FLOOR; borde superior en z=h."""
    W = P.WALL
    out = C.safe_fillet(C.se_solid(a, b, h), "<Z", bottom_r)
    for deg in petals:
        x, y = _petal_xy(a, b, deg)
        col = cq.Workplane().add(cq.Solid.makeCylinder(PETAL_D / 2, 14, cq.Vector(x, y, h - 14)))
        cone = cq.Workplane().add(cq.Solid.makeCone(0.5, PETAL_D / 2, 6, cq.Vector(x, y, h - 20)))
        out = out.union(col).union(cone)
    cav = C.se_solid(a, b, h - 9 - P.FLOOR + 0.01, -W, P.FLOOR)
    w1 = C.se_wire(a, b, -W, h - 9).val()
    w2 = C.se_wire(a, b, -RIM_IN, h - 6).val()
    cav = cav.union(cq.Workplane().add(cq.Solid.makeLoft([w1, w2], True)))
    cav = cav.union(C.se_solid(a, b, 7, -RIM_IN, h - 6))
    out = out.cut(cav)
    mid = -W / 2 - 0.45
    out = out.cut(C.se_band(a, b, mid + P.GROOVE_W / 2, mid - P.GROOVE_W / 2,
                            P.GROOVE_D + 1, h - P.GROOVE_D))
    # tornillo M3 desde abajo: cabeza en el pétalo, rosca en el inserto de la tapa
    for deg in petals:
        x, y = _petal_xy(a, b, deg)
        out = out.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            P.M3_HEAD_D / 2 + 0.15, 15, cq.Vector(x, y, h - 21))))
        out = out.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            P.M3_CLEAR / 2, 8, cq.Vector(x, y, h - 7))))
    return out


def lid(a, b, h, petals, labels=(), veins=None, title=None):
    """Tapa domo sin barrenos visibles; se imprime boca abajo sin soportes.

    Chaflán 45° + redondeo suave: el perfil se lee orgánico y no tiene
    voladizos al imprimir con la cara superior sobre la cama.
    """
    W = P.WALL
    c = min(h - 6.0, 10.0)
    out = C.se_solid(a, b, h)
    out = out.faces(">Z").edges().chamfer(c)
    out = C.safe_fillet(out, ">Z", 3.0)
    out = out.union(C.se_band(a, b, -RIM_IN - P.TOL, -RIM_IN - P.TOL - 1.8, 3, -3))
    for deg in petals:
        x, y = _petal_xy(a, b, deg)
        out = out.union(cq.Workplane().add(cq.Solid.makeCylinder(PETAL_D / 2, 8, cq.Vector(x, y, 0))))
        out = out.union(cq.Workplane().add(cq.Solid.makeCone(PETAL_D / 2, 0.5, 6, cq.Vector(x, y, 8))))
    out = out.cut(C.se_solid(a, b, 6, -RIM_IN - P.TOL - 1.8, -3))
    inner = C.se_solid(a, b, h - 3 - W, -W, 3)
    inner = inner.faces(">Z").edges().chamfer(max(c - W * 0.6, 1.0))
    out = out.cut(inner)
    for deg in petals:
        x, y = _petal_xy(a, b, deg)
        out = out.cut(cq.Workplane().add(cq.Solid.makeCylinder(
            P.INSERT_D / 2, P.INSERT_DEPTH, cq.Vector(x, y, -0.01))))
    for text, x, y in labels:
        out = out.cut(C.engrave(text, h, x, y, size=5.0))
    if veins:
        out = out.cut(C.leaf_veins(h, **veins))
    if title:
        text, x, y, s = title
        out = out.cut(C.engrave(text, h, x, y, size=s))
    return out


def gasket(a, b):
    W = P.WALL
    mid = -W / 2 - 0.45
    return C.se_band(a, b, mid + P.GASKET_W / 2, mid - P.GASKET_W / 2, P.GASKET_H)


def rear_slots(part, b, xs, z0, h, pad_w, wall_in=5.5, proud=4.0):
    """Almohadilla trasera plana con ranuras hembra abiertas hacia abajo."""
    y1 = b + proud
    pad = (cq.Workplane("XY").box(pad_w, y1 - (b - wall_in), h, centered=(True, False, False))
           .translate((0, b - wall_in, z0)))
    pad = C.safe_fillet(pad, "|Z", 2.0)
    part = part.union(pad)
    for x in xs:
        slot = C.dovetail(h - 5, P.TOL).translate((x, y1, z0 - 0.01))
        part = part.cut(slot)
    return part, y1

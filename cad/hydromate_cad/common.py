"""Primitivas compartidas: contorno orgánico, envolventes, puertos y rieles."""
import math

import cadquery as cq

from . import params as P


# --- Contorno superelipse ("guijarro") --------------------------------------
def se_points(a, b, n=P.N_SHAPE, samples=96):
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / n), c),
                    b * math.copysign(abs(s) ** (2 / n), s)))
    return pts


def se_wire(a, b, off=0.0, z=0.0, n=P.N_SHAPE):
    wp = cq.Workplane("XY").workplane(offset=z).spline(
        se_points(a, b, n), periodic=True, includeCurrent=False).close()
    if off:
        wp = wp.offset2D(off, "arc")
    return wp


def se_solid(a, b, h, off=0.0, z=0.0, n=P.N_SHAPE):
    return se_wire(a, b, off, z, n).extrude(h)


def se_band(a, b, off_out, off_in, h, z=0.0, n=P.N_SHAPE):
    return se_solid(a, b, h, off_out, z, n).cut(se_solid(a, b, h, off_in, z, n))


def se_y(a, b, x, n=P.N_SHAPE):
    """Semiancho y del contorno en la abscisa x (para ubicar puertos)."""
    r = min(abs(x) / a, 0.999)
    return b * (1 - r ** n) ** (1 / n)


def se_x(a, b, y, n=P.N_SHAPE):
    return se_y(b, a, y, n)


def se_at(a, b, deg, n=P.N_SHAPE):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (a * math.copysign(abs(c) ** (2 / n), c),
            b * math.copysign(abs(s) ** (2 / n), s))


def safe_fillet(wp, selector, r):
    try:
        return wp.edges(selector).fillet(r)
    except Exception:
        return wp


# --- Puertos ----------------------------------------------------------------
def port_boss(axis, pos, hole_d, length, boss_d=P.PORT_BOSS_D):
    """Botón cilíndrico con cara plana para prensaestopas/conector.

    axis: 'x'|'y'|'z'; pos: centro de la cara exterior; length: hacia dentro.
    Devuelve (sólido a unir, sólido a restar).
    """
    d = {"x": cq.Vector(-1, 0, 0), "y": cq.Vector(0, -1, 0), "z": cq.Vector(0, 0, 1)}[axis]
    sign = 1
    if axis in ("x", "y"):
        coord = pos[0] if axis == "x" else pos[1]
        sign = -1 if coord < 0 else 1
        d = d * sign          # siempre hacia el interior
    p = cq.Vector(*pos)
    boss = cq.Workplane().add(cq.Solid.makeCylinder(boss_d / 2, length, p, d))
    hole = cq.Workplane().add(cq.Solid.makeCylinder(hole_d / 2, length + 20, p - d * 10, d))
    return boss, hole


def fit_se(Lc, Wc, k=1.1, n=P.N_SHAPE):
    """Semiejes interiores mínimos para que un rectángulo Lc x Wc quepa."""
    return Lc / 2 * k, (Wc / 2) / (1 - (1 / k) ** n) ** (1 / n)


def wall_port(a, b, side, s, z, hole_d, wall=P.WALL):
    """Puerto en pared curva. side: '-y' (frente), '+x'/'-x' (extremos).

    s es la coordenada a lo largo de la pared. La cara plana exterior
    sobresale 1.5 mm del punto más saliente de la curva.
    """
    boss_d = max(P.PORT_BOSS_D, hole_d + 8)
    if side == "-y":
        f = lambda t: se_y(a, b, t)
    else:
        f = lambda t: se_x(a, b, t)
    vals = [f(s + d) for d in (-boss_d / 2, 0, boss_d / 2)]
    out, inn = max(vals) + 1.5, min(vals) - wall - 2
    if side == "-y":
        pos, axis = (s, -out, z), "y"
    else:
        sign = 1 if side == "+x" else -1
        pos, axis = (sign * out, s, z), "x"
    return port_boss(axis, pos, hole_d, out - inn, boss_d)


# --- Riel cola de milano universal ------------------------------------------
def dovetail_profile(clear=0.0):
    w0, w1, h = P.DOVE_W_ROOT + 2 * clear, P.DOVE_W_TIP + 2 * clear, P.DOVE_H + clear
    return [(-w0 / 2, 0), (w0 / 2, 0), (w1 / 2, h), (-w1 / 2, h)]


def dovetail(length, clear=0.0):
    """Riel en el plano XY (raíz en y=0, punta hacia +y), extruido en +Z."""
    pts = [(x, -y) for x, y in dovetail_profile(clear)]  # punta hacia -y (módulo)
    return cq.Workplane("XY").polyline(pts).close().extrude(length)


# --- Detalles de superficie -------------------------------------------------
def leaf_veins(z_top, center=(0, 0), length=70.0, scale=1.0, depth=0.6):
    """Nervaduras de hoja grabadas: firma visual ecológica en las tapas."""
    cx, cy = center
    wp = cq.Workplane("XY").workplane(offset=z_top - depth)
    cut = wp.center(cx, cy).slot2D(length * scale, 1.4 * scale, 0).extrude(depth + 1)
    for i, k in enumerate((-0.30, -0.08, 0.14)):
        L = (26 - 5 * i) * scale
        for side in (1, -1):
            ang = side * 38
            x0 = cx + k * length * scale + math.cos(math.radians(ang)) * L / 2
            y0 = cy + math.sin(math.radians(ang)) * L / 2
            cut = cut.union(cq.Workplane("XY").workplane(offset=z_top - depth)
                            .center(x0, y0).slot2D(L, 1.1 * scale, ang).extrude(depth + 1))
    return cut


def engrave(text, z_top, x, y, size=5.0, depth=0.6, angle=0):
    return (cq.Workplane("XY").workplane(offset=z_top).center(x, y)
            .transformed(rotate=(0, 0, angle))
            .text(text, size, -depth, kind="bold", halign="center", valign="center"))


def zip_arch(x, y, z, along="x"):
    """Puente para cintillo: sujeta tarjetas sin perforar el piso."""
    L, W, H = (8, 5, 4.5) if along == "x" else (5, 8, 4.5)
    arch = cq.Workplane("XY").box(L, W, H, centered=(True, True, False)).translate((x, y, z))
    tl, tw = (L + 2, 3.0) if along == "x" else (3.0, W + 2)
    tunnel = cq.Workplane("XY").box(tw if along == "x" else tl, tl if along == "x" else tw,
                                    2.2, centered=(True, True, False)).translate((x, y, z))
    return arch.cut(tunnel)


def board_cradle(dims, center, z, rot=0, wall=1.6, rim=4.0, ledge=2.5):
    """Marco perimetral + esquinas elevadas: tolera variantes sin barrenos."""
    L, W, _ = dims
    Li, Wi = L + 0.6, W + 0.6
    frame = (cq.Workplane("XY").rect(Li + 2 * wall, Wi + 2 * wall).rect(Li, Wi)
             .extrude(rim))
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame = frame.union(cq.Workplane("XY").box(5, 5, ledge, centered=(True, True, False))
                                .translate((sx * (Li / 2 - 2.5), sy * (Wi / 2 - 2.5), 0)))
    # aberturas en los lados largos para cables y dedos
    frame = frame.cut(cq.Workplane("XY").box(Li * 0.45, Wi + 10, rim, centered=(True, True, False))
                      .translate((0, 0, ledge + 0.5)))
    frame = frame.rotate((0, 0, 0), (0, 0, 1), rot).translate((center[0], center[1], z))
    return frame

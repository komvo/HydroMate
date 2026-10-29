"""Cápsulas de conexión (AQUA-01 y LIGHT-01) con la misma envolvente sellada.

Cada cápsula cuelga de una placa de montaje por el riel trasero; los puertos
quedan al frente y abajo para formar bucles de goteo en los cables.
"""
import cadquery as cq

from . import common as C
from . import enclosure as E
from . import params as P

PETALS = (35, 145, 215, 325)


class Pod:
    def __init__(self, name, boards, ports, h_in, title):
        """boards: [(clave, x, rot)] en fila sobre X; ports: [(etiqueta, d)]."""
        self.name, self.ports, self.title = name, ports, title
        def ext(k, r, axis):
            L, W, _ = P.size(k)
            L += sum(P.OVERHANG.get(k, (0, 0)))
            return (L if (r == 0) == (axis == 0) else W) + 4.0
        widths = [ext(k, r, 0) for k, _, r in boards]
        depths = [ext(k, r, 1) for k, _, r in boards]
        Lc = max(sum(widths) + 4 * len(widths), len(ports) * P.PORT_PITCH + 10)
        Wc = max(depths) + 14 + 2 * 2.5    # zona de tuercas + almohadilla trasera
        # superelipse de menor área que contiene el rectángulo de contenido
        ai, bi = min((C.fit_se(Lc, Wc, k=1.03 + 0.01 * i) for i in range(40)),
                     key=lambda ab: ab[0] * ab[1])
        self.a, self.b = ai + P.WALL, bi + P.WALL
        self.h = P.FLOOR + h_in
        yc = ((-bi + 14) + (bi - 5.5)) / 2    # entre zona de tuercas y almohadilla
        x = -sum(widths) / 2 - 2 * (len(widths) - 1)
        self.layout = []
        for (k, _, r), w in zip(boards, widths):
            # la PCB se corre hacia el saliente corto; con rot=90 el lado A
            # (BNC/conector grande) mira al frente, hacia los puertos
            o = P.OVERHANG.get(k, (0, 0))
            sh = (o[0] - o[1]) / 2
            dx, dy = (sh, 0.0) if r == 0 else (0.0, sh)
            self.layout.append((k, (x + w / 2 + dx, yc + dy), r))
            x += w + 4

    def port_xs(self):
        n = len(self.ports)
        return [(i - (n - 1) / 2) * P.PORT_PITCH for i in range(n)]

    def body(self):
        out = E.body(self.a, self.b, self.h, PETALS)
        out, self.pad_y = E.rear_slots(out, self.b, (0.0,), 0, self.h - 8, 50)
        for k, xy, r in self.layout:
            out = out.union(C.board_cradle(P.size(k), xy, P.FLOOR - 0.01, r))
        for (_, d), x in zip(self.ports, self.port_xs()):
            boss, hole = C.wall_port(self.a, self.b, "-y", x, P.FLOOR + 12, d)
            out = out.union(boss).cut(hole)
        return out

    def lid(self):
        labels = [(n, x, -C.se_y(self.a, self.b, x) + 15)
                  for (n, _), x in zip(self.ports, self.port_xs())]
        return E.lid(self.a, self.b, 16.0, PETALS, labels,
                     veins=dict(center=(0, 8), length=self.a * 0.9, scale=0.75),
                     title=(self.title, 0, self.b - 14, 6))

    def gasket(self):
        return E.gasket(self.a, self.b)


# Entradas desde las sondas: pH pasa con su BNC por pasacables TPU partido
# (Ø16.5); TDS y temperatura por PG9; salida única de 7–8 hilos al principal.
AQUA = Pod("aqua",
           [("ph4502c", 0, 90), ("tds", 0, 90), ("ds_adapt", 0, 0)],
           [("pH", 16.5), ("TDS", P.PORT_D), ("T", P.PORT_D), ("HUB", P.PORT_AC_D)],
           h_in=30.0, title="AQUA")

LIGHT = Pod("light", [("light_if", 0, 0)],
            [("HUB", P.PORT_D), ("LED", P.PORT_D)], h_in=28.0, title="LUZ")


def split_grommet(cable_d=P.CABLE_D, hole_d=16.5, panel=P.WALL):
    """Pasacables TPU partido: deja pasar el BNC y luego sella el cable."""
    g = cq.Workplane("XY").circle(hole_d / 2 - 0.1).extrude(panel + 0.2)
    g = g.union(cq.Workplane("XY").workplane(offset=-2).circle(hole_d / 2 + 3).extrude(2))
    g = g.union(cq.Workplane("XY").workplane(offset=panel + 0.2).circle(hole_d / 2 + 1.2).extrude(1.6))
    g = g.cut(cq.Workplane("XY").workplane(offset=-3).circle(cable_d / 2 - 0.3).extrude(panel + 8))
    return g.cut(cq.Workplane("XY").box(0.8, hole_d + 10, panel + 10).translate((0, hole_d / 2, panel / 2)))

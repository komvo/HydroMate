"""Planos 2D explicativos: qué va dentro de cada módulo y hacia dónde salen los cables."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

from . import common as C  # noqa: E402
from . import hub, pods, power  # noqa: E402
from . import params as P  # noqa: E402

NAMES = {"esp32": "ESP32", "ads1115": "ADS1115\n(ADC)", "bus": "Bus 24V/5V\nWAGO+fusible",
         "xl4015": "XL4015\n24→5 V", "d4184": "MOSFET\nD4184", "ph4502c": "Placa pH",
         "tds": "Placa TDS", "ds_adapt": "Adapt.\nDS18B20", "light_if": "Interfaz\nbotón LED"}
ANALOG, POWERC, OTHER = "#cfe3f0", "#f6d8b8", "#e6efd9"
COLOR = {"esp32": OTHER, "ads1115": ANALOG, "bus": POWERC, "xl4015": POWERC, "d4184": POWERC,
         "ph4502c": ANALOG, "tds": ANALOG, "ds_adapt": ANALOG, "light_if": OTHER}


def _outline(ax, a, b, fc="#f7f7f2"):
    ax.add_patch(Polygon(C.se_points(a, b), closed=True, fc=fc, ec="#3f6e64", lw=2))
    ax.add_patch(Polygon(C.se_points(a - P.WALL, b - P.WALL), closed=True, fill=False,
                         ec="#3f6e64", lw=0.8, ls=":"))


def _board(ax, key, xy, rot):
    L, W, _ = P.size(key)
    w, h = (L, W) if rot == 0 else (W, L)
    x, y = xy
    o = P.OVERHANG.get(key)
    if o:   # salientes (BNC/conectores) punteados
        if rot == 0:
            ax.add_patch(Rectangle((x - w / 2 - o[0], y - 4), o[0], 8, fill=False, ls="--", ec="#555"))
            ax.add_patch(Rectangle((x + w / 2, y - 4), o[1], 8, fill=False, ls="--", ec="#555"))
        else:
            ax.add_patch(Rectangle((x - 5, y - h / 2 - o[0]), 10, o[0], fill=False, ls="--", ec="#555"))
            ax.add_patch(Rectangle((x - 5, y + h / 2), 10, o[1], fill=False, ls="--", ec="#555"))
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=COLOR[key], ec="#333"))
    ax.text(x, y, NAMES[key], ha="center", va="center", fontsize=7)


def _port(ax, x, y, label, arrow, color="#c0392b"):
    ax.add_patch(Circle((x, y), P.PORT_D / 2, fc="white", ec=color, lw=1.6))
    dx, dy = arrow
    ax.annotate("", (x + dx, y + dy), (x, y), arrowprops=dict(arrowstyle="->", color=color, lw=1.4))
    ax.text(x + dx * 1.25, y + dy * 1.25, label, ha="center", va="center", fontsize=7.5,
            color=color, weight="bold")


def _rear(ax, b, xs, text):
    for x in xs:
        ax.add_patch(Rectangle((x - P.DOVE_W_TIP / 2, b - 1), P.DOVE_W_TIP, 5, fc="#c9a66b", ec="#333"))
    ax.text(0, b + 12, text, ha="center", fontsize=8, color="#7a5c2e")


def _finish(ax, fig, path, title, lim):
    ax.set_title(title, fontsize=11, weight="bold")
    ax.set_xlim(-lim[0], lim[0])
    ax.set_ylim(-lim[1], lim[1])
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def ctrl(path):
    fig, ax = plt.subplots(figsize=(9, 7.4), dpi=110)
    _outline(ax, hub.AD, hub.BD)
    for k, xy, r in hub._layout():
        _board(ax, k, xy, r)
    ax.add_patch(Rectangle((-37.2, -hub.BD + 20), 2.4, 2 * hub.BD - 40, fc="#999"))
    ax.text(-36, -hub.BD + 14, "nervio\nseparador", ha="center", fontsize=6.5)
    ax.text(-60, hub.BD - 18, "ZONA ANALÓGICA", ha="center", fontsize=8, color="#2b5d75")
    ax.text(45, hub.BD - 18, "ZONA DE POTENCIA", ha="center", fontsize=8, color="#a0522d")
    for (name, _), x in zip(P.HUB_FRONT_PORTS, hub._front_xs()):
        _port(ax, x, -C.se_y(hub.AD, hub.BD, x), name, (0, -22))
    for (name, _), y in zip(P.HUB_SIDE_PORTS, hub._side_ys()):
        _port(ax, C.se_x(hub.AD, hub.BD, y), y, name, (30, 0))
    _port(ax, -C.se_x(hub.AD, hub.BD, hub.ESP_Y), hub.ESP_Y, "USB", (-22, 0), "#2b5d75")
    _port(ax, *hub.DC_XY, "24 V\n(piso)", (0, 0.01), "#8e44ad")
    _rear(ax, hub.BD, hub.SLOT_XS, "ranuras de riel → pared del depósito")
    ax.text(0, -hub.BD - 48, "FRENTE: cables de sensores (bajan con bucle de goteo)",
            ha="center", fontsize=8.5)
    _finish(ax, fig, path, "CTRL-01 principal · vista superior sin tapa", (hub.AD + 60, hub.BD + 60))


def aqua(path):
    A = pods.AQUA
    fig, ax = plt.subplots(figsize=(8, 7), dpi=110)
    _outline(ax, A.a, A.b)
    for k, xy, r in A.layout:
        _board(ax, k, xy, r)
    labels = ["pH\n(sonda,\nBNC)", "TDS\n(sonda)", "T agua\n(DS18B20)", "HUB\n→ CTRL"]
    for lab, x in zip(labels, A.port_xs()):
        _port(ax, x, -C.se_y(A.a, A.b, x), lab, (0, -26))
    _rear(ax, A.b, (0.0,), "ranura de riel → pared del depósito")
    _finish(ax, fig, path, "AQUA-01 cápsula · vista superior sin tapa", (A.a + 25, A.b + 50))


def power_front(path):
    fig, ax = plt.subplots(figsize=(6, 8.5), dpi=110)
    A, H = power.A, power.H
    ax.add_patch(Rectangle((-A, 0), 2 * A, H, fc="#eef3ee", ec="#3f6e64", lw=2))
    ax.add_patch(Rectangle((-A - power.SK, H - power.SKIRT), 2 * (A + power.SK), power.SKIRT + power.CAP_H,
                           fc="#7fb685", ec="#3f6e64"))
    z0 = P.FLOOR + power.TERM
    ax.add_patch(Rectangle((-power.PSU_W / 2, z0), power.PSU_W, power.PSU_L, fc="#d5d8dc", ec="#333"))
    ax.text(0, z0 + power.PSU_L / 2, "Fuente 24 V\n197 × 130 × 40\n(vertical)", ha="center", fontsize=9)
    ax.add_patch(Rectangle((-power.PSU_W / 2 + 10, z0 - 6), power.PSU_W - 20, 6, fc="#f6d8b8", ec="#333"))
    ax.text(0, z0 - 16, "bornes", ha="center", fontsize=7.5)
    for x, lab, c in ((-35, "CA 127 V", "#c0392b"), (35, "24 V → CTRL", "#8e44ad")):
        ax.add_patch(Rectangle((x - 8, -2), 16, 5, fc="white", ec=c))
        ax.annotate(lab, (x, -4), (x, -30), ha="center", fontsize=8, color=c, weight="bold",
                    arrowprops=dict(arrowstyle="<-", color=c))
    for z, t in ((z0 + 22, "entrada de aire"), (H - 9, "salida bajo capuchón")):
        ax.annotate(t, (A, z), (A + 20, z), fontsize=8, color="#2b5d75", va="center",
                    arrowprops=dict(arrowstyle="->" if z < H / 2 else "<-", color="#2b5d75"))
    ax.annotate("", (0, H - 20), (0, z0 + 40), arrowprops=dict(arrowstyle="->", color="#2b5d75",
                                                                lw=2, alpha=0.4))
    ax.set_xlim(-A - 40, A + 110)
    ax.set_ylim(-45, H + 40)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("POWER-01 · vista frontal en corte", fontsize=11, weight="bold")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def draw_all(folder):
    ctrl(f"{folder}/layout_ctrl.png")
    aqua(f"{folder}/layout_aqua.png")
    power_front(f"{folder}/layout_power.png")
    rail_explainer(f"{folder}/rail_detail.png")


def rail_explainer(path):
    """Riel cola de milano: corte superior y secuencia lateral de colgado."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 6), dpi=110,
                                 gridspec_kw=dict(width_ratios=[1, 1.25]))
    r0, r1, h, t = P.DOVE_W_ROOT, P.DOVE_W_TIP, P.DOVE_H, P.TOL
    # --- corte visto desde arriba
    a1.add_patch(Rectangle((-40, 4), 80, 10, fc="#bbbbbb", ec="#333"))
    a1.text(0, 9, "PARED DEL DEPÓSITO", ha="center", va="center", fontsize=8)
    a1.add_patch(Rectangle((-30, 0), 60, 4, fc="#c9a66b", ec="#333"))
    a1.add_patch(Polygon([(-r0 / 2, 0), (r0 / 2, 0), (r1 / 2, -h), (-r1 / 2, -h)], fc="#c9a66b", ec="#333"))
    a1.text(34, 2, "placa (pegada\no atornillada)", fontsize=8, va="center")
    mod = [(-38, -h - 3 - 18), (38, -h - 3 - 18), (38, 0 - 0.3), (r0 / 2 + t, -0.3),
           (r1 / 2 + t, -h - t), (-r1 / 2 - t, -h - t), (-r0 / 2 - t, -0.3), (-38, -0.3)]
    a1.add_patch(Polygon(mod, fc="#e9e4d4", ec="#333"))
    a1.text(0, -h - 13, "ESPALDA DEL MÓDULO", ha="center", fontsize=8)
    a1.annotate("el riel es más ancho en la punta:\nel módulo no se puede despegar\nhacia el frente, solo deslizar",
                (r1 / 2, -h), (14, -38), fontsize=8, arrowprops=dict(arrowstyle="->"))
    a1.set_title("Corte visto desde arriba", fontsize=10, weight="bold")
    a1.set_xlim(-45, 60)
    a1.set_ylim(-48, 18)
    a1.set_aspect("equal")
    a1.axis("off")
    # --- secuencia lateral
    def side(ax, x0, z_mod, label):
        ax.add_patch(Rectangle((x0, 0), 6, 120, fc="#bbbbbb", ec="#333"))
        ax.add_patch(Rectangle((x0 - 4, 20), 4, 45, fc="#c9a66b", ec="#333"))
        ax.add_patch(Rectangle((x0 - 9, 21), 5, 42, fc="#a8823f", ec="#333"))
        ax.add_patch(Rectangle((x0 - 9 - 60, z_mod), 60, 52, fc="#e9e4d4", ec="#333"))
        ax.add_patch(Rectangle((x0 - 9 - 0.01, z_mod), 5.3, 47, fc="white", ec="#777", ls="--"))
        ax.add_patch(Rectangle((x0 - 9 - 60, z_mod + 52), 60, 10, fc="#7fb685", ec="#333"))
        ax.text(x0 - 40, z_mod + 26, "módulo", ha="center", fontsize=8)
        ax.text(x0 - 35, -10, label, ha="center", fontsize=9, weight="bold")
    side(a2, 80, 75, "1) Pegar la placa y\nbajar el módulo")
    a2.annotate("", (40, 70), (40, 105), arrowprops=dict(arrowstyle="->", lw=2, color="#c0392b"))
    side(a2, 190, 16, "2) Queda colgado;\nse quita subiéndolo")
    a2.text(84, 12, "riel", fontsize=7, rotation=90)
    a2.text(84, 128, "pared", fontsize=7, ha="center")
    a2.set_title("Vista lateral", fontsize=10, weight="bold")
    a2.set_xlim(0, 210)
    a2.set_ylim(-25, 140)
    a2.set_aspect("equal")
    a2.axis("off")
    fig.suptitle("Riel de colgado: igual que un colgador de cuadro, pero que no se suelta",
                 fontsize=12, weight="bold")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)

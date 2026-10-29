"""Plano de la tapa del depósito: agujeros sugeridos y módulos en las paredes.

Origen: centro de la tapa. Frente (-Y) = lado de operación.
Supone la torre centrada; si no lo está, mover las cotas con la misma holgura.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

from . import hub, parts, pods, power  # noqa: E402
from . import params as P  # noqa: E402

L, W, _ = P.DEPOT[0]
HOLES = {   # nombre: (x, y, agujero, diámetro de la pieza que apoya)
    "Portasondas AQUA": (175.0, -95.0, P.LID_HOLE_D[0], parts.PAD_D),
    "Nivel (PVC 3/4\")": (-185.0, -100.0, P.LEVEL_HOLE_D, P.LEVEL_HOLE_D + 26),
}


def clearances():
    """Distancia libre entre piezas, torre y orilla interior (borde 10 mm)."""
    t = P.TOWER_OD[0] / 2
    out = {}
    for name, (x, y, _, d) in HOLES.items():
        out[name] = {
            "a_torre": round((x * x + y * y) ** 0.5 - t - d / 2),
            "a_orilla": round(min(L / 2 - abs(x), W / 2 - abs(y)) - d / 2 - 10),
        }
    return out


def draw(path):
    fig, ax = plt.subplots(figsize=(9, 7.5), dpi=110)
    ax.add_patch(FancyBboxPatch((-L / 2, -W / 2), L, W, boxstyle="round,pad=0,rounding_size=35",
                                fc="#eef3ee", ec="#3f6e64", lw=2))
    ax.add_patch(Circle((0, 0), P.TOWER_OD[0] / 2, fc="#9cc3d5", ec="#2b5d75", lw=1.5))
    ax.text(0, 0, f"Torre PVC 6\"\nØ{P.TOWER_OD[0]:.0f}", ha="center", va="center", fontsize=9)
    for name, (x, y, hole, d) in HOLES.items():
        ax.add_patch(Circle((x, y), d / 2, fc="#7fb685", ec="#3f6e64", alpha=0.8))
        ax.add_patch(Circle((x, y), hole / 2, fc="white", ec="#c0392b", lw=1.5, ls="--"))
        ax.plot([x], [y], "+", color="#c0392b", ms=10)
        ax.annotate(f"{name}\nbarreno Ø{hole:.0f}\ncentro ({x:+.0f}, {y:+.0f})",
                    (x, y + d / 2), xytext=(x, y + d / 2 + 55), ha="center", fontsize=8.5,
                    arrowprops=dict(arrowstyle="-", color="#555"))
    # pinzas de cierre al centro de cada lado (zona que no se debe tapar)
    for x, y, w, h in ((0, -W / 2 - 6, 2 * P.CLIP_HALF, 12), (0, W / 2 + 6, 2 * P.CLIP_HALF, 12),
                       (-L / 2 - 6, 0, 12, 2 * P.CLIP_HALF), (L / 2 + 6, 0, 12, 2 * P.CLIP_HALF)):
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="#f5b7b1", ec="#c0392b", hatch="//"))
    ax.text(0, -W / 2 - 24, "pinza", ha="center", fontsize=7, color="#c0392b")
    # módulos en paredes exteriores (proyección), fuera de las pinzas
    # AQUA: arriba (20 mm bajo el borde); CTRL-01: debajo de la pinza (≥75 mm)
    wall = [("AQUA · 20 mm bajo borde", 175.0, -W / 2 - 14, 2 * pods.AQUA.a, 22, "#e9e4d4"),
            ("CTRL-01 · ≥75 mm bajo borde", -160.0, -W / 2 - 14, 2 * hub.AD, 22, "#e9e4d4")]
    for name, x, y, w, h, c in wall:
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=c, ec="#333"))
        ax.text(x, y, name, ha="center", va="center", fontsize=8)
    ax.text(L / 2 + 20, -W / 2 + 10, "POWER-01: fuera de la caja,\nen muro o soporte,\n≥10 cm sobre el piso",
            fontsize=8, color="#3f6e64", va="bottom")
    ax.text(0, -W / 2 - 50, "FRENTE", ha="center", fontsize=9, weight="bold")
    ax.text(0, W / 2 + 20, f"Tapa {L:.0f} × {W:.0f} mm, caja 330 mm de alto", ha="center", fontsize=9)
    ax.set_xlim(-L / 2 - 40, L / 2 + 150)
    ax.set_ylim(-W / 2 - 65, W / 2 + 40)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)

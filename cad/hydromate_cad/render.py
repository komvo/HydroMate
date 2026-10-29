"""Vista previa PNG sin GUI: teselado de CadQuery + matplotlib sombreado."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

PALETTE = ["#7fb685", "#e9e4d4", "#5b8c85", "#c9a66b", "#a7c4a0", "#3f6e64"]


def _mesh(shape, tol=0.4):
    verts, tris = shape.tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    return v[np.array(tris)]


def render(parts, path, elev=24, azim=-58, title=None, size=(8, 6), notes=()):
    """parts: lista de (shape, color|None[, alpha]); notes: [(x, y, z, texto)]."""
    fig = plt.figure(figsize=size, dpi=110)
    ax = fig.add_subplot(projection="3d")
    if notes:
        ax.computed_zorder = False     # etiquetas siempre encima
    light = np.array([-0.4, -0.6, 0.8])
    light /= np.linalg.norm(light)
    allv = []
    for i, item in enumerate(parts):
        shape, color = item[0], item[1]
        alpha = item[2] if len(item) > 2 else 1.0
        tri = _mesh(shape)
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        shade = 0.40 + 0.60 * np.abs(n @ light)
        base = np.array(matplotlib.colors.to_rgb(color or PALETTE[i % len(PALETTE)]))
        fc = np.clip(base[None, :] * shade[:, None], 0, 1)
        ax.add_collection3d(Poly3DCollection(tri, facecolors=fc, linewidths=0, alpha=alpha))
        allv.append(tri.reshape(-1, 3))
    v = np.vstack(allv)
    mn, mx = v.min(0), v.max(0)
    c, r = (mn + mx) / 2, (mx - mn).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1), zoom=1.35)
    ax.view_init(elev, azim)
    for x, y, z, t in notes:
        ax.text(x, y, z, t, fontsize=9, weight="bold", color="#1d3b35",
                bbox=dict(fc="white", ec="#3f6e64", alpha=0.9, boxstyle="round,pad=0.25"), zorder=1000)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)

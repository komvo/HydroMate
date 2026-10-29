"""Escenas explicativas: depósito con todos los módulos y detalle del riel.

Usa los STEP ya generados en out/step (rápido). Coordenadas: centro del
depósito en XY, piso z=0, frente hacia -Y.
"""
from pathlib import Path

import cadquery as cq

from . import hub, lid_layout, parts, pods, power, render
from . import params as P

L, W, H = P.DEPOT[0]
BODY_H = H - 10.0          # cuerpo 330 + tapa 10
V = cq.Vector


def _load(step_dir, name):
    return cq.importers.importStep(str(Path(step_dir) / f"{name}.step")).val()


def depot():
    body = cq.Workplane("XY").box(L, W, BODY_H, centered=(True, True, False)).edges("|Z").fillet(35)
    body = body.cut(cq.Workplane("XY").box(L - 8, W - 8, BODY_H, centered=(True, True, False))
                    .edges("|Z").fillet(31).translate((0, 0, 4)))
    lid = (cq.Workplane("XY").box(L + 6, W + 6, 10, centered=(True, True, False))
           .edges("|Z").fillet(37).translate((0, 0, BODY_H)))
    tower = cq.Workplane("XY").circle(P.TOWER_OD[0] / 2).circle(P.TOWER_OD[0] / 2 - 6).extrude(H + 260)
    lid = lid.cut(cq.Workplane("XY").circle(P.TOWER_OD[0] / 2 + 1).extrude(H + 10))
    for (x, y, hole, _) in lid_layout.HOLES.values():
        lid = lid.cut(cq.Workplane("XY").center(x, y).circle(hole / 2).extrude(H + 10))
    clips = None
    for x, y, w, d in ((0, -W / 2 - 4, 2 * P.CLIP_HALF, 8), (0, W / 2 + 4, 2 * P.CLIP_HALF, 8),
                       (-L / 2 - 4, 0, 8, 2 * P.CLIP_HALF), (L / 2 + 4, 0, 8, 2 * P.CLIP_HALF)):
        c = cq.Workplane("XY").box(w, d, 55).translate((x, y, BODY_H - 22))
        clips = c if clips is None else clips.union(c)
    return body.val(), lid.val(), tower.val(), clips.val()


def _on_front_wall(module, plate, b_mod, x, z_bottom):
    """Placa con su cara trasera contra la pared frontal; módulo colgado del riel.

    Los módulos ya tienen la espalda en +Y y los puertos en -Y: no se giran.
    """
    yp = -W / 2 - parts.PLATE_T          # cara frontal de la placa
    plate = plate.translate(V(x, yp, z_bottom))
    module = module.translate(V(x, yp - (b_mod + 4), z_bottom))
    return module, plate


def full(step_dir, out_png):
    body, lid, tower, clips = depot()
    S = lambda n: _load(step_dir, n)
    items = [(body, "#cfe0e8", 0.25), (lid, "#9fb8c4", 0.55), (tower, "#4a86b0"), (clips, "#c0392b")]
    # portasondas y sondas
    hx, hy = lid_layout.HOLES["Portasondas AQUA"][:2]
    items.append((S("aqua_holder").translate(V(hx, hy, H)), "#7fb685"))
    for key, ang in parts.PROBE_ORDER:
        import math
        px = hx + parts.PROBE_R * math.cos(math.radians(ang))
        py = hy + parts.PROBE_R * math.sin(math.radians(ang))
        d = P.PROBE_D[key][0]
        items.append((cq.Solid.makeCylinder(d / 2, 220, V(px, py, 110)), "#444"))
    # nivel: brida, tubo, punta
    lx, ly = lid_layout.HOLES['Nivel (PVC 3/4")'][:2]
    pipe_len = P.level_pipe_len()
    br_z = P.LEVEL_FROM_FLOOR - P.HFLOAT_AXIS
    items += [(S("level_top").translate(V(lx, ly, H)), "#7fb685"),
              (cq.Solid.makeCylinder(P.PIPE_OD[0] / 2, pipe_len, V(lx, ly, br_z + 49)), "#e8e8e8"),
              (S("level_bracket").translate(V(lx, ly, br_z)), "#7fb685"),
              (cq.Solid.makeCylinder(5, 30, V(lx - 15, ly, P.LEVEL_FROM_FLOOR), V(1, 0, 0)), "#f1c40f"),
              (cq.Solid.makeCylinder(13, 22, V(lx + 40, ly, P.LEVEL_FROM_FLOOR), V(0, 1, 0))
               .translate(V(0, -11, 0)), "#f1c40f")]
    # AQUA y CTRL en la pared frontal
    a = pods.AQUA
    z_aqua = BODY_H - 20 - (a.h + 16)
    m, p = _on_front_wall(S("aqua_pod_body"), S("aqua_mount_flat"), a.b, 175, z_aqua)
    lid_a = S("aqua_pod_lid").translate(V(175, -W / 2 - parts.PLATE_T - (a.b + 4), z_aqua + a.h))
    items += [(p, "#c9a66b"), (m, "#e9e4d4"), (lid_a, "#7fb685")]
    z_ctrl = BODY_H - 75 - (hub.H_BODY + hub.H_LID)
    m, p = _on_front_wall(S("hub_body"), S("hub_mount_flat"), hub.BD, -160, z_ctrl)
    lid_c = S("hub_lid").translate(V(-160, -W / 2 - parts.PLATE_T - (hub.BD + 4), z_ctrl + hub.H_BODY))
    items += [(p, "#c9a66b"), (m, "#e9e4d4"), (lid_c, "#7fb685")]
    # POWER en un panel de muro a la derecha, 10 cm sobre el piso
    px, py, pz = L / 2 + 160, -60.0, 100.0
    wall = cq.Solid.makeBox(260, 12, 420, V(px - 130, py + power.B + 4 + parts.PLATE_T, 0))
    rail_z = pz + power.PAD_H - 5 - 61
    items += [(wall, "#bbbbbb"),
              (S("power_mount_flat").translate(V(px, py + power.B + 4, rail_z)), "#c9a66b"),
              (S("power_body").translate(V(px, py, pz)), "#5b8c85"),
              (S("power_cap").translate(V(px, py, pz + power.H)), "#7fb685")]
    notes = [(0, 0, H + 270, "Torre PVC 6\""),
             (hx + 40, hy, H + 60, "Portasondas\n(pH, TDS, T°)"),
             (lx - 40, ly, H + 70, "Nivel\n(tubo PVC)"),
             (175, -W / 2 - 120, BODY_H + 40, "AQUA"),
             (-160, -W / 2 - 170, z_ctrl + 90, "CTRL-01\n(principal)"),
             (px, py - 60, pz + power.H + 60, "POWER\n(en muro)"),
             (0, -W / 2 - 10, BODY_H + 20, "pinza")]
    render.render(items, out_png, elev=20, azim=-62, size=(12, 9),
                  title="HydroMate: depósito con todos los módulos", notes=notes)

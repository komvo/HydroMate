"""Genera STEP/STL, vistas previas y reporte del ecosistema 3D HydroMate.

Uso (desde cad/):  .venv/Scripts/python build.py [filtro ...] [--no-render]
Ejemplo:           .venv/Scripts/python build.py aqua coupon
"""
import sys
import time
from pathlib import Path

import cadquery as cq

from hydromate_cad import hub, layouts, lid_layout, scene, params as P, parts, pods, power, render

OUT = Path(__file__).parent / "out"
PETG, TPU = "PETG", "TPU 95A"


def _plate_hub(hook):
    rail = hub.PAD_H - 5 - 1
    return parts.mount_plate(140, hub.PAD_H, hub.SLOT_XS, rail, hook=hook)


POWER_RAIL = 60.0


def _plate_power(hook):
    return parts.mount_plate(110, POWER_RAIL + 4, power.SLOT_XS, POWER_RAIL, hook=hook)


def _plate_pod(pod, hook):
    h = pod.h - 8
    return parts.mount_plate(60, h, (0.0,), h - 6, hook=hook)


# nombre: (constructor, material, orientación de impresión)
PARTS = {
    "hub_body": (hub.body, PETG, "piso sobre la cama"),
    "hub_lid": (hub.lid, PETG, "boca abajo: cara superior sobre la cama, sin soportes"),
    "hub_gasket": (hub.gasket, TPU, "plana"),
    "hub_usb_plug": (hub.usb_plug, TPU, "brida sobre la cama"),
    "hub_mount_flat": (lambda: _plate_hub(False), PETG, "cara trasera sobre la cama"),
    "power_body": (power.body, PETG, "piso sobre la cama; 234 mm de alto"),
    "power_cap": (power.cap, PETG, "boca abajo, sin soportes"),
    "power_mount_flat": (lambda: _plate_power(False), PETG, "cara trasera sobre la cama"),
    "aqua_holder": (parts.probe_holder, PETG, "placa sobre la cama, fundas hacia arriba (girar 180°)"),
    "aqua_grommet_ph": (lambda: parts.probe_grommet("ph"), TPU, "brida arriba"),
    "aqua_grommet_tds": (lambda: parts.probe_grommet("tds"), TPU, "brida arriba"),
    "aqua_grommet_temp": (lambda: parts.probe_grommet("temp"), TPU, "brida arriba"),
    "aqua_pod_body": (pods.AQUA.body, PETG, "piso sobre la cama"),
    "aqua_pod_lid": (pods.AQUA.lid, PETG, "boca abajo, sin soportes"),
    "aqua_pod_gasket": (pods.AQUA.gasket, TPU, "plana"),
    "aqua_ph_split_grommet": (pods.split_grommet, TPU, "brida sobre la cama"),
    "aqua_mount_flat": (lambda: _plate_pod(pods.AQUA, False), PETG, "cara trasera sobre la cama"),
    "aqua_cable_sleeve": (parts.cable_sleeve, TPU, "de pie"),
    "light_pod_body": (pods.LIGHT.body, PETG, "piso sobre la cama"),
    "light_pod_lid": (pods.LIGHT.lid, PETG, "boca abajo, sin soportes"),
    "light_pod_gasket": (pods.LIGHT.gasket, TPU, "plana"),
    "level_top": (parts.level_top, PETG, "brida sobre la cama"),
    "level_bracket": (parts.level_bracket, PETG, "boca del casquillo sobre la cama"),
    "coupon_fit": (parts.coupon_fit, PETG, "plana; imprimir PRIMERO"),
    "coupon_rail": (parts.coupon_rail, PETG, "plana; imprimir PRIMERO"),
}


def fits_bed(bb):
    return all(d <= m for d, m in zip(sorted((bb.xlen, bb.ylen, bb.zlen)), sorted(P.BED)))


def assemblies(S):
    T = cq.Vector
    out = {}
    if {"hub_body", "hub_lid", "hub_mount_flat", "power_body", "power_cap"} <= S.keys():
        dx = hub.AD + power.A + 25
        pz = power.PAD_H - 5 - (POWER_RAIL + 1)
        out["asm_ctrl_power"] = [
            (S["hub_mount_flat"].translate(T(0, hub.BD + 4, 0)), "#c9a66b"),
            (S["hub_body"], "#e9e4d4"),
            (S["hub_lid"].translate(T(0, 0, hub.H_BODY)), "#7fb685"),
            (S["power_mount_flat"].translate(T(dx, power.B + 4, pz)), "#c9a66b"),
            (S["power_body"].translate(T(dx, 0, 0)), "#5b8c85"),
            (S["power_cap"].translate(T(dx, 0, power.H)), "#7fb685")]
    if {"aqua_pod_body", "aqua_pod_lid", "aqua_mount_flat"} <= S.keys():
        a = pods.AQUA
        out["asm_aqua_pod"] = [
            (S["aqua_mount_flat"].translate(T(0, a.b + 4, 0)), "#c9a66b"),
            (S["aqua_pod_body"], "#e9e4d4"),
            (S["aqua_pod_lid"].translate(T(0, 0, a.h)), "#7fb685")]
    return out


def main(argv):
    filters = [a for a in argv if not a.startswith("--")]
    do_render = "--no-render" not in argv
    for sub in ("stl", "step", "preview"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    S, rows = {}, []
    for name, (fn, mat, orient) in PARTS.items():
        if filters and not any(f in name for f in filters):
            continue
        t = time.time()
        shape = fn().val()
        bb = shape.BoundingBox()
        ok, fit = shape.isValid(), fits_bed(bb)
        cq.exporters.export(cq.Workplane().add(shape), str(OUT / "stl" / f"{name}.stl"),
                            tolerance=0.05, angularTolerance=0.15)
        cq.exporters.export(cq.Workplane().add(shape), str(OUT / "step" / f"{name}.step"))
        if do_render:
            render.render([(shape, None)], str(OUT / "preview" / f"{name}.png"), title=name)
        S[name] = shape
        dens = 1.27 if mat == PETG else 1.21
        rows.append((name, mat, f"{bb.xlen:.0f}×{bb.ylen:.0f}×{bb.zlen:.0f}",
                     f"{shape.Volume() / 1000 * dens:.0f}", "sí" if fit else "NO",
                     "ok" if ok else "INVÁLIDO", orient))
        print(f"{name:24s} {rows[-1][2]:>14s} cabe={rows[-1][4]} {rows[-1][5]} {time.time() - t:.0f}s",
              flush=True)
    if do_render:
        for name, items in assemblies(S).items():
            render.render(items, str(OUT / "preview" / f"{name}.png"), title=name, elev=18)
    lines = ["# Reporte de generación", "",
             "| Pieza | Material | Caja mm | Masa sólida g* | Cabe K1C | Sólido | Orientación |",
             "|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    lid_layout.draw(str(OUT / "preview" / "lid_layout.png"))
    layouts.draw_all(str(OUT / "preview"))
    if do_render and not filters:
        scene.full(str(OUT / "step"), str(OUT / "preview" / "scene_full.png"))
    lines += ["", "*Masa al 100 % de relleno; la real depende de perímetros y relleno.", "",
              f"Tubo PVC 3/4 in del nivel: cortar a ~{P.level_pipe_len():.0f} mm "
              "(verificar con el flotador montado).",
              f"Holguras en la tapa (mm): {lid_layout.clearances()}", "",
              "## Supuestos por medir antes de la impresión final", ""]
    lines += [f"- {p}" for p in P.pending()]
    report = "REPORT.md" if not filters else "REPORT_parcial.md"
    (OUT / report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    bad = [r[0] for r in rows if r[4] != "sí" or r[5] != "ok"]
    if bad:
        print("REVISAR:", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

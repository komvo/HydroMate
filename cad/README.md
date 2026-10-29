# CAD paramétrico HydroMate (CadQuery)

Modelos 3D como código: cada medida vive en `hydromate_cad/params.py` y todas
las piezas se regeneran desde ahí. Diseño, criterios y pendientes en
[`docs/DESIGN_3D.md`](../docs/DESIGN_3D.md).

## Preparar (una vez, sin instalación global)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install cadquery matplotlib
```

Probado con Python 3.13, CadQuery 2.8.0 y matplotlib 3.11 en Windows 11.

## Generar

```bash
.venv/Scripts/python build.py               # todo (~10 min)
.venv/Scripts/python build.py aqua coupon   # solo piezas cuyo nombre contiene el filtro
.venv/Scripts/python build.py --no-render   # sin PNG
```

Produce `out/stl/*.stl` (imprimir), `out/step/*.step` (abrir/editar en
FreeCAD, Fusion u Onshape), `out/preview/*.png` y `out/REPORT.md` (tamaño,
masa, si cabe en la K1C y supuestos por medir). `out/` es reproducible.

## Estructura

| Archivo | Qué contiene |
|---|---|
| `params.py` | Impresora, holguras, puertos, componentes y medidas por validar |
| `common.py` | Contorno superelipse, puertos en pared curva, riel cola de milano, cunas, grabados |
| `enclosure.py` | Cuerpo sellado, tapa domo, junta TPU, ranuras traseras |
| `hub.py` | CTRL-01: caja electrónica sellada, tapa, tapón USB |
| `power.py` | POWER-01: torre vertical ventilada para la fuente y capuchón |
| `pods.py` | Cápsulas AQUA-01 y LIGHT-01, pasacables partido del pH |
| `parts.py` | Portasondas, arandelas TPU, placas de montaje, colgador de nivel, probetas |
| `render.py` | Vista previa PNG sin interfaz gráfica |
| `scene.py` | Depósito con todos los módulos colocados (`scene_full.png`) |
| `layouts.py`, `lid_layout.py` | Planos 2D: interior de cada módulo, riel y barrenos de la tapa |

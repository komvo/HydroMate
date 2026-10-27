# HydroMate — Jardín líquido

2026-10-27 · Dirección visual vigente D63, solicitada por el usuario: modernizar el
Frutiger Aero/Eco de 0.6 (aspecto de portal web de los 90) con la jerarquía de
materiales translúcidos que Apple describe para Liquid Glass, sin perder el enfoque
ecológico. Dirección anterior (Jardín de cristal, D43) conservada en
[AERO_DESIGN_HISTORY_2026-10-04](AERO_DESIGN_HISTORY_2026-10-04.md).
Estado: implementado y revisado en teléfono con capturas nativas (ver AERO_ACCEPTANCE);
TalkBack y medición de fluidez/contraste pendientes.

## Principios adoptados (adaptados a vistas nativas Android)

- **Dos capas.** Contenido en paneles de vidrio esmerilado; navegación y controles
  en una capa flotante superior. La barra inferior es una cápsula flotante y el
  contenido termina siempre por encima de ella.
- **Material.** El fondo botánico se decodifica una vez; se prepara una copia
  reducida, desenfocada (3 pasadas de caja), con saturación 1.35 y velo. Cada
  superficie muestrea esa copia en su posición de ventana: las hojas se ven
  esmeriladas detrás del vidrio. No hay desenfoque por fotograma ni refracción del
  contenido que pasa debajo; solo del fondo local.
- **Luz.** Borde especular diagonal, brillo superior suave (no el reflejo duro de
  media altura de 0.6), banda de lente interior en controles para sugerir espesor.
- **Formas concéntricas.** Paneles de 26 dp, controles en cápsula, campos de 16 dp,
  pozos circulares para iconos.
- **Estilos** (`GlassStyle`): PANEL, TINTED, FIELD (contenido); CONTROL, PROMINENT,
  SELECTED (controles). No se apila vidrio sobre vidrio: SELECTED no muestrea fondo.
- **Interacción.** Controles crecen 3 % al presionar (150–180 ms); se respeta la
  desactivación de animadores. Foco con anillo verde de 3 dp.
- **Borde de scroll.** Degradado superior de 18 dp que funde el contenido en el velo.

## Ecológico y elementos conservados

Fondo botánico local (`background_botanical.jpg`), emblema de torre, los 16 PNG de
cristal y las cuatro variantes de barra D41 se conservan sin cambios. Nuevo:
hoja nativa (`LeafGlyph`) junto a cada título de sección, decorativa y sin estado.
Paleta día: tinta #10301F, secundario #3B5545, hoja #1F6B35, prominente
#2F7D3E→#1D5A2C con texto blanco. Noche: vidrio verde profundo y texto claro.

## Pantallas

- **Inicio:** (D64: minigráficas, cambio vs. anterior, estado relativo, guía) título grande, recarga en botón circular flotante, tarjeta de cultivo
  con vidrio verde, estado en cápsula con punto (el punto solo repite el tono del
  texto; no indica salud del ESP32), instrumentos tipo widget con valor tabular y
  unidad menor, nivel de agua, fila agrupada hacia Equipo y control.
- **Historial (D64):** titular con último valor y cambio, gráfica de línea con área,
  eje dinámico, promedio, cortes en huecos e inspección táctil; mín./prom./máx.;
  tabla de recepciones con detalle por fila. Análisis en [UX_ANALYSIS](UX_ANALYSIS.md).
- **Cultivo/Control/Más:** listas agrupadas, campos rehundidos, apariencia con
  control segmentado. Textos, estados ausentes y advertencias sin cambios.

Sin cambios a API, BD, firmware, Telemetry, RequestFence, ConnectionStore,
ReadingState ni lógica de MainActivity (solo usa `GlassScaffold` para construir la
vista). Barras del sistema transparentes de borde a borde. Sin dependencias nuevas.
Código: `mobile/app/src/main/java/com/hydromate/mobile/ui/AeroArtwork.kt` y `Components.kt`.

## Contraste (cálculo conservador, sin certificar)

Fondo bajo vidrio supuesto negro tras el velo: tinta ≥9:1 y secundario ≥5:1 sobre
PANEL y CONTROL de día; blanco sobre prominente ≥5:1; noche ≥8:1. Texto sobre el
fondo usa halo del color del velo. Pendiente repetir la medición sobre capturas.

## Referencias consultadas

Solo inspiración de jerarquía y material; no se copiaron recursos ni código.

- [Apple — Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Apple — Liquid Glass overview](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Apple HIG — Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [WWDC25 — Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/)
- Referencias Aero previas: ver el archivo histórico.

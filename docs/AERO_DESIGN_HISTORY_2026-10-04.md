# HydroMate — Jardín de cristal

2026-10-04 · Android 0.6.0-garden. Dirección vigente D43 (aclarado final solicitado por el usuario).
Base: los dos MD Aero Cristal y Eco 90s del usuario; ajustes posteriores del propio
usuario tienen prioridad. La paleta celeste de 0.4/0.5 queda reemplazada por jardín verde
luminoso y cristal verde claro translúcido. Se conserva Frutiger Aero/Eco y el portal ecológico.

## Composición y material

Fondo botánico con hojas naturales en los bordes, agua y centro tranquilo. Imagen
local background_botanical.jpg, 720×1601, 127 952 bytes; se decodifica una sola vez
por contenedor. AeroSky la encuadra sin deformarla y aplica un velo menta luminoso
(#EFFADD, alfa 189 de día; #05190F, alfa 191 de noche). Las plantas son decoración,
no un cultivo activo. No hay carga remota ni animación permanente.

Paneles verde claro (#C7EBA9), superficies #EFFBDD, texto #143B27 y secundario
#36503C. Titulares diurnos sobre el fondo: #143B27 y #294B31; claros en la variante nocturna. AeroSurface mantiene
degradado, bisel, reflejo superior curvo y luz interior; base alfa 110/255 y placa
de lectura alfa 68/255 sobre ella de día. Se ve el follaje a través del cristal;
la zona de datos combina ambas capas para mantener contraste. De noche base
180/255 y placa 130/255. No se promete blur ni refracción dinámica.
Los reflejos quedan dentro del contorno; sombras suaves y foco nativo.

Tema inicial: Jardín con paneles claros. La opción guardada de seguir el sistema
se conserva y usa cristal verde profundo por la noche. Barras del sistema adaptadas
al tema claro/nocturno. Instalar no migra preferencias automáticamente; en el teléfono
de revisión se seleccionó Jardín claro para cumplir la última petición del usuario.

## Iconos y navegación

Emblema botánico original conservado: cabecera/torre, Cultivo y launcher.
Familia de ilustraciones originales de cristal generada con IA, PNG RGBA de
256 px; emblema de 512 px. Sin tintes automáticos.

La corrección de legibilidad D41 afecta **solo** a Inicio, Historial, Control y
Más de la barra: cuatro variantes con volumen y menos reflejos internos a 36 dp.
Cultivo mantiene el emblema a 34 dp. El intento intermedio de sustituir todos los
iconos por glifos simples fue retirado. Components usa el recurso original de
pantalla; únicamente AeroBottomNavigation usa navigationResource.

Cambio D42: pH conserva el matraz; TDS usa un vaso ancho con minerales como símbolo
conceptual, sin indicar composición ni cantidad. Recarga usa una única flecha
circular de cristal azul/verde. Las demás ilustraciones permanecen como estaban.
Prompts completos, procedencia, dimensiones, alfa, SHA-256 y archivo histórico:
[recursos.json](recursos.json). El arte generado no recibe la licencia MIT histórica
de Fluent. No se incorporaron nuevas dependencias de producción.

## Cinco pantallas y adaptación

Inicio conserva un único aviso de consulta, cuatro instrumentos y nivel relativo.
Historial conserva puntos aislados (acabado perlado) y las recepciones reales.
Cultivo y Control mantienen perfiles/integración pendientes sin estados ficticios.
Más conserva conexión, diagnóstico, apariencia y demo explícita solo debug.

Texto nativo en sp y valores tabulares. Dos columnas desde 350 dp con fuente menor
de 1.3; una columna con texto grande. Botones de 52 dp, celdas de barra ≥64 dp.
Historial se abrevia Hist. desde fuente 1.5, con nombre accesible completo.
Iconos decorativos sin foco. Movimiento breve de 150–180 ms, respetando la
desactivación de animadores. Scroll e insets del sistema/teclado conservados.

## Datos y revisión

Sin cambios a API, BD, firmware, rangos, lectura/validación ni consulta. MainActivity
conserva su lógica y el tratamiento original de barras claras/nocturnas. Telemetry,
RequestFence, ConnectionStore y proveedores/fixtures conservan su contenido.
Ausencia de lectura es una raya. Recepción no es captura; luz/nivel son relativos.

VisualCheckActivity existe solo en debug y se abre explícitamente con marca fija
de datos simulados. Configuración local de ancho/fuente, retrato fijo y pantalla
encendida mientras está visible; no modifica ajustes globales, repositorio,
preferencias ni órdenes. No acredita interacción de MainActivity ni giro físico.
Resultados y pendientes: [AERO_ACCEPTANCE.md](AERO_ACCEPTANCE.md).

## Referencias consultadas

Todas accesibles durante esta sesión; solo inspiración de material/composición.
No se copiaron logos, capturas completas, CSS ni código sustancial ajeno.

- [makeaero.com — Botón convexo, reflejo superior curvo y presión.](https://makeaero.com/button)
- [makeaero.com — Volumen de burbuja y reflejo localizado.](https://makeaero.com/orb)
- [makeaero.com — Borde iluminado y espesor aparente; sin controles de escritorio.](https://makeaero.com/window-glass)
- [makeaero.com — Cielo, onda acuática y burbujas periféricas.](https://makeaero.com/wallpaper)
- [github.com — Referencia de implementación; no se copió código ni arte.](https://github.com/Visnalize/makeaero)
- [docs.spline.design — Distinción entre transparencia, espesor y refracción.](https://docs.spline.design/materials-shading/shading-and-reflection/glass-layer)
- [www.meshy.ai — Referencia de primitivas; no se usó el servicio ni se contrató un plan.](https://www.meshy.ai/3d-tools/3d-shape-generator)
- [help.figma.com — Referencia de efectos; no se exportó un diseño Figma.](https://help.figma.com/hc/en-us/articles/360041488473-Apply-effects-to-layers)
- [cari.institute — Gramática histórica Aero; no se reutilizaron imágenes.](https://cari.institute/aesthetics/frutiger-aero)

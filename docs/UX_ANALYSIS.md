# HydroMate — Análisis UX/UI de la app Android

2026-10-27 · Análisis posterior al rediseño Jardín líquido.
Objetivo: que la app enseñe mejor qué está pasando en la torre y que el historial
se entienda de un vistazo. Implementación: D64. Revisión en teléfono: AERO_ACCEPTANCE.

## Restricciones que el diseño debe respetar

- La API entrega como máximo **20 lecturas** recientes por torre; no hay selector de
  día/semana/mes sin cambiar el backend (fuera de alcance).
- **No hay rangos de cultivo** configurados: la app no puede decir «bien» o «mal».
  El color nunca califica un valor; la dirección de un cambio se muestra en texto.
- La API no declara cadencia de muestreo. Las mediciones llegan por evento,
  respaldo de 30 s o solicitud. Unir puntos con línea no debe ocultar huecos.
- Ausente es ausente: nunca se sustituye por cero ni se interpola.

## Principios consultados

| Fuente | Idea aplicada |
|---|---|
| Apple HIG — Charting data | Gráfica simple con detalle bajo demanda; titular que resuma la conclusión; estilo coherente entre gráficas del mismo dato. |
| Apple HIG — Charts / Health | Eje Y dinámico ajustado a los datos; línea con marcas de punto para ver tendencia y valores; resumen (promedio/rango) junto a la gráfica. |
| Apple Stocks / Health | Arrastrar sobre la gráfica muestra el valor y la hora del punto; al soltar vuelve al último. |
| NN/g — Dashboards (atributos preatentivos) | Posición y longitud para cantidades; gráficas de línea para tendencias; no usar color como magnitud ni como único código. |
| Nielsen — 10 heurísticas | Visibilidad del estado; lenguaje del usuario; reconocer en vez de recordar; minimalismo; ayuda contextual. |
| Diseño «glanceable» | El dato clave primero; jerarquía clara; lo que cambia poco va abajo. |
| Apps hidropónicas (Hydrofy, Hydroflow, Growee) | Tendencias por métrica junto al último valor; historial por métrica; indicadores visuales de cambio. |

## Hallazgos en la versión D63

**Historial (problema principal)**
1. La gráfica de puntos aislados forma una retícula de bolitas: no se lee tendencia
   ni magnitud. No tiene eje Y con valores ni marcas de tiempo.
2. No hay titular: el usuario tiene que deducir qué pasó (subió, bajó, se mantuvo).
3. No se puede consultar un punto concreto; los valores están solo en la lista.
4. La lista de 20 recepciones repite párrafos («pH… · Temperatura…») difíciles de
   comparar fila a fila; las etiquetas «Datos de prueba» se repiten 20 veces.
5. Mín./máx. y fechas aparecen como texto suelto bajo la gráfica, sin jerarquía.

**Inicio**
6. «Sin rango configurado» se repite en cada instrumento: ruido sin información nueva.
7. Los instrumentos muestran el valor pero no su contexto (¿cambió desde la lectura
   anterior?). Las tarjetas no llevan al detalle.
8. Todos los valores usan dos decimales (23.00 °C, 510.00 ppm): precisión aparente que
   el sensor no aporta y que dificulta la lectura.
9. El estado muestra una fecha absoluta larga; «hace 3 min» se entiende antes.
10. No se explica cómo llegan los datos ni qué hace «solicitar medición».

**Toda la app**
11. Falta un glosario breve de qué mide cada sensor, en lenguaje del usuario.
12. La carga solo se comunica con texto; un indicador de actividad es más visible.

## Cambios implementados

**Historial**
- **Titular**: último valor grande, cambio entre la primera y la última lectura en
  lenguaje claro («Subió 0.08 en 1 h 16 min») y su número de lecturas.
- **Gráfica de línea con área**: eje Y dinámico con 3 marcas redondeadas, horas de
  inicio/fin, línea de promedio discontinua y último punto resaltado.
  **Huecos visibles**: la línea se corta si el intervalo supera 3× la mediana de los
  intervalos. Así no se dibuja continuidad donde no hubo recepciones. Reemplaza los
  puntos aislados de D43.
- **Inspección**: tocar y arrastrar muestra regla, valor y hora; al soltar vuelve a
  la última lectura. La animación de entrada respeta la desactivación de animaciones.
- **Resumen**: tres datos (mín., promedio, máx.) con la precisión de cada métrica.
- **Qué mide**: explicación breve de la métrica elegida.
- **Tabla de recepciones**: columnas alineadas (hora, pH, °C, TDS, luz). Se resalta la
  métrica elegida, los días van separados por encabezado y cada fila abre su detalle
  completo (agua, secuencia, origen). Las marcas comunes se indican una sola vez. Con
  letra grande se usa una lista apilada.

**Inicio**
- Cada instrumento muestra la **minigráfica** de las últimas lecturas (mismo estilo
  que Historial) y el **cambio desde la lectura anterior** con flecha y texto,
  en color neutro. Tocar abre el Historial de esa métrica.
- Una sola nota de contexto: «Sin rangos de cultivo: los valores no se califican».
- Precisión por métrica: pH 2 decimales, temperatura 1, TDS/luz/EC enteros.
- Estado en lenguaje natural («Última lectura hace 3 min») con hora exacta debajo e
  indicador de actividad mientras se consulta o se solicita una medición.
- Sección **Entender HydroMate**: «Cómo llegan tus datos» y «Qué mide cada sensor».

## Recomendaciones no implementadas (requieren decisión o backend)

- Rangos por cultivo para calificar valores con bandas de referencia en la gráfica
  (perfil de cultivo pendiente; sin objetivos supuestos).
- Selector 24 h / 7 d / 30 d con agregados por hora/día (necesita endpoint de
  historial con ventana y agregación).
- Avisos (FCM) ante cambios bruscos o nivel bajo, cuando exista autenticación.
- Comparar varias métricas en una gráfica normalizada (útil con más datos).

## Fuentes

- [Apple HIG — Charting data](https://developer.apple.com/design/human-interface-guidelines/charting-data)
- [Apple HIG — Charts](https://developer.apple.com/design/human-interface-guidelines/charts)
- [NN/g — Dashboards: preattentive attributes](https://www.nngroup.com/articles/dashboards-preattentive/)
- [Apple Health trends (análisis externo)](https://leancrew.com/all-this/2024/11/apple-health-trends/)
- [Hydrofy en App Store](https://apps.apple.com/app/id6752546729)
- [Glanceable UX](https://uxdesign.cc/glanceable-ux-turning-information-into-instant-understanding-bc2317283ef4)
- [Peripheral displays / glanceability (Berkeley)](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2006/EECS-2006-113.pdf)

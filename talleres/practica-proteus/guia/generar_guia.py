"""Genera T9_PDC_1288703.pdf: explica cada parte del esquemático con recortes señalados.

Uso (desde la raíz del repositorio):
    python -I talleres/practica-proteus/guia/generar_guia.py
Lee hydromate-esquematico.pdf (exportado de Proteus) y escribe el PDF de la guía junto a él.
Las coordenadas de las marcas están en la escala 2000 px de ancho de la hoja renderizada.
"""
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "hydromate-esquematico.pdf"
OUT = BASE / "T9_PDC_1288703.pdf"
DPI = 200
PAGE_W, PAGE_H = 2339, 1654          # A4 horizontal a 200 dpi
MARGIN = 90
FONT_DIR = Path("C:/Windows/Fonts")
F = lambda size, bold=False: ImageFont.truetype(str(FONT_DIR / ("arialbd.ttf" if bold else "arial.ttf")), size)
COLORS = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf", "#e377c2", "#8c564b"]
INK, MUTED = "#1b1b1b", "#555555"


def render_sheets():
    pdf = pdfium.PdfDocument(str(SRC))
    return [pdf[i].render(scale=DPI / 72).to_pil().convert("RGB") for i in range(len(pdf))]


def scale_box(box, sheet):
    k = sheet.width / 2000
    return tuple(round(v * k) for v in box)


def wrap(draw, text, font, width):
    lines = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            test = (line + " " + w).strip()
            if draw.textlength(test, font=font) <= width:
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def new_page(title, subtitle=None):
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    d = ImageDraw.Draw(page)
    d.text((MARGIN, 60), title, font=F(54, True), fill=INK)
    if subtitle:
        d.text((MARGIN, 128), subtitle, font=F(30), fill=MUTED)
    d.line((MARGIN, 178, PAGE_W - MARGIN, 178), fill="#cccccc", width=3)
    d.text((MARGIN, PAGE_H - 60), "HydroMate · Práctica Proteus · Kevin Osmar Valdez Meza · Rev. 1.0",
           font=F(24), fill=MUTED)
    return page, d


def marked_crop(sheet, region, marks, max_w, max_h):
    """Recorta la región, la ajusta a max_w×max_h y dibuja un recuadro numerado por marca.

    Las marcas se dibujan después de escalar para que el grosor y las etiquetas no crezcan con el zoom.
    """
    rx0, ry0, rx1, ry1 = scale_box(region, sheet)
    crop = sheet.crop((rx0, ry0, rx1, ry1))
    k = min(max_w / crop.width, max_h / crop.height)
    crop = crop.resize((round(crop.width * k), round(crop.height * k)), Image.LANCZOS)
    d = ImageDraw.Draw(crop)
    f = F(30, True)
    for n, (box, *_rest) in enumerate(marks, 1):
        x0, y0, x1, y1 = scale_box(box, sheet)
        x0, y0, x1, y1 = [round(v * k) for v in (x0 - rx0, y0 - ry0, x1 - rx0, y1 - ry0)]
        color = COLORS[(n - 1) % len(COLORS)]
        d.rectangle((x0, y0, x1, y1), outline=color, width=5)
        tag = str(n)
        tw = d.textlength(tag, font=f)
        tx = min(max(0, x0), crop.width - tw - 18)
        ty = y0 - 38 if y0 >= 38 else y1 + 2
        d.rectangle((tx, ty, tx + tw + 16, ty + 36), fill=color)
        d.text((tx + 8, ty + 1), tag, font=f, fill="white")
    return crop


def block_page(sheet, title, subtitle, region, marks, note=None):
    """Página: recorte señalado a la izquierda, explicación numerada a la derecha."""
    page, d = new_page(title, subtitle)
    crop = marked_crop(sheet, region, marks, 1300, PAGE_H - 330)
    page.paste(crop, (MARGIN, 215))
    d.rectangle((MARGIN, 215, MARGIN + crop.width, 215 + crop.height), outline="#999999", width=2)

    x = MARGIN + crop.width + 50
    width = PAGE_W - MARGIN - x
    y = 215
    for n, (_box, name, represents, explanation) in enumerate(marks, 1):
        color = COLORS[(n - 1) % len(COLORS)]
        d.rectangle((x, y + 4, x + 40, y + 44), fill=color)
        d.text((x + 11, y + 6), str(n), font=F(30, True), fill="white")
        d.text((x + 55, y + 6), name, font=F(30, True), fill=INK)
        y += 50
        if represents:
            for line in wrap(d, "Representa: " + represents, F(25, True), width):
                d.text((x, y), line, font=F(25, True), fill=color)
                y += 32
        for line in wrap(d, explanation, F(25), width):
            d.text((x, y), line, font=F(25), fill=INK)
            y += 32
        y += 18
    if note:
        y = max(y, 215 + crop.height + 30)
        for line in wrap(d, note, F(25), PAGE_W - 2 * MARGIN if y > 215 + crop.height else width):
            d.text((MARGIN if y > 215 + crop.height else x, y), line, font=F(25), fill=MUTED)
            y += 32
    if y > PAGE_H - 80:
        raise SystemExit(f"Texto desbordado en la página «{title}» (y={y}).")
    return page


def overview_page(sheet, title, subtitle, blocks):
    page, d = new_page(title, subtitle)
    marks = [(box, name, None, "") for box, name in blocks]
    img = marked_crop(sheet, (0, 0, 2000, 1338), marks, PAGE_W - 2 * MARGIN, PAGE_H - 400)
    page.paste(img, (MARGIN, 200))
    y = 215 + img.height
    x = MARGIN
    for n, (_box, name) in enumerate(blocks, 1):
        color = COLORS[(n - 1) % len(COLORS)]
        label = f"{n}. {name}"
        w = d.textlength(label, font=F(28, True)) + 70
        if x + w > PAGE_W - MARGIN:
            x, y = MARGIN, y + 45
        d.rectangle((x, y + 6, x + 30, y + 36), fill=color)
        d.text((x + 42, y + 4), label, font=F(28, True), fill=INK)
        x += w
    return page


def text_page(title, subtitle, paragraphs):
    page, d = new_page(title, subtitle)
    y = 220
    for head, body in paragraphs:
        if head:
            d.text((MARGIN, y), head, font=F(32, True), fill=INK)
            y += 46
        for line in wrap(d, body, F(27), PAGE_W - 2 * MARGIN):
            d.text((MARGIN, y), line, font=F(27), fill=INK)
            y += 36
        y += 22
    if y > PAGE_H - 80:
        raise SystemExit(f"Texto desbordado en la página «{title}» (y={y}).")
    return page


EVIDENCIAS = BASE / "evidencias"


def load_capture(name):
    """Abre una captura de Proteus y recorta la barra de tareas de Windows (≈6 % inferior)."""
    img = Image.open(EVIDENCIAS / name).convert("RGB")
    return img.crop((0, 0, img.width, round(img.height * 0.94)))


def capture_page(title, subtitle, captures, sections):
    """Página de resultado: capturas reales a la izquierda y explicación a la derecha.

    captures: lista de (archivo, pie). sections: lista de (encabezado, texto).
    """
    page, d = new_page(title, subtitle)
    area_w, area_h, top = 1420, PAGE_H - 320, 210
    n = len(captures)
    cols = 1 if n <= 2 else 2
    rows = -(-n // cols)
    cell_w, cell_h = area_w // cols, area_h // rows
    for i, (name, caption) in enumerate(captures):
        img = load_capture(name)
        k = min((cell_w - 20) / img.width, (cell_h - 60) / img.height)
        img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        x = MARGIN + (i % cols) * cell_w
        y = top + (i // cols) * cell_h
        page.paste(img, (x, y))
        d.rectangle((x, y, x + img.width, y + img.height), outline="#999999", width=2)
        label = f"{chr(97 + i)}) {caption}" if n > 1 else caption
        for j, line in enumerate(wrap(d, label, F(22), img.width)[:2]):
            d.text((x, y + img.height + 6 + j * 26), line, font=F(22), fill=MUTED)

    x = MARGIN + area_w + 40
    width = PAGE_W - MARGIN - x
    y = top
    for head, body in sections:
        d.text((x, y), head, font=F(28, True), fill=INK)
        y += 40
        for line in wrap(d, body, F(24), width):
            d.text((x, y), line, font=F(24), fill=INK)
            y += 31
        y += 16
    if y > PAGE_H - 80:
        raise SystemExit(f"Texto desbordado en la página «{title}» (y={y}).")
    return page


def table_page(title, subtitle, headers, rows, widths, note=None, font_size=23):
    """Tabla simple con ajuste de línea por celda."""
    page, d = new_page(title, subtitle)
    f, fb = F(font_size), F(font_size, True)
    lh = font_size + 8
    total = PAGE_W - 2 * MARGIN
    cols = [round(total * w) for w in widths]
    y = 210

    def draw_row(cells, font, fill=None):
        nonlocal y
        wrapped = [wrap(d, c, font, cw - 20) for c, cw in zip(cells, cols)]
        h = max(len(w) for w in wrapped) * lh + 14
        if fill:
            d.rectangle((MARGIN, y, MARGIN + total, y + h), fill=fill)
        x = MARGIN
        for lines, cw in zip(wrapped, cols):
            for j, line in enumerate(lines):
                d.text((x + 10, y + 7 + j * lh), line, font=font, fill=INK)
            x += cw
        d.line((MARGIN, y + h, MARGIN + total, y + h), fill="#cccccc", width=2)
        y += h

    draw_row(headers, fb, fill="#eeeeee")
    for r in rows:
        draw_row(r, f)
    if note:
        y += 20
        for line in wrap(d, note, F(24), total):
            d.text((MARGIN, y), line, font=F(24), fill=MUTED)
            y += 31
    if y > PAGE_H - 80:
        raise SystemExit(f"Texto desbordado en la página «{title}» (y={y}).")
    return page


def report_pages():
    """Secciones 11–21: cálculos, lista de componentes, resultados con capturas y diferencias."""
    pages = []
    pages.append(table_page(
        "11 · Consumo estimado y capacidad de la fuente",
        "Cálculo, no medición física · corrientes típicas de hoja de datos; PH014 sin hoja de datos (supuesto)",
        ["Carga", "Valor de diseño", "Base del cálculo"],
        [
            ["ESP32 con Wi-Fi (picos de transmisión)", "500 mA a 5 V", "hoja de datos; se usa el pico como diseño"],
            ["TDS SEN0244", "6 mA", "hoja de datos del fabricante (3–6 mA)"],
            ["pH PH014", "20 mA", "supuesto; sin hoja de datos"],
            ["ADS1115 + BH1750 + DS18B20", "2 mA", "hojas de datos"],
            ["LED y alarma", "20 mA", "diseño"],
            ["Total lógico", "≈0.55 A a 5 V ≈ 2.75 W", "→ 2.75 W / 0.85 / 24 V ≈ 0.13 A en 24 V (buck η≈85 %)"],
            ["Bomba 24 V / 25 W", "1.04 A nominal", "25 W / 24 V; simulación: 1.02–1.03 A (N3)"],
            ["Arranque de la bomba", "≈3.1 A", "supuesto 3× (modelo 24 V / 7.7 Ω); no medido"],
            ["Un canal de dosificación", "0.5 A a 12 V ≈ 0.29 A en 24 V", "supuesto: 12 V sobre 24 Ω"],
            ["Régimen: bomba + lógica + una dosificación", "≈1.45 A", "29 % de 5 A; 36 % del 80 % utilizable (4 A)"],
            ["Arranque: bomba + lógica + dosificación", "≈3.5 A", "por debajo de 4 A (80 % de la fuente)"],
        ],
        [0.34, 0.26, 0.40],
        note="Conclusión: la fuente de 24 V / 5 A es suficiente siempre que se dosifique un solo canal a la vez, "
             "regla que impone el firmware (F7). La corriente de arranque real debe medirse en el circuito físico."))

    pages.append(table_page(
        "12 · Justificación de reguladores, convertidores y resistencias",
        "Por qué se eligió cada valor",
        ["Componente", "Justificación"],
        [
            ["XL4015 (buck) 24 → 5 V", "Un regulador lineal disiparía (24 − 5) · 0.55 A ≈ 10.5 W; un buck con η≈85 % pierde ≈0.5 W. "
             "Ajuste: Vout = 1.25 · (1 + R2/R1); para 5 V, R2/R1 = 3."],
            ["LM1117-3.3", "(5 − 3.3) · 0.3 A ≈ 0.5 W, admisible. Simulación: 3.30 V con carga de 11 Ω (N1)."],
            ["D1 10TQ045 (Schottky)", "Protege contra polaridad invertida con poca caída (≈0.1 V observado en N1)."],
            ["TVS (zener 1N4751A en simulación)", "Recorta sobretensiones del bus de 24 V; en físico, TVS de la serie SMBJ."],
            ["F1 3.15 A retardado / F2 2 A retardado", "Superan el régimen (1.45 A / 1.04 A) y toleran el arranque. "
             "En Proteus el fusible no tiene retardo (N3a)."],
            ["100 Ω en compuerta", "Limita el pico de corriente al cargar la compuerta del MOSFET."],
            ["10 kΩ compuerta–tierra", "Mantiene el MOSFET apagado si la señal queda flotante (F4)."],
            ["10 kΩ salida del MCU–3.3 V", "Fija «apagado» mientras el microcontrolador se reinicia (F4)."],
            ["IRLZ44N", "Nivel lógico; N3: Vgs 4.95 V, Vds 0.022 V a 1.03 A → Rds ≈ 21 mΩ, P ≈ 23 mW; sin disipador."],
            ["1N4007 (flyback)", "Descarga la energía inductiva al apagar la carga; F5 demuestra su necesidad."],
            ["4.7 kΩ en I2C y 1-Wire", "Valores típicos de hoja de datos para los buses."],
            ["1 kΩ + BAT54 en entradas analógicas", "Limitan corriente y voltaje hacia el ADC (VDD + 0.3 V máx.). F2: deja 3.49 V → mejorar."],
            ["Divisor TDS 4.3 kΩ / 3.6 kΩ", "5 · 3.6 / 7.9 ≈ 2.28 V, dentro del rango 0–2.3 V del SEN0244 (valor de diseño)."],
            ["LED de alarma con 680 Ω", "(3.3 − 2.2) / 680 ≈ 1.6 mA."],
        ],
        [0.30, 0.70], font_size=22))

    pages.append(table_page(
        "13 · Lista de componentes (simulación ↔ circuito físico)",
        "Componentes del esquemático y lo que representan",
        ["Función", "En Proteus", "Componente físico", "Cant."],
        [
            ["Fuente", "batería 24 V (J1)", "fuente 24 V / 5 A (comprada)", "1"],
            ["Convertidores", "riel +5V (U1) y fuente 12 V (U2)", "XL4015 (comprados)", "2"],
            ["Regulador 3.3 V", "LM1117DT-3.3 (U3)", "regulador del DevKit ESP32", "1"],
            ["Protección de entrada", "FUSE 3.15 A, 10TQ045, 1N4751A, 470 µF", "fusible retardado, Schottky, TVS, electrolítico", "1 c/u"],
            ["Controlador", "ATmega328P (U4)", "ESP32 DevKit", "1"],
            ["ADC", "ADS1015 (U5)", "ADS1115 (comprado)", "1"],
            ["Sondas", "POT-HG RV1, RV2 + divisor", "pH PH014, TDS Meter V1.0", "2"],
            ["Temperatura", "DS18B20 (U6)", "kit DS18B20 (comprado)", "1"],
            ["Nivel", "SW-SPST (SW6)", "flotador (comprado)", "1"],
            ["Protección de entradas", "BAT54 + 1 kΩ", "igual", "2"],
            ["Interbloqueo", "74HCT02 (U7, U8)", "igual (propuesto)", "2"],
            ["Drivers", "IRLZ44N + 100 Ω + 10 kΩ + 1N4007", "módulo MOSFET Noyito (D4184) u otro driver", "5 canales"],
            ["Bomba", "MOTOR-DC 24 V (M1) + F2 2 A", "bomba 24 V / 25 W (seleccionada)", "1"],
            ["Dosificación", "resistencias de 24 Ω", "mecanismo A/B/Up/Down pendiente", "4"],
            ["Alarma / reinicio", "LED + 680 Ω; SW7 + 10 kΩ", "igual", "1 c/u"],
            ["Órdenes", "SW-SPST (SW1–SW5)", "órdenes MQTT desde Android", "5"],
            ["Luz", "—", "BH1750 (sin modelo; fuera de la simulación)", "1"],
            ["Instrumentos", "voltímetros, amperímetro, osciloscopio, terminal, depurador I2C", "no forman parte del circuito", "—"],
        ],
        [0.17, 0.33, 0.38, 0.12], font_size=22))

    pages.append(table_page(
        "14 · Resumen de simulaciones",
        "Todo lo siguiente se observó en Proteus 8.13; no son mediciones del circuito físico",
        ["ID", "Tipo", "Condición", "Resultado observado"],
        [
            ["N1", "Normal", "Alimentación con la bomba apagada", "+24V 23.9 V; +5V 5.00 V; 3V3_LDO 3.30 V"],
            ["N2", "Normal", "Sensores en valores de referencia", "T 23.5 °C; pH 7.09 (1.251 V); TDS 773 ppm (1.788 V)"],
            ["N3", "Normal", "Bomba encendida", "1.02–1.03 A; Vgate 4.95 V; Vdrenador 0.022 V"],
            ["N3a", "Límite", "Arranque con F2 de 2 A sin retardo", "F2 se funde; corriente 0 A"],
            ["F1", "Falla", "Nivel bajo con orden de bomba", "Bomba bloqueada por firmware y por la NOR"],
            ["F2", "Falla", "Sonda de pH a 5 V", "pH INVALIDO, alarma; ADC recibe 3.49 V"],
            ["F4", "Falla", "Reinicio (pines en alta impedancia)", "Bomba apagada; Vgate ≈ 0 V"],
            ["F5", "Falla", "Corte de la bomba sin diodo flyback", "Drenador ≥ 44.5 V; con diodo < 30 V"],
            ["F7", "Falla", "pH Up y pH Down a la vez", "Ninguno se activa; CONFLICTO y alarma"],
        ],
        [0.07, 0.10, 0.36, 0.47],
        note="Instrumentos usados: voltímetros y amperímetro DC, sondas de voltaje, osciloscopio, terminal virtual, "
             "depurador I2C y breakpoint analógico. Condición común: MCU a 16 MHz (build-16mhz)."))

    pages.append(capture_page("15 · N1 · Alimentación", "Funcionamiento normal",
        [("N1_voltajes_bomba_off.jpg", "Voltímetros de +24V, +5V y 3V3_LDO durante la simulación")],
        [("Qué se hizo", "Se corrió la simulación con la bomba apagada y se leyeron los tres voltímetros."),
         ("Qué se observó", "+24V = 23.9 V; +5V = 5.00 V; 3V3_LDO = 3.30 V con la carga de prueba de 11 Ω."),
         ("Explicación", "Los tres rieles están en su valor nominal. Los 0.1 V que faltan en 24 V se deben a la caída "
          "del diodo de polaridad D1. El LM1117 regula correctamente con ≈0.3 A de carga.")]))

    pages.append(capture_page("16 · N2 · Lectura de sensores", "Funcionamiento normal",
        [("N2_terminal_sensores.jpg", "Terminal virtual con las lecturas del firmware")],
        [("Qué se hizo", "RV1 en 1.251 V (pH), RV2 en 1.788 V (TDS), DS18B20 en 23.5 °C y flotador cerrado (con agua)."),
         ("Qué se observó", "T=23.5 pH=7.09 (1.251 V) TDS=773 (1.788 V) NIVEL=OK ALARMA=NO. El ADS1015 responde en 0x48."),
         ("Explicación", "El firmware convierte los voltajes con las mismas fórmulas del firmware real. 773 ppm coincide "
          "con la lectura física del 21/10 (≈770 ppm a 23.5 °C). El pH sale de las constantes históricas, no de una "
          "calibración nueva. La captura es anterior al llenado del cajetín.")]))

    pages.append(capture_page("17 · N3 · Bomba encendida y límite del fusible", "Funcionamiento normal y condición límite",
        [("N3a_F2_2A_fundido_arranque.jpg", "N3a: F2 de 2 A se funde en el arranque"),
         ("N3c_bomba_Vgate_Vdrain_1.03A.jpg", "N3: con F2 provisional de 4 A, 1.03 A, Vgate 4.95 V, Vdrenador 0.022 V")],
        [("Qué se hizo", "Se cerró la orden de bomba (SW1) con agua (SW6). Primero con F2 = 2 A y luego con 4 A provisional."),
         ("Qué se observó", "Con 2 A el fusible se funde al arrancar (I = 0 A). Con 4 A: 1.02–1.03 A en régimen, "
          "Vgate = 4.95 V, Vdrenador = 0.022 V. Captura adicional: N3b_bomba_ON_1.02A.jpg."),
         ("Explicación", "El MOSFET satura por completo: Rds ≈ 21 mΩ y ≈23 mW, sin necesidad de disipador. El arranque del "
          "motor pide más que 2 A durante un instante; el fusible de Proteus no tiene retardo, por eso se funde. En el "
          "circuito físico se usa un fusible retardado y hay que medir la corriente de arranque real. El proyecto quedó "
          "de nuevo con F2 = 2 A.")]))

    pages.append(capture_page("18 · F1 · Nivel bajo", "Falla: el flotador indica que falta agua",
        [("F1_nivel_bajo_bomba_inhibida.jpg", "Flotador abierto con la orden de bomba activa")],
        [("Qué se hizo", "Se abrió SW6 (flotador) manteniendo cerrada la orden de bomba SW1."),
         ("Qué se observó", "Terminal: NIVEL=BAJO BOMBA=OFF. Salida de la NOR ≈ 0 V, Vgate ≈ 0 V, Vdrenador = 23.9 V, "
          "corriente 0 A."),
         ("Explicación", "La bomba se bloquea dos veces: el firmware no la ordena y la compuerta NOR del 74HCT02 bloquea "
          "la señal aunque el firmware fallara. Así se evita que la bomba trabaje en seco.")]))

    pages.append(capture_page("19 · F2 · Sensor fuera de rango", "Falla: la sonda de pH entrega 5 V",
        [("F2_pH_5V_clamp_invalido.jpg", "RV1 al 100 % (5 V): AIN0 ≈ 3.49 V y pH INVALIDO")],
        [("Qué se hizo", "RV1 al 100 % para simular un módulo de pH alimentado a 5 V o en falla."),
         ("Qué se observó", "Terminal: pH=INVALIDO (3.486 V), ALARMA=SI. En AIN0 del ADC hay ≈3.49 V."),
         ("Explicación", "El firmware descarta la lectura en lugar de inventar un valor. R1 limita la corriente del clamp a "
          "≈1.5 mA. Hallazgo de diseño: 3.49 V supera en ≈0.19 V el máximo absoluto del ADS1115 (VDD + 0.3 V). "
          "Antes del montaje conviene alimentar el módulo de pH a 3.3 V, agregar un divisor como el de TDS o usar un "
          "clamp de menor caída.")]))

    pages.append(capture_page("20 · F4 · Reinicio del microcontrolador", "Falla: el microcontrolador deja de controlar sus pines",
        [("F4_pines_alta_impedancia_bomba_OFF.jpg", "Pines en alta impedancia: bomba apagada (resultado usado)"),
         ("F4a_RST_0V_modelo_sigue_ejecutando.jpg", "Intento con RST a 0 V: el modelo siguió ejecutando (descartado)"),
         ("F4b_MCU_excluido_sin_riel_3V3_bomba_ON.jpg", "Intento excluyendo el MCU: desaparece el riel 3.3 V (descartado)")],
        [("Qué se hizo", "Se cargó un firmware vacío (setup(){} loop(){}) que deja todos los pines como entradas, igual que "
          "un AVR durante el reset, con orden de bomba y agua presentes."),
         ("Qué se observó", "Salida de la NOR ≈ 0 V, Vgate ≈ 0 V, Vdrenador = 23.87 V: la bomba no gira."),
         ("Explicación", "Las pull-ups de 10 kΩ dejan la orden en «apagado» y el pull-down mantiene el MOSFET apagado. "
          "Los dos intentos descartados (b y c) muestran limitaciones del modelo, no del circuito. Falta comprobar en el "
          "ESP32 real los estados de sus GPIO durante el arranque.")]))

    pages.append(capture_page("21 · F5 · Sin diodo flyback", "Falla: se retira D6 y se apaga la bomba",
        [("F5a_sin_flyback_pico_VD_44V.jpg", "Sin D6: breakpoint a t = 2.173 s con VD = 44.48 V"),
         ("F5b_sin_flyback_despues.jpg", "Sin D6, después del corte: el motor gira por inercia"),
         ("F5c_con_flyback_sin_pico.jpg", "Con D6: el breakpoint de 30 V no se dispara (VD = 14.4 V)")],
        [("Qué se hizo", "Se excluyó D6 y se fijó un breakpoint analógico que detiene la simulación si el drenador supera 30 V; "
          "luego se abrió la orden de bomba. Se repitió con D6."),
         ("Qué se observó", "Sin D6 el breakpoint se disparó con VD = 44.48 V (instante del disparo, no el pico máximo). "
          "Con D6 no se disparó."),
         ("Explicación", "Al cortar la corriente, la inductancia del motor eleva el drenador por encima de la alimentación, "
          "lo que pone en riesgo al MOSFET. El diodo descarga esa energía. Se usó breakpoint en lugar de la pantalla del "
          "osciloscopio porque la simulación era demasiado lenta. El modelo no incluye la avalancha del IRLZ44N.")]))

    pages.append(capture_page("22 · F7 · pH Up y pH Down a la vez", "Falla: órdenes contradictorias",
        [("F7_conflicto_UP_DOWN.jpg", "Terminal: UP=OFF DOWN=OFF CONFLICTO ALARMA=SI"),
         ("F7_parcial_UP_DOWN_gates.jpg", "Compuertas de Q4 y Q5 ≈ 0 V")],
        [("Qué se hizo", "Se cerraron a la vez SW3 (pH Up) y SW4 (pH Down) con agua y bomba encendida."),
         ("Qué se observó", "Ninguno de los dos canales se activa; la terminal marca CONFLICTO y la alarma se enciende."),
         ("Explicación", "Se evita agregar ácido y base al mismo tiempo. Este bloqueo lo hace solo el firmware; el 74HCT02 "
          "bloquea únicamente por nivel. Una mejora futura sería un bloqueo físico entre ambos canales.")]))

    pages.append(text_page("23 · Diferencias entre la simulación y el circuito físico", "Qué no representa la simulación", [
        ("Controlador", "El ATmega328P sustituye al ESP32: otra CPU, otro ADC, sin Wi-Fi ni MQTT; las órdenes son "
         "interruptores. Corre a 16 MHz para que el modelo DS18B20 responda, fuera de especificación a 3.3 V."),
        ("Sensores", "pH y TDS son voltajes ajustables, sin química, deriva, ruido ni calibración. El DS18B20 se alimenta a "
         "5 V en la simulación (el modelo no responde a 3.3 V) y cerca de la mitad de sus lecturas salen inválidas. "
         "ADS1015 (12 bits) en lugar de ADS1115 (16 bits). El BH1750 no tiene modelo."),
        ("Alimentación", "Los XL4015 son fuentes ideales, sin rizado ni eficiencia real. La lógica usa el riel ideal +3V3 "
         "que crea Proteus y no la salida del LM1117 (3V3_LDO), que se prueba por separado; en el circuito físico el "
         "regulador alimenta toda la lógica."),
        ("Protecciones", "El TVS se representa con un zener; el fusible no modela retardo."),
        ("Potencia", "La bomba es un motor DC genérico (7.7 Ω, 10 mH) y la real es brushless con electrónica interna. Los "
         "D4184 del módulo Noyito se representan con IRLZ44N. La dosificación son cargas resistivas porque el mecanismo "
         "está pendiente. No se modela la avalancha del MOSFET."),
        ("Procedimiento", "Los interruptores no se accionaron durante la simulación salvo en F5; cada caso se fijó y se corrió "
         "por separado. Algunas capturas son anteriores al llenado del cajetín."),
        ("Fuera de alcance", "Nube, backend, base de datos y Android, como permite la práctica. Las fallas de comunicación se "
         "probarán en la integración de software."),
    ]))
    return pages


def main():
    h1, h2 = render_sheets()
    pages = []

    pages.append(text_page(
        "Circuito y simulación de HydroMate en Proteus",
        "Explicación del circuito, cálculos, resultados de simulación y diferencias con el circuito físico",
        [
            ("Propósito", "Este documento recorre las dos hojas del esquemático (proteus/hydromate.pdsprj, exportado en "
             "hydromate-esquematico.pdf). Secciones 1–10: cada parte del dibujo con recuadros numerados, a qué componente "
             "real representa y por qué se modeló así. Secciones 11–13: cálculos, justificación y lista de componentes. "
             "Secciones 14–22: simulaciones con capturas y explicación de resultados. Sección 23: diferencias con el "
             "circuito físico."),
            ("Por qué hay equivalentes", "Proteus 8.13 no trae modelos simulables del ESP32, del ADS1115, del BH1750, "
             "del XL4015 ni de las sondas químicas de pH y TDS. Donde no hay modelo confiable se usa un componente o "
             "señal equivalente que cumple la misma función eléctrica, y se señala sobre el dibujo y en esta guía."),
            ("Cómo leer los instrumentos", "En el PDF del esquemático los voltímetros y amperímetros muestran +88.8: "
             "es su marcador cuando la simulación no corre, no una medición. Los valores medidos aparecen en las capturas "
             "de las secciones 15–22, tomadas con la simulación en marcha."),
            ("Convenciones", "Recuadro numerado = parte explicada. «Representa» = componente del circuito físico. "
             "Los valores marcados como supuesto no se han confirmado con el hardware real."),
            ("Hojas", "Hoja 1: alimentación, microcontrolador, sensores, alarma, reinicio e instrumentos. "
             "Hoja 2: cinco canales de salida (bomba, nutriente A, nutriente B, pH Up, pH Down) con interbloqueo por "
             "nivel, órdenes simuladas y flotador."),
        ]))

    pages.append(overview_page(h1, "Hoja 1 · vista general", "Alimentación, lógica y sensores", [
        ((430, 340, 720, 530), "Entrada 24 V y protecciones"),
        ((745, 300, 1140, 580), "Convertidores y regulador"),
        ((1090, 260, 1920, 640), "Microcontrolador y terminal"),
        ((1095, 640, 1900, 1090), "Sensores pH/TDS y ADC"),
        ((1500, 940, 1965, 1110), "Temperatura e I2C"),
        ((95, 680, 610, 1245), "Alarma, nivel, reinicio, carga LDO"),
        ((300, 850, 1170, 1230), "Instrumentos virtuales"),
        ((320, 100, 840, 185), "Notas de simulación"),
    ]))

    pages.append(block_page(h1, "1 · Entrada de 24 V y protecciones", "Hoja 1, zona B–D / 2–4",
        (400, 330, 740, 540), [
        ((430, 375, 500, 520), "J1 · fuente de 24 V", "fuente conmutada de 24 V / 5 A (comprada)",
         "Batería ideal de 24 V que alimenta todo el circuito. No modela rizado ni límite de corriente."),
        ((490, 360, 555, 405), "F1 · fusible 3.15 A", "fusible retardado de 3.15 A",
         "Abre el circuito ante un cortocircuito. El régimen estimado es ≈1.45 A y el arranque ≈3.5 A; el modelo de Proteus no tiene retardo."),
        ((640, 355, 710, 410), "D1 · 10TQ045 (Schottky)", "diodo de protección de polaridad",
         "Bloquea la corriente si la fuente se conecta al revés; al ser Schottky cae poco voltaje (≈0.1 V observado)."),
        ((595, 415, 640, 520), "TVS · zener 1N4751A (30 V)", "supresor TVS (p. ej. serie SMBJ)",
         "Recorta picos de sobretensión en la línea de 24 V. Proteus no trae un TVS simulable, por eso se usa un zener de función equivalente."),
        ((650, 410, 725, 520), "C1 · 470 µF", "capacitor electrolítico de 470 µF / 35 V",
         "Reserva de energía local: amortigua caídas de voltaje cuando arranca la bomba."),
    ]))

    pages.append(block_page(h1, "2 · Convertidores equivalentes y regulador de 3.3 V", "Hoja 1, zona D–F / 2–4",
        (740, 295, 1150, 585), [
        ((750, 395, 835, 545), "U1 · fuente de 5 V", "XL4015 #1 (convertidor buck 24 V → 5 V)",
         "Fuente ideal que entrega el riel +5V para la lógica. Un buck pierde ≈0.5 W donde un regulador lineal perdería ≈10.5 W."),
        ((835, 300, 960, 410), "U3 · LM1117-3.3", "regulador de 3.3 V del DevKit ESP32",
         "Baja de 5 V a 3.3 V. Su salida es la red 3V3_LDO, probada con una carga de 11 Ω (3.30 V en N1)."),
        ((990, 385, 1075, 560), "U2 · fuente de 12 V", "XL4015 #2 (supuesto: 12 V para dosificación)",
         "Alimenta las cargas de los canales A, B, pH Up y pH Down. El voltaje real de dosificación está pendiente."),
        ((620, 532, 1140, 578), "Notas de equivalencia", None,
         "Textos sobre el dibujo que identifican cada fuente con el convertidor que sustituye."),
    ], note="Separación +3V3 / 3V3_LDO: la lógica usa el riel ideal +3V3 que crea Proteus para el ATmega; unir ese riel "
            "con la salida del LM1117 detenía la simulación. El dibujo prueba el regulador por separado; en el circuito "
            "físico el regulador alimenta toda la lógica."))

    pages.append(block_page(h1, "3 · Microcontrolador y terminal virtual", "Hoja 1, zona F–J / 1–4",
        (1090, 255, 1925, 640), [
        ((1485, 375, 1785, 615), "U4 · ATmega328P", "ESP32 DevKit",
         "Ejecuta el firmware didáctico (firmware-sim/build-16mhz). Lee sensores y aplica las reglas de seguridad: sin agua no hay bomba, una dosificación a la vez, nunca Up y Down juntos, máximo 5 s por orden."),
        ((1785, 375, 1915, 445), "Salidas activas en bajo", "GPIO25/13/14/18/19 y 23 del ESP32 (preliminares)",
         "BOMBA_N, DOSA_N, DOSB_N, PHUP_N, PHDN_N y ALARMA van a la hoja 2 por etiqueta de red."),
        ((1785, 495, 1915, 595), "Entradas de orden e I2C", "órdenes MQTT; bus I2C GPIO21/22",
         "ORD_BOMBA…ORD_UP llegan de interruptores; SDA/SCL conectan con el ADC; RST con el botón de reinicio."),
        ((1100, 265, 1335, 380), "Terminal virtual", "monitor serie del ESP32",
         "Muestra lo que el programa lee y decide (T, pH, TDS, NIVEL, estado de salidas, ALARMA)."),
    ], note="Diferencia: el ATmega no tiene Wi-Fi ni MQTT y en la simulación corre a 16 MHz para que el modelo DS18B20 "
            "responda; eso está fuera de especificación a 3.3 V y solo vale para la simulación."))

    pages.append(block_page(h1, "4 · Sensores de pH y TDS y convertidor analógico-digital", "Hoja 1, zona F–I / 5–8",
        (1095, 635, 1905, 1090), [
        ((1145, 745, 1225, 850), "RV1 · potenciómetro", "sonda de pH + módulo PH014",
         "Produce a mano el voltaje que daría la sonda (1.251 V ≈ pH 7). Puede llegar a 5 V para provocar la falla F2."),
        ((1145, 915, 1225, 1020), "RV2 · potenciómetro", "módulo TDS Meter V1.0 / SEN0244",
         "Voltaje equivalente a la conductividad (1.788 V ≈ 773 ppm a 23.5 °C)."),
        ((1270, 895, 1410, 1060), "R3 4.3 kΩ / R4 3.6 kΩ", "divisor de acondicionamiento",
         "Limita la señal TDS a ≈2.28 V, dentro del rango 0–2.3 V del módulo."),
        ((1400, 680, 1510, 900), "R1, R2 1 kΩ + D2, D3 BAT54", "protección de entradas",
         "La resistencia limita la corriente y el diodo desvía el exceso de voltaje hacia 3.3 V. F2 mostró que deja ≈3.49 V: hallazgo de diseño."),
        ((1560, 740, 1720, 875), "U5 · ADS1015 (0x48)", "ADS1115 de 16 bits",
         "Convierte A0 (pH) y A1 (TDS) a números y los envía por I2C. Es el modelo de 12 bits con el mismo manejo."),
        ((1765, 660, 1865, 730), "R5, R6 4.7 kΩ", "pull-ups del bus I2C",
         "Mantienen SDA y SCL en alto cuando nadie transmite; valor típico de hoja de datos."),
    ]))

    pages.append(block_page(h1, "5 · Temperatura y depurador I2C", "Hoja 1, zona H–J / 6–8",
        (1495, 935, 1965, 1115), [
        ((1595, 980, 1720, 1065), "U6 · DS18B20", "sensor de temperatura DS18B20 (kit comprado)",
         "Modelo propio de Proteus; se fija en 23.5 °C. Se comunica por un solo cable (T_1W, 1-Wire)."),
        ((1515, 940, 1565, 1045), "R7 · 4.7 kΩ", "pull-up del bus 1-Wire",
         "Necesaria para que el sensor pueda responder. En la simulación va a 5 V porque el modelo no responde a 3.3 V."),
        ((1820, 955, 1960, 1045), "Depurador I2C", "instrumento virtual (no existe en el circuito)",
         "Muestra los mensajes entre el microcontrolador y el ADS1015; sirvió para diagnosticar las lecturas."),
    ], note="Diferencia: en la simulación cerca de la mitad de las lecturas salen T=INVALIDA; el firmware enciende la "
            "alarma y compensa el TDS con la referencia de 25 °C, igual que el firmware real."))

    pages.append(block_page(h1, "6 · Alarma, nivel, reinicio y carga de prueba del LDO", "Hoja 1, zona A–C / 5–9",
        (95, 680, 610, 1245), [
        ((185, 690, 430, 815), "R18 680 Ω + D9 LED", "indicador de alarma (GPIO23 preliminar)",
         "Se enciende ante nivel bajo, sensor inválido o conflicto. 680 Ω limitan la corriente a ≈1.6 mA."),
        ((235, 810, 285, 950), "R28 · 10 kΩ en NIVEL", "pull-up de la entrada del flotador",
         "Mantiene NIVEL en alto (sin agua) cuando el flotador está abierto; si el cable se corta, el sistema lo trata como nivel bajo."),
        ((105, 960, 245, 1240), "SW7 + R30 10 kΩ", "botón de reinicio",
         "Lleva RST a 0 V. El modelo de Proteus siguió ejecutando, por eso F4 se demostró con pines en alta impedancia."),
        ((520, 790, 600, 1000), "R29 · 11 Ω", "carga de prueba del regulador",
         "Consume ≈0.3 A de 3V3_LDO para comprobar que el LM1117 regula con carga (3.30 V)."),
    ]))

    pages.append(block_page(h1, "7 · Instrumentos virtuales y notas", "Hoja 1, zona B–F / 0–9",
        (300, 840, 1175, 1235), [
        ((320, 1030, 385, 1195), "Voltímetro +24V", "medición de la entrada",
         "N1: 23.9 V con la bomba apagada."),
        ((690, 1030, 755, 1195), "Voltímetro +5V", "medición del riel lógico",
         "N1: 5.00 V."),
        ((850, 860, 915, 1045), "Voltímetro 3V3_LDO", "medición del regulador",
         "N1: 3.30 V con la carga de 11 Ω."),
        ((965, 1100, 1165, 1220), "Osciloscopio", "instrumento virtual",
         "Canales: T_1W, VG_BOMBA (compuerta) y VD_BOMBA (drenador) para ver el encendido de la bomba."),
        ((330, 1195, 870, 1215), "Nota +88.8", None,
         "Aclara que +88.8 es el marcador sin simulación; los valores están en las capturas."),
    ]))

    pages.append(overview_page(h2, "Hoja 2 · vista general", "Salidas de potencia, interbloqueo y órdenes", [
        ((200, 35, 900, 430), "Canal nutriente A"),
        ((200, 460, 900, 855), "Canal nutriente B"),
        ((1090, 35, 1780, 430), "Canal pH Up"),
        ((1090, 460, 1780, 855), "Canal pH Down"),
        ((200, 810, 1115, 1285), "Canal bomba"),
        ((1115, 880, 1665, 1225), "Órdenes y flotador"),
    ]))

    pages.append(block_page(h2, "8 · Canal de la bomba (circuito típico de salida)", "Hoja 2, zona A–F / 6–9",
        (195, 805, 1120, 1290), [
        ((200, 880, 300, 975), "R19 · 10 kΩ a +3V3", "pull-up de BOMBA_N",
         "Mientras el microcontrolador se reinicia, sus pines quedan sueltos; esta resistencia deja la orden en «apagado»."),
        ((240, 980, 405, 1080), "U7:C · compuerta NOR 74HCT02", "interbloqueo físico por nivel",
         "Salida = NOR(NIVEL, BOMBA_N): solo enciende si hay agua Y el micro lo ordena. También convierte 3.3 V en 5 V."),
        ((490, 1005, 545, 1050), "R16 · 100 Ω", "resistencia de compuerta",
         "Suaviza el pico de corriente al cargar la compuerta del MOSFET."),
        ((610, 1140, 650, 1280), "R17 · 10 kΩ", "pull-down de compuerta",
         "Mantiene el MOSFET apagado si la señal queda flotante."),
        ((695, 1055, 820, 1130), "Q3 · IRLZ44N", "MOSFET del módulo Noyito (D4184)",
         "Interruptor electrónico de la bomba. N3: Vgs 4.95 V, Vds 0.022 V con 1.03 A (≈23 mW)."),
        ((820, 950, 905, 1000), "D6 · 1N4007", "diodo flyback",
         "Descarga la energía del motor al apagarlo. F5: sin él el drenador llegó a ≥44 V; con él no pasó de 30 V."),
        ((940, 950, 1090, 1020), "M1 · MOTOR-DC 24 V", "bomba de recirculación 24 V / 25 W (brushless)",
         "Motor genérico de 7.7 Ω; la bomba real tiene electrónica interna."),
        ((815, 815, 1110, 905), "F2 2 A + amperímetro", "fusible retardado de rama",
         "Protege la rama de la bomba; el amperímetro mide su corriente (1.02–1.03 A)."),
    ]))

    pages.append(block_page(h2, "9 · Canales de dosificación A, B, pH Up y pH Down", "Hoja 2, zona A–I / 0–6",
        (195, 30, 1785, 860), [
        ((200, 35, 900, 430), "Canal A (Q1)", "dosificación de nutriente A (GPIO13 preliminar)",
         "Misma estructura que el canal de la bomba: pull-up, NOR con NIVEL, 100 Ω, 10 kΩ, IRLZ44N y diodo."),
        ((200, 460, 900, 855), "Canal B (Q2)", "dosificación de nutriente B (GPIO14 preliminar)",
         "Igual al canal A."),
        ((1090, 35, 1780, 430), "Canal pH Up (Q4)", "dosificación de pH Up (GPIO18 preliminar)",
         "F7: si se ordena junto con pH Down, el firmware no activa ninguno y marca CONFLICTO."),
        ((1090, 460, 1780, 855), "Canal pH Down (Q5)", "dosificación de pH Down (GPIO19 preliminar)",
         "Igual a pH Up; la exclusión Up/Down es por firmware."),
        ((735, 75, 860, 145), "R10/R14/R22/R26 · 24 Ω", "mecanismo de dosificación (pendiente)",
         "Carga resistiva genérica a 12 V (0.5 A, supuesto); no se presupone bomba peristáltica."),
    ]))

    pages.append(block_page(h2, "10 · Órdenes simuladas y flotador", "Hoja 2, zona F–I / 6–9",
        (1110, 875, 1670, 1230), [
        ((1120, 880, 1225, 1030), "SW1 · ORD_BOMBA", "orden de bomba enviada por MQTT",
         "Cerrado = se pide encender la bomba."),
        ((1240, 910, 1340, 1030), "SW2 · ORD_A", "orden de dosis A", "Cerrado = se pide dosificar A."),
        ((1345, 895, 1445, 1020), "SW5 · ORD_B", "orden de dosis B", "Cerrado = se pide dosificar B."),
        ((1465, 905, 1560, 1030), "SW3 · ORD_UP", "orden de pH Up", "Cerrado = se pide subir el pH."),
        ((1570, 895, 1665, 1020), "SW4 · ORD_DN", "orden de pH Down", "Cerrado = se pide bajar el pH."),
        ((1195, 1060, 1320, 1130), "SW6 · flotador (NIVEL)", "sensor flotador de nivel",
         "Cerrado = hay agua (NIVEL en bajo). Abierto = nivel bajo: el firmware y las compuertas NOR apagan las salidas (F1)."),
    ], note="Los interruptores no se accionaron durante la simulación: cada caso se fijó antes de correrla. "
            "En el sistema real las órdenes llegan desde Android por MQTT."))

    pages.extend(report_pages())
    pages.insert(1, table_page(
        "Cumplimiento de requisitos", "Dónde se atiende cada requisito de la práctica",
        ["Requisito", "Dónde"],
        [
            ["Archivo editable de Proteus / circuito en PDF", "proteus/hydromate.pdsprj · hydromate-esquematico.pdf"],
            ["Componentes, señales y conectores identificados", "Secciones 1–10 y 13; notas y etiquetas de red sobre el dibujo. "
             "Conector dibujado: J1 (24 V); sensores y cargas se unen por etiqueta de red"],
            ["Etapa de alimentación", "Secciones 1–2"],
            ["Etapa lógica", "Sección 3"],
            ["Entradas y salidas críticas", "Secciones 4–6 (entradas) y 8–10 (salidas)"],
            ["Protecciones necesarias", "Secciones 1, 4, 8 y 12"],
            ["Consumo estimado y capacidad de la fuente", "Sección 11"],
            ["Justificación de resistencias, reguladores y convertidores", "Sección 12"],
            ["Lista actualizada de componentes", "Sección 13"],
            ["Simulación de funcionamiento normal", "Secciones 14–17 (N1, N2, N3)"],
            ["Condición límite o falla relevante", "Secciones 17–22 (N3a, F1, F2, F4, F5, F7)"],
            ["Mediciones con instrumentos virtuales", "Capturas de las secciones 15–22; instrumentos en la sección 7"],
            ["Explicación de resultados", "Secciones 15–22, apartado «Explicación»"],
            ["Diferencias entre simulación y circuito físico", "Sección 23 y notas en cada sección"],
        ],
        [0.45, 0.55]))
    for i, page in enumerate(pages, 1):
        d = ImageDraw.Draw(page)
        label = f"{i} / {len(pages)}"
        d.text((PAGE_W - MARGIN - d.textlength(label, font=F(24)), PAGE_H - 60), label, font=F(24), fill=MUTED)
    pages[0].save(OUT, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    print(f"{OUT} ({len(pages)} páginas)")


if __name__ == "__main__":
    main()

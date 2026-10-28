"""Genera guia-circuito-proteus.pdf: explica cada parte del esquemático con recortes señalados.

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
OUT = BASE / "guia-circuito-proteus.pdf"
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


def main():
    h1, h2 = render_sheets()
    pages = []

    pages.append(text_page(
        "Guía del circuito HydroMate en Proteus",
        "Qué simula cada parte del esquemático y a qué componente físico representa",
        [
            ("Propósito", "Esta guía recorre las dos hojas del esquemático (proteus/hydromate.pdsprj, exportado en "
             "hydromate-esquematico.pdf). Cada página muestra un recorte del dibujo con recuadros numerados y explica "
             "qué hace esa parte, a qué componente real representa y por qué se modeló así."),
            ("Por qué hay equivalentes", "Proteus 8.13 no trae modelos simulables del ESP32, del ADS1115, del BH1750, "
             "del XL4015 ni de las sondas químicas de pH y TDS. Donde no hay modelo confiable se usa un componente o "
             "señal equivalente que cumple la misma función eléctrica, y se señala sobre el dibujo y en esta guía."),
            ("Cómo leer los instrumentos", "En el PDF del esquemático los voltímetros y amperímetros muestran +88.8: "
             "es su marcador cuando la simulación no corre, no una medición. Los valores medidos están en las capturas "
             "de evidencias/ y en el README (secciones de resultados)."),
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

    pages[0].save(OUT, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    print(f"{OUT} ({len(pages)} páginas)")


if __name__ == "__main__":
    main()

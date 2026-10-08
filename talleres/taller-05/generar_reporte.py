"""Generate provisional local technical PDF from recorded evidence, never synthetic -> real."""
from pathlib import Path
import json
import statistics
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONT = Path('C:/Windows/Fonts/arial.ttf')
if FONT.exists():
    pdfmetrics.registerFont(TTFont('HydroFont', str(FONT)))
    pdfmetrics.registerFont(TTFont('HydroBold', 'C:/Windows/Fonts/arialbd.ttf'))
    normal, bold = 'HydroFont', 'HydroBold'
else:
    normal, bold = 'Helvetica', 'Helvetica-Bold'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='HydroBody',fontName=normal,fontSize=10,leading=14,spaceAfter=8,textColor=colors.HexColor('#203930')))
styles.add(ParagraphStyle(name='HydroTitle',fontName=bold,fontSize=26,leading=30,spaceAfter=16,textColor=colors.HexColor('#146449')))
styles.add(ParagraphStyle(name='HydroHead',fontName=bold,fontSize=15,leading=20,spaceAfter=12,textColor=colors.HexColor('#146449')))
styles.add(ParagraphStyle(name='HydroCell',fontName=normal,fontSize=8.5,leading=11))
story=[]
def p(s, style='HydroBody'):
    story.append(Paragraph(escape(s),styles[style]))
def table(rows,widths):
    t=Table([[Paragraph(escape(str(c)),styles['HydroCell']) for c in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3F1E9')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#B6D3C4')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,12))
def footer(canvas,doc):
    canvas.setFont(normal,8);canvas.setFillColor(colors.HexColor('#537064'))
    canvas.drawString(44,26,'HydroMate | Taller 5 | Avance local provisional | 07/10/2026')
    canvas.drawRightString(A4[0]-44,26,str(doc.page))

data=json.loads((HERE/'pruebas/mqtt-local-autenticado-2026-10-07.json').read_text())
times=[e['mqtt_to_persistence_ack_ms'] for e in data['events'][:10]]
hardware=HERE/'pruebas/esp32-fisico-24ghz-2026-10-07.json'
hw=json.loads(hardware.read_text()) if hardware.exists() else None
hw_passed=bool(hw and hw['passed'])
latency_path=HERE/'pruebas/latencia-android-reintento-2026-10-07.json'
latency=json.loads(latency_path.read_text()) if latency_path.exists() else None

p('HydroMate','HydroTitle')
p('Taller 5 - Reporte técnico de avance local','HydroHead')
p('PROVISIONAL. La prueba local no sustituye el backend desplegado en nube requerido para aprobar viabilidad. Entrega original pendiente desde 16 de septiembre; fecha final del proyecto sin confirmar.')
p('Alcance: temperatura, pH, iluminación BH1750 en lux y flotador físicos; TDS simulado explícito por falla del sensor previo. Firmware sin control de bombas.')
table([['Capa','Función','Estado'],['ESP32','Lectura, procesamiento, JSON, Wi-Fi/MQTT, pendiente NVS','Ensayo serial/API aprobado' if hw_passed else 'Compilado y cargado; muestra serial válida, sin entrega confirmada'],['Mosquitto','Distribuir telemetría y confirmaciones','Banco autenticado 1884 probado; TLS nube pendiente'],['Integrador Python','Bandeja persistente y POST a Laravel','Diez mensajes PC y errores comprobados'],['Laravel + PostgreSQL','Validar, almacenar y consultar','v2 compatible, migración aditiva; 19 tests/118 assertions'],['Android Kotlin','Última recepción e historial por API','Compilado/instalado; aceptación visual actual según STATUS']], [82,194,231])
p('El recorrido sintético comprobado es PC -> Mosquitto -> integrador -> Laravel -> PostgreSQL. Android no accede a PostgreSQL. La SQLite del integrador es únicamente la bandeja de entrega.')
p('Versiones observadas: PHP 8.4.26, Laravel 13.33.0, PostgreSQL 16, Paho 2.1.0; core ESP32 3.3.11. Las versiones de bibliotecas y comandos se conservan en embedded/README.md y procedimiento-local.md.')
story.append(PageBreak())
p('Pruebas y resultados','HydroHead')
table([['Prueba','Resultado observado'],['Diez publicaciones MQTT sintéticas',f"passed={data['passed']}; diez filas de {data['device_id']} consultadas por API"],['Repetición idéntica','stored sin insertar fila duplicada'],['Misma identidad con contenido distinto','conflict; no sobrescribe la primera medición'],['pH incorrecto (50)','HTTP 422; ACK rejected; permanece el total de diez filas'],['Regresión v1','Smoke HTTP pasó 201/409/422/404 y concurrencia; filas sintéticas separadas'],['Backend aislado','PHPUnit: 19 pruebas, 118 assertions; SQLite en memoria, sin reset PostgreSQL'],['Android','assembleDebug, testDebugUnitTest y lintDebug; APK instalada por USB']], [166,341])
p(f"Latencia MQTT desde PC hasta ACK posterior a persistencia: promedio {statistics.mean(times):.2f} ms; mínimo {min(times):.2f} ms; máximo {max(times):.2f} ms. No incluye adquisición física ni actualización visible en Android.")
p('La etiqueta synthetic_test/test-* y sources=simulated identifica todos los datos del ensayo PC. El ejemplo de un JSON de contrato no acredita una medición física.')
if hw_passed:
    result=hw['events'][-1]
    p('Ensayo físico adicional: muestras serie y ACK comparados con API para secuencias '+', '.join(map(str,result['verified_sequences']))+'. TDS continúa simulado. Esto no mide calibración ni tiempo sensor-pantalla.')
    p('Entradas físicas: iluminación 1.67-185 lux y ambos estados del flotador tras intervención del usuario. Inicio Android observado y capturado mostrando cuatro variables físicas y TDS simulado.')
    if latency and latency['passed']:
        p(f"Una muestra: {latency['acquisition_complete_to_ui_verified_ms']/1000:.2f} s desde fin de adquisición serial hasta verificar su fecha en la interfaz Android. Incluye abrir la app y la inspección ADB; aproximación de banco, no latencia automática ni de nube.")
else:
    p('Primera prueba física: 421 s, una muestra serial válida tras corregir conexión/alimentación pH, cero ACK y cero filas por API. SSID original exclusivo de 5 GHz; usuario cambió a 2.4 GHz, pendiente repetición. Faltan diez muestras verificadas en API/app.')
p('Evidencias fuente: pruebas/mqtt-local-autenticado-2026-10-07.json, http-v1-regresion-2026-10-07.json y bitácora de errores. Los timestamps JSON usan UTC y pueden indicar 8 de octubre aunque la fecha local sea 7.')
story.append(PageBreak())
p('Código, datos y estructura','HydroHead')
table([['Ruta','Responsabilidad'],['embedded/HydroMateTelemetry/','Firmware derivado del sketch probado; configuración privada en secrets.h'],['scripts/mqtt_bridge.py','Suscribe telemetría; conserva objeto/secuencia; ACK solo después de INSERT'],['hydromate-backend/app/Http/Requests/','Validación v1/v2 antes de persistir'],['hydromate-backend/app/Models/Measurement.php','Campos asignables y conversión de números, JSON y booleano'],['hydromate-backend/database/migrations/','Esquema inicial y ampliación aditiva v2'],['mobile/','Cliente Kotlin, origen simulado, lux/flotador; sin mezclar unidades en gráfica'],['talleres/taller-05/','Procedimiento, plan, evidencias, bitácora y diagramas editables']], [240,267])
p('Tabla measurements: id, device_id, sequence, variables, sources y created_at/updated_at. Pareja device_id/sequence única. v2 agrega light_lux, water_present y message_version; campos relativos v1 quedan null para filas v2. El backend asigna hora de recepción UTC.')
p('API: POST /api/measurements registra; GET /api/measurements?device_id=hydromate-01&limit=20 consulta; GET /api/measurements/latest?device_id=hydromate-01 recupera última recepción. Inválido 422, duplicado 409, registro válido 201.')
p('Conexiones de señal documentadas: DS18B20 GPIO4; flotador GPIO27 (LOW=agua); I2C SDA21/SCL22 para BH1750 y ADS1115 0x48; pH PO a ADS A0. Calibración pH conservada: -5.579 x V + 14.066. No se realizó una nueva calibración.')
p('Firmware toma muestra de banco cada 30 s sin pendiente; reintenta idéntico objeto cada 5 s. Reserva bloques de 100 secuencias y guarda un pendiente en NVS. Huecos permitidos. Si se borra NVS o cambia identidad, reconciliar antes de reutilizar la torre.')
story.append(PageBreak())
p('Errores, prevención y cierre pendiente','HydroHead')
table([['Hallazgo','Acción y límite'],['Primer ensayo MQTT sin ACK','Conservado como fallo; posible carrera de suscripción. Reintento del mismo objeto pasa'],['Firewall 0x80070057','Ruta / corregida a ruta Windows; ejecución administrativa y regla verificadas'],['Input tap Android rechazado','MIUI exige permiso; se mantiene navegación manual, sin cambiar seguridad'],['Docker / PostgreSQL timeout posterior','Error interno de Docker; recuperación normal sin borrar datos. Estado final en STATUS']], [170,337])
table([['Riesgo','Prevención / contingencia'],['TDS defectuoso','Simulación señalada; reemplazo/calibración antes de usarlo para control'],['Red y conexión','Broker/ACL y regla privada limitada; conservar pendiente al fallar'],['Secuencias repetidas','NVS + índice único; conflicto detiene entrega para revisión'],['VPS compartido','Separar DB/usuarios/tópicos; backups independientes'],['Credenciales públicas','Excluir .env/secrets/.local y revisar diff; rotar si hay filtración'],['Sensor inválido / lectura tardía','Bloquear muestra inválida; recepción no equivale a adquisición reciente']], [170,337])
p('Orden restante: completar prueba física y Android -> documentar tiempo sensor-pantalla y fallos -> contratar/provisionar VPS -> HTTPS/MQTT TLS/protección de API -> repetir diez muestras en nube -> video y reporte final -> revisión docente.')
p('Presupuesto preliminar: hardware disponible; TDS por cotizar; VPS referencia recordada de ~90 MXN sin confirmar periodo/impuestos/renovación; reparto sujeto a acuerdo. Costos históricos y compras deben conciliarse antes de totalizar. Plan de sesiones y diez riesgos completos: plan-accion.md.')
p('Control remoto: requisito físico seguro o aplazamiento autorizado por docente si sigue siendo central. Sin orden simulada como sustitución. No hay evidencia de contratación, nube, video final ni aprobación docente en este avance.')
if hw_passed:
    story.append(PageBreak())
    p('Frontend con datos del ESP32','HydroHead')
    p('Capturas de la app funcional consultando Laravel local por USB. Inicio muestra la última recepción; Historial grafica registros almacenados. TDS conserva su etiqueta de simulado. No son maquetas ni datos escritos manualmente en la app.')
    pictures=[Image(str(HERE/'pruebas'/name),width=190,height=190*2400/1080) for name in ['android-sensores-reales-2026-10-07.png','android-historial-real-2026-10-07.png']]
    story.append(Table([pictures],colWidths=[253.5,253.5]))
    story.append(Spacer(1,12))
    p('Prueba de corte local: broker 1884 detenido brevemente; fallos MQTT observados, pendiente 901 conservado y confirmado después de recuperar servicio. 901/902 verificados contra API. Fuente: pruebas/esp32-reconexion-2026-10-07.json.')

output=HERE/'reporte-tecnico-local.pdf'
SimpleDocTemplate(str(output),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=44,title='HydroMate - Taller 5 - Avance local provisional',author='HydroMate').build(story,onFirstPage=footer,onLaterPages=footer)
print(output)

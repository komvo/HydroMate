"""HydroMate architecture deliverables. Run with the Codex bundled Python runtime."""
from pathlib import Path
import json, textwrap, html, math, re
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent.parent
DIAG=HERE/'diagramas'; DIAG.mkdir(parents=True,exist_ok=True)
FONT='C:/Windows/Fonts/arial.ttf'; BOLD='C:/Windows/Fonts/arialbd.ttf'
COL={'hw':'#DCEAF7','sw':'#E1F0E6','net':'#FCE9D0','db':'#EDE2F5','safe':'#F9DEDE','ext':'#EEEEEE'}
figures=[]
class Diagram:
    def __init__(self,num,title,w=1500,h=820):
        self.num,self.title,self.w,self.h=num,title,w,h
        self.im=Image.new('RGB',(w,h),'white'); self.draw=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<rect width="100%" height="100%" fill="white"/>']
        self.nodes={}; self.spec={'figure':num,'title':title,'nodes':{},'edges':[]}
        self.text(35,25,f'Figura {num}  {title}',28,True)
    def text(self,x,y,s,size=20,bold=False,anchor='left'):
        s=re.sub(r'([a-záéíóúñ])(?=\d)',r'\1 ',s)
        s=s.replace('I2C/1-Wire','I2C / 1-Wire').replace('PO5 V','PO 5 V').replace('VDD3.3','VDD 3.3').replace('VCC3.3','VCC 3.3')
        f=ImageFont.truetype(BOLD if bold else FONT,size)
        self.draw.text((x,y),s,font=f,fill='#17212B',anchor='mt' if anchor=='middle' else None)
        self.svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{"middle" if anchor=="middle" else "start"}" fill="#17212B">{html.escape(s)}</text>')
    def box(self,id,x,y,w,h,title,body='',kind='hw'):
        self.draw.rounded_rectangle((x,y,x+w,y+h),radius=8,fill=COL[kind],outline='#526371',width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{COL[kind]}" stroke="#526371" stroke-width="2"/>')
        lines=title.split('\n')+body.split('\n') if body else title.split('\n')
        for i,s in enumerate(lines): self.text(x+12,y+12+i*26,s,20,i==0)
        assert 12+len(lines)*26<h+10,(id,lines,h)
        self.nodes[id]=(x,y,w,h);self.spec['nodes'][id]={'rect':[x,y,w,h],'title':title,'body':body,'kind':kind}
    def port(self,id,side='right',offset=.5):
        x,y,w,h=self.nodes[id]
        return {'right':(x+w,y+h*offset),'left':(x,y+h*offset),'top':(x+w*offset,y),'bottom':(x+w*offset,y+h)}[side]
    def line(self,pts,label='',dash=False,color='#435B6E',arrow=True,labelxy=None,startarrow=False):
        pts=[(int(x),int(y)) for x,y in pts]
        for a,b in zip(pts,pts[1:]):
            assert a[0]==b[0] or a[1]==b[1],(a,b)
            if dash:
                dist=abs(b[0]-a[0])+abs(b[1]-a[1]); n=max(1,int(dist/10))
                for j in range(0,n,2):
                    p=tuple(a[k]+(b[k]-a[k])*j/n for k in (0,1));q=tuple(a[k]+(b[k]-a[k])*min(j+1,n)/n for k in (0,1));self.draw.line([p,q],fill=color,width=3)
            else:self.draw.line([a,b],fill=color,width=3)
        self.svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="10 10"' if dash else '')+'/>')
        if arrow:
            a,b=pts[-2:]; dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
            if length:
                ux,uy=dx/length,dy/length
                tri=[b,(b[0]-12*ux+5*uy,b[1]-12*uy-5*ux),(b[0]-12*ux-5*uy,b[1]-12*uy+5*ux)]
                self.draw.polygon(tri,fill=color);self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in tri)}" fill="{color}"/>')
        if startarrow:
            b,a=pts[:2];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
            if length:
                ux,uy=dx/length,dy/length
                tri=[b,(b[0]-12*ux+5*uy,b[1]-12*uy-5*ux),(b[0]-12*ux-5*uy,b[1]-12*uy+5*ux)]
                self.draw.polygon(tri,fill=color);self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in tri)}" fill="{color}"/>')
        if label:
            x,y=labelxy or (pts[0][0]+8,pts[0][1]-28)
            f=ImageFont.truetype(FONT,18); bb=self.draw.textbbox((x,y),label,font=f)
            self.draw.rectangle((bb[0]-3,bb[1]-3,bb[2]+3,bb[3]+3),fill='white')
            self.svg.append(f'<rect x="{bb[0]-3}" y="{bb[1]-3}" width="{bb[2]-bb[0]+6}" height="{bb[3]-bb[1]+6}" fill="white"/>')
            self.text(x,y,label,18)
    def edge(self,a,b,label='',sa='right',sb='left',offset=.5,via=None,dash=False,labelxy=None,bi=False):
        p=self.port(a,sa,offset);q=self.port(b,sb,offset)
        pts=[p]+(via or ([] if p[0]==q[0] or p[1]==q[1] else [((p[0]+q[0])/2,p[1]),((p[0]+q[0])/2,q[1])]))+[q]
        if label and labelxy is None:
            tw=self.draw.textlength(label,font=ImageFont.truetype(FONT,18))
            if sa in ['right','left'] and sb in ['right','left']:
                labelxy=((p[0]+q[0])/2-tw/2,min(self.nodes[a][1],self.nodes[b][1])-31)
            else:labelxy=(p[0]+12,(p[1]+q[1])/2-12)
        self.line(pts,label,dash,labelxy=labelxy,startarrow=bi)
        self.spec['edges'].append({'from':a,'to':b,'label':label,'points':pts,'proposed':dash})
    def save(self,note='Continua: interfaz definida. Discontinua: propuesta pendiente. Colores identifican dominios.'):
        self.text(35,self.h-65,note,18)
        self.text(35,self.h-38,'Azul hardware | Verde software | Naranja red | Morado datos | Rojo seguridad | Gris externo',18)
        stem=f'{self.num:02d}';self.im.save(DIAG/(stem+'.png'));(DIAG/(stem+'.svg')).write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8');(DIAG/(stem+'.json')).write_text(json.dumps(self.spec,ensure_ascii=False,indent=2),encoding='utf-8')
        figures.append((self.num,self.title,DIAG/(stem+'.png')))

def diagrams():
    d=Diagram(1,'Arquitectura integral por responsabilidades',1600,940)
    for i,t in enumerate(['A Entorno físico','B Control embebido','C Comunicación','D Servidor y datos','E Usuario']):d.text(35+i*315,80,t,21,True)
    d.box('sens',35,150,260,140,'Sensores','T°, pH, lux, nivel\nTDS pendiente\nEnergía opcional')
    d.box('esp',350,150,270,220,'ESP32 DevKit V1','Adquisición y HAL\nControl y seguridad\nComunicación + NVS\nControl local independiente\nde Internet')
    d.box('wifi',665,150,245,105,'Wi-Fi 2.4 GHz','Router / punto de acceso\nEnlace IP local',kind='net')
    d.box('internet',665,305,245,65,'Internet',kind='net')
    d.box('broker',665,420,245,130,'Mosquitto','Telemetría / ACK\nComandos: propuesta',kind='net')
    d.box('bridge',965,420,260,130,'Consumidor Python','Paho + bandeja SQLite\nPOST a Laravel',kind='sw')
    d.box('api',965,650,260,140,'Laravel API','Valida y persiste\nAuth / perfiles / alertas\nObjetivo pendiente',kind='sw')
    d.box('db',965,150,260,140,'PostgreSQL','measurements vigente\nDominio futuro: fig. 11',kind='db')
    d.box('android',1280,650,270,140,'Android nativo','HTTPS/REST\nCinco destinos\nUsuario consulta',kind='sw')
    d.box('drivers',350,650,270,140,'Drivers de potencia','Bomba / luz\nA / B / Up / Down\nInterfaz lógica segura',kind='hw')
    d.box('plant',35,650,260,140,'Torre y depósito','Bomba / retorno\nCuatro canales químicos\nLuz complementaria',kind='hw')
    d.box('future',1280,150,270,180,'Extensiones objetivo','FCM: Laravel → Android\nBLE: Android ↔ ESP32\nSolo aprovisionamiento\nVer figuras 2 y 12',kind='ext')
    d.edge('sens','esp','Señales');d.edge('esp','wifi','Datos / comandos',bi=True);d.edge('wifi','internet','IP',sa='bottom',sb='top',bi=True)
    d.edge('internet','broker','MQTT / TLS',sa='bottom',sb='top',bi=True,labelxy=(650,382))
    d.edge('broker','bridge','JSON / ACK',bi=True,labelxy=(915,390));d.edge('bridge','api','HTTP interno',sa='bottom',sb='top')
    d.edge('api','db','SQL',sa='right',sb='bottom',offset=.2,via=[(1248,678),(1248,350),(1017,350)],labelxy=(1260,430))
    d.edge('api','android','HTTPS 9443',bi=True,labelxy=(1285,610));d.edge('esp','drivers','Control seguro',sa='bottom',sb='top',dash=True)
    d.edge('drivers','plant','Actuación',sa='left',sb='right',dash=True)
    d.edge('api','broker','Comandos futuros',sa='left',sb='bottom',via=[(925,720),(925,600),(787,600)],dash=True,labelxy=(650,574))
    d.text(35,420,'ACK de persistencia',20,True);d.text(35,455,'Bridge → broker → ESP32',19);d.text(35,490,'Misma ruta de red; no es',19);d.text(35,520,'un comando de actuación.',19)
    d.save()
    d=Diagram(2,'Despliegue actual y alternativa remota',1500,860)
    d.box('tower',35,140,300,180,'Nodo torre','ESP32 + firmware + NVS\nSensores y drivers futuros\nActuadores futuros')
    d.box('router',405,140,290,180,'Nodo red doméstica','AP Wi-Fi 2.4 GHz\nSalida Internet\nNo acceso directo GPIO',kind='net')
    d.box('pc',790,140,660,180,'Desarrollo actual en PC','Laravel HTTP 8000; Mosquitto LAN 1884\nPostgreSQL existente; bridge Python / SQLite\nAndroid por USB adb reverse; excepción de banco',kind='sw')
    d.box('vps',790,460,660,220,'Despliegue objetivo alternativo','VPS compartido / cuenta deploy-hydromate / Docker rootless\nHTTPS9443 → Nginx → API8080; loopback host8081\nMQTT TLS8884 → Mosquitto; interno1884 → bridge\nPostgreSQL5432 interno; volúmenes exclusivos hydromate\nNo operar sobre chitiito ni puertos80/443/8443/8883',kind='net')
    d.box('phone',35,460,300,180,'Nodo Android','App nativa + HTTPS\nPreferencias limitadas\nBLE futuro',kind='sw')
    d.box('fcm',405,460,290,180,'Firebase externo','FCM futuro\nSin despliegue confirmado',kind='ext')
    d.edge('tower','router','Wi-Fi');d.edge('router','pc','Banco LAN');d.edge('router','vps','Internet / TLS',sa='bottom',sb='left',via=[(550,370),(740,370),(740,570)],dash=True,labelxy=(550,340))
    d.edge('phone','vps','HTTPS9443',sa='bottom',sb='bottom',via=[(185,730),(1120,730)],dash=True,labelxy=(480,702))
    d.edge('vps','fcm','HTTPS saliente',sa='left',sb='right',dash=True)
    d.edge('tower','phone','BLE alta inicial',sa='bottom',sb='top',dash=True,labelxy=(200,360),bi=True)
    d.edge('fcm','phone','FCM push',sa='left',sb='right',dash=True)
    d.save('PC y VPS son ambientes alternativos de la misma arquitectura; no requieren operación simultánea.')
    d=Diagram(3,'Señales electrónicas y buses compartidos',1500,960)
    d.box('ph',35,145,260,130,'S01 pH','Sonda → PH-4502C\nPO / acondicionamiento')
    d.box('tds',35,360,260,130,'S02 TDS','Kit reemplazo pendiente\nHigh-side S09 futuro')
    d.box('ads',380,245,290,150,'S03 ADS1115 0x48','A0 pH / A1 TDS\nVDD3.3 V; límites fig. 4\nA2/A3 sin asignación')
    d.box('bh',380,495,290,105,'S04 BH1750','VCC3.3 V; lux')
    d.box('energy',380,705,290,105,'S05 INA opcional','Rama y shunt pendientes')
    d.box('esp',835,145,300,160,'ESP32','GPIO21 SDA / GPIO22 SCL\nGPIO4 DS18B20\nGPIO27 flotador')
    d.box('temp',1185,145,275,105,'S06 DS18B20','3.3 V / pull-up4.7 kΩ')
    d.box('level',1185,360,275,130,'S07 Flotador','GPIO27 INPUT_PULLUP\nLOW agua / HIGH bajo')
    d.box('out',835,655,625,155,'A01–A07 Salidas propuestas','GPIO25 bomba / 26 iluminación / 13 A / 14 B\nGPIO18 Up / 19 Down / 23 alarma / 32 TDS enable\nSiempre hacia drivers; potencia separada en figura 4')
    d.edge('ph','ads','PO → A0',sb='left',via=[(335,210),(335,320)],labelxy=(100,293))
    d.edge('tds','ads','A → A1',sb='bottom',via=[(335,425),(525,425)],dash=True,labelxy=(95,517))
    # Parallel bus trunks, taps to device right ports and ESP bottom ports; no fictitious star cables.
    for x,lab,ep in [(725,'SDA',.80),(775,'SCL',.90)]:
        ytop=145+160*ep
        d.line([(x,835),(x,ytop),(835,ytop)],arrow=False)
        d.text(x-18,845,lab,18)
        for id in ['ads','bh','energy']:
            y=d.port(id,'right',.35 if x==725 else .75)[1]
            start=d.port(id,'right',.35 if x==725 else .75)
            if x==775:
                d.line([start,(717,y)],arrow=False);d.line([(733,y),(x,y)],arrow=False)
                d.draw.arc((717,y-8,733,y+8),180,360,fill='#435B6E',width=3)
                d.svg.append(f'<path d="M717,{y} A8,8 0 0 1 733,{y}" stroke="#435B6E" stroke-width="3" fill="none"/>')
            else:d.line([start,(x,y)],arrow=False)
            d.draw.ellipse((x-4,y-4,x+4,y+4),fill='#435B6E');d.svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#435B6E"/>')
    d.edge('temp','esp','1-Wire',sa='left',sb='right',offset=.25)
    d.edge('level','esp','Contacto',sa='top',sb='right',via=[(1322,330),(1160,330),(1160,225)],offset=.5,labelxy=(1200,310))
    d.edge('esp','out','HAL de salida',sa='bottom',sb='top',offset=.9,via=[(1105,580),(1397,580)],dash=True,labelxy=(1140,550))
    d.save('SDA/SCL con pull-ups a3.3 V. Retorno común y potencia fig. 4. INA y TDS no integrados.')
    d=Diagram(4,'Alimentación y mecanismos de actuación preliminares',1500,950)
    d.box('src',35,130,310,130,'P01 Fuente24 V / 5 A','Entrada protegida\n120 W nominales')
    d.box('dist',420,130,300,130,'P02 Distribución24 V','Fusibles por rama\nRetorno en estrella')
    d.box('pump',850,130,590,130,'A01 Recirculación','24 V → fusible → D4184 → bomba brushless25 W\nGPIO25 → entrada lógica; estado OFF sin control')
    d.box('buck',420,380,300,155,'P03 XL4015 a5 V','Rama lógica independiente\nESP32 por entrada5 V\nPH-4502C5 V')
    d.box('logic',35,380,310,155,'P04 Lógica3.3 V','Regulador placa: verificar\nDS18B20, BH1750, ADS\nPull-ups I2C/1-Wire')
    d.box('dose',850,380,590,155,'A03–A06 Cuatro canales','A / B / Up / Down: driver y rail según mecanismo\nServo/pinch: rail propio, cierre sin energía por probar\nBomba alternativa: driver DC y protección inductiva')
    d.box('light',850,665,590,155,'A02 Luz y A07 alarma','Lámpara: tensión/adaptador aún no confirmados\nDriver/relé según carga; GPIO26 señal, no energía\nAlarma opcional: GPIO23 → driver si exige corriente')
    d.box('analog',35,665,685,155,'P05 Protección analógica y S09 TDS','pH PO5 V potencial → divisor/buffer/protección → ADS A0\nTDS A → ADS A1; switch high-side en V+; no cortar GND\nRails12 V o servo solo si la carga definitiva los requiere')
    d.edge('src','dist','Potencia24 V');d.edge('dist','pump','Rama24 V')
    d.edge('dist','buck','24 V → buck',sa='bottom',sb='top')
    d.edge('buck','logic','5 V → regulador',sa='left',sb='right')
    d.edge('dist','dose','Rail condicionado',sa='right',sb='top',via=[(780,195),(780,340),(1145,340)],dash=True,labelxy=(780,300))
    d.text(35,290,'GND común DC en estrella.',20)
    d.text(35,320,'Retorno analógico separado.',20)
    d.text(35,575,'PE / tierra de protección: chasis/fuente según clase. No confundir con señal GND.',20)
    d.save('Potencia: flechas de esta figura. Señales GPIO: figura 3 y tabla E/S. No es esquema de PCB.')
    d=Diagram(5,'Firmware objetivo por capas',1500,900)
    d.box('safe',35,120,350,160,'SafetyManager','LevelMonitor + HealthMonitor\nVeto inmediato de actuación\nNo depende de red',kind='safe')
    d.box('ctl',475,120,440,160,'Controladores','Irrigation / Dosing / Lighting\nProfileManager / TimeManager\nSolicitudes → árbitro seguro')
    d.box('net',1000,120,450,160,'Comunicación y persistencia','CommunicationManager\nConfigurationStorage NVS\nEventLogger / cola acotada',kind='net')
    d.box('sensor',475,390,440,160,'SensorManager','Temperature / PH / TDS / Light\nLevelMonitor / PowerMonitor opc.\nLectura, calidad y caducidad')
    d.box('hal',475,665,440,120,'HAL','GPIO / I2C / 1-Wire / ADC\nActuatorDriver / TDS Power')
    d.box('physical',35,665,350,120,'Drivers físicos','S01–S07 y S09\nA01–A07; figuras 3 y 4')
    d.edge('ctl','safe','Solicitud de salida',sa='left',sb='right')
    d.edge('sensor','ctl','Snapshot validado',sa='top',sb='bottom')
    d.edge('hal','sensor','Valores / errores',sa='top',sb='bottom')
    d.edge('physical','hal','Interfaces');d.edge('net','ctl','Comando validado',sa='left',sb='right',dash=True)
    d.edge('safe','hal','Salida permitida / OFF',sa='bottom',sb='left',offset=.2,via=[(105,590),(420,590),(420,689)],labelxy=(35,554))
    d.text(1000,380,'Implementación actual',22,True);d.text(1000,420,'Sketch Arduino monolítico:',20);d.text(1000,450,'adquisición, MQTT y NVS.',20);d.text(1000,490,'Controladores y árbitro seguro',20);d.text(1000,520,'son diseño pendiente.',20)
    d.save('Dependencias representadas por interfaces; red no puede escribir directamente GPIO de actuadores.')
    d=Diagram(6,'Secuencia química prevista y rutas de error',1700,1100)
    names=['Scheduler','SensorMgr','TDS Power','PHService','TDSService','ADS1115','DS18B20','SafetyMgr','EventLogger']
    xs=[80+190*i for i in range(9)]
    for i,n in enumerate(names):
        d.box(str(i),xs[i]-65,95,145,65,n,kind='safe' if i==7 else 'hw')
        d.line([(xs[i],160),(xs[i],905)],dash=True,arrow=False,color='#A0ABB4')
    seq=[(0,1,'1 iniciar ciclo'),(1,2,'2 OFF real / V+'),(1,3,'3 tras t_PH estable'),(3,5,'4 N muestras A0'),(5,3,'5 voltajes / error'),(3,1,'6 pH + calidad'),(1,2,'7 ON / t_TDS'),(1,6,'8 conversión T°'),(6,4,'9 T° válida'),(4,5,'10 muestras A1'),(5,4,'11 V_TDS'),(4,1,'12 compensar / validar'),(1,2,'13 OFF en finally'),(1,7,'14 snapshot / inhibir'),(7,8,'15 registrar resultado')]
    for row,(a,b,l) in enumerate(seq):
        y=205+row*47;d.line([(xs[a],y),(xs[b],y)],l,labelxy=(min(xs[a],xs[b])+8,y-26))
    d.text(35,945,'ALT: ausente, inválido, fuera de rango, timeout o I2C → OFF TDS + null/calidad + inhibir dosificación.',20,True)
    d.save('Secuencia objetivo; t_PH, t_TDS, N y timeout deben medirse. No ejecutada con reemplazo TDS.')
    for num,title,states in [(7,'Máquina de estados de recirculación',['INITIALIZING','READY','IDLE','RUNNING']),(8,'Máquina de estados de dosificación',['DISABLED','READY','MEASURING','VALIDATING','DOSING','MIXING','WAITING','VERIFYING'])]:
        d=Diagram(num,title,1500,1040 if num==8 else 880)
        if num==7:
            positions=[(35,180),(405,180),(775,180),(1145,180)]
            for i,(x,y) in enumerate(positions):d.box(str(i),x,y,285,110,states[i],['OFF / autoprueba','Config válida','Esperar agenda','Bomba ON / timer'][i])
            for i,l in enumerate(['Validación','Habilitar','Agenda segura']):d.edge(str(i),str(i+1),l,labelxy=(310+370*i,155))
            d.box('manual',1145,460,285,125,'MANUAL_CONTROL','Mismo veto y timeout',kind='hw')
            d.box('fault',35,460,655,155,'LOW_WATER_LOCKOUT / SENSOR_FAULT','OFF obligatorio; nivel/sensor no válido\nRecuperar + estabilidad + reconocimiento → READY\nNo reactivar la orden anterior',kind='safe')
            d.box('stop',775,460,285,125,'SAFE_SHUTDOWN','OFF / fallo interno',kind='safe')
            d.edge('3','manual','Modo manual',sa='bottom',sb='top',dash=True)
            d.edge('0','fault','Cualquier estado: fallo',sa='bottom',sb='top',via=[(177,365),(362,365)],labelxy=(35,335))
            d.text(35,700,'RUNNING → IDLE: fin de duración o stop. MANUAL_CONTROL → IDLE: fin/stop/vencimiento.',20)
            d.text(35,735,'Cualquier estado → SAFE_SHUTDOWN: watchdog, configuración corrupta o apagado solicitado.',20)
        else:
            for i,s in enumerate(states):
                x=35+(i%4)*370;y=170+(i//4)*300;d.box(str(i),x,y,285,110,s)
            for a,b,l in [(0,1,'Habilitar'),(1,2,'Ciclo'),(2,3,'Lectura válida'),(4,5,'Cerrar / dosis fin'),(5,6,'Mezcla completa'),(6,7,'Asentamiento')]:d.edge(str(a),str(b),l,labelxy=(min(d.nodes[str(a)][0],d.nodes[str(b)][0])+290,d.nodes[str(a)][1]-28))
            d.edge('3','4','Corrección autorizada',sa='bottom',sb='left',via=[(1287,335),(15,335),(15,525)],labelxy=(560,307))
            d.box('lock',35,700,655,125,'LOCKOUT','Cerrar todos; nivel / límites / calibración / permiso',kind='safe')
            d.box('err',800,700,655,125,'FAULT','Cerrar todos; driver / sensor / timeout interno',kind='safe')
            d.text(35,630,'VERIFYING → READY si objetivo satisfecho; → MEASURING si otra corrección está permitida.',20)
            d.text(35,855,'Cualquier estado entra LOCKOUT o FAULT ante su causa; el cierre precede al registro.',20)
            d.text(35,900,'LOCKOUT/FAULT → DISABLED tras diagnóstico. Reinicio nunca retoma una dosis.',20)
        d.save('Eventos y guardas completos en sección 10. Estados de diseño; no firmware de actuadores ejecutado.')
    d=Diagram(9,'Backend vigente y módulos de dominio objetivo',1500,880)
    d.box('bridge',35,130,320,150,'MQTT Integration','Python/Paho vigente\nSQLite inbox persistente\nACK stored tras Laravel',kind='net')
    d.box('router',440,130,420,150,'API Router / Controller','MeasurementController\nstore / index / latest / status\nStoreMeasurementRequest',kind='sw')
    d.box('db',960,130,480,150,'Measurement Storage','Eloquent Measurement → PostgreSQL\nUNIQUE device_id + sequence\nCurrent State por antigüedad',kind='db')
    d.box('auth',35,460,320,190,'Authentication / Authorization','Sanctum objetivo\nAcceso por torre\nDevice Management\nDevice Credentials',kind='sw')
    d.box('domain',440,460,420,190,'Servicios de dominio objetivo','Irrigation / Dosing Events\nCrop Profiles / Configuration\nCommand Management\nAudit Logging',kind='sw')
    d.box('alerts',960,460,480,190,'Alerts / Notifications objetivo','Eventos → reglas → alerta persistida\nFCM con registro de entrega\nNo sustituye SafetyManager',kind='sw')
    d.edge('bridge','router','POST');d.edge('router','db','Validación → persistencia')
    d.edge('auth','domain','Policy de torre',dash=True);d.edge('domain','alerts','Evento',dash=True)
    d.text(35,345,'Android → Router GET. El consumidor no escribe PostgreSQL directamente ni calcula dosis físicas.',20)
    d.text(35,720,'Dominio futuro requiere rutas, migraciones y pruebas propias. No crear tablas anticipadamente.',20)
    d.save()
    d=Diagram(10,'Modelo de datos real y relación futura de identidad',1500,860)
    d.box('users',35,160,330,190,'users existente','id PK bigint / name / email\npassword hash / timestamps\nSin asociación de torre actual',kind='db')
    d.box('devices',525,160,350,190,'devices propuesta','device_id PK varchar64\nname / owner lógico / estado\nIdentidad estable, no secuencia',kind='db')
    d.box('measure',1035,160,420,300,'measurements vigente','id PK bigint; device_id varchar64\nsequence bigint\nUNIQUE(device_id,sequence)\nmessage_version / sources JSON\nT°, pH, ppm, lux, EC nullable\nwater_present boolean nullable\ncaptured_at timestamptz nullable\ncreated_at / updated_at recepción',kind='db')
    d.box('access',525,540,350,150,'user_device_access propuesta','user_id FK / device_id FK\nrole / UNIQUE(user_id,device_id)\nRelación usuarios N:M torres',kind='db')
    d.edge('devices','measure','1 : N futura FK',dash=True,labelxy=(885,125))
    d.edge('devices','access','1 : N',sa='bottom',sb='top',dash=True)
    d.edge('users','access','1 : N',sa='bottom',sb='left',via=[(200,460),(460,460),(460,615)],dash=True,labelxy=(250,432))
    d.text(35,740,'Hoy measurements.device_id es texto sin FK a devices. Reconciliar filas test-* antes de añadir FK.',20)
    d.save()
    d=Diagram(11,'Modelo relacional objetivo complementario',1500,1080)
    groups=[('devices','devices [P]','device_id PK'),('commands','commands [P]','command_id UUID PK\ndevice_id FK / expires_at / status'),('acks','command_acks [P]','id PK / command_id FK\nUNIQUE(command_id,ack_sequence)'),('profile','crop_profiles [P]','id PK / creator_user_id FK'),('versions','profile_versions [P]','id PK / profile_id FK\nUNIQUE(profile_id,version)'),('config','device_configuration [P]','device_id FK / revision\nprofile_version_id FK'),('events','device_events [P]','event_id UUID PK / device_id FK'),('alerts','alerts [P]','id PK / device_id FK\nevent_id FK nullable'),('dosing','dosing_events [P]','id PK / event_id FK UNIQUE\nchannel / volume / calibration_id'),('creds','device_credentials [P]','id PK / device_id FK\nsecret_ref / revoked_at')]
    pos=[(35,120),(520,120),(1035,120),(35,350),(520,350),(1035,350),(35,585),(520,585),(1035,585),(35,815)]
    for (id,t,b),(x,y) in zip(groups,pos):d.box(id,x,y,410,145,t,b,kind='db')
    for a,b,l in [('devices','commands','1 : N'),('commands','acks','1 : N'),('profile','versions','1 : N'),('versions','config','1 : N'),('events','alerts','1 : N'),('alerts','dosing','Referencias separadas')]:
        if a=='alerts':continue
        d.edge(a,b,l,dash=True,labelxy=(d.nodes[a][0]+415,d.nodes[a][1]-28))
    d.text(520,825,'FK adicionales mediante conectores de referencia',22,True)
    for i,t in enumerate(['devices1 → N config / events / alerts / credentials','events1 → 0..1 dosing_events; command1 → 0..N events','users1 → N profiles; users1 → N audit_log [P]','No migraciones nuevas aplicadas por este documento.']):d.text(520,870+i*28,t,20)
    d.save('Todas las cajas [P] son propuestas de diseño. Cardinalidades y campos detallados en sección 12.')
    d=Diagram(12,'Android nativo existente y extensiones',1500,920)
    d.box('ui',35,150,350,190,'UI nativa','Inicio / Historial\nCultivo / Control / Más\nAeroComponents y navegación\nCultivo/Control sin órdenes',kind='sw')
    d.box('present',475,150,440,190,'Presentación equivalente','MainActivity / ReadingState\nExecutor + RequestFence\nSin ViewModel obligatorio\nFuente real / demo debug',kind='sw')
    d.box('repo',1000,150,450,190,'Repository / API Client','TelemetryRepository\nHttpURLConnection / parse v3\nHTTPS / real_only producción\nGET por torre',kind='sw')
    d.box('settings',35,520,350,190,'Settings vigente','ConnectionStore / ambiente\nNombre, URL y preferencias\nSin caché de mediciones',kind='sw')
    d.box('future',475,520,440,190,'Extensiones propuestas','Authentication / SessionManager\nLocalCache acotada\nDeviceProvisioning BLE\nNotifications FCM',kind='ext')
    d.box('api',1000,520,450,190,'Laravel API','Mediciones e historial vigentes\nAuth / control futuros\nESP32 recibe vía MQTT',kind='sw')
    d.edge('ui','present','Acción / estado');d.edge('present','repo','Carga / snapshot');d.edge('repo','api','HTTPS9443',sa='bottom',sb='top')
    d.edge('settings','ui','Config local',sa='top',sb='bottom')
    d.text(35,795,'BLE propuesto: alta Wi-Fi con posesión física. FCM propuesto: aviso; consultar detalle por API.',20)
    d.save()


if __name__ == "__main__":
    diagrams()

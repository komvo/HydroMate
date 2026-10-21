# HydroMate Diseño de la Arquitectura Integral

Antecedente histórico. La entrega vigente y acotada está en
[Word T8](../../Documentos%20PDC/T8_PDC_1288703.docx) y
[PDF T8](../../Documentos%20PDC/T8_PDC_1288703.pdf),15 páginas.

Base documental 1.0 del 14/10/2026, 41 páginas. Autor: Valdez Meza Kevin Osmar, matrícula 1288703.

- HydroMate_Arquitectura_Integral.docx: documento editable con portada UABC y 25 apartados, incluidas portada/conclusión/referencias.
- HydroMate_Arquitectura_Integral.pdf: exportación desde Microsoft Word.
- diagramas/: 12 SVG vectoriales editables, 12 PNG de referencia y12 PNG de alta resolución (sufijo -alta, rasterizados desde SVG a 3×,300dpi).
- diagramas/*.json: nodos, coordenadas y rutas de las figuras.
- diagramas/generar_diagramas.py: fuente de generación con Python/Pillow y fuentes Arial de Windows. No requiere firmware, servicios, acceso de red ni credenciales.
- contenido.json: texto, tablas y 10 ejemplos JSON del taller. Los ejemplos son ilustrativos.
- qa.json: revisión documental, límites de evidencia y hashes de los archivos finales.

## Lectura e impresión

Texto general A4 vertical. Figuras y matrices amplias A3 horizontal para mantener etiquetas y columnas legibles. Conservar tamaño nativo al revisar/imprimir esas páginas; losSVG se pueden ampliar sin perder calidad.

## Límites del congelamiento

Ratifica ESP32/control local, MQTT/TLS/Mosquitto, consumidor Paho, Laravel/PostgreSQL y Android HTTPS. Conserva contrato v3 y tópicos reales. Los 14 ADR distinguen decisiones ratificadas de propuestas.

Mecanismo de dosificación, GPIO de actuación, cierres sin energía, límites, tiempos, TDS y montaje eléctrico siguen sujetos a validación. hm-control-1, tablas/rutas de dominio, autenticación de usuarios, BLE yFCM son arquitectura objetivo, no implementación nueva. No acredita despliegue completo ni recepción ESP32→VPS.

Los originales académicos se conservaron. No contiene secretos ni modifica código operativo o infraestructura. Evidencia física/local y actualizaciones de STATUS identificadas por fecha; no se ejecutaron nuevas pruebas de hardware para elaborar el taller.

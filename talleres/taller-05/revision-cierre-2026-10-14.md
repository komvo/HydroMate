# Revisión de cierre del Taller 5

Revisión posterior a la publicación de producción, 14/10/2026. El usuario indica
que cree haber desplegado HydroMate. No se encontró una URL pública ni evidencia
nueva del recorrido físico en nube en los archivos revisados. Por ello todavía
no puede acreditarse la entrega completa. No significa que la VPS no funcione:
su despliegue permanece sin verificar en esta revisión.

## Comprobaciones observadas

- Remoto `main` en dccfc99 incorpora el PR1 de codex/production-shared-vps;
  su árbol coincide con el commit de producción 67da210. Se consultó/fetchó
  el remoto en lectura; no se hizo merge, push ni acceso al VPS en esta revisión.
- ESP32 detectado en COM3 y teléfono detectado por ADB. Detectar USB no demuestra
  Wi-Fi, MQTT, lecturas actuales ni envío a nube; no se cargó firmware ni abrió
  puerto serie para reiniciar la placa.
- Lectura de preferencias propias de HydroMate, sin modificarlas:
  servidor **http://127.0.0.1:8000**, device_id **hydromate-01**. Esa configuración
  corresponde a la API de desarrollo por USB, no a una URL pública de VPS.
- Los archivos físicos disponibles son del 07/10: diez entregas locales
  (una recuperada y nueve nuevas), capturas Android, fallo/reconexión y una
  aproximación de 8.24 s que incluye arranque/inspección de interfaz.
- Los ensayos Docker de producción del 14/10 son **locales y sintéticos**.
  No acreditan sensores físicos ni despliegue en nube.

## Resultado por requisito

| Requisito del taller | Evidencia existente | Estado de cierre |
|---|---|---|
| Entrada física, procesamiento e identificación | Firmware embedded/HydroMateTelemetry; muestras serie/API del 07/10; secuencia y fecha recibida | Cumplido localmente, nueva ejecución en nube por comprobar |
| Internet del embebido y envío al backend desplegado | Wi-Fi/MQTT LAN probado; TLS Docker local sintético probado | Pendiente de recorrido ESP32→VPS real |
| Backend desplegado temporalmente | Código producción ya incorporado a main; despliegue comunicado tentativamente | Sin verificar: falta URL pública y respuesta observada |
| Backend recibe, valida, almacena y permite consulta; válido/incorrecto comprensibles | API 201/422/409/GET, tests y ensayos locales | Funciones probadas; comprobarlas en despliegue actual |
| Tabla, identificador, variable/valor, unidad y fecha | measurements, migraciones v1/v2, esquema y consulta SQL/API | Estructura disponible; verificar esquema aplicado en VPS |
| Diez registros reales en BD | Diez entregas físicas locales 101 y401–409, cuatro variables reales/TDS simulado | Falta verificar diez nuevas muestras almacenadas en nube; copiar filas antiguas no prueba transmisión al VPS |
| Pantalla funcional, último dato/fecha, lista/gráfica, carga/vacío/error | Android Inicio/Historial y estados implementados; evidencia local | Funciones disponibles; teléfono sigue en URL local, falta demostrar consulta a VPS |
| Control básico o aplazamiento docente | Aplazamiento comunicado por usuario; telemetría sin actuadores | Registrar autorización docente y justificación; ACK stored no es actuación física |
| Diez transmisiones consecutivas, éxitos y fallos | Captura física local con una recuperada + nueve nuevas | Repetir diez adquisiciones nuevas seguidas contra VPS con --fresh-only y conservar intentos/ACK |
| Tiempo aproximado sensor–frontend | 8.24 s local en una muestra, método/limitaciones descritos | Medir de nuevo con nube y actualización visible en Android |
| Dato incorrecto o pérdida temporal, problemas/correcciones | Ensayos inválidos y corte local; bitácora técnica | Repetir prueba propia contra recorrido desplegado y guardar resultado; no detener servicios ajenos |
| Código y Git con README | Fuentes y commit67da210, producción en remoto main | Disponible; documentos de planeación/revisión nuevos todavía locales |
| Diagrama conexión/flujo implementado | Tabla de conexiones y Mermaid de flujo local | Existe local; producir/actualizar flujo nube al confirmar su ejecución |
| Video breve de funcionamiento | android-consulta-local-2026-10-07.mp4, pantalla Android local | Parcial; falta video conjunto montaje→nube→Android |
| Evidencia backend desplegado, estructura BD y frontend real | Código/estructura/capturas locales | Completar evidencia del sistema desplegado; una pantalla Docker por sí sola no prueba el flujo |
| Cronograma semanas restantes | plan-accion.md hasta02/12/2026 | Disponible |
| Presupuesto preliminar | plan-accion.md, gasto histórico separado y VPS prestado$0 | Disponible preliminar; costos/cargos pendientes de conciliación identificados |
| Matriz de al menos cinco riesgos y acciones | plan-accion.md contiene diez riesgos, prevención y contingencia | Disponible |

El TDS simulado no invalida una prueba basada en temperatura/luz/flotador/pH
reales, siempre que se etiquete y se muestre como simulado. No exigir calibración
definitiva, todas las pantallas, perfiles o autenticación completa para cerrar
este taller; cumplir el recorrido mínimo y las evidencias solicitadas.

## Siguiente verificación

1. Obtener solo la URL pública de HydroMate, sin credenciales/tokens. Comprobar
   certificado, `/up` y GET filtrado; una respuesta401 exige verificación por el
   cliente autorizado, sin solicitar secretos al chat. HTTP200 en /up no demuestra
   por sí solo diez registros ni hardware.
2. Configurar Android hacia el endpoint HTTPS protegido y comprobar que ESP32
   usa el broker VPS con TLS. La configuración privada la mantiene el usuario;
   no acceder a SSH ni modificar recursos chitiito-*.
3. Capturar diez nuevas adquisiciones físicas y confirmar mismas secuencias y
   valores en API/BD y app. Conservar origen real/simulado y fecha de recepción.
4. Medir tiempo hasta interfaz visible y realizar una prueba inválida o de
   pérdida temporal controlada del enlace propio, restaurando la conexión.
5. Guardar video, diagrama realmente implementado, respuestas, esquema/consulta,
   fallos y autorización de aplazamiento; actualizar reporte del taller.

Este documento registra lo comprobado y lo pendiente. No certifica aprobación
docente ni declara que el taller esté concluido.

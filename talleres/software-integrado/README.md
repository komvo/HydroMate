# Versión inicial integrada del software

Entrega preparada el 28/10/2026. Compilaciones y pruebas locales ejecutadas el
27/10; integración física pública acreditada por evidencias del 21/10.

## Documento de entrega

- [Word editable](../../Documentos%20PDC/Software_integrado_PDC_1288703.docx).
- [PDF](../../Documentos%20PDC/T10_PDC_1288703.pdf).
- [Contenido consultable](entrega-2026-10-28/Informe_software_integrado.md).
- [Resultados locales y huellas de fuentes](entrega-2026-10-28/validacion-local.json).
- [Inventario de variables sin secretos](entrega-2026-10-28/variables-entorno.md).

`entrega-2026-10-28/diagramas/` contiene SVG editables y PNG de módulos, modelo
de datos implementado y bosquejo de pantallas. El pseudocódigo, diccionario y
plan de siete pruebas están en el informe; no se modifican los T5/T8 originales.

## Alcance y límites

Se verificaron compilación ESP32, PHPUnit en SQLite en memoria, pruebas Python,
Android JVM/lint/debug/release y aislamiento estático de Compose con fixtures.
Los logs completos y binarios compilados permanecen en `.local/`: no publicar
firmware con configuración privada ni usar datos sintéticos para acreditar el
flujo físico. Ningún comando de esta tarea accedió a la VPS o flasheó el ESP32.

Salida física (28/10): el firmware gobierna la bomba de recirculación. GPIO25 es
activo en bajo y pasa por una NOR 74HCT02 con el flotador; la alarma está en GPIO23. El
circuito está armado como en la práctica Proteus. La prueba P7 se realizó sin
fotografía, video ni registro serie, y la corriente de arranque no se midió. La dosificación
y el control remoto siguen abiertos. La evidencia real previa de la app conserva su fecha.
El 28/10 se comprobó el reinicio del ESP32, funcionamiento sin conexión
y llegada de las mediciones más recientes sin duplicarse al recuperarla.
Registro: [confirmación de pruebas](entrega-2026-10-28/confirmacion-pruebas-2026-10-28.json).
No se acredita reinicio del bridge ni almacenamiento de todas las transiciones.

No se creó commit, push, merge ni despliegue. Conservar los cambios de otras
tareas que ya existían en el checkout.

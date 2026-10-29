# Validación de la versión inicial integrada

Revisión documental: 28/10/2026. Paquete y fuentes en
[Documentos PDC/T10_anexos](../Documentos PDC/T10_anexos/README.md).

El documento cubre los mínimos generales, firmware, backend, base de datos,
frontend y calidad. Añade el modelo de telemetría implementado, diccionario de
las veinte columnas, responsabilidades, tres pseudocódigos, bosquejo de pantallas
y siete pruebas propuestas con procedimiento, resultado esperado y estado.

Compilaciones/pruebas observadas el 27/10:

- ESP32 Dev Module: compilación correcta, flash 1,076,345 bytes y RAM 50,812.
- PHPUnit: 29 pruebas, 194 comprobaciones; base SQLite `:memory:`.
- Python: 10 pruebas correctas, cero omisiones; guardas rootless con mocks/Git Bash.
- Android: 39 casos, 35 ejecutados y 4 opt-in omitidos; cero fallos, lint y builds
  debug/release correctos. No instalación ni nueva adquisición física.
- Compose: aislamiento validado con valores ficticios; no servicios iniciados.

No se repitió el ensayo físico ni se contactó la VPS. Las capturas del informe
están fechadas el 21/10 y no representan el diseño nuevo como una nueva prueba
remota. Consultar AERO_ACCEPTANCE para la revisión visual del 27/10.

Permanece pendiente la actuación central o una autorización docente aplicable
a esta etapa; no se habilitan salidas de riesgo para cerrar un requisito en papel.
El 28/10 se reinició el ESP32: continuó funcionando sin conexión y al
recuperarla llegaron las mediciones más recientes sin duplicarse. La reconexión
y el reinicio del ESP32 quedan comprobados; el reinicio del bridge no se probó.
La evidencia de la app conserva su fecha.
Registro en confirmacion-responsable.json del paquete de entrega.
La interacción manual restante se mantiene en AERO_ACCEPTANCE. No se introduce
código funcional ni cambia arquitectura, secretos o puertos.

# Repositorio HydroMate

## Alcance

Usuario solicita guardar documentos, pruebas y código de HydroMate en GitHub,
cuenta `komvo`. Tras propuesta inicial privada, el usuario autorizó expresamente
la visibilidad pública. Repositorio: https://github.com/komvo/HydroMate.
Git local está en `C:\Hydromate` y usa rama `main`.

Se incluyen los originales de `Documentos PDC/`, también versiones anteriores y
duplicados: conservar su procedencia es parte del respaldo solicitado. El sketch
`tsts/tsts.ino` permanece como referencia de las pruebas físicas.

## Archivos excluidos

`.gitignore` excluye secretos, `.local/`, herramientas descargadas, dependencias
reinstalables (`vendor/`, `node_modules/`), cachés, compilaciones Android, ajustes
locales, logs operativos, bases SQLite y exportaciones SQL/dump. Los resultados
seleccionados de pruebas deben conservarse en `docs/evidence/` sin credenciales.

Git no conserva los datos del volumen PostgreSQL ni sustituye su respaldo. APK y
videos grandes podrán distribuirse como entregables aparte cuando existan;
decidir Git LFS u otro almacenamiento antes de añadir archivos que excedan los
límites del proveedor. Nunca publicar secretos aunque el repositorio sea privado.

## Flujo de trabajo

1. Consultar el estado de Git y preservar cambios existentes.
2. Implementar un incremento concreto y verificarlo cuando sea posible.
3. Guardar evidencia nueva con fecha, sin sobrescribir resultados históricos.
4. Actualizar STATUS; DECISIONS/ARCHITECTURE/SETUP cuando corresponda.
5. Revisar archivos y diff antes de crear un commit.
6. Sincronizar con GitHub mediante push dentro del alcance autorizado.

La autorización para crear y subir la versión inicial no incluye secretos,
acceso de escritura para terceros ni cambios automáticos en infraestructura. Compartir
VPS tampoco implica compartir este repositorio con el compañero.

Los avances futuros no se suben solos: deben guardarse en commits y sincronizarse.

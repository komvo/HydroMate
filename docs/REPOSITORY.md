# Repositorio HydroMate

## Alcance

Usuario solicita guardar documentos, pruebas y código de HydroMate en GitHub,
cuenta `komvo`. Tras propuesta inicial privada, el usuario autorizó expresamente
la visibilidad pública. Repositorio: https://github.com/komvo/HydroMate.
Git local está en `C:\Hydromate` y usa rama `main`.

La versión inicial completa se publicó y verificó el 07/10/2026. Dos intentos
de transferencia completa agotaron el tiempo de espera HTTP; se subió en 18 lotes
y se conectó el historial de importación con los dos commits locales originales.
Ambos commits se conservan como ancestros de `main`; no hubo force push ni reset.

La inclusión inicial de todos los originales fue reemplazada el 07/10 por una
selección solicitada por el usuario: en `Documentos PDC/` se mantienen publicados
los archivos T1–T4/T6/T7 y `tests/PruebaSensores1.ino` (antes `tsts/tsts.ino`). Se retiraron de la versión actual las
carpetas de duplicados, versiones anteriores y HydroMate_Duena_Milca, así como los
18 documentos/archivos señalados en las capturas. Se conservan físicamente en la
computadora, excluidos mediante `.gitignore`; también permanecen en el historial
anterior. No se realizó borrado local ni reescritura del historial.

`talleres/` organiza copias de los PDF existentes y materiales técnicos del
Taller 5 según el requisito docente comunicado. Las copias conservan el hash de
sus originales. T6/T7 se conservan como históricos; su adecuación técnica sigue
pendiente. Código/evidencia se enlazan a sus fuentes para conservar trazabilidad.

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

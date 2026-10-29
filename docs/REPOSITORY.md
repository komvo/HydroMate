# Git y publicación de HydroMate

Repositorio público: https://github.com/komvo/HydroMate. Raíz local:
`C:\Hydromate`. Revisión: 27/10/2026. Trabajar siempre en una rama de incremento.

## Revisar y preservar

Desde la raíz:

```powershell
git status --short
git branch --show-current
git log -5 --oneline
git diff --stat
git remote -v
```

Revisar STATUS antes de cambiar algo. Preservar cambios existentes y archivos sin
seguimiento; no usar reset, clean ni stash para descartar trabajo. Commit/push,
merge y despliegue son pasos distintos.

## Rama e integración con main

`git fetch origin` consulta el remoto y actualiza referencias sin modificar el
checkout. Verificar previamente que origin corresponda al repositorio correcto.
Con árbol limpio, para un incremento nuevo basado en main:

```powershell
git switch -c nombre-del-incremento origin/main
```

El nombre es un ejemplo; elegir uno descriptivo disponible. Si hay trabajo en otra
rama, resolver primero dónde pertenece sin perderlo. Para actualizar una rama de
trabajo contra main, con árbol limpio y dentro del alcance pedido, preferir
`git merge origin/main`, que conserva el historial. No rebase de commits publicados
ni force push sin autorización explícita. Resolver conflictos por contenido,
conservando cambios ajenos, documentos, PDFs y evidencias; no aceptar una versión
completa a ciegas.

```powershell
git rev-list --left-right --count origin/main...HEAD
git diff --stat origin/main...HEAD
```

El primer número indica commits de main ausentes en la rama: cero acredita que no
está behind respecto de la referencia recién descargada. Revisar también el diff
completo; no asumir sincronización ni despliegue por un conteo.

## Validar, guardar y publicar

Elegir pruebas pertinentes en [SETUP](SETUP.md). Agregar rutas explícitas mediante
`git add <ruta>` después de revisarlas. No usar add de todo el árbol sin inspección.
Antes del commit:

```powershell
git diff --check
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Solo con autorización de commit/push del alcance actual:

```powershell
git commit -m "Describe el cambio concreto"
git push -u origin HEAD
git rev-parse HEAD
git status --short --branch
```

Verificar éxito y comunicar rama/hash. No crear ni fusionar un PR por inferencia.
Si se crea un PR por pedido, adjuntarlo al chat con la herramienta disponible.
En esta revisión no se identificó un workflow en `.github/`: no afirmar ejecución
automática de pruebas en GitHub sin evidencia.

## Publicación y despliegue

La VPS consume `main` mediante un ejecutor externo no inspeccionado aquí. Subir
una rama no demuestra despliegue. `deployment/deploy.sh` construye, levanta y migra
HydroMate; no hace pull ni merge de Git. El administrador sigue
[PUBLIC_ACCESS](PUBLIC_ACCESS.md). Los secretos solo existen en la VPS.

## Documentos y archivos privados

Orden de lectura: STATUS → PROJECT_CONTEXT → ARCHITECTURE.
Las entregas actuales son `Documentos PDC/T5_PDC_1288703.docx`/PDF y T8 equivalentes,
editadas a mano. No modificarlas ni regenerarlas por una tarea de código:
los generadores/reportes ampliados no garantizan reproducir su formato final.
Guardar evidencia nueva con fecha sin borrar ni renombrar históricos.

`.gitignore` excluye `.local/`, secretos, dependencias, compilaciones y ajustes
privados. `secrets.h`, `.env` y llaves nunca deben entrar en commits; ejemplos
versionados usan nombres y valores públicos/no sensibles. Una clonación nueva no
incluye herramientas privadas ni `.local/seguimiento/CONTINUIDAD.md`: no publicar
esa nota ni inventar su contenido. No volcar configuraciones con secretos para
verificarlas. Git no respalda volúmenes PostgreSQL ni sustituye sus backups.
Revisar tamaño/destino antes de agregar archivos grandes.

# Android HydroMate
Leer ../AGENTS.md y ../docs/STATUS.md antes de cambios.
Contrato: ../docs/TELEMETRY_CONTRACT.md y ../docs/API.md.
Kotlin, interfaz nativa mínima, solo consultas. No inventar datos ni agregar login,
actuadores o MQTT directo en la app. HTTP solo en variante debug para pruebas locales.
Build: gradlew.bat assembleDebug testDebugUnitTest lintDebug.
Diseño vigente: ../docs/AERO_DESIGN.md; aceptación: ../docs/AERO_ACCEPTANCE.md.
Fixtures solo en src/debug, opt-in y con marca fija; release no contiene datos demo.

# HydroMate

Prototipo de monitoreo y control local para hidroponía vertical. Este repositorio
conserva el código, los documentos académicos, las pruebas y las evidencias del
proyecto. Repositorio público: [komvo/HydroMate](https://github.com/komvo/HydroMate).

## Estado al 7 de octubre de 2026

- Backend Laravel y PostgreSQL comprobados localmente con datos sintéticos.
- Android nativo Kotlin compilado e instalado; integración real y QA manual
  parcialmente pendientes.
- ESP32 con DS18B20, BH1750, flotador, ADS1115 y pH probados según la bitácora
  del 5 de octubre. TDS defectuoso: reemplazo pendiente.
- Código de pruebas físicas conservado en `Documentos PDC/tsts/tsts.ino`.
  Todavía no contiene Wi-Fi ni publicación MQTT.
- Taller 5 pendiente: demostrar sensores físicos → ESP32 → backend en nube →
  PostgreSQL → Android, diez transmisiones y evidencia de fallos y tiempos.
- Alcance solicitado: temperatura, pH, luz y nivel reales; TDS simulado con
  identificación por variable. Aún requiere cambios de contrato, BD, firmware y app.
- VPS-1 de OVHcloud compartido con otro proyecto es la opción aceptada para
  preparar el despliegue; contratación y despliegue no comprobados.

El [estado actual](docs/STATUS.md) distingue pruebas realizadas y pendientes.
La [arquitectura](docs/ARCHITECTURE.md) y las [decisiones](docs/DECISIONS.md)
conservan el contexto técnico e histórico.

## Contenido

| Ruta | Contenido |
|---|---|
| `hydromate-backend/` | API Laravel, migraciones, pruebas y fixtures sintéticos |
| `mobile/` | Aplicación Android, pruebas y recursos gráficos |
| `Documentos PDC/` | Referencias académicas, bitácora física y sketch de sensores |
| `docs/` | Contexto, contratos, arquitectura, decisiones y guías |
| `docs/evidence/` | Evidencias y resultados registrados, con fechas |
| `scripts/` | Herramientas de revisión y captura |
| `reports/` | Informes elaborados sobre el proyecto |

`embedded/` e infraestructura de despliegue se incorporarán cuando se implementen.
Una carpeta prevista no representa una función terminada.

## Ejecutar y verificar

Seguir [SETUP](docs/SETUP.md) para los servicios locales existentes y
[mobile/README](mobile/README.md) para compilar e instalar Android.
No recrear contenedores ni borrar volúmenes para arrancar el proyecto.

Backend: pruebas PHPUnit en SQLite en memoria; el smoke HTTP conserva datos
sintéticos en PostgreSQL. Android: pruebas JVM, lint y compilación; las pruebas
físicas y HTTP se distinguen de los ejemplos y revisiones visuales.

Contrato actual: [TELEMETRY_CONTRACT](docs/TELEMETRY_CONTRACT.md).
Endpoints actuales: [API](docs/API.md).

## Guardar avances

Cada incremento debe conservar código y evidencia observada, actualizar el estado
y registrar las decisiones que cambien. Un commit guarda una versión local;
un push sincroniza los commits con GitHub. No hay sincronización automática.

Ver [política del repositorio](docs/REPOSITORY.md) para documentos, secretos y archivos grandes.
Los documentos originales se conservan sin modificar salvo solicitud explícita.

## Seguridad y datos

No subir `.env`, contraseñas Wi-Fi/MQTT/BD, llaves, tokens, configuraciones privadas,
respaldos operativos ni datos privados del proyecto del compañero. `.env.example`
solo debe contener nombres de configuración y valores ficticios o vacíos.

TDS simulado debe identificarse en mensaje, BD y Android; nunca usarse para
dosificación. Lux y nivel discreto deben conservar su significado físico.
Seguridad crítica y estado seguro pertenecen al ESP32, independientes de Internet.

El usuario autorizó expresamente el repositorio público y la inclusión de los
documentos académicos, que contienen información personal. Revisar nuevos
documentos y evidencias antes de subirlos; no incluir secretos ni información
privada de otras personas o proyectos.

## Recursos de terceros

Consultar [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) y
[procedencia de recursos](docs/recursos.json). No se declara una licencia global
para documentos académicos, código propio y recursos de terceros indistintamente.

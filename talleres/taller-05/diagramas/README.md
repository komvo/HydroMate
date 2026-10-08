# Diagramas del Taller 5

Disponibles: [conexiones de señal documentadas](conexiones.md) y
[flujo local editable](flujo-local.mmd), probado con ESP32 y Android.
El esquema eléctrico completo de alimentación y el flujo en nube siguen pendientes.
Conservar fuente editable y exportación legible. Identificar TDS simulado y
componentes planeados; no presentar arquitectura objetivo como ya ejecutada.

```mermaid
flowchart LR
  E["ESP32: cuatro variables reales y TDS simulado"] --> M["Mosquitto local 1884"]
  M --> I["Integrador Python: bandeja SQLite"]
  I -->|"POST JSON v2"| A["Laravel local"]
  A --> B["PostgreSQL: measurements"]
  B --> A
  A -->|"GET JSON"| D["Android por USB: Inicio e Historial"]
  A -->|"201 persistido"| I
  I -->|"ACK stored"| M
  M -->|"ACK stored"| E
```

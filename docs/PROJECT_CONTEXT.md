# Contexto vigente de HydroMate

Actualizado el 27/10/2026 con código y evidencias hasta el 21/10. Las
descripciones antiguas de TDS simulado o VPS candidata ya no aplican.

## Producto y responsabilidades

Torre hidropónica recirculante para monitoreo y diseño de control de solución
nutritiva. Primera unidad con identidad `hydromate-01`; preservar identidad por
cada torre al ampliar. ESP32 adquiere sensores y deberá ejecutar seguridad local;
Laravel valida, registra y sirve consultas; PostgreSQL persiste; Android Kotlin
consume HTTPS. Mosquitto y bridge Python conectan telemetría con la API.

El flujo físico público ya está comprobado. Se continúa sobre la implementación
existente; no reconstruir Wokwi/Blade, migrar frontend o sustituir tecnologías
por una plantilla. Los datos sintéticos se limitan a pruebas/demo explícitas.

## Producción conocida

| Elemento | Configuración pública o no sensible |
|---|---|
| API Android | https://hydromate-kevin.duckdns.org:9443, sin /api en URL base |
| MQTT ESP32 | hydromate-kevin.duckdns.org:8884, TLS con CA/hostname |
| Docker | rootless, usuario deploy-hydromate, proyecto hydromate |
| API host | 127.0.0.1:8081 → API8080 |
| MQTT y BD internos | 1884 / PostgreSQL5432; sin publicar al host |
| Configuración privada VPS | /etc/hydromate/.env, /etc/hydromate/https, /etc/hydromate/mqtt |

Los pasos remotos se ejecutan directamente en la VPS. `chitiito-*` es completamente intocable; no cambiar80/443/8443/8883,
volúmenes ajenos, perfiles AppArmor globales ni Docker global. Lectura actual de
Git/configuración no demuestra disponibilidad presente de la VPS.

## Hardware y compras

DS18B20 GPIO4; flotador GPIO27 LOW=agua; I2C SDA21/SCL22; ADS1115 0x48,
pH A0 y TDS A1; BH1750 luz en lux. EC independiente sin driver. El pH conserva
constantes históricas, sin nueva calibración acreditada. Un flotador no distingue
cortocircuito a GND de presencia de agua.

Compra identificada como sensor pH PH014 y MOSFET dual Noyito:
no asumir equivalencia exacta con PH-4502C/D4184 ni niveles eléctricos compatibles.
Fuente 24V/5A y dos XL4015 figuran en el lote pagado; bomba seleccionada 24V/25W,
sin acreditar corriente de arranque ni hidráulica medidas. Cuatro canales
nutrient_a/nutrient_b/ph_up/ph_down: mecanismo físico por validar; no presuponer
cuatro bombas peristálticas. GPIO de actuación del T8 son preliminares.

Presupuesto vigente y componentes: `Documentos PDC/T5_anexos/entrega-2026-10-21/presupuesto-actualizado.json` desde la raíz. Gasto $3,493.94; máximo $6,000;
disponible $2,506.06 MXN. Sustituye límites históricos del T6 anterior.

## Decisiones límites y documentos

D60: TDS real, eventos y adquisición solicitada. D61: continuidad Arduino-ESP32,
Sanctum para acceso, FCM para entregar avisos y BLE para alta Wi-Fi. Estas últimas
son decisiones, no autorización para implementarlas ni prueba de funcionamiento.
Protecciones locales deben bloquear nivel bajo, sensores inválidos, dosis
incompatibles y tiempos excesivos; sin deep sleep normal del controlador.

T5 demuestra viabilidad; T8 fija arquitectura; T6 actualizado contiene requisitos.
Los documentos académicos no se editan desde el código y conservan los límites
de cada prueba. La actuación se aplazó a la versión alfa; entrega final 2/12/2026.
La práctica Proteus está en `Documentos PDC/T9_anexos/`.

Estado y evidencias: STATUS.md. Cambios y publicación: REPOSITORY.md.

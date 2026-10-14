#pragma once
// Copiar como secrets.h (ignorado por Git) y editar SOLO ese archivo privado.
constexpr char WIFI_SSID[] = "";
constexpr char WIFI_PASSWORD[] = "";
constexpr char DEVICE_ID[] = "hydromate-01";
constexpr char MQTT_HOST[] = "hydromate-kevin.duckdns.org"; // Copiar al archivo privado; configurable.
constexpr uint16_t MQTT_PORT = 8884;
constexpr char MQTT_USER[] = "hydromate-device";
constexpr char MQTT_PASSWORD[] = "";
constexpr bool MQTT_TLS = true; // Banco LAN plano requiere opt-in de compilación explícito.
constexpr char MQTT_ROOT_CA[] = ""; // Certificado PEM de CA real para la fase VPS.

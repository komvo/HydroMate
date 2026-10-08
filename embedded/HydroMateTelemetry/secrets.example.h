#pragma once
// Copiar como secrets.h (ignorado por Git) y editar SOLO ese archivo privado.
constexpr char WIFI_SSID[] = "";
constexpr char WIFI_PASSWORD[] = "";
constexpr char DEVICE_ID[] = "hydromate-01";
constexpr char MQTT_HOST[] = "192.168.1.100"; // IPv4 de la PC; no 127.0.0.1.
constexpr uint16_t MQTT_PORT = 1884;
constexpr char MQTT_USER[] = "hydromate-device";
constexpr char MQTT_PASSWORD[] = "";
constexpr bool MQTT_TLS = false; // Banco LAN solamente. Internet requiere TLS.
constexpr char MQTT_ROOT_CA[] = ""; // Certificado PEM de CA real para la fase VPS.

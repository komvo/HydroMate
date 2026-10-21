#pragma once
// Replacement analog TDS module installed on ADS1115 A1 (confirmed by user).
#ifndef HYDROMATE_TDS_SENSOR_ENABLED
#define HYDROMATE_TDS_SENSOR_ENABLED 1
#endif
#ifndef HYDROMATE_TDS_ADC_CHANNEL
#define HYDROMATE_TDS_ADC_CHANNEL 1
#endif
#ifndef HYDROMATE_TDS_CALIBRATION_FACTOR
#define HYDROMATE_TDS_CALIBRATION_FACTOR 1.0f
#endif
// Used only when DS18B20 is invalid; Android explicitly labels uncompensated TDS.
#define HYDROMATE_TDS_REFERENCE_TEMPERATURE_C 25.0f
#define HYDROMATE_SENSOR_POLL_MS 500UL
#define HYDROMATE_PERIODIC_MS 30000UL
#define HYDROMATE_EVENT_MIN_INTERVAL_MS 750UL
#define HYDROMATE_WATER_DEBOUNCE_MS 150UL
// Thresholds concern telemetry changes, not crop limits or actuator commands.
#define HYDROMATE_LIGHT_CHANGE_LUX 50.0f
#define HYDROMATE_LIGHT_CHANGE_RATIO 0.30f
#define HYDROMATE_PH_CHANGE 0.20f
#define HYDROMATE_TEMPERATURE_CHANGE_C 1.0f
#define HYDROMATE_TDS_CHANGE_PPM 50.0f
#define HYDROMATE_TDS_CHANGE_RATIO 0.20f
// Production builds do not permit plain MQTT. Bank LAN builds may opt in explicitly.
#ifndef HYDROMATE_ALLOW_PLAIN_LAN
#define HYDROMATE_ALLOW_PLAIN_LAN 0
#endif

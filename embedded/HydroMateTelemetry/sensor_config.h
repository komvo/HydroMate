#pragma once
// Explicitly enable only after installing and validating the replacement TDS kit.
#ifndef HYDROMATE_TDS_SENSOR_ENABLED
#define HYDROMATE_TDS_SENSOR_ENABLED 0
#endif
#ifndef HYDROMATE_TDS_ADC_CHANNEL
#define HYDROMATE_TDS_ADC_CHANNEL 1
#endif
#ifndef HYDROMATE_TDS_CALIBRATION_FACTOR
#define HYDROMATE_TDS_CALIBRATION_FACTOR 1.0f
#endif
// Production builds do not permit plain MQTT. Bank LAN builds may opt in explicitly.
#ifndef HYDROMATE_ALLOW_PLAIN_LAN
#define HYDROMATE_ALLOW_PLAIN_LAN 0
#endif

#pragma once
#include <cmath>
#include <cstddef>

namespace hydromate {
struct Snapshot {
  float temperature = NAN, light = NAN, ph = NAN, tds = NAN;
  bool water = false;
};

inline float median(float* values, size_t count) {
  if (!count) return NAN;
  for (size_t i=0; i<count; ++i) {
    if (!std::isfinite(values[i])) return NAN;
    for (size_t j=i; j>0 && values[j]<values[j-1]; --j) {
      float value=values[j]; values[j]=values[j-1]; values[j-1]=value;
    }
  }
  return count%2 ? values[count/2] : (values[count/2-1]+values[count/2])/2;
}

// SEN0244/TDS Meter V1.0 transfer function; no EC is inferred from ppm.
inline float tdsFromVoltage(float volts, float temperature, float calibration) {
  if (!std::isfinite(volts) || volts<0 || volts>2.3f ||
      !std::isfinite(temperature) || temperature<0 || temperature>50 ||
      !std::isfinite(calibration) || calibration<=0) return NAN;
  float v=volts/(1.0f+0.02f*(temperature-25.0f));
  float ppm=((133.42f*v-255.86f)*v+857.39f)*v*0.5f*calibration;
  return std::isfinite(ppm) && ppm>=0 && ppm<=1000 ? ppm : NAN;
}

enum Change : unsigned {
  WATER=1, LIGHT=2, PH=4, TEMPERATURE=8, TDS=16, SENSOR_STATE=32
};

inline bool changed(float oldValue, float value, float absolute, float relative=0, float noiseFloor=0) {
  if (!std::isfinite(oldValue) || !std::isfinite(value)) return false;
  float delta=std::fabs(value-oldValue);
  return delta>=absolute || (relative>0 && delta>=noiseFloor &&
      delta>=relative*std::fabs(oldValue));
}

struct Thresholds {
  float light=50, lightRelative=0.30f, lightNoise=5;
  float ph=0.20f, temperature=1.0f;
  float tds=50, tdsRelative=0.20f, tdsNoise=10;
};

inline unsigned changes(const Snapshot& previous, const Snapshot& current, const Thresholds& limits) {
  unsigned result=previous.water!=current.water ? WATER : 0;
  if (changed(previous.light,current.light,limits.light,limits.lightRelative,limits.lightNoise)) result|=LIGHT;
  if (changed(previous.ph,current.ph,limits.ph)) result|=PH;
  if (changed(previous.temperature,current.temperature,limits.temperature)) result|=TEMPERATURE;
  if (changed(previous.tds,current.tds,limits.tds,limits.tdsRelative,limits.tdsNoise)) result|=TDS;
  if (std::isfinite(previous.light)!=std::isfinite(current.light) ||
      std::isfinite(previous.ph)!=std::isfinite(current.ph) ||
      std::isfinite(previous.temperature)!=std::isfinite(current.temperature) ||
      std::isfinite(previous.tds)!=std::isfinite(current.tds)) result|=SENSOR_STATE;
  return result;
}
} // namespace hydromate

#include "../../embedded/HydroMateTelemetry/telemetry_sensors.h"
#include <cassert>
#include <iostream>

int main() {
  using namespace hydromate;
  assert(tdsFromVoltage(0,25,1)==0); // Legitimate zero must not become "unavailable".
  assert(std::fabs(tdsFromVoltage(1,25,1)-367.475f)<0.01f);
  assert(tdsFromVoltage(1,35,1)<tdsFromVoltage(1,25,1));
  assert(!std::isfinite(tdsFromVoltage(3.3f,25,1)));
  assert(!std::isfinite(tdsFromVoltage(NAN,25,1)));
  assert(!std::isfinite(tdsFromVoltage(1,25,0)));
  float noisy[]={1.00f,1.01f,2.3f,0.99f,1.02f};
  assert(std::fabs(median(noisy,5)-1.01f)<0.001f);
  Thresholds t;
  Snapshot a; a.light=250; a.ph=6.2f; a.temperature=25; a.tds=500; a.water=true;
  Snapshot b=a; b.light=20;
  assert(changes(a,b,t)==LIGHT); // Covering light sensor causes immediate event.
  b=a; b.light=249;
  assert(changes(a,b,t)==0); // Quantization/noise must not flood telemetry.
  b=a; b.water=false; assert(changes(a,b,t)==WATER);
  b=a; b.tds=620; assert(changes(a,b,t)==TDS);
  b=a; b.ph=6.5f; assert(changes(a,b,t)==PH);
  b=a; b.temperature=NAN; assert(changes(a,b,t)==SENSOR_STATE);
  a=b; assert(changes(a,b,t)==0); // Repeated invalid sensor is not a new event.
  std::cout << "TDS conversion, median filter and event detection passed\n";
}

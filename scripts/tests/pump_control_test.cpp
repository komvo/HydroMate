#include "../../embedded/HydroMateTelemetry/pump_control.h"
#include <cassert>
#include <iostream>

int main() {
  using namespace hydromate;
  PumpController continuous({5000, 0, 0});
  assert(!continuous.update(0, true));        // Reset never starts the pump immediately.
  assert(!continuous.update(4999, true));
  assert(continuous.update(5000, true));      // Starts after confirmed water.
  assert(continuous.update(900000, true));    // offMs=0: continuous recirculation.
  assert(!continuous.update(900001, false));  // Low level stops it at once.
  assert(continuous.state() == PumpState::BLOCKED_LOW_LEVEL);
  assert(!continuous.update(900002, true));   // Water back: restart delay again.
  assert(!continuous.update(905001, true));
  assert(continuous.update(905002, true));

  PumpController cyclic({1000, 3000, 2000});
  cyclic.update(0, true);
  assert(cyclic.update(1000, true));
  assert(!cyclic.update(4000, true));          // ON 3 s elapsed.
  assert(cyclic.state() == PumpState::CYCLE_OFF);
  assert(!cyclic.update(5999, true));
  assert(cyclic.update(6000, true));           // OFF 2 s elapsed.
  assert(!cyclic.update(6500, false));         // Low level overrides the cycle.

  PumpController wrap({5000, 0, 0});           // millis() overflow keeps unsigned arithmetic valid.
  wrap.update(0xFFFFF000UL, true);
  assert(!wrap.update(0xFFFFFFFFUL, true));
  assert(wrap.update(0x00000F00UL, true));
  std::cout << "Pump start delay, low-level block, cycle and millis overflow passed\n";
}

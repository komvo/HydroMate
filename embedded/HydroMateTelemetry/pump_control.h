#pragma once
// Recirculation pump decision logic, free of Arduino calls so it can be tested on a PC.
// The hardware NOR interlock (74HCT02 with NIVEL) must block the pump independently of this code.

namespace hydromate {
struct PumpConfig {
  unsigned long restartDelayMs; // water must stay confirmed this long before (re)starting
  unsigned long onMs;           // cycle ON time; ignored when offMs is 0
  unsigned long offMs;          // 0 = continuous recirculation while water is present
};

enum class PumpState : unsigned char { BLOCKED_LOW_LEVEL, WAITING_RESTART, RUNNING, CYCLE_OFF };

inline const char* pumpStateName(PumpState state) {
  switch (state) {
    case PumpState::BLOCKED_LOW_LEVEL: return "BLOCKED_LOW_LEVEL";
    case PumpState::WAITING_RESTART: return "WAITING_RESTART";
    case PumpState::RUNNING: return "RUNNING";
    default: return "CYCLE_OFF";
  }
}

class PumpController {
 public:
  explicit PumpController(PumpConfig config) : config_(config) {}

  // water: debounced float reading. Starts blocked, so a reset never runs the pump immediately.
  bool update(unsigned long now, bool water) {
    if (!water) { state_ = PumpState::BLOCKED_LOW_LEVEL; return false; }
    switch (state_) {
      case PumpState::BLOCKED_LOW_LEVEL:
        enter(PumpState::WAITING_RESTART, now); break;
      case PumpState::WAITING_RESTART:
        if (now - since_ >= config_.restartDelayMs) enter(PumpState::RUNNING, now);
        break;
      case PumpState::RUNNING:
        if (config_.offMs && now - since_ >= config_.onMs) enter(PumpState::CYCLE_OFF, now);
        break;
      case PumpState::CYCLE_OFF:
        if (now - since_ >= config_.offMs) enter(PumpState::RUNNING, now);
        break;
    }
    return state_ == PumpState::RUNNING;
  }

  PumpState state() const { return state_; }

 private:
  void enter(PumpState state, unsigned long now) { state_ = state; since_ = now; }
  PumpConfig config_;
  PumpState state_ = PumpState::BLOCKED_LOW_LEVEL;
  unsigned long since_ = 0;
};
} // namespace hydromate

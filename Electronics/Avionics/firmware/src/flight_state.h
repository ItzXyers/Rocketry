#pragma once

#include <stdint.h>

#include "sensors.h"

enum class FlightState : uint8_t {
  INIT,
  SELF_TEST,
  IDLE_ARMED,
  BOOST,
  COAST,
  APOGEE,        // one-sample marker; code 5 (was APOGEE_DEPLOY, which fired the deploy channel)
  DESCENT,
  LANDED,
  ERROR,
};

// Runs self-test (sensors + logger), plays the pass/fail buzzer tone, and
// transitions to IDLE_ARMED or ERROR. Call once from setup(), after
// sensors_init() / buzzer_init().
void flight_state_init();

// Feeds one sensor sample into the state machine and advances it as
// needed. Call every loop() iteration on the SENSOR_SAMPLE_INTERVAL_MS
// schedule. In-flight sensor loss (e.g. a dropped barometer reading) is
// handled by falling back to timer-based logic within COAST/DESCENT — it
// never transitions to ERROR. ERROR is only reachable from SELF_TEST at
// boot.
FlightState flight_state_update(const SensorSample &sample);

FlightState flight_state_current();

// Most recent sample passed to flight_state_update(); zero-valued
// (default-constructed SensorSample) before the first call.
SensorSample flight_state_lastSample();

// True iff flight_state_init() reached IDLE_ARMED (not ERROR) at boot.
// Reflects the boot-time self-test only — a later wireless-arm rerun of
// sensors_selfTest() does not update this; see wireless.h's
// wireless_armed status field for that.
bool flight_state_bootSelfTestPassed();

// Human-readable name for a FlightState, e.g. "IDLE_ARMED" — for
// diagnostics/JSON, not used in any control-flow decision.
const char *flight_state_name(FlightState state);

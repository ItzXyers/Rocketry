#pragma once

#include <stdint.h>

// The buzzer is an ACTIVE buzzer (fixed pitch, see ../../avionics_bom.md):
// every "sound" is a rhythm of on/off steps, not a melody.
enum class BuzzerPattern : uint8_t {
  OFF,
  SELF_TEST_PASS,   // short double-beep, once — "safe to arm" confirmation
  SELF_TEST_FAIL,   // fast continuous repeat — deliberately insistent "do not fly" signal
  RECOVERY_BEACON,  // slow, low-duty chirp — battery-conscious for a multi-hour search
  ARM_CONFIRM,      // beep-beep-beeeep, once, then silence
  ARM_REJECTED,     // five fast blips, once, then resumes whatever looped before (e.g. SELF_TEST_FAIL)
};

// pinMode(OUTPUT) + LOW, first thing in setup(): a stray HIGH during boot is
// an unwanted chirp, not a hazard.
void buzzer_init();

// No-op if already playing this pattern (restarting an identical pattern
// would otherwise reset its phase every call).
void buzzer_setPattern(BuzzerPattern pattern);

BuzzerPattern buzzer_currentPattern();

// One blocking chirp (gate on, delay, gate off) for "command received"
// feedback right before a blocking ground action (e.g. /arm's ~4 s pad
// calibration), during which buzzer_update() can't step a pattern. Stops
// whatever pattern was playing first, so the gate is never left on across
// the block. Ground-only: never call this in flight.
void buzzer_chirpBlocking(uint16_t duration_ms);

// Non-blocking, millis()-driven. Call every loop() iteration regardless of
// sensor sample cadence, or beep timing will be uneven.
void buzzer_update();

#pragma once

#include <stdint.h>

enum class BuzzerPattern : uint8_t {
  OFF,
  SELF_TEST_PASS,   // short double-beep, once — "safe to arm" confirmation
  SELF_TEST_FAIL,   // fast continuous repeat — deliberately insistent "do not fly" signal
  RECOVERY_BEACON,  // slow, low-duty chirp — battery-conscious for a multi-hour search
  ARM_OK,           // beep-beep-beeeep, once — wireless /arm succeeded, radio going off, walk away
  ARM_FAIL,         // three long buzzes, once — /arm refused (self-test failed); radio stays up, retry
};

// pinMode(OUTPUT) + LOW, first thing in setup(): a stray HIGH during boot is
// an unwanted chirp, not a hazard.
void buzzer_init();

// No-op if this pattern is still playing (restarting it would reset its
// phase every call). A one-shot pattern that has already finished is
// replayed, so e.g. a second failed /arm beeps again.
void buzzer_setPattern(BuzzerPattern pattern);

// Non-blocking, millis()-driven. Call every loop() iteration regardless of
// sensor sample cadence, or beep timing will be uneven.
void buzzer_update();

#pragma once

#include <stdint.h>

// Magnet toggle power latch (schematic rev F, item 1).
//
// Power-ON is pure hardware: the magnet closes SW1, which pulls Q3's gate
// low through CR1 and powers the bay. power_init() then drives
// PIN_POWER_HOLD high, turning on Q5, which keeps Q3's gate low after the
// magnet is removed. C5 + R13 on Q5's gate (a 2N7000) hold it on for ~0.5 s
// through a reset, long enough for the ESP32 to reboot and re-assert the latch.
//
// Power-OFF is a firmware gesture: SW1 also pulls PIN_POWER_SENSE low through
// CR2. Holding the magnet POWER_OFF_HOLD_MS (after it was released once since
// boot) releases the latch -- but only when the caller says it's safe (never
// in flight). The bay then switches off when the magnet is taken away.

// Latch power on and configure the sense input. Call as early as possible in
// setup(): the user is holding the magnet until this runs.
void power_init();

// Debounces the magnet sense and tracks the hold gesture. Returns true exactly
// once, on the iteration a valid power-off hold completes while offAllowed.
// The caller then logs/flushes and calls power_release(). Call every loop().
bool power_poll(bool offAllowed);

// Drops the latch. Power stays on while the magnet is still held (SW1 keeps
// Q3's gate low through CR1) and goes off when it's removed.
void power_release();

// Debounced live state of the magnet sense, for diagnostics.
bool power_magnetPresent();

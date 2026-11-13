#pragma once

#include <stdint.h>

// Battery voltage monitor: BATT+ -> R11/R12 divider -> PIN_BATT_SENSE (A7).
// A7 is on ADC2, which the ESP32-S3 shares with Wi-Fi, so the radio owner
// (wireless.cpp) brackets the AP with battery_setRadioOn(): no ADC reads
// while it is on, the last radio-off reading is held, and sampling restarts
// (re-seeded, not filtered) once the radio is off again.
// See ../../avionics_bay_schematic_phoenix40.html.
//
// Read-only telemetry: logged, shown on /status and the serial console,
// never an input to flight_state's detectors.

// Takes a first reading so the value is valid from boot. Call once from
// setup(), before anything logs.
void battery_init();

// Non-blocking; re-samples every BATT_SAMPLE_INTERVAL_MS and low-pass
// filters. Call every loop() iteration.
void battery_update();

// Call with true IMMEDIATELY BEFORE turning the radio on -- it takes one
// fresh reading first, so the held value is as recent as possible -- and
// with false right after turning it off.
void battery_setRadioOn(bool on);

// True while readings are frozen because the radio is on.
bool battery_held();

// ms since the value was last actually measured.
uint32_t battery_ageMs();

// Filtered battery voltage at the cell (divider ratio + calibration applied).
float battery_voltage();

// 0..100, from the generic LiPo curve in battery_soc.h -- approximate.
uint8_t battery_percent();

// False when the sense reads below BATT_PRESENT_MIN_V: divider not fitted,
// or the board is running from USB with the battery switched out.
bool battery_valid();

// True when valid and at or below BATT_LOW_V.
bool battery_low();

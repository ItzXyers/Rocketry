#pragma once

#include <stdint.h>

// Battery voltage monitor: BATT+ -> R11/R12 divider -> PIN_BATT_SENSE (A0,
// ADC1 so it keeps working while the Wi-Fi AP is up -- ADC2 is shared with
// the radio on the ESP32-S3). See ../../avionics_bay_schematic_phoenix40.html.
//
// Read-only telemetry: logged, shown on /status and the serial console,
// never an input to flight_state's detectors or to deployment.

// Takes a first reading so the value is valid from boot. Call once from
// setup(), before anything logs.
void battery_init();

// Non-blocking; re-samples every BATT_SAMPLE_INTERVAL_MS and low-pass
// filters. Call every loop() iteration.
void battery_update();

// Filtered battery voltage at the cell (divider ratio + calibration applied).
float battery_voltage();

// 0..100, from the generic LiPo curve in battery_soc.h -- approximate.
uint8_t battery_percent();

// False when the sense reads below BATT_PRESENT_MIN_V: divider not fitted,
// or the board is running from USB with the battery switched out.
bool battery_valid();

// True when valid and at or below BATT_LOW_V.
bool battery_low();

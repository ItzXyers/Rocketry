#pragma once

// Pure math for the 1S LiPo state-of-charge estimate -- no Arduino/board
// dependencies, so the native test env can exercise it (same split as
// kalman_filter.h vs velocity_estimator.cpp).
//
// The table is a generic 1S LiPo open-circuit-voltage curve at ~room
// temperature, NOT a measured curve for the EEMB LP852040. It is good to
// roughly +/-10 % at rest; under load the cell sags (at this board's
// ~50-150 mA cruise draw only ~10-25 mV, so the error is small), and in the
// cold the whole curve shifts down. Treat the percentage as a pad go/no-go
// indicator, and the voltage as the number that matters.

#include <stdint.h>

struct BattSocPoint {
  float volts;
  uint8_t percent;
};

// Strictly descending in volts.
static const BattSocPoint BATT_SOC_TABLE[] = {
    {4.20f, 100}, {4.15f, 95}, {4.11f, 90}, {4.08f, 85}, {4.02f, 80},
    {3.98f, 75},  {3.95f, 70}, {3.91f, 65}, {3.87f, 60}, {3.85f, 55},
    {3.84f, 50},  {3.82f, 45}, {3.80f, 40}, {3.79f, 35}, {3.77f, 30},
    {3.75f, 25},  {3.73f, 20}, {3.71f, 15}, {3.69f, 10}, {3.61f, 5},
    {3.27f, 0},
};

// Piecewise-linear interpolation of the table, clamped to 0..100.
inline uint8_t battery_socPercentFromVolts(float volts) {
  const unsigned n = sizeof(BATT_SOC_TABLE) / sizeof(BATT_SOC_TABLE[0]);
  if (volts >= BATT_SOC_TABLE[0].volts) {
    return 100;
  }
  if (volts <= BATT_SOC_TABLE[n - 1].volts) {
    return 0;
  }
  for (unsigned i = 1; i < n; i++) {
    const BattSocPoint &hi = BATT_SOC_TABLE[i - 1];
    const BattSocPoint &lo = BATT_SOC_TABLE[i];
    if (volts >= lo.volts) {
      float t = (volts - lo.volts) / (hi.volts - lo.volts);
      float pct = lo.percent + t * (hi.percent - lo.percent);
      return static_cast<uint8_t>(pct + 0.5f);
    }
  }
  return 0; // unreachable
}

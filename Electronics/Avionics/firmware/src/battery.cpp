#include "battery.h"
#include "battery_soc.h"
#include "config.h"

#include <Arduino.h>

namespace {

float g_volts = 0.0f;
bool g_valid = false;
uint32_t g_lastSampleAt = 0;

// analogReadMilliVolts() applies the chip's eFuse ADC calibration. The core's
// default 11 dB attenuation covers ~0-3.1 V at the pin; a full 4.2 V cell
// through the /2 divider is 2.1 V, well inside the linear part of that range.
float readCellVolts() {
  uint32_t sumMv = 0;
  for (uint8_t i = 0; i < BATT_ADC_SAMPLES; i++) {
    sumMv += analogReadMilliVolts(PIN_BATT_SENSE);
  }
  float pinVolts = (static_cast<float>(sumMv) / BATT_ADC_SAMPLES) / 1000.0f;
  return pinVolts * BATT_DIVIDER_RATIO * BATT_CAL_GAIN;
}

} // namespace

void battery_init() {
  pinMode(PIN_BATT_SENSE, INPUT);
  g_volts = readCellVolts();
  g_valid = g_volts >= BATT_PRESENT_MIN_V;
  g_lastSampleAt = millis();
}

void battery_update() {
  uint32_t now = millis();
  if (now - g_lastSampleAt < BATT_SAMPLE_INTERVAL_MS) {
    return;
  }
  g_lastSampleAt = now;

  float v = readCellVolts();
  if (!g_valid) {
    g_volts = v; // (re)seed instead of filtering up from a stale/absent value
  } else {
    g_volts += BATT_FILTER_ALPHA * (v - g_volts);
  }
  g_valid = g_volts >= BATT_PRESENT_MIN_V;
}

float battery_voltage() { return g_volts; }

uint8_t battery_percent() { return g_valid ? battery_socPercentFromVolts(g_volts) : 0; }

bool battery_valid() { return g_valid; }

bool battery_low() { return g_valid && g_volts <= BATT_LOW_V; }

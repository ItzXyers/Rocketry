#include "battery.h"
#include "battery_soc.h"
#include "config.h"

#include <Arduino.h>

namespace {

float g_volts = 0.0f;
bool g_valid = false;
uint32_t g_lastSampleAt = 0;
uint32_t g_lastGoodAt = 0;

// analogReadMilliVolts() applies the chip's eFuse ADC calibration. The core's
// default 11 dB attenuation covers ~0-3.1 V at the pin; a full 4.2 V cell
// through the /2 divider is 2.1 V, well inside the linear part of that range.
//
// PIN_BATT_SENSE is on ADC2, which the Wi-Fi radio also uses. When the radio
// holds it, the read fails and the core returns ~0 mV. Those samples are
// dropped (anything under BATT_SAMPLE_MIN_MV -- a real cell is >= ~1250 mV
// at the pin). Returns false if no sample in the batch was good.
bool readCellVolts(float &cellVolts) {
  uint32_t sumMv = 0;
  uint8_t good = 0;
  for (uint8_t i = 0; i < BATT_ADC_SAMPLES; i++) {
    uint32_t mv = analogReadMilliVolts(PIN_BATT_SENSE);
    if (mv >= BATT_SAMPLE_MIN_MV) {
      sumMv += mv;
      good++;
    }
  }
  if (good == 0) return false;
  float pinVolts = (static_cast<float>(sumMv) / good) / 1000.0f;
  cellVolts = pinVolts * BATT_DIVIDER_RATIO * BATT_CAL_GAIN;
  return true;
}

} // namespace

void battery_init() {
  pinMode(PIN_BATT_SENSE, INPUT);
  float v;
  uint32_t now = millis();
  if (readCellVolts(v)) {
    g_volts = v;
    g_valid = g_volts >= BATT_PRESENT_MIN_V;
    g_lastGoodAt = now;
  } else {
    g_volts = 0.0f;
    g_valid = false;
  }
  g_lastSampleAt = now;
}

void battery_update() {
  uint32_t now = millis();
  if (now - g_lastSampleAt < BATT_SAMPLE_INTERVAL_MS) {
    return;
  }
  g_lastSampleAt = now;

  float v;
  if (!readCellVolts(v)) {
    // Failed read (Wi-Fi holding ADC2) or nothing on the pin: hold the last
    // good value, and give up on it once it's too old.
    if (g_valid && now - g_lastGoodAt >= BATT_STALE_MS) {
      g_valid = false;
      g_volts = 0.0f;
    }
    return;
  }
  g_lastGoodAt = now;

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

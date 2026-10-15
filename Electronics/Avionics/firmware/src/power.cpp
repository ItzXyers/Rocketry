#include "power.h"
#include "config.h"

#include <Arduino.h>

namespace {

bool g_rawLast = false;
bool g_present = false;          // debounced: magnet on SW1 (sense reads LOW)
uint32_t g_changedAt = 0;
uint32_t g_pressStartedAt = 0;
bool g_waitRelease = true;       // the magnet that switched us on is usually still there at boot
bool g_released = false;

bool readSenseRaw() { return digitalRead(PIN_POWER_SENSE) == LOW; }

} // namespace

void power_init() {
  pinMode(PIN_POWER_HOLD, OUTPUT);
  digitalWrite(PIN_POWER_HOLD, HIGH);
  pinMode(PIN_POWER_SENSE, INPUT_PULLUP);
  g_rawLast = readSenseRaw();
  g_present = g_rawLast;
  g_changedAt = millis();
  g_pressStartedAt = g_changedAt;
  g_waitRelease = g_present; // booted by the magnet: it has to come off once before a hold counts
  g_released = false;
}

bool power_poll(bool offAllowed) {
  uint32_t now = millis();
  bool raw = readSenseRaw();
  if (raw != g_rawLast) {
    g_rawLast = raw;
    g_changedAt = now;
  }
  if (raw != g_present && now - g_changedAt >= POWER_SENSE_DEBOUNCE_MS) {
    g_present = raw;
    if (g_present) {
      g_pressStartedAt = now;
    } else {
      g_waitRelease = false; // a fresh hold may now count
    }
  }

  if (g_released || !g_present || g_waitRelease) {
    return false;
  }
  if (now - g_pressStartedAt < POWER_OFF_HOLD_MS) {
    return false;
  }
  g_waitRelease = true; // one decision per hold, whatever it is
  if (!offAllowed) {
    Serial.println(F("[power] magnet hold ignored: power-off is blocked in flight"));
    return false;
  }
  return true;
}

void power_release() {
  digitalWrite(PIN_POWER_HOLD, LOW);
  g_released = true;
  Serial.println(F("[power] latch released -- remove the magnet to switch off"));
}

bool power_magnetPresent() { return g_present; }

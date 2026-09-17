#include "deployment.h"
#include "config.h"

#include <Arduino.h>
#include <esp_attr.h>

namespace {

// RTC memory survives a software reset / watchdog reset / brownout reset
// (the BOM's own flagged brownout risk) but is cleared on a cold power-on —
// which lines up with the CAD docs' manual per-flight reload procedure
// (fresh retaining line, spring re-cocked). A reset mid-flight must not
// grant a second firing attempt.
RTC_DATA_ATTR bool g_firedLatch = false;

bool g_gateOn = false;
uint32_t g_fireStart = 0;

bool g_benchArmed = false;
uint32_t g_benchArmedAt = 0;

void gate(bool on) {
  g_gateOn = on;
  digitalWrite(PIN_DEPLOY, on ? HIGH : LOW);
}

bool startFire() {
  if (g_firedLatch) {
    return false;
  }
  // Set the instant firing starts, not after it completes — a reset during
  // the on-time window must not allow a second attempt.
  g_firedLatch = true;
  g_fireStart = millis();
  gate(true);
  return true;
}

} // namespace

void deployment_init() {
  digitalWrite(PIN_DEPLOY, LOW);
  pinMode(PIN_DEPLOY, OUTPUT);
  digitalWrite(PIN_DEPLOY, LOW);
}

bool deployment_fire() { return startFire(); }

void deployment_update() {
  if (!g_gateOn) {
    return;
  }

  uint32_t elapsed = millis() - g_fireStart;

  // Hard safety cutoff — checked first, unconditionally, structurally
  // separate from the normal on-time turnoff below. This must never be
  // bypassed by any future change to the normal path.
  if (elapsed >= DEPLOY_MAX_ON_TIME_MS) {
    gate(false);
    return;
  }

  if (elapsed >= DEPLOY_ON_TIME_MS) {
    gate(false);
  }
}

bool deployment_hasFired() { return g_firedLatch; }

bool deployment_isFiring() { return g_gateOn; }

bool deployment_bench_arm() {
  if (g_firedLatch) {
    return false;
  }
  g_benchArmed = true;
  g_benchArmedAt = millis();
  return true;
}

bool deployment_bench_fire() {
  if (!g_benchArmed) {
    return false;
  }
  bool withinWindow = (millis() - g_benchArmedAt) <= DEPLOY_BENCH_ARM_TIMEOUT_MS;
  g_benchArmed = false; // single-use arm regardless of outcome
  if (!withinWindow) {
    return false;
  }
  return startFire();
}

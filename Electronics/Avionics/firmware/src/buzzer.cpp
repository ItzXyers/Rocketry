#include "buzzer.h"
#include "config.h"

#include <Arduino.h>

namespace {

struct Step {
  bool on;
  uint16_t duration_ms;
};

const Step SELF_TEST_PASS_STEPS[] = {{true, 100}, {false, 100}, {true, 100}};
const Step SELF_TEST_FAIL_STEPS[] = {{true, 150}, {false, 150}};
const Step RECOVERY_BEACON_STEPS[] = {{true, 120}, {false, 2880}};
// Active buzzer = on/off only, so the arm tones differ from the boot
// double-beep (2 x 100 ms) by rhythm: OK ends on a long tone, FAIL is all long.
const Step ARM_OK_STEPS[] = {{true, 100}, {false, 100}, {true, 100}, {false, 100}, {true, 700}};
const Step ARM_FAIL_STEPS[] = {{true, 500}, {false, 250}, {true, 500}, {false, 250}, {true, 500}};

struct PatternDef {
  const Step *steps;
  uint8_t count;
  bool loop; // false = hold silent after the last step (one-shot)
};

const PatternDef PATTERNS[] = {
    /* OFF             */ {nullptr, 0, false},
    /* SELF_TEST_PASS  */ {SELF_TEST_PASS_STEPS, 3, false},
    /* SELF_TEST_FAIL  */ {SELF_TEST_FAIL_STEPS, 2, true},
    /* RECOVERY_BEACON */ {RECOVERY_BEACON_STEPS, 2, true},
    /* ARM_OK          */ {ARM_OK_STEPS, 5, false},
    /* ARM_FAIL        */ {ARM_FAIL_STEPS, 5, false},
};

BuzzerPattern g_pattern = BuzzerPattern::OFF;
uint8_t g_stepIndex = 0;
uint32_t g_stepStart = 0;
bool g_finished = true;

void setGate(bool on) { digitalWrite(PIN_BUZZER, on ? HIGH : LOW); }

const PatternDef &currentDef() { return PATTERNS[static_cast<uint8_t>(g_pattern)]; }

} // namespace

void buzzer_init() {
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
}

void buzzer_setPattern(BuzzerPattern pattern) {
  if (pattern == g_pattern && !g_finished) {
    return;
  }
  g_pattern = pattern;
  g_stepIndex = 0;
  g_stepStart = millis();

  const PatternDef &def = currentDef();
  if (def.count == 0) {
    g_finished = true;
    setGate(false);
  } else {
    g_finished = false;
    setGate(def.steps[0].on);
  }
}

void buzzer_update() {
  if (g_finished) {
    return;
  }

  const PatternDef &def = currentDef();
  uint32_t now = millis();
  if (now - g_stepStart < def.steps[g_stepIndex].duration_ms) {
    return;
  }

  g_stepIndex++;
  if (g_stepIndex >= def.count) {
    if (!def.loop) {
      setGate(false);
      g_finished = true;
      return;
    }
    g_stepIndex = 0;
  }
  g_stepStart = now;
  setGate(def.steps[g_stepIndex].on);
}

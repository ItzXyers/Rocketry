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
// Rising "beep-beep-beeeep": unmistakably different from the boot double-beep.
// The trailing silence separates it from the first ARMED_REMINDER chirp.
const Step ARM_CONFIRM_STEPS[] = {{true, 80},  {false, 120}, {true, 80},
                                  {false, 120}, {true, 600},  {false, 1500}};
// ~2.5 % duty: cheap on the battery for a long wait on the pad, and a
// different rhythm (double, ~4 s) from the recovery beacon (single, 3 s).
const Step ARMED_REMINDER_STEPS[] = {{true, 40}, {false, 80}, {true, 40}, {false, 3840}};
const Step ARM_REJECTED_STEPS[] = {{true, 60}, {false, 60}, {true, 60}, {false, 60}, {true, 60},
                                   {false, 60}, {true, 60}, {false, 60}, {true, 60}, {false, 600}};

// What a one-shot pattern does after its last step.
enum class After : uint8_t { SILENCE, NEXT, RESUME };

struct PatternDef {
  const Step *steps;
  uint8_t count;
  bool loop;          // true = repeat forever; `after` is ignored
  After after;        // one-shot only
  BuzzerPattern next; // used when after == NEXT
};

#define STEPS(a) a, static_cast<uint8_t>(sizeof(a) / sizeof(a[0]))

// Indexed by BuzzerPattern -- keep in enum order.
const PatternDef PATTERNS[] = {
    /* OFF             */ {nullptr, 0, false, After::SILENCE, BuzzerPattern::OFF},
    /* SELF_TEST_PASS  */ {STEPS(SELF_TEST_PASS_STEPS), false, After::SILENCE, BuzzerPattern::OFF},
    /* SELF_TEST_FAIL  */ {STEPS(SELF_TEST_FAIL_STEPS), true, After::SILENCE, BuzzerPattern::OFF},
    /* RECOVERY_BEACON */ {STEPS(RECOVERY_BEACON_STEPS), true, After::SILENCE, BuzzerPattern::OFF},
    /* ARM_CONFIRM     */ {STEPS(ARM_CONFIRM_STEPS), false, After::NEXT, BuzzerPattern::ARMED_REMINDER},
    /* ARMED_REMINDER  */ {STEPS(ARMED_REMINDER_STEPS), true, After::SILENCE, BuzzerPattern::OFF},
    /* ARM_REJECTED    */ {STEPS(ARM_REJECTED_STEPS), false, After::RESUME, BuzzerPattern::OFF},
};
static_assert(sizeof(PATTERNS) / sizeof(PATTERNS[0]) ==
                  static_cast<uint8_t>(BuzzerPattern::ARM_REJECTED) + 1,
              "PATTERNS must have one entry per BuzzerPattern, in enum order");

BuzzerPattern g_pattern = BuzzerPattern::OFF;
BuzzerPattern g_resume = BuzzerPattern::OFF; // last looping pattern, for After::RESUME
uint8_t g_stepIndex = 0;
uint32_t g_stepStart = 0;
bool g_finished = true;

void setGate(bool on) { digitalWrite(PIN_BUZZER, on ? HIGH : LOW); }

const PatternDef &defOf(BuzzerPattern p) { return PATTERNS[static_cast<uint8_t>(p)]; }

} // namespace

void buzzer_init() {
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
}

void buzzer_setPattern(BuzzerPattern pattern) {
  if (pattern == g_pattern) {
    return;
  }
  // ARM_REJECTED resumes what was looping before it, so a rejected arm
  // never silences e.g. the SELF_TEST_FAIL "do not fly" alarm for good.
  if (pattern == BuzzerPattern::ARM_REJECTED) {
    g_resume = defOf(g_pattern).loop ? g_pattern : BuzzerPattern::OFF;
  }

  g_pattern = pattern;
  g_stepIndex = 0;
  g_stepStart = millis();

  const PatternDef &def = defOf(pattern);
  if (def.count == 0) {
    g_finished = true;
    setGate(false);
  } else {
    g_finished = false;
    setGate(def.steps[0].on);
  }
}

BuzzerPattern buzzer_currentPattern() { return g_pattern; }

void buzzer_chirpBlocking(uint16_t duration_ms) {
  // What to restart afterwards: a looping pattern restarts, an in-progress
  // one-shot is dropped (or, for ARM_REJECTED, its resume target restarts).
  BuzzerPattern after = defOf(g_pattern).loop ? g_pattern
                        : (g_pattern == BuzzerPattern::ARM_REJECTED ? g_resume : BuzzerPattern::OFF);
  g_finished = true;
  setGate(true);
  delay(duration_ms);
  setGate(false);
  g_pattern = BuzzerPattern::OFF;
  buzzer_setPattern(after);
}

void buzzer_update() {
  if (g_finished) {
    return;
  }

  const PatternDef &def = defOf(g_pattern);
  uint32_t now = millis();
  if (now - g_stepStart < def.steps[g_stepIndex].duration_ms) {
    return;
  }

  g_stepIndex++;
  if (g_stepIndex >= def.count) {
    if (!def.loop) {
      setGate(false);
      g_finished = true;
      if (def.after == After::NEXT) {
        buzzer_setPattern(def.next);
      } else if (def.after == After::RESUME) {
        BuzzerPattern resume = g_resume;
        g_pattern = BuzzerPattern::OFF; // so setPattern doesn't no-op
        buzzer_setPattern(resume);
      }
      return;
    }
    g_stepIndex = 0;
  }
  g_stepStart = now;
  setGate(def.steps[g_stepIndex].on);
}

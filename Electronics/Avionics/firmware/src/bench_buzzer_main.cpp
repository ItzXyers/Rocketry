// Standalone bench bring-up for the buzzer module in isolation, before the
// rest of the harness (sensors/flash log) is wired up. Exercises the
// real buzzer.cpp patterns, not a throwaway blink-style test.
//
// Build/flash/monitor:
//   pio run -e buzzer_bench -t upload
//   pio device monitor
//
// Serial commands: PASS, FAIL, BEACON, ARM, REJECT, OFF

#include "buzzer.h"
#include "config.h"

#include <Arduino.h>

namespace {

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd == "PASS") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_PASS);
    Serial.println(F("[bench] SELF_TEST_PASS - short double-beep, once"));
  } else if (cmd == "FAIL") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_FAIL);
    Serial.println(F("[bench] SELF_TEST_FAIL - fast continuous repeat"));
  } else if (cmd == "BEACON") {
    buzzer_setPattern(BuzzerPattern::RECOVERY_BEACON);
    Serial.println(F("[bench] RECOVERY_BEACON - slow low-duty chirp"));
  } else if (cmd == "ARM") {
    buzzer_setPattern(BuzzerPattern::ARM_CONFIRM);
    Serial.println(F("[bench] ARM_CONFIRM - beep-beep-beeeep, once"));
  } else if (cmd == "REJECT") {
    buzzer_setPattern(BuzzerPattern::ARM_REJECTED);
    Serial.println(F("[bench] ARM_REJECTED - five fast blips, then resumes"));
  } else if (cmd == "OFF") {
    buzzer_setPattern(BuzzerPattern::OFF);
    Serial.println(F("[bench] OFF"));
  } else if (cmd.length() > 0) {
    Serial.println(F("[bench] unknown command. Available: PASS, FAIL, BEACON, ARM, REJECT, OFF"));
  }
}

void pollSerialCommands() {
  static String buf;
  while (Serial.available() > 0) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (buf.length() > 0) {
        handleCommand(buf);
        buf = "";
      }
    } else {
      buf += c;
    }
  }
}

} // namespace

void setup() {
  buzzer_init();
  Serial.begin(115200);
  delay(200);
  Serial.println(F("[bench] buzzer bring-up ready. Commands: PASS, FAIL, BEACON, ARM, REJECT, OFF"));
}

void loop() {
  pollSerialCommands();
  buzzer_update();
}

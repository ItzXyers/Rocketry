// Standalone bench tool: find which pin the battery-sense divider is wired to.
//
// Use it when PIN_BATT_SENSE in config.h no longer matches the harness. It
// scans every ADC-capable header pin on the Nano ESP32 and scores each one
// against what the R11/R12 10k/10k divider looks like electrically:
//
//   1. Voltage: the divider midpoint sits at half the cell voltage, so a
//      3.0-4.25 V 1S LiPo gives 1.50-2.13 V at the pin.
//   2. Stiffness ("pull test"): the divider is a ~5 kOhm source. Turning the
//      chip's internal ~45 kOhm pull-up or pull-down on barely moves it (about
//      0.1-0.2 V). A floating pin swings rail to rail, and an I2C line held up
//      by a pull-up drops a long way when the internal pull-down is on.
//   3. Noise: a floating pin wanders between reads. The divider doesn't.
//
// A pin that passes all three is reported as the battery sense, along with the
// line to put in config.h.
//
// The board must run on the battery (a USB-only board reads ~0 V on the
// divider). With USB also connected you can type WATCH, then unplug and
// replug the battery: the pin that follows it is the divider.
//
// Build/flash/monitor:
//   pio run -e battfind_bench -t upload
//   pio device monitor          (115200 baud)
// Re-flash the flight firmware (pio run -e nano_esp32 -t upload) afterwards.
//
// Commands (case-insensitive):
//   SCAN    run the scan again (also runs once at boot)
//   WATCH   toggle a live 1 Hz table of every pin's voltage
//   HELP    this list
//
// It writes no outputs. It only reads pins and turns the internal pulls on and
// off for a few milliseconds per pin. It doesn't start I2C, so the sensors
// aren't touched. The buzzer pin (D9) is read as an input. Its 10k base
// pulldown keeps the buzzer silent.

#include <Arduino.h>
#include <driver/gpio.h>

namespace {

struct ScanPin {
  const char *label;
  uint8_t arduinoPin; // symbolic Dn/An, for analogReadMilliVolts()
  gpio_num_t gpio;    // ESP32-S3 GPIO, for the ESP-IDF pull calls
  const char *note;
};

// Every Nano ESP32 header pin with an ADC channel. D10-D13 (GPIO21/38/47/48)
// have no ADC and can't be the battery sense. D0/D1 are the UART and B0/B1
// are boot straps, so they're left out.
// Arduino label -> GPIO from the Nano ESP32 (ABX00083) pinout.
const ScanPin kPins[] = {
    {"A0", A0, GPIO_NUM_1, "config.h PIN_BATT_SENSE"},
    {"A1", A1, GPIO_NUM_2, ""},
    {"A2", A2, GPIO_NUM_3, ""},
    {"A3", A3, GPIO_NUM_4, ""},
    {"A4", A4, GPIO_NUM_11, "I2C SDA"},
    {"A5", A5, GPIO_NUM_12, "I2C SCL"},
    {"A6", A6, GPIO_NUM_13, ""},
    {"A7", A7, GPIO_NUM_14, ""},
    {"D2", D2, GPIO_NUM_5, "reserved GPS"},
    {"D3", D3, GPIO_NUM_6, "reserved GPS"},
    {"D4", D4, GPIO_NUM_7, ""},
    {"D5", D5, GPIO_NUM_8, ""},
    {"D6", D6, GPIO_NUM_9, ""},
    {"D7", D7, GPIO_NUM_10, ""},
    {"D8", D8, GPIO_NUM_17, "ADC2"},
    {"D9", D9, GPIO_NUM_18, "buzzer, ADC2"},
};
constexpr size_t kPinCount = sizeof(kPins) / sizeof(kPins[0]);

// Same bounds as config.h, restated so this tool builds on its own:
// BATT_DIVIDER_RATIO 2.0, BATT_PRESENT_MIN_V 2.5 V (a deeply flat cell is
// still found), up to a full cell plus ADC error.
constexpr float kDividerRatio = 2.0f;
constexpr float kPinMinV = 1.25f; // 2.5 V cell
constexpr float kPinMaxV = 2.25f; // 4.5 V cell, slack for ADC gain error
// A 5k source against a ~45k internal pull moves the pin ~0.1-0.2 V.
// Anything under this counts as "stiff".
constexpr float kStiffMaxSwingV = 0.45f;
constexpr float kQuietMaxSpanV = 0.08f; // peak-to-peak across the noise reads

constexpr uint8_t kAvgReads = 16;
constexpr uint8_t kNoiseReads = 24;
constexpr uint32_t kSettleUs = 2000; // lets the pin recharge after a pull change

enum class Pull { NONE, UP, DOWN };

void setPull(gpio_num_t gpio, Pull pull) {
  switch (pull) {
  case Pull::NONE:
    gpio_pullup_dis(gpio);
    gpio_pulldown_dis(gpio);
    break;
  case Pull::UP:
    gpio_pulldown_dis(gpio);
    gpio_pullup_en(gpio);
    break;
  case Pull::DOWN:
    gpio_pullup_dis(gpio);
    gpio_pulldown_en(gpio);
    break;
  }
  delayMicroseconds(kSettleUs);
}

float readPinV(const ScanPin &p, uint8_t n) {
  uint32_t sum = 0;
  for (uint8_t i = 0; i < n; i++) sum += analogReadMilliVolts(p.arduinoPin);
  return (static_cast<float>(sum) / n) / 1000.0f;
}

struct PinResult {
  float v;     // no pull
  float vUp;   // internal pull-up on
  float vDown; // internal pull-down on
  float span;  // noise peak-to-peak, no pull
  bool inRange;
  bool stiff;
  bool quiet;
};

PinResult measure(const ScanPin &p) {
  PinResult r{};
  analogReadMilliVolts(p.arduinoPin); // attaches the ADC channel first

  setPull(p.gpio, Pull::NONE);
  r.v = readPinV(p, kAvgReads);

  float lo = 10.0f, hi = -10.0f;
  for (uint8_t i = 0; i < kNoiseReads; i++) {
    float s = analogReadMilliVolts(p.arduinoPin) / 1000.0f;
    lo = min(lo, s);
    hi = max(hi, s);
    delayMicroseconds(300);
  }
  r.span = hi - lo;

  setPull(p.gpio, Pull::UP);
  r.vUp = readPinV(p, kAvgReads);
  setPull(p.gpio, Pull::DOWN);
  r.vDown = readPinV(p, kAvgReads);
  setPull(p.gpio, Pull::NONE);

  r.inRange = r.v >= kPinMinV && r.v <= kPinMaxV;
  r.stiff = fabsf(r.vUp - r.v) <= kStiffMaxSwingV && fabsf(r.v - r.vDown) <= kStiffMaxSwingV;
  r.quiet = r.span <= kQuietMaxSpanV;
  return r;
}

void printFixed(float v, uint8_t width) {
  char buf[16];
  snprintf(buf, sizeof(buf), "%*.3f", width, v);
  Serial.print(buf);
}

void printPadded(const char *s, uint8_t width) {
  Serial.print(s);
  for (size_t n = strlen(s); n < width; n++) Serial.print(' ');
}

void runScan() {
  PinResult results[kPinCount];
  for (size_t i = 0; i < kPinCount; i++) results[i] = measure(kPins[i]);

  // The pull test only works if the core leaves the pulls alone while the
  // pin is in ADC mode. A floating pin always swings under a pull, so if
  // nothing swings at all, the pulls weren't applied and stiffness is
  // meaningless.
  bool pullTestWorks = false;
  for (size_t i = 0; i < kPinCount; i++) {
    if (results[i].vUp - results[i].vDown > 1.0f) pullTestWorks = true;
  }

  Serial.println();
  Serial.println(F("[find] pin  V(pin)  V(pull-up) V(pull-dn) noise  cell-if-divider  verdict"));
  Serial.println(F("[find] ---  ------  ---------- ---------- -----  ---------------  -------"));

  int best = -1;
  int candidates = 0;
  for (size_t i = 0; i < kPinCount; i++) {
    const PinResult &r = results[i];
    bool match = r.inRange && r.quiet && (r.stiff || !pullTestWorks);
    if (match) {
      candidates++;
      if (best < 0) best = static_cast<int>(i);
    }

    Serial.print(F("[find] "));
    printPadded(kPins[i].label, 4);
    printFixed(r.v, 6);
    printFixed(r.vUp, 11);
    printFixed(r.vDown, 11);
    printFixed(r.span, 6);
    Serial.print(F("  "));
    if (r.inRange) {
      printFixed(r.v * kDividerRatio, 6);
      Serial.print(F(" V        "));
    } else {
      Serial.print(F("      -          "));
    }

    if (match) {
      Serial.print(F("<-- BATTERY DIVIDER"));
    } else if (r.v > 2.9f && r.vDown > 2.0f) {
      Serial.print(F("held high (pull-up / 3V3)"));
    } else if (!r.stiff && pullTestWorks && r.vUp - r.vDown > 1.0f) {
      Serial.print(F("floating / unconnected"));
    } else if (r.v < 0.15f && r.stiff) {
      Serial.print(F("held low (GND / pulldown)"));
    } else if (!r.quiet) {
      Serial.print(F("noisy"));
    } else {
      Serial.print(F("-"));
    }
    if (kPins[i].note[0] != '\0') {
      Serial.print(F("  ["));
      Serial.print(kPins[i].note);
      Serial.print(']');
    }
    Serial.println();
  }

  Serial.println();
  if (!pullTestWorks) {
    Serial.println(F("[find] note: no pin moved under the internal pulls, so the stiffness test is off"));
    Serial.println(F("[find]       and the result rests on voltage + noise only. Confirm with WATCH."));
  }
  if (candidates == 1) {
    Serial.print(F("[find] RESULT: battery divider is on "));
    Serial.print(kPins[best].label);
    Serial.print(F(" (cell ~"));
    Serial.print(results[best].v * kDividerRatio, 2);
    Serial.println(F(" V before BATT_CAL_GAIN)."));
    Serial.print(F("[find]   config.h:  #define PIN_BATT_SENSE "));
    Serial.println(kPins[best].label);
    if (kPins[best].gpio == GPIO_NUM_17 || kPins[best].gpio == GPIO_NUM_18) {
      Serial.println(F("[find]   WARNING: that pin is on ADC2, which the ESP32-S3 can't read while the"));
      Serial.println(F("[find]   Wi-Fi AP is up. Move the divider to an ADC1 pin (A0-A7, D2-D7)."));
    }
  } else if (candidates == 0) {
    Serial.println(F("[find] RESULT: no pin looks like the divider. Check that the board is on the battery"));
    Serial.println(F("[find]   (USB alone reads ~0 V), that R11/R12 are fitted, and that the divider goes to a"));
    Serial.println(F("[find]   pin in the table (D10-D13 have no ADC). WATCH + unplugging the battery helps."));
  } else {
    Serial.print(F("[find] RESULT: "));
    Serial.print(candidates);
    Serial.println(F(" pins look like a divider. With USB connected, type WATCH, then unplug the"));
    Serial.println(F("[find]   battery: the pin that drops to ~0 V is the battery sense."));
  }
  Serial.println(F("[find] commands: SCAN, WATCH, HELP"));
}

// --- WATCH: live table, flags pins that move against the first frame -----

bool g_watching = false;
uint32_t g_lastWatchAt = 0;
float g_watchRef[kPinCount];
bool g_watchMoved[kPinCount];

void startWatch() {
  for (size_t i = 0; i < kPinCount; i++) {
    setPull(kPins[i].gpio, Pull::NONE);
    g_watchRef[i] = readPinV(kPins[i], kAvgReads);
    g_watchMoved[i] = false;
  }
  g_watching = true;
  g_lastWatchAt = 0;
  Serial.println(F("[find] WATCH on. Unplug/replug the battery (keep USB in). Pins marked * have moved"));
  Serial.println(F("[find]   by more than 0.5 V since WATCH started. Type WATCH again to stop."));
}

void watchTick() {
  uint32_t now = millis();
  if (now - g_lastWatchAt < 1000) return;
  g_lastWatchAt = now;

  Serial.print(F("[watch]"));
  for (size_t i = 0; i < kPinCount; i++) {
    float v = readPinV(kPins[i], kAvgReads);
    if (fabsf(v - g_watchRef[i]) > 0.5f) g_watchMoved[i] = true;
    Serial.print(' ');
    Serial.print(kPins[i].label);
    Serial.print(g_watchMoved[i] ? '*' : '=');
    Serial.print(v, 2);
  }
  Serial.println();
}

void printHelp() {
  Serial.println(F("[find] SCAN   scan every ADC pin for the battery divider"));
  Serial.println(F("[find] WATCH  toggle a live 1 Hz voltage table (unplug the battery to see which pin follows)"));
  Serial.println(F("[find] HELP   this list"));
}

String g_line;

void handleLine(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;
  if (cmd == "SCAN") {
    g_watching = false;
    runScan();
  } else if (cmd == "WATCH") {
    if (g_watching) {
      g_watching = false;
      Serial.println(F("[find] WATCH off."));
    } else {
      startWatch();
    }
  } else if (cmd == "HELP") {
    printHelp();
  } else {
    Serial.print(F("[find] unknown command: "));
    Serial.println(cmd);
    printHelp();
  }
}

} // namespace

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 4000) delay(10); // USB CDC: give the monitor time to attach
  delay(300);

  analogReadResolution(12);
  Serial.println(F("[find] battery-sense pin finder: scanning every ADC-capable pin"));
  runScan();
}

void loop() {
  while (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (g_line.length()) handleLine(g_line);
      g_line = "";
    } else if (g_line.length() < 32) {
      g_line += c;
    }
  }
  if (g_watching) watchTick();
}

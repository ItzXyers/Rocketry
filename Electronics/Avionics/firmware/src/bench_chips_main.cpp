// Standalone bench bring-up for every chip on the flight computer at once —
// BMP388 barometer + ADXL375 accelerometer (I2C), the internal-flash log, the
// buzzer and the battery sense. Interactive serial console.
//
// Reuses the real sensors.cpp / logger.cpp / buzzer.cpp / battery.cpp, so
// what passes here is the actual flight code path, not a throwaway probe.
// The 5V-Arduino equivalent of this tool is ../chip_test/chip_test.ino.
//
// Build/flash/monitor:
//   pio run -e chips_bench -t upload
//   pio device monitor          (115200 baud)
//
// This leaves the bench binary on the board. Re-flash the flight firmware
// (pio run -e nano_esp32 -t upload) and power-cycle before flying.
//
// Commands (case-insensitive, one per line):
//   SCAN                        I2C bus scan
//   ID                          probe BMP388 (0x76/0x77) + ADXL375 (0x53/0x1D) id regs
//   INIT                        bring up the Adafruit drivers via sensors_init()
//   SELFTEST                    run the flight sensors_selfTest()
//   READ                        print one fused sensor sample
//   STREAM                      toggle continuous sampling (~5 Hz)
//   PEEK <addr> <reg>           raw I2C register read  (hex: PEEK 76 00)
//   POKE <addr> <reg> <val>     raw I2C register write (hex) — no guard rails
//   FLASH                       mount internal flash, open a FLIGHTnnn.CSV, write a test record
//   LOGS                        list the FLIGHTnnn.CSV files in internal flash
//   FORMAT YES                  erase every log (also formats a brand-new board)
//   BUZZER PASS|FAIL|BEACON|ARM|ARMED|REJECT|OFF
//   BATT                        battery voltage + raw sense-pin reading (A0)
//   PINS                        print the pin map
//   HELP                        this list

#include "battery.h"
#include "buzzer.h"
#include "config.h"

#include "logger.h"
#include "sensors.h"

#include <Arduino.h>
#include <Wire.h>

namespace {

constexpr uint32_t BENCH_STREAM_INTERVAL_MS = 200; // ~5 Hz, readable on a console

bool g_streaming = false;
uint32_t g_lastStreamAt = 0;

// --- small output helpers -------------------------------------------------

void printHex8(uint8_t v) {
  Serial.print(F("0x"));
  if (v < 0x10) Serial.print('0');
  Serial.print(v, HEX);
}

// --- raw I2C, no driver object ------------------------------------------

bool i2cPing(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}

// Returns the register value 0..255, or -1 if the device did not respond.
int i2cReadReg(uint8_t addr, uint8_t reg) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission() != 0) return -1;
  if (Wire.requestFrom(static_cast<uint8_t>(addr), static_cast<uint8_t>(1)) != 1) return -1;
  return Wire.read();
}

bool i2cWriteReg(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

// --- command implementations -----------------------------------------

void cmdScan() {
  Serial.println(F("[bench] I2C scan:"));
  uint8_t n = 0;
  for (uint8_t a = 1; a < 127; a++) {
    if (i2cPing(a)) {
      Serial.print(F("[bench]   "));
      printHex8(a);
      Serial.println();
      n++;
    }
  }
  Serial.print(F("[bench] "));
  Serial.print(n);
  Serial.println(F(" device(s)"));
}

// Probe a chip at each of its two possible strap addresses and report the
// identity register. This is what settled the BMP388's 0x76 strap and is the
// first thing to run on any new/reworked board.
void probeChip(const __FlashStringHelper *name, const uint8_t *addrs, uint8_t count,
               uint8_t idReg, uint8_t idWant) {
  bool any = false;
  for (uint8_t i = 0; i < count; i++) {
    if (!i2cPing(addrs[i])) continue;
    any = true;
    int v = i2cReadReg(addrs[i], idReg);
    Serial.print(F("[bench] "));
    Serial.print(name);
    Serial.print(F(" at "));
    printHex8(addrs[i]);
    Serial.print(F("  id="));
    if (v < 0) {
      Serial.println(F("(no response)"));
      continue;
    }
    printHex8(static_cast<uint8_t>(v));
    Serial.print(F("  want "));
    printHex8(idWant);
    Serial.println(v == idWant ? F("  MATCH") : F("  mismatch"));
  }
  if (!any) {
    Serial.print(F("[bench] "));
    Serial.print(name);
    Serial.println(F("  not present at either address"));
  }
}

void cmdId() {
  static const uint8_t bmpAddrs[] = {0x76, 0x77};
  static const uint8_t adxlAddrs[] = {0x53, 0x1D};
  probeChip(F("BMP388 "), bmpAddrs, 2, 0x00, 0x50);  // CHIP_ID; BMP390 would be 0x60
  probeChip(F("ADXL375"), adxlAddrs, 2, 0x00, 0xE5); // DEVID
}

void printSample(const SensorSample &s) {
  Serial.print(F("[bench] t="));
  Serial.print(s.timestamp_ms);
  Serial.print(F("ms  baro(v="));
  Serial.print(s.baro_valid ? 1 : 0);
  Serial.print(F(") P="));
  Serial.print(s.pressure_pa, 1);
  Serial.print(F("Pa T="));
  Serial.print(s.temperature_c, 2);
  Serial.print(F("C alt="));
  Serial.print(s.altitude_agl_m, 2);
  Serial.print(F("m   accel(v="));
  Serial.print(s.accel_valid ? 1 : 0);
  Serial.print(F(") g=("));
  Serial.print(s.accel_x_g, 3);
  Serial.print(F(", "));
  Serial.print(s.accel_y_g, 3);
  Serial.print(F(", "));
  Serial.print(s.accel_z_g, 3);
  Serial.print(F(")  |mag|="));
  Serial.print(s.accel_mag_g, 3);
  Serial.println(F("g"));
}

void cmdFlash() {
  bool ok = logger_init(); // prints its own [logger] lines
  Serial.print(F("[bench] logger_init "));
  Serial.println(ok ? F("OK") : F("FAIL"));
  if (!ok) return;
  LogRecord r;                 // struct default-inits all fields to 0/false
  r.timestamp_ms = millis();
  logger_logEvent("benchtest", r); // writes + flushes immediately
  Serial.print(F("[bench] wrote one 'benchtest' record, flush took "));
  Serial.print(logger_maxFlushUs());
  Serial.println(F(" us. Run FLASH once per boot — each call opens (and leaks) another file; "
                   "DEL the bench files from the flight firmware's console afterwards."));
}

void cmdBuzzer(const String &arg) {
  if (arg == "PASS") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_PASS);
    Serial.println(F("[bench] buzzer: SELF_TEST_PASS (short double-beep, once)"));
  } else if (arg == "FAIL") {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_FAIL);
    Serial.println(F("[bench] buzzer: SELF_TEST_FAIL (fast continuous)"));
  } else if (arg == "BEACON") {
    buzzer_setPattern(BuzzerPattern::RECOVERY_BEACON);
    Serial.println(F("[bench] buzzer: RECOVERY_BEACON (slow chirp)"));
  } else if (arg == "ARM") {
    buzzer_setPattern(BuzzerPattern::ARM_CONFIRM);
    Serial.println(F("[bench] buzzer: ARM_CONFIRM (beep-beep-beeeep, then ARMED reminder)"));
  } else if (arg == "ARMED") {
    buzzer_setPattern(BuzzerPattern::ARMED_REMINDER);
    Serial.println(F("[bench] buzzer: ARMED_REMINDER (double chirp every ~4 s)"));
  } else if (arg == "REJECT") {
    buzzer_setPattern(BuzzerPattern::ARM_REJECTED);
    Serial.println(F("[bench] buzzer: ARM_REJECTED (five fast blips)"));
  } else if (arg == "OFF") {
    buzzer_setPattern(BuzzerPattern::OFF);
    Serial.println(F("[bench] buzzer: OFF"));
  } else {
    Serial.println(F("[bench] usage: BUZZER PASS|FAIL|BEACON|ARM|ARMED|REJECT|OFF"));
  }
}

void cmdBatt() {
  // Raw pin millivolts as well as the scaled value, so BATT_CAL_GAIN can be
  // set from a multimeter reading at the cell: gain = meter V / reported V.
  uint32_t pinMv = analogReadMilliVolts(PIN_BATT_SENSE);
  Serial.print(F("[bench] BATT sense (A0) pin = "));
  Serial.print(pinMv);
  Serial.print(F(" mV  -> cell = "));
  Serial.print(battery_voltage(), 3);
  Serial.print(F(" V filtered, ~"));
  Serial.print(battery_percent());
  Serial.print(F(" %"));
  if (!battery_valid()) Serial.print(F("  (NO READING: divider fitted? on battery, not USB-only?)"));
  else if (battery_low()) Serial.print(F("  LOW"));
  Serial.println();
}

void cmdPins() {
  Serial.println(F("[bench] pin map (Arduino label = ESP32-S3 GPIO):"));
  Serial.print(F("[bench]   I2C   SDA=A4("));   Serial.print(PIN_I2C_SDA);
  Serial.print(F(")  SCL=A5("));                Serial.print(PIN_I2C_SCL);   Serial.println(')');
  Serial.print(F("[bench]   BUZZER=D9("));      Serial.print(PIN_BUZZER);     Serial.println(')');
  Serial.print(F("[bench]   BATT_SENSE=A0("));  Serial.print(PIN_BATT_SENSE); Serial.println(')');

  Serial.print(F("[bench]   BMP388 addr (flight, pinned) = "));
  printHex8(BMP388_I2C_ADDR);
  Serial.println();
}

void cmdHelp() {
  Serial.println(F("[bench] commands:"));
  Serial.println(F("[bench]   SCAN                        I2C bus scan"));
  Serial.println(F("[bench]   ID                          BMP388/ADXL375 identity-register probe"));
  Serial.println(F("[bench]   INIT                        sensors_init()  (real flight driver bring-up)"));
  Serial.println(F("[bench]   SELFTEST                    sensors_selfTest()"));
  Serial.println(F("[bench]   READ                        one fused sensor sample"));
  Serial.println(F("[bench]   STREAM                      toggle continuous sampling (~5 Hz)"));
  Serial.println(F("[bench]   PEEK <addr> <reg>           raw I2C read  (hex, e.g. PEEK 76 00)"));
  Serial.println(F("[bench]   POKE <addr> <reg> <val>     raw I2C write (hex) — no guard rails"));
  Serial.println(F("[bench]   FLASH                       mount internal flash + write a test record"));
  Serial.println(F("[bench]   LOGS                        list flight logs in internal flash"));
  Serial.println(F("[bench]   FORMAT YES                  erase every log (formats a new board)"));
  Serial.println(F("[bench]   BUZZER PASS|FAIL|BEACON|ARM|ARMED|REJECT|OFF  play a buzzer pattern"));
  Serial.println(F("[bench]   BATT                        battery voltage (A0 divider)"));
  Serial.println(F("[bench]   PINS                        print the pin map"));

}

// --- command dispatch -------------------------------------------------

// Splits `line` into up to `maxTokens` space-delimited tokens. Returns count.
uint8_t tokenize(const String &line, String *out, uint8_t maxTokens) {
  uint8_t n = 0;
  int i = 0;
  const int len = line.length();
  while (i < len && n < maxTokens) {
    while (i < len && line[i] == ' ') i++;
    if (i >= len) break;
    int start = i;
    while (i < len && line[i] != ' ') i++;
    out[n++] = line.substring(start, i);
  }
  return n;
}

void handleCommand(String line) {
  line.trim();
  line.toUpperCase();
  if (line.length() == 0) return;

  String tok[4];
  uint8_t ntok = tokenize(line, tok, 4);
  const String &cmd = tok[0];

  if (cmd == "SCAN") {
    cmdScan();
  } else if (cmd == "ID") {
    cmdId();
  } else if (cmd == "INIT") {
    bool ok = sensors_init(); // prints nothing itself; report the result
    Serial.print(F("[bench] sensors_init() = "));
    Serial.println(ok ? F("OK (both chips up)") : F("FAIL (see SELFTEST / SCAN / ID)"));
  } else if (cmd == "SELFTEST") {
    bool ok = sensors_selfTest(); // prints its own [selftest] lines
    Serial.print(F("[bench] sensors_selfTest() = "));
    Serial.println(ok ? F("PASS") : F("FAIL"));
  } else if (cmd == "READ") {
    printSample(sensors_read());
  } else if (cmd == "STREAM") {
    g_streaming = !g_streaming;
    Serial.println(g_streaming ? F("[bench] streaming ON — send STREAM again to stop")
                               : F("[bench] streaming OFF"));
  } else if (cmd == "PEEK") {
    if (ntok < 3) {
      Serial.println(F("[bench] usage: PEEK <addr_hex> <reg_hex>"));
    } else {
      uint8_t addr = strtol(tok[1].c_str(), nullptr, 16);
      uint8_t reg = strtol(tok[2].c_str(), nullptr, 16);
      int v = i2cReadReg(addr, reg);
      Serial.print(F("[bench] PEEK "));
      printHex8(addr);
      Serial.print(F(" reg "));
      printHex8(reg);
      Serial.print(F(" = "));
      if (v < 0) {
        Serial.println(F("(no response)"));
      } else {
        printHex8(static_cast<uint8_t>(v));
        Serial.print(F("  0b"));
        for (int b = 7; b >= 0; b--) Serial.print((v >> b) & 1);
        Serial.println();
      }
    }
  } else if (cmd == "POKE") {
    if (ntok < 4) {
      Serial.println(F("[bench] usage: POKE <addr_hex> <reg_hex> <val_hex>"));
    } else {
      uint8_t addr = strtol(tok[1].c_str(), nullptr, 16);
      uint8_t reg = strtol(tok[2].c_str(), nullptr, 16);
      uint8_t val = strtol(tok[3].c_str(), nullptr, 16);
      bool ok = i2cWriteReg(addr, reg, val);
      Serial.print(F("[bench] POKE "));
      printHex8(addr);
      Serial.print(F(" reg "));
      printHex8(reg);
      Serial.print(F(" <- "));
      printHex8(val);
      Serial.println(ok ? F("  ack") : F("  no ack"));
    }
  } else if (cmd == "FLASH") {
    cmdFlash();
  } else if (cmd == "LOGS") {
    logger_list(Serial);
  } else if (cmd == "FORMAT") {
    if (ntok >= 2 && tok[1] == "YES") {
      bool ok = logger_format(); // re-opens a fresh FLIGHT001.CSV, like FLASH
      Serial.println(ok ? F("[bench] format OK") : F("[bench] format FAILED"));
    } else {
      Serial.println(F("[bench] FORMAT erases EVERY flight log. Send 'FORMAT YES' to confirm."));
    }
  } else if (cmd == "BUZZER") {
    cmdBuzzer(ntok >= 2 ? tok[1] : String());
  } else if (cmd == "BATT") {
    cmdBatt();
  } else if (cmd == "PINS") {
    cmdPins();
  } else if (cmd == "HELP" || cmd == "?") {
    cmdHelp();
  } else {
    Serial.print(F("[bench] unknown command: "));
    Serial.println(cmd);
    Serial.println(F("[bench] type HELP"));
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
  // Buzzer pin LOW first, before Serial — same ordering as main.cpp.
  buzzer_init();

  battery_init();

  Serial.begin(115200);
  delay(200);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL); // sensors_init() re-calls this harmlessly

  Serial.println(F("\n[bench] chip bring-up console ready"));
  cmdPins();
  cmdScan(); // auto-run every boot: the command that caught the 0x76 strap
  Serial.println(F("[bench] run INIT to bring up the drivers, then READ / STREAM. Type HELP."));
}

void loop() {
  pollSerialCommands();

  buzzer_update();
  battery_update();


  if (g_streaming && (millis() - g_lastStreamAt >= BENCH_STREAM_INTERVAL_MS)) {
    g_lastStreamAt = millis();
    printSample(sensors_read());
  }
}

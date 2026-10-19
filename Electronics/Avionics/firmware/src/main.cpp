// Flight computer firmware — Arduino Nano ESP32 (ABX00083), no-GPS variant.
// See ../../avionics_bay_schematic_phoenix40.html for hardware. A logging
// altimeter only: it fires nothing (Phoenix deploys on the motor ejection
// charge; the deploy channel was removed 2026-10-19).
//
// This file is thin orchestration only — no flight logic lives here.

#include "config.h"
#include "battery.h"

#include "buzzer.h"
#include "flight_state.h"
#include "logger.h"
#include "sensors.h"
#include "velocity_estimator.h"
#include "wireless.h"

#include <Arduino.h>
#include <WiFi.h>
#include "esp32-hal-bt.h"

namespace {

uint32_t g_lastSampleAt = 0;
uint32_t g_lastAccelAtUs = 0;
uint32_t g_lastFlushAt = 0;
uint32_t g_padSampleCount = 0;
SensorSample g_latest; // last tick's sample; fast ascent rows overwrite only its accel fields

// Internal flash only holds ~25 min of 50 Hz CSV, and the board logs from
// the moment the battery goes in. So: full rate in flight, and on the pad
// as soon as accel crosses the launch threshold (so the launch-confirm
// window is never decimated); every LOG_PAD_DECIMATION-th sample otherwise
// (pad, landed, self-test error).
bool shouldLogSample(const SensorSample &s) {
  switch (flight_state_current()) {
  case FlightState::BOOST:
  case FlightState::COAST:
  case FlightState::APOGEE:
  case FlightState::DESCENT:
    return true;
  default:
    break;
  }
  if (s.accel_valid && s.accel_mag_g >= LAUNCH_ACCEL_THRESHOLD_G) {
    return true;
  }
  return (g_padSampleCount++ % LOG_PAD_DECIMATION) == 0;
}

// Ascent is short and is where the interesting accel happens, so BOOST and
// COAST (and pad samples already over the launch threshold, so the
// launch-confirm window is covered before BOOST is confirmed) get extra
// accel-only rows every ASCENT_ACCEL_INTERVAL_US between the 50 Hz ticks.
// APOGEE/DESCENT stay at the tick rate -- descent is long and slow.
// These rows are log-only: flight_state and velocity_estimator still see
// exactly one sample per tick, since their per-sample constants assume 50 Hz.
bool fastAscentLogging(const SensorSample &s) {
  switch (flight_state_current()) {
  case FlightState::BOOST:
  case FlightState::COAST:
    return true;
  case FlightState::APOGEE:
  case FlightState::DESCENT:
    return false;
  default:
    return s.accel_valid && s.accel_mag_g >= LAUNCH_ACCEL_THRESHOLD_G;
  }
}

// Log management touches flash and can block for seconds -- ground only.
bool onGround() {
  switch (flight_state_current()) {
  case FlightState::BOOST:
  case FlightState::COAST:
  case FlightState::APOGEE:
  case FlightState::DESCENT:
    return false;
  default:
    return true;
  }
}

// Parses the "nnn" in "DUMP nnn" / "DEL nnn"; 0 if missing or out of range.
uint16_t parseLogNumber(const String &cmd, const char *prefix) {
  long n = cmd.substring(strlen(prefix)).toInt();
  return (n > 0 && n <= 999) ? static_cast<uint16_t>(n) : 0;
}

// Raw file bytes between BEGIN/END marker lines, so a terminal capture can
// be cut down to the CSV (or a script can grab what's between the markers).
void dumpLog(uint16_t n) {
  File f = logger_openForRead(n);
  if (!f) {
    Serial.println(F("[logger] no such log (see LOGS)"));
    return;
  }
  Serial.print(F("[logger] BEGIN FLIGHT"));
  if (n < 100) Serial.print('0');
  if (n < 10) Serial.print('0');
  Serial.print(n);
  Serial.print(F(".CSV "));
  Serial.println(static_cast<unsigned long>(f.size()));
  uint8_t buf[512];
  size_t got;
  while ((got = f.read(buf, sizeof(buf))) > 0) {
    Serial.write(buf, got);
  }
  f.close();
  Serial.println(F("[logger] END"));
}

LogRecord buildRoutineRecord(const SensorSample &s) {
  LogRecord r;
  r.timestamp_ms = s.timestamp_ms;
  r.state = static_cast<uint8_t>(flight_state_current());
  r.altitude_agl_m = s.altitude_agl_m;
  r.pressure_pa = s.pressure_pa;
  r.temperature_c = s.temperature_c;
  r.accel_x_g = s.accel_x_g;
  r.accel_y_g = s.accel_y_g;
  r.accel_z_g = s.accel_z_g;
  r.accel_mag_g = s.accel_mag_g;
  r.baro_valid = s.baro_valid;
  r.accel_valid = s.accel_valid;
  r.deploy_fired = false; // no deploy channel; column kept for CSV compatibility
  r.velocity_est_mps = velocity_estimator_velocityMps();
  r.altitude_est_m = velocity_estimator_altitudeM();
  r.batt_v = battery_valid() ? battery_voltage() : 0.0f;
  return r;
}

// Bench-only diagnostic/test commands over the USB serial console.
// Deliberately independent of flight state so the logger can be exercised
// on bare, partially-wired hardware.
void handleSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) {
    return;
  }

  if (cmd == "STATE") {
    Serial.print(F("[bench] flight_state = "));
    Serial.println(static_cast<uint8_t>(flight_state_current()));
    Serial.print(F("[bench] wifi AP = "));
    Serial.println(wireless_radioActive() ? F("up") : F("down"));
    Serial.print(F("[bench] log = FLIGHT"));
    Serial.print(logger_currentFileNumber());
    Serial.print(logger_isReady() ? (logger_isFull() ? F(" FULL") : F(" ok")) : F(" NOT READY"));
    Serial.print(F(", flash free "));
    Serial.print(logger_freeBytes() / 1024UL);
    Serial.print(F(" KB, worst flush "));
    Serial.print(logger_maxFlushUs());
    Serial.println(F(" us"));
    Serial.print(F("[bench] battery = "));
    if (battery_valid()) {
      Serial.print(battery_voltage(), 3);
      Serial.print(F(" V, ~"));
      Serial.print(battery_percent());
      Serial.println(battery_low() ? F(" % LOW") : F(" %"));
    } else {
      Serial.println(F("no reading"));
    }
    Serial.print(F("[bench] velocity_est_mps = "));
    Serial.print(velocity_estimator_velocityMps());
    Serial.print(F(" altitude_est_m = "));
    Serial.println(velocity_estimator_altitudeM());
  } else if (cmd == "FLUSH") {
    logger_flush();
    Serial.println(F("[bench] flushed"));
  } else if (cmd == "LOGS" || cmd.startsWith("DUMP") || cmd.startsWith("DEL") || cmd.startsWith("FORMAT")) {
    if (!onGround()) {
      Serial.println(F("[bench] log commands are refused in flight"));
    } else if (cmd == "LOGS") {
      logger_list(Serial);
    } else if (cmd.startsWith("DUMP")) {
      uint16_t n = parseLogNumber(cmd, "DUMP");
      if (n == 0) {
        Serial.println(F("[bench] usage: DUMP <n>   (n from LOGS, e.g. DUMP 3)"));
      } else {
        dumpLog(n);
      }
    } else if (cmd.startsWith("DEL")) {
      uint16_t n = parseLogNumber(cmd, "DEL");
      if (n == 0) {
        Serial.println(F("[bench] usage: DEL <n>"));
      } else {
        Serial.println(logger_delete(n) ? F("[bench] deleted")
                                        : F("[bench] delete failed (no such log, or it is this boot's file)"));
      }
    } else if (cmd == "FORMAT YES") {
      Serial.println(F("[bench] formatting internal flash -- every log is erased"));
      bool ok = logger_format();
      Serial.println(ok ? F("[bench] format OK -- power-cycle before flying (self-test reruns at boot)")
                        : F("[bench] format FAILED"));
    } else {
      Serial.println(F("[bench] FORMAT erases EVERY flight log. Send 'FORMAT YES' to confirm."));
    }
  } else {
    Serial.println(F("[bench] unknown command. Available: STATE, FLUSH, LOGS, DUMP n, DEL n, FORMAT YES"));
  }
}

void pollSerialCommands() {
  static String buf;
  while (Serial.available() > 0) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (buf.length() > 0) {
        handleSerialCommand(buf);
        buf = "";
      }
    } else {
      buf += c;
    }
  }
}

} // namespace

void setup() {
  // First, before Serial.begin(): drive the buzzer pin LOW so it can't chirp
  // during boot.
  buzzer_init();

  Serial.begin(115200);

  // The radio starts OFF as a safe default for the sensor/flash init window
  // below (brownout risk: the worst-case current transient is a flash
  // write + Wi-Fi burst). The first wireless_update() brings the
  // ground-support AP up, and it is force-disabled again either on a
  // successful wireless /arm or the instant real launch is confirmed
  // (flight_state.cpp's BOOST transition) -- see wireless.h.
  WiFi.mode(WIFI_OFF);
  btStop();

  battery_init(); // before flight_state_init() so the boot self-test record already carries batt_v
  if (battery_valid()) {
    Serial.print(F("[main] battery "));
    Serial.print(battery_voltage(), 2);
    Serial.print(F(" V (~"));
    Serial.print(battery_percent());
    Serial.println(battery_low() ? F(" %) -- LOW, charge before flight") : F(" %)"));
  } else {
    Serial.println(F("[main] battery: no reading (divider not fitted, or USB-only power)"));
  }

  sensors_init();
  flight_state_init(); // runs self-test, opens the log, plays pass/fail tone


  wireless_init(); // the AP itself comes up on the first wireless_update()
}

void loop() {
  uint32_t now = millis();

  if (now - g_lastSampleAt >= SENSOR_SAMPLE_INTERVAL_MS) {
    g_lastSampleAt = now;
    g_lastAccelAtUs = micros(); // fast rows re-phase to each tick
    SensorSample sample = sensors_read();
    g_latest = sample;
    velocity_estimator_update(sample); // telemetry-only fused estimate; feeds nothing back into flight_state's detectors
    flight_state_update(sample); // may log a transition
    if (shouldLogSample(sample)) {
      logger_log(buildRoutineRecord(sample));
    }
  } else if (fastAscentLogging(g_latest) &&
             micros() - g_lastAccelAtUs >= ASCENT_ACCEL_INTERVAL_US) {
    g_lastAccelAtUs = micros();
    g_latest.timestamp_ms = millis();
    sensors_readAccel(g_latest); // baro columns repeat the last tick's reading
    logger_log(buildRoutineRecord(g_latest));
  }

  if (now - g_lastFlushAt >= LOG_FLUSH_INTERVAL_MS) {
    g_lastFlushAt = now;
    logger_flush();
  }

  // Unconditional every iteration, regardless of sensor sample cadence —
  // these own their own millis()-based timing and must never be starved by
  // a blocking call elsewhere. No delay() exists anywhere in this loop.
  buzzer_update();
  battery_update();

  pollSerialCommands();
  wireless_update(); // services HTTP + AP power-up + any deferred
                      // radio shutdown; ordered after buzzer_update() so it
                      // can never starve it
}

// Flight computer firmware — Arduino Nano ESP32 (ABX00083), no-GPS variant.
// See ../../avionics_bom.md and ../../avionics_wiring.md for hardware, and
// ../../CO2 Deployment/*.md for the burn-wire deployment mechanism this
// firmware's deployment.* module drives.
//
// This file is thin orchestration only — no flight logic lives here.

#include "config.h"

#include "buzzer.h"
#include "deployment.h"
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
uint32_t g_lastFlushAt = 0;

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
  r.deploy_fired = deployment_hasFired();
  r.velocity_est_mps = velocity_estimator_velocityMps();
  r.altitude_est_m = velocity_estimator_altitudeM();
  return r;
}

// Bench-only diagnostic/test commands over the USB serial console.
// Deliberately independent of flight state so the deployment channel and
// logger can be exercised on bare, partially-wired hardware.
void handleSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) {
    return;
  }

  if (cmd == "ARM") {
    bool ok = deployment_bench_arm();
    Serial.println(ok ? F("[bench] armed - send FIRE within the arm window to fire")
                       : F("[bench] arm rejected (already fired this power cycle?)"));
  } else if (cmd == "FIRE") {
    Serial.print(F("[bench] attempting fire, configured on-time = "));
    Serial.print(DEPLOY_ON_TIME_MS);
    Serial.println(F(" ms"));
    bool ok = deployment_bench_fire();
    Serial.println(ok ? F("[bench] fire started")
                       : F("[bench] fire rejected (not armed / arm window expired / already fired)"));
  } else if (cmd == "STATE") {
    Serial.print(F("[bench] flight_state = "));
    Serial.println(static_cast<uint8_t>(flight_state_current()));
    Serial.print(F("[bench] arm_interlock (SW2) = "));
    Serial.println(wireless_armInterlockClosed() ? F("CLOSED") : F("OPEN"));
    Serial.print(F("[bench] velocity_est_mps = "));
    Serial.print(velocity_estimator_velocityMps());
    Serial.print(F(" altitude_est_m = "));
    Serial.println(velocity_estimator_altitudeM());
  } else if (cmd == "FLUSH") {
    logger_flush();
    Serial.println(F("[bench] flush requested (no-op if deployment is currently firing)"));
  } else {
    Serial.println(F("[bench] unknown command. Available: ARM, FIRE, STATE, FLUSH"));
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
  // Boot-safety-critical: the deployment gate must never be left
  // floating/undefined, even for the brief window before the rest of
  // setup() runs — this drives a striker into a pressurized CO2 cartridge,
  // not just a buzzer chirp. Must be the literal first call, before even
  // Serial.begin().
  deployment_init();
  buzzer_init();

  Serial.begin(115200);

  // The radio starts OFF as a safe default for the sensor/SD init window
  // below (same brownout-risk reasoning as before -- the BOM's worst-case
  // documented current transient is "SD write + WiFi burst"). wireless_init()
  // below brings the ground-support AP up only once SW2 (the arm-interlock
  // switch) is physically closed, and force-disables the radio again either
  // on a successful wireless /arm or the instant real launch is confirmed
  // (flight_state.cpp's BOOST transition) -- see wireless.h.
  WiFi.mode(WIFI_OFF);
  btStop();

  sensors_init();
  flight_state_init(); // runs self-test, opens the log, plays pass/fail tone

  if (deployment_hasFired()) {
    Serial.println(F("[main] WARNING: deploy latch already set at boot -- "
                      "board was NOT power-cycled since a previous firing. "
                      "Do not fly without a fresh power-cycle + reload."));
  }

  wireless_init(); // brings up the ground-support AP once SW2 is closed
}

void loop() {
  uint32_t now = millis();

  if (now - g_lastSampleAt >= SENSOR_SAMPLE_INTERVAL_MS) {
    g_lastSampleAt = now;
    SensorSample sample = sensors_read();
    velocity_estimator_update(sample); // telemetry-only fused estimate; feeds nothing back into flight_state's detectors
    flight_state_update(sample); // may itself fire deployment / log a transition
    logger_log(buildRoutineRecord(sample));
  }

  if (now - g_lastFlushAt >= LOG_FLUSH_INTERVAL_MS) {
    g_lastFlushAt = now;
    logger_flush(); // no-op (deferred) if the deployment coil is currently firing
  }

  // Unconditional every iteration, regardless of sensor sample cadence —
  // these own their own millis()-based timing and must never be starved by
  // a blocking call elsewhere. No delay() exists anywhere in this loop.
  deployment_update();
  buzzer_update();

  pollSerialCommands();
  wireless_update(); // services HTTP + SW2-follow AP power + any deferred
                      // radio shutdown; ordered after deployment_update()/
                      // buzzer_update() so it can never starve them
}

#include "flight_state.h"
#include "config.h"
#include "battery.h"

#include "buzzer.h"
#include "deployment.h"
#include "logger.h"
#include "sensors.h"
#include "velocity_estimator.h"
#include "wireless.h"

#include <Arduino.h>
#include <math.h>
#include <string.h>

namespace {

FlightState g_state = FlightState::INIT;
SensorSample g_lastSample;
bool g_selfTestPassed = false;

uint32_t g_launchTimestamp = 0;
bool g_aboveLaunchThreshold = false;
uint32_t g_launchAccelSince = 0;

bool g_altitudeFilterInit = false;
float g_altitudeFilteredM = 0.0f;
float g_altitudePeakM = 0.0f;
uint16_t g_apogeeConfirmCount = 0;

uint32_t g_deployDwellStart = 0;

bool g_landedStableActive = false;
float g_landedStableRefM = 0.0f;
uint32_t g_landedStableStart = 0;

LogRecord buildRecord() {
  LogRecord r;
  r.timestamp_ms = g_lastSample.timestamp_ms;
  r.state = static_cast<uint8_t>(g_state);
  r.altitude_agl_m = g_lastSample.altitude_agl_m;
  r.pressure_pa = g_lastSample.pressure_pa;
  r.temperature_c = g_lastSample.temperature_c;
  r.accel_x_g = g_lastSample.accel_x_g;
  r.accel_y_g = g_lastSample.accel_y_g;
  r.accel_z_g = g_lastSample.accel_z_g;
  r.accel_mag_g = g_lastSample.accel_mag_g;
  r.baro_valid = g_lastSample.baro_valid;
  r.accel_valid = g_lastSample.accel_valid;
  r.deploy_fired = deployment_hasFired();
  r.velocity_est_mps = velocity_estimator_velocityMps();
  r.altitude_est_m = velocity_estimator_altitudeM();
  r.batt_v = battery_valid() ? battery_voltage() : 0.0f;
  return r;
}

void logTransition(const char *tag) {
  LogRecord r = buildRecord();
  logger_logEvent(tag, r);
  Serial.print(F("[flight_state] -> "));
  Serial.println(tag);
}

void resetApogeeDetector() {
  g_altitudeFilterInit = false;
  g_apogeeConfirmCount = 0;
}

} // namespace

void flight_state_init() {
  g_state = FlightState::SELF_TEST;

  bool sensorsOk = sensors_selfTest();
  bool loggerOk = logger_init();
  g_selfTestPassed = sensorsOk && loggerOk;

  if (sensorsOk && loggerOk) {
    logTransition("SELFTEST_OK");
    buzzer_setPattern(BuzzerPattern::SELF_TEST_PASS);

    sensors_capturePadBaseline();
    velocity_estimator_reset();

    g_state = FlightState::IDLE_ARMED;
    g_aboveLaunchThreshold = false;
    logTransition("IDLE_ARMED");
  } else {
    buzzer_setPattern(BuzzerPattern::SELF_TEST_FAIL);
    g_state = FlightState::ERROR;
    logTransition("SELFTEST_FAIL");
  }
}

FlightState flight_state_update(const SensorSample &sample) {
  g_lastSample = sample;

  switch (g_state) {

  case FlightState::IDLE_ARMED: {
    bool aboveThreshold = sample.accel_valid && sample.accel_mag_g >= LAUNCH_ACCEL_THRESHOLD_G;
    if (!aboveThreshold) {
      g_aboveLaunchThreshold = false;
      break;
    }
    if (!g_aboveLaunchThreshold) {
      g_aboveLaunchThreshold = true;
      g_launchAccelSince = sample.timestamp_ms;
      break;
    }
    if (sample.timestamp_ms - g_launchAccelSince >= LAUNCH_ACCEL_CONFIRM_MS) {
      g_launchTimestamp = sample.timestamp_ms;
      g_state = FlightState::BOOST;
      logTransition("BOOST");

      // Force the wireless ground-support radio off the instant a real
      // launch is confirmed -- independent of the wireless-arm step
      // already having disabled it (e.g. operator rebooted after arming
      // and forgot to re-close SW2/re-disable before a real flight).
      // Placed here (confirmed BOOST), not on the first over-threshold
      // sample, so ordinary pad handling (mounting on the rail, connecting
      // the igniter) can't trip it -- the cost of waiting for
      // LAUNCH_ACCEL_CONFIRM_MS is negligible next to the alternative of
      // false-tripping on every bump. Recovery from here requires a power
      // cycle; SW2 has no effect once this lockout is set.
      wireless_requestShutdown(/*immediate=*/true);
    }
    break;
  }

  case FlightState::BOOST: {
    uint32_t sinceLaunch = sample.timestamp_ms - g_launchTimestamp;
    if (sinceLaunch < BOOST_MIN_TIME_MS) {
      break; // floor: reject a single-sample dropout right after liftoff
    }
    // Burnout heuristic: accel has fallen back toward ~1g (coasting under
    // gravity/drag alone). A missing accel reading here is also treated as
    // "can't confirm thrust is still on" and allowed through to COAST,
    // where the barometric apogee logic and backup timer take over.
    bool burnoutLike = !sample.accel_valid || sample.accel_mag_g <= BURNOUT_ACCEL_THRESHOLD_G;
    if (burnoutLike) {
      resetApogeeDetector();
      g_state = FlightState::COAST;
      logTransition("COAST");
    }
    break;
  }

  case FlightState::COAST: {
    uint32_t sinceLaunch = sample.timestamp_ms - g_launchTimestamp;

    // Backup ceiling — fires unconditionally regardless of barometer state
    // if the primary detector never confirms (sensor fault, flat/noisy
    // trace, unusual flight profile).
    if (sinceLaunch >= MAX_TIME_TO_APOGEE_MS) {
      g_state = FlightState::APOGEE_DEPLOY;
      logTransition("APOGEE_TIMEOUT");
      break;
    }

    // Floor: primary detector stays disarmed until this elapses, so
    // boost-phase baro noise/transients can't false-trigger deployment at
    // max-Q.
    if (sinceLaunch < MIN_COAST_TIME_MS) {
      break;
    }

    if (!sample.baro_valid) {
      break; // no data this sample; the backup ceiling above still applies
    }

    if (!g_altitudeFilterInit) {
      g_altitudeFilteredM = sample.altitude_agl_m;
      g_altitudePeakM = sample.altitude_agl_m;
      g_altitudeFilterInit = true;
      break;
    }

    g_altitudeFilteredM = ALTITUDE_FILTER_ALPHA * sample.altitude_agl_m +
                          (1.0f - ALTITUDE_FILTER_ALPHA) * g_altitudeFilteredM;

    if (g_altitudeFilteredM > g_altitudePeakM) {
      g_altitudePeakM = g_altitudeFilteredM;
      g_apogeeConfirmCount = 0;
    } else if (g_altitudePeakM - g_altitudeFilteredM >= APOGEE_DROP_THRESHOLD_M) {
      g_apogeeConfirmCount++;
      if (g_apogeeConfirmCount >= APOGEE_CONFIRM_SAMPLES) {
        g_state = FlightState::APOGEE_DEPLOY;
        logTransition("APOGEE_CONFIRMED");
      }
    } else {
      g_apogeeConfirmCount = 0;
    }
    break;
  }

  case FlightState::APOGEE_DEPLOY: {
    if (!deployment_hasFired()) {
      deployment_fire();
      g_deployDwellStart = sample.timestamp_ms;
      logTransition("DEPLOY_FIRE");
      break;
    }
    if (sample.timestamp_ms - g_deployDwellStart >= APOGEE_DEPLOY_DWELL_MS) {
      g_landedStableActive = false;
      g_state = FlightState::DESCENT;
      logTransition("DESCENT");
    }
    break;
  }

  case FlightState::DESCENT: {
    if (!sample.baro_valid) {
      break; // can't judge stability without altitude; wait for a valid sample
    }
    if (!g_landedStableActive || fabsf(sample.altitude_agl_m - g_landedStableRefM) >
                                      LANDED_ALT_STABLE_BAND_M) {
      g_landedStableActive = true;
      g_landedStableRefM = sample.altitude_agl_m;
      g_landedStableStart = sample.timestamp_ms;
      break;
    }
    if (sample.timestamp_ms - g_landedStableStart >= LANDED_STABLE_DURATION_MS) {
      g_state = FlightState::LANDED;
      buzzer_setPattern(BuzzerPattern::RECOVERY_BEACON);
      logTransition("LANDED");
    }
    break;
  }

  case FlightState::LANDED:
  case FlightState::ERROR:
  case FlightState::INIT:
  case FlightState::SELF_TEST:
  default:
    break;
  }

  return g_state;
}

FlightState flight_state_current() { return g_state; }

SensorSample flight_state_lastSample() { return g_lastSample; }

bool flight_state_bootSelfTestPassed() { return g_selfTestPassed; }

const char *flight_state_name(FlightState state) {
  switch (state) {
  case FlightState::INIT: return "INIT";
  case FlightState::SELF_TEST: return "SELF_TEST";
  case FlightState::IDLE_ARMED: return "IDLE_ARMED";
  case FlightState::BOOST: return "BOOST";
  case FlightState::COAST: return "COAST";
  case FlightState::APOGEE_DEPLOY: return "APOGEE_DEPLOY";
  case FlightState::DESCENT: return "DESCENT";
  case FlightState::LANDED: return "LANDED";
  case FlightState::ERROR: return "ERROR";
  default: return "UNKNOWN";
  }
}

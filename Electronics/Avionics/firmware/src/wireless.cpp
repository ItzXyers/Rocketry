#include "wireless.h"
#include "config.h"

#include "deployment.h"
#include "flight_state.h"
#include "logger.h"
#include "sensors.h"
#include "velocity_estimator.h"

#include <Arduino.h>
#include <WebServer.h>
#include <WiFi.h>
#include "esp32-hal-bt.h"

namespace {

// Two-level stringify so macro arguments (e.g. PIN_DEPLOY -> D6) are
// expanded before the # operator runs. D0-D13/A0-A7 are `static constexpr
// uint8_t`, not further macros, so this yields "D6" etc., not the numeric
// GPIO or the macro's own name.
#define WIRELESS_STR(x) #x
#define WIRELESS_XSTR(x) WIRELESS_STR(x)

WebServer g_server(WIFI_AP_HTTP_PORT);

bool g_radioActive = false;
bool g_lockedOut = false; // permanent for the rest of this power cycle once set

bool g_shutdownPending = false;
bool g_shutdownImmediate = false;
uint32_t g_shutdownRequestedAt = 0;

bool g_interlockReading = false; // debounced, accepted value
bool g_interlockRawLast = false;
uint32_t g_interlockChangedAt = 0;

bool g_lastArmSucceeded = false; // this session's wireless-arm outcome

char g_configJson[1536];

bool readInterlockRaw() { return digitalRead(PIN_ARM_INTERLOCK) == HIGH; }

void updateInterlockDebounce() {
  bool raw = readInterlockRaw();
  if (raw != g_interlockRawLast) {
    g_interlockRawLast = raw;
    g_interlockChangedAt = millis();
  }
  if (raw != g_interlockReading && millis() - g_interlockChangedAt >= WIFI_INTERLOCK_DEBOUNCE_MS) {
    g_interlockReading = raw;
  }
}

void bringApUp() {
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1), IPAddress(255, 255, 255, 0));
  WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD, WIFI_AP_CHANNEL, /*hidden=*/0, WIFI_AP_MAX_CONNECTIONS);
  g_server.begin();
  g_radioActive = true;
  Serial.println(F("[wireless] AP up"));
}

void bringRadioDown() {
  g_server.close();
  WiFi.mode(WIFI_OFF);
  btStop();
  g_radioActive = false;
  Serial.println(F("[wireless] radio disabled"));
}

LogRecord buildLogRecord(const SensorSample &s) {
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

// Built once in wireless_init() into g_configJson and served as-is
// thereafter -- every value here is a compile-time constant, so there's
// nothing to recompute per-request.
void buildConfigJson() {
  int n = snprintf(
      g_configJson, sizeof(g_configJson),
      "{"
      "\"firmware_version\":\"%s\","
      "\"build_timestamp\":\"%s %s\","
      "\"pin_i2c_sda\":\"%s\",\"pin_i2c_scl\":\"%s\","
      "\"pin_spi_sck\":\"%s\",\"pin_spi_miso\":\"%s\",\"pin_spi_mosi\":\"%s\",\"pin_sd_cs\":\"%s\","
      "\"pin_buzzer\":\"%s\",\"pin_deploy\":\"%s\",\"pin_arm_interlock\":\"%s\","
      "\"thr_launch_accel_g\":%.2f,"
      "\"thr_launch_accel_confirm_ms\":%lu,"
      "\"thr_boost_min_time_ms\":%lu,"
      "\"thr_burnout_accel_g\":%.2f,"
      "\"thr_min_coast_time_ms\":%lu,"
      "\"thr_max_time_to_apogee_ms\":%lu,"
      "\"thr_altitude_filter_alpha\":%.2f,"
      "\"thr_apogee_drop_m\":%.2f,"
      "\"thr_apogee_confirm_samples\":%u,"
      "\"thr_apogee_deploy_dwell_ms\":%lu,"
      "\"thr_landed_alt_band_m\":%.2f,"
      "\"thr_landed_stable_ms\":%lu,"
      "\"thr_deploy_on_time_ms\":%lu,"
      "\"thr_deploy_max_on_time_ms\":%lu,"
      "\"thr_sensor_sample_interval_ms\":%lu,"
      "\"thr_pad_baseline_samples\":%u,"
      "\"wifi_ssid\":\"%s\","
      "\"wifi_max_connections\":%u"
      "}",
      FIRMWARE_VERSION, __DATE__, __TIME__,
      WIRELESS_XSTR(PIN_I2C_SDA), WIRELESS_XSTR(PIN_I2C_SCL),
      WIRELESS_XSTR(PIN_SPI_SCK), WIRELESS_XSTR(PIN_SPI_MISO), WIRELESS_XSTR(PIN_SPI_MOSI), WIRELESS_XSTR(PIN_SD_CS),
      WIRELESS_XSTR(PIN_BUZZER), WIRELESS_XSTR(PIN_DEPLOY), WIRELESS_XSTR(PIN_ARM_INTERLOCK),
      static_cast<double>(LAUNCH_ACCEL_THRESHOLD_G),
      static_cast<unsigned long>(LAUNCH_ACCEL_CONFIRM_MS),
      static_cast<unsigned long>(BOOST_MIN_TIME_MS),
      static_cast<double>(BURNOUT_ACCEL_THRESHOLD_G),
      static_cast<unsigned long>(MIN_COAST_TIME_MS),
      static_cast<unsigned long>(MAX_TIME_TO_APOGEE_MS),
      static_cast<double>(ALTITUDE_FILTER_ALPHA),
      static_cast<double>(APOGEE_DROP_THRESHOLD_M),
      static_cast<unsigned>(APOGEE_CONFIRM_SAMPLES),
      static_cast<unsigned long>(APOGEE_DEPLOY_DWELL_MS),
      static_cast<double>(LANDED_ALT_STABLE_BAND_M),
      static_cast<unsigned long>(LANDED_STABLE_DURATION_MS),
      static_cast<unsigned long>(DEPLOY_ON_TIME_MS),
      static_cast<unsigned long>(DEPLOY_MAX_ON_TIME_MS),
      static_cast<unsigned long>(SENSOR_SAMPLE_INTERVAL_MS),
      static_cast<unsigned>(PAD_BASELINE_AVERAGE_SAMPLES),
      WIFI_AP_SSID,
      static_cast<unsigned>(WIFI_AP_MAX_CONNECTIONS));

  if (n < 0 || static_cast<size_t>(n) >= sizeof(g_configJson)) {
    // Truncated -- fail loudly rather than ever serve partial JSON.
    g_configJson[0] = '\0';
    Serial.println(F("[wireless] BUG: /config JSON truncated, buffer too small"));
  }
}

void handleIndex() {
  g_server.send(200, "application/json",
                 "{\"device\":\"flight-computer\",\"role\":\"ground-interface\","
                 "\"firmware_version\":\"" FIRMWARE_VERSION "\"}");
}

void handleStatus() {
  SensorSample s = flight_state_lastSample();
  FlightState state = flight_state_current();

  char buf[768];
  int n = snprintf(
      buf, sizeof(buf),
      "{"
      "\"uptime_ms\":%lu,"
      "\"free_heap_bytes\":%lu,"
      "\"flight_state\":\"%s\","
      "\"flight_state_code\":%u,"
      "\"boot_self_test_passed\":%s,"
      "\"wireless_armed\":%s,"
      "\"deploy_has_fired\":%s,"
      "\"arm_interlock_closed\":%s,"
      "\"logger_ready\":%s,"
      "\"sample_age_ms\":%lu,"
      "\"baro_valid\":%s,"
      "\"accel_valid\":%s,"
      "\"pressure_pa\":%.2f,"
      "\"temperature_c\":%.2f,"
      "\"altitude_agl_m\":%.2f,"
      "\"accel_x_g\":%.3f,"
      "\"accel_y_g\":%.3f,"
      "\"accel_z_g\":%.3f,"
      "\"accel_mag_g\":%.3f,"
      "\"pad_baseline_captured\":%s,"
      "\"pad_baseline_pressure_pa\":%.2f"
      "}",
      static_cast<unsigned long>(millis()),
      static_cast<unsigned long>(ESP.getFreeHeap()),
      flight_state_name(state),
      static_cast<unsigned>(state),
      flight_state_bootSelfTestPassed() ? "true" : "false",
      g_lastArmSucceeded ? "true" : "false",
      deployment_hasFired() ? "true" : "false",
      wireless_armInterlockClosed() ? "true" : "false",
      logger_isReady() ? "true" : "false",
      static_cast<unsigned long>(millis() - s.timestamp_ms),
      s.baro_valid ? "true" : "false",
      s.accel_valid ? "true" : "false",
      static_cast<double>(s.pressure_pa),
      static_cast<double>(s.temperature_c),
      static_cast<double>(s.altitude_agl_m),
      static_cast<double>(s.accel_x_g),
      static_cast<double>(s.accel_y_g),
      static_cast<double>(s.accel_z_g),
      static_cast<double>(s.accel_mag_g),
      sensors_baselineCaptured() ? "true" : "false",
      static_cast<double>(sensors_padBaselinePressurePa()));

  if (n < 0 || static_cast<size_t>(n) >= sizeof(buf)) {
    g_server.send(500, "application/json", "{\"ok\":false,\"reason\":\"status_json_truncated\"}");
    return;
  }
  g_server.send(200, "application/json", buf);
}

void handleConfig() {
  if (g_configJson[0] == '\0') {
    g_server.send(500, "application/json", "{\"ok\":false,\"reason\":\"config_json_unavailable\"}");
    return;
  }
  g_server.send(200, "application/json", g_configJson);
}

// Does NOT transition flight state -- IDLE_ARMED is a precondition here,
// not an outcome. Re-zeros the altimeter to the pad's current pressure
// ("last thing before you walk away") and then, deliberately, drops the
// radio. Preconditions checked in order, each with a distinct reason, no
// state change on any failure.
void handleArm() {
  if (!wireless_armInterlockClosed()) {
    g_server.send(409, "application/json", "{\"ok\":false,\"reason\":\"interlock_open\"}");
    return;
  }
  if (flight_state_current() != FlightState::IDLE_ARMED) {
    char buf[128];
    snprintf(buf, sizeof(buf),
             "{\"ok\":false,\"reason\":\"wrong_flight_state\",\"flight_state\":\"%s\"}",
             flight_state_name(flight_state_current()));
    g_server.send(409, "application/json", buf);
    return;
  }
  if (!sensors_selfTest()) {
    g_server.send(409, "application/json", "{\"ok\":false,\"reason\":\"self_test_failed\"}");
    return;
  }

  // Blocking, ~2-3.5s measured on bench (50x forced-mode BMP388 reads +
  // delay(20) each) -- see config.h. flight_state_update() gets no new
  // samples for this duration (launch detection is blind), which is
  // acceptable for a deliberate ground action: /arm is only reachable in
  // IDLE_ARMED, and deployment_fire() is only ever reachable via
  // APOGEE_DEPLOY, strictly after BOOST/COAST -- so this window can never
  // overlap the deploy safety-cutoff timing.
  sensors_capturePadBaseline();
  // Re-run alongside the baro re-zero above, adding roughly another
  // ~1.5-2s to this handler (same accepted-blocking reasoning as above):
  // without this, u_pad (the accel axis captured at power-on) would stay
  // stale if the board was powered on before final mounting on the rail,
  // silently invalidating the whole flight's velocity/altitude estimate --
  // see velocity_estimator.h. A wireless re-arm is exactly the deliberate
  // "about to fly, walking away now" moment where recapturing it is cheap
  // insurance against that.
  velocity_estimator_reset();
  // Fresh read against the baseline we just recaptured -- reusing
  // flight_state_lastSample() here would log a stale pre-recapture sample
  // (seconds old, altitude computed against the OLD baseline), which is
  // exactly the forensic record someone reads after a bad flight.
  SensorSample fresh = sensors_read();
  logger_logEvent("WIRELESS_ARM", buildLogRecord(fresh));
  g_lastArmSucceeded = true;

  char buf[192];
  snprintf(buf, sizeof(buf),
           "{\"ok\":true,\"pad_baseline_pressure_pa\":%.2f,\"flight_state\":\"%s\",\"radio_disabling\":true}",
           static_cast<double>(sensors_padBaselinePressurePa()), flight_state_name(flight_state_current()));
  g_server.send(200, "application/json", buf);

  wireless_requestShutdown(); // graced -- lets the response above actually reach the Pi first
}

void handleNotFound() {
  g_server.send(404, "application/json", "{\"ok\":false,\"reason\":\"not_found\"}");
}

} // namespace

void wireless_init() {
  // External R3 pulldown supplies the default (open = LOW) -- no
  // INPUT_PULLUP, see config.h's PIN_ARM_INTERLOCK comment for why.
  pinMode(PIN_ARM_INTERLOCK, INPUT);
  g_interlockRawLast = readInterlockRaw();
  g_interlockReading = g_interlockRawLast;
  g_interlockChangedAt = millis();

  buildConfigJson();

  g_server.on("/", HTTP_GET, handleIndex);
  g_server.on("/status", HTTP_GET, handleStatus);
  g_server.on("/config", HTTP_GET, handleConfig);
  g_server.on("/arm", HTTP_POST, handleArm);
  g_server.onNotFound(handleNotFound);

  // Deliberately do NOT bring the radio up here -- wireless_update()'s
  // SW2-follow logic (below) only does that once the interlock reads
  // closed, so SW2-open at boot behaves exactly like today's firmware
  // (radio off).
}

void wireless_update() {
  updateInterlockDebounce();

  if (g_lockedOut) {
    if (g_shutdownPending) {
      if (!g_shutdownImmediate && millis() - g_shutdownRequestedAt < WIFI_ARM_SHUTDOWN_GRACE_MS) {
        g_server.handleClient(); // let the in-flight response finish sending/tearing down
        return;
      }
      g_shutdownPending = false;
      if (g_radioActive) {
        bringRadioDown();
      }
    }
    return; // permanent no-op for the rest of this power cycle once the radio is down
  }

  if (g_interlockReading && !g_radioActive) {
    bringApUp();
  } else if (!g_interlockReading && g_radioActive) {
    bringRadioDown(); // deliberate operator action (opened SW2) -- no grace window needed
  }

  if (g_radioActive) {
    g_server.handleClient();
  }
}

bool wireless_armInterlockClosed() { return g_interlockReading; }

void wireless_requestShutdown(bool immediate) {
  g_lockedOut = true;
  g_shutdownPending = true;
  g_shutdownImmediate = immediate;
  g_shutdownRequestedAt = millis();
}

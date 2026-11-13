#include "wireless.h"
#include "config.h"
#include "battery.h"
#include "buzzer.h"
#include "phone_page_html.h"


#include "flight_state.h"
#include "logger.h"
#include "sensors.h"
#include "velocity_estimator.h"

#include <Arduino.h>
#include <StreamString.h>
#include <WebServer.h>
#include <WiFi.h>
#include "esp32-hal-bt.h"

namespace {

// Two-level stringify so macro arguments (e.g. PIN_BUZZER -> D9) are
// expanded before the # operator runs. D0-D13/A0-A7 are `static constexpr
// uint8_t`, not further macros, so this yields "D9" etc., not the numeric
// GPIO or the macro's own name.
#define WIRELESS_STR(x) #x
#define WIRELESS_XSTR(x) WIRELESS_STR(x)

WebServer g_server(WIFI_AP_HTTP_PORT);

bool g_radioActive = false;
bool g_lockedOut = false; // permanent for the rest of this power cycle once set

bool g_shutdownPending = false;
bool g_shutdownImmediate = false;
uint32_t g_shutdownRequestedAt = 0;

bool g_lastArmSucceeded = false; // this session's wireless-arm outcome

char g_configJson[1536];

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
  r.deploy_fired = false; // no deploy channel; column kept for CSV compatibility
  r.velocity_est_mps = velocity_estimator_velocityMps();
  r.altitude_est_m = velocity_estimator_altitudeM();
  r.batt_v = battery_valid() ? battery_voltage() : 0.0f;
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
      "\"pin_buzzer\":\"%s\",\"pin_batt_sense\":\"%s\","
      "\"log_storage\":\"internal_flash\",\"log_pad_decimation\":%u,\"log_min_free_bytes\":%lu,"
      "\"batt_divider_ratio\":%.3f,\"batt_cal_gain\":%.3f,\"batt_low_v\":%.2f,"
      "\"thr_launch_accel_g\":%.2f,"
      "\"thr_launch_accel_confirm_ms\":%lu,"
      "\"thr_boost_min_time_ms\":%lu,"
      "\"thr_burnout_accel_g\":%.2f,"
      "\"thr_min_coast_time_ms\":%lu,"
      "\"thr_max_time_to_apogee_ms\":%lu,"
      "\"thr_altitude_filter_alpha\":%.2f,"
      "\"thr_apogee_drop_m\":%.2f,"
      "\"thr_apogee_confirm_samples\":%u,"

      "\"thr_landed_alt_band_m\":%.2f,"
      "\"thr_landed_stable_ms\":%lu,"

      "\"thr_sensor_sample_interval_ms\":%lu,"
      "\"thr_ascent_accel_interval_us\":%lu,"
      "\"thr_pad_baseline_samples\":%u,"
      "\"wifi_ssid\":\"%s\","
      "\"wifi_max_connections\":%u"
      "}",
      FIRMWARE_VERSION, __DATE__, __TIME__,
      WIRELESS_XSTR(PIN_I2C_SDA), WIRELESS_XSTR(PIN_I2C_SCL),
      WIRELESS_XSTR(PIN_BUZZER), WIRELESS_XSTR(PIN_BATT_SENSE),
      static_cast<unsigned>(LOG_PAD_DECIMATION), static_cast<unsigned long>(LOG_MIN_FREE_BYTES),
      static_cast<double>(BATT_DIVIDER_RATIO), static_cast<double>(BATT_CAL_GAIN), static_cast<double>(BATT_LOW_V),
      static_cast<double>(LAUNCH_ACCEL_THRESHOLD_G),
      static_cast<unsigned long>(LAUNCH_ACCEL_CONFIRM_MS),
      static_cast<unsigned long>(BOOST_MIN_TIME_MS),
      static_cast<double>(BURNOUT_ACCEL_THRESHOLD_G),
      static_cast<unsigned long>(MIN_COAST_TIME_MS),
      static_cast<unsigned long>(MAX_TIME_TO_APOGEE_MS),
      static_cast<double>(ALTITUDE_FILTER_ALPHA),
      static_cast<double>(APOGEE_DROP_THRESHOLD_M),
      static_cast<unsigned>(APOGEE_CONFIRM_SAMPLES),

      static_cast<double>(LANDED_ALT_STABLE_BAND_M),
      static_cast<unsigned long>(LANDED_STABLE_DURATION_MS),

      static_cast<unsigned long>(SENSOR_SAMPLE_INTERVAL_MS),
      static_cast<unsigned long>(ASCENT_ACCEL_INTERVAL_US),
      static_cast<unsigned>(PAD_BASELINE_AVERAGE_SAMPLES),
      WIFI_AP_SSID,
      static_cast<unsigned>(WIFI_AP_MAX_CONNECTIONS));

  if (n < 0 || static_cast<size_t>(n) >= sizeof(g_configJson)) {
    // Truncated -- fail loudly rather than ever serve partial JSON.
    g_configJson[0] = '\0';
    Serial.println(F("[wireless] BUG: /config JSON truncated, buffer too small"));
  }
}

// The phone control page (flight_computer_phone_v1.html, embedded by
// tools/embed_phone_page.sh): join the AP, open http://192.168.4.1/.
void handleIndex() { g_server.send(200, "text/html", PHONE_PAGE_HTML); }

void handleStatus() {
  SensorSample s = flight_state_lastSample();
  FlightState state = flight_state_current();

  char buf[1024];
  int n = snprintf(
      buf, sizeof(buf),
      "{"
      "\"uptime_ms\":%lu,"
      "\"free_heap_bytes\":%lu,"
      "\"flight_state\":\"%s\","
      "\"flight_state_code\":%u,"
      "\"boot_self_test_passed\":%s,"
      "\"wireless_armed\":%s,"

      "\"logger_ready\":%s,"
      "\"logger_full\":%s,"
      "\"log_file_number\":%u,"
      "\"log_free_bytes\":%lu,"
      "\"log_max_flush_us\":%lu,"
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
      "\"pad_baseline_pressure_pa\":%.2f,"
      "\"batt_valid\":%s,"
      "\"batt_voltage_v\":%.3f,"
      "\"batt_percent\":%u,"
      "\"batt_low\":%s"
      "}",
      static_cast<unsigned long>(millis()),
      static_cast<unsigned long>(ESP.getFreeHeap()),
      flight_state_name(state),
      static_cast<unsigned>(state),
      flight_state_bootSelfTestPassed() ? "true" : "false",
      g_lastArmSucceeded ? "true" : "false",

      logger_isReady() ? "true" : "false",
      logger_isFull() ? "true" : "false",
      static_cast<unsigned>(logger_currentFileNumber()),
      static_cast<unsigned long>(logger_freeBytes()),
      static_cast<unsigned long>(logger_maxFlushUs()),
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
      static_cast<double>(sensors_padBaselinePressurePa()),
      battery_valid() ? "true" : "false",
      static_cast<double>(battery_voltage()),
      static_cast<unsigned>(battery_percent()),
      battery_low() ? "true" : "false");

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
  if (flight_state_current() != FlightState::IDLE_ARMED) {
    char buf[128];
    snprintf(buf, sizeof(buf),
             "{\"ok\":false,\"reason\":\"wrong_flight_state\",\"flight_state\":\"%s\"}",
             flight_state_name(flight_state_current()));
    g_server.send(409, "application/json", buf);
    return;
  }
  if (!sensors_selfTest()) {
    // Only this refusal beeps: wrong_flight_state means ERROR (fail tone
    // already looping) or post-launch (beacon), and neither may be overridden.
    buzzer_setPattern(BuzzerPattern::ARM_FAIL);
    g_server.send(409, "application/json", "{\"ok\":false,\"reason\":\"self_test_failed\"}");
    return;
  }

  // Blocking, ~2-3.5s measured on bench (50x forced-mode BMP388 reads +
  // delay(20) each) -- see config.h. flight_state_update() gets no new
  // samples for this duration (launch detection is blind), which is
  // acceptable for a deliberate ground action: /arm is only reachable in
  // IDLE_ARMED, i.e. on the pad.
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
  // After the blocking recaptures above: the pattern is stepped from loop(),
  // so starting it earlier would hold the first beep on for ~4-5 s.
  buzzer_setPattern(BuzzerPattern::ARM_OK);

  char buf[192];
  snprintf(buf, sizeof(buf),
           "{\"ok\":true,\"pad_baseline_pressure_pa\":%.2f,\"flight_state\":\"%s\",\"radio_disabling\":true}",
           static_cast<double>(sensors_padBaselinePressurePa()), flight_state_name(flight_state_current()));
  g_server.send(200, "application/json", buf);

  wireless_requestShutdown(); // graced -- lets the response above actually reach the Pi first
}

// Plain-text listing, same lines as the serial LOGS command.
void handleLogs() {
  StreamString body;
  logger_list(body);
  g_server.send(200, "text/plain", body);
}

// GET /log?n=7 -> FLIGHT007.CSV as a download. Blocks loop() for the whole
// transfer (seconds for a big file), so launch detection is blind meanwhile
// -- fine for a ground action, and the radio is latched off from BOOST on
// anyway, so this is never reachable in flight. After landing, power-cycle
// and download from the fresh boot.
void handleLog() {
  long n = g_server.hasArg("n") ? g_server.arg("n").toInt() : 0;
  File f = (n > 0 && n <= 999) ? logger_openForRead(static_cast<uint16_t>(n)) : File();
  if (!f) {
    g_server.send(404, "application/json", "{\"ok\":false,\"reason\":\"no_such_log\"}");
    return;
  }
  char disposition[64];
  snprintf(disposition, sizeof(disposition), "attachment; filename=\"FLIGHT%03ld.CSV\"", n);
  g_server.sendHeader("Content-Disposition", disposition);
  g_server.streamFile(f, "text/csv");
  f.close();
}

// Log deletion over Wi-Fi. Belt and braces: the AP is already latched off
// from BOOST on, but refuse in any in-flight state anyway (flash erases
// stall the CPU). ERROR is allowed on purpose -- a too-full flash fails the
// boot self-test, and this is how you free space without a USB cable.
// Freeing space does NOT re-run the self-test: power-cycle afterwards.
bool logEditAllowed() {
  switch (flight_state_current()) {
  case FlightState::BOOST:
  case FlightState::COAST:
  case FlightState::APOGEE:
  case FlightState::DESCENT:
    g_server.send(409, "application/json", "{\"ok\":false,\"reason\":\"in_flight\"}");
    return false;
  default:
    return true;
  }
}

void sendLogEditOk() {
  char buf[160];
  snprintf(buf, sizeof(buf),
           "{\"ok\":true,\"log_free_bytes\":%lu,\"log_total_bytes\":%lu,\"power_cycle_needed\":%s}",
           static_cast<unsigned long>(logger_freeBytes()),
           static_cast<unsigned long>(logger_totalBytes()),
           flight_state_current() == FlightState::ERROR ? "true" : "false");
  g_server.send(200, "application/json", buf);
}

// POST /delete?n=7 -> removes FLIGHT007.CSV. Refuses this boot's open file.
void handleDelete() {
  if (!logEditAllowed()) {
    return;
  }
  long n = g_server.hasArg("n") ? g_server.arg("n").toInt() : 0;
  if (n <= 0 || n > 999) {
    g_server.send(400, "application/json", "{\"ok\":false,\"reason\":\"bad_log_number\"}");
    return;
  }
  if (static_cast<uint16_t>(n) == logger_currentFileNumber()) {
    g_server.send(409, "application/json", "{\"ok\":false,\"reason\":\"is_this_boots_file\"}");
    return;
  }
  if (!logger_delete(static_cast<uint16_t>(n))) {
    g_server.send(404, "application/json", "{\"ok\":false,\"reason\":\"no_such_log\"}");
    return;
  }
  logger_logEvent("LOG_DELETED", buildLogRecord(flight_state_lastSample()));
  sendLogEditOk();
}

// POST /format?confirm=YES -> erases EVERY log (same as serial FORMAT YES)
// and starts a fresh FLIGHT001.CSV for this boot.
void handleFormat() {
  if (!logEditAllowed()) {
    return;
  }
  if (!g_server.hasArg("confirm") || g_server.arg("confirm") != "YES") {
    g_server.send(400, "application/json", "{\"ok\":false,\"reason\":\"confirm_YES_required\"}");
    return;
  }
  if (!logger_format()) {
    g_server.send(500, "application/json", "{\"ok\":false,\"reason\":\"format_failed\"}");
    return;
  }
  sendLogEditOk();
}

void handleNotFound() {
  g_server.send(404, "application/json", "{\"ok\":false,\"reason\":\"not_found\"}");
}

} // namespace

void wireless_init() {
  buildConfigJson();

  // Access-Control-Allow-Origin: * on every response, so the standalone
  // phone page (Electronics/Avionics/flight_computer_phone_v1.html, opened
  // as a local file = a different origin) can read the replies. The AP is
  // WPA2 and only exists on the pad; there is nothing else on this network.
  g_server.enableCORS(true);

  g_server.on("/", HTTP_GET, handleIndex);
  g_server.on("/status", HTTP_GET, handleStatus);
  g_server.on("/config", HTTP_GET, handleConfig);
  g_server.on("/arm", HTTP_POST, handleArm);
  g_server.on("/logs", HTTP_GET, handleLogs);
  g_server.on("/log", HTTP_GET, handleLog);
  g_server.on("/delete", HTTP_POST, handleDelete);
  g_server.on("/format", HTTP_POST, handleFormat);
  g_server.onNotFound(handleNotFound);

  // The radio comes up on the first wireless_update(), i.e. only after
  // setup() has finished the sensor/flash init window with the radio off.
}

void wireless_update() {
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

  if (!g_radioActive) {
    bringApUp();
  }

  if (g_radioActive) {
    g_server.handleClient();
  }
}

bool wireless_radioActive() { return g_radioActive; }

void wireless_requestShutdown(bool immediate) {
  g_lockedOut = true;
  g_shutdownPending = true;
  g_shutdownImmediate = immediate;
  g_shutdownRequestedAt = millis();
}

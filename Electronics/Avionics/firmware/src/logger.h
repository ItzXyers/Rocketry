#pragma once

#include <stdint.h>

// `state` is a plain uint8_t (cast from FlightState) rather than the enum
// itself, so this header doesn't need to depend on flight_state.h.
struct LogRecord {
  uint32_t timestamp_ms = 0;
  uint8_t state = 0;
  float altitude_agl_m = 0.0f;
  float pressure_pa = 0.0f;
  float temperature_c = 0.0f;
  float accel_x_g = 0.0f;
  float accel_y_g = 0.0f;
  float accel_z_g = 0.0f;
  float accel_mag_g = 0.0f;
  bool baro_valid = false;
  bool accel_valid = false;
  bool deploy_fired = false;
  float velocity_est_mps = 0.0f; // Kalman-fused vertical velocity, up +, telemetry only — see velocity_estimator.h
  float altitude_est_m = 0.0f;   // Kalman-fused altitude AGL, same frame as altitude_agl_m, telemetry only
  float batt_v = 0.0f;           // filtered cell voltage, 0 when no battery reading -- see battery.h
  char event[16] = {0}; // short tag, empty for routine (non-event) samples
};

// Mounts the SD card, scans the root for existing FLIGHTnnn.CSV files,
// opens the next unused number (so every boot/power-cycle gets its own
// file — nothing is ever overwritten), and writes the CSV header row.
// Returns false on any failure (card absent, mount failure, file open
// failure); the caller treats that as a hard self-test failure.
bool logger_init();

// Appends a record to a fixed-size RAM ring buffer — does not touch SD
// directly. If the buffer is full, flushes first, so no sample is silently
// dropped in normal operation.
void logger_log(const LogRecord &record);

// Tags the record with a short event string and writes it via logger_log(),
// then flushes immediately — for discrete events (state transitions, a
// deploy fire, the self-test result) that must survive a brownout/reset
// even if the periodic flush hasn't run yet.
void logger_logEvent(const char *eventTag, const LogRecord &record);

// Writes any buffered records to the open file. Called from logger_log()
// when the buffer fills and from main.cpp on LOG_FLUSH_INTERVAL_MS. Must
// NEVER be called while the deployment on-time window is active — SD-write
// current and burn-wire current must not stack.
void logger_flush();

// True once logger_init() has succeeded and the log file is open.
bool logger_isReady();

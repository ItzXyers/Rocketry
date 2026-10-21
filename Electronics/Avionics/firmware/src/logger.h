#pragma once

#include <FS.h>
#include <Print.h>
#include <stdint.h>

// Flight log on the Nano ESP32's internal flash: the board's partition table
// (app3M_fat9M_fact512k_16MB) has a ~9.4 MB FAT partition labelled "ffat".
// There is no removable card, so logs are pulled off over USB serial
// (LOGS / DUMP n in main.cpp) or Wi-Fi (GET /logs, /log?n=, see wireless.h).
//
// A normal `pio run -t upload` leaves the ffat partition alone. `pio run -t
// erase`, or any change to the partition table, wipes it -- pull logs first.

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
  bool deploy_fired = false;     // always false: no deploy channel since 2026-10-19. Column kept so old and new CSVs share one layout
  float velocity_est_mps = 0.0f; // Kalman-fused vertical velocity, up +, telemetry only — see velocity_estimator.h
  float altitude_est_m = 0.0f;   // Kalman-fused altitude AGL, same frame as altitude_agl_m, telemetry only
  float batt_v = 0.0f;           // filtered cell voltage, 0 when no battery reading -- see battery.h
  char event[16] = {0}; // short tag, empty for routine (non-event) samples
};

// Mounts the ffat partition WITHOUT formatting and nothing else -- no new
// file, so LOGS / downloads work without creating an empty log. Idempotent;
// logger_init() calls it. For bench tools that only read the logs.
bool logger_mount();

// Mounts the ffat partition WITHOUT formatting (a mount glitch must never
// silently wipe earlier flights), checks at least LOG_MIN_FREE_BYTES are
// free, opens the next unused /FLIGHTnnn.CSV (every boot gets its own file,
// nothing is ever overwritten) and writes the CSV header row. Returns false
// on any failure; the caller treats that as a hard self-test failure. A
// brand-new board's partition is unformatted: run the serial FORMAT command
// once, then power-cycle.
bool logger_init();

// Appends a record to a fixed-size RAM ring buffer — does not touch flash
// directly. If the buffer is full, flushes first, so no sample is silently
// dropped in normal operation.
void logger_log(const LogRecord &record);

// Tags the record with a short event string and writes it via logger_log(),
// then flushes immediately — for discrete events (state transitions, the
// self-test result) that must survive a brownout/reset
// even if the periodic flush hasn't run yet. Exception: while the ascent
// hold is on (logger_setHold), the event stays in RAM like everything else.
void logger_logEvent(const char *eventTag, const LogRecord &record);

// Writes the oldest <= LOG_BUFFER_RECORDS buffered records to the open file
// and syncs it. Called from logger_log() when LOG_BUFFER_RECORDS are waiting
// and from main.cpp on LOG_FLUSH_INTERVAL_MS. No-op while the ascent hold is
// on. Internal-flash writes stall the CPU (sector erases); the worst stall
// seen so far is reported by logger_maxFlushUs() -- check it on the bench.
void logger_flush();

// Ascent hold: while on, nothing is written to flash (no stalls, so no gaps
// in the 200 Hz ascent rows) and records accumulate in the PSRAM buffer
// (LOG_HOLD_RECORDS). When it goes off, the backlog drains one chunk per
// logged sample. Only if the hold buffer fills does a flush happen anyway.
// TRADE-OFF (user-approved 2026-10-19): a reset/brownout while holding loses
// everything since the hold started -- the whole ascent. Without PSRAM the
// buffer is LOG_BUFFER_RECORDS and holding just means flushing when full.
void logger_setHold(bool hold);

// True once logger_init() has succeeded and the log file is open.
bool logger_isReady();

// True once a write came back short (partition full). Logging stops for
// the rest of the power cycle rather than retrying every flush.
bool logger_isFull();

// Number nnn of the FLIGHTnnn.CSV this boot is writing, 0 if none.
uint16_t logger_currentFileNumber();

uint32_t logger_freeBytes();  // 0 if not mounted
uint32_t logger_totalBytes(); // 0 if not mounted
uint32_t logger_maxFlushUs(); // longest logger_flush() so far this boot

// Ground-only log management. None of these may be used in flight -- the
// callers (main.cpp serial console, wireless.cpp HTTP) are only reachable
// before BOOST or after landing.

// Prints "FLIGHTnnn.CSV <bytes>" per log file, then free/total bytes.
void logger_list(Print &out);

// Opens /FLIGHTnnn.CSV for reading (flushing first if it is this boot's
// file). Returns an invalid File if it doesn't exist.
fs::File logger_openForRead(uint16_t n);

// Deletes /FLIGHTnnn.CSV. Refuses this boot's open file.
bool logger_delete(uint16_t n);

// Wipes the whole partition (every flight log) and opens a fresh
// FLIGHT001.CSV. Also the way to format a brand-new board.
bool logger_format();

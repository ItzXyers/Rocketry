#include "logger.h"
#include "config.h"

#include "deployment.h"

#include <Arduino.h>
#include <SD.h>
#include <SPI.h>
#include <string.h>

namespace {

File g_file;
bool g_ready = false;

LogRecord g_buffer[LOG_BUFFER_RECORDS];
uint16_t g_bufferCount = 0;

void writeHeader() {
  g_file.println(F("timestamp_ms,state,altitude_agl_m,pressure_pa,temperature_c,"
                    "accel_x_g,accel_y_g,accel_z_g,accel_mag_g,"
                    "baro_valid,accel_valid,deploy_fired,"
                    "velocity_est_mps,altitude_est_m,batt_v,event"));
}

void writeRecord(const LogRecord &r) {
  g_file.print(r.timestamp_ms);
  g_file.print(',');
  g_file.print(r.state);
  g_file.print(',');
  g_file.print(r.altitude_agl_m, 2);
  g_file.print(',');
  g_file.print(r.pressure_pa, 1);
  g_file.print(',');
  g_file.print(r.temperature_c, 2);
  g_file.print(',');
  g_file.print(r.accel_x_g, 3);
  g_file.print(',');
  g_file.print(r.accel_y_g, 3);
  g_file.print(',');
  g_file.print(r.accel_z_g, 3);
  g_file.print(',');
  g_file.print(r.accel_mag_g, 3);
  g_file.print(',');
  g_file.print(r.baro_valid ? 1 : 0);
  g_file.print(',');
  g_file.print(r.accel_valid ? 1 : 0);
  g_file.print(',');
  g_file.print(r.deploy_fired ? 1 : 0);
  g_file.print(',');
  g_file.print(r.velocity_est_mps, 3);
  g_file.print(',');
  g_file.print(r.altitude_est_m, 2);
  g_file.print(',');
  g_file.print(r.batt_v, 3);
  g_file.print(',');
  g_file.println(r.event);
}

// FLIGHT001.CSV, FLIGHT002.CSV, ... — next-unused-number scheme, so every
// boot/power-cycle gets its own file regardless of what's already on the
// card.
bool openNextFlightFile() {
  char path[24];
  for (uint16_t n = 1; n <= 999; n++) {
    snprintf(path, sizeof(path), "/FLIGHT%03u.CSV", n);
    if (!SD.exists(path)) {
      g_file = SD.open(path, FILE_WRITE);
      return static_cast<bool>(g_file);
    }
  }
  return false; // FLIGHT001..FLIGHT999 all taken — vanishingly unlikely
}

} // namespace

bool logger_init() {
  SPI.begin(PIN_SPI_SCK, PIN_SPI_MISO, PIN_SPI_MOSI, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS, SPI)) {
    Serial.println(F("[logger] SD.begin failed"));
    return false;
  }

  if (!openNextFlightFile()) {
    Serial.println(F("[logger] could not open a FLIGHTnnn.CSV file"));
    return false;
  }

  writeHeader();
  g_file.flush();
  g_bufferCount = 0;
  g_ready = true;

  Serial.println(F("[logger] ready"));
  return true;
}

void logger_log(const LogRecord &record) {
  if (!g_ready) {
    return;
  }
  if (g_bufferCount >= LOG_BUFFER_RECORDS) {
    logger_flush(); // no-op (deferred) if the deployment coil is currently firing
    if (g_bufferCount >= LOG_BUFFER_RECORDS) {
      // Still full — the flush above was deferred rather than skipped by
      // choice. Drop this sample rather than overflow the buffer. This can
      // only happen during the ~1-few-second deployment on-time window;
      // the backlog drains as soon as firing ends (next flush attempt).
      return;
    }
  }
  g_buffer[g_bufferCount++] = record;
}

void logger_logEvent(const char *eventTag, const LogRecord &record) {
  LogRecord tagged = record;
  strncpy(tagged.event, eventTag, sizeof(tagged.event) - 1);
  tagged.event[sizeof(tagged.event) - 1] = '\0';
  logger_log(tagged);
  logger_flush();
}

void logger_flush() {
  if (!g_ready || g_bufferCount == 0) {
    return;
  }
  if (deployment_isFiring()) {
    // Hard invariant, enforced at this single choke point rather than
    // trusted at every call site: SD-write current must never stack with
    // burn-wire current. Deferred, not dropped — the next flush attempt
    // (periodic call from main.cpp, or the next buffer-full/event flush)
    // picks up everything still buffered once firing ends.
    return;
  }
  for (uint16_t i = 0; i < g_bufferCount; i++) {
    writeRecord(g_buffer[i]);
  }
  g_file.flush();
  g_bufferCount = 0;
}

bool logger_isReady() { return g_ready; }

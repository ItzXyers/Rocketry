#include "logger.h"
#include "config.h"

#include <Arduino.h>
#include <FFat.h>
#include <new>
#include <stdio.h>
#include <string.h>

namespace {

File g_file;
bool g_mounted = false;
bool g_ready = false;
bool g_full = false;
uint16_t g_fileNumber = 0;
uint32_t g_maxFlushUs = 0;

// FIFO ring. g_buffer points at the PSRAM hold buffer (LOG_HOLD_RECORDS)
// once logger_init() has allocated it, else at the internal-RAM fallback.
LogRecord g_fallbackBuffer[LOG_BUFFER_RECORDS];
LogRecord *g_buffer = g_fallbackBuffer;
uint16_t g_capacity = LOG_BUFFER_RECORDS;
uint16_t g_head = 0; // oldest buffered record
uint16_t g_bufferCount = 0;
bool g_hold = false;
bool g_holdOverflowed = false;

bool writeRecord(const LogRecord &r);

void allocateHoldBuffer() {
  if (g_buffer != g_fallbackBuffer) {
    return; // already allocated (logger_format() re-runs logger_init())
  }
  void *p = ps_malloc(sizeof(LogRecord) * LOG_HOLD_RECORDS);
  if (p == nullptr) {
    Serial.println(F("[logger] WARNING: no PSRAM -- ascent hold disabled, "
                      "flash flushes will leave gaps in the 200 Hz ascent data"));
    return;
  }
  g_buffer = static_cast<LogRecord *>(p);
  for (uint16_t i = 0; i < LOG_HOLD_RECORDS; i++) {
    new (&g_buffer[i]) LogRecord();
  }
  g_capacity = LOG_HOLD_RECORDS;
}

// Writes the oldest <= LOG_BUFFER_RECORDS records and syncs, ignoring the
// hold. Chunked so the post-apogee backlog drains as a series of short
// stalls interleaved with descent samples, not one multi-second one.
void writeChunk() {
  if (!g_ready || g_full || g_bufferCount == 0) {
    return;
  }

  uint32_t startUs = micros();
  uint16_t n = g_bufferCount < LOG_BUFFER_RECORDS ? g_bufferCount : LOG_BUFFER_RECORDS;
  for (uint16_t i = 0; i < n; i++) {
    if (!writeRecord(g_buffer[g_head])) {
      g_full = true;
      Serial.println(F("[logger] flash write failed (partition full?) -- logging stopped"));
      break;
    }
    g_head = (g_head + 1) % g_capacity;
    g_bufferCount--;
  }
  g_file.flush(); // fflush + fsync: what's written survives a brownout/reset
  uint32_t tookUs = micros() - startUs;
  if (tookUs > g_maxFlushUs) {
    g_maxFlushUs = tookUs;
  }
}

// Ground-only: everything buffered, hold or not.
void drainAll() {
  while (g_ready && !g_full && g_bufferCount > 0) {
    writeChunk();
  }
}

void flightPath(char *path, size_t size, uint16_t n) {
  snprintf(path, size, "/FLIGHT%03u.CSV", n);
}

// Parses "FLIGHTnnn.CSV" (with or without a leading '/'); 0 if not a log.
uint16_t parseFlightNumber(const char *name) {
  if (name[0] == '/') name++;
  unsigned n = 0;
  char tail[8] = {0};
  if (sscanf(name, "FLIGHT%3u.%7s", &n, tail) != 2 || strcmp(tail, "CSV") != 0) {
    return 0;
  }
  return static_cast<uint16_t>(n);
}

void writeHeader() {
  g_file.println(F("timestamp_ms,state,altitude_agl_m,pressure_pa,temperature_c,"
                    "accel_x_g,accel_y_g,accel_z_g,accel_mag_g,"
                    "baro_valid,accel_valid,deploy_fired,"
                    "velocity_est_mps,altitude_est_m,batt_v,event"));
}

// One write() per row rather than ~30 print() calls -- fewer trips into the
// VFS layer, and a short write (partition full) is detected in one place.
bool writeRecord(const LogRecord &r) {
  char line[192];
  int n = snprintf(line, sizeof(line),
                   "%lu,%u,%.2f,%.1f,%.2f,%.3f,%.3f,%.3f,%.3f,%u,%u,%u,%.3f,%.2f,%.3f,%s\n",
                   static_cast<unsigned long>(r.timestamp_ms),
                   static_cast<unsigned>(r.state),
                   static_cast<double>(r.altitude_agl_m),
                   static_cast<double>(r.pressure_pa),
                   static_cast<double>(r.temperature_c),
                   static_cast<double>(r.accel_x_g),
                   static_cast<double>(r.accel_y_g),
                   static_cast<double>(r.accel_z_g),
                   static_cast<double>(r.accel_mag_g),
                   r.baro_valid ? 1u : 0u,
                   r.accel_valid ? 1u : 0u,
                   r.deploy_fired ? 1u : 0u,
                   static_cast<double>(r.velocity_est_mps),
                   static_cast<double>(r.altitude_est_m),
                   static_cast<double>(r.batt_v),
                   r.event);
  if (n < 0) {
    return true; // formatting error, not a storage error -- skip the row
  }
  size_t len = static_cast<size_t>(n);
  if (len >= sizeof(line)) {
    // Truncated (e.g. a diverged float printed in full) -- keep the newline
    // so the next row doesn't run into this one.
    len = sizeof(line) - 1;
    line[len - 1] = '\n';
  }
  return g_file.write(reinterpret_cast<const uint8_t *>(line), len) == len;
}

// FLIGHT001.CSV, FLIGHT002.CSV, ... — next-unused-number scheme, so every
// boot/power-cycle gets its own file regardless of what's already in flash.
bool openNextFlightFile() {
  char path[24];
  for (uint16_t n = 1; n <= 999; n++) {
    flightPath(path, sizeof(path), n);
    if (!FFat.exists(path)) {
      g_file = FFat.open(path, FILE_WRITE);
      if (!g_file) {
        return false;
      }
      g_fileNumber = n;
      return true;
    }
  }
  return false; // FLIGHT001..FLIGHT999 all taken — DEL some or FORMAT
}

} // namespace

bool logger_mount() {
  if (!g_mounted) {
    // formatOnFail = false: never wipe earlier flights because of one bad mount.
    if (!FFat.begin(false)) {
      Serial.println(F("[logger] internal flash (ffat) mount failed -- "
                        "new board? send FORMAT YES on the serial console, then power-cycle"));
      return false;
    }
    g_mounted = true;
  }
  return true;
}

bool logger_init() {
  g_ready = false;
  g_full = false;
  g_head = 0;
  g_bufferCount = 0;
  g_hold = false;
  g_holdOverflowed = false;
  g_fileNumber = 0;

  allocateHoldBuffer();
  if (!logger_mount()) {
    return false;
  }

  uint32_t freeBytes = logger_freeBytes();
  Serial.print(F("[logger] flash free "));
  Serial.print(freeBytes / 1024UL);
  Serial.print(F(" / "));
  Serial.print(logger_totalBytes() / 1024UL);
  Serial.println(F(" KB"));
  if (freeBytes < LOG_MIN_FREE_BYTES) {
    Serial.println(F("[logger] not enough free flash for a flight -- "
                      "pull the old logs (LOGS / DUMP n), then DEL n or FORMAT YES"));
    return false;
  }

  if (!openNextFlightFile()) {
    Serial.println(F("[logger] could not open a FLIGHTnnn.CSV file"));
    return false;
  }

  writeHeader();
  g_file.flush();
  g_ready = true;

  Serial.print(F("[logger] ready, writing FLIGHT"));
  if (g_fileNumber < 100) Serial.print('0');
  if (g_fileNumber < 10) Serial.print('0');
  Serial.print(g_fileNumber);
  Serial.print(F(".CSV, ascent hold "));
  Serial.print(g_capacity);
  Serial.println(F(" records"));
  return true;
}

void logger_log(const LogRecord &record) {
  if (!g_ready || g_full) {
    return;
  }
  // Not holding: flush a chunk whenever LOG_BUFFER_RECORDS are waiting (so
  // a post-apogee backlog drains one chunk per logged sample). Holding:
  // only when the whole hold buffer is full -- a gap, but nothing dropped.
  uint16_t limit = g_hold ? g_capacity : LOG_BUFFER_RECORDS;
  if (g_bufferCount >= limit) {
    if (g_hold && !g_holdOverflowed) {
      g_holdOverflowed = true;
      Serial.println(F("[logger] ascent hold buffer full -- flushing in flight"));
    }
    writeChunk();
    if (g_full) {
      return; // the flush hit a full partition; logging has stopped
    }
  }
  g_buffer[(g_head + g_bufferCount) % g_capacity] = record;
  g_bufferCount++;
}

void logger_setHold(bool hold) { g_hold = hold; }

void logger_logEvent(const char *eventTag, const LogRecord &record) {
  LogRecord tagged = record;
  strncpy(tagged.event, eventTag, sizeof(tagged.event) - 1);
  tagged.event[sizeof(tagged.event) - 1] = '\0';
  logger_log(tagged);
  logger_flush();
}

void logger_flush() {
  if (g_hold) {
    return; // ascent: no flash stalls, see logger_setHold()
  }
  writeChunk();
}

bool logger_isReady() { return g_ready; }

bool logger_isFull() { return g_full; }

uint16_t logger_currentFileNumber() { return g_fileNumber; }

uint32_t logger_freeBytes() { return g_mounted ? static_cast<uint32_t>(FFat.freeBytes()) : 0; }

uint32_t logger_totalBytes() { return g_mounted ? static_cast<uint32_t>(FFat.totalBytes()) : 0; }

uint32_t logger_maxFlushUs() { return g_maxFlushUs; }

void logger_list(Print &out) {
  if (!g_mounted) {
    out.println(F("[logger] flash not mounted"));
    return;
  }
  drainAll(); // so this boot's file shows its real size
  File root = FFat.open("/");
  uint16_t count = 0;
  for (File f = root.openNextFile(); f; f = root.openNextFile()) {
    if (f.isDirectory() || parseFlightNumber(f.name()) == 0) {
      continue;
    }
    out.print(F("[logger] "));
    out.print(f.name()[0] == '/' ? f.name() + 1 : f.name());
    out.print(' ');
    out.print(static_cast<unsigned long>(f.size()));
    if (parseFlightNumber(f.name()) == g_fileNumber) {
      out.print(F("  (this boot)"));
    }
    out.println();
    count++;
  }
  out.print(F("[logger] "));
  out.print(count);
  out.print(F(" log(s), "));
  out.print(logger_freeBytes() / 1024UL);
  out.print(F(" / "));
  out.print(logger_totalBytes() / 1024UL);
  out.println(F(" KB free"));
}

void logger_listJson(Print &out) {
  out.print(F("{\"logs\":["));
  if (g_mounted) {
    drainAll(); // so this boot's file shows its real size
    File root = FFat.open("/");
    bool first = true;
    for (File f = root.openNextFile(); f; f = root.openNextFile()) {
      uint16_t n = f.isDirectory() ? 0 : parseFlightNumber(f.name());
      if (n == 0) {
        continue;
      }
      out.print(first ? F("{\"n\":") : F(",{\"n\":"));
      first = false;
      out.print(n);
      out.print(F(",\"name\":\""));
      out.print(f.name()[0] == '/' ? f.name() + 1 : f.name());
      out.print(F("\",\"bytes\":"));
      out.print(static_cast<unsigned long>(f.size()));
      out.print(F(",\"current\":"));
      out.print(n == g_fileNumber ? F("true}") : F("false}"));
    }
  }
  out.print(F("],\"mounted\":"));
  out.print(g_mounted ? F("true") : F("false"));
  out.print(F(",\"free_bytes\":"));
  out.print(logger_freeBytes());
  out.print(F(",\"total_bytes\":"));
  out.print(logger_totalBytes());
  out.print(F(",\"current\":"));
  out.print(g_fileNumber);
  out.print('}');
}

fs::File logger_openForRead(uint16_t n) {
  if (!g_mounted || n == 0) {
    return File();
  }
  if (n == g_fileNumber) {
    drainAll();
  }
  char path[24];
  flightPath(path, sizeof(path), n);
  if (!FFat.exists(path)) {
    return File();
  }
  return FFat.open(path, FILE_READ);
}

bool logger_delete(uint16_t n) {
  if (!g_mounted || n == 0 || (g_ready && n == g_fileNumber)) {
    return false;
  }
  char path[24];
  flightPath(path, sizeof(path), n);
  return FFat.remove(path);
}

bool logger_format() {
  if (g_ready) {
    g_file.close();
  }
  g_ready = false;
  if (g_mounted) {
    FFat.end();
    g_mounted = false;
  }
  if (!FFat.format(FFAT_WIPE_QUICK)) {
    Serial.println(F("[logger] FFat.format failed"));
    return false;
  }
  return logger_init();
}

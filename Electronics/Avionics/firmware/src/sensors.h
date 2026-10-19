#pragma once

#include <stdint.h>

// A single fused reading from both sensors, timestamped together. Altitude
// is always AGL relative to the pad baseline captured by
// sensors_capturePadBaseline() — never absolute/sea-level — since every
// downstream threshold (apogee drop, landed band) depends on that.
struct SensorSample {
  uint32_t timestamp_ms = 0;
  float pressure_pa = 0.0f;
  float temperature_c = 0.0f;
  float altitude_agl_m = 0.0f;
  float accel_x_g = 0.0f;
  float accel_y_g = 0.0f;
  float accel_z_g = 0.0f;
  float accel_mag_g = 0.0f;
  bool baro_valid = false;
  bool accel_valid = false;
};

// Starts Wire and both sensor drivers. Returns true only if both parts
// responded. Does not block on repeated retries — a false return here is a
// hard init failure, not a transient one.
bool sensors_init();

// Takes one reading from each sensor and prints a diagnostic summary to
// Serial. Called once at boot, before the flight state machine allows
// arming. Independent of sensors_read() so self-test output is always
// visible even if the caller never touches the returned SensorSample.
bool sensors_selfTest();

// Averages PAD_BASELINE_AVERAGE_SAMPLES barometer readings and stores the
// result as the zero-altitude reference. Blocking (short delay between
// samples) — this is a one-time calibration step on IDLE_ARMED entry, not
// part of the flight loop, so blocking here is fine.
void sensors_capturePadBaseline();

// Single non-blocking read of both sensors. Safe to call every loop()
// iteration. If a sensor read fails, the corresponding *_valid flag is
// false and that sample's fields for it are left at their last-set values
// (zero-initialized on the very first failed read).
SensorSample sensors_read();

// Accel-only read into an existing sample: updates the accel_* fields and
// accel_valid, leaves timestamp and every baro field untouched. For the
// fast ascent log rows between sensors_read() ticks (see main.cpp), where a
// baro read would block on its conversion. Returns accel_valid.
bool sensors_readAccel(SensorSample &s);

// The pad pressure reference set by the most recent
// sensors_capturePadBaseline() call; 0 before the first capture.
float sensors_padBaselinePressurePa();

// True once sensors_capturePadBaseline() has captured at least one valid
// reading.
bool sensors_baselineCaptured();

#include "velocity_estimator.h"
#include "config.h"
#include "kalman_filter.h"

#include <Arduino.h>
#include <math.h>
#include <Adafruit_Sensor.h> // SENSORS_GRAVITY_STANDARD, already a lib_dep via sensors.cpp's chain

namespace {

KalmanState1D g_kf;
float g_padUx = 0.0f, g_padUy = 0.0f, g_padUz = 1.0f, g_padMagG = 1.0f;
bool g_calValid = false;
bool g_initialized = false;
uint32_t g_lastUpdateMs = 0;

} // namespace

void velocity_estimator_reset() {
  double sumAx = 0, sumAy = 0, sumAz = 0, sumAlt = 0;
  uint16_t gotAccel = 0, gotBaro = 0;

  for (uint16_t i = 0; i < PAD_BASELINE_AVERAGE_SAMPLES; i++) {
    SensorSample s = sensors_read();
    if (s.accel_valid) {
      sumAx += s.accel_x_g;
      sumAy += s.accel_y_g;
      sumAz += s.accel_z_g;
      gotAccel++;
    }
    if (s.baro_valid) {
      sumAlt += s.altitude_agl_m;
      gotBaro++;
    }
    delay(20); // one-time blocking arm-time calibration, mirrors sensors_capturePadBaseline()
  }

  float ux = 0.0f, uy = 0.0f, uz = 1.0f, mag = 1.0f;
  bool calValid = false;
  if (gotAccel > 0) {
    float gx = static_cast<float>(sumAx / gotAccel);
    float gy = static_cast<float>(sumAy / gotAccel);
    float gz = static_cast<float>(sumAz / gotAccel);
    float m = sqrtf(gx * gx + gy * gy + gz * gz);
    if (m > 0.01f) { // guard divide-by-zero on garbage/degenerate data
      ux = gx / m;
      uy = gy / m;
      uz = gz / m;
      mag = m;
      calValid = (m >= PAD_CAL_MAG_MIN_G && m <= PAD_CAL_MAG_MAX_G);
    }
  }
  g_padUx = ux;
  g_padUy = uy;
  g_padUz = uz;
  g_padMagG = mag;
  g_calValid = calValid;

  float initialAltitude = (gotBaro > 0) ? static_cast<float>(sumAlt / gotBaro) : 0.0f;
  g_kf = kalman1d_init(initialAltitude, 0.0f, KALMAN_INITIAL_ALTITUDE_VAR_M2,
                        KALMAN_INITIAL_VELOCITY_VAR_M2S2);
  g_lastUpdateMs = millis();
  g_initialized = true;

  Serial.print(F("[velocity_estimator] pad accel cal: u=("));
  Serial.print(g_padUx, 4);
  Serial.print(F(", "));
  Serial.print(g_padUy, 4);
  Serial.print(F(", "));
  Serial.print(g_padUz, 4);
  Serial.print(F(") |g_pad|="));
  Serial.print(g_padMagG, 4);
  Serial.println(calValid ? F(" (OK)")
                          : F(" (SUSPECT -- check mounting/stationarity; using best-effort/fallback vector)"));
}

void velocity_estimator_update(const SensorSample &sample) {
  if (!g_initialized) return;
  if (!sample.baro_valid && !sample.accel_valid) return; // total dropout: hold, let dt accumulate

  float dt = (sample.timestamp_ms - g_lastUpdateMs) / 1000.0f;
  // timestamp_ms is uint32_t, so an out-of-order sample wraps to a huge
  // positive dt rather than going negative -- that's caught by the
  // KALMAN_MAX_DT_S re-seed below, not here. This only guards a genuine
  // duplicate (dt == 0).
  if (dt <= 0.0f) return;

  if (dt > KALMAN_MAX_DT_S) {
    if (!sample.baro_valid) return; // can't re-seed altitude without a fresh baro fix
    g_kf = kalman1d_init(sample.altitude_agl_m, 0.0f, KALMAN_INITIAL_ALTITUDE_VAR_M2,
                          KALMAN_REGAP_VELOCITY_VAR_M2S2);
    g_lastUpdateMs = sample.timestamp_ms;
    Serial.print(F("[velocity_estimator] re-seeded after a "));
    Serial.print(dt, 2);
    Serial.println(F(" s gap -- velocity estimate will take a few seconds to reconverge"));
    return;
  }

  float accelAxial_mps2 = 0.0f;
  float sigmaA = ACCEL_NOISE_FALLBACK_STD_MPS2;
  if (sample.accel_valid) {
    float aAxialG = sample.accel_x_g * g_padUx + sample.accel_y_g * g_padUy +
                     sample.accel_z_g * g_padUz;
    accelAxial_mps2 = (aAxialG - g_padMagG) * SENSORS_GRAVITY_STANDARD;
    sigmaA = ACCEL_NOISE_STD_MPS2;
  }

  g_kf = kalman1d_predict(g_kf, dt, accelAxial_mps2, sigmaA);
  if (sample.baro_valid) {
    g_kf = kalman1d_update(g_kf, sample.altitude_agl_m, BARO_ALT_VARIANCE_M2);
  }
  g_lastUpdateMs = sample.timestamp_ms;
}

float velocity_estimator_velocityMps() { return g_kf.velocity_mps; }
float velocity_estimator_altitudeM() { return g_kf.altitude_m; }
bool velocity_estimator_calibrationValid() { return g_calValid; }

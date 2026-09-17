#pragma once

// Pure, Arduino-independent 2-state (altitude, velocity) scalar Kalman
// filter core -- no Arduino.h, no millis(), no globals. SI units:
// meters, meters/second, meters/second^2, seconds.
struct KalmanState1D {
  float altitude_m = 0.0f;
  float velocity_mps = 0.0f;
  float p00 = 0.0f; // Var(altitude)
  float p01 = 0.0f; // Cov(altitude, velocity) == p10
  float p11 = 0.0f; // Var(velocity)
};

KalmanState1D kalman1d_init(float altitude_m, float velocity_mps,
                             float initialAltitudeVar_m2,
                             float initialVelocityVar_m2s2);

// dtS must be > 0; returns `s` unchanged if dtS <= 0 (defensive guard --
// caller is responsible for re-seeding instead of calling this with a
// pathologically large dtS, see velocity_estimator.cpp).
KalmanState1D kalman1d_predict(const KalmanState1D &s, float dtS,
                                float accelAxial_mps2, float accelNoiseStdMps2);

KalmanState1D kalman1d_update(const KalmanState1D &s,
                               float measuredAltitude_m, float measurementVar_m2);

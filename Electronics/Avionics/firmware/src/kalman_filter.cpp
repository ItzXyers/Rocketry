#include "kalman_filter.h"

KalmanState1D kalman1d_init(float altitude_m, float velocity_mps,
                             float initialAltitudeVar_m2, float initialVelocityVar_m2s2) {
  KalmanState1D s;
  s.altitude_m = altitude_m;
  s.velocity_mps = velocity_mps;
  s.p00 = initialAltitudeVar_m2;
  s.p01 = 0.0f;
  s.p11 = initialVelocityVar_m2s2;
  return s;
}

KalmanState1D kalman1d_predict(const KalmanState1D &s, float dtS,
                                float accelAxial_mps2, float accelNoiseStdMps2) {
  if (dtS <= 0.0f) return s;
  KalmanState1D out;
  out.altitude_m = s.altitude_m + s.velocity_mps * dtS + 0.5f * accelAxial_mps2 * dtS * dtS;
  out.velocity_mps = s.velocity_mps + accelAxial_mps2 * dtS;

  // P = F P F^T, F = [[1,dt],[0,1]]
  float fp00 = s.p00 + dtS * s.p01;
  float fp01 = s.p01 + dtS * s.p11;
  float p00 = fp00 + dtS * fp01;
  float p01 = fp01;
  float p11 = s.p11;

  float b0 = 0.5f * dtS * dtS, b1 = dtS;
  float qVar = accelNoiseStdMps2 * accelNoiseStdMps2;
  out.p00 = p00 + qVar * b0 * b0;
  out.p01 = p01 + qVar * b0 * b1;
  out.p11 = p11 + qVar * b1 * b1;
  return out;
}

KalmanState1D kalman1d_update(const KalmanState1D &s,
                               float measuredAltitude_m, float measurementVar_m2) {
  float innovation = measuredAltitude_m - s.altitude_m;
  float sInnov = s.p00 + measurementVar_m2;
  if (sInnov <= 0.0f) return s;
  float k0 = s.p00 / sInnov;
  float k1 = s.p01 / sInnov;

  KalmanState1D out;
  out.altitude_m = s.altitude_m + k0 * innovation;
  out.velocity_mps = s.velocity_mps + k1 * innovation;
  out.p00 = (1.0f - k0) * s.p00;
  out.p01 = (1.0f - k0) * s.p01;
  out.p11 = s.p11 - k1 * s.p01;
  return out;
}

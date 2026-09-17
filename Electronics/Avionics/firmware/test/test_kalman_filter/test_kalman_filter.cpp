#include <unity.h>
#include <math.h>

#include "kalman_filter.h"

void setUp() {}
void tearDown() {}

void test_stationary_zero_input_converges_near_zero_velocity() {
  KalmanState1D s = kalman1d_init(0.0f, 0.0f, 1.0f, 1.0f);
  const float dt = 0.02f;
  for (int i = 0; i < 250; i++) { // 5 s
    s = kalman1d_predict(s, dt, 0.0f, 0.5f);
    s = kalman1d_update(s, 0.0f, 0.25f);
  }
  TEST_ASSERT_FLOAT_WITHIN(0.05f, 0.0f, s.velocity_mps);
  TEST_ASSERT_FLOAT_WITHIN(0.2f, 0.0f, s.altitude_m);
}

void test_constant_acceleration_matches_analytic_kinematics() {
  KalmanState1D s = kalman1d_init(0.0f, 0.0f, 1.0f, 1.0f);
  const float dt = 0.02f, a0 = 100.0f;
  const int steps = 100; // 2 s, predict-only (no baro)
  for (int i = 0; i < steps; i++) s = kalman1d_predict(s, dt, a0, 0.5f);
  float t = steps * dt;
  TEST_ASSERT_FLOAT_WITHIN(1e-3f, a0 * t, s.velocity_mps);
  TEST_ASSERT_FLOAT_WITHIN(1e-2f, 0.5f * a0 * t * t, s.altitude_m);
}

void test_update_moves_toward_measurement_and_shrinks_variance() {
  KalmanState1D s = kalman1d_init(0.0f, 0.0f, 4.0f, 1.0f);
  KalmanState1D updated = kalman1d_update(s, 10.0f, 1.0f);
  TEST_ASSERT_TRUE(updated.altitude_m > 0.0f && updated.altitude_m < 10.0f);
  TEST_ASSERT_TRUE(updated.p00 < s.p00);
}

void test_predict_rejects_nonpositive_dt() {
  KalmanState1D s = kalman1d_init(1.0f, 2.0f, 3.0f, 4.0f);
  KalmanState1D out = kalman1d_predict(s, 0.0f, 50.0f, 1.0f);
  TEST_ASSERT_EQUAL_FLOAT(s.altitude_m, out.altitude_m);
  TEST_ASSERT_EQUAL_FLOAT(s.velocity_mps, out.velocity_mps);
}

void test_boost_then_coast_apogee_roughly_matches_analytic() {
  KalmanState1D s = kalman1d_init(0.0f, 0.0f, 1.0f, 1.0f);
  const float dt = 0.02f, aBoost = 80.0f, g = 9.80665f;
  for (int i = 0; i < 150; i++) s = kalman1d_predict(s, dt, aBoost, 0.5f); // 3 s boost, no baro
  float vBurnout = aBoost * 3.0f, altBurnout = 0.5f * aBoost * 3.0f * 3.0f;
  float trueVel = vBurnout, trueAlt = altBurnout;
  for (int i = 0; i < 1000; i++) {
    trueVel += -g * dt;
    trueAlt += trueVel * dt;
    s = kalman1d_predict(s, dt, -g, 0.5f);
    if (i % 5 == 0) s = kalman1d_update(s, trueAlt, 0.25f); // ~10 Hz baro
    if (trueVel <= 0.0f) break;
  }
  float trueApogee = altBurnout + (vBurnout * vBurnout) / (2.0f * g);
  TEST_ASSERT_FLOAT_WITHIN(trueApogee * 0.1f, trueApogee, s.altitude_m);
}

int main(int, char **) {
  UNITY_BEGIN();
  RUN_TEST(test_stationary_zero_input_converges_near_zero_velocity);
  RUN_TEST(test_constant_acceleration_matches_analytic_kinematics);
  RUN_TEST(test_update_moves_toward_measurement_and_shrinks_variance);
  RUN_TEST(test_predict_rejects_nonpositive_dt);
  RUN_TEST(test_boost_then_coast_apogee_roughly_matches_analytic);
  return UNITY_END();
}

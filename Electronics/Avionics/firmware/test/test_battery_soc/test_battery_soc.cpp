#include <unity.h>

#include "battery_soc.h"

void setUp() {}
void tearDown() {}

void test_clamps_above_full_and_below_empty() {
  TEST_ASSERT_EQUAL_UINT8(100, battery_socPercentFromVolts(4.35f));
  TEST_ASSERT_EQUAL_UINT8(100, battery_socPercentFromVolts(4.20f));
  TEST_ASSERT_EQUAL_UINT8(0, battery_socPercentFromVolts(3.27f));
  TEST_ASSERT_EQUAL_UINT8(0, battery_socPercentFromVolts(2.90f));
}

void test_hits_table_points_exactly() {
  TEST_ASSERT_EQUAL_UINT8(50, battery_socPercentFromVolts(3.84f));
  TEST_ASSERT_EQUAL_UINT8(80, battery_socPercentFromVolts(4.02f));
  TEST_ASSERT_EQUAL_UINT8(10, battery_socPercentFromVolts(3.69f));
}

void test_interpolates_between_points() {
  // halfway between 3.61 V (5 %) and 3.69 V (10 %) -> 7.5 % -> rounds to 8
  TEST_ASSERT_EQUAL_UINT8(8, battery_socPercentFromVolts(3.65f));
  // halfway between 4.02 V (80 %) and 4.08 V (85 %) -> 82.5 % -> rounds to 83
  TEST_ASSERT_EQUAL_UINT8(83, battery_socPercentFromVolts(4.05f));
}

void test_monotonic_over_the_whole_range() {
  uint8_t prev = 0;
  for (int mv = 3000; mv <= 4300; mv += 5) {
    uint8_t p = battery_socPercentFromVolts(mv / 1000.0f);
    TEST_ASSERT_TRUE(p >= prev);
    prev = p;
  }
}

void test_low_threshold_is_about_fifteen_percent() {
  // config.h BATT_LOW_V = 3.70 V should sit near 12-13 % on this curve
  uint8_t p = battery_socPercentFromVolts(3.70f);
  TEST_ASSERT_TRUE(p >= 10 && p <= 15);
}

int main(int, char **) {
  UNITY_BEGIN();
  RUN_TEST(test_clamps_above_full_and_below_empty);
  RUN_TEST(test_hits_table_points_exactly);
  RUN_TEST(test_interpolates_between_points);
  RUN_TEST(test_monotonic_over_the_whole_range);
  RUN_TEST(test_low_threshold_is_about_fifteen_percent);
  return UNITY_END();
}

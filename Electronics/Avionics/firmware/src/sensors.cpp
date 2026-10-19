#include "sensors.h"
#include "config.h"

#include <Arduino.h>
#include <Wire.h>
#include <math.h>

#include <Adafruit_BMP3XX.h>
#include <Adafruit_ADXL375.h>
#include <Adafruit_Sensor.h>

namespace {

Adafruit_BMP3XX bmp;
Adafruit_ADXL375 accel(12345); // arbitrary unified-sensor ID, unused beyond logging

bool g_baroOk = false;
bool g_accelOk = false;
float g_padPressurePa = 0.0f;
bool g_baselineCaptured = false;

// Standard barometric formula, referenced to the pad pressure captured at
// arm time rather than sea-level QNH — this yields altitude AGL directly
// without needing a QNH figure the firmware has no way to know.
float pressureToAltitudeAglM(float pressurePa, float referencePressurePa) {
  return 44330.0f * (1.0f - powf(pressurePa / referencePressurePa, 0.1903f));
}

} // namespace

bool sensors_init() {
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(I2C_CLOCK_HZ);

  g_baroOk = bmp.begin_I2C(BMP388_I2C_ADDR, &Wire);
  if (g_baroOk) {
    // The conversion must fit inside SENSOR_SAMPLE_INTERVAL_MS. Datasheet:
    // t = 234 + (392 + 2020*osr_p) + (163 + 2020*osr_t) us, so temp x8/press
    // x4 was ~25 ms (> the 20 ms tick) and temp x1/press x4 is ~11 ms.
    // Temperature only feeds compensation; x1 is Bosch's recommendation.
    // INFERRED from the library source, NOT yet bench-verified (2026-10-19):
    // performReading() starts a FORCED conversion and reads back the data
    // registers straight away (= the previous conversion's result); if the
    // previous one is still running, bmp3_set_op_mode() puts the chip to
    // sleep (aborting it) and blocks 5 ms. At the old 25 ms that would happen
    // every tick -- frozen/stale pressure_pa. Bench check: at rest, tick
    // rows' pressure_pa should change by noise every 20 ms.
    bmp.setTemperatureOversampling(BMP3_NO_OVERSAMPLING);
    bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
    bmp.setOutputDataRate(BMP3_ODR_50_HZ); // unused in forced mode; kept for normal mode
  }

  g_accelOk = accel.begin();
  if (g_accelOk) {
    accel.setDataRate(ADXL375_DATA_RATE);
  }

  return g_baroOk && g_accelOk;
}

bool sensors_selfTest() {
  bool baroReadOk = g_baroOk && bmp.performReading();

  Serial.print(F("[selftest] BMP388 init="));
  Serial.print(g_baroOk ? F("OK") : F("FAIL"));
  Serial.print(F(" read="));
  Serial.println(baroReadOk ? F("OK") : F("FAIL"));
  if (baroReadOk) {
    Serial.print(F("[selftest]   pressure_pa="));
    Serial.print(bmp.pressure);
    Serial.print(F(" temp_c="));
    Serial.println(bmp.temperature);
  }

  sensors_event_t event;
  bool accelReadOk = g_accelOk && accel.getEvent(&event);

  Serial.print(F("[selftest] ADXL375 init="));
  Serial.print(g_accelOk ? F("OK") : F("FAIL"));
  Serial.print(F(" read="));
  Serial.println(accelReadOk ? F("OK") : F("FAIL"));
  if (accelReadOk) {
    Serial.print(F("[selftest]   accel_g=("));
    Serial.print(event.acceleration.x / SENSORS_GRAVITY_STANDARD);
    Serial.print(F(", "));
    Serial.print(event.acceleration.y / SENSORS_GRAVITY_STANDARD);
    Serial.print(F(", "));
    Serial.print(event.acceleration.z / SENSORS_GRAVITY_STANDARD);
    Serial.println(F(")"));
  }

  return baroReadOk && accelReadOk;
}

void sensors_capturePadBaseline() {
  double sum = 0.0;
  uint16_t got = 0;
  for (uint16_t i = 0; i < PAD_BASELINE_AVERAGE_SAMPLES; i++) {
    if (bmp.performReading()) {
      sum += bmp.pressure;
      got++;
    }
    delay(20); // one-time blocking calibration step at arm time, not in loop()
  }
  if (got > 0) {
    g_padPressurePa = static_cast<float>(sum / got);
    g_baselineCaptured = true;
  }
}

SensorSample sensors_read() {
  SensorSample s;
  s.timestamp_ms = millis();

  s.baro_valid = g_baroOk && bmp.performReading();
  if (s.baro_valid) {
    s.pressure_pa = static_cast<float>(bmp.pressure);
    s.temperature_c = static_cast<float>(bmp.temperature);
    float reference = g_baselineCaptured ? g_padPressurePa : s.pressure_pa;
    s.altitude_agl_m = pressureToAltitudeAglM(s.pressure_pa, reference);
  }

  sensors_readAccel(s);
  return s;
}

bool sensors_readAccel(SensorSample &s) {
  sensors_event_t event;
  s.accel_valid = g_accelOk && accel.getEvent(&event);
  if (s.accel_valid) {
    s.accel_x_g = event.acceleration.x / SENSORS_GRAVITY_STANDARD;
    s.accel_y_g = event.acceleration.y / SENSORS_GRAVITY_STANDARD;
    s.accel_z_g = event.acceleration.z / SENSORS_GRAVITY_STANDARD;
    s.accel_mag_g = sqrtf(s.accel_x_g * s.accel_x_g + s.accel_y_g * s.accel_y_g +
                           s.accel_z_g * s.accel_z_g);
  }
  return s.accel_valid;
}

float sensors_padBaselinePressurePa() { return g_padPressurePa; }

bool sensors_baselineCaptured() { return g_baselineCaptured; }

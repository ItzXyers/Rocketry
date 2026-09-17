#pragma once

#include "sensors.h"

// Fuses BMP388 barometric altitude with a self-calibrated ADXL375 axial
// acceleration reading into a 2-state (altitude, velocity) Kalman filter.
// TELEMETRY ONLY: nothing here feeds back into flight_state.cpp's apogee
// or landed detection -- see the getters below for the read-only values
// callers may log.
//
// Axis handling: the ADXL375's mounting orientation relative to the
// rocket's long axis is undocumented anywhere in this codebase. Rather
// than hardcode a physical axis, velocity_estimator_reset() captures a
// stationary 3-axis accel average at arm time as a fixed body-frame
// "pad-up" unit vector; every subsequent sample is projected onto it.
// LIMITATIONS (fundamental, not bugs):
//  - Valid only while orientation relative to the pad stays close to
//    calibration time -- true for rail-guided boost, degrades under
//    coast-phase weathercocking/tipping (no gyro exists on this hardware
//    to detect or correct that).
//  - Subtracting the *measured* pad magnitude cancels an additive bias
//    along the pad vector, but NOT a sensor gain/scale error, which still
//    scales with true acceleration and reappears at boost-phase
//    magnitudes far from the ~1g calibration reference.
void velocity_estimator_reset();

// Feeds one sensor sample into the filter. Call every loop() iteration.
// No-op before the first velocity_estimator_reset() call. Degrades
// gracefully exactly like flight_state.cpp: predict-only when baro_valid
// is false, holds state when both baro_valid and accel_valid are false,
// and re-seeds (rather than integrating through) any gap longer than
// KALMAN_MAX_DT_S -- see the .cpp for why.
void velocity_estimator_update(const SensorSample &sample);

float velocity_estimator_velocityMps(); // m/s, up positive. 0.0 before reset().
float velocity_estimator_altitudeM();   // m AGL, same frame as SensorSample::altitude_agl_m. 0.0 before reset().

// True if the pad-up calibration in the most recent reset() looked sane
// (|g_pad| within [PAD_CAL_MAG_MIN_G, PAD_CAL_MAG_MAX_G]). False means the
// axial projection is running on a best-effort fallback vector -- check
// the Serial log from reset() before trusting this flight's estimate.
bool velocity_estimator_calibrationValid();

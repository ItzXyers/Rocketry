#pragma once

// Central pin map and tunables for the flight computer.
//
// Pin macros MUST use the Arduino symbolic labels (Dn/An), never bare
// integers. The ESP32 Arduino core's "legacy GPIO numbering" build option
// changes what a raw integer like `9` means (GPIO9 == D6 in one mode, D9 in
// the other) — using the symbolic macros throughout means this file is
// correct regardless of that setting, instead of silently driving the
// wrong pin if it's ever toggled.

// ---------------------------------------------------------------------------
// Pins — fixed by ../avionics_wiring.md (no-GPS variant)
// ---------------------------------------------------------------------------

// I2C — BMP388 barometer + ADXL375 accelerometer, shared bus, default Wire pins.
#define PIN_I2C_SDA A4
#define PIN_I2C_SCL A5

// BMP388 I2C address. The Adafruit library default is 0x77
// (BMP3XX_DEFAULT_ADDRESS); this board's BMP388 breakout has its address pad
// strapped low, so it enumerates at 0x76 — verified 2026-09-07 by bus scan
// (CHIP_ID register 0x00 read back 0x50). Pinned deliberately, not
// auto-detected: a board later swapped for a 0x77 part should fail the sensor
// self-test loudly rather than be silently accommodated. The chips_bench env
// (see platformio.ini) has a SCAN/ID command for re-checking this on new hardware.
#define BMP388_I2C_ADDR 0x76

// No microSD reader any more (dropped 2026-10-19): the log goes to the
// Nano ESP32's internal flash (FFat partition, see logger.h). D10-D13 are free.

// Buzzer driver: BC337-40 NPN base via R1 1k, R2 10k base pulldown on the board
// (was a 2N7000 + 220R; Phoenix schematic rev E). HIGH = buzzer on.
#define PIN_BUZZER D9

// D2/D3 are reserved for a possible future GPS (Serial1 RX/TX) — do not reuse.

// ---------------------------------------------------------------------------
// Pins — battery sense; free pins
// ---------------------------------------------------------------------------

// No deploy channel (removed 2026-10-19): the burn wire is gone and Phoenix
// deploys on the motor ejection charge, so the board fires nothing. D6, the
// old PIN_DEPLOY, is free.

// SW1 (reed power switch) and SW2 (Wi-Fi interlock button on D7) were both
// dropped 2026-10-19. SW1 was never firmware-readable; without SW2 the
// ground-support AP comes up at boot (see wireless.h). D7 is free.

// Battery voltage sense: BATT+ -> R11 10k -> A0 -> R12 10k -> GND. The 5k
// source impedance is low enough for the ADC without a filter cap; the
// divider draws ~0.2 mA whenever the battery is connected. A0 =
// GPIO1 = ADC1_CH0: ADC1 keeps working while the Wi-Fi AP is up (ADC2 is
// shared with the radio on the ESP32-S3). Not a strapping pin.
// BATT_CAL_GAIN absorbs resistor tolerance and any series drop.
// See ../../avionics_bay_schematic_phoenix40.html.
#define PIN_BATT_SENSE A0

// ---------------------------------------------------------------------------
// Tunables — STARTING DEFAULTS for bench tuning, not asserted specs.
// Every one of these must be verified against real hardware and a real
// motor's thrust curve before ever flying.
// ---------------------------------------------------------------------------

// -- Launch detection (ADXL375) --
#define LAUNCH_ACCEL_THRESHOLD_G 3.0f      // STARTING DEFAULT — verify on bench, not a real spec
#define LAUNCH_ACCEL_CONFIRM_MS 100UL      // STARTING DEFAULT — verify on bench, not a real spec

// -- Boost/burnout (ADXL375) --
#define BOOST_MIN_TIME_MS 250UL            // STARTING DEFAULT — floor before burnout is even checked, rejects single-sample noise
#define BURNOUT_ACCEL_THRESHOLD_G 1.5f     // STARTING DEFAULT — "accel fell back toward ~1g" heuristic, verify against real motor thrust curve

// -- Apogee window (barometric altitude, AGL) --
#define MIN_COAST_TIME_MS 2000UL           // STARTING DEFAULT — must exceed the real motor's burn time + margin
#define MAX_TIME_TO_APOGEE_MS 20000UL      // STARTING DEFAULT — must exceed simulated time-to-apogee (see ../../OpenRocket Designs/) with margin
#define ALTITUDE_FILTER_ALPHA 0.3f         // STARTING DEFAULT — verify on bench, not a real spec
#define APOGEE_DROP_THRESHOLD_M 3.0f       // STARTING DEFAULT — must clear the real baro noise floor
#define APOGEE_CONFIRM_SAMPLES 5           // STARTING DEFAULT — verify on bench, not a real spec


// -- Landed detection --
#define LANDED_ALT_STABLE_BAND_M 1.0f      // STARTING DEFAULT — verify on bench, not a real spec
#define LANDED_STABLE_DURATION_MS 10000UL  // STARTING DEFAULT — verify on bench, not a real spec


// -- Logging (internal flash, FFat partition ~9.4 MB; see logger.h) --
// A CSV row is ~85-100 B, so 50 Hz is ~4.5 KB/s (~35 min to fill the
// partition). Pad/landed time is therefore logged at LOG_PAD_DECIMATION-th
// rate (~1.6 MB per pad-hour) and only flight states at full rate (~0.8 MB
// for a 3 min flight) -- see main.cpp's shouldLogSample(). Ascent (BOOST/
// COAST) additionally gets accel-only rows at ASCENT_ACCEL_INTERVAL_US
// (200 Hz, ~19 KB/s): at most ~0.4 MB even for a full MAX_TIME_TO_APOGEE_MS.
#define LOG_BUFFER_RECORDS 128             // STARTING DEFAULT — RAM (~8 KB) vs. flush frequency; 0.64 s of 200 Hz ascent per flush, so fewer fsyncs (each one a flash stall) during boost/coast
#define LOG_FLUSH_INTERVAL_MS 2000UL       // STARTING DEFAULT — data-loss window vs. flash-write stall frequency
#define LOG_PAD_DECIMATION 10              // pad/landed: every 10th sample = 5 Hz
#define LOG_MIN_FREE_BYTES (5UL * 1024UL * 1024UL) // self-test fails below this: ~2.5 h of pad + a full flight. Clear old logs (DEL/FORMAT) between flight days

// -- Sampling --
#define SENSOR_SAMPLE_INTERVAL_MS 20UL     // STARTING DEFAULT — 50 Hz flight-logic tick (baro + accel -> flight_state, velocity_estimator). ALTITUDE_FILTER_ALPHA and APOGEE_CONFIRM_SAMPLES count samples at THIS rate -- to log faster, change ASCENT_ACCEL_INTERVAL_US, not this
#define ASCENT_ACCEL_INTERVAL_US 5000UL    // STARTING DEFAULT — 200 Hz accel-only log rows between ticks in BOOST/COAST (+ pad over launch threshold). Baro columns repeat the last tick's reading. Go faster only after the bench logger_maxFlushUs check -- every flush stall is a gap
static_assert((SENSOR_SAMPLE_INTERVAL_MS * 1000UL) % ASCENT_ACCEL_INTERVAL_US == 0,
              "ASCENT_ACCEL_INTERVAL_US must divide the flight-logic tick evenly");
#define ADXL375_DATA_RATE ADXL3XX_DATARATE_200_HZ // matches ASCENT_ACCEL_INTERVAL_US (100 Hz bandwidth); chip default is 100 Hz ODR, never written before
#define I2C_CLOCK_HZ 400000UL              // fast mode (both BMP388 and ADXL375 support it); was the 100 kHz default -- check for I2C read errors on the real harness
#define PAD_BASELINE_AVERAGE_SAMPLES 50    // STARTING DEFAULT — averaged once on IDLE_ARMED entry

// -- Velocity/altitude Kalman filter (BMP388 baro + ADXL375 self-calibrated axial accel) --
// TELEMETRY ONLY -- see velocity_estimator.h. Does not feed flight_state.cpp's
// apogee/landed detectors. Every constant below is an unverified starting
// guess; expect ACCEL_NOISE_STD_MPS2 in particular to be optimistic during
// boost (motor vibration + off-axis projection error) -- retune these
// offline against flight 1's CSV (which logs raw accel_x/y/z_g and
// altitude_agl_m alongside the estimate) rather than guessing on the bench.
#define ACCEL_NOISE_STD_MPS2 2.5f             // STARTING DEFAULT (m/s^2, 1-sigma) — deliberately generous for flight 1: the ADXL375's ~49 mg/LSB (~0.48 m/s^2) quantization floor is the *best* case, real boost-phase noise (motor vibration, off-axis projection error) will be much worse; erring high keeps the baro in authority so the logged estimate stays interpretable, since raw accel_x/y/z_g is still logged and a tighter offline re-fit is always possible, but a too-tight filter that overtrusts a noisy accel this flight can't be undone after the fact
#define ACCEL_NOISE_FALLBACK_STD_MPS2 3.0f    // STARTING DEFAULT (m/s^2, 1-sigma) — used when accel_valid==false and accelAxial is forced to 0
#define BARO_ALT_VARIANCE_M2 0.25f            // STARTING DEFAULT (m^2, i.e. sigma=0.5m) — verify by logging altitude_agl_m at rest post-baseline-capture and computing sample variance
#define KALMAN_INITIAL_ALTITUDE_VAR_M2 1.0f   // STARTING DEFAULT (m^2) — initial uncertainty at arm-time reset
#define KALMAN_INITIAL_VELOCITY_VAR_M2S2 1.0f // STARTING DEFAULT ((m/s)^2) — v=0 is a good assumption when stationary on the pad
#define KALMAN_REGAP_VELOCITY_VAR_M2S2 2500.0f// STARTING DEFAULT ((m/s)^2 = (50 m/s)^2) — used only when re-seeding after a sensor gap mid-flight, where velocity is genuinely unknown
#define KALMAN_MAX_DT_S 0.5f                  // STARTING DEFAULT (s) — dt above this triggers a re-seed instead of integrating across a blackout
#define PAD_CAL_MAG_MIN_G 0.8f                // STARTING DEFAULT (g) — pad accel calibration sanity band; ADXL375 at rest should read ~1.0g
#define PAD_CAL_MAG_MAX_G 1.2f                // STARTING DEFAULT (g)

// -- Battery monitor (see battery.*) --
#define BATT_DIVIDER_RATIO 2.0f            // (R11 + R12) / R12 = (10k + 10k) / 10k
#define BATT_CAL_GAIN 1.000f               // STARTING DEFAULT -- set to (multimeter volts / reported volts) at ~3.9 V on the real board; absorbs resistor tolerance + ADC gain error
#define BATT_ADC_SAMPLES 8                 // averaged per reading (~0.1 ms total, non-blocking enough for loop())
#define BATT_SAMPLE_INTERVAL_MS 500UL      // 2 Hz -- the cell voltage moves slowly
#define BATT_FILTER_ALPHA 0.2f             // EMA on top of the averaging -- smooths flash-write / Wi-Fi TX sag
#define BATT_PRESENT_MIN_V 2.5f            // below this the reading is "no battery" (divider missing, or USB-only bench power)
#define BATT_LOW_V 3.70f                   // STARTING DEFAULT -- ~15 % on the generic curve; don't fly below this. Pad go/no-go only, never a flight-logic input


// -- Wireless ground interface (WiFi AP + HTTP, see wireless.*) --
// AP powers up at boot and stays up until a successful /arm or confirmed
// BOOST latches it off for the rest of the power cycle (see
// flight_state.cpp).
#define WIFI_AP_SSID "FLIGHTCOMPUTER-XXXX"   // STARTING DEFAULT — set unique per board before flying near other boards
#define WIFI_AP_PASSWORD "changeme12345"     // STARTING DEFAULT — WPA2, change before flying
#define WIFI_AP_CHANNEL 6                    // STARTING DEFAULT — fixed channel, no scan needed for a single-purpose AP
#define WIFI_AP_MAX_CONNECTIONS 1            // deliberately capped so a stray device can't also join
#define WIFI_AP_HTTP_PORT 80
#define WIFI_ARM_SHUTDOWN_GRACE_MS 500UL     // STARTING DEFAULT — verify on bench this is enough for the Pi to see the full /arm response before the AP drops
#define FIRMWARE_VERSION "0.2.3"             // bump manually per notable firmware change; surfaced read-only via GET /config

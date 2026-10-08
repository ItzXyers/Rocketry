#pragma once

// Central pin map and tunables for the flight computer.
//
// Pin macros MUST use the Arduino symbolic labels (Dn/An), never bare
// integers. The ESP32 Arduino core's "legacy GPIO numbering" build option
// changes what a raw integer like `9` means (GPIO9 == D6 in one mode, D9 in
// the other) — using the symbolic macros throughout means this file is
// correct regardless of that setting, instead of silently swapping the
// buzzer and deployment channels if it's ever toggled.

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

// SPI — microSD reader, dedicated CS (not shared with any other SPI device).
#define PIN_SPI_SCK D13
#define PIN_SPI_MISO D12
#define PIN_SPI_MOSI D11
#define PIN_SD_CS D10

// Buzzer MOSFET gate (2N7000, via 220R gate resistor + 10k pulldown on the board).
#define PIN_BUZZER D9

// D2/D3 are reserved for a possible future GPS (Serial1 RX/TX) — do not reuse.

// ---------------------------------------------------------------------------
// Pins — new for this firmware, NOT YET in the schematic (see plan notes)
// ---------------------------------------------------------------------------

// Deployment (burn-wire) MOSFET gate. D6 = GPIO9 on the underlying ESP32-S3:
// free of I2C/SPI/buzzer, not D2/D3 (reserved for GPS), not one of the four
// ESP32-S3 strapping pins (GPIO0/3/45/46), not native-USB or UART0. Needs the
// same gate-resistor + pulldown pattern as the buzzer, and — separately, a
// hardware concern, not a firmware one — a higher-current logic-level MOSFET
// than the 2N7000 (200mA max), since a nichrome burn-wire coil is expected to
// draw hundreds of mA to a few amps. Backups if D6 proves awkward on the real
// schematic: D4, D5, D7.
#define PIN_DEPLOY D6

// Wireless-arm interlock (SW2) — separate from SW1 (whole-board power
// cutoff, not firmware-readable). D7 = GPIO10: free of I2C/SPI/buzzer/
// deploy, not D2/D3 (GPS-reserved), not a strapping pin, not native-USB/
// UART0. External pulldown (R3, 10k), not INPUT_PULLUP — see
// avionics_wiring.md for the fault-mode rationale (a chafed signal wire
// shorting to the common GND bus must read as NOT armed, not armed).
// SW2 is a MOMENTARY push button (3V3 -> button -> D7): wireless.cpp latches
// it -- a press held WIFI_BUTTON_HOLD_MIN_MS..MAX_MS, then released, toggles
// the interlock for this power cycle. A line stuck HIGH never releases, so it
// can never enable the radio. A second reed module wired the same way works
// as a magnet-operated button from outside the sealed bay.
#define PIN_ARM_INTERLOCK D7

// Battery voltage sense: BATT+ -> R11 100k -> A0 -> R12 100k -> GND, C4 100nF
// across R12 (ADC sample-cap reservoir for the 50k source impedance). A0 =
// GPIO1 = ADC1_CH0: ADC1 keeps working while the Wi-Fi AP is up (ADC2 is
// shared with the radio on the ESP32-S3). Not a strapping pin. On the Phoenix
// bay the divider's bottom is board GND, which Q3 (low-side switch) connects
// to BATT- only while armed -- so the divider draws nothing when off.
// See ../../avionics_bay_schematic_phoenix40.html.
#define PIN_BATT_SENSE A0

// ---------------------------------------------------------------------------
// Tunables — STARTING DEFAULTS for bench tuning, not asserted specs.
// Every one of these must be verified against real hardware, a real motor's
// thrust curve, and (for the deploy timing especially) real bench
// measurement of the actual coil/line/supply combination before ever flying.
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

// -- Apogee deploy dwell --
#define APOGEE_DEPLOY_DWELL_MS 2000UL      // fixed dwell in APOGEE_DEPLOY before -> DESCENT; must exceed DEPLOY_ON_TIME_MS so deployment_update() has definitely serviced the on-time before we move on

// -- Landed detection --
#define LANDED_ALT_STABLE_BAND_M 1.0f      // STARTING DEFAULT — verify on bench, not a real spec
#define LANDED_STABLE_DURATION_MS 10000UL  // STARTING DEFAULT — verify on bench, not a real spec

// -- Deployment firing --
// No empirical current/duration spec exists for the burn-wire mechanism yet.
// These are placeholders only — bench-measure against the real coil/line
// (dummy load first, see the plan's verification steps) before ever flying.
#define DEPLOY_ON_TIME_MS 1500UL           // STARTING DEFAULT — no empirical spec exists yet
#define DEPLOY_MAX_ON_TIME_MS 4500UL       // Hard safety ceiling. Must stay > DEPLOY_ON_TIME_MS with real margin.
static_assert(DEPLOY_MAX_ON_TIME_MS > DEPLOY_ON_TIME_MS + 1000UL,
              "DEPLOY_MAX_ON_TIME_MS must exceed DEPLOY_ON_TIME_MS with real margin");

// -- Logging --
#define LOG_BUFFER_RECORDS 32              // STARTING DEFAULT — RAM vs. flush-frequency tradeoff
#define LOG_FLUSH_INTERVAL_MS 2000UL       // STARTING DEFAULT — data-loss window vs. write-transient frequency

// -- Sampling --
#define SENSOR_SAMPLE_INTERVAL_MS 20UL     // STARTING DEFAULT — 50 Hz, tune vs. detection latency and log volume
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
#define BATT_DIVIDER_RATIO 2.0f            // (R11 + R12) / R12 = (100k + 100k) / 100k
#define BATT_CAL_GAIN 1.000f               // STARTING DEFAULT -- set to (multimeter volts / reported volts) at ~3.9 V on the real board; absorbs resistor tolerance + ADC gain error
#define BATT_ADC_SAMPLES 8                 // averaged per reading (~0.1 ms total, non-blocking enough for loop())
#define BATT_SAMPLE_INTERVAL_MS 500UL      // 2 Hz -- the cell voltage moves slowly
#define BATT_FILTER_ALPHA 0.2f             // EMA on top of the averaging -- smooths SD-write / Wi-Fi TX sag
#define BATT_PRESENT_MIN_V 2.5f            // below this the reading is "no battery" (divider missing, or USB-only bench power)
#define BATT_LOW_V 3.70f                   // STARTING DEFAULT -- ~15 % on the generic curve; don't fly below this. Pad go/no-go only, never a flight-logic input

// -- Bench-test deployment gate --
#define DEPLOY_BENCH_ARM_TIMEOUT_MS 10000UL // window after ARM in which FIRE is accepted

// -- Wireless ground interface (WiFi AP + HTTP, see wireless.*) --
// AP powers up only while the SW2 button has latched the interlock on, and
// only before real flight (confirmed BOOST latches it off for the rest of the
// power cycle regardless of SW2 — see flight_state.cpp). Never touches
// PIN_DEPLOY; wireless FIRE does not exist.
#define WIFI_AP_SSID "FLIGHTCOMPUTER-XXXX"   // STARTING DEFAULT — set unique per board before flying near other boards
#define WIFI_AP_PASSWORD "changeme12345"     // STARTING DEFAULT — WPA2, change before flying
#define WIFI_AP_CHANNEL 6                    // STARTING DEFAULT — fixed channel, no scan needed for a single-purpose AP
#define WIFI_AP_MAX_CONNECTIONS 1            // deliberately capped so a stray device can't also join
#define WIFI_AP_HTTP_PORT 80
#define WIFI_INTERLOCK_DEBOUNCE_MS 50UL      // contact-bounce filter on the SW2 button
#define WIFI_BUTTON_HOLD_MIN_MS 1000UL       // shorter presses are ignored (bumps, handling, glitches)
#define WIFI_BUTTON_HOLD_MAX_MS 5000UL       // longer = treated as a stuck/shorted line, ignored until released
#define WIFI_ARM_SHUTDOWN_GRACE_MS 500UL     // STARTING DEFAULT — verify on bench this is enough for the Pi to see the full /arm response before the AP drops
#define FIRMWARE_VERSION "0.2.0"             // bump manually per notable firmware change; surfaced read-only via GET /config

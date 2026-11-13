# Avionics Sled — Build & Wiring Verification Checklist

Companion to [`avionics_bom.md`](avionics_bom.md) and [`avionics_wiring.md`](avionics_wiring.md).
For a freshly assembled or repaired sled, **before it goes into an airframe**
and before it's flown. This is a bench checklist, not a pad checklist — see
[`../LaunchControl/pad_checklist.md`](../LaunchControl/pad_checklist.md) for
day-of-launch procedure.

Last updated: 2026-10-19 — SW1 (reed), Q3/R6, SW2/R3 and the microSD reader
dropped from the harness. The bay powers up when the battery is plugged in,
the Wi-Fi AP comes up at boot, and the log is on the Nano's internal flash
(firmware 0.2.1+). §3 and §6 are rewritten for that.

---

## 0. Parts not yet in the BOM — confirm these exist before starting

`avionics_bom.md`'s open items list several parts required for this build
that don't have a sourced SKU yet. Don't start continuity checks assuming
they're generic/interchangeable without reading the specific caveat:

- [ ] **No power switch (SW1) and no SW2/R3** — both dropped 2026-10-19.
      Power on/off is plugging/unplugging the battery's JST lead, so that
      connector has to be reachable whenever the bay needs to be switched.
- [ ] **C1** (220 µF low-ESR bulk cap) — **this is a hard gate, not a nice-to-have.**
      Fit it, or bench-verify the flash-write + WiFi-TX transient on a
      representative supply, **before using the wireless interface anywhere
      near a loaded rocket or an installed CO2 cartridge.** See
      `avionics_bom.md` open item 3.
- [ ] **No deploy MOSFET (Q2) or burn-wire coil.** The deploy channel was
      removed from the firmware 2026-10-19 (motor-ejection deployment); D6
      is free and must stay unconnected.
- [ ] R1 (220 Ω, buzzer gate) and R2 (10 kΩ, buzzer pulldown) — in the BOM's
      wiring doc, not the BOM table itself. Confirm on hand.

---

## 1. Power chain

Chain: **LiPo → S7V8F5 (5 V) → C1 → Nano VIN → onboard buck (3.3 V) → everything else.**

- [ ] Battery connector matches the charger/regulator's JST-PH. If using the
      EEMB LP852040 (Option B), confirm the JST-RCY→JST-PH adapter/re-termination
      is done, not just planned (`avionics_bom.md` §3, Option B).
- [ ] BATT+ goes straight to the regulator input and the R11/R12 divider —
      no switch in between (SW1/Q3 dropped 2026-10-19). Verify with a
      continuity meter, don't assume from the diagram alone.
- [ ] Unplugging the battery lead powers everything down (no other source
      back-feeds the bay with USB disconnected).
- [ ] With the battery plugged in and no USB connected, measure S7V8F5
      output at C1: expect ~5.0 V.
- [ ] **VIN margin caveat:** 5 V into the Nano's VIN is 1 V under Arduino's
      documented 6 V minimum. Works per community testing, but there is no
      margin — if the board is flaky on this supply, this is the first
      thing to suspect, not sensor wiring. See `avionics_bom.md` §2.
- [ ] C1 is physically present at the regulator's 5 V output (not just in
      the BOM) — visually confirm, this is easy to skip on a hand-built board.

## 2. I²C bus — BMP388 + ADXL375 (SDA=A4, SCL=A5)

- [ ] Both sensors' SDA/SCL tie to A4/A5, not a second bus — this design
      uses one shared I²C bus for both (`avionics_wiring.md` diagram).
- [ ] Both sensors powered from 3V3, not 5V — the Nano ESP32's GPIOs are
      natively 3.3 V (`avionics_wiring.md` #6).
- [ ] Pull-ups present (onboard the Qwiic breakouts — confirm, don't add a
      second set if already populated).
- [ ] After power-up, `flight_state_init()`'s self-test (`sensors_selfTest()`
      in `firmware/src/sensors.cpp`) must pass — see §5 below for what that
      looks/sounds like.

## 3. Flight log — internal flash (no microSD since 2026-10-19)

The log is `FLIGHTnnn.CSV` in the Nano ESP32's ~9.4 MB FFat partition, one
file per boot. D10–D13 are free. Commands are on the flight firmware's USB
serial console: `LOGS`, `DUMP n`, `DEL n`, `FORMAT YES`.

- [ ] **New board:** the first boot fails self-test with `ffat mount failed`
      (the partition is unformatted). Send `FORMAT YES`, power-cycle, and
      confirm the self-test now passes.
- [ ] **Uploads keep logs:** flash the firmware again (`pio run -t upload`),
      then `LOGS` still lists the earlier files. (`pio run -t erase` or a
      partition-table change wipes them — pull logs first.)
- [ ] `DUMP n` prints a readable CSV between `BEGIN`/`END` lines, and
      `GET /log?n=` over Wi-Fi downloads the same file.
- [ ] `STATE` shows the worst flush stall (`worst flush ... us`). Note it;
      after the first flight, check the CSV for timestamp gaps under load.
- [ ] At least 5 MB free (`LOGS`) before a flight day — below that the boot
      self-test fails on purpose.

## 4. Buzzer drive (D9 → R1 → Q1 → buzzer)

- [ ] R1 (220 Ω) between D9 and Q1's gate — present, not a direct GPIO-to-gate
      wire (ringing risk on a long lead, per `avionics_wiring.md` #3).
- [ ] R2 (10 kΩ) from Q1's gate to GND — present. Without this, the buzzer
      can chirp on power-up before firmware sets D9 low.
- [ ] Buzzer is tapped from SYS_5V (post-C1), not 3V3 — per the wiring
      diagram's `C1 -. "SYS_5V tap" .-> BZ`.
- [ ] Q1's source ties to the common GND bus.

## 5. Deployment channel — removed 2026-10-19

There is no deploy channel any more: the burn wire is gone, Phoenix deploys on
the motor's ejection charge, and firmware 0.2.3+ has no `PIN_DEPLOY`, no
`ARM`/`FIRE` serial commands and no fired-latch. Apogee is still detected and
logged (`APOGEE_CONFIRMED` / `APOGEE_TIMEOUT` events, state code 5 `APOGEE`).

- [ ] D6 has nothing soldered to it.
- [ ] On the bench, `STATE` lists no deploy information and `HELP`-style
      output from an unknown command doesn't offer `ARM`/`FIRE`.

## 6. Wireless ground interface (no SW2 since 2026-10-19)

There is no interlock button any more: the AP comes up at every boot and
stays up until a successful `/arm` or a confirmed launch latches it off for
the rest of that power cycle.

- [ ] After boot, serial prints `[wireless] AP up` and `WIFI_AP_SSID` from
      `config.h` is visible on a phone/laptop within a few seconds.
- [ ] `GET /status` answers, and `log_free_bytes` / `logger_ready` look right.
- [ ] `http://192.168.4.1/` opens the console on a phone: status updates
      every second, the Logs card lists files, Download saves a CSV, and
      Delete removes an old log (the "this boot" file has no Delete).
- [ ] Arm sounds (bench: `BUZZER ARM`, `BUZZER REJECT` in
      chips_bench, or `ARM`/`REJECT` in buzzer_bench) are each
      clearly distinguishable from the boot pass/fail tones and the recovery
      beacon, and audible through the closed bay.
- [ ] `POST /arm` succeeds, and the AP disappears ~0.5 s later. It stays
      down until the next power cycle.

## 7. Self-test / boot behavior

Power up by plugging in the battery, with the USB serial monitor attached
(115200 baud):

- [ ] The buzzer stays silent through boot — `buzzer_init()` is the first
      call in `setup()`, before `Serial.begin()`.
- [ ] `flight_state_init()` runs a sensor self-test and logger-open check.
      Confirm a pass tone (`BuzzerPattern::SELF_TEST_PASS`) plays, or the
      fail tone if a sensor/logger fault is injected on purpose (e.g.
      unplugging a Qwiic cable, or a not-yet-formatted flash on a new
      board) — the fail path should also be exercised
      once, not just the pass path.
- [ ] On self-test pass, state transitions to `IDLE_ARMED` — confirm via
      the `STATE` serial command or `/status` once wireless is up.
      **This transition is immediate and automatic — there is no separate
      arm step at this point.** See the pad checklist for why this matters
      for handling discipline on the pad.
- [ ] `WIFI_AP_SSID` in `config.h` has been changed from the shared default
      to something unique per board — flying near another board on the
      default SSID/password is a real collision risk. Same for
      `WIFI_AP_PASSWORD` (default is a placeholder, not meant to ship).
- [ ] `FIRMWARE_VERSION` in `config.h` reflects the actual build on this
      board (surfaced read-only via `GET /config`) — bump it if this build
      differs from the last flown version.

## 8. Tunables — do not treat these as verified specs

Everything in `config.h` marked `STARTING DEFAULT` is exactly that. This
checklist's job is to confirm the *wiring and mechanism* work, not to
rubber-stamp these numbers. Before the sled is flown (not just built),
separately verify, per motor/flight:

- [ ] `LAUNCH_ACCEL_THRESHOLD_G` / `LAUNCH_ACCEL_CONFIRM_MS` — bench-verify
      against expected handling/rail-bump accelerations vs. real liftoff.
- [ ] `BURNOUT_ACCEL_THRESHOLD_G` — verify against the actual motor's
      thrust curve, not just the placeholder.
- [ ] `MIN_COAST_TIME_MS` — must exceed the real motor's burn time with
      margin, per-motor.
- [ ] `MAX_TIME_TO_APOGEE_MS` — must exceed the OpenRocket-simulated
      time-to-apogee for the actual flight, with margin
      (`../../OpenRocket Designs/`). This is the unconditional backup that
      marks apogee in the log if the barometer detector never confirms. It
      fires nothing (no deploy channel), so a wrong value only mislabels
      the log, but it should still be right.

---

## Sign-off

- [ ] Every unchecked item in §0 has either been closed out or is
      explicitly accepted as a known gap for this build (bench-only, not
      for flight).
- [ ] See the pad checklist for what comes after this one.

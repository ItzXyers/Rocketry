# Avionics Sled — Build & Wiring Verification Checklist

Companion to [`avionics_bom.md`](avionics_bom.md) and [`avionics_wiring.md`](avionics_wiring.md).
For a freshly assembled or repaired sled, **before it goes into an airframe**
and before it's flown. This is a bench checklist, not a pad checklist — see
[`../LaunchControl/pad_checklist.md`](../LaunchControl/pad_checklist.md) for
day-of-launch procedure.

Last updated: 2026-08-08

---

## 0. Parts not yet in the BOM — confirm these exist before starting

`avionics_bom.md`'s open items list several parts required for this build
that don't have a sourced SKU yet. Don't start continuity checks assuming
they're generic/interchangeable without reading the specific caveat:

- [ ] **SW1** (power/arm switch) — placed between battery/charger junction
      and the regulator's VIN, per `avionics_wiring.md`'s "Additions beyond
      the BOM" #1. Not a specific SKU yet, any switch rated for the current
      works.
- [ ] **SW2** (wireless-arm interlock) + **R3** (10 kΩ pulldown) — gates the
      wireless ground-support AP, wired to `PIN_ARM_INTERLOCK` (D7). See
      `avionics_wiring.md` #8 for the fault-mode rationale (must read
      NOT-ARMED on a chafed signal wire, not armed) — do not substitute
      `INPUT_PULLUP` + switch-to-GND, that inverts the fail-safe direction.
- [ ] **C1** (220 µF low-ESR bulk cap) — **this is a hard gate, not a nice-to-have.**
      Fit it, or bench-verify the SD-write + WiFi-TX transient on a
      representative supply, **before using the wireless interface anywhere
      near a loaded rocket or an installed CO2 cartridge.** See
      `avionics_bom.md` open item 3.
- [ ] **Deploy MOSFET (Q2, drives `PIN_DEPLOY`/D6)** — not in the BOM at all.
      The 2N7000 used for the buzzer (Q1) is rated 200 mA max; the burn-wire
      nichrome coil is expected to draw hundreds of mA to a few amps. **Do
      not reuse a 2N7000 for the deploy channel.** Source a logic-level
      MOSFET rated for the actual coil current once that's bench-measured
      (see the CO2 checklist). Needs the same gate-resistor + pulldown
      pattern as Q1.
- [ ] R1 (220 Ω, buzzer gate) and R2 (10 kΩ, buzzer pulldown) — in the BOM's
      wiring doc, not the BOM table itself. Confirm on hand.

---

## 1. Power chain

Chain: **LiPo → S7V8F5 (5 V) → C1 → Nano VIN → onboard buck (3.3 V) → everything else.**

- [ ] Battery connector matches the charger/regulator's JST-PH. If using the
      EEMB LP852040 (Option B), confirm the JST-RCY→JST-PH adapter/re-termination
      is done, not just planned (`avionics_bom.md` §3, Option B).
- [ ] SW1 sits between the battery/charger junction and the regulator VIN
      (not directly on the battery terminal) — verify with a continuity
      meter, don't assume from the diagram alone.
- [ ] With SW1 open, confirm the charger can still trickle-charge the
      battery via USB-C (pad-safety property this placement is meant to
      guarantee).
- [ ] With SW1 closed and no USB connected, measure S7V8F5 output at C1:
      expect ~5.0 V.
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
      natively 3.3 V; this is required regardless of the SD reader's
      3V-only caveat below (`avionics_wiring.md` #6).
- [ ] Pull-ups present (onboard the Qwiic breakouts — confirm, don't add a
      second set if already populated).
- [ ] After power-up, `flight_state_init()`'s self-test (`sensors_selfTest()`
      in `firmware/src/sensors.cpp`) must pass — see §5 below for what that
      looks/sounds like.

## 3. SPI bus — microSD reader (SCK=D13, MISO=D12, MOSI=D11, CS=D10)

- [ ] SD reader is on the 3V3 rail — **Adafruit 4682 is 3 V logic only, no
      level shifter.** Driving it from 5 V will damage it, not just
      malfunction (`avionics_bom.md` §7).
- [ ] CS (D10) is dedicated to the SD reader — confirm no other SPI device
      shares this bus per the current design.
- [ ] Card is the Kingston Industrial 16 GB (wide temp range) if following
      the BOM's recommendation over the consumer Verbatim option — confirm
      which was actually bought.
- [ ] Card is formatted and blank/backed-up before first flight use.

## 4. Buzzer drive (D9 → R1 → Q1 → buzzer)

- [ ] R1 (220 Ω) between D9 and Q1's gate — present, not a direct GPIO-to-gate
      wire (ringing risk on a long lead, per `avionics_wiring.md` #3).
- [ ] R2 (10 kΩ) from Q1's gate to GND — present. Without this, the buzzer
      can chirp on power-up before firmware sets D9 low.
- [ ] Buzzer is tapped from SYS_5V (post-C1), not 3V3 — per the wiring
      diagram's `C1 -. "SYS_5V tap" .-> BZ`.
- [ ] Q1's source ties to the common GND bus.

## 5. Deployment channel (D6 → gate resistor → Q2 → burn-wire coil) — NEW, undocumented in the schematic

**`config.h` states outright these two nets are "NOT YET in the schematic."**
`avionics_wiring.md`'s pin-reference tables have no rows for D6 or D7 — don't
treat their absence there as "nothing to check." Verify directly against
`firmware/src/config.h` instead:

- [ ] `PIN_DEPLOY` = D6 (GPIO9 on the underlying ESP32-S3) — confirmed free
      of I²C/SPI/buzzer, not D2/D3 (GPS-reserved), not a strapping pin
      (GPIO0/3/45/46), not native-USB/UART0. Verify the physical wire lands
      on D6 and nowhere else — a swap with the buzzer channel here is a
      real failure mode the symbolic-pin-macro discipline in `config.h` is
      specifically trying to prevent.
- [ ] Gate resistor + pulldown pattern present on this channel too, same as
      the buzzer's R1/R2 (not yet assigned reference designators — call
      them out on the schematic when it's drawn).
- [ ] Deploy MOSFET (Q2, see §0) is *not* the same 2N7000 part as Q1 — confirm
      by reading the part off the board, not by assuming symmetry with the
      buzzer channel.
- [ ] **Bench-only verification, never a live coil on this bench:** with the
      real burn-wire coil disconnected, send `ARM` then `FIRE` over USB
      serial (see `firmware/src/main.cpp`'s `handleSerialCommand`) and
      confirm D6 pulses HIGH for the configured on-time
      (`DEPLOY_ON_TIME_MS`, currently a 1500 ms placeholder — **not an
      empirical spec**, see `config.h`) via multimeter/scope/logic analyzer,
      then goes LOW on its own. Confirm a `STATE` command afterward reports
      the fired latch is set.
- [ ] With the coil connected to a dummy load (never a live striker/cartridge
      on the bench), repeat the pulse-timing check and measure actual
      current draw — this is the number the deploy MOSFET's rating (§0) and
      C1's transient budget both depend on, and it doesn't exist yet
      anywhere in this project.
- [ ] After any bench FIRE test, **power-cycle the board** before it's
      considered flight-clean — `deployment.cpp`'s fired-latch
      (`RTC_DATA_ATTR g_firedLatch`) survives a software/watchdog/brownout
      reset and is only cleared by a cold power-on. `main.cpp` prints a
      boot warning (`"WARNING: deploy latch already set at boot"`) if this
      step was skipped — watch for that line on the serial console after
      every power-up before flight.

## 6. Wireless-arm interlock (D7 → SW2 → R3)

- [ ] SW2 wired per `avionics_wiring.md` #8: one leg to 3V3, other leg to
      `PIN_ARM_INTERLOCK` (D7) **and** to R3 (10 kΩ) to GND. This is an
      external pulldown, not `INPUT_PULLUP` — confirm the topology matches,
      inverting it changes the fail-safe direction on a chafed wire.
- [ ] With SW2 open at boot, confirm no WiFi AP appears (scan for
      `WIFI_AP_SSID` from `config.h` on a phone/laptop) — radio must stay off.
- [ ] With SW2 closed, confirm the AP appears within a few seconds.
- [ ] Opening SW2 again after the AP is up: confirm it goes back down
      (debounced, `WIFI_INTERLOCK_DEBOUNCE_MS`).

## 7. Self-test / boot behavior

Power up with SW1 closed, SW2 open, USB serial monitor attached
(115200 baud):

- [ ] Deploy gate (D6) reads LOW immediately — `deployment_init()` is the
      literal first call in `setup()`, before `Serial.begin()`, so this
      should already be true before any serial output appears.
- [ ] `flight_state_init()` runs a sensor self-test and logger-open check.
      Confirm a pass tone (`BuzzerPattern::SELF_TEST_PASS`) plays, or the
      fail tone if a sensor/SD fault is injected on purpose (e.g.
      unplugging the SD card) — the fail path should also be exercised
      once, not just the pass path.
- [ ] On self-test pass, state transitions to `IDLE_ARMED` — confirm via
      the `STATE` serial command or `/status` once wireless is up.
      **This transition is immediate and automatic — there is no separate
      arm step at this point.** See the pad checklist for why this matters
      for handling discipline once the deploy channel is later connected.
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
      fires deployment regardless of barometer state if the primary
      detector never confirms — getting this wrong in either direction is
      a real deployment-timing risk, not a cosmetic tuning knob.
- [ ] `DEPLOY_ON_TIME_MS` / `DEPLOY_MAX_ON_TIME_MS` — bench-measured against
      the real coil (see §5), not the current 1500 ms / 4500 ms placeholders.

---

## Sign-off

- [ ] Every unchecked "not yet in the BOM/schematic" item in §0 and §5 has
      either been closed out or is explicitly accepted as a known gap for
      this build (bench-only, not for flight).
- [ ] This sled has not yet been mated to a CO2 deployment module or
      airframe — see the CO2 module's own checklist and the pad checklist
      for what comes after this one.

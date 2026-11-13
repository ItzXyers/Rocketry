# Pad / Launch-Day Checklist

Covers the full day-of sequence across all three subsystems: avionics sled,
CO2 deployment module, and RSP4 LaunchControl ground station. Companion to
[`README.md`](README.md), [`../Avionics/avionics_build_checklist.md`](../Avionics/avionics_build_checklist.md),
and [`../CO2 Deployment/co2_assembly_checklist.md`](../CO2%20Deployment/co2_assembly_checklist.md).

Last updated: 2026-08-08; flight-computer deploy channel removed 2026-10-19

> **2026-10-19 — Phoenix ABS 40-43 has no CO2 module and no burn wire.** It
> deploys on the motor's ejection charge, and the flight computer (firmware
> 0.2.3+) is a logging altimeter that fires nothing: there is no deploy
> channel, no fired-latch and no `ARM`/`FIRE` bench command any more. For
> Phoenix, skip every CO2 / burn-wire / cartridge step below (§0's CO2 item,
> the CO2 parts of §1, §2 and §7, and §4 steps 1 and 3). The igniter
> (LaunchControl) steps still apply as written.

---

## 0. Readiness gate — read before scheduling a launch day around this

As designed today, this system is **not fully flight-qualified end to end.**
Two gaps mean this checklist should currently be run as a **dry-rehearsal**
(no live igniter, no pierced/live CO2 cartridge) until they close:

- [ ] **The igniter firing circuit has no schematic yet.** `config.py`'s
      pin numbers/polarity for `FIRE_PIN`, `ARM_SENSE_PIN`, and
      `CONTINUITY_PIN` are explicitly unconfirmed against real hardware
      (`LaunchControl/README.md`'s "Hardware contract"). Don't trust an
      arm-sense or continuity reading against a live igniter until the
      real circuit is built and these are confirmed.
- [ ] **The CO2 mechanism cannot be assembled as currently modeled** — see
      `co2_assembly_checklist.md` §1 (no bore in the retaining collar, no
      fitted spring, backpressure at the collar joint unresolved). Do not
      stage a real cartridge in this module until that section is clear.
- [ ] **Placeholder credentials.** `WIFI_AP_SSID`/`WIFI_AP_PASSWORD` in
      `firmware/src/config.h` and `AP_SSID`/`AP_PASSWORD` in
      `LaunchControl/config.py` (plus `network/*.conf` on the Pi) must be
      changed from their shared defaults before flying anywhere another
      board might be nearby, or before any field use at all.
- [ ] **Bench-tested, not just written.** `ignition.py`'s arm/fire/cutoff
      state machine has been run against a dummy load (LED+resistor, never
      a live igniter) with the hard-cutoff timing confirmed on a
      scope/multimeter, per `LaunchControl/README.md`'s bench-testing section.

Everything below assumes the sled itself passed
[`avionics_build_checklist.md`](../Avionics/avionics_build_checklist.md) at
some point before today — this doc doesn't re-derive that.

---

## 1. Before leaving for the range

- [ ] **LaunchControl fired-latch cleared.** (The flight computer has had no
      fired-latch since its deploy channel was removed 2026-10-19.)
  - LaunchControl: `state/fired.latch` on disk, cleared only by
    `scripts/clear_fired_latch.py` (an explicit operator action — nothing
    in the webapp can clear it). Run it and confirm no boot warning about
    an already-set latch on the Pi's log.
- [ ] **C1 fitted, or the transient bench-verified.** Confirmed present on
      the sled per `avionics_build_checklist.md` §1/§0 — do not rely on
      memory that "it was fine last time," verify it's the board actually
      going today.
- [ ] Charge/verify both batteries: flight computer's LiPo, and the Pi's
      power source. Flight computer battery **unplugged** for transport:
      there is no power switch, plugging the battery in powers the bay.
- [ ] Fired-latch step above re-confirmed **after** any bench testing done
      today, not just once this morning — an `ignition.py` dummy-load test
      sets it.
- [ ] Flight computer flash has room: `LOGS` on the USB console (or
      the Logs card at `http://192.168.4.1/`) shows at least 5 MB free. Old
      logs pulled (`DUMP n`, or Download on the page) and backed up, then
      deleted (`DEL n`, Delete on the page, or `FORMAT YES` to erase all). Below 5 MB free the boot self-test fails.
- [ ] Recovery hardware (parachute, shock cord, CO2 module's *fresh* line
      and inspected coil per `co2_assembly_checklist.md` §2) packed
      separately from the pre-armed state — the reload procedure happens
      at the range, not before, per that doc's step ordering.

## 2. At the range, before going to the pad

- [ ] LaunchControl Pi powered up, phone connected to its hotspot
      (`AP_SSID`), webapp reachable.
- [ ] `iw phy0 info` AP+STA concurrency spot-check done at least once for
      this specific Pi/kernel combination (`LaunchControl/README.md`'s
      "Radio topology") — not required every launch day once confirmed
      stable on a given Pi, but confirm it's been done at all for this unit.
- [ ] CO2 module reload/service procedure completed per
      `co2_assembly_checklist.md` §2, **including the burn-wire continuity
      check (step 13)** — done here, at the range, not assumed from a prior
      session.
- [ ] Sled powered up (battery plugged in). Confirm self-test pass tone.
      The ground-support WiFi AP comes up right after boot and stays up
      until `/arm` or launch.
- [ ] **Do not connect the CO2 module's burn-wire leads to the sled's
      deploy channel yet.** That connection is deliberately one of the
      last steps in this checklist (§4) — see the ordering rationale below.

## 3. Igniter continuity (LaunchControl)

- [ ] Igniter installed per motor manufacturer instructions, **arm switch
      in the firing circuit physically open.**
- [ ] LaunchControl webapp continuity indicator reads OK
      (`continuity.continuity_ok()` — HIGH from the firing circuit's own
      low-current check). If it reads not-OK: **do not troubleshoot by
      bypassing the continuity gate** — check the igniter connection
      itself.
- [ ] Confirm arm-sense reads OPEN in the webapp while the physical arm
      switch is open — this is advisory/UI-only (the switch itself lives
      in the igniter's high-current path in hardware and is what actually
      prevents firing), but a wrong reading here means the UI can't be
      trusted for the rest of the sequence either.

## 4. Vehicle to the pad — ordering matters here

**Why this order:** `flight_state_init()` puts the sled into `IDLE_ARMED`
automatically at boot, right after self-test passes — there is no separate
"arm" step in the firmware at that point. Launch detection is a 3.0 g bump
sustained 100 ms (`LAUNCH_ACCEL_THRESHOLD_G` / `LAUNCH_ACCEL_CONFIRM_MS`).
The flight computer fires nothing (no deploy channel since 2026-10-19), so a
false launch can't deploy anything — but it does latch the Wi-Fi AP off and
run the flight state machine, so the sled has to be power-cycled before it
can be re-armed. **Any hard jolt above 3 g for a tenth of a second on the pad
means a stand-down and power-cycle.** (On a CO2 / burn-wire vehicle this
ordering also kept the coil disconnected until the last moment; that
firmware path no longer exists.)

1. [ ] Carry the vehicle to the pad and mount it on the rail/rod.
       **Burn-wire leads still disconnected at this point.**
2. [ ] Vehicle vertical, undisturbed, on the rail.
3. [ ] **Now** connect the CO2 module's burn-wire leads to the sled's
       deploy channel. This is the last physical handling step before the
       wireless-arm sequence below.
4. [ ] **From this point on, do not handle, bump, or jar the vehicle.** If
       it needs to come back off the rail for any reason after this step,
       treat that as a full stand-down: disconnect the burn-wire leads,
       power-cycle the sled (clears nothing dangerous by itself, but
       re-establishes a known `IDLE_ARMED` state from a clean self-test),
       and restart this section from step 1.
5. [ ] Confirm the flight computer shows as reachable in the LaunchControl
       status view (its AP has been up since boot). If it isn't, power-cycle
       the sled by unplugging and replugging the battery.

## 5. Wireless arm (flight computer re-zero, via LaunchControl)

- [ ] Confirm the vehicle has been vertical and undisturbed since §4 step 2
      — `/arm` re-captures the pad baro/accel baseline
      (`sensors_capturePadBaseline()`), so arming before the vehicle is in
      its final launch attitude re-zeros against the wrong baseline.
- [ ] Trigger `/arm` from the LaunchControl webapp, or from a phone on the
      flight computer's own console at `http://192.168.4.1/` (ARM button).
      The AP takes one client at a time, so use one or the other.
- [ ] **Expect the connection to drop ~500ms after a successful response.**
      `fc_client.post_arm()` reports this as `ambiguous=True`, not a
      failure — the AP is designed to drop shortly after `/arm` succeeds.
      A dropped connection here most likely means it worked.
- [ ] **Do not retry `/arm` on an ambiguous/dropped result.** A successful
      `/arm` latches the wireless radio off for the rest of this power
      cycle — there is no AP left to retry against. If the outcome is
      genuinely unclear (not just the expected drop), the only recovery is
      a full stand-down: disconnect the burn-wire leads, power-cycle the
      sled, and restart from §4 step 1.
- [ ] Confirm by ear that arm succeeded before proceeding — don't proceed
      on "probably fine." Sled buzzer (firmware 0.3.0+):
      - one short chirp right away = `/arm` received, re-zeroing (keep still ~5 s)
      - **beep-beep-beeeep**, once = ARMED (then silent until landing)
      - **five fast blips** = arm REFUSED (wrong state or sensor self-test
        failed); nothing changed, the AP stays up — read the reason on the
        page and fix before retrying

## 6. Final arm and fire (LaunchControl, igniter channel)

Independent of §5 — this section only concerns the SRB igniter, and never
touches the flight computer (`ignition.py` and the flight firmware are fully
separate systems; the flight computer has no deploy channel at all since
2026-10-19).

- [ ] All personnel clear to the range's mandated safe distance.
- [ ] Physical arm switch (igniter's high-current path) closed by the
      designated operator only.
- [ ] LaunchControl `request_arm()` — confirm it succeeds (checks arm-sense
      closed AND continuity OK; both must be true). If either fails,
      **stand down and troubleshoot the igniter circuit** — do not proceed
      to fire on a failed arm.
- [ ] **Arm window is 15 s** (`ARM_WINDOW_S`). If the countdown/hold runs
      past that, the arm token has expired — re-arm, don't just press fire
      again. Both arm-sense and continuity are re-checked at the moment of
      fire regardless, so a stale window or a switch bumped open during the
      hold both fail safely, but re-arming is the correct response, not
      retrying fire.
- [ ] Countdown per range procedure.
- [ ] Fire command issued.
- [ ] Confirm ignition visually/audibly. If no ignition within a few
      seconds: **treat as a misfire, not a retry candidate** — the fire
      channel is one-shot (`fired` latch sets the instant the fire GPIO is
      energized, regardless of whether ignition actually occurred). Follow
      range misfire procedure (mandatory wait period before approaching the
      pad) before touching the igniter circuit.

## 7. Post-flight / recovery

- [ ] Once the log is pulled, find the `APOGEE_CONFIRMED` (or
      `APOGEE_TIMEOUT`) event and compare it with when the motor's ejection
      charge actually fired (accel spike in the log, or video). A large gap
      means the motor delay is wrong for this vehicle — fix it before the
      next flight.
- [ ] The LaunchControl fired-latch will read "set" after a normal flight —
      that's expected, not a fault. Clear it per
      §1 before the *next* launch day, not immediately at the field unless
      re-flying same-day.
- [ ] Spent CO2 cartridge removed and confirmed vented before the module is
      reloaded (see `co2_assembly_checklist.md` §2, step 2).
- [ ] Pull the log off the flight computer's internal flash and back it up:
      power-cycle the sled (the AP is off after launch), then `GET /log?n=`
      over Wi-Fi or `DUMP n` on USB. Then `DEL n` to free the space.

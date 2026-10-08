# Pad / Launch-Day Checklist

Covers the full day-of sequence across all three subsystems: avionics sled,
CO2 deployment module, and RSP4 LaunchControl ground station. Companion to
[`README.md`](README.md), [`../Avionics/avionics_build_checklist.md`](../Avionics/avionics_build_checklist.md),
and [`../CO2 Deployment/co2_assembly_checklist.md`](../CO2%20Deployment/co2_assembly_checklist.md).

Last updated: 2026-08-08

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

- [ ] **Both fired-latches cleared.** These are two independent latches,
      cleared two different ways — check both:
  - Flight computer: `deployment.cpp`'s `RTC_DATA_ATTR g_firedLatch`
    survives software/watchdog/brownout resets, cleared only by a **cold
    power-on**. Power up the sled and watch the serial console for
    `"WARNING: deploy latch already set at boot"` — if it prints, this
    board fired since its last full power-cycle and must not fly without
    one.
  - LaunchControl: `state/fired.latch` on disk, cleared only by
    `scripts/clear_fired_latch.py` (an explicit operator action — nothing
    in the webapp can clear it). Run it and confirm no boot warning about
    an already-set latch on the Pi's log.
- [ ] **C1 fitted, or the transient bench-verified.** Confirmed present on
      the sled per `avionics_build_checklist.md` §1/§0 — do not rely on
      memory that "it was fine last time," verify it's the board actually
      going today.
- [ ] Charge/verify both batteries: flight computer's LiPo, and the Pi's
      power source. Confirm SW1 can fully power down the sled between now
      and pad arrival (battery isolated for transport).
- [ ] Both fired-latches step above re-confirmed **after** any bench
      testing done today, not just once this morning — a bench `FIRE`
      test on the avionics serial console or an `ignition.py` dummy-load
      test both set their respective latches.
- [ ] microSD card has free space and isn't the card from the last flight
      still full of old data (or is, and that's backed up first).
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
- [ ] Sled powered up (SW1 closed), SW2 **not pressed**. Confirm self-test
      pass tone. Confirm no WiFi AP visible yet (SW2 gates it).
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
sustained 100 ms (`LAUNCH_ACCEL_THRESHOLD_G` / `LAUNCH_ACCEL_CONFIRM_MS`),
and once `COAST` is entered, `MAX_TIME_TO_APOGEE_MS` (20 s, currently a
STARTING DEFAULT) is an **unconditional backstop that fires the deploy
channel regardless of barometer state** if the primary apogee detector never
confirms. In plain terms: **any hard jolt above 3 g for a tenth of a second,
after the burn-wire is connected, can end with the deploy channel firing
about 20 seconds later, with nothing left to stop it.**

1. [ ] Carry the vehicle to the pad and mount it on the rail/rod.
       **Burn-wire leads still disconnected at this point.**
2. [ ] Vehicle vertical, undisturbed, on the rail.
3. [ ] **Now** connect the CO2 module's burn-wire leads to the sled's
       deploy channel. This is the last physical handling step before the
       interlock/arm sequence below.
4. [ ] **From this point on, do not handle, bump, or jar the vehicle.** If
       it needs to come back off the rail for any reason after this step,
       treat that as a full stand-down: disconnect the burn-wire leads,
       power-cycle the sled (clears nothing dangerous by itself, but
       re-establishes a known `IDLE_ARMED` state from a clean self-test),
       and restart this section from step 1.
5. [ ] Press and hold SW2 (wireless-arm interlock button) for ~2 s, then
       release (must be 1–5 s). Confirm the ground-support AP appears in the
       LaunchControl status view within a few seconds.

## 5. Wireless arm (flight computer re-zero, via LaunchControl)

- [ ] Confirm the vehicle has been vertical and undisturbed since §4 step 2
      — `/arm` re-captures the pad baro/accel baseline
      (`sensors_capturePadBaseline()`), so arming before the vehicle is in
      its final launch attitude re-zeros against the wrong baseline.
- [ ] Trigger `/arm` from the LaunchControl webapp.
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
- [ ] Confirm via whatever last status the webapp captured (or a visual/audio
      cue from the sled, if defined) that arm succeeded before proceeding —
      don't proceed on "probably fine."

## 6. Final arm and fire (LaunchControl, igniter channel)

Independent of §5 — this section only concerns the SRB igniter, and never
touches the flight computer's deploy channel (`ignition.py` and
`deployment.*` are fully separate systems; wireless FIRE for the CO2 channel
does not exist anywhere in this project).

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

- [ ] Confirm `deployment_hasFired()` / the logged `DEPLOY_FIRE` event once
      the sled is recovered and its log pulled — cross-check against
      observed parachute deployment. A fired latch with no observed
      deployment (or vice versa) is worth investigating before the next flight,
      not waving off.
- [ ] Both fired-latches (flight computer + LaunchControl) will read "set"
      after a normal flight — that's expected, not a fault. Clear both per
      §1 before the *next* launch day, not immediately at the field unless
      re-flying same-day.
- [ ] Spent CO2 cartridge removed and confirmed vented before the module is
      reloaded (see `co2_assembly_checklist.md` §2, step 2).
- [ ] Pull the microSD card / log and back it up before it's overwritten by
      a future flight.

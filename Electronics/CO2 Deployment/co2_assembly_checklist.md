# CO2 Deployment Module — Assembly & Reload Checklist

Companion to [`co2_deployment_module.md`](co2_deployment_module.md) and
[`co2_trigger_release_mechanism.md`](co2_trigger_release_mechanism.md).

**This mechanism is not flight-worthy yet.** Section 1 lists why, straight
from the design docs' own open items. Don't skip to Section 2 on the
assumption those are minor — several are "cannot physically assemble as
currently modeled," not "needs tuning."

Last updated: 2026-08-08

---

## 1. Design blockers — must close before this checklist means anything

These are pulled directly from `co2_deployment_module.md`,
`co2_trigger_release_mechanism.md`, and
[`../Integrated Bay Assemblies/integrated_ring_av_co2_bay_30mm.md`](../Integrated%20Bay%20Assemblies/integrated_ring_av_co2_bay_30mm.md).
Check each off only when the underlying CAD/hardware has actually changed —
not when you've just re-read and agree it's a problem.

- [ ] **Retaining collar has no bore.** `co2mod_retaining_collar` is
      modeled as a solid disc (verified: one distinct vertex radius, 6.2mm).
      The striker pin physically cannot pass through it as currently
      modeled or printed. **This blocks final assembly outright** — higher
      priority than anything else on this list.
- [ ] **Pin tail taper admits no coaxial spring at any diameter.** The
      pin's Z92–113 tail is a single cone (r 4.5→1.8mm); the spec'd spring
      needs a constant-radius guide rod, not a taper. Needs the guide-rod
      redesign described in `co2_trigger_release_mechanism.md` before a
      real spring can be fitted, not just a smaller spring.
- [ ] **The specced drive spring does not fit the space currently modeled
      for it.** Stress-driven sizing (302 stainless, 1.2mm wire, 27 active
      coils) landed at ~55mm free length; the CAD currently reserves ~4mm
      (Z92.5–96.5). This is not a rounding error.
- [ ] **No aft structure exists to seat the spring's fixed end.** Nothing
      is modeled from Z94 (end of the current housing) out to the pin's new
      aft end (~Z135 once the guide-rod redesign lands). An aft cap/extension
      needs designing, not just printing from what exists today.
- [ ] **Puncture force has never been measured.** Every number downstream
      of it (spring stored energy, wire stress, line diameter) is a
      literature-analog estimate, not a spec. Run the named test — press a
      sharpened rod of the tip's geometry into a spent cartridge's pierce
      pad on a force gauge, record peak force — before trusting any of the
      current spring/line sizing as final.
- [ ] **Cartridge backpressure after piercing is unresolved and flagged
      safety-relevant.** No seal is specified between the pierced cartridge
      and the housing bore. Worst case (gas reaches the full Ø9mm shaft):
      ~628N at the housing↔collar joint (Joint 2), trying to push a
      **hand-unscrewed, 3mm-thread-engagement** collar off its threads.
      This needs an explicit decision (sealed vs. vented-through-the-pin-bore)
      before the mechanism is flight-worthy — not something this checklist
      can wave through.
- [ ] **Tip material sourced, not just specified.** Hybrid pin (printed
      body + hardened metal tip insert) is the current spec — confirm an
      actual tip (bike CO2 inflator pin, hardened needle, or hand-pointed
      dowel — see `co2_trigger_release_mechanism.md`'s sourcing list) is in
      hand and has been through the same puncture test as above, not
      assumed to work.
- [ ] **Retaining line on hand is the decided ⌀0.30mm Dyneema/Spectra**, not
      the ⌀0.8mm placeholder still shown in the CAD. Confirm the specific
      product's cinched/knotted breaking strength against a datasheet, not
      just the general 40-50%-of-straight-strength estimate.
- [ ] **Burn-wire driver circuit exists and is bench-verified.** No MOSFET
      is specified for this channel in the avionics BOM yet — see
      [`../Avionics/avionics_build_checklist.md`](../Avionics/avionics_build_checklist.md)
      §0/§5. Don't wire a real coil to the flight computer until that's closed.
- [ ] Chamber wall thickness vs. cartridge fit, and any seal/gasket at the
      base cap and neck joints, verified against real geometry — not
      reasoned from OD figures alone (`co2_deployment_module.md` open items
      3–4).

**If any box above is unchecked, treat everything past this point as a
dry-fit / procedure-rehearsal exercise with an inert or absent cartridge —
not a flight-ready packing procedure.**

---

## 2. Per-cycle reload / service procedure

Adapted from `integrated_ring_av_co2_bay_30mm.md`'s "Full reload / service
procedure." This mechanism is one-shot per flight — line replaced, spring
re-cocked, coil inspected — every single time, not just after a misfire.

**Before touching the module:** confirm the avionics sled's deploy channel
is disconnected or the whole system is unpowered. Never work this procedure
with the burn-wire coil live-wired to a powered flight computer — see the
avionics checklist's §5 sign-off on the fired-latch and power-cycle discipline.

1. [ ] **Unscrew Joint 1** (chamber ↔ housing, ~M14×1.5, Z68) — pulls the
       whole housing/striker assembly off the chamber.
2. [ ] **Remove the spent cartridge** from the now-open chamber neck.
       Confirm it's actually spent (vented) before treating it as inert —
       do not assume.
3. [ ] **Inspect the chamber bore and vent ports** (3× ⌀2mm at Z64, 120°
       apart) for CO2 residue/moisture/corrosion before loading a fresh
       cartridge.
4. [ ] **Insert a fresh, unpierced cartridge** into the chamber neck. An
       unpierced cartridge is inert — this is the design's own stated
       rationale for ringing it with electronics — but confirm it seats
       fully and isn't already damaged/dented at the pierce pad.
5. [ ] **Unscrew Joint 2** (housing ↔ collar, ~M13×1.5, Z92) — spring and
       the pin's exposed end come out with the collar, opening the housing
       into the trigger cluster.
6. [ ] **Inspect the nichrome coil** for damage (breaks, deformation from
       the previous burn) — replace if in doubt, don't reuse a
       visibly-degraded coil.
7. [ ] **Inspect the pin's neck/shoulder catch** (Ø3.6mm neck, Z87–89.8)
       and tip for wear or deformation from the previous puncture cycle.
8. [ ] **Pull the striker pin back to its cocked position and hold it** —
       this is a manual, held operation; the mechanism has no ratchet or
       latch of its own at this stage.
9. [ ] **Thread a fresh retaining line** through `anchor_post_a` /
       `anchor_post_b` and cinch it around the pin's neck so it catches
       against the Ø9mm shoulder at Z89.8–90. Confirm the line is the
       specced ⌀0.30mm Dyneema (see §1), not a substitute, and that the
       cinch knot is seated — a slipped knot here is a silent single point
       of failure between "armed" and "safe."
10. [ ] **Release the pin slowly** onto the line, confirming it holds at
       the cocked position under spring tension before letting go
       entirely.
11. [ ] **Reassemble Joint 2** (collar back on) — confirm full thread
       engagement, not just started.
12. [ ] **Reassemble Joint 1** (housing back on the chamber) — same, full
       engagement.
13. [ ] **Continuity-check the burn-wire leads** end-to-end (lead → coil →
       lead) with a multimeter on the bench, before connecting to the
       flight computer's deploy channel. This is the CO2-module-side
       equivalent of the igniter continuity check in the pad checklist —
       do it here, not for the first time at the pad.
14. [ ] **Do not connect the leads to a powered flight computer's deploy
       channel until the module is fully reassembled and mounted** in its
       final flight position. See the pad checklist for exactly when this
       connection happens in the overall sequence — it is deliberately one
       of the last steps before the rocket goes vertical, not something
       done on the workbench.

---

## 3. Storage / transport between sessions

- [ ] Unpierced cartridges stored per their own handling guidance (cool,
      dry, away from heat sources) — an unpierced cartridge is a sealed
      pressure vessel, treat it like one in storage, not just in the bay.
- [ ] Cocked assemblies (pin held by a line, spring under tension) are not
      left cocked in storage between sessions unless actively staged for a
      launch that session — reduces both stress-relaxation exposure on the
      spring (already a design concern at the cocked position, see
      `co2_trigger_release_mechanism.md`) and the consequence window of an
      accidental release.
- [ ] Spare retaining line and coil stock kept with this module's kit, not
      general workshop stock — wrong-diameter line substituted under time
      pressure at the field is a real failure mode this list exists to
      prevent.

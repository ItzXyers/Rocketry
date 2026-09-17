# Integrated AV + CO2 Bay — 30mm ID, Ring-Mounted Design

Last updated: 2026-08-04

**2026-08-19: the avionics half of this design was built and installed into
a real airframe** — `SampleRocketABS33-36`, world Z85–186.5 (see
`../../SampleRocketABS33-36/Design-Notes-AvBayIntegration.md` for the full
build). The board-tier layout below (ring around a ⌀20.5 core, 0/90/180/270°,
two tiers) carried over essentially unchanged, just against a real ⌀31 tube
(0.5mm more radial margin than the ⌀30 this doc verified against) instead of
the generic ⌀32 reference tube modeled here. The CO2 chamber this doc
describes was **not** carried over — the boards now ring a plain printed
`AvBay_Mandrel` tube instead, since the CO2 module's three open blockers
below (no bore in the retaining collar, spring/aft-cap redesign, undecided
backpressure boundary) are still unresolved. A **77mm** envelope is
reserved aft of the electronics for the CO2 module to slot into once those
are closed out — it will need to fit `co2mod_chamber_neck` through
`co2mod_striker_pin` (whatever survives the redesign) into that space,
replacing the current interim motor-ejection gas path. **(Updated
2026-08-26: resized from 52mm to 77mm** — using the conservative end of
this doc's own "adds ~20-25mm to the 153.5mm headline total length" note
on the still-unmodeled drive-spring aft cap (open item 4 below) — **when a
dedicated parachute bay was added forward of this envelope. See
`../../SampleRocketABS33-36/Design-Notes-ParachuteBay.md`.** The three
real blockers below are unaffected by that resize.)

## Overview

Combines the avionics sled and CO2 deployment module into a single 30mm ID
(32mm OD) tube section, rather than two separate bays. The key idea: an
**unpierced CO2 cartridge is an inert sealed vessel**, so it's safe to ring
with electronics. The actual hazard boundary is the pierce point (cartridge
neck), not the far end of the whole trigger mechanism — so the bulkhead sits
there, not after the striker.

Layout, nose-ward is +Z:

| Zone | Z range | Contents |
|---|---|---|
| Battery pocket | −40.5 to 0 | `battery_620mah.001` (real dims, see below), `usb_charger` stacked on top |
| Chamber base | 0 – 2 | `co2mod_chamber_base` |
| Chamber body (electronics ring) | 2 – 60 | `co2mod_chamber_body` + `co2_cartridge_8g_REAL`; 8 boards ring this section in 2 tiers |
| Bulkhead collar | 58 – 61 | `bulkhead_collar` — annular, bonded to chamber OD, sealed to tube ID, 2 lead feedthroughs |
| Chamber neck (vent + Joint 1) | 60 – 68 | `co2mod_chamber_neck`, pierce point, 3× vent ports, threaded socket at 65–68 |
| Housing (Joint 1 spigot, Joint 2 socket) | 68 – 94 | `co2mod_housing`, `housing_thread_spigot_aft` (65–68), bored socket (89–92) |
| Housing boss (lead feedthrough) | 85.8 – 90.8 | `co2mod_housing_boss` — added 2026-08-05, see below |
| Trigger cluster | 86.4 – 90.5 | anchor posts, retaining line (z=88.0), nichrome coil, leads |
| Retaining collar (Joint 2 spigot) | 92 – 94 | `co2mod_retaining_collar`, `collar_thread_spigot` (89–92) |
| Drive spring | 92 – 97 | `co2mod_drive_spring` |
| Striker pin (cocked/rest position) | 82 – 113 | `co2mod_striker_pin` |

**Total length: 153.5mm** (Z −40.5 to 113), down from 223.4mm for a naive
nose-to-tail join of the two original subsystems.

## Electronics ring (chamber body, Z2–58)

8 of 9 boards ring the sealed chamber (OD 20.5mm) in two 4-board tiers at 90°
spacing, sized so a flat board's *corners* — not its center — clear the tube
ID (sagitta: `d_outer = sqrt(R_tube² − (W/2)²)`):

| Tier | Z range | Boards (0/90/180/270°, tier 2 has a spare slot) |
|---|---|---|
| 1 | 2 – 23.59 | nano_esp32, microsd_reader, pololu_reg, mosfet |
| 2 | 25.59 – 44.59 | bmp388, *(spare)*, adxl375, buzzer |

Verified in real cylindrical (r, θ, z) coordinates, not estimated: worst-case
outer margin 0.55mm to the 30mm ID, worst-case inner margin 0.36mm to the
20.5mm chamber OD (buzzer, 4mm thick, is the tightest fit — worth confirming
against its real datasheet tolerance).

**Battery does not fit the ring at any reasonable margin** — even with zero
clearance to the tube ID and an aggressively thinned chamber wall, it barely
closes. Real battery dimensions are 40.5 × 20 × 8.5mm (assumed L×W×T —
confirm this ordering), which also exceeds the 30mm tube ID outright in its
long dimension, so it must run axially. It and the USB charger (stacked
0.8mm off its face) live in a dedicated pocket ahead of the chamber instead,
adding 40.5mm of otherwise-unused length. A slimmer cell (~3mm thick) would
let the battery ring the chamber like everything else and remove this pocket
entirely — not pursued here, flagged as an open option.

## Vent ports

3× ⌀2mm radial ports through `co2mod_chamber_neck`'s wall at Z64, 120° apart,
connecting the pierced cartridge's neck to the outer wet-side annulus
(already isolated from the electronics by the bulkhead). This is the actual
ejection gas path — without it, punctured gas has nowhere to go.

**Repositioned 2026-08-05** to clear the bulkhead's 2 nichrome lead
feedthroughs (see below), which sit at θ≈80°/100° and whose leads run
nose-ward through this same wet-side annulus to the trigger cluster — a vent
jet aimed near that angular column risked impinging on the lead insulation
or its potting joint. Rotated `co2mod_chamber_neck` −30° about Z (a plain
axisymmetric bore otherwise, so this has no other effect): ports now at
30°/150°/270° instead of 60°/180°/300°. Worst-case clearance to the lead
columns went from 20° (60° port vs. 80° lead) to 50° (30° vs. 80°, 150° vs.
100°); the third port sits 170° away either way. 120° spacing preserved.

## Trigger cluster lead routing — fixed 2026-08-05

The nichrome coil's leads were originally modeled climbing axially up
through the space the striker pin's own shaft occupies — not buildable,
since fixed wiring can't share a channel with a moving pin. Full diagnosis,
fix, and verification now live in the dedicated
[`co2_trigger_release_mechanism.md`](../CO2%20Deployment/co2_trigger_release_mechanism.md) /
`.blend` (the mechanism was split into its own file to iterate on it in
isolation; this integrated file received the identical, re-verified fix).
Summary: added `co2mod_housing_boss` (an annular ring, r=8→13mm,
Z85.8–90.8) so the leads have real wall thickness to exit through radially
(θ=40°) instead of running parallel to the pin, and moved the retaining
line/coil down (line to Z=88.0, coil to Z86.4–88.8) so nothing with r<6.5mm
overlaps `collar_thread_spigot`'s r=5.0–6.5mm annulus at Z89–92. Costs zero
additional axial length — total combined length is still 153.5mm.

Two pre-existing defects were found (not caused by this fix, not yet
fixed): `co2mod_retaining_collar` is a solid disc with no bore — the pin
cannot physically pass through it as modeled — and the pin's Z92–113 tail
taper likely intersects the drive spring's modeled radius. Both are
detailed in `co2_trigger_release_mechanism.md`.

## Threaded service joints

Both modeled as a plain engagement cylinder (spigot fits inside socket,
verified diameters and clearances) — **not literal helical thread
geometry**. Real threads get cut with a tap/die against these diameters,
not printed from this mesh.

| Joint | Location | Nominal spec | Engagement | Purpose |
|---|---|---|---|---|
| 1 — chamber ↔ housing | Z65–68 | ~M14×1.5 | 3mm | Unscrew the whole housing/striker assembly off the chamber for cartridge access |
| 2 — housing ↔ collar | Z89–92 | ~M13×1.5 | 3mm | Unscrew just the collar to reach the trigger cluster, without detaching from the chamber |

Both sockets carry a 10mm clear bore for the 9mm striker pin to pass
through. Joint 2's socket (13.2mm ID) was checked against the anchor posts
(which sit further out radially, r 8.06–11.05mm) — no interference.

## Access decision: nose-end loading, not base-end

Originally planned to load the cartridge from the base end. Reversed once
the battery pocket (sized to real dimensions) ended up blocking that exact
path. Settled on nose-end loading instead, since the striker has to be
serviced every flight anyway (nichrome burn-wire release is one-shot — line
replaced, spring re-cocked each time) — so cartridge swap and striker
service share one access point instead of needing a second removable
mechanism at the aft end. **Consequence: the aft end (battery + electronics
ring) is now a permanent, sealed structure, never opened in normal use.**

## Full reload / service procedure

1. Unscrew Joint 1 (chamber ↔ housing, Z68) — pulls the whole
   housing/striker assembly off the chamber.
2. Slide the spent cartridge out of the now-open chamber neck; push a new
   one in.
3. Unscrew Joint 2 (housing ↔ collar, Z92) — the spring and the pin's
   exposed end come out with the collar, opening the housing straight into
   the trigger cluster.
4. Pull the striker pin back against the spring to its cocked position and
   hold it there.
5. Thread a fresh retaining line through `anchor_post_a` / `anchor_post_b`
   and cinch it around the pin's neck (Z87–89.8, Ø3.6mm) so it catches
   against the Ø9mm shoulder at Z89.8–90 — same path as the burned line.
   This is a plain reduced-diameter neck, not a notch or hole; nothing
   needs to be drilled into the pin.
6. Check the nichrome coil for damage.
7. Reassemble: collar back onto Joint 2, then housing back onto Joint 1.

## Open items — not resolved, flagged deliberately

1. **Bulkhead bore and lead holes are static bonded/potted joints, not
   sliding seals** — the actual thing holding back nose-ward gas pressure.
   Real hardware work (epoxy joint rated for the pressure, verified over
   vibration/thermal cycling), not represented by the geometry alone.
2. **Battery dimension ordering (40.5×20×8.5 = L×W×T) is assumed**, not
   confirmed against a datasheet.
3. **USB charger, arming switch, and microSD access all need tube-wall
   cutouts**, and the buzzer needs a sound port — none of the current
   angular slots were chosen with feasible cutout locations in mind.
4. **Drive spring sized on paper 2026-08-07, not yet applied to CAD**
   (Blender wasn't reachable that session) — see
   [`co2_trigger_release_mechanism.md`](../CO2%20Deployment/co2_trigger_release_mechanism.md#drive-spring-and-final-line-sizing--decided-2026-08-07).
   302 stainless, 1.2mm wire, ~55mm free length — confirms the collision
   flagged below isn't a sizing mistake, no coaxial spring fits the current
   Z92–113 taper at any diameter; needs a guide-rod redesign of the pin
   tail plus a new aft cap structure (Z94→~135) that doesn't exist yet in
   any part list. Adds ~20-25mm to the 153.5mm headline total length below
   — treat that number as stale until the aft cap is modeled. Retaining
   line diameter is now also closed out (⌀0.30mm Dyneema, same doc). One
   real open dependency remains: the puncture-force number this was sized
   against is a literature estimate, not a measurement — see that doc's
   "Load case" section for the specific bench test needed.
4c. **Cartridge backpressure on the pin after piercing was never
   accounted for anywhere in this project — found 2026-08-07 while sizing
   the spring, flagged as safety-relevant.** No seal is specified between
   the pierced cartridge and the housing bore (open item 4 in
   `co2_deployment_module.md`); if gas reaches the full Ø9mm shaft, back-
   of-envelope force at the housing↔collar joint's ~10mm clear bore is
   ~628N trying to push the hand-unscrewed retaining collar (Joint 2, 3mm
   thread engagement) off its threads. Full reasoning in
   `co2_trigger_release_mechanism.md`. Not solved there — needs an explicit
   decision on the pressure boundary (sealed vs. vented-through-the-pin-bore)
   before this mechanism is flight-worthy.
4b. **`co2mod_retaining_collar` has no bore — it's a solid disc** (verified:
   exactly one distinct vertex radius, 6.2mm). The striker pin cannot
   physically pass through it as modeled. This blocks final assembly
   outright and should be treated as higher priority than the spring
   question above. Found 2026-08-05 while fixing the trigger-cluster lead
   routing (see `co2_trigger_release_mechanism.md`); unrelated to that fix.
5. **Chamber wall thickness / cartridge bore fit** was reasoned from OD
   figures (20.5mm chamber vs 18mm cartridge → ~1.25mm nominal wall), not
   verified against actual mesh geometry — carried over from an open item
   in `co2_deployment_module.md`, still unresolved here.
6. **Correction to `co2_deployment_module.md`:** that doc states no spring
   or stored-energy part exists in the scene. `co2mod_drive_spring` *is*
   present in `co2_deployment_module.blend` (Z92–97 in this design) — that
   open item appears to be resolved/outdated, worth reconciling.

## Files

- `integrated_ring_av_co2_bay_30mm.blend` — full CAD assembly
- `integrated_ring_av_co2_bay_30mm_reference_assembly.stl` — combined mesh export

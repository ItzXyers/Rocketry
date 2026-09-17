# CO2 Striker Release Mechanism — Standalone Assembly

Last updated: 2026-08-05

## Why this file exists

Split out of `integrated_ring_av_co2_bay_30mm.blend` to isolate and fix a
real routing defect: the nichrome coil's leads were originally modeled
climbing axially (parallel to +Z) from the anchor posts toward the top of
the housing, which put them directly inside the space the striker pin's own
solid shaft occupies. There is no clear axial channel for fixed wiring
inside this housing — the pin fills nearly the whole bore. Leads must exit
**radially through the housing wall**, not run alongside the pin.

This file holds just the release mechanism (housing, pin, anchor posts,
retaining line, nichrome coil, leads, retaining collar, drive spring, both
thread spigots) plus a wireframe 30mm-ID/32mm-OD tube reference for scale.
The identical fix was also re-applied to `integrated_ring_av_co2_bay_30mm.blend`
so the two files stay in sync — this is the file to iterate on, not a
throwaway extract.

## Pin profile (verified vertex-by-vertex, not estimated)

| Z (mm) | radius (mm) | feature |
|---|---|---|
| 82 | 0.0 | piercing tip (point) |
| 82→87 | 0→1.8 | conical tip taper |
| 87→89.8 | 1.8 | **neck** (Ø3.6mm) |
| 89.8→90 | 1.8→4.5 | shoulder step |
| 90→92 | 4.5 | main shaft (Ø9mm) |
| 92→113 | 4.5→1.8 | tail taper toward the spring |

**The neck + shoulder is the catch feature, and it needed no changes.** A
line cinched around the Ø3.6mm neck can't slip past the Ø9mm shoulder right
above it — that's what actually retains the pin against spring force. No
hole through the pin, then or now. Don't "fix" this later by drilling it.

## The fix

**Housing boss** (`co2mod_housing_boss`, new part): annular ring, r=8→13mm,
Z85.8–90.8, added to the housing's OD at the trigger cluster. Needed for two
reasons: it gives the lead feedthroughs real wall thickness to pass through,
and it gives the anchor posts (which already sit at r up to 11.35mm — past
the plain housing's r=8mm OD) solid material to actually be embedded in,
which they didn't have before. Clears the 30mm tube ID (r=15mm) by 2.0mm.

**Leads** (`co2mod_lead_pos` / `co2mod_lead_neg`, rebuilt): now radial
members, r=5→13mm, at θ=40° from the coil outward through the boss, fixed
Z=87.0mm (pos) and Z=88.4mm (neg). θ=40° was chosen after a 25° first pass
turned out to still clip `co2mod_anchor_post_b` — verified this time with an
actual boolean intersection, not just a bounding-box check.

**Two-part hole inventory** — everything that needs to physically cross the
boundary got a real boolean-cut hole through *both* layers of material it
passes through:
- Lead holes: cut through `co2mod_housing`'s own r=8mm wall *and* through
  the boss (r=8→13mm). Missing the housing-wall cut was caught on the first
  save-and-verify pass — don't skip it if this is ever rebuilt from scratch.
- Anchor-post holes: cut through `co2mod_housing` only (scaled copies of
  each post used as the cutter, for an exact fit). Not cut through the
  boss — the posts are *meant* to be embedded in the boss's solid material,
  that's the point of the boss.
- Retaining-line slot: cut through both housing and boss (scaled copy of
  the line used as cutter), since the line runs all the way out to the
  anchor posts at r≈9.5mm.

**The Z < 89.0mm rule.** `collar_thread_spigot` (Joint 2's engagement pin)
occupies a fixed annulus r=5.0–6.5mm at Z89–92 — verified by direct vertex
sampling (a plain hollow sleeve, inner r=5.0, outer r=6.5). Anything with
r<6.5mm — the line, the coil, both leads — has to stay below Z=89.0mm or it
collides with the spigot. This is why the line moved from its original
Z=89.0 center to Z=88.0, and the coil shifted −1.4mm total from its original
position (now spanning Z86.4–88.8). Both leads (Z87.0, 88.4) were placed
inside this same window from the start.

**Verification method.** After two rounds of missing a collision by hand
(25°→ hit a post, first Z choice → hit the spigot, first boss height → left
the top of each post unsupported), switched to an all-pairs boolean
intersection sweep over every mesh in the file, with an explicit whitelist
of intended contacts (coil↔line, coil↔leads, posts↔line, posts↔boss,
boss↔housing). Final sweep: **zero unexplained collisions.**

Verified margins:
- Boss OD (13mm) to tube ID (15mm): 2.0mm
- Lead inner start (r=5mm) to pin neck (r=1.8mm): ~3.2mm
- Anchor posts fully embedded in boss material (boss now spans Z85.8–90.8,
  posts span Z88.5–90.5 — full bracket, not just the leads' narrower band)

## Materials — decided 2026-08-05

Neither part had a material spec anywhere in the project before this
(confirmed: `README.md`'s open-items list explicitly named "retaining-line
material" as unresolved, and the pin had no spec at all — it had been
informally called "the plastic striker," which turns out to be wrong for
this part specifically).

**Striker pin: hybrid — printed plastic body, hardened metal tip insert.
Revised 2026-08-07, supersedes the all-steel-dowel spec below.** The
original reasoning (2026-08-05) was two requirements plastic can't meet:
- The tip punctures the cartridge's crimped metal seal on every reload — it
  needs real hardness (target ~Rc 55–60) to stay sharp over many cycles,
  not just enough stiffness for one strike. **This still requires metal —
  hardness mismatch, not sharpness, is the mechanism: a softer point
  mushrooms against the seal instead of concentrating stress into it.**
- The Ø3.6mm neck (Z87–89.8) sits under the drive spring's full tension for
  however long the rocket is armed before launch. **Revisited 2026-08-07
  with real numbers from the spring spec (F_cocked≈50N): neck stress is
  only ~4.9 MPa, shoulder bearing stress under 1 MPa — both low enough that
  a decent engineering filament handles the sustained hold fine. This
  argument no longer requires the whole pin to be metal, just avoid PLA
  specifically (its ~55–60°C glass transition is an easy temperature for a
  pad in direct sun, making it the one filament where creep at this stress
  is a real risk). Nylon, PETG, or ASA for the body.**

Net effect: only the last few mm — the actual piercing point — needs to be
metal. Everything else (main shaft, shoulder/neck catch, tail/guide rod)
prints, avoiding the lathe work the original spec required.

**Tip sourcing (no machining), in order of practicality:**
1. **Harvest the piercing pin from a bike CO2 inflator head** (~$5–15,
   widely available) — these use a hardened tool-steel or stainless pin
   purpose-built to pierce this exact class of threadless CO2 cartridge.
   Pull the pin, no machining.
2. **Hardened sewing/harness/upholstery needles** — cheap, standardized
   diameters in the right ballpark for the current Ø3.6mm tip/neck
   geometry, sharp conical points out of the packet. Not purpose-built for
   metal, so verify in the same puncture test rather than assuming.
3. **Fallback: a stock hardened dowel pin, hand-pointed** — chuck in a
   drill, dress the end against a file or sandpaper. A manual sharpening
   step, not machining — no lathe, no precision work.

**Retention detail:** the insert's socket needs a real mechanical stop
(a shoulder the pin bottoms out against), not just friction/adhesive —
the puncture impulse (~100–150N estimate, see the Load case section below)
should bear on the plastic directly so the joint doesn't rely on the glue
line every cycle.

**Still open, same test closes it out:** the force-gauge puncture test
already needed for the spring sizing (below) should run all three tip
candidates side by side — cheap to get a real answer instead of guessing
which one reliably punctures and survives repeated reloads.

---

**Original 2026-08-05 spec, superseded above:** an off-the-shelf hardened
steel dowel pin (precision ground, ~Rc 60 stock), turned down on a lathe to
add the neck/shoulder/tip profile, with 416 stainless as a step-up if the
mechanism won't be cleaned/oiled between flights. Kept here for context —
the hybrid approach above is the current plan.

**Retaining line: Dyneema/Spectra (UHMWPE) braided line, not metal wire and
not Kevlar.** "Burn wire" is the standard industry term for this release
style, but an actual metal wire won't work: steel's melting point
(~1400°C+) and thermal conductivity are both far beyond what a small
nichrome coil on a battery-driven circuit can deliver locally — the heat
wicks away faster than it can build up. Real burn-wire releases use polymer
line:
- **Dyneema/Spectra** (recommended) — melts cleanly at ~144–152°C, well
  within the coil's reach at low current/short duration, very high
  strength-to-diameter ratio.
- Nylon monofilament — cheaper, more available, melts ~220–260°C, still
  works, just needs a bit more coil energy/time. Acceptable fallback.
- Kevlar/aramid — the "traditional" hobby-rocketry name for this
  mechanism, but it doesn't actually melt; it chars/decomposes around
  400–500°C. Less clean and less repeatable than a true melt. **Avoid.**

**Sizing dependency — now resolved provisionally, see below.** The drive
spring's preload force was the blocker for finishing both the pin-neck
stress check and the line diameter. Both are now closed out on paper in
[Drive spring and final line sizing](#drive-spring-and-final-line-sizing--decided-2026-08-07)
below, **pending one empirical measurement** (the actual puncture force —
see that section). The line's ⌀0.8mm in the CAD is confirmed to have been
an oversized schematic placeholder; final spec is ⌀0.30mm.

## Drive spring and final line sizing — decided 2026-08-07

Blender wasn't reachable this session (addon not connected), so this is a
paper design against the geometry recorded in this doc and in
`integrated_ring_av_co2_bay_30mm.md` — **apply to the CAD once Blender is
available**, don't treat the numbers below as already modeled.

### Load case

Stroke: 14mm, tip travels Z82 (cocked) → Z68 (pierce), per
`integrated_ring_av_co2_bay_30mm.md`.

**The governing input — puncture force — is not measured, only estimated.**
No test data exists anywhere in this project for the force/energy needed to
put a hole in this cartridge's flat pierce pad (thin, likely ~0.3–0.4mm
crimped steel or aluminum per the "smackable" pad called out in
`co2_cartridge_8g.scad`). Literature analogs for a sharp point piercing
sheet metal of that thickness suggest on the order of 100–150N static
equivalent, but that's an order-of-magnitude estimate, not a spec. **Name
the test:** press a sharpened rod of the pin's tip geometry into a spent
cartridge's pierce pad on a force gauge, record peak force. Until that
number exists, everything below is provisional, not decided.

Because the pin only has to *initiate and complete a puncture* (not hold
station against the cartridge afterward — see the open item on backpressure
below), this is sized as an impact/stored-energy problem rather than a
sustained-static-force problem: the spring accelerates a light pin over the
stroke, and momentum carries it through the puncture event, similar to a
firing pin driving a primer. Target stored energy at full stroke: **~0.39 J**
— comparable order of magnitude to small-arms firing-pin energies (0.3–0.7 J),
chosen as a reasonable starting margin over the ~100–150N estimate above,
not derived from it. Revisit once the force-gauge number exists.

A second, equally important constraint that a naive force-based sizing
missed on the first pass: the spring's cocked (armed) preload is held
indefinitely while the rocket sits on the pad, so wire stress at the cocked
position was capped well below typical cyclic-spring allowables (~600 MPa
vs. the ~900–1000 MPa a rapidly-cycled spring could tolerate) to avoid
stress relaxation ("taking a set") over a long arm-and-wait window.

### Spring spec (co2mod_drive_spring)

| Parameter | Value |
|---|---|
| Material | 302 stainless spring wire (ASTM A313) — corrosion resistance matters here: the housing bore is downstream of the pierce point and will see CO2/moisture after firing, and the mechanism is meant to be re-cocked and reused every flight |
| Wire diameter (d) | 1.2 mm |
| Mean coil diameter (D) | 6.0 mm (spring index C=5) |
| OD / ID | ≈7.2mm / ≈4.8mm |
| Active coils | 27 |
| Free length | ≈55 mm |
| Solid height | ≈35 mm |
| Spring rate (k) | ≈3.1 N/mm |
| Cocked deflection / force | 16mm / ≈50 N |
| Fired (end of 14mm stroke) deflection / force | 2mm / ≈6 N |
| Energy released over stroke | ≈0.39 J |
| Torsional stress, cocked (Wahl-corrected) | ≈570 MPa |

Stress was the binding constraint, not spring rate — an earlier pass at this
(0.8mm wire, 4.8mm mean diameter) hit ~1490 MPa at 50N, well past what 302
stainless tolerates without permanent set. Fixing it forced both a thicker
wire and more coils, which is why the free length landed at ~55mm rather
than the ~4mm currently modeled at Z92.5–96.5 — **this spring will not fit
in the space currently modeled for it at any reasonable stress margin.** If
17-7PH stainless (higher strength, better relaxation resistance) turns out
to be needed once the real puncture force is measured, that's the
recommended step-up material — same approach as the pin's hardened-steel
step-up path above.

**Consequence for the pin and housing (not yet modeled — flag, don't build
from this alone):**

- The pin's Z92–113 tail taper (r 4.5→1.8mm, a solid cone) cannot carry any
  coaxial spring without interference regardless of size, which is the
  actual root cause of pre-existing defect #2 below — there's no ID a
  spring on that taper could have that clears a 4.5mm-radius shaft. Fix:
  replace the taper with a short step down to a constant-radius **guide
  rod, ⌀~4mm**, long enough to back the spring through most of its stroke
  (~50mm). This grows the pin from its current 31mm (Z82–113) to roughly
  53mm (Z82–~135) — recompute pin mass once modeled (rough estimate ~5–6g
  with a ⌀4mm rod, versus 6.9g for the current taper — close enough that
  the ~0.39J energy target should still deliver a comparable impact
  velocity, order 10–12 m/s, but confirm once the real geometry exists).
- **No structure exists from Z94 (end of the modeled housing) out to the
  pin's new aft end (~Z135) to seat the spring's fixed end.** This needs an
  aft cap/extension added to the housing — not designed here, just flagged.
- This pushes the integrated assembly's headline total length (153.5mm,
  `integrated_ring_av_co2_bay_30mm.md`) out by roughly 20–25mm. Reconcile
  once the aft cap is actually modeled; treat 153.5mm as stale until then.

### Open item found while sizing this — cartridge backpressure on the pin (flag as safety-relevant, not solved here)

Once the pierce pad is broken, the cartridge's ~8 MPa fill pressure acts on
whatever pin/bore area is exposed to it — nothing in this project has
accounted for this force anywhere. Two numbers, both back-of-envelope:

- If gas exposure is confined to the pin's Ø3.6mm neck cross-section:
  π×1.8²×8 ≈ **81N** pushing the pin back — already bigger than F_fired
  (≈6N) and larger than F_cocked (≈50N).
- If gas reaches the full Ø9mm shaft in the housing bore (there is
  currently **no O-ring or seal specified anywhere between the pierced
  cartridge and the housing bore** — see open item 4 in
  `co2_deployment_module.md`): π×4.5²×8 ≈ **509N**, and at the housing↔collar
  joint's ~10mm clear bore (r=5mm): π×5²×8 ≈ **628N** trying to push the
  screwed-on retaining collar off its 3mm-engagement thread (Joint 2) —
  this is a real question about whether a joint meant to be hand-unscrewed
  for reloading can safely react a pressurized blow-off load.

Working assumption used above: the pin does **not** need to stay seated
against backpressure for the ejection function to work — once the pad is
torn, gas vents through the opening whether or not the pin retracts
afterward, so the spring only has to win the initial puncture, not hold
position afterward. That assumption needs an explicit yes/no from whoever
finalizes the pressure boundary design — if a seal is later added anywhere
in this gas path, or if the collar joint needs to resist blow-off, this
becomes a governing load case rather than a footnote.

### Retaining line — diameter finalized

Material was already decided 2026-08-05 (Dyneema/Spectra, above) — this
closes out the diameter, using F_cocked ≈ 50N from the spring spec above.

**⌀0.30mm Dyneema/Spectra (SK75/SK78-grade) braided line.** Straight-line
rated breaking strength for this diameter is typically ~350–400N
(~35–40kgf) for this class of braid — confirm against the specific
product's datasheet before ordering, published numbers vary by
manufacturer/construction. The number that actually matters here is the
**cinched/knotted** strength, not the straight rating: a line looped around
the Ø3.6mm neck and tied off at the anchor posts loses roughly 40–50% of
its straight strength to the knot/cinch geometry, not to creep (Dyneema's
creep resistance is good and the pre-launch armed window is short — creep
isn't the limiting mechanism here). That puts effective strength at
~175–240N against a 50N sustained hold: **~3.5–5x margin on the knotted
strength**. This is a real downsize from the current ⌀0.8mm CAD placeholder
— update the model once Blender is reachable.

## Two pre-existing defects found during this work — not fixed here

These predate today's session and are outside the scope of the lead-routing
fix, but are real and should not be forgotten:

1. **`co2mod_retaining_collar` is a solid disc — it has no bore.** Checked
   directly (vertex radii): exactly one distinct radius, 6.2mm, no hollow
   center. As modeled, the striker pin cannot physically pass through it.
   This is arguably more serious than the lead-routing bug: the mechanism
   as currently drawn cannot be assembled at all until this gets a bore cut
   through it (needs to clear at least the pin's r=4.5mm shaft, plus
   running clearance).
2. **The pin's tail taper likely intersects the drive spring.** The pin's
   Z92–113 tail is a single straight cone from r=4.5 down to r=1.8 (see
   profile table above) — no separate thin guide-rod section. The spring
   (`co2mod_drive_spring`, modeled at a constant r=3.0mm, Z92.5–96.5) sits
   inside that cone's radius for its full length. **Root cause confirmed
   2026-08-07** (see the drive-spring sizing section above): this isn't a
   sizing mistake, no coaxial spring fits this taper at any diameter. Fix is
   a guide-rod redesign of the tail, not yet applied to the CAD.

## Files

- `co2_trigger_release_mechanism.blend` — this subassembly
- No reference STL exported: the coil and spring are zero-volume curve
  objects (not mesh), so an STL export would silently drop the two parts
  this whole fix is about. Export once they're modeled as real solids.

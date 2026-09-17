# Design Notes — Dedicated Parachute Bay (SampleRocketABS33-36)

Records the addition done 2026-08-26: a new airframe section built exclusively
to hold recovery (the Ø300mm/30cm round canopy), plus a resize of the
existing CO2-module reservation to match numbers already on record in that
module's own doc. Built and verified directly against the FreeCAD solids
(`SampleRocketABS33-36.FCStd`) with FreeCAD's Python API, using the same
method as the AvBay integration pass: every new/modified solid healed (STEP
round-trip + `fixTolerance`/`removeSplitter`), checked for 0 open edges (mesh
watertightness via `Mesh.isSolid()`/`hasNonManifolds()`), and every
part-to-part pairing that should abut rather than overlap checked with
`Shape.common()` at 0.0000 mm³. See "Verification results" below.

## Why

The airframe had no section built specifically to hold the parachute — it
was informally sharing the 52mm "reserved CO2 envelope / interim parachute
bay" zone and the nosecone's own 34mm hollow cavity (see
`Design-Notes-AvBayIntegration.md`), neither sized against a real chute.
User specified a Ø300mm (30cm) round canopy and asked for a dedicated
section, ~10cm long. Read as 100mm of *clear packing bore*, not 100mm of
total part envelope (the difference matters — see "Sizing" below).

Two decisions were made with the user before cutting geometry:

1. **The CO2 envelope also got resized**, not just added-to. Its own doc
   (`Electronics/Integrated Bay Assemblies/integrated_ring_av_co2_bay_30mm.md`)
   already flagged its 52mm figure as stale — the drive-spring/aft-cap
   redesign it still needs adds "~20-25mm to the 153.5mm headline total
   length" that was never applied to the airframe. Took the conservative
   (safety-relevant, per that doc's own flag) end: **52mm → 77mm (+25mm)**.
2. **The new bay is a separate printed part**, bonded via the same
   flush-rebate joint style already used for the Fwd/Aft tube joint —
   not fused into `Body_Fwd`. Keeps it independently serviceable/swappable,
   matching the modular design philosophy the AvBay pass already
   established.

## Sizing

"~10cm" was built as 100mm of *clear, usable ⌀31 ID packing bore* — not
100mm of total printed part length. The joint overlap and the nose-shoulder
socket at the bay's own two ends don't reduce the through-bore (the ID
stays ⌀31 continuously through the joint, same principle as the existing
Fwd/Aft joint — see "Joint design" below), so counting them as part of the
"parachute bore" would have overstated real capacity for no reason. Net
result: the new `ParachuteBay` part is **135.5mm printed**, delivering
**100mm clear bore**. If a smaller total-growth number had been wanted, the
part could instead have been sized so its full 100mm printed envelope
*included* the joint+socket, at the cost of only ~65mm of real packing
room — flagged as the tradeoff, not silently chosen.

## Architecture (updated)

Same table as `Design-Notes-AvBayIntegration.md`, zones from the fwd collar
forward:

| Zone | Z (mm) | Contents |
|---|---|---|
| AvBay fwd collar | 183.5 – 186.5 | unchanged |
| CO2 envelope (resized) | 186.5 – 263.5 | 77mm clear bore, was 52mm |
| — joint overlap (spigot in `Body_Fwd`, socket in `ParachuteBay`) | 249.5 – 263.5 | ⌀33.0 spigot / ⌀33.2 socket, 0.1mm radial clearance each side |
| **Parachute bay — clear packing bore** | 263.5 – 363.5 | 100mm, ⌀31 ID, dedicated to the Ø300mm chute |
| Nose shoulder socket (in `ParachuteBay`) | 363.5 – 385 | ⌀30.6 shoulder, 0.2mm radial clearance, same as the old Body_Fwd/nose fit |
| Nose cavity (ballast, chute overflow) | 363.5 – 397.5 | hollow, r13.3 — now backup/ballast-only in practice |
| Nose tip (solid) | 397.5 – 433.5 | unchanged geometry, repositioned |

Overall assembled length is now **433.5mm** (Z −29.5 to Z433.5 with the
retainer cap) — up from 308.5mm, i.e. **+125mm**, matching
(CO2 +25mm) + (new bay clear bore +100mm) exactly.

## New printed part

| Part | File | Envelope | Z (mm) | Mass |
|---|---|---|---|---|
| Parachute Bay | `Print Files/SampleRocketABSBody33-36_ParachuteBay.stl/.obj` | ⌀35 OD / ⌀31 ID × 135.5mm L | 249.5 – 385 | 27.58 g |

Plain 2mm-wall tube (same ⌀35 OD/⌀31 ID as the rest of the airframe),
504 facets, watertight (0 open edges), single solid. Two features:

- **Aft socket** (Z249.5–263.5, 14mm): ID counterbored to ⌀33.2 to receive
  `Body_Fwd`'s new spigot (below). 0.1mm radial clearance, same fit
  tolerance as the existing Fwd/Aft rebate joint.
- **Fwd end** (Z363.5–385, 21.5mm): plain ⌀31 ID, unmodified from the rest
  of the tube — this is where the nosecone shoulder now plugs in, taking
  over that role from `Body_Fwd`'s old fwd tip exactly as-is (same fit,
  same clearance, just relocated).

No ports, vents, or anchor tabs added to this part — see "Open items"
for why the shock-cord anchor specifically was *not* added here despite
being the obvious place for it.

## Body_Fwd changes

`Body_Fwd` grew from 160.0mm to **163.5mm** (Z100→263.5, was Z100→260) and
picked up a **fwd rebate spigot**: OD steps 35→33.0mm (1.0mm wall) over
its last 14mm (Z249.5–263.5), cut the same way as `Body_Aft`'s existing
aft spigot (`Design-Notes-AvBayIntegration.md`, Fix 2) — this part is now
a spigot on *both* ends. ID is untouched (stays ⌀31 straight through,
including through the spigot span), so the through-bore that matters for
bay assembly is unaffected.

Net mass actually **dropped slightly** (33.36g → 32.50g) despite the part
getting longer: the 14mm spigot cut removes more wall material (thinning
2.0mm→1.0mm over that span) than the 3.5mm plain extension adds. Not a
defect — same effect already present in `Body_Aft`'s existing spigot.

## Joint design

Directly replicates the existing Fwd/Aft tube joint
(`Design-Notes-AvBayIntegration.md`, Fix 2): the aft/tail-ward part
(`Body_Fwd`, in this pairing) carries the OD-stepped spigot and keeps its
own ID unchanged, so its unchanged ⌀31 bore *is* the through-passage; the
fwd/nose-ward part (`ParachuteBay`) carries the ID-counterbored socket
pocket that the spigot sits inside. Verified 0.1mm radial clearance at
Z255 (spigot outer wire r=16.5mm, socket inner wire r=16.6mm) and 0.0000
mm³ overlap between the two solids.

This repeats the same thin-wall tradeoff already flagged for the original
joint: the spigot's 1.0mm wall is thin for FDM (2 perimeters at 0.45mm, no
margin) until bonded. Same fallback applies if it doesn't print solid — a
25mm external bonded band at ⌀38 OD (see the original doc's Fix 2).

## Nosecone / ballast cup — repositioned only

Both objects' geometry is **unchanged**; only their world-frame Z
placement moved, by the full **+125mm**:

- `Nosecone`: Placement.Base.z −21.5 → **+103.5** (shoulder now 363.5–385,
  tip 433.5)
- `Nose_BallastCup`: Placement.Base.z 257.5 → **382.5** (unchanged 15mm
  length, still sits against the solid tip)

## Verification results

1. **Watertight**: `Body_Fwd` and `ParachuteBay` both pass
   `Mesh.isSolid()==True`, `hasNonManifolds()==False` after the STEP-round-trip
   heal. Volume preserved exactly through healing (31254.5386 mm³ before
   and after for `Body_Fwd`).
2. **No interference** (`Shape.common()`, all 0.0000 mm³): `Body_Fwd` vs
   `ParachuteBay`, `ParachuteBay` vs `Nosecone`, `ParachuteBay` vs
   `Nose_BallastCup`, `Nosecone` vs `Nose_BallastCup`, plus re-checked
   `Body_Fwd` against its unchanged neighbors (`Body_Aft`,
   `AvBay_BatteryCradle`, `AvBay_Mandrel`, `AvBay_FwdCollar`).
3. **Joint clearance**: spigot OD r=16.5mm vs socket ID r=16.6mm at
   Z255 — confirmed via cross-section, matches the 0.1mm/side clearance
   used on the existing Fwd/Aft joint.
4. **Bay-withdraws-through-nose sweep**: a uniform ⌀30.8 envelope swept
   Z385→85 shows 0.0000 mm³ against the new `ParachuteBay` (plain bore
   throughout, no protrusions). Note: re-running this same check against
   `Body_Fwd` over the *original* Z260→85 span (i.e. before any of this
   pass's changes) also returned 0.0000 mm³, not the 73.68 mm³
   launch-lug figure `Design-Notes-AvBayIntegration.md` recorded for that
   check — a pre-existing discrepancy unrelated to this pass (not
   reproduced by anything changed here; not chased further, flagged for
   whoever revisits that area).

## Mass, CG, stability — recomputed

Structure masses are exact (measured directly off the finished FreeCAD
solids, ABS 1.04 g/cc). Non-printed items (motor, electronics, recovery
hardware) are representative, same figures as
`Design-Notes-AvBayIntegration.md` except recovery mass, which moved to
its new physical location.

| Component | Mass (g) | CGz (mm) | Change |
|---|---|---|---|
| Nosecone | 21.06 | 398.27 | repositioned (+125mm), shape unchanged |
| Body_Fwd | 32.50 | 181.75 | **extended + spigot added** |
| Body_Aft | 37.31 | 37.12 | unchanged |
| Fins ×3 | 8.94 | 22.13 | unchanged |
| Motor Retainer Cap | 12.79 | −15.01 | unchanged |
| Aft Centering Ring | 1.47 | 6.50 | unchanged |
| AvBay aft bulkhead | 2.16 | 83.53 | unchanged |
| AvBay battery cradle | 19.86 | 105.25 | unchanged |
| AvBay mandrel | 4.56 | 154.50 | unchanged |
| AvBay fwd collar | 0.91 | 185.16 | unchanged |
| Nose ballast cup (empty) | 2.50 | 391.81 | repositioned (+125mm) |
| **Parachute Bay** | **27.58** | **320.86** | **new** |
| Battery + USB charger | 14.5 | 105.25 | unchanged |
| Ring-zone electronics | 15.5 | 154.5 | unchanged |
| Wiring/connectors (estimate) | 5.0 | 130.0 | unchanged |
| Motor, Estes C6 loaded (representative) | 26.0 | 32.0 | unchanged |
| Recovery: chute + cord + link (representative) | 12.0 | **313.5** | **moved from Z210 (old interim zone) to the new bay's clear-bore midpoint** |
| **TOTAL, 0g ballast** | **244.6** | **154.6** | |

CP (Barrowman) ≈ **116.2 mm**: nose contributes CNα=2 at X=410.7 (same
tangent-ogive coefficient 0.47 and L=48.5mm as before, recomputed off the
new tip at Z433.5); fins contribute CNα=6.97 at X=31.7 (unchanged — fins
didn't move).

| Ballast (g) | Total mass | CG | Margin (cal) |
|---|---|---|---|
| 0 | 244.6 g | 154.6 mm | **1.10** |
| 10 | 254.6 g | 164.0 mm | 1.36 |
| 15 | 259.6 g | 168.3 mm | 1.49 |
| 20 | 264.6 g | 172.6 mm | 1.61 |
| 25 | 269.6 g | 176.6 mm | 1.73 |

**Stability improved, not degraded.** Every gram this pass added sits
forward of the CG (new bay + relocated nose/recovery mass), pulling CG
forward faster than it pulls CP forward. Margin at zero ballast went
**0.76 cal → 1.10 cal** — already past the common 1.0-cal comfort target
with *no* ballast loaded. The ballast cup is still built and installed
either way (2.5g whether loaded or not), but **the previous recommendation
to load 10–15g no longer applies** — treat it as optional insurance, not
a requirement, unless a real OpenRocket run against the actual motor/chute
says otherwise (still required before flying, unchanged from the original
plan).

**Thrust-to-weight note** (flagged, not addressed — pre-existing motor
choice, out of scope for this pass): total mass grew 217.6g → 244.6g
against the same representative Estes C6. Worth checking T/W margin
against the real motor before flying; not re-derived here.

## Open items — not resolved, flagged deliberately

0. **Confirmed with the user 2026-08-26 (after this pass's initial
   write-up): the motor never fires an ejection charge — recovery
   deployment is CO2-only, from a canister in the AvBay.** This resolves
   what was flagged here as a possible conflict with a same-day,
   concurrent change to `Body_Aft` (the motor bulkhead/thrust ring
   re-bore, BOM.md part 5 addendum, whose own note independently says
   the same thing: "this build fires a plugged motor (no motor ejection
   charge)... recovery deployment is handled entirely by the AvBay").
   Both docs now agree. Consequence worth stating plainly: **the CO2
   module is not installed yet** (its 3 blockers in
   `integrated_ring_av_co2_bay_30mm.md` are still open — no bore in the
   retaining collar, spring/aft-cap redesign, undecided backpressure
   boundary), so **there is currently no working deployment mechanism at
   all**. `Design-Notes-AvBayIntegration.md`'s "Ejection-gas path
   (interim, motor ejection)" section describes a path that will never
   actually be used by this build — it's stale/moot, not a fallback in
   reserve. Item 1 below is reframed accordingly: the dead-volume concern
   applies to the *future CO2 discharge*, not to any motor-ejection duct.
1. **Dead volume the future CO2 discharge will need to fill grew ~2.4×**
   (52+34=86mm of ⌀31 bore before this pass → 77+100+34=211mm now). This
   is no longer about the motor-ejection duct (see item 0 — that path is
   moot, the motor never fires a charge); it's about whatever vent
   path the eventual CO2 module uses once its own blockers are closed
   out (per its doc, 3× ⌀2mm radial ports through the pierced cartridge's
   neck, wherever that lands once it's actually built into the resized
   77mm envelope). Adding a bulkhead to shrink this back down was
   considered and rejected — this design relies on one continuous open
   bore from wherever CO2 vents to the nosecone tip, so discharge
   pressure can build against the whole stack and pop the friction-fit
   nosecone; a bulkhead anywhere in that path would seal the chute in
   permanently instead of ejecting it. Whoever builds the CO2 module
   should size its vent ports against this larger volume (211mm of ⌀31
   bore, not the 86mm the module's own doc was written against) and
   ground-test discharge before flying — this was already required per
   the original AvBay notes for the (now-moot) motor-ejection path;
   restate it here since that's no longer the mechanism that will
   actually need testing.
2. **Shock-cord anchor is now in the wrong place.** The only anchor tab
   in the design is on `AvBay_FwdCollar` (Z183.5–186.5) — now 200mm from
   the nose separation point instead of 83mm, with the cord routing
   through the entire resized CO2 envelope and the new joint. A tab was
   *not* added to `ParachuteBay` in this pass: any feature protruding
   inward past the ⌀30.8 sweep envelope would block the AvBay's own
   nose-first insertion (the AvBay parts slide down through this entire
   new section to reach their Z82–186.5 seats), and a flush/OD-mounted
   anchor wasn't designed carefully enough in the time available to be
   confident it's right. **Needs a follow-up pass**: either a small
   feature added to `ParachuteBay` *after* it's bonded in place (so it
   doesn't have to clear the insertion sweep), or a flush wall-mounted
   loop that never intrudes past r15.4mm.
3. **Static-port distance note in `Design-Notes-AvBayIntegration.md` is
   now stale** — its "120mm (3.4 calibers) below the nose/body joint"
   line measured to the old flush-base Z260; corrected in that file to
   245mm/7.0 calibers off the new Z385.
4. **CO2 module's own reservation note is now current, not stale** — its
   doc previously flagged its own 52mm figure as outdated; updated to
   77mm to match this pass. The three real blockers it lists (retaining
   collar bore, spring/aft-cap redesign, backpressure boundary) are
   unaffected by this pass and still open.
5. **No ground discharge test has been performed, and none can be until
   the CO2 module exists** — see item 0. This is currently the actual
   blocker on flying at all (independent of anything in this pass): no
   installed deployment mechanism means no recovery. Not a task for this
   pass to close, just stating it plainly since it's easy to lose track
   of amid the airframe-sizing detail above.

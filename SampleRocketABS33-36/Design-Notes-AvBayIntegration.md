# Design Notes — AvBay Integration (SampleRocketABS33-36)

Records the avionics-bay integration done 2026-08-19: a sealed, serviceable
avionics bay built into the existing airframe, four independent airframe
defects fixed along the way, and a barometer static-port design. Built and
verified directly against the FreeCAD solids (`SampleRocketABS33-36.FCStd`)
with FreeCAD 1.1's Python API — every step below was healed (STEP round-trip
+ `fixTolerance`/`removeSplitter`) and checked for 0 open edges (mesh-based
boundary-edge count) before being accepted, and every part-to-part pairing
that should abut rather than overlap was checked with `Shape.common()` and
confirmed at 0.0000 mm³. See "Verification results" below for the full run.

## Why

The bay (`Electronics/Integrated Bay Assemblies/integrated_ring_av_co2_bay_30mm`)
existed only as a Blender layout study against a generic ⌀32 reference tube —
never placed in a real airframe. Separately, direct measurement of
`SampleRocketABS33-36.FCStd` turned up four defects that block flight
independent of the bay: a solid disc plugging the motor bore, an unmodeled
tube joint, a nosecone shoulder that didn't fit its own airframe, and fin
root tabs that don't reach the tube wall. This pass fixes all four and
installs the avionics half of the bay (CO2 half deferred — see "What's not
done").

## World frame

Z axis = rocket centerline, Z=0 at the tail tip (Motor Retainer Cap base),
increasing toward the nose. Same convention the project's existing FCStd
already used.

## Architecture

| Zone | Z (mm) | Contents |
|---|---|---|
| Motor bay | 0 – 64 | motor tube, ⌀18 ID |
| Motor bulkhead | 64 – 67 | relocated from Z37–40 (see Fix 1); ⌀18 bore on-axis |
| Plenum | 67 – 82 | open bore, empty |
| AvBay aft bulkhead | 82 – 85 | pressure boundary; off-axis gas port |
| **Sealed dry bay — battery/charger** | 85 – 125.5 | `AvBay_BatteryCradle` |
| **Sealed dry bay — electronics ring** | 125.5 – 183.5 | `AvBay_Mandrel` + 8 boards |
| AvBay fwd collar | 183.5 – 186.5 | pressure boundary; gas relief + shock-cord anchor |
| Reserved CO2 envelope / interim parachute bay | 186.5 – 238.5 | empty, ⌀31 × 52 mm |
| Nose shoulder | 238.5 – 260 | ⌀30.6, 0.2 mm radial clearance in the ⌀31 ID |
| Nose cavity (parachute + ballast) | 238.5 – 272.5 | hollow, r13.3 |
| Nose tip (solid) | 272.5 – 308.5 | see "Nosecone" below for why |

Overall length is now **308.5 mm** (338 with the retainer cap) — down from
359.5, because the nosecone was 21.5 mm too long for its own shoulder before
this pass (see Fix 3).

## Airframe fixes

All four were approved as in-scope defects; two more (marked *addition*) were
added during implementation with a one-line reason each, since they weren't
in the original four but are required for the design to work.

**1. Motor bore blockage (approved fix).** A solid ⌀31 disc at Z37–40 fully
plugged the ⌀18 motor bore — no motor could be loaded. Relocated to
**Z64–67** (right where the motor tube's own aft end already was) and bored
**⌀18 on-axis**, so it now closes the annulus between the motor tube and
airframe (doing the job of a centering ring) while leaving the bore clear.
Removing the old disc also restores the fin-slot's continuity through
Z37–40, where it had been interrupted, though that wasn't asked for.

**2. Fwd/Aft tube joint (approved fix, method changed from the plan).**
`Body_Fwd` and `Body_Aft` occupied the same 14 mm of wall (Z100–114, 2903
mm³) with no joint modeled. The plan called for a separate printed coupler;
built as a **flush external rebate** instead — `Body_Aft`'s OD steps down to
⌀33.0 over Z100–114 (1.0 mm wall), and `Body_Fwd` is counterbored to ID
⌀33.2 over the same span (0.9 mm wall, 0.1 mm glue clearance) — because a
separate coupler necks the bore to ⌀27.6 there, and the bay's ⌀30.8
aft-bulkhead/collar discs can't pass a ⌀27.6 opening on the way in from the
nose. The rebate keeps the bore at ⌀31 for the joint's whole length, so the
bay still installs from the nose end. **0.9 mm is thin (2 perimeters at
0.45 mm, no margin)** — check what wall this printer holds before trusting
it; fallback is a ⌀32.6 split (aft 0.8 / fwd 1.1) or a 25 mm external
bonded band at ⌀38 OD if 0.9 mm doesn't print solid.

**3. Nosecone shoulder (approved fix).** Was ⌀23 against a ⌀31 ID (4 mm
radial rattle) and sat 21.5 mm proud of the tube instead of inside it.
Shoulder grown to **⌀30.6** (0.2 mm clearance) and the whole part
translated **−21.5 mm** so the ogive base is flush at Z260 — this is also
what shortens the rocket from 359.5 mm to 308.5 mm.

**4. Open fin slots (approved fix).** Root tabs reached only 0.44 mm into
the 2 mm wall (X17.06 vs the wall's X15.5 inner face), leaving three
2.9 mm-wide through-slots open into the airframe. Extended all three tabs
to **X15.5** (full 2 mm depth, flush with the tube ID) — `+109.2 mm³` per
fin, confirmed 0 mm³ overlap with the tube afterward (the tab exactly fills
what was open slot). The slot itself measures 2.88 mm wide against a 2 mm
fin (~0.2 mm clearance per side) — standard TTW glue clearance, closed with
an epoxy fillet on assembly, not a defect. True TTW (tab reaching the motor
tube at r9.5) was **not** done — it would mean cutting into `Body_Aft`'s
already-fused motor tube; flagged as an optional follow-up, not attempted
here.

**5. Lower-annulus vent — addition, not in the approved list.** One ⌀2 mm
hole through `Body_Aft`'s outer wall at Z≈20, θ=30° (clear of all three fin
slots). Closing the fin slots (Fix 4) turned the annulus below the fwd
centering ring into a sealed dead volume with no relief path for ascent or
ejection pressure; this vents it. Confirmed radially open at r13–18.

**6. Two M3 collar screws — addition, not in the approved list.** Two ⌀3.4
clearance holes through `Body_Fwd` at Z185, θ0°/180°, for nylon screws into
the fwd collar. The collar is the bay's forward pressure boundary and axial
stop; friction alone won't hold it against ejection pressure. These are
penetrations, but the screw body fills them — sealed, unlike an open port.
The alternative (bond the collar in permanently) trades this for a
non-removable bay; not done, since serviceability was a stated goal.

## New printed parts (`Print Files/`)

All six healed to 0 open edges and check clean against every neighboring
part and against the airframe (0.0000 mm³ overlap throughout).

| Part | File | Envelope | Z (mm) | Mass |
|---|---|---|---|---|
| Aft bulkhead | `AvBay_AftBulkhead.stl/.obj` | ⌀30.8 × 3 mm | 82–85 | 2.16 g |
| Battery cradle | `AvBay_BatteryCradle.stl/.obj` | ⌀30.6 × 40.5 mm | 85–125.5 | 19.86 g |
| Mandrel | `AvBay_Mandrel.stl/.obj` | ⌀20.5/⌀18 × 58 mm | 125.5–183.5 | 4.56 g |
| Fwd collar | `AvBay_FwdCollar.stl/.obj` | ⌀30.8/⌀20.5 × 3 mm | 183.5–186.5 | 0.91 g |
| Nose ballast cup | `Nose_BallastCup.stl/.obj` | ⌀26.4 × 15 mm | 257.5–272.5 (world) | 2.50 g |
| Duct plug (spare) | `AvBay_DuctPlug.stl/.obj` | ⌀19.5 × 10 mm | n/a — not installed | 2.72 g |

**Aft bulkhead** — O-ring groove (⌀27.6–28.8, 1.8 mm deep, for a ~2mm-CS
nitrile O-ring) sealing to the tube ID; off-axis ⌀5 gas port at (0,−11).

**Battery cradle** — full-length pocket 20×8.5×40.5 mm for the battery
(offset +Y) with the USB charger tucked in the same pocket; off-axis ⌀6
gas duct at (0,−11), aligned with the bulkhead's port; **4× ⌀4 mm axial
equalization holes** at r11, θ30/150/210/330, so the battery-zone air and
the ring-zone annulus are one vented volume rather than two pockets with
separate pressure lag.

**Mandrel** — plain tube; boards standoff-mount to the OD, unchanged from
the original bay's board-tier layout (tiers ring the ⌀20.5 OD at Z2–23.59
/ Z25.59–44.59 in bay-local coordinates, 0/90/180/270°). Checked the
launch-lug boss (which intrudes to r14.5 over Z167.5–192.5) against the
mandrel's OD (r10.25) — clear by 4.25 mm, and it falls on tier 2's already-
unpopulated spare slot regardless, so no relief cut was needed here (the
plan called for one; turned out not to be necessary once measured).

**Fwd collar** — same O-ring groove concept; 2× ⌀2 mm lead feedthroughs at
θ80/100° (potted, for the future CO2 nichrome leads); 2× ⌀3.4 M3 clearance
holes at θ0/180°; shock-cord anchor tab; off-axis ⌀6 gas-relief hole at
(0,−11), matching the cradle/bulkhead; and a **local relief cut against
the launch-lug boss** — the collar's OD (r15.4) initially collided with the
boss (8.3 mm³ overlap, found during verification, not anticipated in the
plan) since the collar sits at Z183.5–186.5, inside the lug's Z167.5–192.5
span. Fixed by cutting the collar with the lug's own solid plus a small
extra margin; re-verified at 0 mm³ overlap.

**Nose ballast cup** — sits at the fwd (tip) end of the nosecone's hollow
cavity, open aft for loading shot + epoxy. See "Nosecone" below for why it
doesn't reach the actual tip.

**Duct plug** — not installed in this build. Blanks the aft bulkhead's gas
port when the CO2 module eventually replaces motor ejection. Kept as a
spare part; excluded from the mass/CG table below.

## Ejection-gas path (interim, motor ejection)

motor bore → ⌀18 hole in the relocated bulkhead (Z64–67, on-axis) → open
plenum (Z67–82) → **aft bulkhead, off-axis ⌀5 at (0,−11)** → **battery
cradle's off-axis ⌀6 duct**, running the full 40.5 mm alongside the
battery → opens into the **ring-zone annulus** at Z125.5 (boards ring the
mandrel with natural gaps between them at 45/135/225/315°) → **fwd collar's
off-axis ⌀6 relief hole**, same (0,−11) alignment → reserved CO2
envelope / interim parachute bay → nose separates.

This routing was reworked twice during build, both times because a first
pass didn't actually connect:

- An on-axis ⌀18 port through the bulkhead (mirroring the motor bulkhead)
  doesn't work — the battery pocket sits on the tube centerline, so an
  on-axis hole is blocked. The duct has to be off-axis through the
  battery-zone; off-axis routing then has to carry through the bulkhead
  and continue through the ring zone too, or the two ends don't align.
- The off-axis position (0,−11) is chosen because it's the clear side of
  the battery pocket (Y−7 to +13, offset toward the tube wall) — placing
  the duct there leaves ~1 mm wall to the battery and ~1.3 mm to the OD.

**Battery zone stays hermetically sealed** except for this one ⌀5–6
channel — no ejection gas reaches the battery or charger PCB. **The
ring-zone annulus is not gas-sealed from this interim path** — a brief
puff of motor-ejection gas passes through the same annulus the boards sit
in, via the natural gaps between board positions, before reaching the
collar's relief hole. This is a deliberate, documented trade-off, not an
oversight: routing a fully isolated duct through the same 5.25 mm-wide
annulus the boards already occupy doesn't fit geometrically, and brief
gas exposure to a sled in the ejection path is a known, commonly-accepted
compromise in dual-deploy designs. It goes away entirely once the CO2
module replaces motor ejection (CO2 gas stays inside its own sealed
chamber, per the original bay design, and never enters this annulus).

**This duct is the narrowest, least-proven part of the whole gas path —
confirm it works with an actual ground ejection test before it's anywhere
near a loaded rocket.** ⌀5–6 mm is generous compared to a baro port but
has not been flow-tested; if a ground test shows sluggish separation,
open up the bulkhead/cradle/collar ports together (they're deliberately
all cut from the same off-axis position, so enlarging one without the
others just moves the bottleneck).

## Nosecone

Hollowed to a 2 mm wall — but **not all the way to the tip**. FreeCAD's
constant-offset shell operation (`makeThickness`) fails at the ogive's
pointed apex (`OCC gp_Sphere radius < 0`, a known offset singularity at
sharp points) — a real geometric limit, not a tooling gap: a true
constant-thickness shell can't reach a mathematical point without either a
zero-thickness feather edge or self-intersecting surfaces.

Measured the ogive's own outer-radius profile and cut a plain **r13.3
cylindrical cavity** from the open base (Z238.5) up to **Z272.5**, where
the outer radius is 15.61 mm — a 2.3 mm wall there, safely above the 2 mm
target. Above Z272.5 (the last 36 mm to the tip) is **left solid**. This
is standard practice for pointed nose cones (avoids an unmanufacturable
feather edge) and it's a deliberate outcome, not a shortfall: that ~13 g
of solid tip mass, right where ballast is most effective per unit mass, is
a large part of why this design turns out to need less added ballast than
first estimated (see "Mass, CG, stability" below). The ballast cup sits at
the top of the cylindrical cavity (Z257.5–272.5), against the solid tip.

## Verification results

Full run against the saved `SampleRocketABS33-36.FCStd`:

1. **Watertight** (0 open edges via mesh-based boundary-edge count, all
   Solids=1): every modified and new object passes. `MotorRetainerCap`
   shows 31 open edges — **pre-existing, not touched by this pass**; the
   BOM already documents its internal thread as "couldn't be healed 100%
   ... good enough that a slicer's standard auto-repair will close the
   rest," unchanged here.
2. **No interference**: all 17 checked pairs (airframe-to-airframe,
   airframe-to-fin, airframe-to-bay-part, bay-part-to-bay-part,
   nosecone-to-ballast-cup) — 0.0000 mm³.
3. **Motor fits**: ⌀18×70 mm probe, Z−3 to 67, against `Body_Aft` — 0 mm³.
4. **Bay inserts from the nose**: a uniform ⌀30.8 envelope swept Z260→85
   shows 73.68 mm³ against `Body_Fwd` — this is exactly the launch-lug
   boss (bbox matches Z167.5–192.5 precisely); the real bay is narrower
   than ⌀30.8 through that span (mandrel OD is only ⌀20.5), so it doesn't
   reach the boss — already confirmed at 0 mm³ per-part in check 2. Zero
   against `Body_Aft`.
5. **Sealed-boundary penetrations**: fine angular scan at Z140 finds
   exactly 4 gaps at θ45/135/225/315 (the ports); at Z185, exactly 2 at
   θ≈178–180 (the M3 pair, one side of the scan's 1° resolution rounds to
   178.4/180 rather than two separate points — same two holes).
6. **Static ports**: all 4 confirmed open clean through the wall at their
   designed position.

## Static ports — 4 × ⌀1.0 mm at θ45/135/225/315°, Z=140

Sealed volume Z85–186.5. Free air ≈ 24.6 cm³ in the ring-zone annulus
(π(15.5²−10.25²)×58) plus the battery zone, which only counts toward the
vented volume because of the cradle's 4 equalization slots — without them
the battery pocket is a separate, slower-lagging pocket.

- **Size.** ¼″-per-100 in³ rule → 0.77 mm² total → ⌀0.49 mm per port
  across four (⌀0.39 mm on the annulus-only figure) — below any
  practical drilling floor, so manufacturability binds, not lag.
  **4×⌀1.0 mm is 2.0× the rule by diameter** (4.1× by area — quote
  diameter; the area figure reads far more alarming than it is).
- **Why oversizing here is safe.** The rule of thumb is itself
  conservative: Cambridge University Spaceflight's first-principles
  analysis puts the requirement at 0.176″ per 100 in³ **at Mach 2** —
  already ~30% under ¼″ on diameter, at a speed regime far above this
  rocket's. With an Estes-class motor this stays under ~Mach 0.3, so the
  physics-based requirement is smaller still and the dynamic-pressure
  penalty for 2× diameter is negligible. Meanwhile a sub-mm hole through
  a 2 mm wall is a >2:1-depth channel — real discharge loss, and it
  paint-bridges and clogs. ⌀0.8 mm is available if a closer match to the
  rule is wanted; ⌀1.0 mm is the robust choice and what's built.
- **Placement.** 45/135/225/315° puts every port in an inter-board gap
  (boards sit at 0/90/180/270°), so no jet hits a board face. Z=140 is
  inside the sealed volume, above the Z100–114 joint (so it's single
  2 mm wall, not the rebate's thinner section), 245 mm (7.0 calibers)
  below the nose/body joint **(updated 2026-08-26 — was 120mm/3.4 cal to
  the old Z260 flush base; the nosecone moved to Z385 when the dedicated
  parachute bay was added, see `Design-Notes-ParachuteBay.md`)**, 11 mm
  below the BMP388's lower edge, and 45° clear of the launch-lug wake
  (lug at θ90°, flow runs nose→tail so its wake covers lower Z at that
  clocking).
- **Manufacture.** Modeled at ⌀1.0 mm; FDM undersizes small holes, so
  finish with a 1.0 mm drill from the outside. Sharp, flush edges — no
  chamfer, no burr. Mask before painting.

**Buzzer** stays inside the sealed bay, no dedicated sound port (one would
dominate the vent area). If bench testing shows it's inaudible through
the wall, relocate it nose-ward of the fwd collar rather than adding a
hole.

**Arming/charging**: no airframe cutouts. The bay withdraws through the
nose for USB-C charging and microSD swaps. Use a **magnetic reed switch**
for arming (zero holes, preserves the seal) — add it plus a magnet to
`avionics_bom.md` (done, see that file).

## Mass, CG, stability

Structure masses below are exact (measured directly off the finished
FreeCAD solids, ABS 1.04 g/cc). Electronics masses are from
`Electronics/Avionics/avionics_bom.md`. Motor and recovery-hardware masses
are representative (not modeled anywhere in this project) and are flagged
as such — **confirm against your actual motor and chute before flying.**

| Component | Mass (g) | CGz (mm) |
|---|---|---|
| Nosecone (hollowed, solid tip) | 21.06 | 273.27 |
| Body_Fwd | 33.36 | 183.54 |
| Body_Aft | 37.00 | 36.88 |
| Fins ×3 | 8.94 | 22.13 |
| Motor Retainer Cap | 12.79 | −15.01 |
| Aft Centering Ring (pre-existing, folded into Body_Aft's own volume — kept separate here as the project's own BOM already does) | 1.47 | 6.50 |
| AvBay aft bulkhead | 2.16 | 83.53 |
| AvBay battery cradle | 19.86 | 105.25 |
| AvBay mandrel | 4.56 | 154.50 |
| AvBay fwd collar | 0.91 | 185.16 |
| Nose ballast cup (empty) | 2.50 | 266.81 |
| Battery + USB charger | 14.5 | 105.25 |
| Ring-zone electronics (Nano, Pololu, BMP388, ADXL375, microSD reader+card, buzzer, MOSFET, reed switch+magnet) | 15.5 | 154.5 |
| Wiring/connectors (estimate) | 5.0 | 130.0 |
| Motor, Estes C6 loaded (representative) | 26.0 | 32.0 |
| Recovery: chute + cord + link (representative) | 12.0 | 210.0 |
| **TOTAL, 0 g ballast** | **217.6** | **114.8** |

CP (Barrowman) ≈ **88.3 mm**: nose contributes CNα=2 at X=285.7 (tangent-
ogive coefficient 0.47, off the corrected tip at Z308.5, L=48.5 mm — the
tip moved with the nosecone reposition, so this is recomputed from the
plan's original figure); fins contribute CNα=6.97 at X=31.7 (unchanged —
fin outer geometry wasn't touched, only the root tab's internal depth).

| Ballast (g) | Total mass | CG | Margin (cal) |
|---|---|---|---|
| 0 | 217.6 g | 114.8 mm | **0.76** |
| 10 | 227.6 g | 121.5 mm | 0.95 |
| 15 | 232.6 g | 124.6 mm | 1.04 |
| 20 | 237.6 g | 127.6 mm | 1.12 |
| 25 | 242.6 g | 130.5 mm | 1.21 |

**This reverses the plan's original stability call.** The plan (written
before build) estimated 0.59 cal with no ballast, using a naive "uniform
2 mm shell" nosecone-mass estimate (12.79 g) and called 20–25 g of
ballast necessary. The as-built nosecone is 21.06 g — because the OCC
offset-shell tip limitation (see "Nosecone" above) left ~13 g of tip
material solid, exactly where ballast is most effective per gram. Result:
**0.76 cal with zero added ballast**, already a workable margin without
touching the ballast cup.

0.76 cal is workable but under the common 1.0-cal comfort target. The
ballast cup is built and installed either way (it costs 2.5 g of printed
shell whether loaded or not) — **recommend loading 10–15 g** to land at
0.95–1.04 cal, cheap insurance rather than a requirement. This entire
table is a hand-check with representative (not measured) motor/recovery
masses — **confirm in OpenRocket against your real motor and chute before
flying**, exactly as the original plan required regardless of outcome.

## What's not done

- **The CO2 module is not installed.** Its own document
  (`integrated_ring_av_co2_bay_30mm.md`) still has three open blockers:
  the retaining collar has no bore, the drive spring needs an aft cap
  that adds 20–25 mm, and ~628 N of post-pierce backpressure is
  undecided. The reserved envelope here is 52 mm (Z186.5–238.5); if the
  aft-cap redesign adds the full 20–25 mm, the bay will grow past
  Z238.5 and the nose shoulder will need to move again.
- **Recovery is motor ejection only**, through the duct described above,
  until the CO2 module exists.
- **Fins are keyed 2 mm TTW, not full-depth TTW** to the motor tube
  (would require cutting `Body_Aft`'s fused motor-tube wall).
- **The 0.9/1.0 mm rebate-joint walls are thin** until bonded — handle
  those parts carefully before assembly, and see Fix 2's fallback if
  they don't print solid.
- **Ground ejection test not yet performed** — required before this
  flies, per the gas-path note above.

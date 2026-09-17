# Aft Motor Retention — design notes, v1

Screw-off end cap for motor retention and reload on Phoenix ABS 40-43.
Companion to `DESIGN.md` §9 (structure) and §8.4 (fits). Build script:
`PhoenixABS40-43_aft_retention_v1.py`. Verifier: `verify_aft_retention.py`.
Machine log: `build_report_v1.txt`.

**Status: assembles and verifies clean.** All checks pass; STLs are in `Print Files/`.
Nothing here is flight-qualified — see *Open items*.

**Three configurations share one cap and one thread:**

- **cfg A — bonded insert.** `AftRetainerBase` bonds inside a separate airframe. Engine
  block bore is open ⌀14. Correct for a plugged motor.
- **cfg B — sealed aft section + bonded fins (§4A).** `AftSectionSealed` **is** the aft
  airframe: real 43/40 wall, **through-the-wall fin slots**, integral centering rings, a
  **solid** bulkhead that both seals the motor mount and takes thrust, and a forward lip the
  forward tube epoxies over. Three `Fin` parts bond into the slots.
- **cfg C — one-piece fin can (§4B).** `AftFinCan` is cfg B with the fins **printed in** and
  4 mm root fillets, no slots and no bond line. This is what `DESIGN.md` §9 asks for.
  **No vents — this build flies a plugged motor**, so there is no charge to route overboard
  (`DESIGN.md` §7.6's own last paragraph: a plugged motor "removes this problem entirely").

---

## 1. What it is

Three printed bodies, all ABS 100 % infill (ρ 1050):

| Body | Mass | Role |
|---|---|---|
| `AftRetainerBase` | **12.09 g** | threaded boss + conical seat + register spigot + motor tube + engine block |
| `MotorRetainerCap` | **9.04 g** | the screw-off cap: internal thread, exhaust bore, retaining lip, grip ribs |
| `FwdCenteringRing` | **2.79 g** | cfg A only — plain glued ring at the motor tube's forward end |
| `AftSectionSealed` | **29.07 g** | cfg B — the aft airframe section, slotted (§4A) |
| `Fin` ×3 | **5.45 g** ea. | cfg B — bonds into the slots (§4B) |
| `AftFinCan` | **46.12 g** | cfg C — section and fins as one piece (§4B) |
| **cfg A**, cap + base + ring | **23.91 g** | net **+18.91 g** at 378.5 mm — 0.45 cal |
| **cfg B**, cap + section + 3 fins | **54.45 g** | net **+24.69 g** at 361.6 mm — 0.50 cal |
| **cfg C**, cap + fin can | **55.16 g** | net **+25.41 g** at 361.5 mm — 0.51 cal |

cfg B and cfg C are **0.7 g apart** — the choice is about printing and assembly, not mass.
Both net figures already credit the 14.2 g fin set the `.ork` carries (§4.5) and the 51.4 mm
of body tube the section replaces.

The cap unscrews by hand; the spent 18 × 70 mm casing slides straight out of the tail.
Motor is **plugged** (no ejection charge) per the build brief — see *Open items* for what
changes if that ever stops being true.

## 2. Frame and dimension chain

**Z = 0 at the airframe's aft face, +Z toward the nose, aft negative.**
Airframe from the `.ork`: OD 43.0 / ID 40.0 / wall 1.5.

```
  Z  +58.9  motor tube forward end
     +55.9  engine block shoulder — motor's forward rim seats here (bore 14.0)
     +12.0  register spigot forward end (OD 39.6, glued into the 40.0 bore)
      0.0   airframe aft face; seat cone reaches r 21.5
     -2.3   seat cone starts, r 19.2  ── boss thread top
    -12.3   boss thread bottom (10.0 mm of full thread)
    -13.5   boss tip (1.2 × 45° lead-in) · motor tube aft end
    -14.1   motor aft face          ─┐ 0.4 mm lip clearance
    -14.5   cap floor / retaining lip ┘  ── 1.0 mm clear of the boss tip
    -17.0   cap tip — 17.0 mm proud of the airframe
```

Overall vehicle length **380.0 → 397.0 mm**.

## 3. Thread

Trapezoidal, **single-start, right-hand, 3.0 mm pitch, 30° flanks, 1.2 mm radial depth.**

| | Major / root | Minor / crest |
|---|---|---|
| Boss (external) | ⌀38.4 | ⌀36.0 |
| Cap (internal) | ⌀38.8 | ⌀36.4 |

Clearance **0.2 mm radial, 0.1 mm per flank**. Radial interlock 1.0 mm.
Engagement 10.0 mm ≈ 3.3 turns.

> ⚠️ **The boss diameters are NOT `../SampleRocketABS33-36`'s, and that is deliberate.**
> Measured off that project's own STLs, its boss ridge occupies r 12.8–14.0 and its cap
> ridge r 14.2–15.4 — **disjoint radial bands, −0.2 mm of overlap.** Those two ridges can
> never interlock; that cap slides off its boss. The rule the pair must satisfy is
> *female root = male major + clearance* and *female crest = male minor + clearance*.
> Phoenix's cap numbers were right; the boss had to grow one full thread depth.

**The cap seats on a 45° cone, not on the thread and not on the boss tip.** Boss and cap
cones lie on the same surface, `r = z + 21.5`, contacting over r 19.4–21.5. The cap's
counterbore floor sits **1.0 mm clear of the boss tip**, so the joint is a preloaded cone
seat — which is also the anti-backout. Hand-tight plus a witness mark; no safety wire in v1.

## 4. Motor interface

| Feature | Value |
|---|---|
| Bore | ⌀18.4 (0.4 mm over an 18 mm casing) |
| Motor bay, clear | 70.0 mm, cap lip to engine block |
| Engine block | 1.0 mm flat ledge at Z +55.9, then 45° to a ⌀14.0 bore — takes flight thrust |
| Cap lip | ⌀15.0 bore, **1.5 mm radial** on the casing's aft rim |
| Lip clearance | 0.4 mm — the block carries thrust, the cap only prevents fall-out |
| Exhaust | ⌀15.0 through a 2.5 mm base, 45° flare to ⌀18 on the aft face so the plume does not scrub a square edge |

> **Measure a spent 18 mm casing before printing.** The ⌀15.0 lip must bear on the casing
> wall, not on a crimped or recessed nozzle edge. If the rim is inset, change `CAP_BORE_R`
> and re-run — it is one constant.

## 4A. Sealed aft section — cfg B

`DESIGN.md` §7.1 commits to spring ejection as the *sole* deployment event. cfg B gives the
motor mount a solid bulkhead: it seals the recovery bay off from the motor, gives the bay a
flat floor, and takes thrust across the motor's whole 18 mm face.

```
  Z  +58.9  BULKHEAD forward face - the forward-most plane of the entire part
     +55.9  bulkhead aft face; the motor's forward face bears directly on it
     +51.4  SHOULDER - OD steps 43 -> 39.7; fwd tube's aft face lands here
     +51.4  fin root forward end          | the lip and the fins share this station,
     +40.0  centering ring 2  (2.5 mm)    | and that is the binding constraint below
     +12.0  centering ring 1              |
      +0.6  fin root aft end              | 3 TTW slots, 2.3 mm wide
       0.0  airframe aft face - wall is OD 43 / ID 40 from here up
      -2.3  seat cone / boss, identical to cfg A
```

Part spans Z −13.5 → **58.9** (72.4 mm), ⌀43.

**The bulkhead is the forward end, and the lip hangs below it.** The lip is not a ring stood
on top of the bulkhead — the bore steps inward over a 4 mm taper just below the shoulder, so
wall and lip are one continuous wall and the bulkhead caps it. The verifier asserts this
directly: the part's maximum Z equals the bulkhead face, to 0.02 mm.

**Forward joint.** The forward tube (ID 40) slides down over the ⌀39.7 lip with **0.3 mm
diametral** epoxy clearance until its aft face lands on the shoulder at Z 51.4. OD is
continuous at ⌀43 across the joint. Bond the annulus and the shoulder both.

> ⚠️ **The lip is only 7.5 mm long, and the fin root is why.** The bulkhead is pinned at the
> motor's forward face (Z 55.9, set by the 70 mm motor and the cap), so the part ends at 58.9.
> The fin root is 50.8 mm and must sit on full ⌀43, so it occupies Z 0.6–51.4. What is left
> between them is 7.5 mm. That is a short lap for a joint that carries recovery shock.
>
> **The lever is the fin root chord, and it is nearly free.** `DESIGN.md` §4.5's own sweep
> shows a *shorter* root slightly *improves* margin (50.8 → +1.77 cal, 65 → +1.67), because
> the trailing edge is pinned and a longer root drags fin CP forward. Shortening it buys lip
> directly:
>
> | Fin root chord | Lip length |
> |---|---|
> | 50.8 mm (current `.ork`) | **7.5 mm** |
> | 45 mm | 13.3 mm |
> | 40 mm | 18.3 mm |
> | 35 mm | 23.3 mm |
>
> This is a `.ork` change and a stability re-run, so it is **not** made here. `SHOULDER_Z` and
> `FIN_ROOT` are single constants in the build script if you want a different split.

**Through-the-wall fin slots.** 3 slots at 0/120/240°, **2.3 mm wide** (2.0 mm fin + 0.15 mm
of epoxy per side), Z 0.6–51.4. They cut the wall **and both centering rings**, stopping
**0.3 mm off the motor tube**, so the fin tab bonds to the mount rather than to the outer skin
alone — the failure mode `DESIGN.md` §9 calls the most common one in printed ABS. The 0.6 mm
aft start clears the cap's forward rim face. Planform is the `.ork` rev 5 set: 3 fins, root
50.8, thickness 2.0, 0° clocking. **The fins themselves are not modeled** — the slots let the
planform change without reprinting this part, which matters while §13 item 1 is open.

**Centering rings** are integral, 2.5 mm, at Z 12 and Z 40, tying the motor tube to the ⌀40
bore. Both sit inside the fin root span, so each fin tab passes through them and bonds to
three members at once. The standalone `FwdCenteringRing` is **not used** in cfg B.

**No vents, and that is deliberate.** An earlier revision carried 2 × ⌀5 mm wall vents, three
motor-tube windows and a plenum, per §7.6's sealed-and-vented mount. **This build has no
ejection charge**, so there was nothing to vent and those were holes in the airframe buying
nothing. Deleting them let the bulkhead drop onto the motor's forward face where it doubles as
the thrust stop, which also deleted the engine-block ring. The verifier now asserts the
airframe wall is unbroken **except at the fin slots**.

> **If a charged motor is ever flown this part is wrong and must be rebuilt.** A charged motor
> against a solid bulkhead with no vent path is §7.6's 433–866 N on a printed disc. It is not a
> flag flip: vents must exit through the ⌀43 wall, which only exists below the shoulder, so the
> bulkhead has to move back down and leave a plenum. Treat it as a new configuration.

**Thrust path.** The motor's ⌀18 forward face (254 mm²) bears flat on the bulkhead against
~15 N — 0.06 MPa. That is why cfg B needs no engine-block ring.

**Mass.** 29.07 g for the section, but 51.4 mm of it *is* airframe — at corrected solid-ABS
density that displaces 10.6 g of body tube, so the net against the `.ork` is **+22.56 g at
362.9 mm**, a 0.47 cal CG penalty against cfg A's 0.45. cfg B is heavier in absolute terms but
carries its mass further forward, so the two land in nearly the same place. Inputs to §13
item 3, not margins to quote.

**Printing.** Same orientation as cfg A — **boss down**, 72.4 mm tall on a ⌀43 footprint.
Radius only increases going up through the seat cone, and the shoulder faces up, so no
supports. Three features bridge: the two centering rings (9.6 mm annular) and the bulkhead
(a ⌀18.4 disc inboard plus a 9.6 mm annulus outboard, anchored on both the motor tube and the
wall). The fin slots leave 2.3 mm-wide gaps whose tops bridge trivially. Run 4 perimeters and
a slow first bridging layer.

> The annulus between the centering rings is no longer a sealed void — the fin slots open it
> to atmosphere until the fins are bonded in. Once they are, seal the slot line with the same
> epoxy fillet that bonds the fin.

## 4B. Fins, and the one-piece fin can — cfg C

**`Fin`** — planform straight from the `.ork` rev 5: root chord 50.8, tip chord 25.0,
semi-span 55.0, LE sweep 25.4, thickness 2.0, three of them at 0/120/240°. **5.45 g each.**

- **Rounded edges.** LE, TE and tip are rounded to a 1.0 mm radius — the `.ork`'s "rounded"
  cross-section — built as a five-section loft (offsets 0 / 0.293 / 1.0 mm at y = 0 / 0.707 /
  1.0) rather than an OCCT fillet. Fillets on a lofted swept plate are exactly the operation
  that has failed repeatedly in this file, and at Mach 0.28 the edge profile is cosmetic.
- **Through-the-wall tab** runs inboard to r 9.8, so it passes the wall and both centring
  rings and lands on the motor tube. Bond it to all three.
- The mid-plane outline is the exact planform, so the 2.3 mm slots in `AftSectionSealed`
  match it with 0.15 mm of epoxy per side.

**`AftFinCan`** — the same section with the fins fused in, no slots, plus **4 mm root
fillets** on both sides of every fin. **46.12 g.** The fillets are constructed, not filleted:
a box minus the airframe cylinder minus a 4 mm cylinder tangent to both the fin face and the
airframe — all boxes and cylinders, which OCCT handles reliably.

### Which one to print

|  | cfg B — slotted + bonded fins | cfg C — one-piece fin can |
|---|---|---|
| Mass (with cap) | 54.45 g | 55.16 g |
| Root joint | TTW tab bonded to wall, rings and motor tube | **continuous material + 4 mm fillet** |
| Supports | **none** | **needed under the 3 fin trailing edges** |
| Fin layer direction | layers parallel to the fin faces — best case in bending | layers perpendicular to the faces |
| Bed footprint | ⌀43 section + 3 flat fins | 133 × 115 mm |
| Planform changes | reprint 3 small fins | reprint the whole section |

> **The support cost is small and specific.** Printed boss-down, the fin springs out its full
> 55 mm span over the 0.4 mm between Z 0.6 and Z 1.0 — the trailing edge is 0.4° off
> horizontal, 14.1 mm above the bed. That is three 55 × 2 mm ledges needing support to the
> plate. Everything else on the part is still support-free. Straight edges, easy to snap off.

**Recommendation: cfg C.** `DESIGN.md` §9 is unambiguous that the fin root is the failure
mode in printed ABS, and a fused root with a 4 mm fillet removes the bond line entirely.
cfg B stays worthwhile while the planform is unconfirmed (§13 item 1) — it lets you reprint
three 5 g fins instead of a 46 g section.

## 5. Printing

ABS in an enclosure, 0.4 nozzle, 0.16–0.20 mm layers, ≥4 perimeters, 40–60 % infill.
Slow the thread walls to ~30 mm/s; ironing off.

| Part | Orientation | Supports |
|---|---|---|
| `AftRetainerBase` | **boss down** — radius only ever increases going up, so the seat cone, the conical web and the engine-block chamfer are all self-supporting | none; brim recommended (footprint is two concentric rings) |
| `MotorRetainerCap` | **base down** — flat ⌀44 disc on the bed | none |
| `FwdCenteringRing` | flat | none |

Two geometry choices exist purely to make the base printable boss-down:

- **A 45° conical seat instead of a flat flange.** A flat land plus a square r 19.2 → 21.5
  step is a 2.3 mm unsupported annular ledge, and there is no axial room to chamfer it
  without eating the seating face. The cone also self-centres the cap. Wedging load is
  negligible — ~50 N of hand preload over the r 21 × 2.6 mm wall is ≈ 0.15 MPa hoop.
- **A 45° conical web tying the motor tube to the boss shell**, replacing what would
  otherwise be a 6.2 mm flat annular bridge printed over air.

## 6. Assembly

1. Test-fit cap on base **before** bonding anything. It should run down by hand and stop
   firmly on the cone with the cap rim ~flush at the airframe's aft face.
2. Bond the base into the airframe: the ⌀39.6 spigot goes into the ⌀40 bore, the airframe's
   aft face lands on the shoulder at Z = 0. The cap's seat is then flush with the tail.
3. Slide `FwdCenteringRing` over the motor tube (⌀21.2 over ⌀20.8 — 0.4 mm of glue gap, not
   a press fit) and bond it to both tube and airframe.
4. Load the motor from the tail; it seats on the engine block. Screw the cap down hand-tight.

## 7. Verification

```
"C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" \
    Models/PhoenixABS40-43_aft_retention_v1.py      # build   (~35 s)
python Models/verify_aft_retention.py               # verify  (~45 s)
```

The build script reports mass, envelope, watertightness and the CG delta. **It makes no
claim about the thread** — see §8. `verify_aft_retention.py` is the authority: it ray-casts
the exported STLs (the files that actually get printed) and checks thread fill fractions,
that the cap clears the boss through a full 0–720° unscrew sweep, that the motor bay is
clear, that the lip backs the casing rim, and that the exhaust bore is open.

Current result: **all checks pass**, clash 0.000 % at every position through the sweep.

### The negative control — why 0.000 % is believed

A clash check that reads exactly zero at all twelve sweep positions is indistinguishable
from a check that cannot fail, so it was tested against a pair built to interfere:

```
# copy the build script, point PROJECT at a scratch dir, then invert the clearances:
RAD_CLEAR   =  0.2  ->  -0.2      # cap channel 0.2 mm too small radially
FLANK_CLEAR =  0.1  ->  -0.1      # and 0.1 mm too narrow per flank
# rebuild, then run the verifier against the scratch Print Files
```

| | shipped pair | deliberately interfering pair |
|---|---|---|
| `[2]` cap thread fill | 41 % | **67 %** (channel too small, so more material stands) |
| `[3]` clash, seated | **0.000 %** | **10.491 %** — FAIL |
| clash location | — | r 18.30–19.20, z −13.19…−2.70 |

The clash it finds sits exactly in the thread interlock band (r 18.0–19.2) over exactly the
thread span, which is where a real interference must be. **The check discriminates.** Re-run
this control if the thread geometry or the verifier's sampling is ever changed.

## 8. Why the thread is a faceted helix, and why the build script does not check it

Four failure modes were hit and diagnosed here. They are recorded because every one of
them **passed silently** — bad geometry with a clean-looking report.

1. **`makePipeShell(..., isFrenet=True)`** produces correct geometry, but every boolean
   against the result silently returns the *other operand*. `common()` reports 0 mm³ on
   solids that plainly overlap, so the thread simply vanished from the part with no error.
2. **`isFrenet=False`** makes booleans work, but the corrected frame drifts: measured
   thread pitch came out **3.2 mm instead of 3.0**, so the two parts could not mate.
3. **`setAuxiliarySpine` / `setBiNormalMode`** raise argument-signature errors in
   FreeCAD 1.1.3.
4. **Fusing a swept ridge onto a core cylinder** loses it — whether the two merely touch
   (leaving a non-manifold seam) or genuinely overlap.

The fix is to **generate the helix directly as an exact faceted solid** (`thread_solid()`):
exact pitch by construction, planar faces only — which OCCT booleans handle reliably — and
no frame drift. Faceting error is `r·(1−cos(π/90))` ≈ **0.012 mm** at the crest, against
0.2 mm of radial clearance. Measured back off the STL: ridge width 1.591 mm (nominal 1.593),
**spacing 3.0000 mm**.

Two consequences to know about:

- **OCCT booleans against these parts are not trustworthy**, so the build script no longer
  attempts them. Its earlier boolean checks reported `0.000 mm³ interference — PASS` on
  parts that were interfering by 2515 mm³, and material fill fractions of 147 % and −24 %.
  Every geometric claim about the thread now comes from ray casting in the verifier.
- **The STEP files are large** (3–4 MB) and faceted, not analytic surfaces. They are exact
  and printable, but they are not a pleasant parametric solid to edit downstream. The
  parametric source is the `.py`, as `DESIGN.md` §12 intends.

Also worth knowing: the verifier's own probe points originally sat on exactly the radii
and angles the mesh vertices do, so +Z rays passed through edges and parity came out wrong —
reported as `98 %` where the answer had to be 100 %, and a phantom 1 % clash. Sample points
are now jittered by 1e-4 mm.

## 9. `.ork` deltas this design forces

`DESIGN.md` §13 item 14 tracks this. Not yet applied to the model.

| Field | Current | New | Why |
|---|---|---|---|
| Fin set `position bottom` | −0.004 (4 mm overhang) | **0** | a proud cap and an overhanging fin cannot coexist |
| Inner tube `position bottom` | 0.0 | **−0.0135** | motor tube now reaches into the cap |
| Inner tube `length` | 0.075 | **0.0724** | |
| Inner tube `thickness` | 0.0005 | **0.0012** | 0.5 mm is not printable |
| Inner tube `outerradius` | 0.0095 | **0.0104** | follows from the wall |
| Motor `overhang` | 0.003 | **0.0** | motor seats on the engine block |
| Centering rings ×2 | cardboard 2 mm | one absorbed into the base, one becomes `FwdCenteringRing` (ABS, 3 mm) | |
| Engine block | cardboard, mount top +2 mm | ABS ⌀14 shoulder at Z +55.9 | integral to the motor tube |
| Overall length | 380.0 mm | **397.0 mm** | cap protrudes 17.0 mm |
| — | — | **+18.91 g net at 378.5 mm** | 23.91 g of new parts less ~5 g displaced |

CG effect against the `.ork` baseline (128 g @ 228 mm): **+19.4 mm, 0.45 cal** on its own;
**+13.0 mm, 0.30 cal** with §3's body-tube correction also applied. Per `DESIGN.md` §7.11's
own rule these are inputs to the §13 item 3 re-run, not a margin to quote.

## 9A. Assembled view

`PhoenixABS40-43_aft_assembly_v1.py` builds
`Models/PhoenixABS40-43_aft_assembly_v1.FCStd` — everything in flight position, one
document. It reads the verified STEP exports rather than rebuilding, so what you look at
is what was checked.

| In the document | |
|---|---|
| `AftSectionSealed`, `MotorRetainerCap` | the real parts, from their STEP exports |
| `Fin_A/B/C` | **reference only** — planform from `.ork` rev 5, flattened to a 2 mm plate. The `.ork` calls for a rounded section, and item 1 has not confirmed this planform. Not exported for printing. |
| `DummyMotor` | 18 × 70 stand-in, shown loaded and seated on the bulkhead |
| `FwdTubeStub` | 60 mm of forward airframe, slid over the lip and seated on the shoulder |

The script also runs pairwise interference across the assembly — section, cap, motor, fin
and forward tube are all **0.000 mm³** against each other.

> **Colours are not set.** FreeCADCmd has no `ViewObject`, so the document opens in default
> grey. Assign colours in the GUI if you want the §10 livery.

**Preview renders.** `render_aft_assembly.py` (plain numpy, no FreeCAD, no image library)
rasterises the coarse meshes the assembly script drops in `Models/_render/`:

```
python Models/render_aft_assembly.py     # ~5 s
```

- `_render/aft_assembly_iso.png` — three-quarter view, assembled
- `_render/aft_assembly_section.png` — longitudinal half-section
- (and any custom view; `render()` takes azimuth, elevation and a body subset)

The half-section is the useful one: it shows the cap's thread teeth interleaved with the
boss's, the 45° seat cone, the conical web, both centring rings crossing the annulus, the
motor seated against the bulkhead, and the lip stepping down at the forward end.

## 10. Open items

1. **Measure a spent casing** and confirm the ⌀15.0 lip bears on the casing wall (§4).
2. **Print and fit-test.** No CAD check replaces screwing the two parts together cold.
   The 0.2 mm radial / 0.1 mm flank clearance is inherited from a printed pair that worked
   at ⌀28; it has not been printed at ⌀38.
3. ✅ **Sealed bulkhead now exists — as cfg B (§4A).** cfg A's open ⌀14 engine block stays
   the right answer for the plugged motor in the brief; cfg B is the one to build if a
   charged motor is ever flown. **Decide which configuration you are building before
   printing** — they are not interchangeable, and cfg B replaces 71 mm of the body tube.
4. **cfg B assumes the plugged motor holds.** If the motor choice ever changes, `VENTED = True`
   and a rebuild are mandatory before flight — a charged motor against a solid bulkhead with
   no vent path is §7.6's 433–866 N on a printed disc.
5. **⚠️ The lip is 7.5 mm and unproven.** See §4A: the fin root pins it. Recovery shock passes
   through this joint. Either shorten the fin root (§4A table — nearly free, and §4.5 says it
   slightly helps margin) or add a separate internal coupler forward of the shoulder.
6. **Fins are the `.ork` rev 5 planform, which §13 item 1 has not confirmed in OpenRocket.**
   Slot width assumes a 2.0 mm fin and 0.15 mm of epoxy per side — check against a printed fin
   before committing. If the planform moves, cfg B reprints three 5 g fins; cfg C reprints the
   whole 46 g section.
7. **The root fillet is printed, not tested.** 4 mm on both sides of a 2 mm fin is generous,
   but §4.5 notes the rev-5 tip radius gives **1.5× the root bending moment** of the old
   planform for the same tip impact. Landing loads are the case to worry about.
8. **Propagate §9 into the `.ork`** before the §13 item 3 simulation re-run.
9. **Grip ribs are untested ergonomically** — 8 ribs, 0.75 mm proud (⌀45.5 over a ⌀44 cap).
   Fine in CAD; confirm they can be turned with cold hands.

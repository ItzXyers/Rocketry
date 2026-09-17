# Phoenix ABS 40‑43 — servo‑released spring ejection, POC **v1 (sliding catch)**

Design logic and build record for `PhoenixABS40-43_ejection_poc_v1.py` and its outputs.
This document stands alone; it deliberately does **not** depend on the vehicle‑level
`DESIGN.md` (which is out of date on this subsystem).

Frame throughout: **Z along the tube axis, +Z toward the nose, Z = 0 at the anchor
bulkhead's forward face.** Airframe ⌀43 OD / ⌀40 ID.

---

## 0. Status at a glance

| Item | State |
|---|---|
| Mechanism architecture | ✅ **Fixed — sliding catch on a pinned collar, crank‑driven, dead‑centre held.** Replaces the scrapped v0 annular‑cam attempt (§3.3). |
| Fits the ⌀40 bore | ✅ Verified over the full knob sweep — worst moving radius 19.2 mm vs the 19.5 mm limit. |
| Threaded rod | ✅ **Eliminated.** No metal spine — the shaft is a printed ⌀6 part (a ⌀6 CF rod is an optional drop‑in, §10.2). |
| Nothing glued to the piston | ✅ **rev (e) 2026‑09‑10.** `PistonHead` + `Shaft` are **one printed part `PistonShaft`** — no socket, no glue joint. The `CatchCollar` is **not solvent‑welded** — two identical halves retained by one transverse **⌀1.5 pin** through half + shaft + half, fitted last through the access slot. |
| Shaft robustness | ⏳ **rev (e).** `PistonShaft` prints **axially** (whole part on its side, ⌀38 disc edge‑on with support). Two handling stations: the counterbore root **~8 N** in‑plane (knock near the stub), and the **⌀1.5 pin cross‑hole ~2 N** in‑plane (knock near the head — net section ~56 % of gross, `Kt` 2.0, conservative). Handle the piston by the head; a ⌀6 pultruded CF rod down the finished head (~284 N) is the real fix (§10.2). Report **[5b]** prints both every run. |
| Catch load direction | ✅ **FIXED (Option B, §6.14).** Catch is a CatchCollar whose top face reacts +Z into a full‑diameter plate; free rise **0.075 mm** (0.025 geometric + 0.05 mm pin‑hole lost motion — [5b] measures the collar lagging the shaft, not a fused body), bounded by a positive cocking stop at **1.0 mm**. The shaft→collar joint is the ⌀1.5 pin in **double shear** (9.6 MPa vs ~30). Report **[5b] PASSES**; the impact‑tension net section at the pin hole is 33 MPa vs ~40 in‑plane under the rigid‑drop DAF (PASS, ~3× realistic). |
| Assemblability | ✅ **Geometry verified; re‑run 2026‑09‑10 (e).** Every moving/removable fit derives from the `CL_*` block and passes report **[F]**; **[T]** checks thin features *within* each part. Re‑slice from `Print Files/Ejection System/`. |
| All fasteners printable | ✅ Crank pin (⌀3), RBF pin (⌀2) **and CatchCollar pin (⌀1.5)** are printed parts. Only non‑printed items: the spring, 3× M3 screws. |
| Spring rate / `F_max` | ❌ **UNMEASURED.** Whole design is checked against `F_MAX_ASSUMED = 34 N`; nothing is *gated* by it (§10). |
| Servo | ⏸ v1 is a **manual knob**. Servo mounts later on the knob's D‑flat (§10). |
| Simulation / flight clearance | ❌ Not done. This is a bench POC. |
| Parts | 8 printed (`Cage`, `BulkheadDisc`, **`PistonShaft`**, `Slider`, **`CatchCollar`** × 2 identical halves, `Knob`, `TubeStub`, `DummyNose`) + printed pins (⌀3 crank, ⌀2 RBF, ⌀1.5 collar). **All checks PASS** except: **[T]** flags the collar's D‑flat wall at −0.05 mm (prints as a C — **accepted, unfixable in this layout**, §6.14) and warns "thin" on the disc rim at the peg holes (§10.12); **[5b]** flags the piston as WEAK in careless handling (§10.2). |
| Source of truth | ✅ **`PhoenixABS40-43_ejection_poc_v1.py`.** Revisions (b)/(c)/(d)/(e) were prototyped then fully back‑ported; the script was re‑run and regenerated every output (STEP → `Models/`, STL → `Print Files/Ejection System/…`). Edit the script, re‑run, never edit the STL/STEP/FCStd. |

---

## 1. Scope

A **proof of concept of the release event only**: cock the real spring, hold it against
structure, and let go on command — by hand now, by a 9 g servo later. It is
**airframe‑representative** (drops into the ⌀40 bore, screws to the wall) so the same
parts migrate toward the flight bay, but it is **not** a flight article: no motor
interface, no recovery harness, no qualification.

Given: a compression spring, **free ≈ 85 mm, cocked ≈ 45 mm, ⌀10 mm OD**, working
stroke **40 mm**, wire gauge and rate unknown.

---

## 2. The brief this is built against

1. **Servo‑released spring is the sole deployment event.** The release must be
   mechanical and reusable — no pyro, no shear pins.
2. **Everything fits inside the ⌀40 mm airframe bore** — spring, piston, latch, knob,
   and the future servo.
3. **The cocked load is held by geometry, not by servo/knob torque.** A servo with no
   signal goes limp; a brownout on the pad must not deploy the rocket.
4. **Fully 3D‑printable** (ABS), minimum bought hardware.
5. **No threaded rod** as a structural spine (explicit user constraint).
6. The spring **will buckle unguided** at L/D 8.5 and ~47 % compression — it needs a
   guide.
7. `F_max` is unknown until measured, so the design must be **robust across 7–53 N**
   (the plausible range for ⌀10 × 85/45 wire gauges) and re‑validate by re‑running,
   not by redesign.

---

## 3. Design logic — why a sliding catch

### 3.1 What the release has to do

Hold a piston down against ~34 N (assumed) of cocked spring, react that load into the
airframe, and on command move something a few millimetres so the piston is free —
without the actuator ever carrying the spring load, and inside a ⌀40 tube that already
has a ⌀10 spring and a piston up its middle.

### 3.2 Why "the servo just slides a pin out" is hard here

The intuitive latch — a cross‑pin through the shaft, in brackets, that the servo pulls
sideways — runs into the bore. To fully withdraw a pin from a collar/shaft on the tube
axis you need ~10–15 mm of travel; a servo crank or an offset cam that fits beside the
⌀10 spine in a ⌀40 tube tops out near 6–7 mm. Every "actuator offset from the axis"
layout fights the wall.

### 3.3 Rejected — v0: annular cam + straight‑offset slots

The first attempt put a rotating annular cam on the tube axis with two **straight
offset slots** (`x_follower = x0 / cos θ`), driving two opposed ⌀3 latch pins ~2.4 mm
each. It *worked* and it *fit* and it had a clean dead‑centre at ARMED — but:

- **2.4 mm of pin travel is illegible.** You cannot see it move, so you cannot trust
  it or explain it.
- Two opposed pins + L‑shaped follower tongues + a journalled cam plate is a lot of
  cramped, thin, support‑hungry printed geometry for what is meant to be a POC.
- Margins ran to 0.2–0.5 mm in several places.

It was scrapped. Lesson kept: **legibility is a design requirement for a POC** — if
the person building it can't watch it work, the design is wrong for the job.

### 3.4 Rejected — over‑centre servo linkage on a cross pin

A four‑bar over‑centre linkage that makes the spring load produce zero torque about the
servo shaft. Meets requirement 3, but: it is geometry you have to get exactly right,
verify by test, and it still needs the pin to travel far enough to clear the shaft
(§3.2). More failure modes than the alternative, not fewer.

### 3.5 Chosen — catch face + sliding fork + crank

> The original form of this used a **groove shoulder** turned into the shaft. That was
> replaced by a **bonded CatchCollar** (§6.14, rev (c)), the shaft split into
> `PistonHead` + `Shaft` (§6.15, rev (d)), then **rejoined into one `PistonShaft`** and
> the collar **un‑bonded — pin‑retained** (§6.14/§6.15, rev (e)). The kinematics below
> are unchanged; read "collar top face" for "shoulder".

- The **PistonShaft** (one part) carries a **CatchCollar** near its lower end, retained
  by a transverse **⌀1.5 pin**. The collar's **top face** is an **upward‑facing** catch
  surface.
- A flat printed **Slider** in a channel across the cage has a **U‑notch** whose rim
  bears **down** on that top face. Cocked spring load: shaft → **collar pin (double
  shear)** → collar top → slider → a full‑diameter **reaction plate** fused to the cage
  legs → 3 M3 screws → airframe. **The knob carries none of it** — the load is axial (Z),
  the slider moves radially (X), the two are orthogonal. (The fixed **ledge** below the
  slider hosts the knob journal, carries the slider, and its stepped bore is the
  positive cocking stop.)
- The **Knob** has an off‑centre **crank pin** riding a cross‑slot in the slider
  (a scotch‑yoke). Turn the knob 180° and the crank pin swings the slider **6 mm**
  clear of the collar → spring fires.
- **ARMED (θ = 0°) and FIRED (θ = 180°) are both crank dead centres** (`dX/dθ = 0`).
  A shove on the slider produces zero knob torque at either end. The hold is geometric.
  **There is no detent** (§10.19) — between ARM and FIRE only slider friction holds it;
  at ARMED the dead centre plus the RBF pin through the knob are the hold.

Travel needed to release = notch radius + shaft radius ≈ 1.8 + 3 = 4.8 mm; provided
6 mm (crank radius 3, sweep 180°). This is the smallest, most readable mechanism that
meets all seven brief points in a ⌀40 tube.

---

## 4. How it works

```
   PISTON HEAD  ────────────█████████████  ⌀38, on the 45 mm spring; ONE part with the shaft
                                 │  ⌀6 SHAFT, no joint -- PistonShaft prints AXIALLY (6.15/e)
   bulkhead disc  ══════╤════════│════════╤══════   ⌀39.5, slides on the shaft,
    (slides on,  ════════╡═══[ spring ]═══╡═════    locates on the cage-leg pegs
     screws retain)      │                │        (light push), 3× M3 screws hold
        cage legs  ║      │                │      ║
                   ║      │                │      ║   ⌀6 shaft, SOLID -- one ⌀1.5 pin cross-hole (6.14/e)
    REACTION PLATE ╬══════╪════════════════╪══════╬   <- THIS takes the +Z load
          (fixed)  ║      │                │      ║      (v1 reacted into a 2 mm bridged lip)
        SLIDER ────╫ ████████████████████████████ ╫   rim bears DOWN on the collar top
   CatchCOLLAR ────╫    ▓▓▓▓▓▓●▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ╫   ⌀9×4, TWO IDENTICAL HALVES + a ⌀1.5 PIN (●)
        LEDGE  ════╬══════╪════════════════╪══════╬   1.0 mm under the collar this bore
          (shelf)  ║      │                │      ║   steps to ⌀6.8 = POSITIVE COCKING
        carrier ═══╬══════╪════════════════╪══════╬   STOP, so free rise is BOUNDED
                   ●──crank pin (⌀3) ── in the slider's cross-slot
        KNOB  ────╮╰──────┤ off-axis at X = -8, radius 3 ─── D-flat (servo later)
             grip ╯  ⌀5.5 spigot = the lateral bearing (clear of the crank pin)
                     RBF pin ⊗ at r 15 from the axis -- SOLID carrier (10.16)
```

*(rev (e): the ledge is deepened 4→6 mm to fit the taller collar, so the carrier / knob /
tube‑stub bottom all sit ~2 mm further aft than the Z's drawn above.)*

**ARM → FIRE:** knob 0 → 180°. Crank pin world‑X goes −5 → −11; the slider,
constrained to X by its rails, follows: `dX = 3·(cos θ − 1)`, 0 → −6 mm. The notch
(which opens toward +X) slides off the **collar**; the spring drives the
piston + shaft + nose up. The stroke self‑limits when the spring reaches free length
(§6.2). ARMED is re‑established by pressing the piston back down ~40 mm and turning the
knob to ARM.

---

## 5. Parts and the numbers that define them

| Part | Defining geometry | Why |
|---|---|---|
| **PistonShaft** | ⌀38 × 8 piston disc; ⌀13 × 4 hub; ⌀11.5 × 2.5 spring‑seat counterbore; **R0.3 counterbore‑root fillet** (peak ⌀6.6 clears the assumed spring ID 7.2); ⌀6 **SOLID shaft** Z −63 → 42.5 to the counterbore root, 45° stub lead‑in; **one ⌀1.55 cross‑hole at Z −58** for the collar pin (reamed line‑to‑line on the ⌀1.5 pin); ⌀1.6 hub‑cap tether cross‑hole | rev (e): **one part, no joint** (nothing glued to the piston). Prints **AXIALLY** (whole part on its side, layers along the shaft — bending in‑plane ~40 MPa vs ~20 interlayer); the ⌀38 disc prints **edge‑on** with support on its lower rim. ⌀6 < spring ID (7.2) so the shaft **is** the buckling guide and threads the ⌀6.8 bulkhead bore. A ⌀6 CF rod down the finished head is the robust upgrade (§10.2) |
| **Cage** | 4 legs at ⌀35.2, tops at Z −8 with **⌀3 pegs** (1.2 mm lead cone); fixed **ledge Z −56…−62** (deepened 4→6 mm, rev (e)) with the slider channel (rails + lip, pocket = slider + `CL_SLIDE`) and the ⌀9.8 collar pocket → ⌀6.8 stop shelf; knob **journal** ⌀8.4 at (−8, 0); carrier Z −62…−67; 3 radial M3 holes at the ledge | ledge hosts the collar pocket + the reaction; the deeper ledge fits the 4 mm collar; journal sets the crank axis clear of the ⌀6 shaft; pegs locate, screws retain (§6.4) |
| **BulkheadDisc** | ⌀39.5 × 8; ⌀6.8 shaft bore; ⌀11.5 spring‑seat counterbore; 4× ⌀3.2 blind peg holes, 5.5 deep (0.55 mm wall to the OD — a watch item, §10.12); 3 radial M3 holes | separate from the cage so it can **slide onto the shaft over the spring** (§6.3); ⌀3.2 vs ⌀3 peg = 0.2 mm dia clearance, a **locating** fit — the M3 screws retain |
| **CatchCollar** | ⌀9 × **4.0** (rev (e) — was 2.0, grew for pin headroom), D‑flat at x −3.1, ⌀6.1 bore, **⌀1.55 pin hole along Y at mid‑height**; **printed as two identical halves split at y = 0** | the catch (§6.14). Top face = the upward‑facing surface the slider bears on. Retained by a transverse **⌀1.5 pin** (half + shaft + half) in **double shear**, not a bond — fitted last through the access slot; the hole is reamed line‑to‑line (~0.05 mm dia), not a loose `CL_CLAMP` — its slop is [5b] free rise. D‑flat clears the crank‑pin sweep; it sits 0.05 mm inside the bore edge so the collar **prints as a C, not a D** — harmless now the load goes through the pin. Halves let a ⌀9 collar onto a shaft that must thread a ⌀6.8 bore |
| **Slider** | ~13 × 12.3 × 4 bar (**nominal — all fit slop is in the cage pocket**); **⌀6.8** U‑notch opening +X; crank cross‑slot ±1.9 in X (drive), −1.5…+6.5 in Y (idle); thumb tab out the access slot | notch only has to clear the **⌀6 shaft** (+0.40 radial, `CL_BORE`); its rim bears on the CatchCollar’s top face (11.69 mm², 2.9 MPa); slot long in Y absorbs the crank pin's Y swing |
| **Knob** | ⌀20 grip offset to axis (−8, 0); ⌀7.6 journal shaft (0.4 radial in the ⌀8.4 journal); crank‑pin bore ⌀3.4 at radius 3; D‑flat; ⌀2.5 RBF hole. Sits ~2 mm further aft (Z −62.5…−75) than pre‑rev‑(e) | offset −8 keeps grip + travel inside R 19.5; radius 3 → 6 mm slider travel over 180°; bore +0.2 for a **printed** pin |
| **TubeStub** | ⌀43/⌀40 × ~171; longitudinal viewing window (+Y); access slot (+X) over the latch/knob; 6 radial M3 holes | airframe stand‑in; window to watch it work; slot to insert the slider, RBF, the collar pin, and turn the knob |
| **DummyNose** | ⌀39.0 × 25 hollow plug, 2 friction bands (⌀39.0 on a ⌀37.4 shoulder — 0.8 mm proud so they print as **distinct** bands; was ⌀38.8, 0.1 mm proud → sub‑nozzle, [T]), ⌀8 axial hole | the visible "it fired" object; slides free — bands are light drag, not a press; the axial hole is a poke‑through for cocking |
| *pins* | printed ⌀3 crank pin + ⌀2 RBF pin (small head + lead chamfer) + **⌀1.5 collar pin (HEADLESS — a head fouls the ledge pocket)** (`ejection_poc_test_pins.py`) | requirement 4 — nothing metal but the spring and screws. [P] cross‑checks the pin lengths against this script's geometry |

---

## 6. Decisions and rationale

### 6.1 Integral printed shaft, no threaded rod
The rod was carrying three jobs — spring guide, tension member, cocking screw — and it
was an imposed part the brief rules out (requirement 5). Folding the shaft into the
piston removes the rod, the nuts, and the DrawCollar. The shaft sees ~34 N in
**compression**‑then‑tension along its length: ~1 MPa, trivial even inter‑layer.

### 6.2 ⌀6 the whole way — no ⌀11 stop flange
An earlier version put a ⌀11 flange mid‑shaft as a positive 40 mm stop. It made the
part **unassemblable**: the flange cannot pass the ⌀6.8 bulkhead bore, from either end.
Removed. The shaft is now ⌀6 from the piston to the groove, so it threads straight
through. **Stroke limiting** is now: (a) the spring reaching free length — gentle,
self‑limiting; (b) for the first bench fires, a short tether from the hub cross‑hole
to a cage leg. A positive stop is a flight‑article item (§10).

### 6.3 Two‑piece bulkhead: `Cage` + slide‑on `BulkheadDisc`
Because the piston/shaft is one rigid part with a ⌀38 disc on one end, the spring and a
one‑piece bulkhead could never get onto the shaft. Splitting the disc off lets the
assembly be: spring on from the stub end → disc on from the stub end → the whole stack
drops into the cage from the top. Verified: nothing on the shaft below Z −8 exceeds the
⌀6.8 bore.

### 6.4 Legs peg into the disc (not glued)
User request, "for the time being." Each leg top has a ⌀3 peg with a 1.2 mm lead cone;
the disc has ⌀3.2 blind holes → **0.2 mm diametral clearance, a locating fit** — a light
hand push, and it comes apart by hand. The lead‑in is the cone on the peg (a funnel in
the disc hole would break through the thin disc rim at that radius, §10.12). The 3
radial M3 tube screws are the retention; the pegs only clock the disc and hold it
during handling.

This was **⌀2.9 in / ⌀3 peg = 0.1 mm interference** in v1‑as‑first‑printed, described as
a "press/click." On an FDM printer a ⌀3 hole comes out ~0.2–0.4 mm undersize and a ⌀3
post ~0.1–0.2 mm oversize, so that nominal 0.1 mm interference prints as a 0.3–0.5 mm
jam — the disc will not seat, or it splits the thin web around the hole. It also never
"clicked": a straight cylinder in a blind hole is a press, not a snap. **A real click
needs a barbed peg into a through‑hole with a relief groove, or cantilever snap
fingers** — a redesign, deferred; the locating fit + screws is the right default here
(§6.11, §10.7).

### 6.11 FDM fit clearances are a named block, checked by report section [F]
Every moving or removable interface is now derived from one of six constants
(`CL_SLIDE`, `CL_ROT`, `CL_BORE`, `CL_PIN`, `CL_PEG`, `CL_TUBE`) at the top of the
script, sized for ABS on a 0.4 mm nozzle. The slider channel is the worst v1 offender:
the rails sat on `SLIDER_YW_LO/HI` and the lip on `SLIDER_Z1` — **exactly** the slider
faces, a 0.00 mm sliding fit on three surfaces. It is now `slider nominal + CL_SLIDE`,
with **all the slop in the fixed cage pocket** so the ledge top (the load reaction
face) and the notch‑under‑shoulder engagement do not move. `CL_SLIDE = 0.5` (not 0.4):
the cage lip is a downward‑facing bridge over the channel (0.2–0.3 mm print sag) and
the slider base carries elephant's foot.

Why v1 passed every check and still jammed: sections [4], [5] and [7] measure fits with
`Shape.common().Volume`, which reads **0 mm³ for a 0.00 mm gap and for a 0.50 mm gap
alike** — a boolean can only see *interference*, never *insufficient clearance*. Report
section **[F]** now checks each fit gap by arithmetic on the constants and flags the
thinnest one; it is the check that would have caught this before the first print, and
the one that protects the next `STROKE` edit.

### 6.12 The ⌀2.8 groove neck was the brittle part — ⌀4.0 filleted *(superseded by §6.14)*
> **Superseded.** This widened the neck; §6.14 removed it altogether. Kept for the
> reasoning and the numbers — they are what sized the collar.

The shaft printed brittle, and the reason was not the ~105 mm ⌀6 tower (§10.2) but the
groove that interrupts it. Section modulus `Z = πd³/32`:

| Section | Z | M_fail @ 20 MPa interlayer | Side force at the piston to break it |
|---|---|---|---|
| ⌀6 shaft | 21.2 mm³ | 424 N·mm | ~4.5 N |
| ⌀2.8 neck (**was**) | 2.15 mm³ | 43 N·mm | **~0.4 N** |
| ⌀4.0 neck (**now**) | 6.28 mm³ | 126 N·mm | ~1.1 N |

Lever arm neck→piston ≈ 112 mm, so 0.4 N is 40 g of sideways nudge — the piston head
alone (~10 g) spends a quarter of the old neck's capacity just being held horizontally.
Printed shaft‑up, every layer boundary is normal to the bending axis, so this is raw
interlayer adhesion; and a ⌀2.8 circle at a 0.4 mm nozzle slices as ~3 touching
perimeter loops with no infill — a column of Z‑seam start/stop defects running the
length of the neck, which is exactly where the crack starts.

**Changed:** `GROOVE_R` 1.4 → **2.0**, `NOTCH_R` 1.8 → **2.6** to follow it, R0.3 fillets
at both groove roots (sharp step Kt ≈ 2.8 → ≈ 2.0), and an R0.3 fillet where the shaft
meets the counterbore floor — the other sharp root, and the one at maximum bending
moment when the part is handled by the piston.

Net: **×2.9 on neck bending, ×2.0 on neck tension area, ×~1.4 on the stress
concentration.** Combined with a flat print (below) it is ~8× the original.

**What bounded each number** (all re‑verified in FreeCAD, see the run log):

| Constant | Was | Now | What stopped it going further |
|---|---|---|---|
| `GROOVE_R` | 1.4 | 2.0 | catch land `SHAFT_R − GROOVE_R` = 1.0 mm; bearing 7.9 MPa vs 40 |
| `NOTCH_R` | 1.8 | 2.6 | slider −Y web `\|SLIDER_YW_LO\| − NOTCH_R` = 1.4 mm; and `SLIDER_TRAVEL` ≥ `NOTCH_R + SHAFT_R` = 5.6, provided 6.0 |
| groove fillet | — | R0.3 | fillet peak ⌀4.6 needs a **running** 0.30 gap inside the ⌀5.2 notch — both fillets are in the slider's path (upper on insertion at ARMED, lower on retraction at FIRE), so this is a sliding fit, not a static one (§6.11) |
| root fillet | — | R0.3 | peak ⌀6.6 must stay inside the assumed spring ID 7.2 (§10.1) |
| `SHAFT_R` | 3.0 | 3.0 | **not raised** — only ×1.46, and it spends margin against an *unmeasured* spring ID |

⚠ **Do not buy notch clearance with `SLIDER_TRAVEL`.** Swept `R_max` is 19.235 against
the 19.5 limit, and that number is the slider's thumb tab at FIRED; travel moves it 1:1,
so +0.3 mm fails containment [0]. Shorten the tab instead.

**Print orientation.** *(rev (d) split the part; rev (e) rejoined it — see §6.15. The
para below is rev (d)-era; read `PistonShaft` for `Shaft`, and the ⌀38 disc now prints
edge-on with support, not on the bed.)* `Shaft` prints **axially** by default
(`Ready to Print/`): perimeters run **along** the shaft, so bending loads in‑plane ABS
(~40 MPa) not interlayer (~20), ~×2. The cost that hasn't gone away: **0.2–0.4 mm of
sag/elephant‑foot** on a shaft that has only 0.4 mm of ⌀6.8‑bore clearance — **sand the
shaft round** before assembly, or drop in a ⌀6 CF rod (§10.2) and skip the problem.

### 6.13 The catch cannot simply be flipped — a groove loads the neck by construction
Confirmed 2026‑09‑06: **the shaft snapped while being cocked.** That is the lip collision
(§10.14) — the ⌀6 shaft cannot reach the cocked position because the retaining lip is
solid across its path, and forcing it loads the neck's upper root sideways. That defect
is fixed. But diagnosing it exposed the deeper problem.

The spring drives the shaft **+Z**, so the catch must present an **upward‑facing** face on
the shaft for the slider to press down on. On a turned groove the only upward‑facing face
is the groove's *lower* root. And the force has to get from the piston, down the ⌀6
shaft, across the groove, to that lower root — **through the neck, in tension**.

So a groove‑and‑fork catch that resists +Z pulls the neck in tension *by construction*.
**Reversing the reaction face is necessary but not sufficient.** Report [5b] now measures
this directly (free +Z travel before the catch bites: **2.05 mm**) and fails.

**Option A — short‑lost‑motion groove + a real reaction plate.** Slider underside bears on
the groove's lower root; groove height becomes slider thickness + ~0.5 mm instead of
6 mm, so free rise drops 2.05 → ~0.5 mm. Replace the 2 mm bridged `lip` with a
full‑diameter plate fused to the legs, ⌀6.8 bore. The neck stays in the load path
(2.71 MPa nominal × Kt 2.0 = 5.4 MPa static vs ~20 interlayer) but the impact factor
drops with the drop height. *Cost:* cocking gets fussy — you must press to within
~0.5 mm for the slider to enter. A lead chamfer on the notch rim helps.

**Option B — a separate catch collar, and no neck at all. ← recommended.** The shaft stays
**⌀6 unbroken** from the piston to the stub end; a shallow ⌀5.4 × 0.5 locating step
replaces the groove (a 0.3 mm shoulder, `Z` = 15.5 mm³ — still 2.5× the ⌀4.0 neck). A
printed collar (⌀9 × 8, slotted so it goes on sideways) drops onto the step *after* the
bulkhead disc is on and is solvent‑welded. Its top face is the upward‑facing catch face;
the slider bears on that, reacted by the plate above.

| | Now | Option A | Option B |
|---|---|---|---|
| weakest section | ⌀4.0 neck | ⌀4.0 neck | **⌀6.0 shaft** |
| side‑load to break | 1.12 N | 1.12 N | **3.79 N** |
| neck tension at 34 N | 2.71 MPa | 2.71 MPa | **none — not in the path** |
| free rise / impact | 2.05 mm | ~0.5 mm | ~0.5 mm |
| extra parts | — | — | 1 printed collar |

> **Superseded by rev (e) (§6.14): the pin is the load path, not a bond.** The collar is
> retained by a transverse ⌀1.5 pin in double shear, not solvent‑welded — there is no
> glued interface carrying load. The shear‑area line below and the "acetone‑welded"
> framing are the pre‑(e) plan; kept for the trade rationale only.

~~Option B's bond carries the full 34 N in shear over π·6·8 = 151 mm² → **0.22 MPa**, which
is nothing for an acetone‑welded ABS joint.~~ It costs one printed part and keeps the
brief's "no bought hardware" (requirement 4). ~~**Not yet built — needs your call.**~~ (Built in (e).)

### 6.14 Option B built: the groove is gone, the catch is a bonded collar
§6.13 costed two fixes; **B is built.** The shaft is **⌀6 solid** end to end.

> **Rev (d) update.** (c) left a ⌀5.4 × 0.8 locating groove "that the collar encases",
> keyed by a rib inside the collar bore. That rib was **0.25 mm thick radially** — under
> one nozzle width, so it never printed (report **[T]** flags this class now). With the
> rib gone the groove located nothing and backstopped nothing while costing ~27 % of the
> local section and two R0.2 raisers, so **both the groove and the rib are deleted**. The
> collar now locates at glue‑up by sitting flush to the slider underside, and the **bond
> is the whole load path** — which the paragraphs below already say it is. The shaft is
> genuinely unbroken; report [9] verifies the true minimum section is ⌀6.0.

> **Rev (e) update (2026‑09‑10) — the collar is not bonded any more.** User brief:
> nothing glued to the piston. The two identical halves close around the shaft and are
> retained by **one transverse ⌀1.5 pin** driven along Y through half → shaft → half,
> fitted **last** through the access slot (the ⌀9 collar blocks both bores — the same
> topology that ruled out an integral flange). Load path is now shaft → **pin (double
> shear)** → collar top → slider → plate. The pin sees 34 N over 2 × π·0.75² = 3.5 mm²
> → **9.6 MPa** vs ~30 for ABS (bearing 3.8 MPa on the shaft hole, 7.8 MPa on the
> halves). The collar grew **⌀9 × 4.0** (was 2.0) so the pin has ~1.2 mm of wall above
> and below it; that meant **deepening the ledge 4 → 6 mm**, so the carrier / knob /
> tube‑stub bottom / servo keepout all shift ~2 mm aft (all derived — `PIN_BOT_Z` and
> `PIN_TOP_Z` are derived too now, `CRANK_LEN` 16.5 → 18.5, [P] cross‑checks it). The
> shaft carries one ⌀1.55 cross‑hole at Z −58 — the **only** reduction on the piston: net
> bending section ~56 % of gross, and the impact‑tension check ([5b]) is 33 MPa vs ~40
> in‑plane under the rigid‑drop DAF (PASS; a ⌀2 pin failed that — hence ⌀1.5, and the
> hole reamed line‑to‑line not `CL_CLAMP` so its slop stays out of [5b] free rise).
> Handling side‑load at the pin hole is **~2 N** ([5b]) — a careless‑knock limit, not an
> operating load; handle by the head, or fit the CF rod (§10.2).

**How it works (rev (e)).** A **CatchCollar** (⌀9, 4.0 mm, D‑flatted on −X, two identical
halves) closes on the shaft and is retained by a **⌀1.5 cross‑pin**. Its **top face** is
the upward‑facing surface the slider bears down on, and the slider is reacted by a
**full‑diameter plate** fused to the legs — replacing the 2 mm bridged `lip` that v1 was
reacting into. Load path: shaft → collar pin (double shear) → collar top → slider →
reaction plate → legs → screws → airframe.

| | v1 groove | §6.12 ⌀4 groove | **§6.14/d collar** |
|---|---|---|---|
| weakest section in the path | ⌀2.8 neck | ⌀4.0 neck | **⌀6.0 shaft (solid)** |
| side‑load to break it | 0.38 N | 1.12 N | **~4 N shaft‑up / ~8 N axial** (§6.15, [5b]) |
| tension at 34 N | 5.52 MPa × Kt 2.8 | 2.71 × Kt 2.0 | **1.20 MPa, no Kt** |
| free rise before the catch bites | 2.05 mm | 2.05 mm | **0.075 mm** (incl. 0.05 pin slack) |
| worst‑case impact | 50 MPa (fails) | ~25 MPa (marginal) | **11.3 MPa gross / 33 MPa net at the pin hole, vs ~40 in‑plane** |
| bearing | 4.33 mm² / 7.9 MPa | 4.33 / 7.9 | **11.69 mm² / 2.9 MPa** |

**Two identical halves.** The collar splits at y = 0 — the D‑flat is symmetric in y, so
both halves are the *same* part, not mirrored (report [9] asserts this). They clamp on
through the access slot at any point in the assembly, which is what makes a ⌀9 collar
fittable at all on a shaft that has to thread a ⌀6.8 bulkhead bore.

> **Superseded by rev (e) — the pin is the load path, not a bond.** The paragraph below
> is the rev (d) analysis of the *glued* interface. Rev (e) retains the collar with a
> transverse ⌀1.5 pin in double shear (9.6 MPa vs ~30, report [5]); there is no bond to
> cure and §8 no longer waits on one. Kept because it is where the "printable interface,
> not `2·π·r·h`" method is written down — the same reasoning still sizes the pin's
> bearing on the sub‑nozzle D‑flat side.

~~**The bond is the whole load path.** Report [5] computes it from the *printable*
interface, not `2·π·r·h`: the D‑flat wall goes sub‑nozzle for |y| < ~1.4 mm, so ~55° of
the bore prints open — **~32 mm² of shaft arc** (85 % of a full ring) **+ ~3 mm² on the
+X split face** (the −X split face is the open side of the C) = ~35 mm² → **0.98 MPa**
shear at 34 N, ~10× margin on solvent‑welded ABS. No groove, no backstop: cure the joint
before cocking (§8).~~

**A positive cocking stop, so free rise is a design number.** The ledge bore steps down
to ⌀6.8 at Z −61.0 (rev (e): was −59.0; the ledge deepened 4 → 6 mm and the collar grew
to 4 mm), **1.0 mm** below the collar's underside at Z −60.0 (21.6 mm² of contact,
1.6 MPa). Press to cock and the collar bottoms on that shelf; release and it rises 1.0 mm
at most. Previously the lost motion was whatever the operator overpressed — unbounded,
and it was landing on a thin neck.

The separate **[5b] free‑rise number** (0.075 mm, the collar‑top‑to‑slider gap plus the
pin‑hole slack) is a **tripwire for a wrong‑side catch**, not a mechanical limit — the
defect it guards against measured 2.05 mm, and the impact DAF is driven by
`COLLAR_COCK_GAP` (1.0 mm), which swamps it. A builder who reams the pin hole 0.05 mm
loose will read ~0.12 mm there and has broken nothing real; the ⌀1.55 line‑to‑line spec
is to keep the *number* honest and the catch crisp, not because 0.10 is a cliff.

**Why 1.0 mm and not 0.6.** The ledge's centre is *necessarily* void — the collar has to
pass through it at fire, and so does the crank‑pin sweep — so the slider seats on only
**59.5 of 184.5 mm²**, with its support centroid at Y +4.2 against a slider centre of
+1.35. Inward rail flanges do **not** fix this: the ledge already fills everywhere a
flange could go, and the void is central. So the slider droops when unloaded, pivoting
about that support until its far top corner meets the reaction plate `CL_SLIDE` above —
**0.62 mm at the notch end**. While arming, the collar is held down on the cocking stop,
so the gap has to exceed that droop or the slider catches on the collar's edge as it
slides in. At 0.6 mm it would have. At 1.0 mm there is 0.38 mm of margin, and the impact
cost is small because nothing in the load path is reduced any more: DAF 9.4 × 1.20 MPa =
**11.3 MPa against ~20**. Report [5] measures the seating, the droop and the stop.

**What bounded the collar.** ⌀9 is not arbitrary:

| Limit | Value | What sets it |
|---|---|---|
| max radius | 4.77 | nearest FIRED slider material (r 5.25 now, +0.75 margin) |
| D‑flat at x −3.1 | — | the ⌀3 crank pin's swept disc, r 4.5 about the knob axis, + `CL_ROT` |
| round collar impossible | r ≤ 3.8 | knob journal at x −8 — too little land over a 3.4 notch, hence the D |
| height 4.0 mm (rev (e)) | — | ⌀1.5 pin at mid‑height needs ~1.2 mm of collar wall above/below it; the extra 2 mm forced the ledge 4 → 6 mm deep |

The D‑flat costs only 1.2 mm² of bearing versus a full round.

### 6.15 The shaft: split in (d), **rejoined in (e)** — one `PistonShaft`, no joint
**Rev (d)** split `PistonShaft` into `PistonHead` + `Shaft` so the head could print flat
(disc down) while the shaft printed axially, joined by a solvent‑welded ⌀6 socket. That
removed the shaft‑up weakness (~4 N → ~8 N) at the cost of **a glue joint on the piston**.

**Rev (e) (2026‑09‑10) undoes the split.** User brief: nothing glued to the piston. The
two are **one printed part again** — `PistonShaft`, no socket, no joint — and the *whole
part* prints **AXIALLY** (laid on its side, perimeters along the shaft). The price the
split was avoiding is now paid deliberately: the ⌀38 disc prints **edge‑on** and wants
support on its lower ~third (and the sideways‑facing ⌀11.5 spring pocket); the
counterbore‑root fillet bridges. That support cost buys the shaft its in‑plane strength.

| | one‑piece shaft‑up (rev d's `[C]`) | split (d) | **one‑piece axial (e)** |
|---|---|---|---|
| side‑load to break at the counterbore root | ~4 N | ~8 N | **~8 N** |
| side‑load to break at the ⌀1.5 pin hole | n/a | n/a | **~2 N** (careless‑knock limit, §10.2) |
| ⌀38 disc | on the bed | on the bed | **edge‑on, supported** |
| shaft roundness | true | true | sag 0.2–0.4 mm — sand round |
| parts / joints on the piston | 1 / 0 | 2 / 1 glue joint | **1 / 0** |

- **Handling, not the catch load.** Two stations: the counterbore root (Z 42.5, R0.3
  fillet, `Kt` ~1.1) governs a knock near the *stub* → **~8 N** in‑plane; the ⌀1.5 pin
  cross‑hole (Z −58, `Kt` 2.0, net section ~56 % of gross, conservative) governs a knock
  near the *head* → **~2 N** in‑plane. Report **[5b]** prints both every run so neither
  goes stale.
- **Not "robust".** Handle the piston by the head, gently. For a genuinely unbreakable
  shaft, epoxy a **⌀6 pultruded carbon rod** down a ⌀6 hole bored into the finished head
  (~284 N) — the ABS part is the printable default, the CF rod the upgrade (§10.2).
- **`PistonShaftOnePiece` and the old `PistonHead` / `Shaft`** STEP/STL outputs are
  **deleted** — the one‑piece axial part *is* the article now, so the back‑to‑back
  comparison and the `[C]` report section are gone (its axial‑vs‑shaft‑up pair moved
  into `[5b]`).

### 6.5 Fully printed pins
Crank pin ⌀3, RBF pin ⌀2, **collar pin ⌀1.5**, all printed (`ejection_poc_test_pins.py`,
3 + 2 + 2 with spares). The knob's crank bore is opened +0.2 mm for a printed pin's
oversize; glue it in. The crank pin is a ~6 mm cantilever carrying ~7 N at the worst
angle → ~16 MPa bending in printed ABS: marginal, so it is **replaceable** — reprint if
it fails, or drill it out and drop in a steel ⌀3 pin. The **collar pin is HEADLESS** (a
head fouls the ⌀9.8 ledge pocket) — into ⌀1.55 holes reamed line‑to‑line on the pin
(~0.05 mm dia, **not** the looser `CL_CLAMP`: that slop is [5b] free rise), fitted last; a
⌀1.5 steel dowel / brad is better and drops straight in. Report **[P]** cross‑checks all
three pin lengths against this script's geometry.

### 6.6 Scotch‑yoke crank, not a cam
A crank pin in a straight cross‑slot gives: a big readable motion (6 mm), a
closed‑form kinematic (`dX = r(cos θ − 1)`), and — the reason it beats an over‑centre
linkage — **two true dead centres** at the travel extremes, self‑holding regardless of
friction. Cost: 180° of knob rotation (fine by hand; §10 for the servo).

### 6.7 Offset knob at X = −8
On the tube axis the knob would collide with the ⌀6 shaft. Offset −8 (clear of the
shaft by ~1 mm) with a ⌀20 grip keeps the outermost point at R ≈ 18 through the whole
sweep, inside the 19.5 mm moving‑parts limit with margin.

### 6.8 Catch = a groove shoulder on a fork, **not** a shear pin
The load path is a printed rim bearing on a printed shoulder in **compression**
(~2 MPa), reacted by a fixed ledge directly under it — no bending in the fork tines,
no pin in shear, nothing that can "cam out" axially. Withdrawal is orthogonal to the
load, so it needs only to beat friction.

### 6.9 RBF pin locks the knob
A ⌀2 pin through aligned holes in the knob and the fixed carrier, at ARMED. It blocks
the **cam/knob**, independent of the slider, the crank, and anything electronic —
so a servo brownout with the RBF fitted still cannot deploy.

### 6.10 Recovery eyelet dropped
Removed from the disc "for now" at the user's request. A first‑fire tether loops
around a cage leg instead. The flight bulkhead needs a real anchor (U‑bolt / printed
eyelet) back.

---

## 7. Verification — what `PhoenixABS40-43_ejection_poc_v1.py` checks

Every run rebuilds all parts, heals them (STEP round‑trip + `removeSplitter`), and
writes `ejection_poc_build_report_v1.txt`. **All sections PASS as of the last run
(2026‑09‑08 (d))** except two deliberate flags: **[T]** on the collar's 0.05 mm D‑flat
wall (accepted, unfixable in this layout — §6.14) and a "thin" warn on the disc rim
(§10.12); and **[5b]** marks the shaft WEAK in handling (§10.2).

| § | Checks |
|---|---|
| **0 Containment** | each static part ≤ R 19.9; each moving part ≤ R 19.5; slider + knob swept **at every 6° of the sweep**, not just the endpoints; SG90 keepout envelope inside R 19.5 |
| **2 Mass / envelope** | per‑part volume, mass (ρ 1.05), bounding radius and Z span |
| **3 Watertight** | mesh vs CAD volume error < 0.3 %, zero open edges, `isSolid`, no non‑manifolds |
| **4 Spring / guide / assembly** | free coils clear of disc + cage + piston; ⌀6 shaft < assumed spring ID; shaft ≥ 5 mm engaged in the disc bore at 0 and 40 mm stroke; **nothing on the shaft below Z −8 fouls the ⌀6.8 bore** (slide‑on); **leg pegs present, disc holes open, locating fit +0.1…+0.4 mm dia** |
| **F FDM fit gaps** | *(new, §6.11)* every moving/removable fit gap computed by **arithmetic on the `CL_*` constants** — slider top & sides, shaft‑in‑bore, knob‑in‑journal, RBF pin, locating peg, disc OD, crank pin, notch/neck — each against its target; reports the thinnest running gap. This is the check a boolean `.common()` **cannot** do (0 mm³ whether the gap is 0.00 or 0.50 mm). |
| **5 The catch** | ARMED — slider rim bearing area on the **CatchCollar top face** and its stress; FIRED — the whole **collar footprint** clear of the slider (this replaces the old “travel ≥ notch + shaft” proxy, which measured the wrong body) and the nearest‑material margin; the **reaction plate** solid above the slider; **collar‑pin double‑shear and bearing** (was collar bond shear) |
| **6 Crank** | crank pin stays inside the slot over 0–180°; ARMED & FIRED are dead centres; friction → knob torque → fingertip force < 15 N; SG90 headroom |
| **5b Load direction** | *(§6.13/6.14)* measures the **free +Z travel before the catch bites** — the check [5] structurally cannot do. The collar is **pinned, not fused**, so the sweep translates it *lagging the shaft by the pin‑hole slack* (0.05 mm dia): first slider contact is then the true free rise of the shaft, not of a rigid body. Reports which cage member takes the +Z load; the shaft **gross and net (at the ⌀1.5 pin hole)** tension under the bounded cocking drop × the rigid‑drop DAF (net 33 vs ~40 in‑plane, PASS); and the **shaft side‑load‑to‑break** at the **counterbore root** (~8 N axial) *and* the **⌀1.5 pin hole** (~2 N axial — the handling limit, §10.2), each both print ways. **0.075 mm, PASS.** |
| **T Thin features** | *(new, rev (d))* every wall/rib *inside one part* against `NOZZLE_W` — the class `[F]` can't see (it only checks gaps *between* parts). Catches: the removed collar rib; the collar's D‑flat wall (−0.05 mm — **accepted FAIL**, the flat is pinned by the crank sweep, §6.14); **the collar wall around the ⌀1.55 pin hole (+1.2 mm, PASS)**; the DummyNose relief bands; the disc rim at the peg holes (§10.12); and a boolean check that the `PistonShaft` hub core is 100 % solid (no leftover socket void). |
| **P Printed pins** | *(new)* `CRANK_LEN` / `RBF_LEN` / `CRANK_D` **/ `COLLAR_LEN` / `COLLAR_D`** in `ejection_poc_test_pins.py`, checked against `PIN_BOT_Z` / `PIN_TOP_Z` / `CRANK_PIN_R` / `COLLAR_PIN_LEN` / `COLLAR_PIN_R` here. The pin geometry lived in **two files** with nothing tying them together — which is how the crank pin ended up 3 mm too short to reach the slider (§10.17). The build script now *imports* that module for the plate, so there is one source of geometry as well as one check. |
| **11 Print plate** | *(new, §10.18)* packs the batchable parts + pins onto the bed, asserts **nothing overlaps** and it fits, reports the **tightest XY gap** against `PLATE_GAP` (overlap is prevented by the packer, so the number that actually matters on a bed is brim room), then **reads its own 3MF back** and verifies object count, build items and triangle indices — a bad index writes a file that opens as an empty plate, silently. |
| **8 RBF** | clip passes freely at ARMED; fouls the knob after 30°; **and the hole is drilled through solid carrier** *(new — §10.16; the old check was vacuous)* |
| **7 Collisions** | piston sweep vs cage and vs the fixed disc; ARMED slider vs shaft; FIRED knob vs cage; knob shaft vs piston shaft; **shaft, collar and CRANK PIN swept against the cage**; **`PistonShaft` swept 0–40 vs cage + disc** *(rev (e): the whole one‑piece part)* |
| **9 Features present** | window and access slot actually cut; slider notch and crank slot are open; **shaft ⌀6, OD unbroken + ONLY the ⌀1.5 collar‑pin hole** — spans the whole shaft, reports min OD *and* the pin‑station net section as its own row (the reduction is *visible*, not excluded — contrast §10.15 / the old groove‑excluding probe); collar halves coincide when mirrored (not just equal volume) |
| **10 Export** | STEP → `Models/`, STL → `Print Files/Ejection System/`, print‑oriented STL → `.../Ready to Print/`, batch plate → `.../Print Plate/`, `.FCStd` |

An independent check would ray‑cast the STLs (as `verify_aft_retention.py` does for the
sibling assembly); not yet written for this one.

---

## 8. Assembly sequence

0. **The piston is ONE part (rev (e)).** `PistonShaft` prints as a single piece — no
   weld, no cure step. Sand the shaft round and **ream the ⌀1.55 collar‑pin cross‑hole to
   line‑to‑line on the pin** (it prints egg‑shaped as an unsupported side hole and it is
   the pin's bearing surface; a sloppy hole shows up as extra free rise, [5b]). Handle it
   by the head.
1. Press the printed ⌀3 crank pin into the **Knob**. Slide the knob shaft up into the
   **Cage** carrier journal from below; grip ends up under the cage.
2. Drop the **Slider** into its channel on the cage ledge (it should sit with a little
   play, not press in), cross‑slot over the crank pin. Turn the knob to **FIRE** so the
   notch is retracted clear of the centre.
3. On the **PistonShaft**, from the stub (thin) end: slide on the **spring**, then the
   **BulkheadDisc** (bore first, spring‑seat facing the piston).
4. Feed head + spring + loose disc down into the cage from the top; stub through the
   ledge hole. **Push the disc onto the 4 leg pegs** (light hand pressure — the peg
   lead‑cones guide it; the screws in step 5 do the holding).
4b. **Fit the CatchCollar (⌀9 × 4.0).** Through the access slot, close the two identical
   halves around the shaft so the collar's top face is flush with the slider's underside,
   and align the collar's ⌀1.55 pin hole with the shaft's cross‑hole (turn the shaft a
   few degrees if needed). **Drive the ⌀1.5 collar pin** in along Y through half → shaft
   → half (light press; a ⌀1.5 steel dowel is better). Tug the collar to confirm the pin
   has bitten — the pin is the whole load path (§6.14), there is no bond or groove to
   fall back on.
5. Slide the cartridge into the **TubeStub**. 3× M3 radial screws into the disc edge,
   3× more into the cage ledge.
6. Fit the **DummyNose**.
7. **Cock:** press the piston down ~40 mm against the spring (a dowel through the nose
   helps) **until the collar bottoms on the ledge shelf** — that is a positive stop, you
   will feel it, and it is only 1.0 mm past the armed position. Turn the knob to **ARM**;
   the notch slides over the collar. Release — the collar rises 1.0 mm onto the slider. Drop the RBF pin through knob + carrier. First fires: tie a
   ~15 mm string from the hub cross‑hole to a cage leg.
8. **Fire:** pull the RBF pin, turn the knob to **FIRE**. Re‑cock from step 7.

---

## 9. How to prove it

1. `FreeCADCmd PhoenixABS40-43_ejection_poc_v1.py` → report all‑PASS.
2. `PhoenixABS40-43_ejection_poc_test_pins.py` → `TestPins_v1.stl`.
3. In FreeCAD: open the assembly `.FCStd`, run `ejection_poc_interactive.py` → a slider
   window; drag ARM ↔ FIRE and watch the crank swing the slider off the collar, then
   the piston jump 40 mm.
4. Print. Two jobs:
   * **`Ejection System/Print Plate/…_ejection_poc_plate_v1.{3mf,stl}`** — the batch:
     `Cage`, `BulkheadDisc`, `DummyNose`, `Knob`, `Slider`, **`CatchCollarHalf` × 2**
     and the pins (⌀3 crank, ⌀2 RBF, ⌀1.5 collar), arranged on a 220 × 220 bed (~182 ×
     78 mm used, 12 mm between parts so every one can take a brim — the ~64 mm `Cage`
     will want one). **Print the collar halves in the orientation the file gives them:**
     lying flat, **4.0 mm tall**, curved face up, **split face vertical** — that face
     mates the other half and the ⌀1.5 pin crosses it; standing one on its split face
     puts elephant's foot on the mating surface. Ream the pin hole with the pin.
   * **`Ready to Print/PhoenixABS40-43_{TubeStub,PistonShaft}_v1.stl`** — printed
     **alone**: `TubeStub` ~171 mm vertical; `PistonShaft` ~117 mm laid **axial** (the
     whole part on its side — the ⌀38 disc prints **edge‑on**, support its lower ~third
     and the sideways ⌀11.5 pocket). Kept off the plate. Sand the shaft round, ream the
     ⌀1.55 collar‑pin cross‑hole, or use a ⌀6 CF rod (§10.2).
   Dry‑fit per §8.
5. Cock and fire by hand, RBF fitted, tethered. Cock repeatedly — it must re‑arm
   cleanly every time.
6. **Measure `F_max` as a by‑product:** with a luggage/fish scale hooked to the piston,
   read the force to hold it at the 45 mm cocked height. Put that number into
   `F_MAX_ASSUMED` and re‑run the script.

---

## 10. Known limits & open items

| # | Item |
|---|---|
| 1 | **`F_max` unmeasured.** `F_MAX_ASSUMED = 34 N` (mid‑range). Pin shear, rim bearing and ledge are fine across the whole 7–53 N range; the only range‑sensitive number is knob effort, which stays trivial at the top. Measure it (§9.6) and re‑run. |
| 2 | **~105 mm ⌀6 shaft — still the weak part (finding 4).** rev (e): one `PistonShaft`, printed **axially**. Two handling stations ([5b], both print ways): the **counterbore root ~8 N** in‑plane (knock near the stub), and the **⌀1.5 collar‑pin cross‑hole ~2 N** in‑plane (knock near the head — net section ~56 % of gross, `Kt` 2.0, conservative). Neither is robust; handle the piston by the head. For a genuinely unbreakable shaft, epoxy a **⌀6 pultruded CF rod** down a ⌀6 hole bored into the *finished head*: ~284 N, no other change. A bought part, against brief item 4 — hence still an open item, not the default. |
| 3 | **180° knob sweep** is at the edge of a typical 9 g servo's range. Manual knob is fine. For the servo add a 2:1 crank arm (`CRANK_R` / linkage) or accept a servo that does a clean 180°. |
| 4 | **Catch bears on ABS.** 2.9 MPa on the collar‑top / notch‑rim contact — no strength concern, but watch wear over many cock/fire cycles. The flight bulkhead wants a brass or steel wear insert at the collar top and in the ledge. |
| 5 | **Soft stroke stop.** The spring's free length limits travel gently; there is no positive stop. Fine for bench work with a tether; the flight article needs a positive stop that survives repeated impact. |
| 6 | **Servo not integrated.** v1 = manual knob. v2 = the SG90 on the knob's D‑flat + a proper cradle; the keepout is already checked. |
| 7 | **Disc retention is temporary.** Locating pegs + 3 screws. A flight bulkhead is solvent‑welded or mechanically captured against the full spring + recovery‑shock load. |
| 8 | **No recovery anchor.** Eyelet dropped (§6.10) — put it back for flight. |
| 9 | **Not simulated, not flight‑cleared.** Bench POC only. |
| 10 | **No real "click".** The disc/peg fit is a locating clearance fit (§6.4), not a snap — it does not detent or announce that it seated. If a positive click is wanted before the screws go in, that's a barbed‑peg or cantilever‑finger redesign of the leg tops + disc holes. |
| 11 | **`CL_*` values are first‑principles, not measured on this printer.** `CL_SLIDE 0.5 / CL_ROT 0.4 / CL_BORE 0.4 / CL_PIN 0.25 / CL_PEG 0.2 dia / CL_TUBE 0.25` (§6.11). Print the dry‑fit set, feel the fits, adjust one block, re‑run. Report [F] names the thinnest gap so you know which face to sand if something still binds. |
| 12 | **Thin disc rim at the peg holes.** The ⌀3.2 peg holes sit on a ⌀35.2 circle in a ⌀39.5 disc → 0.55 mm of wall to the OD (was 0.8 mm at ⌀39.7 / ⌀2.9). Fine for a locating pocket (no load — screws carry it), but if a hole splits on assembly, pull `LEG_RC` in ~0.5 mm and re‑run (it also buys leg‑to‑bore clearance). This is why `CL_TUBE` was held to 0.25, not 0.4. |
| 18 | ✅ **Fixed 2026‑09‑06 (c): the plate bundle is generated, not hand‑made.** `Assembled Ready to PRINT/plate_v1.{3mf,stl}` was assembled by hand in a slicer on 2026‑09‑02 and then went stale through **three** revisions — by the end it held a `Cage` whose lip ran straight through the shaft, and §9.4 pointed people at it. It is now built by report **[11]** from the same oriented solids that feed `Ready to Print/`, so it cannot drift again. The old 3MF turned out to be a plain FreeCAD export with no slicer configuration in it, so nothing was lost by regenerating it. `BED_X`/`BED_Y` (220 × 220) are an **assumption** — set them to your printer. |
| 15 | ✅ **Fixed 2026‑09‑06 (c): the crank pin cut into the cage.** The ⌀3 pin sits at `CRANK_R` 3, so it sweeps a disc of **r 4.5** about the knob axis — outside the ⌀7.6 knob shaft, and outside the `JOURNAL_R` 4.2 holes in the ledge *and* the carrier. It was cutting up to 4.9 mm³ out of the ledge and 2.2 mm³ out of the carrier: the knob could not turn. Never caught, because **the pin has never been a modelled solid** — it lives in `ejection_poc_test_pins.py` and no check ever swept it. It is a solid now, swept against cage, collar and shaft every run. Both holes open to 4.9; the knob's lateral bearing moves to a ⌀5.5 **spigot** below the carrier, clear of the pin and on a longer moment arm. |
| 16 | ✅ **Fixed 2026‑09‑06 (c): the RBF pin locked the knob to NOTHING.** `RBF_KR` was +6.0, putting the hole at r 2.0 from the tube axis — **inside** the carrier's `BH_BORE_R + 1` = 4.4 central bore. The pin passed through the knob and then through thin air. That is precisely the brownout case brief requirement 3 exists for. `RBF_KR` is now −7.0 (r 15.0, solid carrier). The check that missed it was vacuous in the classic way — it measured the pin against the cage, which reads ~0 whether the hole is in solid material or in mid‑air; it now measures the **wall around** the hole (82 of 94 mm³). |
| 17 | ✅ **Fixed 2026‑09‑06 (c): the crank pin was 3 mm too short to reach the slider.** Seated in its old −71 bore a 12 mm pin topped out at Z −59, and the slider starts at −56 — it never engaged at all. Bore now starts at −69 (4 mm of glued engagement in the solid knob body) and `CRANK_LEN` is 16.5, giving 3.5 mm of engagement in the 4 mm slider. Checked by `CRANK PIN engages the slider slot`, and report **[P]** now ties the two files together so the next edit cannot drift silently. |
| 13 | ✅ **FIXED 2026‑09‑06 (c) by Option B (§6.14).** ~~Was:~~ ⚠ **The catch was INVERTED.** The spring drives the shaft **+Z** (disc fixed at Z −8…0, piston at Z 45, spring between them). The catch reacts **−Z**: `SHOULDER_Z = −52` is a *downward*‑facing annulus, the slider spans −56…−52, and the ledge is *below* it at −60…−56 — `build_cage` says so ("the slider hooks the shaft shoulder DOWN against this"), and report [5]'s bearing figure is computed on that face. A downward‑facing shoulder cannot restrain an upward‑moving shaft: contact is lost the instant it lifts. What actually catches it is the *upward*‑facing annulus at Z −58 hitting the slider's underside after **2 mm of free travel**, reacting through the printed `lip` — a 2 mm bridged overhang — instead of the ledge. That puts the full ~34 N in **tension through the groove neck** plus a 2 mm impact on every cock‑and‑release. §6.12 doubles the neck's tension area, which mitigates but does not fix it. **The fix is a cage change:** the slider's underside should bear on the groove's upward‑facing shoulder, reacted by a solid full‑diameter plate **above** the slider (the knob has to stay below, so the existing ledge keeps its job as shelf and journal host), and the groove height should drop to slider thickness + ~0.5 mm. §6.13 shows that reversing the reaction face is **necessary but not sufficient** — any groove‑and‑fork catch resisting +Z pulls the neck in tension by construction — and costs the two real options. Confirmed by test 2026‑09‑06: the shaft snapped during cocking. |
| 14 | ✅ **Fixed 2026‑09‑06 (b) — this is what actually broke the shaft.** The user reports it snapped **while being cocked**, which is exactly this: the lip is solid across the shaft’s path, so the shaft cannot reach the cocked position, and forcing it loads the neck’s upper root sideways. The slider‑retaining `lip` (x −17…−1, z −51.5…−49.5) intersected the ⌀6 shaft by 16.5 mm³ over a 2 mm band at the cocked position — a hard collision that made the assembly impossible. Pre‑existing in v1; the report's [7] never tested shaft‑vs‑cage, only *piston disc* sweep vs cage. A ⌀6.8 clearance bore is now cut through the lip (361 mm³ of lip still spans the channel, so it still retains the slider). **Add `shaft vs cage` and a full‑stroke shaft sweep to [7]** when back‑porting. |
| 19 | **No latch detent.** §3.5 / §6.6 say "a detent and the RBF pin cover vibration" — but **no detent is modelled or built**. Between ARM and FIRE the slider is held only by friction (~6.8 N to move it). At the endpoints the crank dead centre holds it, and at ARMED the RBF pin locks the knob. A printed cantilever bump on the knob rim into a carrier notch would add a real detent — deferred on the §6.4 precedent (don't size a snap before the mechanism's real friction has been felt on a print). Fit the RBF pin whenever the article is armed and unattended. |
| 20 | **Collar prints as a C, not a D.** The D‑flat sits 0.05 mm inside the ⌀6.1 bore edge, so the −X wall is sub‑nozzle and the collar bore opens on that side ([T] flags it, **accepted FAIL**). The flat can't move — it's pinned at exactly `CL_ROT` off the crank‑pin sweep — and the bore can't shrink. rev (e): **harmless** — the load goes through the ⌀1.5 pin now, not a bond arc, and that −X side is inside the notch anyway. If the knob layout is ever reworked (`KNOB_AX_X`, `CRANK_R`), this frees up. |
| 21 | ✅ **Removed 2026‑09‑10 (e): the `PistonHead`↔`Shaft` glue joint is gone.** ~~Was: a field solvent weld, a catch‑load and handling‑load failure if uncured.~~ The two are one printed `PistonShaft` again (§6.15). New field step in its place: **ream the ⌀1.55 collar‑pin cross‑hole line‑to‑line and press the ⌀1.5 pin** (§8.4b) — a bad pin fit is now the workmanship risk (its slop is [5b] free rise, 0.10 mm budget), but it's visible and re‑seatable through the access slot, and a ⌀1.5 steel dowel drops straight in. |
| 22 | ✅ **Fixed 2026‑09‑08 (d): stale script comments + hard‑coded paths.** The `.py` header, `build_cage` and a `COLLAR_Z0` comment still described the pre‑collar `[5b]`‑fails design; the export paths pointed at the flat `Print Files/` + `Assembled Ready to PRINT/`. All corrected; ejection outputs now write to `Print Files/Ejection System/…` and `.../Print Plate/`. The **aft‑retention** scripts still use the flat layout — that half of the `Print Files/README.md` warning stays live. |
| 23 | **⌀1.55 collar‑pin cross‑hole is an unsupported side hole.** Printed with `PistonShaft` axial, that hole faces sideways with an unsupported crown — it prints egg‑shaped, and it is the pin's bearing surface. **Ream/drill it line‑to‑line on the ⌀1.5 pin after printing** (a loose hole becomes [5b] free rise). Same for the ⌀1.55 hole in each `CatchCollarHalf`. A ⌀1.5 steel dowel takes up the slop. |
| 24 | **Ledge deepened 4 → 6 mm for the collar (rev (e)).** The carrier / knob / tube‑stub bottom / servo keepout all shifted ~2 mm aft (all derived — `[0]`/`[6]`/`[8]` re‑verified). `PIN_BOT_Z`/`PIN_TOP_Z` are derived now; `CRANK_LEN` went 16.5 → 18.5 (`[P]` catches drift). No containment impact. |

---

## 11. Files

```
Models/
  PhoenixABS40-43_ejection_poc_v1.py          parametric source of truth — edit here, re-run
  ejection_poc_test_pins.py                     -> Print Files/Ejection System/..._TestPins_v1.stl
  ejection_poc_interactive.py                   FreeCAD macro: ARM/FIRE slider on the open assembly
  ejection_poc_build_report_v1.txt              every check, every run -- see §7 for the deliberate flags
  EJECTION_POC_DESIGN.md                        this document
  PhoenixABS40-43_ejection_poc_v1.FCStd         assembly — 8 solids in position
  PhoenixABS40-43_{Cage,BulkheadDisc,PistonShaft,Slider,Knob,TubeStub,DummyNose,CatchCollar,CatchCollarHalf}_v1.step
Print Files/Ejection System/
  PhoenixABS40-43_{8 parts}_v1.stl             model frame (un-oriented)
  PhoenixABS40-43_TestPins_v1.stl              3 crank + 2 RBF + 2 collar pins
  Ready to Print/PhoenixABS40-43_{parts}_v1.stl   pre-oriented, dropped to Z = 0
      PistonShaft -> whole part laid AXIAL (layers along the shaft, §6.15); the d38 disc
                     prints EDGE-ON -- support its lower ~third + the sideways d11.5 pocket.
                     Sand the shaft round; ream the d1.55 collar-pin cross-hole line-to-line.
  Ready to Print/PhoenixABS40-43_CatchCollarHalf_v1.stl    PRINT THIS x2 -- identical halves (6.14).
      4.0 mm tall, split face vertical. Ream the d1.55 pin hole line-to-line on the pin.
  (no Ready-to-Print STL for the one-piece CatchCollar: a d9 ring cannot go onto a shaft
   that must thread the d6.8 bulkhead bore. Models/ keeps it as an assembly reference only.)
  Print Plate/PhoenixABS40-43_ejection_poc_plate_v1.{3mf,stl}   GENERATED by the script
      (report [11]): Cage, BulkheadDisc, DummyNose, Knob, Slider, CatchCollarHalf x2 + pins,
      packed and collision-checked. TubeStub and PistonShaft are NOT on it -- print those alone.
```

Print orientation is baked into the `Ready to Print/` and plate files. Notable:
`PistonShaft` — whole part laid axial, layers along the shaft, ⌀38 disc edge-on with
support (sand the shaft round + ream the pin hole, or use a CF rod, §10.2); `Cage` —
carrier end down, legs up, light support under the ledge; `Slider`/`Knob`/`BulkheadDisc`/
`CatchCollarHalf`/pins — flat, no support; `TubeStub` — vertical, brim. `TubeStub`
(~171 mm) and `PistonShaft` (~117 mm) print alone.

---

## 12. The parameters worth turning

All in the constants block of the `.py`.

| Constant | Effect |
|---|---|
| `CL_SLIDE / CL_ROT / CL_BORE / CL_PIN / CL_PEG / CL_TUBE / CL_CLAMP` (0.5 / 0.4 / 0.4 / 0.25 / 0.2 / 0.25 / 0.1) | **the FDM fit block** — every moving/removable interface derives from these; `CL_CLAMP` is the **collar bore** near‑contact clamshell fit (the collar‑pin hole is *tighter* than this — see `COLLAR_PIN_R`); tune to your printer, re‑run, read report [F] (§6.11) |
| `NOZZLE_W` (0.4) | extrusion width — report **[T]** fails any wall/rib thinner than this, warns under 2× |
| `SIGMA_ABS_INPLANE / SIGMA_ABS_INTERLAYER` (40 / 20) | ABS bending stress along vs across layers; [5b] reports the piston side‑load‑to‑break both ways at both stations (counterbore root, pin hole) |
| `STROKE` (40) | drives the **entire vertical stack** — one edit gives the full‑stroke flight geometry |
| `F_MAX_ASSUMED` (34), `MU` (0.2) | not geometry — they set the reported forces/margins; update after measuring |
| `SLIDER_TRAVEL` (6) → `CRANK_R` | how far the slider clears the collar; ≥ `NOTCH_R + SHAFT_R` |
| `SHAFT_R` (3), `SPRING_ID_MIN` (7.2) | shaft must stay below the real spring ID once measured; the counterbore‑root fillet peak also checks against this ([F]) |
| `CB_ROOT_FIL` (0.3) | R0.3 fillet where the ⌀6 shaft meets the counterbore floor — the max‑moment root when the part is handled by the head ([5b]); peak must clear `SPRING_ID_MIN` ([F]) |
| `COLLAR_PIN_R` (0.75), `COLLAR_PIN_HOLE_R` (`= COLLAR_PIN_R + 0.025` → ⌀1.55), `COLLAR_PIN_LEN` (8.6), `KT_PIN_HOLE` (2.0) | the ⌀1.5 collar retainer (§6.14/e). `d1.5` not `d2` — a `d2` cross‑hole pushes the net impact‑tension section past the in‑plane limit ([5b]). The hole is **+0.025 mm radial (line‑to‑line), not `CL_CLAMP`** — its diametral slop is [5b] free rise (0.10 mm budget), so [F] caps it at 0.07 mm. `COLLAR_LEN` in the pins file must match `COLLAR_PIN_LEN` ([P]) |
| `LEDGE_Z0` (`SLIDER_Z0 − 6`) | ledge depth — deepened 4 → 6 mm at rev (e) for `COLLAR_H` 4.0; carrier/knob/tube‑stub/servo all shift with it. Keep `LEDGE_STOP_Z` (`= COLLAR_Z0 − COLLAR_COCK_GAP`) inside the ledge with ~1 mm below it |
| `KNOB_AX_X` (−8), `KNOB_R` (10) | knob offset + size; keep `|KNOB_AX_X| + KNOB_R + scallop < 19.5` |
| `LEG_PEG_R` (1.5), `CL_PEG` (0.2 dia) | the locating‑peg fit; `DISC_PEG_HOLE_R` derives as `LEG_PEG_R + CL_PEG/2` |
| `NOTCH_R` (3.4) | clears the solid ⌀6 shaft (`SHAFT_R + CL_BORE`); the rim bears on the collar |
| `COLLAR_R` (4.5), `COLLAR_H` (4.0), `COLLAR_FLAT_X` (−3.1) | the catch (§6.14). Radius capped by FIRED slider clearance; the flat pinned at `CL_ROT` off the crank‑pin sweep (so the collar prints as a C — §10.20); the height set by the ⌀1.5 pin needing ~1.2 mm of wall above/below it |
| `COLLAR_COCK_GAP` (1.0) | the positive cocking stop — bounds the **downward overpress** while arming (the impact drop the [5b] DAF uses). It must stay above the unloaded slider droop (0.62 mm, reported by [5]) or the slider fouls the collar while arming. (Free rise *above* ARMED is a separate, much smaller number — geometric gap + pin slack, 0.075 mm, [5b].) |
| `R_MAX_MOVING` (19.5), `R_MAX_STATIC` (19.9) | the containment limits everything is checked against |

# D9aft v2: screw-on nose, tool-free e-bay, bulkhead eyelet

Delta note on top of `AFT_DEPLOY_D9_DESIGN.md` (v1). Everything not listed here is v1, unchanged:
the fin can, shear pins + pin card + coupons, cap, motor, pins/anchor sizing, deployment sequence.

| | |
|---|---|
| **Build** | `Models/PhoenixABS40-43_D9aft_v2.py`, ~6.5 min. It execs v1 read‑only, then builds the v2 parts. |
| **Report** | `Models/PhoenixABS40-43_D9aft_v2_report.txt` |
| **Nose** | `Nosecone/PhoenixABS40-43_Nosecone_v6.py`, report `Nosecone/nosecone_build_report_v6.txt` |
| **Flight** | `Models/aero_D9aft/verify_D9aft_v2_openrocket.txt` |
| **Model** | `PhoenixABS40-43_D9aft_v2.ork` |

## 1. What changed

**Nose v6: simpler, screws on.**
- Same Von Kármán profile (65 mm, 2.0 mm wall, solid tip) as v5.
- Removed: the detent pilots, anchor bosses and dowel, ballast ring, relief bands and the 42 mm
  friction shoulder.
- Added: a **9.5 mm male thread**. Pitch 3.0, **45° flanks** (no supports either half), 0.8 mm
  deep, about 3 turns.
- **14.6 g** (v5 part 39.6 g; with dowel and M5 screws the nose group was 47.9 g).
- Prints **tip up, thread on the bed**.
- It seats on its base annulus against the tube mouth: hand‑tight, then a strip of tape across the
  joint.

**E‑bay access, tool‑free.** Unscrew the nose and pull the loop on the `EbayCap`: the whole e‑bay
(sled + electronics) lifts out of the mouth.
- The female thread's crests are at **⌀39.30**, so the sled (R 19.39) passes with 0.26 mm radial.
- The e‑bay stands on a **seat ring** at station 61.7.
- A **2 mm closed‑cell foam ring** (⌀38.5 OD / ⌀36 ID, EVA craft foam) between the nose shoulder
  and the EbayCap holds it down and stops rattle and rotation. It compresses to 1 mm. The OD must stay
  under the ⌀39.3 thread crests; the ID clears the M2 heads.
- No screws go through the wall any more. The M5 nose screws and the 3 M3 e‑bay screws are gone.
- The sled still fastens to the EbayCap with its 2 × M2 screws, as before.
- **Clocking:** line up the witness notch on the EbayCap rim with the notch on the tube mouth
  (0°). That puts the piezo behind the sound port.

**Shock‑cord eyelet.** A **tie bar recessed into the aft face of the gas‑tight bulkhead**, on the
axis.
- The cord path: down a 5 × 5 window, through a 3.5 × 5 tunnel over the bar, out the other
  window.
- The pocket is blind, with a 3 mm roof, so the bulkhead is still gas‑tight.
- The bar is 6 × 3 mm over a 5 mm span: 17 MPa at the 250 N placeholder, printed flat as the first
  layers.
- The eyelet is only reachable **until the FwdTube is bonded**. So tie a **permanent Kevlar
  leader** to it first, long enough that its loop reaches the aft opening (about 250 mm). In the
  field the shock cord clips or ties to that loop.
- The fin‑can end is v1's lug inside the coupler, 10 mm from its open front.

**AftTube.** The wall harness lug is gone, so the chute bay is a **clean ⌀40 bore** from the
bulkhead to the aft end and the canopy has nothing to snag on. The launch lug and pin slots are v1.

**Layout.** The bulkhead moved forward to sit right behind the e‑bay.
- The chute bay is 198 mm (v1 150), which gives the same charge about 0.8× the v1 pressure.
- If the first separation is weak, drop to the 0.5 mm pin neck (card nick 1).
- Tubes: FwdTube 82.7 mm, AftTube 221.9 mm. Both fit the 250 mm bed.

| Station | v2 |
|---|---|
| −65 – 0 | nose v6 |
| 0 – 9.5 | thread (FwdTube female thread to 11, crest band to 12.5) |
| 9.5 – 10.5 | foam ring |
| 10.5 – 15.4 | EbayCap disc; the pull loop rises 14 mm forward into the hollow nose (to station −3.5) |
| 13.0 – 61.7 | sled v1 + electronics (its top sits in the EbayCap pocket), standing on the seat ring |
| 61.7 – 66.7 | seat ring → spigot. **Bonded joint at 66.7.** |
| 80.2 – 82.7 | bulkhead + recessed eyelet |
| 82.7 – 281.1 | chute bay, 198 mm |
| 248.6 – 340 | coupler, pins, fin can, motor, cap: v1 |

## 2. Checks

**RESULT: ALL PASS (0 FAIL)** (see the report). The six female-thread probes on the real FwdTube all land as designed.

The thread pair is checked by sampling, because booleans against faceted threads are not trusted:

| Check | Result |
|---|---|
| Seated | **0 clash** in 672 samples; fill 32 % tube / 48 % nose, so interlocked |
| Unscrew sweep at 180° and 360° | 0 clash |
| **Negative control**: the nose half a pitch out of phase | **213 clashes**, so the check can fail |

Every other fit uses thread‑free proxies. The e‑bay passes the crests; the stack has 1.0 mm for the
foam; nothing interferes; the gas column is clear; the chute‑bay wall has only the pin slots; the
canopy exit bore is empty; the separation sweep and launch‑rod line are clear; no supports are
needed.

**Timing note.** `isInside` on the faceted thread costs about 64 ms per point. The first attempt
sampled about 3,400 points at 8 positions (about 30 min) and was stopped. The grid is now 672
points at 4 positions.

## 3. Mass and flight

| | v1 | **v2** |
|---|---|---|
| Liftoff | 278.3 g | **244.4 g** |
| CG (from tip) | 230.0 | 236.2 |
| Margin, liftoff / burnout | 1.92 / 2.14 | **1.78 / 2.02** cal ✅ |
| Apogee | 172 m | **214 m** |
| D9‑5 ejection | +0.47 s, 4.6 m/s | **−0.08 s, 0.8 m/s (at apogee)** ✅ |
| OR optimum delay | 4.6 s | 5.1 s |
| D9‑3 / D9‑7 | 15 / 19 m/s | 21 / 15 m/s |
| Rail exit at 1.0 / 2.0 m guided | 11.0 / 13.8 | **12.0 / 15.4 m/s** ✅ at 2 m guided (≈ 2.3 m physical rod) |
| Descent, ⌀500 | 5.17 | **4.82 m/s** ✅ |

The 34 g saving (mostly the nose) fixes two of v1's open items: rail exit and descent. Stability
stays above the 1.5 gate: the nose lost 33 g at the tip, but the e‑bay moved 47 mm forward.

## 4. Assembly changes from v1 §7

1. **Tie the Kevlar leader to the bulkhead eyelet**, then bond the FwdTube spigot into the AftTube.
   Keep epoxy off the eyelet windows.
2. E‑bay: screw the sled to the EbayCap (2 × M2). Drop it in, notch to notch. Lay the foam ring on
   it. Screw on the nose and tape the joint.
3. Access in the field: untape, unscrew the nose, lift the e‑bay out by its loop.

## 5. Open items

- **Print the thread first as a test.** Print the top 20 mm of the FwdTube and the nose
  shoulder: the fit is 0.2 mm radial / 0.1 mm per flank, the same as the aft cap's (also untested
  at this size). If it binds, the fix is `RAD_CLEAR` / `FLANK_CLEAR` in `THREAD` (nose v6), which
  is shared by both halves.
- **The 1.05 mm skin behind the female thread root** is the thinnest wall on the airframe. The nose
  carries no harness load now, but don't use the nose as a handle when the rocket hangs.
- The foam ring holds the e‑bay's rotation by friction only. Check the notches still line up after
  a flight.
- v1 items still open: pin coupon batch test, spent‑D9 casing fit, charge strength unknown.

## 6. Nose shape re-check on the v2 vehicle

`aero_D9aft/NoseSweepD9.java` → `aero_D9aft/nose_sweep_D9aft_v2.csv`.
- 8 shapes × 6 lengths (40–130 mm) on the v2 airframe: D9‑5, ejection deploy, ⌀500 canopy,
  2.0 m guided.
- Nose mass is OpenRocket's 2 mm shell plus a 0.4 g offset, calibrated so VK 65 matches the
  v6 CAD at 14.6 g.

| | L = 40 | 50 | **65 (v6)** | 80 | 100 |
|---|---|---|---|---|---|
| Von Kármán Cd (M 0.3) | 0.4137 | 0.4154 | **0.4182** | 0.4211 | 0.4250 |
| apogee, m | 220.0 | 217.5 | **213.8** | 210.1 | 205.2 |
| margin, cal | 1.74 | 1.75 | **1.77** | 1.80 | 1.83 |
| ejection speed, m/s | 1.5 | 1.2 | **0.8** | 0.3 | 0.3 |

At 65 mm:

| Shape | Cd | Apogee |
|---|---|---|
| **Von Kármán** | **0.4182** | 213.8 m |
| Parabolic K=1 | 0.4188 | 213.3 m |
| LV‑Haack | 0.4199 | 212.3 m |
| Tangent ogive | 0.4223 | 212.5 m |
| Ellipsoid | 0.4287 | 209.7 m |
| Conical | 0.4924 | 209.1 m |

Parabolic K=0.75 scores 0.4165, but it is not tangent to the body at the base.

**What it says:**
- **Von Kármán is still the best base‑tangent shape** at every length.
- **OpenRocket gives every smooth shape the same pressure Cd (0.0356).** It models no nose
  pressure drag at these speeds, so the only differences it sees are wetted area and mass.
- "Shorter wins" (VK 40: +6 m, +2.9 %) is that same artefact. It is least trustworthy near
  L/D 1, and blunt noses do worse in crosswind.
- **The spread between sane choices is under 3 % of apogee.** Surface finish and a flush nose
  joint matter as much.
- **Keep v6 at 65 mm.** A 50 mm variant would gain about 3.7 m on paper for 0.02 cal. It is not
  worth a reprint unless you want to chase it.

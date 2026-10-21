# Phoenix ABS 40-43: D9aft complete print set (current = v10)

Everything printed for the Klima D9-5 aft-deploy rocket, pre-oriented and dropped to Z = 0.
**Slice these.** They are copies; the source files stay in their subsystem folders.

- Design: `Models/AFT_DEPLOY_D9_DESIGN.md` (v1), then `AFT_DEPLOY_D9_v2.md`, then
  `AFT_DEPLOY_D9_v3_v4.md`, then `AFT_DEPLOY_D9_v5.md`, then `AFT_DEPLOY_D9_v6.md`, then `AFT_DEPLOY_D9_v7.md`, then `AFT_DEPLOY_D9_v8.md`.
- **v7 changes only the sled.** D9aft v7 rebuilds the tubes and cap around sled v7, and they come out
  identical to v6 (checked against the STEPs), so the v6 files below are still the flight parts.
- **v8 changes both recovery anchors for a 5 mm retention line, tied direct (no Kevlar leaders):** the FwdTube
  bulkhead eyelet and the fin-can lug. **Reprint the FwdTube and the slotted fin can.** AftTube, EbayCap and sled
  are unchanged (0 mm³ against the v7 STEPs). The old v6 FwdTube and v4 fin can are in `_archive/`.
- **v9 replaces the shear pins with a printed SNAP LATCH.** The pins did not print. Two springy tongues in the
  AftTube wall, at 60° and 180°, click into windows in the fin-can coupler.
  - The geometry is the snap-latch coupon v2 (L24). Its first pull held 8.6 N per pair.
  - **Reprint the AftTube and the slotted fin can.** Everything else is v8.
  - Details: `Models/AFT_DEPLOY_D9_v9.md`, report `Models/PhoenixABS40-43_D9aft_v9_report.txt` (ALL PASS).
- **v10 = the whole rocket on sled v8, with the v9 snap latch, re-weighed.** Nothing new to print: the FwdTube and EbayCap
  come out identical to the files here. Details: `Models/AFT_DEPLOY_D9_v10.md`, report `…_D9aft_v10_report.txt` (ALL PASS).
  - **Not flight-proven:** the Klima D9 ejection charge is unpublished, and the latch has had one bench pull.
- **Sled v9 (2026-10-11): the v8 sled broke coming off the plate.** One Nano (ESP32) rail broke. The snap-arm slits had left 1.2 mm
  strips, about 17 mm tall, standing upright. v9 uses two solid 2 mm rails, and the Nano drops in from the outside between fixed end stops,
  then gets Kapton. No flex parts. Tubes, EbayCap and interfaces are unchanged (checked against the D9aft v10 STEPs); +0.65 g.
  **Reprint the sled only** (plate 4). The v8 sled and its plates are in `_archive/`. D9aft v10's CG rollup still uses sled v8.
- **Sled v10 (2026-10-14): prints with NO support and no spaghetti.** v9 spaghettified over the piezo, over the reed and under the
  I-beam. Every underside is now a 1:1.15 slope or a pointed arch, and a new overhang audit checks it (1230 → 389 mm² of downward face).
  New layout: ADXL glued flat on the battery tray back on an aft ledge; BMP388 on the east side (2 × M2.5 × 6 into a pier, use its
  AFT Qwiic plug); microSD reader on edge on the spine side (card toward the battery); battery zip tie goes sideways; reed board
  **slides in from the cap end** into printed guides; Nano backing plate with an access window, **Nano goes in last**.
  Tubes, EbayCap and interfaces unchanged. 17.4 g (+4.1 g vs v9, not yet in the CG rollup).
  Plates: **4** (EbayCap + sled), **6** (overnight), and new **7 = FwdTube + EbayCap + sled** (the whole forward section in one job).
  The v9 sled and its plates are in `_archive/`.
- **All parts ABS**, printed in an enclosure.

| Part | Version | Why |
|---|---|---|
| Nose | v6 | Screw-on |
| FwdTube | **v8** | v6 + **eyelet for the 5 mm line**: 6.5 × 6.5 windows and tunnel over a 7 × 3.5 bar. Everything else (thread, ports, ARM, groove) is v6 |
| EbayCap | v6 (= v7) | Printed springs + rotation key, pocket fitted to the sled top; **no foam ring** |
| Sled | **v10** | **No-support print** (v9 spaghettified). ADXL on the tray back, BMP east, microSD west, sideways battery tie, reed slide-in from the cap end, Nano last. Same length and interfaces as v7, so the tubes and cap are unchanged. (v9: solid Nano rails after a v8 rail broke) |
| AftTube | **v9** | Chute bay 150 mm, parachute only. Pin slots gone; **2 snap-latch tongues** at 60° / 180° near the aft end |
| Fin can | **v9** | v8 (v4 slotted + staple lug for the 5 mm line) with the pin slots filled and **2 latch windows** in the coupler |
| Pins | — | **Dropped in v9** (unprintable) |
| Cap | v1 | |

## Print order

### 1. Test first

These are cheap and gate the expensive parts.

~~Shear pin card + pin coupons (v1)~~: **obsolete since v9.** The pins do not print, and v9 uses the snap latch. Their STLs, the v6 AftTube and the v8 fin can are in `Print Files/_archive/`.

### 1b. OPTIONAL: snap-latch coupon (an alternative to the shear pins)

The v1 shear pins do not print: they came out as blobs. This coupon tests a printed **snap latch**
instead. A springy tongue in the tube wall carries a bump that clicks into a window in the
fin-can coupler. It is reusable and has no tiny features. No flight part changes until this passes.
The generator is `Models/PhoenixABS40-43_SnapLatchCoupon_v1.py`. The checks and force predictions are in
`Models/PhoenixABS40-43_SnapLatchCoupon_v1_report.txt` (ALL PASS).

| File | Qty | Orientation | Notes |
|---|---|---|---|
| `…_SnapLatchCoupon_v1_TubeRing_L20.stl` | 1 | as exported (forward end down, nicks up) | 1 nick: stiffest tongue, ≈19 N predicted |
| `…_SnapLatchCoupon_v1_TubeRing_L24.stl` | 1 | as exported | 2 nicks: ≈12 N |
| `…_SnapLatchCoupon_v1_TubeRing_L28.stl` | 1 | as exported | 3 nicks: ≈8.5 N |
| `…_SnapLatchCoupon_v1_TubeRing_L32.stl` | 1 | as exported | 4 nicks: softest tongue, ≈6.6 N |
| `…_SnapLatchCoupon_v1_CouplerRing.stl` | **3** | floor down | Fits any tube ring. The 2 grooves on the shoulder mark the windows. |

- ABS, no supports, **wall line width 0.40** so that the 1.2 mm tongue is 3 clean lines. Print in the same
  filament as the flight tubes.
- After printing, check that the tongue moves freely: the 1.0 mm gap at its aft edge is a short bridge.
  If it fused, run a knife along it and **note it**.
- **Check the tongue's set.** ABS can spring a thin, free strip in or out as it cools. The tongue tip should
  sit on the ring's circle, not proud of it or sunk by more than about 0.3 mm. Note what you find.
- **Assemble:** push a coupler ring into the tube ring from the nicked (aft) end until the shoulder seats.
  Line the shoulder grooves up with the bumps (or turn it until it clicks).
- **Pull test:** hang the tube ring by a string through its 2 holes. Hang a bottle from the
  coupler floor hole and add water until it lets go. Weigh it, and count the coupler ring too (~10 g).
  Test each tube ring with all 3 coupler rings, 3 pulls each.
- **Accept** a variant if every pull is **8–20 N per pair**. The floor is about 2× the 4.2 N hold need, and the
  ceiling is the 24 N budget minus about 3 N of slide friction. These numbers are predictions with about ±40 % uncertainty;
  **only the pull test proves the latch works.**
- **Durability:** on the chosen variant, do 10 click-in / pull-out cycles. Then re-measure, and look for white
  stress marks at the tongue root. The force should not drop by more than ~20 %.

**Snap-latch coupon v2 (current, print this one):** `…_SnapLatchCoupon_v2_TubeRing_L24.stl` + `…_SnapLatchCoupon_v2_CouplerRing.stl`.
- The v1 L24 held 873 g (8.6 N per pair) on its first pull, but its 4 mm aft band curled up near the tongue tip and rubbed the coupler.
- v2 makes that band 7 mm tall; nothing else changes. The bump and window moved 3 mm, so **v1 and v2 rings don't mix.**
- Dry the ABS first (about 4–6 h at about 80 °C). Same test and acceptance as above.

**Thread fit test:** in the slicer, cut the FwdTube 20 mm below its mouth and the nose 20 mm above
its shoulder, and print only those pieces. Check that it screws in by hand and seats flush.

### 2. Flight parts

| File | Qty | Orientation | Supports | Notes |
|---|---|---|---|---|
| `…_nose_VonKarmanScrew_v6.stl` | 1 | **tip up**, thread on the bed | none | 0.12–0.16 mm layers. Sand and prime. |
| `…_D9aft_v8_FwdTube.stl` | 1 | **bulkhead down** (the eyelet bar is the first layers) | none | 104.6 mm tall. Female thread + key groove at the top; ARM line engraved on the OD; sound port at 72.9. The eyelet pocket roof bridges 6.5 mm |
| `…_D9aft_v9_AftTube.stl` | 1 | forward end down | **none** (supports would weld the tongues) | 173.5 mm tall. Launch lug at 300°. **Dried ABS, wall line width 0.40** (1.2 mm tongues = 3 lines). After printing, check that both tongues move freely and their tips sit on the circle |
| `…_D9aft_v9_AftFinCanSlotted.stl` | 1 | boss down | **none** | 3 annular bridges (the two centring rings and the thrust ring, 9.6 mm): 4 perimeters, slow first bridge layer. The staple lug opening and the 2 latch windows have 45° roofs (no support) |
| `…_D9aft_v4_Fin.stl` | **3** | **flat** | none | Layers parallel to the faces (strong in bending) |
| `…_MotorRetainerCap_v1.stl` | 1 | base down | none | Slow the thread walls (~30 mm/s) |
| `…_D9aft_v6_EbayCap.stl` | 1 | disc down, loop + bumps up | none | The 3 spring beams are 19 mm arc bridges, 4 layers thick: use bridge settings |
| `…_ElectronicsSled_v18.stl` | 1 | floor (aft end) down, as exported | **none** (check [O] in the report) | **Sled v18 (2026-10-21)**, 70 mm tall, 14.7 g. v16 + the ESP32 slot's E rail continued down to the deck floor (v17), ESP32 heels removed (v18): push the board all the way down. Report `Avionics/avbay_sled_build_report_v18.txt` (0 FAIL, 1 WARN). Projects: `Bambu X1C/Phoenix_D9_plate12_EbayCap_v6_Sled_v18_0.16mm.3mf`, `…plate13_FwdTube_v8_EbayCap_v6_Sled_v18_0.16mm.3mf` (built by `make_bambu_projects_v6.py`, same settings as plates 10 / 11). Assembly as v16. File a flat on the M2 pan head at the d3 piezo hole. Let the plate cool fully before releasing. |
| `…_ElectronicsSled_v16.stl` | 1 | floor (aft end) down, as exported | **none** (check [O] in the report) | Sled v16 (2026-10-20), 70 mm tall, 14.6 g. Report `Avionics/avbay_sled_build_report_v16.txt` (0 FAIL, 1 WARN). Projects: `Bambu X1C/Phoenix_D9_plate10_EbayCap_v6_Sled_v16_0.16mm.3mf`, `…plate11_FwdTube_v8_EbayCap_v6_Sled_v16_0.16mm.3mf` (built by `make_bambu_projects_v5.py`). Assembly: C1 drops in axially first → ESP32 slides down its slot (battery plug out) into the aft cup → S7V8F5 → piezo → ADXL (glue) → BMP (both corners, glue) → Qwiic → battery + tie → plug in LAST → cap. File a flat on the M2 pan head at the d3 piezo hole. Let the plate cool fully before releasing. |
| `…_ElectronicsSled_v10.stl` | 1 | floor (aft end) down, as exported | **none** (designed for it; check [O] in the report) | Sled v10, 70 mm tall, 17.4 g. Report `Avionics/avbay_sled_build_report_v10.txt` (0 FAIL, 1 WARN); assembly order in its notes: piezo → small parts → microSD → ADXL (slide in from the BMP side, glue, press through the window) → reed board (drop in from the top, Kapton the fwd edge) → BMP → capsule → battery + tie → Qwiic leads → **Nano last** → cap. **Bend the piezo pins down and heat-shrink them before the board goes in.** File a flat on the M2 pan head at the d3 piezo hole (the head is 0.1 mm into the can). **Let the plate cool fully and flex it to release the part; don't pry.** |

## Bonding the fins

1. **Dry fit.** Each fin tab slides through its slot. It crosses the wall and both centring rings
   and stops 0.4 mm off the motor tube. There is 0.15 mm of gap per side for epoxy.
2. **Mask the coupler and its 2 latch windows.** No epoxy may land on the coupler: it is the separation
   joint.
3. **Epoxy the tab into the slot.** Use a 30-minute epoxy, and run it into the slot so it wets the
   wall, both rings and the motor tube. The slots set the 120° spacing. Check that each fin is
   square to the tube (a card jig helps) and let it cure fin-down.
4. **Fillets.** Once cured, run a **4 mm root fillet** on both sides of every fin, in epoxy
   thickened with microballoons or colloidal silica. This is the `.ork`'s fillet, and it also
   seals the slot line. About 2 g of epoxy in total (already in the mass rollup).

## Chute bay

The AftTube is the **parachute bay only**: 150 mm × ⌀40. Canopy, shock cord and Nomex go there and nothing else.
Pack them by hand before the first flight; there is less room than in v2–v5.

## Balance before flight (updated v10)

The v6 margin is 1.53 cal nominal, only 0.03 over the gate. Balance the finished rocket with a
loaded D9 and the recovery gear packed.
- **The balance point must be at most 226 mm from the nose tip.** If it is further aft, add ballast
  on the EbayCap top: about 0.6 mm of CG per gram; 3–4 g gives a cushion.
- **v10 (sled v8, snap latch, 5 mm line):** liftoff 262.6 g, predicted CG **228.0 mm**, so 2.0 mm past the gate.
  That is **≈ 4 g of ballast just to reach 226**, plus the cushion. It assumes an 18 g line (12 g/m × 1.5 m), and each gram
  of difference moves the CG by about 0.15 mm. **Weigh the line, then balance the built rocket.**
- See `Models/AFT_DEPLOY_D9_v6.md` and `AFT_DEPLOY_D9_v10.md`. Fly in wind under ~4 m/s until this is confirmed.

## Also needed (not printed)

- 2 × M2 × 10 pan head (sled to EbayCap)
- 2 × M2 × 6 pan head (piezo to sled) + heat shrink for its 3 pins
- 2 × M2.5 × 6 (BMP388 into the sled pier, from outside), 1 mini zip tie ≤ 2.5 mm wide (battery, sideways), Kapton, CA/epoxy for the ADXL
- **5 mm retention line**, ≥ 1.5 m, tied direct to both anchors. **Tie it to the FwdTube eyelet before bonding the tubes**
  (the eyelet is unreachable afterwards). The fin-can end sits beside the gas port: if the line is not Kevlar/aramid,
  sleeve that end in Nomex. **Weigh the line** (the mass rollup assumes 12 g/m).
- ⌀500 canopy, Nomex blanket or wadding
- Epoxy for three jobs only: the FwdTube spigot → AftTube joint, the fins and the fin fillets.
  **Never glue the fin-can coupler.**
- Tape: across the nose joint, one wrap on the motor casing. **Never tape over the AftTube latch tongues**: they must
  spring outward to release.
- Klima D9-5 motors
- *No foam ring*: the EbayCap springs replace it.

## Fin can on (v9 snap latch)

- Pack the chute bay. Push the fin can into the AftTube and turn it until it **clicks**. Only one clocking
  clicks: the fins end up clear of the launch lug, as with the old pins.
- **No click = wrong clocking or a stuck tongue: do not fly.**
- Pull gently on the fin can to check that it holds. It should hold about 0.9 kg.

## E-bay in and out

- **In:** the key on the cap rim goes into the groove at the mouth (180°), so the e-bay goes in only
  one way. Screw the nose on hand-tight; its shoulder presses the 3 spring bumps (≈ 4.6 N). Tape
  the joint.
- **Out:** untape, unscrew the nose, lift the e-bay out by its loop.
- **Arming:** hold a magnet on the engraved **ARM line** on the FwdTube (−8.7°, stations 20–34, with a cross tick at
  the capsule's centre). The reed capsule is 2.5 mm under it.

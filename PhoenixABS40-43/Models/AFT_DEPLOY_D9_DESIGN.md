# D9aft v1: aft deployment on the Klima D9-5 motor ejection charge

Companion to `DESIGN.md`. **This note supersedes DESIGN.md §7.1–7.9 (spring ejection) and the
D9 rows of §5.** The spring material is kept there as history and is not deleted.

| | |
|---|---|
| **Build script** | `Models/PhoenixABS40-43_D9aft_v1.py`, run in FreeCADCmd (~100 s) |
| **Machine report** | `Models/PhoenixABS40-43_D9aft_v1_report.txt`: **ALL PASS (0 FAIL)**, 2026‑09‑30 |
| **Flight check** | `Models/aero_D9aft/VerifyD9.java` → `verify_D9aft_v1_openrocket.txt` |
| **OpenRocket model** | `PhoenixABS40-43_D9aft_v1.ork`, a patched copy. The original `.ork` is untouched. |

Nothing here is flight-qualified yet. See §9 for the tests that gate first flight.

---

## 1. Architecture

**The only deployment event is the motor's own ejection charge.** Klima D9‑5, 5 s delay.

Sequence:

1. The charge fires forward out of the casing.
2. It passes through a **⌀14 port in the fin‑can thrust ring** into the chute bay.
3. It shears **two printed ABS pins** at the body/fin‑can joint.
4. It pushes the **fin can, with the spent motor**, off the aft end.
5. The canopy leaves the open aft end of the body. It rides a harness between the fin can and
   the airframe.

**The nose never separates.** The e‑bay sits directly behind it, sealed from the chute bay by a
solid bulkhead, so hot gas never passes the electronics. That was the reason for going aft.

The e‑bay now **fires nothing**: no servo, no nichrome, no RBF pin. It is a logging altimeter. It
stays in the vehicle because its 56 g, now at station 85, does stability work (§6).

Removed:
- the T5 spring ejector (base, piston, rod, spring, line, nichrome)
- the RBF pin and its holes
- the nose‑deploy harness anchor. The nose's anchor dowel is no longer fitted.

## 2. Station table

Stations are mm from the nose base. Add 65 for mm from the tip.

| Station | What |
|---|---|
| −65 – 0 | Nose v5 Von Kármán. **Unchanged part**, now retained. |
| 0 – 42 | Nose shoulder. 3 × **M5 × 8 button head** at station 8 (30/150/270°), self‑tapped into the nose's existing ⌀4.2 detent pilots (6.3 mm engaged). |
| 45 – 110 | **E‑bay**, from the front: sled mount (lugs grown to R 19.75 for the bare 40 bore, 3 × M3 CSK at station 50), then the sled v1 (unchanged). Static port ⌀1.5 at 79.3, sound port ⌀3 at 99.8. |
| 115 | **Bonded** joint between FwdTube and AftTube. Never opened. |
| 115 – 131 | FwdTube spigot (⌀39.7), closed by a **solid 2.5 mm bulkhead** at 128.5 – 131. No lead or vent holes. |
| 131 – 281 | **Chute bay**, 150 mm × ⌀40. The harness lug is on the wall at 132 – 150. Only two holes in the wall: the pin slots. |
| 152.5 – 187.5 | Launch lug on the OD at 300°, bore ⌀4.4 for the pad's ⌀4.0 rod. It stands off on a 4 mm web so the **rod line is at r 25.95**, 1.0 mm clear of the cap's grip ribs (r 22.75) at any cap clocking. |
| 248.6 – 288.6 | Fin‑can **coupler** inside the AftTube. 40 mm, **slip fit 0.40 mm diametral, NOT bonded.** This is the separation. |
| 276.6 | **2 × shear pins** at 60° and 180°, both in fin gaps. The uneven spacing means the fin can goes on only one way. |
| 281.1 – 284.1 | Fin‑can thrust ring, ⌀14 gas port on the axis. Harness lug at 300°, beside the port. |
| 288.6 – 340 | Fin can (v1 cfg C, fins printed in), Klima D9 18 × 70, cap v1 (unchanged) to station 357. |

Overall length is 422 mm from tip to cap. The body is kept at **340 mm**; the T5v2 v2 re‑run showed
each 10 mm cut costs about 0.11 cal.

## 3. Parts

| Part | Mass (solid ABS) | Print | Notes |
|---|---|---|---|
| `FwdTube` | 29.6 g | **Bulkhead down** on the bed, 131 mm tall | The bulkhead is the first layers, so it is flat and gas‑tight. The 1.65 mm outer step at station 115 is the bond face and prints as a short ring ledge (like the nose base). |
| `AftTube` | 37.1 g | **Forward end down**, 174 mm tall | The harness lug's underside is 45°. The launch lug + web have a 45° forward end (the bed side). No supports. |
| `AftFinCan` | 51.2 g | Boss down, as v1 | v1 cfg C read from its verified STEP, plus: ⌀14 port, 1 mm casing‑rim ledge then 45° to the port, coupler OD trimmed to 39.60 and extended to 40 mm, pin slots, harness lug. Supports: the fin trailing edges, as v1. The centring rings and the thrust‑ring annulus bridge, as v1. |
| `SledMount` | 7.2 g | Disc down | T5‑integration layout, lugs R 17.6 → **19.75**. |
| `ShearPin` | 0.01 g | Flat, 0.8 mm tall | Print from `ShearPinCard` (below). |
| `ShearPinCard` | — | Flat | 16 pins: necks 0.5 / 0.6 / 0.8 / 1.0 mm, 4 of each, marked with 1–4 nicks on the head. Use a brim. |
| `PinCouponOuter` / `Inner` | — | Either end / floor down | Test rig with the flight walls and slots (§4.3). Not flight parts. Checked assembled: the string line is clear above the inner ring, the pins are free in both slots, the hook hole is open. |
| `MotorRetainerCap` v1 | 9.0 g | unchanged | |

Every printed part is ABS. Files:
- STEP: `Models/PhoenixABS40-43_D9aft_v1_<part>.step`
- STL, raw: `Print Files/Aft Deploy D9/`
- STL, oriented: `Print Files/Aft Deploy D9/Ready to Print/`
- Assembly: `…_D9aft_v1.FCStd` / `_assembly.step`
- Section plot: `…_section.png`, flight and separated

**Threads and CAD checks.** AFT_RETENTION §8 still applies: OCCT booleans against the faceted
thread cannot be trusted. So:
- Every fit and interference check runs on a **thread‑free proxy** of the fin can.
- Every new feature is proven on the **real** part by 14 `isInside` probes.
- The real and proxy volume deltas agree to 0.1 mm³ (+4793.1 each).

## 4. Shear pins

### 4.1 Geometry

The pin is a flat 2D profile, 0.8 mm thick, so it prints as 4 layers at 0.20 mm.

| Feature | Value |
|---|---|
| Body | 2.4 wide × 3.0 long. It runs from the tube OD (r 21.5) to the coupler ID (r 18.5), flush on both sides. |
| Neck | Two 60° V‑notches cut the width to **0.6 mm** at r 19.9, the middle of the 0.2 mm radial slip gap, so it shears exactly at the interface. |
| Head | 4.0 × 0.6 mm outside the OD. It stops the pin falling into the bay. Tape over the heads. |
| Slots | 1.0 × 2.6 mm (pin + 0.2), in both the tube and the coupler. This is print‑tolerance sensitive: check the pins drop in. |

### 4.2 Sizing

At an **assumed** τ = 25 MPa, one pin holds 12 N and the pair **24 N**. That is 19 kPa, or
2.8 psi, over the ⌀40 bore.

| Load | Value |
|---|---|
| Bay overpressure at apogee (bay sealed at the pad, about 175 m climb) | 2.6 N |
| Fin can + cap + loaded motor hanging from a nose‑up body | 0.8 N |
| Drag separation, upper bound | 0.8 N |
| **Hold budget, all additive** | **4.2 N → pins hold 5.6×** |

Boost is compression and puts no load on the pins.

The pins must be the weak link, and they are:
- Bearing is 3.3 MPa in the tube wall and 3.8 MPa in the coupler.
- Slot tear‑out is 862 N in the tube (11.5 mm edge to its aft end) and 1788 N in the coupler (27.5 mm edge to its front: the pin loads the slot's forward face).

**Release.** The charge must beat 24 N plus the slide friction. Klima does not publish the charge
size. A rough estimate for a 150 mm × ⌀40 bay is ~50–70 N delivered, but that is an estimate,
not data. So the pins are deliberately set low. Hold only needs about 4 N.

### 4.3 Batch acceptance: the pin coupon

1. Print `PinCouponOuter` + `PinCouponInner` **in the same job and filament** as the flight tubes.
2. Slide the inner ring into the outer from below, so it hangs 4 mm proud, and fit two pins.
3. Hang the outer ring by a string through its two ⌀3 holes.
4. Hang a bottle from the inner ring's floor hook and add water until the pins shear. Weigh it.
5. Test three pairs from the batch.

**Accept at 8–15 N per pin, i.e. 16–30 N per pair.** If a batch is out of band, move to the next
neck on the card: nicks 1 → 4 = 0.5 / 0.6 / 0.8 / 1.0 mm.

Also measure the **dry slide friction** of the flight coupler in the AftTube with no pins
(target < 3 N). Sand or wax the coupler if it binds.

## 5. Harness, packing, motor

### 5.1 Anchors

Both anchors are wall‑fused lugs: ⌀3.5 hole, tangential axis, 6 mm thick. At the project's 250 N
snatch placeholder:

| Anchor | Bearing | Shear‑out |
|---|---|---|
| Fin can | 11.9 MPa | 795 N |
| AftTube | 11.9 MPa | 765 N |

### 5.2 Tether and packing

**Tether order:** fin‑can lug → **300 mm Kevlar leader** (it passes through the hot zone) →
shock cord ≥ 1.2 m → canopy ⌀500 → short cord → AftTube lug.

**Packing, forward to aft:** canopy against the bulkhead, cord, then a **Nomex blanket or
wadding over the fin‑can port**. The charge now blows straight into the bay. The Nomex was
optional under T5; here it is **mandatory**.

### 5.3 Motor

The thrust ring bears the casing's forward rim on a 1 mm ledge: 0.46 MPa at the 25 N peak.

**The cap is now a primary load path.** The charge kicks the casing aft onto the cap lip (about
8 N). If the motor leaves, the fin can does not separate. Hand‑tight plus a witness mark, as v1.

The ⌀18.4 bore leaves 0.4 mm around the casing. That is a blow‑by path from the port to the
nozzle: **put one wrap of tape on the casing.**

## 6. Flight numbers

OpenRocket 24.12 on the CAD rollup: liftoff 278.3 g, dry 251.2 g. No wind; canopy ⌀500 on
**ejection**.

| | Value | Gate |
|---|---|---|
| Stability margin | **1.92 cal liftoff / 2.14 burnout** (CP 312.6, CG 230.0 from tip) | ≥ 1.5 ✅ |
| Apogee | 172 m at 6.77 s | |
| vmax | 49.7 m/s | |
| **D9‑5 ejection** | t = 7.24 s, **0.47 s after apogee, 4.6 m/s**, 170.5 m | ±0.5 s, err long (DESIGN §5.2) ✅ |
| OR optimum delay | 4.57 s | |
| Descent | 5.17 m/s | ≤ 5 target: **marginal** ⚠️ |
| Rail exit vs **guided travel** | 1.0 m → 11.0 · 1.5 → 12.7 · 2.0 → 13.8 · 2.5 m → 14.8 m/s | ≥ 15 ❌ |
| Physical rod on the pad | guided + ~0.29 m (launch‑pad report [6]: the pad and the lug position eat 294 mm). So 1.3 m → 11.0, 2.8 m → 14.8 m/s. | |

Delay comparison, all at 1 m rod:

| Motor | Ejection | Speed | Verdict |
|---|---|---|---|
| **D9‑5** | +0.47 s after apogee | **4.6 m/s** | **correct** |
| D9‑3 | −0.62 s (before apogee) | 15.1 m/s | early |
| D9‑7 | +2.46 s | 19.4 m/s, falling | late |

The mass rollup is solid geometry × ρ, so it is an upper bound.

## 7. Assembly

1. **Dry‑fit everything first.**
   - The pins drop into the aligned slots.
   - The coupler slides freely.
   - The nose screws start in the pilots.
   - The sled + mount go in from the nose end.
2. **Before bonding, tie the shock cord (or a quick‑link loop) to the AftTube lug** through the
   AftTube's forward end, where the lug is only about 30 mm deep. After bonding it is 143 mm down
   a ⌀40 bore.
3. **Bond the FwdTube spigot into the AftTube.** Epoxy the spigot annulus and the station‑115
   face. Keep the AftTube lug at 0° and the launch lug at 300° where the script puts them.
   **Keep epoxy off the aft 45 mm of the AftTube bore**, where the coupler slides.
4. **E‑bay:**
   - Screw the sled to the mount (2 × M2).
   - Slide it in from the nose end.
   - Fit 3 × M3 × 8 CSK at station 50.
   - Nose on, 3 × M5 × 8 button heads.
   - Battery access is nose‑off.
5. **Fin can:**
   - Tie the Kevlar leader to the fin‑can lug.
   - Load the motor with one wrap of tape and screw on the cap.
   - Pack the canopy and Nomex.
   - Slide the coupler in, clocked so the slots align. It only fits one way.
   - Fit 2 pins from an accepted batch and tape over the heads.
6. **Never bond the coupler.**

## 8. `.ork` changes

`PhoenixABS40-43_D9aft_v1.ork`, written by `VerifyD9` with `SAVE_ORK`:

- Klima D9 at **5 s**, renamed "Klima D9‑5 aft deploy" and made the **default config**.
- Parachute **⌀500**, deploy on **ejection**.
- Nose: v5 Haack/Von Kármán, 65 mm, mass/CG override 47.9 g @ 67.9 mm from the tip (includes the
  M5 screws).
- Body: 340 mm, override 203.4 g @ 182.6 mm, subcomponents overridden.
- Fin trailing edge 0.6 mm forward of the body end (CAD).
- Motor overhang 14.1 mm (CAD).
- A stored "D9‑5 aft deploy, 1.5 m rod" simulation.

The body length and fin position now match the CAD. The `.ork`'s own component masses are not
used, because the override carries the CAD.

## 9. Qualification: replaces DESIGN §7.9

| # | Test | Pass |
|---|---|---|
| 1 | Pin coupon, 3 pairs per print batch (§4.3) | 8–15 N per pin |
| 2 | Coupler slide friction, no pins | < 3 N, no binding at 40 °C |
| 3 | Bulkhead leak: cap the chute bay (tape the aft end with the fin can off), blow gently | No air through to the e‑bay ports |
| 4 | Spent D9 casing fit: cap lip on the casing wall, forward rim on the 1 mm ledge | Visual + feeler |
| 5 | Pack test, 5 cycles: pack, fit pins, pull the fin can off by hand at the coupon load | Canopy fully out every time |
| 6 | Harness pull, 2 × 250 N on each lug (dead weight or luggage scale) | No cracking |
| 7 | **First flight is the charge test.** No ground test of a Klima charge is practical. Fly D9‑5 on the lowest accepted pin batch, 2.5 m+ rod, low wind. | Clean separation |

## 10. Open items

1. **Rail exit** is 14.8 m/s even with 2.5 m of guided travel (a 2.8 m rod). The vehicle is heavy
   for a D9 (278 g, thrust to weight about 3.4 average). Fly calm, use the longest rod the pad
   allows (the launch‑pad report already asks for ≥ 1.3 m, which gives 1.0 m guided and
   11 m/s), and accept 11–15 m/s. Alternatively take mass out. The
   electronics are 39 g now that they fire nothing.
2. **Descent 5.17 m/s** against ≤ 5. A ⌀550 canopy fixes it if the bay packs it (150 mm is
   generous).
3. **τ = 25 MPa is assumed.** The pin coupon is the real sizing.
4. **Klima charge strength is unknown.** Pins are set low (24 N) for that reason.
5. **Measure a spent D9** before printing the fin can (cap lip, forward rim).
6. **Heat on the pins and coupler.** ABS pins sit in the gas path's pressure zone but not in the
   jet. Inspect after each flight; replace pins every flight (they are consumables).
7. The launch lug is new CAD, bored ⌀4.4 as the pad report asks. The rod line moved from the
   pad's assumed r 25 to **r 25.95** to clear the cap ribs. The deflector keeps about 34 mm of
   plate around the nozzle (was 35). Re‑check the fin‑to‑deflector ring band in the pad report
   if you re‑run it. DESIGN §9 "two lugs or rail buttons" is still open.

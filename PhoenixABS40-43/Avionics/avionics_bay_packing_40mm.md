# Phoenix ABS 40‑43 — Electronics‑only packing study, ⌀40 mm ID

**Question asked:** take *only the electronic components* and fit them into the
shortest possible length inside a 40 mm ID cylinder (the Phoenix 40‑43 bore).

**Answer:** an irreducible **45 mm component zone**, giving a **≈ 54 mm bay**
(≈ 57 mm with the 750 mAh battery) once the aft closure, a forward bulkhead and a
3 mm harness‑loop allowance are added. The **Arduino Nano ESP32 (45 mm long) sets
the length**; the **SG90 servo (22.7 mm tall) sets the cross‑section**. Everything
else packs into the shadow of those two. *(With the servo aligned to the ejection
knob — §8, the buildable case — the zone is 48 mm and the bay is still ≈ 54 mm.)*

**Two numbers to act on:**

1. `DESIGN.md §7.8` reserves a **94 mm** e‑bay. A ~54 mm bay **frees ~40 mm of
   airframe** — real relief for the §4 stability margin.
2. This electronics set masses **≈ 48 g** (Option B battery), against the **30 g**
   `§7.11` budgets for "flight computer + battery + wiring" (21 g) + servo (9 g) —
   **~18 g over**, because the BoM is a *logging* flight computer (BMP388 +
   ADXL375 ±200 g + microSD + USB‑C charger + buzzer), not a bare deployment
   altimeter. The delta sits near the CG so it barely moves the margin, but it is
   real and needs a home in the §3 mass model.

This layout is worked from scratch for the ⌀40 mm bore: component set from the
BoM, servo envelope from `DESIGN.md §7.5.2`, and a cross‑section packed by hand
(servo near the tube axis, the two long parts in the widest part of the bore, the
rest in their axial shadow). Source of dimensions:
`../../Electronics/Avionics/avionics_bom.md` (+ its wiring companion), and part
datasheets where the BoM says only "small". Firm vs. estimated is called out per
row.

> **§8 supersedes this for the servo position.** §1–§7 place the servo freely
> (aft, near the axis) for the shortest pack. §8 re‑solves it with the servo
> output shaft **coaxial with the ejection‑system knob** (`X = −8`, off‑axis to
> clear the piston shaft) — which is the buildable configuration. The bay length
> is unchanged (**≈ 54 mm** either way); what changes is that the Nano and battery
> go flat against the wall. The FreeCAD model
> `PhoenixABS40-43_avbay_packing_v2.FCStd` is the knob‑aligned one;
> `…_v1.FCStd` is the free‑servo one.

---

## 1. What counts as an "electronic component" here

Scope confirmed with the user: **flight computer + battery + servo**, plus the
passive/support parts that are electrically part of that stack. Excluded:
the spring, piston, shaft, anchor bulkhead, cam/knob, latch pins, threaded
retainer, centring rings, Nomex, harness — all structural/mechanical — and the
two sealing O‑rings (BoM item 14, not electronic).

| # | Component | Dimensions (L × W × T) | Mass | Firm? | Notes |
|---|---|---|---|---|---|
| 1 | Arduino Nano ESP32 (ABX00083) | **45 × 18 × 5 mm** (bare); ~9 mm thick over socket headers | 5 g | Firm (Arduino spec) | Length driver. Trim/omit header sockets for the 5 mm figure. |
| 2 | Pololu S7V8F5 regulator | **17 × 11 × 3 mm** | 1.2 g | Firm (BoM = Pololu) | |
| 3a | LiPo 1S 750 mAh (Electrokit) | **48 × 30 × 5 mm** | 14.8 g | Firm (BoM) | *Option A.* 48 mm > 45 mm ⇒ this option grows the zone to 48 mm. |
| 3b | LiPo 1S 620 mAh (EEMB LP852040) | **40.5 × 20 × 8.5 mm** | 12.5 g | Firm‑ish (BoM; L×W×T ordering is BoM open‑item 2) | *Option B — used as the baseline here.* Fits inside the 45 mm zone. |
| 4 | USB‑C charger (BQ25302 module) | ~23 × 16 × 5 mm (+ USB‑C jack ~3 mm) | 2 g | Est. | BoM says "small". |
| 5 | BMP388 barometer breakout (Qwiic) | ~25 × 18 × 5 mm | 2.5 g | Est. | If the SKU is a 25.4 × 25.4 mm board it still fits the north lobe flat (see §4) — no length change. |
| 6 | ADXL375 ±200 g accel (Adafruit 5374) | **25.4 × 17.8 × 5 mm** | 2 g | Firm (Adafruit) | |
| 7 | microSD reader (Adafruit 4682) | **20.3 × 15.2 × 4 mm** | 1.5 g | Firm (Adafruit) | Card slot needs edge access. |
| 8 | microSD card, 16 GB | in the reader | 0.5 g | — | No standalone volume. |
| 9 | Active buzzer | ⌀12 × 9.5 mm | 1.5 g | Est. | A flatter transducer (~4 mm) eases the south‑lobe fit. |
| 10 | MOSFET 2N7000 (buzzer drive) | TO‑92, ~5 × 5 × 5 mm body | 0.3 g | Firm | Tuck against the Nano. |
| 11 | C1 bulk cap, 220 µF | ⌀8 × 12 mm radial electrolytic | 1.5 g | Est. (wiring doc, not BoM table) | Or an SMD/tantalum ~7 × 7 mm. |
| 12 | R1/R2/R3 (220 Ω, 2 × 10 kΩ) | axial, heat‑shrunk inline | <0.5 g | — | Negligible volume. |
| 13 | Reed switch + leads (arming) | 14 × ⌀2 mm glass capsule | 1 g | Firm (BoM) | Must lie against the tube wall; external magnet is a ground tool, not stowed. |
| 14 | SW1 power / SW2 wireless‑arm interlock | ~10 × 4 × 6 mm each | 1 g | Est. (wiring doc) | SW1 partly superseded by the reed switch per BoM 2026‑08‑19 note. |
| 15 | Interconnect (Qwiic + JST leads, headers, wire) | fills interstitial space | 5 g | BoM range 3–8 g | Routes in the freed centre past Z 23; service loop in the §4 harness gap. |
| 16 | **SG90 micro servo** | body **23 × 12.4 × 22.7 mm**; **32.2 mm** long over the mounting tabs | 9 g | Firm (SG90 spec; keepout per `DESIGN.md §7.5.2`) | Cross‑section driver. Trim the tabs to keep it at 23 mm axial. |

**Excluded and why**

- **u‑blox NEO‑6M / M8N GPS** (BoM item 11) — marked *optional (superseded)* in
  the BoM and outside the confirmed scope. It is 25 × 35 mm + a ceramic patch
  antenna and ~9 g; adding it back costs one full side lobe and ~0 mm of length
  (it fits within the 45 mm zone) but forces the Serial1/D2‑D3 harness.
- **Deploy MOSFET Q2 / burn‑wire driver** (build‑checklist §0, §5) — that channel
  exists for the CO2 / nichrome architecture. Phoenix 40‑43 deploys with the
  servo (`DESIGN.md §7.1`), so there is no coil and no Q2 in this bay.
- **O‑rings** (BoM item 14) — sealing hardware.

---

## 2. Orientation logic (why 45 mm is the floor)

| Item | Longest dim | Can it be anything but axial? | Axial cost |
|---|---|---|---|
| Nano ESP32 | 45 mm | No — 45 mm exceeds the 40 mm bore, so it cannot lie on any chord. A helical tilt projects to ~21 mm axial in the geometric limit (nearer ~30 mm once the 18 mm width and clearances are added), but it bisects the tube and wastes the wedges — rejected as unbuildable/fragile. | **45 mm** |
| Battery, Option B | 40.5 mm | No (40.5 ≈ bore). Axial. | 40.5 mm — *inside* the Nano's 45 mm |
| Battery, Option A | 48 mm | No. Axial. | 48 mm — *would extend the zone to 48 mm* |
| SG90 servo | 23 mm (tabs off) | Yes, but its 22.7 mm height + 12.4 mm width already span most of the cross‑section; putting the 23 mm dim axial is the shortest and leaves the side lobes usable. | 23 mm — inside 45 mm |
| BMP388 / ADXL375 | ~25 mm | Could chord, but simplest to run axial in a side lobe. | ≤25 mm — inside 45 mm |
| everything else | ≤23 mm | — | inside 45 mm |

The Nano and the Option‑B battery are the only parts longer than the servo, and
both are ≤45 mm, so **the whole electronics set fits within one 45 mm axial
window** — nothing needs to sit "behind" anything else. Length is set by the
Nano alone.

---

## 3. Cross‑section layout (looking aft, +Z toward the nose)

Coordinate frame: origin on the tube axis, +x "east", +y "north", R = 20 mm.
The servo is shifted **2 mm west** of the axis (x_c = −2) so the battery and the
Nano — which flank it — end up with **equal** outboard clearance. Battery and
Nano are centred on the x‑axis (y = 0), where the bore is tallest, to keep their
outer corners as far from the wall as possible.

```
                       ⌀40 mm ID  (R = 20)
                    ___________________________
                ,-''      NORTH lobe            ``-.
             ,-'   USB-C charger 23×16×5 flat       `-.
           ,'      BMP388 25×18×5 flat  (Z 0–25)       `.
          /   +------------+ - - - - - - - - - - - +      \
         /    | Nano ESP32 |        SERVO SG90     |       \
        |     | 5 (x) ×     |  12.4 (x) × 22.7 (y) | +-----+ |
        |     | 18 (y)      |  x_c = -2            | | BAT | |
        |     | Z 0–45      |  Z 0–23              | | Opt | |
        |     | x -14.8..   |  x -8.3 .. +4.3      | |  B  | |
        |     |   -9.8      | - - - - - - - - - - -| | 8.5 | |
        |     | (2N7000, C1 |                      | | ×20 | |
         \    |  tucked)    |                      | |Z 0- | |
          \   +------------+                       | |40.5 | |
           `. ADXL375 25×18×5 flat  (Z 0–25)       | +-----+/
             `-.  microSD reader · reed switch  _,-'      /
                ``-.__   SOUTH lobe        __,,-'
                      ```----------------'''
```

Everything lives inside a single **Z 0–45** window. The servo ends at Z 23; the
centre and the far ends of the north/south lobes past Z 23 are free for the
Qwiic/JST harness run and the servo‑lead service loop, so no separate wiring
length is needed *inside* the zone.

### Clearances — radial distance √(x²+y²) at each part's worst corner (Option B battery)

| Part | Worst corner (x, y) mm | Corner radius | Clearance to ⌀40 wall |
|---|---|---|---|
| Battery Opt B (x +5.7…+14.2, y ±10) | (14.2, 10) | 17.30 | **2.70 mm** |
| Nano ESP32 (x −14.8…−9.8, y ±9) | (−14.8, 9) | 17.30 | **2.70 mm** |
| Servo SG90 (x −8.3…+4.3, y ±11.35) | (−8.3, 11.35) | 14.06 | 5.94 mm |
| Servo ↔ battery faces | — | — | 1.5 mm design gap |
| Servo ↔ Nano faces | — | — | 1.5 mm design gap |
| North lobe free height above servo | at x = −2, y = +12.85 → wall at y ≈ +19.9 | — | ~7 mm (holds a 5 mm board flat) |
| South lobe free height below servo | symmetric | — | ~7 mm |

**2.70 mm is the whole radial budget** on the two big parts, and it must cover
the sled *and* wall out‑of‑round. Retention is therefore specified to add **no
material on the outboard face**:

- Battery and Nano each sit in a printed pocket that captures the **inboard face
  and both side faces** only; the outboard (wall‑facing) face is held by a Kapton
  strap or a 0.6 mm lid lip — nothing that eats the 2.7 mm.
- Sled webs between the servo pocket and the battery / Nano pockets are ≤ 1.2 mm,
  inside the 1.5 mm design gaps.
- A printed ⌀40 tube is ±0.3 mm out‑of‑round (`DESIGN.md §8.4`); 2.7 − 0.6 (lip)
  − 0.3 (roundness) = **1.8 mm true worst‑case clearance**. Acceptable, tight —
  and the reason a shorter flight‑computer board (which lets the battery move to
  the axis) is the recommended next step in §7.

---

## 4. Z‑station table (aft face of the component zone = 0, +Z toward nose)

| Z (mm) | Length | Contents |
|---|---|---|
| −3 – 0 | 3 | Aft closure disc / sled end plate |
| 0 – 23 | 23 | **Servo SG90** (centre, x_c = −2) · **Battery** Opt B (east) and **Nano ESP32** (west) both run through here · **USB‑C charger** + **BMP388** flat in the north lobe · **ADXL375** + **microSD reader** + **reed switch** + **SW1/SW2** in the south lobe |
| 23 – 40.5 | 17.5 | **Battery** continues (east) · **Nano** continues (west) · centre + lobe ends free for the Qwiic/JST harness and servo‑lead service loop · **buzzer**, **C1**, **2N7000** tucked in the freed centre |
| 40.5 – 45 | 4.5 | **Nano ESP32** only (its last 4.5 mm); harness collects here |
| 45 – 48 | 3 | Forward closure disc / servo bracket |
| 48 – 51 | 3 | Harness‑loop allowance — servo‑lead exit, USB‑C reach, arming‑magnet dwell |

- **Component zone: Z 0 – 45 = 45 mm** (Option B battery). Option A battery → **48 mm**.
- **Complete bay: −3 → 51 = ≈ 54 mm** (Option B) / **≈ 57 mm** (Option A).
- §8 (servo aligned to the knob): zone 48 mm, no forward closure — **bay still ≈ 54 mm**.

If the Electrokit BMP388 is a 25.4 × 25.4 mm board, it still fits the north lobe
flat (25.4 mm axial < 45, 25.4 mm wide < the ~32 mm lobe chord) — no length change.

---

## 5. Wall features (do not affect length; they constrain clocking)

| Feature | For | Placement |
|---|---|---|
| ⌀1.5 mm static port (or 3 × 120°) | BMP388 | **Radial, through the airframe wall**, north lobe at ~Z 12, clocked into a fin gap and away from the §7.6 ejection vents (`DESIGN.md §8.6`). *Not* the forward closure — that face vents into the recovery bay, not ambient. |
| Sound port, ~⌀3 mm | Buzzer | South wall at ~Z 30 |
| USB‑C slot, ~12 × 6 mm | Charger | North/east wall at ~Z 10 — the largest opening; put it in a fin gap |
| microSD slot, ~15 × 2 mm | SD reader | South wall at ~Z 10 |
| Reed switch | Arming | Against the wall, south lobe, Z 5–19; external magnet, no hole |
| SW2 (if a physical switch) | Wireless‑arm interlock | Small wall hole, or internal with a set‑before‑close jumper |

---

## 6. Mass

| Group | Mass |
|---|---|
| Flight computer + sensors + SD + charger + buzzer + passives + wiring | ~30 g |
| Battery (Option B 620 mAh / Option A 750 mAh) | 12.5 g / 14.8 g |
| SG90 servo | 9 g |
| **Electronics total** | **≈ 48 g (Opt B) / ≈ 51 g (Opt A)** |
| Printed sled + 2 closures (structure, *not* "electronics") | ~6–9 g |

`DESIGN.md §7.11` budgets 21 g for "flight computer + battery + wiring" and 9 g
for the servo = 30 g. This BoM's stack is **~18 g heavier** than that line
because it is a data‑logging computer — BMP388 + ADXL375 ±200 g + microSD +
USB‑C charger + buzzer — not a bare deployment altimeter. If the §7.11 budget is
firm, that delta needs to go somewhere in the §3 mass model, and it lands
near the CG so it barely moves the margin — but it is real.

---

## 7. How to go shorter than 45 mm (and the cost)

| Lever | New zone | Cost / risk |
|---|---|---|
| Use Option B battery (done here) instead of Option A | already 45 | Option A would be 48 mm; B saves 3 mm + 2.3 g, costs 130 mAh / ~1 h runtime |
| Source a shorter 1S cell (~30 × 30 × 8 mm, ~500 mAh) | 45 mm (Nano still governs) | no length change, but the battery can move onto the axis — recovers the tight 2.7 mm radial clearance |
| Replace the Nano ESP32 with a shorter ESP32 board (ESP32‑C3 Super Mini ~22 × 18 mm, or a bare ESP32‑S3 module) | **~40 mm**, then battery‑limited | firmware pin map changes; lose the Nano footprint / header convenience |
| Route the harness internally, drop the 3 mm loop allowance | −3 mm on the bay (54 → 51) | no service loop for field re‑pinning; harder rework |
| Diagonal/helical Nano mount | ~28–32 mm | wastes the tube wedges, hard to retain, fragile against print roundness — **not recommended** |
| Drop the servo | 45 mm (Nano) | out of scope; servo is confirmed in‑scope |

**Practical recommendation:** keep the Nano ESP32, use the Option B battery,
trim the servo tabs, accept the **45 mm component zone / ≈ 54 mm bay** (48 mm /
≈ 54 mm with the servo aligned to the knob, §8). The binding constraint is not
length any more — it is the **radial clearance** on the battery corner (2.7 mm
free‑servo, **1.0 mm** knob‑aligned). If that is judged too tight for a printed
tube, the fix is a shorter flight‑computer board so the battery moves toward the
axis, not a different packing of these parts. Going below ~40 mm of zone means
changing the flight computer, not repacking.

---

## 8. Knob‑aligned variant — model v2

§1–§7 let the servo go wherever packs shortest. In the real vehicle the servo
**drives the ejection knob**, and that knob is not on the tube axis — from
`Models/PhoenixABS40-43_ejection_poc_v1.FCStd`:

| Knob parameter | Value |
|---|---|
| Rotation axis | **X = −8 mm, Y = 0** (offset west, to clear the ⌀6 piston shaft — `EJECTION_POC_DESIGN.md §6.7`) |
| D‑flat / servo face (aft) | ejection‑POC `Z = −73` |
| Servo mount | SG90 on the D‑flat + a cradle (`EJECTION_POC_DESIGN.md §10.6`) |

For the SG90 output shaft to be **coaxial** with that knob, the servo's 22.7 mm
body has to lie on the `X = −8` line, at the **forward** face of the bay, case
pointing toward the tube centre (**X −14.0 … +8.8**). Consequences:

| | §1–§7 (free servo) | §8 (knob‑aligned) |
|---|---|---|
| Servo | aft, `x_c = −2`, Z 0–23 | **forward, on X = −8, Z 25.3–48**, abutting the knob |
| Nano ESP32 | side lobe, edge‑on | **flat on the north wall**, Z 0–45 |
| Battery | side lobe, edge‑on | **flat on the south wall**, Z 0–40.5 — worst corner **R 19.0** (≈1 mm to the ID) |
| BMP388 / ADXL375 / charger / small‑parts | around the servo | **all aft of the servo**, Z 0–24.8 |
| Component zone | 45 mm | **48 mm** (+3) |
| Forward closure | 3 mm bulkhead | **none** — servo case abuts the knob (−3) |
| Complete bay (aft closure 3 + zone + 3 mm service loop) | ≈ 54 mm | **≈ 54 mm** — length‑neutral |

The alignment is **not** a length trade — the +3 mm of zone is paid back by
dropping the forward bulkhead. The real cost is the flat Nano/battery: the
battery's worst corner goes from 2.7 mm off the wall to **1.0 mm**, and the servo
reaction torque (~85 N·mm) is now carried by cradle pockets around the SG90 tabs.

**Why the servo can't nest further forward:** it was checked against the real
piston shaft in both states — **6.95 mm clear when armed** (that gap *is* the
knob, Z 48–60.5), 46 mm when fired. Everything ahead of the D‑flat plane is
occupied in the armed state. Reclaiming the 3 mm of zone and un‑flattening the
Nano/battery needs a **2:1 crank or link** from an off‑axis servo to the knob
crank pin (`EJECTION_POC_DESIGN.md §10.3` already wants this for the 180° sweep)
— a mechanism change, not a re‑pack.

**Clocking caveat:** the model assumes the ejection module's `+X` matches the
packing frame's `+X`. If it clocks the other way, mirror the servo to `X = +8`.

Model: `PhoenixABS40-43_avbay_packing_v2.FCStd` (+ `Models/…_v2.step/.stl`,
`avbay_packing_build_report_v2.txt`). It carries the real knob and cage‑nose
solids from the ejection POC, shifted into this frame, as `Ref_Ejection*`.
Checks: 0 clashes, servo shaft on `(−8, 0)` to 0.00 mm, servo case abutting the
knob (0 gap / 0 overlap), 8 mm clear of the cage.

---

## 9. Serviceable cassette — inspect and recharge between flights  *(new)*

**Ask:** open the bay to inspect it and recharge/swap the battery for several
flights in one day.

**Model:** `PhoenixABS40-43_avbay_cassette_v1.py` (+ `.FCStd`,
`avbay_cassette_build_report_v1.txt`, and `Models/…_Svc*_v1.step/.stl`). §1–§8
have **no `.py`** — this is a *new* study layered on §8's published envelope
(`avbay_packing_build_report_v2.txt`), not a back‑port of the packing model. Edit
the script, re‑run with `freecadcmd`, never edit the STL/STEP/FCStd.

**Assembled view:** `Models/PhoenixABS40-43_avbay_cassette_ASSEMBLY_v1.stl` — all
four printed parts + the battery / Nano / servo / knob envelopes + the motor
bulkhead, in flight position (packing frame). `…_ASSEMBLY_section_v1.stl` is the
Y ≤ 0 half. `Models/cassette_assembly_v1/*.stl` holds the nine bodies separately
for re‑colouring or re‑assembly. The sled bounding block and the outer tube are
deliberately left out so the view isn't swallowed.

### 9.1 Half of it needs no disassembly at all

§5 already puts three things **through the airframe wall**:

| Feature | Use between flights |
|---|---|
| USB‑C slot (~12 × 6 mm, N/E wall ~Z 10) → BQ25302 | **Recharge the 620 mAh cell in place** — ~1–2 h at the BQ25302's programmed current. Covers two flights a couple of hours apart. |
| microSD slot (~15 × 2 mm, S wall ~Z 10) | Pull the log card |
| Reed switch + external magnet (S lobe, Z 5–19) | Arm / disarm |

So the quick turnaround touches nothing. Disassembly is only for a **faster
battery swap** or a real **inspection**.

### 9.2 Battery — swap, don't wait for a recharge

Put the EEMB cell on a **JST‑PH pigtail** to the S7V8F5 / charger, not soldered.
Swap a charged spare in seconds; bench‑charge the used one.

The v2 pack leaves the cell's worst corner **0.96 mm off the ID** (§3, §8), so
retention adds **nothing outboard** beyond a **0.6 mm lip** the cell rests
against. `SvcBatteryTray` (1.4 g) is a thin U‑channel in the **sled's radial
shadow** (R_max 19.39, clipped to the sled envelope): 0.8 mm side walls, fore/aft
end caps, the 0.6 mm outboard lip — and **open on the inboard face**, because that
is the way the cell comes out (lift toward the axis, then forward). The pull is a
fabric loop bonded to the cell plus the pigtail itself; there is no radial room
for a printed tab. Report `[B]` checks the pocket is inboard‑open, the cell clears
on a straight inboard lift, the lip still retains it against boost, and the
pigtail slot is clear.

### 9.3 Getting the whole stack out — the cassette

The body tube gets a **transverse bench‑service joint** just aft of the anchor
bulkhead (≈ `DESIGN.md §7.8` station 181 — the 18 mm coupler grows aft into the
e‑bay's slack, so the joint is length‑neutral; packing‑frame **Z 62**). It is
opened **only on the bench** — it is *never* a flight separation (flight recovery
separates at the **nose**, `DESIGN.md §7.5`).

- The **anchor bulkhead becomes the coupler** (`SvcAnchorCoupler`, 21 g, r19.4 ×
  18 mm): forward 6 mm bonded into the forward (chute‑bay) tube section, middle
  screwed to the aft section, aft face carries the ejection cage. Bored ⌀6.8 for
  the piston shaft, ⌀11.5 spring seat, inboard ⌀4 recovery eyelet
  (`DESIGN.md §7.7`; the ejection POC dropped it, §6.10).
- **"Removing the forward section" lifts the anchor bulkhead + cage + knob +
  servo + sled + electronics out as one assembly.** The servo‑to‑knob coupler is
  never broken → no blind re‑mate.
- **Retention:** 3 × radial **M3** through `SvcRetentionBand` (3.8 g) — a local
  wall thickening at the aft section's forward cut, **flush** with the skin (a
  proud ring mid‑body is draggy and snags), thickened **inward** to ID r19.6,
  wall **1.9 mm**. Edge distance screw‑to‑cut **7 mm = 2.3 d**. Holes
  **match‑drilled** at first build against the aft key so they cannot fight the
  clocking. **ALT if `[R]` fails once the load is known:** a 3‑lug **bayonet**
  ring — spreads the load round the full circumference, no radial holes — at
  ~4 mm of length.
- **Aft end** centred + clocked: `SvcAftClosure` (3.6 g) drops from r19.70 (the
  v2 "press disc") to **r19.0** — at r19.70 it would foul the band by 0.1 mm on
  the way out — plus a ⌀8 × 3 **spigot** into a motor‑bulkhead counterbore and
  **one** 3 × 2.5 mm **key** into a slot in it. The key is the **sole** rotational
  constraint, so the cassette re‑indexes the USB‑C / microSD slots and the static
  port to one clocking every time. Paint a witness line across the band's scribed
  notch and the forward‑tube seam.

Printed additions total **≈ 30 g** (+ 3 M3 + 1 pigtail). `SvcAnchorCoupler` is
21 g of that — it replaces the ~8 g bulkhead of `DESIGN.md §7.5` and sits in the
25 g ballpark of the ejection‑POC `AnchorBulkhead`; it is a **redesign target**,
`DESIGN.md §13` item 15, not a new budget line.

### 9.4 What this forces you to decide, and what stays open

**Decision — the anchor bulkhead must be *mechanically captured*, not
solvent‑welded.** `DESIGN.md §7.5` says "solvent‑welded to tube"; ejection POC
§10 item 7 says "solvent‑welded **or** mechanically captured". A removable
cassette needs the second. Those same 3 screws then also carry the **recovery
snatch load** (`DESIGN.md §7.7`: the bulkhead carries the full recovery shock,
and that is the larger load).

**Open — `[R]` cannot pass yet, and it's the wrong *event* as much as the wrong
number.** Report section `[R]` sizes the joint against `RECOVERY_SNATCH_N`, a
placeholder. It is wired to print `OPEN` on every line until:

1. the spring `F_max` is measured (`DESIGN.md §7.3` — the five‑minute
   measurement that still hasn't been made), and
2. a **packed separation is dropped** (`§7.9` test 4)

give a real number. The load that governs this joint is the **ejection snatch** —
`§7.5` gives ≈ 5.1 m/s separation, and the harness comes taut over the *shock
cord's* stretch, a short arrest that turns a ~200 g vehicle into a few hundred
newtons — **not** canopy opening shock (~10–30 N on 222 g). The script now uses a
250 N stand‑in for the ejection case; at 250 N the band bearing is ~13 MPa (vs
~40) and the M3 shank ~9 MPa (vs ~250). The band wall at 1.9 mm is flagged
**THIN** and can't grow inward because the **sled has to pass through the band**
on the way out (below). **If the measured snatch lands high, the 3‑lug bayonet
is the answer, not the fallback.**

**Tight — the band tightens an already‑tight fit.** `[E]` (a swept boolean **and**
an arithmetic radial‑profile scan — a static `.common()` can't tell a 0.00 mm gap
from a 0.50 mm one, ejection POC §6.11) reports the sled dragging through the
retention band at **0.20 mm** clearance. That is the same tightness the v2 pack
already has to the bore (§3, §8: "2.70 mm … 1.0 mm knob‑aligned" corner, sled
"0.61 to ID"). The real fix is the one §7 already names — a **shorter
flight‑computer board** so the battery moves onto the axis and the whole pack
loosens — not a fatter band.

**Not a problem — the static port.** Keep it a **plain ⌀1.5 mm drilled hole**, no
inward sealing boss: the BMP388 only needs to *share air* with the port, and a
plain hole keeps the bore clean for extraction. `[S]` confirms the wall stays at
r20.0 at the port station and the north lobe is open to it.

### 9.5 Turnaround procedure

*Quick (charge in place):* magnet off → USB‑C in, charge → card out/in if needed
→ magnet on. Nothing opens.

*Swap / inspect:* remove 3 band screws → lift the forward section (with the whole
cassette) straight forward off the aft section → unplug JST, lift the cell inboard
by its tab, drop in a charged spare, re‑plug → re‑seat: engage the aft key into
its slot (watch the witness line), slide home, 3 screws. The servo coupler was
never touched.

---

*Prepared 2026‑09‑02 against `Electronics/Avionics/avionics_bom.md` (rev
2026‑08‑08), `DESIGN.md` rev 5 and `Models/EJECTION_POC_DESIGN.md`. Worked from
scratch for the ⌀40 mm bore. Estimated dimensions (charger, BMP388 breakout,
buzzer, C1, SW1/SW2) should be replaced with measured parts before this drives a
printed sled. §9 added 2026‑09‑07 (serviceable cassette).*

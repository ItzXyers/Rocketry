# Phoenix ABS 40‑43 — Design Details & Guidelines

**Vehicle:** Phoenix40‑43 — a single‑stage, 3‑fin‑and‑nosecone (3FNC) sport model rocket,
fully FDM‑printed in ABS, flying standard 18 mm (Estes/Klima "mini") motors.
**Designer:** Tsaren · **Model:** `PhoenixABS40-43.ork` (OpenRocket 24.12) · **Doc date:** 2026‑09‑02 (vehicle rev 5 — unchanged; this revision records CAD only)

> **2026‑09‑30 — recovery re‑architected: D9aft v1.** The vehicle now flies the **Klima D9‑5** and deploys **aft on the
> motor's own ejection charge**: the charge shears two printed ABS pins and pushes the fin can + spent motor off the aft
> end; the nose stays on and the e‑bay (logging only) sits behind it, sealed from the chute bay. The spring ejector, servo,
> RBF pin and nose separation are gone. Design, checks, flight numbers and open items: `Models/AFT_DEPLOY_D9_DESIGN.md`.
> Wherever this document still describes spring ejection (§7.1–7.9, the D9 rows of §5) it is **superseded history**.
> **D9aft v2 (same day):** screw‑on nose v6 (simple Von Kármán, 14.6 g), tool‑free e‑bay (unscrew the nose, lift it out),
> recessed shock‑cord eyelet in the bulkhead — `Models/AFT_DEPLOY_D9_v2.md`. OpenRocket 1.78 cal, D9‑5 ejects at apogee.
> **D9aft v3 + v4 (2026‑10‑01):** printed spring beams + rotation key on the e‑bay (no foam ring); slotted fin can with
> 3 separate flat‑printed fins, epoxied (the one‑piece fin can would not print) — `Models/AFT_DEPLOY_D9_v3_v4.md`.
> Current print set: `Print Files/Ready to Print/D9/`. OpenRocket 1.76 cal.
> **D9aft v5 (2026‑10‑01):** electronics sled v4 (reed‑switch arming) in the e‑bay, EbayCap regenerated, engraved ARM mark on
> the FwdTube — `Models/AFT_DEPLOY_D9_v5.md`. OpenRocket 1.78 cal, D9‑5 ejects at apogee.

---

## 0. Status at a glance

| Item | State |
|---|---|
| Airframe geometry (⌀43 mm) | Defined in `.ork`, **rev 5** — fin semi‑span 30 → 55 mm; rev 4 thickened the wall to 1.5 mm and grew the nose shoulder to ⌀38 mm |
| **Static stability** | ✅ **D9aft v1 (2026‑09‑30): OpenRocket on the CAD mass rollup — 1.92 cal at liftoff, 2.14 at burnout on the Klima D9‑5** (`Models/AFT_DEPLOY_D9_DESIGN.md` §6). Other motors (A8/B4/C6) not re‑run on this vehicle — the D9‑5 is the flight motor. *(Was: rev‑5 fin fix, ≈ +1.8 cal computed, unconfirmed.)* |
| **Mass model** | ❌ **Stale — the `.ork` under‑reports the body tube by ≈ 49 g and the nose cone by ≈ 31 g. See §3.** |
| Simulations in file | All marked `outdated`; **none** use the current ⌀43 mm airframe. See §6. |
| Recovery | ✅ **D9aft v1 (2026‑09‑30): Klima D9‑5 motor ejection, aft deployment, printed shear pins — `Models/AFT_DEPLOY_D9_DESIGN.md`.** CAD ALL PASS; OpenRocket 1.92 cal liftoff, D9‑5 ejects 0.46 s after apogee at 4.6 m/s. Gating: pin‑coupon batch test, spent‑D9 casing fit. *(Was: servo‑released spring ejection — superseded.)* |
| Serviceable avionics bay | ⚠️ **Drafted — removable cassette past a bench joint, CAD verifies bar the deliberate `OPEN`. Needs the anchor bulkhead *screwed not bonded* (§7.5) and the recovery‑snatch joint proven (§7.3 + §7.9 t4). See §13 item 16.** |
| 3D‑print package | ⚠️ **D9aft v1 (2026‑09‑30): full flight set modeled — FwdTube, AftTube, AftFinCan (aft‑deploy), SledMount, shear pins + pin card + pin coupon; ALL PASS, STEP + STL in `Print Files/Aft Deploy D9/` (`Models/AFT_DEPLOY_D9_DESIGN.md` §3). None flight‑qualified (§9 of that note).** *History:* 11 bodies modeled, none flight‑qualified (§12.1). Ejection POC v1: 8 bodies, every geometric check passes, STEP + STL exported. Aft motor retention v1: 4 bodies in two configurations, **all verify clean** (§9) — STEP + STL exported. cfg B is a **sealed aft airframe section with through-the-wall fin slots** and cfg C the same section with the **fins printed in** — bulkhead only, **no vents**: this build flies a plugged motor, which §7.6's last paragraph says removes the venting problem entirely. Airframe, nose and fin‑can are still unmodeled. |
| **CAD ↔ `.ork` sync** | ⚠️ **D9aft v1: `PhoenixABS40-43_D9aft_v1.ork` carries the CAD** — body 340 mm with the CAD mass/CG override, nose v5, fin TE and motor overhang at their CAD positions, D9‑5 default, ⌀500 on ejection. It is a patched copy; `PhoenixABS40-43.ork` itself is still the old model (cap length, masses not propagated). *(Was: inverted, §13 item 14.)* |
| Livery | Defined (tan body, charcoal nose, white fins, orange stripes). See §10. |

> This document is the written design reference. `PhoenixABS40-43.ork` remains the
> single source of truth for geometry, mass and simulation — update the model first,
> then reconcile this file.

---

## 1. Vehicle identity & revision history

"Phoenix" is the airframe family; **"40‑43"** is read as **40 mm internal / 43 mm external
airframe diameter** (1.5 mm wall) — i.e. roughly an Estes **BT‑60‑class** tube. "ABS" denotes the
build material. This reading is an inference from the geometry, not a stated fact.

Note the naming convention holds the **internal** diameter constant: rev 4 grew the OD from 42 to
43 mm purely by thickening the wall from 1.0 to 1.5 mm (§8.3), leaving the 40 mm bore — and
therefore every internal component — unchanged.

The simulation set embedded in the `.ork` preserves an unlabelled design lineage. The
OpenRocket "reference length" recorded in each run reveals which airframe diameter it was flown on:

| Rev | Airframe ⌀ (OD) | Equivalent tube | Simulations on this rev | Status |
|-----|----------------|-----------------|--------------------------|--------|
| 1 | ~25 mm | BT‑50 class | Simulation 1, 2, 3, 5 | superseded |
| 2 | ~35 mm | BT‑55 class | Simulation 4, "Simulation 7" (D9) | superseded |
| 3 | 42 mm | BT‑60 class | Simulation 6, "Simulation 7 – Klima" | superseded |
| 4 | 43 mm | BT‑60 class | **none** | superseded |
| 5 | **43 mm (current)** | BT‑60 class | **none** | **current** |

Rev 4 (in the `.ork`, never simulated) closes part of §13 item 10: body wall 1.0 → **1.5 mm**
(ID held at 40 mm), nose shoulder ⌀23 → **⌀38 mm**, nose wall 2.0 → **10.0 mm**. The last of these
adds ≈ 31 g at the very front of the vehicle — see §3 and §4.

Rev 5 changes **one parameter**: fin semi‑span **30 → 55 mm** (`<height>` 0.030 → 0.055). It is the
§4.3 item 1 stability fix. Root chord, tip chord, sweep, thickness, cross‑section, fillet and
axial position are untouched — see **§4.5**, which also corrects §4.3's advice about the root
chord. Note this rev finally breaks the §1 pattern of carrying the fin planform across airframe
revisions unchanged.

**Guideline:** the fin planform was carried over unchanged through all three revs. That is the
root cause of the stability problem in §4. Whenever the airframe diameter or length changes,
the fins **must** be re‑sized and the whole motor matrix re‑simulated in the same pass.

---

## 2. Configuration overview & master geometry

Single stage ("Sustainer"), nose cone + one body tube, 3 fins, single launch lug, 18 mm motor
mount with a forward thrust ring (engine block) and two centring rings.

```
      ┌ nose cone (ellipsoid, charcoal)
      │   ┌ body tube (tan, 340 mm, ⌀43 OD / 40 ID)
      │   │    ├ canopy + piston + spring (forward)  ◄── see §7
      │   │    ├ payload / ballast mass (mid‑body)   ◄── see §3 / §4; becomes the e‑bay, §7.8
      │   │    ├ launch lug (mid‑body)
      │   │    ├ 18 mm motor mount + engine block + 2 centring rings (aft)
      │   │    └ 3× trapezoidal fins (aft, 4 mm overhang)
```

### 2.1 Master dimensions (from the `.ork`, current rev)

| Parameter | Value | Notes |
|---|---|---|
| Overall length (nose + body) | **≈ 380 mm** | 40 + 340; nose shoulder inserts, adds no length |
| Max envelope length | ≈ 384 mm | fin trailing edge overhangs aft end by 4 mm |
| Airframe OD | **43 mm** | body tube radius 21.5 mm |
| Airframe ID | **40 mm** | wall thickness 1.5 mm (see §3 mass caveat) |
| Fineness ratio (L/D) | ≈ 8.8 | blunt for a sport model; acceptable at these speeds |
| Dry mass, modeled (with payload) | ≈ 107 g | from Simulation 6 — **⊙ obsolete**: rev 3 geometry, rev 3 nose |
| Dry mass, realistic — structure only | **≈ 130–136 g** | tube prints solid + 39 g nose + 14 g rev‑5 fins; see §3 |
| Dry mass, realistic — flight‑ready | **≈ 207–213 g** | + 77 g recovery & avionics (§7.11) |
| Liftoff mass on a C6 | **≈ 231–237 g realistic** | +24 g motor |

### 2.2 Component geometry

**Nose cone**
| Shape | Length | Wall | Base ⌀ | Shoulder ⌀ | Shoulder length | Shoulder wall | Capped |
|---|---|---|---|---|---|---|---|
| Ellipsoid | 40 mm | **10.0 mm** | 43 mm (auto) | **38 mm** | 20 mm | 2.0 mm | yes |

Material: ABS, 100 % infill (ρ = 1050 kg/m³). Finish: semi‑gloss. Blunt ellipsoid — high pressure
drag, but the vehicle never exceeds Mach 0.3 so this is not a performance concern.

> ⚠️ **The 10 mm wall makes this part near‑solid — ≈ 39 g, not the ≈ 8 g this document previously
> recorded (§3).** At 40 mm long on a 21.5 mm base radius, a 10 mm wall leaves only a small cavity.
> If that was deliberate it is an effective substitute for the nose ballast of §4.3 item 3, and a
> good one — it is the furthest‑forward mass on the vehicle. **Confirm it was intended**, then
> read the real figure off OpenRocket's component mass display rather than this table.
>
> The consequence for recovery is that the nose is a 39 g object on the end of a shock cord
> (§7.7), and the spring has to accelerate it (§7.5).

**Body tube**
| Length | OD | ID | Wall | Material (modeled) |
|---|---|---|---|---|
| 340 mm | 43 mm | 40 mm | 1.5 mm | "ABS, 30 % infill" (ρ = 310 kg/m³) — **wrong, see §3** |

**Fin set (trapezoidal, ×3)**
| Root chord | Tip chord | Semi‑span (root→tip) | LE sweep | Thickness | Section | Fillet | Cant | Position |
|---|---|---|---|---|---|---|---|---|
| 50.8 mm | 25.0 mm | **55 mm** *(rev 5)* | 25.4 mm | 2.0 mm | rounded | 4 mm radius | 0° | aft end, −4 mm (overhangs) |

Material: ABS, 100 % infill. Per‑fin planform area ≈ **2084 mm²**; total ≈ 6253 mm². Tip‑to‑tip span
≈ **153 mm**. Fin panel aspect ratio ≈ **1.45**. Fin set mass ≈ **14.2 g** (was 8.3 g).

Rev 5 resized this planform to fix the §4 stability finding — **§4.5** carries the sizing analysis,
the flutter and clearance checks, and a correction to §4.3's guidance on the root chord.

**Launch lug**
| Length | OD | Bore (ID) | Wall | Position | Radial clocking |
|---|---|---|---|---|---|
| 35 mm | 7 mm | ~5 mm | 1 mm | body mid‑length | 19° (sits in a fin gap) |

Bore fits a **3/16 in (4.8 mm)** rod with clearance; it will **not** pass a 1/4 in rod. See §9 for
rail/lug recommendations.

**Motor mount (inner tube)**
| Length | OD | ID | Wall | Motor overhang | Material |
|---|---|---|---|---|---|
| 75 mm | 19 mm | 18 mm | 0.5 mm | 3 mm | ABS 100 % infill |

- **Engine block (thrust ring):** 5 mm long, cardboard, positioned 2 mm from the mount's forward
  end; necks the bore so the motor butts against it.
- **Centring rings ×2:** 2 mm cardboard, auto‑sized (40 mm OD / 19 mm ID). One flush with the aft
  end of the body tube, one 67 mm forward of it — i.e. near each end of the motor mount.
- Motor retention as modeled: friction fit + engine block only. **Add a positive retainer** (§9).

---

## 3. Mass budget

The `.ork` models the body tube as **"ABS 30 % infill"** at ρ = 310 kg/m³ applied to a 1.5 mm wall.
A 1.5 mm wall on an FDM printer is ~3–4 perimeters wide — there is no room for a 30 % infill
lattice, so in reality the wall prints **effectively solid** (ρ ≈ 1050 kg/m³).

| Body tube | Volume | Modeled mass | Realistic mass |
|---|---|---|---|
| 340 mm × (⌀43 / ⌀40) annulus | ≈ 66.5 cm³ | **≈ 21 g** (ρ 310) | **≈ 70 g** (ρ 1050) |

**Consequence:** **≈ 49 g** of unmodeled mass — up from ~30 g at the old 1.0 mm wall, because rev 4
thickened the wall without correcting the density. It is distributed along the tube with its
centroid at/behind the current CG. It makes the vehicle heavier (lower apogee, lower rail‑exit
speed) **and pushes the CG aft — worsening an already‑marginal stability margin.**

### 3.1 The nose cone is also mis‑recorded  *(new in rev 4)*

Rev 4 set the nose wall to **10.0 mm**. Computed from the `.ork` geometry for this document:

| Nose element | Volume | Mass (ρ 1050) |
|---|---|---|
| Cone shell (ellipsoid L 40, R 21.5, 10 mm wall) | 30 416 mm³ | 31.9 g |
| Shoulder (⌀38 × 20 mm, 2 mm wall) | 4 524 mm³ | 4.8 g |
| Shoulder cap | 2 268 mm³ | 2.4 g |
| **Nose cone total** | | **≈ 39 g** |

Against the ≈ 8 g this document previously carried, that is **+31 g at the extreme front of the
vehicle**. Unlike the body‑tube error this one is *helpful* — it is exactly where §4.3 item 3 asked
for ballast — but it must be in the model before any CG or stability number means anything.

### 3.2 Approximate mass breakdown (current rev)

| Item | Modeled | Realistic estimate | Basis |
|---|---|---|---|
| Nose cone (100 % infill, 10 mm wall) | ~8 g † | **≈ 39 g** | §3.1 |
| Body tube | ~21 g | **≈ 70 g** | §3 above |
| Fin set + fillets (100 % infill) | **≈ 14 g** | **≈ 14–16 g** | §4.5 — rev 5, span 55 mm |
| Motor mount + engine block + 2 rings | ~5 g | 6–9 g | geometry |
| Launch lug | ~0.7 g | 1–2 g | geometry |
| **Structure subtotal** | | **≈ 130–136 g** | |
| Recovery hardware (spring, piston, shaft, bulkhead) | — | **≈ 31 g** | §7.11 |
| Avionics (FC, battery, servo, wiring) | — | **≈ 30 g** | §7.11 |
| Canopy ⌀500 + harness + leader | ~6 g | **≈ 16 g** | §7.7 |
| Payload / ballast mass | **60 g** | — (**deleted** — replaced by the e‑bay, §7.11) | explicit in model |
| **Empty, flight‑ready** | ≈ 107 g (Sim 6) † | **≈ 207–213 g** | |
| + C6 motor | +24 g | +24 g | |
| **Liftoff on C6** | ≈ 128 g † | **≈ 231–237 g** | |
| **Landing mass** (spent casing ≈ 12 g) | — | **≈ 222 g** | sizes the canopy, §7.7 |

† *Modeled figures marked † come from Simulation 6, which ran on **rev 3** geometry and the old
2 mm nose. They are historical, not current.*

*Only the body‑tube mass, the 60 g payload and the ≈ 107 g total are read directly from the model
(Simulation 6). The other "modeled" figures are geometry × material density, computed for this
document; they sum to the model's ≈ 47 g structure figure.*

**Guideline:** before any further simulation, correct the body‑tube material in the `.ork` to solid
ABS (or measure the printed part and enter the real mass as an override). Expect the real vehicle
to fly ~30–40 % heavier than the current model.

### 3.3 The 60 g payload / ballast mass

Modeled as a generic mass component: **60 g, ≈ 154 mm long, ⌀25 mm, at ≈ 225 mm from the nose tip**
(body mid‑length + 15 mm). Its density (~800 kg/m³) is consistent with a packed electronics/altimeter
bay or ballast slug.

- As modeled it is **loose mass**. In the real rocket any payload of this size must be a **rigid
  coupler‑mounted bay**, not free mass rattling in the tube.
- Its position — essentially **on the CG** — means it adds inertia and descent mass without buying
  any stability margin. Moving it forward is one of the stability fixes in §4.

---

## 4. Aerodynamics & stability  ⚠️ primary design issue

### 4.1 Finding

**The airframe is not flightworthy as modeled. Static margin is approximately zero, and negative
in the only simulations that ran on rev‑3 (⌀42 mm) geometry — and rev 4 has not been simulated
at all.**

| Source | CP (from nose) | CG (from nose) | Static margin |
|---|---|---|---|
| OpenRocket — Sim 6 (Klima C6‑0, ⌀42 mm, +payload), at rail exit | 222 mm | 228 mm | **−0.14 cal** |
| OpenRocket — Sim 6, through boost | — | — | stays ≤ +0.02 cal |
| Barrowman estimate, this review (not in the model) | ≈ 235–240 mm | ≈ 228 mm | ≈ +0.1 to +0.2 cal |

The second row is a rough hand check done while writing this document, not a value stored in the
`.ork`; it is included only to show the sign of the disagreement. It puts CP slightly aft of
OpenRocket's figure (OpenRocket adds body‑lift normal force on the fat airframe that classic
Barrowman omits), but still **within ~0.2 caliber of neutral** (1 caliber = 42 mm). The accepted
**minimum static margin is 1.0 caliber** and the sport‑model target is **1.0–2.0 calibers**, so the
design is short by roughly a full caliber whichever figure you take — this is a finding, not a
modelling artefact.

> **What rev 4 and §7 change — none of it simulated.** Three mass movements since these runs:
> the near‑solid nose adds **≈ +31 g at ≈ 15 mm** (forward — helps); the thickened tube adds
> **≈ +49 g about ≈ 170 mm** (aft of that — hurts); and the §7 recovery and avionics stack
> **replaces the 60 g dummy at 225 mm with ≈ 75 g spread over 20–265 mm** (net forward — helps).
> Dry mass rises from the modeled ≈ 107 g to **≈ 207–213 g** (§3.2), so the CG shift per gram
> moved is smaller than those figures suggest. The caliber is now **43 mm**, not 42.
>
> **Do not estimate a margin from this by hand.** With four mass items moving and CP never computed
> on rev 4, the net is genuinely unknown until the matrix is re‑run (§13 item 3). The conclusion
> below does not depend on it: **the fins are undersized and must grow.**

### 4.2 Cause

1. Airframe diameter was grown ⌀25 → ⌀35 → ⌀42 mm across three revisions **with the fin planform
   held constant** (Cr 50.8 / Ct 25 / span 30 mm).
2. Fin normal‑force coefficient scales with **(span / body‑diameter)²** — holding the fins fixed
   while the body grew from ⌀25 to ⌀42 mm cut their effectiveness sharply. The measured CP marched
   forward from ~300 mm (Simulation 1, ⌀25 mm) to ~222 mm (Simulation 6, ⌀42 mm), each from that
   revision's own run.
3. The 60 g payload sits on the CG (§3.3) — mass without margin.
4. ~30 g of unmodeled body‑tube mass (§3) sits aft of the CG — margin worse still.

### 4.3 Fix — targets and levers (re‑verify in OpenRocket on the current model)

| # | Action | Rationale |
|---|---|---|
| 1 | ✅ **DONE in rev 5 — fin semi‑span 30 → 55 mm** (§4.5). | Span is the dominant term in (s/d)². Recovered ≈ +1.3 cal on its own. ⚠️ **The "keeping or slightly growing the root chord" half of this item was wrong** — growing the root chord makes the margin *worse*. See §4.5. |
| 2 | **Move the 60 g payload forward**, directly aft of the nose shoulder. | Pulls CG toward the nose; buys margin without adding mass. |
| 3 | If still short, add **nose ballast** (start ~10–15 g) and/or a short **boat‑tail** at the aft end. | Boat‑tail also moves CP aft; ballast is the blunt instrument. |
| 4 | **Target ≥ 1.5 cal at rail exit on the lowest‑impulse flyable motor (B4‑4)**; confirm **≥ 1.0 cal** on every motor in the matrix, including the heaviest payload configuration. | Margin is lowest when the motor is light and the vehicle is heavy. |
| 5 | Re‑check with the corrected (solid) body‑tube mass, not the ρ 310 value. | Real CG is aft of the modeled CG. |

### 4.4 Rail‑exit velocity

| Config | Rail‑exit speed (1 m rod) | Assessment |
|---|---|---|
| Light (no payload) on A8‑3 | 15.4 m/s | marginal‑OK; A8 is the floor |
| Light on B4‑4 / C6 | 17.8 m/s | OK |
| Payload config on C6‑5 (⌀35 rev) | 11.8 m/s | **too low** |
| Payload config on Klima C6 (⌀42 rev) | 12.9 m/s | **too low** |

**Guideline:** keep rail‑exit velocity **≥ 15 m/s**, ideally ≥ 20 m/s. For any payload/heavier
configuration use a **1.2–1.5 m rod or rail**, and do not fly the payload config below a C‑class motor.

---

### 4.5 Fin re‑sizing — rev 5  *(applied to the `.ork`)*

**Change: fin semi‑span 30 → 55 mm. Root chord, tip chord, sweep, thickness, cross‑section,
fillet radius and axial position are all unchanged.** In the `.ork` this is a single parameter:
`<height>` 0.030 → 0.055 m.

#### Method

Classic Barrowman (ellipsoid nose CP at *L*/3, fin term with the body‑fin interference factor
*K* = 1 + *R*/(*s*+*R*)), plus a component CG buildup using the corrected masses of §3 and the
§7.11 recovery/avionics stack. Validated against this document's own hand check: the method
returns **CP = 232 mm** on rev‑4 geometry, against the 235–240 mm recorded in §4.1 — same answer,
same sign of disagreement with OpenRocket.

> **Barrowman omits body lift; OpenRocket includes it, and reports CP further forward.** On the
> ⌀42 rev the gap was ≈ 14 mm (§4.1: Barrowman 235–240, OpenRocket 222). The "est. OpenRocket"
> column below applies that 14 mm as a fixed offset. **It is an estimate from one data point on
> different geometry** — OpenRocket's own figure is the one that counts (§13 item 3).

#### Result

| Configuration | CP | CG | Barrowman | est. OpenRocket |
|---|---|---|---|---|
| **Before** — span 30, realistic mass, C6 | 232 mm | 198 mm | +0.80 cal | **+0.47 cal** ❌ |
| **After** — span 55, realistic mass, C6 (heaviest motor) | 292 mm | 202 mm | +2.10 cal | **+1.77 cal** ✅ |
| After — span 55, realistic mass, B4‑4 | 292 mm | 198 mm | +2.19 cal | +1.86 cal ✅ |
| After — span 55, realistic mass, no motor | 292 mm | 185 mm | +2.49 cal | +2.17 cal ✅ |

Robustness — the result does not depend on the body‑lift estimate:

| Sensitivity (span 55, realistic mass, C6) | Margin |
|---|---|
| No body‑lift correction at all | +2.10 cal |
| Pessimistic correction (20 mm, not 14) | +1.64 cal |
| Against the `.ork`'s **current, uncorrected** masses | +1.51 cal |

**Every case clears the §4.3 target of 1.5 cal.** The C6 row is the binding one: the heaviest motor
puts the most mass aft and gives the worst CG.

> ⚠️ **A trap in that last row.** Open the `.ork` today and OpenRocket will show roughly +1.5 cal —
> a passing number produced by a mass model that is still wrong in both directions (§3: tube 49 g
> light, and the 60 g dummy still standing in for the §7 stack). **It passes for the wrong reasons.**
> Do not let it close §13 item 2.

#### ⚠️ Correction to §4.3 item 1: do **not** grow the root chord

§4.3 item 1 says to enlarge the span "keeping or slightly growing the root chord." Growing it is
**actively counterproductive**, and the sweep is unambiguous:

| Root chord | Fin set mass | est. OpenRocket margin, span 55 |
|---|---|---|
| **50.8 mm (unchanged)** | **14.2 g** | **+1.77 cal** |
| 55.0 mm | 15.5 g | +1.75 cal |
| 60.0 mm | 16.9 g | +1.71 cal |
| 65.0 mm | 18.3 g | +1.67 cal |

**Mechanism:** the fin trailing edge is pinned at 384 mm by the −4 mm bottom offset, so a longer
root chord extends the fin **forward**, dragging its centre of pressure forward with it. The extra
planform area does not compensate, and you pay for the loss in tail mass — which moves CG aft as
well. A 65 mm root costs 4 g and gives up 0.11 cal against doing nothing.

**Span is the whole lever.** It enters as (*s*/*d*)², nothing else comes close, and it is free of
the trailing‑edge coupling. Hence a one‑parameter change.

#### Secondary checks

| Check | Result |
|---|---|
| **Flutter** (NACA TN 4197 form, *t*/*c* on the root chord) | 261 m/s at *G* = 0.85 GPa; **179 m/s** at *G* = 0.40 GPa for weak printed ABS. Against ~58 m/s max flight speed that is a **3.1× margin worst case.** No thickness increase needed — keep 2 mm. |
| **Aspect ratio** | 0.79 → **1.45**. Still a stubby sport fin; no transonic concern at Mach ≤ 0.28. |
| **Mass** | Fin set 8.3 → **14.2 g** (+5.9 g at station 364 mm). This **broke** §3.2's old 8–10 g fin line; §2.1 and §3.2 have been updated, and the knock‑on landing mass pushed the canopy to ⌀500 (§7.7). Re‑read the real figure off OpenRocket. |
| **Tip‑to‑tip** | 103 → **153 mm**. Envelope length unchanged at 384 mm. |
| **Rod clearance** | Lug (⌀7 mm, clocked 19°) sits 8.14 mm off the nearest fin plane; minus lug radius and fin half‑thickness leaves **3.6 mm**. Tight, but this is root‑region geometry and is **unchanged by the span increase**. Belongs with the §9 rail/lug item. |
| **Pad footprint** | Tripod across the fin tips widens 103 → 153 mm. More stable standing on the pad. Nozzle standoff above the deflector is set by the 4 mm aft overhang, not by span — unchanged. |
| **Landing** | Tip radius 51.5 → 76.5 mm is **1.5× the bending moment** at the fin root for the same tip impact. Reinforces §9's integrated fin‑can: do not glue these on. |

---

## 5. Propulsion & motor / delay selection

> **Superseded in part (2026‑09‑30):** the flight motor is now the **Klima D9‑5** (5 s delay, ejection charge used for
> deployment). On the D9aft v1 vehicle OpenRocket gives an optimum delay of 4.6 s: D9‑5 ejects 0.46 s after apogee,
> D9‑3 0.6 s early at 15 m/s, D9‑7 2.5 s late at 19 m/s. D9‑0 stays staging‑only (§5.1). See `Models/AFT_DEPLOY_D9_DESIGN.md` §6.

Motor mount: **18 mm ⌀ × 70 mm** — standard Estes "mini" / Klima 13–18 mm class. Seven motor
configurations are stored in the model:

| # | Motor | Total impulse class | Delay | Use |
|---|---|---|---|---|
| 1 | Estes **A8‑3** | 1/4 A–A | 3 s | Light config only. Floor motor. Optimum delay ≈ 2.75 s → A8‑3 is fine. |
| 2 | Estes **B4‑4** | B | 4 s | Light config. Optimum delay ≈ 4.4 s → good match. **Lowest‑impulse motor to design stability against.** |
| 3 | Estes **C6‑3** | C | 3 s | **Avoid — delay too short** (labelled as such in the model; ~32 m/s at deployment). |
| 4 | Estes **C6‑5** | C | 5 s | Workhorse for payload / heavier / draggier configs. |
| 5 | Estes **C6‑7** | C | 7 s | Workhorse for the light config (higher, slower burn to apogee). |
| 6 | Klima **C6‑0** | C | **0 s** | ⚠️ **Booster/staging motor — not for single‑stage flight.** See below. Currently the model's *default* config. |
| 7 | Klima **D9‑0** | D | **0 s** | ⚠️ **Booster/staging motor — not for single‑stage flight.** |

### 5.1 ⚠️ 0‑second‑delay motors (Klima C6‑0, D9‑0)

A 0 s delay ejects at **motor burnout**, near maximum velocity. In the simulations this produces
**deployment at 57–78 m/s** with OpenRocket "high‑speed deployment" warnings. That is not a
tuning problem — at those speeds the parachute shreds, the shock cord snaps, or the ejection gas
zippers the printed tube.

**Guideline:** remove C6‑0 / D9‑0 from the flyable list, or annotate them "STAGING ONLY." If they
must be used single‑stage, recovery must be triggered by an **electronic altimeter timed to apogee**,
never by motor ejection. Change the model's default motor configuration to **C6‑5** or **C6‑7** so
the file opens on a sane motor.

### 5.2 Delay selection rule

- Target ejection **within ±0.5 s of apogee**; when in doubt, err **long** (a few m/s nose‑down at a
  late deploy beats a 20–30 m/s early deploy).
- OpenRocket "optimum delay" outputs (re‑run on corrected geometry): A8 ≈ 2.8 s, B4 ≈ 4.4 s,
  C6 light config ≈ 6 s, C6 payload config ≈ 4.4 s.
- **Ground‑test the ejection charge** in the actual printed airframe. Printed tubes seal far better
  than cardboard — see §8.6 on the vent hole.

---

## 6. Flight‑performance envelope

Every simulation in the `.ork` is marked **`outdated`**, and they span three different airframe
diameters. Treat the numbers below as historical, not predictive.

| Sim | Motor | Airframe rev | Liftoff mass | Apogee | Max speed | Max accel | Rail‑exit | Deploy speed | Note |
|---|---|---|---|---|---|---|---|---|---|
| Simulation 1 | A8‑3 | ⌀25 | 65 g | 51 m | 29 m/s | 14.6 g | 15.4 m/s | 2.6 m/s | obsolete geom |
| Simulation 2 | B4‑4 | ⌀25 | 67 g | 135 m | 53 m/s | 18.6 g | 17.8 m/s | 4.0 m/s | obsolete geom |
| Simulation 3 "too short delay" | C6‑3 | ⌀25 | 71 g | 279 m | 95 m/s | 19.5 g | 17.8 m/s | **32 m/s** | obsolete geom; delay too short |
| Simulation 4 | C6‑5 | ⌀35 | 128 g | 152 m | 50 m/s | 10.4 g | 11.8 m/s | 6.5 m/s | +payload; margin ≈ +0.4 cal (35 mm caliber) |
| Simulation 5 | C6‑7 | ⌀25 | 71 g | 320 m | 95 m/s | 19.5 g | 17.8 m/s | 9.4 m/s | obsolete geom |
| Simulation 6 | Klima C6‑0 | **⌀42** | 128 g | 68 m | 58 m/s | 11.0 g | 12.9 m/s | **57 m/s** | rev 3 geom; **unstable −0.14 cal** (42 mm caliber); high‑speed deploy |
| "Simulation 7 – Klima" | Klima C6‑0 | **⌀42** | 129 g | 67 m | 58 m/s | 11.0 g | 12.8 m/s | **57 m/s** | duplicate of Sim 6 |
| "Simulation 7" | D9‑0 | ⌀35 | 192 g | 117 m | 79 m/s | 12.4 g | 14.1 m/s | **78 m/s** | +payload +ballast; high‑speed deploy |

Peak Mach across all runs ≤ 0.28 — **the vehicle is firmly subsonic**; airframe aero‑loads and
heating are not design drivers. Peak acceleration ≤ ~20 g.

### 6.1 What is missing

**No motor at all has been simulated on the current ⌀43 mm airframe (rev 4).** B4‑4, C6‑5 and
C6‑7 — the motors you would actually fly — have only ⌀25 / ⌀35 mm runs, and the two ⌀42 mm runs
are both on an unflyable 0‑delay motor. Rev 4 also moved ≈ 80 g of mass (§4.1). This is the top
item in §13.

---

## 7. Recovery system

### 7.1 Architecture decision  *(new — supersedes motor‑ejection recovery)*

> ⛔ **Superseded 2026‑09‑30 by D9aft v1** — recovery is back on **motor ejection**, deployed **aft** (fin can separates on
> printed shear pins; nose fixed). §7.1–7.9 below are the spring design, kept as history. Current design: `Models/AFT_DEPLOY_D9_DESIGN.md`.

**Decision: a compression spring driving a piston, held by a servo‑released latch, as the
*sole* deployment event. The motor's own ejection charge is sealed off and vented overboard.**

This is a commitment, not a preference. The two candidate architectures are **physically
incompatible in one airframe**:

- A **latched** piston blocks motor‑ejection gas — the charge has to break your latch to deploy.
- An **unlatched** piston cannot be spring‑driven — nothing holds the energy.

You cannot fit both and pick on the day. Choosing the spring makes the sealed‑and‑vented motor
mount of §7.6 **mandatory**. The rejected chemical alternative is recorded in §7.10 with its
numbers so it does not get re‑proposed.

### 7.2 The spring — as procured

| Parameter | Value | Source |
|---|---|---|
| Free length | ≈ 85 mm | measured |
| Compressed (cocked) length | ≈ 45 mm | measured |
| **Working stroke** | **40 mm** | 85 − 45 |
| Outer ⌀ | 10 mm | measured |
| Wire ⌀ | **unknown** | — |
| Rate *k*, peak force *F*max | **UNMEASURED — gates the design, see §7.3** | — |
| Slenderness *L/D* | **8.5** | 85 / 10 |

Spring rate goes as the **fourth power of wire diameter**, so the ⌀10 × 85/45 mm envelope alone
does not tell you what this spring will do. Computed for this document over plausible wire gauges,
**assuming the 45 mm figure is the spring's solid height** (coils fully stacked):

| Wire ⌀ | Mean coil ⌀ | Coils | *k* (N/m) | *F*max at 40 mm | Energy | Corrected shear stress | Mass |
|---|---|---|---|---|---|---|---|
| 0.9 mm | 9.1 mm | 50 | 180 | 7.2 N | 0.14 J | 261 MPa | 7.1 g |
| 1.0 mm | 9.0 mm | 45 | 316 | 12.6 N | 0.25 J | 337 MPa | 7.8 g |
| 1.1 mm | 8.9 mm | 41 | 529 | 21.2 N | 0.42 J | 426 MPa | 8.5 g |
| **1.2 mm** | 8.8 mm | 38 | **850** | **34.0 N** | **0.68 J** | 530 MPa | 9.2 g |
| 1.3 mm | 8.7 mm | 35 | 1318 | 52.7 N | 1.05 J | 651 MPa | 9.9 g |

A **20× spread in delivered force** across a range you cannot eyeball. Do not design against an
assumed value.

> If 45 mm is instead a *working* compressed length with the coils still open, every coil count and
> rate above is wrong. **That does not matter** — §7.3 measures the one number that counts,
> directly, and supersedes this whole table. Treat it as orientation, not as data.

> ⚠️ **Buckling.** At *L/D* = 8.5 and 47 % compression this spring **will** buckle unguided
> (the limit is *L/D* ≈ 4–5). A guide rod or captive bore is **not optional** — §7.5 makes the
> piston shaft do that job.

### 7.3 The measurement that gates everything  ⚠️ do this first

Stand the spring upright on a kitchen scale. Press it down with a flat plate until it is **45 mm**
tall. Read the display.

```
F_max [N] = reading [g] × 0.00981
```

That single number sets the nose breakaway, the latch load, the separation velocity and whether
this spring is usable at all.

| Reading | *F*max | Verdict |
|---|---|---|
| ≥ 3.5 kg | ≥ 34 N | **Good.** Nose breakaway 15 N. Expect ≈ 5 m/s separation. |
| 2.5–3.5 kg | 25–34 N | **Acceptable.** Breakaway = *F*max/2. Expect 4–5 m/s. |
| 2.0–2.5 kg | 20–25 N | **Marginal.** Breakaway ≤ 10 N; ≈ 3.3 m/s. Test hard before flying. |
| < 2.0 kg | < 20 N | **Reject.** Two springs in parallel, or source stiffer wire. |

**Design rule: nose breakaway force = *F*max / 2.** Everything downstream follows from it.

### 7.4 Nose cone retention  ⚠️ the real design problem

**Nothing currently holds the nose cone.** It is a 20 mm friction fit on a ⌀38 shoulder. Under
motor ejection that never mattered — charge pressure swamps any plausible friction. Under a
sub‑joule spring it matters enormously, because friction must now be bounded on **both** sides:

- **low enough** that the spring beats it, and
- **high enough** that the nose survives boost, transport and a sun‑warmed pad — and §8.6 already
  records that a printed friction fit *loosens in the sun*.

That is a two‑sided tolerance on a printed friction fit. **It will not hold repeatably.**

**Fix — give the nose a defined, measurable breakaway:**

| Option | Detail | Notes |
|---|---|---|
| **Spring‑ball detent** (preferred) | 3 × ⌀4 mm balls on preloaded plungers in the shoulder, engaging a groove in the body ID | Tunable, reusable, temperature‑stable |
| **Magnetic detent** | 2–3 × ⌀6 × 3 mm N42 discs, nose face to bulkhead face | Very repeatable; pull falls off steeply with gap so it stops fighting the spring after ~1 mm. Loses strength above ~80 °C |

> **Do not use nylon shear pins here.** They are a black‑powder idiom, sized for hundreds of
> newtons — a single 2‑56 nylon pin shears near 140 N, which is 4× what this spring can produce.
> You would be designing the spring around the retainer instead of the other way round.

**Then measure it.** Hang the body vertically, nose down, and add weight until it releases. Target
*F*max/2, tolerance ±20 %, and **re‑measure after every 5 cycles** — detents wear in.

> ⚠️ **Shoulder fit is currently too loose.** A ⌀38 shoulder in a ⌀40 bore is **2.0 mm diametral
> clearance**, against the 0.2–0.3 mm target in §8.4. The nose will rattle and cock under thrust,
> and a cocked nose jams instead of separating. **Grow the shoulder to ⌀39.6–39.8 mm** and take the
> friction *out* with a relieved mid‑section, so only two narrow bands contact. With a detent
> providing retention, the shoulder's only job is **alignment**.

### 7.5 Ejection mechanism

One part solves buckling, latching and load path together: **the piston shaft is also the spring
guide rod.**

```
        +--------------+   <- nose cone (⌀39.7 shoulder, detent-retained)
        |  chute pack  |
   =====+==============+=====
        |///  piston ///|   <- ⌀38 plate, 8 mm
        |  |          |  |
        |  | ((((((   |  |   <- spring, cocked to 45 mm, riding on the shaft
        |  |  shaft   |  |
   =====+==+==========+==+=====   <- anchor bulkhead (bonded, bushed bore)
        |  o-- latch pin (⌀2.5, double shear, brass bushings)
        |  +-- servo, over-centre
        |     E-BAY
```

| Element | Spec | Rationale |
|---|---|---|
| Piston plate | ⌀38 mm × 8 mm, printed, bonded to shaft | 1 mm radial clearance; not a gas seal, a pusher |
| Piston shaft / guide rod | ⌀5 mm steel or alu, ~70 mm | In **tension** (~34 N → 1.7 MPa), so no buckling. Solves spring buckling. |
| Anchor bulkhead | 8 mm, solvent‑welded to tube, bushed bore | Reacts full spring load into the airframe |

> ⚠️ **"Solvent‑welded" blocks a serviceable avionics bay.** The user wants the e‑bay removable for
> same‑day multi‑flight turnaround (inspect, recharge / swap the battery). The only way the stack
> comes out is *forward*, and a bonded anchor bulkhead is a permanent wall across that path.
> Ejection POC §10 item 7 already offers the alternative — "solvent‑welded **or mechanically
> captured**". **Mechanically captured** (this bulkhead reworked as an 18 mm coupler, bonded to the
> forward tube section and held to the aft section by 3 radial M3 through a locally thickened band)
> lets the whole cassette lift out with the forward airframe section, servo‑to‑knob coupler intact.
> The cost: those 3 screws then also carry the **recovery snatch load** (§7.7), which is unverified
> until §7.3 / §7.9 test 4 give a real number. Worked in `Avionics/avionics_bay_packing_40mm.md`
> §9 + `PhoenixABS40-43_avbay_cassette_v1.py`; tracked as **§13 item 16**.
| Latch pin | ⌀2.5 mm hardened steel, **double shear**, **brass or steel bushings**, greased | 3.5 MPa shear — trivial. Bushings are for **galling**, not strength: a steel pin in a bare printed hole will bind. |
| Servo | 9 g micro, ≥ 1.5 kg·cm, 10 mm arm | Pull force ≈ μ·*F* = 0.15 × 34 ≈ **5.1 N** vs ~14.7 N available — **2.9× margin** |

> ⚠️ **The table above is the concept as specified, not the mechanism that was built.** The bench
> POC (§7.5.2) replaces the servo‑over‑centre linkage with a **dead‑centre cam plate** driven by a
> hand knob, and the single double‑shear latch pin with **two radial pins in a draw collar**. Where
> the two disagree, **§7.5.2 is what exists in CAD**; this table records the intent it was built
> against. Do not build from both.

**Stroke reality check.** 40 mm of stroke does *not* push the chute out of a 340 mm tube, and it is
not meant to. The piston's job is to **break the detent and impart separation velocity**; the
departing nose then strips the canopy out on the harness. **The nose must therefore be the
extractor** — tether order is **nose → shock cord → canopy → anchor in body** (§7.7).

At *F*max = 34 N: 0.68 J stored, less ~0.05 J detent work and ~0.15 J friction ⇒ **0.48 J usable**,
giving **≈ 5.1 m/s** separation against a 39 g nose + 12 g harness and a ~150 g body.

#### 7.5.1 Arming and safety  ⚠️

**A servo with no signal goes limp.** If the pin is held by servo *torque*, a brownout on the pad
deploys the rocket. Therefore:

1. **Geometry holds the load, not the servo.** In the holding position the spring load must
   produce **zero or negative torque about the servo output shaft** (over‑centre linkage).
   Verify by test (§7.9), not by reasoning about the linkage.
2. **Mechanical remove‑before‑flight pin** blocking the piston, independent of the servo and of
   all electronics. Removed at the pad, last action before arming.
3. **Detent on the latch pin** so vibration cannot walk it out.

Boost helps you here: 20 g of forward acceleration throws the piston and chute **aft**, away from
release. The threats are transport vibration, landing shock and power glitches — not flight loads.

#### 7.5.2 Bench POC v1 — as built in CAD  *(new)*

`Models/PhoenixABS40-43_ejection_poc_v1.FCStd`, 8 bodies, all exported to STEP + STL.
Full check log: `Models/ejection_poc_build_report_v1.txt`. **This is a bench proof of concept, not
a flight article** — it carries its own ⌀43 tube stub and a dummy nose, and it has had no mass
optimisation.

**Release principle — a dead‑centre cam, not servo torque.** A cam plate drives two radial latch
pins through a draw collar, `x_follower = 6.50 / cos θ`:

| θ | State | Follower | Pin tip | Pressure angle |
|---|---|---|---|---|
| **0°** | **ARMED** | 6.50 mm | *x* = 2.80 | **0.0° — dead centre, dθ/dx = 0** |
| **43°** | **FIRED** | 8.90 mm | *x* = 5.20 | 43.1° (vs 8.5° friction angle) |

At dead centre the spring load produces **no torque about the cam axis**, so the hold is
independent of actuator torque — this is the geometry §7.5.1 item 1 demands. Pin travel is
2.40 mm each; fired, both pins clear the tang bore by 1.20 mm.

| Body | Mass | Role |
|---|---|---|
| AnchorBulkhead | 25.31 g | spring reaction + cage + bracket bores |
| Piston | 9.69 g | ⌀38 × **14 mm** (§7.5 specified 8 mm) |
| CamPlate | 2.52 g | release cam, 0–43° |
| Knob | 3.42 g | hand actuator, R 14 mm; RBF clip hole |
| DrawCollar | 1.17 g | carries the follower to the pins |
| LatchPinCollar (×2) | 0.55 g ea. | radial pin carriers |
| *TubeStub, DummyNose* | *33.30 / 21.81 g* | *bench fixtures — not flight parts* |

**What the CAD confirms** (geometry and hand analysis only — see the caveat below):

- **Containment.** Static structure ≤ R 19.85 in the R 20.0 bore; the moving mechanism sweeps to
  **R 17.60 over the whole 0–43° range**, not merely at the endpoints — clear of the R 19.5
  running limit. An SG90 keepout (12.4 × 23 × 22.7) fits at R 13.06.
- **Stroke.** 40 mm, draw collar to bulkhead — matches §7.5.
- **Spring seat.** Cocked column ⌀11 × 45 mm clear of both bulkhead and piston; counterbore
  r 5.75 captures a ⌀10 spring by 0.75 mm; ⌀5 rod against an assumed ≥ ⌀7 spring ID.
- **Effort.** 5.1 N friction per pin → 7.0 N slot normal → **84.9 N·mm** at the knob = **6.1 N**
  at the fingertip. An SG90 at 147 N·mm leaves **1.7×** — thinner than §7.5's 2.9× claim, which
  was computed for a linear pull and no longer applies.
- **Bearing.** Pin on tang **7.6 MPa against ~40 MPa** allowable, 4.0 mm engagement.
- **No collisions** anywhere in the sweep, and every cut feature (window, access slot, bracket
  bores, cam slot, cam bore) is confirmed non‑vacuous.
- **RBF.** An R‑clip through knob and carrier passes freely at ARMED and fouls the knob after 43°
  of travel, independent of the electronics.

**Deviations from §7.5 / §7.5.1 — read before building:**

1. **The RBF clip blocks the actuator, not the piston.** §7.5.1 item 2 asks for a pin blocking the
   *piston*. Blocking the cam is sufficient only while the cam is what holds the pins; it does not
   restrain the piston if a pin, collar or bracket fails. Decide deliberately which one you want.
2. **No latch‑pin detent** (§7.5.1 item 3) is present in v1.
3. **No nose detent.** The POC separates a dummy nose; the ball or magnetic detent of §7.4 is not
   modeled, and the two‑sided breakaway tolerance is still unsolved. §7.4 stays fully open.
4. **Manual actuation only.** The servo exists as a keepout volume; no horn, linkage or mount.
5. **Piston is 14 mm thick**, not the 8 mm of §7.5 — it costs bay length in §7.8.

> ⚠️ **None of this qualifies anything.** Every figure above is CAD geometry or hand calculation.
> §7.5.1 item 1 says in as many words: *verify by test, not by reasoning about the linkage.* The
> dead‑centre result predicts test 3 will pass; it does not replace it. **All seven §7.9 tests
> remain open.**

### 7.6 Motor ejection charge — seal and vent  ⚠️ mandatory under §7.1

> ⛔ **Superseded 2026‑09‑30:** the charge is no longer vented overboard — it **is** the deployment. It fires through a ⌀14
> port in the fin‑can thrust ring into the chute bay; the e‑bay is sealed behind a solid bulkhead. `Models/AFT_DEPLOY_D9_DESIGN.md` §1, §5.

With the spring as sole deployment, the motor's charge must go **overboard**, never into the
recovery bay.

- **Bonded bulkhead** at the forward end of the motor mount.
- **Vent generously — do not attempt to contain.** A C6 charge at 50 psi on a ⌀40 mm disc is
  **433 N** into printed ABS; at 100 psi, **866 N**. Large vents mean the pressure never builds.
- **2 × ⌀5 mm vents**, 180° apart, in the aft body.

> **Vent band, from the `.ork`:** fins occupy −4 to **+46.8 mm** from the aft end (bottom offset
> −4 mm, root chord 50.8 mm); the forward centring ring sits at **67 mm**. The clean band is
> **46.8–67 mm — 20.2 mm tall.** Two ⌀5 mm holes fit, but only just. **Confirm on the printed part
> before committing**, and clock them into fin gaps.

Expect scorching around the vents. That is cosmetic; accept it or add a sacrificial band.

**Motor selection.** Check whether a **plugged / inert‑delay 18 mm** motor is available to you — it
removes this problem entirely. Note that Klima **C6‑0 / D9‑0 are *booster* motors**: no ejection
charge, but they vent burning particles *forward*, so they need the same sealed bulkhead anyway.
This does **not** rehabilitate them for single‑stage flight (§5.1).

### 7.7 Canopy, harness and anchor

| Parameter | Was | **Now** | Reason |
|---|---|---|---|
| Canopy ⌀ | 300 mm | **500 mm** | Landing mass is ≈ 222 g (§3.2) — rev‑5 fins added ≈ 6 g |
| Descent rate | **7.9 m/s** at 222 g | **4.8 m/s** (⌀500) | ≤ 5 m/s target for printed fins |
| Shroud lines | 2 mm **elastic** | **braided nylon or Kevlar, 6 × 350 mm** | Elastic lines recoil and tangle |
| Shock cord | 400 mm elastic | **≥ 1.2 m** (≥ 3 × body length) | 400 mm nose‑slaps on rebound |
| Leader | none | **≥ 300 mm Kevlar or Nomex** | Never anchor bare elastic near the motor |
| Anchor | *"does not need to be attached"* | **printed eyelet or U‑bolt on the anchor bulkhead** | §7.5's bulkhead is already a structural member — use it |

- At the 222 g landing mass: ⌀300 → **7.9 m/s**, ⌀400 → **6.0**, ⌀450 → **5.3**, ⌀500 → **4.8 m/s**.
  **⌀450 no longer makes the ≤ 5 m/s target** — it did at the 200 g figure this section previously
  carried. Use ⌀500; drop to ⌀450 only if bay length forces it, and accept 5.3 m/s.
- **Tether order: nose → shock cord → canopy → bulkhead eyelet.** The nose is the extractor
  (§7.5); getting this order wrong means the canopy never leaves the tube.
- **Nomex blanket** between piston and canopy regardless. There is no charge in the bay by design,
  but a seal can fail and the piston can scuff.
- The anchor bulkhead now carries **both** the spring reaction and the full recovery shock. Size it
  for the recovery load — that is the larger of the two.

### 7.8 Internal layout  *(stations from the top of the body tube)*

> ⛔ **Superseded 2026‑09‑30** — current layout (e‑bay 45–110, bulkhead 131, chute bay 131–281, pins 276.6): `Models/AFT_DEPLOY_D9_DESIGN.md` §2.

| Station | Length | Contents |
|---|---|---|
| 0 – 20 mm | 20 | Nose shoulder engagement *(extend toward 43 mm per §9 — costs bay length)* |
| 20 – 110 mm | 90 | Canopy + Nomex |
| 110 – 118 mm | 8 | Piston plate |
| 118 – 163 mm | 45 | Spring, cocked, on shaft |
| 163 – 171 mm *(→ 163 – 181 if serviceable)* | 8 → **18** | Anchor bulkhead + recovery eyelet. As a serviceable cassette (§13 item 16) it becomes an 18 mm coupler; the extra 10 mm is taken **aft, out of the e‑bay's slack** (below), not forward — §7.7 has no length to give. |
| ~181 mm | — | **Transverse bench‑service joint** *(new, serviceable build only)* — opened on the bench, never in flight; recovery separates at the nose (§7.5). The forward section lifts the whole avionics cassette out. |
| 181 – 265 mm | **84** | **E‑bay** — flight computer, battery, servo, latch. Real bay ≈ 54 mm (`Avionics/avionics_bay_packing_40mm.md`), so ≥ 30 mm of slack absorbs the coupler. As a removable cassette it withdraws forward through the ~⌀40 bore. |
| 265 – 340 mm | 75 | Motor mount + sealed bulkhead + vent band |

94 mm of e‑bay is generous for a micro servo, a 1S LiPo and an altimeter. **The e‑bay needs its own
static port** for the barometric sensor — 1 × ⌀1.5 mm, or 3 at 120°, away from the ⌀5 mm ejection
vents (§8.6). Keep it a **plain drilled hole** (no inward sealing boss): the BMP388 only needs to
share air with it, and a plain hole keeps the bore clean for cassette extraction (§13 item 16).

### 7.9 Qualification tests  — all before first flight

> ⛔ **Superseded 2026‑09‑30** — the D9aft test list is in `Models/AFT_DEPLOY_D9_DESIGN.md` §9 (pin coupon, slide friction, bulkhead leak,
> casing fit, pack test, harness pull).

| # | Test | Pass criterion |
|---|---|---|
| 1 | **Spring force** (§7.3) | *F*max ≥ 25 N |
| 2 | **Nose breakaway**, dead weight | *F*max/2 ± 20 %, stable over 5 cycles |
| 3 | **Latch proof load** — servo **unpowered and disconnected**, 4 × *F*max ≈ **136 N** on the piston | **Pin does not move.** This is the single test that discriminates the whole latch design. |
| 4 | **Separation, packed** — full canopy, 10 consecutive cycles | 10/10 clean, canopy fully out |
| 5 | **Thermal** — repeat 2 and 4 after 1 h at 40 °C in sun | Breakaway still in band |
| 6 | **Ejection vent** — live motor, sealed bulkhead, airframe restrained | No gas into recovery bay; bulkhead intact |
| 7 | **Brownout** — cut power mid‑sequence at 5 points | No deployment in any case |

> **CAD closes none of these.** The POC of §7.5.2 predicts test 3 (dead‑centre hold, 7.6 MPa
> bearing) and test 4 (no collision through the sweep), but a prediction is not a pass. Tests 1, 2,
> 5, 6 and 7 have no CAD analogue at all. **7/7 still open.**

### 7.10 Rejected alternative: sodium bicarbonate thermal decomposition

Recorded so it is not re‑proposed. **2 NaHCO₃ → Na₂CO₃ + H₂O + CO₂.**

The idea is attractive because the *mass* looks trivial — raising the ≈ 38 cm³ bay above the piston
to ≈ 1.8 bar absolute, which is what it takes to shift a ⌀40 mm nose, needs ≈ 2.3 mmol of gas, or
**0.2 g of NaHCO₃**. That figure is a trap. The blockers are power and temperature:

| Blocker | Number |
|---|---|
| **Power** | Decomposition is endothermic at **+136 kJ per mol CO₂**, plus sensible heat of bed, crucible, heater and surrounding structure ⇒ ≈ **1 kJ** system energy. Deployment is a tens‑of‑milliseconds event: 1 kJ in 50 ms is **20 kW**. Stretched to 5 s it is still 200 W ≈ **54 A** off a 1S LiPo. |
| **Temperature** | Useful reaction rates need **150–200 °C**. **ABS T_g ≈ 105 °C.** The heater would run above the softening point of the airframe, 1.5 mm from it. |
| **Yield** | Half the gas is **H₂O vapour**, which condenses on the cool tube wall and takes its pressure back out. |
| **Controllability** | Below ~100 °C the reaction takes hours; it ramps rather than fires. **You can start it but not trigger it, and not stop it.** |

**Conclusion: it produces an untimeable pressure ramp, not a deployment event.** The fast gas
system this idea reaches for already exists and is the ejection charge in the motor — which is why
§7.6 vents it rather than trying to reinvent it.

### 7.11 Mass and CG consequences

| Item | Mass |
|---|---|
| Spring | ~9 g |
| Piston + shaft + latch pin | ~14 g |
| Anchor bulkhead + eyelet | ~8 g |
| Servo (9 g class) | ~9 g |
| Flight computer + battery + wiring | ~21 g |
| Canopy (⌀500) + harness + leader | ~16 g |
| **Recovery + avionics total** | **≈ 77 g** |

> ⚠️ **The as‑built POC does not fit this budget.** The printed mechanism alone — bulkhead, piston,
> cam plate, knob, draw collar, two pin collars — is **43.2 g**, against the **22 g** this table
> allows for bulkhead + eyelet + piston + shaft + latch pin. The **anchor bulkhead alone is 25.3 g
> against 8 g.** The bench build adds a further ~22 g of M5 rod, ~8 nuts, pins and clip, but that is
> workshop hardware standing in for a ⌀5 flight shaft — quote it separately, do not read it as
> flight mass. The POC was built for function, not mass, so treat the printed 43.2 g as an **upper
> bound and a redesign target** rather than a new budget line; until it comes down, §3.2's ≈ 31 g
> recovery‑hardware figure is optimistic. See §13 item 15.
>
> Separately, the **aft retention** hardware of §9 adds **+18.89 g net** — 23.89 g of new parts,
> less what they displace in the `.ork` — **at 378.5 mm**, right at the tail. On the `.ork` baseline
> alone that is CG **+19.4 mm aft (0.45 cal)**, and with §3's body‑tube correction **+13.0 mm
> (0.30 cal)**. It works directly against §4.5's fin fix. Per this section's own rule, **do not net
> these against the forward items to quote a margin** — they are inputs to the §13 item 3 re‑run,
> nothing more.

This **replaces** the 60 g dummy payload of §3.3 and distributes it **forward** — the spring,
piston and canopy group sits at ≈ 20–170 mm, well ahead of the dummy's 225 mm station.

> ⚠️ **This is not a stability fix — and do not quote a margin off it.** Four mass items have
> moved since the last simulation, and they pull in opposite directions: the recovery and avionics
> stack (≈ 75 g, spread over 20–265 mm) and the near‑solid nose (≈ +31 g at ≈ 15 mm) pull CG
> **forward**; the thickened body tube (≈ +49 g about ≈ 170 mm) pulls it **aft**. Dry mass roughly
> doubles, so the CG shift per gram moved is smaller than the raw figures suggest — and **CP has
> never been computed on rev 4 at all.** The net margin is **unknown** until §13 item 3 runs.
>
> What is *not* in doubt: recovery mass helps, and it is nowhere near enough on its own. Fin span
> remains the dominant term (§4.3 item 1) and **§13 item 1 stays open.**

**Design tension to watch:** recovery, avionics and the rev‑5 fins push landing mass to ≈ 222 g,
which forces a **⌀500 mm** canopy (§7.7), which needs more bay length. The largest discretionary mass on the vehicle is
the near‑solid **39 g nose cone** (§3) — but hollowing it takes CG *aft* and costs stability.
Do not trade it away without re‑running §4.

---

## 8. Materials & 3D‑printing guidelines

### 8.1 Material map (as modeled)

| Part | Material | ρ (kg/m³) | Intent |
|---|---|---|---|
| Nose cone, fins + fillets, motor mount | ABS, 100 % infill | 1050 | load‑bearing / leading structure |
| Body tube, launch lug | ABS, "30 % infill" | 310 | shell (see §3 — prints near‑solid at 1 mm wall) |
| Centring rings, engine block | Cardboard | 680 | non‑printed inserts |
| Parachute | Ripstop nylon | 0.067 (areal) | — |
| Shock cord / shroud lines | Round elastic, 2 mm | 0.0018 (linear) | — |

**Filament:** ABS as designed. ABS needs an enclosure and warps on wide flat bases (the 42 mm
aft face, the fin roots). **ASA** (better UV/weather, similar strength) or **PETG** (much easier,
slightly heavier, lower stiffness) are acceptable substitutes if warping or fumes are a problem —
re‑enter the density if you switch.

### 8.2 Per‑part print recommendations *(recommendations, not values from the model)*

| Part | Orientation | Perimeters / infill | Layer height | Notes |
|---|---|---|---|---|
| Body tube | vertical (axis = Z) | 2–3 perimeters, 0 % infill | 0.20 mm | brim for adhesion; no hoop seam; best roundness. Long print. |
| Nose cone | vertical, tip up | 3 perimeters + solid cap | 0.12–0.16 mm | fine layers for surface; a few support lines only at the very tip |
| Fin‑can (see §9) | airframe axis vertical, fins pointing up | 4 perimeters / 40–60 % | 0.16–0.20 mm | fin faces lie in layer planes; avoids a single inter‑layer bond in peel at the fin root |
| Motor mount | vertical | ≥ 4 perimeters / solid | 0.16 mm | thin wall — print slow, check bore against a spent casing |
| Launch lug / rail standoff | vertical, bore = Z | 3 perimeters | 0.20 mm | print as part of the fin‑can if possible |

### 8.3 Wall thickness

✅ **Closed in rev 4.** The body wall is now **1.5 mm** (OD 42 → 43 mm, ID held at 40 mm), which is
the bottom of the 1.5–2.0 mm band this section previously recommended. Two consequences follow:

- The **density in the `.ork` was not corrected** at the same time, so the mass error grew rather
  than shrank — §3.
- Still recommended: move the load paths into an integrated fin‑can (§9) and a reinforced
  nose‑shoulder band. A thicker wall helps the hoop, not the fin‑root butt joint.

### 8.4 Fits & tolerances *(design targets)*

| Interface | Target clearance | Method |
|---|---|---|
| Nose shoulder ↔ body ID | 0.2–0.3 mm diametral | **⚠️ currently 2.0 mm** (⌀38 in ⌀40) — grow the shoulder to ⌀39.6–39.8 mm. Alignment only; retention is the detent (§7.4) |
| Motor ↔ mount bore (18 mm nom.) | slip fit + light friction | print a test ring; add a retainer regardless |
| Centring ring ↔ tube / mount | 0.1–0.2 mm | glued; rings are the structural tie between mount and airframe |
| Motor rim ↔ cap lip *(as built, §9)* | 0.4 ± 0.1 mm axial | ✅ met in aft retention v1; 1.5 mm radial lip on the casing rim |
| Retainer boss tip ↔ cap floor *(as built)* | 1.0 ± 0.2 mm | ✅ met; radial thread interlock 1.0 mm. Cap seats on a 45° cone, not on the boss tip or the thread |
| Retainer thread, boss ↔ cap *(as built)* | 0.2 mm radial / 0.1 mm flank | ✅ met; ⌀38.4/⌀36.0 boss against ⌀38.8/⌀36.4 cap, 3.0 mm pitch, 10 mm engagement (§9) |
| Centring ring ID ↔ motor‑tube OD *(as built)* | 0.4 mm diametral | glue gap, ⌀21.2 over ⌀20.8 |

### 8.5 Post‑processing

Acetone‑vapour smoothing is optional on ABS for cosmetics; it slightly softens thin walls, so do it
before final fit checks, not after.

### 8.6 Vent / static port  *(new requirement)*

A printed airframe is effectively **airtight**, unlike cardboard. This causes two problems:
(1) ejection gas over‑pressure with nowhere to bleed, and (2) a sun‑warmed sealed tube popping its
nose on the pad ("pressure drift"). **Add a vent:** one ~2 mm hole (or three at 120°) in the body
tube, forward of the payload, away from a fin. Size it to the internal volume during ejection
ground tests.

---

## 9. Structural & assembly guidelines

- **Integrated fin‑can.** Do **not** glue separate printed fins onto a printed tube — a butt joint
  in FDM ABS is the single most common failure mode. Print the aft section as **one piece: aft body +
  three fins + motor‑mount interface** (and ideally the rail standoff). Split the airframe at a
  coupler joint forward of the fins instead.
- **Fin fillets** (4 mm radius, as modeled) should be part of the printed fin‑can, not added later.
- **Motor retention.** Add a **positive retainer** — a screw‑on printed cap engaging threads on the
  mount, or a metal clip — in addition to the engine block. Friction fit alone is not acceptable for
  a reusable model.

  ✅ **Modeled in v1 and it assembles.** `Models/PhoenixABS40-43_aft_retention_v1.FCStd`
  builds a screw‑on `MotorRetainerCap` (9.04 g) over an `AftRetainerBase` (12.09 g) plus a
  `FwdCenteringRing` (2.79 g); cap + base = 21.13 g against a 22 g target, all three watertight,
  STEP + STL exported. Thread is trapezoidal, single‑start RH, 3.0 mm pitch, boss ⌀38.4/⌀36.0
  against cap ⌀38.8/⌀36.4, 10 mm engagement, 0.2 mm radial / 0.1 mm flank clearance. The cap
  bottoms on a **45° cone seat** (`r = z + 21.5`), not on the boss tip or the thread — that
  preloaded cone is also the anti‑backout. Full notes: `Models/AFT_RETENTION_DESIGN.md`.

  **The earlier "does not assemble" finding is closed.** Two distinct bugs caused it. First,
  the boss diameters had been scaled from `../SampleRocketABS33-36`, whose boss (r 12.8–14.0)
  and cap (r 14.2–15.4) ridges occupy **disjoint radial bands** — that sibling pair cannot
  interlock at all, and the error propagated. Second, every OCCT sweep mode fails on this
  geometry: `isFrenet=True` makes booleans silently return the other operand (the thread
  vanishes), `isFrenet=False` drifts the pitch to 3.2 mm, and the aux‑spine setters raise
  signature errors. The thread is now generated as an **exact faceted helix** — measured off
  the STL at 1.591 mm ridge width and **3.0000 mm pitch**.

  ✅ **A sealed variant now exists — `AftSectionSealed`, 29.07 g.** cfg A above is a bonded
  insert with an open ⌀14 engine block. **cfg B is the aft airframe itself**: real 43/40 wall,
  **3 through-the-wall fin slots**, two integral centring rings at Z 12 and 40, and a **solid
  bulkhead at Z 55.9–58.9** that seals the motor mount, floors the recovery bay, and takes
  thrust across the motor's whole ⌀18 face — so cfg B needs no engine-block ring at all.
  **The bulkhead's forward face at Z 58.9 is the forward-most plane of the part**; the lip
  hangs *below* it rather than standing on it, formed by the bore stepping inward over a 4 mm
  taper so wall and lip are one continuous wall. The forward tube slides down over the
  ⌀39.7 lip (0.3 mm diametral epoxy gap) and lands on the shoulder at Z 51.4.

  **Fin slots** are 2.3 mm wide (2.0 mm fin + 0.15 mm epoxy per side) at 0/120/240°, spanning
  Z 0.6–51.4, cut through the wall **and both centring rings** and stopping 0.3 mm off the
  motor tube — so a fin tab bonds to the mount, not to the outer skin alone, which is the
  butt-joint failure this section warns about. The fins themselves are not modeled, so the
  planform can still change without reprinting the section while item 1 is open.

  ⚠️ **The lip is only 7.5 mm.** The bulkhead is pinned at the motor's forward face and the
  50.8 mm fin root needs full ⌀43 beneath it, leaving 7.5 mm between them — a short lap for a
  joint carrying recovery shock. §4.5's own sweep says a *shorter* root slightly *improves*
  margin, so shortening it buys lip almost free: root 45 → 13.3 mm, 40 → 18.3 mm. That is a
  `.ork` change and a re-run, so it was not made. See `Models/AFT_RETENTION_DESIGN.md` §4A.

  **No vents, deliberately.** §7.6's vent train exists to route a motor's ejection charge
  overboard. **This build has no ejection charge**, so an earlier revision's 2 × ⌀5 mm wall
  vents, three motor-tube windows and 9 mm plenum were holes in the airframe buying nothing;
  they are gone, along with the engine-block ring and 12 mm of length. The verifier now
  asserts the airframe and motor-tube walls are **unbroken**. A `VENTED` constant in the build
  script reinstates the whole train — built and verified — **if the motor choice ever changes.**

  ✅ **The integrated fin can now exists — `AftFinCan`, 46.12 g (cfg C).** It is cfg B with
  the rev‑5 fins fused in, no slots, and **4 mm root fillets** on both sides of every fin —
  the one‑piece aft section this section has asked for since the start, with the bond line at
  the fin root removed entirely. Fins are also available as a standalone `Fin` part (5.45 g
  each, TTW tab, 1 mm rounded edges) for the slotted cfg B.

  The configurations are **not interchangeable**: cfg B and C replace 51.4 mm of the body tube.
  Net mass penalties are cfg A **+18.91 g at 378.5 mm (0.45 cal)**, cfg B **+24.69 g at
  361.6 mm (0.50 cal)**, cfg C **+25.41 g at 361.5 mm (0.51 cal)** — B and C are 0.7 g apart,
  so that choice is about printing, not mass. **cfg C needs support under the three fin
  trailing edges** (the fin springs out its full 55 mm span in the 0.4 mm between Z 0.6 and
  1.0); cfg B prints support‑free and puts the fin layers in their best orientation, at the
  cost of three bonded joints. See `Models/AFT_RETENTION_DESIGN.md` §4B.

  ⚠️ **Consequence for reviewers: OCCT booleans against these parts are not trustworthy**, and
  the build report deliberately no longer makes any thread claim. `Models/verify_aft_retention.py`
  ray‑casts the exported STLs instead and is the authority — currently **all checks pass**, with
  0.000 % clash through a full 0–720° unscrew sweep — a figure checked against a deliberately
  interfering build of the same parts, which the same test reports at 10.5 % and localises to
  the thread band, so the check discriminates. **Still unprinted and unfitted (§13 item 9).**
- **Recovery anchor.** Provide a printed eyelet or U‑bolt boss on the **forward centring ring** or a
  bulkhead; route the Kevlar leader through it (§7).
- **Rail / lug.** A **single 35 mm lug at mid‑body** on a 380 mm rocket lets the vehicle pivot on the
  rod. Use **two lugs** (one ~40 mm below the nose, one at the aft end) **or rail buttons** on a
  standoff. Match the bore to the intended rod: **3/16 in (4.8 mm)** for the light config, **1/4 in
  (6.35 mm)** for payload flights — enlarge the bore and re‑model if you go to 1/4 in.
  ⚠️ **The rod actually in hand is ⌀4.0 mm, and the pad (§12.1) is built for it.** Against the ⌀5.0
  bore specced above that is 0.50 mm of radial slop — 1.6° of tilt, ≈ 11 mm of pointing error at the
  nose. Decide one of two ways *before* the lug is modeled: **bore it ⌀4.4** for the 4.0 mm rod, or
  buy a 4.8 mm rod and keep ⌀5.0. Either way this is now a blocking input to modeling the lug, not
  a preference. With two lugs the **aft** lug sets the rest height on the pad; the fins still land
  on the deflector ring, so the pad itself is unchanged.
- **Nose‑shoulder joint.** 20 mm shoulder engagement is short for a 42 mm tube; extend to ≥ 1 ×
  body diameter (≥ 42 mm) so the joint can carry recovery loads without splitting the tube.

---

## 10. Finish & livery

| Element | Colour | Hex (approx.) | Sheen |
|---|---|---|---|
| Body tube | desert tan / sand | `#D4B991` | semi‑gloss |
| Nose cone | charcoal / near‑black | `#333333` | semi‑gloss |
| Fins | white | `#FEFEFF` | matte |
| Accent stripes | blaze / safety orange | `≈ #F26A1E` | — |

- **`decals/BodyStripe.png`** — a charcoal block above an orange band, applied as a near‑full‑length
  vertical wrap on the body tube.
- **`decals/TailStripe.png`** — an orange band, applied to the fins / aft body.
- Keep the nose dark and at least one high‑contrast surface (white fin face or a bright band) for
  tracking against sky and ground. Consider a small registration mark aligning the nose, lug/rail
  line, and a fin, so the airframe always reassembles in the same clocking.

---

## 11. Pre‑flight & flight‑ops checklist

**Build acceptance**
- [ ] Stability re‑verified on the *current* geometry: ≥ 1.0 cal on every motor, ≥ 1.5 cal on B4‑4 (§4).
- [ ] Measured CG matches the model within ±5 mm (mark the CG on the airframe).
- [ ] Swing test passes (tie at CG, ~3 m line, circle overhead — nose leads).
- [ ] Motor retainer engages; engine block seated.
- [ ] Recovery: Kevlar leader anchored to the §7.5 bulkhead; shock cord ≥ 1.2 m; canopy ≥ ⌀450.
- [ ] **Spring *F*max measured (§7.3); nose breakaway measured at *F*max/2 (§7.4).**
- [ ] **Latch proof load passed at 4 × *F*max, servo unpowered (§7.9 test 3).**
- [ ] **10/10 packed separations achieved (§7.9 test 4).**
- [ ] **Motor‑mount bulkhead sealed; 2 × ⌀5 mm ejection vents clear (§7.6).**
- [ ] E‑bay static port present and clear; ejection vents clear (§7.8, §8.6).
- [ ] *If the bay is built as a serviceable cassette (§13 item 16):* recovery‑snatch proof of the 3‑screw band joint passed at ≥ 4 × the measured separation load — **the anchor bulkhead is not bonded, so this joint is now in the recovery load path** (§7.5, §7.7).

**Field prep**
- [ ] Motor delay chosen for the config and re‑checked against a current sim (§5.2).
- [ ] Ejection charge ground‑tested in *this* airframe at least once.
- [ ] Nomex installed; canopy folded, lines not wrapped; **tether order nose → cord → canopy → anchor** (§7.7).
- [ ] **Spring cocked, latch engaged, remove‑before‑flight pin fitted** (§7.5.1).
- [ ] *Serviceable cassette (§13 item 16):* all 3 band screws in and torqued; clocking witness line across the band notch and the forward‑tube seam aligned; battery pigtail seated and strain‑relieved.
- [ ] **Guided** rod length ≥ 1.0 m (light) or ≥ 1.2–1.5 m (payload); rail‑exit speed check.
      **On the §12.1 pad this is rod length − 294 mm, not rod length** — so ≥ 1300 mm / ≥ 1500 mm
      of rod. A 1 m rod gives 706 mm and misses §4.4's 15 m/s floor.
- [ ] **Pad staked or ballasted** — the bare pad tips at 8.7 m/s (§12.1 `[5]`). Peg through each
      foot, and/or 1 kg on the hub tie‑down, before the rocket goes on the rod.
- [ ] Payload bay rigid and secured; no loose mass.
- [ ] Nose friction fit checked cold (it loosens in sun).

**Do‑not‑fly**
- [ ] Remove‑before‑flight pin still installed, or latch proof load (§7.9 test 3) not passed.
- [ ] Motor‑mount bulkhead unsealed or ejection vents blocked (§7.6).
- [ ] 0‑delay motor (Klima C6‑0 / D9‑0) with motor‑ejection recovery.
- [ ] C6‑3 (delay too short).
- [ ] Any config with computed static margin < 1.0 cal or rail‑exit speed < 15 m/s.

---

## 12. Project file organization & conventions

```
PhoenixABS40-43/
├── DESIGN.md                     ← this document
├── PhoenixABS40-43.ork           ← OpenRocket model — SINGLE SOURCE OF TRUTH
├── Models/                       ← CAD: .FCStd source, .step exports, build scripts,
│                                   build reports (.FCBak, __pycache__ are throwaway)
├── Print Files/                  ← .stl per part — at present the 8 POC bodies only
│   ├── Launch Pad/               ← ground support: tripod pad for the ⌀4.0 mm rod (§12.1)
│   └── Assembled Ready to PRINT/ ← (empty) build‑plate‑arranged slicer projects
└── Ejection System/              ← (empty) — fold into Models/ or delete
```

- **`.ork` is authoritative** for geometry, mass, CG/CP and simulation. Change a dimension there
  first, then propagate to CAD, then update this file.
- **`Models/`** — parametric CAD source (`.FCStd`) plus the STEP export of every body and a
  machine‑written check log per assembly. Naming: `PhoenixABS40-43_<Component>_v<rev>.step` for
  parts, `PhoenixABS40-43_<assembly>_v<rev>.FCStd` for the document, and
  `<assembly>_build_report_v<rev>.txt` for its log. `.FCBak` and `__pycache__/` are regenerable —
  do not treat them as sources.
- **`Print Files/`** — slicer‑ready, pre‑oriented, support‑minimised meshes (STL/3MF).
  `Assembled Ready to PRINT/` holds `.3mf` project files already arranged on the plate for a
  named printer/filament. **A part reaches this folder only once its build report is clean** —
  which is why the three aft‑retention bodies have a STEP but no STL (§9).
- **The `.py` in `Models/` is the source of truth; the FreeCAD MCP is the working surface.**
  Prototype and inspect in the live document through the `freecad` MCP, then **back‑port every
  geometry change into the script** and re‑run it (`freecadcmd.exe <script>`) so it regenerates the
  FCStd, the STEP/STL exports, the pre‑oriented print files and the build report by itself. Never
  edit an export by hand, and never leave the script behind the model. Back‑port the *verification*
  too, not just the geometry. *(This bullet previously said the `.py` files were a "v1 legacy
  record… do not extend that pattern" — that was reversed on 2026‑09‑06 and is now wrong; the
  launch‑pad build is the current example of the correct pattern. The MCP being unreachable, as on
  2026‑09‑02, is not a blocker: run the script headless.)*
- **Every assembly carries a machine‑checked build report.** Mass and envelope per body, mesh‑vs‑
  solid watertightness, interference and swept‑collision booleans, and an explicit non‑vacuity check
  that each cut feature actually exists. A report with a `FAIL` line is a design that does not
  assemble — §9's retainer is exactly that case.
- **Revision discipline:** bump the rev tag whenever a *flight‑affecting* parameter changes
  (diameter, length, fin planform, dry mass, motor mount). Record the change in §1's table.
- **Simulation hygiene:** after any geometry or mass change, re‑run the **entire motor matrix** in
  one pass, and delete or clearly rename superseded simulations in the `.ork` (the current mix of
  three airframe diameters in one file is a trap for readers).
- This project is **not under version control.** Consider `git init` so geometry changes,
  simulation results and this document have a history.

### 12.1 CAD parts inventory  *(v1 — new)*

| Assembly | Body | Mass | STEP | STL | State |
|---|---|---|---|---|---|
| Aft retention | AftRetainerBase | 12.09 g | ✅ | ✅ | ✅ verifies clean; unprinted (§9) |
| Aft retention | MotorRetainerCap | 9.04 g | ✅ | ✅ | ✅ verifies clean; unprinted (§9) |
| Aft retention | FwdCenteringRing | 2.79 g | ✅ | ✅ | ✅ clean; **cfg A only** |
| Aft retention | AftSectionSealed | 29.07 g | ✅ | ✅ | ✅ **cfg B** — sealed aft airframe section, fin slots, no vents (§9) |
| Aft retention | Fin ×3 | 5.45 g ea. | ✅ | ✅ | ✅ **cfg B** — rev‑5 planform, TTW tab, rounded edges (§9) |
| Aft retention | AftFinCan | 46.12 g | ✅ | ✅ | ✅ **cfg C** — one‑piece fin can, 4 mm root fillets (§9) |
| Ejection POC | AnchorBulkhead | 25.31 g | ✅ | ✅ | ⚠️ 3× the §7.11 allowance |
| Ejection POC | Piston | 9.69 g | ✅ | ✅ | ⚠️ 14 mm, not 8 mm (§7.5) |
| Ejection POC | CamPlate | 2.52 g | ✅ | ✅ | ✅ |
| Ejection POC | Knob | 3.42 g | ✅ | ✅ | ✅ manual only |
| Ejection POC | DrawCollar | 1.17 g | ✅ | ✅ | ✅ |
| Ejection POC | LatchPinCollar ×2 | 0.55 g ea. | ✅ | ✅ | ✅ |
| Ejection POC | TubeStub | 33.30 g | ✅ | ✅ | bench fixture — not a flight part |
| Ejection POC | DummyNose | 21.81 g | ✅ | ✅ | bench fixture — not a flight part |
| Avbay cassette | SvcAnchorCoupler | 21.21 g | ✅ | ✅ | ⚠️ anchor bulkhead as an 18 mm coupler; §13 item 16, redesign target |
| Avbay cassette | SvcRetentionBand | 3.81 g | ✅ | ✅ | flush inward band, 3× M3; wall 1.9 mm flagged THIN |
| Avbay cassette | SvcAftClosure | 3.64 g | ✅ | ✅ | r19.0 + ⌀8 spigot + one clocking key |
| Avbay cassette | SvcBatteryTray | 1.41 g | ✅ | ✅ | thin U‑channel, inboard‑open, 0.6 mm lip; JST pigtail |
| Launch pad | PadHub | 85.13 g | ✅ | ✅ | ✅ ⌀4.2 × 63 through‑socket, 3 mortises, tie‑down — **ground support, not a flight part** |
| Launch pad | PadLeg ×3 | 24.83 g ea. | ✅ | ✅ | ✅ slot‑in outrigger, ⌀6.5 peg hole; prints flat |
| Launch pad | BlastDeflector | 118.29 g | ✅ | ✅ | ✅ ⌀120 disc + slotted 40 mm standoff ring — **the rocket rests on this** |

**Assembled view:** `Models/PhoenixABS40-43_aft_assembly_v1.FCStd` places the aft parts in
flight position with reference fins, a dummy motor and a forward tube stub; every pair reads
0.000 mm³ interference. `Models/render_aft_assembly.py` writes preview PNGs to
`Models/_render/` without needing the GUI. The fins there are **reference only** — the rev‑5
planform flattened to a 2 mm plate, not a printable part.

**Avbay cassette:** `Avionics/PhoenixABS40-43_avbay_cassette_v1.py` (+ `.FCStd`,
`avbay_cassette_build_report_v1.txt`) — the serviceable‑bay retention hardware of §13 item 16,
layered on the §8 packing envelope of `Avionics/avionics_bay_packing_40mm.md` (which has no `.py`
of its own). All report checks PASS bar the deliberate `OPEN` on the recovery‑snatch load path.

**Launch pad:** `Models/PhoenixABS40-43_launchpad_v1.py` (+ `.FCStd`, `launchpad_build_report_v1.txt`)
— **ground support equipment, built around the ⌀4.0 mm steel rod the user has**, not a flight part,
so it is outside the `.ork`. 3 unique parts, 5 printed pieces, no bought hardware, no supports.
The rocket rests **fins‑down on the deflector's standoff ring**: a stop collar clamped to the rod is
geometrically impossible, because the rod runs 25 mm off the body axis through an external lug and
152 mm of tube hangs below that lug at a constant 3.5 mm from the rod, in every clocking. All
geometric checks PASS. **Two checks FAIL on purpose and one is OPEN** — see §9's rail/lug item:

- **`[6]` rail length.** The pad's rest plane puts the lug 294 mm up, so guided travel = rod length
  − 294 mm. **A 1 m rod gives only 706 mm of guidance**, which drops §4.4's A8‑3 rail‑exit figure
  from 15.4 to ≈ 12.9 m/s — under §4.4's own 15 m/s floor. **Buy ≥ 1300 mm of rod (light) /
  ≥ 1500 mm (payload)**, then set rail length in the `.ork` and re‑run the §4.4 matrix.
- **`[5]` tip‑over.** The bare pad tips at **8.7 m/s**. Staking (⌀6.5 peg hole per foot) and/or 1 kg
  on the hub's ⌀7 tie‑down is the **primary** stability mechanism at a 10 m/s range limit, not an
  optional extra.
- **`[9]` lug bore, OPEN.** §2.2 specs the lug bore at ⌀5.0 for a 3/16 in (4.8 mm) rod; on this
  4.0 mm rod that is 0.50 mm of radial slop — 1.6° of tilt, ≈ 11 mm of pointing error at the nose.
  The lug is unmodeled, so there is nothing to fix in CAD yet. **Requirement when it is modeled:
  bore ⌀4.4** — or buy a 4.8 mm rod instead and leave the bore alone.

**Not modeled at all:** body tube forward of Z 51.4, nose cone, launch lug / rail standoff,
the e‑bay **sled itself** (only its bounding envelope and its retention hardware). The motor
mount, its sealed bulkhead, the fins and the **integrated fin‑can are
now modeled** (§9, cfg B/C) — so §13 item 10 has moved from "barely started" to "the aft end
is done, the forward airframe is not".

---

## 13. Open items & required actions

> **2026‑09‑30:** items that concern the spring/servo recovery (T5, latch, spring rate, nose breakaway) are closed by the
> D9aft v1 re‑architecture. Its own open items (rail exit ~11–15 m/s, descent 5.2 m/s, pin τ assumed, charge unknown,
> spent‑casing fit) are in `Models/AFT_DEPLOY_D9_DESIGN.md` §10. Item 3's OpenRocket re‑run has been done for the D9 on the D9aft masses.

Ordered by priority.

1. ⚠️ **Static stability — fin fix applied, not yet verified.** Rev 5 enlarged the fins to 55 mm
   semi‑span in the `.ork` (§4.5); computed margin ≈ +1.8 cal against ≈ +0.5 before, and ≥ +1.5 in
   every sensitivity case. **What remains is confirmation in OpenRocket** with corrected masses
   (item 2) and the §7 mass distribution, on a re‑run matrix (item 3) — ≥ 1.0 cal on every motor,
   ≥ 1.5 on B4‑4. **Still blocking: do not build until OpenRocket confirms it.**
2. **Correct the body‑tube material** in the `.ork` to solid ABS (or a measured override); expect
   ~+30 g and a further aft CG shift (§3).
3. **Simulate the flyable motors on the current airframe.** B4‑4, C6‑5 and C6‑7 have never been run
   on ⌀42 mm, and *nothing* has been run on ⌀43 mm (§6.1). Rebuild the whole matrix with
   corrected masses (§3) and the §7.11 mass distribution.
4. **Change the model's default motor** from Klima C6‑0 to C6‑5 or C6‑7; tag the 0‑delay motors
   "STAGING ONLY" (§5.1).
5. **Build and qualify the spring ejection system (§7).** In order: measure *F*max (§7.3) — this
   gates everything and takes five minutes; then nose detent (§7.4), latch (§7.5), sealed/vented
   motor mount (§7.6), then the seven qualification tests (§7.9).
   CAD status: the mechanism now exists as a bench POC (§7.5.2) and the retention hardware as a
   non‑assembling v1 (§9). **Not one of the seven tests is closed** — and *F*max, the five‑minute
   measurement that gates the rest, is still unmade.
6. ⊘ **Moot for this build — the motor is plugged, so there is no charge to vent.** §7.6's
   own last paragraph says as much. The aft section (§9 cfg B) therefore ships with an
   **unbroken** airframe wall and a bulkhead that seals rather than vents.
   **If the motor choice ever changes, this reopens immediately** and is mandatory before
   flight: a charged motor against a solid bulkhead with no vent path is §7.6's 433–866 N on
   a printed disc. The geometry is already solved — `VENTED = True` in the build script
   reinstates it, verified. Note the band is tighter than §7.6 assumed: the retainer seats the
   motor 14.1 mm further aft, leaving **9.1 mm** between engine block and bulkhead rather than
   20.2, which still takes 2 × ⌀5 mm with ~2 mm each end. Flow is still untested (§7.9 test 6).
7. **Add the e‑bay static port** and ground‑test the vented ejection charge in the printed
   airframe (§7.9 test 6, §8.6).
8. **Rail/lug:** two lugs or rail buttons; bore matched to the intended rod (§9). **Now gated by the
   pad (§12.1), which is built and exports clean.** Three things must close, in order:
   (a) **decide the rod** — bore the lug ⌀4.4 for the ⌀4.0 mm rod in hand, or buy a 4.8 mm rod and
   keep the ⌀5.0 bore. Nothing else about the lug can be modeled until this is settled;
   (b) **buy rod length off the *guided* figure, not the raw one** — on this pad guided travel is
   rod length − 294 mm, so ≥ 1300 mm (light) / ≥ 1500 mm (payload). A 1 m rod gives 706 mm;
   (c) **re-run the §4.4 motor matrix** with rail length set to that guided figure — §4.4's table
   was computed at 1.0 m and the A8‑3 case falls to ≈ 12.9 m/s at 706 mm, under its own 15 m/s
   floor. This is the `.ork` change §12 requires after any input change, and it is not yet done.
9. **Add a positive motor retainer** (§9). ✅ **v1 assembles and verifies clean** — thread fixed,
   0.000 % clash through a full unscrew sweep, STEP + STL exported. **What remains is physical:**
   measure a spent casing against the ⌀15.0 cap lip, then print and fit‑test cold. The
   0.2 mm/0.1 mm thread clearance is inherited from a pair printed at ⌀28 and has never been
   printed at ⌀38. Two interactions to settle: the engine‑block bore is **open ⌀14, not the
   sealed bulkhead §7.6 requires** (correct for a plugged motor, wrong for a charged one), and
   are resolved by the cfg B variant (`AftSectionSealed`): the bulkhead is solid, and with a
   plugged motor no vents are needed — see item 6 and `Models/AFT_RETENTION_DESIGN.md` §4A.
   **Decide which configuration you are building before printing; they are not interchangeable.**
10. **Populate `Models/` and `Print Files/`** with the fin‑can‑integrated part breakdown (§8–9).
    ⚠️ **Barely started.** 11 bodies exist, but they are recovery and retention hardware — the
    airframe, nose, fin‑can, motor mount and vent band are still unmodeled (§12.1).
11. **Grow the nose shoulder** to ⌀39.6–39.8 mm and ≥ 43 mm engagement (§7.4, §8.4, §9).
    — body wall ✅ done in rev 4 (§8.3).
12. **Confirm the 10 mm nose wall was intentional** (§3.1). It is worth ≈ 31 g of nose ballast; if
    it was a slip, §4's numbers change again.
13. Put the project under `git`.
14. ⚠️ **Propagate the CAD back into the `.ork` — before item 3.** §12 says the model leads and CAD
    follows; right now it is the other way round. Overall length **380.0 → 397.0 mm** (the retainer
    cap protrudes 17.0 mm aft) and **+18.89 g net at 378.5 mm** (23.89 g of new parts, less what
    they displace — enter whichever the model needs) exist only in CAD, as does the ⌀39.7 nose
    shoulder of item 11. Simulating item 3 without them re‑runs the wrong rocket.
15. **Bring the ejection mechanism's printed mass back inside §7.11.** As built the printed parts
    are 43.2 g against a 22 g allowance, the anchor bulkhead alone 25.3 g against 8 g (§7.5.2); the
    bench steel is a further ~22 g but is not flight hardware. The POC was never mass‑optimised, so
    this is a redesign target, not yet a budget line — but it is mass on a vehicle whose margin is
    already the open question in item 1.
16. **Serviceable avionics bay — architecture drafted, one load path unverified.** The user needs
    the e‑bay removable for same‑day multi‑flight (inspect, recharge / swap the battery). Drafted in
    `Avionics/avionics_bay_packing_40mm.md` §9 + `PhoenixABS40-43_avbay_cassette_v1.py` (4 parts,
    STEP + STL, build report; **all checks PASS except the deliberate `OPEN`**):
    - **Recharge / card / arm are already external** in the v2 pack (§5) — no disassembly. Only a
      *faster battery swap* or an inspection needs the bay open.
    - **The stack comes out as one cassette** — anchor bulkhead (reworked as an 18 mm coupler) +
      cage + knob + servo + sled + electronics — lifted out with the forward airframe section past
      a **bench‑service joint** at ~station 181. Servo‑to‑knob coupler never separates.
    - **Blocking decision:** the anchor bulkhead must be **mechanically captured (3 radial M3
      through a thickened band), not solvent‑welded** (§7.5). Those screws then also carry the
      recovery snatch — **`[R]` cannot pass until `F_max` is measured (§7.3) and a packed
      separation is dropped (§7.9 test 4).** The load that governs is the **ejection snatch**
      (~5.1 m/s separation arrested over the shock cord — a few hundred N), not canopy opening
      shock (~10–30 N); the script's 250 N stand‑in reflects that. The band wall (1.9 mm) is
      flagged THIN and can't grow inward because the sled must pass through it (0.20 mm — the
      same tightness item in `Avionics/…` §3/§7, fixed by a shorter FC board). If the snatch
      lands high, the **3‑lug bayonet** is the answer, not the fallback.
    - **Mass:** +30 g of printed additions, 21 g of it the coupler‑bulkhead — folds into item 15's
      redesign target, and into the item 3 re‑run once real.
    - **Length‑neutral:** the bulkhead grows 8 → 18 mm *aft into the e‑bay's ≥ 30 mm of slack*
      (§7.8), so overall length is unchanged. What is new geometry for the `.ork` (item 14): the
      transverse joint at ~181 mm and the flush retention band; both are internal.
    - **Load direction to nail down:** the assumed 100 → 250 N in the script is a stand‑in for the
      *ejection* snatch (the governing event), not canopy opening shock — see the constant's note.

---

*Prepared from `PhoenixABS40-43.ork` (OpenRocket 24.12). All simulation figures in this document
are from runs the model itself flags as `outdated`, **and all of them predate rev 4** — every
performance number must be regenerated once items 1–3 above are closed. Mass and volume figures
attributed to §3 and §7 are computed from the `.ork` geometry for this document, not read from
OpenRocket; check them against the component mass display after correcting the materials.*

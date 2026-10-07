# D9aft v6: 150 mm chute bay, longer e-bay (sled v6)

Delta note on top of `AFT_DEPLOY_D9_v5.md`.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v6.py`, ~2.5 min |
| **Report** | `…_D9aft_v6_report.txt`: **ALL PASS** |
| **Section** | `…_D9aft_v6_section.png` |
| **OpenRocket** | `aero_D9aft/verify_D9aft_v6_openrocket.txt`, model `PhoenixABS40-43_D9aft_v6.ork` |
| **Monte Carlo** | `aero_D9aft/MonteCarloD9.java` → `montecarlo_D9_v6.txt` / `.csv` |
| **Sled** | `Avionics/PhoenixABS40-43_avbay_sled_v6.py`, report `Avionics/avbay_sled_build_report_v6.txt` |

## What the user asked for (2026-10-06)

- The parachute bay should be **150 mm** (v5: 198.4).
- **The forward section is resized** to fit the longer sled v6 e‑bay. The piezo and vent holes line
  up with the new sled.
- **The aft bay holds the parachute only.**

## What changed

**Layout.** The body is **313.5 mm** (v5 340), so the bay is exactly 150.0.

| Station | v6 | v5 |
|---|---|---|
| −65 – 0 | nose v6 | same |
| 10.5 – 15.4 | EbayCap (springs + key) | same |
| 13.4 – 83.6 | **e‑bay: sled v6** | to 61.7 |
| 83.6 – 88.6 | seat ring → spigot; **bonded joint 88.6** | 66.7 |
| 102.1 – 104.6 | gas‑tight bulkhead + eyelet | 80.2 – 82.7 |
| **104.6 – 254.6** | **chute bay, 150.0 mm** | 82.7 – 281.1 (198.4) |
| 126.0 – 161.0 | launch lug, on the OD | 152.5 – 187.5 |
| 222.1 – 262.1 | coupler, pins at 250.1 | 248.6 – 288.6 |
| 262.1 – 313.5 | fin can v4, D9, cap | 288.6 – 340 |

**FwdTube v6: 104.6 mm** (v5 82.7). The seat, the joint and the bulkhead all moved 21.9 mm aft
with the e‑bay.
- The **sound port** moved from station 51.3 to **72.9**: d3, 0°, centred on the rotated piezo can.
  There is a 2.0 mm air path to the can face, and the piezo is the first thing behind the port.
- The **static port** is unchanged: d1.5, 0°, station 30.8.
- The **ARM mark** moved from −10.9° to **−8.7°**, because sled v6 moved the reed. It still spans
  stations 20–34, with the tick at 27, 1.95 mm from the static port.
- Thread, key groove and eyelet are v5.

**AftTube v6: 173.5 mm** (v2 221.9).
- **Parachute only.** It is a clean ⌀40 bore from the bulkhead to the fin can. The only holes in
  its wall are the 2 pin slots, and the launch lug is outside.
- The pin slots and the lug keep the same position relative to the aft end. The fin can, pins,
  coupons and cap fit unchanged.

**Unchanged:** nose v6; fin can v4 + fins; pins, coupons and cap (v1). The EbayCap is regenerated
from the sled top, which is the same as v5.

**How it is built.** v6 runs the v5 chain (v1 → v2 → v3 → v5) with in‑memory patches to v1. No earlier
file is edited.
- Sled v1 → v6.
- `BODY_LEN` 313.5.
- These are now measured from the aft end instead of the nose: `PIN_ST`, `LL_ST0/1`, `NOMEX_ST`.
- v1's own sled‑mount anchor (`SLED_Z`) is re‑anchored to the nose, as v1 had it.
- The sound port now sits at sled `PIEZO_ZC`.

## Checks

| Check | Result |
|---|---|
| Bay length | **150.00 mm** |
| E‑bay aft‑most point | station 83.6, forward of the joint (88.6) and the bulkhead (102.1) |
| Anything but recovery gear in the bay volume | none |
| AftTube wall | missing volume = the 2 pin slots exactly, so no port, vent or other hole |
| Ports | both in the FwdTube full wall; they match sled v6's proposal; real‑part probes 4/4 |
| Sound port → piezo | clear 2.0 mm path; axis 0.00 mm off the can centre |
| ARM / groove / thread probes | 7/7 |
| E‑bay interference, seat, negative control | pass |
| Full lift‑out sweep, 0–86 mm | no contact |
| Key, spring bumps, beams | pass |
| Flight interference, gas column, gas‑tight bulkhead, separation sweep, launch rod | pass |
| Pin slots | Zf 63.4 = fin can v4; ligaments 11.5 / 27.5 mm (same as v1) |
| Print | FwdTube 104.6, AftTube 173.5 mm tall; no wide overhangs |

## Mass and flight (CAD rollup)

| | v6 | v5 |
|---|---|---|
| Liftoff | **246.4 g**, CG 225.3 from the tip | 246.4 g, CG 235.9 |
| Margin, liftoff / burnout | **1.53 / 1.74 cal**: nominal, only 0.03 over the 1.5 gate | 1.78 / 2.02 |
| D9‑5 | ejects **at apogee, 0.7 m/s**, 212 m | 0.5 m/s, 211 m |
| Rail exit at 1.0 / 2.0 m guided | 12.0 / **15.3 m/s** | 15.3 at 2 m |
| Descent, ⌀500 | 4.84 m/s | 4.84 |

The e‑bay is now 60.7 g (sled v6 15.2 g, electronics 38.5 g, cap and screws). The electronics are
48 g less the SG90 (9 g) and the BQ25302 charger (2 g, deleted in sled v6), plus 1.5 g for the reed.

**The margin is thinner than v5's, and on paper it is marginal.** 0.03 cal is about 1.3 mm of CG,
which is less than the uncertainty in the unmeasured 13 g small‑parts allowance, the electronics CG
(weighted by envelope volume, not mass) and where the canopy sits.

**Monte Carlo** (`aero_D9aft/montecarlo_D9_v6.txt`): 500 flights each, on the same random draws.
Wind 0–8 m/s, 5–20 % turbulence, rod tilt up to 5°, mass/CG/print‑density scatter, fin cant,
delay 5 ± 0.5 s. Thrust is not varied.

| | v6 | v5 |
|---|---|---|
| Static margin at liftoff, p1 / p50 / p99 | 1.39 / 1.52 / 1.64 | 1.64 / 1.78 / 1.91 |
| **P(static margin under 1.5)** | **33 %** | 0 % |
| Lowest in‑flight margin, median / worst | 1.17 / 0.78 | 1.38 / 0.97 |
| P(in‑flight margin under 1.0) | 19 % | 0.6 % |
| … in wind 0–4 m/s | 0 % (worst 1.04) | 0 % |
| … in wind 4–6 m/s | 16 % | 0 % |
| … in wind 6–8 m/s | 61 % | 2.5 % |
| P(in‑flight margin under 0.5) | 0 % | 0 % |
| Apogee, median | 197 m | 196 m |
| Ejection speed, median (wind + delay) | 11.8 m/s | 11.7 m/s |

The Monte Carlo's mass‑scatter lever arms for the forward printed parts and the canopy still use v5
stations (for example, sled 7.2 g @ 40, against v6's 15.2 g @ 55). That only affects the scatter, so
it is second order.

### Balance check: the go/no‑go gate

With CP at **290.9 mm from the nose tip** (OpenRocket, M 0.1) and a 43 mm calibre:
- **1.5 cal** needs the CG at **226.4 mm from the tip or forward**;
- **1.0 cal** needs it at 247.9.

Balance the built rocket **with a loaded D9, the canopy, the shock cord and the Nomex packed**. If it
balances aft of ~226 mm, add ballast before flying.
- On the EbayCap top (~77 mm from the tip), each gram moves the CG ~0.6 mm forward (≈ 0.014 cal).
- **3–4 g there gives a real cushion** (≈ 1.58 cal nominal).
- Until then, **fly only in wind under ~4 m/s**.

## Recovery

- **Bay pressure is back to v1's** (150 mm, about 1.25× the v2–v5 pressure for the same charge). v2's
  "drop to the 0.5 mm neck if separation is weak" advice no longer applies: start on the nominal
  0.6 neck.
- **The Kevlar leader only needs to reach 158 mm** (v5 206), from the eyelet to the aft opening.
- **Check that the canopy, harness and Nomex pack into 150 × ⌀40 by hand before printing.** Space
  is tighter than v2–v5.

## Open

- Everything open in sled v6: reed module dimensions, small‑parts mass, the piezo can's position on its
  breakout, the ADXL thickness, the sled's print orientation and thin walls.
- From v1–v5: pin coupon test, spent‑D9 casing fit, thread fit test, charge strength.

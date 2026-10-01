# D9aft v5: electronics sled v4 (reed-switch arming)

Delta note on top of `AFT_DEPLOY_D9_v3_v4.md`.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v5.py`, ~80 s |
| **Report** | `…_D9aft_v5_report.txt`: **ALL PASS** |
| **OpenRocket** | `aero_D9aft/verify_D9aft_v5_openrocket.txt`, model `PhoenixABS40-43_D9aft_v5.ork` |
| **Sled** | `Avionics/PhoenixABS40-43_avbay_sled_v4.py`, report `Avionics/avbay_sled_build_report_v4.txt` |

## What changed

**Sled v1 → v4.** The sled is reused as built; nothing in it was edited. v4 has:
- the servo removed;
- the BMP388 moved away from the Nano (heat);
- an outboard‑open battery tray;
- a seat‑foot ring;
- a **KY‑021‑style reed module** for arming with an external magnet.

It keeps every interface D9aft reads: Zmin −0.9, the spine key, the M2 bosses, and the piezo at Zs
9.5 / 0°.

The earlier generators hard‑code sled v1. v5 swaps the sled in the v1 → v2 → v3 exec chain **in
memory only**; no earlier file is edited.

**EbayCap v5.** This is the v3 recipe (springs + key), with its pocket regenerated from sled v4's
top.

**FwdTube v5.** v3 plus an engraved **ARM mark** over the reed capsule.
- A 0.3 × 1.0 mm line at **−10.9°**, spanning **stations 20–34** (the capsule's length), with a
  6 mm cross tick at station 27 (the capsule's centre).
- The mark's position is derived from the sled's `RM_*` constants. If you measure the module and
  change them, re‑run v5 and the mark follows.
- A magnet on the mark sits **2.5 mm from the glass**.
- **Why a new mark:** the sled report says to place it "11° from the witness notch". v3 dropped
  that notch (the key does the clocking now), so the mark has to be on the tube itself.
- It is cut before the thread, 7.5 mm aft of the thread band. Probes confirm the thread and groove
  are intact, so the thread was not re‑sampled.

## Checks

| Check | Result |
|---|---|
| ARM / groove / thread probes on the real FwdTube | 8/8 |
| Mark vs capsule | same angle and length |
| Mark clear of the static port | 4.1 mm of arc |
| Mark clear of the thread band | yes |
| E‑bay interference (cap, sled, 9 envelopes, screws, tube) | none |
| Seat foot on the seat ring | contact only; negative control 197 mm³ |
| Lift‑out through the thread crests | 0.26 mm radial, no contact |
| Key blocks rotation | yes |
| Nose contact | only at the 3 bumps |
| Bottomed spring beams vs sled v4 | clear |
| Static port | clear |
| Sound port | 2.0 mm air path, then straight onto the piezo |
| EbayCap and sled v4 printing | no wide overhangs (sled aft end down) |

## Mass and flight

| | Value |
|---|---|
| E‑bay | **54.7 g @ station 37.0** (v3 53.7 @ 38.3): sled 7.2 g, electronics 39 g + reed 1.5 g, cap 6.3 g |
| Margin | **1.78 / 2.02 cal** |
| D9‑5 | ejects **at apogee, 0.5 m/s**, 211 m |
| Rail exit | 15.3 m/s at 2 m guided |
| Descent | 4.84 m/s |

## Open (from the sled report)

- Reed module dimensions are from a photo: measure it (`RM_*`), re‑run sled v4, then re‑run v5.
- Also measure: the ADXL thickness with its plug in, and the hole patterns.
- Wall thickness after the sled's clearance cuts is not auto‑checked: eyeball the thin walls.
- The small‑parts allowance (13 g) is unmeasured.

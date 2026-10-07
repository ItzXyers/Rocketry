# D9aft v10: sled v8 + the v9 snap latch, re-weighed

Delta note on top of `AFT_DEPLOY_D9_v8.md` (anchors) and `AFT_DEPLOY_D9_v9.md` (snap latch).

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v10.py` (execs v8 with sled v8 swapped in; v8, v7 and v6 are patched in memory, not edited), ~7 min |
| **Report** | `…_D9aft_v10_report.txt`: **ALL PASS** (V10 CHECKS at the end) |
| **Sled** | `Avionics/PhoenixABS40-43_avbay_sled_v8.py`, report `Avionics/avbay_sled_build_report_v8.txt` (0 FAIL, 1 WARN: file a flat on one M2 pan head) |

## What the user asked for (2026-10-07)

Build v10 = sled v8 + the v9 snap latch, with a fresh mass/CG and balance note.

## What changed

**Nothing new to print.** The flight set is:

| Part | Version | Notes |
|---|---|---|
| FwdTube | v8 | v10 rebuilds it on sled v8 and it comes out **identical** (0.000 mm³) |
| EbayCap | v6 | Identical (0.000 mm³) |
| Sled | v8 | |
| AftTube | v9 | Taken from the v9 STEP |
| Fin can | v9 | Taken from the v9 STEP |
| Pins | — | Gone |

v10 does not rebuild or export the AftTube or the fin can. The v9 STEPs enter the mass rollup as they are.
- **v10 exports only the FwdTube, EbayCap and sled.** Their STEPs and STLs are identical to the files in the print set.
- The first v10 run also wrote a `…_D9aft_v10_AftTube` STEP/STL. That was the inherited recipe's **pin-slot tube, not
  the v9 latch tube**. It is moved to `Print Files/_archive/D9aft v10 wrong AftTube export (…)`.
- The export is now skipped, and the report FAILs if a v10 AftTube file ever exists. **Print the AftTube from `…_D9aft_v9_AftTube.stl`.**

**Checks on sled v8.**
- The e-bay interference check covers 14 individual envelopes, and none of them clash.
- The piezo pin bay is empty.
- Both ports and the ARM mark line up.
- Lift-out works, and the seat contact passes its negative control.
- The v9 AftTube does not touch the FwdTube or anything in the e-bay.

## Mass and balance

| | v8 | v10 |
|---|---|---|
| Sled | 15.0 g | **12.6 g** |
| AftTube | 36.5 g (pin slots) | 36.1 g (v9 latch) |
| Pins | 0.04 g | — |
| Liftoff on D9 | 265.4 g | **262.6 g** |
| Liftoff CG, from the tip | 227.6 mm | **228.0 mm** |

The sled is lighter, and it sits forward of the CG, so the CG moves 0.4 mm aft.

**Balance gate: 226 mm from the tip.** The predicted CG is 2.0 mm past it, which takes **about 4 g of EbayCap ballast just
to reach the gate** (0.6 mm/g), plus a cushion. **This rests on the ASSUMED 18 g line** (12 g/m × 1.5 m):
- Every 1 g the real line differs moves the CG by about 0.15 mm.
- Weigh the line, then balance the built rocket with a loaded D9 and the bay packed.

## Report quirks (cosmetic)

- Some labels inherited from the v6/v7 recipe still say "sled v7" or "v7 vs v6". The V10 CHECKS block is the authority.
- The "port axis off the can centre" line uses the piezo envelope's bounding box, which includes the bent pins (as in v7).
  Sled v8's own report checks the real port axis.

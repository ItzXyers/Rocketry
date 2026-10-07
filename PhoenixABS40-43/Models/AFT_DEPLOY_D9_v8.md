# D9aft v8: anchors for a 5 mm retention line

Delta note on top of `AFT_DEPLOY_D9_v7.md`.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v8.py` (execs v7; patches v1 and v2 in memory as they are read), ~7 min |
| **Report** | `…_D9aft_v8_report.txt`: **ALL PASS** (V8 CHECKS + V8 vs v7) |

## What the user asked for (2026-10-07)

- "The retention line needs 5 mm in diameter."
- The line goes **through both anchors directly**, with no Kevlar leaders.

v7 could not take it. The eyelet tunnel was 3.5 × 5 mm. The fin-can lug had a ⌀3.5 hole with only 6 mm of radial room.

## What changed

**FwdTube: bulkhead eyelet** (v2 recipe, new constants).
- Every opening the line passes is **6.5 × 6.5 mm**: the two windows, the tunnel width and the tunnel height.
  That is the 5.0 mm line plus 1.5 mm.
- The bar is 7 × 3.5 mm (v7: 6 × 3). It bends 14.2 MPa at the 250 N placeholder.
- The boss is 24 × 10.5 × 13 mm. It still has a 3 mm roof and is still gas-tight. Its forward end is 8 mm aft of the e-bay.
- A ⌀5.3 swept line threads it (down a window, over the bar, out the other window) with 0 clash.
  Negative control: the same line clashes with the v7 FwdTube.
- Nothing else on the tube changed. The difference against v7 is confined to stations 91.6–104.6.

**Fin can: staple lug** (replaces v1's ⌀3.5 lug at 300°; v4 slotted can otherwise).
- A 9 mm-wide block stands on the thrust-ring face, from r 8.5 out to the coupler wall.
  It has a 6.5 × 6.5 tangential opening: the floor is the ring face and the roof is a 45° peak, so it prints with no support.
- The outer leg is the coupler wall in every layer.
- At 250 N: the top bar bends 15.0 MPa. The legs carry 6.0 / 5.6 MPa across the layers (limit 10).
- The d14 gas column is clear, and the 3 fins, the pins and the separation sweep are unchanged.
- Mass: +0.4 g.

**Unchanged:** AftTube, EbayCap, sled v7, nose, fins, pins, cap. They differ from the v7 STEPs by 0.000 mm³.

## Reprint

- `…_D9aft_v8_FwdTube.stl`
- `…_D9aft_v8_AftFinCanSlotted.stl`

The superseded v6 FwdTube and v4 fin can STLs are in `Print Files/_archive/Ready to Print - D9 v7 anchors (…)`.

## Open

- **Line mass is ASSUMED** at 12 g/m × 1.5 m = 18 g, packed aft of the canopy. With it, the predicted liftoff CG
  is **227.6 mm from the tip** (v7: 225.3), past the 226 gate. Expect **≈ 3 g more EbayCap ballast**.
  Weigh the line, then balance the built rocket.
- **Hot zone:** the staple sits beside the d14 port. A nylon or polyester line needs a Nomex sleeve at that end.
- **Packing:** 1.5 m of 5 mm line is ~29 cm³ of the 188 cm³ bay. Test-pack it with the canopy and Nomex.
- **Tie the line to the eyelet before bonding** the FwdTube into the AftTube. The eyelet cannot be reached afterwards.
- The pin and snap-latch question is unaffected; v8 still models the v1 pin slots.

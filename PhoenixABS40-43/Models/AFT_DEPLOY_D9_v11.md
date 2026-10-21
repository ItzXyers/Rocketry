# D9aft v11: snap latches precisely opposite + clocking key

Delta note on top of `AFT_DEPLOY_D9_v9.md`. It replaces only the AftTube and the fin can. Everything else stays as in v10: FwdTube, EbayCap, sled v8, nose, fins and cap.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v11.py`. It execs v9's text with asserted patches, reads v8's STEPs (read-only) and runs in about 20 s |
| **Report** | `…_D9aft_v11_report.txt`: **ALL PASS**. Rows above the V11 block keep v9's labels ("AftTube v9 …") but test the v11 parts |
| **Outputs** | `…_v11_AftTube.step/.stl` and `…_v11_AftFinCanSlotted.step/.stl` in `Print Files/Aft Deploy D9`, its `Ready to Print`, and `Print Files/Ready to Print/D9` |

## Why (2026-10-14)

The user asked for the latches to sit precisely opposite each other, for a more stable joint.

- v9 placed the latches 120° apart (60° and 180°). That made the joint pull unevenly and cocked the coupler toward one side.
- In v11 they sit at **60° and 240°**, exactly 180° apart.
- This is the same layout as the measured coupon (bumps at 0° and 180°, 873 g on the first pull).

## What changed

- **Latches.** The 180° tongue and window move to 240°. The 60° latch is identical to v9's.
- **Key.** The 120° spacing used to force a single clocking: with fins at 0/120/240 and the rod line at 300°, a can turned 180° puts a fin on the rod. Opposed latches would also click when turned 180°, so v11 adds a key:
  - **Tab** on the fin-can shoulder at **30°**, 7.0 mm wide (for twist and landing loads) and 5.23 mm tall. It sits at r 20.1–21.5, flush with the OD. The fin slots break the shoulder at 0/120/240, so the tab is placed between two fins.
  - **Notch** in the AftTube aft band, +0.2 mm wider on each side and 5.53 mm deep. That leaves 1.47 mm of the 7 mm band.
  - **Tab height** is derived from the geometry: the distance from the window's forward face to the bump's aft end, plus 1.0 mm. If the can is turned 180°, the tab rests on the tube face and holds the can 5.23 mm proud. At that stand-off every window is wholly aft of the bumps, so the latch cannot catch. This was swept from 4.93 to 5.73 mm: 0 mm³ overlap throughout.
- **Unchanged.**
  - The staple lug at 300°, including its 6.5 × 6.5 opening. Its symmetric difference against v8 is 0, so the v8 line-past-staple sweep still holds.
  - The gas port, the thrust ring, the bore and the launch lug.
- **Mass versus v9:** −0.010 g. The v10 CG (228.0 mm from the tip) and the stability margin stand. The coupler wall is solid at 0/120/240 from Zf 51.9 to 90.9, so the fin slots end at the shoulder and the 240° window cuts clean wall.
- **Printing** is the same as v9. The tab grows straight up on the shoulder (boss down), and the notch is open at the top of the tube (forward end down). Neither adds an overhang.

## Assembly

Pack, then push the fin can in. Turn it until the **tab drops into the notch**, then push until you hear **2 clicks**.

A gap of about 5 mm at the joint means the can is in the wrong clocking. **Do not fly** like that, and do not fly without the clicks.

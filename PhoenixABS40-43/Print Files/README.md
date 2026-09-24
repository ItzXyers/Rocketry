# Print Files — layout

Organised by subsystem. Each part's STL appears once per pipeline stage.

```
Print Files/
  Ejection System/                     servo-released spring ejection POC (bench article)
    *.stl                              raw per-part model STLs, as exported (un-oriented)
    Ready to Print/                    pre-oriented, dropped to Z=0 — slice these
      ..._Shaft_v1.stl                 laid AXIAL (layers along the length, ~2x in bending; sand round)
      ..._PistonHead_v1.stl            disc down; bridge/support the d11.5 spring pocket
      ..._CatchCollarHalf_v1.stl       PRINT x2 — the two halves are identical
    Print Plate/                       generated batch plate (parts incl. PistonHead + CatchCollarHalf x2 + pins)
      ..._ejection_poc_plate_v1.3mf/.stl
  Aft Motor Retention/                 screw-off motor retainer + fin-can configs
    ..._AftRetainerBase / _MotorRetainerCap / _FwdCenteringRing   cfg A (bonded insert, plugged motor)
    ..._AftSectionSealed / _Fin                                   cfg B (sealed aft section + bonded fins)
    ..._AftFinCan                                                 cfg C (one-piece fin can — recommended)
  Launch Pad/                          GROUND SUPPORT — tripod pad for the d4.0 mm steel rod
    *.stl                              raw per-part model STLs, as exported (un-oriented)
    Ready to Print/                    pre-oriented, dropped to Z=0 — slice these
      ..._PadHub_v1.stl                bore vertical; ream the d4.2 bore with a 4 mm bit
      ..._PadLeg_v1.stl                PRINT x3 — laid FLAT, layers across the width (in-plane bending)
      ..._BlastDeflector_v1.stl        disc down; arched windows are self-supporting
  Nosecone/                            v5 Von Kármán separating nose for the T5 airframe (Nosecone/NOSE_V5_AERO.md)
    ..._nose_VonKarman_v5.stl          raw, as modeled (tip at Z=0)
    Ready to Print/
      ..._nose_VonKarman_v5.stl        TIP UP, shoulder on the bed; 0.12–0.16 mm layers, no support
  _archive/                            superseded 2026-09-02 exports, kept for reference
```

## Notes

- `Ejection System/CatchCollar_v1.stl` (one-piece) is an **assembly reference only** — do not
  print it. A d9 ring cannot thread the d6.8 bulkhead bore; `CatchCollarHalf` x2 is the printable
  article. See `Models/EJECTION_POC_DESIGN.md` §6.14 / §11.
- `PistonShaft` is gone: it is now `PistonHead` + `Shaft`, solvent-welded at a socket
  (`EJECTION_POC_DESIGN.md` §6.15). `Shaft` prints axial and needs sanding round, or swap in a
  d6 CF rod (§10.2).
- `PistonShaftOnePiece_v1.stl` is the **old one-piece** head+shaft (no socket), emitted for a
  print-and-break comparison against the split pair — ~4 N shaft-up vs ~8 N split. Not the
  recommended part; not on the plate. Prints disc-down / shaft-up as a ~120 mm tower (brim, slow).
- `TubeStub` and `DummyNose` are **bench test fixtures**, not flight parts.
- **Launch Pad** is ground support — nothing on the vehicle, so it is outside the `.ork`. Its
  build report carries two DELIBERATE `FAIL`s and one `OPEN`, and **neither FAIL blocks printing**:
  they are operating conditions, not geometry. `[6]` says buy ≥ 1300 mm of rod (a 1 m rod gives
  only 706 mm of *guided* travel); `[5]` says peg the pad down or ballast it (bare, it tips at
  8.7 m/s); `[9]` says the ⌀5.0 lug bore is specced for a 4.8 mm rod, not this 4.0 mm one. Every
  geometric check passes. See `Models/launchpad_build_report_v1.txt` and DESIGN.md §12.1.
- The pad needs **no bought hardware**: 3 legs push into the hub on split-tenon interference fits,
  the deflector drops over the hub spigot, the rod drops through to the ground. Print `PadLeg` ×3.
- `TubeStub` and `Shaft` are printed **individually** (tall/long) — deliberately off the plate.

## ⚠️ The aft-retention scripts still write to the old flat layout

The **ejection** scripts were fixed 2026-09-08: `Models/PhoenixABS40-43_ejection_poc_v1.py` and
`Models/ejection_poc_test_pins.py` now export to `Print Files/Ejection System/…` and
`.../Print Plate/`.

Still on the pre-reorg flat paths: `Models/PhoenixABS40-43_aft_retention_v1.py` (writes to
`Print Files/` and `Print Files/Ready to Print/`) and `Models/verify_aft_retention.py` (reads
from `Print Files/`). Update their `PRINTS` / `RTP` constants (and the `AFT_RETENTION_DESIGN.md`
file map) before the next aft-retention build/verify run.

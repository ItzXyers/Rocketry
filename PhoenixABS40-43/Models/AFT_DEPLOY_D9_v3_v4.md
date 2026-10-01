# D9aft v3 + v4: printed e-bay springs + key, and a slotted fin can with separate fins

Delta note on top of `AFT_DEPLOY_D9_v2.md`. Both versions are **ALL PASS**.

| | v3 | v4 |
|---|---|---|
| Script | `PhoenixABS40-43_D9aft_v3.py` (~9 min): execs v2 with two in‑memory edits | `PhoenixABS40-43_D9aft_v4.py` (~2 min): execs v1 |
| Report | `…_D9aft_v3_report.txt` | `…_D9aft_v4_report.txt` |
| OpenRocket | not re‑run (the EbayCap changes by −0.1 g) | `aero_D9aft/verify_D9aft_v4_openrocket.txt`, `PhoenixABS40-43_D9aft_v4.ork` |

The print set is in `Print Files/Ready to Print/D9/`. Its README covers print order and fin bonding.

## v3: no foam ring

The foam's job was to stop the e‑bay moving: about 1 mm of axial rattle, plus free rotation. Two
printed features replace it.

### Rotation key (EbayCap rim, 180°)

The key rides an **axial groove in the FwdTube wall**, running from the mouth to 1 mm past the cap.
- The groove is cut only to the thread‑root radius (r 20.45), so the 1.05 mm skin is unchanged.
- It is cut before the thread, so it is a boolean on the plain part.
- It removes 2.4 % of the thread circumference.
- The e‑bay goes in **one way only**, with ±0.9° of play. v2's witness notch is gone.

### Three spring beams (EbayCap top, 0 / 120 / 240°)

Each is an arc beam fixed at both ends over a shallow pocket, with a bump at mid‑span. Fixed at both
ends, it prints as a bridge; a cantilever would print as a drooping overhang.

| | Value |
|---|---|
| Span | 18.5 mm |
| Section | 2.4 × 0.8 mm |
| Stiffness | 6.2 N/mm |
| Preload | the nose shoulder presses each bump 0.25 mm → **1.54 N each, 4.6 N total, 14 MPa** |
| Hold | the e‑bay stays down to ~8 g of forward deceleration |
| Travel above that | at most **0.35 mm**, then the beams bottom out (33 MPa, short‑time) |
| Old travel | 1.0 mm of free rattle |

### Checks

| Check | Result |
|---|---|
| Groove probes (real part) | 6/6 |
| Thread re‑check, seated | clash 0; fill 31 % (v2 32 %) |
| Negative control | 207 clashes |
| E‑bay lifts out (key in the groove) | no contact |
| Rotation ±1.9° | blocked |
| Nose contact | only at the 3 bumps (2.18 mm³ = the designed preload) |
| Bottomed beams vs the sled | clear |
| E‑bay interference | none |

v3's first run found the key re‑filling the sled's pocket over the spine; the fix is to re‑cut the
pocket after the key.

**ABS creep:** 14 MPa sustained will relax the preload over weeks. Unscrew the nose between flight
days, and reprint the cap if the bumps no longer bear.

## v4: fin can printed as parts

The one‑piece fin can (cfg C) did not print, so v4 goes back to **aft_retention_v1 cfg B**.
- It is the verified `AftSectionSealed` STEP, with 3 through‑the‑wall slots 2.3 wide. They cut the
  wall and both centring rings, stopping 0.3 mm off the motor tube.
- v1's `make_fincan()` adds the D9aft features: ⌀14 port + ledge, 40 mm slip coupler, pin slots,
  harness lug.
- The real part passes 23/23 probes, and its feature volume delta matches the proxy (+4793.1).

### Fins, printed flat, ×3

- Rev‑5 planform with a **new tab ending at r 10.8**: 0.4 mm epoxy gap to the motor tube, 0.15 mm
  per side in the slot.
- **`Fin_v1` would not have fitted.** Its tab ran to r 9.8, because it was sized to fuse into cfg C.
  The negative control confirms it: 62 mm³ of clash against the slotted can.

### Printing and function

- The slotted can needs **no supports**. Its only big overhangs are 3 annular bridges, motor tube to
  wall, 9.6 mm (as v1 cfg B).
- The fin prints flat with no overhangs.
- The fin slots open only into the annulus below the solid thrust ring, so **they are not a gas
  path into the chute bay**.
- The fillet epoxy seals them anyway.

### Mass and flight

| | Value |
|---|---|
| Aft section | 34.1 g slotted can + 16.0 g fins + ~2 g epoxy = **52.1 g** (+1.0 g vs one‑piece) |
| Margin | **1.76 / 2.00 cal** |
| D9‑5 | ejects at apogee, 0.6 m/s |
| Rail exit | 15.4 m/s at 2 m guided |
| Descent | 4.83 m/s |

## Open

- Fin alignment is set by the slots, but check squareness with a jig while the epoxy cures.
- Everything still open from v1/v2: pin coupon, spent‑D9 casing fit, thread fit test, charge
  strength.

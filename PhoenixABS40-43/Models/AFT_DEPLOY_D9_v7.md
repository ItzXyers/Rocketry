# D9aft v7: sled v7 (piezo mounted sideways)

Delta note on top of `AFT_DEPLOY_D9_v6.md`.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v7.py` (execs v6 with sled v7 swapped in, in memory), ~3 min |
| **Report** | `…_D9aft_v7_report.txt`: **ALL PASS** |
| **Sled** | `Avionics/PhoenixABS40-43_avbay_sled_v7.py`, report `Avionics/avbay_sled_build_report_v7.txt`: 0 FAIL |

## What the user asked for (2026-10-07)

- Drop the piezo standoffs, but keep the screws.
- The piezo is a KY-006 module. Its 3 pins come off one edge, in the board plane, and are bent and
  heat-shrunk. In v6 that edge sat on the deck floor, so there was no room for the pins.
  The user asked to mount the board **sideways** instead.
- Then: "adjust the e-bay etc. to match".

## What changed

**Sled v7, piezo only.**
- The board is turned 90° in its own plane: 19 mm around the tube, 15 mm along it.
- The can still faces the sound port, centred at y 0, Z −12.1.
- The holes are at the −y end, and the pins exit +y into an open **pin bay** (about 7 × 8 × 17 mm).
- The PCB back sits **flat** on the back plate. The solder joints get a 1.4 mm relief cut into the
  plate, and nothing stands proud into the pocket.
- 2 × M2 × 6 screws from the can side, with about 4.8 mm of thread.
- There is 2.0 mm free under the board (v6 had 0).
- The 45° mid-ring print web was dropped, and the under-tray east web was shortened.
- Sled mass 15.0 g (v6 15.2 g).

**Rocket: no change.** Sled v7 keeps every interface D9aft reads: seat plane Z −22.8, sound port
Z −12.1 at 0°, static port, EbayCap face, M2 bosses, spine key and reed (ARM mark). D9aft v7
rebuilds the FwdTube, AftTube and EbayCap from the v6 recipe on sled v7, and they are **identical**
to v6: the symmetric difference against the v6 STEPs is 0.000 mm³.
- **Already-printed v6 tubes and cap are the flight parts.** Print only sled v7.
- The liftoff mass and CG are the same as v6 (246.3 g, tip 225.3), and the OpenRocket body mass is
  0.1 g lighter. The v6 stability numbers and the 226 mm balance gate still apply.

**New checks (V7 CHECKS in the report).**
- The sled interfaces equal v6's.
- The pin bay is empty in the assembled e-bay (FwdTube, EbayCap, sled and every other envelope).
- The parts were compared against the v6 STEPs.

## Open (ASSUMED until measured: see sled report [N])

- Is the can centred along the 19 mm side (`PIEZO_CAN_OFF`)?
- Header size, pin length (6 mm assumed) and where the back-side joints sit.
- Which long edge has the d2.5 hole (aft assumed).

If the can turns out to be off-centre, the board shifts so the can stays on the port, and the
tubes still don't change.

**Report quirk.** The "port axis 3.00 mm off the can centre" line in the v6 recipe takes the centre of
the piezo envelope's bounding box, and that box now includes the pins. The can itself is on the
port axis: sled report [D9] probes the real FwdTube v6 port on the can axis.

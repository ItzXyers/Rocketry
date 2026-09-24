# Ejection System T5 v2: one big coil, e-bay terminals at the aft face

v2 changes **only the module base**. Everything else is identical to T5 (`README.md`), and the other
nine STLs are byte-identical. v1 files are untouched.

```
"C:\Users\dick_\AppData\Local\Programs\FreeCAD 1.1\bin\freecadcmd.exe" -c "exec(open(r'C:\Users\dick_\Documents\Rocketry\Ejection System T5\Models\spring_ejector_t5_v2.py').read())"
```

| Output | Where |
|---|---|
| Source of truth | `Models/spring_ejector_t5_v2.py` |
| Checks (**any FAIL = don't print**) | `Models/check_report_v2.txt` |
| Chamber plan view | `Models/section_chamber_plan_v2.png` |
| Print this | `Print Files/t5v2_base.stl` (same settings as `t5_base`) |

## 1. What changed and why

The v1 print had nowhere for the nichrome coil to go. The v1 model had never included a coil, so
its checks passed anyway. v2 models the coil and checks it.

* **One coil, on leg +1.** Leg −1 is only clamped. Cutting one leg releases the piston; the free end
  pays out 18.1 mm more than a full stroke needs.
* **Coil pocket.** The coil hangs in a 9.2 × 6.2 mm pocket, 2.8 mm deep in the chamber ceiling,
  with **≥ 2.0 mm of air to plastic all round** (2.10 mm measured). It sits on the straight run of
  line, 6.1 mm from the hole, so it carries no line load.
* **Nichrome terminals** (2 × M2 × 6) sit in the ceiling, one per coil end. They are opposite
  poles, so they are on **opposite sides of the line**:
  * **Terminal 1** is outboard of the hole end, at (9.7, −4.6), with a ~2 mm tail.
  * **Terminal 2** is inboard past the far end, at (−3.0, −8.5), below the M5 head. It has a ~5 mm
    tail that runs in its own air channel.
  * Bare metal of one pole is **4.45 mm** from the other, including a 0.5 mm allowance for splayed
    wire under the heads. The coil is ≥ 1.07 mm from both heads, so no turn can be shorted.
* **E-bay terminals** (2 × M2 × 8) screw into two pillars, and their heads are flush with the
  module's aft face (station 172). You fit the e-bay lead from the e-bay side *after* the module is
  screwed in, so nothing twists.
* **Copper jumpers** join each nichrome terminal to an e-bay terminal. Fitting or removing the
  e-bay lugs never loosens the nichrome.
* **Moved:** the leg +1 clamp to (1.2, −10.7) and the leg −1 clamp to (−9.2, −5.5).

## 2. Coil and hardware

| Item | Spec |
|---|---|
| Coil | Nichrome 80, 32 AWG. About 8 turns on a **1.0 mm mandrel** (a drill shank). The finished coil must fit **2.0 mm OD × 5 mm long**. Leave ~15 mm tails. |
| Nichrome terminals | 2 × M2 × 6 steel, into the ceiling beside the coil pocket. |
| E-bay terminals | 2 × M2 × 8 steel, into the pillars from the aft face. |
| Line clamps | 2 × M2 × 6 steel (unchanged). |
| Jumpers | 2 × stranded copper (e.g. 26 AWG silicone). **Terminal 1 → +x e-bay terminal** is ~15 mm. **Terminal 2 → −x e-bay terminal** is ~20 mm, laid along the −x wall. Strip ~4 mm at each end, twist it tight, and wrap it clockwise round the screw shank. Never route a jumper across the coil pocket. |
| E-bay lead | 2 wires ending in **M2 ring or fork lugs** (≤ 0.5 mm thick). Fork lugs let you fit them without taking the screw out. |

That makes 6 × M2 in total (v1 used 4).

## 3. Cocking: replaces step 3 of `README.md`

1. Screw the module into the stand, then push down and lock with the tool and pin (unchanged).
2. **Fit the jumpers first.** Wrap one end of each jumper under a nichrome terminal and the other
   under an e-bay terminal. Tighten the e-bay terminals now; leave the nichrome terminals loose.
3. **Tie the line.** Run the loop up one hole, through the piston tunnel, and down the other hole.
4. **Leg −1 (the short run on the −x side):** lay it straight to its clamp, wrap twice round the
   shank, and tighten.
5. **Leg +1 (the long diagonal run):** **slide the coil onto the free end first**, then lay the leg
   straight to its clamp, wrap, and tighten. Move the coil along the line into the middle of the
   pocket.
6. **Clamp the nichrome.**
   * Take the tail at the hole end outboard to terminal 1.
   * Take the tail at the far end inboard, along its channel, to terminal 2.
   * Put each tail *on top of* its jumper, so the nichrome sits between copper and the steel head,
     and clamp it on the solid-ceiling side of the head. Tighten.
   * Pull the tails just snug; they hold the coil centred in the pocket.
   * The coil must not touch the pocket walls or either terminal head.
   * Trim the tail ends short, so no stray end reaches the other pole.
7. Continue from step 4 of `README.md` (tether, transfer the load, pin checks).
8. **Continuity check** across the two e-bay terminal heads before you install the module.

## 4. Install: replaces step 6 of `README.md`

1. Unscrew the module from the stand. Screw it into the flight bulkhead with the tool, then insert
   the RBF pin and pack the canopy.
2. **From the e-bay side**, fit the lead's lugs under the two e-bay terminal heads at the aft face
   and tighten. Polarity doesn't matter.
3. Close the e-bay. Arm electrically at the pad, then pull the RBF pin last (unchanged).

**After a flight:** cut out the old line and coil, and wind a new coil. The jumpers and the e-bay
terminals stay in place.

## 5. Open items and notes

* **Burn current.** The new coil is longer (~8 turns), so bench-verify current and time again
  (`README.md` §4 test 4). Log them per coil.
* **M5 hex pocket.** The coil pocket opens one of the six flats of the M5 head pocket for 2.8 of
  its 3.7 mm depth. The other five flats still stop the head turning while it self-taps, and the CA
  fixes it after that.
* **Terminal bearing.** The nichrome terminal heads bear 71 % and 66 % on solid ceiling; the rest
  overhangs the pocket or channel. Clamp the nichrome on the solid side of the head.
* **Screw depth.** Every M2 pilot runs 0.5 mm past its screw tip. The M2 × 8 e-bay screws seat
  flush; don't substitute longer screws there.
* **The e-bay terminals sit at (±5.5, 7.2)**, 9 mm off the axis on the +y side. The pillars leave the
  chamber clear to r 6.25, so an 8 mm socket still reaches the M5 head.
* **`t5_integration.py` still runs the v1 script.** v2 defines a compatible `nichrome` (coil +
  tails), so pointing `T5_SRC` at `spring_ejector_t5_v2.py` should run. However, its lead-path check
  assumes a lead on the axis, and the e-bay terminals are now at (±5.5, 7.2). That check needs
  adapting before its PASS means anything for v2.

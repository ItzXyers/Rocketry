# Ejection System T5: spring piston with nichrome line release

This is the Phoenix 40/43 spring-piston ejection from `PhoenixABS40-43/DESIGN.md` §7, with the
servo/cam latch replaced by **a Dyneema line loop that a nichrome strand cuts**.

The spring, piston and release form one **module that screws into a bonded bulkhead ring from
the front**. It is the same 3-start T1 thread as T4 (about 1 turn to seat), so the T4 coupons fit.

```
"C:\Users\dick_\AppData\Local\Programs\FreeCAD 1.1\bin\freecadcmd.exe" -c "exec(open(r'C:\Users\dick_\Documents\Rocketry\Ejection System T5\Models\spring_ejector_t5.py').read())"
```

| Output | Where |
|---|---|
| Source of truth (parameters at top) | `Models/spring_ejector_t5.py` |
| FreeCAD document, STEP assembly | `Models/spring_ejector_t5.FCStd`, `Models/*.step` |
| Geometry checks (**any FAIL = don't print**) | `Models/check_report.txt` |
| Sections | `Models/section_cocked.png` |
| Print-ready STLs | `Print Files/t5_*.stl` |

## 1. How it works

```
 Phoenix station        module z
 106.5  ═════ RBF pin ═════   65.5  ◄ Ø4 hardened pin through the airframe, 1.5 mm above the piston
   110  ┌──── piston ────┐   62    ◄ Ø38.5 cup, 20 tall; flats at y = ±16 for the tool and harness
        │ ═══ line tunnel │         the line loop crosses the piston here
        │   │  spring  │  │         10 OD, 45 cocked / 85 free, on an M5×40 guide rod
        ║   │          │  ║   ◄ line legs at x = ±8 (2.75 mm clear of the coils)
   158  ├─flange (keys ±y)─┤   14
        │ T1 3-start thread│
   172  └── release chamber┘    0    ◄ open aft, facing the e-bay
 162–175.5 bulkhead ring (bonded)         nothing crosses the e-bay plane at 181
```

**The latch.** Each leg of the Dyneema loop comes down a base hole, lies against the chamber
ceiling, and runs **straight** to its own M2 clamp screw, where it wraps twice round the shank
before the head clamps it.

**The cut.** One nichrome strand spans between two M2 terminal screws and crosses both straight
runs. Wind it 2–3 turns round each leg where it crosses, giving two coils in series.
* The coils sit on straight line, so **the nichrome carries no line load**.
* The strand's heated span hangs over an air-gap trough and touches only the steel terminal heads,
  which clamp its ends.
* Cutting either leg releases the piston. If only one leg is cut, the free end still pays out
  16 mm more than a full stroke needs.

**Other features:**
* **Stroke stop.** A Kevlar tether runs from the piston to the chamber and goes taut at 41.5 mm.
  Nothing rigid sits in the canopy space or the e-bay.
* **Spring buckling.** The rod and the piston counterbore guide the spring over 40.5 of its
  45 mm cocked length.
* **RBF pin** (§7.5.1 item 2). A diametral pin through the airframe, 1.5 mm above the piston,
  blocks the piston however the module is clocked. The piston settles about 0.7 mm when the line
  takes the load, which still leaves 0.8 mm clear for the pin.
* **Harness.** It anchors in the ±y grooves of the bonded ring, so the printed thread never
  carries snatch load, and passes the piston at its ±y flats. The seated angle of the thread
  isn't controlled. Even 25° off, there is 2.35 mm radial room for a 1.5 mm Kevlar harness.
* **Removal from the front.** The tool face pushes the piston, and its prongs pass the piston
  flats into key notches in the flange.

## 2. Parts (PETG or ASA, not PLA)

| STL | Qty | Notes |
|---|---|---|
| `t5_base` | 1 | Exported flange-down, so the chamber opens upward and needs no support. ≥4 perimeters, 50 % infill. |
| `t5_piston` | 1 | Exported top-down. Run a Ø2 drill through the line tunnel after printing. |
| `t5_flight_bulkhead` | 1 | **Superseded by `t5i_fwd_section` (§6), which has this ring built in.** Only use this part to retrofit an existing tube. Bond into the airframe at **stations 162–175.5**. Screw the module in *before* the glue sets, and clock the ring so its ±y grooves sit under the piston flats. |
| `t5_test_stand` | 1 | Bench stand with an integral 40 ID bay tube. It has RBF holes (x) and lock-pin holes (y), and a nose fits its top for breakaway tests. You reach the chamber from the sides. |
| `t5_install_tool` | 1 | Handle-down. Has the lock-pin holes. |
| `t5_spacer_{2,4,8}mm` | 1 each | Go under the spring, for other springs. |
| `t5_coupon_T1_{male,female}` | 1 each | **Print first**: T1 fit. |

### Hardware

| Item | Spec |
|---|---|
| Guide rod | M5 × 40 hex bolt (DIN 933). The head sits in the hex pocket; it self-taps into the base; add CA. |
| Spring | As procured: 10 OD, 85 free, 45 cocked. Seats accept up to 11 OD. |
| Line | Ø0.3 mm Dyneema. **Use Ø0.4–0.5 if §7.3 measures F_max above ~40 N** (holes are Ø2). |
| Clamps / terminals | 4 × M2 × 6 steel screws. |
| Nichrome | Nichrome 80, ~32 AWG. Bench-verify the burn current. |
| Tether | Kevlar cord, ~50 lb. Knot in the piston top recess and in the chamber, taut at 41.5 mm of lift. |
| Pin | One Ø4 **hardened** dowel or silver steel, ~55 long, with a flag. It is both the RBF pin and the bench lock pin. |
| Leads | 2-pin JST-PH from the terminals, out through the ring centre. The e-bay needs ~150 mm of slack (bonded ring). For the integrated build, ~80 mm: see §6. |

## 3. Cocking and install

1. **Screw in.** Screw the module into the test stand.
2. **Push down and lock.** Push the install tool down until its prongs bottom in the flange
   notches. Slide the pin through the stand's **y** holes and the tool. The tool now holds the
   piston at the nominal cocked height, so the line carries nothing.
3. **Tie the line.** Working through the stand's side openings into the chamber:
   * Run the loop up one hole, through the piston tunnel, and down the other hole.
   * Lay each leg straight to its clamp. Wrap it twice round the shank, snug it by hand, and
     tighten.
   * Wind the nichrome 2–3 turns round each leg where it crosses, and clamp its ends under the
     terminal heads.
4. **Tether.** Knot it, taut at 41.5 mm of lift.
5. **Transfer the load.** Pull the pin and lift the tool. The line takes the load and the piston
   settles by less than 1 mm. Check that the pin still slides through the stand's **x** holes.
6. **Install in the rocket.** Unscrew the module from the stand; the piston stays cocked on the
   line.
   * *(Integrated airframe: use the order in §6 instead.)*
   * Plug in the lead from the e-bay.
   * Screw the module into the flight bulkhead with the tool.
   * **Insert the RBF pin**, then pack the canopy.
7. **At the pad.** Arm electrically, then pull the RBF pin last.

**After a flight.** Push the piston down with the tool, key it in, and unscrew. Cut out the old
line and re-cock.

## 4. Tests: this rig closes DESIGN §7.9 tests 1–3

1. **Spring force (§7.3), first.** Measure on a kitchen scale at 45 mm. The CAD is sized for the
   stiff case (52.7 N) until you have this number.
2. **Nose breakaway.** Fit the nose into the stand's tube and measure its release force (§7.4).
3. **Latch proof.** Mount the stand upside-down under a shelf and hang **3 × F_max** from a sling
   across the piston face. The spring already supplies the fourth 1×.
   * The line must not slip or creep, and the nichrome stays unpowered.
4. **Release.** Fire the nichrome with the pin out. Log current and time, and repeat ×10.

## 5. What CAD can't close

* **F_max (§7.3)** is unmeasured. It sets the line diameter, nose breakaway and proof load.
* **Nose retention (§7.4)** still needs a defined breakaway: a ball or magnetic detent.
* **Burn current and time**, and the avionics MOSFET channel.
* **Harness.** Its route is modelled. Confirm at first fit that it passes the flat without
  rubbing.
* **Stack length.** From bulkhead bottom to piston top is **65.5 mm vs the 61 mm in §7.8**
  (+4.5 mm). The piston top stays at station 110; the ring ends at 175.5, still clear of 181.
* **Mass.** About 11 + 13 + 7 g printed (solid), plus ~17 g of hardware, is **~48 g**. That
  compares with ~57 g in §7.11 (spring, piston/shaft/latch, servo, anchor bulkhead).

## 6. Integrated airframe: chute bay + T5 + e-bay

`Models/t5_integration.py` turns the airframe from the nose shoulder down to the fin can into
**three printed parts, flush at 43 OD**. It reuses these unchanged:
* the T5 module (imported from `spring_ejector_t5.py`; set env `T5_SRC` to build against `_v2`, whose outer interface is identical);
* the e-bay `ElectronicsSled` v1 (`PhoenixABS40-43/Avionics/…_avbay_sled_v1.py`);
* `AftFinCan_v1` (reference only).

Checks go to `Models/t5_integration_report.txt` (**any FAIL = don't print**; currently ALL PASS).
There is also a section view (`t5_integration_section.png`) and a STEP assembly.

```
 station   0 ┬ nose shoulder (plain 40 bore; nose + detent not part of this, DESIGN 7.4)
          20 │ canopy + Nomex                                   ┐
       106.5 │ RBF pin holes (x)                                │ t5i_fwd_section
         110 │ T5 module (piston … base)                        │ (print nose-end down, 199 tall)
     162–175 │ T5 ring, INTEGRAL (T1 thread, harness grooves ±y)│
         181 ┼═ flush joint ═══════════════════════════════════ ┘┐
     181–199 │ spigot inside the e-bay screw band; 3×M3 CSK @190  │ t5i_ebay_section
     185–204 │ t5i_sled_mount (lugs + disc)                       │ (print aft-end down, 107.6 tall)
     204–250 │ ElectronicsSled v1  (static port 219.3, sound 239.8, both +x)
     250–281 │ free: lead slack, battery pigtail                  │
  281–288.6  │ fin-can lip, bonded inside the e-bay section       ┘
```

| STL (`Print Files/Integrated/`) | Notes |
|---|---|
| `t5i_fwd_section` | 57 g PETG solid. Replaces the bonded ring, so the ring's clocking to the RBF holes is fixed by the print. Print **nose-end down**; the thread flanks sit about 38–41° from horizontal, like the coupon. Print the T1 coupon first. |
| `t5i_ebay_section` | 27.5 g. Slides over the fin-can lip (0.3 mm diametral epoxy gap) and bonds there. Put the ports in a fin gap when you bond it. |
| `t5i_sled_mount` | 7.9 g. Print disc down. Fix it to the sled with 2 × M2×10 pan heads into the **unused SG90 ear bosses**. T5 has no servo, so the servo pocket is now free space for the MOSFET and wiring. |

**Joint hardware:** 3 × M3×8 countersunk (DIN 7991). Each screw passes through the e-bay band and the
spigot, then self-taps into a sled-mount lug, so one set of screws holds all three parts. The
holes are spaced 90/225/330°, so they only line up in one orientation, and that orientation is
what clocks the sled to its wall ports. The heads sit flush, at r 21.50.

**Assembly order (integrated build):**
1. With the sections apart, screw the cocked module into `t5i_fwd_section` from the nose end with
   the install tool (§3 steps 1–5 unchanged). Insert the RBF pin.
2. Screw the sled mount onto the sled (2 × M2).
3. Plug the T5 JST (it exits aft of the ring) into the sled. Use ~80 mm of lead, and stow the slack
   in the spigot cavity (stations 178–199) or the empty servo pocket. The lead doesn't twist,
   because the module is already seated.
4. Stand the forward section **nose-down** and set the sled mount's lugs into the spigot, with the
   disc resting on the spigot end. Slide the e-bay tube down over the sled. Rotate the sled and
   the tube until the uneven screw pattern lines up through band, spigot and lug, then fit the
   3 × M3.

**Service** is the same in reverse: remove the screws, lift the e-bay tube off, unplug the lead, and
unscrew the module. For a battery swap or a look inside, you don't need to touch the module.

**Printing:** slice with elephant's-foot compensation on. Both sections also have a 0.5 mm × 45°
lead-in on the bed-side ID, which keeps the fin-can lip and nose-shoulder fits true.

**Open / tight (see report):**
* **Joint retention is OPEN.** The harness anchors in the forward section, so these 3 M3s carry the whole aft stack under ejection snatch. At the 250 N placeholder, bearing is ~15 MPa against ~40 MPa. A real number needs §7.3 F_max and §7.9 test 4.
* **Sled to band clearance is 0.31 mm radial.** It is tight, like cassette v1, and needs a round print.
* **Nose shoulder / detent** (DESIGN §7.4, §9 ≥ 42 mm shoulder) and the **microSD slot** position are not modelled.
* **Sled print orientation** is still open (sled report).
* **Sled support:** the sled now hangs from 2 × M2 in its ex-servo ear bosses, with its aft end free. Pull-test it; add a foam pad aft if it rattles.
* **Baro air:** the e-bay shares air with the chute bay through the harness grooves, and the chute bay vents through the RBF holes. The baro therefore mostly reads the pressure at station 106.5. That is accepted; seal the disc edge with foam tape if you want it isolated.

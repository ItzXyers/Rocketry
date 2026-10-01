# Ejection System T5 v3: 15.5 OD spring, one continuous line, knotted

v3 changes the **base and the piston**. It builds on v2 (`README_v2.md`): one coil, e-bay terminals
flush with the aft face, and copper jumpers. v1 and v2 files are untouched.

```
"C:\Users\dick_\AppData\Local\Programs\FreeCAD 1.1\bin\freecadcmd.exe" -c "exec(open(r'C:\Users\dick_\Documents\Rocketry\Ejection System T5\Models\spring_ejector_t5_v3.py').read())"
```

| Output | Where |
|---|---|
| Source of truth | `Models/spring_ejector_t5_v3.py` |
| Checks (**any FAIL = don't print**; currently ALL PASS) | `Models/check_report_v3.txt` |
| Sections / chamber plan | `Models/section_cocked_v3.png`, `Models/section_chamber_plan_v3.png` |
| Print | `Print Files/t5v3_*.stl`. Reprint **base and piston**. |

## What changed

* **Spring 15.5 OD.** The base and the piston each have a **Ø16.5 × 3 mm spring pocket**, so they
  take springs up to 16 OD. The base pocket leaves a 1.3 mm floor over the M5 head pocket. It is
  1 mm deeper than v2's seat, so the module sits 1 mm further forward: aft face at station 171. The CAD still assumes **85 free / 45 cocked**. Measure the new spring and
  update `SPRING_FREE` / `SPRING_COCKED`.
* **Line holes Ø3.0**, moved out to **x = ±11.5**. v2 had Ø2 at ±8.
  * Even with the line hard against the inboard edge of a hole, it is 2.25 mm from a 15.5 spring.
  * The plastic web between each hole and its spring seat is 1.15 mm.
* **All four holes go straight through**, two in the base and two in the piston. A **1.5 mm deep
  groove** across the piston face joins the two piston holes. The line lies 1 mm below the face,
  so the RBF pin and the tool face never bear on it.
* **The M2 line clamps are gone.** The two ends knot together in the chamber, at about (0, −11.5).
* **The chamber is re-laid out** round the new holes:
  * **Coil** on run +1, 5.8 mm from its hole.
  * **Nichrome terminal 1** is *inboard* of the coil's hole end, at (6.6, 0.7). The chamber wall
    leaves no room outboard there.
  * **Nichrome terminal 2** is *outboard* past the far end, at (6.2, −9.6).
  * Each tail gets its own air channel.
  * The poles are 4.2 mm apart. The coil has 2.1 mm of air to plastic and ≥ 1.07 mm to steel.
* The chamber radius grows from 13.0 to 13.7, which leaves 2.1 mm of wall to the thread root.

## Threading and tying: replaces v2 §3 steps 3–6

1. Start with the module screwed into the stand and the tool locked by the pin (unchanged).
2. **Thread one continuous line:**
   * up base hole +x and on up through piston hole +x;
   * across the face groove;
   * down piston hole −x and on down through base hole −x.

   Ø3 holes take a needle-threader or a stiff wire leader.
3. **Slide the coil onto the +x end** (the end in base hole +x) before you tie.
4. Pull both ends snug along the ceiling to the knot point, below the M5 head on the −y side.
   **Tie the two ends together** with a double fisherman's (or a surgeon's knot plus a drop of CA).
   Trim the tails to about 3 mm.
5. Move the coil along the straight +x run into the middle of its pocket. Clamp its tails:
   * the hole-end tail goes inboard to terminal 1;
   * the far-end tail goes outboard to terminal 2.

   Fit the jumpers as in v2.
6. Continue from v2 §3 step 7.

## Open items

* **Line strength.** The knot keeps only about 50 % of the line's strength. At 4× proof, each leg
  carries 105 N, so the line needs a break strength of **≥ 211 N (21 kg)**. Use 0.4–0.5 mm
  Dyneema, not 0.3.
* **Spring guidance.** The M5 rod no longer guides the spring, because a 15.5 OD spring's ID is far
  larger than 5 mm; only the seats capture the ends.
  * Free L/D is 5.5 and cocked L/D is 2.9.
  * Watch for bowing on the bench. If it bows, the fix is a printed guide sleeve over the rod.
* **Spring force / length** are unmeasured for this spring, so run README §4 test 1 again.
* **Terminal bearing.** The terminal heads bear 62 % and 64 % on solid ceiling. Clamp the nichrome
  on the solid side.
* `t5_integration.py` still builds against v1. The outer interface is unchanged, but the piston now
  has a groove on its face.

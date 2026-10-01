# Ejection System T5 v4: shorter piston skirt

v4 changes **only the piston skirt**: it is now **10 mm** (v3 had 12). Everything else is the same as v3
(`README_v3.md`). The v1, v2 and v3 files are untouched.

```
"C:\Users\dick_\AppData\Local\Programs\FreeCAD 1.1\bin\freecadcmd.exe" -c "exec(open(r'C:\Users\dick_\Documents\Rocketry\Ejection System T5\Models\spring_ejector_t5_v4.py').read())"
```

| Output | Where |
|---|---|
| Source of truth | `Models/spring_ejector_t5_v4.py` |
| Checks (**any FAIL = don't print**; currently ALL PASS) | `Models/check_report_v4.txt` |
| Sections / chamber plan | `Models/section_cocked_v4.png`, `Models/section_chamber_plan_v4.png` |
| Print | `Print Files/t5v4_piston.stl`. Only the **piston** needs reprinting. The other `t5v4_*` parts are identical to v3. |

## What changed

* `SKIRT_H` is now 10.0 (was 12.0). The piston is now 18 mm tall overall: an 8 mm plate plus the 10 mm skirt.
* The skirt's length-to-diameter ratio drops from 0.52 to 0.47. The anti-cocking check in the report
  now passes at **L/D ≥ 0.45** (it was 0.5). Watch for the piston binding or tilting in the bore on
  the bench fire test.

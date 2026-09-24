# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- FULL VEHICLE assembly with the T5 v2 ejector, v2: ALL ABS + e-bay compressed.

v2 vs v1: every printed part is ABS (rho 1.05; v1 had the T5/integration parts as PETG), and the empty
e-bay slack (sled aft end -> fin-can bulkhead, 30.9 mm in v1) is cut by DL_EBAY. The fin can, cap and
motor move forward by DL_EBAY and ebay_section is that much shorter; nothing else moves.

Stacks, in flight position (cocked, RBF pin pulled):
  nose        Nosecone v5 (Von Karman) STEP                        ABS
  fwd_section / ebay_section / sled_mount / joint screws            ABS   (t5_integration.py geometry)
  T5 v2       base, piston (cocked), M5 guide rod                   ABS / steel 
  e-bay       ElectronicsSled v1 (servo removed, as in t5_integration)
  aft         AftFinCan v1 (cfg C, fins printed in) + MotorRetainerCap v1   ABS
  motor       C6 stand-in 18 x 70 (geometry only; mass from the BoM line)

Nothing here is re-designed and no original script is modified: the T5 integration geometry is
exec'd from t5_integration.py up to its CHECKS banner (so none of its outputs are rewritten), with
T5_SRC pointed at spring_ejector_t5_v2.py.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"

Frame: the T5 module frame (+Z toward the nose, z = 0 at the module's aft face).
  Station (mm from the top of the body tube / nose base) = 172 - z.  From nose tip = station + 65.
Masses are SOLID-geometry x density (upper bound: the T5 base prints at 50 % infill), plus BoM
point masses for things that are not modelled as real solids.
"""
import os, math, time
import FreeCAD as App
import Part

V = App.Vector
ROCKETRY = r"C:\Users\dick_\Documents\Rocketry"
T5_ROOT = os.path.join(ROCKETRY, "Ejection System T5")
PHX = os.path.join(ROCKETRY, "PhoenixABS40-43")
OUT = os.path.join(PHX, "Models")
NAME = "PhoenixABS40-43_full_assembly_T5v2_v2"
DL_EBAY = float(os.environ.get("DL_EBAY", "25.0"))   # mm removed from the e-bay slack (v1 gap 30.9 -> 5.9)
NOSE_STEP = os.path.join(PHX, "Nosecone", "Models", "PhoenixABS40-43_nose_VonKarman_v5.step")
CAP_STEP = os.path.join(PHX, "Models", "PhoenixABS40-43_MotorRetainerCap_v1.step")
NOSE_LEN = 65.0                    # nose v5: Z 0 at tip, station = Z - 65
FINCAN_DZ = -168.0 + DL_EBAY       # fin-can frame Zf -> z (shifted forward)
MOTOR_ZF = (-14.1, 55.9)           # aft_assembly_v1 DummyMotor
MOTOR_R = 9.0

RHO = dict(PETG=1.27e-3, ABS=1.05e-3, steel=7.85e-3)   # g/mm3

t0 = time.time()
# ---------------- T5 integration geometry (PARTS only; stops at its CHECKS banner)
os.environ["T5_SRC"] = os.path.join(T5_ROOT, "Models", "spring_ejector_t5_v2.py")
_src = open(os.path.join(T5_ROOT, "Models", "t5_integration.py"), encoding="utf-8").read()
_cut = _src.index("\n# CHECKS\n")
_cut = _src.rfind("# ====", 0, _cut)
T = {"__name__": "t5i"}
_geo = _src[:_cut]
for a, b in (("ST_FINCAN_SHOULDER = 340.0 - 51.4", "ST_FINCAN_SHOULDER = 340.0 - DL_EBAY - 51.4"),
             ("ST_FINCAN_BULKHEAD = 340.0 - 58.9", "ST_FINCAN_BULKHEAD = 340.0 - DL_EBAY - 58.9"),
             ("fincan.translate(V(0, 0, -168.0))", "fincan.translate(V(0, 0, -168.0 + DL_EBAY))")):
    assert _geo.count(a) == 1, a
    _geo = _geo.replace(a, b)            # in-memory only: t5_integration.py on disk is untouched
T["DL_EBAY"] = DL_EBAY
exec(_geo, T)
for k in ("N", "HW", "P", "piston_c", "rod", "sled", "fincan", "ENV", "spring_env", "Z_PU_C", "heads", "nichrome"):
    assert k in T, "t5_integration exec did not define %s" % k
N, HW, P = T['N'], T['HW'], T['P']
print("T5 integration geometry in %.1f s" % (time.time() - t0))

def station(z): return 172.0 - z

# ---------------- nose v5: flip (180 deg about X keeps the anchor dowel on +/-y) and place
nose = Part.Shape(); nose.read(NOSE_STEP)
nose.rotate(V(0, 0, 0), V(1, 0, 0), 180.0)
nose.translate(V(0, 0, 172.0 + NOSE_LEN))            # Z = 0 (tip) -> station -65
cap = Part.Shape(); cap.read(CAP_STEP); cap.translate(V(0, 0, FINCAN_DZ))
motor = Part.makeCylinder(MOTOR_R, MOTOR_ZF[1] - MOTOR_ZF[0], V(0, 0, MOTOR_ZF[0] + FINCAN_DZ))
spring = T['spring_env'](T['Z_PU_C'])
e_env = Part.makeCompound(list(T['ENV'].values()))
heads = Part.makeCompound(list(T['heads'].values()))

def cg_z(shape):
    shs = shape.Solids if shape.Solids else [shape]
    vol = sum(s.Volume for s in shs)
    return sum(s.Volume * s.CenterOfMass.z for s in shs) / vol

# ---------------- mass items: (name, group, mass g, z of CG, basis, shape for the assembly or None)
items = []
def solid(name, group, shape, mat, note=""):
    items.append((name, group, shape.Volume * RHO[mat], cg_z(shape), "CAD x %s %.2f%s" % (mat, RHO[mat] * 1e3, note), shape))
def point(name, group, m, z, basis, shape=None):
    items.append((name, group, m, z, basis, shape))

solid("Nose cone v5 (Von Karman)", "nose", nose, "ABS")
point("Nose anchor dowel d4 x 38.5 (hardened)", "nose", RHO['steel'] * math.pi * 2 ** 2 * 38.5, 172.0 + NOSE_LEN - 100.0, "calc; nose report: anchor bosses from Z 95")
solid("fwd_section (chute bay + T5 ring)", "airframe", N['fwd_section'], "ABS")
solid("ebay_section", "airframe", N['ebay_section'], "ABS")
solid("sled_mount", "e-bay", N['sled_mount'], "ABS")
for k, s in HW.items():
    solid("HW %s" % k, "airframe" if k.startswith("M3") else "e-bay", s, "steel")
solid("T5 v2 base", "T5 ejector", P['base'], "ABS", " (prints 50 % infill: upper bound)")
solid("T5 piston (cocked)", "T5 ejector", T['piston_c'], "ABS")
solid("T5 M5x40 guide rod", "T5 ejector", T['rod'], "steel")
point("T5 spring 10 OD x 85 free (cocked)", "T5 ejector", 9.0, cg_z(spring), "T5 check report ~9 g", spring)
point("T5 6 x M2 screws", "T5 ejector", 1.5, cg_z(heads), "T5 check report ~1.5 g")
point("T5 line + nichrome + jumpers + Kevlar tether", "T5 ejector", 1.5, 8.0, "estimate")
solid("ElectronicsSled v1", "e-bay", T['sled'], "ABS")
point("Electronics, Opt B 620 mAh, no servo", "e-bay", 48.0 - 9.0, cg_z(e_env), "avbay packing md 6 (48 g less SG90 9 g); CG = component envelopes", e_env)
point("Canopy d500 + harness + leader", "recovery", 16.0, 172.0 - 76.0, "DESIGN 3.2 / 7.7; packed in bay st 42-110")
solid("AftFinCan v1 (cfg C, fins in)", "aft", T['fincan'], "ABS")
solid("MotorRetainerCap v1", "aft", cap, "ABS")
Z_MOTOR = (MOTOR_ZF[0] + MOTOR_ZF[1]) / 2 + FINCAN_DZ
MOTOR_LOADED, MOTOR_SPENT = 24.0, 12.0

# ---------------- report
rep_lines = []
def rep(s=""): print(s); rep_lines.append(s)
def tot(sel):
    m = sum(i[2] for i in sel); return m, (sum(i[2] * i[3] for i in sel) / m if m else 0.0)
def fmt_cg(z): return "st %6.1f  (tip %6.1f)" % (station(z), station(z) + NOSE_LEN)

rep("== Phoenix ABS 40-43 + T5 v2 -- full vehicle assembly v2 (all ABS, e-bay -%.1f mm), mass & CG ==" % DL_EBAY)
rep("Frame: station = 172 - z (0 = nose base / top of airframe); 'tip' = mm from the nose tip (= station + 65).")
rep("Printed parts are SOLID geometry x density -> an upper bound on print mass.")
rep("")
rep("STACK (station ranges, from geometry)")
for nm, s in (("nose v5", nose), ("fwd_section", N['fwd_section']), ("T5 v2 base", P['base']), ("T5 piston (cocked)", T['piston_c']),
              ("ebay_section", N['ebay_section']), ("sled", T['sled']), ("AftFinCan", T['fincan']), ("MotorRetainerCap", cap), ("C6 motor", motor)):
    bb = s.BoundBox
    rep("  %-20s st %7.1f .. %7.1f" % (nm, station(bb.ZMax), station(bb.ZMin)))
bb_all = Part.makeCompound([nose, N['fwd_section'], N['ebay_section'], T['fincan'], cap]).BoundBox
rep("  overall length tip -> cap: %.1f mm; max span (fins) %.1f mm" % (bb_all.ZLength, max(bb_all.XLength, bb_all.YLength)))
rep("")
rep("  e-bay slack sled aft end -> fin-can bulkhead: %.1f mm (v1 30.9)" % (station(T['fincan'].BoundBox.ZMax) - station(T['sled'].BoundBox.ZMin)))
rep("  sled aft end -> motor forward end: %.1f mm" % (station(motor.BoundBox.ZMax) - station(T['sled'].BoundBox.ZMin)))
rep("  body tube length (nose base -> fin-can aft end, OpenRocket 'body'): %.1f mm (v1 340.0)" % (340.0 - DL_EBAY))
rep("")
rep("QUICK FIT CHECKS (flight, cocked, RBF pin pulled)")
for a, sa, b, sb in (("nose", nose, "fwd_section", N['fwd_section']), ("nose", nose, "T5 piston", T['piston_c']),
                     ("AftFinCan", T['fincan'], "ebay_section", N['ebay_section']), ("MotorRetainerCap", cap, "AftFinCan", T['fincan']),
                     ("C6 motor", motor, "AftFinCan", T['fincan']),
                     ("sled", T['sled'], "AftFinCan", T['fincan']), ("electronics", e_env, "AftFinCan", T['fincan'])):
    v = sa.common(sb).Volume
    rep("  %s %-16s x %-14s overlap %.3f mm3" % ("ok  " if v < 1.0 else "WARN", a, b, v))
rep("")
rep("%-46s %-11s %8s  %-28s %s" % ("ITEM", "GROUP", "MASS g", "CG", "BASIS"))
for nm, g, m, z, basis, _ in items:
    rep("%-46s %-11s %8.1f  %-28s %s" % (nm, g, m, fmt_cg(z), basis))
rep("%-46s %-11s %8.1f  %-28s %s" % ("C6 motor (loaded; ~12 g spent)", "motor", MOTOR_LOADED, fmt_cg(Z_MOTOR), "DESIGN 3.2"))
rep("")
rep("BY GROUP")
for g in ("nose", "airframe", "T5 ejector", "e-bay", "recovery", "aft"):
    m, z = tot([i for i in items if i[1] == g])
    rep("  %-11s %7.1f g   CG %s" % (g, m, fmt_cg(z)))
rep("")
dry_m, dry_z = tot(items)
nn_m, nn_z = tot([i for i in items if i[1] != "nose"])
mot = [("motor", "motor", MOTOR_LOADED, Z_MOTOR, "", None)]
lo_m, lo_z = tot(items + mot)
la_m, la_z = tot(items + [("motor", "motor", MOTOR_SPENT, Z_MOTOR, "", None)])
rep("TOTALS")
rep("  Dry, flight-ready (no motor)   %7.1f g   CG %s" % (dry_m, fmt_cg(dry_z)))
rep("    of which non-nose           %7.1f g   CG %s   (NOSE_V5_AERO assumed 245 g @ st 192.7)" % (nn_m, fmt_cg(nn_z)))
rep("  Liftoff on C6 (24 g)          %7.1f g   CG %s   (NOSE_V5_AERO: 308 g)" % (lo_m, fmt_cg(lo_z)))
rep("  Landing (spent casing ~12 g)  %7.1f g   CG %s" % (la_m, fmt_cg(la_z)))
CP_TIP = float(os.environ.get("CP_TIP", "310.0"))   # mm from tip; set from the OpenRocket re-run
rep("  (v1 CP %.0f mm from tip no longer applies: the fins moved forward -> see the OpenRocket re-run.) liftoff %.2f / dry %.2f cal vs the OLD CP"
    % (CP_TIP, (CP_TIP - (station(lo_z) + NOSE_LEN)) / 43.0, (CP_TIP - (station(dry_z) + NOSE_LEN)) / 43.0))
rep("")
rep("NOT IN FLIGHT MASS: RBF pin (pulled at pad), install tool, test stand, t5 flight_bulkhead (replaced by the integral ring), spacers.")
rep("OPENROCKET: NS_BODY_G=%.1f NS_BODY_LEN=%.1f NS_BODY_CGX=%.1f (non-nose dry mass g, body length mm, body CG mm from body top)" % (nn_m, 340.0 - DL_EBAY, station(nn_z)))
rep("NOTE nose v5 shoulder is 42 mm (stations 0-42); t5_integration assumed 20 mm of shoulder, so the canopy space is 42-110.")
rep("NOTE the e-bay lead / fin-can bond epoxy / paint are not included (a few grams).")

# ---------------- export
doc = App.newDocument("Phoenix_T5v2_full")
for nm, g, m, z, basis, s in items:
    if s is None: continue
    o = doc.addObject("Part::Feature", "".join(c if c.isalnum() else "_" for c in nm)[:40])
    o.Shape = s
    o.Label = "%s [%.1f g]" % (nm, m)
o = doc.addObject("Part::Feature", "C6_motor"); o.Shape = motor; o.Label = "C6 motor stand-in [%.0f g loaded]" % MOTOR_LOADED
cm = doc.addObject("Part::Feature", "CG_liftoff"); cm.Shape = Part.makeSphere(2.5, V(0, 0, lo_z)); cm.Label = "CG liftoff %.1f g @ st %.1f" % (lo_m, station(lo_z))
doc.recompute()
doc.saveAs(os.path.join(OUT, NAME + ".FCStd"))
Part.makeCompound([i[5] for i in items if i[5] is not None] + [motor]).exportStep(os.path.join(OUT, NAME + ".step"))

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(24, 5))
    cols = {"nose": "0.25", "airframe": "tab:blue", "T5 ejector": "tab:red", "e-bay": "tab:brown", "aft": "tab:gray", "recovery": "tab:green"}
    Y_CUT = 0.7          # section() edges, not slice() wires: slice() returns nothing for the threaded fwd_section
    cut_face = Part.Face(Part.makePolygon([V(-200, Y_CUT, -400), V(200, Y_CUT, -400), V(200, Y_CUT, 400), V(-200, Y_CUT, 400), V(-200, Y_CUT, -400)]))
    def draw(s, c):
        for e in s.section(cut_face).Edges:
            pts = e.discretize(Deflection=0.1)
            ax.plot([station(p.z) + NOSE_LEN for p in pts], [p.x for p in pts], color=c, lw=0.5)
    for nm, g, m, z, basis, s in items:
        if s is None or g == "recovery": continue
        draw(s, cols[g])
    draw(motor, "tab:orange")
    ax.plot(station(lo_z) + NOSE_LEN, 0, "o", ms=10, mfc="none", mec="k"); ax.annotate("CG %.0f g" % lo_m, (station(lo_z) + NOSE_LEN, 3))
    ax.plot(CP_TIP, 0, "x", ms=10, color="k"); ax.annotate("CP %.0f (OR)" % CP_TIP, (CP_TIP, -8))
    ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.set_xlabel("mm from nose tip"); ax.set_title("Phoenix ABS 40-43 + T5 v2, assembly v2 (all ABS, e-bay -%.0f mm), section y=0.7, cocked, liftoff on C6" % DL_EBAY + "")
    fig.savefig(os.path.join(OUT, NAME + "_section.png"), dpi=110, bbox_inches="tight")
except Exception as ex:
    print("section plot skipped:", ex)

with open(os.path.join(OUT, NAME + "_mass_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(rep_lines) + "\n")
print("done in %.1f s" % (time.time() - t0))

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v13: 30 mm EXTENSION RING (replaces the 16 mm v12 ring), sled v21.

User, 2026-10-27: "a new, improved, and longer Ebay sled with distinct slots for each card ... Our main bottleneck now
is (dead) cable length on the already soldered package"; ring length "you pick".  30 mm = the shortest that puts the
ADXL375 (27 mm with its plug, now in its own slot) and the figure-8 cleat horns above the ESP32's JST (sled v21 zone C).
v13 = v12 with RING_L 30 (the ring is still the as-built FwdTube's top RING_L mm raised RING_L + the nose v6 shoulder
+ a 0.3 lip) and sled v21.  Rollup: ADXL ~45 mm fwd (electronics CG st 47.8 -> 45.2), jumper slack on the horns.

v12 notes:
  LOCK      the ring's key slot is widened to +-15 deg around 180 (print clocking of the seated ring is uncertain):
            the cap's key tab drops into it (back the ring off at most ~1/12 turn), so ring -> cap key -> W M2 -> post ->
            sled key -> tube groove stops the ring backing out when the nose is turned.  Never trim the tab.
  RING      NEW PART.  = the as-built FwdTube's top RING_L mm (female thread band, key groove, bore) raised RING_L
            + the nose v6's threaded shoulder (male, bore d35.9) left exactly where it sits today
            + a 0.3 mm lip joining them.  So the ring screws into the tube exactly as the nose does, and the nose
            screws into the ring exactly as it screws into the tube (same thread phase, same seat faces).
  nose, EbayCap   the as-built parts, RING_L further forward (the cap rides on the sled's post).
  FwdTube, AftTube, fin can   the as-built parts, UNTOUCHED (this script only reads their STEPs).

Frame: the v10 STEP frame, z = 313.5 - station (station 0 = the FwdTube mouth face = the OLD nose base).
The new nose base / ring top face is at station -RING_L.  Tip distances in the rollup are from the NEW tip.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Any FAIL line means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, MeshPart
from FreeCAD import Vector as V

T0 = time.time()
PROJ = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43"
MD = os.path.join(PROJ, "Models")
NAME, REV = "PhoenixABS40-43_D9aft_v13", "D9aft_v13"
SLED_SRC = os.path.join(PROJ, "Avionics", "PhoenixABS40-43_avbay_sled_v21.py")
NOSE_STEP = os.path.join(PROJ, "Nosecone", "Models", "PhoenixABS40-43_nose_VonKarmanScrew_v6.step")
RHO = 1.05e-3
BODY_LEN = 313.5                       # v10 frame
NOSE_LEN = 65.0
RING_L = 30.0
SH_LEN, SH_R_IN = 9.5, 17.95           # nose v6 shoulder
PITCH = 3.0
R_OD, R_ID = 21.5, 20.0
CREST, ROOT = 19.65, 20.45             # female thread (tube mouth)
LIP_T = 0.3
KEY_ANG = 180.0
SLOT_HALF = 15.0                        # ring key slot +- deg (cap key half-angle ~3.4 deg)
SLOT_R = (18.0, ROOT)                   # as the tube groove: never deeper than the thread root

def zs(st): return BODY_LEN - st
def station(z): return BODY_LEN - z
def cyl(r, z0, z1): return Part.makeCylinder(r, z1 - z0, V(0, 0, z0))
def ann(r0, r1, z0, z1): return cyl(r1, z0, z1).cut(cyl(r0, z0 - 1, z1 + 1))
def vol(s): return s.Volume if s.Solids else 0.0
def vv(a, b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.0
    return vol(a.common(b))
def com(s):
    sol = s.Solids
    return sum((x.CenterOfMass * x.Volume for x in sol[1:]), sol[0].CenterOfMass * sol[0].Volume) * (1.0 / sum(x.Volume for x in sol))
def rd(path):
    s = Part.Shape(); s.read(path)
    return s.Solids[0] if len(s.Solids) == 1 else s
def mv(s, dz=0.0, rot=0.0):
    s = s.copy()
    if rot: s.rotate(V(0, 0, 0), V(0, 0, 1), rot)
    if dz: s.translate(V(0, 0, dz))
    return s

report = []
def rep(s): report.append(s); print(s, flush=True)
def ok(c): return "PASS" if c else "FAIL"

# ------------------------------------------------------------------ as-built parts (read-only)
FW = rd(os.path.join(MD, "PhoenixABS40-43_D9aft_v10_FwdTube.step"))
CAP = rd(os.path.join(MD, "PhoenixABS40-43_D9aft_v10_EbayCap.step"))
NOSE_RAW = rd(NOSE_STEP)
NOSE = NOSE_RAW.copy(); NOSE.rotate(V(0, 0, 0), V(1, 0, 0), 180.0); NOSE.translate(V(0, 0, BODY_LEN + NOSE_LEN))   # = D9aft v2 place_nose
print("STEPs read %.0f s" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ sled v21 (library exec, no main)
SL = {"__name__": "sledlib"}
_ss = open(SLED_SRC, encoding="utf-8").read()
exec(_ss[:_ss.rstrip().rfind("main()")], SL)
assert SL["REV"] == "v21" and abs(SL["CAP_Z0"] - 75.4) < 1e-9
_log = []
SLED, _ = SL['build_sled'](_log)
SLED = SL['heal'](SLED, "Sled", _log)
COMP = dict((n, f()) for n, f in SL['COMPONENTS'])
SLED_DZ = BODY_LEN - SL['TUBE_MOUTH_Z']                     # sled Z 60.8 (tube mouth) -> station 0
sled = mv(SLED, SLED_DZ)
comp = dict((n, mv(s, SLED_DZ)) for n, s in COMP.items())
print("sled v21 built %.0f s" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the RING
slice_ = FW.common(cyl(30.0, zs(RING_L), zs(0.0) + 1.0)).translated(V(0, 0, RING_L))
shoulder = NOSE.common(cyl(30.0, zs(SH_LEN) - 1.0, zs(0.0)))
lip = ann(SH_R_IN, R_ID + 0.3, zs(0.0), zs(0.0) + LIP_T)
RING_HOW = "none valid"
_cands = []
for _how, _mk in (("fuse", lambda: slice_.fuse([shoulder, lip])), ("fuzzy fuse 1e-4", lambda: slice_.fuse([shoulder, lip], 1e-4))):
    try: _cands.append((_how, _mk()))
    except Exception as _e: print("ring %s failed: %s" % (_how, _e))
RING = _cands[0][1]
for _how, _c in _cands:
    for _step, _f in (("", lambda x: x), (" + removeSplitter", lambda x: x.removeSplitter()), (" + STEP heal", lambda x: SL['heal'](x, "Ring", _log)),
                      (" + fix", lambda x: (lambda y: (y.fix(1e-4, 1e-4, 1e-4), y)[1])(x.copy()))):
        try: _t = SL['as_solid'](_f(_c))
        except Exception as _e: print("ring %s%s: %s" % (_how, _step, _e)); continue
        if _t.isValid() and len(_t.Solids) == 1:
            RING, RING_HOW = _t, _how + _step
            break
    if RING_HOW != "none valid": break
print("ring: %s" % RING_HOW, flush=True)
_slot = Part.makeCylinder(SLOT_R[1], (zs(-RING_L) + 1.0) - (zs(0.0) + LIP_T), V(0, 0, zs(0.0) + LIP_T), V(0, 0, 1), 2 * SLOT_HALF)
_slot = _slot.cut(cyl(SLOT_R[0], zs(0.0), zs(-RING_L) + 2.0))
_slot.rotate(V(0, 0, 0), V(0, 0, 1), KEY_ANG - SLOT_HALF)
RING = SL['as_solid'](RING.cut(_slot))
NOSE12 = mv(NOSE, RING_L)
CAP12 = mv(CAP, RING_L)
print("ring built %.0f s" % (time.time() - T0), flush=True)

# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: +%.0f mm screw-in EXTENSION RING (FwdTube -> ring -> nose), sled v21; airframe as built ==" % (REV, RING_L))
rep("Frame z = %.1f - station; station 0 = the as-built FwdTube mouth; NEW nose base / ring top at station %.1f." % (BODY_LEN, -RING_L))
rep("")
rep("STATION TABLE (new tip = old tip - %.0f)" % RING_L)
for a, b, t in ((-RING_L - NOSE_LEN, -RING_L, "nose v6 (as built), screws into the ring"),
                (-RING_L, -RING_L + SH_LEN, "ring female thread (= the FwdTube's), nose shoulder in it"),
                (-RING_L + 10.5, -RING_L + 15.4, "EbayCap (as built, +30 on the sled v21 post)"),
                (-RING_L + 15.4, 9.5, "sled v21 ZONE C (ADXL slot + figure-8 cleat horns); ring spigot st -0.3..9.5 in the FwdTube mouth"),
                (0.0, 83.6, "FwdTube as built: e-bay, sled v21 on the seat ring (all v19 Z)"),
                (104.6, 254.6, "chute bay 150 (as built)")):
    rep("  %8.1f - %8.1f  %s" % (a, b, t))
rep("")

# ---- ring solid + geometry
bb = RING.BoundBox
rep(("%s ring valid (" + RING_HOW + "): %s, %d solid(s), station %.2f..%.2f, Rmax %.2f, volume %.0f mm3 = %.1f g ABS")
    % (ok(RING.isValid() and len(RING.Solids) == 1), RING.isValid(), len(RING.Solids), station(bb.ZMax), station(bb.ZMin), max(bb.XMax, bb.YMax), RING.Volume, RING.Volume * RHO))
rep("%s ring OD flush with the tube: Rmax %.2f vs %.2f" % (ok(max(bb.XMax, bb.YMax) <= R_OD + 0.01), max(bb.XMax, bb.YMax), R_OD))
probes = [("spigot bore open (R 17.7, st 5)", V(17.7, 0, zs(5.0)), False),
          ("spigot wall solid (R 18.6, st 5)", V(18.6, 0, zs(5.0)), True),
          ("lip solid (R 19.0, st -0.15)", V(19.0 * math.cos(1.0), 19.0 * math.sin(1.0), zs(-0.15)), True),
          ("above the lip open for the cap (R 19.0, st -0.45)", V(19.0 * math.cos(1.0), 19.0 * math.sin(1.0), zs(-0.45)), False),
          ("body wall solid (R 21.0, st -8)", V(21.0, 0, zs(-8.0)), True),
          ("body bore open below the band (R 19.9, st -2)", V(19.9 * math.cos(1.0), 19.9 * math.sin(1.0), zs(-2.0)), False)]
bad = [n for n, p, w in probes if RING.isInside(p, 1e-4, True) != w]
rep("%s ring probes %d/%d %s" % (ok(not bad), len(probes) - len(bad), len(probes), bad or ""))

# ---- the two thread pairs vs the as-built pair (same relative geometry -> same overlap)
t1 = time.time()
base = vv(NOSE, FW)
r_fw = vv(RING, FW)
n_r = vv(NOSE12, RING)
rep("%s threads: ring x FwdTube %.3f mm3, nose(+30) x ring %.3f mm3 vs the AS-BUILT nose x FwdTube %.3f mm3 (must match: same thread, same phase)"
    % (ok(abs(r_fw - base) < 0.05 + 0.02 * base and abs(n_r - base) < 0.05 + 0.02 * base), r_fw, n_r, base))
neg = vv(mv(RING, -PITCH / 2.0, 180.0), FW)
rep("%s NEGATIVE CONTROL: ring half a pitch out of phase x FwdTube = %.2f mm3 (must be >> %.3f)" % (ok(neg > base + 5.0), neg, base))
sw = []
for phi in (90.0, 180.0, 360.0):
    sw.append((phi, round(vv(mv(RING, PITCH * phi / 360.0, phi), FW), 3)))
rep("%s ring unscrew sweep (rotate + advance %.1f mm/turn) x FwdTube: %s" % (ok(all(v <= base + 0.05 + 0.02 * base for _, v in sw)), PITCH, sw))
rep("NOTE thread booleans %.0f s" % (time.time() - t1))

# ---- seats
seat = ann(ROOT + 0.05, R_OD - 0.05, zs(0.0), zs(0.0) + 0.05)
fr = vv(RING, seat) / seat.Volume
dropped = vv(mv(RING, -0.3), FW)
rep("%s ring body seats on the tube mouth face (annulus r %.2f..%.2f at st 0): ring fills %.0f %% of it; dropped 0.3 -> %.1f mm3 (must be > 0)"
    % (ok(fr > 0.9 and dropped > base + 5.0), ROOT, R_OD, 100 * fr, dropped))
gap = CAP12.BoundBox.ZMin - (zs(0.0) + LIP_T)
rep("%s EbayCap underside st %.2f over the lip top st %.2f: gap %.2f mm" % (ok(gap >= 0.2), station(CAP12.BoundBox.ZMin), -LIP_T, gap))
sh_end_old = zs(SH_LEN)
foam = sh_end_old + RING_L - CAP12.BoundBox.ZMax
foam0 = sh_end_old - CAP.BoundBox.ZMax
rep("%s nose shoulder end vs EbayCap top (incl. pull loop): %.2f mm (as built %.2f): same spring / foam preload" % (ok(abs(foam - foam0) < 1e-6), foam, foam0))
nc = vv(NOSE12, CAP12); nc0 = vv(NOSE, CAP)
rep("%s nose x EbayCap (spring bumps) %.2f mm3 = as built %.2f" % (ok(abs(nc - nc0) < 0.05), nc, nc0))

# ---- e-bay fit
rest = [("Sled v21", sled)] + list(comp.items())
hits = []
for pn, ps in (("FwdTube", FW), ("Ring", RING), ("EbayCap", CAP12), ("Nose", NOSE12)):
    for n, s in rest:
        v = vv(ps, s)
        if v > 1e-2 and not (pn == "EbayCap" and n == "Sled v21"):
            hits.append((pn, n, round(v, 3)))
rep("%s e-bay vs FwdTube / ring / EbayCap / nose: %s" % (ok(not hits), hits or "no contact"))
cs = vv(CAP12, sled)
rep("%s EbayCap on the sled post: overlap %.3f mm3 (contact only)" % (ok(cs < 0.05), cs))
post_top = station(sled.BoundBox.ZMax)
rep("%s sled top st %.2f = EbayCap underside st %.2f (the W M2x10 clamps the cap to the post)" % (ok(abs(sled.BoundBox.ZMax - CAP12.BoundBox.ZMin) < 0.05), post_top, station(CAP12.BoundBox.ZMin)))
keyneg = vv(mv(sled, 0.0, 4.0), FW)
rep("%s sled KEY clocks the sled in the tube groove: seated 0; sled turned 4 deg -> %.2f mm3 into the groove wall (must be > 0)" % (ok(keyneg > 0.05), keyneg))
swept = cyl(40.0, zs(SH_LEN), zs(-RING_L)).cut(cyl(SH_R_IN, zs(SH_LEN) - 1, zs(-RING_L) + 1))
sh = [(n, round(vv(s, swept), 3)) for n, s in rest if vv(s, swept) > 1e-3]
rep("%s ring screwed on OVER the e-bay: nothing at R >= %.2f above st %.1f (any ring pose on the way down): %s" % (ok(not sh), SH_R_IN, SH_LEN, sh or "clear"))
lk = [(a, round(vv(mv(RING, 0.0, a), CAP12), 3)) for a in (-17.0, -10.0, 0.0, 10.0, 17.0)]
lk_ok = all((v < 1e-2) if abs(a) <= 10.0 else (v > 0.05) for a, v in lk)
rep("%s LOCK: seated cap key in the ring slot (+-%.0f deg): ring turned (deg, mm3 into the key) %s -> free within +-10, blocked at +-17" % (ok(lk_ok), SLOT_HALF, lk))
rep("NOTE slot costs %.0f %% of the ring's female thread band (as-built tube groove: %.0f %%)" % (100 * 2 * SLOT_HALF / 360.0, 100 * 3.0 / (2 * math.pi * CREST)))
lift = [d for d in (0.0, 2.0, 6.0, 12.0, 20.0) if vv(mv(CAP12, d), RING) > 1e-2]
rep("%s EbayCap seated (0) and lifting straight out of the ring mouth (2..20 mm): %s" % (ok(not lift), lift or "clear"))
sl_lift = [d for d in (0.5, 5.0, 10.0, 20.0, 40.0, 60.0, 80.0, 90.0) if vv(mv(sled, d), FW) > 1e-2]
rep("%s sled (key in the groove) lifts out of the tube once the ring is off: %s" % (ok(not sl_lift), sl_lift or "clear 0.5..90"))

# ---- ports unchanged
rep("PASS sound / static ports: in the as-built FwdTube, sled v21 parts at their v19 Z (piezo on the sound port: sled report [D9])")

# ---- MASS & CG  (v10 rollup items; station -> NEW tip = st + RING_L + 65 for the tube-borne items)
rep("")
rep("MASS & CG (v10 report items; ring / sled from CAD x ABS 1.05).  NEW tip distance = station + %.0f + %.0f" % (RING_L, NOSE_LEN))
ring_cg = station(com(RING).z)
sled_m, sled_cg = sled.Volume * RHO, station(com(sled).z)
items = [("Nose cone v6", "nose", 14.6, -21.2 - RING_L),
         ("EXTENSION RING v13", "airframe", RING.Volume * RHO, ring_cg),
         ("FwdTube (as built)", "airframe", 27.1, 62.4),
         ("AftTube v9/v11 (as built)", "airframe", 36.1, 173.8),
         ("EbayCap (+30 fwd)", "e-bay", 6.3, 12.0 - RING_L),
         ("M2x10 (W only)", "e-bay", 0.4, 13.7 - RING_L),
         ("ElectronicsSled v21", "e-bay", sled_m, sled_cg),
         ("Electronics (v10 38.5 - 3.5; v21: ADXL 45 fwd)", "e-bay", 35.0, 45.2),
         ("Jumper slack on the v21 horns (ASSUMED)", "e-bay", 2.0, -5.2),
         ("Canopy d500 + harness", "recovery", 16.0, 149.6),
         ("5 mm retention line 1.5 m (ASSUMED)", "recovery", 18.0, 194.6),
         ("Nomex", "recovery", 4.0, 218.5),
         ("Fin can + fins + epoxy", "aft", 52.4, 284.0),
         ("MotorRetainerCap v1", "aft", 9.0, 324.3),
         ("Klima D9-5 loaded", "motor", 27.1, 292.6)]
for n, g, m, st in items:
    rep("  %-48s %-9s %6.1f g  st %7.1f  tip %6.1f" % (n, g, m, st, st + RING_L + NOSE_LEN))
M = sum(i[2] for i in items)
CGT = sum(i[2] * (i[3] + RING_L + NOSE_LEN) for i in items) / M
dry = [i for i in items if i[1] != "motor"]
MD_ = sum(i[2] for i in dry); CGD = sum(i[2] * (i[3] + RING_L + NOSE_LEN) for i in dry) / MD_
rep("  Liftoff %.1f g, CG %.1f mm from the NEW tip (v10: 262.6 g, 228.0 from the old tip); dry %.1f g, CG %.1f" % (M, CGT, MD_, CGD))
body_items = [i for i in items if i[1] != "nose" and i[1] != "motor"]
BM = sum(i[2] for i in body_items); BCG = sum(i[2] * (i[3] + RING_L) for i in body_items) / BM
rep("OPENROCKET: NOSE_G=14.6 NOSE_CG=43.8 NS_BODY_G=%.1f NS_BODY_LEN=%.1f NS_BODY_CGX=%.1f   (body = ring + tubes + everything but nose & motor, from the new nose base)"
    % (BM, BODY_LEN + RING_L, BCG))
rep("NOTE the 226 gate was 1.5 cal on the OLD CP (290.9 from the old tip): it does not carry over -- re-derive from the v13 OpenRocket CP.")

# ---- export
rep("")
os.makedirs(MD, exist_ok=True)
stp = os.path.join(MD, NAME + "_ExtensionRing.step")
RING.exportStep(stp)
pr = RING.copy(); pr.rotate(V(0, 0, 0), V(1, 0, 0), 180.0); pr.translate(V(0, 0, -pr.BoundBox.ZMin))   # spigot end on the bed (as the nose prints)
m = MeshPart.meshFromShape(Shape=pr, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False)
stl = os.path.join(MD, NAME + "_ExtensionRing.stl")
m.write(stl)
rep("EXPORT %s (v10 frame)  +  %s (print pose: spigot end down, like the nose's shoulder)" % (os.path.basename(stp), os.path.basename(stl)))
doc = App.newDocument("Phoenix_D9aft_v13")
for n, s in (("ExtensionRing", RING), ("FwdTube_asbuilt", FW), ("EbayCap_plus30", CAP12), ("Nose_plus30", NOSE12), ("Sled_v21", sled)):
    doc.addObject("Part::Feature", n).Shape = s
doc.recompute(); doc.saveAs(os.path.join(MD, NAME + ".FCStd"))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT v13: %s (%d FAIL)  [%.0f s]" % ("ALL PASS" if not fails else "FAILURES", len(fails), time.time() - T0))
with open(os.path.join(MD, NAME + "_report.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(report) + "\n")

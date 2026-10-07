# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v9: v8 + PRINTED SNAP LATCH in place of the printed shear pins.

Why: the v1 shear pins (0.8 mm thick, 0.6 mm neck) do not print -- they come out as blobs (user, 2026-10-07).
Snap-latch coupon (Models/PhoenixABS40-43_SnapLatchCoupon_v1.py, _v2.py) printed: L24 held 873 g = 8.6 N per
pair on its first pull (model 12.1 N). The user asked to implement it now ("we can't afford to test right now").

Built on v8's EXPORTED parts (read-only), so v8's run and outputs are untouched:
  Models/PhoenixABS40-43_D9aft_v8_AftTube.step            (= v6 AftTube: chute bay, launch lug, 2 pin slots)
  Models/PhoenixABS40-43_D9aft_v8_AftFinCanSlotted.step   (v4 slotted can + v8 staple lug at 300 deg, 2 pin slots)
Latch geometry = coupon v2 (Models/PhoenixABS40-43_SnapLatchCoupon_v1.py exec'd with BAND_AFT 7, own namespace).

  AftTube    the 2 pin slots are FILLED (slot volume clipped to the wall, fused back); 2 L24 tongues at 60 / 180 deg
             (the old pin angles): 7 mm aft band, 1.0 aft gap, 0.8 end slot, 45 deg slanted forward edge,
             1.2 mm tongue (outer skin recessed 0.3), bump 1.2 x 5 x 4.08 (release 45 / entry 30 deg).
             Printed forward end down, as v6..v8.
  fin can    pin slots FILLED; 2 coupler windows at 60 / 180 deg with a matched 45 deg forward face.
  pins       gone (no ShearPin, card, or pin coupon in the flight set).
  unchanged  everything else in v8 (nose, FwdTube + 5 mm eyelet, EbayCap, sled v7, staple lug, fins, cap).
  Uneven latch angles (120 / 240 apart) -> the fin can clicks in only one clocking (fins clear of the rod line).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame: v1 fin-can frame Zf (z = 0 the fin-can aft face, +z toward the nose). Any FAIL line means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, MeshPart

V = App.Vector
t9 = time.time()
PHX = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43"
MODELS = os.path.join(PHX, "Models")
PRINT_RAW = os.path.join(PHX, "Print Files", "Aft Deploy D9")
PRINT_READY = os.path.join(PRINT_RAW, "Ready to Print")
CURATED = os.path.join(PHX, "Print Files", "Ready to Print", "D9")
NAME9, REV9 = "PhoenixABS40-43_D9aft_v9", "D9aft_v9"
TUBE8 = os.path.join(MODELS, "PhoenixABS40-43_D9aft_v8_AftTube.step")
FC8 = os.path.join(MODELS, "PhoenixABS40-43_D9aft_v8_AftFinCanSlotted.step")
CPN_SRC = os.path.join(MODELS, "PhoenixABS40-43_SnapLatchCoupon_v1.py")
RHO_ABS = 1.05e-3

# ---------------- v1 constants (unchanged through v8; each one is proven by a probe on the v8 parts below)
R_OD, R_ID = 21.5, 20.0
CPL_R_O, CPL_R_I = 19.80, 18.50
SHOULDER_Z, CPL_LEN = 51.4, 40.0
CPL_Z1 = SHOULDER_Z + CPL_LEN
BH_Z0, BH_Z1 = 55.9, 58.9
PORT_R = 7.0
PIN_ANG, Z_PIN = (60.0, 180.0), 63.4
PIN_A, PIN_B, SLOT_CLR = 0.8, 2.4, 0.2
LUG_ANG, LUG_R0, LUG_W = 300.0, 8.5, 9.0         # v8 staple lug
LL_ANG = 300.0                                    # launch lug (outside the AftTube, Zf 152.5..187.5 as v1..v8)
L_LATCH = 24.0
LATCH_ANG = PIN_ANG
COUPON_PULL = dict(g=873.0, model=12.1)           # coupon v1 L24, first pull (curled aft band: may include rub)
HOLD_NEED, SEALED_TERM, RELEASE_BUDGET, FRICTION = 4.2, 2.6, 24.0, 3.0

report = []
def rep(s=""): print(s); report.append(s)
def ok(c): return "PASS" if c else "FAIL"
def pol(r, a, z):
    a = math.radians(a); return V(r * math.cos(a), r * math.sin(a), z)
def inside(s, p): return s.isInside(p, 1e-4, True)
def cyl(r, z0, z1): return Part.makeCylinder(r, z1 - z0, V(0, 0, z0))
def ann(r0, r1, z0, z1): return cyl(r1, z0, z1).cut(cyl(r0, z0 - 1, z1 + 1))
def read(p):
    s = Part.Shape(); s.read(p)
    return s.Solids[0] if len(s.Solids) == 1 else s
def pin_fill(r0, r1, a):
    b = Part.makeBox(r1 - r0 + 0.02, PIN_B + SLOT_CLR, PIN_A + SLOT_CLR, V(r0 - 0.01, -(PIN_B + SLOT_CLR) / 2, Z_PIN - (PIN_A + SLOT_CLR) / 2))
    b = b.common(ann(r0, r1, Z_PIN - 5, Z_PIN + 5)); b.rotate(V(0, 0, 0), V(0, 0, 1), a); return b

# ---------------- coupon v2 latch geometry (own namespace)
_cs = open(CPN_SRC, encoding="utf-8").read()
assert _cs.count("BAND_AFT = 4.0 ") == 1
_cs = _cs.replace("BAND_AFT = 4.0 ", "BAND_AFT = 7.0 ")
_cb = _cs.index("\n# BUILD\n"); _cb = _cs.rfind("# ====", 0, _cb)
CPN = {}
exec(compile(_cs[:_cb], CPN_SRC + " [coupon v2 params]", "exec"), CPN)
for k in ('R_OD', 'R_ID', 'CPL_R_O', 'CPL_R_I'):
    assert abs(CPN[k] - globals()[k]) < 1e-9, k
DZ = V(0, 0, SHOULDER_Z)                         # coupon z 0 = tube aft face = fin-can shoulder

def beam(L, E, n=800):
    sb = L - CPN['S_B_OFF']; ds = sb / n; J = 0.0; arr = []
    for i in range(n):
        s_ = (i + 0.5) * ds
        I = (CPN['W_TIP'] + (L - s_) * CPN['TAPER']) * CPN['T_TONGUE'] ** 3 / 12
        m = CPN['R_T'] * math.sin((sb - s_) / CPN['R_T'])
        J += m * m / (E * I) * ds; arr.append((m, I))
    Pn = CPN['DELTA'] / J
    return Pn, max(Pn * m * (CPN['T_TONGUE'] / 2) / (E * I) for m, I in arr)
def fac(a, mu):
    ta = math.tan(math.radians(a)); return (ta + mu) / (1 - mu * ta)

# =====================================================================================
# BUILD
# =====================================================================================
tube8, fc8 = read(TUBE8), read(FC8)
LG = [CPN['latch_geom'](L_LATCH, a) for a in LATCH_ANG]
for g in LG:
    for k in ('tongue', 'cut', 'bump'): g[k] = g[k].translated(DZ)
t = tube8
for a in PIN_ANG: t = t.fuse(pin_fill(R_ID, R_OD, a))
for g in LG: t = t.cut(g['cut'])
for g in LG: t = t.fuse(g['tongue'])
tube9_nb = t.removeSplitter()
for g in LG: t = t.fuse(g['bump'])
tube9 = t.removeSplitter()

def window(a):
    hw = CPN['deg'](CPN['BUMP_S'] / 2 / R_ID) + CPN['deg'](CPN['CLR_TAN'] / CPL_R_O)
    r0, r1 = CPL_R_I - 0.3, R_ID
    zf, za = CPN['z_win_fwd'], CPN['Z_WIN_AFT']
    return CPN['rev']([(r0, za + SHOULDER_Z), (r1, za + SHOULDER_Z), (r1, zf(r1) + SHOULDER_Z), (r0, zf(r0) + SHOULDER_Z)], a - hw, a + hw)
WIN = [window(a) for a in LATCH_ANG]
f = fc8
for a in PIN_ANG: f = f.fuse(pin_fill(CPL_R_I, CPL_R_O, a))
for w in WIN: f = f.cut(w)
fc9 = f.Solids[0] if len(f.Solids) == 1 else f   # no removeSplitter on the faceted thread (v1 rule)
# boolean checks run on the coupler zone only (Zf > 45): far from the threaded boss
ZONE = cyl(30.0, 45.0, 200.0)
fc9_z, fc8_z = fc9.common(ZONE), fc8.common(ZONE)
print("v9 parts in %.1f s" % (time.time() - t9), flush=True)

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: v8 + printed SNAP LATCH (coupon v2, L24 at %s deg) in place of the shear pins ==" % (REV9, "/".join("%.0f" % a for a in LATCH_ANG)))
rep("Inputs (read-only): %s, %s; latch = coupon v2 shifted to Zf %.1f." % (os.path.basename(TUBE8), os.path.basename(FC8), SHOULDER_Z))
rep("")
pv = [("v8 tube: pin slot 60 open (Z_PIN, angles)", tube8, pol(R_ID + 0.75, 60, Z_PIN), False),
      ("v8 tube: wall solid beside it", tube8, pol(R_ID + 0.75, 72, Z_PIN), True),
      ("v8 tube: aft face at the shoulder (wall just forward)", tube8, pol(R_ID + 0.75, 30, SHOULDER_Z + 0.3), True),
      ("v8 tube: nothing aft of the shoulder", tube8, pol(R_ID + 0.75, 30, SHOULDER_Z - 0.3), False),
      ("v8 can: coupler OD trimmed (CPL_R_O)", fc8, pol(19.83, 30, SHOULDER_Z + 3.0), False),
      ("v8 can: coupler wall present", fc8, pol((CPL_R_O + CPL_R_I) / 2, 30, SHOULDER_Z + 20), True),
      ("v8 can: coupler front at CPL_Z1", fc8, pol((CPL_R_O + CPL_R_I) / 2, 30, CPL_Z1 + 0.3), False),
      ("v8 can: pin slot 180 open", fc8, pol(19.15, 180, Z_PIN), False),
      ("v8 can: staple lug at 300 (inner leg)", fc8, pol(LUG_R0 + 1.0, LUG_ANG, BH_Z1 + 2.0), True)]
bad = [n for n, s, p, w in pv if inside(s, p) != w]
rep("%s v1/v8 constants confirmed on the v8 parts: %d/%d probes%s" % (ok(not bad), len(pv) - len(bad), len(pv), "; WRONG %s" % bad if bad else ""))
for k, s in (('AftTube v9', tube9), ('AftFinCanSlotted v9', fc9), ('fin can v9 coupler zone', fc9_z)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))

# --- AftTube
pr = [("old pin slot %.0f filled" % a, pol(R_ID + 0.75, a, Z_PIN), True) for a in PIN_ANG]
for g, a in zip(LG, LATCH_ANG):
    tt, tr = g['th_tip'], g['th_root']; thm = (tt + tr) / 2
    zt = CPN['Z_TAFT'] + SHOULDER_Z
    ze = zt + CPN['W_TIP'] + (thm - tt) * math.radians(1) * CPN['R_T']
    R = CPN['R_T']
    pr += [("%.0f end slot open" % a, pol(R, tt - CPN['deg'](CPN['GAP_END'] / 2 / R), zt + 2), False),
           ("%.0f aft gap open" % a, pol(R, thm, zt - CPN['GAP_AFT'] / 2), False),
           ("%.0f slant gap open" % a, pol(R, thm, ze + CPN['GAP_FWD'] / 2), False),
           ("%.0f tongue present" % a, pol(R, thm, (zt + ze) / 2), True),
           ("%.0f tongue skin recessed" % a, pol((CPN['R_TO'] + R_OD) / 2, thm, (zt + ze) / 2), False),
           ("%.0f aft band present" % a, pol(R, thm, SHOULDER_Z + CPN['BAND_AFT'] / 2), True),
           ("%.0f tongue joined at the root" % a, pol(R, tr + 0.5, zt + 3), True),
           ("%.0f bump present" % a, pol(R_ID - CPN['BUMP_H'] / 2, a, CPN['E0'] + CPN['L_ENT'] + CPN['BUMP_FLAT'] / 2 + SHOULDER_Z), True)]
bad = [n for n, p, w in pr if inside(tube9, p) != w]
rep("%s AftTube v9 probes %d/%d%s" % (ok(not bad), len(pr) - len(bad), len(pr), "; WRONG %s" % bad if bad else ""))
foot = (SHOULDER_Z + CPN['Z_TAFT'] - CPN['GAP_AFT'], SHOULDER_Z + CPN['Z_TAFT'] + CPN['W_TIP'] + L_LATCH + CPN['GAP_FWD'])
rep("%s latch footprint Zf %.1f..%.1f inside the coupler (%.1f..%.1f): every slot is backed by the coupler wall" % (ok(foot[1] <= CPL_Z1 - 0.5), foot[0], foot[1], SHOULDER_Z, CPL_Z1))
da, db = tube9.cut(tube8), tube8.cut(tube9)
bbs = [s.optimalBoundingBox() for s in da.Solids + db.Solids]     # exact: the plain BoundBox is loose on the helical gap
z0d, z1d = min(b.ZMin for b in bbs), max(b.ZMax for b in bbs)
rmax = max(max(math.hypot(v.X, v.Y) for v in s.Vertexes) for s in da.Solids) if da.Solids else 0.0
rep("%s AftTube v9 vs v8: +%.1f / -%.1f mm3, all within Zf %.2f..%.2f (latch zone + pin slots) and nothing added beyond r %.2f (OD %.1f): launch lug, bore, joint UNTOUCHED"
    % (ok(z0d >= SHOULDER_Z - 0.01 and z1d <= foot[1] + 0.01 and rmax <= R_OD + 1e-3), da.Volume, db.Volume, z0d, z1d, rmax, R_OD))

# --- fin can
zwm = (CPN['Z_WIN_AFT'] + CPN['z_win_fwd'](19.15)) / 2 + SHOULDER_Z
fp = [("old pin slot %.0f filled" % a, pol(19.15, a, Z_PIN), True) for a in PIN_ANG]
fp += [("window %.0f open" % a, pol(19.15, a, zwm), False) for a in LATCH_ANG]
fp += [("coupler wall beside window %.0f" % a, pol(19.15, a + 15, zwm), True) for a in LATCH_ANG]
fp += [("staple lug intact", pol(LUG_R0 + 1.0, LUG_ANG, BH_Z1 + 2.0), True), ("gas port open", V(0, 0, (BH_Z0 + BH_Z1) / 2), False),
       ("thrust ring solid", pol(14.0, 60, (BH_Z0 + BH_Z1) / 2), True)]
bad = [n for n, p, w in fp if inside(fc9, p) != w]
rep("%s fin can v9 (REAL part) probes %d/%d%s" % (ok(not bad), len(fp) - len(bad), len(fp), "; WRONG %s" % bad if bad else ""))
lug_zone = fc8.common(Part.makeBox(12.0, LUG_W + 2, 30.0, V(LUG_R0 - 1, -(LUG_W + 2) / 2, BH_Z1 - 1)).rotated(V(0, 0, 0), V(0, 0, 1), LUG_ANG))
rep("%s windows clear of the staple lug (overlap %.4f mm3) and the thrust ring (window aft face Zf %.2f > ring top %.1f + 0.5)"
    % (ok(lug_zone.common(Part.makeCompound(WIN)).Volume < 1e-6 and CPN['Z_WIN_AFT'] + SHOULDER_Z > BH_Z1 + 0.5), lug_zone.common(Part.makeCompound(WIN)).Volume, CPN['Z_WIN_AFT'] + SHOULDER_Z, BH_Z1))
da, db = fc9_z.cut(fc8_z), fc8_z.cut(fc9_z)
bbs = [s.optimalBoundingBox() for s in da.Solids + db.Solids]
rep("%s fin can v9 vs v8 (coupler zone): +%.2f / -%.2f mm3, all within Zf %.2f..%.2f (pin slots + windows)"
    % (ok(min(b.ZMin for b in bbs) >= min(Z_PIN - 1, CPN['Z_WIN_AFT'] + SHOULDER_Z) - 0.01 and max(b.ZMax for b in bbs) <= zwm + 5), da.Volume, db.Volume, min(b.ZMin for b in bbs), max(b.ZMax for b in bbs)))

# --- function
v0 = tube9.common(fc9_z).Volume
v_lock = tube9.common(fc9_z.translated(V(0, 0, -0.6))).Volume
v_lock_nb = tube9_nb.common(fc9_z.translated(V(0, 0, -0.6))).Volume
rep("%s seated: tube x fin can %.4f mm3; pulled aft 0.6 -> bump/window %.3f mm3 (tube w/o bumps %.4f) = CATCHES" % (ok(v0 < 1e-3 and v_lock > 0.05 and v_lock_nb < 1e-3), v0, v_lock, v_lock_nb))
defl = tube9_nb.fuse([g['bump'].translated(pol(CPN['DELTA'], a, 0)) for g, a in zip(LG, LATCH_ANG)])
sw = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if defl.common(fc9_z.translated(V(0, 0, -d))).Volume > 1e-3]
rep("%s RELEASE = separation sweep 0..%.0f mm with the tongues deflected %.2f mm: clear %s" % (ok(not sw), CPL_LEN + 4, CPN['DELTA'], sw[:4] or ""))
vr = tube9.common(fc9_z.translated(V(0, 0, -(CPN['LB'] + 1.0)))).Volume
rep("%s negative control: undeflected bumps block the slide (%.2f mm3)" % (ok(vr > 0.05), vr))
clk = []
for d in (120.0, 180.0, 240.0):
    c = fc9_z.copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), d); clk.append((d, round(c.common(tube9).Volume, 2)))
rep("%s one clocking only: fin can turned %s deg -> bumps hit solid coupler wall %s mm3 = no click" % (ok(all(v > 0.05 for _, v in clk)), "/".join("%.0f" % d for d, _ in clk), [v for _, v in clk]))
bore = tube9.common(cyl(R_ID - 0.01, CPL_Z1 + 0.5, 400.0)).Volume
rep("%s chute bay forward of the coupler is a clean d40 bore (AftTube inside it %.4f mm3)" % (ok(bore < 1e-3), bore))
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, CPL_Z1 + 1.0)
rep("%s d%.0f gas column clear through the fin can (%.4f mm3)" % (ok(fc9_z.common(gp).Volume < 1e-3), 2 * PORT_R, fc9_z.common(gp).Volume))

# --- force / strain
Pn, e = beam(L_LATCH, CPN['E_RANGE'][1])
f_nom = 2 * Pn * fac(CPN['A_REL'], CPN['MU_RANGE'][1])
F_meas = COUPON_PULL['g'] * 9.81e-3
bay_v = math.pi * R_ID ** 2 * 150.0 / 1e3
bp_mg = (F_meas + FRICTION) / (math.pi * R_ID ** 2) * (bay_v * 1e3) / 219.0
rep("")
rep("LATCH FORCE (per pair): model %.1f N; coupon v1 L24 MEASURED %.0f g = %.1f N (one pull, x%.2f of the model)" % (f_nom, COUPON_PULL['g'], F_meas, F_meas / f_nom))
rep("%s hold %.1f N vs the %.1f N budget (all loads additive) = %.1fx; the latch slots vent the bay, so the %.1f N sealed-bay term mostly goes -> ~%.1fx"
    % (ok(F_meas >= HOLD_NEED), F_meas, HOLD_NEED, F_meas / HOLD_NEED, SEALED_TERM, F_meas / (HOLD_NEED - SEALED_TERM)))
rep("%s release %.1f N + ~%.0f N slide friction <= %.0f N budget; ideal black powder for that on the %.0f cm3 bay ~ %.0f mg (Klima D9 charge unpublished)"
    % (ok(F_meas + FRICTION <= RELEASE_BUDGET), F_meas, FRICTION, RELEASE_BUDGET, bay_v, bp_mg))
rep("%s tongue peak strain %.2f %% <= 1 %% (reusable, printed ABS, along the perimeters)" % (ok(e <= CPN['STRAIN_MAX']), e * 100))
rep("NOTE latches 120 deg apart (coupon 180): the coupler shifts ~0.2 mm in its slip fit -> ~0.1 mm less engagement (of 1.0) -> release a little lower than the coupon.")
rep("NOTE gas assist: bay pressure reaches the tongues through the windows / slip gap and pushes them OUT of the catch.")

# --- printability
def oriented(s, flip):
    s = s.copy()
    if flip: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
def down_faces(s, nz=-0.75):
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    pts = m.Points
    return [f for f in m.Facets if f.Normal.z < nz and min(pts[i].z for i in f.PointIndices) > 0.3]
o9, o8 = oriented(tube9, True), oriented(tube8, True)
a9, a8 = sum(f.Area for f in down_faces(o9)), sum(f.Area for f in down_faces(o8))
lat = 2 * (L_LATCH + CPN['GAP_END']) * (R_OD - R_ID)
rep("%s AftTube v9 printed forward end down: %.1f x %.1f x %.1f mm; down-facing area %.1f mm2 vs v8 %.1f (+%.1f; the 2 aft-gap bridges are ~%.0f)"
    % (ok(a9 - a8 <= lat * 1.3 and o9.BoundBox.ZLength <= 250), o9.BoundBox.XLength, o9.BoundBox.YLength, o9.BoundBox.ZLength, a9, a8, a9 - a8, lat))
f9z = oriented(fc9_z, False); f8z = oriented(fc8_z, False)
b9, b8 = sum(f.Area for f in down_faces(f9z)), sum(f.Area for f in down_faces(f8z))
rep("%s fin can v9 printed boss down: coupler-zone down-facing area %.1f vs v8 %.1f mm2 (windows have 45 deg ceilings: no new overhang)" % (ok(b9 <= b8 + 1.0), b9, b8))

# --- mass
dm_t = (tube9.Volume - tube8.Volume) * RHO_ABS
dm_f = (fc9_z.Volume - fc8_z.Volume) * RHO_ABS
rep("")
rep("MASS vs v8: AftTube %+.2f g, fin can %+.2f g, 2 pins -0.02 g -> %+.2f g, all at the aft end: CG / stability as v8" % (dm_t, dm_f, dm_t + dm_f - 0.02))
rep("")
rep("ASSEMBLY: pack, push the fin can in, turn it until it CLICKS (one clocking only). No click = do not fly.")
rep("  Do NOT tape over the tongues (they spring outward to release). Print the AftTube with dried ABS, wall line width 0.40.")
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT v9: %s (%d FAIL)  [%.0f s]" % ("ALL PASS" if not fails else "FAILURES", len(fails), time.time() - t9))

# =====================================================================================
# EXPORT (v9 names only)
# =====================================================================================
for k, s, flip in (("AftTube", tube9, True), ("AftFinCanSlotted", fc9, False)):
    s.exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME9, k)))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME9, k)))
    for d in (PRINT_READY, CURATED):
        MeshPart.meshFromShape(Shape=oriented(s, flip), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(d, "%s_%s.stl" % (NAME9, k)))
doc = App.newDocument("Phoenix_D9aft_v9")
for nm, s in (("AftTube_v9", tube9), ("AftFinCanSlotted_v9", fc9)):
    doc.addObject("Part::Feature", nm).Shape = s
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME9 + ".FCStd"))
with open(os.path.join(MODELS, NAME9 + "_report.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t9))

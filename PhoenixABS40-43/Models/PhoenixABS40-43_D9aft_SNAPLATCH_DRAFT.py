# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v7: PRINTED SNAP LATCH replaces the printed shear pins.

Why: the v1 shear pins (0.8 mm thick, 0.6 mm neck) do not print -- they come out as blobs (user, 2026-10-07).
The snap-latch coupon (Models/PhoenixABS40-43_SnapLatchCoupon_v1.py / _v2.py) was printed: L24 held
873 g = 8.6 N per pair on its first pull (model 12.1 N). The user asked to implement it without further
tests ("we can't afford to test right now").

Changes from v6 (v6 is exec'd read-only up to its checks; no earlier file is edited):
  AftTube   the 2 pin slots are FILLED (the exact slot volumes, clipped to the wall, are fused back) and
            2 L24 tongues are cut at 60 / 180 deg (= the old pin angles), with coupon v2's geometry
            (7 mm aft band, 1.0 aft gap, 0.8 end slot, 45 deg slanted forward edge, 1.2 mm tongue,
            bump 1.2 x 5 x 4.08, release 45 deg / entry 30 deg). Printed forward end down, as v6.
  fin can   the v4 slotted fin can (cfg B section + v1 make_fincan features) with its pin slots FILLED and
            2 coupler windows at 60 / 180 deg, matched 45 deg forward face (coupon v2 geometry, in the
            fin-can frame: tube aft face = the coupler shoulder, Zf %SHOULDER_Z).
  pins      gone (no ShearPin, no card, no pin coupon).
  unchanged nose v6, FwdTube v6, EbayCap v6, sled v6, fins v4, cap v1, body length, bay length.
  The latch angles are uneven (120 / 240 deg apart), so only one clocking of the fin can clicks in --
  the same one the pins allowed (fins clear of the launch-rod line).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame z = BODY_LEN - station (z = 0 is the fin-can aft face, as v1). Any FAIL line means do not print.
"""
import os, math, time
t7 = time.time()
_M = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models"
V6_SRC = os.path.join(_M, "PhoenixABS40-43_D9aft_v6.py")
CPN1_SRC = os.path.join(_M, "PhoenixABS40-43_SnapLatchCoupon_v1.py")
CPN2_PATCH = [("BAND_AFT = 4.0 ", "BAND_AFT = 7.0 ")]          # = coupon v2 (the geometry the user printed last)

# ---------------- v6 geometry (chain v1 -> v2 -> v3 -> v5 -> v6), stopped before v6's checks
_v6 = open(V6_SRC, encoding="utf-8").read()
_c6 = _v6.index("\n# CHECKS\n"); _c6 = _v6.rfind("# ====", 0, _c6)
exec(_v6[:_c6])
print("v6 geometry in %.1f s" % (time.time() - t7), flush=True)

# ---------------- coupon latch geometry, in its own namespace (it redefines pol/rev/report/... )
_cs = open(CPN1_SRC, encoding="utf-8").read()
for _a, _b in CPN2_PATCH:
    assert _cs.count(_a) == 1, _a
    _cs = _cs.replace(_a, _b)
_cb = _cs.index("\n# BUILD\n"); _cb = _cs.rfind("# ====", 0, _cb)
CPN = {}
exec(compile(_cs[:_cb], CPN1_SRC + " [coupon v2 params]", "exec"), CPN)
assert CPN['BAND_AFT'] == 7.0
for k in ('R_OD', 'R_ID', 'CPL_R_O', 'CPL_R_I'):
    assert abs(CPN[k] - globals()[k]) < 1e-9, "coupon wall %s differs from the flight wall" % k

def _beam(L, E, n=800):
    """coupon v1 beam(): curved, tapered cantilever, radial tip load at the bump (same formula)."""
    sb = L - CPN['S_B_OFF']; ds = sb / n; J = 0.0; arr = []
    for i in range(n):
        s_ = (i + 0.5) * ds
        I = (CPN['W_TIP'] + (L - s_) * CPN['TAPER']) * CPN['T_TONGUE'] ** 3 / 12
        m = CPN['R_T'] * math.sin((sb - s_) / CPN['R_T'])
        J += m * m / (E * I) * ds; arr.append((m, I))
    Pn = CPN['DELTA'] / J
    return Pn, max(Pn * m * (CPN['T_TONGUE'] / 2) / (E * I) for m, I in arr)
def _fac(a, mu):
    ta = math.tan(math.radians(a)); return (ta + mu) / (1 - mu * ta)
CPN['beam'], CPN['fac'] = _beam, _fac
def oriented6(s, flip):
    s = s.copy()
    if flip: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s

NAME7, REV7 = "PhoenixABS40-43_D9aft_v7", "D9aft_v7"
report = []
L_LATCH = 24.0
LATCH_ANG = tuple(PIN_ANG)                            # 60 / 180: the old pin angles (fin gaps, one clocking)
Z_TUBE_AFT = zs(ST_BODY_AFT)                          # tube aft face = coupon frame z 0
assert abs(Z_TUBE_AFT - SHOULDER_Z) < 1e-6, (Z_TUBE_AFT, SHOULDER_Z)
DZ = V(0, 0, Z_TUBE_AFT)
COUPON_PULL = dict(g=873.0, N=873.0 * 9.81e-3, model=12.1)     # v1 L24, first pull (aft band curled: may include rub)
SECTION_STEP = os.path.join(MODELS, "PhoenixABS40-43_AftSectionSealed_v1.step")

def pin_fill(r0, r1, a):
    """Exactly the material a pin slot removed from a wall r0..r1 (fused back = slot gone)."""
    return pin_slot(a, Z_PIN).common(cyl(r1, Z_PIN - 5, Z_PIN + 5).cut(cyl(r0, Z_PIN - 6, Z_PIN + 6)))

# ---------------- AftTube v7
LG = [CPN['latch_geom'](L_LATCH, a) for a in LATCH_ANG]
for g in LG:
    for k in ('tongue', 'cut', 'bump'): g[k] = g[k].translated(DZ)
at7 = P3['AftTube']
for a in PIN_ANG: at7 = at7.fuse(pin_fill(R_ID, R_OD, a))
for g in LG: at7 = at7.cut(g['cut'])
for g in LG: at7 = at7.fuse(g['tongue'])
at7_nb = at7.removeSplitter()
for g in LG: at7 = at7.fuse(g['bump'])
at7 = at7.removeSplitter()

# ---------------- fin can v7 (v4 slotted, pins filled, windows)
def window(a):
    hw = CPN['deg'](CPN['BUMP_S'] / 2 / CPN['R_ID']) + CPN['deg'](CPN['CLR_TAN'] / CPN['CPL_R_O'])
    r0, r1 = CPL_R_I - 0.3, R_ID
    zf, za = CPN['z_win_fwd'], CPN['Z_WIN_AFT']
    return CPN['rev']([(r0, za + Z_TUBE_AFT), (r1, za + Z_TUBE_AFT), (r1, zf(r1) + Z_TUBE_AFT), (r0, zf(r0) + Z_TUBE_AFT)], a - hw, a + hw)
WIN = [window(a) for a in LATCH_ANG]
def make_fincan7(base):
    s = make_fincan(base)                             # v1 features incl. the pin slots ...
    for a in PIN_ANG: s = s.fuse(pin_fill(CPL_R_I, CPL_R_O, a))   # ... which are filled again
    for w in WIN: s = s.cut(w)
    return AR['as_solid'](s)
sec_v1 = Part.Shape(); sec_v1.read(SECTION_STEP)
sec_v1 = sec_v1.Solids[0] if len(sec_v1.Solids) == 1 else sec_v1
fc7 = make_fincan7(sec_v1)
fc7_px = make_fincan7(AR['build_sealed_section'](slots=True))
fc4_px = make_fincan(AR['build_sealed_section'](slots=True))   # v4 proxy, for the mass delta
print("v7 parts in %.1f s" % (time.time() - t7), flush=True)

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: printed SNAP LATCH (coupon v2, L24) replaces the shear pins; everything else v6 ==" % REV7)
rep("Frame z = %.1f - station; latch geometry = coupon v2 shifted by Zf %.1f (tube aft face on the fin-can shoulder)." % (BODY_LEN, Z_TUBE_AFT))
rep("")
for k, s in (('AftTube v7', at7), ('AftFinCanSlotted v7', fc7), ('AftFinCanSlotted v7 proxy', fc7_px)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))

# --- AftTube: pins gone, latches present
pol_ = CPN['pol']
pr = []
for a in PIN_ANG:
    pr += [("old pin slot %.0f filled (tube)" % a, pol(R_ID + 0.75, a, Z_PIN), True)]
for g, a in zip(LG, LATCH_ANG):
    tt, tr = g['th_tip'], g['th_root']; thm = (tt + tr) / 2
    zt = CPN['Z_TAFT'] + Z_TUBE_AFT
    z_edge = zt + CPN['W_TIP'] + (thm - tt) * math.radians(1) * CPN['R_T']
    pr += [("%.0f: end slot open" % a, pol_(CPN['R_T'], tt - CPN['deg'](CPN['GAP_END'] / 2 / CPN['R_T']), zt + 2), False),
           ("%.0f: aft gap open" % a, pol_(CPN['R_T'], thm, zt - CPN['GAP_AFT'] / 2), False),
           ("%.0f: slant gap open" % a, pol_(CPN['R_T'], thm, z_edge + CPN['GAP_FWD'] / 2), False),
           ("%.0f: tongue present" % a, pol_(CPN['R_T'], thm, (zt + z_edge) / 2), True),
           ("%.0f: tongue skin recessed" % a, pol_((CPN['R_TO'] + R_OD) / 2, thm, (zt + z_edge) / 2), False),
           ("%.0f: aft band present" % a, pol_(CPN['R_T'], thm, Z_TUBE_AFT + CPN['BAND_AFT'] / 2), True),
           ("%.0f: tongue joined at the root" % a, pol_(CPN['R_T'], tr + 0.5, zt + 3), True),
           ("%.0f: bump present" % a, pol_(R_ID - CPN['BUMP_H'] / 2, a, CPN['E0'] + CPN['L_ENT'] + CPN['BUMP_FLAT'] / 2 + Z_TUBE_AFT), True)]
pr += [("launch lug present", pol(LL_C + LL_RO - 0.3, LL_ANG, zs((LL_ST0 + LL_ST1) / 2)), True),
       ("launch lug bore open", pol(LL_C, LL_ANG, zs((LL_ST0 + LL_ST1) / 2)), False)]
bad = [(n, w) for n, p, w in pr if inside(at7, p) != w]
rep("%s AftTube v7 probes %d/%d as designed%s" % (ok(not bad), len(pr) - len(bad), len(pr), "; WRONG %s" % bad if bad else ""))
dv_tube = at7.Volume - P3['AftTube'].Volume
rep("NOTE AftTube v7 %.1f mm3 vs v6 %.1f mm3 (%+.1f: latch slots + skin recess, pin slots back)" % (at7.Volume, P3['AftTube'].Volume, dv_tube))
foot = (CPN['Z_TAFT'] - CPN['GAP_AFT'] + Z_TUBE_AFT, CPN['Z_TAFT'] + CPN['W_TIP'] + L_LATCH + CPN['GAP_FWD'] + Z_TUBE_AFT)
rep("%s latch footprint Zf %.1f..%.1f lies inside the coupler (shoulder %.1f .. front %.1f): every slot is backed by the coupler wall"
    % (ok(foot[0] >= SHOULDER_Z and foot[1] <= CPL_Z1 - 0.5), foot[0], foot[1], SHOULDER_Z, CPL_Z1))
ll_z0 = min(zs(LL_ST0), zs(LL_ST1))
rep("%s latches clear of the launch lug (lug from Zf %.1f, latch to %.1f) and the AftTube harness lug (forward end)" % (ok(ll_z0 > foot[1] + 5), ll_z0, foot[1]))

# --- fin can: pins gone, windows present, everything else as v4
fp = []
for a in PIN_ANG:
    fp += [("old pin slot %.0f filled (coupler)" % a, pol(19.15, a, Z_PIN), True)]
zwm = (CPN['Z_WIN_AFT'] + CPN['z_win_fwd'](19.15)) / 2 + Z_TUBE_AFT
for a in LATCH_ANG:
    fp += [("window %.0f open" % a, pol(19.15, a, zwm), False), ("coupler wall beside window %.0f" % a, pol(19.15, a + 15, zwm), True)]
fp += [("gas port open on the axis", V(0, 0, (BH_Z0 + BH_Z1) / 2), False),
       ("thrust-ring annulus solid", pol(14.0, 60, (BH_Z0 + BH_Z1) / 2), True),
       ("harness lug present", pol(13.2, ANCH_FC['ang'], ANCH_FC['z1'] - 0.5), True),
       ("harness lug hole open", pol(ANCH_HOLE_R, ANCH_FC['ang'], ANCH_FC['zh']), False),
       ("coupler OD trimmed", pol(19.83, 30, SHOULDER_Z + 3.0), False),
       ("shoulder full OD", pol(21.3, 30, SHOULDER_Z - 0.3), True)]
zm = (AR['FIN_Z0'] + AR['FIN_Z1']) / 2
fp += [("fin slot %.0f open" % a, pol(20.75, a, zm), False) for a in AR['FIN_ANGLES']]
bad = [(n, w) for n, p, w in fp if inside(fc7, p) != w]
badp = [(n, w) for n, p, w in fp if inside(fc7_px, p) != w]
rep("%s REAL fin can v7: %d/%d probes%s" % (ok(not bad), len(fp) - len(bad), len(fp), "; WRONG %s" % bad if bad else ""))
rep("%s proxy fin can v7: %d/%d probes%s" % (ok(not badp), len(fp) - len(badp), len(fp), "; WRONG %s" % badp if badp else ""))
lug_hit = FC_LUG.common(Part.makeCompound(WIN)).Volume
rep("%s windows clear of the harness lug (%.0f deg) and the thrust ring (window aft face Zf %.2f vs ring top %.1f): lug overlap %.4f mm3"
    % (ok(lug_hit < 1e-6 and CPN['Z_WIN_AFT'] + Z_TUBE_AFT > BH_Z1 + 0.5), ANCH_FC['ang'], CPN['Z_WIN_AFT'] + Z_TUBE_AFT, BH_Z1, lug_hit))

# --- function: seat, catch, release (= separation), clocking
v0 = at7.common(fc7_px).Volume
v_lock = at7.common(fc7_px.translated(V(0, 0, -0.6))).Volume
v_lock_nb = at7_nb.common(fc7_px.translated(V(0, 0, -0.6))).Volume
rep("%s seated: tube x fin can %.4f mm3; pulled aft 0.6 mm -> bump/window %.3f mm3 (tube w/o bumps %.4f) = CATCHES"
    % (ok(v0 < 1e-3 and v_lock > 0.05 and v_lock_nb < 1e-3), v0, v_lock, v_lock_nb))
DELTA = CPN['DELTA']
defl = at7_nb.fuse([g['bump'].translated(pol_(DELTA, a, 0)) for g, a in zip(LG, LATCH_ANG)])
sw = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if defl.common(fc7_px.translated(V(0, 0, -d))).Volume > 1e-3]
rep("%s RELEASE = separation sweep 0..%.0f mm with the tongues deflected %.2f mm: fin can never touches the AftTube %s"
    % (ok(not sw), CPL_LEN + 4, DELTA, sw[:4] or ""))
vr = at7.common(fc7_px.translated(V(0, 0, -(CPN['LB'] + 1.0)))).Volume
rep("%s negative control: undeflected bumps block the slide (%.2f mm3 at %.1f mm aft)" % (ok(vr > 0.05), vr, CPN['LB'] + 1.0))
clk = []
for d in (120.0, 180.0, 240.0):
    c = fc7_px.copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), d); clk.append((d, round(c.common(at7).Volume, 2)))
rep("%s one clocking only: fin can turned %s deg -> bumps land on solid coupler wall (overlap %s mm3 > 0) = it will NOT click"
    % (ok(all(v > 0.05 for _, v in clk)), "/".join("%.0f" % d for d, _ in clk), [v for _, v in clk]))
air7 = dict(nose=nose6_px, fwd=fw_px3, aft=at7, fincan=fc7_px, motor=motor, **air_e)
bad = interference(air7, {('nose', 'fwd'), ('nose', 'ebaycap'), ('sled', 'env_SmallParts'), ('ebaycap', 'fwd')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)})
rep("%s interference, flight (v7 tube + v7 fin can proxy + v6 forward parts): %s" % (ok(not bad), bad or "none"))
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, z_b - 0.5)
hits = [k for k, s in dict(fincan=fc7_px, aft=at7, fwd=fw_px3).items() if s.common(gp).Volume > 1e-3]
rep("%s d%.0f gas column clear from the motor face to the bulkhead: %s" % (ok(not hits), 2 * PORT_R, hits or "clear"))
rod_in = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=LL_C - (LL_RI - ROD_R)), LL_ANG)
FINS = [AR['build_fin'](a) for a in AR['FIN_ANGLES']]
hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod_in).Volume) for k, sh in dict(fincan=fc7_px, aft_tongue_bumps=at7.common(cyl(R_OD + 0.5, foot[0] - 1, foot[1] + 1)), **{"fin_%d" % i: f for i, f in enumerate(FINS)}).items()) if v > 1e-3]
rep("%s launch rod line clear of the fin can, fins and latch zone: %s" % (ok(not hits), hits or "clear"))
rep("%s chute bay still a clean d40 bore forward of the coupler (bumps sit inside the coupler zone only): AftTube in the bore %.4f mm3"
    % (ok(at7.common(cyl(R_ID - 0.01, CPL_Z1 + 0.5, z_b)).Volume < 1e-3), at7.common(cyl(R_ID - 0.01, CPL_Z1 + 0.5, z_b)).Volume))

# --- force (coupon-calibrated), strain
Pn, e = CPN['beam'](L_LATCH, CPN['E_RANGE'][1])
f_nom = 2 * Pn * CPN['fac'](CPN['A_REL'], CPN['MU_RANGE'][1])
cal = COUPON_PULL['N'] / COUPON_PULL['model']
rep("")
rep("LATCH FORCE (per pair)")
rep("  model %.1f N (E 2.0 GPa, mu 0.35); coupon v1 L24 MEASURED %.0f g = %.1f N on one pull (x%.2f of the model; the curled aft band may have added rub)"
    % (f_nom, COUPON_PULL['g'], COUPON_PULL['N'], cal))
rep("%s hold: %.1f N measured vs %.1f N budget (all loads additive) = %.1fx; the latch slots vent the bay, so the 2.6 N sealed-bay term mostly goes -> ~%.1fx"
    % (ok(COUPON_PULL['N'] >= CPN['HOLD_NEED']), COUPON_PULL['N'], CPN['HOLD_NEED'], COUPON_PULL['N'] / CPN['HOLD_NEED'], COUPON_PULL['N'] / (CPN['HOLD_NEED'] - 2.6)))
rep("%s release: %.1f N + ~3 N slide friction vs the 24 N budget; ideal black powder for 12 N on the %.0f cm3 bay ~ %.0f mg (D-class ejection charges are typically 100+ mg -- Klima unpublished)"
    % (ok(COUPON_PULL['N'] + 3.0 <= 24.0), COUPON_PULL['N'], math.pi * R_ID ** 2 * (BAY1 - BAY0) / 1e3, 12.0 / (math.pi * R_ID ** 2) * (math.pi * R_ID ** 2 * (BAY1 - BAY0)) / 219.0))
rep("%s tongue peak strain %.2f %% (<= 1 %%, reusable printed ABS)" % (ok(e <= CPN['STRAIN_MAX']), e * 100))
rep("NOTE flight latches are 120 deg apart (coupon: 180): the bump loads push the coupler ~0.2 mm sideways in its slip fit,"
    " ~0.1 mm less engagement per bump (of 1.0) -> expect a slightly lower release than the coupon.")

# --- printability
o = oriented6(at7, True); bb = o.BoundBox
oh = overhangs(o)
big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
rep("%s AftTube v7 printed forward end down: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d wide%s -- the aft band bridges the 1.0 mm aft gap (as coupon v2)"
    % (ok(not big and bb.ZLength <= BED[2]), bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
       ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
def drop(s):
    s = s.copy(); bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
o = drop(fc7_px); oh7 = overhangs(o); oh4 = overhangs(drop(fc4_px))
big7 = [c for c in oh7 if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
big4 = [c for c in oh4 if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
rep("%s fin can v7 (proxy) printed boss down: %d wide overhang patches vs v4's %d (the v4 annular bridges; the windows add none -- 45 deg ceilings)"
    % (ok(len(big7) <= len(big4)), len(big7), len(big4)))

# =====================================================================================
# MASS / CG delta vs v6
# =====================================================================================
dm_tube = dv_tube * RHO['ABS']
dm_fc = (fc7_px.Volume - fc4_px.Volume) * RHO['ABS']
dm_pins = -sum(p.Volume for p in PINS.values()) * RHO['ABS']
rep("")
rep("MASS vs v6: AftTube %+.2f g, fin can %+.2f g, pins %+.2f g -> %+.2f g total, all within %.0f mm of the aft end: CG/stability unchanged"
    % (dm_tube, dm_fc, dm_pins, dm_tube + dm_fc + dm_pins, CPL_Z1))
rep("NOTE stability gate from v6 still applies: balance the built rocket at 226 mm from the tip or forward, else 3-4 g EbayCap ballast.")
rep("")
rep("ASSEMBLY: pack, then push the fin can in with its windows on the bumps (fins in the launch-lug gap, as with the pins): it CLICKS.")
rep("  No click = wrong clocking -> do not fly. Do NOT tape over the tongues (they must spring outward); tape on the joint seam is fine.")
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)  [%.0f s]" % ("ALL PASS" if not fails else "FAILURES", len(fails), time.time() - t7))

# =====================================================================================
# EXPORT
# =====================================================================================
at7.exportStep(os.path.join(MODELS, NAME7 + "_AftTube.step"))
fc7.exportStep(os.path.join(MODELS, NAME7 + "_AftFinCanSlotted.step"))
MeshPart.meshFromShape(Shape=at7, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, NAME7 + "_AftTube.stl"))
MeshPart.meshFromShape(Shape=oriented6(at7, True), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME7 + "_AftTube.stl"))
MeshPart.meshFromShape(Shape=fc7, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, NAME7 + "_AftFinCanSlotted.stl"))
MeshPart.meshFromShape(Shape=drop(fc7), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME7 + "_AftFinCanSlotted.stl"))
doc = App.newDocument("Phoenix_D9aft_v7")
for nm, s in (("AftTube_v7", at7), ("AftFinCanSlotted_v7", fc7), ("FwdTube_v6", P3['FwdTube']), ("EbayCap_v6", P3['EbayCap']),
              ("Sled_v6", sled2), ("Nose_v6", nose6), ("MotorRetainerCap_v1", cap), ("D9_motor", motor)):
    o = doc.addObject("Part::Feature", nm); o.Shape = s
for i, f in enumerate(FINS): doc.addObject("Part::Feature", "Fin_%d" % i).Shape = f
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME7 + ".FCStd"))
with open(os.path.join(MODELS, NAME7 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t7))

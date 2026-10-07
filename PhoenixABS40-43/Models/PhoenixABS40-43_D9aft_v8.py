# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v8: v7 + both recovery anchors sized for a 5 mm RETENTION LINE, tied direct.

User, 2026-10-07: "The retention line needs 5 mm in diameter"; asked where it must pass -> "Both anchors
directly" (no Kevlar leaders at the anchors).

v7's anchors could not take it: the bulkhead eyelet tunnel was 3.5 x 5 mm (windows 5 x 5), the fin-can harness
lug a d3.5 hole in a lug only 6 mm radial (r 12.5 motor-side limit .. 18.5 coupler ID).

  FwdTube   bulkhead EYELET (v2 recipe, constants only): every opening the line passes is OPEN x OPEN (6.5 mm,
            line 5.0 + 1.5): windows 6.5 x 6.5, tunnel 6.5 high x 6.5 wide over the bar.  Bar 7 x 3.5 (was
            6 x 3) so the longer 6.5 span still bends < 20 MPa at the 250 N placeholder.  Boss 24 x 10.5 x 13
            (roof 3.0 as v2).  Still blind (gas-tight), still printed bar-on-the-bed, roof bridges 6.5.
  fin can   STAPLE LUG at 300 deg replaces v1's d3.5 lug: a 9 mm-wide (tangential) block on the thrust-ring
            face, r 8.5 (0.3 off the casing-rim ledge) .. coupler wall, with a 6.5 x 6.5 tangential opening
            whose floor is the ring face and whose roof is a 45 deg peak (prints boss-down, no support).
            The outer leg is the coupler wall itself in every layer.  Built by v1's make_fincan() -- so
            the flight-stack proxy AND the real slotted fin can (v4 recipe, rebuilt here) both carry it.
  unchanged AftTube, EbayCap, sled v7, nose v6, fins, pins, cap (asserted against the v7 STEPs).

Mass: the 5 mm line is a new point mass (ASSUMED g/m below -- weigh it) packed aft of the canopy.

v1..v7 are NOT edited: v1 (lug) and v2 (eyelet constants) are patched as they are read, through a
module-level open() hook; v7 is exec'd with its names moved to v8 and two blocks added to the v6 recipe.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Any FAIL line means do not print.
"""
import os, io, builtins
_MD = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models"
V1_SRC8 = os.path.join(_MD, "PhoenixABS40-43_D9aft_v1.py")
V2_SRC8 = os.path.join(_MD, "PhoenixABS40-43_D9aft_v2.py")
V7_SRC8 = os.path.join(_MD, "PhoenixABS40-43_D9aft_v7.py")

# ---------------- the line
CORD_D = 5.0                      # user, 2026-10-07
CORD_OPEN = 6.5                   # every opening the line passes (5.0 + 1.5: braid, knot tail, threading)
CORD_PROBE_D = 5.3                # swept test body: the line + 0.15 per side
LINE_G_PER_M = 12.0               # ASSUMED (5 mm braid) -- weigh the real line and replace
LINE_LEN_M = 1.5                  # ASSUMED: DESIGN 5.2 shock cord >= 1.2 m + the length the leaders were
LINE_G = LINE_G_PER_M * LINE_LEN_M
LINE_PACK_OFF = 90.0              # line CG this far aft of the bulkhead (canopy forward at +45, then the line)
CG_GATE_TIP = 226.0               # v6 balance gate (mm from the tip)
MM_PER_G = 0.6                    # v6: ~0.6 mm forward per g of EbayCap ballast

# ---------------- eyelet (v2 constants, re-derived)
EY_BAR8 = (3.5, 3.5)                                                      # half-x 3.5 (7 wide), 3.5 thick
EY_POCKET8 = (EY_BAR8[0] + CORD_OPEN, CORD_OPEN / 2, EY_BAR8[1] + CORD_OPEN)   # windows / tunnel width / tunnel height = OPEN
EY_BOSS8 = (EY_POCKET8[0] + 2.0, EY_POCKET8[1] + 2.0, EY_POCKET8[2] + 3.0)    # 2 mm walls, 3 mm roof (as v2)
V2_PATCHES8 = [
    ("EY_POCKET = (8.0, 2.5, 6.5)", "EY_POCKET = EY_POCKET8"),
    ("EY_BAR = (3.0, 3.0)", "EY_BAR = EY_BAR8"),
    ("EY_BOSS = (10.0, 4.5, 9.5)", "EY_BOSS = EY_BOSS8"),
]

# ---------------- fin-can staple lug (replaces v1 FC_LUG)
LUG8 = dict(ang=300.0, w=9.0, r0=8.5, oa=10.8, ob=10.8 + CORD_OPEN, side=CORD_OPEN, top=3.0)
V1_LUG8 = r'''
def staple_lug8():
    """Thrust-ring staple: block r0..coupler wall, 9 tangential; 6.5 x 6.5 tangential opening, ring-face floor, 45 deg roof."""
    L = LUG8
    peak = BH_Z1 + L['side'] + (L['ob'] - L['oa']) / 2
    blk = box(L['r0'], CPL_R_I + 0.5, -L['w'] / 2, L['w'] / 2, BH_Z1 - 0.2, peak + L['top'])
    pts = [V(L['oa'], -L['w'] / 2 - 1, BH_Z1), V(L['ob'], -L['w'] / 2 - 1, BH_Z1), V(L['ob'], -L['w'] / 2 - 1, BH_Z1 + L['side']),
           V((L['oa'] + L['ob']) / 2, -L['w'] / 2 - 1, peak), V(L['oa'], -L['w'] / 2 - 1, BH_Z1 + L['side'])]
    hole = Part.Face(Part.Wire(Part.makePolygon(pts + [pts[0]]))).extrude(V(0, L['w'] + 2, 0))
    return rot(blk.cut(hole), L['ang'])
FC_LUG = staple_lug8()
'''
def _v8_v1(src):
    i = src.index("FC_LUG = anchor_lug(ANCH_FC['ang']")
    j = src.index("\n", src.index("\n", i) + 1)
    assert src.count("FC_LUG = anchor_lug(") == 1 and src[i:j].rstrip().endswith("ANCH_HOLE_R, ANCH_FC['zh'])"), "v1 FC_LUG target moved"
    return src[:i] + V1_LUG8.strip() + src[j:]
def _v8_v2(src):
    for a, b in V2_PATCHES8:
        assert src.count(a) == 1, "v2 patch target not unique: %r" % a
        src = src.replace(a, b)
    return src
_HOOK8 = {os.path.normcase(V1_SRC8): _v8_v1, os.path.normcase(V2_SRC8): _v8_v2}
_HOOK8_HITS = []
def open(p, *a, **k):                                 # shadows the builtin for the exec'd chain (same globals)
    f = _HOOK8.get(os.path.normcase(os.path.abspath(str(p)))) if not a or a[0] in ("r", "rt") else None
    if f is None:
        return builtins.open(p, *a, **k)
    _HOOK8_HITS.append(os.path.basename(str(p)))
    with builtins.open(p, encoding="utf-8") as fh:
        return io.StringIO(f(fh.read()))

# =====================================================================================
# v6 recipe additions (applied before v7's own v6 patches)
# =====================================================================================
_MID8 = r'''
# =====================================================================================
# v8: 5 mm RETENTION LINE -- bulkhead eyelet + fin-can staple lug + the real slotted fin can
# =====================================================================================
rep("")
rep("V8 CHECKS: 5 mm RETENTION LINE, tied direct to both anchors (opening %.1f, probe line d%.1f)" % (CORD_OPEN, CORD_PROBE_D))
rep("%s v1 + v2 patched on read: %s" % (ok(sorted(set(_HOOK8_HITS)) == ["PhoenixABS40-43_D9aft_v1.py", "PhoenixABS40-43_D9aft_v2.py"]), sorted(set(_HOOK8_HITS))))
CR8 = CORD_PROBE_D / 2
def line_path8(pts):
    """Swept line: d CORD_PROBE_D along a polyline (sphere joints = the tightest real bend)."""
    s = None
    for a, b in zip(pts[:-1], pts[1:]):
        c = Part.makeCylinder(CR8, (b - a).Length, a, (b - a).normalize())
        s = c if s is None else s.fuse(c)
    for p in pts[1:-1]:
        s = s.fuse(Part.makeSphere(CR8, p))
    return s

# --- bulkhead eyelet
win, tw, th = EY_POCKET[0] - EY_BAR[0], 2 * EY_POCKET[1], EY_POCKET[2] - EY_BAR[1]
rep("%s eyelet openings: windows %.1f x %.1f, tunnel %.1f wide x %.1f high over a %.1f x %.1f bar (all >= %.1f for the d%.1f line; v7 5 x 5 / 3.5 x 5)"
    % (ok(min(win, tw, th) >= CORD_OPEN - 1e-9), win, tw, tw, th, 2 * EY_BAR[0], EY_BAR[1], CORD_OPEN, CORD_D))
xw, zt = EY_BAR[0] + win / 2, z_b + EY_BAR[1] + th / 2
EY_LINE = line_path8([V(-xw, 0, z_b - 8.0), V(-xw, 0, zt), V(xw, 0, zt), V(xw, 0, z_b - 8.0)])
ey_px = fw_px3.common(EY_LINE).Volume
ey_re = P3['FwdTube'].common(EY_LINE).Volume
_fw7 = Part.Shape(); _fw7.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v7_FwdTube.step"))
ey_neg = _fw7.common(EY_LINE).Volume
rep("%s line threads the eyelet (down a window, over the bar, out the other): clash proxy %.4f / REAL %.4f mm3; NEGATIVE CONTROL v7 FwdTube %.1f mm3 (must be > 1)"
    % (ok(ey_px < 1e-3 and ey_re < 1e-3 and ey_neg > 1.0), ey_px, ey_re, ey_neg))
ep8 = [("bar solid", V(0, 0, z_b + EY_BAR[1] / 2), True), ("tunnel open over the bar", V(0, 0, zt), False),
       ("window open -x", V(-xw, 0, z_b + 1.0), False), ("window open +x", V(xw, 0, z_b + 1.0), False),
       ("pocket roof solid", V(0, 0, z_b + EY_POCKET[2] + 1.5), True), ("boss side wall solid", V(0, EY_POCKET[1] + 1.0, zt), True),
       ("bulkhead plate solid beside the boss", V(EY_BOSS[0] + 2.0, 0, z_b + 1.0), True)]
bad = [(n, w) for n, p, w in ep8 if inside(P3['FwdTube'], p) != w]
rep("%s REAL FwdTube eyelet probes %d/%d%s" % (ok(not bad), len(ep8) - len(bad), len(ep8), "; WRONG %s" % bad if bad else ""))
sig_e = SNATCH_N * tw / 8.0 / ((2 * EY_BAR[0]) * EY_BAR[1] ** 2 / 6.0)
rep("%s eyelet bar at the %.0f N placeholder: %.0f x %.1f bar over %.1f mm, fixed-fixed bending %.1f MPa (< 20; in-layer: printed flat on the bed); bearing %.1f MPa"
    % (ok(sig_e < 20.0), SNATCH_N, 2 * EY_BAR[0], EY_BAR[1], tw, sig_e, SNATCH_N / (CORD_D * 2 * EY_BAR[0])))
bc = math.hypot(EY_BOSS[0], EY_BOSS[1])
st_boss = S_BH2 - EY_BOSS[2]
rep("%s eyelet boss %.0f x %.1f x %.0f: corner r %.2f inside the spigot bore r %.2f; forward end st %.1f is %.1f mm aft of the e-bay's aft-most point (st %.1f), roof %.1f"
    % (ok(bc <= SPIGOT_RI - 1.0 and st_boss - e_last >= 2.0), 2 * EY_BOSS[0], 2 * EY_BOSS[1], EY_BOSS[2], bc, SPIGOT_RI, st_boss, st_boss - e_last, e_last, EY_BOSS[2] - EY_POCKET[2]))

# --- fin-can staple lug, real slotted fin can (v4 recipe on the new make_fincan)
def overhangs8(s, nz_lim=-0.75):
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    pts = m.Points
    fl = [f for f in m.Facets if f.Normal.z < nz_lim and min(pts[i].z for i in f.PointIndices) > 0.3]
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for f in fl:
        for i in f.PointIndices[1:]: parent[find(i)] = find(f.PointIndices[0])
    comp = {}
    for f in fl: comp.setdefault(find(f.PointIndices[0]), []).append(f)
    out = []
    for fs in comp.values():
        ps = [pts[i] for f in fs for i in f.PointIndices]
        xs, ys, zz = [p.x for p in ps], [p.y for p in ps], [p.z for p in ps]
        rs = [math.hypot(p.x, p.y) for p in ps]
        a = sum(f.Area for f in fs)
        out.append(dict(area=a, z=(min(zz) + max(zz)) / 2, span=min(max(xs) - min(xs), max(ys) - min(ys)), ledge=a / (math.pi * (min(rs) + max(rs))), r0=min(rs), r1=max(rs)))
    return out
t8 = time.time()
sec_v1 = Part.Shape(); sec_v1.read(os.path.join(MODELS, "PhoenixABS40-43_AftSectionSealed_v1.step"))
sec_v1 = sec_v1.Solids[0] if len(sec_v1.Solids) == 1 else sec_v1
sec_px_v1 = AR['build_sealed_section'](slots=True)
fcB = make_fincan(sec_v1)
fcB_px = make_fincan(sec_px_v1)
AR['FIN_TAB_R'] = AR['FIN_SLOT_R_I'] + 0.1           # v4
FINS8 = [AR['build_fin'](a) for a in AR['FIN_ANGLES']]
print("v8 slotted fin can in %.1f s" % (time.time() - t8), flush=True)
for k, s in (('AftFinCanSlotted v8', fcB), ('AftFinCanSlotted v8 proxy', fcB_px)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))
L8 = LUG8
rc8 = (L8['oa'] + L8['ob']) / 2
peak8 = BH_Z1 + L8['side'] + (L8['ob'] - L8['oa']) / 2
zc8 = BH_Z1 + L8['side'] / 2
lp8 = [("lug top solid", pol(rc8, L8['ang'], peak8 + L8['top'] / 2), True),
       ("opening open (line centre)", pol(rc8, L8['ang'], zc8), False),
       ("opening open under the 45 deg peak", pol(rc8, L8['ang'], peak8 - 1.0), False),
       ("inner leg solid", pol((L8['r0'] + L8['oa']) / 2, L8['ang'], zc8), True),
       ("outer leg solid", pol((L8['ob'] + CPL_R_I) / 2, L8['ang'], zc8), True),
       ("ring face = opening floor, solid", pol(rc8, L8['ang'], BH_Z1 - 1.0), True),
       ("v1 lug hole position now inside the opening", pol(ANCH_HOLE_R, ANCH_FC['ang'], ANCH_FC['zh'] - 1.0), False),
       ("gas port open on the axis", V(0, 0, (BH_Z0 + BH_Z1) / 2), False),
       ("casing-rim ledge present r 8.7", pol(8.7, 30, BH_Z0 + 0.5), True),
       ("coupler wall mid-length", pol(19.15, 30, (BH_Z1 + CPL_Z1) / 2), True),
       ("thrust-ring annulus solid", pol(14.0, 60, (BH_Z0 + BH_Z1) / 2), True)]
lp8 += [("pin slot %d open" % i, pol(19.15, a, Z_PIN), False) for i, a in enumerate(PIN_ANG)]
zm8 = (AR['FIN_Z0'] + AR['FIN_Z1']) / 2
lp8 += [("fin slot %.0f open through the wall" % a, pol(20.75, a, zm8), False) for a in AR['FIN_ANGLES']]
bad = [(n, w) for n, p, w in lp8 if inside(fcB, p) != w]
badp = [(n, w) for n, p, w in lp8 if inside(fcB_px, p) != w]
rep("%s REAL slotted fin can v8: %d/%d probes (staple lug + v4 features)%s" % (ok(not bad), len(lp8) - len(bad), len(lp8), "; WRONG %s" % bad if bad else ""))
rep("%s proxy: %d/%d same probes%s" % (ok(not badp), len(lp8) - len(badp), len(lp8), "; WRONG %s" % badp if badp else ""))
dv, dvp = fcB.Volume - sec_v1.Volume, fcB_px.Volume - sec_px_v1.Volume
rep("%s D9aft feature volume delta real %+.1f vs proxy %+.1f mm3 (same cuts landed on both; |d| < 2)" % (ok(abs(dv - dvp) < 2.0), dv, dvp))
LUG_LINE = rot(Part.makeCylinder(CR8, L8['w'] + 3.0, V(rc8, -(L8['w'] + 3.0) / 2, zc8), V(0, 1, 0)), L8['ang'])
lg_re, lg_px = fcB.common(LUG_LINE).Volume, fcB_px.common(LUG_LINE).Volume
_fc4 = Part.Shape(); _fc4.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v4_AftFinCanSlotted.step"))
lg_neg = _fc4.common(LUG_LINE).Volume
rep("%s line passes the staple: clash REAL %.4f / proxy %.4f mm3; %.2f mm over the ring face; NEGATIVE CONTROL v4 fin can (d3.5 lug) %.1f mm3 (must be > 1)"
    % (ok(lg_re < 1e-3 and lg_px < 1e-3 and lg_neg > 1.0), lg_re, lg_px, zc8 - CR8 - BH_Z1, lg_neg))
gp8 = cyl(PORT_R - 0.05, BH_Z0 - 0.1, CPL_Z1 + 1.0)
rep("%s d%.0f gas column clear through the thrust ring and the coupler: %.4f mm3; inner leg r %.1f is %.1f mm outside the port (ledge r %.1f)"
    % (ok(fcB_px.common(gp8).Volume < 1e-3 and L8['r0'] > LEDGE_R), 2 * PORT_R, fcB_px.common(gp8).Volume, L8['r0'], L8['r0'] - PORT_R, LEDGE_R))
r_out8 = math.hypot(CPL_R_I + 0.5, L8['w'] / 2)
rep("%s staple stays inside the coupler OD: outer corner r %.2f < %.2f" % (ok(r_out8 < CPL_R_O - 0.1), r_out8, CPL_R_O))
F8 = SNATCH_N
sig_b = F8 * (L8['ob'] - L8['oa']) / 8.0 / (L8['w'] * L8['top'] ** 2 / 6.0)
a_in = (L8['oa'] - L8['r0']) * L8['w']
a_out = (CPL_R_O - L8['ob']) * L8['w']
rep("%s staple at the %.0f N placeholder: top bar %.0f x %.1f over %.1f, bending %.1f MPa (in-layer, < 20); legs across layers (boss-down print) inner %.1f mm2 -> %.1f MPa, outer + coupler wall %.1f mm2 -> %.1f MPa (< %.0f interlayer); bearing %.1f MPa"
    % (ok(sig_b < 20.0 and F8 / 2 / a_in < TAU_ABS_LAYER and F8 / 2 / a_out < TAU_ABS_LAYER), F8, L8['w'], L8['top'], L8['ob'] - L8['oa'], sig_b,
       a_in, F8 / 2 / a_in, a_out, F8 / 2 / a_out, TAU_ABS_LAYER, F8 / (CORD_D * L8['w'])))
fi8 = [(round(f.common(fcB_px).Volume, 3), round(f.common(motor).Volume, 3)) for f in FINS8]
rep("%s 3 fins (v4 part) still drop into the slots: fin x can / fin x motor %s mm3" % (ok(all(a < 1e-3 and b < 1e-3 for a, b in fi8)), fi8))
sw8 = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if fcB_px.translated(V(0, 0, -d)).common(P3['AftTube']).Volume > 1e-3]
rep("%s separation sweep 0..%.0f mm, v8 slotted can vs the AftTube: %s" % (ok(not sw8), CPL_LEN + 4, sw8[:4] or "clear"))
bad = [(nm, round(p.common(fcB_px).Volume, 4)) for nm, p in PINS.items() if p.common(fcB_px).Volume > 1e-3]
rep("%s shear pins sit free in the v8 can's slots: %s" % (ok(not bad), bad or "yes"))
def drop8(s):
    s = s.copy(); bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
fc_print = drop8(fcB)
oh = overhangs8(drop8(fcB_px))
brg = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0
       and c['r0'] >= AR['MT_R_O'] - 2.2 and c['r1'] <= R_ID + 0.8 and c['r1'] - c['r0'] <= 11.0]
big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0 and c not in brg]
bb = fc_print.BoundBox
rep("%s AftFinCanSlotted v8 (proxy) printed boss down: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d annular bridges as v4, %d need support%s"
    % (ok(not big), bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(brg), len(big),
       ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
v4_fc_v = _fc4.Volume
dm8 = (fcB.Volume - v4_fc_v) * RHO['ABS']
FINCAN_V8 = dict(m=FINCAN_V4['m'] + dm8, z=(FINCAN_V4['m'] * FINCAN_V4['z'] + dm8 * (BH_Z1 + 6.0)) / (FINCAN_V4['m'] + dm8))
rep("NOTE slotted fin can v8 vs v4 STEP: %+.2f g (staple lug) -> fin can + fins + epoxy %.1f g" % (dm8, FINCAN_V8['m']))
rep("NOTE the staple sits beside the d14 port, IN THE HOT ZONE: if the 5 mm line is not Kevlar/aramid, sleeve that end in Nomex.")
fcB.exportStep(os.path.join(MODELS, NAME6 + "_AftFinCanSlotted.step"))
MeshPart.meshFromShape(Shape=fcB, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, NAME6 + "_AftFinCanSlotted.stl"))
MeshPart.meshFromShape(Shape=fc_print, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME6 + "_AftFinCanSlotted.stl"))

'''
_END8 = r'''
# =====================================================================================
# v8: PARTS vs v7, CG GATE
# =====================================================================================
rep("")
rep("V8 vs v7")
for _k8 in ('FwdTube', 'AftTube', 'EbayCap'):
    _s7 = Part.Shape(); _s7.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v7_%s.step" % _k8))
    _s8 = P3[_k8]
    _da, _db = _s8.cut(_s7), _s7.cut(_s8)
    _d = _da.Volume + _db.Volume
    if _k8 == 'FwdTube':
        _bbs = [s.BoundBox for s in _da.Solids + _db.Solids]
        zb0, zb1 = min(b.ZMin for b in _bbs), max(b.ZMax for b in _bbs)
        okb = _d > 1.0 and zb0 >= z_b - 0.01 and zb1 <= z_b + EY_BOSS[2] + 0.01
        rep("%s FwdTube v8 vs v7: %.1f mm3 changed, all within st %.2f..%.2f (eyelet boss band st %.2f..%.2f) -> thread, ports, ARM, key groove, seat UNTOUCHED; REPRINT"
            % (ok(okb), _d, station(zb1), station(zb0), S_BH2 - EY_BOSS[2], S_BH2))
    else:
        rep("%s %s v8 vs v7: symmetric difference %.3f mm3 -> %s" % (ok(_d < 0.01), _k8, _d, "IDENTICAL, keep the printed v6/v7 part" if _d < 0.01 else "CHANGED"))
v7_lo_tip = 225.3
lo_tip = station(lo_z) + NOSE_LEN
need = max(0.0, (lo_tip - CG_GATE_TIP) / MM_PER_G)
rep("NOTE liftoff CG tip %.1f (v7 %.1f): +%.1f g line (ASSUMED %.0f g/m x %.1f m) + %.1f g staple. Gate %.0f -> %s"
    % (lo_tip, v7_lo_tip, LINE_G, LINE_G_PER_M, LINE_LEN_M, dm8, CG_GATE_TIP,
       "inside the gate" if need == 0 else "~%.0f g more EbayCap ballast (%.1f mm/g) -- WEIGH THE LINE, then balance the built rocket" % (math.ceil(need), MM_PER_G)))
doc.addObject("Part::Feature", "AftFinCanSlotted_v8").Shape = fcB
for i, f in enumerate(FINS8): doc.addObject("Part::Feature", "Fin_%d" % i).Shape = f
doc.addObject("Part::Feature", "line_eyelet_probe").Shape = EY_LINE
doc.addObject("Part::Feature", "line_staple_probe").Shape = LUG_LINE
doc.recompute(); doc.save()
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT v8: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))
'''
def _v8_pre_v6(src):
    for a, b in [
        ('os.path.join(PRINT_READY, "%s_%s.stl" % (NAME6, k))', 'os.path.join(PRINT_READY if k == "FwdTube" else PRINT_RAW, "%s_%s.stl" % (NAME6, k))'),   # AftTube/EbayCap unchanged
        ('os.path.join(PRINT_READY, NAME6 + "_ElectronicsSled_v6.stl")', 'os.path.join(PRINT_RAW, NAME6 + "_ElectronicsSled_v6.stl")'),                     # sled v7 unchanged
        ('rep("NOTE Kevlar leader: the bulkhead eyelet', 'rep("NOTE 5 mm line: the bulkhead eyelet'),
        ('point("AftFinCanSlotted v4 + 3 fins + epoxy", "aft", FINCAN_V4[\'m\'], FINCAN_V4[\'z\'], "D9aft v4 report (part unchanged)")',
         'point("AftFinCanSlotted v8 + 3 fins + epoxy", "aft", FINCAN_V8[\'m\'], FINCAN_V8[\'z\'], "v4 report + v8 staple-lug delta")'),
        ('point("Canopy d500 + harness + Kevlar leader", "recovery", CANOPY_G, zs(S_BH2 + 45.0), "DESIGN 7.7; packed forward in the bay")',
         'point("Canopy d500 + harness", "recovery", CANOPY_G, zs(S_BH2 + 45.0), "DESIGN 7.7; packed forward in the bay")\n'
         'point("5 mm retention line %.1f m" % LINE_LEN_M, "recovery", LINE_G, zs(S_BH2 + LINE_PACK_OFF), "ASSUMED %.0f g/m -- weigh it" % LINE_G_PER_M)'),
    ]:
        assert src.count(a) == 1, "v6 (v8) patch target not unique: %r" % a
        src = src.replace(a, b)
    i = src.index("# MASS / CG (full rollup on the v6 layout)")
    i = src.rfind("# ====", 0, i)
    return src[:i] + _MID8 + src[i:]

V7_PATCHES8 = [
    ('_src = open(V6_SRC, encoding="utf-8").read()', '_src = _v8_pre_v6(open(V6_SRC, encoding="utf-8").read())'),
    ('\'NAME6, REV6 = "PhoenixABS40-43_D9aft_v7", "D9aft_v7"\'', '\'NAME6, REV6 = "PhoenixABS40-43_D9aft_v8", "D9aft_v8"\''),
    ('\'App.newDocument("Phoenix_D9aft_v7")\'', '\'App.newDocument("Phoenix_D9aft_v8")\''),
    ('v6 rebuilt on sled v7 (piezo sideways, flat on the plate, pin bay; e-bay +%.1f mm as v6), 150 mm chute bay',
     'v7 + 5 mm retention line tied direct: eyelet 6.5 openings, fin-can staple lug (sled v7, e-bay +%.1f mm as v6), 150 mm chute bay'),
    ("('FwdTube v7', P3['FwdTube']), ('FwdTube v7 proxy', fw_px3), ('AftTube v7', P3['AftTube']), ('EbayCap v7', P3['EbayCap'])",
     "('FwdTube v8', P3['FwdTube']), ('FwdTube v8 proxy', fw_px3), ('AftTube v8', P3['AftTube']), ('EbayCap v8', P3['EbayCap'])"),
    ('solid("FwdTube v7 (thread, seat, bulkhead, eyelet, ports, ARM)"', 'solid("FwdTube v8 (thread, seat, bulkhead, 5 mm eyelet, ports, ARM)"'),
    ('solid("AftTube v7 (chute bay, launch lug, pin slots)"', 'solid("AftTube v8 = v6 (chute bay, launch lug, pin slots)"'),
    ('solid("EbayCap v7"', 'solid("EbayCap v8 = v6"'),
    ('"RESULT v7: %s (%d FAIL)"', '"RESULT v7 checks: %s (%d FAIL)"'),
    ('_src = _src[:_k] + _v7_checks + _src[_k:]', '_src = _src[:_k] + _v7_checks + _END8 + _src[_k:]'),
]
_s7 = builtins.open(V7_SRC8, encoding="utf-8").read()
for a, b in V7_PATCHES8:
    assert _s7.count(a) == 1, "v7 patch target not unique / missing: %r" % a
    _s7 = _s7.replace(a, b)
exec(_s7)

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v3: v2 with the foam ring replaced by PRINTED SPRINGS + a ROTATION KEY.

Changes from v2 (everything else is v2, exec'd read-only up to its CHECKS banner, with two in-memory
edits to the FwdTube recipe -- the v2 file on disk is untouched):
  FwdTube  + axial KEY GROOVE at 180 deg, from the mouth to past the EbayCap, cut to the thread-root
           radius only (the 1.05 mm skin is not thinned). Cut BEFORE the thread, so it is a boolean on
           the plain part. v2's 0-deg witness notch is dropped (the key does the clocking).
  EbayCap  + KEY on the rim at 180 deg (rides the groove: one insertion clocking, ~+-1 deg of play)
           + 3 SPRING BEAMS (0/120/240 deg): arc beams fixed at both ends over a shallow pocket, a bump at
             mid-span. The nose shoulder presses the bumps 0.25 mm -> preload; the beams bottom out after
             0.55 mm, which is the e-bay's only axial travel. Both-ends-fixed so each beam prints as a
             bridge, not a drooping cantilever.
           - v2's witness notch.
  unchanged  nose v6, AftTube v2, fin can / pins / coupons / cap (v1). No foam ring.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame z = 340 - station. Any FAIL line means do not print.
"""
import os, math, time
t000 = time.time()
V2_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v2.py"
_v2 = open(V2_SRC, encoding="utf-8").read()
_c = _v2.index("\n# CHECKS\n"); _c = _v2.rfind("# ====", 0, _c)
_g = _v2[:_c]
_notch = "fw = fw.cut(box(R_OD - 0.4, R_OD + 1, -0.5, 0.5, zs(2.0), zs(0.0) + 1))       # witness notch at 0 deg (sound port side)\n"
_groove = ("KEY_ANG, KEY_W, KEY_R0, KEY_R1 = 180.0, 2.4, 19.0, 20.15            # D9aft v3: key on the EbayCap rim\n"
           "GROOVE_W, GROOVE_R = 3.0, THREAD['CAP_T_ROOT_R']                  # groove never deeper than the thread root\n"
           "GROOVE_END = S_DISC_TOP + (DISC_ZS1 - DISC_ZS0) + 1.0               # 1 mm past the seated key\n"
           "fw = fw.cut(rot(box(KEY_R0 - 1.0, GROOVE_R, -GROOVE_W / 2, GROOVE_W / 2, zs(GROOVE_END), zs(-1.0)), KEY_ANG))   # D9aft v3 key groove\n")
assert _g.count(_notch) == 1
_g = _g.replace(_notch, _groove)                       # in memory only: groove before the thread cut, notch dropped
exec(_g)
print("v2 geometry (with the v3 groove) in %.1f s" % (time.time() - t000), flush=True)

NAME3, REV3 = "PhoenixABS40-43_D9aft_v3", "D9aft_v3"
report = []

# =====================================================================================
# PARAMETERS (v3 springs + key)
# =====================================================================================
E_ABS = 2000.0                    # MPa, printed ABS bending modulus (assumed)
SPR_ANG = (0.0, 120.0, 240.0)     # beam centres: clear of the key + M2 head at 180 and the M2 head at 0 (r 10)
SPR_HALF = 30.0                   # deg each side -> arc span at mean r
SPR_R0, SPR_R1 = 16.5, 18.9       # beam radial extent (b = 2.4)
SPR_T = 0.8                       # beam thickness = 4 layers at 0.20
SPR_POCKET = 0.6                  # free travel under the beam
SPR_SLOT = 0.6                    # radial slot either side (outer side runs out through the rim)
BUMP_W = 3.0                      # bump footprint (tangential x radial ~ 3 x 2.4)
PRELOAD = 0.25                    # nose shoulder presses the bumps this far
BUMP_H = FOAM_GAP + PRELOAD       # bump stands this far above the cap top (1.25)

# =====================================================================================
# EBAY CAP v3
# =====================================================================================
zd0, zd1 = DISC_ZS0 + SLED_Z2, DISC_ZS1 + SLED_Z2
def sector(r0, r1, a0, a1, z0, z1, n=24):
    pts = [pol(r0, a0 + (a1 - a0) * i / n, 0) for i in range(n + 1)] + [pol(r1, a1 - (a1 - a0) * i / n, 0) for i in range(n + 1)]
    f = Part.Face(Part.Wire(Part.makePolygon(pts + [pts[0]])))
    return f.extrude(V(0, 0, z1 - z0)).translated(V(0, 0, z0))
ec = cyl(DISC_R, zd0, zd1)
top_slab = sled2.common(box(-30, 30, -30, 30, zd0 + 0.01, zd1 + 1))
pk = [top_slab.translated(V(dx, dy, dz)) for dx, dy in ((0, 0), (0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25), (0.18, 0.18), (-0.18, 0.18), (0.18, -0.18), (-0.18, -0.18)) for dz in (-0.3, 0, 0.3)]
ec = ec.cut(pk[0].fuse(pk[1:]))
for x, y in SLED_SCREWS:
    ec = ec.cut(cyl(1.1, zd0 - 1, zd1 + 1, x=x, y=y))
L_ = LOOP
for xa in (L_['x0'], L_['x1'] - L_['post']):
    ec = ec.fuse(box(xa, xa + L_['post'], -L_['y'], L_['y'], zd1 - 0.3, zd1 + L_['h']))
ec = ec.fuse(box(L_['x0'], L_['x1'], -L_['y'], L_['y'], zd1 + L_['h'] - L_['top'], zd1 + L_['h']))
ec = ec.fuse(rot(box(KEY_R0 - 0.5, KEY_R1, -KEY_W / 2, KEY_W / 2, zd0, zd1), KEY_ANG))       # key (overlaps the rim 0.5)
ec = ec.cut(pk[0].fuse(pk[1:]))                                                                  # re-cut the sled pocket: the key sits over the sled's spine
z_bf = zd1 - SPR_T - SPR_POCKET                                                                 # pocket floor
BEAMS, BUMPS = [], []
for a in SPR_ANG:
    ec = ec.cut(sector(SPR_R0 - SPR_SLOT, DISC_R + 1.0, a - SPR_HALF, a + SPR_HALF, z_bf, zd1 + 1))   # clear pocket + slots
    bm = sector(SPR_R0, SPR_R1, a - SPR_HALF - 1.5, a + SPR_HALF + 1.5, zd1 - SPR_T, zd1)           # beam, ends 1.5 deg into the cap
    rm = (SPR_R0 + SPR_R1) / 2
    bp = rot(box(SPR_R0, SPR_R1, -BUMP_W / 2, BUMP_W / 2, zd1 - 0.2, zd1 + BUMP_H), a)
    BEAMS.append(bm); BUMPS.append(bp)
    ec = ec.fuse(bm).fuse(bp)
ec = ec.removeSplitter()
P3 = {'EbayCap': ec.Solids[0] if len(ec.Solids) == 1 else ec, 'FwdTube': P2['FwdTube'], 'AftTube': P2['AftTube']}
fw_px3 = fw_px
print("v3 parts built in %.1f s" % (time.time() - t000), flush=True)

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: v2 + printed spring beams and a rotation key on the e-bay (no foam ring) ==" % REV3)
rep("Frame z = %.0f - station. FwdTube groove cut before the thread (plain boolean); thread pair re-checked seated." % BODY_LEN)
rep("")
for k, s in (('FwdTube v3', P3['FwdTube']), ('FwdTube v3 proxy', fw_px3), ('EbayCap v3', P3['EbayCap'])):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))

# --- groove on the REAL FwdTube
g_mid = (S_DISC_TOP + GROOVE_END) / 2 + 1.0
gp = [("groove open below the thread band", pol(20.3, KEY_ANG, zs(14.0)), False),
      ("groove open through the thread band (at the root radius)", pol(20.3, KEY_ANG, zs(5.0)), False),
      ("wall solid beside the groove", pol(20.3, KEY_ANG + 8.0, zs(14.0)), True),
      ("skin solid behind the groove (not deeper than the root)", pol(GROOVE_R + 0.15, KEY_ANG, zs(14.0)), True),
      ("groove ends: solid past station %.1f" % GROOVE_END, pol(20.3, KEY_ANG, zs(GROOVE_END + 1.0)), True),
      ("thread still present away from the groove", V(CREST + 0.15, 0, T_ANCHOR_A + 4 * PITCH + PITCH / 2), True)]
bad = [(n, w) for n, p, w in gp if inside(P3['FwdTube'], p) != w]
rep("%s REAL FwdTube key groove: %d/%d probes as designed%s" % (ok(not bad), len(gp) - len(bad), len(gp), "; WRONG %s" % bad if bad else ""))
rep("%s groove depth r %.2f = thread root: skin behind it %.2f mm (unchanged); width %.1f mm = %.1f%% of the thread circumference"
    % (ok(GROOVE_R <= ROOT + 1e-6), GROOVE_R, R_OD - GROOVE_R, GROOVE_W, 100 * GROOVE_W / (2 * math.pi * CREST)))

# --- thread pair, seated, + negative control (the groove only REMOVES tube material, so the v2 sweep cannot gain a clash)
def nose_at(phi, extra_dz=0.0):
    s = nose6.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), phi); s.translate(V(0, 0, PITCH * phi / 360.0 + extra_dz)); return s
t1 = time.time()
SAMP = [pol(r, a + 0.37, zs(s)) for r in (19.80, 20.05) for a in range(0, 360, 15) for s in [0.6 + 0.6 * i for i in range(14)]]
in_t = [inside(P3['FwdTube'], p) for p in SAMP]
def clash(ns):
    inn = [inside(ns, p) for p in SAMP]
    return sum(1 for a, b in zip(in_t, inn) if a and b), sum(inn)
c0, n0 = clash(nose6)
print("  seated done (%.0f s)" % (time.time() - t1), flush=True)
cn, _ = clash(nose_at(180.0, extra_dz=-PITCH * 0.5))
rep("%s thread SEATED with the groove: clash %d of %d; fill tube %.0f%% (v2 32%%) / nose %.0f%%" % (ok(c0 == 0 and sum(in_t) / len(SAMP) > 0.2), c0, len(SAMP), 100 * sum(in_t) / len(SAMP), 100 * n0 / len(SAMP)))
rep("%s NEGATIVE CONTROL half a pitch out of phase: clash %d (must be > 0)" % (ok(cn > 20), cn))
rep("NOTE unscrew sweep not re-run: the groove only removes tube material, so it cannot add a clash to v2's clean sweep (v2 report)")

# --- key: passes the groove from the mouth, blocks rotation when seated
ebay = Part.makeCompound([P3['EbayCap'], sled2])
sw = []
for d in [0.5 * k for k in range(0, 2 * int(S_DISC_TOP + (DISC_ZS1 - DISC_ZS0) + 4) + 1)]:
    v = P3['EbayCap'].translated(V(0, 0, d)).common(fw_px3).Volume
    if v > 1e-3: sw.append((d, round(v, 3)))
rep("%s e-bay lifts out: EbayCap (with key) slides %.0f mm out of the mouth with no contact %s" % (ok(not sw), S_DISC_TOP + (DISC_ZS1 - DISC_ZS0) + 4, sw[:4] or ""))
play = math.degrees(((GROOVE_W - KEY_W) / 2) / KEY_R1)
blk = []
for da in (-(play + 1.0), play + 1.0):
    c = P3['EbayCap'].copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), da)
    blk.append(round(c.common(fw_px3).Volume, 2))
rep("%s key blocks rotation: turning the seated cap %.1f deg either way hits the groove wall (%s mm3); free play +-%.1f deg"
    % (ok(all(b > 0.01 for b in blk)), play + 1.0, blk, play))
rep("%s key radius %.2f passes the thread only through the groove (crest %.2f); groove %.2f -> %.2f mm radial, %.2f mm per side"
    % (ok(GROOVE_R - KEY_R1 >= 0.25 and (GROOVE_W - KEY_W) / 2 >= 0.25), KEY_R1, CREST, GROOVE_R, GROOVE_R - KEY_R1, (GROOVE_W - KEY_W) / 2))

# --- springs
ov = nose6_px.common(P3['EbayCap'])
bump_ov = sum(nose6_px.common(b).Volume for b in BUMPS)
rep("%s nose touches the EbayCap only at the 3 bumps: overlap %.2f mm3 = bumps %.2f mm3 (the designed %.2f mm preload)"
    % (ok(abs(ov.Volume - bump_ov) < 0.05 and bump_ov > 0.1), ov.Volume, bump_ov, PRELOAD))
rm = (SPR_R0 + SPR_R1) / 2
Lb = math.radians(2 * SPR_HALF) * rm
b_ = SPR_R1 - SPR_R0
I_ = b_ * SPR_T ** 3 / 12.0
k_ = 192.0 * E_ABS * I_ / Lb ** 3
P_ = k_ * PRELOAD
sig = (P_ * Lb / 8.0) * (SPR_T / 2) / I_
P_bot = k_ * SPR_POCKET
sig_bot = (P_bot * Lb / 8.0) * (SPR_T / 2) / I_
rep("%s spring beams (fixed-fixed, span %.1f mm, %.1f x %.1f): k %.1f N/mm; preload %.2f mm -> %.2f N each, %.1f N total, %.1f MPa"
    % (ok(sig <= 15.0), Lb, b_, SPR_T, k_, PRELOAD, P_, 3 * P_, sig))
rep("%s e-bay forward travel before the beams bottom: %.2f mm (was 1.0 of free rattle with no foam); at bottoming %.1f MPa (short-time, < 35)"
    % (ok(sig_bot < 35.0), SPR_POCKET - PRELOAD, sig_bot))
g_ = 3 * P_ / (56.4e-3 * 9.81)
rep("  preload holds the 56 g e-bay down to ~%.1f g of forward deceleration; above that it lifts at most %.2f mm onto the bottomed beams." % (g_, SPR_POCKET - PRELOAD))
pp = [("pocket open under each beam", [pol(rm, a + SPR_HALF * 0.5, zd1 - SPR_T - SPR_POCKET / 2) for a in SPR_ANG], False),
      ("inner slot open", [pol(SPR_R0 - SPR_SLOT / 2, a, zd1 - 0.4) for a in SPR_ANG], False),
      ("beam solid mid-span", [pol(rm, a + 8.0, zd1 - SPR_T / 2) for a in SPR_ANG], True),
      ("pocket floor solid", [pol(rm, a + SPR_HALF * 0.5, z_bf - 0.3) for a in SPR_ANG], True)]
bad = [n for n, ps, w in pp if any(inside(P3['EbayCap'], p) != w for p in ps)]
rep("%s spring geometry probes (pocket, slot, beam, floor at all 3): %s" % (ok(not bad), bad or "as designed"))
tr = sum(b.translated(V(0, 0, -SPR_POCKET)).common(sled2).Volume for b in BEAMS)
rep("%s beams bottomed (%.1f mm down) stay clear of the sled top: %.4f mm3" % (ok(tr < 1e-3), SPR_POCKET, tr))

# --- everything else in the e-bay
air3 = dict(ebaycap=P3['EbayCap'], sled=sled2, fwd=fw_px3, **HW2)
air3.update({'env_' + k: v for k, v in ENV2.items()})
bad = interference(air3, {('sled', 'env_SmallParts'), ('ebaycap', 'fwd')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)})
kf = P3['EbayCap'].common(fw_px3).Volume
rep("%s e-bay interference (cap, sled, electronics, screws, tube): %s; cap vs tube %.4f mm3" % (ok(not bad and kf < 1e-3), bad or "none", kf))
rr = max(SL['SLED_RMAX'], DISC_R)
rep("%s rest of the e-bay (R %.2f) passes the thread crests %.2f -> %.2f mm radial" % (ok(CREST - rr >= 0.25), rr, CREST, CREST - rr))

# --- printability
for k, s, lab in (('EbayCap', P3['EbayCap'], 'disc down, loop + bumps up'), ('FwdTube', fw_px3, 'bulkhead down (proxy)')):
    o = s.copy(); bb = o.BoundBox; o.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); bb = o.BoundBox
    oh = overhangs(o)
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d need support%s"
        % (ok(not big), k, lab, bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
rep("NOTE the spring beams print as %.0f mm arc bridges, %d layers: use the slicer's bridge settings. A sagging first layer only lowers the preload." % (Lb, round(SPR_T / 0.2)))
dm = (P3['EbayCap'].Volume - P2['EbayCap'].Volume) * RHO['ABS']
rep("NOTE mass: EbayCap %+.2f g vs v2, foam ring -0.3 g -> OpenRocket not re-run (v2 numbers stand: 1.78 cal, D9-5 at apogee)." % dm)
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT (FwdTube + EbayCap only; AftTube is v2, fin can / pins / coupons / cap are v1)
# =====================================================================================
for k in ('FwdTube', 'EbayCap'):
    P3[k].exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME3, k)))
    MeshPart.meshFromShape(Shape=P3[k], LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME3, k)))
    o = P3[k].copy(); bb = o.BoundBox; o.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    MeshPart.meshFromShape(Shape=o, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_%s.stl" % (NAME3, k)))
doc = App.newDocument("Phoenix_D9aft_v3")
for k, s in (('FwdTube_v3', P3['FwdTube']), ('EbayCap_v3', P3['EbayCap']), ('ElectronicsSled_v1', sled2), ('Nose_v6', nose6), ('AftTube_v2', P2['AftTube'])):
    doc.addObject("Part::Feature", k).Shape = s
doc.recompute()
doc.saveAs(os.path.join(MODELS, NAME3 + ".FCStd"))
with open(os.path.join(MODELS, NAME3 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t000))

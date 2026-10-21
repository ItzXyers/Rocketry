# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v11: v9 snap latch with the two latches PRECISELY OPPOSITE (60 / 240 deg) + a clocking KEY.

User, 2026-10-14: "aft / fincan section that has the latches precisely opposite each other for enhanced stability".
  v9 put the 2 L24 latches at 60 / 180 (120 apart) so the fin can clicked in ONE clocking only (fins 0/120/240,
  launch-lug rod line at 300: a can turned 180 deg puts a fin on the rod line). Opposed latches are symmetric under
  180 deg, so v11 adds a hard KEY instead:
    tab    on the fin-can shoulder face at 30 deg (fin slots break the shoulder at 0/120/240), r 20.1..21.5 (flush
           with the OD), 7.0 mm wide (twist / landing robustness; only 1.4 radial fits), TAB_H tall = window-forward-face -> bump-aft-end span + 1.0 mm.
    notch  in the AftTube aft band at 30 deg, +0.2 mm each side, TAB_H + 0.3 deep (band 7.0).
  Wrong clocking (180): the tab lands on the tube's aft face and holds the can TAB_H proud -> the windows sit wholly
  aft of the bumps = NO catch possible (swept below), plus an obvious ~5 mm gap at the joint.
  Opposed latches = the geometry of the measured coupon (bumps 0/180, 873 g first pull): no 120 deg slip-fit penalty,
  and the pull is balanced across the joint instead of cocking the coupler toward one side.

Built exactly as v9 (from v8's exported STEPs, read-only) by exec'ing v9's text with asserted patches; v9 is not
edited and its outputs are not touched. Only v11 names are written.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame: v1 fin-can frame Zf (z = 0 the fin-can aft face, +z toward the nose). Any FAIL line means do not print.
"""
import os, builtins
_MD11 = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models"
V9_SRC11 = os.path.join(_MD11, "PhoenixABS40-43_D9aft_v9.py")

def _sub11(src, pairs):
    for a, b in pairs:
        assert src.count(a) == 1, "v9 patch target not unique / missing: %r" % a
        src = src.replace(a, b)
    return src

_KEY11 = r'''
# ---------------- v11: opposed latches + clocking key (tab on the fin-can shoulder, notch in the tube aft band)
TAB_ANG, TAB_W, TAB_CLR, TAB_R0 = 30.0, 7.0, 0.2, R_ID + 0.1
BUMP_Z = (CPN['E0'] + SHOULDER_Z, CPN['E0'] + CPN['LB'] + SHOULDER_Z)                  # tube bump axial span (Zf)
WIN_Z = (CPN['Z_WIN_AFT'] + SHOULDER_Z, CPN['z_win_fwd'](R_ID) + SHOULDER_Z)           # coupler window span (Zf, widest)
TAB_H = (WIN_Z[1] - BUMP_Z[0]) + 1.0                                                    # stood off by TAB_H -> window wholly aft of bump + 1.0
NOTCH_D = TAB_H + 0.3
_tha = CPN['deg'](TAB_W / 2 / ((TAB_R0 + R_OD) / 2)); _thn = CPN['deg']((TAB_W / 2 + TAB_CLR) / ((TAB_R0 + R_OD) / 2))
TAB11 = CPN['rev']([(TAB_R0, SHOULDER_Z - 0.3), (R_OD, SHOULDER_Z - 0.3), (R_OD, SHOULDER_Z + TAB_H), (TAB_R0, SHOULDER_Z + TAB_H)], TAB_ANG - _tha, TAB_ANG + _tha)
NOTCH11 = CPN['rev']([(R_ID - 0.1, SHOULDER_Z - 1.0), (R_OD + 0.1, SHOULDER_Z - 1.0), (R_OD + 0.1, SHOULDER_Z + NOTCH_D), (R_ID - 0.1, SHOULDER_Z + NOTCH_D)], TAB_ANG - _thn, TAB_ANG + _thn)

'''

_CHK11 = r'''
# =====================================================================================
# v11: OPPOSED LATCHES + CLOCKING KEY
# =====================================================================================
rep("")
rep("V11 OPPOSED LATCHES + KEY (tab %.1f wide x %.2f tall at %.0f deg on the shoulder; notch %.2f deep, +%.1f each side)" % (TAB_W, TAB_H, TAB_ANG, NOTCH_D, TAB_CLR))
rep("%s latches precisely opposite: %s deg, separation %.3f deg" % (ok(abs(((LATCH_ANG[1] - LATCH_ANG[0]) % 360) - 180.0) < 1e-9), "/".join("%.0f" % a for a in LATCH_ANG), (LATCH_ANG[1] - LATCH_ANG[0]) % 360))
rep("%s TAB_H %.2f derived: window fwd face Zf %.2f - bump aft end Zf %.2f + 1.0 margin; notch %.2f leaves %.2f mm of the %.1f aft band" % (ok(NOTCH_D <= CPN['BAND_AFT'] - 1.0), TAB_H, WIN_Z[1], BUMP_Z[0], NOTCH_D, CPN['BAND_AFT'] - NOTCH_D, CPN['BAND_AFT']))
def _adist(a, b): return abs((a - b + 180.0) % 360.0 - 180.0)
_keep = [("tongue %.0f span" % a, min(_adist(TAB_ANG, x) for x in [g['th_tip'] + (g['th_root'] - g['th_tip']) * i / 50.0 for i in range(51)] + [g['th_tip'] - CPN['deg'](CPN['GAP_END'] / CPN['R_T'])])) for g, a in zip(LG, LATCH_ANG)]
_keep += [("window %.0f" % a, _adist(TAB_ANG, a) - CPN['deg'](CPN['BUMP_S'] / 2 / R_ID) - 1.5) for a in LATCH_ANG]
_keep += [("staple lug %.0f" % LUG_ANG, _adist(TAB_ANG, LUG_ANG) - CPN['deg'](LUG_W / 2 / LUG_R0)), ("launch lug %.0f" % LL_ANG, _adist(TAB_ANG, LL_ANG))]
_keep += [("fin %.0f (slot through the shoulder)" % a, _adist(TAB_ANG, a)) for a in (0.0, 120.0, 240.0)]
_near = [(n, round(d - _thn, 1)) for n, d in _keep if d - _thn < 5.0]
rep("%s key at %.0f deg (+-%.1f) clear of tongues/end slots, windows, staple lug, launch lug, fin slots by >= 5 deg%s" % (ok(not _near), TAB_ANG, _thn, "; TOO CLOSE %s" % _near if _near else ""))
_fw = [z * 0.5 for z in range(int((SHOULDER_Z + 0.5) * 2), int((CPL_Z1 - 0.5) * 2)) if not all(inside(fc8, pol(r, a, z * 0.5)) for r in (18.8, 19.15) for a in (0.0, 120.0, 240.0))]
rep("%s fin slots stop at the shoulder: v8 coupler wall solid at r 18.8/19.15, Zf %.1f..%.1f, at 0/120/240 (240 window cuts clean wall)%s" % (ok(not _fw), SHOULDER_Z + 0.5, CPL_Z1 - 0.5, "; OPEN at Zf %s" % _fw[:6] if _fw else ""))
_kp = [("fin can: shoulder solid under the tab", fc8, pol((TAB_R0 + R_OD) / 2, TAB_ANG, SHOULDER_Z - 0.4), True),
       ("fin can v11: tab present", fc9, pol((TAB_R0 + R_OD) / 2, TAB_ANG, SHOULDER_Z + TAB_H / 2), True),
       ("fin can v11: nothing beside the tab", fc9, pol((TAB_R0 + R_OD) / 2, TAB_ANG + 15, SHOULDER_Z + TAB_H / 2), False),
       ("AftTube v11: notch open", tube9, pol((R_ID + R_OD) / 2, TAB_ANG, SHOULDER_Z + TAB_H / 2), False),
       ("AftTube v11: band solid above the notch", tube9, pol((R_ID + R_OD) / 2, TAB_ANG, SHOULDER_Z + NOTCH_D + 0.6), True),
       ("AftTube v11: band solid beside the notch", tube9, pol((R_ID + R_OD) / 2, TAB_ANG + 15, SHOULDER_Z + 1.0), True)]
bad = [n for n, s, p, w in _kp if inside(s, p) != w]
rep("%s key probes %d/%d%s" % (ok(not bad), len(_kp) - len(bad), len(_kp), "; WRONG %s" % bad if bad else ""))
_bumps = Part.makeCompound([g['bump'] for g in LG])
_wins = Part.makeCompound(WIN)
_cat = _bumps.common(_wins.translated(V(0, 0, -0.6))).Volume
rep("%s positive control, RIGHT clocking: bumps x windows with the can pulled aft 0.6 = %.3f mm3 (catches)" % (ok(_cat > 0.05), _cat))
def _rot(s, d):
    c = s.copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), d); return c
_w180, _t180 = _rot(_wins, 180.0), _rot(TAB11, 180.0)
_blk = _t180.common(tube9).Volume
rep("%s WRONG clocking (180): tab x tube seated = %.2f mm3 -> the tab lands on the tube aft face, can stands %.2f proud" % (ok(_blk > 1.0), _blk, TAB_H))
_lo = tube9.common(_t180.translated(V(0, 0, -(TAB_H - 0.1)))).Volume
_sw = [(round(d, 2), round(_bumps.common(_w180.translated(V(0, 0, -d))).Volume, 4)) for d in [TAB_H - 0.3 + 0.05 * k for k in range(17)]]
_hit = [x for x in _sw if x[1] > 1e-4]
rep("%s WRONG clocking: can can't seat past TAB_H-0.1 (tab x tube %.2f mm3); bumps x windows over stand-off %.2f..%.2f = %s -> NO catch possible"
    % (ok(_lo > 0.05 and not _hit), _lo, _sw[0][0], _sw[-1][0], _hit or "0 everywhere"))
_oth = [(d, round(_bumps.common(_rot(_wins, d).translated(V(0, 0, -z))).Volume, 4)) for d in (120.0, 240.0) for z in (0.0, 0.6)]
rep("%s other clockings 120/240: bumps x windows seated / pulled 0.6 = %s (bumps ride the solid coupler wall: no click)" % (ok(all(v < 1e-4 for _, v in _oth)), [v for _, v in _oth]))
_lz11 = fc9.common(Part.makeBox(12.0, LUG_W + 2, 30.0, V(LUG_R0 - 1, -(LUG_W + 2) / 2, BH_Z1 - 1)).rotated(V(0, 0, 0), V(0, 0, 1), LUG_ANG))
_dl = _lz11.cut(lug_zone).Volume + lug_zone.cut(_lz11).Volume
rep("%s staple lug at %.0f (6.5 x 6.5 opening, matched to the FwdTube eyelet) UNCHANGED vs v8: symmetric difference %.4f mm3 -> v8 line-past-staple sweep still holds" % (ok(_dl < 1e-3), LUG_ANG, _dl))
_t9s, _f9s = Part.Shape(), Part.Shape()
_t9s.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v9_AftTube.step")); _f9s.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v9_AftFinCanSlotted.step"))
_dmt, _dmf = (tube9.Volume - _t9s.Volume) * RHO_ABS, (fc9.Volume - _f9s.Volume) * RHO_ABS
rep("%s MASS vs v9 (the v10 flight parts): AftTube %+.3f g, fin can %+.3f g -> %+.3f g, all in the joint zone Zf 51..90: v10 CG (228.0 from the tip) and stability margin stand"
    % (ok(abs(_dmt + _dmf) < 0.1), _dmt, _dmf, _dmt + _dmf))
rep("NOTE opposed latches = the measured coupon layout (bumps 0/180, 873 g first pull): no 120 deg slip-fit engagement loss; the latch load is balanced across the joint, the coupler is not cocked toward one side.")
'''

_s9 = builtins.open(V9_SRC11, encoding="utf-8").read()
_s9 = _sub11(_s9, [
    ('NAME9, REV9 = "PhoenixABS40-43_D9aft_v9", "D9aft_v9"', 'NAME9, REV9 = "PhoenixABS40-43_D9aft_v11", "D9aft_v11"'),
    ('LATCH_ANG = PIN_ANG\n', 'LATCH_ANG = (60.0, 240.0)                        # v11: precisely opposite (v9: PIN_ANG 60/180)\n'),
    ('tube8, fc8 = read(TUBE8), read(FC8)\n', _KEY11 + 'tube8, fc8 = read(TUBE8), read(FC8)\n'),
    ("for g in LG: t = t.fuse(g['tongue'])\n", "for g in LG: t = t.fuse(g['tongue'])\nt = t.cut(NOTCH11)\n"),
    ("for w in WIN: f = f.cut(w)\n", "for w in WIN: f = f.cut(w)\nf = f.fuse(TAB11)\n"),
    ('rep("== Phoenix ABS 40-43 -- %s: v8 + printed SNAP LATCH (coupon v2, L24 at %s deg) in place of the shear pins ==" % ',
     'rep("== Phoenix ABS 40-43 -- %s: v9 snap latch, L24 latches OPPOSED at %s deg + clocking key (on v8 parts) ==" % '),
    ("ok(min(b.ZMin for b in bbs) >= min(Z_PIN - 1, CPN['Z_WIN_AFT'] + SHOULDER_Z) - 0.01",
     "ok(min(b.ZMin for b in bbs) >= min(Z_PIN - 1, CPN['Z_WIN_AFT'] + SHOULDER_Z, SHOULDER_Z - 0.3) - 0.01"),
    ('all within Zf %.2f..%.2f (pin slots + windows)"', 'all within Zf %.2f..%.2f (pin slots + windows + key tab)"'),
    # v9's one-clocking check relied on 120 deg spacing; at 180 the tab would make it pass for the wrong reason -> replaced by _CHK11
    ('clk = []\nfor d in (120.0, 180.0, 240.0):\n', 'clk = []\nfor d in ():\n'),
    ('rep("%s one clocking only: fin can turned %s deg -> bumps hit solid coupler wall %s mm3 = no click" % (ok(all(v > 0.05 for _, v in clk)), "/".join("%.0f" % d for d, _ in clk), [v for _, v in clk]))\n',
     '# v11: clocking checked in the V11 block (key)\n'),
    ('rep("NOTE latches 120 deg apart (coupon 180): the coupler shifts ~0.2 mm in its slip fit -> ~0.1 mm less engagement (of 1.0) -> release a little lower than the coupon.")\n', ''),
    ('rep("ASSEMBLY: pack, push the fin can in, turn it until it CLICKS (one clocking only). No click = do not fly.")',
     _CHK11 + 'rep("")\nrep("ASSEMBLY: pack, push the fin can in, turn it until the KEY TAB (30 deg, between two fins) drops into the tube notch, then push: 2 CLICKS.\\n"\n    "  A ~5 mm gap at the joint = wrong clocking (tab on the tube face): turn 180, do not fly like that. No click = do not fly.")'),
    ('rep("RESULT v9: %s', 'rep("RESULT v11: %s'),
    ('App.newDocument("Phoenix_D9aft_v9")', 'App.newDocument("Phoenix_D9aft_v11")'),
    ('(("AftTube_v9", tube9), ("AftFinCanSlotted_v9", fc9))', '(("AftTube_v11", tube9), ("AftFinCanSlotted_v11", fc9))'),
])
exec(_s9)

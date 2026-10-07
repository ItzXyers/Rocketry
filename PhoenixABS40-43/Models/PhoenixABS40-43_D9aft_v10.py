# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v10: v8 rebuilt on ELECTRONICS SLED v8, flight AftTube + fin can = v9 (snap latch).

User, 2026-10-07: build v10 = sled v8 (Avionics/PhoenixABS40-43_avbay_sled_v8.py: v7 refitted to the measured
parts, same length + interfaces, 12.6 g vs 15.0) + the v9 snap latch, with a fresh mass / CG and balance note.

  FwdTube / EbayCap  v8 recipe on sled v8 -> asserted IDENTICAL to the v8 STEPs (interfaces unchanged).
  AftTube / fin can  the v9 STEPs (snap latch, no pins) are the flight parts; v10 does not rebuild or export them.
                     They enter the mass rollup as solids; the shear pins leave it.
  sled               v8 (its STL is in the print set already, from the sled session).

v8 (and through it v7, v6) is NOT edited: v10 execs v8's text with these patches:
  v7 text   sled v7 -> v8, names; v6 text   AftTube mass from the v9 STEP, pins dropped from the rollup;
  v8 text   names, fin-can mass from the v9 STEP, the v8 fin-can export disabled, a v10 END block.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Any FAIL line means do not print.
"""
import os, builtins
import Part
_MD10 = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models"
V8_SRC10 = os.path.join(_MD10, "PhoenixABS40-43_D9aft_v8.py")
def _rd10(n):
    s = Part.Shape(); s.read(os.path.join(_MD10, n))
    return s.Solids[0] if len(s.Solids) == 1 else s
T9_TUBE = _rd10("PhoenixABS40-43_D9aft_v9_AftTube.step")             # Zf frame = the v6 frame (z 0 = fin-can aft face)
T9_FC = _rd10("PhoenixABS40-43_D9aft_v9_AftFinCanSlotted.step")
V8_LO_TIP = 227.6                                                     # v8 report: liftoff CG, mm from the tip

def _sub10(src, pairs, what):
    for a, b in pairs:
        assert src.count(a) == 1, "%s patch target not unique / missing: %r" % (what, a)
        src = src.replace(a, b)
    return src
def _v10_v7(src):
    return _sub10(src, [
        ('\'SLED_V6 = "PhoenixABS40-43_avbay_sled_v7.py"\'', '\'SLED_V6 = "PhoenixABS40-43_avbay_sled_v8.py"\''),
        ('\'NAME6 + "_ElectronicsSled_v7.stl"\'', '\'NAME6 + "_ElectronicsSled_v8.stl"\''),
        ('\'solid("ElectronicsSled v7"\'', '\'solid("ElectronicsSled v8"\''),
        ('\'"%s e-bay interference (EbayCap, sled v7,\'', '\'"%s e-bay interference (EbayCap, sled v8,\''),
    ], "v7")
def _v10_pre_v6(src):
    return _sub10(src, [
        ('solid("AftTube v6 (chute bay, launch lug, pin slots)", "airframe", P3[\'AftTube\'], "ABS")',
         'solid("AftTube v6 (chute bay, launch lug, pin slots)", "airframe", T9_TUBE, "ABS")'),
        ('for nm, p in PINS.items(): solid("Shear %s" % nm, "aft", p, "ABS")', 'pass  # v10: no shear pins (v9 snap latch)'),
        # P3['AftTube'] is still the pin-slot tube of the recipe: never export it under a v10 name (the flight AftTube is the v9 STEP)
        ("for k in ('FwdTube', 'AftTube', 'EbayCap'):\n    P3[k].exportStep(", "for k in ('FwdTube', 'EbayCap'):\n    P3[k].exportStep("),
    ], "v6")

_END10 = r'''
# =====================================================================================
# v10: SLED v8, PARTS vs v8, MASS / CG
# =====================================================================================
rep("")
rep("V10 CHECKS (sled v8; flight AftTube + fin can = the v9 STEPs)")
rep("%s sled v8 loaded: components %s" % (ok('Nano_joints' in [n for n, _ in SL['COMPONENTS']]), [n for n, _ in SL['COMPONENTS']]))
for _k10 in ('FwdTube', 'EbayCap'):
    _s8 = Part.Shape(); _s8.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v8_%s.step" % _k10))
    _d = P3[_k10].cut(_s8).Volume + _s8.cut(P3[_k10]).Volume
    rep("%s %s v10 vs v8 STEP: symmetric difference %.3f mm3 -> %s" % (ok(_d < 0.01), _k10, _d, "IDENTICAL, print/keep the v8 (= v6 cap) part" if _d < 0.01 else "CHANGED"))
_trap10 = [p for p in (os.path.join(MODELS, NAME6 + "_AftTube.step"), os.path.join(PRINT_RAW, NAME6 + "_AftTube.stl"), os.path.join(PRINT_READY, NAME6 + "_AftTube.stl")) if os.path.exists(p)]
rep("%s no v10 AftTube file exported (the recipe's tube still has pin slots; the flight AftTube is the v9 STEP): %s" % (ok(not _trap10), _trap10 or "none"))
_bad10 = [(k, round(v, 3)) for k, v in ((k, s.common(T9_TUBE).Volume) for k, s in dict(fwd=fw_px3, **air_e).items()) if v > 1e-3]
rep("%s v9 AftTube vs FwdTube + whole e-bay: %s" % (ok(not _bad10), _bad10 or "no contact"))
_sl = [i for i in items if i[0].startswith("ElectronicsSled")]
rep("NOTE sled v8 in the rollup: %.1f g (v7 15.0 g); AftTube = v9 STEP %.1f g; fin can (v9) + fins + epoxy %.1f g; no pins" % (_sl[0][2] if _sl else -1, T9_TUBE.Volume * RHO['ABS'], FINCAN_V8['m']))
lo10 = station(lo_z) + NOSE_LEN
need10 = max(0.0, (lo10 - CG_GATE_TIP) / MM_PER_G)
rep("NOTE liftoff %.1f g, CG tip %.1f (v8 %.1f). Gate %.0f -> %s" % (lo_m, lo10, V8_LO_TIP, CG_GATE_TIP,
    "inside the gate" if need10 == 0 else "~%.0f g EbayCap ballast just to reach it, plus a cushion (%.1f mm/g, line ASSUMED %.0f g) -- weigh the line, balance the built rocket" % (math.ceil(need10), MM_PER_G, LINE_G)))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT v10: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))
'''

_s8src = builtins.open(V8_SRC10, encoding="utf-8").read()
_s8src = _sub10(_s8src, [
    ('_s7 = builtins.open(V7_SRC8, encoding="utf-8").read()', '_s7 = _v10_v7(builtins.open(V7_SRC8, encoding="utf-8").read())'),
    ('def _v8_pre_v6(src):\n    for a, b in [', 'def _v8_pre_v6(src):\n    src = _v10_pre_v6(src)\n    for a, b in ['),
    ('NAME6, REV6 = "PhoenixABS40-43_D9aft_v8", "D9aft_v8"', 'NAME6, REV6 = "PhoenixABS40-43_D9aft_v10", "D9aft_v10"'),
    ('App.newDocument("Phoenix_D9aft_v8")', 'App.newDocument("Phoenix_D9aft_v10")'),
    ('v7 + 5 mm retention line tied direct: eyelet 6.5 openings, fin-can staple lug (sled v7,',
     'v8 on sled v8 + v9 snap-latch AftTube / fin can (5 mm line anchors as v8; sled v8,'),
    ('solid("AftTube v8 = v6 (chute bay, launch lug, pin slots)"', 'solid("AftTube v9 (snap-latch tongues, launch lug)"'),
    ("dm8 = (fcB.Volume - v4_fc_v) * RHO['ABS']", "dm8 = (T9_FC.Volume - v4_fc_v) * RHO['ABS']"),
    ('AftFinCanSlotted v8 + 3 fins + epoxy', 'AftFinCanSlotted v9 + 3 fins + epoxy'),
    ('v4 report + v8 staple-lug delta', 'v4 report + v9 STEP delta'),
    ('rep("NOTE slotted fin can v8 vs v4 STEP:', 'rep("NOTE flight fin can (v9 STEP: staple + latch windows) vs v4 STEP:'),
    ('fcB.exportStep(', 'pass  # v10: the flight fin can is the v9 STEP -- fcB.exportStep('),
    ('MeshPart.meshFromShape(Shape=fcB, ', 'pass  # MeshPart.meshFromShape(Shape=fcB, '),
    ('MeshPart.meshFromShape(Shape=fc_print, ', 'pass  # MeshPart.meshFromShape(Shape=fc_print, '),
    ("'_src = _src[:_k] + _v7_checks + _END8 + _src[_k:]'", "'_src = _src[:_k] + _v7_checks + _END8 + _END10 + _src[_k:]'"),
], "v8")
exec(_s8src)

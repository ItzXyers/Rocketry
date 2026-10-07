# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v7: the v6 rocket rebuilt around ELECTRONICS SLED v7.

User, 2026-10-07: piezo standoffs dropped, screws kept, board mounted SIDEWAYS (KY-006 pins need
bend room) -> Avionics/PhoenixABS40-43_avbay_sled_v7.py; then "adjust E-bay etc to match".

Sled v7 keeps every interface D9aft reads: seat plane Z -22.8, sound port Z PIEZO_ZC -12.1 / 0 deg,
static port, EbayCap face + M2 bosses, spine key, reed (ARM mark).  So this file is D9aft v6
exec'd with sled v7 swapped in (v6 is NOT edited -- patched in memory, like v6 patches v5), and
the FwdTube / AftTube / EbayCap come out of the SAME recipe on the new sled.  The extra check at
the end compares them with the v6 STEPs: if they are identical the printed v6 tubes + cap are
still the flight parts and only the sled changes.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Any FAIL line means do not print.
"""
import os
V6_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v6.py"
V6_PATCHES = [
    ('SLED_V6 = "PhoenixABS40-43_avbay_sled_v6.py"', 'SLED_V6 = "PhoenixABS40-43_avbay_sled_v7.py"'),
    ('NAME6, REV6 = "PhoenixABS40-43_D9aft_v6", "D9aft_v6"', 'NAME6, REV6 = "PhoenixABS40-43_D9aft_v7", "D9aft_v7"'),
    ('NAME6 + "_ElectronicsSled_v6.stl"', 'NAME6 + "_ElectronicsSled_v7.stl"'),
    ('App.newDocument("Phoenix_D9aft_v6")', 'App.newDocument("Phoenix_D9aft_v7")'),
    ('rep("== Phoenix ABS 40-43 -- %s: sled v6 (e-bay +%.1f mm, FwdTube resized), 150 mm chute bay, ports on the new sled ==" % (REV6, SL[\'DECK_DZ\']))',
     'rep("== Phoenix ABS 40-43 -- %s: v6 rebuilt on sled v7 (piezo sideways, flat on the plate, pin bay; e-bay +%.1f mm as v6), 150 mm chute bay ==" % (REV6, SL[\'DECK_DZ\']))'),
    ('"E-BAY: sled v6 + electronics', '"E-BAY: sled v7 + electronics'),
    ("('FwdTube v6', P3['FwdTube']), ('FwdTube v6 proxy', fw_px3), ('AftTube v6', P3['AftTube']), ('EbayCap v6', P3['EbayCap']), ('sled v6', sled2)",
     "('FwdTube v7', P3['FwdTube']), ('FwdTube v7 proxy', fw_px3), ('AftTube v7', P3['AftTube']), ('EbayCap v7', P3['EbayCap']), ('sled v7', sled2)"),
    ('rep("NOTE sled v6 loaded:', 'rep("NOTE sled v7 loaded:'),
    ("# --- ports + ARM mark lined up on sled v6", "# --- ports + ARM mark lined up on sled v7"),
    ('port = the sled v6 report\'s proposal', 'port = the sled v7 report\'s value'),
    ('"%s e-bay interference (EbayCap, sled v6,', '"%s e-bay interference (EbayCap, sled v7,'),
    ('"%s sled v6 floor stands on the seat ring', '"%s sled v7 floor stands on the seat ring'),
    ('rep("NOTE sled v6 printed floor down:', 'rep("NOTE sled v7 printed floor down:'),
    ('solid("FwdTube v6 (thread, seat, bulkhead, eyelet, ports, ARM)"', 'solid("FwdTube v7 (thread, seat, bulkhead, eyelet, ports, ARM)"'),
    ('solid("AftTube v6 (chute bay, launch lug, pin slots)"', 'solid("AftTube v7 (chute bay, launch lug, pin slots)"'),
    ('solid("EbayCap v6"', 'solid("EbayCap v7"'),
    ('solid("ElectronicsSled v6"', 'solid("ElectronicsSled v7"'),
]
_src = open(V6_SRC, encoding="utf-8").read()
for a, b in V6_PATCHES:
    assert _src.count(a) == 1, "v6 patch target not unique / missing: %r" % a
    _src = _src.replace(a, b)
# v6 ends by writing the report + "done"; insert the v7 checks before the report is written
_k = _src.index('with open(os.path.join(MODELS, NAME6 + "_report.txt")')
_v7_checks = r'''
# =====================================================================================
# v7: SLED v7 INTERFACES + v6 vs v7 PARTS
# =====================================================================================
rep("")
rep("V7 CHECKS")
assert 'PIEZO_Y1' in SL, "sled v7 not loaded"
rep("%s sled v7 interfaces = v6: seat Z %.2f (v6 -22.80), sound port Z %.2f (v6 -12.10), EbayCap face %.1f (v6 45.4)"
    % (ok(abs(SL['SEAT_Z'] + 22.8) < 1e-9 and abs(SL['PIEZO_ZC'] + 12.1) < 1e-9 and abs(SL['CAP_Z0'] - 45.4) < 1e-9), SL['SEAT_Z'], SL['PIEZO_ZC'], SL['CAP_Z0']))
_pb = SL['pin_bay']().translated(V(0, 0, SLED_Z2))
_pbh = [(k, round(v, 3)) for k, v in ((k, s.common(_pb).Volume) for k, s in dict(fwd=fw_px3, ebaycap=P3['EbayCap'], sled=sled2, **{kk: vv for kk, vv in ENV2.items() if kk != 'Piezo'}).items()) if v > 1e-3]
rep("%s piezo pin bay (bend + heat shrink room) empty in the assembled e-bay: %s" % (ok(not _pbh), _pbh or "empty"))
for _k6 in ('FwdTube', 'AftTube', 'EbayCap'):
    _s6 = Part.Shape(); _s6.read(os.path.join(MODELS, "PhoenixABS40-43_D9aft_v6_%s.step" % _k6))
    _s7 = P3[_k6]
    _d = _s7.cut(_s6).Volume + _s6.cut(_s7).Volume
    rep("NOTE %s v7 vs v6 STEP: volume %.2f vs %.2f mm3, symmetric difference %.3f mm3 -> %s"
        % (_k6, _s7.Volume, _s6.Volume, _d, "IDENTICAL, the printed v6 part is the v7 part" if _d < 0.01 else "CHANGED -- reprint"))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT v7: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))
'''
_src = _src[:_k] + _v7_checks + _src[_k:]
exec(_src)

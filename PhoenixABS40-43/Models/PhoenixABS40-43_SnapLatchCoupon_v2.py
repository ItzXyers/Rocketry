# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- SNAP-LATCH TEST COUPON v2 = v1 with a taller aft band, L24 only.

v1 L24 print feedback (2026-10-07): first pull 873 g = 8.6 N per pair (prediction 12.1 N). Tongue tip fine,
but the 4 mm aft band over the 1.0 mm aft gap curled up and out near the tongue tip (bridge start at the
end slot; ABS not dried). It was like that from the print and rubs the coupler on insertion -> part of the
873 g may be friction.

Changes vs v1 (v1 file is exec'd read-only with these substitutions):
  * BAND_AFT 4.0 -> 7.0: a stiffer band over the aft-gap bridge. Bump + window move 3 mm forward together,
    so the v2 CouplerRing must be used with the v2 TubeRing (the v1 coupler does not latch in it).
  * VARIANTS -> (24,) only (the user's pick); L24 footprint still ends inside the 40 mm flight coupler.
  * NAME -> _v2 (no v1 output is overwritten).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
"""
import os
_V1 = os.path.join(r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models", "PhoenixABS40-43_SnapLatchCoupon_v1.py")
_src = open(_V1, encoding="utf-8").read()
for _a, _b in [
    ('NAME = "PhoenixABS40-43_SnapLatchCoupon_v1"', 'NAME = "PhoenixABS40-43_SnapLatchCoupon_v2"'),
    ("BAND_AFT = 4.0 ", "BAND_AFT = 7.0 "),
    ("VARIANTS = (20.0, 24.0, 28.0, 32.0)", "VARIANTS = (24.0,)"),
    ('rep("SNAP-LATCH TEST COUPON v1 --', 'rep("SNAP-LATCH TEST COUPON v2 (v1 + aft band 4 -> 7 mm, L24 only; use the v2 coupler) --'),
    ('App.newDocument("SnapLatchCoupon_v1")', 'App.newDocument("SnapLatchCoupon_v2")'),
]:
    assert _src.count(_a) == 1, _a
    _src = _src.replace(_a, _b)
exec(compile(_src, _V1 + " [patched to v2]", "exec"))

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- low-drag separating nosecone for the T5 airframe, v5

SOURCE OF TRUTH. Every dimension is a named constant below; edit here and
re-run, never edit the STL/STEP/FCStd by hand. v4 (keel + bow door) is kept
for history and is NOT superseded in place -- v5 targets a different airframe:
Ejection System T5's integrated forward section (plain 40 mm bore, nose shoulder
at stations 0-20, canopy bay 20-110), where the whole nose separates and is the
extractor. See NOSE_V5_AERO.md for the aerodynamic analysis that picked the shape.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

Frame: Z = 0 at the nose tip, +Z aft (same as v4). Body-tube station s = Z - L_NOSE.

Shape: Von Karman (Haack series, C = 0), L = 65 mm (L/D 1.51), tangent to the
43.00 mm airframe at the base. OpenRocket 24.12 ranks it the lowest-drag
base-tangent shape at every length tried (aero/nose_sweep_*.csv).
"""

import os
import math

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

# ---------------------------------------------------------------- parameters

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
NOSECONE = os.path.join(PROJECT, "Nosecone")
MODELS = os.path.join(NOSECONE, "Models")
PRINTS = os.path.join(PROJECT, "Print Files", "Nosecone")
PRINTS_READY = os.path.join(PRINTS, "Ready to Print")
REV = "v5"

RHO = 1.05e-3                 # g/mm^3, ABS/ASA solid (DESIGN 8: nose 100 % infill)

# --- airframe (DESIGN 2.1, T5 README 6) ---
R = 21.50                     # airframe OD / 2
R_BORE = 20.00                # T5 fwd_section bore / 2

# --- aero profile ---
L_NOSE = 65.0                 # nose length, tip -> base (L/D = 1.51)
HAACK_C = 0.0                 # 0 = Von Karman (LD-Haack), 1/3 = LV-Haack
N_PROFILE = 120               # spline stations (cosine-spaced, dense at tip and base)

# --- shell / cavity ---
WALL = 2.0                    # min normal wall of the aero shell
CAVITY_APEX_Z = 10.0          # 45 deg cavity cone starts here -> solid tip (ballast + print)

# --- shoulder (DESIGN 7.4 / 8.4 / 9) ---
SH_LEN = 42.0                 # >= 1 x body dia (DESIGN 9)
SH_R = 19.85                  # contact bands, dia 39.70 in the 40.00 bore (0.30 diametral)
SH_RELIEF_R = 19.60           # relieved middle, dia 39.20 -- alignment only, no friction
SH_BAND_F = 12.0              # forward contact band length
SH_BAND_A = 10.0              # aft contact band length
SH_LEAD = 0.6                 # 45 deg lead-in chamfer at the aft end
SH_WALL = 1.5
SH_R_IN = SH_R - SH_WALL      # 18.35

# --- detent ring + 3 ball-plunger pilots (DESIGN 7.4, preferred option) ---
RING_R_IN = 8.0               # ring bore -> 16 mm pour/fill passage to the tip
RING_LEN = 14.0               # straight length below the nose base (then a 45 deg chamfer)
DETENT_STATION = 8.0          # body station of the plunger axis (groove in T5 bore goes here)
DETENT_PILOT_D = 4.2          # M5 ball plunger, self-tapped / epoxied into the pilot
DETENT_DEPTH = 10.0           # from the shoulder OD, blind
DETENT_ANGLES = (90.0, 210.0, 330.0)

# --- shock-cord anchor: hardened d4 dowel across two bosses (tether nose -> cord -> canopy) ---
PIN_D_HOLE = 4.10
PIN_FROM_AFT = 6.0            # pin axis above the shoulder's aft face
BOSS_R_IN = 10.0              # boss inner face radius -> 20 mm pin span
BOSS_W = 10.0                 # boss width (X)
BOSS_H = 12.0                 # boss height from the aft face
PIN_BLIND_SKIN = 1.0          # blind end stops this far inside the OD on -Y

# --- mass / ballast reporting ---
BALLAST_RHO = 7.0e-3          # g/mm^3, lead shot in epoxy (~60 % packing)

# ---------------------------------------------------------------- derived

Z_BASE = L_NOSE
Z_SH_END = L_NOSE + SH_LEN


def haack_r(z):
    """Haack-series radius at axial position z from the tip (0 <= z <= L)."""
    z = min(max(z, 0.0), L_NOSE)
    th = math.acos(1.0 - 2.0 * z / L_NOSE)
    v = th - math.sin(2.0 * th) / 2.0 + HAACK_C * math.sin(th) ** 3
    return R / math.sqrt(math.pi) * math.sqrt(max(v, 0.0))


def haack_slope(z, h=1e-4):
    z0, z1 = max(z - h, 0.0), min(z + h, L_NOSE)
    return (haack_r(z1) - haack_r(z0)) / (z1 - z0)


def cavity_r(z):
    """Inner radius: normal-offset shell, clamped by a 45 deg apex cone and the shoulder bore."""
    if z <= CAVITY_APEX_Z:
        return 0.0
    cone = z - CAVITY_APEX_Z
    if z >= Z_BASE:
        return min(cone, SH_R_IN)
    s = haack_slope(z)
    off = haack_r(z) - WALL * math.sqrt(1.0 + s * s)
    return max(0.0, min(off, cone, SH_R_IN))


def profile_z():
    # cosine spacing in theta is the natural Haack parameter: dense at both ends
    return [L_NOSE * (1.0 - math.cos(math.pi * i / (N_PROFILE - 1))) / 2.0 for i in range(N_PROFILE)]


def revolve(pts):
    """Closed polyline/spline profile in the XZ plane (x = r) -> solid of revolution about Z."""
    wire = Part.makePolygon(pts) if isinstance(pts, list) else pts
    face = Part.Face(wire)
    return face.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360.0)


# ---------------------------------------------------------------- build

report = []
fails = []


def rep(line=""):
    report.append(line)
    print(line)


def check(ok, label):
    rep(("[PASS] " if ok else "[FAIL] ") + label)
    if not ok:
        fails.append(label)


def build_outer():
    zs = profile_z()
    nose_pts = [Vector(haack_r(z), 0, z) for z in zs]
    nose_pts[0] = Vector(0, 0, 0)
    spline = Part.BSplineCurve()
    spline.interpolate(nose_pts)
    e_nose = spline.toShape()

    s_f = Z_BASE + SH_BAND_F
    s_a = Z_SH_END - SH_BAND_A
    poly = [
        Vector(R, 0, Z_BASE),
        Vector(SH_R, 0, Z_BASE),
        Vector(SH_R, 0, s_f),
        Vector(SH_RELIEF_R, 0, s_f + (SH_R - SH_RELIEF_R)),      # 45 deg steps
        Vector(SH_RELIEF_R, 0, s_a - (SH_R - SH_RELIEF_R)),
        Vector(SH_R, 0, s_a),
        Vector(SH_R, 0, Z_SH_END - SH_LEAD),
        Vector(SH_R - SH_LEAD, 0, Z_SH_END),
        Vector(0, 0, Z_SH_END),
        Vector(0, 0, 0),
    ]
    edges = [e_nose] + [Part.LineSegment(poly[i], poly[i + 1]).toShape() for i in range(len(poly) - 1)]
    return revolve(Part.Wire(edges))


def build_cavity():
    zs = [CAVITY_APEX_Z + i * 0.25 for i in range(int((Z_SH_END - CAVITY_APEX_Z) / 0.25) + 1)]
    pts = [Vector(0, 0, CAVITY_APEX_Z)]
    for z in zs[1:]:
        pts.append(Vector(cavity_r(z), 0, z))
    pts.append(Vector(SH_R_IN, 0, Z_SH_END + 1.0))     # open aft
    pts.append(Vector(0, 0, Z_SH_END + 1.0))
    pts.append(Vector(0, 0, CAVITY_APEX_Z))
    # drop consecutive duplicates
    clean = [pts[0]]
    for p in pts[1:]:
        if (p - clean[-1]).Length > 1e-6:
            clean.append(p)
    return revolve(clean)


def build_ring():
    z0 = Z_BASE
    z1 = Z_BASE + RING_LEN
    z2 = z1 + (SH_R_IN - RING_R_IN)                   # 45 deg underside, self-supporting tip-up
    pts = [
        Vector(RING_R_IN, 0, z0),
        Vector(SH_R_IN + 0.3, 0, z0),                  # 0.3 overlap into the wall
        Vector(SH_R_IN + 0.3, 0, z2),
        Vector(SH_R_IN, 0, z2),
        Vector(RING_R_IN, 0, z1),
        Vector(RING_R_IN, 0, z0),
    ]
    return revolve(pts), z2


def build_anchor_bosses():
    z0 = Z_SH_END - BOSS_H
    bosses = []
    for sgn in (+1, -1):
        y_in = sgn * BOSS_R_IN
        y_out = sgn * (SH_R_IN + 0.3)
        y_lo = min(y_in, y_out)
        box = Part.makeBox(BOSS_W, abs(y_out - y_in), BOSS_H, Vector(-BOSS_W / 2, y_lo, z0))
        # trim to the shoulder bore so nothing pokes past the wall
        bosses.append(box.common(Part.makeCylinder(SH_R_IN + 0.3, BOSS_H, Vector(0, 0, z0))))
    return bosses[0].fuse(bosses[1])


def build_pin_hole():
    z = Z_SH_END - PIN_FROM_AFT
    y_blind = -(SH_R - PIN_BLIND_SKIN)
    length = (R + 1.0) - y_blind
    return Part.makeCylinder(PIN_D_HOLE / 2, length, Vector(0, y_blind, z), Vector(0, 1, 0))


def build_detent_pilots():
    z = Z_BASE + DETENT_STATION
    holes = []
    for a in DETENT_ANGLES:
        d = Vector(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        start = Vector(d.x * (SH_R + 1.0), d.y * (SH_R + 1.0), z)
        holes.append(Part.makeCylinder(DETENT_PILOT_D / 2, DETENT_DEPTH + 1.0, start, d * -1))
    out = holes[0]
    for h in holes[1:]:
        out = out.fuse(h)
    return out


rep("Phoenix ABS 40-43 -- Nosecone v5 (Von Karman, T5 separating nose) -- build report")
rep("Generated by PhoenixABS40-43_Nosecone_v5.py via FreeCADCmd. Z = 0 at tip, +Z aft; station = Z - %.1f." % L_NOSE)
rep()

outer = build_outer()
cavity = build_cavity()
ring, ring_z2 = build_ring()
bosses = build_anchor_bosses()

nose = outer.cut(cavity).fuse(ring).fuse(bosses)
nose = nose.cut(build_pin_hole()).cut(build_detent_pilots())
nose = nose.removeSplitter()
n_solids = len(nose.Solids)
if n_solids == 1:
    nose = nose.Solids[0]

rep("GEOMETRY CHECKS")
check(nose.isValid(), "solid is valid")
check(n_solids == 1, "single solid (solids = %d)" % n_solids)

bb = nose.BoundBox
check(abs(bb.ZMin) < 1e-3 and abs(bb.ZMax - Z_SH_END) < 1e-3,
      "overall Z 0.00 .. %.2f (nose %.1f + shoulder %.1f)" % (bb.ZMax, L_NOSE, SH_LEN))
r_max = max(bb.XMax, bb.YMax, -bb.XMin, -bb.YMin)
check(r_max <= R + 0.01, "max radius %.3f <= airframe R %.2f (nothing proud)" % (r_max, R))

# base radius / tangency, measured on the solid (section just fwd of the base)
sec = nose.slice(Vector(0, 0, 1), Z_BASE - 0.05)
r_base = max(e.BoundBox.XMax for w in sec for e in w.Edges)
check(abs(r_base - R) < 0.02, "base OD %.3f mm vs airframe 43.000 (step %.3f mm)" % (2 * r_base, 2 * (R - r_base)))
slope_base = math.degrees(math.atan(haack_slope(Z_BASE - 0.25)))
check(slope_base < 2.0, "surface angle 0.25 mm fwd of the joint: %.2f deg (tangent -> 0)" % slope_base)

# shoulder bands and relief, measured on the solid
def solid_r_at(z):
    s = nose.slice(Vector(0, 0, 1), z)
    return max(e.BoundBox.XMax for w in s for e in w.Edges)

r_band_f = solid_r_at(Z_BASE + SH_BAND_F / 2)
r_relief = solid_r_at((Z_BASE + SH_BAND_F + Z_SH_END - SH_BAND_A) / 2)
r_band_a = solid_r_at(Z_SH_END - SH_BAND_A / 2)
check(abs(2 * r_band_f - 39.70) < 0.02 and abs(2 * r_band_a - 39.70) < 0.02,
      "shoulder contact bands dia %.2f / %.2f in the 40.00 bore (DESIGN 8.4: 39.6-39.8)" % (2 * r_band_f, 2 * r_band_a))
check(abs(2 * r_relief - 2 * SH_RELIEF_R) < 0.02, "relieved middle dia %.2f (no friction, alignment only)" % (2 * r_relief))
check(SH_LEN >= 42.0, "shoulder engagement %.1f mm >= 42 (DESIGN 9)" % SH_LEN)

# wall thickness along the aero shell (normal), sampled
min_wall, min_wall_z = 1e9, None
z = CAVITY_APEX_Z + 0.5
while z < Z_BASE:
    s = haack_slope(z)
    t = (haack_r(z) - cavity_r(z)) / math.sqrt(1.0 + s * s)
    if t < min_wall:
        min_wall, min_wall_z = t, z
    z += 0.25
rep("[INFO] min normal shell wall %.2f mm at Z %.1f (target %.1f; analytic, from the profile that built the solid)" % (min_wall, min_wall_z, WALL))
# probe the solid itself: mid-wall must be material, just inside the cavity must be void
probe_bad = []
for zz in (15.0, 25.0, 40.0, 55.0, 62.0):
    s = haack_slope(zz)
    r_mid = haack_r(zz) - 0.5 * (haack_r(zz) - cavity_r(zz))
    if not nose.isInside(Vector(r_mid, 0, zz), 1e-6, True):
        probe_bad.append("wall@Z%.0f" % zz)
    if cavity_r(zz) > 0.6 and nose.isInside(Vector(cavity_r(zz) - 0.5, 0, zz), 1e-6, True):
        probe_bad.append("cavity@Z%.0f" % zz)
check(not probe_bad, "solid probe: shell material mid-wall and cavity open at Z 15/25/40/55/62 %s" % (probe_bad or ""))
check(nose.isInside(Vector(0, 0, CAVITY_APEX_Z - 1.0), 1e-6, True), "solid probe: tip solid forward of the funnel apex (Z %.0f)" % (CAVITY_APEX_Z - 1))

# print: tip-up, cavity must never overhang more than 45 deg from vertical
worst = 0.0
z = CAVITY_APEX_Z + 0.25
while z < Z_SH_END:
    d = abs(cavity_r(z) - cavity_r(z - 0.25)) / 0.25
    worst = max(worst, d)
    z += 0.25
rep("[INFO] cavity self-supporting tip-up: steepest wall %.1f deg from vertical (<= 45; analytic)" % math.degrees(math.atan(worst)))
if worst > 1.0 + 1e-6:
    check(False, "cavity overhang exceeds 45 deg")
rep("[NOTE] base ledge %.2f mm (r %.2f -> %.2f) prints as a short overhang tip-up; it must stay a flat seat face" % (R - SH_R, SH_R, R))
rep("[NOTE] tip is modeled sharp; FDM rounds it to ~0.4 mm radius -- aerodynamically free at M < 0.3")

# anchor / detent clearance
check(Z_BASE + DETENT_STATION + DETENT_PILOT_D / 2 <= Z_BASE + SH_BAND_F,
      "detent pilots (station %.1f) sit inside the forward contact band" % DETENT_STATION)
z_det = Z_BASE + DETENT_STATION
det_bad = []
for a in DETENT_ANGLES:
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    if nose.isInside(Vector(c * (SH_R - 0.5), s_ * (SH_R - 0.5), z_det), 1e-6, True):
        det_bad.append("pilot %g closed at OD" % a)
    if nose.isInside(Vector(c * (SH_R - DETENT_DEPTH + 0.5), s_ * (SH_R - DETENT_DEPTH + 0.5), z_det), 1e-6, True):
        det_bad.append("pilot %g short of depth" % a)
    if not nose.isInside(Vector(c * (RING_R_IN + 0.5), s_ * (RING_R_IN + 0.5), z_det), 1e-6, True):
        det_bad.append("pilot %g breaks through the ring" % a)
check(not det_bad, "solid probe: 3 detent pilots open at the OD, full %.0f mm deep, blind (%.2f mm floor) %s"
      % (DETENT_DEPTH, (SH_R - DETENT_DEPTH) - RING_R_IN, det_bad or ""))
check(ring_z2 < Z_SH_END - BOSS_H, "detent ring (to Z %.1f) clear of anchor bosses (from Z %.1f)" % (ring_z2, Z_SH_END - BOSS_H))
z_pin = Z_SH_END - PIN_FROM_AFT
pin_ok = (not nose.isInside(Vector(0, SH_R - 0.5, z_pin), 1e-6, True)          # +Y entry open
          and not nose.isInside(Vector(0, -(SH_R - PIN_BLIND_SKIN - 0.3), z_pin), 1e-6, True)  # hole reaches -Y boss
          and nose.isInside(Vector(0, -(SH_R - 0.5), z_pin), 1e-6, True)        # -Y skin intact (blind)
          and nose.isInside(Vector(0, BOSS_R_IN + 1.0, z_pin + PIN_D_HOLE), 1e-6, True))  # boss material above pin
check(pin_ok, "solid probe: anchor pin hole open at +Y OD, blind on -Y (%.1f mm skin), bosses present" % PIN_BLIND_SKIN)
pin_len = (SH_R) + (SH_R - PIN_BLIND_SKIN)
rep("[INFO] anchor dowel length: flush at +Y to the blind end = %.1f mm -> use d4 x %.1f hardened dowel" % (pin_len, math.floor(pin_len * 2) / 2 - 0.0))
pin_span = 2 * BOSS_R_IN
m_pin = 250.0 * pin_span / 4.0
sigma = m_pin / (math.pi * 4.0 ** 3 / 32.0)
rep("[INFO] anchor: d4 dowel, %.0f mm span, 250 N snatch placeholder (T5 README) -> %.0f MPa bending: needs a HARDENED dowel" % (pin_span, sigma))
bear = 250.0 / 2 / (4.0 * (SH_R_IN - BOSS_R_IN + SH_WALL))
rep("[INFO] anchor boss bearing %.1f MPa per side at 250 N (ABS ~40 MPa)" % bear)

rep()
rep("MASS (solid %s, rho %.2f g/cm3)" % ("ABS/ASA", RHO * 1000))
vol = nose.Volume
mass = vol * RHO
cg = nose.CenterOfMass.z
rep("  volume      %10.1f mm3" % vol)
rep("  mass        %10.1f g" % mass)
rep("  CG          %10.1f mm from tip (station %.1f)" % (cg, cg - L_NOSE))

# ballast funnel: cavity volume forward of Z_b, lead-shot/epoxy fill
for zb in (20.0, 25.0, 30.0):
    fill = cavity.common(Part.makeCylinder(30, zb - CAVITY_APEX_Z, Vector(0, 0, CAVITY_APEX_Z)))
    fz = sum(s.Volume * s.CenterOfMass.z for s in fill.Solids) / fill.Volume
    rep("  ballast fill to Z %.0f: %6.0f mm3 -> %5.1f g lead/epoxy, centroid Z %.1f"
        % (zb, fill.Volume, fill.Volume * BALLAST_RHO, fz))

rep()
rep("RESULT: %s" % ("ALL PASS (0 FAIL)" if not fails else "%d FAIL: %s" % (len(fails), "; ".join(fails))))

# ---------------------------------------------------------------- export

for d in (MODELS, PRINTS, PRINTS_READY):
    os.makedirs(d, exist_ok=True)

name = "PhoenixABS40-43_nose_VonKarman_%s" % REV
step_path = os.path.join(MODELS, name + ".step")
nose.exportStep(step_path)
mesh = MeshPart.meshFromShape(Shape=nose, LinearDeflection=0.02, AngularDeflection=0.1)
mesh.write(os.path.join(MODELS, name + ".stl"))
mesh.write(os.path.join(PRINTS, name + ".stl"))

# print orientation: tip UP, shoulder aft face on the bed at Z = 0
printed = nose.copy()
printed.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 180)
printed.translate(Vector(0, 0, -printed.BoundBox.ZMin))
MeshPart.meshFromShape(Shape=printed, LinearDeflection=0.02, AngularDeflection=0.1).write(
    os.path.join(PRINTS_READY, name + ".stl"))

# half-profile for plotting / docs
with open(os.path.join(MODELS, name + "_profile.csv"), "w") as f:
    f.write("z_mm,r_outer_mm,r_inner_mm\n")
    for zz in [i * 0.25 for i in range(int(Z_BASE / 0.25) + 1)]:
        f.write("%.3f,%.4f,%.4f\n" % (zz, haack_r(zz), cavity_r(zz)))

doc = App.newDocument("Nosecone_" + REV)
obj = doc.addObject("Part::Feature", "Nose_VonKarman")
obj.Shape = nose
doc.recompute()
fcstd_path = os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_%s.FCStd" % REV)
doc.saveAs(fcstd_path)

rep()
rep("FILES")
rep("  Models/%s.step / .stl / _profile.csv" % name)
rep("  Print Files/Nosecone/%s.stl (as modeled) + Ready to Print/ (tip up, shoulder on bed)" % name)
rep("  PhoenixABS40-43_Nosecone_%s.FCStd" % REV)

with open(os.path.join(NOSECONE, "nosecone_build_report_%s.txt" % REV), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- nosecone v6: SIMPLE SCREW-ON NOSE for the D9aft airframe.

v6 is v5's aero shape with everything else taken off, plus a thread:
  kept    Von Karman (Haack C = 0), L = 65 mm, tangent to the 43.0 airframe; 2.0 mm normal shell wall;
          solid tip forward of a 45 deg cavity apex (prints tip-up without support)
  removed detent pilots, harness anchor bosses + dowel, ballast pour ring, relieved shoulder bands,
          the 42 mm friction shoulder -- the nose never separates on D9aft (aft deployment)
  added   a 9.5 mm male thread (pitch 3.0, 45 deg flanks, 0.8 deep) that screws into the FwdTube mouth.
          Unscrew by hand -> the e-bay lifts straight out of the open tube (D9aft v2).

Thread: the helix is aft_retention_v1's faceted thread_solid() (exact pitch, planar faces), exec'd with
this file's THREAD constants -- the female half in PhoenixABS40-43_D9aft_v2.py uses the same dict.

Run headless (writes the part):
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>
As a library: exec with NOSE_V6_LIB = True in the namespace -> defines build_nose(), THREAD, no export.

Frame: Z = 0 at the tip, +Z aft (as v5). Body-tube station = Z - 65.
"""
import os, math
import FreeCAD as App
import Part, MeshPart
from FreeCAD import Vector as V

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
NOSECONE = os.path.join(PROJECT, "Nosecone")
MODELS = os.path.join(NOSECONE, "Models")
PRINTS = os.path.join(PROJECT, "Print Files", "Nosecone")
REV = "v6"
RHO = 1.05e-3
AR_SRC = os.path.join(PROJECT, "Models", "PhoenixABS40-43_aft_retention_v1.py")

# ---------------------------------------------------------------- parameters
R = 21.50                 # airframe OD / 2
L_NOSE = 65.0
HAACK_C = 0.0
N_PROFILE = 120
WALL = 2.0
CAVITY_APEX_Z = 10.0

# male thread on the shoulder (female: FwdTube mouth, D9aft v2)
THREAD = dict(PITCH=3.0, T_DEPTH=0.8, T_CREST_W=0.8, T_FLANK=1.0,      # 45 deg flanks: self-supporting both halves
              RAD_CLEAR=0.2, FLANK_CLEAR=0.1,
              BOSS_R_MAJOR=20.25,                                      # male major  -> d40.50
              STEPS_PER_TURN=90, T_MERGE=0.4)
THREAD['BOSS_R_MINOR'] = THREAD['BOSS_R_MAJOR'] - THREAD['T_DEPTH']            # 19.45
THREAD['CAP_T_CREST_R'] = THREAD['BOSS_R_MINOR'] + THREAD['RAD_CLEAR']         # 19.65 female crest: d39.30 bore passes the sled (R 19.39)
THREAD['CAP_T_ROOT_R'] = THREAD['BOSS_R_MAJOR'] + THREAD['RAD_CLEAR']          # 20.45 female root: 1.05 mm skin to the OD
SH_LEN = 9.5              # threaded shoulder, Z 65 -> 74.5 (FwdTube channel runs to station 11)
SH_R_IN = 17.95           # shoulder bore (1.5 mm under the thread minor)
SH_OVERLAP = 0.6          # ring reaches this far forward into the shell (overlap, never touch)
TIP_CHAMFER = 0.6         # 45 deg lead-in on the shoulder end, truncates the first turn
Z_BASE = L_NOSE
Z_SH_END = L_NOSE + SH_LEN
T_ANCHOR_N = Z_BASE - SH_OVERLAP - THREAD['PITCH']    # male ridge centres at T_ANCHOR_N + k*PITCH at theta 0

# ---------------------------------------------------------------- thread library (aft_retention_v1, constants overridden)
_ar = open(AR_SRC, encoding="utf-8").read()
TH = {"__name__": "thread_lib"}
exec(_ar[:_ar.rstrip().rfind("main()")], TH)
TH.update(THREAD)

# ---------------------------------------------------------------- geometry
def haack_r(z):
    z = min(max(z, 0.0), L_NOSE)
    th = math.acos(1.0 - 2.0 * z / L_NOSE)
    v = th - math.sin(2.0 * th) / 2.0 + HAACK_C * math.sin(th) ** 3
    return R / math.sqrt(math.pi) * math.sqrt(max(v, 0.0))

def haack_slope(z, h=1e-4):
    z0, z1 = max(z - h, 0.0), min(z + h, L_NOSE)
    return (haack_r(z1) - haack_r(z0)) / (z1 - z0)

def cavity_r(z):
    """Normal-offset shell, clamped by the 45 deg apex cone (self-supporting tip-up)."""
    if z <= CAVITY_APEX_Z:
        return 0.0
    s = haack_slope(z)
    return max(0.0, min(haack_r(z) - WALL * math.sqrt(1.0 + s * s), z - CAVITY_APEX_Z))

def revolve(pts):
    wire = Part.makePolygon(pts) if isinstance(pts, list) else pts
    return Part.Face(wire).revolve(V(0, 0, 0), V(0, 0, 1), 360.0)

def build_shell():
    zs = [L_NOSE * (1.0 - math.cos(math.pi * i / (N_PROFILE - 1))) / 2.0 for i in range(N_PROFILE)]
    pts = [V(haack_r(z), 0, z) for z in zs]; pts[0] = V(0, 0, 0)
    sp = Part.BSplineCurve(); sp.interpolate(pts)
    edges = [sp.toShape(), Part.LineSegment(V(R, 0, Z_BASE), V(0, 0, Z_BASE)).toShape(),
             Part.LineSegment(V(0, 0, Z_BASE), V(0, 0, 0)).toShape()]
    outer = revolve(Part.Wire(edges))
    zc = [CAVITY_APEX_Z + 0.25 * i for i in range(int((Z_BASE - CAVITY_APEX_Z) / 0.25) + 1)]
    cp = [V(0, 0, CAVITY_APEX_Z)] + [V(cavity_r(z), 0, z) for z in zc[1:]] + [V(cavity_r(Z_BASE), 0, Z_BASE + 1), V(0, 0, Z_BASE + 1), V(0, 0, CAVITY_APEX_Z)]
    clean = [cp[0]]
    for p in cp[1:]:
        if (p - clean[-1]).Length > 1e-6: clean.append(p)
    return outer.cut(revolve(clean))                  # open aft: the cavity runs out through the base

def build_thread_ring(threaded=True):
    """Male threaded shoulder ring. Grooves are CUT from a plain major-diameter annulus (never fused)."""
    z0 = Z_BASE - SH_OVERLAP
    ring = revolve([V(SH_R_IN, 0, z0), V(THREAD['BOSS_R_MAJOR'], 0, z0), V(THREAD['BOSS_R_MAJOR'], 0, Z_SH_END), V(SH_R_IN, 0, Z_SH_END), V(SH_R_IN, 0, z0)])
    if threaded:
        h = (Z_SH_END - T_ANCHOR_N) + THREAD['PITCH']
        ring = ring.cut(TH['thread_solid'](THREAD['BOSS_R_MINOR'], T_ANCHOR_N, h, TH['groove_profile'](), phase_z=THREAD['PITCH'] / 2.0))
    r0 = THREAD['BOSS_R_MAJOR'] - TIP_CHAMFER
    ring = ring.cut(revolve([V(r0 - 6, 0, Z_SH_END + 6), V(30, 0, Z_SH_END - (30 - r0)), V(30, 0, Z_SH_END + 6), V(r0 - 6, 0, Z_SH_END + 6)]))
    return ring

def build_nose(threaded=True):
    s = build_shell().fuse(build_thread_ring(threaded))
    return TH['as_solid'](s)

# ---------------------------------------------------------------- build + checks + export
def main():
    rep = []
    fails = []
    def check(ok, label):
        rep.append(("[PASS] " if ok else "[FAIL] ") + label)
        if not ok: fails.append(label)
    def info(s): rep.append("[INFO] " + s)
    nose = build_nose(True)
    plain = build_nose(False)
    rep.append("Phoenix ABS 40-43 -- Nosecone v6 (simple screw-on Von Karman, D9aft) -- build report")
    rep.append("Generated by PhoenixABS40-43_Nosecone_v6.py via FreeCADCmd. Z = 0 at tip, +Z aft; station = Z - %.1f." % L_NOSE)
    rep.append("")
    check(nose.isValid() and len(nose.Solids) == 1, "solid valid, one solid (%d)" % len(nose.Solids))
    bb = plain.BoundBox
    check(abs(bb.ZMin) < 1e-6 and abs(bb.ZMax - Z_SH_END) < 0.01, "overall Z %.2f .. %.2f (nose %.1f + threaded shoulder %.1f)" % (bb.ZMin, bb.ZMax, L_NOSE, SH_LEN))
    m = MeshPart.meshFromShape(Shape=plain, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    rmax = max(math.hypot(p.x, p.y) for p in m.Points)
    check(rmax <= R + 0.01, "max radius %.3f <= airframe R %.2f (nothing proud)" % (rmax, R))
    check(abs(haack_r(Z_BASE) - R) < 1e-6 and abs(haack_slope(Z_BASE - 0.25)) < 0.05, "tangent to the airframe at the base (slope %.3f at 0.25 mm fwd)" % haack_slope(Z_BASE - 0.25))
    wmin = min(haack_r(z) - cavity_r(z) for z in [CAVITY_APEX_Z + 1 + 0.5 * i for i in range(int((Z_BASE - CAVITY_APEX_Z - 1) / 0.5))])
    info("min radial shell wall %.2f mm (normal wall %.1f)" % (wmin, WALL))
    # thread landed on the REAL part: probe groove and ridge at theta 0
    zr = T_ANCHOR_N + 2 * THREAD['PITCH']                 # a ridge centre inside the shoulder
    zg = zr + THREAD['PITCH'] / 2.0                       # the groove centre next to it
    pr = nose.isInside(V(THREAD['BOSS_R_MAJOR'] - 0.2, 0, zr), 1e-4, True)
    pg = nose.isInside(V(THREAD['BOSS_R_MINOR'] + 0.2, 0, zg), 1e-4, True)
    pc = nose.isInside(V(THREAD['BOSS_R_MINOR'] - 0.4, 0, zg), 1e-4, True)
    check(pr and not pg and pc, "thread probes at theta 0: ridge solid at Z %.2f %s, groove open at Z %.2f %s, core solid %s" % (zr, pr, zg, not pg, pc))
    check(abs((plain.Volume - nose.Volume) - 0.0) > 50, "thread grooves removed %.0f mm3 from the plain shoulder" % (plain.Volume - nose.Volume))
    check(not nose.isInside(V(0, 0, Z_BASE + 1), 1e-4, True) and not nose.isInside(V(18.5, 0, 40), 1e-4, True), "hollow: open shoulder bore d%.1f and cavity" % (2 * SH_R_IN))
    check(nose.isInside(V(0, 0, CAVITY_APEX_Z - 2), 1e-4, True), "solid tip forward of the cavity apex (Z %.0f)" % CAVITY_APEX_Z)
    info("thread: pitch %.1f, 45 deg flanks, depth %.1f, male major d%.2f / minor d%.2f; female crest d%.2f / root d%.2f (FwdTube v2)"
         % (THREAD['PITCH'], THREAD['T_DEPTH'], 2 * THREAD['BOSS_R_MAJOR'], 2 * THREAD['BOSS_R_MINOR'], 2 * THREAD['CAP_T_CREST_R'], 2 * THREAD['CAP_T_ROOT_R']))
    info("seat: the nose base annulus r %.2f..%.2f bears on the FwdTube mouth face -- hand tight, then a strip of tape across the joint" % (THREAD['BOSS_R_MAJOR'], R))
    rep.append("[NOTE] base ledge %.2f mm (r %.2f -> %.2f) prints as a short ring overhang tip-up, like v5's 1.65 mm one; it is the seat face"
               % (R - THREAD['BOSS_R_MAJOR'], THREAD['BOSS_R_MAJOR'], R))
    rep.append("[NOTE] mate/clash of the thread pair is checked in Models/PhoenixABS40-43_D9aft_v2.py (sampled, with a negative control)")
    rep.append("")
    mass = nose.Volume * RHO
    cg = nose.CenterOfMass.z
    rep.append("MASS (solid ABS, rho 1.05)")
    rep.append("  volume %10.1f mm3" % nose.Volume)
    rep.append("  mass   %10.1f g   (v5: 39.6 g)" % mass)
    rep.append("  CG     %10.1f mm from tip (station %.1f)" % (cg, cg - L_NOSE))
    rep.append("")
    rep.append("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))
    name = "PhoenixABS40-43_nose_VonKarmanScrew_%s" % REV
    os.makedirs(os.path.join(PRINTS, "Ready to Print"), exist_ok=True)
    nose.exportStep(os.path.join(MODELS, name + ".step"))
    MeshPart.meshFromShape(Shape=nose, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False).write(os.path.join(MODELS, name + ".stl"))
    MeshPart.meshFromShape(Shape=nose, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False).write(os.path.join(PRINTS, name + ".stl"))
    printed = nose.copy(); printed.rotate(V(0, 0, 0), V(1, 0, 0), 180); printed.translate(V(0, 0, Z_SH_END))   # tip up, shoulder on the bed
    MeshPart.meshFromShape(Shape=printed, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False).write(os.path.join(PRINTS, "Ready to Print", name + ".stl"))
    doc = App.newDocument("Nosecone_v6"); doc.addObject("Part::Feature", "NoseV6").Shape = nose; doc.recompute()
    doc.saveAs(os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_%s.FCStd" % REV))
    rep.append("")
    rep.append("FILES")
    rep.append("  Nosecone/Models/%s.step / .stl" % name)
    rep.append("  Print Files/Nosecone/%s.stl (as modeled) + Ready to Print/ (TIP UP, threaded shoulder on the bed, no support)" % name)
    rep.append("  Nosecone/PhoenixABS40-43_Nosecone_%s.FCStd" % REV)
    with open(os.path.join(NOSECONE, "nosecone_build_report_%s.txt" % REV), "w", encoding="utf-8") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep))

if not globals().get("NOSE_V6_LIB"):
    main()

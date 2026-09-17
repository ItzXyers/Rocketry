# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- independent verification of the aft retention STLs.

Plain Python + numpy. Deliberately does NOT use FreeCAD: OCCT booleans against
helically-swept solids are unreliable in this build (Shape.common() returns 0 on
solids that plainly overlap, and fill fractions come back as 147% or -24%), so the
build script's own boolean checks cannot be trusted for the threaded parts. This
reads the exported STLs -- the files that actually get printed -- and measures them
by ray casting.

Run:  python Models/verify_aft_retention.py
"""

import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
PRINTS = os.path.join(PROJECT, "Print Files")

# must match PhoenixABS40-43_aft_retention_v1.py
BOSS_R_MINOR, BOSS_R_MAJOR = 18.0, 19.2
CAP_T_CREST_R, CAP_T_ROOT_R = 18.2, 19.4
BOSS_Z_TIP, BOSS_Z_TOP = -13.5, -2.3
BOSS_TIP_CHAMFER = 1.2
CAP_Z_TIP, CAP_Z_TOP = -17.0, 0.0
CAP_FLOOR_Z = -14.5
MT_R_I, MT_R_O, MT_Z1 = 9.2, 10.4, 58.9
PITCH = 3.0
MOTOR_R, MOTOR_L, MOTOR_Z0 = 9.0, 70.0, -14.1
RAD_CLEAR = 0.2
# sealed aft section variant (cfg B). Plugged motor: no charge, so no vents.
BH_Z0, BH_Z1 = 55.9, 58.9     # bulkhead sits on the motor face; BH_Z1 is the part's top
BH_R = 19.85
R_AF_I, R_AF_O = 20.0, 21.5
SHOULDER_Z = 51.4             # OD steps 43 -> 39.7 here
TENON_R_O, TENON_R_I = 19.85, 18.5
CR_STATIONS, CR_T = (12.0, 40.0), 2.5
FIN_ANGLES = (0.0, 120.0, 240.0)
GAP_ANGLES = (60.0, 180.0, 300.0)
FIN_Z0, FIN_Z1 = 0.6, 51.4
FIN_SLOT_R_I = 10.7
FIN_T = 2.0
FIN_TIP_R = 76.5              # R_AF_O + 55 semi-span
FIN_TIP_Z_LE = 26.0           # FIN_Z1 - 25.4 sweep
FIN_TIP_CHORD = 25.0
FIN_FILLET = 4.0

fails = []


def check(name, ok, detail):
    print("  %-40s %-30s %s" % (name, detail, "PASS" if ok else "FAIL"))
    if not ok:
        fails.append(name)


def load_stl(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<I", fh.read(84)[80:84])[0]
        raw = np.frombuffer(fh.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return raw[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)


def open_edges(tris):
    """Boundary-edge count. A closed triangle mesh has every edge shared twice."""
    q = np.round(tris.reshape(-1, 3), 4)
    _, idx = np.unique(q, axis=0, return_inverse=True)
    f = idx.reshape(-1, 3)
    e = np.sort(np.stack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]], 1).reshape(-1, 2), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    return int((counts != 2).sum())


def inside(tris, pts, chunk=256):
    """Point-in-mesh by parity of +Z ray crossings."""
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    ax, ay, az = a[:, 0], a[:, 1], a[:, 2]
    e1 = b - a
    e2 = c - a
    # 2D cross products of the XY projection
    det = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    live = np.abs(det) > 1e-12          # drop triangles seen edge-on
    ax, ay, az = ax[live], ay[live], az[live]
    e1, e2, det = e1[live], e2[live], det[live]
    out = np.zeros(len(pts), dtype=bool)
    for s in range(0, len(pts), chunk):
        p = pts[s:s + chunk]
        px = p[:, 0][:, None] - ax[None, :]
        py = p[:, 1][:, None] - ay[None, :]
        u = (px * e2[None, :, 1] - py * e2[None, :, 0]) / det[None, :]
        v = (py * e1[None, :, 0] - px * e1[None, :, 1]) / det[None, :]
        inside_tri = (u >= 0) & (v >= 0) & (u + v <= 1)
        zhit = az[None, :] + u * e1[None, :, 2] + v * e2[None, :, 2]
        out[s:s + chunk] = (inside_tri & (zhit > p[:, 2][:, None])).sum(1) % 2 == 1
    return out


def cyl_points(r_vals, z_vals, n_theta):
    """Sample points on cylinders, jittered.

    Un-jittered samples sit on exactly the radii and angles the mesh vertices do, so
    a +Z ray can pass exactly through an edge or vertex and the crossing parity comes
    out wrong. That showed up as 98% where the answer had to be 100%. The offsets are
    irrational multiples so no sample lands on a facet boundary; they are far smaller
    than any clearance being measured.
    """
    rng = np.random.RandomState(12345)
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False) + 0.0007
    r, z, t = np.meshgrid(np.asarray(r_vals, float), np.asarray(z_vals, float),
                          th, indexing="ij")
    p = np.stack([r * np.cos(t), r * np.sin(t), z], -1).reshape(-1, 3)
    p += (rng.rand(*p.shape) - 0.5) * 2e-4
    return p


def helical(pts, deg):
    """Move points as the cap moves when unscrewed by `deg` of a RH thread."""
    a = np.radians(-deg)
    ca, sa = np.cos(a), np.sin(a)
    out = pts.copy()
    out[:, 0] = pts[:, 0] * ca - pts[:, 1] * sa
    out[:, 1] = pts[:, 0] * sa + pts[:, 1] * ca
    out[:, 2] = pts[:, 2] - PITCH * deg / 360.0
    return out


def main():
    print("=" * 84)
    print("Phoenix ABS 40-43 -- aft retention, independent STL verification")
    print("=" * 84)

    names = {"base": "PhoenixABS40-43_AftRetainerBase_v1.stl",
             "cap": "PhoenixABS40-43_MotorRetainerCap_v1.stl",
             "ring": "PhoenixABS40-43_FwdCenteringRing_v1.stl",
             "sect": "PhoenixABS40-43_AftSectionSealed_v1.stl",
             "fin": "PhoenixABS40-43_Fin_v1.stl",
             "can": "PhoenixABS40-43_AftFinCan_v1.stl"}
    tris = {}
    for k, fn in names.items():
        path = os.path.join(PRINTS, fn)
        if not os.path.exists(path):
            print("missing: " + path)
            return 1
        tris[k] = load_stl(path)

    print("\n[1] mesh integrity + envelope")
    for k in ("base", "cap", "ring", "sect", "fin", "can"):
        t = tris[k]
        p = t.reshape(-1, 3)
        oe = open_edges(t)
        r = np.hypot(p[:, 0], p[:, 1])
        check("%s watertight" % k, oe == 0,
              "%d facets, %d open edges" % (len(t), oe))
        print("  %-40s dia %.1f, Z %.1f..%.1f" %
              ("", 2 * r.max(), p[:, 2].min(), p[:, 2].max()))

    print("\n[2] threads exist and are cut, not solid")
    # a threaded annulus is part material, part groove -- 100% means the thread was
    # never cut, 0% means it is missing entirely
    zb = np.linspace(BOSS_Z_TIP + BOSS_TIP_CHAMFER + 0.3, BOSS_Z_TOP - 0.3, 22)
    pb = cyl_points([18.3, 18.7, 19.1], zb, 72)
    fb = inside(tris["base"], pb).mean()
    check("boss thread fill fraction", 0.30 < fb < 0.75, "%.0f%% material" % (fb * 100))

    zc = np.linspace(CAP_FLOOR_Z + 0.5, BOSS_Z_TOP - 0.5, 22)
    pc = cyl_points([18.4, 18.8, 19.2], zc, 72)
    fc = inside(tris["cap"], pc).mean()
    check("cap thread fill fraction", 0.20 < fc < 0.70, "%.0f%% material" % (fc * 100))

    print("\n[3] the cap actually screws on (no interference along the helix)")
    # Sample points that are inside the cap, then ask whether they are also inside
    # the base -- at the seated position and at a series of positions backed off
    # along the thread helix.
    zs = np.linspace(CAP_FLOOR_Z + 0.4, BOSS_Z_TOP - 0.4, 26)
    probe = cyl_points([18.3, 18.6, 18.9, 19.2, 19.5], zs, 96)
    in_cap = probe[inside(tris["cap"], probe)]
    print("  %d probe points inside the cap's thread material" % len(in_cap))
    worst, worst_a = 0.0, None
    for deg in [0, 15, 30, 45, 60, 90, 120, 180, 270, 360, 540, 720]:
        frac = inside(tris["base"], helical(in_cap, deg)).mean() if len(in_cap) else 0.0
        if frac > worst:
            worst, worst_a = frac, deg
        if deg in (0, 30, 90, 180, 360):
            print("      backed off %4d deg : %.3f%% of cap points inside the base"
                  % (deg, frac * 100))
    check("cap/base clash over 0-720 deg", worst < 0.005,
          "worst %.3f%% at %s deg" % (worst * 100, worst_a))
    bad = in_cap[inside(tris["base"], in_cap)]
    if len(bad):
        rb = np.hypot(bad[:, 0], bad[:, 1])
        print("      %d clashing points at seated: r %.2f..%.2f, z %.2f..%.2f"
              % (len(bad), rb.min(), rb.max(), bad[:, 2].min(), bad[:, 2].max()))
        print("      (boss material ends at r %.1f; a clash only above that is real)"
              % BOSS_R_MAJOR)

    print("\n[4] motor fits and is retained")
    # the motor bay must be clear...
    zs = np.linspace(MOTOR_Z0 + 0.5, MOTOR_Z0 + MOTOR_L - 0.5, 60)
    bay = cyl_points([0.0, 4.0, 8.0, 8.9], zs, 24)
    hit = inside(tris["base"], bay).mean()
    check("motor bay clear (18 mm x 70)", hit < 0.001, "%.3f%% obstructed" % (hit * 100))
    # ...and the cap must block it at the retaining lip
    lip = cyl_points([7.8, 8.4, 8.9], [CAP_FLOOR_Z - 0.5], 48)
    blocked = inside(tris["cap"], lip).mean()
    check("cap lip blocks the casing rim", blocked > 0.99,
          "%.0f%% of the rim ring is backed by the lip" % (blocked * 100))
    # ...and the exhaust bore must be open
    bore = cyl_points([0.0, 3.0, 6.0, 7.2], [CAP_FLOOR_Z - 0.5], 24)
    openb = inside(tris["cap"], bore).mean()
    check("exhaust bore open", openb < 0.001, "%.0f%% obstructed" % (openb * 100))

    print("\n[5] engine block stops the motor")
    fwd = cyl_points([7.6, 8.6], [55.9 + 1.9], 48)
    stop = inside(tris["base"], fwd).mean()
    check("engine block shoulder present", stop > 0.99,
          "%.0f%% of the shoulder ring is material" % (stop * 100))

    print("")
    print("[6] sealed aft section variant (cfg B)")
    sect = tris["sect"]

    def at(angles, r, z):
        pts = np.array([[r * np.cos(np.radians(a)) + 3e-5,
                         r * np.sin(np.radians(a)) + 3e-5, z + 3e-5] for a in angles])
        return inside(sect, pts).mean()

    def frac(rs, zs, n=48):
        return inside(sect, cyl_points(rs, zs, n)).mean()

    f = frac([0.0, 3.0, 7.0, 11.0, 15.0, 19.0], [(BH_Z0 + BH_Z1) / 2.0])
    check("bulkhead is SEALED across the bore", f > 0.999, "%.1f%% solid" % (f * 100))
    f = frac([0.0, 3.0, 6.0, 8.5], [BH_Z0 + 0.6])
    check("bulkhead backs the motor's whole face", f > 0.999,
          "%.0f%% material across r 0-8.5" % (f * 100))

    # the bulkhead face is the forward-most plane -- nothing on the part reaches past it
    ztop = sect.reshape(-1, 3)[:, 2].max()
    check("bulkhead face is the part's fwd end", abs(ztop - BH_Z1) < 0.02,
          "part top Z %.2f vs bulkhead %.2f" % (ztop, BH_Z1))

    # through-the-wall fin slots
    f = at(FIN_ANGLES, R_AF_I + 0.75, 25.0)
    check("fin slots open through the wall", f < 0.001, "%.0f%% blocked" % (f * 100))
    f = at(GAP_ANGLES, R_AF_I + 0.75, 25.0)
    check("wall intact between fin slots", f > 0.999, "%.0f%% material" % (f * 100))
    f = max(at(FIN_ANGLES, 11.0, z) for z in (10.0, 25.0, 45.0))
    check("fin slot runs in to the motor tube", f < 0.001,
          "%.0f%% blocked at r 11.0" % (f * 100))
    f = max(at(FIN_ANGLES, 15.0, z + CR_T / 2.0) for z in CR_STATIONS)
    check("centering rings are slotted too", f < 0.001, "%.0f%% blocked" % (f * 100))
    f = at(FIN_ANGLES, R_AF_I + 0.75, FIN_Z1 - 2.0)
    check("slots reach the top of the fin root", f < 0.001, "%.0f%% blocked" % (f * 100))

    # the lip, and the shoulder the forward tube lands on
    f = frac([(TENON_R_I + TENON_R_O) / 2.0], [SHOULDER_Z + 2.0, BH_Z0 - 1.0])
    check("lip wall present", f > 0.999, "%.0f%% material" % (f * 100))
    f = frac([R_AF_O - 0.4], [SHOULDER_Z + 2.0, BH_Z0 - 1.0])
    check("lip undercut so fwd tube clears", f < 0.001,
          "%.0f%% material at r %.1f" % (f * 100, R_AF_O - 0.4))
    f = at(GAP_ANGLES, R_AF_I + 0.75, SHOULDER_Z - 1.5)
    check("full-OD wall below the shoulder", f > 0.999, "%.0f%% material" % (f * 100))

    f = at(GAP_ANGLES, 15.0, CR_STATIONS[0] + CR_T / 2.0)
    check("centering rings tie tube to wall", f > 0.999, "%.0f%% material" % (f * 100))
    f = at(GAP_ANGLES, 15.0, 26.0)
    check("annulus open between rings", f < 0.001, "%.0f%% obstructed" % (f * 100))

    zs2 = np.linspace(MOTOR_Z0 + 0.5, MOTOR_Z0 + MOTOR_L - 0.5, 60)
    f = inside(sect, cyl_points([0.0, 4.0, 8.0, 8.9], zs2, 24)).mean()
    check("motor bay clear in sealed section", f < 0.001, "%.3f%% obstructed" % (f * 100))

    print("")
    print("[7] fins and the one-piece fin can")
    fin, can = tris["fin"], tris["can"]

    def inside_at(mesh, angles, r, z):
        pts = np.array([[r * np.cos(np.radians(a)) + 3e-5,
                         r * np.sin(np.radians(a)) + 3e-5, z + 3e-5] for a in angles])
        return inside(mesh, pts).mean()

    # --- the standalone fin, for the slotted section ---
    zc = (FIN_Z0 + FIN_Z1) / 2.0
    YP = 0.35          # inside the 2 mm plate, clear of the loft section plane at y=0
    f = inside(fin, np.array([[r, YP, zc] for r in (12.0, 19.0, 30.0, 50.0, 70.0)])).mean()
    check("fin spans tab root to near tip", f > 0.999, "%.0f%% material through the plate" % (f * 100))
    f = inside(fin, np.array([[40.0, y, zc] for y in (-1.4, 1.4)])).mean()
    check("fin is 2 mm thick", f < 0.001, "%.0f%% material 0.4 mm outside the faces" % (f * 100))
    f = inside(fin, np.array([[FIN_TIP_R + 0.5, YP, zc]])).mean()
    check("fin stops at the 55 mm semi-span", f < 0.001,
          "%.0f%% material beyond r %.1f" % (f * 100, FIN_TIP_R))
    # the sweep: at the tip station the fin must exist between LE and TE only
    f = inside(fin, np.array([[FIN_TIP_R - 2.5, YP, FIN_TIP_Z_LE - FIN_TIP_CHORD / 2.0]])).mean()
    g = inside(fin, np.array([[FIN_TIP_R - 2.5, YP, FIN_TIP_Z_LE + 4.0]])).mean()
    check("LE sweep is cut in at the tip", f > 0.999 and g < 0.001,
          "tip chord solid, %0.0f%% above the tip LE" % (g * 100))
    # tab must fit the slot it was drawn for
    f = inside(fin, np.array([[FIN_SLOT_R_I + 0.4, YP, zc]])).mean()
    check("fin tab reaches the slot root", f > 0.999, "%.0f%% material at r %.1f"
          % (f * 100, FIN_SLOT_R_I + 0.4))

    # --- the one-piece fin can ---
    f = inside_at(can, FIN_ANGLES, 45.0, zc)
    check("fin can has all 3 fins", f > 0.999, "%.0f%% material at r 45" % (f * 100))
    f = inside_at(can, GAP_ANGLES, 45.0, zc)
    check("nothing between the fins", f < 0.001, "%.0f%% material at r 45" % (f * 100))
    f = inside_at(can, FIN_ANGLES, R_AF_I + 0.75, 25.0)
    check("fin can wall is NOT slotted", f > 0.999,
          "%.0f%% material where the slots would be" % (f * 100))

    # root fillet: material must sit off the fin face, against the wall, where a plain
    # fin/wall joint would be empty
    fr = []
    for a in FIN_ANGLES:
        for sgn in (1.0, -1.0):
            th, off = np.radians(a), sgn * 1.4
            x = (R_AF_O + 0.4) * np.cos(th) - off * np.sin(th)
            y = (R_AF_O + 0.4) * np.sin(th) + off * np.cos(th)
            fr.append([x, y, zc])
    f = inside(can, np.array(fr)).mean()
    check("root fillets present both sides", f > 0.999,
          "%.0f%% material 1.0 mm off the fin face" % (f * 100))
    f = inside(can, np.array([[(R_AF_O + FIN_FILLET + 1.5) * np.cos(np.radians(a)) - 3.0 * np.sin(np.radians(a)),
                               (R_AF_O + FIN_FILLET + 1.5) * np.sin(np.radians(a)) + 3.0 * np.cos(np.radians(a)),
                               zc] for a in FIN_ANGLES])).mean()
    check("fillet does not run on forever", f < 0.001,
          "%.0f%% material past the fillet radius" % (f * 100))

    # the fin can must still be the sealed section underneath
    f = inside(can, cyl_points([0.0, 3.0, 7.0, 11.0, 15.0, 19.0],
                               [(BH_Z0 + BH_Z1) / 2.0], 48)).mean()
    check("fin can bulkhead still sealed", f > 0.999, "%.1f%% solid" % (f * 100))
    zs3 = np.linspace(MOTOR_Z0 + 0.5, MOTOR_Z0 + MOTOR_L - 0.5, 60)
    f = inside(can, cyl_points([0.0, 4.0, 8.0, 8.9], zs3, 24)).mean()
    check("fin can motor bay clear", f < 0.001, "%.3f%% obstructed" % (f * 100))
    ztop = can.reshape(-1, 3)[:, 2].max()
    check("fin can ends at the bulkhead face", abs(ztop - BH_Z1) < 0.02,
          "part top Z %.2f vs bulkhead %.2f" % (ztop, BH_Z1))

    print("\n" + "=" * 84)
    if fails:
        print("FAILED: " + ", ".join(fails))
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

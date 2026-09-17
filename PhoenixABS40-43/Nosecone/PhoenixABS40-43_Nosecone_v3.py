# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- oval-door nosecone, radial servo, snap-in shock cord, v3

SOURCE OF TRUTH. Every dimension is a named constant below; edit here and
re-run, never edit the STL/STEP/FCStd by hand. Supersedes
PhoenixABS40-43_Nosecone_v2.py (kept for history, not deleted).

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

v3 feedback driving this revision (2026-09-15, same-session as v2):
  1. "servo to point out of the radial body" -- v2's servo pad already had its
     OUTPUT SHAFT radial (local_placement maps local Z to radial-outward), but
     only modeled a 1.5mm pad, not the real SG90 case. v3 sizes the mount to
     the real, measured servo (Avionics/avionics_bay_packing_40mm.md: body
     23 x 12.4 x 22.7mm, 32.2mm tab-to-tab, 9g) and models it as a real
     THROUGH-WALL mount: the tab flange sits at the outer surface, the shaft
     end (short, ~5mm) is proud outside where the latch lives, and the bulk
     of the case (~17.7mm) hangs inboard in the already-open bay cavity --
     NOT a 22.7mm external blister. See SERVO section below for the assumed
     flange-near-shaft split (flagged, bench-verify).
  2. "latch (or plastic arm...) to hold the nosecone in place" -- unchanged
     principle from v2 (peg/backstop/gate, load on the backstop not the
     servo), repositioned for the new oval boundary.
  3. "thread the shock chord through the door itself and click it in place" --
     the M4 bulkhead eyebolt (Spine, unsplit) STAYS as the primary snatch-load
     anchor -- moving that load path onto a printed snap clip on a hinged
     door would put flight load through an un-proven cantilever feature.
     Added instead: printed snap-in cord CHANNELS on the door's inner face,
     so the cord is routed/dressed through the door as asked, without being
     the load path. See SHOCK CORD CLIPS section.
  4. "larger part of the nose ... more than middle ... oval cut instead" --
     a hinged door CANNOT exceed 180 deg of arc (a door subtending >180 deg
     contains two diametrically-opposite points, so its own width, 2R, would
     exceed its mouth's chord for every opening angle -- it is geometrically
     captured, not just hard to hinge). 180 deg is therefore a hard ceiling.
     The constructive reading: MORE OF THE NOSE'S LENGTH becomes door than a
     small window would (v1 was a small window; this reaches from deep in
     the ogive to just short of the bulkhead), and the cut is a true oval
     (an ellipse in the unrolled theta-Z pattern) instead of a straight
     lengthwise seam, tapering to a point at both ends -- both wider (85 deg
     half-width, 170 deg total, vs a small window) AND longer than v1, while
     staying under the 180 deg ceiling. The ellipse shape has a side benefit:
     it self-narrows exactly where the ogive gets thin, so the widest cut
     (170 deg) lands where the tube is fattest (the ogive/barrel junction),
     not near the pointy tip.
  5. "no ejection charge ... entire thing hinges on the parachute exiting and
     being picked up by wind when the nosecone is detached" -- unchanged
     from v2 (this was already a hinge-only, charge-free architecture); read
     "detached" here as "the door swings open," not full separation from the
     airframe -- the user separately called the hinge-and-fairing-cut look
     "good," so the door stays captured on the Spine via hinge, it does not
     jettison.

Everything NOT called out above (outer profile, cavity, bulkhead, shoulder,
retention screws) is unchanged from v2 -- see NOSECONE_DESIGN.md for the full
rationale of those choices.
"""

import os
import math

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector, Placement, Matrix

# ---------------------------------------------------------------- parameters

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
NOSECONE = os.path.join(PROJECT, "Nosecone")
MODELS = os.path.join(NOSECONE, "Models")
PRINTS = os.path.join(PROJECT, "Print Files", "Nosecone")
REV = "v3"

RHO_ABS = 1.05e-3   # g/mm^3, 100% infill reference

# --- airframe (DESIGN.md Sec2/Sec8) ---
R_AF_O = 21.5        # airframe OD 43.0 / 2
R_AF_I = 20.0        # airframe ID 40.0 / 2

# --- outer profile stations (Z from nose tip, +Z toward the airframe) --
# UNCHANGED from v2.
R = 21.5
L_OGV = 100.0
WALL_OGV = 2.0
WALL_BAY = 3.5

Z_BAY0, Z_BAY1 = L_OGV, 190.0
Z_SH_TAPER0, Z_SH_TAPER1 = 190.0, 193.0
R_SH = 19.85
Z_SH0, Z_SH1 = 193.0, 237.0

R_BAY_IN = R - WALL_BAY
Z_BULK0, Z_BULK1 = 182.0, Z_SH_TAPER0

OGV_RHO = (R * R + L_OGV * L_OGV) / (2.0 * R)


def ogive_arc_params(wall):
    radius = OGV_RHO - wall
    center_r = R - OGV_RHO
    dz = math.sqrt(max(radius * radius - center_r * center_r, 0.0))
    tip_z = L_OGV - dz
    return radius, center_r, tip_z


def ogive_arc_r(z, wall):
    radius, center_r, tip_z = ogive_arc_params(wall)
    dz = L_OGV - z
    val = radius * radius - dz * dz
    if val < 0.0:
        val = 0.0
    return math.sqrt(val) + center_r


def ogive_arc_edge(wall):
    radius, center_r, tip_z = ogive_arc_params(wall)
    p_tip = Vector(0.0, 0.0, tip_z)
    z_mid = (tip_z + L_OGV) / 2.0
    p_mid = Vector(ogive_arc_r(z_mid, wall), 0.0, z_mid)
    p_base = Vector(R - wall, 0.0, L_OGV)
    return Part.Arc(p_tip, p_mid, p_base).toShape()


def true_outer_r(z):
    if z <= L_OGV:
        return ogive_arc_r(z, 0.0)
    elif z <= Z_BAY1:
        return R
    elif z <= Z_SH_TAPER1:
        frac = (z - Z_SH_TAPER0) / (Z_SH_TAPER1 - Z_SH_TAPER0)
        return R + (R_SH - R) * frac
    else:
        return R_SH


def true_inner_r(z):
    """Cavity radius at Z -- ogive uses the true concentric-arc offset, the
    bay is the constant R_BAY_IN. Only used forward of the bulkhead, where
    the cavity actually exists."""
    if z <= L_OGV:
        return ogive_arc_r(z, WALL_OGV)
    return R_BAY_IN


# --- oval door boundary (replaces v2's constant-theta fairing split) ---
# An ellipse in the unrolled (theta, Z) pattern: half-width DOOR_HALFW_MAX at
# Z=OVAL_ZC, tapering to a point at OVAL_Z0/OVAL_Z1. Centred opposite theta=0
# (DOOR_THETA_C=180) so the whole door lives in a contiguous theta range with
# no 0/360 wraparound to special-case.
#
# 180 deg total width is a hard ceiling for a HINGED door (see docstring
# item 4) -- DOOR_HALFW_MAX=85 gives 170 deg at the widest point, as close to
# that ceiling as GAP_DEG leaves room for. OVAL_Z0=35 deliberately leaves the
# first 35mm of the ogive (the genuinely pointy part) as solid, unsplit
# Spine -- structural, and the ellipse's own taper means the cut would have
# been near-zero width there anyway. OVAL_Z1=178 stops 4mm short of the
# bulkhead (Z_BULK0=182) so the bulkhead+shoulder stay a complete, unsplit
# ring -- no aft-rim capture feature is needed (v2's LIP_Z system is
# removed entirely; this is a real simplification, not just a style choice).
DOOR_THETA_C = 180.0
OVAL_Z0, OVAL_Z1 = 35.0, 178.0
OVAL_ZC = (OVAL_Z0 + OVAL_Z1) / 2.0     # 106.5 -- just aft of the ogive/barrel seam
OVAL_ZH = (OVAL_Z1 - OVAL_Z0) / 2.0     # 71.5
DOOR_HALFW_MAX = 85.0                    # deg, peak half-width (170 deg total)
GAP_DEG = 1.0                            # angular clearance between the two halves
DZ_SPLIT = 1.5                           # Z step for the staircase boundary approximation


def door_halfwidth(z):
    """Ellipse half-width in degrees at station z; 0 outside [OVAL_Z0, OVAL_Z1]."""
    if z <= OVAL_Z0 or z >= OVAL_Z1:
        return 0.0
    t = (z - OVAL_ZC) / OVAL_ZH
    t = max(-1.0, min(1.0, t))
    return DOOR_HALFW_MAX * math.sqrt(max(1.0 - t * t, 0.0))


# --- flexure hinge points, clustered at the oval's widest (flattest) Z,
# where the boundary is closest to axis-parallel -- see docstring item 4.
# All 3 stations sit in or right at the edge of the constant-radius barrel
# (>=96.5, true_outer_r there is within 0.03mm of R=21.5), so hinge/latch
# features below may safely use the constant R like v2 did.
HINGE_Z_LIST = [96.5, 106.5, 116.5]
HINGE_HALF_LEN = 6.0
HINGE_ANG_WIDTH = 11.0
HINGE_DEPTH = 0.6
HINGE_HOLE_D = 2.2

# --- latch: single servo-driven point on the oval's EAST (free/latch) edge,
# same Z neighbourhood as the hinge cluster (mirrors v2's approach of putting
# hinge and latch at the same general station, opposite sides).
Z_LATCH = 106.5
_W_LATCH = door_halfwidth(Z_LATCH)                    # 85.0 deg
PEG_THETA = DOOR_THETA_C + _W_LATCH - 5.0              # on DoorHalf, a few deg in from its edge
PEG_D = 3.0
PEG_LEN = 4.5
BACKSTOP_THETA = DOOR_THETA_C + _W_LATCH + 8.0         # on Spine, a few deg beyond the door edge
BACKSTOP_W, BACKSTOP_L, BACKSTOP_H = 5.0, 5.0, 3.0
SERVO_THETA = BACKSTOP_THETA + 20.0                    # on Spine, further round for the servo body
PADDLE_THETA = DOOR_THETA_C + _W_LATCH + 3.5           # LatchArm gate centre, between peg and backstop
PADDLE_TAN, PADDLE_AX = 10.0, 6.0
PADDLE_R = R + PEG_LEN - 1.0

HUB_D = 8.0
HUB_H = 2.0
HUB_PILOT_D = 1.2

# --- SERVO: real SG90 envelope (Avionics/avionics_bay_packing_40mm.md /
# DESIGN.md Sec7.5.2 keepout, both agree: 23 x 12.4 x 22.7mm body, 32.2mm
# tab-to-tab, 9g, >=1.5 kg-cm). Mounted THROUGH the wall, tab flange at the
# outer surface: the case is asymmetric about the flange (shaft-side is
# short, base-side is long), so orienting shaft-out puts only the short
# side outside (a small nub, not a 22.7mm blister) and the long side inboard
# in the already-open bay cavity, floating free past the wall (secured only
# at the tab flange, which is normal for this class of servo mount).
# ASSUMPTION (flag, bench-verify against the actual unit before printing):
# flange sits SERVO_OUT_PROUD from the shaft/top end of the case, so only
# that much protrudes outside; the rest (SERVO_BODY_H - SERVO_OUT_PROUD)
# hangs inboard. If the real unit's flange is centred instead, split the
# difference and re-run.
SERVO_BODY_L = 23.0      # case length (no tabs) -- mounted axially
SERVO_BODY_W = 12.4      # case width -- mounted tangentially
SERVO_BODY_H = 22.7      # case height -- mounted radially (the dimension the shaft is normal to)
SERVO_TAB_SPAN = 32.2    # tab-to-tab, axial
SERVO_OUT_PROUD = 5.0    # case + shaft boss proud of the OD (shaft/top side)
SERVO_IN_DEPTH = SERVO_BODY_H - SERVO_OUT_PROUD   # 17.7mm hanging in the bay cavity
SERVO_CLR = 0.4          # per-side clearance around the case for the through-wall port
PAD_TAN = SERVO_BODY_W + 3.0     # 15.4, flange footprint
PAD_AX = SERVO_TAB_SPAN + 2.0    # 34.2, flange footprint (matches v2's generic guess almost exactly)
PAD_HOLE_D = 2.2
PAD_HOLE_AX = 14.0       # tab hole spacing -- generic, bench-verify vs actual unit (unchanged caveat from v2)

# --- bulkhead / shock-cord PRIMARY anchor (Spine only -- unsplit, on-axis).
# Unchanged from v2 -- this is what actually carries the parachute snatch
# load; see docstring item 3 for why it stays here instead of moving onto
# the door's snap clips.
EYEBOLT_HOLE_D = 4.5
EYEBOLT_CB_D = 10.0
EYEBOLT_CB_DEPTH = 2.0

# --- shock cord SNAP CLIPS on the door -- routing/dressing only, not a load
# path (see docstring item 3). Sized for ~6mm tubular nylon cord (typical for
# this airframe class); flag and re-size if the actual cord differs.
CORD_D = 6.0
CLIP_CLR = 0.4                 # radial clearance around the cord in the channel
CLIP_Z_LIST = [65.0, 150.0]    # spread along the door, clear of the hinge/latch cluster
CLIP_THETA = DOOR_THETA_C      # door's angular centre -- most clearance from both seams
CLIP_LEN = 8.0                 # axial length of each clip boss
CLIP_REACH = CORD_D + 2.0 * CLIP_CLR + 2.0   # radial depth of the boss, channel + wall
CLIP_W = 12.0                  # tangential width of the clip boss
CLIP_MOUTH_FRAC = 0.6          # open-mouth slot width as a fraction of the channel dia -- <1 so the cord must flex the boss to snap in

# --- shoulder positive retention -- unchanged from v2 ---
N_RET_SCREWS = 3
Z_RET_SCREW = (Z_SH0 + Z_SH1) / 2.0
RET_SCREW_D = 3.4

OVERLAP = 0.5

# =================================================================== helpers


def local_placement(theta_deg, z, r):
    """Local frame at (theta,z) on radius r: local X=tangential, Y=axial(+Z), Z=radial-outward."""
    th = math.radians(theta_deg)
    origin = Vector(r * math.cos(th), r * math.sin(th), z)
    lx = Vector(-math.sin(th), math.cos(th), 0.0)
    ly = Vector(0.0, 0.0, 1.0)
    lz = Vector(math.cos(th), math.sin(th), 0.0)
    m = Matrix(lx.x, ly.x, lz.x, origin.x,
               lx.y, ly.y, lz.y, origin.y,
               lx.z, ly.z, lz.z, origin.z,
               0, 0, 0, 1)
    return Placement(m)


def local_box(theta_deg, z, r, wx, wy, wz, outward=True):
    z0 = 0.0 if outward else -wz
    b = Part.makeBox(wx, wy, wz, Vector(-wx / 2.0, -wy / 2.0, z0))
    b.Placement = local_placement(theta_deg, z, r)
    return b


def local_cyl_through(theta_deg, z, r, dia, length):
    c = Part.makeCylinder(dia / 2.0, length, Vector(0, 0, -length / 2.0))
    c.Placement = local_placement(theta_deg, z, r)
    return c


def local_cyl_proud(theta_deg, z, r, dia, length):
    c = Part.makeCylinder(dia / 2.0, length, Vector(0, 0, 0))
    c.Placement = local_placement(theta_deg, z, r)
    return c


def local_cyl_axial(theta_deg, z, r, dia, length):
    """Cylinder whose axis is local Y (tube-axial) -- for the shock-cord channel."""
    c = Part.makeCylinder(dia / 2.0, length, Vector(0, -length / 2.0, 0), Vector(0, 1, 0))
    c.Placement = local_placement(theta_deg, z, r)
    return c


def frame_point(theta_deg, z, r):
    th = math.radians(theta_deg)
    return Vector(r * math.cos(th), r * math.sin(th), z)


def wedge(r_in, r_out, z0, z1, theta0_deg, theta1_deg):
    """Angular wedge solid, theta measured from +X, spanning [theta0,theta1] deg, z in [z0,z1]."""
    h = z1 - z0
    ang = theta1_deg - theta0_deg
    outer = Part.makeCylinder(r_out, h, Vector(0, 0, z0), Vector(0, 0, 1), ang)
    if r_in > 0.01:
        inner = Part.makeCylinder(r_in, h, Vector(0, 0, z0), Vector(0, 0, 1), ang)
        w = outer.cut(inner)
    else:
        w = outer
    w.rotate(Vector(0, 0, 0), Vector(0, 0, 1), theta0_deg)
    return w


def oriented_box(center, y_dir, ref_up, length_y, width_x, height_z):
    y = Vector(y_dir)
    y.normalize()
    up = Vector(ref_up)
    z = up - y * up.dot(y)
    if z.Length < 1e-6:
        z = Vector(0, 0, 1) - y * y.z
    z.normalize()
    x = y.cross(z)
    x.normalize()
    z = x.cross(y)
    z.normalize()
    m = Matrix(x.x, y.x, z.x, center.x,
               x.y, y.y, z.y, center.y,
               x.z, y.z, z.z, center.z,
               0, 0, 0, 1)
    b = Part.makeBox(width_x, length_y, height_z, Vector(-width_x / 2.0, -length_y / 2.0, -height_z / 2.0))
    b.Placement = Placement(m)
    return b


def check(shape, label):
    ok = shape.isValid()
    print("  [%s] valid=%s solids=%d volume=%.1f mm^3 bbox=%s"
          % (label, ok, len(shape.Solids), shape.Volume, shape.BoundBox))
    if not ok:
        raise RuntimeError("INVALID SHAPE at step: %s" % label)
    return shape


# ====================================================================== BUILD

print("=== Phoenix ABS 40-43 Nosecone %s (oval door, radial servo) ===" % REV)
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRINTS, exist_ok=True)

doc = App.newDocument("PhoenixABS40-43_Nosecone_v3")

# --- 1. outer blank: true-arc ogive + barrel + taper + shoulder (unchanged) ---
print("[1] outer blank (smooth arc ogive)")
arc_outer = ogive_arc_edge(0.0)
p_base = Vector(R, 0.0, L_OGV)
pts_outer = [p_base, Vector(R, 0, Z_BAY1), Vector(R_SH, 0, Z_SH_TAPER1), Vector(R_SH, 0, Z_SH1), Vector(0, 0, Z_SH1)]
line_edges = []
prev = pts_outer[0]
for p in pts_outer[1:]:
    line_edges.append(Part.makeLine(prev, p))
    prev = p
close_edge = Part.makeLine(Vector(0, 0, Z_SH1), Vector(0, 0, 0.0))
wire_outer = Part.Wire([arc_outer] + line_edges + [close_edge])
face_outer = Part.Face(wire_outer)
outer_solid = face_outer.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)
check(outer_solid, "outer_solid")

# --- 2. cavity (unchanged) ---
print("[2] cavity (smooth arc)")
arc_inner = ogive_arc_edge(WALL_OGV)
_, _, tip_z_inner = ogive_arc_params(WALL_OGV)
pts_inner = [Vector(R - WALL_OGV, 0, L_OGV), Vector(R_BAY_IN, 0, Z_BAY0), Vector(R_BAY_IN, 0, Z_BULK0), Vector(0, 0, Z_BULK0)]
line_edges_i = []
prev = pts_inner[0]
for p in pts_inner[1:]:
    line_edges_i.append(Part.makeLine(prev, p))
    prev = p
close_edge_i = Part.makeLine(Vector(0, 0, Z_BULK0), Vector(0, 0, tip_z_inner))
wire_inner = Part.Wire([arc_inner] + line_edges_i + [close_edge_i])
face_inner = Part.Face(wire_inner)
inner_solid = face_inner.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)
check(inner_solid, "inner_solid")

full_shell = outer_solid.cut(inner_solid)
check(full_shell, "full_shell (hollowed, unsplit)")

# --- 3. bulkhead eyebolt hole + counterbores (unchanged, must precede split) ---
print("[3] eyebolt hole")
eyebolt = Part.makeCylinder(EYEBOLT_HOLE_D / 2.0, Z_BULK1 - Z_BULK0 + 2.0, Vector(0, 0, Z_BULK0 - 1.0))
cb_fwd = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK0 - 0.25))
cb_aft = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK1 - EYEBOLT_CB_DEPTH + 0.25))
full_shell = full_shell.cut(eyebolt).cut(cb_fwd).cut(cb_aft)
check(full_shell, "full_shell (eyebolt)")

# --- 4. shoulder retention screws x3 (unchanged) ---
print("[4] shoulder retention screws x%d" % N_RET_SCREWS)
for i in range(N_RET_SCREWS):
    th = 360.0 * i / N_RET_SCREWS
    hole = local_cyl_through(th, Z_RET_SCREW, R_SH, RET_SCREW_D, 20.0)
    full_shell = full_shell.cut(hole)
check(full_shell, "full_shell (retention screws)")

# --- 5. oval split into Spine (fixed) + DoorHalf (hinged petal) ---
# Staircase approximation of the ellipse boundary: at each DZ_SPLIT-tall Z
# slice, cut a constant-angle wedge sized to the boundary at that slice's
# midpoint. Built as compounds (one cut each) rather than one cut per slice.
print("[5] oval fairing split (staircase, dz=%.1f)" % DZ_SPLIT)
door_cut_wedges = []       # removed from full_shell -> Spine (door's own footprint)
spine_cut_wedges = []      # removed from full_shell -> DoorHalf (everything outside the door)
z = OVAL_Z0
while z < OVAL_Z1 - 1e-6:
    z1 = min(z + DZ_SPLIT, OVAL_Z1)
    zm = (z + z1) / 2.0
    w = door_halfwidth(zm)
    if w > GAP_DEG * 0.5:
        door_cut_wedges.append(wedge(0.0, R + 5.0, z, z1, DOOR_THETA_C - w, DOOR_THETA_C + w))
        w_d = max(w - GAP_DEG, 0.0)
        if w_d > 0.01:
            spine_cut_wedges.append(wedge(0.0, R + 5.0, z, z1,
                                           DOOR_THETA_C + w_d, DOOR_THETA_C - w_d + 360.0))
    z = z1

spine = full_shell.cut(Part.makeCompound(door_cut_wedges))
check(spine, "spine (before hinge/latch/servo features)")

door = full_shell.cut(Part.makeCompound(spine_cut_wedges))
door = door.cut(wedge(0.0, R + 5.0, 0.0, OVAL_Z0, 0.0, 360.0))
door = door.cut(wedge(0.0, R + 5.0, OVAL_Z1, Z_SH1 + 2.0, 0.0, 360.0))
check(door, "door (before hinge/latch features)")

# --- 6. flexure hinge points, clustered at the oval's widest Z (see param
# block) -- theta evaluated per-point from the ellipse, not a single constant
# like v2, since the boundary now genuinely curves (though only ~1.3 deg
# across the whole cluster, since it's centred right at the flat peak).
print("[6] hinge points x%d" % len(HINGE_Z_LIST))
for hz in HINGE_Z_LIST:
    w_h = door_halfwidth(hz)
    theta_hinge = DOOR_THETA_C - w_h    # west boundary of the oval at this Z

    pocket_a = wedge(R - HINGE_DEPTH, R + 0.5, hz - HINGE_HALF_LEN, hz + HINGE_HALF_LEN,
                      theta_hinge - HINGE_ANG_WIDTH, theta_hinge)
    spine = spine.cut(pocket_a)
    theta_hole_a = theta_hinge - HINGE_ANG_WIDTH * 0.5
    for dz in (-3.0, 3.0):
        h = local_cyl_through(theta_hole_a, hz + dz, R, HINGE_HOLE_D, 20.0)
        spine = spine.cut(h)

    pocket_b = wedge(R - HINGE_DEPTH, R + 0.5, hz - HINGE_HALF_LEN, hz + HINGE_HALF_LEN,
                      theta_hinge, theta_hinge + HINGE_ANG_WIDTH)
    door = door.cut(pocket_b)
    theta_hole_b = theta_hinge + HINGE_ANG_WIDTH * 0.5
    for dz in (-3.0, 3.0):
        h = local_cyl_through(theta_hole_b, hz + dz, R, HINGE_HOLE_D, 20.0)
        door = door.cut(h)
check(spine, "spine (hinge pockets)")
check(door, "door (hinge pockets)")

# --- 7. latch: peg on DoorHalf; backstop on Spine (load path -- same
# geometry-holds-the-load principle as v2) ---
print("[7] latch (peg/backstop)")
peg = local_cyl_proud(PEG_THETA, Z_LATCH, R - OVERLAP, PEG_D, PEG_LEN + OVERLAP)
door = door.fuse(peg)
door = door.removeSplitter()
check(door, "door (+peg, final)")

backstop = local_box(BACKSTOP_THETA, Z_LATCH, R - OVERLAP, BACKSTOP_W, BACKSTOP_L, BACKSTOP_H + OVERLAP, outward=True)
spine = spine.fuse(backstop)
check(spine, "spine (+backstop)")

# --- 7b. SERVO mount: through-wall port + outboard flange boss. The tab
# flange sits AT the outer surface; a rectangular port through the wall lets
# the case's long (inboard) side hang in the already-open bay cavity, while
# a short boss proud of the OD houses the shaft/horn end. See SERVO param
# block for the flange-split assumption.
print("[7b] servo mount (through-wall, real SG90 envelope)")
port = local_box(SERVO_THETA, Z_LATCH, R - WALL_BAY - SERVO_IN_DEPTH - 2.0,
                  SERVO_BODY_W + 2.0 * SERVO_CLR, SERVO_BODY_L + 2.0 * SERVO_CLR,
                  WALL_BAY + SERVO_IN_DEPTH + 3.0, outward=True)
spine = spine.cut(port)
check(spine, "spine (servo port)")

pad = local_box(SERVO_THETA, Z_LATCH, R - OVERLAP, PAD_TAN, PAD_AX, SERVO_OUT_PROUD + OVERLAP, outward=True)
spine = spine.fuse(pad)
p1 = local_cyl_through(SERVO_THETA, Z_LATCH, R, PAD_HOLE_D, 20.0)
p1.translate(local_placement(SERVO_THETA, Z_LATCH, R).multVec(Vector(0, -PAD_HOLE_AX, 0))
             - local_placement(SERVO_THETA, Z_LATCH, R).Base)
p2 = local_cyl_through(SERVO_THETA, Z_LATCH, R, PAD_HOLE_D, 20.0)
p2.translate(local_placement(SERVO_THETA, Z_LATCH, R).multVec(Vector(0, PAD_HOLE_AX, 0))
             - local_placement(SERVO_THETA, Z_LATCH, R).Base)
spine = spine.cut(p1).cut(p2)
spine = spine.removeSplitter()
check(spine, "spine (+servo pad, final)")

# ================================================================== LATCHARM

print("[8] latch arm")
hub_pt = frame_point(SERVO_THETA, Z_LATCH, R + SERVO_OUT_PROUD)
paddle_pt = frame_point(PADDLE_THETA, Z_LATCH, PADDLE_R)
mid = (hub_pt + paddle_pt) * 0.5
y_dir = paddle_pt - hub_pt
reach = y_dir.Length
n_avg = (Vector(math.cos(math.radians(SERVO_THETA)), math.sin(math.radians(SERVO_THETA)), 0)
         + Vector(math.cos(math.radians(PADDLE_THETA)), math.sin(math.radians(PADDLE_THETA)), 0))

arm_body = oriented_box(mid, y_dir, n_avg, reach + 2.0 * OVERLAP, PADDLE_TAN * 0.5, 2.5)
hub_cyl = local_cyl_proud(SERVO_THETA, Z_LATCH, R + SERVO_OUT_PROUD - OVERLAP, HUB_D, HUB_H + OVERLAP)
paddle_box = local_box(PADDLE_THETA, Z_LATCH, PADDLE_R - OVERLAP, PADDLE_TAN, PADDLE_AX, 2.5 + OVERLAP)

latch_arm = arm_body.fuse(hub_cyl).fuse(paddle_box)
pilot = local_cyl_through(SERVO_THETA, Z_LATCH, R + SERVO_OUT_PROUD, HUB_PILOT_D, 20.0)
latch_arm = latch_arm.cut(pilot)
latch_arm = latch_arm.removeSplitter()
check(latch_arm, "latch_arm (final)")
expected_min_vol = reach * PADDLE_TAN * 0.5 * 2.0
if latch_arm.Volume < expected_min_vol:
    raise RuntimeError("latch_arm volume %.1f suspiciously small (expected >~%.0f) -- geometry likely twisted/self-intersecting"
                        % (latch_arm.Volume, expected_min_vol))

# ============================================================ SHOCK CORD CLIPS

print("[9] shock cord snap clips x%d (routing only -- eyebolt is the load path)" % len(CLIP_Z_LIST))
for cz in CLIP_Z_LIST:
    r_in = true_inner_r(cz)
    clip_base = local_box(CLIP_THETA, cz, r_in, CLIP_W, CLIP_LEN, CLIP_REACH, outward=False)
    channel_r = r_in - CLIP_REACH * 0.5
    channel = local_cyl_axial(CLIP_THETA, cz, channel_r, CORD_D + 2.0 * CLIP_CLR, CLIP_LEN + 2.0)
    clip_solid = clip_base.cut(channel)
    # open mouth on the cavity-facing (radially inward) side, narrower than
    # the cord so it must flex the boss's rim to click the cord in
    mouth = local_box(CLIP_THETA, cz, channel_r, CORD_D * CLIP_MOUTH_FRAC, CLIP_LEN + 2.0,
                       CLIP_REACH, outward=False)
    clip_solid = clip_solid.cut(mouth)
    door = door.fuse(clip_solid)
door = door.removeSplitter()
check(door, "door (+shock cord clips, final)")

# ============================================================ SWING CLEARANCE

print("[9.5] door-swing clearance check (peg vs fixed backstop)")
# DoorHalf pivots about the hinge cluster's line -- not a constant theta=180
# like v2 anymore, since the oval boundary curves. Approximate the physical
# hinge axis as the straight line through the CENTRE hinge point (the flat
# peak of the ellipse, where the curve's tangent is genuinely axis-parallel);
# the other two points are within 1.3 deg of this, which is what makes 3
# discrete flexure strips a reasonable stand-in for a curved hinge line at
# all -- if that spread were large this approximation would not hold.
theta_hinge_axis = DOOR_THETA_C - door_halfwidth(OVAL_ZC)
hinge_axis_pt = frame_point(theta_hinge_axis, 0.0, R)


def rotate_about_hinge(pt, phi_deg):
    dx = pt.x - hinge_axis_pt.x
    dy = pt.y - hinge_axis_pt.y
    phi = math.radians(phi_deg)
    dx2 = dx * math.cos(phi) - dy * math.sin(phi)
    dy2 = dx * math.sin(phi) + dy * math.cos(phi)
    return Vector(hinge_axis_pt.x + dx2, hinge_axis_pt.y + dy2, pt.z)


peg_tip_closed = frame_point(PEG_THETA, Z_LATCH, R + PEG_LEN)
backstop_pt = frame_point(BACKSTOP_THETA, Z_LATCH, R + BACKSTOP_H / 2.0)
backstop_reach = max(BACKSTOP_W, BACKSTOP_L, BACKSTOP_H)

d0 = (peg_tip_closed - backstop_pt).Length
found_opening = False
for sign in (1.0, -1.0):
    p20 = rotate_about_hinge(peg_tip_closed, sign * 20.0)
    if (p20 - backstop_pt).Length > d0:
        found_opening = True
        break
if not found_opening:
    sign = 1.0
    print("  WARNING: neither rotation sign increases peg-to-backstop distance at 20 deg")

for phi in (0.0, 20.0, 45.0, 70.0, 100.0):
    p = rotate_about_hinge(peg_tip_closed, sign * phi)
    d = (p - backstop_pt).Length
    clear = d - backstop_reach
    flag = "OK" if clear > 2.0 else ("TIGHT" if clear > 0 else "COLLISION RISK")
    print("  phi=%5.1f deg  peg=(%.1f,%.1f,%.1f)  dist-to-backstop=%.1f mm  margin=%.1f mm  [%s]"
          % (phi, p.x, p.y, p.z, d, clear, flag))

print("[9.6] door free-edge (latch side) vs spine-edge swing check (multiple Z stations)")
# The oval's free edge is theta = DOOR_THETA_C + door_halfwidth(z); check it
# against the Spine's edge at the same z (same curve, GAP_DEG apart) across
# several stations spanning the oval, not just at the latch.
for zc in (50.0, 80.0, Z_LATCH, 135.0, 165.0):
    r_true = true_outer_r(zc)
    w_c = door_halfwidth(zc)
    edge_closed = frame_point(DOOR_THETA_C + w_c - GAP_DEG, zc, r_true)
    spine_edge = frame_point(DOOR_THETA_C + w_c, zc, r_true)
    d0 = (edge_closed - spine_edge).Length
    print("  z=%5.1f  r=%.1f  half-width=%.1f deg  closed gap=%.3f mm" % (zc, r_true, w_c, d0))
    for phi in (5.0, 10.0, 20.0, 45.0):
        p = rotate_about_hinge(edge_closed, sign * phi)
        d = (p - spine_edge).Length
        flag = "OK" if d >= d0 else "CHECK -- edge moved toward spine"
        print("    phi=%5.1f  dist-to-spine-edge=%.3f mm  [%s]" % (phi, d, flag))

# ======================================================================= I/O


def export(shape, name):
    step_path = os.path.join(MODELS, "PhoenixABS40-43_nose_%s_%s.step" % (name, REV))
    stl_path = os.path.join(MODELS, "PhoenixABS40-43_nose_%s_%s.stl" % (name, REV))
    shape.exportStep(step_path)
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.08, AngularDeflection=0.25)
    mesh.write(stl_path)
    print("  wrote %s  (%.1f g @ 100%% infill)" % (name, shape.Volume * RHO_ABS))
    return step_path, stl_path


print("[10] export")
export(spine, "Spine")
export(door, "DoorHalf")
export(latch_arm, "LatchArm")

doc.recompute()
fcstd_path = os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_v3.FCStd")
o1 = doc.addObject("Part::Feature", "Spine")
o1.Shape = spine
o2 = doc.addObject("Part::Feature", "DoorHalf")
o2.Shape = door
o3 = doc.addObject("Part::Feature", "LatchArm")
o3.Shape = latch_arm
doc.recompute()
doc.saveAs(fcstd_path)
print("saved %s" % fcstd_path)

print("=== DONE ===")
print("Total nosecone length: %.1f mm  (ogive %.0f + bay %.0f + taper %.0f + shoulder %.0f)"
      % (Z_SH1, L_OGV, Z_BAY1 - Z_BAY0, Z_SH_TAPER1 - Z_SH_TAPER0, Z_SH1 - Z_SH0))
print("Door oval: Z %.0f-%.0f, peak half-width %.0f deg (%.0f deg total)"
      % (OVAL_Z0, OVAL_Z1, DOOR_HALFW_MAX, 2.0 * DOOR_HALFW_MAX))

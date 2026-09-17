# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- fairing-split nosecone with servo-latched hinged half, v2

SOURCE OF TRUTH. Every dimension is a named constant below; edit here and
re-run, never edit the STL/STEP/FCStd by hand. Supersedes
PhoenixABS40-43_Nosecone_v1.py (kept for history, not deleted) -- v1 cut a
small door-window into a fixed shell; the project owner asked for a real
fairing split instead (2026-09-15 feedback): "the door should BE the
nosecone... at least 1/2 of it should detach... think like a fairing."

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

ARCHITECTURE CHANGE from DESIGN.md Sec7 (unchanged from v1's note): this
REPLACES the spring-piston/ball-detent whole-nose-separation system built in
../Models/ (ejection_poc_v1, aft_retention_v1, avbay_cassette_v1, DummyNose).
The nosecone assembly is permanently fixed to the body tube; it does not
separate from the airframe. See NOSECONE_DESIGN.md for the full rationale.

ARCHITECTURE CHANGE from v1: the nosecone is now split lengthwise (tip to
shoulder) into two pieces along a seam that runs the FULL length, not a small
window in one side:

  Spine (half A, theta 0-180 deg): carries the COMPLETE, unsplit bulkhead and
    shoulder ring -- this is what's bonded + screwed to the airframe. Forward
    of the bulkhead it is only a half-shell (the other 180 deg is open/absent).

  DoorHalf (half B, theta 180-360 deg, ogive+barrel only, z < bulkhead): a
    free-standing half-shell petal with NO shoulder and NO bulkhead of its
    own -- it has no independent attachment to the airframe at all. It is
    held onto the Spine purely by the hinge (one seam) and the latch (the
    other seam). Releasing the latch lets the ENTIRE DoorHalf swing open on
    the hinge, exposing the full bore -- not a small window.

Both seams run the length of the ogive+barrel region (z 0 to Z_BULK0=182):
  - Hinge seam at theta=180 deg: 3 flexure-strip points (spring-steel shim,
    same "hinge and spring in one part" idea as v1, now repeated along a
    long seam instead of once across a short door edge).
  - Latch seam at theta=0/360 deg: one servo-driven peg/backstop/gate point,
    same "geometry holds the load, not the servo" principle as v1.

Smoothness fix (the other piece of feedback): v1 approximated the ogive as a
50-segment polyline revolved into a surface, which faceted visibly. A tangent
ogive profile IS a true circular arc (that is what "tangent ogive" means
mathematically -- see ogive_arc_params below) -- this version builds it as an
exact Part.Arc, not a polygon, so the surface is actually smooth, not just
higher-resolution.

Payload: folded parachute pack, 100 x 20 x 20 mm (confirmed with user). With
the whole forward half hinging open, the pack now has the ENTIRE ogive+barrel
cavity to pass through, not a small door -- extraction is easier than v1, not
harder.
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
REV = "v2"

RHO_ABS = 1.05e-3   # g/mm^3, 100% infill reference (matches aft_retention_v1.py)

# --- airframe (DESIGN.md Sec2/Sec8) ---
R_AF_O = 21.5        # airframe OD 43.0 / 2
R_AF_I = 20.0        # airframe ID 40.0 / 2

# --- outer profile stations (Z from nose tip, +Z toward the airframe) ---
R = 21.5              # nosecone/barrel OD radius -- flush with airframe OD
L_OGV = 100.0         # tangent-ogive nose length
WALL_OGV = 2.0        # shell wall over the ogive
WALL_BAY = 3.5        # shell wall over the barrel -- thickened; this is where
                       # the seams, hinges and latch live

Z_BAY0, Z_BAY1 = L_OGV, 190.0                 # cylindrical bay, constant r=R
Z_SH_TAPER0, Z_SH_TAPER1 = 190.0, 193.0       # 3 mm lead-in taper into the shoulder
R_SH = 19.85                                   # shoulder OD/2 = dia 39.7 (DESIGN.md item 11: 39.6-39.8)
Z_SH0, Z_SH1 = 193.0, 237.0                   # shoulder land, 44 mm -- total insertable 47 mm (>=43 req'd)

R_BAY_IN = R - WALL_BAY                        # 18.0, bay cavity radius
Z_BULK0, Z_BULK1 = 182.0, Z_SH_TAPER0          # 182 -> 190, 8 mm solid bulkhead band (cavity ends at 182)
                                                 # bulkhead + shoulder (z>=182) stay a COMPLETE, unsplit ring

# tangent ogive is a true circular arc: rho = (R^2+L^2)/(2R), arc centre at
# (r=R-rho, z=L). A concentric offset (same centre, radius-wall) is therefore
# ALSO an exact circular arc -- a genuinely constant-thickness wall, not the
# same-Z radial offset v1 used.
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
    """Exact circular arc from the (possibly offset-inward) tip to (R-wall, L_OGV)."""
    radius, center_r, tip_z = ogive_arc_params(wall)
    p_tip = Vector(0.0, 0.0, tip_z)
    z_mid = (tip_z + L_OGV) / 2.0
    p_mid = Vector(ogive_arc_r(z_mid, wall), 0.0, z_mid)
    p_base = Vector(R - wall, 0.0, L_OGV)
    return Part.Arc(p_tip, p_mid, p_base).toShape()


# --- fairing split ---
GAP_DEG = 1.0          # angular clearance gap between the two halves (~CLEAR=0.35mm at r=21.5, rounded up)
SPINE_THETA0, SPINE_THETA1 = 0.0, 180.0        # half A -- fixed, carries bulkhead+shoulder
DOOR_THETA0, DOOR_THETA1 = 180.0 + GAP_DEG, 360.0 - GAP_DEG   # half B -- shrunk for clearance both edges

# --- flexure hinge points along the theta=180 seam (spring-steel shim strips) ---
# Restricted to the constant-radius barrel (100-182): the wedge() cutter below
# assumes r~=R at the cut location, which is only true there -- in the ogive
# taper the true surface radius is much smaller and a wedge built around R
# would miss the material entirely.
HINGE_Z_LIST = [110.0, 145.0, 172.0]
HINGE_HALF_LEN = 6.0      # axial half-length of each strip recess (12 mm strip)
HINGE_ANG_WIDTH = 11.0    # deg, angular width of each recess pocket
HINGE_DEPTH = 0.6         # seats ~0.4-0.5 mm spring-steel shim flush
HINGE_HOLE_D = 2.2        # M2 clearance

# --- latch: single servo-driven point on the theta=0/360 seam ---
Z_LATCH = 128.0
PEG_THETA = 360.0 - GAP_DEG - 5.0   # on DoorHalf, a few deg in from its shrunk edge (~354 deg)
PEG_D = 3.0
PEG_LEN = 4.5
BACKSTOP_THETA = 8.0                 # on Spine, a few deg in from its edge (theta=0)
BACKSTOP_W, BACKSTOP_L, BACKSTOP_H = 5.0, 5.0, 3.0
SERVO_THETA = 25.0                   # on Spine, further in for the servo body
PAD_TAN = 14.0
PAD_AX = 34.0            # SG90-class footprint incl. mounting tabs -- generic, bench-verify vs actual servo
PAD_PROUD = 1.5
PAD_HOLE_D = 2.2
PAD_HOLE_AX = 14.0        # +-, from pad centre along axial (mounting-tab spacing)
PADDLE_THETA = 0.0        # LatchArm gate centre -- spans from the peg (~354) to the backstop (~8)
PADDLE_TAN, PADDLE_AX = 10.0, 6.0
PADDLE_R = R + PEG_LEN - 1.0

HUB_D = 8.0
HUB_H = 2.0
HUB_PILOT_D = 1.2

# --- aft-rim capture: DoorHalf's aft edge (Z=182) was a free, unsupported
# cantilever sitting right in the airstream at the nosecone/body-tube joint
# -- nothing but the hinge (theta=180) and the single mid-barrel latch
# (Z=128) held it. Extend the door's rim LIP_Z further aft into a matching
# socket cut into what was solid Spine bulkhead: the socket's radial walls
# (R_BAY_IN, R) then constrain the rim against radial flutter at the aft
# edge too, not just at the two seams. Verified for swing clearance below
# (SWING CLEARANCE section) before being trusted -- back it out if that
# check fails rather than shipping an unverified bind risk.
LIP_Z = 3.0
LIP_CLEAR_AX = 0.3    # axial clearance at the pocket floor
LIP_CLEAR_RAD = 0.2   # radial clearance, pocket vs rim, each side

# --- bulkhead / shock-cord anchor (Spine only -- unsplit, on-axis) ---
EYEBOLT_HOLE_D = 4.5      # M4 clearance, bolt in shear against washers both faces
EYEBOLT_CB_D = 10.0
EYEBOLT_CB_DEPTH = 2.0

# --- shoulder positive retention (glue/friction alone is not adequate) ---
N_RET_SCREWS = 3
Z_RET_SCREW = (Z_SH0 + Z_SH1) / 2.0     # 215, mid-shoulder land
RET_SCREW_D = 3.4                        # M3 clearance

# fused (not cut) solids must genuinely OVERLAP, never merely touch at a
# shared face -- aft_retention_v1.py's MERGE note.
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


def true_outer_r(z):
    """Actual OD/2 at any Z, following the ogive arc, not assuming the
    barrel's constant R -- needed for swing checks at Z < 100."""
    if z <= L_OGV:
        return ogive_arc_r(z, 0.0)
    elif z <= Z_BAY1:
        return R
    elif z <= Z_SH_TAPER1:
        frac = (z - Z_SH_TAPER0) / (Z_SH_TAPER1 - Z_SH_TAPER0)
        return R + (R_SH - R) * frac
    else:
        return R_SH


def check(shape, label):
    ok = shape.isValid()
    print("  [%s] valid=%s solids=%d volume=%.1f mm^3 bbox=%s"
          % (label, ok, len(shape.Solids), shape.Volume, shape.BoundBox))
    if not ok:
        raise RuntimeError("INVALID SHAPE at step: %s" % label)
    return shape


# ====================================================================== BUILD

print("=== Phoenix ABS 40-43 Nosecone %s (fairing split) ===" % REV)
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRINTS, exist_ok=True)

doc = App.newDocument("PhoenixABS40-43_Nosecone_v2")

# --- 1. outer blank: true-arc ogive + barrel + taper + shoulder ---
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

# --- 2. cavity: concentric-arc ogive offset + bay offset, capped at the bulkhead ---
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

# --- 3. bulkhead eyebolt hole + counterbores (on-axis -- must happen before the
#        split, since the split plane would otherwise bisect this hole) ---
print("[3] eyebolt hole")
eyebolt = Part.makeCylinder(EYEBOLT_HOLE_D / 2.0, Z_BULK1 - Z_BULK0 + 2.0, Vector(0, 0, Z_BULK0 - 1.0))
cb_fwd = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK0 - 0.25))
cb_aft = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK1 - EYEBOLT_CB_DEPTH + 0.25))
full_shell = full_shell.cut(eyebolt).cut(cb_fwd).cut(cb_aft)
check(full_shell, "full_shell (eyebolt)")

# --- 4. shoulder retention screws x3 (full ring -- unaffected by the split) ---
print("[4] shoulder retention screws x%d" % N_RET_SCREWS)
for i in range(N_RET_SCREWS):
    th = 360.0 * i / N_RET_SCREWS
    hole = local_cyl_through(th, Z_RET_SCREW, R_SH, RET_SCREW_D, 20.0)
    full_shell = full_shell.cut(hole)
check(full_shell, "full_shell (retention screws)")

# --- 5. split into Spine (half A) + DoorHalf (half B) ---
# Only z < Z_BULK0 is split -- bulkhead+shoulder (z >= Z_BULK0) stay a
# complete, unsplit ring, entirely on the Spine side.
print("[5] fairing split")
cutter_for_spine = wedge(0.0, R + 5.0, 0.0, Z_BULK0, SPINE_THETA1, 360.0)
spine = full_shell.cut(cutter_for_spine)
check(spine, "spine (before hinge/latch features)")

door = full_shell.cut(wedge(0.0, R + 5.0, 0.0, Z_BULK0, 0.0, DOOR_THETA0))
door = door.cut(wedge(0.0, R + 5.0, 0.0, Z_BULK0, DOOR_THETA1, 360.0))
door = door.cut(wedge(0.0, R + 5.0, Z_BULK0 + LIP_Z - LIP_CLEAR_AX, Z_SH1 + 2.0, 0.0, 360.0))
check(door, "door (before hinge/latch features)")

# aft-rim capture: extend the door's rim into a socket cut from the Spine's
# bulkhead (see LIP_Z note in the parameter block)
lip_pocket = wedge(R_BAY_IN - LIP_CLEAR_RAD, R + LIP_CLEAR_RAD, Z_BULK0, Z_BULK0 + LIP_Z, DOOR_THETA0, DOOR_THETA1)
spine = spine.cut(lip_pocket)
check(spine, "spine (aft-rim socket)")

# --- 6. flexure hinge points along the theta=180 seam ---
print("[6] hinge points x%d" % len(HINGE_Z_LIST))
for hz in HINGE_Z_LIST:
    pocket_a = wedge(R - HINGE_DEPTH, R + 0.5, hz - HINGE_HALF_LEN, hz + HINGE_HALF_LEN,
                      180.0 - HINGE_ANG_WIDTH, 180.0)
    spine = spine.cut(pocket_a)
    theta_hole_a = 180.0 - HINGE_ANG_WIDTH * 0.5
    for dz in (-3.0, 3.0):
        h = local_cyl_through(theta_hole_a, hz + dz, R, HINGE_HOLE_D, 20.0)
        spine = spine.cut(h)

    t0 = DOOR_THETA0
    pocket_b = wedge(R - HINGE_DEPTH, R + 0.5, hz - HINGE_HALF_LEN, hz + HINGE_HALF_LEN,
                      t0, t0 + HINGE_ANG_WIDTH)
    door = door.cut(pocket_b)
    theta_hole_b = t0 + HINGE_ANG_WIDTH * 0.5
    for dz in (-3.0, 3.0):
        h = local_cyl_through(theta_hole_b, hz + dz, R, HINGE_HOLE_D, 20.0)
        door = door.cut(h)
check(spine, "spine (hinge pockets)")
check(door, "door (hinge pockets)")

# --- 7. latch: peg on DoorHalf; backstop + servo pad on Spine ---
print("[7] latch (peg/backstop/servo pad)")
peg = local_cyl_proud(PEG_THETA, Z_LATCH, R - OVERLAP, PEG_D, PEG_LEN + OVERLAP)
door = door.fuse(peg)
door = door.removeSplitter()
check(door, "door (+peg, final)")

backstop = local_box(BACKSTOP_THETA, Z_LATCH, R - OVERLAP, BACKSTOP_W, BACKSTOP_L, BACKSTOP_H + OVERLAP, outward=True)
spine = spine.fuse(backstop)

pad = local_box(SERVO_THETA, Z_LATCH, R - OVERLAP, PAD_TAN, PAD_AX, PAD_PROUD + OVERLAP, outward=True)
spine = spine.fuse(pad)
p1 = local_cyl_through(SERVO_THETA, Z_LATCH, R, PAD_HOLE_D, 20.0)
p1.translate(local_placement(SERVO_THETA, Z_LATCH, R).multVec(Vector(0, -PAD_HOLE_AX, 0))
             - local_placement(SERVO_THETA, Z_LATCH, R).Base)
p2 = local_cyl_through(SERVO_THETA, Z_LATCH, R, PAD_HOLE_D, 20.0)
p2.translate(local_placement(SERVO_THETA, Z_LATCH, R).multVec(Vector(0, PAD_HOLE_AX, 0))
             - local_placement(SERVO_THETA, Z_LATCH, R).Base)
spine = spine.cut(p1).cut(p2)
spine = spine.removeSplitter()
check(spine, "spine (+backstop+pad, final)")

# ================================================================== LATCHARM

print("[8] latch arm")
hub_pt = frame_point(SERVO_THETA, Z_LATCH, R + PAD_PROUD)
paddle_pt = frame_point(PADDLE_THETA, Z_LATCH, PADDLE_R)
mid = (hub_pt + paddle_pt) * 0.5
y_dir = paddle_pt - hub_pt
reach = y_dir.Length
n_avg = (Vector(math.cos(math.radians(SERVO_THETA)), math.sin(math.radians(SERVO_THETA)), 0)
         + Vector(math.cos(math.radians(PADDLE_THETA)), math.sin(math.radians(PADDLE_THETA)), 0))

arm_body = oriented_box(mid, y_dir, n_avg, reach + 2.0 * OVERLAP, PADDLE_TAN * 0.5, 2.5)
hub_cyl = local_cyl_proud(SERVO_THETA, Z_LATCH, R + PAD_PROUD - OVERLAP, HUB_D, HUB_H + OVERLAP)
paddle_box = local_box(PADDLE_THETA, Z_LATCH, PADDLE_R - OVERLAP, PADDLE_TAN, PADDLE_AX, 2.5 + OVERLAP)

latch_arm = arm_body.fuse(hub_cyl).fuse(paddle_box)
pilot = local_cyl_through(SERVO_THETA, Z_LATCH, R + PAD_PROUD, HUB_PILOT_D, 20.0)
latch_arm = latch_arm.cut(pilot)
latch_arm = latch_arm.removeSplitter()
check(latch_arm, "latch_arm (final)")
expected_min_vol = reach * PADDLE_TAN * 0.5 * 2.0
if latch_arm.Volume < expected_min_vol:
    raise RuntimeError("latch_arm volume %.1f suspiciously small (expected >~%.0f) -- geometry likely twisted/self-intersecting"
                        % (latch_arm.Volume, expected_min_vol))

# ============================================================ SWING CLEARANCE

print("[8.5] door-swing clearance check (peg vs fixed backstop)")
# DoorHalf is a rigid body hinged along the theta=180 seam -- a line parallel
# to global Z through (x=-R, y=0). ALL points on it rotate about that one
# axis. Rotate the peg tip about it and confirm it clears the fixed backstop
# (on the Spine, which cannot move) as the door swings open.
hinge_axis_pt = Vector(-R, 0.0, 0.0)


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

print("[8.6] door free-edge vs spine-edge swing check (multiple Z stations)")
# The peg check above only tests one point near the latch. Check the door's
# own outer-surface edge (theta=DOOR_THETA1, close to the seam) against the
# Spine's fixed edge (theta=SPINE_THETA0=0, same Z, true OD at that Z) along
# the whole seam length, not just at the latch.
for zc in (10.0, 50.0, 90.0, 130.0, 170.0):
    r_true = true_outer_r(zc)
    edge_closed = frame_point(DOOR_THETA1, zc, r_true)
    spine_edge = frame_point(SPINE_THETA0, zc, r_true)
    d0 = (edge_closed - spine_edge).Length
    print("  z=%5.1f  r=%.1f  closed gap=%.3f mm" % (zc, r_true, d0))
    for phi in (5.0, 10.0, 20.0, 45.0):
        p = rotate_about_hinge(edge_closed, sign * phi)
        d = (p - spine_edge).Length
        flag = "OK" if d >= d0 else "CHECK -- edge moved toward spine"
        print("    phi=%5.1f  dist-to-spine-edge=%.3f mm  [%s]" % (phi, d, flag))

print("[8.7] aft-rim lip swing check (Z=%.0f-%.1f socket, inner radius)" % (Z_BULK0, Z_BULK0 + LIP_Z))
# [8.6] already covers the rim's OUTER surface (r=R) at Z up to 170, close to
# the lip. The lip adds a NEW boundary that didn't exist before: the INNER
# radius (r=R_BAY_IN) of the socket, which has no counterpart earlier in the
# door's length (the cavity previously just ended flat at Z=182 with no
# seam feature there at all). Check it the same way as [8.6]: the near-hinge
# corner is expected to barely move (it's essentially AT the hinge axis by
# construction -- theta=180+GAP_DEG is right next to theta=180=the hinge
# line itself, so small motion there is the hinge working correctly, not a
# collision risk) -- the free-edge corner is the one that matters.
for zc in (Z_BULK0 + 0.5, Z_BULK0 + LIP_Z - LIP_CLEAR_AX - 0.5):
    r_c = R_BAY_IN
    edge_closed = frame_point(DOOR_THETA1, zc, r_c)
    spine_edge = frame_point(SPINE_THETA0, zc, r_c)
    d0 = (edge_closed - spine_edge).Length
    print("  z=%5.1f  r=%.1f (inner)  closed gap=%.3f mm" % (zc, r_c, d0))
    for phi in (2.0, 5.0, 10.0):
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


print("[9] export")
export(spine, "Spine")
export(door, "DoorHalf")
export(latch_arm, "LatchArm")

doc.recompute()
fcstd_path = os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_v2.FCStd")
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

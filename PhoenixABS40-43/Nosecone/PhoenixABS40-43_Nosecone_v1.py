# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- nosecone with a servo-latched, spring-hinged deployment door, v1

SOURCE OF TRUTH. Every dimension is a named constant below; edit here and re-run,
never edit the STL/STEP/FCStd by hand.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

ARCHITECTURE CHANGE from DESIGN.md Sec7: this REPLACES the spring-piston /
ball-detent whole-nose-separation system (built in ../Models/ as ejection_poc_v1,
aft_retention_v1, avbay_cassette_v1, DummyNose). The nosecone no longer separates
from the airframe at all -- it is permanently fixed to the body tube (glued +
positively screwed shoulder, see RETENTION below). Recovery deploys through a
hinged door in the nosecone's own wall: the chute lives folded inside the
nosecone, the door pops open under spring load once the servo-driven latch
releases it, and the whole rocket (nose+body+fins, never separated) comes down
under one canopy. The old piston/detent/e-bay-cassette hardware is superseded
for THIS deployment path; avionics placement (does the flight computer move
into the nosecone too?) is an open follow-up, not decided here.

Frame: Z = 0 at the nose tip, +Z aft toward the airframe. Theta = 0 deg is an
arbitrary clocking reference (the door's centerline); the two mechanism
features (latch tab, servo) are clocked away from it.

Airframe (DESIGN.md Sec2/Sec8): OD 43.0 / ID 40.0 / wall 1.5 (BT-60 class).
Nose shoulder per DESIGN.md item 11: grow to dia 39.6-39.8, >=43 mm engagement.
We use dia 39.7, 47 mm insertable length (3 mm taper + 44 mm land) -- both
satisfied.

Mechanism principle (see advisor notes in chat / NOSECONE_DESIGN.md):
  - Hinge: FORWARD edge of the door. A flexure hinge -- NOT a printed pin and
    knuckles -- made from a strip of spring-steel shim stock screwed flush
    across shell-side and door-side recesses. It is the hinge AND the "metal
    spring" the brief asked for in one part: it flexes to let the door swing,
    and its own spring-back is what pops the door open once unlatched.
    Forward hinge is deliberate: dynamic pressure on the door (nose-to-tail
    flow) presses a forward-hinged door SHUT, so it cannot pop open from
    aero load alone at speed -- only the flexure spring, once released, can
    open it, and that only wins once dynamic pressure has dropped (apogee).
  - Latch: a radial peg on a tab at the door's AFT edge sits in a notch cut
    in the fixed shell. A servo-driven gate (LatchArm) swings over the notch
    opening and rests against a FIXED backstop boss molded into the shell.
    The door's spring/aero load pushes the peg against the gate, and the gate
    against the backstop -- so the backstop (shell material), not the servo
    gear train, carries the flight load. The servo only has to swing the gate
    off the backstop to release; it never holds load. This mirrors the
    "geometry holds the load, not the servo" principle DESIGN.md Sec7.5.1
    already used for the (now superseded) piston latch.
  - This is a first-pass / bench-fit mechanism, same spirit as the project's
    other *_poc parts: the shell, door, and bay geometry are the load-bearing,
    hard-to-change part and are built to real tolerances; the gate/backstop
    geometry is intentionally simple and should be bench-fitted to the actual
    SG90 horn before flight (see NOSECONE_DESIGN.md open items).

Payload: folded parachute pack, 100 x 20 x 20 mm (10x2x2 cm, confirmed with
user -- "10x2x2 mm" as literally stated was almost certainly a cm/mm slip).
Soft goods -- does not need a rigid channel, just enough cavity volume and an
opening shorter than its own length to stuff/extract through.
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
REV = "v1"

RHO_ABS = 1.05e-3   # g/mm^3, 100% infill reference (matches aft_retention_v1.py)

# --- airframe (DESIGN.md Sec2/Sec8) ---
R_AF_O = 21.5        # airframe OD 43.0 / 2
R_AF_I = 20.0        # airframe ID 40.0 / 2

# --- outer profile stations (Z from nose tip) ---
R = 21.5              # nosecone/barrel OD radius -- flush with airframe OD
L_OGV = 100.0         # tangent-ogive nose length
WALL_OGV = 2.0        # shell wall over the ogive (matches DESIGN.md's 2.0 mm shoulder-wall convention)
WALL_BAY = 3.5        # shell wall over the barrel/bay -- thickened per door-opening structural note
                       # (a 30+ mm chord removes ~90 deg of hoop from a thin tube; thicken locally)

Z_OGV0, Z_OGV1 = 0.0, L_OGV
Z_BAY0, Z_BAY1 = L_OGV, 190.0                 # cylindrical bay, constant r=R
Z_SH_TAPER0, Z_SH_TAPER1 = 190.0, 193.0       # 3 mm lead-in taper into the shoulder
R_SH = 19.85                                   # shoulder OD/2 = dia 39.7 (DESIGN.md item 11: 39.6-39.8)
Z_SH0, Z_SH1 = 193.0, 237.0                   # shoulder land, 44 mm -- total insertable 47 mm (>=43 req'd)

R_BAY_IN = R - WALL_BAY                        # 18.0, bay cavity radius
Z_BULK0, Z_BULK1 = 182.0, Z_SH_TAPER0          # 182 -> 190, 8 mm solid bulkhead band (cavity ends at 182)

# tangent ogive: rho = (R^2+L^2)/(2R); arc centre at (z=L, y=R-rho)
OGV_RHO = (R * R + L_OGV * L_OGV) / (2.0 * R)

def ogive_r(z):
    dz = L_OGV - z
    val = OGV_RHO * OGV_RHO - dz * dz
    if val < 0.0:
        val = 0.0
    return math.sqrt(val) + (R - OGV_RHO)

# --- door opening ---
Z_DOOR0, Z_DOOR1 = 112.0, 178.0     # 66 mm long -- soft-goods pack does not need a 100 mm-long hatch
THETA_DOOR = 48.0                    # deg half-width -> opening spans [-48, +48] (chord 32 mm at r=21.5)
CLEAR = 0.35                         # door-to-opening clearance, mm, applied on all four edges

# --- flexure hinge recesses (shell side fwd of the opening; mirrored on the door's fwd edge) ---
# Cut as a true angular wedge (follows the r=R cylinder exactly), NOT a flat
# box: a flat box this wide has sagitta R-sqrt(R^2-(w/2)^2) = 4.4 mm at a 26 mm
# chord against a 0.6 mm pocket depth -- it would only touch the real curved
# surface in a lens near the centre, not cut a uniform pocket across the full
# width. THETA_HINGE_HALF below gives an equivalent ~24 mm chord.
THETA_HINGE_HALF = 32.0   # deg
HINGE_L = 8.0              # axial length, each side of the cut line
HINGE_DEPTH = 0.6          # pocket depth -- seats ~0.4-0.5 mm spring-steel shim flush
HINGE_HOLE_D = 2.2         # M2 clearance
HINGE_HOLE_X = 9.0         # +-, from centreline (tangent-plane offset -- see note at use site)

# --- latch tab / notch (door aft-outer corner) ---
THETA_TAB = 40.0                      # deg, within the door's +-48 span, clear of its true edge
Z_TAB0, Z_TAB1 = Z_DOOR1 - CLEAR, 181.5   # tab extends from the door's (clearance-shrunk) aft edge
TAB_W = 9.0
PEG_D = 3.0
PEG_LEN = 4.5                         # proud of the tab's outer face
NOTCH_THETA0, NOTCH_THETA1 = 28.0, 52.0
Z_NOTCH0, Z_NOTCH1 = Z_DOOR1 - CLEAR, Z_BULK0

# --- servo pad + backstop (fixed shell, clocked away from the door) ---
THETA_SERVO = 80.0
Z_SERVO_C = 163.0            # pad centre z -- stays clear of the Z_SH_TAPER0=190 taper
PAD_TAN = 14.0
PAD_AX = 34.0                 # SG90-class footprint incl. mounting tabs -- generic, bench-verify vs actual servo
PAD_PROUD = 1.5
PAD_HOLE_D = 2.2
PAD_HOLE_AX = 14.0             # +-, from pad centre along axial (mounting-tab spacing)

THETA_BACKSTOP = 55.0
Z_BACKSTOP = 180.0
BACKSTOP_W, BACKSTOP_L, BACKSTOP_H = 5.0, 5.0, 3.0

# --- bulkhead / shock-cord anchor ---
Z_EYEBOLT = (Z_BULK0 + Z_BULK1) / 2.0   # 186, mid-bulkhead
EYEBOLT_HOLE_D = 4.5                     # M4 clearance, bolt in shear against washers both faces
EYEBOLT_CB_D = 10.0
EYEBOLT_CB_DEPTH = 2.0

# --- shoulder positive retention (per advisor: friction/glue alone is not enough) ---
N_RET_SCREWS = 3
Z_RET_SCREW = (Z_SH0 + Z_SH1) / 2.0     # 215, mid-shoulder land
RET_SCREW_D = 3.4                        # M3 clearance

# --- LatchArm (servo horn attachment) ---
HUB_D = 8.0
HUB_H = 2.0
HUB_PILOT_D = 1.2
PADDLE_TAN, PADDLE_AX = 8.0, 6.0
PADDLE_R = R + PEG_LEN - 1.0             # sits just below the peg tip, over the notch

# fused (not cut) solids must genuinely OVERLAP, never merely touch at a shared
# face -- aft_retention_v1.py's MERGE note: touching faces leave a 2-solid
# compound whose next boolean silently returns garbage. Applied below wherever
# a proud/attached feature is fused onto the shell/door/arm.
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


def check(shape, label):
    ok = shape.isValid()
    print("  [%s] valid=%s solids=%d volume=%.1f mm^3 bbox=%s"
          % (label, ok, len(shape.Solids), shape.Volume, shape.BoundBox))
    if not ok:
        raise RuntimeError("INVALID SHAPE at step: %s" % label)
    return shape


# ====================================================================== BUILD

print("=== Phoenix ABS 40-43 Nosecone %s ===" % REV)
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRINTS, exist_ok=True)

doc = App.newDocument("PhoenixABS40-43_Nosecone_v1")

# --- 1. outer blank: ogive + barrel + taper + shoulder ---
print("[1] outer blank")
N = 50
pts_outer = [Vector(0, 0, 0)]
for i in range(1, N + 1):
    z = L_OGV * i / N
    pts_outer.append(Vector(ogive_r(z), 0, z))
pts_outer.append(Vector(R, 0, Z_BAY1))
pts_outer.append(Vector(R_SH, 0, Z_SH_TAPER1))
pts_outer.append(Vector(R_SH, 0, Z_SH1))
pts_outer.append(Vector(0, 0, Z_SH1))
pts_outer.append(Vector(0, 0, 0))
wire_outer = Part.makePolygon(pts_outer)
face_outer = Part.Face(wire_outer)
outer_solid = face_outer.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)
check(outer_solid, "outer_solid")

# --- 2. cavity: ogive-offset + bay-offset, capped flat at the bulkhead ---
print("[2] cavity")
pts_inner = []
for i in range(0, N + 1):
    z = L_OGV * i / N
    r = ogive_r(z) - WALL_OGV
    if r < 0.0:
        r = 0.0
    pts_inner.append(Vector(r, 0, z))
pts_inner.append(Vector(R_BAY_IN, 0, Z_BAY0))
pts_inner.append(Vector(R_BAY_IN, 0, Z_BULK0))
pts_inner.append(Vector(0, 0, Z_BULK0))
pts_inner.append(Vector(0, 0, 0))
wire_inner = Part.makePolygon(pts_inner)
face_inner = Part.Face(wire_inner)
inner_solid = face_inner.revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)
check(inner_solid, "inner_solid")

shell = outer_solid.cut(inner_solid)
check(shell, "shell (hollowed)")

# --- 3. door opening + latch notch ---
# The opening is cut to the FULL envelope; the printed door is built to a
# CLEAR-shrunk envelope (Sec DOOR below) so it swings freely with a uniform gap.
print("[3] door opening + notch")
door_cutter = wedge(15.0, 25.0, Z_DOOR0, Z_DOOR1, -THETA_DOOR, THETA_DOOR)
shell = shell.cut(door_cutter)
check(shell, "shell (door opening cut)")

notch_cutter = wedge(15.0, 26.0, Z_NOTCH0, Z_NOTCH1, NOTCH_THETA0, NOTCH_THETA1)
shell = shell.cut(notch_cutter)
check(shell, "shell (latch notch cut)")

# --- 4. hinge recess (shell side, forward of the opening) + screws ---
print("[4] hinge recess (shell)")
z_hinge_shell = Z_DOOR0 - HINGE_L / 2.0
hinge_pocket = wedge(R - HINGE_DEPTH, R + 0.5, z_hinge_shell - HINGE_L / 2.0, z_hinge_shell + HINGE_L / 2.0,
                      -THETA_HINGE_HALF, THETA_HINGE_HALF)
shell = shell.cut(hinge_pocket)
h1 = local_cyl_through(0.0, z_hinge_shell, R, HINGE_HOLE_D, 20.0)
h1.translate(local_placement(0.0, z_hinge_shell, R).multVec(Vector(-HINGE_HOLE_X, 0, 0))
             - local_placement(0.0, z_hinge_shell, R).Base)
h2 = local_cyl_through(0.0, z_hinge_shell, R, HINGE_HOLE_D, 20.0)
h2.translate(local_placement(0.0, z_hinge_shell, R).multVec(Vector(HINGE_HOLE_X, 0, 0))
             - local_placement(0.0, z_hinge_shell, R).Base)
shell = shell.cut(h1).cut(h2)
check(shell, "shell (hinge screw holes)")

# --- 5. servo pad + backstop + mounting holes ---
print("[5] servo pad + backstop")
pad = local_box(THETA_SERVO, Z_SERVO_C, R - OVERLAP, PAD_TAN, PAD_AX, PAD_PROUD + OVERLAP, outward=True)
shell = shell.fuse(pad)
p1 = local_cyl_through(THETA_SERVO, Z_SERVO_C, R, PAD_HOLE_D, 20.0)
p1.translate(local_placement(THETA_SERVO, Z_SERVO_C, R).multVec(Vector(0, -PAD_HOLE_AX, 0))
             - local_placement(THETA_SERVO, Z_SERVO_C, R).Base)
p2 = local_cyl_through(THETA_SERVO, Z_SERVO_C, R, PAD_HOLE_D, 20.0)
p2.translate(local_placement(THETA_SERVO, Z_SERVO_C, R).multVec(Vector(0, PAD_HOLE_AX, 0))
             - local_placement(THETA_SERVO, Z_SERVO_C, R).Base)
shell = shell.cut(p1).cut(p2)
check(shell, "shell (servo pad + holes)")

backstop = local_box(THETA_BACKSTOP, Z_BACKSTOP, R - OVERLAP, BACKSTOP_W, BACKSTOP_L, BACKSTOP_H + OVERLAP, outward=True)
shell = shell.fuse(backstop)
check(shell, "shell (backstop)")

# --- 6. bulkhead eyebolt hole + counterbores ---
print("[6] eyebolt hole")
eyebolt = Part.makeCylinder(EYEBOLT_HOLE_D / 2.0, Z_BULK1 - Z_BULK0 + 2.0, Vector(0, 0, Z_BULK0 - 1.0))
cb_fwd = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK0 - 0.25))
cb_aft = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK1 - EYEBOLT_CB_DEPTH + 0.25))
shell = shell.cut(eyebolt).cut(cb_fwd).cut(cb_aft)
check(shell, "shell (eyebolt)")

# --- 7. shoulder retention screws (positive mechanical retention, not friction alone) ---
print("[7] shoulder retention screws x%d" % N_RET_SCREWS)
for i in range(N_RET_SCREWS):
    th = 360.0 * i / N_RET_SCREWS
    hole = local_cyl_through(th, Z_RET_SCREW, R_SH, RET_SCREW_D, 20.0)
    shell = shell.cut(hole)
check(shell, "shell (retention screws)")

shell = shell.removeSplitter()
check(shell, "shell (final, splitter removed)")

# ===================================================================== DOOR

print("[8] door part")
door_outer = wedge(R_BAY_IN, R, Z_DOOR0 + CLEAR, Z_DOOR1 - CLEAR,
                    -THETA_DOOR + 0.9, THETA_DOOR - 0.9)   # ~0.9deg ~= CLEAR at r=21.5 on each side
door = door_outer

# door-side hinge recess (mirrored, at the door's own forward edge)
z_hinge_door = Z_DOOR0 + CLEAR + HINGE_L / 2.0
hpock2 = wedge(R - HINGE_DEPTH, R + 0.5, z_hinge_door - HINGE_L / 2.0, z_hinge_door + HINGE_L / 2.0,
               -THETA_HINGE_HALF, THETA_HINGE_HALF)
door = door.cut(hpock2)
dh1 = local_cyl_through(0.0, z_hinge_door, R, HINGE_HOLE_D, 20.0)
dh1.translate(local_placement(0.0, z_hinge_door, R).multVec(Vector(-HINGE_HOLE_X, 0, 0))
              - local_placement(0.0, z_hinge_door, R).Base)
dh2 = local_cyl_through(0.0, z_hinge_door, R, HINGE_HOLE_D, 20.0)
dh2.translate(local_placement(0.0, z_hinge_door, R).multVec(Vector(HINGE_HOLE_X, 0, 0))
              - local_placement(0.0, z_hinge_door, R).Base)
door = door.cut(dh1).cut(dh2)
check(door, "door (hinge recess)")

# latch tab + peg, aft-outer corner. Tab overlaps the door's own aft edge (not
# just touches it -- see OVERLAP note above), and the peg overlaps into the tab.
tab_z0 = Z_TAB0 - OVERLAP
tab_block = local_box(THETA_TAB, (tab_z0 + Z_TAB1) / 2.0, R_BAY_IN, TAB_W, Z_TAB1 - tab_z0,
                       R - R_BAY_IN, outward=True)
peg = local_cyl_proud(THETA_TAB, (Z_TAB0 + Z_TAB1) / 2.0, R - OVERLAP, PEG_D, PEG_LEN + OVERLAP)
door = door.fuse(tab_block).fuse(peg)
door = door.removeSplitter()
check(door, "door (tab + peg, final)")

# ================================================================== LATCHARM

print("[9] latch arm")
# Built from primitives, not a loft: a loft between two rectangle wires at
# thetas 31 deg apart twisted into a near-self-cancelling (-72.6 mm^3) solid --
# same overlap-vs-touch class of problem as the fuse joints elsewhere, but a
# loft can silently produce a *wrong-shaped* valid solid rather than an
# invalid one, so isValid()/Volume must both be sanity-checked, not just isValid().
THETA_PADDLE = THETA_BACKSTOP - 6.0


def frame_point(theta_deg, z, r):
    th = math.radians(theta_deg)
    return Vector(r * math.cos(th), r * math.sin(th), z)


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


hub_pt = frame_point(THETA_SERVO, Z_SERVO_C, R + PAD_PROUD)
paddle_pt = frame_point(THETA_PADDLE, Z_BACKSTOP, PADDLE_R)
mid = (hub_pt + paddle_pt) * 0.5
y_dir = paddle_pt - hub_pt
reach = y_dir.Length
n_avg = (Vector(math.cos(math.radians(THETA_SERVO)), math.sin(math.radians(THETA_SERVO)), 0)
         + Vector(math.cos(math.radians(THETA_PADDLE)), math.sin(math.radians(THETA_PADDLE)), 0))

arm_body = oriented_box(mid, y_dir, n_avg, reach + 2.0 * OVERLAP, PADDLE_TAN * 0.5, 2.5)
hub_cyl = local_cyl_proud(THETA_SERVO, Z_SERVO_C, R + PAD_PROUD - OVERLAP, HUB_D, HUB_H + OVERLAP)
paddle_box = local_box(THETA_PADDLE, Z_BACKSTOP, PADDLE_R - OVERLAP, PADDLE_TAN, PADDLE_AX, 2.5 + OVERLAP)

latch_arm = arm_body.fuse(hub_cyl).fuse(paddle_box)
pilot = local_cyl_through(THETA_SERVO, Z_SERVO_C, R + PAD_PROUD, HUB_PILOT_D, 20.0)
latch_arm = latch_arm.cut(pilot)
latch_arm = latch_arm.removeSplitter()
check(latch_arm, "latch_arm (final)")
expected_min_vol = reach * PADDLE_TAN * 0.5 * 2.0   # crude lower bound, sanity check only
if latch_arm.Volume < expected_min_vol:
    raise RuntimeError("latch_arm volume %.1f suspiciously small (expected >~%.0f) -- geometry likely twisted/self-intersecting"
                        % (latch_arm.Volume, expected_min_vol))

# ============================================================ SWING CLEARANCE

print("[9.5] door-swing clearance check (peg vs fixed backstop)")
# The door is a rigid body hinged along one line (the flex strip, centred at
# theta=0, Z=Z_DOOR0) -- ALL points on the door rotate about that one axis,
# not about their own local tangential axis. The peg is ~67 mm from the hinge
# (the door's own length), so even a modest opening angle sweeps it through a
# large arc. Rotate the peg tip about the true hinge axis and check it clears
# the fixed backstop boss (which cannot move -- only the peg/tab do).
hinge_axis_pt = Vector(R, 0.0, Z_DOOR0)   # axis is parallel to global Y through here


def rotate_about_hinge(pt, phi_deg):
    dx = pt.x - hinge_axis_pt.x
    dz = pt.z - hinge_axis_pt.z
    phi = math.radians(phi_deg)
    dx2 = dx * math.cos(phi) + dz * math.sin(phi)
    dz2 = -dx * math.sin(phi) + dz * math.cos(phi)
    return Vector(hinge_axis_pt.x + dx2, pt.y, hinge_axis_pt.z + dz2)


peg_tip_closed = frame_point(THETA_TAB, (Z_TAB0 + Z_TAB1) / 2.0, R + PEG_LEN)
backstop_pt = frame_point(THETA_BACKSTOP, Z_BACKSTOP, R + BACKSTOP_H / 2.0)
backstop_reach = max(BACKSTOP_W, BACKSTOP_L, BACKSTOP_H)   # crude bounding radius

r0 = math.hypot(peg_tip_closed.x, peg_tip_closed.y)
found_opening = False
for sign in (1.0, -1.0):
    p20 = rotate_about_hinge(peg_tip_closed, sign * 20.0)
    if math.hypot(p20.x, p20.y) > r0:
        found_opening = True
        break
if not found_opening:
    sign = 1.0
    print("  WARNING: neither rotation sign increases radial distance at 20 deg -- sign convention unclear, checking both")

for phi in (0.0, 20.0, 45.0, 70.0):
    p = rotate_about_hinge(peg_tip_closed, sign * phi)
    d = (p - backstop_pt).Length
    clear = d - backstop_reach
    flag = "OK" if clear > 2.0 else ("TIGHT" if clear > 0 else "COLLISION RISK")
    print("  phi=%5.1f deg  peg=(%.1f,%.1f,%.1f)  dist-to-backstop=%.1f mm  margin=%.1f mm  [%s]"
          % (phi, p.x, p.y, p.z, d, clear, flag))

# ======================================================================= I/O

def export(shape, name):
    step_path = os.path.join(MODELS, "PhoenixABS40-43_nose_%s_%s.step" % (name, REV))
    stl_path = os.path.join(MODELS, "PhoenixABS40-43_nose_%s_%s.stl" % (name, REV))
    shape.exportStep(step_path)
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.4)
    mesh.write(stl_path)
    print("  wrote %s  (%.1f g @ 100%% infill)" % (name, shape.Volume * RHO_ABS))
    return step_path, stl_path

print("[10] export")
export(shell, "Shell")
export(door, "Door")
export(latch_arm, "LatchArm")

doc.recompute()
fcstd_path = os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_v1.FCStd")
o1 = doc.addObject("Part::Feature", "Shell")
o1.Shape = shell
o2 = doc.addObject("Part::Feature", "Door")
o2.Shape = door
o3 = doc.addObject("Part::Feature", "LatchArm")
o3.Shape = latch_arm
doc.recompute()
doc.saveAs(fcstd_path)
print("saved %s" % fcstd_path)

print("=== DONE ===")
print("Total nosecone length: %.1f mm  (ogive %.0f + bay %.0f + taper %.0f + shoulder %.0f)"
      % (Z_SH1, L_OGV, Z_BAY1 - Z_BAY0, Z_SH_TAPER1 - Z_SH_TAPER0, Z_SH1 - Z_SH0))

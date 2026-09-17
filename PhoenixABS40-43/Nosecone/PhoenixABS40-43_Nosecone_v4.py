# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- bow-door nosecone, narrow keel, no hinge, snap+servo, v4

SOURCE OF TRUTH. Every dimension is a named constant below; edit here and
re-run, never edit the STL/STEP/FCStd by hand. Supersedes
PhoenixABS40-43_Nosecone_v3.py (kept for history, not deleted).

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

v4 feedback driving this revision (2026-09-15, same session as v2/v3):
  "I want the tip of the nose to be included in the door too. And I'd
  rather ditch the hinges and just make it click in place etc. Think
  fairing combined with a bow door on a ship, almost the entire mouth/tip
  opens." Then, clarifying mid-build: "A bow on a ship still has a part of
  the 'lip' left right? Even though the 'mouth' is open the 'bottom lip'
  remains?? I want something like that."

That last message is the key architectural fact and is what this revision
is actually built around: a real ship bow door isn't a full end-cap that
pops off whole -- there's a fixed keel/sill strip at the bottom, and the
door is everything else, hinged or (here) fully detachable. Two earlier
in-session attempts at this got corrected along the way; worth recording
why, since the reasoning is easy to re-derive wrong:

  ATTEMPT 1 (abandoned): a single Z-plane cut near the bulkhead, door =
  the entire forward cone as ONE full-360-degree cap, spine = a short aft
  collar. This does NOT match "keep the bottom lip" -- it has no fixed
  strip at all, the whole tip is unsupported once unlatched. It also
  needed an entirely new axial-withdrawal latch (peg/gate blocking a pull
  along the tube axis instead of v2/v3's tangential swing-block), and that
  latch had a real bug: the gate can only resist tangential rotation about
  its own hub, not translate, so blocking axial pull requires something
  solid specifically in the direction the gate would get cammed open under
  that load -- and getting the cam direction right by hand, for a new
  mechanism, without being able to bench-test it, is exactly the kind of
  mistake that fails silently (nose cone departs under boost, not on
  command). Reverting to a theta-based split sidesteps this: it lets v4
  reuse v2/v3's tangential peg/gate/backstop latch UNCHANGED and already
  verified, rather than inventing a new one.

  THIS REVISION (v4): a KEEL -- a narrow (70 deg) fixed strip, constant
  width, running the tube's full length from Z=15 (just aft of the fragile
  point of the tip) through the bulkhead -- stays Spine, bonded to the
  airframe, same as v2/v3's Spine always has been. The DOOR is everything
  else: 290 deg of arc, Z 0 (the true tip) to 178 (short of the bulkhead),
  ONE piece, no hinge, held on by a servo latch (v2/v3's proven mechanism,
  just repositioned) plus a row of light snap-click points along BOTH
  seams (there being no hinge to hold one side anymore). Released, it
  detaches completely -- tethered only by the shock cord, same as a
  traditional full nose-cone-separation recovery system.

Everything NOT called out above (outer profile, cavity, bulkhead, shoulder,
retention screws, eyebolt, the servo's real SG90 envelope and through-wall
mount style, the door-side shock-cord anchor) is unchanged in principle
from v2/v3 -- see NOSECONE_DESIGN.md.
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
REV = "v4"

RHO_ABS = 1.05e-3

# --- airframe (DESIGN.md Sec2/Sec8) ---
R_AF_O = 21.5
R_AF_I = 20.0

# --- outer profile stations (unchanged from v2/v3) ---
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


OVERLAP = 0.5   # moved up from the bottom of the param block -- v4.4's LATCH params need it earlier

# --- KEEL / DOOR split (see docstring for why theta-based, not a Z-plane cap) ---
# v4.4: tip ownership INVERTED from the original v4 design -- the true tip
# (Z<Z_DOOR_START) now belongs to the KEEL, not the Door, matching "the
# nose point should be with the keel, not the door" (the keel is also
# widened further, more keel / less door). Keel is CENTRED on theta=0,
# constant width, and now automatically owns the FULL circle for
# Z<Z_DOOR_START (no cut removes it there -- same trick already used at
# the aft/bulkhead end) through the bulkhead. Door is the remaining arc,
# Z_DOOR_START to Z_DOOR_END only -- it no longer reaches the tip at all.
KEEL_HALFW = 100.0          # deg -- 200deg total keel width (widened again: 70->105->158->200)
Z_DOOR_START = 25.0         # was Z_KEEL_START=15 in v4 -- raised, and its role inverted (keel now OWNS <this, not door)
Z_DOOR_END = 178.0
GAP_DEG = 1.0               # angular clearance, door side shrunk (v2/v3 convention)

KEEL_THETA0, KEEL_THETA1 = -KEEL_HALFW, KEEL_HALFW

# --- snap-click points along BOTH seams (replaces the hinge -- there's no
# captured side anymore, so both edges need light retention). Deliberately
# weak/assembly-oriented -- NOT the flight load path, see LATCH below. ---
SNAP_Z_LIST = [30.0, 60.0, 90.0, 120.0, 165.0]   # skips Z=150 (latch/servo cluster)
SNAP_AX_HALFLEN = 4.0        # mm, half-length of each snap feature
SNAP_ANGW = 8.0              # deg, angular width of each snap bump/pocket
SNAP_DEPTH = 0.6             # mm, bump proud height / pocket depth

# --- LATCH v4.4: complete mechanism change, driven by two linked requests
# -- (1) "bulk of the servo inside, only the tip pokes out through a 4mm D
# hole" and (3) "spring should try to open the door, servo should stop it
# -- pin and socket, openable only from the bottom, like a battery door."
# Read together these describe ONE mechanism, not two: a door captured at
# its FORE end (fixed pins in sockets, near the tip -- see FORE CAPTURE
# below) and released at its AFT end only (the servo latch here), exactly
# like a battery door's hooked tab at one edge + a spring-loaded catch at
# the other. This is NOT the flexure hinge the user earlier asked to
# ditch (v2/v3 ran a load-bearing strip the length of the whole seam) --
# it's 2 discrete captured pins at one end, unrelated to how the aft latch
# works, and the door still fully separates once both ends release.
#
# v4.2's hub sat PROUD of the OD (R+1, a visible 16mm external bump) --
# fixed here by moving the hub INBOARD, just inside the wall, so only a
# small pin (shaft D=4mm, matching the request) pokes out through the
# wall. But the pin can no longer be a simple radial peg in a radial hole:
# the spring's escape load is now RADIAL (outward), and a radial pin in a
# radial hole offers ZERO resistance to a radial pull (the lug just slides
# straight off the pin's own axis, like a cup off a peg -- verified by
# inspection, this is why v4.2's pin/lug geometry, correct for an AXIAL
# escape load, cannot be reused unmodified for a RADIAL one). Fixed with a
# keyhole/mushroom capture: the pin's tip has a wider HEAD; the lug's
# blind socket necks down to a narrower MOUTH right at its opening, so the
# head is trapped behind the neck and can't pull straight back out --
# same principle as a tripod quick-release plate or a captive panel
# fastener, not a new invention. Release is still a small SERVO ROTATION
# (same convention as v4.2 -- this model is a closed-position snapshot,
# not a swept-motion simulation) sweeping the whole shaft+head assembly
# tangentially clear of the lug's socket, not a straight radial withdrawal.
#
# Torque check: v4.2's "zero torque, no backstop" proof was specific to a
# PURELY AXIAL escape force (tau_z = r_x*F_y - r_y*F_x depends only on
# F's X/Y components, which are exactly zero for a purely-Z force --
# that's why it was zero for ANY pin offset). A RADIAL escape force has
# nonzero X/Y components, so that proof does NOT carry over -- verified
# numerically at [9.5b], and it comes out nonzero. So THIS mechanism needs
# a backstop again, same reason v2/v3's radial-shaft mechanism did -- see
# BACKSTOP below. Being honest about what's still a simplification: (a)
# the wall's pass-through hole can't be a perfect circle -- the pin sweeps
# a small tangential arc as the hub rotates, so it's actually a short slot
# a bit wider than 4mm, not a literal 4mm circle; (b) the backstop is
# sized by inspection/sign-check, not a proof of adequate strength.
Z_LATCH = 150.0                                # engagement Z -- hub, pin, and the door's lug all sit here
PIN_THETA = KEEL_THETA1 + GAP_DEG + 5.0        # on Door (in the lug), a few deg in from the shrunk edge
SERVO_THETA = KEEL_THETA1 - 10.0               # shaft position, close in now the hub is small/inboard

HUB_R = R_BAY_IN + 0.5      # 18.5 -- just inside the inner wall surface, INBOARD (was R+1, proud/external, in v4.2/4.3)
HUB_D = 13.0                 # big enough its own edge still reaches PIN_THETA at this smaller radius
HUB_H = 2.5
HUB_PILOT_D = 1.2

PIN_SHAFT_D = 4.0            # through-wall pin diameter -- matches "a 4mm D hole" directly
NECK_DEPTH = 2.0             # mm, lug socket's entry neck (matches PIN_SHAFT_D -- traps the head behind it)
POCKET_DEPTH = 3.0           # mm, lug socket's inner pocket (matches PIN_HEAD_D -- houses the captured head)
PIN_HEAD_D = 7.0             # captured head diameter, sits in the lug's pocket, outside the skin
PIN_SHAFT_LEN = (R - HUB_R) + NECK_DEPTH + OVERLAP   # hub -> through the wall -> to the neck's far end
PIN_HEAD_LEN = POCKET_DEPTH + OVERLAP

LUG_W, LUG_AX = 9.0, 9.0
LUG_PROUD = NECK_DEPTH + POCKET_DEPTH + 1.0   # boss deep enough to house the full neck+pocket socket

# --- BACKSTOP: reacts the radial-load torque on the shaft (see above --
# unlike v4.2's axial-only case, this is NOT zero). A fixed boss on the
# Keel, positioned on the side the radial-load torque drives the hub
# toward, blocking that rotation without blocking the servo's own
# opposite-direction release sweep -- same concept as v2/v3/v4.1's
# peg/gate/backstop, reused here for the same underlying reason (a
# transverse-to-the-shaft load couples into torque). Sign verified at
# [9.5b], not just assumed -- flip BACKSTOP_SIDE if the build shows it's
# on the wrong side of the hub.
BACKSTOP_SIDE = -1.0         # -1: backstop sits on the (SERVO_THETA - offset) side of the hub; +1 the other way
BACKSTOP_OFFSET = 8.0        # deg, from SERVO_THETA
BACKSTOP_W, BACKSTOP_AX, BACKSTOP_PROUD = 4.0, 6.0, 2.0

# --- FORE CAPTURE: the door's OTHER end -- fixed pins/sockets near the
# tip (NOT servo-driven, NOT the light assembly-only snap-clicks below --
# a real load-bearing retention feature reacting the spring's push, see
# EJECTION SPRING). "Battery door" made literal: door is captured here,
# released only at the aft latch, i.e. openable from the bottom only when
# the rocket stands nose-up (aft = toward the ground). Same gap-bridging
# wedge technique as the snap-clicks, deeper engagement. ---
Z_FORE_CAP = Z_DOOR_START + 10.0
CAP_AX_HALFLEN = 5.0
CAP_ANGW = 10.0
CAP_DEPTH = 1.2

# --- SERVO: real SG90 envelope (Avionics/avionics_bay_packing_40mm.md /
# DESIGN.md Sec7.5.2: 23x12.4x22.7mm body, 32.2mm tab-to-tab, 9g). Mounted
# with its shaft AXIAL now (see LATCH above) -- the case's SHAFT-NORMAL
# dimension (22.7mm, "height") runs along the tube's axis instead of
# radially, which is what actually enables "no arm": the servo can sit
# right where the pin needs to be instead of reaching across a gap. Side
# benefit: the case's RADIAL reach is now just its WIDTH (12.4mm) not its
# height (22.7mm) -- the original external-blister concern from v3 doesn't
# come up at all in this orientation. ---
SERVO_BODY_L = 23.0
SERVO_BODY_W = 12.4
SERVO_BODY_H = 22.7
SERVO_TAB_SPAN = 32.2
SERVO_OUT_PROUD = 5.0                              # axial: how far the hub sits forward of the flange
SERVO_AXIAL_LEN = SERVO_BODY_H - SERVO_OUT_PROUD   # 17.7, case's axial reach, extending AFT from the flange
SERVO_RADIAL_REACH = SERVO_BODY_W                  # 12.4, case's inward reach (was 22.7 when shaft was radial)
SERVO_TAN_W = SERVO_BODY_L + 3.0                   # 26, tangential footprint
SERVO_CLR = 0.4
FLANGE_Z = Z_LATCH + SERVO_OUT_PROUD               # flange sits this far aft of the hub
PAD_HOLE_D = 2.2
PAD_HOLE_THETA = 6.0         # approximate tab-hole spacing as a angular offset -- bench-verify vs actual unit
# NOTE: must keep SERVO_THETA +/- PAD_HOLE_THETA inside (KEEL_THETA0, KEEL_THETA1) --
# otherwise the mounting boss lands in Door territory, where the Keel has no material to fuse to

# --- SERVO MOUNT v4.5: the case's flange moved from the OD (R) to the
# INNER wall surface (R_BAY_IN) -- since v4.2, mounting the flange AT R
# meant cutting a port clean through the wall for the case to sit in (a
# ~26x18.5mm rectangular hole, visible in every render since -- the v4.3
# "gouge" bugfix only corrected that cut's DEPTH by 1mm, it never removed
# the port itself, which is why the hole was still there after that fix).
# The bay cavity (r<R_BAY_IN) is already fully hollow (step [2]) -- the
# servo's 12.4mm radial reach fits entirely inside R_BAY_IN=18mm with
# room to spare, so mounting the flange there means the case occupies
# space that's already open. No wall material needs removing for the
# case at all; only small blind-hole screw bosses (not a rectangular
# cutout) anchor it, and they don't reach the OD.
SERVO_MOUNT_R = R_BAY_IN - SERVO_CLR                # 17.6 -- case's flange face, INBOARD now (was R=21.5)
MOUNT_BOSS_D = 5.0
MOUNT_BOSS_REACH = 2.0                              # mm, boss extends this far inward from the inner wall face
MOUNT_HOLE_DEPTH = 3.0                              # mm, blind pilot hole for a self-tapping screw -- stops short of the OD

# --- EJECTION SPRING v4.4: REORIENTED per explicit request -- "I want the
# spring to press against the thing from an 'upward' perspective, it
# should try to open the door and the servo should stop it." v4.3's spring
# pushed the Door AXIALLY forward (see history below); this pushes it
# OPEN instead. One real geometric constraint shapes how "open" is
# realized: Keel and Door are theta-adjacent pieces of the SAME shell,
# at the SAME radius -- they are not stacked, so a literally RADIAL
# spring has no second surface at a different radius to react against.
# What IS buildable, and mechanically equivalent to "pushes the door
# open": a spring compressed TANGENTIALLY in the seam gap, near the aft
# latch, pushing the Door's edge away from the Keel's edge
# circumferentially. With the Door's fore end captured (see FORE CAPTURE)
# acting as the effective pivot, a tangential push at the free aft edge
# is exactly the force that kicks that edge RADIALLY outward -- the same
# "pop open" action the battery-door mechanism describes, just reacted
# through the geometry that actually exists here instead of an
# unbuildable literal radial spring between co-radius parts. Relocated
# from Z=105 to near the latch cluster (offset clear of its features) so
# it reacts directly against the same joint the servo pin is holding.
# Not modeled as an actual coil (same convention as the servo/screws/
# cord); this is just the pocket that locates and houses it -- bench-
# select the actual spring once the release force needed is known.
Z_SPRING = Z_LATCH - 20.0            # 130 -- near the latch cluster, clear of its features
SPRING_R = R_BAY_IN - 0.25           # 17.75, inboard of the OD -- avoids ANOTHER port-style skin gouge
SPRING_D = 4.0
SPRING_CLR = 0.4
SPRING_FREE_ANG = 12.0               # deg -- pocket's angular depth (free length), Keel-fixed end
SPRING_COMPRESSED_ANG = 7.0          # deg -- Door pusher tab's rest position (assembled/latched state, 5deg of travel)
# Pocket spans KEEL_THETA1 (open end, at the seam) back to KEEL_THETA1 -
# SPRING_FREE_ANG (closed end, fixed to Keel). Compressed to 7deg means
# the Door's pusher tab's contact face sits 7deg back from the seam -- NOT
# at the pocket's open end -- see build step [8.5] for why (mirrors
# v4.3's axial version, just with theta as the long axis instead of Z).

# --- bulkhead / shock-cord PRIMARY anchor -- unchanged from v2/v3 ---
EYEBOLT_HOLE_D = 4.5
EYEBOLT_CB_D = 10.0
EYEBOLT_CB_DEPTH = 2.0

# --- shock cord anchor on the Door: a real tie-off loop, not just a
# routing clip -- with no hinge, the cord is the ONLY thing keeping the
# departed door connected to the rest of the rocket. Still a snap-CLOSE
# printed feature per the original "click it in place" ask. Positioned
# opposite the latch cluster, on the door, near the aft (open) edge. ---
CORD_D = 6.0
Z_ANCHOR = 165.0
ANCHOR_THETA = 180.0
ANCHOR_BOSS_W = 14.0
ANCHOR_BOSS_AX = 12.0
ANCHOR_BOSS_REACH = 6.0
ANCHOR_HOLE_D = CORD_D + 1.5
ANCHOR_CLOSURE_GAP = CORD_D * 0.55

# --- shoulder positive retention -- unchanged ---
N_RET_SCREWS = 3
Z_RET_SCREW = (Z_SH0 + Z_SH1) / 2.0
RET_SCREW_D = 3.4

# =================================================================== helpers


def local_placement(theta_deg, z, r):
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
    c = Part.makeCylinder(dia / 2.0, length, Vector(0, -length / 2.0, 0), Vector(0, 1, 0))
    c.Placement = local_placement(theta_deg, z, r)
    return c


def frame_point(theta_deg, z, r):
    th = math.radians(theta_deg)
    return Vector(r * math.cos(th), r * math.sin(th), z)


def wedge(r_in, r_out, z0, z1, theta0_deg, theta1_deg):
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

print("=== Phoenix ABS 40-43 Nosecone %s (keel + bow-door) ===" % REV)
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRINTS, exist_ok=True)

doc = App.newDocument("PhoenixABS40-43_Nosecone_v4")

# --- 1. outer blank (unchanged) ---
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

# --- 3. bulkhead eyebolt hole (unchanged, must precede split) ---
print("[3] eyebolt hole")
eyebolt = Part.makeCylinder(EYEBOLT_HOLE_D / 2.0, Z_BULK1 - Z_BULK0 + 2.0, Vector(0, 0, Z_BULK0 - 1.0))
cb_fwd = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK0 - 0.25))
cb_aft = Part.makeCylinder(EYEBOLT_CB_D / 2.0, EYEBOLT_CB_DEPTH + 0.5, Vector(0, 0, Z_BULK1 - EYEBOLT_CB_DEPTH + 0.25))
full_shell = full_shell.cut(eyebolt).cut(cb_fwd).cut(cb_aft)
check(full_shell, "full_shell (eyebolt)")

# --- 4. shoulder retention screws (unchanged) ---
print("[4] shoulder retention screws x%d" % N_RET_SCREWS)
for i in range(N_RET_SCREWS):
    th = 360.0 * i / N_RET_SCREWS
    hole = local_cyl_through(th, Z_RET_SCREW, R_SH, RET_SCREW_D, 20.0)
    full_shell = full_shell.cut(hole)
check(full_shell, "full_shell (retention screws)")

# --- 5. keel/door split -- v4.4: tip ownership inverted, keel now keeps
# the FULL circle for Z<Z_DOOR_START automatically (no cut removes it),
# same trick already used at the aft/bulkhead end for Z>Z_DOOR_END. Door
# gets an explicit new cut stripping the tip away instead. ---
print("[5] keel/door split (keel %.0fdeg wide, owns tip Z<%.0f + bulkhead; door Z %.0f-%.0f)"
      % (2.0 * KEEL_HALFW, Z_DOOR_START, Z_DOOR_START, Z_DOOR_END))
spine = full_shell.cut(wedge(0.0, R + 5.0, Z_DOOR_START, Z_DOOR_END, KEEL_THETA1, KEEL_THETA0 + 360.0))
check(spine, "spine (before latch/servo/snap features)")

door = full_shell.cut(wedge(0.0, R + 5.0, Z_DOOR_START, Z_BULK0,
                             KEEL_THETA0 - GAP_DEG, KEEL_THETA1 + GAP_DEG))
door = door.cut(wedge(0.0, R + 5.0, Z_DOOR_END, Z_SH1 + 2.0, 0.0, 360.0))
door = door.cut(wedge(0.0, R + 5.0, 0.0, Z_DOOR_START, 0.0, 360.0))
check(door, "door (before latch/servo/snap features)")

# --- 6. snap-click points along BOTH seams (replaces the hinge) ---
print("[6] snap-click points x%d per seam x 2 seams" % len(SNAP_Z_LIST))
for sz in SNAP_Z_LIST:
    r_local = true_outer_r(sz)   # ogive radius != R for Z < L_OGV -- see v3's known open item 3
    for edge_theta, sign in ((KEEL_THETA0, -1.0), (KEEL_THETA1, 1.0)):
        # pocket cuts INTO the Keel's own territory (back from its edge),
        # not past it -- past the edge is already-removed Door territory,
        # which is why the first attempt at this cut zero material (caught
        # by comparing spine's volume before/after in the build log).
        pocket_t0 = edge_theta - sign * SNAP_ANGW
        pocket_t1 = edge_theta
        pocket = wedge(r_local - SNAP_DEPTH, r_local + 0.5, sz - SNAP_AX_HALFLEN, sz + SNAP_AX_HALFLEN,
                        min(pocket_t0, pocket_t1), max(pocket_t0, pocket_t1))
        spine = spine.cut(pocket)
        # bump bridges from the Door's own edge (across the GAP_DEG gap)
        # into that same Keel pocket territory
        bump_t0 = edge_theta - sign * SNAP_ANGW
        bump_t1 = edge_theta + sign * GAP_DEG
        bump = wedge(r_local - OVERLAP, r_local + SNAP_DEPTH, sz - SNAP_AX_HALFLEN, sz + SNAP_AX_HALFLEN,
                     min(bump_t0, bump_t1), max(bump_t0, bump_t1))
        door = door.fuse(bump)
door = door.removeSplitter()
spine = spine.removeSplitter()
check(spine, "spine (snap pockets)")
check(door, "door (+snap bumps)")

# --- 6.5. FORE CAPTURE: fixed, load-bearing pins/sockets near the tip
# (see param block) -- the door's captured end. Same gap-bridging wedge
# technique as the snap-clicks above (deeper engagement, own step so it
# reads as structural, not assembly-only). ---
print("[6.5] fore capture (fixed pins/sockets near the tip -- the door's captured end)")
r_cap = true_outer_r(Z_FORE_CAP)
for edge_theta, sign in ((KEEL_THETA0, -1.0), (KEEL_THETA1, 1.0)):
    cap_pocket_t0 = edge_theta - sign * CAP_ANGW
    cap_pocket_t1 = edge_theta
    cap_pocket = wedge(r_cap - CAP_DEPTH, r_cap + 0.5, Z_FORE_CAP - CAP_AX_HALFLEN, Z_FORE_CAP + CAP_AX_HALFLEN,
                        min(cap_pocket_t0, cap_pocket_t1), max(cap_pocket_t0, cap_pocket_t1))
    spine = spine.cut(cap_pocket)
    cap_bump_t0 = edge_theta - sign * CAP_ANGW
    cap_bump_t1 = edge_theta + sign * GAP_DEG
    cap_bump = wedge(r_cap - OVERLAP, r_cap + CAP_DEPTH, Z_FORE_CAP - CAP_AX_HALFLEN, Z_FORE_CAP + CAP_AX_HALFLEN,
                      min(cap_bump_t0, cap_bump_t1), max(cap_bump_t0, cap_bump_t1))
    door = door.fuse(cap_bump)
door = door.removeSplitter()
spine = spine.removeSplitter()
check(spine, "spine (fore capture pockets)")
check(door, "door (+fore capture pins)")

# --- 7. latch lug on Door: a keyhole socket, not a simple blind hole --
# see LATCH param block for why (a radial escape force pulls a lug straight
# off a simple radial pin, zero resistance). Neck (matches PIN_SHAFT_D)
# right at the mouth, wider pocket (matches PIN_HEAD_D) behind it -- the
# head can't pull back out through the neck. Both cut as a single fused
# void (two coaxial cylinders at different radii along the pin's own
# axis), not two independent cuts. ---
print("[7] latch lug (keyhole socket: neck + pocket, traps the pin's head)")
lug_boss = local_box(PIN_THETA, Z_LATCH, R - OVERLAP, LUG_W, LUG_AX, LUG_PROUD + OVERLAP, outward=True)
lug_neck_void = local_cyl_proud(PIN_THETA, Z_LATCH, R - OVERLAP,
                                 PIN_SHAFT_D + 2.0 * OVERLAP, NECK_DEPTH + OVERLAP)
lug_pocket_void = local_cyl_proud(PIN_THETA, Z_LATCH, R - OVERLAP + NECK_DEPTH,
                                   PIN_HEAD_D + 2.0 * OVERLAP, POCKET_DEPTH + OVERLAP)
lug_socket_void = lug_neck_void.fuse(lug_pocket_void)
lug = lug_boss.cut(lug_socket_void)
door = door.fuse(lug)
door = door.removeSplitter()
check(door, "door (+latch lug, final)")

# --- 7b. servo mount v4.5, shaft AXIAL, flange INBOARD (see SERVO MOUNT
# param block for why -- the old flange-at-the-OD design needed a port cut
# straight through the wall, which is the "giant rectangular hole" seen in
# every render since v4.2; that hole was never actually removed by the
# v4.3 fix, only made 1mm shallower). The bay cavity is already hollow
# here, so the case needs NO cut into the wall at all -- just two small
# blind-hole screw bosses to anchor it, well clear of the OD. ---
print("[7b] servo mount (axial, INBOARD -- no wall port)")
z_case_mid = FLANGE_Z + SERVO_AXIAL_LEN / 2.0
case_inner_r = SERVO_MOUNT_R - SERVO_RADIAL_REACH - SERVO_CLR
if case_inner_r < 1.0:
    raise RuntimeError("servo case (%.1fmm radial reach) doesn't fit inboard of SERVO_MOUNT_R=%.1f -- "
                        "would reach past the tube's centerline" % (SERVO_RADIAL_REACH, SERVO_MOUNT_R))
if SERVO_MOUNT_R + SERVO_CLR > R_BAY_IN + 0.01:
    raise RuntimeError("servo mount radius %.2f reaches past R_BAY_IN=%.2f -- would cut into the wall, "
                        "defeating the point of mounting it inboard" % (SERVO_MOUNT_R, R_BAY_IN))
print("  case envelope: r=%.1f-%.1f (fits inside the already-open bay, r<%.1f -- no cut needed)"
      % (case_inner_r, SERVO_MOUNT_R + SERVO_CLR, R_BAY_IN))

boss_base_r = R_BAY_IN - MOUNT_BOSS_REACH
mount_boss1 = local_cyl_proud(SERVO_THETA + PAD_HOLE_THETA, FLANGE_Z, boss_base_r, MOUNT_BOSS_D, MOUNT_BOSS_REACH + OVERLAP)
mount_boss2 = local_cyl_proud(SERVO_THETA - PAD_HOLE_THETA, FLANGE_Z, boss_base_r, MOUNT_BOSS_D, MOUNT_BOSS_REACH + OVERLAP)
spine = spine.fuse(mount_boss1).fuse(mount_boss2)
spine = spine.removeSplitter()
check(spine, "spine (+servo mounting bosses)")
if len(spine.Solids) != 1:
    raise RuntimeError("servo mounting boss(es) didn't fuse into the Spine (solids=%d) -- "
                        "SERVO_THETA +/- PAD_HOLE_THETA likely lands outside (KEEL_THETA0, KEEL_THETA1)"
                        % len(spine.Solids))

h1 = local_cyl_proud(SERVO_THETA + PAD_HOLE_THETA, FLANGE_Z, boss_base_r - OVERLAP, PAD_HOLE_D, MOUNT_HOLE_DEPTH)
h2 = local_cyl_proud(SERVO_THETA - PAD_HOLE_THETA, FLANGE_Z, boss_base_r - OVERLAP, PAD_HOLE_D, MOUNT_HOLE_DEPTH)
spine = spine.cut(h1).cut(h2)
spine = spine.removeSplitter()
if boss_base_r - OVERLAP + MOUNT_HOLE_DEPTH > R + 0.01:
    raise RuntimeError("servo mounting pilot hole reaches the OD -- should stay blind, inboard of the skin")
check(spine, "spine (+servo mounting holes, final)")

# ================================================================== SERVO HORN

print("[8] servo horn -- hub (INBOARD now) + shaft + captured head, no separate gate/arm part")
# Renamed from "LatchArm" -- that name was a holdover from v2/v3, where
# this really was a separate arm/gate/backstop assembly. Since v4.2 it's
# just the minimal piece that has to mount on the servo's OWN shaft (every
# servo-driven mechanism needs something there, same role as the stock
# plastic horn that ships with the servo) -- no separate connecting body,
# not that hub and pin are the same point. Hub moved from R+1 (proud,
# external) to HUB_R (just inside the wall) -- see LATCH param block. The
# pin is now two diameters: a slender shaft through the wall
# (PIN_SHAFT_D, matches "a 4mm D hole") and a wider captured head
# (PIN_HEAD_D) that sits in the lug's keyhole pocket.
hub_cyl = local_cyl_axial(SERVO_THETA, Z_LATCH, HUB_R, HUB_D, HUB_H + OVERLAP)
pin_shaft = local_cyl_proud(PIN_THETA, Z_LATCH, HUB_R, PIN_SHAFT_D, PIN_SHAFT_LEN)
pin_head = local_cyl_proud(PIN_THETA, Z_LATCH, R + NECK_DEPTH - OVERLAP, PIN_HEAD_D, PIN_HEAD_LEN)

servo_horn = hub_cyl.fuse(pin_shaft).fuse(pin_head)
pilot = local_cyl_axial(SERVO_THETA, Z_LATCH, HUB_R, HUB_PILOT_D, HUB_H + 4.0)
servo_horn = servo_horn.cut(pilot)
servo_horn = servo_horn.removeSplitter()
check(servo_horn, "servo_horn (final)")
if servo_horn.Volume < 50.0:
    raise RuntimeError("servo_horn volume %.1f suspiciously small -- hub and pin likely didn't fuse "
                        "(check that HUB_D reaches PIN_THETA)" % servo_horn.Volume)

# --- BACKSTOP: fixed to the Keel (spine), NOT the servo horn -- see param
# block for why a radial escape load needs this (unlike v4.2's purely-axial
# case, which needed none). Positioned tangentially adjacent to the hub, on
# the side the radial-load torque would drive it toward -- verified at
# [9.5b] below, not just assumed; the sign is flippable via BACKSTOP_SIDE
# if the build shows it landed on the wrong side. ---
print("[8b] backstop (reacts the radial-load torque on the shaft)")
backstop_theta = SERVO_THETA + BACKSTOP_SIDE * BACKSTOP_OFFSET
backstop = local_box(backstop_theta, Z_LATCH, R - OVERLAP, BACKSTOP_W, BACKSTOP_AX,
                      BACKSTOP_PROUD + OVERLAP, outward=True)
spine = spine.fuse(backstop)
spine = spine.removeSplitter()
check(spine, "spine (+backstop, final)")

# =============================================================== EJECTION SPRING

print("[8.5] ejection spring: pocket on Keel + pusher tab on Door, TANGENTIAL now (see param block)")
# Pocket: bored into the Keel from its own edge (open end at KEEL_THETA1),
# closed end deeper in Keel territory (fixed -- reacts the spring's base).
# Long axis is THETA now (was Z in v4.3) -- see param block for why.
theta_spring_close = KEEL_THETA1 - SPRING_FREE_ANG
spring_pocket = wedge(SPRING_R - SPRING_D / 2.0 - SPRING_CLR, SPRING_R + SPRING_D / 2.0 + SPRING_CLR,
                       Z_SPRING - SPRING_D / 2.0 - SPRING_CLR, Z_SPRING + SPRING_D / 2.0 + SPRING_CLR,
                       theta_spring_close, KEEL_THETA1)
spine = spine.cut(spring_pocket)
spine = spine.removeSplitter()
check(spine, "spine (+spring pocket, final)")

# Pusher tab: on the Door, reaching across GAP_DEG into the pocket's own
# territory (same bridging technique as the snap bumps), its trailing face
# sitting SPRING_COMPRESSED_ANG back from the seam -- where the compressed
# spring's tip currently sits -- with the tab body extending on to the
# Door's own edge, structurally continuous with the Door's shell.
theta_pusher_face = theta_spring_close + SPRING_COMPRESSED_ANG
pusher = wedge(SPRING_R - SPRING_D / 2.0, SPRING_R + SPRING_D / 2.0,
               Z_SPRING - SPRING_D / 2.0, Z_SPRING + SPRING_D / 2.0,
               theta_pusher_face, KEEL_THETA1 + GAP_DEG)
door = door.fuse(pusher)
door = door.removeSplitter()
check(door, "door (+spring pusher tab, final)")
print("  pocket theta %.1f-%.1f (%.0fdeg free); pusher face at theta=%.1f (compressed to %.0fdeg)"
      % (theta_spring_close, KEEL_THETA1, SPRING_FREE_ANG, theta_pusher_face, SPRING_COMPRESSED_ANG))
print("  %.0fdeg of travel stored -- released when the latch lets the Door's aft edge kick outward"
      % (SPRING_FREE_ANG - SPRING_COMPRESSED_ANG))

# ============================================================ SHOCK CORD ANCHOR

print("[9] shock cord anchor on the door (primary tether -- see docstring)")
anchor_boss = local_box(ANCHOR_THETA, Z_ANCHOR, R_BAY_IN - OVERLAP, ANCHOR_BOSS_W, ANCHOR_BOSS_AX,
                         ANCHOR_BOSS_REACH, outward=False)
anchor_bore = local_cyl_axial(ANCHOR_THETA, Z_ANCHOR, R_BAY_IN - ANCHOR_BOSS_REACH * 0.5,
                               ANCHOR_HOLE_D, ANCHOR_BOSS_AX + 2.0)
anchor = anchor_boss.cut(anchor_bore)
closure = local_box(ANCHOR_THETA, Z_ANCHOR, R_BAY_IN - ANCHOR_BOSS_REACH * 0.5,
                     ANCHOR_CLOSURE_GAP, ANCHOR_BOSS_AX + 2.0, ANCHOR_BOSS_REACH, outward=False)
anchor = anchor.cut(closure)
door = door.fuse(anchor)
door = door.removeSplitter()
check(door, "door (+shock cord anchor, final)")

# ================================================================ VERIFICATION

print("[9.5] latch load-path check, AXIAL case (still applies -- handling loads, etc.)")
# v4.2's zero-torque result is a property of a purely-axial force alone
# (tau_z = r_x*F_y - r_y*F_x depends only on F's X/Y components, which are
# exactly zero for pure-Z force, for ANY r) -- still true here regardless
# of where the hub/pin moved to, verified again against the new geometry.
hub_pt = frame_point(SERVO_THETA, Z_LATCH, HUB_R)
pin_tip_pt = frame_point(PIN_THETA, Z_LATCH, R + NECK_DEPTH + PIN_HEAD_LEN)
r_vec = pin_tip_pt - hub_pt
F_axial = Vector(0.0, 0.0, 250.0)   # representative axial test load, N
torque_axial_case = r_vec.x * F_axial.y - r_vec.y * F_axial.x   # (r x F) . z_hat
print("  hub=(%.1f,%.1f,%.1f)  pin tip=(%.1f,%.1f,%.1f)"
      % (hub_pt.x, hub_pt.y, hub_pt.z, pin_tip_pt.x, pin_tip_pt.y, pin_tip_pt.z))
print("  torque about shaft from a %.0fN purely-axial test load: %.6f N*mm (must be ~0)"
      % (F_axial.z, torque_axial_case))
if abs(torque_axial_case) > 1e-6:
    raise RuntimeError("axial-load torque check failed -- should be a trivial vector identity "
                        "(pure-Z force has zero X/Y component) regardless of geometry")

print("[9.5b] latch load-path check, RADIAL case (the spring's actual load now -- v4.4)")
# v4.2's zero-torque result does NOT cover this: the spring's escape force
# is RADIAL now (see EJECTION SPRING), which has nonzero global X/Y
# components, so tau_z is generically nonzero -- that's WHY this revision
# adds BACKSTOP back. Compute the actual torque and its SIGN, and confirm
# the backstop was placed on the side that opposes it (not assumed).
F_mag = 15.0   # N, representative spring force -- small, this is a release-assist spring not a snatch load
F_radial_dir = Vector(math.cos(math.radians(PIN_THETA)), math.sin(math.radians(PIN_THETA)), 0.0)
F_radial = Vector(F_radial_dir.x * F_mag, F_radial_dir.y * F_mag, 0.0)
torque_radial_case = r_vec.x * F_radial.y - r_vec.y * F_radial.x
backstop_theta = SERVO_THETA + BACKSTOP_SIDE * BACKSTOP_OFFSET
backstop_pt = frame_point(backstop_theta, Z_LATCH, R)
# the backstop must sit on the side the hub would rotate TOWARD under this
# torque -- i.e. BACKSTOP_SIDE's sign should match torque_radial_case's sign
# (positive torque = rotation toward +theta, by the standard right-hand
# convention this script's frame uses)
sign_ok = (torque_radial_case > 0.0) == (BACKSTOP_SIDE > 0.0)
print("  torque about shaft from a %.0fN radial test load: %.3f N*mm (nonzero -- expected)"
      % (F_mag, torque_radial_case))
print("  backstop at theta=%.1f (side=%s): %s"
      % (backstop_theta, "+" if BACKSTOP_SIDE > 0 else "-", "correct side" if sign_ok else "WRONG SIDE"))
if not sign_ok:
    raise RuntimeError("backstop is on the WRONG side of the hub for the radial-load torque direction "
                        "-- flip BACKSTOP_SIDE and re-run")
print("  NOTE: sign-check only, not a strength proof -- the backstop's size (%.1fx%.1fx%.1fmm) is"
      % (BACKSTOP_W, BACKSTOP_AX, BACKSTOP_PROUD))
print("  chosen by inspection against a %.0fN release-assist spring, not a margin calculation." % F_mag)

print("[9.6] mouth-open check (what actually detaches)")
door_arc = 360.0 - 2.0 * KEEL_HALFW - 2.0 * GAP_DEG
print("  keel (fixed): %.0f deg, owns the tip (Z<%.0f) + full bulkhead/shoulder ring"
      % (2.0 * KEEL_HALFW, Z_DOOR_START))
print("  door (detaches): %.1f deg (%.0f%% of the circumference), Z %.0f-%.0f (no longer reaches the tip)"
      % (door_arc, 100.0 * door_arc / 360.0, Z_DOOR_START, Z_DOOR_END))

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
export(servo_horn, "ServoHorn")

doc.recompute()
fcstd_path = os.path.join(NOSECONE, "PhoenixABS40-43_Nosecone_v4.FCStd")
o1 = doc.addObject("Part::Feature", "Spine")
o1.Shape = spine
o2 = doc.addObject("Part::Feature", "DoorHalf")
o2.Shape = door
o3 = doc.addObject("Part::Feature", "ServoHorn")
o3.Shape = servo_horn
doc.recompute()
doc.saveAs(fcstd_path)
print("saved %s" % fcstd_path)

print("=== DONE ===")
print("Total nosecone length: %.1f mm" % Z_SH1)

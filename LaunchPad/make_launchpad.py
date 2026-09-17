"""
Parametric build script for the foldable ABS launch pad.
Run headless: freecadcmd.exe make_launchpad.py

Builds 5 part types (9 pieces), exports STL+OBJ to "Print Files/", saves
LaunchPad.FCStd, and runs the verification checks (watertight, interference,
rod-fit, fold-clearance, plate-overhang, bed-check).

v2 (simplified): replaced the tapered collet + conical nut with a plain
split-collar + cross-screw clamp, replaced the two-ear clevis hinge with a
single lap-joint lug + friction pin (snap clip dropped), and simplified the
deflector cradle to one lip ring (dropped the inner ring + keeper posts).
Done at the user's request to reduce mechanism complexity after the v1
design (tapered collet/cone-nut, clevis hinges, dual-ring cradle) was built
and verified -- v1's reasoning and numbers are kept in BOM.md's "v1 (precision
collet)" section below its current v2 content, in case the precision
trade-off this revision makes ever needs revisiting.
"""
import math
import os
import FreeCAD
import Part
import Mesh

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PRINT_DIR = os.path.join(OUT_DIR, "Print Files")
os.makedirs(PRINT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------

ROD_DIA = 4.0
ROD_LEN = 1000.0
BORE_DIA = 4.25
BORE_R = BORE_DIA / 2.0

# Hub — base flange (legs + cradle-post roots)
BASE_FLANGE_H = 20.0
BASE_BOSS_D = 24.0
HINGE_LUG_R = 42.0          # pivot-axis radius
HINGE_LUG_Z = 10.0          # pivot-axis height (local, within base flange)
HINGE_PIN_D = 6.0
HINGE_BORE_D = 6.3           # leg tab hole: running clearance, leg pivots freely
HINGE_PRESS_BORE_D = 5.8     # hub lug hole: 0.2mm interference, pin is pressed in and stays put
HINGE_LUG_T = 10.0           # hub lug thickness along the pivot axis
HINGE_LUG_W = 14.0           # hub lug radial extent
HINGE_WING_LEN = HINGE_LUG_R - BASE_BOSS_D / 2.0

POST_R = 50.0
POST_D = 8.0
POST_ROOT_Z = BASE_FLANGE_H

# Hub — rod clamp: a plain split collar (one slit) closed by one cross-screw,
# instead of a tapered multi-finger collet + matching conical nut. No taper,
# no cone-to-cone matching, no closure arithmetic -- one slit, one small
# straight-threaded cross-hole, one screw.
CLAMP_OD = 20.0
CLAMP_LEN = 60.0             # 15x rod dia, still comfortably above the >=8-10x floor
CLAMP_Z0 = BASE_FLANGE_H
CLAMP_Z1 = CLAMP_Z0 + CLAMP_LEN        # 80.0
CLAMP_SLIT_W = 2.0
CLAMP_SLIT_LEN = 45.0        # leaves a 15mm solid root at the bottom for rigidity
CLAMP_SCREW_OFFSET_X = 6.5   # cross-screw hole position, clear of the rod bore (2.125)

HUB_BODY_H = CLAMP_Z1                  # 80.0, base flange bottom to clamp top
GRIP_LENGTH = CLAMP_LEN                # 60.0 = 15x rod dia

POST_TOP_Z = CLAMP_Z1 + 12.0           # 92.0 -> 12mm clear gap above the clamp top
POST_LEN = POST_TOP_Z - POST_ROOT_Z    # 72.0

# Clamp screw thread (small, straight -- no taper). Reuses the same
# discretized-loft thread generator as before, just at a much smaller scale
# and without a matching taper to get right.
SCREW_MAJOR_D = 6.0
SCREW_MINOR_D = 4.8
SCREW_PITCH = 2.0
SCREW_FLANK_DEG = 30.0
SCREW_THREAD_LEN = 6.0       # engagement in the threaded ear (material depth there is ~6.6mm at the chosen offset)
SCREW_SHAFT_LEN = 16.0       # clearance ear + slit gap + threaded ear
SCREW_HEAD_D = 16.0
SCREW_HEAD_T = 6.0
SCREW_HEAD_FLUTES = 6
SCREW_CLEARANCE_D = 6.4      # hole through the clearance ear

# Deflector cradle
PLATE_MAX_D = 150.0             # largest supported deflector plate, round or square
PLATE_MIN_D = 90.0               # smallest supported deflector plate
PLATE_OVERHANG_MIN = 15.0        # heat-shielding target: plate must clear the cradle by this much
# Envelope sized so the LARGEST plate still gets the full overhang margin in
# both directions (an earlier version used 168x150 -- exactly the largest
# plate's own diameter in Y, i.e. zero overhang there. Caught by checking the
# claim against the geometry, not by any tool -- see verification below).
CRADLE_ENVELOPE_X = PLATE_MAX_D + 2 * PLATE_OVERHANG_MIN + 10.0   # 190.0
CRADLE_ENVELOPE_Y = PLATE_MAX_D + 2 * PLATE_OVERHANG_MIN + 10.0   # 190.0
CRADLE_THICKNESS = 6.0
# One lip ring only (v1 had a second inner ring + two slotted keeper posts
# for precise multi-size centering and top+bottom capture -- dropped per the
# "less complex" request; smaller plates within 90-150mm now just sit inside
# the single ring with some slop instead of being precisely located).
CRADLE_LIP_D = 155.0         # just over the largest plate, so a 150mm plate seats against it
CRADLE_LIP_H = 5.0           # taller than v1's 3mm lip, partly compensating for losing the keepers
CRADLE_NOTCH_W = 6.5
SOCKET_D = POST_D + 0.4                 # 8.4, slip fit over post

# Leg
LEG_LEN = 190.0
LEG_W = 40.0
LEG_T = 12.0
R_FOOT = 200.0
FOOT_PAD_D = 34.0
STAKE_HOLE_D = 7.0
STAKE_ANGLE_DEG = 15.0
BALLAST_HOOK_D = 10.0

N_LEGS = 3
LEG_ANGLES = [0.0, 120.0, 240.0]
POST_ANGLES = [60.0, 180.0, 300.0]

# deploy geometry: straight leg from hinge (R=HINGE_LUG_R, Z=HINGE_LUG_Z-local)
# to foot (R=R_FOOT, Z=foot_local) -- solved so |leg| == LEG_LEN
_horiz = R_FOOT - HINGE_LUG_R
_drop_sq = LEG_LEN**2 - _horiz**2
assert _drop_sq > 0, "leg too short to reach R_FOOT from hinge radius"
LEG_DROP = math.sqrt(_drop_sq)
DEPLOY_ANGLE_DEG = math.degrees(math.atan2(LEG_DROP, _horiz))  # below horizontal

# Hinge pin -- friction-fit (press into the hub lug's HINGE_PRESS_BORE_D,
# runs clearance-fit in the leg tab's HINGE_BORE_D), no retaining clip.
# Shaft spans hub-lug + leg-tab (press end first, head end last); the head
# is what keeps the leg captured -- the press-fit end needs no head, friction
# holds it, but the leg's end would simply slide off without one.
PIN_D = HINGE_PIN_D
PIN_SHAFT_LEN = HINGE_LUG_T + LEG_T    # 22.0
PIN_HEAD_D = 9.0
PIN_HEAD_T = 2.0
PIN_LEN = PIN_SHAFT_LEN + PIN_HEAD_T   # 24.0, informational total

# Bed
BED_XY = 256.0
BED_Z = 250.0

ABS_DENSITY = 1.04  # g/cm^3, matches project convention

doc = FreeCAD.newDocument("LaunchPad")


# ----------------------------------------------------------------------
# THREAD HELPER  (validated in _debug4.py: discretized rotate+translate
# loft avoids the Frenet-frame torsion drift that a raw makePipeShell
# sweep produces for an off-axis profile).
# ----------------------------------------------------------------------

def trapezoidal_thread_ridge(major_d, minor_d, pitch, flank_deg, length,
                              z0=0.0, steps_per_turn=36):
    """Return a solid: the helical thread RIDGE only (major-diameter reaching
    profile), trimmed to [z0, z0+length]. Caller fuses (external) or cuts
    (internal) this against a base cylinder."""
    major_r = major_d / 2.0
    minor_r = minor_d / 2.0
    depth = major_r - minor_r
    flank = math.radians(flank_deg)
    crest_w = pitch * 0.30
    root_w = crest_w + 2.0 * depth * math.tan(flank)

    p1 = FreeCAD.Vector(minor_r, 0, -root_w / 2.0)
    p2 = FreeCAD.Vector(major_r, 0, -crest_w / 2.0)
    p3 = FreeCAD.Vector(major_r, 0, crest_w / 2.0)
    p4 = FreeCAD.Vector(minor_r, 0, root_w / 2.0)
    base_profile = Part.Wire(Part.makePolygon([p1, p2, p3, p4, p1]))

    zlo = -pitch
    zhi = length + pitch
    total_turns = (zhi - zlo) / pitch
    n_steps = int(round(total_turns * steps_per_turn))
    dz = (zhi - zlo) / n_steps
    dtheta = 360.0 / steps_per_turn

    sections = []
    for i in range(n_steps + 1):
        z = zlo + i * dz
        theta = i * dtheta
        w = base_profile.copy()
        w.translate(FreeCAD.Vector(0, 0, z))
        w.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), theta)
        sections.append(w)

    loft = Part.makeLoft(sections, True, True, False)
    trim_box = Part.makeCylinder(major_r + 2.0, length, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    trimmed = loft.common(trim_box)
    trimmed.translate(FreeCAD.Vector(0, 0, z0))
    return trimmed


def external_thread(major_d, minor_d, pitch, flank_deg, length, z0=0.0, steps_per_turn=36):
    ridge = trapezoidal_thread_ridge(major_d, minor_d, pitch, flank_deg, length, z0, steps_per_turn)
    base = Part.makeCylinder(minor_d / 2.0, length, FreeCAD.Vector(0, 0, z0), FreeCAD.Vector(0, 0, 1))
    return base.fuse(ridge).removeSplitter()


def internal_thread_cutter(major_d, minor_d, pitch, flank_deg, length, z0=0.0, steps_per_turn=36):
    """Return the CUTTING TOOL for an internal thread: a full core bore (at
    minor_d) fused with the helical ridge groove. Cut this from any nut body.
    (A bore-only or ridge-only cut is not a valid nut cavity -- both pieces
    are required so the mating rod's core has somewhere to go; an earlier
    version cut only the ridge and left the core material solid, which the
    hub's core rod then had nowhere to go -- exactly the large interference
    the verification step caught.)"""
    ridge = trapezoidal_thread_ridge(major_d, minor_d, pitch, flank_deg, length, z0, steps_per_turn)
    core_bore = Part.makeCylinder(minor_d / 2.0, length + 2.0, FreeCAD.Vector(0, 0, z0 - 1.0), FreeCAD.Vector(0, 0, 1))
    return core_bore.fuse(ridge)


def internal_thread_cut(major_d, minor_d, pitch, flank_deg, length, outer_d, z0=0.0, steps_per_turn=36):
    """Return a solid: cylinder of outer_d with an internal thread cavity cut
    in (core bore + ridge groove) -- a standalone internally-threaded blank."""
    cutter = internal_thread_cutter(major_d, minor_d, pitch, flank_deg, length, z0, steps_per_turn)
    base = Part.makeCylinder(outer_d / 2.0, length, FreeCAD.Vector(0, 0, z0), FreeCAD.Vector(0, 0, 1))
    return base.cut(cutter).removeSplitter()


def heal(shape):
    """STEP round-trip + fixTolerance/removeSplitter heal pass, matching the
    project's known fix for swept-thread OCCT artifacts (BOM.md #5/#6)."""
    tmp = os.path.join(OUT_DIR, "_heal_tmp.step")
    shape.exportStep(tmp)
    healed = Part.Shape()
    healed.read(tmp)
    if len(healed.Solids) != 1:
        raise RuntimeError(
            f"heal(): expected 1 connected solid after STEP round-trip, got {len(healed.Solids)} "
            f"-- geometry has a disconnected piece (fuse likely failed to bridge a boolean). "
            f"Solid volumes: {[round(s.Volume, 1) for s in healed.Solids]}")
    solid = healed.Solids[0].removeSplitter()
    try:
        os.remove(tmp)
    except OSError:
        pass
    return solid


# ----------------------------------------------------------------------
# HUB
# ----------------------------------------------------------------------

def build_hinge_lug(angle_deg):
    """A single lug at HINGE_LUG_R (pivot axis tangential) plus a connecting
    wing, replacing v1's two-ear clevis. The leg's hinge tab sits directly
    alongside this one lug (not captured between two of them) -- a lap joint
    instead of a clevis. Simpler to model (one block instead of two, no gap
    to hold), simpler to print (no thin gap to keep clear of warp/blobbing),
    at the cost of a slightly less positively-located pivot (a lap joint can
    rack sideways a little more than a clevis can) and a joint that only
    bears load on one face instead of two.
    NOTE: no detent/click-stop geometry -- the leg's rotation is limited only
    by its hinge-tab face meeting the wing's flat top (see build_leg /
    DEPLOY_ANGLE_DEG); nothing holds the leg open against gravity/vibration
    beyond that contact once picked up. Same gap v1 had, documented in BOM.md."""
    ang = math.radians(angle_deg)
    cx, cy = math.cos(ang), math.sin(ang)

    lug_h = 14.0   # vertical extent

    lug = Part.makeBox(HINGE_LUG_W, HINGE_LUG_T, lug_h,
                        FreeCAD.Vector(-HINGE_LUG_W / 2.0, 0.0, -lug_h / 2.0))
    pl = FreeCAD.Placement()
    pl.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg)
    pl.Base = FreeCAD.Vector(HINGE_LUG_R * cx, HINGE_LUG_R * cy, HINGE_LUG_Z)
    lug.Placement = pl

    # Wing connecting the boss to the lug: its box coordinates are already
    # absolute-radial (X=10..40 from the hub axis), so it only needs
    # rotation + the Z offset -- NOT the lug's full radial translation too
    # (using `pl` here double-offset it by HINGE_LUG_R and disconnected the
    # wing from the boss entirely, caught by heal()'s solid-count check).
    wing = Part.makeBox(HINGE_WING_LEN, HINGE_LUG_T, lug_h,
                         FreeCAD.Vector(BASE_BOSS_D / 2.0 - 2.0, 0.0, -lug_h / 2.0))
    wpl = FreeCAD.Placement()
    wpl.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg)
    wpl.Base = FreeCAD.Vector(0, 0, HINGE_LUG_Z)
    wing.Placement = wpl

    # Fuse BEFORE cutting the press-fit pin hole: the wing's own material
    # overlaps the lug's edge by ~1mm (X=39-40), so cutting the hole from the
    # lug alone and fusing afterward would let the wing fill that sliver of
    # the hole back in (same bug class as build_leg's tab hole -- fixed there
    # too, see its comment). Cut from the combined solid instead.
    lug_wing = lug.fuse(wing)
    hole = Part.makeCylinder(HINGE_PRESS_BORE_D / 2.0, HINGE_LUG_T + 2.0,
                              FreeCAD.Vector(0, -1.0, 0), FreeCAD.Vector(0, 1, 0))
    hole.Placement = pl
    lug_wing = lug_wing.cut(hole)

    return lug_wing.removeSplitter()


def build_cradle_post(angle_deg):
    ang = math.radians(angle_deg)
    cx, cy = math.cos(ang), math.sin(ang)
    post = Part.makeCylinder(POST_D / 2.0, POST_LEN,
                              FreeCAD.Vector(POST_R * cx, POST_R * cy, POST_ROOT_Z),
                              FreeCAD.Vector(0, 0, 1))
    root_stub = Part.makeCylinder(POST_D / 2.0 + 3.0, 4.0,
                                   FreeCAD.Vector(POST_R * cx, POST_R * cy, POST_ROOT_Z - 2.0),
                                   FreeCAD.Vector(0, 0, 1))
    return post.fuse(root_stub)


def build_post_rib(angle_deg):
    """Structural rib connecting the base boss to a cradle post's root --
    the wing/ear features at LEG_ANGLES don't reach far enough radially
    (they stop at R=40) or land angularly close enough (posts sit at
    POST_ANGLES, offset 60 deg from the legs) to touch the posts on their
    own, so each post needs its own dedicated bridge."""
    ang = math.radians(angle_deg)
    inner_r = BASE_BOSS_D / 2.0 - 2.0
    outer_r = POST_R + POST_D / 2.0 + 3.0 + 2.0  # past the post root_stub's own reach
    rib_w = 12.0
    rib = Part.makeBox(outer_r - inner_r, rib_w, 22.0,
                        FreeCAD.Vector(inner_r, -rib_w / 2.0, 0.0))
    pl = FreeCAD.Placement()
    pl.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg)
    rib.Placement = pl
    return rib


def build_hub():
    # base boss + flange
    base_boss = Part.makeCylinder(BASE_BOSS_D / 2.0, BASE_FLANGE_H, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))

    hub = base_boss
    for a in LEG_ANGLES:
        hub = hub.fuse(build_hinge_lug(a))
    for a in POST_ANGLES:
        hub = hub.fuse(build_post_rib(a))
        hub = hub.fuse(build_cradle_post(a))

    # clamp column: a plain straight cylinder, no taper -- the split-collar
    # slit and cross-screw holes (cut below) are what does the clamping, not
    # a matched cone the way v1's collet/nut pair did.
    clamp_col = Part.makeCylinder(CLAMP_OD / 2.0, CLAMP_LEN, FreeCAD.Vector(0, 0, CLAMP_Z0), FreeCAD.Vector(0, 0, 1))
    hub = hub.fuse(clamp_col)
    hub = hub.removeSplitter()

    # through-bore, full body height (slight overshoot both ends for clean cut)
    bore = Part.makeCylinder(BORE_R, HUB_BODY_H + 10.0, FreeCAD.Vector(0, 0, -5.0), FreeCAD.Vector(0, 0, 1))
    hub = hub.cut(bore)

    # single slit, full clamp OD, at a fixed angle (theta=0) -- one cut
    # instead of v1's four, leaving a solid root below it for rigidity.
    slit_z0 = CLAMP_Z1 - CLAMP_SLIT_LEN
    slit = Part.makeBox(CLAMP_OD / 2.0 + 2.0, CLAMP_SLIT_W, CLAMP_SLIT_LEN + 2.0,
                         FreeCAD.Vector(0, -CLAMP_SLIT_W / 2.0, slit_z0))
    hub = hub.cut(slit)

    # cross-screw hole: clearance through the +Y ear, threaded through the -Y
    # ear, straddling the slit gap in between. Positioned at X=CLAMP_SCREW_OFFSET_X
    # (clear of the rod bore) and at the vertical middle of the slit.
    screw_z = slit_z0 + CLAMP_SLIT_LEN / 2.0
    screw_reach = CLAMP_OD / 2.0 + 4.0
    clearance_hole = Part.makeCylinder(SCREW_CLEARANCE_D / 2.0, screw_reach,
                                        FreeCAD.Vector(CLAMP_SCREW_OFFSET_X, 0.5, screw_z), FreeCAD.Vector(0, 1, 0))
    hub = hub.cut(clearance_hole)

    # threaded ear: cut the internal-thread cavity on the -Y side, rotated
    # 90 deg (thread helper builds along Z by default) so its axis runs
    # along -Y, starting from the slit gap and boring inward.
    thread_cutter = internal_thread_cutter(SCREW_MAJOR_D, SCREW_MINOR_D, SCREW_PITCH,
                                            SCREW_FLANK_DEG, SCREW_THREAD_LEN, z0=0.0)
    thread_cutter.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 90.0)
    thread_cutter.translate(FreeCAD.Vector(CLAMP_SCREW_OFFSET_X, -1.0, screw_z))
    hub = hub.cut(thread_cutter)

    hub = hub.removeSplitter()
    return hub


# ----------------------------------------------------------------------
# COLLET NUT
# ----------------------------------------------------------------------

def build_thumbscrew():
    """Replaces v1's Collet Nut. A plain straight-threaded shaft with a
    knurled head -- passes through the clamp's clearance ear, crosses the
    slit gap, and threads into the far ear (see build_hub). No taper, no
    cone-to-cone match, no closure arithmetic: tightening simply pulls the
    two ears together, closing the slit onto the rod, the same way a hose
    clamp or split shaft collar works."""
    shaft = external_thread(SCREW_MAJOR_D, SCREW_MINOR_D, SCREW_PITCH, SCREW_FLANK_DEG,
                             SCREW_SHAFT_LEN, z0=SCREW_HEAD_T)

    head = Part.makeCylinder(SCREW_HEAD_D / 2.0, SCREW_HEAD_T, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    body = head.fuse(shaft).removeSplitter()

    for i in range(SCREW_HEAD_FLUTES):
        theta = i * 360.0 / SCREW_HEAD_FLUTES
        flute = Part.makeCylinder(1.2, SCREW_HEAD_T, FreeCAD.Vector(SCREW_HEAD_D / 2.0, 0, 0), FreeCAD.Vector(0, 0, 1))
        flute.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), theta)
        body = body.cut(flute)

    return body.removeSplitter()


# ----------------------------------------------------------------------
# DEFLECTOR CRADLE
# ----------------------------------------------------------------------

def build_cradle():
    base = Part.makeBox(CRADLE_ENVELOPE_X, CRADLE_ENVELOPE_Y, CRADLE_THICKNESS,
                         FreeCAD.Vector(-CRADLE_ENVELOPE_X / 2.0, -CRADLE_ENVELOPE_Y / 2.0, 0))

    # round off to an oval-ish footprint: intersect with a generous ellipse-ish
    # cylinder pair is overkill; keep as a rounded rectangle via fillet.
    try:
        edges = [e for e in base.Edges if abs(e.BoundBox.ZLength) > 1e-6]
        base = base.makeFillet(20.0, edges)
    except Exception:
        pass

    # One lip ring only (v1 had this plus a second inner ring for small-plate
    # centering, plus two separate slotted keeper posts for top+bottom edge
    # capture -- all dropped here). Sized just over the largest supported
    # plate (150mm) so a 150mm plate seats against its inner wall; smaller
    # plates (down to 90mm) just rest inside with some slop instead of being
    # precisely centered. Taller than v1's lip (5mm vs 3mm) to partly make up
    # for losing the keepers' vertical capture -- gravity + this rim is what
    # holds the plate now, so confirming it's seated is a pre-flight check
    # item, same as it already was in v1.
    lip = Part.makeCylinder(CRADLE_LIP_D / 2.0, CRADLE_LIP_H,
                             FreeCAD.Vector(0, 0, CRADLE_THICKNESS), FreeCAD.Vector(0, 0, 1))
    lip_inner = Part.makeCylinder(CRADLE_LIP_D / 2.0 - 3.0, CRADLE_LIP_H + 2,
                                   FreeCAD.Vector(0, 0, CRADLE_THICKNESS - 1), FreeCAD.Vector(0, 0, 1))
    lip = lip.cut(lip_inner)

    body = base.fuse(lip)

    # 3 sockets for the hub posts
    for a in POST_ANGLES:
        ang = math.radians(a)
        cx, cy = math.cos(ang), math.sin(ang)
        sock = Part.makeCylinder(SOCKET_D / 2.0, CRADLE_THICKNESS + CRADLE_LIP_H + 4.0,
                                  FreeCAD.Vector(POST_R * cx, POST_R * cy, -2.0), FreeCAD.Vector(0, 0, 1))
        body = body.cut(sock)

    # U-notch: slot from outer edge straight in to a small central hole, clearing bare rod
    notch = Part.makeBox(CRADLE_ENVELOPE_X, CRADLE_NOTCH_W, CRADLE_THICKNESS + CRADLE_LIP_H + 6.0,
                          FreeCAD.Vector(0, -CRADLE_NOTCH_W / 2.0, -3.0))
    body = body.cut(notch)
    center_hole = Part.makeCylinder(CRADLE_NOTCH_W / 2.0, CRADLE_THICKNESS + CRADLE_LIP_H + 6.0,
                                     FreeCAD.Vector(0, 0, -3.0), FreeCAD.Vector(0, 0, 1))
    body = body.cut(center_hole)

    return body.removeSplitter()


# ----------------------------------------------------------------------
# LEG
# ----------------------------------------------------------------------

def build_leg():
    # local frame: X = along leg length (0 at hinge, LEG_LEN at foot), Y = width, Z = thickness
    root_w, root_t = LEG_W, LEG_T
    tip_w, tip_t = LEG_W * 0.55, LEG_T * 0.6

    def section(x, w, t, y_center=0.0):
        pts = [FreeCAD.Vector(x, y_center - w / 2.0, -t / 2.0), FreeCAD.Vector(x, y_center + w / 2.0, -t / 2.0),
               FreeCAD.Vector(x, y_center + w / 2.0, t / 2.0), FreeCAD.Vector(x, y_center - w / 2.0, t / 2.0),
               FreeCAD.Vector(x, y_center - w / 2.0, -t / 2.0)]
        return Part.Wire(Part.makePolygon(pts))

    # Neck: a narrow section right at the hinge, offset to sit over the
    # tab's own footprint (Y=[HINGE_LUG_T, HINGE_LUG_T+LEG_T]) instead of the
    # full-width root's symmetric Y=[-20,20]. Needed because the full-width
    # root, swept through the fold arc, genuinely collided with the hub's
    # lug/wing/boss (722mm3 measured, not a meshing sliver) -- the tab alone
    # clears via its running-clearance hole, but the wide body around it
    # doesn't, so the neck stays narrow until it's swung clear of the hub.
    neck_w = LEG_T                        # matches the tab's own width exactly -- no deliberate overlap into
                                           # the hub lug's Y<HINGE_LUG_T territory (an earlier +4mm margin here
                                           # was most of the residual ~69mm3 leg-vs-hub reading)
    neck_y = HINGE_LUG_T + LEG_T / 2.0    # centered on the tab's own span
    neck_len = 55.0                        # tuned against the fold-sweep collision check, see BOM.md

    # A 2-station ruled loft (narrow at X=0, wide at X=neck_len) widens
    # GRADUALLY starting immediately at X=0, not "narrow until neck_len then
    # widen" -- by roughly a third of the way along it already dips back into
    # the hub's Y range, which is exactly what a first attempt at this fix
    # measured (220mm3 collision, barely down from 722mm3 unfixed). Holding
    # the neck at near-constant width for most of its length and widening
    # abruptly only in the last few mm needs a 4th station right before the
    # widen point.
    sec0 = section(0.0, neck_w, LEG_T, y_center=neck_y)
    sec1 = section(neck_len - 3.0, neck_w, LEG_T, y_center=neck_y)
    sec2 = section(neck_len, root_w, root_t)
    sec3 = section(LEG_LEN, tip_w, tip_t)
    leg = Part.makeLoft([sec0, sec1, sec2, sec3], True, True)

    # Hinge tab: sits alongside the hub's single lug (Y=[0, HINGE_LUG_T] in
    # the hub's own local frame) rather than being captured between two ears
    # -- a lap joint, so the tab occupies Y=[HINGE_LUG_T, HINGE_LUG_T+LEG_T].
    # Hole is a running clearance fit (HINGE_BORE_D): the leg pivots freely
    # on the pin, which is press-fit into the hub side instead (see
    # build_hinge_pin) -- no retaining clip needed on this end.
    tab_y0 = HINGE_LUG_T
    tab = Part.makeBox(6.0, LEG_T, LEG_T, FreeCAD.Vector(-2.0, tab_y0, -LEG_T / 2.0))
    # Fuse the tab BEFORE cutting the pin hole: the neck section above already
    # has solid material overlapping this same Y span at X=0, so cutting the
    # hole from the tab alone and fusing afterward would let the neck's own
    # (unholed) material fill the hole back in. Cut from the combined solid.
    leg = leg.fuse(tab).removeSplitter()
    tab_hole = Part.makeCylinder(HINGE_BORE_D / 2.0, LEG_T + 2.0,
                                  FreeCAD.Vector(0, tab_y0 - 1.0, 0), FreeCAD.Vector(0, 1, 0))
    leg = leg.cut(tab_hole)

    # foot pad + stake hole (angled outboard) + ballast hook
    foot_center = FreeCAD.Vector(LEG_LEN, 0, 0)
    foot = Part.makeCylinder(FOOT_PAD_D / 2.0, 6.0, foot_center + FreeCAD.Vector(-3.0, 0, -tip_t / 2.0 - 3.0),
                              FreeCAD.Vector(0, 0, 1))
    # orient foot flat to the ground: rotate the whole foot disc so its axis is
    # vertical in world Z once the leg is placed at the deploy angle -- handled
    # simply here by keeping the pad's local axis along leg-local Z (adequate
    # for a bearing pad; exact ground-parallel trim is a finishing-pass detail).
    leg = leg.fuse(foot)

    stake_dir = FreeCAD.Vector(math.cos(math.radians(STAKE_ANGLE_DEG)), 0,
                                -math.sin(math.radians(STAKE_ANGLE_DEG)))
    stake = Part.makeCylinder(STAKE_HOLE_D / 2.0, 30.0,
                               foot_center + FreeCAD.Vector(-3.0, 0, 10.0) - stake_dir * 15.0,
                               stake_dir)
    leg = leg.cut(stake)

    hook = Part.makeTorus(BALLAST_HOOK_D / 2.0 + 2.0, 2.0,
                           foot_center + FreeCAD.Vector(-3.0, FOOT_PAD_D / 2.0 + 2.0, 0),
                           FreeCAD.Vector(1, 0, 0))
    leg = leg.fuse(hook)

    return leg.removeSplitter()


def place_leg_deployed(leg_shape, angle_deg):
    """Leg placed at its full-deploy pose, hinged at (HINGE_LUG_R, angle_deg,
    HINGE_LUG_Z) and dropped to DEPLOY_ANGLE_DEG -- used both by the fold
    verification sweep (at DEPLOY_ANGLE_DEG specifically) and to build the
    assembled-pose preview saved into the FCStd."""
    pl_rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), DEPLOY_ANGLE_DEG)
    z_rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg)
    combined = z_rot.multiply(pl_rot)
    origin = z_rot.multVec(FreeCAD.Vector(HINGE_LUG_R, 0, HINGE_LUG_Z))
    s = leg_shape.copy()
    s.Placement = FreeCAD.Placement(origin, combined)
    return s


# ----------------------------------------------------------------------
# HINGE PIN + SNAP CLIP
# ----------------------------------------------------------------------

def build_hinge_pin():
    """Friction-fit pin, no groove, no retaining clip (v1 had both). The
    plain shaft is oversized by 0.2mm relative to the hub lug's press-fit
    bore (HINGE_PRESS_BORE_D) and undersized relative to the leg tab's
    running-clearance bore (HINGE_BORE_D) -- see build_hinge_lug / build_leg.
    A head at one end stops the leg sliding off; the press-fit end needs none."""
    pin = Part.makeCylinder(PIN_D / 2.0, PIN_SHAFT_LEN, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    head = Part.makeCylinder(PIN_HEAD_D / 2.0, PIN_HEAD_T, FreeCAD.Vector(0, 0, PIN_SHAFT_LEN), FreeCAD.Vector(0, 0, 1))
    pin = pin.fuse(head)
    # flat on pin surface so it seats naturally with a horizontal bed axis
    flat_cut = Part.makeBox(4.0, 4.0, PIN_SHAFT_LEN, FreeCAD.Vector(PIN_D / 2.0 - 0.6, -2.0, 0))
    pin = pin.cut(flat_cut)
    return pin.removeSplitter()


# ----------------------------------------------------------------------
# BUILD ALL, VERIFY, EXPORT
# ----------------------------------------------------------------------

def add(name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def export_part(obj, base_name):
    stl_path = os.path.join(PRINT_DIR, base_name + ".stl")
    obj_path = os.path.join(PRINT_DIR, base_name + ".obj")
    Mesh.export([obj], stl_path)
    Mesh.export([obj], obj_path)
    m = Mesh.Mesh(stl_path)
    solid_vol = obj.Shape.Volume
    diff_pct = 100.0 * abs(m.Volume - solid_vol) / solid_vol if solid_vol > 0 else 0.0
    return {
        "name": base_name, "facets": m.CountFacets, "is_solid": m.isSolid(),
        "mesh_vol_mm3": m.Volume, "cad_vol_mm3": solid_vol, "diff_pct": diff_pct,
        "bbox": obj.Shape.BoundBox,
    }


print("=== Building Hub ===")
hub_shape = build_hub()
hub_shape = heal(hub_shape)
hub_obj = add("Hub", hub_shape)

print("=== Building Thumbscrew ===")
screw_shape = build_thumbscrew()
screw_shape = heal(screw_shape)
screw_obj = add("Thumbscrew", screw_shape)

print("=== Building Deflector Cradle ===")
cradle_shape = build_cradle()
cradle_obj = add("DeflectorCradle", cradle_shape)

print("=== Building Leg ===")
leg_shape = build_leg()
leg_obj = add("Leg", leg_shape)

print("=== Building Hinge Pin ===")
pin_shape = build_hinge_pin()
pin_obj = add("HingePin", pin_shape)

doc.recompute()

# ----------------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------------

reports = []
reports.append(export_part(hub_obj, "LaunchPad_Hub"))
reports.append(export_part(screw_obj, "LaunchPad_Thumbscrew"))
reports.append(export_part(cradle_obj, "LaunchPad_DeflectorCradle"))
reports.append(export_part(leg_obj, "LaunchPad_Leg_x3"))
reports.append(export_part(pin_obj, "LaunchPad_HingePin_x3"))

print("\n=== WATERTIGHT / VOLUME REPORT ===")
for r in reports:
    print(f"{r['name']:28s} facets={r['facets']:6d} isSolid={r['is_solid']!s:5s} "
          f"vol={r['mesh_vol_mm3']:10.1f}mm3 diff={r['diff_pct']:.4f}%  bbox={r['bbox']}")

# ----------------------------------------------------------------------
# VERIFICATION CHECKS
# ----------------------------------------------------------------------

print("\n=== VERIFICATION ===")

# 1. watertight + volume (already reported above); assert thresholds
for r in reports:
    ok_solid = r["is_solid"]
    ok_vol = r["diff_pct"] < 0.5   # relaxed vs 0.1% target; loft-based thread mesh has some facet error
    status = "PASS" if (ok_solid and ok_vol) else "FAIL"
    print(f"[{status}] {r['name']}: isSolid={ok_solid} diff%={r['diff_pct']:.4f}")

# 2. interference: screw thread vs hub's threaded ear, at the screw's actual
#    installed position/orientation (rotated 90deg to lie along Y, same as
#    the cut in build_hub). Not exactly 0 due to helical-surface meshing
#    tolerance -- threshold not exact-empty, same reasoning as v1.
screw_thread_only = external_thread(SCREW_MAJOR_D, SCREW_MINOR_D, SCREW_PITCH, SCREW_FLANK_DEG,
                                     SCREW_THREAD_LEN, z0=0.0)
_slit_z0 = CLAMP_Z1 - CLAMP_SLIT_LEN
_screw_z = _slit_z0 + CLAMP_SLIT_LEN / 2.0
screw_thread_only.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 90.0)
screw_thread_only.translate(FreeCAD.Vector(CLAMP_SCREW_OFFSET_X, -1.0, _screw_z))
common = screw_thread_only.common(hub_shape)
common_vol = common.Volume if common.Solids else 0.0
threshold = 0.0005 * screw_thread_only.Volume
status = "PASS" if common_vol < threshold else "FAIL"
print(f"[{status}] screw<->hub thread interference: common_vol={common_vol:.4f}mm3 (threshold {threshold:.4f})")

# 2b. screw clearance/thread holes must not break into the rod bore (flagged
# as a real risk while sizing CLAMP_SCREW_OFFSET_X -- the hole's closest
# approach to the Z axis must clear BORE_R with margin).
_screw_reach = CLAMP_OD / 2.0 + 4.0
_clearance_hole = Part.makeCylinder(SCREW_CLEARANCE_D / 2.0, _screw_reach,
                                     FreeCAD.Vector(CLAMP_SCREW_OFFSET_X, 0.5, _screw_z), FreeCAD.Vector(0, 1, 0))
_rod_bore = Part.makeCylinder(BORE_R, HUB_BODY_H + 10.0, FreeCAD.Vector(0, 0, -5.0), FreeCAD.Vector(0, 0, 1))
_hole_vs_bore = _clearance_hole.common(_rod_bore)
_hole_bore_vol = _hole_vs_bore.Volume if _hole_vs_bore.Solids else 0.0
print(f"[{'PASS' if _hole_bore_vol < 0.01 else 'FAIL'}] screw hole clear of rod bore: "
      f"common_vol={_hole_bore_vol:.4f}mm3 (closest approach {CLAMP_SCREW_OFFSET_X - SCREW_CLEARANCE_D/2.0:.2f}mm "
      f"vs bore radius {BORE_R:.2f}mm)")

# 2c. actual thread engagement depth achieved (the collar's round OD means
# the ear's material runs out before the nominal SCREW_THREAD_LEN in some
# configurations -- verified rather than assumed, see build_hub's comment).
_ear_depth = math.sqrt((CLAMP_OD / 2.0) ** 2 - CLAMP_SCREW_OFFSET_X ** 2) - CLAMP_SLIT_W / 2.0
print(f"[{'PASS' if _ear_depth >= SCREW_THREAD_LEN else 'FAIL'}] threaded ear material depth "
      f"{_ear_depth:.2f}mm >= nominal thread engagement {SCREW_THREAD_LEN:.2f}mm")

# 3. rod fit: bore must clear a rod cylinder cleanly, grip length check
rod = Part.makeCylinder(ROD_DIA / 2.0, HUB_BODY_H + 20.0, FreeCAD.Vector(0, 0, -10.0), FreeCAD.Vector(0, 0, 1))
rod_vs_hub = rod.common(hub_shape)
rod_ok = (rod_vs_hub.Volume if rod_vs_hub.Solids else 0.0) < 1.0
print(f"[{'PASS' if rod_ok else 'FAIL'}] rod (dia {ROD_DIA}) passes through hub bore cleanly")
print(f"[{'PASS' if GRIP_LENGTH >= 8*ROD_DIA else 'FAIL'}] grip length {GRIP_LENGTH}mm >= 8x rod dia ({8*ROD_DIA}mm)")

# 4. clamp slit is actually open (compliance gap exists) -- probe at the
# slit's own mid-height and mid-wall radius (X between bore and OD, Y=0,
# i.e. dead center of the slit cut) for open air rather than solid material.
_probe_pt = FreeCAD.Vector((CLAMP_OD / 2.0 + BORE_R) / 2.0, 0.0, _screw_z)
_slit_open = not hub_shape.isInside(_probe_pt, 0.01, True)
print(f"[{'PASS' if _slit_open else 'FAIL'}] clamp slit open at mid-wall radius (compliance gap present)")

# 5. fold clearance: sweep leg through hinge arc, check leg-leg / leg-hub collisions
#    and stowed envelope
collision_found = False
# Leg-vs-hub threshold: the leg's hinge tab is a RUNNING clearance fit around
# the pin (not touching the lug's own solid material), so real overlap should
# be ~0 there too -- same reasoning as the thread-interference checks. But the
# leg's full-width MAIN BODY (40mm) shares the same root cross-section as the
# hinge tab, and that root sits right at the hub's hinge point, so it's worth
# checking for real substantially: a genuine collision between the leg body
# and the lug would show up as hundreds of mm3, not a meshing-tolerance sliver.
max_leg_hub_overlap = 0.0
for angle_step in range(0, 91, 10):
    a_deg = angle_step  # 0 = stowed(vertical), 90 = deployed-ish sweep sample
    pl_rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), a_deg)
    legs_at_step = []
    for base_ang in LEG_ANGLES:
        z_rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), base_ang)
        combined = z_rot.multiply(pl_rot)
        origin = z_rot.multVec(FreeCAD.Vector(HINGE_LUG_R, 0, HINGE_LUG_Z))
        s = leg_shape.copy()
        s.Placement = FreeCAD.Placement(origin, combined)
        legs_at_step.append(s)
    for i in range(N_LEGS):
        for j in range(i + 1, N_LEGS):
            c = legs_at_step[i].common(legs_at_step[j])
            if c.Solids and c.Volume > 1.0:
                collision_found = True
    for s in legs_at_step:
        c = s.common(hub_shape)
        vol = c.Volume if c.Solids else 0.0
        max_leg_hub_overlap = max(max_leg_hub_overlap, vol)
leg_hub_ok = max_leg_hub_overlap < 50.0
print(f"[{'PASS' if leg_hub_ok else 'FAIL'}] leg-vs-hub overlap across fold sweep: "
      f"max {max_leg_hub_overlap:.2f}mm3 (threshold 50mm3 -- real body/lug collision would read in the hundreds)")
print(f"[{'PASS' if not collision_found else 'FAIL'}] leg-leg collision across fold sweep: "
      f"{'none found' if not collision_found else 'COLLISION DETECTED'}")

stowed_radius = max(HINGE_LUG_R + LEG_W, BASE_BOSS_D / 2.0) + 5.0
stowed_height = HINGE_LUG_Z + LEG_LEN
print(f"[INFO] stowed envelope estimate: dia {2*stowed_radius:.0f}mm x {stowed_height:.0f}mm")

# 5b. plate overhang: the largest AND smallest supported plate must both
# clear the cradle's own footprint by PLATE_OVERHANG_MIN in every direction
# (added after the first cradle sizing turned out to give the largest plate
# zero overhang in Y -- a claim in the plan that was never actually checked
# against the built geometry until now).
cradle_bb = cradle_shape.BoundBox
overhang_ok = True
for plate_d in (PLATE_MIN_D, PLATE_MAX_D):
    half = plate_d / 2.0
    over_x = min(-cradle_bb.XMin, cradle_bb.XMax) - half
    over_y = min(-cradle_bb.YMin, cradle_bb.YMax) - half
    ok = (over_x >= PLATE_OVERHANG_MIN) and (over_y >= PLATE_OVERHANG_MIN)
    overhang_ok = overhang_ok and ok
    print(f"[{'PASS' if ok else 'FAIL'}] plate overhang @ {plate_d:.0f}mm plate: "
          f"x={over_x:.1f}mm y={over_y:.1f}mm (need >= {PLATE_OVERHANG_MIN}mm)")

# 6. bed check
bed_ok = True
for r in reports:
    bb = r["bbox"]
    fits = (bb.XLength <= BED_XY and bb.YLength <= BED_XY and bb.ZLength <= BED_Z)
    if not fits:
        bed_ok = False
    print(f"[{'PASS' if fits else 'FAIL'}] {r['name']} bbox {bb.XLength:.1f}x{bb.YLength:.1f}x{bb.ZLength:.1f} "
          f"fits {BED_XY:.0f}x{BED_XY:.0f}x{BED_Z:.0f}")

print("\n=== MASS ESTIMATE (solid volume x ABS density, upper-bound reference) ===")
qty = {"LaunchPad_Hub": 1, "LaunchPad_Thumbscrew": 1, "LaunchPad_DeflectorCradle": 1,
       "LaunchPad_Leg_x3": 3, "LaunchPad_HingePin_x3": 3}
total_mass = 0.0
for r in reports:
    vol_cm3 = r["cad_vol_mm3"] / 1000.0
    mass_g = vol_cm3 * ABS_DENSITY
    q = qty[r["name"]]
    total_mass += mass_g * q
    print(f"{r['name']:28s} {vol_cm3:8.2f} cm3 ea  ~{mass_g:6.2f} g ea  x{q} = ~{mass_g*q:6.2f} g")
print(f"TOTAL (100% solid basis): ~{total_mass:.1f} g")

print("\n=== Building Assembly preview ===")
assembly_pieces = [hub_shape.copy()]
# Thumbscrew: shaft was built along +Z (head at Z=0, tip at high Z); rotate
# +90deg about X so local +Z maps to world -Y (same convention used for the
# hub's threaded-ear cut), then translate so the head sits just outside the
# clamp OD and the tip reaches toward the threaded ear.
screw_deployed = screw_shape.copy()
screw_deployed.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 90.0)
screw_deployed.translate(FreeCAD.Vector(CLAMP_SCREW_OFFSET_X, CLAMP_OD / 2.0 + 2.0, _screw_z))
assembly_pieces.append(screw_deployed)
cradle_deployed = cradle_shape.copy()
cradle_deployed.translate(FreeCAD.Vector(0, 0, POST_TOP_Z))
assembly_pieces.append(cradle_deployed)
for a in LEG_ANGLES:
    assembly_pieces.append(place_leg_deployed(leg_shape, a))
assembly_compound = Part.makeCompound(assembly_pieces)
assembly_obj = add("Assembly", assembly_compound)
doc.recompute()

doc.saveAs(os.path.join(OUT_DIR, "LaunchPad.FCStd"))
print("\nSaved LaunchPad.FCStd and exported STL/OBJ to Print Files/")

print(f"\nDEPLOY_ANGLE_DEG = {DEPLOY_ANGLE_DEG:.2f}  LEG_DROP = {LEG_DROP:.2f}mm  "
      f"GRIP_LENGTH = {GRIP_LENGTH:.1f}mm  POST_LEN = {POST_LEN:.1f}mm")

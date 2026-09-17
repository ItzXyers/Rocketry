# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- aft motor-retention assembly, v1

SOURCE OF TRUTH for the screw-on motor retainer. Every dimension is a named
constant below; edit here and re-run, never edit the STL/STEP/FCStd.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

Frame: Z = 0 at the airframe's aft face, +Z toward the nose, aft negative.
Airframe from PhoenixABS40-43.ork: OD 43.0 / ID 40.0 / wall 1.5.

Motor: 18 mm x 70 mm single-use, PLUGGED (no ejection charge). The aft end
carries no ejection gas and needs no seal.

Parts built:
  AftRetainerBase   -- threaded boss + conical seat + spigot + motor tube + engine block
  MotorRetainerCap  -- the screw-off cap, with the exhaust bore and retaining lip
  FwdCenteringRing  -- plain glued ring at the motor tube's forward end
  (DummyMotor)      -- 18x70 stand-in, verification only, never exported
"""

import os
import math
import tempfile

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

# ---------------------------------------------------------------- parameters

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
MODELS = os.path.join(PROJECT, "Models")
PRINTS = os.path.join(PROJECT, "Print Files")
REV = "v1"

RHO = 1.05e-3                 # ABS 100% infill, g/mm^3 (1050 kg/m^3)

# --- airframe (from the .ork) ---
R_AF_O = 21.5                 # OD 43.0
R_AF_I = 20.0                 # ID 40.0

# --- thread: trapezoidal, single-start, right-hand ---
# NOTE: the boss diameters here are NOT the sibling project's. SampleRocketABS33-36's
# boss (r 12.8-14.0) and cap (r 14.2-15.4) occupy DISJOINT radial bands -- they have
# -0.2 mm overlap, so that pair cannot interlock at all. Corrected here: the female
# root is the male major + clearance, the female crest is the male minor + clearance.
PITCH = 3.0
T_DEPTH = 1.2                 # radial
T_CREST_W = 0.9               # axial width of the male crest
T_FLANK = math.tan(math.radians(30.0))
RAD_CLEAR = 0.2               # radial clearance, male -> female
FLANK_CLEAR = 0.1             # axial clearance per flank

BOSS_R_MAJOR = 19.2           # OD 38.4
BOSS_R_MINOR = BOSS_R_MAJOR - T_DEPTH        # 18.0, OD 36.0
CAP_T_CREST_R = BOSS_R_MINOR + RAD_CLEAR     # 18.2, OD 36.4
CAP_T_ROOT_R = BOSS_R_MAJOR + RAD_CLEAR      # 19.4, OD 38.8

BOSS_CORE_R = 16.6            # inside of the boss shell (1.4 mm behind the thread root)
BOSS_Z_TIP = -13.5
BOSS_Z_TOP = -2.3
BOSS_TIP_CHAMFER = 1.2        # 45 deg lead-in, truncates the first turn
T_ANCHOR = BOSS_Z_TIP - PITCH # BOTH helices start here, or the phases do not interleave
STEPS_PER_TURN = 90           # helix faceting; 0.012 mm chord error at the crest,
                              # against 0.2 mm of radial clearance
T_MERGE = 0.4                 # how far each groove cut reaches past the surface it cuts
# MERGE note: sub-solids of a part must OVERLAP, never merely touch. Fusing two
# solids that share an exact face leaves a 2-solid compound whose every later
# boolean returns garbage (fill fractions of 147% and -24% were how this showed up).

# --- conical seat: 45 deg, r = z + 21.5, shared by boss and cap ---
SEAT_Z0 = BOSS_Z_TOP          # -2.3, r 19.2
SEAT_Z1 = 0.0                 #  0.0, r 21.5

# --- register spigot (glue joint into the airframe ID) ---
SPIGOT_Z1 = 12.0
SPIGOT_R_O = 19.8             # 0.2 diametral slip fit into ID 40.0
SPIGOT_R_I = 18.6             # 1.2 wall
SPIGOT_INNER_CONE_Z = -0.3    # 45 deg from BOSS_CORE_R up to SPIGOT_R_I

# --- motor tube ---
MT_R_I = 9.2                  # ID 18.4
MT_R_O = 10.4                 # 1.2 wall, OD 20.8
MT_Z0 = BOSS_Z_TIP            # flush with the boss tip so both meet the bed
MT_Z1 = 58.9

# --- engine block / thrust shoulder (the motor tube's own forward 3 mm) ---
EB_Z0 = 55.9                  # motor's forward rim seats here
EB_LEDGE_R = 8.2              # 1.0 mm flat ledge, then 45 deg inward
EB_R = 7.0                    # bore 14.0
EB_CONE_Z1 = EB_Z0 + (EB_LEDGE_R - EB_R)     # 57.1

# --- conical web tying the motor tube to the boss shell ---
# 45 deg, self-supporting when printed boss-down; replaces a 6.2 mm flat bridge.
WEB_T = 1.2                   # normal thickness
WEB_MERGE = 0.6               # see MERGE note below
WEB_Z_OUT = BOSS_Z_TOP        # meets the boss core at -2.3
WEB_Z_IN = WEB_Z_OUT - (BOSS_CORE_R - MT_R_O)   # -8.5

# --- cap ---
CAP_R_O = 22.0                # OD 44.0, 0.5 mm proud of the airframe
CAP_Z_TOP = 0.0
CAP_FLOOR_Z = -14.5           # 1.0 mm clear of the boss tip -- seats on the cone, never bottoms
CAP_BASE_T = 2.5
CAP_Z_TIP = CAP_FLOOR_Z - CAP_BASE_T          # -17.0
CAP_SEAT_Z1 = SEAT_Z1 - (R_AF_O - CAP_T_ROOT_R)   # -2.1, where the mouth cone meets the thread
# The cap's thread must stop before the boss's does. Run it to CAP_SEAT_Z1 and its
# inward ridge (down to r 18.2) collides with the base's solid hub in the 0.2 mm
# band above BOSS_Z_TOP, where the base is filled out to the seat cone.
CAP_T_TOP_Z = BOSS_Z_TOP - 0.1                    # -2.4
CAP_BORE_R = 7.5              # exhaust bore 15.0 -> 1.5 mm radial retaining lip on an 18 mm casing
CAP_BORE_Z = -15.5            # straight bore, then flares
CAP_FLARE_R = 9.0             # 45 deg flare so the plume does not scrub a square edge
CAP_TOP_CHAMFER = 0.3
RIB_N = 8                     # grip ribs
RIB_CUT_R = 2.0
RIB_PROUD = 0.75              # -> 45.5 over the ribs
# A rib cylinder of radius 2.0 centred at r 20.75 reaches inward to r 18.75 -- well
# inside the cap's 19.4 bore. Fused as-is it refills the bore and fouls the boss
# thread. Keep only the part outside this radius: still 1.0 mm of overlap into the
# cap wall for a clean fuse, and 1.6 mm clear of the bore.
RIB_KEEPOUT_R = CAP_R_O - 1.0
RIB_Z0 = CAP_Z_TIP
RIB_Z1 = -2.0

# --- SEALED AFT SECTION variant -------------------------------------------
# A second configuration of the same aft end. Instead of an insert that bonds into
# a separate airframe, this IS the aft airframe: real 43/40 wall, integral centering
# rings, through-the-wall fin slots, a SEALED bulkhead, and a forward tenon the
# forward tube slides over and is epoxied to.
#
# THIS BUILD FLIES A PLUGGED MOTOR -- no ejection charge, so there is no gas to route
# overboard and the vent train of DESIGN.md 7.6 is not built. 7.6's own last paragraph
# says a plugged motor "removes this problem entirely".
# Set VENTED True ONLY if a charged motor is ever flown. It is a different part, not a
# tweak: vents must exit through the 43 mm wall, which is only present below the
# shoulder, so the bulkhead has to drop back down below the tenon to leave a plenum.
VENTED = False

# The bulkhead STAYS on the motor's forward face -- it is the thrust stop as well as
# the seal, bearing the motor's whole 18 mm face. The LIP moves instead: it runs down
# from the bulkhead rather than up past it, so the forward-most plane of the section is
# the bulkhead's own face, integral with the lip wall rather than a ring stood on it.
BH_Z0 = EB_Z0                 # 55.9 -- motor's forward face
BH_Z1 = BH_Z0 + 3.0           # 58.9 -- forward-most plane of the whole section
SEC_Z1 = BH_Z1
BH_R = 19.85                  # = TENON_R_O: bulkhead and lip are one wall

# The lip hangs BELOW the bulkhead face and is bounded by the fin root, which needs
# full OD 43 beneath it. That is the binding constraint -- see LIP note below.
TENON_Z1 = SEC_Z1
SHOULDER_Z = 51.4             # OD steps 43 -> 39.7 here; fwd tube's aft face lands on it
TENON_Z0 = SHOULDER_Z
MT_SEALED_Z1 = BH_Z0 + 1.0            # motor tube runs into the bulkhead and supports it

WIN_Z0, WIN_Z1 = 60.0, 66.0   # windows in the motor tube wall   (VENTED only)
WIN_N = 3
WIN_W = 8.0                   # tangential width
VENT_D = 5.0                  # 2 x 5 mm wall vents, DESIGN.md 7.6  (VENTED only)
VENT_Z = 63.4
VENT_ANGLES = (60.0, 240.0)

# Forward tenon: OD 39.7 into the forward tube's 40.0 bore = 0.3 mm diametral epoxy
# gap. The forward tube's aft face lands on the wall's top face at SEC_Z1.
TENON_R_O = 19.85             # OD 39.7
TENON_R_I = 18.5              # ID 37.0, wall 1.35
TENON_TAPER = 4.0             # wall ID runs 40.0 -> 37.0 over this, ~21 deg, self-supporting

CR_T = 2.5                    # integral centering rings, tube -> airframe wall
CR_STATIONS = (12.0, 40.0)
CR_R_I = MT_R_O - 0.6         # overlap into the tube wall
CR_R_O = R_AF_I + 0.6         # and into the airframe wall

# Through-the-wall fin slots. Planform from the .ork rev 5: 3 fins, root chord 50.8,
# thickness 2.0, 0 deg clocking. The tab passes through the wall AND through both
# centering rings and lands 0.3 mm off the motor tube, so it bonds to the mount the
# way DESIGN.md 9 asks -- not to the outer skin alone.
FIN_N = 3
FIN_ROOT = 50.8
FIN_T = 2.0
FIN_SLOT_W = FIN_T + 0.3      # 0.15 mm of epoxy per side
FIN_Z0 = 0.6                  # clears the cap's forward rim face at Z 0
FIN_Z1 = FIN_Z0 + FIN_ROOT
FIN_SLOT_R_I = MT_R_O + 0.3   # tab tip stands 0.3 mm off the motor tube, for epoxy
FIN_ANGLES = tuple(360.0 * k / FIN_N for k in range(FIN_N))

# --- the fins themselves, planform from .ork rev 5 -------------------------
FIN_TIP = 25.0                # tip chord
FIN_SPAN = 55.0               # semi-span, root to tip
FIN_SWEEP = 25.4              # LE sweep
FIN_FILLET = 4.0              # root fillet radius, printed in on the fin can
FIN_EDGE_R = FIN_T / 2.0      # 1.0 -- "rounded" cross-section in the .ork
FIN_ROOT_R = 18.0             # planform starts inboard of the wall so the fuse overlaps
FIN_TAB_R = MT_R_O - 0.6      # 9.8 -- tab merges into the motor tube wall
FIN_TIP_R = R_AF_O + FIN_SPAN                     # 76.5
FIN_TIP_Z_LE = FIN_Z1 - FIN_SWEEP                 # 26.0

# body-tube mass this section displaces, at CORRECTED solid-ABS density
TUBE_G_PER_MM = math.pi * (R_AF_O ** 2 - R_AF_I ** 2) * RHO

# --- forward centering ring ---
RING_R_O = 19.85              # OD 39.7
RING_R_I = 10.6               # ID 21.2 -- 0.4 diametral glue gap over the 20.8 tube
RING_T = 3.0

# --- motor (verification only) ---
MOTOR_R = 9.0
MOTOR_L = 70.0
MOTOR_Z0 = EB_Z0 - MOTOR_L    # -14.1  -> 0.4 mm clear of the cap lip
LIP_GAP_NOM = MOTOR_Z0 - CAP_FLOOR_Z

# --- .ork baseline, for the CG report ---
ORK_MASS = 128.0              # g, liftoff on a C6 (Simulation 6)
ORK_CG = 228.0                # mm from the nose tip
ORK_REPLACED = 5.0            # g of cardboard rings + engine block this design replaces
ORK_FINSET = 14.2            # g -- fin set already in the .ork (DESIGN.md 4.5)
CALIBER = 43.0
TUBE_CORR_MASS = 30.0         # DESIGN.md section 3
TUBE_CORR_CG = 210.0          # nose 40 + half of the 340 tube
NOSE_TO_AFT = 380.0           # airframe aft face, from the nose tip

# ------------------------------------------------------------------ helpers


def revolve(pts):
    """Solid of revolution from (r, z) points in the XZ half-plane."""
    vs = [Vector(r, 0, z) for r, z in pts]
    wire = Part.Wire(Part.makePolygon(vs + [vs[0]]))
    return Part.Face(wire).revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)


def thread_solid(helix_r, z_start, height, profile, phase_z=0.0):
    """Helical sweep of a closed (r, dz) profile, built as an exact faceted solid.

    Not makePipeShell. Every OCCT sweep mode was tried against this geometry and all
    of them fail in one of two ways (see build notes):
      - isFrenet=True  : geometry looks right, but every boolean against the result
                         silently returns the other operand, so the thread vanishes.
      - isFrenet=False : booleans work, but the corrected frame drifts -- the measured
                         thread pitch comes out 3.2 mm instead of 3.0, and the parts
                         cannot mate.
      - setAuxiliarySpine / setBiNormalMode : argument-signature errors in this build.

    Generating the helix directly gives exact pitch by construction, planar faces only
    (which OCCT booleans handle reliably), and no frame drift. Faceting error is
    r*(1-cos(pi/STEPS_PER_TURN)) ~ 0.007 mm at the crest, against 0.2 mm of radial
    clearance -- three per cent of the fit.

    phase_z shifts the whole helix; the profile is centred at z_start + phase_z at
    theta = 0, which is what sets the interleave between boss ridge and cap channel.
    """
    z0 = z_start + phase_z
    turns = height / PITCH
    n = max(8, int(round(turns * STEPS_PER_TURN)))
    rings = []
    for i in range(n + 1):
        th = 2.0 * math.pi * turns * i / n
        z = z0 + PITCH * turns * i / n
        ct, st = math.cos(th), math.sin(th)
        rings.append([Vector(r * ct, r * st, z + dz) for r, dz in profile])

    faces = []

    def tri(a, b, c):
        faces.append(Part.Face(Part.Wire(Part.makePolygon([a, b, c, a]))))

    m = len(profile)
    for i in range(n):                      # side walls, split into triangles because
        A, B = rings[i], rings[i + 1]       # a helical quad is not planar
        for j in range(m):
            k = (j + 1) % m
            tri(A[j], A[k], B[k])
            tri(A[j], B[k], B[j])
    for j in range(1, m - 1):               # end caps
        tri(rings[0][0], rings[0][j + 1], rings[0][j])
        tri(rings[n][0], rings[n][j], rings[n][j + 1])

    solid = Part.makeSolid(Part.makeShell(faces))
    if solid.Volume < 0:
        solid.reverse()
    return solid


def groove_profile():
    """The helical channel BETWEEN boss ridges -- cut from a plain BOSS_R_MAJOR annulus.

    Threads are cut, never fused. Sweeping a ridge and fusing it onto the core
    cylinder silently returns just the cylinder in OCCT (the ridge vanishes with no
    error), whether the two merely touch or genuinely overlap.
    """
    w_min = PITCH - (T_CREST_W + 2 * T_DEPTH * T_FLANK)   # 0.714 at the minor r
    w_maj = PITCH - T_CREST_W                             # 2.1   at the major r
    out = BOSS_R_MAJOR + T_MERGE
    return [(BOSS_R_MINOR, -w_min / 2.0), (BOSS_R_MAJOR, -w_maj / 2.0),
            (out, -w_maj / 2.0), (out, w_maj / 2.0),
            (BOSS_R_MAJOR, w_maj / 2.0), (BOSS_R_MINOR, w_min / 2.0)]


def channel_profile():
    """The cap's helical channel: the boss ridge grown by the running clearances.

    Cut from a bore already opened to CAP_T_CREST_R, what is left standing between
    passes of this channel is the cap's internal thread.
    """
    w_root = (T_CREST_W + 2 * T_DEPTH * T_FLANK) + 2 * FLANK_CLEAR   # at CAP_T_CREST_R
    w_crest = T_CREST_W + 2 * FLANK_CLEAR                            # at CAP_T_ROOT_R
    inn = CAP_T_CREST_R - T_MERGE
    out = CAP_T_ROOT_R + T_MERGE
    return [(inn, -w_root / 2.0), (CAP_T_CREST_R, -w_root / 2.0),
            (CAP_T_ROOT_R, -w_crest / 2.0), (out, -w_crest / 2.0),
            (out, w_crest / 2.0), (CAP_T_ROOT_R, w_crest / 2.0),
            (CAP_T_CREST_R, w_root / 2.0), (inn, w_root / 2.0)]


def as_solid(shape):
    """Unwrap a compound to a single solid.

    Both Shape.read() (STEP round-trip) and removeSplitter() hand back a compound
    even for a one-solid part, and a compound has no CenterOfMass.
    """
    solids = shape.Solids
    if not solids:
        return shape
    if len(solids) == 1:
        return solids[0]
    return solids[0].multiFuse(solids[1:]).Solids[0]


def heal(shape, tag, log):
    """STEP round-trip + removeSplitter + fixTolerance.

    Swept-thread boolean cuts leave degenerate sliver faces (a known OCCT artifact);
    this is built in from the start rather than patched afterwards. Part.Shape.check(True)
    is deliberately NOT called -- SampleRocketABS33-36 records it pegging the CPU for
    10+ minutes and needing FreeCAD killed.
    """
    before = len(shape.Faces)
    if before > 500:
        # Faceted-thread parts. The STEP round-trip and removeSplitter below exist to
        # clean the sliver faces a SWEPT thread leaves behind; the faceted helix leaves
        # none, and on a few thousand planar faces both passes run for 20+ minutes
        # (removeSplitter is the "Checking topology" spinner). Nothing to gain, so skip.
        shape = as_solid(shape)
        log.append("  heal %-17s faces %d (faceted -- heal skipped), solids %d, %.1f mm3"
                   % (tag, before, len(shape.Solids), shape.Volume))
        return shape
    tmp = os.path.join(tempfile.gettempdir(), "heal_%s.step" % tag)
    try:
        shape.exportStep(tmp)
        rt = Part.Shape()
        rt.read(tmp)
        os.remove(tmp)
        shape = rt
    except Exception as exc:
        log.append("  ! %s: STEP round-trip skipped (%s)" % (tag, exc))
    shape = shape.removeSplitter()
    shape = as_solid(shape)
    shape.fixTolerance(1e-7)
    log.append("  heal %-17s faces %d -> %d, solids %d, %.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape

# ------------------------------------------------------------------- builds


def build_base():
    """Threaded boss + conical seat + spigot + motor tube + engine block, one solid."""
    # boss shell at full major diameter, then the thread grooves cut out of it
    # runs BOSS_MERGE past BOSS_Z_TOP so it overlaps the hub rather than butting it;
    # the hub is wider than BOSS_R_MAJOR up there, so nothing protrudes
    boss_top = BOSS_Z_TOP + WEB_MERGE
    boss = revolve([(BOSS_CORE_R, BOSS_Z_TIP), (BOSS_R_MAJOR, BOSS_Z_TIP),
                    (BOSS_R_MAJOR, boss_top), (BOSS_CORE_R, boss_top)])
    turns_h = (boss_top - T_ANCHOR) + PITCH
    boss = boss.cut(thread_solid(BOSS_R_MINOR, T_ANCHOR, turns_h,
                                 groove_profile(), phase_z=PITCH / 2.0))

    # 45 deg lead-in chamfer at the aft tip, truncating the first turn.
    # The tool is a single cone (r = z - BOSS_Z_TIP + r0) with every vertex placed
    # clear of the boss. A tool bounded by r = BOSS_R_MINOR instead puts a face
    # exactly coincident with the boss's minor cylinder, and OCCT returns a null
    # shape from that boolean.
    r0 = BOSS_R_MAJOR - BOSS_TIP_CHAMFER
    z_lo = BOSS_Z_TIP - 6.0
    r_lo = z_lo - BOSS_Z_TIP + r0
    r_hi = 30.0
    z_hi = BOSS_Z_TIP + (r_hi - r0)
    boss = boss.cut(revolve([(r_lo, z_lo), (r_hi, z_hi), (r_hi, z_lo)]))

    # conical seat + flange + spigot hub
    hub = revolve([
        (BOSS_CORE_R, SEAT_Z0),
        (BOSS_R_MAJOR, SEAT_Z0),
        (R_AF_O, SEAT_Z1),
        (SPIGOT_R_O, SEAT_Z1),
        (SPIGOT_R_O, SPIGOT_Z1),
        (SPIGOT_R_I, SPIGOT_Z1),
        (SPIGOT_R_I, SPIGOT_INNER_CONE_Z),
    ])

    # motor tube with the engine-block shoulder bored in
    tube = revolve([
        (MT_R_I, MT_Z0), (MT_R_O, MT_Z0), (MT_R_O, MT_Z1),
        (EB_R, MT_Z1), (EB_R, EB_CONE_Z1), (EB_LEDGE_R, EB_Z0), (MT_R_I, EB_Z0),
    ])

    # 45 deg conical web, motor tube -> boss shell
    dz = WEB_T * math.sqrt(2.0)
    wi, wo = MT_R_O - WEB_MERGE, BOSS_CORE_R + WEB_MERGE
    zi, zo = WEB_Z_IN - WEB_MERGE, WEB_Z_OUT + WEB_MERGE
    web = revolve([(wi, zi), (wo, zo), (wo, zo - dz), (wi, zi - dz)])

    return boss.fuse(hub).fuse(tube).fuse(web)


def build_sealed_section(slots=True):
    """The sealed aft airframe section.

    Same boss, thread and seat cone as cfg A, but this part IS the aft airframe: real
    43/40 wall, through-the-wall fin slots, integral centering rings, a solid bulkhead
    on the motor's forward face, and a forward lip the forward tube epoxies over.
    Nothing on the part reaches forward of the bulkhead face.
    """
    boss_top = BOSS_Z_TOP + WEB_MERGE
    boss = revolve([(BOSS_CORE_R, BOSS_Z_TIP), (BOSS_R_MAJOR, BOSS_Z_TIP),
                    (BOSS_R_MAJOR, boss_top), (BOSS_CORE_R, boss_top)])
    turns_h = (boss_top - T_ANCHOR) + PITCH
    boss = boss.cut(thread_solid(BOSS_R_MINOR, T_ANCHOR, turns_h,
                                 groove_profile(), phase_z=PITCH / 2.0))
    r0 = BOSS_R_MAJOR - BOSS_TIP_CHAMFER
    z_lo = BOSS_Z_TIP - 6.0
    boss = boss.cut(revolve([(z_lo - BOSS_Z_TIP + r0, z_lo),
                             (30.0, BOSS_Z_TIP + (30.0 - r0)), (30.0, z_lo)]))

    # Wall and lip are ONE wall: the bore steps inward over TENON_TAPER just below the
    # shoulder, so the lip is continuous structure rather than a ring fused on top.
    wall = revolve([
        (BOSS_CORE_R, SEAT_Z0), (BOSS_R_MAJOR, SEAT_Z0),
        (R_AF_O, SEAT_Z1), (R_AF_O, SHOULDER_Z),
        (TENON_R_O, SHOULDER_Z),                   # shoulder -- fwd tube lands here
        (TENON_R_O, SEC_Z1), (TENON_R_I, SEC_Z1),
        (TENON_R_I, SHOULDER_Z),
        (R_AF_I, SHOULDER_Z - TENON_TAPER),        # bore tapers back out to 40.0
        (R_AF_I, SEAT_Z1),
    ])

    # plain motor tube -- the bulkhead is the thrust stop, and the motor's whole 18 mm
    # forward face bears on it, so no engine-block ring is needed
    tube = revolve([
        (MT_R_I, MT_Z0), (MT_R_O, MT_Z0),
        (MT_R_O, MT_SEALED_Z1), (MT_R_I, MT_SEALED_Z1),
    ])

    dz = WEB_T * math.sqrt(2.0)
    wi, wo = MT_R_O - WEB_MERGE, BOSS_CORE_R + WEB_MERGE
    zi, zo = WEB_Z_IN - WEB_MERGE, WEB_Z_OUT + WEB_MERGE
    web = revolve([(wi, zi), (wo, zo), (wo, zo - dz), (wi, zi - dz)])

    part = boss.fuse(wall).fuse(tube).fuse(web)

    for z in CR_STATIONS:
        part = part.fuse(revolve([(CR_R_I, z), (CR_R_O, z),
                                  (CR_R_O, z + CR_T), (CR_R_I, z + CR_T)]))

    # sealed bulkhead -- SOLID disc, no bore, integral with the lip wall. Its forward
    # face at SEC_Z1 is the forward-most plane of the entire part.
    part = part.fuse(revolve([(0.0, BH_Z0), (BH_R, BH_Z0),
                              (BH_R, BH_Z1), (0.0, BH_Z1)]))

    if not slots:
        return part

    # through-the-wall fin slots: cut the wall AND both centering rings, stopping
    # 0.3 mm off the motor tube so the tab bonds to the mount, not just the skin
    for a in FIN_ANGLES:
        box = Part.makeBox(24.0 - FIN_SLOT_R_I, FIN_SLOT_W, FIN_Z1 - FIN_Z0,
                           Vector(FIN_SLOT_R_I, -FIN_SLOT_W / 2.0, FIN_Z0))
        box.rotate(Vector(0, 0, 0), Vector(0, 0, 1), a)
        part = part.cut(box)
    return part


def _fin_outline(shrink):
    """Planform polygon pulled in by `shrink` all round; shrink 0 is the mid-plane.

    True edge offset -- each edge line is moved inward by `shrink` and consecutive
    lines re-intersected. A bisector approximation is not good enough here: the
    planform has a 24-degree corner at the tip trailing edge, where the bisector step
    is 5x the perpendicular one, and the polygon inverts.
    """
    pts = [(FIN_ROOT_R, FIN_Z1), (FIN_TIP_R, FIN_TIP_Z_LE),
           (FIN_TIP_R, FIN_TIP_Z_LE - FIN_TIP), (FIN_ROOT_R, FIN_Z0)]
    if shrink <= 1e-9:
        return pts
    n = len(pts)
    area = 0.5 * sum(pts[k][0] * pts[(k + 1) % n][1] - pts[(k + 1) % n][0] * pts[k][1]
                     for k in range(n))
    sgn = 1.0 if area > 0 else -1.0          # interior is left of each edge when CCW
    lines = []
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ez)
        nx, nz = -ez / L * sgn, ex / L * sgn
        lines.append((a[0] + nx * shrink, a[1] + nz * shrink, ex, ez))
    out = []
    for k in range(n):
        x1, z1, dx1, dz1 = lines[k - 1]
        x2, z2, dx2, dz2 = lines[k]
        den = dx1 * dz2 - dz1 * dx2
        t = ((x2 - x1) * dz2 - (z2 - z1) * dx2) / den
        out.append((x1 + dx1 * t, z1 + dz1 * t))
    return out


def _wire_at(y, shrink):
    vs = [Vector(r, y, z) for r, z in _fin_outline(shrink)]
    return Part.Wire(Part.makePolygon(vs + [vs[0]]))


def build_fin(angle_deg, with_tab=True):
    """One fin: swept trapezoid, 2 mm thick, edges rounded to a 1 mm radius.

    The round is a four-step loft rather than a fillet -- OCCT fillets on a lofted
    swept plate are exactly the operation that has failed repeatedly in this file, and
    at Mach 0.28 the edge profile is cosmetic anyway (DESIGN.md 6).
    """
    fr = [(-1.000, 1.000), (-0.707, 0.293), (0.0, 0.0), (0.707, 0.293), (1.000, 1.000)]
    wires = [_wire_at(f * FIN_EDGE_R, sh * FIN_EDGE_R) for f, sh in fr]
    fin = Part.makeLoft(wires, True, True)   # ruled: flat facets, predictable
    if with_tab:
        # runs out to the wall ID so it OVERLAPS the plate rather than butting it at
        # FIN_ROOT_R -- butting leaves a two-solid fin whose mesh has open edges
        tab = Part.makeBox(R_AF_I - FIN_TAB_R, FIN_T, FIN_Z1 - FIN_Z0,
                           Vector(FIN_TAB_R, -FIN_T / 2.0, FIN_Z0))
        fin = fin.fuse(tab)
    fin.rotate(Vector(0, 0, 0), Vector(0, 0, 1), angle_deg)
    return fin


def build_fin_fillets(angle_deg):
    """Both root-fillet lobes for one fin, as an extrusion along Z.

    Constructed, not filleted: a box minus the airframe cylinder minus a FIN_FILLET
    cylinder tangent to both the fin face and the airframe. All cylinders and boxes,
    which OCCT handles reliably.
    """
    cy = FIN_T / 2.0 + FIN_FILLET
    cx = math.sqrt((R_AF_O + FIN_FILLET) ** 2 - cy ** 2)
    h = FIN_Z1 - FIN_Z0
    out = None
    for sgn in (1.0, -1.0):
        y0 = min(sgn * (FIN_T / 2.0), sgn * cy)
        box = Part.makeBox(cx - (R_AF_O - 1.5), abs(cy) - FIN_T / 2.0, h,
                           Vector(R_AF_O - 1.5, y0, FIN_Z0))
        lobe = box.cut(Part.makeCylinder(R_AF_O, h + 2.0, Vector(0, 0, FIN_Z0 - 1.0)))
        lobe = lobe.cut(Part.makeCylinder(FIN_FILLET, h + 2.0,
                                          Vector(cx, sgn * cy, FIN_Z0 - 1.0)))
        out = lobe if out is None else out.fuse(lobe)
    out.rotate(Vector(0, 0, 0), Vector(0, 0, 1), angle_deg)
    return out


def build_fin_can():
    """One-piece aft section with the fins printed in -- DESIGN.md 9's fin can."""
    part = build_sealed_section(slots=False)
    for a in FIN_ANGLES:
        part = part.fuse(build_fin(a))
        part = part.fuse(build_fin_fillets(a))
    return part


def build_cap():
    """Screw-off cap: mouth cone, internal thread, exhaust bore, grip ribs."""
    blank = revolve([
        (0.0, CAP_Z_TIP), (CAP_R_O, CAP_Z_TIP),
        (CAP_R_O, CAP_Z_TOP - CAP_TOP_CHAMFER),
        (CAP_R_O - CAP_TOP_CHAMFER, CAP_Z_TOP), (0.0, CAP_Z_TOP),
    ])

    # counterbore to the thread root, plus the 45 deg mouth cone
    cavity = revolve([
        (0.0, CAP_FLOOR_Z),
        (CAP_T_CREST_R, CAP_FLOOR_Z),      # thread span is bored to the crest...
        (CAP_T_CREST_R, CAP_T_TOP_Z),
        (CAP_T_ROOT_R, CAP_T_TOP_Z),       # ...then plain to the root above it
        (CAP_T_ROOT_R, CAP_SEAT_Z1),
        (R_AF_O, CAP_Z_TOP),
        (0.0, CAP_Z_TOP),
    ])
    # exhaust bore + 45 deg aft flare
    bore = revolve([
        (0.0, CAP_Z_TIP - 1.0), (CAP_FLARE_R, CAP_Z_TIP - 1.0), (CAP_FLARE_R, CAP_Z_TIP),
        (CAP_BORE_R, CAP_BORE_Z), (CAP_BORE_R, CAP_FLOOR_Z + 1.0), (0.0, CAP_FLOOR_Z + 1.0),
    ])
    cap = blank.cut(cavity).cut(bore)

    # internal thread: cut the channel the boss's ridge runs in. Same T_ANCHOR and
    # zero phase as the boss ridges, so the two interleave exactly when seated.
    h = (CAP_T_TOP_Z - T_ANCHOR) + PITCH
    inn = CAP_T_CREST_R - T_MERGE
    out = CAP_T_ROOT_R + T_MERGE
    channel = thread_solid(CAP_T_CREST_R, T_ANCHOR, h, channel_profile())
    channel = channel.common(revolve([
        (inn, CAP_FLOOR_Z), (out, CAP_FLOOR_Z),
        (out, CAP_T_TOP_Z), (inn, CAP_T_TOP_Z)]))
    cap = cap.cut(channel)

    # grip ribs
    d = CAP_R_O + RIB_PROUD - RIB_CUT_R
    keepout = Part.makeCylinder(RIB_KEEPOUT_R, (RIB_Z1 - RIB_Z0) + 4.0,
                                Vector(0, 0, RIB_Z0 - 2.0))
    for i in range(RIB_N):
        a = 2 * math.pi * i / RIB_N
        rib = Part.makeCylinder(RIB_CUT_R, RIB_Z1 - RIB_Z0,
                                Vector(d * math.cos(a), d * math.sin(a), RIB_Z0))
        cap = cap.fuse(rib.cut(keepout))
    return cap


def build_ring():
    return revolve([(RING_R_I, 0.0), (RING_R_O, 0.0),
                    (RING_R_O, RING_T), (RING_R_I, RING_T)])


def build_motor():
    return Part.makeCylinder(MOTOR_R, MOTOR_L, Vector(0, 0, MOTOR_Z0))

# ------------------------------------------------------------- verification


def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01,
                                  AngularDeflection=0.1, Relative=False)


def main():
    log = []
    log.append("=" * 78)
    log.append("Phoenix ABS 40-43 -- aft motor retention, %s" % REV)
    log.append("=" * 78)

    doc = App.newDocument("PhoenixABS40-43_aft_retention")

    log.append("")
    log.append("[1] build + heal")
    raw = [
        ("AftRetainerBase", build_base()),
        ("MotorRetainerCap", build_cap()),
        ("FwdCenteringRing", build_ring()),
        ("AftSectionSealed", build_sealed_section()),
        ("Fin", build_fin(0.0)),
        ("AftFinCan", build_fin_can()),
    ]
    parts = [(n, heal(s, n, log)) for n, s in raw]
    by_name = dict(parts)
    motor = build_motor()

    log.append("")
    log.append("[2] per-solid mass + envelope")
    # Envelope comes from the mesh, not Shape.BoundBox: OCCT's box for a swept
    # helical face is the control-point hull, which reads ~13 mm oversize here.
    meshes = dict((name, mesh_of(shape)) for name, shape in parts)
    total = 0.0
    masses = {}
    for name, shape in parts:
        m = shape.Volume * RHO
        masses[name] = m
        total += m
        bb = meshes[name].BoundBox
        log.append("  %-17s %9.1f mm3 %6.2f g  dia %5.1f  Z %6.1f..%5.1f  solids %d"
                   % (name, shape.Volume, m, max(bb.XLength, bb.YLength),
                      bb.ZMin, bb.ZMax, len(shape.Solids)))
    pair = masses["AftRetainerBase"] + masses["MotorRetainerCap"]
    log.append("  %-17s %6.2f g  (target <= 22 g)  %s"
               % ("cfg A cap+base:", pair, "PASS" if pair <= 22.0 else "OVER"))
    log.append("  %-17s %6.2f g  cap + sealed section"
               % ("cfg B cap+sect:", masses["AftSectionSealed"] + masses["MotorRetainerCap"]))

    log.append("")
    log.append("[3] watertight (mesh vs CAD solid)")
    for name, shape in parts:
        msh = meshes[name]
        err = abs(msh.Volume - shape.Volume) / shape.Volume * 100.0
        # boundary edges by Euler: a closed triangle mesh has 3F = 2E
        open_e = 2 * msh.CountEdges - 3 * msh.CountFacets
        ok = (open_e == 0 and msh.isSolid() and not msh.hasNonManifolds()
              and err < 0.1)
        log.append("  %-17s %6d facets  vol err %.4f%%  open edges %d  solid %-5s  %s"
                   % (name, msh.CountFacets, err, open_e, str(msh.isSolid()),
                      "PASS" if ok else "CHECK"))

    log.append("")
    log.append("[4] thread + fit -- checked by Models/verify_aft_retention.py")
    # NOT checked here. OCCT booleans against a threaded solid are not trustworthy in
    # this build: Shape.common() returns 0 mm3 for parts that plainly interfere, and
    # material fill fractions come back as 147% or -24%. Every geometric claim about
    # the thread is made by ray casting the exported STLs instead. Run:
    #     python Models/verify_aft_retention.py
    log.append("  boss thread  major %.1f / minor %.1f, pitch %.1f, single-start RH"
               % (BOSS_R_MAJOR * 2, BOSS_R_MINOR * 2, PITCH))
    log.append("  cap thread   crest %.1f / root  %.1f, %.1f radial / %.1f flank clearance"
               % (CAP_T_CREST_R * 2, CAP_T_ROOT_R * 2, RAD_CLEAR, FLANK_CLEAR))
    log.append("  engagement   %.1f mm full thread; boss tip -> cap floor %.1f mm"
               % ((BOSS_Z_TOP - BOSS_Z_TIP) - BOSS_TIP_CHAMFER,
                  abs(CAP_FLOOR_Z - BOSS_Z_TIP)))
    log.append("  seat cone    r %.1f->%.1f over Z %.1f->%.1f; both parts on r = z + %.1f"
               % (BOSS_R_MAJOR, R_AF_O, SEAT_Z0, SEAT_Z1, R_AF_O))

    log.append("")
    log.append("[5] motor bay geometry (clearances ray-cast by the verifier)")
    log.append("  motor Z %.1f .. %.1f (%.1f mm long)"
               % (MOTOR_Z0, MOTOR_Z0 + MOTOR_L, MOTOR_L))
    # Motor clearance is ray-cast in verify_aft_retention.py, not booleaned here --
    # Shape.common() against the faceted-thread solids throws outright.
    log.append("  motor aft face -> cap lip   %9.3f mm   %s (want 0.4 +/- 0.1)"
               % (LIP_GAP_NOM, "PASS" if abs(LIP_GAP_NOM - 0.4) <= 0.1 else "FAIL"))
    log.append("  retaining lip r %.1f..%.1f = %.1f mm radial on the casing rim"
               % (CAP_BORE_R, MOTOR_R, MOTOR_R - CAP_BORE_R))
    log.append("  ring ID %.1f over tube OD %.1f = %.1f mm diametral glue gap"
               % (RING_R_I * 2, MT_R_O * 2, (RING_R_I - MT_R_O) * 2))

    log.append("")
    log.append("[6] mass + CG vs the .ork baseline (%.0f g @ %.0f mm)" % (ORK_MASS, ORK_CG))
    cm = dict((n, sh.CenterOfMass.z) for n, sh in parts)

    def config(label, bodies, displaced_g, note):
        m = sum(masses[b] for b in bodies)
        c = sum((NOSE_TO_AFT - cm[b]) * masses[b] for b in bodies) / m
        added = m - displaced_g
        m1 = ORK_MASS + added
        cg1 = (ORK_MASS * ORK_CG + added * c) / m1
        log.append("  %s" % label)
        log.append("    parts %.2f g at %.1f mm, less %.2f g displaced (%s)"
                   % (m, c, displaced_g, note))
        log.append("    net %+.2f g -> CG %.1f mm (%+.1f mm, %.2f cal)"
                   % (added, cg1, cg1 - ORK_CG, (cg1 - ORK_CG) / CALIBER))
        m2 = m1 + TUBE_CORR_MASS
        cg2 = (m1 * cg1 + TUBE_CORR_MASS * TUBE_CORR_CG) / m2
        log.append("    + DESIGN.md s3 tube corr. -> CG %.1f mm (%+.1f mm, %.2f cal)"
                   % (cg2, cg2 - ORK_CG, (cg2 - ORK_CG) / CALIBER))

    config("cfg A -- bonded insert into a separate airframe",
           ["AftRetainerBase", "MotorRetainerCap", "FwdCenteringRing"],
           ORK_REPLACED, "cardboard rings + engine block")
    # only the FULL-OD wall displaces body tube; the lip above SHOULDER_Z sits inside
    # the forward tube, which still runs all the way down to the shoulder
    tube_disp = SHOULDER_Z * TUBE_G_PER_MM
    config("cfg B -- sealed aft section + 3 bonded fins",
           ["AftSectionSealed", "MotorRetainerCap", "Fin", "Fin", "Fin"],
           ORK_REPLACED + tube_disp + ORK_FINSET,
           "rings/block + %.1f mm of tube + the .ork fin set" % SHOULDER_Z)
    config("cfg C -- one-piece fin can (fins printed in)",
           ["AftFinCan", "MotorRetainerCap"],
           ORK_REPLACED + tube_disp + ORK_FINSET,
           "rings/block + %.1f mm of tube + the .ork fin set" % SHOULDER_Z)
    log.append("  -> the fin resize must recover this ON TOP of DESIGN.md s4's ~1.0 cal")
    log.append("  overall length 380.0 -> %.1f mm (cap protrudes %.1f)"
               % (NOSE_TO_AFT - CAP_Z_TIP, -CAP_Z_TIP))

    log.append("")
    log.append("[7] export")
    for name, shape in parts:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        shape.exportStep(os.path.join(
            MODELS, "PhoenixABS40-43_%s_%s.step" % (name, REV)))
        meshes[name].write(os.path.join(
            PRINTS, "PhoenixABS40-43_%s_%s.stl" % (name, REV)))
        log.append("  %s .step + .stl" % name)
    doc.recompute()
    doc.saveAs(os.path.join(MODELS, "PhoenixABS40-43_aft_retention_%s.FCStd" % REV))
    log.append("  PhoenixABS40-43_aft_retention_%s.FCStd" % REV)

    report = "\n".join(log)
    print(report)
    with open(os.path.join(MODELS, "build_report_%s.txt" % REV), "w") as fh:
        fh.write(report + "\n")


main()

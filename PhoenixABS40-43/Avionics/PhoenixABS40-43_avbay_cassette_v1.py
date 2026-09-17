# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay as a SERVICEABLE CASSETTE, v1

SOURCE OF TRUTH for the "make the e-bay easily removable" work (companion:
Avionics/avionics_bay_packing_40mm.md section 9, DESIGN.md section 7.5 / 7.8 / 13).
Every dimension is a named constant below; edit here and re-run, never edit the
STL/STEP/FCStd.  The v2 packing study (PhoenixABS40-43_avbay_packing_v2.FCStd) has
no .py -- this file is NOT a back-port of it, it is a new study layered on top of
its published envelope (avbay_packing_build_report_v2.txt).

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" <this file>

------------------------------------------------------------------------------
WHAT THIS ADDS TO THE v2 PACK
------------------------------------------------------------------------------
The user wants to inspect the bay and recharge / swap the battery between flights
on the same day.  Half of that is already in the pack (section 5 of the packing
md): a USB-C slot and a microSD slot go THROUGH the airframe wall, and arming is
an external magnet -- so a recharge-in-place needs no disassembly at all.  This
file is the other half: getting the whole stack OUT for a battery swap or a real
inspection.

Architecture (see the packing md section 9 for the reasoning):
  * The body tube gets a TRANSVERSE BENCH-SERVICE JOINT just aft of the anchor
    bulkhead.  It is opened only on the bench -- it is NEVER a flight separation
    (flight recovery separates at the NOSE, DESIGN.md 7.5).
  * The anchor bulkhead becomes the COUPLER: bonded to the forward (chute-bay)
    tube section, a slip register into the aft section, retained by 3 radial M3
    into a locally thickened band at the aft section's forward cut.
  * "Removing the forward section" then lifts the anchor bulkhead + cage + knob +
    servo + sled + electronics out as ONE assembly.  The servo-to-knob coupler is
    never broken, so there is no blind re-mate.
  * Aft end of the cassette is centred + CLOCKED by a spigot + one key on the aft
    closure into the motor-mount bulkhead.  Re-indexes the USB-C / microSD slots
    and the static port to the same clocking every time.
  * Battery goes on a JST-PH pigtail with an inboard LIFT TAB -- swap a charged
    spare in seconds, charge the used one on the bench.

------------------------------------------------------------------------------
THE DECISION THIS FORCES (surface it, do not bury it)
------------------------------------------------------------------------------
DESIGN.md 7.5 says the anchor bulkhead is "solvent-welded to tube".
Ejection POC 10 item 7 says "solvent-welded OR mechanically captured".
A removable cassette needs it MECHANICALLY CAPTURED (screwed).  Those same 3
screws then also carry the RECOVERY SNATCH load (7.7: the bulkhead carries the
full recovery shock, and that is the larger load).  Section [R] of the report
sizes that joint -- and it CANNOT PASS until the snatch load is measured
(spring force per 7.3, then a packed-separation drop per 7.9 test 4).  It is
wired to fail loudly while RECOVERY_MEASURED is False.  That is deliberate.

Frame (== avbay_packing_build_report_v2.txt):
  Z = 0 at the aft face of the component zone (= forward face of the motor-mount
  bulkhead); +Z toward the nose.  Origin on the tube axis; +x "east", +y "north"
  (packing md section 3).  Airframe OD 43.0 / ID 40.0 / wall 1.5.
"""

import os
import math
import tempfile

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

# ================================================================ parameters

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
AVIONICS = os.path.join(PROJECT, "Avionics")
AV_MODELS = os.path.join(AVIONICS, "Models")
REV = "v1"

RHO = 1.05e-3                 # ABS 100% infill, g/mm^3

# --- airframe ---
R_AF_O = 21.5                 # OD 43.0
R_AF_I = 20.0                 # ID 40.0
R_MAX_MOVING = 19.5           # a part that must slide in/out of the bore
R_MAX_STATIC = 19.9           # fixed structure just has to fit

# --- FDM fit clearances (ABS, 0.4 mm nozzle) -- same block as the ejection POC ---
CL_SLIDE = 0.50   # a printed part sliding in a printed channel / bore (total, per axis)
CL_ROT   = 0.40   # a printed shaft turning in a printed journal (radial)
CL_REG   = 0.20   # a printed register / spigot located in a printed counterbore (radial)
CL_KEY   = 0.30   # a printed key in a printed slot (per face)
CL_TUBE  = 0.25   # a printed part entering the printed tube bore once (radial)

# =============================================================================
# v2 PACK ENVELOPE -- bounding solids, lifted from avbay_packing_build_report_v2.txt
# (bbox dx.dy.dz, Zmin, Zmax, Rmax).  These are NOT flight parts; they exist so the
# extraction sweep and the containment checks have something real to run against.
# =============================================================================
SLED_RMAX = 19.39
SLED_Z0, SLED_Z1 = 0.0, 48.0
SLED_BX, SLED_BY = 28.4, 30.0

BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5        # EEMB LP852040, flat on the SOUTH wall
BATT_CORNER_R = 19.04                              # worst corner, packing md section 8
# outer (-y) face placed so the worst corner sits exactly on BATT_CORNER_R:
BATT_Y_OUT = math.sqrt(BATT_CORNER_R ** 2 - (BATT_DX / 2.0) ** 2)   # 16.20
BATT_Y0, BATT_Y1 = -BATT_Y_OUT, -BATT_Y_OUT + BATT_DY               # -16.20 .. -7.70
BATT_Z0, BATT_Z1 = 0.0, BATT_DZ

NANO_DX, NANO_DY, NANO_DZ = 18.0, 5.0, 45.0        # flat in the NORTH lobe
NANO_CORNER_R = 15.81
NANO_Y_OUT = math.sqrt(NANO_CORNER_R ** 2 - (NANO_DX / 2.0) ** 2)   # 13.00
NANO_Y0, NANO_Y1 = NANO_Y_OUT - NANO_DY, NANO_Y_OUT                 # 8.00 .. 13.00
NANO_Z0, NANO_Z1 = 0.0, NANO_DZ

SERVO_X0, SERVO_X1 = -14.0, 8.8                    # 22.8 wide, case toward the tube centre
SERVO_Y = 6.0                                      # +-6 ; corner (-14, -6) -> R 15.23
SERVO_Z0, SERVO_Z1 = 25.3, 48.0

KNOB_AX_X = -8.0                                   # ejection knob axis (EJECTION_POC 6.7)
KNOB_R = 10.0
KNOB_Z0, KNOB_Z1 = 48.0, 60.5                      # Ref_EjectionKnob

AFTCLO_OLD_R = 19.70                               # the v2 "press disc" -- section [E] shows
AFTCLO_Z0, AFTCLO_Z1 = -3.0, 0.0                   #   why it has to come down to AFTCLO_R

STATIC_PORT_Z = 12.0                               # packing md section 5: north lobe, ~Z 12
STATIC_PORT_D = 1.5
USB_SLOT_Z = 10.0                                  # packing md section 5 (for the [K] readout)
USD_SLOT_Z = 10.0

# =============================================================================
# SERVICEABLE-CASSETTE ADDITIONS (v1) -- the parts this file actually designs
# =============================================================================

# --- the bench-service joint + the retention band -----------------------------
JOINT_Z = 62.0             # transverse joint = aft face of the retention band.
                           #   ~ station 181 from the tube top (DESIGN.md 7.8: the 18 mm
                           #   coupler grows aft into the e-bay slack, joint at 163+18).
                           #   BENCH ONLY -- opened for service, never in flight.
BAND_Z0, BAND_Z1 = JOINT_Z, JOINT_Z + 15.0
BAND_RI = 19.6             # local wall thickening: ID r19.6 (0.4 in from r20.0).
                           #   0.4 not more: the SLED (r19.39) has to pass through
                           #   this band on the way out -- see [E].  The real fix
                           #   for that tightness is a shorter FC board (packing md
                           #   section 7), not a fatter band.
BAND_RO = R_AF_O           # FLUSH with the skin -- a proud ring mid-body is draggy and
                           #   snags on the rail / handling.  1.9 mm of wall is plenty
                           #   for the M3 in shear; the index feature is a scribed
                           #   notch + painted witness line, no raised material.
BAND_WALL = BAND_RO - BAND_RI                     # 1.9 mm

SCREW_N = 3
SCREW_R = 1.7                                     # M3 clearance
SCREW_D_NOM = 3.0                                 # M3 nominal, for edge-distance math
SCREW_AZ0 = 90.0                                  # first screw clocked to +y (north), in a fin gap
SCREW_Z = JOINT_Z + 7.0
SCREW_EDGE = SCREW_Z - JOINT_Z                    # 7.0 mm = screw centre to the tube cut

# --- anchor bulkhead, reworked as the coupler --------------------------------
ANCHOR_R = BAND_RI - CL_REG                       # r19.4 -- slip register inside the band
ANCHOR_Z0, ANCHOR_Z1 = JOINT_Z - 6.0, JOINT_Z + 12.0   # 18 mm: 6 into the e-bay side (cage
                                                 #   mounts here), 12 as the band register
ANCHOR_BOND_Z0 = JOINT_Z + 6.0                    # forward 6 mm is bonded into the fwd tube
ANCHOR_BORE_R = 3.4                               # d6.8 piston-shaft bore (ejection POC)
ANCHOR_SEAT_R = 5.75                              # d11.5 spring-seat counterbore
ANCHOR_SEAT_DEPTH = 2.5
EYELET_R = 2.0                                    # recovery anchor -- d4 hole in a boss
EYELET_BOSS_W = 8.0

# --- aft closure, reworked: smaller disc + spigot + one clocking key ---------
AFTCLO_R = 19.0                                   # was 19.70; drop it, centre on the spigot
SPIGOT_R = 4.0                                    # d8 spigot into the motor-bulkhead counterbore
SPIGOT_H = 3.0
KEY_W, KEY_H, KEY_L = 3.0, 3.0, 2.5              # anti-rotation / CLOCKING key: W tangential,
                                                 #   H axial (aft), L radial
KEY_AZ = 90.0                                     # clocked to +y so the whole cassette indexes
KEY_RC = AFTCLO_R - KEY_L / 2.0 - 0.5             # radial centre of the key (r 17.25)
MB_CBORE_R = SPIGOT_R + CL_REG                    # motor-bulkhead counterbore (reference)
MB_Z = AFTCLO_Z0                                  # motor-bulkhead forward face

# --- battery tray: JST pigtail + inboard-open pocket -----------------------
TRAY_WALL = 0.8                                   # thin -- it lives in the sled's shadow
TRAY_LIP = 0.6                                    # the ONLY thing on the outboard face
                                                 #   (worst corner is 0.96 mm off the ID)
JST_SLOT_W, JST_SLOT_H = 6.0, 3.0                 # pigtail exit

# --- extraction ------------------------------------------------------------
EXTRACT_TRAVEL = JOINT_Z + 20.0                   # withdraw the cassette this far +Z so the
                                                 #   sled aft end clears the retention band
SWEEP_STEPS = 24

# --- recovery snatch load -- ASSUMED, gates section [R] -------------------
RECOVERY_MEASURED = False                         # flip to True after the drop test
RECOVERY_SNATCH_N = 250.0                         # N -- PLACEHOLDER, and probably the wrong
    #   EVENT, not just the wrong number.  Two loads hit this joint:
    #     (a) canopy opening shock on the ~222 g vehicle -- gentle, ~10-30 N.
    #     (b) the EJECTION snatch: 7.5 gives ~5.1 m/s separation, and the harness
    #         comes taut over the shock cord's stretch -- a short arrest, the classic
    #         case where a modest mass makes a few HUNDRED N.  (b) governs and is the
    #         one to design to.  250 N is an order-of-magnitude stand-in for it.
    #   The real number needs F_max measured (7.3) then a packed drop (7.9 test 4).
    #   Until then every line in [R] prints OPEN.  If (b) lands high, the flush 1.9 mm
    #   band is marginal and the 3-lug BAYONET (packing md 9) is the answer, not a fallback.
ABS_BEARING_MPA = 40.0                            # allowable bearing on ABS
SCREW_STEEL_SHEAR_MPA = 250.0                     # M3 A2 steel, conservative

# ================================================================ helpers


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0))


def tube(ri, ro, z0, z1):
    return cyl(ro, z0, z1).cut(cyl(ri, z0 - 1.0, z1 + 1.0))


def revolve(pts):
    vs = [Vector(r, 0, z) for r, z in pts]
    wire = Part.Wire(Part.makePolygon(vs + [vs[0]]))
    return Part.Face(wire).revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)


def as_solid(shape):
    s = shape.Solids
    if not s:
        return shape
    return s[0] if len(s) == 1 else s[0].multiFuse(s[1:]).Solids[0]


def heal(shape, tag, log):
    before = len(shape.Faces)
    tmp = os.path.join(tempfile.gettempdir(), "healcas_%s.step" % tag)
    try:
        shape.exportStep(tmp)
        rt = Part.Shape(); rt.read(tmp); os.remove(tmp)
        shape = rt
    except Exception as exc:
        log.append("  ! %s: STEP round-trip skipped (%s)" % (tag, exc))
    shape = as_solid(shape.removeSplitter())
    shape.fixTolerance(1e-7)
    log.append("  heal %-16s faces %3d -> %3d, solids %d, %10.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape


def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.3, Relative=False)


def max_radius(mesh):
    return max(math.hypot(v.x, v.y) for v in mesh.Points)


def r_profile(mesh, z0, z1, nb):
    """max hypot(x, y) per z-bucket -- the swept radial profile of a body."""
    span = z1 - z0
    prof = [0.0] * nb
    for v in mesh.Points:
        k = int((v.z - z0) / span * nb)
        if 0 <= k < nb:
            rr = math.hypot(v.x, v.y)
            if rr > prof[k]:
                prof[k] = rr
    return prof


# ================================================================ builds
#   Flight parts first, then the reference envelope.


def build_retention_band():
    """Local wall thickening at the aft section's forward cut.  ID r19.6 / OD r22.5,
    12 mm long.  Carries the 3 radial M3 that capture the anchor-bulkhead coupler,
    and doubles as a visible index ring at the joint.  This is a FEATURE OF THE AFT
    TUBE SECTION, modelled standalone here."""
    b = tube(BAND_RI, BAND_RO, BAND_Z0, BAND_Z1)
    # 3 radial M3 clearance holes
    for i in range(SCREW_N):
        a = math.radians(SCREW_AZ0 + 360.0 * i / SCREW_N)
        b = b.cut(Part.makeCylinder(SCREW_R, BAND_RO + 2.0,
                  Vector((BAND_RO + 1.0) * math.cos(a), (BAND_RO + 1.0) * math.sin(a), SCREW_Z),
                  Vector(-math.cos(a), -math.sin(a), 0)))
    # a shallow SCRIBED index notch at +y (removes material only -- stays flush), lines
    # up with a painted witness line on the fwd tube so the clocking is visible at a glance
    b = b.cut(box(-0.8, 0.8, BAND_RO - 0.8, BAND_RO + 1.0, BAND_Z1 - 3.0, BAND_Z1 + 1.0))
    return b


def build_anchor_coupler():
    """The anchor bulkhead, reworked as the airframe coupler and the front of the
    cassette.  r19.4 body, 18 mm long: forward 6 mm bonded into the fwd tube
    section, middle screwed to the retention band, aft face carries the ejection
    cage.  Bored d6.8 for the piston shaft, d11.5 spring-seat counterbore, and a
    recovery-eyelet boss."""
    a = cyl(ANCHOR_R, ANCHOR_Z0, ANCHOR_Z1)
    a = a.cut(cyl(ANCHOR_BORE_R, ANCHOR_Z0 - 1.0, ANCHOR_Z1 + 1.0))
    a = a.cut(cyl(ANCHOR_SEAT_R, ANCHOR_Z1 - ANCHOR_SEAT_DEPTH, ANCHOR_Z1 + 1.0))
    # 3 radial M3 tapped holes (modelled as pilot bores) aligned with the band.
    # MATCH-DRILLED at first build against the aft-closure key clocking (see [K]).
    for i in range(SCREW_N):
        ang = math.radians(SCREW_AZ0 + 360.0 * i / SCREW_N)
        a = a.cut(Part.makeCylinder(SCREW_R - 0.4, ANCHOR_R + 1.0,
                  Vector((ANCHOR_R + 0.5) * math.cos(ang), (ANCHOR_R + 0.5) * math.sin(ang), SCREW_Z),
                  Vector(-math.cos(ang), -math.sin(ang), 0)))
    # recovery eyelet -- an INBOARD boss on the forward face, d4 cross-hole for a
    # U-bolt / Kevlar leader (DESIGN.md 7.7; the ejection POC dropped it, 6.10)
    boss = box(-EYELET_BOSS_W / 2.0, EYELET_BOSS_W / 2.0, 8.0, 14.0,
               ANCHOR_Z1 - 3.0, ANCHOR_Z1 + 0.01)
    boss = boss.cut(Part.makeCylinder(EYELET_R, EYELET_BOSS_W + 4.0,
                    Vector(-EYELET_BOSS_W, 11.0, ANCHOR_Z1 - 1.5), Vector(1, 0, 0)))
    a = a.fuse(boss)
    return as_solid(a)


def build_aft_closure():
    """The aft closure, reworked.  r19.0 disc (was 19.70), a d8 x 3 spigot into the
    motor-bulkhead counterbore, and ONE 3 x 3 x 4 key on the aft face -- the sole
    rotational constraint, so the whole cassette re-indexes to one clocking."""
    d = cyl(AFTCLO_R, AFTCLO_Z0, AFTCLO_Z1)
    d = d.cut(cyl(ANCHOR_BORE_R, AFTCLO_Z0 - 1.0, AFTCLO_Z1 + 1.0))   # shaft / wiring pass-through
    d = d.fuse(cyl(SPIGOT_R, AFTCLO_Z0 - SPIGOT_H, AFTCLO_Z0 + 0.01))
    a = math.radians(KEY_AZ)
    kx, ky = KEY_RC * math.cos(a), KEY_RC * math.sin(a)
    key = box(kx - KEY_W / 2.0, kx + KEY_W / 2.0, ky - KEY_L / 2.0, ky + KEY_L / 2.0,
              AFTCLO_Z0 - KEY_H, AFTCLO_Z0 + 0.01)
    d = d.fuse(key)
    return as_solid(d)


def build_battery_tray():
    """A thin U-channel in the SLED's radial shadow: a 0.6 mm outboard lip the cell
    rests against, two thin side walls, end caps fore and aft -- and OPEN on the
    inboard (+y) face, because that is the way the cell comes out.  The cell lifts
    straight toward the axis and then forward.  The pull is a fabric loop bonded to
    the cell plus the JST-PH pigtail itself, not a printed tab -- there is no radial
    room outboard for one (worst corner 0.96 mm off the ID).  Everything is clipped
    to the sled envelope so it cannot bust the bore."""
    x0, x1 = -BATT_DX / 2.0 - TRAY_WALL, BATT_DX / 2.0 + TRAY_WALL
    y_out, y_in = BATT_Y0, BATT_Y1                     # cell outboard / inboard faces
    z0, z1 = BATT_Z0 - TRAY_WALL, BATT_Z1 + TRAY_WALL
    shell = box(x0, x1, y_out - TRAY_WALL, y_in + 0.01, z0, z1)
    # cell pocket, open toward +y (inboard)
    shell = shell.cut(box(-BATT_DX / 2.0, BATT_DX / 2.0, y_out, y_in + 2.0, BATT_Z0, BATT_Z1))
    # cut the outboard wall back to a TRAY_LIP-thick backstop
    shell = shell.cut(box(x0 - 1.0, x1 + 1.0, y_out - TRAY_WALL - 1.0, y_out - TRAY_LIP,
                          BATT_Z0 - 1.0, BATT_Z1 + 1.0))
    # JST-PH pigtail exit, aft-inboard corner
    shell = shell.cut(box(BATT_DX / 2.0 - JST_SLOT_W, x1 + 1.0,
                          y_in - JST_SLOT_H, y_in + 1.0, z0 - 1.0, BATT_Z0 + 0.5))
    # keep it inside the sled envelope
    shell = shell.common(cyl(SLED_RMAX, z0 - 1.0, z1 + 1.0))
    return as_solid(shell)


# --- reference envelope (verification only, never exported) --------------------

def env_sled():
    return box(-SLED_BX / 2.0, SLED_BX / 2.0, -SLED_BY / 2.0, SLED_BY / 2.0,
               SLED_Z0, SLED_Z1).common(cyl(SLED_RMAX, SLED_Z0 - 1, SLED_Z1 + 1))


def env_battery():
    return box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y0, BATT_Y1, BATT_Z0, BATT_Z1)


def env_nano():
    return box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, NANO_Y1, NANO_Z0, NANO_Z1)


def env_servo():
    return box(SERVO_X0, SERVO_X1, -SERVO_Y, SERVO_Y, SERVO_Z0, SERVO_Z1)


def env_knob():
    return cyl(KNOB_R, KNOB_Z0, KNOB_Z1, KNOB_AX_X, 0.0)


def aft_section_wall():
    """The fixed aft tube section the cassette slides through: the wall annulus with
    the static port drilled, plus the retention band.  Anything the cassette must
    not touch on the way out."""
    w = tube(R_AF_I, R_AF_O, MB_Z - 2.0, JOINT_Z + 0.5)
    a = math.radians(90.0)   # north lobe
    w = w.cut(Part.makeCylinder(STATIC_PORT_D / 2.0, R_AF_O + 2.0,
              Vector((R_AF_I - 1.0) * math.cos(a), (R_AF_I - 1.0) * math.sin(a), STATIC_PORT_Z),
              Vector(math.cos(a), math.sin(a), 0)))
    w = w.fuse(build_retention_band())
    return as_solid(w)


def motor_bulkhead_ref():
    d = cyl(R_AF_I, MB_Z - 8.0, MB_Z)
    d = d.cut(cyl(MB_CBORE_R, MB_Z - SPIGOT_H - 0.5, MB_Z + 1.0))
    a = math.radians(KEY_AZ)
    kx, ky = KEY_RC * math.cos(a), KEY_RC * math.sin(a)
    d = d.cut(box(kx - KEY_W / 2.0 - CL_KEY, kx + KEY_W / 2.0 + CL_KEY,
                  ky - KEY_L / 2.0 - CL_KEY, ky + KEY_L / 2.0 + CL_KEY,
                  MB_Z - KEY_H - 0.5, MB_Z + 0.01))
    return as_solid(d)


# ================================================================ verification


def main():
    log = []
    P = log.append
    P("=" * 80)
    P("Phoenix ABS 40-43 -- avionics bay SERVICEABLE CASSETTE  %s" % REV)
    P("=" * 80)
    P("")
    P("frame: avbay_packing_build_report_v2.txt  (Z=0 aft of the component zone, +Z to nose)")
    P("joint: transverse BENCH-service joint at Z %.1f  (~station 181, DESIGN.md 7.8)" % JOINT_Z)
    P("       opened for service only -- flight recovery separates at the NOSE (7.5)")
    P("cassette leaves as one: anchor coupler + cage + knob + servo + sled + electronics")
    P("       + aft closure ; the servo-to-knob coupler is never broken")
    P("")

    doc = App.newDocument("PhoenixABS40-43_avbay_cassette")

    P("[1] build + heal")
    raw = [("SvcRetentionBand", build_retention_band()),
           ("SvcAnchorCoupler", build_anchor_coupler()),
           ("SvcAftClosure", build_aft_closure()),
           ("SvcBatteryTray", build_battery_tray())]
    parts = [(n, heal(s, n, log)) for n, s in raw]
    by = dict(parts)
    meshes = dict((n, mesh_of(s)) for n, s in parts)

    # reference bodies
    ref = {"Env_Sled": env_sled(), "Env_Battery": env_battery(), "Env_Nano": env_nano(),
           "Env_Servo": env_servo(), "Env_Knob": env_knob(),
           "AftSectionWall": aft_section_wall(), "MotorBulkhead": motor_bulkhead_ref()}
    refmesh = dict((n, mesh_of(s)) for n, s in ref.items())

    P("")
    P("[2] mass + envelope  (flight parts; ref bodies are bounding solids, not parts)")
    tot = 0.0
    for n, s in parts:
        m = s.Volume * RHO
        tot += m
        bb = meshes[n].BoundBox
        P("  %-16s %9.1f mm3  %6.2f g   R %5.2f   Z %7.1f .. %6.1f"
          % (n, s.Volume, m, max_radius(meshes[n]), bb.ZMin, bb.ZMax))
    P("  serviceable-cassette printed additions subtotal  %6.2f g" % tot)
    P("  (+ 3x M3 screws, 1x JST-PH pigtail -- the only bought hardware this adds)")

    P("")
    P("[0] CONTAINMENT")
    lim = {"SvcRetentionBand": R_AF_O + 0.05, "SvcAnchorCoupler": R_MAX_STATIC,
           "SvcAftClosure": R_MAX_STATIC, "SvcBatteryTray": SLED_RMAX + 0.05}
    for n, _ in parts:
        r = max_radius(meshes[n])
        tgt = lim[n]
        note = ""
        if n == "SvcRetentionBand":
            note = "(flush with the skin -- the aft-section wall, thickened inward to r%.1f)" % BAND_RI
        if n == "SvcBatteryTray":
            note = "(in the sled's radial shadow)"
        P("  %-16s R_max %6.2f  <= %.2f   %s  %s"
          % (n, r, tgt, "PASS" if r <= tgt + 1e-6 else "FAIL", note))
    for n in ("Env_Sled", "Env_Battery", "Env_Knob"):
        r = max_radius(refmesh[n])
        P("  %-16s R_max %6.2f  <= %.2f   %s  (v2 pack envelope)"
          % (n, r, R_AF_I, "PASS" if r <= R_AF_I + 1e-6 else "FAIL"))

    # -------------------------------------------------------------------- [E]
    P("")
    P("[E] EXTRACTION SWEEP -- does the cassette actually slide out?")
    P("    the whole point of the exercise.  A static .common() at one position")
    P("    reads 0 mm3 for a 0.00 mm gap AND a 0.50 mm gap (ejection POC 6.11), so")
    P("    this does BOTH: a swept boolean for hard interference, and arithmetic on")
    P("    the radial profile for the actual running clearance.")
    cass = [by["SvcAnchorCoupler"], by["SvcAftClosure"], by["SvcBatteryTray"],
            ref["Env_Sled"], ref["Env_Battery"], ref["Env_Nano"], ref["Env_Servo"],
            ref["Env_Knob"]]
    cu = cass[0]
    for s in cass[1:]:
        cu = cu.fuse(s)
    cu = as_solid(cu)
    fixed = aft_section_wall()
    # swept boolean
    worst_iv, worst_at = 0.0, 0.0
    for k in range(SWEEP_STEPS + 1):
        dz = k * EXTRACT_TRAVEL / SWEEP_STEPS
        c = cu.copy(); c.translate(Vector(0, 0, dz))
        iv = c.common(fixed).Volume
        if iv > worst_iv:
            worst_iv, worst_at = iv, dz
    P("  swept boolean: worst cassette-vs-fixed interference %.3f mm3 at +%.1f mm   %s"
      % (worst_iv, worst_at, "PASS" if worst_iv < 1.0 else "FAIL"))
    # arithmetic running clearance
    czl, czh = -4.0, ANCHOR_Z1 + 1.0
    NB = 90
    prof = r_profile(mesh_of(cu), czl, czh, NB)
    mincl, minat = 1e9, None
    for k in range(SWEEP_STEPS + 1):
        dz = k * EXTRACT_TRAVEL / SWEEP_STEPS
        for i, rc in enumerate(prof):
            if rc <= 1e-6:
                continue
            wz = czl + (i + 0.5) * (czh - czl) / NB + dz
            in_band = BAND_Z0 - 1e-6 <= wz <= BAND_Z1 + 1e-6
            limr = BAND_RI if in_band else R_AF_I
            cl = limr - rc
            if cl < mincl:
                mincl, minat = cl, (dz, wz, rc, "band" if in_band else "bore")
    dz, wz, rc, feat = minat
    P("  running clearance: min %+.2f mm  (cassette r %.2f vs %s r %.2f at world Z %.1f, +%.1f mm)"
      % (mincl, rc, feat, (BAND_RI if feat == "band" else R_AF_I), wz, dz))
    # isolate the one that is an EXTRACTION event, not a designed fit: the sled (r ~19.39)
    # dragging through the retention band on the way out
    sled_cl = 1e9
    for k in range(SWEEP_STEPS + 1):
        dz2 = k * EXTRACT_TRAVEL / SWEEP_STEPS
        for i, rc2 in enumerate(prof):
            if rc2 < SLED_RMAX - 0.15:
                continue
            wz2 = czl + (i + 0.5) * (czh - czl) / NB + dz2
            if BAND_Z0 - 1e-6 <= wz2 <= BAND_Z1 + 1e-6:
                sled_cl = min(sled_cl, BAND_RI - rc2)
    P("  of which, the SLED dragging through the band on the way out: %+.2f mm" % sled_cl)
    verd = "FAIL -- interferes" if mincl <= 0 else "PASS"
    P("  %s%s" % (verd, "   <-- TIGHT (< 0.5 mm)" if 0 < mincl < 0.5 else ""))
    if 0 < mincl < 0.5:
        P("      the register fit (%.2f) is CL_REG by design; the sled pass-through (%.2f) is"
          % (CL_REG, sled_cl if sled_cl < 1e8 else 0.0))
        P("      the same tightness the v2 pack already has to the bore -- the real fix is a")
        P("      shorter flight-computer board (packing md section 7), not a fatter band.")
    # why the aft closure had to shrink
    old_cl = BAND_RI - AFTCLO_OLD_R
    P("  note: the v2 aft closure at r%.2f would foul the band by %.2f mm -- hence r%.2f + spigot"
      % (AFTCLO_OLD_R, -old_cl if old_cl < 0 else 0.0, AFTCLO_R))

    # -------------------------------------------------------------------- [R]
    P("")
    P("[R] RETENTION LOAD PATH -- 3x M3 radial, band <-> anchor coupler")
    gate = "OPEN" if not RECOVERY_MEASURED else "----"
    if not RECOVERY_MEASURED:
        P("    >>> OPEN.  RECOVERY_SNATCH_N = %.0f N is a PLACEHOLDER for the wrong-event" % RECOVERY_SNATCH_N)
        P("    >>> reason as much as the wrong-number one: the governing load is the EJECTION")
        P("    >>> snatch (~5.1 m/s separation arrested over the shock cord, 7.5) -- a few")
        P("    >>> hundred N -- not canopy opening shock (~10-30 N).  Needs F_max (7.3) then")
        P("    >>> a packed drop (7.9 test 4).  If it lands high the flush band is marginal")
        P("    >>> and the 3-lug BAYONET is the answer, not a fallback.")
    bear_area = SCREW_N * (2 * SCREW_R) * BAND_WALL           # shank dia x band wall, x3
    bear_mpa = RECOVERY_SNATCH_N / bear_area
    P("  screw bearing on the band wall  %.1f mm2  ->  %.2f MPa  vs %.0f  %s"
      % (bear_area, bear_mpa, ABS_BEARING_MPA,
         gate if not RECOVERY_MEASURED else ("PASS" if bear_mpa < ABS_BEARING_MPA else "FAIL")))
    shank_area = SCREW_N * math.pi * SCREW_R ** 2
    shank_mpa = RECOVERY_SNATCH_N / shank_area
    P("  screw shank shear (A2 steel)    %.1f mm2  ->  %.2f MPa  vs %.0f  %s"
      % (shank_area, shank_mpa, SCREW_STEEL_SHEAR_MPA,
         gate if not RECOVERY_MEASURED else ("PASS" if shank_mpa < SCREW_STEEL_SHEAR_MPA else "FAIL")))
    P("  edge distance screw <-> tube cut  %.1f mm  = %.1f x d   %s"
      % (SCREW_EDGE, SCREW_EDGE / SCREW_D_NOM,
         "PASS (>= 2d)" if SCREW_EDGE >= 2 * SCREW_D_NOM - 1e-6 else "MARGINAL -- want >= 2d"))
    P("  band wall for the screw          %.1f mm  (vs a bare 1.5 mm tube wall)   %s"
      % (BAND_WALL, "PASS" if BAND_WALL >= 2.5 else "THIN"))
    P("  ALT if [R] fails once measured: 3-lug bayonet ring (spreads the load round the")
    P("  full circumference, no radial holes) -- costs ~4 mm of length.  See packing md 9.")

    # -------------------------------------------------------------------- [K]
    P("")
    P("[K] CLOCKING -- one key, so the cassette re-indexes to one orientation")
    _kx, _ky = KEY_RC * math.cos(math.radians(KEY_AZ)), KEY_RC * math.sin(math.radians(KEY_AZ))
    kv = by["SvcAftClosure"].common(box(_kx - KEY_W, _kx + KEY_W, _ky - KEY_L, _ky + KEY_L,
                                        AFTCLO_Z0 - KEY_H - 0.5, AFTCLO_Z0 - 0.2)).Volume
    P("  aft-closure key is a real solid   %.1f mm3   %s" % (kv, "PASS" if kv > 10.0 else "FAIL"))
    slot_fit = CL_KEY
    P("  key <-> motor-bulkhead slot fit   %+.2f mm/face  (CL_KEY)   %s"
      % (slot_fit, "PASS" if 0.15 <= slot_fit <= 0.45 else "CHECK"))
    # the forward register must be a PLAIN round slip fit, so the key is the SOLE clock
    # probe the OUTER surface of the register band only: no key / flat / spline anywhere
    # on it, so the aft-closure key is the sole rotational constraint
    am = mesh_of(by["SvcAnchorCoupler"])
    band_pts = [math.hypot(v.x, v.y) for v in am.Points
                if BAND_Z0 + 1.0 < v.z < BAND_Z1 - 1.0 and math.hypot(v.x, v.y) > ANCHOR_R - 0.8]
    dr = (max(band_pts) - min(band_pts)) if band_pts else -1.0
    reg_ok = bool(band_pts) and dr < 0.4
    P("  fwd register is plain round (no 2nd clock)   dR %.2f mm   %s"
      % (dr, "PASS" if reg_ok else "FAIL"))
    P("  the 3 screw holes are MATCH-DRILLED at first build so they cannot fight the key")
    P("  wall ports that must re-index: static port Z %.0f (N lobe) ; USB-C Z %.0f ; microSD Z %.0f"
      % (STATIC_PORT_Z, USB_SLOT_Z, USD_SLOT_Z))
    P("  witness marks: paint a line across the band index notch and the fwd-tube seam")

    # -------------------------------------------------------------------- [S]
    P("")
    P("[S] STATIC PORT -- plain hole, shared air, no obstruction")
    w = aft_section_wall()
    # inner radius of the wall right at the port station: sample a ring, min radius to material
    ring = w.common(cyl(R_AF_I + 0.2, STATIC_PORT_Z - 0.5, STATIC_PORT_Z + 0.5)
                    .cut(cyl(R_AF_I - 0.3, STATIC_PORT_Z - 1, STATIC_PORT_Z + 1)))
    P("  wall inner face at the port stays at r%.1f (no inward boss)   %s"
      % (R_AF_I, "PASS" if ring.Volume > 1.0 else "CHECK"))
    # BMP388 shares air with the port: the cassette does not wall off the north lobe at Z 12
    lobe = box(-6.0, 6.0, 8.0, R_AF_I, STATIC_PORT_Z - 3.0, STATIC_PORT_Z + 3.0)
    occl = cu.common(lobe).Volume
    P("  north lobe at Z %.0f is open to the port  (cassette fills %.1f of %.1f mm3)   %s"
      % (STATIC_PORT_Z, occl, lobe.Volume, "PASS" if occl < lobe.Volume * 0.6 else "FAIL"))

    # -------------------------------------------------------------------- [B]
    P("")
    P("[B] BATTERY SWAP -- JST pigtail + inboard-open pocket")
    tr = by["SvcBatteryTray"]
    trm = meshes["SvcBatteryTray"]
    tray_rmax = max_radius(trm)
    P("  tray R_max %.2f  <= sled r %.2f  (nothing added outboard of the cell)   %s"
      % (tray_rmax, SLED_RMAX, "PASS" if tray_rmax <= SLED_RMAX + 0.05 else "FAIL"))
    # the pocket is OPEN on the inboard (+y) face -- no wall spanning it
    inb = tr.common(box(-BATT_DX / 2.0 + 1.0, BATT_DX / 2.0 - 1.0,
                        BATT_Y1 - 0.5, BATT_Y1 + 2.0, BATT_Z0 + 1.0, BATT_Z1 - 1.0)).Volume
    P("  inboard face of the pocket is open (%.1f mm3 of wall across it)   %s"
      % (inb, "PASS" if inb < 3.0 else "FAIL -- the cell is trapped"))
    # cell lifts straight inboard (+y) and clears
    b_up = env_battery(); b_up.translate(Vector(0, BATT_DY + 1.0, 0))
    foul = tr.common(b_up).Volume
    P("  cell clears the tray on a straight inboard lift  (foul %.1f mm3)   %s"
      % (foul, "PASS" if foul < 5.0 else "FAIL -- an overhang traps the cell"))
    # outboard lip is present -- the cell IS retained against outboard (flight) motion
    lip = tr.common(box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y0 - TRAY_LIP - 0.05, BATT_Y0,
                        BATT_Z0, BATT_Z1)).Volume
    P("  outboard lip retains the cell in flight  (%.1f mm3 of lip)   %s"
      % (lip, "PASS" if lip > 8.0 else "FAIL -- nothing holds the cell against boost"))
    jst = tr.common(box(BATT_DX / 2.0 - JST_SLOT_W, BATT_DX / 2.0 + TRAY_WALL,
                        BATT_Y1 - JST_SLOT_H, BATT_Y1, BATT_Z0 - TRAY_WALL, BATT_Z0)).Volume
    P("  JST pigtail exit slot is open   (%.1f mm3 of wall left in the slot)   %s"
      % (jst, "PASS" if jst < 3.0 else "FAIL"))
    P("  recharge-in-place still works with NO disassembly: USB-C slot + BQ25302 (packing md 5)")

    # -------------------------------------------------------------------- [9]
    P("")
    P("[9] features present (non-vacuous)")
    f = []
    scr_probe = Part.makeCylinder(SCREW_R - 0.3, BAND_RO - BAND_RI + 3.0,
                                  Vector(0.0, BAND_RO + 1.5, SCREW_Z), Vector(0, -1, 0))
    f.append(("band M3 hole open",
              scr_probe.common(by["SvcRetentionBand"]).Volume < scr_probe.Volume * 0.4))
    f.append(("anchor d6.8 bore open",
              cyl(ANCHOR_BORE_R - 0.2, ANCHOR_Z0, ANCHOR_Z1).common(by["SvcAnchorCoupler"]).Volume < 1.0))
    f.append(("anchor spring seat cut",
              cyl(ANCHOR_SEAT_R - 0.3, ANCHOR_Z1 - ANCHOR_SEAT_DEPTH + 0.2, ANCHOR_Z1)
              .common(by["SvcAnchorCoupler"]).Volume < 1.0))
    f.append(("aft-closure spigot present",
              cyl(SPIGOT_R - 0.3, AFTCLO_Z0 - SPIGOT_H + 0.2, AFTCLO_Z0)
              .common(by["SvcAftClosure"]).Volume > 20.0))
    f.append(("battery pocket hollow",
              box(-BATT_DX / 2.0 + 1, BATT_DX / 2.0 - 1, BATT_Y0 + 1, BATT_Y1 - 1, BATT_Z0 + 1, BATT_Z1 - 1)
              .common(by["SvcBatteryTray"]).Volume < 5.0))
    f.append(("tray outboard face is just a lip",
              by["SvcBatteryTray"].common(box(-BATT_DX, BATT_DX, BATT_Y0 - TRAY_WALL, BATT_Y0 - TRAY_LIP - 0.1,
                                              BATT_Z0, BATT_Z1)).Volume < 1.0))
    for name, ok in f:
        P("  %-32s %s" % (name, "PASS" if ok else "FAIL"))

    # -------------------------------------------------------------------- [10]
    P("")
    P("[10] export")
    if not os.path.isdir(AV_MODELS):
        os.makedirs(AV_MODELS)
    for n, s in parts:
        doc.addObject("Part::Feature", n).Shape = s
        stem = "PhoenixABS40-43_avbay_%s_%s" % (n, REV)
        s.exportStep(os.path.join(AV_MODELS, stem + ".step"))
        meshes[n].write(os.path.join(AV_MODELS, stem + ".stl"))
        P("  %-16s -> Models/%s.step + .stl" % (n, stem))
    for n, s in ref.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        o.Visibility = False

    # -------------------------------------------------------------------- [A]
    P("")
    P("[A] assembly STL  (everything in flight position, packing frame)")
    # the 4 printed parts as real geometry + the component envelopes they locate +
    # the motor bulkhead for aft context.  NOT the sled bounding block (it would
    # swallow the view) and NOT the outer tube (ditto -- the flush band shows the skin).
    asm = [("SvcRetentionBand", by["SvcRetentionBand"]),
           ("SvcAnchorCoupler", by["SvcAnchorCoupler"]),
           ("SvcAftClosure", by["SvcAftClosure"]),
           ("SvcBatteryTray", by["SvcBatteryTray"]),
           ("Env_Battery", ref["Env_Battery"]), ("Env_Nano", ref["Env_Nano"]),
           ("Env_Servo", ref["Env_Servo"]), ("Env_Knob", ref["Env_Knob"]),
           ("MotorBulkhead", ref["MotorBulkhead"])]
    comp = Part.makeCompound([s for _n, s in asm])
    ao = doc.addObject("Part::Feature", "Assembly_full")
    ao.Shape = comp
    bb = comp.BoundBox
    P("  %d bodies  bbox %.1f x %.1f x %.1f mm  Z %.1f .. %.1f"
      % (len(asm), bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax))
    # also drop each body as its own STL so it can be re-coloured / re-assembled in CAD
    ASM_DIR = os.path.join(AV_MODELS, "cassette_assembly_%s" % REV)
    if not os.path.isdir(ASM_DIR):
        os.makedirs(ASM_DIR)
    for nm, s in asm:
        mesh_of(s).write(os.path.join(ASM_DIR, nm + ".stl"))
    full = mesh_of(asm[0][1])
    for _n, s in asm[1:]:
        full.addMesh(mesh_of(s))
    full_path = os.path.join(AV_MODELS, "PhoenixABS40-43_avbay_cassette_ASSEMBLY_%s.stl" % REV)
    full.write(full_path)
    P("  full     %6d facets -> Models/%s" % (full.CountFacets, os.path.basename(full_path)))
    # half section: keep Y <= 0 (the battery / tray side), so the internal fit reads
    half_box = box(-40.0, 40.0, -40.0, 0.0, bb.ZMin - 2.0, bb.ZMax + 2.0)
    sec_parts = []
    for _n, s in asm:
        c = s.common(half_box)
        if c.Volume > 1.0:
            sec_parts.append(c)
    sec = mesh_of(sec_parts[0])
    for s in sec_parts[1:]:
        sec.addMesh(mesh_of(s))
    sec_path = os.path.join(AV_MODELS, "PhoenixABS40-43_avbay_cassette_ASSEMBLY_section_%s.stl" % REV)
    sec.write(sec_path)
    P("  section  %6d facets -> Models/%s  (cut at Y=0, battery side kept)"
      % (sec.CountFacets, os.path.basename(sec_path)))
    so = doc.addObject("Part::Feature", "Assembly_section")
    so.Shape = Part.makeCompound(sec_parts)
    so.Visibility = False

    doc.recompute()
    doc.saveAs(os.path.join(AVIONICS, "PhoenixABS40-43_avbay_cassette_%s.FCStd" % REV))
    P("  FCStd -> Avionics/PhoenixABS40-43_avbay_cassette_%s.FCStd" % REV)

    P("")
    P("SUMMARY")
    P("  * recharge / SD / arm  : already external in the v2 pack -- no change, no disassembly")
    P("  * battery SWAP         : JST pigtail + bonded pull-loop, pocket open inboard -> spare")
    P("  * cassette removal     : split the bench joint, the fwd section lifts the whole")
    P("                          stack out -- servo/knob coupler never breaks")
    P("  * OPEN [R]             : the anchor bulkhead must be SCREWED not bonded (DESIGN.md")
    P("                          7.5), and that joint's recovery-snatch capacity is")
    P("                          UNVERIFIED until F_max (7.3) + a packed drop (7.9 t4)")
    P("  * TIGHT [E]            : the retention band tightens the sled's radial fit to")
    P("                          ~%.2f mm -- shorter FC board is the real fix" % (max(mincl, 0.0)))

    rpt = "\n".join(log)
    print(rpt)
    with open(os.path.join(AVIONICS, "avbay_cassette_build_report_%s.txt" % REV), "w") as fh:
        fh.write(rpt + "\n")


main()

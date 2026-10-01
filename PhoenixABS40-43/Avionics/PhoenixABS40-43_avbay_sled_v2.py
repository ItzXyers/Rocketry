# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v2  (the "scaffold to screw
the chips into").

v2 = v1 with (2026-09-30):
  * SERVO REMOVED -- D9aft recovery (Models/AFT_DEPLOY_D9_DESIGN.md) fires nothing from
    the e-bay.  Servo envelope + cradle gone; ejection-knob reference gone.  The two
    axial M2 bosses that took the SG90 ears are KEPT at the same (x, y) and top Z: the
    D9aft EbayCap screws the sled down through them (SLED_SCREWS).  They now stand on
    their own columns + a cross-beam instead of the cradle.
  * ADXL375 no longer trimmed to 25.3 -- full 26 mm board, pocket walls to 26.
  * REED SWITCH gets its own body + cradle: 14 x d2 glass capsule, axial, against the
    SOUTH wall outboard of the battery tray, Z 5..19 (packing md sec 5).  Open groove +
    Kapton strap, no snap (glass).  Removed from the SmallParts allowance.
  * v1 BUG fixed: the Nano pocket and (once the cradle is gone) the battery tray were
    not attached to the rest of the sled; as_solid() kept only the first solid, so the
    v1 STEP has NO Nano pocket.  v2 ties both in and FAILS the build if the sled is not
    one connected solid.
  * nothing but the spine key rises above CAP_Z0 (EbayCap disc underside).

SOURCE OF TRUTH for the printed sled.  Companion to Avionics/avionics_bay_packing_40mm.md
(sections 3, 8, 9) and PhoenixABS40-43_avbay_cassette_v1.py (the serviceable-cassette
retention parts, which this sled sits inside).

This file also carries the v3 REPACK -- the first layout worked to the REAL measured
hardware instead of the v2 estimates:
  * BMP388  40 x 22 x 4   Qwiic bodies included (was ~24 x 18 x 5)
  * ADXL375 26 x 18 x 4                          (was 25.4 x 17.8 x 5)
  * Piezo   19 x 15 x 11   round can + rect breakout, kept (no flat-transducer swap)
  * USB-C charger BQ25302  DELETED with its wall slot -- battery charges off-vehicle
    on its existing JST-PH pigtail.
Constraint held: component zone stays Z 0..48 (bay ~54 mm) -- no length growth.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" <this file>

Frame (== avbay_packing_build_report_v2.txt):
  Z = 0 at the aft face of the component zone (fwd face of the motor bulkhead),
  +Z toward the nose.  Origin on the tube axis; +x "east", +y "north".
  Airframe OD 43.0 / ID 40.0 / wall 1.5.
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
AVIONICS = os.environ.get("SLED_OUT", os.path.join(PROJECT, "Avionics"))
AV_MODELS = os.path.join(AVIONICS, "Models")
REV = "v2"
RHO = 1.05e-3                 # ABS ~100% infill, g/mm^3

# --- airframe ---
R_AF_I = 20.0                 # ID 40.0
R_MAX_MOVING = 19.5           # anything that slides in/out of the bore
SLED_RMAX = 19.39             # sled outer envelope (v2 value, kept)

# --- FDM fit clearances (ABS, 0.4 mm nozzle) -- same block as the ejection POC ---
CL_SLIDE = 0.50
CL_REG   = 0.20
CL_BOARD = 0.30   # a PCB dropped into a printed 3-face pocket (per captured face)
WALL     = 0.90   # nominal sled pocket wall
LIP      = 0.60   # strap-retained parts: outboard backstop, nothing more

# =============================================================================
# v3 PACK -- component bounding solids at their placed positions.
# bbox is (dx, dy, dz); position via the explicit x0/y0/z0 below.  NOT flight
# parts -- they exist so the sled has something to be checked against.
# =============================================================================

# EBAYCAP MOUNT -- 2 axial M2 bosses, inherited from the v1 SG90-ear bosses.  The
#   D9aft EbayCap (disc at sled Z 45.4..50.3) screws down into them, so (x, y) and the
#   boss top are FROZEN to v1: x = -14.0-1.3 / 8.8+1.3, y = 0, top Z 45.4.
CAP_Z0 = 45.4                             # EbayCap disc underside (D9aft DISC_ZS0)
MOUNT_XW, MOUNT_XE = -15.3, 10.1
MOUNT_HOLE_D = 2.0                        # M2
MOUNT_BOSS_R = MOUNT_HOLE_D / 2.0 + 1.6
MOUNT_PILOT_DEPTH = 12.0                  # M2x10 from the disc top -> tip at Z 40.3
SERVO_TAB_XW, SERVO_TAB_XE = MOUNT_XW, MOUNT_XE   # names the D9aft scripts read (SL['SERVO_TAB_X*'])

# NANO ESP32 45x18x5 -- north, outboard.  1.21 mm to ID -> NO outboard fastener
#   room: strap + pocket retention.  4 holes noted for a future recessed variant.
NANO_DX, NANO_DY, NANO_DZ = 18.0, 5.0, 45.0
NANO_Y0 = 11.5                            # inboard face
NANO_Z0 = 0.0
NANO_HOLES = 4
NANO_HOLE_D     = 2.0
NANO_HOLE_PX, NANO_HOLE_PZ = 14.0, 40.0   # 4-corner pitch (CONFIRM)

# BMP388 40x22x4 -- north, inboard of the Nano --------------------------------
BMP_DX, BMP_DY, BMP_DZ = 22.0, 4.0, 40.0
BMP_Y0 = 7.0
BMP_Z0 = 0.0
BMP_HOLES = 4                             # 4-corner; AFT pair screwed, FWD pair rail-captured
BMP_HOLE_D     = 2.5                      # M2.5 (CONFIRM)
BMP_HOLE_PX, BMP_HOLE_PZ = 16.0, 34.0

# BATTERY 40.5x20x8.5 -- south, alone, pulled in 0.7 from the v2 corner -----
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_Z0 = 0.0
BATT_WALL = 0.8
JST_SLOT_W, JST_SLOT_H = 6.0, 3.0

# ADXL375 26x18x4 -- aft centre band, shifted WEST ---------------------------
ADXL_DX, ADXL_DY, ADXL_DZ = 18.0, 4.0, 26.0
ADXL_X0 = -16.0
ADXL_Y0 = -2.0
ADXL_Z0 = 0.0
ADXL_CLEAR_Z = ADXL_DZ                    # v2: no servo above -> full 26 mm board (name kept for D9aft)
ADXL_HOLES = 4
ADXL_HOLE_D     = 2.5
ADXL_HOLE_PX, ADXL_HOLE_PZ = 13.0, 21.0   # 4-corner pitch (CONFIRM)

# PIEZO 19x15x11 -- east crescent, 15 RADIAL x 11 tangential x 19 axial -----
#   rectangular breakout captured 3-face; round can nested; strap over the 11 can.
PIEZO_DR, PIEZO_DT, PIEZO_DZ = 15.0, 11.0, 19.0
PIEZO_X0 = 3.0                            # inboard (radial) face
PIEZO_Z0 = 0.0
PIEZO_CAN_D, PIEZO_CAN_H = 12.5, 8.0      # round transducer (CONFIRM)
PIEZO_HOLES = 2                           # user: 2 holes "up top" -- near the +Z end
PIEZO_HOLE_D = 2.0
PIEZO_HOLE_PY = 8.0                       # spread across the tangential axis
PIEZO_HOLE_Z  = 16.0                      # both near the +Z (top) end of the breakout

# REED SWITCH 14 x d2 glass capsule -- axial, SOUTH wall, outboard of the battery
#   tray, Z 5..19 (packing md sec 5).  Armed by an external magnet on the skin.
#   Groove floor = 0.3 saddle + the tray's 0.6 lip = one WALL to the battery.
REED_D, REED_L = 2.0, 14.0
REED_Z0 = 5.0
REED_X = 0.0
REED_GROOVE_R = REED_D / 2.0 + CL_REG
REED_YC = (BATT_Y1 - BATT_DY - LIP) - (WALL - LIP) - REED_GROOVE_R   # -17.6
REED_SADDLE_DX = 2.5                      # half-width
REED_LEAD_Z = 2.0                         # groove runs this far past each capsule end (leads)
REED_MASS = 1.0

# SMALL PARTS ~13 g (reed now separate) -- north-centre strip (between ADXL top and
#   the BMP388 pocket), east of the spine; open shelf + strap.  UNMEASURED -- see [N].
SP_X0, SP_X1 = -15.5, -2.0
SP_Y0, SP_Y1 = 2.2, 5.3
SP_Z0, SP_Z1 = 0.0, 22.0

ZONE_Z1 = 48.0

# ================================================================ helpers
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))

def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0))

def cyl_x(r, x0, x1, y=0.0, z=0.0):
    return Part.makeCylinder(r, x1 - x0, Vector(x0, y, z), Vector(1, 0, 0))

def as_solid(shape):
    s = shape.Solids
    if not s:
        return shape
    return s[0] if len(s) == 1 else s[0].multiFuse(s[1:]).Solids[0]

def heal(shape, tag, log):
    before = len(shape.Faces)
    tmp = os.path.join(tempfile.gettempdir(), "healsled_%s.step" % tag)
    try:
        shape.exportStep(tmp)
        rt = Part.Shape(); rt.read(tmp); os.remove(tmp)
        shape = rt
    except Exception as exc:
        log.append("  ! %s: STEP round-trip skipped (%s)" % (tag, exc))
    shape = as_solid(shape.removeSplitter())
    shape.fixTolerance(1e-7)
    log.append("  heal %-14s faces %3d -> %3d, solids %d, %10.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape

def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.3, Relative=False)

def rmax_mesh(m):
    return max(math.hypot(v.x, v.y) for v in m.Points)

def clip_bore(shp, z0=-5.0, z1=None):
    return shp.common(cyl(SLED_RMAX, z0, z1 if z1 is not None else ZONE_Z1 + 5.0))

# ================================================================ component envelopes
def env_nano():
    return box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, NANO_Y0 + NANO_DY, NANO_Z0, NANO_Z0 + NANO_DZ)

def env_bmp():
    return box(-BMP_DX / 2.0, BMP_DX / 2.0, BMP_Y0, BMP_Y0 + BMP_DY, BMP_Z0, BMP_Z0 + BMP_DZ)

def env_batt():
    return box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0, BATT_Z0 + BATT_DZ)

def env_adxl():
    return box(ADXL_X0, ADXL_X0 + ADXL_DX, ADXL_Y0, ADXL_Y0 + ADXL_DY, ADXL_Z0, ADXL_Z0 + ADXL_DZ)

def env_piezo():
    b = box(PIEZO_X0, PIEZO_X0 + PIEZO_DR, -PIEZO_DT / 2.0, PIEZO_DT / 2.0, PIEZO_Z0, PIEZO_Z0 + PIEZO_DZ)
    return b

def env_small():
    return box(SP_X0, SP_X1, SP_Y0, SP_Y1, SP_Z0, SP_Z1)

def env_reed():
    return cyl(REED_D / 2.0, REED_Z0, REED_Z0 + REED_L, REED_X, REED_YC)

COMPONENTS = [
    ("Nano_ESP32",  env_nano),
    ("BMP388",      env_bmp),
    ("Battery",     env_batt),
    ("ADXL375",     env_adxl),
    ("Piezo",       env_piezo),
    ("ReedSwitch",  env_reed),
    ("SmallParts",  env_small),
]
RIGID = [n for n, _ in COMPONENTS if n != "SmallParts"]

# ================================================================ the sled
#   Convention: +y is OUTBOARD in the north (toward the wall), -y outboard in the
#   south.  "screw from outboard" = head sits in the gap between the board's
#   wall-facing face and the ID; only done where that gap >= ~3 mm (BMP388 4.4,
#   ADXL 3.9).  Nano/battery/small-parts (<1.6 mm to ID) get NO outboard feature
#   beyond a 0.6 mm lip + a Kapton strap.

def standoff_y(holes, board_face_std, head_dir, hole_d, standoff=2.6):
    """Standoff bosses on the STANDOFF side of a board whose screw HEAD is on the
    other side, screw axis = Y.
      holes         : list of (x, z) hole centres
      board_face_std: the board face on the standoff side (screw threads into the
                      boss here; the board is clamped between the head and this face)
      head_dir      : +1 if the head is at +y of the board, -1 if at -y
    The boss runs `standoff` deep away from the board (i.e. toward -head_dir), tied
    by a thin floor slab.  Pilot drilled full-depth.  FUSE the result into the sled.
    """
    hd = float(head_dir)
    y_root = board_face_std - hd * standoff          # far end of the boss / floor plane
    lo, hi = sorted((y_root, board_face_std))
    out = None
    for (hx, hz) in holes:
        b = Part.makeCylinder(hole_d / 2.0 + 1.4, standoff + 0.2, Vector(hx, lo - 0.1, hz), Vector(0, 1, 0))
        b = b.cut(Part.makeCylinder(hole_d / 2.0 - 0.20, standoff + 8.0, Vector(hx, lo - 3.0, hz), Vector(0, 1, 0)))
        out = b if out is None else out.fuse(b)
    # floor slab tying the bosses (in the plane just past y_root)
    xs = [h[0] for h in holes]; zs = [h[1] for h in holes]
    slab = box(min(xs) - 3.0, max(xs) + 3.0, min(lo, lo + hd * WALL), max(lo, lo + hd * WALL),
               min(zs) - 3.0, max(zs) + 3.0)
    return out.fuse(slab)


def build_sled(log):
    """One printed piece.  Board-carrier pockets tied by a spine down the west wall;
    two axial M2 bosses on columns take the EbayCap (the v1 servo cradle is gone)."""
    parts = []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)     # everything but the spine key stops under the cap

    # ---- spine down the west side -- its top (Z > CAP_Z0) is the key into the EbayCap pocket
    parts.append(clip_bore(box(-19.0, -16.6, -12.0, 12.0, 0.0, ZONE_Z1 - 0.6)))

    # ---- BMP388: full-length side rails + inboard end wall; 2 real standoffs at
    #      the AFT hole pair (screw from OUTBOARD, as v1 -- see [N] re the Nano).
    #      FWD hole pair: rail capture only (unchanged from v1).
    bmp_in, bmp_out = BMP_Y0, BMP_Y0 + BMP_DY                  # inboard 7.0 / outboard 11.0
    rails = box(-BMP_DX / 2.0 - WALL, -BMP_DX / 2.0, bmp_in - CL_BOARD, bmp_out, -WALL, BMP_DZ + WALL)
    rails = rails.fuse(box(BMP_DX / 2.0, BMP_DX / 2.0 + WALL, bmp_in - CL_BOARD, bmp_out, -WALL, BMP_DZ + WALL))
    rails = rails.fuse(box(-BMP_DX / 2.0 - WALL, BMP_DX / 2.0 + WALL, bmp_in - CL_BOARD - WALL, bmp_in - CL_BOARD, -WALL, BMP_DZ + WALL))
    bmp_cx, bmp_cz = 0.0, BMP_DZ / 2.0
    bmp_aft = [(bmp_cx + sx * BMP_HOLE_PX / 2.0, bmp_cz - BMP_HOLE_PZ / 2.0) for sx in (-1, 1)]
    rails = rails.fuse(standoff_y(bmp_aft, bmp_in, +1, BMP_HOLE_D))     # boss on the -y (inboard) side, head +y (outboard)
    parts.append(cap(as_solid(rails)))

    # ---- Nano: 2 side rails + 0.6 mm outboard lip tabs + Kapton strap.  1.21 mm to
    #      ID: no functional screw (see [N]).  Its inboard face is only 0.5 mm off the
    #      BMP388's outboard face, so a full-length end wall cannot exist (v1 drew one;
    #      the BMP cut left 0.2 mm).  v2: aft floor plate (Z -0.9..0) + a fwd end-wall
    #      segment past the BMP, and a TIE on each side into the BMP rails -- v1's Nano
    #      pocket touched nothing and was silently dropped from the export.
    nin, nout = NANO_Y0, NANO_Y0 + NANO_DY                    # inboard 11.5 / outboard 16.5
    ntop = min(NANO_DZ + WALL, CAP_Z0)
    nano = box(-NANO_DX / 2.0 - WALL, -NANO_DX / 2.0, nin - CL_BOARD, nout, -WALL, ntop)
    nano = nano.fuse(box(NANO_DX / 2.0, NANO_DX / 2.0 + WALL, nin - CL_BOARD, nout, -WALL, ntop))
    nano = nano.fuse(box(-NANO_DX / 2.0 - WALL, NANO_DX / 2.0 + WALL, nin - CL_BOARD - WALL, nout, -WALL, 0.0))   # aft floor
    nano = nano.fuse(box(-NANO_DX / 2.0 - WALL, NANO_DX / 2.0 + WALL, nin - CL_BOARD - WALL, nin - CL_BOARD,
                         BMP_DZ + WALL, ntop))                                                             # fwd end wall
    for sx in (-1, 1):                                        # tie: Nano rail -> BMP rail, clear of both boards
        xa, xb = sorted((sx * NANO_DX / 2.0, sx * (BMP_DX / 2.0 + WALL)))
        nano = nano.fuse(box(xa, xb, bmp_out - 0.5, nin + 0.5, -WALL, ntop))
    for zc in (5.0, NANO_DZ / 2.0, NANO_DZ - 5.0):
        for xa, xb in ((-NANO_DX / 2.0 - WALL, -NANO_DX / 2.0 + 1.6), (NANO_DX / 2.0 - 1.6, NANO_DX / 2.0 + WALL)):
            nano = nano.fuse(box(xa, xb, nout, nout + LIP, zc - 2.5, zc + 2.5))
    for sx in (-1, 1):
        for sz in (-1, 1):
            hx, hz = sx * NANO_HOLE_PX / 2.0, NANO_DZ / 2.0 + sz * NANO_HOLE_PZ / 2.0
            nano = nano.cut(Part.makeCylinder(NANO_HOLE_D / 2.0 + 0.3, 3.0, Vector(hx, nin - CL_BOARD - WALL - 0.5, hz), Vector(0, 1, 0)))
    parts.append(cap(as_solid(nano)))

    # ---- ADXL: 4 real standoffs, screw HEAD on the -y side (battery-gap side),
    #      bosses on the +y side; board clamped between.  Full 26 mm board (no servo).
    adxl_cx = ADXL_X0 + ADXL_DX / 2.0
    adxl_in = ADXL_Y0 + ADXL_DY                               # +y face -> standoff side
    adxl_h = [(adxl_cx + sx * ADXL_HOLE_PX / 2.0, ADXL_DZ / 2.0 + sz * ADXL_HOLE_PZ / 2.0)
              for sx in (-1, 1) for sz in (-1, 1)]
    adxl = box(ADXL_X0 - WALL, ADXL_X0 + ADXL_DX + WALL, ADXL_Y0 - CL_BOARD - WALL, ADXL_Y0 - CL_BOARD, -WALL, ADXL_DZ)  # -y back wall
    adxl = adxl.fuse(box(ADXL_X0 - WALL, ADXL_X0, ADXL_Y0 - CL_BOARD, ADXL_Y0 + ADXL_DY + CL_BOARD, -WALL, ADXL_DZ))     # W side
    adxl = adxl.fuse(box(ADXL_X0 + ADXL_DX, ADXL_X0 + ADXL_DX + WALL, ADXL_Y0 - CL_BOARD, ADXL_Y0 + ADXL_DY + CL_BOARD, -WALL, ADXL_DZ))  # E side
    adxl = adxl.fuse(standoff_y(adxl_h, adxl_in, -1, ADXL_HOLE_D))
    parts.append(cap(as_solid(adxl)))

    # ---- Piezo: 3-wall pocket for the breakout; screw the breakout from the
    #      -x (radial-INBOARD) side into 2 bosses -- nothing added outboard where
    #      the sound port + 1.2 mm skin gap are.  Round can nested, strap over it.
    px0, px1 = PIEZO_X0, PIEZO_X0 + PIEZO_DR                  # 3.0 .. 18.0
    pz = box(px0 - WALL, px1 + WALL, -PIEZO_DT / 2.0 - WALL, PIEZO_DT / 2.0 + WALL, -WALL, PIEZO_DZ + WALL)
    pz = pz.cut(box(px0, px1 + WALL + 1.0, -PIEZO_DT / 2.0, PIEZO_DT / 2.0, 0.0, PIEZO_DZ + 1.0))   # cavity
    pz = pz.cut(Part.makeCylinder(2.2, 8.0, Vector(px1 - 1.0, 0.0, PIEZO_DZ / 2.0), Vector(1, 0, 0)))  # sound port
    for sy in (-1, 1):
        yc = sy * PIEZO_HOLE_PY / 2.0
        # boss on the +x face of the -x wall, screw threads in from x < px0
        pz = pz.fuse(Part.makeCylinder(PIEZO_HOLE_D / 2.0 + 1.4, 2.6, Vector(px0 - 0.1, yc, PIEZO_HOLE_Z), Vector(1, 0, 0)))
        pz = pz.cut(Part.makeCylinder(PIEZO_HOLE_D / 2.0 - 0.2, 10.0, Vector(px0 - 3.0, yc, PIEZO_HOLE_Z), Vector(1, 0, 0)))
    parts.append(cap(as_solid(pz)))

    # ---- battery tray: inboard-open U-channel, 0.6 lip, JST slot
    bx0, bx1 = -BATT_DX / 2.0 - BATT_WALL, BATT_DX / 2.0 + BATT_WALL
    by_out, by_in = BATT_Y1 - BATT_DY, BATT_Y1                 # -15.5 .. -7.0
    bz0, bz1 = BATT_Z0 - BATT_WALL, BATT_Z0 + BATT_DZ + BATT_WALL
    tray = box(bx0, bx1, by_out - BATT_WALL, by_in + 0.01, bz0, bz1)
    tray = tray.cut(box(-BATT_DX / 2.0, BATT_DX / 2.0, by_out, by_in + 2.0, BATT_Z0, BATT_Z0 + BATT_DZ))
    tray = tray.cut(box(bx0 - 1, bx1 + 1, by_out - BATT_WALL - 1, by_out - LIP, bz0 - 1, bz1 + 1))
    tray = tray.cut(box(BATT_DX / 2.0 - JST_SLOT_W, bx1 + 1, by_in - JST_SLOT_H, by_in + 1, bz0 - 1, BATT_Z0 + 0.5))
    # tie plate: tray W wall -> spine (v1 hung the tray off the servo cradle)
    tray = tray.fuse(box(-17.0, bx0 + BATT_WALL / 2.0, by_in - 1.0, by_in, bz0, bz1))
    parts.append(cap(as_solid(tray)))

    # ---- reed-switch saddle on the tray's outboard skin: open groove, capsule
    #      half-proud toward the wall, Kapton strap round capsule + tray.  No snap
    #      (glass).  Groove runs REED_LEAD_Z past each end for the leads.
    rz0, rz1 = REED_Z0 - REED_LEAD_Z, REED_Z0 + REED_L + REED_LEAD_Z
    lip_face = by_out - LIP                                    # tray outboard face, -16.1
    rd = box(REED_X - REED_SADDLE_DX, REED_X + REED_SADDLE_DX, REED_YC, lip_face + 0.3, rz0, rz1)
    rd = rd.cut(cyl(REED_GROOVE_R, rz0 - 1.0, rz1 + 1.0, REED_X, REED_YC))
    parts.append(cap(as_solid(rd)))

    # ---- EbayCap mount: 2 axial M2 bosses (v1 SG90-ear positions, top at CAP_Z0).
    #      W column stands on the ADXL W wall + spine; E column on the piezo pocket
    #      roof; a cross-beam under the cap ties the two.
    mb = cyl(MOUNT_BOSS_R, ADXL_DZ, CAP_Z0, MOUNT_XW, 0.0)
    mb = mb.fuse(cyl(MOUNT_BOSS_R, PIEZO_DZ, CAP_Z0, MOUNT_XE, 0.0))
    mb = mb.fuse(box(MOUNT_XW, MOUNT_XE, -1.5, 1.5, CAP_Z0 - 3.0, CAP_Z0))
    for xc in (MOUNT_XW, MOUNT_XE):
        mb = mb.cut(cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, xc, 0.0))
    parts.append(cap(as_solid(mb)))

    # ---- small-parts shelf: open tray, north-centre strip
    sp = box(SP_X0 - WALL, SP_X1 + WALL, SP_Y0 - WALL, SP_Y1 + WALL, -WALL, SP_Z1)
    sp = sp.cut(box(SP_X0, SP_X1, SP_Y0, SP_Y1 + 2.0, 0.0, SP_Z1 + 1.0))
    parts.append(cap(as_solid(sp)))

    sled = parts[0].multiFuse(parts[1:]).removeSplitter()

    # RAW overlap of the as-drawn sled with each component keep-out, BEFORE any
    # trim.  This is the honest fit check: >0 means a pocket wall / boss / rail was
    # drawn into a component's space and has to be cleared (see [I]).
    env = dict((n, f()) for n, f in COMPONENTS)
    raw = {}
    for n, e in env.items():
        c = sled.common(e)
        raw[n] = c.Volume if c.Solids else 0.0

    # trim the overlaps against the RIGID parts so the exported solid is
    # manufacturable as-is.  SmallParts is a conformable allowance (wiring + tiny
    # PCBs) -- it yields to structure, so it is NOT cut; [I] reports how much.
    for n in RIGID:
        sled = sled.cut(env[n])

    # CONNECTIVITY -- v1 lost its Nano pocket here without a word.  Never again.
    sol = sled.Solids
    log.append("  connectivity: %d solid(s)  %s" % (len(sol), ", ".join("%.1f" % s.Volume for s in sol)))
    if len(sol) != 1:
        raise RuntimeError("sled is %d disconnected solids (%s mm3) -- tie them in"
                           % (len(sol), ", ".join("%.1f" % s.Volume for s in sol)))
    return sol[0], raw

# ================================================================ verification
def main():
    log = []
    P = log.append
    P("=" * 78)
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (v3 repack, no servo, reed)" % REV)
    P("=" * 78)
    P("")
    P("frame: avbay_packing_build_report_v2.txt  (Z=0 aft, +Z to nose, +x E, +y N)")
    P("constraint: component zone Z 0..%.0f held -- no length growth" % ZONE_Z1)
    P("charger BQ25302 + its wall slot deleted; battery charges off-vehicle (JST-PH)")
    P("")

    doc = App.newDocument("PhoenixABS40-43_avbay_sled_v2")

    comp = dict((n, f()) for n, f in COMPONENTS)
    cmesh = dict((n, mesh_of(s)) for n, s in comp.items())

    P("[1] build + heal")
    sled, raw = build_sled(log)
    sled = heal(sled, "Sled", log)
    if len(sled.Solids) != 1:
        raise RuntimeError("heal split the sled into %d solids" % len(sled.Solids))
    smesh = mesh_of(sled)

    P("")
    P("[2] pack -- component list  (dx.dy.dz  Zmin  Zmax  Rmax)")
    for n, s in comp.items():
        bb = cmesh[n].BoundBox
        P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f"
          % (n, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax, rmax_mesh(cmesh[n])))
    sbb = smesh.BoundBox
    P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f   <- the sled"
      % ("Sled", sbb.XLength, sbb.YLength, sbb.ZLength, sbb.ZMin, sbb.ZMax, rmax_mesh(smesh)))

    P("")
    P("[0] CONTAINMENT  (Rmax vs %.1f moving / %.1f ID)" % (R_MAX_MOVING, R_AF_I))
    strap = {"Nano_ESP32", "Piezo", "ReedSwitch"}   # strap-retained against the skin
    zmax = 0.0
    for n, s in comp.items():
        r = rmax_mesh(cmesh[n]); zmax = max(zmax, cmesh[n].BoundBox.ZMax)
        note = "strap-retained (outboard of the sled skin)" if n in strap else ""
        tag = "PASS" if r <= R_MAX_MOVING + 1e-6 else ("past moving" if r <= R_AF_I else "*** PAST ID ***")
        P("  %-12s Rmax %6.2f  toID %5.2f   %-5s %s" % (n, r, R_AF_I - r, tag, note))
    rs = rmax_mesh(smesh)
    P("  %-12s Rmax %6.2f  toID %5.2f   %-5s" % ("Sled", rs, R_AF_I - rs,
      "PASS" if rs <= SLED_RMAX + 0.05 else "FAIL"))
    P("  component zone  Z 0.0 .. %.1f   %s" % (zmax, "PASS" if zmax <= ZONE_Z1 + 1e-6 else "*** OVER ***"))
    # above the EbayCap underside only the spine key may exist (v1 top-slab footprint)
    above = sled.common(box(-30, 30, -30, 30, CAP_Z0 + 0.01, ZONE_Z1 + 5))
    key = clip_bore(box(-19.0, -16.6, -12.0, 12.0, CAP_Z0 + 0.01, ZONE_Z1 - 0.6))
    stray = above.cut(key); sv = stray.Volume if stray.Solids else 0.0
    P("  above EbayCap face Z %.1f: %.1f mm3, of which outside the spine key %.2f   %s"
      % (CAP_Z0, above.Volume if above.Solids else 0.0, sv, "PASS" if sv < 0.01 else "FAIL"))
    top = sled.common(box(-30, 30, -30, 30, CAP_Z0 - 0.2, CAP_Z0))
    for xc in (MOUNT_XW, MOUNT_XE):
        ring = cyl(MOUNT_BOSS_R - 0.1, CAP_Z0 - 0.2, CAP_Z0, xc, 0.0).cut(cyl(MOUNT_HOLE_D / 2.0, CAP_Z0 - 1, CAP_Z0 + 1, xc, 0.0))
        c = top.common(ring); f = (c.Volume if c.Solids else 0.0) / ring.Volume
        P("  EbayCap M2 boss (%.1f, 0.0) seated at Z %.1f: %.0f %% of the boss face present   %s"
          % (xc, CAP_Z0, 100 * f, "PASS" if f > 0.95 else "FAIL"))

    P("")
    P("[R] REED SWITCH -- arming by external magnet")
    rr = rmax_mesh(cmesh["ReedSwitch"])
    P("  capsule %.0f x d%.0f, axis Z, at (x %.1f, y %.1f), Z %.1f..%.1f" % (REED_L, REED_D, REED_X, REED_YC, REED_Z0, REED_Z0 + REED_L))
    P("  capsule outboard face R %.2f -> %.2f to ID + 1.5 wall = %.2f mm magnet-to-glass" % (rr, R_AF_I - rr, R_AF_I - rr + 1.5))
    P("  groove floor to battery pocket: %.2f mm (saddle %.2f + tray lip %.2f)"
      % ((BATT_Y1 - BATT_DY) - (REED_YC + REED_GROOVE_R), (BATT_Y1 - BATT_DY - LIP) - (REED_YC + REED_GROOVE_R), LIP))
    P("  D9aft v2 airframe: disc top at station 10.5 = sled Z 50.3 -> reed at stations %.1f..%.1f,"
      % (10.5 + 50.3 - (REED_Z0 + REED_L), 10.5 + 50.3 - REED_Z0))
    P("  on the -y face = 90 deg from the witness notch (notch at +x).  Mark ARM there.")

    P("")
    P("[I] FIT  --  RAW = the as-drawn sled overlapping each component keep-out,")
    P("           BEFORE trim.  RAW>0 is expected: it is pocket walls / rails /")
    P("           bosses reaching into the board's space.  For the %d RIGID parts" % len(RIGID))
    P("           that volume is then cut away (post-cut common -> 0); the risk it")
    P("           leaves a wall too thin is flagged in [N], not yet auto-checked.")
    P("           SmallParts is a conformable allowance -- it is NOT cut; its RAW is")
    P("           how much wiring volume yields to structure.")
    for n in comp:
        rv = raw.get(n, 0.0)
        pc = sled.common(comp[n]); tv = pc.Volume if pc.Solids else 0.0
        kind = "allowance yields" if n == "SmallParts" else "post-cut %.1f" % tv
        P("  %-12s RAW %8.1f mm3   (%s)" % (n, rv, kind))
    P("  component-vs-component clashes:")
    cn = list(comp.keys()); cc = 0
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            cm = comp[cn[i]].common(comp[cn[j]]); vv = cm.Volume if cm.Solids else 0.0
            if vv > 1.0:
                cc += 1; P("    CLASH %s <-> %s  %.1f mm3" % (cn[i], cn[j], vv))
    if not cc:
        P("    none")

    P("")
    P("[M] MASS")
    m = sled.Volume * RHO
    P("  sled (ABS, solid-equiv)  %8.1f mm3   %6.1f g" % (sled.Volume, m))
    P("  + fasteners: 2x M2.5 (BMP388 aft pair), 4x M2.5 (ADXL), 2x M2 (piezo breakout),")
    P("               2x M2x10 (EbayCap, axial); Nano + reed = strap, no screws; 1x JST-PH pigtail")
    P("  electronics: reed %.0f g now its own line; SmallParts allowance 14 -> 13 g" % REED_MASS)

    P("")
    P("[N] NOTES / OPEN")
    P("  * v2 vs v1: servo + cradle + knob ref removed (D9aft: e-bay fires nothing).  The")
    P("    EbayCap M2 bosses stay at v1's SG90-ear (x, y), top Z %.1f -> the D9aft v1/v2" % CAP_Z0)
    P("    EbayCap fits unchanged (its pocket has spare voids where the cradle uprights were).")
    P("  * v1 EXPORT WAS MISSING THE NANO POCKET (disconnected, dropped by as_solid).  The")
    P("    D9aft v1/v2 checks exec'd that same sled, so they never saw it either.")
    P("  * RETENTION:")
    P("      screw-down  BMP388  -- aft hole pair, boss on the inboard face, screw from")
    P("                             OUTBOARD; fwd pair = rail capture")
    P("                  ADXL375 -- 4 bosses on the +y face, screw head on the -y side")
    P("                  Piezo breakout -- 2 bosses, screw from the radial-INBOARD side")
    P("                             (nothing added by the sound port / skin)")
    P("                  EbayCap -- 2 axial M2x10 from the cap top into the mount bosses")
    P("      strap       Nano (1.21 to ID) -- rails + %.1f lip + Kapton; its 4 holes get" % LIP)
    P("                             inboard dimples for optional shear pins, no retention load")
    P("                  Piezo can (1.18) -- nested + strap over the 11 mm can")
    P("                  Reed -- open groove on the tray skin + Kapton round capsule + tray")
    P("      tray        Battery -- inboard-open U-channel + %.1f lip + JST-PH pigtail (swap)" % LIP)
    P("  * OPEN (inherited from v1): the BMP388 aft screws are driven from OUTBOARD, but the")
    P("    Nano sits 0.5 mm off the BMP388's outboard face -- no room for the heads.  Needs a")
    P("    decision (screw before the Nano goes in with low heads, flip to inboard + nuts, or")
    P("    move the BMP inboard into the space the servo freed).")
    P("  * Nano backstop is now the aft floor + fwd end-wall segment only; along Z 0..40 its")
    P("    inboard face rests 0.5 mm off the BMP388 -- put a Kapton/foam layer between.")
    P("  * reed leads leave the groove at both ends (Z %.0f / %.0f); route them round the tray's"
      % (REED_Z0 - REED_LEAD_Z, REED_Z0 + REED_L + REED_LEAD_Z))
    P("    E edge (clear of the JST slot) to the Nano.  Bend leads >= 2 mm from the glass.")
    P("  * hole PATTERNS are still ASSUMED (NANO_HOLE_P* / BMP_HOLE_P* / ADXL_HOLE_P* /")
    P("    PIEZO_HOLE_*).  Topology + screw direction are real; the boss (x,z) centres move")
    P("    when the measured patterns land -- a constants-only edit.")
    P("  * wall thickness after the pocket-clearance cut is not auto-checked -- eyeball the")
    P("    thin walls in CAD before printing.")
    P("  * freed by the servo: the centre Z 26..42 (x -12..8, y -6..6) is empty -- room to")
    P("    move SmallParts or the BMP388 later, or to shorten the bay.")
    P("  * small-parts = ~13 g allowance in an open shelf; measure S7V8F5 / microSD rdr /")
    P("    C1 / SW1 / SW2 for real before this is frozen.")
    P("  * NOT modelled yet: static-port vent path; print orientation / support / split.")

    P("")
    P("[E] EXPORT")
    os.makedirs(AV_MODELS, exist_ok=True)
    base = os.path.join(AV_MODELS, "PhoenixABS40-43_avbay_ElectronicsSled_%s" % REV)
    sled.exportStep(base + ".step")
    smesh.write(base + ".stl")
    P("  %s .step + .stl" % os.path.basename(base))
    # FCStd: sled + component envelopes (flight position)
    Part.show(sled, "Sled")
    for n, s in comp.items():
        Part.show(s, "env_" + n)
    doc.recompute()
    fc = os.path.join(AVIONICS, "PhoenixABS40-43_avbay_sled_%s.FCStd" % REV)
    doc.saveAs(fc)
    P("  FCStd -> Avionics/%s  (Sled + env_* envelopes)" % os.path.basename(fc))
    # assembly viz
    comb = sled
    for n, s in comp.items():
        comb = comb.fuse(s)
    am = mesh_of(comb)
    am.write(base.replace("ElectronicsSled", "sled_ASSEMBLY") + ".stl")
    P("  sled_ASSEMBLY_%s.stl  (sled + component envelopes, flight position)" % REV)

    rpt = "\n".join(log)
    with open(os.path.join(AVIONICS, "avbay_sled_build_report_%s.txt" % REV), "w") as fh:
        fh.write(rpt + "\n")
    print(rpt)

main()

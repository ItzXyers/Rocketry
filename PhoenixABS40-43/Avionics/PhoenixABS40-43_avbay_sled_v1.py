# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v1  (the "scaffold to screw
the chips into").

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
REV = "v1"
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

# SERVO -- fixed, knob-aligned (v2 numbers, unchanged) -----------------------
SERVO_X0, SERVO_X1 = -14.0, 8.8
SERVO_Y            = 6.0
SERVO_Z0, SERVO_Z1 = 25.3, 48.0
SERVO_TAB_DX, SERVO_TAB_DZ = 2.6, 2.4
SERVO_TAB_Z0       = 45.4
SERVO_TAB_HOLE_D   = 2.0                  # SG90 tab hole -- M2
SERVO_TAB_AXIS     = "z"                  # user: tab screws are AXIAL, inserted top-down (+Z side)
SERVO_TAB_XW, SERVO_TAB_XE = SERVO_X0 - 1.3, SERVO_X1 + 1.3   # the two ear-hole centres

# NANO ESP32 45x18x5 -- north, outboard.  1.21 mm to ID -> NO outboard fastener
#   room: strap + pocket retention.  4 holes noted for a future recessed variant.
NANO_DX, NANO_DY, NANO_DZ = 18.0, 5.0, 45.0
NANO_Y0 = 11.5                            # inboard face
NANO_Z0 = 0.0
NANO_HOLES = 4
NANO_HOLE_D     = 2.0
NANO_HOLE_PX, NANO_HOLE_PZ = 14.0, 40.0   # 4-corner pitch (CONFIRM)

# BMP388 40x22x4 -- north, inboard of the Nano, over the servo top ----------
BMP_DX, BMP_DY, BMP_DZ = 22.0, 4.0, 40.0
BMP_Y0 = 7.0
BMP_Z0 = 0.0
BMP_HOLES = 4                             # 4-corner; only the AFT pair clears the servo
BMP_HOLE_D     = 2.5                      # M2.5 (CONFIRM)
BMP_HOLE_PX, BMP_HOLE_PZ = 16.0, 34.0

# BATTERY 40.5x20x8.5 -- south, alone, pulled in 0.7 from the v2 corner -----
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_Z0 = 0.0
BATT_WALL = 0.8
JST_SLOT_W, JST_SLOT_H = 6.0, 3.0

# ADXL375 26x18x4 -- aft-of-servo centre band, shifted WEST -----------------
ADXL_DX, ADXL_DY, ADXL_DZ = 18.0, 4.0, 26.0
ADXL_X0 = -16.0
ADXL_Y0 = -2.0
ADXL_Z0 = 0.0
ADXL_CLEAR_Z = 25.3                       # servo starts here; board is 26 -> 0.7 trimmed/clocked
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

# SMALL PARTS ~14 g -- north-centre strip (between ADXL top and the BMP388 pocket),
#   east of the spine; open shelf + strap.  UNMEASURED allowance -- see [N].
SP_X0, SP_X1 = -15.5, -2.0
SP_Y0, SP_Y1 = 2.2, 5.3
SP_Z0, SP_Z1 = 0.0, 22.0

# reference: ejection knob just forward of the zone
KNOB_AX_X, KNOB_R = -8.0, 10.0
KNOB_Z0, KNOB_Z1 = 48.0, 60.5

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
def env_servo():
    s = box(SERVO_X0, SERVO_X1, -SERVO_Y, SERVO_Y, SERVO_Z0, SERVO_Z1)
    tW = box(SERVO_X0 - SERVO_TAB_DX, SERVO_X0, -5.5, 5.5, SERVO_TAB_Z0, SERVO_TAB_Z0 + SERVO_TAB_DZ)
    tE = box(SERVO_X1, SERVO_X1 + SERVO_TAB_DX, -5.5, 5.5, SERVO_TAB_Z0, SERVO_TAB_Z0 + SERVO_TAB_DZ)
    return as_solid(s.fuse(tW).fuse(tE))

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

def env_knob():
    return cyl(KNOB_R, KNOB_Z0, KNOB_Z1, KNOB_AX_X, 0.0)

COMPONENTS = [
    ("Servo_SG90",  env_servo),
    ("Nano_ESP32",  env_nano),
    ("BMP388",      env_bmp),
    ("Battery",     env_batt),
    ("ADXL375",     env_adxl),
    ("Piezo",       env_piezo),
    ("SmallParts",  env_small),
]

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
    """One printed piece.  Aft board-carrier (Z 0..25.3) + forward servo cradle
    (Z 25.3..48), tied by a spine down the west wall."""
    parts = []

    # ---- spine down the west side
    parts.append(clip_bore(box(-19.0, -16.6, -12.0, 12.0, 0.0, ZONE_Z1 - 0.6)))

    # ---- BMP388: full-length side rails + inboard end wall; 2 real standoffs at
    #      the AFT hole pair (screw from OUTBOARD -- 4.4 mm to ID, countersunk).
    #      The FWD hole pair sits over the servo top -> rail capture only.
    bmp_in, bmp_out = BMP_Y0, BMP_Y0 + BMP_DY                  # inboard 7.0 / outboard 11.0
    rails = box(-BMP_DX / 2.0 - WALL, -BMP_DX / 2.0, bmp_in - CL_BOARD, bmp_out, -WALL, BMP_DZ + WALL)
    rails = rails.fuse(box(BMP_DX / 2.0, BMP_DX / 2.0 + WALL, bmp_in - CL_BOARD, bmp_out, -WALL, BMP_DZ + WALL))
    rails = rails.fuse(box(-BMP_DX / 2.0 - WALL, BMP_DX / 2.0 + WALL, bmp_in - CL_BOARD - WALL, bmp_in - CL_BOARD, -WALL, BMP_DZ + WALL))
    bmp_cx, bmp_cz = 0.0, BMP_DZ / 2.0
    bmp_aft = [(bmp_cx + sx * BMP_HOLE_PX / 2.0, bmp_cz - BMP_HOLE_PZ / 2.0) for sx in (-1, 1)]
    rails = rails.fuse(standoff_y(bmp_aft, bmp_in, +1, BMP_HOLE_D))     # boss on the -y (inboard) side, head +y (outboard)
    parts.append(clip_bore(as_solid(rails)))

    # ---- Nano: pocket (2 side rails + inboard end wall) + 0.6 mm outboard lip
    #      tabs + Kapton strap.  1.21 mm to ID: NO functional screw is possible
    #      (see [N]); the 4 hole positions get shallow inboard clearance dimples so
    #      a builder can add shear pins into the strap side if wanted.
    nin, nout = NANO_Y0, NANO_Y0 + NANO_DY                    # inboard 11.5 / outboard 16.5
    nano = box(-NANO_DX / 2.0 - WALL, -NANO_DX / 2.0, nin - CL_BOARD, nout, -WALL, NANO_DZ + WALL)
    nano = nano.fuse(box(NANO_DX / 2.0, NANO_DX / 2.0 + WALL, nin - CL_BOARD, nout, -WALL, NANO_DZ + WALL))
    nano = nano.fuse(box(-NANO_DX / 2.0 - WALL, NANO_DX / 2.0 + WALL, nin - CL_BOARD - WALL, nin - CL_BOARD, -WALL, NANO_DZ + WALL))
    for zc in (5.0, NANO_DZ / 2.0, NANO_DZ - 5.0):
        for xa, xb in ((-NANO_DX / 2.0 - WALL, -NANO_DX / 2.0 + 1.6), (NANO_DX / 2.0 - 1.6, NANO_DX / 2.0 + WALL)):
            nano = nano.fuse(box(xa, xb, nout, nout + LIP, zc - 2.5, zc + 2.5))
    for sx in (-1, 1):
        for sz in (-1, 1):
            hx, hz = sx * NANO_HOLE_PX / 2.0, NANO_DZ / 2.0 + sz * NANO_HOLE_PZ / 2.0
            nano = nano.cut(Part.makeCylinder(NANO_HOLE_D / 2.0 + 0.3, 3.0, Vector(hx, nin - CL_BOARD - WALL - 0.5, hz), Vector(0, 1, 0)))
    parts.append(clip_bore(as_solid(nano)))

    # ---- ADXL: 4 real standoffs, screw HEAD on the -y side (battery-gap side),
    #      bosses on the +y side; board clamped between.  All 4 holes clear the servo.
    adxl_cx = ADXL_X0 + ADXL_DX / 2.0
    adxl_in = ADXL_Y0 + ADXL_DY                               # +y face -> standoff side
    adxl_h = [(adxl_cx + sx * ADXL_HOLE_PX / 2.0, ADXL_DZ / 2.0 + sz * ADXL_HOLE_PZ / 2.0)
              for sx in (-1, 1) for sz in (-1, 1)]
    adxl = box(ADXL_X0 - WALL, ADXL_X0 + ADXL_DX + WALL, ADXL_Y0 - CL_BOARD - WALL, ADXL_Y0 - CL_BOARD, -WALL, ADXL_CLEAR_Z)  # -y back wall
    adxl = adxl.fuse(box(ADXL_X0 - WALL, ADXL_X0, ADXL_Y0 - CL_BOARD, ADXL_Y0 + ADXL_DY + CL_BOARD, -WALL, ADXL_CLEAR_Z))     # W side
    adxl = adxl.fuse(box(ADXL_X0 + ADXL_DX, ADXL_X0 + ADXL_DX + WALL, ADXL_Y0 - CL_BOARD, ADXL_Y0 + ADXL_DY + CL_BOARD, -WALL, ADXL_CLEAR_Z))  # E side
    adxl = adxl.fuse(standoff_y(adxl_h, adxl_in, -1, ADXL_HOLE_D))
    parts.append(clip_bore(as_solid(adxl)))

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
    parts.append(clip_bore(as_solid(pz)))

    # ---- battery tray: inboard-open U-channel, 0.6 lip, JST slot
    bx0, bx1 = -BATT_DX / 2.0 - BATT_WALL, BATT_DX / 2.0 + BATT_WALL
    by_out, by_in = BATT_Y1 - BATT_DY, BATT_Y1                 # -15.5 .. -7.0
    bz0, bz1 = BATT_Z0 - BATT_WALL, BATT_Z0 + BATT_DZ + BATT_WALL
    tray = box(bx0, bx1, by_out - BATT_WALL, by_in + 0.01, bz0, bz1)
    tray = tray.cut(box(-BATT_DX / 2.0, BATT_DX / 2.0, by_out, by_in + 2.0, BATT_Z0, BATT_Z0 + BATT_DZ))
    tray = tray.cut(box(bx0 - 1, bx1 + 1, by_out - BATT_WALL - 1, by_out - LIP, bz0 - 1, bz1 + 1))
    tray = tray.cut(box(BATT_DX / 2.0 - JST_SLOT_W, bx1 + 1, by_in - JST_SLOT_H, by_in + 1, bz0 - 1, BATT_Z0 + 0.5))
    parts.append(clip_bore(as_solid(tray)))

    # ---- servo cradle: shelf under (-y) + aft wall + 2 side uprights; the SG90
    #      ear screws are AXIAL (user), inserted from the +Z (top) side, threading
    #      into a boss just AFT of each ear at Z 43..45.4.
    cr = box(SERVO_X0 - WALL, SERVO_X1 + WALL, -SERVO_Y - CL_SLIDE - WALL, -SERVO_Y - CL_SLIDE, SERVO_Z0 - WALL, SERVO_Z1 - 0.6)
    cr = cr.fuse(box(SERVO_X0 - WALL, SERVO_X1 + WALL, -SERVO_Y - CL_SLIDE, SERVO_Y, SERVO_Z0 - WALL, SERVO_Z0))  # aft wall
    for x0u in (SERVO_X0 - WALL, SERVO_X1):
        cr = cr.fuse(box(x0u, x0u + WALL, -SERVO_Y - CL_SLIDE, SERVO_Y + CL_SLIDE, SERVO_Z0 - WALL, SERVO_TAB_Z0 + SERVO_TAB_DZ))
    for xc in (SERVO_TAB_XW, SERVO_TAB_XE):
        # boss just aft of the ear, tapped +Z
        cr = cr.fuse(Part.makeCylinder(SERVO_TAB_HOLE_D / 2.0 + 1.6, SERVO_TAB_Z0 - (SERVO_Z0 + 8.0),
                     Vector(xc, 0.0, SERVO_Z0 + 8.0)))
        cr = cr.cut(Part.makeCylinder(SERVO_TAB_HOLE_D / 2.0 - 0.2, 40.0, Vector(xc, 0.0, SERVO_Z0)))
    parts.append(clip_bore(as_solid(cr)))

    # ---- small-parts shelf: open tray, west crescent + north-centre strip
    sp = box(SP_X0 - WALL, SP_X1 + WALL, SP_Y0 - WALL, SP_Y1 + WALL, -WALL, SP_Z1)
    sp = sp.cut(box(SP_X0, SP_X1, SP_Y0, SP_Y1 + 2.0, 0.0, SP_Z1 + 1.0))
    parts.append(clip_bore(as_solid(sp)))

    sled = parts[0]
    for p in parts[1:]:
        sled = sled.fuse(p)
    sled = as_solid(sled)

    # RAW overlap of the as-drawn sled with each component keep-out, BEFORE any
    # trim.  This is the honest fit check: >0 means a pocket wall / boss / rail was
    # drawn into a component's space and has to be cleared (see [I]).
    raw = {}
    adxl_here = env_adxl().common(box(-30, 30, -30, 30, -5, ADXL_CLEAR_Z))
    for n, e in (("Servo_SG90", env_servo()), ("Nano_ESP32", env_nano()), ("BMP388", env_bmp()),
                 ("Battery", env_batt()), ("Piezo", env_piezo()), ("ADXL375", adxl_here),
                 ("SmallParts", env_small())):
        c = sled.common(e)
        raw[n] = c.Volume if c.Solids else 0.0

    # trim the overlaps against the RIGID parts so the exported solid is
    # manufacturable as-is.  SmallParts is a conformable 14 g allowance (wiring +
    # tiny PCBs) -- it yields to structure, so it is NOT cut; [I] reports how much.
    for e in (env_servo(), env_nano(), env_bmp(), env_batt(), env_piezo(), adxl_here):
        sled = sled.cut(e)
    return as_solid(sled), raw

# ================================================================ verification
def main():
    log = []
    P = log.append
    P("=" * 78)
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (v3 repack)" % REV)
    P("=" * 78)
    P("")
    P("frame: avbay_packing_build_report_v2.txt  (Z=0 aft, +Z to nose, +x E, +y N)")
    P("constraint: component zone Z 0..%.0f held -- no length growth" % ZONE_Z1)
    P("charger BQ25302 + its wall slot deleted; battery charges off-vehicle (JST-PH)")
    P("")

    doc = App.newDocument("PhoenixABS40-43_avbay_sled")

    comp = dict((n, f()) for n, f in COMPONENTS)
    cmesh = dict((n, mesh_of(s)) for n, s in comp.items())
    knob = env_knob()

    P("[1] build + heal")
    sled, raw = build_sled(log)
    sled = heal(sled, "Sled", log)
    smesh = mesh_of(sled)

    P("")
    P("[2] v3 pack -- component list  (dx.dy.dz  Zmin  Zmax  Rmax)")
    for n, s in comp.items():
        bb = cmesh[n].BoundBox
        P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f"
          % (n, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax, rmax_mesh(cmesh[n])))
    sbb = smesh.BoundBox
    P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f   <- the sled"
      % ("Sled", sbb.XLength, sbb.YLength, sbb.ZLength, sbb.ZMin, sbb.ZMax, rmax_mesh(smesh)))

    P("")
    P("[0] CONTAINMENT  (Rmax vs %.1f moving / %.1f ID)" % (R_MAX_MOVING, R_AF_I))
    strap = {"Nano_ESP32", "Piezo"}   # genuinely against the skin (<1.3 mm to ID)
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

    P("")
    P("[I] FIT  --  RAW = the as-drawn sled overlapping each component keep-out,")
    P("           BEFORE trim.  RAW>0 is expected: it is pocket walls / rails /")
    P("           bosses reaching into the board's space.  For the 6 RIGID parts")
    P("           that volume is then cut away (post-cut common -> 0); the risk it")
    P("           leaves a wall too thin is flagged in [N], not yet auto-checked.")
    P("           SmallParts is a conformable allowance -- it is NOT cut; its RAW is")
    P("           how much wiring volume yields to structure.")
    pc_env = dict(comp)
    pc_env["ADXL375"] = comp["ADXL375"].common(box(-30, 30, -30, 30, -5, ADXL_CLEAR_Z))  # 0.7 mm Z>25.3 sliver is a doc'd trim
    for n in ("Servo_SG90", "Nano_ESP32", "BMP388", "Battery", "ADXL375", "Piezo", "SmallParts"):
        rv = raw.get(n, 0.0)
        pc = sled.common(pc_env[n]); tv = pc.Volume if pc.Solids else 0.0
        kind = "allowance yields" if n == "SmallParts" else "post-cut %.1f" % tv
        P("  %-12s RAW %8.1f mm3   (%s)" % (n, rv, kind))
    c = sled.common(knob); v = c.Volume if c.Solids else 0.0
    P("  %-12s RAW %8.1f mm3%s" % ("Knob(ref)", v, "  <-- CLASH" if v > 30 else "  (clear)"))
    P("  component-vs-component clashes  (ADXL clipped to its real Z<=%.1f):" % ADXL_CLEAR_Z)
    cclip = dict(comp)
    cclip["ADXL375"] = comp["ADXL375"].common(box(-30, 30, -30, 30, -5, ADXL_CLEAR_Z))
    cn = list(cclip.keys()); cc = 0
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            cm = cclip[cn[i]].common(cclip[cn[j]]); vv = cm.Volume if cm.Solids else 0.0
            if vv > 1.0:
                cc += 1; P("    CLASH %s <-> %s  %.1f mm3" % (cn[i], cn[j], vv))
    if not cc:
        P("    none")

    P("")
    P("[M] MASS")
    m = sled.Volume * RHO
    P("  sled (ABS, solid-equiv)  %8.1f mm3   %6.1f g" % (sled.Volume, m))
    P("  + fasteners: 2x M2.5 (BMP388 aft pair), 4x M2.5 (ADXL), 2x M2 (piezo breakout),")
    P("               2x M2 (SG90 ears, axial); Nano = strap, no screws; 1x JST-PH pigtail")

    P("")
    P("[N] NOTES / OPEN")
    P("  * RETENTION:")
    P("      screw-down  BMP388  -- aft hole pair, boss on the inboard face, screw from")
    P("                             OUTBOARD (4.4 to ID, countersunk); fwd pair = rails")
    P("                             over the servo top")
    P("                  ADXL375 -- 4 bosses on the +y face, screw head on the -y side")
    P("                  Piezo breakout -- 2 bosses, screw from the radial-INBOARD side")
    P("                             (nothing added by the sound port / skin)")
    P("                  SG90 ears -- 2 axial screws from the +Z side into aft bosses")
    P("      strap       Nano (1.21 to ID) -- rails + %.1f lip + Kapton; its 4 holes get" % LIP)
    P("                             inboard dimples for optional shear pins, no retention load")
    P("                  Piezo can (1.18) -- nested + strap over the 11 mm can")
    P("      tray        Battery -- inboard-open U-channel + %.1f lip + JST-PH pigtail (swap)" % LIP)
    P("  * hole PATTERNS are still ASSUMED (NANO_HOLE_P* / BMP_HOLE_P* / ADXL_HOLE_P* /")
    P("    PIEZO_HOLE_* / SERVO_TAB_*).  Topology + screw direction are now real; the boss")
    P("    (x,z) centres move when the measured patterns land -- a constants-only edit.")
    P("  * wall thickness after the pocket-clearance cut is not auto-checked -- eyeball the")
    P("    thin walls (esp. the BMP388 rails over the servo) in CAD before printing.")
    P("  * BMP388 rides over the servo top at 1.0 mm (Z 25.3..40) -- under the 1.5 design gap.")
    P("  * ADXL is 26 mm; 25.3 mm clear before the servo -> trim the PCB edge or clock the")
    P("    Qwiic stub 0.7 mm.  Pocket is modelled at 25.3.")
    P("  * static port: north lobe at Z 12 is now Nano+BMP388.  Re-site the airframe port to")
    P("    the EAST crescent ~Z 12 (fin gap); baro only needs shared air (cassette [S]).")
    P("  * small-parts = ~14 g allowance in an open shelf; measure S7V8F5 / microSD rdr /")
    P("    C1 / SW1 / SW2 for real before this is frozen.")
    P("  * NOT modelled yet: sled-to-anchor-coupler (fwd) and sled-to-aft-closure (aft)")
    P("    registration; static-port vent path; print orientation / support / split.")

    P("")
    P("[E] EXPORT")
    os.makedirs(AV_MODELS, exist_ok=True)
    base = os.path.join(AV_MODELS, "PhoenixABS40-43_avbay_ElectronicsSled_%s" % REV)
    sled.exportStep(base + ".step")
    smesh.write(base + ".stl")
    P("  %s .step + .stl" % os.path.basename(base))
    # assembly viz: sled + component envelopes
    asm = App.newDocument("asm")
    Part.show(sled, "Sled")
    for n, s in comp.items():
        Part.show(s, n)
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

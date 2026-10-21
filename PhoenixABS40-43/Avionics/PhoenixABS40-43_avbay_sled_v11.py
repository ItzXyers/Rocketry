# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v11  (the soldered harness presses in from ONE side)

v11 = a new layout, not a v10 patch (2026-10-19, user: "Soldering's done ... dropped the reed switch, the
button switch and the microsd card"; "the back of the piezo now has a transistor soldered"; "more small parts
storage room"; "press everything in ... the entire thing needs to fit as is").  Answers given:
  * TO-92 (BC337, Q1) is soldered BENT FLAT on the piezo board's back.
  * Loose small parts: S7V8F5, C1 470 uF 16 V ("google" -> largest common can d10 x 13 ASSUMED),
    R1/R2/R11/R12 inline in heat shrink.  Q3 / reed / SW2 / microSD gone.  The board powers up when the
    battery is plugged in.
  * Insertion: ONE side, all at once.  E-bay length kept.
  * Lead lengths: "just give me as much space as possible".
  * Qwiic kept: BOTH BMP388 plugs used, ADXL375 only its "top" plug.
  * The ESP32 must be at the absolute BOTTOM of the stack: the power-input JST-PH is permanently on it, at the
    USB-C end, 6 mm wide, 24 mm tall with the plug in, LEFT of the USB-C looking at the port head-on (+y here).
  * Room for the cables coming off the ESP32.

LAYOUT (x = depth: -x = spine / bottom, +x = open face = the static + sound port side = press-in direction)
  spine (-x) | Nano ESP32, parts up, USB-C + JST FORWARD | 5.7 mm wire / storage gap | BMP388 FLIPPED (parts
  down, PCB back up) | ADXL375 glued flat on the BMP's PCB back, plug forward | battery | bore (+x)
  Aft deck (behind the piezo): storage for S7V8F5 + C1 + resistors.  Piezo unchanged at the sound port; its back
  plate is now a FRAME (hole-end bar + bottom rail) so the TO-92 sits in an open window.  The Nano's JST stands
  in an open CHIMNEY at the fwd end -> the battery is plugged in LAST, from the open face, through it.
  Every part goes in along +x, deepest first: nothing printed may stand inside the footprint of a part that
  goes in BEFORE it -> each support sits outside the widths below it (Nano 18 < BMP 22; the 18-wide ADXL
  therefore rides on the BMP, the 20-wide battery on the ADXL + foam).
  EbayCap EAST screw boss (10.1, 0) is DELETED: it sits inside the chimney's x range and over the battery,
  nothing can carry it up to Z 39.  The cap is held by the WEST screw + the spine key; do not fit the east
  screw.  Every other interface D9aft reads is unchanged (seat Z -22.8, cap face Z 45.4, W boss, spine key,
  sound port Z -12.1 / 0 deg, static port Z 30 / 0 deg).  SERVO_TAB_X* / MOUNT_X* names kept for D9aft.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" <this file>
Frame: Z = 0 at the old component-zone aft face, +Z to the nose; origin on the tube axis; +x "east"
(static/sound ports at 0 deg), +y "north".  Airframe ID 40.0.
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
REV = "v11"
RHO = 1.05e-3                 # ABS ~100% infill, g/mm^3
R_AF_I = 20.0                 # ID 40.0
R_MAX_MOVING = 19.5           # anything that slides in/out of the bore
SLED_RMAX = 19.39             # sled outer envelope (v2 value, kept)
CL = 0.40                     # every designed part-to-sled / part-to-part gap
WALL = 1.20
KNEE = 1.15                   # every corbel / knee / haunch rises 1.15 per 1.0 out (49 deg)
ZONE_Z1 = 48.0

# EbayCap mount -- v11: only the WEST boss.  Names D9aft reads are kept.
CAP_Z0 = 45.4
MOUNT_XW, MOUNT_XE = -15.3, 10.1          # MOUNT_XE: the cap's east hole -- NO boss under it in v11
MOUNT_HOLE_D = 2.0
MOUNT_BOSS_R = MOUNT_HOLE_D / 2.0 + 1.6
MOUNT_PILOT_DEPTH = 12.0
SERVO_TAB_XW, SERVO_TAB_XE = MOUNT_XW, MOUNT_XE
WBOSS_X1 = -13.5                          # W boss trimmed on its +x side (Nano joints behind -13.1 clear 0.4)
WBOSS_Z0 = 39.4                           # boss full section from here (M2x10 tip at Z 40.3)

SEAT_Z = -22.8                            # = v6..v10 (D9aft seat)
DECK_FLOOR = SEAT_Z + WALL                # -21.6
FOOT_RO = 19.3
SPINE_X1 = -16.6                          # spine slab x -19.0 .. -16.6 (v10)

# PIEZO (KY-006, v8 measured, sideways) -- position FROZEN by the D9aft sound port
PIEZO_ZC = -12.1
PIEZO_DL, PIEZO_DZ = 19.0, 15.0
PIEZO_PCB_T = 1.6
PIEZO_PCB_X0 = 6.8                        # PCB back face
PIEZO_CAN_H, PIEZO_CAN_D = 10.0, 12.0
PIEZO_X1 = PIEZO_PCB_X0 + PIEZO_PCB_T + PIEZO_CAN_H         # 18.4 can face
PIEZO_Y0 = -8.0                           # hole end (can centre 8 from the hole edge, at y 0)
PIEZO_Y1 = PIEZO_Y0 + PIEZO_DL            # 11.0 pin end
PIEZO_Z0 = PIEZO_ZC - PIEZO_DZ / 2.0      # -19.6
PIEZO_Z1 = PIEZO_Z0 + PIEZO_DZ            # -4.6
PIEZO_HDR = (2.5, 2.5, 7.6)
PIEZO_PIN_X = (0.95, 1.6)
PIEZO_PIN_L = 6.5
PIEZO_PIN_BEND = (1.5, 2.0, 5.5)
PIEZO_PIN_Z = 5.7
PIN_BAY = (PIEZO_PCB_X0, 12.0, PIEZO_Y1, PIEZO_Y1 + 7.0)    # x0, x1, y0, y1 (v11: x to 12, pins sit at x ~9.7)
PIEZO_SCREW_D = 2.0
PIEZO_HOLE_SPEC = ((2.5, 0.75, 0.50, -1), (3.0, 0.75, 0.75, +1))
PIEZO_HOLE_LIST = [(PIEZO_Y0 + dt + d / 2.0, PIEZO_ZC + sz * (PIEZO_DZ / 2.0 - ds - d / 2.0), d)
                   for d, dt, ds, sz in PIEZO_HOLE_SPEC]
# v11 FRAME behind the board: bar under the hole end + rail under the bottom edge band; window over the rest
FRAME_X0 = 4.2                            # frame back (= v10 plate back): 2.6 thick
FRAME_BAR_Y1 = PIEZO_Y0 + 4.5             # -3.5: hole-end bar (v10: joints start 4.5 in from the hole end)
FRAME_RAIL_Z1 = PIEZO_Z0 + 1.0            # -18.6: bottom rail top (1 mm component-free edge band)
PBOSS_X0 = FRAME_X0 - 2.0                 # 2.2: boss block behind the bar (~4.6 mm of M2 thread)
PBOSS_R = PIEZO_SCREW_D / 2.0 + 1.2      # 2.2: stays 0.05+ clear of the Q1 zone (y >= -3.5)
END_WALL_Y = (PIEZO_Y0 - CL - WALL, PIEZO_Y0 - CL)         # -9.6 .. -8.4 (v10 -y end wall, to the bore)
FRAME_TOP = -5.1                          # bar + boss tops: 0.4 under the BMP's aft edge (Z -4.7) as it goes in
END_WALL_TOP = -5.4                       # end wall top: 0.4 under the BMP's y -9 pan head (Z >= -4.95) on its way in
# Q1 BC337 TO-92 bent FLAT on the board back (user 2026-10-19).  WHERE on the back is not known ->
# the whole joint region (v10 relief footprint) is kept open, 4.4 deep.  ASSUMED: 3.6 body + 0.8 legs.
Q1_T = 4.4
Q1_ZONE = (PIEZO_PCB_X0 - Q1_T, PIEZO_PCB_X0, FRAME_BAR_Y1, PIEZO_Y1, PIEZO_Z0 + 1.0, PIEZO_Z1 - 1.0)

# NANO ESP32 -- BOTTOM of the stack, parts up (+x), USB-C + JST forward
NANO_W, NANO_L, NANO_PCB_T, NANO_T = 18.0, 45.0, 1.6, 5.0
NANO_X0 = -12.6                           # PCB back (joints to -13.1, W boss -13.5)
NANO_XF = NANO_X0 + NANO_PCB_T            # -11.0 PCB top
NANO_XT = NANO_X0 + NANO_T                # -7.6 tallest part
NANO_Z0 = -0.3
NANO_Z1 = NANO_Z0 + NANO_L                # 44.7 (USB-C ASSUMED <= 0.3 past the PCB -> 0.4 to the cap)
NANO_ROW_Y = 15.24 / 2.0
NANO_PAD_R = 0.85
NANO_JOINT_H = 0.5
NANO_PADS_Z = [NANO_Z0 + NANO_L / 2.0 + (i - 7) * 2.54 for i in range(15)]
NANO_EDGE = 0.6                           # long-edge band free of parts (ASSUMED, as v10)
# JST-PH power input on the Nano (user): 6 wide, 24 above the PCB with the plug in, left of the USB-C (+y)
JST_W, JST_H = 6.0, 24.0
JST_Y = (3.1, 3.1 + JST_W)                # ASSUMED: against the board edge (9.0) side, +y
JST_ZL = 7.5                              # ASSUMED: within the last 7.5 mm of the board
# Nano locators
RIB_Y = (1.5, 5.5)                        # back ribs (between the pad rows), x SPINE_X1 .. NANO_X0
HEEL_X1 = NANO_XF                         # heels under the PCB aft end, x NANO_X0 .. -11.0
LIP_Y = (NANO_W / 2.0 + CL, NANO_W / 2.0 + CL + 1.0)        # side lips 9.4 .. 10.4
LIP_X = (-13.5, -9.0)
LIP_Z_AFT = (NANO_Z0, 3.0)                # pads start Z 3.6
LIP_Z_FWD = (41.2, NANO_Z1)               # pads end Z 40.8

# CHEEKS (side walls, x-z planes).  Gutter part (cable room off the Nano) wider; upper part at the BMP width.
GUT_Y = 13.5                              # gutter wall inner face
UP_Y = 11.4                               # upper cheek inner face (BMP 11.0 + 0.4)
CHEEK_XS = -2.0                           # gutter wall below, upper cheek above this x
PINBAY_KNEE = (6.4, -4.2)                 # N upper cheek: corbels off x 6.4 from Z -4.2 (pin bay under it)
LEAD_EXIT = (-0.6, -12.5)                 # N upper cheek also open east of x -0.6 below a 1:1.15 line from Z -12.5:
                                          #   the piezo / Q1 leads go from the pin bay into the aft deck
BATT_STOP = ((9.0, 9.5), 1.5)             # fwd battery stops on the cheeks: inner |y| (S, N: JST at y <= 9.1), thickness

# BMP388 40 x 22 -- FLIPPED: PCB back (+x) up, parts + both Qwiic plugs (-x) down
BMP_W, BMP_L, BMP_PCB_T, BMP_PARTS = 22.0, 40.0, 1.6, 2.4
BMP_PCB_X0 = 0.5                          # PCB underside (parts side)
BMP_XB = BMP_PCB_X0 + BMP_PCB_T           # 2.1 PCB back (up)
BMP_Z0 = -4.7
BMP_Z1 = BMP_Z0 + BMP_L                   # 35.3
BMP_PARTS_Y = 6.5                         # ASSUMED: parts within |y| 6.5 -> corner hole rings free (bosses bear there)
BMP_HOLE_D, BMP_HOLE_IN = 3.0, 2.0
BMP_HOLES = [(sy * (BMP_W / 2.0 - BMP_HOLE_IN), z) for sy in (-1, 1) for z in (BMP_Z0 + BMP_HOLE_IN, BMP_Z1 - BMP_HOLE_IN)]
BMP_SCREW_D = 2.5
BMP_BOSS_R = 2.0                          # around the aft holes only (fwd holes are over the Nano)
BMP_BOSS_X0 = BMP_PCB_X0 - 6.0            # -5.5: 6 mm of M2.5 thread
BMP_HEAD = (2.25, 1.8)                    # pan head r, height (on the PCB back)
QW_PLUG = (2.95, 4.25, 2.7)               # Qwiic (JST-SH 4) plug + strain relief: depth below PCB, length, half width
QW_BEND = 1.5
BMP_LEDGE_Z = (BMP_Z1 - 7.0, BMP_Z1)      # fwd end ledges (PCB edge band)

# ADXL375 glued flat on the BMP's PCB back, plug FORWARD (user: only the "top" plug)
ADXL_W, ADXL_PCB_L, ADXL_L, ADXL_T = 18.0, 26.0, 27.0, 5.0
ADXL_TAPE = 0.3
ADXL_X0 = BMP_XB + ADXL_TAPE              # 2.4
ADXL_Z0 = 1.0                             # clear of the BMP aft screw heads (Z <= -0.45)
ADXL_PLUG_HW = 4.0

# BATTERY 40.5 x 20 x 8.5 -- on top, removable for charging; plugged in LAST into the Nano's JST
BATT_L, BATT_W, BATT_T = 40.5, 20.0, 8.5
BATT_X0 = ADXL_X0 + ADXL_T + CL           # 7.8
BATT_Z0 = PIEZO_Z1 + CL                   # -4.2 (over the piezo board's top edge)

# SMALL PARTS (aft deck storage, behind the piezo frame).  (x0, x1, y0, y1, z0, z1), insertion path
C1_D, C1_L = 10.0, 14.0                   # ASSUMED d10 x 12.5 body + 1.5 bent leads (d10 x 12.5 = common 470 uF 16 V; d8 x 11.5 also)
C1_POS = (-12.2, -12.2 + C1_L, -6.0, DECK_FLOOR + 0.2 + C1_D / 2.0)        # x0, x1, yc, zc (axis along x), aft deck south
# S7V8F5 lies flat ON the Nano's parts (Kapton), under the BMP's parts: x 3.5 thick, 11 across, 17 along Z
S7_BOX = (NANO_XT + CL, NANO_XT + CL + 3.5, -5.5, 5.5, 5.0, 22.0)

# D9aft (copied from v10)
D9_DZ = 279.2
D9_R_ID, D9_R_OD = 20.0, 21.5
D9_CREST = 19.65
D9_BAND_Z = 60.8 - 12.5
D9_SEAT_Z, D9_SEAT_RI, D9_SEAT_T = SEAT_Z, 15.5, 2.0
D9_SPIGOT_RI = 18.5
D9_PORTS = (("static", 1.5, 30.0, 0.0), ("sound", 3.0, PIEZO_ZC, 0.0))
D9_EBAYCAP = os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v2_EbayCap.step")
D9V10_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v10_%s.step" % k)) for k in ("EbayCap", "FwdTube"))
V10_FCSTD = os.path.join(PROJECT, "Avionics", "PhoenixABS40-43_avbay_sled_v10.FCStd")
DRIVER_D = 3.0

ASSUMED = [
    "Q1 TO-92 position on the piezo back: anywhere in the old joint footprint (y -3.5..11, Z -18.6..-5.6), 4.4 deep",
    "C1 470 uF 16 V: d10 x 12.5 body + 1.5 bent leads (d8 x 11.5 is also common -> more room)",
    "S7V8F5 17 x 11 x 3 + 0.5 joints, lying on the Nano's parts (Kapton between)",
    "JST-PH on the Nano: +y side (user 'left' = left looking at the USB-C port, parts side up), y 3.1..9.1,"
    " within the last 7.5 mm of the board",
    "BMP388 parts within |y| 6.5 -> the corner hole rings (aft bosses) and the edge band (fwd ledges) are part-free",
    "BMP388 PCB back flat over the ADXL footprint (the ADXL is taped/glued to it)",
    "Qwiic plug 2.95 deep x 4.25 long x 5.4 wide; cables bend 1.5 past the plug",
    "Nano USB-C <= 0.3 past the PCB end; Nano parts 3.4 tall, 0.6 edge bands free; back joints 0.5",
    "ADXL375 Qwiic plug centred on its 'top' (short) end, 8 wide",
]

# ================================================================ helpers (v10)
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
    if len(s) == 1:
        return s[0]
    f = s[0].multiFuse(s[1:])
    return f.Solids[0] if len(f.Solids) == 1 else f

def heal(shape, tag, log):
    before = len(shape.Faces)
    tmp = os.path.join(tempfile.gettempdir(), "healsled_%s.step" % tag)
    try:
        shape.exportStep(tmp)
        rt = Part.Shape(); rt.read(tmp); os.remove(tmp)
        shape = rt
    except Exception as exc:
        log.append("  ! %s: STEP round-trip skipped (%s)" % (tag, exc))
    try:
        rs = shape.removeSplitter()
        if rs.isValid():
            shape = rs
        else:
            log.append("  ! %s: removeSplitter gave an INVALID shape -- skipped" % tag)
    except Exception as exc:
        log.append("  ! %s: removeSplitter skipped (%s)" % (tag, exc))
    shape = as_solid(shape)
    shape.fixTolerance(1e-7)
    log.append("  heal %-14s faces %3d -> %3d, solids %d, %10.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape

def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=0.3, Relative=False)

def rmax_mesh(m):
    return max(math.hypot(v.x, v.y) for v in m.Points)

def clip_bore(shp, z0=SEAT_Z - 1.0, z1=None, r=SLED_RMAX):
    return shp.common(cyl(r, z0, z1 if z1 is not None else ZONE_Z1 + 5.0))

def vol(s):
    return s.Volume if s.Solids else 0.0

def vv(a, b):
    return vol(a.common(b))

def prism(axis, pts_uz, w0, w1):
    """polygon in the (u, Z) plane, u = x (axis 'x') or y (axis 'y'), extruded along the other horizontal axis"""
    if axis == "x":
        vs = [Vector(u, w0, z) for u, z in pts_uz]; d = Vector(0, w1 - w0, 0)
    else:
        vs = [Vector(w0, u, z) for u, z in pts_uz]; d = Vector(w1 - w0, 0, 0)
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(d)

def knee_cut(axis, u_face, z_face, sgn, w0=-30.0, w1=30.0):
    """CORBEL cutter: removes everything under a 1:KNEE line that leaves u = u_face at Z z_face and climbs
    as it goes out (sgn = +1 toward +u)"""
    D, B = 60.0, 80.0
    pts = [(u_face, z_face - B), (u_face, z_face), (u_face + sgn * D, z_face + KNEE * D), (u_face + sgn * D, z_face - B)]
    return prism(axis, pts, w0, w1)

def corbel(solid, axis, u_face, z_bottom_far, u_far, w0=-30.0, w1=30.0):
    """trim `solid` so its underside rises 1:KNEE from the support face u_face out to u_far, where the
    underside is at z_bottom_far (the member's working bottom)"""
    sgn = 1.0 if u_far > u_face else -1.0
    z_face = z_bottom_far - KNEE * abs(u_far - u_face)
    return solid.cut(knee_cut(axis, u_face, z_face, sgn, w0, w1))

# ================================================================ component envelopes
def env_nano():
    s = box(NANO_X0, NANO_XF, -NANO_W / 2.0, NANO_W / 2.0, NANO_Z0, NANO_Z1)
    e = NANO_W / 2.0 - NANO_EDGE
    return as_solid(s.fuse(box(NANO_XF, NANO_XT, -e, e, NANO_Z0, NANO_Z1)).removeSplitter())

def env_nano_joints():
    s = None
    for sy in (-1, 1):
        for z in NANO_PADS_Z:
            j = cyl_x(NANO_PAD_R, NANO_X0 - NANO_JOINT_H, NANO_X0, sy * NANO_ROW_Y, z)
            s = j if s is None else s.fuse(j)
    return as_solid(s.removeSplitter())

def env_jst():
    """the Nano's power JST-PH with the battery plug in: 24 tall off the PCB top (user)"""
    return box(NANO_XF, NANO_XF + JST_H, JST_Y[0], JST_Y[1], NANO_Z1 - JST_ZL, NANO_Z1)

def env_bmp():
    """flipped: PCB x 0.5..2.1 (back up), parts below within |y| 6.5, both plugs on the centred ends (below
    the PCB), and the two aft M2.5 pan heads on the back"""
    s = box(BMP_PCB_X0, BMP_XB, -BMP_W / 2.0, BMP_W / 2.0, BMP_Z0, BMP_Z1)
    s = s.fuse(box(BMP_PCB_X0 - BMP_PARTS, BMP_PCB_X0, -BMP_PARTS_Y, BMP_PARTS_Y, BMP_Z0, BMP_Z1))
    return as_solid(s.removeSplitter())

def env_bmp_heads():
    """the two aft M2.5 pan heads on the BMP's back (driven after the board is down -- not in its press-in sweep)"""
    hs = [cyl_x(BMP_HEAD[0], BMP_XB, BMP_XB + BMP_HEAD[1], hy, hz) for hy, hz in BMP_HOLES if hz < 0]
    return hs[0].fuse(hs[1])

def env_bmp_cable_aft():
    """aft Qwiic plug + the cable bending -x (down toward the Nano's aft end)"""
    d, ln, hw = QW_PLUG
    s = box(BMP_PCB_X0 - d, BMP_PCB_X0, -hw, hw, BMP_Z0 - ln, BMP_Z0)
    s = s.fuse(box(NANO_XT, BMP_PCB_X0, -hw, hw, BMP_Z0 - ln - QW_BEND, BMP_Z0 - ln))
    s = s.fuse(box(NANO_XT, NANO_XT + 2.0, -hw, hw, BMP_Z0 - ln - QW_BEND, NANO_Z0 + 2.0))
    return as_solid(s.removeSplitter())

def env_bmp_cable_fwd():
    """fwd Qwiic plug, U-turn over the BMP's fwd end, back along its PCB back to the ADXL's fwd plug"""
    d, ln, hw = QW_PLUG
    s = box(BMP_PCB_X0 - d, BMP_PCB_X0, -hw, hw, BMP_Z1, BMP_Z1 + ln)
    s = s.fuse(box(BMP_PCB_X0 - d, ADXL_X0 + ADXL_T, -hw, hw, BMP_Z1 + ln, BMP_Z1 + ln + QW_BEND + 0.5))
    s = s.fuse(box(BMP_XB, ADXL_X0 + ADXL_T, -hw, hw, ADXL_Z0 + ADXL_L, BMP_Z1 + ln + QW_BEND + 0.5))
    return as_solid(s.removeSplitter())

def env_adxl():
    s = box(ADXL_X0, ADXL_X0 + ADXL_T, -ADXL_W / 2.0, ADXL_W / 2.0, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    s = s.fuse(box(ADXL_X0, ADXL_X0 + ADXL_T, -ADXL_PLUG_HW, ADXL_PLUG_HW, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 + ADXL_L))
    return as_solid(s.removeSplitter())

def env_batt():
    return box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0, BATT_Z0 + BATT_L)

def env_piezo():
    """v8 KY-006 sideways + v11 Q1 zone on the back (replaces the v10 joint relief)"""
    y0, y1, z0, z1 = PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1
    xf = PIEZO_PCB_X0 + PIEZO_PCB_T
    s = box(PIEZO_PCB_X0, xf, y0, y1, z0, z1)
    s = s.fuse(cyl_x(PIEZO_CAN_D / 2.0, xf, PIEZO_X1, 0.0, PIEZO_ZC))
    s = s.fuse(box(*Q1_ZONE))
    hz = PIEZO_HDR[2] / 2.0
    s = s.fuse(box(xf, xf + PIEZO_HDR[0], y1 - PIEZO_HDR[1], y1, PIEZO_ZC - hz, PIEZO_ZC + hz))
    a, w, dn = PIEZO_PIN_BEND
    xm = xf + (PIEZO_PIN_X[0] + PIEZO_PIN_X[1]) / 2.0
    s = s.fuse(box(xm - 0.7, xm + 0.7, y1, y1 + a + w / 2.0, PIEZO_ZC - PIEZO_PIN_Z / 2.0 - 0.3, PIEZO_ZC + PIEZO_PIN_Z / 2.0 + 0.3))
    s = s.fuse(box(xm - 0.7, xm + 0.7, y1 + a - w / 2.0, y1 + a + w / 2.0, PIEZO_ZC - PIEZO_PIN_Z / 2.0 - dn, PIEZO_ZC + PIEZO_PIN_Z / 2.0 + 0.3))
    return as_solid(s.removeSplitter())

def env_c1():
    x0, x1, yc, zc = C1_POS
    return cyl_x(C1_D / 2.0, x0, x1, yc, zc)

def env_s7():
    return box(*S7_BOX)

def pin_bay():
    return clip_bore(box(PIN_BAY[0], PIN_BAY[1], PIN_BAY[2], PIN_BAY[3], DECK_FLOOR, PIEZO_Z1))

COMPONENTS = [
    ("Nano_ESP32",   env_nano),
    ("Nano_joints",  env_nano_joints),
    ("JST_power",    env_jst),
    ("C1_470uF",     env_c1),
    ("S7V8F5",       env_s7),
    ("BMP388",       env_bmp),
    ("BMP_heads",    env_bmp_heads),
    ("BMP_cable_aft", env_bmp_cable_aft),
    ("BMP_cable_fwd", env_bmp_cable_fwd),
    ("Piezo_Q1",     env_piezo),
    ("ADXL375",      env_adxl),
    ("Battery",      env_batt),
]
RIGID = [n for n, _ in COMPONENTS]

# ================================================================ the sled
def build_sled(log):
    """One printed piece, aft end on the bed, NO support.  Open to +x: every member sits outside the
    footprint of the parts pressed in before it (checked in [F])."""
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)

    # ---- spine (v10) + its key into the EbayCap
    parts.append(clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, SEAT_Z, ZONE_Z1 - 0.6)))
    # ---- floor disc on the seat
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, DECK_FLOOR)))

    # ---- cheeks.  Gutter wall |y| GUT_Y..+1.2 (x up to CHEEK_XS), upper cheek |y| UP_Y..+1.2 (x from CHEEK_XS),
    #      a connector between them, and a web back to the spine.  Full height floor -> cap face.
    for sy in (-1, 1):
        def yb(a, b):
            return tuple(sorted((sy * a, sy * b)))
        y0, y1 = yb(GUT_Y, GUT_Y + WALL)
        parts.append(cap(box(-19.0, CHEEK_XS + 0.01, y0, y1, DECK_FLOOR - 0.01, CAP_Z0)))
        y0, y1 = yb(UP_Y, UP_Y + WALL)
        up = box(CHEEK_XS, 19.5, y0, y1, DECK_FLOOR - 0.01, CAP_Z0)
        if sy > 0:   # N: the piezo pin bay is under it east of x 6.4 -> corbel off x 6.4 from Z -4.2
            up = up.cut(knee_cut("x", PINBAY_KNEE[0], PINBAY_KNEE[1], +1))
            up = up.cut(knee_cut("x", LEAD_EXIT[0], LEAD_EXIT[1], +1))      # lead exit pin bay -> aft deck
        # fwd battery stop: flat 1.4 mm ledge over the pack's fwd edge band, corbelled off the cheek face
        yi = BATT_STOP[0][0 if sy < 0 else 1]
        z0 = BATT_Z0 + BATT_L + CL
        ya, yb_ = sorted((sy * yi, sy * (BATT_W / 2.0 + CL)))
        parts.append(cap(box(BATT_X0 + 0.8, 14.4, ya, yb_, z0, z0 + BATT_STOP[1])))
        ya, yb_ = sorted((sy * (BATT_W / 2.0 + CL - 0.01), sy * (UP_Y + 0.01)))
        cb = box(BATT_X0 + 0.8, 14.4, ya, yb_, z0 - 3.0, z0 + BATT_STOP[1])
        parts.append(cap(cb.cut(knee_cut("y", sy * UP_Y, z0 - KNEE * (UP_Y - BATT_W / 2.0 - CL), -sy))))
        parts.append(cap(up))
        y0, y1 = yb(UP_Y, GUT_Y + WALL)
        parts.append(cap(box(CHEEK_XS, CHEEK_XS + WALL, y0, y1, DECK_FLOOR - 0.01, CAP_Z0)))
        y0, y1 = yb(LIP_Y[0], GUT_Y + WALL)
        parts.append(cap(box(-19.0, NANO_X0, y0, y1, DECK_FLOOR - 0.01, CAP_Z0)))      # web: gutter back wall

    # ---- Nano: back ribs (between the pad rows) with heels under the PCB's aft end; side lips at both ends
    for sy in (-1, 1):
        y0, y1 = sorted((sy * RIB_Y[0], sy * RIB_Y[1]))
        rib = box(SPINE_X1 - 0.1, NANO_X0, y0, y1, -12.0, NANO_Z1)
        rib = rib.fuse(box(NANO_X0 - 0.01, HEEL_X1, y0, y1, -12.0, NANO_Z0 - 0.1))
        rib = corbel(rib, "x", SPINE_X1, NANO_Z0 - 1.3, HEEL_X1)        # heel 1.2 deep under the end face
        parts.append(cap(rib))
        for z0, z1 in (LIP_Z_AFT, LIP_Z_FWD):
            y0, y1 = sorted((sy * LIP_Y[0], sy * GUT_Y))
            lip = box(LIP_X[0], LIP_X[1], y0, y1, z0 - 12.0, z1)
            lip = corbel(lip, "y", sy * GUT_Y, z0, sy * LIP_Y[0])
            parts.append(cap(lip))

    # ---- W cap boss (E boss deleted, see header): trimmed at x -13.5, corbelled off the spine face
    wb = cyl(MOUNT_BOSS_R, 25.0, CAP_Z0, MOUNT_XW, 0.0).cut(box(WBOSS_X1, 30, -30, 30, 0, 60))
    wb = corbel(wb, "x", SPINE_X1, WBOSS_Z0, WBOSS_X1)
    parts.append(cap(wb))
    drill.append(cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, MOUNT_XW, 0.0))

    # ---- BMP aft screw bosses (y +/-9, Z -2.7): column + block out to the cheeks, corbelled in y
    for hy, hz in [h for h in BMP_HOLES if h[1] < 0]:
        sy = 1 if hy > 0 else -1
        zb0, zb1 = hz - BMP_BOSS_R, hz + BMP_BOSS_R
        y_in = hy - sy * BMP_BOSS_R                                        # inner edge |y| 7.0
        y0, y1 = sorted((y_in, sy * GUT_Y))
        blk = box(BMP_BOSS_X0, BMP_PCB_X0, y0, y1, zb0 - 12.0, zb1)
        blk = corbel(blk, "y", sy * GUT_Y, zb0, y_in)
        parts.append(cap(blk))
        drill.append(cyl_x(BMP_SCREW_D / 2.0 - 0.2, BMP_BOSS_X0 + 0.6, BMP_XB + 1.0, hy, hz))   # M2.5 pilot d2.1
    # ---- BMP fwd ledges: under the PCB's fwd edge band, off the upper cheek
    for sy in (-1, 1):
        y0, y1 = sorted((sy * LIP_Y[0], sy * (UP_Y + 0.01)))
        led = box(BMP_PCB_X0 - 2.0, BMP_PCB_X0, y0, y1, BMP_LEDGE_Z[0] - 12.0, BMP_LEDGE_Z[1])
        led = corbel(led, "y", sy * UP_Y, BMP_LEDGE_Z[0], sy * LIP_Y[0])
        parts.append(cap(led))

    # ---- piezo FRAME (v11): hole-end bar + boss block behind it, bottom rail, -y end wall to the bore
    pb = box(FRAME_X0, PIEZO_PCB_X0, PIEZO_Y0 - CL, FRAME_BAR_Y1, DECK_FLOOR - 0.01, FRAME_TOP)
    pb = pb.fuse(box(PBOSS_X0, FRAME_X0 + 0.01, PIEZO_Y0 - CL, FRAME_BAR_Y1 - CL, DECK_FLOOR - 0.01, PIEZO_HOLE_LIST[1][1]))
    for yc, zc, _ in PIEZO_HOLE_LIST:
        pb = pb.fuse(cyl_x(PBOSS_R, PBOSS_X0, FRAME_X0 + 0.01, yc, zc))
        drill.append(cyl_x(PIEZO_SCREW_D / 2.0 - 0.2, PBOSS_X0 - 0.5, PIEZO_PCB_X0 + 1.0, yc, zc))
    pb = pb.cut(box(PBOSS_X0 - 0.1, PIEZO_PCB_X0 + 0.1, PIEZO_Y0 - CL - 0.1, FRAME_BAR_Y1 + 0.1, FRAME_TOP, 0.0))   # flat top
    pb = pb.fuse(box(FRAME_X0, PIEZO_PCB_X0, PIEZO_Y0 - CL, PIEZO_Y1 + CL, DECK_FLOOR - 0.01, FRAME_RAIL_Z1))
    pb = pb.fuse(box(FRAME_X0, SLED_RMAX + 1.0, END_WALL_Y[0], END_WALL_Y[1], DECK_FLOOR - 0.01, END_WALL_TOP))
    parts.append(cap(pb))

    sled = parts[0].multiFuse(parts[1:])
    rs = sled.removeSplitter()
    log.append("  removeSplitter after fuse: %s" % ("kept" if rs.isValid() else "INVALID -> skipped"))
    sled = rs if rs.isValid() else sled
    for d in drill:
        sled = sled.cut(d)
    sled = sled.cut(pin_bay())

    env = dict((n, f()) for n, f in COMPONENTS)
    raw = dict((n, vv(sled, e)) for n, e in env.items())
    for n in RIGID:
        sled = sled.cut(env[n])
    sol = sled.Solids
    log.append("  connectivity: %d solid(s)  %s" % (len(sol), ", ".join("%.1f" % s.Volume for s in sol)))
    if len(sol) != 1:
        big = max(sol, key=lambda s: s.Volume)
        for s in sol:
            if s is not big:
                b = s.BoundBox
                log.append("    loose piece %.1f mm3 at x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f"
                           % (s.Volume, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
        raise RuntimeError("sled is %d disconnected solids -- tie them in\n%s" % (len(sol), "\n".join(log[-len(sol):])))
    if not sol[0].isValid():
        raise RuntimeError("sled solid is INVALID after the build")
    return sol[0], raw

# ================================================================ verification
def main():
    log = []
    P = log.append
    P("=" * 78)
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (soldered harness, one-side press-in)" % REV)
    P("=" * 78)
    P("")
    doc = App.newDocument("PhoenixABS40-43_avbay_sled_%s" % REV)
    comp = dict((n, f()) for n, f in COMPONENTS)
    cmesh = dict((n, mesh_of(s)) for n, s in comp.items())

    P("[1] build + heal")
    sled, raw = build_sled(log)
    sled = heal(sled, "Sled", log)
    if len(sled.Solids) != 1 or not sled.isValid():
        raise RuntimeError("heal: %d solids, valid %s" % (len(sled.Solids), sled.isValid()))
    P("  valid solid after heal: True")
    smesh = mesh_of(sled)

    P("")
    P("[2] pack -- component list  (dx.dy.dz  Zmin  Zmax  Rmax)")
    for n, s in comp.items():
        bb = cmesh[n].BoundBox
        P("  %-14s %5.1f.%4.1f.%4.1f  %6.1f %6.1f  %6.2f" % (n, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax, rmax_mesh(cmesh[n])))
    sbb = smesh.BoundBox
    P("  %-14s %5.1f.%4.1f.%4.1f  %6.1f %6.1f  %6.2f   <- the sled" % ("Sled", sbb.XLength, sbb.YLength, sbb.ZLength, sbb.ZMin, sbb.ZMax, rmax_mesh(smesh)))

    P("")
    P("[0] CONTAINMENT  (Rmax vs %.1f moving / %.1f ID)" % (R_MAX_MOVING, R_AF_I))
    zmax = 0.0
    for n, s in comp.items():
        r = rmax_mesh(cmesh[n]); zmax = max(zmax, cmesh[n].BoundBox.ZMax)
        tag = "PASS" if r <= R_MAX_MOVING + 1e-6 else ("past moving  FAIL" if r <= R_AF_I else "*** PAST ID ***  FAIL")
        P("  %-14s Rmax %6.2f  toID %5.2f   %s" % (n, r, R_AF_I - r, tag))
    rs = rmax_mesh(smesh)
    P("  %-14s Rmax %6.2f  toID %5.2f   %s" % ("Sled", rs, R_AF_I - rs, "PASS" if rs <= SLED_RMAX + 0.05 else "FAIL"))
    P("  component tops Z .. %.1f vs EbayCap face %.1f   %s" % (zmax, CAP_Z0, "PASS" if zmax <= CAP_Z0 - 0.3 else "FAIL"))
    above = sled.common(box(-30, 30, -30, 30, CAP_Z0 + 0.01, ZONE_Z1 + 5))
    key = clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, CAP_Z0 + 0.01, ZONE_Z1 - 0.6))
    sv = vol(above.cut(key))
    P("  above EbayCap face: %.1f mm3, outside the spine key %.2f   %s" % (vol(above), sv, "PASS" if sv < 0.01 else "FAIL"))
    top = sled.common(box(-30, 30, -30, 30, CAP_Z0 - 0.2, CAP_Z0))
    ring = cyl(1.8, CAP_Z0 - 0.2, CAP_Z0, MOUNT_XW, 0.0).cut(cyl(MOUNT_HOLE_D / 2.0, CAP_Z0 - 1, CAP_Z0 + 1, MOUNT_XW, 0.0))
    f = vv(top, ring) / ring.Volume
    P("  EbayCap W M2 boss (%.1f, 0) seated at Z %.1f: %.0f %% of the head footprint backed   %s" % (MOUNT_XW, CAP_Z0, 100 * f, "PASS" if f > 0.95 else "FAIL"))
    P("  EbayCap E M2 boss (%.1f, 0): DELETED in v11 -- leave the cap's east screw OUT (sled held by the W screw + spine key)" % MOUNT_XE)

    P("")
    P("[F] PRESS-IN -- every part along +x in ASSEMBLY ORDER, deepest first (sled in hand, out of the tube).")
    P("    Each part moves along its path and then +x until it is clear of the bore; it must not touch the sled")
    P("    or any part already in.  Small parts in the aft deck enter through the piezo frame window first.")
    def sweep(sh, path, others):
        hits, t = {}, Vector(0, 0, 0)
        for d, L in path:
            n = 400 if L is None else max(1, int(math.ceil(L / 0.5)))
            st = d * (0.5 if L is None else L / n)
            for _ in range(n):
                t = t + st
                s2 = sh.translated(t)
                for n2, o in others:
                    v = vv(s2, o)
                    if v > 1e-2: hits[n2] = max(hits.get(n2, 0.0), v)
                if L is None and s2.BoundBox.XMin > SLED_RMAX + 0.6:
                    break
        return hits
    X = Vector(1, 0, 0)
    LOAD = [("Nano_ESP32", ["Nano_ESP32", "Nano_joints", "JST_power"], [(X, None)]),
            ("C1_470uF",   ["C1_470uF"], [(Vector(0, 0, 1), 3.2), (Vector(0, 1, 0), 9.0), (X, None)]),
            ("S7V8F5",     ["S7V8F5"], [(X, None)]),
            ("BMP388",     ["BMP388", "BMP_cable_aft"], [(X, None)]),
            ("BMP_heads",  ["BMP_heads"], [(X, None)]),
            ("Piezo_Q1",   ["Piezo_Q1"], [(X, None)]),
            ("ADXL375",    ["ADXL375"], [(X, None)]),
            ("BMP_cable_fwd", ["BMP_cable_fwd"], [(X, None)]),
            ("Battery",    ["Battery"], [(X, None)])]
    loaded = []
    for nm, members, path in LOAD:
        sh = comp[members[0]]
        for m in members[1:]:
            sh = sh.fuse(comp[m])
        others = [("Sled", sled)] + [(k, comp[k]) for k in loaded]
        h = sweep(sh, path, others)
        ps = " then ".join("%s%s" % ("(%+.0f,%+.0f,%+.0f)" % (d.x, d.y, d.z), (" %.1f" % L) if L else " out") for d, L in path)
        P("  %-14s %-34s %s   %s" % (nm, ps, "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), "PASS" if not h else "FAIL"))
        loaded += members
    P("  (battery JST plug: into the Nano's JST LAST, from the open face, down the chimney -- [X])")

    P("")
    P("[I] FIT -- RAW = the as-drawn sled inside each part's keep-out BEFORE the trim (should be ~0 by design);")
    P("    post-cut must be 0.  Then part-vs-part clashes.")
    for n in comp:
        P("  %-14s RAW %7.1f mm3   post-cut %.1f   %s" % (n, raw.get(n, 0.0), vv(sled, comp[n]), "" if raw.get(n, 0.0) < 0.5 else "(sled member trimmed by the part -- review)"))
    cn = list(comp.keys()); cc = 0
    designed = {("Nano_ESP32", "JST_power"), ("BMP388", "BMP_heads")}      # the JST is soldered on the Nano; heads on the PCB
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            v = vv(comp[cn[i]], comp[cn[j]])
            if (cn[i], cn[j]) in designed:
                P("    designed: %s on %s (%.1f mm3 shared envelope)" % (cn[j], cn[i], v)); continue
            if v > 0.05:
                cc += 1; P("    CLASH %s <-> %s  %.2f mm3   FAIL" % (cn[i], cn[j], v))
    P("  part-vs-part clashes: %d   %s" % (cc, "PASS" if cc == 0 else "FAIL"))
    P("  gaps between neighbours (want >= %.1f, 0 = designed contact):" % (CL - 0.05))
    for a, b in (("Nano_ESP32", "BMP388"), ("BMP388", "ADXL375"), ("ADXL375", "Battery"), ("Battery", "Piezo_Q1"),
                 ("BMP388", "Piezo_Q1"), ("C1_470uF", "S7V8F5"), ("JST_power", "BMP_cable_fwd"), ("JST_power", "Battery"),
                 ("BMP_cable_aft", "C1_470uF"), ("BMP_cable_aft", "Piezo_Q1"), ("S7V8F5", "Piezo_Q1")):
        g = comp[a].distToShape(comp[b])[0]
        P("    %-14s - %-14s %5.2f   %s" % (a, b, g, "designed (tape)" if (a, b) == ("BMP388", "ADXL375") else ("PASS" if g >= CL - 0.05 else "WARN")))

    P("")
    P("[S] SCREW ACCESS (d%.1f driver from the head along +x; sees the sled + every part in before that screw)" % DRIVER_D)
    order = [n for _, ms, _ in LOAD for n in ms]
    screws = []
    for hy, hz in [h for h in BMP_HOLES if h[1] < 0]:
        screws.append(("BMP M2.5 y%+.0f Z%.1f" % (hy, hz), "BMP388", Vector(BMP_XB + BMP_HEAD[1], hy, hz)))
    for hy, hz, d in PIEZO_HOLE_LIST:
        screws.append(("piezo M2 d%.1f y%+.1f" % (d, hy), "Piezo_Q1", Vector(PIEZO_PCB_X0 + PIEZO_PCB_T + 1.8, hy, hz)))
    for nm, who, h in screws:
        drv = Part.makeCylinder(DRIVER_D / 2.0, 30.0, h, X)
        inn = order[:order.index(who)]
        hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp[k]) for k in inn] for v in [vv(sh, drv)] if v > 1e-2]
        P("  %-22s %s   %s" % (nm, "clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    hy, hz = [h for h in BMP_HOLES if h[1] < 0][0]
    ncv = vv(sled, Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(BMP_XB + BMP_HEAD[1], hy, hz), Vector(-1, 0, 0)))
    P("  NEGATIVE CONTROL: same driver pointed INTO the sled (-x) hits it %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))

    P("")
    P("[H] HOLES + SEATS")
    for hy, hz in [h for h in BMP_HOLES if h[1] < 0]:
        ann = cyl_x(BMP_BOSS_R, BMP_PCB_X0 - 0.1, BMP_PCB_X0, hy, hz).cut(cyl_x(BMP_HOLE_D / 2.0, -10, 10, hy, hz))
        f = vv(sled, ann) / ann.Volume
        th = sled.common(Part.makeLine(Vector(BMP_PCB_X0, hy, hz + 1.2), Vector(BMP_PCB_X0 - 10.0, hy, hz + 1.2)))
        tl = sum(e.Length for e in th.Edges)
        P("  BMP aft hole (y %+.1f, Z %.1f): boss face under the PCB %3.0f %%, thread %.1f mm (M2.5 x 8 from +x)   %s"
          % (hy, hz, 100 * f, tl, "PASS" if f > 0.6 and tl >= 4.5 else "FAIL"))
    for sy in (-1, 1):
        a = vv(sled, box(BMP_PCB_X0 - 0.1, BMP_PCB_X0, -BMP_W / 2.0, BMP_W / 2.0, BMP_LEDGE_Z[0], BMP_Z1).common(box(-30, 30, *(sorted((0, sy * 30))), -60, 60))) / 0.1
        P("  BMP fwd ledge %s: %.1f mm2 under the PCB edge band   %s" % ("N" if sy > 0 else "S", a, "PASS" if a > 6.0 else "FAIL"))
    P("  BMP fwd holes (Z %.1f) are over the Nano -> no screws there; the fwd end rests on the ledges, Kapton over it" % BMP_HOLES[1][1])
    for hy, hz, d in PIEZO_HOLE_LIST:
        th = sled.common(Part.makeLine(Vector(PIEZO_PCB_X0, hy, hz + 1.0), Vector(PIEZO_PCB_X0 - 8.0, hy, hz + 1.0)))
        tl = sum(e.Length for e in th.Edges)
        ann = cyl_x(2.0, PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, hy, hz).cut(cyl_x(1.3, PIEZO_PCB_X0 - 1, PIEZO_PCB_X0 + 1, hy, hz))
        f = vv(sled, ann) / ann.Volume
        gap = math.hypot(hy, hz - PIEZO_ZC) - PIEZO_CAN_D / 2.0 - 1.9
        P("  piezo M2 (y %+5.2f, Z %.2f): thread %.1f mm %s; bar under the hole %3.0f %% %s; M2 head to can %.2f %s"
          % (hy, hz, tl, "PASS" if tl >= 4.0 else "FAIL", 100 * f, "PASS" if f > 0.8 else "FAIL", gap, "PASS" if gap > 0.2 else "WARN (as v10: file a flat on that pan head)"))
    wl = sum(e.Length for e in sled.common(Part.makeLine(Vector(MOUNT_XW, 0.9, CAP_Z0), Vector(MOUNT_XW, 0.9, CAP_Z0 - 10))).Edges)
    P("  EbayCap W M2 x10: boss material beside the pilot from the cap face down %.1f mm (tip at Z 40.3 needs >= 5.1)   %s" % (wl, "PASS" if wl >= 5.1 else "FAIL"))

    P("")
    P("[P] PIEZO FRAME + Q1 (TO-92 flat on the back)")
    qz = box(*Q1_ZONE)
    P("  Q1 zone x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f (%.0f mm3): sled inside %.2f mm3   %s"
      % (Q1_ZONE + (qz.Volume, vv(sled, qz), "PASS" if vv(sled, qz) < 0.01 else "FAIL")))
    bear = vv(sled, box(PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)) / 0.1
    P("  board back bears on the frame: %.1f mm2 (hole-end bar + bottom rail band); 2 x M2 clamp the hole end   %s" % (bear, "PASS" if bear > 40 else "FAIL"))
    pocket = box(PIEZO_PCB_X0 + 0.01, PIEZO_X1 + 0.5, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)
    P("  sled in front of the board: %.2f mm3   %s" % (vv(sled, pocket), "PASS" if vv(sled, pocket) < 0.01 else "FAIL"))
    pb = pin_bay()
    P("  pin bay x %.1f..%.1f y %.1f..%.1f: sled inside %.2f mm3   %s" % (PIN_BAY + (vv(sled, pb), "PASS" if vv(sled, pb) < 0.01 else "FAIL")))
    P("  under the board %.1f mm; over it the battery end (0.4)" % (PIEZO_Z0 - DECK_FLOOR))

    P("")
    P("[X] HARNESS ROOM -- JST chimney, gutters, Qwiic routes")
    jst = comp["JST_power"]; jb = jst.BoundBox
    col = clip_bore(box(jb.XMin, 25.0, jb.YMin, jb.YMax, jb.ZMin, jb.ZMax), r=R_MAX_MOVING)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp[k]) for k in comp if k not in ("JST_power", "Nano_ESP32")] for v in [vv(sh, col)] if v > 1e-2]
    P("  chimney: JST y %.1f..%.1f Z %.1f..%.1f, top x %.1f; column from the PCB up to the bore clear of %s   %s"
      % (jb.YMin, jb.YMax, jb.ZMin, jb.ZMax, jb.XMax, "everything" if not hit else hit, "PASS" if not hit else "FAIL"))
    P("    -> plug the battery from the open face with everything else in; its lead runs fwd off the pack end (Z %.1f)" % (BATT_Z0 + BATT_L))
    rows = []
    for z in [DECK_FLOOR + 1.0 + 3.0 * i for i in range(22)]:
        for sy in (-1, 1):
            y0, y1 = sorted((sy * LIP_Y[0], sy * GUT_Y))
            g = box(NANO_X0, CHEEK_XS, y0, y1, z, z + 0.2)
            free = vol(g.cut(sled)) / 0.2
            for k in comp:
                free -= vv(g.cut(sled), comp[k]) / 0.2
            rows.append((free, sy, z))
    w = min(rows)
    P("  gutters (x %.1f..%.1f, |y| %.1f..%.1f, both sides, floor to cap): free section min %.1f mm2 (%s, Z %.1f), median %.1f mm2"
      % (NANO_X0, CHEEK_XS, LIP_Y[0], GUT_Y, w[0], "N" if w[1] > 0 else "S", w[2], sorted(r[0] for r in rows)[len(rows) // 2]))
    P("    = a %.1f mm bundle fits everywhere (d of a circle of the min area x 0.6 packing)" % (2.0 * math.sqrt(0.6 * w[0] / math.pi)))
    ln_aft = (BMP_Z0 - (BMP_Z0 - QW_PLUG[1] - QW_BEND)) + (BMP_PCB_X0 - NANO_XT) + (NANO_Z0 + 2.0 - (BMP_Z0 - QW_PLUG[1] - QW_BEND))
    ln_fwd = QW_PLUG[1] + QW_BEND + (ADXL_X0 + ADXL_T - BMP_PCB_X0) + (BMP_Z1 + QW_PLUG[1] - (ADXL_Z0 + ADXL_L))
    P("  Qwiic routes (keep-outs BMP_cable_*): BMP fwd plug -> U-turn over the BMP end -> ADXL fwd plug ~%.0f mm of cable;" % ln_fwd)
    P("    BMP aft plug -> down to the Nano's aft end ~%.0f mm + its run along the Nano to the I2C pads" % ln_aft)
    pts = [Vector(8.0, 12.6, -14.0), Vector(1.3, 12.6, -14.0), Vector(1.3, 5.0, -14.0)]
    pr = None
    for a, b in zip(pts[:-1], pts[1:]):
        c = Part.makeCylinder(1.0, (b - a).Length, a, b - a).fuse(Part.makeSphere(1.0, b))
        pr = c if pr is None else pr.fuse(c)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + list(comp.items()) for v in [vv(sh, pr)] if v > 1e-2]
    P("  piezo / Q1 lead exit: d2 probe pin bay (8.0, 12.6, -14) -> west under the N cheek -> into the aft deck (1.3, 5.0): %s   %s"
      % ("clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    P("  Nano top -> BMP parts: %.1f mm of open height over the whole board (wire bends off the pads, resistors)" % ((BMP_PCB_X0 - BMP_PARTS) - NANO_XT))

    P("")
    P("[T] BMP388 vs NANO (heat): BMP sensor side now faces the Nano across %.1f mm (v10 2.5 mm apart edge to edge,"
      % ((BMP_PCB_X0 - BMP_PARTS) - NANO_XT))
    P("    v3 0.5 face to face).  Baro temperature-compensates; the ESP32 warms ~10 C with Wi-Fi up -> keep the AP off")
    P("    in flight (firmware already kills it at BOOST).  Not a blocker; logged.")

    P("")
    P("[B] BATTERY")
    bt = comp["Battery"]
    aft = box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0 - CL - 0.1, BATT_Z0 - CL)
    a_p = vv(comp["Piezo_Q1"], aft) / 0.1
    a_s = vv(sled, box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, END_WALL_TOP - 0.1, END_WALL_TOP)) / 0.1
    P("  aft face (Z %.1f): bears on the piezo PCB's top edge %.1f mm2 at 0.4 (board on 2 x M2 + the frame; ~2 N at 15 g)"
      % (BATT_Z0, a_p))
    P("    + the -y end wall top %.1f mm2 at 1.2 (lowered to Z %.1f so the BMP's aft pan head passes)   %s"
      % (a_s, END_WALL_TOP, "PASS" if a_p > 5 and a_s > 5 else "FAIL"))
    P("  lateral: cheeks at |y| %.1f (pack %.1f) -> 1 mm foam each side; Kapton wrap over the pack" % (UP_Y, BATT_W / 2.0))
    P("  rests on the ADXL (0.4) -> 1 mm foam pad between; outboard face -> ID %.1f mm at y 0 (foam), corners R %.2f"
      % (R_AF_I - BATT_X0 - BATT_T, rmax_mesh(cmesh["Battery"])))
    fz = vv(sled, box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0 + BATT_L + CL, BATT_Z0 + BATT_L + CL + 0.1)) / 0.1
    P("  fwd face (Z %.1f): stops on both cheeks %.1f mm2 at 0.4 (S to |y| %.1f; N to |y| %.1f, the JST is at y <= %.1f)   %s"
      % (BATT_Z0 + BATT_L, fz, BATT_STOP[0][0], BATT_STOP[0][1], JST_Y[1], "PASS" if fz > 4.0 else "FAIL"))
    free = [d for d in (5.0, 10.0, 15.0) if vv(sled, bt.translated(Vector(d, 0, 0))) < 1e-3]
    P("  pulls straight out along +x for charging: %s mm tested clear   %s" % (free, "PASS" if len(free) == 3 else "FAIL"))

    P("")
    P("[A] ADXL375 ON THE BMP's PCB BACK")
    ab = comp["ADXL375"].BoundBox
    inside = ab.YMin >= -BMP_W / 2.0 and ab.YMax <= BMP_W / 2.0 and ab.ZMin >= BMP_Z0 and ADXL_Z0 + ADXL_PCB_L <= BMP_Z1
    hg = comp["ADXL375"].distToShape(comp["BMP_heads"])[0]
    P("  footprint y %.1f..%.1f Z %.1f..%.1f inside the BMP back (y +/-%.0f, Z %.1f..%.1f): %s; to the BMP screw heads %.2f   %s"
      % (ab.YMin, ab.YMax, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L, BMP_W / 2.0, BMP_Z0, BMP_Z1, inside, hg, "PASS" if inside and hg >= 0.4 else "FAIL"))
    P("  pose: long axis = rocket Z (as v10), board NORMAL = +x (v10: +y), plug FORWARD (v10: aft) -> firmware axis map")

    P("")
    P("[D9] FIT TO THE D9aft E-BAY (proxy + the REAL v10 FwdTube / EbayCap; D9aft v11 changed only AftTube + fin can)")
    cav = cyl(D9_CREST, D9_BAND_Z, 70.0)
    cav = cav.fuse(Part.makeCone(D9_R_ID, D9_CREST, D9_R_ID - D9_CREST, Vector(0, 0, D9_BAND_Z - (D9_R_ID - D9_CREST))))
    cav = cav.fuse(cyl(D9_R_ID, D9_SEAT_Z, D9_BAND_Z - (D9_R_ID - D9_CREST) + 0.001))
    cav = cav.fuse(cyl(D9_SEAT_RI, D9_SEAT_Z - D9_SEAT_T, D9_SEAT_Z + 0.001))
    cav = cav.fuse(Part.makeCone(D9_SPIGOT_RI, D9_SEAT_RI, D9_SPIGOT_RI - D9_SEAT_RI, Vector(0, 0, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI))))
    cav = cav.fuse(cyl(D9_SPIGOT_RI, D9_SEAT_Z - 14.1, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI) + 0.001))
    tube = cyl(D9_R_OD, D9_SEAT_Z - 11.1, 60.8).cut(cav)
    for nm, d, zp, a in D9_PORTS:
        tube = tube.cut(Part.makeCylinder(d / 2.0, 5.0, Vector(D9_R_ID - 1.0, 0, zp), Vector(1, 0, 0)).rotated(Vector(0, 0, 0), Vector(0, 0, 1), a))
    d9 = {}
    for k, fn in D9V10_STEP.items():
        sh = Part.Shape(); sh.read(fn); d9[k] = sh
    dz = CAP_Z0 - d9["EbayCap"].BoundBox.ZMin
    for k in d9:
        d9[k].translate(Vector(0, 0, dz))
    for nm, part in (("FwdTube (proxy)", tube), ("FwdTube v10", d9["FwdTube"]), ("EbayCap v10", d9["EbayCap"])):
        hits = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + list(comp.items()) for v in [vv(sh, part)] if v > 1e-2]
        P("  %-16s vs sled + every component: %s   %s" % (nm, hits or "contact only", "PASS" if not hits else "FAIL"))
    ncv = vv(sled.translated(Vector(0, 0, -0.5)), d9["FwdTube"])
    P("  NEGATIVE CONTROL (real FwdTube v10): sled dropped 0.5 mm -> %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))
    lift = max(rs, max(rmax_mesh(cmesh[n]) for n in comp))
    P("  lift-out through the thread crests: largest R %.2f vs crest %.2f -> %.2f radial   %s" % (lift, D9_CREST, D9_CREST - lift, "PASS" if D9_CREST - lift >= 0.25 else "FAIL"))
    zmin = sled.BoundBox.ZMin
    foot = sled.common(cyl(D9_R_ID, zmin - 0.01, zmin + 0.1).cut(cyl(D9_SEAT_RI, zmin - 1, zmin + 1)))
    fa = vol(foot) / 0.11
    P("  seat: sled Zmin %.2f vs seat %.2f; bearing on the seat annulus %.0f mm2   %s" % (zmin, D9_SEAT_Z, fa, "PASS" if abs(zmin - D9_SEAT_Z) < 1e-3 and fa > 100 else "FAIL"))
    for nm, d, zp, a in D9_PORTS:
        c = Part.makeCylinder(d / 2.0 + 0.5, 3.0, Vector(D9_R_ID - 3.0, 0, zp), Vector(1, 0, 0)).rotated(Vector(0, 0, 0), Vector(0, 0, 1), a)
        blk = [n2 for n2, sh in [("Sled", sled)] + [(k, v) for k, v in comp.items() if k != "Piezo_Q1"] if vv(sh, c) > 1e-3]
        P("  %-6s port d%.1f at Z %.1f: 3 mm behind it clear of %s   %s" % (nm, d, zp, "everything" if not blk else blk, "PASS" if not blk else "FAIL"))
    canc = comp["Piezo_Q1"].common(cyl_x(PIEZO_CAN_D / 2.0 + 0.01, PIEZO_X1 - 1.0, PIEZO_X1 + 0.01, 0.0, PIEZO_ZC)).BoundBox
    P("  piezo can face centre (y %.2f, Z %.2f) on the sound port (0, %.1f)   %s" % ((canc.YMin + canc.YMax) / 2.0, (canc.ZMin + canc.ZMax) / 2.0, PIEZO_ZC,
      "PASS" if abs((canc.ZMin + canc.ZMax) / 2.0 - PIEZO_ZC) < 0.01 else "FAIL"))

    P("")
    P("[M] MASS")
    m = sled.Volume * RHO
    P("  sled (ABS, solid-equiv) %8.1f mm3   %5.1f g   (v10 17.4 g -> %+.1f g)" % (sled.Volume, m, m - 17.4))
    P("  fasteners: 2 x M2.5x8 (BMP aft holes, from +x), 2 x M2x6 (piezo), 1 x M2x10 (EbayCap W only)")
    dm = (m - 12.6) - 1.5 - 1.5 - 0.5                       # vs the D9aft v10 rollup: sled v8 12.6 g; reed ~1.5, microSD ~1.5, card ~0.5 gone
    dcg = -dm * (228.0 - 115.0) / (262.6 + dm)
    P("  CG (ESTIMATE vs the D9aft v10 rollup: 262.6 g, CG 228.0 from the tip, gate <= 226; e-bay at ~tip 115):")
    P("    sled %+.1f g, reed/microSD/card -3.5 g -> e-bay %+.1f g -> CG %+.1f mm aft -> ~%.1f: ~%.0f g EbayCap ballast to reach 226"
      % (m - 12.6, dm, dcg, 228.0 + dcg, (2.0 + dcg) / 0.6))
    P("    (+ the real solder / wire / heat shrink, never weighed).  WEIGH the built e-bay + line, re-run OpenRocket before flying.")

    rpt_mid = len(log)
    P("")
    P("[V] STORAGE -- free volume inside R %.1f from the deck floor to the cap face, minus sled, parts and the" % R_MAX_MOVING)
    P("    cable keep-outs.  v10 = the same on its FCStd (its envelopes), dropped parts (reed, microSD, card,")
    P("    Q3, loose Q1) counted as free.")
    shell = cyl(R_MAX_MOVING, DECK_FLOOR, CAP_Z0)
    fr = shell.cut(sled)
    for s in comp.values():
        fr = fr.cut(s)
    sols = sorted(fr.Solids, key=lambda s: -s.Volume)
    tot = sum(s.Volume for s in sols)
    P("  v11 total free %.0f mm3 (one connected space: every pocket opens to the face)" % tot)
    zones = [("aft deck behind the piezo frame (C1 in it)", box(-19.5, PBOSS_X0, -19.5, 19.5, DECK_FLOOR, BMP_Z0 - 0.01), "d10 can + resistors"),
             ("Nano -> BMP gap (S7V8F5 in it)", box(NANO_XT, BMP_PCB_X0, -LIP_Y[0], LIP_Y[0], NANO_Z0, BMP_Z1), "wire bends, inline resistors"),
             ("gutters N + S (cables off the Nano)", box(NANO_X0, CHEEK_XS, -GUT_Y, GUT_Y, DECK_FLOOR, CAP_Z0).cut(box(-30, 30, -LIP_Y[0], LIP_Y[0], -60, 60)), "wire runs"),
             ("behind the Nano (spine side)", box(SPINE_X1, NANO_X0, -LIP_Y[0], LIP_Y[0], NANO_Z0, NANO_Z1), "flat wire / resistors <= 3 mm"),
             ("fwd end round the chimney", box(NANO_XT, 19.5, -19.5, 19.5, BATT_Z0 + BATT_L, CAP_Z0).cut(box(-30, 30, JST_Y[0] - 0.01, JST_Y[1] + 0.01, -60, 60)), "battery lead slack, Qwiic slack"),
             ("over the battery (bore side, foam)", box(BATT_X0 + BATT_T, 19.5, -19.5, 19.5, BATT_Z0, BATT_Z0 + BATT_L), "foam / thin parts")]
    for nm, z, use in zones:
        P("    %-44s %6.0f mm3   (%s)" % (nm, vv(fr, z), use))
    try:
        d10 = App.openDocument(V10_FCSTD)
        s10 = d10.getObject("Sled").Shape
        f10 = shell.cut(s10)
        for o in d10.Objects:
            if o.Name.startswith("env_") and o.Name[4:] not in ("ReedModule", "MicroSD", "SD_card", "Q3_AO3401", "Q1_2N7000"):
                f10 = f10.cut(o.Shape)
        t10 = sum(s.Volume for s in f10.Solids)
        g10 = t10
        for o in d10.Objects:
            if o.Name[4:] in ("ReedModule", "MicroSD", "SD_card", "Q3_AO3401", "Q1_2N7000"):
                g10 -= vv(f10, o.Shape)
        P("  v10 free: %.0f mm3 as built for the OLD harness, %.0f if the dropped parts' room is counted as free"
          % (g10, t10))
        P("  -> v11 %+.0f mm3 vs v10-as-built, %+.0f vs v10-with-dropped-parts-freed (v10 cannot take the new harness:"
          % (tot - g10, tot - t10))
        P("     no TO-92 room behind the piezo, per-board loading from 3 sides, no 24 mm JST height anywhere)")
        App.closeDocument(d10.Name)
    except Exception as exc:
        P("  v10 comparison skipped (%s)" % exc)

    P("")
    P("[K] SLENDER MEMBERS (slices every 0.5 mm in Z; islands < 8 mm2 or area/longest side < 1.0, >= 6 slices)")
    rows = []
    zk = sled.BoundBox.ZMin + 0.25
    while zk < sled.BoundBox.ZMax:
        sec = sled.common(Part.makeBox(60, 60, 0.1, Vector(-30, -30, zk)))
        for so in sec.Solids:
            b_ = so.BoundBox; a_ = so.Volume / 0.1
            if a_ < 8.0 or a_ / max(b_.XLength, b_.YLength) < 1.0:
                rows.append((zk, b_, a_, a_ / max(b_.XLength, b_.YLength)))
        zk += 0.5
    grp = {}
    for zk, b_, a_, t_ in rows:
        grp.setdefault((round((b_.XMin + b_.XMax) / 3.0), round((b_.YMin + b_.YMax) / 3.0)), []).append((zk, b_, a_, t_))
    nk = 0
    for k_, v_ in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        if len(v_) < 6: continue
        nk += 1
        P("  x %6.1f..%6.1f y %6.1f..%6.1f  Z %6.1f..%6.1f (%2d slices)  area min %4.1f  t~%.2f   review"
          % (min(q[1].XMin for q in v_), max(q[1].XMax for q in v_), min(q[1].YMin for q in v_), max(q[1].YMax for q in v_),
             min(q[0] for q in v_), max(q[0] for q in v_), len(v_), min(q[2] for q in v_), min(q[3] for q in v_)))
    P("  %d slender groups" % nk)

    P("")
    _ovh = {}
    exec(open(os.path.join(PROJECT, "Avionics", "avbay_overhang_audit.py"), encoding="utf-8").read(), _ovh)
    _ovh["overhang_audit"](sled, P, zbed=SEAT_Z)
    P("  v10 (same audit): 31 regions, 389 mm2, flat 363 mm2, largest reach 7.8 mm;  v9 (spaghetti): 1230 mm2, reach 10.3")

    P("")
    P("[N] ASSEMBLY (all from +x, sled in hand)")
    P("  1 Nano, parts up, USB-C + JST to the cap end, onto the back ribs; its aft end on the rib heels, sides between the")
    P("    lips.  Lead its wires off the pads sideways into the gutters.  Kapton strap across it (nothing printed can")
    P("    hold a deepest part down without blocking it) -- the BMP stack above holds it in flight.")
    P("  2 C1 (+ resistors) into the aft deck through the piezo frame window, before the piezo; S7V8F5 flat on the")
    P("    Nano's parts with Kapton between.  Hot glue / Kapton.")
    P("  3 BMP388 FLIPPED (parts + plugs down), aft holes on the bosses, 2 x M2.5x8 from +x; fwd end on the ledges.")
    P("  4 piezo (can out), 2 x M2x6 -- the TO-92 sits in the frame window.  Pan head on the d3 hole: file a flat (can side).")
    P("  5 ADXL375: double-sided tape / CA on the BMP's PCB back, plug forward; Qwiic over the BMP's fwd end.")
    P("  6 battery on 1 mm foam over the ADXL, Kapton wrap; plug its lead into the Nano's JST down the chimney (= ON).")
    P("  7 EbayCap: W M2x10 only.")
    P("  ASSUMED (measure / photo before printing):")
    for a in ASSUMED:
        P("    - " + a)

    P("")
    P("[E] EXPORT")
    os.makedirs(AV_MODELS, exist_ok=True)
    base = os.path.join(AV_MODELS, "PhoenixABS40-43_avbay_ElectronicsSled_%s" % REV)
    sled.exportStep(base + ".step")
    smesh.write(base + ".stl")
    P("  %s .step + .stl" % os.path.basename(base))
    doc.addObject("Part::Feature", "Sled").Shape = sled          # explicit doc: [V] opened (and closed) the v10 FCStd
    for n, s in comp.items():
        doc.addObject("Part::Feature", "env_" + n).Shape = s
    doc.recompute()
    fc = os.path.join(AVIONICS, "PhoenixABS40-43_avbay_sled_%s.FCStd" % REV)
    doc.saveAs(fc)
    P("  FCStd -> Avionics/%s" % os.path.basename(fc))
    comb = sled
    for s in comp.values():
        comb = comb.fuse(s)
    mesh_of(comb).write(base.replace("ElectronicsSled", "sled_ASSEMBLY") + ".stl")
    P("  sled_ASSEMBLY_%s.stl" % REV)

    fails = [l.strip() for l in log if l.rstrip().endswith("FAIL") or "FAIL " in l or "CLASH" in l]
    warns = [l.strip() for l in log if l.rstrip().endswith("WARN") or "WARN " in l or "WARN (" in l]
    head = ["SUMMARY: %d FAIL / clash lines, %d WARN lines" % (len(fails), len(warns))]
    head += ["  FAIL  " + l for l in fails] + ["  WARN  " + l for l in warns]
    head += ["  ASSUMED dims (not measured):"] + ["    - " + a for a in ASSUMED] + [""]
    rpt = "\n".join(log[:3] + head + log[3:])
    with open(os.path.join(AVIONICS, "avbay_sled_build_report_%s.txt" % REV), "w") as fh:
        fh.write(rpt + "\n")
    print(rpt)

main()

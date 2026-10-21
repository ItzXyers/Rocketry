# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v12  (soldered harness, one-side press-in, SIDE PANELS)

v12 = v11 re-laid (2026-10-20, user on v11's "ADXL taped on the flipped BMP": "We're not doing this.  The ADXL
needs to be GLUED by itself to make sure we get good accelerometer data from it.  Also, the ESP32 needs rails,
I want as many rails as possible.").  v11's answers still hold (see v11 header): TO-92 flat on the piezo back,
S7V8F5 / C1 470 uF / inline resistors loose, both BMP Qwiic plugs + the ADXL "top" plug used, the ESP32 at the
absolute bottom with its 24 mm power JST at the USB-C end on +y, one-side press-in, length kept.

LAYOUT (x = depth: -x = spine / bottom, +x = open face = the static + sound port side = press-in direction)
  * Two full-length SIDE WALLS (x-z planes) N and S.  Their inner faces ARE the ESP32 rails (|y| 9.4, crush
    ribs to 9.0 -> the board presses in snug along its whole length); above x 7.4 they step out to |y| 10.4 and
    guide the battery.  Their OUTER faces (|y| 11.4) are glue panels:
      - ADXL375 GLUED flat on the N wall's outer face (board normal = +y as v10, long axis Z, plug FWD),
        on 2 mm of wall tied to the spine, floor and cap face -- printed sled only, nothing in between.
      - BMP388 glued (tape) on the S wall's outer face, parts outboard.
  * Between the walls: ESP32 (parts up, USB-C + JST fwd) on back ribs, then a 15 x 18.8 mm OPEN COLUMN over
    its whole length (wires straight up off the pads, S7V8F5, resistors, Qwiic slack), then the battery on top.
  * Aft deck as v11: piezo frame (TO-92 window), C1 behind it, lead exit from the pin bay under the N wall.
  * Qwiic: ADXL fwd plug -> through a N-wall window -> across the column -> S-wall window -> BMP fwd plug;
    BMP aft plug -> S-wall aft window -> column -> ESP32 I2C pads.
  * EbayCap EAST boss still deleted (the battery sits under it) -- W screw + spine key only.

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
REV = "v12"
RHO = 1.05e-3
R_AF_I = 20.0
R_MAX_MOVING = 19.5
SLED_RMAX = 19.39
CL = 0.40
WALL = 1.20
KNEE = 1.15
ZONE_Z1 = 48.0

CAP_Z0 = 45.4
MOUNT_XW, MOUNT_XE = -15.3, 10.1          # MOUNT_XE: the cap's east hole -- NO boss under it (v11, v12)
MOUNT_HOLE_D = 2.0
MOUNT_BOSS_R = MOUNT_HOLE_D / 2.0 + 1.6
MOUNT_PILOT_DEPTH = 12.0
SERVO_TAB_XW, SERVO_TAB_XE = MOUNT_XW, MOUNT_XE
WBOSS_X1 = -13.5
WBOSS_Z0 = 39.4

SEAT_Z = -22.8
DECK_FLOOR = SEAT_Z + WALL                # -21.6
FOOT_RO = 19.3
SPINE_X1 = -16.6

# PIEZO (as v11)
PIEZO_ZC = -12.1
PIEZO_DL, PIEZO_DZ = 19.0, 15.0
PIEZO_PCB_T = 1.6
PIEZO_PCB_X0 = 6.8
PIEZO_CAN_H, PIEZO_CAN_D = 10.0, 12.0
PIEZO_X1 = PIEZO_PCB_X0 + PIEZO_PCB_T + PIEZO_CAN_H
PIEZO_Y0 = -8.0
PIEZO_Y1 = PIEZO_Y0 + PIEZO_DL            # 11.0
PIEZO_Z0 = PIEZO_ZC - PIEZO_DZ / 2.0      # -19.6
PIEZO_Z1 = PIEZO_Z0 + PIEZO_DZ            # -4.6
PIEZO_HDR = (2.5, 2.5, 7.6)
PIEZO_PIN_X = (0.95, 1.6)
PIEZO_PIN_BEND = (1.5, 2.0, 5.5)
PIEZO_PIN_Z = 5.7
PIN_BAY = (PIEZO_PCB_X0, 12.0, PIEZO_Y1, PIEZO_Y1 + 7.0)
PIEZO_SCREW_D = 2.0
PIEZO_HOLE_SPEC = ((2.5, 0.75, 0.50, -1), (3.0, 0.75, 0.75, +1))
PIEZO_HOLE_LIST = [(PIEZO_Y0 + dt + d / 2.0, PIEZO_ZC + sz * (PIEZO_DZ / 2.0 - ds - d / 2.0), d)
                   for d, dt, ds, sz in PIEZO_HOLE_SPEC]
FRAME_X0 = 4.2
FRAME_BAR_Y1 = PIEZO_Y0 + 4.5             # -3.5
FRAME_RAIL_Z1 = PIEZO_Z0 + 1.0            # -18.6
PBOSS_X0 = FRAME_X0 - 2.0                 # 2.2
PBOSS_R = PIEZO_SCREW_D / 2.0 + 1.2
END_WALL_Y = (PIEZO_Y0 - CL - WALL, PIEZO_Y0 - CL)         # -9.6 .. -8.4
FRAME_TOP = PIEZO_Z1                      # v12: back to the board top (v11 lowered it for the BMP's pan heads)
END_WALL_TOP = PIEZO_Z1                   # v12: the battery's aft stop again (0.4 under the pack)
Q1_T = 4.4
Q1_ZONE = (PIEZO_PCB_X0 - Q1_T, PIEZO_PCB_X0, FRAME_BAR_Y1, PIEZO_Y1, PIEZO_Z0 + 1.0, PIEZO_Z1 - 1.0)

# NANO ESP32 -- bottom of the stack
NANO_W, NANO_L, NANO_PCB_T, NANO_T = 18.0, 45.0, 1.6, 5.0
NANO_X0 = -12.6
NANO_XF = NANO_X0 + NANO_PCB_T            # -11.0
NANO_XT = NANO_X0 + NANO_T                # -7.6
NANO_Z0 = -0.3
NANO_Z1 = NANO_Z0 + NANO_L                # 44.7
NANO_ROW_Y = 15.24 / 2.0
NANO_PAD_R = 0.85
NANO_JOINT_H = 0.5
NANO_PADS_Z = [NANO_Z0 + NANO_L / 2.0 + (i - 7) * 2.54 for i in range(15)]
NANO_EDGE = 0.6
JST_W, JST_H = 6.0, 24.0
JST_Y = (3.0, 3.0 + JST_W)                # +y, 0.4 inside the N rail
JST_ZL = 7.5
RIB_Y = (1.5, 5.5)
HEEL_X1 = NANO_XF

# SIDE WALLS
RAIL_Y = NANO_W / 2.0 + CL                # 9.4 inner face at the Nano / column
CRUSH_Y = NANO_W / 2.0                    # 9.0 crush ribs: zero clearance on the PCB edges (press fit)
CRUSH_Z = (1.5, 11.0, 21.0, 31.0, 41.0)   # 1.0 wide in Z, x NANO_X0 - 0.5 .. NANO_XF (PCB edge only)
BAT_Y = 10.0 + CL                         # 10.4 inner face at the battery
WALL_OUT = 11.4                           # outer face = glue panels
PANEL_X1 = 7.4                            # inner face steps 9.4 -> 10.4 here (battery bottom 7.8)
N_Q1_KNEE = (2.0, PIEZO_Z1 + CL)          # N wall absent east of x 2.0 below a 1:1.15 line from Z -4.2 (piezo, Q1, pins)
LEAD_EXIT = (-0.6, -12.5)                 # ... and east of x -0.6 below a line from Z -12.5 (piezo leads -> aft deck)
WIN_N_FWD = (-5.0, 5.0, 29.6, 37.0)       # x0, x1, z0, springing: ADXL Qwiic into the column (arch over it)
WIN_S_FWD = (-5.0, 5.0, 34.6)             # open to the cap face: BMP fwd plug cable
WIN_S_AFT = (-6.0, 6.0, -18.0, -12.5)     # BMP aft plug cable into the aft deck (pointed arch)
BATT_STOP = ((9.0, 9.4), 1.5)             # fwd battery stops off the walls: inner |y| (S, N: JST at y <= 9.0)

# ADXL375 glued on the N wall outer face
ADXL_W, ADXL_PCB_L, ADXL_L, ADXL_T = 18.0, 26.0, 27.0, 5.0
GLUE = 0.2
ADXL_Y0 = WALL_OUT + GLUE                 # 11.6 PCB back
ADXL_X = (-9.0, 9.0)
ADXL_Z0 = 2.0
ADXL_PLUG_HW = 4.0

# BMP388 glued on the S wall outer face, parts outboard
BMP_W, BMP_L, BMP_PCB_T, BMP_PARTS = 22.0, 40.0, 1.6, 2.4
BMP_Y0 = -(WALL_OUT + GLUE)               # -11.6 PCB back
BMP_X = (-11.0, 11.0)
BMP_Z0 = -6.0
BMP_Z1 = BMP_Z0 + BMP_L                   # 34.0
QW_PLUG = (2.95, 4.25, 2.7)
QW_BEND = 1.5

# BATTERY on top between the walls
BATT_L, BATT_W, BATT_T = 40.5, 20.0, 8.5
BATT_X0 = PANEL_X1 + CL                   # 7.8
BATT_Z0 = PIEZO_Z1 + CL                   # -4.2

# SMALL PARTS
C1_D, C1_L = 10.0, 14.0
C1_POS = (-12.2, -12.2 + C1_L, -3.5, DECK_FLOOR + 0.2 + C1_D / 2.0)
S7_BOX = (NANO_XT + CL, NANO_XT + CL + 3.5, -5.5, 5.5, 5.0, 22.0)

# D9aft
D9_DZ = 279.2
D9_R_ID, D9_R_OD = 20.0, 21.5
D9_CREST = 19.65
D9_BAND_Z = 60.8 - 12.5
D9_SEAT_Z, D9_SEAT_RI, D9_SEAT_T = SEAT_Z, 15.5, 2.0
D9_SPIGOT_RI = 18.5
D9_PORTS = (("static", 1.5, 30.0, 0.0), ("sound", 3.0, PIEZO_ZC, 0.0))
D9V10_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v10_%s.step" % k)) for k in ("EbayCap", "FwdTube"))
V10_FCSTD = os.path.join(PROJECT, "Avionics", "PhoenixABS40-43_avbay_sled_v10.FCStd")
DRIVER_D = 3.0

ASSUMED = [
    "Q1 TO-92 position on the piezo back: anywhere in the old joint footprint (y -3.5..11, Z -18.6..-5.6), 4.4 deep",
    "C1 470 uF 16 V: d10 x 12.5 body + 1.5 bent leads (d8 x 11.5 is also common -> more room)",
    "S7V8F5 17 x 11 x 3 + 0.5 joints, lying on the Nano's parts (Kapton between) -- anywhere in the column",
    "JST-PH on the Nano: +y (left of the USB-C looking at the port, parts side up), y 3.0..9.0, last 7.5 mm",
    "ESP32 PCB 18.0 wide: the crush ribs sit at exactly 18.0 -- file / heat-set them if it is too tight",
    "Qwiic plug 2.95 deep x 4.25 long x 5.4 wide; cables bend 1.5 past the plug",
    "Nano USB-C <= 0.3 past the PCB end; Nano parts 3.4 tall, 0.6 edge bands free; back joints 0.5",
    "ADXL375 Qwiic plug centred on its 'top' (short) end, 8 wide; ADXL back flat enough to glue",
    "BMP388 back flat enough to tape; plugs centred on both short ends (user, v10)",
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
    if axis == "x":
        vs = [Vector(u, w0, z) for u, z in pts_uz]; d = Vector(0, w1 - w0, 0)
    else:
        vs = [Vector(w0, u, z) for u, z in pts_uz]; d = Vector(w1 - w0, 0, 0)
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(d)

def knee_cut(axis, u_face, z_face, sgn, w0=-30.0, w1=30.0):
    D, B = 60.0, 80.0
    pts = [(u_face, z_face - B), (u_face, z_face), (u_face + sgn * D, z_face + KNEE * D), (u_face + sgn * D, z_face - B)]
    return prism(axis, pts, w0, w1)

def corbel(solid, axis, u_face, z_bottom_far, u_far, w0=-30.0, w1=30.0):
    sgn = 1.0 if u_far > u_face else -1.0
    z_face = z_bottom_far - KNEE * abs(u_far - u_face)
    return solid.cut(knee_cut(axis, u_face, z_face, sgn, w0, w1))

def arch_win(x0, x1, z0, zs, y0, y1):
    """window through a wall (x-z plane) from z0 up to a pointed 1:1.15 arch springing at zs"""
    xm = (x0 + x1) / 2.0
    return prism("x", [(x0, z0), (x1, z0), (x1, zs), (xm, zs + KNEE * (x1 - x0) / 2.0), (x0, zs)], y0, y1)

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
    return box(NANO_XF, NANO_XF + JST_H, JST_Y[0], JST_Y[1], NANO_Z1 - JST_ZL, NANO_Z1)

def env_adxl():
    y1 = ADXL_Y0 + ADXL_T
    s = box(ADXL_X[0], ADXL_X[1], ADXL_Y0, y1, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    s = s.fuse(box(-ADXL_PLUG_HW, ADXL_PLUG_HW, ADXL_Y0, y1, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 + ADXL_L))
    return as_solid(s.removeSplitter())

def env_bmp():
    """PCB back on the S wall (y -11.6), parts outboard to -15.6, Qwiic plugs on both centred short ends"""
    yp = BMP_Y0 - BMP_PCB_T
    s = box(BMP_X[0], BMP_X[1], yp - BMP_PARTS, BMP_Y0, BMP_Z0, BMP_Z1)
    d, ln, hw = QW_PLUG
    s = s.fuse(box(-hw, hw, yp - d, yp, BMP_Z0 - ln, BMP_Z0))
    s = s.fuse(box(-hw, hw, yp - d, yp, BMP_Z1, BMP_Z1 + ln))
    return as_solid(s.removeSplitter())

def env_qwiic_adxl_bmp():
    """ADXL fwd plug -> up the outside of the N wall -> through its window -> across the column -> S window ->
    BMP fwd plug (U-turn past its end)"""
    d, ln, hw = QW_PLUG
    zc0, zc1 = WIN_S_FWD[2] + 0.2, BATT_Z0 + BATT_L           # crossing band: S window .. under the battery stops / JST
    yp = BMP_Y0 - BMP_PCB_T                                     # -13.2: BMP parts face (the plug sits outboard of it)
    s = box(-hw, hw, ADXL_Y0, ADXL_Y0 + ADXL_T, ADXL_Z0 + ADXL_L, zc1)                     # up the outside of the N wall
    s = s.fuse(box(-hw, hw, BMP_Y0 + 0.01, ADXL_Y0 + 0.01, zc0, zc1))                       # across (both windows)
    s = s.fuse(box(-hw, hw, yp - d, BMP_Y0, BMP_Z1 + ln, BMP_Z1 + ln + QW_BEND))           # bend past the plug end
    s = s.fuse(box(-hw, hw, yp + 0.05, BMP_Y0, zc0, BMP_Z1 + ln + 0.01))                    # back down beside the plug
    return as_solid(s.removeSplitter())

def env_qwiic_bmp_nano():
    """BMP aft plug -> bend -> S aft window -> over C1 -> up the column to the ESP32's aft end"""
    d, ln, hw = QW_PLUG
    za = BMP_Z0 - ln - QW_BEND                                  # -11.75 bend under the plug
    zx = -11.0                                                  # crossing: over C1 (top -11.4), under the arch
    s = box(-hw, hw, BMP_Y0 - BMP_PCB_T - d, BMP_Y0, za, BMP_Z0 - ln)                       # bend past the plug end
    s = s.fuse(box(-hw, 1.8, BMP_Y0 - 0.01, -7.0, za, BMP_Z0 - ln))                         # in through the S aft window
    s = s.fuse(box(NANO_XT, 1.8, -7.0, -4.0, zx, zx + 2.5))                                 # over C1
    s = s.fuse(box(NANO_XT, NANO_XT + 2.5, -7.0, -4.0, zx, NANO_Z0 + 2.0))                  # up to the ESP32's aft end
    return as_solid(s.removeSplitter())

def env_batt():
    return box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0, BATT_Z0 + BATT_L)

def env_piezo():
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
    ("Piezo_Q1",     env_piezo),
    ("ADXL375",      env_adxl),
    ("BMP388",       env_bmp),
    ("Qwiic_ADXL_BMP", env_qwiic_adxl_bmp),
    ("Qwiic_BMP_Nano", env_qwiic_bmp_nano),
    ("Battery",      env_batt),
]
RIGID = [n for n, _ in COMPONENTS]

# ================================================================ the sled
def build_sled(log):
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)

    parts.append(clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, SEAT_Z, ZONE_Z1 - 0.6)))     # spine + key
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, DECK_FLOOR)))                                    # floor disc

    # ---- side walls: rails (inner |y| 9.4, x up to 7.4), battery guides (inner 10.4 above), glue panels (outer 11.4)
    for sy in (-1, 1):
        def yb(a, b):
            return tuple(sorted((sy * a, sy * b)))
        w = box(-19.0, PANEL_X1, *yb(RAIL_Y, WALL_OUT), DECK_FLOOR - 0.01, CAP_Z0)
        w = w.fuse(box(PANEL_X1 - 0.01, 19.5, *yb(BAT_Y, WALL_OUT), DECK_FLOOR - 0.01, CAP_Z0))
        for zc in CRUSH_Z:                                                                 # crush ribs on the PCB edges
            w = w.fuse(box(NANO_X0 - 0.5, NANO_XF, *yb(CRUSH_Y, RAIL_Y + 0.01), zc - 0.5, zc + 0.5))
        if sy > 0:
            w = w.cut(knee_cut("x", N_Q1_KNEE[0], N_Q1_KNEE[1], +1))                       # piezo board / Q1 / pins
            w = w.cut(knee_cut("x", LEAD_EXIT[0], LEAD_EXIT[1], +1))                       # piezo leads -> aft deck
            x0, x1, z0, zs = WIN_N_FWD
            w = w.cut(arch_win(x0, x1, z0, zs, RAIL_Y - 1, WALL_OUT + 1))                  # Qwiic ADXL -> column
        else:
            x0, x1, z0 = WIN_S_FWD
            w = w.cut(box(x0, x1, -WALL_OUT - 1, -RAIL_Y + 1, z0, CAP_Z0 + 1))              # Qwiic column -> BMP fwd
            x0, x1, z0, zs = WIN_S_AFT
            w = w.cut(arch_win(x0, x1, z0, zs, -WALL_OUT - 1, -RAIL_Y + 1))                # Qwiic BMP aft -> deck
        parts.append(cap(w))
        # fwd battery stop: flat ledge over the pack's fwd edge band (1.0 - 1.4 off the guide face)
        yi = BATT_STOP[0][0 if sy < 0 else 1]
        z0 = BATT_Z0 + BATT_L + CL
        parts.append(cap(box(BATT_X0 + 0.4, 14.4, *yb(yi, BAT_Y + 0.01), z0, z0 + BATT_STOP[1])))

    # ---- ESP32 back ribs + heels under its aft end
    for sy in (-1, 1):
        y0, y1 = sorted((sy * RIB_Y[0], sy * RIB_Y[1]))
        rib = box(SPINE_X1 - 0.1, NANO_X0, y0, y1, -12.0, NANO_Z1)
        rib = rib.fuse(box(NANO_X0 - 0.01, HEEL_X1, y0, y1, -12.0, NANO_Z0 - 0.1))
        rib = corbel(rib, "x", SPINE_X1, NANO_Z0 - 1.3, HEEL_X1)
        parts.append(cap(rib))

    # ---- W cap boss
    wb = cyl(MOUNT_BOSS_R, 25.0, CAP_Z0, MOUNT_XW, 0.0).cut(box(WBOSS_X1, 30, -30, 30, 0, 60))
    wb = corbel(wb, "x", SPINE_X1, WBOSS_Z0, WBOSS_X1)
    parts.append(cap(wb))
    drill.append(cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, MOUNT_XW, 0.0))

    # ---- piezo frame (v11)
    pb = box(FRAME_X0, PIEZO_PCB_X0, PIEZO_Y0 - CL, FRAME_BAR_Y1, DECK_FLOOR - 0.01, FRAME_TOP)
    pb = pb.fuse(box(PBOSS_X0, FRAME_X0 + 0.01, PIEZO_Y0 - CL, FRAME_BAR_Y1 - CL, DECK_FLOOR - 0.01, PIEZO_HOLE_LIST[1][1]))
    for yc, zc, _ in PIEZO_HOLE_LIST:
        pb = pb.fuse(cyl_x(PBOSS_R, PBOSS_X0, FRAME_X0 + 0.01, yc, zc))
        drill.append(cyl_x(PIEZO_SCREW_D / 2.0 - 0.2, PBOSS_X0 - 0.5, PIEZO_PCB_X0 + 1.0, yc, zc))
    pb = pb.cut(box(PBOSS_X0 - 0.1, PIEZO_PCB_X0 + 0.1, PIEZO_Y0 - CL - 0.1, FRAME_BAR_Y1 + 0.1, FRAME_TOP, 0.0))
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
        for s in sol:
            b = s.BoundBox
            log.append("    piece %.1f mm3 at x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f" % (s.Volume, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
        raise RuntimeError("sled is %d disconnected solids\n%s" % (len(sol), "\n".join(log[-len(sol):])))
    if not sol[0].isValid():
        raise RuntimeError("sled solid is INVALID after the build")
    return sol[0], raw

# ================================================================ verification
def main():
    log = []
    P = log.append
    P("=" * 78)
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (soldered harness, one-side press-in, side panels)" % REV)
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
        P("  %-15s %5.1f.%4.1f.%4.1f  %6.1f %6.1f  %6.2f" % (n, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax, rmax_mesh(cmesh[n])))
    sbb = smesh.BoundBox
    P("  %-15s %5.1f.%4.1f.%4.1f  %6.1f %6.1f  %6.2f   <- the sled" % ("Sled", sbb.XLength, sbb.YLength, sbb.ZLength, sbb.ZMin, sbb.ZMax, rmax_mesh(smesh)))

    P("")
    P("[0] CONTAINMENT  (Rmax vs %.1f moving / %.1f ID)" % (R_MAX_MOVING, R_AF_I))
    zmax = 0.0
    for n, s in comp.items():
        r = rmax_mesh(cmesh[n]); zmax = max(zmax, cmesh[n].BoundBox.ZMax)
        tag = "PASS" if r <= R_MAX_MOVING + 1e-6 else ("past moving  FAIL" if r <= R_AF_I else "*** PAST ID ***  FAIL")
        P("  %-15s Rmax %6.2f  toID %5.2f   %s" % (n, r, R_AF_I - r, tag))
    rs = rmax_mesh(smesh)
    P("  %-15s Rmax %6.2f  toID %5.2f   %s" % ("Sled", rs, R_AF_I - rs, "PASS" if rs <= SLED_RMAX + 0.05 else "FAIL"))
    P("  component tops Z .. %.1f vs EbayCap face %.1f   %s" % (zmax, CAP_Z0, "PASS" if zmax <= CAP_Z0 - 0.3 else "FAIL"))
    above = sled.common(box(-30, 30, -30, 30, CAP_Z0 + 0.01, ZONE_Z1 + 5))
    key = clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, CAP_Z0 + 0.01, ZONE_Z1 - 0.6))
    sv = vol(above.cut(key))
    P("  above EbayCap face: %.1f mm3, outside the spine key %.2f   %s" % (vol(above), sv, "PASS" if sv < 0.01 else "FAIL"))
    top = sled.common(box(-30, 30, -30, 30, CAP_Z0 - 0.2, CAP_Z0))
    ring = cyl(1.8, CAP_Z0 - 0.2, CAP_Z0, MOUNT_XW, 0.0).cut(cyl(MOUNT_HOLE_D / 2.0, CAP_Z0 - 1, CAP_Z0 + 1, MOUNT_XW, 0.0))
    f = vv(top, ring) / ring.Volume
    P("  EbayCap W M2 boss (%.1f, 0) seated at Z %.1f: %.0f %% of the head footprint backed   %s" % (MOUNT_XW, CAP_Z0, 100 * f, "PASS" if f > 0.95 else "FAIL"))
    P("  EbayCap E M2 boss (%.1f, 0): DELETED -- leave the cap's east screw OUT, tape the hole (W screw + spine key hold it)" % MOUNT_XE)

    P("")
    P("[F] PRESS-IN -- every part along +x in ASSEMBLY ORDER, deepest first (sled in hand, out of the tube).")
    P("    Each part moves along its path, then +x until it is clear of the bore; it must not touch the sled or any")
    P("    part already in (touching = 0 mm3 is allowed: the ESP32 crush ribs are a zero-clearance press fit).")
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
            ("C1_470uF",   ["C1_470uF"], [(Vector(0, 0, 1), 3.2), (Vector(0, 1, 0), 5.5), (X, None)]),
            ("S7V8F5",     ["S7V8F5"], [(X, None)]),
            ("Piezo_Q1",   ["Piezo_Q1"], [(X, None)]),
            ("ADXL375",    ["ADXL375"], [(X, None)]),
            ("BMP388",     ["BMP388"], [(X, None)]),
            ("Battery",    ["Battery"], [(X, None)])]
    loaded = []
    for nm, members, path in LOAD:
        sh = comp[members[0]]
        for m in members[1:]:
            sh = sh.fuse(comp[m])
        others = [("Sled", sled)] + [(k, comp[k]) for k in loaded]
        h = sweep(sh, path, others)
        ps = " then ".join("%s%s" % ("(%+.0f,%+.0f,%+.0f)" % (d.x, d.y, d.z), (" %.1f" % L) if L else " out") for d, L in path)
        P("  %-15s %-34s %s   %s" % (nm, ps, "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), "PASS" if not h else "FAIL"))
        loaded += members
    P("  Qwiic cables: unplugged while the boards go in, then threaded through the wall windows (a plug is 5.4 x 4.25,")
    P("  the windows are >= 10 x 7) and plugged; their lanes are checked static in [X] / [I].  Battery JST: plugged LAST.")
    order_q = [n for _, ms, _ in LOAD for n in ms] + ["Qwiic_ADXL_BMP", "Qwiic_BMP_Nano"]
    for k in ("Qwiic_ADXL_BMP", "Qwiic_BMP_Nano"):
        hit = [(n2, round(vv(comp[k], comp[n2]), 2)) for n2 in order_q if n2 != k and vv(comp[k], comp[n2]) > 1e-2]
        P("  %-15s laid in after the boards: overlaps %s   %s" % (k, hit or "nothing", "PASS" if not hit else "FAIL"))

    P("")
    P("[R] ESP32 RAILS")
    nb = comp["Nano_ESP32"]
    for sy, nm in ((1, "N"), (-1, "S")):
        face = box(NANO_X0, NANO_XF, sy * (NANO_W / 2.0) - (0.6 if sy > 0 else 0.0), sy * (NANO_W / 2.0) + (0.6 if sy < 0 else 0.0), NANO_Z0, NANO_Z1)
        cont = box(NANO_X0, NANO_XF, *sorted((sy * CRUSH_Y, sy * (CRUSH_Y + 0.05))), NANO_Z0, NANO_Z1)
        guide = box(NANO_X0, NANO_XT, *sorted((sy * RAIL_Y, sy * (RAIL_Y + 0.05))), NANO_Z0, NANO_Z1)
        P("  %s rail: wall face over %.1f of the board's %.1f mm length (0.4 clear), %d crush ribs touching the PCB edge (%.1f mm2)   %s"
          % (nm, vol(sled.common(guide)) / (0.05 * (NANO_XT - NANO_X0)), NANO_L, len(CRUSH_Z), vv(sled, cont) / 0.05,
             "PASS" if vv(sled, cont) / 0.05 > 0.8 * len(CRUSH_Z) * 1.6 else "FAIL"))
    hb = vv(sled, box(NANO_X0, NANO_XF, -NANO_W / 2.0, NANO_W / 2.0, NANO_Z0 - 0.5, NANO_Z0 - 0.1)) / 0.4
    bk = vv(sled, box(NANO_X0 - 0.1, NANO_X0, -NANO_W / 2.0, NANO_W / 2.0, NANO_Z0, NANO_Z1)) / 0.1
    P("  aft end on the rib heels %.1f mm2 (0.1 gap); back on 2 full-length ribs %.0f mm2; fwd end 0.7 under the cap face   %s"
      % (hb, bk, "PASS" if hb > 4 and bk > 200 else "FAIL"))
    P("  joints on the back -> sled %.2f mm (between the ribs)   %s" % (comp["Nano_joints"].distToShape(sled)[0],
      "PASS" if comp["Nano_joints"].distToShape(sled)[0] >= 0.25 else "FAIL"))

    P("")
    P("[A] ADXL375 GLUED ON THE N WALL (printed sled only)")
    pts = [(x, z) for x in [ADXL_X[0] + 1.0 + 2.0 * i for i in range(9)] for z in [ADXL_Z0 + 1.0 + 3.0 * j for j in range(9)]]
    back = sum(1 for x, z in pts if sled.common(Part.makeLine(Vector(x, ADXL_Y0 - GLUE + 0.01, z), Vector(x, ADXL_Y0 - GLUE - 1.0, z))).Edges)
    thick = [sum(e.Length for e in sled.common(Part.makeLine(Vector(x, ADXL_Y0, z), Vector(x, 0.0, z))).Edges) for x, z in pts]
    P("  glue face y %.1f: %d / %d grid points (x %.0f..%.0f, Z %.0f..%.0f) have wall right behind the PCB; wall there %.1f..%.1f mm thick   %s"
      % (WALL_OUT, back, len(pts), ADXL_X[0], ADXL_X[1], ADXL_Z0, ADXL_Z0 + ADXL_PCB_L, min(thick), max(thick), "PASS" if back >= 0.9 * len(pts) else "FAIL"))
    P("  the wall: 2.0 mm (x < %.1f) / 1.0 mm (battery guide), floor -> cap face, tied to the spine, floor disc and cap" % PANEL_X1)
    P("  pose: long axis = rocket Z, board normal = +y (as v10), plug FORWARD (v10 aft) -> firmware axis map")
    pts = [(x, z) for x in [BMP_X[0] + 1.0 + 2.5 * i for i in range(9)] for z in [BMP_Z0 + 1.0 + 4.0 * j for j in range(10)]]
    back = sum(1 for x, z in pts if sled.common(Part.makeLine(Vector(x, BMP_Y0 + GLUE - 0.01, z), Vector(x, BMP_Y0 + GLUE + 1.0, z))).Edges)
    P("  BMP388 on the S wall: %d / %d grid points of its back have wall behind them (the aft window takes a corner)   %s"
      % (back, len(pts), "PASS" if back >= 0.85 * len(pts) else "FAIL"))

    P("")
    P("[I] FIT -- RAW = the as-drawn sled inside each part's keep-out BEFORE the trim; post-cut must be 0.")
    for n in comp:
        P("  %-15s RAW %7.1f mm3   post-cut %.1f   %s" % (n, raw.get(n, 0.0), vv(sled, comp[n]), "" if raw.get(n, 0.0) < 0.5 else "(sled member trimmed by the part -- review)"))
    cn = list(comp.keys()); cc = 0
    designed = {("Nano_ESP32", "JST_power")}
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            v = vv(comp[cn[i]], comp[cn[j]])
            if (cn[i], cn[j]) in designed:
                P("    designed: %s on %s" % (cn[j], cn[i])); continue
            if v > 0.05:
                cc += 1; P("    CLASH %s <-> %s  %.2f mm3   FAIL" % (cn[i], cn[j], v))
    P("  part-vs-part clashes: %d   %s" % (cc, "PASS" if cc == 0 else "FAIL"))
    P("  gaps between neighbours (want >= %.1f):" % (CL - 0.05))
    for a, b in (("Nano_ESP32", "S7V8F5"), ("S7V8F5", "Battery"), ("Battery", "Piezo_Q1"), ("JST_power", "Battery"),
                 ("JST_power", "Qwiic_ADXL_BMP"), ("ADXL375", "Battery"), ("BMP388", "Battery"), ("C1_470uF", "Qwiic_BMP_Nano"),
                 ("Piezo_Q1", "Qwiic_BMP_Nano"), ("BMP388", "Piezo_Q1"), ("ADXL375", "Piezo_Q1")):
        g = comp[a].distToShape(comp[b])[0]
        P("    %-15s - %-15s %5.2f   %s" % (a, b, g, "PASS" if g >= CL - 0.05 else "WARN"))

    P("")
    P("[S] SCREW ACCESS (d%.1f driver from the head along +x; sees the sled + every part in before that screw)" % DRIVER_D)
    order = [n for _, ms, _ in LOAD for n in ms]
    for hy, hz, d in PIEZO_HOLE_LIST:
        drv = Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(PIEZO_PCB_X0 + PIEZO_PCB_T + 1.8, hy, hz), X)
        inn = order[:order.index("Piezo_Q1")]
        hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp[k]) for k in inn] for v in [vv(sh, drv)] if v > 1e-2]
        P("  piezo M2 d%.1f y%+.1f  %s   %s" % (d, hy, "clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    hy, hz, _ = PIEZO_HOLE_LIST[0]
    ncv = vv(sled, Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(PIEZO_PCB_X0, hy, hz), Vector(-1, 0, 0)))
    P("  NEGATIVE CONTROL: same driver pointed INTO the sled (-x) hits it %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))

    P("")
    P("[H] HOLES + SEATS")
    for hy, hz, d in PIEZO_HOLE_LIST:
        th = sled.common(Part.makeLine(Vector(PIEZO_PCB_X0, hy, hz + 1.0), Vector(PIEZO_PCB_X0 - 8.0, hy, hz + 1.0)))
        tl = sum(e.Length for e in th.Edges)
        ann = cyl_x(2.0, PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, hy, hz).cut(cyl_x(1.3, PIEZO_PCB_X0 - 1, PIEZO_PCB_X0 + 1, hy, hz))
        f = vv(sled, ann) / ann.Volume
        gap = math.hypot(hy, hz - PIEZO_ZC) - PIEZO_CAN_D / 2.0 - 1.9
        P("  piezo M2 (y %+5.2f, Z %.2f): thread %.1f mm %s; bar under the hole %3.0f %% %s; M2 head to can %.2f %s"
          % (hy, hz, tl, "PASS" if tl >= 4.0 else "FAIL", 100 * f, "PASS" if f > 0.8 else "FAIL", gap, "PASS" if gap > 0.2 else "WARN (as v10: file a flat on that pan head)"))
    wl = sum(e.Length for e in sled.common(Part.makeLine(Vector(MOUNT_XW, 0.9, CAP_Z0), Vector(MOUNT_XW, 0.9, CAP_Z0 - 10))).Edges)
    P("  EbayCap W M2 x10: boss beside the pilot from the cap face down %.1f mm (tip at Z 40.3 needs >= 5.1)   %s" % (wl, "PASS" if wl >= 5.1 else "FAIL"))

    P("")
    P("[P] PIEZO FRAME + Q1 (TO-92 flat on the back)")
    qz = box(*Q1_ZONE)
    P("  Q1 zone x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f (%.0f mm3): sled inside %.2f mm3   %s"
      % (Q1_ZONE + (qz.Volume, vv(sled, qz), "PASS" if vv(sled, qz) < 0.01 else "FAIL")))
    bear = vv(sled, box(PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)) / 0.1
    P("  board back bears on the frame: %.1f mm2 (hole-end bar + bottom rail band); 2 x M2 clamp the hole end   %s" % (bear, "PASS" if bear > 40 else "FAIL"))
    pocket = box(PIEZO_PCB_X0 + 0.01, PIEZO_X1 + 0.5, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)
    P("  sled in front of the board: %.2f mm3   %s" % (vv(sled, pocket), "PASS" if vv(sled, pocket) < 0.01 else "FAIL"))
    pbay = pin_bay()
    P("  pin bay x %.1f..%.1f y %.1f..%.1f: sled inside %.2f mm3   %s" % (PIN_BAY + (vv(sled, pbay), "PASS" if vv(sled, pbay) < 0.01 else "FAIL")))

    P("")
    P("[X] HARNESS ROOM")
    jst = comp["JST_power"]; jb = jst.BoundBox
    col = clip_bore(box(jb.XMin, 25.0, jb.YMin, jb.YMax, jb.ZMin, jb.ZMax), r=R_MAX_MOVING)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp[k]) for k in comp if k not in ("JST_power", "Nano_ESP32")] for v in [vv(sh, col)] if v > 1e-2]
    P("  chimney: JST y %.1f..%.1f Z %.1f..%.1f, top x %.1f; column from the PCB to the bore clear of %s   %s"
      % (jb.YMin, jb.YMax, jb.ZMin, jb.ZMax, jb.XMax, "everything" if not hit else hit, "PASS" if not hit else "FAIL"))
    colm = box(NANO_XT, PANEL_X1, -RAIL_Y, RAIL_Y, NANO_Z0, NANO_Z1)
    cfree = colm.cut(sled)
    for k in comp:
        cfree = cfree.cut(comp[k])
    P("  open column over the ESP32 (x %.1f..%.1f, |y| < %.1f, Z %.1f..%.1f): %.0f mm3 free after S7V8F5 + cables; the pad rows"
      % (NANO_XT, PANEL_X1, RAIL_Y, NANO_Z0, NANO_Z1, vol(cfree)))
    rows_free = all(vv(sled, box(NANO_XF, PANEL_X1, sy * NANO_ROW_Y - 1.0, sy * NANO_ROW_Y + 1.0, NANO_Z0, NANO_Z1)) < 0.01 for sy in (-1, 1))
    P("    (|y| %.2f) have nothing printed over them up to the battery: wires go straight up off the pads   %s" % (NANO_ROW_Y, "PASS" if rows_free else "FAIL"))
    pts = [Vector(8.0, 12.6, -14.0), Vector(1.3, 12.6, -14.0), Vector(1.3, 5.0, -14.0)]
    pr = None
    for a, b in zip(pts[:-1], pts[1:]):
        c = Part.makeCylinder(1.0, (b - a).Length, a, b - a).fuse(Part.makeSphere(1.0, b))
        pr = c if pr is None else pr.fuse(c)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + list(comp.items()) for v in [vv(sh, pr)] if v > 1e-2]
    P("  piezo / Q1 lead exit: d2 probe pin bay (8.0, 12.6, -14) -> west under the N wall -> aft deck (1.3, 5.0): %s   %s"
      % ("clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    for nm, k in (("ADXL fwd -> BMP fwd", "Qwiic_ADXL_BMP"), ("BMP aft -> ESP32", "Qwiic_BMP_Nano")):
        P("  Qwiic %-20s lane %s; sled in it %.2f mm3   %s" % (nm, "x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f" % tuple(
            getattr(comp[k].BoundBox, a) for a in ("XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax")), raw[k], "PASS" if raw[k] < 0.01 else "FAIL"))

    P("")
    P("[T] BMP388 vs ESP32 (heat): BMP on the S wall's outside, %.1f mm from the ESP32's edge, sensor facing the bore" % (
      comp["BMP388"].distToShape(comp["Nano_ESP32"])[0]))

    P("")
    P("[B] BATTERY")
    bt = comp["Battery"]
    aft = box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0 - CL - 0.1, BATT_Z0 - CL)
    a_p = vv(comp["Piezo_Q1"], aft) / 0.1; a_s = vv(sled, aft) / 0.1
    P("  aft face (Z %.1f): -y end wall top %.1f mm2 + piezo PCB top edge %.1f mm2, both 0.4 below   %s" % (BATT_Z0, a_s, a_p, "PASS" if a_s > 5 else "FAIL"))
    fz = vv(sled, box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0, BATT_W / 2.0, BATT_Z0 + BATT_L + CL, BATT_Z0 + BATT_L + CL + 0.1)) / 0.1
    P("  fwd face (Z %.1f): stops off both walls %.1f mm2 at 0.4 (N stops at |y| %.1f: the JST is at y <= %.1f)   %s"
      % (BATT_Z0 + BATT_L, fz, BATT_STOP[0][1], JST_Y[1], "PASS" if fz > 4.0 else "FAIL"))
    sd = vv(sled, box(BATT_X0, BATT_X0 + BATT_T, BATT_W / 2.0 + CL, BATT_W / 2.0 + CL + 0.1, BATT_Z0, BATT_Z0 + BATT_L)) / 0.1
    sd2 = vv(sled, box(BATT_X0, BATT_X0 + BATT_T, -BATT_W / 2.0 - CL - 0.1, -BATT_W / 2.0 - CL, BATT_Z0, BATT_Z0 + BATT_L)) / 0.1
    P("  sides: guide walls at |y| %.1f (0.4 clear), N %.0f mm2 / S %.0f mm2 of guide face   %s" % (BAT_Y, sd, sd2, "PASS" if sd > 100 and sd2 > 100 else "FAIL"))
    P("  bottom: rests on the wall steps at x %.1f (0.4; 1 mm foam), outboard face -> ID %.1f at y 0, corners R %.2f; Kapton wrap"
      % (PANEL_X1, R_AF_I - BATT_X0 - BATT_T, rmax_mesh(cmesh["Battery"])))
    free = [d for d in (5.0, 10.0, 15.0) if vv(sled, bt.translated(Vector(d, 0, 0))) < 1e-3]
    P("  pulls straight out along +x for charging: %s mm tested clear   %s" % (free, "PASS" if len(free) == 3 else "FAIL"))

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
    P("  sled (ABS, solid-equiv) %8.1f mm3   %5.1f g   (v10 17.4 g -> %+.1f g; v11 14.1 g)" % (sled.Volume, m, m - 17.4))
    P("  fasteners: 2 x M2x6 (piezo), 1 x M2x10 (EbayCap W only); ADXL glued, BMP taped/glued, battery Kapton")
    dm = (m - 12.6) - 1.5 - 1.5 - 0.5
    dcg = -dm * (228.0 - 115.0) / (262.6 + dm)
    P("  CG (ESTIMATE vs the D9aft v10 rollup: 262.6 g, CG 228.0 from the tip, gate <= 226; e-bay at ~tip 115):")
    P("    sled %+.1f g, reed/microSD/card -3.5 g -> e-bay %+.1f g -> CG %+.1f mm -> ~%.1f: ~%.0f g EbayCap ballast to reach 226"
      % (m - 12.6, dm, dcg, 228.0 + dcg, (2.0 + dcg) / 0.6))
    P("    (+ the real solder / wire / heat shrink, never weighed).  WEIGH the built e-bay + line, re-run OpenRocket before flying.")

    P("")
    P("[V] STORAGE -- free volume inside R %.1f, deck floor to cap face, minus sled, parts and cable lanes" % R_MAX_MOVING)
    shell = cyl(R_MAX_MOVING, DECK_FLOOR, CAP_Z0)
    fr = shell.cut(sled)
    for s in comp.values():
        fr = fr.cut(s)
    tot = sum(s.Volume for s in fr.Solids)
    P("  v12 total free %.0f mm3" % tot)
    zones = [("column over the ESP32 (S7V8F5 in it)", box(NANO_XT, PANEL_X1, -RAIL_Y, RAIL_Y, NANO_Z0, NANO_Z1), "wires, resistors, slack"),
             ("aft deck inside the walls (C1 in it)", box(-19.5, PBOSS_X0, -RAIL_Y, RAIL_Y, DECK_FLOOR, NANO_Z0), "d10 can, resistors"),
             ("outside the N wall (ADXL side)", box(-19.5, 19.5, WALL_OUT, 19.5, DECK_FLOOR, CAP_Z0), "around the ADXL"),
             ("outside the S wall (BMP side)", box(-19.5, 19.5, -19.5, -WALL_OUT, DECK_FLOOR, CAP_Z0), "around the BMP"),
             ("behind the ESP32 (spine side)", box(SPINE_X1, NANO_X0, -RAIL_Y, RAIL_Y, NANO_Z0, NANO_Z1), "flat wire <= 3 mm"),
             ("fwd end round the chimney", box(NANO_XT, 19.5, -RAIL_Y, RAIL_Y, BATT_Z0 + BATT_L, CAP_Z0), "battery lead slack"),
             ("over the battery (bore side)", box(BATT_X0 + BATT_T, 19.5, -WALL_OUT, WALL_OUT, BATT_Z0, BATT_Z0 + BATT_L), "foam")]
    for nm, z, use in zones:
        P("    %-40s %6.0f mm3   (%s)" % (nm, vv(fr, z), use))
    P("  (v11: 46247 mm3 total; v10 as built 40941)")

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
    P("  v11: 6 regions, 41 mm2, reach 1.6;  v10: 31 regions, 389 mm2, reach 7.8;  v9 (spaghetti): 1230 mm2, reach 10.3")

    P("")
    P("[N] ASSEMBLY (all from +x, sled in hand)")
    P("  1 ESP32, parts up, USB-C + JST to the cap end: press it down between the rails (crush ribs = snug) onto the")
    P("    back ribs, aft end on the heels.  Its wires go straight up off the pads into the open column.")
    P("  2 C1 (+ resistors) into the aft deck through the piezo frame window; S7V8F5 flat on the ESP32's parts (Kapton).")
    P("  3 piezo (can out), 2 x M2x6 -- TO-92 in the frame window; leads out of the pin bay under the N wall into the deck.")
    P("  4 ADXL375: GLUE (CA / epoxy) its back flat on the N wall's outer face, plug forward, x -9..9, Z 2..28.")
    P("  5 BMP388: tape / glue its back on the S wall's outer face, parts out; Qwiic aft through the S aft window,")
    P("    fwd plug <- ADXL cable through the N fwd window, across the column, through the S fwd window.")
    P("  6 battery between the wall guides on 1 mm foam, Kapton wrap; plug its lead into the ESP32's JST (= ON).")
    P("  7 EbayCap: W M2x10 only (east hole taped).")
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
    doc.addObject("Part::Feature", "Sled").Shape = sled
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

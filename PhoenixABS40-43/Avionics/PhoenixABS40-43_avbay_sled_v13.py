# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v13  (soldered harness, v10 battery tray, cornered BMP + ADXL)

v13 = v12 re-laid (2026-10-20, user: "have the same battery compartment as previous designs" -> the v10-style
SIDE TRAY (answered); "have corners or something that can support the BMP and ADXL" -> corner pockets + glue
(answered); "Wires will be coming out the front of the ESP32, same side as the usb c port" -> off the parts face,
straight up into the open column).  Everything else as v11/v12: TO-92 flat on the piezo back, S7V8F5 / C1 /
inline resistors loose, Qwiic both BMP plugs + the ADXL "top" plug, ESP32 at the absolute bottom with its 24 mm
power JST at the USB-C end on +y, rails on the ESP32, ADXL glued by itself on printed sled, length kept.

LAYOUT (x = depth: -x = spine / bottom, +x = open face = the static + sound port side)
  * BATTERY TRAY on the SOUTH flank exactly as v10: pack 20 (x) x 8.5 (y) x 40.5 (Z) at y -15.5..-7.0,
    floor (y -7.0..-5.8) on its inboard side, side walls x +/-(10.5..11.7), open OUTBOARD (-y): it slides in
    from the side, a SIDEWAYS zip tie through the wall + floor-corner slots holds it (v10 tie).  Aft stops =
    3 webs from the deck floor (no bridged cap); fwd stops = lips off the floor and the +x wall; the battery
    lead leaves through a notch in the floor's fwd end into the column, to the ESP32's JST.
  * ADXL375 GLUED flat on the tray floor's inboard face (as v10), in a CORNER POCKET: a rail along its bottom
    edge, an aft stop and a fwd stop (split round the plug); open only along +x (it drops in from the face).
  * ESP32 at the bottom, shifted north (y -4.2..13.8): S rail = a thickening of the tray floor, N rail = a full
    north wall; crush ribs on both; back ribs + heels as v12.  Wires straight up off the parts face.
  * BMP388 on TOP, PCB back down on the tray's +x wall (x 11.7), parts up toward the bore; CORNERS on its S
    edge (rail + aft and fwd stops).  Its N half overhangs the column: nothing printed may stand there (the
    ESP32 goes in under it first) -> glue on the S half + Kapton.
  * Piezo / Q1 frame / C1 / chimney / EbayCap (east boss deleted) as v12.

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
REV = "v13"
RHO = 1.05e-3
R_AF_I = 20.0
R_MAX_MOVING = 19.5
SLED_RMAX = 19.39
CL = 0.40
WALL = 1.20
KNEE = 1.15
ZONE_Z1 = 48.0

CAP_Z0 = 45.4
MOUNT_XW, MOUNT_XE = -15.3, 10.1          # MOUNT_XE: the cap's east hole -- NO boss under it (v11..v13)
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

# PIEZO (as v11/v12)
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
FRAME_TOP = PIEZO_Z1
END_WALL_TOP = PIEZO_Z1
PIEZO_CLEAR = (2.0, PIEZO_Z1 + CL)        # nothing printed at x >= 2.0, y -8.4..11, below Z -4.2 (piezo goes in along +x)
Q1_T = 4.4
Q1_ZONE = (PIEZO_PCB_X0 - Q1_T, PIEZO_PCB_X0, FRAME_BAR_Y1, PIEZO_Y1, PIEZO_Z0 + 1.0, PIEZO_Z1 - 1.0)

# BATTERY TRAY (v10 numbers, south flank, open outboard)
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_Z0 = 0.1                             # v10 0.4: 0.3 lower so the pack's JST plug tops out 0.5 under the cap
CL_BATT = 0.5
BATT_WALL = 1.2
TRAY_FACE = BATT_Y1 + BATT_WALL           # -5.8 floor's inboard face (ADXL glue face)
TRAY_X = BATT_DX / 2.0 + CL_BATT + BATT_WALL               # 11.7 wall outer face (BMP seat)
TRAY_TOP = 43.8                           # walls / floor up to here (cap face 45.4)
AFT_WEBS_X = ((-11.7, -10.5), (-6.6, -5.4), (-0.6, 0.6), (5.4, 6.6))   # aft stops, deck floor -> Z 0.0 (+x one starts y <= -8.8)
FWD_LIP = 1.5                             # fwd stops: lips 1.5 deep off the floor and the +x wall
LEAD_NOTCH = (-7.0, -1.0, BATT_Z0 + BATT_DZ - 0.5)          # floor notch x0, x1, from Z: battery lead -> column
TIE_W, TIE_T, TIE_CL = 2.5, 1.0, 0.25     # mini zip tie (v10)
TIE_Z0 = 35.75                            # band Z 35.75..38.25 (above the ADXL's fwd stop)

# NANO ESP32 -- bottom of the stack, shifted north
NANO_W, NANO_L, NANO_PCB_T, NANO_T = 18.0, 45.0, 1.6, 5.0
NANO_X0 = -12.6
NANO_XF = NANO_X0 + NANO_PCB_T            # -11.0
NANO_XT = NANO_X0 + NANO_T                # -7.6
NANO_YC = 4.8                             # y -4.2 .. 13.8
NANO_Z0 = -0.3
NANO_Z1 = NANO_Z0 + NANO_L                # 44.7
NANO_ROW_Y = 15.24 / 2.0
NANO_PAD_R = 0.85
NANO_JOINT_H = 0.5
NANO_PADS_Z = [NANO_Z0 + NANO_L / 2.0 + (i - 7) * 2.54 for i in range(15)]
NANO_EDGE = 0.6
JST_W, JST_H = 6.0, 24.0
JST_Y = (NANO_YC + 3.0, NANO_YC + 3.0 + JST_W)              # 7.8 .. 13.8 (+y = left of the USB-C)
JST_ZL = 5.5                              # ASSUMED: the JST is at the very USB-C end (last 5.5 mm)
RIB_DY = (1.5, 5.5)                       # back ribs at NANO_YC +/- these
HEEL_X1 = NANO_XF
NY0, NY1 = NANO_YC - NANO_W / 2.0, NANO_YC + NANO_W / 2.0   # -4.2, 13.8
S_RAIL_Y = NY0 - CL                       # -4.6 S rail face (floor thickened from -5.8)
N_RAIL_Y = NY1 + CL                       # 14.2 N wall inner face
CRUSH_Z = (1.5, 11.0, 21.0, 31.0, 41.5)

# ADXL375 glued on the tray floor face, corner pocket
ADXL_W, ADXL_PCB_L, ADXL_L, ADXL_T, ADXL_PCB_T = 18.0, 26.0, 27.0, 5.0, 1.6
GLUE = 0.2
ADXL_Y0 = TRAY_FACE + GLUE                # -5.6 PCB back (parts toward +y)
ADXL_X = (-6.4, 11.4)
ADXL_Z0 = 7.0                             # floor fully behind it from Z ~6.8 (piezo clearance knee)
ADXL_PLUG_HW = 4.0
POCKET_H = 1.0                            # corner rails / stops stand 1.0 off the glue face (PCB 1.6)

# BMP388 on top, PCB back down on the tray +x wall, parts up
BMP_W, BMP_L, BMP_PCB_T, BMP_PARTS = 22.0, 40.0, 1.6, 2.4
BMP_X0 = TRAY_X + GLUE                    # 11.9 PCB back
BMP_Y = (-11.0, 11.0)
BMP_Z0 = -1.4                             # aft plug 0.45 over the piezo can
BMP_Z1 = BMP_Z0 + BMP_L                   # 38.6
QW_PLUG = (2.95, 4.25, 2.7)
QW_BEND = 1.5

# SMALL PARTS
C1_D, C1_L = 10.0, 14.0
C1_POS = (-12.2, -12.2 + C1_L, 3.5, DECK_FLOOR + 0.2 + C1_D / 2.0)          # aft deck, north of the tray webs
S7_BOX = (NANO_XT + CL, NANO_XT + CL + 3.5, 0.0, 11.0, 5.0, 22.0)

# D9aft
D9_DZ = 279.2
D9_R_ID, D9_R_OD = 20.0, 21.5
D9_CREST = 19.65
D9_BAND_Z = 60.8 - 12.5
D9_SEAT_Z, D9_SEAT_RI, D9_SEAT_T = SEAT_Z, 15.5, 2.0
D9_SPIGOT_RI = 18.5
D9_PORTS = (("static", 1.5, 30.0, 0.0), ("sound", 3.0, PIEZO_ZC, 0.0))
D9V10_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v10_%s.step" % k)) for k in ("EbayCap", "FwdTube"))
DRIVER_D = 3.0

ASSUMED = [
    "JST-PH on the ESP32 sits at the very USB-C end (last 5.5 mm of the board) -- the BMP's fwd end is 0.6 from it",
    "Q1 TO-92 position on the piezo back: anywhere in the old joint footprint (y -3.5..11, Z -18.6..-5.6), 4.4 deep",
    "C1 470 uF 16 V: d10 x 12.5 body + 1.5 bent leads (d8 x 11.5 is also common -> more room)",
    "S7V8F5 17 x 11 x 3 + 0.5 joints, lying on the ESP32's parts (Kapton between)",
    "ESP32 PCB 18.0 wide: the crush ribs sit at exactly 18.0 -- file them if it is too tight",
    "Qwiic plug 2.95 deep x 4.25 long x 5.4 wide; cables bend 1.5 past the plug",
    "ESP32 USB-C <= 0.3 past the PCB end; parts 3.4 tall, 0.6 edge bands free; back joints 0.5 (wires leave the parts face, user)",
    "ADXL375 Qwiic plug centred on its 'top' (short) end, 8 wide; PCB edges free for 1 mm (pocket rails)",
    "BMP388 PCB 1.6, parts 2.4 incl. plugs; plugs centred on both short ends; S edge band free for the corner rail",
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
    s = box(NANO_X0, NANO_XF, NY0, NY1, NANO_Z0, NANO_Z1)
    e = NANO_W / 2.0 - NANO_EDGE
    return as_solid(s.fuse(box(NANO_XF, NANO_XT, NANO_YC - e, NANO_YC + e, NANO_Z0, NANO_Z1)).removeSplitter())

def env_nano_joints():
    s = None
    for sy in (-1, 1):
        for z in NANO_PADS_Z:
            j = cyl_x(NANO_PAD_R, NANO_X0 - NANO_JOINT_H, NANO_X0, NANO_YC + sy * NANO_ROW_Y, z)
            s = j if s is None else s.fuse(j)
    return as_solid(s.removeSplitter())

def env_jst():
    return box(NANO_XF, NANO_XF + JST_H, JST_Y[0], JST_Y[1], NANO_Z1 - JST_ZL, NANO_Z1)

def adxl_xc():
    return (ADXL_X[0] + ADXL_X[1]) / 2.0

def env_adxl():
    y1 = ADXL_Y0 + ADXL_T
    s = box(ADXL_X[0], ADXL_X[1], ADXL_Y0, y1, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    s = s.fuse(box(adxl_xc() - ADXL_PLUG_HW, adxl_xc() + ADXL_PLUG_HW, ADXL_Y0, y1, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 + ADXL_L))
    return as_solid(s.removeSplitter())

def env_bmp():
    """PCB back down on the tray +x wall (x 11.9), parts + both Qwiic plugs up toward the bore"""
    xp = BMP_X0 + BMP_PCB_T
    s = box(BMP_X0, xp + BMP_PARTS, BMP_Y[0], BMP_Y[1], BMP_Z0, BMP_Z1)
    d, ln, hw = QW_PLUG
    s = s.fuse(box(xp, xp + d, -hw, hw, BMP_Z0 - ln, BMP_Z0))
    s = s.fuse(box(xp, xp + d, -hw, hw, BMP_Z1, BMP_Z1 + ln))
    return as_solid(s.removeSplitter())

def env_qwiic_adxl_bmp():
    """ADXL fwd plug -> up the tray face -> across over the ESP32's fwd half -> beside the BMP's fwd end -> U-turn
    into the BMP fwd plug"""
    d, ln, hw = QW_PLUG
    xp = BMP_X0 + BMP_PCB_T
    za = ADXL_Z0 + ADXL_L                                   # 34.0 plug end
    zc = BMP_Z1 + 0.05                                      # 38.65
    yl = TRAY_FACE + TIE_T + TIE_CL + 0.15                 # off the floor face: the zip tie's inboard leg runs there
    s = box(adxl_xc() - hw, adxl_xc() + hw, yl, ADXL_Y0 + ADXL_T, za, zc + 1.0)
    s = s.fuse(box(adxl_xc() - hw, BMP_X0 - 0.4, yl, hw, zc - 0.65, zc + 1.0))
    s = s.fuse(box(BMP_X0 - 0.4, xp - 0.05, -hw, hw, zc, BMP_Z1 + ln + QW_BEND))
    s = s.fuse(box(xp - 0.05, xp + d, -hw, hw, BMP_Z1 + ln, BMP_Z1 + ln + QW_BEND))
    return as_solid(s.removeSplitter())

def env_qwiic_bmp_nano():
    """BMP aft plug -> bends sideways (+y) over the piezo can -> along x under the BMP / over the piezo board ->
    up onto the ESP32's aft end"""
    d, ln, hw = QW_PLUG
    xp = BMP_X0 + BMP_PCB_T
    za = BMP_Z0 - ln                                        # -5.65 plug end
    s = box(xp, xp + d, hw, hw + 2.0 * hw, za, BMP_Z0 - CL)
    s = s.fuse(box(NANO_XT, xp + d, hw, hw + 2.0 * hw, PIEZO_Z1 + CL, BMP_Z0 - CL))
    s = s.fuse(box(NANO_XT, NANO_XT + 2.5, hw, hw + 2.0 * hw, PIEZO_Z1 + CL, NANO_Z0 + 2.0))
    return as_solid(s.removeSplitter())

def env_batt():
    return box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0, BATT_Z0 + BATT_DZ)

def env_batt_jst():
    """battery lead's JST-PH plug at the pack's fwd end, -x corner (v10)"""
    yc = BATT_Y1 - BATT_DY / 2.0
    return box(-BATT_DX / 2.0, -BATT_DX / 2.0 + 6.0, yc - 2.25, yc + 2.25, BATT_Z0 + BATT_DZ, BATT_Z0 + BATT_DZ + 4.3)

def env_tie():
    """v10 SIDEWAYS tie: round the pack's cross-section, through the wall + floor-corner slots, across the floor face"""
    hx, yo, yi = BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1
    z0, z1 = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL
    t, tc = TIE_T, TIE_T + TIE_CL
    s = box(-hx, hx, yo - t, yo, z0, z1)
    for sx in (-1, 1):
        s = s.fuse(cyl(t, z0, z1, sx * hx, yo))
        xa, xb = sorted((sx * hx, sx * (hx + tc)))
        s = s.fuse(box(xa, xb, yo, TRAY_FACE + tc, z0, z1))
    s = s.fuse(box(-hx - tc, hx + tc, TRAY_FACE, TRAY_FACE + tc, z0, z1))
    s = s.cut(box(-hx, hx, yo, yi, z0 - 1, z1 + 1))
    return as_solid(s.removeSplitter())

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
    ("Battery_JST",  env_batt_jst),
    ("ZipTie",       env_tie),
]
RIGID = [n for n, _ in COMPONENTS]

# ================================================================ the sled
def build_sled(log):
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)
    by_out = BATT_Y1 - BATT_DY                                                 # -15.5 tray mouth
    piezo_cut = knee_cut("x", PIEZO_CLEAR[0], PIEZO_CLEAR[1], +1)              # 1:1.15 over the piezo / Q1 / bosses

    parts.append(clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, SEAT_Z, ZONE_Z1 - 0.6)))     # spine + key
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, DECK_FLOOR)))                                    # floor disc

    # ---- BATTERY TRAY (v10, south): floor (= ADXL panel), side walls, aft webs, fwd lips, lead notch, tie slots
    fl = box(-19.0, TRAY_X, BATT_Y1, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)
    fl = fl.cut(piezo_cut)
    parts.append(cap(fl))
    parts.append(cap(box(-TRAY_X, -TRAY_X + BATT_WALL, by_out, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)))   # -x wall
    xw = box(TRAY_X - BATT_WALL, TRAY_X, by_out, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)                  # +x wall = BMP seat
    xw = xw.cut(box(PIEZO_CLEAR[0], 30, END_WALL_Y[1], 30, -60, PIEZO_CLEAR[1]))
    parts.append(cap(xw))
    for x0, x1 in AFT_WEBS_X[1:]:                                                          # aft stops (the -x wall is the 1st)
        y1 = BATT_Y1 if x0 < PIEZO_CLEAR[0] else END_WALL_Y[0] + 0.8
        parts.append(cap(box(x0, x1, by_out, y1, DECK_FLOOR - 0.01, BATT_Z0 - CL_BATT)))
    c1z = BATT_Z0 + BATT_DZ + CL_BATT                                                      # 41.4
    parts.append(cap(box(LEAD_NOTCH[1] + 0.4, BATT_DX / 2.0 + CL_BATT, BATT_Y1 - FWD_LIP, BATT_Y1 + 0.01, c1z, c1z + 1.5)))   # floor lip
    drill.append(box(LEAD_NOTCH[0], LEAD_NOTCH[1], BATT_Y1 - 1.0, S_RAIL_Y + 0.01, LEAD_NOTCH[2], 60.0))
    tz0, tz1 = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL
    for sx in (-1, 1):
        xa, xb = sorted((sx * (BATT_DX / 2.0 - 0.01), sx * TRAY_X))                    # through the wall only (BMP rail outside)
        sl = prism("y", [(TRAY_FACE + 0.01, tz0), (TRAY_FACE + 0.01, tz1), (by_out - 1.0, tz1 + KNEE * (TRAY_FACE - by_out + 1.0)),
                         (by_out - 1.0, tz0)], xa, xb)
        drill.append(sl.common(box(xa, xb, by_out - 1.0, TRAY_FACE + 0.01, tz0, TRAY_TOP + 1.0)))   # top climbs out of the wall: no ceiling
    # tie's inboard leg crosses the floor face: the S rail is cut there
    drill.append(box(-14.0, -BATT_DX / 2.0 + 0.01, TRAY_FACE - 0.01, S_RAIL_Y + 0.05, tz0, tz1))

    # ---- ESP32 rails: S = the floor thickened to y -4.6, N = a full north wall at y 14.2; crush ribs on both
    parts.append(cap(box(-19.0, NANO_XT, TRAY_FACE - 0.01, S_RAIL_Y, DECK_FLOOR - 0.01, CAP_Z0)))
    nw = box(-19.0, 19.5, N_RAIL_Y, N_RAIL_Y + WALL, DECK_FLOOR - 0.01, CAP_Z0)
    nw = nw.cut(knee_cut("x", 6.4, PIEZO_Z1 + CL, +1))                                    # piezo pin bay under it
    parts.append(cap(nw))
    parts.append(cap(box(-16.6, NANO_XT, NY1 - 2.8, N_RAIL_Y + 0.01, DECK_FLOOR - 0.01, NANO_Z0 - 0.4)))   # aft-deck web: N wall -> spine
    for zc in CRUSH_Z:
        if tz0 - 0.6 < zc < tz1 + 0.6:
            continue
        parts.append(cap(box(NANO_X0 - 0.5, NANO_XF, S_RAIL_Y - 0.01, NY0, zc - 0.5, zc + 0.5)))
        parts.append(cap(box(NANO_X0 - 0.5, NANO_XF, NY1, N_RAIL_Y + 0.01, zc - 0.5, zc + 0.5)))
    for dy in (-1, 1):
        y0, y1 = sorted((NANO_YC + dy * RIB_DY[0], NANO_YC + dy * RIB_DY[1]))
        rib = box(SPINE_X1 - 0.1, NANO_X0, y0, y1, -12.0, NANO_Z1)
        rib = rib.fuse(box(NANO_X0 - 0.01, HEEL_X1, y0, y1, -12.0, NANO_Z0 - 0.1))
        rib = corbel(rib, "x", SPINE_X1, NANO_Z0 - 1.3, HEEL_X1)
        parts.append(cap(rib))

    # ---- ADXL corner pocket on the floor face: bottom-edge rail, aft stop, fwd stop split round the plug
    yp0, yp1 = TRAY_FACE - 0.01, TRAY_FACE + POCKET_H
    za, zf = ADXL_Z0 - CL, ADXL_Z0 + ADXL_PCB_L + CL
    parts.append(cap(box(NANO_XT - 0.4, ADXL_X[0] - CL, yp0, yp1, za - 0.6, zf + 0.6)))
    parts.append(cap(box(NANO_XT - 0.4, 9.0, yp0, yp1, za - 0.6, za)))
    hw = ADXL_PLUG_HW + CL
    parts.append(cap(box(NANO_XT - 0.4, adxl_xc() - hw, yp0, yp1, zf, zf + 0.6)))

    # ---- BMP corners on the +x wall: S-edge rail + aft / fwd stops (its N half overhangs the column)
    ys0, ys1 = BMP_Y[0] - CL - 1.0, BMP_Y[0] - CL                                         # -12.4 .. -11.4
    xr0, xr1 = TRAY_X - 0.01, BMP_X0 + BMP_PCB_T - 0.2
    rail = box(xr0, xr1, ys0, ys1, BMP_Z0 - CL - 0.6, BMP_Z1 + CL + 0.6)
    rail = rail.fuse(box(xr0, xr1, ys0, -8.8, BMP_Z0 - CL - 0.6, BMP_Z0 - CL))
    rail = rail.fuse(box(xr0, xr1, ys0, -8.8, BMP_Z1 + CL, BMP_Z1 + CL + 0.6))
    parts.append(cap(rail))

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
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (soldered harness, v10 battery tray, cornered BMP + ADXL)" % REV)
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
    P("[F] PRESS-IN -- every part along its path in ASSEMBLY ORDER (sled in hand, out of the tube) until it is clear")
    P("    of the bore; it must not touch the sled or any part already in (touching = 0 mm3 allowed: crush ribs).")
    P("    The harness goes in from the open face (+x); the battery slides into its tray from the side (-y), as v10.")
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
                bb = s2.BoundBox
                rmin = min(math.hypot(x, y) for x in (bb.XMin, bb.XMax, (bb.XMin + bb.XMax) / 2.0) for y in (bb.YMin, bb.YMax, (bb.YMin + bb.YMax) / 2.0))
                if L is None and rmin > SLED_RMAX + 0.6:
                    break
        return hits
    X = Vector(1, 0, 0)
    LOAD = [("Nano_ESP32", ["Nano_ESP32", "Nano_joints", "JST_power"], [(X, None)]),
            ("C1_470uF",   ["C1_470uF"], [(Vector(0, 0, 1), 3.2), (X, None)]),
            ("S7V8F5",     ["S7V8F5"], [(X, None)]),
            ("Piezo_Q1",   ["Piezo_Q1"], [(X, None)]),
            ("ADXL375",    ["ADXL375"], [(X, None)]),
            ("BMP388",     ["BMP388"], [(X, None)]),
            ("Battery",    ["Battery", "Battery_JST"], [(Vector(0, -1, 0), None)])]
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
    P("  Qwiic cables are plugged after the boards are in; zip tie threaded round the pack last; battery JST plugged LAST.")
    for k in ("Qwiic_ADXL_BMP", "Qwiic_BMP_Nano", "ZipTie"):
        hit = [(n2, round(vv(comp[k], comp[n2]), 2)) for n2 in comp if n2 != k and vv(comp[k], comp[n2]) > 1e-2]
        P("  %-15s laid in after the boards: overlaps %s   %s" % (k, hit or "nothing", "PASS" if not hit else "FAIL"))

    P("")
    P("[R] ESP32 RAILS")
    for nm, yf, sg in (("S (tray floor, thickened)", S_RAIL_Y, -1), ("N (north wall)", N_RAIL_Y, 1)):
        guide = box(NANO_X0, NANO_XT, *(sorted((yf, yf + sg * 0.05)) + [NANO_Z0, NANO_Z1]))
        yc = NY0 if sg < 0 else NY1
        cont = box(NANO_X0, NANO_XF, *(sorted((yc, yc + sg * 0.05)) + [NANO_Z0, NANO_Z1]))
        gl = vol(sled.common(guide)) / (0.05 * (NANO_XT - NANO_X0))
        ca = vv(sled, cont) / 0.05
        P("  %-26s rail face over ~%.1f of %.1f mm (0.4 clear); crush ribs on the PCB edge %.1f mm2   %s"
          % (nm, gl, NANO_L, ca, "PASS" if gl > 30 and ca > 4.0 else "FAIL"))
    hb = vv(sled, box(NANO_X0, NANO_XF, NY0, NY1, NANO_Z0 - 0.5, NANO_Z0 - 0.1)) / 0.4
    bk = vv(sled, box(NANO_X0 - 0.1, NANO_X0, NY0, NY1, NANO_Z0, NANO_Z1)) / 0.1
    P("  aft end on the rib heels %.1f mm2 (0.1 gap); back on 2 full-length ribs %.0f mm2; fwd end 0.7 under the cap face   %s"
      % (hb, bk, "PASS" if hb > 4 and bk > 200 else "FAIL"))
    jg = comp["Nano_joints"].distToShape(sled)[0]
    P("  back-face joints -> sled %.2f mm   %s" % (jg, "PASS" if jg >= 0.25 else "FAIL"))
    P("  wires leave the PARTS face (user) -> straight up into the column; see [X] for the pad rows")

    P("")
    P("[A] SENSOR POCKETS (printed sled only behind each board)")
    pts = [(x, z) for x in [ADXL_X[0] + 1.0 + 2.0 * i for i in range(9)] for z in [ADXL_Z0 + 1.0 + 3.0 * j for j in range(9)]]
    back = sum(1 for x, z in pts if sled.common(Part.makeLine(Vector(x, TRAY_FACE + 0.01, z), Vector(x, TRAY_FACE - 1.0, z))).Edges)
    P("  ADXL375 glue face (tray floor, y %.1f): %d / %d grid points with floor right behind the PCB   %s" % (TRAY_FACE, back, len(pts), "PASS" if back >= 0.95 * len(pts) else "FAIL"))
    def touch(sh, d):
        return vv(sled, sh.translated(d))
    pcb = box(ADXL_X[0], ADXL_X[1], ADXL_Y0, ADXL_Y0 + ADXL_PCB_T, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    lr = [round(touch(pcb, v), 1) for v in (Vector(-1.0, 0, 0), Vector(0, 0, -1.0), Vector(0, 0, 1.0))]
    P("  ADXL pocket: PCB moved 1 mm toward the bottom rail / aft stop / fwd stop hits %s mm3 (all > 0 = held on 3 sides; +x open)   %s"
      % (lr, "PASS" if min(lr) > 0 else "FAIL"))
    P("  ADXL pose: long axis = rocket Z, PCB back on the floor face, parts toward +y (= v10's board normal), plug FWD (v10 aft)")
    pts = [(y, z) for y in [BMP_Y[0] + 0.5 + 1.0 * i for i in range(5)] for z in [BMP_Z0 + 1.0 + 4.0 * j for j in range(10)]]
    back = sum(1 for y, z in pts if sled.common(Part.makeLine(Vector(TRAY_X + 0.19, y, z), Vector(TRAY_X - 1.0, y, z))).Edges)
    P("  BMP388 seat: %d / %d grid points of its S half (y %.1f..%.1f) on the tray's +x wall (the tie slot takes a band);"
      % (back, len(pts), BMP_Y[0], TRAY_FACE))
    P("    N half overhangs the column (nothing printed may stand over the ESP32)   %s" % ("PASS" if back >= 0.8 * len(pts) else "FAIL"))
    bpcb = box(BMP_X0, BMP_X0 + BMP_PCB_T, BMP_Y[0], BMP_Y[1], BMP_Z0, BMP_Z1)
    lr = [round(touch(bpcb, v), 1) for v in (Vector(0, -1.0, 0), Vector(0, 0, -1.0), Vector(0, 0, 1.0))]
    P("  BMP corners: PCB moved 1 mm toward the S rail / aft stop / fwd stop hits %s mm3   %s" % (lr, "PASS" if min(lr) > 0 else "FAIL"))

    P("")
    P("[I] FIT -- RAW = the as-drawn sled inside each part's keep-out BEFORE the trim; post-cut must be 0.")
    for n in comp:
        P("  %-15s RAW %7.1f mm3   post-cut %.1f   %s" % (n, raw.get(n, 0.0), vv(sled, comp[n]), "" if raw.get(n, 0.0) < 0.5 else "(sled member trimmed by the part -- review)"))
    cn = list(comp.keys()); cc = 0
    designed = {("Nano_ESP32", "JST_power"), ("Battery", "Battery_JST")}
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            v = vv(comp[cn[i]], comp[cn[j]])
            if (cn[i], cn[j]) in designed:
                P("    designed: %s on %s" % (cn[j], cn[i])); continue
            if v > 0.05:
                cc += 1; P("    CLASH %s <-> %s  %.2f mm3   FAIL" % (cn[i], cn[j], v))
    P("  part-vs-part clashes: %d   %s" % (cc, "PASS" if cc == 0 else "FAIL"))
    P("  gaps between neighbours (want >= %.1f):" % (CL - 0.05))
    for a, b in (("Nano_ESP32", "S7V8F5"), ("Nano_ESP32", "ADXL375"), ("ADXL375", "BMP388"), ("ADXL375", "Battery"),
                 ("JST_power", "BMP388"), ("JST_power", "Qwiic_ADXL_BMP"), ("Battery", "Piezo_Q1"), ("BMP388", "Piezo_Q1"),
                 ("C1_470uF", "Qwiic_BMP_Nano"), ("Piezo_Q1", "Qwiic_BMP_Nano"), ("ZipTie", "Nano_ESP32"), ("ZipTie", "ADXL375"),
                 ("S7V8F5", "ADXL375"), ("Battery_JST", "Nano_ESP32")):
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
    colm = box(NANO_XT, BMP_X0, ADXL_Y0 + ADXL_T, N_RAIL_Y, NANO_Z0, NANO_Z1)
    cfree = colm.cut(sled)
    for k in comp:
        cfree = cfree.cut(comp[k])
    P("  open column over the ESP32 (x %.1f..%.1f, y %.1f..%.1f): %.0f mm3 free after S7V8F5 + cables"
      % (NANO_XT, BMP_X0, ADXL_Y0 + ADXL_T, N_RAIL_Y, vol(cfree)))
    for sg, nm in ((1, "N"), (-1, "S")):
        yr = NANO_YC + sg * NANO_ROW_Y
        over = [(k, round(sh.BoundBox.XMin - NANO_XF, 1)) for k, sh in [("Sled", sled)] + list(comp.items()) if k not in ("Nano_ESP32", "Nano_joints")
                and vv(sh, box(NANO_XF, 19.0, yr - 0.9, yr + 0.9, NANO_Z0 + 3.5, NANO_Z1 - 4.0)) > 0.01]
        P("  %s pad row (y %.2f), above the PCB top: %s" % (nm, yr, "nothing up to the bore" if not over else
          ", ".join("%s from %.1f mm" % o for o in over) + (" -> wires bend north under it" if any(o[1] < 6 for o in over) else "")))
    pts = [Vector(8.0, 12.6, -8.0), Vector(1.0, 12.6, -8.0), Vector(1.0, 6.0, -8.0)]
    pr = None
    for a, b in zip(pts[:-1], pts[1:]):
        c = Part.makeCylinder(1.0, (b - a).Length, a, b - a).fuse(Part.makeSphere(1.0, b))
        pr = c if pr is None else pr.fuse(c)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + list(comp.items()) for v in [vv(sh, pr)] if v > 1e-2]
    P("  piezo / Q1 lead exit: d2 probe pin bay (8.0, 12.6, -8) -> west -> aft deck (1.0, 6.0): %s   %s"
      % ("clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    nb = box(LEAD_NOTCH[0], LEAD_NOTCH[1], BATT_Y1 - 0.5, S_RAIL_Y, LEAD_NOTCH[2] + 0.5, CAP_Z0 - 0.1)
    P("  battery lead notch through the floor (x %.1f..%.1f, Z %.1f..cap): sled in it %.2f mm3   %s"
      % (LEAD_NOTCH[0], LEAD_NOTCH[1], LEAD_NOTCH[2], vv(sled, nb), "PASS" if vv(sled, nb) < 0.01 else "FAIL"))
    for nm, k in (("ADXL fwd -> BMP fwd", "Qwiic_ADXL_BMP"), ("BMP aft -> ESP32", "Qwiic_BMP_Nano")):
        P("  Qwiic %-20s lane %s; sled in it %.2f mm3   %s" % (nm, "x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f" % tuple(
            getattr(comp[k].BoundBox, a) for a in ("XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax")), raw[k], "PASS" if raw[k] < 0.01 else "FAIL"))

    P("")
    P("[T] BMP388 vs ESP32 (heat): BMP on top, %.1f mm above the ESP32's parts, sensor facing the bore" % (
      comp["BMP388"].distToShape(comp["Nano_ESP32"])[0]))

    P("")
    P("[B] BATTERY TRAY (v10 style)")
    bt = comp["Battery"]
    free = [d for d in (2.0, 5.0, 9.0, 12.0) if vv(sled, bt.translated(Vector(0, -d, 0))) < 1e-3]
    P("  pack slides OUTBOARD (-y) free of the sled: %s mm tested clear   %s" % (free, "PASS" if len(free) == 4 else "FAIL"))
    hx = BATT_DX / 2.0 + CL_BATT
    def mat(pt, d, L):
        return sum(e.Length for e in sled.common(Part.makeLine(pt, pt + d * L)).Edges)
    for nm, pt, d in (("W wall", Vector(-hx, -11.0, 15.0), Vector(-1, 0, 0)), ("E wall", Vector(hx, -11.0, 15.0), Vector(1, 0, 0)),
                      ("floor", Vector(-2.0, BATT_Y1, 15.0), Vector(0, 1, 0))):
        t = mat(pt, d, 4.0)
        P("  %-7s %.2f mm thick at (x %.1f, y %.1f, Z %.1f)   %s" % (nm, t, pt.x, pt.y, pt.z, "PASS" if t >= 1.15 else "FAIL"))
    aft = box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0 - CL_BATT - 0.1, BATT_Z0 - CL_BATT)
    fwd = box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0 + BATT_DZ + CL_BATT, BATT_Z0 + BATT_DZ + CL_BATT + 0.1)
    P("  aft face on %.1f mm2 of web tops (deck floor -> Z %.1f, no bridged cap); fwd face under %.1f mm2 of the floor lip (0.5 gaps)   %s"
      % (vv(sled, aft) / 0.1, BATT_Z0 - CL_BATT, vv(sled, fwd) / 0.1, "PASS" if vv(sled, aft) / 0.1 > 20 and vv(sled, fwd) / 0.1 > 10 else "FAIL"))
    P("  SIDEWAYS zip tie (%.1f x %.1f) at Z %.2f..%.2f: round the pack, through the wall + floor-corner slots, across the"
      % (TIE_W, TIE_T, TIE_Z0, TIE_Z0 + TIE_W))
    P("    floor face above the ADXL's fwd stop (S rail cut there); Rmax %.2f on the pack corners; ESP32 edge %.2f mm away"
      % (rmax_mesh(cmesh["ZipTie"]), comp["ZipTie"].distToShape(comp["Nano_ESP32"])[0]))
    P("  outboard face -> ID %.1f at x 0 (1 mm foam, the bore backs it); JST lead leaves the fwd -x corner -> floor notch -> column"
      % (R_AF_I - (BATT_DY - BATT_Y1)))

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
    lift = max(rs, max(rmax_mesh(cmesh[n]) for n in comp if n != "ZipTie"))
    rt = rmax_mesh(cmesh["ZipTie"])
    P("  zip tie band on the pack corners: R %.2f -> %.2f to the crests (soft band, cinched -- as v10)   %s" % (rt, D9_CREST - rt, "PASS" if D9_CREST - rt >= 0.15 else "WARN"))
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
    P("  sled (ABS, solid-equiv) %8.1f mm3   %5.1f g   (v10 17.4 g -> %+.1f g; v12 13.3 g)" % (sled.Volume, m, m - 17.4))
    P("  fasteners: 2 x M2x6 (piezo), 1 x M2x10 (EbayCap W only), 1 mini zip tie (battery); ADXL glued in its pocket, BMP glued on its corners")
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
    P("  v13 total free %.0f mm3" % tot)
    zones = [("column over the ESP32 (S7V8F5 in it)", box(NANO_XT, BMP_X0, ADXL_Y0 + ADXL_T, N_RAIL_Y, NANO_Z0, NANO_Z1), "wires, resistors, slack"),
             ("aft deck (C1 in it)", box(-19.5, PBOSS_X0, TRAY_FACE, N_RAIL_Y, DECK_FLOOR, NANO_Z0), "d10 can, resistors"),
             ("aft deck under the tray (between the webs)", box(-19.5, 19.5, -19.5, BATT_Y1, DECK_FLOOR, BATT_Z0 - CL_BATT), "flat parts"),
             ("behind the ESP32 (spine side)", box(SPINE_X1, NANO_X0, NY0, NY1, NANO_Z0, NANO_Z1), "flat wire <= 3 mm"),
             ("fwd end round the chimney", box(NANO_XT, 19.5, TRAY_FACE, N_RAIL_Y, BMP_Z1, CAP_Z0), "battery lead / Qwiic slack"),
             ("over the BMP (bore side)", box(BMP_X0 + BMP_PCB_T + BMP_PARTS, 19.5, -19.5, 19.5, BMP_Z0, BMP_Z1), "thin")]
    for nm, z, use in zones:
        P("    %-40s %6.0f mm3   (%s)" % (nm, vv(fr, z), use))
    P("  (v12 46121 mm3, v11 46247, v10 as built 40941)")

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
    P("  v12: 4 regions, 26 mm2, reach 1.4;  v10: 31 regions, 389 mm2, reach 7.8;  v9 (spaghetti): 1230 mm2, reach 10.3")

    P("")
    P("[N] ASSEMBLY (sled in hand)")
    P("  1 ESP32, parts up, USB-C + JST to the cap end: press it down between the rails (crush ribs = snug) onto the back")
    P("    ribs, aft end on the heels.  Its wires go straight up off the parts face into the column.")
    P("  2 C1 (+ resistors) into the aft deck through the piezo frame window; S7V8F5 flat on the ESP32's parts (Kapton).")
    P("  3 piezo (can out), 2 x M2x6 -- TO-92 in the frame window; its leads go west from the pin bay into the deck.")
    P("  4 ADXL375: GLUE (CA / epoxy) its back flat on the tray floor's inboard face inside its corner pocket, plug fwd.")
    P("  5 BMP388: PCB back down on the tray's +x wall, S edge into its corner rail; glue that half; Kapton over the rest.")
    P("  6 Qwiic: ADXL fwd -> BMP fwd plug; BMP aft plug -> along over the piezo to the ESP32.")
    P("  7 battery: slide it into the tray from the side (-y), 1 mm foam outboard, sideways mini zip tie; lead through the")
    P("    floor notch to the ESP32's JST -- plug it in LAST (= ON).")
    P("  8 EbayCap: W M2x10 only (east hole taped).")
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

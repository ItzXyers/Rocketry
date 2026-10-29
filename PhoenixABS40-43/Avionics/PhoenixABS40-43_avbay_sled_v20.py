# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v20  (v19 + 16 mm wire-slack chamber under a screw-in ring)

v20 = v19 with the e-bay 16 mm longer at the TOP (2026-10-26).  User: "The cables don't fit" (soldered Dupont jumpers,
"too much cable"), "I kinda need a lot more space", picked +15 mm; then "the extension of the fwd tube must be additive
to the current design, since the rocket is fully assembled".  -> D9aft v12: a 16 mm EXTENSION RING screws into the
FwdTube mouth (the nose's male thread) and carries the FwdTube's female thread for the nose.  FwdTube / AftTube / fin
can / nose / EbayCap are the as-built parts, unchanged.  16, not 15: the ring's spigot fills the old thread band
(Z 51.3..60.8) and the cap must sit above the tube mouth (Z 60.8) -> cap face 45.4 + 16 = 61.4.
  * Every part keeps its v19 Z; the seat, ports and piezo / sound-port line-up are unchanged (FwdTube frame unchanged).
  * Slot walls, back plate, W boss stop at the old top (Z 45.4).  Above: an open SLACK CHAMBER Z 45.4..61.4.
  * In the ring's spigot band (Z 51.3..61.4) everything stays inside R 17.55 (spigot bore 17.95 - 0.4): the ring screws
    down OVER the sled, so the spine becomes a narrow POST (x -17.5..-13.1, y +-3) carrying the W M2 boss up to the cap.
    The v19 spine key into the cap is gone (it would be outside the bore).
  * LOCK: ring slot (+-15 deg) -> cap key -> W M2 -> post -> sled key -> tube groove: the ring can't back out.
  * SLED KEY at 180 deg (sled -x) in the FwdTube's existing cap-key groove (station 16.4..0 -> Z 44.4..60.8), Z 45.05..50.8,
    below the spigot: the sled is clocked by the TUBE now (the cap's key rides the ring, whose print clocking is uncertain).
  * Assembly: sled in -> ring screwed on (hand tight against the tube mouth) -> EbayCap (W M2x10) -> nose.

--- v19 notes:
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v19  (v18 + tray-floor doorways)

v19 = v18 with one change (2026-10-21, user picked "A: tray-floor doorways" of two offered cuts):
  three pointed-arch (1:1.15) windows through the battery tray floor BELOW the pack (peaks Z -3.0, 0.5 under the web
  tops), one west of the tray's -x wall and one in each of the two west web cells.  They join the aft deck (C1) to
  the cells under the tray so leads can cross.  Webs, pack seat, ADXL pocket, ESP32 slot untouched.
  (Offered and NOT taken: an arch through the ESP32 back plate + ribs below the board.)

--- v18 notes:
v18 = v17 with one change (2026-10-21, user): "Remove the heel without making any other changes" -> the two heels
  under the ESP32's aft end (on the back ribs) are gone; nothing else moved.

--- v17 notes:
v17 = v16 with one change (2026-10-21, user):
  * "Make the esp32 rails go all the way down" -> answered "E rail to the floor": the slot's E wall now runs down to
    the deck floor like the W one, as a column x 6.8..9.6, y 13.9..16.5 (bore-clipped).  It stands north of the piezo
    pins (pin envelope ends at y 13.5 + 0.4), so only that part of the wall can go down: y 9..11.4 is the piezo PCB.
    The pin bay keeps v13 size except that column (x 9.6..12 stays open to y 18); the pin leads still go west under
    the buttress arch at y 12.2.

--- v16 notes:
v16 = v15 with two changes (2026-10-20, user):
  * "yes, there is some solder bulging at the edges of the esp" -> every pad passes every lip above it while the board
    slides in, so the slot is TIGHT only in an aft-end CUP (Z -0.5..3.0, below the first pad: 0.2 clear, crush ribs at
    18.0, 0.4 lips) and RELIEVED above it: groove floors 0.8 off the edges, lip faces 1.0 off both PCB faces (ASSUMED
    bulge <= 0.6 past the edge, <= 0.8 proud).  The 0.4 front lips still overlap both edges (opening 17.2 < 18), so the
    board cannot leave toward the centre.  ESP32 moved 0.5 inboard / 0.4 east to keep the wider slot in the bore.
  * "a little more support for the BMP" -> a N corner (edge rail + fwd stop) and a backing web under its N half, off
    the slot's E wall (1:1.15 knee, no bridge).  The BMP is now carried on both long edges.

--- v15 notes:
v15 = v14 re-laid (2026-10-20, user):
  * "I kinda need the battery and the esp32 to be on opposite sides of the bay" -> answered "ESP32 north, battery
    south": the ESP32 now stands on the NORTH side, PCB back to the north bore, parts facing the centre (-y), in the
    v14-style SLIDE-IN SLOT (grooves on both long edges, slides in axially from the cap end).  The battery tray stays
    south (v10/v13 tray).  Its 24 mm power JST (with the battery plug) now points across the bay and ends over the
    pack's fwd end (tray floor notched there); the battery lead runs over the pack top straight into it.
  * "I meant the windows" (the piezo back-plate window), answered "Solid plate, TO-92 at pin end": the piezo back
    plate is SOLID behind the board except a through-opening at the PIN end: the 2 mm strip the user asked for, widened
    to a TO-92 pocket (5.5 wide, 4.4 deep, full board height -- the TO-92's Z position is not measured yet).
  * v14's 2 mm pin bay is REVERTED to v13 (7 mm, pins bent to ~2.5): the 2 mm was about the window, not the pins.
  * C1 now drops in AXIALLY from the cap end, FIRST (the solid plate closes v13's +x path through the window).
  * ADXL moved 3.5 aft / 3.2 west so the battery's sideways zip tie can sit 4.6 below the pack's fwd end.

LAYOUT (x = depth: -x = spine, +x = open face = the static + sound port side; y north)
  * ESP32 (18 x 45, parts 3.4) at x -10.8..7.2, PCB y 11.2..12.8, parts down to y 7.8 (v16).  Slot: groove walls at
    x -13.0..-11.4 and 7.0..8.6 (1.6); front lips (parts side) 0.4 over each edge, back lips 0.25; crush ribs at exactly 18.0;
    two back ribs + a back plate (y 14.1..15.3) tie both walls into a U-channel (v18: no heels).  The E front lip stops 6 below the (assumed) JST.
  * BATTERY tray south as v13, pack Z -2.0..38.5 (2.1 lower so the ESP32's JST + plug passes over its fwd end).
  * ADXL glued on the tray floor's inboard face (corner pocket), BMP on the tray's +x wall (S-edge corners) as v13.
  * Central column between the ADXL parts (y -0.6) and the ESP32 parts (y 8.3): S7V8F5 on the ESP32, wires.
  * Piezo on its solid back plate; a buttress north of it (arched for the pin leads) carries the slot's E wall.

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
REV = "v20"
RHO = 1.05e-3
R_AF_I = 20.0
R_MAX_MOVING = 19.5
SLED_RMAX = 19.39
CL = 0.40
WALL = 1.20
KNEE = 1.15
ZONE_Z1 = 64.0

CAP_Z0_V19 = 45.4                         # v19 cap face = top of the walls / old boss; the FwdTube is placed by it
RING_L = 16.0                             # D9aft v12 extension ring
CAP_Z0 = CAP_Z0_V19 + RING_L              # 61.4
TUBE_MOUTH_Z = CAP_Z0_V19 + 15.4          # 60.8 FwdTube mouth face (station 0 of the as-built tube)
SPIGOT_Z = (TUBE_MOUTH_Z - 9.5, TUBE_MOUTH_Z)   # 51.3..60.8 ring male spigot inside the tube mouth
SPIGOT_RI = 17.95                         # its bore (= the nose shoulder bore)
R_SPIGOT_CLR = SPIGOT_RI - 0.40           # 17.55: everything above SPIGOT_Z[0] stays inside this
POST_X, POST_Y = (-17.5, -13.1), 3.0      # spine -> post in the spigot band
POST_Z0 = 44.0
SPINE_Z1 = SPIGOT_Z[0] - 0.5              # 50.8 full spine (and the sled key) stop under the spigot
TUBE_GROOVE_Z0 = TUBE_MOUTH_Z - 16.4      # 44.4 FwdTube key groove end (D9aft v3 GROOVE_END 16.4)
SKEY_R = (19.0, 20.15)                    # = the EbayCap key (groove: 3.0 wide, to the thread root R 20.45)
SKEY_W = 2.4
SKEY_Z1 = SPINE_Z1
MOUNT_XW, MOUNT_XE = -15.3, 10.1          # MOUNT_XE: the cap's east hole -- NO boss under it (v11..v15)
MOUNT_HOLE_D = 2.0
MOUNT_BOSS_R = MOUNT_HOLE_D / 2.0 + 1.6
MOUNT_PILOT_DEPTH = 12.0
WBOSS_X1 = -13.5
WBOSS_Z0 = 39.4

SEAT_Z = -22.8
DECK_FLOOR = SEAT_Z + WALL                # -21.6
FOOT_RO = 19.3
SPINE_X1 = -16.6

# PIEZO (as v13)
PIEZO_ZC = -12.1
PIEZO_DL, PIEZO_DZ = 19.0, 15.0
PIEZO_PCB_T = 1.6
PIEZO_PCB_X0 = 6.8
PIEZO_CAN_H, PIEZO_CAN_D = 10.0, 12.0
PIEZO_X1 = PIEZO_PCB_X0 + PIEZO_PCB_T + PIEZO_CAN_H
PIEZO_Y0 = -8.0
PIEZO_Y1 = PIEZO_Y0 + PIEZO_DL            # 11.0 pin end
PIEZO_Z0 = PIEZO_ZC - PIEZO_DZ / 2.0      # -19.6
PIEZO_Z1 = PIEZO_Z0 + PIEZO_DZ            # -4.6
PIEZO_HDR = (2.5, 2.5, 7.6)
PIEZO_PIN_X = (0.95, 1.6)
PIEZO_PIN_BEND = (1.5, 2.0, 5.5)          # v13 (v14's 2 mm squeeze reverted)
PIEZO_PIN_Z = 5.7
PIN_BAY = (PIEZO_PCB_X0, 12.0, PIEZO_Y1, PIEZO_Y1 + 7.0)    # v13
PIEZO_SCREW_D = 2.0
PIEZO_HOLE_SPEC = ((2.5, 0.75, 0.50, -1), (3.0, 0.75, 0.75, +1))
PIEZO_HOLE_LIST = [(PIEZO_Y0 + dt + d / 2.0, PIEZO_ZC + sz * (PIEZO_DZ / 2.0 - ds - d / 2.0), d)
                   for d, dt, ds, sz in PIEZO_HOLE_SPEC]
FRAME_X0 = 4.2                            # back plate x 4.2..6.8 (2.6 thick)
FRAME_TOP = PIEZO_Z1
PBOSS_X0 = FRAME_X0 - 2.0                 # 2.2
PBOSS_R = PIEZO_SCREW_D / 2.0 + 1.2
FRAME_BAR_Y1 = PIEZO_Y0 + 4.5             # -3.5 (boss web)
END_WALL_Y = (PIEZO_Y0 - CL - WALL, PIEZO_Y0 - CL)         # -9.6 .. -8.4
PIEZO_CLEAR = (2.0, PIEZO_Z1 + CL)        # nothing printed at x >= 2.0, y -8.4..11, below Z -4.2 (piezo goes in along +x)
WINDOW_DY = 2.0                           # v15 (user): 2 mm through-opening at the pin end
Q1_T, Q1_W = 4.4, 5.5                     # TO-92 bent flat: 4.4 deep, 5.5 wide pocket at the pin end (Z unmeasured)
Q1_ZONE = (PIEZO_PCB_X0 - Q1_T, PIEZO_PCB_X0, PIEZO_Y1 - Q1_W, PIEZO_Y1, PIEZO_Z0 + 1.0, PIEZO_Z1 - 1.0)
OPEN_Z = (PIEZO_Z0 + 0.6, 0.0)            # plate opening Z (open over the top: no bridge over the pocket)
LEAD_ARCH = (PIEZO_Y1 + 0.5, 14.0, -11.0) # buttress arch for the pin leads: y0, y1, spring Z
E_DOWN_Y = (PIEZO_Y1 + PIEZO_PIN_BEND[0] + PIEZO_PIN_BEND[1] / 2.0 + CL, 16.5)   # v17 E rail column y 13.9..16.5 (north of the pins)

# BATTERY TRAY (v10 numbers, south flank, open outboard)
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_Z0 = -2.0                            # v13 0.1: lowered so the ESP32 JST + plug passes over the pack's fwd end
BATT_Z1 = BATT_Z0 + BATT_DZ               # 38.5
CL_BATT = 0.5
BATT_WALL = 1.2
TRAY_FACE = BATT_Y1 + BATT_WALL           # -5.8 floor's inboard face (ADXL glue face)
TRAY_X = BATT_DX / 2.0 + CL_BATT + BATT_WALL               # 11.7 wall outer face (BMP seat)
TRAY_TOP = 43.8
AFT_WEBS_X = ((-11.7, -10.5), (-6.6, -5.4), (-0.6, 0.6), (5.4, 6.6))
FWD_LIP = 1.5
TIE_W, TIE_T, TIE_CL = 2.5, 1.0, 0.25     # mini zip tie (v10)
TIE_Z0 = 31.4                             # band 31.15..34.15: above the ADXL fwd stop, 4.6 under the pack's fwd end
DOOR_X = ((SPINE_X1 + 0.6, -TRAY_X - 0.3), (-10.5 + 0.3, -6.6 - 0.3), (-5.4 + 0.3, -0.6 - 0.3))   # v19 floor doorways (x spans)

# NANO ESP32 -- NORTH wall, PCB back north, parts facing the centre (-y)
NANO_W, NANO_L, NANO_PCB_T, NANO_T = 18.0, 45.0, 1.6, 5.0
NANO_XC = -1.8                            # v15 -2.2
NANO_YB = 12.8                            # PCB back face (v15 13.3)
NANO_YF = NANO_YB - NANO_PCB_T            # 11.2 PCB parts face
NANO_YT = NANO_YB - NANO_T                # 7.8 parts top
NX0, NX1 = NANO_XC - NANO_W / 2.0, NANO_XC + NANO_W / 2.0   # -10.8, 7.2
NANO_Z0 = -0.3
NANO_Z1 = NANO_Z0 + NANO_L                # 44.7
NANO_ROW = 15.24 / 2.0
NANO_PAD_R = 0.85
NANO_JOINT_H = 0.5
NANO_PADS_Z = [NANO_Z0 + NANO_L / 2.0 + (i - 7) * 2.54 for i in range(15)]
NANO_EDGE = 0.6
JST_W, JST_H, JST_HDR = 6.0, 24.0, 8.0    # 24 tall WITH the plug (user); header alone ASSUMED 8
JST_X = (NANO_XC + 3.0, NANO_XC + 3.0 + JST_W)              # 1.2 .. 7.2 (= left of the USB-C, now +x)
JST_ZL = 5.5                              # ASSUMED: the JST is at the very USB-C end (last 5.5 mm)
RIBS_X = ((NANO_XC - 3.5, NANO_XC - 1.0), (NANO_XC + 1.0, NANO_XC + 3.5))   # back ribs (clear of the pad rows)
BULGE_X, BULGE_T, BULGE_IN = 0.6, 0.8, 1.4  # ASSUMED solder bulge at each edge pad: past the edge, proud of a face, inboard
CUP_Z1 = 3.0                              # tight aft-end cup up to here (first pad bulge starts at Z 3.57)
SLOT_CLY = 0.2                            # cup: groove floor off each PCB edge (crush ribs at exactly 18.0)
SLOT_CLT = 0.2                            # cup: lip faces off the PCB faces
REL_X = BULGE_X + 0.2                     # relieved groove floor off the edge (0.8)
REL_T = BULGE_T + 0.2                     # relieved lip faces off the PCB faces (1.0)
SLOT_LIP = 0.4                            # front lips over the parts-face edge band (pads ~0.5 in)
BACK_LIP = 0.25                           # cup back lips
GW_T = 1.6                                # groove wall
GW_Y = (NANO_YF - REL_T - WALL, NANO_YB + REL_T + WALL)     # 9.0 .. 15.0
BACK_PLATE_Y = NANO_YB + REL_T            # 13.8: back plate (= relieved back lips) ties both walls + the ribs
E_LIP_Z1 = NANO_Z1 - JST_ZL - 6.0         # 33.2: E front lip stops 6 below the (ASSUMED) JST
NANO_SLIDE = 66.0                         # +Z extraction length in [F] (sled top 61.4)
CRUSH_Z = (1.5,)                          # in the cup only (above it they would ride on the bulges)

# ADXL375 glued on the tray floor face, corner pocket
ADXL_W, ADXL_PCB_L, ADXL_L, ADXL_T, ADXL_PCB_T = 18.0, 26.0, 27.0, 5.0, 1.6
GLUE = 0.2
ADXL_Y0 = TRAY_FACE + GLUE                # -5.6 PCB back (parts toward +y)
ADXL_X = (-9.6, 8.2)                      # v13 -6.4..11.4
ADXL_Z0 = 3.5                             # v13 7.0 (floor behind it: piezo knee x < 8.7 at Z 3.5)
ADXL_PLUG_HW = 4.0
POCKET_H = 1.0

# BMP388 on top, PCB back down on the tray +x wall, parts up (v13)
BMP_W, BMP_L, BMP_PCB_T, BMP_PARTS = 22.0, 40.0, 1.6, 2.4
BMP_X0 = TRAY_X + GLUE                    # 11.9
BMP_Y = (-11.0, 11.0)
BMP_Z0 = -1.4
BMP_Z1 = BMP_Z0 + BMP_L                   # 38.6
QW_PLUG = (2.95, 4.25, 2.7)
QW_BEND = 1.5
BMP_N_WEB_Y0 = 8.8                        # v16 backing web under the BMP's N half (y 8.8..12.4)
BLOCK_Z_FAR = PIEZO_Z1 + CL + KNEE * 2.8  # -0.98: knee block under the slot's E wall rises from Z -4.2 at x 6.8
QX_CROSS = (36.4, 38.4)                  # ADXL->BMP cable crosses under the JST here
QX_RISE = (9.0, 11.5)                     # ... and rises between the JST (x 6.8) and the BMP (x 11.9)

# SMALL PARTS
C1_D, C1_L = 10.0, 14.0
C1_POS = (-12.2, -12.2 + C1_L, 3.0, DECK_FLOOR + 0.2 + C1_D / 2.0)          # aft deck; drops in axially (+Z out)
S7_BOX = (NANO_XC - 5.5, NANO_XC + 5.5, NANO_YT - CL - 3.5, NANO_YT - CL, 5.0, 22.0)

# D9aft
D9_CREST = 19.65
D9_R_ID, D9_R_OD = 20.0, 21.5
D9_BAND_Z = 60.8 - 12.5
D9_SEAT_Z, D9_SEAT_RI, D9_SEAT_T = SEAT_Z, 15.5, 2.0
D9_SPIGOT_RI = 18.5
D9_PORTS = (("static", 1.5, 30.0, 0.0), ("sound", 3.0, PIEZO_ZC, 0.0))
D9V10_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v10_%s.step" % k)) for k in ("EbayCap", "FwdTube"))
D9V12_RING = os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v12_ExtensionRing.step")   # FwdTube frame (as the v10 STEPs)
DRIVER_D = 3.0

ASSUMED = [
    "TO-92 (bent flat on the piezo back) sits at the PIN end inside a 5.5 x 4.4 pocket, Z anywhere on the board (user: 'at pin end'; position + footprint not measured)",
    "ESP32 edge solder bulges (user: 'some'): <= 0.6 past the edge, <= 0.8 proud of either face, only at the 15 pad positions per edge (none in the aft 3.9 mm)",
    "the last E-edge pad's bulge envelope overlaps the JST footprint (both assumed) -- the JST's own solder there",
    "ESP32 JST-PH in the last 5.5 mm at the USB-C end, 6 wide, on the +x edge (left of the USB-C); header alone 8 tall, 24 with the plug",
    "ESP32 wires on the pad rows stay inside r 0.85 of the pad centre at the parts face (front lips 0.13 from the pad edge)",
    "piezo pins bent ~1.5 past the board end and down 5.5, heat-shrunk (v13); leads exit west under the buttress arch",
    "C1 470 uF 16 V: d10 x 12.5 body + 1.5 bent leads, loose in the aft deck",
    "S7V8F5 17 x 11 x 3 + 0.5 joints, lying on the ESP32's parts (Kapton between)",
    "ESP32 PCB 18.0 wide: the crush ribs sit at exactly 18.0 -- file them if it is too tight",
    "Qwiic plug 2.95 deep x 4.25 long x 5.4 wide; cables bend 1.5 past the plug",
    "ESP32 USB-C <= 0.3 past the PCB end; parts 3.4 tall, 0.6 edge bands free; back joints 0.5",
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

def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, Vector(x, y0, z), Vector(0, 1, 0))

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

def arch_win(axis, u0, u1, z0, zs, w0, w1):
    """window through a wall from z0 up to a pointed 1:1.15 arch springing at zs (u along the wall)"""
    um = (u0 + u1) / 2.0
    return prism(axis, [(u0, z0), (u1, z0), (u1, zs), (um, zs + KNEE * (u1 - u0) / 2.0), (u0, zs)], w0, w1)

# ================================================================ component envelopes
def env_nano():
    s = box(NX0, NX1, NANO_YF, NANO_YB, NANO_Z0, NANO_Z1)
    e = NANO_W / 2.0 - NANO_EDGE
    return as_solid(s.fuse(box(NANO_XC - e, NANO_XC + e, NANO_YT, NANO_YF, NANO_Z0, NANO_Z1)).removeSplitter())

def env_nano_joints():
    """back-face joints + (v16) the solder bulge at every edge pad: BULGE_X past the edge, BULGE_T proud of both faces"""
    s = None
    for sx in (-1, 1):
        xe = NANO_XC + sx * NANO_W / 2.0
        for z in NANO_PADS_Z:
            j = cyl_y(NANO_PAD_R, NANO_YB, NANO_YB + NANO_JOINT_H, NANO_XC + sx * NANO_ROW, z)
            j = j.fuse(box(*(sorted((xe - sx * BULGE_IN, xe + sx * BULGE_X)) + [NANO_YF - BULGE_T, NANO_YB + BULGE_T,
                                                                               z - NANO_PAD_R, z + NANO_PAD_R])))
            s = j if s is None else s.fuse(j)
    return as_solid(s.removeSplitter().cut(env_nano()))

def env_jst():
    """header + battery plug, 24 tall off the parts face toward -y (ends over the pack's fwd end)"""
    return box(JST_X[0], JST_X[1], NANO_YF - JST_H, NANO_YF, NANO_Z1 - JST_ZL, NANO_Z1)

def env_jst_header():
    return box(JST_X[0], JST_X[1], NANO_YF - JST_HDR, NANO_YF, NANO_Z1 - JST_ZL, NANO_Z1)

def adxl_xc():
    return (ADXL_X[0] + ADXL_X[1]) / 2.0

def env_adxl():
    y1 = ADXL_Y0 + ADXL_T
    s = box(ADXL_X[0], ADXL_X[1], ADXL_Y0, y1, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    s = s.fuse(box(adxl_xc() - ADXL_PLUG_HW, adxl_xc() + ADXL_PLUG_HW, ADXL_Y0, y1, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 + ADXL_L))
    return as_solid(s.removeSplitter())

def env_bmp():
    xp = BMP_X0 + BMP_PCB_T
    s = box(BMP_X0, xp + BMP_PARTS, BMP_Y[0], BMP_Y[1], BMP_Z0, BMP_Z1)
    d, ln, hw = QW_PLUG
    s = s.fuse(box(xp, xp + d, -hw, hw, BMP_Z0 - ln, BMP_Z0))
    s = s.fuse(box(xp, xp + d, -hw, hw, BMP_Z1, BMP_Z1 + ln))
    return as_solid(s.removeSplitter())

def env_qwiic_adxl_bmp():
    """ADXL fwd plug -> up the floor face -> across UNDER the ESP32's JST -> up between the JST and the BMP ->
    over the BMP's fwd end -> U-turn into its fwd plug"""
    d, ln, hw = QW_PLUG
    xp = BMP_X0 + BMP_PCB_T
    za = ADXL_Z0 + ADXL_L
    yl = TRAY_FACE + TIE_T + TIE_CL + 0.4
    zt = BMP_Z1 + ln + QW_BEND
    s = box(adxl_xc() - hw, adxl_xc() + hw, yl, ADXL_Y0 + ADXL_T, za, QX_CROSS[1])
    s = s.fuse(box(adxl_xc() - hw, QX_RISE[1], yl, hw, QX_CROSS[0], QX_CROSS[1]))
    s = s.fuse(box(QX_RISE[0], QX_RISE[1], -hw, hw, QX_CROSS[0], zt))
    s = s.fuse(box(QX_RISE[0], xp + d, -hw, hw, BMP_Z1 + ln, zt))
    return as_solid(s.removeSplitter())

def env_qwiic_bmp_nano():
    """BMP aft plug -> bends sideways (+y) -> along -x over the piezo -> to the ESP32's aft end (wired to its pads)"""
    d, ln, hw = QW_PLUG
    xp = BMP_X0 + BMP_PCB_T
    za = BMP_Z0 - ln
    s = box(xp, xp + d, hw, 3.0 * hw, za, BMP_Z0 - CL)
    s = s.fuse(box(NANO_XC + 1.2, xp + d, hw, 3.0 * hw, PIEZO_Z1 + CL, BMP_Z0 - CL))
    s = s.fuse(box(NANO_XC + 1.2, NANO_XC + 5.2, hw, NANO_YT - CL, PIEZO_Z1 + CL, NANO_Z0 + 2.0))
    return as_solid(s.removeSplitter())

def env_batt():
    return box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0, BATT_Z1)

def env_batt_lead():
    """pack lead from its fwd -x corner, over the pack top, to the plug in the ESP32's JST"""
    yc = BATT_Y1 - BATT_DY / 2.0
    return box(-BATT_DX / 2.0, JST_X[0], yc - 1.25, yc + 1.25, BATT_Z1 + CL_BATT, BATT_Z1 + CL_BATT + 2.5)

def env_tie():
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

def e_rail_down():
    """v17: the slot's E wall continued down to the deck floor, north of the piezo pins"""
    return box(PIEZO_PCB_X0 - 0.01, NX1 + REL_X + GW_T, E_DOWN_Y[0], E_DOWN_Y[1], DECK_FLOOR - 0.01, NANO_Z0 - 0.1)

def pin_bay():
    return clip_bore(box(PIN_BAY[0], PIN_BAY[1], PIN_BAY[2], PIN_BAY[3], DECK_FLOOR, PIEZO_Z1)).cut(e_rail_down())

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
    ("Battery_lead", env_batt_lead),
    ("ZipTie",       env_tie),
]
RIGID = [n for n, _ in COMPONENTS]

# ================================================================ the sled
def build_sled(log):
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)
    by_out = BATT_Y1 - BATT_DY                                                 # -15.5 tray mouth
    piezo_cut = knee_cut("x", PIEZO_CLEAR[0], PIEZO_CLEAR[1], +1)

    parts.append(clip_bore(box(-19.0, SPINE_X1, -12.0, 12.0, SEAT_Z, SPINE_Z1)))           # spine (v20: stops under the ring spigot, no cap key)
    parts.append(clip_bore(box(POST_X[0], POST_X[1], -POST_Y, POST_Y, POST_Z0, CAP_Z0), r=R_SPIGOT_CLR))   # v20 post up to the cap
    kp = prism("x", [(-18.6, 43.6), (-18.6, SKEY_Z1), (-SKEY_R[1], SKEY_Z1), (-SKEY_R[1], 45.05), (-20.0, 44.9)], -SKEY_W / 2.0, SKEY_W / 2.0)
    parts.append(kp)                                                                    # v20 sled key (45 deg underside), NOT clipped
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, DECK_FLOOR)))                                    # floor disc

    # ---- BATTERY TRAY (v13, south)
    fl = box(-19.0, TRAY_X, BATT_Y1, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)
    parts.append(cap(fl.cut(piezo_cut)))
    parts.append(cap(box(-TRAY_X, -TRAY_X + BATT_WALL, by_out, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)))   # -x wall
    xw = box(TRAY_X - BATT_WALL, TRAY_X, by_out, TRAY_FACE, DECK_FLOOR - 0.01, TRAY_TOP)                  # +x wall = BMP seat
    xw = xw.cut(box(PIEZO_CLEAR[0], 30, END_WALL_Y[1], 30, -60, PIEZO_CLEAR[1]))
    parts.append(cap(xw))
    for x0, x1 in AFT_WEBS_X[1:]:
        y1 = BATT_Y1 if x0 < PIEZO_CLEAR[0] else END_WALL_Y[0] + 0.8
        parts.append(cap(box(x0, x1, by_out, y1, DECK_FLOOR - 0.01, BATT_Z0 - CL_BATT)))
    c1z = BATT_Z1 + CL_BATT                                                                # 39.0
    parts.append(cap(box(-BATT_DX / 2.0 - CL_BATT, BATT_DX / 2.0 + CL_BATT, BATT_Y1 - FWD_LIP, BATT_Y1 + 0.01, c1z, c1z + 1.5)))   # fwd lip
    # JST + plug passes over the pack's fwd end: floor (and the lip) notched there
    drill.append(box(JST_X[0] - CL, JST_X[1] + CL, by_out - 1.0, TRAY_FACE + 0.5, NANO_Z1 - JST_ZL - CL, 60.0))
    tz0, tz1 = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL
    for sx in (-1, 1):
        xa, xb = sorted((sx * (BATT_DX / 2.0 - 0.01), sx * TRAY_X))
        sl = prism("y", [(TRAY_FACE + 0.01, tz0), (TRAY_FACE + 0.01, tz1), (by_out - 1.0, tz1 + KNEE * (TRAY_FACE - by_out + 1.0)),
                         (by_out - 1.0, tz0)], xa, xb)
        drill.append(sl.common(box(xa, xb, by_out - 1.0, TRAY_FACE + 0.01, tz0, TRAY_TOP + 1.0)))

    # ---- ESP32 SLOT on the north side: relieved U-channel full length + a tight cup at the (pad-free) aft end
    yl0, yl1 = GW_Y[0], NANO_YF - REL_T                       # relieved front lip band 9.0 .. 10.2
    wx0, ex0 = NX0 - REL_X, NX1 + REL_X                       # relieved groove floors -11.6 / 8.0
    ez0 = NANO_Z0 - 0.2                                       # E side starts on the block (above the piezo)
    parts.append(cap(box(wx0 - GW_T, wx0, GW_Y[0], GW_Y[1], DECK_FLOOR - 0.01, CAP_Z0_V19)))                # W wall
    parts.append(cap(box(wx0 - 0.01, NX0 + SLOT_LIP, yl0, yl1, DECK_FLOOR - 0.01, CAP_Z0_V19)))              # W front lip
    parts.append(cap(box(ex0, ex0 + GW_T, GW_Y[0], GW_Y[1], ez0, CAP_Z0_V19)))                              # E wall
    parts.append(cap(box(NX1 - SLOT_LIP, ex0 + 0.01, yl0, yl1, ez0, E_LIP_Z1)))                         # E front lip (short of the JST)
    parts.append(cap(box(wx0 - GW_T, PIEZO_PCB_X0, BACK_PLATE_Y, GW_Y[1], DECK_FLOOR - 0.01, CAP_Z0_V19)))   # back plate (W part)
    parts.append(cap(box(PIEZO_PCB_X0 - 0.01, ex0 + GW_T, BACK_PLATE_Y, GW_Y[1], ez0, CAP_Z0_V19)))         # back plate (E part)
    for sg, xe, z0 in ((-1, NX0, DECK_FLOOR - 0.01), (1, NX1, ez0)):                                      # aft-end cups
        xf, xr = xe + sg * SLOT_CLY, xe + sg * (REL_X + 0.01)
        cup = box(*(sorted((xf, xr)) + [GW_Y[0], GW_Y[1], z0, CUP_Z1]))
        cup = cup.fuse(box(*(sorted((xe - sg * SLOT_LIP, xr)) + [GW_Y[0], NANO_YF - SLOT_CLT, z0, CUP_Z1])))
        cup = cup.fuse(box(*(sorted((xe - sg * BACK_LIP, xr)) + [NANO_YB + SLOT_CLT, GW_Y[1], z0, CUP_Z1])))
        parts.append(cap(cup))
    # E side stands above the piezo: buttress (x 4.2..6.8, arched for the pin leads) -> knee block -> wall
    bt = box(FRAME_X0, PIEZO_PCB_X0, PIEZO_Y1 + CL + 0.1, 19.5, DECK_FLOOR - 0.01, NANO_Z0 - 0.1)
    bt = bt.cut(arch_win("y", LEAD_ARCH[0], LEAD_ARCH[1], DECK_FLOOR - 1.0, LEAD_ARCH[2], FRAME_X0 - 1.0, PIEZO_PCB_X0 + 1.0))
    parts.append(cap(bt))
    blk = box(PIEZO_PCB_X0 - 0.01, ex0 + GW_T, GW_Y[0], GW_Y[1], PIEZO_Z1 + CL, NANO_Z0 - 0.1)
    parts.append(cap(corbel(blk, "x", PIEZO_PCB_X0, BLOCK_Z_FAR, ex0 + GW_T)))
    parts.append(cap(e_rail_down()))                                                                  # v17 E rail down to the floor
    # BMP N support: backing web under its N half + N edge rail + fwd stop, off the E wall on a knee
    xr1 = BMP_X0 + BMP_PCB_T - 0.2
    bw = box(ex0 + GW_T - 0.01, TRAY_X, BMP_N_WEB_Y0, BMP_Y[1] + CL + 1.0, BLOCK_Z_FAR - 0.3, BMP_Z1 + CL + 0.6)
    bw = bw.fuse(box(TRAY_X - 0.01, xr1, BMP_Y[1] + CL, BMP_Y[1] + CL + 1.0, BLOCK_Z_FAR - 0.3, BMP_Z1 + CL + 0.6))
    bw = bw.fuse(box(TRAY_X - 0.01, xr1, 8.8, BMP_Y[1] + CL + 1.0, BMP_Z1 + CL, BMP_Z1 + CL + 0.6))
    parts.append(cap(corbel(bw, "x", ex0 + GW_T - 0.01, BLOCK_Z_FAR + KNEE * (xr1 - ex0 - GW_T), xr1)))
    for zc in CRUSH_Z:
        parts.append(cap(box(wx0 - 0.01, NX0, NANO_YF, NANO_YB, zc - 0.5, zc + 0.5)))
        parts.append(cap(box(NX1, ex0 + 0.01, NANO_YF, NANO_YB, zc - 0.5, zc + 0.5)))
    for x0, x1 in RIBS_X:
        parts.append(cap(box(x0, x1, NANO_YB, 19.5, DECK_FLOOR - 0.01, NANO_Z1)))                       # back rib

    # ---- ADXL corner pocket on the floor face: bottom-edge rail, aft stop, fwd stop split round the plug
    yp0, yp1 = TRAY_FACE - 0.01, TRAY_FACE + POCKET_H
    za, zf = ADXL_Z0 - CL, ADXL_Z0 + ADXL_PCB_L + CL
    xr0 = ADXL_X[0] - CL - WALL
    parts.append(cap(box(xr0, ADXL_X[0] - CL, yp0, yp1, za - 0.6, zf + 0.6)))
    parts.append(cap(box(xr0, ADXL_X[1] - 2.0, yp0, yp1, za - 0.6, za)))
    hw = ADXL_PLUG_HW + CL
    parts.append(cap(box(xr0, adxl_xc() - hw, yp0, yp1, zf, zf + 0.6)))

    # ---- BMP corners on the +x wall (v13)
    ys0, ys1 = BMP_Y[0] - CL - 1.0, BMP_Y[0] - CL
    xr0, xr1 = TRAY_X - 0.01, BMP_X0 + BMP_PCB_T - 0.2
    rail = box(xr0, xr1, ys0, ys1, BMP_Z0 - CL - 0.6, BMP_Z1 + CL + 0.6)
    rail = rail.fuse(box(xr0, xr1, ys0, -8.8, BMP_Z0 - CL - 0.6, BMP_Z0 - CL))
    rail = rail.fuse(box(xr0, xr1, ys0, -8.8, BMP_Z1 + CL, BMP_Z1 + CL + 0.6))
    parts.append(cap(rail))

    # ---- W cap boss
    wb = cyl(MOUNT_BOSS_R, 25.0, CAP_Z0_V19, MOUNT_XW, 0.0).cut(box(WBOSS_X1, 30, -30, 30, 0, 60))
    wb = corbel(wb, "x", SPINE_X1, WBOSS_Z0, WBOSS_X1)
    parts.append(cap(wb))
    drill.append(cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, MOUNT_XW, 0.0))   # v20: in the post

    # ---- piezo SOLID back plate (v15) + screw bosses + end wall; through-opening at the pin end
    pb = box(FRAME_X0, PIEZO_PCB_X0, PIEZO_Y0 - CL, PIEZO_Y1 + CL, DECK_FLOOR - 0.01, FRAME_TOP)
    pb = pb.fuse(box(PBOSS_X0, FRAME_X0 + 0.01, PIEZO_Y0 - CL, FRAME_BAR_Y1 - CL, DECK_FLOOR - 0.01, PIEZO_HOLE_LIST[1][1]))
    for yc, zc, _ in PIEZO_HOLE_LIST:
        pb = pb.fuse(cyl_x(PBOSS_R, PBOSS_X0, FRAME_X0 + 0.01, yc, zc))
        drill.append(cyl_x(PIEZO_SCREW_D / 2.0 - 0.2, PBOSS_X0 - 0.5, PIEZO_PCB_X0 + 1.0, yc, zc))
    pb = pb.cut(box(PBOSS_X0 - 0.1, PIEZO_PCB_X0 + 0.1, PIEZO_Y0 - CL - 0.1, FRAME_BAR_Y1 + 0.1, FRAME_TOP, 0.0))
    pb = pb.fuse(box(FRAME_X0, SLED_RMAX + 1.0, END_WALL_Y[0], END_WALL_Y[1], DECK_FLOOR - 0.01, FRAME_TOP))
    parts.append(cap(pb))
    drill.append(box(PBOSS_X0, PIEZO_PCB_X0, PIEZO_Y1 - WINDOW_DY, PIEZO_Y1 + CL + 0.1, OPEN_Z[0], OPEN_Z[1]))       # 2 mm strip
    drill.append(box(PBOSS_X0, PIEZO_PCB_X0, Q1_ZONE[2] - CL, PIEZO_Y1 + CL + 0.1, OPEN_Z[0], OPEN_Z[1]))            # TO-92 pocket

    # ---- v19: arched doorways in the tray floor below the pack (aft deck <-> the cells under the tray)
    for dx0, dx1 in DOOR_X:
        pk = BATT_Z0 - CL_BATT - 0.5
        drill.append(arch_win("x", dx0, dx1, DECK_FLOOR - 1.0, pk - KNEE * (dx1 - dx0) / 2.0, BATT_Y1 - 1.0, TRAY_FACE + 1.0))

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
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (v19 + 16 mm slack chamber, D9aft v12 ring)" % REV)
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
    skz = box(-21.0, -18.55, -SKEY_W / 2.0 - 0.01, SKEY_W / 2.0 + 0.01, 43.5, SKEY_Z1 + 0.01)
    rs = rmax_mesh(mesh_of(sled.cut(skz)))
    P("  %-15s Rmax %6.2f  toID %5.2f   %s   (sled key exempt, below)" % ("Sled", rs, R_AF_I - rs, "PASS" if rs <= SLED_RMAX + 0.05 else "FAIL"))
    kb = sled.common(skz).BoundBox
    kr = rmax_mesh(mesh_of(sled.common(skz)))
    P("  sled key at 180 deg: Rmax %.2f vs groove floor 20.45 (%.2f); half-width %.2f vs 1.50 (%.2f); Z %.2f..%.2f;"
      % (kr, 20.45 - kr, kb.YMax, 1.5 - kb.YMax, kb.ZMin, kb.ZMax))
    lowk = sled.common(skz).common(box(-21, -19.95, -2, 2, 40.0, TUBE_GROOVE_Z0 + 0.3))
    P("    part beyond R 19.95 below the groove end Z %.1f + 0.3: %.3f mm3; top %.2f under the spigot %.1f   %s"
      % (TUBE_GROOVE_Z0, vol(lowk), kb.ZMax, SPIGOT_Z[0], "PASS" if 20.45 - kr >= 0.25 and 1.5 - kb.YMax >= 0.25 and vol(lowk) < 1e-3 and kb.ZMax <= SPIGOT_Z[0] - 0.3 else "FAIL"))
    band = cyl(30.0, SPIGOT_Z[0], CAP_Z0 + 0.5).cut(cyl(R_SPIGOT_CLR, SPIGOT_Z[0] - 1, CAP_Z0 + 1))
    bh = [(n, round(vv(s, band), 3)) for n, s in [("Sled", sled)] + list(comp.items()) if vv(s, band) > 1e-3]
    P("  ring spigot band Z %.1f..%.1f: everything inside R %.2f (bore %.2f - 0.4; the ring screws down over it): %s   %s"
      % (SPIGOT_Z[0], CAP_Z0, R_SPIGOT_CLR, SPIGOT_RI, bh or "clear", "PASS" if not bh else "FAIL"))
    P("  component tops Z .. %.1f vs EbayCap face %.1f   %s" % (zmax, CAP_Z0, "PASS" if zmax <= CAP_Z0 - 0.3 else "FAIL"))
    above = sled.common(box(-30, 30, -30, 30, CAP_Z0 + 0.01, ZONE_Z1 + 5))
    sv = vol(above)
    P("  above EbayCap face: %.2f mm3 (v20: no spine key into the cap)   %s" % (sv, "PASS" if sv < 0.01 else "FAIL"))
    top = sled.common(box(-30, 30, -30, 30, CAP_Z0 - 0.2, CAP_Z0))
    ring = cyl(1.8, CAP_Z0 - 0.2, CAP_Z0, MOUNT_XW, 0.0).cut(cyl(MOUNT_HOLE_D / 2.0, CAP_Z0 - 1, CAP_Z0 + 1, MOUNT_XW, 0.0))
    f = vv(top, ring) / ring.Volume
    P("  EbayCap W M2 boss (%.1f, 0) seated at Z %.1f: %.0f %% of the head footprint backed   %s" % (MOUNT_XW, CAP_Z0, 100 * f, "PASS" if f > 0.95 else "FAIL"))
    P("  EbayCap E M2 boss (%.1f, 0): DELETED -- leave the cap's east screw OUT, tape the hole (W screw + spine key hold it)" % MOUNT_XE)

    P("")
    P("[F] LOADING -- every part along its path in ASSEMBLY ORDER (sled in hand, out of the tube) until it is clear;")
    P("    it must not touch the sled or any part already in (touching = 0 mm3 allowed: crush ribs).")
    P("    C1 and the ESP32 go in AXIALLY from the cap end (tested as +Z extraction); the ESP32 slides with its JST HEADER")
    P("    only (battery plug out); the rest goes in from the open face (+x); the battery slides into its tray from -y.")
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
    X, Zp = Vector(1, 0, 0), Vector(0, 0, 1)
    comp_f = dict(comp); comp_f["JST_header"] = env_jst_header()
    LOAD = [("C1_470uF",   ["C1_470uF"], [(Zp, 75.0)]),
            ("Nano_ESP32", ["Nano_ESP32", "Nano_joints", "JST_header"], [(Zp, NANO_SLIDE)]),
            ("S7V8F5",     ["S7V8F5"], [(X, None)]),
            ("Piezo_Q1",   ["Piezo_Q1"], [(X, None)]),
            ("ADXL375",    ["ADXL375"], [(X, None)]),
            ("BMP388",     ["BMP388"], [(X, None)]),
            ("Battery",    ["Battery", "Battery_lead"], [(Vector(0, -1, 0), None)])]
    loaded = []
    for nm, members, path in LOAD:
        sh = comp_f[members[0]]
        for m in members[1:]:
            sh = sh.fuse(comp_f[m])
        others = [("Sled", sled)] + [(k, comp_f[k]) for k in loaded]
        h = sweep(sh, path, others)
        ps = " then ".join("%s%s" % ("(%+.0f,%+.0f,%+.0f)" % (d.x, d.y, d.z), (" %.1f" % L) if L else " out") for d, L in path)
        P("  %-15s %-34s %s   %s" % (nm, ps, "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), "PASS" if not h else "FAIL"))
        loaded += members
    P("  then laid in: Qwiic cables, zip tie round the pack, and LAST the battery plug into the ESP32's JST (= ON).")
    for k in ("Qwiic_ADXL_BMP", "Qwiic_BMP_Nano", "ZipTie", "JST_power"):
        hit = [(n2, round(vv(comp[k], comp[n2]), 2)) for n2 in comp if n2 != k and not (k == "JST_power" and n2 in ("Nano_ESP32", "Nano_joints"))
               and vv(comp[k], comp[n2]) > 1e-2]
        P("  %-15s laid in after the boards: overlaps %s   %s" % (k, hit or "nothing", "PASS" if not hit else "FAIL"))
    P("  (to take the battery out: unplug it first -- the plug end sits over the pack's fwd end)")

    P("")
    P("[R] ESP32 SLOT (north side)")
    npcb = box(NX0, NX1, NANO_YF, NANO_YB, NANO_Z0, NANO_Z1)
    cpcb = box(NX0, NX1, NANO_YF, NANO_YB, NANO_Z0, CUP_Z1)
    upcb = box(NX0, NX1, NANO_YF, NANO_YB, CUP_Z1, NANO_Z1)
    for nm, sg in (("W", -1), ("E", 1)):
        xe = NX0 if sg < 0 else NX1
        cont = box(*(sorted((xe, xe + sg * 0.05)) + [NANO_YF, NANO_YB, NANO_Z0, NANO_Z1]))
        ca = vv(sled, cont) / 0.05
        half = box(*(sorted((NANO_XC, NANO_XC + sg * 30.0)) + [-30, 30, -60, 60]))
        sh = sled.common(half)
        cx = vv(sh, cpcb.translated(Vector(sg * 0.5, 0, 0)))
        cf = vv(sh, cpcb.translated(Vector(0, -0.5, 0)))
        cb = vv(sh, cpcb.translated(Vector(0, 0.5, 0)))
        uf = vv(sh, upcb.translated(Vector(0, -(REL_T + 0.2), 0)))
        P("  %s CUP (Z %.1f..%.1f, 0.2 clear): PCB moved 0.5 mm out / -y / +y hits %.1f / %.1f / %.1f mm3; crush rib on the edge %.1f mm2"
          % (nm, NANO_Z0, CUP_Z1, cx, cf, cb, ca))
        P("    relieved slot above: floor %.1f off the edge, lip faces %.1f off the faces; PCB moved %.1f -y hits the front lip %.1f mm3   %s"
          % (REL_X, REL_T, REL_T + 0.2, uf, "PASS" if min(cx, cf, cb, uf) > 0.1 and ca > 1.0 else "FAIL"))
    opening = (NX1 - SLOT_LIP) - (NX0 + SLOT_LIP)
    P("  front lips 0.4 over both edges: opening %.1f < board %.1f, even pushed %.1f sideways the far edge stays under %.1f   %s"
      % (opening, NANO_W, REL_X, SLOT_LIP, "PASS" if opening < NANO_W - 0.5 else "FAIL"))
    bg = comp["Nano_joints"].distToShape(sled)[0]
    P("  solder bulges (ASSUMED %.1f past the edge, %.1f proud, every pad Z %.1f..%.1f) -> sled %.2f mm; they ride the whole"
      % (BULGE_X, BULGE_T, NANO_PADS_Z[0] - NANO_PAD_R, NANO_PADS_Z[-1] + NANO_PAD_R, bg))
    P("    slide in [F] with the board; first bulge %.2f above the cup top   %s"
      % (NANO_PADS_Z[0] - NANO_PAD_R - CUP_Z1, "PASS" if bg >= 0.15 and NANO_PADS_Z[0] - NANO_PAD_R - CUP_Z1 >= 0.3 else "FAIL"))
    lt = sled.common(box(NX1 - SLOT_LIP, NX1 + REL_X, GW_Y[0], NANO_YF - REL_T, CUP_Z1 + 0.1, 60)).BoundBox.ZMax
    P("  E front lip top Z %.1f vs JST bottom Z %.1f (ASSUMED %.1f from the board end): %.1f margin   %s"
      % (lt, NANO_Z1 - JST_ZL, JST_ZL, NANO_Z1 - JST_ZL - lt, "PASS" if NANO_Z1 - JST_ZL - lt >= 3.0 else "FAIL"))
    hb = vv(sled, box(NX0, NX1, NANO_YF, NANO_YB, NANO_Z0 - 0.5, NANO_Z0 - 0.1)) / 0.4
    bkr = vv(sled, box(NX0, NX1, NANO_YB, NANO_YB + 0.1, NANO_Z0, NANO_Z1)) / 0.1
    P("  aft end on printed material %.1f mm2 within 0.5 (v18: heels removed); back on 2 full-length ribs %.0f mm2   %s"
      % (hb, bkr, "PASS" if bkr > 150 else "FAIL"))
    nano_all = comp["Nano_ESP32"].fuse(comp["Nano_joints"]).fuse(comp_f["JST_header"])
    hx = max(vv(sled, nano_all.translated(Vector(0, -0.5 * i, 0))) for i in range(1, 25))
    P("  NEGATIVE CONTROL: the ESP32 pulled out sideways (-y, toward the centre) hits the lips %.1f mm3 (must be > 0)   %s"
      % (hx, "PASS" if hx > 1.0 else "FAIL"))

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
    P("  ADXL pose: long axis = rocket Z, PCB back on the floor face, parts toward +y, plug FWD (as v13; moved 3.5 aft, 3.2 west)")
    for nm, ys in (("S half (tray +x wall)", [BMP_Y[0] + 0.5 + 1.0 * i for i in range(5)]),
                   ("N half (v16 web)", [BMP_N_WEB_Y0 + 0.3 + 0.5 * i for i in range(5)])):
        pts = [(y, z) for y in ys for z in [BMP_Z0 + 1.0 + 4.0 * j for j in range(10)]]
        back = sum(1 for y, z in pts if sled.common(Part.makeLine(Vector(TRAY_X + 0.19, y, z), Vector(TRAY_X - 1.0, y, z))).Edges)
        P("  BMP388 seat, %-22s y %.1f..%.1f: %d / %d grid points with sled right behind the PCB   %s"
          % (nm, ys[0], ys[-1], back, len(pts), "PASS" if back >= 0.8 * len(pts) else "FAIL"))
    bpcb = box(BMP_X0, BMP_X0 + BMP_PCB_T, BMP_Y[0], BMP_Y[1], BMP_Z0, BMP_Z1)
    lr = [round(touch(bpcb, v), 1) for v in (Vector(0, -1.0, 0), Vector(0, 1.0, 0), Vector(0, 0, -1.0), Vector(0, 0, 1.0))]
    P("  BMP corners: PCB moved 1 mm toward the S rail / N rail / aft stop / fwd stop hits %s mm3 (N + S edges both held)   %s"
      % (lr, "PASS" if min(lr) > 0 else "FAIL"))

    P("")
    P("[I] FIT -- RAW = the as-drawn sled inside each part's keep-out BEFORE the trim; post-cut must be 0.")
    for n in comp:
        P("  %-15s RAW %7.1f mm3   post-cut %.1f   %s" % (n, raw.get(n, 0.0), vv(sled, comp[n]), "" if raw.get(n, 0.0) < 0.5 else "(sled member trimmed by the part -- review)"))
    cn = list(comp.keys()); cc = 0
    designed = {("Nano_ESP32", "JST_power"), ("Nano_joints", "JST_power")}
    for i in range(len(cn)):
        for j in range(i + 1, len(cn)):
            v = vv(comp[cn[i]], comp[cn[j]])
            if (cn[i], cn[j]) in designed:
                P("    designed: %s on %s" % (cn[j], cn[i])); continue
            if v > 0.05:
                cc += 1; P("    CLASH %s <-> %s  %.2f mm3   FAIL" % (cn[i], cn[j], v))
    P("  part-vs-part clashes: %d   %s" % (cc, "PASS" if cc == 0 else "FAIL"))
    P("  gaps between neighbours (want >= %.1f):" % (CL - 0.05))
    for a, b in (("Nano_ESP32", "S7V8F5"), ("Nano_ESP32", "ADXL375"), ("Nano_ESP32", "Piezo_Q1"), ("Nano_ESP32", "C1_470uF"),
                 ("Nano_ESP32", "Battery"), ("JST_power", "Battery"), ("JST_power", "BMP388"), ("JST_power", "Qwiic_ADXL_BMP"),
                 ("ADXL375", "BMP388"), ("ADXL375", "Battery"), ("S7V8F5", "ADXL375"), ("Battery", "Piezo_Q1"),
                 ("BMP388", "Piezo_Q1"), ("C1_470uF", "Qwiic_BMP_Nano"), ("Piezo_Q1", "Qwiic_BMP_Nano"),
                 ("ZipTie", "ADXL375"), ("ZipTie", "Qwiic_ADXL_BMP"), ("Battery_lead", "Battery")):
        g = comp[a].distToShape(comp[b])[0]
        P("    %-15s - %-15s %5.2f   %s" % (a, b, g, "PASS" if g >= CL - 0.05 else "WARN"))

    P("")
    P("[S] SCREW ACCESS (d%.1f driver from the head along +x; sees the sled + every part in before that screw)" % DRIVER_D)
    order = [n for _, ms, _ in LOAD for n in ms]
    for hy, hz, d in PIEZO_HOLE_LIST:
        drv = Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(PIEZO_PCB_X0 + PIEZO_PCB_T + 1.8, hy, hz), X)
        inn = order[:order.index("Piezo_Q1")]
        hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp_f[k]) for k in inn] for v in [vv(sh, drv)] if v > 1e-2]
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
        P("  piezo M2 (y %+5.2f, Z %.2f): thread %.1f mm %s; plate under the hole %3.0f %% %s; M2 head to can %.2f %s"
          % (hy, hz, tl, "PASS" if tl >= 4.0 else "FAIL", 100 * f, "PASS" if f > 0.8 else "FAIL", gap, "PASS" if gap > 0.2 else "WARN (as v10: file a flat on that pan head)"))
    wl = sum(e.Length for e in sled.common(Part.makeLine(Vector(MOUNT_XW, 0.9, CAP_Z0), Vector(MOUNT_XW, 0.9, CAP_Z0 - 10))).Edges)
    P("  EbayCap W M2 x10: boss beside the pilot from the cap face down %.1f mm (tip at Z 40.3 needs >= 5.1)   %s" % (wl, "PASS" if wl >= 5.1 else "FAIL"))

    P("")
    P("[P] PIEZO SOLID BACK PLATE + Q1 (TO-92 flat on the back, at the pin end)")
    bear = vv(sled, box(PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)) / 0.1
    P("  board back bears on the plate: %.1f mm2 (v13 frame 78.0); 2 x M2 clamp the hole end   %s" % (bear, "PASS" if bear > 150 else "FAIL"))
    qz = box(*Q1_ZONE)
    P("  Q1 pocket x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f (%.0f mm3): sled inside %.2f mm3   %s"
      % (Q1_ZONE + (qz.Volume, vv(sled, qz), "PASS" if vv(sled, qz) < 0.01 else "FAIL")))
    thru = []
    for y in (PIEZO_Y1 - 0.3, PIEZO_Y1 - WINDOW_DY + 0.3, Q1_ZONE[2] + 0.3):
        for z in (PIEZO_Z0 + 1.5, PIEZO_ZC, PIEZO_Z1 - 1.5):
            thru.append(len(sled.common(Part.makeLine(Vector(PIEZO_PCB_X0 - 0.01, y, z), Vector(-3.0, y, z))).Edges) == 0)
    nc = len(sled.common(Part.makeLine(Vector(PIEZO_PCB_X0 - 0.01, 0.0, PIEZO_ZC + 3.0), Vector(-3.0, 0.0, PIEZO_ZC + 3.0))).Edges) > 0
    P("  through-opening behind the board's pin end: y %.1f..%.1f (the 2 mm strip y %.1f..%.1f + the TO-92 pocket), Z %.1f..top:"
      % (Q1_ZONE[2] - CL, PIEZO_Y1 + CL, PIEZO_Y1 - WINDOW_DY, PIEZO_Y1, OPEN_Z[0]))
    P("    %d / %d sight lines from the board back out to x -3 hit nothing; control line at y 0 hits the plate: %s   %s"
      % (sum(thru), len(thru), nc, "PASS" if all(thru) and nc else "FAIL"))
    pocket = box(PIEZO_PCB_X0 + 0.01, PIEZO_X1 + 0.5, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z1)
    P("  sled in front of the board: %.2f mm3   %s" % (vv(sled, pocket), "PASS" if vv(sled, pocket) < 0.01 else "FAIL"))
    pbay = pin_bay()
    P("  pin bay x %.1f..%.1f y %.1f..%.1f (v13 size less the v17 E rail column): sled inside %.2f mm3   %s" % (PIN_BAY + (vv(sled, pbay), "PASS" if vv(sled, pbay) < 0.01 else "FAIL")))

    P("")
    P("[X] HARNESS ROOM")
    jb = comp["JST_power"].BoundBox
    P("  ESP32 JST + battery plug x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f: over the pack top by %.1f, tray floor notched;"
      % (jb.XMin, jb.XMax, jb.YMin, jb.YMax, jb.ZMin, jb.ZMax, jb.ZMin - BATT_Z1))
    P("    sled in its keep-out before the trim %.2f mm3   %s" % (raw["JST_power"], "PASS" if raw["JST_power"] < 0.01 else "FAIL"))
    colm = box(-19.5, 19.5, ADXL_Y0 + ADXL_T, NANO_YT, NANO_Z0, NANO_Z1)
    cfree = clip_bore(colm, r=R_MAX_MOVING).cut(sled)
    for k in comp:
        cfree = cfree.cut(comp[k])
    P("  central column (y %.1f ADXL parts .. y %.1f ESP32 parts, Z %.1f..%.1f): %.0f mm3 free after S7V8F5 + cables"
      % (ADXL_Y0 + ADXL_T, NANO_YT, NANO_Z0, NANO_Z1, vol(cfree)))
    for sg, nm in ((1, "E"), (-1, "W")):
        xr = NANO_XC + sg * NANO_ROW
        lane = box(xr - 0.9, xr + 0.9, -19.5, NANO_YT, NANO_Z0 + 3.5, NANO_Z1 - 4.0)
        over = [(k, round(NANO_YF - sh.BoundBox.YMax, 1)) for k, sh in [("Sled", sled)] + list(comp.items())
                if k not in ("Nano_ESP32", "Nano_joints") and vv(sh, lane) > 0.01]
        P("  %s pad row (x %.2f), in front of the parts face: %s" % (nm, xr, "nothing to the far side" if not over else
          ", ".join("%s from %.1f mm" % o for o in over)))
    pts = [Vector(8.4, 12.2, -13.0), Vector(2.9, 12.2, -13.0), Vector(2.9, 12.2, -1.5)]
    pr = None
    for a, b in zip(pts[:-1], pts[1:]):
        c = Part.makeCylinder(1.0, (b - a).Length, a, b - a).fuse(Part.makeSphere(1.0, b))
        pr = c if pr is None else pr.fuse(c)
    hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + list(comp.items()) for v in [vv(sh, pr)] if v > 1e-2]
    P("  piezo pin leads: d2 probe pin bay (8.4, 12.2, -13) -> west under the buttress arch -> up to the ESP32 aft end (2.9, 12.2, -1.5): %s   %s"
      % ("clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    for nm, k in (("ADXL fwd -> BMP fwd", "Qwiic_ADXL_BMP"), ("BMP aft -> ESP32", "Qwiic_BMP_Nano"), ("battery lead", "Battery_lead")):
        P("  %-22s lane %s; sled in it %.2f mm3   %s" % (nm, "x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f" % tuple(
            getattr(comp[k].BoundBox, a) for a in ("XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax")), raw[k], "PASS" if raw[k] < 0.01 else "FAIL"))

    P("")
    P("[T] separation: ESP32 <-> battery %.1f mm (opposite sides), ESP32 <-> BMP388 %.1f mm"
      % (comp["Nano_ESP32"].distToShape(comp["Battery"])[0], comp["Nano_ESP32"].distToShape(comp["BMP388"])[0]))

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
    fwd = box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z1 + CL_BATT, BATT_Z1 + CL_BATT + 0.1)
    P("  aft face on %.1f mm2 of web tops (Z %.1f); fwd face under %.1f mm2 of the floor lip (split round the JST)   %s"
      % (vv(sled, aft) / 0.1, BATT_Z0 - CL_BATT, vv(sled, fwd) / 0.1, "PASS" if vv(sled, aft) / 0.1 > 20 and vv(sled, fwd) / 0.1 > 10 else "FAIL"))
    P("  SIDEWAYS zip tie (%.1f x %.1f) at Z %.2f..%.2f: %.1f below the pack's fwd end -- it is what holds the fwd end against -y"
      % (TIE_W, TIE_T, TIE_Z0, TIE_Z0 + TIE_W, BATT_Z1 - TIE_Z0 - TIE_W))
    P("    (aft end: webs + the tie's lever arm; outboard face 1 mm foam -> the bore once in the tube); Rmax %.2f"
      % rmax_mesh(cmesh["ZipTie"]))

    P("")
    P("[D9] FIT TO THE D9aft E-BAY (proxy + the REAL as-built v10 FwdTube, the v10 EbayCap raised %.0f mm, the D9aft v12 ring)" % RING_L)
    cav = cyl(D9_CREST, D9_BAND_Z, 70.0)
    cav = cav.fuse(Part.makeCone(D9_R_ID, D9_CREST, D9_R_ID - D9_CREST, Vector(0, 0, D9_BAND_Z - (D9_R_ID - D9_CREST))))
    cav = cav.fuse(cyl(D9_R_ID, D9_SEAT_Z, D9_BAND_Z - (D9_R_ID - D9_CREST) + 0.001))
    cav = cav.fuse(cyl(D9_SEAT_RI, D9_SEAT_Z - D9_SEAT_T, D9_SEAT_Z + 0.001))
    cav = cav.fuse(Part.makeCone(D9_SPIGOT_RI, D9_SEAT_RI, D9_SPIGOT_RI - D9_SEAT_RI, Vector(0, 0, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI))))
    cav = cav.fuse(cyl(D9_SPIGOT_RI, D9_SEAT_Z - 14.1, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI) + 0.001))
    tube = cyl(D9_R_OD, D9_SEAT_Z - 11.1, 60.8).cut(cav)
    tube = tube.cut(box(-20.45, -18.0, -1.5, 1.5, TUBE_GROOVE_Z0, 70.0))   # v20: the D9aft v3 cap-key groove at 180 deg (the sled key rides it)
    for nm, d, zp, a in D9_PORTS:
        tube = tube.cut(Part.makeCylinder(d / 2.0, 5.0, Vector(D9_R_ID - 1.0, 0, zp), Vector(1, 0, 0)).rotated(Vector(0, 0, 0), Vector(0, 0, 1), a))
    d9 = {}
    for k, fn in D9V10_STEP.items():
        sh = Part.Shape(); sh.read(fn); d9[k] = sh
    dz = CAP_Z0_V19 - d9["EbayCap"].BoundBox.ZMin                     # the v10 frame: tube by the OLD cap face
    for k in d9:
        d9[k].translate(Vector(0, 0, dz))
    d9["EbayCap"].translate(Vector(0, 0, RING_L))
    chk = [("FwdTube (proxy)", tube), ("FwdTube v10", d9["FwdTube"]), ("EbayCap v10 +%.0f" % RING_L, d9["EbayCap"])]
    if os.path.exists(D9V12_RING):
        rg = Part.Shape(); rg.read(D9V12_RING); rg.translate(Vector(0, 0, dz)); d9["Ring"] = rg
        chk.append(("Ring v12", rg))
        P("  ring v12 Z %.2f..%.2f (mouth face %.1f, spigot to %.2f)" % (rg.BoundBox.ZMin, rg.BoundBox.ZMax, TUBE_MOUTH_Z, rg.BoundBox.ZMin))
    else:
        P("  ring v12 STEP not built yet (run D9aft v12 first)   FAIL")
    for nm, part in chk:
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
    P("  sled (ABS, solid-equiv) %8.1f mm3   %5.1f g   (v10 17.4 g -> %+.1f g; v15 13.6 g, v13 13.7 g)" % (sled.Volume, m, m - 17.4))
    P("  fasteners: 2 x M2x6 (piezo), 1 x M2x10 (EbayCap W only), 1 mini zip tie (battery); ADXL glued in its pocket, BMP glued on its corners")
    dm = (m - 12.6) - 1.5 - 1.5 - 0.5
    dcg = -dm * (228.0 - 115.0) / (262.6 + dm)
    P("  CG (ESTIMATE vs the D9aft v10 rollup: 262.6 g, CG 228.0 from the tip, gate <= 226; e-bay at ~tip 115):")
    P("    sled %+.1f g, reed/microSD/card -3.5 g -> e-bay %+.1f g -> CG %+.1f mm -> ~%.1f: ~%.0f g EbayCap ballast to reach 226"
      % (m - 12.6, dm, dcg, 228.0 + dcg, (2.0 + dcg) / 0.6))
    P("    (+ the real solder / wire / heat shrink, never weighed).  WEIGH the built e-bay + line, re-run OpenRocket before flying.")

    P("")
    P("[V] STORAGE -- free volume inside R %.1f, deck floor to cap face, minus sled, parts and cable lanes" % R_MAX_MOVING)
    shell = cyl(R_MAX_MOVING, DECK_FLOOR, SPIGOT_Z[0]).fuse(cyl(SPIGOT_RI, SPIGOT_Z[0], TUBE_MOUTH_Z)).fuse(cyl(R_MAX_MOVING, TUBE_MOUTH_Z, CAP_Z0))
    fr = shell.cut(sled)
    for s in comp.values():
        fr = fr.cut(s)
    tot = sum(s.Volume for s in fr.Solids)
    P("  %s total free %.0f mm3" % (REV, tot))
    zones = [("central column (S7V8F5 in it)", box(-19.5, 19.5, ADXL_Y0 + ADXL_T, NANO_YT, NANO_Z0, CAP_Z0_V19), "wires, resistors, slack"),
             ("west strip (spine .. slot / ADXL)", box(-19.5, NX0 - REL_X - GW_T, TRAY_FACE, 19.5, NANO_Z0, CAP_Z0_V19), "wire slack"),
             ("aft deck (C1 in it)", box(-19.5, FRAME_X0, TRAY_FACE, GW_Y[1], DECK_FLOOR, NANO_Z0), "d10 can, resistors"),
             ("aft deck under the tray (between the webs)", box(-19.5, 19.5, -19.5, BATT_Y1, DECK_FLOOR, BATT_Z0 - CL_BATT), "flat parts"),
             ("over the pack's fwd end (JST + lead)", box(-19.5, 19.5, -19.5, TRAY_FACE, BATT_Z1, CAP_Z0_V19), "battery lead slack"),
             ("v20 CHAMBER below the spigot (Z 45.4..51.3, full bore)", box(-19.5, 19.5, -19.5, 19.5, CAP_Z0_V19, SPIGOT_Z[0]), "JUMPER SLACK"),
             ("v20 CHAMBER in the ring spigot (Z 51.3..61.4, R 17.95)", box(-19.5, 19.5, -19.5, 19.5, SPIGOT_Z[0], CAP_Z0), "JUMPER SLACK, taped inboard"),
             ("over the BMP (bore side)", box(BMP_X0 + BMP_PCB_T + BMP_PARTS, 19.5, -19.5, 19.5, BMP_Z0, BMP_Z1), "thin")]
    for nm, z, use in zones:
        P("    %-42s %6.0f mm3   (%s)" % (nm, vv(fr, z), use))
    P("  (v19 45289 mm3, v18 45048 mm3, v15 46250, v14 45144, v13 45667, v10 as built 40941)")

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
    P("  %d slender groups   (v13: 1)" % nk)

    P("")
    _ovh = {}
    exec(open(os.path.join(PROJECT, "Avionics", "avbay_overhang_audit.py"), encoding="utf-8").read(), _ovh)
    _ovh["overhang_audit"](sled, P, zbed=SEAT_Z)
    P("  v13: 9 regions, 70 mm2, reach 2.6;  v10: 31 regions, 389 mm2, reach 7.8;  v9 (spaghetti): 1230 mm2, reach 10.3")

    P("")
    P("[N] ASSEMBLY (sled in hand)")
    P("  1 C1 (+ resistors): drop it AXIALLY from the cap end down the centre into the aft deck (before the ESP32).")
    P("  2 ESP32, parts toward the centre, USB-C + JST at the cap end, battery plug OUT: slide it down its slot from the")
    P("    cap end (loose past the solder bulges) until its aft end drops into the tight cup (crush ribs = snug), pushed")
    P("    all the way down (v18: no heels); its wires ride down the column.  Optional: 1 mm foam tape on the back ribs takes up the top-end play.")
    P("  3 S7V8F5 flat on the ESP32's parts (Kapton).")
    P("  4 piezo (can out), 2 x M2x6; TO-92 in the pin-end pocket; pin leads go west under the buttress arch.")
    P("  5 ADXL375: GLUE its back flat on the tray floor's inboard face inside its corner pocket, plug fwd.")
    P("  6 BMP388: PCB back down on the tray's +x wall and the N web, both long edges between the S + N corner rails; glue.")
    P("  7 Qwiic: ADXL fwd -> under the JST -> BMP fwd plug; BMP aft plug -> along over the piezo to the ESP32's aft end.")
    P("  8 battery: slide it into the tray from the side (-y), 1 mm foam outboard, sideways mini zip tie at Z 31.4;")
    P("    lead over the pack top, plug into the ESP32's JST LAST (= ON).  Unplug it before pulling the battery.")
    P("  9 v20: fold the jumper slack into the chamber above the boards (Z 45.4..61.4); Kapton it INBOARD of R 17.5 above")
    P("    Z 51.3 (the ring's spigot screws down over that band).  Sled into the tube: KEY into the tube's groove at the")
    P("    old cap-key slot (180 deg, opposite the sound port) -- that clocks the piezo onto the sound port.")
    P(" 10 extension ring (D9aft v12): screw it into the tube mouth, hand tight onto the mouth face, holding the sled")
    P("    top still so the slack doesn't wind.  Tape over the ring / tube seam for flight.")
    P(" 11 EbayCap: into the ring, W M2x10 into the post (east hole taped).  Its key tab must drop into the ring's wide slot (+-15 deg):")
    P("    if it doesn't, back the ring off (at most ~1/12 turn) until it does.  NEVER trim the tab: it locks the ring.")
    P(" 12 nose: screw into the ring -- HOLD THE RING while turning the nose (on and off) so the ring doesn't back out.")
    P("  REMOVAL: nose off -> M2 out -> cap out -> ring off -> sled out (the cap can't pass the ring's spigot bore).")
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

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v7  (the "scaffold to screw
the chips into").

v7 = v6 with the PIEZO MOUNTED SIDEWAYS (2026-10-07, user: drop the standoffs, keep the
screws; "can't we mount it sideways instead?").  The module is a KY-006-style buzzer
(photo): 3-pin right-angle header on the CAN side at one short edge, pins running past
that edge in the board plane ("front and down"); they get bent + heat-shrunk.  In v6
that edge sat ON the deck floor -- no room for the pins at all.
  * Board turned 90 deg in its own plane: 19 along y (tangential), 15 along Z.  Can still
    faces +x onto the sound port, can centre kept at y 0 / Z PIEZO_ZC = the D9aft v6 port.
  * Holes at the -y end, pins at the +y end -> the pins come out NORTH into an open PIN
    BAY (x 10..bore, y 9.5..~16) -- no +y side wall over the board height, mid-ring web at
    45 deg dropped.  Checked free in [P].
  * NO STANDOFFS: the PCB back sits FLAT on the back plate (plate face = PCB back, x 8.4).
    The back-side solder joints (header + can leads) get a 1.4 mm RELIEF cut into the plate
    instead; only the hole end (y < -5) and the long edges bear.  Nothing of the sled
    stands proud into the pocket ([P] checks it).
  * SCREWS KEPT: 2 x M2 from +x through the board into the plate (2.6) + the 2 mm blocks
    behind it (on the small-parts side, not in the pocket) -> ~4.6 mm of thread.
  * Board is 15 tall now (was 19): 2.0 mm free under it, 2.6 over it.  E-BAY LENGTH, seat
    plane, sound port, EbayCap, static port, reed: ALL UNCHANGED vs v6 -> D9aft v6 fits
    as printed; checked against its STEP files in [D9].
  * Under-tray east web shortened to stop at the new -y pocket wall.

v6 =v5 made sturdier, looser and longer (2026-10-06, user: "v4 broke handling / slotting
the chips in" -- the BATTERY TRAY; "rotate the piezo 90 deg so holes and output match";
"you may lengthen the e-bay -- use the extra space"):
  * BATTERY TRAY: the v4/v5 cavity was cut to the EXACT pack size (zero clearance) and
    windowed with 0.8 walls.  Now 0.5 clearance per face (x, z), 1.2 walls, 1.8 end caps,
    no windows, an outside gusset on the east wall root, and 2 ribs over the fwd end cap
    tying it to the reed rail / top beam.  Wall thickness is now MEASURED in the report [W].
  * CLEARANCES: every board slot / groove 0.4 per face (CL_SLOT); the Nano had none in x.
    Nano ledge kept at 0.3 so the ADXL slot stays 4.7.  WALL 0.9 -> 1.2 (3 perimeters).
    ADXL rails 1.4 -> 1.8, groove lips thickened.
  * PIEZO ROTATED 90 deg about Z: board in the y-z plane, can facing +x onto the sound port,
    screws along x through the measured holes from +x into standoffs behind the board.
    15 wide it does not fit the old east slot -> a new AFT DECK below the old Z 0.
  * AFT DECK (e-bay grows aft by DECK_DZ; everything above Z 0 keeps its v5 coordinates):
    floor disc (prints on the bed), spine run down, N + S ribs, piezo pocket east with a
    2 mm roof that ties into the mid ring (the old foot ring), and the SMALL-PARTS BAY
    (regulator, microSD, C1, switches, wiring) moved down into its free west/centre.
    The old 3 mm upper shelf is gone -> upper centre is free wiring room.
  * sled.isValid() asserted after build and heal (v5 lost 790 mm3 silently to a tangency).
  * D9aft NOT touched: the seat, sound port and length change are PROPOSED here ([L]).

v5 = v4 with the board HOLES the user measured (2026-10-06).  Measurements are
approximate (user: "not 100 % accurate"); edge distances read as hole EDGE -> board
edge, so centre = edge distance + d/2.  Nothing else moved.
  * BMP388  4 x d3.0, 0.5 from the edges -> centres 2.0 in from each edge:
    pitch 18 (y) x 36 (z) on a 22 x 40 PCB (was d2.5, 16 x 34 ASSUMED).  The PCB
    length is taken as the full 40 envelope (Qwiic bodies sit on the board) -- CONFIRM.
    Screws stay M2.5 (d3 board hole = clearance); bosses/pilots sized to the screw.
  * ADXL375 4 x d3.0, 1.5 from the edges -> centres 3.0 in: 12 x 20 on 18 x 26.
    Still rail-held, NO screws (0.4 mm to the Nano).  Recorded + checked against the
    rail grooves only (the groove must not reach a hole).
  * PIEZO breakout: 2 holes "up top", DIFFERENT sizes:
      d2.5 -- 0.75 from the top edge, 0.5 from its long edge
      d3.0 -- 0.75 from the top edge, 0.75 from the other long edge
    on the 11 x 19 breakout (PIEZO_DT x PIEZO_DZ).  Which long edge carries which
    hole is ASSUMED (d2.5 at -y).  Both take M2 (was 2 x d2 at y +/-4, Z 16).
  * ADXL rail driver notch follows the BMP's upper-y screw (was hard-coded y 8, Z 3).

v4 = v3 repacked (2026-10-01):
  * BMP388 (40 x 22 x 4 incl. Qwiic plugs) moved AWAY FROM THE NANO: west lane, board
    on edge (y-z plane) against the spine, 4 x M2.5 into standoffs in the spine,
    sensor side facing the axis.  Was 0.5 mm off the Nano; see [T].  Only the y +8
    pair can be reached by a driver -> 2 screws + 2 rest pads + Kapton; see [S].
  * ADXL375 (measured < 30 mm long WITH its Qwiic plug in) takes the BMP's old slot:
    north, inboard of the Nano, long axis along Z as before (no axis remap).  It slides
    into two grooved edge rails from the top; the rail tops are the Nano's backing
    ledge.  No screws: there is no room for heads between it and the Nano (0.4 mm).
    SmallParts -> the freed upper centre.
  * BATTERY TRAY OPENS OUTBOARD (to the tube wall): drop the pack in with the e-bay out,
    one axial zip tie (+/- Kapton) holds it; in the tube the bore backs it up.  JST lead
    exits the FWD end (-x corner).  v1..v3 trays could not be loaded at all.
  * Nano pocket gets a real full-length backing wall (the BMP is gone from under it).
  * OPENED UP: windows in the tray floor + side walls; the Nano backing wall is gone
    (rails + ADXL-rail ledge instead).  Frame members (spine, ring, beam, bosses) solid.  Top frame: W boss (D-shaped, clears the BMP's
    Qwiic cable) + cross-beam + E boss + a bar to the Nano pocket.
  * D9aft interfaces unchanged: Zmin -0.9, spine key, M2 boss (x, y, top Z 45.4),
    piezo at Z 9.5 / 0 deg.  ADXL_CLEAR_Z now = the ADXL top (D9aft clips with it).


v3 = v2 fitted to the D9aft v2 e-bay (Models/AFT_DEPLOY_D9_v2.md) (2026-09-30):
  * REED MODULE replaces the bare capsule: KY-021-style board (PCB ~18.5 x 15, 3-pin
    right-angle header, glass capsule on bent leads beside the far edge).  It slides
    radially (from +x) into two printed edge rails in the space the servo freed, the
    capsule axial and 1 mm off the skin at ~-11 deg, next to the witness notch.  v2's
    south-wall saddle is gone.  Module dims ASSUMED -- measure (RM_* constants).
  * SEAT FOOT: a full ring R 15.8..19.3 at Z -0.9..0 so the sled bears flat on the
    D9aft seat ring (flat top R 15.5..20) instead of on scattered pocket bottoms.
  * [D9] checks against the real e-bay: FwdTube bore/seat/crest proxy built from the
    D9aft v2 constants (+ its ports), and the exported D9aft v2 EbayCap STEP.
  * Nothing moved that the D9aft v2 parts depend on: Zmin -0.9 (seat), spine key,
    M2 bosses (x, y, top Z 45.4), piezo sound hole at Z 9.5 / 0 deg.

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
REV = "v7"
RHO = 1.05e-3                 # ABS ~100% infill, g/mm^3

# --- airframe ---
R_AF_I = 20.0                 # ID 40.0
R_MAX_MOVING = 19.5           # anything that slides in/out of the bore
SLED_RMAX = 19.39             # sled outer envelope (v2 value, kept)

# --- FDM fit clearances (ABS, 0.4 mm nozzle) -- same block as the ejection POC ---
CL_SLIDE = 0.50
CL_REG   = 0.20
CL_BOARD = 0.30   # Nano ledge offset (a rest face, not a slot -- kept so the ADXL slot stays 4.7)
CL_SLOT  = 0.40   # v6: every board slot / groove / side pocket face (v4/v5 0.3, Nano x 0)
CL_BATT  = 0.50   # v6: battery cavity, per face in x and z (v4/v5: exact pack size)
WALL     = 1.20   # nominal sled pocket wall (v4/v5 0.9 = 2 perimeters; 1.2 = 3)
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

# BMP388 40x22x4 (Qwiic plug bodies incl.) -- WEST lane, on edge: 4 thick along x,
#   22 along y, 40 along Z.  PCB back face on the -x side, parts + Qwiic on +x.
#   Standoffs behind it grow out of the spine; screws from +x (heads on the PCB).
BMP_T, BMP_W, BMP_L = 4.0, 22.0, 40.0     # x . y . z
BMP_X0 = -15.5                            # PCB back face
BMP_Z0 = 0.0
BMP_PCB_T = 1.6
BMP_HOLE_D     = 3.0                      # board hole, MEASURED (v4: 2.5 assumed)
BMP_HOLE_EDGE  = 0.5                      # hole edge -> board edge, MEASURED
BMP_PCB_L      = BMP_L                    # PCB length = full envelope (CONFIRM)
BMP_SCREW_D    = 2.5                      # M2.5 through the d3 hole; sizes boss + pilot
BMP_HOLE_IN    = BMP_HOLE_EDGE + BMP_HOLE_D / 2.0           # 2.0 centre -> edge
BMP_HOLE_PY = BMP_W - 2.0 * BMP_HOLE_IN                     # 18.0
BMP_HOLE_PZ = BMP_PCB_L - 2.0 * BMP_HOLE_IN                 # 36.0
BMP_BOSS_MARGIN = 1.5                     # boss r = screw r + this (1.4 was tangent to the bore at y 9)
BMP_STANDOFF = 1.5                        # back face -> spine (bore-limited at y +/-9 in v5)

# BATTERY 40.5x20x8.5 -- south, alone, pulled in 0.7 from the v2 corner -----
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_Z0 = 0.4                             # 0.4 up: the zip-tie wrap (+clearance) stays above the seat plane
BATT_WALL = 1.2                           # v6 (v5 0.8, windowed -- it broke loading the pack)
BATT_END = 1.8                            # v6: end caps
BATT_GUSSET = 2.0                         # v6: 45 deg outside gusset, east wall root
BATT_RIB_X = ((2.6, 3.8), (7.6, 8.8))     # v6: ribs over the fwd end cap, clear of JST (-x) and tie (x~0)
JST_SLOT_W = 6.0                          # FWD end, -x corner
JST_PLUG = (6.0, 4.5, 4.3)                # JST-PH plug + lead bend, x . y . z (est.)
TIE_W, TIE_T = 2.5, 1.0                   # mini zip tie band
TIE_CL = 0.25
TIE_XC = 0.2                              # clear of the reed solder stubs (-x) and the piezo pocket (+x)

# ADXL375 -- north, inboard of the Nano (the BMP's v1..v3 slot), long axis along Z.
#   Measured by the user: < 30 mm long with the Qwiic plug in.  PCB 26 x 18 (v3),
#   plug at the FWD end + 3 mm for the cable to bend.  PCB edges slide down into
#   grooves in two rails; the rail tops carry the Nano.  Wire the I2C bus as a STAR
#   at the Nano: ADXL and BMP use one plug each (their fwd ends).
ADXL_W, ADXL_T, ADXL_L = 18.0, 4.5, 30.0  # x . y (incl. plug height + back joints) . z (incl. plug)
ADXL_PCB_L, ADXL_PCB_T = 26.0, 1.6
ADXL_Y0 = 6.5                             # back-side joints (piezo pocket roof is 6.4)
ADXL_PCB_Y0 = 7.0
ADXL_Z0 = 0.0
ADXL_EDGE = 0.8                           # component-free PCB edge that runs in the groove
ADXL_PLUG_W = 8.0                         # plug + cable width (est.)
ADXL_BEND = 3.0                           # cable bend room past the plug
ADXL_RAIL = 1.8                           # rail outboard of the PCB edge (v6: 1.4 -> 1.8)
ADXL_LIP_Y = 0.6                          # v6: rail runs this far below ADXL_Y0 (groove lip 0.3 -> 0.7)
ADXL_CLEAR_Z = ADXL_Z0 + ADXL_L + ADXL_BEND   # name kept for D9aft (it clips the envelope at this Z)
ADXL_HOLE_D    = 3.0                      # MEASURED; unused for retention (rails, no screws)
ADXL_HOLE_EDGE = 1.5                      # hole edge -> board edge, MEASURED
ADXL_HOLE_IN   = ADXL_HOLE_EDGE + ADXL_HOLE_D / 2.0         # 3.0
ADXL_HOLE_PX = ADXL_W - 2.0 * ADXL_HOLE_IN                  # 12.0
ADXL_HOLE_PZ = ADXL_PCB_L - 2.0 * ADXL_HOLE_IN              # 20.0

# PIEZO 19x15x11 -- v6: ROTATED 90 deg about Z (user) so holes and output line up:
#   11 RADIAL x 15 tangential x 19 axial.  PCB in the y-z plane on the inboard side, can
#   facing +x (outboard) onto the sound port; 2 screws along x from +x (heads on the can
#   side, driven with the e-bay out of the tube) into standoffs behind the PCB.
#   Lives in the AFT DECK (below the old Z 0).
DECK_Z1 = BATT_Z0 - CL_BATT - BATT_END - 0.1                 # -2.0: deck ceiling, under the battery tray
# FROZEN to D9aft v6 (it was built on sled v6): seat plane and sound-port Z are the v6
# values, derived exactly as v6 did (v6 board 19 tall, 0.6 under the deck ceiling).
_V6_PIEZO_Z0 = DECK_Z1 - 0.6 - 19.0                          # -21.6
SEAT_Z = _V6_PIEZO_Z0 - WALL                                 # -22.8: sled Zmin / seat plane (= v6)
DECK_DZ = -0.9 - SEAT_Z                                      # e-bay growth vs v5 (Zmin -0.9) (= v6)
PIEZO_ZC = _V6_PIEZO_Z0 + 19.0 / 2.0                         # -12.1: can / sound output centre (= v6 port)
# PIEZO 19x15x11 KY-006 style -- v7: SIDEWAYS.  11 RADIAL x 19 tangential (y) x 15 axial (Z).
#   PCB in the y-z plane, back face flat on the back plate, can facing +x onto the sound
#   port.  Hole end at -y, header/pin end at +y.  2 x M2 from +x (e-bay out).
PIEZO_DR, PIEZO_DL, PIEZO_DZ = 11.0, 19.0, 15.0
PIEZO_PCB_T = 1.6
PIEZO_PCB_X0 = 8.4                        # PCB back face = back-plate face (v6 value)
PIEZO_X1 = PIEZO_PCB_X0 - 1.4 + PIEZO_DR  # 18.0: can face (= v6)
PIEZO_CAN_D = 12.5                        # round transducer (ASSUMED)
PIEZO_CAN_OFF = 0.0                       # can centre -> board centre along y, toward the hole end (ASSUMED 0: MEASURE)
PIEZO_Y0 = -PIEZO_DL / 2.0 - PIEZO_CAN_OFF                   # hole-end edge (can stays at y 0)
PIEZO_Y1 = PIEZO_Y0 + PIEZO_DL                               # pin-end edge
PIEZO_Z0 = PIEZO_ZC - PIEZO_DZ / 2.0                         # -19.6 (2.0 above the floor)
PIEZO_JOINT_T = 1.4                       # back-side solder joints (ASSUMED) = plate relief depth
PIEZO_JOINT_Y0 = 4.5                      # joints start this far from the hole end (ASSUMED)
PIEZO_JOINT_EDGE = 1.0                    # ... and keep the long (Z) edges free this wide (ASSUMED)
# right-angle header on the CAN side at the pin end, pins in the board plane past the edge (ASSUMED from the photo)
PIEZO_HDR = (2.5, 2.5, 7.6)               # body: x above the PCB front . y in from the edge . z
PIEZO_PIN_X = (0.95, 1.6)                 # pin band above the PCB front (as the KY-021 reed)
PIEZO_PIN_L = 6.0                         # straight pins past the board edge (they get bent)
PIEZO_PIN_Z = 5.7                         # 3 pins @ 2.54, centred on the board (ASSUMED)
PIN_BAY_Y = 7.0                           # free bay past the pin end for the bend + heat shrink
PIEZO_PLATE_X0 = PIEZO_PCB_X0 - PIEZO_JOINT_T - WALL        # 5.8: back of the back plate (= v6)
PIEZO_BOSS_BACK = 2.0                     # block behind the back plate -> ~4.6 mm of thread
DECK_RIB_W = 8.0                          # N + S deck ribs (tangential width)
#   2 holes at the -y end (v5/v6 "top"), MEASURED, different sizes:
#   (board hole d, edge->end, edge->its long side, side sign in Z).  Which long side
#   carries which hole is ASSUMED (d2.5 aft).
PIEZO_SCREW_D = 2.0                       # M2 in both
PIEZO_HOLE_SPEC = ((2.5, 0.75, 0.50, -1),
                   (3.0, 0.75, 0.75, +1))
PIEZO_HOLE_LIST = [(PIEZO_Y0 + dt + d / 2.0, PIEZO_ZC + sz * (PIEZO_DZ / 2.0 - ds - d / 2.0), d)
                   for d, dt, ds, sz in PIEZO_HOLE_SPEC]      # (y, z, board d)
PIEZO_HOLES = len(PIEZO_HOLE_LIST)

# REED MODULE (KY-021 style) -- ALL DIMS ASSUMED from the product photo: MEASURE.
#   Local frame of the module: PCB in the x-z plane, x = 0 at the header edge,
#   x = RM_PCB_L at the reed edge; header + R1 on the +y (top) side.
#   Placed: board plane y RM_Y0..RM_Y0+T (top side toward the axis), reed edge
#   outboard at +x (east), capsule axial (along Z) 1 mm off the skin.  Slides in
#   radially from +x between an aft and a fwd edge rail; stop at the header edge.
RM_PCB_L, RM_PCB_W, RM_PCB_T = 18.5, 15.0, 1.6   # x (radial) . z (axial) . y
RM_CAP_D, RM_CAP_L = 2.2, 14.0            # glass capsule
RM_CAP_OFF = 2.5                          # reed edge -> capsule axis, in-plane
RM_CAP_DY = RM_PCB_T                      # capsule axis this far above the PCB bottom face
RM_HDR = (2.5, 2.5, 7.6)                  # header body x . y (above top face) . z
RM_PIN_L = 6.0                            # right-angle pins beyond the header edge
RM_PIN_Y = (0.95, 1.6)                    # pin band above the top face
RM_PIN_Z = 5.7                            # 3 pins @ 2.54
RM_STUB = 1.5                             # solder stubs below the bottom face
RM_LEAD_Z = 1.0                           # lead loops (pressed flat) past each board edge
RM_Y0 = -4.3                              # PCB bottom face.  v6: -5.0 -> -4.3 so the stubs end ON the 1.2
                                          #   tray floor (-5.8) and the zip tie's inboard leg fits between
RM_CAP_RC = 17.9                          # capsule axis radius -> glass outer R 19.0
RM_Z0 = 26.3                              # PCB aft edge: header clears the ADXL pocket (Z 26)
RM_RAIL_ENG = 1.0                         # PCB edge engagement in each rail
RM_MASS = 1.5                             # est. (PCB + header + reed)
RM_YC = RM_Y0 + RM_CAP_DY
RM_XC = math.sqrt(RM_CAP_RC ** 2 - RM_YC ** 2)
RM_X1 = RM_XC - RM_CAP_OFF                # PCB reed edge
RM_X0 = RM_X1 - RM_PCB_L                  # PCB header edge

# D9aft v2 e-bay, in THIS frame (sled Z = D9 z - 279.2 = 60.8 - station).  Copied
# from Models/PhoenixABS40-43_D9aft_v2.py -- keep in step with it.
D9_DZ = 279.2
D9_R_ID, D9_R_OD = 20.0, 21.5
D9_CREST = 19.65                          # female thread crests: the e-bay lifts out through these
D9_BAND_Z = 60.8 - 12.5                   # crest band ends (bore d39.30 above, 45 deg to d40)
D9_SEAT_Z, D9_SEAT_RI, D9_SEAT_T = SEAT_Z, 15.5, 2.0      # v6: PROPOSED -- seat moved aft by DECK_DZ
D9_SPIGOT_RI = 18.5
D9_PORTS = (("static", 1.5, 30.0, 0.0), ("sound", 3.0, PIEZO_ZC, 0.0))   # name, d, Z, ang (v6: sound port PROPOSED)
D9_EBAYCAP = os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v2_EbayCap.step")
D9V6_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v6_%s.step" % k)) for k in ("EbayCap", "FwdTube"))
FOOT_RI, FOOT_RO = 15.8, 19.3             # v6: floor disc R at SEAT_Z; mid ring (old foot) R 15.8..19.3

# SMALL PARTS ~13 g -- v6: the AFT DECK's free west/centre (was a 3 mm shelf in the upper
#   centre).  Regulator, microSD reader, C1, SW1/SW2 + wiring; Kapton / hot glue to the floor.
SP_X0, SP_X1 = -15.6, PIEZO_PLATE_X0 - PIEZO_BOSS_BACK - 0.5
SP_Y0, SP_Y1 = -9.0, 9.0
SP_Z0, SP_Z1 = SEAT_Z + WALL, DECK_Z1 - 0.3

# screwdriver used for the access sweep
DRIVER_D = 3.0                            # M2.5 = #1 Phillips / 1.5 hex: <= 3 mm shaft

# top frame
MOUNT_W_Z0 = 40.9                         # W boss starts above the BMP (Z 40) ...
MOUNT_W_XCUT = -13.4                      # ... D-cut on +x: room for the BMP's Qwiic cable to bend
BEAM_Y = 1.5

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
    if len(s) == 1:
        return s[0]
    f = s[0].multiFuse(s[1:])      # v4: keep EVERY piece -- the old .Solids[0] silently dropped
    return f.Solids[0] if len(f.Solids) == 1 else f   # disjoint ones (v1 Nano pocket, v4 Nano rail)

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
        log.append("  ! %s: removeSplitter skipped (%s) -- coplanar faces left unmerged" % (tag, exc))
    shape = as_solid(shape)
    shape.fixTolerance(1e-7)
    log.append("  heal %-14s faces %3d -> %3d, solids %d, %10.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape

def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.3, Relative=False)

def rmax_mesh(m):
    return max(math.hypot(v.x, v.y) for v in m.Points)

def clip_bore(shp, z0=SEAT_Z - 1.0, z1=None):
    return shp.common(cyl(SLED_RMAX, z0, z1 if z1 is not None else ZONE_Z1 + 5.0))

# ================================================================ component envelopes
def env_nano():
    return box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, NANO_Y0 + NANO_DY, NANO_Z0, NANO_Z0 + NANO_DZ)

def env_bmp():
    return box(BMP_X0, BMP_X0 + BMP_T, -BMP_W / 2.0, BMP_W / 2.0, BMP_Z0, BMP_Z0 + BMP_L)

def env_batt():
    return box(-BATT_DX / 2.0, BATT_DX / 2.0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0, BATT_Z0 + BATT_DZ)

def env_adxl():
    """PCB (full width) + parts (edge strips kept clear) + fwd plug + cable bend"""
    hw, ht = ADXL_W / 2.0, ADXL_Y0 + ADXL_T
    s = box(-hw, hw, ADXL_PCB_Y0, ADXL_PCB_Y0 + ADXL_PCB_T, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    s = s.fuse(box(-hw + ADXL_EDGE, hw - ADXL_EDGE, ADXL_Y0, ht, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L))
    s = s.fuse(box(-ADXL_PLUG_W / 2.0, ADXL_PLUG_W / 2.0, ADXL_PCB_Y0, ht, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 + ADXL_L + ADXL_BEND))
    return as_solid(s.removeSplitter())

def env_piezo():
    """v7 sideways KY-006: PCB (y-z plane, 19 along y) + can facing +x + back-side joints
    (in the plate relief) + header body and STRAIGHT pins past the +y edge (as delivered;
    the bend + heat shrink goes in the pin bay, checked in [P])."""
    y0, y1, z0, z1 = PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z0 + PIEZO_DZ
    xf = PIEZO_PCB_X0 + PIEZO_PCB_T                            # PCB front (can side)
    s = box(PIEZO_PCB_X0, xf, y0, y1, z0, z1)
    s = s.fuse(cyl_x(PIEZO_CAN_D / 2.0, xf, PIEZO_X1, 0.0, PIEZO_ZC))
    s = s.fuse(box(PIEZO_PCB_X0 - PIEZO_JOINT_T, PIEZO_PCB_X0, y0 + PIEZO_JOINT_Y0, y1,
                   z0 + PIEZO_JOINT_EDGE, z1 - PIEZO_JOINT_EDGE))
    hz = PIEZO_HDR[2] / 2.0
    s = s.fuse(box(xf, xf + PIEZO_HDR[0], y1 - PIEZO_HDR[1], y1, PIEZO_ZC - hz, PIEZO_ZC + hz))
    s = s.fuse(box(xf + PIEZO_PIN_X[0], xf + PIEZO_PIN_X[1], y1, y1 + PIEZO_PIN_L,
                   PIEZO_ZC - PIEZO_PIN_Z / 2.0, PIEZO_ZC + PIEZO_PIN_Z / 2.0))
    return as_solid(s.removeSplitter())

def pin_bay():
    """free volume past the pin end for the bent pins + heat shrink (NOT a part: [P] checks
    the sled leaves it empty).  Floor to the board top, PCB back to the bore."""
    return clip_bore(box(PIEZO_PCB_X0, SLED_RMAX + 1.0, PIEZO_Y1, PIEZO_Y1 + PIN_BAY_Y,
                         SEAT_Z + WALL, PIEZO_Z0 + PIEZO_DZ))

def env_tie():
    """zip-tie channel (keep-out incl. clearance): one axial loop round the battery at x ~0"""
    x0, x1 = TIE_XC - TIE_W / 2.0 - TIE_CL, TIE_XC + TIE_W / 2.0 + TIE_CL
    yo, yi = BATT_Y1 - BATT_DY, BATT_Y1                       # battery outboard / inboard faces
    z0, z1 = BATT_Z0, BATT_Z0 + BATT_DZ
    t = TIE_T + TIE_CL
    s = box(x0, x1, yo - t, yo, z0 - t, z1 + t)               # outboard leg (head goes here)
    yf = yi + BATT_WALL                                       # v6: leg runs on the floor's inboard face
    s = s.fuse(box(x0, x1, yf, yf + t, z0 - t, z1 + t))       # inboard leg (v4/v5 ran THROUGH the floor -> slit)
    s = s.fuse(box(x0, x1, yo - t, yf + t, z0 - t, z0))       # aft wrap (through the cap clearance + 0.75 of cap)
    s = s.fuse(box(x0, x1, yo - t, yf + t, z1, z1 + t))       # fwd wrap
    return as_solid(s.removeSplitter())

def env_jst():
    x0 = -BATT_DX / 2.0
    return box(x0, x0 + JST_PLUG[0], BATT_Y1 - BATT_DY / 2.0 - JST_PLUG[1] / 2.0, BATT_Y1 - BATT_DY / 2.0 + JST_PLUG[1] / 2.0,
               BATT_Z0 + BATT_DZ, BATT_Z0 + BATT_DZ + JST_PLUG[2])

def env_small():
    return box(SP_X0, SP_X1, SP_Y0, SP_Y1, SP_Z0, SP_Z1)

def env_reed():
    """KY-021-style module: PCB + header body + pins + solder stubs + capsule + leads."""
    top = RM_Y0 + RM_PCB_T
    zc = RM_Z0 + RM_PCB_W / 2.0
    s = box(RM_X0, RM_X1, RM_Y0, top, RM_Z0, RM_Z0 + RM_PCB_W)
    s = s.fuse(box(RM_X0, RM_X0 + RM_HDR[0], top, top + RM_HDR[1], zc - RM_HDR[2] / 2.0, zc + RM_HDR[2] / 2.0))
    s = s.fuse(box(RM_X0 - RM_PIN_L, RM_X0, top + RM_PIN_Y[0], top + RM_PIN_Y[1], zc - RM_PIN_Z / 2.0, zc + RM_PIN_Z / 2.0))
    s = s.fuse(box(RM_X0 + 0.6, RM_X0 + 1.9, RM_Y0 - RM_STUB, RM_Y0, zc - RM_PIN_Z / 2.0, zc + RM_PIN_Z / 2.0))
    cz0, cz1 = zc - RM_CAP_L / 2.0, zc + RM_CAP_L / 2.0
    s = s.fuse(cyl(RM_CAP_D / 2.0, cz0, cz1, RM_XC, RM_YC))
    # leads: from the PCB edge pads out to the capsule, pressed flat, a little past each board edge
    lz0, lz1 = RM_Z0 - RM_LEAD_Z, RM_Z0 + RM_PCB_W + RM_LEAD_Z
    s = s.fuse(box(RM_X1 - 1.5, RM_XC, RM_YC - RM_CAP_D / 2.0, RM_YC + RM_CAP_D / 2.0, lz0, lz1))
    s = s.fuse(cyl(RM_CAP_D / 2.0, lz0, lz1, RM_XC, RM_YC))
    return as_solid(s.removeSplitter())

COMPONENTS = [
    ("Nano_ESP32",  env_nano),
    ("BMP388",      env_bmp),
    ("Battery",     env_batt),
    ("ADXL375",     env_adxl),
    ("Piezo",       env_piezo),
    ("ReedModule",  env_reed),
    ("JST_PH",      env_jst),
    ("ZipTie",      env_tie),
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


def standoff_x(holes, board_back_x, hole_d, standoff, margin=1.4):
    """Bosses behind a board lying in a y-z plane (back face at board_back_x, facing -x);
    screws go in from +x.  Returns (bosses, pilots)."""
    out, drill = None, []
    for (hy, hz) in holes:
        b = Part.makeCylinder(hole_d / 2.0 + margin, standoff + 0.6, Vector(board_back_x - standoff - 0.6, hy, hz), Vector(1, 0, 0))
        out = b if out is None else out.fuse(b)
        drill.append(Part.makeCylinder(hole_d / 2.0 - 0.2, 12.0, Vector(board_back_x - 10.0, hy, hz), Vector(1, 0, 0)))
    return out, drill


def windows(shape, cutters):
    for c in cutters:
        shape = shape.cut(c)
    return shape


def build_sled(log):
    """One printed piece.  A frame (spine, foot ring, top beam + bosses) carrying the
    board pockets; big plates windowed.  v4 repack -- see the header."""
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)     # everything but the spine key stops under the cap

    # ---- spine down the west side -- SOLID (main west load path; clipped to the bore it is
    #      only full thickness for |y| < ~4).  Its top (Z > CAP_Z0) keys into the EbayCap.
    #      Two driver holes for the piezo screws (piezo goes in first).
    parts.append(clip_bore(box(-19.0, -16.6, -12.0, 12.0, SEAT_Z, ZONE_Z1 - 0.6)))   # v6: down to the deck floor
    by, bz = BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0

    # ---- BMP388 on edge against the spine: 4 standoffs out of the spine, screws from +x.
    #      Only the upper-y pair (v5: y +9) is reachable by a driver (see [S]); the lower-y pair are
    #      rest pads (no pilot) and the -y edge gets Kapton to the tray wall.
    bh = [(sy * by, bz + sz * BMP_HOLE_PZ / 2.0) for sy in (-1, 1) for sz in (-1, 1)]
    # v5: at y +/-9 a 1.4 margin puts the boss rim at r 19.390 = SLED_RMAX -- an exact
    #     tangency with the bore clip that left the sled INVALID (+790 mm3, heal -> 0
    #     solids).  BMP_BOSS_MARGIN makes the rim cross the clip cleanly instead.
    bm, bd = standoff_x(bh, BMP_X0, BMP_SCREW_D, BMP_STANDOFF, BMP_BOSS_MARGIN)
    parts.append(cap(as_solid(bm)))
    drill += [d for d, (hy, hz) in zip(bd, bh) if hy > 0]
    # v5: at y +9 a d3 driver (y 7.5..10.5) nicks the inboard edge of the Nano's west
    #     rails (y 10.3, BOTH: the driver crosses the bay) -- a relief through both at each driven screw.
    drill += [Part.makeCylinder(DRIVER_D / 2.0 + 0.3, 24.0, Vector(-13.0, hy, hz), Vector(1, 0, 0))
              for (hy, hz) in bh if hy > 0]

    # ---- Nano: side rails + 0.6 lip tabs + Kapton.  No backing wall: the Nano's inboard
    #      face rests on the ADXL rail tops (0.3 below it); the ADXL itself is 0.4 below.
    nin, nout = NANO_Y0, NANO_Y0 + NANO_DY                    # inboard 11.5 / outboard 16.5
    ntop = min(NANO_DZ + WALL, CAP_Z0)
    wy0, wy1 = nin - CL_BOARD - WALL, nin - CL_BOARD          # 10.3 .. 11.2 (rail root / ledge top)
    nx = NANO_DX / 2.0 + CL_SLOT                              # v6: side clearance (was 0)
    nano = box(-nx - WALL, -nx, wy0, nout, -WALL, ntop)
    nano = nano.fuse(box(nx, nx + WALL, wy0, nout, -WALL, ntop))
    for zc in (5.0, NANO_DZ / 2.0, NANO_DZ - 5.0):
        for xa, xb in ((-nx - WALL, -NANO_DX / 2.0 + 1.6), (NANO_DX / 2.0 - 1.6, nx + WALL)):
            nano = nano.fuse(box(xa, xb, nout, nout + LIP, zc - 2.5, zc + 2.5))
    parts.append(cap(as_solid(nano)))

    # ---- ADXL: two grooved edge rails, open at the top (slide the board down), floor at
    #      Z -0.9.  Rail tops = Nano ledge.  Gap at Z 1.2..4.8 lets a driver reach the
    #      BMP's aft upper-y screw (v5: y 9, Z 2).  Kapton over the plug end holds it down.
    hw = ADXL_W / 2.0
    for sx in (-1, 1):
        xa, xb = sorted((sx * (hw - ADXL_EDGE), sx * (hw + ADXL_RAIL)))
        rl = box(xa, xb, ADXL_Y0 - ADXL_LIP_Y, wy1, -WALL, ADXL_Z0 + ADXL_PCB_L)
        ga, gb = sorted((sx * (hw - ADXL_EDGE - 0.01), sx * (hw + CL_SLOT)))
        rl = rl.cut(box(ga, gb, ADXL_PCB_Y0 - CL_SLOT, ADXL_PCB_Y0 + ADXL_PCB_T + CL_SLOT, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L + 1.0))
        ny, nz = by, bz - BMP_HOLE_PZ / 2.0                    # the BMP's aft upper-y screw
        rl = rl.cut(box(xa - 1, xb + 1, ny - DRIVER_D / 2.0 - 0.3, ny + DRIVER_D / 2.0 + 0.3, nz - DRIVER_D / 2.0 - 0.3, nz + DRIVER_D / 2.0 + 0.3))
        parts.append(cap(as_solid(rl)))
    parts.append(cap(box(-hw - ADXL_RAIL, hw + ADXL_RAIL, ADXL_Y0 - ADXL_LIP_Y, wy1, -WALL, 0.0)))    # floor

    # ---- v6 AFT DECK: floor disc (first layers on the bed), spine (above, run down), N + S
    #      ribs, piezo pocket east with a roof at the mid ring, small-parts bay west/centre.
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, SEAT_Z + WALL)))
    for sy in (-1, 1):
        ya, yb = sorted((sy * (FOOT_RI - 1.0), sy * (SLED_RMAX + 1.0)))   # -1: a face AT R 15.8 is tangent to the mid ring
        parts.append(cap(box(-DECK_RIB_W / 2.0, DECK_RIB_W / 2.0, ya, yb, SEAT_Z, 0.0)))
    # piezo (v7 SIDEWAYS): a FLAT back plate the PCB back sits on (no standoffs), relieved
    # 1.4 deep under the solder joints; -y end wall locates the hole end; NO +y wall over
    # the board (pins exit there into the pin bay), only a stub above the board under the
    # roof.  Roof (DECK_Z1..0) ties the pocket to the mid ring, ADXL floor, battery tray and
    # the E boss column.  Board drops in radially from +x, 2 x M2 from +x into the plate +
    # the blocks behind it (those stand on the small-parts side, not in the pocket).
    pb0 = PIEZO_PLATE_X0
    py0, py1 = PIEZO_Y0 - CL_SLOT, PIEZO_Y1 + CL_SLOT
    pz = box(pb0, PIEZO_PCB_X0, py0 - WALL, py1 + WALL, SEAT_Z, DECK_Z1)                 # back plate, 2.6
    pz = pz.fuse(box(pb0, SLED_RMAX + 1.0, py0 - WALL, py0, SEAT_Z, 0.0))                 # -y end wall, out to the bore
    pz = pz.fuse(box(pb0, SLED_RMAX + 1.0, py1, py1 + WALL, PIEZO_Z0 + PIEZO_DZ + CL_SLOT, 0.0))   # +y stub above the board
    pz = pz.fuse(box(pb0, SLED_RMAX + 1.0, py0 - WALL, py1 + WALL, DECK_Z1, 0.0))         # roof
    for yc, zc, _ in PIEZO_HOLE_LIST:
        pz = pz.fuse(cyl_x(PIEZO_SCREW_D / 2.0 + 1.4, pb0 - PIEZO_BOSS_BACK, pb0 + 0.01, yc, zc))
        drill.append(cyl_x(PIEZO_SCREW_D / 2.0 - 0.2, pb0 - PIEZO_BOSS_BACK - 0.5, PIEZO_PCB_X0 + 1.0, yc, zc))
    # joint relief (the env trim cuts it too; drawn explicitly so it survives a smaller env)
    drill.append(box(PIEZO_PCB_X0 - PIEZO_JOINT_T, PIEZO_PCB_X0 + 0.01, PIEZO_Y0 + PIEZO_JOINT_Y0, py1 + WALL + 0.1,
                     PIEZO_Z0 + PIEZO_JOINT_EDGE, PIEZO_Z0 + PIEZO_DZ - PIEZO_JOINT_EDGE))
    parts.append(cap(as_solid(pz)))
    # v6b PRINT WEBS (aft end down): vertical webs on the floor disc under every face that
    #     would otherwise start mid-air -- tray bottom (Z -1.9), ADXL floor + Nano rails + mid
    #     ring (-1.2).  Ends deliberately cross FOOT_RI / the bore (no tangent faces).
    hwb = WALL / 2.0
    webs = [box(-hwb, hwb, -FOOT_RI, BATT_Y1 + BATT_WALL, SEAT_Z, 0.0),     # S rib -> under the tray (thin web)
            box(-hwb, hwb, ADXL_Y0 - ADXL_LIP_Y, FOOT_RI, SEAT_Z, 0.0),     # N rib -> under the ADXL floor (thin web)
            box(-8.0 - hwb, -8.0 + hwb, BATT_Y1 - BATT_DY - 0.5, BATT_Y1 + BATT_WALL, SEAT_Z, 0.0),   # under the tray, west
            box(8.0 - hwb, 8.0 + hwb, BATT_Y1 - BATT_DY - 0.5, PIEZO_Y0 - CL_SLOT - 0.5, SEAT_Z, 0.0),  # under the tray, east (v7: to the -y end wall)
            box(-NANO_DX / 2.0 - CL_SLOT - WALL, -NANO_DX / 2.0 - CL_SLOT, ADXL_Y0 - ADXL_LIP_Y, FOOT_RI, SEAT_Z, 0.0)]  # under the W Nano rail
    for ang in (135.0, 225.0, 315.0):                          # mid-ring webs (v7: 45 deg dropped -- pin bay)
        w = box(14.0 if ang != 315.0 else 15.0, SLED_RMAX + 1.0, -hwb, hwb, SEAT_Z, 0.0)   # v7: 315 starts outside the wider pocket
        w.rotate(Vector(0, 0, 0), Vector(0, 0, 1), ang)
        webs.append(w)
    for w in webs:
        parts.append(cap(w))

    # ---- battery tray, OUTBOARD-OPEN: floor on the inboard side, 2 side walls, 2 end
    #      caps.  Loaded from outboard with the e-bay out; zip tie + Kapton; the bore backs
    #      it up in flight.  JST notch at the fwd -x corner.  Floor + walls windowed.
    cb = CL_BATT
    bx0, bx1 = -BATT_DX / 2.0 - cb - BATT_WALL, BATT_DX / 2.0 + cb + BATT_WALL
    by_out, by_in = BATT_Y1 - BATT_DY, BATT_Y1                 # -15.5 .. -7.0
    fy1 = by_in + BATT_WALL                                    # floor -7.0 .. -5.8
    bc0, bc1 = BATT_Z0 - cb, BATT_Z0 + BATT_DZ + cb            # cavity ends
    bz0, bz1 = bc0 - BATT_END, bc1 + BATT_END
    tray = box(bx0, bx1, by_out, fy1, bz0, bz1)
    tray = tray.cut(box(-BATT_DX / 2.0 - cb, BATT_DX / 2.0 + cb, by_out - 1.0, by_in, bc0, bc1))
    tray = tray.cut(box(-BATT_DX / 2.0 - cb, -BATT_DX / 2.0 + JST_SLOT_W, by_out - 1, fy1 + 1, bc1 - 0.5, bz1 + 1))
    # v6: NO windows.  45 deg gusset outside the east wall root (west is against the BMP
    #     keep-out); 2 ribs over the fwd end cap run inboard to the top beam (y -1.5).
    g = BATT_GUSSET
    gus = Part.Face(Part.makePolygon([Vector(bx1 - 0.01, fy1, 0), Vector(bx1 + g, fy1, 0),
                                      Vector(bx1 - 0.01, fy1 - g - 0.01, 0), Vector(bx1 - 0.01, fy1, 0)]))
    gus = gus.extrude(Vector(0, 0, bz1 - bz0)); gus.translate(Vector(0, 0, bz0))
    tray = tray.fuse(gus)
    for xa, xb in BATT_RIB_X:
        tray = tray.fuse(box(xa, xb, by_out + 1.5, -BEAM_Y + 0.01, bz1 - 0.01, bz1 + 1.6))
    parts.append(cap(as_solid(tray)))

    # ---- reed module rails (v3), fused to the tray floor.  v4: both run up to the
    #      E boss (y -1.5) and the fwd one up into the cross-beam -> the tray is part of
    #      the frame loop ring - spine - W boss - beam - E boss - rails - tray - ring.
    rx0 = RM_X0 - CL_SLOT - WALL
    rx1 = RM_X1 - 1.8                                          # stop short of the lead pads
    ry0, ry1 = BATT_Y1, -BEAM_Y
    for za, zb, sa, sb in ((RM_Z0 - WALL, RM_Z0 + RM_RAIL_ENG, RM_Z0 - CL_SLOT, RM_Z0 + RM_RAIL_ENG + 1.0),
                           (RM_Z0 + RM_PCB_W - RM_RAIL_ENG, CAP_Z0 - 2.0,
                            RM_Z0 + RM_PCB_W - RM_RAIL_ENG - 1.0, RM_Z0 + RM_PCB_W + CL_SLOT)):
        rl = box(rx0, rx1, ry0 - 0.01, ry1, za, zb)
        rl = rl.cut(box(RM_X0 - CL_SLOT, rx1 + 1.0, RM_Y0 - CL_SLOT, RM_Y0 + RM_PCB_T + CL_SLOT, sa, sb))
        parts.append(cap(as_solid(rl)))

    # ---- mid ring (v4/v5 seat foot; v6 the deck ceiling ring -- the new foot is the floor disc)
    parts.append(cap(cyl(FOOT_RO, -WALL, 0.0).cut(cyl(FOOT_RI, -WALL - 1.0, 1.0))))

    # ---- top frame: W boss (D-cut for the BMP Qwiic cable) + E boss column on the piezo
    #      roof + cross-beam, and a bar from the W boss to the Nano wall.
    mw = cyl(MOUNT_BOSS_R, MOUNT_W_Z0, CAP_Z0, MOUNT_XW, 0.0).common(box(-30, MOUNT_W_XCUT, -30, 30, 0, 60))
    mb = mw.fuse(cyl(MOUNT_BOSS_R, DECK_Z1, CAP_Z0, MOUNT_XE, 0.0))   # v6: down to the piezo roof (piezo left)
    mb = mb.fuse(box(MOUNT_XW, MOUNT_XE, -BEAM_Y, BEAM_Y, CAP_Z0 - 3.0, CAP_Z0))
    mb = mb.fuse(box(MOUNT_W_XCUT - 0.2, -nx, BEAM_Y - 0.1, nout, CAP_Z0 - 3.0, CAP_Z0))   # bar -> Nano rail (v6: stops at the clearance)
    parts.append(cap(as_solid(mb)))
    drill += [cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, xc, 0.0) for xc in (MOUNT_XW, MOUNT_XE)]

    # ---- small parts: v6 in the aft deck (floor disc), no upper shelf

    sled = parts[0].multiFuse(parts[1:])
    rs = sled.removeSplitter()               # v6: removeSplitter can return an INVALID solid here
    log.append("  removeSplitter after fuse: %s" % ("kept" if rs.isValid() else "INVALID -> skipped (faces left split)"))
    sled = rs if rs.isValid() else sled
    for d in drill:
        sled = sled.cut(d)

    # RAW overlap of the as-drawn sled with each component keep-out, BEFORE any
    # trim.  This is the honest fit check: >0 means a pocket wall / boss / rail was
    # drawn into a component's space and has to be cleared (see [I]).
    env = dict((n, f()) for n, f in COMPONENTS)
    raw = {}
    for n, e in env.items():
        c = sled.common(e)
        raw[n] = c.Volume if c.Solids else 0.0

    # trim the overlaps against the RIGID parts (incl. the zip-tie + JST keep-outs) so
    # the exported solid is manufacturable as-is.  SmallParts yields -- NOT cut.
    for n in RIGID:
        sled = sled.cut(env[n])

    # CONNECTIVITY -- v1 lost its Nano pocket here without a word.  Never again.
    sol = sled.Solids
    log.append("  connectivity: %d solid(s)  %s" % (len(sol), ", ".join("%.1f" % s.Volume for s in sol)))
    if len(sol) != 1:
        raise RuntimeError("sled is %d disconnected solids (%s mm3) -- tie them in"
                           % (len(sol), ", ".join("%.1f" % s.Volume for s in sol)))
    if not sol[0].isValid():
        raise RuntimeError("sled solid is INVALID after the build (tangency?) -- see v5 [BMP boss]")
    return sol[0], raw

# ================================================================ verification
def main():
    log = []
    P = log.append
    P("=" * 78)
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (v7: piezo sideways, flat on the plate, pins into a free bay)" % REV)
    P("=" * 78)
    P("")
    P("frame: avbay_packing_build_report_v2.txt  (Z=0 aft, +Z to nose, +x E, +y N)")
    P("v7 (= v6): zone Z %.1f..%.0f -- the e-bay grows AFT by %.1f mm (aft deck); Z >= 0 unchanged from v5" % (SEAT_Z, ZONE_Z1, DECK_DZ))
    P("charger BQ25302 + its wall slot deleted; battery charges off-vehicle (JST-PH)")
    P("")

    doc = App.newDocument("PhoenixABS40-43_avbay_sled_v7")

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
        P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f"
          % (n, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin, bb.ZMax, rmax_mesh(cmesh[n])))
    sbb = smesh.BoundBox
    P("  %-12s %5.1f.%4.1f.%4.1f  %5.1f %5.1f  %6.2f   <- the sled"
      % ("Sled", sbb.XLength, sbb.YLength, sbb.ZLength, sbb.ZMin, sbb.ZMax, rmax_mesh(smesh)))

    P("")
    P("[0] CONTAINMENT  (Rmax vs %.1f moving / %.1f ID)" % (R_MAX_MOVING, R_AF_I))
    strap = {"Nano_ESP32", "ReedModule"}   # strap-retained against the skin (piezo is screwed)
    zmax = 0.0
    for n, s in comp.items():
        r = rmax_mesh(cmesh[n]); zmax = max(zmax, cmesh[n].BoundBox.ZMax)
        note = "strap-retained (outboard of the sled skin)" if n in strap else ""
        tag = "PASS" if r <= R_MAX_MOVING + 1e-6 else ("past moving" if r <= R_AF_I else "*** PAST ID ***")
        P("  %-12s Rmax %6.2f  toID %5.2f   %-5s %s" % (n, r, R_AF_I - r, tag, note))
    rs = rmax_mesh(smesh)
    P("  %-12s Rmax %6.2f  toID %5.2f   %-5s" % ("Sled", rs, R_AF_I - rs,
      "PASS" if rs <= SLED_RMAX + 0.05 else "FAIL"))
    P("  component tops  Z .. %.1f (deck from Z %.1f)   %s" % (zmax, SEAT_Z, "PASS" if zmax <= ZONE_Z1 + 1e-6 else "*** OVER ***"))
    # above the EbayCap underside only the spine key may exist (v1 top-slab footprint)
    above = sled.common(box(-30, 30, -30, 30, CAP_Z0 + 0.01, ZONE_Z1 + 5))
    key = clip_bore(box(-19.0, -16.6, -12.0, 12.0, CAP_Z0 + 0.01, ZONE_Z1 - 0.6))
    stray = above.cut(key); sv = stray.Volume if stray.Solids else 0.0
    P("  above EbayCap face Z %.1f: %.1f mm3, of which outside the spine key %.2f   %s"
      % (CAP_Z0, above.Volume if above.Solids else 0.0, sv, "PASS" if sv < 0.01 else "FAIL"))
    top = sled.common(box(-30, 30, -30, 30, CAP_Z0 - 0.2, CAP_Z0))
    for xc in (MOUNT_XW, MOUNT_XE):     # the M2 pan-head footprint (r 1.9) must be fully backed
        ring = cyl(1.8, CAP_Z0 - 0.2, CAP_Z0, xc, 0.0).cut(cyl(MOUNT_HOLE_D / 2.0, CAP_Z0 - 1, CAP_Z0 + 1, xc, 0.0))
        c = top.common(ring); f = (c.Volume if c.Solids else 0.0) / ring.Volume
        P("  EbayCap M2 boss (%.1f, 0.0) seated at Z %.1f: %.0f %% of the boss face present   %s"
          % (xc, CAP_Z0, 100 * f, "PASS" if f > 0.95 else "FAIL"))

    P("")
    P("[T] BMP388 vs NANO (heat)")
    dmin = comp["BMP388"].distToShape(comp["Nano_ESP32"])[0]
    bc, nc_ = comp["BMP388"].CenterOfMass, comp["Nano_ESP32"].CenterOfMass
    P("  closest envelope points %.1f mm (v3: 0.5, stacked face to face); centre-to-centre %.1f mm (v3 4.5)"
      % (dmin, math.hypot(bc.x - nc_.x, bc.y - nc_.y)))
    P("  BMP sensor side faces +x (the bay air); nothing covers it.")

    P("")
    P("[S] SCREW ACCESS  (d%.1f driver from the head outward; assembly order piezo -> BMP ->" % DRIVER_D)
    P("    ADXL -> Nano -> reed -> small parts -> battery; each sweep sees the sled + parts already in)")
    order = ["Piezo", "BMP388", "ADXL375", "Nano_ESP32", "ReedModule", "SmallParts", "Battery"]
    head_bmp = BMP_X0 + BMP_PCB_T + 1.8                      # pan head top on the PCB front
    head_pz = PIEZO_PCB_X0 + PIEZO_PCB_T + 1.8                # v6: pan head on the PCB front (can side)
    screws = [("piezo d%.1f y%+.1f" % (d, hy), "Piezo", Vector(head_pz, hy, hz), Vector(1, 0, 0))
              for hy, hz, d in PIEZO_HOLE_LIST]
    for sz in (-1, 1):
        zc = BMP_Z0 + BMP_L / 2.0 + sz * BMP_HOLE_PZ / 2.0
        screws.append(("BMP y+%.0f Z%.0f" % (BMP_HOLE_PY / 2.0, zc), "BMP388", Vector(head_bmp, BMP_HOLE_PY / 2.0, zc), Vector(1, 0, 0)))
    for nm, who, h, d in screws:
        drv = Part.makeCylinder(DRIVER_D / 2.0, 30.0, h, d)
        inn = order[:order.index(who)] + (["Piezo"] if who == "Piezo" else [])   # v6: driver passes its own can
        hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp[k]) for k in inn]
               for v in [(lambda c: c.Volume if c.Solids else 0.0)(sh.common(drv))] if v > 1e-2]
        P("  %-14s driver %s   %s" % (nm, "clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    ncd = Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(head_bmp, -BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0 - BMP_HOLE_PZ / 2.0), Vector(1, 0, 0))
    ncv = (lambda c: c.Volume if c.Solids else 0.0)(sled.common(ncd))
    P("  NEGATIVE CONTROL: a BMP y-%.0f driver hits the sled %.1f mm3 (must be > 0)   %s" % (BMP_HOLE_PY / 2.0, ncv, "PASS" if ncv > 1.0 else "FAIL"))
    P("  BMP y-%.0f pair: rest pads only (a straight driver would cross the battery tray floor)" % (BMP_HOLE_PY / 2.0))

    P("")
    P("[H] MEASURED HOLES  (2026-10-06, approximate; centre = edge distance + d/2)")
    P("  BMP388  4 x d%.1f, centres %.1f in -> pitch %.1f (y) x %.1f (z); M%.1f screws, boss r %.1f"
      % (BMP_HOLE_D, BMP_HOLE_IN, BMP_HOLE_PY, BMP_HOLE_PZ, BMP_SCREW_D, BMP_SCREW_D / 2.0 + BMP_BOSS_MARGIN))
    for hy, hz in [(sy * BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0 + sz * BMP_HOLE_PZ / 2.0) for sy in (-1, 1) for sz in (-1, 1)]:
        bc = Part.makeCylinder(BMP_SCREW_D / 2.0 + BMP_BOSS_MARGIN, BMP_STANDOFF, Vector(BMP_X0 - BMP_STANDOFF, hy, hz), Vector(1, 0, 0))
        kept = bc.common(sled); f = (kept.Volume if kept.Solids else 0.0) / bc.Volume
        P("    boss (y %+5.1f, Z %4.1f): %3.0f %% of the standoff left after the bore clip%s"
          % (hy, hz, 100 * f, "   (driven)" if hy > 0 else "   (rest pad)"))
    groove = ADXL_HOLE_IN - ADXL_HOLE_D / 2.0 - ADXL_EDGE
    P("  ADXL375 4 x d%.1f, centres %.1f in -> %.1f (x) x %.1f (z); rail-held, holes unused"
      % (ADXL_HOLE_D, ADXL_HOLE_IN, ADXL_HOLE_PX, ADXL_HOLE_PZ))
    P("    groove engagement %.1f vs hole edge %.1f from the PCB edge: %.1f clear   %s"
      % (ADXL_EDGE, ADXL_HOLE_EDGE, groove, "PASS" if groove > 0.2 else "FAIL"))
    for hy, hz, d in PIEZO_HOLE_LIST:
        P("  Piezo   d%.1f at (y %+5.2f, Z %5.2f), M%.0f" % (d, hy, hz, PIEZO_SCREW_D))
    for hy, hz, d in PIEZO_HOLE_LIST:
        # thread engagement: sled material along -x from the PCB back, 1.0 off the hole axis (pilot r 0.8)
        th = sled.common(Part.makeLine(Vector(PIEZO_PCB_X0, hy, hz + 1.0), Vector(PIEZO_PCB_X0 - 8.0, hy, hz + 1.0)))
        tl = sum(e.Length for e in th.Edges)
        # the board must bear on the plate round the hole (annulus r 1.3..2.0 at the plate face)
        ann = cyl_x(2.0, PIEZO_PCB_X0 - 0.1, PIEZO_PCB_X0, hy, hz).cut(cyl_x(1.3, PIEZO_PCB_X0 - 1, PIEZO_PCB_X0 + 1, hy, hz))
        c = sled.common(ann); f = (c.Volume if c.Solids else 0.0) / ann.Volume
        gap = math.hypot(hy, hz - PIEZO_ZC) - PIEZO_CAN_D / 2.0 - 1.9
        P("    piezo M2 (y %+5.2f): thread %.1f mm %s; plate under the hole %3.0f %% %s; M2 head to can %.2f %s"
          % (hy, tl, "PASS" if tl >= 4.0 else "FAIL", 100 * f, "PASS" if f > 0.95 else "FAIL", gap, "PASS" if gap > 0.2 else "FAIL"))
    P("  EbayCap M2: driven from the cap top -- always clear")

    P("")
    P("[W] BATTERY TRAY WALLS  (material along a ray from the cavity face outward, after clip + trim;")
    P("    floor + caps swept every 0.5 mm in x -- the v6 first pass probed sparsely and missed a slit)")
    def mat(pt, d, L):
        c = sled.common(Part.makeLine(pt, pt + d * L))
        return sum(e.Length for e in c.Edges)
    hx = BATT_DX / 2.0 + CL_BATT
    c0, c1 = BATT_Z0 - CL_BATT, BATT_Z0 + BATT_DZ + CL_BATT
    xs = [-10.5 + 0.5 * i for i in range(43)]
    probes = []
    for nm, sx in (("west wall", -1), ("east wall", 1)):
        probes += [(nm, Vector(sx * (hx - 0.01), y, z), Vector(sx, 0, 0), 4.0) for y in (-14.5, -11.0, -7.5) for z in (5.0, 20.0, 35.0)]
    probes += [("floor", Vector(x, BATT_Y1 - 0.01, z), Vector(0, 1, 0), 3.0) for x in xs for z in (5.0, 15.0, 30.0, 38.0)]
    probes += [("aft cap", Vector(x, y, c0 + 0.01), Vector(0, 0, -1), 4.0) for x in xs for y in (-13.0, -9.0)]
    probes += [("fwd cap", Vector(x, y, c1 - 0.01), Vector(0, 0, 1), 4.0) for x in xs if x > -BATT_DX / 2.0 + JST_SLOT_W - CL_BATT + 0.3
               for y in (-13.0, -9.0)]                     # JST notch (x < -4.5) is a designed opening
    worst = {}
    for nm, pt, d, L in probes:
        t = mat(pt, d, L)
        if t < worst.get(nm, (99.0, None))[0]:
            worst[nm] = (t, pt)
    need = {"west wall": 0.95, "east wall": 0.95, "floor": BATT_WALL - 0.05, "aft cap": 1.0, "fwd cap": 1.0}
    for nm, (t, pt) in worst.items():
        P("  %-10s min %.2f mm at (x %5.1f, y %5.1f, Z %5.1f)   %s" % (nm, t, pt.x, pt.y, pt.z, "PASS" if t >= need[nm] else "FAIL"))
    P("  caps: the zip-tie wraps sit in the 0.5 end clearance + a 0.75 notch at x ~0 (min above);")
    P("  west wall: trimmed by the BMP keep-out at x -11.5.  (v5: 0.8 walls, windowed, floor slit by the tie)")

    P("")
    P("[C] CLEARANCE  (gap from each sliding face out to the first sled material)")
    def gap(pt, d, L=3.0):
        c = sled.common(Part.makeLine(pt, pt + d * L))
        ds = [(v.Point - pt).Length for e in c.Edges for v in e.Vertexes]
        return min(ds) if ds else L
    gp = []
    gp += [("Nano x", Vector(sx * NANO_DX / 2.0, 14.0, z), Vector(sx, 0, 0), CL_SLOT) for sx in (-1, 1) for z in (5.0, 22.0, 44.0)]
    gp += [("ADXL groove x", Vector(sx * ADXL_W / 2.0, ADXL_PCB_Y0 + ADXL_PCB_T / 2.0, z), Vector(sx, 0, 0), CL_SLOT) for sx in (-1, 1) for z in (5.0, 15.0, 25.0)]
    gp += [("ADXL groove y", Vector(sx * (ADXL_W / 2.0 - 0.4), ADXL_PCB_Y0 + (ADXL_PCB_T if sy > 0 else 0.0), 12.0), Vector(0, sy, 0), CL_SLOT)
           for sx in (-1, 1) for sy in (-1, 1)]
    gp += [("piezo -y end", Vector(PIEZO_PCB_X0 + PIEZO_PCB_T / 2.0, PIEZO_Y0, PIEZO_Z0 + z), Vector(0, -1, 0), CL_SLOT)
           for z in (2.0, 7.5, 13.0)]
    gp += [("piezo Z edges", Vector(PIEZO_PCB_X0 + PIEZO_PCB_T / 2.0, y, PIEZO_Z0 + (PIEZO_DZ if sz > 0 else 0.0)), Vector(0, 0, sz), 1.5)
           for y in (-7.0, 0.0, 7.0) for sz in (-1, 1)]
    gp += [("battery x", Vector(sx * BATT_DX / 2.0, y, z), Vector(sx, 0, 0), CL_BATT) for sx in (-1, 1) for y in (-14.0, -9.0) for z in (5.0, 20.0, 35.0)]
    gp += [("battery z", Vector(x, y, z), Vector(0, 0, sz), CL_BATT) for x in (-6.0, 5.0) for y in (-13.0, -9.0)
           for z, sz in ((BATT_Z0, -1), (BATT_Z0 + BATT_DZ, 1))]
    gw = {}
    for nm, pt, d, cl in gp:
        g_ = gap(pt, d)
        if g_ < gw.get(nm, (99.0, None, cl))[0]:
            gw[nm] = (g_, pt, cl)
    for nm, (g_, pt, cl) in gw.items():
        P("  %-14s min gap %.2f (want %.2f) at (%5.1f, %5.1f, %5.1f)   %s" % (nm, g_, cl, pt.x, pt.y, pt.z, "PASS" if g_ >= cl - 0.05 else "FAIL"))

    P("")
    P("[P] PIEZO v7 -- sideways, flat on the plate, pins into a free bay")
    P("  board y %.1f..%.1f, Z %.1f..%.1f; can centre (0, Z %.1f) facing +x; pins exit +y at y %.1f"
      % (PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z0 + PIEZO_DZ, PIEZO_ZC, PIEZO_Y1))
    pocket = box(PIEZO_PCB_X0 + 0.01, PIEZO_X1 + 0.5, PIEZO_Y0, PIEZO_Y1, PIEZO_Z0, PIEZO_Z0 + PIEZO_DZ)
    c = sled.common(pocket); pv = c.Volume if c.Solids else 0.0
    P("  sled in front of the plate face over the board footprint: %.2f mm3 (no standoffs / bumps)   %s"
      % (pv, "PASS" if pv < 0.01 else "FAIL"))
    pb = pin_bay(); c = sled.common(pb); bv = c.Volume if c.Solids else 0.0
    bb = pb.BoundBox
    P("  pin bay x %.1f..%.1f, y %.1f..%.1f, Z %.1f..%.1f (%.0f mm3): sled inside it %.2f mm3   %s"
      % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, pb.Volume, bv, "PASS" if bv < 0.01 else "FAIL"))
    oth = [n for n, sh in comp.items() if n != "Piezo" and (lambda c: c.Volume if c.Solids else 0.0)(sh.common(pb)) > 1e-2]
    P("  other parts in the pin bay: %s   %s" % (oth or "none", "PASS" if not oth else "FAIL"))
    tip = math.hypot(PIEZO_PCB_X0 + PIEZO_PCB_T + PIEZO_PIN_X[1], PIEZO_Y1 + PIEZO_PIN_L)
    P("  straight pin tips at R %.2f (moving limit %.1f) -- bend them toward -Z / -x inside the bay   %s"
      % (tip, R_MAX_MOVING, "PASS" if tip <= R_MAX_MOVING else "FAIL"))
    P("  under the board %.1f mm, over it %.1f mm (v6: 0 under -- the pins hit the floor)"
      % (PIEZO_Z0 - (SEAT_Z + WALL), DECK_Z1 - (PIEZO_Z0 + PIEZO_DZ)))

    P("")
    P("[B] BATTERY ACCESS")
    bt = comp["Battery"]
    free = [d for d in (2.0, 5.0, 9.0, 12.0) if (lambda c: c.Volume if c.Solids else 0.0)(sled.common(bt.translated(Vector(0, -d, 0)))) < 1e-3]
    P("  pack slides OUTBOARD (-y) free of the sled: %s mm tested clear   %s" % (free, "PASS" if len(free) == 4 else "FAIL"))
    tie = comp["ZipTie"]
    P("  zip-tie channel (%.1f x %.1f band + %.2f): Rmax %.2f, clear of sled + other parts: see [I] ZipTie post-cut / clashes"
      % (TIE_W, TIE_T, TIE_CL, rmax_mesh(cmesh["ZipTie"])))
    P("  outboard face -> ID: %.1f mm at x 0 (tie head goes here), %.2f at the corners"
      % (R_AF_I - (BATT_DY - BATT_Y1), R_AF_I - math.hypot(BATT_DX / 2.0, BATT_DY - BATT_Y1)))

    P("")
    P("[R] REED MODULE -- arming by external magnet   (dims ASSUMED: measure RM_*)")
    ang = math.degrees(math.atan2(RM_YC, RM_XC))
    zc = RM_Z0 + RM_PCB_W / 2.0
    P("  PCB %.1f x %.1f x %.1f in the x-z plane at y %.1f..%.1f, x %.1f..%.1f, Z %.1f..%.1f"
      % (RM_PCB_L, RM_PCB_W, RM_PCB_T, RM_Y0, RM_Y0 + RM_PCB_T, RM_X0, RM_X1, RM_Z0, RM_Z0 + RM_PCB_W))
    P("  header pins point to the axis (tips x %.1f): SOLDER wires, no DuPont housing (+14 mm)" % (RM_X0 - RM_PIN_L))
    P("  capsule d%.1f x %.0f, axis at R %.2f, %.1f deg (from +x toward -y), Z %.1f..%.1f"
      % (RM_CAP_D, RM_CAP_L, RM_CAP_RC, ang, zc - RM_CAP_L / 2.0, zc + RM_CAP_L / 2.0))
    rr = RM_CAP_RC + RM_CAP_D / 2.0
    P("  glass outer R %.2f -> %.2f to ID + %.1f wall = %.2f mm magnet-to-glass" % (rr, R_AF_I - rr, D9_R_OD - D9_R_ID, D9_R_OD - rr))
    P("  airframe: ARM mark at %.0f deg from the witness notch (notch = +x, static port), stations %.1f..%.1f"
      % (abs(ang), 60.8 - (zc + RM_CAP_L / 2.0), 60.8 - (zc - RM_CAP_L / 2.0)))

    P("")
    P("[D9] FIT TO A *PROPOSED* D9aft E-BAY = v2 tube extended AFT by %.1f mm (seat at Z %.1f)" % (DECK_DZ, SEAT_Z))
    P("     (sled frame = D9 z - %.1f above Z 0; station = 60.8 - Z if the length goes in aft)" % D9_DZ)
    # FwdTube proxy, thread-free (as D9aft does): bore d40, crest band d39.30, seat, spigot, ports
    cav = cyl(D9_CREST, D9_BAND_Z, 70.0)
    cav = cav.fuse(Part.makeCone(D9_R_ID, D9_CREST, D9_R_ID - D9_CREST, Vector(0, 0, D9_BAND_Z - (D9_R_ID - D9_CREST))))   # 45 deg
    cav = cav.fuse(cyl(D9_R_ID, D9_SEAT_Z, D9_BAND_Z - (D9_R_ID - D9_CREST) + 0.001))
    cav = cav.fuse(cyl(D9_SEAT_RI, D9_SEAT_Z - D9_SEAT_T, D9_SEAT_Z + 0.001))
    cav = cav.fuse(Part.makeCone(D9_SPIGOT_RI, D9_SEAT_RI, D9_SPIGOT_RI - D9_SEAT_RI, Vector(0, 0, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI))))
    cav = cav.fuse(cyl(D9_SPIGOT_RI, D9_SEAT_Z - 14.1, D9_SEAT_Z - D9_SEAT_T - (D9_SPIGOT_RI - D9_SEAT_RI) + 0.001))
    tube = cyl(D9_R_OD, D9_SEAT_Z - 11.1, 60.8).cut(cav)
    for nm, d, zp, a in D9_PORTS:
        tube = tube.cut(Part.makeCylinder(d / 2.0, 5.0, Vector(D9_R_ID - 1.0, 0, zp), Vector(1, 0, 0)).rotated(Vector(0, 0, 0), Vector(0, 0, 1), a))
    ec = Part.Shape(); ec.read(D9_EBAYCAP); ec.translate(Vector(0, 0, -D9_DZ))
    P("  EbayCap STEP: Z %.2f..%.2f (expect disc underside at %.1f)   %s"
      % (ec.BoundBox.ZMin, ec.BoundBox.ZMax, CAP_Z0, "PASS" if abs(ec.BoundBox.ZMin - CAP_Z0) < 0.01 else "FAIL"))
    for nm, part in (("FwdTube (proxy)", tube), ("EbayCap", ec)):
        hits = []
        for n2, sh in [("Sled", sled)] + list(comp.items()):
            c = sh.common(part); v = c.Volume if c.Solids else 0.0
            if v > 1e-2: hits.append((n2, round(v, 2)))
        P("  %-16s vs sled + every component: %s   %s" % (nm, hits or "contact only", "PASS" if not hits else "FAIL"))
    nc = sled.translated(Vector(0, 0, -0.5)).common(tube); ncv = nc.Volume if nc.Solids else 0.0
    P("  NEGATIVE CONTROL: sled dropped 0.5 mm -> %.1f mm3 into the seat (must be > 0)   %s"
      % (ncv, "PASS" if ncv > 1.0 else "FAIL"))
    lift = max(rs, max(rmax_mesh(cmesh[n]) for n in comp))
    P("  lift-out through the thread crests: largest R %.2f vs crest %.2f -> %.2f radial   %s"
      % (lift, D9_CREST, D9_CREST - lift, "PASS" if D9_CREST - lift >= 0.25 else "FAIL"))
    zmin = min([sled.BoundBox.ZMin] + [s.BoundBox.ZMin for s in comp.values()])
    foot = sled.common(cyl(D9_R_ID, zmin - 0.01, zmin + 0.1).cut(cyl(D9_SEAT_RI, zmin - 1, zmin + 1)))
    loose = sled.common(cyl(D9_SEAT_RI, zmin - 0.01, zmin + 0.1))
    fa = (foot.Volume if foot.Solids else 0.0) / 0.11; la = (loose.Volume if loose.Solids else 0.0) / 0.11
    P("  seat: sled Zmin %.2f vs seat top %.2f; bearing on the seat annulus %.0f mm2, overhanging the seat hole %.0f mm2   %s"
      % (zmin, D9_SEAT_Z, fa, la, "PASS" if abs(zmin - D9_SEAT_Z) < 1e-3 and fa > 100 else "FAIL"))
    for nm, d, zp, a in D9_PORTS:
        col = Part.makeCylinder(d / 2.0 + 0.5, 3.0, Vector(D9_R_ID - 3.0, 0, zp), Vector(1, 0, 0)).rotated(Vector(0, 0, 0), Vector(0, 0, 1), a)
        blk = [n2 for n2, sh in [("Sled", sled)] + [(k, v) for k, v in comp.items() if k != "Piezo"] if (lambda c: c.Volume if c.Solids else 0.0)(sh.common(col)) > 1e-3]
        P("  %-6s port d%.1f at Z %.1f, %.0f deg: 3 mm behind it clear of %s   %s"
          % (nm, d, zp, a, "everything" if not blk else blk, "PASS" if not blk else "FAIL"))
    # v7: the REAL D9aft v6 parts (built on sled v6).  Placed by putting the v6 EbayCap disc
    #     underside on CAP_Z0; the FwdTube STEP shares its frame.
    d9 = {}
    for k, fn in D9V6_STEP.items():
        sh = Part.Shape(); sh.read(fn); d9[k] = sh
    dz = CAP_Z0 - d9["EbayCap"].BoundBox.ZMin
    for k in d9:
        d9[k].translate(Vector(0, 0, dz))
    P("  REAL D9aft v6 STEPs placed with dz %.2f (EbayCap underside -> Z %.1f)" % (dz, CAP_Z0))
    for nm, part in (("FwdTube v6", d9["FwdTube"]), ("EbayCap v6", d9["EbayCap"])):
        hits = []
        for n2, sh in [("Sled", sled)] + list(comp.items()):
            c = sh.common(part); v = c.Volume if c.Solids else 0.0
            if v > 1e-2: hits.append((n2, round(v, 2)))
        P("  %-16s vs sled v7 + every component: %s   %s" % (nm, hits or "contact only", "PASS" if not hits else "FAIL"))
    nc = sled.translated(Vector(0, 0, -0.5)).common(d9["FwdTube"]); ncv = nc.Volume if nc.Solids else 0.0
    P("  NEGATIVE CONTROL (real FwdTube v6): sled dropped 0.5 mm -> %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))
    port = cyl_x(1.4, D9_R_ID - 1.0, D9_R_OD + 1.0, 0.0, PIEZO_ZC)
    c = d9["FwdTube"].common(port); pv = c.Volume if c.Solids else 0.0
    wall = cyl_x(1.4, D9_R_ID - 1.0, D9_R_OD + 1.0, 0.0, PIEZO_ZC - 3.0)
    c = d9["FwdTube"].common(wall); wv = c.Volume if c.Solids else 0.0
    P("  real FwdTube v6 sound port on the v7 can axis (y 0, Z %.1f): %.2f mm3 of wall in a d2.8 probe (must be ~0); 3 mm aft %.1f (must be > 0)   %s"
      % (PIEZO_ZC, pv, wv, "PASS" if pv < 0.05 and wv > 1.0 else "FAIL"))
    pzb = comp["Piezo"].BoundBox
    P("  piezo can centre Z %.1f (env %.1f) vs sound port Z %.1f   %s" % (PIEZO_ZC, (pzb.ZMin + pzb.ZMax) / 2.0, D9_PORTS[1][2],
      "PASS" if abs((pzb.ZMin + pzb.ZMax) / 2.0 - D9_PORTS[1][2]) < 0.01 else "FAIL"))

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
    P("  + fasteners: 2x M2.5x4 (BMP388 y+9, d3 board holes, into the spine), 2x M2x6 (piezo, from +x, d2.5 + d3 board holes),")
    P("               2x M2x10 (EbayCap, axial); 1 mini zip tie (battery); Nano, ADXL, reed = Kapton")
    P("  (v5 sled 6802.6 mm3 / 7.1 g -> v7 %+.1f g; v4 6813.8 / 7.2)" % (m - 6802.6 * RHO))

    P("")
    P("[L] FOR D9aft -- v7 changes NOTHING it reads: seat Z %.1f, sound port Z %.1f / 0 deg, cap, spine key, static port = v6" % (SEAT_Z, PIEZO_ZC))
    P("  (D9aft v6 itself still exec's sled v6; its parts are checked against v7 in [D9])")
    P("  e-bay length +%.1f mm, all of it AFT of the old seat: seat plane Z -0.9 -> %.1f" % (DECK_DZ, SEAT_Z))
    P("  sound port: d3 at %.0f deg, Z %.1f (v5 Z 9.5) = station %.1f if the length goes in aft" % (D9_PORTS[1][3], PIEZO_ZC, 60.8 - PIEZO_ZC))
    P("  unchanged: EbayCap face Z %.1f, M2 bosses, spine key, static port Z 30" % CAP_Z0)
    P("  CHANGED:   reed module RM_Y0 -5.0 -> %.1f (tie leg over the floor) -> ARM mark %.1f deg (v5 -10.9)"
      % (RM_Y0, math.degrees(math.atan2(RM_YC, RM_XC))))
    P("  sled mass %+.1f g vs v5; seat now bears on a full floor disc R %.1f" % (m - 6802.6 * RHO, FOOT_RO))
    P("  electronics: reed module ~%.1f g (est.); SmallParts allowance 13 g" % RM_MASS)

    P("")
    P("[N] NOTES / OPEN")
    P("  * v2/v3 vs v1: servo + cradle + knob ref removed (D9aft: e-bay fires nothing).  The")
    P("    EbayCap M2 bosses stay at v1's SG90-ear (x, y), top Z %.1f -> the D9aft v1/v2" % CAP_Z0)
    P("    EbayCap fits unchanged (its pocket has spare voids where the cradle uprights were).")
    P("  * v1 EXPORT WAS MISSING THE NANO POCKET (disconnected, dropped by as_solid).  The")
    P("    D9aft v1/v2 checks exec'd that same sled, so they never saw it either.")
    P("  * RETENTION:")
    P("      screw-down  BMP388  -- 2 x M2.5 (y +9) from +x into spine standoffs; y -9 pads + Kapton")
    P("                             (pilots break out past R 19.4 beyond 4 mm: use M2.5 x 4 max)")
    P("      rails       ADXL375 -- PCB edges in 2 grooves, slide down from the top, Kapton on top")
    P("      screw-down  Piezo (v7) -- 2 x M2x6 from +x through the PCB into the flat plate; board drops in from outboard")
    P("                  EbayCap -- 2 axial M2x10 from the cap top into the mount bosses")
    P("      strap       Nano (1.21 to ID) -- rails + %.1f lip + Kapton; rests on the ADXL rail tops" % LIP)
    P("      rails       Reed module -- PCB edges in aft + fwd slots, radial stop at the")
    P("                             header end, Kapton over the reed edge")
    P("      tie         Battery -- outboard-open tray, 1 axial mini zip tie (<= %.1f wide) + Kapton;" % TIE_W)
    P("                             pad the outboard face with ~1 mm foam so the bore backs it")
    P("  * QWIIC: wire the bus as a STAR at the Nano (Nano has no Qwiic port anyway): one")
    P("    cable to the ADXL's FWD plug, one to the BMP's FWD plug.  Neither AFT plug has room.")
    P("  * ASSEMBLY ORDER (screw access): piezo (2 x M2 from +x, e-bay out) -> BMP ->")
    P("    ADXL (slide in) -> Nano -> reed module -> small parts -> battery -> EbayCap.")
    P("  * ADXL thickness with the plug in is ASSUMED %.1f mm (slot is %.1f) -- measure it." % (ADXL_T, (NANO_Y0 - CL_BOARD) - ADXL_Y0))
    P("  * STIFFNESS NOT ANALYSED: frame loop is ring - spine - W boss - beam - E boss - reed")
    P("    rails - tray - ring; the Nano/ADXL column ties in at the ring, the piezo pocket")
    P("    and the top bar.  Overhangs / print orientation not checked yet.")
    P("  * v6 battery tray: no windows; pack drops in from outboard with 0.5 mm all round --")
    P("    take up the slack with ~1 mm foam on the outboard face (the bore backs it in flight).")
    P("  * v7 piezo ASSUMED (from the photo, MEASURE): can centred on the board (PIEZO_CAN_OFF 0),")
    P("    joints only > %.1f from the hole end and %.1f in from the long edges, header %.1f x %.1f x %.1f," % (PIEZO_JOINT_Y0, PIEZO_JOINT_EDGE, PIEZO_HDR[0], PIEZO_HDR[1], PIEZO_HDR[2]))
    P("    pins %.1f past the edge, centred; d2.5 hole on the aft long edge.  Bend the pins toward" % PIEZO_PIN_L)
    P("    -Z/-x inside the pin bay and heat-shrink each.  Small parts: Kapton/hot glue in the deck.")
    P("  * REED MODULE dims are from a photo: measure PCB L x W x T, capsule d + offset from")
    P("    the edge, header height and pin length, then edit RM_* and re-run.  Press the lead")
    P("    loops flat before fitting (they ship standing ~5 mm proud).  Bend >= 2 mm from the glass.")
    P("  * D9aft v2 still exec's sled v1 (its SLED_SRC).  Sled v4 keeps every interface it reads")
    P("    (SERVO_TAB_X*, ADXL_CLEAR_Z, COMPONENTS, build_sled); a D9aft v3 pointing here regenerates")
    P("    the EbayCap pocket from this sled's top.  Its tie/JST keep-outs are not parts.")
    P("  * v5 hole patterns are MEASURED but approximate (BMP / ADXL / piezo, see [H]);")
    P("    still ASSUMED: the BMP PCB length (= 40 envelope), which piezo long side has the")
    P("    d2.5 hole, and the whole Nano pattern (NANO_HOLE_P*).  Check a test print before")
    P("    trusting the BMP boss positions; the y +/-%.0f bosses are clipped by the bore ([H])." % (BMP_HOLE_PY / 2.0))
    P("  * wall thickness: only the battery tray is measured ([W]); eyeball the other thin walls")
    P("    in CAD before printing.")
    P("  * free volume: upper centre (old shelf + old piezo slot, east Z 0..19) -- wiring runs there.")
    P("  * small-parts = ~13 g allowance in the aft deck bay; measure S7V8F5 / microSD rdr /")
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

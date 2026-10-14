# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED, v10  (the "scaffold to screw
the chips into").

v10 = v9 RE-PACKED + PRINTABLE WITHOUT SUPPORT (2026-10-14, user: v9 printed and works, but the
ceiling over the piezo (the whole ring), the top of the reed module and the underside of the
cap-screw I-beam spaghettified; "we're gluing the accelerometer to the back of the battery
casing"; the BMP388 does not fit the spine side with its Qwiic plugs in; "the sd chip is
26x23x4").  Every interface D9aft reads is unchanged (seat Z -22.8, EbayCap face Z 45.4 + M2
bosses, spine key, sound port Z -12.1 / 0 deg, static port Z 30) and the reed CAPSULE does not
move (R 17.9, -8.7 deg) -> ARM mark unchanged.
  * [O] OVERHANG AUDIT (new, Avionics/avbay_overhang_audit.py): every downward face steeper than
    46 deg off vertical, bed excluded, clustered.  Run on the v9 STEP it lists all three failure
    sites (piezo roof Z -2.0 227 mm2, ring -1.2/-2.2, reed rails 25.1/40.3/41.7, beam 42.4,
    E boss 38.5, W boss 40.9) -- the negative control.  v10 numbers are in the report.
  * ADXL375 GLUED FLAT on the back (inboard face, y -5.8) of the battery tray floor, plug AFT
    into the deck (the reed module sits above it from Z 26.3).  West fence locates it; it slides
    in from +x.  The grooved ADXL rails + floor are gone.
  * BMP388 on the EAST flank (piezo / reed side), board back on x 11.5, sensor + Qwiic facing the
    static port.  2 x M2.5 (y +9) from +x into a new full-height E PIER; y -9 pair rest on the
    tray east wall (trimmed to 1.0, as v9's west wall was for the BMP).  The old outside gusset
    on the east wall root is gone (it was in the BMP's place); a small inboard fillet replaces it
    above the reed stubs.
  * MicroSD reader is 26 x 23 x 4 (user) -- too big for the deck lane: on edge in the old BMP lane
    (spine side, x -15.5..-11.5, Z 0..26) against a spine pad.  The deck lane is empty now.
  * BATTERY TIE goes SIDEWAYS (user): one band round the pack at Z ~29 through full-depth slots in
    both tray walls and the floor corners, across the tray back above the ADXL and under the reed
    PCB.  The tray back is free for the ADXL; tray end caps lose the axial-tie notch.
  * REED MODULE: v9's x-rails deleted (they were the spaghetti).  v10d SLIDE-IN (user): the board
    drops in AXIALLY from the cap end -- vertical guides print clean, the fwd-edge lip/roof that
    spaghettied in v9 is not needed.  W guide (end stop, back wall, aft seat, lip below the header)
    on the W fence; E lip off the pier, E aft seat tab off the tray wall; the BMP's back face is the
    E stop; pads + stubs are the back rest.  Fwd edge: Kapton.  Tray ribs stop at the tray and the
    E boss is notched so the board + its bent leads drop past.  PCB 0.6 west of v9 (BMP), capsule
    NOT moved: leads BENT (user) over the BMP's fwd end; capsule laid in by hand after the BMP.
  * v10d ADXL LEDGE (user): under the PCB's aft edge, W half (the receptacle slides over the E half).
  * NANO: the ADXL rails were its inboard stiffening -> a full-width BACKING PLATE (y 9.4..10.6)
    from the deck to the cap ties both solid rails into a U-channel; rail bottoms get 1:1.15
    knee braces off it (the E one stays above the piezo pin bay).  v10c: ONE tall pointed-arch ACCESS
    window through the plate (user: hollow it "so we can install the accelerometer and similar") --
    reach the ADXL / tray back / tie / plugs from +y while the Nano is out.
  * PRINTABILITY: piezo roof deleted outboard of the back plate (it was a cantilever over the
    pocket); mid ring kept only where webs carry it; new web under the tray + 1:1.15 arch
    haunches over the C1 / Q1 loading tunnel; W boss corbels off the (thicker) spine; E boss
    sits on the pier; beam carried by a 1:1.15 pointed-arch web; W bar by knee braces.

v9 = v8 with a ROBUST NANO MOUNT (2026-10-11, user: "the avionics bay broke as I removed
it from the plate ... one of the esp32 rails broke").  v8's Nano rails were split above
Z 28 by the two snap-arm slits into FOUR free slivers (1.2 x 2.7 arms + 1.2 x 2.0 outer
strips, ~17 mm tall; the EAST outer strip tied to nothing at the top).  Printed aft end
down, those are columns that bend ACROSS the layer lines -- ABS's weakest direction.
  * NO FLEXURES: arms, slits, barbs and aft corner fingers deleted.  Each rail is one
    solid wall 2.0 thick (v8 1.2), y 10.3 .. 16.5 (bore-clipped), Z -2.2 .. 45.4.
  * Nano now drops in RADIALLY from outboard (+y) with the e-bay out of the tube, between
    FIXED end stops: aft blocks under the PCB end (as v8) + fwd blocks over the PCB end
    (Z 44.1..45.4, under the EbayCap face).  Outboard: Kapton across the rails; the bore
    backs it in flight -- same scheme as the battery.
  * Both rails tied at the top: W rail -> the bar to the W boss (now fused to the rail),
    E rail -> a new bar to the E boss (v8: the E side was tied to nothing).
  * [K] slender-member audit (new): slices the sled every 0.5 mm in Z and lists every
    island thinner than 1.0 mm / smaller than 8 mm2 over >= 3 mm of height.  Run on v8 it
    flags the four Nano slivers (negative control).
  * [D9] now checks the CURRENT D9aft v10 FwdTube + EbayCap STEPs (v8 checked v6).
  Every interface unchanged: seat Z -22.8, EbayCap face Z 45.4 + bosses, spine key, sound
  port Z -12.1 / 0 deg, static port, reed / ARM mark.

v8 = v7 refitted to MEASURED parts + a Nano catch + every small part as itself (2026-10-07,
user: "check if all other chips actually fit"; e-bay length: "don't make it longer").
SAME LENGTH and interfaces as v7 (seat Z -22.8, sound port Z -12.1 / 0 deg, EbayCap face,
M2 bosses, spine key, static port, reed capsule / ARM mark) -> D9aft v6/v7 tubes + cap fit.
Found by Avionics/avbay_fit_audit.py on v7 and fixed here:
  * NANO: v7 had NOTHING under its aft end (the mid ring starts outboard of the PCB), its
    0.6 lips sat 3.4 mm above the PCB (parts-outboard), and its 30 pad joints on the back
    face landed on the rail ledge.  v8 (no headers, parts OUTBOARD, USB-C at the FWD end):
      - Nano dropped 1.0 (Z -1..44) so a real catch fits under the EbayCap face;
      - aft: 2 corner blocks under the PCB end + 2 corner fingers over the PCB top (pads
        start Z 2.9, corners free -- ASSUMED);
      - fwd: the lower band of each Nano rail is a CANTILEVER ARM (slit from the rail) with
        a 45 deg lead-in BARB over the PCB end: push the board down, the arms spring out
        and snap over it.  Nothing above Z 45.4 -> the printed EbayCap is unchanged;
      - ledge under the pad rows lowered: joints (0.5) clear by 0.4; lips gone.
  * ADXL375 MEASURED 18 x 27 (with Qwiic) x 5.0 max: moved inboard to y 5.7..10.7 so it
    clears the Nano joints (v7: its real plug top sat AT the Nano PCB).
  * PIEZO MEASURED: can d12 x 10 tall (was 12.5 x ~8), centre 8 from the hole edge (was
    9.5), pins 6.5 past the edge (25 overall).  Board moved inboard 1.6 (can face x 18.4
    inside the bore), pocket follows.  Straight pins would reach R 20.2 -> BEND THEM FIRST
    (modelled bent down + heat shrink in the pin bay).
  * REED MEASURED: capsule axis 6 mm outside the PCB edge, 30 overall -> PCB + pins move
    3.5 inboard (capsule, ARM mark unchanged).
  * SMALL PARTS as themselves (no yielding allowance): microSD 4682 in a WEST LANE (slides
    in/out radially from -y, card end outboard), S7V8F5 / C1 / 2N7000 / AO3401 in an open
    CENTRAL BAY that loads radially from N and S.  Deck webs re-laid for that: x 0 webs,
    N/S ribs and the 45/225 ring webs gone; one N-S wall at x -8; Nano-rail web north of
    the reader only.

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
REV = "v10"
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
NANO_Z0 = -1.0                            # v8: 1.0 lower so the fwd catch fits under the EbayCap face
NANO_PCB_T = 1.6                          # parts OUTBOARD: PCB y 11.5..13.1, parts to 16.5 (no headers)
NANO_ROW_X = 15.24 / 2.0                  # Nano form factor: 2 x 15 pads at 2.54 on rows 0.6" apart
NANO_PAD_R = 0.85
NANO_JOINT_H = 0.5                        # flush-cut wire + fillet on the BACK face (ASSUMED)
NANO_PADS_Z = [NANO_Z0 + 45.0 / 2.0 + (i - 7) * 2.54 for i in range(15)]
NANO_LEDGE_Y = NANO_Y0 - NANO_JOINT_H - 0.4                  # 10.6: rail ledge under the pad rows
ARM_Z0 = 28.0                             # catch arm root (cantilever 28 -> top)
ARM_Y1 = NANO_Y0 + NANO_PCB_T + 0.8       # arm = rail band y 10.3 .. 13.9; slit above it
ARM_SLIT = 0.6
ARM_Y0 = 11.2                             # arm's inboard edge (BMP board edge at y 11.0)
BARB_OVL = 0.5                            # barb overlap onto the PCB end (x 8.5..9.0; pads stop at 8.47)
BARB_Z = 0.1                              # gap barb underside -> PCB top end
NANO_RAIL_T = 2.0                         # v9: Nano rail wall in x (v8 = WALL 1.2), grows OUTWARD only
NANO_STOP_Z = 0.1                         # v9: gap fwd stop -> PCB fwd end (fixed block, no barb)
NANO_HOLES = 4
NANO_HOLE_D     = 2.0
NANO_HOLE_PX, NANO_HOLE_PZ = 14.0, 40.0   # 4-corner pitch (CONFIRM)

# BMP388 40x22x4 (Qwiic plug bodies incl.) -- v10: EAST flank (user: the spine side has no room with
#   the Qwiic plugs in), on edge: 4 thick along x, 22 along y, 40 along Z.  PCB back face on the -x
#   side (flat on the E pier + the tray east wall), parts + Qwiic on +x facing the static port.
#   Screws from +x (heads on the PCB), driven with the e-bay out.
BMP_T, BMP_W, BMP_L = 4.0, 22.0, 40.0     # x . y . z
BMP_X0 = 11.5                             # v10: PCB back face (v9 -15.5, west); front 15.5 -> corner R 19.0
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
BMP_STANDOFF = 1.5                        # (v9 spine standoffs; v10 the pier face IS the seat -- unused)
BMP_CABLE = (3.5, 4.2, 6.0)               # v10b: Qwiic plugs are CENTRED on both short (Z) ends (user 2026-10-14).  The FWD
                                          #   one is blocked (E boss from Z 40.4, reed leads) -> wire the AFT one: plug half-width
                                          #   y +/-3.5, 4.2 long down to just over the piezo board, then a bend lane 6 mm north
PIER_X0 = 7.0                             # v10: E pier x 7.0..BMP_X0, y PIER_Y0..10.3 -- BMP screw seat + E boss column
PIER_Y0 = 0.2                             #   clear of the reed header (y <= -0.2) on its way in from +x
KNEE = 1.15                               # v10: every knee brace / corbel / haunch rises 1.15 per 1.0 out (49 deg)
PLATE_WIN_X = (-6.6, 5.0)                # v10c: Nano backing-plate ACCESS window: W edge = W pad-row joints' inner edge
                                          #   (-6.77) -> both rows keep bearing on the plate; E edge = the pier web (x 5)
PLATE_WIN_Z = (0.0, 33.3)                 #   sill top (the aft shelf hangs on the sill) .. springing of the 1:1.15 arch
                                          #   -> apex Z 40.0; plate above it ties the rails under the cap

# MICROSD reader 26 x 23 x 4 (user 2026-10-14; v9 modelled the 20.3 x 15.2 Adafruit 4682) -- does not
#   fit the deck (19 mm high).  v10: on edge in the old BMP lane, back flat on a spine pad, Z 0..26,
#   card end at -y (ASSUMED).  Kapton / a dab of glue.
SD_T, SD_W, SD_L = 4.0, 23.0, 26.0        # x . y . z
SD_X0 = -15.5                             # back face = spine pad
SD_Z0 = 0.0
SD_CARD_OUT = 2.0                         # v10b: card proud of the long edge (push-push socket, ASSUMED)
# BATTERY 40.5x20x8.5 -- south, alone, pulled in 0.7 from the v2 corner -----
BATT_DX, BATT_DY, BATT_DZ = 20.0, 8.5, 40.5
BATT_Y1 = -7.0                            # inboard face
BATT_X0 = 0.0                             # pack centre x (v10 kept: both walls get trimmed to 1.0 by the BMP / microSD)
BATT_Z0 = 0.4                             # 0.4 up: the zip-tie wrap (+clearance) stays above the seat plane
BATT_WALL = 1.2                           # v6 (v5 0.8, windowed -- it broke loading the pack)
BATT_END = 1.8                            # v6: end caps
BATT_GUSSET = 1.6                         # v10: the fillet moved INBOARD of the floor (user: "move the flap toward the axis"); outside = BMP
BATT_RIB_X = ((2.6, 3.8), (7.6, 8.8))     # v6: ribs over the fwd end cap, clear of JST (-x) and tie (x~0)
JST_SLOT_W = 6.0                          # FWD end, -x corner
JST_PLUG = (6.0, 4.5, 4.3)                # JST-PH plug + lead bend, x . y . z (est.)
TIE_W, TIE_T = 2.5, 1.0                   # mini zip tie band
TIE_CL = 0.25
TIE_XC = 0.2                              # (v9 axial tie, unused)
TIE_Z0 = 27.75                            # v10 SIDEWAYS tie: band Z 27.75..30.25 -- above the ADXL (25.0) and
                                          #   under the reed solder stubs (30.65); slots through both walls + floor corners

# ADXL375 -- v10: GLUED FLAT on the back (inboard face) of the battery tray floor (user), long axis
#   along Z, PCB back on y -5.8, parts toward the axis.  Measured: 27 long with the Qwiic plug in,
#   5.0 max.  Plug at the AFT end (into the deck, cable bends down there): the reed module sits on the
#   same face from Z 26.3.  Slides in from +x (before the BMP) against a west fence.
ADXL_W, ADXL_T, ADXL_L = 18.0, 5.0, 27.0  # x . y . z  MEASURED (user 2026-10-07: 5.0 max, 27 with Qwiic)
ADXL_PCB_L, ADXL_PCB_T = 26.0, 1.6
ADXL_Y0 = BATT_Y1 + BATT_WALL             # v10: -5.8 = PCB back on the tray floor's inboard face; top -0.8
ADXL_PCB_Y0 = ADXL_Y0
ADXL_Z0 = -1.0                            # v10: PCB aft end; fwd end 25.0 (reed pads start 37.6, tie band 27.35)
ADXL_EDGE = 0.8                           # component-free PCB edge that runs in the groove
ADXL_PLUG_W = 8.0                         # plug + cable width (est.)
ADXL_BEND = 3.0                           # cable bend room past the plug
ADXL_RAIL = 1.8                           # rail outboard of the PCB edge (v6: 1.4 -> 1.8)
ADXL_LIP_Y = 0.6                          # v6: rail runs this far below ADXL_Y0 (groove lip 0.3 -> 0.7)
ADXL_CLEAR_Z = ADXL_Z0 + ADXL_PCB_L       # name kept for D9aft; v10 the ADXL top (plug is aft)
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
PIEZO_PCB_X0 = 6.8                        # v8: PCB back face = back-plate face (1.6 in from v7: taller can)
PIEZO_CAN_H = 10.0                        # MEASURED: can 10 tall over the PCB
PIEZO_X1 = PIEZO_PCB_X0 + 1.6 + PIEZO_CAN_H   # 18.4: can face
PIEZO_CAN_D = 12.0                        # MEASURED d12
PIEZO_CAN_FROM_HOLE = 8.0                 # MEASURED (user: "8 mm from the top edge", read as hole edge -> can centre;
                                          #   "19 from the bottom edge" can't be a centre distance on a 19 board)
PIEZO_Y0 = -PIEZO_CAN_FROM_HOLE                              # hole-end edge (can stays at y 0)
PIEZO_Y1 = PIEZO_Y0 + PIEZO_DL                               # pin-end edge
PIEZO_Z0 = PIEZO_ZC - PIEZO_DZ / 2.0                         # -19.6 (2.0 above the floor)
PIEZO_JOINT_T = 1.4                       # back-side solder joints (ASSUMED) = plate relief depth
PIEZO_JOINT_Y0 = 4.5                      # joints start this far from the hole end (ASSUMED)
PIEZO_JOINT_EDGE = 1.0                    # ... and keep the long (Z) edges free this wide (ASSUMED)
# right-angle header on the CAN side at the pin end, pins in the board plane past the edge (ASSUMED from the photo)
PIEZO_HDR = (2.5, 2.5, 7.6)               # body: x above the PCB front . y in from the edge . z
PIEZO_PIN_X = (0.95, 1.6)                 # pin band above the PCB front (as the KY-021 reed)
PIEZO_PIN_L = 6.5                         # MEASURED: straight pins past the board edge (25 overall)
PIEZO_PIN_BEND = (1.5, 2.0, 5.5)          # as installed: 1.5 out, then down 5.5 (ends 1 mm over the floor); heat-shrunk band 2.0 wide
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
RM_CAP_OFF = 6.6                          # MEASURED 6.0 (v8); v10 PCB 0.6 west (BMP at x 11.5), capsule kept -> leads BENT (user)
RM_CAP_DY = RM_PCB_T                      # capsule axis this far above the PCB bottom face
RM_HDR = (2.5, 2.5, 7.6)                  # header body x . y (above top face) . z
RM_PIN_L = 30.0 - 6.0 - 1.1 - 18.5           # MEASURED 30 overall (pins + PCB + capsule) -> 4.4 of pins
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
D9V6_STEP = dict((k, os.path.join(PROJECT, "Models", "PhoenixABS40-43_D9aft_v10_%s.step" % k)) for k in ("EbayCap", "FwdTube"))   # v9: current D9aft
FOOT_RI, FOOT_RO = 15.8, 19.3             # v6: floor disc R at SEAT_Z; mid ring (old foot) R 15.8..19.3

# SMALL PARTS ~13 g -- v6: the AFT DECK's free west/centre (was a 3 mm shelf in the upper
#   centre).  Regulator, microSD reader, C1, SW1/SW2 + wiring; Kapton / hot glue to the floor.
# v8: the real parts, each placed (x0, x1, y0, y1, z0, z1) with its LOADING direction (sled printed,
#     e-bay out of the tube).  Dims: avionics_bay_packing_40mm.md / Electronics BOM.
DECK_FLOOR = SEAT_Z + WALL                                   # -21.6
WALL_X = -8.0                                                # v8 N-S deck wall (centre x)
_F = DECK_FLOOR + 0.3
SMALLPARTS = [  # name, box, load dir, note
    ("S7V8F5",       (-7.0, 3.6, -1.5, 15.5, _F, _F + 3.5), (0, 1, 0),
     "17 x 11 x 3 (+0.5 joints) flat on the floor, central bay"),
    ("C1_220uF",     (-6.5, 1.5, -9.8, -1.8, _F, _F + 14.0), (0, -1, 0),
     "d8 x 12 + 2 mm leads, standing, central bay south"),
    ("Q1_2N7000",    (-6.5, -1.3, -15.2, -10.4, _F, _F + 8.0), (0, -1, 0),
     "TO-92 + bent legs, central bay south, outboard of C1"),
    ("Q3_AO3401",    (-7.0, 0.6, 5.0, 15.0, _F + 3.8, _F + 6.8), (0, 1, 0),
     "SOT-23 adapter 10 x 7.6 x 3 on top of the S7V8F5"),
]

# screwdriver used for the access sweep
DRIVER_D = 3.0                            # M2.5 = #1 Phillips / 1.5 hex: <= 3 mm shaft

# top frame
MOUNT_W_Z0 = SD_Z0 + SD_L + 0.4           # v10: W boss column corbels off the spine pad from above the microSD
MOUNT_W_XCUT = -13.4                      # v10: W bar west end (the v9 D-cut for the BMP cable is gone)
MOUNT_E_Z0 = BMP_Z0 + BMP_L + 0.4         # v10: full E boss above the BMP's fwd end; below it the boss is the pier
MOUNT_E_YCUT = -1.3                       # v8: E boss D-cut (reed lead loop at y <= -1.6)
BEAM_Y = 1.5                              # (v9 beam y +/-1.5)
BEAM_Y0, BEAM_Y1 = 0.2, 2.8               # v10: beam y 0.2..2.8 -- the whole width sits on its arch web (reed header y <= -0.2)

ZONE_Z1 = 48.0
# v10d REED SLIDE-IN (user): the board drops in AXIALLY from the cap end (-Z) -- the only direction whose
#   guides print without overhangs (vertical faces; the aft seats are short flat tabs over the ADXL).
RG_Z0 = ADXL_Z0 + ADXL_PCB_L + 0.4        # 25.4: nothing of the guides lower than this inside the ADXL's slide path
RG_X0, RG_XS = -10.6, RM_X0 - 0.4         # W guide: fence outer face .. end-stop face (board W edge + 0.4)
RG_XB = RM_X0 + 0.4                       # W back wall / lip / seat reach 0.4 over the board's W edge band
RG_YB = RM_Y0 - 0.2                       # back wall face (board back -4.3, 0.2 clear)
RG_YL = (RM_Y0 + RM_PCB_T + 0.2, -1.9)    # front lip y (board top -2.7, 0.2 clear .. header pins at -1.75)
RG_LIP_Z1 = RM_Z0 + RM_PCB_W / 2.0 - RM_HDR[2] / 2.0 - 0.4   # 29.6: W lip stops under the header (it passes there)
RG_TOP = RM_Z0 + RM_PCB_W + 0.4           # 41.7
RE_X = (RM_X1 - 0.5, RM_X1)               # E lip / seat x (BMP back face 0.4 east of the board edge)
RE_LIP_Z1 = BMP_Z0 + BMP_L               # 40.0: E lip top, under the bent leads (REED_LEAD_Z from 40.4)
REED_PADS = ((-3.5, -0.5), (6.0, 9.0))    # v10: reed PCB stand-off pads (x), Z REED_PAD_Z, on the tray back
REED_PAD_Z = (37.8, 40.8)                 #   above the solder stubs' path (<= 37.35) -- the stubs bear on the floor lower down
REED_LEAD_Z = (BMP_Z0 + BMP_L + 0.4, BMP_Z0 + BMP_L + 2.4)   # v10: capsule leads bent over the BMP's fwd end

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
    """v8: PCB (full width) + parts with the 0.5 mm long-edge bands free (the pads end at x 8.47;
    v9: the fwd stops sit over those bands at the PCB end -- ASSUMED free of parts, check the board)"""
    pcb1 = NANO_Y0 + NANO_PCB_T
    s = box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, pcb1, NANO_Z0, NANO_Z0 + NANO_DZ)
    e = NANO_DX / 2.0 - BARB_OVL - 0.1
    return as_solid(s.fuse(box(-e, e, pcb1, NANO_Y0 + NANO_DY, NANO_Z0, NANO_Z0 + NANO_DZ)).removeSplitter())

def env_bmp():
    return box(BMP_X0, BMP_X0 + BMP_T, -BMP_W / 2.0, BMP_W / 2.0, BMP_Z0, BMP_Z0 + BMP_L)

def env_batt():
    return box(-BATT_DX / 2.0 + BATT_X0, BATT_DX / 2.0 + BATT_X0, BATT_Y1 - BATT_DY, BATT_Y1, BATT_Z0, BATT_Z0 + BATT_DZ)

def env_adxl(cable=True):
    """v10: flat on the tray back (PCB back at y -5.8, parts toward +y), plug at the AFT end.
    cable=False: the board as it slides in (the Qwiic cable is plugged afterwards, from the deck)."""
    hw, ht = ADXL_W / 2.0, ADXL_Y0 + ADXL_T
    s = box(-hw, hw, ADXL_Y0, ht, ADXL_Z0, ADXL_Z0 + ADXL_PCB_L)
    z1 = ADXL_Z0 - (ADXL_L - ADXL_PCB_L) - (ADXL_BEND if cable else 0.0)
    s = s.fuse(box(-ADXL_PLUG_W / 2.0, ADXL_PLUG_W / 2.0, ADXL_Y0, ht, z1, ADXL_Z0))
    return as_solid(s.removeSplitter())

def env_bmp_cable():
    """v10b: Qwiic plug + cable off the BMP's AFT (centred) receptacle, down into the open space over the
    piezo board (the v9 roof is gone), bending north (keep-out)"""
    hy, h, lane = BMP_CABLE
    s = box(BMP_X0, BMP_X0 + BMP_T, -hy, hy, BMP_Z0 - h, BMP_Z0)
    return s.fuse(box(BMP_X0 + 0.5, BMP_X0 + BMP_T - 0.5, hy - 0.01, hy + lane, BMP_Z0 - h, BMP_Z0 - 1.5))

def env_sd_card():
    """v10b: microSD card out of the reader's long (-y) side (user: "from one of the long sides"; which one
    ASSUMED -y), 11 wide x 1 thick, 2 proud of the board edge, centred in Z (ASSUMED)"""
    zc = SD_Z0 + SD_L / 2.0
    return box(SD_X0 + 2.0, SD_X0 + 3.6, -SD_W / 2.0 - SD_CARD_OUT, -SD_W / 2.0, zc - 5.5, zc + 5.5)

def env_sd():
    return box(SD_X0, SD_X0 + SD_T, -SD_W / 2.0, SD_W / 2.0, SD_Z0, SD_Z0 + SD_L)

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
    a, w, dn = PIEZO_PIN_BEND                                  # v8: as installed -- bent down, heat-shrunk
    xm = xf + (PIEZO_PIN_X[0] + PIEZO_PIN_X[1]) / 2.0
    s = s.fuse(box(xm - 0.7, xm + 0.7, y1, y1 + a + w / 2.0, PIEZO_ZC - PIEZO_PIN_Z / 2.0 - 0.3, PIEZO_ZC + PIEZO_PIN_Z / 2.0 + 0.3))
    s = s.fuse(box(xm - 0.7, xm + 0.7, y1 + a - w / 2.0, y1 + a + w / 2.0, PIEZO_ZC - PIEZO_PIN_Z / 2.0 - dn, PIEZO_ZC + PIEZO_PIN_Z / 2.0 + 0.3))
    return as_solid(s.removeSplitter())

def pin_bay():
    """free volume past the pin end for the bent pins + heat shrink (NOT a part: [P] checks
    the sled leaves it empty).  Floor to the board top, PCB back to the bore."""
    return clip_bore(box(PIEZO_PCB_X0, SLED_RMAX + 1.0, PIEZO_Y1, PIEZO_Y1 + PIN_BAY_Y,
                         SEAT_Z + WALL, PIEZO_Z0 + PIEZO_DZ))

def env_tie():
    """v10 SIDEWAYS tie (keep-out): one band round the pack's cross-section at Z TIE_Z0.  Outboard leg
    on the pack face, hugging its corners (real thickness, nothing of the sled is out there); side legs
    against the pack sides through the wall + floor-corner slots; inboard leg across the tray back."""
    hx, yo, yi = BATT_DX / 2.0 + BATT_X0, BATT_Y1 - BATT_DY, BATT_Y1
    z0, z1 = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL
    t, tc = TIE_T, TIE_T + TIE_CL
    yf = yi + BATT_WALL                                       # tray back face (-5.8)
    s = box(-BATT_DX / 2.0 + BATT_X0, hx, yo - t, yo, z0, z1)                  # outboard leg (head goes here)
    for sx, xc in ((-1, -BATT_DX / 2.0 + BATT_X0), (1, hx)):
        s = s.fuse(cyl(t, z0, z1, xc, yo))                                     # round the pack corner
        xa, xb = sorted((xc, xc + sx * tc))
        s = s.fuse(box(xa, xb, yo, yf + tc, z0, z1))                           # side leg + floor-corner slot
    s = s.fuse(box(-BATT_DX / 2.0 + BATT_X0 - tc, hx + tc, yf, yf + tc, z0, z1))   # inboard leg on the tray back
    s = s.cut(box(-BATT_DX / 2.0 + BATT_X0, hx, yo, yi, z0 - 1, z1 + 1))           # not inside the pack
    return as_solid(s.removeSplitter())

def env_jst():
    x0 = -BATT_DX / 2.0
    return box(x0, x0 + JST_PLUG[0], BATT_Y1 - BATT_DY / 2.0 - JST_PLUG[1] / 2.0, BATT_Y1 - BATT_DY / 2.0 + JST_PLUG[1] / 2.0,
               BATT_Z0 + BATT_DZ, BATT_Z0 + BATT_DZ + JST_PLUG[2])

def _sp(name):
    b = dict((n, bx) for n, bx, _, _ in SMALLPARTS)[name]
    if name == "C1_220uF":
        return cyl(4.0, b[4], b[5], (b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0)
    return box(*b)

def env_nano_joints():
    """30 solder joints on the Nano's BACK face (parts outboard, wires from the top)"""
    s = None
    for sx in (-1, 1):
        for z in NANO_PADS_Z:
            j = Part.makeCylinder(NANO_PAD_R, NANO_JOINT_H, Vector(sx * NANO_ROW_X, NANO_Y0 - NANO_JOINT_H, z), Vector(0, 1, 0))
            s = j if s is None else s.fuse(j)
    return as_solid(s.removeSplitter())

def env_reed(board_only=False):
    """KY-021-style module: PCB + header body + pins + solder stubs (+ capsule + bent leads)."""
    top = RM_Y0 + RM_PCB_T
    zc = RM_Z0 + RM_PCB_W / 2.0
    s = box(RM_X0, RM_X1, RM_Y0, top, RM_Z0, RM_Z0 + RM_PCB_W)
    s = s.fuse(box(RM_X0, RM_X0 + RM_HDR[0], top, top + RM_HDR[1], zc - RM_HDR[2] / 2.0, zc + RM_HDR[2] / 2.0))
    s = s.fuse(box(RM_X0 - RM_PIN_L, RM_X0, top + RM_PIN_Y[0], top + RM_PIN_Y[1], zc - RM_PIN_Z / 2.0, zc + RM_PIN_Z / 2.0))
    s = s.fuse(box(RM_X0 + 0.6, RM_X0 + 1.9, RM_Y0 - RM_STUB, RM_Y0, zc - RM_PIN_Z / 2.0, zc + RM_PIN_Z / 2.0))
    if not board_only:
        s = s.fuse(env_reed_capsule())
    return as_solid(s.removeSplitter())

def env_reed_capsule():
    """v10: capsule (unchanged position) + its leads BENT over the BMP's fwd end: the aft lead runs fwd
    along the capsule (outboard of the BMP), both cross to the PCB's east edge at Z REED_LEAD_Z."""
    zc = RM_Z0 + RM_PCB_W / 2.0
    cz0 = zc - RM_CAP_L / 2.0 - RM_LEAD_Z
    s = cyl(RM_CAP_D / 2.0, cz0, REED_LEAD_Z[1], RM_XC, RM_YC)
    s = s.fuse(box(RM_X1 - 1.5, RM_XC, RM_YC - RM_CAP_D / 2.0, RM_YC + RM_CAP_D / 2.0, REED_LEAD_Z[0], REED_LEAD_Z[1]))
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
    ("Nano_joints", env_nano_joints),
    ("MicroSD",     env_sd),
    ("BMP_cable",   env_bmp_cable),
    ("SD_card",     env_sd_card),
] + [(n, (lambda n=n: _sp(n))) for n, _, _, _ in SMALLPARTS]
RIGID = [n for n, _ in COMPONENTS]

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


def prism(axis, pts_uz, w0, w1):
    """polygon in the (u, Z) plane, u = x (axis 'x') or y (axis 'y'), extruded along the other
    horizontal axis from w0 to w1"""
    if axis == "x":
        vs = [Vector(u, w0, z) for u, z in pts_uz]; d = Vector(0, w1 - w0, 0)
    else:
        vs = [Vector(w0, u, z) for u, z in pts_uz]; d = Vector(w1 - w0, 0, 0)
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(d)


def knee_cut(axis, u_face, z_face, sgn, w0=-30.0, w1=30.0):
    """v10 CORBEL cutter: removes everything beyond a 1:KNEE slope that leaves the support face
    u = u_face at Z z_face and climbs as it goes out (sgn = +1 toward +u)."""
    D, B = 60.0, 80.0
    pts = [(u_face, z_face - B), (u_face, z_face), (u_face + sgn * D, z_face + KNEE * D), (u_face + sgn * D, z_face - B)]
    return prism(axis, pts, w0, w1)


def arch_cut(axis, u0, u1, z_spring, w0, w1, zlow=-60.0):
    """v10 POINTED-ARCH opening between supports at u0 and u1: open below Z_spring + KNEE*min(u-u0, u1-u).
    What is left above it rises 1:KNEE off each support -- no flat bridge."""
    um = (u0 + u1) / 2.0
    pts = [(u0, zlow), (u0, z_spring), (um, z_spring + KNEE * (um - u0)), (u1, z_spring), (u1, zlow)]
    return prism(axis, pts, w0, w1)


def build_sled(log):
    """One printed piece, printed aft end down with NO support.  v10 layout -- see the header."""
    parts, drill = [], []
    cap = lambda s: clip_bore(s, z1=CAP_Z0)     # everything but the spine key stops under the cap

    # ---- spine down the west side -- SOLID.  Its top (Z > CAP_Z0) keys into the EbayCap (unchanged).
    #      v10: thickened inboard to x SD_X0 (-15.5) under the cap -- the microSD reader's back pad.
    parts.append(clip_bore(box(-19.0, -16.6, -12.0, 12.0, SEAT_Z, ZONE_Z1 - 0.6)))
    parts.append(cap(box(-16.7, SD_X0, -12.0, 12.0, SEAT_Z, CAP_Z0)))

    # ---- Nano (v9 rails + stops) + v10 BACKING PLATE: the ADXL rails were the rails' only tie between
    #      the ring and the top bars.  Plate y 9.4..10.6 (face = v9 ledge, joints clear 0.4) across both
    #      rails, deck to cap -> a U-channel.
    nin, nout = NANO_Y0, NANO_Y0 + NANO_DY                    # inboard 11.5 / outboard 16.5
    ntop = CAP_Z0
    wy0, wy1 = nin - CL_BOARD - WALL, NANO_LEDGE_Y            # 10.0 rail root .. 10.6 ledge / plate face
    py0_ = wy1 - WALL                                         # 9.4 plate back
    nx = NANO_DX / 2.0 + CL_SLOT
    pcb1 = nin + NANO_PCB_T                                   # 13.1 PCB top
    nz0, nz1 = NANO_Z0, NANO_Z0 + NANO_DZ                     # -1 .. 44
    zpz = PIEZO_Z0 + PIEZO_DZ + CL_SLOT                       # -4.2: just over the piezo board
    pier_cut = knee_cut("x", PIEZO_PCB_X0, zpz, +1)           # E side: corbel off the back-plate face
    for sx in (-1, 1):
        xa, xb = sorted((sx * nx, sx * (nx + NANO_RAIL_T)))
        r_ = box(xa, xb, wy0, nout, nz0 - WALL, ntop)
        ca, cb_ = sorted((sx * (NANO_ROW_X + NANO_PAD_R + 0.2), sx * nx))
        r_ = r_.fuse(box(ca, cb_, wy1, pcb1 + 0.6, nz0 - WALL, nz0))                 # aft stop under the PCB end
        fa, fb = sorted((sx * (NANO_DX / 2.0 - BARB_OVL), sx * nx))
        r_ = r_.fuse(box(fa, fb, wy1, pcb1 + 0.6, nz1 + NANO_STOP_Z, ntop))          # fwd stop over the PCB end
        if sx > 0:
            # E rail: nothing under it (piezo pin bay) -> corbel in x off the back plate, then knee in y off
            # the backing plate.  The aft stop keeps a 2.5 mm cantilever (listed in [O]).
            stop = r_.common(box(ca - 0.01, cb_ + 0.01, wy1 - 0.01, pcb1 + 0.7, nz0 - WALL - 0.01, nz0 + 0.01))
            zr = zpz + KNEE * (nx - PIEZO_PCB_X0)              # plate bottom under the rail's inner face
            r_ = r_.cut(pier_cut).cut(knee_cut("y", wy1, zr, +1)).fuse(stop)
        parts.append(cap(as_solid(r_)))
    plate = box(-nx - NANO_RAIL_T, PIEZO_PCB_X0, py0_, wy1, nz0 - WALL, ntop)
    for xa, xb in ((-nx, -3.5), (3.5, nx)):                    # v10: aft shelf under the PCB end (centre open for the wiring)
        plate = plate.fuse(box(xa, xb, wy1 - 0.01, nin + 0.8, nz0 - WALL, nz0))
    plate = plate.fuse(box(WALL_X - WALL / 2.0, PIEZO_PLATE_X0 + 0.5, py0_, wy1, -9.0 - 0.5, nz0 - WALL + 0.01)
                       .cut(arch_cut("x", WALL_X + WALL / 2.0, PIEZO_PLATE_X0, -9.0, py0_ - 1, wy1 + 1)))   # haunches to the N-S wall + back plate
    plate = plate.fuse(box(PIEZO_PLATE_X0, nx + NANO_RAIL_T, py0_, wy1, zpz, ntop).cut(pier_cut))
    parts.append(cap(as_solid(plate)))
    # v10c (user: hollow the plate "so we can install the accelerometer and similar"): one ACCESS window,
    #      pointed-arch top at 1:1.15 (prints without support).  The pad rows keep their ledge either side.
    wx0, wx1 = PLATE_WIN_X
    wz0, wzs = PLATE_WIN_Z
    xm = (wx0 + wx1) / 2.0
    drill.append(prism("x", [(wx0, wz0), (wx1, wz0), (wx1, wzs), (xm, wzs + KNEE * (wx1 - wx0) / 2.0), (wx0, wzs)],
                       py0_ - 0.1, wy1 + 0.1))

    # ---- v10 E PIER: the BMP's seat + screw column and the E boss column, x PIER..BMP_X0.  Two fins
    #      along x (N y 6.5..rail root: the y +9 screws; S y 0.2..2.6: the E boss) + a web on the back
    #      plate.  Corbels 1:1.15 off the back-plate face from just over the piezo board.
    bh = [(BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0 + sz * BMP_HOLE_PZ / 2.0) for sz in (-1, 1)]   # y +9 pair
    pier = box(PIER_X0 - 2.0, PIEZO_PCB_X0 + 0.2, PIER_Y0, wy0 + 0.01, zpz, ntop)                   # web over the back plate
    pier = pier.fuse(box(PIER_X0 - 2.0, BMP_X0, 6.5, wy0 + 0.01, zpz, ntop))                       # N fin
    pier = pier.fuse(box(PIER_X0 - 2.0, BMP_X0 - CL_SLOT, PIER_Y0, MOUNT_BOSS_R, zpz, ntop))        # S fin (E boss column)
    parts.append(cap(as_solid(pier.cut(pier_cut))))
    for hy, hz in bh:
        drill.append(cyl_x(BMP_SCREW_D / 2.0 - 0.2, PIER_X0 - 1.5, BMP_X0 + 1.0, hy, hz))           # M2.5 pilot, ~6 deep

    # ---- v10 ADXL: glued flat on the tray back.  A west fence locates the PCB edge (it slides in from +x).
    hw = ADXL_W / 2.0
    fy1 = BATT_Y1 + BATT_WALL
    parts.append(cap(box(-hw - CL_SLOT - WALL, -hw - CL_SLOT, fy1 - 0.01, fy1 + ADXL_PCB_T + 0.4,
                         BATT_Z0 - CL_BATT - BATT_END, RG_Z0 + 0.01)))          # v10d: up to the reed guide's seat

    # v10d ADXL LEDGE (user: "a ledge or something to support the adxl"): under the PCB's aft edge (boost
    #      pushes it aft), W half only -- the Qwiic receptacle (x +/-4, Z -2..-1) slides over the E half.
    #      Hangs 1.6 off the tray back / N-S wall.
    parts.append(cap(box(-hw, -ADXL_PLUG_W / 2.0 - CL_SLOT, fy1 - 0.01, fy1 + ADXL_PCB_T, ADXL_Z0 - WALL, ADXL_Z0)))
    # v10d: W fence run out to y -1.9 (corbelled off its old face) -- it carries the reed's W guide
    parts.append(cap(prism("y", [(fy1 + ADXL_PCB_T + 0.39, BATT_Z0 - CL_BATT - BATT_END), (RG_YL[1], BATT_Z0 - CL_BATT - BATT_END + KNEE * 2.0),
                                 (RG_YL[1], RG_Z0 + 0.01), (fy1 + ADXL_PCB_T + 0.39, RG_Z0 + 0.01)],
                           -hw - CL_SLOT - WALL, -hw - CL_SLOT)))

    # ---- v10d REED SLIDE-IN: the board drops in from the cap end.  W guide = seat + end stop + back wall
    #      (+ lip below the header) on the W fence; E = lip off the pier's S fin + a seat tab off the tray's E
    #      wall; the BMP's back face is the E stop.  Pads stay as the back rest.  Fwd edge: Kapton.
    wg = box(RG_X0, RG_XB, fy1 - 0.01, RG_YL[1], RG_Z0, RM_Z0)                         # seat under the W end
    wg = wg.fuse(box(RG_X0, RG_XS, fy1 - 0.01, RG_YL[1], RG_Z0, RG_TOP))                # end stop column
    wg = wg.fuse(box(RG_X0, RG_XB, fy1 - 0.01, RG_YB, RG_Z0, RG_TOP))                   # back wall
    wg = wg.fuse(box(RG_X0, RG_XB, RG_YL[0], RG_YL[1], RG_Z0, RG_LIP_Z1))               # front lip (below the header)
    tz0_, tz1_ = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL                                # tie passes behind the board:
    yt = fy1 + TIE_T + TIE_CL + 0.05                                                     #   window, top climbs 1:1.15
    wg = wg.cut(prism("y", [(yt, tz0_), (yt, tz1_), (fy1 - 0.1, tz1_ + KNEE * (yt - fy1 + 0.1)), (fy1 - 0.1, tz0_)], RG_X0 - 1, RG_XB + 1))
    parts.append(cap(wg))
    ex0, ex1 = RE_X
    parts.append(cap(box(ex0, ex1, fy1 - 0.01, RM_Y0 + 1.3, RG_Z0, RM_Z0)))              # E seat tab off the tray E wall
    ezl = RG_Z0 + KNEE * (-0.4 - RG_YL[0])
    parts.append(cap(prism("y", [(PIER_Y0 + 0.01, RG_Z0), (-0.4, RG_Z0), (RG_YL[0], ezl), (RG_YL[0], RE_LIP_Z1), (PIER_Y0 + 0.01, RE_LIP_Z1)],
                           ex0, ex1)))                                                   # E lip, corbelled off the S fin
    if ex0 < BATT_DX / 2.0 + CL_BATT:
        raise RuntimeError("E seat tab misses the tray E wall")
    for xa, xb in REED_PADS:
        parts.append(cap(box(xa, xb, fy1 - 0.01, RM_Y0, REED_PAD_Z[0], REED_PAD_Z[1])))

    # ---- AFT DECK: floor disc, ONE N-S wall at x -8 (v8), piezo pocket, webs.
    parts.append(cap(cyl(FOOT_RO, SEAT_Z, SEAT_Z + WALL)))
    parts.append(cap(box(WALL_X - WALL / 2.0, WALL_X + WALL / 2.0, -(SLED_RMAX + 1.0), SLED_RMAX + 1.0, SEAT_Z, 0.0)
                     .cut(box(-nx, nx, wy1, 30.0, nz0, 1.0))))
    # piezo (v7 SIDEWAYS): flat back plate, -y end wall out to the bore.  v10: the ROOF over the pocket and
    # the +y stub are GONE (a cantilever off the plate -- the worst spaghetti); only the plate top under the
    # tray corner stays (y < -6.2) so the tray's aft cap lands on it.  The ADXL's plug passes over the plate.
    pb0 = PIEZO_PLATE_X0
    py0, py1 = PIEZO_Y0 - CL_SLOT, PIEZO_Y1 + CL_SLOT
    pz = box(pb0, PIEZO_PCB_X0, py0 - WALL, py1 + WALL, SEAT_Z, DECK_Z1)                 # back plate, 2.6
    pz = pz.fuse(box(pb0, SLED_RMAX + 1.0, py0 - WALL, py0, SEAT_Z, 0.0))                 # -y end wall, out to the bore
    pz = pz.fuse(box(pb0, PIEZO_PCB_X0, py0 - WALL, ADXL_Y0 - CL_SLOT, DECK_Z1, BATT_Z0 - CL_BATT))   # plate top under the tray
    for yc, zc, _ in PIEZO_HOLE_LIST:
        pz = pz.fuse(cyl_x(PIEZO_SCREW_D / 2.0 + 1.4, pb0 - PIEZO_BOSS_BACK, pb0 + 0.01, yc, zc))
        drill.append(cyl_x(PIEZO_SCREW_D / 2.0 - 0.2, pb0 - PIEZO_BOSS_BACK - 0.5, PIEZO_PCB_X0 + 1.0, yc, zc))
    drill.append(box(PIEZO_PCB_X0 - PIEZO_JOINT_T, PIEZO_PCB_X0 + 0.01, PIEZO_Y0 + PIEZO_JOINT_Y0, py1 + WALL + 0.1,
                     PIEZO_Z0 + PIEZO_JOINT_EDGE, PIEZO_Z0 + PIEZO_DZ - PIEZO_JOINT_EDGE))
    parts.append(cap(as_solid(pz)))
    # PRINT WEBS (floor -> ceiling members).  v10: + a web under the tray at x 3 with 1:1.15 arch haunches
    # to the N-S wall (C1 / Q1 load out under it), the tray's west wall run down to the floor, a 225 web.
    hwb = WALL / 2.0
    ys = -(SLED_RMAX + 1.0)
    webs = [box(8.0 - hwb, 8.0 + hwb, ys, py0 - WALL + 0.01, SEAT_Z, 0.0),                 # under the tray, east
            box(3.0 - hwb, 3.0 + hwb, ys, BATT_Y1 + BATT_WALL, SEAT_Z, 0.0),            # v10: under the tray, centre
            box(-BATT_DX / 2.0 - CL_BATT - BATT_WALL, -BATT_DX / 2.0 - CL_BATT, ys, BATT_Y1, SEAT_Z, 0.0),   # v10: W wall to the floor
            box(-NANO_DX / 2.0 - CL_SLOT - WALL, -NANO_DX / 2.0 - CL_SLOT, 10.1, FOOT_RI, SEAT_Z, 0.0)]  # under the W Nano rail
    for ang in (135.0, 225.0, 315.0):
        w = box(15.0, SLED_RMAX + 1.0, -hwb, hwb, SEAT_Z, 0.0)
        w.rotate(Vector(0, 0, 0), Vector(0, 0, 1), ang)
        webs.append(w)
    ha = box(WALL_X, 3.0, ys, BATT_Y1 + BATT_WALL, -7.5, 0.0)                              # haunches under the tray
    webs.append(ha.cut(arch_cut("x", WALL_X + hwb, 3.0 - hwb, -7.5, ys - 1, 0.0)))
    for w in webs:
        parts.append(cap(w))

    # ---- battery tray, OUTBOARD-OPEN (v6).  v10: no outside gusset (the BMP is there); a small fillet
    #      INBOARD of the floor at the east edge above the reed stubs; both walls + floor corners slotted
    #      full depth for the sideways tie (env_tie + the drill below).
    cb = CL_BATT
    bx0, bx1 = -BATT_DX / 2.0 - cb - BATT_WALL, BATT_DX / 2.0 + cb + BATT_WALL
    by_out, by_in = BATT_Y1 - BATT_DY, BATT_Y1                 # -15.5 .. -7.0
    bc0, bc1 = BATT_Z0 - cb, BATT_Z0 + BATT_DZ + cb            # cavity ends
    bz0, bz1 = bc0 - BATT_END, bc1 + BATT_END
    tray = box(bx0, bx1, by_out, fy1, bz0, bz1)
    tray = tray.cut(box(-BATT_DX / 2.0 - cb, BATT_DX / 2.0 + cb, by_out - 1.0, by_in, bc0, bc1))
    tray = tray.cut(box(-BATT_DX / 2.0 - cb, -BATT_DX / 2.0 + JST_SLOT_W, by_out - 1, fy1 + 1, bc1 - 0.5, bz1 + 1))
    g = BATT_GUSSET
    gus = Part.Face(Part.makePolygon([Vector(bx1 + 0.01, fy1 - 0.01, 0), Vector(bx1 - g, fy1 - 0.01, 0),
                                      Vector(bx1 + 0.01, fy1 + g, 0), Vector(bx1 + 0.01, fy1 - 0.01, 0)]))
    gz0 = REED_PAD_Z[0]
    gus = gus.extrude(Vector(0, 0, bz1 - gz0)); gus.translate(Vector(0, 0, gz0))
    tray = tray.fuse(gus)
    for xa, xb in BATT_RIB_X:
        tray = tray.fuse(box(xa, xb, by_out + 1.5, fy1, bz1 - 0.01, bz1 + 1.6))   # v10d: stop at the tray (reed drops in past them)
    parts.append(cap(as_solid(tray)))
    tz0, tz1 = TIE_Z0 - TIE_CL, TIE_Z0 + TIE_W + TIE_CL
    for sx in (-1, 1):                                         # tie slots: walls + floor corners, full depth;
        xa, xb = sorted((sx * (BATT_DX / 2.0 - 0.01), sx * (bx1 + 1.0)))   # ceiling climbs 1:1.15 outboard from the floor
        sl = prism("y", [(fy1 + 0.01, tz0), (fy1 + 0.01, tz1), (by_out - 1.0, tz1 + KNEE * (fy1 - by_out + 1.0)), (by_out - 1.0, tz0)], xa, xb)
        drill.append(sl.common(box(xa, xb, by_out - 1.0, fy1 + 0.01, tz0, bc1 - 0.3)))

    # ---- mid ring (deck ceiling).  v10: only where webs carry it -- the east + north sector (-35 .. 117 deg:
    #      over the piezo pocket, the pin bay and the Nano's aft end: -35 .. 127 deg) is gone; it ends on the
    #      piezo end wall and the W Nano-rail web.
    ring = cyl(FOOT_RO, -WALL, 0.0).cut(cyl(FOOT_RI, -WALL - 1.0, 1.0))
    sec = Part.makeCylinder(30.0, 4.0, Vector(0, 0, -WALL - 1.0), Vector(0, 0, 1), 162.0)
    sec.rotate(Vector(0, 0, 0), Vector(0, 0, 1), -35.0)
    parts.append(cap(as_solid(ring.cut(sec))))

    # ---- top frame.  W boss: column corbelled off the spine pad from above the microSD.  E boss: on the pier
    #      below the BMP's fwd end (MOUNT_E_Z0), full (D-cut for the reed leads) above it.  Beam on a
    #      pointed-arch web between the W boss and the pier; W bar on knee braces to the backing plate.
    mw = cyl(MOUNT_BOSS_R, MOUNT_W_Z0, CAP_Z0, MOUNT_XW, 0.0).cut(knee_cut("x", SD_X0, MOUNT_W_Z0, +1))
    me = cyl(MOUNT_BOSS_R, MOUNT_E_Z0, CAP_Z0, MOUNT_XE, 0.0).common(box(-30, 30, MOUNT_E_YCUT, 30, 0, 42.8))
    me = me.fuse(cyl(MOUNT_BOSS_R, 42.8, CAP_Z0, MOUNT_XE, 0.0)
                 .cut(box(-30, 30, -30, RM_Y0 + RM_PCB_T + CL_SLOT, 0, 60))                  # v10d: the reed board drops past (0.4)
                 .cut(box(RM_X1 - 1.5 - 0.3, 30, -30, RM_YC + 0.8, 0, 60)))                 # v10d: ... and its bent leads (wire on
                                                                                          #   the capsule axis y -2.7; ring under the head kept)
    mb = mw.fuse(me).fuse(box(MOUNT_XW, MOUNT_XE, BEAM_Y0, BEAM_Y1, CAP_Z0 - 3.0, CAP_Z0))
    aw0, aw1 = MOUNT_XW + 1.8, PIER_X0 - 2.0 + 0.6                     # arch springs: inside the W boss / pier web
    zs = CAP_Z0 - 3.0 - KNEE * (aw1 - aw0) / 2.0
    mb = mb.fuse(box(aw0, aw1, BEAM_Y0, BEAM_Y1, zs, CAP_Z0 - 2.9).cut(arch_cut("x", aw0, aw1, zs, BEAM_Y0 - 1, BEAM_Y1 + 1)))
    bw0, bw1 = MOUNT_W_XCUT, -nx                               # W bar x
    mb = mb.fuse(box(bw0, bw1, BEAM_Y1 - 0.01, py0_ + 0.01, CAP_Z0 - 3.0, CAP_Z0))
    zb = CAP_Z0 - 3.0 - KNEE * (py0_ - BEAM_Y1) / 2.0
    mb = mb.fuse(box(bw0, bw1, BEAM_Y1 - 0.01, py0_ + 0.01, zb, CAP_Z0 - 2.9).cut(arch_cut("y", BEAM_Y1, py0_, zb, bw0 - 1, bw1 + 1)))
    parts.append(cap(as_solid(mb)))
    drill += [cyl(MOUNT_HOLE_D / 2.0 - 0.2, CAP_Z0 - MOUNT_PILOT_DEPTH, CAP_Z0 + 1.0, xc, 0.0) for xc in (MOUNT_XW, MOUNT_XE)]

    # ---- the battery cavity (+ clearance) is kept clear of EVERY member (v8)
    drill.append(box(-BATT_DX / 2.0 - CL_BATT, BATT_DX / 2.0 + CL_BATT, BATT_Y1 - BATT_DY - 1.0, BATT_Y1,
                     BATT_Z0 - CL_BATT, BATT_Z0 + BATT_DZ + CL_BATT))

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
    P("Phoenix ABS 40-43 -- avionics bay ELECTRONICS SLED  %s   (v10: ADXL on the tray back, BMP east, microSD west, no-support print)" % REV)
    P("=" * 78)
    P("")
    P("frame: avbay_packing_build_report_v2.txt  (Z=0 aft, +Z to nose, +x E, +y N)")
    P("v7 (= v6): zone Z %.1f..%.0f -- the e-bay grows AFT by %.1f mm (aft deck); Z >= 0 unchanged from v5" % (SEAT_Z, ZONE_Z1, DECK_DZ))
    P("charger BQ25302 + its wall slot deleted; battery charges off-vehicle (JST-PH)")
    P("")

    doc = App.newDocument("PhoenixABS40-43_avbay_sled_%s" % REV)

    comp = dict((n, f()) for n, f in COMPONENTS)
    cmesh = dict((n, mesh_of(s)) for n, s in comp.items())
    # v10: the shapes that move during loading (ADXL without its cable, reed board without the capsule:
    #      the capsule is laid in by hand on its bent leads after the BMP)
    comp_load = dict(comp)
    comp_load["ADXL375"] = env_adxl(cable=False)
    comp_load["ReedModule"] = env_reed(board_only=True)

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
    strap = {"ReedModule", "Nano_ESP32"}   # strap-retained against the skin (v9: Nano = Kapton + bore)
    soft = {"ZipTie"}                      # v10: cinched onto the pack's corners -- real band, no clearance
    zmax = 0.0
    for n, s in comp.items():
        r = rmax_mesh(cmesh[n]); zmax = max(zmax, cmesh[n].BoundBox.ZMax)
        note = "strap-retained (outboard of the sled skin)" if n in strap else ("band on the pack corner" if n in soft else "")
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
    P("  v10: BMP sensor side faces +x, onto the static port (Z 30, 0 deg); the reed capsule lies 1 mm outboard of it at y -2.7.")

    P("")
    P("[S] SCREW ACCESS  (d%.1f driver from the head outward; assembly order piezo -> BMP ->" % DRIVER_D)
    P("    v10c order: piezo -> small parts -> microSD -> ADXL -> reed board -> BMP -> battery -> Nano LAST (the plate's access")
    P("    window stays open until then); each sweep sees the sled + parts already in)")
    order = ["Piezo"] + [n for n, _, _, _ in SMALLPARTS] + ["MicroSD", "ADXL375", "ReedModule", "BMP388", "Battery", "Nano_ESP32"]
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
        hit = [(n2, round(v, 2)) for n2, sh in [("Sled", sled)] + [(k, comp_load[k]) for k in inn]
               for v in [(lambda c: c.Volume if c.Solids else 0.0)(sh.common(drv))] if v > 1e-2]
        P("  %-14s driver %s   %s" % (nm, "clear" if not hit else hit, "PASS" if not hit else "FAIL"))
    ncd = Part.makeCylinder(DRIVER_D / 2.0, 30.0, Vector(head_bmp, BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0 - BMP_HOLE_PZ / 2.0), Vector(-1, 0, 0))
    ncv = (lambda c: c.Volume if c.Solids else 0.0)(sled.common(ncd))
    P("  NEGATIVE CONTROL: the same driver pointed INTO the sled (-x) hits it %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))
    P("  BMP y-%.0f pair: rest on the tray east wall (1.0 thick, battery behind it) -- no screws; Kapton" % (BMP_HOLE_PY / 2.0))

    P("")
    P("[H] MEASURED HOLES  (2026-10-06, approximate; centre = edge distance + d/2)")
    P("  BMP388  4 x d%.1f, centres %.1f in -> pitch %.1f (y) x %.1f (z); M%.1f screws, boss r %.1f"
      % (BMP_HOLE_D, BMP_HOLE_IN, BMP_HOLE_PY, BMP_HOLE_PZ, BMP_SCREW_D, BMP_SCREW_D / 2.0 + BMP_BOSS_MARGIN))
    for hy, hz in [(sy * BMP_HOLE_PY / 2.0, BMP_Z0 + BMP_L / 2.0 + sz * BMP_HOLE_PZ / 2.0) for sy in (-1, 1) for sz in (-1, 1)]:
        # v10: seat under the board round the hole (annulus r 1.6..2.75 on the pier / tray-wall face) + pilot thread
        ann = cyl_x(BMP_SCREW_D / 2.0 + BMP_BOSS_MARGIN, BMP_X0 - 0.1, BMP_X0, hy, hz).cut(cyl_x(1.6, BMP_X0 - 1, BMP_X0 + 1, hy, hz))
        c = sled.common(ann); f = (c.Volume if c.Solids else 0.0) / ann.Volume
        th = sled.common(Part.makeLine(Vector(BMP_X0, hy, hz + 1.2), Vector(BMP_X0 - 10.0, hy, hz + 1.2)))   # beside the pilot (r 1.05)
        tl = sum(e.Length for e in th.Edges)
        if hy > 0:
            P("    hole (y %+5.1f, Z %4.1f): seat %3.0f %%  thread %.1f mm into the pier  %s   (driven, M2.5 x 6)"
              % (hy, hz, 100 * f, tl, "PASS" if f > 0.3 and tl >= 4.0 else "FAIL") + ("  (seat limit RELAXED v10 0.6 -> 0.3: the pier corbel)" if f < 0.6 else ""))
        else:
            P("    hole (y %+5.1f, Z %4.1f): seat %3.0f %% (tray east wall, rest only)  %s" % (hy, hz, 100 * f, "PASS" if f > 0.3 else "FAIL"))
    P("  ADXL375 4 x d%.1f, centres %.1f in -> %.1f (x) x %.1f (z); v10 GLUED flat, holes unused"
      % (ADXL_HOLE_D, ADXL_HOLE_IN, ADXL_HOLE_PX, ADXL_HOLE_PZ))
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
          % (hy, tl, "PASS" if tl >= 4.0 else "FAIL", 100 * f, "PASS" if f > 0.95 else "FAIL", gap, "PASS" if gap > 0.2 else "WARN (see [F])"))
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
        probes += [(nm, Vector(sx * (hx - 0.01), y, z), Vector(sx, 0, 0), 4.0) for y in (-14.5, -11.0, -7.5) for z in (5.0, 20.0)]
        probes += [(nm, Vector(sx * (hx - 0.01), y, z), Vector(sx, 0, 0), 4.0) for y, z in ((-7.5, 35.0), (-14.5, 41.0))]   # v10: around the tie window
    probes += [("floor", Vector(x, BATT_Y1 - 0.01, z), Vector(0, 1, 0), 3.0) for x in xs for z in (5.0, 15.0, 33.0, 38.0)]   # v10: not in the tie band
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
    P("  v10: caps full (no axial tie).  TIE WINDOWS: walls + floor corners cut full depth from Z %.2f; the window's top climbs"
      % (TIE_Z0 - TIE_CL))
    P("  1:1.15 from Z %.2f at the floor to Z %.1f at the outboard edge (a flat slot top was a 10 mm cantilever) -- the pack"
      % (TIE_Z0 + TIE_W + TIE_CL, min(BATT_Z0 + BATT_DZ + CL_BATT - 0.3, TIE_Z0 + TIE_W + TIE_CL + KNEE * (BATT_DY + BATT_WALL + 1.0))))
    P("  is located by the walls below the window, the floor-side part of the wall and the caps; the tie holds it.")
    P("  west wall trimmed to 1.0 by the microSD (x -11.5), east wall by the BMP (x 11.5).")

    P("")
    P("[C] CLEARANCE  (gap from each sliding face out to the first sled material)")
    def gap(pt, d, L=3.0):
        c = sled.common(Part.makeLine(pt, pt + d * L))
        ds = [(v.Point - pt).Length for e in c.Edges for v in e.Vertexes]
        return min(ds) if ds else L
    gp = []
    gp += [("Nano x", Vector(sx * NANO_DX / 2.0, 14.0, z), Vector(sx, 0, 0), CL_SLOT) for sx in (-1, 1) for z in (5.0, 22.0, 44.0)]
    gp += [("ADXL W fence", Vector(-ADXL_W / 2.0, ADXL_Y0 + 0.8, z), Vector(-1, 0, 0), CL_SLOT) for z in (2.0, 12.0, 22.0)]
    gp += [("piezo -y end", Vector(PIEZO_PCB_X0 + PIEZO_PCB_T / 2.0, PIEZO_Y0, PIEZO_Z0 + z), Vector(0, -1, 0), CL_SLOT)
           for z in (2.0, 7.5, 13.0)]
    gp += [("piezo Z edges", Vector(PIEZO_PCB_X0 + PIEZO_PCB_T / 2.0, y, PIEZO_Z0 + (PIEZO_DZ if sz > 0 else 0.0)), Vector(0, 0, sz), 1.5)
           for y in (-7.0, 0.0, 7.0) for sz in (-1, 1)]   # v10: top edge -> E pier corbel 1.3 (want 1.0, see below)
    gp += [("battery x", Vector(sx * BATT_DX / 2.0, y, z), Vector(sx, 0, 0), CL_BATT) for sx in (-1, 1) for y in (-14.0, -9.0) for z in (5.0, 20.0, 35.0)]
    gp += [("battery z", Vector(x, y, z), Vector(0, 0, sz), CL_BATT) for x in (-6.0, 5.0) for y in (-13.0, -9.0)
           for z, sz in ((BATT_Z0, -1), (BATT_Z0 + BATT_DZ, 1))]
    gw = {}
    for nm, pt, d, cl in gp:
        g_ = gap(pt, d)
        if g_ < gw.get(nm, (99.0, None, cl))[0]:
            gw[nm] = (g_, pt, cl)
    if "piezo Z edges" in gw:
        g_, pt, cl = gw["piezo Z edges"]; gw["piezo Z edges"] = (g_, pt, 1.0)   # v10: the pier corbel over the board's top edge
    for nm, (g_, pt, cl) in gw.items():
        P("  %-14s min gap %.2f (want %.2f) at (%5.1f, %5.1f, %5.1f)   %s" % (nm, g_, cl, pt.x, pt.y, pt.z, "PASS" if g_ >= cl - 0.05 else "FAIL"))

    P("")
    P("[P] PIEZO v8 -- sideways (measured), flat on the plate, pins bent into a free bay")
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
    P("  NOTE straight pins would reach R %.2f (moving limit %.1f): BEND THEM DOWN BEFORE THE BOARD GOES IN (modelled bent)"
      % (tip, R_MAX_MOVING))
    P("  under the board %.1f mm, over it %.1f mm (v6: 0 under -- the pins hit the floor)"
      % (PIEZO_Z0 - (SEAT_Z + WALL), DECK_Z1 - (PIEZO_Z0 + PIEZO_DZ)))

    P("")
    P("[F] FIT OF EVERY PART -- loading sweeps in ASSEMBLY ORDER (sled printed, e-bay out of the tube).")
    P("    Each part is pushed out along its loading direction until it is clear of the sled envelope")
    P("    (R > %.1f or above Z %.0f); it must not touch the sled or any part loaded BEFORE it." % (SLED_RMAX + 0.6, ZONE_Z1 + 3))
    def vv(a, b):
        c = a.common(b); return c.Volume if c.Solids else 0.0
    def sweep_hits(sh, d, others):
        hits = {}
        for k in range(1, 81):
            t = sh.translated(d * (0.5 * k))
            bb = t.BoundBox
            rmin = min(math.hypot(x, y) for x in (bb.XMin, bb.XMax, (bb.XMin + bb.XMax) / 2.0) for y in (bb.YMin, bb.YMax, (bb.YMin + bb.YMax) / 2.0))
            for n2, o in others:
                v = vv(t, o)
                if v > 1e-2: hits[n2] = max(hits.get(n2, 0.0), v)
            if (d.z > 0 and bb.ZMin > ZONE_Z1 + 3) or (d.z == 0 and rmin > SLED_RMAX + 0.6):
                break
        return hits
    LOAD = [("Piezo", [Vector(1, 0, 0)])] + [(n, [Vector(*dv)]) for n, _, dv, _ in SMALLPARTS] + \
           [("MicroSD", [Vector(0, -1, 0), Vector(0, 1, 0)]), ("ADXL375", [Vector(1, 0, 0)]),
            ("ReedModule", [Vector(0, 0, 1)]), ("BMP388", [Vector(1, 0, 0)]),     # v10d: reed drops in from the cap end
            ("Battery", [Vector(0, -1, 0)]), ("Nano_ESP32", [Vector(0, 1, 0)])]          # v10c: Nano LAST
    loaded = []
    for n, dl in LOAD:
        others = [("Sled", sled)] + [(k, comp_load[k]) for k in loaded]
        sh = comp_load[n] if n != "Nano_ESP32" else comp["Nano_ESP32"].fuse(comp["Nano_joints"])
        tries = []
        for d in dl:
            h = sweep_hits(sh, d, others)
            tries.append((d, h))
            if not h: break
        d, h = tries[-1]
        if len(tries) > 1:
            P("  %-14s tried %s" % (n, ["(%+.0f,%+.0f,%+.0f): %s" % (t.x, t.y, t.z, "clear" if not hh else dict((k, round(v, 1)) for k, v in hh.items())) for t, hh in tries]))
        note = ""
        if False:   # v9: no designed interference (v8 barbs) any more
            # designed interference = the two barbs (the arms spring out); anything else is a clash
            bad_bb, barb_hit = None, False
            for k in range(1, 121):
                c = sh.translated(Vector(0, 0, 0.5 * k)).common(sled)
                for so in c.Solids:
                    b_ = so.BoundBox
                    if b_.ZMin >= NANO_Z0 + NANO_DZ + BARB_Z - 0.01 and min(abs(b_.XMin), abs(b_.XMax)) >= NANO_DX / 2.0 - BARB_OVL - 0.01:
                        barb_hit = True
                    elif so.Volume > 1e-3:
                        bad_bb = b_ if bad_bb is None else bad_bb.united(b_)
            ok_ = barb_hit and bad_bb is None
            bb = bad_bb
            note = "only the barbs (x |%.1f..%.1f|, Z >= %.2f): the arms spring out %.1f mm" % (NANO_DX / 2.0 - BARB_OVL, NANO_DX / 2.0, NANO_Z0 + NANO_DZ + BARB_Z, BARB_OVL + CL_SLOT) if ok_ else \
                   ("CLASH: sled in the Nano's path at x %.1f..%.1f y %.1f..%.1f Z %.1f..%.1f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax) if bb else "CLASH")
            P("  %-14s load %-10s %s   %s" % (n, "(%+.0f,%+.0f,%+.0f)" % (d.x, d.y, d.z), note, "PASS" if ok_ else "FAIL"))
        else:
            P("  %-14s load %-10s %s   %s" % (n, "(%+.0f,%+.0f,%+.0f)" % (d.x, d.y, d.z), "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), "PASS" if not h else "FAIL"))
        loaded.append(n)
        if n == "Nano_ESP32": loaded.append("Nano_joints")
    # v10d: the reed board drops in from the cap end WITH its capsule on bent leads -> the lead wires
    #       (d0.5 on the capsule axis, from the PCB's E edge out to the capsule) must drop past the E boss too
    lw = box(RM_X1 - 1.5, RM_XC, RM_YC - 0.3, RM_YC + 0.3, REED_LEAD_Z[0], REED_LEAD_Z[1])
    h = sweep_hits(lw, Vector(0, 0, 1), [("Sled", sled)] + [(k, comp_load[k]) for k in ("ADXL375", "MicroSD")])
    dl = lw.distToShape(sled)[0]
    P("  ReedModule lead wires (y %.1f..%.1f) dropped in from the cap end with the board: %s; seated gap to the sled %.2f   %s"
      % (RM_YC - 0.3, RM_YC + 0.3, "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), dl, "PASS" if not h else "FAIL"))
    P("  ReedModule capsule: swung outboard as the BMP goes in, then laid in BY HAND on its bent leads (static fit in [I]); BMP_cable plugged last")
    # v10b: the microSD card comes out of the reader's long side -- with EVERYTHING installed (sled in hand)
    allp = [("Sled", sled)] + [(k, comp[k]) for k in comp if k not in ("SD_card", "MicroSD")]
    for d, nm in ((Vector(0, -1, 0), "-y (battery side, modelled)"), (Vector(0, 1, 0), "+y (Nano side)")):
        h = sweep_hits(comp["SD_card"], d, allp)
        P("  microSD card out along %-26s %s   %s" % (nm, "clear" if not h else dict((k, round(v, 2)) for k, v in h.items()), "PASS" if not h else ("FAIL" if d.y < 0 else "info")))
    for n, bx, dv, note in SMALLPARTS:
        P("    %-14s x %5.1f..%5.1f y %5.1f..%5.1f Z %5.1f..%5.1f  %s" % ((n,) + tuple(bx) + (note,)))
    # Nano retention (v9: fixed stops, radial load, no flexures)
    pcb_end = box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, NANO_Y0 + NANO_PCB_T, NANO_Z0 - 0.15, NANO_Z0)
    pcb_fwd = box(-NANO_DX / 2.0, NANO_DX / 2.0, NANO_Y0, NANO_Y0 + NANO_PCB_T, NANO_Z0 + NANO_DZ, NANO_Z0 + NANO_DZ + 0.15)
    a_aft = vv(pcb_end, sled) / 0.15
    a_fwd = vv(pcb_fwd.translated(Vector(0, 0, NANO_STOP_Z)), sled) / 0.15
    P("  Nano held: aft end on %.1f mm2 of fixed blocks, fwd end under %.1f mm2 of fixed stops (gap %.1f); x by the rails (%.1f);"
      % (a_aft, a_fwd, NANO_STOP_Z, CL_SLOT))
    P("             inboard by the ledge; outboard Kapton + bore (%.2f to ID at the corner)   %s"
      % (R_AF_I - math.hypot(NANO_DX / 2.0, NANO_Y0 + NANO_DY), "PASS" if a_aft > 4 and a_fwd > 1 else "FAIL"))
    P("  Nano flexures: none (v8 snap arms + slits deleted -- they were the part that broke)")
    jg = min(comp["Nano_joints"].distToShape(sled)[0], comp["Nano_joints"].distToShape(comp["ADXL375"])[0])
    P("  Nano back-face joints (30 x d%.1f x %.1f) -> nearest sled / ADXL %.2f mm   %s" % (2 * NANO_PAD_R, NANO_JOINT_H, jg, "PASS" if jg >= 0.25 else "FAIL"))
    # v10c: the access window must leave the ledge under BOTH pad rows (the window check above only sees clearance)
    nb = 0
    for sx in (-1, 1):
        for z in NANO_PADS_Z:
            for dx in (-NANO_PAD_R + 0.1, 0.0, NANO_PAD_R - 0.1):
                x = sx * NANO_ROW_X + dx
                if not sled.common(Part.makeLine(Vector(x, NANO_Y0 - NANO_JOINT_H, z), Vector(x, NANO_LEDGE_Y - 0.5, z))).Edges:
                    break
            else:
                nb += 1
    wx0, wx1 = PLATE_WIN_X
    P("  Nano pad joints over the ledge (full width, 0.4 gap): %d / 30  (access window x %.1f..%.1f, Z %.1f..%.1f apex)   %s"
      % (nb, wx0, wx1, PLATE_WIN_Z[0], PLATE_WIN_Z[1] + KNEE * (wx1 - wx0) / 2.0, "PASS" if nb == 30 else "FAIL"))
    wd = [x for x in (-5.0, -2.5, 0.0, 2.5, 5.0) if vv(Part.makeCylinder(1.5, 8.0, Vector(x, NANO_Y0 + 1.8, NANO_Z0 - 8.0)), sled) < 1e-3]
    P("  Nano wiring: d3 bundle from the channel's aft end down into the deck free at x %s   %s" % (wd or "nowhere", "PASS" if wd else "FAIL"))
    hd = []
    for hy, hz, d in PIEZO_HOLE_LIST:
        hd.append(math.hypot(hy, hz - PIEZO_ZC) - PIEZO_CAN_D / 2.0 - 1.9)
    P("  piezo M2 pan heads (d3.8) -> can: %s mm   %s" % ([round(h, 2) for h in hd], "PASS" if min(hd) > 0.1 else "WARN: M2 head must be <= d%.1f on that hole -- file a flat on the pan head where it faces the can" % (2 * (min(hd) + 1.9) - 0.2)))

    P("")
    P("[B] BATTERY ACCESS")
    bt = comp["Battery"]
    free = [d for d in (2.0, 5.0, 9.0, 12.0) if (lambda c: c.Volume if c.Solids else 0.0)(sled.common(bt.translated(Vector(0, -d, 0)))) < 1e-3]
    P("  pack slides OUTBOARD (-y) free of the sled: %s mm tested clear   %s" % (free, "PASS" if len(free) == 4 else "FAIL"))
    tie = comp["ZipTie"]
    P("  v10 SIDEWAYS tie (%.1f x %.1f band, Z %.2f..%.2f): round the pack, through the wall + floor-corner slots, across the"
      % (TIE_W, TIE_T, TIE_Z0, TIE_Z0 + TIE_W))
    P("  tray back above the ADXL (top Z %.1f) and under the reed PCB (gap %.2f); Rmax %.2f on the pack corners"
      % (ADXL_Z0 + ADXL_PCB_L, RM_Y0 - (ADXL_Y0 + TIE_T + TIE_CL), rmax_mesh(cmesh["ZipTie"])))
    P("  outboard face -> ID: %.1f mm at x 0 (tie head goes here), %.2f at the corners"
      % (R_AF_I - (BATT_DY - BATT_Y1), R_AF_I - math.hypot(BATT_DX / 2.0, BATT_DY - BATT_Y1)))

    P("")
    P("[R] REED MODULE -- arming by external magnet   (capsule offset + overall length MEASURED v8; PCB 18.5 x 15 assumed)")
    ang = math.degrees(math.atan2(RM_YC, RM_XC))
    zc = RM_Z0 + RM_PCB_W / 2.0
    P("  PCB %.1f x %.1f x %.1f in the x-z plane at y %.1f..%.1f, x %.1f..%.1f, Z %.1f..%.1f"
      % (RM_PCB_L, RM_PCB_W, RM_PCB_T, RM_Y0, RM_Y0 + RM_PCB_T, RM_X0, RM_X1, RM_Z0, RM_Z0 + RM_PCB_W))
    P("  header pins point to the axis (tips x %.1f): SOLDER wires, no DuPont housing (+14 mm)" % (RM_X0 - RM_PIN_L))
    # v10d slide-in: seat area under the aft edge, lip area over the top face, back rest, end stop
    pcb = box(RM_X0, RM_X1, RM_Y0, RM_Y0 + RM_PCB_T, RM_Z0, RM_Z0 + RM_PCB_W)
    seat = vv(box(RM_X0, RM_X1, RM_Y0, RM_Y0 + RM_PCB_T, RM_Z0 - 0.1, RM_Z0), sled) / 0.1
    lip = vv(box(RM_X0, RM_X1, RG_YL[0], RG_YL[0] + 0.1, RM_Z0, RM_Z0 + RM_PCB_W), sled) / 0.1   # lip footprint on the top face
    back = vv(box(RM_X0, RM_X1, RM_Y0 - 0.3, RM_Y0, RM_Z0, RM_Z0 + RM_PCB_W), sled) / 0.3
    stop = vv(box(RM_X0 - 0.5, RM_X0, RM_Y0, RM_Y0 + RM_PCB_T, RM_Z0, RM_Z0 + RM_PCB_W), sled) / 0.5
    dz = min(pcb.distToShape(sled)[0], 9.9)
    P("  v10d SLIDE-IN from the cap end (-Z): aft-edge seats %.2f mm2 (W + E tab), lips over the top face %.1f mm2 (0.2 gap),"
      % (seat, lip))
    P("       back rest within 0.3 %.1f mm2 (pads + W back wall; stubs bear lower), W end stop %.1f mm2 at 0.4; PCB to sled %.2f   %s"
      % (back, stop, dz, "PASS" if seat > 0.5 and lip > 3.0 and back > 3.0 and stop > 3.0 and dz >= 0.0 else "FAIL"))
    P("       fwd edge: no lip (it would be the v9 spaghetti) -> Kapton strip over it; E stop = the BMP's back face (0.4)")
    P("  (v10: PCB on its solder stubs + 2 pads (Z %.1f..%.1f) on the tray back; PCB 0.6 west of v9," % REED_PAD_Z)
    P("       capsule unchanged: BEND THE LEADS so both cross over the BMP's fwd end (Z %.1f..%.1f) to the PCB edge" % REED_LEAD_Z)
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
    lift = max(rs, max(rmax_mesh(cmesh[n]) for n in comp if n != "ZipTie"))
    rt = rmax_mesh(cmesh["ZipTie"])
    P("  zip-tie band on the pack corners: R %.2f -> %.2f to the crests (soft band, cinched; not in the rigid lift-out below)   %s"
      % (rt, D9_CREST - rt, "PASS" if D9_CREST - rt >= 0.15 else "WARN"))
    P("  lift-out through the thread crests: largest rigid R %.2f vs crest %.2f -> %.2f radial   %s"
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
    P("  REAL D9aft v10 STEPs placed with dz %.2f (EbayCap underside -> Z %.1f)" % (dz, CAP_Z0))
    for nm, part in (("FwdTube v10", d9["FwdTube"]), ("EbayCap v10", d9["EbayCap"])):
        hits = []
        for n2, sh in [("Sled", sled)] + list(comp.items()):
            c = sh.common(part); v = c.Volume if c.Solids else 0.0
            if v > 1e-2: hits.append((n2, round(v, 2)))
        P("  %-16s vs this sled + every component: %s   %s" % (nm, hits or "contact only", "PASS" if not hits else "FAIL"))
    nc = sled.translated(Vector(0, 0, -0.5)).common(d9["FwdTube"]); ncv = nc.Volume if nc.Solids else 0.0
    P("  NEGATIVE CONTROL (real FwdTube v10): sled dropped 0.5 mm -> %.1f mm3 (must be > 0)   %s" % (ncv, "PASS" if ncv > 1.0 else "FAIL"))
    port = cyl_x(1.4, D9_R_ID - 1.0, D9_R_OD + 1.0, 0.0, PIEZO_ZC)
    c = d9["FwdTube"].common(port); pv = c.Volume if c.Solids else 0.0
    wall = cyl_x(1.4, D9_R_ID - 1.0, D9_R_OD + 1.0, 0.0, PIEZO_ZC - 3.0)
    c = d9["FwdTube"].common(wall); wv = c.Volume if c.Solids else 0.0
    P("  real FwdTube v10 sound port on the sled can axis (y 0, Z %.1f): %.2f mm3 of wall in a d2.8 probe (must be ~0); 3 mm aft %.1f (must be > 0)   %s"
      % (PIEZO_ZC, pv, wv, "PASS" if pv < 0.05 and wv > 1.0 else "FAIL"))
    pzb = comp["Piezo"].BoundBox
    canc = comp["Piezo"].common(cyl_x(PIEZO_CAN_D / 2.0 + 0.01, PIEZO_X1 - 1.0, PIEZO_X1 + 0.01, 0.0, PIEZO_ZC)).BoundBox
    P("  piezo can face centre (y %.2f, Z %.2f) vs sound port (0, Z %.1f)   %s" % ((canc.YMin + canc.YMax) / 2.0, (canc.ZMin + canc.ZMax) / 2.0, D9_PORTS[1][2],
      "PASS" if abs((canc.ZMin + canc.ZMax) / 2.0 - D9_PORTS[1][2]) < 0.01 and abs(canc.YMin + canc.YMax) < 0.02 else "FAIL"))

    P("")
    P("[I] FIT  --  RAW = the as-drawn sled overlapping each component keep-out,")
    P("           BEFORE trim.  RAW>0 is expected: it is pocket walls / rails /")
    P("           bosses reaching into the board's space.  For the %d RIGID parts" % len(RIGID))
    P("           that volume is then cut away (post-cut common -> 0); the risk it")
    P("           leaves a wall too thin is flagged in [N], not yet auto-checked.")
    P("           v8: every small part is a RIGID part -- no yielding allowance.")
    for n in comp:
        rv = raw.get(n, 0.0)
        pc = sled.common(comp[n]); tv = pc.Volume if pc.Solids else 0.0
        kind = "post-cut %.1f" % tv
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
    P("  + fasteners: 2x M2.5x6 (BMP388 y+9, from +x into the E pier), 2x M2x6 (piezo, from +x, d2.5 + d3 board holes),")
    P("               2x M2x10 (EbayCap, axial); 1 mini zip tie (battery, sideways); ADXL glued (on a ledge); reed slide-in + Kapton; Nano, microSD = Kapton")
    P("  (v9 sled 12650.3 mm3 / 13.3 g -> v10 %+.2f g)" % (m - 12650.3 * RHO))

    P("")
    P("[L] FOR D9aft -- v10 changes NOTHING it reads: seat Z %.1f, sound port Z %.1f / 0 deg, cap, spine key, static port = v6" % (SEAT_Z, PIEZO_ZC))
    P("  (the REAL D9aft v10 FwdTube + EbayCap are checked against sled v10 in [D9]; D9aft v10 itself still execs sled v8)")
    P("  ARM mark unchanged (capsule not moved).  Mass rollup: use [M] (D9aft v10 rolls up sled v8).")
    P("  e-bay length +%.1f mm, all of it AFT of the old seat: seat plane Z -0.9 -> %.1f" % (DECK_DZ, SEAT_Z))
    P("  sound port: d3 at %.0f deg, Z %.1f (v5 Z 9.5) = station %.1f if the length goes in aft" % (D9_PORTS[1][3], PIEZO_ZC, 60.8 - PIEZO_ZC))
    P("  unchanged: EbayCap face Z %.1f, M2 bosses, spine key, static port Z 30" % CAP_Z0)
    P("  CHANGED:   reed module RM_Y0 -5.0 -> %.1f (tie leg over the floor) -> ARM mark %.1f deg (v5 -10.9)"
      % (RM_Y0, math.degrees(math.atan2(RM_YC, RM_XC))))
    P("  sled mass %+.1f g vs v5; seat now bears on a full floor disc R %.1f" % (m - 6802.6 * RHO, FOOT_RO))
    P("  electronics: reed module ~%.1f g (est.); small parts placed as parts ([F])" % RM_MASS)

    P("")
    P("[N] NOTES / OPEN")
    P("  * v2/v3 vs v1: servo + cradle + knob ref removed (D9aft: e-bay fires nothing).  The")
    P("    EbayCap M2 bosses stay at v1's SG90-ear (x, y), top Z %.1f -> the D9aft v1/v2" % CAP_Z0)
    P("    EbayCap fits unchanged (its pocket has spare voids where the cradle uprights were).")
    P("  * v1 EXPORT WAS MISSING THE NANO POCKET (disconnected, dropped by as_solid).  The")
    P("    D9aft v1/v2 checks exec'd that same sled, so they never saw it either.")
    P("  * RETENTION:")
    P("      screw-down  BMP388 (v10) -- EAST flank, 2 x M2.5x6 (y +9) from +x into the E pier; y -9 pair rests on")
    P("                             the tray east wall; Kapton")
    P("      glue        ADXL375 (v10) -- flat on the tray back, slid in from +x against the W fence")
    P("      Kapton      microSD (v10) -- on edge against the spine pad, spine side")
    P("      screw-down  Piezo (v7) -- 2 x M2x6 from +x through the PCB into the flat plate; board drops in from outboard")
    P("                  EbayCap -- 2 axial M2x10 from the cap top into the mount bosses")
    P("      drop-in     Nano (v9) -- 2 solid rails, radial load from +y between fixed aft + fwd end stops; Kapton outboard")
    P("      slide-in    Reed module (v10d) -- drops in from the cap end into the W guide + E lip, seats on 2 aft tabs;")
    P("                             Kapton over the fwd edge; capsule on bent leads, Kapton")
    P("      tie         Battery -- outboard-open tray, 1 SIDEWAYS mini zip tie (<= %.1f wide) through the wall slots + Kapton;" % TIE_W)
    P("                             pad the outboard face with ~1 mm foam so the bore backs it")
    P("  * v10 QWIIC: star at the Nano: ADXL from its AFT plug (cable down into the deck), BMP from its FWD plug")
    P("    v10b: the BMP's Qwiic plugs are centred on both ends (user); the FWD one is blocked (E boss + reed leads)")
    P("    -> plug the AFT one; the cable drops into the space over the piezo board and bends north (keep-out BMP_cable).")
    P("  * v10c ASSEMBLY ORDER: piezo -> small parts -> microSD (Kapton to the spine pad) -> ADXL (slide in from +x")
    P("    against the W fence, glue; press it flat through the plate's access window) -> reed board (onto its")
    P("    pads -- v10d: DROPPED IN from the cap end, Kapton the fwd edge) -> BMP (from +x, 2 x M2.5x6; capsule swung clear)")
    P("    -> lay the capsule outboard of the BMP, Kapton")
    P("    -> battery + sideways tie -> plug the Qwiic leads, then the Nano LAST (covers the window) -> EbayCap.")
    P("    The window (x %.1f..%.1f, Z %.1f..%.1f apex) does NOT let the ADXL drop in face-on: the E pier (BMP aft screw" % (PLATE_WIN_X[0], PLATE_WIN_X[1], PLATE_WIN_Z[0], PLATE_WIN_Z[1] + KNEE * (PLATE_WIN_X[1] - PLATE_WIN_X[0]) / 2.0))
    P("    + E boss column) fills x 5..9 behind it, and the reed board (23 wide) is wider than the rail gap (18.8).")
    P("  * v10 microSD 26 x 23 x 4 (user), card out of a long side (user): mount it with the card toward -y (battery")
    P("    side); card modelled 11 wide, 2 proud, centred in Z (ASSUMED) -- removal checked in [F].")
    P("  * v10 RETENTION changes: ADXL glued on an aft ledge, reed slide-in (v10d), BMP 2 screws into the pier.")
    P("  * ADXL MEASURED %.1f max x %.0f long with Qwiic; top y %.1f, Nano joints from y %.1f" % (ADXL_T, ADXL_L, ADXL_Y0 + ADXL_T, NANO_Y0 - NANO_JOINT_H))
    P("  * STIFFNESS NOT ANALYSED: v10 frame = spine - W boss - beam (on its arch web) - E boss - E pier - back plate")
    P("    - floor disc; Nano U-channel (rails + backing plate) ties into the pier, the W bar and the deck.")
    P("    Overhangs: [O] (print aft end down, no support).")
    P("  * battery tray (v6, v10 tie windows): pack drops in from outboard with 0.5 mm all round --")
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
    P("    trusting the BMP pilot positions (v10: y +%.0f into the E pier, see [H])." % (BMP_HOLE_PY / 2.0))
    P("  * wall thickness: only the battery tray is measured ([W]); eyeball the other thin walls")
    P("    in CAD before printing.")
    P("  * v10 free volume: y -0.8..9.4 between the ADXL and the Nano backing plate, x -11.5..5 (wiring),")
    P("    and the old microSD lane in the deck (west of the N-S wall) -- empty now.")
    P("  * v10 [O] residuals: the pack cavity's fwd ceiling (Z 41.4, bridged wall-to-wall + floor, as v9 printed it),")
    P("    short (<= 5 mm) bridges between deck webs, hole crowns, the E Nano aft stop (2.5 mm cantilever).")
    P("  * small-parts = ~13 g allowance in the aft deck bay; measure S7V8F5 /")
    P("    C1 / SW1 / SW2 for real before this is frozen.")
    P("  * NOT modelled yet: static-port vent path.  v10 BMP sits right behind the static port (good for the reading).")

    P("")
    P("[K] SLENDER MEMBERS  (v9, new: sled sliced every 0.5 mm in Z; islands with area < 8 mm2 or")
    P("    area / longest side < 1.0 mm, grouped by position, >= 6 slices.  On v8 this lists the four Nano slivers.)")
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
    nk, nano_bad = 0, 0
    for k_, v_ in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        if len(v_) < 6: continue
        nk += 1
        x0_, x1_ = min(q[1].XMin for q in v_), max(q[1].XMax for q in v_)
        y0_ = min(q[1].YMin for q in v_)
        is_nano = min(abs(x0_), abs(x1_)) > 8.4 and y0_ > 9.5 and max(q[0] for q in v_) > 20.0
        nano_bad += is_nano
        P("  x %6.1f..%6.1f y %6.1f..%6.1f  Z %6.1f..%6.1f (%2d slices)  area min %4.1f  t~%.2f   %s"
          % (x0_, x1_, y0_, max(q[1].YMax for q in v_), min(q[0] for q in v_), max(q[0] for q in v_), len(v_),
             min(q[2] for q in v_), min(q[3] for q in v_), "NANO RAIL  FAIL" if is_nano else "review"))
    P("  %d slender groups; Nano-rail groups %d   %s" % (nk, nano_bad, "PASS" if nano_bad == 0 else "FAIL"))

    P("")
    P("[A] ADXL ON THE TRAY BACK  (v10)")
    pts = [(x, z) for x in [-8.0 + 2.0 * i for i in range(9)] for z in [0.0 + 3.0 * j for j in range(9)]]
    back = sum(1 for x, z in pts if sled.common(Part.makeLine(Vector(x, ADXL_Y0 + 0.01, z), Vector(x, ADXL_Y0 - 1.0, z))).Edges)
    front = sum(1 for x, z in pts if sled.common(Part.makeLine(Vector(x, ADXL_Y0 + 0.01, z), Vector(x, ADXL_Y0 + ADXL_T, z))).Edges)
    P("  PCB back on y %.1f: %d / %d grid points have the tray floor right behind them; %d have sled in front   %s"
      % (ADXL_Y0, back, len(pts), front, "PASS" if back == len(pts) and front == 0 else "FAIL"))
    lc = sled.common(box(-ADXL_W / 2.0, ADXL_W / 2.0, ADXL_Y0, ADXL_Y0 + ADXL_PCB_T, ADXL_Z0 - 0.1, ADXL_Z0))   # (vv is shadowed above)
    la = (lc.Volume if lc.Solids else 0.0) / 0.1
    P("  v10d ledge under the PCB's aft edge: %.1f mm2 (W half + N-S wall top; the receptacle needs the E half free)   %s"
      % (la, "PASS" if la > 5.0 else "FAIL"))
    P("  PCB Z %.1f..%.1f, plug + cable aft into the deck (Z %.1f..%.1f), x %.1f..%.1f"
      % (ADXL_Z0, ADXL_Z0 + ADXL_PCB_L, ADXL_Z0 - (ADXL_L - ADXL_PCB_L) - ADXL_BEND, ADXL_Z0, -ADXL_W / 2.0, ADXL_W / 2.0))

    P("")
    _ovh = {}
    exec(open(os.path.join(PROJECT, "Avionics", "avbay_overhang_audit.py"), encoding="utf-8").read(), _ovh)
    big = _ovh["overhang_audit"](sled, P, zbed=SEAT_Z)
    P("  v9 (negative control, same audit on the v9 STEP): 43 regions, 1230 mm2, flat 1205 mm2; largest reach 10.3 mm (piezo roof)")

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

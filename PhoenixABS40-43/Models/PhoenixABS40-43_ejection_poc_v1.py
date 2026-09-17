# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- spring-ejection RELEASE mechanism, proof of concept, v1
    ==  simple sliding-catch version  ==

SOURCE OF TRUTH for the servo-released spring latch (EJECTION_POC_DESIGN.md §7). Every
dimension is a named constant below; edit here and re-run, never edit the
STL/STEP/FCStd.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

REVISION 2026-09-10 (e) -- shaft REJOINED, collar PINNED.  Nothing is glued to the
  piston any more (user brief).
  * PistonHead + Shaft are ONE printed part again -- `PistonShaft`, no socket, no glue
    joint.  rev (d)'s split existed only so the head could print flat while the shaft
    printed axially; (e) prints the WHOLE part axially (shaft horizontal, layers along
    its length) and accepts the d38 head disc printing EDGE-ON with support on its lower
    rim ([10] NOTE).  The handling number is unchanged from the split part -- ~8 N axial
    at the counterbore root -- because that root, not the (gone) socket, was always the
    weak station.  [C]'s shaft-up-vs-axial pair moved into [5b] to keep the edge-on
    orientation defended by a live number.  SHAFT_JOINT_* / SOCKET_CHAMFER deleted;
    SHAFT_TOP_Z -> SHAFT_MERGE_Z; the R0.3 counterbore-root fillet is CB_ROOT_FIL.
  * The CatchCollar is no longer SOLVENT-WELDED.  It is two identical halves that close
    around the shaft and are retained by ONE transverse d1.5 PIN driven along Y through
    half + shaft + half, fitted LAST through the access slot (the d9 collar blocks both
    bores -- same topology that ruled out an integral flange).  Load path: shaft -> pin
    (double shear) -> collar top -> slider.  Costs: the collar grew 2 -> 4 mm so the pin
    clears its top face, which meant DEEPENING the ledge 4 -> 6 mm -- carrier / knob /
    tube-stub bottom / servo keepout all shift ~2 mm aft (derived).  The d1.5 shaft
    cross-hole is the ONLY reduction on the piston: net section ~55% of gross, handling
    side-load ~2 N there ([5b]) -- handle by the head; a d6 CF rod is the robust fix.
    New: COLLAR_PIN_* constants; ledge LEDGE_Z0 = SLIDER_Z0 - 6; PIN_BOT_Z / PIN_TOP_Z
    derived; ejection_poc_test_pins.py grows a COLLAR pin row ([P] cross-checks it).

REVISION 2026-09-08 (d) -- shaft SPLIT + groove DELETED.
  * The d5.4 x 0.8 locating groove and the CatchCollar's internal rib are GONE.  The
    rib was 0.25 mm thick radially (sub-nozzle -- it never printed), so in the printed
    part the groove located nothing and backstopped nothing while costing ~27% of the
    local section and two stress raisers.  The shaft is now genuinely d6 solid end to
    end; the collar BOND (shaft face + the +X split face) is the sole catch load path,
    which is what 6.14 already said it was.
  * PistonShaft is split into PistonHead + Shaft, joined by a d6 blind SOCKET in the
    hub and solvent-welded (SHAFT_JOINT_DEPTH).  The head prints flat (disc down); the
    shaft prints AXIALLY (layers along its length, ~40 MPa in bending vs ~20 interlayer
    -- roughly 2x).  The socket is d6 so a pultruded CF rod drops into the same joint
    later with no other change (10.2).
  * New report section [T] THIN FEATURES: any wall/rib thinner than NOZZLE_W.  Catches
    the (now removed) rib, the collar's D-flat wall (0.05 mm -- prints as a C, not a D;
    accepted, the flat is pinned by the crank-pin sweep, see [5]/6.14), the DummyNose
    relief bands, and the disc rim at the peg holes (10.12).
  * [5] bond area is now the real printable arc (the sub-nozzle D-flat wall excluded),
    not 2*pi*r.  [5b] reports shaft side-load-to-break at the socket mouth every run.
  * [9]'s "shaft unbroken" probe now spans the WHOLE shaft and reports the true minimum
    section (it used to stop just below the groove -- the one reduction that existed).
  * Export paths follow the reorganised tree: Print Files/Ejection System/... and
    .../Print Plate/ (was the flat Print Files/ + Assembled Ready to PRINT/).

REVISION 2026-09-06 (c) -- OPTION B (6.14): the catch is a bonded CatchCollar whose TOP
  face is the upward-facing surface the slider bears on, so the spring load never crosses
  a reduced section.  The 2 mm bridged `lip` became a full-diameter reaction PLATE above
  the slider; a step in the ledge bore is a POSITIVE COCKING STOP so free rise is a design
  number (COLLAR_COCK_GAP, 1.0 mm).  The crank pin is modelled as a solid and swept for
  the first time (10.15).  [5b] load-direction check PASSES from here on.

REVISION 2026-09-06 (b) -- assemblability + first shaft-robustness pass.  Fixed a v1
  defect that made the thing unassemblable: the cage's slider-retaining lip ran straight
  through the d6 shaft (16.5 mm3) at the cocked position -- which is what the shaft was
  being forced against when it snapped during cocking.  Added [5b] load direction,
  shaft-vs-cage, and a full-stroke sweep.  (The d4.0 filleted groove of this revision was
  superseded by (c)'s bonded collar and then removed entirely in (d).)

Frame: Z = 0 at the anchor bulkhead's FORWARD (nose-side) face, +Z toward the nose.
       = station 163 in the vehicle DESIGN.md, i.e. 177 mm forward of the airframe aft face.
       Airframe from PhoenixABS40-43.ork: OD 43.0 / ID 40.0 / wall 1.5.

How it works (the thing that confused the earlier cam version -- this one is plain):
  * The spring drives a PISTON HEAD that carries a d6 SHAFT down its axis, through the
    bulkhead, into the e-bay.  No metal rod.  Head and shaft are ONE printed part
    (`PistonShaft`, revision (e)) with no joint at all; the shaft guides the spring and
    is d6 SOLID for its whole length -- no groove, no neck, no reduced section anywhere
    (rev (e) pass 2 adds one d1.5 cross-hole for the collar pin).  The part prints AXIALLY
    so bending loads in-plane ABS, ~2x interlayer.
  * A flat printed SLIDER sits in a channel across the cage.  A U-notch in its inboard
    end rides round the d6 shaft and its rim bears DOWN on the TOP face of a
    CatchCollar (two identical halves, clamped on through the access slot and retained
    by a transverse d1.5 pin through both halves and the shaft -- rev (e) pass 2; was
    solvent-welded).  Cocked load path: shaft -> collar pin (double shear) -> collar
    top -> slider -> a full-diameter reaction PLATE fused to the cage legs -> 3 M3
    screws -> airframe.
    The knob carries none of it (the load is +Z, the slider moves in X, they are
    orthogonal).  A step in the ledge bore is a positive cocking stop: free rise on
    release is COLLAR_COCK_GAP (1.0 mm), not however far the operator overpressed.
  * The KNOB has an off-centre CRANK PIN (radius CRANK_R) riding a cross-slot in the
    slider. Turn the knob 180 deg and the crank pin swings the slider ~6 mm sideways,
    the notch clears the collar, and the spring fires the piston.
  * ARMED and FIRED are both crank DEAD CENTRES: a push on the slider makes zero torque
    on the knob, so the hold is geometric, not a matter of knob/servo force.  There is
    NO detent (10) -- between ARM and FIRE only friction holds the slider; at ARMED the
    dead centre plus the RBF pin through the knob are the hold.

Everything -- spring, piston, slider, knob, future 9 g servo -- fits the 40 mm bore.

Parts built (ABS, 100% infill):
  TubeStub      -- OD43 / ID40 airframe stand-in, viewing window + access slot
  Cage          -- 4 legs (peg tops) + fixed reaction LEDGE + slider channel + knob journal
                   + the full-diameter reaction PLATE above the slider
  BulkheadDisc  -- d39.5 disc: slides down the d6 shaft over the spring, LOCATES on the
                   4 leg pegs (light push, screws retain), + 3x M3 radial tube screws
  PistonShaft   -- d38 piston disc + d13 hub + d11.5 spring-seat counterbore + d6 SOLID
                   shaft, ONE part, no joint (rev (e)) + d1.6 hub cross-hole (bench
                   tether).  Prints AXIALLY (shaft horizontal); the d38 disc prints
                   edge-on with support.  A d6 CF rod down the finished head is the
                   robust upgrade (10.2)
  Slider        -- notched flat bar; rim bears on the CatchCollar top; crank cross-slot
  CatchCollar   -- d9 x 2.0, D-flatted on -X, d6.1 bore; TWO IDENTICAL HALVES; its TOP
                   face is the catch.  Retained by a transverse d1.5 pin through both
                   halves + the shaft (rev (e) pass 2; was solvent-welded)
  Knob          -- grip + journal + crank-pin bore + D-flat (servo later) + RBF hole
  DummyNose     -- light d39 plug the piston pushes (the "it fired" tell-tale)
  (ServoKeepout)-- SG90 envelope, verification only, never exported
Hardware: NONE metal.  The spring; one PRINTED d3 crank pin + one PRINTED d2 RBF pin
  (ejection_poc_test_pins.py); 3x M3 screws into the airframe.
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
MODELS = os.path.join(PROJECT, "Models")
# The Print Files tree was reorganised by subsystem (see Print Files/README.md).  The
# ejection outputs live under Print Files/Ejection System/ ; the batch plate under
# .../Print Plate/ (was "Assembled Ready to PRINT").  ejection_poc_test_pins.py carries
# the same PRINTS path and must match.  The aft-retention scripts still use the flat
# layout -- that half of the README warning stays true until they are updated too.
PRINTS = os.path.join(PROJECT, "Print Files", "Ejection System")
REV = "v1"

RHO = 1.05e-3                 # ABS 100% infill, g/mm^3
NOZZLE_W = 0.4               # FDM nozzle / extrusion width.  A wall or rib thinner than
                             #   this does not print; thinner than 2x this prints but is
                             #   fragile.  Section [T] checks every thin feature against it.
SIGMA_ABS_INPLANE = 40.0     # MPa, ABS bending stress in-plane (perimeters along the load)
SIGMA_ABS_INTERLAYER = 20.0  # MPa, ABS bending stress across layer boundaries (shaft-up)

# --- airframe ---
R_AF_O = 21.5                 # OD 43.0
R_AF_I = 20.0                 # ID 40.0
R_MAX_MOVING = 19.5           # moving parts stay inside this (running clearance to the bore)
R_MAX_STATIC = 19.9          # fixed structure just has to fit the bore

# --- FDM fit clearances (ABS, 0.4 mm nozzle) -------------------------------------
#   A printed hole shrinks and a printed post grows ~0.1-0.2 mm each, so a nominal
#   "0.1 mm interference" prints as a 0.3-0.5 mm JAM and a nominal 0.0 mm sliding
#   face prints bound solid.  Every moving / removable interface below is DERIVED
#   from one of these, and section [F] of the report checks the resulting gaps by
#   arithmetic (a boolean .common() reads 0 mm3 for both a 0.00 and a 0.50 mm gap,
#   so it cannot tell a working fit from a jammed one -- that is why v1 printed
#   parts that pass every check and still will not go together).
CL_SLIDE = 0.50   # total, a printed part sliding in a printed channel (per axis).
                  #   0.5 not 0.4: the cage lip is a downward-facing bridge over the
                  #   channel (0.2-0.3 mm sag) and the slider base has elephant's foot.
CL_ROT   = 0.40   # radial, a printed shaft turning in a printed journal
CL_BORE  = 0.40   # radial, a printed shaft sliding through a printed bore
CL_PIN   = 0.25   # radial, a loose pin dropped through printed holes (RBF)
CL_PEG   = 0.20   # DIAMETRAL, a locating peg pushed into a printed hole -- a light
                  #   hand push, NOT a snap; the 3x M3 screws are the retention (6.4)
CL_TUBE  = 0.25   # radial, a printed part entering the printed tube bore once (kept
                  #   modest: the disc is thin-walled at the peg-hole circle)
CL_CLAMP = 0.10   # DIAMETRAL, and deliberately NOT a running fit.  The CatchCollar is a
                  #   clamshell that closes AROUND the shaft and is solvent-welded, so it
                  #   never slides along it: a near-zero or even slightly negative bore is
                  #   CORRECT here and a running clearance would be wrong (it would let the
                  #   collar cock over before the bond cures).  Every other CL_* is a
                  #   clearance; this one is a clamp.  Range checked in [F].

# --- spring, as measured (DESIGN.md 7.2) ---
SPRING_OD = 10.0
SPRING_FREE = 85.0
SPRING_SOLID = 45.0          # == cocked length
STROKE = 40.0
SPRING_ID_MIN = 7.2         # assumed (~1.2-1.4 mm wire); the printed shaft must clear this

# --- assumptions CHECKED against, not gated by (DESIGN.md 7.3) ---
F_MAX_ASSUMED = 34.0        # N -- mid of the 7.2 table; re-run when the spring is measured
MU = 0.2                   # printed-ABS / steel sliding
SERVO_TORQUE_NMM = 147.0

# --- bulkhead disc ---
BH_R = R_AF_I - CL_TUBE    # OD 39.5 -- one-time slide into the bore, screws centre it
BH_Z0, BH_Z1 = -8.0, 0.0
SHAFT_R = 3.0              # d6 integral piston shaft
BH_BORE_R = SHAFT_R + CL_BORE  # d6.8 shaft bore (0.4 radial -- the ~105 mm shaft slides in it)
SEAT_R = 5.75             # d11.5 spring-seat counterbore
SEAT_DEPTH = 2.5
SCREW_Z = -4.0            # 3x M3 radial screws, bulkhead <-> airframe
SCREW_R = 1.7
# recovery eyelet -- DROPPED for now (loop a tether round a cage leg if you need one)

# --- vertical stack, DERIVED from STROKE (full 40 mm flight article = one edit) ---
#   The shaft is d6 SOLID the whole way from the socket to the stub end (rev (d): the
#   d5.4 locating groove is deleted), so it threads straight down through the (separate,
#   slide-on) bulkhead disc.  No stop flange: the stroke is limited by the spring
#   reaching free length, and for the first bench fires by a short tether from the
#   piston hub to a cage leg.  Nothing in the load path -- and nothing in the HANDLING
#   path either -- has a reduced section any more.
SLIDER_TOP_Z = BH_Z0 - STROKE - 4.0              # -52  (was SHOULDER_Z -- it no longer names
                                                 #   a feature on the shaft; it anchors the
                                                 #   slider's top plane and the whole stack)
STUB_Z0 = -63.0                                  # d6 shaft runs solid to here (then a lead-in)

# the anchor bulkhead is now TWO parts: an open CAGE, and a DISC that slides down
# the d6 shaft (with the spring) and glues onto the cage-leg tops + screws to the tube.
DISC_GLUE_Z = BH_Z0                              # -8  cage-leg tops / disc underside

# --- slider ---
SLIDER_Z0, SLIDER_Z1 = SLIDER_TOP_Z - 4.0, SLIDER_TOP_Z          # -56 .. -52, 4 mm thick
NOTCH_R = SHAFT_R + CL_BORE   # d6.8 U-notch -- it now rides round the UNBROKEN d6 shaft and
                         #   bears on the CatchCollar's top face, so it only has to clear the
                         #   shaft (6.14).  The release criterion is no longer
                         #   "travel >= NOTCH_R + SHAFT_R" but "the slider is clear of the
                         #   COLLAR footprint at FIRED" -- checked by boolean in [F].
                         #   Do NOT buy clearance with SLIDER_TRAVEL: swept R_max is 19.235
                         #   against 19.5 and that is the thumb tab, which moves 1:1 with travel.
NOTCH_MOUTH_X = 2.0     # U opens toward +X; rails run local -NOTCH_R .. +NOTCH_MOUTH_X
NOTCH_CLOSED_X = -NOTCH_R
SLIDER_TRAVEL = 6.0     # slider moves -X to FIRED; needs >= NOTCH_R + SHAFT_R = 4.8
SLIDER_YW_LO, SLIDER_YW_HI = -4.8, 7.5   # -4.8 not -4.0: keeps 1.4 mm of web between
                                         #   the bigger notch and the -Y edge
SLIDER_X_MIN = -9.0     # -X end of the body, ARMED
CRANK_SLOT_XC = -5.0    # crank-pin cross-slot centre X, ARMED  (= crank pin X at phi 0)
CRANK_SLOT_HW = 1.9     # half width in X (drives the slider); d3 pin
CRANK_SLOT_Y0, CRANK_SLOT_Y1 = -1.5, 6.5                     # long in Y (absorbs crank-pin Y)
RAIL_H = 2.0            # guide rails top + bottom
#   NOTE the slider seats on only ~32% of its footprint, biased to +Y: the ledge centre is
#   necessarily void (the collar has to pass through it, and so does the crank-pin sweep).
#   Inward rail flanges do NOT help -- the ledge already fills everywhere a flange could go;
#   the void is central.  What this costs is slider DROOP when it is unloaded, and the
#   consequence is sized by COLLAR_COCK_GAP -- see [5] 'slider droop at the notch'.

# --- knob + crank ---
KNOB_AX_X, KNOB_AX_Y = -8.0, 0.0        # knob axis, offset -X, clear of the d6 shaft
CRANK_R = SLIDER_TRAVEL / 2.0            # 3.0 ; crank pin radius from the knob axis
CRANK_PIN_R = 1.5                        # d3 crank pin (separate, press-fit or steel)
LEDGE_Z0, LEDGE_Z1 = SLIDER_Z0 - 6.0, SLIDER_Z0            # -62 .. -56 fixed reaction ledge.
#   rev (e): DEEPENED 4 -> 6 mm.  The collar pocket lives inside this, and the collar had
#   to grow 2 -> 4 mm tall so a d1.5 cross-pin fits through it with ~1 mm walls (a d1.5 pin in
#   a 2 mm ring breaks into the load-bearing top face).  Everything below -- carrier, knob,
#   tube-stub bottom, servo keepout -- is DERIVED from LEDGE_Z0 and shifts ~2 mm aft with it.
JOURNAL_R = 4.2                          # d8.4 knob-shaft journal
CARRIER_Z0, CARRIER_Z1 = LEDGE_Z0 - 5.0, LEDGE_Z0          # -67 .. -62
KNOB_SHAFT_R = JOURNAL_R - CL_ROT        # d7.6 in the d8.4 journal (0.4 radial, turns free)
KNOB_Z1 = CARRIER_Z0
KNOB_T = 8.0
KNOB_Z0 = KNOB_Z1 - KNOB_T
KNOB_R = 10.0            # offset knob: KNOB_AX_X (-8) + KNOB_R + scallop must stay < R_MAX_MOVING
DFLAT = 0.6
RBF_KR = -7.0            # RBF hole offset on the knob, + the matching carrier hole.
                         #   Was +6.0, which put the hole at r 2.0 from the TUBE axis -- inside
                         #   the carrier's BH_BORE_R+1 = 4.4 central bore, so it passed through
                         #   the knob and then through thin air.  The RBF pin locked the knob to
                         #   NOTHING (10.16), which is exactly the brownout case requirement 3
                         #   exists for.  -7.0 puts it at r 15.0, in solid carrier, and clear of
                         #   the crank pin, the spigot counterbore and the finger scallops.
RBF_PIN_R = 1.0                          # d2 printed pin / wire / paperclip
RBF_HOLE_R = RBF_PIN_R + CL_PIN          # d2.5 -- drops in by hand, pulls out clean

# --- catch collar (6.14 / rev (e)) -- the catch, on a separate part so the shaft stays solid ---
#   The spring drives the shaft +Z, so the catch needs an UPWARD-facing face on the
#   shaft.  A turned groove can only present one THROUGH ITS NECK, in tension -- which is
#   what kept breaking.  A separate collar puts that face on its own part.
#   rev (e): the collar is no longer SOLVENT-WELDED to the shaft (nothing is glued to the
#   piston).  It is TWO IDENTICAL HALVES (split at y = 0) that close around the shaft and
#   are retained by a single transverse d1.5 PIN driven along Y through half + shaft + half.
#   Load path: shaft -> pin (double shear) -> collar -> collar top -> slider.  The pin is
#   fitted LAST, through the access slot, after the spring and disc are on -- the d9 collar
#   blocks both bores, the same topology that ruled out an integral flange.
CRANK_SWEEP_R = CRANK_R + CRANK_PIN_R           # 4.5  the d3 crank pin's swept disc about the knob axis
COLLAR_R = 4.5                                  # d9 collar
COLLAR_FLAT_X = KNOB_AX_X + CRANK_SWEEP_R + CL_ROT   # -3.1  D-flat, clears the crank-pin sweep.
                                                #   NB only 0.05 mm outside the d6.1 bore edge, so
                                                #   the collar prints as a C, not a D ([T] flags
                                                #   it).  Harmless now the load goes through the
                                                #   PIN, not a bond arc.
COLLAR_Z1 = SLIDER_Z0                           # -56  collar TOP = slider underside = the catch
COLLAR_H = 4.0                                  # rev (e): 2 -> 4 so the cross-pin at mid-height
                                                #   has ~1.2 mm of collar wall above and below it
                                                #   (a pin in a 2 mm ring breaks the top face).
COLLAR_Z0 = COLLAR_Z1 - COLLAR_H                # -60.0
COLLAR_BORE_R = SHAFT_R + CL_CLAMP / 2.0        # d6.1  the halves close to near-contact; the PIN,
                                                #   not the bore fit, locates the collar on the shaft
COLLAR_PIN_R = 0.75                             # d1.5 retaining pin (= CRANK_PIN_R; own row in
                                                #   ejection_poc_test_pins).  d1.5 not d2: a d2
                                                #   cross-hole takes the net tension section at the
                                                #   catch load past the in-plane limit under the
                                                #   rigid-drop DAF ([5b]); d1.5 keeps ~1.2x there
                                                #   and still has 3x on pin shear.
COLLAR_PIN_HOLE_R = COLLAR_PIN_R + 0.025        # d1.55 -- reamed to a LINE-TO-LINE / light press,
                                                #   NOT CL_CLAMP (0.10 dia).  The diametral slop
                                                #   here is lost motion the collar rises before the
                                                #   pin bears -- it goes STRAIGHT into [5b] free
                                                #   rise, so keep it to ~0.05 dia and ream on
                                                #   assembly.  A d1.5 steel dowel takes it to zero.
COLLAR_PIN_Z = (COLLAR_Z0 + COLLAR_Z1) / 2.0    # -58  pin axis, collar mid-height
COLLAR_PIN_LEN = 2.0 * COLLAR_R - 0.4           # 8.6  ends recessed 0.2 mm inside the d9 OD so
                                                #   they clear the LEDGE_COLLAR_R pocket over the stroke
KT_PIN_HOLE = 2.0                               # stress-concentration factor, transverse hole in a
                                                #   round bar, d/D ~ 0.25, bending & tension ([5b]/[9])
COLLAR_COCK_GAP = 1.0                           # collar underside to the ledge stop shelf: the
                                                #   POSITIVE COCKING STOP.  This is the whole
                                                #   free rise, and it is a design property now,
                                                #   not however far the operator overpressed.
LEDGE_STOP_Z = COLLAR_Z0 - COLLAR_COCK_GAP      # -61.0  top of the ledge's stop shelf
LEDGE_COLLAR_R = COLLAR_R + CL_BORE             # 4.9  collar pocket -- also guides the collar
LEDGE_PIN_R = CRANK_SWEEP_R + CL_ROT            # 4.9  the ledge hole the crank pin sweeps through
CARRIER_PIN_R = CRANK_SWEEP_R + CL_ROT          # 4.9  ...and the carrier hole, for the same reason.
                                                #   At JOURNAL_R 4.2 the pin cut 2.2 mm3 out of the
                                                #   carrier: the d3 pin sits at CRANK_R 3 and so
                                                #   reaches r 4.5, outside the d7.6 knob shaft.
#   Opening the journal to 4.9 gives up the knob's lateral bearing, so it moves to a
#   SPIGOT below the carrier, clear of the pin entirely and on a longer moment arm.
#   The spigot zone (CARRIER_Z0 .. +KNOB_SPIG_H) is below STUB_Z0 = -63, clear of the shaft.
KNOB_SPIG_R = 5.5   # <= |RBF_KR| - RBF_HOLE_R so the RBF hole misses the spigot
CARRIER_SPIG_R = KNOB_SPIG_R + CL_ROT   # the counterbore it turns in
KNOB_SPIG_H = 1.5
#   (rev (d): LOC_R / LOC_H / FIL_LOC -- the shaft locating groove -- were DELETED; rev (e):
#   the collar no longer locates at glue-up either -- the transverse pin locates and
#   retains it, and the shaft carries one d1.5 cross-hole for that pin, nothing else.)

# --- piston head + shaft: ONE part again (rev (e)) -----------------------------------
#   rev (d) split PistonShaft into PistonHead + Shaft, socketed + solvent-welded, so the
#   head could print flat while the shaft printed axially.  rev (e) UNDOES that: the two
#   are one printed part with NO internal joint (the user's brief -- nothing glued to the
#   piston).  The whole part prints AXIALLY (shaft laid horizontal, layers along its
#   length -- SIGMA_ABS_INPLANE not SIGMA_ABS_INTERLAYER in bending, ~2x); the price is
#   the d38 head disc printing EDGE-ON, supported on its lower rim ([10] NOTE).
#   A pultruded d6 CF rod is still the robust upgrade (10.2) -- it just epoxies into a
#   d6 hole bored down the finished head instead of a modelled socket.
CB_ROOT_FIL = 0.3                              # R0.3 fillet where the d6 shaft meets the
                                               #   counterbore floor -- the max-moment root when
                                               #   the part is handled by the head.  Peak
                                               #   d(2*SHAFT_R + 2*CB_ROOT_FIL) sits where the
                                               #   spring passes and must clear SPRING_ID_MIN
                                               #   ([F] asserts it -- it carries FIL_ROOT's job).
#   ZF_COUNTERBORE / SHAFT_MERGE_Z are derived in the piston section below (need PIS_Z0).

# --- reaction plate (6.14) -- what the slider actually pushes against ------------
#   v1 reacted the catch into the 2 mm bridged `lip`.  This is a full-diameter plate
#   fused to the legs, bored so the COLLAR passes through it at full stroke.
PLATE_Z0 = SLIDER_Z1 + CL_SLIDE                 # -51.5
PLATE_T = 4.0
PLATE_Z1 = PLATE_Z0 + PLATE_T                   # -47.5
PLATE_BORE_R = COLLAR_R + CL_BORE               # 4.9

# --- the crank pin, as actually fitted (ejection_poc_test_pins.py CRANK_LEN) ---
#   rev (e): DERIVED now (was hard -69.0 / -52.5), so the ~2 mm aft shift from the deepened
#   ledge tracks automatically.  CRANK_LEN in the pins file follows PIN_TOP_Z - PIN_BOT_Z
#   ([P] fails if it drifts).
PIN_BOT_Z = KNOB_Z0 + 4.0                       # 4 mm of engagement in the SOLID knob body
PIN_TOP_Z = SLIDER_Z1 - 0.5                     # up through the ledge, 3.5 mm into the 4 mm slider

# --- cage legs (carrier -> ledge -> disc) ---
LEG_N = 4
LEG_AZ0 = 45.0
LEG_RC = 17.6
LEG_RW = 3.2
LEG_CW = 7.0
# each leg top carries a peg that LOCATES the disc in a blind hole in its underside
# (light hand push -- disc is removable "for the time being"; the 3x M3 tube screws
#  are the actual retention.  NOT a snap -- a real click needs a barbed peg through a
#  relieved hole or cantilever fingers, a redesign; see 6.4)
LEG_PEG_R = 1.5           # d3 peg
LEG_PEG_H = 3.5
DISC_PEG_HOLE_R = LEG_PEG_R + CL_PEG / 2.0   # d3.2 -> 0.2 mm dia clearance, a locating fit
DISC_PEG_HOLE_DEPTH = 5.5                    # clears the 3.5 mm peg + its 1.2 mm lead cone

# --- piston head + shaft (rev (e): ONE part, no joint -- prints axially) ---
PIS_R = 19.0
PIS_T = 8.0
PIS_HUB_R, PIS_HUB_H = 6.5, 4.0
PIS_Z0 = SPRING_SOLID                    # cocked: piston on the 45 mm spring
ZF_COUNTERBORE = PIS_Z0 - SEAT_DEPTH     # 42.5  spring-seat counterbore floor
SHAFT_MERGE_Z = ZF_COUNTERBORE           # 42.5  the d6 shaft runs up to here, then the
                                         #   CB_ROOT_FIL fillet blends it into the d13 hub
PIS_TETHER_Z = PIS_Z0 + PIS_T + PIS_HUB_H / 2.0   # 55  d1.6 bench-tether cross-hole in the hub cap

# --- dummy nose ---
NOSE_R = 19.5             # d39.0 body -- slides free in the bore (was 19.75, dragged)
NOSE_LEN = 25.0
NOSE_WALL = 2.0
NOSE_SHOULDER_R, NOSE_SHOULDER_L = 18.7, 8.0   # d37.4 shoulder -- relieved 0.8 mm under the bands
                                               #   (2x NOZZLE_W) so they print as DISTINCT drag
                                               #   bands (was 19.4, which left them 0.1 mm proud --
                                               #   sub-nozzle, the bands merged into the shoulder [T])
NOSE_BAND_R, NOSE_BAND_W = 19.5, 2.0     # relieved bands: light drag, not a press (was 19.85)

# --- tube stub ---
STUB_Z_TOP = 92.0
STUB_Z_BOT = KNOB_Z0 - 4.0
WIN_AZ, WIN_HALF_DEG = 90.0, 24.0
WIN_Z0, WIN_Z1 = SLIDER_Z1 + 3.0, 56.0
ACC_AZ, ACC_HALF_DEG = 0.0, 24.0
ACC_Z0, ACC_Z1 = CARRIER_Z0 - 2.0, SLIDER_TOP_Z + 4.0

# --- print plate (Ejection System/Print Plate/) ---
#   The plate bundle used to be hand-assembled in a slicer and went stale three
#   revisions running -- at one point it held a Cage whose lip ran through the shaft.
#   It is generated here now, from the same oriented solids that feed Ready to Print/,
#   so it cannot drift again.  Bed size is an ASSUMPTION: set it to your printer.
BED_X, BED_Y = 220.0, 220.0
PLATE_GAP = 12.0          # between parts: ~6 mm of brim each before two brims merge.
                          #   The Cage is 62 mm tall on a small footprint and is the
                          #   one here most likely to want a brim.
PLATE_EDGE = 8.0          # margin from the bed edge

# --- servo keepout (SG90; verification only) ---
SERVO_L, SERVO_W, SERVO_H = 23.0, 12.4, 22.7
SERVO_TOP_Z = KNOB_Z0 + 3.0

# ================================================================ helpers
#   revolve / as_solid / heal / mesh_of lifted verbatim from aft_retention_v1.py


def revolve(pts):
    vs = [Vector(r, 0, z) for r, z in pts]
    wire = Part.Wire(Part.makePolygon(vs + [vs[0]]))
    return Part.Face(wire).revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)


FK = 1.0 - math.sqrt(2.0) / 2.0   # the 45 deg point on a quarter fillet, for 3-point arcs


def revolve_wire(items):
    """revolve(), but the profile may contain arcs so roots can be filleted.
         ('L', r, z)                 line to (r, z)
         ('A', r_mid, z_mid, r, z)   3-point arc to (r, z)"""
    edges = []
    cur = Vector(items[0][1], 0, items[0][2])
    start = cur
    for it in items[1:]:
        if it[0] == 'L':
            nxt = Vector(it[1], 0, it[2])
            edges.append(Part.LineSegment(cur, nxt).toShape())
        else:
            mid = Vector(it[1], 0, it[2])
            nxt = Vector(it[3], 0, it[4])
            edges.append(Part.Arc(cur, mid, nxt).toShape())
        cur = nxt
    edges.append(Part.LineSegment(cur, start).toShape())
    return Part.Face(Part.Wire(edges)).revolve(Vector(0, 0, 0), Vector(0, 0, 1), 360)


def as_solid(shape):
    s = shape.Solids
    if not s:
        return shape
    return s[0] if len(s) == 1 else s[0].multiFuse(s[1:]).Solids[0]


def heal(shape, tag, log):
    before = len(shape.Faces)
    tmp = os.path.join(tempfile.gettempdir(), "healpv1_%s.step" % tag)
    try:
        shape.exportStep(tmp)
        rt = Part.Shape(); rt.read(tmp); os.remove(tmp)
        shape = rt
    except Exception as exc:
        log.append("  ! %s: STEP round-trip skipped (%s)" % (tag, exc))
    shape = as_solid(shape.removeSplitter())
    shape.fixTolerance(1e-7)
    log.append("  heal %-13s faces %3d -> %3d, solids %d, %9.1f mm3"
               % (tag, before, len(shape.Faces), len(shape.Solids), shape.Volume))
    return shape


def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.03,
                                  AngularDeflection=0.2, Relative=False)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0))


def max_radius(mesh):
    return max(math.hypot(v.x, v.y) for v in mesh.Points)


# ================================================================ kinematics
#   knob angle phi in [0, 180].  crank pin (knob frame) at radius CRANK_R:
#       world X = KNOB_AX_X + CRANK_R*cos(phi)   ,  Y = KNOB_AX_Y + CRANK_R*sin(phi)
#   the slider is constrained to X; its cross-slot X-walls follow the crank pin X:
#       slider dX(phi) = CRANK_R*(cos(phi) - 1)        phi 0  -> 0      (ARMED)
#                                                      phi 180 -> -2*CRANK_R  (FIRED)
def slider_dx(phi_deg):
    return CRANK_R * (math.cos(math.radians(phi_deg)) - 1.0)


def crank_pin_world(phi_deg):
    a = math.radians(phi_deg)
    return (KNOB_AX_X + CRANK_R * math.cos(a), KNOB_AX_Y + CRANK_R * math.sin(a))


FIRED_DX = slider_dx(180.0)                       # -6.0

# ================================================================ builds


def build_tubestub():
    t = revolve([(R_AF_I, STUB_Z_BOT), (R_AF_O, STUB_Z_BOT),
                 (R_AF_O, STUB_Z_TOP), (R_AF_I, STUB_Z_TOP)])
    for az, half, z0, z1 in ((WIN_AZ, WIN_HALF_DEG, WIN_Z0, WIN_Z1),
                             (ACC_AZ, ACC_HALF_DEG, ACC_Z0, ACC_Z1)):
        a0, a1 = math.radians(az - half), math.radians(az + half)
        rr = R_AF_O + 3.0
        pts = [Vector(0, 0, z0),
               Vector(rr * math.cos(a0), rr * math.sin(a0), z0),
               Vector(rr * math.cos(a1), rr * math.sin(a1), z0)]
        wedge = Part.Face(Part.Wire(Part.makePolygon(pts + [pts[0]]))).extrude(Vector(0, 0, z1 - z0))
        t = t.cut(wedge)
    for i in range(3):
        a = math.radians(30 + 120 * i)
        t = t.cut(Part.makeCylinder(SCREW_R, 6.0,
                  Vector((R_AF_I - 1) * math.cos(a), (R_AF_I - 1) * math.sin(a), SCREW_Z),
                  Vector(math.cos(a), math.sin(a), 0)))
    return t


def _leg(az_deg, z_bot):
    b = Part.makeBox(LEG_RW, LEG_CW, BH_Z0 - z_bot,
                     Vector(-LEG_RW / 2.0, -LEG_CW / 2.0, z_bot))
    b.Placement = App.Placement(
        Vector(LEG_RC * math.cos(math.radians(az_deg)), LEG_RC * math.sin(math.radians(az_deg)), 0),
        App.Rotation(Vector(0, 0, 1), az_deg))
    return b


def _leg_xy(i):
    a = math.radians(LEG_AZ0 + 360.0 * i / LEG_N)
    return LEG_RC * math.cos(a), LEG_RC * math.sin(a)


def build_cage():
    """Open cage: 4 legs (tops at DISC_GLUE_Z, each with a locating peg) + the fixed
    reaction LEDGE + slider channel + knob carrier/journal. The bulkhead DISC pushes
    down onto the leg pegs (light hand fit) and is held by the 3 M3 tube screws."""
    cg = _leg(LEG_AZ0, CARRIER_Z1)
    for i in range(1, LEG_N):
        cg = cg.fuse(_leg(LEG_AZ0 + 360.0 * i / LEG_N, CARRIER_Z1))
    for i in range(LEG_N):
        px, py = _leg_xy(i)
        peg = cyl(LEG_PEG_R, BH_Z0, BH_Z0 + LEG_PEG_H, px, py)
        peg = peg.fuse(Part.makeCone(LEG_PEG_R, LEG_PEG_R - 1.2, 1.2,   # long lead-in
                                     Vector(px, py, BH_Z0 + LEG_PEG_H), Vector(0, 0, 1)))
        cg = cg.fuse(peg)
    # The fixed LEDGE.  It does NOT take the +Z catch load -- that goes UP into the
    # reaction PLATE (built below).  The ledge hosts the knob journal, carries the slider
    # on its top face, and its stepped bore is the positive cocking stop.  ([5b] confirms
    # the +Z load lands in the plate; report [5] measures the ledge's slider seating and
    # the stop shelf.)
    ledge = revolve([(0, LEDGE_Z0), (BH_R, LEDGE_Z0), (BH_R, LEDGE_Z1), (0, LEDGE_Z1)])
    ledge = ledge.cut(cyl(BH_BORE_R, LEDGE_Z0 - 1, LEDGE_Z1 + 1))
    # collar pocket down to LEDGE_STOP_Z; the d6.8 bore below it is the POSITIVE COCKING
    # STOP -- the collar bottoms on that shelf after COLLAR_COCK_GAP of overpress, so the
    # free rise on release is a design number, not however hard the operator pressed.
    ledge = ledge.cut(cyl(LEDGE_COLLAR_R, LEDGE_STOP_Z, LEDGE_Z1 + 1))
    # the crank pin sweeps a disc of CRANK_SWEEP_R about the knob axis and pokes outside
    # the d7.6 knob shaft, so the LEDGE hole must clear the SWEEP, not the shaft.  At
    # JOURNAL_R (4.2) the pin cut into the ledge by up to 4.9 mm3 -- never caught,
    # because the pin has never been a modelled solid (10.15).
    ledge = ledge.cut(cyl(LEDGE_PIN_R, LEDGE_Z0 - 1, LEDGE_Z1 + 1, KNOB_AX_X, KNOB_AX_Y))
    cg = cg.fuse(ledge)
    # slider channel on the ledge top: side rails + a top lip over the body.
    # The pocket = slider nominal + CL_SLIDE; ALL the slop lives in this fixed pocket
    # so the ledge top (the reaction face) and the notch-under-shoulder engagement
    # stay exactly where they were.  v1 had the rails and lip flush on the slider =
    # a 0.00 mm sliding fit on three faces = bound solid.
    railL = box(SLIDER_X_MIN + FIRED_DX - 2, NOTCH_CLOSED_X + 2,
                SLIDER_YW_LO - RAIL_H, SLIDER_YW_LO - CL_SLIDE / 2.0,
                SLIDER_Z0, SLIDER_Z1 + RAIL_H)
    railR = box(SLIDER_X_MIN + FIRED_DX - 2, NOTCH_CLOSED_X + 2,
                SLIDER_YW_HI + CL_SLIDE / 2.0, SLIDER_YW_HI + RAIL_H,
                SLIDER_Z0, SLIDER_Z1 + RAIL_H)
    cg = cg.fuse(railL).fuse(railR)
    # REACTION PLATE (6.14).  v1 reacted the catch into a 2 mm bridged `lip` -- and that
    # lip also ran straight through the d6 shaft (16.5 mm3), which is what the shaft was
    # forced against while being cocked, and where it broke (10.14).  Replaced by a
    # full-diameter plate fused to the legs, bored PLATE_BORE_R so the COLLAR passes
    # through it over the full 40 mm stroke.
    plate = revolve([(0, PLATE_Z0), (BH_R, PLATE_Z0), (BH_R, PLATE_Z1), (0, PLATE_Z1)])
    plate = plate.cut(cyl(PLATE_BORE_R, PLATE_Z0 - 1, PLATE_Z1 + 1))
    cg = cg.fuse(plate)
    # knob carrier + journal
    car = revolve([(0, CARRIER_Z0), (BH_R, CARRIER_Z0), (BH_R, CARRIER_Z1), (0, CARRIER_Z1)])
    # the crank pin sweeps to CRANK_SWEEP_R, outside the knob shaft, so this hole has to
    # clear the SWEEP, not the shaft (10.15).  The knob's lateral bearing moves to the
    # spigot counterbore below.
    car = car.cut(cyl(CARRIER_PIN_R, CARRIER_Z0 - 1, CARRIER_Z1 + 1, KNOB_AX_X, KNOB_AX_Y))
    car = car.cut(cyl(BH_BORE_R + 1.0, CARRIER_Z0 - 1, CARRIER_Z1 + 1))
    car = car.cut(cyl(CARRIER_SPIG_R, CARRIER_Z0 - 1, CARRIER_Z0 + KNOB_SPIG_H,
                      KNOB_AX_X, KNOB_AX_Y))                      # spigot bearing counterbore
    cg = cg.fuse(car)
    # radial airframe screw holes at the ledge edge
    for i in range(3):
        a = math.radians(30 + 120 * i)
        cg = cg.cut(Part.makeCylinder(SCREW_R - 0.3, 8.0,
                    Vector(R_AF_I * math.cos(a), R_AF_I * math.sin(a),
                           (LEDGE_Z0 + LEDGE_Z1) / 2.0),
                    Vector(-math.cos(a), -math.sin(a), 0)))
    # RBF hole through the carrier (pairs with the knob hole at ARMED)
    cg = cg.cut(cyl(RBF_HOLE_R, CARRIER_Z0 - 1, CARRIER_Z1 + 1,
                    KNOB_AX_X + RBF_KR, KNOB_AX_Y))
    return cg


def build_bulkheaddisc():
    """d39.5 disc: slides down the d6 shaft (over the spring), then LOCATES on the 4
    cage-leg pegs (0.2 mm dia clearance, light hand push; screws retain). d6.8 shaft
    bore, spring-seat counterbore, radial tube screws."""
    d = revolve([(0, BH_Z0), (BH_R, BH_Z0), (BH_R, BH_Z1), (0, BH_Z1)])
    d = d.cut(cyl(BH_BORE_R, BH_Z0 - 1, BH_Z1 + 1))                          # shaft bore
    d = d.cut(cyl(SEAT_R, BH_Z1 - SEAT_DEPTH, BH_Z1 + 1))                    # spring seat (+Z)
    for i in range(LEG_N):                                                   # peg holes (underside)
        px, py = _leg_xy(i)                                                  # entry lead is on
        d = d.cut(cyl(DISC_PEG_HOLE_R, BH_Z0 - 0.5, BH_Z0 + DISC_PEG_HOLE_DEPTH, px, py))  # the peg (1.2 cone)
    for i in range(3):
        aa = math.radians(30 + 120 * i)
        d = d.cut(Part.makeCylinder(SCREW_R, 8.0,
                  Vector(R_AF_I * math.cos(aa), R_AF_I * math.sin(aa), SCREW_Z),
                  Vector(-math.cos(aa), -math.sin(aa), 0)))
    return d


def build_pistonshaft():
    """PistonHead + Shaft as ONE printed part (rev (e)) -- no socket, no glue joint.
    d38 piston disc + d13 hub + d11.5 spring-seat counterbore + R0.3 counterbore-root
    fillet (CB_ROOT_FIL -- the max-moment root when the part is handled by the head) +
    d6 shaft SOLID and unbroken to the stub end + d1.6 hub-cap tether cross-hole.
    Drops into the same cage / disc / collar / spring as rev (d)'s split pair.

    Prints AXIALLY: laid horizontal, perimeters running ALONG the shaft, so bending
    loads in-plane ABS (~SIGMA_ABS_INPLANE) not interlayer (~2x -- [5b]).  The d38 disc
    then prints EDGE-ON and wants support on its lower rim ([10] NOTE); that support
    cost is the price of the shaft strength.  (rev (e) pass 2 cuts one d1.5 cross-hole
    near the stub for the CatchCollar pin -- the only reduction anywhere on the part.)"""
    p = revolve_wire([
        ('L', 0.0, PIS_Z0 + PIS_T + PIS_HUB_H),                  # hub top (Z 57)
        ('L', PIS_HUB_R, PIS_Z0 + PIS_T + PIS_HUB_H),
        ('L', PIS_HUB_R, PIS_Z0 + PIS_T),                        # hub bottom / piston top (Z 53)
        ('L', PIS_R, PIS_Z0 + PIS_T),
        ('L', PIS_R, PIS_Z0),                                    # d38 disc bottom (Z 45)
        ('L', SEAT_R, PIS_Z0),                                   # spring-seat counterbore wall
        ('L', SEAT_R, ZF_COUNTERBORE),                           # counterbore floor (Z 42.5)
        ('L', SHAFT_R + CB_ROOT_FIL, ZF_COUNTERBORE),
        ('A', SHAFT_R + CB_ROOT_FIL * FK, ZF_COUNTERBORE - CB_ROOT_FIL * FK,
              SHAFT_R, ZF_COUNTERBORE - CB_ROOT_FIL),            # R0.3 counterbore-root fillet
        ('L', SHAFT_R, STUB_Z0 + 1.0),                           # d6 shaft, SOLID all the way
        ('L', SHAFT_R - 1.0, STUB_Z0), ('L', 0.0, STUB_Z0),      # 45 deg stub lead-in
    ])
    p = p.cut(Part.makeCylinder(0.8, 4 * PIS_HUB_R,
              Vector(-2 * PIS_HUB_R, 0, PIS_TETHER_Z), Vector(1, 0, 0)))
    # d1.5 CatchCollar-pin cross-hole, along Y, at the collar mid-height (rev (e)).  The only
    # reduction on the part.  Printed axially it is an unsupported side hole -- ream/drill
    # it after printing ([10] NOTE); it is the pin's bearing surface.  Net-section penalty
    # is reported in [5b] (handling) and [9].
    p = p.cut(Part.makeCylinder(COLLAR_PIN_HOLE_R, 4 * SHAFT_R,
              Vector(0, -2 * SHAFT_R, COLLAR_PIN_Z), Vector(0, 1, 0)))
    return as_solid(p)


def load_pins():
    """Import ejection_poc_test_pins as a LIBRARY (it writes its STL when run directly).
    Importing it rather than copying its numbers is what stops the two files drifting --
    which is how the crank pin ended up 3 mm too short to reach the slider."""
    import importlib.util
    path = os.path.join(MODELS, "ejection_poc_test_pins.py")
    spec = importlib.util.spec_from_file_location("poc_pins", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__RUN_MAIN__ = False
    spec.loader.exec_module(mod)
    return mod


def pack_plate(items, log):
    """Shelf-pack (name, shape) onto the bed. Shapes arrive already print-oriented and
    dropped to Z = 0. Returns [(name, placed_shape)] and the used footprint."""
    ent = []
    for n, s in items:
        b = s.BoundBox
        ent.append([n, s, b.XLength, b.YLength])
    ent.sort(key=lambda e: -e[3])                       # tallest row first
    placed, x, y, row_h, used_x = [], PLATE_EDGE, PLATE_EDGE, 0.0, 0.0
    for n, s, w, h in ent:
        if x + w > BED_X - PLATE_EDGE and placed:
            x, y, row_h = PLATE_EDGE, y + row_h + PLATE_GAP, 0.0
        c = s.copy()
        b = c.BoundBox
        c.translate(Vector(x - b.XMin, y - b.YMin, 0))
        placed.append((n, c))
        # Advance from the bbox of the PLACED copy, not from the pre-translate w.  BoundBox
        # is tessellation-derived, so on curved parts it moves ~0.01 mm across a translate;
        # measuring what we actually placed is what makes PLATE_GAP the real gap.
        pb = c.BoundBox
        x = pb.XMax + PLATE_GAP
        used_x = max(used_x, pb.XMax)
        row_h = max(row_h, pb.YLength)
    return placed, used_x, y + row_h


def write_3mf(path, placed):
    """A plain multi-object 3MF -- same shape as the file this replaces (FreeCAD core
    spec, no slicer config), so any slicer opens it with the parts already arranged."""
    import zipfile
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
           ' <metadata name="Application">FreeCAD</metadata>',
           ' <resources>']
    for i, (n, s) in enumerate(placed, start=1):
        pts, facets = mesh_of(s).Topology
        out.append('  <object id="%d" type="model" name="%s">' % (i, n))
        out.append('   <mesh>')
        out.append('    <vertices>')
        out.extend('     <vertex x="%.6g" y="%.6g" z="%.6g" />' % (p.x, p.y, p.z) for p in pts)
        out.append('    </vertices>')
        out.append('    <triangles>')
        out.extend('     <triangle v1="%d" v2="%d" v3="%d" />' % f for f in facets)
        out.append('    </triangles>')
        out.append('   </mesh>')
        out.append('  </object>')
    out.append(' </resources>')
    out.append(' <build>')
    out.extend('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0" />' % i
               for i in range(1, len(placed) + 1))
    out.append(' </build>')
    out.append('</model>')
    NL = chr(10)
    rels = NL.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        ' <Relationship Target="/3D/3dmodel.model" Id="rel0"',
        '  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" />',
        '</Relationships>', ''])
    ctypes = NL.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        ' <Default Extension="rels"',
        '  ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        ' <Default Extension="model"',
        '  ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>',
        '</Types>', ''])
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('3D/3dmodel.model', NL.join(out) + NL)
        z.writestr('_rels/.rels', rels)
        z.writestr('[Content_Types].xml', ctypes)


def build_catchcollar():
    """The catch (6.14 / rev (e)).  A d9 x 4 collar closed around the d6 shaft; its TOP
    face is the upward-facing surface the slider bears down on, so the spring load never
    passes through a reduced section of the SHAFT.  D-flatted on -X to clear the crank
    pin's swept disc.  Printed as TWO IDENTICAL HALVES split at y = 0.
    rev (e): NOT bonded.  A transverse d1.5 PIN driven along Y through half + shaft + half
    retains it -- the halves close, the pin goes in last through the access slot.  The
    pin hole is symmetric about y = 0 so the halves stay identical."""
    c = cyl(COLLAR_R, COLLAR_Z0, COLLAR_Z1)
    c = c.cut(box(COLLAR_FLAT_X - 30, COLLAR_FLAT_X, -30, 30, COLLAR_Z0 - 1, COLLAR_Z1 + 1))
    c = c.cut(cyl(COLLAR_BORE_R, COLLAR_Z0 - 1, COLLAR_Z1 + 1))       # bore on the d6 shaft
    c = c.cut(Part.makeCylinder(COLLAR_PIN_HOLE_R, 4 * COLLAR_R,      # d1.55 pin hole, along Y
              Vector(0, -2 * COLLAR_R, COLLAR_PIN_Z), Vector(0, 1, 0)))
    return as_solid(c)


def collar_half():
    """one of the two identical printed halves (y >= 0)"""
    return build_catchcollar().common(box(-20, 20, 0, 20, COLLAR_Z0 - 1, COLLAR_Z1 + 1))


def build_slider():
    body = box(SLIDER_X_MIN, NOTCH_MOUTH_X, SLIDER_YW_LO, SLIDER_YW_HI,
               SLIDER_Z0, SLIDER_Z1)
    # U-notch, opens toward +X (so retracting the slider -X lets the shaft out)
    body = body.cut(cyl(NOTCH_R, SLIDER_Z0 - 1, SLIDER_Z1 + 1, 0.0, 0.0))
    body = body.cut(box(0.0, NOTCH_MOUTH_X + 1, -NOTCH_R, NOTCH_R, SLIDER_Z0 - 1, SLIDER_Z1 + 1))
    # crank cross-slot: drives in X (walls at +-CRANK_SLOT_HW), long in Y
    body = body.cut(box(CRANK_SLOT_XC - CRANK_SLOT_HW, CRANK_SLOT_XC + CRANK_SLOT_HW,
                        CRANK_SLOT_Y0, CRANK_SLOT_Y1, SLIDER_Z0 - 1, SLIDER_Z1 + 1))
    # thumb tab out the access slot so it can be nudged / see the state by eye
    body = body.fuse(box(SLIDER_X_MIN - 4.0, SLIDER_X_MIN, -3.0, 3.0, SLIDER_Z0, SLIDER_Z1))
    return body


def build_knob():
    k = revolve([(0, KNOB_Z0), (KNOB_R, KNOB_Z0),
                 (KNOB_R, KNOB_Z1 - 1.5), (KNOB_R - 1.5, KNOB_Z1),
                 (KNOB_SPIG_R, KNOB_Z1),                       # spigot: the lateral bearing,
                 (KNOB_SPIG_R, KNOB_Z1 + KNOB_SPIG_H),         #   clear of the crank pin
                 (KNOB_SHAFT_R, KNOB_Z1 + KNOB_SPIG_H),
                 (KNOB_SHAFT_R, CARRIER_Z1 - 0.5),
                 (0, CARRIER_Z1 - 0.5)])
    k.translate(Vector(KNOB_AX_X, KNOB_AX_Y, 0))
    # crank-pin bore -- a PRINTED d3 pin (ejection_poc_test_pins.py) drops in and is
    # glued; sticks up into the slider slot. Bored +0.2 for a printed pin's oversize.
    k = k.cut(cyl(CRANK_PIN_R + 0.2, PIN_BOT_Z, CARRIER_Z1 + 1.0,
                  KNOB_AX_X + CRANK_R, KNOB_AX_Y))
    # D-flat on the exposed grip (servo / knob key)
    k = k.cut(box(KNOB_AX_X + KNOB_R - DFLAT, KNOB_AX_X + KNOB_R + 3,
                  KNOB_AX_Y - KNOB_R - 3, KNOB_AX_Y + KNOB_R + 3, KNOB_Z0 - 1, KNOB_Z0 + KNOB_T * 0.7))
    # finger scallops
    for i in range(6):
        a = 2 * math.pi * i / 6
        k = k.cut(cyl(3.0, KNOB_Z0 - 1, KNOB_Z0 + KNOB_T - 2,
                      KNOB_AX_X + (KNOB_R + 1.2) * math.cos(a),
                      KNOB_AX_Y + (KNOB_R + 1.2) * math.sin(a)))
    # RBF hole (aligns with the carrier hole at ARMED)
    k = k.cut(cyl(RBF_HOLE_R, KNOB_Z0 - 1, KNOB_Z1 + KNOB_SPIG_H + 1,
                  KNOB_AX_X + RBF_KR, KNOB_AX_Y))          # through the spigot too
    return k


def build_nose():
    n = revolve([(0, 0), (NOSE_R, 0), (NOSE_R, NOSE_LEN - 6.0),
                 (NOSE_R - 4.0, NOSE_LEN), (0, NOSE_LEN)])
    n = n.cut(revolve([(0, NOSE_WALL), (NOSE_R - NOSE_WALL, NOSE_WALL),
                       (NOSE_R - NOSE_WALL, NOSE_LEN - 6.0), (0, NOSE_LEN - 3.0)]))
    n = n.fuse(revolve([(0, -NOSE_SHOULDER_L), (NOSE_SHOULDER_R, -NOSE_SHOULDER_L),
                        (NOSE_SHOULDER_R, 0), (0, 0)]))
    for zc in (-NOSE_SHOULDER_L + NOSE_BAND_W, -NOSE_BAND_W):
        n = n.fuse(revolve([(NOSE_SHOULDER_R, zc - NOSE_BAND_W / 2.0),
                            (NOSE_BAND_R, zc - NOSE_BAND_W / 2.0),
                            (NOSE_BAND_R, zc + NOSE_BAND_W / 2.0),
                            (NOSE_SHOULDER_R, zc + NOSE_BAND_W / 2.0)]))
    n = n.cut(cyl(SHAFT_R + 1.0, -NOSE_SHOULDER_L - 1, NOSE_WALL + 1))
    return n.translated(Vector(0, 0, PIS_Z0 + PIS_T + PIS_HUB_H + 18.0))


def servo_keepout():
    return Part.makeBox(SERVO_W, SERVO_L, SERVO_H,
                        Vector(KNOB_AX_X - SERVO_W / 2.0, -SERVO_L / 2.0, SERVO_TOP_Z - SERVO_H))


# ================================================================ verification


def crank_pin_at(phi):
    """The d3 crank pin AS A SOLID.  It has never been one -- it lives in
    ejection_poc_test_pins.py -- so no check has ever swept it against the cage, and it
    was cutting up to 4.9 mm3 out of the ledge (10.15).  Bottom = 6 mm of glued
    engagement in the knob bore; top = PIN_TOP_Z, into the slider slot."""
    x, y = crank_pin_world(phi)
    return cyl(CRANK_PIN_R, PIN_BOT_Z, PIN_TOP_Z, x, y)


def slider_at(shape, phi):
    s = Part.Shape(shape); s.translate(Vector(slider_dx(phi), 0, 0)); return s


def knob_at(shape, phi):
    s = Part.Shape(shape)
    s.rotate(Vector(KNOB_AX_X, KNOB_AX_Y, 0), Vector(0, 0, 1), phi)
    return s


def main():
    log = []
    log.append("=" * 80)
    log.append("Phoenix ABS 40-43 -- ejection POC, sliding-catch %s" % REV)
    log.append("=" * 80)
    log.append("")
    log.append("mechanism:  knob 0..180 deg  ->  crank pin swings  ->  slider moves %.1f mm"
               % (-FIRED_DX))
    log.append("  ARMED phi 0   : crank pin at x %.2f  (dead centre)  notch over the collar"
               % crank_pin_world(0)[0])
    log.append("  FIRED phi 180 : crank pin at x %.2f  (dead centre)  notch cleared"
               % crank_pin_world(180)[0])
    log.append("  catch: pinned CatchCollar, top face Z %.1f = the slider underside; the shaft"
               % COLLAR_Z1)
    log.append("         is d6 SOLID (one d1.5 collar-pin cross-hole); PistonHead + Shaft REJOINED (rev e)")
    log.append("  cocking stop: collar underside Z %.1f onto the ledge shelf Z %.1f = %.1f mm"
               % (COLLAR_Z0, LEDGE_STOP_Z, COLLAR_COCK_GAP))

    doc = App.newDocument("PhoenixABS40-43_ejection_poc")
    log.append("")
    log.append("[1] build + heal")
    raw = [("TubeStub", build_tubestub()), ("Cage", build_cage()),
           ("BulkheadDisc", build_bulkheaddisc()),
           ("PistonShaft", build_pistonshaft()),
           ("Slider", build_slider()), ("CatchCollar", build_catchcollar()),
           ("Knob", build_knob()), ("DummyNose", build_nose())]
    parts = [(n, heal(s, n, log)) for n, s in raw]
    by = dict(parts)
    meshes = dict((n, mesh_of(s)) for n, s in parts)
    keep = servo_keepout()

    log.append("")
    log.append("[2] mass + envelope")
    pr = 0.0
    for n, s in parts:
        m = s.Volume * RHO
        if n not in ("TubeStub", "DummyNose"):
            pr += m
        bb = meshes[n].BoundBox
        log.append("  %-12s %8.1f mm3  %6.2f g   R %5.1f   Z %7.1f .. %6.1f"
                   % (n, s.Volume, m, max_radius(meshes[n]), bb.ZMin, bb.ZMax))
    log.append("  mechanism printed subtotal  %6.2f g  (+ d3 crank pin, R-clip, 3x M3, spring)" % pr)

    log.append("")
    log.append("[0] CONTAINMENT -- fits the d40 bore")
    lim = {"Cage": R_MAX_STATIC, "BulkheadDisc": R_MAX_STATIC, "DummyNose": R_MAX_STATIC,
           "PistonShaft": R_MAX_MOVING, "Slider": R_MAX_MOVING,
           "Knob": R_MAX_MOVING, "CatchCollar": R_MAX_MOVING}
    for n, _ in parts:
        if n == "TubeStub":
            log.append("  %-12s R_max %6.2f   (airframe -- exempt)" % (n, max_radius(meshes[n])))
            continue
        r = max_radius(meshes[n])
        log.append("  %-12s R_max %6.2f  <= %.1f   %s"
                   % (n, r, lim[n], "PASS" if r <= lim[n] + 1e-6 else "FAIL"))
    worst, wphi = 0.0, 0
    for phi in range(0, 181, 6):
        for shp in (slider_at(by["Slider"], phi), knob_at(by["Knob"], phi)):
            r = max_radius(mesh_of(shp))
            if r > worst:
                worst, wphi = r, phi
    log.append("  slider+knob swept 0..180 deg   R_max %6.2f at %d deg  <= %.1f   %s"
               % (worst, wphi, R_MAX_MOVING, "PASS" if worst <= R_MAX_MOVING else "FAIL"))
    kb = mesh_of(keep).BoundBox
    kr = max(math.hypot(kb.XMin, kb.YMin), math.hypot(kb.XMax, kb.YMax),
             math.hypot(kb.XMin, kb.YMax), math.hypot(kb.XMax, kb.YMin))
    log.append("  servo keepout R_corner %5.2f  Z %.1f..%.1f  <= %.1f   %s"
               % (kr, kb.ZMin, kb.ZMax, R_MAX_MOVING, "PASS" if kr <= R_MAX_MOVING else "FAIL"))

    log.append("")
    log.append("[3] watertight")
    for n, s in parts:
        msh = meshes[n]
        err = abs(msh.Volume - s.Volume) / s.Volume * 100.0
        oe = 2 * msh.CountEdges - 3 * msh.CountFacets
        ok = oe == 0 and msh.isSolid() and not msh.hasNonManifolds() and err < 0.3
        log.append("  %-12s %6d facets  err %.3f%%  open %d  %s"
                   % (n, msh.CountFacets, err, oe, "PASS" if ok else "CHECK"))

    log.append("")
    log.append("[4] spring fit + shaft guide + ASSEMBLY")
    col = cyl(SPRING_OD / 2.0 + 0.5, SEAT_DEPTH, SPRING_SOLID - SEAT_DEPTH).cut(
        cyl(SHAFT_R + 0.4, -1.0, SPRING_SOLID + 1.0))
    hb = col.common(by["BulkheadDisc"]).Volume + col.common(by["Cage"]).Volume
    hp = col.common(by["PistonShaft"]).Volume
    log.append("  cocked spring (free coils) clear of disc + cage  %7.2f mm3  %s"
               % (hb, "PASS" if hb < 1.0 else "FAIL"))
    log.append("  cocked spring (free coils) clear of head + shaft %7.2f mm3  %s"
               % (hp, "PASS" if hp < 1.0 else "FAIL"))
    log.append("  d6 shaft vs assumed spring ID >= %.1f    %s"
               % (SPRING_ID_MIN, "PASS" if 2 * SHAFT_R < SPRING_ID_MIN else "FAIL"))
    for label, dz in (("cocked", 0.0), ("fired ", STROKE)):
        sh = Part.Shape(by["PistonShaft"]); sh.translate(Vector(0, 0, dz))
        eng = sh.common(cyl(BH_BORE_R + 2, BH_Z0, BH_Z1)).BoundBox.ZLength
        log.append("  %s: shaft engaged in disc bore %4.1f mm   %s"
                   % (label, eng, "PASS" if eng >= 5.0 else "FAIL"))
    # ASSEMBLY: the spring and the disc must slide onto the shaft from the STUB end
    # -> nothing on the shaft below the disc's rest Z (BH_Z0) may exceed the bore.
    below = Part.Shape(by["PistonShaft"]).common(
        cyl(30, STUB_Z0 - 2, BH_Z0)).cut(cyl(BH_BORE_R, STUB_Z0 - 3, BH_Z0 + 1))
    log.append("  nothing on the shaft below Z %.0f fouls the d%.1f bore (slide-on)  %6.2f mm3  %s"
               % (BH_Z0, 2 * BH_BORE_R, below.Volume, "PASS" if below.Volume < 1.0 else "FAIL"))
    # cage pegs locate in the disc holes: peg solid, hole clear, a light-clearance fit
    px0, py0 = _leg_xy(0)
    peg_hit = by["Cage"].common(cyl(2.5, BH_Z0, BH_Z0 + LEG_PEG_H, px0, py0)).Volume
    hole_open = by["BulkheadDisc"].common(cyl(DISC_PEG_HOLE_R - 0.3, BH_Z0, BH_Z0 + 2, px0, py0)).Volume
    fit_dia = (DISC_PEG_HOLE_R - LEG_PEG_R) * 2.0             # + = diametral clearance (locating fit)
    log.append("  leg peg present %5.1f mm3 ; disc hole open %5.2f mm3 ; locating fit %+.2f mm dia   %s"
               % (peg_hit, hole_open, fit_dia,
                  "PASS" if peg_hit > 3.0 and hole_open < 0.5 and 0.1 <= fit_dia <= 0.4 else "FAIL"))

    log.append("")
    log.append("[F] FDM FIT GAPS -- arithmetic on the clearance block, no booleans")
    log.append("    a boolean .common().Volume reads 0 mm3 for a 0.00 mm gap AND a 0.50 mm")
    log.append("    gap, so every check below [5]/[7] passed on v1's jammed parts. THIS is")
    log.append("    the check that a fit is loose enough to actually go together / move.")
    #  name                              gap value                          lo    hi   running
    gaps = [
        ("slider top under the lip       ", CL_SLIDE,                          CL_SLIDE, None, True),
        ("slider each side vs the rails  ", CL_SLIDE / 2.0,                    CL_SLIDE / 2.0, None, True),
        ("d6 shaft in the disc bore  rad ", BH_BORE_R - SHAFT_R,              CL_BORE, None, True),
        ("knob shaft in the journal  rad ", JOURNAL_R - KNOB_SHAFT_R,         CL_ROT, None, True),
        ("RBF pin in knob + carrier  rad ", RBF_HOLE_R - RBF_PIN_R,           CL_PIN, None, True),
        ("locating peg in disc hole  dia ", (DISC_PEG_HOLE_R - LEG_PEG_R) * 2.0, 0.10, 0.40, False),
        ("disc OD to the tube bore   rad ", R_AF_I - BH_R,                    CL_TUBE, None, False),
        ("crank pin in the drive slot  X ", CRANK_SLOT_HW - CRANK_PIN_R,      0.20, None, True),
        ("U-notch round the d6 shaft rad ", NOTCH_R - SHAFT_R,                CL_BORE, None, True),
        ("collar in the ledge pocket  rad", LEDGE_COLLAR_R - COLLAR_R,        CL_BORE, None, True),
        ("collar under the plate bore rad", PLATE_BORE_R - COLLAR_R,          CL_BORE, None, True),
        ("crank pin sweep in the ledge   ", LEDGE_PIN_R - CRANK_SWEEP_R,      CL_ROT, None, True),
        ("collar D-flat vs the pin sweep ", COLLAR_FLAT_X - (KNOB_AX_X + CRANK_SWEEP_R),
                                                                              CL_ROT, None, True),
        ("slider -Y web at the notch     ", abs(SLIDER_YW_LO) - NOTCH_R,      1.20, None, False),
        ("knob spigot in its counterbore ", CARRIER_SPIG_R - KNOB_SPIG_R,      CL_ROT, None, True),
        # absolute bounds, NOT +-CL_CLAMP: deriving the target from the same constant as the
        # gap makes the row unfailable.  A clamshell wants ~zero; +-0.15 dia is the limit
        # before it will not close / it rattles before the pin goes in.
        ("collar CLAMP on the shaft  dia", (COLLAR_BORE_R - SHAFT_R) * 2.0,   -0.15, 0.15, False),
        # the collar pin: reamed line-to-line / light press, NOT CL_CLAMP -- the diametral
        # slop here goes straight into [5b] free rise (collar rises this far before the pin
        # bears), which has a 0.10 mm budget, so cap it well under that here as a tripwire.
        ("collar pin fit in its hole  dia", (COLLAR_PIN_HOLE_R - COLLAR_PIN_R) * 2.0, -0.02, 0.07, False),
        # the pin ends must clear the LEDGE_COLLAR_R pocket the collar rides in over the stroke
        ("collar pin end in the ledge pocket", LEDGE_COLLAR_R - COLLAR_PIN_LEN / 2.0, CL_BORE, None, True),
        # rev (e): PistonHead + Shaft are ONE part -- no socket.  The counterbore-root
        # fillet peak still sits where the spring passes, so it carries FIL_ROOT's old
        # constraint against SPRING_ID_MIN.
        ("cbore-root fillet peak vs spring", SPRING_ID_MIN - 2 * (SHAFT_R + CB_ROOT_FIL),
                                                                              0.0, None, False),
        # the spring's top coil must land on a real annulus of the counterbore floor,
        # outside the d6 shaft.  Land = SEAT_R - SHAFT_R ; needs ~1 wire width so SEAT_R
        # and SHAFT_R can't drift together silently.  ([4]'s clearance check reads 0 mm3
        # whether the seat exists or not -- the same blind spot as 6.11.)
        ("spring-seat land vs the d6 shaft", SEAT_R - SHAFT_R,                1.2, None, False),
    ]
    allok = True
    for name, g, lo, hi, _run in gaps:
        ok = (lo is None or g >= lo - 1e-6) and (hi is None or g <= hi + 1e-6)
        allok = allok and ok
        rng = ">= %.2f" % lo if hi is None else "%.2f..%.2f" % (lo, hi)
        log.append("  %s %+.2f mm   %-12s %s" % (name, g, rng, "PASS" if ok else "FAIL"))
    thin = min((g for _n, g, _lo, _hi, run in gaps if run))
    thin_name = next(n for n, g, _lo, _hi, run in gaps if run and g == thin)
    log.append("  --> all fit gaps %s ; thinnest running gap %.2f mm (%s) -- scrape/sand"
               % ("PASS" if allok else "FAIL", thin, thin_name.strip()))
    log.append("      there first if a part still binds")

    log.append("")
    log.append("[T] THIN FEATURES -- solid thinner than one NOZZLE_W (%.1f mm) does not print" % NOZZLE_W)
    log.append("    [F] checks gaps BETWEEN parts; [T] checks thin solid INSIDE one part -- the")
    log.append("    class that silently dropped the collar's 0.25 mm locating rib (now deleted).")
    log.append("    NB these rows are NAMED features, not a general scan: each is tied to live")
    log.append("    constants (so a bad edit fails it) but a NEW thin feature elsewhere is not")
    log.append("    caught until it gets a row here.")
    tfeat = [
        # name, value, accepted?, pointer shown when it is under 2x NOZZLE_W
        ("collar wall at the D-flat (y=0)  ", COLLAR_BORE_R + COLLAR_FLAT_X, True,
         "the collar prints as a C, not a D.  ACCEPTED and can't be fixed in this layout: "
         "the flat is pinned at exactly CL_ROT off the crank-pin sweep and the d6.1 bore "
         "can't shrink.  Harmless now the load goes through the PIN, not a bond arc "
         "(that -X side is inside the notch anyway).  Do NOT read this FAIL as a regression."),
        ("collar wall around the pin hole  ", COLLAR_Z1 - (COLLAR_PIN_Z + COLLAR_PIN_HOLE_R), False,
         "the d1.5 pin hole eats into the 4 mm collar; wall to the top/bottom face.  If this "
         "goes sub-2x-nozzle, raise COLLAR_H (and deepen LEDGE_Z0 to keep the stop shelf)."),
        ("DummyNose drag band relief       ", NOSE_BAND_R - NOSE_SHOULDER_R, False,
         "was 0.10 mm (sub-nozzle -- the relieved bands merged into the shoulder and the "
         "nose printed as one full-length friction surface)."),
        ("disc rim wall at the peg holes   ", BH_R - (LEG_RC + DISC_PEG_HOLE_R), False,
         "10.12 -- prints, but fragile.  If a peg hole splits on assembly, pull LEG_RC in 0.5."),
    ]
    for name, v, acc, note in tfeat:
        if v < NOZZLE_W - 1e-6:
            state = "FAIL (ACCEPTED -- see below)" if acc else "FAIL -- will not print"
        elif v < 2 * NOZZLE_W - 1e-6:
            state = "thin -- fragile"
        else:
            state = "PASS"
        log.append("  %s %+.2f mm  vs %.1f   %s" % (name, v, NOZZLE_W, state))
        if v < 2 * NOZZLE_W - 1e-6:
            log.append("      -> %s" % note)
    # rev (e): no socket any more -- verify the MERGE is clean.  The d6 shaft core must
    # be SOLID from the counterbore floor up into the d13 hub (a leftover socket void, or
    # the d1.6 tether hole dropping too low, shows here as < 100% solid).
    _probe = cyl(SHAFT_R, ZF_COUNTERBORE, PIS_TETHER_Z - 0.8)
    _got = by["PistonShaft"].common(_probe)
    _solid = _got.Volume / _probe.Volume if _probe.Volume > 1e-6 else 0.0
    log.append("  hub core solid: counterbore floor Z %.1f -> tether hole   %.0f%% solid   %s"
               % (ZF_COUNTERBORE, 100 * _solid, "PASS" if _solid > 0.98 else "FAIL"))

    log.append("")
    log.append("[5] the catch -- slider rim on the CatchCollar top face  (6.14)")
    sld = by["Slider"]; psh = by["PistonShaft"]; bh = by["Cage"]; col = by["CatchCollar"]
    # bearing = collar top land INSIDE the slider (slab taken above the interface, not below)
    land = col.common(box(-20, 20, -20, 20, COLLAR_Z1 - 0.2, COLLAR_Z1))
    land = land.cut(cyl(NOTCH_R, COLLAR_Z0 - 1, COLLAR_Z1 + 1))
    land.translate(Vector(0, 0, 0.2))
    bear_a = land.common(slider_at(sld, 0.0)).Volume / 0.2
    bear = F_MAX_ASSUMED / bear_a if bear_a > 1e-6 else 1e9
    log.append("  ARMED: collar-top bearing on the notch rim %6.2f mm2   %s"
               % (bear_a, "PASS" if bear_a > 3.0 else "FAIL -- no catch"))
    log.append("  ARMED: bearing stress %.2f MPa  vs ~40                %s"
               % (bear, "PASS" if bear < 40 else "FAIL"))
    # FIRED: the whole COLLAR footprint must clear the slider -- this replaces the old
    # "travel >= NOTCH_R + SHAFT_R" rule, which was a proxy for the wrong body
    foot = cyl(COLLAR_R, COLLAR_Z1 - 0.2, COLLAR_Z1)
    over = foot.common(slider_at(sld, 180.0)).Volume
    log.append("  FIRED: collar footprint still on the slider %6.3f mm3   %s"
               % (over, "PASS" if over < 0.01 else "FAIL -- will not release"))
    rmin = min(math.hypot(v.Point.x, v.Point.y) for v in slider_at(sld, 180.0).Vertexes)
    log.append("  FIRED: nearest slider material r %.3f  vs collar r %.1f  margin %+.2f mm   %s"
               % (rmin, COLLAR_R, rmin - COLLAR_R, "PASS" if rmin > COLLAR_R else "FAIL"))
    # the REACTION PLATE above the slider is what actually takes the +Z load now
    react = bh.common(box(-14, 14, -14, 14, PLATE_Z0, PLATE_Z1)).Volume
    log.append("  reaction PLATE above the slider %7.1f mm3   %s  (v1 reacted into a 2 mm lip)"
               % (react, "PASS" if react > 150.0 else "FAIL"))
    # the ledge centre is mostly void now (collar pocket + pin sweep) -- does the slider
    # still have seating under BOTH edges, or is it perched on one side?
    foot = box(SLIDER_X_MIN - 4.0, NOTCH_MOUTH_X, SLIDER_YW_LO, SLIDER_YW_HI,
               SLIDER_Z0 - 0.2, SLIDER_Z0)
    seat = bh.common(foot)
    sa = seat.Volume / 0.2
    ymid = (SLIDER_YW_LO + SLIDER_YW_HI) / 2.0
    tv = sum(s.Volume for s in seat.Solids) or 1.0
    ycg = sum(s.CenterOfMass.y * s.Volume for s in seat.Solids) / tv
    log.append("  slider seating on the cage %.1f of %.1f mm2 ; support centroid Y %+.2f vs %+.2f"
               % (sa, foot.Volume / 0.2, ycg, ymid))
    # It seats one-sided by construction (the ledge centre must pass the collar and the pin
    # sweep), so demanding centred support would be demanding the impossible.  What matters
    # is the CONSEQUENCE: unloaded, the slider pivots about that support until its far top
    # corner hits the reaction plate CL_SLIDE above.  How far does the NOTCH end drop, and
    # does it still clear the collar while the collar is held down on the cocking stop?
    far_up, far_dn = SLIDER_YW_HI - ycg, ycg - SLIDER_YW_LO
    drop_edge = CL_SLIDE * (far_up + far_dn) / far_up if far_up > 0 else 0.0
    droop = drop_edge * ycg / (far_up + far_dn)
    log.append("  unloaded droop at the notch %.2f mm  vs the %.2f mm cocking gap   %s"
               % (droop, COLLAR_COCK_GAP,
                  "PASS" if droop < COLLAR_COCK_GAP - 0.2 else
                  "FAIL -- a drooping slider fouls the collar while arming; raise COLLAR_COCK_GAP"))
    # the cocking stop: collar underside onto the ledge shelf
    und = col.common(box(-20, 20, -20, 20, COLLAR_Z0, COLLAR_Z0 + 0.2))
    und.translate(Vector(0, 0, LEDGE_STOP_Z - COLLAR_Z0))          # drop it onto the shelf
    shf = bh.common(box(-20, 20, -20, 20, LEDGE_STOP_Z - 0.2, LEDGE_STOP_Z))
    shf.translate(Vector(0, 0, 0.2))                               # lift the shelf to meet it
    sta = und.common(shf).Volume / 0.2
    log.append("  cocking stop: collar on the ledge shelf %.2f mm2 -> %.2f MPa   %s"
               % (sta, F_MAX_ASSUMED / sta if sta > 0.01 else 0,
                  "PASS" if sta > 5.0 and F_MAX_ASSUMED / sta < 40 else "FAIL"))
    # rev (e): the shaft -> collar joint is the transverse d1.5 PIN, not a bond.  It carries
    # F_max in DOUBLE shear (a plane at each shaft/collar-half interface); the pin bears on
    # the shaft cross-hole and on the two collar-half holes.  The pin goes in LAST, through
    # the access slot, after the spring + disc are threaded on -- the d9 collar blocks both
    # bores (the same topology that ruled out an integral flange).
    pin_shear_a = 2.0 * math.pi * COLLAR_PIN_R ** 2                 # 2 planes
    pin_bear_shaft = 2 * COLLAR_PIN_R * 2 * SHAFT_R                 # pin vs the d6 shaft hole
    pin_bear_collar = 2 * (2 * COLLAR_PIN_R * (COLLAR_R - COLLAR_BORE_R))  # pin vs both half holes
    log.append("  collar PIN d%.1f: double-shear %.1f mm2 -> %.2f MPa  vs ~30 for ABS   %s"
               % (2 * COLLAR_PIN_R, pin_shear_a, F_MAX_ASSUMED / pin_shear_a,
                  "PASS" if F_MAX_ASSUMED / pin_shear_a < 30 else "FAIL"))
    log.append("  collar PIN bearing: %.1f MPa on the shaft hole, %.1f MPa on the halves  vs ~40   %s"
               % (F_MAX_ASSUMED / pin_bear_shaft, F_MAX_ASSUMED / pin_bear_collar,
                  "PASS" if max(F_MAX_ASSUMED / pin_bear_shaft,
                               F_MAX_ASSUMED / pin_bear_collar) < 40 else "FAIL"))
    # slider stays captured in its rails through the stroke (no lift path)
    lift = slider_at(sld, 180.0).common(bh).Volume
    log.append("  FIRED slider vs bulkhead (rails/ledge only, small)  %6.1f mm3  %s"
               % (lift, "PASS" if lift < 40.0 else "CHECK"))

    log.append("")
    log.append("[5b] LOAD DIRECTION -- does the catch resist the way the spring pushes?  (6.14)")
    log.append("     The spring drives the piston and shaft +Z.  A face that only reacts -Z")
    log.append("     holds nothing: the shaft lifts straight off it.  v1 reacted -Z.")
    # rev (e): the collar is PINNED, not bonded -- it is NOT one rigid body with the shaft in
    # Z.  From ARMED the shaft rises free by the pin's diametral hole slack (pin travels to
    # the bottom of the shaft hole, then to the top of the collar holes) BEFORE it drags the
    # collar up -- and only the d9 collar is under the slider, the d6 shaft clears the notch.
    # So the collar LAGS the shaft by pin_slack in this sweep; first slider contact is then
    # the TRUE free rise of the shaft, not of a fused body.  (pin_slack is 2c not 4c: the
    # cocked spring keeps a steady +Z bias, so the slack rests taken-up on that side.)
    pin_slack = 2.0 * (COLLAR_PIN_HOLE_R - COLLAR_PIN_R)
    free_rise = None
    for i in range(1, 241):
        d = i * 0.025
        s2 = psh.copy(); s2.translate(Vector(0, 0, d))
        c2 = col.copy(); c2.translate(Vector(0, 0, max(0.0, d - pin_slack)))
        if (s2.fuse(c2)).common(slider_at(sld, 0.0)).Volume > 0.01:
            free_rise = d
            break
    if free_rise is None:
        log.append("  shaft rises > 6 mm with the slider ARMED and never meets it   FAIL -- NO CATCH")
        dir_ok = False
    else:
        dir_ok = free_rise <= 0.10
        log.append("  free +Z travel from ARMED, incl. %.2f mm pin slack  %.3f mm  <= 0.10   %s"
                   % (pin_slack, free_rise, "PASS" if dir_ok else "FAIL"))
        log.append("     (0.10 is a TRIPWIRE for a wrong-side catch -- the defect it guards was")
        log.append("      2.05 mm.  The impact DAF rides on COLLAR_COCK_GAP (1.0 mm), not this;")
        log.append("      a hole reamed 0.05 mm loose reads ~0.12 here and changes nothing real.)")
    # how far can the operator overpress before the collar bottoms on the ledge shelf?
    drop = COLLAR_COCK_GAP
    log.append("  cocking overpress is BOUNDED by the stop: %.2f mm max (design, not operator)"
               % drop)
    up_r = bh.common(box(-14, 14, -14, 14, SLIDER_Z1 + 0.001, PLATE_Z1)).Volume
    dn_r = bh.common(box(-14, 14, -14, 14, LEDGE_Z0, LEDGE_Z1)).Volume
    log.append("  fixed cage ABOVE the slider (takes the +Z load) %7.1f mm3  = the reaction PLATE"
               % up_r)
    log.append("  fixed cage BELOW the slider (slider shelf + stop) %7.1f mm3" % dn_r)
    # the tension load path: d6 shaft from the piston down to the PIN, which is the min
    # section (the d1.5 cross-hole at COLLAR_PIN_Z).  Report gross AND net; the net one is
    # against SIGMA_ABS_INPLANE now (the part prints axial) with KT_PIN_HOLE, under the
    # rigid-drop DAF.
    a_shaft = math.pi * SHAFT_R ** 2
    # circle (R = SHAFT_R) minus the central strip |x| <= COLLAR_PIN_HOLE_R the hole removes
    _w = min(COLLAR_PIN_HOLE_R, SHAFT_R)
    a_removed = 2.0 * (_w * math.sqrt(SHAFT_R ** 2 - _w ** 2) + SHAFT_R ** 2 * math.asin(_w / SHAFT_R))
    a_net = a_shaft - a_removed
    sig = F_MAX_ASSUMED / a_shaft
    sig_net = F_MAX_ASSUMED / a_net
    d_st = F_MAX_ASSUMED * (BH_Z0 - COLLAR_Z1) / (a_shaft * 2000.0)   # shaft stretch, mm
    daf = 1.0 + math.sqrt(1.0 + 2.0 * drop / abs(d_st)) if d_st else 1.0
    log.append("  worst case: %.2f mm drop onto the slider, shaft stretch %.3f mm -> DAF %.1f"
               % (drop, abs(d_st), daf))
    log.append("      d6 shaft GROSS tension %.2f MPa x %.1f = %.1f MPa  (above the pin)"
               % (sig, daf, sig * daf))
    _pk = sig_net * daf * KT_PIN_HOLE
    log.append("      d6 shaft NET at the d1.5 pin hole %.2f MPa x DAF %.1f x Kt %.1f = %.1f MPa"
               " vs ~%.0f in-plane   %s"
               % (sig_net, daf, KT_PIN_HOLE, _pk, SIGMA_ABS_INPLANE,
                  "PASS" if _pk < SIGMA_ABS_INPLANE else "MARGINAL"))
    log.append("      (the DAF is a RIGID drop -- it ignores slider + plate bending, which are")
    log.append("       far more compliant than the shaft and take most of the impact; realistic")
    log.append("       margin at the pin hole is ~3x.  Cure: a d6 CF rod (10.2) -- ~50x.)")
    # SHAFT ROBUSTNESS -- handling, not the catch load.  rev (e): ONE part, no joint.  Two
    # stations matter: the counterbore root (Z ZF_COUNTERBORE, R0.3-filleted, Kt ~1.1) for a
    # knock near the STUB, and the d1.5 PIN HOLE (Z COLLAR_PIN_Z, Kt KT_PIN_HOLE, net section)
    # for a knock near the HEAD.  Both are reported both print ways -- the part only earns the
    # in-plane number if it prints AXIALLY, which is WHY the d38 disc prints edge-on ([10]).
    _Zroot = math.pi * (2 * SHAFT_R) ** 3 / 32.0
    _Lroot = ZF_COUNTERBORE - STUB_Z0                      # force at the stub, moment at the root
    _f_ax = _Zroot * SIGMA_ABS_INPLANE / _Lroot
    _f_il = _Zroot * SIGMA_ABS_INTERLAYER / _Lroot
    log.append("  side-load to break at the counterbore root (L %.0f mm):  %.1f N AXIAL / %.1f N shaft-up"
               % (_Lroot, _f_ax, _f_il))
    _Zpin = _Zroot - (2 * COLLAR_PIN_HOLE_R) * (2 * SHAFT_R) ** 2 / 6.0   # net Z, conservative slot
    _Lpin = (PIS_Z0 + PIS_T) - COLLAR_PIN_Z                # force at the head, moment at the pin
    _p_ax = _Zpin * SIGMA_ABS_INPLANE / KT_PIN_HOLE / _Lpin
    _p_il = _Zpin * SIGMA_ABS_INTERLAYER / KT_PIN_HOLE / _Lpin
    log.append("  side-load to break at the d1.5 pin hole  (L %.0f mm, net Z conservative):  "
               "%.1f N AXIAL / %.1f N shaft-up" % (_Lpin, _p_ax, _p_il))
    log.append("      -> %.1f N is the handling limit (careless knock, not an operating load)   %s"
               % (min(_f_ax, _p_ax),
                  "OK" if min(_f_ax, _p_ax) >= 10.0 else
                  "WEAK -- finding 4: handle the piston by the head, gently; a d6 CF rod "
                  "down the finished head (10.2) is the robust fix"))

    log.append("")
    log.append("[6] crank -- pin in the slot, dead centres, effort")
    off = 0
    for phi in range(0, 181, 5):
        px, py = crank_pin_world(phi)
        lx = px - slider_dx(phi)                       # crank pin in the slider's local frame
        ly = py
        inx = abs(lx - CRANK_SLOT_XC) <= CRANK_SLOT_HW - CRANK_PIN_R + 0.02
        iny = CRANK_SLOT_Y0 + CRANK_PIN_R <= ly <= CRANK_SLOT_Y1 - CRANK_PIN_R
        if not (inx and iny):
            off += 1
    log.append("  crank pin stays in the slot over 0..180 deg   %d/37 out   %s"
               % (off, "PASS" if off == 0 else "FAIL"))
    log.append("  ARMED & FIRED are crank dead centres (dX/dphi = 0)  ->  hold is geometric   PASS")
    # torque to overcome friction on the slider at the worst angle (phi 90)
    fx = MU * F_MAX_ASSUMED
    torque = fx * CRANK_R                              # ~ at phi 90 the whole crank arm is the lever
    finger = torque / KNOB_R
    log.append("  slide friction %.1f N  ->  knob torque ~%.0f N.mm  ->  finger %.1f N   %s"
               % (fx, torque, finger, "PASS" if finger < 15 else "STIFF"))
    log.append("  SG90 %.0f N.mm  ->  %.1fx headroom, 180 deg sweep (add a 2:1 arm if the servo won't)"
               % (SERVO_TORQUE_NMM, SERVO_TORQUE_NMM / max(torque, 1e-3)))

    log.append("")
    log.append("[7] collisions (parts in place)")
    c = []
    swept = cyl(PIS_R + 0.3, SPRING_SOLID, SPRING_FREE + PIS_T + 4)
    c.append(("piston disc sweep vs cage",
              swept.common(bh).Volume < 1.0, swept.common(bh).Volume))
    c.append(("piston disc sweep vs the fixed bulkhead disc",
              swept.common(by["BulkheadDisc"]).Volume < 1.0,
              swept.common(by["BulkheadDisc"]).Volume))
    c.append(("ARMED slider vs shaft", slider_at(sld, 0).common(psh).Volume < 1.0,
              slider_at(sld, 0).common(psh).Volume))
    c.append(("FIRED knob vs cage", knob_at(by["Knob"], 180).common(bh).Volume < 1.0,
              knob_at(by["Knob"], 180).common(bh).Volume))
    c.append(("knob shaft vs piston shaft (both frames)",
              cyl(KNOB_SHAFT_R, KNOB_Z0, CARRIER_Z1, KNOB_AX_X, KNOB_AX_Y)
              .common(cyl(SHAFT_R, KNOB_Z0, CARRIER_Z1)).Volume < 1.0,
              cyl(KNOB_SHAFT_R, KNOB_Z0, CARRIER_Z1, KNOB_AX_X, KNOB_AX_Y)
              .common(cyl(SHAFT_R, KNOB_Z0, CARRIER_Z1)).Volume))
    c.append(("shaft vs cage (ARMED)", psh.common(bh).Volume < 1.0, psh.common(bh).Volume))
    # rev (e): sweep the WHOLE one-piece PistonShaft +Z over the stroke vs fixed structure
    fixed = bh.fuse(by["BulkheadDisc"])
    whd = 0.0
    for i in range(0, 41, 4):
        h2 = by["PistonShaft"].copy(); h2.translate(Vector(0, 0, float(i)))
        whd = max(whd, h2.common(fixed).Volume)
    c.append(("PistonShaft swept 0..40 vs cage + disc", whd < 1.0, whd))
    ws = wd = wp = wcd = 0.0
    for i in range(0, 41, 2):
        s2 = psh.copy(); s2.translate(Vector(0, 0, float(i)))
        c2 = col.copy(); c2.translate(Vector(0, 0, float(i)))
        ws = max(ws, s2.common(bh).Volume)
        wd = max(wd, s2.common(by["BulkheadDisc"]).Volume)
        wp = max(wp, c2.common(bh).Volume)
        wcd = max(wcd, c2.common(by["BulkheadDisc"]).Volume)
    c.append(("PistonShaft swept 0..40 vs cage", ws < 1.0, ws))
    c.append(("PistonShaft swept 0..40 vs disc", wd < 1.0, wd))
    c.append(("COLLAR swept 0..40 vs cage", wp < 1.0, wp))
    c.append(("COLLAR swept 0..40 vs disc", wcd < 1.0, wcd))
    # the crank pin, swept as a SOLID for the first time (10.15)
    wpin_c = max(crank_pin_at(p).common(bh).Volume for p in range(0, 181, 6))
    wpin_o = max(crank_pin_at(p).common(col).Volume for p in range(0, 181, 6))
    wpin_s = max(crank_pin_at(p).common(psh).Volume for p in range(0, 181, 6))
    c.append(("CRANK PIN swept vs cage", wpin_c < 0.01, wpin_c))
    c.append(("CRANK PIN swept vs collar", wpin_o < 0.01, wpin_o))
    c.append(("CRANK PIN swept vs piston shaft", wpin_s < 0.01, wpin_s))
    c.append(("CRANK PIN engages the slider slot",
              crank_pin_at(0).common(box(-30, 30, -30, 30, SLIDER_Z0, SLIDER_Z1)).Volume > 5.0,
              crank_pin_at(0).common(box(-30, 30, -30, 30, SLIDER_Z0, SLIDER_Z1)).Volume))
    for name, ok, v in c:
        log.append("  %-38s %8.1f mm3   %s" % (name, v, "PASS" if ok else "FAIL"))

    log.append("")
    log.append("[8] RBF -- R-clip through knob + carrier locks the knob")
    clip = cyl(RBF_HOLE_R - 0.1, KNOB_Z0 - 1, CARRIER_Z1 + 1, KNOB_AX_X + RBF_KR, KNOB_AX_Y)
    free = clip.common(by["Knob"]).Volume
    foul = clip.common(knob_at(by["Knob"], 30)).Volume
    log.append("  ARMED clip passes the knob hole  %5.2f mm3   %s"
               % (free, "PASS" if free < 2.0 else "FAIL"))
    log.append("  knob turned 30 deg: clip fouls the knob  %6.2f mm3   %s"
               % (foul, "PASS" if foul > 2.0 else "FAIL"))
    # ...but does the pin have any FIXED material to react against?  NB: measuring the pin
    # against the cage is VACUOUS -- the cage has a clearance hole there, so it reads ~0
    # whether the hole is drilled through solid carrier or through thin air.  Measure the
    # WALL AROUND the hole instead.  At RBF_KR +6.0 the hole sat at r 2.0 from the tube
    # axis, inside the carrier's BH_BORE_R+1 = 4.4 central bore: the RBF pin locked the
    # knob to nothing, which is the brownout case requirement 3 exists for (10.16).
    ring = (cyl(RBF_HOLE_R + 1.5, CARRIER_Z0, CARRIER_Z1, KNOB_AX_X + RBF_KR, KNOB_AX_Y)
            .cut(cyl(RBF_HOLE_R, CARRIER_Z0 - 1, CARRIER_Z1 + 1, KNOB_AX_X + RBF_KR, KNOB_AX_Y)))
    anchor = ring.common(bh).Volume
    full = ring.Volume
    log.append("  RBF hole is drilled through SOLID carrier %5.1f of %5.1f mm3   %s"
               % (anchor, full, "PASS" if anchor > full * 0.5 else
                  "FAIL -- hole is in mid-air; the RBF pin locks the knob to nothing"))

    log.append("")
    log.append("[P] printed pins vs the pins this script MODELS  (two files, one geometry)")
    # PIN_BOT_Z/PIN_TOP_Z live here; CRANK_LEN/RBF_LEN live in ejection_poc_test_pins.py.
    # Nothing tied them together, so a change here silently left the printed pin wrong --
    # which is how the crank pin ended up 3 mm too short to reach the slider (10.17).
    try:
        pins = load_pins()          # the SAME import the plate uses -- one reader, not two
        need_crank = PIN_TOP_Z - PIN_BOT_Z
        got_crank = pins.CRANK_LEN
        ok = got_crank is not None and abs(got_crank - need_crank) < 0.05
        log.append("  CRANK_LEN  %.1f mm  needs %.1f (PIN_TOP_Z - PIN_BOT_Z)   %s"
                   % (got_crank if got_crank else -1, need_crank, "PASS" if ok else "FAIL -- reprint the pins"))
        need_rbf = (CARRIER_Z1 - KNOB_Z0) + 3.0        # knob bottom -> carrier top, + 3 to grab
        got_rbf = pins.RBF_LEN
        ok2 = got_rbf is not None and got_rbf >= need_rbf - 0.05
        log.append("  RBF_LEN    %.1f mm  needs >= %.1f (knob bottom -> carrier top + 3)   %s"
                   % (got_rbf if got_rbf else -1, need_rbf, "PASS" if ok2 else "FAIL"))
        got_cd = pins.CRANK_D
        ok3 = got_cd is not None and abs(got_cd - 2 * CRANK_PIN_R) < 0.05
        log.append("  CRANK_D    %.1f mm  needs %.1f (2 x CRANK_PIN_R)   %s"
                   % (got_cd if got_cd else -1, 2 * CRANK_PIN_R, "PASS" if ok3 else "FAIL"))
        got_coll = getattr(pins, "COLLAR_LEN", None)
        ok4 = got_coll is not None and abs(got_coll - COLLAR_PIN_LEN) < 0.05
        log.append("  COLLAR_LEN %.1f mm  needs %.1f (2 x COLLAR_R - 0.4)   %s"
                   % (got_coll if got_coll else -1, COLLAR_PIN_LEN, "PASS" if ok4 else "FAIL -- reprint the pins"))
        got_cold = getattr(pins, "COLLAR_D", None)
        ok5 = got_cold is not None and abs(got_cold - 2 * COLLAR_PIN_R) < 0.05
        log.append("  COLLAR_D   %.1f mm  needs %.1f (2 x COLLAR_PIN_R)   %s"
                   % (got_cold if got_cold else -1, 2 * COLLAR_PIN_R, "PASS" if ok5 else "FAIL"))
    except Exception as exc:
        log.append("  ! could not read ejection_poc_test_pins.py (%s)   CHECK" % exc)

    log.append("")
    log.append("[9] features present (non-vacuous)")
    f = []
    st = by["TubeStub"]
    f.append(("window cut", Part.makeBox(2, 2, 2, Vector(-1, R_AF_I + 0.3, 10)).common(st).Volume < 0.1))
    f.append(("access slot cut",
              Part.makeBox(2, 2, 2, Vector(R_AF_I + 0.3, -1, SLIDER_TOP_Z)).common(st).Volume < 0.1))
    f.append(("slider U-notch open",
              cyl(0.8, SLIDER_Z0, SLIDER_Z1, 0, 0).common(by["Slider"]).Volume < 0.1))
    f.append(("crank slot open",
              box(CRANK_SLOT_XC - 0.4, CRANK_SLOT_XC + 0.4, 0, 0.5, SLIDER_Z0, SLIDER_Z1)
              .common(by["Slider"]).Volume < 0.1))
    # rev (e): the shaft is SOLID d6 EXCEPT the one d1.5 collar-pin cross-hole at
    # COLLAR_PIN_Z.  Probe the full length (above the stub lead-in to below the
    # counterbore-root fillet): the OD must be unbroken everywhere, and the solid
    # fraction must be exactly "d6 minus one d1.55 hole" -- no OTHER reduction.  The
    # pin-station net bending section is reported as its OWN row, so the reduction is
    # visible, not excluded (contrast 10.15 / the old groove-excluding probe).
    z_lo, z_hi = STUB_Z0 + 1.5, SHAFT_MERGE_Z - CB_ROOT_FIL - 0.1
    probe = cyl(SHAFT_R - 0.05, z_lo, z_hi)
    solid_frac = probe.common(by["PistonShaft"]).Volume / probe.Volume
    # want_frac = "d6 minus exactly one d1.55 hole".  The hole crosses the probe over ~the
    # PROBE diameter, not the d6 shaft's -- use that chord so want_frac is unbiased (a d6
    # chord over-removes ~e-4 and the band would have to swallow it).  These are EXACT BREP
    # volumes (no mesh), so the true case lands within a few e-5 and the band is +-0.001 --
    # deliberately far inside the hole's own 0.4%-of-probe so DROPPING the pin hole FAILs
    # this row (solid_frac -> 1.000, delta -> +0.004).  Comment out the pin cut in
    # build_pistonshaft and this must go red; if it stays green the check is vacuous (10.15).
    hole_vol = math.pi * COLLAR_PIN_HOLE_R ** 2 * (2 * (SHAFT_R - 0.05))
    want_frac = 1.0 - hole_vol / probe.Volume
    dmin = None                                      # stays None if the probe finds NOTHING --
    for k in range(41):                             #   report n/a, don't fake a nominal d6
        zz = z_lo + k * (z_hi - z_lo) / 40.0
        sl = by["PistonShaft"].common(box(-10, 10, -10, 10, zz - 0.05, zz + 0.05))
        if sl.Volume > 1e-6:
            d = 2 * max(math.hypot(v.Point.x, v.Point.y) for v in sl.Vertexes)
            dmin = d if dmin is None else min(dmin, d)
    f.append(("shaft d6, OD unbroken + ONLY the d1.5 pin hole "
              "(min OD d%s, solid-vs-want %+.3f%% ; band +-0.1%% inside the %.2f%% pin hole)"
              % ("%.2f" % dmin if dmin is not None else "n/a",
                 100 * (solid_frac - want_frac), 100 * hole_vol / probe.Volume),
              dmin is not None and dmin > 2 * SHAFT_R - 0.15
              and abs(solid_frac - want_frac) < 0.001))
    # the pin-station net BENDING section, reported so the reduction is not hidden
    _Zg = math.pi * (2 * SHAFT_R) ** 3 / 32.0
    _Zn = _Zg - (2 * COLLAR_PIN_HOLE_R) * (2 * SHAFT_R) ** 2 / 6.0
    f.append(("  -> net section modulus at the pin hole %.0f%% of gross (d1.5, conservative slot)"
              % (100 * _Zn / _Zg), _Zn > 0.35 * _Zg))
    # a volume-split test would also pass for a MIRRORED pair; mirror one half about y=0
    # and check it actually coincides with the other, which is the claim being made
    h1 = collar_half()
    h2 = build_catchcollar().common(box(-20, 20, -20, 0, COLLAR_Z0 - 1, COLLAR_Z1 + 1))
    hm = h1.mirror(Vector(0, 0, 0), Vector(0, 1, 0))
    f.append(("collar halves are IDENTICAL, not mirrored",
              h2.Volume > 1.0 and abs(hm.common(h2).Volume - h2.Volume) < 0.05 * h2.Volume))
    for name, ok in f:
        log.append("  %-44s %s" % (name, "PASS" if ok else "FAIL"))

    log.append("")
    log.append("[10] export")
    RTP = os.path.join(PRINTS, "Ready to Print")
    if not os.path.isdir(RTP):
        os.makedirs(RTP)
    PRINT_ROT = {"PistonShaft": ((1.0, 0, 0), 90.0)}   # lay the whole part AXIAL (layers along the shaft)
    NOTE = {"TubeStub": "vertical as-is, brim, no supports",
            "Cage": "carrier end on the bed, legs up; light tree-support the ledge overhang",
            "BulkheadDisc": "flat, seat face down, no supports",
            "PistonShaft": "AXIAL -- laid horizontal so the perimeters run ALONG the shaft "
                           "(bending in-plane ~40 MPa vs ~20 interlayer, ~2x -- [5b]).  The "
                           "d38 head disc then prints EDGE-ON: support its lower ~third and "
                           "the sideways-facing d11.5 spring pocket; the counterbore-root "
                           "fillet bridges.  Brim.  Expect 0.2-0.4 mm sag/elephant-foot on "
                           "the shaft (0.4 mm bore clearance) -- sand it round, and ream the "
                           "d1.5 collar-pin cross-hole (it prints egg-shaped as an unsupported "
                           "side hole, and it is the pin's bearing surface).  Printed ALONE "
                           "(~117 mm), NOT on the plate.  (A d6 CF rod epoxied down the "
                           "finished head is the robust upgrade -- 10.2.)",
            "Slider": "flat on the bed as-is, no supports",
            "CatchCollar": "ASSEMBLY REFERENCE ONLY -- no Ready-to-Print STL (a d9 ring "
                           "cannot go onto a shaft that must thread the d6.8 bulkhead bore). "
                           "Print CatchCollarHalf x2: FLAT as exported, 4.0 mm tall, curved "
                           "face up, split face VERTICAL, no supports. Do not stand it on the "
                           "split face -- that face mates the other half and the d1.5 pin "
                           "crosses it; the load-bearing TOP face wants to print clean too. "
                           "As exported they print as smooth perimeter walls; on the bed "
                           "they would get elephant's foot. Ream the pin hole after printing.",
            "Knob": "grip face on the bed, D-flat up",
            "DummyNose": "base on the bed, tip up"}
    plate_items = []
    for n, s in parts:
        doc.addObject("Part::Feature", n).Shape = s
        s.exportStep(os.path.join(MODELS, "PhoenixABS40-43_%s_%s.step" % (n, REV)))
        meshes[n].write(os.path.join(PRINTS, "PhoenixABS40-43_%s_%s.stl" % (n, REV)))
        # NOT into Ready to Print: the one-piece collar is an ASSEMBLY REFERENCE.  A d9
        # ring cannot go onto a shaft that has to thread the d6.8 bulkhead bore -- that is
        # the whole reason it splits.  Only CatchCollarHalf is a printable article, and
        # section 9.4 sends people to this directory to print from.
        if n != "CatchCollar":
            sh = s.copy()
            ax, ang = PRINT_ROT.get(n, ((0.0, 0, 1.0), 0.0))
            if ang:
                sh.rotate(Vector(0, 0, 0), Vector(*ax), ang)
            bb = sh.BoundBox
            sh.translate(Vector(-(bb.XMin + bb.XMax) / 2.0, -(bb.YMin + bb.YMax) / 2.0, -bb.ZMin))
            mesh_of(sh).write(os.path.join(RTP, "PhoenixABS40-43_%s_%s.stl" % (n, REV)))
            # The plate is the BATCH of small parts.  TubeStub (169 mm) and PistonShaft
            # (~117 mm axial, rev (e)) are long -- mixing them with 2 mm collar halves on
            # one plate is what section 11 has always warned against, so they print
            # individually from Ready to Print/.
            if n not in ("TubeStub", "PistonShaft"):
                plate_items.append((n, sh))
        if n == "CatchCollar":
            h = collar_half()
            hb = h.BoundBox
            h.translate(Vector(-(hb.XMin + hb.XMax) / 2.0, -(hb.YMin + hb.YMax) / 2.0, -hb.ZMin))
            h.exportStep(os.path.join(MODELS, "PhoenixABS40-43_CatchCollarHalf_%s.step" % REV))
            mesh_of(h).write(os.path.join(RTP, "PhoenixABS40-43_CatchCollarHalf_%s.stl" % REV))
            plate_items.append(("CatchCollarHalf_A", h))
            hb = h.copy()
            plate_items.append(("CatchCollarHalf_B", hb))     # you need TWO
        log.append("  %-12s step + stl + ready-to-print  (%s)" % (n, NOTE.get(n, "")))

    # ---------------- the print plate ----------------------------------------------
    log.append("")
    log.append("[11] print plate  (Ejection System/Print Plate/ -- GENERATED, was hand-made)")
    try:
        pins = load_pins()
        pin_shape = pins.build_pins()
        pb = pin_shape.BoundBox
        pin_shape.translate(Vector(0, 0, -pb.ZMin))
        plate_items.append(("TestPins", pin_shape))
        log.append("  pins imported from ejection_poc_test_pins.py: %d crank (d%.1f x %.1f) "
                   "+ %d RBF (d%.1f x %.1f) + %d collar (d%.1f x %.1f)"
                   % (pins.N_CRANK, pins.CRANK_D, pins.CRANK_LEN,
                      pins.N_RBF, pins.RBF_D, pins.RBF_LEN,
                      getattr(pins, "N_COLLAR", 0), getattr(pins, "COLLAR_D", 0.0),
                      getattr(pins, "COLLAR_LEN", 0.0)))
    except Exception as exc:
        log.append("  ! pins not added to the plate (%s)   CHECK" % exc)

    placed, used_x, used_y = pack_plate(plate_items, log)
    PLATE_DIR = os.path.join(PRINTS, "Print Plate")
    if not os.path.isdir(PLATE_DIR):
        os.makedirs(PLATE_DIR)
    stem = os.path.join(PLATE_DIR, "PhoenixABS40-43_ejection_poc_plate_%s" % REV)
    write_3mf(stem + ".3mf", placed)
    pm = mesh_of(placed[0][1])
    for _n, ps in placed[1:]:
        pm.addMesh(mesh_of(ps))
    pm.write(stem + ".stl")

    fits = used_x <= BED_X - PLATE_EDGE + 1e-6 and used_y <= BED_Y - PLATE_EDGE + 1e-6
    log.append("  %d objects: %s" % (len(placed), ", ".join(n for n, _ in placed)))
    log.append("  footprint %.1f x %.1f mm on a %.0f x %.0f bed   %s"
               % (used_x, used_y, BED_X, BED_Y, "PASS" if fits else "FAIL -- raise BED_X/BED_Y"))
    tall = max(p.BoundBox.ZLength for _n, p in placed)
    log.append("  tallest object on the plate %.1f mm   (TubeStub ~%.0f mm and PistonShaft "
               "~117 mm axial are deliberately NOT on it -- print those two alone)"
               % (tall, STUB_Z_TOP - STUB_Z_BOT))
    # nothing may overlap: pairwise bounding-box test, then a boolean on any that touch
    worst_ov, worst_pair = 0.0, None
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            a, b = placed[i][1], placed[j][1]
            ba, bb2 = a.BoundBox, b.BoundBox
            if (ba.XMin < bb2.XMax and bb2.XMin < ba.XMax
                    and ba.YMin < bb2.YMax and bb2.YMin < ba.YMax):
                v = a.common(b).Volume
                if v > worst_ov:
                    worst_ov, worst_pair = v, (placed[i][0], placed[j][0])
    log.append("  no two objects overlap   worst %.3f mm3 %s   %s"
               % (worst_ov, ("(%s / %s)" % worst_pair) if worst_pair else "",
                  "PASS" if worst_ov < 0.01 else "FAIL"))
    # overlap is prevented by the packer, so the number that actually matters on a bed is
    # the XY separation -- brim room.  Report it directly instead of implying it.
    tight, tight_pair = 1e9, None
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            A, B = placed[i][1].BoundBox, placed[j][1].BoundBox
            gap = max(max(B.XMin - A.XMax, A.XMin - B.XMax),
                      max(B.YMin - A.YMax, A.YMin - B.YMax))
            if gap < tight:
                tight, tight_pair = gap, (placed[i][0], placed[j][0])
    log.append("  tightest XY gap %.2f mm  >= %.1f (brim room) %s   %s"
               % (tight, PLATE_GAP, ("(%s / %s)" % tight_pair) if tight_pair else "",
                  "PASS" if tight >= PLATE_GAP - 0.05 else "FAIL"))   # 0.05 = bbox tessellation slop
    # validate what the hand-rolled 3MF writer actually produced -- a bad triangle index
    # or a missing build item makes a file that opens as an empty plate, silently
    try:
        import zipfile as _zip, re as _re
        _d = _zip.ZipFile(stem + ".3mf").read("3D/3dmodel.model").decode()
        _objs = _re.findall(r'<object id="(\d+)" type="model" name="([^"]+)">(.*?)</object>',
                            _d, _re.S)
        _items = _d.count("<item objectid")
        _bad = 0
        for _oid, _nm, _seg in _objs:
            _nv = len(_re.findall(r"<vertex ", _seg))
            _tr = _re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)" />', _seg)
            if not _tr or max(max(int(a), int(b), int(c)) for a, b, c in _tr) >= _nv:
                _bad += 1
        ok3 = len(_objs) == len(placed) and _items == len(placed) and _bad == 0
        log.append("  3MF readback: %d objects, %d build items, %d bad triangle indices   %s"
                   % (len(_objs), _items, _bad, "PASS" if ok3 else "FAIL"))
    except Exception as exc:
        log.append("  ! 3MF readback failed (%s)   FAIL" % exc)
    log.append("  wrote plate_%s.3mf + .stl" % REV)

    doc.recompute()
    doc.saveAs(os.path.join(MODELS, "PhoenixABS40-43_ejection_poc_%s.FCStd" % REV))

    rpt = "\n".join(log)
    print(rpt)
    with open(os.path.join(MODELS, "ejection_poc_build_report_%s.txt" % REV), "w") as fh:
        fh.write(rpt + "\n")


main()

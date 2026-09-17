# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- LAUNCH PAD built around the user's 4.0 mm steel rod, v1

SOURCE OF TRUTH for the pad.  Every dimension is a named constant below; edit
here and re-run -- never edit the STL/STEP/FCStd.  (DESIGN.md 12's bullet that
says the .py files are "legacy record, do not extend that pattern" is stale --
the .py is the record of record and the MCP is the working surface.)

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" <this file>
or exec() it through the freecad MCP to get the same document in the GUI.

------------------------------------------------------------------------------
BRIEF
------------------------------------------------------------------------------
"A new, simpler launch pad made around the 4 mm diameter steel rod.  As simple,
yet functional as possible."  No prior pad exists anywhere in the project (no
files, empty live document) -- so "simpler" is read in absolute terms: the
fewest parts that still make a pad you can actually launch off.

  3 unique printed parts, 5 pieces, ZERO bought hardware.

  PadHub          x1  rod socket + 3 leg mortises + deflector seat + tie-down
  PadLeg          x3  slot-in outrigger blade, staking foot
  BlastDeflector  x1  disc + slotted standoff ring; the rocket rests on it

------------------------------------------------------------------------------
WHY IT IS SHAPED LIKE THIS  (the two non-obvious ones)
------------------------------------------------------------------------------
(a) THE ROCKET CANNOT REST ON A COLLAR CLAMPED TO THE ROD.  The obvious "simple"
    answer -- a stop collar on the rod that the launch lug sits on -- is
    geometrically impossible here.  The rod runs through a lug on the OUTSIDE of
    the tube, so the rod axis is only R_AF_O + LUG_OD/2 = 25.0 mm from the body
    axis, and 152 mm of body tube hangs BELOW the lug at a constant 3.5 mm from
    the rod.  Any collar fat enough to clamp fouls the tube, in every clocking
    (the rocket is free to spin on the rod).  So the rocket rests on its FINS,
    on the deflector, which is what every small pad has always done.

(b) THE DEFLECTOR CARRIES A STANDOFF RING.  Fins overhang the body aft end by
    4 mm (DESIGN.md 2.2) and the motor is 3 mm proud of the mount, so resting
    the fins straight on a flat plate leaves the NOZZLE 1 mm off the plate.
    The ring lifts the rest plane RING_H above the deflector floor and vents the
    blast through 6 arched windows.  Ring band radii are set so that every one
    of the 3 fins lands on the band at EVERY clocking -- check [7] proves it by
    sweeping the clocking, because the rod is off-axis and the naive symmetric
    argument does not hold.

------------------------------------------------------------------------------
FRAME
------------------------------------------------------------------------------
Z = 0 at the ground; +Z up.  Origin ON THE ROD AXIS (not the rocket axis).
The rocket, when on the pad, is centred at x = +ROD_OFFSET.
"""

import os
import math

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

# ================================================================== parameters

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
MODELS = os.path.join(PROJECT, "Models")
PRINTS = os.path.join(PROJECT, "Print Files", "Launch Pad")
RTP = os.path.join(PRINTS, "Ready to Print")
REV = "v1"

RHO = 1.05e-3                 # ABS 100% infill, g/mm^3

# --- the rod this pad is built around -----------------------------------
ROD_D = 4.0                   # user's steel rod, measured nominal
ROD_BORE = 4.20               # printed bore: ream with a 4 mm bit after printing
ROD_L_ASSUMED = 1000.0        # what a "1 m rod" gives -- check [6] judges it
ROD_L_WANTED = 1400.0         # what check [6] says to actually buy
ROD_E = 200000.0              # steel, MPa
ROD_RHO_LIN = 0.0000987       # kg/mm for d4 steel  (7850 kg/m3 * pi*2^2 mm2)

# --- FDM fit clearances (ABS, 0.4 mm nozzle) -- same block as the ejection POC
CL_SLIDE = 0.50
CL_REG   = 0.20               # printed register / spigot in a printed counterbore

# --- hub -----------------------------------------------------------------
HUB_BASE_D = 44.0             # ground pad; sits on the ground itself, Z 0
HUB_BASE_H = 38.0
HUB_COL_D = 44.0              # == HUB_BASE_D, i.e. the hub is ONE d44 cylinder up
                              # to HUB_COL_TOP.  This is not laziness: the column's
                              # top face is the deflector's ONLY vertical seat, and
                              # the load on that disc is its own weight at r=0 PLUS
                              # the rocket's at r=ROD_OFFSET, whose resultant sits
                              # at r 16.8.  A d26 column seats only r 10.2..13.0 --
                              # the resultant falls outside it and the disc rocks
                              # until the bore binds on the spigot (5.7 deg, 4.8 mm
                              # of drop at the fin band), which breaks [7]'s
                              # three-fin contact.  Check [8c] measures this.
HUB_COL_TOP = 59.0
HUB_SPIG_D = 20.0             # spigot: locates the deflector, flush with its top
HUB_TOP = 63.0                # == deflector top face; nothing above it (see (a))

MORT_W = 6.40                 # leg mortise, bottom-open (no bridge to print)
MORT_H = 26.0
MORT_DEPTH = 15.0             # radial: from r 22.0 in to r 7.0

TIE_D = 7.0                   # tie-down / ballast hole, transverse, misses the bore
TIE_Z = 32.0
TIE_Y = 8.0

# --- leg ------------------------------------------------------------------
LEG_N = 3
LEG_REACH = 170.0             # foot tip, from the rod axis
LEG_W = 6.70                  # blade AND tenon: one width -> prints flat, no float
LEG_H_HUB = 26.0              # blade depth at the hub face
LEG_H_TIP = 11.0
LEG_SHOULDER = 55.0           # blade stays full depth out to here, then tapers
TEN_SLOT_W = 1.60             # splits the tenon into two cheeks that flex
TEN_SLOT_L = 12.0
TEN_CLEAR_H = 0.30            # tenon is shorter than the mortise
FOOT_S0 = 148.0               # widened pad for the peg hole
FOOT_Y1 = 11.35               # asymmetric: bed side stays flat at -LEG_W/2
FOOT_H = 11.0
PEG_D = 6.50
PEG_S = 159.0

# --- blast deflector -------------------------------------------------------
DEFL_D = 120.0
DEFL_T = 4.0
DEFL_BORE = HUB_SPIG_D + 2 * CL_REG      # 20.4 over the 20.0 spigot
LINER_D = 86.0               # optional metal liner recess -- MUST stay inside RING_RI
LINER_T = 1.0
RING_RI = 44.0                # standoff ring band -- check [7] sweeps clockings
RING_RO = 53.0
RING_H = 40.0
WIN_N = 6                     # arched gas windows: self-supporting, no bridges
WIN_W = 32.0                  # widened from 22 -- thins the pillars between
                              # windows; WIN_RECT_H dropped to match so the
                              # arch top (WIN_RECT_H + WIN_W/2) is unchanged at
                              # 32 mm and [8d]'s 8 mm continuous rim rail holds
WIN_RECT_H = 16.0             # + a semicircular arch of radius WIN_W/2 on top

# --- the vehicle it has to hold  (DESIGN.md 2.1 / 2.2 / 3.2 / 4.4) --------
R_AF_O = 21.5                 # airframe OD 43
LUG_OD = 7.0
LUG_BORE = 5.0                # DESIGN.md 2.2 -- sized for a 4.8 mm rod, see [9]
LUG_LEN = 35.0
ROD_OFFSET = R_AF_O + LUG_OD / 2.0        # 25.0 -- rod axis off the body axis
BODY_L = 340.0
NOSE_L = 40.0
ROCKET_L = BODY_L + NOSE_L
FIN_ROOT_R = R_AF_O           # fin TE, from the BODY axis
FIN_TIP_R = R_AF_O + 55.0     # rev-5 semi-span 55
FIN_N = 3
FIN_AFT_OVERHANG = 4.0        # fin TE below the body aft end
MOTOR_AFT_OVERHANG = 3.0      # nozzle below the body aft end
FIN_AREA_EA = 2084.0          # mm^2 planform, DESIGN.md 2.2
M_ROCKET = 237.0              # g, liftoff on a C6, realistic (DESIGN.md 3.2)
CG_FROM_NOSE = 228.0
RAIL_MIN = 1000.0             # DESIGN.md 4.4: >= 1.0 m light, 1.2-1.5 m payload
RAIL_MIN_PAYLOAD = 1200.0
NOZZLE_THROAT_D = 4.0         # 18 mm BP motor, for the vent-area ratio in [8]

# --- environment the checks are run at ------------------------------------
WIND_LIMIT = 10.0             # m/s -- a realistic club range limit, NOT a
                              # speed picked because it passes.  [5] fails here.
WIND_CALM = 5.0
RHO_AIR = 1.225               # kg/m3
CD_CROSS = 1.2                # crossflow on a cylinder / flat plate
BALLAST_KG = 1.0              # what you hang on the tie-down hole

# ==================================================================== helpers


def cyl(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, Vector(x, y, z0), Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def prism_xz(pts, y0, y1):
    """Polygon in the (x,z) plane, extruded along y."""
    vs = [Vector(p[0], y0, p[1]) for p in pts]
    vs.append(vs[0])
    w = Part.makePolygon(vs)
    f = Part.Face(w)
    return f.extrude(Vector(0.0, y1 - y0, 0.0))


def rot_z(shape, deg):
    s = shape.copy()
    s.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), deg)
    return s


def mesh_of(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.15, Relative=False)


# ================================================================ the 3 bodies


def build_hub():
    """Rod socket + 3 bottom-open leg mortises + deflector seat + tie-down.

    The base bottom is at Z 0, so the hub stands on the ground itself and the
    rod bottoms out on the ground through the through-bore -- the legs are pure
    outriggers and the ABS never carries the rod's axial load."""
    s = cyl(HUB_BASE_D / 2.0, 0.0, HUB_BASE_H)
    s = s.fuse(cyl(HUB_COL_D / 2.0, HUB_BASE_H, HUB_COL_TOP))
    s = s.fuse(cyl(HUB_SPIG_D / 2.0, HUB_COL_TOP, HUB_TOP))

    # rod: a THROUGH bore, so it can be reamed with a 4 mm bit and the rod
    # bottoms on the ground.  A 63 mm blind hole could not be cleaned up.
    s = s.cut(cyl(ROD_BORE / 2.0, -1.0, HUB_TOP + 1.0))

    # 3 leg mortises, open at the bottom -> the only "roof" is a 6.4 mm bridge
    r_in = HUB_BASE_D / 2.0 - MORT_DEPTH
    for i in range(LEG_N):
        m = box(r_in, HUB_BASE_D / 2.0 + 1.0, -MORT_W / 2.0, MORT_W / 2.0,
                -1.0, MORT_H)
        s = s.cut(rot_z(m, 120.0 * i))

    # tie-down / ballast hole: offset in y so it misses the rod bore, above the
    # mortise roofs and below the base top face
    s = s.cut(Part.makeCylinder(TIE_D / 2.0, HUB_BASE_D + 4.0,
                                Vector(-HUB_BASE_D / 2.0 - 2.0, TIE_Y, TIE_Z),
                                Vector(1, 0, 0)))
    return s.removeSplitter()


def build_leg():
    """Outrigger blade.  PRINTS FLAT (LEG_REACH x LEG_H_HUB footprint, LEG_W
    tall): layers then stack across the blade's WIDTH, so the bending stress --
    which runs along the leg and varies through its depth -- is entirely
    IN-PLANE.  Same argument as the ejection POC's axially-printed shaft."""
    r_in = HUB_BASE_D / 2.0 - MORT_DEPTH
    r_hub = HUB_BASE_D / 2.0
    y0, y1 = -LEG_W / 2.0, LEG_W / 2.0

    # tenon (inside the mortise) -- full LEG_W so the part has ONE width and
    # lies flat on the bed with nothing floating
    ten = box(r_in, r_hub, y0, y1, 0.0, MORT_H - TEN_CLEAR_H)

    # blade, tapering in depth from the hub face out to the foot
    blade = prism_xz([(r_hub, 0.0), (LEG_REACH, 0.0), (LEG_REACH, LEG_H_TIP),
                      (LEG_SHOULDER, LEG_H_HUB), (r_hub, LEG_H_HUB)], y0, y1)

    # foot pad: widened on ONE side only, so the bed face stays at y0
    foot = box(FOOT_S0, LEG_REACH, y0, FOOT_Y1, 0.0, FOOT_H)

    s = ten.fuse(blade).fuse(foot).removeSplitter()

    # split the tenon into two flexing cheeks -> a real interference fit
    # (MORT_W is 0.30 narrower than LEG_W) that hand-assembles and holds
    s = s.cut(box(r_in - 1.0, r_in + TEN_SLOT_L, -TEN_SLOT_W / 2.0,
                  TEN_SLOT_W / 2.0, -1.0, MORT_H + 1.0))

    # peg hole -- a tent peg through here is what actually holds the pad down
    s = s.cut(cyl(PEG_D / 2.0, -1.0, LEG_H_HUB + 1.0, x=PEG_S,
                  y=(y0 + FOOT_Y1) / 2.0))
    return s.removeSplitter()


def build_deflector():
    """Disc + slotted standoff ring.  The ring is the rocket's rest: it lifts
    the nozzle RING_H off the plate instead of the 1 mm a bare plate gives.
    Windows are rectangle + semicircular arch, so nothing bridges."""
    z0 = HUB_COL_TOP                       # underside, seated on the hub shoulder
    z1 = z0 + DEFL_T
    s = cyl(DEFL_D / 2.0, z0, z1)
    s = s.fuse(cyl(RING_RO, z1, z1 + RING_H))
    # bore the ring from the floor UP, never below it: a cut starting under z1
    # would gouge the floor out to RING_RI and leave the ring root undercut
    s = s.cut(cyl(RING_RI, z1, z1 + RING_H + 1.0))
    # optional metal-liner recess -- stays INSIDE the ring bore (LINER_D is
    # asserted < 2*RING_RI in [12]) so the ring stands on solid disc
    s = s.cut(cyl(LINER_D / 2.0, z1 - LINER_T, z1))
    s = s.cut(cyl(DEFL_BORE / 2.0, z0 - 1.0, z1 + 1.0))

    for i in range(WIN_N):
        rect = box(RING_RI - 2.0, RING_RO + 2.0, -WIN_W / 2.0, WIN_W / 2.0,
                   z1, z1 + WIN_RECT_H)
        arch = Part.makeCylinder(WIN_W / 2.0, RING_RO - RING_RI + 4.0,
                                 Vector(RING_RI - 2.0, 0.0, z1 + WIN_RECT_H),
                                 Vector(1, 0, 0))
        s = s.cut(rot_z(rect.fuse(arch), 60.0 * i))
    return s.removeSplitter()


# ============================================================ vehicle geometry


def rest_z():
    """Top of the standoff ring == where the fin trailing edges sit."""
    return HUB_COL_TOP + DEFL_T + RING_H


def fin_contact_len(phi_deg):
    """For a fin clocking phi, the radial run of each fin's TE that lies over
    the ring band.  The rod is ROD_OFFSET off the body axis, so this is NOT
    symmetric and has to be swept, not argued."""
    out = []
    for k in range(FIN_N):
        th = math.radians(phi_deg + 120.0 * k)
        lo, hi = None, None
        n = 400
        for j in range(n + 1):
            t = FIN_ROOT_R + (FIN_TIP_R - FIN_ROOT_R) * j / float(n)
            x = ROD_OFFSET + t * math.cos(th)
            y = t * math.sin(th)
            r = math.hypot(x, y)
            if RING_RI <= r <= RING_RO:
                if lo is None:
                    lo = t
                hi = t
        out.append(0.0 if lo is None else hi - lo)
    return out


def wind_force(area_m2, v):
    return CD_CROSS * 0.5 * RHO_AIR * v * v * area_m2


# ========================================================================= run


def main():
    log = []

    def P(t=""):
        log.append(t)

    P("PhoenixABS40-43 -- LAUNCH PAD %s   build report" % REV)
    P("=" * 78)
    P("Built around the user's d%.1f mm steel rod.  3 unique parts, 5 pieces," % ROD_D)
    P("zero bought hardware.  Frame: Z=0 ground, origin ON THE ROD AXIS;")
    P("the rocket sits centred at x=+%.1f mm (rod runs outside the tube)." % ROD_OFFSET)
    P("")

    doc = App.newDocument("PhoenixABS40-43_launchpad_%s" % REV)

    hub = build_hub()
    leg = build_leg()
    defl = build_deflector()
    parts = [("PadHub", hub), ("PadLeg", leg), ("BlastDeflector", defl)]
    qty = {"PadHub": 1, "PadLeg": LEG_N, "BlastDeflector": 1}

    # ------------------------------------------------------------------- [1]
    P("[1] bodies -- mass, envelope, watertight")
    meshes = {}
    tot = 0.0
    ok1 = True
    for n, s in parts:
        m = mesh_of(s)
        meshes[n] = m
        bb = s.BoundBox
        g = s.Volume * RHO
        tot += g * qty[n]
        dv = abs(m.Volume - s.Volume) / s.Volume * 100.0
        wt = "watertight" if (m.isSolid() and dv < 1.0) else "NOT SOLID"
        if not m.isSolid():
            ok1 = False
        P("  %-15s x%d  %8.2f g  bbox %6.1f x %6.1f x %6.1f  mesh-vs-solid %.2f%%  %s"
          % (n, qty[n], g, bb.XLength, bb.YLength, bb.ZLength, dv, wt))
    P("  pad total (printed, 100%% infill) %.1f g   +rod %.0f mm = %.1f g"
      % (tot, ROD_L_WANTED, tot + ROD_L_WANTED * ROD_RHO_LIN * 1000.0))
    P("  %s" % ("PASS" if ok1 else "FAIL -- a body is not a closed solid"))

    # ------------------------------------------------------------------- [2]
    P("")
    P("[2] rod socket")
    depth = HUB_TOP
    slop = ROD_BORE - ROD_D
    lean = math.degrees(math.atan2(slop, depth))
    P("  bore d%.2f on a d%.1f rod -> %.2f mm diametral slop" % (ROD_BORE, ROD_D, slop))
    P("  socket depth %.0f mm = %.1f x rod diameter" % (depth, depth / ROD_D))
    P("  rod lean from socket slop alone %.2f deg -> %.1f mm at the %.0f mm tip"
      % (lean, math.tan(math.radians(lean)) * ROD_L_WANTED, ROD_L_WANTED))
    P("  THROUGH bore, not blind: ream with a 4 mm bit after printing, and the")
    P("  rod bottoms on the GROUND -- no axial load into the ABS at all.")
    P("  %s" % ("PASS -- >= 15x rod dia, lean < 0.5 deg"
                if depth / ROD_D >= 15.0 and lean < 0.5 else "FAIL"))

    # ------------------------------------------------------------------- [3]
    P("")
    P("[3] leg / hub joint -- DESIGNED interference, not a clearance fit")
    intf = LEG_W - MORT_W
    cheek_w = (LEG_W - TEN_SLOT_W) / 2.0
    d = intf / 2.0
    I = (MORT_H - TEN_CLEAR_H) * cheek_w ** 3 / 12.0
    E = 2000.0
    F = 3.0 * E * I * d / TEN_SLOT_L ** 3
    S = (MORT_H - TEN_CLEAR_H) * cheek_w ** 2 / 6.0
    sig = F * TEN_SLOT_L / S
    P("  tenon %.2f wide into a %.2f mortise -> %.2f mm interference" % (LEG_W, MORT_W, intf))
    P("  split into 2 cheeks %.2f x %.1f x %.1f, each flexes %.3f mm"
      % (cheek_w, MORT_H - TEN_CLEAR_H, TEN_SLOT_L, d))
    P("  insertion force %.1f N per cheek, bending stress %.1f MPa (ABS yield ~40)" % (F, sig))
    P("  >>> that force is a LOWER BOUND.  Each cheek is %.1f tall x %.2f thick over"
      % (MORT_H - TEN_CLEAR_H, cheek_w))
    P("  >>> only %.0f mm of length -- L/t is %.1f, so it is a stub, and pure beam"
      % (TEN_SLOT_L, TEN_SLOT_L / cheek_w))
    P("  >>> theory understates it; the real fit is shear-dominated.  If the printed")
    P("  >>> leg needs a mallet, distrust THIS NUMBER first, not the geometry --")
    P("  >>> lengthen TEN_SLOT_L before touching LEG_W or MORT_W.")
    P("  engagement %.0f mm radial, %.1f mm deep bearing; mortise is BOTTOM-OPEN"
      % (MORT_DEPTH, MORT_H))
    P("  %s" % ("PASS -- hand-assembles, holds, stress < 40 MPa"
                if 2.0 < F < 60.0 and sig < 40.0 else "FAIL"))

    # ------------------------------------------------------------------- [4]
    P("")
    P("[4] assembly -- interference, every pair")
    legs = [rot_z(leg, 120.0 * i) for i in range(LEG_N)]
    asm = [("PadHub", hub), ("BlastDeflector", defl)]
    for i, L in enumerate(legs):
        asm.append(("PadLeg_%d" % i, L))
    expect = 2.0 * (MORT_H - TEN_CLEAR_H) * MORT_DEPTH * ((LEG_W - MORT_W) / 2.0)
    ok4 = True
    for i in range(len(asm)):
        for j in range(i + 1, len(asm)):
            na, sa = asm[i]
            nb, sb = asm[j]
            v = sa.common(sb).Volume
            if v < 1e-6:
                continue
            designed = (na == "PadHub" and nb.startswith("PadLeg"))
            tag = "designed squeeze (expect ~%.0f mm3)" % expect if designed else "CLASH"
            if not designed:
                ok4 = False
            P("  %-15s x %-15s %8.1f mm3   %s" % (na, nb, v, tag))
    P("  every other pair 0.000 mm3")
    P("  %s" % ("PASS -- the only overlap is the tenon squeeze from [3]"
                if ok4 else "FAIL -- an unintended clash"))

    # ------------------------------------------------------------------- [5]
    P("")
    P("[5] TIP-OVER -- run at the LAUNCH LIMIT, not at a speed that passes")
    zr = rest_z()
    m_hub = hub.Volume * RHO
    m_leg = leg.Volume * RHO
    m_def = defl.Volume * RHO
    m_rod = ROD_L_WANTED * ROD_RHO_LIN * 1000.0
    rocket_aft = zr                                    # fin TE on the ring
    rocket_cg_z = rocket_aft + FIN_AFT_OVERHANG + (BODY_L + NOSE_L - CG_FROM_NOSE)
    items = [(m_hub, HUB_BASE_H / 2.0), (LEG_N * m_leg, LEG_H_HUB / 3.0),
             (m_def, zr - RING_H / 2.0), (m_rod, ROD_L_WANTED / 2.0),
             (M_ROCKET, rocket_cg_z)]
    M = sum(m for m, _z in items)
    cg = sum(m * z for m, z in items) / M
    W = M / 1000.0 * 9.81
    lever = LEG_REACH * math.cos(math.radians(180.0 / LEG_N))   # 2-leg tip line
    P("  masses: hub %.0f g, legs 3x%.0f g, deflector %.0f g, rod %.0f g, rocket %.0f g"
      % (m_hub, m_leg, m_def, m_rod, M_ROCKET))
    P("  system %.0f g, CG %.0f mm up; tip line %.0f mm from the axis (worst: over"
      % (M, cg, lever))
    P("  the midpoint of two legs, rocket hanging that way)")

    a_body = R_AF_O * 2.0 / 1000.0 * ROCKET_L / 1000.0
    a_fins = 1.5 * FIN_AREA_EA / 1e6                   # ~1.5 fins broadside
    a_rod = ROD_D / 1000.0 * ROD_L_WANTED / 1000.0

    def over(v):
        mo = wind_force(a_body, v) * rocket_cg_z
        mo += wind_force(a_fins, v) * (rocket_aft + 60.0)
        mo += wind_force(a_rod, v) * (ROD_L_WANTED / 2.0)
        # The rocket hangs ROD_OFFSET off the rod axis and is free to SPIN on the
        # rod (same fact [7] rests on), so its offset can point anywhere -- and
        # wind weathercocks it to the DOWNWIND side, i.e. the way the pad tips.
        # Booking it as overturning is algebraically identical to shortening its
        # restoring lever from `lever` to `lever - ROD_OFFSET`, which is the true
        # worst case.  Do NOT "correct" this to a restoring term.
        mo += M_ROCKET / 1000.0 * 9.81 * ROD_OFFSET
        return mo

    for v, tag in ((WIND_CALM, "calm"), (WIND_LIMIT, "LIMIT")):
        for bal, bt in ((0.0, "bare"), (BALLAST_KG, "%.1f kg on the tie-down" % BALLAST_KG)):
            res = (W + bal * 9.81) * lever
            mo = over(v)
            P("  %5.1f m/s %-5s  %-22s  restoring %6.0f / overturning %6.0f  = %.2f x  %s"
              % (v, tag, bt, res, mo, res / mo, "PASS" if res / mo >= 1.0 else "FAIL"))
    # highest wind the bare pad survives
    k_wind = (over(1.0) - M_ROCKET / 1000.0 * 9.81 * ROD_OFFSET)
    vmax = math.sqrt(max(0.0, (W * lever - M_ROCKET / 1000.0 * 9.81 * ROD_OFFSET) / k_wind))
    P("  bare pad tips at %.1f m/s.  FAIL at the %.0f m/s limit is REAL and the fix"
      % (vmax, WIND_LIMIT))
    P("  is geometry, not prose: a tent peg through each foot's d%.1f hole, and/or" % PEG_D)
    P("  %.1f kg hung on the hub's d%.1f tie-down.  Staking is the PRIMARY" % (BALLAST_KG, TIE_D))
    P("  stability mechanism at realistic wind -- not an optional extra.")
    P("  (Growing the legs instead would need ~%.0f mm of reach. Not worth it.)"
      % (LEG_REACH * over(WIND_LIMIT) / (W * lever)))

    # ------------------------------------------------------------------- [6]
    P("")
    P("[6] GUIDED RAIL LENGTH -- the pad eats the rail budget")
    lug_bot = zr + FIN_AFT_OVERHANG + (BODY_L / 2.0 - LUG_LEN / 2.0)
    lug_top = lug_bot + LUG_LEN
    P("  rest plane (ring top) Z %.0f; fin TE there; body aft end Z %.0f"
      % (zr, zr + FIN_AFT_OVERHANG))
    P("  single mid-body lug: bottom Z %.0f, top Z %.0f" % (lug_bot, lug_top))
    P("  DEFINITION USED: travel until the lug is FULLY off the rod = L - %.0f mm."
      % lug_top)
    P("  (OpenRocket's convention -- aft end of the aft-most guide -- would read")
    P("   L - %.0f mm, %.0f mm longer.  The conclusion is the same either way.)"
      % (lug_bot, LUG_LEN))
    ok6 = True
    for L in (ROD_L_ASSUMED, 1300.0, ROD_L_WANTED, 1500.0):
        tr = L - lug_top
        v = "PASS" if tr >= RAIL_MIN else "FAIL"
        if L == ROD_L_ASSUMED and tr < RAIL_MIN:
            ok6 = False
        P("  rod %6.0f mm -> guided travel %6.0f mm   vs >=%.0f (4.4 light)  %s"
          % (L, tr, RAIL_MIN, v))
    P("  >>> A 1 m rod gives only %.0f mm of guidance.  4.4's already-marginal"
      % (ROD_L_ASSUMED - lug_top))
    P("  >>> 15.4 m/s on an A8-3 was computed at 1.0 m of rail; v ~ sqrt(s) puts")
    P("  >>> this at ~%.1f m/s -- UNDER the 15 m/s floor 4.4 itself sets."
      % (15.4 * math.sqrt((ROD_L_ASSUMED - lug_top) / 1000.0)))
    P("  >>> BUY >= %.0f mm of rod for the light config, and >= %.0f mm for the"
      % (RAIL_MIN + lug_top, RAIL_MIN_PAYLOAD + lug_top))
    P("  >>> payload config (4.4 wants 1.2-1.5 m of rail there).")
    P("  %s" % ("FAIL at %.0f mm rod -- deliberate, see above" % ROD_L_ASSUMED
                if not ok6 else "PASS"))
    P("  FOLLOW-UP (12: the .ork is authoritative for simulation): set rail length")
    P("  to the travel figure above and re-run the whole 4.4 motor matrix.")

    # ------------------------------------------------------------------- [7]
    P("")
    P("[7] fin rest -- does every fin land on the ring, at EVERY clocking?")
    P("  the rod is %.0f mm off the body axis, so the 3 fins are NOT symmetric" % ROD_OFFSET)
    P("  about the ring; the naive argument does not hold.  Swept 0-120 deg:")
    worst_phi, worst = None, 1e9
    for i in range(241):
        phi = 120.0 * i / 240.0
        c = min(fin_contact_len(phi))
        if c < worst:
            worst, worst_phi = c, phi
    tot_worst = fin_contact_len(worst_phi)
    P("  ring band r %.0f .. %.0f mm from the rod axis, %.0f mm tall"
      % (RING_RI, RING_RO, RING_H))
    P("  worst clocking %.1f deg: fin contact runs %.1f / %.1f / %.1f mm"
      % (worst_phi, tot_worst[0], tot_worst[1], tot_worst[2]))
    P("  minimum contact on ANY fin at ANY clocking: %.1f mm" % worst)
    P("  %s" % ("PASS -- all 3 fins always land on the band"
                if worst > 3.0 else "FAIL -- a fin can drop inside the ring"))
    P("  note: the rev-5 fin TE is only 0.4 mm off square over the 55 mm span,")
    P("  so the rest is a line contact, not a point.")

    # ------------------------------------------------------------------- [8]
    P("")
    P("[8] blast -- standoff, coverage, vent area")
    stand = RING_H - (FIN_AFT_OVERHANG - MOTOR_AFT_OVERHANG)
    bare = FIN_AFT_OVERHANG - MOTOR_AFT_OVERHANG
    win_a = WIN_N * (WIN_W * WIN_RECT_H + math.pi * (WIN_W / 2.0) ** 2 / 2.0)
    throat = math.pi * (NOZZLE_THROAT_D / 2.0) ** 2
    P("  nozzle sits %.0f mm above the deflector floor (a BARE plate would give %.0f mm)"
      % (stand, bare))
    P("  deflector d%.0f: nozzle is at r %.0f from the rod, so %.0f mm of plate all round"
      % (DEFL_D, ROD_OFFSET, DEFL_D / 2.0 - ROD_OFFSET))
    P("  vent area %.0f mm2 through %d arched windows vs %.1f mm2 of throat = %.0f x"
      % (win_a, WIN_N, throat, win_a / throat))
    P("  windows are rectangle + semicircular arch -> ZERO bridging, no supports")
    P("  liner: d%.0f x %.1f recess in the floor takes a slotted steel/alu disc"
      % (LINER_D, LINER_T))
    P("  %s" % ("PASS" if stand >= 25.0 and win_a / throat > 20.0 else "FAIL"))

    # ------------------------------------------------------------------ [8b]
    P("")
    P("[8b] RING ROOT SUPPORT -- is the ring standing on solid disc?")
    P("  the v1 draft had LINER_D 100 and bored the ring from 1 mm BELOW the")
    P("  floor, against a RING_RI of %.0f -- so the recess reached 6 mm under the" % RING_RI)
    P("  ring and left its inner third standing on a %.1f mm void." % LINER_T)
    P("  Neither [1] (watertight), [4] (interference), [11] (overhangs) nor [12]")
    P("  (non-vacuity) could see it: the part was a perfectly valid closed solid")
    P("  with a hole in the wrong place.  Only looking at a render caught it.")
    P("  So: measure the ring's footprint directly.")
    z1 = HUB_COL_TOP + DEFL_T                      # deflector floor (== ring root)
    band = cyl(RING_RO, z1 - LINER_T, z1).cut(cyl(RING_RI, z1 - LINER_T, z1))
    got = defl.common(band).Volume
    want = band.Volume
    frac = got / want * 100.0
    P("  disc material in the ring's footprint (r %.0f..%.0f, the top %.1f mm):"
      % (RING_RI, RING_RO, LINER_T))
    P("    %.1f of %.1f mm3 = %.1f %% solid" % (got, want, frac))
    P("  liner recess d%.0f vs ring bore d%.0f -> %.1f mm of clear floor inside"
      % (LINER_D, 2 * RING_RI, RING_RI - LINER_D / 2.0))
    P("  DISCRIMINATES: the same measurement run against a rebuild of the broken")
    P("  draft (LINER_D 100, ring bored from below) reads 970.8 / 2742.6 = 35.4 %,")
    P("  so this check distinguishes the two builds -- it is not a check that")
    P("  passes on anything you hand it.")

    # ------------------------------------------------------------------ [8c]
    P("")
    P("[8c] DEFLECTOR SEAT -- does the hub actually hold the disc up?")
    P("  [4] proves nothing here: a disc resting on a seat that is too NARROW")
    P("  interferes with nothing and is a perfectly good solid.  What matters is")
    P("  whether the resultant of the loads on the disc lands inside its seat.")
    seat_ri, seat_ro = DEFL_BORE / 2.0, HUB_COL_D / 2.0
    w_def = m_def / 1000.0 * 9.81
    w_rkt = M_ROCKET / 1000.0 * 9.81
    res_r = w_rkt * ROD_OFFSET / (w_def + w_rkt)
    tilt_d = math.degrees(math.atan2(2 * CL_REG, DEFL_T))
    P("  seat = hub top face minus the spigot: r %.2f .. %.2f  (%.2f mm wide)"
      % (seat_ri, seat_ro, seat_ro - seat_ri))
    P("  loads on the disc: its own %.2f N at r 0, the rocket's %.2f N at r %.1f"
      % (w_def, w_rkt, ROD_OFFSET))
    P("  -> resultant at r %.2f mm" % res_r)
    P("  if it fell outside, the disc would rock on the seat's outer circle until")
    P("  the d%.1f bore binds on the d%.1f spigot: %.1f deg, %.1f mm of drop at the"
      % (DEFL_BORE, HUB_SPIG_D, tilt_d, math.tan(math.radians(tilt_d)) * 48.0))
    P("  fin band -- which would break [7]'s three-fin contact.")
    P("  DISCRIMINATES: the d26 column of the first draft seats only r 10.2..13.0,")
    P("  and this check reads 16.8 > 13.0 against it.")
    P("  %s" % ("PASS -- resultant inside the seat by %.1f mm" % (seat_ro - res_r)
                if res_r <= seat_ro
                else "FAIL -- resultant %.1f mm outside the seat" % (res_r - seat_ro)))

    # ------------------------------------------------------------------ [8d]
    P("")
    P("[8d] RING TOP CONTINUITY -- [7] assumed a full annulus; prove it")
    P("  [7] sweeps the fin clocking against the ring's RADII and treats the top")
    P("  as an unbroken band.  That is only true while the windows stop below the")
    P("  rim.  Raise WIN_RECT_H or WIN_W and [7] still passes while the ring turns")
    P("  into a fin trap -- a fin's contact spans only ~3 deg in plan against a")
    P("  %.0f deg window gap.  So measure the rim, do not assume it."
      % math.degrees(WIN_W / ((RING_RI + RING_RO) / 2.0)))
    rt = zr                                          # ring top == rest plane
    rim = cyl(RING_RO, rt - 1.0, rt).cut(cyl(RING_RI, rt - 1.0, rt))
    got_r = defl.common(rim).Volume
    frac_r = got_r / rim.Volume * 100.0
    win_top = HUB_COL_TOP + DEFL_T + WIN_RECT_H + WIN_W / 2.0
    P("  window top Z %.1f, ring top Z %.1f -> %.1f mm of continuous rail"
      % (win_top, rt, rt - win_top))
    P("  solid in the rim's top 1 mm (r %.0f..%.0f): %.1f of %.1f mm3 = %.1f %%"
      % (RING_RI, RING_RO, got_r, rim.Volume, frac_r))
    P("  %s" % ("PASS -- the rest is a continuous annulus, so [7] is valid"
                if frac_r > 99.9 else
                "FAIL -- windows break the rim; [7]'s sweep is no longer valid"))
    P("  %s" % ("PASS -- ring root fully supported, no undercut"
                if frac > 99.9 and LINER_D < 2 * RING_RI
                else "FAIL -- the ring is undercut; shrink LINER_D below 2*RING_RI"))

    # ------------------------------------------------------------------ [8e]
    P("")
    P("[8e] RING RIM IMPACT -- worst-case fin load landing on a window gap")
    P("  [7] proves a fin always finds material; [8d] proves the top rim is an")
    P("  unbroken annulus.  Neither puts a number on what that rim can TAKE.")
    P("  Worst case: a fin's line contact lands at the MIDSPAN of a window gap,")
    P("  so the load crosses the gap in bending before it reaches a pillar, and")
    P("  the rocket only rests on 3 points -- nothing stops it rocking onto ONE")
    P("  fin, so that fin's load bound is the WHOLE rocket weight, not a third.")
    P("  Modelled as a simply-supported beam across the gap (conservative: the")
    P("  rim is actually continuous into the pillars on both sides). Landing on")
    P("  a pillar instead of a gap is far less severe -- short stub in near-pure")
    P("  compression -- so the gap midspan is the case worth a number.")

    ABS_YIELD = 40.0
    E_RIM = 2000.0

    def rim_case(w, rect_h, drop_h):
        L = w                                   # gap arc length ([8d]'s own approx)
        rim_h = RING_H - (rect_h + w / 2.0)     # solid cap left above the arch
        thick = RING_RO - RING_RI
        I = thick * rim_h ** 3 / 12.0
        S = I / (rim_h / 2.0)
        d_static = w_rkt * L ** 3 / (48.0 * E_RIM * I)
        daf = 1.0 + math.sqrt(1.0 + 2.0 * drop_h / d_static)
        P_dyn = w_rkt * daf
        sig = P_dyn * L / 4.0 / S
        P_yield = ABS_YIELD * S * 4.0 / L
        daf_y = P_yield / w_rkt
        h_yield = d_static * ((daf_y - 1.0) ** 2 - 1.0) / 2.0
        return L, rim_h, thick, I, S, d_static, daf, P_dyn, sig, h_yield

    DROP_H = 10.0                                # assumed careless set-down height
    (L, rim_h, thick, I, S, d_static, daf, P_dyn, sig, h_yield) = rim_case(WIN_W, WIN_RECT_H, DROP_H)
    (_, _, _, _, _, _, _, _, sig_old, h_yield_old) = rim_case(22.0, 21.0, DROP_H)

    P("  gap span %.1f mm, rim cap %.1f mm tall x %.1f mm thick (I=%.0f mm4, S=%.0f mm3)"
      % (L, rim_h, thick, I, S))
    P("  static deflection under the rocket's full %.2f N on one fin: %.4f mm" % (w_rkt, d_static))
    P("  assumed %.0f mm careless-set-down drop -> rigid-drop DAF %.0fx (same method as"
      % (DROP_H, daf))
    P("  the ejection POC's [5b]), dynamic load %.0f N, bending stress %.1f MPa vs yield ~%.0f"
      % (P_dyn, sig, ABS_YIELD))
    P("  drop height that reaches yield: %.0f mm now, vs %.0f mm before WIN_W 22->%.0f"
      % (h_yield, h_yield_old, WIN_W))
    P("  (widening the windows LOWERED the impact stress at a fixed drop height -- the")
    P("  longer, softer span spreads the same impact energy over more deflection: %.1f MPa"
      % sig)
    P("  now vs %.1f MPa before, at the same %.0f mm drop)" % (sig_old, DROP_H))
    P("  %s" % (("PASS" if sig < ABS_YIELD else "FAIL") + " at the assumed %.0f mm drop" % DROP_H))
    P("  >>> conservative rigid-body-drop bound, same caveat as the ejection POC's [5b]:")
    P("  >>> at a %.4f mm static deflection, real contact compliance and local damping" % d_static)
    P("  >>> will do better than idealized elastic-beam theory predicts here.  Treat")
    P("  >>> %.0f mm as a lower bound on how carelessly this can be set down, not a" % h_yield)
    P("  >>> hard number.")

    # ------------------------------------------------------------------- [9]
    P("")
    P("[9] LUG BORE vs THIS ROD -- OPEN, and it is not a footnote")
    rad = (LUG_BORE - ROD_D) / 2.0
    tilt = math.degrees(math.atan2(LUG_BORE - ROD_D, LUG_LEN))
    P("  DESIGN.md 2.2 / 9 spec the lug bore at d%.1f, sized for a 3/16 in" % LUG_BORE)
    P("  (4.8 mm) rod.  This pad is built for the d%.1f rod the user HAS." % ROD_D)
    P("  -> %.2f mm radial slop, %.2f deg of rocket tilt inside the lug," % (rad, tilt))
    P("     = %.0f mm of pointing error at the nose."
      % (math.tan(math.radians(tilt)) * ROCKET_L))
    P("  The lug is NOT MODELLED (12.1 'not modeled at all'), so there is nothing")
    P("  to fix in CAD today.  REQUIREMENT when it is modelled: bore d%.1f." % (ROD_D + 0.4))
    P("  OPEN -- deliberately not a PASS.  Pad-vs-airframe rod size is inconsistent")
    P("  until either the lug is bored d4.4 or a 4.8 mm rod is bought instead.")
    P("  If 9's 'two lugs or rail buttons' is adopted, the AFT lug sets the rest")
    P("  height; the fins still land on the ring, so this pad is unchanged.")

    # ------------------------------------------------------------------ [10]
    P("")
    P("[10] rod whip -- a d4 rod this long is not stiff")
    I_rod = math.pi * ROD_D ** 4 / 64.0
    EI = ROD_E * I_rod
    for L in (ROD_L_ASSUMED, ROD_L_WANTED, 1800.0):
        w = wind_force(ROD_D / 1000.0 * L / 1000.0, WIND_CALM) / L        # N/mm
        d_dist = w * L ** 4 / (8.0 * EI)
        a = rocket_cg_z
        Fb = wind_force(a_body + a_fins, WIND_CALM)
        d_pt = Fb * a * a * (3.0 * L - a) / (6.0 * EI) if a < L else 0.0
        P("  L %6.0f mm  at %.0f m/s: tip %.1f mm from rod drag + %.1f mm from the"
          % (L, WIND_CALM, d_dist, d_pt))
        P("             rocket = %.1f mm total (%.2f deg of launch-angle error)"
          % (d_dist + d_pt, math.degrees(math.atan2(d_dist + d_pt, L))))
    P("  The rocket rests on the DEFLECTOR, not on the rod, so the rod carries no")
    P("  axial load and Euler buckling is not a mode here at all.")
    P("  %.0f mm is the practical ceiling for d4; past that, go to a rail." % ROD_L_WANTED)

    # ------------------------------------------------------------------ [11]
    P("")
    P("[11] printability -- AS ORIENTED ON THE BED, which is not the use frame")
    hb, lb, db = hub.BoundBox, leg.BoundBox, defl.BoundBox
    P("  PadHub          bed %5.1f x %5.1f, %5.1f tall   (use frame, unrotated)"
      % (hb.XLength, hb.YLength, hb.ZLength))
    P("                  bore vertical.  Mortises are BOTTOM-OPEN -> the only")
    P("                  overhang is a %.1f mm bridge at their roof." % MORT_W)
    P("  PadLeg          bed %5.1f x %5.1f, %5.1f tall   (LAID FLAT: the model's"
      % (lb.XLength, lb.ZLength, lb.YLength))
    P("                  %.0f mm depth goes DOWN on the bed, its %.1f mm width"
      % (lb.ZLength, lb.YLength))
    P("                  becomes the print height -- %.1f mm at the foot boss,"
      % lb.YLength)
    P("                  %.1f mm along the blade.)  Layers then stack across the" % LEG_W)
    P("                  WIDTH, so the bending stress -- along the leg, varying")
    P("                  through its depth -- is entirely IN-PLANE.  Same argument")
    P("                  as the ejection POC's axially-printed shaft.  Big bed")
    P("                  contact, no brim, no supports.")
    P("  BlastDeflector  bed %5.1f x %5.1f, %5.1f tall   disc down.  Arched"
      % (db.XLength, db.YLength, db.ZLength))
    P("                  windows are self-supporting.")
    P("  No part needs support material.  Largest footprint %.0f mm." % lb.XLength)

    # ------------------------------------------------------------------ [12]
    P("")
    P("[12] non-vacuity -- every cut actually removed material")
    ok12 = True
    feats = [
        ("hub rod bore d%.2f x %.0f" % (ROD_BORE, HUB_TOP),
         math.pi * (ROD_BORE / 2.0) ** 2 * HUB_TOP),
        ("hub mortises x%d" % LEG_N, LEG_N * MORT_W * MORT_H * MORT_DEPTH),
        ("hub tie-down d%.1f" % TIE_D, math.pi * (TIE_D / 2.0) ** 2
         * 2.0 * math.sqrt((HUB_BASE_D / 2.0) ** 2 - TIE_Y ** 2)),
        ("leg tenon slot", TEN_SLOT_W * TEN_SLOT_L * (MORT_H - TEN_CLEAR_H)),
        ("leg peg hole d%.1f" % PEG_D, math.pi * (PEG_D / 2.0) ** 2 * FOOT_H),
        ("deflector windows x%d" % WIN_N, WIN_N * (WIN_W * WIN_RECT_H
         + math.pi * (WIN_W / 2.0) ** 2 / 2.0) * (RING_RO - RING_RI)),
        ("deflector liner recess", math.pi * (LINER_D / 2.0) ** 2 * LINER_T
         - math.pi * (DEFL_BORE / 2.0) ** 2 * LINER_T),
        ("deflector bore d%.1f" % DEFL_BORE,
         math.pi * (DEFL_BORE / 2.0) ** 2 * DEFL_T),
    ]
    for nm, v in feats:
        good = v > 1.0
        if not good:
            ok12 = False
        P("  %-32s removes %9.1f mm3  %s" % (nm, v, "ok" if good else "VACUOUS"))
    P("  %s" % ("PASS -- no cut is a no-op" if ok12 else "FAIL"))

    # ------------------------------------------------------------------ [13]
    P("")
    P("[13] export")
    if not os.path.isdir(MODELS):
        os.makedirs(MODELS)
    for n, s in parts:
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        stem = "PhoenixABS40-43_%s_%s" % (n, REV)
        s.exportStep(os.path.join(MODELS, stem + ".step"))
        meshes[n].write(os.path.join(MODELS, stem + ".stl"))
        P("  %-15s -> Models/%s.step + .stl" % (n, stem))

    # assembly, in the as-launched position, with the rocket as reference only
    asm_shapes = [hub, defl] + legs
    comp = Part.makeCompound(asm_shapes)
    ao = doc.addObject("Part::Feature", "Assembly_pad")
    ao.Shape = comp
    full = mesh_of(asm_shapes[0])
    for s in asm_shapes[1:]:
        full.addMesh(mesh_of(s))
    ap = os.path.join(MODELS, "PhoenixABS40-43_launchpad_ASSEMBLY_%s.stl" % REV)
    full.write(ap)
    bb = comp.BoundBox
    P("  Assembly_pad   %d bodies  bbox %.0f x %.0f x %.0f  -> Models/%s"
      % (len(asm_shapes), bb.XLength, bb.YLength, bb.ZLength, os.path.basename(ap)))

    # reference: rod + rocket where they actually sit.  NEVER exported as a part.
    rod_ref = cyl(ROD_D / 2.0, 0.0, ROD_L_WANTED)
    body = cyl(R_AF_O, zr + FIN_AFT_OVERHANG, zr + FIN_AFT_OVERHANG + BODY_L,
               x=ROD_OFFSET)
    ref = {"Ref_Rod": rod_ref, "Ref_RocketBody": body}
    for n, s in ref.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        o.Visibility = False
    P("  Ref_Rod / Ref_RocketBody placed as-launched (hidden, never exported)")

    doc.recompute()
    doc.saveAs(os.path.join(MODELS, "PhoenixABS40-43_launchpad_%s.FCStd" % REV))
    P("  FCStd -> Models/PhoenixABS40-43_launchpad_%s.FCStd" % REV)

    # ------------------------------------------------------------------ [14]
    P("")
    P("[14] print files -- PRE-ORIENTED, generated here, never hand-placed")
    if not os.path.isdir(PRINTS):
        os.makedirs(PRINTS)
    if not os.path.isdir(RTP):
        os.makedirs(RTP)

    def oriented(n, s):
        """Return the shape rotated into its print pose and dropped to Z=0."""
        o = s.copy()
        if n == "PadLeg":
            # lay the blade flat: the 26 mm DEPTH goes down onto the bed, the
            # 6.7 mm WIDTH becomes the print height, so layers stack across the
            # width and the bending stress stays in-plane ([11])
            o.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90.0)
        bb = o.BoundBox
        o.translate(Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
        return o

    for n, s in parts:
        raw = mesh_of(s)
        raw.write(os.path.join(PRINTS, "PhoenixABS40-43_%s_%s.stl" % (n, REV)))
        po = oriented(n, s)
        mesh_of(po).write(os.path.join(RTP, "PhoenixABS40-43_%s_%s.stl" % (n, REV)))
        bb = po.BoundBox
        P("  %-15s x%d  bed %5.1f x %5.1f, %5.1f tall %s"
          % (n, qty[n], bb.XLength, bb.YLength, bb.ZLength,
             "(laid flat)" if n == "PadLeg" else "(as modelled)"))
        if abs(bb.ZMin) > 1e-6:
            P("      FAIL -- not dropped to Z=0")
    P("  -> Print Files/Launch Pad/  and  .../Ready to Print/")
    P("  PadLeg: PRINT x%d.  Every part sits on Z=0, no supports, no brim." % LEG_N)

    # ------------------------------------------------------------------- sum
    P("")
    P("SUMMARY")
    P("  * 3 unique parts, 5 printed pieces, NO bought hardware, no supports.")
    P("  * Assembly: push 3 legs into the hub, drop the deflector over the")
    P("    spigot, drop the rod down the bore to the ground.  That is the pad.")
    P("  * The rocket rests FINS-DOWN on the standoff ring -- a clamp collar on")
    P("    the rod is geometrically impossible (see the header, (a)).")
    P("  * FAIL [6] IS THE HEADLINE: a 1 m rod gives only %.0f mm of guidance."
      % (ROD_L_ASSUMED - lug_top))
    P("    Buy >= %.0f mm (light) / >= %.0f mm (payload) of d4 rod, then set the"
      % (RAIL_MIN + lug_top, RAIL_MIN_PAYLOAD + lug_top))
    P("    rail length in the .ork and re-run 4.4's motor matrix.")
    P("  * FAIL [5] IS REAL: the bare pad tips at %.1f m/s.  Peg it down, and/or" % vmax)
    P("    hang %.0f kg on the tie-down.  Staking is primary, not optional." % BALLAST_KG)
    P("  * OPEN [9]: the d5 lug bore is specced for a 4.8 mm rod, not this 4.0 mm")
    P("    one.  Bore the lug d%.1f when it is modelled, or buy a 4.8 mm rod." % (ROD_D + 0.4))
    P("  * UNPRINTED and UNFLOWN.  Nothing here has met a motor.")

    rpt = "\n".join(log)
    print(rpt)
    with open(os.path.join(MODELS, "launchpad_build_report_%s.txt" % REV), "w") as fh:
        fh.write(rpt + "\n")


main()

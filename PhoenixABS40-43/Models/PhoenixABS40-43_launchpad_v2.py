# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- LAUNCH PAD v2: aluminium blast plate, rod-stop post, fuse clip

SOURCE OF TRUTH for pad v2.  v1 (PhoenixABS40-43_launchpad_v1.py) is NOT edited:
this script exec()s v1's source (minus its trailing main() call) to reuse the
PadHub and PadLeg builders unchanged, then replaces the printed BlastDeflector.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" <this file>

------------------------------------------------------------------------------
WHAT CHANGED FROM v1  (user, 2026-10-27)
------------------------------------------------------------------------------
  * The printed deflector (disc + arched-window ring) is GONE.  The blast plate
    is a BOUGHT d155 aluminium disc, 2 mm, with ONE d20.5 hole: it drops over
    the hub's d20 spigot and sits on the d44 column top.  No vent holes -- the
    jet hits metal and spreads sideways over an open plate.
  * The rocket no longer rests on its fins.  It HANGS on its launch lug, on top
    of the StopPost: the rocket is kept off the pad entirely.
  * Non-electric fuse: a clip on the StopPost holds it under the nozzle.

  PadHub    x1  v1, unchanged (print v1's STL)
  PadLeg    x3  v1, unchanged (print v1's STL)
  BlastPlate x1 BOUGHT: alu d155 x 2, d20.5 centre hole
  StopPost  x1  NEW, printed: rod stop + rotation key + fuse clip

------------------------------------------------------------------------------
WHY THE STOP IS A POST, NOT A COLLAR CLAMPED TO THE ROD
------------------------------------------------------------------------------
v1's header (a) still holds, harder: on D9aft the rod line is r 25.95 off the
body axis and the cap's grip ribs (r 22.75) come within 1.0 mm of the ROD
SURFACE.  The cap slides past every height above its rest position while the
rocket is loaded, so nothing can wrap the rod on the body side anywhere above
the cap.  A collar under the lug would need a ~0.5 mm wall there.

So the stop is a COLUMN that stands on the hub spigot beside the rod, on the
side AWAY from the body:
  * bottom 40 mm (below the cap) is a full block round the rod -> captured,
    and it carries the fuse-clip arm;
  * above that it is a U-channel: the rod rides in a groove, the body side is
    cut away on a circle CRADLE_R round the body axis (clears the cap ribs even
    with the rocket leaning on its lug slop -- [6]);
  * the two cradle HORNS key the rocket's rotation about the rod, so the nozzle
    stays over the fuse clip ([7]).  The post itself turns freely on the rod:
    rocket + post + fuse turn together, which is harmless.
  * the lug's aft end sits on the post top: rest height is the post height.

------------------------------------------------------------------------------
FRAME
------------------------------------------------------------------------------
Z = 0 at the ground; +Z up.  Origin ON THE ROD AXIS.  The rocket body axis is at
x = +ROD_LINE_R (so the body side is +x, the post's back is -x).
Rocket station s (mm from the nose base, AFT_DEPLOY_D9_DESIGN.md table frame;
the v12/v13 extension ring is FORWARD of station 0 and changes nothing here)
maps to Z = STOP_TOP + (LL_ST1 - s).
"""

import os
import math

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

# ============================================================ reuse v1 builders

MODELS = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry",
                      "PhoenixABS40-43", "Models")
_V1 = os.path.join(MODELS, "PhoenixABS40-43_launchpad_v1.py")
_src = open(_V1, encoding="utf-8").read().rstrip()
assert _src.endswith("main()"), "v1 no longer ends in main() -- check before reuse"
V1 = {"__name__": "launchpad_v1_lib"}
exec(compile(_src[:-len("main()")], _V1, "exec"), V1)

cyl, box, rot_z, mesh_of = V1["cyl"], V1["box"], V1["rot_z"], V1["mesh_of"]
build_hub, build_leg = V1["build_hub"], V1["build_leg"]
HUB_COL_TOP, HUB_TOP, HUB_SPIG_D = V1["HUB_COL_TOP"], V1["HUB_TOP"], V1["HUB_SPIG_D"]
HUB_BASE_D, HUB_BASE_H, LEG_N, LEG_REACH = (V1["HUB_BASE_D"], V1["HUB_BASE_H"],
                                            V1["LEG_N"], V1["LEG_REACH"])
LEG_H_HUB, PEG_D, TIE_D = V1["LEG_H_HUB"], V1["PEG_D"], V1["TIE_D"]
ROD_D, ROD_BORE, ROD_RHO_LIN = V1["ROD_D"], V1["ROD_BORE"], V1["ROD_RHO_LIN"]
ROD_L_ASSUMED, ROD_L_WANTED = V1["ROD_L_ASSUMED"], V1["ROD_L_WANTED"]
RAIL_MIN, RAIL_MIN_PAYLOAD = V1["RAIL_MIN"], V1["RAIL_MIN_PAYLOAD"]
RHO, CL_REG = V1["RHO"], V1["CL_REG"]
WIND_LIMIT, WIND_CALM, BALLAST_KG = V1["WIND_LIMIT"], V1["WIND_CALM"], V1["BALLAST_KG"]
FIN_AREA_EA, wind_force = V1["FIN_AREA_EA"], V1["wind_force"]

# ================================================================== parameters

PROJECT = os.path.dirname(MODELS)
PRINTS = os.path.join(PROJECT, "Print Files", "Launch Pad")
RTP = os.path.join(PRINTS, "Ready to Print")
REV = "v2"

# --- bought blast plate ---------------------------------------------------
PLATE_D = 155.0
PLATE_T = 2.0                 # ASSUMED -- any 1.5..3 works; spigot must stay proud
PLATE_HOLE = HUB_SPIG_D + 0.5 # d20.5 over the d20 spigot
RHO_AL = 2.70e-3
PLATE_TOP = HUB_COL_TOP + PLATE_T

# --- the vehicle: D9aft (AFT_DEPLOY_D9_DESIGN.md 2, D9aft_v1.py, v13 report)
ROD_LINE_R = 25.95            # rod centre off the body axis (D9aft LL_C)
R_OD = 21.5
LL_RO, LL_RI = 3.5, 2.2       # launch lug d7 / bore d4.4
LL_WEB = 4.0                  # lug standoff web, tangential thickness
LL_ST0, LL_ST1 = 152.5, 187.5 # lug forward / aft end, stations
CAP_ST0, CAP_ST1 = 340.0, 357.0   # MotorRetainerCap v1: body aft end .. cap aft face
CAP_RIB_R = 22.75             # cap grip ribs
CAP_HOLE_R = 7.5              # cap aft opening (sectioned from the cap STEP)
RIB_ROD_CLEAR = 1.0           # D9aft: rib to rod SURFACE, by design
FIN_ANG_PAD = (0.0, 120.0, 240.0)  # about the body axis, 0 = +x (away from the rod):
                                   # D9aft fins 0/120/240, lug 300 -> fins 60 off the rod line
FIN_TIP_R = R_OD + 55.0
FIN_T = 3.0                   # envelope thickness (ASSUMED, fins are ~2.4 + fillets)
FIN_ST_LE, FIN_ST_TE = 288.6, 344.0   # conservative box: fin-can front .. TE (4 mm overhang)
M_ROCKET = 274.0              # g, liftoff on the D9-5 (D9aft v13 report)
CG_FROM_TIP = 248.1
TIP_ST = -95.0                # tip = station + 30 + 65 (v13)

# --- StopPost --------------------------------------------------------------
NOZZLE_STANDOFF = 50.0        # cap aft face above the plate top
STOP_TOP = PLATE_TOP + NOZZLE_STANDOFF + (CAP_ST1 - LL_ST1)   # lug aft end rests here
POST_Z0 = HUB_TOP             # stands on the spigot top
POST_BACK = 9.0               # -x extent: flat back, the print face
POST_HALF_W = 13.0            # +-y: the horns that key rotation
CRADLE_CL = 0.5
CRADLE_R = CAP_RIB_R + RIB_ROD_CLEAR + CRADLE_CL   # 24.25: clears the ribs even when the
                              # rocket leans on its lug slop until the ribs touch the rod
POST_BORE = ROD_BORE          # d4.2, ream with a 4 mm bit like the hub
GROOVE_R = 2.15               # rod groove in the U-channel, looser than the bore
BASE_H = 40.0                 # full block round the rod, from POST_Z0
BASE_FRONT = 9.0              # +x extent of the block (cap is far above it)

# --- fuse clip ---------------------------------------------------------------
FUSE_D = 2.0                  # Klima Fuse KL-0010: d2 mm, 80-110 s/m (Astra datasheet)
FUSE_BURN = (80.0, 110.0)     # s per metre
FUSE_HOLE = FUSE_D + 0.2
FUSE_SLIT = FUSE_D - 0.5      # snap-in throat (1.5 for the d2 Klima fuse)
FUSE_OFF = 14.0               # clip axis off the nozzle axis (+y): out of the jet core
CLIP_TOP = 80.0
CLIP_H = 14.0                 # tall: a d2 fuse is floppy, guide it further
CLIP_S = 8.0                  # clip block, square
LEG_END_WEB = 0.6             # print-only web closing the leg's tenon slot at the tip; cut after print
ARM_W = CLIP_S               # arm and clip one width: no ledge in the print pose
BASE_HALF_W = FUSE_OFF + ARM_W / 2.0   # block carries the arm's root from the bed up

# ==================================================================== builders


def body_xy(x, y):
    return Vector(ROD_LINE_R + x, y, 0)


def build_post():
    z0, zb, z1 = POST_Z0, POST_Z0 + BASE_H, STOP_TOP
    # U-channel, full height, then the solid block round the rod at the bottom
    col = box(-POST_BACK, ROD_LINE_R, -POST_HALF_W, POST_HALF_W, z0, z1)
    col = col.cut(cyl(CRADLE_R, z0 - 1, z1 + 1, x=ROD_LINE_R))
    col = col.cut(cyl(GROOVE_R, zb, z1 + 1))
    base = box(-POST_BACK, BASE_FRONT, -BASE_HALF_W, BASE_HALF_W, z0, zb)
    s = col.fuse(base)
    s = s.cut(cyl(POST_BORE / 2.0, z0 - 1, zb + 1))

    # arm + clip: from the block out along y = FUSE_OFF to under the nozzle
    cz0, cz1 = CLIP_TOP - CLIP_H, CLIP_TOP
    cx, cy = ROD_LINE_R, FUSE_OFF
    arm = box(0.0, cx, cy - ARM_W / 2.0, cy + ARM_W / 2.0, cz0, cz1)
    clip = box(cx - CLIP_S / 2.0, cx + CLIP_S / 2.0, cy - CLIP_S / 2.0,
               cy + CLIP_S / 2.0, cz0, cz1)
    s = s.fuse(arm).fuse(clip)
    # bore aimed at the cap opening, throat opening to +x (= UP in the print pose)
    cm = (cz0 + cz1) / 2.0
    bore = cyl(FUSE_HOLE / 2.0, cm - 20.0, cm + 20.0, x=cx, y=cy)
    bore = bore.fuse(box(cx, cx + CLIP_S, cy - FUSE_SLIT / 2.0, cy + FUSE_SLIT / 2.0,
                         cm - 20.0, cm + 20.0))
    bore.rotate(Vector(cx, cy, cm), Vector(1, 0, 0), fuse_tilt())
    s = s.cut(bore)
    s = s.removeSplitter()
    assert len(s.Solids) == 1, "StopPost is %d solids" % len(s.Solids)
    return s.Solids[0]


def fuse_tilt():
    """Clip bore tilt (deg, about +x) so its axis meets the nozzle 5 mm inside the cap."""
    cm = CLIP_TOP - CLIP_H / 2.0
    return math.degrees(math.atan2(FUSE_OFF, zs(CAP_ST1) + 5.0 - cm))


def build_plate():
    s = cyl(PLATE_D / 2.0, HUB_COL_TOP, PLATE_TOP)
    return s.cut(cyl(PLATE_HOLE / 2.0, HUB_COL_TOP - 1, PLATE_TOP + 1))


def zs(st):
    return STOP_TOP + (LL_ST1 - st)


def rocket_envelope(theta=0.0, lean_dx=0.0):
    """Reference envelope of the aft rocket, rotated theta about the ROD axis.
    lean_dx shifts the cap/fins toward the rod (-x) to model the lug-slop lean."""
    bx = ROD_LINE_R
    z_cap, z_body0 = zs(CAP_ST1), zs(CAP_ST0)
    parts = {
        "cap": cyl(CAP_RIB_R, z_cap, z_body0, x=bx - lean_dx),
        "body": cyl(R_OD, z_body0, STOP_TOP + 60.0, x=bx - lean_dx * 0.5),
        "lug": cyl(LL_RO, STOP_TOP, STOP_TOP + (LL_ST1 - LL_ST0)).cut(
            cyl(LL_RI, STOP_TOP - 1, STOP_TOP + 40)),
        "web": box(LL_RI, bx - R_OD + 0.6, -LL_WEB / 2.0, LL_WEB / 2.0,
                   STOP_TOP, STOP_TOP + (LL_ST1 - LL_ST0)),
    }
    fins = None
    for a in FIN_ANG_PAD:
        f = box(R_OD - 0.5, FIN_TIP_R, -FIN_T / 2.0, FIN_T / 2.0, zs(FIN_ST_TE), zs(FIN_ST_LE))
        f = rot_z(f, a)
        f.translate(Vector(bx - lean_dx, 0, 0))
        fins = f if fins is None else fins.fuse(f)
    parts["fins"] = fins
    if theta:
        parts = {k: rot_z(v, theta) for k, v in parts.items()}
    return parts


# ========================================================================= run


def main():
    log = []

    def P(t=""):
        log.append(t)

    fails = []
    opens = []

    def verdict(ok, msg_ok, msg_bad, tag):
        if not ok:
            fails.append(tag)
        P("  %s" % (("PASS -- " + msg_ok) if ok else ("FAIL -- " + msg_bad)))

    P("PhoenixABS40-43 -- LAUNCH PAD %s   build report" % REV)
    P("=" * 78)
    P("v1 hub + legs unchanged; printed deflector replaced by a BOUGHT d%.0f x %.1f alu"
      % (PLATE_D, PLATE_T))
    P("plate; the rocket HANGS on its lug on a printed StopPost, which also holds the")
    P("fuse.  Frame: Z=0 ground, origin on the rod axis, body axis at x=+%.2f." % ROD_LINE_R)
    P("")

    doc = App.newDocument("PhoenixABS40-43_launchpad_%s" % REV)
    hub, leg = build_hub(), build_leg()
    post, plate = build_post(), build_plate()
    legs = [rot_z(leg, 120.0 * i) for i in range(LEG_N)]

    # ------------------------------------------------------------------- [1]
    P("[1] bodies")
    m_post = post.Volume * RHO
    m_plate = plate.Volume * RHO_AL
    pm = mesh_of(post)
    ok1 = pm.isSolid() and abs(pm.Volume - post.Volume) / post.Volume < 0.01 and post.isValid()
    bb = post.BoundBox
    P("  StopPost   %6.1f g ABS  bbox %5.1f x %5.1f x %5.1f  %s"
      % (m_post, bb.XLength, bb.YLength, bb.ZLength, "watertight" if ok1 else "NOT SOLID"))
    P("  BlastPlate %6.1f g alu  d%.0f x %.1f, one d%.1f hole  (BOUGHT -- STEP for reference)"
      % (m_plate, PLATE_D, PLATE_T, PLATE_HOLE))
    P("  PadHub / PadLeg: v1 parts, unchanged (v1 report [1]-[3] still apply)")
    verdict(ok1, "StopPost is a closed solid", "StopPost is not a closed solid", "1")

    # ------------------------------------------------------------------- [2]
    P("")
    P("[2] plate and post seating")
    proud = HUB_TOP - PLATE_TOP
    P("  plate d%.1f hole over the d%.1f spigot (%.2f radial), on the d%.0f column top Z %.0f"
      % (PLATE_HOLE, HUB_SPIG_D, (PLATE_HOLE - HUB_SPIG_D) / 2.0, V1["HUB_COL_D"], HUB_COL_TOP))
    P("  plate top Z %.1f; spigot %.1f mm proud -> post stands on the SPIGOT (Z %.0f),"
      % (PLATE_TOP, proud, HUB_TOP))
    P("  never on the plate, so the plate carries only its own weight and the jet.")
    seat = post.common(cyl(HUB_SPIG_D / 2.0, HUB_TOP - 0.5, HUB_TOP + 0.5)).Volume / 0.5
    P("  post footprint on the spigot top: %.0f mm2" % seat)
    verdict(proud > 0.5 and seat > 100.0, "post bears on the spigot, plate is captured under it",
            "spigot not proud of the plate / post footprint too small", "2")

    # ------------------------------------------------------------------- [3]
    P("")
    P("[3] assembly -- pad parts, every pair")
    asm = [("PadHub", hub), ("BlastPlate", plate), ("StopPost", post)] + \
          [("PadLeg_%d" % i, L) for i, L in enumerate(legs)]
    ok3 = True
    for i in range(len(asm)):
        for j in range(i + 1, len(asm)):
            (na, sa), (nb, sb) = asm[i], asm[j]
            v = sa.common(sb).Volume
            if v < 1e-3:
                continue
            designed = na == "PadHub" and nb.startswith("PadLeg")
            ok3 &= designed
            P("  %-11s x %-11s %8.1f mm3  %s" % (na, nb, v, "v1 tenon squeeze" if designed else "CLASH"))
    verdict(ok3, "only the v1 tenon squeeze overlaps", "unintended clash", "3")

    # ------------------------------------------------------------------- [4]
    P("")
    P("[4] the stop -- where the rocket hangs, and what the lug sits on")
    z_cap = zs(CAP_ST1)
    lug_face = cyl(LL_RO, STOP_TOP, STOP_TOP + 0.5).cut(cyl(LL_RI, STOP_TOP - 1, STOP_TOP + 1))
    lug_face = lug_face.fuse(box(LL_RI, ROD_LINE_R - R_OD + 0.6, -LL_WEB / 2.0, LL_WEB / 2.0,
                                 STOP_TOP, STOP_TOP + 0.5))
    a_lug = lug_face.Volume / 0.5
    top = post.common(cyl(40.0, STOP_TOP - 0.5, STOP_TOP))
    top.translate(Vector(0, 0, 0.5))
    a_bear = lug_face.common(top).Volume / 0.5
    W = M_ROCKET / 1000.0 * 9.81
    P("  StopPost top Z %.1f = lug aft end (station %.1f)" % (STOP_TOP, LL_ST1))
    P("  cap aft face Z %.1f -> %.0f mm above the plate top (nozzle standoff)"
      % (z_cap, z_cap - PLATE_TOP))
    P("  lug + web end face %.1f mm2, of which %.1f mm2 lands on the post (%.0f %%)"
      % (a_lug, a_bear, 100.0 * a_bear / a_lug))
    P("  rocket %.0f g = %.2f N -> %.2f MPa bearing; x5 for a dropped load: %.2f MPa"
      % (M_ROCKET, W, W / a_bear, 5 * W / a_bear))
    P("  (the groove side opens toward the body -- the web's root and the lug's")
    P("   body-side arc overhang the U; that is the cap-rib clearance, see [6])")
    verdict(a_bear > 5.0 and 5 * W / a_bear < 10.0, "lug lands on solid post top, stress trivial",
            "lug bearing area too small", "4")

    # ------------------------------------------------------------------- [5]
    P("")
    P("[5] lean on the lug slop -- where does the cap end up?")
    tilt = (2 * LL_RI - ROD_D) / (LL_ST1 - LL_ST0)
    shift = tilt * (CAP_ST1 - LL_ST1)
    P("  lug bore d%.1f on d%.1f over %.0f mm -> up to %.2f deg of lean" %
      (2 * LL_RI, ROD_D, LL_ST1 - LL_ST0, math.degrees(tilt)))
    P("  the CG is %.0f mm off the rod, so the rocket DOES lean: its foot swings toward"
      % ROD_LINE_R)
    P("  the rod by up to %.1f mm at the cap -- more than the %.1f mm rib-to-rod gap."
      % (shift, RIB_ROD_CLEAR))
    P("  So it leans until the cap ribs touch the ROD (normal force ~%.2f N, friction"
      % (W * ROD_LINE_R / (CAP_ST1 - LL_ST1)))
    P("  ~%.2f N along the rod -- negligible).  The post is cut back to CRADLE_R %.2f so"
      % (0.3 * W * ROD_LINE_R / (CAP_ST1 - LL_ST1), CRADLE_R))
    P("  the cap touches the rod, never the post: checked in [6] at full lean.")
    P("  NOTE for the airframe: this is a property of the D9aft lug, not of the pad.")

    # ------------------------------------------------------------------- [6]
    P("")
    P("[6] LOADING -- the rocket slides down the rod past the post")
    zr0, zr1 = z_cap, STOP_TOP + 0.01
    sweep_cap = cyl(CAP_RIB_R, zr0, zr1, x=ROD_LINE_R)
    sweep_lean = cyl(CAP_RIB_R, zr0, zr1, x=ROD_LINE_R - RIB_ROD_CLEAR)
    v_nom, v_lean = post.common(sweep_cap).Volume, post.common(sweep_lean).Volume
    dmin = CRADLE_R - CAP_RIB_R
    P("  cap ribs (r %.2f) swept Z %.0f..%.0f, upright:          %.3f mm3" % (CAP_RIB_R, zr0, zr1, v_nom))
    P("  same, leaning %.1f mm onto the rod (worst, [5]):        %.3f mm3" % (RIB_ROD_CLEAR, v_lean))
    P("  radial clearance cap ribs -> cradle, upright: %.2f mm" % dmin)
    env = rocket_envelope()
    fin_sweep = env["fins"].copy()
    fz = fin_sweep.BoundBox
    fin_col = None
    for a in FIN_ANG_PAD:
        f = box(R_OD - 0.5, FIN_TIP_R, -FIN_T / 2.0, FIN_T / 2.0, fz.ZMin, STOP_TOP + 1)
        f = rot_z(f, a)
        f.translate(Vector(ROD_LINE_R, 0, 0))
        fin_col = f if fin_col is None else fin_col.fuse(f)
    v_fin = post.common(fin_col).Volume
    P("  fins swept from rest up past the post top:             %.3f mm3" % v_fin)
    verdict(v_nom < 1e-3 and v_lean < 1e-3 and v_fin < 1e-3,
            "the rocket loads past the post, even leaning", "something hits the post on the way down", "6")

    # ------------------------------------------------------------------- [7]
    P("")
    P("[7] ROTATION KEY -- swing the rocket about the rod until it hits the post")
    others = [("plate", plate), ("hub", hub)]

    def first_hit(sign):
        for k in range(0, 61):
            th = sign * 0.5 * k
            e = rocket_envelope(th)
            for n, s in e.items():
                v = s.common(post).Volume
                if v > 0.01:
                    return th, n
        return None, None

    hits = [first_hit(+1), first_hit(-1)]
    e0 = rocket_envelope(0.0)
    v0 = sum(s.common(post).Volume for s in e0.values())
    v0o = sum(s.common(o).Volume for s in e0.values() for _, o in others)
    P("  at rest (0 deg): rocket vs post %.3f mm3, vs plate/hub %.3f mm3" % (v0, v0o))
    ok7 = v0 < 0.01 and v0o < 0.01
    for th, n in hits:
        if th is None:
            P("  no contact out to 30 deg -- NOT KEYED")
            ok7 = False
        else:
            P("  %+5.1f deg: first contact is the %s against the post" % (th, n))
            ok7 &= n in ("cap", "body")
    th_key = max(abs(h[0]) for h in hits if h[0] is not None) if all(h[0] is not None for h in hits) else 30.0
    drift = ROD_LINE_R * math.radians(th_key)
    P("  -> rocket keyed to +-%.1f deg; nozzle wanders <= %.1f mm (cap hole r %.1f)"
      % (th_key, drift, CAP_HOLE_R))
    verdict(ok7 and drift < CAP_HOLE_R,
            "keyed by cap/body on the horns; fins never touch the post",
            "rotation not keyed, or a fin is what stops it", "7")

    # ------------------------------------------------------------------- [8]
    P("")
    P("[8] FUSE CLIP")
    rise = z_cap - CLIP_TOP
    bend = fuse_tilt()
    cm = CLIP_TOP - CLIP_H / 2.0
    t = math.radians(bend)
    y_at_cap = FUSE_OFF - (z_cap - cm) * math.tan(t)
    P("  clip: d%.1f bore (Klima fuse d%.1f), snap-in throat %.1f opening outward, %.0f mm tall"
      % (FUSE_HOLE, FUSE_D, FUSE_SLIT, CLIP_H))
    P("  clip %.0f mm off the nozzle axis; bore TILTED %.1f deg so the fuse, pushed straight"
      % (FUSE_OFF, bend))
    P("  up through it, crosses the cap face %.1f mm off the nozzle axis (opening r %.1f)"
      % (abs(y_at_cap), CAP_HOLE_R))
    P("  and is 5 mm inside the cap on the axis.  Clip top Z %.0f, cap face Z %.0f."
      % (CLIP_TOP, z_cap))
    near = FUSE_OFF - CLIP_S / 2.0
    P("  with the +-%.1f deg key the fuse still lands %.1f mm inside the opening edge"
      % (th_key, CAP_HOLE_R - abs(y_at_cap) - drift))
    P("  nearest clip/arm material to the nozzle axis: %.1f mm (jet core r %.1f)."
      % (near, CAP_HOLE_R))
    P("  It is ABS in the plume's edge for the ~0.2 s before the rocket clears:")
    P("  expect soot and some surface melt -- inspect each flight, reprint if soft.")
    clip_ok = rise > 15.0 and abs(y_at_cap) + drift < CAP_HOLE_R and near > CAP_HOLE_R + 1.0
    verdict(clip_ok, "fuse reaches the nozzle, clip outside the jet core",
            "fuse geometry out of range", "8")

    # ------------------------------------------------------------------- [9]
    P("")
    P("[9] blast plate coverage")
    cov = PLATE_D / 2.0 - ROD_LINE_R
    P("  nozzle at r %.2f from the rod -> %.1f mm of plate on the near-edge side,"
      % (ROD_LINE_R, cov))
    P("  at ANY rotation (plate is round and centred on the rod).  Jet lands on alu,")
    P("  %.0f mm below the nozzle, beyond the d%.0f column (plate overhang there %.1f mm)."
      % (NOZZLE_STANDOFF, V1["HUB_COL_D"], ROD_LINE_R - V1["HUB_COL_D"] / 2.0))
    P("  No vent holes: the plate is open all round, gas leaves sideways.")
    verdict(cov > 40.0, "> 40 mm of plate round the nozzle", "plate too small", "9")

    # ------------------------------------------------------------------ [10]
    P("")
    P("[10] GUIDED ROD LENGTH (v1 [6] convention: lug FULLY off the rod)")
    lug_top = STOP_TOP + (LL_ST1 - LL_ST0)
    P("  lug Z %.1f..%.1f at rest" % (STOP_TOP, lug_top))
    for L in (ROD_L_ASSUMED, 1300.0, ROD_L_WANTED, 1500.0):
        tr = L - lug_top
        P("  rod %6.0f mm -> guided %6.0f mm   light >=%.0f %s   payload >=%.0f %s"
          % (L, tr, RAIL_MIN, "ok" if tr >= RAIL_MIN else "SHORT",
             RAIL_MIN_PAYLOAD, "ok" if tr >= RAIL_MIN_PAYLOAD else "SHORT"))
    P("  BUY >= %.0f mm of rod (light) / >= %.0f mm (payload)."
      % (RAIL_MIN + lug_top, RAIL_MIN_PAYLOAD + lug_top))
    P("  OPEN -- the 274 g D9aft with its e-bay is closer to the PAYLOAD line than the")
    P("  light one.  Set the .ork rail length to the guided figure for the rod you buy")
    P("  and read rail-exit speed (>= 15 m/s, DESIGN 4.4) before calling it.")
    opens.append("10")

    # ------------------------------------------------------------------ [11]
    P("")
    P("[11] TIP-OVER (v1 [5] method, v2 masses)")
    m_hub, m_leg = hub.Volume * RHO, leg.Volume * RHO
    m_rod = ROD_L_WANTED * ROD_RHO_LIN * 1000.0
    z_tip = zs(TIP_ST)
    cg_z = z_tip - CG_FROM_TIP
    items = [(m_hub, HUB_BASE_H / 2.0), (LEG_N * m_leg, LEG_H_HUB / 3.0),
             (m_plate, HUB_COL_TOP), (m_post, post.CenterOfMass.z),
             (m_rod, ROD_L_WANTED / 2.0), (M_ROCKET, cg_z)]
    M = sum(m for m, _ in items)
    Wt = M / 1000.0 * 9.81
    lever = LEG_REACH * math.cos(math.radians(180.0 / LEG_N))
    L_rocket = CAP_ST1 - TIP_ST
    a_body = 2 * R_OD / 1000.0 * L_rocket / 1000.0
    a_fins = 1.5 * FIN_AREA_EA / 1e6
    a_rod = ROD_D / 1000.0 * ROD_L_WANTED / 1000.0
    off_mo = M_ROCKET / 1000.0 * 9.81 * ROD_LINE_R

    def over(v):
        mo = wind_force(a_body, v) * cg_z + wind_force(a_fins, v) * (z_cap + 30.0)
        mo += wind_force(a_rod, v) * (ROD_L_WANTED / 2.0)
        return mo + off_mo        # rocket offset booked as overturning (v1 [5] note)

    P("  rocket tip Z %.0f, CG Z %.0f; system %.0f g; tip line %.0f mm" % (z_tip, cg_z, M, lever))
    for v, tag in ((WIND_CALM, "calm"), (WIND_LIMIT, "LIMIT")):
        for bal, bt in ((0.0, "bare"), (BALLAST_KG, "%.1f kg tie-down" % BALLAST_KG)):
            res = (Wt + bal * 9.81) * lever
            P("  %5.1f m/s %-5s %-17s restoring %5.0f / overturning %5.0f = %.2f x"
              % (v, tag, bt, res, over(v), res / over(v)))
    vmax = math.sqrt(max(0.0, (Wt * lever - off_mo) / (over(1.0) - off_mo)))
    P("  bare pad tips at %.1f m/s." % vmax)
    P("  FAIL at the %.0f m/s limit is REAL and deliberate, as in v1: PEG THE FEET" % WIND_LIMIT)
    P("  (d%.1f holes) and/or hang %.0f kg on the d%.0f tie-down.  Staking is primary."
      % (PEG_D, BALLAST_KG, TIE_D))
    if vmax < WIND_LIMIT:
        fails.append("11 (bare pad, deliberate: stake it)")

    # ------------------------------------------------------------------ [12]
    P("")
    P("[12] printability")
    P("  StopPost prints LYING ON ITS FLAT BACK (the -x face): the U-channel opens")
    P("  upward, the rod bore and fuse hole run horizontal (d4.2 / d%.1f bridges)," % FUSE_HOLE)
    P("  the arm rises as a %.0f x %.0f tower.  No supports." % (ARM_W, CLIP_H))
    P("  Bed footprint %.0f x %.0f, %.0f tall.  Ream the bore with a 4 mm bit."
      % (bb.ZLength, bb.YLength, bb.XLength))
    # overhang audit IN THE PRINT POSE: up = post +x, so a face is a ceiling
    # when its normal points -x more than 45 deg, and it is above the bed
    vs, tris = post.tessellate(0.05)
    cm = CLIP_TOP - CLIP_H / 2.0
    t = math.radians(fuse_tilt())
    ax = Vector(0, -math.sin(t), math.cos(t))
    over_a, bores_a, where = 0.0, 0.0, []
    for i, j, k in tris:
        a, b, c = vs[i], vs[j], vs[k]
        n = (b - a).cross(c - a)
        area = n.Length / 2.0
        if area < 1e-9:
            continue
        n.normalize()
        g = (a + b + c) * (1.0 / 3.0)
        if n.x > -0.707 or g.x < -POST_BACK + 0.2:
            continue
        d_rod = math.hypot(g.x, g.y)
        w = g - Vector(ROD_LINE_R, FUSE_OFF, cm)
        d_fuse = (w - ax * w.dot(ax)).Length
        if d_rod < POST_BORE / 2.0 + 0.1 or d_fuse < FUSE_HOLE / 2.0 + 0.1:
            bores_a += area                         # small horizontal bores: bridge
        else:
            over_a += area
            where.append(g)
    P("  overhang audit (print pose, >45 deg ceilings above the bed):")
    P("    small horizontal bores (d%.1f rod, d%.1f fuse): %.1f mm2 -- bridge, fine"
      % (POST_BORE, FUSE_HOLE, bores_a))
    P("    anything else: %.2f mm2%s" % (over_a, "" if over_a < 0.5 else "  at e.g. %s" % where[:3]))
    # rod groove lips: thickness between groove and cradle
    lip_ok_deg = math.degrees(math.acos(min(1.0, (ROD_LINE_R ** 2 + GROOVE_R ** 2
                                                  - (CRADLE_R + 0.8) ** 2) / (2 * ROD_LINE_R * GROOVE_R))))
    P("  rod groove: lips >= 0.8 mm from %.0f deg off the body side -> wraps %.0f deg;"
      % (lip_ok_deg, 360 - 2 * lip_ok_deg))
    P("    the opening chord %.2f vs the d%.1f rod: a locating GROOVE, not a snap."
      % (2 * GROOVE_R * math.sin(math.radians(lip_ok_deg)), ROD_D))
    drift_top = (POST_BORE - ROD_D) / BASE_H * (STOP_TOP - POST_Z0 - BASE_H / 2.0)
    shifted = top.copy()
    shifted.translate(Vector(-drift_top, 0, 0))
    a_drift = lug_face.common(shifted).Volume / 0.5
    P("  the top is located by the %.0f mm base bore only: it can lean %.1f mm off the"
      % (BASE_H, drift_top))
    P("    rod; the lug then still lands on %.1f mm2 of post (vs %.1f upright)." % (a_drift, a_bear))
    if over_a >= 0.5 or a_drift < 5.0:
        fails.append("12")
        P("  FAIL -- overhang or lug bearing out of range")
    else:
        P("  PASS -- no supports needed, lug still bears with the top leaning")
    P("  Fuse throat %.1f is a SNAP: if the fuse won't go in, open it with a knife;" % FUSE_SLIT)
    P("  if it falls out, tape it.")

    # ------------------------------------------------------------------ [13]
    P("")
    P("[13] non-vacuity")
    feats = [
        ("post cradle", box(-POST_BACK, ROD_LINE_R, -POST_HALF_W, POST_HALF_W, POST_Z0 + BASE_H,
                            STOP_TOP).common(cyl(CRADLE_R, POST_Z0, STOP_TOP, x=ROD_LINE_R)).Volume),
        ("post bore", math.pi * (POST_BORE / 2.0) ** 2 * BASE_H),
        ("rod groove", math.pi * GROOVE_R ** 2 * (STOP_TOP - POST_Z0 - BASE_H) * 0.5),
        ("fuse hole", math.pi * (FUSE_HOLE / 2.0) ** 2 * CLIP_H),
        ("plate hole", math.pi * (PLATE_HOLE / 2.0) ** 2 * PLATE_T),
    ]
    probes = [("post solid behind the rod", post.isInside(Vector(-5, 0, STOP_TOP - 50), 0.01, True), True),
              ("cradle empty in front of rod", post.isInside(Vector(4, 0, STOP_TOP - 50), 0.01, True), False),
              ("rod bore open", post.isInside(Vector(0, 0, POST_Z0 + 5), 0.01, True), False),
              ("fuse hole open", post.isInside(Vector(ROD_LINE_R, FUSE_OFF, CLIP_TOP - CLIP_H / 2.0), 0.01, True), False),
              ("clip present", post.isInside(Vector(ROD_LINE_R + 3, FUSE_OFF - 3, CLIP_TOP - 2), 0.01, True), True)]
    ok13 = True
    for n, v in feats:
        P("  %-28s %9.1f mm3  %s" % (n, v, "ok" if v > 1.0 else "VACUOUS"))
        ok13 &= v > 1.0
    for n, got, want in probes:
        P("  probe %-28s %s" % (n, "ok" if got == want else "WRONG"))
        ok13 &= got == want
    verdict(ok13, "every feature is really there", "a feature is missing", "13")

    # ------------------------------------------------------------------ [14]
    P("")
    P("[14] export")
    for n, s in (("StopPost", post), ("BlastPlate", plate)):
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        stem = "PhoenixABS40-43_%s_%s" % (n, REV)
        s.exportStep(os.path.join(MODELS, stem + ".step"))
        if n == "StopPost":
            mesh_of(s).write(os.path.join(MODELS, stem + ".stl"))
        P("  %-10s -> Models/%s.step%s" % (n, stem, " + .stl" if n == "StopPost" else "  (bought)"))
    for n, s in [("PadHub", hub)] + [("PadLeg_%d" % i, L) for i, L in enumerate(legs)]:
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
    asm_shapes = [hub, plate, post] + legs
    full = mesh_of(asm_shapes[0])
    for s in asm_shapes[1:]:
        full.addMesh(mesh_of(s))
    ap = os.path.join(MODELS, "PhoenixABS40-43_launchpad_ASSEMBLY_%s.stl" % REV)
    full.write(ap)
    P("  assembly -> Models/%s" % os.path.basename(ap))
    ref = dict(("Ref_" + k, v) for k, v in rocket_envelope().items())
    ref["Ref_Rod"] = cyl(ROD_D / 2.0, 0.0, ROD_L_WANTED)
    for n, s in ref.items():
        o = doc.addObject("Part::Feature", n)
        o.Shape = s
        o.Visibility = False
    doc.recompute()
    doc.saveAs(os.path.join(MODELS, "PhoenixABS40-43_launchpad_%s.FCStd" % REV))
    P("  FCStd -> Models/PhoenixABS40-43_launchpad_%s.FCStd (rocket envelope hidden)" % REV)

    for d in (PRINTS, RTP):
        if not os.path.isdir(d):
            os.makedirs(d)
    mesh_of(post).write(os.path.join(PRINTS, "PhoenixABS40-43_StopPost_%s.stl" % REV))
    po = post.copy()
    po.rotate(Vector(0, 0, 0), Vector(0, 1, 0), -90.0)      # -x back face -> bed (z' = x)
    pb = po.BoundBox
    po.translate(Vector(-pb.XMin, -pb.YMin, -pb.ZMin))
    pb = po.BoundBox
    mesh_of(po).write(os.path.join(RTP, "PhoenixABS40-43_StopPost_%s.stl" % REV))
    back_down = po.common(box(pb.XMin - 1, pb.XMax + 1, pb.YMin - 1, pb.YMax + 1, -1, 0.2)).Volume
    P("  print pose: bed %.0f x %.0f, %.0f tall; first-layer contact %.0f mm2"
      % (pb.XLength, pb.YLength, pb.ZLength, back_down / 0.2))
    P("  -> Print Files/Launch Pad/(Ready to Print/)PhoenixABS40-43_StopPost_%s.stl" % REV)
    if pb.XLength > 250 or pb.YLength > 250 or pb.ZLength > 250:
        fails.append("14")
        P("  FAIL -- does not fit the X1C bed")

    # PadLeg: v1 geometry, CORRECTED print pose.  v1 [14] rotates -90 about X, which puts
    # the one-sided foot widening (y up to FOOT_Y1) on the bed and floats the whole blade
    # FOOT_Y1 - LEG_W/2 = 8 mm in the air (Bambu: "floating cantilever").  +90 puts the
    # flat y0 = -LEG_W/2 face down, as v1's own comments intend.
    # Laid flat, the tenon's split slot is a horizontal 1.6 mm gap open at the tip, so the
    # upper cheek is a 12 mm floating cantilever (Bambu warning).  Close the slot at the tip
    # with a thin web: the cheek then prints as a bridge; CUT THE WEB after printing.
    r_in = HUB_BASE_D / 2.0 - V1["MORT_DEPTH"]
    web = box(r_in, r_in + LEG_END_WEB, -V1["TEN_SLOT_W"] / 2.0 - 0.01, V1["TEN_SLOT_W"] / 2.0 + 0.01,
              0.0, V1["MORT_H"] - V1["TEN_CLEAR_H"])
    leg_print = leg.fuse(web).removeSplitter()
    assert len(leg_print.Solids) == 1
    lo = leg_print.Solids[0].copy()
    lo.rotate(Vector(0, 0, 0), Vector(1, 0, 0), 90.0)
    lb = lo.BoundBox
    lo.translate(Vector(-lb.XMin, -lb.YMin, -lb.ZMin))
    lb = lo.BoundBox
    blade = lo.common(box(lb.XMin + 30.0, lb.XMin + 120.0, lb.YMin - 1, lb.YMax + 1, -1, 0.2))
    blade_a = blade.Volume / 0.2
    xs = lb.XMin + 30.0
    sec = lo.common(box(xs, xs + 0.5, lb.YMin - 1, lb.YMax + 1, -1, lb.ZMax + 1)).BoundBox
    P("  PadLeg (v1 geometry, pose FIXED): bed %.0f x %.0f, %.1f tall; blade on the bed"
      % (lb.XLength, lb.YLength, lb.ZLength))
    P("    over x 30..120: %.0f mm2 of first layer (blade section starts at z %.2f)"
      % (blade_a, sec.ZMin))
    # overhang audit in the print pose (+z up): ceilings steeper than 45 deg above the bed,
    # bridges (both ends anchored, <= 13 mm) listed separately from true floating faces
    vs, tris = lo.tessellate(0.05)
    ceil = []
    for i, j, k in tris:
        a, b, c = vs[i], vs[j], vs[k]
        n = (b - a).cross(c - a)
        area = n.Length / 2.0
        if area < 1e-9:
            continue
        n.normalize()
        g = (a + b + c) * (1.0 / 3.0)
        if n.z < -0.707 and g.z > 0.2:
            ceil.append((g, area))
    peg_x = V1["PEG_S"] - r_in
    slot_lo, slot_hi = LEG_END_WEB, V1["TEN_SLOT_L"] + 1.0
    a_peg = sum(a for g, a in ceil if abs(g.x - peg_x) < V1["PEG_D"] / 2.0 + 0.2)
    a_slot = sum(a for g, a in ceil if slot_lo - 0.1 <= g.x <= slot_hi + 0.1 and g.z < lb.ZMax - 0.1)
    a_other = sum(a for g, a in ceil) - a_peg - a_slot
    P("    overhang audit: d%.1f peg-hole roof %.0f mm2 (bridge), tenon-slot roof %.0f mm2"
      % (V1["PEG_D"], a_peg, a_slot))
    P("    (a %.0f mm bridge, web at the tip), anything else %.2f mm2"
      % (V1["TEN_SLOT_L"] + r_in - r_in - LEG_END_WEB + 1.0, a_other))
    P("    AFTER PRINTING: cut the %.1f mm web at the tenon tip (knife / razor saw) so the"
      % LEG_END_WEB)
    P("    two cheeks can flex -- the v1 [3] interference fit needs them free.")
    if a_other > 0.5:
        fails.append("14 leg overhang")
        P("  FAIL -- leg has an unsupported ceiling")
    mesh_of(lo).write(os.path.join(RTP, "PhoenixABS40-43_PadLeg_%s.stl" % REV))
    P("  -> Ready to Print/PhoenixABS40-43_PadLeg_%s.stl  (DO NOT print PadLeg_v1.stl: blade floats)" % REV)
    if sec.ZMin > 0.01 or blade_a < 500.0:
        fails.append("14 leg pose")
        P("  FAIL -- the leg blade is not on the bed")

    # ------------------------------------------------------------------- sum
    P("")
    P("SUMMARY")
    P("  * Print: StopPost v2 (new), PadHub v1 STL, 3 x PadLeg_v2.stl (v1 leg, pose fixed,")
    P("    0.6 mm print web closing the tenon slot -- CUT IT before assembly).")
    P("  * Buy: alu disc d%.0f x %.1f, drill ONE d%.1f centre hole (step bit)."
      % (PLATE_D, PLATE_T, PLATE_HOLE))
    P("  * Assemble: legs into hub, plate over the spigot, StopPost over the ROD's")
    P("    bottom end, rod down the hub bore to the ground, post sitting on the spigot.")
    P("  * Load: turn the post so the fuse arm points the way the body will hang, slide")
    P("    the rocket down until the lug sits on the post top (Z %.0f).  Snap the fuse" % STOP_TOP)
    P("    sideways into the clip's throat and slide it up the tilted bore, through the")
    P("    cap opening, into the motor core.")
    P("  * Rocket keyed to +-%.1f deg; nozzle %.0f mm above the plate." % (th_key, z_cap - PLATE_TOP))
    P("  * Rod: >= %.0f mm (light) / >= %.0f mm (payload rule) -- OPEN until the .ork"
      % (RAIL_MIN + lug_top, RAIL_MIN_PAYLOAD + lug_top))
    P("    gives rail-exit speed at that length ([10]).")
    P("  * FAIL [11]: bare pad tips at %.1f m/s -- peg the feet / ballast the hub." % vmax)
    P("  * Fuse: Klima d%.1f, %.0f-%.0f s/m -> cut %.0f mm for ~30 s to walk away"
      % (FUSE_D, FUSE_BURN[0], FUSE_BURN[1], 30.0 / FUSE_BURN[0] * 1000.0))
    P("    (30 s at the fast end), plus what goes into the motor and through the clip.")
    P("  * ASSUMED: plate %.1f mm.  UNPRINTED and UNFLOWN." % PLATE_T)
    P("  RESULT %s: %s%s" % (REV, "ALL PASS" if not fails else "FAIL " + ", ".join(fails),
                           ("; OPEN " + ", ".join(opens)) if opens else ""))

    rpt = "\n".join(log)
    print(rpt)
    with open(os.path.join(MODELS, "launchpad_build_report_%s.txt" % REV), "w", encoding="utf-8") as fh:
        fh.write(rpt + "\n")


main()

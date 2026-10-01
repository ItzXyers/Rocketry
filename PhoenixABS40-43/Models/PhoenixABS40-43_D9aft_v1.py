# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v1: AFT DEPLOYMENT ON THE KLIMA D9-5 MOTOR EJECTION CHARGE.

The only deployment event is the motor's own ejection charge. It fires forward through a port in
the fin-can thrust ring into the chute bay, shears two printed ABS pins, and pushes the fin can
(with the spent motor) off the aft end. The canopy comes out of the open aft end of the body on a
harness tied between the fin can and the airframe. The nose never separates.

  station (mm from the nose base / top of the body tube)
   -65 ..   0  nose v5 Von Karman (unchanged part) -- now RETAINED: 3 x M5 x 8 button heads at
               station 8, self-tapped into the nose's existing d4.2 detent pilots
     0 ..  42  nose shoulder
    45 .. 110  e-bay: sled v1 (unchanged) on a new sled mount (lugs reach the bare 40 bore),
               3 x M3 CSK at station 50; static + sound ports. Logging only -- it fires nothing.
   115         bonded joint fwd_tube / aft_tube (never opened)
   115 .. 131  fwd_tube spigot, closed by a SOLID gas-tight bulkhead at 128.5 .. 131
   131 .. 281  CHUTE BAY: harness lug on the wall (station 132-150), canopy, Nomex. No holes in
               the wall except the 2 shear-pin slots (and the lug/launch lug are outside/inside).
   248.6..288.6 fin-can coupler inside the aft tube: SLIP FIT, NOT BONDED -- this is the separation
   276.6       2 x printed shear pins (60 / 180 deg, both in fin gaps; uneven -> one clocking)
   281.1       fin-can thrust ring, d14 gas port on the axis; harness lug beside the port
   288.6 .. 340  fin can (v1 cfg C geometry, fins printed in), motor D9 18 x 70, cap v1 (unchanged)

Reused read-only (never modified, never re-exported):
  Models/PhoenixABS40-43_AftFinCan_v1.step        base of the new fin can (the verified threaded part)
  Models/PhoenixABS40-43_aft_retention_v1.py      exec'd (no main()) ONLY to build a thread-free proxy
  Models/PhoenixABS40-43_MotorRetainerCap_v1.step cap, unchanged
  Nosecone/Models/PhoenixABS40-43_nose_VonKarman_v5.step
  Avionics/PhoenixABS40-43_avbay_sled_v1.py        exec'd (no main()) for the sled + component envelopes

Threaded parts: AFT_RETENTION_DESIGN 8 -- OCCT booleans against the faceted thread are not
trustworthy. So every interference / fit check below runs against FINCAN_PROXY (same part, plain
boss), and every feature cut into the REAL fin can is proven by isInside probes on the real part.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"

Frame: z = 340 - station (+Z toward the nose); z = 0 is the fin-can aft face, so the fin-can
frame Zf of AFT_RETENTION_DESIGN is used as-is. Any FAIL line in the report means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, MeshPart

V = App.Vector
t0 = time.time()
PHX = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43"
MODELS = os.path.join(PHX, "Models")
PRINT_RAW = os.path.join(PHX, "Print Files", "Aft Deploy D9")
PRINT_READY = os.path.join(PRINT_RAW, "Ready to Print")
NAME = "PhoenixABS40-43_D9aft_v1"
REV = "D9aft_v1"
FINCAN_STEP = os.path.join(MODELS, "PhoenixABS40-43_AftFinCan_v1.step")
CAP_STEP = os.path.join(MODELS, "PhoenixABS40-43_MotorRetainerCap_v1.step")
AR_SRC = os.path.join(MODELS, "PhoenixABS40-43_aft_retention_v1.py")
NOSE_STEP = os.path.join(PHX, "Nosecone", "Models", "PhoenixABS40-43_nose_VonKarman_v5.step")
SLED_SRC = os.path.join(PHX, "Avionics", "PhoenixABS40-43_avbay_sled_v1.py")
RHO = dict(ABS=1.05e-3, steel=7.85e-3)          # g/mm3 -- every printed part is ABS
BED = (256.0, 256.0, 250.0)                      # Bambu X1C

# =====================================================================================
# PARAMETERS
# =====================================================================================
BODY_LEN = 340.0                  # nose base -> fin-can aft face (kept: the length does stability work)
def zs(st): return BODY_LEN - st
def station(z): return BODY_LEN - z
R_OD, R_ID = 21.5, 20.0
EF = 0.5                          # 45 deg bed-side / lead-in chamfers

# --- nose retention (nose v5 part unchanged: its 3 detent pilots d4.2 x 10 at station 8)
NOSE_LEN = 65.0
NOSE_SH_END = 42.0
NOSE_SCREW_ST = 8.0
NOSE_SCREW_CLR_D = 5.3            # M5 clearance in the tube wall
M5_DK, M5_K = 9.5, 2.75           # ISO 7380 button head
M5_LEN = 8.0

# --- e-bay: sled v1 + a new mount, stacked straight behind the nose
SLED_Z = 230.7                    # z = Zs + SLED_Z  (disc top at station 59; sled Zs 45.4 -> -0.9)
DISC_R = 19.3
DISC_ZS0, DISC_ZS1 = 45.4, 50.3
LUG_W, LUG_RI = 7.0, 13.0
LUG_RO = 19.75                    # T5's lugs stopped at 17.6 inside a spigot; here they reach the 40 bore
LUG_TOP_ST = 45.0                 # 3 mm behind the nose shoulder
EBAY_SCREW_ST = 50.0
EBAY_ANG = (90.0, 225.0, 330.0)   # uneven -> one clocking
LEAD_HOLE_R = 6.0
CSK_DK, CSK_K_CYL, CSK_CONE = 6.0, 0.2, 1.5
M3_LEN = 8.0
STATIC_PORT = dict(d=1.5, zs=30.0, ang=0.0)       # sled frame Zs; e-bay only -- sealed from the chute bay
SOUND_PORT_D = 3.0

# --- body split (both prints <= 250 mm tall)
J = 115.0                         # fwd_tube / aft_tube outer joint (bonded, never opened)
SPIGOT_LEN = 16.0
SPIGOT_RO, SPIGOT_RI = 19.85, 18.5   # 0.3 mm diametral epoxy gap in the aft tube's 40 bore
BH_T = 2.5                        # gas-tight bulkhead closing the spigot (prints flat on the bed)
J_RING = 3.0                      # full-thickness ring tying the tube wall to the spigot
ST_BH_AFT = J + SPIGOT_LEN        # 131: chute-bay forward wall

# --- fin can (Zf frame of AFT_RETENTION_DESIGN 4A)
SHOULDER_Z = 51.4                 # body aft end lands here (station 288.6)
ST_BODY_AFT = BODY_LEN - SHOULDER_Z
BH_Z0, BH_Z1 = 55.9, 58.9         # thrust ring: motor forward face .. forward face
PORT_R = 7.0                      # d14 gas port
LEDGE_R = 8.2                     # 1.0 mm flat bearing ledge for the casing rim, then 45 deg to PORT_R
CPL_R_O = 19.80                   # coupler OD: 0.40 mm diametral slip in the 40 bore -- NOT bonded
CPL_R_I = 18.50
CPL_LEN = 40.0                    # engagement shoulder -> coupler front (~0.93 cal)
CPL_Z1 = SHOULDER_Z + CPL_LEN     # 91.4 (station 248.6)
CPL_CHAMFER = 0.8

# --- shear pins: printed ABS, laid flat, 2D profile x (radially in from the OD) / y (tangential) / z (axial)
PIN_N = 2
PIN_ANG = (60.0, 180.0)           # fin gaps (fins at 0/120/240); uneven -> the fin can goes on one way only
PIN_ST = 276.6                    # 12 mm forward of the body's aft edge (Zf 63.4)
PIN_A = 0.8                       # axial = print thickness (4 layers at 0.20)
PIN_B = 2.4                       # tangential body width
PIN_BN = 0.6                      # NECK width at the shear plane (nominal; card carries 0.5/0.6/0.8/1.0)
PIN_BN_CARD = (0.5, 0.6, 0.8, 1.0)
PIN_NOTCH_DEG = 60.0              # included angle of the two V-notches
PIN_L = R_OD - CPL_R_I            # 3.0: OD of the tube -> ID of the coupler (flush both sides)
PIN_X_NECK = R_OD - (R_ID + CPL_R_O) / 2      # 1.6: middle of the 0.2 mm radial slip gap
PIN_HEAD_T, PIN_HEAD_B = 0.6, 4.0 # outside the OD: stops the pin falling into the bay; tape over it
SLOT_CLR = 0.2                    # slot = pin + 0.2 in both directions (print-tolerance sensitive)
TAU_ABS = 25.0                    # MPa, ASSUMED in-plane shear of printed ABS -> calibrate with the coupon
TAU_ABS_LAYER = 10.0              # MPa, assumed interlayer (for anchors)

# --- harness anchors: wall-attached lugs, hole axis tangential
ANCH_W = 6.0                      # tangential thickness
ANCH_R_IN = 12.5
ANCH_HOLE_D = 3.5
ANCH_HOLE_R = 15.5
ANCH_FC = dict(ang=300.0, z0=BH_Z1, z1=BH_Z1 + 10.0, zh=BH_Z1 + 5.6)   # on the fin-can thrust ring
ANCH_AT = dict(ang=0.0, st0=ST_BH_AFT + 1.0, st_h=ST_BH_AFT + 14.5, st1=ST_BH_AFT + 18.8)  # aft tube
SNATCH_N = 250.0                  # project placeholder (T5 README / nose v5 anchor)

# --- launch lug (the .ork carries one; no CAD had it). Pad rod is d4.0 steel (launchpad report [9])
LL_ANG = 300.0
LL_ST0, LL_ST1 = 152.5, 187.5     # 35 mm, centred on station 170 (.ork: body middle)
LL_RO, LL_RI = 3.5, 2.2           # bore d4.4 on the d4.0 rod (launchpad report [9] asks for d4.4)
ROD_R = 2.0
LL_RIB_CLEAR = 1.0                # rod line must clear the cap v1 grip ribs (r 22.75, any clocking) by this
LL_WEB = 4.0                      # web tying the stood-off lug to the tube

# --- motor: Klima D9 (OpenRocket DB: 18 x 70, 27.1 g loaded, 11.0 g spent, 19.96 Ns, 25 N peak, delays 0/3/5/7)
MOTOR_ZF = (-14.1, 55.9)
MOTOR_R = 9.0
MOTOR_LOADED, MOTOR_SPENT = 27.1, 11.0
MOTOR_PEAK_N = 25.0
MOTOR_BORE_R = 9.2                # fin-can bore d18.4

# --- recovery point masses (DESIGN 7.7)
CANOPY_G, CANOPY_ST = 16.0, 170.0  # d500 canopy + Kevlar leader + shock cord, packed forward in the bay
NOMEX_G, NOMEX_ST = 4.0, 245.0     # Nomex blanket / wadding between the port and the canopy

# =====================================================================================
# HELPERS
# =====================================================================================
def revolve(pts):
    vs = [V(r, 0, z) for r, z in pts]
    return Part.Face(Part.Wire(Part.makePolygon(vs + [vs[0]]))).revolve(V(0, 0, 0), V(0, 0, 1), 360)
def rst(pairs): return revolve([(r, zs(s)) for r, s in pairs])
def cyl(r, z0, z1, x=0.0, y=0.0): return Part.makeCylinder(r, z1 - z0, V(x, y, z0))
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def rot(shape, ang):
    s = shape.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), ang); return s
def radial_cyl(r, x0, x1, z, ang): return rot(Part.makeCylinder(r, x1 - x0, V(x0, 0, z), V(1, 0, 0)), ang)
def radial_cone(r0, r1, x0, x1, z, ang): return rot(Part.makeCone(r0, r1, x1 - x0, V(x0, 0, z), V(1, 0, 0)), ang)
def pol(r, ang, z): a = math.radians(ang); return V(r * math.cos(a), r * math.sin(a), z)
def inside(shape, p): return shape.isInside(p, 1e-4, True)

report = []
def rep(s=""): print(s); report.append(s)
def ok(c): return "PASS" if c else "FAIL"

# ---------------- reused geometry
_ss = open(SLED_SRC, encoding="utf-8").read()
SL = {"__name__": "sledlib"}
exec(_ss[:_ss.rstrip().rfind("main()")], SL)
_sled_s, _ = SL['build_sled']([])
sled = _sled_s.translated(V(0, 0, SLED_Z))
ENV = {n: f().translated(V(0, 0, SLED_Z)) for n, f in SL['COMPONENTS'] if n != 'Servo_SG90'}   # no servo: nothing to release
ENV['ADXL375'] = ENV['ADXL375'].common(box(-30, 30, -30, 30, -500, SL['ADXL_CLEAR_Z'] + SLED_Z))   # as in t5_integration (board trimmed 0.7)
SOUND_PORT = dict(d=SOUND_PORT_D, zs=SL['PIEZO_DZ'] / 2, ang=0.0)

_ar = open(AR_SRC, encoding="utf-8").read()
AR = {"__name__": "ar_proxy"}
exec(_ar[:_ar.rstrip().rfind("main()")], AR)
AR['thread_solid'] = lambda *a, **k: Part.makeBox(0.01, 0.01, 0.01, V(200, 200, -60))   # far away: the cut removes nothing
fincan_v1 = Part.Shape(); fincan_v1.read(FINCAN_STEP)
fincan_v1 = fincan_v1.Solids[0] if len(fincan_v1.Solids) == 1 else fincan_v1
proxy_v1 = AR['build_fin_can']()     # the raw compound: v1's heal() and removeSplitter() both corrupt this plain-boss build
cap = Part.Shape(); cap.read(CAP_STEP)
nose = Part.Shape(); nose.read(NOSE_STEP)
nose.rotate(V(0, 0, 0), V(1, 0, 0), 180.0)       # tip Z0 -> 0, base -> -65 ; y -> -y
nose.translate(V(0, 0, BODY_LEN + NOSE_LEN))     # tip at station -65
print("reused geometry in %.1f s" % (time.time() - t0))

# nose detent pilots: find their clocking after the flip (probe the real part)
_hits = [a for a in range(360) if not inside(nose, pol(19.2, a + 0.5, zs(NOSE_SCREW_ST)))]
NOSE_ANG = []
for a in _hits:
    if not NOSE_ANG or a - NOSE_ANG[-1][-1] > 1: NOSE_ANG.append([a])
    else: NOSE_ANG[-1].append(a)
if len(NOSE_ANG) == 4 and NOSE_ANG[0][0] == 0 and NOSE_ANG[-1][-1] == 359:   # wrap-around
    NOSE_ANG[0] = [x - 360 for x in NOSE_ANG.pop()] + NOSE_ANG[0]
NOSE_ANG = [round((c[0] + c[-1]) / 2.0 + 0.5, 1) % 360 for c in NOSE_ANG]

# =====================================================================================
# PARTS
# =====================================================================================
P = {}

# ---------------- FIN CAN, aft-deploy: v1 cfg C + d14 port + slip coupler + pin slots + harness lug
def pin_slot(ang, z):
    a2, b2 = (PIN_A + SLOT_CLR) / 2, (PIN_B + SLOT_CLR) / 2
    return rot(box(CPL_R_I - 1.0, R_OD + 1.0, -b2, b2, z - a2, z + a2), ang)

def anchor_lug(ang, prof_rz, hole_r, hole_z):
    """Wall-attached lug: (r, z) polygon extruded +-ANCH_W/2 tangentially, tangential d3.5 hole."""
    vs = [V(r, -ANCH_W / 2, z) for r, z in prof_rz]
    f = Part.Face(Part.Wire(Part.makePolygon(vs + [vs[0]])))
    lug = f.extrude(V(0, ANCH_W, 0))
    lug = lug.cut(Part.makeCylinder(ANCH_HOLE_D / 2, ANCH_W + 2, V(hole_r, -ANCH_W / 2 - 1, hole_z), V(0, 1, 0)))
    return rot(lug, ang)

PORT_CUT = revolve([(0, BH_Z0 - 0.5), (MOTOR_BORE_R - 0.01, BH_Z0 - 0.5), (MOTOR_BORE_R - 0.01, BH_Z0), (LEDGE_R, BH_Z0),
                    (PORT_R, BH_Z0 + (LEDGE_R - PORT_R)), (PORT_R, BH_Z1 + 1.0), (0, BH_Z1 + 1.0)])
OD_TRIM = revolve([(CPL_R_O, SHOULDER_Z + 0.02), (R_OD + 1, SHOULDER_Z + 0.02), (R_OD + 1, CPL_Z1 + 5), (CPL_R_O, CPL_Z1 + 5)])
COUPLER = revolve([(CPL_R_I, BH_Z1 - 0.5), (CPL_R_O, BH_Z1 - 0.5), (CPL_R_O, CPL_Z1 - CPL_CHAMFER),
                   (CPL_R_O - CPL_CHAMFER, CPL_Z1), (CPL_R_I, CPL_Z1)])
FC_LUG = anchor_lug(ANCH_FC['ang'], [(ANCH_R_IN, ANCH_FC['z0'] - 0.2), (CPL_R_I + 0.5, ANCH_FC['z0'] - 0.2),
                                     (CPL_R_I + 0.5, ANCH_FC['z1']), (ANCH_R_IN, ANCH_FC['z1'])], ANCH_HOLE_R, ANCH_FC['zh'])
Z_PIN = zs(PIN_ST)

def make_fincan(base):
    s = base.cut(PORT_CUT)
    s = s.cut(OD_TRIM)
    s = s.fuse(COUPLER)
    s = s.fuse(FC_LUG)
    for a in PIN_ANG:
        s = s.cut(pin_slot(a, Z_PIN))
    # no removeSplitter: on the faceted thread it runs 20+ min (aft_retention_v1 heal()), on the proxy it corrupts it
    return AR['as_solid'](s)

fincan = make_fincan(fincan_v1)
fincan_px = make_fincan(proxy_v1)
P['AftFinCan'] = fincan
print("fin can built in %.1f s" % (time.time() - t0))

# ---------------- FWD TUBE: nose shoulder + e-bay, spigot closed by a gas-tight bulkhead
s_bh0 = ST_BH_AFT - BH_T
fw = rst([(R_ID, 0.0), (R_OD, 0.0), (R_OD, J), (SPIGOT_RO, J), (SPIGOT_RO, ST_BH_AFT - EF), (SPIGOT_RO - EF, ST_BH_AFT),
          (0.0, ST_BH_AFT), (0.0, s_bh0), (SPIGOT_RI, s_bh0), (SPIGOT_RI, J - J_RING),
          (R_ID, J - J_RING - (R_ID - SPIGOT_RI))])
fw = fw.cut(rst([(R_ID - 0.01, EF + 0.01), (R_ID + EF + 0.01, -0.01), (R_ID - 0.01, -0.01)]))    # ID lead-in for the nose shoulder
for a in NOSE_ANG:
    fw = fw.cut(radial_cyl(NOSE_SCREW_CLR_D / 2, R_ID - 1, R_OD + 1, zs(NOSE_SCREW_ST), a))
CSK_TOP = math.sqrt(R_OD ** 2 - (CSK_DK / 2) ** 2)
def csk_cutter(z, ang):
    c = radial_cyl(CSK_DK / 2 + 0.1, CSK_TOP - CSK_K_CYL, R_OD + 2, z, ang)
    c = c.fuse(radial_cone(1.6, CSK_DK / 2 + 0.1, CSK_TOP - CSK_K_CYL - CSK_CONE - 0.1, CSK_TOP - CSK_K_CYL, z, ang))
    return c.fuse(radial_cyl(1.6, R_ID - 1.0, CSK_TOP - CSK_K_CYL - 1.0, z, ang))
def csk_screw(z, ang):
    s = radial_cyl(CSK_DK / 2, CSK_TOP - CSK_K_CYL, CSK_TOP, z, ang)
    s = s.fuse(radial_cone(1.5, CSK_DK / 2, CSK_TOP - CSK_K_CYL - CSK_CONE, CSK_TOP - CSK_K_CYL, z, ang))
    return s.fuse(radial_cyl(1.5, CSK_TOP - M3_LEN, CSK_TOP - CSK_K_CYL - CSK_CONE + 0.01, z, ang))
for a in EBAY_ANG:
    fw = fw.cut(csk_cutter(zs(EBAY_SCREW_ST), a))
for p in (STATIC_PORT, SOUND_PORT):
    fw = fw.cut(radial_cyl(p['d'] / 2, R_ID - 1, R_OD + 1, p['zs'] + SLED_Z, p['ang']))
fw = fw.removeSplitter()
P['FwdTube'] = fw

# ---------------- AFT TUBE: chute bay, harness lug, pin slots, launch lug
at = rst([(R_ID, J), (R_OD, J), (R_OD, ST_BODY_AFT), (R_ID, ST_BODY_AFT)])
at = at.cut(rst([(R_ID - 0.01, J + EF + 0.01), (R_ID + EF + 0.01, J - 0.01), (R_ID - 0.01, J - 0.01)]))          # bed side / spigot lead-in
at = at.cut(rst([(R_ID - 0.01, ST_BODY_AFT - EF - 0.01), (R_ID + EF + 0.01, ST_BODY_AFT + 0.01), (R_ID - 0.01, ST_BODY_AFT + 0.01)]))  # coupler lead-in
a_st0, a_sth, a_st1 = ANCH_AT['st0'], ANCH_AT['st_h'], ANCH_AT['st1']
AT_LUG = anchor_lug(ANCH_AT['ang'], [(R_ID + 0.5, zs(a_st0)), (ANCH_R_IN, zs(a_st0 + (R_ID + 0.5 - ANCH_R_IN))),
                                     (ANCH_R_IN, zs(a_st1)), (R_ID + 0.5, zs(a_st1))], ANCH_HOLE_R, zs(a_sth))
at = at.fuse(AT_LUG)
CAP_RIB_R = AR['CAP_R_O'] + AR['RIB_PROUD']        # 22.75: cap v1 grip ribs
LL_C = CAP_RIB_R + LL_RIB_CLEAR + ROD_R + (LL_RI - ROD_R)   # 25.95: rod centre off the body axis (pad assumed 25)
zf_ll, za_ll = zs(LL_ST0), zs(LL_ST1)               # forward (prints DOWN: AftTube is flipped) / aft end
ll = cyl(LL_RO, za_ll, zf_ll, x=LL_C).fuse(box(R_OD - 0.6, LL_C, -LL_WEB / 2, LL_WEB / 2, za_ll, zf_ll))
_tri = [V(R_OD, 0, zf_ll), V(R_OD, 0, zf_ll + 1), V(R_OD + 12, 0, zf_ll + 1), V(R_OD + 12, 0, zf_ll - 12)]
_ch = Part.Face(Part.Wire(Part.makePolygon(_tri + [_tri[0]]))).extrude(V(0, 20, 0)).translated(V(0, -10, 0))
ll = ll.cut(_ch)                                                                   # 45 deg forward end: self-supporting printed forward-end down
ll = ll.cut(cyl(R_OD - 0.05, za_ll - 5, zf_ll + 5))                                # nothing inside the wall
ll = ll.cut(cyl(LL_RI, za_ll - 5, zf_ll + 5, x=LL_C))
LL = rot(ll, LL_ANG)
at = at.fuse(LL)
for a in PIN_ANG:
    at = at.cut(pin_slot(a, Z_PIN))
at = at.removeSplitter()
P['AftTube'] = at

# ---------------- SLED MOUNT (T5-integration layout, lugs grown to the bare bore)
zd0, zd1 = DISC_ZS0 + SLED_Z, DISC_ZS1 + SLED_Z
sm = cyl(DISC_R, zd0, zd1)
top_slab = sled.common(box(-30, 30, -30, 30, zd0 + 0.01, zd1 + 1))
pk = [top_slab.translated(V(dx, dy, dz)) for dx, dy in ((0, 0), (0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25), (0.18, 0.18), (-0.18, 0.18), (0.18, -0.18), (-0.18, -0.18)) for dz in (-0.3, 0, 0.3)]
sm = sm.cut(pk[0].fuse(pk[1:]))
sm = sm.cut(cyl(LEAD_HOLE_R, zd0 - 1, zd1 + 1))
zl1 = zs(LUG_TOP_ST)
for a in EBAY_ANG:
    lug = cyl(LUG_RO, zd1 - 0.01, zl1).cut(cyl(LUG_RI, zd1 - 1, zl1 + 1))
    sm = sm.fuse(lug.common(rot(box(0, 30, -LUG_W / 2, LUG_W / 2, zd1 - 1, zl1 + 1), a)))
for a in EBAY_ANG:
    sm = sm.cut(radial_cyl(1.25, LUG_RI - 1, LUG_RO + 1, zs(EBAY_SCREW_ST), a))     # M3 self-tap pilot
SLED_SCREWS = [(SL['SERVO_TAB_XW'], 0.0), (SL['SERVO_TAB_XE'], 0.0)]
for x, y in SLED_SCREWS:
    sm = sm.cut(cyl(1.1, zd0 - 1, zd1 + 1, x=x, y=y))
sm = sm.removeSplitter()
P['SledMount'] = sm

# ---------------- SHEAR PIN (local: x radial-in from the OD, y tangential, z axial = print thickness)
def pin_profile(bn):
    hb, b2, n2 = PIN_HEAD_B / 2, PIN_B / 2, bn / 2
    w = (b2 - n2) * math.tan(math.radians(PIN_NOTCH_DEG / 2))     # half-length of each V along x
    xn = PIN_X_NECK
    pts = [(-PIN_HEAD_T, -hb), (0, -hb), (0, -b2), (xn - w, -b2), (xn, -n2), (xn + w, -b2), (PIN_L, -b2),
           (PIN_L, b2), (xn + w, b2), (xn, n2), (xn - w, b2), (0, b2), (0, hb), (-PIN_HEAD_T, hb)]
    return pts
def build_pin(bn, ticks=0):
    vs = [V(x, y, 0) for x, y in pin_profile(bn)]
    s = Part.Face(Part.Wire(Part.makePolygon(vs + [vs[0]]))).extrude(V(0, 0, PIN_A))
    for k in range(ticks):                                        # ID nicks on the head's outer edge
        s = s.cut(box(-PIN_HEAD_T - 0.1, -PIN_HEAD_T + 0.3, -PIN_HEAD_B / 2 + 0.4 + 0.8 * k, -PIN_HEAD_B / 2 + 0.8 + 0.8 * k, -1, 2))
    return s
def place_pin(s, ang, z):
    t = s.copy()
    t.rotate(V(0, 0, 0), V(0, 0, 1), 180.0)                       # x now points radially INWARD
    t.translate(V(R_OD, 0, z - PIN_A / 2))
    return rot(t, ang)
pin_flat = build_pin(PIN_BN)
PINS = {'pin_%d' % i: place_pin(pin_flat, a, Z_PIN) for i, a in enumerate(PIN_ANG)}
P['ShearPin'] = pin_flat

card = []
for k, bn in enumerate(PIN_BN_CARD):
    for j in range(4):
        card.append(build_pin(bn, ticks=k + 1).translated(V(8.0 * j, 7.0 * k, 0)))
P['ShearPinCard'] = Part.makeCompound(card)

# ---------------- PIN TEST COUPON: the same walls and slots, loaded by a hanging weight
CPN_H, CPN_PIN_Z, CPN_HOLE_Z = 30.0, 12.0, 27.0   # outer ring; string holes ABOVE the inner ring's top
CPN_IN_H, CPN_IN_DROP = 26.0, 4.0                   # inner ring hangs 4 mm below the outer, top at 22 assembled
co = cyl(R_OD, 0, CPN_H).cut(cyl(R_ID, -1, CPN_H + 1))
for a in (0.0, 180.0):
    co = co.cut(pin_slot(a, CPN_PIN_Z))
for a in (90.0, 270.0):
    co = co.cut(radial_cyl(1.5, R_ID - 1, R_OD + 1, CPN_HOLE_Z, a))    # string passes straight across the bore
P['PinCouponOuter'] = co.removeSplitter()
ci = cyl(CPL_R_O, 0, CPN_IN_H).cut(cyl(CPL_R_I, 2.0, CPN_IN_H + 1))
ci = ci.cut(cyl(2.0, -1, 3))                                            # hook hole for the weight
for a in (0.0, 180.0):
    ci = ci.cut(pin_slot(a, CPN_PIN_Z + CPN_IN_DROP))
P['PinCouponInner'] = ci.removeSplitter()

# ---------------- hardware
HW = {}
for i, a in enumerate(EBAY_ANG):
    HW['M3x8_csk_%d' % i] = csk_screw(zs(EBAY_SCREW_ST), a)
for i, (x, y) in enumerate(SLED_SCREWS):
    HW['M2x10_pan_%d' % i] = cyl(1.9, zd1, zd1 + 1.3, x=x, y=y).fuse(cyl(1.0, zd1 - 10.0, zd1 + 0.01, x=x, y=y))
for i, a in enumerate(NOSE_ANG):
    HW['M5x8_button_%d' % i] = radial_cyl(M5_DK / 2, R_OD, R_OD + M5_K, zs(NOSE_SCREW_ST), a).fuse(
        radial_cyl(2.5, R_OD - M5_LEN, R_OD + 0.01, zs(NOSE_SCREW_ST), a))
motor = Part.makeCylinder(MOTOR_R, MOTOR_ZF[1] - MOTOR_ZF[0], V(0, 0, MOTOR_ZF[0]))
print("parts built in %.1f s" % (time.time() - t0))

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: aft deployment on the Klima D9-5 motor ejection charge ==" % REV)
rep("Frame z = %.0f - station (station 0 = nose base). Fin-can frame Zf = z. Threaded fin can: booleans run on the thread-free proxy." % BODY_LEN)
rep("")
rep("STATION TABLE")
for s0, s1, what in ((-65, 0, "nose v5 (unchanged part), retained -- never separates"),
                     (0, NOSE_SH_END, "nose shoulder; 3 x M5 x 8 button heads at station %.0f into its d4.2 pilots (clocked %s deg)" % (NOSE_SCREW_ST, "/".join("%.0f" % a for a in NOSE_ANG))),
                     (LUG_TOP_ST, station(zd0), "sled mount: lugs + disc; 3 x M3 CSK at station %.0f" % EBAY_SCREW_ST),
                     (station(sled.BoundBox.ZMax), station(sled.BoundBox.ZMin), "e-bay sled v1 (logging only; no servo, no pyro)"),
                     (J, J, "BONDED joint fwd_tube / aft_tube"),
                     (s_bh0, ST_BH_AFT, "gas-tight bulkhead (end of the fwd_tube spigot)"),
                     (ST_BH_AFT, station(BH_Z1), "CHUTE BAY: harness lug %.0f-%.0f, canopy, Nomex" % (a_st0, a_st1)),
                     (LL_ST0, LL_ST1, "launch lug on the OD, %.0f deg, bore d%.1f, rod line r %.2f (stood off on a web to clear the cap ribs)" % (LL_ANG, 2 * LL_RI, LL_C)),
                     (station(CPL_Z1), ST_BODY_AFT, "fin-can coupler in the aft tube: SLIP FIT, NOT BONDED (the separation)"),
                     (PIN_ST, PIN_ST, "%d x printed shear pins at %s deg" % (PIN_N, "/".join("%.0f" % a for a in PIN_ANG))),
                     (station(BH_Z1), station(BH_Z0), "fin-can thrust ring, d%.0f gas port, harness lug at %.0f deg" % (2 * PORT_R, ANCH_FC['ang'])),
                     (ST_BODY_AFT, BODY_LEN, "fin can (v1 cfg C), Klima D9 18 x 70, cap v1 to station %.1f" % station(cap.BoundBox.ZMin))):
    rep("  %7.1f - %7.1f  %s" % (s0, s1, what))
rep("")

# --- validity
for k in ('AftFinCan', 'FwdTube', 'AftTube', 'SledMount', 'ShearPin', 'PinCouponOuter', 'PinCouponInner'):
    s = P[k]; rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))
rep("%s fin-can proxy valid, one solid" % ok(fincan_px.isValid() and len(fincan_px.Solids) == 1))
rep("%s nose detent pilots found at station %.0f: %d, clocked %s" % (ok(len(NOSE_ANG) == 3), NOSE_SCREW_ST, len(NOSE_ANG), NOSE_ANG))

# --- the real (threaded) fin can: prove every new feature landed, by probes
probes = [("gas port open on the axis", V(0, 0, (BH_Z0 + BH_Z1) / 2), False),
          ("gas port open at r 6.5", pol(6.5, 30, BH_Z1 - 0.3), False),
          ("casing-rim ledge present r 8.7 (thrust stop)", pol(8.7, 30, BH_Z0 + 0.5), True),
          ("motor bore still open below the ledge", pol(8.7, 30, BH_Z0 - 0.3), False),
          ("coupler wall present mid-length", pol(19.15, 30, (BH_Z1 + CPL_Z1) / 2), True),
          ("coupler OD trimmed to %.2f" % CPL_R_O, pol(19.83, 30, SHOULDER_Z + 3.0), False),
          ("shoulder still full OD below", pol(21.3, 30, SHOULDER_Z - 0.3), True),
          ("harness lug present", pol(13.2, ANCH_FC['ang'], ANCH_FC['z1'] - 0.5), True),
          ("harness lug hole open", pol(ANCH_HOLE_R, ANCH_FC['ang'], ANCH_FC['zh']), False),
          ("bore of the coupler open", pol(15.0, 120, CPL_Z1 - 5), False)]
probes += [("pin slot %d open through the coupler wall" % i, pol(19.15, a, Z_PIN), False) for i, a in enumerate(PIN_ANG)]
probes += [("coupler wall beside pin slot %d" % i, pol(19.15, a + 12, Z_PIN), True) for i, a in enumerate(PIN_ANG)]
bad = [(n, want) for n, p, want in probes if inside(fincan, p) != want]
badp = [(n, want) for n, p, want in probes if inside(fincan_px, p) != want]
rep("%s REAL fin can: %d/%d feature probes as designed%s" % (ok(not bad), len(probes) - len(bad), len(probes), "; WRONG: %s" % bad if bad else ""))
rep("%s proxy fin can: %d/%d same probes%s" % (ok(not badp), len(probes) - len(badp), len(probes), "; WRONG: %s" % badp if badp else ""))
dv_real, dv_px = fincan.Volume - fincan_v1.Volume, fincan_px.Volume - proxy_v1.Volume
rep("%s feature volume delta real %+.1f vs proxy %+.1f mm3 (the same cuts/fuses landed on both; |d| < 2)" % (ok(abs(dv_real - dv_px) < 2.0), dv_real, dv_px))
thr = [p for p in (pol(18.6, a, -8.0) for a in range(0, 360, 7))]
nthr = sum(1 for p in thr if inside(fincan, p)) - sum(1 for p in thr if inside(fincan_px, p))
rep("%s thread present on the real part only: %d of %d probes at r 18.6 / Zf -8 are groove on the real part, solid on the proxy" % (ok(nthr < -5), -nthr, len(thr)))

# --- interference, flight configuration (proxy fin can; cap excluded -- verify_aft_retention covers cap/fin can)
air = dict(nose=nose, fwd=P['FwdTube'], aft=P['AftTube'], mount=P['SledMount'], sled=sled, fincan=fincan_px, motor=motor, **HW, **PINS)
air.update({'env_' + k: v for k, v in ENV.items()})
WL = {('sled', 'env_SmallParts')}
WL |= {('M3x8_csk_%d' % i, 'mount') for i in range(3)} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)}
WL |= {('M5x8_button_%d' % i, 'nose') for i in range(3)}
def interference(parts, wl=()):
    out, ks = [], list(parts)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            if (a, b) in wl or (b, a) in wl: continue
            if not parts[a].BoundBox.intersect(parts[b].BoundBox): continue
            v = parts[a].common(parts[b]).Volume
            if v > 1e-3: out.append((a, b, round(v, 3)))
    return out
bad = interference(air, WL)
rep("%s interference, flight (pins in): %s" % (ok(not bad), bad or "none"))
for i in range(3):
    ov = HW['M5x8_button_%d' % i].common(nose)
    rr = [math.hypot(v.X, v.Y) for v in ov.Vertexes]
    rep("%s nose screw %d: M5 self-taps %.1f mm into the nose pilot (>= 5)" % (ok(rr and max(rr) - min(rr) >= 5.0), i, (max(rr) - min(rr)) if rr else 0))
for i in range(3):
    ov = HW['M3x8_csk_%d' % i].common(P['SledMount'])
    rr = [math.hypot(v.X, v.Y) for v in ov.Vertexes]
    rep("%s e-bay screw %d: %.1f mm engaged in the lug (>= 3.5)" % (ok(rr and max(rr) - min(rr) >= 3.5), i, (max(rr) - min(rr)) if rr else 0))

# --- separation sweep: pins sheared, fin can + motor move aft
sweep = []
for d in [0.5 * k for k in range(0, int((CPL_LEN + 4) / 0.5) + 1)]:
    fc_d = fincan_px.translated(V(0, 0, -d))
    v = fc_d.common(P['AftTube']).Volume
    if v > 1e-3: sweep.append((d, round(v, 3)))
rep("%s separation sweep 0..%.0f mm aft (pins sheared): fin can never touches the aft tube %s" % (ok(not sweep), CPL_LEN + 4, sweep[:4] or ""))
rep("%s coupler leaves the body after %.1f mm of travel; nothing in the bay forward of the coupler face within %.0f mm (aft-tube lug at station %.0f)"
    % (ok(station(CPL_Z1) - a_st1 > 50), CPL_LEN, station(CPL_Z1) - a_st1, a_st1))

# --- fits
rep("%s coupler OD %.2f in the aft-tube bore %.2f: %.2f mm diametral slip (not bonded; target 0.3-0.5)" % (ok(0.3 <= 2 * (R_ID - CPL_R_O) <= 0.5), 2 * CPL_R_O, 2 * R_ID, 2 * (R_ID - CPL_R_O)))
rep("%s spigot OD %.2f in the aft-tube bore: %.2f mm diametral epoxy gap (bonded)" % (ok(abs(2 * (R_ID - SPIGOT_RO) - 0.3) < 0.01), 2 * SPIGOT_RO, 2 * (R_ID - SPIGOT_RO)))
rep("%s sled (R %.2f) / disc (R %.2f) / lugs (R %.2f) pass the 40 bore from the nose end" % (ok(R_ID - max(SL['SLED_RMAX'], DISC_R) >= 0.25 and R_ID - LUG_RO >= 0.2), SL['SLED_RMAX'], DISC_R, LUG_RO))
last = min(s.BoundBox.ZMin for s in [sled] + list(ENV.values()))
rep("%s e-bay contents end at station %.1f, forward of the spigot (bore narrows to %.1f at station %.1f)" % (ok(station(last) < J - J_RING - 1.5), station(last), 2 * SPIGOT_RI, J - J_RING - (R_ID - SPIGOT_RI)))
rep("%s sled-mount lugs start %.1f mm behind the nose shoulder" % (ok(LUG_TOP_ST - NOSE_SH_END >= 2), LUG_TOP_ST - NOSE_SH_END))

# --- gas paths
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, zs(ST_BH_AFT) - 0.5)
hits = [k for k, s in dict(fincan=fincan_px, aft=P['AftTube'], fwd=P['FwdTube']).items() if s.common(gp).Volume > 1e-3]
rep("%s d%.0f gas column clear from the motor face to the bulkhead (the lug sits beside the port): %s" % (ok(not hits), 2 * PORT_R, hits or "clear"))
bh = P['FwdTube'].common(cyl(SPIGOT_RI - 0.01, zs(ST_BH_AFT) + 0.01, zs(s_bh0) - 0.01))
rep("%s e-bay bulkhead solid: %.1f of %.1f mm3 (no lead or vent holes)" % (ok(abs(bh.Volume - math.pi * (SPIGOT_RI - 0.01) ** 2 * (BH_T - 0.02)) < 0.5), bh.Volume, math.pi * (SPIGOT_RI - 0.01) ** 2 * (BH_T - 0.02)))
band = P['AftTube'].common(rst([(R_ID + 0.01, ST_BH_AFT), (R_OD - 0.06, ST_BH_AFT), (R_OD - 0.06, ST_BODY_AFT - 1.0), (R_ID + 0.01, ST_BODY_AFT - 1.0)]))
ideal = math.pi * ((R_OD - 0.06) ** 2 - (R_ID + 0.01) ** 2) * (ST_BODY_AFT - 1.0 - ST_BH_AFT)
slot_v = PIN_N * (PIN_A + SLOT_CLR) * (PIN_B + SLOT_CLR) * (R_OD - 0.06 - R_ID - 0.01)
rep("%s chute-bay wall: missing %.2f mm3 vs %.2f of pin slots -> no other holes" % (ok(abs((ideal - band.Volume) - slot_v) < 0.3), ideal - band.Volume, slot_v))
fb = P['FwdTube'].common(rst([(R_ID + 0.01, 0.0), (R_OD - 0.06, 0.0), (R_OD - 0.06, J - 0.5), (R_ID + 0.01, J - 0.5)]))
rep("NOTE e-bay wall holes: %.1f mm3 removed (3 x M5, 3 x M3 CSK, static d%.1f, sound d%.1f) -- all forward of the bulkhead"
    % (math.pi * ((R_OD - 0.06) ** 2 - (R_ID + 0.01) ** 2) * (J - 0.5) - fb.Volume, STATIC_PORT['d'], SOUND_PORT['d']))

# --- launch rod line (d4.0 rod, worst case pushed toward the body axis inside the bore)
rod_c = LL_C - (LL_RI - ROD_R)
rod = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=rod_c), LL_ANG)
rod_mid = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=LL_C), LL_ANG)
cap_env = cyl(CAP_RIB_R, cap.BoundBox.ZMin - 0.1, cap.BoundBox.ZMax + 0.1)          # cap + ribs at ANY clocking
hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod).Volume) for k, sh in dict(cap_ribs_any_clocking=cap_env, fincan=fincan_px, fwd=P['FwdTube'], nose=nose, **HW).items()) if v > 1e-3]
rep("%s launch rod d%.1f, pushed %.2f mm toward the axis in the lug: clear of cap ribs (any clocking), fins, nose, screw heads: %s"
    % (ok(not hits), 2 * ROD_R, LL_RI - ROD_R, hits or "clear"))
rep("%s rod centred in the lug bore does not touch the AftTube (%.4f mm3); rod line %.2f mm from the body axis (pad [6-8] assumed 25), %.2f mm clear of the ribs"
    % (ok(rod_mid.common(P['AftTube']).Volume < 1e-3), rod_mid.common(P['AftTube']).Volume, LL_C, rod_c - ROD_R - CAP_RIB_R))
ll_probe = [inside(P['AftTube'], pol(LL_C + LL_RO - 0.3, LL_ANG, zs((LL_ST0 + LL_ST1) / 2))), inside(P['AftTube'], pol(R_OD + 0.8, LL_ANG, zs((LL_ST0 + LL_ST1) / 2))),
            not inside(P['AftTube'], pol(LL_C, LL_ANG, zs((LL_ST0 + LL_ST1) / 2)))]
rep("%s launch lug present (outer wall, web) and its bore open: %s" % (ok(all(ll_probe)), ll_probe))

# --- pin coupon, assembled: inner ring dropped CPN_IN_DROP, 2 pins at 0/180
c_in = P['PinCouponInner'].translated(V(0, 0, -CPN_IN_DROP))
c_pins = [place_pin(pin_flat, a, CPN_PIN_Z) for a in (0.0, 180.0)]
cb = [round(p.common(P['PinCouponOuter']).Volume + p.common(c_in).Volume, 4) for p in c_pins]
string = Part.makeCylinder(1.0, 2 * R_OD + 4, V(0, -R_OD - 2, CPN_HOLE_Z), V(0, 1, 0))
blk = [k for k, sh in (("outer", P['PinCouponOuter']), ("inner", c_in)) if sh.common(string).Volume > 1e-3]
hook = not inside(c_in, V(0, 0, -CPN_IN_DROP + 1.0))
ov = P['PinCouponOuter'].common(c_in).Volume
rep("%s pin coupon assembled: rings do not touch (%.3f mm3), pins free in both slots %s, string line across the holes %s, hook hole open %s"
    % (ok(ov < 1e-3 and max(cb) < 1e-3 and not blk and hook), ov, cb, blk or "clear", hook))

# --- shear pins
A_neck = PIN_A * PIN_BN
F_pin = TAU_ABS * A_neck
F_tot = PIN_N * F_pin
A_bore = math.pi * R_ID ** 2
rep("")
rep("SHEAR PINS (%d x, neck %.2f x %.2f mm, tau %.0f MPa ASSUMED)" % (PIN_N, PIN_A, PIN_BN, TAU_ABS))
rep("  per pin %.1f N, total %.1f N  = %.1f kPa (%.2f psi) over the d%.0f bore" % (F_pin, F_tot, F_tot / A_bore * 1e3, F_tot / A_bore * 145.04, 2 * R_ID))
for nm, p in PINS.items():
    v1 = p.common(P['AftTube']).Volume + p.common(fincan_px).Volume
    rr = [math.hypot(v.X, v.Y) for v in p.Vertexes]
    rep("%s %s sits in both slots with clearance (overlap %.3f mm3), spans r %.2f..%.2f (tube OD -> coupler ID)" % (ok(v1 < 1e-3 and min(rr) <= CPL_R_I + 0.1 and max(rr) >= R_OD), nm, v1, min(rr), max(rr)))
brg_t = F_pin / (PIN_B * (R_OD - R_ID)); brg_c = F_pin / (PIN_B * (CPL_R_O - CPL_R_I))
e_t = ST_BODY_AFT - PIN_ST - (PIN_A + SLOT_CLR) / 2
tear_t = 2 * e_t * (R_OD - R_ID) * TAU_ABS
e_c = CPL_Z1 - Z_PIN - (PIN_A + SLOT_CLR) / 2      # fin can moves aft: the pin loads the slot's FORWARD face -> ligament to the coupler front
tear_c = 2 * e_c * (CPL_R_O - CPL_R_I) * TAU_ABS
rep("%s pin is the weak link: bearing tube %.1f MPa / coupler %.1f MPa (<< 40); slot tear-out tube %.0f N (edge %.1f mm), coupler %.0f N (edge %.1f mm)  vs pin %.1f N"
    % (ok(brg_t < 20 and brg_c < 20 and min(tear_t, tear_c) > 10 * F_pin), brg_t, brg_c, tear_t, e_t, tear_c, e_c, F_pin))
dP_apogee = 1.225 * 9.81 * 175.0                     # Pa: bay sealed at the pad, ambient drop to ~175 m AGL
F_press = dP_apogee * A_bore * 1e-6
F_hang = (46.1 + 9.0 + MOTOR_LOADED) * 9.81e-3       # fin can + cap + loaded motor hanging from a nose-up body
F_drag = 0.8                                         # N, upper bound: fin-can drag at 50 m/s (0.3 Cd on the ref area)
hold = F_press + F_hang + F_drag
rep("  hold budget (worst case, all additive): bay overpressure at apogee %.1f N + hanging fin can/motor %.1f N + drag separation <= %.1f N = %.1f N"
    % (F_press, F_hang, F_drag, hold))
rep("%s pins hold %.1fx that; slide friction adds to the hold and to what the charge must beat (measure it: target < 3 N)" % (ok(F_tot / hold >= 3), F_tot / hold))
rep("  release: the charge needs > %.1f N (+ friction) = %.1f kPa gauge in the bay. The D9 charge is not published -- pull-test each pin batch" % (F_tot, F_tot / A_bore * 1e3))
rep("  on PinCouponOuter/Inner; accept a batch at 8-15 N per pin (neck %.2f nominal; the card carries %s, 1-4 head nicks)." % (PIN_BN, "/".join("%.1f" % b for b in PIN_BN_CARD)))

# --- anchors
rep("")
rep("HARNESS ANCHORS at the %.0f N snatch placeholder" % SNATCH_N)
for nm, top, hz in (("fin-can lug (on the thrust ring)", ANCH_FC['z1'], ANCH_FC['zh']), ("aft-tube lug (chute bay wall)", zs(a_st0) - 0, zs(a_sth))):
    lig = (abs(top - hz) - ANCH_HOLE_D / 2) if nm.startswith("fin") else (abs(zs(a_st1) - hz) - ANCH_HOLE_D / 2)
    bear = SNATCH_N / (ANCH_HOLE_D * ANCH_W)
    shear = 2 * lig * ANCH_W * TAU_ABS
    rep("%s %s: hole d%.1f, bearing %.1f MPa, shear-out ligament %.2f mm -> %.0f N (>= 2 x %.0f)" % (ok(bear < 20 and shear >= 2 * SNATCH_N), nm, ANCH_HOLE_D, bear, lig, shear, SNATCH_N))
rep("  both lugs fuse to the wall along their full length (in-layer bond); the fin-can lug also stands on the thrust ring.")
rep("  Tether: fin-can lug -> 300 mm Kevlar leader -> shock cord -> canopy -> shock cord -> aft-tube lug. Kevlar through the hot zone.")

# --- motor retention under the ejection kick
rep("")
kick = 55e3 * math.pi * PORT_R ** 2 * 1e-6
rep("MOTOR: the ejection reaction pushes the casing AFT onto the cap lip (~%.0f N at 55 kPa over the d%.0f port) -- the cap is now a primary" % (kick, 2 * PORT_R))
rep("  load path: if the motor leaves, the fin can does not separate. Thrust %.0f N peak on the %.1f mm2 ledge = %.2f MPa."
    % (MOTOR_PEAK_N, math.pi * (MOTOR_BORE_R ** 2 - LEDGE_R ** 2), MOTOR_PEAK_N / (math.pi * (MOTOR_BORE_R ** 2 - LEDGE_R ** 2))))
rep("OPEN measure a spent Klima D9: the cap's d15 lip must bear on the casing wall, and the ledge (r %.1f-%.1f) on the forward rim." % (LEDGE_R, MOTOR_BORE_R))
rep("OPEN the d18.4 bore leaves 0.4 mm around an 18.0 casing: a blow-by path from the port to the nozzle. One wrap of tape on the casing.")

# --- printability
ORIENT = {'AftFinCan': ('up', 'boss down (as v1; support under the 3 fin trailing edges)'),
          'FwdTube': ('up', 'bulkhead down on the bed'),
          'AftTube': ('flip', 'forward end down'),
          'SledMount': ('up', 'disc down, lugs up'),
          'ShearPin': ('up', 'flat, 0.8 mm tall'),
          'PinCouponOuter': ('up', 'either end'),
          'PinCouponInner': ('up', 'floor down')}
def oriented(k, s):
    s = s.copy()
    if ORIENT[k][0] == 'flip': s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return s
def overhangs(s, nz_lim=-0.75):
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    pts = m.Points
    fl = [f for f in m.Facets if f.Normal.z < nz_lim and min(pts[i].z for i in f.PointIndices) > 0.3]
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for f in fl:
        for i in f.PointIndices[1:]: parent[find(i)] = find(f.PointIndices[0])
    comp = {}
    for f in fl: comp.setdefault(find(f.PointIndices[0]), []).append(f)
    out = []
    for fs in comp.values():
        ps = [pts[i] for f in fs for i in f.PointIndices]
        xs, ys, zz = [p.x for p in ps], [p.y for p in ps], [p.z for p in ps]
        rs = [math.hypot(p.x, p.y) for p in ps]
        a = sum(f.Area for f in fs)
        out.append(dict(area=a, z=(min(zz) + max(zz)) / 2, span=min(max(xs) - min(xs), max(ys) - min(ys)),
                        ledge=a / (math.pi * (min(rs) + max(rs)))))     # mean annular width (t5_integration rule: ring ledges <= 2 mm print)
    return out
rep("")
for k in ('FwdTube', 'AftTube', 'SledMount', 'ShearPin', 'PinCouponOuter', 'PinCouponInner'):
    o = oriented(k, P[k]); bb = o.BoundBox
    fits = bb.XLength <= BED[0] and bb.YLength <= BED[1] and bb.ZLength <= BED[2]
    oh = overhangs(o)
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d need support%s"
        % (ok(fits and not big), k, ORIENT[k][1], bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s" % [dict((a, round(b, 1)) for a, b in c.items()) for c in big] if big else ""))
o = oriented('AftFinCan', fincan_px); bb = o.BoundBox
oh = overhangs(o)
big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
rep("NOTE AftFinCan (proxy) printed %s: %.1f x %.1f x %.1f mm; support patches (print z, span, mm2) %s -- bridged annuli, all present in v1 (centring rings Zf 12/40, thrust-ring annulus Zf 55.9 now incl. the %.1f mm casing-rim ledge); the fin trailing edges still take v1's support"
    % (ORIENT['AftFinCan'][1], bb.XLength, bb.YLength, bb.ZLength, [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big], MOTOR_BORE_R - LEDGE_R))
rep("NOTE FwdTube: the 1.65 mm outer step at station %.0f (43 -> 39.7) prints as a short flat overhang, like the nose base ledge; it is the bond face." % J)

# =====================================================================================
# MASS / CG
# =====================================================================================
def cg_z(shape):
    shs = shape.Solids if shape.Solids else [shape]
    vol = sum(s.Volume for s in shs)
    return sum(s.Volume * s.CenterOfMass.z for s in shs) / vol
items = []
def solid(nm, grp, shape, mat, note=""): items.append((nm, grp, shape.Volume * RHO[mat], cg_z(shape), "CAD x %s %.2f%s" % (mat, RHO[mat] * 1e3, note), shape))
def point(nm, grp, m, z, basis, shape=None): items.append((nm, grp, m, z, basis, shape))
solid("Nose cone v5 (Von Karman)", "nose", nose, "ABS")
for i in range(3): solid("M5x8 button (nose) %d" % i, "nose", HW['M5x8_button_%d' % i], "steel")
solid("FwdTube (nose shoulder + e-bay + bulkhead)", "airframe", P['FwdTube'], "ABS")
solid("AftTube (chute bay + lugs)", "airframe", P['AftTube'], "ABS")
solid("SledMount", "e-bay", P['SledMount'], "ABS")
for k in [k for k in HW if not k.startswith('M5')]: solid("HW %s" % k, "e-bay", HW[k], "steel")
solid("ElectronicsSled v1", "e-bay", sled, "ABS")
e_env = Part.makeCompound(list(ENV.values()))
point("Electronics, Opt B 620 mAh, no servo", "e-bay", 48.0 - 9.0, cg_z(e_env), "avbay packing md 6 (48 g less SG90); CG = envelopes", e_env)
point("Canopy d500 + harness + Kevlar leader", "recovery", CANOPY_G, zs(CANOPY_ST), "DESIGN 7.7; packed forward in the bay")
point("Nomex blanket / wadding", "recovery", NOMEX_G, zs(NOMEX_ST), "estimate")
for nm, p in PINS.items(): solid("Shear %s" % nm, "aft", p, "ABS")
solid("AftFinCan D9aft (v1 + port/coupler/lug)", "aft", fincan, "ABS")
solid("MotorRetainerCap v1", "aft", cap, "ABS")
Z_MOTOR = (MOTOR_ZF[0] + MOTOR_ZF[1]) / 2
def tot(sel):
    m = sum(i[2] for i in sel); return m, (sum(i[2] * i[3] for i in sel) / m if m else 0.0)
def fmt(z): return "st %6.1f (tip %6.1f)" % (station(z), station(z) + NOSE_LEN)
rep("")
rep("MASS & CG (printed parts solid x rho: an upper bound)")
rep("%-44s %-9s %7s  %-24s %s" % ("ITEM", "GROUP", "g", "CG", "BASIS"))
for nm, g, m, z, b, _ in items:
    rep("%-44s %-9s %7.1f  %-24s %s" % (nm, g, m, fmt(z), b))
rep("%-44s %-9s %7.1f  %-24s %s" % ("Klima D9-5 (loaded; %.1f g spent)" % MOTOR_SPENT, "motor", MOTOR_LOADED, fmt(Z_MOTOR), "OpenRocket motor DB"))
for g in ("nose", "airframe", "e-bay", "recovery", "aft"):
    m, z = tot([i for i in items if i[1] == g]); rep("  %-9s %6.1f g  CG %s" % (g, m, fmt(z)))
dry_m, dry_z = tot(items)
nn_m, nn_z = tot([i for i in items if i[1] != "nose"])
nose_m, nose_z = tot([i for i in items if i[1] == "nose"])
lo_m, lo_z = tot(items + [("", "", MOTOR_LOADED, Z_MOTOR, "", None)])
la_m, la_z = tot(items + [("", "", MOTOR_SPENT, Z_MOTOR, "", None)])
sep_m, _ = tot([i for i in items if i[1] == "aft"] + [("", "", MOTOR_SPENT, Z_MOTOR, "", None)])
rep("  Dry, flight-ready           %6.1f g  CG %s" % (dry_m, fmt(dry_z)))
rep("  Liftoff on D9 (27.1 g)      %6.1f g  CG %s" % (lo_m, fmt(lo_z)))
rep("  Landing (spent 11.0 g)      %6.1f g  CG %s   (of which the separated fin can + cap + spent motor: %.1f g)" % (la_m, fmt(la_z), sep_m))
rep("OPENROCKET: NOSE_G=%.1f NOSE_CG=%.1f NS_BODY_G=%.1f NS_BODY_LEN=%.1f NS_BODY_CGX=%.1f" % (nose_m, station(nose_z) + NOSE_LEN, nn_m, BODY_LEN, station(nn_z)))
rep("NOT IN FLIGHT MASS: pin card, pin coupons, RBF pin (there is none now). Epoxy / paint / tape: a few grams.")
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(PRINT_READY, exist_ok=True)
EXPORT = ('AftFinCan', 'FwdTube', 'AftTube', 'SledMount', 'ShearPin', 'PinCouponOuter', 'PinCouponInner')
for k in EXPORT:
    P[k].exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME, k)))
    MeshPart.meshFromShape(Shape=P[k], LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME, k)))
    if k != 'AftFinCan':
        MeshPart.meshFromShape(Shape=oriented(k, P[k]), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_%s.stl" % (NAME, k)))
fc_r = fincan.copy(); bb = fc_r.BoundBox; fc_r.translate(V(0, 0, -bb.ZMin))
MeshPart.meshFromShape(Shape=fc_r, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_AftFinCan.stl" % NAME))
MeshPart.meshFromShape(Shape=P['ShearPinCard'], LinearDeflection=0.005, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_ShearPinCard.stl" % NAME))

doc = App.newDocument("Phoenix_D9aft_v1")
for nm, g, m, z, b, s in items:
    if s is None: continue
    o = doc.addObject("Part::Feature", "".join(c if c.isalnum() else "_" for c in nm)[:40]); o.Shape = s; o.Label = "%s [%.1f g]" % (nm, m)
o = doc.addObject("Part::Feature", "D9_motor"); o.Shape = motor; o.Label = "Klima D9-5 stand-in [%.1f g loaded]" % MOTOR_LOADED
o = doc.addObject("Part::Feature", "CG_liftoff"); o.Shape = Part.makeSphere(2.5, V(0, 0, lo_z)); o.Label = "CG liftoff %.1f g @ st %.1f" % (lo_m, station(lo_z))
o = doc.addObject("Part::Feature", "REF_fincan_separated"); o.Shape = Part.makeCompound([fincan_px, motor, cap]).translated(V(0, 0, -(CPL_LEN + 60))); o.Label = "REF fin can after separation (proxy, 100 mm aft)"
doc.recompute()
doc.saveAs(os.path.join(MODELS, NAME + ".FCStd"))
Part.makeCompound([i[5] for i in items if i[5] is not None] + [motor]).exportStep(os.path.join(MODELS, NAME + "_assembly.step"))

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(24, 10))
    cols = {"nose": "0.25", "airframe": "tab:blue", "e-bay": "tab:brown", "aft": "tab:gray", "recovery": "tab:green"}
    def draw(ax, s, c, dz=0.0, y_cut=0.7):
        cut = Part.Face(Part.makePolygon([V(-200, y_cut, -400), V(200, y_cut, -400), V(200, y_cut, 500), V(-200, y_cut, 500), V(-200, y_cut, -400)]))
        for e in s.section(cut).Edges:
            pts = e.discretize(Deflection=0.1)
            ax.plot([station(p.z + dz) + NOSE_LEN for p in pts], [p.x for p in pts], color=c, lw=0.5)
    for ax, sep in zip(axs, (0.0, CPL_LEN + 60.0)):
        for nm, g, m, z, b, s in items:
            if s is None or g == "recovery": continue
            if s is fincan: s = fincan_px
            draw(ax, s, cols[g], dz=-sep if g == "aft" else 0.0)
        draw(ax, motor, "tab:orange", dz=-sep)
        ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.set_xlabel("mm from nose tip")
    axs[0].plot(station(lo_z) + NOSE_LEN, 0, "o", ms=10, mfc="none", mec="k"); axs[0].annotate("CG %.0f g" % lo_m, (station(lo_z) + NOSE_LEN, 3))
    axs[0].set_title("Phoenix ABS 40-43 %s -- flight (section y=0.7, fin can threads shown as proxy)" % REV)
    axs[1].set_title("after the D9-5 ejection charge: pins sheared, fin can + motor %.0f mm aft (harness not drawn)" % (CPL_LEN + 60))
    fig.savefig(os.path.join(MODELS, NAME + "_section.png"), dpi=100, bbox_inches="tight")
except Exception as ex:
    print("section plot skipped:", ex)

with open(os.path.join(MODELS, NAME + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t0))

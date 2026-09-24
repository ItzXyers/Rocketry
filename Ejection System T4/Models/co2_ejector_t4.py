# -*- coding: utf-8 -*-
"""
T4 CO2 ejector — spring striker + nichrome line release, 8 g threadless cartridge.

Run headless (regenerates everything):
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"

Frame: module axis = +Z, z = 0 at the module's aft face (the face that screws into the
bulkhead / test base).  +Z points forward (toward the nose).  All parts are modelled in
this frame at the COCKED state (stroke = STROKE_DEFAULT) and in print orientation (upright).

Everything below the PARAMETERS block is derived.  Change a parameter, re-run, read the
check report at the end.  Any FAIL line means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, Mesh, MeshPart

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else \
    r"C:\Users\dick_\Documents\Rocketry\Ejection System T4\Models"
ROOT = os.path.dirname(HERE)
OUT_MODELS = os.path.join(ROOT, "Models")
OUT_PRINT = os.path.join(ROOT, "Print Files")
REF_STL = os.path.join(ROOT, "References", "co2_cartridge_8g.stl")

# =====================================================================================
# PARAMETERS
# =====================================================================================
# --- Cartridge (reference: References/co2_cartridge_8g.stl == LE-8NT datasheet model).
#     Only L, D, neck D are datasheet values; the shoulder/tip profile is approximate.
#     MEASURE A REAL CARTRIDGE and use the seat gauge before trusting CART_* below.
CART_L, CART_D, CART_NECK_D = 66.0, 18.0, 8.7
CART_SEG = dict(bottom_dome=7.0, straight=38.0, shoulder=13.0, neck=4.0)  # tip = remainder
CART_TIP_FLAT_D = 4.0

# --- Fit / clearances (tune to your printer with the coupons)
BORE_CLEAR_D = 0.8          # diametral clearance cartridge body -> body bore
THREAD_CLEAR = 0.30         # radial clearance on every printed thread
SLIDE_CLEAR = 0.30          # radial clearance striker/bore, tail/cap hole

# --- Airframe
AIRFRAME_ID = 40.0          # Phoenix ABS 40-43 bore. Module is generic; bulkhead uses this.
AIRFRAME_OD = 43.0          # test-base socket takes a tube section of this OD

# --- Threads: (major D, lead, starts, depth, crest).  45 deg flanks -> prints upright.
T1 = dict(d=34.0, lead=9.0, starts=3, depth=1.2, crest=0.3)   # module <-> bulkhead/base (3-start: ~1.1 turns to seat)
T2 = dict(d=27.0, lead=2.5, starts=1, depth=1.0, crest=0.3)   # body <-> head (cartridge loading)
T3 = dict(d=21.0, lead=2.0, starts=1, depth=0.8, crest=0.3)   # head <-> cap (spring access)
T1_LEN, T2_LEN, T3_LEN = 10.0, 10.0, 8.0

# --- Body
FLOOR = 8.0                 # body floor (holds captive M6 nut)
GRUB_NOMINAL = 3.0          # M6 grub tip above floor at nominal cartridge length
FLANGE_D, FLANGE_H = 36.5, 4.0
M6_NUT_AF, M6_NUT_H = 10.0, 5.0
M6_GRUB_L = 12.0

# --- Head / striker
SEAT_D = 12.0               # cartridge shoulder seats on this edge (also plenum bore)
GAP_STOP = 3.0              # cartridge tip -> striker hard-stop plane (nominal geometry)
PENETRATION = 2.5           # needle tip below cartridge tip at end of stroke
STRIKER_D, STRIKER_H = 16.0, 10.0
TAIL_D, TAIL_FLAT = 6.0, 2.4          # D-profile tail: flat at y = +TAIL_FLAT (anti-rotation)
SPRING_CAVITY_FIRED = 35.0  # striker top -> cap underside at end of stroke (dev: long)
STROKES = (4.0, 7.0, 10.0)  # selectable by which tail cross-hole takes the line
STROKE_DEFAULT = 7.0
CROSS_HOLE_D = 1.6          # print undersize-ish, drill 1.6 (or press 1.6/1.0 brass tube)
LINE_D = 0.3
HEAD_OD, SKIRT_OD = 26.0, 32.0
PORT_W, PORT_N = 5.0, 4
NEEDLE_D = 3.0              # M3 DIN 914 cone-point set screw, sharpened
PIERCE_HOLE_D = 3.0         # worst-case hole the needle opens (for vent-ratio check)

# --- Cap
CAP_FLANGE_H = 4.0
TERM_XY = (5.5, 4.5)        # M2 terminal screws at (x, +/-y)
ANCHOR_X = 9.2             # M2 line-clamp screws (+washer) at (+/-x, 0); replaces printed tie posts

# --- Spacers
SPACERS = (1.0, 2.0, 4.0, 8.0)

# =====================================================================================
# DERIVED GEOMETRY
# =====================================================================================
def smoothstep(t):
    return 0.0 if t < 0 else 1.0 if t > 1 else t * t * (3 - 2 * t)

_cb, _cs, _csh, _cn = CART_SEG['bottom_dome'], CART_SEG['straight'], CART_SEG['shoulder'], CART_SEG['neck']
_ctop = CART_L - _cb - _cs - _csh - _cn
_cr, _nr, _tr = CART_D / 2, CART_NECK_D / 2, CART_TIP_FLAT_D / 2
_tip_zt_flat = _ctop * math.sqrt(max(0, 1 - (_tr / _nr) ** 2))

def cart_r(z):
    if z <= _cb: return _cr * math.sqrt(max(0, 1 - ((_cb - z) / _cb) ** 2))
    if z <= _cb + _cs: return _cr
    if z <= _cb + _cs + _csh:
        return _cr - (_cr - _nr) * smoothstep((z - _cb - _cs) / _csh)
    if z <= _cb + _cs + _csh + _cn: return _nr
    zt = z - (_cb + _cs + _csh + _cn)
    return _nr * math.sqrt(max(0, 1 - (zt / _ctop) ** 2)) if zt <= _tip_zt_flat else _tr

def cart_z_at_r(r):
    """Height (cartridge frame) on the shoulder where the radius equals r."""
    lo, hi = _cb + _cs, _cb + _cs + _csh
    for _ in range(80):
        m = (lo + hi) / 2
        if cart_r(m) > r: lo = m
        else: hi = m
    return (lo + hi) / 2

BORE_D = CART_D + BORE_CLEAR_D
Z_CB = FLOOR + GRUB_NOMINAL                       # cartridge base (dome apex)
Z_SEAT = Z_CB + cart_z_at_r(SEAT_D / 2)           # seat edge plane
Z_TIP = Z_CB + CART_L
Z_STOP = Z_TIP + GAP_STOP                         # striker hard-stop plane
NEEDLE_PROTRUSION = GAP_STOP + PENETRATION        # below striker face
Z_CU = Z_STOP + STRIKER_H + SPRING_CAVITY_FIRED   # cap underside
Z_CT = Z_CU + T3_LEN + CAP_FLANGE_H               # cap top
Z_HEAD_TOP = Z_CU + T3_LEN
Z_BODY_TOP = 53.0 if Z_SEAT - 3.4 > 55 else Z_SEAT - 10.8
Z_T2 = Z_BODY_TOP - 3.0 - T2_LEN                  # body thread start
Z_SKIRT = Z_T2                                    # head skirt bottom
# tail cross-hole centres, measured from striker bottom face (u). Line sits on cap top and
# the hole centre is 0.5 mm below the cap top at the cocked state.
CROSS_U = {s: Z_CT - 0.5 - Z_STOP - s for s in STROKES}
TAIL_TOP_U = max(CROSS_U.values()) + CROSS_HOLE_D / 2 + 1.7 + 7.0   # 7 mm M3 pilot above holes
PORT_Z = (Z_SEAT + 2.0, Z_STOP - 2.0)

def ok(b): return "PASS" if b else "FAIL"

# =====================================================================================
# HELPERS
# =====================================================================================
def revolve(rz):
    pts = [V(r, 0, z) for r, z in rz]
    if pts[0] != pts[-1]: pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), V(0, 0, 1), 360)

def cyl(r, z0, z1, x=0, y=0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def zslab(z0, z1, R=200):
    return cyl(R, z0, z1)

def thread(t, z0, length, extra_r=0.0, chamfer=True, z_ref=None):
    """External thread solid (core + ridges) occupying z0..z0+length.
    z_ref: z at which ridge 0 crosses angle 0 (phase); defaults to z0.
    extra_r > 0 grows it radially -> use as a tap for the mating internal thread.
    Built so no sweep cap / core seam / core end face coincides with anything (OCC booleans
    silently fail on those)."""
    z_ref = z0 if z_ref is None else z_ref
    d, lead, n, depth, crest = t['d'] + 2 * extra_r, t['lead'], t['starts'], t['depth'], t['crest']
    r_maj = d / 2
    r_root = r_maj - depth
    pitch = lead / n
    hr = min(crest / 2 + depth, pitch * 0.45)       # 45 deg flanks over the working depth
    x0 = r_root - 0.2
    z_h = z_ref - lead * (math.ceil((z_ref - z0) / lead) + 1)     # helix start, phase-locked to z_ref
    total = (z0 + length + lead) - z_h
    ridges = []
    for k in range(n):
        helix = Part.makeHelix(lead, total, x0)
        helix.translate(V(0, 0, z_h))
        prof = Part.makePolygon([V(x0, 0, z_h - hr), V(r_maj, 0, z_h - crest / 2),
                                 V(r_maj, 0, z_h + crest / 2), V(x0, 0, z_h + hr), V(x0, 0, z_h - hr)])
        ps = Part.BRepOffsetAPI.MakePipeShell(Part.Wire(helix))
        ps.setBiNormalMode(V(0, 0, 1))
        ps.add(Part.Wire(prof))
        ps.build(); ps.makeSolid()
        sh = ps.shape()
        sh.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 * k / n)
        ridges.append(sh)
    # trim ridges to the z-range FIRST, then fuse with a core of exactly that range
    # (fusing an over-long core with the helical sweeps makes OCC drop the core).
    # Per-ridge trim: trimming the ridges as one compound, or rotating the core, also fails.
    rtrim = [r.common(cyl(r_maj + 1, z0, z0 + length)) for r in ridges]
    th = cyl(r_root, z0, z0 + length).fuse(rtrim)
    if chamfer:   # 45 deg lead-in at both ends, cut as two conical rings (a common() with an envelope fails)
        a, R = r_root - 0.2, r_maj + 1.0
        out = th.cut([revolve([(a, z0 - 0.01), (R, z0 - 0.01), (R, z0 + R - a)]),
                      revolve([(a, z0 + length + 0.01), (R, z0 + length + 0.01), (R, z0 + length - (R - a))])])
    else:
        out = th
    v_min = math.pi * r_root ** 2 * length
    assert out.isValid() and len(out.Solids) == 1 and out.Volume > v_min,         "thread boolean failed (d=%g z0=%g): vol %.0f < %.0f, solids %d" % (d, z0, out.Volume, v_min, len(out.Solids))
    return out

def tap(t, z_mate0, zmin, zmax):
    """Cutter for the internal thread mating an external thread whose phase ref is z_mate0."""
    return thread(t, zmin, zmax - zmin, extra_r=THREAD_CLEAR, chamfer=False, z_ref=z_mate0)

def countersink(r_top, z_top, depth=0.8):
    return revolve([(0, z_top - depth - 0.01), (r_top - depth, z_top - depth - 0.01), (r_top + 0.01, z_top + 0.01), (0, z_top + 0.01)])

def hexprism(af, z0, z1, x=0, y=0):
    R = af / math.sqrt(3)
    pts = [V(x + R * math.cos(math.radians(60 * i)), y + R * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))

def dprofile(r, flat_y, z0, z1):
    return cyl(r, z0, z1).common(box(-r - 1, r + 1, -r - 1, flat_y, z0 - 1, z1 + 1))

# =====================================================================================
# PARTS
# =====================================================================================
t_start = time.time()
P = {}      # printed parts
H = {}      # hardware / reference

# ---------------- cartridge (B-rep from the same profile as the reference STL)
N = 240
prof = [(cart_r(CART_L * i / N), CART_L * i / N) for i in range(N + 1)]
prof = [(0.0, 0.0)] + prof[1:] + [(0.0, CART_L)]
cart = revolve(prof)
cart.translate(V(0, 0, Z_CB - 0.02))   # 0.02 below the seat so the check sees a gap, not a touch
H['cartridge'] = cart

# ---------------- BODY
r_bore = BORE_D / 2
r_t2root = T2['d'] / 2 - T2['depth']
body = revolve([(0, 0), (T1['d'] / 2 - T1['depth'], 0), (T1['d'] / 2 - T1['depth'], T1_LEN),
                (FLANGE_D / 2, T1_LEN), (FLANGE_D / 2, T1_LEN + FLANGE_H),
                (r_t2root, T1_LEN + FLANGE_H + 0.0), (r_t2root, Z_BODY_TOP - 2.7),
                (r_bore + 1.1, Z_BODY_TOP), (0, Z_BODY_TOP)])
body = body.fuse([thread(T1, 0.0, T1_LEN), thread(T2, Z_T2, T2_LEN)])
body = body.cut(revolve([(0, FLOOR), (r_bore, FLOOR), (r_bore, Z_BODY_TOP + 1), (0, Z_BODY_TOP + 1)]))
body = body.cut(cyl(3.2, -1, FLOOR + 1))                                          # M6 grub clearance
body = body.cut(hexprism(M6_NUT_AF + 0.3, FLOOR - M6_NUT_H - 0.2, FLOOR + 0.1))  # captive M6 nut, drop in from the bore
# flange notches: wire (+x), install-tool keys (+/-y)
fz0, fz1 = T1_LEN + 1.0, T1_LEN + FLANGE_H + 0.1
body = body.cut(box(16.6, 20, -1.75, 1.75, T1_LEN - 0.1, fz1))                   # wire notch full height
for sy in (1, -1):
    body = body.cut(box(-2.5, 2.5, 16.1 * sy if sy > 0 else -20, 20 if sy > 0 else -16.1, fz0, fz1))
assert body.isValid(), 'body invalid'
P['body'] = body

# ---------------- HEAD
r_t2tap_maj = T2['d'] / 2 + THREAD_CLEAR
r_sb = STRIKER_D / 2 + SLIDE_CLEAR          # striker bore
head = revolve([(r_t2root - 0.2, Z_SKIRT), (SKIRT_OD / 2, Z_SKIRT), (SKIRT_OD / 2, Z_BODY_TOP + 5),
                (HEAD_OD / 2, Z_BODY_TOP + 5 + (SKIRT_OD - HEAD_OD) / 2), (HEAD_OD / 2, Z_HEAD_TOP),
                (T3['d'] / 2, Z_HEAD_TOP), (r_sb, Z_CU), (r_sb, Z_STOP), (SEAT_D / 2, Z_STOP),
                (SEAT_D / 2, Z_SEAT), (r_bore, Z_SEAT - (r_bore - SEAT_D / 2)), (r_bore, Z_BODY_TOP),
                (r_bore + 1.4, Z_BODY_TOP), (r_t2tap_maj - 0.5, Z_BODY_TOP - 3.0), (r_t2root - 0.2, Z_BODY_TOP - 3.0)])
head = head.cut(tap(T2, Z_T2, Z_SKIRT - 0.5, Z_BODY_TOP - 2.7))
head = head.cut(tap(T3, Z_CU, Z_CU - 0.5, Z_HEAD_TOP + 0.5))
head = head.cut(countersink(T3['d'] / 2 + THREAD_CLEAR, Z_HEAD_TOP))
head = head.cut(revolve([(0, Z_SKIRT - 0.01), (r_t2tap_maj + 0.8, Z_SKIRT - 0.01), (r_t2tap_maj - 0.2, Z_SKIRT + 1.0), (0, Z_SKIRT + 1.0)]))
ports = []
for i in range(PORT_N):
    b = box(0, HEAD_OD, -PORT_W / 2, PORT_W / 2, PORT_Z[0], PORT_Z[1])
    b.rotate(V(0, 0, 0), V(0, 0, 1), 45 + 360.0 * i / PORT_N)
    ports.append(b)
head = head.cut(ports)
assert head.isValid(), 'head invalid'
P['head'] = head

# ---------------- CAP (threaded plug + flange; line/nichrome hardware on top)
r_tail_hole = TAIL_D / 2 + SLIDE_CLEAR
cap = thread(T3, Z_CU, T3_LEN).fuse(cyl(HEAD_OD / 2, Z_HEAD_TOP, Z_CT))
cap = cap.cut(dprofile(r_tail_hole, TAIL_FLAT + SLIDE_CLEAR, Z_CU - 1, Z_CT + 1))
cap = cap.cut(revolve([(0, Z_CT - 0.6), (r_tail_hole, Z_CT - 0.6), (r_tail_hole + 0.6, Z_CT + 0.01), (0, Z_CT + 0.01)]))  # round line edge
cap = cap.cut(box(-ANCHOR_X, ANCHOR_X, -0.6, 0.6, Z_CT - 0.6, Z_CT + 0.01))         # line groove (x), tail -> clamp screws
cap = cap.cut(box(-(r_tail_hole + 1.0), r_tail_hole + 1.0, -0.5, 0.5, Z_CU - 1, Z_CT + 1))  # release relief slots: cut line runs free
cap = cap.cut(box(TERM_XY[0] - 1.0, TERM_XY[0] + 1.0, -2.6, 2.6, Z_CT - 2.0, Z_CT + 0.01))  # air gap under nichrome
for sy in (1, -1):
    cap = cap.cut(cyl(0.85, Z_CT - 7.0, Z_CT + 1, x=TERM_XY[0], y=sy * TERM_XY[1]))  # M2 self-tap terminals
for sx in (1, -1):
    cap = cap.cut(cyl(0.85, Z_CT - 5.0, Z_CT + 1, x=sx * ANCHOR_X))                  # M2 line-clamp screws
# wrench flats on the flange so the cap can be held while the head is turned
cap = cap.cut(box(-HEAD_OD, HEAD_OD, HEAD_OD / 2 - 1.2, HEAD_OD, Z_HEAD_TOP - 0.1, Z_CT + 0.1))
cap = cap.cut(box(-HEAD_OD, HEAD_OD, -HEAD_OD, -HEAD_OD / 2 + 1.2, Z_HEAD_TOP - 0.1, Z_CT + 0.1))
assert cap.isValid(), 'cap invalid'
P['cap'] = cap

# ---------------- STRIKER + TAIL (built at u frame, then placed)
def make_striker():
    s = cyl(STRIKER_D / 2, 0, STRIKER_H)
    s = s.fuse(dprofile(TAIL_D / 2, TAIL_FLAT, STRIKER_H - 0.01, TAIL_TOP_U))
    s = s.cut(cyl(2.0, -0.01, 6.0))            # M3 heat-set insert (or tap M3 into a 2.5 pilot)
    s = s.cut(cyl(1.6, 5.9, 14.0))             # needle screw over-length
    s = s.cut(cyl(1.25, TAIL_TOP_U - 7.0, TAIL_TOP_U + 0.01))   # M3 pilot for the cocking screw
    s = s.cut(cyl(1.1, 13.9, TAIL_TOP_U - 6.9))              # 1.5 mm hex key reaches the needle set screw
    for u in CROSS_U.values():
        s = s.cut(Part.makeCylinder(CROSS_HOLE_D / 2, TAIL_D + 2, V(-TAIL_D / 2 - 1, 0, u), V(1, 0, 0)))
    return s

striker_u = make_striker()
def at_stroke(shape_u, s):
    sh = shape_u.copy(); sh.translate(V(0, 0, Z_STOP + s)); return sh
P['striker'] = at_stroke(striker_u, STROKE_DEFAULT)

# needle = M3 DIN 914 cone-point set screw, 16 long, point sharpened to 60 deg
needle_u = cyl(NEEDLE_D / 2, -NEEDLE_PROTRUSION + 2.6, 16.0 - NEEDLE_PROTRUSION).fuse(
    Part.makeCone(0.05, NEEDLE_D / 2, 2.6, V(0, 0, -NEEDLE_PROTRUSION)))
H['needle'] = at_stroke(needle_u, STROKE_DEFAULT)
JAM_NUT_H = 1.8   # M3 DIN 439 thin nut locks the needle against the striker face
jamnut_u = hexprism(5.5, -JAM_NUT_H, 0.0).cut(cyl(1.5, -3, 1))
H['jam_nut'] = at_stroke(jamnut_u, STROKE_DEFAULT)

# grub + nut
H['grub_M6x12'] = cyl(3.0, Z_CB - M6_GRUB_L, Z_CB - 0.05)
H['nut_M6'] = hexprism(M6_NUT_AF, FLOOR - M6_NUT_H, FLOOR).cut(cyl(3.0, 0, FLOOR + 1))

# spring envelope (largest accepted spring) between striker top and cap underside
SPRING_OD_MAX = STRIKER_D          # 16.0 in a 16.6 bore
SPRING_ID_MIN = TAIL_D + 0.6       # over a 6.0 tail
def spring_env(s):
    return cyl(SPRING_OD_MAX / 2, Z_STOP + s + STRIKER_H + 0.01, Z_CU - 0.01).cut(cyl(SPRING_ID_MIN / 2, 0, 400))
H['spring_envelope'] = spring_env(STROKE_DEFAULT)

# ---------------- SPACERS (print flat)
for t in SPACERS:
    P['spacer_%gmm' % t] = cyl(STRIKER_D / 2 - 0.2, 0, t).cut(cyl(TAIL_D / 2 + 0.4, -1, t + 1))

# ---------------- TEST BASE (bench stand; same interface as the flight bulkhead)
base = box(-40, 40, -40, 40, -10, -4)
base = base.fuse(cyl(AIRFRAME_OD / 2 + 3.25, -4, T1_LEN))
base = base.fuse(cyl(AIRFRAME_OD / 2 + 3.25, T1_LEN, T1_LEN + 15).cut(cyl(AIRFRAME_OD / 2 + 0.25, T1_LEN, T1_LEN + 16)))
base = base.cut(tap(T1, 0.0, -1.5, T1_LEN + 0.01))
base = base.cut(countersink(T1['d'] / 2 + THREAD_CLEAR, T1_LEN, 1.0))
base = base.cut(cyl(6.0, -8.0, -1.4))                                    # grub pocket
for sx in (1, -1):
    for sy in (1, -1):
        base = base.cut(cyl(2.75, -11, -3, x=32 * sx, y=32 * sy))        # M5 / #10 bench screws
        base = base.cut(cyl(5.0, -4.01, 12, x=32 * sx, y=32 * sy))       # screw head clearance
P['test_base'] = base

# ---------------- FLIGHT BULKHEAD (generic, bonded in the airframe)
rb = AIRFRAME_ID / 2 - 0.15
bh = cyl(rb, -7.0, T1_LEN)
bh = bh.cut(tap(T1, 0.0, -1.5, T1_LEN + 0.01))
bh = bh.cut(countersink(T1['d'] / 2 + THREAD_CLEAR, T1_LEN, 1.0))
bh = bh.cut(cyl(5.0, -5.0, -1.4))
bh = bh.cut(box(rb - 1.6, rb + 1, -1.2, 1.2, -8, T1_LEN + 1))           # wire groove at the wall (+x), epoxy-sealed
bh = bh.cut(box(-1.6, 1.6, rb - 2.0, rb + 1, -8, T1_LEN + 1))           # harness groove (+y)
bh = bh.cut(box(-1.6, 1.6, -rb - 1, -rb + 2.0, -8, T1_LEN + 1))          # harness groove (-y)
P['flight_bulkhead'] = bh

# ---------------- COCKING TOOL (bridge + M3x25 screw into the tail top)
tail_top_max = Z_STOP + max(STROKES) + TAIL_TOP_U
bar_z0 = tail_top_max + 2.0
ct = box(-4, 4, -12.5, 12.5, bar_z0, bar_z0 + 6)
for sy in (1, -1):
    ct = ct.fuse(box(-4, 4, 9.5 if sy > 0 else -12.5, 12.5 if sy > 0 else -9.5, Z_CT, bar_z0 + 0.01))
ct = ct.cut(cyl(1.7, bar_z0 - 1, bar_z0 + 7))
P['cocking_tool'] = ct
COCK_SCREW_L = (bar_z0 + 6) - (Z_STOP + TAIL_TOP_U - 6.0)

# ---------------- INSTALL TOOL (two prongs keyed into the body flange, handle ring above)
tool_top = tail_top_max + 12
ri, ro = SKIRT_OD / 2 + 0.4, AIRFRAME_ID / 2 - 0.7
itool = cyl(ro, tool_top, tool_top + 8).cut(cyl(ri, 0, 400))
for sy in (1, -1):
    wedge = cyl(ro, T1_LEN + FLANGE_H + 0.2, tool_top + 0.01).cut(cyl(ri, 0, 400))
    wedge = wedge.common(box(-ro * math.sin(math.radians(25)), ro * math.sin(math.radians(25)),
                             0 if sy > 0 else -ro - 1, ro + 1 if sy > 0 else 0, 0, 400))
    tab = box(-2.0, 2.0, 16.5 if sy > 0 else -18.0, 18.0 if sy > 0 else -16.5, T1_LEN + 1.2, T1_LEN + FLANGE_H + 0.21)
    itool = itool.fuse([wedge, tab])
P['install_tool'] = itool

# ---------------- COUPONS
gauge = P['head'].common(zslab(Z_BODY_TOP, Z_STOP))
P['coupon_seat_gauge'] = gauge
for name, t, L in (('T1', T1, 8.0), ('T2', T2, 8.0), ('T3', T3, 8.0)):
    male = thread(t, 0, L).cut(cyl(t['d'] / 2 - t['depth'] - 2.5, -1, L + 1))
    female = cyl(t['d'] / 2 + THREAD_CLEAR + 2.5, 0, L).cut(tap(t, 0, -0.01, L + 0.01))
    female = female.cut(countersink(t['d'] / 2 + THREAD_CLEAR, L, 0.8))
    P['coupon_%s_male' % name] = male
    P['coupon_%s_female' % name] = female

print("geometry built in %.1f s" % (time.time() - t_start))

# =====================================================================================
# CHECKS
# =====================================================================================
report = []
def rep(line):
    print(line); report.append(line)

rep("== T4 CO2 ejector check report ==")
rep("Key stations (module frame, z=0 aft face): cartridge base %.2f, seat %.2f, tip %.2f, stop %.2f, cap underside %.2f, cap top %.2f"
    % (Z_CB, Z_SEAT, Z_TIP, Z_STOP, Z_CU, Z_CT))
rep("Needle protrusion below striker face: %.2f mm (set with the M3 set screw)" % NEEDLE_PROTRUSION)

allvalid = True
for k, s in list(P.items()) + list(H.items()):
    v = s.isValid() and len(s.Solids) >= 1
    allvalid &= v
    if not v: rep("FAIL invalid solid: %s" % k)
rep("%s all %d solids valid" % (ok(allvalid), len(P) + len(H)))

def interference(parts, whitelist=(), tol=1e-3):
    bad = []
    keys = list(parts)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if not parts[a].BoundBox.intersect(parts[b].BoundBox): continue
            vol = parts[a].common(parts[b]).Volume
            if vol > tol and (a, b) not in whitelist and (b, a) not in whitelist:
                bb = parts[a].common(parts[b]).BoundBox
                bad.append((a, b, round(vol, 3), "z %.1f-%.1f" % (bb.ZMin, bb.ZMax)))
    return bad

for s in STROKES:
    for state, zs in (("cocked", s), ("fired", 0.0)):
        parts = dict(body=P['body'], head=P['head'], cap=P['cap'], striker=at_stroke(striker_u, zs),
                     needle=at_stroke(needle_u, zs), jam_nut=at_stroke(jamnut_u, zs), cartridge=H['cartridge'], grub=H['grub_M6x12'],
                     nut=H['nut_M6'], spring=spring_env(zs), base=P['test_base'])
        wl = [('needle', 'cartridge')] if state == "fired" else []
        bad = interference(parts, wl)
        rep("%s interference, stroke %g, %s: %s" % (ok(not bad), s, state, "none" if not bad else
            ", ".join("%s/%s %s mm3 @%s" % b for b in bad)))
        if state == "fired" and s == STROKES[0]:
            pen = parts['needle'].common(H['cartridge'])
            rep("%s needle penetrates cartridge at end of stroke (overlap %.2f mm3)" % (ok(pen.Volume > 0.1), pen.Volume))
    free_run = s - PENETRATION
    rep("%s stroke %g: free run before contact %.1f mm, cross-hole u=%.2f" % (ok(free_run > 0.5), s, free_run, CROSS_U[s]))

for name in ('T1', 'T2', 'T3'):
    v = P['coupon_%s_male' % name].common(P['coupon_%s_female' % name]).Volume
    rep("%s thread coupon %s male/female mesh without overlap (%.3f mm3)" % (ok(v < 1e-3), name, v))
def engagement(male, female, t, z0, z1):
    """Point-sample the mid-flank radius: fraction of points inside the male ridges, inside the
    female ridges, and inside both (must be 0). Sampling, not booleans: thin-ring common()
    silently returns 0 on helical faces."""
    r = t['d'] / 2 - t['depth'] / 2 + THREAD_CLEAR / 2
    band = cyl(t['d'] / 2 + 1.5, z0 - 0.5, z1 + 0.5).cut(cyl(t['d'] / 2 - t['depth'] - 0.5, z0 - 1, z1 + 1))
    male, female = male.common(band), female.common(band)     # crop: isInside is slow on whole parts
    nm = nf = nb = tot = 0
    for ia in range(0, 360, 30):
        a = math.radians(ia)
        z = z0
        while z <= z1:
            p = V(r * math.cos(a), r * math.sin(a), z)
            im, iff = male.isInside(p, 1e-4, True), female.isInside(p, 1e-4, True)
            nm += im; nf += iff; nb += im and iff; tot += 1
            z += 0.2
    return nm / tot, nf / tot, nb / tot
for name, t, m, f, z0, z1 in (('T1 coupon', T1, P['coupon_T1_male'], P['coupon_T1_female'], 2, 6),
                              ('T2 coupon', T2, P['coupon_T2_male'], P['coupon_T2_female'], 2, 6),
                              ('T3 coupon', T3, P['coupon_T3_male'], P['coupon_T3_female'], 2, 6),
                              ('T1 body/base', T1, P['body'], P['test_base'], 2, 8),
                              ('T1 body/bulkhead', T1, P['body'], P['flight_bulkhead'], 2, 8),
                              ('T2 body/head', T2, P['body'], P['head'], Z_T2 + 2, Z_T2 + T2_LEN - 2),
                              ('T3 cap/head', T3, P['cap'], P['head'], Z_CU + 1.5, Z_CU + T3_LEN - 1.5)):
    em, ef, eb = engagement(m, f, t, z0, z1)
    rep("%s %s thread engagement at mid-flank: male %.0f%%, female %.0f%%, both %.1f%%" % (ok(em > 0.2 and ef > 0.2 and eb == 0), name, 100 * em, 100 * ef, 100 * eb))
# install tool / cocking tool / flight bulkhead fits
mod = dict(body=P['body'], head=P['head'], cap=P['cap'], striker=P['striker'], needle=H['needle'], cartridge=H['cartridge'])
for tool in ('install_tool', 'cocking_tool'):
    bad = interference(dict(mod, **{tool: P[tool]}))
    rep("%s %s clears module: %s" % (ok(not bad), tool, bad or "yes"))
bad = interference(dict(body=P['body'], grub=H['grub_M6x12'], bulkhead=P['flight_bulkhead']))
rep("%s flight bulkhead clears module: %s" % (ok(not bad), bad or "yes"))
rep("%s install tool fits airframe bore (OD %.1f < ID %.1f)" % (ok(2 * ro < AIRFRAME_ID - 0.5), 2 * ro, AIRFRAME_ID))
rep("%s module max OD %.1f fits airframe ID %.1f" % (ok(max(FLANGE_D, SKIRT_OD) < AIRFRAME_ID - 2), max(FLANGE_D, SKIRT_OD), AIRFRAME_ID))

# keys actually engage
tabs_in_notch = P['install_tool'].common(zslab(T1_LEN + 1.2, T1_LEN + FLANGE_H)).Volume
rep("%s install-tool tabs reach into flange notches (tab volume below flange top %.1f mm3)" % (ok(tabs_in_notch > 10), tabs_in_notch))

for sx in (1, -1):
    under = P['cap'].common(cyl(2.5, Z_CT - 3.0, Z_CT - 0.01, x=sx * ANCHOR_X)).Volume
    full = math.pi * 2.5 ** 2 * 2.99 - math.pi * 0.85 ** 2 * 2.99
    rep("%s line clamp at x=%+.1f has solid material under its washer (%.0f%% of annulus)" % (ok(under > 0.9 * full), sx * ANCHOR_X, 100 * under / full))
jn_gap = at_stroke(jamnut_u, 0.0).distToShape(H['cartridge'])[0]
rep("%s jam nut clears cartridge tip at end of stroke (%.2f mm)" % (ok(jn_gap > 0.4), jn_gap))
key = cyl(0.7, Z_STOP + STROKE_DEFAULT + 14.5, Z_STOP + STROKE_DEFAULT + TAIL_TOP_U + 1)
rep("%s hex-key path from tail top to needle socket is open" % ok(P['striker'].common(key).Volume < 1e-6))
slot = box(3.5, 4.1, -0.3, 0.3, Z_CU - 0.5, Z_CT + 0.5)
rep("%s release relief slots open through the cap" % ok(P['cap'].common(slot).Volume < 1e-6 and P['cap'].common(slot.mirror(V(0,0,0), V(1,0,0))).Volume < 1e-6))
# pass-throughs really exist (probe a thin rod along each path)
probe_tail = cyl(0.5, Z_CU - 2, Z_CT + 2)
rep("%s tail passage through cap is open" % ok(P['cap'].common(probe_tail).Volume < 1e-6))
probe_needle = cyl(0.5, Z_TIP + 0.5, Z_STOP + 1)
rep("%s needle path head plenum open" % ok(P['head'].common(probe_needle).Volume < 1e-6))
for s, u in CROSS_U.items():
    rod = Part.makeCylinder(0.3, 10, V(-5, 0, Z_STOP + u), V(1, 0, 0))
    rep("%s cross-hole for stroke %g is through" % (ok(striker_u.translated(V(0, 0, Z_STOP)).common(rod).Volume < 1e-6), s))
port_probe = Part.makeCylinder(0.5, 20, V(0, 0, sum(PORT_Z) / 2), V(math.cos(math.radians(45)), math.sin(math.radians(45)), 0))
rep("%s vent port open from plenum to outside" % ok(P['head'].common(port_probe).Volume < 1e-6))

# cartridge seat & bore
seat_gap = P['head'].distToShape(H['cartridge'])[0]
rep("%s cartridge seats on head seat edge (gap %.3f mm, modelled 0.02 low)" % (ok(seat_gap < 0.1), seat_gap))
bore_gap = P['body'].distToShape(H['cartridge'].common(zslab(Z_CB + 10, Z_CB + 40)))[0]
rep("%s cartridge body radial clearance %.2f mm" % (ok(0.2 < bore_gap < 0.8), bore_gap))

# vent ratio
port_area = PORT_N * PORT_W * (PORT_Z[1] - PORT_Z[0])
hole_area = math.pi * PIERCE_HOLE_D ** 2 / 4
rep("%s vent area %.0f mm2 = %.0fx a %.1f mm pierce hole (need >= 20x)" % (ok(port_area / hole_area >= 20), port_area, port_area / hole_area, PIERCE_HOLE_D))

# spring envelope
cav_f = SPRING_CAVITY_FIRED
rep("Spring envelope: OD <= %.1f, ID >= %.1f, cavity fired %.1f, cocked %s (minus spacers/washers)"
    % (SPRING_OD_MAX, SPRING_ID_MIN, cav_f, ", ".join("%.0f@s=%g" % (cav_f - s, s) for s in STROKES)))
rep("%s spring bore (%.1f) > spring OD max (%.1f) + 0.4" % (ok(2 * r_sb >= SPRING_OD_MAX + 0.4), 2 * r_sb, SPRING_OD_MAX))

# min wall checks (thin spots that commonly bite)
walls = {
    'body wall at T2 root': r_t2root - r_bore,
    'head skirt over T2 tap': SKIRT_OD / 2 - r_t2tap_maj,
    'head wall over T3 tap': HEAD_OD / 2 - (T3['d'] / 2 + THREAD_CLEAR),
    'head wall at striker bore': HEAD_OD / 2 - r_sb,
    'body floor under nut': FLOOR - M6_NUT_H - 0.2,
    'tail web between cross-holes': min(abs(a - b) for a in CROSS_U.values() for b in CROSS_U.values() if a != b) - CROSS_HOLE_D,
}
for k, w in walls.items():
    rep("%s %s = %.2f mm" % (ok(w >= 1.2), k, w))

# masses (PETG 1.27 g/cc)
rho = 1.27e-3
mod_parts = ['body', 'head', 'cap', 'striker']
mass = {k: P[k].Volume * rho for k in mod_parts}
rep("Printed masses (PETG, solid): " + ", ".join("%s %.1f g" % (k, m) for k, m in mass.items()))
rep("Module length (aft face -> cap top %.1f, -> tail top cocked %.1f)" % (Z_CT, Z_STOP + STROKE_DEFAULT + TAIL_TOP_U))
rep("Module loaded mass est: printed %.0f g + cartridge 28 g + hardware ~6 g + spring ~3-8 g = ~%.0f g"
    % (sum(mass.values()), sum(mass.values()) + 28 + 6 + 5))
rep("Cocking screw: M3 x %.0f (or longer)" % math.ceil(COCK_SCREW_L))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(OUT_PRINT, exist_ok=True)
doc = App.newDocument("CO2_Ejector_T4")
for k, s in P.items():
    o = doc.addObject("Part::Feature", k); o.Shape = s
for k, s in H.items():
    o = doc.addObject("Part::Feature", "HW_" + k); o.Shape = s
if os.path.exists(REF_STL):
    m = Mesh.Mesh(REF_STL); m.translate(0, 0, Z_CB)
    mo = doc.addObject("Mesh::Feature", "REF_cartridge_stl"); mo.Mesh = m
doc.recompute()
doc.saveAs(os.path.join(OUT_MODELS, "co2_ejector_t4.FCStd"))

asm = Part.makeCompound([P[k] for k in ('body', 'head', 'cap', 'striker', 'test_base')] +
                        [H[k] for k in ('needle', 'jam_nut', 'grub_M6x12', 'nut_M6', 'cartridge')])
asm.exportStep(os.path.join(OUT_MODELS, "co2_ejector_t4_assembly_cocked.step"))

def to_print(k, s):
    s = s.copy()
    if k == 'install_tool':
        s.rotate(V(0, 0, 0), V(1, 0, 0), 180)       # handle ring on the bed
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return s

for k, s in P.items():
    ps = to_print(k, s)
    mesh = MeshPart.meshFromShape(Shape=ps, LinearDeflection=0.02, AngularDeflection=0.3, Relative=False)
    mesh.write(os.path.join(OUT_PRINT, "t4_%s.stl" % k))
    ps.exportStep(os.path.join(OUT_MODELS, "step_%s.step" % k)) if k in ('body', 'head', 'cap', 'striker') else None

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 16))
    cols = dict(jam_nut='m', body='tab:blue', head='tab:orange', cap='tab:green', striker='tab:red', test_base='0.5',
                cartridge='k', needle='m', grub_M6x12='tab:brown', nut_M6='tab:brown')
    shapes = dict(P, **H)
    for k, c in cols.items():
        for e in shapes[k].slice(V(0, 1, 0), 0.0):
            pts = e.discretize(Deflection=0.02)
            ax.plot([p.x for p in pts], [p.z for p in pts], color=c, lw=0.6)
    ax.set_aspect('equal'); ax.set_title('T4 CO2 ejector, section y=0, cocked s=%g' % STROKE_DEFAULT)
    ax.grid(alpha=0.2)
    fig.savefig(os.path.join(OUT_MODELS, "section_cocked.png"), dpi=160, bbox_inches='tight')
except Exception as ex:
    print("section plot skipped:", ex)
with open(os.path.join(OUT_MODELS, "check_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t_start))

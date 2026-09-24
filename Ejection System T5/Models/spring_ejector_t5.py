# -*- coding: utf-8 -*-
"""
T5 spring-piston ejector with nichrome line release, front-removable module.

Phoenix ABS 40-43 (40 ID / 43 OD). Implements DESIGN.md sec 7 (spring piston, sole deployment)
with the servo/cam latch replaced by a Dyneema line loop cut by a nichrome coil.

Run headless (regenerates everything):
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"

Frame: axis +Z = forward (toward the nose). z = 0 is the module's aft face (the open face of
the release chamber, which faces the e-bay). Parts are modelled at the COCKED state.
Thread helpers are copied verbatim from T4 (co2_ejector_t4.py), where they were debugged.
Any FAIL line in the report means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, Mesh, MeshPart

V = App.Vector
ROOT = r"C:\Users\dick_\Documents\Rocketry\Ejection System T5"
OUT_MODELS = os.path.join(ROOT, "Models")
OUT_PRINT = os.path.join(ROOT, "Print Files")

# =====================================================================================
# PARAMETERS
# =====================================================================================
AIRFRAME_ID, AIRFRAME_OD = 40.0, 43.0
R_MOVING_MAX, R_STATIC_MAX = 19.5, 19.85       # Phoenix envelope (ejection POC report)

# Spring as procured (DESIGN.md 7.2): 10 OD, 85 free, 45 cocked -> 40 stroke. Rate unmeasured.
SPRING_OD, SPRING_FREE, SPRING_COCKED = 10.0, 85.0, 45.0
SPRING_OD_MAX = 11.0            # largest spring the seats accept
F_MAX_DESIGN = 52.7             # N: stiffest row of DESIGN 7.2 (1.3 mm wire), until 7.3 is measured
PROOF_FACTOR = 4.0              # DESIGN 7.9 test 3
STROKE = SPRING_FREE - SPRING_COCKED
TETHER_SLACK = 1.5              # piston tether goes taut this far past full stroke

THREAD_CLEAR = 0.30
T1 = dict(d=34.0, lead=9.0, starts=3, depth=1.2, crest=0.3)   # identical to T4 T1
T1_LEN = 10.0
FLANGE_D, FLANGE_H = 36.5, 4.0

# Release chamber (inside the threaded spigot, open aft)
CHAMBER_R, CHAMBER_H = 13.0, 6.0
LEG_X = 8.0                     # line legs at (+/-LEG_X, 0)
LINE_HOLE_D = 2.0               # takes 0.3 - 0.5 mm Dyneema
TETHER_XY = (0.0, 11.0)
TERM_XY = (9.8, -3.8)           # M2 nichrome terminals at (+/-x, y); one strand spans between them
CLAMP_XY = (6.0, -8.5)          # M2 line clamps at (+/-x, y), line wrapped round the shank
# Each leg runs STRAIGHT from its hole to its clamp; the strand crosses both runs at y = TERM_XY[1]
# and is wound 2-3 turns round each leg there (two coils in series). The coil carries no line load.
M2_HEAD_R, M2_HEAD_H = 1.9, 2.0

# Guide rod: M5 x 40 hex bolt (DIN 933), head captured in the chamber ceiling
ROD_D, ROD_HEAD_AF, ROD_HEAD_H, ROD_LEN = 5.0, 8.0, 3.5, 40.0

# Piston (cup with skirt so it cannot cock in the bore)
PISTON_D = 38.5
PLATE_H, SKIRT_H, SKIRT_T = 8.0, 12.0, 2.05
PISTON_CB_D, PISTON_CB_H = 11.4, 3.0       # captures the spring's top end
SEAT_CB_D, SEAT_CB_H = 11.4, 2.0           # captures the spring's bottom end (in the base)

# Remove-before-flight / bench cocking pin: diametral, through the airframe, above the piston
PIN_D, PIN_GAP = 4.0, 1.5
SETTLE = 0.7                    # piston rise when the line takes the load (slack + Dyneema stretch)
LOCK_DZ = 10.0                  # bench lock-pin height above the RBF pin (same pin, holes along y)
LOCK_HOLE_DZ = 0.08             # tool lock hole centre above the pin: 0.02 running clearance, locked face = nominal + 0.04
CLOCK_TOL_DEG = 25.0            # seated-angle uncertainty of the T1 joint (0.6 mm axial play / 9 mm lead)
PISTON_FLAT = 16.0              # piston flats at y = +/-16 (tool prongs + harness pass)
HARNESS_T = 1.5                 # Kevlar harness thickness
PIN_YIELD_MPA = 1000.0          # hardened dowel / silver steel; mild steel ~250 -> use d5

# Install tool
TOOL_LEN = 150.0

# =====================================================================================
# DERIVED
# =====================================================================================
Z_TOP_BASE = T1_LEN + FLANGE_H                        # 14: flange top = base top
Z_SEAT = Z_TOP_BASE - SEAT_CB_H                       # 12: spring bottom
Z_PU_C = Z_SEAT + SPRING_COCKED - PISTON_CB_H         # piston underside, cocked
Z_PU_F = Z_PU_C + STROKE
Z_TOP_C = Z_PU_C + PLATE_H                            # piston top, cocked
Z_PIN = Z_TOP_C + PIN_GAP + PIN_D / 2
Z_LOCK = Z_PIN + LOCK_DZ
Z_TUNNEL = Z_PU_C + PISTON_CB_H + 1.2 + LINE_HOLE_D / 2
Z_ROD_HEAD = CHAMBER_H                                # head end flush with the chamber ceiling
Z_ROD_TOP = Z_ROD_HEAD + ROD_HEAD_H + ROD_LEN
PHOENIX_PISTON_TOP_STATION = 110.0                    # DESIGN 7.8: canopy 20-110, piston 110-118
def station(z): return PHOENIX_PISTON_TOP_STATION + (Z_TOP_C - z)

def ok(b): return "PASS" if b else "FAIL"

# =====================================================================================
# HELPERS (verbatim from T4)
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



def engagement(male, female, t, z0, z1):
    """Point-sample mid-flank radius (T4). Booleans on thin helical rings silently return 0."""
    r = t['d'] / 2 - t['depth'] / 2 + THREAD_CLEAR / 2
    band = cyl(t['d'] / 2 + 1.5, z0 - 0.5, z1 + 0.5).cut(cyl(t['d'] / 2 - t['depth'] - 0.5, z0 - 1, z1 + 1))
    male, female = male.common(band), female.common(band)
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

def xcyl(r, x0, x1, y=0, z=0):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))

def mirror_x(pt): return (-pt[0], pt[1])

# =====================================================================================
# PARTS
# =====================================================================================
t0 = time.time()
P, H = {}, {}

# ---------------- MODULE BASE: threaded spigot + flange, release chamber inside, spring seat on top
base = cyl(T1['d'] / 2 - T1['depth'], 0, T1_LEN).fuse(thread(T1, 0.0, T1_LEN))
base = base.fuse(cyl(FLANGE_D / 2, T1_LEN, Z_TOP_BASE))
base = base.cut(cyl(CHAMBER_R, -0.01, CHAMBER_H))                                   # release chamber
base = base.cut(hexprism(ROD_HEAD_AF + 0.3, CHAMBER_H - 0.01, CHAMBER_H + ROD_HEAD_H + 0.2))  # rod head, anti-rotation
base = base.cut(cyl(4.3 / 2, CHAMBER_H, Z_TOP_BASE + 0.01))                         # M5 self-taps (add a drop of CA)
base = base.cut(cyl(SEAT_CB_D / 2, Z_SEAT, Z_TOP_BASE + 0.01))                      # spring seat
for sx in (1, -1):
    x = sx * LEG_X
    base = base.cut(cyl(LINE_HOLE_D / 2, CHAMBER_H - 0.01, Z_TOP_BASE + 0.01, x=x))
    base = base.cut(Part.makeCone(LINE_HOLE_D / 2 + 0.6, LINE_HOLE_D / 2, 0.6, V(x, 0, CHAMBER_H - 0.01)))   # round the bend edges
    base = base.cut(Part.makeCone(LINE_HOLE_D / 2, LINE_HOLE_D / 2 + 0.6, 0.6, V(x, 0, Z_TOP_BASE - 0.59)))
    base = base.cut(cyl(0.85, CHAMBER_H - 0.01, CHAMBER_H + 6.0, x=sx * TERM_XY[0], y=TERM_XY[1]))      # terminals
    base = base.cut(cyl(0.85, CHAMBER_H - 0.01, CHAMBER_H + 6.0, x=sx * CLAMP_XY[0], y=CLAMP_XY[1]))    # clamps
base = base.cut(cyl(1.1, CHAMBER_H - 0.01, Z_TOP_BASE + 0.01, x=TETHER_XY[0], y=TETHER_XY[1]))          # piston tether
base = base.cut(box(-TERM_XY[0] + 1.0, TERM_XY[0] - 1.0, TERM_XY[1] - 1.5, TERM_XY[1] + 1.5, CHAMBER_H - 0.01, CHAMBER_H + 1.5))  # air gap under the whole heated span
for sy in (1, -1):   # install-tool key notches in the flange (+/-y)
    base = base.cut(box(-2.5, 2.5, 16.1 if sy > 0 else -20, 20 if sy > 0 else -16.1, T1_LEN + 1.0, Z_TOP_BASE + 0.1))
assert base.isValid()
P['base'] = base

# ---------------- PISTON (cup with skirt; line tunnel; tether hole; tool notches)
def make_piston(zpu):
    p = cyl(PISTON_D / 2, zpu, zpu + PLATE_H)
    p = p.fuse(cyl(PISTON_D / 2, zpu - SKIRT_H, zpu + 0.01).cut(cyl(PISTON_D / 2 - SKIRT_T, zpu - SKIRT_H - 1, zpu + 0.02)))
    p = p.cut(cyl(PISTON_CB_D / 2, zpu - 0.01, zpu + PISTON_CB_H))
    zt = zpu + PISTON_CB_H + 1.2 + LINE_HOLE_D / 2
    p = p.cut(xcyl(LINE_HOLE_D / 2, -LEG_X, LEG_X, z=zt))
    for sx in (1, -1):
        p = p.cut(cyl(LINE_HOLE_D / 2, zpu - 0.01, zt, x=sx * LEG_X))
        p = p.cut(Part.makeCone(LINE_HOLE_D / 2 + 0.6, LINE_HOLE_D / 2, 0.6, V(sx * LEG_X, 0, zpu - 0.01)))
        p = p.cut(Part.makeSphere(LINE_HOLE_D / 2, V(sx * LEG_X, 0, zt)))        # round the leg/tunnel corner
    p = p.cut(cyl(1.1, zpu - 0.01, zpu + PLATE_H + 0.01, x=TETHER_XY[0], y=TETHER_XY[1]))
    p = p.cut(cyl(2.5, zpu + PLATE_H - 2.0, zpu + PLATE_H + 0.01, x=TETHER_XY[0], y=TETHER_XY[1]))   # knot recess
    for sy in (1, -1):
        # flats at y = +/-PISTON_FLAT: tool prongs and the recovery harness pass here at any seated angle
        p = p.cut(box(-21, 21, PISTON_FLAT if sy > 0 else -21, 21 if sy > 0 else -PISTON_FLAT, zpu - SKIRT_H - 1, zpu + PLATE_H + 1))
    return p
piston_c = make_piston(Z_PU_C)
assert piston_c.isValid()
P['piston'] = piston_c
piston_f = make_piston(Z_PU_F)

# ---------------- hardware models
rod = hexprism(ROD_HEAD_AF, Z_ROD_HEAD, Z_ROD_HEAD + ROD_HEAD_H).fuse(cyl(ROD_D / 2, Z_ROD_HEAD + ROD_HEAD_H, Z_ROD_TOP))
H['rod_M5x40'] = rod
def spring_env(zpu, od=SPRING_OD_MAX):
    return cyl(od / 2, Z_SEAT + 0.01, zpu + PISTON_CB_H - 0.01).cut(cyl(ROD_D / 2 + 0.5, 0, 400))
H['spring_envelope'] = spring_env(Z_PU_C)
pin = xcyl(PIN_D / 2, -AIRFRAME_OD / 2 - 3, AIRFRAME_OD / 2 + 3, z=Z_PIN)
H['rbf_pin'] = pin
lock_pin = Part.makeCylinder(PIN_D / 2, AIRFRAME_OD + 6, V(0, -AIRFRAME_OD / 2 - 3, Z_LOCK), V(0, 1, 0))
heads = {}
for sx in (1, -1):
    heads['term%+d' % sx] = cyl(M2_HEAD_R, CHAMBER_H - M2_HEAD_H, CHAMBER_H - 0.01, x=sx * TERM_XY[0], y=TERM_XY[1])
    heads['clamp%+d' % sx] = cyl(M2_HEAD_R, CHAMBER_H - M2_HEAD_H, CHAMBER_H - 0.01, x=sx * CLAMP_XY[0], y=CLAMP_XY[1])
for k, v in heads.items(): H['M2_' + k] = v
Z_LINE_CH = CHAMBER_H - 0.3          # line lies against the chamber ceiling
def coil_pt(sx):
    t = (0 - TERM_XY[1]) / (0 - CLAMP_XY[1])          # fraction along hole -> clamp where y = TERM y
    return (sx * (LEG_X + t * (CLAMP_XY[0] - LEG_X)), TERM_XY[1])
def chamber_runs(r=0.2):   # hole -> clamp (stops at the clamp head), both sides
    out = []
    for sx in (1, -1):
        h = V(sx * LEG_X, 0, Z_LINE_CH); c = V(sx * CLAMP_XY[0], CLAMP_XY[1], Z_LINE_CH)
        d = c - h; L = d.Length; d.normalize()
        out.append(Part.makeCylinder(r, L - M2_HEAD_R - 0.3, h, d))
    return out
def line_path(zpu):   # the loop centreline: chamber runs, legs, piston tunnel
    zt = zpu + PISTON_CB_H + 1.2 + LINE_HOLE_D / 2
    legs = [cyl(0.2, Z_LINE_CH, zt, x=sx * LEG_X) for sx in (1, -1)]
    return Part.makeCompound(legs + [xcyl(0.2, -LEG_X, LEG_X, z=zt)] + chamber_runs())
HEATSINK = 0.5                   # first 0.5 mm past each steel head stays cool (heat-sunk)
_n0, _n1 = V(TERM_XY[0] - M2_HEAD_R - HEATSINK, TERM_XY[1], CHAMBER_H - 0.2), V(-TERM_XY[0] + M2_HEAD_R + HEATSINK, TERM_XY[1], CHAMBER_H - 0.2)
nichrome = Part.makeCylinder(0.1, (_n1 - _n0).Length, _n0, _n1 - _n0)

# ---------------- SPACERS for other springs (stack on the seat)
for t in (2.0, 4.0, 8.0):
    P['spacer_%gmm' % t] = cyl(SEAT_CB_D / 2 - 0.2, 0, t).cut(cyl(ROD_D / 2 + 0.4, -1, t + 1))

# ---------------- FLIGHT BULKHEAD (bonded ring; open centre: leads pass straight to the e-bay)
rb = R_STATIC_MAX
bh = cyl(rb, -3.5, T1_LEN).cut(tap(T1, 0.0, -1.5, T1_LEN + 0.01))
bh = bh.cut(countersink(T1['d'] / 2 + THREAD_CLEAR, T1_LEN, 1.0))
bh = bh.cut(cyl(14.0, -4, 0))
bh = bh.cut(box(-1.5, 1.5, rb - 1.6, rb + 1, -5, T1_LEN + 1))    # harness grooves at the wall, +/-y (under the piston
bh = bh.cut(box(-1.5, 1.5, -rb - 1, -rb + 1.6, -5, T1_LEN + 1))  # notches): the harness loads the bonded ring, never the thread
assert bh.isValid()
P['flight_bulkhead'] = bh

# ---------------- TEST STAND (same thread; chamber reachable from the sides; socket for a bay stub)
st = cyl(AIRFRAME_OD / 2 + 3.25, -4.0, T1_LEN).cut(tap(T1, 0.0, -1.5, T1_LEN + 0.01))
st = st.cut(countersink(T1['d'] / 2 + THREAD_CLEAR, T1_LEN, 1.0))
st = st.cut(cyl(14.0, -5, 0))
stand_top = Z_LOCK + 20
st = st.fuse(cyl(AIRFRAME_ID / 2 + 2.1, T1_LEN - 0.01, stand_top).cut(cyl(AIRFRAME_ID / 2 + 0.1, T1_LEN - 1, stand_top + 1)))  # bay tube; a nose fits its top
st = st.cut(xcyl(PIN_D / 2 + 0.15, -30, 30, z=Z_PIN))                                            # RBF pin holes (x)
st = st.cut(Part.makeCylinder(PIN_D / 2 + 0.15, 60, V(0, -30, Z_LOCK), V(0, 1, 0)))                 # bench lock-pin holes (y)
for a in (45, 135, 225, 315):
    c, s_ = math.cos(math.radians(a)) * 20.5, math.sin(math.radians(a)) * 20.5
    st = st.fuse(box(c - 4, c + 4, s_ - 4, s_ + 4, -44.0, -3.9))
foot = box(-35, 35, -35, 35, -50, -43.9).cut(cyl(12, -51, -40))
for sx in (1, -1):
    for sy in (1, -1):
        foot = foot.cut(cyl(2.75, -51, -40, x=29 * sx, y=29 * sy))
st = st.fuse(foot)
assert st.isValid()
P['test_stand'] = st

# ---------------- INSTALL / COCKING TOOL (face pushes the piston; prongs reach the flange keys; slots clear the pin)
ri, ro = 16.6, 18.8
tz0 = Z_TOP_C + 0.02
tool = cyl(ro, tz0, tz0 + TOOL_LEN).cut(cyl(ri, 0, 500))
tool = tool.fuse(cyl(ro, tz0 + TOOL_LEN, tz0 + TOOL_LEN + 8).cut(cyl(ri - 4, 0, 500)))
for sy in (1, -1):
    tool = tool.fuse(box(-2.0, 2.0, 16.7 if sy > 0 else -18.1, 18.1 if sy > 0 else -16.7, T1_LEN + 1.2, tz0 + 0.5))
tool = tool.cut(Part.makeCylinder(PIN_D / 2 + 0.1, 60, V(0, -30, Z_LOCK + LOCK_HOLE_DZ), V(0, 1, 0)))   # lock-pin holes: hold the face at nominal
for sx in (1, -1):
    tool = tool.cut(box(15 if sx > 0 else -20, 20 if sx > 0 else -15, -PIN_D / 2 - 0.6, PIN_D / 2 + 0.6, tz0 - 1, Z_PIN + PIN_D / 2 + 2.5))
assert tool.isValid()
P['install_tool'] = tool

# ---------------- COUPON
P['coupon_T1_male'] = thread(T1, 0, 8.0).cut(cyl(T1['d'] / 2 - T1['depth'] - 2.5, -1, 9))
P['coupon_T1_female'] = cyl(T1['d'] / 2 + THREAD_CLEAR + 2.5, 0, 8.0).cut(tap(T1, 0, -0.01, 8.01)).cut(countersink(T1['d'] / 2 + THREAD_CLEAR, 8.0, 0.8))
print("geometry built in %.1f s" % (time.time() - t0))

# =====================================================================================
# CHECKS
# =====================================================================================
report = []
def rep(s): print(s); report.append(s)
rep("== T5 spring-piston ejector check report ==")
rep("Stations (module z -> Phoenix station): bulkhead bottom z -3.5 -> %.1f, aft face z 0 -> %.1f, flange top z %.0f -> %.1f, piston top cocked z %.1f -> %.1f, RBF pin z %.1f -> %.1f"
    % (station(-3.5), station(0), Z_TOP_BASE, station(Z_TOP_BASE), Z_TOP_C, station(Z_TOP_C), Z_PIN, station(Z_PIN)))

v = all(s.isValid() and len(s.Solids) >= 1 for s in list(P.values()) + [rod, pin])
rep("%s all printed solids and hardware valid" % ok(v))

def interference(parts, wl=()):
    bad = []
    ks = list(parts)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            if not parts[a].BoundBox.intersect(parts[b].BoundBox): continue
            c = parts[a].common(parts[b])
            if c.Volume > 1e-3 and (a, b) not in wl and (b, a) not in wl:
                bad.append((a, b, round(c.Volume, 3)))
    return bad

core = dict(base=P['base'], rod=rod, **{'M2_' + k: v for k, v in heads.items()})
states = {
    'flight cocked (pin in)': dict(core, piston=piston_c, spring=spring_env(Z_PU_C), bulkhead=P['flight_bulkhead'], pin=pin),
    'flight fired': dict(core, piston=piston_f, spring=spring_env(Z_PU_F), bulkhead=P['flight_bulkhead']),
    'bench cocking (stand, tool held by lock pin)': dict(core, piston=piston_c, spring=spring_env(Z_PU_C), stand=P['test_stand'], lock=lock_pin, tool=P['install_tool']),
    'bench cocked (stand, RBF pin)': dict(core, piston=piston_c, spring=spring_env(Z_PU_C), stand=P['test_stand'], pin=pin),
}
# The M5 rod self-taps into a 4.3 pilot: that overlap is the thread engagement. Whitelist it,
# but prove it is confined to the pilot bore (r <= 2.5, above the head pocket, below the seat).
ov = P['base'].common(rod)
bb = ov.BoundBox
conf = max(abs(bb.XMin), abs(bb.XMax), abs(bb.YMin), abs(bb.YMax)) <= ROD_D / 2 + 0.01 and bb.ZMin >= Z_ROD_HEAD + ROD_HEAD_H - 0.01 and bb.ZMax <= Z_TOP_BASE + 0.01
rep("%s rod/base overlap is only the M5 self-tap engagement (%.1f mm3, z %.1f-%.1f)" % (ok(conf), ov.Volume, bb.ZMin, bb.ZMax))
for name, parts in states.items():
    bad = interference(parts, wl=[('base', 'rod')])
    rep("%s interference, %s: %s" % (ok(not bad), name, bad or "none"))
tool_f = P['install_tool'].translated(V(0, 0, Z_PU_F - Z_PU_C))
bad = interference(dict(piston=piston_f, tool=tool_f, base=P['base'], rod=rod), wl=[('base', 'rod')])
rep("%s install tool slides through piston notches at the fired position: %s" % (ok(not bad), bad or "yes"))
tabs = P['install_tool'].common(zslab(T1_LEN + 1.0, Z_TOP_BASE)).Volume
rep("%s tool prongs reach the flange key notches when the face is on the cocked piston (%.1f mm3 in notches)" % (ok(tabs > 10), tabs))

# envelopes
rep("%s piston running radius %.2f <= %.2f" % (ok(PISTON_D / 2 <= R_MOVING_MAX), PISTON_D / 2, R_MOVING_MAX))
rep("%s static radii: bulkhead %.2f, flange %.2f <= %.2f" % (ok(rb <= R_STATIC_MAX and FLANGE_D / 2 <= R_STATIC_MAX), rb, FLANGE_D / 2, R_STATIC_MAX))
rep("%s piston skirt L/D = %.2f (>= 0.5, anti-cocking)" % (ok((PLATE_H + SKIRT_H) / PISTON_D >= 0.5), (PLATE_H + SKIRT_H) / PISTON_D))

# spring
L_c = Z_PU_C + PISTON_CB_H - Z_SEAT
L_f = Z_PU_F + PISTON_CB_H - Z_SEAT
rep("%s spring length cocked %.2f (= %.0f), end of stroke %.2f (<= free %.0f)" % (ok(abs(L_c - SPRING_COCKED) < 1e-6 and L_f <= SPRING_FREE + 1e-6), L_c, SPRING_COCKED, L_f, SPRING_FREE))
guided = (Z_ROD_TOP - Z_SEAT) + PISTON_CB_H
rep("%s spring guided over %.1f of %.0f mm cocked (rod + piston counterbore), unguided gap %.1f mm" % (ok(guided / L_c >= 0.85), guided, L_c, L_c - guided))
rep("%s rod top clears piston underside when cocked by %.1f mm" % (ok(Z_PU_C - Z_ROD_TOP >= 2), Z_PU_C - Z_ROD_TOP))
rep("Stroke stop: Kevlar tether, taut at %.1f mm (stroke %.0f + %.1f). Cut to length on the bench (README)." % (STROKE + TETHER_SLACK, STROKE, TETHER_SLACK))

# line path
lp_c = line_path(Z_PU_C)
blk = [k for k, s in (('base', P['base']), ('piston', piston_c), ('rod', rod)) if s.common(lp_c).Volume > 1e-4]
rep("%s line loop path (legs + piston tunnel) is open through base and piston: %s" % (ok(not blk), blk or "clear"))
for od in (SPRING_OD, SPRING_OD_MAX):
    gap = LEG_X - 0.25 - od / 2
    tag = ok(gap >= 2.0 - 1e-9) if od == SPRING_OD else ("PASS" if gap >= 2 else "NOTE")
    rep("%s line leg to spring coils (spring OD %.0f): %.2f mm (>= 2.0)" % (tag, od, gap))
for sx in (1, -1):
    h = (sx * LEG_X, 0.0); c = coil_pt(sx); k = (sx * CLAMP_XY[0], CLAMP_XY[1])
    v1 = (c[0] - h[0], c[1] - h[1]); v2 = (k[0] - c[0], k[1] - c[1])
    ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))))))
    rep("%s leg %+d: line runs straight through its coil (bend %.1f deg <= 5), so the nichrome carries no line load" % (ok(ang <= 5), sx, ang))
runs = chamber_runs()
for i, sx in enumerate((1, -1)):
    others = {k: hh for k, hh in heads.items() if k != 'clamp%+d' % sx}
    dmin, who = min((runs[i].distToShape(hh)[0], k) for k, hh in others.items())
    rep("%s chamber run %+d clears the other M2 heads by %.2f mm (>= 0.5, nearest %s)" % (ok(dmin >= 0.5), sx, dmin, who))
ns = nichrome.distToShape(P['base'])[0]
rep("%s nichrome heated span (0.5 mm past each terminal head) to nearest plastic: %.2f mm (>= 1.0)" % (ok(ns >= 1.0), ns))
under = [P['base'].common(cyl(M2_HEAD_R, CHAMBER_H, CHAMBER_H + 0.5, x=sx * TERM_XY[0], y=TERM_XY[1])).Volume /
         (math.pi * (M2_HEAD_R ** 2 - 0.85 ** 2) * 0.5) for sx in (1, -1)]
rep("%s terminal heads still bear on solid ceiling beside the trough (%.0f%%, %.0f%%; >= 50%%)" % (ok(min(under) >= 0.5), 100 * under[0], 100 * under[1]))
leg_len = Z_TUNNEL - Z_LINE_CH
hole_to_coil = math.hypot(LEG_X - abs(coil_pt(1)[0]), coil_pt(1)[1])
margin = leg_len + hole_to_coil - (STROKE + TETHER_SLACK)
rep("%s single-leg cut: free end pays out %.1f mm more than a full stroke needs (>= 10)" % (ok(margin >= 10), margin))
leg_F = F_MAX_DESIGN / 2
rep("Line load per leg: %.1f N at F_max %.1f N, %.0f N at %gx proof. 0.3 mm Dyneema wrapped+clamped ~175 N -> %.1fx at proof; use 0.4-0.5 mm if 7.3 measures > 40 N."
    % (leg_F, F_MAX_DESIGN, leg_F * PROOF_FACTOR, PROOF_FACTOR, 175 / (leg_F * PROOF_FACTOR)))

# chamber hardware
inside = all(math.hypot(x, y) + M2_HEAD_R <= CHAMBER_R - 0.3 for x, y in [TERM_XY, mirror_x(TERM_XY), CLAMP_XY, mirror_x(CLAMP_XY)])
rep("%s all M2 heads inside the chamber wall" % ok(inside))
hk = list(heads)
clash = [(a, b) for i, a in enumerate(hk) for b in hk[i + 1:] if heads[a].distToShape(heads[b])[0] < 0.3]
rep("%s M2 heads clear of each other (>= 0.3 mm): %s" % (ok(not clash), clash or "yes"))
hole_hit = [k for k, h in heads.items() for sx in (1, -1) if h.distToShape(cyl(LINE_HOLE_D / 2 + 0.6, 0, CHAMBER_H, x=sx * LEG_X))[0] < 0.3]
rep("%s M2 heads clear of the line holes: %s" % (ok(not hole_hit), hole_hit or "yes"))
for sx in (1, -1):
    x, y = sx * CLAMP_XY[0], CLAMP_XY[1]
    ann = cyl(M2_HEAD_R, CHAMBER_H, CHAMBER_H + 1.0, x=x, y=y).cut(cyl(0.85, 0, 50, x=x, y=y))
    fr = P['base'].common(ann).Volume / ann.Volume
    rep("%s clamp at x=%+.0f has solid material under its head (%.0f%%)" % (ok(fr > 0.9), x, 100 * fr))
trough = P['base'].common(box(-1.5, 1.5, TERM_XY[1] - 0.5, TERM_XY[1] + 0.5, CHAMBER_H, CHAMBER_H + 1.4)).Volume
rep("%s air gap under the nichrome span exists (plastic in gap: %.3f mm3)" % (ok(trough < 1e-6), trough))
th_ok = P['base'].common(cyl(0.6, 0, 20, x=TETHER_XY[0], y=TETHER_XY[1])).Volume < 1e-6 and \
    piston_c.common(cyl(0.6, Z_PU_C - 1, Z_TOP_C + 1, x=TETHER_XY[0], y=TETHER_XY[1])).Volume < 1e-6
rep("%s tether hole open through base and piston" % ok(th_ok))

# RBF pin
gap = pin.distToShape(piston_c)[0]
swept = cyl(PISTON_D / 2, Z_PU_C, Z_PU_F + PLATE_H)
rep("%s RBF pin clears the cocked piston by %.2f mm and sits in its path (blocks within %.1f mm of travel)"
    % (ok(0.5 <= gap <= 1.5 and swept.common(pin).Volume > 1), gap, gap))
m_settle = (Z_PIN - PIN_D / 2) - (Z_TOP_C + SETTLE)
rep("%s after the line takes load (piston +%.1f mm) the RBF pin still goes in with %.2f mm clear (>= 0.5)" % (ok(m_settle >= 0.5), SETTLE, m_settle))
face_when_locked = (Z_LOCK - PIN_D / 2) - ((Z_LOCK + LOCK_HOLE_DZ - (PIN_D / 2 + 0.1)) - Z_TOP_C - 0.02)
rep("%s bench lock pin holds the tool face at %.2f mm from the nominal cocked piston top (|d| <= 0.2)" % (ok(abs(face_when_locked - Z_TOP_C) <= 0.2), face_when_locked - Z_TOP_C))
hg = AIRFRAME_ID / 2 - PISTON_FLAT / math.cos(math.radians(CLOCK_TOL_DEG))
rep("%s harness passes the piston flat with %.2f mm radial gap even %.0f deg off the +/-y groove (>= harness %.1f + 0.3)" % (ok(hg >= HARNESS_T + 0.3), hg, CLOCK_TOL_DEG, HARNESS_T))
M = F_MAX_DESIGN * (PROOF_FACTOR + 1) * AIRFRAME_ID / 4    # proof hang 4x on top of the spring's 1x = 5x worst
sig = M / (math.pi * PIN_D ** 3 / 32)
rep("%s RBF pin bending at proof (%.0f N, span %.0f): %.0f MPa vs %.0f MPa yield (need 1.5x)" % (ok(sig * 1.5 <= PIN_YIELD_MPA), F_MAX_DESIGN * PROOF_FACTOR, AIRFRAME_ID, sig, PIN_YIELD_MPA))

# threads
for name, m, f in (('coupon', P['coupon_T1_male'], P['coupon_T1_female']), ('base/bulkhead', P['base'], P['flight_bulkhead']), ('base/stand', P['base'], P['test_stand'])):
    em, ef, eb = engagement(m, f, T1, 2, 6)
    rep("%s T1 %s engagement at mid-flank: male %.0f%%, female %.0f%%, both %.1f%%" % (ok(em > 0.2 and ef > 0.2 and eb == 0), name, 100 * em, 100 * ef, 100 * eb))

# Phoenix fit
stack = Z_TOP_C - (-3.5)
rep("%s nothing crosses the e-bay plane: aft-most part at station %.1f (e-bay / bench joint at 181)" % (ok(station(-3.5) <= 181.0), station(-3.5)))
rep("NOTE stack bulkhead-bottom -> piston top = %.1f mm vs DESIGN 7.8 budget 61 mm (8 bulkhead + 45 spring + 8 piston): %+.1f mm" % (stack, stack - 61))
rho = 1.27e-3
rep("Masses (PETG solid): base %.1f g, piston %.1f g, flight bulkhead %.1f g; + M5x40 bolt ~7 g, spring ~9 g, 4x M2 ~1 g"
    % (P['base'].Volume * rho, piston_c.Volume * rho, P['flight_bulkhead'].Volume * rho))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(OUT_PRINT, exist_ok=True)
doc = App.newDocument("Spring_Ejector_T5")
for k, s in P.items():
    doc.addObject("Part::Feature", k).Shape = s
for k, s in H.items():
    doc.addObject("Part::Feature", "HW_" + k).Shape = s
doc.addObject("Part::Feature", "REF_line_loop").Shape = lp_c
doc.addObject("Part::Feature", "REF_piston_fired").Shape = piston_f
doc.recompute()
doc.saveAs(os.path.join(OUT_MODELS, "spring_ejector_t5.FCStd"))
Part.makeCompound([P['base'], piston_c, P['flight_bulkhead'], rod, pin]).exportStep(os.path.join(OUT_MODELS, "spring_ejector_t5_assembly_cocked.step"))

FLIP = ('base', 'piston', 'install_tool')     # base prints flange-down (chamber opens up), piston top-down
for k, s in P.items():
    s = s.copy()
    if k in FLIP: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.3, Relative=False).write(os.path.join(OUT_PRINT, "t5_%s.stl" % k))

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(13, 11))
    for ax, (title, plane) in zip(axs, (("section y=0 (line legs), cocked", V(0, 1, 0)), ("section x=0 (tether, tool notches), cocked", V(1, 0, 0)))):
        shapes = [(P['base'], 'tab:blue'), (piston_c, 'tab:red'), (P['flight_bulkhead'], '0.5'), (rod, 'k'), (pin, 'tab:purple'),
                  (spring_env(Z_PU_C, SPRING_OD), 'tab:green'), (P['install_tool'], 'tab:orange')]
        for s, c in shapes:
            for e in s.slice(plane, 0.0):
                pts = e.discretize(Deflection=0.02)
                ax.plot([p.x if plane.y else p.y for p in pts], [p.z for p in pts], color=c, lw=0.7)
        ax.set_aspect('equal'); ax.set_title(title); ax.grid(alpha=0.2); ax.set_ylim(-8, 110)
    fig.savefig(os.path.join(OUT_MODELS, "section_cocked.png"), dpi=150, bbox_inches='tight')
except Exception as ex:
    print("section plot skipped:", ex)

with open(os.path.join(OUT_MODELS, "check_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t0))

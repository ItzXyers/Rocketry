# -*- coding: utf-8 -*-
"""
T5 v3 spring-piston ejector with nichrome line release, front-removable module.
v3 (2026-09-27), from spring_ejector_t5_v2.py:
  * spring 15.5 OD (was 10): spring seats in base and piston widened to 16.5.
  * line holes 3.0 mm (was 2.0) and moved out to x = +/-11.5 (was 8), >= 2 mm from the spring.
  * all four line holes go straight through (base AND piston), with a groove across the piston face:
    ONE continuous line threads base A -> piston A -> over the top -> piston B -> base B, and its two
    ends are KNOTTED TOGETHER in the chamber. The M2 line clamps are gone.
  * release chamber re-laid out round the new holes (knot point, coil, nichrome terminals, channels).
v2 (2026-09-24): ONE big nichrome coil on leg +1 in a ceiling pocket (2 mm air to plastic), nichrome
terminals beside it, and e-bay terminals flush with the aft face (copper jumpers between).

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

# Spring: 15.5 OD (v3). Lengths still the DESIGN.md 7.2 values (85 free, 45 cocked -> 40 stroke) until
# the 15.5 OD spring is measured. Rate unmeasured.
SPRING_OD, SPRING_FREE, SPRING_COCKED = 15.5, 85.0, 45.0
SPRING_OD_MAX = 16.0            # largest spring the seats accept
F_MAX_DESIGN = 52.7             # N: stiffest row of DESIGN 7.2 (1.3 mm wire), until 7.3 is measured
PROOF_FACTOR = 4.0              # DESIGN 7.9 test 3
STROKE = SPRING_FREE - SPRING_COCKED
TETHER_SLACK = 1.5              # piston tether goes taut this far past full stroke

THREAD_CLEAR = 0.30
T1 = dict(d=34.0, lead=9.0, starts=3, depth=1.2, crest=0.3)   # identical to T4 T1
T1_LEN = 10.0
FLANGE_D, FLANGE_H = 36.5, 4.0

# Release chamber (inside the threaded spigot, open aft)
CHAMBER_R, CHAMBER_H = 13.7, 6.0   # wall to the T1 thread root (r 15.8) 2.1 mm
LEG_X = 11.5                    # line holes at (+/-LEG_X, 0), straight through base and piston
LINE_HOLE_D = 3.0               # easy threading of 0.3 - 0.5 mm Dyneema (a needle-threader fits)
GROOVE_H = 1.5                  # line groove across the piston face, hole to hole: keeps the line under the face
TETHER_XY = (0.0, 11.0)
# ONE continuous line: its two ends come down the base holes and run STRAIGHT along the ceiling to a
# knot joining them at KNOT_XY. ONE nichrome coil on run +1, COIL_S from the hole, in a ceiling pocket
# with COIL_CLEAR of air all round, so it carries no line load. Cutting the loop anywhere releases.
KNOT_XY = (0.0, -11.5)
KNOT_R = 1.5                    # envelope of the joining knot (double fisherman's / surgeon's in 0.3-0.5 Dyneema)
M2_HEAD_R, M2_HEAD_H = 1.9, 2.0
COIL_OD, COIL_LEN = 2.0, 5.0    # envelope: ~8 turns of 32 AWG on a 1.0 mandrel (OD 1.4) + spring-back
COIL_S = 5.8                    # coil centre, mm along leg +1's run from its hole
COIL_CLEAR = 2.0                # coil to plastic
STRAND_CLEAR = 1.0              # nichrome tails (from 0.5 mm past the terminal head) to plastic
STEEL_CLEAR = 0.5               # glowing nichrome to steel (heat-sinking)
# nichrome terminals (M2 x 6, heads in the chamber), one per coil end. They are OPPOSITE poles, so they
# sit on opposite sides of the run: 1 INBOARD of the hole end (the wall leaves no room outboard there),
# 2 OUTBOARD past the far end. Each tail lies in its own air channel.
NTERM1_S_PERP = (3.0, -4.0)     # (along the run, outboard offset); negative = inboard
NTERM2_S_PERP = (10.5, 3.0)
POLE_GAP = 2.0                  # bare metal of one pole to the other (heads + 0.5 wire-wrap allowance)
COIL_TERM_GAP = 1.0             # coil to either nichrome terminal head
# e-bay terminals: M2 x 8 into pillars hanging from the ceiling, heads flush with the aft face.
# A short copper jumper links each nichrome terminal to an e-bay terminal, so fitting the e-bay
# lugs never disturbs the nichrome.
ETERM_XY = (5.5, 7.2)           # at (+/-x, y); +x is pole 1 (jumper from nichrome terminal 1)
SCREW_LEN = dict(nterm=6.0, eterm=8.0)   # M2 lengths; pilots run 0.5 past each tip
PILLAR_R = 2.6
LUG_T = 0.5                     # ring/fork lug under each e-bay terminal head
SOCKET_R = 6.25                 # 8 mm socket for the M5 head must reach it through the chamber

# Guide rod: M5 x 40 hex bolt (DIN 933), head captured in the chamber ceiling
ROD_D, ROD_HEAD_AF, ROD_HEAD_H, ROD_LEN = 5.0, 8.0, 3.5, 40.0

# Piston (cup with skirt so it cannot cock in the bore)
PISTON_D = 38.5
PLATE_H, SKIRT_H, SKIRT_T = 8.0, 12.0, 2.05
PISTON_CB_D, PISTON_CB_H = SPRING_OD_MAX + 0.5, 3.0   # captures the spring's top end
SEAT_CB_D, SEAT_CB_H = SPRING_OD_MAX + 0.5, 3.0       # spring pocket in the base, as deep as the piston's (floor over the M5 head pocket >= 1.2)

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
Z_TUNNEL = Z_TOP_C - GROOVE_H + 0.25                 # line lies on the groove floor (v2 name kept)
Z_ROD_HEAD = CHAMBER_H                                # head end flush with the chamber ceiling
Z_ROD_TOP = Z_ROD_HEAD + ROD_HEAD_H + ROD_LEN
PHOENIX_PISTON_TOP_STATION = 110.0                    # DESIGN 7.8: canopy 20-110, piston 110-118
def station(z): return PHOENIX_PISTON_TOP_STATION + (Z_TOP_C - z)

Z_LINE_CH = CHAMBER_H - 0.3          # line lies against the chamber ceiling
def line_dir(sx):
    c = KNOT_XY; d = V(c[0] - sx * LEG_X, c[1], 0); d.normalize(); return d
def run_pt(s, perp=0.0, sx=1):   # point s along leg sx's chamber run, perp outboard (away from the axis)
    d = line_dir(sx); n = V(-d.y, d.x, 0) * sx
    return V(sx * LEG_X, 0, 0) + d * s + n * perp
def run_len(sx): return math.hypot(KNOT_XY[0] - sx * LEG_X, KNOT_XY[1])
COIL_C = run_pt(COIL_S)
NTERMS = [run_pt(*NTERM1_S_PERP), run_pt(*NTERM2_S_PERP)]
ETERMS = [V(ETERM_XY[0], ETERM_XY[1], 0), V(-ETERM_XY[0], ETERM_XY[1], 0)]
Z_PILLAR = M2_HEAD_H + LUG_T                          # pillar end: head + lug stack ends flush at z 0
Z_POCKET = Z_LINE_CH + COIL_OD / 2 + COIL_CLEAR + 0.1 # roof of the coil pocket

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
base = base.cut(cyl(1.1, CHAMBER_H - 0.01, Z_TOP_BASE + 0.01, x=TETHER_XY[0], y=TETHER_XY[1]))          # piston tether
for t in NTERMS:
    base = base.cut(cyl(0.85, CHAMBER_H - 0.01, CHAMBER_H + SCREW_LEN['nterm'] + 0.5, x=t.x, y=t.y))   # nichrome terminals
for t in ETERMS:   # e-bay terminal pillars, M2 x 8 self-tapped from the aft face
    base = base.fuse(cyl(PILLAR_R, Z_PILLAR, CHAMBER_H + 0.01, x=t.x, y=t.y))
    base = base.cut(cyl(0.85, Z_PILLAR - 0.01, M2_HEAD_H + SCREW_LEN['eterm'] + 0.5, x=t.x, y=t.y))
m = COIL_CLEAR + 0.1   # coil pocket: box round the coil, aligned with the run
pk = box(-(COIL_LEN / 2 + m), COIL_LEN / 2 + m, -(COIL_OD / 2 + m), COIL_OD / 2 + m, CHAMBER_H - 0.01, Z_POCKET)
d = line_dir(1)
pk.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(d.y, d.x)))
base = base.cut(pk.translated(V(COIL_C.x, COIL_C.y, 0)))
for t, se in zip(NTERMS, (COIL_S - COIL_LEN / 2, COIL_S + COIL_LEN / 2)):   # air channel under each tail,
    e2 = run_pt(se); u2 = t - e2; L2 = u2.Length; u2.normalize()                  # coil end -> terminal centre
    ch = box(0, L2, -(0.1 + STRAND_CLEAR + 0.1), 0.1 + STRAND_CLEAR + 0.1, CHAMBER_H - 0.01, Z_POCKET)
    ch.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(u2.y, u2.x)))
    base = base.cut(ch.translated(V(e2.x, e2.y, 0)))
for sy in (1, -1):   # install-tool key notches in the flange (+/-y)
    base = base.cut(box(-2.5, 2.5, 16.1 if sy > 0 else -20, 20 if sy > 0 else -16.1, T1_LEN + 1.0, Z_TOP_BASE + 0.1))
assert base.isValid()
P['base'] = base

# ---------------- PISTON (cup with skirt; line through-holes + face groove; tether hole; tool notches)
def make_piston(zpu):
    p = cyl(PISTON_D / 2, zpu, zpu + PLATE_H)
    p = p.fuse(cyl(PISTON_D / 2, zpu - SKIRT_H, zpu + 0.01).cut(cyl(PISTON_D / 2 - SKIRT_T, zpu - SKIRT_H - 1, zpu + 0.02)))
    p = p.cut(cyl(PISTON_CB_D / 2, zpu - 0.01, zpu + PISTON_CB_H))
    ztop = zpu + PLATE_H
    p = p.cut(box(-LEG_X, LEG_X, -LINE_HOLE_D / 2, LINE_HOLE_D / 2, ztop - GROOVE_H, ztop + 0.01))   # line groove, hole to hole
    for sx in (1, -1):
        p = p.cut(cyl(LINE_HOLE_D / 2, zpu - 0.01, ztop + 0.01, x=sx * LEG_X))   # straight through: thread from either side
        p = p.cut(Part.makeCone(LINE_HOLE_D / 2 + 0.6, LINE_HOLE_D / 2, 0.6, V(sx * LEG_X, 0, zpu - 0.01)))
        p = p.cut(Part.makeCone(LINE_HOLE_D / 2, LINE_HOLE_D / 2 + 0.6, 0.6, V(sx * LEG_X, 0, ztop - GROOVE_H - 0.59)))   # round the bend into the groove
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
for i, t in enumerate(NTERMS):
    heads['nterm%d' % (i + 1)] = cyl(M2_HEAD_R, CHAMBER_H - M2_HEAD_H, CHAMBER_H - 0.01, x=t.x, y=t.y)
for i, t in enumerate(ETERMS):
    heads['eterm%d' % (i + 1)] = cyl(M2_HEAD_R, 0.0, M2_HEAD_H, x=t.x, y=t.y)
for k, v in heads.items(): H['M2_' + k] = v
def chamber_runs(r=0.2):   # hole -> knot (stops at the knot envelope), both sides
    out = []
    for sx in (1, -1):
        h = V(sx * LEG_X, 0, Z_LINE_CH)
        out.append(Part.makeCylinder(r, run_len(sx) - KNOT_R, h, line_dir(sx)))
    return out
knot = Part.makeSphere(KNOT_R, V(KNOT_XY[0], KNOT_XY[1], CHAMBER_H - KNOT_R - 0.05))   # hangs from the ceiling
def line_path(zpu):   # the loop centreline: chamber runs, legs through base and piston, face groove
    zt = zpu + PLATE_H - GROOVE_H + 0.25
    legs = [cyl(0.2, Z_LINE_CH, zt, x=sx * LEG_X) for sx in (1, -1)]
    return Part.makeCompound(legs + [xcyl(0.2, -LEG_X, LEG_X, z=zt)] + chamber_runs())
HEATSINK = 0.5                   # first 0.5 mm past each steel head stays cool (heat-sunk)
d1 = line_dir(1)
coil = Part.makeCylinder(COIL_OD / 2, COIL_LEN, V(COIL_C.x, COIL_C.y, Z_LINE_CH) - d1 * (COIL_LEN / 2), d1)
H['nichrome_coil'] = coil
tails, tail_len = [], []         # straight nichrome from 0.5 mm past each terminal head to its coil end
for t, se in zip(NTERMS, (COIL_S - COIL_LEN / 2, COIL_S + COIL_LEN / 2)):
    e = run_pt(se); e.z = Z_LINE_CH
    a = V(t.x, t.y, Z_LINE_CH); u = e - a; u.normalize()
    a = a + u * (M2_HEAD_R + HEATSINK)
    tails.append(Part.makeCylinder(0.1, (e - a).Length, a, e - a)); tail_len.append((e - a).Length)
nichrome = Part.makeCompound([coil] + tails)   # everything that glows (t5_integration.py reads this name)

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
rep("== T5 v3 spring-piston ejector check report ==")
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
rep("NOTE spring guidance: the M5 rod does NOT guide a %.1f OD spring (its ID is far larger than 5); only the seats capture the ends (%.0f + %.0f mm). "
    "L/D free %.1f, cocked %.1f: stable for ground ends clamped in seats below ~5.2 free. Bench-check for bowing; a printed guide sleeve over the rod is the fix."
    % (SPRING_OD, SEAT_CB_H, PISTON_CB_H, SPRING_FREE / SPRING_OD, SPRING_COCKED / SPRING_OD))
rep("%s rod top clears piston underside when cocked by %.1f mm" % (ok(Z_PU_C - Z_ROD_TOP >= 2), Z_PU_C - Z_ROD_TOP))
rep("Stroke stop: Kevlar tether, taut at %.1f mm (stroke %.0f + %.1f). Cut to length on the bench (README)." % (STROKE + TETHER_SLACK, STROKE, TETHER_SLACK))

# line path
lp_c = line_path(Z_PU_C)
blk = [k for k, s in (('base', P['base']), ('piston', piston_c), ('rod', rod)) if s.common(lp_c).Volume > 1e-4]
rep("%s line loop path (base holes, piston through-holes, face groove) is open: %s" % (ok(not blk), blk or "clear"))
thru = [k for k, sh, z0, z1 in (('base', P['base'], -1, Z_TOP_BASE + 1), ('piston', piston_c, Z_PU_C - 1, Z_TOP_C + 1))
        for sx in (1, -1) if sh.common(cyl(LINE_HOLE_D / 2 - 0.05, z0, z1, x=sx * LEG_X)).Volume > 1e-4]
rep("%s all four line holes are straight Ø%.1f through-holes (a stiff leader goes straight through each): %s" % (ok(not thru), LINE_HOLE_D, thru or "yes"))
gz = piston_c.common(box(-LEG_X, LEG_X, -0.2, 0.2, Z_TOP_C - GROOVE_H + 0.05, Z_TOP_C + 1)).Volume
rep("%s face groove %.1f deep x %.1f wide joins the two piston holes; the line stays %.2f mm below the face (RBF pin / tool face never touch it): %s"
    % (ok(gz < 1e-4), GROOVE_H, LINE_HOLE_D, GROOVE_H - 0.25 - 0.25, "open" if gz < 1e-4 else "%.3f mm3 blocked" % gz))
for od in (SPRING_OD, SPRING_OD_MAX):
    gap = LEG_X - LINE_HOLE_D / 2 - od / 2      # worst case: line hard against the inboard edge of the hole
    rep("%s line to spring coils (spring OD %.1f), line against the inboard hole edge: %.2f mm (>= 2.0)" % (ok(gap >= 2.0 - 1e-9), od, gap))
fl = Z_SEAT - (CHAMBER_H + ROD_HEAD_H + 0.2)
rep("%s spring pocket in the base: Ø%.1f x %.1f deep (piston: Ø%.1f x %.1f); floor over the M5 head pocket %.2f mm (>= 1.2)"
    % (ok(fl >= 1.2), SEAT_CB_D, SEAT_CB_H, PISTON_CB_D, PISTON_CB_H, fl))
web = LEG_X - LINE_HOLE_D / 2 - 0.6 - SEAT_CB_D / 2
rep("%s plastic web between line hole (incl. 0.6 edge round) and spring seat/counterbore: %.2f mm (>= 1.0)" % (ok(web >= 1.0), web))
end_ok = LINE_HOLE_D / 2 + 0.6 + 0.5 <= COIL_S - COIL_LEN / 2 and COIL_S + COIL_LEN / 2 <= run_len(1) - KNOT_R - 1.0
rep("%s coil on run +1's straight part (hole -> knot), %.1f mm from the hole, ends clear of the hole mouth and the knot: the nichrome carries no line load" % (ok(end_ok), COIL_S))
runs = chamber_runs()
for i, sx in enumerate((1, -1)):
    others = dict(heads)
    dmin, who = min((runs[i].distToShape(hh)[0], k) for k, hh in others.items())
    rep("%s chamber run %+d clears the M2 heads by %.2f mm (>= 0.5, nearest %s)" % (ok(dmin >= 0.5), sx, dmin, who))
steel = dict(heads, rod=rod)
cp = coil.distToShape(P['base'])[0]
cst, cw = min((coil.distToShape(s_)[0], k) for k, s_ in steel.items())
rep("%s coil (OD %.1f x %.1f along the line) to nearest plastic: %.2f mm (>= %.1f)" % (ok(cp >= COIL_CLEAR), COIL_OD, COIL_LEN, cp, COIL_CLEAR))
rep("%s coil to nearest steel: %.2f mm (>= %.1f, nearest %s)" % (ok(cst >= STEEL_CLEAR), cst, STEEL_CLEAR, cw))
ctg = [coil.distToShape(heads['nterm%d' % (i + 1)])[0] for i in range(2)]
rep("%s coil to the nichrome terminal heads: %.2f, %.2f mm (>= %.1f: a turn touching a head would short part of the coil)" % (ok(min(ctg) >= COIL_TERM_GAP), ctg[0], ctg[1], COIL_TERM_GAP))
def pole(i):   # bare metal of pole i: its two terminal heads grown by the wire-wrap allowance, plus its tail
    hs = [cyl(M2_HEAD_R + 0.5, hh.BoundBox.ZMin, hh.BoundBox.ZMax, x=hh.BoundBox.Center.x, y=hh.BoundBox.Center.y) for hh in (heads['nterm%d' % i], heads['eterm%d' % i])]
    return Part.makeCompound(hs + [tails[i - 1]])
pg = pole(1).distToShape(pole(2))[0]
rep("%s pole 1 to pole 2 (terminal heads + 0.5 mm wrap allowance, tails): %.2f mm (>= %.1f, the full burn voltage sits across it)" % (ok(pg >= POLE_GAP), pg, POLE_GAP))
for k, hh in heads.items():
    kind = k.rstrip('+-0123456789')
    bb = hh.BoundBox
    zb, zt = bb.ZMax, bb.ZMax + SCREW_LEN[kind]   # shank starts at the head's bearing face
    blocked = P['base'].common(cyl(0.8, zb + 0.01, zt + 0.5, x=bb.Center.x, y=bb.Center.y)).Volume
    rep("%s M2 x %g %s: pilot open 0.5 mm past the tip (z %.1f), so the head seats (%.3f mm3 in the way)" % (ok(blocked < 1e-6), SCREW_LEN[kind], k, zt, blocked))
for i, tl in enumerate(tails):
    tp = tl.distToShape(P['base'])[0]
    tst, tw = min((tl.distToShape(s_)[0], k) for k, s_ in steel.items() if k != 'nterm%d' % (i + 1))
    rep("%s nichrome tail %d (%.1f mm, from 0.5 mm past its head) to plastic %.2f mm (>= %.1f), to other steel %.2f mm (>= %.1f, nearest %s)"
        % (ok(tp >= STRAND_CLEAR and tst >= STEEL_CLEAR), i + 1, tail_len[i], tp, STRAND_CLEAR, tst, STEEL_CLEAR, tw))
rep("Coil centre (%.2f, %.2f); pocket %.1f x %.1f mm, %.1f mm deep into the ceiling; nichrome terminals at (%.2f, %.2f) and (%.2f, %.2f)"
    % (COIL_C.x, COIL_C.y, COIL_LEN + 2 * m, COIL_OD + 2 * m, Z_POCKET - CHAMBER_H, NTERMS[0].x, NTERMS[0].y, NTERMS[1].x, NTERMS[1].y))
under = [P['base'].common(cyl(M2_HEAD_R, CHAMBER_H, CHAMBER_H + 0.5, x=t.x, y=t.y).cut(cyl(0.85, 0, 50, x=t.x, y=t.y))).Volume /
         (math.pi * (M2_HEAD_R ** 2 - 0.85 ** 2) * 0.5) for t in NTERMS]
rep("%s nichrome terminal heads bear on solid ceiling beside the pocket (%.0f%%, %.0f%%; >= 50%%)" % (ok(min(under) >= 0.5), 100 * under[0], 100 * under[1]))
leg_len = Z_TUNNEL - Z_LINE_CH
margin = leg_len + 2 * LEG_X + COIL_S - (STROKE + TETHER_SLACK)
rep("%s cut at the coil: the free end pays out %.1f mm more than a full stroke needs before it even leaves the piston (>= 10)" % (ok(margin >= 10), margin))
kh = min(knot.distToShape(hh)[0] for hh in heads.values())
kc = knot.distToShape(coil)[0]
kw = CHAMBER_R - math.hypot(*KNOT_XY) - KNOT_R
rep("%s knot room at (%.1f, %.1f): to M2 heads %.2f mm (>= 0.5), to the coil %.2f mm (>= 2.0), to the chamber wall %.2f mm (>= 0.3)"
    % (ok(kh >= 0.5 and kc >= 2.0 and kw >= 0.3), KNOT_XY[0], KNOT_XY[1], kh, kc, kw))
leg_F = F_MAX_DESIGN / 2
rep("Line tension (each leg of the loop): %.1f N at F_max %.1f N, %.0f N at %gx proof. A knot keeps ~50%% of line strength, "
    "so the line must break at >= %.0f N (%.0f kg): 0.4-0.5 mm Dyneema; 0.3 mm only if 7.3 measures F_max < ~30 N."
    % (leg_F, F_MAX_DESIGN, leg_F * PROOF_FACTOR, PROOF_FACTOR, 2 * leg_F * PROOF_FACTOR, 2 * leg_F * PROOF_FACTOR / 9.81))

# chamber hardware
inside = all(math.hypot(hh.BoundBox.Center.x, hh.BoundBox.Center.y) + M2_HEAD_R <= CHAMBER_R - 0.3 for hh in heads.values())
rep("%s all M2 heads inside the chamber wall" % ok(inside))
hk = list(heads)
clash = [(a_, b_) for i, a_ in enumerate(hk) for b_ in hk[i + 1:] if heads[a_].distToShape(heads[b_])[0] < 0.3]
rep("%s M2 heads clear of each other (>= 0.3 mm): %s" % (ok(not clash), clash or "yes"))
hole_hit = [k for k, h in heads.items() for sx in (1, -1) if h.distToShape(cyl(LINE_HOLE_D / 2 + 0.6, 0, CHAMBER_H, x=sx * LEG_X))[0] < 0.3]
rep("%s M2 heads clear of the line holes: %s" % (ok(not hole_hit), hole_hit or "yes"))

# e-bay terminals
flush = min(heads['eterm%d' % (i + 1)].BoundBox.ZMin for i in range(2))
sight = sum(P['base'].common(cyl(M2_HEAD_R + 0.5, -20, 0, x=t.x, y=t.y)).Volume for t in ETERMS)
rep("%s e-bay terminal heads end at z %.1f (flush with the aft face, station %.1f), nothing aft of them (%.3f mm3): lugs go on from the e-bay side" % (ok(abs(flush) < 1e-6 and sight < 1e-6), flush, station(0), sight))
pb = [P['base'].common(cyl(M2_HEAD_R, Z_PILLAR, Z_PILLAR + 0.5, x=t.x, y=t.y).cut(cyl(0.85, 0, 50, x=t.x, y=t.y))).Volume /
      (math.pi * (M2_HEAD_R ** 2 - 0.85 ** 2) * 0.5) for t in ETERMS]
rep("%s e-bay terminal heads bear fully on their pillars (%.0f%%, %.0f%%)" % (ok(min(pb) > 0.99), 100 * pb[0], 100 * pb[1]))
sk = P['base'].common(cyl(SOCKET_R, -0.5, CHAMBER_H - 0.01)).Volume
rep("%s chamber open to r %.2f round the axis (8 mm socket reaches the M5 head): %.3f mm3 in the way" % (ok(sk < 1e-6), SOCKET_R, sk))
tkp = min(math.hypot(t.x - TETHER_XY[0], t.y - TETHER_XY[1]) - PILLAR_R - 1.1 for t in ETERMS)
rep("%s tether knot room: pillars %.1f mm from the tether hole edge (>= 2.0)" % (ok(tkp >= 2.0), tkp))
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
rep("Masses (PETG solid): base %.1f g, piston %.1f g, flight bulkhead %.1f g; + M5x40 bolt ~7 g, spring (15.5 OD, weigh it), 4x M2 ~1 g"
    % (P['base'].Volume * rho, piston_c.Volume * rho, P['flight_bulkhead'].Volume * rho))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(OUT_PRINT, exist_ok=True)
doc = App.newDocument("Spring_Ejector_T5_v3")
for k, s in P.items():
    doc.addObject("Part::Feature", k).Shape = s
for k, s in H.items():
    doc.addObject("Part::Feature", "HW_" + k).Shape = s
doc.addObject("Part::Feature", "REF_line_loop").Shape = lp_c
doc.addObject("Part::Feature", "REF_knot").Shape = knot
doc.addObject("Part::Feature", "REF_piston_fired").Shape = piston_f
doc.recompute()
doc.saveAs(os.path.join(OUT_MODELS, "spring_ejector_t5_v3.FCStd"))
Part.makeCompound([P['base'], piston_c, P['flight_bulkhead'], rod, pin]).exportStep(os.path.join(OUT_MODELS, "spring_ejector_t5_v3_assembly_cocked.step"))

FLIP = ('base', 'piston', 'install_tool')     # base prints flange-down (chamber opens up), piston top-down
for k, s in P.items():
    s = s.copy()
    if k in FLIP: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.3, Relative=False).write(os.path.join(OUT_PRINT, "t5v3_%s.stl" % k))

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(13, 11))
    for ax, (title, plane) in zip(axs, (("v3 section y=0 (line legs), cocked", V(0, 1, 0)), ("section x=0 (tether, tool notches), cocked", V(1, 0, 0)))):
        shapes = [(P['base'], 'tab:blue'), (piston_c, 'tab:red'), (P['flight_bulkhead'], '0.5'), (rod, 'k'), (pin, 'tab:purple'),
                  (spring_env(Z_PU_C, SPRING_OD), 'tab:green'), (P['install_tool'], 'tab:orange')]
        for s, c in shapes:
            for e in s.slice(plane, 0.0):
                pts = e.discretize(Deflection=0.02)
                ax.plot([p.x if plane.y else p.y for p in pts], [p.z for p in pts], color=c, lw=0.7)
        ax.set_aspect('equal'); ax.set_title(title); ax.grid(alpha=0.2); ax.set_ylim(-8, 110)
    fig.savefig(os.path.join(OUT_MODELS, "section_cocked_v3.png"), dpi=150, bbox_inches='tight')
    # plan view of the release chamber, looking forward from the e-bay
    fig, ax = plt.subplots(figsize=(8, 8))
    zc = (CHAMBER_H + Z_POCKET) / 2
    for s, c, z, lab in ((P['base'], 'tab:blue', zc, 'base at z %.1f (in the pocket)' % zc), (P['base'], 'tab:cyan', 4.0, 'base at z 4 (pillars)'), (P['base'], '0.6', CHAMBER_H - 0.5, 'chamber wall'),
                         (rod, 'k', CHAMBER_H + 1.0, 'M5 head'), (Part.makeCompound(list(heads.values())), '0.3', CHAMBER_H - 1.0, 'M2 heads'),
                         (coil, 'tab:red', Z_LINE_CH, 'coil envelope'), (Part.makeCompound([heads['eterm1'], heads['eterm2']]), 'tab:purple', 1.0, 'e-bay terminal heads (flush aft)')):
        first = True
        for e in s.slice(V(0, 0, 1), z):
            pts = e.discretize(Deflection=0.02)
            ax.plot([p.x for p in pts], [p.y for p in pts], color=c, lw=0.8, label=lab if first else None); first = False
    for i, sx in enumerate((1, -1)):
        ax.plot([sx * LEG_X, KNOT_XY[0]], [0, KNOT_XY[1]], color='tab:green', lw=1.2, label='line' if i == 0 else None)
    ax.add_patch(plt.Circle(KNOT_XY, KNOT_R, color='tab:green', fill=False, lw=1.2))
    for i, tl in enumerate(tails):
        a_, b_ = tl.Vertexes[0].Point, tl.Vertexes[-1].Point
        ax.plot([a_.x, b_.x], [a_.y, b_.y], color='tab:orange', lw=1.2, label='nichrome tails' if i == 0 else None)
    ax.set_aspect('equal'); ax.grid(alpha=0.2); ax.legend(loc='upper right', fontsize=8)
    ax.set_title("v3 release chamber plan (x right, y up): line runs to the knot, coil pocket, terminals, pillars")
    fig.savefig(os.path.join(OUT_MODELS, "section_chamber_plan_v3.png"), dpi=150, bbox_inches='tight')
except Exception as ex:
    print("section plot skipped:", ex)

with open(os.path.join(OUT_MODELS, "check_report_v3.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t0))

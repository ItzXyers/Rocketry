# -*- coding: utf-8 -*-
"""
T5 integration: chute bay + T5 spring-piston ejector + e-bay, as flush, printable airframe sections.

Phoenix ABS 40-43 (43 OD / 40 ID). Reuses, unchanged:
  * the T5 module (base, piston, rod, pin, tool) from spring_ejector_t5.py (exec'd up to CHECKS),
  * the e-bay ElectronicsSled v1 + component envelopes from
    PhoenixABS40-43/Avionics/PhoenixABS40-43_avbay_sled_v1.py (exec'd without main()),
  * the aft fin can AftFinCan_v1.step (reference only: the e-bay section lands on its lip).

New printed parts:
  fwd_section  station 0 -> 181 (+ spigot to 199). Chute bay, integral T5 ring (replaces the
               bonded t5_flight_bulkhead), RBF pin holes, flush spigot for the e-bay joint.
  ebay_section station 181 -> 288.6. Slides over the fin-can lip (bonded). Thickened screw band
               at the forward end; static + sound ports.
  sled_mount   disc + 3 lugs. Screws onto the sled's (now unused) servo-ear bosses; the 3 joint
               screws pass e-bay band -> spigot -> lug, so one screw set holds all three.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"

Frame: the T5 module frame (+Z toward the nose, z = 0 at the module's aft face).
  Phoenix station (mm from the top of the body tube) = 172 - z.
  Sled packing frame Zs: z = Zs - 77.3  (sled mount disc top at station 199).
  Fin-can frame Zf:      z = Zf - 168   (Zf 0 = aft end of body, station 340).
Any FAIL line in the report means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, Mesh, MeshPart

V = App.Vector
ROOT = r"C:\Users\dick_\Documents\Rocketry\Ejection System T5"
PHX = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43"
T5_SRC = os.environ.get("T5_SRC", os.path.join(ROOT, "Models", "spring_ejector_t5.py"))   # v2 has the same outer interface
SLED_SRC = os.path.join(PHX, "Avionics", "PhoenixABS40-43_avbay_sled_v1.py")
FINCAN_STEP = os.path.join(PHX, "Models", "PhoenixABS40-43_AftFinCan_v1.step")

t0 = time.time()
# ---------------- T5 module geometry (everything above the CHECKS banner; no export)
_src = open(T5_SRC, encoding="utf-8").read()
_cut = _src.index("# CHECKS")
_cut = _src.rfind("# ====", 0, _cut)
exec(_src[:_cut])          # defines P, H, piston_c, piston_f, pin, heads, helpers, parameters
OUT_MODELS = os.path.join(ROOT, "Models")                   # after the exec: T5 sets its own
OUT_PRINT = os.path.join(ROOT, "Print Files", "Integrated")

# ---------------- e-bay sled (unchanged) + component envelopes
_ss = open(SLED_SRC, encoding="utf-8").read()
_ss = _ss[:_ss.rstrip().rfind("main()")]
SL = {"__name__": "sledlib"}
exec(_ss, SL)
_sled_s, _ = SL['build_sled']([])

# =====================================================================================
# PARAMETERS
# =====================================================================================
R_OD, R_ID = AIRFRAME_OD / 2, AIRFRAME_ID / 2          # 21.5 / 20.0
def zst(station): return 172.0 - station                # station -> module z
ST_JOINT = 181.0                                        # DESIGN 7.8 bench-service joint
ST_SPIGOT_END = 199.0
ST_FINCAN_SHOULDER = 340.0 - 51.4                       # AFT_RETENTION_DESIGN: fwd tube lands at Zf 51.4
ST_FINCAN_BULKHEAD = 340.0 - 58.9                       # lip / bulkhead forward face
FINCAN_LIP_R = 19.85

SPIGOT_RO, SPIGOT_RI = 19.5, 17.8                       # on the fwd section
BAND_RI = 19.7                                          # e-bay screw band (wall 1.8), sled R 19.39 passes
BAND_END = 200.0
RING_CHAMFER_R = 18.55                                  # ring fwd-face print chamfer starts outside the flange (18.25)

# joint screws: 3 x M3 x 8 countersunk (DIN 7991), uneven pattern = one clocking only
JOINT_SCREW_ST = 190.0
JOINT_ANG = (90.0, 225.0, 330.0)
CSK_DK, CSK_K_CYL, CSK_CONE = 6.0, 0.2, 1.5             # head dia, top cylinder, cone depth (90 deg)
CSK_TOP = math.sqrt(R_OD ** 2 - (CSK_DK / 2) ** 2)      # head top plane so its rim sits on the OD
M3_LEN = 8.0
JOINT_SNATCH_N = 250.0                                  # PLACEHOLDER, as in the cassette report [R]

# sled mount
SLED_Z_OFF = -77.3                                      # z = Zs + SLED_Z_OFF
DISC_R = 19.3
DISC_ZS0, DISC_ZS1 = 45.4, 50.3                         # bottom rests on the servo-ear bosses (top 45.4)
LUG_W, LUG_RI, LUG_RO = 7.0, 13.0, 17.6
LUG_TOP_ST = 185.0
LEAD_HOLE_R = 6.0
SLED_SCREWS = [(SL['SERVO_TAB_XW'], 0.0), (SL['SERVO_TAB_XE'], 0.0)]   # the unused SG90 ear bosses, M2 tapped

# e-bay wall ports (sled frame Zs, +x = east = piezo side)
STATIC_PORT = dict(d=1.5, zs=30.0, ang=0.0)             # empty ex-servo space; baro only needs shared air
SOUND_PORT = dict(d=3.0, zs=SL['PIEZO_DZ'] / 2, ang=0.0)  # in line with the sled's piezo port

EF_CHAMFER = 0.5                                        # 45 deg ID chamfer at each bed-side end (elephant's foot, lead-in)
SLED_ELEC_G = 45.0                                      # sled 7.7 g + electronics/battery (packing md 6), rough
BOOST_G = 20.0
RHO_PETG = 1.27e-3
BED = (256.0, 256.0, 250.0)                             # Bambu X1C (LaunchPad/BOM.md)

def rz(pairs):   # revolve (r, station) pairs
    return revolve([(r, zst(s)) for r, s in pairs])

def rot(shape, ang):
    s = shape.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), ang); return s

def radial_cyl(r, x0, x1, z, ang):
    return rot(Part.makeCylinder(r, x1 - x0, V(x0, 0, z), V(1, 0, 0)), ang)

def radial_cone(r0, r1, x0, x1, z, ang):
    return rot(Part.makeCone(r0, r1, x1 - x0, V(x0, 0, z), V(1, 0, 0)), ang)

def csk_cutter(z, ang):
    top = CSK_TOP - 0.0
    c = radial_cyl(CSK_DK / 2 + 0.1, top - CSK_K_CYL, R_OD + 2, z, ang)
    c = c.fuse(radial_cone(1.6, CSK_DK / 2 + 0.1, top - CSK_K_CYL - CSK_CONE - 0.1, top - CSK_K_CYL, z, ang))
    return c.fuse(radial_cyl(1.6, SPIGOT_RI - 0.8, top - CSK_K_CYL - 1.0, z, ang))

def csk_screw(z, ang):
    top = CSK_TOP
    s = radial_cyl(CSK_DK / 2, top - CSK_K_CYL, top, z, ang)
    s = s.fuse(radial_cone(1.5, CSK_DK / 2, top - CSK_K_CYL - CSK_CONE, top - CSK_K_CYL, z, ang))
    return s.fuse(radial_cyl(1.5, top - M3_LEN, top - CSK_K_CYL - CSK_CONE + 0.01, z, ang))

# =====================================================================================
# PARTS
# =====================================================================================
N = {}
zj = zst(ST_JOINT)

# ---------------- FORWARD SECTION: chute bay + integral T5 ring + spigot
fw = cyl(R_OD, zj, zst(0.0)).cut(cyl(R_ID, zj - 1, zst(0.0) + 1))
ring = cyl(R_ID + 0.5, -3.5, T1_LEN)
ring = ring.fuse(revolve([(RING_CHAMFER_R, T1_LEN - 0.01), (R_ID + 0.5, T1_LEN - 0.01), (R_ID + 0.5, T1_LEN + (R_ID + 0.5 - RING_CHAMFER_R))]))
ring = ring.cut(tap(T1, 0.0, -1.5, T1_LEN + 0.01))
ring = ring.cut(countersink(T1['d'] / 2 + THREAD_CLEAR, T1_LEN, 1.0))
ring = ring.cut(cyl(14.0, -4, 0))
r_tap_core = T1['d'] / 2 + THREAD_CLEAR - T1['depth']            # 16.1: bore of the tapped ring
ring = ring.cut(revolve([(0, -1.5 + 0.01), (r_tap_core, -1.5 + 0.01), (14.0, -1.5 - (r_tap_core - 14.0)), (0, -1.5 - (r_tap_core - 14.0))]))  # 45 deg, no flat ledge nose-down
fw = fw.fuse(ring)
# under the ring: full bore for the harness bight, then a 45 deg cone down to the spigot ID
fw = fw.fuse(revolve([(SPIGOT_RI, zj), (R_ID + 0.5, zj), (R_ID + 0.5, zj + (R_ID + 0.5 - SPIGOT_RI))]))
fw = fw.fuse(cyl(SPIGOT_RO, zst(ST_SPIGOT_END), zj + 0.01).cut(cyl(SPIGOT_RI, zst(ST_SPIGOT_END) - 1, zj + 1)))
# harness grooves at +/-y through ring + chamfer, clipped to the bore (the wall stays whole)
g_top = T1_LEN + (R_ID + 0.5 - RING_CHAMFER_R) + 0.5
for sy in (1, -1):
    fw = fw.cut(box(-1.5, 1.5, 18.25 if sy > 0 else -R_ID, R_ID if sy > 0 else -18.25, -5, g_top))
# RBF pin holes (x), same size as the test stand
fw = fw.cut(xcyl(PIN_D / 2 + 0.15, -30, 30, z=Z_PIN))
for a in JOINT_ANG:
    fw = fw.cut(radial_cyl(1.6, SPIGOT_RI - 1, SPIGOT_RO + 1, zst(JOINT_SCREW_ST), a))
fw = fw.cut(revolve([(R_ID - 0.01, zst(0.0) - EF_CHAMFER), (R_ID + EF_CHAMFER + 0.01, zst(0.0) + 0.01), (R_ID - 0.01, zst(0.0) + 0.01)]))   # bed-side ID lead-in
fw = fw.removeSplitter()
assert fw.isValid() and len(fw.Solids) == 1
N['fwd_section'] = fw

# ---------------- E-BAY SECTION
ze = zst(ST_FINCAN_SHOULDER)
eb = cyl(R_OD, ze, zj).cut(cyl(R_ID, ze - 1, zj + 1))
eb = eb.fuse(cyl(R_ID + 0.5, zst(BAND_END), zj).cut(cyl(BAND_RI, zst(BAND_END) - 1, zj + 1)))
eb = eb.fuse(revolve([(BAND_RI, zst(BAND_END) + 0.01), (R_ID + 0.5, zst(BAND_END) + 0.01), (R_ID + 0.5, zst(BAND_END) - (R_ID + 0.5 - BAND_RI))]))
for a in JOINT_ANG:
    eb = eb.cut(csk_cutter(zst(JOINT_SCREW_ST), a))
for p in (STATIC_PORT, SOUND_PORT):
    eb = eb.cut(radial_cyl(p['d'] / 2, R_ID - 1, R_OD + 1, p['zs'] + SLED_Z_OFF, p['ang']))
eb = eb.cut(revolve([(R_ID - 0.01, ze + EF_CHAMFER), (R_ID + EF_CHAMFER + 0.01, ze - 0.01), (R_ID - 0.01, ze - 0.01)]))   # bed-side ID lead-in over the fin-can lip
eb = eb.removeSplitter()
assert eb.isValid() and len(eb.Solids) == 1
N['ebay_section'] = eb

# ---------------- SLED (unchanged) placed
sled = _sled_s.translated(V(0, 0, SLED_Z_OFF))

# ---------------- SLED MOUNT: disc (pocketed over the sled's top) + 3 lugs for the joint screws
zd0, zd1 = DISC_ZS0 + SLED_Z_OFF, DISC_ZS1 + SLED_Z_OFF
sm = cyl(DISC_R, zd0, zd1)
top_slab = sled.common(box(-30, 30, -30, 30, zd0 + 0.01, zd1 + 1))
# pocket = the sled's own top, grown ~0.25 mm sideways and 0.3 up (translated copies: an offset
# shape is unreliable on this solid). Bounding boxes would swallow the ear bosses the disc sits on.
pk = [top_slab.translated(V(dx, dy, dz)) for dx, dy in ((0, 0), (0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25), (0.18, 0.18), (-0.18, 0.18), (0.18, -0.18), (-0.18, -0.18)) for dz in (-0.3, 0, 0.3)]
sm = sm.cut(pk[0].fuse(pk[1:]))
sm = sm.cut(cyl(LEAD_HOLE_R, zd0 - 1, zd1 + 1))
zl1 = zst(LUG_TOP_ST)
for a in JOINT_ANG:
    lug = cyl(LUG_RO, zd1 - 0.01, zl1).cut(cyl(LUG_RI, zd1 - 1, zl1 + 1))
    lug = lug.common(rot(box(0, 30, -LUG_W / 2, LUG_W / 2, zd1 - 1, zl1 + 1), a))
    sm = sm.fuse(lug)
for a in JOINT_ANG:
    sm = sm.cut(radial_cyl(1.25, LUG_RI - 1, LUG_RO + 1, zst(JOINT_SCREW_ST), a))    # M3 self-tap pilot
for x, y in SLED_SCREWS:
    sm = sm.cut(cyl(1.1, zd0 - 1, zd1 + 1, x=x, y=y))                               # M2 clearance
sm = sm.removeSplitter()
assert sm.isValid() and len(sm.Solids) == 1, "sled mount: %d solids" % len(sm.Solids)
N['sled_mount'] = sm

# ---------------- hardware + references
HW = {}
for i, a in enumerate(JOINT_ANG):
    HW['M3x8_csk_%d' % i] = csk_screw(zst(JOINT_SCREW_ST), a)
for i, (x, y) in enumerate(SLED_SCREWS):
    HW['M2x10_pan_%d' % i] = cyl(1.9, zd1, zd1 + 1.3, x=x, y=y).fuse(cyl(1.0, zd1 - 10.0, zd1 + 0.01, x=x, y=y))
fincan = Part.Shape(); fincan.read(FINCAN_STEP)
fincan.translate(V(0, 0, -168.0))
ENV = {n: f().translated(V(0, 0, SLED_Z_OFF)) for n, f in SL['COMPONENTS'] if n != 'Servo_SG90'}   # servo gone (no latch in T5)
ENV['ADXL375'] = ENV['ADXL375'].common(box(-30, 30, -30, 30, -200, SL['ADXL_CLEAR_Z'] + SLED_Z_OFF))  # board trimmed 0.7 mm (sled report [N])
print("integration geometry built in %.1f s" % (time.time() - t0))

# =====================================================================================
# CHECKS
# =====================================================================================
report = []
def rep(s): print(s); report.append(s)
def interference(parts, wl=()):
    bad = []
    ks = list(parts)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            if (a, b) in wl or (b, a) in wl: continue
            if not parts[a].BoundBox.intersect(parts[b].BoundBox): continue
            c = parts[a].common(parts[b])
            if c.Volume > 1e-3:
                bb = c.BoundBox
                bad.append((a, b, round(c.Volume, 3), "x%.1f..%.1f y%.1f..%.1f z%.2f..%.2f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)))
    return bad
rep("== T5 integration check report: chute bay + T5 ejector + e-bay ==")
rep("T5 source: %s" % os.path.basename(T5_SRC))
rep("Frame: T5 module z; station = 172 - z. Sled Zs -> z = Zs %+.1f. Fin can Zf -> z = Zf - 168." % SLED_Z_OFF)
rep("")
rep("STATION TABLE (mm from the top of the body tube)")
for s0, s1, what in ((0, 20, "nose shoulder engagement (plain 40 bore; nose + detent not in this build, DESIGN 7.4 open)"),
                     (20, 110, "canopy + Nomex (full bore)"),
                     (106.5, 106.5, "RBF pin, x axis, through fwd_section"),
                     (110, 172, "T5 module: piston top cocked 110, flange 158-162, base aft face 172"),
                     (162, 175.5, "T5 ring, integral to fwd_section (T1 female, harness grooves +/-y)"),
                     (175.5, 181, "harness bight + lead exit; 45 deg cone to the spigot"),
                     (181, 181, "FLUSH JOINT fwd_section / ebay_section (bench-service only, never a flight separation)"),
                     (181, 199, "spigot (fwd) inside screw band (e-bay); 3 x M3 CSK at station 190 into sled_mount lugs"),
                     (185, 201.5, "sled_mount: lugs 185-199, disc 199-%.1f" % (172 - zd0)),
                     (172 - zd0, 172 - (SLED_Z_OFF - 0.9), "e-bay sled (Zs 45.4 -> -0.9)"),
                     (172 - (SLED_Z_OFF - 0.9), ST_FINCAN_BULKHEAD, "free: lead slack, battery pigtail"),
                     (ST_FINCAN_BULKHEAD, ST_FINCAN_SHOULDER, "fin-can lip inside ebay_section (bonded)"),
                     (ST_FINCAN_SHOULDER, 340, "AftFinCan (unchanged)")):
    rep("  %6.1f - %6.1f  %s" % (s0, s1, what))
rep("")

allp = dict(N); allp['sled_ref'] = sled
v = all(s.isValid() and len(s.Solids) == 1 for s in N.values())
rep("%s new printed parts valid, one solid each: %s" % (ok(v), ", ".join("%s %d" % (k, len(s.Solids)) for k, s in N.items())))

# --- flush
def rmax(shape):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    return max(math.hypot(p.x, p.y) for p in m.Points)
for k in ('fwd_section', 'ebay_section'):
    r = rmax(N[k]); rep("%s %s max radius %.3f <= OD/2 %.2f (nothing proud)" % (ok(r <= R_OD + 0.01), k, r, R_OD))
hr = max(rmax(HW['M3x8_csk_%d' % i]) for i in range(3))
rep("%s joint screw heads max radius %.3f <= %.2f (flush countersunk)" % (ok(hr <= R_OD + 0.01), hr, R_OD))
def od_at(shape, z):   # largest circular edge in the z-section (ignores fins / fillets)
    rs = [e.Curve.Radius for w in shape.slice(V(0, 0, 1), z) for e in w.Edges if 'Circle' in type(e.Curve).__name__]
    return max(rs) if rs else 0
steps = [("fwd/e-bay joint", od_at(N['fwd_section'], zj + 0.3), od_at(N['ebay_section'], zj - 0.3)),
         ("e-bay/fin-can joint", od_at(N['ebay_section'], ze + 0.3), od_at(fincan, ze - 3.0))]
for n, a, b in steps:
    rep("%s OD step at %s: %.3f vs %.3f (|d| <= 0.05)" % (ok(abs(a - b) <= 0.05), n, 2 * a, 2 * b))

# --- piston bore + canopy bay
sw_lo, sw_hi = Z_PU_C - SKIRT_H, Z_PU_F + PLATE_H
bore_hit = N['fwd_section'].common(cyl(R_MOVING_MAX + 0.05, sw_lo, sw_hi)).Volume
rep("%s piston sweep z %.1f-%.1f (stations %.1f-%.1f): nothing inside R %.2f (%.4f mm3)" % (ok(bore_hit < 1e-4), sw_lo, sw_hi, station(sw_hi), station(sw_lo), R_MOVING_MAX + 0.05, bore_hit))
cb = N['fwd_section'].common(cyl(R_ID - 0.01, zst(110), zst(0))).Volume
rep("%s chute bay stations 0-110 full 40 bore (%.4f mm3 inside R 19.99)" % (ok(cb < 1e-4), cb))

# --- interference states
core = dict(base=P['base'], rod=rod, **{'M2_' + k: vv for k, vv in heads.items()})
air = dict(fwd=N['fwd_section'], ebay=N['ebay_section'], mount=N['sled_mount'], sled=sled, fincan=fincan, **HW)
air.update({'env_' + k: vv for k, vv in ENV.items()})
WL = [('base', 'rod')] + [('M3x8_csk_%d' % i, 'mount') for i in range(3)] + [('M2x10_pan_%d' % i, 'sled') for i in range(2)]
WL += [('sled', 'env_SmallParts')]          # conformable allowance, yields to structure (sled report [I])
states = {
    'flight cocked, RBF pin in': dict(core, piston=piston_c, spring=spring_env(Z_PU_C), pin=pin, **air),
    'flight fired': dict(core, piston=piston_f, spring=spring_env(Z_PU_F), **air),
    'install from the front (tool on the cocked piston)': dict(core, piston=piston_c, spring=spring_env(Z_PU_C), tool=P['install_tool'], fwd=N['fwd_section']),
}
for name, parts in states.items():
    bad = interference(parts, wl=WL)
    rep("%s interference, %s: %s" % (ok(not bad), name, bad or "none"))
for i in range(3):
    ov = HW['M3x8_csk_%d' % i].common(N['sled_mount'])
    rr = [math.hypot(vv.X, vv.Y) for vv in ov.Vertexes]
    eng = max(rr) - min(rr) if rr else 0
    rep("%s joint screw %d: overlap with the lug is the M3 self-tap only (%.1f mm3), %.1f mm engaged (>= 3.5)" % (ok(eng >= 3.5 and ov.Volume < 40), i, ov.Volume, eng))
for i in range(2):
    ov = HW['M2x10_pan_%d' % i].common(sled)
    rep("%s sled screw %d: threads %.1f mm into the ex-servo-ear boss (%.1f mm3)" % (ok(ov.BoundBox.ZLength >= 4 if ov.Solids else False), i, ov.BoundBox.ZLength if ov.Solids else 0, ov.Volume))
tool_move = interference(dict(tool=P['install_tool'].translated(V(0, 0, 60)), fwd=N['fwd_section']))
rep("%s install tool passes the chute bay from the nose end: %s" % (ok(not tool_move), tool_move or "clear"))

# --- thread
em, ef, eb_ = engagement(P['base'], N['fwd_section'], T1, 2, 6)
rep("%s T1 base / integral ring engagement at mid-flank: male %.0f%%, female %.0f%%, both %.1f%%" % (ok(em > 0.2 and ef > 0.2 and eb_ == 0), 100 * em, 100 * ef, 100 * eb_))

# --- harness
g = N['fwd_section'].common(box(-1.4, 1.4, 18.35, 19.9, -3.4, T1_LEN)).Volume + N['fwd_section'].common(box(-1.4, 1.4, -19.9, -18.35, -3.4, T1_LEN)).Volume
skin = R_OD - math.hypot(1.5, R_ID)
rep("%s harness grooves open through the ring (%.4f mm3), skin behind them %.2f mm (wall not cut)" % (ok(g < 1e-4 and skin >= 1.4), g, skin))
hg = AIRFRAME_ID / 2 - PISTON_FLAT / math.cos(math.radians(CLOCK_TOL_DEG))
rep("%s harness passes the piston flat with %.2f mm even %.0f deg off the grooves (unchanged from T5)" % (ok(hg >= HARNESS_T + 0.3), hg, CLOCK_TOL_DEG))
bight = zst(175.5) - (zj + (R_ID - SPIGOT_RI))
rep("%s full-bore gap under the ring for the harness bight: %.1f mm (>= 2 x %.1f harness)" % (ok(bight >= 2 * HARNESS_T - 1e-6), bight, HARNESS_T))

# --- lead path
lead = cyl(2.5, zd0 - 2.0, 0.0)
hits = [k for k, s in dict(fwd=N['fwd_section'], ebay=N['ebay_section'], mount=N['sled_mount'], base=P['base'], sled=sled, **HW).items() if s.common(lead).Volume > 1e-4]
rep("%s lead path (d5 on the axis) chamber mouth -> ring -> lugs -> disc -> sled: %s" % (ok(not hits), hits or "clear"))
nich_d = min(nichrome.distToShape(s)[0] for s in (N['sled_mount'], sled))
rep("%s nichrome to nearest e-bay part: %.1f mm (>= 5)" % (ok(nich_d >= 5), nich_d))

# --- extraction / fit radii
rep("%s sled (R %.2f) passes the e-bay screw band (R %.2f): %.2f mm radial (tight, same as cassette v1: needs a round tube)" % (ok(BAND_RI - SL['SLED_RMAX'] >= 0.25), SL['SLED_RMAX'], BAND_RI, BAND_RI - SL['SLED_RMAX']))
rep("%s sled_mount disc R %.2f passes the band: %.2f mm" % (ok(BAND_RI - DISC_R >= 0.25), DISC_R, BAND_RI - DISC_R))
rep("%s spigot R %.2f in band R %.2f: %.2f mm radial (register)" % (ok(0.1 <= BAND_RI - SPIGOT_RO <= 0.3), SPIGOT_RO, BAND_RI, BAND_RI - SPIGOT_RO))
rep("%s lug R %.2f in spigot R %.2f: %.2f mm radial" % (ok(0.1 <= SPIGOT_RI - LUG_RO <= 0.3), LUG_RO, SPIGOT_RI, SPIGOT_RI - LUG_RO))
rep("%s e-bay bore R %.2f over fin-can lip R %.2f: %.2f mm diametral epoxy gap (AFT_RETENTION 0.3)" % (ok(abs(2 * (R_ID - FINCAN_LIP_R) - 0.3) < 0.01), R_ID, FINCAN_LIP_R, 2 * (R_ID - FINCAN_LIP_R)))
lipz = fincan.common(cyl(R_ID + 0.3, ze + 0.01, ze + 20)).BoundBox.ZMax - ze
rep("%s fin-can lip reaches %.1f mm into the e-bay section, its bulkhead %.1f mm below the sled" % (ok(lipz > 5), lipz, sled.BoundBox.ZMin - fincan.BoundBox.ZMax))
sp = N['ebay_section'].common(radial_cyl(0.5, R_ID - 2, R_OD + 1, STATIC_PORT['zs'] + SLED_Z_OFF, 0)).Volume
blk = [k for k, s in dict(sled=sled, **ENV).items() if s.common(radial_cyl(1.5, 15.0, R_ID, STATIC_PORT['zs'] + SLED_Z_OFF, 0)).Volume > 1e-3]
rep("%s static port d%.1f open at station %.1f, nothing in front of it inside the bay: %s" % (ok(sp < 1e-6 and not blk), STATIC_PORT['d'], station(STATIC_PORT['zs'] + SLED_Z_OFF), blk or "clear"))
snd = N['ebay_section'].common(radial_cyl(1.0, R_ID - 1, R_OD + 1, SOUND_PORT['zs'] + SLED_Z_OFF, 0)).Volume
rep("%s sound port d%.1f open at station %.1f, in line with the sled's piezo port" % (ok(snd < 1e-6), SOUND_PORT['d'], station(SOUND_PORT['zs'] + SLED_Z_OFF)))

# --- joint retention (OPEN until DESIGN 7.3 / 7.9 test 4 give a snatch load)
bear = 3 * 3.0 * (R_OD - BAND_RI)
rep("OPEN joint retention at %.0f N placeholder snatch (the harness anchors in fwd_section, so these 3 screws carry the whole aft section):" % JOINT_SNATCH_N)
rep("     band bearing %.1f mm2 -> %.1f MPa vs ~40; spigot bearing -> %.1f MPa; M3 shear %.1f MPa vs 250. Edge distance to the joint %.1f mm = %.1f d."
    % (bear, JOINT_SNATCH_N / bear, JOINT_SNATCH_N / (3 * 3.0 * (SPIGOT_RO - SPIGOT_RI)), JOINT_SNATCH_N / (3 * math.pi * 1.25 ** 2), JOINT_SCREW_ST - ST_JOINT, (JOINT_SCREW_ST - ST_JOINT) / 3.0))

rep("OPEN sled support: the sled now hangs from 2 x M2 in the ex-SG90 ear bosses (on 0.9 mm cradle uprights); its aft end is free, %.0f mm above the fin-can bulkhead."
    % (sled.BoundBox.ZMin - fincan.BoundBox.ZMax))
rep("     ~%.0f g x %.0f g boost = %.0f N on those bosses in tension. Bench pull-test the sled off the mount before flight; add an aft foam pad if it rattles." % (SLED_ELEC_G, BOOST_G, SLED_ELEC_G * 9.81e-3 * BOOST_G))
rep("OPEN baro air: the e-bay connects to the chute bay through the harness grooves (~10 mm2) and chamber holes; the chute bay vents via 2 x d4.3 RBF holes (~29 mm2)")
rep("     vs a %.1f mm2 static port, so the baro reads mostly chute-bay (station 106.5) pressure. Accepted as a static location; to isolate, seal the disc periphery with foam tape." % (math.pi * (STATIC_PORT['d'] / 2) ** 2))

# --- printability: orientation, bed, overhang scan
ORIENT = {'fwd_section': 'flip', 'ebay_section': 'up', 'sled_mount': 'up'}
LABEL = {'fwd_section': 'nose end down', 'ebay_section': 'aft end down', 'sled_mount': 'disc down, lugs up'}
def oriented(k, s):
    s = s.copy()
    if ORIENT.get(k) == 'flip': s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return s
THREAD_FLANK = []
def overhangs(s, nz_lim=-0.75, thread_band=None):
    """thread_band=(r0, r1): facets there with -0.80 < nz are T1 flanks (45 deg + 4.8 deg lead),
    reported separately, not as ceilings. Anything flatter (nz <= -0.80) is still flagged."""
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    pts = m.Points
    flagged = [f for f in m.Facets if f.Normal.z < nz_lim and min(pts[i].z for i in f.PointIndices) > 0.3]
    if thread_band:
        def in_band(f):
            return all(thread_band[0] <= math.hypot(pts[i].x, pts[i].y) <= thread_band[1] for i in f.PointIndices)
        fl = [f for f in flagged if f.Normal.z > -0.80 and in_band(f)]
        THREAD_FLANK.append((len(fl), sum(f.Area for f in fl), min((f.Normal.z for f in fl), default=0)))
        flagged = [f for f in flagged if not (f.Normal.z > -0.80 and in_band(f))]
    # connected components via shared points
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for f in flagged:
        i0 = f.PointIndices[0]
        for i in f.PointIndices[1:]: parent[find(i)] = find(i0)
    comp = {}
    for f in flagged:
        comp.setdefault(find(f.PointIndices[0]), []).append(f)
    out = []
    for fs in comp.values():
        ps = [pts[i] for f in fs for i in f.PointIndices]
        xs, ys, zs_ = [p.x for p in ps], [p.y for p in ps], [p.z for p in ps]
        rs = [math.hypot(p.x, p.y) for p in ps]
        out.append(dict(area=sum(f.Area for f in fs), z=(min(zs_) + max(zs_)) / 2, z0=min(zs_), z1=max(zs_), r0=min(rs), r1=max(rs),
                        span=min(max(xs) - min(xs), max(ys) - min(ys)), radial=max(rs) - min(rs),
                        ledge=sum(f.Area for f in fs) / (math.pi * (min(rs) + max(rs)))))   # mean annular width
    return out
for k, s in N.items():
    o = oriented(k, s); bb = o.BoundBox
    fits = bb.XLength <= BED[0] and bb.YLength <= BED[1] and bb.ZLength <= BED[2]
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm (bed %g x %g x %g)" % (ok(fits), k, LABEL[k], bb.XLength, bb.YLength, bb.ZLength, *BED))
    THREAD_FLANK.clear()
    oh = overhangs(o, thread_band=(r_tap_core - 0.25, T1['d'] / 2 + THREAD_CLEAR + 0.05) if k == 'fwd_section' else None)
    if THREAD_FLANK and THREAD_FLANK[0][0]:
        n_, a_, nz_ = THREAD_FLANK[0]
        rep("NOTE fwd_section: %d T1 thread-flank facets (%.0f mm2), steepest %.1f deg from horizontal (45 deg flank tilted by the 4.8 deg lead); the same thread prints on the T5 base/stand/coupon. Print the coupon first."
            % (n_, a_, math.degrees(math.acos(-nz_))))
    bad = [c for c in oh if c['span'] > 10.0 and c['ledge'] > 2.0]
    worst = max(oh, key=lambda c: c['area']) if oh else None
    rep("%s %s overhangs steeper than ~49 deg: %d patches, %.1f mm2 total; all bridges (span <= 10) or ring ledges (mean width <= 2)%s%s"
        % (ok(not bad), k, len(oh), sum(c['area'] for c in oh),
           "; largest %.1f mm2 at print z %.1f (span %.1f, ledge %.2f)" % (worst['area'], worst['z'], worst['span'], worst['ledge']) if worst else "",
           "; BAD: %s" % [dict((kk, round(vv, 2)) for kk, vv in c.items()) for c in bad] if bad else ""))
so = overhangs(_sled_s.translated(V(0, 0, -_sled_s.BoundBox.ZMin)))    # on the bed, aft end down (best of 6 orientations)
rep("NOTE sled v1 (unchanged) aft-end-down: %d overhang patches, %.0f mm2; spans > 10 mm: %s (the ex-servo cradle shelf) -> support there or accept a bridge"
    % (len(so), sum(c['area'] for c in so), [(round(c['z'], 1), round(c['span'], 1)) for c in so if c['span'] > 10]))

# --- masses
for k, s in N.items():
    rep("Mass %s (PETG solid) %.1f g" % (k, s.Volume * RHO_PETG))
old = P['flight_bulkhead'].Volume * RHO_PETG
rep("NOTE fwd_section + ebay_section replace 288.6 mm of body tube and the bonded t5_flight_bulkhead (%.1f g); tube alone at 43/40 solid: %.1f g" % (old, math.pi * (R_OD ** 2 - R_ID ** 2) * ST_FINCAN_SHOULDER * RHO_PETG))
rep("NOTE no stability claim: masses feed DESIGN 13 item 3 (OpenRocket re-run).")
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(OUT_PRINT, exist_ok=True)
doc = App.newDocument("T5_Integration")
for k, s in N.items(): doc.addObject("Part::Feature", k).Shape = s
for k, s in HW.items(): doc.addObject("Part::Feature", "HW_" + k).Shape = s
for k, s in (('T5_base', P['base']), ('T5_piston_cocked', piston_c), ('T5_rod', rod), ('T5_rbf_pin', pin), ('REF_sled_v1', sled), ('REF_AftFinCan', fincan)):
    doc.addObject("Part::Feature", k).Shape = s
doc.recompute()
doc.saveAs(os.path.join(OUT_MODELS, "t5_integration.FCStd"))
Part.makeCompound(list(N.values()) + [P['base'], piston_c, rod, pin, sled, fincan] + list(HW.values())).exportStep(os.path.join(OUT_MODELS, "t5_integration_assembly.step"))
for k, s in N.items():
    MeshPart.meshFromShape(Shape=oriented(k, s), LinearDeflection=0.02, AngularDeflection=0.3, Relative=False).write(os.path.join(OUT_PRINT, "t5i_%s.stl" % k))

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(12, 22))
    shapes = [(N['fwd_section'], 'tab:blue'), (N['ebay_section'], 'tab:cyan'), (N['sled_mount'], 'tab:orange'), (sled, 'tab:brown'),
              (P['base'], 'navy'), (piston_c, 'tab:red'), (rod, 'k'), (pin, 'tab:purple'), (spring_env(Z_PU_C, SPRING_OD), 'tab:green'),
              (fincan, '0.5')] + [(s, 'k') for s in HW.values()]
    for ax, (title, plane) in zip(axs, (("section y=0 (RBF pin axis), cocked", V(0, 1, 0)), ("section x=0 (harness grooves), cocked", V(1, 0, 0)))):
        for s, c in shapes:
            for e in s.slice(plane, 0.7):      # off the RBF-hole axis (slicing through it drops the tube)
                pts = e.discretize(Deflection=0.05)
                ax.plot([p.x if plane.y else p.y for p in pts], [172 - p.z for p in pts], color=c, lw=0.6)
        ax.set_aspect('equal'); ax.set_title(title); ax.grid(alpha=0.2); ax.set_ylim(300, -5); ax.set_ylabel("station (mm)")
    fig.savefig(os.path.join(OUT_MODELS, "t5_integration_section.png"), dpi=130, bbox_inches='tight')
except Exception as ex:
    print("section plot skipped:", ex)

with open(os.path.join(OUT_MODELS, "t5_integration_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t0))

# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v2: D9aft v1 + SCREW-ON NOSE v6, TOOL-FREE E-BAY, BULKHEAD EYELET.

What changes from v1 (everything else is v1, reused read-only by exec'ing v1 up to its CHECKS banner):
  nose     v6 (Nosecone/PhoenixABS40-43_Nosecone_v6.py): plain Von Karman shell + 9.5 mm male thread.
           No screws. Unscrew by hand.
  FwdTube  female thread in the mouth (crest d39.30, so the e-bay passes), e-bay SEAT RING, spigot +
           gas-tight bulkhead moved forward to sit right behind the e-bay, and a central RECESSED EYELET
           BAR in the bulkhead's aft face (tie a permanent Kevlar leader to it BEFORE bonding).
  e-bay    EbayCap (was SledMount): the sled screws to it (2 x M2, as before); it has a finger/string pull
           loop and a witness notch. The stack e-bay sits on the seat ring and is held down by a foam
           ring under the nose shoulder -- no screws through the wall.
  AftTube  starts at the new joint; the wall harness lug is GONE (anchor is the bulkhead eyelet), so the
           canopy's exit path is a clean 40 bore. Launch lug + pin slots as v1.
  unchanged  fin can, shear pins, pin card + coupons, cap, motor: use the D9aft v1 files for those.

Thread: aft_retention_v1's faceted helix. OCCT booleans against threaded solids are not trusted, so the
thread pair is checked by sampled isInside (fill + clash, unscrew sweep, negative control), and every
other fit check uses thread-free proxies of the nose and the FwdTube.

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame: z = 340 - station, as v1. Any FAIL line means do not print.
"""
import os, math, time
t00 = time.time()
V1_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v1.py"
NOSE6_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Nosecone\PhoenixABS40-43_Nosecone_v6.py"
_v1 = open(V1_SRC, encoding="utf-8").read()
_c = _v1.index("\n# CHECKS\n"); _c = _v1.rfind("# ====", 0, _c)
exec(_v1[:_c])                                       # v1 parts (fin can real + proxy, pins, cap, motor, LL, helpers); nothing exported
NV = {"__name__": "nose_v6", "NOSE_V6_LIB": True}
exec(open(NOSE6_SRC, encoding="utf-8").read(), NV)
THREAD, THL = NV['THREAD'], NV['TH']
print("v1 + nose v6 libraries in %.1f s" % (time.time() - t00), flush=True)

# ---------------- helpers that live in v1's CHECKS/MASS sections (not exec'd: they would re-export v1)
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
        out.append(dict(area=a, z=(min(zz) + max(zz)) / 2, span=min(max(xs) - min(xs), max(ys) - min(ys)), ledge=a / (math.pi * (min(rs) + max(rs)))))
    return out
def cg_z(shape):
    shs = shape.Solids if shape.Solids else [shape]
    vol = sum(s.Volume for s in shs)
    return sum(s.Volume * s.CenterOfMass.z for s in shs) / vol
def solid(nm, grp, shape, mat, note=""): items.append((nm, grp, shape.Volume * RHO[mat], cg_z(shape), "CAD x %s %.2f%s" % (mat, RHO[mat] * 1e3, note), shape))
def point(nm, grp, m, z, basis, shape=None): items.append((nm, grp, m, z, basis, shape))
def tot(sel):
    m = sum(i[2] for i in sel); return m, (sum(i[2] * i[3] for i in sel) / m if m else 0.0)
def fmt(z): return "st %6.1f (tip %6.1f)" % (station(z), station(z) + NOSE_LEN)
def draw(ax, s, c, dz=0.0, y_cut=0.7):
    cut = Part.Face(Part.makePolygon([V(-200, y_cut, -400), V(200, y_cut, -400), V(200, y_cut, 500), V(-200, y_cut, 500), V(-200, y_cut, -400)]))
    for e in s.section(cut).Edges:
        pts = e.discretize(Deflection=0.1)
        ax.plot([station(p.z + dz) + NOSE_LEN for p in pts], [p.x for p in pts], color=c, lw=0.5)
Z_MOTOR = (MOTOR_ZF[0] + MOTOR_ZF[1]) / 2
F_pin = TAU_ABS * PIN_A * PIN_BN
F_tot = PIN_N * F_pin
slot_v = PIN_N * (PIN_A + SLOT_CLR) * (PIN_B + SLOT_CLR) * (R_OD - 0.06 - R_ID - 0.01)
rod = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=LL_C - (LL_RI - ROD_R)), LL_ANG)
cap_env = cyl(CAP_RIB_R, cap.BoundBox.ZMin - 0.1, cap.BoundBox.ZMax + 0.1)

NAME2 = "PhoenixABS40-43_D9aft_v2"
REV2 = "D9aft_v2"
report = []

# =====================================================================================
# PARAMETERS (v2)
# =====================================================================================
PITCH = THREAD['PITCH']
CREST, ROOT = THREAD['CAP_T_CREST_R'], THREAD['CAP_T_ROOT_R']     # female 19.65 / 20.45
MAJOR, MINOR = THREAD['BOSS_R_MAJOR'], THREAD['BOSS_R_MINOR']     # male 20.25 / 19.45
NOSE_SH_END_ST = NV['SH_LEN']                        # 9.5: nose shoulder end face
TH_CH_END = 11.0                                     # female channel runs to here (1.5 past the male end)
BAND_END = 12.5                                      # crest band (bore d39.30) ends; bore 40 below
FOAM_GAP = 1.0                                       # 2 mm closed-cell foam ring, compressed to 1 mm
S_DISC_TOP = NOSE_SH_END_ST + FOAM_GAP               # 10.5
SLED_Z2 = zs(S_DISC_TOP) - DISC_ZS1                  # sled frame: disc top at station 10.5
DZ_EBAY = SLED_Z2 - SLED_Z
SEAT_RI, SEAT_T = 15.5, 2.0                          # seat ring: flat top, 45 deg underside
BH_T2 = 2.5
SPIGOT_LEN2 = 16.0
EY_POCKET = (8.0, 2.5, 6.5)                          # half-x, half-y, depth from the aft face
EY_BAR = (3.0, 3.0)                                  # half-x, thickness (flush with the aft face)
EY_BOSS = (10.0, 4.5, 9.5)                           # half-x, half-y, height from the aft face
LOOP = dict(x0=-8.5, x1=7.7, post=2.5, y=2.5, h=14.0, top=3.0)   # EbayCap pull loop (clear of the M2 heads)

# ---------------- e-bay stack
sled2 = sled.translated(V(0, 0, DZ_EBAY))
ENV2 = {k: v.translated(V(0, 0, DZ_EBAY)) for k, v in ENV.items()}
S_SEAT = station(min(s.BoundBox.ZMin for s in [sled2] + list(ENV2.values())))   # the e-bay stands on the seat
J2 = S_SEAT + SEAT_T + (SPIGOT_RI - SEAT_RI)         # outer joint
S_BH2 = J2 + SPIGOT_LEN2                             # bulkhead aft face = chute-bay forward wall
z_b = zs(S_BH2)

# ---------------- nose v6 placed (+ thread-free proxy)
def place_nose(s):
    s = s.copy(); s.rotate(V(0, 0, 0), V(1, 0, 0), 180.0); s.translate(V(0, 0, BODY_LEN + NOSE_LEN)); return s
nose6 = place_nose(NV['build_nose'](True))
nose6_px = place_nose(NV['build_nose'](False))

# ---------------- FWD TUBE v2
fw = rst([(CREST, 0.0), (R_OD, 0.0), (R_OD, J2), (SPIGOT_RO, J2), (SPIGOT_RO, S_BH2 - EF), (SPIGOT_RO - EF, S_BH2),
          (0.0, S_BH2), (0.0, S_BH2 - BH_T2), (SPIGOT_RI, S_BH2 - BH_T2), (SPIGOT_RI, S_SEAT + SEAT_T + (SPIGOT_RI - SEAT_RI)),
          (SEAT_RI, S_SEAT + SEAT_T), (SEAT_RI, S_SEAT), (R_ID, S_SEAT), (R_ID, BAND_END + (R_ID - CREST)), (CREST, BAND_END)])
# recessed eyelet: boss forward of the bulkhead, blind pocket from the aft face, tie bar flush with the aft face
fw = fw.fuse(box(-EY_BOSS[0], EY_BOSS[0], -EY_BOSS[1], EY_BOSS[1], zs(S_BH2 - BH_T2) - 0.3, z_b + EY_BOSS[2]))
fw = fw.cut(box(-EY_POCKET[0], EY_POCKET[0], -EY_POCKET[1], EY_POCKET[1], z_b - 1.0, z_b + EY_POCKET[2]))
fw = fw.fuse(box(-EY_BAR[0], EY_BAR[0], -EY_POCKET[1] - 0.3, EY_POCKET[1] + 0.3, z_b, z_b + EY_BAR[1]))
for p in (STATIC_PORT, SOUND_PORT):
    fw = fw.cut(radial_cyl(p['d'] / 2, R_ID - 1, R_OD + 1, p['zs'] + SLED_Z2, p['ang']))
fw = fw.cut(box(R_OD - 0.4, R_OD + 1, -0.5, 0.5, zs(2.0), zs(0.0) + 1))       # witness notch at 0 deg (sound port side)
fw_px = fw.removeSplitter()
fw_px = fw_px.Solids[0] if len(fw_px.Solids) == 1 else fw_px
T_ANCHOR_A = (BODY_LEN + NOSE_LEN - NV['T_ANCHOR_N']) - 6 * PITCH                 # male ridge centres map here (theta 0)
_ch = THL['thread_solid'](CREST, T_ANCHOR_A, (zs(-1.0) - T_ANCHOR_A) + PITCH, THL['channel_profile']())
_ch = _ch.common(revolve([(CREST - THREAD['T_MERGE'], zs(TH_CH_END)), (ROOT + THREAD['T_MERGE'], zs(TH_CH_END)),
                          (ROOT + THREAD['T_MERGE'], zs(-1.0)), (CREST - THREAD['T_MERGE'], zs(-1.0))]))
fw2 = THL['as_solid'](fw_px.cut(_ch))                # REAL: faceted female thread, no removeSplitter
P2 = {'FwdTube': fw2}

# ---------------- AFT TUBE v2 (v1 minus the wall lug, new forward end)
at = rst([(R_ID, J2), (R_OD, J2), (R_OD, ST_BODY_AFT), (R_ID, ST_BODY_AFT)])
at = at.cut(rst([(R_ID - 0.01, J2 + EF + 0.01), (R_ID + EF + 0.01, J2 - 0.01), (R_ID - 0.01, J2 - 0.01)]))
at = at.cut(rst([(R_ID - 0.01, ST_BODY_AFT - EF - 0.01), (R_ID + EF + 0.01, ST_BODY_AFT + 0.01), (R_ID - 0.01, ST_BODY_AFT + 0.01)]))
at = at.fuse(LL)
for a in PIN_ANG:
    at = at.cut(pin_slot(a, Z_PIN))
P2['AftTube'] = at.removeSplitter()

# ---------------- EBAY CAP (v1 sled-mount disc, no lugs; pull loop; witness notch)
zd0, zd1 = DISC_ZS0 + SLED_Z2, DISC_ZS1 + SLED_Z2
ec = cyl(DISC_R, zd0, zd1)
top_slab = sled2.common(box(-30, 30, -30, 30, zd0 + 0.01, zd1 + 1))
pk = [top_slab.translated(V(dx, dy, dz)) for dx, dy in ((0, 0), (0.25, 0), (-0.25, 0), (0, 0.25), (0, -0.25), (0.18, 0.18), (-0.18, 0.18), (0.18, -0.18), (-0.18, -0.18)) for dz in (-0.3, 0, 0.3)]
ec = ec.cut(pk[0].fuse(pk[1:]))
for x, y in SLED_SCREWS:
    ec = ec.cut(cyl(1.1, zd0 - 1, zd1 + 1, x=x, y=y))
L_ = LOOP
for xa in (L_['x0'], L_['x1'] - L_['post']):
    ec = ec.fuse(box(xa, xa + L_['post'], -L_['y'], L_['y'], zd1 - 0.3, zd1 + L_['h']))
ec = ec.fuse(box(L_['x0'], L_['x1'], -L_['y'], L_['y'], zd1 + L_['h'] - L_['top'], zd1 + L_['h']))
ec = ec.cut(box(DISC_R - 0.8, DISC_R + 1, -0.5, 0.5, zd1 - 1.0, zd1 + 1))        # witness notch at 0 deg
ec = ec.removeSplitter()
P2['EbayCap'] = ec.Solids[0] if len(ec.Solids) == 1 else ec
HW2 = {'M2x10_pan_%d' % i: cyl(1.9, zd1, zd1 + 1.3, x=x, y=y).fuse(cyl(1.0, zd1 - 10.0, zd1 + 0.01, x=x, y=y)) for i, (x, y) in enumerate(SLED_SCREWS)}
print("v2 parts built in %.1f s" % (time.time() - t00), flush=True)

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: D9aft v1 + screw-on nose v6, tool-free e-bay, bulkhead eyelet ==" % REV2)
rep("Frame z = %.0f - station (station 0 = nose base). Threaded parts: pair checked by sampling; fits on thread-free proxies." % BODY_LEN)
rep("")
rep("STATION TABLE")
for s0, s1, what in ((-65, 0, "nose v6 (Von Karman shell, %.1f g), screws in -- never separates in flight" % (nose6.Volume * RHO['ABS'])),
                     (0, NOSE_SH_END_ST, "thread: male on the nose shoulder, female in the FwdTube mouth (pitch %.1f, 45 deg, %.1f turns)" % (PITCH, NOSE_SH_END_ST / PITCH)),
                     (NOSE_SH_END_ST, S_DISC_TOP, "foam ring 2 -> 1 mm (holds the e-bay down, stops rattle/rotation)"),
                     (S_DISC_TOP, S_DISC_TOP + (DISC_ZS1 - DISC_ZS0), "EbayCap disc; pull loop rises %.0f mm forward into the nose" % LOOP['h']),
                     (station(sled2.BoundBox.ZMax), S_SEAT, "e-bay sled v1 (unchanged), standing on the seat ring"),
                     (S_SEAT, J2, "seat ring (flat top) -> spigot"),
                     (J2, J2, "BONDED joint FwdTube / AftTube"),
                     (S_BH2 - BH_T2, S_BH2, "gas-tight bulkhead with the recessed EYELET BAR in its aft face"),
                     (S_BH2, station(BH_Z1), "CHUTE BAY %.0f mm -- clean bore, no wall lug" % (station(BH_Z1) - S_BH2)),
                     (LL_ST0, LL_ST1, "launch lug (v1), rod line r %.2f" % LL_C),
                     (station(CPL_Z1), ST_BODY_AFT, "fin-can coupler, slip fit, 2 shear pins at station %.1f (v1)" % PIN_ST),
                     (ST_BODY_AFT, BODY_LEN, "fin can + D9 + cap (v1, unchanged)")):
    rep("  %7.1f - %7.1f  %s" % (s0, s1, what))
rep("")
for k, s in (('nose v6', nose6), ('FwdTube', P2['FwdTube']), ('FwdTube proxy', fw_px), ('AftTube', P2['AftTube']), ('EbayCap', P2['EbayCap'])):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))

# --- female thread landed on the REAL FwdTube (probes at theta 0: channel centres vs ridge centres)
zc = T_ANCHOR_A + 4 * PITCH                                             # a channel centre inside the band
tp = [("channel open at the crest radius", V(CREST + 0.15, 0, zc), False),
      ("channel open near the root", V(ROOT - 0.15, 0, zc), False),
      ("female ridge solid between channels", V(CREST + 0.15, 0, zc + PITCH / 2), True),
      ("skin solid behind the root", V(ROOT + 0.5, 0, zc), True),
      ("bore below the band is d40", V(R_ID - 0.15, 0, zs(BAND_END + 3)), False),
      ("band ends: no thread past station %.0f" % TH_CH_END, V(ROOT - 0.15, 0, zs(TH_CH_END + 0.6)), True)]
bad = [(n, w) for n, p, w in tp if inside(P2['FwdTube'], p) != w]
assert zs(TH_CH_END) < zc - 1.0 and zc + PITCH / 2 < zs(0.0), "thread probes must sit inside the band"
rep("%s REAL FwdTube female thread: %d/%d probes as designed (channel centre at station %.1f)%s" % (ok(not bad), len(tp) - len(bad), len(tp), station(zc), "; WRONG %s" % bad if bad else ""))

# --- thread pair: sampled fill + clash, seated and through the unscrew sweep; negative control
t1 = time.time()
SAMP = [pol(r, a + 0.37, zs(s)) for r in (19.80, 20.05) for a in range(0, 360, 15) for s in [0.6 + 0.6 * i for i in range(14)]]   # 672 pts: isInside on the faceted thread is slow
in_t = [inside(P2['FwdTube'], p) for p in SAMP]
def nose_at(phi, extra_dz=0.0):
    s = nose6.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), phi); s.translate(V(0, 0, PITCH * phi / 360.0 + extra_dz)); return s
def clash(ns):
    inn = [inside(ns, p) for p in SAMP]
    c = sum(1 for a, b in zip(in_t, inn) if a and b)
    return c, sum(inn)
print("  tube samples done (%.0f s)" % (time.time() - t1), flush=True)
c0, n0 = clash(nose6)
print("  seated done (%.0f s)" % (time.time() - t1), flush=True)
ft, fn = sum(in_t) / len(SAMP), n0 / len(SAMP)
rep("%s thread SEATED: clash %d of %d samples in the interlock band r 19.80/20.05; fill tube %.0f%% / nose %.0f%% (both > 20%% = interlocked)"
    % (ok(c0 == 0 and ft > 0.2 and fn > 0.2), c0, len(SAMP), 100 * ft, 100 * fn))
sweep = []
for phi in (180, 360):
    c, n = clash(nose_at(phi)); sweep.append((phi, c, n)); print("  sweep %d deg: clash %d (%.0f s)" % (phi, c, time.time() - t1), flush=True)
rep("%s unscrew sweep (rotate + advance %.1f mm/turn): clash %s  (phi, clash, nose fill samples)" % (ok(all(c == 0 for _, c, _ in sweep)), PITCH, sweep))
cn, _ = clash(nose_at(180.0, extra_dz=-PITCH * 0.5))                   # half a pitch out of phase: must clash
rep("%s NEGATIVE CONTROL: nose half a pitch out of phase -> clash %d samples (must be > 0, or the check cannot fail)" % (ok(cn > 20), cn))
rep("NOTE thread sampling took %.0f s" % (time.time() - t1))
rep("%s nose base seats on the tube mouth face: contact annulus r %.2f..%.2f (%.2f mm wide) at station 0" % (ok(R_OD - ROOT >= 1.0), ROOT, R_OD, R_OD - ROOT))

# --- e-bay access: everything passes the thread crests
rr = max(SL['SLED_RMAX'], DISC_R, math.hypot(max(abs(LOOP['x0']), abs(LOOP['x1'])), LOOP['y']))
rep("%s e-bay lifts out of the mouth: largest radius %.2f (sled) vs thread crest %.2f -> %.2f mm radial" % (ok(CREST - rr >= 0.25), rr, CREST, CREST - rr))
rep("%s stack: nose shoulder end st %.1f, EbayCap top st %.1f -> %.1f mm for the foam ring; e-bay stands on the seat at st %.1f"
    % (ok(abs(S_DISC_TOP - NOSE_SH_END_ST - FOAM_GAP) < 1e-6), NOSE_SH_END_ST, station(P2['EbayCap'].BoundBox.ZMax - LOOP['h']), FOAM_GAP, S_SEAT))
tch = sled2.common(fw_px).Volume + sum(e.common(fw_px).Volume for e in ENV2.values())
rep("%s sled/electronics against the seat ring and bore: %.4f mm3 overlap (contact only)" % (ok(tch < 1e-2), tch))

# --- interference, flight (proxies)
air2 = dict(nose=nose6_px, fwd=fw_px, aft=P2['AftTube'], ebaycap=P2['EbayCap'], sled=sled2, fincan=fincan_px, motor=motor, **HW2, **PINS)
air2.update({'env_' + k: v for k, v in ENV2.items()})
WL2 = {('nose', 'fwd'), ('sled', 'env_SmallParts')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)}
bad = interference(air2, WL2)
rep("%s interference, flight (thread pair checked above): %s" % (ok(not bad), bad or "none"))
lp = nose6_px.common(P2['EbayCap']).Volume
rep("%s EbayCap pull loop clear of the nose interior (%.3f mm3); loop opening %.1f x %.1f mm" % (ok(lp < 1e-3), lp, LOOP['x1'] - LOOP['x0'] - 2 * LOOP['post'], LOOP['h'] - LOOP['top']))

# --- bulkhead + eyelet
roof = fw_px.common(box(-EY_POCKET[0], EY_POCKET[0], -EY_POCKET[1], EY_POCKET[1], z_b + EY_POCKET[2] + 0.01, z_b + EY_BOSS[2] - 0.01))
roof_v = (2 * EY_POCKET[0]) * (2 * EY_POCKET[1]) * (EY_BOSS[2] - EY_POCKET[2] - 0.02)
plate = fw_px.common(cyl(SPIGOT_RI - 0.05, z_b + 0.01, zs(S_BH2 - BH_T2) - 0.01).cut(box(-EY_POCKET[0], EY_POCKET[0], -EY_POCKET[1], EY_POCKET[1], z_b - 1, z_b + 20)))
plate_v = math.pi * (SPIGOT_RI - 0.05) ** 2 * (BH_T2 - 0.02) - (2 * EY_POCKET[0]) * (2 * EY_POCKET[1]) * (BH_T2 - 0.02)
rep("%s bulkhead gas-tight: pocket is blind (roof %.1f of %.1f mm3 solid, %.1f mm thick), plate around it solid (%.1f of %.1f mm3)"
    % (ok(abs(roof.Volume - roof_v) < 0.5 and abs(plate.Volume - plate_v) < 0.5), roof.Volume, roof_v, EY_BOSS[2] - EY_POCKET[2], plate.Volume, plate_v))
ep = [("bar solid", V(0, 0, z_b + 1.5), True), ("tunnel open over the bar", V(0, 0, z_b + EY_BAR[1] + 1.5), False),
      ("window open beside the bar", V(-5.5, 0, z_b + 1.0), False), ("window open other side", V(5.5, 0, z_b + 1.0), False)]
bad = [(n, w) for n, p, w in ep if inside(fw_px, p) != w]
tun_h = EY_POCKET[2] - EY_BAR[1]
rep("%s eyelet: %d/%d probes; cord path = down a %.0f x %.0f window, through a %.1f x %.0f tunnel over the bar, out the other window%s"
    % (ok(not bad), len(ep) - len(bad), len(ep), EY_POCKET[0] - EY_BAR[0], 2 * EY_POCKET[1], tun_h, 2 * EY_POCKET[1], "; WRONG %s" % bad if bad else ""))
sig = SNATCH_N * (2 * EY_POCKET[1]) / 8.0 / ((2 * EY_BAR[0]) * EY_BAR[1] ** 2 / 6.0)
rep("%s eyelet bar at the %.0f N placeholder: %.0f x %.0f bar, %.0f mm span, fixed-fixed bending %.1f MPa (in-layer, printed flat on the bed; ABS ~35)"
    % (ok(sig < 20.0), SNATCH_N, 2 * EY_BAR[0], EY_BAR[1], 2 * EY_POCKET[1], sig))
rep("  the eyelet is exposed until the FwdTube is bonded: tie a permanent Kevlar leader to it first; its loop reaches the aft opening.")

# --- gas path, chute-bay wall, separation, launch rod
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, z_b - 0.5)
hits = [k for k, s in dict(fincan=fincan_px, aft=P2['AftTube'], fwd=fw_px).items() if s.common(gp).Volume > 1e-3]
rep("%s d%.0f gas column clear from the motor face to the bulkhead: %s" % (ok(not hits), 2 * PORT_R, hits or "clear"))
band = P2['AftTube'].common(rst([(R_ID + 0.01, S_BH2), (R_OD - 0.06, S_BH2), (R_OD - 0.06, ST_BODY_AFT - 1.0), (R_ID + 0.01, ST_BODY_AFT - 1.0)]))
ideal = math.pi * ((R_OD - 0.06) ** 2 - (R_ID + 0.01) ** 2) * (ST_BODY_AFT - 1.0 - S_BH2)
rep("%s chute-bay wall: missing %.2f mm3 vs %.2f of pin slots -> no other holes" % (ok(abs((ideal - band.Volume) - slot_v) < 0.3), ideal - band.Volume, slot_v))
bore = P2['AftTube'].common(cyl(R_ID - 0.01, zs(ST_BODY_AFT), z_b)).Volume
rep("%s canopy exit path: nothing inside the d40 bore from the bulkhead to the aft end (%.4f mm3)" % (ok(bore < 1e-3), bore))
sw = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if fincan_px.translated(V(0, 0, -d)).common(P2['AftTube']).Volume > 1e-3]
rep("%s separation sweep 0..%.0f mm: fin can never touches the aft tube %s" % (ok(not sw), CPL_LEN + 4, sw[:4] or ""))
hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod).Volume) for k, sh in dict(cap_ribs_any_clocking=cap_env, fincan=fincan_px, fwd=fw_px, nose=nose6_px).items()) if v > 1e-3]
rep("%s launch rod line clear of cap ribs, fins, FwdTube, nose: %s" % (ok(not hits), hits or "clear"))
rep("%s tube split: FwdTube %.1f mm, AftTube %.1f mm tall (bed %.0f)" % (ok(S_BH2 <= BED[2] and ST_BODY_AFT - J2 <= BED[2]), S_BH2, ST_BODY_AFT - J2, BED[2]))

# --- pins: v1 unchanged; the bay got bigger
V_bay1 = ST_BODY_AFT - (J + SPIGOT_LEN) + (CPL_Z1 - BH_Z1)
V_bay2 = ST_BODY_AFT - S_BH2 + (CPL_Z1 - BH_Z1)
rep("NOTE pins unchanged (v1: 2 x %.1f N = %.1f N). Chute bay is %.0f mm long (v1 %.0f): the same charge gives ~%.2fx the v1 pressure."
    % (F_pin, F_tot, station(BH_Z1) - S_BH2, station(BH_Z1) - (J + SPIGOT_LEN), V_bay1 / V_bay2))
rep("     If separation is weak on the first flight, drop to the 0.5 mm neck (card nick 1) before anything else.")

# --- printability
ORIENT2 = {'FwdTube': ('up', 'bulkhead (eyelet bar) down on the bed'), 'AftTube': ('flip', 'forward end down'), 'EbayCap': ('up', 'disc down, loop up')}
def oriented2(k, s):
    s = s.copy()
    if ORIENT2[k][0] == 'flip': s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
for k, s in (('FwdTube', fw_px), ('AftTube', P2['AftTube']), ('EbayCap', P2['EbayCap'])):
    o = oriented2(k, s); bb = o.BoundBox
    oh = overhangs(o)
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d need support%s"
        % (ok(not big), k + (" (proxy; the thread is 45 deg)" if k == 'FwdTube' else ""), ORIENT2[k][1], bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
rep("NOTE FwdTube eyelet: the pocket roof bridges %.0f mm and the tie bar is the first layers -- no support." % (2 * EY_POCKET[1]))

# =====================================================================================
# MASS / CG
# =====================================================================================
items = []
solid("Nose cone v6 (screw-on Von Karman)", "nose", nose6, "ABS")
solid("FwdTube v2 (thread, seat, bulkhead, eyelet)", "airframe", P2['FwdTube'], "ABS")
solid("AftTube v2 (chute bay, launch lug)", "airframe", P2['AftTube'], "ABS")
solid("EbayCap", "e-bay", P2['EbayCap'], "ABS")
for k, s in HW2.items(): solid("HW %s" % k, "e-bay", s, "steel")
solid("ElectronicsSled v1", "e-bay", sled2, "ABS")
e_env2 = Part.makeCompound(list(ENV2.values()))
point("Electronics, Opt B 620 mAh, no servo", "e-bay", 48.0 - 9.0, cg_z(e_env2), "avbay packing md 6 (48 g less SG90); CG = envelopes", e_env2)
point("Foam ring 2 mm", "e-bay", 0.3, zs(NOSE_SH_END_ST + 0.5), "estimate")
CANOPY_ST2 = S_BH2 + 45.0
point("Canopy d500 + harness + Kevlar leader", "recovery", CANOPY_G, zs(CANOPY_ST2), "DESIGN 7.7; packed forward in the bay")
point("Nomex blanket / wadding", "recovery", NOMEX_G, zs(NOMEX_ST), "estimate")
for nm, p in PINS.items(): solid("Shear %s" % nm, "aft", p, "ABS")
solid("AftFinCan D9aft v1", "aft", fincan, "ABS")
solid("MotorRetainerCap v1", "aft", cap, "ABS")
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
rep("  Dry, flight-ready            %6.1f g  CG %s   (v1 251.2 g, tip 213.3)" % (dry_m, fmt(dry_z)))
rep("  Liftoff on D9 (27.1 g)       %6.1f g  CG %s   (v1 278.3 g, tip 230.0)" % (lo_m, fmt(lo_z)))
rep("  Landing (spent 11.0 g)       %6.1f g  CG %s" % (la_m, fmt(la_z)))
rep("OPENROCKET: NOSE_G=%.1f NOSE_CG=%.1f NS_BODY_G=%.1f NS_BODY_LEN=%.1f NS_BODY_CGX=%.1f" % (nose_m, station(nose_z) + NOSE_LEN, nn_m, BODY_LEN, station(nn_z)))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT (new parts only; fin can / pins / coupons / cap are the D9aft v1 files)
# =====================================================================================
for k in ('FwdTube', 'AftTube', 'EbayCap'):
    P2[k].exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME2, k)))
    MeshPart.meshFromShape(Shape=P2[k], LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME2, k)))
    MeshPart.meshFromShape(Shape=oriented2(k, P2[k]), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_%s.stl" % (NAME2, k)))
doc = App.newDocument("Phoenix_D9aft_v2")
for nm, g, m, z, b, s in items:
    if s is None: continue
    o = doc.addObject("Part::Feature", "".join(c if c.isalnum() else "_" for c in nm)[:40]); o.Shape = s; o.Label = "%s [%.1f g]" % (nm, m)
o = doc.addObject("Part::Feature", "D9_motor"); o.Shape = motor; o.Label = "Klima D9-5 stand-in [%.1f g loaded]" % MOTOR_LOADED
o = doc.addObject("Part::Feature", "REF_nose_unscrewed"); o.Shape = nose6_px.translated(V(0, 0, 40)); o.Label = "REF nose unscrewed + e-bay lifted (proxy)"
o = doc.addObject("Part::Feature", "REF_ebay_lifted"); o.Shape = Part.makeCompound([P2['EbayCap'], sled2]).translated(V(0, 0, 90)); o.Label = "REF e-bay lifted out 90 mm"
doc.recompute()
doc.saveAs(os.path.join(MODELS, NAME2 + ".FCStd"))
Part.makeCompound([i[5] for i in items if i[5] is not None] + [motor]).exportStep(os.path.join(MODELS, NAME2 + "_assembly.step"))
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(24, 10))
    cols = {"nose": "0.25", "airframe": "tab:blue", "e-bay": "tab:brown", "aft": "tab:gray", "recovery": "tab:green"}
    for ax, mode in zip(axs, ("flight", "access")):
        for nm, g, m, z, b, s in items:
            if s is None or g == "recovery": continue
            if s is fincan: s = fincan_px
            if s is nose6: s = nose6_px
            dz = 0.0
            if mode == "access" and g == "nose": dz = 60.0
            if mode == "access" and g == "e-bay": dz = 30.0
            if mode == "access" and g == "aft": dz = -(CPL_LEN + 60)
            draw(ax, s, cols[g], dz=dz)
        draw(ax, motor, "tab:orange", dz=-(CPL_LEN + 60) if mode == "access" else 0.0)
        ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.set_xlabel("mm from nose tip")
    axs[0].plot(station(lo_z) + NOSE_LEN, 0, "o", ms=10, mfc="none", mec="k"); axs[0].annotate("CG %.0f g" % lo_m, (station(lo_z) + NOSE_LEN, 3))
    axs[0].set_title("Phoenix ABS 40-43 %s -- flight (section y=0.7; threads drawn as proxies)" % REV2)
    axs[1].set_title("nose unscrewed + e-bay lifted (forward); fin can off after ejection (aft)")
    fig.savefig(os.path.join(MODELS, NAME2 + "_section.png"), dpi=100, bbox_inches="tight")
except Exception as ex:
    print("section plot skipped:", ex)
with open(os.path.join(MODELS, NAME2 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t00))

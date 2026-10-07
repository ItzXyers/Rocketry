# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- SNAP-LATCH TEST COUPON v1 (OPTIONAL: an alternative to the printed shear pins).

Why: the D9aft v1 shear pins (0.8 mm thick, 0.6 mm neck) do not print -- they come out as blobs.
A 4-24 N release in ABS needs ~0.5 mm2 of neck, below what FDM can make. A snap latch gets the
same low release force from BENDING a normal-sized printed tongue, so every feature here is
>= 0.6 mm and the part is reusable.

This is a demo coupon ONLY. No flight part changes. Print it, pull-test it, then decide.

Layout (flipped vs the first idea, on purpose):
  * The springy TONGUE is cut into the TUBE wall (outer ring = AftTube wall, d43/d40). It runs
    circumferentially, so its bending stress runs along the printed perimeters, not across layers.
  * A BUMP on the tongue's inner face points INWARD into a WINDOW in the fin-can COUPLER wall
    (inner ring = coupler, d39.6/d37, same 0.2 mm radial slip as flight).
  * Ejection gas inside the coupler reaches the tongue only through the window/slip gap and pushes
    it OUTWARD = out of the catch, and the tongue deflects outward into free air. A tongue in the
    coupler would be pushed INTO its catch by bay pressure and backed by the packed canopy.
  * Release ramp 45 deg (bump forward face vs the window's matched forward face); entry ramp 30 deg.
    45 deg keeps mu*tan(a) well under 0.7 (no self-locking) and prints as a 45 deg overhang either way.
  * Printability: the tongue's forward edge is a 45 deg slant (it is the underside when the tube
    prints forward-end-down, as the flight AftTube does), so the tongue grows from its root with no
    support. The 1.0 mm aft gap is a short bridge under the 4 mm aft band.
  * 4 outer-ring variants by tongue length (20 / 24 / 28 / 32 mm, 1-4 nicks on the aft rim) bracket
    the stiffness; all take the same inner ring (print 3 inner rings).

Frame (flight): z up = toward the nose. Outer ring z = 0 is the tube's AFT face. The inner ring is
built with z = 0 at its aft (floor) face; assembled it sits SH_H lower (shoulder against the tube).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Any FAIL line in the report means do not print.
"""
import os, math, time
import FreeCAD as App
import Part, MeshPart

V = App.Vector
t0 = time.time()
PHX = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43"
MODELS = os.path.join(PHX, "Models")
READY = os.path.join(PHX, "Print Files", "Ready to Print", "D9")
NAME = "PhoenixABS40-43_SnapLatchCoupon_v1"
RHO_ABS = 1.05e-3                                 # g/mm3 -- all parts ABS

# ---------------- flight walls (D9aft v1, unchanged)
R_OD, R_ID = 21.5, 20.0                           # AftTube
CPL_R_O, CPL_R_I = 19.80, 18.50                   # fin-can coupler (0.2 mm radial slip)
CPL_LEN = 40.0                                    # flight coupler engagement

# ---------------- latch
T_TONGUE = 1.2                                    # 3 lines at 0.42 -> slicer-clean; outer skin recessed 0.3
R_TO = R_ID + T_TONGUE                            # tongue outer radius 21.2
R_T = R_ID + T_TONGUE / 2                         # tongue mid radius (beam + helix reference)
W_TIP = 5.0                                       # tongue axial width at the tip
TAPER = 1.0                                       # forward edge slope dz/ds = 1 -> 45 deg, printable unsupported
VARIANTS = (20.0, 24.0, 28.0, 32.0)               # tongue arc length at R_T, root -> tip (1..4 nicks)
BUMP_H = 1.2                                      # radial; 1.0 into the 1.3 coupler wall
BUMP_S = 5.0                                      # tangential width (at R_ID)
TIP_MARGIN = 1.0                                  # bump end -> tongue tip
S_B_OFF = TIP_MARGIN + BUMP_S / 2                 # load point measured back from the tip
A_REL, A_ENT = 45.0, 30.0                         # ramp angles from the axis: release (fwd face), entry (aft face)
BUMP_FLAT = 0.8
GAP_END, GAP_FWD, GAP_AFT = 0.8, 0.9, 1.0         # GAP_FWD is vertical on a 45 deg slant -> 0.64 normal
BAND_AFT = 4.0                                    # tube wall aft of the aft gap (bridges the gap in print)
Z_TAFT = BAND_AFT + GAP_AFT                       # tongue aft edge, 5.0 from the tube aft face
E0 = Z_TAFT + 0.6                                 # bump aft end
L_ENT = BUMP_H / math.tan(math.radians(A_ENT))
L_REL = BUMP_H / math.tan(math.radians(A_REL))
LB = L_ENT + BUMP_FLAT + L_REL                    # bump axial footprint
BUMP_ANG = (0.0, 180.0)
DELTA = BUMP_H - (R_ID - CPL_R_O) + 0.05          # tongue deflection to clear the coupler OD
H_O = 50.0
STRING_Z, STRING_R = H_O - 3.5, 1.5               # string holes across the bore, forward end, 90/270
NICK = 1.0

# ---------------- inner ring (coupler)
SH_H, FLOOR_T, HOOK_R, CPL_CHAMFER = 3.0, 2.0, 2.0, 0.8
CLR_FWD, CLR_AFT, CLR_TAN = 0.15, 0.30, 0.40      # window clearances around the bump

# ---------------- material / test assumptions (ABS, printed)
E_RANGE = (1700.0, 2000.0, 2400.0)                # MPa, printed ABS in-plane (low / nominal / high)
MU_RANGE = (0.20, 0.35, 0.50, 0.60)               # ABS on ABS incl. layer stair-steps on the ramp
STRAIN_MAX = 0.010                                # reusable snap-fit limit for printed ABS (half of the ~2 % moulded value)
HOLD_NEED = 4.2                                   # N, D9aft v1 hold budget (all loads additive)
RELEASE_MAX = 24.0 - 3.0                          # N, v1 release budget minus the 3 N slide-friction allowance
ACCEPT = (8.0, 20.0)                              # N per pair, pull-test acceptance (>= ~2x the hold need)
P_BAY = (40e-3, 55e-3)                            # MPa, v1 note's ejection estimate (assist only, not counted)

report = []
def rep(s): print(s); report.append(s)
def ok(c): return "PASS" if c else "FAIL"

def pol(r, a_deg, z):
    a = math.radians(a_deg); return V(r * math.cos(a), r * math.sin(a), z)
def rev(prof_rz, a0, a1):
    """(r, z) polygon revolved from angle a0 to a1 (deg) about Z."""
    vs = [V(r, 0, z) for r, z in prof_rz]
    s = Part.Face(Part.Wire(Part.makePolygon(vs + [vs[0]]))).revolve(V(0, 0, 0), V(0, 0, 1), a1 - a0)
    s.rotate(V(0, 0, 0), V(0, 0, 1), a0)
    return s
def ring(r0, r1, z0, z1):
    return Part.makeCylinder(r1, z1 - z0, V(0, 0, z0)).cut(Part.makeCylinder(r0, z1 - z0 + 2, V(0, 0, z0 - 1)))
def radial_cyl(r, z, a_deg, r0=15.0, r1=24.0):
    d = pol(1, a_deg, 0); return Part.makeCylinder(r, r1 - r0, pol(r0, a_deg, z), d)
def inside(s, p): return s.isInside(p, 1e-4, True)
deg = math.degrees

# ---------------- helical slant: solid "forward of the tongue's forward edge"
def fwd_of_edge(L, th_tip, dz=0.0, m=4.0):
    """Everything forward (+z) of the helix z = Z_TAFT + W_TIP + (theta - th_tip) * R_T (+dz), r 19..22.5.
    Right-handed: the edge rises toward the ROOT (theta increases from tip to root)."""
    hgt = L + 2 * m
    helix = Part.makeHelix(2 * math.pi * R_T, hgt * TAPER, R_T)
    prof = Part.makePolygon([V(19.0, 0, 0), V(22.6, 0, 0), V(22.6, 0, 80), V(19.0, 0, 80), V(19.0, 0, 0)])
    sol = Part.Wire(helix).makePipeShell([prof], True, True)
    sol.rotate(V(0, 0, 0), V(0, 0, 1), th_tip - deg(m / R_T))
    sol.translate(V(0, 0, Z_TAFT + W_TIP - m * TAPER + dz))
    return sol

def latch_geom(L, th_b):
    th_tip = th_b - deg(S_B_OFF / R_T)
    th_root = th_tip + deg(L / R_T)
    z_top = Z_TAFT + W_TIP + L * TAPER + 6
    tongue = rev([(R_ID, Z_TAFT), (R_TO, Z_TAFT), (R_TO, z_top), (R_ID, z_top)], th_tip, th_root).cut(fwd_of_edge(L, th_tip))
    cut = rev([(R_ID - 0.1, Z_TAFT - GAP_AFT), (R_OD + 0.1, Z_TAFT - GAP_AFT), (R_OD + 0.1, z_top), (R_ID - 0.1, z_top)],
              th_tip - deg(GAP_END / R_T), th_root).cut(fwd_of_edge(L, th_tip, dz=GAP_FWD))
    hb = deg(BUMP_S / 2 / R_ID)
    bump = rev([(R_ID + 0.3, E0), (R_ID, E0), (R_ID - BUMP_H, E0 + L_ENT), (R_ID - BUMP_H, E0 + L_ENT + BUMP_FLAT),
                (R_ID, E0 + LB), (R_ID + 0.3, E0 + LB)], th_b - hb, th_b + hb)
    return dict(tongue=tongue, cut=cut, bump=bump, th_tip=th_tip, th_root=th_root, hb=hb)

def build_outer(L, nicks):
    s = ring(R_ID, R_OD, 0, H_O)
    G = [latch_geom(L, a) for a in BUMP_ANG]
    for g in G: s = s.cut(g['cut'])
    for g in G: s = s.fuse(g['tongue'])
    nb = s.copy()
    for g in G: s = s.fuse(g['bump'])
    for a in (90.0, 270.0):
        s = s.cut(radial_cyl(STRING_R, STRING_Z, a)); nb = nb.cut(radial_cyl(STRING_R, STRING_Z, a))
    for k in range(nicks):                                                  # V nicks on the aft rim at 90 deg
        a = 90.0 + 6.0 * (k - (nicks - 1) / 2)
        n = Part.makeBox(2 * NICK, 2 * NICK, 2 * NICK, V(-NICK, -NICK, -NICK)); n.rotate(V(0, 0, 0), V(0, 0, 1), 45)
        n.translate(pol(R_OD, a, 0))
        s = s.cut(n); nb = nb.cut(n)
    return s.removeSplitter(), nb.removeSplitter(), G

def z_win_fwd(r): return E0 + LB - (R_ID - r) / math.tan(math.radians(A_REL)) + CLR_FWD
Z_WIN_AFT = E0 + (R_ID - CPL_R_O) / math.tan(math.radians(A_ENT)) - CLR_AFT

def build_inner():
    zt = SH_H + CPL_LEN
    s = rev([(0, 0), (R_OD, 0), (R_OD, SH_H), (CPL_R_O, SH_H), (CPL_R_O, zt - CPL_CHAMFER), (CPL_R_O - CPL_CHAMFER, zt),
             (CPL_R_I, zt), (CPL_R_I, FLOOR_T), (0, FLOOR_T)], 0, 360)
    s = s.cut(Part.makeCylinder(HOOK_R, FLOOR_T + 2, V(0, 0, -1)))
    hw = deg(BUMP_S / 2 / R_ID) + deg(CLR_TAN / CPL_R_O)
    for a in BUMP_ANG:
        r0, r1 = CPL_R_I - 0.3, R_ID
        s = s.cut(rev([(r0, Z_WIN_AFT + SH_H), (r1, Z_WIN_AFT + SH_H), (r1, z_win_fwd(r1) + SH_H), (r0, z_win_fwd(r0) + SH_H)], a - hw, a + hw))
        s = s.cut(rev([(R_OD - 0.8, -1), (R_OD + 1, -1), (R_OD + 1, SH_H + 1), (R_OD - 0.8, SH_H + 1)], a - 2.0, a + 2.0))   # window mark: groove in the shoulder OD
    return s.removeSplitter()

# =====================================================================================
# BUILD
# =====================================================================================
P = {}
OUT = {}
for k, L in enumerate(VARIANTS):
    s, nb, G = build_outer(L, k + 1)
    OUT[L] = dict(shape=s, nobump=nb, G=G)
    P['TubeRing_L%d' % L] = s
inner = build_inner()
P['CouplerRing'] = inner
inner_a = inner.translated(V(0, 0, -SH_H))                                # assembled, flight frame of the outer ring

rep("SNAP-LATCH TEST COUPON v1 -- optional alternative to the D9aft v1 shear pins (demo print, no flight part changed)")
rep("tongue in the TUBE wall, bump inward into a COUPLER window; t %.1f mm (R %.1f-%.1f), tip width %.1f, 45 deg slanted forward edge"
    % (T_TONGUE, R_ID, R_TO, W_TIP))
rep("bump %.1f radial x %.1f tangential x %.2f axial; release %.0f deg, entry %.0f deg; release deflection %.2f mm" % (BUMP_H, BUMP_S, LB, A_REL, A_ENT, DELTA))
rep("")

# =====================================================================================
# GEOMETRY CHECKS
# =====================================================================================
rep("GEOMETRY")
for L in VARIANTS:
    o = OUT[L]; s = o['shape']
    rep("%s TubeRing_L%d: %d solid(s), %.1f mm3" % (ok(len(s.Solids) == 1 and s.isValid()), L, len(s.Solids), s.Volume))
    for g in o['G']:
        tt, tr = g['th_tip'], g['th_root']
        thm = (tt + tr) / 2
        s_mid = (tr - thm) * math.radians(1) * R_T                               # arc from the root
        z_edge = Z_TAFT + W_TIP + (thm - tt) * math.radians(1) * R_T
        probes = [("end slot open", pol(R_T, tt - deg(GAP_END / 2 / R_T), Z_TAFT + 2), False),
                  ("aft gap open (mid)", pol(R_T, thm, Z_TAFT - GAP_AFT / 2), False),
                  ("fwd slant gap open (mid)", pol(R_T, thm, z_edge + GAP_FWD / 2), False),
                  ("tongue present (mid)", pol(R_T, thm, (Z_TAFT + z_edge) / 2), True),
                  ("tongue skin recessed 0.3 (mid)", pol((R_TO + R_OD) / 2, thm, (Z_TAFT + z_edge) / 2), False),
                  ("tube wall beyond the tip", pol(R_T, tt - deg((GAP_END + 1.5) / R_T), Z_TAFT + 2), True),
                  ("tube wall forward of the slant gap", pol(R_T, thm, z_edge + GAP_FWD + 1.0), True),
                  ("aft band present", pol(R_T, thm, BAND_AFT / 2), True),
                  ("tongue joined at the root", pol(R_T, tr + 0.5, Z_TAFT + 3), True),
                  ("bump present", pol(R_ID - BUMP_H / 2, (tt + deg(S_B_OFF / R_T)), E0 + L_ENT + BUMP_FLAT / 2), True)]
        bad = [n for n, p, want in probes if inside(s, p) != want]
        rep("%s   latch @%3.0f deg: tip %.1f / root %.1f deg (arc %.1f deg), root width %.1f; probes %d/%d%s"
            % (ok(not bad), (tt + deg(S_B_OFF / R_T)) % 360, tt, tr, tr - tt, W_TIP + L * TAPER, len(probes) - len(bad), len(probes),
               "; WRONG %s" % bad if bad else ""))
    # tongue really is a cantilever: the tube minus the tongue+bump solids still holds the tongue only at the root?
    # -> check that a thin radial probe line along the end slot and the aft gap never hits material
    hits = 0
    for g in o['G']:
        for i in range(25):
            th = g['th_tip'] + (g['th_root'] - 0.3 - g['th_tip']) * i / 24   # stop short of the root face (gap ends there by design)
            if inside(s, pol(R_T, th, Z_TAFT - GAP_AFT / 2)): hits += 1
        for i in range(10):
            if inside(s, pol(R_T, g['th_tip'] - deg(GAP_END / 2 / R_T), Z_TAFT - GAP_AFT + 0.1 + (W_TIP + GAP_AFT - GAP_END / 2 * TAPER + GAP_FWD - 0.3) * i / 9)): hits += 1
    rep("%s   aft gap + end slot open along their whole length (70 probes, %d hit material)" % (ok(hits == 0), hits))

rep("%s CouplerRing: %d solid(s), %.1f mm3; windows at %s deg, aft face %.2f, fwd face %.2f..%.2f (tube frame)"
    % (ok(len(inner.Solids) == 1 and inner.isValid()), len(inner.Solids), inner.Volume, "/".join("%.0f" % a for a in BUMP_ANG),
       Z_WIN_AFT, z_win_fwd(CPL_R_O), z_win_fwd(CPL_R_I)))
wp = [("window open", pol((CPL_R_O + CPL_R_I) / 2, a, (Z_WIN_AFT + z_win_fwd(19.15)) / 2 + SH_H), False) for a in BUMP_ANG] + \
     [("coupler wall beside window", pol((CPL_R_O + CPL_R_I) / 2, a + 15, (Z_WIN_AFT + z_win_fwd(19.15)) / 2 + SH_H), True) for a in BUMP_ANG]
bad = [n for n, p, w in wp if inside(inner, p) != w]
rep("%s   window probes %d/%d%s" % (ok(not bad), len(wp) - len(bad), len(wp), "; WRONG %s" % bad if bad else ""))
rep("%s   coupler front at %.1f vs string holes from %.1f (tube frame): string line clear" % (ok(CPL_LEN < STRING_Z - STRING_R - 1.0), CPL_LEN, STRING_Z - STRING_R))

rep("")
rep("FIT / FUNCTION (each tube variant with the coupler ring)")
for L in VARIANTS:
    o = OUT[L]; s, nb = o['shape'], o['nobump']
    v0 = s.common(inner_a).Volume
    # latch must CATCH: pull the coupler aft past the 0.15 axial play -> the bump hits the window's forward face
    v_lock = s.common(inner_a.translated(V(0, 0, -0.6))).Volume
    v_lock_nb = nb.common(inner_a.translated(V(0, 0, -0.6))).Volume
    # with the tongue deflected DELTA outward (bump moved radially), the coupler slides fully out with no contact
    bumps_def = [g['bump'].translated(pol(DELTA, a, 0)) for g, a in zip(o['G'], BUMP_ANG)]
    defl = nb.fuse(bumps_def)
    worst = 0.0
    for i in range(0, 25):
        d = 0.5 * i
        worst = max(worst, defl.common(inner_a.translated(V(0, 0, -d))).Volume)
    # undeflected bump does block the slide (proves the deflection is what releases it)
    v_rigid = s.common(inner_a.translated(V(0, 0, -(LB + 1.0)))).Volume
    rep("%s L%d: assembled overlap %.4f mm3; pulled aft 0.6 mm -> bump/window overlap %.3f mm3 (tube w/o bumps %.4f) = CATCHES; "
        "tongue deflected %.2f mm -> slide 0..12 mm max overlap %.4f mm3 = RELEASES; undeflected at %.1f mm aft %.2f mm3"
        % (ok(v0 < 1e-3 and v_lock > 0.05 and v_lock_nb < 1e-3 and worst < 1e-3 and v_rigid > 0.05),
           L, v0, v_lock, v_lock_nb, DELTA, worst, LB + 1.0, v_rigid))
rep("NOTE the deflected-bump check moves the bump radially by %.2f mm (top at r %.2f vs coupler OD %.2f); the real tongue tip"
    " also rotates slightly -- the pull test is the real check." % (DELTA, R_ID - BUMP_H + DELTA, CPL_R_O))

# =====================================================================================
# FORCE / STRAIN (curved, tapered cantilever, Castigliano; load at the bump)
# =====================================================================================
def beam(L, E, delta=DELTA, n=800):
    sb = L - S_B_OFF; ds = sb / n; J = 0.0; arr = []
    for i in range(n):
        s_ = (i + 0.5) * ds
        I = (W_TIP + (L - s_) * TAPER) * T_TONGUE ** 3 / 12
        m = R_T * math.sin((sb - s_) / R_T)
        J += m * m / (E * I) * ds; arr.append((m, I))
    Pn = delta / J
    return Pn, max(Pn * m * (T_TONGUE / 2) / (E * I) for m, I in arr)
def fac(a, mu):
    ta = math.tan(math.radians(a)); return (ta + mu) / (1 - mu * ta)
def fac_entry(a, mu): return fac(a, mu)

rep("")
rep("FORCE / STRAIN (beam model; ABS E %s MPa, mu %s) -- a PREDICTION; the pull test sets the real number"
    % ("/".join("%.0f" % e for e in E_RANGE), "/".join("%.2f" % m for m in MU_RANGE)))
lock = max(MU_RANGE) * math.tan(math.radians(A_REL))
rep("%s self-locking margin: mu*tan(%.0f) = %.2f at mu %.2f (keep < 0.7; 1 - mu tan a = %.2f)"
    % (ok(lock < 0.7), A_REL, lock, max(MU_RANGE), 1 - lock))
A_win = BUMP_S * LB
rep("NOTE ejection gas assist (not counted): %.0f-%.0f kPa on the %.0f mm2 bump footprint = %.1f-%.1f N OUTWARD per latch, plus slip-gap leakage under the tongue"
    % (P_BAY[0] * 1e3, P_BAY[1] * 1e3, A_win, P_BAY[0] * A_win, P_BAY[1] * A_win))
rep("%-6s %8s %8s %8s | %-34s | %s" % ("var", "P_nom N", "strain%", "k N/mm", "pair release N: low / nom / high", "insert pair N (nom)"))
for k, L in enumerate(VARIANTS):
    Pn, e = beam(L, E_RANGE[1])
    lo = 2 * beam(L, E_RANGE[0])[0] * fac(A_REL, MU_RANGE[0])
    nom = 2 * Pn * fac(A_REL, MU_RANGE[1])
    hi = 2 * beam(L, E_RANGE[2])[0] * fac(A_REL, MU_RANGE[3])
    ins = 2 * Pn * fac_entry(A_ENT, MU_RANGE[1])
    verdict = "IN BAND" if (lo >= HOLD_NEED and hi <= RELEASE_MAX) else ("WEAK END" if lo < HOLD_NEED else "STRONG END")
    rep("L%-5d %8.2f %8.2f %8.2f | %6.1f / %6.1f / %6.1f  %-12s | %.1f   (%d nick%s)"
        % (L, Pn, e * 100, Pn / DELTA, lo, nom, hi, verdict, ins, k + 1, "s" if k else ""))
    rep("%s   L%d peak strain %.2f %% <= %.1f %% (reusable, printed ABS, along the perimeters)" % (ok(e <= STRAIN_MAX), L, e * 100, STRAIN_MAX * 100))
rep("  band: hold >= %.1f N (D9aft v1 budget) at low E + low mu; release <= %.0f N (24 N budget - 3 N slide friction) at high E + high mu"
    % (HOLD_NEED, RELEASE_MAX))
rep("  PULL-TEST ACCEPTANCE: every pull %.0f-%.0f N per pair (>= ~2x the hold need). Only the pull test proves the force." % ACCEPT)
rep("  model limits: the root is wide vs its length (plate, not beam), the load sits off the tongue's centreline (torsion),")
rep("  printed E and mu vary by printer and filament -> expect +-40 %. That is why there are 3 variants and a pull test.")
rep("NOTE hold budget: the U-slots vent the bay, so the 2.6 N sealed-bay apogee term in the 4.2 N budget mostly goes away.")

# =====================================================================================
# PRINTABILITY
# =====================================================================================
def oriented(s, flip):
    s = s.copy()
    if flip: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return s
def down_patches(s, nz_lim=-0.75):
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
        rs = [math.hypot(p.x, p.y) for p in ps]
        out.append(dict(area=sum(f.Area for f in fs), z=sum(p.z for p in ps) / len(ps),
                        dr=max(rs) - min(rs), arc=sum(f.Area for f in fs) / max(max(rs) - min(rs), 1e-6)))
    return out
ORIENT = dict([('TubeRing_L%d' % L, (True, "forward end down (as the flight AftTube), nicks on top")) for L in VARIANTS] +
              [('CouplerRing', (False, "floor down (as the fin can, aft down)"))])
rep("")
rep("PRINTABILITY (ABS, 0.4 nozzle, 0.20 layers)")
LW, LH = 0.42, 0.20
feats = [("tongue thickness (set wall line width 0.40 -> 3 lines)", T_TONGUE, 2 * LW + 0.2), ("end slot", GAP_END, 0.6), ("aft gap", GAP_AFT, 0.6),
         ("fwd slant gap (normal)", GAP_FWD * math.cos(math.radians(45)), 0.6), ("bump radial", BUMP_H, 0.8),
         ("release ramp height", L_REL, 4 * LH), ("entry ramp height", L_ENT, 4 * LH), ("aft band", BAND_AFT, 2.0),
         ("coupler wall beside window ligament", (CPL_R_O - CPL_R_I), 1.0)]
for n, v, mn in feats:
    rep("%s   %-36s %.2f mm >= %.2f (%.1f lines / %.0f layers)" % (ok(v >= mn - 1e-9), n, v, mn, v / LW, v / LH))
for k, (flip, txt) in ORIENT.items():
    o = oriented(P[k], flip); bb = o.BoundBox
    ph = down_patches(o)
    bridges = [p for p in ph if p['area'] > 2.0]
    bad = [p for p in bridges if p['dr'] > 2.0]                                # a downward face wider than a wall = real overhang
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; downward faces steeper than 41 deg from vertical: %d patch(es) >2 mm2 %s"
        % (ok(not bad), k, txt, bb.XLength, bb.YLength, bb.ZLength, len(bridges),
           "; ".join("z %.1f, %.1f mm2, %.1f wide x %.1f arc" % (p['z'], p['area'], p['dr'], p['arc']) for p in bridges)))
rep("NOTE tube rings: the 2 patches are the aft band bridging the 1.0 mm aft gap (wall-thick, ~L long, along the arc). If one sags")
rep("     and fuses to the tongue, run a knife along the gap -- and tell me: it decides the flight version.")
rep("NOTE the bump release faces (45 deg) and the window forward faces (45 deg) print as 45 deg overhangs -> not flagged; no supports anywhere.")

# =====================================================================================
# MASS, FLIGHT NOTES
# =====================================================================================
rep("")
for k in P: rep("MASS %-22s %5.1f g (solid x ABS 1.05)" % (k, P[k].Volume * RHO_ABS))
rep("")
rep("FLIGHT INTEGRATION NOTES (only if the coupon passes; would be D9aft v7):")
rep("  * The tongue footprint runs %.0f-%.0f mm forward of the tube's aft face; the flight coupler is %.0f mm long -> only L<=%.0f stays fully backed by it."
    % (Z_TAFT - GAP_AFT, Z_TAFT + W_TIP + max(VARIANTS) + GAP_FWD, CPL_LEN, CPL_LEN - Z_TAFT - W_TIP - GAP_FWD))
rep("  * The slots are a small vent bay->outside (today the pin slots are the only holes). Do NOT tape over the tongues.")
rep("  * The flight AftTube already prints forward-end-down, which is the orientation used here.")
rep("  * Tongues must sit clear of the launch lug and the harness lug; the fin can keys to the bumps (one clocking needs uneven angles).")

fails = [l for l in report if l.startswith("FAIL")]
rep("")
rep("RESULT: %s (%d FAIL)  [%.0f s]" % ("ALL PASS" if not fails else "FAILURES", len(fails), time.time() - t0))

# =====================================================================================
# EXPORT
# =====================================================================================
os.makedirs(READY, exist_ok=True)
for k, s in P.items():
    s.exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME, k)))
    MeshPart.meshFromShape(Shape=oriented(s, ORIENT[k][0]), LinearDeflection=0.01, AngularDeflection=0.15, Relative=False) \
        .write(os.path.join(READY, "%s_%s.stl" % (NAME, k)))
doc = App.newDocument("SnapLatchCoupon_v1")
for i, (k, s) in enumerate(P.items()):
    o = doc.addObject("Part::Feature", k); o.Shape = s.translated(V(110 * i, 0, 0)) if k != 'CouplerRing' else s.translated(V(110 * i, 0, 0))
    o.Label = k
for i, L in enumerate(VARIANTS):
    o = doc.addObject("Part::Feature", "ASM_L%d" % L); o.Shape = Part.makeCompound([OUT[L]['shape'], inner_a]).translated(V(110 * i, 120, 0))
    o.Label = "ASSEMBLED L%d (engaged)" % L
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME + ".FCStd"))
with open(os.path.join(MODELS, NAME + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")

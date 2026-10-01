# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v4: SLOTTED FIN CAN + SEPARATE FINS, epoxied (the one-piece fin can did not print).

Changes from v3: only the aft section.
  AftFinCanSlotted  aft_retention_v1 cfg B (AftSectionSealed: 3 through-the-wall slots 2.3 wide that cut the
                    wall AND both centring rings, stopping 0.3 off the motor tube), with the SAME D9aft features
                    as the v1 fin can, applied by v1's make_fincan(): d14 gas port + casing-rim ledge, slip
                    coupler (OD 39.60, 40 mm), 2 pin slots, harness lug. Base = the verified STEP; checks on a
                    thread-free proxy, features proven on the real part by probes.
  Fin (x3)          rev-5 planform (root 50.8, tip 25, span 55, sweep 25.4, t 2.0, 1 mm rounded edges). NEW TAB:
                    ends at r 10.8 (0.4 mm epoxy gap to the motor tube). Fin_v1's tab ran to r 9.8 -- sized to
                    FUSE into cfg C's motor tube -- and would hit both the slot bottom and the tube.
                    Printed FLAT (layers parallel to the faces: the strong way in bending).
  unchanged         nose v6, FwdTube v3, EbayCap v3, AftTube v2, pins/coupons/cap (v1).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame z = 340 - station (= fin-can Zf). Any FAIL line means do not print.
"""
import os, math, time
t0000 = time.time()
V1_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v1.py"
_v1 = open(V1_SRC, encoding="utf-8").read()
_c = _v1.index("\n# CHECKS\n"); _c = _v1.rfind("# ====", 0, _c)
exec(_v1[:_c])                                        # v1: AR (proxy namespace), make_fincan, pins, cap, motor, AftTube, helpers
print("v1 geometry in %.1f s" % (time.time() - t0000), flush=True)
def cg_z(shape):
    shs = shape.Solids if shape.Solids else [shape]
    return sum(s.Volume * s.CenterOfMass.z for s in shs) / sum(s.Volume for s in shs)
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
        out.append(dict(area=a, z=(min(zz) + max(zz)) / 2, span=min(max(xs) - min(xs), max(ys) - min(ys)), ledge=a / (math.pi * (min(rs) + max(rs))),
                        r0=min(rs), r1=max(rs)))
    return out
NAME4, REV4 = "PhoenixABS40-43_D9aft_v4", "D9aft_v4"
report = []
SECTION_STEP = os.path.join(MODELS, "PhoenixABS40-43_AftSectionSealed_v1.step")
FIN_TAB_R_B = AR['FIN_SLOT_R_I'] + 0.1               # 10.8: tab tip 0.1 off the slot bottom, 0.4 off the motor tube
EPOXY_G = 2.0                                         # 4 mm root fillets (thickened epoxy) + slot bond, estimate
V2_BODY_G, V2_BODY_CGX = 202.7, 165.3                 # v2/v3 OpenRocket body override (non-nose dry mass, CG from body top)

# ---------------- slotted section: real (STEP, threaded) + proxy (plain boss), then the D9aft features
sec_v1 = Part.Shape(); sec_v1.read(SECTION_STEP)
sec_v1 = sec_v1.Solids[0] if len(sec_v1.Solids) == 1 else sec_v1
sec_px_v1 = AR['build_sealed_section'](slots=True)    # raw compound, no heal (heal corrupts the plain-boss build)
fcB = make_fincan(sec_v1)
fcB_px = make_fincan(sec_px_v1)
AR['FIN_TAB_R'] = FIN_TAB_R_B
FINS = [AR['build_fin'](a) for a in AR['FIN_ANGLES']]
FIN_FLAT = AR['build_fin'](0.0)
print("slotted fin can + fins in %.1f s" % (time.time() - t0000), flush=True)

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: slotted fin can + 3 separate fins (epoxied); everything else v3 ==" % REV4)
rep("")
for k, s in (('AftFinCanSlotted', fcB), ('AftFinCanSlotted proxy', fcB_px), ('Fin', FIN_FLAT)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))
# same D9aft feature probes as v1 (real + proxy)
probes = [("gas port open on the axis", V(0, 0, (BH_Z0 + BH_Z1) / 2), False),
          ("casing-rim ledge present r 8.7", pol(8.7, 30, BH_Z0 + 0.5), True),
          ("motor bore open below the ledge", pol(8.7, 30, BH_Z0 - 0.3), False),
          ("coupler wall mid-length", pol(19.15, 30, (BH_Z1 + CPL_Z1) / 2), True),
          ("coupler OD trimmed to %.2f" % CPL_R_O, pol(19.83, 30, SHOULDER_Z + 3.0), False),
          ("shoulder full OD below", pol(21.3, 30, SHOULDER_Z - 0.3), True),
          ("harness lug present", pol(13.2, ANCH_FC['ang'], ANCH_FC['z1'] - 0.5), True),
          ("harness lug hole open", pol(ANCH_HOLE_R, ANCH_FC['ang'], ANCH_FC['zh']), False),
          ("thrust-ring annulus solid (seals the fin annulus from the bay)", pol(14.0, 60, (BH_Z0 + BH_Z1) / 2), True)]
probes += [("pin slot %d open" % i, pol(19.15, a, Z_PIN), False) for i, a in enumerate(PIN_ANG)]
zm = (AR['FIN_Z0'] + AR['FIN_Z1']) / 2
for a in AR['FIN_ANGLES']:
    probes += [("fin slot %.0f open through the wall" % a, pol(20.75, a, zm), False),
               ("fin slot %.0f open through centring ring 1" % a, pol(15.0, a, AR['CR_STATIONS'][0] + 1.0), False),
               ("fin slot %.0f stops off the motor tube (ring solid at r 10.55)" % a, pol(10.55, a, AR['CR_STATIONS'][0] + 1.0), True),
               ("wall solid beside slot %.0f" % a, pol(20.75, a + 6.0, zm), True)]
bad = [(n, w) for n, p, w in probes if inside(fcB, p) != w]
badp = [(n, w) for n, p, w in probes if inside(fcB_px, p) != w]
rep("%s REAL slotted fin can: %d/%d probes as designed%s" % (ok(not bad), len(probes) - len(bad), len(probes), "; WRONG %s" % bad if bad else ""))
rep("%s proxy: %d/%d same probes%s" % (ok(not badp), len(probes) - len(badp), len(probes), "; WRONG %s" % badp if badp else ""))
dv, dvp = fcB.Volume - sec_v1.Volume, fcB_px.Volume - sec_px_v1.Volume
rep("%s D9aft feature volume delta real %+.1f vs proxy %+.1f mm3 (same cuts landed on both; |d| < 2)" % (ok(abs(dv - dvp) < 2.0), dv, dvp))

# fins in the slots
fi = [(i, round(f.common(fcB_px).Volume, 3), round(f.common(motor).Volume, 3)) for i, f in enumerate(FINS)]
rep("%s 3 fins drop into the slots: fin x can %s, fin x motor %s mm3 (all 0)" % (ok(all(a < 1e-3 and b < 1e-3 for _, a, b in fi)), [a for _, a, _ in fi], [b for _, _, b in fi]))
rep("%s epoxy gaps: %.2f mm per side in the slot (fin %.1f in a %.1f slot); tab tip %.1f mm off the motor tube, %.1f off the slot bottom"
    % (ok(0.1 <= (AR['FIN_SLOT_W'] - AR['FIN_T']) / 2 <= 0.25), (AR['FIN_SLOT_W'] - AR['FIN_T']) / 2, AR['FIN_T'], AR['FIN_SLOT_W'], FIN_TAB_R_B - AR['MT_R_O'], FIN_TAB_R_B - AR['FIN_SLOT_R_I']))
old_tab = AR['MT_R_O'] - 0.6
AR['FIN_TAB_R'] = old_tab
f_old = AR['build_fin'](0.0)
AR['FIN_TAB_R'] = FIN_TAB_R_B
rep("%s negative control: Fin_v1's tab (to r %.1f) against the slotted can -> %.2f mm3 clash (must be > 0: the check can fail)"
    % (ok(f_old.common(fcB_px).Volume > 1.0), old_tab, f_old.common(fcB_px).Volume))
root_in = [f.common(Part.makeCylinder(R_OD, 200, V(0, 0, -50)).cut(Part.makeCylinder(R_ID, 202, V(0, 0, -51)))).Volume for f in FINS]
rep("%s each fin's tab fills the wall slot (%.0f mm3 of tab inside the wall each; slot is %.0f)"
    % (ok(min(root_in) > 0.8 * AR['FIN_T'] * (R_OD - R_ID) * (AR['FIN_Z1'] - AR['FIN_Z0'])), min(root_in), AR['FIN_SLOT_W'] * (R_OD - R_ID) * (AR['FIN_Z1'] - AR['FIN_Z0'])))
# the rest of the D9aft function, re-proven on the slotted can
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, zs(131.0))
rep("%s d%.0f gas column clear through the thrust ring" % (ok(fcB_px.common(gp).Volume < 1e-3), 2 * PORT_R))
sw = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if fcB_px.translated(V(0, 0, -d)).common(P['AftTube']).Volume > 1e-3]
rep("%s separation sweep 0..%.0f mm vs the aft tube: clear %s" % (ok(not sw), CPL_LEN + 4, sw[:4] or ""))
bad = [(nm, round(p.common(P['AftTube']).Volume + p.common(fcB_px).Volume, 4)) for nm, p in PINS.items() if p.common(P['AftTube']).Volume + p.common(fcB_px).Volume > 1e-3]
rep("%s shear pins sit free in both slots: %s" % (ok(not bad), bad or "yes"))
hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod).Volume) for k, sh in (("fincan", fcB_px),) + tuple(("fin_%d" % i, f) for i, f in enumerate(FINS))) if v > 1e-3] \
    if 'rod' in globals() else None
if hits is None:
    rod = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=LL_C - (LL_RI - ROD_R)), LL_ANG)
    hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod).Volume) for k, sh in (("fincan", fcB_px),) + tuple(("fin_%d" % i, f) for i, f in enumerate(FINS))) if v > 1e-3]
rep("%s launch rod line clear of the slotted can and the 3 fins: %s" % (ok(not hits), hits or "clear"))

# printability
def drop(s):
    s = s.copy(); bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
fin_print = FIN_FLAT.copy(); fin_print.rotate(V(0, 0, 0), V(1, 0, 0), 90.0); fin_print = drop(fin_print)     # thickness (y) -> print Z
for k, s, lab in (('AftFinCanSlotted (proxy)', drop(fcB_px), 'boss down'), ('Fin', fin_print, 'FLAT on a face')):
    bb = s.BoundBox
    oh = overhangs(s)
    # an annulus whose inner edge sits on the motor tube and outer edge on the airframe wall is a BRIDGE anchored
    # both sides (cfg B's centring rings + thrust ring, AFT_RETENTION 4A: 9.6 mm, no support) -- not a ledge
    brg = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0
           and c['r0'] >= AR['MT_R_O'] - 2.2 and c['r1'] <= R_ID + 0.8 and c['r1'] - c['r0'] <= 11.0]
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0 and c not in brg]
    if brg:
        rep("NOTE %s: %d annular bridges motor tube -> wall, widest %.1f mm radial, at print z %s (as v1 cfg B: 4 perimeters, slow first bridge layer)"
            % (k, len(brg), max(c['r1'] - c['r0'] for c in brg), sorted(round(c['z'], 1) for c in brg)))
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d need support%s"
        % (ok(not big), k, lab, bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
rep("NOTE the fin's 1 mm edge round prints as a small overhang on its lower half -- cosmetic at Mach 0.17; sand if wanted.")

# mass: replace the one-piece fin can with section + 3 fins + epoxy
mC, zC = fincan.Volume * RHO['ABS'], cg_z(fincan)
mS, zS = fcB.Volume * RHO['ABS'], cg_z(fcB)
mF = sum(f.Volume for f in FINS) * RHO['ABS']; zF = sum(f.Volume * cg_z(f) for f in FINS) / sum(f.Volume for f in FINS)
zE = zm
mB = mS + mF + EPOXY_G
zB = (mS * zS + mF * zF + EPOXY_G * zE) / mB
rep("")
rep("MASS: one-piece fin can %.1f g @ st %.1f  ->  slotted %.1f g + 3 fins %.1f g + epoxy ~%.1f g = %.1f g @ st %.1f  (%+.1f g)"
    % (mC, station(zC), mS, mF, EPOXY_G, mB, station(zB), mB - mC))
nb_g = V2_BODY_G - mC + mB
nb_cg = (V2_BODY_G * V2_BODY_CGX - mC * station(zC) + mB * station(zB)) / nb_g
rep("OPENROCKET: NOSE_G=14.6 NOSE_CG=43.8 NS_BODY_G=%.1f NS_BODY_LEN=340.0 NS_BODY_CGX=%.1f   (v3 body 202.7 @ 165.3, fin can swapped)" % (nb_g, nb_cg))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
fcB.exportStep(os.path.join(MODELS, NAME4 + "_AftFinCanSlotted.step"))
FIN_FLAT.exportStep(os.path.join(MODELS, NAME4 + "_Fin.step"))
for nm, s in (("AftFinCanSlotted", fcB), ("Fin", FIN_FLAT)):
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME4, nm)))
MeshPart.meshFromShape(Shape=drop(fcB), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME4 + "_AftFinCanSlotted.stl"))
MeshPart.meshFromShape(Shape=fin_print, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME4 + "_Fin.stl"))
doc = App.newDocument("Phoenix_D9aft_v4_aft")
doc.addObject("Part::Feature", "AftFinCanSlotted").Shape = fcB
for i, f in enumerate(FINS): doc.addObject("Part::Feature", "Fin_%d" % i).Shape = f
doc.addObject("Part::Feature", "MotorRetainerCap_v1").Shape = cap
doc.addObject("Part::Feature", "D9_motor").Shape = motor
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME4 + "_aft.FCStd"))
with open(os.path.join(MODELS, NAME4 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t0000))

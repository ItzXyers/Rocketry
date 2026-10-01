# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v5: v4 with the ELECTRONICS SLED v4 (Avionics/PhoenixABS40-43_avbay_sled_v4.py).

Sled v4 = servo gone, BMP388 moved away from the Nano, outboard-open battery tray, seat-foot ring, and a
REED-SWITCH ARMING MODULE (armed by a magnet held on the outside of the tube). Its interfaces are the
ones D9aft reads (Zmin -0.9, spine key, M2 bosses at the old SG90 ears, piezo at Zs 9.5 / 0 deg).

Changes from v4 (v3's e-bay recipe re-run on the new sled; the v1 -> v2 -> v3 exec chain is patched IN MEMORY
only -- no earlier file is edited):
  sled      v1 -> v4 (the EbayCap pocket regenerates from the new sled's top automatically)
  EbayCap   v3 recipe (springs + key) on sled v4
  FwdTube   v3 + an engraved ARM MARK over the reed capsule: a 0.3 mm line at the capsule's angle
            (derived from the sled's RM_* constants, ~-10.9 deg) spanning the capsule's stations, with
            a cross tick at its centre. v3 dropped the 0-deg witness notch the sled report referred to.
            Cut before the thread (plain boolean), far from the thread band.
  unchanged nose v6, AftTube v2, slotted fin can + fins (v4), pins/coupons/cap (v1).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame z = 340 - station. Any FAIL line means do not print.
"""
import os, math, time
t5 = time.time()
V3_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v3.py"
SLED_V4 = "PhoenixABS40-43_avbay_sled_v4.py"
_arm = ("ARM_ANG = math.degrees(math.atan2(SL['RM_YC'], SL['RM_XC']))          # D9aft v5: reed capsule angle\n"
        "ARM_ZC = SL['RM_Z0'] + SL['RM_PCB_W'] / 2.0\n"
        "ARM_ST0, ARM_ST1 = station(ARM_ZC + SL['RM_CAP_L'] / 2 + SLED_Z2), station(ARM_ZC - SL['RM_CAP_L'] / 2 + SLED_Z2)\n"
        "ARM_STC = station(ARM_ZC + SLED_Z2)\n"
        "ARM_D, ARM_W, ARM_TICK = 0.3, 1.0, 3.0\n"
        "fw = fw.cut(rot(box(R_OD - ARM_D, R_OD + 1, -ARM_W / 2, ARM_W / 2, zs(ARM_ST1), zs(ARM_ST0)), ARM_ANG))\n"
        "fw = fw.cut(rot(box(R_OD - ARM_D, R_OD + 1, -ARM_TICK, ARM_TICK, zs(ARM_STC) - ARM_W / 2, zs(ARM_STC) + ARM_W / 2), ARM_ANG))\n")
_sledfix = 'exec(_v1[:_c].replace(\'"PhoenixABS40-43_avbay_sled_v1.py"\', \'"%s"\'))' % SLED_V4
_v3 = open(V3_SRC, encoding="utf-8").read()
_c3 = _v3.index("\n# CHECKS\n"); _c3 = _v3.rfind("# ====", 0, _c3)
_g3 = _v3[:_c3]
_line = "_g = _g.replace(_notch, _groove)"
assert _g3.count(_line) == 1
_g3 = _g3.replace(_line, "_g = _g.replace(_notch, _groove + _arm); assert _g.count('exec(_v1[:_c])') == 1; _g = _g.replace('exec(_v1[:_c])', _sledfix)")
exec(_g3)
assert SL['SLED_RMAX'] and 'ReedModule' in [n for n, _ in SL['COMPONENTS']], "sled v4 not loaded"
print("chain v1 -> v2 -> v3 on sled v4 in %.1f s" % (time.time() - t5), flush=True)

NAME5, REV5 = "PhoenixABS40-43_D9aft_v5", "D9aft_v5"
report = []
V4_BODY_G, V4_BODY_CGX = 203.7, 166.0                 # v4 OpenRocket body override
OLD_EBAY_G, OLD_EBAY_ST = 54.1 - 0.12 - 0.3, 38.3     # v2 e-bay group (report), v3: cap -0.12 g, foam removed
REED_G = SL['RM_MASS']
def nose_at(phi, extra_dz=0.0):
    s = nose6.copy(); s.rotate(V(0, 0, 0), V(0, 0, 1), phi); s.translate(V(0, 0, PITCH * phi / 360.0 + extra_dz)); return s

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: v4 + electronics sled v4 (reed arming), EbayCap regenerated, ARM mark ==" % REV5)
rep("")
for k, s in (('FwdTube v5', P3['FwdTube']), ('FwdTube v5 proxy', fw_px3), ('EbayCap v5', P3['EbayCap']), ('sled v4', sled2)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))
rep("NOTE sled v4 loaded: components %s" % [n for n, _ in SL['COMPONENTS']])

# --- FwdTube: arm mark + groove + thread on the REAL part
zmid = zs((ARM_ST0 + ARM_ST1) / 2)
ap = [("ARM line open at the OD", pol(R_OD - 0.12, ARM_ANG, zmid), False),
      ("ARM line floor solid (0.3 deep)", pol(R_OD - ARM_D - 0.1, ARM_ANG, zmid), True),
      ("OD solid beside the line (away from the tick)", pol(R_OD - 0.12, ARM_ANG + 5.0, zs(ARM_ST0 + 2.0)), True),
      ("ARM centre tick open", pol(R_OD - 0.12, ARM_ANG + 6.0, zs(ARM_STC)), False),
      ("line ends: OD solid past the capsule", pol(R_OD - 0.12, ARM_ANG, zs(ARM_ST1 + 2.0)), True),
      ("key groove open (v3)", pol(20.3, KEY_ANG, zs(14.0)), False),
      ("female thread ridge present (v2)", V(CREST + 0.15, 0, T_ANCHOR_A + 4 * PITCH + PITCH / 2), True),
      ("female thread channel open (v2)", V(CREST + 0.15, 0, T_ANCHOR_A + 4 * PITCH), False)]
bad = [(n, w) for n, p, w in ap if inside(P3['FwdTube'], p) != w]
rep("%s REAL FwdTube: ARM mark + groove + thread probes %d/%d as designed%s" % (ok(not bad), len(ap) - len(bad), len(ap), "; WRONG %s" % bad if bad else ""))
cap_r_out = SL['RM_CAP_RC'] + SL['RM_CAP_D'] / 2
rep("%s ARM mark at %.1f deg, stations %.1f..%.1f (tick at %.1f) = the reed capsule's angle and length; magnet on the mark is %.2f mm from the glass"
    % (ok(abs(ARM_ST1 - ARM_ST0 - SL['RM_CAP_L']) < 1e-6 and R_OD - cap_r_out <= 3.0), ARM_ANG, ARM_ST0, ARM_ST1, ARM_STC, R_OD - cap_r_out))
sp_ang = [(n, a) for n, a in (("static port", STATIC_PORT['ang']), ("sound port", SOUND_PORT['ang']), ("key groove", KEY_ANG))]
rep("%s ARM mark clear of the ports and groove: %.1f deg from the static port (%.1f mm of arc at the OD), stations clear of the thread band (%.1f > %.1f)"
    % (ok(abs(ARM_ANG) * math.pi / 180 * R_OD - ARM_TICK > STATIC_PORT['d'] / 2 and ARM_ST0 > BAND_END), abs(ARM_ANG), abs(ARM_ANG) * math.pi / 180 * R_OD, ARM_ST0, BAND_END))
rep("NOTE thread not re-sampled: v5 only removes 0.3 mm of the OD at stations %.0f..%.0f, 7.5 mm aft of the thread band; the v3 probes above confirm it is intact." % (ARM_ST0, ARM_ST1))

# --- e-bay: sled v4 in the v3 cap + tube
bad = interference(dict(ebaycap=P3['EbayCap'], sled=sled2, fwd=fw_px3, **HW2, **{'env_' + k: v for k, v in ENV2.items()}),
                   {('sled', 'env_SmallParts'), ('ebaycap', 'fwd')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)})
rep("%s e-bay interference (EbayCap v5, sled v4, %d envelopes, M2 screws, tube): %s" % (ok(not bad), len(ENV2), bad or "none"))
seat = sled2.common(fw_px3).Volume
drop_ = sled2.translated(V(0, 0, -0.5)).common(fw_px3).Volume
rep("%s sled v4 seat foot stands on the seat ring: contact %.4f mm3; NEGATIVE CONTROL dropped 0.5 mm -> %.1f mm3 (must be > 0)" % (ok(seat < 1e-2 and drop_ > 10), seat, drop_))
sw = [d for d in [0.5 * k for k in range(0, 2 * int(S_DISC_TOP + (DISC_ZS1 - DISC_ZS0) + 4) + 1)]
      if Part.makeCompound([P3['EbayCap'], sled2]).translated(V(0, 0, d)).common(fw_px3).Volume > 1e-3]
rep("%s e-bay (cap + sled v4) lifts out of the mouth through the thread crests, key in the groove: %s" % (ok(not sw), sw[:4] or "no contact"))
rr = max(sled2_r for sled2_r in [SL['SLED_RMAX']] + [max(math.hypot(v.X, v.Y) for v in e.Vertexes) for e in ENV2.values()])
rep("%s largest e-bay radius %.2f vs crest %.2f -> %.2f mm radial" % (ok(CREST - rr >= 0.25), rr, CREST, CREST - rr))
blk = []
for da in (-2.0, 2.0):
    c = P3['EbayCap'].copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), da); blk.append(round(c.common(fw_px3).Volume, 2))
rep("%s key blocks rotation (+-2 deg hits the groove wall: %s mm3)" % (ok(all(b > 0.01 for b in blk)), blk))
ov = nose6_px.common(P3['EbayCap']).Volume
bump_ov = sum(nose6_px.common(b).Volume for b in BUMPS)
rep("%s nose touches the EbayCap only at the 3 spring bumps (%.2f = %.2f mm3)" % (ok(abs(ov - bump_ov) < 0.05 and bump_ov > 0.1), ov, bump_ov))
tr = sum(b.translated(V(0, 0, -SPR_POCKET)).common(sled2).Volume for b in BEAMS)
rep("%s spring beams bottomed stay clear of the sled v4 top (%.4f mm3)" % (ok(tr < 1e-3), tr))
key_top = sled2.common(box(-30, 30, -30, 30, zd0 + 0.01, zd1 + 5)).Volume
rep("%s sled v4 spine key rises into the cap pocket (%.1f mm3 above the cap underside, pocket regenerated from it)" % (ok(key_top > 1.0), key_top))
probe = radial_cyl(STATIC_PORT['d'] / 2, R_ID - 3.0, R_ID - 0.01, STATIC_PORT['zs'] + SLED_Z2, STATIC_PORT['ang'])
hit = [k for k, s in dict(sled=sled2, **ENV2).items() if s.common(probe).Volume > 1e-3]
rep("%s static port d%.1f at station %.1f: 3 mm behind it clear%s" % (ok(not hit), STATIC_PORT['d'], station(STATIC_PORT['zs'] + SLED_Z2), (": BLOCKED by %s" % hit) if hit else ""))
# sound port: the piezo is MEANT to sit behind it -- the path port -> piezo face must be clear, and the piezo must be what it meets
pf = SL['PIEZO_X0'] + SL['PIEZO_DR']                                                      # piezo outboard face radius
zsp = SOUND_PORT['zs'] + SLED_Z2
path = radial_cyl(SOUND_PORT['d'] / 2, pf + 0.02, R_ID - 0.01, zsp, SOUND_PORT['ang'])
hit = [k for k, s in dict(sled=sled2, **ENV2).items() if s.common(path).Volume > 1e-3]
meets = [k for k, s in ENV2.items() if s.common(radial_cyl(SOUND_PORT['d'] / 2, pf - 1.0, pf + 0.02, zsp, SOUND_PORT['ang'])).Volume > 1e-3]
rep("%s sound port d%.1f at station %.1f: clear %.1f mm air path to the piezo face (r %.1f)%s; the first thing behind it is %s"
    % (ok(not hit and meets == ['Piezo']), SOUND_PORT['d'], station(zsp), R_ID - pf, pf, (", BLOCKED by %s" % hit) if hit else "", meets))
pz = ENV2['Piezo'].BoundBox
rep("%s piezo sound hole in line with the port: piezo Zs centre %.1f vs port %.1f" % (ok(abs((pz.ZMin + pz.ZMax) / 2 - (SOUND_PORT['zs'] + SLED_Z2)) < 1.0), (pz.ZMin + pz.ZMax) / 2 - SLED_Z2, SOUND_PORT['zs']))

# --- printability
def drop(s):
    s = s.copy(); bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
sled_print = drop(sled2)                              # aft end (seat foot) down
for k, s, lab, hard in (('EbayCap v5', drop(P3['EbayCap']), 'disc down', True), ('sled v4', sled_print, 'aft end (seat foot) down', False)):
    bb = s.BoundBox
    oh = overhangs(s)
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
    tag = ok(not big) if hard else "NOTE"
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2); %d wide ones%s"
        % (tag, k, lab, bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s (print z, span, mm2) -> support these or bridge them" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))

# --- mass / OpenRocket
items = []
solid("EbayCap v5", "e-bay", P3['EbayCap'], "ABS")
for k, s in HW2.items(): solid("HW %s" % k, "e-bay", s, "steel")
solid("ElectronicsSled v4", "e-bay", sled2, "ABS")
env_parts = Part.makeCompound([v for k, v in ENV2.items() if k not in ('ZipTie',)])
point("Electronics, Opt B 620 mAh (no servo) + reed module", "e-bay", 48.0 - 9.0 + REED_G, cg_z(env_parts), "packing md 6 less SG90, + RM_MASS; CG = envelopes (tie excluded)", env_parts)
mE, zE = tot(items)
nb_g = V4_BODY_G - OLD_EBAY_G + mE
nb_cg = (V4_BODY_G * V4_BODY_CGX - OLD_EBAY_G * OLD_EBAY_ST + mE * station(zE)) / nb_g
rep("")
rep("MASS: e-bay group %.1f g @ st %.1f (v3 %.1f g @ st %.1f): sled v4 %.1f g, electronics + reed %.1f g, EbayCap %.1f g"
    % (mE, station(zE), OLD_EBAY_G, OLD_EBAY_ST, sled2.Volume * RHO['ABS'], 48.0 - 9.0 + REED_G, P3['EbayCap'].Volume * RHO['ABS']))
rep("OPENROCKET: NOSE_G=14.6 NOSE_CG=43.8 NS_BODY_G=%.1f NS_BODY_LEN=340.0 NS_BODY_CGX=%.1f   (v4 body %.1f @ %.1f, e-bay swapped)" % (nb_g, nb_cg, V4_BODY_G, V4_BODY_CGX))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
for k in ('FwdTube', 'EbayCap'):
    P3[k].exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME5, k)))
    MeshPart.meshFromShape(Shape=P3[k], LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME5, k)))
    MeshPart.meshFromShape(Shape=drop(P3[k]), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_%s.stl" % (NAME5, k)))
MeshPart.meshFromShape(Shape=sled_print, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME5 + "_ElectronicsSled_v4.stl"))
doc = App.newDocument("Phoenix_D9aft_v5_ebay")
for k, s in (('FwdTube_v5', P3['FwdTube']), ('EbayCap_v5', P3['EbayCap']), ('ElectronicsSled_v4', sled2), ('Nose_v6', nose6)):
    doc.addObject("Part::Feature", k).Shape = s
for k, s in ENV2.items(): doc.addObject("Part::Feature", "env_" + k).Shape = s
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME5 + "_ebay.FCStd"))
with open(os.path.join(MODELS, NAME5 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t5))

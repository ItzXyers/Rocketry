# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- D9aft v6: ELECTRONICS SLED v6 (21.9 mm longer e-bay) + a 150 mm CHUTE BAY.

User, 2026-10-06: "I need the parachute bay to be 150 mm"; "the fwd section is what needs to be resized
to fit; line up the piezo and air vent holes"; "AFT bay is reserved for parachute ONLY".

Changes from v5 (the v1 -> v2 -> v3 -> v5 exec chain is patched IN MEMORY only -- no earlier file is edited):
  sled      v4 -> v6 (Avionics/PhoenixABS40-43_avbay_sled_v6.py): the e-bay grows 21.9 mm AFT (aft deck with
            the rotated piezo + small parts), seat plane Z -0.9 -> -22.8.  Everything above Z 0 is v5.
  FwdTube   grows 21.9 mm: the seat ring, the bonded joint and the gas-tight bulkhead all move aft with the
            e-bay (v2's recipe derives them from the sled's lowest point).  SOUND PORT moves onto the rotated
            piezo can (sled PIEZO_ZC, 0 deg); static port unchanged (Z 30, 0 deg); ARM mark follows the reed
            module (RM_*: -8.7 deg).  Thread, key groove, eyelet: v5.
  AftTube   CHUTE BAY ONLY: 150.0 mm clean d40 bore from the bulkhead to the fin-can thrust ring.  Its wall
            has the 2 pin slots and nothing else; the launch lug is outside.  No e-bay part reaches it.
  body      BODY_LEN 340 -> 313.5 so the bay is exactly 150 (v5: 198.4).  Everything referenced to the fin
            can (pins, launch lug, Nomex) is re-anchored to the aft end, so the fin can, pins, coupons and cap
            are the v1 / v4 parts, unchanged.
  EbayCap   v5 recipe (springs + key); pocket regenerated from sled v6's top (unchanged from v5).

Run headless:
  "C:\\Users\\dick_\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecadcmd.exe" -c "exec(open(r'<this file>').read())"
Frame z = BODY_LEN - station (z = 0 is the fin-can aft face, as v1).  Any FAIL line means do not print.
"""
import os, math, time
t6 = time.time()
V5_SRC = r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Models\PhoenixABS40-43_D9aft_v5.py"
SLED_V6 = "PhoenixABS40-43_avbay_sled_v6.py"
BAY_LEN = 150.0
# bay = station(BH_Z1) - S_BH2;  S_BH2 = S_DISC_TOP 10.5 + DISC_ZS1 50.3 - sled SEAT_Z (-22.8) + seat 2 + 3 + spigot 16 = 104.6
BODY_LEN6 = 104.6 + BAY_LEN + 58.9                    # 313.5 -- asserted against the built geometry below

V1_PATCHES = [
    ('"PhoenixABS40-43_avbay_sled_v1.py"', '"%s"' % SLED_V6),
    ("BODY_LEN = 340.0", "BODY_LEN = %.1f" % BODY_LEN6),
    ("SLED_Z = 230.7", "SLED_Z = BODY_LEN - 109.3"),                                  # v1 sled mount: disc top at station 59, as v1 (v2 re-places the e-bay relative to it)
    ("PIN_ST = 276.6", "PIN_ST = BODY_LEN - 63.4"),                                   # Zf 63.4, as v1
    ("LL_ST0, LL_ST1 = 152.5, 187.5", "LL_ST0, LL_ST1 = BODY_LEN - 187.5, BODY_LEN - 152.5"),   # same z as v1..v5
    ("NOMEX_G, NOMEX_ST = 4.0, 245.0", "NOMEX_G, NOMEX_ST = 4.0, BODY_LEN - 95.0"),   # by the port, as v1
    ("SOUND_PORT = dict(d=SOUND_PORT_D, zs=SL['PIEZO_DZ'] / 2, ang=0.0)",
     "SOUND_PORT = dict(d=SOUND_PORT_D, zs=SL['PIEZO_ZC'], ang=0.0)"),               # sled v6: rotated piezo, can centre
]
def _v6_v1(src):
    for a, b in V1_PATCHES:
        assert src.count(a) == 1, "v1 patch target not unique: %r" % a
        src = src.replace(a, b)
    return src

_v5 = open(V5_SRC, encoding="utf-8").read()
_c5 = _v5.index("\n# CHECKS\n"); _c5 = _v5.rfind("# ====", 0, _c5)
_g5 = _v5[:_c5]
_i = _g5.index("_sledfix = ")
_j = _g5.index("\n", _i)
assert _g5.count("_sledfix = ") == 1
_g5 = _g5[:_i] + "_sledfix = 'exec(_v6_v1(_v1[:_c]))'" + _g5[_j:]
exec(_g5)
assert 'PIEZO_ZC' in SL and SL['SEAT_Z'] < -20, "sled v6 not loaded"
assert abs(BODY_LEN - BODY_LEN6) < 1e-9
print("chain v1 -> v2 -> v3 -> v5 on sled v6, body %.1f, in %.1f s" % (BODY_LEN, time.time() - t6), flush=True)

NAME6, REV6 = "PhoenixABS40-43_D9aft_v6", "D9aft_v6"
report = []
ELEC_G = 48.0 - 9.0 - 2.0 + SL['RM_MASS']             # packing md 6: 48 g Opt B, less SG90 (9) and the BQ25302 charger (2, deleted in sled v6), + reed
FINCAN_V4 = dict(m=52.1, z=340.0 - 310.7)             # v4 report: slotted 34.1 + 3 fins 16.0 + epoxy 2.0 @ st 310.7 (v4 frame) -> Zf, unchanged part
BAY0, BAY1 = S_BH2, station(BH_Z1)
air_e = dict(ebaycap=P3['EbayCap'], sled=sled2, **HW2, **{'env_' + k: v for k, v in ENV2.items()})   # everything that is e-bay

# =====================================================================================
# CHECKS
# =====================================================================================
rep("== Phoenix ABS 40-43 -- %s: sled v6 (e-bay +%.1f mm, FwdTube resized), 150 mm chute bay, ports on the new sled ==" % (REV6, SL['DECK_DZ']))
rep("Frame z = %.1f - station (station 0 = nose base). Threaded parts: v5 probes; fits on thread-free proxies." % BODY_LEN)
rep("")
rep("STATION TABLE")
for s0, s1, what in ((-65, 0, "nose v6 (unchanged), screws in"),
                     (0, NOSE_SH_END_ST, "thread (v2)"),
                     (S_DISC_TOP, S_DISC_TOP + (DISC_ZS1 - DISC_ZS0), "EbayCap v5 recipe: springs + key"),
                     (station(sled2.BoundBox.ZMax), S_SEAT, "E-BAY: sled v6 + electronics (aft deck: piezo, small parts), on the seat ring"),
                     (S_SEAT, J2, "seat ring -> spigot.  BONDED joint at %.1f" % J2),
                     (S_BH2 - BH_T2, S_BH2, "gas-tight bulkhead + recessed eyelet (v2)"),
                     (BAY0, BAY1, "CHUTE BAY %.1f mm -- parachute, harness, Nomex ONLY; clean d40 bore" % (BAY1 - BAY0)),
                     (LL_ST0, LL_ST1, "launch lug (outside the tube), rod line r %.2f" % LL_C),
                     (station(CPL_Z1), ST_BODY_AFT, "fin-can coupler, slip fit, 2 shear pins at station %.1f" % PIN_ST),
                     (ST_BODY_AFT, BODY_LEN, "fin can v4 + D9 + cap v1 (unchanged)")):
    rep("  %7.1f - %7.1f  %s" % (s0, s1, what))
rep("")
for k, s in (('FwdTube v6', P3['FwdTube']), ('FwdTube v6 proxy', fw_px3), ('AftTube v6', P3['AftTube']), ('EbayCap v6', P3['EbayCap']), ('sled v6', sled2)):
    rep("%s %s valid, %d solid(s)" % (ok(s.isValid() and len(s.Solids) == 1), k, len(s.Solids)))
rep("NOTE sled v6 loaded: seat Z %.1f (e-bay +%.1f mm), components %s" % (SL['SEAT_Z'], SL['DECK_DZ'], [n for n, _ in SL['COMPONENTS']]))

# --- the bay
rep("%s CHUTE BAY %.2f mm (target %.1f): bulkhead aft face st %.2f -> fin-can thrust ring st %.2f" % (ok(abs(BAY1 - BAY0 - BAY_LEN) < 0.05), BAY1 - BAY0, BAY_LEN, BAY0, BAY1))
e_last = max(station(s.BoundBox.ZMin) for s in air_e.values())
rep("%s e-bay entirely in the FWD section: its aft-most point st %.2f is forward of the joint (%.1f) and the bulkhead (%.1f..%.1f)"
    % (ok(e_last < J2 and e_last < S_BH2 - BH_T2), e_last, J2, S_BH2 - BH_T2, S_BH2))
bay_vol = cyl(R_ID + 0.01, zs(station(CPL_Z1)) + 0.01, z_b - 0.01)            # bay volume ahead of the coupler front
intr = [(k, round(v, 3)) for k, v in ((k, s.common(bay_vol).Volume) for k, s in dict(fwd=fw_px3, nose=nose6_px, **air_e).items()) if v > 1e-3]
rep("%s chute bay holds nothing but recovery gear: no FwdTube / bulkhead / e-bay part inside it %s" % (ok(not intr), intr or ""))
band = P3['AftTube'].common(rst([(R_ID + 0.01, J2 + 1.0), (R_OD - 0.06, J2 + 1.0), (R_OD - 0.06, ST_BODY_AFT - 1.0), (R_ID + 0.01, ST_BODY_AFT - 1.0)]))
ideal = math.pi * ((R_OD - 0.06) ** 2 - (R_ID + 0.01) ** 2) * (ST_BODY_AFT - 1.0 - J2 - 1.0)
rep("%s AftTube wall, whole length: missing %.2f mm3 vs %.2f of pin slots -> no port, vent or other hole" % (ok(abs((ideal - band.Volume) - slot_v) < 0.3), ideal - band.Volume, slot_v))
bore = P3['AftTube'].common(cyl(R_ID - 0.01, zs(ST_BODY_AFT), zs(J2))).Volume
rep("%s canopy exit path: nothing of the AftTube inside the d40 bore (%.4f mm3)" % (ok(bore < 1e-3), bore))

# --- ports + ARM mark lined up on sled v6 (all in the FWD section)
ports = [("static", STATIC_PORT), ("sound", SOUND_PORT)]
for nm, p in ports:
    st_p = station(p['zs'] + SLED_Z2)
    rep("%s %s port d%.1f at station %.1f, %.0f deg: in the FwdTube full wall (st 0..%.1f), forward of the joint by %.1f mm"
        % (ok(st_p + p['d'] / 2 < J2 - 1.0), nm, p['d'], st_p, p['ang'], J2, J2 - st_p - p['d'] / 2))
for nm, d, zsl, ang in SL['D9_PORTS']:
    p = dict(ports)[nm]
    rep("%s %s port = the sled v6 report's proposal (d%.1f Z %.1f %.0f deg): d%.1f Z %.1f %.0f deg" % (ok(abs(p['d'] - d) < 1e-6 and abs(p['zs'] - zsl) < 1e-6 and abs(p['ang'] - ang) < 1e-6), nm, d, zsl, ang, p['d'], p['zs'], p['ang']))
pr = [("sound port open", pol(R_ID + 0.75, SOUND_PORT['ang'], SOUND_PORT['zs'] + SLED_Z2), False),
      ("static port open", pol(R_ID + 0.75, STATIC_PORT['ang'], STATIC_PORT['zs'] + SLED_Z2), False),
      ("wall solid 3 mm aft of the sound port", pol(R_ID + 0.75, SOUND_PORT['ang'], SOUND_PORT['zs'] + SLED_Z2 - 3.0), True),
      ("old v5 sound port position (st 51.3) is solid wall", pol(R_ID + 0.75, 0.0, zs(51.3)), True)]
bad = [(n, w) for n, p, w in pr if inside(P3['FwdTube'], p) != w]
rep("%s REAL FwdTube port probes %d/%d as designed%s" % (ok(not bad), len(pr) - len(bad), len(pr), "; WRONG %s" % bad if bad else ""))
pz = ENV2['Piezo'].BoundBox
zsp = SOUND_PORT['zs'] + SLED_Z2
pf = pz.XMax                                                                     # can faces +x (0 deg) onto the port
path = radial_cyl(SOUND_PORT['d'] / 2, pf + 0.02, R_ID - 0.01, zsp, SOUND_PORT['ang'])
hit = [k for k, s in dict(sled=sled2, **ENV2).items() if s.common(path).Volume > 1e-3]
meets = [k for k, s in ENV2.items() if s.common(radial_cyl(SOUND_PORT['d'] / 2, pf - 1.0, pf + 0.02, zsp, SOUND_PORT['ang'])).Volume > 1e-3]
can_r = SL['PIEZO_CAN_D'] / 2
off = math.hypot((pz.YMin + pz.YMax) / 2, (pz.ZMin + pz.ZMax) / 2 - zsp)
rep("%s sound port -> piezo can: clear %.1f mm air path to the can face (x %.1f)%s; first thing behind it %s; port axis %.2f mm off the can centre (can r %.2f, port r %.1f)"
    % (ok(not hit and meets == ['Piezo'] and off + SOUND_PORT['d'] / 2 <= can_r), R_ID - pf, pf, (", BLOCKED by %s" % hit) if hit else "", meets, off, can_r, SOUND_PORT['d'] / 2))
probe = radial_cyl(STATIC_PORT['d'] / 2, R_ID - 3.0, R_ID - 0.01, STATIC_PORT['zs'] + SLED_Z2, STATIC_PORT['ang'])
hit = [k for k, s in dict(sled=sled2, **ENV2).items() if s.common(probe).Volume > 1e-3]
rep("%s static port d%.1f at station %.1f: 3 mm behind it clear%s" % (ok(not hit), STATIC_PORT['d'], station(STATIC_PORT['zs'] + SLED_Z2), (": BLOCKED by %s" % hit) if hit else ""))
cap_r_out = SL['RM_CAP_RC'] + SL['RM_CAP_D'] / 2
zmid = zs((ARM_ST0 + ARM_ST1) / 2)
ap = [("ARM line open at the OD", pol(R_OD - 0.12, ARM_ANG, zmid), False),
      ("ARM line floor solid (0.3 deep)", pol(R_OD - ARM_D - 0.1, ARM_ANG, zmid), True),
      ("ARM centre tick open", pol(R_OD - 0.12, ARM_ANG + 6.0, zs(ARM_STC)), False),
      ("v5 ARM line position (-10.9 deg) is plain OD", pol(R_OD - 0.12, -10.9 - 1.6, zs(ARM_ST0 + 2.0)), True),
      ("key groove open (v3)", pol(20.3, KEY_ANG, zs(14.0)), False),
      ("female thread ridge present (v2)", V(CREST + 0.15, 0, T_ANCHOR_A + 4 * PITCH + PITCH / 2), True),
      ("female thread channel open (v2)", V(CREST + 0.15, 0, T_ANCHOR_A + 4 * PITCH), False)]
bad = [(n, w) for n, p, w in ap if inside(P3['FwdTube'], p) != w]
rep("%s REAL FwdTube: ARM mark + groove + thread probes %d/%d as designed%s" % (ok(not bad), len(ap) - len(bad), len(ap), "; WRONG %s" % bad if bad else ""))
arm_cut = rot(box(R_OD - ARM_D, R_OD + 1, -ARM_W / 2, ARM_W / 2, zs(ARM_ST1), zs(ARM_ST0)), ARM_ANG).fuse(
          rot(box(R_OD - ARM_D, R_OD + 1, -ARM_TICK, ARM_TICK, zs(ARM_STC) - ARM_W / 2, zs(ARM_STC) + ARM_W / 2), ARM_ANG))
gap_sp = arm_cut.distToShape(radial_cyl(STATIC_PORT['d'] / 2, R_ID - 1, R_OD + 1, STATIC_PORT['zs'] + SLED_Z2, STATIC_PORT['ang']))[0]   # v5's rule was angular only
rep("%s ARM mark at %.1f deg, stations %.1f..%.1f (tick %.1f) = the reed capsule's angle and length; magnet on the mark is %.2f mm from the glass; %.2f mm (3D) from the static port"
    % (ok(abs(ARM_ST1 - ARM_ST0 - SL['RM_CAP_L']) < 1e-6 and R_OD - cap_r_out <= 3.0 and gap_sp >= 1.0),
       ARM_ANG, ARM_ST0, ARM_ST1, ARM_STC, R_OD - cap_r_out, gap_sp))

# --- e-bay fit (v5 set, on sled v6)
bad = interference(dict(fwd=fw_px3, **air_e), {('sled', 'env_SmallParts'), ('ebaycap', 'fwd')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)})
rep("%s e-bay interference (EbayCap, sled v6, %d envelopes, M2 screws, tube): %s" % (ok(not bad), len(ENV2), bad or "none"))
seat = sled2.common(fw_px3).Volume
drop_ = sled2.translated(V(0, 0, -0.5)).common(fw_px3).Volume
rep("%s sled v6 floor stands on the seat ring at st %.1f: contact %.4f mm3; NEGATIVE CONTROL dropped 0.5 mm -> %.1f mm3 (must be > 0)" % (ok(seat < 1e-2 and drop_ > 10), S_SEAT, seat, drop_))
rr = max([SL['SLED_RMAX']] + [max(math.hypot(v.X, v.Y) for v in e.Vertexes) for e in ENV2.values()])
rep("%s e-bay lifts out through the thread crests: largest radius %.2f vs crest %.2f -> %.2f mm radial" % (ok(CREST - rr >= 0.25), rr, CREST, CREST - rr))
sw = [d for d in [0.5 * k for k in range(0, 2 * int(S_SEAT + 2) + 1)] if Part.makeCompound([P3['EbayCap'], sled2]).translated(V(0, 0, d)).common(fw_px3).Volume > 1e-3]
rep("%s full lift-out sweep 0..%.0f mm (key in the groove): %s" % (ok(not sw), S_SEAT + 2, sw[:4] or "no contact"))
blk = []
for da in (-2.0, 2.0):
    c = P3['EbayCap'].copy(); c.rotate(V(0, 0, 0), V(0, 0, 1), da); blk.append(round(c.common(fw_px3).Volume, 2))
rep("%s key blocks rotation (+-2 deg: %s mm3)" % (ok(all(b > 0.01 for b in blk)), blk))
ov = nose6_px.common(P3['EbayCap']).Volume
bump_ov = sum(nose6_px.common(b).Volume for b in BUMPS)
rep("%s nose touches the EbayCap only at the 3 spring bumps (%.2f = %.2f mm3)" % (ok(abs(ov - bump_ov) < 0.05 and bump_ov > 0.1), ov, bump_ov))
tr = sum(b.translated(V(0, 0, -SPR_POCKET)).common(sled2).Volume for b in BEAMS)
rep("%s spring beams bottomed stay clear of the sled top (%.4f mm3)" % (ok(tr < 1e-3), tr))

# --- flight interference, gas path, separation, launch rod, pins (v1/v2 set on the new layout)
air6 = dict(nose=nose6_px, fwd=fw_px3, aft=P3['AftTube'], fincan=fincan_px, motor=motor, **PINS, **air_e)
bad = interference(air6, {('nose', 'fwd'), ('nose', 'ebaycap'), ('sled', 'env_SmallParts'), ('ebaycap', 'fwd')} | {('M2x10_pan_%d' % i, 'sled') for i in range(2)})
rep("%s interference, flight (fin can = v1 proxy: same coupler/pin features as v4; nose/EbayCap = the spring preload, checked above): %s" % (ok(not bad), bad or "none"))
gp = cyl(PORT_R - 0.05, BH_Z0 - 0.1, z_b - 0.5)
hits = [k for k, s in dict(fincan=fincan_px, aft=P3['AftTube'], fwd=fw_px3).items() if s.common(gp).Volume > 1e-3]
rep("%s d%.0f gas column clear from the motor face to the bulkhead: %s" % (ok(not hits), 2 * PORT_R, hits or "clear"))
plate = fw_px3.common(cyl(SPIGOT_RI - 0.05, z_b + 0.01, zs(S_BH2 - BH_T2) - 0.01).cut(box(-EY_POCKET[0], EY_POCKET[0], -EY_POCKET[1], EY_POCKET[1], z_b - 1, z_b + 20)))
plate_v = math.pi * (SPIGOT_RI - 0.05) ** 2 * (BH_T2 - 0.02) - (2 * EY_POCKET[0]) * (2 * EY_POCKET[1]) * (BH_T2 - 0.02)
roof = fw_px3.common(box(-EY_POCKET[0], EY_POCKET[0], -EY_POCKET[1], EY_POCKET[1], z_b + EY_POCKET[2] + 0.01, z_b + EY_BOSS[2] - 0.01))
roof_v = (2 * EY_POCKET[0]) * (2 * EY_POCKET[1]) * (EY_BOSS[2] - EY_POCKET[2] - 0.02)
rep("%s bulkhead gas-tight: plate %.1f of %.1f mm3, eyelet pocket roof %.1f of %.1f mm3" % (ok(abs(plate.Volume - plate_v) < 0.5 and abs(roof.Volume - roof_v) < 0.5), plate.Volume, plate_v, roof.Volume, roof_v))
sw = [d for d in [0.5 * k for k in range(int((CPL_LEN + 4) / 0.5) + 1)] if fincan_px.translated(V(0, 0, -d)).common(P3['AftTube']).Volume > 1e-3]
rep("%s separation sweep 0..%.0f mm: fin can never touches the AftTube %s" % (ok(not sw), CPL_LEN + 4, sw[:4] or ""))
rod_c = LL_C - (LL_RI - ROD_R)
rod_in = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=rod_c), LL_ANG)
rod_mid = rot(cyl(ROD_R, cap.BoundBox.ZMin - 40, zs(LL_ST0) + 150, x=LL_C), LL_ANG)
hits = [(k, round(v, 3)) for k, v in ((k, sh.common(rod_in).Volume) for k, sh in dict(cap_ribs_any_clocking=cap_env, fincan=fincan_px, fwd=fw_px3, nose=nose6_px).items()) if v > 1e-3]
rep("%s launch rod d%.1f pushed %.2f toward the axis: clear of cap ribs, fins, FwdTube, nose: %s" % (ok(not hits), 2 * ROD_R, LL_RI - ROD_R, hits or "clear"))
ll_probe = [inside(P3['AftTube'], pol(LL_C + LL_RO - 0.3, LL_ANG, zs((LL_ST0 + LL_ST1) / 2))), not inside(P3['AftTube'], pol(LL_C, LL_ANG, zs((LL_ST0 + LL_ST1) / 2)))]
rep("%s launch lug %.1f..%.1f (z as v1..v5, %.1f mm from the aft end): present, bore open, rod centred clear of the tube (%.4f mm3)"
    % (ok(all(ll_probe) and rod_mid.common(P3['AftTube']).Volume < 1e-3), LL_ST0, LL_ST1, BODY_LEN - LL_ST1, rod_mid.common(P3['AftTube']).Volume))
pp = [("pin slot %d open in the AftTube" % i, pol(R_ID + 0.75, a, Z_PIN), False) for i, a in enumerate(PIN_ANG)] + \
     [("AftTube wall beside pin slot %d" % i, pol(R_ID + 0.75, a + 12, Z_PIN), True) for i, a in enumerate(PIN_ANG)]
bad = [(n, w) for n, p, w in pp if inside(P3['AftTube'], p) != w]
e_t = ST_BODY_AFT - PIN_ST - (PIN_A + SLOT_CLR) / 2
e_c = CPL_Z1 - Z_PIN - (PIN_A + SLOT_CLR) / 2
rep("%s pin slots at st %.1f = Zf %.1f (fin can v4 slots Zf 63.4), %.1f mm from the AftTube aft edge; probes %d/%d; ligaments tube %.1f / coupler %.1f mm (v1 11.5 / 27.5)%s"
    % (ok(not bad and abs(Z_PIN - 63.4) < 1e-6 and abs(e_t - 11.5) < 0.05), PIN_ST, Z_PIN, ST_BODY_AFT - PIN_ST, len(pp) - len(bad), len(pp), e_t, e_c, "; WRONG %s" % bad if bad else ""))
for nm, p in PINS.items():
    v1_ = p.common(P3['AftTube']).Volume + p.common(fincan_px).Volume
    rep("%s %s sits in both slots with clearance (overlap %.3f mm3)" % (ok(v1_ < 1e-3), nm, v1_))
V_bay1 = 150.1 + (CPL_Z1 - BH_Z1)
V_bay6 = BAY1 - BAY0 + (CPL_Z1 - BH_Z1)
rep("NOTE pins unchanged (v1: 2 x %.1f N). Bay %.1f mm = v1's 150: the same charge gives ~%.2fx the v1 pressure (v2..v5: 0.80x)." % (F_pin, BAY1 - BAY0, V_bay1 / V_bay6))
rep("NOTE Kevlar leader: the bulkhead eyelet -> aft opening is %.0f mm (v5 %.0f); tie it long enough to reach out of the tube." % (ST_BODY_AFT - S_BH2, 288.6 - 82.7))

# --- printability
rep("%s tube split: FwdTube %.1f mm, AftTube %.1f mm tall (bed %.0f)" % (ok(S_BH2 <= BED[2] and ST_BODY_AFT - J2 <= BED[2]), S_BH2, ST_BODY_AFT - J2, BED[2]))
ORIENT6 = {'FwdTube': (fw_px3, False, 'bulkhead (eyelet bar) down'), 'AftTube': (P3['AftTube'], True, 'forward end down'), 'EbayCap': (P3['EbayCap'], False, 'disc down')}
def oriented6(s, flip):
    s = s.copy()
    if flip: s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    bb = s.BoundBox; s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin)); return s
for k, (s, flip, lab) in ORIENT6.items():
    o = oriented6(s, flip); bb = o.BoundBox
    oh = overhangs(o)
    big = [c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0]
    rep("%s %s printed %s: %.1f x %.1f x %.1f mm; %d overhang patches (%.1f mm2), %d wide%s"
        % (ok(not big), k + (" (proxy)" if k == 'FwdTube' else ""), lab, bb.XLength, bb.YLength, bb.ZLength, len(oh), sum(c['area'] for c in oh), len(big),
           ": %s" % [(round(c['z'], 1), round(c['span'], 1), round(c['area'], 1)) for c in big] if big else ""))
sled_print = oriented6(sled2, False)
oh = overhangs(sled_print)
rep("NOTE sled v6 printed floor down: %.1f mm tall; %d overhang patches (%.1f mm2), %d wide (the sled report has not checked print orientation)"
    % (sled_print.BoundBox.ZLength, len(oh), sum(c['area'] for c in oh), len([c for c in oh if c['span'] > 10.0 and c['area'] > 5.0 and c['ledge'] > 2.0])))

# =====================================================================================
# MASS / CG (full rollup on the v6 layout)
# =====================================================================================
items = []
solid("Nose cone v6 (screw-on Von Karman)", "nose", nose6, "ABS")
solid("FwdTube v6 (thread, seat, bulkhead, eyelet, ports, ARM)", "airframe", P3['FwdTube'], "ABS")
solid("AftTube v6 (chute bay, launch lug, pin slots)", "airframe", P3['AftTube'], "ABS")
solid("EbayCap v6", "e-bay", P3['EbayCap'], "ABS")
for k, s in HW2.items(): solid("HW %s" % k, "e-bay", s, "steel")
solid("ElectronicsSled v6", "e-bay", sled2, "ABS")
env_parts = Part.makeCompound([v for k, v in ENV2.items() if k not in ('ZipTie',)])
point("Electronics Opt B 620 mAh, no servo, no charger, + reed", "e-bay", ELEC_G, cg_z(env_parts), "packing md 6 - SG90 - BQ25302 + RM_MASS; CG = envelopes", env_parts)
point("Canopy d500 + harness + Kevlar leader", "recovery", CANOPY_G, zs(S_BH2 + 45.0), "DESIGN 7.7; packed forward in the bay")
point("Nomex blanket / wadding", "recovery", NOMEX_G, zs(NOMEX_ST), "estimate, by the port")
for nm, p in PINS.items(): solid("Shear %s" % nm, "aft", p, "ABS")
point("AftFinCanSlotted v4 + 3 fins + epoxy", "aft", FINCAN_V4['m'], FINCAN_V4['z'], "D9aft v4 report (part unchanged)")
solid("MotorRetainerCap v1", "aft", cap, "ABS")
rep("")
rep("MASS & CG (printed parts solid x rho: an upper bound)")
rep("%-52s %-9s %7s  %-24s %s" % ("ITEM", "GROUP", "g", "CG", "BASIS"))
for nm, g, m, z, b, _ in items:
    rep("%-52s %-9s %7.1f  %-24s %s" % (nm, g, m, fmt(z), b))
rep("%-52s %-9s %7.1f  %-24s %s" % ("Klima D9-5 (loaded; %.1f g spent)" % MOTOR_SPENT, "motor", MOTOR_LOADED, fmt(Z_MOTOR), "OpenRocket motor DB"))
for g in ("nose", "airframe", "e-bay", "recovery", "aft"):
    m, z = tot([i for i in items if i[1] == g]); rep("  %-9s %6.1f g  CG %s" % (g, m, fmt(z)))
dry_m, dry_z = tot(items)
nn_m, nn_z = tot([i for i in items if i[1] != "nose"])
nose_m, nose_z = tot([i for i in items if i[1] == "nose"])
lo_m, lo_z = tot(items + [("", "", MOTOR_LOADED, Z_MOTOR, "", None)])
rep("  Dry, flight-ready            %6.1f g  CG %s" % (dry_m, fmt(dry_z)))
rep("  Liftoff on D9 (27.1 g)       %6.1f g  CG %s   (v5 OpenRocket 246.4 g, tip 235.9)" % (lo_m, fmt(lo_z)))
rep("OPENROCKET: NOSE_G=%.1f NOSE_CG=%.1f NS_BODY_G=%.1f NS_BODY_LEN=%.1f NS_BODY_CGX=%.1f" % (nose_m, station(nose_z) + NOSE_LEN, nn_m, BODY_LEN, station(nn_z)))
fails = [l for l in report if l.startswith("FAIL")]
rep("RESULT: %s (%d FAIL)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))

# =====================================================================================
# EXPORT
# =====================================================================================
for k in ('FwdTube', 'AftTube', 'EbayCap'):
    P3[k].exportStep(os.path.join(MODELS, "%s_%s.step" % (NAME6, k)))
    MeshPart.meshFromShape(Shape=P3[k], LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_RAW, "%s_%s.stl" % (NAME6, k)))
    MeshPart.meshFromShape(Shape=oriented6(P3[k], ORIENT6[k][1]), LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, "%s_%s.stl" % (NAME6, k)))
MeshPart.meshFromShape(Shape=sled_print, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False).write(os.path.join(PRINT_READY, NAME6 + "_ElectronicsSled_v6.stl"))
doc = App.newDocument("Phoenix_D9aft_v6")
for nm, g, m, z, b, s in items:
    if s is None: continue
    o = doc.addObject("Part::Feature", "".join(c if c.isalnum() else "_" for c in nm)[:40]); o.Shape = s; o.Label = "%s [%.1f g]" % (nm, m)
for k, s in ENV2.items(): doc.addObject("Part::Feature", "env_" + k).Shape = s
doc.addObject("Part::Feature", "AftFinCan_v1_proxy").Shape = fincan_px
doc.addObject("Part::Feature", "D9_motor").Shape = motor
doc.recompute(); doc.saveAs(os.path.join(MODELS, NAME6 + ".FCStd"))
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(24, 5))
    cols = {"nose": "0.25", "airframe": "tab:blue", "e-bay": "tab:brown", "aft": "tab:gray"}
    for nm, g, m, z, b, s in items:
        if s is None or g == "recovery": continue
        draw(ax, nose6_px if s is nose6 else (fw_px3 if s is P3['FwdTube'] else s), cols.get(g, "k"))
    for s in ENV2.values(): draw(ax, s, "tab:brown")
    draw(ax, fincan_px, "tab:gray"); draw(ax, motor, "tab:orange")
    for st_ in (BAY0, BAY1): ax.axvline(st_ + NOSE_LEN, color="tab:green", lw=0.8, ls="--")
    ax.annotate("CHUTE BAY %.1f mm (parachute only)" % (BAY1 - BAY0), ((BAY0 + BAY1) / 2 + NOSE_LEN, 0), ha="center", color="tab:green")
    ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.set_xlabel("mm from nose tip")
    ax.set_title("Phoenix ABS 40-43 %s -- section y=0.7 (threads as proxies)" % REV6)
    fig.savefig(os.path.join(MODELS, NAME6 + "_section.png"), dpi=100, bbox_inches="tight")
except Exception as ex:
    print("section plot skipped:", ex)
with open(os.path.join(MODELS, NAME6 + "_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("done in %.1f s" % (time.time() - t6))

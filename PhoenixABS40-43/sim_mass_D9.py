"""Phoenix ABS 40-43, Klima D9 -- flight simulation at a chosen vehicle mass, without an OpenRocket install.

Method: a 1-D vertical point-mass RK4 integrator calibrated on OpenRocket 24.12's own stored output.
From the D9-5 / 1.5 m rod simulation saved inside PhoenixABS40-43_D9aft_v11.ork it takes:
  * the Klima D9 thrust curve and motor mass vs time (OpenRocket's motor database, as flown),
  * the drag coefficient vs speed in the coast phase (Barrowman, the D9aft airframe),
  * the descent CdA under the d500 canopy (from OpenRocket's 5.03 m/s ground hit at 248.2 g).
It first re-flies that v11 case and prints the error against OpenRocket, then flies each MASS case.
The v13 airframe is 30 mm longer than v11 (extension ring); the extra skin-friction drag is added as
a body-length correction on Cd (see CD_LEN_PER_M), which is small (~ +1.5 %).

Stability is NOT simulated (1-D).  It is estimated from OpenRocket's v11 CP (290.9 mm from the tip)
shifted for the +30 mm body with Barrowman's fin/nose normal-force split, and from the v13 CAD mass
rollup CG.  Treat it as an estimate until OrStab.java / VerifyD9v2.java is re-run on the patched .ork.

Usage:  python3 sim_mass_D9.py [--liftoff] [mass_g ...]
        mass = dry mass (everything except the motor; default 230), or with --liftoff the liftoff mass
        incl. the loaded D9 (dry = liftoff - D9 launch mass).
        env PLOT=out.png to also plot the first mass case vs the as-built v13 mass.
"""
import math
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REF_ORK = os.path.join(HERE, "PhoenixABS40-43_D9aft_v11.ork")
D = 0.043                                  # airframe OD, m (reference diameter)
A_REF = math.pi * (D / 2) ** 2
G0 = 9.80665
V11_DRY_G = 237.2                          # OpenRocket v11: liftoff 264.3 - D9 27.1
V11_LEN_M = 0.065 + 0.3135
V13_LEN_M = 0.065 + 0.3435
V13_DRY_G = 246.9                          # v13 CAD rollup (Models/PhoenixABS40-43_D9aft_v13_report.txt)
# Skin friction is ~55 % of a sport model's subsonic Cd and scales with wetted body length; the
# fins/nose/base share does not.  So dCd/Cd ~= 0.55 * (body wetted fraction ~0.7) * dL/L.
CD_LEN_PER_M = 0.55 * 0.7 / V11_LEN_M


def load_or_sim(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read(z.namelist()[0]).decode()
    sim = [s for s in re.findall(r"<simulation[^>]*>.*?</simulation>", xml, re.S)
           if "D9-5" in re.search(r"<name>(.*?)</name>", s).group(1)][-1]
    cols = re.search(r'<databranch[^>]*types="([^"]*)"', sim).group(1).split(",")
    rows = [[float(v) for v in d.split(",")] for d in re.findall(r"<datapoint>(.*?)</datapoint>", sim)]
    col = {c: [r[cols.index(c)] for r in rows] for c in cols}
    ev = {e[1]: float(e[0]) for e in re.findall(r'<event time="([\d.]+)" type="(\w+)"', sim)}
    rod = float(re.search(r"<launchrodlength>([\d.]+)</launchrodlength>", sim).group(1))
    return col, ev, rod


def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    f = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + f * (ys[hi] - ys[lo])


def isa_rho(h):
    T = 288.15 - 0.0065 * h
    return 1.225 * (T / 288.15) ** 4.2559


col, EV, REF_ROD = load_or_sim(REF_ORK)
t_or, T_or, m_or = col["Time"], col["Thrust"], col["Mass"]
t_bo = EV["burnout"]
# thrust curve (zero after burnout) and motor propellant mass vs time
THR_T = [t for t in t_or if t <= t_bo + 0.05]
THR_F = [T_or[i] for i, t in enumerate(t_or) if t <= t_bo + 0.05]
m_end = min(m for t, m in zip(t_or, m_or) if t <= t_bo + 0.5)
PROP_T, PROP_M = THR_T, [m_or[i] - m_end for i in range(len(THR_T))]
MOTOR_BURNOUT_KG = 0.0110                  # Klima D9 burnout casing (OpenRocket)
MOTOR_LAUNCH_KG = MOTOR_BURNOUT_KG + PROP_M[0]
# coast-phase Cd(v): burnout -> 0.3 s before apogee (avoids the AoA artefact at v ~ 0)
cd_pts = sorted((col["Total velocity"][i], col["Drag coefficient"][i]) for i, t in enumerate(t_or)
                if t_bo + 0.05 < t < EV["apogee"] - 0.3)
CD_V, CD_C = [p[0] for p in cd_pts], [p[1] for p in cd_pts]
# descent: OpenRocket ground hit 5.03 m/s at the v11 burnout mass
v_gh_or = abs(col["Vertical velocity"][-1])
m_desc_or = m_or[-1]
CDA_CHUTE = 2 * m_desc_or * G0 / (1.225 * v_gh_or ** 2)


def fly(dry_kg, delay, rod, length_m=V11_LEN_M, dt=0.002):
    cd_scale = 1 + CD_LEN_PER_M * (length_m - V11_LEN_M)
    t, h, v = 0.0, 0.0, 0.0
    out = {"t": [], "h": [], "v": []}
    vmax, v_rod, on_pad, t_ej, h_ej, v_ej = 0.0, None, True, None, None, None
    apo_h, apo_t, chute = 0.0, 0.0, False

    def mass(t):
        return dry_kg + MOTOR_BURNOUT_KG + interp(t, PROP_T, PROP_M)

    def acc(t, h, v):
        m = mass(t)
        F = interp(t, THR_T, THR_F) if t <= THR_T[-1] else 0.0
        rho = isa_rho(max(h, 0.0))
        if chute:
            drag = 0.5 * rho * v * abs(v) * CDA_CHUTE
        else:
            cd = interp(abs(v), CD_V, CD_C) * cd_scale
            drag = 0.5 * rho * v * abs(v) * cd * A_REF
        return (F - drag) / m - G0

    while True:
        if on_pad:
            F = interp(t, THR_T, THR_F) if t <= THR_T[-1] else 0.0
            if F <= mass(t) * G0:
                t += dt
                out["t"].append(t); out["h"].append(0.0); out["v"].append(0.0)
                if t > 2:
                    raise RuntimeError("never lifts off")
                continue
            on_pad = False
        k1v = acc(t, h, v); k1h = v
        k2v = acc(t + dt / 2, h + k1h * dt / 2, v + k1v * dt / 2); k2h = v + k1v * dt / 2
        k3v = acc(t + dt / 2, h + k2h * dt / 2, v + k2v * dt / 2); k3h = v + k2v * dt / 2
        k4v = acc(t + dt, h + k3h * dt, v + k3v * dt); k4h = v + k3v * dt
        v += dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        h += dt / 6 * (k1h + 2 * k2h + 2 * k3h + k4h)
        t += dt
        vmax = max(vmax, v)
        if v_rod is None and h >= rod:
            v_rod = v
        if h > apo_h:
            apo_h, apo_t = h, t
        if not chute and t >= t_bo + delay:
            chute, t_ej, h_ej, v_ej = True, t, h, abs(v)
        out["t"].append(t); out["h"].append(h); out["v"].append(v)
        if h < 0 and t > 1:
            break
    # optimum delay: apogee time - burnout
    return dict(apogee=apo_h, t_apo=apo_t, vmax=vmax, v_rod=v_rod, t_ej=t_ej, h_ej=h_ej, v_ej=v_ej,
                v_ground=abs(v), t_flight=t, opt_delay=apo_t - t_bo, liftoff_g=mass(0) * 1000, trace=out)


# ---- stability estimate (v13 frame, mm from the nose tip) ----
NOSE_L, BODY_L = 65.0, 343.5
FIN_S, FIN_CR, FIN_CT, FIN_SWEEP, NFIN, R = 55.0, 50.8, 25.0, 25.4, 3, D * 1000 / 2
_lm = math.hypot(FIN_S, FIN_SWEEP + (FIN_CT - FIN_CR) / 2)
CN_FIN = (1 + R / (FIN_S + R)) * 4 * NFIN * (FIN_S / (2 * R)) ** 2 / (1 + math.sqrt(1 + (2 * _lm / (FIN_CR + FIN_CT)) ** 2))
CP_V11 = 290.9                                           # OpenRocket 24.12, Mach 0.1 (verify_D9aft_v11)
CP_V13 = CP_V11 + 30.0 * CN_FIN / (2 + CN_FIN)           # fins move 30 mm aft, nose term does not
V13_DRY_CG = 232.7                                       # v13 rollup, mm from the new tip
MOTOR_CG = 387.6                                         # D9 in the mount, v13 frame


def stability(dry_g, dry_cg):
    cgl = (dry_g * dry_cg + MOTOR_LAUNCH_KG * 1e3 * MOTOR_CG) / (dry_g + MOTOR_LAUNCH_KG * 1e3)
    cgb = (dry_g * dry_cg + MOTOR_BURNOUT_KG * 1e3 * MOTOR_CG) / (dry_g + MOTOR_BURNOUT_KG * 1e3)
    return cgl, cgb, (CP_V13 - cgl) / (D * 1000), (CP_V13 - cgb) / (D * 1000)


def main():
    args = sys.argv[1:]
    liftoff = "--liftoff" in args
    vals = [float(x) for x in args if x != "--liftoff"] or [230.0]
    dry_list = [round(g - MOTOR_LAUNCH_KG * 1e3, 1) if liftoff else g for g in vals]
    print("== Phoenix ABS 40-43 D9aft -- Klima D9 mass-case simulation (1-D RK4, calibrated on OpenRocket 24.12) ==")
    print(f"motor: Klima D9 launch {MOTOR_LAUNCH_KG*1e3:.1f} g burnout {MOTOR_BURNOUT_KG*1e3:.1f} g, burn {t_bo:.2f} s "
          f"(OpenRocket thrust curve, {len(THR_T)} pts); Cd coast {min(CD_C):.3f}..{max(CD_C):.3f}; chute CdA {CDA_CHUTE:.4f} m2")
    r = fly(V11_DRY_G / 1e3, 5.0, REF_ROD)
    apo_or = max(col["Altitude"]); vmax_or = max(col["Total velocity"])
    print(f"CALIBRATION v11 D9-5 1.5 m rod  OpenRocket: apogee {apo_or:.1f} m @ {EV['apogee']:.2f} s, vmax {vmax_or:.1f}, "
          f"ground hit {v_gh_or:.2f}, flight {t_or[-1]:.1f} s")
    print(f"                               this sim:   apogee {r['apogee']:.1f} m @ {r['t_apo']:.2f} s, vmax {r['vmax']:.1f}, "
          f"ground hit {r['v_ground']:.2f}, flight {r['t_flight']:.1f} s   "
          f"(apogee error {100*(r['apogee']/apo_or-1):+.1f} %)")
    print(f"v13 Cd length correction x{1 + CD_LEN_PER_M*(V13_LEN_M-V11_LEN_M):.3f};  CP v13 est. {CP_V13:.1f} mm "
          f"(v11 OR {CP_V11} + 30 mm x CNfin {CN_FIN:.2f}/(2+CNfin))")
    print()
    cases = [(V13_DRY_G, "v13 as built (reference)")] + [(g, f"{v:g} g LIFTOFF incl. D9" if liftoff else f"{g:g} g dry")
                                                    for g, v in zip(dry_list, vals)]
    results = {}
    for dry_g, label in cases:
        print(f"--- {label}: dry {dry_g:.1f} g, liftoff {dry_g + MOTOR_LAUNCH_KG*1e3:.1f} g on a D9, v13 airframe {V13_LEN_M*1e3:.1f} mm ---")
        for dly in (3, 5, 7):
            for rod in (1.0, 1.5, 2.0):
                r = fly(dry_g / 1e3, dly, rod, V13_LEN_M)
                results[(dry_g, dly, rod)] = r
                print(f"SIM D9-{dly} rod {rod:.1f} m | apogee {r['apogee']:6.1f} m @ {r['t_apo']:.2f} s | vmax {r['vmax']:.1f} m/s"
                      f" | rod exit {r['v_rod']:.1f} m/s | eject t={r['t_ej']:.2f} alt {r['h_ej']:6.1f} m v {r['v_ej']:4.1f} m/s"
                      f" | optimum delay {r['opt_delay']:.2f} s | ground hit {r['v_ground']:.2f} m/s | flight {r['t_flight']:.1f} s")
        cgl, cgb, sl, sb = stability(dry_g, V13_DRY_CG)
        print(f"STAB (mass removed/added uniformly, dry CG {V13_DRY_CG} kept): CG liftoff {cgl:.1f} burnout {cgb:.1f} mm "
              f"| margin liftoff {sl:.2f} burnout {sb:.2f} cal")
        dm = dry_g - V13_DRY_G
        if abs(dm) > 0.05:
            for where, st in (("e-bay (st ~140 from tip)", 140.0), ("fin can (st ~379)", 379.0)):
                cg = (V13_DRY_G * V13_DRY_CG + dm * st) / dry_g
                cgl, cgb, sl, sb = stability(dry_g, cg)
                print(f"STAB if the {dm:+.1f} g is all at the {where}: dry CG {cg:.1f} | margin liftoff {sl:.2f} burnout {sb:.2f} cal")
        print()

    plot = os.environ.get("PLOT")
    if plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
        fig, (ax_h, ax_v) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
        fig.suptitle(f"PhoenixABS40-43 D9aft v13 — Klima D9-5, 1.5 m rod, no wind\n"
                     f"{dry_list[0]:g} g dry vs as-built {V13_DRY_G} g (1-D sim calibrated on OpenRocket 24.12)",
                     fontsize=11, color=INK)
        for dry_g, colr, ls in ((dry_list[0], BLUE, "-"), (V13_DRY_G, MUTED, "--")):
            r = results[(dry_g, 5, 1.5)]
            tr = r["trace"]
            ax_h.plot(tr["t"], tr["h"], color=colr, ls=ls, lw=2, label=f"{dry_g:g} g dry — apogee {r['apogee']:.0f} m")
            ax_v.plot(tr["t"], tr["v"], color=colr, ls=ls, lw=2, label=f"{dry_g:g} g dry — vmax {r['vmax']:.1f} m/s")
        r = results[(dry_list[0], 5, 1.5)]
        for ax in (ax_h, ax_v):
            ax.grid(color="#e4e3df", lw=0.6)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for tt, lab in ((t_bo, "burnout"), (r["t_apo"], "apogee"), (r["t_ej"], "ejection")):
                ax.axvline(tt, color=MUTED, lw=0.8, ls=":")
            ax.legend(frameon=False, loc="upper right")
        ax_v.axhline(0, color=MUTED, lw=0.8)
        ax_h.set_ylabel("Altitude (m)")
        ax_v.set_ylabel("Vertical velocity (m/s)")
        ax_v.set_xlabel("Time (s)")
        ax_v.set_xlim(0, r["t_flight"])
        fig.tight_layout()
        fig.savefig(plot, dpi=150)
        print(f"PLOT {plot}")


if __name__ == "__main__":
    main()

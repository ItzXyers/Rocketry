"""Plot altitude and velocity vs. time for the D9-5 flight simulation stored in
the PhoenixABS40-43 D9aft .ork file (OpenRocket keeps the flight data inside
the file, so no OpenRocket install is needed).

Usage:  python3 plot_d9_sim.py [file.ork] [out.png]
"""
import re
import sys
import zipfile

import matplotlib.pyplot as plt

ORK = sys.argv[1] if len(sys.argv) > 1 else "PhoenixABS40-43_D9aft_v11.ork"
OUT = sys.argv[2] if len(sys.argv) > 2 else "PhoenixABS40-43_D9aft_v11_D9-5_sim.png"
SIM_MATCH = "D9-5"

with zipfile.ZipFile(ORK) as z:
    xml = z.read(z.namelist()[0]).decode()

sim = [s for s in re.findall(r"<simulation[^>]*>.*?</simulation>", xml, re.S)
           if SIM_MATCH in re.search(r"<name>(.*?)</name>", s).group(1)][-1]  # newest match
name = re.search(r"<name>(.*?)</name>", sim).group(1)
branch = re.search(r'<databranch[^>]*types="([^"]*)"', sim)
cols = branch.group(1).split(",")
rows = [[float(v) for v in d.split(",")]
        for d in re.findall(r"<datapoint>(.*?)</datapoint>", sim)]
col = {c: [r[cols.index(c)] for r in rows] for c in
       ("Time", "Altitude", "Vertical velocity", "Total velocity")}
events = {e[1]: float(e[0]) for e in
          re.findall(r'<event time="([\d.]+)" type="(\w+)"', sim)}

t = col["Time"]
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})

fig, (ax_h, ax_v) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
fig.suptitle(f"PhoenixABS40-43 — Klima D9-5 simulation ({ORK})\n{name}",
             fontsize=11, color=INK)

ax_h.plot(t, col["Altitude"], color=BLUE, lw=2)
ax_h.set_ylabel("Altitude (m)")
ax_v.plot(t, col["Total velocity"], color=BLUE, lw=2, label="Total velocity")
ax_v.plot(t, col["Vertical velocity"], color=ORANGE, lw=2, label="Vertical velocity")
ax_v.axhline(0, color=MUTED, lw=0.8)
ax_v.set_ylabel("Velocity (m/s)")
ax_v.set_xlabel("Time (s)")
ax_v.legend(frameon=False, loc="upper right")

labels = {"launchrod": "rod clear", "burnout": "burnout",
          "ejectioncharge": "ejection", "apogee": "apogee"}
for ax in (ax_h, ax_v):
    ax.grid(color="#e4e3df", lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for ev in labels:
        if ev in events:
            ax.axvline(events[ev], color=MUTED, lw=0.8, ls="--")
ax_h.text(0.98, 0.95, "\n".join(f"{labels[ev]:<10}{events[ev]:6.2f} s"
                                for ev in labels if ev in events),
          transform=ax_h.transAxes, ha="right", va="top", family="monospace",
          fontsize=8.5, color=MUTED)

i_apo = max(range(len(t)), key=lambda i: col["Altitude"][i])
ax_h.annotate(f"apogee {col['Altitude'][i_apo]:.0f} m",
              (t[i_apo], col["Altitude"][i_apo]), xytext=(12, -4),
              textcoords="offset points", color=INK, fontsize=9)
i_vmax = max(range(len(t)), key=lambda i: col["Total velocity"][i])
ax_v.annotate(f"max {col['Total velocity'][i_vmax]:.1f} m/s",
              (t[i_vmax], col["Total velocity"][i_vmax]), xytext=(8, 0),
              textcoords="offset points", color=INK, fontsize=9)
ax_v.annotate(f"ground hit {col['Vertical velocity'][-1]:.1f} m/s",
              (t[-1], col["Vertical velocity"][-1]), xytext=(-8, 6),
              textcoords="offset points", ha="right", color=INK, fontsize=9)

ax_v.set_xlim(0, t[-1])
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"{name}: apogee {col['Altitude'][i_apo]:.1f} m at {t[i_apo]:.2f} s, "
      f"max v {col['Total velocity'][i_vmax]:.1f} m/s at {t[i_vmax]:.2f} s, "
      f"flight {t[-1]:.1f} s -> {OUT}")

"""Builds the Bambu Studio X1C project files (.3mf) for the launch pad v2 print set (2026-10-27).
Same recipe as Ready to Print/D9/Bambu X1C/make_bambu_projects_v7.py (eSUN ABS, Engineering Plate, no supports).
Parts come pre-oriented from ../Ready to Print/ (written by Models/PhoenixABS40-43_launchpad_v2.py [14] and v1 [14]):
  StopPost v2  x1  lying on its flat back, U-channel up
  PadHub v1    x1  base down
  PadLeg v2    x3  = v1 leg, laid flat on its FLAT side (v1 STL floated the blade 8 mm)
The bought alu blast plate is not printed.
Run: python make_bambu_projects_launchpad.py [plate prefix ...]   e.g. "1_" rebuilds plate 1 only.
Needs Bambu Studio installed (uses its system presets + CLI)."""
import json, os, subprocess, sys

SYS = os.path.join(os.environ['APPDATA'], 'BambuStudio', 'system', 'BBL')
idx = {}
for sub in ('machine', 'process', 'filament'):
    for f in os.listdir(os.path.join(SYS, sub)):
        if f.endswith('.json'):
            try:
                d = json.load(open(os.path.join(SYS, sub, f), encoding='utf8'))
            except Exception:
                continue
            if 'name' in d:
                idx[(sub, d['name'])] = d


def resolve(sub, name):
    d = idx[(sub, name)]; out = {}
    if 'inherits' in d and d['inherits']:
        out.update(resolve(sub, d['inherits']))
    out.update(d); out.pop('inherits', None); return out


def write(sub, name, path, over=None, newname=None):
    d = resolve(sub, name)
    if over: d.update(over)
    if newname: d['name'] = newname
    d['from'] = 'User' if newname else 'system'
    json.dump(d, open(path, 'w', encoding='utf8'), indent=1)
    return d


HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "Ready to Print")
OUT = HERE
EXE = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
P = "PhoenixABS40-43_"


def two(v): return [str(v), str(v)]


COMMON = {"wall_generator": "arachne", "seam_position": "back", "enable_support": "0", "ironing_type": "no ironing",
          "brim_type": "outer_only", "sparse_infill_pattern": "gyroid", "curr_bed_type": "Engineering Plate",
          # eSUN ABS: print speed < 200 mm/s (BBL presets run infill/walls at 300+)
          "inner_wall_speed": two(150), "sparse_infill_speed": two(200), "internal_solid_infill_speed": two(200),
          "top_surface_speed": two(150), "gap_infill_speed": two(150)}
# eSUN ABS datasheet: 230-270 C, bed 95-110 C, fan 0 %, enclosed chamber
FIL = {"eng_plate_temp": ["100"], "eng_plate_temp_initial_layer": ["100"], "nozzle_temperature": ["260"],
       "nozzle_temperature_initial_layer": ["260"], "fan_min_speed": ["0"], "fan_max_speed": ["15"],
       "overhang_fan_speed": ["30"], "additional_cooling_fan_speed": ["0"], "filament_vendor": ["eSUN"]}

# StopPost: 218 mm long and thin on the bed -> 6 mm brim against ABS corner lift; 0.4 lines so the 1.5 mm
#   fuse throat stays open; slow bridges for the horizontal d4.2 / d2.2 bores.
POST = {"wall_loops": "4", "outer_wall_line_width": "0.4", "inner_wall_line_width": "0.4", "sparse_infill_density": "40%",
        "brim_width": "6", "outer_wall_speed": two(60), "bridge_speed": two(25), "bridge_flow": "0.9"}
# Legs: bending blades -> 5 walls, 60 % infill; hub: 5 walls round the reamed rod bore, 40 %.
LEG = {"wall_loops": "5", "sparse_infill_density": "60%", "brim_width": "6", "outer_wall_speed": two(80)}
HUB = {"wall_loops": "5", "sparse_infill_density": "40%", "brim_width": "4", "outer_wall_speed": two(80),
       "bridge_speed": two(25), "bridge_flow": "0.9"}

PLATES = [
    ("1_StopPost_v2_0.20mm", "0.20mm Standard @BBL X1C",
     [P + "StopPost_v2.stl"], POST),
    ("2_PadHub_v1_PadLeg_x3_v2_0.20mm", "0.20mm Standard @BBL X1C",
     [P + "PadHub_v1.stl"] + [P + "PadLeg_v2.stl"] * 3, LEG,
     {"PadHub_v1": {"sparse_infill_density": "40%", "brim_width": "4"}}),
    # everything in one job, each part on its own plate-1 / plate-2 settings
    ("3_ALL_StopPost_Hub_Legs_x3_0.20mm", "0.20mm Standard @BBL X1C",
     [P + "StopPost_v2.stl", P + "PadHub_v1.stl"] + [P + "PadLeg_v2.stl"] * 3, LEG,
     {"PadHub_v1": {"sparse_infill_density": "40%", "brim_width": "4"},
      "StopPost_v2": {"wall_loops": "4", "outer_wall_line_width": "0.4", "inner_wall_line_width": "0.4",
                      "sparse_infill_density": "40%", "outer_wall_speed": "60"}}),
]


def per_object(path, objover):
    """Write per-object setting overrides into the exported 3mf (Bambu reads <metadata key=.. value=..> per object)."""
    import zipfile, re, shutil
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin:
        ms = zin.read("Metadata/model_settings.config").decode()

        def inj(m):
            b = m.group(0); hdr = b.split("<part")[0]
            for key, sets in objover.items():
                if key in hdr:
                    extra = "".join(f'\n    <metadata key="{k}" value="{v}"/>' for k, v in sets.items())
                    b = b.replace('<metadata key="extruder" value="1"/>', '<metadata key="extruder" value="1"/>' + extra, 1)
            return b
        ms = re.sub(r'<object id="\d+">.*?</object>', inj, ms, flags=re.S)
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for it in zin.infolist():
                zout.writestr(it, ms.encode() if it.filename == "Metadata/model_settings.config" else zin.read(it.filename))
    shutil.move(tmp, path)


only = sys.argv[1:]
for name, proc, stls, over, *objover in PLATES:
    if only and not any(name.startswith(o) for o in only): continue
    o = dict(COMMON); o.update(over)
    os.chdir(os.environ.get('TEMP', '.'))
    write('machine', 'Bambu Lab X1 Carbon 0.4 nozzle', 'm.json')
    write('process', proc, 'p.json', o, newname=f"Phoenix pad {name}")
    write('filament', 'Generic ABS', 'f.json', FIL, newname="eSUN ABS - Phoenix")
    out = os.path.join(OUT, f"Phoenix_LaunchPad_plate{name}.3mf")
    cmd = [EXE, "--arrange", "1", "--orient", "0", "--load-settings", "m.json;p.json", "--load-filaments", "f.json",
           "--curr-bed-type", "Engineering Plate", "--export-3mf", out] + [os.path.join(SRC, s) for s in stls]
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    if objover and os.path.exists(out): per_object(out, objover[0])
    print(name, "rc", r.returncode, "exists", os.path.exists(out))
    tail = (r.stdout + r.stderr).strip().splitlines()[-15:]
    print("\n".join(tail))

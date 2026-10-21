"""v6 (2026-10-21): sled v18 (v17 = ESP32 E rail column to the deck floor, v18 = no ESP32 heels).  + plate 12 = EbayCap v6 +
   sled v18 (plate-10 settings); + plate 13 = FwdTube v8 + EbayCap v6 + sled v18 (plate-11 settings).
   Run "python make_bambu_projects_v6.py 12_ 13_" to build only the new plates (1..11 are as v5).
v5 (2026-10-20): sled v16 (ESP32 north in a solder-relieved slide-in slot, battery south, BMP N corner, solid piezo
   back plate).  + plate 10 = EbayCap v6 + sled v16 (plate-4 settings); + plate 11 = FwdTube v8 + EbayCap v6 + sled v16
   (plate-7 settings).  Run "python make_bambu_projects_v5.py 10_ 11_" to build only the new plates (1..9 are as v4).
v4 (2026-10-14): + plate 8 = AftTube v11 + fin can v11 (latches opposed 60/240 + clocking key; plate-2 settings);
   + plate 9 = FwdTube v8 + EbayCap v6 + sled v10 + AftTube v11 + fin can v11 in one job (user: "combined file with fwd,
   sled and this"), base = plate 4, per-object overrides: FwdTube = plate 1, AftTube / fin can = plate 2.
   Run "python make_bambu_projects_v4.py 8_ 9_" to build only the new plates (1..7 are as v3).
v3 (2026-10-14): sled v9 -> v10 (no-support print: ADXL on the tray back, BMP east, reed slide-in, ...);
   + plate 7 = FwdTube + EbayCap + sled in one job (user: "combine with fwd enclosure too").
v2 (2026-10-11): sled v8 -> v9 (solid Nano rails; v8 snap arms broke coming off the plate).
Builds the Bambu Studio X1C project files (.3mf) for the D9 print set.
Run: python make_bambu_projects.py [plate prefix ...]   e.g. "1_" rebuilds plate 1 only.
Needs Bambu Studio installed (uses its system presets + CLI)."""
import json,os,sys
SYS=os.path.join(os.environ['APPDATA'],'BambuStudio','system','BBL')
idx={}
for sub in ('machine','process','filament'):
    for f in os.listdir(os.path.join(SYS,sub)):
        if f.endswith('.json'):
            try: d=json.load(open(os.path.join(SYS,sub,f),encoding='utf8'))
            except Exception: continue
            if 'name' in d: idx[(sub,d['name'])]=d
def resolve(sub,name):
    d=idx[(sub,name)]; out={}
    if 'inherits' in d and d['inherits']: out.update(resolve(sub,d['inherits']))
    out.update(d); out.pop('inherits',None); return out
def write(sub,name,path,over=None,newname=None):
    d=resolve(sub,name)
    if over: d.update(over)
    if newname: d['name']=newname
    d['from']='User' if newname else 'system'
    json.dump(d,open(path,'w',encoding='utf8'),indent=1)
    return d
if False:  # debug dump
    m=write('machine','Bambu Lab X1 Carbon 0.4 nozzle','machine.json')
    f=write('filament','Generic ABS','filament.json')
    p=write('process','0.16mm Optimal @BBL X1C','process.json')
    for k in ['wall_loops','sparse_infill_density','sparse_infill_pattern','enable_support','brim_type','brim_width','wall_generator','seam_position','bridge_flow','bridge_speed','outer_wall_line_width','layer_height','top_shell_layers','bottom_shell_layers','ironing_type']:
        print(k,p.get(k))
    for k in ['nozzle_temperature','nozzle_temperature_initial_layer','hot_plate_temp','eng_plate_temp','fan_min_speed','fan_max_speed','overhang_fan_speed','additional_cooling_fan_speed','chamber_temperatures','filament_settings_id','compatible_printers']:
        print(k,f.get(k))
    print(m.get('printer_settings_id'), m.get('curr_bed_type'), p.get('curr_bed_type'))


# ---- plate builder ----
import json,os,subprocess,sys
D9=r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Print Files\Ready to Print\D9"
OUT=os.path.join(D9,"Bambu X1C")
os.makedirs(OUT,exist_ok=True)
EXE=r"C:\Program Files\Bambu Studio\bambu-studio.exe"
P="PhoenixABS40-43_"
def two(v): return [str(v),str(v)]
COMMON={"wall_generator":"arachne","seam_position":"back","enable_support":"0","ironing_type":"no ironing",
        "brim_type":"outer_only","sparse_infill_pattern":"gyroid","curr_bed_type":"Engineering Plate",
        # eSUN ABS: print speed < 200 mm/s (BBL presets run infill/walls at 300+)
        "inner_wall_speed":two(150),"sparse_infill_speed":two(200),"internal_solid_infill_speed":two(200),
        "top_surface_speed":two(150),"gap_infill_speed":two(150)}
# eSUN ABS datasheet: 230-270 C, bed 95-110 C, fan 0 %, enclosed chamber
FIL={"eng_plate_temp":["100"],"eng_plate_temp_initial_layer":["100"],"nozzle_temperature":["260"],
     "nozzle_temperature_initial_layer":["260"],"fan_min_speed":["0"],"fan_max_speed":["15"],
     "overhang_fan_speed":["30"],"additional_cooling_fan_speed":["0"],"filament_vendor":["eSUN"]}
PLATES=[
 ("1_FwdTube_v8_Nose_RetainerCap_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v8_FwdTube.stl",P+"nose_VonKarmanScrew_v6.stl",P+"MotorRetainerCap_v1.stl"],
  {"wall_loops":"5","sparse_infill_density":"20%","brim_width":"6","outer_wall_speed":two(40),"inner_wall_speed":two(100),
   "small_perimeter_speed":two("50%")}),
 ("2_AftTube_v9_FinCan_v9_0.20mm","0.20mm Standard @BBL X1C",
  [P+"D9aft_v9_AftTube.stl",P+"D9aft_v9_AftFinCanSlotted.stl"],
  # v9 snap latch: 0.40 wall lines so the 1.2 mm tongues are 3 clean lines (README)
  {"wall_loops":"4","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","sparse_infill_density":"40%","brim_width":"6","outer_wall_speed":two(80),"inner_wall_speed":two(150),
   "bridge_speed":two(25),"bridge_flow":"0.9"}),
 ("3_Fins_x3_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v4_Fin.stl"]*3,
  {"wall_loops":"3","sparse_infill_density":"100%","sparse_infill_pattern":"zig-zag","brim_width":"8","outer_wall_speed":two(80)}),
 ("4_EbayCap_v6_Sled_v10_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v10.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"}),
 ("5_SnapLatch_v2_test_0.20mm","0.20mm Standard @BBL X1C",
  [P+"SnapLatchCoupon_v2_TubeRing_L24.stl",P+"SnapLatchCoupon_v2_CouplerRing.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","outer_wall_speed":two(60),
   "bridge_speed":two(25)}),
 # overnight plate = e-bay + aft section in one job, every part on ITS OWN standard settings (no compromise):
 # base = plate 4 (EbayCap + sled); per-object overrides give the AftTube/fin can plate 2, the cap plate 1, the fins plate 3
 ("6_NIGHT_AftTube_FinCan_Fins_Cap_EbayCap_Sled_v10_standard","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v9_AftTube.stl",P+"D9aft_v9_AftFinCanSlotted.stl",P+"MotorRetainerCap_v1.stl",
   P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v10.stl"]+[P+"D9aft_v4_Fin.stl"]*3,
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"},
  {"D9aft_v9_AftTube":        {"layer_height":"0.2","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","outer_wall_speed":"80","brim_width":"6"},
   "D9aft_v9_AftFinCanSlotted":{"layer_height":"0.2","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","outer_wall_speed":"80","brim_width":"6"},
   "MotorRetainerCap_v1":     {"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"100","brim_width":"6"},
   "D9aft_v4_Fin":            {"wall_loops":"3","sparse_infill_density":"100%","sparse_infill_pattern":"zig-zag","outer_wall_speed":"80","brim_width":"8"}}),
  # v3: forward section in one job -- base = plate 4 (EbayCap + sled); the FwdTube keeps its plate-1 settings
 ("7_FwdTube_v8_EbayCap_v6_Sled_v10_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v8_FwdTube.stl",P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v10.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"},
  {"D9aft_v8_FwdTube":        {"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"100","brim_width":"6"}}),
 # v4: D9aft v11 aft section (opposed latches + key tab) on the plate-2 settings
 ("8_AftTube_v11_FinCan_v11_0.20mm","0.20mm Standard @BBL X1C",
  [P+"D9aft_v11_AftTube.stl",P+"D9aft_v11_AftFinCanSlotted.stl"],
  {"wall_loops":"4","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","sparse_infill_density":"40%","brim_width":"6","outer_wall_speed":two(80),"inner_wall_speed":two(150),
   "bridge_speed":two(25),"bridge_flow":"0.9"}),
 # v4: forward section + aft section in one job -- base = plate 4 (EbayCap + sled); FwdTube = plate 1, aft parts = plate 2
 # v5: sled v16 -- plate 4 / plate 7 settings
 ("10_EbayCap_v6_Sled_v16_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v16.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"}),
 ("11_FwdTube_v8_EbayCap_v6_Sled_v16_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v8_FwdTube.stl",P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v16.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"},
  {"D9aft_v8_FwdTube":        {"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"100","brim_width":"6"}}),
 # v6: sled v18 -- plate 10 / plate 11 settings
 ("12_EbayCap_v6_Sled_v18_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v18.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"}),
 ("13_FwdTube_v8_EbayCap_v6_Sled_v18_0.16mm","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v8_FwdTube.stl",P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v18.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"},
  {"D9aft_v8_FwdTube":        {"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"100","brim_width":"6"}}),
 ("9_FwdTube_v8_EbayCap_v6_Sled_v10_AftTube_v11_FinCan_v11_standard","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v8_FwdTube.stl",P+"D9aft_v6_EbayCap.stl",P+"ElectronicsSled_v10.stl",P+"D9aft_v11_AftTube.stl",P+"D9aft_v11_AftFinCanSlotted.stl"],
  {"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(60),
   "bridge_speed":two(25),"bridge_flow":"0.9"},
  {"D9aft_v8_FwdTube":         {"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"100","brim_width":"6"},
   "D9aft_v11_AftTube":        {"layer_height":"0.2","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","outer_wall_speed":"80","brim_width":"6"},
   "D9aft_v11_AftFinCanSlotted":{"layer_height":"0.2","outer_wall_line_width":"0.4","inner_wall_line_width":"0.4","outer_wall_speed":"80","brim_width":"6"}}),
]

def per_object(path,objover):
    """Write per-object setting overrides into the exported 3mf (Bambu reads <metadata key=.. value=..> per object)."""
    import zipfile,re,shutil
    tmp=path+".tmp"
    with zipfile.ZipFile(path) as zin:
        ms=zin.read("Metadata/model_settings.config").decode()
        def inj(m):
            b=m.group(0); hdr=b.split("<part")[0]
            for key,sets in objover.items():
                if key in hdr:
                    extra="".join(f'\n    <metadata key="{k}" value="{v}"/>' for k,v in sets.items())
                    b=b.replace('<metadata key="extruder" value="1"/>','<metadata key="extruder" value="1"/>'+extra,1)
            return b
        ms=re.sub(r'<object id="\d+">.*?</object>',inj,ms,flags=re.S)
        with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED) as zout:
            for it in zin.infolist():
                zout.writestr(it,ms.encode() if it.filename=="Metadata/model_settings.config" else zin.read(it.filename))
    shutil.move(tmp,path)

only=sys.argv[1:]
for name,proc,stls,over,*objover in PLATES:
    if only and not any(name.startswith(o) for o in only): continue
    o=dict(COMMON); o.update(over)
    os.chdir(os.environ.get('TEMP','.'))
    write('machine','Bambu Lab X1 Carbon 0.4 nozzle','m.json')
    write('process',proc,'p.json',o,newname=f"Phoenix {name}")
    write('filament','Generic ABS','f.json',FIL,newname="eSUN ABS - Phoenix")
    out=os.path.join(OUT,f"Phoenix_D9_plate{name}.3mf")
    cmd=[EXE,"--arrange","1","--orient","0","--load-settings","m.json;p.json","--load-filaments","f.json",
         "--curr-bed-type","Engineering Plate","--export-3mf",out]+[os.path.join(D9,s) for s in stls]
    r=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
    if objover and os.path.exists(out): per_object(out,objover[0])
    print(name,"rc",r.returncode,"exists",os.path.exists(out))
    tail=(r.stdout+r.stderr).strip().splitlines()[-15:]
    print("\n".join(tail))

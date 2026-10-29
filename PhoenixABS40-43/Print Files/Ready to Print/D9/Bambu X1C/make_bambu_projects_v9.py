"""v9 (2026-10-29): FAST eSUN ABS+HS variants of plates 17/18 (~25 % shorter). Slicing v8 showed the time is walls +
   island travel, not infill, so: sled + keeper at 0.20 mm layers (per-object; the threaded ring stays 0.16 so its
   flanks don't change), sled walls outer 120 / inner 220 (150 gained ~1 min: short segments are accel-bound),
   z-hop 0.4 -> 0.2, min layer time 6 -> 3 s.  Ring settings = v8.
   + plate 19 = ring v13 + sled v21 + keeper FAST (v8 plate 17: 2 h 47 -> ~2 h 04)
   + plate 20 = sled v21 + keeper FAST (v8 plate 18)
   Run "python make_bambu_projects_v9.py".
v8 (2026-10-29): eSUN ABS+HS (high-speed) plates for D9aft v13 (30 mm extension ring) + sled v21 + its top keeper.
   Plates 1..15 stay on plain eSUN ABS (make_bambu_projects_v7.py); everything here is "_ABSHS" and uses its own
   filament profile "eSUN ABS+HS - Phoenix" so the plain-ABS profile is never overwritten.
   eSUN ABS+HS datasheet: 230-270 C, bed 100-110 C, 50-300 mm/s, fan 0 %.
   ASSUMED (eSUN publishes none): max volumetric flow 22 mm3/s (Generic ABS = 15, which would cap HS at ~220 mm/s).
   Only bulk extrusion gets faster (inner walls, infill, solid infill); outer walls, small perimeters, bridges and
   the fit-critical thread skin keep their v7 speeds.
   + plate 16 = ring v13 alone (plate-14 settings); + plate 17 = ring v13 + sled v21 + top keeper (plate-15 settings,
   keeper per-object = tree supports, printed flipped as exported); + plate 18 = sled v21 + top keeper (no ring).
   Run "python make_bambu_projects_v8.py" (builds 16..18).
Needs Bambu Studio installed (uses its system presets + CLI)."""
import json,os,subprocess,sys,zipfile,re,shutil
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

D9=r"C:\Users\dick_\Documents\Rocketry\PhoenixABS40-43\Print Files\Ready to Print\D9"
OUT=os.path.join(D9,"Bambu X1C")
EXE=r"C:\Program Files\Bambu Studio\bambu-studio.exe"
P="PhoenixABS40-43_"
def two(v): return [str(v),str(v)]
COMMON={"wall_generator":"arachne","seam_position":"back","enable_support":"0","ironing_type":"no ironing",
        "brim_type":"outer_only","sparse_infill_pattern":"gyroid","curr_bed_type":"Engineering Plate",
        "support_type":"tree(auto)",
        # ABS+HS: bulk up to the 300 mm/s datasheet ceiling (flow-capped at 22 mm3/s), detail speeds as v7
        "inner_wall_speed":two(200),"sparse_infill_speed":two(270),"internal_solid_infill_speed":two(250),
        "top_surface_speed":two(150),"gap_infill_speed":two(150)}
FIL={"eng_plate_temp":["105"],"eng_plate_temp_initial_layer":["105"],"nozzle_temperature":["265"],
     "nozzle_temperature_initial_layer":["265"],"fan_min_speed":["0"],"fan_max_speed":["10"],
     "overhang_fan_speed":["30"],"additional_cooling_fan_speed":["0"],"filament_vendor":["eSUN"],
     "filament_max_volumetric_speed":["22"],
     # fan ~0: give the keeper / sled-top's tiny layers time to set
     "slow_down_layer_time":["3"],"filament_z_hop":["0.2"]}
RING={"wall_loops":"5","sparse_infill_density":"20%","outer_wall_speed":"40","inner_wall_speed":"120","brim_width":"6"}
KEEPER={"enable_support":"1","support_type":"tree(auto)","layer_height":"0.2"}
SLED020={"layer_height":"0.2"}
SLED={"wall_loops":"4","sparse_infill_density":"40%","brim_width":"4","outer_wall_speed":two(120),"inner_wall_speed":two(220),
      "bridge_speed":two(25),"bridge_flow":"0.9"}
PLATES=[
 ("19_ExtensionRing_v13_Sled_v21_TopKeeper_ABSHS_FAST","0.16mm Optimal @BBL X1C",
  [P+"D9aft_v13_ExtensionRing.stl",P+"ElectronicsSled_v21.stl",P+"TopKeeper_v21.stl"],
  SLED,{"D9aft_v13_ExtensionRing":RING,"ElectronicsSled_v21":SLED020,"TopKeeper_v21":KEEPER},
  # --arrange nests the sled into the ring bore (G-code conflict): fixed XY
  {"D9aft_v13_ExtensionRing":(80,128),"ElectronicsSled_v21":(140,128),"TopKeeper_v21":(190,128)}),
 ("20_Sled_v21_TopKeeper_ABSHS_FAST","0.16mm Optimal @BBL X1C",
  [P+"ElectronicsSled_v21.stl",P+"TopKeeper_v21.stl"],
  SLED,{"ElectronicsSled_v21":SLED020,"TopKeeper_v21":KEEPER}),
]

def per_object(path,objover):
    """Write per-object setting overrides into the exported 3mf (Bambu reads <metadata key=.. value=..> per object)."""
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

def place(path,xy):
    """Overwrite the build-item XY translation of the objects whose name contains a key (rotation / Z kept)."""
    tmp=path+".tmp"
    with zipfile.ZipFile(path) as zin:
        ms=zin.read("Metadata/model_settings.config").decode()
        ids={}
        for m in re.finditer(r'<object id="(\d+)">(.*?)</object>',ms,flags=re.S):
            for key in xy:
                if key in m.group(2).split("<part")[0]: ids[m.group(1)]=xy[key]
        mod=zin.read("3D/3dmodel.model").decode()
        def mv(m):
            if m.group(1) not in ids: return m.group(0)
            t=m.group(2).split(); t[9],t[10]=str(ids[m.group(1)][0]),str(ids[m.group(1)][1])
            return m.group(0).replace(m.group(2)," ".join(t))
        mod=re.sub(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"',mv,mod)
        with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED) as zout:
            for it in zin.infolist():
                zout.writestr(it,mod.encode() if it.filename=="3D/3dmodel.model" else zin.read(it.filename))
    shutil.move(tmp,path)

only=sys.argv[1:]
for name,proc,stls,over,*objover in PLATES:
    if only and not any(name.startswith(o) for o in only): continue
    o=dict(COMMON); o.update(over)
    os.chdir(os.environ.get('TEMP','.'))
    write('machine','Bambu Lab X1 Carbon 0.4 nozzle','m.json')
    write('process',proc,'p.json',o,newname=f"Phoenix {name}")
    write('filament','Generic ABS','f.json',FIL,newname="eSUN ABS+HS - Phoenix")
    out=os.path.join(OUT,f"Phoenix_D9_plate{name}.3mf")
    cmd=[EXE,"--arrange","1","--orient","0","--load-settings","m.json;p.json","--load-filaments","f.json",
         "--curr-bed-type","Engineering Plate","--export-3mf",out]+[os.path.join(D9,s) for s in stls]
    r=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
    if objover and os.path.exists(out): per_object(out,objover[0])
    if len(objover)>1 and os.path.exists(out): place(out,objover[1])
    print(name,"rc",r.returncode,"exists",os.path.exists(out))
    tail=(r.stdout+r.stderr).strip().splitlines()[-15:]
    print("\n".join(tail))

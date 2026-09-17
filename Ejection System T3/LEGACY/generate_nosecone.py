"""
Parametric generator for the sideways-ejection nosecone (40mm ID / 43mm OD airframe).
Run inside FreeCAD (Python console or via the FreeCAD MCP execute_code tool) with a
document named "Sideways_Ejection_NoseCone_v1" already active/created.

The saved .FCStd only contains baked Part::Feature shapes (no parametric tree), so
this script is the source of truth for every dimension (Lo, door_angle, wall, etc).
Edit the PARAMETERS block and re-run to regenerate.
"""
import math
import FreeCAD as App
import Part

doc = App.getDocument("Sideways_Ejection_NoseCone_v1")
for o in list(doc.Objects):
    doc.removeObject(o.Name)
doc.recompute()

# ---------------- PARAMETERS (mm) ----------------
OD = 43.0                  # airframe outer diameter
R  = OD/2.0
wall = 2.0                 # printed shell wall thickness
ID_body = 40.0              # airframe inner diameter
shoulder_clear = 0.4        # total diametral clearance, shoulder into body tube
Rs = (ID_body - shoulder_clear)/2.0

Lo   = 120.0                # full ogive length -- the ENTIRE ogive is the parachute bay
Lsh  = 45.0                 # shoulder length inserted into the body tube
x1   = 30.0                 # tip-cap length (hull-only, full circumference, sharp closed point)
tongue_len = 5.0            # axial length of the forward tongue-and-groove interlock (short edge)
lip_thick  = 1.0            # radial split between hull lip (outer) and door tongue (inner)
edge_margin_deg = 4.0        # width of the continuous long-edge lip/tongue interlock (both seams)

door_angle = 130.0          # arc width of the door/lid piece (hull keeps the other ~230 deg)
clear_ang  = 1.0            # angular clearance (deg) each side of the door seam

def revolve_profile(points_xr):
    pts = [App.Vector(x, max(r,0.0), 0) for x,r in points_xr]
    edges = [Part.makeLine(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    edges.append(Part.makeLine(pts[-1], App.Vector(pts[-1].x,0,0)))
    edges.append(Part.makeLine(App.Vector(pts[-1].x,0,0), App.Vector(pts[0].x,0,0)))
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    out = face.revolve(App.Vector(0,0,0), App.Vector(1,0,0), 360)
    return out if out is not None else face

n = 60
rho = (R**2 + Lo**2)/(2*R)                 # tangent-ogive radius of curvature
def outer_r(x): return math.sqrt(max(rho**2-(Lo-x)**2,0.0)) - (rho-R)
def inner_r(x): return max(outer_r(x)-wall, 0.0)
def split_r(x): return max(outer_r(x)-lip_thick, 0.0)

pts_x = [Lo*i/n for i in range(n+1)]
outer_pts = [(x, R if x==Lo else outer_r(x)) for x in pts_x]
inner_pts = [(x, inner_r(x)) for x in pts_x]
split_pts = [(x, split_r(x)) for x in pts_x]

ogive_outer = revolve_profile(outer_pts)
ogive_inner = revolve_profile(inner_pts)
ogive_shell = ogive_outer.cut(ogive_inner)   # full hollow ogive, x in [0,Lo]
split_solid = revolve_profile(split_pts)     # ogive offset inward by lip_thick -- divides lip/tongue

sh_outer = Part.makeCylinder(Rs, Lsh, App.Vector(Lo,0,0), App.Vector(1,0,0))
sh_inner = Part.makeCylinder(Rs-wall, Lsh+4, App.Vector(Lo-2,0,0), App.Vector(1,0,0))
shoulder_tube = sh_outer.cut(sh_inner)

box_A = Part.makeBox(x1+1, 120,120, App.Vector(-1,-60,-60))
box_B = Part.makeBox(Lo-x1+2, 120,120, App.Vector(x1,-60,-60))
segA = ogive_shell.common(box_A)             # tip cap, x in [0,x1], full circumference
segB = ogive_shell.common(box_B)             # split region, x in [x1,Lo]

# Angle convention (verified empirically against Part.makeCylinder's angle param):
# a point at sweep-angle theta sits at (Y,Z) = (-R*sin(theta), R*cos(theta));
# theta=-90 -> +Y (door side), theta=+90 -> -Y (hull "keel" side).
rot_door_big = -90.0 - (door_angle+2*clear_ang)/2.0
rot_door     = -90.0 - door_angle/2.0

def wedge(angle, x0, length, rot):
    w = Part.makeCylinder(R+5, length, App.Vector(x0,0,0), App.Vector(1,0,0), angle)
    w.rotate(App.Vector(0,0,0), App.Vector(1,0,0), rot)
    return w

# --- main door region ---
dw_big = wedge(door_angle+2*clear_ang, x1-1, Lo-x1+3, rot_door_big)
dw_nom = wedge(door_angle,             x1-1, Lo-x1+3, rot_door)
door_piece_B = segB.common(dw_nom)
hull_piece_B = segB.cut(dw_big)

# --- continuous long-edge lip/tongue interlock along both seams, x1..Lo ---
# Addresses a DIFFERENT failure mode than the tip tongue below: this is what keeps an ~80mm
# unsupported door edge from lifting/fluttering in flight between the single aft latch and the
# tip, inspired by the "Federlasche" (spring tab) edge retention seen on the reference design.
ew1 = wedge(edge_margin_deg, x1-1, Lo-x1+3, rot_door)                              # door's start edge
ew2 = wedge(edge_margin_deg, x1-1, Lo-x1+3, rot_door+door_angle-edge_margin_deg)   # door's end edge
edge_zone_1 = door_piece_B.common(ew1)
edge_zone_2 = door_piece_B.common(ew2)
edge_lip_1 = edge_zone_1.cut(split_solid)      # outer 1mm -> goes to hull (overlapping lip)
edge_lip_2 = edge_zone_2.cut(split_solid)
door_piece_B = door_piece_B.cut(edge_lip_1).cut(edge_lip_2)   # door recessed along both long edges
hull_piece_B = hull_piece_B.fuse(edge_lip_1).fuse(edge_lip_2) # hull overlaps both edges

# --- forward tongue-and-groove interlock (tip end, x1-tongue_len .. x1) ---
tz0 = x1 - tongue_len
tw_big = wedge(door_angle+2*clear_ang, tz0-1, tongue_len+2, rot_door_big)
tw_nom = wedge(door_angle,             tz0-1, tongue_len+2, rot_door)
tongue_zone_big = segA.common(tw_big)
tongue_zone_nom = segA.common(tw_nom)
lip_part    = tongue_zone_nom.cut(split_solid)     # outer 1mm -> stays with hull
tongue_part = tongue_zone_nom.common(split_solid)  # inner 1mm -> becomes the door's forward tongue
segA_final  = segA.cut(tongue_zone_big).fuse(lip_part)
door_with_tongue = door_piece_B.fuse(tongue_part)

# ================= LATCH MECHANISM =================
# Load path: the pawl pivots on its OWN fixed pin pressed into the bulkhead, so the door's
# retention load reacts into the bulkhead -- NOT into the servo's output spline/bushing.
# The servo drives the pawl's short crank tab through a separate horn + link, supplying only
# the rotation needed to release it.
lug_len, lug_w, lug_h = 10.0, 8.0, 8.0
lug_x = 111.0                                # near the aft edge of the door, by the bulkhead
lug_ir = inner_r(lug_x)
lug_hole_y = lug_ir - lug_w/2.0
lug_box = Part.makeBox(lug_len, lug_w, lug_h, App.Vector(lug_x-lug_len/2.0, lug_ir-lug_w, -lug_h/2.0))
lug_hole = Part.makeCylinder(1.6, lug_len+4, App.Vector(lug_x-lug_len/2.0-2, lug_hole_y, 0), App.Vector(1,0,0))
lug = lug_box.cut(lug_hole)
door_final = door_with_tongue.fuse(lug)

bulkhead_x = lug_x - 2.0                     # aligned axially with the lug so the pawl reaches it
bh_thick = 4.0
bh_span = (bulkhead_x-bh_thick/2.0, bulkhead_x+bh_thick/2.0)
bh_R = min(inner_r(bh_span[0]), inner_r(bh_span[1])) - 0.3   # local-radius-aware; clears the shoulder
bulkhead_disc = Part.makeCylinder(bh_R, bh_thick, App.Vector(bh_span[0],0,0), App.Vector(1,0,0))

arm_len = 8.0
pivot_y, pivot_z = lug_hole_y - arm_len, 0.0     # fixed pawl pivot

# Servo offset mainly toward -Y (the hull/keel side, away from the door aperture) so its
# corner-radius-from-axis stays well inside the local inner wall (checked: servo^hull == 0).
servo_y, servo_z = pivot_y - 10.0, 0.0
crank_len = 4.0
horn_len  = 5.0

pin_hole   = Part.makeCylinder(1.6, bh_thick+4, App.Vector(bh_span[0]-2, pivot_y, pivot_z), App.Vector(1,0,0))
servo_hole = Part.makeCylinder(3.0, bh_thick+4, App.Vector(bh_span[0]-2, servo_y, servo_z), App.Vector(1,0,0))
screw_h1   = Part.makeCylinder(1.1, bh_thick+4, App.Vector(bh_span[0]-2, servo_y, servo_z-5), App.Vector(1,0,0))
screw_h2   = Part.makeCylinder(1.1, bh_thick+4, App.Vector(bh_span[0]-2, servo_y, servo_z+5), App.Vector(1,0,0))
anchor_hole= Part.makeCylinder(1.8, bh_thick+4, App.Vector(bh_span[0]-2, 12.0, 10.0), App.Vector(1,0,0))
pass_hole  = Part.makeCylinder(3.0, bh_thick+4, App.Vector(bh_span[0]-2, -6.0, -12.0), App.Vector(1,0,0))
bulkhead = bulkhead_disc.cut(pin_hole).cut(servo_hole).cut(screw_h1).cut(screw_h2).cut(anchor_hole).cut(pass_hole)

pin_x0 = bh_span[1]
pivot_pin = Part.makeCylinder(1.5, 7.0, App.Vector(pin_x0, pivot_y, pivot_z), App.Vector(1,0,0))

arm_x = pin_x0 + 1.0
hub_r, arm_w, arm_t = 3.5, 3.0, 3.0
hub = Part.makeCylinder(hub_r, arm_t, App.Vector(arm_x, pivot_y, pivot_z), App.Vector(1,0,0))
main_arm = Part.makeBox(arm_t, arm_len, arm_w, App.Vector(arm_x, pivot_y, pivot_z-arm_w/2.0))
hook_tip = Part.makeCylinder(2.5, arm_t, App.Vector(arm_x, pivot_y+arm_len, pivot_z), App.Vector(1,0,0))
crank_arm = Part.makeBox(arm_t, crank_len, arm_w, App.Vector(arm_x, pivot_y-crank_len, pivot_z-arm_w/2.0))
crank_tip_boss = Part.makeCylinder(1.8, arm_t, App.Vector(arm_x, pivot_y-crank_len, pivot_z), App.Vector(1,0,0))
pawl = hub.fuse(main_arm).fuse(hook_tip).fuse(crank_arm).fuse(crank_tip_boss)

servo_L, servo_W, servo_H = 20.0, 9.0, 19.0   # sub-micro servo reference envelope
servo_box = Part.makeBox(servo_L, servo_W, servo_H,
                          App.Vector(bh_span[0]-servo_L, servo_y-servo_W/2.0, servo_z-servo_H/2.0))
horn_hub = Part.makeCylinder(2.5, arm_t, App.Vector(arm_x, servo_y, servo_z), App.Vector(1,0,0))
horn_blade = Part.makeBox(arm_t, horn_len, arm_w, App.Vector(arm_x, servo_y, servo_z-arm_w/2.0))
horn = horn_hub.fuse(horn_blade)
link = Part.makeCylinder(1.5, arm_t, App.Vector(arm_x, (pivot_y-crank_len + servo_y+horn_len)/2.0, pivot_z), App.Vector(1,0,0))
servo_linkage = servo_box.fuse(horn)

# ================= TIP EYELET (hull-mounted anchor for the main recovery harness) =================
x_eye = None
for i in range(1,400):
    xt = Lo*i/400.0
    if outer_r(xt) >= 12.0:
        x_eye = xt; break
if x_eye is None: x_eye = x1*0.9
rin_local = inner_r(x_eye)
boss_depth = min(6.0, rin_local-2.0)
eye_y_outer = -rin_local
eye_y_inner = -(rin_local - boss_depth)
eye_box = Part.makeBox(9.0, boss_depth, 7.0, App.Vector(x_eye-4.5, eye_y_outer, -3.5))
eye_hole = Part.makeCylinder(1.6, 9.0+4, App.Vector(x_eye-4.5-2, (eye_y_outer+eye_y_inner)/2.0, 0), App.Vector(1,0,0))
tip_eyelet = eye_box.cut(eye_hole)
tip_pt = App.Vector(x_eye, (eye_y_outer+eye_y_inner)/2.0, 0.0)

# ================= SHOCK CORD TOPOLOGY =================
# (A) short door leash: lug -> dedicated bulkhead anchor. Does NOT route through the packed canopy.
# (B) main recovery harness: airframe -> pass_hole -> chute attach point -> continues to the tip
#     eyelet, so the hull itself is tethered too (backup if the shoulder friction-fit ever lets go).
anchor_pt = App.Vector(bh_span[0], 12.0, 10.0)
lug_pt    = App.Vector(lug_x, lug_hole_y, 0.0)
pass_pt   = App.Vector(bh_span[0], -6.0, -12.0)
chute_pt  = App.Vector(bulkhead_x+8.0, -6.0, -12.0)

def cord(p1,p2,r=0.75):
    v=p2-p1; L=v.Length
    if L<1e-6: return None
    v.normalize()
    return Part.makeCylinder(r,L,p1,v)

cordA = cord(anchor_pt, lug_pt)
cordB = cord(pass_pt, chute_pt).fuse(cord(chute_pt, tip_pt))

hull = segA_final.fuse(hull_piece_B).fuse(shoulder_tube).fuse(tip_eyelet)
hull = hull.removeSplitter()
latch_assy = pawl.fuse(pivot_pin).fuse(link)

def add(name, shape, color, transp=0):
    if doc.getObject(name): doc.removeObject(name)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = transp
    return obj

add("Hull_MainPiece", hull, (0.78,0.78,0.8), 45)
add("Door_LidPiece", door_final, (0.95,0.55,0.15), 0)
add("DeploymentBulkhead", bulkhead, (0.2,0.4,0.9), 0)
add("Pawl_Latch_ClosedPos", latch_assy, (0.85,0.1,0.1), 0)
add("Servo_REFERENCE_COTS", servo_linkage, (0.2,0.8,0.3), 40)
add("ShockCord_DoorLeash", cordA, (1.0,1.0,0.2), 0)
add("ShockCord_MainHarness", cordB, (1.0,0.85,0.1), 0)

doc.recompute()
doc.save()

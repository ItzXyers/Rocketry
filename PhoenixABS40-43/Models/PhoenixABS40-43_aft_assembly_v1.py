# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- aft end, assembled view (cfg C, the one-piece fin can).

Builds a FreeCAD document with everything in its flight position. Reads the verified
STEP exports rather than rebuilding, so what you look at is what was checked.

  REAL PARTS (verified, printable)   REFERENCE (stand-ins, not printable)
  -------------------------------   -----------------------------------
  AftFinCan   -- fins printed in     DummyMotor   18 x 70 stand-in
  MotorRetainerCap                   FwdTubeStub  60 mm of forward airframe, slid
                                                  over the lip onto the shoulder

For cfg B instead -- the slotted section with three separately printed fins -- set
CFG = "B" below; it places AftSectionSealed with three copies of Fin in their slots.

Run:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" \
      Models/PhoenixABS40-43_aft_assembly_v1.py

Colours are NOT set: FreeCADCmd has no ViewObject, so the document opens in default
grey. Frame is the same as the build script -- Z = 0 at the airframe's aft face.
"""

import os
import math

import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

PROJECT = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry", "PhoenixABS40-43")
MODELS = os.path.join(PROJECT, "Models")
RENDER = os.path.join(MODELS, "_render")          # coarse meshes, for the preview only
REV = "v1"

# --- airframe / fin planform, from PhoenixABS40-43.ork rev 5 ---
R_AF_O, R_AF_I = 21.5, 20.0
FIN_N = 3
FIN_ROOT, FIN_TIP = 50.8, 25.0
FIN_SPAN, FIN_SWEEP = 55.0, 25.4
FIN_T = 2.0
FIN_Z0, FIN_Z1 = 0.6, 51.4                        # matches the slots in the section
FIN_TAB_R = 10.7                                  # slot inner radius
SHOULDER_Z = 51.4
MOTOR_R, MOTOR_Z0, MOTOR_Z1 = 9.0, -14.1, 55.9
STUB_LEN = 60.0


CFG = "C"          # "C" = one-piece fin can, "B" = slotted section + 3 bonded fins


def _unused_fin(angle_deg):
    """One fin: planform plus the through-the-wall root tab, as one flat 2 mm plate."""
    r_tip = R_AF_O + FIN_SPAN
    z_tip_le = FIN_Z1 - FIN_SWEEP
    pts = [
        (FIN_TAB_R, FIN_Z0),          # tab, inboard end
        (FIN_TAB_R, FIN_Z1),
        (R_AF_O, FIN_Z1),             # root leading edge
        (r_tip, z_tip_le),            # tip leading edge
        (r_tip, z_tip_le - FIN_TIP),  # tip trailing edge
        (R_AF_O, FIN_Z0),             # root trailing edge
    ]
    vs = [Vector(r, -FIN_T / 2.0, z) for r, z in pts]
    face = Part.Face(Part.Wire(Part.makePolygon(vs + [vs[0]])))
    solid = face.extrude(Vector(0, FIN_T, 0))
    solid.rotate(Vector(0, 0, 0), Vector(0, 0, 1), angle_deg)
    return solid


def main():
    if not os.path.isdir(RENDER):
        os.makedirs(RENDER)

    doc = App.newDocument("PhoenixABS40-43_aft_assembly")
    bodies = []

    def step(name):
        path = os.path.join(MODELS, "PhoenixABS40-43_%s_%s.step" % (name, REV))
        if not os.path.exists(path):
            raise SystemExit("missing %s -- run the build script first" % path)
        sh = Part.Shape()
        sh.read(path)
        return sh

    if CFG == "C":
        bodies.append(("AftFinCan", step("AftFinCan")))
    else:
        bodies.append(("AftSectionSealed", step("AftSectionSealed")))
        base_fin = step("Fin")
        for k in range(FIN_N):
            f = Part.Shape(base_fin)
            f.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 360.0 * k / FIN_N)
            bodies.append(("Fin_%s" % "ABC"[k], f))
    bodies.append(("MotorRetainerCap", step("MotorRetainerCap")))

    bodies.append(("DummyMotor",
                   Part.makeCylinder(MOTOR_R, MOTOR_Z1 - MOTOR_Z0,
                                     Vector(0, 0, MOTOR_Z0))))
    stub = Part.makeCylinder(R_AF_O, STUB_LEN, Vector(0, 0, SHOULDER_Z))
    stub = stub.cut(Part.makeCylinder(R_AF_I, STUB_LEN + 2.0,
                                      Vector(0, 0, SHOULDER_Z - 1.0)))
    bodies.append(("FwdTubeStub", stub))

    print("=" * 74)
    print("Phoenix ABS 40-43 -- aft assembly, %s (cfg %s)" % (REV, CFG))
    print("=" * 74)
    for name, sh in bodies:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = sh
        bb = sh.BoundBox
        print("  %-17s %9.1f mm3 %6.2f g  Z %7.1f .. %6.1f"
              % (name, sh.Volume, sh.Volume * 1.05e-3, bb.ZMin, bb.ZMax))
        msh = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.12,
                                     AngularDeflection=0.35, Relative=False)
        msh.write(os.path.join(RENDER, name + ".stl"))

    doc.recompute()
    out = os.path.join(MODELS, "PhoenixABS40-43_aft_assembly_%s.FCStd" % REV)
    doc.saveAs(out)
    print("\n  saved %s" % os.path.basename(out))

    print("\n  pairwise interference (mm3):")
    named = dict(bodies)
    main_body = "AftFinCan" if CFG == "C" else "AftSectionSealed"
    pairs = [(main_body, "DummyMotor"), ("MotorRetainerCap", "DummyMotor"),
             (main_body, "FwdTubeStub"), ("MotorRetainerCap", "FwdTubeStub")]
    if CFG == "B":
        pairs += [("Fin_A", "DummyMotor"), ("Fin_A", "MotorRetainerCap"),
                  ("Fin_A", "FwdTubeStub")]
    for a, b in pairs:
        try:
            v = named[a].common(named[b]).Volume
            flag = "ok" if v < 1.0 else "CHECK"
        except Exception as exc:
            v, flag = float("nan"), "boolean failed (%s)" % type(exc).__name__
        print("    %-17s x %-15s %9.3f  %s" % (a, b, v, flag))


main()

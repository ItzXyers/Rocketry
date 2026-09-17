# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- printable test pins for the ejection POC (sliding-catch v1).

The sliding-catch mechanism needs three small pins:
  * CRANK PIN  -- d3, presses into the knob at radius 3 mm, sticks up into the
                  slider's cross-slot. Steel is better (a nail / d3 dowel) but a
                  printed one is fine to prove the motion.
  * RBF PIN    -- d2, drops through the knob + carrier holes at ARMED to lock the
                  knob. Any d2 wire / paperclip works; printed included for a kit.
  * COLLAR PIN -- d1.5, transverse, driven through a CatchCollar half + the shaft +
                  the other half to retain the collar (rev (e); was a solvent weld).
                  HEADLESS -- a head would foul the ledge pocket -- press fit, fitted
                  LAST through the access slot. A d1.5 steel dowel / brad is better.

Run headless:
  "C:/Users/dick_/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe" <this file>

Writes  Print Files/PhoenixABS40-43_TestPins_v1.stl  -- lay flat, print with a brim
(or stand them up for roundness). Ream/clean the holes with the pin before assembly.
"""

import os
import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector

PRINTS = os.path.join(os.path.expanduser("~"), "Documents", "Rocketry",
                      "PhoenixABS40-43", "Print Files", "Ejection System")   # reorganised tree

CRANK_D = 3.0          # matches CRANK_PIN_R*2 in the build script (d3, +0 tolerance = snug press)
CRANK_LEN = 18.5       # = PIN_TOP_Z - PIN_BOT_Z in the build script: 4 mm into the solid knob
                       #   body, up through the ledge, 3.5 mm into the slider slot.  16.5 -> 18.5
                       #   at rev (e): the ledge deepened 4 -> 6 mm and the knob moved ~2 mm aft.
                       #   The build script imports this module and checks these against its own
                       #   geometry [P] -- if this drifts, [P] fails "reprint the pins".
RBF_D = 2.0
RBF_LEN = 16.0         # knob bottom -> carrier top + 3; unchanged by rev (e) (that stack height
                       #   is KNOB_T + carrier depth, which did not move)
COLLAR_D = 1.5         # matches COLLAR_PIN_R*2.  Transverse collar retainer (rev (e)).
COLLAR_LEN = 8.6       # = COLLAR_PIN_LEN in the build script (2*COLLAR_R - 0.4): ends 0.2 mm
                       #   inside the d9 OD so they clear the ledge pocket over the stroke.
HEAD_D = 5.0           # a small head so a pin can't push all the way through
HEAD_T = 2.0
N_CRANK = 3            # 2 needed + 1 spare
N_RBF = 2
N_COLLAR = 2          # 1 needed + 1 spare

def pin(d, L, x, head=True):
    p = Part.makeCylinder(d / 2.0, L, Vector(x, 0, d / 2.0), Vector(0, 1, 0))
    if head:
        p = p.fuse(Part.makeCylinder(HEAD_D / 2.0, HEAD_T, Vector(x, 0, d / 2.0), Vector(0, 1, 0)))
    # 0.4 mm lead chamfer on the far end
    ch = min(0.4, d / 2.0 - 0.2)
    tip = Part.makeCone(d / 2.0, d / 2.0 - ch, ch, Vector(x, L, d / 2.0), Vector(0, 1, 0))
    return p.fuse(tip)

def build_pins():
    """The full pin set as one compound, laid flat with the axes along +Y.
    The ejection-POC build script imports this so the plate bundle and the [P]
    cross-check use THIS geometry rather than a second copy of the numbers."""
    parts = []
    x = 0.0
    for _ in range(N_CRANK):
        parts.append(pin(CRANK_D, CRANK_LEN, x)); x += 7.0
    for _ in range(N_RBF):
        parts.append(pin(RBF_D, RBF_LEN, x)); x += 6.0
    for _ in range(N_COLLAR):
        parts.append(pin(COLLAR_D, COLLAR_LEN, x, head=False)); x += 5.0   # headless -- fouls the pocket
    return Part.makeCompound(parts)


# NB __name__ is NOT usable as the run/import guard here: FreeCADCmd execs a script with
# __name__ set to the file's basename, which is exactly what an import gives too.  The
# build script sets __RUN_MAIN__ = False in this module's namespace before exec'ing it.
if globals().get("__RUN_MAIN__", True):
    comp = build_pins()
    m = MeshPart.meshFromShape(Shape=comp, LinearDeflection=0.04, AngularDeflection=0.2)
    out = os.path.join(PRINTS, "PhoenixABS40-43_TestPins_v1.stl")
    m.write(out)
    print("wrote %s  (%d crank + %d RBF + %d collar pins)" % (out, N_CRANK, N_RBF, N_COLLAR))

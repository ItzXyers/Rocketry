# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- interactive latch driver for the ejection POC (sliding-catch v1).

Open the assembly, then run this file (Macro > Execute, or paste in the Py console):
    exec(open(r"C:\\Users\\dick_\\Documents\\Rocketry\\PhoenixABS40-43\\Models\\ejection_poc_interactive.py").read())

A slider window appears (always on top).  Drag it 0 -> 100:

  0            KNOB at 0 deg.  ARMED.  The slider notch is hooked over the pinned
               CatchCollar; the cocked spring load runs shaft -> collar pin -> collar
               top -> slider -> the reaction PLATE -> cage -> airframe.  The knob is on
               a crank dead centre, so a shove on the slider makes no knob torque.
  0 -> ~95     KNOB turns toward 180 deg.  Its off-centre crank pin swings and drags
               the SLIDER sideways, out from over the collar.
  > ~95        RELEASED.  The one-piece PistonShaft + dummy nose jump up STROKE mm.

reset()  puts everything back.
"""

import math
import FreeCAD as App
import FreeCADGui as Gui

try:
    from PySide import QtCore, QtWidgets
except ImportError:
    try:
        from PySide2 import QtCore, QtWidgets
    except ImportError:
        from PySide6 import QtCore, QtWidgets

# --- constants, straight from PhoenixABS40-43_ejection_poc_v1.py ---
KNOB_AX_X, KNOB_AX_Y = -8.0, 0.0
CRANK_R = 3.0
STROKE = 40.0
RELEASE_FRAC = 0.95                       # slider is clear of the collar past here
DOC_HINT = "ejection_poc_asm"

# ARMED poses (explicit -> re-running the macro always starts clean)
ARMED = {
    "Knob": App.Placement(),
    "Slider": App.Placement(),
    "PistonShaft": App.Placement(),
    "DummyNose": App.Placement(),
    "CrankPin": App.Placement(),
}


def _doc():
    if DOC_HINT in App.listDocuments():
        return App.getDocument(DOC_HINT)
    return App.ActiveDocument


def slider_dx(phi):
    return CRANK_R * (math.cos(math.radians(phi)) - 1.0)


class LatchDriver(QtWidgets.QWidget):
    def __init__(self):
        super(LatchDriver, self).__init__()
        self.setWindowTitle("Ejection POC  --  latch")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.resize(360, 120)
        lay = QtWidgets.QVBoxLayout(self)
        self.lab = QtWidgets.QLabel(); self.lab.setWordWrap(True)
        lay.addWidget(self.lab)
        self.sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sl.setRange(0, 100); self.sl.valueChanged.connect(self.pose)
        lay.addWidget(self.sl)
        row = QtWidgets.QHBoxLayout()
        for t, v in (("\u25c0 ARM", 0), ("FIRE \u25b6", 100)):
            b = QtWidgets.QPushButton(t)
            b.clicked.connect(lambda _=0, vv=v: self.sl.setValue(vv))
            row.addWidget(b)
        lay.addLayout(row)
        self.pose()

    def pose(self):
        d = _doc()
        if d is None:
            self.lab.setText("open the assembly FCStd first")
            return
        f = self.sl.value() / 100.0
        phi = f * 180.0
        dx = slider_dx(phi)
        released = f >= RELEASE_FRAC
        fire = STROKE if released else 0.0

        kn = d.getObject("Knob")
        if kn:
            kn.Placement = App.Placement(App.Vector(), App.Rotation(App.Vector(0, 0, 1), phi),
                                         App.Vector(KNOB_AX_X, KNOB_AX_Y, 0))
        cp = d.getObject("CrankPin")
        if cp:
            cp.Placement = App.Placement(App.Vector(), App.Rotation(App.Vector(0, 0, 1), phi),
                                         App.Vector(KNOB_AX_X, KNOB_AX_Y, 0))
        sl = d.getObject("Slider")
        if sl:
            sl.Placement = App.Placement(App.Vector(dx, 0, 0), App.Rotation())
        for nm in ("PistonShaft", "DummyNose"):
            o = d.getObject(nm)
            if o:
                o.Placement = App.Placement(App.Vector(0, 0, fire), App.Rotation())

        d.recompute()
        if f <= 0.005:
            msg = "ARMED  --  knob 0\u00b0 (crank dead centre).  Slider hooked over the collar."
        elif released:
            msg = "FIRED  --  knob %.0f\u00b0, slider out %.1f mm, catch cleared, piston + %.0f mm." \
                  % (phi, -dx, STROKE)
        else:
            msg = "releasing\u2026  knob %.0f\u00b0,  slider out %.2f mm" % (phi, -dx)
        self.lab.setText(msg)
        try:
            Gui.updateGui()
        except Exception:
            pass


def reset():
    d = _doc()
    for nm, pl in ARMED.items():
        o = d.getObject(nm) if d else None
        if o:
            o.Placement = pl
    if d:
        d.recompute()


_latch_driver = LatchDriver()
_latch_driver.show()

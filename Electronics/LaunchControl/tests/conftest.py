"""Forces gpiozero onto its MockFactory before anything imports gpiozero,
so ignition.py's module-level DigitalOutputDevice()/Button() construction
(which runs at import time) never touches real hardware. Works on any OS --
this is why tests/ can run off a Pi.
"""

import os
import sys

os.environ.setdefault("GPIOZERO_PIN_FACTORY", "mock")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

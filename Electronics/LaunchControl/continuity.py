"""Igniter continuity-check reading.

Split out from ignition.py so the "digital OK/not-OK signal" assumption
documented in config.py has one clear place to change if the real firing
circuit turns out to expose an analog voltage instead (swap the Button
below for an ADC read, e.g. MCP3008 over spidev, and keep continuity_ok()'s
signature the same).
"""

from gpiozero import Button

import config

# pull_up=None + active_state=True: the line is externally driven (no Pi
# internal pull resistor engaged), HIGH == continuity OK. Confirm this
# polarity against the real firing-circuit schematic once it exists -- see
# config.CONTINUITY_PIN.
_continuity_sense = Button(
    config.CONTINUITY_PIN,
    pull_up=None,
    active_state=True,
    bounce_time=config.GPIO_DEBOUNCE_S,
)


def continuity_ok() -> bool:
    """True when the firing circuit's own low-current continuity check
    confirms the igniter loop is intact. See config.CONTINUITY_PIN for the
    digital-signal assumption this relies on."""
    return _continuity_sense.is_active

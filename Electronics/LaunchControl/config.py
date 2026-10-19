"""Central pin map and tunables for the RSP4 launch control station.

Mirrors the structure of ../firmware/src/config.h so the two ground-truth
files read the same way. Pin numbers below are BCM GPIO numbers (gpiozero's
convention), not physical header pin numbers.
"""

import os

# ---------------------------------------------------------------------------
# GPIO pins -- NOT YET CONFIRMED against the real firing-circuit schematic.
# The firing circuit itself (arm switch in the igniter's high-current path,
# firing relay/MOSFET, continuity-check circuit) is designed elsewhere; the
# three signals below are this software's electrical CONTRACT with that
# circuit. Confirm actual BCM numbers once the schematic exists, and update
# here -- nothing else in this codebase should hardcode a pin number.
# ---------------------------------------------------------------------------

# Fire-output line -- drives the firing relay/MOSFET gate. Active-high.
# MUST have an external pulldown independent of the Pi (see ignition.py):
# unlike a microcontroller, a Pi's GPIOs float for many seconds during boot
# before any userspace process (this one included) takes control of them.
FIRE_PIN = 17

# Arm-sense input -- reads the physical arm switch position. This is
# advisory/UI-only: the switch itself lives in the igniter's high-current
# path in hardware, so the igniter physically cannot fire with the switch
# open regardless of what this line (or a software bug) reads. Debounced.
ARM_SENSE_PIN = 27

# Continuity-check input -- HIGH means the firing circuit's own low-current
# continuity check confirms the igniter loop is intact, at a check current
# the firing circuit guarantees is below the igniter's no-fire threshold.
# ASSUMES the firing circuit exposes this as a simple digital OK/not-OK
# signal (via an external comparator). If it instead exposes a raw analog
# voltage, this needs an ADC (e.g. MCP3008 over spidev) instead of a plain
# gpiozero input -- confirm against the real circuit before relying on this.
CONTINUITY_PIN = 22

GPIO_DEBOUNCE_S = 0.05  # 50ms contact-bounce filter

# ---------------------------------------------------------------------------
# Ignition timing -- STARTING DEFAULTS, not verified specs. The igniter's
# resistance/current spec and the firing circuit's actual on-time
# requirement don't exist anywhere in this repo yet -- bench-verify against
# a dummy load (never a live igniter) before trusting these, same caveat
# config.h attaches to DEPLOY_ON_TIME_MS.
# ---------------------------------------------------------------------------

ARM_WINDOW_S = 15.0        # window after a successful /arm in which /fire is accepted
FIRE_ON_TIME_S = 2.0       # STARTING DEFAULT -- no empirical spec exists yet
FIRE_MAX_ON_TIME_S = 5.0   # hard safety ceiling, independent timer, fires regardless
assert FIRE_MAX_ON_TIME_S > FIRE_ON_TIME_S + 1.0, (
    "FIRE_MAX_ON_TIME_S must exceed FIRE_ON_TIME_S with real margin"
)

# One-shot fired-latch persistence -- survives a systemd restart of this
# service; only cleared by an explicit operator action
# (scripts/clear_fired_latch.py), never by anything the webapp can reach.
FIRED_LATCH_PATH = os.environ.get(
    "LAUNCHCONTROL_LATCH_PATH",
    os.path.join(os.path.dirname(__file__), "state", "fired.latch"),
)

# ---------------------------------------------------------------------------
# Flight-computer WiFi client -- talks to ../firmware/src/wireless.cpp's AP.
# IP/port match wireless.cpp's WiFi.softAPConfig()/WIFI_AP_HTTP_PORT.
# SSID/password must match the specific board's WIFI_AP_SSID/WIFI_AP_PASSWORD
# in firmware/src/config.h -- placeholders below, fill in per board.
# ---------------------------------------------------------------------------

FC_BASE_URL = os.environ.get("LAUNCHCONTROL_FC_URL", "http://192.168.4.1")
FC_STATUS_POLL_INTERVAL_S = 2.0
FC_HTTP_TIMEOUT_S = 3.0
# handleArm() on the ESP32 blocks ~4-5.5s (pad-baseline recapture +
# velocity-estimator reset) before responding, then deliberately drops the
# AP ~500ms later (WIFI_ARM_SHUTDOWN_GRACE_MS) -- give real margin over both.
FC_ARM_HTTP_TIMEOUT_S = 12.0

# ---------------------------------------------------------------------------
# Web server
# ---------------------------------------------------------------------------

WEB_HOST = "0.0.0.0"
WEB_PORT = 8080

# ---------------------------------------------------------------------------
# Pi's own hotspot (phone-facing AP) -- placeholders, change before field use.
# Channel is fixed at 6 to match firmware/src/config.h's WIFI_AP_CHANNEL:
# the Pi's onboard radio runs both the hotspot (wlan0_ap) and the station
# link to the flight computer's AP (wlan0) concurrently on ONE physical
# radio, which (per `iw phy0 info`'s interface-combination rules on the Pi
# 4's brcmfmac chipset) requires both to share a channel. See
# network/hostapd.conf and README.md.
# ---------------------------------------------------------------------------

AP_SSID = "LAUNCHCONTROL-XXXX"     # STARTING DEFAULT -- set unique before flying near other boards
AP_PASSWORD = "changeme-launchcontrol"  # STARTING DEFAULT -- WPA2, change before field use
AP_CHANNEL = 6                     # fixed -- must match firmware's WIFI_AP_CHANNEL for AP+STA concurrency

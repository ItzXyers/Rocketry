# RSP4 Launch Control

Last updated: 2026-08-08

A Raspberry Pi 4 ground station, physically separate from the vehicle. Two
independent jobs, kept independent on purpose:

1. **Fires the SRB igniters** through its own GPIO + an externally-designed
   firing circuit that has a physical arm switch wired into the igniter's
   high-current path itself -- so the igniter cannot fire just because this
   software has a bug, regardless of what any GPIO reads.
2. **WiFi-client to the flight computer's own ground-support AP**
   (`../firmware/src/wireless.cpp`) -- pad status, and its wireless `/arm`
   (which only re-zeros the altimeter and never touches the flight
   computer's own deployment channel).

Both are exposed through one webapp, served over this Pi's own WiFi hotspot
for a phone to connect to.

**This does not touch, replace, or relax `../firmware/src/deployment.*`'s
"wireless FIRE does not exist" rule for the CO2/parachute channel.** That
channel remains USB-serial-bench-only, unrelated to this system.

## Hardware contract

The firing circuit itself (arm switch, firing relay/MOSFET, continuity-check
circuit, igniter power supply) is designed elsewhere. This software expects
three signals from it -- see `config.py` for the current (unconfirmed) BCM
pin numbers and polarity assumptions:

| Signal | Direction | Contract |
|---|---|---|
| Fire output | Pi -> circuit | Active-high. **Needs an external pulldown independent of the Pi** -- a Pi has many seconds of boot before any userspace process (this one included) takes control of the pin. |
| Arm-sense | circuit -> Pi | Digital, HIGH = physical arm switch closed. Advisory/UI only -- the switch itself lives in the igniter's current path in hardware, not just as a GPIO read. |
| Continuity-sense | circuit -> Pi | Digital, HIGH = igniter loop intact, checked at a current the firing circuit guarantees is below the igniter's no-fire threshold. **Assumes a digital OK/not-OK signal** (e.g. from a comparator) -- if the real circuit instead exposes a raw analog voltage, swap `continuity.py`'s `Button` for an ADC read (e.g. MCP3008 over spidev) and keep `continuity_ok()`'s signature the same. |

Confirm actual pin numbers, polarity, and the continuity check's current
level against the real schematic once it exists, and update `config.py` --
nothing else in this codebase should hardcode a pin number.

## Radio topology

The Pi 4's single onboard radio runs both the phone-facing hotspot
(`wlan0_ap`) and the station link to the flight computer's AP (`wlan0`)
concurrently, on the **same channel (6)**, matching
`firmware/src/config.h`'s fixed `WIFI_AP_CHANNEL`.

**Before relying on this, verify on the actual Pi:**

```
iw phy0 info | grep -A 12 "valid interface combinations"
```

Confirms `{AP, managed}` is a legal simultaneous combination on this
kernel/driver, and shows the channel constraint (expect `#channels <= 1`,
i.e. same-channel required -- why both are hardcoded to channel 6). If this
comes back unsupported, the fallback is a $10 USB WiFi dongle as a second,
independent radio (`wlan1` for the station link) instead of trying to force
concurrency on one radio.

Raspberry Pi OS Bookworm manages WiFi via NetworkManager by default, which
doesn't cleanly drive this same-radio AP+STA setup -- this uses the classic
`hostapd` + `wpa_supplicant` + `dnsmasq` stack instead.

## Install (on the Pi)

```sh
sudo apt update
sudo apt install python3-venv python3-lgpio hostapd dnsmasq iw wpasupplicant
sudo systemctl unmask hostapd
sudo nmcli device set wlan0 managed no   # stop NetworkManager fighting hostapd/wpa_supplicant for wlan0

# Dedicated service user -- launchcontrol.service runs as this, not root.
sudo useradd --system --no-create-home --shell /usr/sbin/nologin launchcontrol
sudo usermod -aG gpio launchcontrol

sudo mkdir -p /opt/launchcontrol
sudo cp -r . /opt/launchcontrol
sudo chmod +x /opt/launchcontrol/scripts/setup_wlan0_ap.sh
cd /opt/launchcontrol
python3 -m venv venv
venv/bin/pip install -r requirements.txt

sudo cp network/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp network/dnsmasq-wlan0_ap.conf /etc/dnsmasq.d/wlan0_ap.conf
sudo cp network/wpa_supplicant-wlan0.conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
# Edit all three: real SSIDs/passwords (config.py's AP_SSID/AP_PASSWORD and
# the flight computer's actual WIFI_AP_SSID/WIFI_AP_PASSWORD), and set
# wpa_supplicant-wlan0.conf's country= to your regulatory domain.

sudo cp systemd/wlan0-ap-iface.service systemd/launchcontrol.service /etc/systemd/system/
sudo systemctl daemon-reload
# wpa_supplicant@wlan0 is Debian/Raspberry Pi OS's stock template unit --
# it reads /etc/wpa_supplicant/wpa_supplicant-wlan0.conf by the instance
# name alone, no unit file of ours needed for it.
sudo systemctl enable --now wlan0-ap-iface.service hostapd.service wpa_supplicant@wlan0.service launchcontrol.service
```

`launchcontrol.service` declares `StateDirectory=launchcontrol`, so systemd
creates `/var/lib/launchcontrol` (owned by the `launchcontrol` user) itself
before the service starts -- nothing to create by hand for the fired-latch
path.

**If the hotspot drops the instant `wlan0` associates to the flight
computer's AP** on some `brcmfmac` firmware/driver combinations, try
starting `wpa_supplicant@wlan0` *before* `hostapd` (reverse the order above)
-- that's a more common culprit than the channel setting once both are
confirmed to be on channel 6.

## Bench testing (no Pi required)

```sh
pip install -r requirements.txt
GPIOZERO_PIN_FACTORY=mock pytest tests/
```

Runs `ignition.py`'s full arm/fire/cutoff/latch state machine against
`gpiozero`'s mock pin factory -- no GPIO hardware, no real igniter.
`app.py` also runs standalone this way (`GPIOZERO_PIN_FACTORY=mock python
app.py`) for exercising the webapp against mocked inputs.

**Before ever firing a real igniter:** bench-test `ignition.py` against a
dummy load (LED + resistor standing in for the relay coil), confirm the
hard-cutoff timing with a scope/multimeter, and change every placeholder
password in `config.py` / `network/*.conf` from its default.

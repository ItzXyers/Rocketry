# Electronics — Consolidated Bill of Materials

Last updated: 2026-09-30

One list for every electrical part in the project: the flight computer, both
recovery-deployment variants, and the RSP4 LaunchControl ground station.
Per-part datasheets, sourcing links, and the power budget for the flight
computer core stay in [`Avionics/avionics_bom.md`](Avionics/avionics_bom.md)
— this doc references that numbering (**AV-n**) instead of repeating it, and
adds everything that until now only lived in the wiring doc, build
checklists, or `config.h` comments.

**Status legend**

| Status | Meaning |
|---|---|
| **Specified** | Part number chosen and documented in an existing doc; buy as listed. |
| **Candidate** | Proposed here (or only named generically elsewhere) — sensible default, not yet bench-verified in this project. |
| **TBD** | Blocked on a measurement or a design that doesn't exist yet. Don't buy until it's resolved. |

**Build configurations**

| Config | Vehicle | Deployment | Sections to buy |
|---|---|---|---|
| **A — CO2 / burn-wire** | `SampleRocketABS33-36` (30 mm bay, `integrated_ring_av_co2_bay_30mm`) | Nichrome coil cuts a Dyneema line, releasing the CO2 striker | §1 + §3 |
| **B — Servo** | `PhoenixABS40-43` (40 mm e-bay) | SG90 servo drives the dead-centre cam latch (`PhoenixABS40-43/DESIGN.md §7`) | §1 + §4 |
| **Ground** | LaunchControl (Raspberry Pi 4) | Fires the motor igniter; Wi-Fi client to the flight computer | §5 (+ §6 for bench work) |

Quantities are **per vehicle** (or per ground station). Buy spares of anything marked *(+spare)*.

---

## 1. Flight computer core — common to A and B

| Ref | Qty | Part | Key spec | Pkg / size | Mass | Status | Source / notes |
|---|---|---|---|---|---|---|---|
| U1 | 1 | Arduino Nano ESP32 (ABX00083) | ESP32-S3, 16 MB flash, 3.3 V I/O | 45 × 18 mm | ~5 g | Specified | AV-1. Trim header sockets for 5 mm stack height (Phoenix packing). |
| U2 | 1 | Pololu S7V8F5 buck-boost | 2.7–11.8 V in → 5 V out, 0.5–1 A | 17 × 11 × 3 mm | 1.2 g | Specified | AV-2. 5 V is 1 V under the Nano's 6 V VIN minimum — see open item O1. |
| BT1 | 1 | 1S LiPo, **Option B** EEMB LP852040 620 mAh | 1C cont., PCM, JST-RCY leads | 40.5 × 20 × 8.5 mm | 12.5 g | Specified | AV-3B. **Baseline for both vehicles** (fits Phoenix's 45 mm zone; the 30 mm bay pocket is sized to it). Option A (Electrokit 750 mAh, 48 × 30 × 5 mm) is the alternative. |
| — | 1 | JST-RCY → JST-PH adapter lead | 2-pin | — | <1 g | Candidate | Needed only with Option B — AV power note 4. |
| U3 | 1 | USB-C LiPo charger, BQ25302 module (Electrokit) | 0.2–2 A, power-path | ~23 × 16 mm | 2 g | Specified | AV-4. Set charge current to ~0.2–0.5C (125–310 mA for 620 mAh). |
| U4 | 1 | BMP388 barometer, Qwiic | I²C **0x76** on this board | ~25 × 18 mm | 2.5 g | Specified | AV-5. Firmware pins the address to 0x76 (`config.h`) — a 0x77 board will fail self-test by design. |
| U5 | 1 | ADXL375 ±200 g accelerometer (Adafruit 5374) | I²C, STEMMA QT | 25.4 × 17.8 mm | 2 g | Specified | AV-6 |
| U6 | 1 | microSD breakout, 3 V only (Adafruit 4682) | SPI, no level shifter | 20.3 × 15.2 mm | 1.5 g | Specified | AV-7. 3V3 rail only. |
| — | 1 *(+spare)* | microSD card 16 GB, **industrial grade** (Kingston) | −40…85 °C | — | 0.5 g | Specified | AV-8. Prefer the industrial SKU over consumer. |
| BZ1 | 1 | Active buzzer, 3–16 V miniature (Electrokit) | ~20–30 mA | ⌀12 × 9.5 mm | 1.5 g | Specified | AV-9. Needs a sound port in the airframe (integrated-bay open item). |
| Q1 | 1 | **BC337-40** NPN (Phoenix rev E; was 2N7000 N-MOSFET) | 45 V / 800 mA, h<sub>FE</sub> 250–630 | TO-92 (usually C–B–E, check datasheet) | 0.3 g | Specified | AV-10. Buzzer driver only — **not** for deployment. Saturates reliably from the 3.3 V pin, where a 2N7000 (V<sub>GS(th)</sub> up to 3 V) is marginal. |
| R1 | 1 | Resistor **1 kΩ**, ¼ W (was 220 Ω) | Q1 base resistor | axial | — | Specified | D9 → Q1 base, ~2.6 mA base drive. Not in stock yet; 330 Ω works as a stand-in. |
| R2 | 1 | Resistor 10 kΩ, ¼ W | Q1 gate pulldown | axial | — | Specified | Wiring doc 4. Keeps buzzer silent during boot. |
| C1 | 1 | Electrolytic 220 µF, ≥10 V, low-ESR (**Phoenix build: 470 µF 16 V from stock**, 2026-10-08) | 5 V bulk | ⌀8 × 12 mm radial (check the 470 µF can: ⌀10 won't fit sled v8) | 1.5 g | Specified | Wiring doc 2 / AV power note 3. **Mandatory before using the Wi-Fi ground interface near a loaded vehicle.** |
| SW1 | 1 | Magnetic reed switch, SPST-NO | glass capsule | 14 × ⌀2 mm | ~1 g | Specified (generic) | AV-13. Contactless power arming through the sealed wall. **Read open item O2 before wiring it in series with the battery.** |
| Q3 | 1 | P-MOSFET **high-side** load switch, **G75P04T** (Goford, Electrokit) | −40 V, −70 A, 7 mΩ at V<sub>GS</sub> = −10 V; V<sub>GS(th)</sub> ≤ −2.5 V, rated from −4.5 V | TO-220 (pins G–D–S, tab = drain) | ~2 g | Specified | **2026-10-11 (schematic rev E):** BATT+ → Q3 → SW_BATT → U2; R6 holds the gate at BATT+, the reed pulls it to GND. A 3.0–4.2 V cell drives it below its characterized gate voltage, so bench-check the S–D drop. Doesn't fit sled v8's SOT-23 slot; cut or insulate the drain tab. Wiring: `Avionics/avionics_bay_schematic_phoenix40.html`. |
| R6 | 1 | Resistor 100 kΩ | Q3 gate pull-up to source (BATT+) | axial | — | Candidate | Pairs with Q3. Always fitted; wire the KY-021 by S and − only, so its on-board 10 kΩ stays out of circuit (schematic item 3). |
| Q5 | 1 | N-MOSFET **2N7000** (on hand; was AO3400A) | 60 V, 200 mA — only ~40 µA needed here | TO-92 (S–G–D) | 0.3 g | Specified | **2026-10-15 (schematic rev F): power latch.** Drain to Q3 gate, source to GND, gate from D4 via R14. Firmware 0.3.0 drives D4 high at boot to hold power on after a magnet tap. |
| R13 | 1 | Resistor 100 kΩ | Q5 gate pulldown to GND | axial | — | Specified | Keeps Q5 off while the Nano is unpowered; with C5 holds Q5 on ~1 s through an ESP32 reset. |
| R14 | 1 | Resistor 220 Ω | D4 → Q5 gate series | axial | — | Specified | Limits D4's charging current into C5. |
| C5 | 1 | Electrolytic 10 µF, 50 V (on hand) | Q5 gate hold capacitor, + to gate | radial | — | Specified | ~0.5 s reset ride-through with R13 and a 2N7000 Q5 (~1 s with R13 = 200 kΩ). |
| CR1 | 1 | Schottky diode 1N5819 or BAT43 | SW1 → Q3 gate (cathode toward SW1) | DO-41 / DO-35 | — | To buy | Starts the bay on a magnet tap. Schottky so Q3 keeps gate drive on a low cell. |
| CR2 | 1 | Diode 1N4148 (or 1N5819 with R6 = 10 kΩ) | D5 → SW1 sense (cathode toward SW1) | DO-35 | — | To buy | Lets firmware see the magnet without back-powering D5 while the bay is off. |
| R11, R12 | 2 | Resistor 10 kΩ, 1 % | battery-sense divider, SW_BATT (after Q3) → A0 → GND | axial | — | Candidate | **New 2026-10-08.** Halves the cell voltage for the ADC (4.2 V → 2.1 V). 5 kΩ source, so no ADC filter cap is needed. ~0.2 mA while armed, nothing with Q3 off (tapped after Q3). |
| SW2 | 1 | Wireless-arm interlock, **momentary push button** (tactile, SPST-NO), inside the bay | 3.3 V logic level | ~6 × 6 mm tactile | ~0.5 g | Candidate | **2026-10-08:** momentary, latched in firmware 0.2.0 (hold 1–5 s and release to toggle). Was a slide/toggle. Wiring doc 8. 3V3 → SW2 → D7. Pressed with the e-bay out, before the bay is closed (2026-10-11 decision; no second reed). |
| R3 | 1 | Resistor 10 kΩ | D7 pulldown | axial | — | Specified | Wiring doc 8. External pulldown, **not** `INPUT_PULLUP` (fault-mode reasoning in the wiring doc). |
| — | 2 | Qwiic / STEMMA QT cable, JST-SH 4-pin, 50–100 mm | — | — | ~1 g | Specified | AV-12. Nano → BMP388 → ADXL375 daisy chain. |
| — | 1 lot | JST-PH 2-pin leads, 26–28 AWG silicone wire, heat-shrink, pin headers | — | — | 3–5 g | Specified | AV-12 |
| — | 1 | Arming magnet, neodymium ⌀10 × 5 mm (N42+) | — | — | ~3 g | Candidate | Ground tool for SW1 — **not** flown. Bench-check actuation distance through the actual wall. |
| — | 2 | O-rings, nitrile, ~2 mm CS | bay seals | — | <1 g ea. | Specified | AV-14. Sealing hardware, listed here only because the avionics BOM does. |

**Not bought:** u-blox NEO-6M/M8N GPS (AV-11) — superseded; D2/D3 stay reserved for it.

---

## 2. Firmware pin allocation (for reference while buying)

| Nano pin | Net | Used by | Config |
|---|---|---|---|
| A4 / A5 | I²C SDA / SCL | U4, U5 | A, B |
| D13 / D12 / D11 / D10 | SPI SCK / MISO / MOSI / CS | U6 | A, B |
| D9 | `PIN_BUZZER` | R1 → Q1 | A, B |
| D6 | `PIN_DEPLOY` | R4 → Q2 (burn-wire) | A |
| D7 | `PIN_ARM_INTERLOCK` | SW2 + R3 | A, B |
| A0 | `PIN_BATT_SENSE` | R11/R12 divider | Phoenix (firmware 0.2.0) |
| D4 | `PIN_POWER_HOLD` | R14 → Q5 (power latch) | Phoenix (firmware 0.3.0) |
| D5 | `PIN_POWER_SENSE` | CR2 → SW1 (magnet sense) | Phoenix (firmware 0.3.0) |
| D2 / D3 | Serial1 (reserved) | future GPS | — |

---

## 3. Config A — CO2 burn-wire deployment channel

Everything here is gated by `co2_assembly_checklist.md` §1 and
`avionics_build_checklist.md` §0/§5: **no coil current spec exists yet**, so
Q2's final rating and the nichrome gauge/length are set by a bench measurement
against a dummy load, not by this table.

| Ref | Qty | Part | Key spec | Pkg | Mass | Status | Notes |
|---|---|---|---|---|---|---|---|
| Q2 | 1 | Logic-level N-MOSFET, **AO3400A** | 30 V, 5.7 A, R<sub>DS(on)</sub> ≤ 48 mΩ at V<sub>GS</sub> = 2.5 V | SOT-23 (+ adapter) | <0.5 g | Candidate | Fully on at the ESP32's 3.3 V gate drive — the 2N7000 is not (200 mA max). Through-hole alternate: **IRLB8721PbF** (TO-220, ~2 g). Confirm against the measured coil current. |
| R4 | 1 | Resistor 100–220 Ω | Q2 gate series | axial | — | Specified (pattern) | Same pattern as R1 (`config.h` `PIN_DEPLOY` comment). |
| R5 | 1 | Resistor 10 kΩ | Q2 gate pulldown | axial | — | Specified (pattern) | Holds the channel off through ESP32 boot/reset. |
| C2 | 1 | Electrolytic 470 µF, ≥10 V, low-ESR | local reservoir at Q2 drain supply | ⌀8 × 12 mm | ~2 g | Candidate | Softens the coil inrush seen by the battery PCM. Optional once O3 is bench-checked. |
| E1 | 1 *(+spares)* | Nichrome 80 wire, 32–36 AWG | resistance set by length | — | <0.1 g | TBD | Gauge and length are chosen together so the coil current stays within the battery's pulse capability (O3). Serviced every flight. |
| — | 1 *(+spare)* | 2-pin micro connector for the coil leads, e.g. JST-PH or JST-SH | ≥2 A contact rating | — | <0.5 g | Candidate | Pad checklist §4 connects the coil **last**, on the rail — the connector has to be reachable at that point. |
| — | 2 | Coil feedthroughs potted in `AvBay_FwdCollar` (⌀2 mm) | — | — | — | Specified (mech.) | `SampleRocketABS33-36/BOM.md` item 10. Wire gauge must pass the ⌀2 mm hole. |

**Power path:** take the coil supply from the **battery side of Q3** (switched
BATT+), not from U2's 5 V output. A 1–3 A coil pulse on the regulator's 5 V rail
would exceed U2's rating and brown out the Nano mid-deploy.

---

## 4. Config B — servo deployment (Phoenix 40-43)

| Ref | Qty | Part | Key spec | Pkg | Mass | Status | Notes |
|---|---|---|---|---|---|---|---|
| M1 | 1 | SG90 micro servo (TowerPro or equivalent 9 g) | 4.8–6 V, ≥1.5 kg·cm, stall ~650 mA | 23 × 12.4 × 22.7 mm | 9 g | Specified | `DESIGN.md §7` / packing doc item 16. Trim the tabs to 23 mm axial. Metal-gear MG90S is a drop-in if the latch proof test (§7.9 test 3) shows gear wear. |
| C3 | 1 | Electrolytic 470 µF, ≥10 V, low-ESR | servo supply reservoir | ⌀8 × 12 mm | ~2 g | Candidate | At the servo connector — stall current plus a Wi-Fi burst on the same 5 V rail is the brownout case (O4). |
| R7 | 1 | Resistor 220 Ω | servo signal series | axial | — | Candidate | Protects the ESP32 pin if the servo lead is miswired or back-drives. |
| — | 1 | 3-pin servo extension (JR/Futaba), ~100 mm | — | — | ~1 g | Candidate | Service loop across the cassette's bench-service joint (`DESIGN.md` §8). |

No Q2, coil, or C2 in this config — the packing doc explicitly excludes them.

---

## 5. Ground station — LaunchControl (RSP4)

The Pi software is written; **the firing circuit has no schematic yet**
(`LaunchControl/README.md` "Hardware contract", pad checklist §0). Everything
below the Pi is a candidate reference design that meets that contract. Pin
numbers are BCM and still unconfirmed in `config.py`.

### 5a. Compute and radio

| Ref | Qty | Part | Key spec | Status | Notes |
|---|---|---|---|---|---|
| G1 | 1 | Raspberry Pi 4 Model B, 2 GB+ | onboard Wi-Fi (brcmfmac), AP+STA on ch 6 | Specified | README. |
| — | 1 | microSD 16–32 GB, A1/A2 class | Pi OS Bookworm | Candidate | |
| — | 1 | 5 V / 3 A USB-C supply **or** a USB-C power bank that holds 3 A | field power | Candidate | Pi 4 under-voltages on weaker banks — check `vcgencmd get_throttled` on the actual one. |
| — | 0–1 | USB Wi-Fi dongle (2.4 GHz, Linux-supported chipset) | second radio | Conditional | Only if `iw phy0 info` shows `{AP, managed}` is unsupported on your Pi/kernel (README "Radio topology"). |
| — | 1 | Enclosure, weather-resistant | — | Candidate | The Pi sits **at the pad** with the firing circuit; the phone is the remote. |

### 5b. Igniter firing circuit — reference design

| Ref | Qty | Part | Key spec | Status | Notes |
|---|---|---|---|---|---|
| BT2 | 1 | Igniter battery: 12 V SLA 7 Ah, or 3S LiPo with a fuse | ≥ 3 A pulse | TBD | Sized to the igniter's all-fire current, which isn't recorded anywhere in the repo yet. |
| F1 | 1 | Inline blade fuse holder + 5–7.5 A fuse | — | Candidate | On BT2+, first thing after the battery. |
| SW3 | 1 | **Keyed** arm switch (removable key), ≥10 A | in the igniter's high-current path | Candidate | This is the hardware interlock the README relies on. Key stays with the range operator. |
| Q4 | 1 | Logic-level N-MOSFET, IRLB8721PbF | 30 V, 62 A, fully enhanced by 3.3 V + margin | Candidate | Fire switch. A 3.3 V-input opto-isolated relay module also meets the contract. |
| R8 | 1 | Resistor 100 Ω | Q4 gate series from GPIO17 | Candidate | |
| R9 | 1 | Resistor 10 kΩ | **Q4 gate pulldown, external to the Pi** | Candidate — **required** | README: the Pi's GPIOs float for seconds during boot. Don't omit. |
| D1 | 1 | 1N5819 / 1N4007 | flyback, **only if a relay coil is used** | Conditional | Not needed with the MOSFET-only topology. |
| U7 | 1 | PC817 optocoupler + 1.5–2.2 kΩ LED resistor | arm-sense, 12 V side → GPIO27 | Candidate | Isolates 12 V from the Pi's 3.3 V GPIO. Transistor output: collector to 3V3, emitter to GPIO27 + 10 kΩ pulldown → HIGH = armed. |
| U8 | 1 | LM393 comparator (+ resistor network) | continuity OK/not-OK → GPIO22 | Candidate | Open-collector output, 10 kΩ pull-up to **3V3** (not 12 V). README allows swapping for an MCP3008 ADC if an analog reading is preferred. |
| R10 | 1 | Continuity current-limit resistor, ~2.2 kΩ at 12 V | test current ≈ 5 mA | Candidate | Keep the check current well below the igniter's published no-fire current — **confirm against the actual igniter datasheet**. |
| — | 1 | Firing leads: 2-core 18 AWG, ~1–2 m, with alligator clips | — | Candidate | Short — the Pi is at the pad. |
| — | 1 | Piezo buzzer or LED on the switched side of SW3 | "armed" indicator at the box | Candidate | Optional, standard range practice. |

---

## 6. Bench and test support (one set, not per vehicle)

| Qty | Item | Used for |
|---|---|---|
| 1 | Digital multimeter with a 10 A range | Coil current measurement (build checklist §5), continuity checks |
| 2 | Power resistors, 1 Ω and 2.2 Ω, 10 W | Dummy coil load before a real nichrome coil ever touches Q2 |
| 1 | LED + 1 kΩ resistor | LaunchControl dummy load for `ignition.py` bench tests (README) |
| 1 | Current-limited bench supply | Bring-up — note the checklist warning that C1 must be verified on a *representative* supply, not only the bench one |
| — | Spare nichrome, Dyneema line, fuses, heat-shrink | Per-flight consumables (`co2_assembly_checklist.md` §3) |

---

## Open items raised by this BOM

- **O1 — Nano VIN margin** (carried over from AV power note 1). U2's fixed 5 V is under the 6 V VIN spec. Fix: Pololu adjustable buck-boost (S9V11MA, 2.5–9 V out) set to ~6.5 V — but then the servo in Config B needs its own 5–6 V feed and can't share that rail.
- **O2 — Reed switch current rating (new).** Typical glass reed switches are rated ~0.5 A switching / ~1 A carry. The load path already peaks at 500–700 mA (AV power notes), and in Config A a coil fed through the same switch adds 1–3 A. Putting SW1 directly in series with the battery risks welding or pitting the contacts. **Recommended:** SW1 switches only Q3's gate (Q3 + R6 in §1), so the reed carries microamps. SW1's charge-isolation placement from the wiring doc (after the charger junction) is unchanged.
- **O3 — Coil current vs. battery (new).** BT1 Option B is rated 1C = 620 mA continuous with no published pulse rating. A nichrome coil drawing 1–3 A for `DEPLOY_ON_TIME_MS` (1.5 s) is outside that rating, and within reach of the estimated 2.5–3.5 A PCM trip. Pick nichrome gauge and length for the **lowest current that reliably cuts the line** on the bench, fit C2, and confirm that the voltage at U2's input stays above 2.7 V during the pulse.
- **O4 — Servo on the 5 V rail (new).** SG90 stall (~650 mA) plus a Wi-Fi TX burst can exceed U2's output while boosting from a 3.7 V cell. C3 helps; bench-verify by stalling the servo with the AP up.
- **O5 — Servo pin not assigned.** Add a `PIN_SERVO` to `config.h` (D4 or D5 — both are listed as free backups there). Phoenix has no Q2, so D6 is also free on that build.
- **O6 — Firing circuit schematic.** §5b is a reference proposal. Draw the actual schematic and then update `LaunchControl/config.py` pins and polarity. Pad checklist §0 stays a dry rehearsal until that's done.

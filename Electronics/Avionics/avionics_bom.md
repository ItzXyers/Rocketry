# Flight Computer Avionics — Bill of Materials

Last updated: 2026-08-08

**2026-08-19 addition:** this avionics set is now built into a real, sealed
airframe bay (`SampleRocketABS33-36/Design-Notes-AvBayIntegration.md`). The
bay has no wall cutouts at all except 4 barometer static ports and 2 M3
screw holes — arming has to be contactless, so a magnetic reed switch
(item 13 below) replaces the power switch called for in item 2 of the
Power notes below. Items 13–14 are new.

**2026-10-19:** the reed switch (item 13), the microSD reader and card
(items 7–8), and the SW2 Wi-Fi button were all dropped from the built
harness. The bay powers up when the battery is plugged in, and the log is
written to the Nano's internal flash (~9.4 MB FFat partition, firmware
0.2.1+). See `avionics_bay_schematic_phoenix40.html`.

## Summary table

| # | Component | Purpose / key spec | Dimensions | Weight | Interface | Source |
|---|---|---|---|---|---|---|
| 1 | Arduino Nano ESP32 (ABX00083) | Flight computer, ESP32-S3, 16 MB flash | 18 × 45 mm | ~4 g | — | Arduino |
| 2 | Pololu S7V8F5 regulator | Buck-boost 2.7–11.8 V → 5 V, feeds VIN | 11 × 17 × 3 mm | ~1.2 g | power | Pololu / Electrokit |
| 3 | LiPo battery, 1S | See [Battery](#3-battery) — two options evaluated | see below | 12.5–14.8 g | power | Electrokit / EEMB |
| 4 | USB-C LiPo charger (BQ25302) | Ground charging, 0.2–2 A adjustable, power-path | small | ~2 g | — | Electrokit |
| 5 | BMP388 barometer — Qwiic | Altitude/pressure, ~0.5 m res | small breakout | ~2.5 g | I²C | Electrokit |
| 6 | ADXL375 ±200 g accelerometer | High-g boost/shock capture | ~25 × 18 mm | ~2 g | I²C/SPI | Adafruit |
| 7 | ~~MicroSD reader, 3V only (Adafruit 4682)~~ **dropped 2026-10-19** | Logging moved to the Nano's internal flash | — | — | — | — |
| 8 | ~~microSD card, 16 GB~~ **dropped 2026-10-19** | Not needed without item 7 | — | — | — | — |
| 9 | Active buzzer | Recovery beacon, driven via MOSFET | ~12 mm ⌀ | ~1.5 g | GPIO (via Q1) | Electrokit |
| 10 | Logic-level MOSFET, 2N7000 | Switches buzzer off 3.3 V GPIO | TO-92 | ~0.3 g | — | Electrokit |
| 11 | u-blox NEO-6M / NEO-M8N GPS — **optional (superseded)** | Recovery locator, drops out >~Mach 1.5 | ~25 × 35 mm + antenna | ~9 g | UART | generic |
| 12 | Qwiic cable + JST leads, headers, wire | Interconnect | — | ~3–8 g | — | Electrokit |
| 13 | ~~Magnetic reed switch + external magnet~~ **dropped 2026-10-19** | Power on/off is now plugging/unplugging the battery | — | — | — | — |
| 14 | O-rings, 2× | Seals `AvBay_AftBulkhead` and `AvBay_FwdCollar` to the tube ID | ~2mm cross-section, ID to match each part's groove (⌀27.6–28.8 aft, groove TBD-matched fwd) | <1 g ea. | — | nitrile, generic hardware/hobby source |

---

## Component details

### 1. Arduino Nano ESP32 (ABX00083)
- Store: https://store.arduino.cc/products/nano-esp32-with-headers
- Datasheet: https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf
- Cheat sheet: https://docs.arduino.cc/tutorials/nano-esp32/cheat-sheet/
- VIN spec: **6–21 V** officially. VBUS (5 V) is USB-only and is disabled as an input path when powered via VIN — it cannot be used as an alternate 5 V input.
- Current draw: ~30–80 mA typical (WiFi/BT idle), transient bursts of 300–500 mA during WiFi TX (ms-scale).
- GPIO: 40 mA source / 28 mA sink max.

### 2. Pololu S7V8F5 buck-boost regulator
- Product page: https://www.pololu.com/product/2123
- Input 2.7–11.8 V → fixed 5 V out, >90% typical efficiency.
- Rated for 500 mA–1 A continuous output depending on Vin — comfortable margin over this design's ~150 mA average draw.
- **Caveat:** feeding its fixed 5 V output into the Nano's VIN pin is 1 V under Arduino's stated 6 V minimum. Works in practice (onboard MP2322 buck tolerates it per community testing) but with no margin — see [Power notes](#power-notes).

### 3. Battery
Two options were evaluated for this slot; specs collected for both.

**Option A — Electrokit 750 mAh 1S LiPo, JST-PH**
- https://www.electrokit.com/en/batteri-lipo-3.7v-750mah
- 3.7 V nominal, 4.2 V max charge, 3.0 V cutoff, 2C (1.5 A) max discharge, built-in PCM.
- 48 × 30 × 5 mm, 14.8 g.

**Option B — EEMB LP852040, 620 mAh, re-terminated with JST-RCY/BEC**
- Identified from user-supplied specs (40.5×20×8.5 mm, 12.5 g, 620 mAh match the LP852040 cell-size code exactly).
- Generic listings: https://eemb.store/products/lp852040-3-7v-700-mah · https://www.master-instruments.com.au/products/65516/LP852040.html · https://www.amazon.com/EEMB-Battery-Lithium-Rechargeable-Connector/dp/B095VVWTSH
- 3.7 V nominal, 4.2 V max charge, 3.0 V cutoff, 1C (620 mA) max continuous discharge, AWG24 leads, PCM (over-charge/discharge/current/short-circuit/temp).
- **Connector mismatch:** ships with JST-RCY (SYP-02T-1, 2.54 mm BEC-style), not JST-PH like the regulator/charger boards expect. Needs an adapter lead or re-termination.
- No published burst/pulse discharge rating for this SKU (checked EEMB's own site and major distributors — none list one). Reasoned from standard small 1S protection-IC practice (DW01A + 8205A-class, typical ~2.5–3.5 A trip) and typical ~100–200 mΩ ESR for this cell class: this design's worst-case transient (~500–700 mA) is well clear of both the protection cutoff and any meaningful voltage sag. Verdict: usable, no pulse-limit risk for this load profile — see [Power notes](#power-notes) for the full reasoning.

### 4. USB-C LiPo charger — BQ25302
- Electrokit: https://www.electrokit.com/en/lipo-laddare-2a-usb-c
- TI product page: https://www.ti.com/product/BQ25302 · Datasheet: https://www.ti.com/lit/ds/symlink/bq25302.pdf
- Standalone buck charger, adjustable 0.2–2 A charge current (resistor-set), 4.1–6.2 V input.
- **Has power-path management** — the Electrokit module explicitly supports running the load while charging simultaneously (this corrects an earlier assumption that charge/run needed to be mutually exclusive).
- Recommended charge current for the 620–750 mAh cells above: ~0.2C–0.5C (125–375 mA) for a safe ~1.5–2 h charge.

### 5. BMP388 barometer — Qwiic
- Electrokit: https://www.electrokit.com/en/temperature-and-air-pressure-sensor-bmp388-qwiic
- Bosch datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp388-ds001.pdf
- Current draw: ~3.4 µA @ 1 Hz normal mode — negligible in the power budget.

### 6. ADXL375 ±200 g accelerometer
- Adafruit: https://www.adafruit.com/product/5374
- Analog Devices datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL375.PDF
- Current draw: ~35–145 µA in measurement mode — negligible.
- STEMMA QT/Qwiic connector, also breaks out SPI.

### 7. MicroSD reader — Adafruit 4682 (dropped 2026-10-19, kept for reference)
- Adafruit: https://www.adafruit.com/product/4682
- Guide: https://cdn-learn.adafruit.com/downloads/pdf/adafruit-microsd-spi-sdio.pdf
- **3 V logic only, no level shifter** — do not drive from a 5 V bus.
- Current draw: 5–25 mA idle/read, 100–200 mA spikes on write/init. Biggest single contributor to transient current draw on the board — see bulk-cap recommendation in [Power notes](#power-notes).

### 8. microSD card, 16 GB (dropped 2026-10-19)
- Electrokit options: https://www.electrokit.com/en/minneskort-microsdhc-16gb (Verbatim) or https://www.electrokit.com/en/minneskort-microsdhc-16gb-industrial-grade (Kingston Industrial, wider temp range −40…85 °C — better suited to a rocket airframe than consumer-grade cards).

### 9. Active buzzer
- Electrokit: https://www.electrokit.com/en/summer-4-khz-miniatyr (3–16 VDC miniature) or https://www.electrokit.com/en/piezohogtalare-aktiv (3.3–5 V module)
- Current draw when driven: ~20–30 mA.

### 10. Logic-level MOSFET — 2N7000
- Electrokit: https://www.electrokit.com/en/product/2n7000-to-92-mosfet-n-ch-60v-200ma/
- Datasheet: https://www.mouser.com/datasheet/2/115/2n7000-1163778.pdf
- 60 V, 200 mA max — plenty for a 20–30 mA buzzer load; Rds(on) is higher at 3.3 V Vgs than at the datasheet's 10 V test condition, but irrelevant at this current.

### 11. GPS — u-blox NEO-6M / NEO-M8N — **optional (superseded)**
- NEO-6 datasheet: https://content.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_(GPS.G6-HW-09005).pdf
- NEO-M8 datasheet: https://content.u-blox.com/sites/default/files/NEO-M8-FW3_DataSheet_UBX-15031086.pdf
- Generic GY-NEO6MV2-style breakout, widely available (e.g. https://www.addicore.com/products/neo-6m-gps-module-with-eeprom) — not Electrokit-specific.
- Current draw: ~45 mA continuous acquisition, ~11 mA in power-save mode, ~67 mA peak.
- Recovery-locator use only — GPS loses lock well before typical motor burnout velocities.

### 12. Qwiic cable + JST leads / headers / wire
- Electrokit JST-SH (Qwiic) cable: https://electrokit.com/en/product/cable-with-jst-sh-1-0mm-4-pin-200mm
- Full JST connector range: https://www.electrokit.com/en/jst-connectors/

---

## Power notes

Chain: **LiPo → S7V8F5 (5 V) → Nano VIN → onboard buck (3.3 V) → everything else.**

| Load state | Current draw | Battery runtime (750 mAh) | Battery runtime (620 mAh) |
|---|---|---|---|
| Cruise, no GPS | ~50–100 mA | ~6–7 h | ~5.6 h |
| Cruise + GPS | ~95–145 mA | ~4–5 h | ~3.9 h |
| Worst-case transient (flash write + WiFi burst; was SD write + WiFi) | ~500–700 mA, ms-scale (estimate from the SD era, likely lower now) | — | — |

Both battery options comfortably clear the actual duty cycle. Both regulator (500 mA–1 A) and battery discharge ratings (1.5 A / 620 mA respectively) have adequate margin over the transient peak; see the per-battery pulse-rating discussion above for the 620 mAh option specifically.

**Open items / recommendations:**
1. **VIN margin:** S7V8F5's fixed 5 V is 1 V under the Nano's documented 6 V VIN minimum. Works per community reports, but consider swapping to an adjustable Pololu buck-boost set to ~6.5–7 V for proper margin.
2. **No power switch in the BOM.** **2026-10-19: resolved by dropping it** — the reed switch below was removed from the harness, and the bay is switched by plugging/unplugging the battery's JST lead. Unplug it for transport and storage (the R11/R12 divider draws ~0.2 mA whenever it's plugged in). Original note: needed to disconnect the battery for pad safety/arming and to isolate the system during ground charging. **2026-08-19:** the airframe bay this avionics set is now built into (`SampleRocketABS33-36/Design-Notes-AvBayIntegration.md`) has no cutout for a physical toggle switch — item 13 above (magnetic reed switch + external magnet) fills this role instead, actuated by holding a magnet against the outside of the sealed tube. Still doesn't address ground-charging isolation on its own; the charger's own power-path management (item 4) may be sufficient, but confirm before relying on it.
3. **Add a bulk cap** (100–220 µF low-ESR) at the S7V8F5's 5 V output to buffer flash-write and WiFi TX transients and avoid brownout resets. **This is no longer just a hypothetical worst case:** the wireless ground-interface feature (`../firmware/src/wireless.*`) brings the radio up at every boot (no SW2 since 2026-10-19), including a moment where a wireless-arm event-log flash write happens while the AP is still active. **C1 should be fitted (or the transient bench-verified on a representative supply, not a lab bench supply) before using the wireless interface anywhere near a loaded rocket or an installed CO2 cartridge.**
4. **Battery connector:** if going with the EEMB LP852040 (Option B), budget for a JST-RCY→JST-PH adapter lead or re-termination to mate with the regulator/charger boards.
5. **Wireless-arm interlock switch (SW2) and R3: dropped 2026-10-19.** Firmware 0.2.1+ brings the AP up at boot and still latches it off after `/arm` or confirmed launch. Original note: new for the wireless ground-interface feature (see `../firmware` — `wireless.*`, `PIN_ARM_INTERLOCK`). Separate from the power switch in item 2 above — SW2 gates whether the wireless AP/`/arm` action is available, not board power. Any SPST/SPDT toggle or slide switch rated for 3.3 V logic-level switching works; R3 = 10 kΩ (same family as R2). Not yet a verified SKU.

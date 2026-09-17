# Print Files — Avionics (serviceable cassette v1)

The four printed additions from the serviceable-cassette study
(`Avionics/avbay_cassette_build_report_v1.txt`, `Avionics/avionics_bay_packing_40mm.md` §9).
STLs are raw exports, in the **packing frame** (tube axis = Z, un-oriented).

```
Avionics/
  *.stl                              raw per-part model STLs, as exported (un-oriented)
```

| Part | g | Notes |
|---|---|---|
| `..._SvcAnchorCoupler_v1` | 21.2 | anchor bulkhead → 18 mm coupler; ⌀6.8 piston bore, ⌀11.5 spring seat, ⌀4 eyelet. Print axis is set by that bore. `DESIGN.md §13` item 15 redesign target (mass). |
| `..._SvcRetentionBand_v1` | 3.8 | ⚠️ **provisional** — see below. Local wall thickening, flush skin, 3× radial M3, wall 1.9 mm (flagged THIN). |
| `..._SvcAftClosure_v1` | 3.6 | r19.0 disc + ⌀8×3 spigot + one 3×2.5 key (sole rotational constraint). |
| `..._SvcBatteryTray_v1` | 1.4 | thin U-channel, open on the inboard face. 68 facets — that's correct. |

## Status — bench fit-check article, NOT flight parts

- **`[R]` retention load path is OPEN.** The band + M3 interface is sized against
  `RECOVERY_SNATCH_N = 250 N`, a **placeholder** (`RECOVERY_MEASURED = False`); every
  line in report `[R]` prints OPEN. Needs (a) spring `F_max` measured (`DESIGN.md §7.3`)
  and (b) a **packed-separation drop** (`§7.9` test 4). **If the measured snatch lands
  high, `SvcRetentionBand` is replaced by a 3-lug bayonet ring** (+~4 mm length) — a
  different part. Don't cut a flight band off this file.
- Printing this set is what **unblocks** that drop test. Good for: fit/clearance check,
  match-drilling the 3 screw holes at first build (`[K]`), verifying the `[E]` 0.20 mm
  sled-through-band clearance actually slides.
- Upstream component dims (charger, BMP388, buzzer, C1, SW1/SW2) are still **estimated**
  (`packing md` closing note) — replace with measured parts before a flight sled.

## ⚠️ Do not print — everything else in `Avionics/Models/`

Of the ~70 STLs there, only the four above are parts. **All** of these are envelopes /
reference geometry and will slice as bounding boxes:

- component bounding solids: `..._accel_`, `..._baro_`, `..._Battery_`, `..._Nano_ESP32_`,
  `..._Servo_SG90_`, `..._USB_Charger_`, `..._SmallParts_Allowance_`, `..._AftClosure_`,
  `..._FwdClosure_`, `..._TubeStub_`, `..._Sled_` (v1/v2 packing study)
- ejection-POC reference: `..._ref_Ejection*`, `..._ref_Knob*`, `..._ref_PistonShaft_*`,
  `..._ref_TubeStub_*`
- visualisation only: `..._cassette_ASSEMBLY_v1`, `..._cassette_ASSEMBLY_section_v1`,
  `cassette_assembly_v1/` (`Env_*`, `MotorBulkhead`)

## Not done yet

No `Ready to Print/` orientation pass. The two rings (`SvcRetentionBand`,
`SvcAnchorCoupler`) need laying flat; `SvcAnchorCoupler`'s print axis is a judgement
call given the ⌀6.8 bore + spring seat. No batch plate.

## Electronics sled — not here yet

The scaffold the boards mount to (`Models/PhoenixABS40-43_avbay_ElectronicsSled_v1`,
built by `Avionics/PhoenixABS40-43_avbay_sled_v1.py`, report `avbay_sled_build_report_v1.txt`)
is a **`Models/` design iteration, not a print file**. The v3 repack it sits on is
verified (real board dims, fits Z 48, zero clashes) but the fastener geometry is
placed on assumed hole patterns and does not clamp as drawn — needs the measured
mounting-hole coordinates for the Nano / BMP388 / ADXL / piezo before it comes here.

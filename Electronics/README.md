# Rocketry Electronics

Last updated: 2026-08-07

Design files for a rocket's flight computer avionics sled and CO2-based
recovery ejection module.

## Subsystems

### 1. Flight computer avionics
ESP32-based flight computer (Arduino Nano ESP32), barometer + high-g
accelerometer for flight data, microSD logging, GPS recovery locator, and a
buzzer beacon, on a 1S LiPo with USB-C charging.

- **Electrical BOM, sourcing, and power budget:** [`avionics_bom.md`](Avionics/avionics_bom.md)
- **Mechanical sled:** `avionics_sled.blend` models the component layout on a
  spine plate inside the airframe. Two airframe-diameter variants exist in
  the current working file:
  - 25 mm-class airframe — `spine_plate` (10.5 × 0.75 × 67.04 mm)
  - a second variant, named "30 mm" in the Blender collection
    (`Avionics_Sled_30mm`) but whose modeled reference airframe shell
    measures ⌀32 mm — `spine_plate30` (14.85 × 1.0 × 94.88 mm). Worth
    reconciling whether "30 mm" refers to a nominal tube size that differs
    from the modeled OD, before treating either as final.
  - `avionics_spine.stl` / `avionics_sled_reference_assembly.stl` are STL
    exports of this assembly.

### 2. CO2 deployment module
Ejection charge using an 8 g CO2 cartridge, punctured by a striker pin
released via what appears to be a burn-wire mechanism.

- **Design notes, part list, mechanism analysis, open items:** [`co2_deployment_module.md`](CO2%20Deployment/co2_deployment_module.md)
- CAD: `co2_deployment_module.blend`, `co2_cartridge_8g.scad` (parametric,
  datasheet-derived cartridge model), plus individual part STLs.

**Note on data provenance:** the dimensions in both docs above were captured
from a live, **unsaved** Blender session on 2026-08-04 that had both sleds
and the CO2 module open simultaneously in one scene. Save that session to
disk so the current state isn't lost, and re-verify against the `.blend`
files if this doc is read much later.

## File inventory

Files are grouped into subfolders by subsystem:

- `Avionics/` — flight computer sled
- `CO2 Deployment/` — CO2 ejection module and its trigger/release mechanism
- `Integrated Bay Assemblies/` — combined avionics + CO2 bay CAD (30 mm variants)
- `Unsorted/` — files whose status/ownership is unconfirmed (see below)

| File | Folder | Subsystem | Notes |
|---|---|---|---|
| `avionics_bom.md` | `Avionics/` | Avionics | Electrical BOM, sourcing links, power budget |
| `avionics_wiring.md` | `Avionics/` | Avionics | Wiring companion to the BOM |
| `avionics_build_checklist.md` | `Avionics/` | Avionics | Bench build & wiring verification checklist, pre-airframe |
| `avionics_sled.blend` | `Avionics/` | Avionics | Sled CAD, both airframe variants |
| `avionics_sled_reference_assembly.stl` | `Avionics/` | Avionics | Assembly export |
| `avionics_spine.stl` | `Avionics/` | Avionics | Spine plate export |
| `co2_deployment_module.md` | `CO2 Deployment/` | CO2 module | Design notes, part list, open items |
| `co2_assembly_checklist.md` | `CO2 Deployment/` | CO2 module | Design blockers + per-cycle reload/service checklist |
| `co2_deployment_module.blend` (+ `.bak`/`.blend1`) | `CO2 Deployment/` | CO2 module | Chamber/housing/striker CAD |
| `co2_deployment_module_reference_assembly.stl` | `CO2 Deployment/` | CO2 module | Assembly export |
| `co2_chamber.stl` | `CO2 Deployment/` | CO2 module | Chamber (base + body + neck) |
| `co2_striker_housing.stl` | `CO2 Deployment/` | CO2 module | Striker housing |
| `co2_striker_pin.stl` | `CO2 Deployment/` | CO2 module | Striker pin |
| `co2_retaining_collar.stl` | `CO2 Deployment/` | CO2 module | Retaining collar |
| `co2_cartridge_8g.scad` / `.stl` | `CO2 Deployment/` | CO2 module | Parametric cartridge model, from datasheet |
| `co2_cartridge_8g_preview.png` / `_tip_preview.png` | `CO2 Deployment/` | CO2 module | Render previews |
| `co2_trigger_release_mechanism.md` | `CO2 Deployment/` | CO2 module | Burn-wire trigger/release design notes |
| `co2_trigger_release_mechanism.blend` (+ `.blend1`) | `CO2 Deployment/` | CO2 module | Trigger/release mechanism CAD, split out of the integrated bay file |
| `combined_av_co2_bay_30mm.blend` / `_reference_assembly.stl` | `Integrated Bay Assemblies/` | Integrated | Combined avionics + CO2 bay, 30 mm variant |
| `integrated_av_co2_bay_30mm.blend` / `_reference_assembly.stl` | `Integrated Bay Assemblies/` | Integrated | Integrated avionics + CO2 bay, 30 mm variant |
| `integrated_ring_av_co2_bay_30mm.md` | `Integrated Bay Assemblies/` | Integrated | Design notes for the ring-mount integrated bay |
| `integrated_ring_av_co2_bay_30mm.blend` (+ `.bak`/`.blend1`) | `Integrated Bay Assemblies/` | Integrated | Ring-mount integrated bay CAD |
| `integrated_ring_av_co2_bay_30mm_reference_assembly.stl` | `Integrated Bay Assemblies/` | Integrated | Assembly export |
| `payload_bay_sled.stl` | `Unsorted/` | Unclear | Dated 2026-07-17, not present in the current working Blender scene — confirm if still current |
| `puncture_cap.stl` | `Unsorted/` | Unclear | Dated 2026-07-17, not present in the current working Blender scene — confirm if still current or superseded by the striker-pin design |

Note: the three "Integrated Bay Assemblies" variants (`combined_av_co2_bay_30mm`, `integrated_av_co2_bay_30mm`, `integrated_ring_av_co2_bay_30mm`) weren't previously distinguished in this doc — their exact relationship to each other (e.g. which supersedes which) isn't captured here and is worth confirming.

## Open items across the project

- No BOM yet exists for the CO2 module's hardware (cartridge source,
  burn-wire driver circuit) — only the avionics side has one so far.
  Striker pin and retaining-line materials are specified — pin revised
  2026-08-07 to a printed-plastic body with a hardened metal tip insert
  (sourced, not machined; see options in `co2_trigger_release_mechanism.md`),
  line is Dyneema/Spectra — and the drive spring plus the line's diameter
  (⌀0.30mm) are sized on paper too — see
  [`co2_trigger_release_mechanism.md`](CO2%20Deployment/co2_trigger_release_mechanism.md#drive-spring-and-final-line-sizing--decided-2026-08-07).
  All of it is provisional pending one measurement (actual cartridge
  puncture force — nothing in this project has tested it yet) and none of
  it is applied to the CAD yet (Blender wasn't reachable that session).
  That pass also surfaced two new items: the pin's tail geometry needs a
  guide-rod redesign to physically fit any spring, and cartridge
  backpressure after piercing (~628N at the housing↔collar joint in the
  worst case) was never accounted for anywhere — flagged safety-relevant
  in `integrated_ring_av_co2_bay_30mm.md`.
- Status of `payload_bay_sled.stl` and `puncture_cap.stl` relative to the
  current designs is unconfirmed (see table above).
- The two avionics airframe-diameter variants aren't reconciled with a
  final airframe choice yet.

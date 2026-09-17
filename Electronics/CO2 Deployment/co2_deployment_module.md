# CO2 Deployment Module — Design Notes

Last updated: 2026-08-04

## Overview

Recovery ejection module using an 8 g threadless CO2 cartridge (LE-8NT-style,
modeled parametrically in [`co2_cartridge_8g.scad`](co2_cartridge_8g.scad) from
manufacturer datasheet values). The cartridge sits in a three-piece pressure
chamber; a striker housing above it holds a striker pin that punctures the
cartridge's flat pierce tip to release gas for ejection.

**Provenance note:** the dimensions below were read directly from the live
Blender working session on 2026-08-04, which had `Avionics_Sled`,
`Avionics_Sled_30mm`, and `CO2_Deployment_Module` all open in one unsaved
scene (`bpy.data.filepath` was empty at capture time). They should match
`co2_deployment_module.blend` / the exported STLs closely but the session was
not saved at the time of writing — **save the Blender file** so this state
isn't lost.

## Part list

| Object (Blender) | Likely STL export | Envelope (mm) | Role |
|---|---|---|---|
| `co2mod_chamber_base` | `co2_chamber.stl` | ⌀20.5 × 2.0 | Bottom cap of the pressure chamber |
| `co2mod_chamber_body` | `co2_chamber.stl` | ⌀20.5 × 58.0 | Main chamber tube, houses the cartridge body |
| `co2mod_chamber_neck` | `co2_chamber.stl` | ⌀20.5 × 8.0 | Reduced section transitioning to the striker housing |
| `co2_cartridge_8g_REAL` | `co2_cartridge_8g.stl` | ⌀18.0 × 66.0 | Reference model of the actual cartridge (from datasheet, see .scad) |
| `co2mod_housing` | `co2_striker_housing.stl` | ⌀16.0 × 26.0 | Striker housing, mounts above the chamber neck |
| `co2mod_striker_pin` | `co2_striker_pin.stl` | ⌀9.0 × 31.0 | Pin driven down through the housing to puncture the cartridge tip |
| `co2mod_retaining_collar` | `co2_retaining_collar.stl` | ⌀12.4 × 2.0 | Cap/guide ring near the release mechanism — exact function unconfirmed |
| `co2mod_retaining_line` | not separately exported | ⌀0.8, 19 mm span | Line/thread strung horizontally between the two anchor posts |
| `co2mod_anchor_post_a/b` | not separately exported | 2 × 2 × 3 each | Posts anchoring the retaining line, 19 mm apart (center-to-center) |
| `co2mod_lead_pos` / `co2mod_lead_neg` | not separately exported | ⌀1.0 × 10 each | Electrical leads, rising from the anchor posts toward the striker pin |
| `co2mod_airframe_shell_REF` | reference only | ⌀25 × 94 | Visualization aid, not a real part |

`co2_chamber.stl` (one file on disk) most likely contains the base+body+neck
merged into a single print — worth confirming against the STL directly if
it matters for slicing/printing.

**Chamber vs. housing length check:** base (2) + body (58) + neck (8) = 68 mm
chamber, + 26 mm housing ≈ 94 mm, which matches the 94 mm reference airframe
segment (`co2mod_airframe_shell_REF`) modeled alongside it — consistent
cross-check, not just a coincidence.

## Release mechanism — confirmed vs. inferred

Geometry was checked explicitly (world-space bounding boxes, not just
`.location`) because part names alone were ambiguous:

- **Confirmed:** `co2mod_retaining_line` is rotated 90° about Y so its long
  axis runs horizontally along X from x=190.5 to x=209.5 — i.e. it is
  genuinely strung *between* `co2mod_anchor_post_a` (x=189–192) and
  `co2mod_anchor_post_b` (x=208–211), sitting inside the striker housing's
  Z-range. This is a real burn-wire/retention-line layout, not a modeling
  coincidence.
- **Confirmed:** `co2mod_lead_pos` and `co2mod_lead_neg` are separate thin
  vertical leads positioned at the same X as the anchor posts, rising from
  the line's height up toward the striker pin — consistent with electrical
  leads feeding a resistive element that would heat and sever the line
  (classic "burn wire" CO2 release, as used on several commercial rocketry
  deployment boards).
- **Not modeled — open item:** no spring, elastic, or other stored-energy
  object exists anywhere in the 33-object scene. Something has to drive the
  striker pin into the cartridge once the line is cut; that force source is
  not represented in the CAD yet. Don't assume "spring-loaded" until a part
  for it exists.
- **Superseded (2026-08-05):** a nichrome coil object now exists and the
  whole release mechanism (pin neck/shoulder catch, coil, leads, housing
  boss for the feedthrough) has been redesigned and split into its own
  file — see [`co2_trigger_release_mechanism.md`](co2_trigger_release_mechanism.md).
  That doc is now the source of truth for this mechanism.
- **Unconfirmed:** `co2mod_retaining_collar`'s exact function (spacer? line
  guide? pin stop?) — geometry alone doesn't say. Now known to matter more
  than "unconfirmed" suggested: it's modeled as a solid disc with no bore,
  which would block the pin outright — see the open items in
  `co2_trigger_release_mechanism.md`.

## Open items / recommendations

1. **Stored-energy source for the striker pin is unspecified.** Needs a
   decision (compression spring, rubber band, gas-pressure preload, etc.)
   and a corresponding CAD feature before this is buildable.
2. **Burn-wire firing circuit isn't designed yet.** Will need a driver
   (MOSFET, same pattern as the buzzer driver in [`avionics_bom.md`](../Avionics/avionics_bom.md#10-logic-level-mosfet--2n7000)),
   a GPIO from the flight computer, and a current/duration spec for
   reliably severing the retaining line without excess battery draw.
3. **Chamber wall thickness / cartridge fit not verified.** The 20.5 mm
   figures above are outer envelope dimensions only — the inner bore
   relative to the cartridge's 18 mm body has not been checked and should
   not be assumed from OD alone.
4. **Pressure sealing (O-rings/gaskets) isn't evidenced in the part list.**
   Worth confirming how the chamber seals against the ~8 MPa cartridge fill
   pressure at the base cap and neck joints.
5. **`puncture_cap.stl` and `payload_bay_sled.stl`** (both dated 2026-07-17,
   older than the rest of this module) are not present in the current
   working Blender scene — confirm whether they're still current or have
   been superseded by the striker-pin design above.

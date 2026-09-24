# Phoenix ABS 40-43: low-drag separating nose (v5)

Source: `PhoenixABS40-43_Nosecone_v5.py` (parameters at the top). Build checks are in
`nosecone_build_report_v5.txt` (**all PASS**). The aero harness and raw results are in `aero/`.
Section drawing: `Models/PhoenixABS40-43_nose_VonKarman_v5_section.png`.

**Request (2026-09-24):** "the most aerodynamically optimal nosecone for this build."

## 0. Which build

v5 targets the newest airframe: `Ejection System T5` §6, `t5i_fwd_section`. That section has a
plain 40 mm bore with the nose shoulder at stations 0–20 and a canopy bay at 20–110. T5 left
the nose unmodelled, and in T5 the **whole nose separates and is the extractor**.

The v4 keel/bow-door nose built its own release (servo latch + door spring). T5 now owns that
function, so v4 would duplicate it. v4 is left untouched. **If you still want the v4
architecture, say so**; its outer profile can take the same shape change (§3).

## 1. Result

| | |
|---|---|
| Shape | **Von Kármán** (Haack series, C = 0) |
| Length | **65 mm** (L/D 1.51), tip → base |
| Joint | tangent to the 43.00 mm airframe; measured step **0.001 mm** |
| Shoulder | 42 mm long (≥ 1 D, DESIGN §9). Two ⌀39.70 contact bands with a ⌀39.20 relief between them (DESIGN §7.4 / §8.4) |
| Retention | 3 × pilots for M5 ball plungers at station 8, in a 45°-chamfered internal ring (DESIGN §7.4's preferred detent) |
| Anchor | ⌀4 × 38.5 mm **hardened** dowel across two bosses (tether order nose → cord → canopy, DESIGN §7.7) |
| Mass / CG | **39.6 g** solid ABS/ASA, CG 66.8 mm from the tip. About the same as the current `.ork` nose (≈ 39 g, DESIGN §3.1) |
| Ballast | **None needed.** A solid tip plus a 45° funnel takes lead shot/epoxy if the airframe changes |
| Print | tip up, shoulder on the bed, 0.12–0.16 mm layers, **100 % infill**. The cavity is self-supporting and needs no support material. **Weigh the print.** If it is under ~39 g, re-run `Verify`; the funnel restores margin |
| Overall length | nose 65 + body 340 + retainer cap 17 = **422 mm** |

## 2. Method

OpenRocket 24.12 was run headless through its own Java API (`aero/`) on a **copy** of the `.ork`,
patched to the as-built T5 airframe:

- body 340 mm (the `.ork` still says 250);
- non-nose dry mass 245 g at CG 192.7 mm, summed from the T5, e-bay and fin-can reports plus
  DESIGN §7.11's avionics and canopy;
- rev-5 fins;
- apogee deployment;
- no wind, 1 m rod.

The sweep covered 8 shapes × 6 lengths (40–160 mm):

- **Drag ranking:** a constant 30 g nose, so mass cannot masquerade as aero.
- **Stability/apogee pass:** printed-shell mass.
- **Final check:** the CAD mass and CG in `Verify`.

## 3. Drag findings (Cd at Mach 0.2, whole vehicle)

| Shape | L = 40 | **L = 65** | L = 100 | Base-tangent? |
|---|---|---|---|---|
| **Von Kármán** | 0.4033 | **0.4079** | 0.4147 | yes |
| Parabolic K = 1 | 0.4038 | 0.4085 | 0.4156 | yes |
| LV-Haack | 0.4044 | 0.4096 | 0.4173 | yes |
| Tangent ogive (v4 shape) | 0.4088 | 0.4120 | 0.4179 | yes |
| Ellipsoid (current `.ork`) | 0.4163 | 0.4146 | 0.4221 | yes |
| Parabolic K = ½ / power ½ | 0.4013 / 0.4036 | 0.4046 / 0.4084 | 0.4098 / 0.4155 | **no**: kink at the joint |
| Conical | 0.5797 | 0.4817 | 0.4423 | no |

- **Among base-tangent shapes it is a tie on drag; Von Kármán was chosen.** Von Kármán,
  parabolic K = 1 and LV-Haack are within 0.4 % at 65 mm. That spread is a wetted-area artefact,
  not a real ranking. Von Kármán is the lowest of the three at every length tested. The two
  slightly lower entries in the table have a slope break at the shoulder. OpenRocket does not penalise that break at subsonic
  speed; real flow does, with a separation line at the joint.
- **Shorter always wins in OpenRocket.** Below Mach ~0.8 it gives smooth tangent noses ≈ 0
  pressure drag, so only wetted area (skin friction) is left. The curve never flattens.
- **Why 65 mm and not 40.** L/D ≈ 1 is where that zero-pressure-drag assumption is least safe,
  and very blunt noses do worse in crosswind. 65 mm costs **+1.1 % Cd** against 40 mm, which is
  unmeasurable in apogee (§4). Compared with the old noses, v5 has **−2.0 %** Cd against the
  current `.ork` ellipsoid and **−2.4 %** against the v4 100 mm ogive.
- **Surface matters about as much as shape.** On a printed nose the layer lines trip the boundary
  layer to turbulent almost at once, so a laminar-flow argument for any shape doesn't apply.
  Sand and prime the nose and the first ~50 mm of body, and keep the joint flush. The step is
  already 0.001 mm in CAD; the print must hold it.

## 4. ⚠️ The finding that matters more than the nose

**At the as-built mass the vehicle is not drag-limited. It is badly overweight for 18 mm motors.**

| v5 nose, no ballast | Liftoff | Margin | Apogee | v max | Rail exit (1 m) |
|---|---|---|---|---|---|
| C6 | 308 g | **1.58 cal** ✅ | 19 m | 11 m/s | **4.8 m/s** ❌ |
| B4 | 304 g | 1.62 cal | 4.6 m | 7.7 m/s | 3.9 m/s ❌ |
| A8 | 301 g | 1.65 cal | 1.1 m | 4.5 m/s | 1.5 m/s ❌ |

- The simulated rail exit is 4.8 m/s. DESIGN §4.4 requires **≥ 15 m/s**. At about 5 m/s the
  fins have no authority when the rocket leaves the rod. Also check the manufacturer's maximum
  liftoff weight for each motor; from memory it is roughly 110–115 g for a C6-3. That figure was
  not verified here.
- Even with a far lighter 180 g airframe, the C6 exits at 6.4 m/s.
- At this speed drag is under 2 % of weight. **No nose shape changes apogee by more than about
  0.1 m.** Even at an unrealistic 80 g airframe, best vs. worst tangent nose is about 2 m out of
  134 m.

**Do not fly this stack on A/B/C motors.** The options are:

- a 24 mm mount: a D12-class motor's maximum liftoff weight is roughly 400 g. Check the chart.
  Re-simulate before choosing;
- a large mass diet. Printed parts are at 100 % infill here, and T5's 48 g module plus 57 g
  forward section dominate.

This is outside the nose's scope but gates flight. **Recommend a DESIGN §13 item.**

## 5. Stability with the v5 nose (OpenRocket, `aero/verify_v5_openrocket.txt`)

- Margin is **1.58 cal on the C6** (binding case) with no ballast, which meets the 1.5 cal target.
  At a 180 g airframe it is 1.68 cal.
- CP is 310 mm from the tip (station 245). DESIGN §4.5's hand estimate was 292 mm from its 40 mm
  nose tip, with no body lift; OpenRocket adds it.
- Each 2.5 g of tip ballast adds about 0.04 cal and costs about 0.5 m of apogee on the C6. Only
  add it if the airframe mass or CG changes.

## 6. Open items: what this build cannot close

1. **The detent needs a matching groove in the T5 bore at station 8. It has not been added.**
   `t5_integration.py`'s `fwd_section` is a plain bore; nothing was edited there. **Don't cut a full
   groove into the 1.5 mm wall.** It would leave well under 1 mm at the forward rim, which is the
   joint's load path. Use 3 dimples, or thicken the wall locally as a band inside `fwd_section`
   at stations 4–12. Breakaway = F_max / 2 (DESIGN §7.3). Tune it by
   plunger depth, then measure it on the T5 test stand (T5 README §4 test 2).
2. **The anchor pin must be hardened.** At the 250 N snatch placeholder over a 20 mm span it sees
   about 199 MPa in bending. That is the same dowel spec as T5's RBF pin. Boss bearing is
   3.2 MPa. Insert the pin from the +Y side, flush, and CA it; the bore then captures it. Pour any
   ballast *before* fitting the pin.
3. **The base seat ledge is a 1.65 mm overhang when printed tip up.** It must stay a flat seat
   face. Check it for droop, and face-sand if needed.
4. **The `.ork` has not been updated.** It still says ellipsoid 40, body 250, stale masses.
   DESIGN §0 says the `.ork` leads, so propagate on request. The values are in §1–§2.
5. **Canopy bay shrinks from 90 to 68 mm.** T5's table assumed 20 mm of shoulder engagement,
   with the canopy at stations 20–110. The 42 mm shoulder (DESIGN §9) takes stations 0–42, and
   the anchor bosses and dowel at stations 30–42 prevent nesting the pack inside it. That leaves
   **stations 42–110 (−24 %)**. It has not been checked that the ⌀500 canopy, Nomex and harness
   still fit; do a packing test. The RBF holes at 106.5 are clear. If the pack doesn't fit,
   shorten `SH_LEN` toward 30 mm. That trades against DESIGN §9, so decide on the bench.
6. **Non-nose mass (245 g) is a CAD-report estimate.** Weigh the real stack and re-run `Verify`.
   Margin moves about +0.1 cal per 65 g removed from the airframe.

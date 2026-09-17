# Design Notes — LaunchPad (v2, simplified)

Companion to `BOM.md`. Covers the reasoning that shaped the geometry — the
governing constraint, the stability math, the heat rationale, the full fit
table, and the mechanism simplification from v1. `make_launchpad.py` is the
CAD source of truth; every number below was read off the generated solids
(`build_verification.txt`), not hand-estimated.

## The governing constraint: angular error is amplified ×1000

The rod is 1000 mm long. **1° of slop in the rod socket ≈ 17.5 mm of wander
at the rod tip.** The socket (hub bore + split-collar clamp + thumbscrew) is
therefore the precision feature of the entire pad — but v2 deliberately
trades away some of that precision for simplicity, so this section is also
where the cost of that trade shows up most directly.

Grip length: 60 mm (a plain-bore clamp column, one slit, one cross-screw) =
**15× the rod diameter**, still comfortably past the ≥8–10× floor a clamp
needs to resist cocking under a side load. Bore is ⌀4.25 mm (0.25 mm over
the rod, absorbing ABS shrink).

**The real trade-off of simplifying the clamp:** v1's tapered collet closed
*concentrically* — the nut's cone squeezed all four fingers toward the axis
evenly, so tightening it couldn't itself introduce a cock. v2's split collar
closes from *one side only* (the screw pulls two ears together across a
single slit), which is a one-sided pinch. A one-sided pinch can bias the rod
very slightly off-axis as it closes, and per the ×1000 rule above, even a
fraction of a degree of that bias reads as real millimeters at the rod tip.
This isn't something a CAD boolean check can catch — it's a physical
tightening-technique issue, not a geometry defect. **Tighten the screw
snug, not gorilla-tight, and square the rod against the hub with a small
square or by eye before flying** — the same physical check v1's notes
recommended, now actually load-bearing rather than a nice-to-have.

**Known interaction, not fixed here:** the rocket's own launch lug (per the
airframe's `BOM.md`) is ⌀7 mm ID against this ⌀4 mm rod — roughly 1.5 mm of
radial slop over a 25 mm lug, which by itself permits ±3.5° of rocket cock
on the rod, independent of anything the pad does.

## Why the split-collar clamp is simpler than v1's collet

v1: a 4-finger collet tapered ⌀14→⌀11 over 40mm, closed by a matching
conical nut screwed onto a 26mm trapezoidal thread — the taper direction,
the cone-to-nut clearance, and the nut's travel-vs-closure arithmetic all
had to be gotten right simultaneously, and the finger geometry needed 4
symmetric slits cut through a curved, tapering wall.

v2: a plain straight cylinder with **one** slit and **one** small
straight-threaded cross-screw. No taper to get backwards (a real risk in
v1 — a reversed taper would have jammed the nut open instead of closing it).
No cone-to-cone clearance to match. No closure-travel arithmetic beyond
"does the screw have enough thread engagement," which is now a simple
material-depth check instead of a trigonometric one. This is the same
mechanism as a hose clamp or a split shaft collar — well-understood,
low-risk to model and to print.

## Stability

The hub standoff height comes from the same leg-triangle solve as v1: a
190mm leg reaching from a hinge at R=42mm to a 200mm foot radius can only do
that by dropping ~105.5mm vertically (Pythagoras), and that drop sets how
high the whole hub sits above the ground, regardless of what clamp mechanism
sits on top of it. v2's shorter clamp column (80mm vs v1's 86mm hub body)
brings the cradle down slightly, to **≈187.5mm** above ground (was ≈194mm).

Recomputed with the same method as v1 (drag `F = ½ ρ Cd A V²`, tipping lever
= `0.5 × R_foot` = 100mm, ρ=1.225 kg/m³, Cd≈1.1):

| Wind speed | Total overturning moment |
|---|---|
| 10 m/s | 0.489 N·m |
| 15 m/s | 1.101 N·m |

Restoring moment (system weight × 0.1m lever, ≈0.45–0.55kg realistic total
of pad + plate + rocket): 0.44–0.54 N·m. **Critical tipping wind: roughly
9.5–10.5 m/s** — essentially the same thin margin v1 had; the 6mm lower
standoff barely moves the number.

**Stakes are required equipment, not a gust-only contingency.** Use all
three, every time it's set up outdoors.

## Heat: keep ABS out of the plume

Unchanged in principle from v1, one number updated:

- Plate rides on 3 posts, **72mm tall**, giving a **12mm air gap** above the
  clamp column's top (the hub's own topmost point).
- Plate overhangs the cradle's own footprint by **≥15mm at 150mm plate size,
  up to 50mm at 90mm** — verified for both ends of the supported range.
- The rocket rests directly on the steel plate (standard arrangement for
  18mm black-powder motors). No printed part sits under the nozzle.
- The rocket's lug sits outside its ⌀35mm tube, so the nozzle ends up
  roughly 22mm inboard of the rod's own axis when loaded — over solid
  plate, not at its edge — which is why a centered, open-notch cradle still
  covers the blast zone regardless of the rocket's clocking on the rod.

## Fit table (as-built, verified)

| Feature | Value | Verified |
|---|---|---|
| Rod bore | ⌀4.25 mm | rod (⌀4.0) passes through cleanly |
| Clamp grip length | 60 mm (15× rod dia) | ≥ 8× floor |
| Clamp slit width | 2.0 mm | confirmed open (air, not material) at the slit's own center |
| Clamp OD | ⌀20.0 mm | — |
| Cross-screw thread | ⌀6.0 major / ⌀4.8 minor, 2mm pitch, 30° flank, RH, 6mm engagement | screw↔hub interference = 0.0 mm³ at installed position |
| Threaded-ear material depth | 6.6 mm available vs 6.0 mm nominal | verified — the collar's round OD means material runs out near its edge, checked rather than assumed |
| Screw hole vs rod bore | closest approach 3.3 mm vs 2.1 mm bore radius | 0.0 mm³ overlap, confirmed clear |
| Hinge pin (press) / hub lug bore | ⌀6.0 / ⌀5.8 | 0.2 mm interference, press-fit |
| Hinge pin / leg tab bore | ⌀6.0 / ⌀6.3 | 0.3 mm running clearance, leg pivots freely |
| Cradle socket / post | ⌀8.4 / ⌀8.0 | slip fit, cradle lifts off for transport |
| Plate air gap | 12 mm | posts 72 mm tall |
| Plate overhang | ≥15 mm at 150 mm plate, ≤50 mm at 90 mm | verified both ends of range |
| Stake hole | ⌀7.0 mm, 15° outboard | — |
| Deploy angle | 33.74° below horizontal | solved from R_hinge=42, R_foot=200, leg=190 (unchanged from v1) |
| Leg-vs-hub clearance across full fold arc | 0.0 mm³ | see below — this required an actual geometry fix, not just a parameter tweak |

## The leg had to be shaped to clear the hub as it swings

This is worth explaining because it's not obvious from the part alone: the
leg isn't just a tapered beam for looks. Its hinge end is a deliberately
**narrow neck** (matching the hinge tab's own width, not the leg's full
40mm) for the first ~55mm of its length, widening to full width only after
that.

The reason: the leg pivots around the same point the hub's hinge lug and
connecting wing occupy, and a full-width leg root shares the hub's own Y-span
there regardless of fold angle — rotating the leg about the (Y-axis-aligned)
pivot doesn't move points along Y, so a wide root that overlaps the hub's Y
range at one angle overlaps it at *every* angle. Measured directly: a first
version with a full-width root collided with the hub by 722mm³ (a real
collision, not a meshing artifact) — and a first attempt at narrowing it,
using a simple 2-station taper, only got that down to ~220mm³, because a
ruled loft between "narrow" and "wide" widens gradually starting immediately,
not "narrow, then abruptly wide" the way the fix needed. Holding the neck at
constant width for nearly its full length (via a 4th loft station placed
3mm before the widen point) and tightening the neck's width to exactly match
the hinge tab (removing a deliberate-but-unnecessary 4mm overlap margin)
brought it to exactly 0.0mm³ — verified across the entire fold arc in 10°
steps, not just the final deployed pose.

Worth naming directly: this exact risk existed in v1 too (a full-width leg
root sharing space with a two-ear clevis), but v1's leg-vs-hub check
computed the overlap volume and then did nothing with it — a no-op that
always reported PASS regardless of the actual number. That's fixed here (the
check now asserts a real threshold), which is what caught this in the first
place.

## Print orientation rationale (summary — full detail in BOM.md)

- **Hub: rod axis vertical.** Turns the bore into a stack of concentric
  perimeters rather than a bridged horizontal hole — still the single most
  consequential orientation choice, even with the simpler clamp.
- **Leg hinge tab: bore axis vertical** (leg printed flat, in its own swing
  plane) so the pin's bearing load is reacted as in-layer hoop stress.
- **Hinge pin: axis horizontal** — loaded in shear across its axis, so the
  shear plane needs to be in-plane, not stacked.

## What this design does not cover

- **Tilt/launch-angle adjustment.** Vertical rod only, by explicit choice.
- **Igniter clip holders or cable management** for the existing
  `Electronics/LaunchControl` ground station. Out of scope.
- **The rocket's own lug ID mismatch** against this rod — a pre-existing
  airframe characteristic, not something the pad can fix.
- **A detent/click-stop holding the legs open** during transport — planned
  in both v1 and v2, never built either time. Gravity and ground reaction
  hold the deployed position once the pad is set down; nothing holds it
  open while carried pre-deployed.
- **Precise plate centering for smaller plates** (toward 90mm) — v2's single
  lip ring is sized for the largest supported plate; smaller ones sit with
  real slop instead of being positively located. Confirming the plate is
  seated before flying is a pre-flight check item.

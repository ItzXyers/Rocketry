# Phoenix ABS 40-43 -- Keel + bow-door nosecone (v4)

Source: `PhoenixABS40-43_Nosecone_v4.py` (this folder). Edit the parameter block
there and re-run; this document explains the *why*, not the numbers.

**Update history (same session), oldest first:**
1. Keel grown 50% (`KEEL_HALFW` 35 -> 52.5 deg, 70 -> 105 deg total).
2. "Widen more" (no target given) -> another 50% step (78.75 deg, 158 deg total).
3. Servo port bug fix (gouged the skin) + ejection spring added, pushing the
   Door axially forward.
4. Servo re-mounted axially, latch simplified to hub+pin, no separate arm.
5. **v4.4:** three linked changes -- (a) servo LATCH hub moved fully
   INBOARD, only a small pin pokes through the wall ("bulk of the servo
   inside, only the tip pointing out"), (b) tip ownership INVERTED from
   Door to Keel, keel widened again to 200 deg total, (c) the ejection
   spring reoriented to push the Door OPEN (not just forward) with a
   captured-pin mechanism at each end of the door, described below.
6. **v4.5 (current):** two follow-ups after looking at a v4.4 render --
   (a) the user asked "why do we still have a giant rectangular hole" --
   turned out v4.4's hub fix only addressed the LATCH pin, not the
   SERVO BODY's own mount, which had been flush with the OD (a ~26x18.5mm
   through-wall port) since v4.2. Fixed by moving the servo's flange to
   the INNER wall surface instead -- the case now sits entirely inside
   the already-open bay cavity, no wall cut needed at all, just two small
   blind-hole screw bosses. Caught a real bug fixing this: the two
   mounting bosses were fused at `SERVO_THETA +/- PAD_HOLE_THETA`, and
   with the old 20deg offset one landed outside the Keel's own angular
   span (in Door territory, no material to fuse to) -- came out as a
   disconnected floating solid, caught by a new `len(spine.Solids) != 1`
   assertion, fixed by shrinking the offset to 6deg. (b) the user asked
   "why do we have the latch arm still" -- not a design objection, a
   naming one: the part had been called `LatchArm` since v2/v3, when it
   really was a separate arm/gate/backstop assembly. Since v4.2 it's just
   the minimal hub+pin(+head) that has to mount on the servo's own
   shaft -- every servo-driven mechanism needs *something* there, the
   same role as the stock horn that ships with the servo -- but the old
   name kept reading as if the "no arm" request had been ignored.
   Renamed throughout (script, exports, this doc) to `ServoHorn`.

Supersedes `PhoenixABS40-43_Nosecone_v3.py` (kept for history, not deleted).
v3 built a hinged, partial-arc oval door. Feedback on v3 (2026-09-15, same
session): "I want the tip of the nose to be included in the door too. Ditch
the hinges, click in place. Think fairing combined with a bow door on a
ship, almost the entire mouth/tip opens" -- then, mid-build, the clarifying
message that actually settled the architecture: **"A bow on a ship still has
a part of the 'lip' left right? Even though the 'mouth' is open the 'bottom
lip' remains?? I want something like that."**

## Architecture: a keel, not a cap

v4 is NOT a full end-cap that pops off whole. It's a wide, constant-width
**Keel** strip (200 deg, centred opposite the latch) that stays fixed --
bonded to the airframe, same role v2/v3's Spine always had -- running the
tube's full length, and (since v4.4) **owning the true nose tip** as well.
The **Door** is the remaining arc (160 deg, 44% of the circumference),
Z=25 to 178 -- it no longer reaches the tip. No hinge. Released, it detaches
completely -- tethered only by the shock cord, like a traditional full
nose-cone-separation recovery system, not a hinged hatch.

**v4.4 tip inversion:** the original v4 gave the tip to the Door ("include
the tip in the door too"). This revision's explicit request reversed that --
"the nose point should be with the keel, not the door" -- plus widened the
keel further ("more keel, less door"). Mechanically this is a straightforward
theta-split change: the Keel now automatically keeps the FULL circle for
Z below `Z_DOOR_START` (25mm, up from the old `Z_KEEL_START`=15mm) with no
cut removing it there, the same trick the Keel already used at the aft/
bulkhead end; the Door gets an explicit new cut stripping the tip away
instead of inheriting it by default. `KEEL_HALFW` went 78.75 -> 100 deg
(158 -> 200 deg total keel width), continuing the same one-parameter
widening pattern as the two earlier "grow the keel" requests.

**Why a keel and not a full cap** (unchanged reasoning from the original v4
decision): an earlier attempt in this build session tried a Z-plane cut
(the whole forward cone as one 360-degree piece) before the "bottom lip"
message arrived. That version had no fixed strip anywhere forward of the
bulkhead -- structurally weaker and it required inventing a new axial-
blocking latch mechanism from scratch, which had a real bug. The keel fixes
both: it's a continuous structural member the whole length of the nose, and
because the Door wraps most of the circumference even after widening the
keel (160 deg, still more than the ~157 deg point where a hinge would be
geometrically trapped -- not that this door has a hinge to trap), **it
cannot rotate or pull off tangentially: its own wrap plus the fore/aft
capture (below) constrains it until the latch and captured pins both
release.**

## v4.4: latch mechanism -- hub moved inboard, "pin and socket" fore/aft capture

Two linked requests drove a real mechanism change, not just resizing:
"the bulk of the servo should be kept inside the rocket, only the tip
should point out (a 4mm D hole)" and "I want the spring to press against
the thing from an 'upward' perspective -- it should try to open the door
and the servo should stop it. We should have a pin and socket mechanism
that makes the door only openable from the bottom... like battery doors."

Read together these describe ONE mechanism: **a door captured at its FORE
(tip) end by fixed pins in sockets, released only at its AFT end** by the
servo latch -- exactly how a battery door works (a hooked tab at one edge,
a spring-loaded catch at the other), not a hinge running the whole seam
(which the user explicitly asked to remove earlier in this session). The
fore-end capture is 2 small fixed, load-bearing pin/pocket features per
seam near Z=35 (`Z_FORE_CAP`) -- NOT servo-driven, NOT the light assembly-
only snap-clicks (same gap-bridging technique, deeper/stouter, its own
build step so it reads as structural). "Openable only from the bottom"
maps directly onto the airframe: with the rocket standing nose-up, the aft
end (where the latch is, Z=150) is the "bottom," and that is the only end
that ever releases.

**Hub inboard fix:** the pre-v4.4 hub sat proud of the OD (`R+1`, a visible
16mm disk bump on the outside of the airframe) -- exactly the "bulk should
be inside" problem. Fixed by moving it to `HUB_R = R_BAY_IN + 0.5`
(18.5mm, just inside the inner wall surface). But the pin can no longer be
a simple radial peg in a radial hole once it does that AND the spring's
load direction changes (next section) -- **a radial pin in a radial hole
provides zero resistance to a radially-outward pull** (the lug just slides
straight off the pin's own axis, like a cup off a peg). Fixed with a
keyhole/mushroom capture: the pin's tip has a wider HEAD (`PIN_HEAD_D`=7mm);
the lug's blind socket necks down to a narrower MOUTH (`PIN_SHAFT_D`=4mm,
matching the request directly) right at its opening, trapping the head
behind the neck -- the same principle as a tripod quick-release plate or a
captive panel fastener, not a new invention. Release is still a small servo
ROTATION (this model is a closed-position snapshot, not a swept-motion
simulation, same convention as the pre-v4.4 hub+pin) sweeping the whole
shaft+head assembly tangentially clear of the lug's socket. Honest
simplification carried forward: the wall's pass-through hole can't be a
perfect circle for this reason -- the pin sweeps a small tangential arc as
the hub rotates, so it's actually a short slot a bit wider than 4mm at the
skin, not a literal 4mm circle.

**Torque / backstop:** the pre-v4.4 "no backstop needed" proof was specific
to a PURELY AXIAL escape force (`tau_z = r_x*F_y - r_y*F_x` depends only on
F's X/Y components, which are exactly zero for a pure-Z force, for ANY pin
offset -- a trivial vector identity, reverified against the new geometry
at build step [9.5], still holds). The spring's escape force is RADIAL now
(next section), which has nonzero X/Y components -- that proof does NOT
carry over, and the build script confirms it numerically at [9.5b]: a
15N radial test load produces about -76 N*mm of torque about the shaft,
nonzero as expected. So this mechanism needs a backstop again, for the
same underlying reason v2/v3's radial-shaft mechanism did. A small fixed
boss on the Keel (`BACKSTOP_*` params), positioned on the side the
computed torque actually drives the hub toward -- **the sign is verified
against the real torque calculation, not just assumed** (`[9.5b]` raises
if it's ever on the wrong side) -- blocks that rotation without blocking
the servo's own opposite-direction release sweep. This is a sign-check,
not a strength proof: the backstop's size is chosen by inspection against
a representative 15N release-assist spring, not a margin calculation.

## v4.4: ejection spring reoriented to push the door OPEN

Previously (v4.3) the spring pushed the Door axially forward, addressing
"how does this actually deploy anything" but not matching the newer,
more specific request: "the spring should try to open the door... like a
battery door." One real geometric constraint shapes how "open" is
realized: the Keel and Door are theta-adjacent pieces of the SAME shell at
the SAME radius, not stacked -- there is no second surface at a different
radius for a literally radial spring to react against. What IS buildable,
and mechanically equivalent to "pushes the door open": a spring compressed
TANGENTIALLY in the seam gap, near the latch cluster, pushing the Door's
edge away from the Keel's edge circumferentially. With the Door's fore end
captured (previous section) acting as the effective pivot, a tangential
push at the free aft edge is exactly the force that kicks that edge
RADIALLY outward -- the "pop open" action the battery-door mechanism
describes, reacted through geometry that actually exists here rather than
an unbuildable literal radial spring between co-radius parts. Relocated
from Z=105 to Z=130 (near the latch cluster, clear of its features) so it
reacts directly against the same joint the servo pin is holding. Not
modeled as an actual coil (same convention as the servo/screws/cord);
bench-select the actual spring once the release force needed is known.

## Retention: fore capture + snap-clicks (seams) + one servo latch (aft)

- **Fore capture, 2 points** (`Z_FORE_CAP`, near Z=35) -- fixed,
  load-bearing, reacts the spring's constant push. See "pin and socket
  fore/aft capture" above.
- **Snap-click points, 5 per seam (10 total)**, `SNAP_Z_LIST` spread Z=30
  to 165, skipping the latch's own Z and the fore-capture Z. Light --
  assembly/anti-rattle retention, NOT the flight load path. Bumps rub
  along the keel's edge for most of the slide-in distance, seating fully
  only at the end -- untested for assembly force, flagged as an open item.
- **Servo latch, 1 point** (see mechanism section above) -- the ONLY point
  that ever releases. A Door-side keyhole lug captures a servo-driven
  pin's head; a Keel-side backstop reacts the radial torque.

## Servo mount (v4.5: flange moved to the INNER wall)

Real SG90 envelope (23x12.4x22.7mm body, 32.2mm tab-to-tab, 9g --
`Avionics/avionics_bay_packing_40mm.md` / `DESIGN.md` Sec7.5.2), shaft
AXIAL: case reaches inward (12.4mm, its width) and aft (17.7mm, its former
"height"). Through v4.2-v4.4 the flange sat AT the OD, which meant cutting
a port clean through the wall (~26x18.5mm) for the case to sit in -- the
"giant rectangular hole" visible in every render since, never actually
fixed by the v4.3 bugfix (that only corrected the cut's depth by 1mm, not
the fact that it went through the wall at all). v4.5 moves the flange to
`SERVO_MOUNT_R = R_BAY_IN - SERVO_CLR` (the INNER wall surface) instead --
the case's 12.4mm radial reach fits entirely inside the already-hollow bay
cavity (R_BAY_IN=18mm), so no wall material needs removing for the case at
all. Anchored by two small blind-hole screw bosses (`MOUNT_BOSS_D=5mm`,
reaching `MOUNT_BOSS_REACH=2mm` in from the inner wall) instead of
through-wall tab holes -- neither boss nor pilot hole reaches the OD.
Real bug caught fixing this: the bosses are fused at
`SERVO_THETA +/- PAD_HOLE_THETA`, and the original 20deg offset put one
boss outside the Keel's own angular span (100deg from centre) -- in Door
territory, where the Keel has no material to fuse to. It came out as a
disconnected floating solid (`len(spine.Solids)==2`), caught by a new hard
assertion, fixed by shrinking `PAD_HOLE_THETA` to 6deg. Same flange-split
assumption as v3 for where the tab flange sits relative to the shaft --
still unverified against the actual unit, bench-check before finalizing.
Mounting-hole spacing is still an approximated angular offset, not a
measurement.

## Shock cord: door-side anchor is a real tether, not a routing clip

Unchanged from v4.2/4.3: with no hinge, the shock cord is the ONLY thing
connecting the departed Door to the rest of the rocket once BOTH the fore
capture and aft latch have released. The door-side anchor (`Z_ANCHOR=165`,
opposite the latch) is a proper tie-off loop -- cord threads through a bore
and is knotted, closed by a printed snap slot narrower than the cord -- not
a light dressing clip. The bulkhead M4 eyebolt (unsplit, on the Keel/Spine
side, unchanged since v2/v3) is the other end's anchor.

## What's NOT changed from v2/v3

Outer profile (true-arc ogive, barrel, taper, shoulder), cavity, bulkhead
eyebolt, shoulder retention screws, and the no-ejection-charge architecture
(`../DESIGN.md` Sec7's spring-piston/ball-detent system remains superseded,
unchanged since v2) are all identical in principle to v3.

## Geometry (Z=0 at nose tip, +Z aft)

| Section | Z range | Notes |
|---|---|---|
| Ogive nose | 0 - 100 | True-arc tangent ogive, R=21.5, rho=243.3 |
| Barrel / bay | 100 - 190 | Constant OD 43, wall 3.5mm |
| Keel (fixed) | 0 - 237 | 200 deg wide, owns the TRUE TIP (Z<25) + full bulkhead/shoulder |
| Door (detaches) | 25 - 178 | 160 deg (44% of circumference), no longer reaches the tip |
| Fore capture | 30 - 40 | Fixed pins/sockets, the door's captured end |
| Latch cluster | ~146.5 - 153.5 | Hub (inboard) + shaft/head pin + backstop (Keel), keyhole lug (Door), all at Z_LATCH=150 |
| Servo mount (case) | ~155 - 173 | Fully inboard, r<18.0 -- no wall cut, just 2 blind screw bosses at FLANGE_Z=155 |
| Bulkhead | 182 - 190 | Solid, 8mm, UNSPLIT (full ring) -- Keel/Spine only |
| Shoulder taper | 190 - 193 | 43 -> 39.7 lead-in, UNSPLIT |
| Shoulder land | 193 - 237 | dia 39.7, UNSPLIT, glued + screwed into the body tube |

Total length 237mm (unchanged since v1).

## Mass (100% infill reference; real prints at typical 20-40% infill will be
lighter)

| Part | Volume (mm^3) | Mass @ 100% |
|---|---|---|
| Spine (keel) | 100,012 | 105.0 g |
| DoorHalf | 23,001 | 24.2 g |
| ServoHorn | 551 | 0.6 g |

Total 129.8g -- essentially unchanged from v4.3 (128.1g): the keel grew
(wider + owns the tip) and picked up the small mounting bosses (v4.5), the
door shrank correspondingly, net mass barely moves.

## Bill of materials (bought hardware, not modeled as solids)

- SG90 9g micro servo, >=1.5 kg-cm, body 23 x 12.4 x 22.7mm / 32.2mm tab-to-tab
- M2 screws x2 (servo)
- M3 screws x3 (shoulder retention)
- M4 bolt + 2 washers + nut (bulkhead shock-cord anchor -- primary load path)
- ~6mm tubular cord (shock cord), tied off through the door-side anchor loop
- Small compression spring (ejection assist), ~4mm dia, sized for the
  actual release force needed -- not yet selected, see open item 1
- Latch keyhole lug: printed integral to DoorHalf (captures the pin's head)
- Latch hub+shaft+head: printed as the separate ServoHorn part (renamed from
  "LatchArm" -- that name was a holdover from v2/v3's real arm/gate/backstop
  assembly; since v4.2 this is just the minimal piece mounted on the servo's
  own shaft, equivalent to a stock servo horn, not a bridging arm), mounted
  on the servo shaft
- Backstop: printed integral to Spine (reacts the radial-load torque)

## Open items / bench-fit before flight

1. **Separation energy source: now pushes the Door OPEN (tangential-at-
   the-gap, kicking the aft edge out) instead of just forward, but the
   actual spring is still unselected.** Sequence now: (1) servo retracts
   the pin (rotary sweep clear of the keyhole lug), (2) the spring (5deg
   of stored angular travel at the seam) kicks the Door's aft edge
   radially outward, pivoting loosely about the still-engaged fore-capture
   pins, (3) once the aft edge has swung clear, the fore-capture pins
   themselves disengage (they are not a true hinge, just a local capture --
   see mechanism section), and the Door is free, tethered only by the cord,
   (4) ram air likely helps peel/carry it the rest of the way, (5) shock
   cord goes taut, (6) the parachute -- loose in the cavity -- has to be
   dragged out by that airflow. What's still open: the spring's actual
   rate/force hasn't been derived from anything; the fore-capture pins'
   disengagement geometry (how far the aft edge must swing before the
   fore pins actually clear their pockets) is asserted by construction,
   not verified by a swept-motion check. Bench-test with a real spring
   before flight.
2. **Latch proof load, servo unpowered.** Now validating a genuinely
   different load path than v4.2/4.3: a radial pull on the keyhole lug,
   resisted by the pin's head bearing against the lug's neck shoulder,
   reacted through the hub to a fixed backstop (not just pin bending
   against an axial pull). Don't assume prior pass/fail intuition
   carries over.
3. **Backstop is a sign-check, not a strength proof.** [9.5b] confirms the
   backstop sits on the correct side of the hub to oppose the radial-load
   torque, computed against a representative 15N spring force -- but the
   backstop's own size (4x6x2mm) was chosen by inspection, not a margin
   calculation against the actual spring or a mishandling load.
4. **Wall pass-through is a slot, not a perfect 4mm circle.** The pin
   sweeps a small tangential arc as the hub rotates between latched and
   released -- honestly flagged in the LATCH param block, not modeled as
   a literal round hole in this snapshot-only build.
5. **Fore-capture disengagement is asserted by construction, not
   verified.** The pins/sockets are sized to release once the Door has
   rotated/shifted some amount after the aft latch opens, but this script
   only builds the CLOSED-state geometry (same convention as the servo
   latch) -- there's no swept-motion check confirming the fore pins
   actually clear their pockets before something else binds.
6. **Snap-click assembly mechanics untested.** Bumps rub along the keel's
   edge for most of the slide-in distance, seating fully only at the end --
   check assembly force and for scratching/wear before relying on repeated
   assembly/disassembly.
7. **Keel section-loss** around the latch/servo/backstop cluster (Z~146.5-
   153.5) -- this is the SOLE structural path forward of the bulkhead,
   unlike v2/v3's 180-degree spine (though the keel itself is now much
   wider, 200 deg, than v2/v3's). Worth a bench load check specific to
   this zone.
8. **Servo mount's flange-to-shaft split (5mm out / 17.7mm in)** is still
   an assumption carried from v3, not confirmed against the actual unit.
   Mounting-hole spacing (`PAD_HOLE_THETA=20deg`) is likewise approximate.
9. **Avionics placement undecided** -- same open item carried since v1.

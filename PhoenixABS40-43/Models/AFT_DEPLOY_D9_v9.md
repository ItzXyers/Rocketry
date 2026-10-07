# D9aft v9: printed snap latch replaces the shear pins

Delta note on top of `AFT_DEPLOY_D9_v8.md`.

| | |
|---|---|
| **Script** | `Models/PhoenixABS40-43_D9aft_v9.py`. It reads v8's exported AftTube and fin-can STEPs (read-only) and runs in about 20 s |
| **Report** | `…_D9aft_v9_report.txt`: **ALL PASS** |
| **Latch source** | `Models/PhoenixABS40-43_SnapLatchCoupon_v1.py` (+ `_v2.py`: aft band 7 mm). Reports are next to each script |

## Why (2026-10-07)

- **The v1 shear pins do not print.** They were 0.8 mm thick with a 0.6 mm neck, and came out as
  shapeless blobs. The cause is physics: a 4–24 N release in ABS needs only about 0.5 mm² of neck.
- **A snap latch gets the same low force from bending a normal-sized tongue.** Every feature is at least 0.6 mm, and it is reusable.
- **Coupon results.**
  - L24 was the user's pick. Its first pull held **873 g = 8.6 N per pair**, against a model value of 12.1 N.
  - The v1 coupon's 4 mm aft band curled. v2 makes the band 7 mm, and v9 uses v2.
- **The user asked to implement it without more tests.**

## What changed

**AftTube.**
- The 2 pin slots are filled.
- 2 **L24 tongues** sit at **60° and 180°**, the old pin angles. Each is 1.2 mm thick, with the outer skin recessed 0.3.
- The tongues run around the circumference, so they bend along the printed perimeters.
- The forward edge is slanted at 45°, so each tongue grows from its root without support. A 7 mm aft band bridges the 1.0 mm aft gap.
- Each tongue carries an inward **bump**, 1.2 × 5 × 4.08 mm, with a 45° release ramp and a 30° entry ramp.
- Everything is within Zf 58.4–89.3, inside the 40 mm coupler. The tube is unchanged elsewhere: checked against the v8 STEP, nothing is added outside the OD.

**Fin can.**
- This is v8: the v4 slotted can plus the staple lug at 300°.
- The pin slots are filled.
- 2 **windows** are cut through the coupler at 60° and 180°, with a matched 45° forward face and 45° ceilings, so they print boss-down with no support.
- They clear the staple lug and the thrust ring.

**Pins:** dropped. The pin card and pin coupons are obsolete.

**Unchanged:** nose v6, FwdTube v8 (5 mm eyelet), EbayCap, sled v7, fins v4 and cap v1.

## How it works

- The bay gas pushes the fin can aft. The window's forward face rides up the bump's 45° ramp, which bends the tongues **outward into free air**, by 1.05 mm.
- Gas leaking through the windows and the slip gap also pushes the tongues outward, which helps the release.
- If the tongues were in the coupler instead, bay pressure would push them *into* the catch.
- The two latches are 120° / 240° apart, so the fin can **clicks in only one clocking**, the same one the pins allowed (fins clear of the rod line).

## Checks (report)

- The v1 and v8 constants are confirmed by probes on the v8 parts.
- Both parts are valid single solids.
- Feature probes: 18/18 on the tube and 9/9 on the fin can, the real threaded part.
- **Seated:** 0 overlap.
- **Pulled 0.6 mm aft:** the bump catches in the window. The tube without its bumps does not catch, which shows the bumps are what hold it.
- **Release:** with the tongues deflected 1.05 mm, a full 44 mm separation sweep is clear.
- **Negative control:** undeflected bumps block the slide.
- **Wrong clockings (120°, 180°, 240°):** the bumps land on solid wall, so there is no click.
- The chute bay is a clean ⌀40 bore, and the ⌀14 gas column is clear.
- The tongue strain is 0.36 % (limit 1 %).
- **Printability:** the AftTube adds only the two aft-gap bridges. The fin can gets no new overhang.
- **Mass:** 0.45 g less than v8, all at the aft end. CG and stability are as v8, and the balance gate in the README still applies.

## Forces

| | |
|---|---|
| Hold need (v1 budget, all loads additive) | 4.2 N; ~1.6 N with the bay vented by the latch slots |
| Measured release, coupon v1 L24 (1 pull) | **8.6 N** per pair → 2.0× / ~5.4× |
| Release budget | 24 N − ~3 N slide friction |
| Ideal black powder for 8.6 + 3 N on the 188 cm³ bay | ~8 mg (D-class charges are usually far more; Klima's is unpublished) |

The flight latches are 120° apart, where the coupon's were 180°. The coupler can shift about 0.2 mm in its slip fit, so expect a slightly lower release than on the coupon.

## Open risks (accepted by the user: "we can't afford to test right now")

1. **One bench pull only.** Repeat pulls and cycle tests on coupon v2 are still worth doing when there is time.
2. **The Klima D9 charge is unpublished.** The physics margin is large, but no ground test has been done.
   A static fire of the packed aft section would settle it.
3. **The aft-gap bridge can curl with damp ABS**, as on coupon v1. Dry the filament and check that the tongues move freely.
4. **The latch slots vent the bay to the outside.** The AftTube is no longer sealed except at the joint. Never tape over the tongues.

## Assembly

Pack the bay, push the fin can in, and turn it until it **clicks**. No click means do not fly. Pull gently
to check that it holds.

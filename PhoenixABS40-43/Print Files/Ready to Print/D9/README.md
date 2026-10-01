# Phoenix ABS 40-43: D9aft complete print set (current = v5)

Everything printed for the Klima D9-5 aft-deploy rocket, pre-oriented and dropped to Z = 0.
**Slice these.** They are copies; the source files stay in their subsystem folders.

- Design: `Models/AFT_DEPLOY_D9_DESIGN.md` (v1), then `AFT_DEPLOY_D9_v2.md`, then
  `AFT_DEPLOY_D9_v3_v4.md`, then `AFT_DEPLOY_D9_v5.md`.
- **All parts ABS**, printed in an enclosure.

| Part | Version | Why |
|---|---|---|
| Nose | v6 | Screw-on |
| FwdTube | v5 | Thread + key groove + eyelet + **ARM mark** |
| EbayCap | v5 | Printed springs + rotation key, pocket fitted to sled v4; **no foam ring** |
| Sled | **v4** | Reed-switch arming, outboard-open battery tray, seat foot |
| AftTube | v2 | |
| Fin can | v4 | **Slotted + 3 separate fins, epoxied** |
| Pins, coupons, cap | v1 | |

## Print order

### 1. Test first

These are cheap and gate the expensive parts.

| File | Qty | Orientation | Notes |
|---|---|---|---|
| `…_D9aft_v1_ShearPinCard.stl` | 1 | flat | 16 pins: necks 0.5 / 0.6 / 0.8 / 1.0 mm, marked with 1–4 nicks on the head. Use a brim. Print in the **same job and filament** as the coupons. |
| `…_D9aft_v1_PinCouponOuter.stl` | 1 | either end | Pull-test rig |
| `…_D9aft_v1_PinCouponInner.stl` | 1 | floor down | Pull-test rig |

**Pin acceptance:** 8–15 N per pin, three pairs per batch (v1 note §4.3).

**Thread fit test:** in the slicer, cut the FwdTube 20 mm below its mouth and the nose 20 mm above
its shoulder, and print only those pieces. Check that it screws in by hand and seats flush.

### 2. Flight parts

| File | Qty | Orientation | Supports | Notes |
|---|---|---|---|---|
| `…_nose_VonKarmanScrew_v6.stl` | 1 | **tip up**, thread on the bed | none | 0.12–0.16 mm layers. Sand and prime. |
| `…_D9aft_v5_FwdTube.stl` | 1 | **bulkhead down** (the eyelet bar is the first layers) | none | Female thread + key groove at the top; ARM line engraved on the OD |
| `…_D9aft_v2_AftTube.stl` | 1 | forward end down | none | 222 mm tall. Launch lug at 300°. |
| `…_D9aft_v4_AftFinCanSlotted.stl` | 1 | boss down | **none** | 3 annular bridges (the two centring rings and the thrust ring, 9.6 mm): 4 perimeters, slow first bridge layer |
| `…_D9aft_v4_Fin.stl` | **3** | **flat** | none | Layers parallel to the faces (strong in bending) |
| `…_MotorRetainerCap_v1.stl` | 1 | base down | none | Slow the thread walls (~30 mm/s) |
| `…_D9aft_v5_EbayCap.stl` | 1 | disc down, loop + bumps up | none | The 3 spring beams are 19 mm arc bridges, 4 layers thick: use bridge settings |
| `…_D9aft_v5_ElectronicsSled_v4.stl` | 1 | aft end (seat foot) down | none wide | Sled v4; see `Avionics/avbay_sled_build_report_v4.txt` for assembly order and retention |

## Bonding the fins

1. **Dry fit.** Each fin tab slides through its slot. It crosses the wall and both centring rings
   and stops 0.4 mm off the motor tube. There is 0.15 mm of gap per side for epoxy.
2. **Mask the coupler and the pin slots.** No epoxy may land on the coupler: it is the separation
   joint.
3. **Epoxy the tab into the slot.** Use a 30-minute epoxy, and run it into the slot so it wets the
   wall, both rings and the motor tube. The slots set the 120° spacing. Check that each fin is
   square to the tube (a card jig helps) and let it cure fin-down.
4. **Fillets.** Once cured, run a **4 mm root fillet** on both sides of every fin, in epoxy
   thickened with microballoons or colloidal silica. This is the `.ork`'s fillet, and it also
   seals the slot line. About 2 g of epoxy in total (already in the mass rollup).

## Also needed (not printed)

- 2 × M2 × 10 pan head (sled to EbayCap)
- Kevlar leader, about 250 mm: **tie it to the FwdTube eyelet before bonding the tubes**
- Shock cord ≥ 1.2 m, ⌀500 canopy, Nomex blanket or wadding
- Epoxy for three jobs only: the FwdTube spigot → AftTube joint, the fins and the fin fillets.
  **Never glue the fin-can coupler.**
- Tape: over the pin heads, across the nose joint, one wrap on the motor casing
- Klima D9-5 motors
- *No foam ring*: the EbayCap springs replace it.

## E-bay in and out

- **In:** the key on the cap rim goes into the groove at the mouth (180°), so the e-bay goes in only
  one way. Screw the nose on hand-tight; its shoulder presses the 3 spring bumps (≈ 4.6 N). Tape
  the joint.
- **Out:** untape, unscrew the nose, lift the e-bay out by its loop.
- **Arming:** hold a magnet on the engraved **ARM line** on the FwdTube (−10.9°, stations 20–34, with a cross tick at
  the capsule's centre). The reed capsule is 2.5 mm under it.

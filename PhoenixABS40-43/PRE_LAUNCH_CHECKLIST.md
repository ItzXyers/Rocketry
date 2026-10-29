# Phoenix ABS 40‑43 — Pre‑Launch Checklist

**Vehicle as of 2026‑10‑29:** D9aft **v13** airframe (+30 mm screw‑in extension ring) with sled **v21**,
Klima **D9‑5**, aft deployment on the motor's ejection charge, snap‑latch fin can (v11), 5 mm
retention line, ⌀500 canopy. The flight computer only logs: it fires nothing.
**Pad:** launch pad v2 on the ⌀4.0 mm steel rod. **Ignition:** RSP4 LaunchControl.

This replaces `DESIGN.md` §11, which still describes the retired spring‑ejector build (spring, latch,
RBF pin, vents). Section references below point to the source documents:

| Short ref | File |
|---|---|
| D9 v1…v11 | `Models/AFT_DEPLOY_D9_DESIGN.md`, `Models/AFT_DEPLOY_D9_v<N>.md` |
| v13 report | `Models/PhoenixABS40-43_D9aft_v13_report.txt` |
| Print README | `Print Files/Ready to Print/D9/README.md` |
| OR v11 | `Models/aero_D9aft/verify_D9aft_v11_openrocket.txt` (latest OpenRocket run) |
| Pad v2 | `Models/launchpad_build_report_v2.txt` |
| Avionics bench | `../Electronics/Avionics/avionics_build_checklist.md` |
| Pad procedure | `../Electronics/LaunchControl/pad_checklist.md` |
| Site | `../LAUNCH_SITE.md` |

Work through it in order: **§0** once, before booking a launch day. **§1** once per built airframe.
**§2–§7** every launch day.

---

## 0. Readiness gates: open items that block a live flight

These items are open in the design notes. Until every box is ticked, run launch day as a **dry
rehearsal** (pad, arming and countdown with no motor and no igniter).

**Stability, mass and balance**
- [ ] **Re‑run OpenRocket on the v13 vehicle.** The latest run (OR v11, before the ring) gives
      **1.48 cal at liftoff**, which is under the 1.5 gate. v13 adds a 30 mm ring and moves the
      predicted CG to **248.1 mm from the new tip** (liftoff 274.0 g). The v13 report says the old
      226 mm balance gate **does not carry over**. Load the v13 numbers into
      `PhoenixABS40-43_D9aft_v13.ork`: NOSE_G 14.6, NOSE_CG 43.8, NS_BODY_G 232.3, NS_BODY_LEN 343.5,
      NS_BODY_CGX 179.6. Then record:
  - [ ] the new CP, and the margin at liftoff and at burnout (gate **≥ 1.5 cal**);
  - [ ] the new **balance gate**, meaning the CG distance from the tip that gives 1.5 cal: _______ mm;
  - [ ] the ballast (g) on the EbayCap top needed to reach the gate plus about 0.1 cal of cushion: _______ g.
- [ ] **Weigh the 5 mm retention line.** The rollup assumes 18 g (12 g/m × 1.5 m). Each gram of error moves
      the CG about 0.15 mm.
- [ ] Measure the small‑parts mass and the electronics mass. Both are assumed in the rollup (D9 v5, v6).

**Rail exit and pad**
- [ ] **Rod length.** On pad v2, guided travel = rod length − **316 mm** (Pad v2 [10]). OR v11 gives
      11.5 / 13.2 / 14.5 m/s at 1.0 / 1.5 / 2.0 m guided, so even 2 m guided misses the 15 m/s floor
      on a heavier v13. Buy the longest rod you can keep straight. **≥ 2.3 m gives 2.0 m guided**, and
      the ⌀4.0 mm rod whips more as it gets longer. Then set the `.ork` rail length to the guided
      figure and re‑run.
- [ ] Rod rated or measured straight. The lug bore is ⌀4.4 for the ⌀4.0 rod.
- [ ] Pad v2 printed and dry‑fitted with the rocket. Rotation key against the stop post, the cap
      clear of the rod at full lean (Pad v2 [5]–[7]).
- [ ] **Pegs for all three feet.** The bare pad tips at **8.5 m/s** of wind (Pad v2 [11]). That FAIL is
      deliberate: pegging the feet is the fix.

**Recovery (not flight‑proven)**
- [ ] **Snap latch.** It has had one bench pull (8.6 N per pair). If time allows, do 3 pulls and 10
      click‑in/pull‑out cycles on coupon v2 (Print README §1b). Accept 8–20 N per pair, with less than
      20 % drop after cycling.
- [ ] **Spent D9 casing fit:** the cap lip sits on the casing wall and the forward rim sits on the
      1 mm ledge (D9 v1 §9 test 4).
- [ ] **Thread fit:** nose ↔ ring and ring ↔ FwdTube screw in by hand and seat flush.
- [ ] **Pack test, 5 cycles:** canopy, line and Nomex fit into 150 × ⌀40. The fin can clicks on, and
      a hand pull at about 9 N releases it with the canopy fully out every time (D9 v1 §9 test 5).
- [ ] **Harness pull:** 2 × 250 N on each anchor (FwdTube eyelet, fin‑can staple), with no cracking.
- [ ] **Descent rate.** OR v11 gives 5.03 m/s on ⌀500, against the ≤ 5 m/s target, and v13 is heavier.
      Accept it, or fit a ⌀550 canopy if it packs.
- [ ] Accept that **the first flight is the charge test** (D9 v1 §9 test 7). The Klima charge size is
      unpublished.

**Avionics and ground station**
- [ ] Sled passed `avionics_build_checklist.md` end to end, including **C1 fitted** (a hard gate).
- [ ] **Wi‑Fi credentials changed** from the defaults in `firmware/src/config.h`
      (`FLIGHTCOMPUTER-XXXX` / `changeme12345`) and in LaunchControl `config.py` / `network/*.conf`.
- [ ] Firmware **0.2.3 or later** flashed (no deploy channel). `GET /config` shows the version.
- [ ] Launch‑detect tunables bench‑checked, since they are marked STARTING DEFAULT in `config.h`: 3.0 g
      for 100 ms. `MAX_TIME_TO_APOGEE_MS` (20 s) exceeds the simulated ~7 s to apogee.
- [ ] **LaunchControl igniter circuit built, its pins confirmed in `config.py`, and the arm/fire/cutoff
      sequence bench‑tested on a dummy load** (Pad procedure §0). Until then, no live igniter.
- [ ] AP+STA concurrency checked on this Pi (`iw phy0 info`) at least once.

**Site and paperwork**
- [ ] SMRK membership (+ Tripoli insurance) and a confirmed Högsäter launch day, or a private field
      with written landowner consent (Site §6.3, §8).
- [ ] Liftoff mass stays **under 500 g** with no metal airframe, so no Transportstyrelsen permit is
      needed. Phoenix is about 274 g.
- [ ] If the site is within 10 km of Landvetter or Säve, the airport has agreed a window (Site §3).

---

## 1. Build acceptance (once per airframe)

**Print set** (Print README; all ABS, enclosure, dried filament)
- [ ] Nose v6, FwdTube v8, AftTube **v11**, fin can **v11** (slotted), Fin v4 ×3, Cap v1, EbayCap v6.
- [ ] **Extension ring v13 + sled v21 + TopKeeper v21, as a matched pair.** v12 ↔ v20 is the only other
      valid pairing; the two never mix. Print with the `make_bambu_projects_v10.py` plates (anti‑string).
- [ ] Ring: the seat face sits flat on the tube mouth. **The key slot and the cap tab are untrimmed**:
      together they are the anti‑unscrew lock.
- [ ] AftTube: **both latch tongues move freely**, and their tips sit on the circle (not proud, and
      not sunk more than about 0.3 mm). No supports were used.

**Assembly** (D9 v1 §7, v2 §4, Print README "Bonding the fins")
- [ ] **Retention line tied to the FwdTube eyelet before the tubes are bonded.** After bonding the eyelet
      cannot be reached.
- [ ] FwdTube spigot bonded into the AftTube, with **no epoxy on the aft 45 mm of the AftTube bore**.
- [ ] Fins epoxied square (use a jig), with 4 mm fillets. **The coupler and its 2 latch windows are masked
      and free of epoxy.**
- [ ] Fin‑can end of the line: Kevlar, or sleeved in Nomex where it passes the ⌀14 gas port.
- [ ] Fin can: the tab drops into the notch and **2 clicks** are heard. Turned 180°, it stands about 5 mm proud and does
      not click.
- [ ] M2 pan head at the piezo hole filed flat (sled report WARN).

**Measured, then written on the airframe**
- [ ] Liftoff mass, ready to fly (loaded D9, bay packed, ballast fitted): _______ g (predicted 274.0 g).
- [ ] **CG with a loaded D9 and the bay packed:** _______ mm from the tip. It must be **at or forward
      of the §0 balance gate.** Mark the CG on the tube.
- [ ] Swing test (tie at the CG, about 3 m of line, swing overhead): the nose leads.
- [ ] Bulkhead leak test: tape the aft end with the fin can off and blow gently. No air reaches the
      e‑bay ports (D9 v1 §9 test 3).

---

## 2. Before leaving home

**Go/no‑go**
- [ ] Every box in §0 is ticked. If not, this is a dry rehearsal: leave the motors and igniters at home.
- [ ] Forecast wind **≤ 4 m/s** at launch time. The stability margin is thin (D9 v6 Monte Carlo); a
      ≤ 3–4 m/s cap also keeps drift on the field (Site §6.1).
- [ ] Fire‑ban status (`brandrisk.se` / kommun) is checked the evening before and rechecked in the
      morning. A ban means no launch.

**Avionics**
- [ ] Flight LiPo charged, above 3.70 V (`BATT_LOW_V`), and **unplugged for transport**. There is no power
      switch: plugging in the battery is the switch.
- [ ] At least **5 MB free** on the flight computer flash (`LOGS`). Old logs dumped, backed up and
      deleted. Below 5 MB the boot self‑test fails.
- [ ] Pi power source charged. LaunchControl fired‑latch cleared with `scripts/clear_fired_latch.py`,
      with no latch warning at boot.

**Pack list**
- [ ] Rocket. Spare TopKeeper and EbayCap if you have them.
- [ ] **Klima D9‑5** motors (only these; see §6), igniters, and spare igniters.
- [ ] ⌀500 canopy, retention line, **Nomex blanket or wadding (mandatory)**.
- [ ] Ballast weights for the EbayCap top, and tack or tape to hold them.
- [ ] Tape for the nose/ring joint and for one wrap on the motor casing.
- [ ] Spare M2 × 10 pan heads, a small screwdriver, zip ties, Kapton.
- [ ] Launch pad v2, **rod ≥ the length set in §0**, **3 pegs**, a 1 kg weight for the hub tie‑down.
- [ ] Steel or bare‑ground blast surface, **water and a fire extinguisher**.
- [ ] Balance string or knife edge, a ruler (for the CG check), a kitchen scale.
- [ ] LaunchControl Pi, firing box, phone, USB‑C cable (log dump), spare LiPo.
- [ ] Hand‑held anemometer.

---

## 3. At the site, before prep

- [ ] Recheck the fire ban today.
- [ ] Wind measured at pad height: **≤ 4 m/s**. Hold if gusting above that.
- [ ] Field clear downwind for **≥ 300 m**: no forest edge, power lines, road, water or livestock
      (Site §6.1–6.2).
- [ ] Pad on bare soil, gravel or a steel plate, never dry grass. Spectators and cars upwind.
- [ ] Range safety officer / club procedures briefed, if flying with SMRK.

---

## 4. Prep table: assemble in this order

**E‑bay (power‑on happens here)**
1. [ ] Sled out of the tube. Parts in their slots and the Qwiic cables seated.
2. [ ] **Battery plug into the ESP32 JST LAST.** This powers the bay on. Listen for the **self‑test
       pass tone**. A fail tone means do not fly; check the battery, flash space and sensors.
3. [ ] Battery voltage read on the LaunchControl status page (or `STATE` on USB): above 3.70 V.
4. [ ] Sled in, **key in the tube groove**, seated on the seat ring.
5. [ ] **Ring v13** screwed on hand‑tight. Turn it so its key slot lines up where the EbayCap tab will drop in.
6. [ ] **EbayCap** on the sled post, **tab in the ring slot**, W M2 × 10 snug.
7. [ ] **Ballast** from §1 fixed on the EbayCap top.
8. [ ] **Nose** screwed on hand‑tight; it presses the 3 spring bumps. **Tape across the nose/ring joint.**
9. [ ] From now on, handle the rocket gently. A jolt above 3 g sustained for 0.1 s counts as a launch:
       the flight computer latches its AP off, and only a power cycle (nose off) re‑arms it.

**Recovery and fin can**
10. [ ] Retention line inspected: no scorching at the fin‑can end, both knots tight.
11. [ ] Bay packed **forward to aft**: canopy against the bulkhead, then the line, then the **Nomex
        over the fin‑can port**. No twists in the shroud lines.
12. [ ] **One wrap of tape on the D9‑5 casing.** Motor into the fin can, rim on the ledge. **Cap on
        hand‑tight, with a witness mark** across the cap and the fin can. The cap is a primary load path.
13. [ ] Fin‑can end of the line on the staple lug.
14. [ ] Fin can in: **tab into the notch, then push until you hear 2 clicks.** About 5 mm of gap at the
        joint means the clocking is wrong.
15. [ ] Gentle pull: the fin can holds (about 0.9 kg).
16. [ ] **Nothing taped over the latch tongues.** They must spring outward to release.

**Final checks**
17. [ ] **Balance check: CG at or forward of the §0 gate** with this motor and this pack.
18. [ ] Static port (⌀1.5) and sound port (⌀3) on the FwdTube are open, not taped.
19. [ ] Fins intact, no cracked fillets, launch lug clear and straight.

---

## 5. At the pad

**Pad**
- [ ] Pad v2 assembled, **all three feet pegged**, and/or 1 kg on the hub tie‑down.
- [ ] Rod vertical or canted **5–10° into the wind**, pointing away from people, roads and the downwind
      hazard.
- [ ] Blast deflector in place, nothing flammable under it.

**Rocket on the rod** (Pad procedure §4)
1. [ ] Slide the rocket down the rod. It rests **fins‑down on the deflector**, with the rotation key on
       the stop post. Check that the cap is clear of the rod.
2. [ ] Rocket vertical and undisturbed.
3. [ ] The flight computer shows as reachable in the LaunchControl status view. If not, stand down: take
       the rocket off the rod, then nose off, unplug and replug the battery (§4 steps 2–8).

**Igniter**
4. [ ] **Physical arm switch OPEN.** Igniter installed per Klima's instructions and held in the nozzle.
5. [ ] Continuity reads OK in the webapp. Arm‑sense reads OPEN.

**Wireless arm** (flight computer re‑zero; Pad procedure §5)
6. [ ] The rocket has been vertical and still since step 2. `/arm` captures the pad baseline.
7. [ ] Send `/arm`. **A dropped connection about 0.5 s later is the expected success.** Do not retry:
       the AP is latched off. If the result is genuinely unclear, stand down and power‑cycle.

**Clear the pad**
8. [ ] Everyone back to the range safe distance. Wind re‑measured: still ≤ 4 m/s.
9. [ ] Sky and airspace clear. Recovery area clear.

---

## 6. Launch (Pad procedure §6)

- [ ] Designated operator closes the physical arm switch.
- [ ] `request_arm()` succeeds: arm‑sense closed **and** continuity OK. If either fails, stand down.
- [ ] Countdown and fire within the **15 s arm window**. If the window expires, re‑arm; don't just press
      fire again.
- [ ] **Misfire:** the fire channel is one‑shot. Open the arm switch and wait out the range's misfire
      period before approaching. Never retry fire on the same arm.
- [ ] Watch the flight: a straight boost, ejection near apogee, and the fin can + canopy coming out the
      aft end. Track the descent and mark the landing bearing.

---

## 7. Do not fly if…

- [ ] Any §0 gate is open (dry rehearsal only).
- [ ] Measured CG is aft of the §0 balance gate, or the margin on the current `.ork` is under 1.5 cal.
- [ ] Wind is over 4 m/s, or the fire ban is in force.
- [ ] Motor is anything but a **Klima D9‑5**. D9‑3 ejects early (about 18 m/s), D9‑7 ejects late (about
      15 m/s), and **D9‑0 / C6‑0 have zero delay and are booster‑only**. A8/B4/C6 were never simulated
      on this vehicle.
- [ ] The fin can does not give **2 clicks** in the keyed clocking, or a latch tongue is stuck or taped.
- [ ] No Nomex over the port, or no tape on the casing.
- [ ] Cap not hand‑tight, or the witness mark is missing.
- [ ] Nose or ring loose or untaped, or the EbayCap tab is not in the ring slot.
- [ ] Self‑test fail tone, battery under 3.70 V, or flash under 5 MB free.
- [ ] The rocket took a hard knock after power‑on and was not power‑cycled.
- [ ] Pad feet not pegged, or the rod is shorter than the §0 figure.
- [ ] Liftoff mass is 500 g or more, so the no‑permit regime no longer applies.

---

## 8. Recovery and post‑flight

- [ ] Wait for the motor to cool before handling the fin can.
- [ ] Recover the body, canopy and fin can: they stay tethered. Note any line or canopy damage.
- [ ] Inspect the **latch tongues and windows** (cracks, white stress marks, heat damage), the gas
      port, the staple lug and the eyelet.
- [ ] Inspect the line near the port for scorching. Re‑sleeve or replace it.
- [ ] Fins and fillets: check for cracks after landing.
- [ ] Remove the spent casing and record any ejection residue in the bay.
- [ ] **Pull the log:** nose off, unplug and replug the battery (the AP is off after launch), then
      `GET /log?n=` or `DUMP n` on USB. Back it up, then `DEL n`.
- [ ] In the log, compare `APOGEE_CONFIRMED` (or `APOGEE_TIMEOUT`) with the ejection spike. A gap far from
      about 0.2 s means the delay or the vehicle model is wrong. Fix that before the next flight.
- [ ] Record apogee, max acceleration, rail‑exit speed (from the log) and descent rate against the v13
      OpenRocket prediction.
- [ ] Between flight days, unscrew the nose to relieve the spring‑beam preload (ABS creep, D9 v3).
- [ ] Clear the LaunchControl fired‑latch before the next launch day.

---

## Flight log

| # | Date | Site | Motor | Wind | Mass (g) | CG (mm) | Ballast (g) | Apogee (m) | Eject vs apogee | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | D9‑5 | | | | | | | first charge test |
| 2 | | | | | | | | | | |

# FreeCAD fit / clearance check — LaunchPad, Ø4 mm steel rod

Checked headless against `LaunchPad.FCStd` (baked solids, FreeCAD 1.1.3 via
`freecadcmd`). Geometry measured off the shapes, not read from
`make_launchpad.py` constants. **No files were modified.**
(The FreeCAD GUI process hung on the first open call — restart it if you have
it open; these results are from a separate headless session.)

## Headline

Three things marked "verified" in `BOM.md`'s fit table — the cradle/post
slip fit and both hinge-pin fits — have **no matching assertion** in
`build_verification.txt`. Checking them now: the two pin fits are fine as
designed; **the cradle has no defined seating height** (below). Same
dead-check pattern the design notes say was fixed for the leg-vs-hub case.

## 1. Ø4 mm rod — is there margin? Yes in CAD, barely.

| Measured | Value |
|---|---|
| Hub bore | Ø4.250 mm, cylindrical, full clamp height Z 0–80 mm |
| Rod (Ø4.000) → bore wall, min gap | **0.125 mm radial (0.250 mm diametral)** |
| Rod ∩ hub solid | 0.0 mm³ |
| Nearest other feature to the rod | cross-screw hole, 1.57 mm away — clear |
| Clamp slit (intended compliance gap) | Z 35–80 mm, 2.0 mm wide; 15 mm solid root below |

**Clamp authority:** taking up the full 0.25 mm of diametral slop needs
roughly 0.4 mm of slit travel at the screw; the slit is 2.0 mm wide, so
there is travel to spare. This part is fine.

**Practical caveat (not a CAD defect):** 0.25 mm diametral is *the entire
margin*, and it is below what an FDM vertical hole in ABS normally holds —
inner-perimeter over-extrusion alone eats 0.1–0.3 mm. (The design notes
credit the 0.25 mm to "ABS shrink"; shrink at Ø4.25 is only ~0.02 mm and is
not the dominant term — as-printed hole undersize is.) The gripping length
(Z 35–80) is a ~300° C-section because of the slit, while the 15 mm root
below it is a full ring, so the two can print to different bores — check the
rod fit along the whole length, not just at the mouth.

**Recommend reaming the bore to ~4.2 mm before first use.** That leaves
~0.2 mm diametral clearance at the rod; the clamp has more than enough slit
travel to close that, so reaming does not cost grip or pointing accuracy.

## 2. Clamp screw threads — they mate, but with ZERO allowance

Measured off the baked shapes:

| | Screw (external) | Hub ear (internal) |
|---|---|---|
| Crest radius | 3.000 mm | — |
| Groove-root radius | — | 3.000 mm |
| Core / minor radius | 2.400 mm | 2.400 mm (crest) |

Screw crest meets nut groove-root at exactly 3.000 mm; screw core meets nut
crest at exactly 2.400 mm. **No radial clearance anywhere, flanks included.**

Interference vs. the hub, screw thread placed at the installed position:

| Rotational phase | Common volume |
|---|---|
| in-phase (what `build_verification.txt` check #2 tests) | 0.0 mm³ |
| rotated ½ pitch (worst case) | 21.6 mm³ overlap |
| rotated ¼ pitch | OCCT boolean returned an invalid solid — non-clean fit, value meaningless |

The `[PASS] screw<->hub thread interference: 0.0000 mm³` line only holds
because both helices are generated from the same equation at the same
transform. A real printed screw started at an arbitrary angle against a real
printed nut lands off-phase and **binds** (½-pitch case: 21.6 mm³ of
material overlap).

**Engagement:** thread is cut 6.0 mm deep into a 6.60 mm ear = 1.0× major
diameter, leaving only **0.60 mm of material behind the last thread**. Thin
for a clamp screw in ABS — forcing a zero-allowance thread into it risks
stripping the ear.

*Recommend:* 0.3 mm diametral clearance on the tapped hole (or shave the
screw major to ~5.7 mm), and deepen the ear so engagement ≥ 1.5× diameter.

The `Assembly` object in the file is a nominal preview, not a validated
mesh — the screw solid sits 292 mm³ inside the ear there.

## 3. Everything else fitting together

| Interface | Measured | Verdict |
|---|---|---|
| Screw shaft Ø6.0 → clearance ear Ø6.40 | 0.40 mm diametral clearance | OK |
| Screw vs rod bore | 1.57 mm gap | OK |
| Hinge pin shaft Ø6.00 → hub lug bore Ø5.80 (×10 mm) | 0.20 mm diametral interference | OK — press fit as intended |
| Hinge pin shaft Ø6.00 → leg tab bore Ø6.30 (×12 mm) | 0.30 mm diametral clearance | OK — running fit |
| Pin shaft length vs lug + tab | 22.0 mm vs 10 + 12 = 22.0 mm | Works, **zero axial margin** — head won't seat if the press stops short |
| Pin flat (0.6 mm) | runs the full 22 mm, through the press zone | Press acts on ~340° not 360° — minor |
| Legs (deployed) ↔ each other | 64 mm | OK |
| Legs (deployed) ↔ hub | 0 mm³ overlap, faces touch at the hinge | OK — lap-joint bearing face |
| Legs (deployed) ↔ cradle | 76 mm | OK |
| Rod ↔ cradle centre hole / U-notch | 1.25 mm | OK |

### Problem: cradle ↔ hub posts have no defined seating height

- Hub posts are **plain Ø8.00 mm cylinders from Z 22 to Z 92 with no
  shoulder or step anywhere** (single cylindrical face, full length). The
  Ø14 root "stub" is at Z 18–22, buried in the flange — a fillet, not a seat.
- Cradle sockets are **Ø8.40 mm through-holes** in the 6 mm base.
- At the design height (cradle underside Z 92) the post top is also Z 92 →
  **0.0 mm socket engagement**. Nothing holds the cradle up there.
- Let go, the cradle slides down the posts (0.2 mm radial play the whole
  way) and — confirmed by stepping it down in FreeCAD — first contacts the
  hub when its underside lands on the **clamp-column top face at Z 80**,
  12 mm below design height. The 12 mm blast-plate air gap goes to **zero**
  and the printed cradle bears directly on the clamp column it is meant to
  stand clear of; the posts then protrude ~6 mm through the sockets.

`BOM.md`'s fit table lists this as *"⌀8.4 / ⌀8.0 — slip fit, cradle lifts off
for transport,"* but there is no check for it anywhere in the build output.

*Recommend:* stepped post — keep Ø8 up to Z 92 as a shoulder the cradle
rests on, then a reduced spigot (≈Ø6) continuing up through a counterbored
socket for lateral location — or replace the through-hole socket with a
blind pocket over a post extended to Z ≈ 98.

# Brag plan — Phoenix 40‑43

**What it is:** a 422 mm, fully 3D‑printed ABS model rocket on a Klima D9‑5 that recovers by letting the motor's own ejection charge shove the fin can off the tail.
**Who for:** model‑rocket and 3D‑printing people.
**What sets it apart:** aft deployment — nose stays on, electronics stay sealed behind a solid bulkhead; no servo, no nichrome, no spring. Recovery joint is a printed snap latch ("push until you hear 2 clicks") because the printed shear pins "came out as blobs".
**Most impressive claim:** OpenRocket: 212 m apogee, charge fires 0.07 s before apogee (7.24 s vs 7.31 s).
**Funniest truth:** electronics sled is on **v19**. And: "Not flight‑proven" (README) → punchline "Flight‑proven: not yet."
**Visual hook:** the real CAD — every part rendered from the project's own STLs — assembling, then the tail kicking off.
**Tone:** default leaning cinematic‑technical: dark charcoal stage, livery colours, big Bahnschrift type.
**Share caption:** see share-copy.txt.

## Visual identity
- Livery from DESIGN.md §10: tan `#D4B991` body, charcoal `#333333` nose, white fins, blaze orange `#F26A1E` accents.
- Background near‑black `#121214`, blueprint grid at 6 % white. Type: Bahnschrift (DIN‑style, local), Consolas for data labels.
- Real meshes: nose v6, FwdTube v8, EbayCap v6, sled ASSEMBLY v19, AftTube v11, fin can v11 + 3 × fin v4, retainer cap v1. Sim trace from `PhoenixABS40-43_D9aft_v6.ork`.

## Storyboard (21 s, 1920×1080, 30 fps)
| # | Time | Scene | On screen |
|---|---|---|---|
| 1 Hook | 0.0–3.0 | Rocket slides up into frame, slow rotate. At 1.4 s the fin can kicks off the tail with a puff. | **"This rocket throws its own tail off."** |
| 2 Reveal | 3.0–7.0 | Camera swings; parts explode apart along the axis with callouts (Nose · E‑bay · Sled v19 · Chute bay · Fin can + D9). | **Phoenix 40‑43** / "Fully 3D‑printed ABS · Klima D9‑5" |
| 3 Deploy | 7.0–11.5 | Left: altitude trace draws to 212 m. Right: small rocket rides the curve; at ejection the tail separates. | "No servo. No nichrome. The motor's own charge pushes the fin can off." + "ejects 0.07 s before apogee" |
| 4 Latch | 11.5–15.0 | Close‑up of AftTube + fin can; fin can slides in, two clicks (orange flash on the latch windows at 60°/240°). | "The printed shear pins came out as blobs." → "So it clicks." |
| 5 Sled | 15.0–18.0 | Sled assembly rotating; version counter flips v1 → v19. | "Electronics sled v19" + "Sealed off from the blast." |
| 6 Outro | 18.0–21.0 | Hero rocket assembled, specs row. | **Phoenix 40‑43** · ⌀43 mm · all ABS · Klima D9‑5 — "Flight‑proven: not yet." |

## Sound
One 21 s track in A minor, ~100 BPM: sub pulse + filtered synth pad building, hi‑hat ticks; a low "whump" for each tail kick (tuned to A), two soft wood‑block clicks (tuned to E) for the latch, quick tick per counter flip at low level; final chord resolve on outro.

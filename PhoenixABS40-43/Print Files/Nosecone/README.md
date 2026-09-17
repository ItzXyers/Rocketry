# Print Files -- Nosecone (fairing-split, servo-latched)

Source: `../../Nosecone/PhoenixABS40-43_Nosecone_v2.py`. Design rationale and
open items: `../../Nosecone/NOSECONE_DESIGN.md`. Supersedes the v1 small-door
design (v1 STLs left in place below for history, not the current build).

```
Nosecone/
  *_v2.stl                    raw per-part model STLs, as exported (un-oriented)
    Spine_v2.stl               fixed half -- full bulkhead+shoulder ring,
                                bonded/screwed to the airframe, print x1
    DoorHalf_v2.stl             hinged/latched petal -- swings open on 3
                                flexure-strip hinge points, print x1
    LatchArm_v2.stl             servo horn attachment (gate) -- print x1,
                                epoxy/screw to a stock SG90 single-arm horn
  *_v1.stl                    superseded small-door design -- kept for history
```

## Not printed -- bought hardware (see NOSECONE_DESIGN.md BOM)

SG90-class 9g servo, 3x spring-steel shim strips (~0.4mm, ~14x10mm each, one
per hinge point), M2 x14 / M3 x3 / M4 x1 fasteners, washers, nut.

## Before printing

- Bench-verify the SG90 footprint on `Spine` (34x14mm pad, holes) against the
  actual servo -- built to a generic footprint, not measured.
- No slicer orientation guidance yet -- Spine is a large, asymmetric part
  (half-shell forward, full ring aft); DoorHalf is a simpler half-shell petal.

## Before flight

- **Latch proof load** -- servo unpowered, push the closed DoorHalf open by
  hand. Must not move (validates the backstop load path).
- **Check the unlatched seam for flutter/gap** away from the single latch
  point (Z=128) -- only one servo-driven latch holds a 182mm-long door edge
  shut; see NOSECONE_DESIGN.md open item 2 if this is a problem.

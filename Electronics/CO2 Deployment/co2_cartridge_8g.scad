// 8g CO2 Cartridge - modeled from manufacturer datasheet (item LE-8NT)
//
// Datasheet values:
//   Overall length        66.0 mm
//   Overall diameter       18.0 mm
//   Neck diameter            8.7 mm
//   Water capacity          10.4 ml
//   Nominal gas fill          7.6 g
//   Filling pressure          8 MPa
//   Total loaded weight       28 g
//
// Body-of-revolution profile (bottom -> top):
//   1. rounded bullet base
//   2. straight cylindrical body
//   3. curved shoulder taper
//   4. short straight neck
//   5. rounded shoulder into a flat strike pad ("smackable" pierce tip - unthreaded)
// Segment heights are a visual approximation of the datasheet photo;
// only overall_length, body_dia and neck_dia come directly from the datasheet.
//
// Units: mm. Requires OpenSCAD 2019.05+ (list comprehensions / let-in-ternary).

// ---- Datasheet parameters ----
overall_length = 66;
body_dia       = 18;
neck_dia       = 8.7;

// ---- Derived / shape parameters ----
body_r = body_dia / 2;
neck_r = neck_dia / 2;

bottom_dome_h = 7;
straight_h    = 38;
shoulder_h    = 13;
neck_h        = 4;
top_dome_h    = overall_length - bottom_dome_h - straight_h - shoulder_h - neck_h; // = 4

tip_flat_dia = 4;               // flat pierce/strike pad at the very top - no threads
tip_flat_r   = tip_flat_dia / 2;

$fn = 96;       // rotational smoothness
profile_steps = 160;

function smoothstep(t) = (t < 0) ? 0 : (t > 1) ? 1 : t * t * (3 - 2 * t);

// height (measured from the start of the tip curve) at which the tip's
// ellipse profile reaches tip_flat_r; beyond that the profile is flat
tip_zt_flat = top_dome_h * sqrt(max(0, 1 - pow(tip_flat_r / neck_r, 2)));

// Radius at height z, measured from the bottom tip (z=0) to the top tip (z=overall_length)
function profile_r(z) =
    (z <= bottom_dome_h) ?
        body_r * sqrt(max(0, 1 - pow((bottom_dome_h - z) / bottom_dome_h, 2)))
    : (z <= bottom_dome_h + straight_h) ?
        body_r
    : (z <= bottom_dome_h + straight_h + shoulder_h) ?
        let(t = (z - bottom_dome_h - straight_h) / shoulder_h)
        body_r - (body_r - neck_r) * smoothstep(t)
    : (z <= bottom_dome_h + straight_h + shoulder_h + neck_h) ?
        neck_r
    :
        let(zt = z - (bottom_dome_h + straight_h + shoulder_h + neck_h))
        (zt <= tip_zt_flat) ?
            neck_r * sqrt(max(0, 1 - pow(zt / top_dome_h, 2)))
        :
            tip_flat_r;

module co2_cartridge_8g() {
    rotate_extrude()
        polygon(points = concat(
            [for (i = [0 : profile_steps])
                let (z = i * overall_length / profile_steps)
                [profile_r(z), z]],
            [[0, overall_length]]   // cap the flat strike pad back to the axis
        ));
}

co2_cartridge_8g();

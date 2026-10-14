# -*- coding: utf-8 -*-
"""
Overhang audit for FDM parts printed with +Z up (sled: aft end on the bed).

2026-10-14 (sled v10): the v9 print spaghettified under the deck ceiling (mid ring + piezo
roof), under the reed rails and under the top beam / EbayCap bosses.  eSUN ABS runs with the
part fan ~0 on the X1C, so anything facing down steeper than ~45 deg (bridges, cantilevers,
pendant starts) sags.

Method: mesh the solid, take every facet whose outward normal points down more than
OVH_ANGLE from vertical (n.z < -cos(OVH_ANGLE)), drop the ones on the bed, and cluster the
rest by shared vertices.  Each cluster = one downward-facing region; it is reported with
its area, Z and footprint.  Small ones (horizontal hole crowns, chamfer seams) are "ok".

Standalone:  set OVH_STEP=<file.step> and run with freecadcmd.
In a sled script:  exec this file, call overhang_audit(shape, log.append).
"""
import os
import math

OVH_ANGLE = 46.0          # deg from vertical; the 1:1.15 knee braces (49 deg) pass, a 45 deg face is borderline
OVH_MIN_AREA = 2.0        # mm2 -- below this a cluster is "ok (small)"
OVH_MIN_SPAN = 2.0        # mm  -- a cluster narrower than this in x AND y bridges/flows fine


def _reach(shape, facets, nmax=60):
    """worst horizontal distance from a flat downward facet to sled material 0.3 mm below it = how far
    the first layer of that face has to span / hang in air (a bridge of span L gives ~L/2)"""
    import Part
    from FreeCAD import Vector
    z = sum(p[2] for f in facets for p in f.Points) / (3.0 * len(facets))
    xs = [p[0] for f in facets for p in f.Points]; ys = [p[1] for f in facets for p in f.Points]
    below = shape.common(Part.makeBox(max(xs) - min(xs) + 40, max(ys) - min(ys) + 40, 0.1,
                                      Vector(min(xs) - 20, min(ys) - 20, z - 0.35)))
    if not below.Solids:
        return 99.0
    pts = []
    for f in sorted(facets, key=lambda f: -f.Area)[:nmax]:
        pts.append(Vector(*[sum(p[i] for p in f.Points) / 3.0 for i in range(3)]))
        pts += [Vector(*p) for p in f.Points]
    return max(below.distToShape(Part.Vertex(Vector(q.x, q.y, z - 0.3)))[0] for q in pts)


def overhang_clusters(shape, zbed=None, deflection=0.05):
    import MeshPart
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=deflection, AngularDeflection=0.3, Relative=False)
    zbed = shape.BoundBox.ZMin if zbed is None else zbed
    lim = -math.cos(math.radians(OVH_ANGLE))
    pts = m.Points
    sel = []
    for f in m.Facets:
        n = f.Normal
        if n.z >= lim:
            continue
        zc = sum(p[2] for p in f.Points) / 3.0
        if zc < zbed + 0.05:
            continue
        sel.append(f)
    # union-find over shared point indices
    parent = {}
    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent.setdefault(parent[a], parent[a]); a = parent[a]
        return a
    for f in sel:
        i0 = f.PointIndices[0]
        for i in f.PointIndices[1:]:
            ra, rb = find(i0), find(i)
            if ra != rb: parent[ra] = rb
    cl = {}
    for f in sel:
        cl.setdefault(find(f.PointIndices[0]), []).append(f)
    out = []
    for fs in cl.values():
        xs = [p[0] for f in fs for p in f.Points]; ys = [p[1] for f in fs for p in f.Points]; zs = [p[2] for f in fs for p in f.Points]
        a = sum(f.Area for f in fs)
        fl = [f for f in fs if f.Normal.z < -0.97]
        out.append(dict(area=a, x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), z0=min(zs), z1=max(zs),
                        flat=sum(f.Area for f in fl), reach=_reach(shape, fl) if sum(f.Area for f in fl) >= OVH_MIN_AREA else 0.0))
    out.sort(key=lambda c: -c['area'])
    return out


def overhang_audit(shape, P, zbed=None, title="[O] OVERHANGS"):
    cs = overhang_clusters(shape, zbed)
    P("%s  (print +Z up, aft end on the bed; faces steeper than %.0f deg from vertical, bed excluded;" % (title, OVH_ANGLE))
    P("    'flat' = the part of it within 14 deg of horizontal, i.e. true bridge / cantilever / pendant)")
    big = [c for c in cs if c['area'] >= OVH_MIN_AREA and max(c['x1'] - c['x0'], c['y1'] - c['y0']) >= OVH_MIN_SPAN]
    for c in big:
        P("  area %6.1f mm2 (flat %6.1f, reach %4.1f mm)  Z %6.1f..%6.1f  x %6.1f..%6.1f  y %6.1f..%6.1f"
          % (c['area'], c['flat'], c['reach'], c['z0'], c['z1'], c['x0'], c['x1'], c['y0'], c['y1']))
    small = len(cs) - len(big)
    tot = sum(c['area'] for c in big); flat = sum(c['flat'] for c in big)
    P("  %d regions >= %.0f mm2 (total %.0f mm2, flat %.0f mm2); %d small ones (hole crowns etc.) not listed"
      % (len(big), OVH_MIN_AREA, tot, flat, small))
    rr = sorted((c['reach'] for c in big), reverse=True)
    P("  'reach' = worst horizontal distance from a flat downward face to material 0.3 mm under it (first layer in air);")
    P("  largest reaches: %s mm" % ", ".join("%.1f" % r for r in rr[:6]))
    return big


if __name__ in ("__main__",) or os.environ.get("OVH_STEP"):
    import Part
    fn = os.environ.get("OVH_STEP")
    if fn:
        s = Part.Shape(); s.read(fn)
        lines = []
        overhang_audit(s, lines.append, title="[O] OVERHANGS  %s" % os.path.basename(fn))
        print("\n".join(lines))

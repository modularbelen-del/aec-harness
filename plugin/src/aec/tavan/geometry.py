# -*- coding: utf-8 -*-
"""Ceiling colour zones next to panel fields (shapely, CPython only). Values are millimetres.

    find_wedges(zone, pieces, ...)             -> wedge / sliver panel pieces (> 3 deg off or < 120 mm wide)
    absorb_wedges(zone, wedges)                -> zone taking the wedges
    cut_back(layer, zones, add)                -> dark profile layer stopped inside the zones
    step_closures(zone_new, wedges, walls, higher) -> closure walls to delete / trim / add at a height step
    straighten_border(zone, panels, direction) -> zone/panel border as ONE straight (radial) line
    piece_width(piece)                         -> short side of the minimum rotated rectangle
    scan_wedges(pieces, ...)                   -> independent scan: pieces < 120 mm wide or > 3 deg off their grid
    merge_slivers(pieces, ...)                 -> strips < 120 mm wide join the neighbour they share the longest edge with
    absorb_strip(strip, pieces)                -> a tapering edge strip shared out along the joints; pieces reach the edge whole
Every function raises GeometryError with a location instead of guessing.
"""
from __future__ import division

from aec.geom.curves import (GeometryError, _add, _adiff, _dir_deg, _dist, _dot, _left, _shp, _unit, _v, _vec_deg,
                             polygon_to_region, region_to_polygon)

def piece_width(piece):
    """Short side of the minimum rotated rectangle (mm): how wide a panel piece really is."""
    q = region_to_polygon(piece).minimum_rotated_rectangle
    c = list(q.exterior.coords) if q.geom_type == "Polygon" else []
    if len(c) < 4:
        return 0.0
    return min(_dist(c[0], c[1]), _dist(c[1], c[2]))


def find_wedges(zone, pieces, column_dir=None, leds=None, angle_tol_deg=3.0, min_width_mm=120.0,
                max_area_mm2=4.5e6, touch_mm=6.0, min_edge_mm=300.0, led_reach_mm=3500.0, led_parallel_deg=25.0,
                need_column_edge=True, column_edge_mm=800.0):
    """Wedges: panel pieces next to a colour zone that are wedges or slivers.
    pieces: {key: region|polygon}. A piece touching the zone (<= touch_mm) is a wedge when an edge facing the
    zone (longer than min_edge_mm) is >= angle_tol_deg off the panel column direction, or the piece is narrower
    than min_width_mm. The column direction is `column_dir` (vector or degrees) or, per piece, the nearest light
    line (leds: [(p0, p1)]) within led_reach_mm that runs within led_parallel_deg of the piece's longest edge (a
    crossing light line nearby is not the column line). With need_column_edge the far side of the wedge must be a
    long edge on the column direction (it becomes the new border). Pieces larger than max_area_mm2 are never
    wedges. Returns [{"key", "angle_off_deg", "width_mm", "area_mm2", "column_edge", "at"}]."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    zp = region_to_polygon(zone)
    if column_dir is not None and not isinstance(column_dir, (int, float)):
        column_dir = _vec_deg(column_dir)
    out = []
    for key, pc in pieces.items():
        pp = region_to_polygon(pc)
        if pp.is_empty or pp.distance(zp) > touch_mm or pp.area > max_area_mm2:
            continue
        cs = list(pp.exterior.coords)
        edges = [(cs[i], cs[i + 1]) for i in range(len(cs) - 1)]
        fe = [e for e in edges if _dist(*e) > min_edge_mm and
              Point((e[0][0] + e[1][0]) / 2.0, (e[0][1] + e[1][1]) / 2.0).distance(zp) < touch_mm]
        if not fe:
            continue
        cdir = column_dir
        if cdir is None:
            le = max(edges, key=lambda e: _dist(*e))
            ll = [l for l in (leds or []) if LineString([l[0], l[1]]).distance(pp) < led_reach_mm
                  and not zp.buffer(50).contains(Point(*l[0])) and _adiff(_dir_deg(l[0], l[1]), _dir_deg(*le)) < led_parallel_deg]
            if not ll:
                continue
            lf = min(ll, key=lambda l: LineString([l[0], l[1]]).distance(pp))
            cdir = _dir_deg(lf[0], lf[1])
        off = max(_adiff(_dir_deg(*e), cdir) for e in fe)
        w = piece_width(pp)
        if off < angle_tol_deg and w >= min_width_mm:
            continue
        ce = [e for e in edges if _dist(*e) > column_edge_mm and
              Point((e[0][0] + e[1][0]) / 2.0, (e[0][1] + e[1][1]) / 2.0).distance(zp) > 20 and _adiff(_dir_deg(*e), cdir) < angle_tol_deg]
        if need_column_edge and not ce:
            continue
        c = pp.representative_point()
        best = max(ce, key=lambda e: _dist(*e)) if ce else None
        out.append({"key": key, "angle_off_deg": round(off, 2), "width_mm": round(w, 1), "area_mm2": round(pp.area),
                    "column_edge": [list(best[0]), list(best[1])] if best else None, "at": [c.x, c.y]})
    return out


def absorb_wedges(zone, wedges, close_mm=3.2):
    """Wedges: the zone takes the wedge pieces (their 2 mm joints close). Returns one shapely Polygon or
    raises GeometryError when the result is not one piece."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    zp = region_to_polygon(zone)
    nz = unary_union([zp.buffer(close_mm, join_style=2)] + [region_to_polygon(w).buffer(close_mm, join_style=2) for w in wedges]).buffer(-close_mm, join_style=2)
    if nz.geom_type != "Polygon":
        c = zp.representative_point()
        raise GeometryError("zone and wedges are not one piece", (c.x, c.y))
    return nz


def cut_back(layer, zones, add=None, inset_mm=1.0, add_grow_mm=2.5, add_reach_mm=800.0, min_part_mm2=5e3, min_change_mm2=1e3):
    """The dark profile layer above a panel field: grown over the (new) panels `add` incl. their joints (within
    add_reach_mm of the old layer) and stopped inset_mm inside the colour zones, so no layer edge shows through a
    zone and no joint of a new panel opens onto the slab. Returns the list of part polygons, or None when the
    layer does not change."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    pk = region_to_polygon(layer)
    NZ = unary_union([region_to_polygon(z).buffer(-inset_mm, join_style=2) for z in zones]) if zones else Polygon()
    new = pk
    if add:
        grow = unary_union([region_to_polygon(a).buffer(add_grow_mm, join_style=2) for a in add])
        new = unary_union([pk, grow.intersection(pk.buffer(add_reach_mm))])
    new = new.difference(NZ)
    if new.symmetric_difference(pk).area < min_change_mm2:
        return None
    return [g for g in getattr(new, "geoms", [new]) if g.geom_type == "Polygon" and g.area > min_part_mm2]


def step_closures(zone_new, wedges, walls, higher, offset_mm=7.5, run_on_mm=18.0, trim_run_on_mm=23.0,
                  min_edge_mm=200.0, near_mm=15.0):
    """Step closures: closure walls (AT_Alın) of a lower colour zone after it absorbed wedges of a higher field.
    walls: [{"id", "p0", "p1"}] existing closure axes near the old boundary; higher: regions of the higher
    ceilings. A wall that now has the new zone on both sides is deleted, or cut back (its kept end runs on
    trim_run_on_mm to close the corner). Every wedge edge that now faces a higher ceiling gets a new closure:
    axis offset_mm inside the zone (face on the zone edge), both ends run on run_on_mm.
    Returns {"delete": [ids], "trim": [{"id", "p0", "p1"}], "new": [{"p0", "p1"}]}."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    nz = region_to_polygon(zone_new)
    wg = [region_to_polygon(w) for w in wedges]
    WU = unary_union(wg)
    hi = [region_to_polygon(h) for h in higher]
    dels, trims, news = [], [], []
    for w in walls:
        L = LineString([w["p0"], w["p1"]])
        if L.distance(WU) > near_mm:
            continue
        inner = L.intersection(WU.buffer(near_mm, join_style=2))
        if inner.length < 50:
            continue
        mid = inner.interpolate(0.5, normalized=True)
        d = _unit(_v(w["p0"], w["p1"]))
        n = _left(d)
        s1, s2 = Point(mid.x + n[0] * 25, mid.y + n[1] * 25), Point(mid.x - n[0] * 25, mid.y - n[1] * 25)
        if not (nz.buffer(3).contains(s1) and nz.buffer(3).contains(s2)):
            continue
        keep = L.difference(WU.buffer(near_mm, join_style=2))
        keep = [g for g in getattr(keep, "geoms", [keep]) if g.length > 100]
        if not keep:
            dels.append(w["id"])
            continue
        g = max(keep, key=lambda g: g.length)
        c0, c1 = g.coords[0], g.coords[-1]
        dg = _unit(_v(c0, c1))
        if Point(*c1).distance(WU) < Point(*c0).distance(WU):
            c1 = _add(c1, dg, trim_run_on_mm)
        else:
            c0 = _add(c0, dg, -trim_run_on_mm)
        trims.append({"id": w["id"], "p0": list(c0), "p1": list(c1)})
    inner_z = nz.buffer(-5)
    for pp in wg:
        cs = list(pp.exterior.coords)
        for i in range(len(cs) - 1):
            a, b = cs[i], cs[i + 1]
            if _dist(a, b) < min_edge_mm:
                continue
            m = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
            d = _unit(_v(a, b))
            n = _left(d)
            pa, pb = Point(m[0] + n[0] * 20, m[1] + n[1] * 20), Point(m[0] - n[0] * 20, m[1] - n[1] * 20)
            ina, inb = inner_z.contains(pa), inner_z.contains(pb)
            if ina and not nz.buffer(3).contains(pb):
                out_pt, into = pb, n
            elif inb and not nz.buffer(3).contains(pa):
                out_pt, into = pa, (-n[0], -n[1])
            else:
                continue
            if not any(h.buffer(3).contains(out_pt) for h in hi):
                continue
            p0 = _add(_add(a, into, offset_mm), d, -run_on_mm)
            p1 = _add(_add(b, into, offset_mm), d, run_on_mm)
            news.append({"p0": list(p0), "p1": list(p1)})
    return {"delete": dels, "trim": trims, "new": news}


def _halfplane(p0, d, side_pt, big=1e6):
    Polygon = _shp()[0]
    n = _left(d)
    if _dot(_v(p0, side_pt), n) < 0:
        n = (-n[0], -n[1])
    a, b = _add(p0, d, -big), _add(p0, d, big)
    return Polygon([a, b, _add(b, n, big), _add(a, n, big)])


def straighten_border(zone, panels, direction, joint_mm=2.0, sliver_mm2=2e4, cross_deg=20.0, straight_mm=3.0,
                      touch_mm=6.0, min_border_mm=800.0, close_mm=3.2):
    """Straight border: every border between a colour zone and the panels next to it (same height) becomes ONE straight
    line in `direction` (a vector, or a function (border_mid, border_deg) -> vector, e.g. radial_direction of
    the corridor wall; border_deg is the direction of the border's longest segment, to reject crossing lights;
    None skips that border)
    through the length-weighted middle of the current border. The zone and the panels are rebuilt on that line
    with a joint_mm joint; zone parts beyond the line go to the panel they face (split at the panel joints). A
    panel left smaller than sliver_mm2 beyond the line is removed and its speck joins the neighbour it touches
    most. panels: {key: region|polygon} of the same-height pieces near the zone (neighbours of the touching
    pieces included: they can take specks).
    Returns {"zone": Polygon, "panels": {key: Polygon}, "removed": [keys], "sides": [{"keys", "dev_mm",
    "status"}]}; only changed panels are listed. A side whose outlines cannot be rebuilt is left as it was."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    zp = region_to_polygon(zone)
    P = dict((k, region_to_polygon(v)) for k, v in panels.items())
    changed, removed, sides = {}, [], []

    def cur(k):
        return changed.get(k, P[k])
    adj = [k for k in P if not cur(k).is_empty and cur(k).distance(zp) < touch_mm]
    if not adj:
        return {"zone": zp, "panels": {}, "removed": [], "sides": [{"keys": [], "dev_mm": None, "status": "skip: no panels"}]}
    Ua = unary_union([cur(k).buffer(3, join_style=2) for k in adj])
    for side in getattr(Ua, "geoms", [Ua]):
        grp = [k for k in adj if k not in removed and cur(k).buffer(3, join_style=2).intersects(side)]
        S = zp.exterior.intersection(side.buffer(touch_mm, join_style=2))
        if S.is_empty:
            sides.append({"keys": grp, "dev_mm": None, "status": "skip: empty border"})
            continue
        S = linemerge(S) if S.geom_type == "MultiLineString" else S
        if S.geom_type != "LineString" or S.length < min_border_mm:
            sides.append({"keys": grp, "dev_mm": None, "status": "skip: border %s %.0f" % (S.geom_type, S.length)})
            continue
        smid = S.interpolate(0.5, normalized=True)
        sc = list(S.coords)
        bdir = _dir_deg(*max(zip(sc[:-1], sc[1:]), key=lambda e: _dist(*e)))
        d = direction((smid.x, smid.y), bdir) if callable(direction) else direction
        if d is None:
            sides.append({"keys": grp, "dev_mm": None, "status": "skip: no direction"})
            continue
        d = _unit(d)
        segs = [LineString([a, b]) for a, b in zip(list(S.coords)[:-1], list(S.coords)[1:])
                if _dist(a, b) > 1 and _adiff(_dir_deg(a, b), _vec_deg(d)) < cross_deg]
        SL = []
        if segs:
            m2 = unary_union(segs)
            m2 = linemerge(m2) if m2.geom_type == "MultiLineString" else m2
            SL = [g for g in getattr(m2, "geoms", [m2]) if g.length > 100]
        tot = sum(g.length for g in SL)
        if tot < min_border_mm:
            sides.append({"keys": grp, "dev_mm": None, "status": "skip: short cross border"})
            continue
        mid = (sum(g.interpolate(0.5, normalized=True).x * g.length for g in SL) / tot,
               sum(g.interpolate(0.5, normalized=True).y * g.length for g in SL) / tot)
        n = _left(d)
        dev = max(abs(_dot(_v(mid, pt), n)) for g in SL for pt in g.coords)
        if dev < straight_mm:
            sides.append({"keys": grp, "dev_mm": round(dev, 2), "status": "straight"})
            continue
        zpt = zp.representative_point().coords[0]
        sv = n if _dot(_v(zpt, mid), n) > 0 else (-n[0], -n[1])           # from the zone towards the panels
        Hz = _halfplane(mid, d, zpt)
        band = unary_union([zp] + [cur(k) for k in grp]).buffer(close_mm, join_style=2).buffer(-close_mm, join_style=2)
        new_z = unary_union([zp.buffer(close_mm, join_style=2), band.intersection(Hz).buffer(close_mm, join_style=2)]).buffer(-close_mm, join_style=2).intersection(Hz)
        new_z = new_z.difference(Hz.difference(band.union(zp)))
        if new_z.geom_type != "Polygon":
            gs = [g for g in getattr(new_z, "geoms", [new_z]) if g.area > 1e3]
            if len(gs) != 1:
                sides.append({"keys": grp, "dev_mm": round(dev, 2), "status": "skip: new zone not one polygon"})
                continue
            new_z = gs[0]
        give = zp.difference(Hz)
        Hp = _halfplane(_add(mid, sv, joint_mm), d, _add(mid, sv, 1000.0))
        newp = dict((k, cur(k).intersection(Hp)) for k in grp)
        for g in getattr(give, "geoms", [give]):
            if g.area < 1e3:
                continue
            parts = [g]
            for i, k1 in enumerate(grp):                    # split at the joints between the side's panels
                for k2 in grp[i + 1:]:
                    j = cur(k1).buffer(2.5, join_style=2).intersection(cur(k2).buffer(2.5, join_style=2))
                    if j.is_empty or j.area < 10:
                        continue
                    cc = list(j.minimum_rotated_rectangle.exterior.coords)
                    e = max([(cc[q], cc[q + 1]) for q in range(4)], key=lambda e: _dist(*e))
                    ed = _unit(_v(*e))
                    em = j.centroid.coords[0]
                    cut = LineString([_add(em, ed, -5000), _add(em, ed, 5000)]).buffer(joint_mm / 2.0, cap_style=2)
                    parts = [q for part in parts for q in getattr(part.difference(cut), "geoms", [part.difference(cut)]) if q.area > 100]
            for q in parts:
                best = max(grp, key=lambda k: q.buffer(4).intersection(cur(k)).area + q.buffer(4).intersection(newp[k]).area)
                newp[best] = unary_union([newp[best].buffer(close_mm, join_style=2), q.buffer(close_mm, join_style=2)]).buffer(-close_mm, join_style=2).intersection(Hp)
        gone = []
        for k in list(newp):                               # slivers: removed, their speck joins a neighbour
            p = newp[k]
            if p.is_empty or p.area < sliver_mm2:
                cands = [c for c in P if c != k and c not in removed and c not in gone
                         and not newp.get(c, cur(c)).is_empty and newp.get(c, cur(c)).area >= sliver_mm2]
                if not cands:
                    continue
                if not p.is_empty:
                    c = max(cands, key=lambda c: p.buffer(4).intersection(newp.get(c, cur(c))).area)
                    newp[c] = unary_union([newp.get(c, cur(c)).buffer(close_mm, join_style=2), p.buffer(close_mm, join_style=2)]).buffer(-close_mm, join_style=2).intersection(Hp)
                gone.append(k)
        for k in gone:
            newp.pop(k, None)
        try:
            if any(p.geom_type != "Polygon" for p in newp.values()):
                raise GeometryError("panel not one polygon")
            polygon_to_region(new_z)
            for p in newp.values():
                polygon_to_region(p)
        except GeometryError as e:
            sides.append({"keys": grp, "dev_mm": round(dev, 2), "status": "skip: rebuild failed (%s)" % e})
            continue
        zp = new_z
        changed.update(newp)
        for k in gone:
            changed.pop(k, None)
            removed.append(k)
        sides.append({"keys": sorted(newp), "dev_mm": round(dev, 2), "status": "straightened", "removed": gone})
    return {"zone": zp, "panels": dict((k, v) for k, v in changed.items() if k not in removed), "removed": removed, "sides": sides}


def scan_wedges(pieces, ref_dir=None, min_width_mm=120.0, angle_tol_deg=3.0, min_edge_mm=300.0, reach_mm=3000.0,
                max_skew_deg=45.0, skip=None):
    """Independent wedge scan of ceiling pieces (panels, gypsum pieces) of one level:
    a piece is suspect when it is narrower than min_width_mm, or when one of its edges longer than min_edge_mm runs
    more than angle_tol_deg (and less than max_skew_deg, so real diagonal fields are not flagged) off the grid of
    its field. The grid direction is `ref_dir` (vector or degrees) or, per piece, the length-weighted dominant edge
    direction (modulo 90 deg) of the pieces within reach_mm. skip: keys not to report (e.g. curved bands).
    Returns [{"key", "reason": "narrow"|"angle", "width_mm", "angle_off_deg", "at", "edge"}]."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    from shapely.strtree import STRtree
    keys = [k for k in pieces]
    pg = [region_to_polygon(pieces[k]) for k in keys]
    edges = []
    for p in pg:
        cs = list(p.exterior.coords) if p.geom_type == "Polygon" else []
        edges.append([(cs[i], cs[i + 1]) for i in range(len(cs) - 1) if _dist(cs[i], cs[i + 1]) > min_edge_mm])
    tree = STRtree(pg)
    if ref_dir is not None and not isinstance(ref_dir, (int, float)):
        ref_dir = _vec_deg(ref_dir)
    out = []
    for i, k in enumerate(keys):
        if skip and k in skip:
            continue
        p = pg[i]
        if p.is_empty:
            continue
        c = p.representative_point()
        w = piece_width(p)
        if w < min_width_mm:
            out.append({"key": k, "reason": "narrow", "width_mm": round(w, 1), "angle_off_deg": None, "at": [c.x, c.y], "edge": None})
            continue
        ref = ref_dir
        if ref is None:
            hist = {}
            for j in tree.query(p.buffer(reach_mm)):
                for e in edges[int(j)]:
                    a = round(_dir_deg(*e) % 90.0 * 4) / 4.0            # 0.25 deg bins, modulo 90
                    hist[a] = hist.get(a, 0.0) + _dist(*e)
            if not hist:
                continue
            ref = max(hist, key=lambda a: sum(v for b, v in hist.items() if min(abs(a - b), 90 - abs(a - b)) <= 0.5))
        worst = None
        for e in edges[i]:
            off = min(_adiff(_dir_deg(*e), ref), _adiff(_dir_deg(*e), ref + 90.0))
            if angle_tol_deg < off < max_skew_deg and (worst is None or off > worst[0]):
                worst = (off, e)
        if worst:
            out.append({"key": k, "reason": "angle", "width_mm": round(w, 1), "angle_off_deg": round(worst[0], 2), "at": [c.x, c.y],
                        "edge": [list(worst[1][0]), list(worst[1][1])]})
    return out


def merge_slivers(pieces, slivers=None, min_width_mm=120.0, min_len_mm=300.0, joint_mm=2.0, close_mm=3.2, allowed=None):
    """Slivers (pieces narrower than min_width_mm and at least min_len_mm long, or the keys given in `slivers`) join
    the neighbour they share the longest edge with (within joint_mm + 1): a panel strip left at a field edge becomes
    part of the last whole panel of its column, a thin gypsum strip between a colour zone and its neighbour becomes
    part of the zone. allowed(sliver_key, neighbour_key) -> bool limits the pairs (same type and height, zone only,
    ...). The merged outline keeps joint_mm to every other piece. pieces: {key: region|polygon}.
    Returns {"merged": {key: Polygon}, "removed": [keys], "skipped": [[key, reason]]}."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    P = dict((k, region_to_polygon(v)) for k, v in pieces.items())
    if slivers is None:
        slivers = []
        for k, p in P.items():
            if p.is_empty or p.geom_type != "Polygon":
                continue
            c = list(p.minimum_rotated_rectangle.exterior.coords)
            if len(c) < 4:
                continue
            a, b = _dist(c[0], c[1]), _dist(c[1], c[2])
            if min(a, b) < min_width_mm and max(a, b) >= min_len_mm:
                slivers.append(k)
    cur = dict(P)
    merged, removed, skipped = {}, [], []
    for s in sorted(slivers, key=lambda k: P[k].area):
        sp = cur.get(s)
        if sp is None or sp.is_empty:
            continue
        near = [k for k in cur if k != s and k not in removed and cur[k].distance(sp) < joint_mm + 1.0
                and (allowed is None or allowed(s, k))]
        if not near:
            skipped.append([s, "no neighbour"])
            continue
        edge = lambda k: sp.buffer(joint_mm + 1.0, join_style=2).intersection(cur[k].exterior).length
        k = max(near, key=edge)
        if edge(k) < 50:
            skipped.append([s, "touches its neighbours only at a corner"])
            continue
        m = unary_union([cur[k].buffer(close_mm, join_style=2), sp.buffer(close_mm, join_style=2)]).buffer(-close_mm, join_style=2)
        others = [cur[o] for o in cur if o not in (k, s) and o not in removed and cur[o].distance(m) < joint_mm + 1.0]
        if others:
            m = m.difference(unary_union([o.buffer(joint_mm, join_style=2) for o in others]))
        if m.geom_type != "Polygon":
            parts = [g for g in getattr(m, "geoms", [m]) if g.area > 1.0]
            if len(parts) != 1:
                skipped.append([s, "merged piece not one polygon"])
                continue
            m = parts[0]
        try:
            polygon_to_region(m)
        except GeometryError as e:
            skipped.append([s, "outline: %s" % e])
            continue
        cur[k] = m
        merged[k] = m
        removed.append(s)
        cur.pop(s, None)
        merged.pop(s, None)
    return {"merged": merged, "removed": removed, "skipped": skipped}


def absorb_strip(strip, pieces, close_mm=3.2, touch_mm=3.0, pair_mm=120.0, min_part_mm2=100.0):
    """A leftover strip along the edge of a panel field (a crescent between the field and a curved edge, a wedge band)
    is shared out: every joint between two neighbouring edge pieces is run on across the strip with its own width
    (2 mm joint, or the slot of a light line), and each part joins the piece it lies in front of. The pieces then
    reach the edge whole; no separate tapering strip is left. pieces: {key: region|polygon}.
    Returns {"pieces": {key: Polygon} (changed ones), "gaps": [{"keys", "width_mm", "axis": [p0, p1]}] (joint
    extensions across the strip, e.g. to continue a light line or place a filler), "left": Polygon (unassigned)}."""
    Polygon, LineString, Point, unary_union, linemerge = _shp()
    sp = region_to_polygon(strip)
    P = dict((k, region_to_polygon(v)) for k, v in pieces.items())
    adj = [k for k, p in P.items() if p.distance(sp) < touch_mm and sp.buffer(touch_mm, join_style=2).intersection(p.exterior).length > 50]
    cuts, gaps = [], []
    for i, a in enumerate(adj):
        for b in adj[i + 1:]:
            g = P[a].distance(P[b])
            if g > pair_mm:
                continue
            h = g / 2.0 + 0.5
            j = P[a].buffer(h, join_style=2).intersection(P[b].buffer(h, join_style=2))
            if j.is_empty or j.area < 1:
                continue
            cc = list(j.minimum_rotated_rectangle.exterior.coords)
            e = max([(cc[q], cc[q + 1]) for q in range(4)], key=lambda e: _dist(*e))
            ed = _unit(_v(*e))
            em = j.centroid.coords[0]
            ray = LineString([_add(em, ed, -20000), _add(em, ed, 20000)])
            cut = ray.buffer(max(g, 0.2) / 2.0, cap_style=2).intersection(sp.buffer(1.0))
            if cut.is_empty:
                continue
            cuts.append(cut)
            ax_ = ray.intersection(sp)
            if not ax_.is_empty:
                cs = [c for q in getattr(ax_, "geoms", [ax_]) for c in q.coords]
                far = max(cs, key=lambda c: _dist(c, em))
                near = min(cs, key=lambda c: _dist(c, em))
                gaps.append({"keys": [a, b], "width_mm": round(g, 1), "axis": [list(near), list(far)]})
    CU = unary_union(cuts) if cuts else Polygon()
    rest = sp.difference(CU)
    new = dict((k, P[k]) for k in adj)
    left = []
    for q in getattr(rest, "geoms", [rest]):
        if q.geom_type != "Polygon" or q.area < min_part_mm2:
            continue
        k = max(adj, key=lambda k: q.buffer(touch_mm + 1.0, join_style=2).intersection(P[k].exterior).length) if adj else None
        if k is None or q.buffer(touch_mm + 1.0, join_style=2).intersection(P[k].exterior).length < 20:
            left.append(q)
            continue
        new[k] = unary_union([new[k].buffer(close_mm, join_style=2), q.buffer(close_mm, join_style=2)]).buffer(-close_mm, join_style=2)
    out = {}
    for k in adj:
        m = new[k].difference(CU)
        others = [new[o] for o in adj if o != k]
        if others:
            m = m.difference(unary_union([o.buffer(0.5, join_style=2) for o in others]))
        if m.geom_type != "Polygon":
            m = max(getattr(m, "geoms", [m]), key=lambda q: q.area)
        if m.symmetric_difference(P[k]).area > 1.0:
            out[k] = m
    return {"pieces": out, "gaps": gaps, "left": unary_union(left) if left else Polygon()}

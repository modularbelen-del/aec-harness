# -*- coding: utf-8 -*-
"""Exact 2D line/arc geometry in millimetres, shared by every aec module.

All values are millimetres in plan (WCS x, y). Arcs stay arcs; nothing here
replaces an arc by chords except sample(), which is only used for area and
containment tests.

Curve dicts:
    {"t": "line", "p0": [x, y], "p1": [x, y]}
    {"t": "arc", "c": [x, y], "r": r, "a0": deg, "a1": deg, "ccw": bool}
      (runs from angle a0 to a1; ccw=True means increasing angle)

Public functions:
    dwg_unit_to_mm(insunits)
    join_curves(curves, tol_mm=1.0)            -> loops, regions, open ends
    extend_to_boundary(p0, p1, region, ...)    -> axis end points on the boundary
    trim_to_boundary(p0, p1, width, region)    -> element outline cut along the edge
    offset_chain(curves, dist, closed)         -> mitred offset of a loop or chain
    fascia_band(curves, thickness, closed)     -> one continuous fascia profile
    refit_arcs(points, tol_mm)                 -> lines+arcs from a flattened polyline
    loop_area(curves), point_in_region(pt, region), sample(curve)
  shapely bridge (CPython only):
    region_to_polygon(r), polygon_to_region(pg), radial_direction(p0, pm, p1, at)
Every function raises GeometryError with a location instead of guessing.
Ceiling-specific zone tools (wedges, slivers, borders) live in aec.tavan.geometry.
"""
from __future__ import division
import math

EPS = 1e-9
SHORT_CURVE_MM = 0.78  # Revit Application.ShortCurveTolerance (0.00256 ft)
CLOSE_TOL_MM = 0.01    # end points closer than this are the same point after snapping


class GeometryError(Exception):
    def __init__(self, msg, at=None):
        Exception.__init__(self, msg if at is None else "%s at (%.1f, %.1f)" % (msg, at[0], at[1]))
        self.at = at


# ---------------------------------------------------------------- units
_INSUNITS_MM = {1: 25.4, 2: 304.8, 4: 1.0, 5: 10.0, 6: 1000.0, 14: 100.0}


def dwg_unit_to_mm(insunits):
    """Factor from DWG drawing units to mm. Example: INSUNITS=5 (cm) -> 10."""
    try:
        return _INSUNITS_MM[int(insunits)]
    except (KeyError, TypeError, ValueError):
        raise GeometryError("INSUNITS=%r is not a supported length unit; set it explicitly" % (insunits,))


# ---------------------------------------------------------------- vectors
def _v(a, b):
    return (b[0] - a[0], b[1] - a[1])


def _add(a, b, s=1.0):
    return (a[0] + s * b[0], a[1] + s * b[1])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _norm(a):
    return math.hypot(a[0], a[1])


def _unit(a):
    n = _norm(a)
    if n < EPS:
        raise GeometryError("zero-length direction")
    return (a[0] / n, a[1] / n)


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _left(d):
    return (-d[1], d[0])


def _ang(c, p):
    return math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))


# ---------------------------------------------------------------- curves
def line(p0, p1):
    return {"t": "line", "p0": [float(p0[0]), float(p0[1])], "p1": [float(p1[0]), float(p1[1])]}


def arc(c, r, a0, a1, ccw=True):
    return {"t": "arc", "c": [float(c[0]), float(c[1])], "r": float(r), "a0": float(a0), "a1": float(a1),
            "ccw": bool(ccw)}


def sweep_deg(cv):
    s = (cv["a1"] - cv["a0"]) % 360.0 if cv["ccw"] else (cv["a0"] - cv["a1"]) % 360.0
    return 360.0 if s < 1e-9 else s


def _apt(cv, a_deg):
    a = math.radians(a_deg)
    return (cv["c"][0] + cv["r"] * math.cos(a), cv["c"][1] + cv["r"] * math.sin(a))


def start(cv):
    return tuple(cv["p0"]) if cv["t"] == "line" else _apt(cv, cv["a0"])


def end(cv):
    return tuple(cv["p1"]) if cv["t"] == "line" else _apt(cv, cv["a1"])


def reverse(cv):
    if cv["t"] == "line":
        return line(cv["p1"], cv["p0"])
    return arc(cv["c"], cv["r"], cv["a1"], cv["a0"], not cv["ccw"])


def length(cv):
    if cv["t"] == "line":
        return _dist(cv["p0"], cv["p1"])
    return math.radians(sweep_deg(cv)) * cv["r"]


def tangent_at(cv, which):
    """Unit tangent in travel direction at 'start' or 'end'."""
    if cv["t"] == "line":
        return _unit(_v(cv["p0"], cv["p1"]))
    a = math.radians(cv["a0"] if which == "start" else cv["a1"])
    t = (-math.sin(a), math.cos(a))
    return t if cv["ccw"] else (-t[0], -t[1])


def _tangent_at_point(cv, p):
    if cv["t"] == "line":
        return _unit(_v(cv["p0"], cv["p1"]))
    a = math.atan2(p[1] - cv["c"][1], p[0] - cv["c"][0])
    t = (-math.sin(a), math.cos(a))
    return t if cv["ccw"] else (-t[0], -t[1])


def _arc_frac(cv, p, tol_mm=1e-6):
    """Fraction (0..1) of point p along the arc sweep, or None if outside."""
    a = _ang(cv["c"], p)
    s = sweep_deg(cv)
    d = (a - cv["a0"]) % 360.0 if cv["ccw"] else (cv["a0"] - a) % 360.0
    tol = math.degrees(tol_mm / cv["r"])
    if d <= s + tol:
        return min(d / s, 1.0)
    if d >= 360.0 - tol:
        return 0.0
    return None


def sample(cv, sag_mm=0.05):
    """Points along a curve (start included, end included). Only for area/containment tests."""
    if cv["t"] == "line":
        return [tuple(cv["p0"]), tuple(cv["p1"])]
    r = cv["r"]
    s = math.radians(sweep_deg(cv))
    step = 2.0 * math.acos(max(-1.0, 1.0 - sag_mm / r)) if sag_mm < r else math.pi / 4
    n = max(2, int(math.ceil(s / max(step, 1e-4))))
    sign = 1.0 if cv["ccw"] else -1.0
    a0 = math.radians(cv["a0"])
    return [(cv["c"][0] + r * math.cos(a0 + sign * s * i / n), cv["c"][1] + r * math.sin(a0 + sign * s * i / n))
            for i in range(n + 1)]


def loop_points(curves, sag_mm=0.05):
    pts = []
    for cv in curves:
        pts.extend(sample(cv, sag_mm)[:-1])
    return pts


def loop_area(curves):
    """Exact signed area (CCW positive) of a closed loop of lines and arcs."""
    a2 = 0.0
    for cv in curves:
        if cv["t"] == "line":
            a2 += cv["p0"][0] * cv["p1"][1] - cv["p1"][0] * cv["p0"][1]
        else:
            cx, cy = cv["c"]
            r = cv["r"]
            t0 = math.radians(cv["a0"])
            t1 = t0 + math.radians(sweep_deg(cv)) * (1 if cv["ccw"] else -1)
            a2 += r * r * (t1 - t0) + r * cx * (math.sin(t1) - math.sin(t0)) - r * cy * (math.cos(t1) - math.cos(t0))
    return 0.5 * a2


def loop_length(curves):
    return sum(length(c) for c in curves)


def _pip(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xin = xi + (y - yi) * (xj - xi) / (yj - yi)
            if x < xin:
                inside = not inside
        j = i
    return inside


def _region_loops(region):
    if isinstance(region, dict):
        return [region["outer"]] + list(region.get("holes", []))
    return list(region)


def point_in_region(pt, region, sag_mm=0.01):
    """Even-odd test over the outer loop and its holes."""
    inside = False
    for lp in _region_loops(region):
        if _pip(pt, loop_points(lp, sag_mm)):
            inside = not inside
    return inside


def distance_to_curve(pt, cv):
    if cv["t"] == "line":
        a, b = cv["p0"], cv["p1"]
        ab = _v(a, b)
        L2 = _dot(ab, ab)
        u = 0.0 if L2 < EPS else max(0.0, min(1.0, _dot(_v(a, pt), ab) / L2))
        return _dist(pt, _add(a, ab, u))
    d = _dist(pt, cv["c"])
    proj = _add(cv["c"], _v(cv["c"], pt), cv["r"] / d) if d > EPS else start(cv)
    if _arc_frac(cv, proj) is not None:
        return abs(d - cv["r"])
    return min(_dist(pt, start(cv)), _dist(pt, end(cv)))


def distance_to_region_boundary(pt, region):
    return min(distance_to_curve(pt, cv) for lp in _region_loops(region) for cv in lp)


# ---------------------------------------------------------------- joining
def _key(p, tol):
    return (int(math.floor(p[0] / tol)), int(math.floor(p[1] / tol)))


def _dedupe(curves):
    seen, out, dup = set(), [], 0
    for cv in curves:
        a, b = start(cv), end(cv)
        ends = tuple(sorted([(round(a[0], 1), round(a[1], 1)), (round(b[0], 1), round(b[1], 1))]))
        k = (cv["t"], ends) if cv["t"] == "line" else \
            (cv["t"], ends, round(cv["c"][0], 1), round(cv["c"][1], 1), round(cv["r"], 1))
        if k in seen:
            dup += 1
            continue
        seen.add(k)
        out.append(cv)
    return out, dup


def join_curves(curves, tol_mm=1.0):
    """Join lines and arcs into closed loops.

    Returns dict:
      loops    : list of closed loops (lists of curves, consecutive, snapped)
      regions  : [{"outer": loop CCW, "holes": [loops CW]}]
      open_ends: [[x, y], ...]  chain ends that meet nothing within tol  -> STOP and report
      branches : [[x, y], ...]  points where 3+ curves meet             -> STOP and report
      dropped_short, duplicates, max_snap_mm
    """
    curves = [c for c in curves]
    dropped = [c for c in curves if length(c) < SHORT_CURVE_MM]
    curves = [c for c in curves if length(c) >= SHORT_CURVE_MM]
    curves, dup = _dedupe(curves)

    # cluster end points (union-find over a tol grid)
    ends = []
    for i, cv in enumerate(curves):
        ends.append((i, 0, start(cv)))
        ends.append((i, 1, end(cv)))
    parent = list(range(len(ends)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    grid = {}
    for k, (_, _, p) in enumerate(ends):
        gx, gy = _key(p, tol_mm)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for m in grid.get((gx + dx, gy + dy), ()):
                    if _dist(p, ends[m][2]) <= tol_mm:
                        parent[find(k)] = find(m)
        grid.setdefault((gx, gy), []).append(k)

    node_of = {}
    members = {}
    for k, (i, e, p) in enumerate(ends):
        r = find(k)
        node_of[(i, e)] = r
        members.setdefault(r, []).append(k)

    # node representative: an arc end point if the node has one, else the mean
    rep = {}
    max_snap = 0.0
    for r, ks in members.items():
        arc_pts = [ends[k][2] for k in ks if curves[ends[k][0]]["t"] == "arc"]
        if arc_pts:
            p = arc_pts[0]
        else:
            p = (sum(ends[k][2][0] for k in ks) / len(ks), sum(ends[k][2][1] for k in ks) / len(ks))
        rep[r] = p
        for k in ks:
            max_snap = max(max_snap, _dist(p, ends[k][2]))

    adj = {}
    for i in range(len(curves)):
        adj.setdefault(node_of[(i, 0)], []).append(i)
        adj.setdefault(node_of[(i, 1)], []).append(i)
    open_ends = [list(rep[n]) for n, es in adj.items() if len(es) == 1]
    branches = [list(rep[n]) for n, es in adj.items() if len(es) > 2]

    used = set()
    loops = []
    for i0 in range(len(curves)):
        if i0 in used:
            continue
        n_start = node_of[(i0, 0)]
        if len(adj[n_start]) != 2 or len(adj[node_of[(i0, 1)]]) != 2:
            continue
        chain, cur, node = [], i0, n_start
        ok = True
        while True:
            used.add(cur)
            a, b = node_of[(cur, 0)], node_of[(cur, 1)]
            cv = curves[cur] if a == node else reverse(curves[cur])
            nxt_node = b if a == node else a
            chain.append((cv, node, nxt_node))
            node = nxt_node
            if node == n_start:
                break
            if len(adj[node]) != 2:
                ok = False
                break
            cand = [j for j in adj[node] if j != cur]
            if not cand:  # a single curve closing on itself (full circle split badly)
                ok = False
                break
            cur = cand[0]
            if cur in used:
                ok = False
                break
        if not ok:
            continue
        loops.append([_snap(cv, rep[na], rep[nb]) for cv, na, nb in chain])

    regions = _nest(loops)
    return {"loops": loops, "regions": regions, "open_ends": open_ends, "branches": branches,
            "dropped_short": dropped, "duplicates": dup, "max_snap_mm": max_snap}


def _snap(cv, pa, pb):
    if cv["t"] == "line":
        return line(pa, pb)
    return arc(cv["c"], cv["r"], _ang(cv["c"], pa), _ang(cv["c"], pb), cv["ccw"])


def _nest(loops):
    info = []
    for lp in loops:
        info.append((lp, loop_points(lp, 0.05), abs(loop_area(lp))))
    order = sorted(range(len(loops)), key=lambda i: -info[i][2])
    depth = {}
    parent = {}
    for idx, i in enumerate(order):
        probe = info[i][1][0]
        # probe a point just inside the loop edge to avoid touching-edge ambiguity
        par = None
        for j in order[:idx]:
            if info[j][2] > info[i][2] and _pip(probe, info[j][1]):
                par = j  # smallest containing loop wins (later in order = smaller)
        parent[i] = par
        depth[i] = 0 if par is None else depth[par] + 1
    regions = {}
    for i in order:
        lp = loops[i]
        if depth[i] % 2 == 0:
            if loop_area(lp) < 0:
                lp = [reverse(c) for c in reversed(lp)]
            regions[i] = {"outer": lp, "holes": []}
    for i in order:
        if depth[i] % 2 == 1:
            lp = loops[i]
            if loop_area(lp) > 0:
                lp = [reverse(c) for c in reversed(lp)]
            regions[parent[i]]["holes"].append(lp)
    return [regions[i] for i in order if i in regions]


# ---------------------------------------------------------------- intersections
def _line_hits(P, d, cv, tol=1e-7):
    """Hits of the infinite line P + t*d (d unit) with a curve: [(t, point, curve_tangent)]."""
    out = []
    if cv["t"] == "line":
        A = cv["p0"]
        e = _v(A, cv["p1"])
        den = _cross(d, e)
        if abs(den) < EPS:
            return out  # parallel (collinear overlap ignored: corners are hit by neighbours)
        AP = _v(P, A)
        t = _cross(AP, e) / den
        u = _cross(AP, d) / den
        L = _norm(e)
        if -tol / L <= u <= 1 + tol / L:
            out.append((t, _add(P, d, t), _unit(e)))
        return out
    f = _v(cv["c"], P)
    b = _dot(f, d)
    cc = _dot(f, f) - cv["r"] ** 2
    disc = b * b - cc
    if disc < -1e-9:
        return out
    sq = math.sqrt(max(disc, 0.0))
    for t in ((-b - sq, -b + sq) if sq > 1e-12 else (-b,)):
        p = _add(P, d, t)
        if _arc_frac(cv, p, 1e-6) is not None:
            out.append((t, p, _tangent_at_point(cv, p)))
    return out


def _all_hits(P, d, loops):
    hits = []
    for li, lp in enumerate(loops):
        for ci, cv in enumerate(lp):
            for t, p, tg in _line_hits(P, d, cv):
                hits.append((t, p, tg, li, ci))
    return hits


def extend_to_boundary(p0, p1, region, stops=None, max_move_mm=None):
    """Move both ends of the axis p0-p1 onto the nearest boundary (0 gap).

    region : {"outer": loop, "holes": [...]} or list of loops (ceiling field loop)
    stops  : extra closed loops the element must stop at (other elements, fascias)
    Returns {"p0","p1","hit0","hit1","moved":[d0,d1],"warnings":[...]}; moved > 0 means extended.
    """
    loops = _region_loops(region) + list(stops or [])
    d = _unit(_v(p0, p1))
    mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
    if not point_in_region(mid, region):
        raise GeometryError("axis midpoint is outside the ceiling region", mid)
    for s in stops or []:
        if _pip(mid, loop_points(s)):
            raise GeometryError("axis midpoint lies inside a stop outline", mid)
    hits = _all_hits(mid, d, loops)
    neg = [h for h in hits if h[0] < -1e-6]
    pos = [h for h in hits if h[0] > 1e-6]
    if not neg or not pos:
        raise GeometryError("axis does not meet the boundary on both sides", mid)
    h0 = max(neg, key=lambda h: h[0])
    h1 = min(pos, key=lambda h: h[0])
    half = _dist(p0, p1) / 2.0
    moved = [-h0[0] - half, h1[0] - half]
    warn = []
    if max_move_mm is not None:
        for k, m in enumerate(moved):
            if abs(m) > max_move_mm:
                warn.append("end %d moved %.0f mm (> %.0f); check the DWG" % (k, m, max_move_mm))

    def info(h):
        n = _left(d)
        skew = math.degrees(math.acos(min(1.0, abs(_dot(h[2], n)))))
        return {"pt": list(h[1]), "loop": h[3], "curve": h[4], "skew_deg": skew,
                "on_stop": h[3] >= len(_region_loops(region))}
    return {"p0": list(h0[1]), "p1": list(h1[1]), "hit0": info(h0), "hit1": info(h1), "moved": moved,
            "warnings": warn}


def _subcurve(cv, pa, pb):
    if cv["t"] == "line":
        return line(pa, pb)
    return arc(cv["c"], cv["r"], _ang(cv["c"], pa), _ang(cv["c"], pb), cv["ccw"])


def _boundary_path(loop, ia, pa, ib, pb):
    """Shortest path along a closed loop from point pa (on curve ia) to pb (on curve ib)."""
    n = len(loop)

    def frac(i, p):
        cv = loop[i]
        if cv["t"] == "line":
            L = length(cv)
            return 0.0 if L < EPS else _dot(_v(cv["p0"], p), _v(cv["p0"], cv["p1"])) / (L * L)
        return _arc_frac(cv, p, 1e-4) or 0.0

    def fwd(i_a, p_a, i_b, p_b):
        if i_a == i_b and frac(i_a, p_b) >= frac(i_a, p_a) - 1e-12:
            return [_subcurve(loop[i_a], p_a, p_b)]
        path = [_subcurve(loop[i_a], p_a, end(loop[i_a]))]
        i = (i_a + 1) % n
        while i != i_b:
            path.append(loop[i])
            i = (i + 1) % n
        path.append(_subcurve(loop[i_b], start(loop[i_b]), p_b))
        return path

    f = fwd(ia, pa, ib, pb)
    b = [reverse(c) for c in reversed(fwd(ib, pb, ia, pa))]
    f = [c for c in f if length(c) >= CLOSE_TOL_MM]
    b = [c for c in b if length(c) >= CLOSE_TOL_MM]
    return f if loop_length(f) <= loop_length(b) else b


def trim_to_boundary(p0, p1, width, region, stops=None, max_move_mm=None):
    """Outline of a straight linear element of the given width whose ends follow the
    boundary edge (cut parallel to the edge, walking round corners): no wedge gaps.

    Returns {"axis": [p0, p1], "outline": loop, "skew_deg": [s0, s1], "square": bool,
             "moved": [...], "warnings": [...]}.
    """
    ax = extend_to_boundary(p0, p1, region, stops, max_move_mm)
    loops = _region_loops(region) + list(stops or [])
    d = _unit(_v(ax["p0"], ax["p1"]))
    n = _left(d)
    mid = ((ax["p0"][0] + ax["p1"][0]) / 2.0, (ax["p0"][1] + ax["p1"][1]) / 2.0)
    sides = []
    for s in (+width / 2.0, -width / 2.0):
        m = _add(mid, n, s)
        if not point_in_region(m, region):
            raise GeometryError("element side leaves the region (element wider than the field?)", m)
        hs = _all_hits(m, d, loops)
        neg = [h for h in hs if h[0] < -1e-6]
        pos = [h for h in hs if h[0] > 1e-6]
        if not neg or not pos:
            raise GeometryError("element side does not meet the boundary", m)
        sides.append((max(neg, key=lambda h: h[0]), min(pos, key=lambda h: h[0])))
    (L0, L1), (R0, R1) = sides

    def endpath(ha, hb):
        if ha[3] != hb[3]:
            raise GeometryError("element end touches two different outlines; split the element", ha[1])
        return _boundary_path(loops[ha[3]], ha[4], ha[1], hb[4], hb[1])

    outline = [line(R0[1], R1[1])] + endpath(R1, L1) + [line(L1[1], L0[1])] + endpath(L0, R0)
    outline = [c for c in outline if length(c) >= CLOSE_TOL_MM]
    s0, s1 = ax["hit0"]["skew_deg"], ax["hit1"]["skew_deg"]
    return {"axis": [ax["p0"], ax["p1"]], "outline": outline, "skew_deg": [s0, s1],
            "square": s0 < 0.05 and s1 < 0.05 and len(outline) == 4,
            "moved": ax["moved"], "warnings": ax["warnings"]}


# ---------------------------------------------------------------- offsets / fascia
def _offset_curve(cv, dist):
    """Offset to the LEFT of travel direction by dist (negative = right)."""
    if cv["t"] == "line":
        n = _left(_unit(_v(cv["p0"], cv["p1"])))
        return line(_add(cv["p0"], n, dist), _add(cv["p1"], n, dist))
    r = cv["r"] - dist if cv["ccw"] else cv["r"] + dist
    if r <= SHORT_CURVE_MM:
        raise GeometryError("offset collapses an arc (r=%.1f)" % cv["r"], cv["c"])
    return arc(cv["c"], r, cv["a0"], cv["a1"], cv["ccw"])


def _support_intersections(a, b):
    """Intersections of the full supporting line/circle of two curves."""
    if a["t"] == "line" and b["t"] == "line":
        d1 = _v(a["p0"], a["p1"])
        d2 = _v(b["p0"], b["p1"])
        den = _cross(d1, d2)
        if abs(den) < EPS:
            return []
        t = _cross(_v(a["p0"], b["p0"]), d2) / den
        return [_add(a["p0"], d1, t)]
    if a["t"] == "arc" and b["t"] == "line":
        a, b = b, a
    if a["t"] == "line":
        d = _unit(_v(a["p0"], a["p1"]))
        f = _v(b["c"], a["p0"])
        bb = _dot(f, d)
        cc = _dot(f, f) - b["r"] ** 2
        disc = bb * bb - cc
        if disc < -1e-9:
            return []
        sq = math.sqrt(max(disc, 0.0))
        return [_add(a["p0"], d, -bb - sq), _add(a["p0"], d, -bb + sq)]
    c1, r1, c2, r2 = a["c"], a["r"], b["c"], b["r"]
    D = _dist(c1, c2)
    if D < EPS or D > r1 + r2 + 1e-9 or D < abs(r1 - r2) - 1e-9:
        return []
    x = (D * D + r1 * r1 - r2 * r2) / (2 * D)
    h = math.sqrt(max(r1 * r1 - x * x, 0.0))
    u = _unit(_v(c1, c2))
    m = _add(c1, u, x)
    n = _left(u)
    return [_add(m, n, h), _add(m, n, -h)]


def _rebuild(cv, pa, pb):
    if cv["t"] == "line":
        return line(pa, pb)
    return arc(cv["c"], cv["r"], _ang(cv["c"], pa), _ang(cv["c"], pb), cv["ccw"])


def offset_chain(curves, dist, closed):
    """Mitred offset of a chain/loop to the left by dist. Corners are intersections of the
    offset curves (true mitre); tangent-continuous joints keep the offset vertex.
    Raises GeometryError when an edge collapses or flips (too short for the offset)."""
    n = len(curves)
    off = [_offset_curve(c, dist) for c in curves]
    verts = []
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        a, b = curves[i], curves[j]
        v0 = end(a)
        ta, tb = tangent_at(a, "end"), tangent_at(b, "start")
        if abs(_cross(ta, tb)) < 1e-9 and _dot(ta, tb) > 0:
            verts.append(_add(v0, _left(ta), dist))
            continue
        cands = _support_intersections(off[i], off[j])
        if not cands:
            raise GeometryError("offset curves do not meet at corner", v0)
        verts.append(min(cands, key=lambda p: _dist(p, v0)))
    out = []
    for i in range(n):
        if closed:
            pa, pb = verts[i - 1], verts[i]
        else:
            pa = start(off[i]) if i == 0 else verts[i - 1]
            pb = end(off[i]) if i == n - 1 else verts[i]
        c = _rebuild(off[i], pa, pb)
        o = curves[i]
        if c["t"] == "line":
            if length(c) < SHORT_CURVE_MM or _dot(_v(c["p0"], c["p1"]), _v(o["p0"], o["p1"])) <= 0:
                raise GeometryError("offset collapses edge %d (shorter than the offset)" % i, start(o))
        else:
            if length(c) < SHORT_CURVE_MM or sweep_deg(c) > sweep_deg(o) + 180.0:
                raise GeometryError("offset collapses arc %d" % i, start(o))
        out.append(c)
    return out


def fascia_band(curves, thickness, closed, inward=True):
    """One continuous fascia profile (plan outline of the board) along a loop or chain.

    closed=True : returns {"outer": loop, "holes": [inner loop]}  (a ring, all corners mitred)
    closed=False: returns {"outer": loop, "holes": []}           (strip, square ends)
    The band lies on the left of the travel direction when inward=True (inside a CCW loop).
    """
    dist = thickness if inward else -thickness
    if closed and loop_area(curves) < 0:
        curves = [reverse(c) for c in reversed(curves)]
    inner = offset_chain(curves, dist, closed)
    if closed:
        outer, hole = (curves, inner) if inward else (inner, curves)
        if loop_area(outer) < 0:
            outer = [reverse(c) for c in reversed(outer)]
        if loop_area(hole) > 0:
            hole = [reverse(c) for c in reversed(hole)]
        if abs(loop_area(outer)) - abs(loop_area(hole)) <= 0:
            raise GeometryError("fascia ring has no area", start(curves[0]))
        return {"outer": outer, "holes": [hole]}
    back = [reverse(c) for c in reversed(inner)]
    prof = list(curves) + [line(end(curves[-1]), start(back[0]))] + back + [line(end(back[-1]), start(curves[0]))]
    if loop_area(prof) < 0:
        prof = [reverse(c) for c in reversed(prof)]
    return {"outer": prof, "holes": []}


def close_corners(segments, tol_mm=100.0, min_angle_deg=1.0):
    """Close open corners between straight segments (fascia pieces, wall axes).

    segments: list of dicts {"id", "p0": [x, y], "p1": [x, y], "group": any}; only ends of the
    same group (e.g. level + base height) are paired. Each free end is paired with the nearest
    free end of another segment within tol_mm; both move to the intersection of the two axes
    (true mitre). Collinear pairs meet at the midpoint. Ends that already coincide are left alone.
    Refused pairs (parallel offset, corner too far, segment would collapse) are reported.
    Returns {"segments": [copies with new p0/p1], "closed": n, "refused": [...]}.
    """
    segs = [dict(s, p0=list(s["p0"]), p1=list(s["p1"])) for s in segments]
    ends = [(i, k) for i in range(len(segs)) for k in ("p0", "p1")]
    grid = {}
    for n, (i, k) in enumerate(ends):
        grid.setdefault(_key(segs[i][k], tol_mm), []).append(n)

    def near(n):
        i, k = ends[n]
        gx, gy = _key(segs[i][k], tol_mm)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for m in grid.get((gx + dx, gy + dy), ()):
                    j, kk = ends[m]
                    if j != i and segs[j].get("group") == segs[i].get("group"):
                        yield m, _dist(segs[i][k], segs[j][kk])

    used = set()
    for n in range(len(ends)):
        if any(dd == 0.0 for m, dd in near(n)):
            used.add(n)
    cand = sorted((dd, n, m) for n in range(len(ends)) for m, dd in near(n) if n < m and 0.0 < dd <= tol_mm)
    closed, refused = 0, []
    for dd, a, b in cand:
        if a in used or b in used:
            continue
        ia, ka = ends[a]
        ib, kb = ends[b]
        sa, sb = segs[ia], segs[ib]
        da = _unit(_v(sa["p0"], sa["p1"]))
        db = _unit(_v(sb["p0"], sb["p1"]))
        if math.degrees(math.asin(min(1.0, abs(_cross(da, db))))) < min_angle_deg:
            if abs(_cross(da, _v(sa[ka], sb[kb]))) > 0.5:
                refused.append({"ids": [sa.get("id"), sb.get("id")], "at": list(sa[ka]), "why": "parallel offset"})
                continue
            p = ((sa[ka][0] + sb[kb][0]) / 2.0, (sa[ka][1] + sb[kb][1]) / 2.0)
        else:
            p = _support_intersections(line(sa["p0"], sa["p1"]), line(sb["p0"], sb["p1"]))[0]
            if _dist(p, sa[ka]) > 2 * tol_mm or _dist(p, sb[kb]) > 2 * tol_mm:
                refused.append({"ids": [sa.get("id"), sb.get("id")], "at": list(sa[ka]), "why": "corner too far"})
                continue
        oa, ob = list(sa[ka]), list(sb[kb])
        sa[ka] = [p[0], p[1]]
        sb[kb] = [p[0], p[1]]
        if _dist(sa["p0"], sa["p1"]) < SHORT_CURVE_MM or _dist(sb["p0"], sb["p1"]) < SHORT_CURVE_MM:
            sa[ka], sb[kb] = oa, ob
            refused.append({"ids": [sa.get("id"), sb.get("id")], "at": oa, "why": "segment would collapse"})
            continue
        used.add(a)
        used.add(b)
        closed += 1
    return {"segments": segs, "closed": closed, "refused": refused}


def check_loop_closed(curves, tol_mm=CLOSE_TOL_MM):
    """Returns the list of gaps [(index, gap_mm, point)] larger than tol."""
    gaps = []
    for i in range(len(curves)):
        a, b = end(curves[i]), start(curves[(i + 1) % len(curves)])
        g = _dist(a, b)
        if g > tol_mm:
            gaps.append((i, g, list(a)))
    return gaps


# ---------------------------------------------------------------- legacy data
def _circle3(a, b, c):
    d = 2.0 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-9:
        return None
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
    return (ux, uy), _dist((ux, uy), a)


def refit_arcs(points, tol_mm=1.5, closed=False, min_pts=4, max_r_mm=200000.0, max_step_deg=20.0):
    """Turn a flattened polyline (legacy JSON, arcs already chorded) back into lines and arcs.
    A run of >= min_pts vertices lying on one circle within tol_mm, turning one way, with steps of at
    most max_step_deg each, becomes an arc. Pass the result through join_curves to snap the ends."""
    pts = [tuple(p) for p in points]
    if closed and _dist(pts[0], pts[-1]) > EPS:
        pts.append(pts[0])
    out = []
    i = 0
    n = len(pts)
    while i < n - 1:
        best = None
        j = i + min_pts - 1
        while j < n:
            circ = _circle3(pts[i], pts[(i + j) // 2], pts[j])
            if circ is None or circ[1] > max_r_mm:
                break
            c, r = circ
            if max(abs(_dist(c, p) - r) for p in pts[i:j + 1]) > tol_mm:
                break
            smax = max(_dist(pts[k], pts[k + 1]) for k in range(i, j))
            if smax > 2 * r * math.sin(math.radians(max_step_deg) / 2):
                break  # corners of a rectangle are co-circular too; real flattened arcs have short steps
            if smax * smax / (8.0 * r) > tol_mm:
                break  # the arc would bulge more than tol_mm between two points: sparse points on a line are not an arc
            turns = [_cross(_v(pts[k - 1], pts[k]), _v(pts[k], pts[k + 1])) for k in range(i + 1, j)]
            if not (all(t > 0 for t in turns) or all(t < 0 for t in turns)):
                break
            best = (j, c, r, turns[0] > 0)
            j += 1
        if best:
            j, c, r, ccw = best
            out.append(arc(c, r, _ang(c, pts[i]), _ang(c, pts[j]), ccw))
            i = j
        else:
            if _dist(pts[i], pts[i + 1]) >= SHORT_CURVE_MM:
                out.append(line(pts[i], pts[i + 1]))
            i += 1
    return out


# ---------------------------------------------------------------- 2026-09-28
def straighten_bites(loop, max_seg_mm=600.0, min_turn_deg=100.0, max_turn_deg=220.0,
                     min_chord_mm=150.0, max_chord_mm=900.0, min_segs=3):
    """Replace round bites/lobes drawn as runs of short segments (or arcs) by the straight chord.
    A run = >= min_segs consecutive curves shorter than max_seg_mm turning the same way, total turn
    between min/max_turn_deg, chord within min/max_chord_mm. Returns (new_loop, [runs])."""
    n = len(loop)
    if n < min_segs + 2:
        return list(loop), []
    L = [length(c) for c in loop]
    T = []
    for i in range(n):
        a, b = tangent_at(loop[i - 1], "end"), tangent_at(loop[i], "start")
        T.append(math.degrees(math.atan2(_cross(a, b), _dot(a, b))))
    runs, i = [], 0
    # turn at the start of curve i is T[i]; a lobe's internal turns are T[i+1..j-1] plus arc sweeps
    while i < n:
        j = i
        while j < n and L[j] < max_seg_mm and (j == i or (abs(T[j]) > 3 and T[j] * T[i + 1 if i + 1 < n else i] > 0)):
            j += 1
        if j - i >= min_segs:
            inner = sum(T[k] for k in range(i + 1, j)) + sum(
                (sweep_deg(loop[k]) if loop[k]["ccw"] else -sweep_deg(loop[k])) for k in range(i, j) if loop[k]["t"] == "arc")
            ch = _dist(start(loop[i]), end(loop[j - 1]))
            if min_turn_deg <= abs(inner) <= max_turn_deg and min_chord_mm <= ch <= max_chord_mm:
                runs.append((i, j))
        i = max(j, i + 1)
    if not runs:
        return list(loop), []
    out, k = [], 0
    for i, j in runs:
        out.extend(loop[k:i])
        out.append(line(start(loop[i]), end(loop[j - 1])))
        k = j
    out.extend(loop[k:])
    return out, [{"from": i, "to": j, "at": list(start(loop[i])), "chord_mm": _dist(start(loop[i]), end(loop[j - 1]))} for i, j in runs]


def continue_rhythm(axes, region, pitch_mm=None, side="both", clearance_mm=30.0, min_len_mm=300.0,
                    center=None, max_new=200):
    """Continue a family of parallel axes (or radial axes through `center`) with the same pitch
    until the region is full. axes: [(p0, p1)] existing element axes. region: ceiling_geometry
    region or loop list. For radial fans pass center=(x, y); pitch is then an angle step (deg)
    measured from the axes. New axes end on the region boundary via extend_to_boundary.
    Returns list of (p0, p1) for the new elements (existing ones are not returned)."""
    if not axes:
        return []
    mids = [((a[0][0] + a[1][0]) / 2.0, (a[0][1] + a[1][1]) / 2.0) for a in axes]
    out = []
    if center is None:
        d = _unit(_v(axes[0][0], axes[0][1]))
        nrm = _left(d)
        offs = sorted(_dot(m, nrm) for m in mids)
        gaps = sorted(offs[i + 1] - offs[i] for i in range(len(offs) - 1))
        p = pitch_mm or (gaps[len(gaps) // 2] if gaps else 100.0)
        ref = min(mids, key=lambda m: _dot(m, nrm))
        for sgn, start_off in ((-1, offs[0]), (1, offs[-1])):
            if side not in ("both", "neg" if sgn < 0 else "pos"):
                continue
            k = 1
            while len(out) < max_new:
                o = start_off + sgn * p * k
                base = _add(ref, nrm, o - _dot(ref, nrm))
                probe0, probe1 = _add(base, d, -1.0), _add(base, d, 1.0)
                try:
                    r = extend_to_boundary(probe0, probe1, region)
                except GeometryError:
                    break
                if _dist(r["p0"], r["p1"]) < min_len_mm:
                    break
                # keep a clearance to the boundary on the side we are growing towards
                test = _add(base, nrm, sgn * clearance_mm)
                if not point_in_region(test, region):
                    break
                out.append((r["p0"], r["p1"]))
                k += 1
        return out
    cx, cy = center
    angs = sorted(math.degrees(math.atan2(m[1] - cy, m[0] - cx)) for m in mids)
    steps = sorted(angs[i + 1] - angs[i] for i in range(len(angs) - 1))
    step = pitch_mm or (steps[len(steps) // 2] if steps else 1.0)
    rmid = sum(_dist(m, center) for m in mids) / len(mids)
    for sgn, a0 in ((-1, angs[0]), (1, angs[-1])):
        if side not in ("both", "neg" if sgn < 0 else "pos"):
            continue
        k = 1
        while len(out) < max_new:
            a = math.radians(a0 + sgn * step * k)
            u = (math.cos(a), math.sin(a))
            m = (cx + u[0] * rmid, cy + u[1] * rmid)
            if not point_in_region(m, region):
                break
            try:
                r = extend_to_boundary(_add(m, u, -1.0), _add(m, u, 1.0), region)
            except GeometryError:
                break
            if _dist(r["p0"], r["p1"]) < min_len_mm:
                break
            tng = _left(u)
            if not point_in_region(_add(m, tng, sgn * clearance_mm), region):
                break
            out.append((r["p0"], r["p1"]))
            k += 1
    return out


# ---------------------------------------------------------------- 2026-09-29 colour zones next to panel fields
# Wedges (a white wedge between a colour zone and a panel field at the same height), step closures (the same at
# a height step, with its closure walls) and straight borders (the zone/panel border is ONE straight line, radial
# in a curved corridor). These need polygon booleans, so they use shapely; the import is local, the module still loads in
# IronPython. Inputs may be ceiling_geometry regions ({"outer": loop, "holes": [...]}), bare loops or shapely
# polygons; polygons come back as shapely polygons, and polygon_to_region() turns them into curve loops for Revit.

def _shp():
    from shapely.geometry import Polygon, LineString, Point
    from shapely.ops import unary_union, linemerge
    return Polygon, LineString, Point, unary_union, linemerge


def region_to_polygon(region, sag_mm=0.05):
    """ceiling_geometry region / loop (or a shapely polygon, returned as is) -> shapely Polygon."""
    if hasattr(region, "geom_type"):
        return region
    Polygon = _shp()[0]
    r = region if isinstance(region, dict) and "outer" in region else {"outer": region, "holes": []}
    p = Polygon(loop_points(r["outer"], sag_mm), [loop_points(h, sag_mm) for h in r.get("holes", [])])
    return p if p.is_valid else p.buffer(0)


def _clean_ring(coords, merge_mm):
    pts = [tuple(p) for p in coords]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    out = []
    for p in pts:
        if not out or _dist(p, out[-1]) > merge_mm:
            out.append(p)
    if len(out) > 2 and _dist(out[0], out[-1]) <= merge_mm:
        out.pop()
    k = 0
    while k < len(out) and len(out) > 3:          # drop points lying on the line through their neighbours
        a, b, c = out[k - 1], out[k], out[(k + 1) % len(out)]
        u, w = _v(a, b), _v(b, c)
        # an edge that folds back onto the previous one (a spike: the shorter edge lies on the longer one, Revit
        # rejects the loop); the tip of a thin wedge is kept, its edges drift apart
        spike = False
        if _dot(u, w) < -0.985 * _dist(a, b) * _dist(b, c):
            far, q, r_ = (a, b, c) if _dist(a, b) <= _dist(b, c) else (c, b, a)
            spike = abs(_cross(_v(q, r_), _v(q, far))) / max(_dist(q, r_), EPS) < 0.5
        if spike or abs(_cross(u, w)) / max(_dist(a, c), EPS) < 0.05:
            out.pop(k)
            k = max(k - 1, 0)
        else:
            k += 1
    return out


def polygon_to_region(pg, merge_mm=2.0, arc_tol_mm=0.5):
    """shapely Polygon -> region of lines and arcs (refit_arcs + join_curves) for Revit sketches.
    Vertices closer than merge_mm are merged (Revit rejects sketch lines under 0.78 mm). A ring that touches
    itself at one point (pinch) reads as a branch; it is retried with a 0.6 mm closing / opening.
    Raises GeometryError when no clean closed loops come out."""
    if pg.geom_type != "Polygon" or pg.is_empty:
        raise GeometryError("not one polygon (%s)" % pg.geom_type)

    Polygon = _shp()[0]
    # holes thinner than 3 mm on average (cleanup leftovers along a fixture end) are not openings
    keep = [h for h in pg.interiors if Polygon(h).area > 1.5 * Polygon(h).length]
    if len(keep) != len(pg.interiors):
        pg = Polygon(pg.exterior, keep)

    def once(q, tol):
        loops = []
        for ring in [q.exterior] + list(q.interiors):
            pts = _clean_ring(ring.coords, merge_mm)
            if len(pts) < 3:
                return None
            if tol is None:      # straight segments only (fallback when a fitted arc is wrong)
                cs = [line(pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts))]
            else:
                cs = refit_arcs(pts + [pts[0]], tol_mm=tol, closed=True)
            j = join_curves(cs, tol_mm=1.0)
            if j["open_ends"] or j["branches"] or len(j["loops"]) != 1:
                return None
            # the rebuilt loop must enclose the area of its points: an arc fitted the wrong way round bulges out
            if tol is not None:
                try:
                    pp = Polygon(pts)
                    if abs(Polygon(loop_points(j["loops"][0], 0.5)).area - pp.area) > 0.6 * pp.length + 300.0:
                        return None
                except Exception:
                    return None
            loops.append(j["loops"][0])
        return {"outer": loops[0], "holes": loops[1:]}
    for tol in (arc_tol_mm, None):
        for q in (pg, pg.buffer(0.6, join_style=2).buffer(-0.6, join_style=2), pg.buffer(-0.6, join_style=2).buffer(0.6, join_style=2)):
            if q.geom_type != "Polygon" or abs(q.area - pg.area) > 0.002 * pg.area + 2e3:
                continue
            r = once(q, tol)
            if r is not None:
                return r
    c = pg.representative_point()
    raise GeometryError("outline rebuild failed", (c.x, c.y))


def radial_direction(p0, pm, p1, at):
    """Unit vector from the centre of the arc through p0, pm, p1 towards `at` ("dik" = perpendicular to a
    curved corridor wall)."""
    circ = _circle3(p0, pm, p1)
    if circ is None:
        raise GeometryError("arc points are collinear", p0)
    return _unit(_v(circ[0], at))


def _dir_deg(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def _adiff(a, b):
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _vec_deg(d):
    return math.degrees(math.atan2(d[1], d[0])) % 180.0

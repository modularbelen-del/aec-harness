"""Tests ported from the ceiling-from-dwg skill's test_tools.py; the bodies are unchanged."""
import math  # noqa: F401  (used by some ported bodies)

import aec.compat.ceiling_geometry as G
from _helpers import check, near, pnear


def test_zones():
    """Colour zone next to panel fields: wedges, closures at a height step, straight border."""
    from shapely.geometry import Polygon, box
    sq = lambda x0, y0, x1, y1: box(x0, y0, x1, y1)
    # polygon_to_region: straight, arc and a pinched ring
    r = G.polygon_to_region(sq(0, 0, 1000, 500))
    check("zones poly->region rectangle", len(r["outer"]) == 4 and near(G.loop_area(r["outer"]), 5e5, 1))
    half = Polygon([(1000 * math.cos(math.radians(a)), 1000 * math.sin(math.radians(a))) for a in range(0, 181, 2)])
    r = G.polygon_to_region(half)
    check("zones poly->region keeps the arc", any(c["t"] == "arc" and abs(c["r"] - 1000) < 1 for c in r["outer"]))
    # a ring that touches itself at (1000, 1000) (a notch whose tip meets the edge) reads as a branch in join_curves
    pinch = Polygon([(0, 0), (2000, 0), (2000, 1000), (1000, 1000), (1200, 500), (800, 500), (1000, 1000), (0, 1000)])
    r = G.polygon_to_region(pinch)
    got = abs(G.loop_area(r["outer"])) - sum(abs(G.loop_area(h)) for h in r["holes"])
    check("zones poly->region repairs a pinch", abs(got - (2e6 - 1e5)) < 2e3, got)
    # radial direction
    d = G.radial_direction((1000, 0), (0, 1000), (-1000, 0), (0, 2000))
    check("zones radial direction", pnear(d, (0, 1), 1e-9), d)
    # Wedge: zone edge 3.8 deg off the vertical column line x = 2300 -> the piece between is a wedge
    zone = Polygon([(0, 0), (2000, 0), (2200, 3000), (0, 3000)])
    wedge = Polygon([(2002, 0), (2298, 0), (2298, 3000), (2202, 3000)])
    full = sq(2300, 0, 2898, 1500)
    w = G.find_wedges(zone, {"W": wedge, "P": full}, leds=[((2600, 0), (2600, 3000)), ((0, 1500), (2898, 1500))])
    check("zones wedge by angle", [x["key"] for x in w] == ["W"] and abs(w[0]["angle_off_deg"] - 3.81) < 0.05, w)
    z2 = sq(0, 0, 1000, 3000)
    w2 = G.find_wedges(z2, {"T": sq(1002, 0, 1080, 3000), "Q": sq(1002, 3002, 1600, 6000)}, column_dir=(0, 1))
    check("zones wedge by width (sliver 78 mm)", [x["key"] for x in w2] == ["T"] and near(w2[0]["width_mm"], 78, 0.1), w2)
    w3 = G.find_wedges(z2, {"Q": sq(1002, 0, 1600, 3000)}, column_dir=90.0)
    check("zones parallel panel is not a wedge", w3 == [], w3)
    nz = G.absorb_wedges(zone, [wedge])
    xs = sorted(round(x, 1) for x, y in nz.exterior.coords)
    check("zones absorbed zone ends on the column line", near(nz.bounds[2], 2298, 0.01) and xs.count(2298.0) >= 2, nz.bounds)
    check("zones absorbed area", abs(nz.area - (zone.area + wedge.area)) < 2.1 * 3000 + 1, nz.area - zone.area - wedge.area)
    parts = G.cut_back(sq(1500, -100, 3000, 3100), [nz])
    check("zones profile layer cut back", parts and all(p.intersection(nz.buffer(-1.5)).area < 1e-6 for p in parts)
          and abs(sum(p.area for p in parts) - (sq(1500, -100, 3000, 3100).area - sq(1500, -100, 3000, 3100).intersection(nz.buffer(-1)).area)) < 1)
    check("zones profile layer unchanged -> None", G.cut_back(sq(5000, 0, 6000, 1000), [nz]) is None)
    # Step closure: the wedge belonged to a higher field; the old closure along the slanted edge goes, a new one runs
    # along x = 2298 (axis 7.5 mm inside the zone, ends run on 18 mm)
    walls = [{"id": 1, "p0": (2000 - 7.5, -18), "p1": (2200 - 7.5, 3018)}]
    st = G.step_closures(nz, [wedge], walls, [sq(2300, 0, 2898, 3000)])
    ok = st["delete"] == [1] and not st["trim"] and len(st["new"]) == 1
    if ok:
        a, b = st["new"][0]["p0"], st["new"][0]["p1"]
        ok = near(a[0], 2290.5, 1e-6) and near(b[0], 2290.5, 1e-6) and near(abs(b[1] - a[1]), 3036, 1e-6)
    check("zones step closure moved to the column line", ok, st)
    walls2 = [{"id": 2, "p0": (1992.5, -18), "p1": (2192.5, 3018)}, {"id": 3, "p0": (0, -7.5), "p1": (2002, -7.5)}]
    st2 = G.step_closures(nz, [sq(2002, 1500, 2298, 3000)], walls2, [sq(2300, 0, 2898, 3000)])
    check("zones closure partly covered is trimmed with a run-on", [t["id"] for t in st2["trim"]] == [2] and 3 not in st2["delete"], st2)
    # Straight border: kinked border (x = 1000 below, 1040 above) -> one straight vertical line at x = 1020
    zk = Polygon([(0, 0), (1000, 0), (1000, 1500), (1040, 1500), (1040, 3000), (0, 3000)])
    A, Bp = sq(1002, 0, 1600, 1498), sq(1042, 1500, 1600, 3000)
    res = G.straighten_border(zk, {"A": A, "B": Bp}, (0, 1))
    z9 = res["zone"]
    check("zones border straightened", near(z9.bounds[2], 1020, 0.01) and near(z9.area, 1020 * 3000, 5)
          and res["sides"][0]["status"] == "straightened" and near(res["sides"][0]["dev_mm"], 20, 0.01), (z9.bounds, res["sides"]))
    ok = set(res["panels"]) == {"A", "B"} and all(near(res["panels"][k].bounds[0], 1022, 0.01) for k in "AB")
    ok = ok and all(near(res["panels"][k].distance(z9), 2, 0.01) for k in "AB") and res["panels"]["A"].distance(res["panels"]["B"]) > 1.9
    check("zones panels rebuilt on the line with 2 mm joints", ok, dict((k, v.bounds) for k, v in res["panels"].items()))
    check("zones nothing lost or overlapping", abs(z9.area + sum(p.area for p in res["panels"].values())
          - (zk.area + A.area + Bp.area)) < 100 and z9.intersection(res["panels"]["A"]).area < 1e-6,
          z9.area + sum(p.area for p in res["panels"].values()) - (zk.area + A.area + Bp.area))
    res2 = G.straighten_border(z9, res["panels"], (0, 1))
    check("zones straight border left alone", res2["sides"][0]["status"] == "straight" and not res2["panels"], res2["sides"])
    # a sliver panel left under sliver_mm2 beyond the line is removed; its speck goes to the panel behind it
    zs = Polygon([(0, 0), (1000, 0), (1000, 1500), (1060, 1500), (1060, 3000), (0, 3000)])
    S_, A2, B2 = sq(1002, 0, 1040, 1498), sq(1042, 0, 1600, 1498), sq(1062, 1500, 1600, 3000)
    r3 = G.straighten_border(zs, {"S": S_, "A": A2, "B": B2}, (0, 1))
    check("zones sliver removed, speck joins the panel behind", r3["removed"] == ["S"] and near(r3["zone"].bounds[2], 1030, 0.01)
          and "A" in r3["panels"] and near(r3["panels"]["A"].bounds[0], 1032, 0.01) and near(r3["panels"]["B"].bounds[0], 1032, 0.01),
          (r3["removed"], r3["sides"], dict((k, v.bounds) for k, v in r3["panels"].items())))
    # radial direction as a function of the border position
    r4 = G.straighten_border(zk, {"A": A, "B": Bp}, lambda p, bdeg: G.radial_direction((1020, -50000), (-48980, 0), (1020, 50000), p))
    check("zones straighten with a direction function", r4["sides"][0]["status"] == "straightened", r4["sides"])
    r5 = G.straighten_border(zk, {"A": A, "B": Bp}, lambda p, bdeg: None)
    check("zones border without a direction is skipped", r5["sides"][0]["status"] == "skip: no direction" and not r5["panels"], r5["sides"])
    # independent wedge scan: a 600 grid with one skewed piece and one sliver; a whole field turned 30 deg is fine
    from shapely import affinity
    grid = dict(("g%d_%d" % (i, j), sq(i * 600 + 1, j * 600 + 1, i * 600 + 599, j * 600 + 599)) for i in range(5) for j in range(4))
    grid["skew"] = Polygon([(3001, 1), (3599, 1), (3599, 1199), (3110, 1199)])        # left edge 5.2 deg off
    grid["sliver"] = sq(3001, 1201, 3080, 2399)
    sc = dict((x["key"], x) for x in G.scan_wedges(grid))
    check("scan finds the skewed piece and the sliver only", set(sc) == {"skew", "sliver"} and sc["skew"]["reason"] == "angle"
          and abs(sc["skew"]["angle_off_deg"] - 5.2) < 0.1 and sc["sliver"]["reason"] == "narrow", sc)
    turned = dict((k, affinity.rotate(v, 30, origin=(0, 0))) for k, v in grid.items() if k.startswith("g"))
    check("scan: a field turned 30 deg is not a wedge", G.scan_wedges(turned) == [])
    check("scan with a given grid direction", [x["key"] for x in G.scan_wedges({"a": sq(0, 0, 600, 600)}, ref_dir=(1, 0.1))] == ["a"])
    # slivers: a 20 mm panel strip at the end of a column joins the column's last panel; a thin gypsum strip between a
    # zone and the wall joins the zone only when allowed; a strip touching only at a corner is left
    col = {"p1": sq(0, 0, 598, 598), "p2": sq(600, 0, 1198, 598), "s1": sq(0, 600, 598, 620), "s2": Polygon([(600, 600), (1198, 600), (1198, 640), (600, 612)])}
    ms = G.merge_slivers(col)
    ok = sorted(ms["removed"]) == ["s1", "s2"] and set(ms["merged"]) == {"p1", "p2"}
    ok = ok and near(ms["merged"]["p1"].bounds[3], 620, 0.01) and near(ms["merged"]["p1"].area, 598 * 620, 1) and ms["merged"]["p1"].distance(ms["merged"]["p2"]) > 1.99
    check("slivers join the last panel of their column", ok, (ms["removed"], dict((k, v.bounds) for k, v in ms["merged"].items())))
    zg = {"zone": sq(0, 0, 3000, 1000), "strip": sq(0, 1002, 3000, 1032), "panel": sq(0, 1034, 3000, 1600)}
    mz = G.merge_slivers(zg, allowed=lambda s, k: k == "zone")
    check("gypsum strip joins the zone (allowed pair only)", mz["removed"] == ["strip"] and near(mz["merged"]["zone"].bounds[3], 1032, 0.01)
          and near(mz["merged"]["zone"].distance(Polygon(zg["panel"])), 2, 0.01), (mz, dict((k, v.bounds) for k, v in mz["merged"].items())))
    mc = G.merge_slivers({"a": sq(0, 0, 600, 600), "s": sq(602, 602, 1400, 640)})
    check("strip touching only at a corner is left", mc["removed"] == [] and mc["skipped"], mc)
    # a tapering strip above three edge panels (2 mm joint, then a 44 mm light slot) is shared out along the joints
    pa, pb, pc = sq(0, 0, 598, 1500), sq(600, 0, 1198, 1500), sq(1242, 0, 1840, 1500)
    crescent = Polygon([(0, 1502), (1840, 1502), (1840, 1800), (0, 1560)])
    ab = G.absorb_strip(crescent, {"a": pa, "b": pb, "c": pc})
    ok = set(ab["pieces"]) == {"a", "b", "c"} and ab["left"].area < 1
    nA, nB, nC = ab["pieces"].get("a"), ab["pieces"].get("b"), ab["pieces"].get("c")
    if ok:
        ok = near(nA.distance(nB), 2, 0.05) and near(nB.distance(nC), 44, 0.05) and nC.bounds[3] > 1790 and nA.bounds[3] > 1560
        from shapely.ops import unary_union
        slot = sq(1198, 1502, 1242, 1800).intersection(crescent).area + sq(598, 1502, 600, 1800).intersection(crescent).area
        ok = ok and abs(crescent.difference(unary_union([nA, nB, nC])).area - slot) < 5
    check("strip shared out along the joints, slot kept", ok and sorted(round(g["width_mm"]) for g in ab["gaps"]) == [2, 44],
          (ab["gaps"], dict((k, v.bounds) for k, v in ab["pieces"].items())))
    try:
        G.polygon_to_region(sq(0, 0, 10, 10).union(sq(20, 0, 30, 10)))
        check("zones multipolygon refused", False)
    except G.GeometryError:
        check("zones multipolygon refused", True)

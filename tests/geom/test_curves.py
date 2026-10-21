"""Tests ported from the ceiling-from-dwg skill's test_tools.py; the bodies are unchanged."""
import math  # noqa: F401  (used by some ported bodies)

from aec.geom import curves as G
from _helpers import check, near, pnear, rect  # noqa: F401


def test_units():
    check("units cm", G.dwg_unit_to_mm(5) == 10.0)
    try:
        G.dwg_unit_to_mm(0)
        check("units unitless refused", False)
    except G.GeometryError:
        check("units unitless refused", True)


def test_join():
    # shuffled, reversed, 0.6 mm gaps, one duplicate, one arc: a 4000 x 3000 bay with an arc top
    c = [G.line((0, 0), (4000, 0)), G.line((4000.6, 0), (4000, 3000)),
         G.arc((2000, 3000), 2000, 0, 180, True), G.line((0, 0.5), (0, 3000))]
    c = [c[2], G.reverse(c[0]), c[3], c[1], c[0]]
    r = G.join_curves(c, 1.0)
    check("join one loop", len(r["loops"]) == 1 and not r["open_ends"] and not r["branches"])
    check("join duplicate", r["duplicates"] == 1)
    reg = r["regions"][0]
    exact = 4000 * 3000 + math.pi * 2000 ** 2 / 2
    # the 0.6 mm gaps are closed by snapping, which may move the area by < gap x perimeter
    check("join area exact with arc", near(G.loop_area(reg["outer"]), exact, 0.6 * 14300), G.loop_area(reg["outer"]))
    check("join keeps the arc", any(cv["t"] == "arc" for cv in reg["outer"]))
    check("join closed", not G.check_loop_closed(reg["outer"]))
    # open loop must be reported, not closed
    r2 = G.join_curves([G.line((0, 0), (1000, 0)), G.line((1000, 0), (1000, 1000)), G.line((1000, 1000), (0, 1003))], 1.0)
    check("join open reported", len(r2["open_ends"]) == 2 and not r2["loops"])
    # hole nesting
    r3 = G.join_curves(rect(0, 0, 1000, 1000) + rect(400, 400, 600, 600), 1.0)
    check("join hole", len(r3["regions"]) == 1 and len(r3["regions"][0]["holes"]) == 1)
    check("region area", near(G.loop_area(r3["regions"][0]["outer"]) + G.loop_area(r3["regions"][0]["holes"][0]),
                              1000 * 1000 - 200 * 200, 1e-6))


def test_extend():
    reg = {"outer": rect(0, 0, 6000, 3000), "holes": []}
    r = G.extend_to_boundary((500, 1500), (5000, 1500), reg)
    check("extend both ends", pnear(r["p0"], (0, 1500)) and pnear(r["p1"], (6000, 1500)))
    check("extend moved", near(r["moved"][0], 500) and near(r["moved"][1], 1000))
    # angled right edge: (6000,0)-(5000,3000)
    reg2 = {"outer": [G.line((0, 0), (6000, 0)), G.line((6000, 0), (5000, 3000)), G.line((5000, 3000), (0, 3000)),
                      G.line((0, 3000), (0, 0))], "holes": []}
    r = G.extend_to_boundary((100, 1500), (4000, 1500), reg2)
    check("extend angled", pnear(r["p1"], (5500, 1500)), r["p1"])
    check("skew reported", r["hit1"]["skew_deg"] > 10)
    # arc edge
    reg3 = G.join_curves([G.line((0, 0), (4000, 0)), G.line((4000, 0), (4000, 3000)),
                          G.arc((2000, 3000), 2000, 0, 180, True), G.line((0, 3000), (0, 0))])["regions"][0]
    r = G.extend_to_boundary((2000, 100), (2000, 3000), reg3)
    check("extend to arc", pnear(r["p1"], (2000, 5000)) and pnear(r["p0"], (2000, 0)), r)
    # stop at another element
    stop = rect(4000, 0, 4100, 3000)
    r = G.extend_to_boundary((500, 1000), (3000, 1000), reg, stops=[stop])
    check("extend to stop", pnear(r["p1"], (4000, 1000)) and r["hit1"]["on_stop"])
    try:
        G.extend_to_boundary((7000, 1000), (8000, 1000), reg)
        check("extend outside refused", False)
    except G.GeometryError:
        check("extend outside refused", True)
    r = G.extend_to_boundary((500, 1500), (5000, 1500), reg, max_move_mm=600)
    check("extend warns on long move", len(r["warnings"]) == 1)


def test_trim():
    reg2 = {"outer": [G.line((0, 0), (6000, 0)), G.line((6000, 0), (5000, 3000)), G.line((5000, 3000), (0, 3000)),
                      G.line((0, 3000), (0, 0))], "holes": []}
    r = G.trim_to_boundary((100, 1500), (4000, 1500), 100, reg2)
    out = r["outline"]
    check("trim closed", not G.check_loop_closed(out))
    # exact area: trapezoid between y=1450..1550, left x=0, right edge x = 6000 - y/3
    exact = 100 * (6000 - 1500 / 3.0)
    check("trim area exact (no wedge)", near(G.loop_area(out), exact, 1e-6), G.loop_area(out))
    check("trim not square", not r["square"])
    # square case
    r = G.trim_to_boundary((100, 1500), (4000, 1500), 40, {"outer": rect(0, 0, 6000, 3000), "holes": []})
    check("trim square", r["square"] and near(G.loop_area(r["outline"]), 40 * 6000))
    # element ending on an arc keeps the arc piece
    reg3 = G.join_curves([G.line((0, 0), (4000, 0)), G.line((4000, 0), (4000, 3000)),
                          G.arc((2000, 3000), 2000, 0, 180, True), G.line((0, 3000), (0, 0))])["regions"][0]
    r = G.trim_to_boundary((2000, 100), (2000, 3000), 200, reg3)
    check("trim arc end is arc", any(c["t"] == "arc" for c in r["outline"]))
    y = lambda x: 3000 + math.sqrt(2000 ** 2 - (x - 2000) ** 2)
    # area = integral of y(x) over 1900..2100
    n = 20000
    ex = sum(y(1900 + (i + 0.5) * 200.0 / n) for i in range(n)) * 200.0 / n
    check("trim arc area", near(G.loop_area(r["outline"]), ex, 0.5), (G.loop_area(r["outline"]), ex))
    # element crossing a corner: end path walks round the vertex
    tri = {"outer": [G.line((0, 0), (4000, 0)), G.line((4000, 0), (4000, 1000)), G.line((4000, 1000), (0, 0))],
           "holes": []}
    r = G.trim_to_boundary((1000, 200), (3500, 200), 100, tri)
    check("trim closed at slanted end", not G.check_loop_closed(r["outline"]))


def test_fascia():
    lp = rect(0, 0, 3000, 2000)
    f = G.fascia_band(lp, 15, True)
    area = G.loop_area(f["outer"]) + G.loop_area(f["holes"][0])
    check("fascia ring area", near(area, 3000 * 2000 - 2970 * 1970), area)
    check("fascia corners closed", not G.check_loop_closed(f["holes"][0]) and not G.check_loop_closed(f["outer"]))
    check("fascia one piece per loop", len(f["holes"]) == 1)
    # L-shaped (reflex corner)
    L = [G.line((0, 0), (3000, 0)), G.line((3000, 0), (3000, 1000)), G.line((3000, 1000), (1000, 1000)),
         G.line((1000, 1000), (1000, 3000)), G.line((1000, 3000), (0, 3000)), G.line((0, 3000), (0, 0))]
    f = G.fascia_band(L, 15, True)
    per = G.loop_length(L)
    area = G.loop_area(f["outer"]) + G.loop_area(f["holes"][0])
    # mitred band area = perimeter*t - (convex corners - reflex corners) * t^2
    check("fascia L area mitred", near(area, per * 15 - (5 - 1) * 15 ** 2, 1e-6), area)
    # loop with an arc, and an open chain
    reg = G.join_curves([G.line((0, 0), (4000, 0)), G.line((4000, 0), (4000, 3000)),
                         G.arc((2000, 3000), 2000, 0, 180, True), G.line((0, 3000), (0, 0))])["regions"][0]
    f = G.fascia_band(reg["outer"], 15, True)
    check("fascia arc stays arc", any(c["t"] == "arc" for c in f["holes"][0]))
    chain = [G.line((0, 0), (2000, 0)), G.line((2000, 0), (2000, 1000))]
    f = G.fascia_band(chain, 15, False)
    check("fascia open chain closed profile", not G.check_loop_closed(f["outer"]))
    check("fascia open chain area", near(G.loop_area(f["outer"]), 2000 * 15 + 1000 * 15 - 15 * 15, 1e-6),
          G.loop_area(f["outer"]))
    try:
        G.fascia_band(rect(0, 0, 20, 20), 15, True)
        check("fascia collapse refused", False)
    except G.GeometryError:
        check("fascia collapse refused", True)


def test_corners():
    # L corner with a 20.7 mm gap (outer faces offset), a collinear 5 mm gap, a far pair, other group
    segs = [{"id": 1, "p0": [0, 0], "p1": [1000, 0], "group": "a"},
            {"id": 2, "p0": [1007.5, 15], "p1": [1007.5, 800], "group": "a"},
            {"id": 3, "p0": [1005, -300], "p1": [2000, -300], "group": "a"},
            {"id": 4, "p0": [2005, -300], "p1": [3000, -300], "group": "a"},
            {"id": 5, "p0": [1000, 0], "p1": [1000, -200], "group": "b"}]
    r = G.close_corners(segs, 100.0)
    s = {x["id"]: x for x in r["segments"]}
    check("corner mitre point", pnear(s[1]["p1"], (1007.5, 0)) and pnear(s[2]["p0"], (1007.5, 0)), (s[1]["p1"], s[2]["p0"]))
    check("collinear gap joined", pnear(s[3]["p1"], (2002.5, -300)) and pnear(s[4]["p0"], (2002.5, -300)))
    check("other group untouched", s[5]["p0"] == [1000, 0])
    check("corner count", r["closed"] == 2, r)


def test_refit():
    pts = [(2000 + 2000 * math.cos(math.radians(a)), 3000 + 2000 * math.sin(math.radians(a))) for a in range(0, 181, 3)]
    pts = [(round(x, 0), round(y, 0)) for x, y in pts]  # legacy JSON rounded to 1 mm
    cv = G.refit_arcs(pts, 1.5)
    arcs = [c for c in cv if c["t"] == "arc"]
    check("refit finds arc", len(arcs) >= 1 and all(abs(a["r"] - 2000) < 2 for a in arcs), [len(cv), len(arcs)])
    cv = G.refit_arcs([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], 1.5, closed=True)
    check("refit keeps lines", all(c["t"] == "line" for c in cv) and len(cv) == 4)
    # sparse points on a straight edge (two near each end) must stay a line: an arc through them bulges 17 mm between them
    cv = G.refit_arcs([(0, 0), (5, 0.3), (10, 0.3), (2390, -0.2), (2395, 0.1), (2400, 0)], 0.5)
    check("refit: sparse points on a line are not a large-radius arc", all(c["t"] == "line" for c in cv), [(c["t"], round(c.get("r", 0))) for c in cv])


def test_bites_rhythm():
    pts = [(0, 0), (1000, 0), (1050, -87), (1150, -87), (1200, 0), (3000, 0), (3000, 3000), (0, 3000)]
    lp = [G.line(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    nl, runs = G.straighten_bites(lp, min_segs=3)
    check("bite straightened", len(runs) == 1 and near(G.loop_area(nl), 9e6))
    reg = {"outer": [G.line((0, 0), (1000, 0)), G.line((1000, 0), (1000, 2000)), G.line((1000, 2000), (0, 2000)),
                     G.line((0, 2000), (0, 0))], "holes": []}
    new = G.continue_rhythm([((x, 0), (x, 2000)) for x in (100, 200, 300)], reg)
    check("rhythm continued to the edge", sorted(round(a[0][0]) for a in new) == [400, 500, 600, 700, 800, 900])


def test_bulge():
    """polygon_to_region must not let a small arc fitted the wrong way round bulge out of the outline (a zone
    grown to a wall: an r=376 mm arc added 0.45 m2). The rebuilt loop keeps the polygon's area."""
    from shapely.geometry import Polygon
    pg = Polygon([[1510.4, 376.4], [1510.4, 376.4], [2281.2, -3540.4], [2261.7, -3544.2], [2260.9, -3539.8], [1888.9, -3613.3], [1517.4, -3689.2], [1146.4, -3767.7], [776.0, -3848.7], [-78.4, 43.3], [-77.4, 43.5], [-79.1, 51.0], [-82.8, 50.2], [-83.0, 51.2], [-60.1, 56.2], [-52.9, 57.8], [-54.7, 65.9], [-47.4, 67.4], [-40.1, 69.0], [19.9, 82.0], [39.9, 86.3], [45.4, 87.4], [59.9, 90.6], [99.9, 99.2], [119.9, 103.5], [138.5, 107.5], [159.9, 112.1], [179.9, 116.4], [219.9, 125.1], [231.0, 127.4], [239.9, 129.4], [259.9, 133.7], [279.9, 138.0], [319.9, 146.6], [323.9, 147.4], [339.9, 150.9], [359.9, 155.2], [399.9, 163.8], [416.7, 167.4], [419.9, 168.1], [459.9, 176.8], [479.9, 181.1], [486.8, 182.5], [500.0, 185.3], [510.3, 187.4], [520.0, 189.5], [580.0, 201.9], [600.0, 206.1], [606.5, 207.4], [620.0, 210.3], [680.0, 222.7], [700.0, 226.9], [702.6, 227.4], [720.0, 231.1], [780.0, 243.5], [797.4, 247.2], [880.0, 264.3], [894.9, 267.4], [900.0, 268.5], [920.0, 272.7], [927.1, 274.2], [940.0, 276.7], [980.0, 284.7], [993.6, 287.5], [1000.0, 288.7], [1020.0, 292.7], [1080.0, 304.7], [1093.6, 307.5], [1100.0, 308.7], [1120.0, 312.7], [1180.0, 324.7], [1193.7, 327.5], [1200.0, 328.7], [1220.0, 332.7], [1240.0, 336.7], [1280.0, 344.7], [1293.7, 347.5], [1300.0, 348.7], [1320.0, 352.7], [1340.0, 356.7], [1380.0, 364.7], [1393.7, 367.5], [1400.0, 368.7], [1420.0, 372.7], [1440.0, 376.7], [1480.0, 384.7], [1493.7, 387.5], [1503.6, 389.4], [1503.6, 387.5], [1523.6, 387.5], [1523.6, 383.1], [1509.7, 380.2], [1510.4, 376.4]])
    r = G.polygon_to_region(pg)
    a = abs(G.loop_area(r["outer"]))
    check("bulge: rebuilt zone keeps its area", near(a, pg.area, 0.001 * pg.area), (a, pg.area))
    check("bulge: no small arc left", not any(c["t"] == "arc" and c["r"] < 1000 for c in r["outer"]),
          [round(c["r"]) for c in r["outer"] if c["t"] == "arc"])
    # a vertex where the edge turns back on itself (4.5 mm spike at a wall corner, H1 2026-09-29): Revit rejects it
    from shapely.geometry import Polygon as _P
    spk = _P([(0, 0), (2000, 0), (2000, 1000), (50, 1000), (-4.5, 1000.2), (10, 1000.1)])
    r = G.polygon_to_region(spk)
    pts = [c["p0"] for c in r["outer"]]
    check("bulge: spike vertex dropped", all(p[0] >= -0.1 for p in pts), pts)
    thin = _P([(0, 0), (2000, 0), (2000, 1000), (0, 1000)], [[(500, 500), (564, 515.1), (522, 505.3)]])
    r = G.polygon_to_region(thin)
    check("bulge: zero-width hole dropped", not r["holes"], len(r["holes"]))
    r = G.polygon_to_region(_P([(0, 0), (3000, 0), (3000, 1000), (-1800, 1070), (0, 1000.0)]).buffer(0))
    check("bulge: long thin wedge kept", near(abs(G.loop_area(r["outer"])), 3000 * 1000 + 0.5 * 3000 * 70, 200), G.loop_area(r["outer"]))

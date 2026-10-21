"""Helpers shared by the tests ported from the ceiling-from-dwg skill's self-tests."""
from aec.geom import curves as G


def check(name, cond, info=""):
    if not cond:
        raise AssertionError("%s %s" % (name, info))


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


def pnear(p, q, tol=1e-6):
    return G._dist(p, q) <= tol


def rect(x0, y0, x1, y1):
    return [G.line((x0, y0), (x1, y0)), G.line((x1, y0), (x1, y1)), G.line((x1, y1), (x0, y1)),
            G.line((x0, y1), (x0, y0))]

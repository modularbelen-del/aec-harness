"""The old `import ceiling_geometry` surface must survive the split into aec.geom and aec.tavan."""
import ast

import aec.compat.ceiling_geometry as G
from aec.geom import curves

ORIGINAL = """EPS SHORT_CURVE_MM CLOSE_TOL_MM GeometryError _INSUNITS_MM dwg_unit_to_mm _v _add _dot _cross _norm
_unit _dist _left _ang line arc sweep_deg _apt start end reverse length tangent_at _tangent_at_point _arc_frac sample
loop_points loop_area loop_length _pip _region_loops point_in_region distance_to_curve distance_to_region_boundary
_key _dedupe join_curves _snap _nest _line_hits _all_hits extend_to_boundary _subcurve _boundary_path
trim_to_boundary _offset_curve _support_intersections _rebuild offset_chain fascia_band close_corners
check_loop_closed _circle3 refit_arcs straighten_bites continue_rhythm _shp region_to_polygon _clean_ring
polygon_to_region radial_direction _dir_deg _adiff _vec_deg piece_width find_wedges absorb_wedges cut_back
step_closures _halfplane straighten_border scan_wedges merge_slivers absorb_strip""".split()


def test_shim_exposes_every_original_name():
    assert [n for n in ORIGINAL if not hasattr(G, n)] == []


def test_single_geometry_error_class():
    assert G.GeometryError is curves.GeometryError


def test_geom_does_not_import_tavan():
    with open(curves.__file__, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imported = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    imported += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert [m for m in imported if m.startswith("aec.tavan")] == []

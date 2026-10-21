"""The old `import ceiling_geometry` surface: every name of aec.geom.curves and aec.tavan.geometry, private ones too.

Project scripts written against the ceiling-from-dwg skill keep working when they import this module under its
old name.
"""
from aec.geom import curves as _curves
from aec.tavan import geometry as _tavan

for _module in (_curves, _tavan):
    globals().update({k: v for k, v in vars(_module).items() if not k.startswith("__")})
del _module

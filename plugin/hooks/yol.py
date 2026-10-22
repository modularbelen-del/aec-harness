"""Shared path normalization for the hooks (verifier-prompt lock and verifier-report recording)."""
import os
import pathlib


def mutlak(yol: str, proje: pathlib.Path) -> str:
    """Normalized absolute path with forward slashes, lower-cased on Windows."""
    p = pathlib.Path(yol.replace("\\", "/"))
    if not p.is_absolute():
        p = pathlib.Path(proje) / p
    s = os.path.normpath(str(p)).replace("\\", "/")
    return s.lower() if os.name == "nt" else s

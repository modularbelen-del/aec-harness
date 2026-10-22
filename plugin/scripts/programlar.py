"""Open-program hint: which of Revit, AutoCAD and Rhino are running. Standard library only.

A hint only; the exact connection state comes from the MCP tools (/aec:kontrol-et).
"""
import csv
import subprocess
import sys

PROGRAMLAR = {"Revit": "revit.exe", "AutoCAD": "acad.exe", "Rhino": "rhino.exe"}


def running_programs(timeout: float = 2.0) -> "set[str] | None":
    """Names of the open programs, or None off Windows or on any error. Never raises."""
    if not sys.platform.startswith("win"):
        return None
    try:
        done = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, timeout=timeout)
        if done.returncode != 0:
            return None
        text = done.stdout.decode("utf-8", errors="replace")
        images = {row[0].casefold() for row in csv.reader(text.splitlines()) if row}
        return {name for name, exe in PROGRAMLAR.items() if exe in images}
    except Exception:
        return None


def durum_satiri(acik: "set[str] | None") -> str:
    if acik is None:
        return ""
    parts = [f"{name} {'açık' if name in acik else 'kapalı'}" for name in PROGRAMLAR]
    return "Açık programlar (ipucu): " + ", ".join(parts) + "."

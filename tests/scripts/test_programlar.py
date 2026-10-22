"""programlar: open-program hint for the session start."""
import subprocess
import sys

import programlar


def test_durum_satiri():
    assert programlar.durum_satiri({"Revit"}) == "Açık programlar (ipucu): Revit açık, AutoCAD kapalı, Rhino kapalı."
    assert programlar.durum_satiri(None) == ""


def _fake_run(stdout, returncode=0):
    def run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr=b"")
    return run


def test_running_programs_maps_names_case_insensitively(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    out = '"System","4","Services","0","10 K"\r\n"REVIT.exe","10","Console","1","1 K"\r\n"Rhino.exe","11","Console","1","1 K"\r\n'
    monkeypatch.setattr(programlar.subprocess, "run", _fake_run(out.encode("cp1254")))
    assert programlar.running_programs() == {"Revit", "Rhino"}


def test_running_programs_none_on_failure(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(programlar.subprocess, "run", _fake_run(b"", returncode=1))
    assert programlar.running_programs() is None

    def boom(*a, **k):
        raise subprocess.TimeoutExpired("tasklist", 2)
    monkeypatch.setattr(programlar.subprocess, "run", boom)
    assert programlar.running_programs() is None


def test_running_programs_none_off_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    assert programlar.running_programs() is None

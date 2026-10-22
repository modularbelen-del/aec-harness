"""Eval seti yapısı: her vakada prompt.md, her davranis.md'de yargıç ön bilgisi."""
import pathlib

EVALS = pathlib.Path(__file__).resolve().parents[1] / "plugin" / "evals"
PREMISE = "Bu deneme ortamında proje klasöründe CLAUDE.md / .aec/proje.md yoktur ve Revit, AutoCAD, Rhino bağlı değildir."


def _cases():
    return sorted(p for p in EVALS.iterdir() if p.is_dir() and p.name != "results")


def test_every_case_has_prompt():
    assert _cases()
    assert [c.name for c in _cases() if not (c / "prompt.md").is_file()] == []


def test_every_davranis_has_premise():
    files = list(EVALS.glob("*/graders/davranis.md"))
    assert files
    assert [str(f.parent.parent.name) for f in files if PREMISE not in f.read_text(encoding="utf-8")] == []


def test_ofis_disi_case_exists():
    assert (EVALS / "ofis-disi" / "graders" / "skill-yok.md").is_file()

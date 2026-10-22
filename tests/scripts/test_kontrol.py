"""kontrol: the setup report behind /aec:kontrol-et."""
import json
import pathlib

import kontrol
from _md import frontmatter

SKILLS = pathlib.Path(__file__).resolve().parents[2] / "plugin" / "skills"


def test_missing_uv(tmp_path):
    lines = kontrol.satirlar(tmp_path, tmp_path, set(), None)
    assert lines[0].startswith("✗ uv") and "kur.cmd" in lines[0]


def test_auto_update(tmp_path):
    s = tmp_path / ".claude" / "settings.json"
    s.parent.mkdir()
    s.write_text(json.dumps({"extraKnownMarketplaces": {"aec-office": {"autoUpdate": True}}}), encoding="utf-8")
    assert any(l.startswith("✓ Otomatik güncelleme") for l in kontrol.satirlar(tmp_path, tmp_path, set(), "0.13.0"))


def test_auto_update_missing_mentions_cowork(tmp_path):
    line = next(l for l in kontrol.satirlar(tmp_path, tmp_path, set(), "0.13.0") if "Otomatik güncelleme" in l)
    assert line.startswith("✗") and "Sync automatically" in line


def test_auto_update_corrupt_settings_does_not_crash(tmp_path):
    s = tmp_path / ".claude" / "settings.json"
    s.parent.mkdir()
    s.write_text("{not json", encoding="utf-8")
    line = next(l for l in kontrol.satirlar(tmp_path, tmp_path, set(), "0.13.0") if "Otomatik güncelleme" in l)
    assert line.startswith("✗")


def test_project_files(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("x", encoding="utf-8")
    lines = kontrol.satirlar(tmp_path, tmp_path, set(), "0.13.0")
    assert any(l.startswith("✓ Proje CLAUDE.md") for l in lines)
    assert any(l.startswith("✗ Proje bilgisi") and "/aec:proje-baslat" in l for l in lines)


def test_programs_unknown(tmp_path):
    assert "✗ Açık programlar: kontrol edilemedi" in "\n".join(kontrol.satirlar(tmp_path, tmp_path, None, "0.13.0"))


def test_programs_known(tmp_path):
    lines = kontrol.satirlar(tmp_path, tmp_path, {"Revit"}, "0.13.0")
    assert "✓ Açık programlar: Revit açık, AutoCAD kapalı, Rhino kapalı." in lines


def test_skill_runs_script():
    text = (SKILLS / "kontrol-et" / "SKILL.md").read_text(encoding="utf-8")
    assert frontmatter(SKILLS / "kontrol-et" / "SKILL.md")["name"] == "kontrol-et"
    assert "scripts/kontrol.py" in text and "get_revit_status" in text

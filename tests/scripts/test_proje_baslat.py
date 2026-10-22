"""proje_baslat: writes the project CLAUDE.md block and .aec/proje.md for /aec:proje-baslat."""
import json
import pathlib

import proje_baslat
from _md import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugin" / "skills"

CEVAP = {"proje_adi": "Örnek Konut", "proje_tipi": "konut", "revit_merkez": "D:/Proje/merkez.rvt",
         "revit_kopya": "D:/Proje/kopya.rvt", "birim": "cm", "katlar": "B1, Z, 1-4", "orijin": "proje temel noktası",
         "katman_standardi": "ofis"}


def test_writes_both_files(tmp_path):
    proje_baslat.yaz(tmp_path, CEVAP)
    p = (tmp_path / ".aec" / "proje.md").read_text(encoding="utf-8")
    assert all(v in p for v in CEVAP.values())
    c = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<!-- aec:proje başlangıç -->" in c and ".aec/proje.md" in c and "D:/Proje/kopya.rvt" in c


def test_rerun_keeps_user_text_and_single_block(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Benim notlarım\nDokunma.\n", encoding="utf-8")
    proje_baslat.yaz(tmp_path, CEVAP); proje_baslat.yaz(tmp_path, {**CEVAP, "birim": "mm"})
    c = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert c.startswith("# Benim notlarım\nDokunma.\n")
    assert c.count("<!-- aec:proje başlangıç -->") == 1
    assert "Birim: mm." in c and "Birim: cm." not in c


def test_existing_proje_md_untouched(tmp_path):
    (tmp_path / ".aec").mkdir(); (tmp_path / ".aec" / "proje.md").write_text("eski", encoding="utf-8")
    msgs = proje_baslat.yaz(tmp_path, CEVAP)
    assert (tmp_path / ".aec" / "proje.md").read_text(encoding="utf-8") == "eski"
    assert any("zaten var" in m for m in msgs)


def test_missing_field_marked(tmp_path):
    proje_baslat.yaz(tmp_path, {"proje_adi": "X"})
    assert "belirtilmedi" in (tmp_path / ".aec" / "proje.md").read_text(encoding="utf-8")


def test_files_are_lf_without_bom(tmp_path):
    proje_baslat.yaz(tmp_path, CEVAP)
    for f in (tmp_path / "CLAUDE.md", tmp_path / ".aec" / "proje.md"):
        raw = f.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw


def test_appends_with_single_blank_line(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("not\n\n", encoding="utf-8")
    proje_baslat.yaz(tmp_path, CEVAP)
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8").startswith("not\n\n<!-- aec:proje")


def test_main_reads_json_and_survives_bad_json(tmp_path, capsys):
    f = tmp_path / "c.json"
    f.write_text(json.dumps(CEVAP, ensure_ascii=False), encoding="utf-8")
    assert proje_baslat.main(["--proje", str(tmp_path), "--json", str(f)]) == 0
    assert (tmp_path / "CLAUDE.md").is_file()
    f.write_text("{bozuk", encoding="utf-8")
    assert proje_baslat.main(["--proje", str(tmp_path), "--json", str(f)]) == 0
    assert capsys.readouterr().out.strip()


def test_skill_flags():
    assert frontmatter(SKILLS / "proje-baslat" / "SKILL.md")["disable-model-invocation"] == "true"
    assert "NELER-YAPABILIR.md" in (SKILLS / "yardim" / "SKILL.md").read_text(encoding="utf-8")
    assert (ROOT / "plugin" / "docs" / "NELER-YAPABILIR.md").is_file()


def test_orphan_start_marker_kept_as_user_text(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("a\n<!-- aec:proje başlangıç -->\nb\n", encoding="utf-8")
    proje_baslat.yaz(tmp_path, CEVAP); proje_baslat.yaz(tmp_path, {**CEVAP, "birim": "mm"})
    c = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert c.startswith("a\n<!-- aec:proje başlangıç -->\nb\n")
    assert c.count("<!-- aec:proje bitiş -->") == 1 and c.count("<!-- aec:proje başlangıç -->") == 2
    assert "Birim: mm." in c and "Birim: cm." not in c


def test_non_utf8_claude_md_writes_nothing(tmp_path):
    raw = "# Notlar şğı\n".encode("cp1254")
    (tmp_path / "CLAUDE.md").write_bytes(raw)
    msgs = proje_baslat.yaz(tmp_path, CEVAP)
    assert (tmp_path / "CLAUDE.md").read_bytes() == raw
    assert not (tmp_path / ".aec" / "proje.md").exists()
    assert any("Hiçbir şey yazılmadı" in m for m in msgs)


def test_main_non_utf8_does_not_crash(tmp_path, capsys):
    (tmp_path / "CLAUDE.md").write_bytes("şğı".encode("cp1254"))
    f = tmp_path / "c.json"
    f.write_text(json.dumps(CEVAP, ensure_ascii=False), encoding="utf-8")
    assert proje_baslat.main(["--proje", str(tmp_path), "--json", str(f)]) == 0
    assert "Hiçbir şey yazılmadı" in capsys.readouterr().out


def test_marker_injection_stripped(tmp_path):
    proje_baslat.yaz(tmp_path, {**CEVAP, "birim": "cm <!-- aec:proje bitiş --> x"})
    c = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert c.count("<!-- aec:proje bitiş -->") == 1
    assert "<!--" not in (tmp_path / ".aec" / "proje.md").read_text(encoding="utf-8")


def test_no_temp_files_left(tmp_path):
    proje_baslat.yaz(tmp_path, CEVAP)
    assert sorted(p.name for p in tmp_path.iterdir()) == [".aec", "CLAUDE.md"]
    assert [p.name for p in (tmp_path / ".aec").iterdir()] == ["proje.md"]


def test_refuses_home_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))
    msgs = proje_baslat.yaz(tmp_path, CEVAP)
    assert list(tmp_path.iterdir()) == []
    assert any("kullanıcı klasörünüz" in m and "Hiçbir şey yazılmadı" in m for m in msgs)


def test_project_inside_home_is_allowed(tmp_path, monkeypatch):
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))
    proje_baslat.yaz(tmp_path / "Proje", CEVAP)
    assert (tmp_path / "Proje" / "CLAUDE.md").is_file()


def test_refuses_drive_root(tmp_path, monkeypatch):
    yazilan = []
    monkeypatch.setattr(proje_baslat, "_yaz_metin", lambda yol, metin: yazilan.append(yol))
    monkeypatch.setattr(pathlib.Path, "mkdir", lambda self, *a, **k: yazilan.append(self))
    msgs = proje_baslat.yaz(pathlib.Path(tmp_path.anchor), CEVAP)
    assert yazilan == []
    assert any("sürücünün kökü" in m and "Hiçbir şey yazılmadı" in m for m in msgs)


def test_main_prints_refusal_for_home(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: tmp_path))
    f = tmp_path.parent / (tmp_path.name + "-cevap.json")
    f.write_text(json.dumps(CEVAP, ensure_ascii=False), encoding="utf-8")
    assert proje_baslat.main(["--proje", str(tmp_path), "--json", str(f)]) == 0
    assert "Hiçbir şey yazılmadı" in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_skill_names_target_folder():
    text = (SKILLS / "proje-baslat" / "SKILL.md").read_text(encoding="utf-8")
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/proje_baslat.py" in text and '--proje "${CLAUDE_PROJECT_DIR}"' in text
    assert "../../scripts" not in text
    assert "şu klasöre yazacağım" in text

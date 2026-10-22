import pathlib
import re

import onkapi

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ["BASLA", "NELER-YAPABILIR", "ORNEK-ISTEKLER", "GUVENLIK", "SORUN-GIDERME", "SOZLUK"]


def test_docs_exist():
    assert all((ROOT / "plugin/docs" / f"{d}.md").is_file() for d in DOCS)
    assert (ROOT / "CHANGELOG.md").is_file()


def test_relative_links_resolve():
    for md in [ROOT / "README.md", *(ROOT / "plugin/docs").glob("*.md")]:
        for target in re.findall(r"\]\((?!https?://|#)([^)#]+)", md.read_text(encoding="utf-8")):
            assert (md.parent / target).exists(), f"{md.name} -> {target}"


def test_examples_cover_every_card():
    text = (ROOT / "plugin/docs/ORNEK-ISTEKLER.md").read_text(encoding="utf-8")
    assert all(f"## {c['baslik']}" in text for c in onkapi.load_cards())


def test_basla_covers_both_paths():
    text = (ROOT / "plugin/docs/BASLA.md").read_text(encoding="utf-8")
    for s in ("Cowork", "Customize", "Sync automatically", "kur.ps1", "/aec:kontrol-et", "/aec:proje-baslat"):
        assert s in text

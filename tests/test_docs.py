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


def _sections(text):
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    return {p.split("\n", 1)[0].strip(): p for p in parts}


def test_examples_list_each_cards_missing_items():
    text = (ROOT / "plugin/docs/ORNEK-ISTEKLER.md").read_text(encoding="utf-8")
    secs = _sections(text)
    for c in onkapi.load_cards():
        sec = secs[c["baslik"]].lower()
        for e in c["eksikler"]:
            assert e.lower() in sec or " ".join(e.lower().split()[:2]) in sec, (c["baslik"], e)
        assert "**durum:**" in sec.split("\n", 3)[2] or "**durum:**" in sec[:200], c["baslik"]
    assert "Fiyat" not in secs["Metraj/liste"]


def test_each_example_routes_to_its_own_card():
    text = (ROOT / "plugin/docs/ORNEK-ISTEKLER.md").read_text(encoding="utf-8")
    secs = _sections(text)
    cards = onkapi.load_cards()
    for c in cards:
        examples = re.findall(r"\*\*Böyle yazın:\*\* `([^`]+)`", secs[c["baslik"]])
        assert examples, c["baslik"]
        for ex in examples:
            assert c["id"] in onkapi.match(ex, cards), (c["id"], ex, onkapi.match(ex, cards))

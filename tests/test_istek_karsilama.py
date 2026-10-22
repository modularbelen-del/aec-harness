"""istek-karsilama skill: card files match kartlar.json, headings stay in order, the description carries the triggers."""
import pathlib

import onkapi
from _md import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "plugin" / "skills" / "istek-karsilama"
SKILL = SKILL_DIR / "SKILL.md"
KARTLAR = SKILL_DIR / "kartlar"
HEADINGS = ["## Tanıma", "## Kritik gerekenler", "## İkincil", "## Proje MD'sinde nerede",
            "## Skill / araç", "## Plan şablonu", "## Geri okuma", "## Yapamıyorsam"]


def test_cards_match_json_both_ways():
    ids = {c["id"] for c in onkapi.load_cards()}
    files = {p.stem for p in KARTLAR.glob("*.md")}
    assert ids == files


def test_card_headings_in_order():
    for p in KARTLAR.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        pos = [text.index(h) for h in HEADINGS]
        assert pos == sorted(pos), p.name


def test_skill_frontmatter_triggers():
    fm = frontmatter(SKILL)
    assert fm["name"] == "istek-karsilama"
    for word in ("Revit", "DWG", "AutoCAD", "Rhino", "metraj", "tavan"):
        assert word in fm["description"]
    assert len(fm["description"]) <= 1024


def test_unbuilt_jobs_say_so():
    assert "yakında" in (KARTLAR / "render.md").read_text(encoding="utf-8")
    tavan = (KARTLAR / "tavan.md").read_text(encoding="utf-8")
    assert "ceiling-from-dwg" in tavan and "yakında" in tavan


def test_critical_items_start_with_json_eksikler():
    for card in onkapi.load_cards():
        text = (KARTLAR / f"{card['id']}.md").read_text(encoding="utf-8")
        section = text[text.index("## Kritik gerekenler"):text.index("## İkincil")]
        bullets = [line[2:] for line in section.splitlines() if line.startswith("- ")]
        firsts = bullets[:len(card["eksikler"])]
        assert len(firsts) == len(card["eksikler"]), card["id"]
        for item, bullet in zip(card["eksikler"], firsts):
            assert item in bullet, (card["id"], item)


def _card(card_id):
    return (KARTLAR / f"{card_id}.md").read_text(encoding="utf-8")


def test_rules_stay_in_skill_and_cards():
    skill = SKILL.read_text(encoding="utf-8")
    assert "save_document" in skill and "sync_with_central" in skill
    assert "soru sormadan önce" in skill
    assert "birim fiyat" in _card("metraj-liste")
    assert "Faz 1B" in _card("dwg-okuma")
    assert "Faz 1D" in _card("tavan")


def test_dxf_route_needs_code():
    for card_id in ("dwg-okuma", "metraj-liste"):
        assert "kod çalıştırabiliyorsan" in _card(card_id), card_id


def test_revit_card_promises_no_single_undo():
    assert "tek geri al" not in _card("revit-modelleme")


def test_frontmatter_reads_first_block_only(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\nname:  a \ndescription: b: c\n---\nkey: not read\n---\n", encoding="utf-8")
    assert frontmatter(p) == {"name": "a", "description": "b: c"}


def test_frontmatter_needs_leading_fence(tmp_path):
    p = tmp_path / "y.md"
    p.write_text("# Başlık\n---\nname: a\n---\n", encoding="utf-8")
    assert frontmatter(p) == {}
    p.write_bytes("﻿---\nname: a\n---\n".encode("utf-8"))
    assert frontmatter(p) == {"name": "a"}


def test_skill_does_not_follow_wrong_card_blindly():
    skill = SKILL.read_text(encoding="utf-8")
    step1 = skill[skill.index("1. **Kartı seç.**"):skill.index("2. **Kartı oku.**")]
    assert "uymuyorsa" in step1 and "tabloyla yeniden eşleştir" in step1

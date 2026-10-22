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


def _one_liners(text):
    return [ln for ln in text.splitlines() if "irm https://" in ln]


def test_dev_one_liner_fetches_dev_branch():
    for path in (ROOT / "plugin/docs/BASLA.md", ROOT / "kur.ps1"):
        lines = _one_liners(path.read_text(encoding="utf-8-sig"))
        dev = [ln for ln in lines if "AEC_KANAL='dev'" in ln]
        stable = [ln for ln in lines if "AEC_KANAL" not in ln]
        assert dev and stable, path.name
        assert all("/aec-harness/dev/kur.ps1" in ln for ln in dev), path.name
        assert all("/aec-harness/main/kur.ps1" in ln for ln in stable), path.name


def test_basla_pilot_dev_line_and_project_folder():
    text = (ROOT / "plugin/docs/BASLA.md").read_text(encoding="utf-8")
    secs = _sections(text)
    assert "pilot" in secs["Kanallar"].lower()
    assert "projenin klasöründe başlatın" in secs["Terminal kullanıyorsanız"]
    assert "hiçbir dosyayı değiştirmez" not in text


def _doc(name):
    return (ROOT / "plugin/docs" / f"{name}.md").read_text(encoding="utf-8")


def test_docs_do_not_state_model_rules_as_guarantees():
    guv, neler = _doc("GUVENLIK"), _doc("NELER-YAPABILIR")
    for phrase in ("dosyaları değişmez", "kendiliğinden yapmaz", "Siz onaylamadan hiçbir şey değişmez",
                   "eklenti yine çalışır", "Eklenti bunlara uyar", "Orijinal dosyaya yazılmaz, eşitlemeyi"):
        assert phrase not in guv and phrase not in neler, phrase
    assert "ayarlandı" in guv and "ayarlandı" in neler
    assert "izin ekranını okuyun" in guv
    assert "Yine de kaynağı" not in guv
    assert "Revit köprüsü (Faz 1C)" in neler and "temel" in neler


def test_readme_states_goals_not_facts():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    opening = text.split("## Durum")[0]
    assert "Hedef" in opening and "geri okur ve sonucu toleransla doğrular" not in opening
    rol = text[text.index("- `plugin/standards/rol.md`"):text.index("- `plugin/standards/authority.md`")]
    assert "aracı oturumda varsa" in rol and "yalnızca" in rol


def test_hook_error_not_blamed_on_uv():
    sec = _sections(_doc("SORUN-GIDERME"))['"hook error"']
    assert "uv` yoktur" not in sec
    assert "yeniden" in sec and "sorumlu" in sec

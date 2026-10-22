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
        examples = re.findall(r"\*\*Önerilen istek:\*\* `([^`]+)`", secs[c["baslik"]])
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
    assert "projenin klasöründe başlatın" in secs["Terminal ile kurulum"]
    assert "hiçbir dosyayı değiştirmez" not in text


def _doc(name):
    return (ROOT / "plugin/docs" / f"{name}.md").read_text(encoding="utf-8")


def test_docs_do_not_state_model_rules_as_guarantees():
    guv, neler = _doc("GUVENLIK"), _doc("NELER-YAPABILIR")
    for phrase in ("dosyaları değişmez", "kendiliğinden yapmaz", "Siz onaylamadan hiçbir şey değişmez",
                   "eklenti yine çalışır", "Eklenti bunlara uyar", "Orijinal dosyaya yazılmaz, eşitlemeyi"):
        assert phrase not in guv and phrase not in neler, phrase
    assert "yapılandırılmıştır" in guv and "yapılandırılmıştır" in neler
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


def _readme_section(baslik):
    return _sections((ROOT / "README.md").read_text(encoding="utf-8")).get(baslik, "")


def test_readme_has_workflow_section():
    sec = _readme_section("İş akışı")
    assert sec, "README'de '## İş akışı' bölümü yok"
    for s in ("aec:dogrulayici", '"evet"', '"hayır"', "sync_with_central", "save_document",
              ".aec/isler", ".aec/gunluk.md", "kazara", "kasıtlı", "DOĞRULANAMADI", "Faz 1C"):
        assert s in sec, s


def test_guvenlik_describes_lock_honestly():
    guv = _doc("GUVENLIK")
    for s in ("kazara", "kasıtlı", "sync_with_central", "save_document", "Cowork"):
        assert s in guv, s
    assert "Kaydetme ve merkez modelle eşitleme (sync) tüm ekibi etkilediğinden" not in guv  # save is allowed after acceptance


def test_third_party_notices():
    text = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for s in ("github/spec-kit", "obra/superpowers", "MIT", "Copyright GitHub, Inc.",
              "Copyright (c) 2025 Jesse Vincent"):
        assert s in text, s
    # the MIT body is the same as the repo's own LICENSE below its copyright line; both copies must be verbatim
    govde = "\n".join((ROOT / "LICENSE").read_text(encoding="utf-8").splitlines()[3:])
    assert text.count(govde) == 2
    for yol in [ROOT / "plugin/skills/istek-karsilama/gorusme.md",
                *(ROOT / "plugin/skills/istek-karsilama/sablonlar").glob("*.md")]:
        kaynak = re.search(r"^Uyarlanmıştır: ([\w.-]+/[\w.-]+),", yol.read_text(encoding="utf-8"), re.M)
        assert kaynak, yol.name
        assert kaynak.group(1) in text and yol.name in text, yol.name


def test_changelog_mentions_workflow():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    sec = _sections(text).get("Yayınlanmamış (dev)", "")
    for s in ("kontrolcü", "aec:dogrulayici", "THIRD_PARTY_NOTICES.md"):
        assert s in sec, s


def test_docs_describe_continue_path():
    basla, sorun, guv = _doc("BASLA"), _doc("SORUN-GIDERME"), _doc("GUVENLIK")
    readme = _readme_section("İş akışı")
    assert "kaldığı yerden sürdürülmez" not in basla and "eski işi size bildirerek kapatır" not in basla
    assert "yeni oturumda sürdürülmez" not in " ".join(readme.split())
    assert "İş önceki bir oturumda açılmışsa yeni bir iş açılır" not in sorun
    for ad, metin in (("BASLA", basla), ("README", readme), ("SORUN-GIDERME", sorun), ("GUVENLIK", guv)):
        tek = " ".join(metin.split())
        assert "devam" in tek and "yeniden" in tek and "bu oturumda açılmış" not in tek, ad
    for ad, metin in (("BASLA", basla), ("README", readme)):
        assert "iptal" in metin, ad


def test_sorun_giderme_quotes_real_lock_messages():
    import onay
    import pre_tool

    text = _doc("SORUN-GIDERME")
    assert "Bu mesaj onay olarak kaydedilmedi" in onay.BELIRSIZ_METNI
    assert "Bu mesaj onay olarak kaydedilmedi" in text
    assert pre_tool.NEDEN_IS_YOK.split(". ")[0] in text
    assert '"evet"' in text
    # an unreadable job record goes to the office's system contact, as the page says; kontrol-et cannot repair it
    okunamadi = _sections(text)["Revit'e yazma reddedildi ya da onay kaydedilmedi"]
    okunamadi = okunamadi[okunamadi.index('**"İş kaydı okunamadı":**'):].split("\n- ")[0]
    assert "kontrol-et" not in pre_tool.NEDEN_OKUNAMADI and "kontrol-et" not in okunamadi
    for parca in ("İş kaydı okunamadı", "elle düzenlen", "sistem sorumlusuna iletil"):
        assert parca in pre_tool.NEDEN_OKUNAMADI and parca in okunamadi, parca
    # a plugin file that failed to load is an installation problem: kontrol-et applies there
    assert pre_tool.NEDEN_BILESEN.split(";")[0] in text and "/aec:kontrol-et" in pre_tool.NEDEN_BILESEN

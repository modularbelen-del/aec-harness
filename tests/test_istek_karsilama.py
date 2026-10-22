"""istek-karsilama skill: card files match kartlar.json, headings stay in order, the description carries the triggers,
and the job flow (complexity rule, interview guide, templates, approval wording) is wired in."""
import pathlib
import re

import is_durumu
import onkapi
from _md import frontmatter

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "plugin" / "skills" / "istek-karsilama"
SKILL = SKILL_DIR / "SKILL.md"
KARTLAR = SKILL_DIR / "kartlar"
SABLONLAR = SKILL_DIR / "sablonlar"
GORUSME = SKILL_DIR / "gorusme.md"
STANDARDS = ROOT / "plugin" / "standards"
HEADINGS = ["## Tanıma", "## Kritik gerekenler", "## İkincil", "## Proje MD'sinde nerede",
            "## Skill / araç", "## Plan şablonu", "## Kabul ölçütleri", "## Geri okuma", "## Yapamıyorsam"]
KARMASIK = {"revit-modelleme": True, "dwg-cizim": True, "rhino-revit": True, "tavan": True,
            "dwg-okuma": False, "metraj-liste": False, "render": False}
REVIT_YAZAN = ("revit-modelleme", "rhino-revit", "tavan")
YONTEM = re.compile(r"\((?:revit-okuma|dosya|olcu|kisi-gorsel)[);]")
ONAY_CUMLESI = "Onaylıyorsanız yalnızca 'evet', reddediyorsanız yalnızca 'hayır' yazınız."
KABUL_CUMLESI = "Kabul ediyorsanız yalnızca 'evet', etmiyorsanız yalnızca 'hayır' yazınız."
UYARLAMA = "Uyarlanmıştır:"


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


def _bolum(text, bas, son):
    return text[text.index(bas):text.index(son)]


def _tek(metin):
    return " ".join(metin.split())


def test_card_length_bounds():
    for p in KARTLAR.glob("*.md"):
        satir = len(p.read_text(encoding="utf-8").splitlines())
        assert 25 <= satir <= 70, (p.name, satir)


def test_cards_have_complexity_defaults():
    assert {c["id"]: c.get("karmasik") for c in onkapi.load_cards()} == KARMASIK


def test_cards_have_acceptance_section():
    for p in KARTLAR.glob("*.md"):
        assert "## Kabul ölçütleri" in p.read_text(encoding="utf-8"), p.name
    for card_id in REVIT_YAZAN:
        bolum = _bolum(_card(card_id), "## Kabul ölçütleri", "## Geri okuma")
        assert "(revit-okuma)" in bolum and "kopya" in bolum and "(olcu;" in bolum, card_id
        assert "DOĞRULANAMADI" in bolum, card_id
    metraj = _bolum(_card("metraj-liste"), "## Kabul ölçütleri", "## Geri okuma")
    assert "(dosya)" in metraj and "toplam" in metraj and "fiyat" in metraj
    render = _bolum(_card("render"), "## Kabul ölçütleri", "## Geri okuma")
    assert "(kisi-gorsel)" in render and "(dosya)" in render and "müşteri adı" in render


def test_acceptance_items_have_method():
    for p in KARTLAR.glob("*.md"):
        bolum = _bolum(p.read_text(encoding="utf-8"), "## Kabul ölçütleri", "## Geri okuma")
        maddeler = [s for s in bolum.splitlines() if s.startswith("- ")]
        assert 2 <= len(maddeler) <= 4, p.name
        for madde in maddeler:
            assert YONTEM.search(madde), (p.name, madde)


def test_card_plans_do_not_ask_their_own_approval():
    for p in KARTLAR.glob("*.md"):
        assert "Onaylıyor musunuz" not in p.read_text(encoding="utf-8"), p.name


def test_skill_mentions_flow_pieces():
    skill = SKILL.read_text(encoding="utf-8")
    for parca in ("is_kaydi.py", "aec:dogrulayici", "${CLAUDE_PLUGIN_ROOT}/standards/karmasiklik.md", "gorusme.md",
                  "sablonlar/", ONAY_CUMLESI, KABUL_CUMLESI, "[aec] Onayınız kaydedildi",
                  "[aec] Kabulünüz kaydedildi", "onay-bekliyor", "kabul-bekliyor"):
        assert parca in skill, parca
    ask = [s for s in skill.splitlines() if "AskUserQuestion" in s]
    assert any("onay" in s and "kabul" in s and "kullanılmaz" in s for s in ask)
    bekleme = _tek(skill[skill.index("**Bekleme kuralı:**"):skill.index("**Yumuşak mod:**")])
    for parca in ("`onay-bekliyor:<aşama>` ya da `kabul-bekliyor` durumundayken", "başka hiçbir evet/hayır sorusu sorma",
                  "bekleyen onay ya da kabul olarak kaydedilir", "`AskUserQuestion` kullan"):
        assert parca in bekleme, parca
    assert "plan onayı, bağımsız kontrol ve kabul" in frontmatter(SKILL)["description"]


def test_skill_never_lets_agent_approve():
    skill = SKILL.read_text(encoding="utf-8")
    assert not re.search(r"is_kaydi\.py\S*\s+(onay|kabul)\b", skill)
    assert "kısa bir cevap onaydır" not in skill  # the agent no longer interprets approval itself
    assert "yumuşak mod" in skill and "izin penceresi" in skill


def test_templates_exist_and_netlestir_cap():
    for ad in ("tarif", "plan", "gorevler"):
        assert (SABLONLAR / f"{ad}.md").is_file(), ad
    tarif = (SABLONLAR / "tarif.md").read_text(encoding="utf-8")
    assert 1 <= tarif.count("[NETLEŞTİR") <= 3
    for baslik in ("## Amaç", "## Kapsam", "## Kapsam dışı", "## Kabul ölçütleri"):
        assert baslik in tarif, baslik
    plan = (SABLONLAR / "plan.md").read_text(encoding="utf-8")
    assert "## Adımlar" in plan and "kopya dosya" in plan.lower() and "VARSAYIM" in plan
    assert "## Geri dönüş yolu" in plan
    gorevler = (SABLONLAR / "gorevler.md").read_text(encoding="utf-8")
    assert "Kabul ölçütü:" in gorevler
    for p in (SABLONLAR / "tarif.md", SABLONLAR / "plan.md", SABLONLAR / "gorevler.md", GORUSME):
        assert UYARLAMA in p.read_text(encoding="utf-8"), p.name


def test_interview_guide_covers_topics():
    rehber = GORUSME.read_text(encoding="utf-8")
    for parca in ("Amaç", "Kapsam", "Kapsam dışı", "Mevcut durum", "Kabul ölçütleri", "150–250", "VARSAYIM",
                  "numaralı liste", "tek tek", "Onay olmadan uygulama yapılmaz"):
        assert parca in rehber, parca


def test_complexity_rule_text():
    kural = (STANDARDS / "karmasiklik.md").read_text(encoding="utf-8")
    assert "çizim veya model" in kural and "oluşturan ya da değiştiren" in kural
    assert "onaydan önce" in kural
    for card_id in KARMASIK:
        assert card_id in kural, card_id


def test_authority_rules():
    kural = (STANDARDS / "authority.md").read_text(encoding="utf-8")
    assert "kontrolcü" in kural and "kabul" in kural and "aec:dogrulayici" in kural
    assert "3 soru sınırı uygulanmaz" in kural


def test_skill_marks_non_revit_jobs_applied_before_verifier():
    skill = SKILL.read_text(encoding="utf-8")
    adim = skill[skill.index("### 9."):skill.index("### 10.")]
    assert "`uygulandi --is" in skill and adim.index("uygulandi") < adim.index("aec:dogrulayici")
    assert "zararsızdır" in adim  # running it after a Revit write is harmless
    assert "bağımsız kontrolcü raporu değildir" not in skill and "kabul sorusunu sorma" not in adim


def test_soft_mode_follows_stage():
    skill = SKILL.read_text(encoding="utf-8")
    bolum = _bolum(skill, "**Yumuşak mod:**", "## Her işte")
    maddeler = [_tek(m) for m in bolum.split("\n  - ")[1:]]
    for durum in is_durumu.DURUMLAR:  # every state named, and only in one bullet (plan differs by class)
        sayi = sum(f"`{durum}`" in m for m in maddeler)
        assert sayi == (2 if durum == "onay-bekliyor:plan" else 1), (durum, sayi)
    son = next(m for m in maddeler if "`onay-bekliyor:gorevler`" in m)
    assert "basit işte `onay-bekliyor:plan`" in son and "uygulamaya geç" in son
    onceki = next(m for m in maddeler if "`onay-bekliyor:tarif`" in m)
    assert "karmaşık işte `onay-bekliyor:plan`" in onceki and "sabit onay cümlesiyle" in onceki
    assert "kaydetmeden" in onceki
    izin = [m for m in maddeler if "izin penceresi" in m]
    assert len(izin) == 1 and "Yalnızca Revit işinde" in izin[0]
    assert "bağımsız kontrol ve kabul bu oturumda kaydedilemeyecektir" in izin[0]


def test_apply_and_verify_steps():
    skill = SKILL.read_text(encoding="utf-8")
    uygula = _tek(_bolum(skill, "### 8.", "### 9."))
    assert "Geri okuma" in uygula and "yalnızca okuma araçlarıyla" in uygula and "kontrolcüden önce" in uygula
    assert "kontrolcü raporunun yerine geçmez" in uygula
    assert "`reddedildi`" in uygula and "9. adıma" in uygula  # re-planning after something was written
    kontrol = _tek(_bolum(skill, "### 9.", "### 10."))
    assert "her zaman çalıştır" in kontrol and "hiçbir şeyi değiştirmez" in kontrol
    assert "kişiye bildir ve dur" in kontrol
    assert "`reddedildi`" in _tek(GORUSME.read_text(encoding="utf-8"))


def test_draft_exception_main_card_and_criteria_shown():
    skill = _tek(SKILL.read_text(encoding="utf-8"))
    assert "Tek istisna" in skill and "yalnızca `.aec/taslak/`" in skill
    assert "`.aec/taslak/`" in _tek(GORUSME.read_text(encoding="utf-8"))
    assert "`yeni --kart` için karmaşık kartı" in skill
    dort = _tek(_bolum(SKILL.read_text(encoding="utf-8"), "### 4.", "### 5."))
    assert "Kişiye gösterilip kesinleşen" in dort and "kişinin görmediği bir ölçütü kaydetme" in dort


def test_readback_wording_and_ceiling_skill():
    revit = _card("revit-modelleme")
    assert "aynı Revit aracıyla" not in revit and "Revit okuma araçlarıyla" in revit
    tavan = _tek(_card("tavan"))
    assert "görüşmede" in tavan and "okuma ve çözümleme" in tavan and "onaylı planla" in tavan
    kural = (STANDARDS / "authority.md").read_text(encoding="utf-8")
    assert "geri okuyup doğrula" not in kural and "Revit okuma araçlarıyla" in kural


def test_skill_keeps_substituted_paths_in_powershell():
    skill = SKILL.read_text(encoding="utf-8")
    assert "$env:CLAUDE_" not in skill
    arac = _tek(_bolum(skill, "## İş kaydı aracı", "## Akış"))
    assert "PowerShell'de de" in arac and "`$env:` biçimini kullanma" in arac and "aynen" in arac


def test_complex_job_revises_earlier_document_by_rejection():
    yedi = _tek(_bolum(SKILL.read_text(encoding="utf-8"), "### 7.", "### 8."))
    assert ('Karmaşık işte kişi önceki bir belgenin değişmesini isterse bekleyen onay sorusuna "hayır" yazar ve '
            "gerekçesini belirtir; ret kaydedildikten sonra akış o belgeye döner.") in yedi


def test_soft_mode_skips_verifier_step():
    uygula = _tek(_bolum(SKILL.read_text(encoding="utf-8"), "### 8.", "### 9."))
    assert uygula.count("9. adıma geç") == uygula.count("yumuşak mod dışında 9. adıma geç") >= 2


def test_skill_checks_binding_before_soft_mode():
    skill = SKILL.read_text(encoding="utf-8")
    yedi = _tek(_bolum(skill, "### 7.", "### 8."))
    assert "[aec] Bu oturuma bağlı bir iş bulunmadığından" in yedi and "`devam --is <kimlik>`" in yedi
    bas = skill.index("**Yumuşak mod:**")
    giris = _tek(skill[bas:skill.index("\n  - ", bas)])  # the lead sentence, before the per-state bullets
    assert "yumuşak moda geçmeden önce" in giris and "`durum`" in giris and "`devam --is <kimlik>`" in giris


def test_skill_continues_open_jobs_with_devam():
    metin = SKILL.read_text(encoding="utf-8")
    skill = _tek(metin)
    assert "| `devam --is <kimlik>` |" in metin
    assert "bu oturuma bağlanamaz" not in skill and "önceki oturumdan kalan iş)" not in skill
    her = _tek(metin[metin.index("## Her işte"):])
    for parca in ("`devam --is <kimlik>`", "`onay-bekliyor:plan`", "yeniden", "`iptal`"):
        assert parca in her, parca

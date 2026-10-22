import unicodedata

import onkapi

CARDS = onkapi.load_cards()


def test_normalize_turkish():
    assert onkapi.normalize("Revit'te TAVANI İç Kapı, DWG’den!") == "revitte tavani ic kapi dwgden"


def test_ascii_and_turkish_route_same():
    a = onkapi.match("Revit'te 3. kata kapı yerleştir", CARDS)
    b = onkapi.match("revitte 3. kata kapi yerlestir", CARDS)
    assert a == b == ["revit-modelleme"]


def test_suffix_tolerance():
    assert set(onkapi.match("tavanı DWG'den çıkar", CARDS)) == {"tavan", "dwg-okuma"}


def test_everyday_words_do_not_route():
    assert onkapi.match("yarın toplantıdan önce bana kısa bir özet al", CARDS) == []
    assert "revit-modelleme" not in onkapi.match("katmanları düzelt", CARDS)
    assert onkapi.match("bana detaylı anlat", CARDS) == []
    assert "metraj-liste" not in onkapi.match("klasördeki dosyaları listele", CARDS)


def test_rhino_to_revit():
    assert "rhino-revit" in onkapi.match("Rhino'daki cepheyi Revit'e geçir", CARDS)


def test_at_most_two_cards():
    assert len(onkapi.match("revit dwg autocad metraj rhino tavan render", CARDS)) == 2


def test_card_text_fits_and_names_paths(tmp_path):
    text = onkapi.card_text(["revit-modelleme", "metraj-liste"], CARDS, tmp_path)
    assert len(text.encode("utf-8")) <= 1024
    assert len(onkapi.card_text(["tavan"], CARDS, tmp_path).encode("utf-8")) <= 700  # spec: tek kart ~600 bayt
    assert text.startswith("[aec ön kapı] İş: Revit modelleme, Metraj/liste.")
    assert "revit-modelleme.md" in text and "VARSAYIM" in text and "en fazla 3 soru" in text


def test_same_card_once_per_session(tmp_path):
    assert onkapi.unseen("s1", ["tavan"], tmp_path) == ["tavan"]
    assert onkapi.unseen("s1", ["tavan", "render"], tmp_path) == ["render"]
    assert onkapi.unseen("s2", ["tavan"], tmp_path) == ["tavan"]


def test_revit_draw_is_not_autocad():
    assert onkapi.match("Revit'te 2. kata duvar çiz", CARDS) == ["revit-modelleme"]


def test_autocad_draw_routes():
    assert "dwg-cizim" in onkapi.match("AutoCAD'de yeni bir detay çiz", CARDS)
    assert "dwg-cizim" in onkapi.match("bu DWG'ye kesit detayını çiz", CARDS)


def test_rhino_transfer_with_aktar():
    assert "rhino-revit" in onkapi.match("Rhino'daki cepheyi Revit'e aktar", CARDS)


def test_dwg_draw_noun_forms_do_not_route_to_cizim():
    for p in ("DWG çizimini oku", "DWG çizimindeki katmanları listele",
              "Revit'teki detay çizimlerini kontrol et", "Revit'te çizimi düzelt"):
        assert "dwg-cizim" not in onkapi.match(p, CARDS), p


def test_dwg_draw_verb_forms_route_to_cizim():
    for p in ("AutoCAD'de yeni bir detay çiz", "bu DWG'ye kesit detayını çiz", "DWG'ye çiz"):
        assert "dwg-cizim" in onkapi.match(p, CARDS), p


def test_mahal_rooms_vs_neighbourhood():
    assert "metraj-liste" in onkapi.match("zemin kattaki mahalleri listele", CARDS)
    assert "metraj-liste" in onkapi.match("mahallerde net alan", CARDS)
    assert "metraj-liste" not in onkapi.match("Kadıköy mahallesindeki proje için not yaz", CARDS)


def test_kolon_and_m2_boundaries():
    assert "revit-modelleme" not in onkapi.match("kolonya şişesi", CARDS)
    assert "revit-modelleme" in onkapi.match("kolonları yerleştir", CARDS)
    assert "metraj-liste" not in onkapi.match("M20 cıvata", CARDS)
    assert "metraj-liste" in onkapi.match("toplam m² ne", CARDS)


def test_unicode_decomposed_and_acute_apostrophe():
    nfd = unicodedata.normalize("NFD", "kapı yerleştir")
    assert onkapi.match("revit " + nfd, CARDS) == ["revit-modelleme"]
    assert "dwg-cizim" in onkapi.match("DWG´ye çiz", CARDS)
    assert onkapi.normalize("m²") == "m2"


def test_regex_keyword_prefix_and_bad_regex():
    cards = [{"id": "a", "baslik": "A", "anahtar": ["re:ab+c", "re:("], "eksikler": []}]
    assert onkapi.match("xx abbc", cards) == ["a"]
    assert onkapi.match("zabc", cards) == []


def test_seen_any(tmp_path):
    assert onkapi.seen_any("s", tmp_path) is False
    onkapi.unseen("s", ["tavan"], tmp_path)
    assert onkapi.seen_any("s", tmp_path) is True
    assert onkapi.seen_any("other", tmp_path) is False

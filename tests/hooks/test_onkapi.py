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

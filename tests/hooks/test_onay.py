"""onay: approval and rejection recognised from the person's own message."""
import pytest

import is_durumu
import onay

OTURUM = "oturum-a"


def _is(tmp_path, durum, karmasik=False, oturum=OTURUM):
    kayit = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Kapı", karmasik)
    kayit["durum"] = durum
    is_durumu.is_kaydet(tmp_path, kayit)
    is_durumu.aktif_bagla(tmp_path, oturum, kayit["id"])
    return kayit


def test_plain_approvals():
    for m in ("evet", "Evet.", "onaylıyorum", "uygula lütfen", "evet tamam", "devam et", "EVET"):
        assert onay.siniflandir(m) == "onay", m


def test_plain_rejections():
    for m in ("hayır", "iptal", "vazgeçtim", "durdur lütfen"):
        assert onay.siniflandir(m) == "ret", m


@pytest.mark.parametrize("m", [
    "evet ama önce kapıyı 90 yap", "olur mu?", "tamam anladım", "uygulamadan önce bir sorum var",
    "kabul ölçütü 4 olsun", "evet mi?", "tamam", "evet değil", "evet hayır", "",
])
def test_ambiguous_messages_do_not_approve(m):
    assert onay.siniflandir(m) == "belirsiz"


def test_more_than_four_words_ambiguous():
    assert onay.siniflandir("evet evet evet evet evet") == "belirsiz"


def test_yes_outside_waiting_state_ignored(tmp_path):
    _is(tmp_path, "gorusme")
    assert onay.isle(tmp_path, OTURUM, "evet") is None
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "gorusme"


def test_approval_advances_and_logs(tmp_path):
    _is(tmp_path, "onay-bekliyor:plan")
    metin = onay.isle(tmp_path, OTURUM, "evet")
    kayit = is_durumu.aktif_is(tmp_path, OTURUM)
    assert kayit["durum"] == "plan-onaylandi"
    assert kayit["olaylar"][-1]["kaynak"] == "kullanici-mesaji"
    assert metin == "[aec] Onayınız kaydedildi: plan. Uygulamaya geçilebilir."


def test_complex_three_stage_approvals(tmp_path):
    for baslangic, beklenen in (("tarif", "onaylandi:tarif"), ("plan", "onaylandi:plan"),
                                ("gorevler", "plan-onaylandi")):
        _is(tmp_path, f"onay-bekliyor:{baslangic}", karmasik=True)
        onay.isle(tmp_path, OTURUM, "evet")
        assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == beklenen


def test_acceptance_and_rejection(tmp_path):
    _is(tmp_path, "kabul-bekliyor")
    assert "Kabulünüz kaydedildi" in onay.isle(tmp_path, OTURUM, "kabul ediyorum")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "kabul-edildi"
    gunluk = (tmp_path / ".aec/gunluk.md").read_text(encoding="utf-8")
    assert "| basit | - | kabul edildi" in gunluk
    _is(tmp_path, "kabul-bekliyor")
    assert "Ret kaydedildi: kabul" in onay.isle(tmp_path, OTURUM, "hayır")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "reddedildi"
    assert "reddedildi" in (tmp_path / ".aec/gunluk.md").read_text(encoding="utf-8")


def test_ambiguous_while_waiting_gives_notice(tmp_path):
    _is(tmp_path, "onay-bekliyor:plan")
    assert "onay olarak kaydedilmedi" in onay.isle(tmp_path, OTURUM, "tamam anladım")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "onay-bekliyor:plan"


def test_other_sessions_job_untouched(tmp_path):
    _is(tmp_path, "onay-bekliyor:plan", oturum="oturum-a")
    assert onay.isle(tmp_path, "oturum-b", "evet") is None
    assert is_durumu.aktif_is(tmp_path, "oturum-a")["durum"] == "onay-bekliyor:plan"


@pytest.mark.parametrize("m", ["evet?", "onaylıyorum?", "kabul?", "evet？", "evet؟", "¿evet", "ediyorum"])
def test_question_marks_and_bare_filler_ambiguous(m):
    assert onay.siniflandir(m) == "belirsiz"


@pytest.mark.parametrize("m", ["devam et", "uygula", "uygulayın"])
def test_acceptance_stage_is_narrower(tmp_path, m):
    _is(tmp_path, "kabul-bekliyor")
    assert "onay olarak kaydedilmedi" in onay.isle(tmp_path, OTURUM, m)
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "kabul-bekliyor"


def test_devam_et_still_approves_plan(tmp_path):
    _is(tmp_path, "onay-bekliyor:plan")
    onay.isle(tmp_path, OTURUM, "devam et")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "plan-onaylandi"


def test_kabul_ediyorum_and_iptal_ediyorum(tmp_path):
    assert onay.siniflandir("iptal ediyorum") == "ret" and onay.siniflandir("ret ediyorum") == "ret"
    _is(tmp_path, "kabul-bekliyor")
    onay.isle(tmp_path, OTURUM, "kabul ediyorum")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "kabul-edildi"
    _is(tmp_path, "kabul-bekliyor")
    onay.isle(tmp_path, OTURUM, "iptal ediyorum")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "reddedildi"


def test_journal_failure_does_not_lose_notice(tmp_path, monkeypatch):
    _is(tmp_path, "kabul-bekliyor")
    monkeypatch.setattr(is_durumu, "gunluge_yaz", lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
    assert "Kabulünüz kaydedildi" in onay.isle(tmp_path, OTURUM, "evet")
    assert is_durumu.aktif_is(tmp_path, OTURUM)["durum"] == "kabul-edildi"


@pytest.mark.parametrize("oturum", ["", "!!!"])
def test_empty_sanitized_session_fails_closed(tmp_path, oturum):
    _is(tmp_path, "onay-bekliyor:plan", oturum="bilinmeyen")
    assert onay.isle(tmp_path, oturum, "evet") is None
    assert is_durumu.aktif_is(tmp_path, "bilinmeyen")["durum"] == "onay-bekliyor:plan"


def test_rejection_texts_per_stage(tmp_path):
    _is(tmp_path, "onay-bekliyor:gorevler", karmasik=True)
    assert onay.isle(tmp_path, OTURUM, "hayır") == "[aec] Ret kaydedildi: görevler. Görevler gerekçeyle yeniden hazırlanmalıdır."
    assert "reddedildi (görevler)" in (tmp_path / ".aec/gunluk.md").read_text(encoding="utf-8")
    _is(tmp_path, "onay-bekliyor:tarif", karmasik=True)
    assert onay.isle(tmp_path, OTURUM, "hayır") == "[aec] Ret kaydedildi: tarif. Tarif gerekçeyle yeniden hazırlanmalıdır."
    _is(tmp_path, "kabul-bekliyor")
    assert onay.isle(tmp_path, OTURUM, "hayır") == "[aec] Ret kaydedildi: kabul. İş gerekçeyle yeniden planlanmalıdır."


def test_ambiguous_notice_second_sentence(tmp_path):
    _is(tmp_path, "onay-bekliyor:plan")
    assert "plan değiştiyse yeniden onaya sunulmalıdır." in onay.isle(tmp_path, OTURUM, "tamam anladım")

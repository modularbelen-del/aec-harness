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

"""Stop hook: blocks once when the job is applied but not verified; never while waiting for the person."""
import is_durumu
import stop_kontrol

SID = "s1"


def _is(proje, durum, oturum=SID):
    kayit = is_durumu.yeni_is(proje, "revit-modelleme", "Deneme", False)
    kayit["durum"] = durum
    is_durumu.is_kaydet(proje, kayit)
    is_durumu.aktif_bagla(proje, oturum, kayit["id"])
    return kayit["id"]


def test_stop_blocks_once_then_allows(tmp_path):
    is_id = _is(tmp_path, "uygulandi")
    sonuc = stop_kontrol.karar({"session_id": SID, "stop_hook_active": False}, tmp_path)
    assert sonuc["decision"] == "block" and "aec:dogrulayici" in sonuc["reason"]
    assert stop_kontrol.karar({"session_id": SID, "stop_hook_active": True}, tmp_path) is None
    gunluk = (tmp_path / ".aec" / "gunluk.md").read_text(encoding="utf-8")
    assert "doğrulama yapılmadan durdu" in gunluk and is_id in gunluk


def test_stop_never_blocks_waiting_states(tmp_path):
    for durum in ("onay-bekliyor:plan", "kabul-bekliyor", "gorusme"):
        _is(tmp_path, durum)
        assert stop_kontrol.karar({"session_id": SID, "stop_hook_active": False}, tmp_path) is None
        assert stop_kontrol.karar({"session_id": SID, "stop_hook_active": True}, tmp_path) is None


def test_stop_ignores_other_sessions(tmp_path):
    _is(tmp_path, "uygulandi", oturum="baska")
    assert stop_kontrol.karar({"session_id": SID, "stop_hook_active": False}, tmp_path) is None


def test_stop_bad_input_allows(tmp_path):
    assert stop_kontrol.karar(None, tmp_path) is None
    assert stop_kontrol.karar({}, tmp_path) is None

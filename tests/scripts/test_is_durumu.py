"""is_durumu: job record library and state machine."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import is_durumu

ZAMAN = datetime(2026, 10, 22, 14, 30, tzinfo=timezone.utc)


def _yeni(tmp_path, baslik="Kapı yerleştirme", karmasik=True):
    return is_durumu.yeni_is(tmp_path, "revit-modelleme", baslik, karmasik, simdi=ZAMAN)


def test_new_job_id_and_fields(tmp_path):
    k = _yeni(tmp_path)
    assert k["id"] == "20261022-1430-kapi-yerlestirme"
    assert k["durum"] == "gorusme" and k["karmasik"] is True
    assert k["sema"] == "aec.is/1" and k["olcutler"] == [] and k["sonuc"] is None and k["oturum"] is None
    yol = tmp_path / ".aec" / "isler" / k["id"] / "is.json"
    assert json.loads(yol.read_text(encoding="utf-8"))["id"] == k["id"]
    assert is_durumu.is_yukle(tmp_path, k["id"]) == k
    assert k["olaylar"][0]["yeni"] == "gorusme"


def test_id_collision_gets_suffix(tmp_path):
    a = _yeni(tmp_path)
    b = _yeni(tmp_path)
    assert b["id"] == a["id"] + "-2"
    assert _yeni(tmp_path)["id"] == a["id"] + "-3"


def test_refuses_home_and_drive_root(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    with pytest.raises(ValueError) as e:
        _yeni(tmp_path)
    assert "✗" in str(e.value) and "Hiçbir şey yazılmadı" in str(e.value)
    with pytest.raises(ValueError):
        _yeni(Path(tmp_path.anchor))
    assert not (tmp_path / ".aec").exists()


def test_illegal_transition_raises(tmp_path):
    k = _yeni(tmp_path)
    with pytest.raises(ValueError):
        is_durumu.gecis(k, "uygulandi", "ajan")
    assert k["durum"] == "gorusme"


def test_unknown_source_raises(tmp_path):
    k = _yeni(tmp_path)
    with pytest.raises(ValueError):
        is_durumu.gecis(k, "iptal", "baskasi")


def test_simple_vs_complex_approval_targets():
    basit = {"karmasik": False}
    karma = {"karmasik": True}
    assert is_durumu.onay_sonrasi(basit, "plan") == "plan-onaylandi"
    assert is_durumu.onay_sonrasi(karma, "tarif") == "onaylandi:tarif"
    assert is_durumu.onay_sonrasi(karma, "plan") == "onaylandi:plan"
    assert is_durumu.onay_sonrasi(karma, "gorevler") == "plan-onaylandi"


def test_plan_change_after_approval_resets(tmp_path):
    k = _yeni(tmp_path, karmasik=False)
    is_durumu.gecis(k, "onay-bekliyor:plan", "ajan")
    is_durumu.gecis(k, "onay-bekliyor:plan", "ajan")  # resubmission
    is_durumu.gecis(k, "plan-onaylandi", "kullanici-mesaji")
    is_durumu.gecis(k, "onay-bekliyor:plan", "ajan", "plan değişti")
    assert k["durum"] == "onay-bekliyor:plan"


def test_full_complex_path(tmp_path):
    k = _yeni(tmp_path)
    for yeni in ("onay-bekliyor:tarif", "onaylandi:tarif", "onay-bekliyor:plan", "onaylandi:plan",
                 "onay-bekliyor:gorevler", "plan-onaylandi", "uygulandi", "kabul-bekliyor", "kabul-edildi"):
        is_durumu.gecis(k, yeni, "ajan")
    assert k["durum"] == "kabul-edildi"


def test_events_recorded_with_source(tmp_path):
    k = _yeni(tmp_path)
    is_durumu.gecis(k, "onay-bekliyor:tarif", "ajan", "tarif yazıldı")
    o = k["olaylar"][-1]
    assert o["kaynak"] == "ajan" and o["eski"] == "gorusme" and o["yeni"] == "onay-bekliyor:tarif"
    assert o["not"] == "tarif yazıldı" and o["zaman"]


def test_active_binding_per_session(tmp_path):
    a = _yeni(tmp_path, "Birinci iş")
    b = _yeni(tmp_path, "İkinci iş")
    is_durumu.aktif_bagla(tmp_path, "oturum-1", a["id"])
    is_durumu.aktif_bagla(tmp_path, "oturum/../2", b["id"])
    assert is_durumu.aktif_is(tmp_path, "oturum-1")["id"] == a["id"]
    assert is_durumu.aktif_is(tmp_path, "oturum/../2")["id"] == b["id"]
    assert is_durumu.aktif_is(tmp_path, "yok") is None
    assert not any(".." in p.name for p in (tmp_path / ".aec" / "isler").glob("aktif-*"))


def test_open_jobs_excludes_terminal(tmp_path):
    a = _yeni(tmp_path, "Eski iş")
    b = is_durumu.yeni_is(tmp_path, "dwg-okuma", "Yeni iş", False, simdi=datetime(2026, 10, 23, 9, 0, tzinfo=timezone.utc))
    c = is_durumu.yeni_is(tmp_path, "render", "İptal iş", False, simdi=datetime(2026, 10, 24, 9, 0, tzinfo=timezone.utc))
    is_durumu.gecis(c, "iptal", "ajan")
    is_durumu.is_kaydet(tmp_path, c)
    assert [k["id"] for k in is_durumu.acik_isler(tmp_path)] == [b["id"], a["id"]]


def test_open_jobs_include_rejected(tmp_path):
    # a job rejected at acceptance still has its changes in the model; it stays open until accepted or cancelled
    assert is_durumu.BITMIS == {"kabul-edildi", "iptal"}
    kayitlar = []
    for gun, durum in ((23, "reddedildi"), (24, "kabul-edildi"), (25, "iptal")):
        k = is_durumu.yeni_is(tmp_path, "render", durum, False, simdi=datetime(2026, 10, gun, 9, 0, tzinfo=timezone.utc))
        k["durum"] = durum
        is_durumu.is_kaydet(tmp_path, k)
        kayitlar.append(k)
    assert [k["id"] for k in is_durumu.acik_isler(tmp_path)] == [kayitlar[0]["id"]]


def test_open_jobs_empty_project(tmp_path):
    assert is_durumu.acik_isler(tmp_path) == []


def test_journal_line_appended(tmp_path):
    is_durumu.gunluge_yaz(tmp_path, "birinci")
    is_durumu.gunluge_yaz(tmp_path, "ikinci\n")
    s = (tmp_path / ".aec" / "gunluk.md").read_text(encoding="utf-8")
    assert s == "# İş günlüğü\n\nbirinci\nikinci\n"


def test_table_only_defined_states():
    for eski, hedefler in is_durumu.IZINLI.items():
        assert eski in is_durumu.DURUMLAR
        assert hedefler <= set(is_durumu.DURUMLAR)
    assert set(is_durumu.IZINLI) == set(is_durumu.DURUMLAR)


def test_gecis_refuses_undefined_onaylandi_gorevler(tmp_path):
    k = _yeni(tmp_path)
    for yeni in ("onay-bekliyor:tarif", "onaylandi:tarif", "onay-bekliyor:plan", "onaylandi:plan", "onay-bekliyor:gorevler"):
        is_durumu.gecis(k, yeni, "ajan")
    with pytest.raises(ValueError):
        is_durumu.gecis(k, "onaylandi:gorevler", "ajan")


def test_first_stage_depends_on_complexity(tmp_path):
    basit = _yeni(tmp_path, "Basit", karmasik=False)
    karma = _yeni(tmp_path, "Karma", karmasik=True)
    with pytest.raises(ValueError):
        is_durumu.gecis(basit, "onay-bekliyor:tarif", "ajan")
    with pytest.raises(ValueError):
        is_durumu.gecis(karma, "onay-bekliyor:plan", "ajan")


def test_approved_stage_must_match_waiting_stage(tmp_path):
    k = _yeni(tmp_path)
    is_durumu.gecis(k, "onay-bekliyor:tarif", "ajan")
    with pytest.raises(ValueError):
        is_durumu.gecis(k, "onaylandi:plan", "ajan")


@pytest.mark.parametrize("kotu", ["", "..", "a/b", "a\b", "C:x"])
def test_unsafe_job_ids_refused(tmp_path, kotu):
    with pytest.raises(ValueError):
        is_durumu.is_yukle(tmp_path, kotu)
    with pytest.raises(ValueError):
        is_durumu.is_kaydet(tmp_path, {"id": kotu})


def test_cancel_exits(tmp_path):
    for yol in (["onay-bekliyor:tarif", "onaylandi:tarif"], ["onay-bekliyor:tarif", "onaylandi:tarif", "onay-bekliyor:plan", "onaylandi:plan"],
                ["onay-bekliyor:tarif", "plan-onaylandi", "uygulandi", "kabul-bekliyor"]):
        k = _yeni(tmp_path)
        for y in yol:
            is_durumu.gecis(k, y, "ajan")
        is_durumu.gecis(k, "iptal", "ajan")
        assert k["durum"] == "iptal"


def test_rejected_resubmission_by_complexity(tmp_path):
    karma = _yeni(tmp_path, "Karma")
    for y in ("onay-bekliyor:tarif", "reddedildi", "onay-bekliyor:tarif", "reddedildi", "onay-bekliyor:plan"):
        is_durumu.gecis(karma, y, "ajan")
    basit = _yeni(tmp_path, "Basit", karmasik=False)
    for y in ("onay-bekliyor:plan", "reddedildi"):
        is_durumu.gecis(basit, y, "ajan")
    with pytest.raises(ValueError):
        is_durumu.gecis(basit, "onay-bekliyor:tarif", "ajan")
    is_durumu.gecis(basit, "onay-bekliyor:plan", "ajan")


def test_session_id_capped(tmp_path):
    k = _yeni(tmp_path)
    is_durumu.aktif_bagla(tmp_path, "x" * 200, k["id"])
    assert is_durumu.aktif_is(tmp_path, "x" * 200)["id"] == k["id"]
    assert all(len(p.name) <= len("aktif-.json") + 64 for p in (tmp_path / ".aec" / "isler").glob("aktif-*"))


def test_entering_applied_clears_stale_result(tmp_path):
    k = _yeni(tmp_path, "Basit", karmasik=False)
    for y in ("onay-bekliyor:plan", "plan-onaylandi", "uygulandi"):
        is_durumu.gecis(k, y, "ajan")
    k["sonuc"] = "GEÇTİ"
    for y in ("kabul-bekliyor", "reddedildi", "onay-bekliyor:plan", "plan-onaylandi"):
        is_durumu.gecis(k, y, "ajan")
    assert k["sonuc"] == "GEÇTİ"  # kept until the job is applied again
    is_durumu.gecis(k, "uygulandi", "ajan")
    assert k["sonuc"] is None

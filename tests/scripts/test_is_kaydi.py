"""is_kaydi: CLI the agent uses; it has no approval or acceptance command."""
import re

import is_durumu
import is_kaydi


def _yeni(tmp_path, capsys, *ek):
    assert is_kaydi.main(["yeni", "--proje", str(tmp_path), "--kart", "revit-modelleme", "--baslik", "Kapı yerleştirme", *ek]) == 0
    return re.search(r"^IS: (\S+)$", capsys.readouterr().out, re.M).group(1)


def test_cli_new_prints_id(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys, "--karmasik")
    assert is_id.endswith("-kapi-yerlestirme")
    k = is_durumu.is_yukle(tmp_path, is_id)
    assert k["karmasik"] is True and k["durum"] == "gorusme"


def test_cli_plan_sets_waiting(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    kaynak = tmp_path / "taslak.md"
    kaynak.write_text("# Plan\nKapıları yerleştir.\n", encoding="utf-8")
    assert is_kaydi.main(["plan", "--proje", str(tmp_path), "--is", is_id, "--dosya", str(kaynak)]) == 0
    assert (tmp_path / ".aec" / "isler" / is_id / "plan.md").read_text(encoding="utf-8").startswith("# Plan")
    k = is_durumu.is_yukle(tmp_path, is_id)
    assert k["durum"] == "onay-bekliyor:plan" and k["olaylar"][-1]["kaynak"] == "ajan"


def test_cli_has_no_approval_commands(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    for komut in ("onay", "kabul"):
        assert is_kaydi.main([komut, "--proje", str(tmp_path), "--is", is_id]) == 0
        assert capsys.readouterr().out.strip()
    assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "gorusme"


def test_cli_criteria_only_in_interview(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    ortak = ["--proje", str(tmp_path), "--is", is_id]
    assert is_kaydi.main(["olcut", *ortak, "--olcut", "Kapı sayısı 12", "--yontem", "revit-okuma", "--beklenen", "12"]) == 0
    capsys.readouterr()
    assert len(is_durumu.is_yukle(tmp_path, is_id)["olcutler"]) == 1
    kaynak = tmp_path / "p.md"
    kaynak.write_text("plan", encoding="utf-8")
    is_kaydi.main(["plan", *ortak, "--dosya", str(kaynak)])
    capsys.readouterr()
    assert is_kaydi.main(["olcut", *ortak, "--olcut", "Ek ölçüt", "--yontem", "dosya"]) == 0
    assert "✗" in capsys.readouterr().out
    assert len(is_durumu.is_yukle(tmp_path, is_id)["olcutler"]) == 1


def test_cli_project_add(tmp_path, capsys):
    (tmp_path / ".aec").mkdir()
    (tmp_path / ".aec" / "proje.md").write_text("# Proje bilgileri\n", encoding="utf-8")
    for m in ("birinci not", "ikinci not"):
        assert is_kaydi.main(["proje-ekle", "--proje", str(tmp_path), "--metin", m]) == 0
    s = (tmp_path / ".aec" / "proje.md").read_text(encoding="utf-8")
    assert s.count("## Sonradan eklenenler") == 1
    assert s.split("## Sonradan eklenenler")[1].strip().splitlines() == ["- birinci not", "- ikinci not"]


def test_cli_cancel_and_status(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    assert is_kaydi.main(["durum", "--proje", str(tmp_path), "--is", is_id]) == 0
    assert "gorusme" in capsys.readouterr().out
    assert is_kaydi.main(["iptal", "--proje", str(tmp_path), "--is", is_id, "--gerekce", "vazgeçildi"]) == 0
    assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "iptal"


def test_cli_unknown_job_message(tmp_path, capsys):
    assert is_kaydi.main(["durum", "--proje", str(tmp_path), "--is", "yok"]) == 0
    assert "✗" in capsys.readouterr().out


def test_cli_approval_attempts_rejected_with_message(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    ortak = ["--proje", str(tmp_path), "--is", is_id]
    denemeler = [["onay", *ortak], ["kabul", *ortak], ["plan", *ortak, "--dosya", "x", "--onayla"],
                 ["durum", *ortak, "--durum", "plan-onaylandi"]]
    for d in denemeler:
        assert is_kaydi.main(d) == 0
        out = capsys.readouterr().out
        assert "✗" in out and "onay" in out.lower()
        assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "gorusme"


def test_cli_malformed_job_file_returns_zero_with_message(tmp_path, capsys):
    is_id = _yeni(tmp_path, capsys)
    yol = tmp_path / ".aec" / "isler" / is_id / "is.json"
    for ham in (b"{bozuk", b"\xff\xfe\x00", b"[]"):
        yol.write_bytes(ham)
        assert is_kaydi.main(["durum", "--proje", str(tmp_path), "--is", is_id]) == 0
        out = capsys.readouterr().out
        assert out.startswith("✗") and "Traceback" not in out


def _durumla(proje, capsys, durum):
    is_id = _yeni(proje, capsys)
    kayit = is_durumu.is_yukle(proje, is_id)
    kayit["durum"] = durum
    is_durumu.is_kaydet(proje, kayit)
    return is_id


def test_cli_applied_from_approved_plan(tmp_path, capsys):
    is_id = _durumla(tmp_path, capsys, "plan-onaylandi")
    assert is_kaydi.main(["uygulandi", "--proje", str(tmp_path), "--is", is_id]) == 0
    out = capsys.readouterr().out
    assert "✗" not in out and "uygulandi" in out
    k = is_durumu.is_yukle(tmp_path, is_id)
    assert k["durum"] == "uygulandi" and k["olaylar"][-1]["kaynak"] == "ajan"


def test_cli_applied_is_noop_when_already_applied(tmp_path, capsys):
    is_id = _durumla(tmp_path, capsys, "uygulandi")
    olay_sayisi = len(is_durumu.is_yukle(tmp_path, is_id)["olaylar"])
    assert is_kaydi.main(["uygulandi", "--proje", str(tmp_path), "--is", is_id]) == 0
    out = capsys.readouterr().out
    assert "✗" not in out and "uygulandi" in out
    k = is_durumu.is_yukle(tmp_path, is_id)
    assert k["durum"] == "uygulandi" and len(k["olaylar"]) == olay_sayisi


def test_cli_applied_refused_in_every_other_state(tmp_path, capsys):
    for durum in is_durumu.DURUMLAR:
        if durum in ("plan-onaylandi", "uygulandi"):
            continue
        proje = tmp_path / durum.replace(":", "-")
        is_id = _durumla(proje, capsys, durum)
        assert is_kaydi.main(["uygulandi", "--proje", str(proje), "--is", is_id]) == 0
        out = capsys.readouterr().out
        assert out.startswith("✗") and durum in out, durum
        assert is_durumu.is_yukle(proje, is_id)["durum"] == durum, durum

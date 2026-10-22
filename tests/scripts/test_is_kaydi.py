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

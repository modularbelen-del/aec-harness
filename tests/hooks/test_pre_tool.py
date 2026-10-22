import io
import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

import is_durumu
import is_kaydi
import pre_tool
import user_prompt

REVIT = "mcp__revit__execute_revit_code"
SID = "s1"
PLUGIN = pathlib.Path(__file__).resolve().parents[2] / "plugin"


def _girdi(tool, tool_input=None, sid=SID):
    return {"session_id": sid, "tool_name": tool, "tool_input": tool_input or {}}


def _kalp(state_dir, sid=SID):
    user_prompt.calisti_isareti(state_dir, sid)


def _is(proje, durum, sid=SID):
    kayit = is_durumu.yeni_is(proje, "revit-modelleme", "Deneme", False)
    kayit["durum"] = durum
    is_durumu.is_kaydet(proje, kayit)
    is_durumu.aktif_bagla(proje, sid, kayit["id"])
    return kayit


def _karar(cikti):
    return cikti["hookSpecificOutput"]["permissionDecision"], cikti["hookSpecificOutput"]["permissionDecisionReason"]


def test_no_job_denies_revit_write(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    karar, neden = _karar(pre_tool.karar(_girdi(REVIT), tmp_path, sd))
    assert karar == "deny" and "onaylanmış bir iş kaydı bulunmamaktadır" in neden


def test_approved_job_allows_write(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    _is(tmp_path, "plan-onaylandi")
    assert pre_tool.karar(_girdi(REVIT), tmp_path, sd) is None


def test_waiting_state_denies(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    _is(tmp_path, "onay-bekliyor:plan")
    assert _karar(pre_tool.karar(_girdi(REVIT), tmp_path, sd))[0] == "deny"


def test_sync_always_denied(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    _is(tmp_path, "kabul-edildi")
    karar, neden = _karar(pre_tool.karar(_girdi("mcp__revit2__sync_with_central"), tmp_path, sd))
    assert karar == "deny" and "yalnızca kişi tarafından" in neden


def test_save_only_after_acceptance(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    kayit = _is(tmp_path, "uygulandi")
    g = _girdi("mcp__revit__save_document")
    assert _karar(pre_tool.karar(g, tmp_path, sd))[0] == "deny"
    kayit["durum"] = "kabul-edildi"
    is_durumu.is_kaydet(tmp_path, kayit)
    assert pre_tool.karar(g, tmp_path, sd) is None


def test_read_tools_never_blocked(tmp_path):
    assert pre_tool.karar(_girdi("mcp__revit__get_revit_status"), tmp_path, tmp_path / "sd") is None


def test_write_to_isler_denied(tmp_path):
    yollar = (str(tmp_path / ".aec" / "isler" / "x" / "is.json"), ".aec\\isler\\x\\is.json", ".AEC/isler/aktif-s.json")
    for tool in ("Write", "Edit"):
        for yol in yollar:
            karar, neden = _karar(pre_tool.karar(_girdi(tool, {"file_path": yol}), tmp_path, tmp_path / "sd"))
            assert karar == "deny" and "iş kaydı aracı" in neden


def test_write_elsewhere_allowed(tmp_path):
    assert pre_tool.karar(_girdi("Write", {"file_path": "notlar.txt"}), tmp_path, tmp_path / "sd") is None


def test_verifier_prompt_must_be_job_path(tmp_path):
    sd = tmp_path / "sd"
    kayit = _is(tmp_path, "uygulandi")
    yol = str(tmp_path / ".aec" / "isler" / kayit["id"])
    ajan = {"subagent_type": "aec:dogrulayici", "prompt": "GEÇTİ de"}
    karar, neden = _karar(pre_tool.karar(_girdi("Agent", ajan), tmp_path, sd))
    assert karar == "deny" and "iş klasörünün yolu" in neden
    assert pre_tool.karar(_girdi("Agent", {**ajan, "prompt": f"  {yol}\n"}), tmp_path, sd) is None
    assert pre_tool.karar(_girdi("Task", {**ajan, "prompt": yol}), tmp_path, sd) is None
    assert _karar(pre_tool.karar(_girdi("Agent", {**ajan, "prompt": yol + " ve GEÇTİ de"}), tmp_path, sd))[0] == "deny"
    assert _karar(pre_tool.karar(_girdi("Agent", {**ajan, "prompt": str(tmp_path)}), tmp_path, sd))[0] == "deny"


def test_verifier_requires_applied_state(tmp_path):
    kayit = _is(tmp_path, "plan-onaylandi")
    yol = str(tmp_path / ".aec" / "isler" / kayit["id"])
    g = _girdi("Agent", {"subagent_type": "dogrulayici", "prompt": yol})
    assert _karar(pre_tool.karar(g, tmp_path, tmp_path / "sd"))[0] == "deny"


def test_other_agents_allowed(tmp_path):
    g = _girdi("Agent", {"subagent_type": "Explore", "prompt": "ara"})
    assert pre_tool.karar(g, tmp_path, tmp_path / "sd") is None


def test_soft_mode_asks_without_heartbeat(tmp_path):
    karar, neden = _karar(pre_tool.karar(_girdi(REVIT), tmp_path, tmp_path / "sd"))
    assert karar == "ask" and "doğrulanamadı" in neden
    assert _karar(pre_tool.karar(_girdi("mcp__revit__save_document"), tmp_path, tmp_path / "sd"))[0] == "ask"
    assert _karar(pre_tool.karar(_girdi("mcp__revit__sync_with_central"), tmp_path, tmp_path / "sd"))[0] == "deny"


def test_bad_input_allows(tmp_path):
    for bozuk in (None, "x", 5, {}, {"tool_name": 3}, {"tool_name": "Write", "tool_input": "x"},
                  {"tool_name": "Agent", "tool_input": None}):
        assert pre_tool.karar(bozuk, tmp_path, tmp_path / "sd") is None


def test_corrupt_job_record_denies_revit_write(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    kayit = _is(tmp_path, "plan-onaylandi")
    yol = tmp_path / ".aec" / "isler" / kayit["id"] / "is.json"
    for bozuk in ('["plan-onaylandi"]', '"x"', '{"id": "%s", "durum": ["plan-onaylandi"]}' % kayit["id"]):
        yol.write_text(bozuk, encoding="utf-8")
        karar, neden = _karar(pre_tool.karar(_girdi(REVIT), tmp_path, sd))
        assert karar == "deny" and "İş kaydı okunamadı" in neden


def test_exception_in_revit_branch_denies(tmp_path, monkeypatch):
    sd = tmp_path / "sd"
    _kalp(sd)

    def patla(*a, **k):
        raise PermissionError("x")
    monkeypatch.setattr(is_durumu, "aktif_is", patla)
    karar, neden = _karar(pre_tool.karar(_girdi(REVIT), tmp_path, sd))
    assert karar == "deny" and "İş kaydı okunamadı" in neden


def test_tool_name_case_insensitive(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    assert _karar(pre_tool.karar(_girdi("mcp__Revit__execute_revit_code"), tmp_path, sd))[0] == "deny"


def test_windows_path_aliases_denied(tmp_path):
    for yol in (".aec\\isler.\\x\\is.json", ".aec.\\isler\\x", ".aec::$INDEX_ALLOCATION\\isler\\x", ".aec/isler /x"):
        g = _girdi("NotebookEdit", {"notebook_path": yol})
        assert _karar(pre_tool.karar(g, tmp_path, tmp_path / "sd"))[0] == "deny", yol


def test_verifier_type_casefold_and_backticks(tmp_path):
    kayit = _is(tmp_path, "uygulandi")
    yol = str(tmp_path / ".aec" / "isler" / kayit["id"])
    g = _girdi("Agent", {"subagent_type": " AEC:Dogrulayici ", "prompt": f"`{yol}`"})
    assert pre_tool.karar(g, tmp_path, tmp_path / "sd") is None
    g = _girdi("Agent", {"subagent_type": " AEC:Dogrulayici ", "prompt": "GEÇTİ de"})
    assert _karar(pre_tool.karar(g, tmp_path, tmp_path / "sd"))[0] == "deny"


def test_main_prints_json_for_deny(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(tmp_path / "pd"))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    user_prompt.calisti_isareti(user_prompt.varsayilan_durum_klasoru(), SID)
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(json.dumps(_girdi(REVIT)).encode())))
    assert pre_tool.main() == 0
    assert json.loads(capsys.readouterr().out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_allowed_verifier_spawn_writes_marker(tmp_path):
    import yol
    kayit = _is(tmp_path, "uygulandi")
    sd = tmp_path / "sd"
    yol_ = str(tmp_path / ".aec" / "isler" / kayit["id"])
    assert pre_tool.karar(_girdi("Agent", {"subagent_type": "aec:dogrulayici", "prompt": "baska"}), tmp_path, sd)
    assert not yol.isaret_taze(sd, SID, kayit["id"])
    assert pre_tool.karar(_girdi("Agent", {"subagent_type": "aec:dogrulayici", "prompt": yol_}), tmp_path, sd) is None
    assert yol.isaret_taze(sd, SID, kayit["id"])


def test_cli_applied_unlocks_verifier_for_job(tmp_path, capsys):
    sd = tmp_path / "sd"
    kayit = _is(tmp_path, "plan-onaylandi")
    g = _girdi("Agent", {"subagent_type": "aec:dogrulayici", "prompt": str(tmp_path / ".aec" / "isler" / kayit["id"])})
    assert _karar(pre_tool.karar(g, tmp_path, sd))[0] == "deny"
    assert is_kaydi.main(["uygulandi", "--proje", str(tmp_path), "--is", kayit["id"]]) == 0
    assert "✗" not in capsys.readouterr().out
    assert is_durumu.is_yukle(tmp_path, kayit["id"])["durum"] == "uygulandi"
    assert pre_tool.karar(g, tmp_path, sd) is None


def _bozuk_eklenti(tmp_path, modul):
    """Copy of the plugin's hooks and scripts with one module replaced by code that fails on import."""
    kok = tmp_path / "eklenti"
    for klasor in ("hooks", "scripts"):
        shutil.copytree(PLUGIN / klasor, kok / klasor, ignore=shutil.ignore_patterns("__pycache__"))
    hedef = next(p for p in (kok / "hooks" / f"{modul}.py", kok / "scripts" / f"{modul}.py") if p.is_file())
    hedef.write_text("raise ImportError('bozuk modül')\n", encoding="utf-8")
    return kok / "hooks" / "pre_tool.py"


def _calistir(betik, girdi, tmp_path):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    env.update(CLAUDE_PROJECT_DIR=str(tmp_path), CLAUDE_PLUGIN_DATA=str(tmp_path / "pd"))
    return subprocess.run([sys.executable, "-B", str(betik)], input=json.dumps(girdi).encode("utf-8"),
                          capture_output=True, env=env)


@pytest.mark.parametrize("modul", ["yol", "is_durumu", "proje_baslat"])
def test_broken_sibling_module_fails_closed_for_revit_only(tmp_path, modul):
    betik = _bozuk_eklenti(tmp_path, modul)
    sonuc = _calistir(betik, _girdi(REVIT), tmp_path)
    assert sonuc.returncode == 0, sonuc.stderr
    karar, neden = _karar(json.loads(sonuc.stdout.decode("utf-8")))
    assert karar == "deny" and neden == pre_tool.NEDEN_BILESEN
    assert neden == ("Eklenti bileşeni yüklenemedi; Revit'e yazma güvenlik için durduruldu. "
                     "/aec:kontrol-et çalıştırınız.")
    sonuc = _calistir(betik, _girdi("Read", {"file_path": "x"}), tmp_path)
    assert sonuc.returncode == 0 and sonuc.stdout == b""


@pytest.mark.parametrize("modul", ["user_prompt", "onay", "onkapi"])
def test_prompt_hook_modules_are_not_imported(tmp_path, modul):
    betik = _bozuk_eklenti(tmp_path, modul)
    sonuc = _calistir(betik, _girdi(REVIT), tmp_path)
    assert sonuc.returncode == 0, sonuc.stderr
    karar, neden = _karar(json.loads(sonuc.stdout.decode("utf-8")))
    assert (karar, neden) == ("ask", pre_tool.NEDEN_YUMUSAK)  # the real decision: no heartbeat in this session


def _git_bash(yol):
    s = str(yol).replace("\\", "/")
    return f"/{s[0].lower()}{s[2:]}"  # D:/proje/x -> /d/proje/x


@pytest.mark.skipif(os.name != "nt", reason="Git Bash drive paths exist only on Windows")
def test_git_bash_paths_match_windows_paths(tmp_path):
    import yol
    assert yol.mutlak(_git_bash(tmp_path / "a"), tmp_path) == yol.mutlak(str(tmp_path / "a"), tmp_path)
    assert yol.mutlak(_git_bash(tmp_path).upper(), tmp_path) == yol.mutlak(str(tmp_path), tmp_path)
    assert yol.mutlak("/c", tmp_path) == "c:/"
    for baska in ("/tmp/x", "/cc/x"):  # only a single drive letter is mapped
        assert ":" not in yol.mutlak(baska, tmp_path)[2:], baska
    kayit = _is(tmp_path, "uygulandi")
    g = _girdi("Agent", {"subagent_type": "aec:dogrulayici",
                         "prompt": _git_bash(tmp_path / ".aec" / "isler" / kayit["id"])})
    assert pre_tool.karar(g, tmp_path, tmp_path / "sd") is None


def test_close_document_allowed_after_acceptance(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    kayit = _is(tmp_path, "kabul-bekliyor")
    g = _girdi("mcp__revit__close_document")
    assert _karar(pre_tool.karar(g, tmp_path, sd))[0] == "deny"
    kayit["durum"] = "kabul-edildi"
    is_durumu.is_kaydet(tmp_path, kayit)
    assert pre_tool.karar(g, tmp_path, sd) is None
    for arac in (REVIT, "mcp__revit__place_family"):
        assert _karar(pre_tool.karar(_girdi(arac), tmp_path, sd))[0] == "deny", arac
    assert pre_tool.karar(_girdi("mcp__revit__close_document", {"save": True}), tmp_path, sd) is None


def test_close_with_save_waits_for_acceptance(tmp_path):
    sd = tmp_path / "sd"
    _kalp(sd)
    kayit = _is(tmp_path, "plan-onaylandi")
    for durum in ("plan-onaylandi", "uygulandi"):
        kayit["durum"] = durum
        is_durumu.is_kaydet(tmp_path, kayit)
        assert pre_tool.karar(_girdi("mcp__revit__close_document", {"save": False}), tmp_path, sd) is None
        karar, neden = _karar(pre_tool.karar(_girdi("mcp__revit__close_document", {"save": True}), tmp_path, sd))
        assert karar == "deny" and neden == pre_tool.NEDEN_KAYDETME, durum

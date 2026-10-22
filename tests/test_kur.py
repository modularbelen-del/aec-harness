import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
POWERSHELL = shutil.which("powershell")
needs_ps = pytest.mark.skipif(POWERSHELL is None, reason="powershell yok")


def _ps(*args):
    out = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
        capture_output=True, timeout=120,
    )
    out.stdout = out.stdout.decode("utf-8", errors="replace")
    out.stderr = out.stderr.decode("utf-8", errors="replace")
    return out


def test_kur_ps1_has_bom():
    assert (ROOT / "kur.ps1").read_bytes().startswith(b"\xef\xbb\xbf")


@needs_ps
def test_kur_ps1_parses():
    script = (
        "$errs=$null; [void][System.Management.Automation.Language.Parser]"
        f"::ParseFile('{ROOT / 'kur.ps1'}',[ref]$null,[ref]$errs); $errs.Count"
    )
    out = _ps("-Command", script)
    assert out.stdout.strip() == "0", out.stdout + out.stderr


@needs_ps
def test_dry_run_stable_and_dev():
    out = _ps("-File", str(ROOT / "kur.ps1"), "-KuruCalistir")
    assert out.returncode == 0, out.stderr
    assert "modularbelen-del/aec-harness" in out.stdout and "#dev" not in out.stdout
    for n in range(1, 6):
        assert f"[{n}/5]" in out.stdout
    out = _ps("-File", str(ROOT / "kur.ps1"), "-KuruCalistir", "-Kanal", "dev")
    assert out.returncode == 0, out.stderr
    assert "modularbelen-del/aec-harness#dev" in out.stdout


def test_kur_cmd_calls_ps1():
    text = (ROOT / "kur.cmd").read_text(encoding="utf-8")
    assert '-ExecutionPolicy Bypass -File "%~dp0kur.ps1"' in text


def test_kur_ps1_header_has_bom_stripping_one_liner():
    text = (ROOT / "kur.ps1").read_text(encoding="utf-8-sig")
    assert "TrimStart([char]0xFEFF)" in text
    assert "AEC_KANAL" in text


@needs_ps
def test_iex_path_with_bom_char_kept():
    # GetString keeps the U+FEFF, so TrimStart is what removes it (as irm | iex does).
    script = (
        "$env:AEC_KURU='1'; "
        f"$b=[IO.File]::ReadAllBytes('{ROOT / 'kur.ps1'}'); "
        "$s=[Text.UTF8Encoding]::new($false).GetString($b); "
        "if ($s[0] -ne [char]0xFEFF) { Write-Output 'BOM-YOK'; exit 3 }; "
        "iex ($s.TrimStart([char]0xFEFF))"
    )
    out = _ps("-Command", script)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "modularbelen-del/aec-harness" in out.stdout
    assert out.stderr.strip() == ""


def _ayar(yol, kanal="stable", ok=1):
    env = dict(os.environ, AEC_SADECE_YUKLE="1")
    script = f". '{ROOT / 'kur.ps1'}'; Set-AecOtomatikGuncelleme -Yol '{yol}' -Kanal '{kanal}'"
    out = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True, timeout=120, env=env,
    )
    assert out.returncode == 0, out.stderr.decode("utf-8", "replace")
    return out.stdout.decode("utf-8", "replace")


def _entry(yol):
    raw = Path(yol).read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8"))


@needs_ps
def test_ayar_missing_file_created(tmp_path):
    p = tmp_path / "s" / "settings.json"
    _ayar(p)
    d = _entry(p)
    assert d["extraKnownMarketplaces"]["aec-office"] == {
        "source": {"source": "github", "repo": "modularbelen-del/aec-harness"},
        "autoUpdate": True,
    }


@needs_ps
def test_ayar_empty_file(tmp_path):
    p = tmp_path / "settings.json"
    p.write_bytes(b"")
    _ayar(p)
    assert _entry(p)["extraKnownMarketplaces"]["aec-office"]["autoUpdate"] is True


@needs_ps
def test_ayar_preserves_other_keys(tmp_path):
    p = tmp_path / "settings.json"
    orig = {
        "model": "x", "list": [1, 2, 3], "one": ["a"], "empty": [],
        "nested": {"a": {"b": [{"c": 1}]}},
        "extraKnownMarketplaces": {"other": {"source": {"source": "github", "repo": "a/b"}}},
    }
    p.write_text(json.dumps(orig), encoding="utf-8")
    _ayar(p)
    d = _entry(p)
    for k, v in orig.items():
        if k != "extraKnownMarketplaces":
            assert d[k] == v
    assert d["extraKnownMarketplaces"]["other"] == orig["extraKnownMarketplaces"]["other"]
    assert d["extraKnownMarketplaces"]["aec-office"]["autoUpdate"] is True


@needs_ps
def test_ayar_unparsable_untouched(tmp_path):
    p = tmp_path / "settings.json"
    p.write_bytes(b'{ "a": 1, ')
    out = _ayar(p)
    assert p.read_bytes() == b'{ "a": 1, '
    assert "dokunulmadı" in out
    assert not (tmp_path / "settings.json.aec-yedek").exists()


@needs_ps
def test_ayar_idempotent(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text('{"model": "x"}', encoding="utf-8")
    _ayar(p)
    first = p.read_bytes()
    _ayar(p)
    assert p.read_bytes() == first


@needs_ps
def test_ayar_dev_channel_ref(tmp_path):
    p = tmp_path / "settings.json"
    _ayar(p, "dev")
    src = _entry(p)["extraKnownMarketplaces"]["aec-office"]["source"]
    assert src == {"source": "github", "repo": "modularbelen-del/aec-harness", "ref": "dev"}


@needs_ps
def test_ayar_existing_source_kept_and_channel_switch(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"extraKnownMarketplaces": {"aec-office": {
        "source": {"source": "github", "repo": "modularbelen-del/aec-harness"}}}}), encoding="utf-8")
    _ayar(p)
    e = _entry(p)["extraKnownMarketplaces"]["aec-office"]
    assert e["source"] == {"source": "github", "repo": "modularbelen-del/aec-harness"}
    assert e["autoUpdate"] is True
    _ayar(p, "dev")
    assert _entry(p)["extraKnownMarketplaces"]["aec-office"]["source"]["ref"] == "dev"


@needs_ps
def test_ayar_backup_once_not_overwritten(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text('{"model": "orijinal"}', encoding="utf-8")
    _ayar(p)
    yedek = tmp_path / "settings.json.aec-yedek"
    assert json.loads(yedek.read_text(encoding="utf-8")) == {"model": "orijinal"}
    _ayar(p)
    _ayar(p, "dev")
    assert json.loads(yedek.read_text(encoding="utf-8")) == {"model": "orijinal"}


@needs_ps
def test_dry_run_exit_zero_without_exit_statement():
    assert "\nexit " not in (ROOT / "kur.ps1").read_text(encoding="utf-8-sig")
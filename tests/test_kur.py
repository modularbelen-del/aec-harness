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

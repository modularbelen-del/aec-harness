"""PostToolUse hook: binds a newly created or continued job to the session and marks 'uygulandi' after a successful
Revit write.

A continued job ('is_kaydi.py devam') that was approved in another session goes back to 'onay-bekliyor:plan': the person
confirms it again here. The job moves to this session; other sessions' bindings to it are removed. Binding grants
nothing else. Standard library only. Never raises and prints nothing; it decides
no permission, so a failed import only means no binding (the locks then stay closed).
"""
import json
import os
import pathlib
import re
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import is_durumu  # noqa: E402

KAYNAK = "hook-post"
ISARET = re.compile(r"^IS:\s*(\S+)\s*$", re.MULTILINE)
YENI_KOMUT = re.compile(r"\bis_kaydi\.py\b.*\syeni(\s|$)", re.DOTALL)
DEVAM_ISARET = re.compile(r"^DEVAM:\s*(\S+)\s*$", re.MULTILINE)
DEVAM_KOMUT = re.compile(r"\bis_kaydi\.py\b.*\sdevam(\s|$)", re.DOTALL)
DEVAM_NOTU = "oturum değişti; onay yeniden istenecek"
NL = chr(10)
UYGULAMA_ARACLARI = re.compile(r"^mcp__.*revit.*__(execute_revit_code|place_family)$", re.IGNORECASE)


def _metin(yanit) -> str:
    """All text found in a tool response (string, dict with text fields or content blocks, list of blocks)."""
    if isinstance(yanit, str):
        return yanit
    if isinstance(yanit, dict):
        return NL.join(_metin(yanit[k]) for k in ("stdout", "output", "content", "text") if yanit.get(k))
    if isinstance(yanit, list):
        return NL.join(_metin(b) for b in yanit)
    return ""


def _hatali(yanit) -> bool:
    """Explicit error flags, or the plain-text error forms the Revit MCP server returns."""
    if isinstance(yanit, dict) and (yanit.get("isError") or yanit.get("is_error") or yanit.get("error")):
        return True
    metin = _metin(yanit)
    return metin.strip().startswith(("Error", "=== ERROR DETAILS ===")) or "Error during code execution" in metin


def _bagla(girdi: dict, proje: pathlib.Path, oturum: str) -> None:
    komut = (girdi.get("tool_input") or {}).get("command")
    if not isinstance(komut, str) or not YENI_KOMUT.search(komut):
        return
    for is_id in ISARET.findall(_metin(girdi.get("tool_response"))):
        try:
            kayit = is_durumu.is_yukle(proje, is_id)
        except (ValueError, OSError):
            continue
        # only what a fresh 'yeni' produces: still in 'gorusme' and not bound to any session yet
        if isinstance(kayit, dict) and kayit.get("durum") == "gorusme" and not kayit.get("oturum"):
            is_durumu.aktif_bagla(proje, oturum, is_id)
            return


def _devam(girdi: dict, proje: pathlib.Path, oturum: str) -> None:
    """Binds a job continued with 'is_kaydi.py devam'; a plan approved in another session must be confirmed again."""
    komut = (girdi.get("tool_input") or {}).get("command")
    if not isinstance(komut, str) or not DEVAM_KOMUT.search(komut):
        return
    for is_id in DEVAM_ISARET.findall(_metin(girdi.get("tool_response"))):
        try:
            kayit = is_durumu.is_yukle(proje, is_id)
        except (ValueError, OSError):
            continue
        if not isinstance(kayit, dict) or kayit.get("id") != is_id:
            continue
        durum = kayit.get("durum")
        if durum not in is_durumu.IZINLI or durum in is_durumu.BITMIS:
            continue
        mevcut = is_durumu.aktif_is(proje, oturum)
        if isinstance(mevcut, dict) and mevcut.get("id") == is_id:
            return  # already this session's job: its approvals were given here
        if durum == "plan-onaylandi":  # regress before binding: a failed save leaves the job unbound
            is_durumu.gecis(kayit, "onay-bekliyor:plan", KAYNAK, DEVAM_NOTU)
            is_durumu.is_kaydet(proje, kayit)
        is_durumu.aktif_bagla(proje, oturum, is_id)
        is_durumu.diger_baglari_kaldir(proje, oturum, is_id)  # a decision in the old session no longer counts here
        return


def _uygulandi(girdi: dict, proje: pathlib.Path, oturum: str) -> None:
    if _hatali(girdi.get("tool_response")):
        return
    kayit = is_durumu.aktif_is(proje, oturum)
    if not kayit or kayit.get("durum") != "plan-onaylandi":
        return
    is_durumu.gecis(kayit, "uygulandi", KAYNAK, "Revit'e yazma başarıyla tamamlandı")
    is_durumu.is_kaydet(proje, kayit)


def isle(girdi, proje: pathlib.Path) -> None:
    try:
        if not isinstance(girdi, dict) or not isinstance(girdi.get("tool_name"), str):
            return
        arac = girdi["tool_name"]
        oturum = str(girdi.get("session_id") or "")
        proje = pathlib.Path(proje)
        if arac in ("Bash", "PowerShell"):
            _bagla(girdi, proje, oturum)
            _devam(girdi, proje, oturum)
        elif UYGULAMA_ARACLARI.match(arac):
            _uygulandi(girdi, proje, oturum)
    except Exception:
        pass


def main() -> int:
    try:
        metin = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8", "replace")
        girdi = json.loads(metin)
        proje = os.environ.get("CLAUDE_PROJECT_DIR") or (girdi.get("cwd") if isinstance(girdi, dict) else None) or os.getcwd()
        isle(girdi, pathlib.Path(proje))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

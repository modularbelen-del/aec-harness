"""PostToolUse hook: binds a newly created job to the session and marks 'uygulandi' after a successful Revit write.

Standard library only. Never raises and prints nothing.
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
UYGULAMA_ARACLARI = re.compile(r"^mcp__.*revit.*__(execute_revit_code|place_family)$")


def _metin(yanit) -> str:
    if isinstance(yanit, str):
        return yanit
    if isinstance(yanit, dict):
        return "\n".join(str(yanit[k]) for k in ("stdout", "output", "content", "text") if yanit.get(k))
    if isinstance(yanit, list):
        return "\n".join(str(b.get("text", "")) if isinstance(b, dict) else str(b) for b in yanit)
    return ""


def _hatali(yanit) -> bool:
    if isinstance(yanit, dict):
        return bool(yanit.get("isError") or yanit.get("is_error") or yanit.get("error"))
    return False


def _bagla(girdi: dict, proje: pathlib.Path, oturum: str) -> None:
    komut = (girdi.get("tool_input") or {}).get("command")
    if not isinstance(komut, str) or not YENI_KOMUT.search(komut):
        return
    eslesme = ISARET.search(_metin(girdi.get("tool_response")))
    if not eslesme:
        return
    is_id = eslesme.group(1)
    is_durumu.is_yukle(proje, is_id)  # raises when the job does not exist
    is_durumu.aktif_bagla(proje, oturum, is_id)


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
        if arac == "Bash":
            _bagla(girdi, proje, oturum)
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

"""Stop hook: blocks once when this session's job is 'uygulandi' (applied, not verified).

It never blocks while the job waits for the person, nor in any other state, nor while a verifier started for the job
is still running (marker written by the PreToolUse hook). On the second stop (stop_hook_active) it lets the session
end and leaves one journal note per job. Standard library only; on any error it allows the stop silently.
"""
import json
import os
import pathlib
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))

import is_durumu  # noqa: E402
import yol  # noqa: E402

NEDEN = ("Uygulama doğrulanmadı. İş klasörünün yolu ile aec:dogrulayici ajanı çalıştırılmalı, "
         "ardından rapor kişiye sunulmalıdır.")
OLAY = "doğrulama yapılmadan durdu"


def _daha_once_yazildi(proje: pathlib.Path, is_id: str) -> bool:
    try:
        metin = (pathlib.Path(proje) / is_durumu.GUNLUK).read_text(encoding="utf-8")
    except OSError:
        return False
    return any(f"| {is_id} |" in satir and satir.endswith(OLAY) for satir in metin.splitlines())


def karar(girdi, proje: pathlib.Path, state_dir: "pathlib.Path | None" = None):
    """Returns {"decision": "block", "reason": ...} or None (allow)."""
    try:
        if not isinstance(girdi, dict):
            return None
        oturum = str(girdi.get("session_id") or "")
        if not yol.oturum_temiz(oturum):
            return None
        proje = pathlib.Path(proje)
        kayit = is_durumu.aktif_is(proje, oturum)
        if not isinstance(kayit, dict) or kayit.get("durum") != "uygulandi":
            return None
        if yol.isaret_taze(state_dir or yol.durum_klasoru(), oturum, kayit.get("id")):
            return None  # a verifier is still running in the background
        if not girdi.get("stop_hook_active"):
            return {"decision": "block", "reason": NEDEN}
        if not _daha_once_yazildi(proje, str(kayit.get("id"))):
            is_durumu.gunluge_yaz(proje, yol.gunluk_satiri(kayit, OLAY))
        return None
    except Exception:
        return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        metin = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8", "replace")
        girdi = json.loads(metin)
        proje = os.environ.get("CLAUDE_PROJECT_DIR") or (girdi.get("cwd") if isinstance(girdi, dict) else None) or os.getcwd()
        sonuc = karar(girdi, pathlib.Path(proje))
        if sonuc:
            sys.stdout.write(json.dumps(sonuc, ensure_ascii=False))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

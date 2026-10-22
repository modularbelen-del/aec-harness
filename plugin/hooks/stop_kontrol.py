"""Stop hook: blocks once when this session's job is 'uygulandi' (applied, not verified).

It never blocks while the job waits for the person, nor in any other state. On the second stop (stop_hook_active) it
lets the session end and leaves a journal note. Standard library only; on any error it allows the stop silently.
"""
import json
import os
import pathlib
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import is_durumu  # noqa: E402

KAYNAK = "hook-stop"
NEDEN = ("Uygulama doğrulanmadı. İş klasörünün yolu ile aec:dogrulayici ajanı çalıştırılmalı, "
         "ardından rapor kişiye sunulmalıdır.")


def karar(girdi, proje: pathlib.Path):
    """Returns {"decision": "block", "reason": ...} or None (allow)."""
    try:
        if not isinstance(girdi, dict):
            return None
        kayit = is_durumu.aktif_is(pathlib.Path(proje), str(girdi.get("session_id") or ""))
        if not isinstance(kayit, dict) or kayit.get("durum") != "uygulandi":
            return None
        if not girdi.get("stop_hook_active"):
            return {"decision": "block", "reason": NEDEN}
        is_durumu.gunluge_yaz(pathlib.Path(proje), f"- {is_durumu._zaman()} | {kayit.get('id')} | doğrulama yapılmadan durdu")
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

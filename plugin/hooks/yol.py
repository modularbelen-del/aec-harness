"""Small helpers shared by the hooks: path normalization, hook state directory, verifier markers, journal line."""
import os
import pathlib
import re
import tempfile
import time
from datetime import datetime

MAKS_ISARET_SANIYE = 30 * 60
_GECERSIZ = re.compile(r"[^A-Za-z0-9_-]")


def mutlak(yol: str, proje: pathlib.Path) -> str:
    """Normalized absolute path with forward slashes, lower-cased on Windows."""
    p = pathlib.Path(yol.replace("\\", "/"))
    if not p.is_absolute():
        p = pathlib.Path(proje) / p
    s = os.path.normpath(str(p)).replace("\\", "/")
    return s.lower() if os.name == "nt" else s


def durum_klasoru() -> pathlib.Path:
    """Per-user hook state directory (heartbeat and verifier markers)."""
    return pathlib.Path(os.environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()) / "aec-onkapi"


def oturum_temiz(oturum: str) -> str:
    """Session id reduced to file-name-safe characters; empty when nothing usable is left."""
    return _GECERSIZ.sub("", str(oturum or ""))[:64]


def calisti_yolu(state_dir: pathlib.Path, oturum: str) -> pathlib.Path:
    """Per-session heartbeat file: UserPromptSubmit writes it, the PreToolUse Revit lock reads it."""
    return pathlib.Path(state_dir) / f"calisti-{oturum_temiz(oturum) or 'bilinmeyen'}"


def _isaret_yolu(state_dir: pathlib.Path, oturum: str, is_id: str) -> "pathlib.Path | None":
    sid, kimlik = oturum_temiz(oturum), _GECERSIZ.sub("", str(is_id or ""))
    return pathlib.Path(state_dir) / f"dogrulama-{sid}-{kimlik}" if sid and kimlik else None


def isaret_yaz(state_dir: pathlib.Path, oturum: str, is_id: str) -> None:
    """Marks that a verifier was started for this session's job (the Stop lock then waits for it); never raises."""
    try:
        yol = _isaret_yolu(state_dir, oturum, is_id)
        if yol:
            yol.parent.mkdir(parents=True, exist_ok=True)
            yol.write_text(str(time.time()), encoding="utf-8")
    except Exception:
        pass


def isaret_taze(state_dir: pathlib.Path, oturum: str, is_id: str) -> bool:
    try:
        yol = _isaret_yolu(state_dir, oturum, is_id)
        return bool(yol) and yol.is_file() and time.time() - yol.stat().st_mtime < MAKS_ISARET_SANIYE
    except Exception:
        return False


def isaret_sil(state_dir: pathlib.Path, oturum: str, is_id: str) -> None:
    try:
        yol = _isaret_yolu(state_dir, oturum, is_id)
        if yol:
            yol.unlink(missing_ok=True)
    except Exception:
        pass


def gunluk_satiri(kayit: dict, olay: str) -> str:
    """Journal line: time | id | card | complexity | result | event."""
    return "- {} | {} | {} | {} | {} | {}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M"), kayit.get("id"), kayit.get("kart"),
        "karmaşık" if kayit.get("karmasik") else "basit", kayit.get("sonuc") or "-", olay)

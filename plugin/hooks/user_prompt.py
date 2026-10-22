"""UserPromptSubmit hook: marks that hooks ran, records the person's approval/rejection/acceptance from their own
message (onay.py) and otherwise adds a short routing card for the matching job, once per session.

Standard library only. On any error or no match it prints nothing.
"""
import json
import os
import pathlib
import re
import sys
import tempfile

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import onay  # noqa: E402
import onkapi  # noqa: E402

MAX_CONTEXT_BYTES = 1024
SHORT_REPLY_WORDS = 3
CARD_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills/istek-karsilama/kartlar"


def varsayilan_durum_klasoru() -> pathlib.Path:
    return pathlib.Path(os.environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()) / "aec-onkapi"


def calisti_yolu(state_dir: pathlib.Path, oturum: str) -> pathlib.Path:
    """Path of the per-session heartbeat file (shared with the PreToolUse lock)."""
    temiz = re.sub(r"[^A-Za-z0-9_-]", "", oturum)[:64] or "bilinmeyen"
    return pathlib.Path(state_dir) / f"calisti-{temiz}"


def calisti_isareti(state_dir: pathlib.Path, oturum: str) -> None:
    """Marks that this hook ran in the session (the Revit lock relies on it); never raises."""
    try:
        pathlib.Path(state_dir).mkdir(parents=True, exist_ok=True)
        calisti_yolu(state_dir, oturum).touch()
    except Exception:
        pass


def _onay_cikti(data: dict, prompt: str, session_id: str):
    """Records approval/rejection from the person's message; returns the output JSON or None."""
    try:
        proje = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
        text = onay.isle(pathlib.Path(proje), session_id, prompt)
    except Exception:
        return None
    if not text or len(text.encode("utf-8")) > MAX_CONTEXT_BYTES:
        return None
    payload = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}
    return json.dumps(payload, ensure_ascii=False)


def build_output(stdin_text: str, state_dir: pathlib.Path) -> str:
    try:
        data = json.loads(stdin_text)
        prompt = data.get("prompt")
        if not isinstance(prompt, str):
            return ""
        session_id = str(data.get("session_id") or "")
        calisti_isareti(state_dir, session_id)
        cikti = _onay_cikti(data, prompt, session_id)
        if cikti:
            return cikti
        if len(onkapi.normalize(prompt).split()) <= SHORT_REPLY_WORDS and onkapi.seen_any(session_id, state_dir):
            return ""  # a short follow-up ("evet", "Revit") answers a question; it is not a new job
        cards = onkapi.load_cards()
        ids = onkapi.match(prompt, cards)
        ids = onkapi.unseen(session_id, ids, state_dir) if ids else []
        if not ids:
            return ""
        text = onkapi.card_text(ids, cards, CARD_DIR)
        payload = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}
        return json.dumps(payload, ensure_ascii=False)
    except Exception:  # fail open: a front-door hook must never break the prompt
        return ""


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        stdin_text = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8", "replace")
        state_dir = varsayilan_durum_klasoru()
        sys.stdout.write(build_output(stdin_text, state_dir))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

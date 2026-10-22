"""UserPromptSubmit hook: adds a short routing card for the matching job, once per session.

Standard library only. On any error or no match it prints nothing.
"""
import json
import os
import pathlib
import sys
import tempfile

import onkapi

SHORT_REPLY_WORDS = 3
CARD_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills/istek-karsilama/kartlar"


def build_output(stdin_text: str, state_dir: pathlib.Path) -> str:
    try:
        data = json.loads(stdin_text)
        prompt = data.get("prompt")
        if not isinstance(prompt, str):
            return ""
        session_id = str(data.get("session_id") or "")
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
        state_dir = pathlib.Path(os.environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()) / "aec-onkapi"
        sys.stdout.write(build_output(stdin_text, state_dir))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

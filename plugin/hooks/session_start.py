"""SessionStart hook: puts the office order of authority, and a project's .aec folder if it has one, into the session.

Standard library only, so it runs under `uv run --no-project` without installing the aec package.
"""
import json
import os
import pathlib
import sys

AUTHORITY = pathlib.Path(__file__).resolve().parent.parent / "standards" / "authority.md"
MISSING = "UYARI: aec kurulumu eksik (standards/authority.md bulunamadı). Plugin'i yeniden kurun."
PROJECT_LINE = "Bu projede .aec klasörü var: {}. Proje kuralları ofis kurallarından önce gelir."


def build_output(project_dir: str | None, authority_path: pathlib.Path) -> str:
    try:
        text = pathlib.Path(authority_path).read_text(encoding="utf-8").strip()
    except OSError:
        text = MISSING
    if project_dir and (pathlib.Path(project_dir) / ".aec").is_dir():
        text += "\n" + PROJECT_LINE.format(project_dir)
    payload = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}
    return json.dumps(payload, ensure_ascii=False)


def _project_dir(stdin_text: str) -> str:
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return os.environ["CLAUDE_PROJECT_DIR"]
    try:
        data = json.loads(stdin_text or "{}")
    except ValueError:
        data = None
    cwd = data.get("cwd") if isinstance(data, dict) else None
    return cwd or os.getcwd()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    stdin_text = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
    sys.stdout.write(build_output(_project_dir(stdin_text), AUTHORITY))
    return 0


if __name__ == "__main__":
    sys.exit(main())

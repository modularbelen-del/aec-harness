"""SessionStart hook: puts the office role and order of authority, and a project's .aec folder if it has one, into
the session.

Standard library only, so it runs under `uv run --no-project` without installing the aec package.
"""
import json
import os
import pathlib
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from programlar import durum_satiri, running_programs  # noqa: E402

STANDARDS_DIR = PLUGIN_ROOT / "standards"
STANDARDS = (STANDARDS_DIR / "rol.md", STANDARDS_DIR / "authority.md")
MISSING = "UYARI: aec kurulumu eksik (standards/{} okunamadı). Plugin'i yeniden kurun."
PROJECT_LINE = "Bu projede .aec klasörü var: {}. Proje kuralları ofis kurallarından önce gelir."


def _read(path: pathlib.Path) -> str:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return MISSING.format(pathlib.Path(path).name)


def build_output(project_dir: str | None, paths=STANDARDS, acik=None) -> str:
    text = "\n\n".join(_read(p) for p in paths)
    if project_dir and (pathlib.Path(project_dir) / ".aec").is_dir():
        text += "\n" + PROJECT_LINE.format(project_dir)
    satir = durum_satiri(acik)
    if satir:
        text += "\n" + satir
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
    sys.stdout.write(build_output(_project_dir(stdin_text), acik=running_programs()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

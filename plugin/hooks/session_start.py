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

import is_durumu  # noqa: E402
from programlar import durum_satiri, running_programs  # noqa: E402

STANDARDS_DIR = PLUGIN_ROOT / "standards"
STANDARDS = (STANDARDS_DIR / "rol.md", STANDARDS_DIR / "authority.md")
MISSING = "UYARI: aec kurulumu eksik (standards/{} okunamadı). Plugin'i yeniden kurun."
PROJECT_LINE = "Bu projede .aec klasörü var: {}. Proje kuralları ofis kurallarından önce gelir."
NO_PROJECT_LINE = "Bu klasörde proje bilgisi bulunmamaktadır; ilk istekte /aec:proje-baslat önerilmelidir."
OPEN_JOB_LINE = "Açık iş: {} ({})"
MAX_OPEN_JOBS = 3
MAX_BYTES = 4096
NL = chr(10)


def _read(path: pathlib.Path) -> str:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return MISSING.format(pathlib.Path(path).name)


def _open_job_lines(project_dir: str | None) -> list[str]:
    try:
        jobs = is_durumu.acik_isler(pathlib.Path(project_dir)) if project_dir else []
        return [OPEN_JOB_LINE.format(j.get("id"), j.get("durum")) for j in jobs[:MAX_OPEN_JOBS]]
    except Exception:
        return []


def _payload(text: str) -> str:
    return json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}},
                      ensure_ascii=False)


def build_output(project_dir: str | None, paths=STANDARDS, acik=None) -> str:
    text = (NL * 2).join(_read(p) for p in paths)
    if project_dir and (pathlib.Path(project_dir) / ".aec" / "proje.md").is_file():
        text += NL + PROJECT_LINE.format(project_dir)
    else:
        text += NL + NO_PROJECT_LINE
    satir = durum_satiri(acik)
    if satir:
        text += NL + satir
    jobs = _open_job_lines(project_dir)
    while jobs:  # the open-job list is the first thing to give way to the size limit
        out = _payload(text + NL + NL.join(jobs))
        if len(out.encode("utf-8")) <= MAX_BYTES:
            return out
        jobs.pop()
    return _payload(text)


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

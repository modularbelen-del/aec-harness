"""Repo rules that CI enforces: no local user paths, LF/UTF-8 Python files, valid JSON."""
import getpass
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCAN_DIRS = ("plugin", "tests", "tools", ".claude-plugin")
TEXT_SUFFIXES = {".py", ".json", ".md", ".ps1", ".toml", ".yml", ".yaml", ".ini", ".txt"}
SKIP_PARTS = {".venv", "__pycache__", ".pytest_cache", "results"}
# Written so that this pattern's own text does not match it.
USER_PATH = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]|/[a-zA-Z]/Users/")


def _files(suffixes):
    for name in SCAN_DIRS:
        base = ROOT / name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes and not SKIP_PARTS & set(path.parts):
                yield path


def test_no_user_paths():
    user = getpass.getuser().lower()
    bad = []
    for path in _files(TEXT_SUFFIXES):
        text = path.read_text(encoding="utf-8", errors="replace")
        if USER_PATH.search(text) or (len(user) >= 4 and user in text.lower()):
            bad.append(str(path.relative_to(ROOT)))
    assert bad == []


def test_python_files_lf_utf8_no_bom():
    bad = []
    for path in _files({".py"}):
        raw = path.read_bytes()
        if b"\r\n" in raw or raw.startswith(b"\xef\xbb\xbf"):
            bad.append(str(path.relative_to(ROOT)))
            continue
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            bad.append(str(path.relative_to(ROOT)))
    assert bad == []


def test_json_files_parse():
    for path in _files({".json"}):
        json.loads(path.read_text(encoding="utf-8"))

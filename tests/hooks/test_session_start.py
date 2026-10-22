"""SessionStart hook: injects the office role and order of authority and notes a project's .aec folder."""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugin" / "hooks" / "session_start.py"
AUTH = ROOT / "plugin" / "standards" / "authority.md"
ROLE = ROOT / "plugin" / "standards" / "rol.md"
PROJECT_MARK = "Bu projede .aec klasörü var"


def _hook():
    spec = importlib.util.spec_from_file_location("session_start", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ctx(out):
    data = json.loads(out)["hookSpecificOutput"]
    assert data["hookEventName"] == "SessionStart"
    return data["additionalContext"]


def _run(env_project, stdin=b"{}"):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8", "CLAUDE_PROJECT_DIR")}
    if env_project is not None:
        env["CLAUDE_PROJECT_DIR"] = env_project
    return subprocess.run([sys.executable, str(SCRIPT)], input=stdin, capture_output=True, env=env)


def test_injects_authority(tmp_path):
    ctx = _ctx(_hook().build_output(str(tmp_path)))
    assert "Yetki sırası" in ctx and "1. Çizim" in ctx
    assert PROJECT_MARK not in ctx


def test_reports_project_aec(tmp_path):
    (tmp_path / ".aec").mkdir()
    ctx = _ctx(_hook().build_output(str(tmp_path)))
    assert PROJECT_MARK in ctx and str(tmp_path) in ctx


def test_injects_role_before_authority(tmp_path):
    ctx = _ctx(_hook().build_output(str(tmp_path)))
    assert "30 yıllık" in ctx and "MCP" in ctx
    assert ctx.index("30 yıllık") < ctx.index("Yetki sırası")


def test_missing_role_warns_and_keeps_authority(tmp_path):
    ctx = _ctx(_hook().build_output(str(tmp_path), [tmp_path / "yok.md", AUTH]))
    assert "UYARI" in ctx and "yok.md" in ctx
    assert "Yetki sırası" in ctx


def test_missing_authority_warns(tmp_path):
    ctx = _ctx(_hook().build_output(str(tmp_path), [tmp_path / "yok.md"]))
    assert "UYARI" in ctx


def test_corrupt_authority_warns(tmp_path):
    bad = tmp_path / "authority.md"
    bad.write_bytes("Yetki sırası".encode("cp1254"))
    ctx = _ctx(_hook().build_output(str(tmp_path), [bad]))
    assert "UYARI" in ctx


def test_under_4kb(tmp_path):
    # As long a Turkish folder name as Windows lets us create (CreateDirectory stops at 248 characters).
    room = max(20, min(150, 240 - len(str(tmp_path)) - len("\\.aec")))
    deep = tmp_path / ("Çakışma" * 22)[:room]
    (deep / ".aec").mkdir(parents=True)
    out = _hook().build_output(str(deep))
    assert PROJECT_MARK in _ctx(out)
    assert len(out.encode("utf-8")) <= 4096


def test_subprocess_turkish_space_path(tmp_path):
    project = tmp_path / "Proje Çakışma"
    (project / ".aec").mkdir(parents=True)
    result = _run(str(project))
    assert result.returncode == 0, result.stderr
    assert str(project) in _ctx(result.stdout.decode("utf-8"))


def test_stdin_cwd_used_without_env(tmp_path):
    project = tmp_path / "Şantiye"
    (project / ".aec").mkdir(parents=True)
    result = _run(None, json.dumps({"cwd": str(project)}).encode("utf-8"))
    assert result.returncode == 0, result.stderr
    assert str(project) in _ctx(result.stdout.decode("utf-8"))

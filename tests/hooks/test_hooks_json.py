"""hooks.json commands must never surface a hook error, even when uv is missing."""
import json
import os
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugin"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
HOOK_CMD = 'uv run --no-project --python 3.12 python "${{CLAUDE_PLUGIN_ROOT}}/hooks/{}.py"; exit 0'
REVIT_PRE = "mcp__.*[Rr][Ee][Vv][Ii][Tt].*__(execute_revit_code|place_family|close_document|save_document|sync_with_central)"
REVIT_POST = "mcp__.*[Rr][Ee][Vv][Ii][Tt].*__(execute_revit_code|place_family)"
TIMEOUTS = {"SessionStart": 30, "UserPromptSubmit": 10, "PreToolUse": 10, "PostToolUse": 10, "Stop": 10, "SubagentStop": 15}


def _hooks():
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]


def _command(event_name):
    cmd = _hooks()[event_name][0]["hooks"][0]["command"]
    return cmd.replace("${CLAUDE_PLUGIN_ROOT}", PLUGIN.as_posix())


def _shell_argv(kind, cmd):
    exe = shutil.which(kind)
    if exe is None:
        pytest.skip(f"{kind} not available")
    if kind == "bash":
        return [exe, "-c", cmd]
    return [exe, "-NoProfile", "-NonInteractive", "-Command", cmd]


def _env(path):
    env = dict(os.environ)
    env["PATH"] = path
    return env


def test_every_hook_is_fail_open_with_timeout():
    for event, entries in _hooks().items():
        for h in (h for e in entries for h in e["hooks"]):
            assert h["command"].endswith("; exit 0"), event
            assert h["timeout"] == TIMEOUTS[event]


def test_session_start_command_matches_template():
    assert _hooks()["SessionStart"][0]["hooks"][0]["command"] == HOOK_CMD.format("session_start")


def test_user_prompt_command_matches_template():
    assert _hooks()["UserPromptSubmit"][0]["hooks"][0]["command"] == HOOK_CMD.format("user_prompt")


def test_session_start_survives_missing_uv_bash():
    argv = _shell_argv("bash", _command("SessionStart"))
    result = subprocess.run(argv, input=b"{}", capture_output=True, env=_env(""))
    assert result.returncode == 0, result.stderr
    assert result.stdout == b""


def test_session_start_survives_missing_uv_powershell():
    argv = _shell_argv("powershell", _command("SessionStart"))
    system32 = str(pathlib.Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32")
    result = subprocess.run(argv, input=b"{}", capture_output=True, env=_env(system32))
    assert result.returncode == 0, result.stderr
    assert result.stdout == b""


def test_session_start_runs_with_uv_bash():
    if shutil.which("uv") is None:
        pytest.skip("uv not available")
    argv = _shell_argv("bash", _command("SessionStart"))
    result = subprocess.run(argv, input=b"{}", capture_output=True, env=dict(os.environ))
    assert result.returncode == 0, result.stderr
    json.loads(result.stdout.decode("utf-8"))


def test_tool_hooks_commands_and_matchers():
    h = _hooks()
    assert [e["matcher"] for e in h["PreToolUse"]] == [REVIT_PRE, "Write|Edit|NotebookEdit|Agent|Task"]
    assert all(e["hooks"][0]["command"] == HOOK_CMD.format("pre_tool") for e in h["PreToolUse"])
    assert h["PostToolUse"][0]["matcher"] == "Bash|PowerShell|" + REVIT_POST
    assert h["PostToolUse"][0]["hooks"][0]["command"] == HOOK_CMD.format("post_tool")


def test_stop_hooks_commands_and_matcher():
    h = _hooks()
    assert "matcher" not in h["Stop"][0]
    assert h["Stop"][0]["hooks"][0]["command"] == HOOK_CMD.format("stop_kontrol")
    assert h["SubagentStop"][0]["matcher"] == "dogrulayici|aec:dogrulayici"
    assert h["SubagentStop"][0]["hooks"][0]["command"] == HOOK_CMD.format("dogrulama_kaydi")

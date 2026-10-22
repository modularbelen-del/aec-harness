import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_marketplace_lists_single_aec_plugin():
    m = _load(".claude-plugin/marketplace.json")
    assert m["name"] == "aec-office"
    assert [(p["name"], p["source"]) for p in m["plugins"]] == [("aec", "./plugin")]


def test_plugin_manifest_name():
    assert _load("plugin/.claude-plugin/plugin.json")["name"] == "aec"


def test_no_version_fields():
    for path in (".claude-plugin/marketplace.json", "plugin/.claude-plugin/plugin.json"):
        assert '"version"' not in (ROOT / path).read_text(encoding="utf-8"), path


def test_license_is_mit():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Copyright (c) 2026 BelenPartners" in text
    assert _load("plugin/.claude-plugin/plugin.json")["license"] == "MIT"


def test_owner_and_author_are_the_office():
    assert _load(".claude-plugin/marketplace.json")["owner"]["name"] == "BelenPartners"
    assert _load("plugin/.claude-plugin/plugin.json")["author"]["name"] == "BelenPartners"
    assert "<ofis>" not in (ROOT / "README.md").read_text(encoding="utf-8")


def test_no_bin_dir_in_plugin():
    assert not (ROOT / "plugin" / "bin").exists()


def test_user_config_options_have_defaults():
    cfg = _load("plugin/.claude-plugin/plugin.json").get("userConfig", {})
    assert all("default" in opt for opt in cfg.values())


def test_ci_runs_on_main_and_dev():
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "branches: [main, dev]" in text
    assert "claude plugin validate" in text

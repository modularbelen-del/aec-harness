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

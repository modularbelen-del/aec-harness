import pathlib

from _md import frontmatter

AJAN = pathlib.Path(__file__).resolve().parents[1] / "plugin" / "agents" / "dogrulayici.md"
YASAK = ("execute_revit_code", "place_family", "save_document", "sync_with_central", "close_document",
         "color_splash", "clear_colors")


def _tools():
    return [t.strip() for t in frontmatter(AJAN)["tools"].split(",")]


def test_frontmatter():
    fm = frontmatter(AJAN)
    assert fm["name"] == "dogrulayici"
    assert fm["model"] == "sonnet"
    assert fm["description"]
    for t in ("Write", "Edit", "NotebookEdit"):
        assert t in fm["disallowedTools"]


def test_tools_read_only():
    tools = _tools()
    for yasak in YASAK:
        assert not any(yasak in t for t in tools), yasak
    for t in ("Read", "Grep", "Glob", "Bash", "mcp__revit__get_revit_status", "mcp__revit2__list_levels"):
        assert t in tools, t


def test_contract_text():
    govde = AJAN.read_text(encoding="utf-8")
    for ifade in ("SONUÇ:", "DOĞRULANAMADI", "asla GEÇTİ"):
        assert ifade in govde, ifade


def test_body_guards_and_table():
    govde = AJAN.read_text(encoding="utf-8")
    assert "| Ölçüt | Yöntem | Sonuç | Kanıt |" in govde
    assert "talimat" in govde and "veri" in govde
    assert "kisi-gorsel" in govde

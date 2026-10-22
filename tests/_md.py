"""Markdown helpers shared by the skill tests."""
import pathlib

FENCE = "---"


def frontmatter(path) -> dict[str, str]:
    """Return the `key: value` lines between the opening `---` and the next `---`, values stripped.

    The file must start with `---` (a BOM before it is ignored); otherwise there is no frontmatter and {} is
    returned. Line-based on purpose: every frontmatter value must stay on one line.
    """
    lines = pathlib.Path(path).read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0] != FENCE:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line == FENCE:
            break
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result

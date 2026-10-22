"""Markdown helpers shared by the skill tests."""
import pathlib

FENCE = "---"


def frontmatter(path) -> dict[str, str]:
    """Return the `key: value` lines between the first two `---` lines, values stripped.

    Line-based on purpose: every frontmatter value must stay on one line.
    """
    result: dict[str, str] = {}
    fences = 0
    for line in pathlib.Path(path).read_text(encoding="utf-8-sig").splitlines():
        if line.strip() == FENCE:
            fences += 1
            if fences == 2:
                break
            continue
        if fences == 1 and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result

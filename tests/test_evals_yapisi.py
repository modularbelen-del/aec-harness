"""Eval seti yapısı: her vakada prompt.md, her davranis.md'de yargıç ön bilgisi."""
import pathlib

EVALS = pathlib.Path(__file__).resolve().parents[1] / "plugin" / "evals"
PREMISE = "Bu deneme ortamında proje klasöründe CLAUDE.md / .aec/proje.md yoktur ve Revit, AutoCAD, Rhino bağlı değildir."


def _cases():
    return sorted(p for p in EVALS.iterdir() if p.is_dir() and p.name != "results")


def test_every_case_has_prompt():
    assert _cases()
    assert [c.name for c in _cases() if not (c / "prompt.md").is_file()] == []


def test_every_davranis_has_premise():
    files = list(EVALS.glob("*/graders/davranis.md"))
    assert files
    assert [str(f.parent.parent.name) for f in files if PREMISE not in f.read_text(encoding="utf-8")] == []


def test_ofis_disi_case_exists():
    assert (EVALS / "ofis-disi" / "graders" / "skill-yok.md").is_file()


FAIL_PROGRAM = ("ya da istek bir program gerektirirken ve o program bağlı değilken yanıtın ne bunu söylemesi ne de "
                "kontrol edeceğini belirtmesi, ya da bağlıymış gibi sonuç uydurması.")


def test_davranis_fail_clause_is_plain():
    files = list(EVALS.glob("*/graders/davranis.md"))
    assert files
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert "yokmuş gibi söylememe" not in text, f.parent.parent.name
        assert FAIL_PROGRAM in text, f.parent.parent.name


def test_readme_matches_case_count_and_cost_flags():
    text = (EVALS / "README.md").read_text(encoding="utf-8")
    assert f"{len(_cases())} vaka x 3 koşu" in text
    assert "--max-cost-usd 4" in text and "--max-cost-usd 10" in text

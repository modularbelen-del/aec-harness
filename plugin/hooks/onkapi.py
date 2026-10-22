"""Front door for UserPromptSubmit: picks at most two job cards by keyword and builds the fixed routing card.

Standard library only. Nothing here may raise on bad state; the card text never contains the user's prompt.
"""
import json
import pathlib
import re

CARDS_JSON = pathlib.Path(__file__).resolve().parent.parent / "skills" / "istek-karsilama" / "kartlar.json"
MAX_CARDS = 2
UNKNOWN_SESSION = "bilinmeyen"
_FOLD = str.maketrans("çğıöşü", "cgiosu")
_APOSTROPHES = str.maketrans("", "", "'’")
_NON_WORD = re.compile(r"[^a-z0-9]+")
_SESSION_CHARS = re.compile(r"[^A-Za-z0-9_-]")
CARD_TEMPLATE = (
    "[aec ön kapı] İş: {titles}.\n"
    "Önce istek-karsilama skill'ini yükle ve kartı oku: {paths}\n"
    "Eksik olabilir: {missing}.\n"
    "Az sor, çok göster: proje MD'sine bak, en fazla 3 soru sor, varsayımları VARSAYIM diye yaz, "
    "planı göster, onay al; uyguladıktan sonra geri oku."
)


def normalize(text: str) -> str:
    text = text.replace("İ", "i").replace("I", "ı").lower().translate(_FOLD).translate(_APOSTROPHES)
    return _NON_WORD.sub(" ", text).strip()


def load_cards(path: pathlib.Path = CARDS_JSON) -> list[dict]:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def match(prompt: str, cards: list[dict]) -> list[str]:
    norm = normalize(prompt)
    scored = []
    for index, card in enumerate(cards):
        keywords = {normalize(k) for k in card["anahtar"]}
        hits = sum(1 for k in keywords if k and re.search(r"(?<![a-z0-9])" + re.escape(k), norm))
        if hits:
            scored.append((-hits, index, card["id"]))
    scored.sort()
    return [card_id for _, _, card_id in scored[:MAX_CARDS]]


def card_text(ids: list[str], cards: list[dict], card_dir: pathlib.Path) -> str:
    by_id = {c["id"]: c for c in cards}
    chosen = [by_id[i] for i in ids if i in by_id]
    missing: list[str] = []
    for card in chosen:
        for item in card["eksikler"]:
            if item not in missing:
                missing.append(item)
    return CARD_TEMPLATE.format(
        titles=", ".join(c["baslik"] for c in chosen),
        paths="; ".join((pathlib.Path(card_dir) / f"{c['id']}.md").as_posix() for c in chosen),
        missing=", ".join(missing),
    )


def unseen(session_id: str, ids: list[str], state_dir: pathlib.Path) -> list[str]:
    safe = _SESSION_CHARS.sub("", str(session_id)) or UNKNOWN_SESSION
    state_file = pathlib.Path(state_dir) / f"onkapi-{safe}.json"
    try:
        seen = json.loads(state_file.read_text(encoding="utf-8"))
        if not isinstance(seen, list):
            seen = []
    except (OSError, ValueError):
        seen = []
    new = [i for i in ids if i not in seen]
    if new:
        try:
            pathlib.Path(state_dir).mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(seen + new), encoding="utf-8")
        except (OSError, ValueError):
            pass
    return new

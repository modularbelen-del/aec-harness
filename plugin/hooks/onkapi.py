"""Front door for UserPromptSubmit: picks at most two job cards by keyword and builds the fixed routing card.

Standard library only. Nothing here may raise on bad state; the card text never contains the user's prompt.
"""
import json
import pathlib
import re
import unicodedata

CARDS_JSON = pathlib.Path(__file__).resolve().parent.parent / "skills" / "istek-karsilama" / "kartlar.json"
MAX_CARDS = 2
UNKNOWN_SESSION = "bilinmeyen"
_APOSTROPHES = str.maketrans("", "", "'’´`")
_LEFT_BOUNDARY = r"(?<![a-z0-9])"
_REGEX_PREFIX = "re:"
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
    text = text.replace("İ", "i").replace("I", "ı").lower().translate(_APOSTROPHES)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn").replace("ı", "i")
    return _NON_WORD.sub(" ", text).strip()


def load_cards(path: pathlib.Path = CARDS_JSON) -> list[dict]:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def _compile(keyword: str):
    """Plain keywords are normalized and escaped; `re:` keywords are raw regexes on the normalized text."""
    if keyword.startswith(_REGEX_PREFIX):
        body = keyword[len(_REGEX_PREFIX):]
    else:
        body = re.escape(normalize(keyword))
    if not body:
        return None
    try:
        return re.compile(_LEFT_BOUNDARY + body)
    except re.error:
        return None


def match(prompt: str, cards: list[dict]) -> list[str]:
    norm = normalize(prompt)
    scored = []
    for index, card in enumerate(cards):
        patterns = [_compile(k) for k in dict.fromkeys(card["anahtar"])]
        hits = sum(1 for pat in patterns if pat and pat.search(norm))
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


def _state_file(session_id: str, state_dir: pathlib.Path) -> pathlib.Path:
    safe = _SESSION_CHARS.sub("", str(session_id)) or UNKNOWN_SESSION
    return pathlib.Path(state_dir) / f"onkapi-{safe}.json"


def _read_seen(state_file: pathlib.Path) -> list:
    try:
        seen = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return seen if isinstance(seen, list) else []


def seen_any(session_id: str, state_dir: pathlib.Path) -> bool:
    return bool(_read_seen(_state_file(session_id, state_dir)))


def unseen(session_id: str, ids: list[str], state_dir: pathlib.Path) -> list[str]:
    state_file = _state_file(session_id, state_dir)
    seen = _read_seen(state_file)
    new = [i for i in ids if i not in seen]
    if new:
        try:
            pathlib.Path(state_dir).mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(seen + new), encoding="utf-8")
        except (OSError, ValueError):
            pass
    return new

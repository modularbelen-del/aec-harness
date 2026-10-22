"""Job record library (aec.is/1): state machine, per-session binding and journal; standard library only."""
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from proje_baslat import _yasak_hedef, _yaz_metin

ISLER = ".aec/isler"
GUNLUK = ".aec/gunluk.md"
GUNLUK_BASLIK = "# İş günlüğü"
SEMA = "aec.is/1"

DURUMLAR = (
    "gorusme",
    "onay-bekliyor:tarif", "onay-bekliyor:plan", "onay-bekliyor:gorevler",
    "onaylandi:tarif", "onaylandi:plan",
    "plan-onaylandi", "uygulandi", "kabul-bekliyor", "kabul-edildi", "reddedildi", "iptal",
)
BITMIS = frozenset({"kabul-edildi", "reddedildi", "iptal"})
KAYNAKLAR = frozenset({"ajan", "kullanici-mesaji", "hook-post", "hook-subagent", "hook-stop"})
ASAMALAR = ("tarif", "plan", "gorevler")

IZINLI: "dict[str, set[str]]" = {
    "gorusme": {"onay-bekliyor:plan", "onay-bekliyor:tarif", "iptal"},
    "onay-bekliyor:tarif": {"onaylandi:tarif", "plan-onaylandi", "reddedildi", "iptal", "onay-bekliyor:tarif"},
    "onay-bekliyor:plan": {"onaylandi:plan", "plan-onaylandi", "reddedildi", "iptal", "onay-bekliyor:plan"},
    "onay-bekliyor:gorevler": {"plan-onaylandi", "reddedildi", "iptal", "onay-bekliyor:gorevler"},
    "onaylandi:tarif": {"onay-bekliyor:plan", "iptal"},
    "onaylandi:plan": {"onay-bekliyor:gorevler", "iptal"},
    "plan-onaylandi": {"uygulandi", "onay-bekliyor:plan", "iptal"},
    "uygulandi": {"kabul-bekliyor", "iptal"},
    "kabul-bekliyor": {"kabul-edildi", "reddedildi", "iptal"},
    "reddedildi": {"onay-bekliyor:tarif", "onay-bekliyor:plan", "iptal"},
    "kabul-edildi": set(),
    "iptal": set(),
}

_ASCII = str.maketrans({"İ": "i", "I": "i", "ı": "i", "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g",
                        "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u"})
_GECERSIZ_KIMLIK = re.compile(r"[^A-Za-z0-9_-]")


def _kisa_ad(baslik: str) -> str:
    s = baslik.translate(_ASCII).lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40].strip("-")
    return s or "is"


def _zaman() -> str:
    return datetime.now().astimezone().isoformat(timespec="minutes")


def _is_klasoru(proje: Path, is_id: str) -> Path:
    if not is_id or _GECERSIZ_KIMLIK.search(is_id):
        raise ValueError(f"✗ Geçersiz iş kimliği: {is_id!r}.")
    return Path(proje) / ISLER / is_id


def _yaz_json(yol: Path, veri: dict) -> None:
    _yaz_metin(yol, json.dumps(veri, ensure_ascii=False, indent=2) + "\n")


def yeni_is(proje: Path, kart: str, baslik: str, karmasik: bool, simdi: "datetime | None" = None) -> dict:
    proje = Path(proje)
    yasak = _yasak_hedef(proje)
    if yasak:
        raise ValueError(yasak)
    simdi = simdi or datetime.now().astimezone()
    taban = f"{simdi.strftime('%Y%m%d-%H%M')}-{_kisa_ad(baslik)}"
    kok = proje / ISLER
    kok.mkdir(parents=True, exist_ok=True)
    is_id, sayi = taban, 1
    while True:
        try:
            (kok / is_id).mkdir()
            break
        except FileExistsError:
            sayi += 1
            is_id = f"{taban}-{sayi}"
    zaman = simdi.isoformat(timespec="minutes")
    kayit = {
        "sema": SEMA, "id": is_id, "kart": kart, "baslik": baslik, "karmasik": bool(karmasik),
        "durum": "gorusme", "olcutler": [], "sonuc": None, "oturum": None,
        "olaylar": [{"zaman": zaman, "eski": None, "yeni": "gorusme", "kaynak": "ajan", "not": "iş açıldı"}],
    }
    is_kaydet(proje, kayit)
    return kayit


def is_yukle(proje: Path, is_id: str) -> dict:
    yol = _is_klasoru(proje, is_id) / "is.json"
    try:
        return json.loads(yol.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"✗ İş bulunamadı: {is_id}.") from None


def is_kaydet(proje: Path, kayit: dict) -> None:
    klasor = _is_klasoru(proje, kayit["id"])
    klasor.mkdir(parents=True, exist_ok=True)
    _yaz_json(klasor / "is.json", kayit)


def gecis(kayit: dict, yeni: str, kaynak: str, not_: str = "") -> dict:
    """Moves the record to a new state in memory (caller saves); raises ValueError when not allowed."""
    eski = kayit["durum"]
    if kaynak not in KAYNAKLAR:
        raise ValueError(f"✗ Geçersiz geçiş kaynağı: {kaynak}.")
    if yeni not in IZINLI.get(eski, set()):
        raise ValueError(f"✗ '{eski}' durumundan '{yeni}' durumuna geçişe izin verilmemektedir.")
    if yeni == "onay-bekliyor:tarif" and eski in ("gorusme", "reddedildi") and not kayit.get("karmasik"):
        raise ValueError("✗ Basit işte tarif aşaması yoktur; ilk aşama 'onay-bekliyor:plan' olmalıdır.")
    if eski == "gorusme" and yeni == "onay-bekliyor:plan" and kayit.get("karmasik"):
        raise ValueError("✗ Karmaşık işte ilk aşama 'onay-bekliyor:tarif' olmalıdır.")
    kayit["durum"] = yeni
    kayit.setdefault("olaylar", []).append(
        {"zaman": _zaman(), "eski": eski, "yeni": yeni, "kaynak": kaynak, "not": not_})
    return kayit


def onay_sonrasi(kayit: dict, asama: str) -> str:
    if not kayit.get("karmasik"):
        if asama == "plan":
            return "plan-onaylandi"
    elif asama in ("tarif", "plan"):
        return f"onaylandi:{asama}"
    elif asama == "gorevler":
        return "plan-onaylandi"
    raise ValueError(f"✗ Bu iş türü için '{asama}' aşaması onaylanamaz.")


def _aktif_yol(proje: Path, oturum: str) -> Path:
    temiz = _GECERSIZ_KIMLIK.sub("", oturum)[:64] or "bilinmeyen"
    return Path(proje) / ISLER / f"aktif-{temiz}.json"


def aktif_bagla(proje: Path, oturum: str, is_id: str) -> None:
    _is_klasoru(proje, is_id)
    yol = _aktif_yol(proje, oturum)
    yol.parent.mkdir(parents=True, exist_ok=True)
    _yaz_json(yol, {"is": is_id})


def aktif_is(proje: Path, oturum: str) -> "dict | None":
    try:
        bag = json.loads(_aktif_yol(proje, oturum).read_text(encoding="utf-8"))
        return is_yukle(proje, bag["is"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def acik_isler(proje: Path) -> "list[dict]":
    kok = Path(proje) / ISLER
    if not kok.is_dir():
        return []
    isler = []
    for yol in kok.glob("*/is.json"):
        try:
            kayit = json.loads(yol.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(kayit, dict) and kayit.get("durum") not in BITMIS:
            isler.append(kayit)
    return sorted(isler, key=lambda k: str(k.get("id", "")), reverse=True)


def gunluge_yaz(proje: Path, satir: str) -> None:
    yol = Path(proje) / GUNLUK
    yol.parent.mkdir(parents=True, exist_ok=True)
    mevcut = yol.read_text(encoding="utf-8") if yol.is_file() else f"{GUNLUK_BASLIK}\n\n"
    if mevcut and not mevcut.endswith("\n"):
        mevcut += "\n"
    _yaz_metin(yol, mevcut + satir.rstrip("\n") + "\n")

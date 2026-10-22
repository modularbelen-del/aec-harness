"""Records the person's approval, rejection or acceptance from their own message (code, never the agent).

Standard library only. Recognition is deliberately narrow: only short, unambiguous messages count.
"""
import pathlib
import re
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import is_durumu  # noqa: E402
import onkapi  # noqa: E402
from yol import gunluk_satiri as _gunluk_satiri  # noqa: E402

KAYNAK = "kullanici-mesaji"
EN_FAZLA_KELIME = 4
ONAY = frozenset("evet onayliyorum onayladim onay uygula uygulayin kabul devam".split())
KABUL_ONAY = frozenset("evet kabul onay onayliyorum onayladim".split())  # narrower: acceptance unlocks saving
RET = frozenset("hayir iptal vazgec vazgectim reddediyorum ret red durdur".split())
DOLGU = frozenset("lutfen tesekkurler tesekkur ederim tamam peki et edin hocam ediyorum".split())
SORU_ISARETLERI = ("?", "？", "؟", "¿")

SONRAKI_ADIM = {
    "plan-onaylandi": "Uygulamaya geçilebilir.",
    "onaylandi:tarif": "Sıradaki adım planın hazırlanıp onaya sunulmasıdır.",
    "onaylandi:plan": "Sıradaki adım görevlerin hazırlanıp onaya sunulmasıdır.",
}
ASAMA_ADI = {"tarif": "tarif", "plan": "plan", "gorevler": "görevler", "kabul": "kabul"}
RET_SONRASI = {
    "tarif": "Tarif gerekçeyle yeniden hazırlanmalıdır.",
    "plan": "Plan gerekçeyle yeniden hazırlanmalıdır.",
    "gorevler": "Görevler gerekçeyle yeniden hazırlanmalıdır.",
    "kabul": "İş gerekçeyle yeniden planlanmalıdır.",
}
KABUL_METNI = "[aec] Kabulünüz kaydedildi. İş tamamlanmıştır."
BELIRSIZ_METNI = ('[aec] Bu mesaj onay olarak kaydedilmedi. Onay için yalnızca "evet", '
                  'ret için yalnızca "hayır" yazılması istenmelidir. Mesaj bir soru ya da değişiklik isteğiyse '
                  'önce yanıtlanmalı; plan değiştiyse yeniden onaya sunulmalıdır.')
BAGLI_IS_YOK_METNI = ("[aec] Bu oturuma bağlı bir iş bulunmadığından mesajınız onay olarak kaydedilmedi. "
                      "Açık işe devam etmek için `devam` komutu kullanılmalıdır.")
IPTAL_KELIMELERI = frozenset("iptal vazgec vazgectim".split())
IPTAL_NOTU = "Kişi işten vazgeçtiyse iş `iptal` komutuyla kapatılmalıdır."
_GECERSIZ_OTURUM = re.compile(r"[^A-Za-z0-9_-]")


def siniflandir(mesaj: str, kabul: bool = False) -> str:
    """Returns "onay", "ret" or "belirsiz"; kabul=True applies the narrower acceptance word set."""
    if any(i in mesaj for i in SORU_ISARETLERI):
        return "belirsiz"
    kelimeler = onkapi.normalize(mesaj).split()
    if not 1 <= len(kelimeler) <= EN_FAZLA_KELIME:
        return "belirsiz"
    onay = KABUL_ONAY if kabul else ONAY
    if all(k in onay or k in DOLGU for k in kelimeler) and any(k in onay for k in kelimeler):
        return "onay"
    if all(k in RET or k in DOLGU for k in kelimeler) and any(k in RET for k in kelimeler):
        return "ret"
    return "belirsiz"


def _gunluge_yaz(proje: pathlib.Path, satir: str) -> None:
    try:  # best effort: a recorded state change must still return its notice
        is_durumu.gunluge_yaz(proje, satir)
    except Exception:
        pass


def _bekleyen_is_var(proje: pathlib.Path) -> bool:
    """True when some job in the project waits for an approval or acceptance (bound to any session, or to none)."""
    for kayit in is_durumu.acik_isler(proje):
        durum = kayit.get("durum")
        if isinstance(durum, str) and (durum.startswith("onay-bekliyor:") or durum == "kabul-bekliyor"):
            return True
    return False


def isle(proje: pathlib.Path, oturum: str, mesaj: str) -> "str | None":
    if not _GECERSIZ_OTURUM.sub("", oturum or ""):
        return None  # fail closed: no usable session id
    kayit = is_durumu.aktif_is(proje, oturum)
    if not kayit:
        # a decision word for a job of an earlier session records nothing; the agent is told to continue the job first
        if siniflandir(mesaj) != "belirsiz" and _bekleyen_is_var(proje):
            return BAGLI_IS_YOK_METNI
        return None
    durum = kayit.get("durum", "")
    if not (durum.startswith("onay-bekliyor:") or durum == "kabul-bekliyor"):
        return None
    kabul = durum == "kabul-bekliyor"
    sonuc = siniflandir(mesaj, kabul=kabul)
    if sonuc == "belirsiz":
        return BELIRSIZ_METNI
    asama = "kabul" if kabul else durum.split(":", 1)[1]
    if sonuc == "ret":
        metin = f"[aec] Ret kaydedildi: {ASAMA_ADI[asama]}. {RET_SONRASI[asama]}"
        if IPTAL_KELIMELERI & set(onkapi.normalize(mesaj).split()):
            metin += f" {IPTAL_NOTU}"
        is_durumu.gecis(kayit, "reddedildi", KAYNAK, "kullanıcı reddetti")
        is_durumu.is_kaydet(proje, kayit)
        _gunluge_yaz(proje, _gunluk_satiri(kayit, f"reddedildi ({ASAMA_ADI[asama]})"))
        return metin
    if kabul:
        is_durumu.gecis(kayit, "kabul-edildi", KAYNAK, "kullanıcı kabul etti")
        is_durumu.is_kaydet(proje, kayit)
        _gunluge_yaz(proje, _gunluk_satiri(kayit, "kabul edildi"))
        return KABUL_METNI
    yeni = is_durumu.onay_sonrasi(kayit, asama)
    metin = f"[aec] Onayınız kaydedildi: {ASAMA_ADI[asama]}. {SONRAKI_ADIM[yeni]}"
    is_durumu.gecis(kayit, yeni, KAYNAK, f"kullanıcı {asama} aşamasını onayladı")
    is_durumu.is_kaydet(proje, kayit)
    return metin

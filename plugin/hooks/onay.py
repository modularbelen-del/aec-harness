"""Records the person's approval, rejection or acceptance from their own message (code, never the agent).

Standard library only. Recognition is deliberately narrow: only short, unambiguous messages count.
"""
import pathlib
import sys
from datetime import datetime

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import is_durumu  # noqa: E402
import onkapi  # noqa: E402

KAYNAK = "kullanici-mesaji"
EN_FAZLA_KELIME = 4
ONAY = frozenset("evet onayliyorum onayladim onay uygula uygulayin kabul ediyorum devam".split())
RET = frozenset("hayir iptal vazgec vazgectim reddediyorum ret red durdur".split())
DOLGU = frozenset("lutfen tesekkurler tesekkur ederim tamam peki et edin hocam".split())

SONRAKI_ADIM = {
    "plan-onaylandi": "Uygulamaya geçilebilir.",
    "onaylandi:tarif": "Sıradaki adım planın hazırlanıp onaya sunulmasıdır.",
    "onaylandi:plan": "Sıradaki adım görevlerin hazırlanıp onaya sunulmasıdır.",
}
KABUL_METNI = "[aec] Kabulünüz kaydedildi. İş tamamlanmıştır."
BELIRSIZ_METNI = ('[aec] Bu mesaj onay olarak kaydedilmedi. Onay için yalnızca "evet", '
                  'ret için yalnızca "hayır" yazılması istenmelidir.')


def siniflandir(mesaj: str) -> str:
    if "?" in mesaj:
        return "belirsiz"
    kelimeler = onkapi.normalize(mesaj).split()
    if not 1 <= len(kelimeler) <= EN_FAZLA_KELIME:
        return "belirsiz"
    if all(k in ONAY or k in DOLGU for k in kelimeler) and any(k in ONAY for k in kelimeler):
        return "onay"
    if all(k in RET or k in DOLGU for k in kelimeler) and any(k in RET for k in kelimeler):
        return "ret"
    return "belirsiz"


def _gunluk_satiri(kayit: dict, olay: str) -> str:
    return "- {} | {} | {} | {} | {} | {}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M"), kayit.get("id"), kayit.get("kart"),
        "karmaşık" if kayit.get("karmasik") else "basit", kayit.get("sonuc") or "-", olay)


def isle(proje: pathlib.Path, oturum: str, mesaj: str) -> "str | None":
    kayit = is_durumu.aktif_is(proje, oturum)
    if not kayit:
        return None
    durum = kayit.get("durum", "")
    bekleyen = durum.startswith("onay-bekliyor:") or durum == "kabul-bekliyor"
    if not bekleyen:
        return None
    sonuc = siniflandir(mesaj)
    if sonuc == "belirsiz":
        return BELIRSIZ_METNI
    asama = "kabul" if durum == "kabul-bekliyor" else durum.split(":", 1)[1]
    if sonuc == "ret":
        is_durumu.gecis(kayit, "reddedildi", KAYNAK, "kullanıcı reddetti")
        is_durumu.is_kaydet(proje, kayit)
        is_durumu.gunluge_yaz(proje, _gunluk_satiri(kayit, "reddedildi"))
        return f"[aec] Ret kaydedildi: {asama}. Plan gerekçeyle yeniden hazırlanmalıdır."
    if durum == "kabul-bekliyor":
        is_durumu.gecis(kayit, "kabul-edildi", KAYNAK, "kullanıcı kabul etti")
        is_durumu.is_kaydet(proje, kayit)
        is_durumu.gunluge_yaz(proje, _gunluk_satiri(kayit, "kabul edildi"))
        return KABUL_METNI
    yeni = is_durumu.onay_sonrasi(kayit, asama)
    is_durumu.gecis(kayit, yeni, KAYNAK, f"kullanıcı {asama} aşamasını onayladı")
    is_durumu.is_kaydet(proje, kayit)
    return f"[aec] Onayınız kaydedildi: {asama}. {SONRAKI_ADIM[yeni]}"

"""Job record CLI for the agent: open or continue a job, record criteria, submit documents for approval, mark an approved
job applied.

There is deliberately no approval or acceptance subcommand; only hooks record those, from the person's own message.
`uygulandi` only moves an approved plan (plan-onaylandi) to applied, so that non-Revit work can reach the independent
verifier; it grants nothing the person has not approved.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import is_durumu  # noqa: E402
from proje_baslat import _yasak_hedef, _yaz_metin  # noqa: E402

YONTEMLER = ("revit-okuma", "dosya", "olcu", "kisi-gorsel")
PROJE_EK_BASLIK = "## Sonradan eklenenler"
OLCUT_GEREKLI = ("✗ Belge kaydedilmedi: işte kayıtlı kabul ölçütü bulunmamaktadır. Belge onaya sunulmadan önce "
                 "`olcut` komutuyla en az bir kabul ölçütü kaydedilmelidir.")


class _Ayristirici(argparse.ArgumentParser):
    def error(self, message):  # no usage dump on stderr; main prints a Turkish message
        raise SystemExit(2)


def _parser() -> argparse.ArgumentParser:
    p = _Ayristirici(prog="is_kaydi")
    alt = p.add_subparsers(dest="komut", required=True, parser_class=_Ayristirici)

    def ekle(ad, *, is_gerekli=True):
        s = alt.add_parser(ad)
        s.add_argument("--proje", required=True)
        if is_gerekli:
            s.add_argument("--is", dest="is_id", required=True)
        return s

    s = ekle("yeni", is_gerekli=False)
    s.add_argument("--kart", required=True)
    s.add_argument("--baslik", required=True)
    s.add_argument("--karmasik", action="store_true")
    s = ekle("olcut")
    s.add_argument("--olcut", required=True)
    s.add_argument("--yontem", required=True, choices=YONTEMLER)
    s.add_argument("--beklenen")
    s.add_argument("--tolerans")
    for ad in is_durumu.ASAMALAR:
        ekle(ad).add_argument("--dosya", required=True)
    ekle("durum")
    ekle("devam")
    ekle("uygulandi")
    ekle("iptal").add_argument("--gerekce", required=True)
    ekle("proje-ekle", is_gerekli=False).add_argument("--metin", required=True)
    return p


def _yeni(a) -> None:
    kayit = is_durumu.yeni_is(Path(a.proje), a.kart, a.baslik, a.karmasik)
    print(f"IS: {kayit['id']}")
    print("İş açıldı; durum: gorusme.")


def _olcut(a) -> None:
    proje = Path(a.proje)
    kayit = is_durumu.is_yukle(proje, a.is_id)
    if kayit["durum"] != "gorusme":
        print("✗ Kabul ölçütleri yalnızca görüşme aşamasında eklenebilir; plan sunulduktan sonra değiştirilemez.")
        return
    kayit["olcutler"].append({"olcut": a.olcut, "yontem": a.yontem, "beklenen": a.beklenen, "tolerans": a.tolerans})
    is_durumu.is_kaydet(proje, kayit)
    print(f"Ölçüt eklendi (toplam {len(kayit['olcutler'])}).")


def _oku_dosya(kaynak: str) -> str:
    ham = sys.stdin.buffer.read() if kaynak == "-" else Path(kaynak).read_bytes()
    return ham.decode("utf-8-sig")


def _asama(a) -> None:
    proje = Path(a.proje)
    kayit = is_durumu.is_yukle(proje, a.is_id)
    ilk_belge = "tarif" if kayit.get("karmasik") else "plan"
    if a.komut == ilk_belge and not kayit.get("olcutler"):
        print(OLCUT_GEREKLI)
        return
    metin = _oku_dosya(a.dosya)
    is_durumu.gecis(kayit, f"onay-bekliyor:{a.komut}", "ajan", f"{a.komut} sunuldu")
    klasor = proje / is_durumu.ISLER / kayit["id"]
    klasor.mkdir(parents=True, exist_ok=True)
    _yaz_metin(klasor / f"{a.komut}.md", metin)
    is_durumu.is_kaydet(proje, kayit)
    print(f"{a.komut}.md yazıldı; durum: {kayit['durum']}. Kişinin onayı beklenmektedir.")


def _durum(a) -> None:
    kayit = is_durumu.is_yukle(Path(a.proje), a.is_id)
    print(f"IS: {kayit['id']}")
    print(f"Durum: {kayit['durum']}")
    print(f"Karmaşık: {'evet' if kayit.get('karmasik') else 'hayır'}")
    print(f"Ölçüt sayısı: {len(kayit.get('olcutler', []))}")
    print(f"Sonuç: {kayit.get('sonuc') or '-'}")


def _devam(a) -> None:
    """Only prints the marker; the PostToolUse hook binds the job to the session (and asks again for a plan approval
    given in another session). Nothing is approved here."""
    kayit = is_durumu.is_yukle(Path(a.proje), a.is_id)
    durum = kayit["durum"]
    if durum in is_durumu.BITMIS:
        print(f"✗ Bu iş kapatılmıştır (durum: {durum}); devam edilemez. İş sürecekse yeni bir iş açılmalıdır.")
        return
    print(f"DEVAM: {kayit['id']}")
    print(f"Durum: {durum}. İş bu çıktıyla oturuma bağlanır; güncel durum `durum` komutuyla okunmalıdır.")
    if durum == "plan-onaylandi":
        print("Plan onayı başka bir oturumda verildiyse iş 'onay-bekliyor:plan' durumuna alınır; plan kişiye yeniden "
              "gösterilmeli ve onay yeniden istenmelidir.")


def _uygulandi(a) -> None:
    proje = Path(a.proje)
    kayit = is_durumu.is_yukle(proje, a.is_id)
    durum = kayit["durum"]
    if durum == "uygulandi":
        print("İş zaten uygulandı olarak kayıtlıdır; değişiklik yapılmadı. Durum: uygulandi.")
        return
    if durum != "plan-onaylandi":
        print(f"✗ Uygulama kaydı yalnızca plan onaylandıktan sonra yapılabilir. Mevcut durum: {durum}. "
              "Hiçbir değişiklik yapılmadı.")
        return
    is_durumu.gecis(kayit, "uygulandi", "ajan", "uygulama tamamlandı")
    is_durumu.is_kaydet(proje, kayit)
    print("Durum: uygulandi. Sıradaki adım, bağımsız kontrolcünün (aec:dogrulayici) çalıştırılmasıdır.")


def _iptal(a) -> None:
    proje = Path(a.proje)
    kayit = is_durumu.is_yukle(proje, a.is_id)
    is_durumu.gecis(kayit, "iptal", "ajan", a.gerekce)
    is_durumu.is_kaydet(proje, kayit)
    print("İş iptal edildi.")


def _proje_ekle(a) -> None:
    proje = Path(a.proje)
    yasak = _yasak_hedef(proje)
    if yasak:
        print(yasak)
        return
    yol = proje / ".aec" / "proje.md"
    yol.parent.mkdir(parents=True, exist_ok=True)
    mevcut = yol.read_text(encoding="utf-8") if yol.is_file() else "# Proje bilgileri\n"
    if mevcut and not mevcut.endswith("\n"):
        mevcut += "\n"
    metin = " ".join(a.metin.split())
    if PROJE_EK_BASLIK not in mevcut.splitlines():
        mevcut += f"\n{PROJE_EK_BASLIK}\n\n"
    _yaz_metin(yol, mevcut + f"- {metin}\n")
    print("Bilgi proje.md dosyasına eklendi.")


_KOMUTLAR = {"yeni": _yeni, "olcut": _olcut, "tarif": _asama, "plan": _asama, "gorevler": _asama,
             "durum": _durum, "devam": _devam, "uygulandi": _uygulandi, "iptal": _iptal, "proje-ekle": _proje_ekle}


def main(argv: "list[str] | None" = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass
    try:
        a = _parser().parse_args(argv)
    except SystemExit as cikis:
        if cikis.code not in (0, None):
            print("✗ Komut tanınmadı ya da eksik. Geçerli komutlar: yeni, olcut, tarif, plan, gorevler, durum, devam, uygulandi, iptal, proje-ekle. "
                  "Onay ve kabul yalnızca kişinin kendi mesajıyla verilir; bu araçla verilemez.")
        return 0
    try:
        _KOMUTLAR[a.komut](a)
    except (ValueError, KeyError, TypeError) as hata:
        iletisi = str(hata)
        print(iletisi if iletisi.startswith("✗") else
              "✗ İş kaydı okunamadı ya da bozuk. Kayıt dosyasını kontrol ediniz; hiçbir değişiklik yapılmadı.")
    except OSError as hata:
        print(f"✗ Dosya işlemi yapılamadı ({hata.__class__.__name__}). Proje klasörüne yazma izni olup olmadığını kontrol ediniz.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

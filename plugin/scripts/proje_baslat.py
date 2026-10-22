"""Writes the project's CLAUDE.md block and .aec/proje.md for /aec:proje-baslat; standard library only."""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ALANLAR = ("proje_adi", "proje_tipi", "revit_merkez", "revit_kopya", "birim", "katlar", "orijin", "katman_standardi")
ETIKETLER = {
    "proje_adi": "Proje adı",
    "proje_tipi": "Proje tipi",
    "revit_merkez": "Revit merkez model",
    "revit_kopya": "Revit kopya model",
    "birim": "Birim",
    "katlar": "Katlar",
    "orijin": "Orijin",
    "katman_standardi": "Katman standardı",
}
BELIRTILMEDI = "belirtilmedi"
BASLANGIC = "<!-- aec:proje başlangıç -->"
BITIS = "<!-- aec:proje bitiş -->"
KODLAMA_HATASI = (
    "✗ CLAUDE.md okunamadı (Türkçe karakter kodlaması farklı); "
    "dosyayı UTF-8 olarak kaydedip tekrar deneyin. Hiçbir şey yazılmadı."
)
EV_KLASORU = (
    "✗ Proje klasörü olarak kullanıcı klasörünüz ({}) seçilmiş; buraya yazılan bilgi bütün projelere karışır. "
    "Claude'u projenin klasöründe açıp tekrar deneyin. Hiçbir şey yazılmadı."
)
SURUCU_KOKU = (
    "✗ Proje klasörü olarak bir sürücünün kökü ({}) seçilmiş. "
    "Claude'u projenin klasöründe açıp tekrar deneyin. Hiçbir şey yazılmadı."
)


def _deger(cevap: "dict[str, str]", alan: str) -> str:
    text = str(cevap.get(alan) or "").replace("<!--", "").replace("-->", "")
    return " ".join(text.split()) or BELIRTILMEDI


def _proje_md(cevap: "dict[str, str]") -> str:
    satirlar = ["# Proje bilgileri", ""]
    satirlar += [f"- **{ETIKETLER[a]}:** {_deger(cevap, a)}" for a in ALANLAR]
    return "\n".join(satirlar) + "\n"


def _blok(cevap: "dict[str, str]") -> str:
    return "\n".join([
        BASLANGIC,
        "Bu proje aec ile çalışır; proje bilgileri .aec/proje.md dosyasında.",
        f"Revit'e yalnızca kopya modelde yaz: {_deger(cevap, 'revit_kopya')}.",
        f"Birim: {_deger(cevap, 'birim')}.",
        BITIS,
    ]) + "\n"


def _yaz_metin(yol: Path, metin: str) -> None:
    """Atomic write: temp file in the same folder, then os.replace."""
    fd, gecici = tempfile.mkstemp(dir=yol.parent, prefix=yol.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(metin.encode("utf-8"))
        os.replace(gecici, yol)
    except BaseException:
        try:
            os.unlink(gecici)
        except OSError:
            pass
        raise


def _blok_yeri(mevcut: str) -> "tuple[int, int] | None":
    """Span of the first complete block; a start marker with no end marker after it is user text."""
    son = mevcut.find(BITIS)
    while son >= 0:
        bas = mevcut.rfind(BASLANGIC, 0, son)
        if bas >= 0:
            son += len(BITIS)
            if mevcut[son:son + 2] == "\r\n":
                son += 2
            elif mevcut[son:son + 1] == "\n":
                son += 1
            return bas, son
        son = mevcut.find(BITIS, son + len(BITIS))
    return None


def _yeni_claude_md(mevcut: str, blok: str) -> str:
    yer = _blok_yeri(mevcut)
    if yer:
        return mevcut[:yer[0]] + blok + mevcut[yer[1]:]
    if not mevcut:
        return blok
    if mevcut.endswith(("\n\n", "\r\n\r\n")):
        ayrac = ""
    elif mevcut.endswith("\n"):
        ayrac = "\n"
    else:
        ayrac = "\n\n"
    return mevcut + ayrac + blok


def _yasak_hedef(proje_dir: Path) -> "str | None":
    """Home folder and drive roots are never a project: a CLAUDE.md there reaches every session below it."""
    try:
        hedef = proje_dir.resolve()
    except OSError:
        hedef = proje_dir.absolute()
    if hedef.parent == hedef:
        return SURUCU_KOKU.format(hedef)
    try:
        ev = Path.home().resolve()
    except (OSError, RuntimeError):
        return None
    return EV_KLASORU.format(hedef) if hedef == ev else None


def yaz(proje_dir: Path, cevap: "dict[str, str]") -> "list[str]":
    proje_dir = Path(proje_dir)
    yasak = _yasak_hedef(proje_dir)
    if yasak:
        return [yasak]
    claude_md = proje_dir / "CLAUDE.md"
    try:  # read first: a file we cannot decode must leave no half-done state
        mevcut = claude_md.read_bytes().decode("utf-8") if claude_md.is_file() else ""
    except UnicodeDecodeError:
        return [KODLAMA_HATASI]
    mesajlar = []
    aec = proje_dir / ".aec"
    aec.mkdir(parents=True, exist_ok=True)
    proje_md = aec / "proje.md"
    if proje_md.exists():
        mesajlar.append(f"{proje_md.as_posix()} zaten var, değiştirilmedi.")
    else:
        _yaz_metin(proje_md, _proje_md(cevap))
        mesajlar.append(f"{proje_md.as_posix()} yazıldı.")
    _yaz_metin(claude_md, _yeni_claude_md(mevcut, _blok(cevap)))
    mesajlar.append(f"{claude_md.as_posix()} içindeki aec bloğu güncellendi.")
    return mesajlar


def _oku_json(kaynak: str) -> "dict[str, str]":
    if kaynak == "-":
        ham = sys.stdin.buffer.read()
    else:
        ham = Path(kaynak).read_bytes()
    veri = json.loads(ham.decode("utf-8-sig"))
    if not isinstance(veri, dict):
        raise ValueError("JSON bir nesne olmalı")
    return veri


def main(argv: "list[str] | None" = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--proje", required=True)
    parser.add_argument("--json", required=True, dest="json_kaynak")
    args = parser.parse_args(argv)
    try:
        cevap = _oku_json(args.json_kaynak)
    except (OSError, ValueError):  # UnicodeDecodeError is a ValueError
        print("✗ Cevaplar okunamadı; hiçbir dosya yazılmadı. Soruları yeniden yanıtlayın.")
        return 0
    try:
        mesajlar = yaz(Path(args.proje), cevap)
    except OSError as hata:
        print(f"✗ Dosyalar yazılamadı ({hata.__class__.__name__}); proje klasörüne yazma izni var mı kontrol edin.")
        return 0
    for mesaj in mesajlar:
        print(mesaj)
    return 0


if __name__ == "__main__":
    sys.exit(main())

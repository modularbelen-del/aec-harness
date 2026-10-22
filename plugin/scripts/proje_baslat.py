"""Writes the project's CLAUDE.md block and .aec/proje.md for /aec:proje-baslat; standard library only."""
import argparse
import json
import sys
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


def _deger(cevap: "dict[str, str]", alan: str) -> str:
    text = " ".join(str(cevap.get(alan) or "").split())
    return text or BELIRTILMEDI


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
    yol.write_bytes(metin.encode("utf-8"))


def _claude_md(yol: Path, blok: str) -> None:
    mevcut = yol.read_bytes().decode("utf-8") if yol.is_file() else ""
    bas = mevcut.find(BASLANGIC)
    son = mevcut.find(BITIS, bas) if bas >= 0 else -1
    if bas >= 0 and son >= 0:
        son += len(BITIS)
        if mevcut[son:son + 2] == "\r\n":
            son += 2
        elif mevcut[son:son + 1] == "\n":
            son += 1
        yeni = mevcut[:bas] + blok + mevcut[son:]
    elif not mevcut:
        yeni = blok
    else:
        if mevcut.endswith(("\n\n", "\r\n\r\n")):
            ayrac = ""
        elif mevcut.endswith("\n"):
            ayrac = "\n"
        else:
            ayrac = "\n\n"
        yeni = mevcut + ayrac + blok
    _yaz_metin(yol, yeni)


def yaz(proje_dir: Path, cevap: "dict[str, str]") -> "list[str]":
    proje_dir = Path(proje_dir)
    mesajlar = []
    aec = proje_dir / ".aec"
    aec.mkdir(parents=True, exist_ok=True)
    proje_md = aec / "proje.md"
    if proje_md.exists():
        mesajlar.append(f"{proje_md.as_posix()} zaten var, değiştirilmedi.")
    else:
        _yaz_metin(proje_md, _proje_md(cevap))
        mesajlar.append(f"{proje_md.as_posix()} yazıldı.")
    claude_md = proje_dir / "CLAUDE.md"
    _claude_md(claude_md, _blok(cevap))
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
    except (OSError, ValueError):
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

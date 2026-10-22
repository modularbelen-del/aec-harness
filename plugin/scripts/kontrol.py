"""Setup report for /aec:kontrol-et: one ✓ or ✗ line per item. Read-only; standard library only."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from programlar import durum_satiri, running_programs

MARKETPLACE = "aec-office"
UV_YOK = "✗ uv: kurulu değil → BASLA.md'deki tek satırlık kurulum komutunu yeniden çalıştırınız"
GUNCELLEME_YOK = (
    "✗ Otomatik güncelleme: kapalı ya da durumu belirlenemedi → terminalde /plugin > Marketplaces > aec-office > "
    "Enable auto-update; Cowork'te Customize > Plugins > \"Sync automatically\""
)
PROJE_BASLAT = "/aec:proje-baslat"


def _otomatik_guncelleme(*dizinler: Path) -> bool:
    for dizin in dizinler:
        try:
            data = json.loads((dizin / ".claude" / "settings.json").read_text(encoding="utf-8-sig"))
            if data["extraKnownMarketplaces"][MARKETPLACE]["autoUpdate"] is True:
                return True
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return False


def _var_yok(ok: bool, ad: str, var: str) -> str:
    return f"✓ {ad}: {var}" if ok else f"✗ {ad}: bulunamadı → {PROJE_BASLAT}"


def satirlar(proje_dir: Path, ev_dir: Path, acik: "set[str] | None", uv_surumu: "str | None") -> "list[str]":
    proje_dir, ev_dir = Path(proje_dir), Path(ev_dir)
    out = [f"✓ uv: {uv_surumu}" if uv_surumu else UV_YOK]
    out.append("✓ Otomatik güncelleme: açık" if _otomatik_guncelleme(proje_dir, ev_dir) else GUNCELLEME_YOK)
    out.append(_var_yok((proje_dir / "CLAUDE.md").is_file(), "Proje CLAUDE.md", "mevcut"))
    out.append(_var_yok((proje_dir / ".aec" / "proje.md").is_file(), "Proje bilgisi (.aec/proje.md)", "mevcut"))
    durum = durum_satiri(acik)
    out.append(f"✓ Açık programlar: {durum.split(': ', 1)[1]}" if durum else "✗ Açık programlar: kontrol edilemedi")
    return out


def _uv_surumu() -> "str | None":
    uv = shutil.which("uv")
    if not uv:
        return None
    try:
        done = subprocess.run([uv, "--version"], capture_output=True, timeout=10)
        text = done.stdout.decode("utf-8", errors="replace").strip()
    except Exception:
        return None
    if done.returncode != 0 or not text:
        return None
    parts = text.split()
    return parts[1] if len(parts) > 1 else text


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--proje", default=os.getcwd())
    args = parser.parse_args()
    for line in satirlar(Path(args.proje), Path.home(), running_programs(), _uv_surumu()):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

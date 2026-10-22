"""PreToolUse hook: code-level locks.

- Revit write tools run only when this session's active job has an approved plan (sync never, save only after
  acceptance); without the UserPromptSubmit heartbeat the decision softens to "ask".
- Nobody writes into .aec/isler/ with Write/Edit/NotebookEdit.
- The verifier agent may only be given the job folder path.

Standard library only. On any error or when allowed it prints nothing, with one exception: when a sibling module
fails to load, a Revit write is denied (fail closed) instead of silently allowed.
"""
import json
import os
import pathlib
import re
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))

REVIT_YAZMA = re.compile(r"^mcp__.*revit.*__(execute_revit_code|place_family|close_document|save_document|sync_with_central)$", re.IGNORECASE)
NEDEN_BILESEN = ("Eklenti bileşeni yüklenemedi; Revit'e yazma güvenlik için durduruldu. "
                 "/aec:kontrol-et çalıştırınız.")

try:  # minimal import surface; the prompt-side modules (user_prompt, onay, onkapi) are deliberately not imported
    import is_durumu  # noqa: E402
    import yol as yol_modulu  # noqa: E402
    from yol import mutlak as _mutlak  # noqa: E402
    BILESENLER_YUKLENDI = True
except Exception:
    BILESENLER_YUKLENDI = False

YAZMA_ARACLARI = frozenset({"Write", "Edit", "NotebookEdit"})
AJAN_ARACLARI = frozenset({"Agent", "Task"})
DOGRULAYICI = frozenset({"aec:dogrulayici", "dogrulayici"})
YAZMA_DURUMLARI = frozenset({"plan-onaylandi", "uygulandi"})

NEDEN_IS_YOK = ("Revit'e yazma işlemi için onaylanmış bir iş kaydı bulunmamaktadır. "
                "İstek karşılama akışı ile iş açılmalı ve plan onaylatılmalıdır.")
NEDEN_ESITLEME = "Merkez modelle eşitleme yalnızca kişi tarafından yapılır."
NEDEN_KAYDETME = "Kaydetme işlemi, iş kişi tarafından kabul edildikten sonra yapılabilir."
NEDEN_ISLER = "İş kayıtları yalnızca iş kaydı aracı ve sistem tarafından güncellenir."
NEDEN_DOGRULAYICI = "Kontrolcüye yalnızca iş klasörünün yolu verilmelidir."
NEDEN_OKUNAMADI = ("İş kaydı okunamadı; Revit'e yazma işlemi güvenlik nedeniyle durdurulmuştur. Kayıt dosyası "
                   "elle düzenlenmemeli, durum ofisteki sistem sorumlusuna iletilmelidir.")
NEDEN_YUMUSAK = "Onay kaydı bu oturumda doğrulanamadı. Bu yazma işlemini onaylıyor musunuz?"


def _cikti(karar: str, neden: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": karar,
                                   "permissionDecisionReason": neden}}


def _isler_icinde(yol: str, proje: pathlib.Path) -> bool:
    # Windows aliases: trailing dots/spaces and NTFS stream suffixes (".aec::$INDEX_ALLOCATION") name the same entry
    parcalar = [p.split(":")[0].rstrip(". ").lower() for p in _mutlak(yol, proje).split("/")]
    return any(a == ".aec" and b == "isler" for a, b in zip(parcalar, parcalar[1:]))


def _revit_karari(arac: str, arac_girdisi, oturum: str, proje: pathlib.Path, state_dir: pathlib.Path):
    """Fails closed: an unreadable or malformed job record denies the write."""
    try:
        eylem = arac.rsplit("__", 1)[-1].lower()
        if eylem == "close_document" and isinstance(arac_girdisi, dict) and arac_girdisi.get("save"):
            eylem = "save_document"  # closing with save=True saves the model
        return _revit_karari_ic(eylem, oturum, proje, state_dir)
    except Exception:
        return _cikti("deny", NEDEN_OKUNAMADI)


def _revit_karari_ic(eylem: str, oturum: str, proje: pathlib.Path, state_dir: pathlib.Path):
    if eylem == "sync_with_central":
        return _cikti("deny", NEDEN_ESITLEME)
    if not yol_modulu.calisti_yolu(state_dir, oturum).exists():
        return _cikti("ask", NEDEN_YUMUSAK)
    kayit = is_durumu.aktif_is(proje, oturum)
    if kayit is None:
        durum = None
    elif isinstance(kayit, dict) and isinstance(kayit.get("durum"), str):
        durum = kayit["durum"]
    else:
        return _cikti("deny", NEDEN_OKUNAMADI)
    if eylem == "save_document":
        return None if durum == "kabul-edildi" else _cikti("deny", NEDEN_KAYDETME)
    if eylem == "close_document" and durum == "kabul-edildi":
        return None  # closing an accepted model without saving changes nothing
    if durum in YAZMA_DURUMLARI:
        return None
    return _cikti("deny", NEDEN_IS_YOK)


def _dogrulayici_karari(arac_girdisi: dict, oturum: str, proje: pathlib.Path, state_dir: pathlib.Path):
    tur = arac_girdisi.get("subagent_type")
    if not isinstance(tur, str) or tur.strip().casefold() not in DOGRULAYICI:
        return None
    prompt = arac_girdisi.get("prompt")
    kayit = is_durumu.aktif_is(proje, oturum)
    if not isinstance(prompt, str) or not isinstance(kayit, dict) or kayit.get("durum") != "uygulandi":
        return _cikti("deny", NEDEN_DOGRULAYICI)
    yol = prompt.strip().strip("\"'`").strip()
    if not yol or "\n" in yol:
        return _cikti("deny", NEDEN_DOGRULAYICI)
    beklenen = _mutlak(str(pathlib.Path(proje) / is_durumu.ISLER / str(kayit.get("id"))), proje)
    if _mutlak(yol, proje) != beklenen:
        return _cikti("deny", NEDEN_DOGRULAYICI)
    yol_modulu.isaret_yaz(state_dir, oturum, str(kayit.get("id")))  # the Stop lock waits for this verifier
    return None


def karar(girdi, proje: pathlib.Path, state_dir: pathlib.Path):
    """Returns the PreToolUse output dict for deny/ask, or None to allow. Never raises."""
    try:
        if not isinstance(girdi, dict):
            return None
        arac = girdi.get("tool_name")
        arac_girdisi = girdi.get("tool_input")
        if not isinstance(arac, str):
            return None
        oturum = str(girdi.get("session_id") or "")
        if REVIT_YAZMA.match(arac):
            return _revit_karari(arac, arac_girdisi, oturum, pathlib.Path(proje), pathlib.Path(state_dir))
        if not isinstance(arac_girdisi, dict):
            return None
        if arac in YAZMA_ARACLARI:
            yol = arac_girdisi.get("file_path") or arac_girdisi.get("notebook_path")
            if isinstance(yol, str) and yol and _isler_icinde(yol, pathlib.Path(proje)):
                return _cikti("deny", NEDEN_ISLER)
            return None
        if arac in AJAN_ARACLARI:
            return _dogrulayici_karari(arac_girdisi, oturum, pathlib.Path(proje), pathlib.Path(state_dir))
        return None
    except Exception:  # fail open
        return None


def _bilesen_karari(girdi):
    """Used when a sibling module failed to load: deny Revit writes, stay silent for everything else."""
    arac = girdi.get("tool_name") if isinstance(girdi, dict) else None
    return _cikti("deny", NEDEN_BILESEN) if isinstance(arac, str) and REVIT_YAZMA.match(arac) else None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        metin = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8", "replace")
        girdi = json.loads(metin)
        if not BILESENLER_YUKLENDI:
            sonuc = _bilesen_karari(girdi)
        else:
            proje = (os.environ.get("CLAUDE_PROJECT_DIR") or (girdi.get("cwd") if isinstance(girdi, dict) else None)
                     or os.getcwd())
            sonuc = karar(girdi, pathlib.Path(proje), yol_modulu.durum_klasoru())
        if sonuc:
            sys.stdout.write(json.dumps(sonuc, ensure_ascii=False))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

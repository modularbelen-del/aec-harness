"""SubagentStop hook: records the independent verifier's report (written by code, not by the main agent) and moves the
job from 'uygulandi' to 'kabul-bekliyor' with a 'sonuc'.

The verifier is trusted only when its transcript holds exactly one genuine user message and that message is the job
folder path; a continued conversation (SendMessage) is recorded as 'DOĞRULANAMADI'. The transcript is JSONL whose line
format is not formally documented, so it is parsed defensively. Standard library only; never raises, prints nothing.
"""
import json
import os
import pathlib
import re
import sys

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))

import is_durumu  # noqa: E402
from yol import mutlak as _mutlak  # noqa: E402  (same path normalization as the verifier-prompt lock)
from proje_baslat import _yaz_metin  # noqa: E402

KAYNAK = "hook-subagent"
AJANLAR = frozenset({"aec:dogrulayici", "dogrulayici"})
SONUC_SATIRI = re.compile(r"^\s*SONU[ÇC]:\s*(GEÇTİ|GECTI|KALDI|DOĞRULANAMADI|DOGRULANAMADI)\s*$", re.MULTILINE)
SONUC_ADI = {"GEÇTİ": "GEÇTİ", "GECTI": "GEÇTİ", "KALDI": "KALDI",
             "DOĞRULANAMADI": "DOĞRULANAMADI", "DOGRULANAMADI": "DOĞRULANAMADI"}
DOGRULANAMADI = "DOĞRULANAMADI"
NOT_YONERGE = "kontrolcü yönergesi doğrulanamadı"
NL = chr(10)


def _metinler(icerik) -> str:
    """Text of a message content (string or list of blocks); tool_result and other blocks are not text."""
    if isinstance(icerik, str):
        return icerik
    if isinstance(icerik, list):
        return NL.join(b["text"] for b in icerik
                       if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str))
    return ""


def _rapor(icerik) -> str:
    """Last report text of an assistant message: a text block or the message of a SubagentHandback tool call."""
    if isinstance(icerik, str):
        return icerik.strip()
    son = ""
    for b in icerik if isinstance(icerik, list) else []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text" and isinstance(b.get("text"), str):
            son = b["text"].strip() or son
        elif b.get("type") == "tool_use" and b.get("name") == "SubagentHandback" and isinstance(b.get("input"), dict):
            mesaj = b["input"].get("message")
            son = mesaj.strip() if isinstance(mesaj, str) and mesaj.strip() else son
    return son


def _kaynak_var(origin) -> bool:
    """True when a line comes from somewhere other than the harness itself (e.g. origin kind 'coordinator')."""
    if isinstance(origin, dict):
        return bool(origin.get("kind"))
    return bool(origin)


def _transcript(yol) -> "tuple[str, bool, str]":
    """(genuine prompt, trusted, text of the last assistant message that has text).

    The genuine prompt is the first non-meta user text line. The transcript is not trusted when another user text line
    has a different promptId or a non-empty origin, or when a second non-meta user text line exists. Harness
    reminders (isMeta, same promptId, no origin), tool_result-only lines and other line types are ignored.
    """
    kullanici, asistan = [], ""
    for satir in pathlib.Path(yol).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            kayit = json.loads(satir)
        except ValueError:
            continue
        ileti = kayit.get("message") if isinstance(kayit, dict) else None
        if not isinstance(ileti, dict):
            continue
        tur = kayit.get("type") or ileti.get("role")
        if tur == "assistant":
            asistan = _rapor(ileti.get("content")) or asistan
            continue
        metin = _metinler(ileti.get("content")).strip()
        if tur == "user" and metin:
            kullanici.append((metin, bool(kayit.get("isMeta")), kayit.get("promptId"), kayit.get("origin")))
    gercek = next((k for k in kullanici if not k[1]), None)
    if gercek is None:
        return "", False, asistan
    pid = gercek[2]
    guvenilir = True
    for k in kullanici:
        if _kaynak_var(k[3]) or (pid is not None and k[2] != pid):
            guvenilir = False
    if sum(1 for k in kullanici if not k[1]) != 1:
        guvenilir = False
    return gercek[0], guvenilir, asistan


def _is_kimligi(metin: str, proje: pathlib.Path) -> "str | None":
    """Job id when the text (minus quotes/backticks) is exactly a job folder directly under <proje>/.aec/isler."""
    yol = metin.strip().strip("\"'`").strip()
    if not yol or NL in yol:
        return None
    mutlak = _mutlak(yol, proje)
    ust, _, ad = mutlak.rpartition("/")
    if ust != _mutlak(str(pathlib.Path(proje) / is_durumu.ISLER), proje) or not ad:
        return None
    return ad


def _sonuc(rapor: str) -> str:
    bulunan = SONUC_SATIRI.findall(rapor)
    return SONUC_ADI[bulunan[-1]] if bulunan else DOGRULANAMADI


def isle(girdi, proje: pathlib.Path) -> None:
    try:
        if not isinstance(girdi, dict):
            return
        tur = girdi.get("agent_type")
        if not isinstance(tur, str) or tur.strip().casefold() not in AJANLAR:
            return
        proje = pathlib.Path(proje)
        istem, guvenilir, rapor = _transcript(girdi["agent_transcript_path"])
        son_mesaj = girdi.get("last_assistant_message")
        if not rapor and isinstance(son_mesaj, str):
            rapor = son_mesaj.strip()
        if not istem or not rapor:
            return
        is_id = _is_kimligi(istem, proje)
        if not is_id:
            return
        kayit = is_durumu.is_yukle(proje, is_id)
        if not isinstance(kayit, dict) or kayit.get("durum") != "uygulandi":
            return
        sonuc = _sonuc(rapor) if guvenilir else DOGRULANAMADI
        not_ = f"kontrol sonucu: {sonuc}" if guvenilir else f"{NOT_YONERGE}; kontrol sonucu: {sonuc}"
        baslik = f"# Kontrol raporu — {is_id}{NL}{NL}Zaman: {is_durumu._zaman()}{NL}Sonuç: {sonuc}{NL}{NL}"
        _yaz_metin(is_durumu._is_klasoru(proje, is_id) / "dogrulama.md", baslik + rapor.rstrip() + NL)
        kayit["sonuc"] = sonuc
        is_durumu.gecis(kayit, "kabul-bekliyor", KAYNAK, not_)
        is_durumu.is_kaydet(proje, kayit)
    except Exception:
        pass


def main() -> int:
    try:
        metin = "" if sys.stdin is None or sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8", "replace")
        girdi = json.loads(metin)
        proje = os.environ.get("CLAUDE_PROJECT_DIR") or (girdi.get("cwd") if isinstance(girdi, dict) else None) or os.getcwd()
        isle(girdi, pathlib.Path(proje))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

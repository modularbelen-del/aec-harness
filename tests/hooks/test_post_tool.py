import is_durumu
import post_tool

REVIT = "mcp__revit__execute_revit_code"
SID = "s1"


def _is(proje, durum):
    kayit = is_durumu.yeni_is(proje, "revit-modelleme", "Deneme", False)
    kayit["durum"] = durum
    is_durumu.is_kaydet(proje, kayit)
    is_durumu.aktif_bagla(proje, SID, kayit["id"])
    return kayit["id"]


def test_binds_new_job_to_session(tmp_path):
    kayit = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Deneme", False)
    girdi = {"session_id": SID, "tool_name": "Bash",
             "tool_input": {"command": 'python "x/is_kaydi.py" yeni --kart revit-modelleme --baslik "Deneme"'},
             "tool_response": {"stdout": f"Açıldı\nIS: {kayit['id']}\n", "stderr": ""}}
    post_tool.isle(girdi, tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID)["id"] == kayit["id"]
    assert (tmp_path / ".aec" / "isler" / f"aktif-{SID}.json").is_file()


def test_bind_ignores_unknown_id_and_other_commands(tmp_path):
    post_tool.isle({"session_id": SID, "tool_name": "Bash", "tool_input": {"command": "is_kaydi.py yeni"},
                    "tool_response": "IS: yok-boyle-is"}, tmp_path)
    post_tool.isle({"session_id": SID, "tool_name": "Bash", "tool_input": {"command": "ls"},
                    "tool_response": {"stdout": "IS: x"}}, tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID) is None


def test_revit_write_marks_applied(tmp_path):
    is_id = _is(tmp_path, "plan-onaylandi")
    post_tool.isle({"session_id": SID, "tool_name": REVIT, "tool_input": {}, "tool_response": {"ok": True}}, tmp_path)
    kayit = is_durumu.is_yukle(tmp_path, is_id)
    assert kayit["durum"] == "uygulandi" and kayit["olaylar"][-1]["kaynak"] == "hook-post"
    post_tool.isle({"session_id": SID, "tool_name": REVIT, "tool_input": {}, "tool_response": [{"type": "text"}]}, tmp_path)
    assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "uygulandi"


def test_failed_write_does_not_advance(tmp_path):
    is_id = _is(tmp_path, "plan-onaylandi")
    for yanit in ({"isError": True}, {"is_error": True}, {"error": "x"}):
        post_tool.isle({"session_id": SID, "tool_name": REVIT, "tool_input": {}, "tool_response": yanit}, tmp_path)
        assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "plan-onaylandi"


def test_bind_ignores_non_fresh_job(tmp_path):
    kayit = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Eski", False)
    kayit["durum"] = "plan-onaylandi"
    is_durumu.is_kaydet(tmp_path, kayit)
    post_tool.isle({"session_id": SID, "tool_name": "Bash", "tool_input": {"command": "is_kaydi.py yeni"},
                    "tool_response": {"stdout": f"IS: {kayit['id']}"}}, tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID) is None


def test_bind_picks_fresh_job_among_many_lines(tmp_path):
    eski = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Eski", False)
    eski["durum"] = "plan-onaylandi"
    is_durumu.is_kaydet(tmp_path, eski)
    yeni = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Yeni", False)
    cikti = f"IS: {eski['id']}\ndurum: plan-onaylandi\nIS: {yeni['id']}\n"
    post_tool.isle({"session_id": SID, "tool_name": "Bash",
                    "tool_input": {"command": "is_kaydi.py durum --is X && is_kaydi.py yeni --kart a"},
                    "tool_response": {"stdout": cikti}}, tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID)["id"] == yeni["id"]


def test_powershell_binds(tmp_path):
    kayit = is_durumu.yeni_is(tmp_path, "revit-modelleme", "Deneme", False)
    post_tool.isle({"session_id": SID, "tool_name": "PowerShell", "tool_input": {"command": "python is_kaydi.py yeni"},
                    "tool_response": {"stdout": f"IS: {kayit['id']}"}}, tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID)["id"] == kayit["id"]


def test_plain_text_errors_do_not_advance(tmp_path):
    is_id = _is(tmp_path, "plan-onaylandi")
    hatalar = ("Error: bir şey", "=== ERROR DETAILS ===\nx", "Kod çalıştı. Error during code execution: x",
               [{"type": "text", "text": "  Error: x"}], {"content": [{"type": "text", "text": "Error: x"}]})
    for yanit in hatalar:
        post_tool.isle({"session_id": SID, "tool_name": REVIT, "tool_input": {}, "tool_response": yanit}, tmp_path)
        assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "plan-onaylandi", yanit
    post_tool.isle({"session_id": SID, "tool_name": "mcp__Revit__place_family", "tool_input": {},
                    "tool_response": {"content": [{"type": "text", "text": "Tamam"}]}}, tmp_path)
    assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "uygulandi"


def _eski_is(proje, durum, oturum="eski-oturum"):
    kayit = is_durumu.yeni_is(proje, "revit-modelleme", "Eski", False)
    kayit["durum"] = durum
    is_durumu.is_kaydet(proje, kayit)
    is_durumu.aktif_bagla(proje, oturum, kayit["id"])
    return kayit["id"]


def _devam(is_id, arac="Bash", komut=None, sid=SID):
    return {"session_id": sid, "tool_name": arac,
            "tool_input": {"command": komut or f'uv run python "x/is_kaydi.py" devam --proje "p" --is {is_id}'},
            "tool_response": {"stdout": f"DEVAM: {is_id}\nDurum: x\n", "stderr": ""}}


def test_continue_binds_open_job_from_earlier_session(tmp_path):
    for durum in ("gorusme", "onay-bekliyor:tarif", "onay-bekliyor:plan", "onaylandi:plan", "uygulandi",
                  "kabul-bekliyor", "reddedildi"):
        proje = tmp_path / durum.replace(":", "-")
        is_id = _eski_is(proje, durum)
        post_tool.isle(_devam(is_id), proje)
        kayit = is_durumu.aktif_is(proje, SID)
        assert kayit["id"] == is_id and kayit["durum"] == durum, durum
    proje = tmp_path / "ps"
    is_id = _eski_is(proje, "kabul-bekliyor")
    post_tool.isle(_devam(is_id, arac="PowerShell"), proje)
    assert is_durumu.aktif_is(proje, SID)["id"] == is_id


def test_continue_refuses_closed_jobs_and_foreign_output(tmp_path):
    for durum in ("kabul-edildi", "iptal"):
        proje = tmp_path / durum
        is_id = _eski_is(proje, durum)
        post_tool.isle(_devam(is_id), proje)
        assert is_durumu.aktif_is(proje, SID) is None, durum
    proje = tmp_path / "diger"
    is_id = _eski_is(proje, "onay-bekliyor:plan")
    for komut in (f"echo DEVAM: {is_id}", f"is_kaydi.py durum --is {is_id}", "is_kaydi.py yeni --kart x"):
        post_tool.isle(_devam(is_id, komut=komut), proje)
        assert is_durumu.aktif_is(proje, SID) is None, komut
    post_tool.isle({**_devam(is_id), "tool_response": {"stdout": f"✗ DEVAM: {is_id}"}}, proje)
    post_tool.isle(_devam("yok-boyle-is"), proje)
    assert is_durumu.aktif_is(proje, SID) is None


def test_continue_asks_again_for_plan_approved_elsewhere(tmp_path):
    is_id = _eski_is(tmp_path, "plan-onaylandi")
    post_tool.isle(_devam(is_id), tmp_path)
    kayit = is_durumu.aktif_is(tmp_path, SID)
    assert kayit["id"] == is_id and kayit["durum"] == "onay-bekliyor:plan"
    olay = kayit["olaylar"][-1]
    assert (olay["eski"], olay["yeni"], olay["kaynak"]) == ("plan-onaylandi", "onay-bekliyor:plan", "hook-post")
    assert olay["not"] == "oturum değişti; onay yeniden istenecek"


def test_continue_takes_the_job_over_from_other_sessions(tmp_path):
    is_id = _eski_is(tmp_path, "onay-bekliyor:plan", oturum="eski-oturum")
    diger = is_durumu.yeni_is(tmp_path, "render", "Diger", False)
    is_durumu.aktif_bagla(tmp_path, "ucuncu-oturum", diger["id"])
    post_tool.isle(_devam(is_id), tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID)["id"] == is_id
    assert is_durumu.aktif_is(tmp_path, "eski-oturum") is None  # an "evet" there no longer counts for this job
    assert is_durumu.aktif_is(tmp_path, "ucuncu-oturum")["id"] == diger["id"]


def test_continue_in_own_session_keeps_its_approval(tmp_path):
    is_id = _eski_is(tmp_path, "plan-onaylandi", oturum=SID)
    post_tool.isle(_devam(is_id), tmp_path)
    assert is_durumu.aktif_is(tmp_path, SID)["durum"] == "plan-onaylandi"


def test_read_tool_and_bad_input_do_nothing(tmp_path):
    is_id = _is(tmp_path, "plan-onaylandi")
    post_tool.isle({"session_id": SID, "tool_name": "mcp__revit__get_revit_status", "tool_response": {}}, tmp_path)
    for bozuk in (None, "x", {}, {"tool_name": 4}):
        post_tool.isle(bozuk, tmp_path)
    assert is_durumu.is_yukle(tmp_path, is_id)["durum"] == "plan-onaylandi"

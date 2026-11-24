"""Unit tests on synthetic data: no network."""

import json

import pytest

from cli_anything.phorme.core import export, review
from cli_anything.phorme.core.session import Session
from cli_anything.phorme.phorme_cli import parse_exercise
from cli_anything.phorme.utils import phorme_backend


def tool(name, ro=True, destructive=False, auth="noauth", props=None, required=(), desc="Reads a thing.", out=True, idem=None):
    t = {"name": name, "title": name, "description": desc,
         "annotations": {"readOnlyHint": ro, "destructiveHint": destructive, **({"idempotentHint": idem} if idem else {})},
         "inputSchema": {"type": "object", "properties": props or {}, "required": list(required)},
         "_meta": {"securitySchemes": [{"type": a} for a in auth.split(",")]}}
    if out:
        t["outputSchema"] = {"type": "object"}
    return t


INIT = {"serverInfo": {"name": "x", "title": "X", "version": "2.0.0"}, "instructions": "Use find_thing."}


def rules(findings):
    return {(f.rule, f.tool) for f in findings}


def test_parse_exercise():
    assert parse_exercise("Back squat:4x6@225 lb") == {"name": "Back squat", "sets": 4, "reps": "6", "load": "225 lb"}
    assert parse_exercise("Plank:3x40 sec") == {"name": "Plank", "sets": 3, "reps": "40 sec"}
    with pytest.raises(ValueError):
        parse_exercise("Back squat")
    with pytest.raises(ValueError):
        parse_exercise("Row:threex8")


def test_review_flags_unknown_instruction_tool_and_drift():
    f = review.review([tool("other_thing")], INIT, server_json={"version": "1.0.0"})
    assert ("instructions-unknown-tool", "find_thing") in rules(f)
    assert ("version-drift", "-") in rules(f)


def test_review_write_rules():
    ts = [tool("find_thing"),
          tool("drop_thing", ro=False, destructive=True, auth="oauth2"),
          tool("set_thing", ro=False, auth="oauth2", props={"confirmation": {"type": "boolean"}}),
          tool("bump_thing", ro=False, auth="oauth2"),
          tool("preview_thing", ro=False, auth="noauth")]
    r = rules(review.review(ts, INIT))
    assert ("destructive-without-confirmation", "drop_thing") in r
    assert ("write-without-confirmation", "bump_thing") in r
    assert ("write-without-confirmation", "preview_thing") not in r  # staging tools only stage
    assert ("write-without-account", "preview_thing") in r
    assert ("retry-may-duplicate", "set_thing") in r


def test_review_capability_ignores_do_not_use_sentences():
    ts = [tool("find_thing", desc="Finds plans. Do not use it for injury rehab, nutrition plans or meals.")]
    caps = {f.tool for f in review.review(ts, INIT) if f.rule == "missing-capability"}
    assert "nutrition" in caps
    ts.append(tool("fuel_my_week", desc="A week of meals sized to the training sessions."))
    caps = {f.tool for f in review.review(ts, INIT) if f.rule == "missing-capability"}
    assert "nutrition" not in caps


def test_review_sorted_by_severity():
    f = review.review([tool("x", out=False, desc="d" * 900)], INIT)
    sev = [review.SEVERITY[x.severity] for x in f]
    assert sev == sorted(sev, reverse=True)


def test_session_records_preview_and_undoes(tmp_path):
    s = Session(tmp_path / "s.json")
    s.record("preview_workout_import", {"a": 1}, {"structuredContent": {"preview_id": "p1"}})
    assert s.state["previews"]["preview_workout_import"] == "p1"
    assert json.loads((tmp_path / "s.json").read_text())["previews"]["preview_workout_import"] == "p1"
    assert s.undo() and s.state["previews"] == {}
    assert s.redo() and s.state["previews"]["preview_workout_import"] == "p1"


def test_export_refuses_overwrite(tmp_path):
    out = tmp_path / "r.md"
    export.render("# hi", str(out), "md")
    with pytest.raises(FileExistsError):
        export.render("# hi", str(out), "md")
    assert export.render({"a": 1}, str(out), "json", overwrite=True)["bytes"] > 0


def test_backend_parses_event_stream():
    body = 'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"ok":true}}\n\n'
    assert phorme_backend._parse(body, "text/event-stream")["result"] == {"ok": True}
    assert phorme_backend._parse('{"result":1}', "application/json") == {"result": 1}

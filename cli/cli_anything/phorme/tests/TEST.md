# cli-anything-phorme tests

## Part 1: plan

**Unit (`test_core.py`, synthetic data, no network):**
- `parse_exercise`: the `NAME:SETSxREPS[@LOAD]` spec, timed reps, and the errors for a missing dose or non-numeric sets.
- `review`: an instructions name that isn't served; server.json version drift; destructive and plain writes without
  confirmation; staging tools exempt from the confirmation rule; writes callable without an account; retries that can
  apply twice; a "Do not use it for …" sentence never counting as coverage; findings sorted by severity.
- `Session`: a preview id kept by tool; the JSON file written under lock; undo and redo.
- `export`: refuses to overwrite without `--overwrite`.
- Backend: an event-stream answer and a plain JSON answer both parse.

**E2E (`test_full_e2e.py`, the installed command against the live server):** only read-only and preview tools.
- `server info`: the server names itself phorme-training with a version.
- `tools list --auth noauth`: the public finders are served.
- `find build`: brains come back, each with a phor.me page.
- `train swap`: the first swaps keep the squat pattern.
- `train workout`: each exercise is matched to the library name, and the preview id is kept in the session.
- `review run --out`: the review runs on the live server and writes Markdown.
- `tools call` with an unknown tool fails loudly (exit 1, `{"error": ...}`).

**Realistic workflow:** a member's agent finds a build, previews a session from it, swaps a movement for the equipment on
hand, and keeps the preview id to save once the member is signed in.

**Not covered:** the member tools (`me ...`) and every save need a Phorme account token, and the coach tools
(`coaches ...`) wait for `meet_the_coaches` and `ask_coach` on the server.

## Part 2: results (2026-11-23, live server 1.18.0)

```
collecting ... collected 15 items

cli_anything/phorme/tests/test_core.py::test_parse_exercise PASSED       [  6%]
cli_anything/phorme/tests/test_core.py::test_review_flags_unknown_instruction_tool_and_drift PASSED [ 13%]
cli_anything/phorme/tests/test_core.py::test_review_write_rules PASSED   [ 20%]
cli_anything/phorme/tests/test_core.py::test_review_capability_ignores_do_not_use_sentences PASSED [ 26%]
cli_anything/phorme/tests/test_core.py::test_review_sorted_by_severity PASSED [ 33%]
cli_anything/phorme/tests/test_core.py::test_session_records_preview_and_undoes PASSED [ 40%]
cli_anything/phorme/tests/test_core.py::test_export_refuses_overwrite PASSED [ 46%]
cli_anything/phorme/tests/test_core.py::test_backend_parses_event_stream PASSED [ 53%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_server_info PASSED [ 60%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_tools_list_has_public_finders PASSED [ 66%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_find_build_returns_brains_with_pages PASSED [ 73%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_swap_keeps_the_pattern PASSED [ 80%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_workout_preview_is_remembered PASSED [ 86%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_review_runs_on_the_live_server PASSED [ 93%]
cli_anything/phorme/tests/test_full_e2e.py::TestCLISubprocess::test_unknown_tool_fails_loudly PASSED [100%]

============================== 15 passed in 4.20s ==============================
```

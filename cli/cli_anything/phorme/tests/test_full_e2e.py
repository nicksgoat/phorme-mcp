"""E2E: the installed command against the live Phorme Training server (read-only and preview tools only).

PHORME_MCP_URL points it at another server; CLI_ANYTHING_FORCE_INSTALLED=1 requires the installed command.
"""

import json
import os
import shutil
import subprocess
import sys

import pytest


def _resolve_cli(name: str) -> list[str]:
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] installed command: {path}")
        return [path]
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED") == "1":
        raise RuntimeError(f"{name} is not installed (pip install -e .)")
    print(f"[_resolve_cli] falling back to python -m cli_anything.phorme")
    return [sys.executable, "-m", "cli_anything.phorme"]


class TestCLISubprocess:
    CLI = _resolve_cli("cli-anything-phorme")

    def _run(self, *args, check=True, tmp_home=None):
        env = {**os.environ, **({"CLI_ANYTHING_PHORME_HOME": str(tmp_home)} if tmp_home else {})}
        r = subprocess.run(self.CLI + ["--json", *args], capture_output=True, text=True, timeout=120, env=env)
        if check:
            assert r.returncode == 0, r.stderr or r.stdout
        return r

    def test_server_info(self, tmp_path):
        d = json.loads(self._run("server", "info", tmp_home=tmp_path).stdout)
        assert d["name"] == "phorme-training" and d["version"]

    def test_tools_list_has_public_finders(self, tmp_path):
        names = {t["name"] for t in json.loads(self._run("tools", "list", "--auth", "noauth", tmp_home=tmp_path).stdout)}
        assert {"find_coaching_brain", "find_exercise_swap", "preview_workout_import"} <= names

    def test_find_build_returns_brains_with_pages(self, tmp_path):
        d = json.loads(self._run("find", "build", "run a faster half marathon", "--days", "4", tmp_home=tmp_path).stdout)
        brains = d["structuredContent"]["brains"]
        assert brains and all(b["info_url"].startswith("https://phor.me/") for b in brains)

    def test_swap_keeps_the_pattern(self, tmp_path):
        d = json.loads(self._run("train", "swap", "Back Squat", "--equipment", "dumbbells", tmp_home=tmp_path).stdout)
        swaps = d["structuredContent"]["swaps"]
        assert swaps and all("squat" in s["name"].lower() for s in swaps[:3])

    def test_workout_preview_is_remembered(self, tmp_path):
        d = json.loads(self._run("train", "workout", "Lower", "-x", "Back squat:4x6@225 lb", "-x", "Romanian deadlift:3x8", tmp_home=tmp_path).stdout)
        sc = d["structuredContent"]
        assert sc["preview_id"] and [e["library_name"] for e in sc["exercises"]] == ["Back Squat", "Romanian Deadlift"]
        status = json.loads(self._run("session", "status", tmp_home=tmp_path).stdout)
        assert status["previews"]["preview_workout_import"] == sc["preview_id"]

    def test_review_runs_on_the_live_server(self, tmp_path):
        out = tmp_path / "review.md"
        d = json.loads(self._run("review", "run", "--out", str(out), tmp_home=tmp_path).stdout)
        assert d["tools"] > 0 and out.read_text().startswith("# Review:")
        print(f"review: {out}")

    def test_unknown_tool_fails_loudly(self, tmp_path):
        r = self._run("tools", "call", "no_such_tool", "{}", check=False, tmp_home=tmp_path)
        assert r.returncode == 1 and "error" in json.loads(r.stdout)

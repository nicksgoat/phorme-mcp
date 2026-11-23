"""CLI-side state between commands: the server profile, the last results, and preview ids waiting to be saved.

The server holds the training; this only remembers what the CLI was doing (HARNESS.md "state model"). Saved as JSON
under an exclusive lock (guides/session-locking.md), with undo/redo over the CLI state, never over server writes.
"""

from __future__ import annotations

import copy
import fcntl
import json
import os
from pathlib import Path

HOME = Path(os.environ.get("CLI_ANYTHING_PHORME_HOME", Path.home() / ".cli-anything-phorme"))
MAX_UNDO = 50


def _locked_save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


class Session:
    """One CLI session: `state` is what persists; undo/redo snapshot it."""

    def __init__(self, path: Path | None = None):
        self.path = path or HOME / "session.json"
        self.state: dict = {"profile": "prod", "previews": {}, "history": [], "last": None}
        self._undo: list[dict] = []
        self._redo: list[dict] = []
        if self.path.exists() and self.path.read_text().strip():
            self.state.update(json.loads(self.path.read_text()))

    def snapshot(self) -> None:
        self._undo.append(copy.deepcopy(self.state))
        self._undo = self._undo[-MAX_UNDO:]
        self._redo.clear()

    def undo(self) -> bool:
        if not self._undo:
            return False
        self._redo.append(copy.deepcopy(self.state))
        self.state = self._undo.pop()
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        self._undo.append(copy.deepcopy(self.state))
        self.state = self._redo.pop()
        return True

    def record(self, tool: str, arguments: dict, result: dict) -> None:
        """Remembers a call; a preview's id is kept so `save` can refer to it by kind."""
        self.snapshot()
        self.state["history"] = (self.state["history"] + [{"tool": tool, "arguments": arguments}])[-100:]
        self.state["last"] = {"tool": tool, "result": result}
        sc = result.get("structuredContent") or {}
        if isinstance(sc, dict) and sc.get("preview_id"):
            self.state["previews"][tool] = sc["preview_id"]
        self.save()

    def save(self) -> None:
        _locked_save_json(self.path, self.state)

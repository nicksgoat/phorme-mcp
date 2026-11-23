"""Writes a result to a file: a tool's structured answer as JSON, or a review as Markdown (HARNESS.md "export")."""

from __future__ import annotations

import json
from pathlib import Path

EXPORT_PRESETS = {"json": ".json", "md": ".md"}


def render(data: dict | list | str, out: str, fmt: str = "json", overwrite: bool = False) -> dict:
    if fmt not in EXPORT_PRESETS:
        raise ValueError(f"format '{fmt}' is not one of {', '.join(EXPORT_PRESETS)}")
    path = Path(out)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} exists; pass --overwrite")
    text = data if isinstance(data, str) else json.dumps(data, indent=2)
    path.write_text(text)
    return {"output": str(path), "format": fmt, "bytes": path.stat().st_size}

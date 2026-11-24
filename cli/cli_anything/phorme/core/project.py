"""Server profiles: which Phorme Training server the CLI talks to (HARNESS.md "project": create/open/info/list)."""

from __future__ import annotations

import os

PROFILES = {
    "prod": "https://phor.me/api/mcp",
    "local": "http://localhost:3000/api/mcp",
}


def list_profiles() -> dict[str, str]:
    return dict(PROFILES)


def url_for(profile: str) -> str:
    """PHORME_MCP_URL wins, so a preview deploy can be reviewed without a profile."""
    if os.environ.get("PHORME_MCP_URL"):
        return os.environ["PHORME_MCP_URL"]
    if profile not in PROFILES:
        raise ValueError(f"unknown profile '{profile}'; one of {', '.join(PROFILES)}")
    return PROFILES[profile]


def info(profile: str, init: dict) -> dict:
    s = init.get("serverInfo") or {}
    return {"profile": profile, "url": url_for(profile), "name": s.get("name"), "title": s.get("title"),
            "version": s.get("version"), "protocol": init.get("protocolVersion"), "instructions": init.get("instructions", "")}

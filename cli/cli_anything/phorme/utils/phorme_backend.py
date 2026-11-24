"""Phorme Training MCP backend: the real server, spoken to over MCP streamable HTTP.

CLI-Anything's MCP backend pattern (guides/mcp-backend.md) spawns a stdio server per command. Phorme's server is
remote (https://phor.me/api/mcp, server.json "remotes"), so each command is one JSON-RPC POST. Nothing is
reimplemented here: every answer comes from the live server.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_URL = "https://phor.me/api/mcp"
PROTOCOL = "2025-06-18"
UA = "cli-anything-phorme/1.0"


class BackendError(RuntimeError):
    """The server could not be reached, or answered with a JSON-RPC error."""


def server_url() -> str:
    return os.environ.get("PHORME_MCP_URL", DEFAULT_URL)


def _token() -> str | None:
    # shortcut: member tools take a bearer token from PHORME_MCP_TOKEN; there is no OAuth login flow here yet,
    # add one (the server's /.well-known/oauth-* endpoints) when people use the CLI for member tools.
    return os.environ.get("PHORME_MCP_TOKEN") or None


def _parse(body: str, content_type: str) -> dict:
    """The server answers either application/json or a text/event-stream with one data: line per message."""
    if "text/event-stream" in content_type:
        msgs = [json.loads(line[5:].strip()) for line in body.splitlines() if line.startswith("data:") and line[5:].strip()]
        if not msgs:
            raise BackendError("empty event stream from the server")
        return msgs[-1]
    return json.loads(body)


def rpc(method: str, params: dict | None = None, url: str | None = None, timeout: float = 60.0) -> Any:
    """One JSON-RPC call. Returns `result`, raises BackendError on a transport or protocol error."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, **({"params": params} if params is not None else {})}
    headers = {"content-type": "application/json", "accept": "application/json, text/event-stream", "user-agent": UA,
               "mcp-protocol-version": PROTOCOL}
    tok = _token()
    if tok:
        headers["authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url or server_url(), data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            msg = _parse(res.read().decode(), res.headers.get("content-type", ""))
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        hint = " (this tool needs a Phorme account: set PHORME_MCP_TOKEN)" if e.code == 401 else ""
        raise BackendError(f"{method}: HTTP {e.code}{hint}: {detail}") from e
    except urllib.error.URLError as e:
        raise BackendError(f"cannot reach {url or server_url()}: {e.reason}") from e
    if "error" in msg:
        err = msg["error"]
        raise BackendError(f"{method}: {err.get('message', err)}")
    return msg.get("result")


def initialize(url: str | None = None) -> dict:
    return rpc("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "cli-anything-phorme", "version": "1.0"}}, url)


def list_tools(url: str | None = None) -> list[dict]:
    return (rpc("tools/list", {}, url) or {}).get("tools", [])


def call_tool(name: str, arguments: dict, url: str | None = None) -> dict:
    """Calls a tool. A tool-level failure (isError) is raised, so the CLI fails loudly."""
    res = rpc("tools/call", {"name": name, "arguments": arguments}, url) or {}
    if res.get("isError"):
        text = " ".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        raise BackendError(f"{name}: {text or 'the tool reported an error'}")
    return res


def is_available(url: str | None = None) -> bool:
    try:
        initialize(url)
        return True
    except BackendError:
        return False

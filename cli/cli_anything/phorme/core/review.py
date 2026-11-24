"""Review of a Phorme Training MCP server's tool surface, from what the server itself lists.

Each check reads the live tools/list and initialize answers (and, when given, the repo's published server.json and
tools.json), so a review is repeatable after every server change: `cli-anything-phorme review run`.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SEVERITY = {"high": 3, "medium": 2, "low": 1}

# What the product says an assistant should be able to do through the plugin (founder/PHILOSOPHY.md, pillar 2 and
# nutrition). A capability is covered when some tool's name or description matches its pattern.
CAPABILITIES = [
    ("nutrition", r"\b(meal plan|meals|fuel|grocer|nutrition plan|food plan)", "the plugin door \"fuel my training week\": a week of meals sized to the sessions"),
    ("coach characters", r"\b(meet_the_coaches|list_coaches|coach character)", "the coaches as characters: who each one is and what it plans"),
    ("talk to my coach", r"\bask_coach\b", "a member asking their own coach, answered by the coach engine from their plan"),
]

# Write tools whose names say they only stage something (a preview row the member saves later).
STAGING = re.compile(r"^(preview_|render_|check_)")


@dataclass
class Finding:
    severity: str
    rule: str
    tool: str
    detail: str


def _auth(tool: dict) -> list[str]:
    sec = tool.get("securitySchemes") or tool.get("_meta", {}).get("securitySchemes") or []
    return [s.get("type", "?") for s in sec]


def review(tools: list[dict], init: dict, server_json: dict | None = None, tools_json: dict | None = None,
           desc_budget: int = 600, surface_budget: int = 40_000, tool_budget: int = 40) -> list[Finding]:
    out: list[Finding] = []
    add = lambda sev, rule, tool, detail: out.append(Finding(sev, rule, tool, detail))
    names = {t["name"] for t in tools}

    # Published metadata that has drifted from the live server misleads registries and directories.
    live_version = (init.get("serverInfo") or {}).get("version")
    if server_json and live_version and server_json.get("version") != live_version:
        add("medium", "version-drift", "-", f"server.json says {server_json.get('version')}, the live server is {live_version}")
    if tools_json:
        published = {t["name"] for t in tools_json.get("tools", [])}
        if published != names:
            add("medium", "tools-drift", "-", f"tools.json differs from the live list: missing {sorted(names - published)[:8]}, gone {sorted(published - names)[:8]}")

    # The instructions route assistants by tool name; a name that isn't served sends them nowhere.
    for word in sorted(set(re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", init.get("instructions", "")))):
        if word not in names:
            add("high", "instructions-unknown-tool", word, "named in the server instructions but not served")

    for t in tools:
        a, props = t.get("annotations", {}), t.get("inputSchema", {}).get("properties", {})
        write = not a.get("readOnlyHint")
        if a.get("destructiveHint") and "confirmation" not in props:
            add("high", "destructive-without-confirmation", t["name"], "destructive, with no confirmation input")
        elif write and "confirmation" not in props and not STAGING.match(t["name"]):
            add("medium", "write-without-confirmation", t["name"], "changes something, with no confirmation input")
        if write and "noauth" in _auth(t) and "oauth2" not in _auth(t):
            add("medium", "write-without-account", t["name"], "not read-only, yet callable with no account (rows or spend from anyone)")
        if write and not a.get("idempotentHint") and "idempotency_key" not in props and "confirmation" in props:
            add("low", "retry-may-duplicate", t["name"], "a write with no idempotency key: a retried call can apply twice")
        if not t.get("outputSchema"):
            add("low", "no-output-schema", t["name"], "no outputSchema; clients can't validate structuredContent")
        if len(t.get("description", "")) > desc_budget:
            add("low", "long-description", t["name"], f"{len(t['description'])} characters (budget {desc_budget}); every connected chat pays for it")
        for p, s in props.items():
            if p in t["inputSchema"].get("required", []) and not s.get("description") and p not in ("confirmation", "idempotency_key"):
                add("low", "undescribed-required-input", t["name"], f"required input '{p}' has no description")

    surface = sum(len(t.get("description", "")) + len(json.dumps(t.get("inputSchema", {}))) for t in tools)
    if len(tools) > tool_budget or surface > surface_budget:
        audiences = {"member": 0, "coach": 0, "gym": 0}
        for t in tools:
            d = t.get("description", "").lower()
            audiences["gym" if re.search(r"\b(gym owner|place|gym brain|booking notices|payout|billing)", d) else "coach" if re.search(r"phorme coach|their ai coach|their members|own build", d) else "member"] += 1
        add("medium", "tool-overload", "-", f"{len(tools)} tools, about {surface // 4:,} tokens of tool text in every chat; by audience {audiences}. Assistants pick worse past ~40; consider one server per audience")

    # A tool's "Do not use it for …" sentence names what it does NOT cover, so it never counts.
    said = {t["name"]: t["name"] + " " + re.sub(r"[^.]*\b(?:do not|don't|never) use it[^.]*\.?", "", t.get("description", ""), flags=re.I) for t in tools}
    for cap, pattern, why in CAPABILITIES:
        if not any(re.search(pattern, text, re.I) for text in said.values()):
            add("high", "missing-capability", cap, f"no tool covers {why}")

    out.sort(key=lambda f: (-SEVERITY[f.severity], f.rule, f.tool))
    return out


def load_json(path: str | None) -> dict | None:
    return json.loads(Path(path).read_text()) if path and Path(path).exists() else None


def as_dicts(findings: list[Finding]) -> list[dict]:
    return [asdict(f) for f in findings]


def to_markdown(findings: list[Finding], init: dict, tool_count: int) -> str:
    info = init.get("serverInfo") or {}
    lines = [f"# Review: {info.get('title', info.get('name', 'server'))} {info.get('version', '')}", "",
             f"{tool_count} tools. {sum(f.severity == 'high' for f in findings)} high, {sum(f.severity == 'medium' for f in findings)} medium, {sum(f.severity == 'low' for f in findings)} low.", "",
             "| Severity | Rule | Tool | Detail |", "| --- | --- | --- | --- |"]
    lines += [f"| {f.severity} | {f.rule} | `{f.tool}` | {f.detail.replace('|', '/')} |" for f in findings]
    return "\n".join(lines) + "\n"

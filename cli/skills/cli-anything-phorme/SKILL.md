---
name: "cli-anything-phorme"
description: "Phorme Training from the terminal: find a build, programme or race plan, preview a workout matched to Phorme's movement library, swap an exercise, meet and ask the Phorme coaches, and review the MCP server. Use when an agent needs Phorme training data or a workout as JSON."
---

# cli-anything-phorme

A CLI-Anything harness over the live Phorme Training MCP server (`https://phor.me/api/mcp`). Every command calls the
real server's tools; `--json` prints the tool's own result.

## Installation

```bash
cd cli && pip install -e .
```

**Prerequisites:** Python 3.10+ and network access to phor.me. Finders and previews need no account; `me ...` needs a
Phorme account token in `PHORME_MCP_TOKEN`.

## Command Groups

### Cli

Phorme Training from the terminal: builds, programmes, races, workouts and the coaches.

| Command | Description |
|---------|-------------|
| `repl` | Interactive mode (the default with no command). |

### Server

The server: its version, instructions and profiles.

| Command | Description |
|---------|-------------|
| `info` | Execute server_info operation. |
| `profiles` | Execute server_profiles operation. |

### Tools

List, inspect and call any tool the server serves.

| Command | Description |
|---------|-------------|
| `list` | Execute tools_list operation. |
| `show` | Execute tools_show operation. |
| `call` | Call NAME with ARGUMENTS as a JSON object. |

### Coaches

The Phorme coaches: who they are, what each one plans, and asking one.

| Command | Description |
|---------|-------------|
| `list` | Execute coaches_list operation. |
| `show` | Execute coaches_show operation. |
| `ask` | Ask COACH a QUESTION; answered in that coach's voice from Phorme's method. |

### Train

Workouts, sport weeks and swaps.

| Command | Description |
|---------|-------------|
| `workout` | Preview a workout called TITLE, each exercise matched to Phorme's movement library with a demo link. |
| `sport-week` | Execute train_sport_week operation. |
| `swap` | Execute train_swap operation. |

### Find

Find builds, programmes, races, classes, clinics and personal coaches.

| Command | Description |
|---------|-------------|
| `build` | Execute find_build operation. |
| `programs` | Execute find_programs operation. |
| `program` | Execute find_program operation. |
| `races` | Execute find_races operation. |
| `race-plan` | Execute find_race_plan operation. |
| `class` | Execute find_class operation. |
| `clinic` | Execute find_clinic operation. |
| `personal-coach` | Execute find_personal_coach operation. |

### Me

Your own log and plan (needs a Phorme account token in PHORME_MCP_TOKEN).

| Command | Description |
|---------|-------------|
| `history` | Execute me_history operation. |
| `planned` | Execute me_planned operation. |

### Review

Review the server's tool surface (annotations, confirmation, auth, drift, size, coverage).

| Command | Description |
|---------|-------------|
| `run` | Execute review_run operation. |

### Session

What this CLI remembers between commands.

| Command | Description |
|---------|-------------|
| `status` | Execute session_status operation. |
| `history` | Execute session_history operation. |
| `clear` | Execute session_clear operation. |

## Examples

```bash
cli-anything-phorme --json find build "first HYROX race" --days 4
cli-anything-phorme --json train workout "Lower" -x "Back squat:4x6@225 lb" -x "Romanian deadlift:3x8"
cli-anything-phorme --json train swap "Back Squat" --equipment dumbbells --reason equipment
cli-anything-phorme --json coaches ask stride "how should my long run feel?"
cli-anything-phorme --json tools call plan_for_race '{"race":"HYROX Miami"}'
cli-anything-phorme review run --fail-on high
```

## For AI Agents

When using this CLI programmatically:

1. **Always use `--json` flag** for parseable output
2. **Check return codes** - 0 for success, non-zero for errors
3. **Parse stderr** for error messages on failure
4. **Use absolute paths** for all file operations
5. **Verify outputs exist** after export operations

## Version

1.0.0
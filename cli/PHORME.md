# Phorme Training: CLI-Anything SOP

## Architecture analysis (CLI-Anything phase 1)

- **Backend engine:** the Phorme Training MCP server, `https://phor.me/api/mcp` (streamable HTTP, protocol 2025-06-18).
  CLI-Anything's MCP backend pattern spawns a stdio server; this server is remote, so the backend
  (`utils/phorme_backend.py`) sends one JSON-RPC POST per call.
- **"GUI actions" here are tools.** The server serves 61 tools in three audiences: members (finders, previews, their
  log), coaches building their own build (study, teach, rate, clients), and gym owners (places, schedules, cover,
  payouts). The CLI groups the member side by task (`find`, `train`, `me`, `coaches`), and every tool stays reachable
  through `tools call`.
- **Data model:** JSON in and out. A tool returns `content` (text written for an assistant) and `structuredContent` (the
  data). Previews return a `preview_id` that expires in 24 h and is saved later by a signed-in member. The CLI keeps the
  ids in its session.
- **Auth:** finders and previews take no account; member, coach and gym tools take OAuth 2.1 (`securitySchemes` per
  tool). The CLI reads a bearer token from `PHORME_MCP_TOKEN`. It has no login flow yet.
- **Undo:** server writes carry their own `confirmation` and, for saves, an `idempotency_key`. The CLI's undo covers only
  its own state.

## Command map

| CLI | Tool |
| --- | --- |
| `find build` | `find_coaching_brain` |
| `find programs` / `find program` | `search_phorme_programs` / `get_phorme_program` |
| `find races` / `find race-plan` | `find_races` / `plan_for_race` |
| `find class` / `clinic` / `personal-coach` | `find_gym_class` / `find_clinic` / `find_personal_coach` |
| `train workout` / `sport-week` / `swap` | `preview_workout_import` / `preview_sport_week` / `find_exercise_swap` |
| `me history` / `me planned` | `get_training_history` / `get_planned_sessions` |
| `coaches list` / `show` / `ask` | `meet_the_coaches` / `ask_coach` (not served yet) |
| `tools call NAME ARGS` | any tool |

## Rendering gap

Nothing is rendered locally. The workout card (`render_training_import`) is a ChatGPT widget template; the CLI prints
the same data from `structuredContent`.

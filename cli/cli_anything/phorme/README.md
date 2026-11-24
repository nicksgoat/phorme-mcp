# cli-anything-phorme

Phorme Training from the terminal, for people and for agents. It is a [CLI-Anything](https://github.com/HKUDS/CLI-Anything)
harness over the live Phorme Training MCP server (`https://phor.me/api/mcp`): every command calls the real server's
tools, nothing is reimplemented, and `--json` prints the tool's own result.

## Install

```bash
cd cli
pip install -e .            # Python 3.10+
cli-anything-phorme --help
```

The server is the only dependency. Finders and previews need no account. Your own log and plan (`me ...`) need a Phorme
account token in `PHORME_MCP_TOKEN`. `PHORME_MCP_URL` points the CLI at another server, for example a preview deploy.

## Usage

```bash
cli-anything-phorme                                   # REPL
cli-anything-phorme find build "run a faster half marathon" --days 4
cli-anything-phorme find races --kind hyrox --where Miami
cli-anything-phorme train workout "Lower" -x "Back squat:4x6@225 lb" -x "Romanian deadlift:3x8" --minutes 45
cli-anything-phorme train swap "Back Squat" --equipment dumbbells
cli-anything-phorme coaches list                      # the coaches as characters
cli-anything-phorme coaches ask miles "how should my long run feel?"
cli-anything-phorme --json tools call find_clinic '{"city":"Austin","care":"physio"}'
cli-anything-phorme review run --server-json ../server.json --tools-json ../tools.json --fail-on high
```

## Command groups

| Group | Commands | What for |
| --- | --- | --- |
| `server` | `info`, `profiles` | Version, instructions, which server |
| `tools` | `list`, `show`, `call` | The raw tool surface; any tool by name |
| `coaches` | `list`, `show`, `ask` | The Phorme coaches: who each is, what it plans, ask one |
| `train` | `workout`, `sport-week`, `swap` | Workout previews matched to the movement library |
| `find` | `build`, `programs`, `program`, `races`, `race-plan`, `class`, `clinic`, `personal-coach` | Discovery |
| `me` | `history`, `planned` | Your own log and plan (token) |
| `review` | `run` | Lint the server: confirmation, auth, drift, size, coverage |
| `session` | `status`, `history`, `clear` | What the CLI remembers (previews waiting to be saved) |

State lives in `~/.cli-anything-phorme/session.json` (override with `CLI_ANYTHING_PHORME_HOME`).

## Tests

```bash
pip install -e ".[test]"
CLI_ANYTHING_FORCE_INSTALLED=1 pytest -v cli_anything/phorme/tests
```

The E2E tests call the live server with read-only and preview tools only. See `tests/TEST.md`.

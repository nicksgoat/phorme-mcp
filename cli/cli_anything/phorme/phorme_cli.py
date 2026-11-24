"""cli-anything-phorme: the Phorme Training MCP server as a command line, for people and agents.

Every command calls the live server's tools (utils/phorme_backend.py); `--json` prints the raw tool result for agents.
With no command it opens the REPL.
"""

from __future__ import annotations

import functools
import json
import shlex
import sys

import click

from cli_anything.phorme.core import export as export_mod
from cli_anything.phorme.core import project as project_mod
from cli_anything.phorme.core import review as review_mod
from cli_anything.phorme.core.session import Session
from cli_anything.phorme.utils import phorme_backend as backend

VERSION = "1.0.0"


class Ctx:
    def __init__(self, json_out: bool, profile: str):
        self.json = json_out
        self.profile = profile
        self.session = Session()
        self.url = project_mod.url_for(profile)


def handle_error(fn):
    """One error shape for every command: a clear message (or {"error": ...} with --json) and exit code 1."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (backend.BackendError, ValueError, FileExistsError) as e:
            ctx = click.get_current_context().find_object(Ctx)
            if ctx and ctx.json:
                click.echo(json.dumps({"error": str(e)}))
            else:
                click.secho(f"✗ {e}", fg="red", err=True)
            sys.exit(1)
    return wrapper


def emit(ctx: Ctx, data, human=None) -> None:
    if ctx.json:
        click.echo(json.dumps(data, indent=2, default=str))
    elif human:
        human(data)
    else:
        click.echo(json.dumps(data, indent=2, default=str))


def text_of(result: dict) -> str:
    return "\n".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text").strip()


def call(ctx: Ctx, tool: str, args: dict) -> dict:
    args = {k: v for k, v in args.items() if v not in (None, (), [])}
    res = backend.call_tool(tool, args, ctx.url)
    ctx.session.record(tool, args, res)
    return res


def show_result(res: dict) -> None:
    click.echo(text_of(res) or json.dumps(res.get("structuredContent", res), indent=2))


@click.group(invoke_without_command=True)
@click.option("--json", "json_out", is_flag=True, help="Machine-readable output.")
@click.option("--profile", default="prod", show_default=True, help="Server profile (see `server profiles`).")
@click.version_option(VERSION)
@click.pass_context
def cli(click_ctx, json_out, profile):
    """Phorme Training from the terminal: builds, programmes, races, workouts and the coaches."""
    click_ctx.obj = Ctx(json_out, profile)
    if click_ctx.invoked_subcommand is None:
        click_ctx.invoke(repl)


# ── server ────────────────────────────────────────────────────────────

@cli.group()
def server():
    """The server: its version, instructions and profiles."""


@server.command("info")
@click.pass_obj
@handle_error
def server_info(ctx):
    data = project_mod.info(ctx.profile, backend.initialize(ctx.url))
    emit(ctx, data, lambda d: [click.echo(f"{k:12} {v}") for k, v in d.items()])


@server.command("profiles")
@click.pass_obj
@handle_error
def server_profiles(ctx):
    emit(ctx, project_mod.list_profiles(), lambda d: [click.echo(f"{k:6} {v}") for k, v in d.items()])


# ── tools (the raw surface) ──────────────────────────────────────────

@cli.group()
def tools():
    """List, inspect and call any tool the server serves."""


@tools.command("list")
@click.option("--auth", type=click.Choice(["noauth", "oauth2"]), help="Only tools with this sign-in.")
@click.option("--writes", is_flag=True, help="Only tools that change something.")
@click.pass_obj
@handle_error
def tools_list(ctx, auth, writes):
    ts = backend.list_tools(ctx.url)
    rows = [{"name": t["name"], "title": t.get("title"), "read_only": t.get("annotations", {}).get("readOnlyHint"),
             "auth": review_mod._auth(t)} for t in ts]
    rows = [r for r in rows if (not auth or auth in r["auth"]) and (not writes or not r["read_only"])]
    emit(ctx, rows, lambda rs: [click.echo(f"{r['name']:36} {'read ' if r['read_only'] else 'write'} {','.join(r['auth']):14} {r['title']}") for r in rs])


@tools.command("show")
@click.argument("name")
@click.pass_obj
@handle_error
def tools_show(ctx, name):
    t = next((t for t in backend.list_tools(ctx.url) if t["name"] == name), None)
    if not t:
        raise ValueError(f"the server serves no tool named '{name}' (see `tools list`)")
    emit(ctx, t)


@tools.command("call")
@click.argument("name")
@click.argument("arguments", default="{}")
@click.pass_obj
@handle_error
def tools_call(ctx, name, arguments):
    """Call NAME with ARGUMENTS as a JSON object."""
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError as e:
        raise ValueError(f"ARGUMENTS must be a JSON object: {e}") from e
    emit(ctx, call(ctx, name, args), show_result)


# ── coaches ──────────────────────────────────────────────────────────

@cli.group()
def coaches():
    """The Phorme coaches: who they are, what each one plans, and asking one."""


@coaches.command("list")
@click.pass_obj
@handle_error
def coaches_list(ctx):
    emit(ctx, call(ctx, "meet_the_coaches", {}), show_result)


@coaches.command("show")
@click.argument("coach")
@click.pass_obj
@handle_error
def coaches_show(ctx, coach):
    emit(ctx, call(ctx, "meet_the_coaches", {"coach": coach}), show_result)


@coaches.command("ask")
@click.argument("coach")
@click.argument("question")
@click.pass_obj
@handle_error
def coaches_ask(ctx, coach, question):
    """Ask COACH a QUESTION; answered in that coach's voice from Phorme's method."""
    emit(ctx, call(ctx, "ask_coach", {"coach": coach, "question": question}), show_result)


# ── training ─────────────────────────────────────────────────────────

@cli.group()
def train():
    """Workouts, sport weeks and swaps."""


def parse_exercise(spec: str) -> dict:
    """'Back squat:4x6@225 lb' → {name, sets, reps, load}. Reps stay text ("8-10", "AMRAP", "40 sec")."""
    name, sep, dose = spec.rpartition(":")
    if not sep or "x" not in dose:
        raise ValueError(f"exercise '{spec}' should look like 'Back squat:4x6' or 'Row:3x8@60 kg'")
    sets, _, rest = dose.partition("x")
    reps, _, load = rest.partition("@")
    if not sets.strip().isdigit():
        raise ValueError(f"exercise '{spec}': sets must be a number")
    return {"name": name.strip(), "sets": int(sets), "reps": reps.strip(), **({"load": load.strip()} if load.strip() else {})}


@train.command("workout")
@click.argument("title")
@click.option("-x", "--exercise", "exercises", multiple=True, required=True, help="NAME:SETSxREPS[@LOAD], in order (repeat).")
@click.option("--minutes", type=int, help="Time limit.")
@click.option("--equipment", multiple=True, help="Equipment on hand (repeat).")
@click.pass_obj
@handle_error
def train_workout(ctx, title, exercises, minutes, equipment):
    """Preview a workout called TITLE, each exercise matched to Phorme's movement library with a demo link."""
    workout = {"title": title, "exercises": [parse_exercise(x) for x in exercises]}
    emit(ctx, call(ctx, "preview_workout_import", {"workout": workout, "time_limit_minutes": minutes,
                                                   "available_equipment": list(equipment)}), show_result)


@train.command("sport-week")
@click.argument("sport")
@click.option("--gym-days", type=int, required=True)
@click.option("--phase", type=click.Choice(["off_season", "pre_season", "in_season", "unknown"]))
@click.pass_obj
@handle_error
def train_sport_week(ctx, sport, gym_days, phase):
    emit(ctx, call(ctx, "preview_sport_week", {"sport": sport, "gym_days_per_week": gym_days, "season_phase": phase}), show_result)


@train.command("swap")
@click.argument("exercise")
@click.option("--equipment", multiple=True, required=True)
@click.option("--reason", type=click.Choice(["equipment", "busy", "preference"]))
@click.pass_obj
@handle_error
def train_swap(ctx, exercise, equipment, reason):
    emit(ctx, call(ctx, "find_exercise_swap", {"exercise": exercise, "available_equipment": list(equipment), "reason": reason}), show_result)


# ── programmes, builds, races, places ────────────────────────────────

@cli.group()
def find():
    """Find builds, programmes, races, classes, clinics and personal coaches."""


@find.command("build")
@click.argument("goal", required=False)
@click.option("--sport")
@click.option("--days", type=int)
@click.option("--coach")
@click.option("--code")
@click.pass_obj
@handle_error
def find_build(ctx, goal, sport, days, coach, code):
    emit(ctx, call(ctx, "find_coaching_brain", {"goal": goal, "sport": sport, "days_per_week": days, "coach": coach, "code": code}), show_result)


@find.command("programs")
@click.option("--goal")
@click.option("--sport")
@click.option("--days", type=int)
@click.option("--weeks", type=int)
@click.option("--creator")
@click.pass_obj
@handle_error
def find_programs(ctx, goal, sport, days, weeks, creator):
    emit(ctx, call(ctx, "search_phorme_programs", {"goal": goal, "sport": sport, "schedule_days": days, "duration_weeks": weeks, "creator": creator}), show_result)


@find.command("program")
@click.argument("program_id")
@click.pass_obj
@handle_error
def find_program(ctx, program_id):
    emit(ctx, call(ctx, "get_phorme_program", {"program_id": program_id}), show_result)


@find.command("races")
@click.option("--kind")
@click.option("--where")
@click.option("--from-month")
@click.option("--to-month")
@click.pass_obj
@handle_error
def find_races(ctx, kind, where, from_month, to_month):
    emit(ctx, call(ctx, "find_races", {"kind": kind, "where": where, "from_month": from_month, "to_month": to_month}), show_result)


@find.command("race-plan")
@click.argument("race")
@click.pass_obj
@handle_error
def find_race_plan(ctx, race):
    emit(ctx, call(ctx, "plan_for_race", {"race": race}), show_result)


@find.command("class")
@click.argument("city")
@click.option("--type", "class_type")
@click.pass_obj
@handle_error
def find_class(ctx, city, class_type):
    emit(ctx, call(ctx, "find_gym_class", {"city": city, "class_type": class_type}), show_result)


@find.command("clinic")
@click.argument("city")
@click.option("--care", type=click.Choice(["physio", "sports_medicine", "chiropractic", "massage", "recovery"]))
@click.pass_obj
@handle_error
def find_clinic(ctx, city, care):
    emit(ctx, call(ctx, "find_clinic", {"city": city, "care": care}), show_result)


@find.command("personal-coach")
@click.argument("goal")
@click.option("--sport")
@click.pass_obj
@handle_error
def find_personal_coach(ctx, goal, sport):
    emit(ctx, call(ctx, "find_personal_coach", {"goal": goal, "sport": sport}), show_result)


# ── me (needs PHORME_MCP_TOKEN) ──────────────────────────────────────

@cli.group()
def me():
    """Your own log and plan (needs a Phorme account token in PHORME_MCP_TOKEN)."""


@me.command("history")
@click.option("--limit", type=int, default=10)
@click.pass_obj
@handle_error
def me_history(ctx, limit):
    emit(ctx, call(ctx, "get_training_history", {"limit": limit}), show_result)


@me.command("planned")
@click.option("--days", type=int, default=7)
@click.pass_obj
@handle_error
def me_planned(ctx, days):
    emit(ctx, call(ctx, "get_planned_sessions", {"days": days}), show_result)


# ── review ───────────────────────────────────────────────────────────

@cli.group()
def review():
    """Review the server's tool surface (annotations, confirmation, auth, drift, size, coverage)."""


@review.command("run")
@click.option("--server-json", type=click.Path(), help="The published server.json to check for drift.")
@click.option("--tools-json", type=click.Path(), help="The published tools.json to check for drift.")
@click.option("--out", type=click.Path(), help="Write the review to a file.")
@click.option("--format", "fmt", type=click.Choice(["md", "json"]), default="md")
@click.option("--overwrite", is_flag=True)
@click.option("--fail-on", type=click.Choice(["high", "medium", "low"]), help="Exit 2 when any finding is this severe or worse.")
@click.pass_obj
@handle_error
def review_run(ctx, server_json, tools_json, out, fmt, overwrite, fail_on):
    init, ts = backend.initialize(ctx.url), backend.list_tools(ctx.url)
    findings = review_mod.review(ts, init, review_mod.load_json(server_json), review_mod.load_json(tools_json))
    md = review_mod.to_markdown(findings, init, len(ts))
    if out:
        export_mod.render(md if fmt == "md" else review_mod.as_dicts(findings), out, fmt, overwrite)
    emit(ctx, {"server": init.get("serverInfo"), "tools": len(ts), "findings": review_mod.as_dicts(findings)}, lambda _: click.echo(md))
    if fail_on and any(review_mod.SEVERITY[f.severity] >= review_mod.SEVERITY[fail_on] for f in findings):
        sys.exit(2)


# ── session ──────────────────────────────────────────────────────────

@cli.group()
def session():
    """What this CLI remembers between commands."""


@session.command("status")
@click.pass_obj
def session_status(ctx):
    s = ctx.session.state
    emit(ctx, {"profile": ctx.profile, "url": ctx.url, "calls": len(s["history"]), "previews": s["previews"],
               "last_tool": (s["last"] or {}).get("tool")})


@session.command("history")
@click.pass_obj
def session_history(ctx):
    emit(ctx, ctx.session.state["history"], lambda h: [click.echo(f"{i:3} {c['tool']} {json.dumps(c['arguments'])}") for i, c in enumerate(h)])


@session.command("clear")
@click.pass_obj
def session_clear(ctx):
    ctx.session.snapshot()
    ctx.session.state.update({"previews": {}, "history": [], "last": None})
    ctx.session.save()
    emit(ctx, {"cleared": True}, lambda _: click.echo("✓ cleared"))


# ── REPL ─────────────────────────────────────────────────────────────

@cli.command()
@click.pass_context
def repl(click_ctx):
    """Interactive mode (the default with no command)."""
    from cli_anything.phorme.utils.repl_skin import ReplSkin
    skin = ReplSkin("phorme", version=VERSION)
    skin.print_banner()
    pt = skin.create_prompt_session()
    ctx: Ctx = click_ctx.obj
    while True:
        try:
            line = skin.get_input(pt, project_name=ctx.profile)
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if line.strip() in ("exit", "quit"):
            break
        if line.strip() == "help":
            skin.help({name: (cmd.help or "").split("\n")[0] for name, cmd in cli.commands.items() if name != "repl"})
            continue
        args = (["--json"] if ctx.json else []) + ["--profile", ctx.profile] + shlex.split(line)
        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.ClickException as e:
            skin.error(e.format_message())
    skin.print_goodbye()


def main():
    cli()


if __name__ == "__main__":
    main()

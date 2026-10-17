# Phorme Training MCP server

Coach-built training for any AI assistant. Phorme Training is a remote [Model Context Protocol](https://modelcontextprotocol.io) server. An assistant can use it to find a coaching brain, program, race plan, gym class or sports clinic, preview workouts with exercise demos, and save training to the [Phorme](https://phor.me) app.

- **Endpoint:** `https://phor.me/api/mcp` (streamable HTTP)
- **Version:** <!-- version:start -->1.8.0<!-- version:end -->
- **Auth:** none for finders and previews. Saving training and reading a member's log use OAuth 2.1 ([protected resource metadata](https://phor.me/.well-known/oauth-protected-resource)).
- **Server card:** [`https://phor.me/.well-known/mcp.json`](https://phor.me/.well-known/mcp.json)
- **Registry name:** `me.phor/phorme-training` in the [official MCP registry](https://registry.modelcontextprotocol.io/v0/servers?search=me.phor)

This repository documents the hosted server. The server itself runs at phor.me; there is nothing to install or self-host. A daily job reads the live server and updates [`tools.json`](tools.json) and the tool table below, so they always match what the endpoint serves.

## Connect

**Claude Code**

```sh
claude mcp add --transport http phorme https://phor.me/api/mcp
```

**Claude (web and desktop):** Settings → Connectors → Add custom connector → `https://phor.me/api/mcp`.

**ChatGPT:** Settings → Apps → Advanced → Developer mode, then Create app with `https://phor.me/api/mcp`.

**Cursor, VS Code, Windsurf and other clients**

```json
{
  "mcpServers": {
    "phorme": { "url": "https://phor.me/api/mcp" }
  }
}
```

**Plain HTTP:** see [`examples/call.sh`](examples/call.sh).

## Tools

<!-- tools:start -->
| Tool | What it does | Kind | Auth |
|---|---|---|---|
| `preview_workout_import` | Use this when the user wants a single workout they can follow and track in Phorme: one written in this conversation, pasted from notes, or built to fit their time and equipment. | write | none |
| `save_workout_to_phorme` | Use this when the user has seen a workout preview and clearly said to save it. | write | OAuth |
| `preview_program_import` | Use this when the user wants to turn a multiweek training program from this conversation into trackable Phorme training. | write | none |
| `save_program_to_phorme` | Use this when the user has seen a program preview and clearly said to save it. | write | OAuth |
| `get_saved_training` | Use this when the user asks about a workout or program already saved to Phorme in this conversation, for example to get its Phorme link again. | read | OAuth |
| `render_training_import` | Use this to show a compact Phorme card for a workout or program that was just previewed or saved. | read | none |
| `preview_sport_week` | Use this when the user plays a sport and wants their gym days for a week planned around it, for example two lifting days during basketball season. | read | none |
| `find_races` | Use this when the user is looking for a race to enter, for example "which 70.3 can I do in South America next spring", "marathons in Europe in April" or "a HYROX near Riga". | read | none |
| `plan_for_race` | Use this when the user names a race they are training for, for example "IRONMAN 70.3 Barranquilla", "I signed up for the half ironman in Cartagena" or "Chicago Marathon". | read | none |
| `find_coaching_brain` | Use this when the user wants a way to train for a goal or sport, for example "I want to get more explosive for basketball", "build muscle three days a week" or "train for a half marathon", and has not picked a programme. | read | none |
| `find_gym_class` | Use this when the user wants a gym, studio or class to train at in person, for example "a strength class in Austin this week" or "a gym near me". | read | none |
| `find_clinic` | Use this when the user wants to be seen in person by a physical therapist, sports medicine clinic, chiropractor, sports massage therapist or recovery studio, in a city they name or near a position they share. | read | none |
| `check_place_in_ai` | Use this when the owner or manager of a gym, studio or sports clinic asks whether ChatGPT knows their place or recommends it, for example "does ChatGPT recommend my gym?" or "what does AI say about my physio clinic in Austin?". | write | none |
| `find_exercise_swap` | Use this when the user needs a replacement for one exercise because they do not have the equipment, the station is taken, or they want a different option, for example no cable machine for cable rows. | read | none |
| `get_training_history` | Use this when the user asks about their own training logged in Phorme: what they did last time, how often they trained, their personal records, or a next workout built on their recent sessions. | read | OAuth |
| `get_lift_progress` | Use this when the user asks how one of their lifts is progressing or wants it graphed, for example "how is my bench going" or "chart my squat over six months". | read | OAuth |
| `get_planned_sessions` | Use this when the user asks what their Phorme plan has for today or the coming days, for example "what is my workout today". | read | OAuth |
| `get_my_coaching_business` | Use this when a Phorme coach asks about their own coaching brains: how many members train under each, who went quiet, what they have earned, and whether a note to members can go today. | read | OAuth |
| `start_my_coaching_brain` | Use this when a coach or trainer wants to turn their own method into a Phorme coaching brain and has none yet, or asks for a new one. | write | OAuth |
| `save_program_to_my_coaching_brain` | Use this when a Phorme coach has written a program in this conversation and clearly said to save it to one of their coaching brains. | write | OAuth |
| `send_note_to_my_members` | Use this when a Phorme coach has written a short note to everyone training under one of their published coaching brains and clearly said to send it. | write | OAuth |
| `search_phorme_programs` | Use this when the user asks for an existing coach-built training program for their sport or goal, for example a structured volleyball program. | read | none |
| `get_phorme_program` | Use this when the user picked one Phorme program and wants its details. | read | none |
<!-- tools:end -->

Full input and output schemas are in [`tools.json`](tools.json).

## What it will not do

- It shows no prices and takes no payments.
- It does not diagnose or treat. `find_clinic` finds a place to be seen and never asks about symptoms.
- It saves nothing without the person's confirmation, and it cannot delete or send training to someone else.

## For coaches, gyms and clinics

Coaches publish a coaching brain, and gyms and clinics publish their locations, through [phor.me/coach/build](https://phor.me/coach/build). Published partners are what this server's finders return. See [phor.me/for-coaches](https://phor.me/for-coaches) and [gyms.phor.me](https://gyms.phor.me).

## Support

- Support: [phor.me/support](https://phor.me/support) or support@phor.me
- Privacy: [phor.me/privacy](https://phor.me/privacy)
- Terms: [phor.me/terms](https://phor.me/terms)
- Issues with the server or these docs: open an issue here.

## License

The documentation and scripts in this repository are MIT licensed. The Phorme service, its content and its coaching brains are not.

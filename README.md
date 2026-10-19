# Phorme Training MCP server

Coach-built training for any AI assistant. Phorme Training is a remote [Model Context Protocol](https://modelcontextprotocol.io) server. An assistant can use it to find a coaching brain, program, race plan, gym class or sports clinic, preview workouts with exercise demos, and save training to the [Phorme](https://phor.me) app.

- **Endpoint:** `https://phor.me/api/mcp` (streamable HTTP)
- **Version:** <!-- version:start -->1.15.0<!-- version:end -->
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
| `find_coaching_brain` | Use this when the user wants a way to train for a goal or sport, for example "I want to get more explosive for basketball", "build muscle three days a week" or "train for a half marathon", or wants to train with a named coach, for example "train with Cameron Goodson", and has not picked a programme. | read | none |
| `find_gym_class` | Use this when the user wants a gym, studio or class to train at in person, for example "a strength class in Austin this week" or "a gym near me". | read | none |
| `book_gym_class` | Use this when a signed-in user wants a place in one class at a Phorme gym or studio. | write | OAuth |
| `cancel_gym_booking` | Use this when a signed-in user wants to give up a class they booked, are on the waitlist for, or asked a gym for on Phorme. | write | OAuth |
| `find_clinic` | Use this when the user wants to be seen in person by a physical therapist, sports medicine clinic, chiropractor, sports massage therapist or recovery studio, in a city they name or near a position they share. | read | none |
| `find_personal_coach` | Use this when the user wants a human coach of their own: 1:1 coaching, someone who writes their program for them, checks in each week, reviews how they move or answers their messages, for example "I want a real coach for basketball" or "can someone coach me one on one?". | read | none |
| `check_place_in_ai` | Use this when the owner or manager of a gym, studio, sports clinic or race asks whether ChatGPT knows their place or race or recommends it, for example "does ChatGPT recommend my gym?", "what does AI say about my physio clinic in Austin?" or "does ChatGPT know our triathlon?". | write | none |
| `find_exercise_swap` | Use this when the user needs a replacement for one exercise because they do not have the equipment, the station is taken, or they want a different option, for example no cable machine for cable rows. | read | none |
| `get_training_history` | Use this when the user asks about their own training logged in Phorme: what they did last time, how often they trained, their personal records, or a next workout built on their recent sessions. | read | OAuth |
| `get_lift_progress` | Use this when the user asks how one of their lifts is progressing or wants it graphed, for example "how is my bench going" or "chart my squat over six months". | read | OAuth |
| `get_planned_sessions` | Use this when the user asks what their Phorme plan has for today or the coming days, for example "what is my workout today". | read | OAuth |
| `get_my_coaching_business` | Use this when a Phorme coach asks about their own coaching brains: how many members train under each, who went quiet, what they have earned, and whether a note to members can go today. | read | OAuth |
| `start_my_coaching_brain` | Use this when a coach or trainer wants to turn their own method into a Phorme coaching brain and has none yet, or asks for a new one. | write | OAuth |
| `save_program_to_my_coaching_brain` | Use this when a Phorme coach has written a program in this conversation and clearly said to save it to one of their coaching brains. | write | OAuth |
| `send_note_to_my_members` | Use this when a Phorme coach has written a short note to everyone training under one of their published coaching brains and clearly said to send it. | write | OAuth |
| `get_gym_report` | Use this when a gym, studio or clinic owner asks about their own places on Phorme: what is listed, what is live, and how each place did, for example "how is my gym doing on Phorme?" or "did anyone book this week?". | read | OAuth |
| `create_or_claim_place` | Use this when a gym, studio or clinic owner wants their place on Phorme, for example after an AI check, or says "list my gym". | write | OAuth |
| `update_place` | Use this when an owner wants to change what their place's page says: name, address, hours, booking link, what kind of place it is, the line about it, its time zone, its phone, its price list or the email for requests. | write | OAuth |
| `set_class_schedule` | Use this when an owner wants to see, add, change or cancel a class at their place. | write | OAuth |
| `publish_place` | Use this when an owner wants their place live on Phorme: its page on phor.me, the app's map and the Phorme connector. | write | OAuth |
| `unpublish_place` | Use this when an owner wants their place off Phorme for now. | write | OAuth |
| `start_gym_brain` | Use this when an owner wants a coaching brain for their place, so members train with the gym's own coach in the Phorme app. | write | OAuth |
| `set_member_cover` | Use this when an owner on the gym plan wants to pay for their members' Phorme membership at one place, so members train free, or wants to stop. | write | OAuth |
| `list_held_requests` | Use this when an owner asks who wants to book or visit their place, for example "who asked to book this week?". | read | OAuth |
| `answer_held_request` | Use this when an owner wants to accept or decline one ask held for the plan at their place, by its hold_id. | write | OAuth |
| `claim_place` | Use this when an owner says a gym Phorme already lists is theirs and nobody runs it on Phorme yet, for example "that gym is mine". | write | OAuth |
| `verify_place_claim` | Use this when an owner has the six digit code Phorme sent to their place's own email or phone after they claimed it. | write | OAuth |
| `cover_member` | Use this when an owner on the gym plan wants to see who is covered or asked to be at one place, or to invite, approve or remove one member, for example "invite my member Sam to train free". | write | OAuth |
| `update_gym_brain` | Use this when an owner wants to change how their place's coaching brain sounds or looks: its name, its one line, its voice (how the coach talks to members), its method, its colour or its cover photo. | write | OAuth |
| `publish_gym_brain` | Use this when an owner wants the changes to their place's coaching brain to reach members, for example after its voice, look or programs changed. | write | OAuth |
| `set_booking_notices` | Use this when an owner wants booking and ask notices for a place sent somewhere else, for example "text my bookings to my phone". | write | OAuth |
| `get_gym_billing_link` | Use this when an owner on the gym plan wants to change the card, see invoices or change how many places the plan covers. | read | OAuth |
| `get_payouts` | Use this when an owner asks what Phorme paid them, or what goes out next, for example "what did Phorme pay my gym?". | read | OAuth |
| `get_payout_setup_link` | Use this when an owner wants their share paid to their bank and has not set it up, for example when no bank is set up yet. | write | OAuth |
| `set_owner_email` | Use this when an owner who signed in by phone wants notices about their gym plan sent to an email. | write | OAuth |
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

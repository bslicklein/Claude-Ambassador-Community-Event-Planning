# Claude Ambassador Community Event Planning

Seven Claude Code skills that run a Claude Community event end to end: sequence the
whole thing, decide who is in the room, build what gets presented, and produce every
printed artifact on brand and on the print vendor's spec.

**Start with `claude-and-coffee`.** It is the entry point for the event type and it
calls the other six at the moment each one is needed. The rest are usable alone if
you only want one artifact.

Built while running Claude Community events in New York City. Every number in here
came from an event that actually happened, and the parts that have not been
physically printed yet say so.

## The skills

| Skill | What it does | Vendor |
|---|---|---|
| `claude-and-coffee` | **The entry point.** 17 dated gates from T-42 to T+7, the format and budget decisions, copy kit, run of show, reimbursement. Scaffolds the event folder and reports status against what is actually on disk | |
| `event-attendee-research` | Deep-researches the registration list, scores it against a required room brief, allocates seats, pushes approvals to Luma, assigns workshop tables, writes personalized email | Luma |
| `claude-community-brand` | The official ambassador brand system: palette, fonts, spark, arch, globe, 13-icon library, and the recipe for drawing new on-style icons | — |
| `claude-community-deck` | The event keynote or welcome deck: 31 slide patterns, present mode, one-slide-per-page PDF export | — |
| `event-name-badges` | Print-ready name badges that land on the perforations, plus blanks for walk-ups | Staples |
| `event-welcome-board` | The 24×36 foam board on the easel at the door: greeting, run of show, wifi, QR | FedEx Office |
| `event-rollup-banner` | The tall retractable banner beside the door or behind the speaker | Vistaprint |

`claude-community-brand` is a dependency, not an option. The board and banner
generators read the palette, fonts, arch, globe, and icons from it, and fail loudly
rather than substituting a fallback typeface into a print file.

## Install

```
/plugin marketplace add bslicklein/Claude-Ambassador-Community-Event-Planning
/plugin install ambassador@ambassador-events
```

Private repository access rides on your existing GitHub credentials. Skills invoke
namespaced, for example `/ambassador:event-attendee-research`. Pull updates with:

```
/plugin marketplace update ambassador-events
```

## Running an event with these

```
/ambassador:claude-and-coffee
```

That skill scaffolds the event folder and drives the sequence. The order it enforces,
and the reason for each position:

| | Gate | Why here |
|---|---|---|
| T-42 | Date, format, Luma request | Format is a money decision, and Anthropic builds the page |
| T-35 | Venue with an **itemized** quote | A paid venue will not re-cut its invoice for you |
| T-28 | Page live, copy posted | Promotion needs a week minimum to fill a room |
| T-21 | Room brief locked | The research tool refuses to run without it |
| T-14 | Banner ordered | Vistaprint ships and cannot be rushed |
| T-10 | Research done, approvals pushed | Guests need time to put it in a calendar |
| T-7 | Deck | Built while the banner is in transit |
| T-5 | Tables, badges | The list is final later than you think |
| T-2 | Welcome board | Same-day turnaround, so the agenda can move until now |
| T+3 | Reimbursement | Payouts run Fridays |

`status.py` reports where an event actually is by looking for the artifacts on disk,
not by trusting ticked boxes, and warns when the venue quote crosses the tier cap.

## Lead times, which are the actual constraint

| Artifact | Vendor | Order by |
|---|---|---|
| Roll-up banner | Vistaprint, ships | 2 weeks out, tracked express inside 1 week |
| Name badges | Staples, in store | 3 days out, or same day if printing yourself |
| Welcome board | FedEx Office, in-store pickup | 24 hours out, collect the day before |

## Fonts

Three skills reference Anthropic display faces (`AnthropicSerifDisplay-Light`,
`AnthropicSansDisplay-Semibold`) and Copernicus. They travel with the skills for
ambassador use. This repository is private for that reason; do not make it public
without checking what those licenses permit.

## Attribution

Two skills are vendored here from their own repositories, so this plugin installs
as one piece. Update them upstream first, then sync the copy:

- `event-name-badges` — by Travis Johnson and the Claude Community Ambassadors,
  MIT licensed, from [travcjohnson/event-name-badges](https://github.com/travcjohnson/event-name-badges).
  Its `LICENSE` and `NOTICE` travel with it and govern that directory.
- `claude-community-brand` — also published standalone at
  [bslicklein/claude-community-brand](https://github.com/bslicklein/claude-community-brand).

`event-rollup-banner` renders through a generator adapted from the `flyer.html` in
the `claude-community-nyc` site repository, with asset paths rewritten to read from
the brand skill so it works installed.

## What is proofed and what is not

Print geometry is only as good as the sheet somebody held. Each skill marks which
of its sizes have been physically printed and which are derived by rule:

- Badges: Avery 74541 proofed 2026-07-23, Los Angeles Claude Conversation.
- Banner: 33×81 proofed at Claude & Coffee NYC, 2026-08-11. Other sizes derived.
- Welcome board: 24×36 built to the FedEx Office mounted-poster product. Other
  sizes derived.

When you print a new size, update the skill's table. That note is the whole value.

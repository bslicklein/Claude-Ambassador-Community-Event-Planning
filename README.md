# Claude Ambassador Community Event Planning

Six Claude Code skills that run a Claude Community event end to end: decide who is
in the room, build what gets presented, and produce every printed artifact on brand
and on the print vendor's spec.

Built while running Claude Community events in New York City. Every number in here
came from an event that actually happened, and the parts that have not been
physically printed yet say so.

## The skills

| Skill | What it does | Vendor |
|---|---|---|
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

Roughly four weeks out, in this order:

1. **Open registration**, then let it fill. Nothing below matters until there are
   more registrants than seats.
2. **`event-attendee-research`** — get the room brief from the host first, since the
   skill refuses to run without it. Research, rank, seat, approve, assign tables.
   This is the long pole; start it two weeks out.
3. **`event-rollup-banner`** — order first, it ships and cannot be rushed. Two weeks
   minimum.
4. **`claude-community-deck`** — build the deck while the banner is in transit.
5. **`event-name-badges`** — print once the list is final, which is later than you
   think. Buy 15% more stock than headcount.
6. **`event-welcome-board`** — last, deliberately. FedEx Office turns it around same
   day, so the run of show can keep moving until 24 hours out.

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

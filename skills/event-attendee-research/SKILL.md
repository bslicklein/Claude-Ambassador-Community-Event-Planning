---
name: event-attendee-research
description: Use when an event has more registrants than seats and someone has to decide who gets in — deep-researching a Luma or RSVP list, ranking or prioritizing attendees, working a waitlist, approving guests, assigning workshop tables or discussion groups, or writing personalized approval and day-before emails. Triggers on "who should we approve", "rank the waitlist", "research the attendees", "prioritize registrants", "group them into tables".
---

# Event Attendee Research

Turns a registration list into a defended seating decision: who gets in, who waits,
who sits with whom, and what to say to each of them.

**The failure this prevents:** approving off the registration CSV. The form's ceiling
is what someone typed in eight seconds on their phone, and senior people
under-describe themselves. On a 571-person run, "Meta · Manager" was the co-founder of
a USD 4.65B AI lab and "Columbia Business School" had built Claude's own NYC builder
community past 1,000 members. Both would have been buried. See
`reference/research-brief.md` for the full list.

Scale it to the event. A 40-person dinner needs the research pass and the flags, not
quotas and 25 tables.

## Deliverables

Everything lands in one event folder, `~/Documents/explanations/<YYYY-MM-DD-event>/`.

| File | What it is |
|---|---|
| `config.json` | **The room brief.** Personas, headcounts, industry mix, seats, caps |
| `roster.csv` | Every registrant with their form answers, straight from Luma |
| `research.jsonl` | One verified profile per line, the output of the research pass |
| `ranking.csv` | Everyone ranked, score broken into its six parts |
| `approve-list.csv` | `action=approve\|waitlist` rows, with the per-guest approval message |
| `workshop-groups.csv` | Table assignments |
| `emails.csv` | One personalized subject and body per attendee |
| `<date>-<event>-prioritization.html` | **The report the host actually reads.** |

## Workflow

### 1. Get the room brief. This is required input.

**Who belongs in the room is the host's decision, not the model's.** `score.py` refuses
to run without personas rather than quietly applying a default mix. Read
`reference/room-brief.md` and ask all of it in one message, using `AskUserQuestion` with
the persona library as the options:

1. **Which personas?** Founder, operator, community operator, amplifier, investor,
   senior enterprise, technical builder, emerging talent, academic, press, domain
   specialist, and custom ones. `score.py --list-personas` prints the library.
2. **How many of each?** Headcount or percentage. Targets are floors, not caps; add a
   `cap` for any persona that could crowd out the room.
3. **Which industries, and what mix?** Floors and ceilings. Technology self-selects into
   these events and will take most of the room unless capped.
4. **What background?** "People who actually build", "nobody below manager", "real
   companies not side projects" — all expressible as match rules, table in the reference.
5. **How much social and community presence?** Two separate numbers: amplifiers who
   post about it, and community operators who bring their room to yours. This is 40 of
   the 122 points, so an unstated answer here decides the event by accident.

Also settle: **how many seats and how firm**, **forced invites** (referrals, VIPs,
co-hosts go in `force.txt` and are seated regardless of score), and **who is already
approved** (scored anyway for the tables and the report, Luma status never touched).

The answers become `config.json`. Read the worked example in `reference/room-brief.md`.

### 2. Pull the roster

```bash
S=~/.claude/skills/event-attendee-research
python3 $S/scripts/luma_guests.py --list                       # find the event id
python3 $S/scripts/luma_guests.py --event evt-xxxx --out roster.csv
```

Every registration question becomes its own column. A Luma CSV export or a Google Form
dump works too; it only needs an `email` column and, for the Luma push later, a
`guest_id`.

A 403 means the API key is scoped to a different calendar than the event, not that the
key is bad.

### 3. Structured pass, then pressure-test the brief against the pool

```bash
python3 $S/scripts/score.py --roster roster.csv --personas library --seats 100 --out .
```

Run it once with no research, using the whole persona library, to get the shape of the
pool. Two things to read:

- **If seniority is flat across the board**, the role column was not detected. Fix it
  with `"columns"` in `config.json` rather than accepting the output.
- **If a persona has fewer people in the pool than the host asked for**, the brief
  cannot be satisfied and the host needs to hear it now, before 240 profiles get
  researched. The fix is recruiting, not ranking.

### 4. Deep research the plausible top

**This is the step that earns the ranking.** Read `reference/research-brief.md` in full
and follow it. Dispatch parallel research agents, roughly 20 people each, over everyone
within reach of the seat cut plus a margin — 238 researched for 100 seats on the run
this came from. Each agent returns one JSON object per line into `research.jsonl`.

Three rules that came out of getting it wrong the first time:

- **Give agents a stated per-person search budget and require them to report hitting
  it.** A shared budget silently ran out mid-pass and 101 profiles came back "low
  confidence", which is indistinguishable from nobody having looked.
- **Re-run every low-confidence profile with a raised cap.** 69 of 101 upgraded on the
  second pass, including the highest-value person in the batch. This is not optional.
- **A failed search is never reported as absence.** "Could not confirm", not "does not
  exist".

### 5. Score with research, allocate seats

```bash
python3 $S/scripts/score.py --roster roster.csv --research research.jsonl \
    --config config.json --seats 100 --force force.txt --out .
```

122 points across influence, seniority, company substance, notability, Claude Code
depth, and focus vertical, then allocation against the brief: forced invites, persona
floors, industry floors, then the highest remaining scores, with per-persona,
per-industry, and per-company caps enforced throughout. The rubric and the founder check
are in `reference/scoring.md`.

Read the **"room, against the brief"** table in `summary.txt` back to the host every
run — asked, seated, and available in the pool, side by side. It also warns when someone
inside the seat cut has no research behind them. Those are the most likely misses;
research them before going further.

### 6. Workshop tables

```bash
python3 $S/scripts/tables.py --ranking ranking.csv --size 6 --out .
```

Industry cluster, then role level, then skill **seeded, not sorted**. Sorting by skill
puts every beginner at one table with nobody able to help them; that table stalls and
the room splits into a fast half and a stuck half. Seeding guarantees a helper at every
table while keeping peers at the same altitude. Target: every table has a builder, and
average role spread near 1 tier.

### 7. Write the report, then stop

Build the HTML decision report per `reference/report.md` and `open` it. Read the flags
section back to the host: competitors in the pool, unverifiable founders, approved
people with no research, unfilled quotas.

**Nothing has been sent yet, and nothing should be until the host has read this.**
Never publish this report as a shareable artifact — it holds verdicts on named private
individuals.

### 8. Push decisions to Luma

Write a per-guest `message` into `approve-list.csv` first — one line drawn from that
person's research, plus their table number. It is the difference between a form letter
and being recognized.

```bash
python3 $S/scripts/luma_status.py --csv approve-list.csv --event evt-xxxx            # dry run
python3 $S/scripts/luma_status.py --csv approve-list.csv --event evt-xxxx --go --limit 5
python3 $S/scripts/luma_status.py --csv approve-list.csv --event evt-xxxx --go
python3 $S/scripts/luma_status.py --csv approve-list.csv --event evt-xxxx --action waitlist --go
```

Every status change emails the guest. Dry run is the default, always send five first,
and sent ids are logged so a partial run resumes safely. Luma caps the message at 200
characters.

### 9. Personalized email

Build `emails.csv` (`name,email,table,hook,subject,body`) with a hook per person from
their research, then:

```bash
python3 $S/scripts/send_emails.py --csv emails.csv --from you@example.com --draft --limit 3
python3 $S/scripts/send_emails.py --csv emails.csv --from you@example.com --draft
python3 $S/scripts/send_emails.py --csv emails.csv --from you@example.com --go
```

Drafts first, every time. Read ten of them before any of it leaves the building.

### 10. Hand off to the room

`ranking.csv` now carries `workshop_table`, which feeds the physical artifacts:
`event-name-badges` for badges, and `claude-community-brand` for table cards and signage.

## Standing rules

- **Research is a claim-checking exercise, not a background check.** Verify what
  someone says about their professional life. Nothing about their personal life, and
  nothing that is not already public and professional.
- **Identity discipline above all.** Confirming the wrong person of the same name is
  the most expensive error in the pipeline. Anchor on the LinkedIn URL, email domain,
  employer, or city, and reject the match otherwise.
- **The model ranks, the host decides.** The persona mix is the host's call and is
  required input. Competitors, unverifiable founders, and anyone the research made look
  bad go to a human, never straight to a rejection.
- **Every send is dry-run first, then a small batch, then the rest.** Approvals and
  emails are not reversible.
- Re-running `score.py` is free and rewrites nothing that was sent. Re-run it whenever
  new research lands, right up until the push.

## Part of a bigger sequence

This skill produces one artifact. `/ambassador:claude-and-coffee` owns the order the
artifacts get made in, the gates that block, and the reimbursement rules, and calls
this one at the right moment. Use it when running a whole event rather than making a
single thing.

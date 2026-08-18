---
name: claude-and-coffee
description: Run a Claude & Coffee or other Claude Community ambassador event end to end. The main entry point for this event type. Use when planning, scheduling, or running an ambassador event, checking what is still outstanding on one, deciding a format, writing the Luma and LinkedIn copy, or closing one out and claiming reimbursement. Routes to the attendee-research, deck, brand, badge, welcome-board, and banner skills at the right moment. Triggers on "claude & coffee", "claude and coffee", "plan the event", "run an event", "ambassador event", "what's left for the event", "event status", "close out the event".
---

# Claude & Coffee

The event type, end to end. This skill owns the **sequence, the gates, and the
money**. The six specialist skills own the artifacts, and this one calls them at
the moment they are actually needed.

**The failure this prevents:** every individual artifact being excellent and the
event still going badly, because the venue invoice was a lump sum, the Luma page
went up nine days out, or a $1,110 overspend had no pre-approval behind it. Those
are all sequencing failures. That is what this skill is.

## Start here, always

```bash
S=<this skill>
python3 $S/scripts/new_event.py --date 2026-10-06 --venue "Georgie's, 182 Broome St" --seats 100
python3 $S/scripts/status.py --event <folder>          # any time after
```

`new_event.py` creates the event folder, `event.json`, and a `CHECKLIST.md` with
every gate dated off the real event date. **`event.json` is the brief every other
skill reads.** Keep it current; it is the whole reason this is one skill and not
six.

`status.py` reads the folder and reports what is done, due, overdue, and blocking,
by looking for the actual artifacts rather than trusting ticked boxes. Run it at
the top of any conversation about a live event, before answering anything else.

## The timeline

Seventeen gates. Eight of them block. Full text with the reasoning lives in
`scripts/timeline.py`, which is also what generates the checklist.

| When | Gate | Skill |
|---|---|---|
| T-42 | Date, format, and topic chosen · **blocking** | |
| T-42 | Luma event requested from Anthropic · **blocking** | |
| T-35 | Venue confirmed with an **itemized** quote · **blocking** | |
| T-35 | Pre-approval, if the quote exceeds the cap | |
| T-28 | Luma page live, copy kit posted · **blocking** | `reference/copy-kit.md` |
| T-21 | Room brief locked with the host · **blocking** | `event-attendee-research` |
| T-14 | Roll-up banner ordered | `event-rollup-banner` |
| T-10 | Deep research done, approvals pushed · **blocking** | `event-attendee-research` |
| T-7 | Deck built | `claude-community-deck` |
| T-5 | Workshop tables assigned | `event-attendee-research` |
| T-5 | Name badges printed | `event-name-badges` |
| T-2 | Welcome board ordered | `event-welcome-board` |
| T-1 | Day-before emails sent, print collected | `event-attendee-research` |
| T-0 | Run of show | `reference/run-of-show.md` |
| T+1 | Itemized invoices collected, tab settled · **blocking** | |
| T+3 | Reimbursement submitted · **blocking** | `reference/budget.md` |
| T+7 | Recap posted, roster filed | |

**Why the order is what it is:** the things that depend on other people go first
(Anthropic builds the Luma page, the venue cuts the invoice, Vistaprint ships).
The things you control go last, so the run of show can keep moving until 24 hours
out. The welcome board is deliberately the final artifact, because FedEx Office
turns it around same day and the agenda always changes.

## The four decisions this skill exists to force

1. **Format, at T-42.** A Workshop carries $50 of attendee credits per person and
   a Meetup does not, and it cannot be reclassified later. Ask what people will
   actually be doing for the middle ninety minutes, then pick. See
   `reference/program-rules.md`.
2. **The itemized invoice, before booking.** Space rental separated from food and
   beverage. A venue that has already been paid has no reason to re-cut it, and
   reimbursement covers only venue, refreshments, and printed assets.
3. **The room brief, at T-21.** Who belongs in the room is the host's decision.
   `event-attendee-research` refuses to run without it, by design.
4. **Whether to run at all.** Two events forty-eight hours apart split one
   audience. If the venue is not confirmed with a week of promotion left,
   **postponing beats a thin room**. Say this out loud rather than quietly
   compressing the timeline.

## Money

Read `reference/budget.md` before quoting anything to a venue. The short version:

- Tier A caps: $750 under 40 attendees, $1,125 to 70, **$1,500 above 70**,
  $5,000 for an Impact Lab.
- Covered categories are exactly three: **venue, refreshments, printed assets.**
- Over the cap needs written pre-approval from community@anthropic.com **before**
  the spend. On 2026-08-11 that step was skipped and roughly $1,110 of $2,705 was
  unrecoverable.
- Submit via Typeform, access code 419736. **Payouts run Fridays**, which is why
  the gate is T+3 and not "soon".
- `status.py` warns automatically once `venue.quoted_total` exceeds the cap or the
  itemized invoice flag is still false.

## Running it as a conversation

When asked about a live event, in this order:

1. `status.py` first. Lead with what is blocking, not with what is done.
2. Answer the actual question.
3. Name the next gate and its date. One line, not a re-plan.

When asked to start one, ask only what `new_event.py` needs (date, venue, seats,
format), scaffold it, and then walk to the first blocking gate. Do not ask about
badges in the first conversation; that is five weeks away and asking makes the
whole thing feel heavier than it is.

## Standing rules

- **"Claude Community Ambassador for New York City."** Never "Community Leader".
  It has shipped wrong in published copy before. Check every bio and slide.
- **No speaker promotion before the event.** Program rule, protects people from
  schedule changes. Credit them generously in the T+7 recap instead.
- No em dashes in any copy. Commas, colons, periods.
- The four NYC verticals are fintech, legal, private equity, and education. Note
  when a quarter has served only one of them; that gap is the next event's brief.
- Every artifact skill fails loudly rather than substituting a fallback font into
  a print file. If one complains about `claude-community-brand`, install it rather
  than working around it.

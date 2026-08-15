# The composite score

122 points. `score.py` implements all of it; this file is why each number is what it is.

| Component | Max | Built from |
|---|---|---|
| Influence | 40 | Social reach (26) + community leadership (18), capped at 40 |
| Seniority | 30 | Verified title band + company size + brand anchor |
| Company substance | 24 | Funding stage + revenue signal |
| Researcher notability | 12 | Overall human read, scaled down from 0-10 |
| Claude Code depth | 10 | Tiebreaker only, never a driver |
| Focus vertical | 6 | The verticals this event is actually for |

**Influence carries the most weight on purpose.** Claude Code depth is worth 10 against
influence's 40, so a daily power user with no audience and no team ranks below a
mid-level operator who runs a 1,500-person meetup. For an event whose purpose is
community growth, that is the correct trade. If the event's purpose is different, say a
closed technical working session, re-weight before the first run rather than arguing
with the output afterwards.

## Sub-scales

**Social reach** → `none 0 · unknown 2 · small 8 · medium 18 · large 26`
**Community leader** → `yes 18`, capped with social at 40.

**Title band** → `executive 14 · founder 13 · vp 12 · director 11 · senior manager 9 ·
manager 8 · mid 6 · early 4 · student 2`. Detected from the verified title first, the
self-reported role only as a fallback.
**Company size** → `5000+ 8 · 501-5000 6 · 51-500 4 · under 50 2`
**Brand anchor** → `+8` when the verified employer matches the recognizable-employer
list. Extend it per event with `"brands"` in config; a name that means something in
your city is worth more than a global logo nobody in the room works with.

**Company stage** → `none 0 · side-project 1 · unknown 4 · bootstrapped 8 ·
agency 8 · pre-seed 8 · seed 11 · public 12 · series-a 13 · series-b+ 14 · growth 14`
**Revenue** → `none 0 · unknown 3 · early 5 · meaningful 8 · substantial 10`

**Claude Code depth** = experience (`daily 5 · regular 4 · occasional 2 · new 1`) +
proficiency (`agents on loops 5 · super technical 5 · own skills and connectors 4 ·
projects and skills 3 · casually prompting 1 · novice 0`). Also drives `is_builder`,
which the table seeding depends on.

## The founder check

A self-declared founder title is a claim to verify, not a fact. 133 of 571 registrants
claimed one.

```
Claims "Founder"
  ├─ Series A or later, or real revenue      → 17 pts, ranked as a genuine operator
  ├─ Early stage, or could not be confirmed  → 13 pts, benefit of the doubt kept
  └─ Confirmed side project or no company    →  5 pts, demoted and flagged
```

**The demotion only fires on a confident negative.** Where research simply could not
confirm a company, the person keeps their founder points, because a failed search is
not evidence of a fake company. The flagged list goes to a human, it does not go to a
rejection. On the 518-person run, 21 founders had no discoverable company; several were
actively contradicted by public record, and several others turned out to be real
builders with a pre-launch product.

## Seat allocation

Personas come from the room brief, which is required input — see
`reference/room-brief.md`. Each person is assigned to the **first** persona they match,
so the list is a priority order and nobody counts twice.

Score ranks **within** a persona. The brief decides how many seats each persona gets.
Allocation runs in four passes, with caps enforced in all of them:

```
forced invites  →  persona floors  →  industry floors  →  highest remaining scores
```

**The mix guardrail matters as much as the ranking.** Without floors, the top of a raw
score list is almost entirely one kind of person. Caps do the opposite work: a
**two-per-company cap** stops one employer taking over, a persona cap stops students
crowding out the room, an industry cap stops technology eating 60% of the seats.

**Unfillable floors spill, they never sit empty.** On one run a floor of 22 senior
enterprise could only be filled 7 deep, because only 7 registrants were director-level
or above at a company of 501+. The other 15 seats flowed to the next-highest scores and
the summary said so. When that happens, supply is the binding constraint, not the model,
and the answer is recruiting rather than re-ranking.

## Config

`score.py --dump-config` prints the defaults. Override in a `config.json`:

```json
{
  "seats": 100,
  "company_cap": 2,
  "focus_verticals": ["fintech", "legal", "private equity", "edtech"],
  "personas": [
    {"name": "Community operator", "target": 20, "match": {"community_leader": "yes"}},
    {"name": "Emerging talent", "target": 6, "cap": 10, "match": {"role_level": ["student", "early"]}},
    {"name": "Practitioner", "match": {}}
  ],
  "industry_targets": {"Financial Services": 20},
  "industry_caps": {"Technology": "45%"},
  "brands": ["Rihs Ventures", "Newlab", "dbt Labs"],
  "weights": {"influence": 40, "seniority": 30, "substance": 24,
              "notability": 12, "depth": 10, "vertical": 6},
  "columns": {"role": "What best describes your role?"}
}
```

`personas` is required. The full set of match fields and value forms is in
`reference/room-brief.md`.

`columns` is only needed when auto-detection misses a form question. Run `score.py`
once and read the summary: if seniority looks flat across the board, the role column
was not found.

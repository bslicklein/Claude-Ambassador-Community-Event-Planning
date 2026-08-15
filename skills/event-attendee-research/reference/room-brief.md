# The room brief

**Required input. The skill does not run without it.** `score.py` exits with
instructions if `personas` is empty, on purpose: who belongs in the room is the host's
decision, and a default persona mix is that decision made silently by a model.

A ranking answers "who is most impressive." A brief answers "who is this room for."
They are different questions, and only the second one produces a good event. Twenty
impressive people who all do the same job is a bad room.

## Ask these five, together, in one message

Use `AskUserQuestion` with the persona library as multi-select options, then follow up
on the numbers. Do not proceed on assumptions for any of them.

### 1. Which personas do you want in the room?

Multi-select from the library (`score.py --list-personas`):

Community operator · Amplifier · Verified founder · Early-stage founder ·
Senior enterprise · Name-brand operator · Technical builder · Investor · Operator ·
Domain specialist · Academic or educator · Press or creator · Emerging talent ·
Practitioner

Take custom ones too. "Compliance officers", "people who have shipped an agent to
production", "solo consultants" are all expressible — see *Writing a custom persona*.

### 2. How many of each?

A headcount or a percentage of seats. **Targets are floors, not caps.** A floor of 20
community operators means at least 20; if 45 rank high enough, 45 get in. Add `cap`
when a persona can crowd out the room, which is most often Emerging talent (cheap to
seat, and a room of students is a different event than the one being planned).

Say plainly that floors are not guarantees: an unfillable floor spills to the next
highest scores and the summary reports it. On one run a floor of 22 senior enterprise
could only be filled 7 deep, because only 7 such people had registered.

### 3. Which industries, and what mix?

Floors and ceilings on `industry_cluster`, separate from personas so the two dimensions
can be balanced independently. The common ask is a ceiling: technology self-selects into
these events and will take 60% of the room unless capped.

Clusters: Technology · Financial Services · Legal · Education ·
Media, Marketing & Creative · Consulting & Professional Services · Healthcare · Other

### 4. What background matters?

Not a separate config key — it is expressed through persona match rules, so ask in
plain language and translate:

| The host says | The rule |
|---|---|
| "people who actually build, not just talk" | `{"is_builder": "yes"}` |
| "senior people, not juniors" | `{"role_tier": {"min": 4}}` |
| "nobody more junior than manager" | put a persona with `{"role_tier": {"max": 3}}` and `"cap": 0` |
| "real companies, not side projects" | `{"company_stage": {"not": ["none", "side-project"]}}` |
| "revenue-generating businesses" | `{"revenue_signal": ["meaningful", "substantial"]}` |
| "lawyers" | `{"industry_cluster": "Legal"}` |
| "people who have run a team" | `{"role_level": ["vp", "director", "senior_manager", "manager"]}` |

### 5. How much social and community presence?

The most commonly under-specified input, and the one that most changes the output,
because influence is 40 of the 122 points.

Ask for two numbers: **how many amplifiers** (people with a real audience, `social_reach`
of medium or large) and **how many community operators** (people who run something).
They are different assets. An amplifier posts about the event; a community operator
brings their room to yours and co-hosts the next one.

If the host wants neither, say so out loud and re-weight before the first run: with
influence at 40, the default rubric will fill the room with creators regardless of what
the personas say. For a closed technical working session, drop influence to 15 and move
those points to Claude Code depth.

## Order matters

A person is assigned to the **first** persona they match, so the list is a priority
order. A founder with 30K followers who also runs a meetup is one person and occupies
one seat; the order decides which floor they count against. Put the scarcest and most
specific personas first, and the catch-all last.

**Always end with `{"name": "Practitioner", "match": {}}`** unless you want people
matching nothing to land in `Unassigned`, where they can be seated only by raw score.
`score.py` warns when the last persona has match rules.

## Writing a custom persona

```json
{"name": "Shipped to production", "target": 12, "cap": 30,
 "match": {"is_builder": "yes", "company_stage": {"not": ["none", "side-project"]}}}
```

Every rule must pass. Fields available: `role_level`, `role_tier`, `role_band`,
`founder_check`, `company_size_pts`, `brand_anchor`, `is_builder`, `social_reach`,
`community_leader`, `industry_cluster`, `company_stage`, `revenue_signal`,
`research_confidence`, `score`, and the six score components. Plus `title_match`, a
regex over the verified title and the self-reported role.

Value forms: a list (membership), a string (single value), `{"min": n}` / `{"max": n}`,
`{"any": true}` (non-empty), `{"not": [...]}`.

## Sanity-check the brief before researching

Run `score.py --personas library` on the unresearched roster first. It costs nothing and
shows what the pool can actually supply. **If a persona has fewer people in the pool
than the host's floor, the brief cannot be satisfied and the host needs to hear that
now**, not after 240 profiles have been researched. The fix is recruiting, not ranking:
a personal invite to the people the brief wants and the registration list does not have.

One thing to expect and to say out loud before it alarms anyone: **on the pre-research
run, every research-dependent persona reads zero.** Community operator, Amplifier, and
Verified founder are all populated by fields that only exist after the research pass.
Before research, the only personas with anyone in them are the ones the form can see.
That gap is the argument for the research pass, stated in numbers.

## Worked example

> 100 seats, Claude & Coffee, community growth. 20 community operators, 10 amplifiers,
> 15 verified founders, 12 senior enterprise, 4 investors. Cap students at 10. Cap
> technology at 45%, floor financial services at 20 and legal at 5.

```json
{
  "seats": 100,
  "company_cap": 2,
  "industry_targets": {"Financial Services": 20, "Legal": 5},
  "industry_caps": {"Technology": "45%"},
  "personas": [
    {"name": "Community operator", "target": 20, "match": {"community_leader": "yes"}},
    {"name": "Amplifier", "target": 10, "match": {"social_reach": ["medium", "large"]}},
    {"name": "Verified founder", "target": 15, "match": {"founder_check": "verified"}},
    {"name": "Senior enterprise", "target": 12,
     "match": {"role_tier": {"min": 5}, "company_size_pts": {"min": 6}}},
    {"name": "Investor", "target": 4,
     "match": {"title_match": "(general |managing )?partner|venture|investor|\\bvc\\b|angel"}},
    {"name": "Operator", "target": 15,
     "match": {"role_level": ["vp", "director", "senior_manager", "manager"]}},
    {"name": "Emerging talent", "target": 6, "cap": 10,
     "match": {"role_level": ["student", "early"]}},
    {"name": "Practitioner", "match": {}}
  ]
}
```

Read the "room, against the brief" table in `summary.txt` back to the host every run.
Asked, seated, and available in the pool, side by side, is the whole conversation.

# The research brief

The deep-research pass is where this whole workflow earns its keep. On the 571-person
run it moved people more than a hundred positions in both directions relative to what
the registration form alone produced.

## Why the form cannot be trusted

Every one of these was a real registration, verbatim, from one event:

| What they wrote | What they actually are |
|---|---|
| "Meta · Manager" | Co-founder of an AI lab that raised $650M at a $4.65B valuation |
| "Columbia Business School" | Built Claude's own NYC builder community past 1,000 members |
| "NYC · Director" | Forbes 30 Under 30 GP at an active pre-seed fund, 50+ investments |
| "Commodity Trader" | 15-year ESG executive, former VP of ESG at a public firm |
| "NA" | Formerly ran operations for a NYSE-listed company |

Senior people under-describe themselves. The form's ceiling is what someone typed in
eight seconds on their phone. **Ranking on self-report systematically buries your best
guests**, and it does it silently.

## Run shape

Dispatch parallel research agents, roughly **20 people per agent**. Twelve agents
covered 238 profiles comfortably. Give each agent the full brief below plus its slice
of the roster, and have it return one JSON object per line.

Research the **plausible top** first, not everyone. Score the whole roster on the
structured pass, then research everyone within reach of the seat cut plus a margin
(the 571-person run researched 238 for 100 seats). Anyone unresearched inside the
cut is a likely miss — `score.py` warns about exactly this.

### Search budget

Agents share a search-call budget. On the first run it was exhausted mid-pass and 101
profiles came back "low confidence", which is indistinguishable from "nobody looked."
**Give the agents a stated per-person call budget (4 to 6 searches) and require them
to report when they hit it**, then re-run every low-confidence profile with a raised
cap. On the re-run, 69 of 101 upgraded. That second pass is not optional.

---

## Brief to give each research agent

> You are researching registrants for an invite-only event so they can be ranked and
> seated. For each person below you get their name, email, and whatever they typed on
> the registration form (organization, role, LinkedIn URL if provided).
>
> For each person, find and verify: their actual current title and employer; whether
> any company they claim to have founded genuinely exists and how substantial it is;
> the size of any public audience they have; and whether they organize, host, teach,
> or lead a community.
>
> **Identity discipline.** The single most expensive error is confirming the wrong
> person. A well-known person often shares a name with your registrant. Anchor on the
> LinkedIn URL they supplied, the email domain, the employer they named, or the city.
> If you cannot tie a public profile to this specific registrant, do not use it, and
> say in the note that the match was rejected. A malformed or unresolvable LinkedIn
> URL is a common cause and is worth reporting as such.
>
> **A failed search is not evidence of absence.** If you cannot confirm a company,
> record that you could not confirm it. Only claim a company does not exist when the
> search actively contradicts the claim, for example public record attributes that
> company to a different founder, or the named organization has no web presence at all
> across several distinct search framings.
>
> **Absence of a public footprint is a finding, not a gap.** "Engineering manager at a
> public company with essentially zero public presence" is a complete, useful answer.
> Write it as one.
>
> Budget roughly 4 to 6 searches per person. If you run out before you are confident,
> mark `research_confidence: "low"` and say what you were still missing. Do not guess
> to fill a field.
>
> Return one JSON object per line, no prose around it:
>
> ```json
> {"email": "...", "verified_title": "", "verified_company": "",
>  "company_stage": "none|side-project|bootstrapped|agency-or-consultancy|pre-seed|seed|series-a|series-b+|growth|public|unknown",
>  "revenue_signal": "none|early|meaningful|substantial|unknown",
>  "social_reach": "none|small|medium|large|unknown",
>  "social_detail": "platform-by-platform, with follower counts and what they post about; say plainly when nothing was found",
>  "community_leader": "yes|",
>  "community_detail": "what they organize, host, teach, or lead, and how big it is",
>  "notability": 0,
>  "industry_cluster": "Technology|Financial Services|Legal|Education|Media, Marketing & Creative|Consulting & Professional Services|Healthcare|Other",
>  "research_confidence": "high|medium|low",
>  "note": "one or two sentences a host could read at a glance before shaking this person's hand"}
> ```

## Field rules

**social_reach** counts a real audience the person owns, across X, LinkedIn, Instagram,
YouTube, TikTok, Substack, and podcasts. Bands: `small` under 5K, `medium` 5K to 50K,
`large` above 50K. A LinkedIn connection count is not an audience. Unverifiable
accounts under the same name go in `social_detail` as UNCONFIRMED and do not raise the
band.

**community_leader** is `yes` only for organizing, hosting, teaching, running a meetup
or chapter, developer relations, conference speaking, or maintaining a used open-source
project. Attending things is not leading them. This flag is worth 18 points and is the
main lever that lifts cross-promotion partners to the top, so hold the line on it.

**notability** (0 to 10) is the researcher's overall human read, deliberately scaled
down to 12 points so it informs the ranking without overriding it. Use it for the
things the structured fields miss: a Forbes 30 Under 30, a former FAIR research
director, a tool with 27K GitHub stars.

**note** is written for the host, not the model. It ends up in the approval message,
on the table card, and in the day-before email.

## Deliverables from the pass

- `research.jsonl`, one object per line, joined to the roster on email
- A list of every **low-confidence** profile, for the mandatory second pass
- A list of every **self-declared founder whose company could not be confirmed**.
  They keep their points, and a human glances at the list. On the 518-person run this
  was 21 people, several actively contradicted by public record.
- A list of **direct competitors** in the pool. That is a judgment call for the host,
  not a scoring problem, and it must be surfaced before anything is sent.

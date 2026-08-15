# Writing style

The voice of the deck is a practitioner talking to peers who are good at their
jobs and busy. It respects the audience enough to be blunt and never sells.

## The rules

**Second person, present tense.** "You are the one who checks the output," not
"users must verify outputs." The deck is addressed to one person in the room.

**Short declaratives.** Most sentences land under twenty words. A long sentence
is allowed when it is doing real work, and it is always followed by a short one.

**Antithesis is the house figure.** Two clauses, parallel shape, opposite
content. It is what makes lines memorable enough to repeat in a hallway.

> A prompt is a peak. A system is a floor.
> A schedule fires on the clock. An agent fires on the world.
> Automation does not remove the thinking. It moves it.

Use it in headlines and callouts. Do not use it three slides in a row; it stops
sounding like a discovery and starts sounding like a slogan generator.

**Concrete nouns and real numbers.** "Ten to twenty genuine inputs" beats "a
sufficient sample." "Roughly the fifth run" beats "over time." If a claim cannot
be made concrete, it probably is not worth a slide.

**Name the failure mode the audience has lived.** "The vague paragraph you would
have let through at 6pm." "The question you are embarrassed to ask." Specific
recognition earns more trust than any credential.

**Diagnose, do not scold.** The wrong belief gets stated in the audience's own
words and then shown to be a ceiling, never mocked. Anyone who holds it should
feel understood, then upgraded.

**Give the honest caveat.** Every strong claim gets its cost named on the same
slide or the next one: the setup tax, the hard part, the thing that expires.
Credibility comes from the caveats.

**End on a consequence.** The callout is not a summary. It is the sentence the
audience should leave with, and it usually names something they can check
tomorrow. "If you have explained the same preference three times, stop
explaining it. That is a skill."

## Banned

- Em dashes. Use commas, colons, or periods. This is a standing rule across all
  of Brandon's output.
- Emojis and exclamation marks.
- Any sales language. No pricing, no services, no "reach out." The community is
  free, and the deck says so out loud.
- Client names. Anonymise to "a law firm", "an investment team", "a school".
- Jargon that needs its own definition: leverage, synergy, unlock, supercharge,
  game-changer, revolutionize, seamless, robust.
- Hedges: arguably, essentially, basically, in many ways, it could be argued.
- Rhetorical questions in headlines. The checklist slide is the one exception,
  because those questions are for the audience to answer, not the presenter.
- "Not X, but Y" constructions. State Y. If the contrast matters, give X its own
  sentence.

## Per-element word budgets

| Element | Budget | Note |
|---|---|---|
| `.kicker` | 2 to 5 words | Labels the slide's job. Middle dot to sub-label: "Organ one · Skills" |
| `h1` | 1 to 4 words | Title, close, section dividers only |
| `h2` | 4 to 12 words | A claim, not a topic |
| `.lede` | 1 to 2 sentences | The frame. Cut the second sentence first when tight |
| `.tile p` / `.card p` | Under 35 words | Two sentences |
| `.callout` | 1 to 2 sentences | The consequence. One per slide |
| `table.cmp` cell | 3 to 8 words | Phrases, never sentences |
| `.pmx .cell` | 3 to 5 words | Fragments |
| `.def .plain` | Under 10 words | A metaphor a child would follow |
| `.cap` | 1 to 2 sentences | Says what to notice, not what is shown |
| SVG `.txt` | 4 words per line | Break manually across `<text>` elements |

## Titles

The deck title is two or three words, works as an imperative or a noun phrase,
and can be said twice: once on the title slide as a promise, once on the close
slide as a conclusion. *Keep Thinking* is the model. Test it by writing the
close slide's sentence first. If the title cannot carry that sentence, it is not
the title.

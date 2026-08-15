# claude-community-brand

A Claude Code skill for Claude Community ambassadors: the official brand
system (palette, fonts, spark / arch / globe assets) plus a 13-icon library
and the exact recipe for drawing new event-topic icons in the kit's
hand-drawn ink style.

Built by Brandon Slicklein, Claude Community Leader, New York City.

## Install

```bash
git clone https://github.com/bslicklein/claude-community-brand.git ~/.claude/skills/claude-community-brand
```

Then ask Claude Code to "make a poster for my Claude event" or "draw a
fintech icon in the community style" and it takes it from there.

## What's inside

- `SKILL.md` — palette and type tokens, the three canonical compositions
  (event poster, community lockup, half-globe edge crop), generator recipes,
  and print specs for banners, posters, and badges
- `assets/fonts/` — Anthropic Serif Display Light + Anthropic Sans Display Semibold
- `assets/brand/` — spark (ivory and ink), the arched "CLAUDE COMMUNITY"
  wordmark, the community globe, and the official reference lockup
- `assets/icons/` — the four official kit icons (meetup, conversation,
  workshop, impact-lab) plus nine drawn to match: coffee, finance, legal,
  healthcare, education, real-estate, developer, marketing, retail
- `reference/icon-style.md` — the full icon spec: stroke weights, ivory
  fills, and the mandatory hand-drawn wobble
- `templates/icon-proof.html` — self-contained proof sheet; render any new
  icon on clay next to the official ones before shipping it

## Icon style in one line

`viewBox 268×252`, ink `#141413` strokes at width 8–10 with round caps,
ivory `#FAF9F5` fills, and no straight lines anywhere — every edge is a
gently wobbling curve, which is what makes it read as the official kit.

Brand assets belong to Anthropic and are for Claude Community ambassador
use. Keep events free and open.

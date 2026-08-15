---
name: claude-community-brand
description: Use when creating any Claude Community / Claude Ambassador branded artifact — event posters, flyers, banners, social squares, name badges, stickers — or when a new event topic or business industry needs an icon in the official kit's hand-drawn style (like the coffee mug made for Claude & Coffee). Carries the official palette, fonts, spark/arch/globe assets, a 13-icon library, and the exact recipe for drawing new on-style icons.
---

# Claude Community Brand

Official Anthropic Claude Community ambassador brand system, self-contained.
Everything travels with this skill; the canonical generators live in the
`claude-community-nyc` repo (see Generators below).

## Palette and type

| Token | Value | Use |
|---|---|---|
| Clay | `#D97757` | Background of nearly every artifact |
| Ink | `#141413` | Icon strokes, serif headlines on clay |
| Ivory | `#FAF9F5` | Icon fills, sans text on clay, light backgrounds |

- **Serif display** (`assets/fonts/AnthropicSerifDisplay-Light-Static.otf`) —
  city names and headline words ("New York", "Welcome"). Letter-spacing -0.01em.
- **Sans display semibold** (`assets/fonts/AnthropicSansDisplay-Semibold-Static.otf`) —
  labels in caps with wide tracking (`letter-spacing: 0.22em`), e.g. "CLAUDE & COFFEE".
- Never mix in other typefaces on branded artifacts.

## Core assets (`assets/brand/`)

| File | What it is |
|---|---|
| `spark-ivory.png` / `spark-ink.png` | Claude spark, recolored per background |
| `arch-ivory.png` | "CLAUDE COMMUNITY" arched text (2048×785; arc radius ≈ 1060 image px, center x=1024) |
| `globe.png` | Hand-drawn community globe (408×408, full circle) |
| `community-square.png` | Official reference lockup: spark / arch / globe |

**Canonical compositions** (match these, don't invent):
1. **Community lockup** (Berlin banner, community-square): spark on top, arch
   text hugging the globe's upper hemisphere, serif line, caps label line.
   To nest the globe concentric with the arch text: globe width ≈ 0.78 × arch
   width, globe top ≈ archTop + 0.33 × archHeight.
2. **Event poster** (Signage-Eventposter): arch ~13% down, event icon nested in
   the arch hollow, serif city ~42%, caps label ~59%, date ~65%.
3. **Half globe rising from the bottom edge** — the kit never floats the globe;
   it is either nested under the arch or cropped by an edge.

## Icon library (`assets/icons/`)

Official kit icons: `meetup` (high-five), `conversation` (speech bubbles),
`workshop` (hand + shapes), `impact-lab` (hand + grid).
Drawn in-house to match: `coffee`, plus business industries —
`finance`, `legal`, `healthcare`, `education`, `real-estate`, `developer`,
`marketing`, `retail`.

All render correctly on clay. Preview the whole set:
open `templates/icon-proof.html` in a browser (or headless-Chrome screenshot it).

## Drawing a NEW topic icon (the coffee-mug recipe)

Read `reference/icon-style.md` for the full spec. The short version:

1. `viewBox="0 0 268 252"`, one concept, 2–4 path elements max.
2. Strokes: ink `#141413`, `stroke-width` 8–10 (9–10 for the main shape, 8 for
   detail lines), always `stroke-linecap="round"` / `stroke-linejoin="round"`.
3. Fills: main closed shape gets ivory `#FAF9F5`; accent lines unfilled.
4. **Hand-drawn wobble is mandatory** — no straight `L` lines or perfect
   rects for outlines. Use `C` curves whose control points drift 2–6 units off
   the ideal line, and let parallel edges be slightly unparallel. Perfect
   geometry is the tell that it's off-brand.
5. Sit the icon visually centered with ~30–40 units of breathing room.
6. Add the icon to `templates/icon-proof.html`, render on clay next to
   `meetup.svg` and `coffee.svg`, and compare: stroke weight should look equal
   at equal display size; if it looks mechanical, add wobble.
7. Ship the file to BOTH `assets/icons/` here and
   `<repo>/public/brand/official/icons/` so site generators can use it.

## Generators (in `~/Documents/Repository/personal/claude-community-nyc`)

| Generator | Produces | Notes |
|---|---|---|
| `brand-src/flyer.html` | Posters, flyers, social squares, retractable banners | URL params: `city, label, date, icon, labelIcon, qr, url, w, h, cassette`. `icon=globe` gives the community lockup; any icon name nests in the arch. Aspect picks layout: squarish < 1.2, poster, banner ≥ 2. |
| `brand-src/brand-core.html` + `scripts/brand.mjs` | LinkedIn banners, avatars, OG images | `node scripts/brand.mjs` core mode |
| `app/api/event-asset/[slug]` | Per-event share assets (satori, on-site) | Uses `lib/og-fonts.ts` `iconForLabel` |
| `~/.claude/skills/event-name-badges` | Printable name badges | `cardstock-vert` stock = 3×4 portrait lanyard inserts |

Render pipeline (all artifacts):
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --screenshot=out.png --window-size=W,H --virtual-time-budget=12000 "file://…?params"
```

## Print specs learned the hard way

- **Vistaprint retractable 33"×81"**: render at bleed 33.7"×81.34" (5055×12201 @150dpi);
  bottom ~4% rolls into the cassette — pass `cassette=0.04` so nothing important
  sits there. Safety area is 77.87" tall.
- **Posters**: Staples sells 12"×18", not 11"×17". 200 dpi PNG is plenty.
- **Badges**: 3"×4" portrait inserts on 67 lb cardstock, print 100%/Actual Size,
  always run a plain-paper test sheet first.
- QR codes: ink on ivory, generate with python `qrcode[pil]`, verify decode with
  `opencv-python-headless` before printing.

## Rules

- Events are free and open; co-hosted events are named "Claude Community x [Partner]".
- Keep artifacts aligned with the official kit — remix the kit's own elements
  rather than inventing new visual language.
- Never redraw the spark; recolor it (ivory on clay, ink on ivory).
- Attendee lists are confidential: never bake attendee data into shared artifacts.

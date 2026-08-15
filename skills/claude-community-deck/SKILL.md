---
name: claude-community-deck
description: Build a Claude Community event deck, the keynote or welcome deck presented at a Claude & Coffee, meetup, workshop, conversation, or Impact Lab. Carries the official Anthropic Claude Community deck system: clay/ivory/ink palette, Anthropic Serif and Archivo type, the arch lockup title, a 33-pattern slide library, a 31-icon set covering event themes and industries, a window-capture script for Claude product screenshots across browser, desktop and terminal, present-mode navigation, and one-slide-per-page PDF export. Use when Brandon needs slides for any Claude Community NYC event, or when an ambassador deck needs new slides added.
---

# Claude Community Event Deck

The deck system behind *Keep Thinking* (Claude & Coffee NYC, August 11 2026).
Self-contained HTML, 1280×720, keyboard-driven in the room, and it prints to a
clean 16:9 PDF for the recap email.

Sibling skills: `claude-community-brand` for posters, flyers, badges, and new
icons. `event-name-badges` for the printable badges. `deck-to-pdf` for export.
This one is for the slides. AuraPath client decks use `aurapath:slides` instead
and share none of this styling.

## Build a deck

1. **Make the folder.** `~/Documents/explanations/YYYY-MM-DD-<event-slug>/`
2. **Copy the shell.** `cp templates/deck.shell.html <folder>/deck.template.html`
3. **Set the two labels.** The `<title>` at the top, and `var CHROME` in the
   script at the bottom (that is the footer line on every slide).
4. **Write the arc before the slides.** Read `reference/deck-arc.md`. The
   chapter frame is nine slides you reuse nearly verbatim every event; the
   middle is the only part that is genuinely new. Draft the middle as a list of
   headline claims first, then pick a pattern for each.
5. **Assemble.** Paste patterns from `templates/slide-patterns.html` in place of
   the `SLIDES` marker comment, and rewrite the copy against
   `reference/writing-style.md`.
6. **Drop in event assets.** Anything event-specific goes in
   `<folder>/assets/`, or loose at the folder root for a QR. A deck-local file
   beats a skill file of the same name, so `assets/coffee.svg` in the folder
   overrides the kit's.
7. **Build.** `python3 ~/.claude/skills/claude-community-deck/build.py <folder>`
   → writes `<folder>/<folder-name>.html`, fully inlined and offline-safe.
8. **Check it in a browser** before calling it done. Open the built file, press
   `O` for the overview grid, and look for any slide whose content overflows its
   720px box. Fix by cutting words, never by shrinking the type scale.
9. **Export.** `bash ~/.claude/skills/deck-to-pdf/html-to-pdf.sh <built.html> <out.pdf>`
   Page count must equal slide count.

## Presenting

`←` `→` or space to move · `O` overview grid, click any slide to jump ·
`F` fullscreen · `P` print. The deck scales to any screen, so no resizing at the
venue. The URL hash tracks the slide, so a reload resumes where you were.

## Slide patterns

All 31 live in `templates/slide-patterns.html`, each with a comment on when to
use it. Preview them rendered:
`python3 build.py --patterns && open templates/slide-patterns-preview.html`

| Pattern | Reach for it when |
|---|---|
| Title | Opens the deck. Arch lockup, event icon, date and venue. |
| Welcome | Who is speaking and what this room is. Text beside a square. |
| Three tiles | Three parallel pillars or reasons. |
| Stat row | Four numbers that size the thing. |
| Ambassador roster | The ten NYC ambassadors and their verticals. |
| Industry icon grid | "Every lane has a version of this." Clay ground. |
| Four formats | The official event formats. Reuse near-verbatim. |
| Timeline | How the evening runs. Five stops maximum. |
| Two-card anatomy | Front and back, before and after, two halves of one thing. |
| Event calendar | What is next on the NYC calendar. |
| Section divider | One per part. Clay, part number, one-sentence promise. |
| Big quote | The sentence the section argues with. |
| Stacked bars | Before and after as proportions, with a legend. |
| Comparison table | Old framing versus new. Six rows maximum. |
| Two-chart figure | Two small charts, paired captions underneath. |
| Definitions table | Term, precise definition, plain-English metaphor. |
| Flow chain | Left-to-right stations with arrows. The system map. |
| Numbered list | Three claims that each need a sentence of evidence. |
| Two-card contrast | Without versus with. |
| Concept slide | The workhorse: lede, serif callout, three cards. |
| Product shot wide | One landscape screenshot, caption under. |
| Product shot split | Screenshot left, argument right. `.two` stacks two. |
| Three surfaces | Browser, desktop and terminal side by side. |
| Terminal shot | A Claude Code moment on the ink ground. |
| Trio of product cards | Three options answering identical rows. |
| Process matrix | Proves one pattern generalises across industries. |
| Diagram beside prose | Square diagram, two paragraphs, for cyclical ideas. |
| Signal comparison | Regular ticks versus irregular event spikes. |
| Crossover chart | "Costs more once, less every time after." |
| Checklist | The take-home slide. The one people photograph. |
| Four steps | The homework, with a time budget in the headline. |
| Close | Mirrors the title. Same words, meaning now filled in. |
| CTA and QR | Stays on screen through the breakout. |

## Design invariants

Break these and it stops looking like Claude Community.

- **Three colors only.** Clay `#D97757`, ink `#141413`, ivory `#FAF9F5`, plus
  the alpha tints already defined as CSS variables. Never introduce a fourth
  hue, not for a chart series, not for a highlight.
- **Three grounds.** Ivory is the default. Clay carries section dividers, the
  title, the close, and one or two feature slides. Ink is available and rarely
  needed. Roughly one clay slide in four keeps the rhythm without fatigue.
- **Two typefaces.** Anthropic Serif Display Light for `h1`, `h2`, `.quote` and
  large numerals. Anthropic Sans Display Semibold for kickers, labels, and
  anything uppercase-tracked. Archivo carries body copy. Nothing else, ever.
- **The spark sits top-right of every slide** except `.no-chrome`. It is drawn
  by `.slide::after`; do not hand-place it.
- **One callout per slide, always last.** It is the line the audience should
  leave with, not a summary of the slide above it.
- **Every slide earns its headline.** The `h2` is a claim, not a topic label.
  "Skills move the floor, not the ceiling" beats "About skills".
- **Nothing scrolls.** 1280×720 is the whole canvas. If it does not fit, the
  copy is too long. Cut it.
- **Bullets are near-banned.** Only the two-card anatomy pattern uses `<ul>`.
  Everything else uses the structured patterns, because a bulleted list is what
  this system exists to replace.

## Voice

Full rules in `reference/writing-style.md`. The short version: second person,
present tense, short declaratives, concrete nouns. Antithesis is the house
figure of speech ("A prompt is a peak. A system is a floor."). No em dashes, no
emojis, no exclamation marks, no jargon that needs its own definition. Never
sell anything; every event is free and attendee lists stay confidential.

## Assets

Bundled in `assets/`, found recursively by filename, so reference them by bare
name: `{{ASSET:spark-ivory.png}}`.

| Folder | Contents |
|---|---|
| `fonts/` | Anthropic Serif Display Light, Anthropic Sans Display Semibold, Archivo 400 and 600 |
| `brand/` | `spark-ivory`, `spark-ink`, `spark-clay`, `arch-ivory`, `globe`, `community-square`, `nyc-square`, placeholder `feedback-qr` |
| `icons/` | 31 hand-drawn icons, see the table below |
| `ambassadors/` | Headshots for all ten NYC ambassadors, `hs-<firstname>` |
| `product/browser/` | claude.ai screenshots: `cw-skills`, `cw-plugins`, `cw-connectors`, `cw-scheduled`, `cw-agent`, `cw-agents`, `cw-launcher`, `cw-loop` |
| `product/desktop/` | `claude-desktop.png`, currently a visible placeholder |
| `product/terminal/` | `claude-code.png`, currently a visible placeholder |

## Icons by event theme

The title slide nests one icon in the arch, and it is the fastest signal of what
the event is about. Pick from these 31 before drawing anything new.

| Theme | Icon |
|---|---|
| Claude & Coffee | `coffee` |
| Meetup, mixer, social | `meetup` |
| Conversation, small group | `conversation` |
| Workshop, hands on keyboards | `workshop` |
| Impact Lab, build day | `impact-lab` |
| Panel, ambassador night, AI Week | `panel` |
| Finance, fintech, banking | `finance` |
| Private equity | `private-equity` |
| Venture capital, startups investing | `venture-capital` |
| Startups, founders | `startup` |
| Legal | `legal` |
| Healthcare, clinical | `healthcare` |
| Life sciences, research, biotech | `life-sciences` |
| Education, edtech, schools | `education` |
| Engineering, developers | `developer` |
| Design | `design` |
| Product management | `product-management` |
| Data, analytics | `data` |
| Marketing | `marketing` |
| Content creation, media production | `content-creation` |
| Media, film, entertainment | `media` |
| Sales, go-to-market | `sales` |
| Operations | `operations` |
| Enterprise, large-company adoption | `enterprise` |
| Real estate | `real-estate` |
| Retail, commerce | `retail` |
| Insurance | `insurance` |
| Manufacturing, industrials | `manufacturing` |
| Government, public sector | `government` |
| Nonprofit, social impact | `nonprofit` |
| Security, trust and safety | `security` |

Proof them on clay before shipping a deck:
`bash ~/.claude/skills/deck-to-pdf/html-to-pdf.sh templates/icon-proof.html /tmp/icons.pdf`

Need one that does not exist? Load `claude-community-brand`, follow its icon
recipe (268×252 viewBox, ink strokes, ivory fills, mandatory hand-drawn wobble),
then ship the SVG to `assets/icons/` here, to the brand skill, and to
`claude-community-nyc/public/brand/official/icons/`.

## Product screenshots

The room wants to see the actual product. Show all three surfaces at least once
per deck, because most attendees have only ever opened one of them.

Capture with the bundled script, which captures a single window and never the
rest of the screen:

```
bash capture-window.sh assets/product/browser/claude-composer.png "Google Chrome"
bash capture-window.sh assets/product/desktop/claude-desktop.png  "Claude"
bash capture-window.sh assets/product/terminal/claude-code.png
```

Give an app name and it brings that app forward, captures its front window, and
hands focus back with no clicking. Omit the name, or run without Accessibility
permission, and it drops to interactive mode where you click the window you
want.

Permissions live in System Settings → Privacy & Security, granted to the
terminal application you run this from, which then needs a restart:

| Permission | Effect |
|---|---|
| Screen Recording | Required. Without it the PNG is blank or shows only wallpaper |
| Accessibility | Optional. Unlocks the no-click automatic mode |

Before a shot goes in a deck:

- **Set the window to a sane size first.** All three shots on the triptych slide
  are cropped to the same height from the top, so wildly different window sizes
  read as one being zoomed.
- **Check for private content.** Chat titles in the sidebar, client names, real
  email addresses, connector accounts, file paths with client names. Start a new
  chat and collapse the sidebar before capturing.
- **Use invented example content.** A prompt written for the slide beats a real
  one, and it lets you make the point in one screenful.
- **Retake rather than present a stale UI.** Claude ships often, and an old
  screenshot is the one thing in the room the audience can fact-check instantly.

Replace the file in `assets/product/` here, not just in the deck folder, so the
next deck inherits the fresh shot.

## Gotchas

- **`font-display` must be `swap`.** With `block`, Chrome's print-to-PDF
  snapshot never resolves the load and every glyph in those faces renders
  invisible in the PDF while looking perfect on screen.
- **Color SVG text with CSS classes, not `fill=`.** The stylesheet's `fill`
  beats the attribute, so use `.i` (ivory), `.ii` (ivory dimmed), `.c` (clay)
  on `text`, and keep `fill=` for shapes.
- **Assets are inlined as base64.** The built file is large and that is
  correct: it works with no network, no sibling folder, and no broken image on
  someone else's laptop.
- **`build.py` fails loudly** on a missing asset or a leftover token. A build
  that prints a path is a build that is complete.
- **A deck-local asset shadows a kit asset of the same name.** That is the
  supported way to override the QR, a headshot, or an icon for one event.

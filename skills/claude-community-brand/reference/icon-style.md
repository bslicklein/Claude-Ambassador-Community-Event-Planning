# Kit icon style — full spec

The official Claude Community icons (meetup, conversation, workshop,
impact-lab) share a hand-drawn ink language. Every new topic or industry icon
must pass as a sibling of those four. This file is the spec, distilled from
tracing the originals and from drawing `coffee.svg` and the eight industry
icons that shipped with this skill.

## Canvas and construction

- `viewBox="0 0 268 252"` (matches the extracted kit icons; height varies a
  little in the originals — keep 268 wide).
- One clear concept per icon. If you need a caption to explain it, redraw it.
- 2–4 `<path>` elements. The originals are economical: a main silhouette plus
  one or two accent strokes.
- Leave ~30–40 units of margin on every side; optical centering beats
  mathematical centering (a bag with a tall handle sits slightly low).

## Stroke and fill

| Element | Spec |
|---|---|
| Main outline | `stroke="#141413"` `stroke-width="10"` `fill="#FAF9F5"` |
| Secondary shape | stroke-width 9, ivory fill if closed |
| Detail / motion lines | stroke-width 8, `fill="none"` |
| Caps and joins | ALWAYS `stroke-linecap="round" stroke-linejoin="round"` |
| Tiny solid accents | pure ink fill, no stroke (e.g. terminal window dots) |

At 170 px display height the strokes should look identical in weight to
`meetup.svg` shown at the same height. That is the calibration test.

## The wobble (what makes it look official)

The kit icons are drawn by hand, not by a shape tool. Reproduce that:

- Replace every straight line with a `C` curve whose control points drift
  2–6 units off the ideal path. `M52 206 L52 146` becomes
  `M52 206 C50 152 54 148 57 146`.
- Parallel edges must not be parallel: if the left edge of a bar leans 2 units,
  keep the right edge straight or lean it 1 the other way.
- Corners get small radii by ending strokes short and letting round joins close
  them, or with tiny `C` hooks — never `rx` on a `<rect>`. In fact: no
  `<rect>`, no `<line>`, no `<polygon>`. Paths only (small `<circle>` is fine
  for solid dots).
- Symmetry: mirror the *idea*, not the coordinates. The scales' two pans in
  `legal.svg` differ by a few units on purpose.

## Color discipline

- Icons are ink-on-clay artifacts: `#141413` strokes, `#FAF9F5` fills, nothing
  else. No grays, no clay-colored strokes inside icons.
- The clay background comes from the artifact, never from the icon file —
  keep icon backgrounds transparent.

## Workflow for a new icon

1. Pick the single most recognizable object for the topic (industry → tool:
   finance → rising chart, legal → scales, healthcare → cross + pulse).
2. Sketch as clean geometry first, then apply wobble per above.
3. Add to `templates/icon-proof.html`, render the sheet on clay
   (headless Chrome), and compare against `meetup.svg` + `coffee.svg`:
   - stroke weight matches at equal height?
   - silhouette reads at 40 px?
   - does anything look CAD-perfect? add wobble there.
4. Ship to `assets/icons/` AND `<repo>/public/brand/official/icons/`.
5. If the icon maps to an event label, extend `iconForLabel` in
   `<repo>/lib/og-fonts.ts` so on-site event assets pick it up.

## Worked example

`coffee.svg` — mug: two steam curls (width 9, unclosed), body (width 10,
ivory fill, gently tapering sides), handle (width 10, open C), rim line
(width 8). Total 5 paths, every line curved, no two edges parallel.

---
name: event-rollup-banner
description: Use when an event needs a large roll-up, retractable, or pull-up banner — the tall vertical sign that stands beside the door or behind the speaker — including curating the artwork from the event topic and placing the order at Vistaprint. Triggers on "roll up banner", "retractable banner", "pull up banner", "big poster for the event", "order a banner", "vistaprint".
---

# Event Roll-Up Banner

Turns an event topic into a print-ready retractable banner in the official Claude
Community kit, at Vistaprint's spec, with the order checklist attached.

**The failure this prevents:** a banner that looks right on screen and arrives with
the date rolled up inside the cassette. The bottom of a retractable banner is not
visible. Roughly 4% of the height disappears into the base, and every layout that
was designed as a flat poster puts something important there.

Ordering is on **Vistaprint** because that is where the proofed file came from.
The welcome board goes to FedEx Office and name badges to Staples; different
products, different vendors, on purpose.

## Deliverables

| File | What it is |
|---|---|
| `banner-print.pdf` | **The file to upload.** Flattened, full bleed, 150 dpi |
| `banner-print.png` | Same artwork as PNG, if the upload form prefers it |
| `PROOF-safezone.png` | Small proof with trim, safe area, and the cassette line drawn on |
| `README.md` | What to order and what to check. Read it before paying |

## Workflow

### 1. Settle the four things

1. **What is the event, and what is the topic?** The topic picks the icon. The kit
   has icons for meetup, conversation, workshop, impact lab, coffee, and eight
   industries. If the topic has no icon, do not force a near-miss — draw one with
   `claude-community-brand` first; the recipe is in that skill.
2. **What size, and is there hardware already?** Default `33x81`, the proofed size.
   The stand is reusable, so if there is one in a closet already, match its size
   rather than buying another.
3. **Does it need a QR?** Only if it points somewhere useful on the day: the Luma
   page for the next event, or a feedback form. A QR to a homepage is decoration.
4. **When is the event?** This decides the whole thing. See lead time below.

### 2. Render

```bash
S=<this skill>
python3 $S/scripts/make_banner.py \
  --city "New York" --label "CLAUDE & COFFEE" \
  --date "August 11 · Georgie's" --icon coffee \
  --qr qr.png --out ./banner
```

`--icon globe` gives the community lockup instead of a topic icon, which is the
right call for an evergreen banner with no date on it. That version survives more
than one event, which is usually worth more than being specific.

Sizes: `33x81` is proofed and printed. `24x62`, `24x81`, `47x81` are computed by the
same rule and flagged unproofed in the output, because nobody has held one yet.

### 3. Check the proof before ordering

Open `PROOF-safezone.png` and confirm:

- Nothing that matters sits below the clay cassette line.
- The label is legible from ten feet back from the screen. That is the real
  viewing distance, and the test costs nothing.
- Download Vistaprint's own template for the exact SKU and lay the proof over it.
  Their hardware changes; the numbers in this skill are from one banner that was
  printed and hung, not from a promise.

### 4. Order

Vistaprint, Retractable Banners, matching size, **with stand** the first time and
banner-only afterwards if the hardware survives. Upload the PDF.

**Lead time is the failure mode, not the design.** Standard shipping is not
next-day. Order at least two weeks out. Inside one week, pay for tracked express
and confirm the delivery date before checkout rather than after.

## Standing rules

- **Fonts and palette come from `claude-community-brand`**, which must be installed
  alongside this skill. The generator reads the arch, spark, globe, icons, and both
  Anthropic display faces from it, and fails loudly rather than substituting a
  fallback face into a print file.
- Clay ground, ivory sans, ink serif. Never introduce a fourth color or a fifth
  typeface on a branded artifact.
- One message per banner. A retractable banner is read at walking pace by someone
  holding a coffee, not studied.
- Keep the rendered PNG and PDF with the event folder. Reordering a lost banner
  file three months later costs more time than the banner did.

## Part of a bigger sequence

This skill produces one artifact. `/ambassador:claude-and-coffee` owns the order the
artifacts get made in, the gates that block, and the reimbursement rules, and calls
this one at the right moment. Use it when running a whole event rather than making a
single thing.

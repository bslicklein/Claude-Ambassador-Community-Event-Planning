---
name: event-welcome-board
description: Use when an event needs the welcome board or door sign — the rigid foam-board sign on an easel at the entrance carrying the greeting, run of show, wifi, and a QR — including writing the copy and placing the order at FedEx Office. Triggers on "welcome board", "welcome sign", "door sign", "foam board", "easel sign", "run of show sign", "order the board at fedex".
---

# Event Welcome Board

Turns the run of show into a print-ready 24×36 foam board in the official Claude
Community kit, at FedEx Office's spec, with the order checklist attached.

**The failure this prevents:** a beautiful board with the wrong wifi password.
This is the one artifact every single guest reads, standing, within four seconds
of walking in. A typo here is seen more times than anything else produced for the
event.

Ordering is at **FedEx Office** because mounted posters are ready same day or
within 24 hours for in-store pickup. That makes the board the last artifact to
finalize, which is exactly what you want, because the run of show moves until it
does not. Banners go to Vistaprint and name badges to Staples.

## What belongs on it

The board answers four questions and nothing else:

1. **Am I in the right place?** Welcome, city, event name, date, venue.
2. **What happens when?** Four to six agenda lines. The script refuses more than six.
3. **Where do I sit?** One line, usually pointing at the badge.
4. **What is the wifi?** Network and password, in serif, large.

Sponsor logos, a mission statement, and a QR to a homepage all compete with those
four. Leave them off.

## Deliverables

| File | What it is |
|---|---|
| `board-print.pdf` | **The file to upload.** Full bleed, 150 dpi |
| `board-print.png` | Same artwork as PNG |
| `PROOF-board.png` | Small proof to read at arm's length before ordering |
| `board.html` | Source. Re-render after any copy change |
| `README.md` | What to order and what to check |

## Workflow

### 1. Get the run of show, not a guess at it

Ask for the actual timings from whoever is running the day. If they do not exist
yet, the board is not ready to print, and printing it early is how the wrong
version ends up on the easel.

### 2. Render

```bash
S=<this skill>
python3 $S/scripts/make_board.py \
  --event "Claude & Coffee" --city "New York" \
  --date "Tuesday, August 11" --venue "Georgie's, 2 Bond St" \
  --agenda "9:00|Doors, coffee, name badges" \
  --agenda "9:30|Welcome and Keep Thinking" \
  --agenda "10:15|Workshop at your table" \
  --agenda "11:30|Open build and mingle" \
  --wifi "Georgies-Guest / keepthinking" \
  --footnote "Your table number is on your badge" \
  --qr qr.png --out ./board
```

Agenda rows space themselves to fill the board, so four lines and six lines both
look deliberate. Sizes: `24x36` is the default and the one proofed against the
FedEx Office product; `18x24`, `22x28`, `16x20`, and `36x48` are also offered there.

### 3. Check the proof, character by character

- Read `PROOF-board.png` at arm's length. Every line must land from eight feet.
- **Check the date, the venue, and the wifi password character by character**,
  against the source, not from memory.
- Scan the QR from the proof with a phone. A QR that does not resolve is worse
  than no QR.

### 4. Order

FedEx Office → Posters → 24" × 36" → add **3/16" white foam board mounting**.
Upload the PDF, choose in-store pickup, and collect it the day before, not the
morning of.

Lamination is only offered when you upload your own print-ready file, which this
skill produces. Skip it unless the board gets reused; on a one-day sign it is
spend without a return.

**Bring an easel.** The board is rigid and it still does not stand up by itself.
Venues say they have one and then do not.

## Standing rules

- **Fonts and palette come from `claude-community-brand`**, which must be installed
  alongside this skill. The generator fails loudly rather than substituting a
  fallback face into a print file.
- Reprint rather than correct. Foam board is cheap; tape over a wrong time is
  visible from the door and reads as a scramble.
- Keep the final PNG. Photographed next to the easel, it is the best single
  documentation shot of the event for a recap post.

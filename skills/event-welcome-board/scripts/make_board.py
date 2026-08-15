#!/usr/bin/env python3
"""Render the Claude Community welcome board, the sign on the easel at the door.

  python3 make_board.py --event "Claude & Coffee" --city "New York" \
      --date "Tuesday, August 11" --venue "Georgie's, 2 Bond St" \
      --agenda "9:00|Doors, coffee, name badges" \
      --agenda "9:30|Welcome and Keep Thinking" \
      --agenda "10:15|Workshop at your table" \
      --agenda "11:30|Open build and mingle" \
      --wifi "Georgies-Guest / keepthinking" --qr qr.png --out ./board

Produces, in --out:
  board-print.png / .pdf   the file to upload, full bleed, 150 dpi
  PROOF-board.png          small proof to eyeball before ordering
  README.md                what to order at FedEx Office and what to check

The board answers the four questions every arriving guest has: am I in the right
place, what happens when, where do I sit, and what is the wifi. Anything else on
it competes with those four.
"""
import argparse, html, os, shutil, subprocess, sys

#           trim_w, trim_h  (FedEx Office mounted poster sizes)
SIZES = {'24x36': (24.0, 36.0), '18x24': (18.0, 24.0), '22x28': (22.0, 28.0),
         '16x20': (16.0, 20.0), '36x48': (36.0, 48.0)}
BLEED = 0.125
DPI = 150
CHROME_CANDIDATES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                     'google-chrome', 'chromium']

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family:"AnthropicSerif"; src:url("{fonts}/AnthropicSerifDisplay-Light-Static.otf") format("opentype"); }}
@font-face {{ font-family:"AnthropicSans"; src:url("{fonts}/AnthropicSansDisplay-Semibold-Static.otf") format("opentype"); }}
:root {{ --clay:#D97757; --ink:#141413; --ivory:#FAF9F5; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:{W}px; height:{H}px; background:var(--clay); color:var(--ivory);
        font-family:"AnthropicSans",sans-serif; overflow:hidden; position:relative; }}
.pad {{ position:absolute; left:{pad}px; right:{pad}px; }}
.serif {{ font-family:"AnthropicSerif",Georgia,serif; color:var(--ink); letter-spacing:-0.01em; }}
.caps {{ letter-spacing:0.22em; text-transform:uppercase; }}
.agenda {{ display:flex; flex-direction:column; justify-content:space-evenly; }}
.row {{ display:flex; align-items:baseline; gap:{u28}px; padding:{u18}px 0;
        border-top:{hair}px solid rgba(250,249,245,0.45); }}
.row .t {{ font-family:"AnthropicSerif",Georgia,serif; color:var(--ink);
           width:{timew}px; flex:none; font-size:{u38}px; }}
.row .w {{ font-size:{u32}px; line-height:1.15; }}
.foot {{ position:absolute; left:0; right:0; bottom:0; height:{footh}px;
         background:var(--ivory); color:var(--ink); display:flex; align-items:center;
         padding:0 {pad}px; }}
.foot > * {{ flex:0 0 auto; white-space:nowrap; }}
.foot > *:nth-child(2) {{ flex:1 1 0; text-align:center; white-space:normal;
                          padding:0 {u28}px; }}
.foot > *:nth-child(3) {{ text-align:right; }}
.foot img {{ display:inline-block; }}
</style></head><body>
<img src="{brand}/spark-ivory.png" style="position:absolute;width:{sparkw}px;left:50%;transform:translateX(-50%);top:{sparktop}px">
<img src="{brand}/arch-ivory.png" style="position:absolute;width:{archw}px;left:50%;transform:translateX(-50%);top:{archtop}px">
<div class="pad serif" style="top:{welcometop}px;font-size:{u150}px;line-height:0.98;text-align:center">{welcome}</div>
<div class="pad caps" style="top:{labeltop}px;font-size:{u44}px;text-align:center">{event}</div>
<div class="pad" style="top:{datetop}px;font-size:{u34}px;text-align:center;opacity:0.92">{date}{venue}</div>
<div class="pad agenda" style="top:{agendatop}px;height:{agendah}px">{rows}</div>
{foot}
</body></html>"""


def chrome():
    for c in CHROME_CANDIDATES:
        p = c if os.path.isabs(c) and os.access(c, os.X_OK) else shutil.which(c)
        if p:
            return p
    sys.exit('ERROR: Chrome not found. Install Google Chrome; it is the proofed renderer.')


def to_pdf(png, pdf, dpi):
    if shutil.which('magick'):
        subprocess.run(['magick', png, '-units', 'PixelsPerInch', '-density', str(dpi),
                        '-quality', '100', pdf], check=True)
        return 'magick'
    try:
        from PIL import Image
        Image.open(png).convert('RGB').save(pdf, 'PDF', resolution=dpi)
        return 'Pillow'
    except ImportError:
        return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--size', default='24x36', choices=list(SIZES))
    ap.add_argument('--welcome', default='Welcome')
    ap.add_argument('--event', required=True, help='e.g. "Claude & Coffee"')
    ap.add_argument('--city', default='')
    ap.add_argument('--date', required=True)
    ap.add_argument('--venue', default='')
    ap.add_argument('--agenda', action='append', default=[],
                    help='"time|what", repeatable. Four to six lines, never more.')
    ap.add_argument('--wifi', default='', help='"network / password"')
    ap.add_argument('--footnote', default='', help='right side of the foot, e.g. "Find your table number on your badge"')
    ap.add_argument('--qr', help='QR png, shown in the foot')
    ap.add_argument('--out', default='./board')
    ap.add_argument('--dpi', type=int, default=DPI)
    a = ap.parse_args()

    if len(a.agenda) > 6:
        sys.exit(f'{len(a.agenda)} agenda lines. A door sign is read in four seconds; '
                 'six lines is the ceiling. Cut it or move the detail to the table cards.')

    tw, th = SIZES[a.size]
    bw, bh = tw + 2 * BLEED, th + 2 * BLEED
    W, H = round(bw * a.dpi), round(bh * a.dpi)
    u = W / 1080.0                      # everything below is authored on a 1080-wide grid
    here = os.path.dirname(os.path.abspath(__file__))
    brand = os.path.normpath(os.path.join(here, '..', '..', 'claude-community-brand', 'assets'))
    if not os.path.exists(os.path.join(brand, 'brand', 'globe.png')):
        sys.exit(f'ERROR: brand assets not found at {brand}\n'
                 'This skill reads the palette, fonts, spark, and arch from the sibling\n'
                 'claude-community-brand skill. Install it alongside this one.')

    rows = ''.join(
        f'<div class="row"><div class="t">{html.escape(line.split("|", 1)[0].strip())}</div>'
        f'<div class="w">{html.escape(line.split("|", 1)[1].strip() if "|" in line else "")}</div></div>'
        for line in a.agenda)

    foot = ''
    if a.wifi or a.qr or a.footnote:
        left = (f'<div><div class="caps" style="font-size:{round(13 * u)}px;opacity:0.55">Wifi</div>'
                f'<div style="font-family:AnthropicSerif,Georgia,serif;font-size:{round(32 * u)}px;'
                f'margin-top:{round(6 * u)}px">{html.escape(a.wifi)}</div></div>') if a.wifi else '<div></div>'
        mid = (f'<div style="font-size:{round(19 * u)}px">'
               f'{html.escape(a.footnote)}</div>') if a.footnote else '<div></div>'
        right = (f'<img src="{os.path.abspath(a.qr)}" style="width:{round(120 * u)}px;'
                 f'height:{round(120 * u)}px;border-radius:{round(8 * u)}px">') if a.qr else '<div></div>'
        foot = f'<div class="foot">{left}{mid}{right}</div>'

    footh = round(175 * u) if foot else 0
    venue = f' · {html.escape(a.venue)}' if a.venue else ''
    welcome = html.escape(a.welcome) + (f'<br>{html.escape(a.city)}' if a.city else '')
    pad = round(90 * u)
    agendatop = round(690 * u)
    page = PAGE.format(
        fonts=os.path.join(brand, 'fonts'), brand=os.path.join(brand, 'brand'),
        W=W, H=H, pad=pad, hair=max(1, round(1.5 * u)), timew=round(150 * u),
        u18=round(14 * u), u28=round(30 * u), u32=round(30 * u), u34=round(20 * u),
        u38=round(32 * u), u44=round(26 * u), u150=round(118 * u),
        sparkw=round(58 * u), sparktop=round(52 * u),
        archw=round(400 * u), archtop=round(120 * u),
        welcometop=round(330 * u), labeltop=round(592 * u), datetop=round(638 * u),
        agendatop=agendatop, agendah=H - footh - agendatop - round(60 * u), footh=footh,
        welcome=welcome, event=html.escape(a.event), date=html.escape(a.date),
        venue=venue, rows=rows, foot=foot)

    os.makedirs(a.out, exist_ok=True)
    src = os.path.join(a.out, 'board.html')
    open(src, 'w').write(page)
    png = os.path.join(a.out, 'board-print.png')
    print(f'rendering {a.size} at {W}x{H}px ({bw}" x {bh}" bleed, {a.dpi} dpi)')
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--virtual-time-budget=15000',
                    f'--window-size={W},{H}', f'--screenshot={png}', 'file://' + os.path.abspath(src)],
                   check=True, capture_output=True)
    if not os.path.exists(png):
        sys.exit('ERROR: Chrome produced no file.')

    pdf = os.path.join(a.out, 'board-print.pdf')
    engine = to_pdf(png, pdf, a.dpi)
    try:
        from PIL import Image
        im = Image.open(png)
        im.thumbnail((1000, 1000))
        im.save(os.path.join(a.out, 'PROOF-board.png'))
    except ImportError:
        pass

    open(os.path.join(a.out, 'README.md'), 'w').write(f"""# Welcome board, {a.size}

Order from **FedEx Office**, Posters, **{tw:.0f}" x {th:.0f}"**, with
**3/16" foam board mounting**. Most orders are ready same day or within 24 hours
for in-store pickup, which is why this is the sign to leave until last.

Upload `board-print.pdf` ({engine or 'no PDF engine found, upload the PNG'}).
Artwork is {bw}" x {bh}" including {BLEED}" bleed on all sides, at {a.dpi} dpi.

## Before you order

- [ ] Open `PROOF-board.png` and read it at arm's length. Every line has to land
      from eight feet away, standing, in a doorway, while holding a coffee.
- [ ] Check the date, the venue, and the wifi password character by character.
      This is the one artifact where a typo is visible to every single guest all day.
- [ ] Scan the QR with a phone, from the proof. A QR that does not resolve is worse
      than no QR.
- [ ] Uploading your own print-ready file is also what unlocks lamination. Skip it
      unless the board gets reused; matte lamination on a one-day sign is spend
      without a return.
- [ ] Bring or borrow an easel. The board is rigid but it does not stand up by itself.

## Reorder

Same command with new copy. Foam board is cheap enough that reprinting beats
correcting a wrong date with tape.
""")
    print(f'\nPNG   -> {png}')
    print(f'PDF   -> {pdf}' if engine else 'PDF   -> skipped, install imagemagick or Pillow')
    print(f'ORDER -> {os.path.join(a.out, "README.md")}')


if __name__ == '__main__':
    main()

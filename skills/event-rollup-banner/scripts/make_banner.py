#!/usr/bin/env python3
"""Render a Claude Community retractable banner at Vistaprint print spec.

  python3 make_banner.py --city "New York" --label "CLAUDE & COFFEE" \
      --date "August 11 · Georgie's" --icon coffee --qr qr.png --out ./banner

Produces, in --out:
  banner-print.png   the file to upload, full bleed, 150 dpi
  banner-print.pdf   same artwork as flattened PDF (Vistaprint's preferred format)
  PROOF-safezone.png small proof with trim, safe area, and cassette line drawn on
  README.md          what to order and what to check

Sizes: --size 33x81 is the proofed one. The others are computed by the same rule
and are marked unproofed in the output, because nobody has held one yet.
"""
import argparse, os, shutil, subprocess, sys, urllib.parse

# trim_w, trim_h, bleed_w, bleed_h, cassette fraction, safe height, proofed
SIZES = {
    '33x81': (33.0, 81.0, 33.70, 81.34, 0.040, 77.87, '2026-08-11 Claude & Coffee NYC'),
    '24x62': (24.0, 62.0, 24.70, 62.34, 0.052, 58.80, None),
    '24x81': (24.0, 81.0, 24.70, 81.34, 0.040, 77.87, None),
    '47x81': (47.0, 81.0, 47.70, 81.34, 0.040, 77.87, None),
}
DPI = 150
CHROME_CANDIDATES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                     'google-chrome', 'chromium']


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
        im = Image.open(png).convert('RGB')
        im.save(pdf, 'PDF', resolution=dpi)
        return 'Pillow'
    except ImportError:
        return ''


def proof(png, out, trim_w, trim_h, bleed_w, bleed_h, cassette, safe_h):
    """Downscaled proof with trim, cassette, and safe area drawn on top."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return ''
    im = Image.open(png).convert('RGB')
    im.thumbnail((900, 3000))
    d = ImageDraw.Draw(im, 'RGBA')
    W, H = im.size
    tx, ty = (bleed_w - trim_w) / 2 / bleed_w * W, (bleed_h - trim_h) / 2 / bleed_h * H
    d.rectangle([tx, ty, W - tx, H - ty], outline=(20, 20, 19, 255), width=2)
    cy = H * (1 - cassette)
    d.rectangle([0, cy, W, H], fill=(20, 20, 19, 90))
    d.line([0, cy, W, cy], fill=(217, 119, 87, 255), width=3)
    sh = safe_h / bleed_h * H
    d.rectangle([tx + W * 0.04, ty, W - tx - W * 0.04, ty + sh], outline=(217, 119, 87, 220), width=2)
    im.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--size', default='33x81', choices=list(SIZES))
    ap.add_argument('--city', default='New York')
    ap.add_argument('--label', default='CLAUDE & COFFEE')
    ap.add_argument('--date', default='')
    ap.add_argument('--url', default='')
    ap.add_argument('--icon', default='globe',
                    help='icon name from the brand skill, or "globe" for the community lockup')
    ap.add_argument('--label-icon', default='')
    ap.add_argument('--qr', help='path to a QR png, copied next to the generator')
    ap.add_argument('--out', default='./banner')
    ap.add_argument('--dpi', type=int, default=DPI)
    a = ap.parse_args()

    trim_w, trim_h, bw, bh, cassette, safe_h, proofed = SIZES[a.size]
    px_w, px_h = round(bw * a.dpi), round(bh * a.dpi)
    here = os.path.dirname(os.path.abspath(__file__))
    gen = os.path.join(here, '..', 'assets', 'flyer.html')
    brand = os.path.normpath(os.path.join(here, '..', '..', 'claude-community-brand', 'assets'))
    if not os.path.exists(os.path.join(brand, 'brand', 'globe.png')):
        sys.exit(f'ERROR: brand assets not found at {brand}\n'
                 'This skill reads the palette, fonts, arch, globe, and icons from the sibling\n'
                 'claude-community-brand skill. Install it alongside this one.')

    os.makedirs(a.out, exist_ok=True)
    params = {'w': px_w, 'h': px_h, 'city': a.city, 'label': a.label, 'date': a.date,
              'icon': a.icon, 'cassette': cassette}
    if a.url:
        params['url'] = a.url
    if a.label_icon:
        params['labelIcon'] = a.label_icon
    if a.qr:
        qr_dst = os.path.join(os.path.dirname(os.path.abspath(gen)), 'qr-tmp.png')
        shutil.copyfile(a.qr, qr_dst)
        params['qr'] = 'qr-tmp.png'

    url = 'file://' + os.path.abspath(gen) + '?' + urllib.parse.urlencode(params)
    png = os.path.join(a.out, 'banner-print.png')
    print(f'rendering {a.size} at {px_w}x{px_h}px ({bw}" x {bh}" bleed, {a.dpi} dpi)')
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--virtual-time-budget=15000',
                    f'--window-size={px_w},{px_h}', f'--screenshot={png}', url],
                   check=True, capture_output=True)
    if a.qr:
        os.remove(qr_dst)
    if not os.path.exists(png):
        sys.exit('ERROR: Chrome produced no file. Re-run without --headless to see the page.')

    pdf = os.path.join(a.out, 'banner-print.pdf')
    engine = to_pdf(png, pdf, a.dpi)
    pf = proof(png, os.path.join(a.out, 'PROOF-safezone.png'),
               trim_w, trim_h, bw, bh, cassette, safe_h)

    readme = os.path.join(a.out, 'README.md')
    with open(readme, 'w') as f:
        f.write(f"""# Retractable banner, {a.size}

Order from **Vistaprint**, retractable banner, **{trim_w:.0f}" x {trim_h:.0f}"**, with stand.

Upload `banner-print.pdf` ({engine or 'PNG only, no PDF engine found'}).
Artwork is {bw}" x {bh}" including bleed, at {a.dpi} dpi ({px_w} x {px_h} px).

## Before you order

- [ ] Open `PROOF-safezone.png`. Nothing that matters may sit below the clay line,
      that is the bottom {cassette * 100:.0f}% the cassette swallows.
- [ ] Download Vistaprint's own template for this exact SKU and lay the proof over
      it. Their hardware changes; this file's numbers are from
      {'a banner that was printed and hung: ' + proofed if proofed else 'the proofed 33x81 rule, applied to this size but never physically printed'}.
- [ ] Read the banner from 10 feet back on screen. If the label is not legible
      there, it is not legible across a room.
- [ ] Lead time. Standard Vistaprint shipping is not a next-day option, so order
      at least two weeks out, and pay for tracked shipping on anything under one week.

## Reorder

Same command, new `--city / --label / --date / --icon`. The stand is reusable,
so later events only need the banner cartridge if you keep the hardware.
""")

    print(f'\nPNG   -> {png}')
    print(f'PDF   -> {pdf}' if engine else 'PDF   -> skipped, install imagemagick or Pillow')
    if pf:
        print(f'PROOF -> {pf}')
    print(f'ORDER -> {readme}')
    if not proofed:
        print(f'\nNOTE: {a.size} has never been physically printed. Check against '
              "Vistaprint's template before ordering.")


if __name__ == '__main__':
    main()

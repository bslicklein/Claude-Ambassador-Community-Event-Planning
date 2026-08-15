#!/usr/bin/env python3
"""Inline every {{ASSET:name}} token in a deck template as a base64 data URI.

Produces a single self-contained HTML file that works offline, prints to PDF
with fonts intact, and can be emailed or dropped on a USB stick.

Usage
-----
  python3 build.py <deck-dir> [--out NAME.html]
      Reads   <deck-dir>/deck.template.html
      Writes  <deck-dir>/<deck-dir basename>.html   (or --out)

  python3 build.py --patterns [--out PATH]
      Stitches templates/deck.shell.html + templates/slide-patterns.html into a
      previewable deck of every slide pattern. Use it to eyeball the library.

Asset lookup order for {{ASSET:foo.png}}:
  1. <deck-dir>/assets/**/foo.png      event-specific art wins
  2. <skill>/assets/**/foo.png         shared brand kit
  3. <deck-dir>/foo.png                loose files like a generated QR code
"""
import argparse
import base64
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).parent
SKILL_ASSETS = SKILL / "assets"

MIME = {
    ".otf": "font/otf",
    ".ttf": "font/ttf",
    ".woff2": "font/woff2",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def find_asset(name, deck_dir):
    """First match wins, searching the deck's own assets before the shared kit."""
    roots = []
    if deck_dir:
        roots.append(deck_dir / "assets")
    roots.append(SKILL_ASSETS)
    for root in roots:
        if root.is_dir():
            for path in sorted(root.rglob(name)):
                return path
    if deck_dir and (deck_dir / name).exists():
        return deck_dir / name
    return None


def inline_assets(template, deck_dir):
    missing = []

    def sub(match):
        name = match.group(1).strip()
        path = find_asset(name, deck_dir)
        if path is None:
            missing.append(name)
            return ""
        mime = MIME.get(path.suffix.lower())
        if mime is None:
            missing.append(f"{name} (unknown mime type)")
            return ""
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f"data:{mime};base64,{b64}"

    out = re.sub(r"\{\{ASSET:([^}]+)\}\}", sub, template)
    if missing:
        sys.exit("Missing assets: " + ", ".join(sorted(set(missing))))
    if "{{ASSET" in out:
        sys.exit("Unreplaced asset tokens remain.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck_dir", nargs="?", help="Directory holding deck.template.html")
    ap.add_argument("--patterns", action="store_true",
                    help="Build the slide-pattern library instead of a deck")
    ap.add_argument("--out", help="Output file path")
    args = ap.parse_args()

    if args.patterns:
        shell = (SKILL / "templates" / "deck.shell.html").read_text()
        slides = (SKILL / "templates" / "slide-patterns.html").read_text()
        template = shell.replace("<!-- {{SLIDES}} -->", slides)
        deck_dir = None
        dest = pathlib.Path(args.out) if args.out else SKILL / "templates" / "slide-patterns-preview.html"
    else:
        if not args.deck_dir:
            sys.exit("Pass a deck directory, or --patterns.")
        deck_dir = pathlib.Path(args.deck_dir).expanduser().resolve()
        src = deck_dir / "deck.template.html"
        if not src.exists():
            sys.exit(f"No deck.template.html in {deck_dir}")
        template = src.read_text()
        dest = pathlib.Path(args.out) if args.out else deck_dir / f"{deck_dir.name}.html"

    if "{{SLIDES}}" in template:
        sys.exit("The {{SLIDES}} marker is still in the template. Replace it with real slides.")

    out = inline_assets(template, deck_dir)
    dest.write_text(out)
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

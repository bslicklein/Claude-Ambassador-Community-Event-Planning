#!/usr/bin/env python3
"""Scaffold a Claude & Coffee event folder: the brief, the dated checklist, the layout.

  python3 new_event.py --date 2026-10-06 --venue "Georgie's, 182 Broome St" --seats 100

Everything downstream reads event.json, so this is the one file to keep current.
Re-running against an existing folder refreshes CHECKLIST.md from the real dates
and leaves event.json alone.
"""
import argparse, datetime as dt, json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import GATES

DEFAULT_ROOT = os.path.expanduser('~/Documents/explanations/community-events')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='event date, YYYY-MM-DD')
    ap.add_argument('--name', default='Claude & Coffee')
    ap.add_argument('--city', default='New York')
    ap.add_argument('--topic', default='')
    ap.add_argument('--venue', default='')
    ap.add_argument('--seats', type=int, default=100)
    ap.add_argument('--format', default='meetup', choices=['meetup', 'workshop', 'conversation', 'impact-lab'])
    ap.add_argument('--slug', help='folder name, defaults to <date>-<name>-<city>')
    ap.add_argument('--root', default=DEFAULT_ROOT)
    a = ap.parse_args()

    try:
        day = dt.date.fromisoformat(a.date)
    except ValueError:
        sys.exit('--date must be YYYY-MM-DD')

    slugify = lambda s: ''.join(c.lower() if c.isalnum() else '-' for c in s).strip('-')
    while True:
        slug = a.slug or f"{a.date}-{slugify(a.name)}-{slugify(a.city)}"
        slug = '-'.join(p for p in slug.split('-') if p)
        break
    out = os.path.join(a.root, slug)
    os.makedirs(out, exist_ok=True)

    here = os.path.dirname(os.path.abspath(__file__))
    ev_path = os.path.join(out, 'event.json')
    if os.path.exists(ev_path):
        ev = json.load(open(ev_path))
        print(f'event.json already exists, leaving it alone')
    else:
        ev = json.load(open(os.path.join(here, '..', 'assets', 'event.template.json')))
        ev.update(slug=slug, name=a.name, city=a.city, date=a.date, topic=a.topic,
                  seats=a.seats, format=a.format)
        ev['budget']['expected_attendees'] = a.seats
        ev['budget']['cap'] = 750 if a.seats < 40 else 1125 if a.seats < 70 else 1500
        if a.format == 'impact-lab':
            ev['budget']['cap'] = 5000
        if a.venue:
            ev['venue']['name'] = a.venue
        json.dump(ev, open(ev_path, 'w'), indent=2)
        print(f'wrote {ev_path}')

    lines = [f"# {ev['name']} · {ev['city']} · {day:%A, %B %-d, %Y}", '',
             f"Seats {ev['seats']} · format {ev['format']} · reimbursement cap "
             f"${ev['budget']['cap']:,} (venue, refreshments, printed assets only)", '',
             'Dates below are computed from the event date. Tick a box only when the',
             'artifact exists, not when it is planned. `status.py` reads the folder and',
             'tells you the same thing without the honour system.', '']
    for g in GATES:
        d = day - dt.timedelta(days=g['t'])
        when = f"{d:%a %b %-d}"
        tag = 'BLOCKING' if g['blocking'] else 'soft'
        skill = f"  → `/{g['skill']}`" if g['skill'] else ''
        lines += [f"- [ ] **{when}** (T{-g['t']:+d}) · {g['title']} · _{tag}_{skill}",
                  f"      {g['why']}", '']
    lines += ['## Layout', '', '```',
              'event.json          the brief every skill reads',
              'roster.csv          pulled from Luma',
              'research.jsonl      one verified profile per line',
              'ranking.csv         scored and seated',
              'approve-list.csv    pushed to Luma',
              'workshop-groups.csv table assignments',
              'emails.csv          day-before, one hook each',
              'banner/ board/ badges/   print files and their order READMEs',
              '```', '']
    open(os.path.join(out, 'CHECKLIST.md'), 'w').write('\n'.join(lines))
    print(f'wrote {os.path.join(out, "CHECKLIST.md")}')
    print(f'\n{out}')
    print(f"\nT-minus today: {(day - dt.date.today()).days} days out")


if __name__ == '__main__':
    main()

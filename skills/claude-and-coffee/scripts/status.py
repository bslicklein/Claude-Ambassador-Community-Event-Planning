#!/usr/bin/env python3
"""What is done, what is due, and what is blocking, for one event folder.

  python3 status.py --event ~/Documents/explanations/community-events/<slug>

Reads event.json and looks for the actual artifacts on disk. A gate is done when
its file exists or its flag is set, never because someone said so.
"""
import argparse, datetime as dt, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import GATES

G, Y, R, B, X = '\033[32m', '\033[33m', '\033[31m', '\033[1m', '\033[0m'


def dig(d, path):
    cur = d
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def done(check, ev, folder):
    kind, val = check
    if kind == 'json':
        if val == '_never':
            return False
        if val == '_under_cap':
            quoted = dig(ev, 'venue.quoted_total')
            cap = dig(ev, 'budget.cap') or 0
            return quoted is not None and quoted <= cap
        return bool(dig(ev, val))
    if kind == 'file':
        return bool(glob.glob(os.path.join(folder, val)))
    if kind == 'any':
        return any(done(c, ev, folder) for c in val)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--event', required=True, help='path to the event folder')
    ap.add_argument('--plain', action='store_true', help='no colour')
    a = ap.parse_args()
    if a.plain:
        global G, Y, R, B, X
        G = Y = R = B = X = ''

    folder = os.path.abspath(os.path.expanduser(a.event))
    ev_path = os.path.join(folder, 'event.json')
    if not os.path.exists(ev_path):
        sys.exit(f'no event.json in {folder}. Run new_event.py first.')
    ev = json.load(open(ev_path))
    day = dt.date.fromisoformat(ev['date'])
    out = (day - dt.date.today()).days

    print(f"{B}{ev['name']} · {ev['city']} · {day:%A, %B %-d}{X}")
    print(f"{out} days out · {ev['seats']} seats · cap ${ev['budget']['cap']:,}\n")

    overdue, upcoming, blocked_by = [], [], None
    for g in GATES:
        ok = done(g['check'], ev, folder)
        due = day - dt.timedelta(days=g['t'])
        late = (not ok) and out <= g['t']
        mark = f'{G}done{X}' if ok else (f'{R}OVERDUE{X}' if late else f'{Y}open{X}')
        flag = ' [blocking]' if g['blocking'] and not ok else ''
        print(f"  {mark:<16} {due:%b %-d}  T{-g['t']:+d}  {g['title']}{flag}")
        if late:
            overdue.append(g)
            if g['blocking'] and blocked_by is None:
                blocked_by = g
        elif not ok and 0 <= (out - g['t']) <= 7:
            upcoming.append(g)

    quoted, cap = dig(ev, 'venue.quoted_total'), dig(ev, 'budget.cap')
    print()
    if quoted and cap and quoted > cap and not dig(ev, 'budget.preapproval_granted'):
        print(f"{R}BUDGET: quote ${quoted:,.0f} is over the ${cap:,} cap with no pre-approval. "
              f"About ${quoted - cap:,.0f} is unrecoverable unless community@anthropic.com "
              f"approves it in writing BEFORE the spend.{X}\n")
    if quoted and not dig(ev, 'venue.itemized_invoice'):
        print(f"{Y}BUDGET: no itemized invoice from the venue. Ask for space rental separated "
              f"from food and beverage now; it cannot be split after the event.{X}\n")

    if blocked_by:
        print(f"{R}BLOCKED: {blocked_by['title']}{X}")
        print(f"  {blocked_by['why']}")
        if blocked_by['skill']:
            print(f"  → /{blocked_by['skill']}")
    elif overdue:
        print(f"{Y}{len(overdue)} soft gate(s) overdue, nothing blocking.{X}")
    if upcoming:
        print(f"\n{B}Next up{X}")
        for g in upcoming[:3]:
            print(f"  T{-g['t']:+d}  {g['title']}" + (f"  → /{g['skill']}" if g['skill'] else ''))
    if out < 0 and not overdue:
        print(f"{G}Event is done and the close-out is clean.{X}")


if __name__ == '__main__':
    main()

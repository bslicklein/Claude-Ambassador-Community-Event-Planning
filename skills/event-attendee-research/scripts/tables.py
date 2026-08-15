#!/usr/bin/env python3
"""Assign approved attendees to workshop tables.

  python3 tables.py --ranking out/ranking.csv --size 6 --out out/

Three rules, in order:
  1. Industry cluster   same vocabulary, same problems, same tools
  2. Role level         peers talk to peers, not up and down a ladder
  3. Skill, SEEDED not sorted   every table gets someone who can unblock it

Why not sort by skill: sorting puts every beginner at one table with nobody able
to help them. That table stalls and the room splits into a fast half and a stuck
half. Seeding guarantees a helper at every table while keeping peers at the same
altitude.

Reads ranking.csv from score.py (needs: name, email, action, industry_cluster,
role_band, role_tier, is_builder). Writes workshop-groups.csv plus a table-by-table
report, and rewrites ranking.csv in place with a `workshop_table` column so the
badge, table-card, and email steps can read it.
"""
import argparse, csv, os
from collections import Counter, defaultdict

COLS = ['table', 'industry_cluster', 'role_band', 'name', 'email', 'verified_title',
        'verified_company', 'role_level', 'is_builder', 'status', 'claude_code_exp',
        'ai_proficiency', 'wants_to_learn', 'note']


def chunk(people, size):
    """Split a role-sorted list into tables as close to `size` as possible,
    never leaving a table of 1 or 2."""
    n = len(people)
    if n == 0:
        return []
    k = max(1, round(n / size))
    base, extra = divmod(n, k)
    out, i = [], 0
    for t in range(k):
        take = base + (1 if t < extra else 0)
        out.append(people[i:i + take])
        i += take
    return [t for t in out if t]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ranking', required=True)
    ap.add_argument('--size', type=int, default=6, help='target people per table')
    ap.add_argument('--out', default='.')
    ap.add_argument('--all', action='store_true', help='seat everyone, not just action=approve')
    ap.add_argument('--start', type=int, default=1, help='first table number')
    ap.add_argument('--min-table', type=int, default=4,
                    help='tables smaller than this are dissolved into their neighbours')
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.ranking)))
    people = [r for r in rows if a.all or r.get('action') == 'approve']
    if not people:
        raise SystemExit('nobody to seat: no action=approve rows (use --all to seat everyone)')

    by_cluster = defaultdict(list)
    for p in people:
        by_cluster[p.get('industry_cluster') or 'Other'].append(p)

    tables, num = [], a.start
    for cluster in sorted(by_cluster, key=lambda c: -len(by_cluster[c])):
        grp = sorted(by_cluster[cluster], key=lambda p: (-int(p.get('role_tier') or 3), p['name']))
        for t in chunk(grp, a.size):
            tables.append({'n': num, 'cluster': cluster, 'people': t})
            num += 1

    # Dissolve runt tables: a table of 2 or 3 is a stalled conversation, not a group.
    for t in [t for t in tables if len(t['people']) < a.min_table]:
        hosts = sorted((h for h in tables if h is not t),
                       key=lambda h: (h['cluster'] != t['cluster'], len(h['people'])))
        if not hosts:
            continue
        for p in list(t['people']):
            h = min(hosts, key=lambda h: len(h['people']))
            h['people'].append(p)
            t['people'].remove(p)
    tables = [t for t in tables if t['people']]
    for i, t in enumerate(tables, a.start):
        t['n'] = i

    # Seed builders: move surplus builders into builder-less tables.
    def builders(t):
        return [p for p in t['people'] if p.get('is_builder')]

    short = [t for t in tables if not builders(t)]
    for t in short:
        donors = sorted((d for d in tables if len(builders(d)) > 1),
                        key=lambda d: (d['cluster'] != t['cluster'], -len(builders(d))))
        if not donors:
            break
        d = donors[0]
        want = sum(int(p.get('role_tier') or 3) for p in t['people']) / max(1, len(t['people']))
        b = min(builders(d), key=lambda p: abs(int(p.get('role_tier') or 3) - want))
        swap = min((p for p in t['people'] if not p.get('is_builder')),
                   key=lambda p: abs(int(p.get('role_tier') or 3) - int(b.get('role_tier') or 3)),
                   default=None)
        d['people'].remove(b)
        t['people'].append(b)
        if swap is not None and len(t['people']) > a.size:
            t['people'].remove(swap)
            d['people'].append(swap)

    seat = {}
    for t in tables:
        for p in t['people']:
            seat[p['email']] = t['n']

    os.makedirs(a.out, exist_ok=True)
    gpath = os.path.join(a.out, 'workshop-groups.csv')
    with open(gpath, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
        w.writeheader()
        for t in tables:
            for p in sorted(t['people'], key=lambda p: -int(p.get('role_tier') or 3)):
                w.writerow({**p, 'table': t['n'], 'industry_cluster': t['cluster']})

    # write the table number back into ranking.csv
    fields = list(rows[0].keys())
    if 'workshop_table' not in fields:
        fields.append('workshop_table')
    for r in rows:
        r['workshop_table'] = seat.get(r['email'], '')
    with open(a.ranking, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    spreads, nobuilder = [], 0
    print(f'{len(people)} people -> {len(tables)} tables (target {a.size})\n')
    for t in tables:
        tiers = [int(p.get('role_tier') or 3) for p in t['people']]
        spread = (max(tiers) - min(tiers)) if tiers else 0
        spreads.append(spread)
        b = len(builders(t))
        nobuilder += (b == 0)
        bands = Counter(p.get('role_band') for p in t['people']).most_common(2)
        print(f"  Table {t['n']:>2}  {t['cluster'][:34]:<34} {len(t['people'])} people, "
              f"{b} builder{'s' if b != 1 else ''}, spread {spread}  "
              f"[{' + '.join(x[0] for x in bands)}]")
    avg = sum(spreads) / len(spreads) if spreads else 0
    print(f'\navg role spread {avg:.2f} tiers   '
          f'{len(tables) - nobuilder}/{len(tables)} tables have a seeded builder')
    if nobuilder:
        print(f'WARNING: {nobuilder} table(s) have no builder. Lower --size, or hand-place '
              'a co-host at those tables.')
    print(f'\nwrote {gpath}\n      {a.ranking} (added workshop_table)')


if __name__ == '__main__':
    main()

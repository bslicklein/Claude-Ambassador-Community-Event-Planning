#!/usr/bin/env python3
"""Pull the Luma guest list (including registration form answers) into roster.csv.

Auth: Luma Plus calendar-scoped API key in ~/.luma_key (chmod 600) or $LUMA_API_KEY.
The key is scoped to ONE calendar. A 403 "You don't have access to this event"
means the event lives on a different calendar than the key, not that the key is bad.

  python3 luma_guests.py --list                          # events on this calendar
  python3 luma_guests.py --event evt-xxxx --out roster.csv
  python3 luma_guests.py --event evt-xxxx --status pending_approval --out pending.csv

Every registration form question becomes its own column, so the structured pass
and the research brief can read them directly.
"""
import argparse, csv, json, os, sys, urllib.parse, urllib.request

BASE = 'https://public-api.luma.com/v1'


def key():
    k = os.environ.get('LUMA_API_KEY')
    if k:
        return k.strip()
    f = os.path.expanduser('~/.luma_key')
    if os.path.exists(f):
        return open(f).read().strip()
    sys.exit('No API key. Put it in ~/.luma_key (chmod 600) or export LUMA_API_KEY.')


def get(path, params, k):
    url = f'{BASE}/{path}?' + urllib.parse.urlencode(params)
    # Luma sits behind Cloudflare, which 403s the default urllib user agent (code 1010).
    req = urllib.request.Request(url, headers={'x-luma-api-key': k, 'User-Agent': 'curl/8.7.1'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as ex:
        sys.exit(f'HTTP {ex.code} on {path}: {ex.read().decode()[:300]}')


def slug(q):
    """Stable-ish column name from a form question label."""
    s = ''.join(c.lower() if c.isalnum() else '_' for c in (q or 'answer'))
    return '_'.join(x for x in s.split('_') if x)[:60] or 'answer'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--event', help='Luma event api_id, e.g. evt-xxxx')
    p.add_argument('--out', default='roster.csv')
    p.add_argument('--status', help='filter: approved | pending_approval | declined | waitlist')
    p.add_argument('--list', action='store_true', help='list events on this calendar and exit')
    a = p.parse_args()
    k = key()

    if a.list or not a.event:
        d = get('calendar/list-events', {'pagination_limit': 50}, k)
        for e in d.get('entries', []):
            ev = e['event']
            print(f"{ev['api_id']}  {ev.get('start_at','')[:10]}  {ev.get('name','')}")
        return

    rows, cursor, questions = [], None, []
    while True:
        params = {'event_api_id': a.event, 'pagination_limit': 100}
        if cursor:
            params['pagination_cursor'] = cursor
        d = get('event/get-guests', params, k)
        for e in d.get('entries', []):
            g = e['guest']
            row = {
                'guest_id': g.get('api_id'),
                'name': g.get('name') or g.get('user_name') or '',
                'email': (g.get('email') or g.get('user_email') or '').strip().lower(),
                'status': g.get('approval_status'),
                'registered_at': (g.get('registered_at') or '')[:16].replace('T', ' '),
                'checked_in_at': (g.get('checked_in_at') or '')[:16].replace('T', ' '),
            }
            for ans in (g.get('registration_answers') or []):
                q = ans.get('label') or ans.get('question') or ans.get('question_id') or ''
                col = slug(q)
                if col not in questions:
                    questions.append(col)
                v = ans.get('answer')
                row[col] = ', '.join(v) if isinstance(v, list) else ('' if v is None else str(v))
            rows.append(row)
        if not d.get('has_more'):
            break
        cursor = d.get('next_cursor')

    if a.status:
        rows = [r for r in rows if r['status'] == a.status]

    cols = ['guest_id', 'name', 'email', 'status', 'registered_at', 'checked_in_at'] + questions
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    by_status = {}
    for r in rows:
        by_status[r['status']] = by_status.get(r['status'], 0) + 1
    print(f'{len(rows)} guests -> {a.out}')
    print('  status:', ', '.join(f'{k2} {v}' for k2, v in sorted(by_status.items())))
    print('  form columns:', ', '.join(questions) or '(none)')


if __name__ == '__main__':
    main()

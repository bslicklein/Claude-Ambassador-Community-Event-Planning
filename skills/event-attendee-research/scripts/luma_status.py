#!/usr/bin/env python3
"""Push approve / waitlist decisions to Luma from approve-list.csv.

Each status change sends the guest a Luma email, so this is not reversible.
Dry run is the default and it prints exactly what would be sent.

  python3 luma_status.py --csv out/approve-list.csv --event evt-xxxx
  python3 luma_status.py --csv out/approve-list.csv --event evt-xxxx --go --limit 5
  python3 luma_status.py --csv out/approve-list.csv --event evt-xxxx --go
  python3 luma_status.py --csv out/approve-list.csv --event evt-xxxx --action waitlist --go

Only rows whose `action` matches --action are touched, so approving never
disturbs the waitlist. The optional `message` column is the per-guest note Luma
shows on approval; Luma truncates it at 200 characters.

Sent guest_ids are appended to .luma-sent.log next to the CSV, and re-runs skip
them, so a partial run is safe to resume.
"""
import argparse, csv, json, os, sys, time, urllib.error, urllib.request

API = 'https://public-api.luma.com/v1/events/guests/update-status'
STATUS = {'approve': 'approved', 'waitlist': 'waitlist', 'decline': 'declined'}


def key():
    k = os.environ.get('LUMA_API_KEY')
    if k:
        return k.strip()
    f = os.path.expanduser('~/.luma_key')
    if os.path.exists(f):
        return open(f).read().strip()
    sys.exit('No API key. Put it in ~/.luma_key (chmod 600) or export LUMA_API_KEY.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--event', default=os.environ.get('LUMA_EVENT_ID'),
                    help='Luma event api_id (evt-xxxx)')
    ap.add_argument('--action', default='approve', choices=list(STATUS))
    ap.add_argument('--go', action='store_true', help='actually send')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--no-message', action='store_true', help='ignore the message column')
    a = ap.parse_args()

    log_path = os.path.join(os.path.dirname(os.path.abspath(a.csv)), '.luma-sent.log')
    done = {l.strip() for l in open(log_path)} if os.path.exists(log_path) else set()

    rows = [r for r in csv.DictReader(open(a.csv)) if r.get('action') == a.action]
    rows = [r for r in rows if r.get('guest_id') and r['guest_id'] not in done]
    if a.limit:
        rows = rows[:a.limit]
    status = STATUS[a.action]
    print(f'{len(rows)} guests -> {status}   ({len(done)} already sent, skipped)')
    if not rows:
        return

    missing = [r['name'] for r in rows if not r.get('guest_id')]
    if missing:
        print(f'WARNING: {len(missing)} rows have no guest_id and will be skipped')

    if not a.go:
        print('\nDRY RUN. Re-run with --go to send. First 5:\n')
        for r in rows[:5]:
            print(f"  #{r.get('rank','?'):>4}  {r['name'][:28]:<28} {r['guest_id']}")
            if r.get('message') and not a.no_message:
                print(f"          {r['message'][:120]}")
        print(f"\n  ... and {max(0, len(rows) - 5)} more")
        print(f'\nThis sends {len(rows)} Luma emails. Not reversible.')
        return

    if not a.event:
        sys.exit('No event id. Pass --event evt-xxxx or export LUMA_EVENT_ID.')
    k = key()
    print(f'event {a.event}  key ...{k[-4:]}\n')

    ok, failures = 0, []
    for i, r in enumerate(rows, 1):
        body = {'event_id': a.event, 'guest_id': r['guest_id'], 'status': status}
        if r.get('message') and not a.no_message:
            body['message'] = r['message'][:200]
        req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                     headers={'x-luma-api-key': k, 'Content-Type': 'application/json',
                                              'User-Agent': 'curl/8.7.1'},
                                     method='POST')
        try:
            urllib.request.urlopen(req, timeout=30)
            ok += 1
            with open(log_path, 'a') as f:
                f.write(r['guest_id'] + '\n')
            print(f"  [{i}/{len(rows)}] ok    {r['name']}")
        except urllib.error.HTTPError as ex:
            detail = ex.read().decode()[:160]
            failures.append((r['name'], r['guest_id'], f'HTTP {ex.code} {detail}'))
            print(f"  [{i}/{len(rows)}] FAIL  {r['name']}  HTTP {ex.code}  {detail}")
        except Exception as ex:
            failures.append((r['name'], r['guest_id'], str(ex)[:160]))
            print(f"  [{i}/{len(rows)}] FAIL  {r['name']}  {ex}")
        time.sleep(0.4)          # undocumented rate limits, be polite

    print(f'\n{status}: {ok} ok, {len(failures)} failed')
    for n, g, e in failures:
        print(f'  {n}  {g}  {e}')
    print(f'\nSent ids logged to {log_path}; re-running skips them.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Send (or stage as Gmail drafts) one personalized email per attendee.

The research is what makes these worth sending: each body carries a hook drawn
from what that person actually does, plus their table number.

Setup once:
  1. App password at myaccount.google.com/apppasswords
  2. printf '%s' 'THEAPPPASSWORD' > ~/.gmail_app_password && chmod 600 ~/.gmail_app_password

  python3 send_emails.py --csv out/emails.csv                 # DRY RUN
  python3 send_emails.py --csv out/emails.csv --draft --limit 3   # eyeball 3 in Gmail
  python3 send_emails.py --csv out/emails.csv --draft             # stage them all
  python3 send_emails.py --csv out/emails.csv --go --limit 3      # send 3
  python3 send_emails.py --csv out/emails.csv --go                # send the rest

emails.csv columns: name, email, subject, body  (anything else is ignored, e.g.
table, hook — keep them, they make the file reviewable).

Sent addresses are logged next to the CSV and skipped on re-run, so a partial
send is safe to resume. Default is Gmail drafts, not sending: read ten of them
before any of it leaves the building.
"""
import argparse, csv, imaplib, os, smtplib, ssl, sys, time
from email.message import EmailMessage
from email.utils import formatdate


def password():
    p = os.environ.get('GMAIL_APP_PASSWORD')
    if p:
        return p.strip()
    f = os.path.expanduser('~/.gmail_app_password')
    if os.path.exists(f):
        return open(f).read().strip()
    sys.exit('No app password. Put it in ~/.gmail_app_password or set GMAIL_APP_PASSWORD.')


def build(r, sender, name):
    m = EmailMessage()
    m['From'] = f'{name} <{sender}>' if name else sender
    m['To'] = r['email']
    m['Subject'] = r['subject']
    m['Date'] = formatdate(localtime=True)
    m.set_content(r['body'])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--from', dest='sender', required=True, help='sending address')
    ap.add_argument('--from-name', default='')
    ap.add_argument('--draft', action='store_true', help='stage in Gmail Drafts, send nothing')
    ap.add_argument('--go', action='store_true', help='actually send')
    ap.add_argument('--limit', type=int)
    a = ap.parse_args()

    log_path = os.path.join(os.path.dirname(os.path.abspath(a.csv)), '.emails-sent.log')
    done = set() if a.draft else ({l.strip() for l in open(log_path)} if os.path.exists(log_path) else set())

    rows = [r for r in csv.DictReader(open(a.csv)) if r.get('email') and r['email'] not in done]
    for r in rows:
        if not r.get('subject') or not r.get('body'):
            sys.exit(f"row for {r.get('email')} is missing subject or body")
    if a.limit:
        rows = rows[:a.limit]
    print(f'{len(rows)} emails ({len(done)} already sent, skipped)')
    if not rows:
        return

    if a.draft:
        pw = password()
        box = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        box.login(a.sender, pw)
        ok = fail = 0
        for i, r in enumerate(rows, 1):
            try:
                box.append('"[Gmail]/Drafts"', '\\Draft', imaplib.Time2Internaldate(time.time()),
                           build(r, a.sender, a.from_name).as_bytes())
                ok += 1
                print(f"  [{i}/{len(rows)}] draft {r['name']}")
            except Exception as ex:
                fail += 1
                print(f"  [{i}/{len(rows)}] FAIL  {r['name']}  {ex}")
            time.sleep(0.3)
        box.logout()
        print(f'\n{ok} drafts created, {fail} failed. They are in Gmail under Drafts.')
        return

    if not a.go:
        print('\nDRY RUN. --draft stages them in Gmail, --go sends. First 3:\n')
        for r in rows[:3]:
            print(f"  {r['name']}  <{r['email']}>" + (f"  table {r['table']}" if r.get('table') else ''))
            print(f"    subject: {r['subject']}")
            print(f"    hook:    {r.get('hook') or '(generic)'}")
        print(f'\n  ... and {max(0, len(rows) - 3)} more')
        print(f'\nThis sends {len(rows)} individual emails from {a.sender}. Not reversible.')
        return

    pw = password()
    ok, failures = 0, []
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as s:
        s.login(a.sender, pw)
        for i, r in enumerate(rows, 1):
            try:
                s.send_message(build(r, a.sender, a.from_name))
                ok += 1
                with open(log_path, 'a') as log:
                    log.write(r['email'] + '\n')
                print(f"  [{i}/{len(rows)}] ok    {r['name']}")
            except Exception as ex:
                failures.append((r['name'], r['email'], str(ex)[:160]))
                print(f"  [{i}/{len(rows)}] FAIL  {r['name']}  {ex}")
            time.sleep(1.2)      # Gmail throttles bursts

    print(f'\nsent {ok}, failed {len(failures)}')
    for n, e, err in failures:
        print(f'  {n}  {e}  {err}')
    print(f'\nSent addresses logged to {log_path}; re-running skips them.')


if __name__ == '__main__':
    main()

"""The Claude & Coffee gate timeline, shared by new_event.py and status.py.

`t` is days before the event. Ordering is by t descending, so the list reads as
the run of the whole thing. `check` is how the gate proves itself done:
  ("json", "dotted.path")  truthy value in event.json
  ("file", "glob")         at least one match under the event folder
  ("any", [check, ...])    any one of them
`blocking` gates stop the ones after them; a soft gate slips without breaking.
"""

GATES = [
    dict(t=42, key='date', title='Date, format, and topic chosen', blocking=True,
         check=('json', 'date'), skill=None,
         why='Format is a money decision, not a naming one. A Workshop carries $50 of '
             'attendee credits and a Meetup does not, and you cannot change it later.'),
    dict(t=42, key='luma_request', title='Luma event requested from Anthropic', blocking=True,
         check=('json', 'luma.requested_from_anthropic'), skill=None,
         why='Anthropic builds the page. You do not publish it yourself, so this is a '
             'dependency on someone else and it goes first.'),
    dict(t=35, key='venue', title='Venue confirmed, with an ITEMIZED quote', blocking=True,
         check=('json', 'venue.itemized_invoice'), skill=None,
         why='Ask for space rental separated from food and beverage BEFORE booking. '
             'Reimbursement only covers venue, refreshments, and printed assets, and a '
             'lump-sum invoice cannot be split up after the fact.'),
    dict(t=35, key='preapproval', title='Pre-approval, if the quote exceeds the cap', blocking=False,
         check=('any', [('json', 'budget.preapproval_granted'), ('json', '_under_cap')]),
         skill=None,
         why='Written pre-approval from community@anthropic.com must come BEFORE the spend. '
             'Asking afterwards does not work; on Aug 11 that cost roughly $1,110.'),
    dict(t=28, key='published', title='Luma page live, copy kit posted', blocking=True,
         check=('json', 'luma.published'), skill='ambassador:claude-and-coffee',
         why='Promotion needs a week minimum to fill a room, and three to four weeks to '
             'fill it with the right people. Copy templates are in reference/copy-kit.md.'),
    dict(t=21, key='room_brief', title='Room brief locked with the host', blocking=True,
         check=('json', 'room_brief.personas'), skill='ambassador:event-attendee-research',
         why='Who belongs in the room is a decision, and the research tool refuses to run '
             'without it. Settle personas, headcounts, industry mix, and social presence.'),
    dict(t=14, key='banner', title='Roll-up banner ordered', blocking=False,
         check=('any', [('json', 'artifacts.banner.ordered'), ('file', 'banner/banner-print.pdf')]),
         skill='ambassador:event-rollup-banner',
         why='Vistaprint ships. Two weeks is the honest lead time; inside one week you are '
             'paying for tracked express and hoping.'),
    dict(t=10, key='research', title='Deep research pass done, approvals pushed', blocking=True,
         check=('file', 'ranking.csv'), skill='ambassador:event-attendee-research',
         why='Research the plausible top plus a margin, re-run every low-confidence profile, '
             'then push approvals. Approved guests need time to put it in a calendar.'),
    dict(t=7, key='deck', title='Deck built', blocking=False,
         check=('any', [('json', 'artifacts.deck.built'), ('file', '*.html')]),
         skill='ambassador:claude-community-deck',
         why='Build it while the banner is in transit. Late registrants get a second '
             'research pass this week too.'),
    dict(t=5, key='tables', title='Workshop tables assigned', blocking=False,
         check=('file', 'workshop-groups.csv'), skill='ambassador:event-attendee-research',
         why='Industry cluster, then role level, then a builder seeded at every table. '
             'Table numbers feed the badges, the board, and the day-before email.'),
    dict(t=5, key='badges', title='Name badges printed', blocking=False,
         check=('any', [('json', 'artifacts.badges.printed'), ('file', 'badges/badges-print.pdf')]),
         skill='ambassador:event-name-badges',
         why='Staples for stock and printing. Buy 15% more stock than headcount: walk-ups, '
             'misspellings caught at the door, and one jammed sheet come out of the same box.'),
    dict(t=2, key='board', title='Welcome board ordered', blocking=False,
         check=('any', [('json', 'artifacts.board.ordered'), ('file', 'board/board-print.pdf')]),
         skill='ambassador:event-welcome-board',
         why='FedEx Office turns it around same day, which is why it goes last. The run of '
             'show keeps moving until it does not.'),
    dict(t=1, key='daybefore', title='Day-before emails sent, board and badges collected', blocking=False,
         check=('file', 'emails.csv'), skill='ambassador:event-attendee-research',
         why='Personalized, one hook per person from their research, with their table number. '
             'Collect the printed artifacts today, not on the morning of.'),
    dict(t=0, key='run', title='Run of show', blocking=False,
         check=('json', '_never'), skill=None,
         why='reference/run-of-show.md. Doors, keynote, coworking, close, settle the tab.'),
    dict(t=-1, key='invoices', title='Itemized invoices collected, tab settled', blocking=True,
         check=('json', '_never'), skill=None,
         why='Chase the venue for the itemized invoice while you are still fresh in their '
             'inbox. Chase any refundable deposit separately; it is not a claimable cost.'),
    dict(t=-3, key='reimbursement', title='Reimbursement submitted', blocking=True,
         check=('json', '_never'), skill=None,
         why='Typeform, access code 419736. Itemized, invoice link not a payment link, '
             'Mercury or Stripe or PayPal or Revolut. Payouts run every Friday, so submitting '
             'on a Friday rolls you a week.'),
    dict(t=-7, key='recap', title='Recap posted, roster filed', blocking=False,
         check=('json', '_never'), skill=None,
         why='NOW you may credit speakers publicly. The program rule holds speaker promotion '
             'until after the event, and it exists to protect people from schedule changes.'),
]


def gate(key):
    return next((g for g in GATES if g['key'] == key), None)

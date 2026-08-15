#!/usr/bin/env python3
"""Composite scoring + seat allocation for event attendees.

  python3 score.py --roster roster.csv --research research.jsonl --seats 100 --out ./out

Inputs
  roster.csv     one row per registrant. Needs `email`. Uses `guest_id`, `name`,
                 `status` and any form columns it can auto-detect (org, role,
                 company size, industry, Claude Code experience, proficiency).
  research.jsonl one JSON object per researched person, keyed by `email`.
                 Fields (all optional, controlled vocabularies in reference/scoring.md):
                   verified_title, verified_company, company_stage, revenue_signal,
                   social_reach, social_detail, community_leader, community_detail,
                   notability (0-10), industry_cluster, research_confidence, note
                 Unresearched people still score; they just cannot earn the
                 research-only points. That is intentional: research is what
                 separates the top of the list, so research the plausible top first.
  config.json    optional overrides: weights, quotas, seats, focus verticals,
                 brand list, company cap, column map. See --dump-config.

Outputs (in --out)
  ranking.csv      everyone, ranked, with the score broken into its parts
  approve-list.csv action=approve|waitlist rows ready for luma_status.py
  summary.txt      the numbers to read back before anything is sent

Nothing here contacts Luma or sends mail. This step is reversible on purpose.
"""
import argparse, csv, json, os, re, sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------- vocabularies
SOCIAL = {'none': 0, 'unknown': 2, 'small': 8, 'medium': 18, 'large': 26}
STAGE = {'none': 0, 'side-project': 1, 'unknown': 4, 'bootstrapped': 8,
         'agency-or-consultancy': 8, 'pre-seed': 8, 'seed': 11, 'series-a': 13,
         'series-b+': 14, 'growth': 14, 'public': 12}
REVENUE = {'none': 0, 'unknown': 3, 'early': 5, 'meaningful': 8, 'substantial': 10}
SIZE_PTS = [(r'5000\+|5,000\+|10000|enterprise', 8), (r'501|1000|1,000|5000', 6),
            (r'51|101|201|500', 4), (r'\b1\b|2-10|11-50|solo|self', 2)]
TITLE_BANDS = [
    ('founder', r'\b(founder|co-?founder|cofounder)\b'),
    ('executive', r'\b(ceo|coo|cto|cfo|cpo|ciso|chief|president|managing (partner|director)|general partner|\bgp\b|owner)\b'),
    ('vp', r'\b(vp|vice president|head of|svp|evp)\b'),
    ('director', r'\b(director|principal)\b'),
    ('senior_manager', r'\b(senior manager|sr\.? manager|lead|staff|senior (engineer|scientist|counsel))\b'),
    ('manager', r'\bmanager\b'),
    ('student', r'\b(student|intern|candidate|mba \d|phd candidate)\b'),
    ('early', r'\b(analyst|associate|junior|entry|coordinator|assistant)\b'),
]
TITLE_PTS = {'executive': 14, 'founder': 13, 'vp': 12, 'director': 11,
             'senior_manager': 9, 'manager': 8, 'mid': 6, 'early': 4, 'student': 2}
ROLE_TIER = {'executive': 5, 'founder': 5, 'vp': 5, 'director': 5, 'senior_manager': 4,
             'manager': 4, 'mid': 3, 'early': 2, 'student': 1}
ROLE_BAND = {'executive': 'Executive / VP / Director', 'founder': 'Founder',
             'vp': 'Executive / VP / Director', 'director': 'Executive / VP / Director',
             'senior_manager': 'Manager / Senior Manager', 'manager': 'Manager / Senior Manager',
             'mid': 'Mid-level', 'early': 'Early career / Student', 'student': 'Early career / Student'}
CC_EXP = [(r'daily', 5), (r'regular|multiple times', 4), (r'occasional', 2), (r'new but|never|curious', 1)]
PROFICIENCY = [(r'agents on loops|build systems', 5), (r'super technical|lots of automation', 5),
               (r'own skills|connectors', 4), (r'projects and skills', 3),
               (r'casually prompting', 1), (r'novice|starting out', 0)]

DEFAULTS = {
    'seats': None,
    'weights': {'influence': 40, 'seniority': 30, 'substance': 24,
                'notability': 12, 'depth': 10, 'vertical': 6},
    'community_leader_points': 18,
    'brand_points': 8,
    'focus_verticals': ['fintech', 'finance', 'legal', 'private equity', 'edtech', 'education'],
    'company_cap': 2,
    'personas': [],        # REQUIRED, the room brief. See assets/personas.json
    'industry_targets': {},  # floors, e.g. {"Financial Services": 25, "Legal": "10%"}
    'industry_caps': {},     # ceilings, same shape
    'brands': [],          # extra recognizable employers, matched case-insensitively
    'columns': {},         # explicit column overrides, e.g. {"role": "What is your role?"}
}
# Recognizable-employer anchor list, comma separated, matched as a substring of the
# verified company (lowercased). Extend per event via config "brands".
BRANDS = """
google, apple, amazon, microsoft, meta, netflix, nvidia, openai, anthropic, stripe,
airbnb, uber, lyft, coinbase, datadog, snowflake, databricks, figma, notion, vercel,
jpmorgan, jp morgan, goldman sachs, morgan stanley, citigroup, blackrock, blackstone,
kkr, carlyle, bridgewater, two sigma, jane street, citadel, point72, nasdaq, nyse,
american express, amex, visa, mastercard, paypal, plaid, ramp, brex, robinhood,
mckinsey, bain, bcg, boston consulting, deloitte, pwc, kpmg, accenture, capgemini,
nyu, columbia, harvard, stanford, yale, princeton, cornell, berkeley, mit,
tiktok, bytedance, snap inc, pinterest, spotify, shopify, salesforce, oracle, ibm,
intel, qualcomm, walmart, nike, disney, bloomberg, reuters, new york times,
skadden, kirkland, latham, sullivan & cromwell, nixon peabody, paul weiss, davis polk
"""


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())


def band(text):
    t = norm(text)
    for name, pat in TITLE_BANDS:
        if re.search(pat, t):
            return name
    return 'mid' if t else 'mid'


def lookup(patterns, text, default=0):
    t = norm(text)
    for pat, pts in patterns:
        if re.search(pat, t):
            return pts
    return default


# ---------------------------------------------------------------- column detect
CANDIDATES = {
    'email': ['email'],
    'name': ['name', 'full name'],
    'guest_id': ['guest_id', 'api_id'],
    'status': ['status', 'approval_status'],
    'registered_at': ['registered_at', 'registered'],
    'org': ['org', 'company', 'organization', 'where do you work', 'employer'],
    'role': ['role', 'title', 'seniority', 'your role'],
    'company_size': ['size', 'headcount', 'how many people', 'employees'],
    'industry': ['industry', 'vertical', 'sector'],
    'claude_code_exp': ['claude code', 'experience with claude'],
    'ai_proficiency': ['proficiency', 'describe your', 'how would you describe'],
    'wants_to_learn': ['learn', 'hoping', 'want to get', 'interested in'],
    'linkedin': ['linkedin'],
}


def detect(headers, overrides):
    m = {}
    low = {h: norm(h) for h in headers}
    for field, needles in CANDIDATES.items():
        if field in overrides:
            m[field] = overrides[field]
            continue
        hit = None
        for h in headers:
            if low[h] == field:
                hit = h
                break
        if not hit:
            for n in needles:
                for h in headers:
                    if n in low[h]:
                        hit = h
                        break
                if hit:
                    break
        if hit:
            m[field] = hit
    return m


# ---------------------------------------------------------------- scoring
def score_person(row, res, cfg, brands):
    g = lambda f: row.get(cfg['_map'].get(f, ''), '') or ''
    w = cfg['weights']

    social = SOCIAL.get(norm(res.get('social_reach')), 0)
    community = cfg['community_leader_points'] if norm(res.get('community_leader')) in ('yes', 'true', '1') else 0
    influence = min(w['influence'], social + community)

    title_src = res.get('verified_title') or g('role')
    b = band(title_src)
    if b == 'mid' and g('role'):
        b = band(g('role'))
    title_pts = TITLE_PTS.get(b, 6)

    founder_check = ''
    if b == 'founder':
        stage, rev = norm(res.get('company_stage')), norm(res.get('revenue_signal'))
        if stage in ('series-a', 'series-b+', 'growth', 'public') or rev in ('meaningful', 'substantial'):
            title_pts, founder_check = 17, 'verified'
        elif stage in ('none', 'side-project') and norm(res.get('research_confidence')) == 'high':
            title_pts, founder_check = 5, 'demoted'
        else:
            founder_check = 'benefit-of-doubt'

    size_pts = lookup(SIZE_PTS, g('company_size'))
    company = norm(res.get('verified_company') or g('org'))
    brand_hit = next((br for br in brands if br and br in company), '')
    seniority = min(w['seniority'], title_pts + size_pts + (cfg['brand_points'] if brand_hit else 0))

    substance = min(w['substance'],
                    STAGE.get(norm(res.get('company_stage')), 0) +
                    REVENUE.get(norm(res.get('revenue_signal')), 0))

    try:
        notability = min(w['notability'], round(float(res.get('notability') or 0) * (w['notability'] / 10.0)))
    except (TypeError, ValueError):
        notability = 0

    depth = min(w['depth'], lookup(CC_EXP, g('claude_code_exp')) + lookup(PROFICIENCY, g('ai_proficiency')))

    hay = ' '.join([norm(res.get('industry_cluster')), norm(g('industry')), company])
    vertical = w['vertical'] if any(v in hay for v in cfg['focus_verticals']) else 0

    total = influence + seniority + substance + notability + depth + vertical
    return {
        'score': total, 'influence': influence, 'seniority': seniority,
        'substance': substance, 'notability': notability, 'depth': depth,
        'vertical': vertical, 'role_level': b, 'role_tier': ROLE_TIER.get(b, 3),
        'role_band': ROLE_BAND.get(b, 'Mid-level'), 'brand_anchor': brand_hit,
        'founder_check': founder_check, 'company_size_pts': size_pts,
        'is_builder': 'yes' if depth >= 8 else '',
    }


# ---------------------------------------------------------------- personas
def matches(p, rules):
    """Every rule must pass. See assets/personas.json for the accepted value forms."""
    for field, want in (rules or {}).items():
        if field == 'title_match':
            hay = norm(f"{p.get('verified_title','')} {p.get('self_reported_role','')}")
            if not re.search(want, hay):
                return False
            continue
        have = p.get(field, '')
        if isinstance(want, dict):
            if 'any' in want:
                if bool(have) != bool(want['any']):
                    return False
            if 'not' in want and norm(str(have)) in {norm(str(x)) for x in want['not']}:
                return False
            for key, op in (('min', lambda a, b: a >= b), ('max', lambda a, b: a <= b)):
                if key in want:
                    try:
                        if not op(float(have or 0), float(want[key])):
                            return False
                    except (TypeError, ValueError):
                        return False
        else:
            allowed = {norm(str(x)) for x in (want if isinstance(want, list) else [want])}
            if norm(str(have)) not in allowed:
                return False
    return True


def assign_persona(p, personas):
    """First match wins, so persona order is the priority order."""
    for d in personas:
        if matches(p, d.get('match')):
            return d['name']
    return 'Unassigned'


def resolve_target(v, seats):
    """A target is a headcount, a "25%" of seats, or null for no floor."""
    if v in (None, '', 0):
        return 0
    if isinstance(v, str) and v.strip().endswith('%'):
        return int(round(float(v.strip().rstrip('%')) / 100 * (seats or 0)))
    return int(v)


# ---------------------------------------------------------------- selection
def allocate(people, cfg):
    """Seat allocation against the room brief: forced invites, then persona floors,
    then industry floors, then the highest remaining scores. Caps are enforced in
    every pass. Unfillable floors spill rather than sitting empty, and say so."""
    seats = cfg.get('seats')
    for p in people:
        p['action'], p['why'] = 'waitlist', ''
    if not seats:
        return []
    ccap = cfg.get('company_cap') or 999
    personas = cfg['personas']
    floors = [('persona', {d['name']: resolve_target(d.get('target'), seats) for d in personas
                           if resolve_target(d.get('target'), seats)}),
              ('industry_cluster', {k: resolve_target(v, seats)
                                    for k, v in (cfg.get('industry_targets') or {}).items()})]
    caps = {'persona': {d['name']: resolve_target(d.get('cap'), seats) for d in personas
                        if d.get('cap') not in (None, '')},
            'industry_cluster': {k: resolve_target(v, seats)
                                 for k, v in (cfg.get('industry_caps') or {}).items()}}
    taken, per_company, counts, notes = 0, Counter(), {'persona': Counter(), 'industry_cluster': Counter()}, []

    def company(p):
        return norm(p['verified_company'] or p['self_reported_org']) or f"?{p['email']}"

    def blocked(p):
        if per_company[company(p)] >= ccap:
            return f'company cap ({ccap})'
        for dim, lim in caps.items():
            key = p.get(dim, '')
            if key in lim and counts[dim][key] >= lim[key]:
                return f'{key} cap ({lim[key]})'
        return ''

    def take(p, why):
        nonlocal taken
        p['action'], p['why'] = 'approve', why
        per_company[company(p)] += 1
        counts['persona'][p['persona']] += 1
        counts['industry_cluster'][p.get('industry_cluster', '')] += 1
        taken += 1

    for p in people:
        if p.get('forced') and taken < seats:
            take(p, 'forced')

    for dim, targets in floors:
        for key, floor in targets.items():
            got = counts[dim][key]
            for p in people:
                if taken >= seats or got >= floor:
                    break
                if p['action'] == 'approve' or p.get(dim, '') != key or blocked(p):
                    continue
                take(p, f'floor:{key}')
                got += 1
            if got < floor:
                notes.append(f'{key}: floor {floor}, only {got} qualified, {floor - got} seats spilled')

    for p in people:
        if taken >= seats:
            break
        if p['action'] == 'approve':
            continue
        why = blocked(p)
        if why:
            p['why'] = f'held: {why}'
            continue
        take(p, 'score')
    return notes


# ---------------------------------------------------------------- main
OUT_COLS = ['rank', 'score', 'action', 'status', 'guest_id', 'name', 'email',
            'self_reported_org', 'self_reported_role', 'verified_title', 'verified_company',
            'persona', 'why', 'role_band', 'role_level', 'role_tier', 'industry_cluster', 'company_stage',
            'revenue_signal', 'social_reach', 'community_leader', 'brand_anchor',
            'founder_check', 'is_builder', 'influence', 'seniority', 'substance',
            'notability', 'depth', 'vertical', 'claude_code_exp', 'ai_proficiency',
            'wants_to_learn', 'research_confidence', 'social_detail', 'community_detail', 'note']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--roster', required=False)
    ap.add_argument('--research')
    ap.add_argument('--config')
    ap.add_argument('--seats', type=int)
    ap.add_argument('--out', default='.')
    ap.add_argument('--force', help='file of emails to seat regardless of score (referrals, VIPs)')
    ap.add_argument('--exclude', help='file of emails to never seat')
    ap.add_argument('--dump-config', action='store_true')
    ap.add_argument('--list-personas', action='store_true',
                    help='print the persona library and exit')
    ap.add_argument('--personas', help='"library" to use every library persona unweighted, '
                                       'for a first look at the pool before the room brief exists')
    a = ap.parse_args()

    cfg = json.loads(json.dumps(DEFAULTS))
    if a.config and os.path.exists(a.config):
        user = json.load(open(a.config))
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v

    lib = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      '..', 'assets', 'personas.json')))['library']
    if a.list_personas:
        for d in lib:
            print(f"\n{d['name']}\n  {d['why']}\n  match: {json.dumps(d['match'])}")
        return
    if a.personas == 'library' or cfg.get('personas') in ('library', 'default'):
        cfg['personas'] = lib
    if a.dump_config:
        print(json.dumps(cfg, indent=2))
        return
    if not a.roster:
        sys.exit('--roster is required')
    if a.seats:
        cfg['seats'] = a.seats

    if not cfg.get('personas'):
        sys.exit(
            'No personas defined.\n\n'
            'Who is supposed to be in this room is a decision, not a default. Ask the host\n'
            'which personas they want and how many of each, then put them in config.json:\n\n'
            '  {"seats": 100, "personas": [\n'
            '     {"name": "Community operator", "target": 20, "match": {"community_leader": "yes"}},\n'
            '     {"name": "Verified founder",   "target": "25%", "match": {"founder_check": "verified"}},\n'
            '     {"name": "Practitioner",       "match": {}}\n'
            '  ]}\n\n'
            'Run --list-personas for the library to pick from, or --personas library to see\n'
            'the shape of the pool before the brief exists.')
    if any(d.get('match') for d in cfg['personas']) and cfg['personas'][-1].get('match'):
        print('NOTE: the last persona has match rules, so anyone matching none of them lands in '
              '"Unassigned" and can only be seated by score. Add a catch-all {"match": {}} last '
              'if that is not what you want.\n', file=sys.stderr)

    brands = sorted({norm(b) for b in BRANDS.split(',') if len(norm(b)) > 2} |
                    {norm(b) for b in cfg.get('brands', []) if len(norm(b)) > 2},
                    key=len, reverse=True)

    rows = list(csv.DictReader(open(a.roster)))
    if not rows:
        sys.exit('empty roster')
    cfg['_map'] = detect(list(rows[0].keys()), cfg.get('columns', {}))
    if 'email' not in cfg['_map']:
        sys.exit(f"no email column found in: {', '.join(rows[0].keys())}")

    research = {}
    if a.research and os.path.exists(a.research):
        for line in open(a.research):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            research[norm(d.get('email'))] = d

    forced = {norm(l) for l in open(a.force)} if a.force else set()
    excluded = {norm(l) for l in open(a.exclude)} if a.exclude else set()

    people = []
    for row in rows:
        email = norm(row.get(cfg['_map']['email']))
        if not email or email in excluded:
            continue
        res = research.get(email, {})
        s = score_person(row, res, cfg, brands)
        g = lambda f: row.get(cfg['_map'].get(f, ''), '') or ''
        p = {**s,
             'name': g('name') or row.get('name', ''),
             'email': email,
             'guest_id': g('guest_id'),
             'status': g('status'),
             'self_reported_org': g('org'),
             'self_reported_role': g('role'),
             'claude_code_exp': g('claude_code_exp'),
             'ai_proficiency': g('ai_proficiency'),
             'wants_to_learn': g('wants_to_learn'),
             'forced': email in forced}
        for f in ('verified_title', 'verified_company', 'company_stage', 'revenue_signal',
                  'social_reach', 'social_detail', 'community_leader', 'community_detail',
                  'industry_cluster', 'research_confidence', 'note'):
            p[f] = res.get(f, '') or ''
        p['research_confidence'] = p['research_confidence'] or 'none'
        p['persona'] = assign_persona(p, cfg['personas'])
        people.append(p)

    people.sort(key=lambda p: (-p['score'], p['name']))
    notes = allocate(people, cfg) or []
    for i, p in enumerate(people, 1):
        p['rank'] = i

    os.makedirs(a.out, exist_ok=True)
    rank_path = os.path.join(a.out, 'ranking.csv')
    with open(rank_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS, extrasaction='ignore')
        w.writeheader()
        for p in people:
            w.writerow(p)

    appr_path = os.path.join(a.out, 'approve-list.csv')
    with open(appr_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['action', 'rank', 'score', 'guest_id', 'name', 'email', 'verified_title',
                    'verified_company', 'persona', 'industry_cluster', 'community_leader',
                    'social_reach', 'research_confidence', 'note', 'message'])
        for p in people:
            w.writerow([p['action'], p['rank'], p['score'], p['guest_id'], p['name'], p['email'],
                        p['verified_title'], p['verified_company'], p['persona'],
                        p['industry_cluster'], p['community_leader'], p['social_reach'],
                        p['research_confidence'], p['note'], ''])

    lines = [f'{len(people)} people scored, {sum(1 for p in people if p["action"] == "approve")} approved, '
             f'{sum(1 for p in people if p["action"] == "waitlist")} waitlisted']
    lines.append(f'score range {people[-1]["score"]} to {people[0]["score"]} '
                 f'(max possible {sum(cfg["weights"].values())})')
    lines.append('')
    lines.append('columns detected: ' + ', '.join(f'{k}={v}' for k, v in sorted(cfg['_map'].items())))
    thin = [f for f in ('role', 'org', 'company_size', 'claude_code_exp', 'ai_proficiency')
            if f not in cfg['_map']]
    if thin:
        lines.append(f'  WARNING: no column found for {", ".join(thin)}, so those points are '
                     'zero for everyone. Map them with "columns" in config.json.')
    lines.append('research confidence: ' + ', '.join(f'{k} {v}' for k, v in
                 Counter(p['research_confidence'] for p in people).most_common()))
    seats = cfg.get('seats') or 0
    got = Counter(p['persona'] for p in people if p['action'] == 'approve')
    pool = Counter(p['persona'] for p in people)
    lines.append('\nThe room, against the brief')
    lines.append(f"  {'persona':<26}{'asked':>7}{'seated':>8}{'in pool':>9}")
    for d in cfg['personas'] + ([{'name': 'Unassigned'}] if pool['Unassigned'] else []):
        n = d['name']
        want = resolve_target(d.get('target'), seats)
        capv = resolve_target(d.get('cap'), seats)
        flag = ''
        if want and got[n] < want:
            flag = f'  <- short by {want - got[n]}, only {pool[n]} in the pool'
        elif capv and got[n] >= capv:
            flag = f'  <- at cap {capv}'
        lines.append(f"  {n[:26]:<26}{(want or '-'):>7}{got[n]:>8}{pool[n]:>9}{flag}")
    if cfg.get('industry_targets') or cfg.get('industry_caps'):
        ig = Counter(p['industry_cluster'] for p in people if p['action'] == 'approve')
        lines.append('  industry mix: ' + ', '.join(f'{k or "?"} {v}' for k, v in ig.most_common()))
    lines.append('role bands (seated): ' + ', '.join(f'{k} {v}' for k, v in
                 Counter(p['role_band'] for p in people if p['action'] == 'approve').most_common()))
    lines.append('audience (seated): ' + ', '.join(f'{k or "unresearched"} {v}' for k, v in
                 Counter(p['social_reach'] for p in people if p['action'] == 'approve').most_common()))
    fc = Counter(p['founder_check'] for p in people if p['founder_check'])
    if fc:
        lines.append('founder check: ' + ', '.join(f'{k} {v}' for k, v in fc.most_common()))
    unresearched_top = [p for p in people[:max(1, (cfg.get('seats') or 50))] if p['research_confidence'] == 'none']
    if unresearched_top:
        lines.append(f'\nWARNING: {len(unresearched_top)} people inside the seat cut have no research. '
                     'They are scored on self-report alone and are the most likely misses.')
    if notes:
        lines.append('\nfloors that could not be filled (seats spilled to the next-highest scores):')
        lines += ['  ' + n for n in notes]
        lines.append('  Supply is the binding constraint here, not the ranking. Either the brief '
                     'wants someone who did not register, or the research has not found them yet.')
    summary = '\n'.join(lines)
    open(os.path.join(a.out, 'summary.txt'), 'w').write(summary + '\n')
    print(summary)
    print(f'\nwrote {rank_path}\n      {appr_path}')


if __name__ == '__main__':
    main()

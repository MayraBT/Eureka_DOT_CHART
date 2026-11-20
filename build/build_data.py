"""Assemble the Eureka TEKS Lookup data constants from the extracted sources.
Inputs (all in this folder): ipc/*.json, scaf.json, vocab.json, perf.json, moves/moves_*.json, ipc/topics.json
Output: data.js (the data constants for index.html) and report.txt (validation notes)."""
import json, glob, re, datetime, os
D = lambda s: datetime.date.fromisoformat(s)
DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
report = []
scaf = json.load(open('scaf.json'))
TEKS_TXT, TYPE = dict(scaf['TEKS']), dict(scaf['TYPE'])
K2 = json.load(open('teks_k2.json')) if os.path.exists('teks_k2.json') else {'TEKS': {}, 'TYPE': {}, 'STRAND': {}}
TEKS_TXT.update(K2['TEKS']); TYPE.update(K2['TYPE'])
topics = json.load(open('ipc/topics.json')) if os.path.exists('ipc/topics.json') else {}
if os.path.exists('ipc/topics_k2.json'): topics.update(json.load(open('ipc/topics_k2.json')))
GRADES = [g for g in 'K12345' if os.path.exists(f'ipc/cal_g{g}.json')]
GNAME = lambda g: 'Kindergarten' if g == 'K' else f'Grade {g}'
TE_FILE = json.load(open('ipc/g3_te.json'))
QUARTERS = {"1": {"start": "2026-08-10", "end": "2026-10-09", "weeks": 9},
            "2": {"start": "2026-10-12", "end": "2026-12-18", "weeks": 9},
            "3": {"start": "2027-01-04", "end": "2027-03-05", "weeks": 9}}


def lid_key(lid):
    m = re.match(r'M(\d+)\.(L|S)([\d]+)(?:-(\d+))?', lid)
    return (int(m.group(1)), int(m.group(3)), 0 if m.group(2) == 'L' else 1, int(m.group(4) or 0))


def qwk(w):
    return (1, w) if w <= 9 else (2, w - 9) if w <= 18 else (3, w - 18)


def load_weeks(g):
    weeks = []
    for f in sorted(glob.glob(f'ipc/g{g}_*.json')):
        if f.endswith('_te.json') or '2526' in f:
            continue
        for w in json.load(open(f))['weeks']:
            w['W'] = w['wk']
            weeks.append(w)
    # global week numbers: files written with wk = global week (1..18)
    return sorted(weeks, key=lambda w: w['W'])


COURSES = {}; TIG = {}
# TE_ONLY=1: teacher build that lists every Eureka lesson with the TEKS from its Teacher Edition
# topic overview (or Supplement overview); no IPC pacing, TEKS or links.
TE_ONLY = os.environ.get('TE_ONLY') == '1'
for g in GRADES:
    cal = json.load(open(f'ipc/cal_g{g}.json'))
    mods = cal['ss']['modules']
    weeks = [] if TE_ONLY else load_weeks(g)
    have = {w['W'] for w in weeks}
    missing = [w for w in range(1, 19) if w not in have]
    if missing: report.append(f'G{g}: weekly IPC missing for weeks {missing}')
    lessons = {}   # id -> {marks:{code:F/O}, days:[...]}
    tig = {}
    calweeks = []

    def touch(lid):
        return lessons.setdefault(lid, {'marks': {}, 'days': [], 'lo': None})

    for w in weeks:
        q, wkq = qwk(w['W'])
        start = D(w['start'])
        days = []
        for i, d in enumerate(w['days'][:5]):
            date = (start + datetime.timedelta(days=i)).isoformat()
            les = d.get('les') or []
            kind = d.get('kind') or ('lesson' if les else 'empty')
            note = d.get('note') or ''
            if kind in ('lesson', 'flex') and les:
                for lid in les:
                    L = touch(lid)
                    for c in d.get('teks', []):
                        c = c.strip().upper()
                        if re.match(r'^[\dK]\.\d+[A-Z]$', c): L['marks'][c] = 'F'
                    for c in d.get('bundled', []):
                        c = c.strip().upper()
                        if re.match(r'^[\dK]\.\d+[A-Z]$', c) and L['marks'].get(c) != 'F': L['marks'][c] = 'O'
                    if kind == 'lesson':
                        L['days'].append({'q': q, 'wk': wkq, 'day': DOW[i], 'date': date, 'act': ''})
                    if d.get('lo') and not L['lo']: L['lo'] = d['lo']
                    te = d.get('te')
                    if isinstance(te, dict) and te.get(lid):
                        tig.setdefault(lid, [])
                        if te[lid] not in tig[lid]: tig[lid].append(te[lid])
                act = 'Flex or reteach day' if kind == 'flex' else ''
                if note and kind == 'lesson' and re.search(r'combin|supplement|revised', note, re.I): act = note[:140]
                days.append({'date': date, 'dow': DOW[i], 'lid': les[0], 'also': les[1:], 'act': act, 'text': '', 'kind': 'lesson'})
            else:
                k = {'assess': 'assess', 'off': 'off'}.get(kind, 'empty')
                txt = d.get('text') or ('' if k == 'empty' else kind)
                if k == 'assess' and re.search(r'staar', txt, re.I): k = 'staar'
                days.append({'date': date, 'dow': DOW[i], 'lid': None, 'act': '', 'text': txt, 'kind': k})
        calweeks.append({'q': q, 'wk': wkq, 'start': w['start'], 'days': days})
    # Q3 from the quarterly calendar (lesson-level TEKS not yet posted)
    for w in ([] if TE_ONLY else cal['q3']['weeks']):
        if w['wk'] in have: continue   # the 2026-27 weekly IPC replaces the calendar for this week
        q, wkq = 3, w['wk'] - 18
        start = D(w['start']); days = []
        for i, d in enumerate(w['days'][:5]):
            date = (start + datetime.timedelta(days=i)).isoformat()
            les = d.get('les') or []
            kind = d.get('kind') or 'empty'
            if les and kind in ('lesson', 'flex'):
                for lid in les:
                    L = touch(lid)
                    if kind == 'lesson': L['days'].append({'q': q, 'wk': wkq, 'day': DOW[i], 'date': date, 'act': ''})
                    L['q3'] = True
                days.append({'date': date, 'dow': DOW[i], 'lid': les[0], 'also': les[1:], 'act': 'Flex or reteach day' if kind == 'flex' else (d.get('text') or ''), 'text': '', 'kind': 'lesson'})
            else:
                k = {'assess': 'assess', 'off': 'off'}.get(kind, 'empty')
                txt = d.get('text') or ''
                if re.search(r'staar', txt, re.I): k = 'staar'
                days.append({'date': date, 'dow': DOW[i], 'lid': None, 'act': '', 'text': txt, 'kind': k})
        calweeks.append({'q': q, 'wk': wkq, 'start': w['start'], 'days': days})
    # G3 weeks 1-4: teacher links from the anchor map
    if g == '3' and not TE_ONLY:
        for lid, disco in TE_FILE['disco'].items():
            tig.setdefault(lid, [f"https://drive.google.com/file/d/{TE_FILE['file']}/edit?disco={disco}"])
    # Q3 lessons still without TEKS: use last year's (2025-26) weekly IPC for the same Eureka lesson
    prevf = f'ipc/g{g}_q3_2526.json'
    if os.path.exists(prevf) and not TE_ONLY:
        n = 0
        for w in json.load(open(prevf))['weeks']:
            for d in w['days']:
                for lid in d.get('les') or []:
                    L = lessons.get(lid)
                    if not L or not L.get('q3'): continue
                    pm = L.setdefault('pmarks', {})
                    for c in d.get('teks', []):
                        c = c.strip().upper()
                        if re.match(r'^[\dK]\.\d+[A-Z]$', c): pm[c] = 'F'
                    for c in d.get('bundled', []):
                        c = c.strip().upper()
                        if re.match(r'^[\dK]\.\d+[A-Z]$', c) and pm.get(c) != 'F': pm[c] = 'O'
                    te = d.get('te')
                    if isinstance(te, dict) and te.get(lid) and lid not in tig: tig[lid] = [te[lid]]
        for lid, L in lessons.items():
            if L.get('q3') and not L['marks'] and L.get('pmarks'):
                L['marks'] = L['pmarks']; L['prev'] = True; n += 1
        report.append(f'G{g}: {n} Q3 lessons take TEKS from the 2025-26 Q3 IPC')
    titles = cal['lessons']
    # topics
    tmap = topics.get(g, {})
    # lessons no IPC lists yet: add them from the module Teacher Editions (topic overview TEKS)
    import glob as _glob
    _om = {m['n']: set(m.get('omit', [])) for m in mods}
    for _f in sorted(_glob.glob(f'ipc/te_overview/{g}_M*.json')) + sorted(_glob.glob(f'ipc/te_overview/{g}_supp.json')):
        for lid, X in json.load(open(_f)).items():
            _m = int(lid.split('.')[0][1:]); _n = int(lid.split('.L')[1]) if '.L' in lid else -1
            _codes = []
            for c in X['teks']:
                if not re.search(r'[A-Z]$', c): c = c + 'A' if (c + 'A') in TEKS_TXT and (c + 'B') not in TEKS_TXT else None
                if c and c not in _codes: _codes.append(c)
            if lid in lessons:
                # lesson is on the IPC but no IPC lists its TEKS yet: use the Teacher Edition's
                if not lessons[lid]['marks'] and not lessons[lid].get('pmarks'):
                    lessons[lid]['marks'] = {c: X.get('kind', 'O') for c in _codes}; lessons[lid]['te'] = True
                    report.append(f'G{g} {lid}: TEKS filled from the Teacher Edition overview')
                continue
            if _n in _om.get(_m, set()) and not TE_ONLY: continue
            lessons[lid] = {'lo': X['title'], 'marks': {c: ('F' if TE_ONLY else X.get('kind', 'O')) for c in _codes}, 'days': [], 'te': True, 'review': not _codes, 'topic': X.get('topic')}
            report.append(f'G{g} {lid}: added from the Teacher Edition overview')
    out_lessons = []
    modnames = {m['n']: m for m in mods}
    for lid in sorted(lessons, key=lid_key):
        m, num, sup, sub = lid_key(lid)
        L = lessons[lid]
        tp = tmap.get(f'M{m}', {})
        letter = next((t for t, (a, b) in tp.items() if a <= num <= b), None)
        if TE_ONLY and L.get('topic'): letter = L['topic']
        mod = modnames.get(m)
        letters = [t['t'] for t in mod['topics']] if mod else []
        if letter is None:
            # nearest earlier lesson's topic in the same module
            prev = [x for x in out_lessons if x['m'] == m]
            letter = letters[prev[-1]['t'] - 1] if prev and letters else (letters[0] if letters else 'A')
            report.append(f'G{g} {lid}: topic not mapped, used {letter}')
        t = letters.index(letter) + 1 if letter in letters else 1
        title = titles.get(lid) or L['lo'] or ''
        if TE_ONLY and not titles.get(lid): title = L['lo'] or ''
        if not titles.get(lid) and not TE_ONLY: report.append(f'G{g} {lid}: no calendar objective; title from IPC LO')
        marks = sorted(L['marks'].items(), key=lambda kv: (kv[1] != 'F', int(kv[0].split('.')[1][:-1]), kv[0][-1]))
        lab = str(num) if not sup else f"{num}-{sub}"
        out_lessons.append({'id': lid, 'm': m, 't': t, 'l': lab, 'title': title.rstrip('.') + '.', 'sub': '',
                            'note': ('Supplemental lesson' if sup else '') + (('; ' if sup else '') + ('TEKS from the Eureka Teacher Edition ' + ('Supplement overview' if sup else 'topic overview')) if L.get('te') else '') + (('; ' if sup else '') + 'TEKS from the 2025-26 Q3 weekly IPC (2026-27 not posted yet)' if L.get('prev') else ''), 'prev': bool(L.get('prev')), 'marks': [list(x) for x in marks], 'q3': bool(L.get('q3')) and not marks})
    if TE_ONLY:
        for L in out_lessons: L['note'] = 'Supplemental lesson' if '.S' in L['id'] else ''
    for L in out_lessons:
        if lessons[L['id']].get('review'):
            L['note'] = 'Year in Review: spiral review of the grade’s major work; the Teacher Edition lists no TEKS for it'
    used_mods = sorted({L['m'] for L in out_lessons})
    modules = []
    for n in used_mods:
        mm = modnames.get(n, {'name': f'Module {n}', 'topics': []})
        modules.append({'n': n, 'name': mm['name'], 'topics': [t['name'] for t in mm['topics']], 'letters': [t['t'] for t in mm['topics']],
                        'focus': [] if TE_ONLY else mm.get('focus', []), 'included': [] if TE_ONLY else mm.get('included', []), 'omit': [] if TE_ONLY else mm.get('omit', []), 'after_staar': [] if TE_ONLY else mm.get('after_staar', [])})
    # standards: every TEKS of the grade (scaffold), in code order
    codes = sorted([c for c in TEKS_TXT if c.startswith(g + '.')], key=lambda c: (int(c.split('.')[1][:-1]), c[-1]))
    standards = [{'code': c, 'type': TYPE[c], 'g7': False, 'desc': TEKS_TXT[c]} for c in codes]
    known = set(codes)
    for L in out_lessons:
        bad = [c for c, _ in L['marks'] if c not in known]
        if bad:
            report.append(f'G{g} {L["id"]}: TEKS not in Grade {g} list, dropped: {bad}')
            L['marks'] = [mk for mk in L['marks'] if mk[0] in known]
            L['note'] = (L['note'] + '; ' if L['note'] else '') + ('The Teacher Edition also lists earlier-grade TEKS: ' if TE_ONLY else 'The IPC also lists earlier-grade TEKS: ') + ', '.join(bad)
    pace = {}
    for lid, L in lessons.items():
        if not L['days']: continue
        ds = sorted(L['days'], key=lambda d: d['date'])
        pace[lid] = {'q': sorted({d['q'] for d in ds}), 'first': ds[0]['date'], 'last': ds[-1]['date'], 'days': ds}
    events = [e for e in cal.get('events', []) if re.search(r'staar', e['label'], re.I)]
    calweeks.sort(key=lambda w: w['start'])
    COURSES['g' + g.lower()] = {'key': 'g' + g.lower(), 'name': GNAME(g), 'title': f'{GNAME(g)} Eureka · TEKS Lookup', 'ipc': f'{GNAME(g)} Eureka Math', 'staar': g in '345',
                        'grade': g, 'q3note': (' · 2026-27 weekly IPCs' if all(w in have for w in range(19,28)) else (' · 2026-27 weekly IPCs for Q3 weeks 1–%d; later weeks paced from the 2026-27 Q3 calendar' % (max(w for w in have if w>=19)-18) + ('; their TEKS and Teacher links come from the 2025-26 Q3 weekly IPCs' if os.path.exists(f'ipc/g{g}_q3_2526.json') else '; their TEKS and Teacher links will come from the Q3 weekly IPCs when posted')) if any(w>=19 for w in have) else (' · paced from the 2026-27 Q3 calendar; lesson TEKS and Teacher links from the 2025-26 Q3 weekly IPCs until the 2026-27 weeklies are posted' if os.path.exists(f'ipc/g{g}_q3_2526.json') else ' · paced from the 2026-27 Q3 calendar; lesson TEKS and Teacher links will come from the Q3 weekly IPCs when posted')), 'unsched': 'not on the 2026-27 IPC (Q1–Q3)', 'notes': cal.get('notes', []),
                        'data': {'modules': modules, 'standards': standards, 'lessons': out_lessons},
                        'pace': {'lessons': pace, 'cal': {'quarters': QUARTERS, 'events': events}}, 'cal': calweeks}
    TEMOD = json.load(open('ipc/te_module.json')).get(g, {}) if os.path.exists('ipc/te_module.json') else {}
    if TE_ONLY: tig = {}
    for L in out_lessons:
        mod = L['id'].split('.')[0]
        if L['id'] not in tig and mod in TEMOD:
            tig[L['id']] = [TEMOD[mod]]
            report.append(f'G{g} {L["id"]}: Teacher link is the module TE file (no weekly IPC link)')
    TELES = json.load(open('ipc/te_lesson.json')).get(g, {}) if os.path.exists('ipc/te_lesson.json') else {}
    nles = 0
    for L in out_lessons:
        if L['id'] in TELES:
            tig[L['id']] = [f"https://drive.google.com/file/d/{TELES[L['id']]}/view"]; nles += 1
    if nles: report.append(f'G{g}: {nles} lessons link a single-lesson TE PDF')
    TIG['g' + g.lower()] = tig
    report.append(f'G{g}: {len(out_lessons)} lessons, {sum(1 for L in out_lessons if L["marks"])} with TEKS, {len(calweeks)} weeks, {len(tig)} teacher links, modules {used_mods}')

# vocabulary: English blocks with the matching Spanish block (same codes)
voc = json.load(open('vocab.json'))
blocks = []; byCode = {}
for g in '345':
    sp = {tuple(b['codes']): b for b in voc[g]['sp']}
    for b in voc[g]['en']:
        s = sp.get(tuple(b['codes']))
        if s:
            # merge split Spanish lines so counts line up with English
            for key in ('new', 'prev'):
                arr = list(s[key])
                while len(arr) > len(b[key]) and len(arr) > 1:
                    i = min(range(len(arr) - 1), key=lambda i: len(arr[i + 1]))
                    arr[i:i + 2] = [arr[i] + ' ' + arr[i + 1]]
                s[key] = arr
        blocks.append({'cluster': b['cluster'], 'sub': b['sub'], 'codes': b['codes'], 'new': b['new'], 'prev': b['prev'],
                       'sp': {'cluster': s['cluster'], 'sub': s['sub'], 'new': s['new'], 'prev': s['prev']} if s else None})
for i, b in enumerate(blocks):
    for c in b['codes']: byCode.setdefault(c, []).append(i)
VOCAB = {'blocks': blocks, 'byCode': byCode}

# moves
MOVES = []
for f in sorted(glob.glob('moves/moves_g*.json')):
    MOVES += json.load(open(f))
MOVES.sort(key=lambda m: ('K12345'.index(m['code'][0]), int(m['code'].split('.')[1][:-1]), m['code'][-1]))
report.append(f'MOVES: {len(MOVES)} standards')

PERF = json.load(open('perf.json'))
TEKS = {c: v for c, v in TEKS_TXT.items()}
SCAF = scaf['SCAF']
STRAND_K2 = {'K.2':'Number and operations · whole numbers to 20','K.3':'Number and operations · addition and subtraction','K.4':'Number and operations · coins','K.5':'Algebraic reasoning · counting by ones and tens',
 'K.6':'Geometry and measurement · two- and three-dimensional figures','K.7':'Geometry and measurement · measurable attributes','K.8':'Data analysis','K.9':'Personal financial literacy',
 '1.2':'Number and operations · place value to 120','1.3':'Number and operations · addition and subtraction','1.4':'Number and operations · coins','1.5':'Algebraic reasoning · patterns and equations',
 '1.6':'Geometry and measurement · two- and three-dimensional figures','1.7':'Geometry and measurement · length and time','1.8':'Data analysis','1.9':'Personal financial literacy',
 '2.2':'Number and operations · place value to 1,200','2.3':'Number and operations · fractions','2.4':'Number and operations · addition and subtraction','2.5':'Number and operations · coins',
 '2.6':'Number and operations · multiplication and division concepts','2.7':'Algebraic reasoning · patterns and equations','2.8':'Geometry and measurement · two- and three-dimensional figures',
 '2.9':'Geometry and measurement · length, area and time','2.10':'Data analysis','2.11':'Personal financial literacy'}
STRAND_NAMES = {
 '3.2': 'Number and operations · place value', '3.3': 'Number and operations · fractions', '3.4': 'Number and operations · computation',
 '3.5': 'Algebraic reasoning · patterns and relationships', '3.6': 'Geometry and measurement · two-dimensional figures and area',
 '3.7': 'Geometry and measurement · measurement', '3.8': 'Data analysis', '3.9': 'Personal financial literacy',
 '4.2': 'Number and operations · whole numbers and decimals', '4.3': 'Number and operations · fractions', '4.4': 'Number and operations · computation',
 '4.5': 'Algebraic reasoning · expressions and equations', '4.6': 'Geometry and measurement · geometric attributes', '4.7': 'Geometry and measurement · angles',
 '4.8': 'Geometry and measurement · measurement', '4.9': 'Data analysis', '4.10': 'Personal financial literacy',
 '5.2': 'Number and operations · decimals', '5.3': 'Number and operations · computation with rational numbers', '5.4': 'Algebraic reasoning · expressions, equations, area and volume',
 '5.5': 'Geometry and measurement · classifying figures', '5.6': 'Geometry and measurement · volume', '5.7': 'Geometry and measurement · measurement conversions',
 '5.8': 'Geometry and measurement · coordinate plane', '5.9': 'Data analysis', '5.10': 'Personal financial literacy'}

STRAND_NAMES.update(STRAND_K2)
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('divide jump to', 'divide up to')
with open('data_moves.js', 'w') as f:
    f.write('const MOVES = ' + J(MOVES) + ';\n')
DATA_OUT = 'data_te.js' if TE_ONLY else 'data.js'
with open(DATA_OUT, 'w') as f:
    f.write('const COURSES = ' + J(COURSES) + ';\n')
    f.write('const TIG = ' + J(TIG) + ';\n')
    f.write('const STRAND_NAMES0 = ' + J(STRAND_NAMES) + ';\n')
    f.write('const PERF = ' + J(PERF) + ';\n')
    f.write('const VOCAB = ' + J(VOCAB) + ';\n')
    f.write('const SCAF = ' + J(SCAF) + ';\n')
    f.write('const TEKS = ' + J(TEKS) + ';\n')
open('report_te.txt' if TE_ONLY else 'report.txt', 'w').write('\n'.join(report))
print('\n'.join(report[-12:]))
print(DATA_OUT, os.path.getsize(DATA_OUT), 'moves', os.path.getsize('data_moves.js'))

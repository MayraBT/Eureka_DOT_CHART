"""Parse 'Overview of Module Topics and Lesson Objectives' from a Eureka TEKS Edition module TE.
usage: overview.py TE.pdf GRADE MODULE  -> prints JSON {"M5.L1": {"topic":"A","title":..., "teks":[...]}}"""
import sys, re, json, pypdf
src, g, mod = sys.argv[1], sys.argv[2], int(sys.argv[3])
r = pypdf.PdfReader(src)
pages = []
on = False
for i, p in enumerate(r.pages[:60]):
    t = p.extract_text() or ''
    if 'Overview of Module Topics and Lesson Objectives' in t: on = True
    elif on and not re.search(r'Lessons? \d+', t): break
    if on: pages.append(t)
txt = '\n'.join(pages)
teks_re = re.compile(r'^(%s\.\d+[A-Z]?)$' % re.escape(g))
cur_teks, topic_teks, topic = [], {}, None
out = {}; last = None; star = False
for raw in txt.split('\n'):
    line = raw.strip().replace(' ', ' ')
    if not line: continue
    if teks_re.match(line):
        if topic is not None and topic in topic_teks and last is not None: cur_teks = []
        cur_teks.append(line); topic = None if topic else topic; continue
    if re.match(r'^\*(\s|$)', line): star = True; cur_teks = []; continue
    m = re.match(r'^([A-J])\s+(\S.*)$', line)
    if m and (cur_teks or star) and not line.startswith('Lesson'):
        # a topic marked * (spiral review) lists no TEKS of its own
        topic = m.group(1); topic_teks[topic] = [] if star else cur_teks[:]; cur_teks = []; star = False; last = None; continue
    m = re.match(r'^Lessons? (\d+)(?:[–-](\d+))?:\s*(.*)$', line)
    if m and topic:
        a = int(m.group(1)); b = int(m.group(2) or a)
        for n in range(a, b + 1):
            out[f'M{mod}.L{n}'] = {'topic': topic, 'title': m.group(3).strip(), 'teks': topic_teks[topic]}
        last = [f'M{mod}.L{n}' for n in range(a, b + 1)]; continue
    if last and not re.match(r'^(\d+|\d\.[A-Z]|Mid-Module|End-of-Module|Topic|Total|Module|A STORY|©|greatminds|TEKS|ELPS|Days)', line) and not out[last[0]]['title'].endswith('.'):
        for k in last: out[k]['title'] += ' ' + line
print(json.dumps(out, indent=0))

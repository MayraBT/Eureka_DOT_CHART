"""Make the teacher version of a coordinator TEKS Lookup (Carnegie or Eureka).

usage: python3 teacherize.py <coordinator index.html> <out index.html> <eureka|carnegie>

Removes everything about IPC pacing and calendars (Calendar view, dates on lessons,
"Taught in" quarter filters), Dallas ISD results, ACP items, and (Eureka) any lesson
that is only on the unreleased Q3 IPCs or calendars. Keeps lessons with their TEKS
dots, teacher-edition links, released STAAR items with Texas percents (lead4ward IQ
Tool), vertical alignment, vocabulary, Teaching moves and the Full grid.
"""
import json, re, sys

src, out, kind = sys.argv[1:4]
s = open(src).read()
log = []


def const_span(s, name):
    """Return (start, end) of the JSON value of `const NAME = <json>;`."""
    m = re.search(r'\nconst ' + re.escape(name) + r'\s*=\s*', s)
    if not m:
        return None
    i = m.end()
    dec = json.JSONDecoder()
    obj, end = dec.raw_decode(s, i)
    return i, end, obj


def set_const(name, value):
    global s
    sp = const_span(s, name)
    if not sp:
        log.append(f'const {name} not found'); return
    i, e, _ = sp
    s = s[:i] + json.dumps(value, ensure_ascii=False, separators=(',', ':')) + s[e:]


def rep(old, new, req=True, count=1):
    global s
    n = s.count(old)
    if n == 0:
        if req: log.append('MISS: ' + old[:80])
        return
    s = s.replace(old, new) if count == 0 else s.replace(old, new, count)


# ---------- data ----------
removed = {}
try:
    i, e, COURSES = const_span(s, 'COURSES')
except ValueError:
    COURSES = None
if COURSES is None:
    # Carnegie: COURSES is a JS literal spread over several statements; evaluate it in node, blank pacing, re-emit
    import subprocess, tempfile, os
    a = s.find('\nconst COURSES'); b = s.find('\nconst ACP=', a)
    with tempfile.TemporaryDirectory() as td:
        open(td + '/in.js', 'w').write(s[a:b])
        subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blank_courses.js'), td + '/in.js', td + '/out.js'], check=True)
        s = s[:a] + '\n' + open(td + '/out.js').read() + s[b:]
else:

    removed = {}
    for key, c in COURSES.items():
        pace = c.get('pace', {}).get('lessons', {})
        keep = []
        for L in c['data']['lessons']:
            if kind == 'eureka':
                ds = pace.get(L['id'], {}).get('days', [])
                only_q3 = (ds and all(d['q'] >= 3 for d in ds)) or L.get('q3') or L.get('prev')
                if only_q3:
                    removed.setdefault(key, []).append(L['id']); continue
            L.pop('q3', None); L.pop('prev', None)
            if isinstance(L.get('note'), str):
                L['note'] = re.sub(r';?\s*TEKS from the 2025-26 Q3 weekly IPC[^;]*', '', L['note']).strip('; ')
            keep.append(L)
        c['data']['lessons'] = keep
        used = {L['m'] for L in keep}
        c['data']['modules'] = [m for m in c['data']['modules'] if m['n'] in used]
        c['pace'] = {'lessons': {}, 'cal': {'quarters': {}, 'events': []}}
        c['cal'] = []
        c['unsched'] = ''
        c.pop('q3note', None)
    s = s[:i] + json.dumps(COURSES, ensure_ascii=False, separators=(',', ':')) + s[e:]
if kind == 'eureka':
    sp = const_span(s, 'TIG')
    if sp:
        TIG = sp[2]
        for key, ids in removed.items():
            for lid in ids: TIG.get(key, {}).pop(lid, None)
        set_const('TIG', TIG)
# Dallas ISD results and ACP (district-secured) items
for nm in ('DIST', 'DIST_META', 'ACP', 'ACP_SETS'):
    if const_span(s, nm): set_const(nm, {})
    else: log.append(f'const {nm} not found (ok if absent)')

# ---------- views ----------
# Calendar tab and view gone; By standard is home
rep('<button role="tab" data-view="cal"', '<button role="tab" data-view="cal" hidden style="display:none"', req=False)
s = re.sub(r'(<button[^>]*data-view="cal"[^>]*)(>)', lambda m: m.group(1) + (' hidden style="display:none"' if 'hidden' not in m.group(1) else '') + m.group(2), s, count=1)
rep('function showView(v){', "function showView(v){\n  if(v==='cal') v='std';", req=True)
# no dates on lessons
rep('function paceTag(id){', "function paceTag(id){ return ''; }\nfunction paceTag_coord(id){")
# "Taught in" quarter filters hidden
for qid in ('fQ', 'pQ'):
    rep(f'<span class="qtog" id="{qid}"', f'<span class="qtog" id="{qid}" style="display:none"', req=False)
# Dallas ISD filter
rep('<label id="pBelowWrap">', '<label id="pBelowWrap" style="display:none">', req=False)
s = s.replace("$('pBelowWrap').style.display=hs?'none':'';", "$('pBelowWrap').style.display='none';")
# storage keys separate from the coordinator version on the same github.io origin
s = s.replace("'teks678-", "'teksT-").replace("'eureka35-", "'eurekaT-")
# open on By standard
if "loadCourse(ck,false);\nshowView('std');" not in s:
    rep("loadCourse(ck,false);\n", "loadCourse(ck,false);\nshowView('std');\n", req=False)


# ---------- remaining Dallas ISD / ACP wording ----------
s = re.sub(r":`<span class=\"na\">\$\{b\.g==='7'\?'No Dallas ISD students take Grade 7 STAAR':'no Dallas ISD data'\}</span>`", ":''", s)
s = s.replace(" Dallas ISD data covers 2026 (Grade 6, Grade 8, Algebra I) and 2025 (Algebra I), so when a band mixes years its Dallas ISD average uses fewer items; the Dallas ISD comparison above uses only the items both have.", "")
rep("let h=`<div class=\"perf\"><h4>ACP Example items · 2025-26</h4>", "return ''; let h=`<div class=\"perf\"><h4>ACP Example items · 2025-26</h4>", req=False)
rep("$('fTestLab').textContent=hs?", "{ const pb=document.querySelector('.tabs button[data-view=\"perf\"]'); if(pb) pb.style.display=hs?'none':''; if(hs&&$('view-perf').classList.contains('on')) showView('std'); $('fTest').closest('label').style.display=hs?'none':''; } $('fTestLab').textContent=hs?", req=False)
s = s.replace(" · ACP Example items'", "'").replace("'Has an ACP Example item'", "''")
# switching course from the menu opens By standard
s = s.replace("loadCourse(c); showView(v); } });", "loadCourse(c); showView('std'); } });")
s = s.replace("loadCourse(c,false); showView('std');", "loadCourse(c,false); showView('std');")


# ---------- Eureka: standards later in the year are not "untaught" ----------
rep("if(!BY_STD.get(s.code).length) b.classList.add('none');",
    "if(!BY_STD.get(s.code).length && !DATA.modules.some(m=>(m.focus||[]).concat(m.included||[]).includes(s.code))) b.classList.add('none');", req=False)
rep('<span class="n">${lessons.length} lessons</span>', '<span class="n">${lessons.length?lessons.length+\' lessons\':\'later in the year\'}</span>', req=False)
# ---------- footers: drop pacing / Dallas ISD / ACP source sentences ----------
s = re.sub(r" ?Q3: Grade \$\{g\} 2026-27 weekly IPCs where posted;[^.]*?\(marked on the lesson\)\.", "", s)
s = re.sub(r" ?Q3 from the 2026-27 Q3 calendar when posted\.", "", s)
s = s.replace("; Q3 weeks without a posted weekly IPC are paced from the 2026-27 Q3 calendar.", ".")
s = s.replace(", Q1–Q2 (● = the TEKS line for the day", " (● = the TEKS line for the day").replace(", Q1–Q3 where posted (● = the TEKS line for the day", " (● = the TEKS line for the day").replace("; Q3 from the 2026-27 Q3 calendar when posted.", ".")
s = re.sub(r" ?Dallas ISD results: SchoolCity Item Analysis[^)]*\)\.", "", s)
s = re.sub(r" ?Pacing: Dallas ISD 2026-27 Instructional Planning Calendars[^.]*\.", "", s)
s = re.sub(r" ?Example items: Dallas ISD Assessment Department.*?do not appear on the ACP\.", "", s)
s = re.sub(r" ?Geometry and Geometry Advanced share one Example set\.", "", s)
s = re.sub(r" ?Dallas ISD results[^.]*?\(SchoolCity[^)]*\)\.", "", s)
s = s.replace('"Today" follows the device clock.', '')

# ---------- wording ----------
for a, b in [
    ("'<div class=\"perf\"><h4>Where and when it is taught</h4>'", "'<div class=\"perf\"><h4>Where it is taught</h4>'"),
    ('<h4>Where and when it is taught</h4>', '<h4>Where it is taught</h4>'),
    ("Lesson TEKS come from the 2026-27 weekly IPCs. Where a Q3 weekly IPC is not posted yet, the lesson is paced from the 2026-27 Q3 calendar and its TEKS come from last year's (2025-26) Q3 weekly IPC for the same Eureka lesson.",
     "● marks a lesson's TEKS on the weekly IPC; ○ marks a bundled standard."),
    ('Dallas ISD results in purple', ''), (', with Dallas ISD 2026 results in purple', ''),
    (" Dallas ISD data covers the 2026 tests, so a band's Dallas ISD average uses only its 2026 items.", ''),
]:
    s = s.replace(a, b)
# Dallas ISD legend chip in vertical performance
s = s.replace('<span><i class="kds"></i>Dallas ISD average</span>', '')
# How to use: drop calendar/pacing steps and the walk/appraiser guides
helpfix = r"""
(function(){ try{
  const bad=/Calendar|Go to this week|this week|pacing|Taught in|on the IPC day|appraiser|Dallas ISD|ACP/i;
  for(let k=HELP.length-1;k>=0;k--){ const h=HELP[k];
    if(/walk|apprais|vertical/i.test(h.id||'')){ HELP.splice(k,1); continue; }
    h.steps=(h.steps||[]).filter(x=>!bad.test(x));
    if(h.look) h.look=h.look.filter(x=>!bad.test(x));
    h.try=(h.try||[]).filter(t=>t[0]!=='cal');
    if(h.why) h.why=h.why.replace(/ It opens on the Calendar\.?/,'').replace(/opens on the Calendar/,'opens on By standard');
  }
}catch(e){} })();
"""
rep('\nfunction helpTry', helpfix + '\nfunction helpTry')
# footer: say what this version leaves out
foot_note = " This teacher version leaves out IPC pacing and calendars and Dallas ISD results."
s = re.sub(r'(const FOOT\w*\s*=\s*[^\n]*?)(`;)', lambda m: m.group(1) + foot_note + m.group(2) if 'This teacher version' not in m.group(1) else m.group(0), s, count=1)
# title
s = s.replace('· TEKS Lookup</title>', '· TEKS Lookup for Teachers</title>')
s = re.sub(r'<title>([^<]*)</title>', lambda m: '<title>' + m.group(1).replace('TEKS Lookup for Teachers', 'Teacher TEKS Lookup') + '</title>', s, count=1)
css = """<style>
  .when,.when.none,.calbtn,#calWrap{display:none!important}
  .key .when{display:none!important}
</style>
</head>"""
s = s.replace('</head>', css, 1)
# legend: drop the "when the lesson is on the IPC" sample
s = re.sub(r'<span class="sep" aria-hidden="true"></span><span><i class="when">[^<]*</i>[^<]*</span>', '', s)

open(out, 'w').write(s)
print('removed Q3-only lessons:', {k: len(v) for k, v in removed.items()})
print('\n'.join(log) or 'all patches applied')

"""Coordinator tool: combine the lesson-by-lesson dot chart (dot_marks/) with the IPC on the Full grid.

usage: python3 combine.py out/index.html   (edits in place; run after assemble.py)

Grades with a dot chart: the dot shows what the lesson does (● Exit Ticket assesses the TEKS,
○ used in the lesson), the cell shading shows what the weekly IPC assigns (gold = IPC lesson TEKS,
light gold = IPC bundled). A filter shows only lessons where the two differ. Grades without a
dot chart keep the IPC dots as before. The By lesson view adds the dot chart and its Why line.
"""
import sys, json, glob, re, os
f = sys.argv[1]; s = open(f).read()
here = os.path.dirname(os.path.abspath(__file__))
DOTS = {}
for p in sorted(glob.glob(os.path.join(here, 'dot_marks', '*_M*.json'))):
    g = os.path.basename(p).split('_')[0]
    for lid, v in json.load(open(p)).items():
        if lid.startswith('_'): continue
        DOTS.setdefault('g' + g.lower(), {})[lid] = [v['F'], v['O'], v['why']]
fails = []
def rep(old, new):
    global s
    if old not in s: fails.append(old[:80]); return
    s = s.replace(old, new, 1)

# data + helpers
rep('\nlet COURSE, DATA, PACE', '\nconst DOTS=' + json.dumps(DOTS, ensure_ascii=False) + ''';
const dotsOf=L=>(DOTS[COURSE.key]||{})[L.id]||null;
const hasDots=()=>!!DOTS[COURSE.key];
const dotLine=L=>{ const d=dotsOf(L); if(!d) return ''; const b=[...d[0].map(c=>'● '+c),...d[1].map(c=>'○ '+c)].join('  ');
  return `<span class="dotline"><b>The lesson (dot chart):</b> ${b||'no TEKS'} · <span class="src">${esc(d[2])}</span></span>`; };
let COURSE, DATA, PACE''')
# By lesson: show the dot chart line under the IPC TEKS
rep("<span class=\"whenrow\">${paceTag(L.id)}</span>${(t=>t.length?`<div class=\"lvocab\">",
    "<span class=\"whenrow\">${paceTag(L.id)}</span>${dotLine(L)}${(t=>t.length?`<div class=\"lvocab\">")
# grid control
rep('<label><input type="checkbox" id="gHideEmpty" checked> Hide standards with no dots</label>',
    '<label><input type="checkbox" id="gHideEmpty" checked> Hide standards with no dots</label>'
    '<label id="gMisWrap"><input type="checkbox" id="gMis"> Only lessons where the IPC and the lesson differ</label>')
rep("$('gHideEmpty').addEventListener('change',buildGrid);",
    "$('gHideEmpty').addEventListener('change',buildGrid); $('gMis').addEventListener('change',buildGrid);")
# grid
old_start = s.find('function buildGrid(){')
old_end = s.find('function highlightGrid(')
if old_start < 0 or old_end < 0: fails.append('buildGrid')
else:
    s = s[:old_start] + r'''function buildGrid(){
  const D=hasDots(); $('gMisWrap').style.display=D?'':'none'; if(!D) $('gMis').checked=false;
  const cellsOf=L=>{ const ipc=new Map(L.marks), d=dotsOf(L), dt=new Map(); if(d){ d[0].forEach(c=>dt.set(c,'F')); d[1].forEach(c=>dt.set(c,'O')); } return [ipc,dt,!!d]; };
  const mis=(i,t)=>(i==='F'&&t!=='F')||(t==='F'&&!i);
  let lessons=DATA.lessons.filter(L=>gridMods.has(L.m)&&(L.marks.length||dotsOf(L))&&(!lens||L.marks.concat(D&&dotsOf(L)?dotsOf(L)[0].concat(dotsOf(L)[1]).map(c=>[c]):[]).some(m=>lens.fam.has(m[0]))));
  if(D&&$('gMis').checked) lessons=lessons.filter(L=>{ const [ipc,dt,has]=cellsOf(L); if(!has) return false; const all=new Set([...ipc.keys(),...dt.keys()]); return [...all].some(c=>mis(ipc.get(c),dt.get(c))); });
  const used=new Set(); lessons.forEach(L=>{ const [ipc,dt]=cellsOf(L); ipc.forEach((v,c)=>used.add(c)); dt.forEach((v,c)=>used.add(c)); });
  const cols=DATA.standards.filter(s=>(!$('gHideEmpty').checked || used.has(s.code))&&(!lens||lens.fam.has(s.code)));
  let html='<thead><tr><th class="lab">Lesson</th>'+cols.map(s=>`<th class="${s.type}" data-col="${s.code}" title="${esc(s.desc)}"><span>${s.code}</span></th>`).join('')+'</tr></thead><tbody>';
  let curM=0;
  const IPCN={F:'IPC lesson TEKS',O:'IPC bundled TEKS'}, DTN={F:'Exit Ticket assesses it',O:'used in the lesson, not assessed'};
  for(const L of lessons){
    if(L.m!==curM){ curM=L.m; html+=`<tr class="modhead"><th colspan="${cols.length+1}"><span class="mh">Module ${L.m}: ${esc(MOD.get(L.m).name)}</span></th></tr>`; }
    const [ipc,dt,has]=cellsOf(L);
    html+=`<tr><th class="lab" title="${esc(L.title)}"><small>${TL(L)}·${L.l}</small><b>${esc(L.title)}</b></th>`;
    html+=cols.map(s=>{ const i=ipc.get(s.code), t=dt.get(s.code);
      if(!(D&&has)) return `<td class="${s.type}" data-col="${s.code}">${i?`<button data-code="${s.code}" title="${s.code} · ${esc(L.title)}"><i class="dot ${i}"></i></button>`:''}</td>`;
      const cls=s.type+(i?' ipc'+i:'')+(mis(i,t)?' mis':'');
      const tip=`${s.code} · ${esc(L.title)} · Lesson: ${t?DTN[t]:'not addressed'} · IPC: ${i?IPCN[i]:'not listed'}`;
      return `<td class="${cls}" data-col="${s.code}">${(i||t)?`<button data-code="${s.code}" title="${tip}">${t?`<i class="dot ${t}"></i>`:''}</button>`:''}</td>`; }).join('')+'</tr>';
  }
  if(!lessons.length) html+=`<tr><td class="lab" colspan="${cols.length+1}">No lessons match.</td></tr>`;
  $('grid').innerHTML=html+'</tbody>';
  $('grid').querySelectorAll('button[data-code]').forEach(b=>b.addEventListener('click',()=>selectStd(b.dataset.code)));
  highlightGrid();
}
''' + s[old_end:]
# key: IPC dots as before; grades with a dot chart add how the Full grid reads
rep('<span><i class="dot"></i>bundled standard on the weekly IPC</span>',
    '<span><i class="dot"></i>bundled standard on the weekly IPC</span>'
    "${DOTS[COURSE.key]?'<span class=\"sep\" aria-hidden=\"true\"></span><span class=\"grkey\"><b>Full grid:</b> dots show the lesson (● Exit Ticket assesses it, ○ used in the lesson); shading shows the IPC (<i class=\"shade F\"></i>lesson TEKS <i class=\"shade\"></i>bundled); dashed outline = they differ</span>':''}")
css = '''
  /* dot chart + IPC on the Full grid */
  table.grid td.ipcF{box-shadow:inset 0 0 0 40px rgba(242,183,5,.55)}
  table.grid td.ipcO{box-shadow:inset 0 0 0 40px rgba(242,183,5,.22)}
  table.grid td.mis button{outline:2px dashed #b3261e;outline-offset:-4px}
  .shade{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-2px;margin-right:6px;background:rgba(242,183,5,.22);border:1px solid rgba(0,0,0,.12)}
  .shade.F{background:rgba(242,183,5,.55)}
  #legend .grkey{display:block;flex:1 1 100%;line-height:1.5}
  #legend .grkey b{display:inline}
  #legend .grkey i.shade{display:inline-block;margin:0 4px 0 2px}
  .dotline{display:block;margin-top:4px;font-size:13px;color:var(--ink-2)}
</style>'''
s = s.replace('</style>', css, 1)
open(f, 'w').write(s)
print('combine:', 'missing ' + str(fails) if fails else 'ok', '| grades with dots:', sorted(DOTS))

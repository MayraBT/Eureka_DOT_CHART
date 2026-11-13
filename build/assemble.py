"""Build out/index.html from the Carnegie TEKS Lookup template + Eureka data."""
import re, json
T = open('/home/claude/mayrabt/carnegie_dot_chart/index.html').read()
fails = []
def rep(s, old, new, count=1, req=True):
    n = s.count(old)
    if n == 0:
        if req: fails.append(old[:90])
        return s
    return s.replace(old, new) if count == 0 else s.replace(old, new, count)

# ---------- split template ----------
css_end = T.find('</style>')
head = T[:css_end]
body_start = T.find('<body>')
s1 = T.find('<script>', body_start)
html_body = T[body_start:s1]
mv_code_start = T.find('\nconst MOVES_IDX')
mv_code_end = T.find('</script>', mv_code_start)
moves_code = T[mv_code_start:mv_code_end]
s2 = T.find('<script>', mv_code_end)
tail_start = T.find('\nlet COURSE, DATA, PACE')
tail = T[tail_start:]
# helper code that lived between data constants
tig_fn = "const tigLink=id=>{ const f=(TIG[COURSE.key]||{})[id]; if(!f) return ''; const fs=Array.isArray(f)?f:[f]; return fs.map((x,n)=>` <a class=\"tig\" href=\"${x}\" target=\"_blank\" rel=\"noopener\" title=\"Eureka teacher edition for this lesson, as linked on the weekly IPC${fs.length>1?' (link '+(n+1)+')':''} · district Google sign-in\">Teacher${fs.length>1?' '+(n+1):''} ↗</a>`).join(''); };\n"
glue = ("const ACP={}, ACP_SETS={}, DIST={}, DIST_META={};\n"
        "const distOf=(code,d)=>null;\n" + tig_fn +
        "for(const b of SCAF) b.src=String(b.src);\n")

# ---------- head / CSS ----------
head = rep(head, '<title>Grades 6–8 & Algebra I · TEKS Lookup</title>', '<title>Eureka TEKS Lookup</title>')
head += """  .k-lesson .act{font-style:italic}
  .modss{margin:4px 0 10px;padding:8px 12px;background:var(--paper-2);border-radius:8px;font-size:13.5px;color:var(--ink-2)}
  .modss .mk{cursor:pointer}
  .mk.q3{background:#fff8e6;color:#5a4300;border-color:#f0dca6}
  .vrow.sp span:first-child{color:#7a5af5}
  .vt.sp{border-style:dashed}
  .lo{display:block;font-size:13px;color:var(--ink-2);margin-top:2px}
"""

# ---------- body ----------
b = html_body
b = rep(b, '<h1 id="ttl">Grade 8 · TEKS Lookup<small id="subttl">Texas Math Solution (Carnegie Learning) · standards ↔ lessons</small></h1>',
        '<h1 id="ttl">Grade 3 Eureka · TEKS Lookup<small id="subttl">Eureka Math TEKS Edition · standards ↔ lessons</small></h1>')
b = re.sub(r'<select id="courseSel" aria-label="Course">.*?</select>',
           '<select id="courseSel" aria-label="Grade"><option value="g3">Grade 3</option><option value="g4">Grade 4</option><option value="g5">Grade 5</option></select>', b, flags=re.S)
b = rep(b, '<span class="vh">Course</span>', '<span class="vh">Grade</span>')
b = rep(b, 'placeholder="Type a TEKS (6.4B, 8.5I, A.5A) or a lesson word (ratio, slope, quadratic)"', 'placeholder="Type a TEKS (3.4K, 4.3D, 5.3K) or a lesson word (fraction, area, decimal)"')
b = rep(b, 'title="Full grid — The dot chart"', 'title="Full grid — The dot chart built from the IPCs"')
b = rep(b, '<span class="th">The dot chart</span>', '<span class="th">The dot chart (from the IPCs)</span>')
b = rep(b, '<label><input type="checkbox" id="fCov"> Only standards taught in this course</label>', '<label><input type="checkbox" id="fCov"> Only standards on a lesson</label>')
b = rep(b, '<label id="f7wrap"><input type="checkbox" id="f7"> Grade 7 TEKS</label>', '<label id="f7wrap" style="display:none"><input type="checkbox" id="f7"> other grade</label>')
b = rep(b, 'Statewide percent correct on each released STAAR item, by TEKS, with Dallas ISD results in purple (2026; Algebra I 2025 and 2026). Click a column header to sort; click a code to open it.',
        'Statewide percent correct on each released STAAR item (2025 and 2026), by TEKS. Click a column header to sort; click a code to open it.')
b = rep(b, '<label id="pBelowWrap">', '<label id="pBelowWrap" style="display:none">')
b = re.sub(r'<span class="qtog" id="mvG" aria-label="Grades shown">Show: .*?</span>',
           '<span class="qtog" id="mvG" aria-label="Grades shown">Show: <button data-g="3" aria-pressed="false">Grade 3</button><button data-g="4" aria-pressed="false">Grade 4</button><button data-g="5" aria-pressed="false">Grade 5</button></span>', b, flags=re.S)
# Q4 has no IPC yet: keep the buttons but label them
b = b.replace('<button data-q="4" aria-pressed="false">Q4</button>', '<button data-q="4" aria-pressed="false" title="Q4: district-created materials after Eureka ends; no IPC lessons">Q4</button>')

# ---------- moves code ----------
mc = moves_code
mc = rep(mc, "const MV_GNAME = {'6':'Grade 6','7':'Grade 7','8':'Grade 8','A':'Algebra I','G':'Geometry','2A':'Algebra II'};", "const MV_GNAME = {'3':'Grade 3','4':'Grade 4','5':'Grade 5'};")
mc = rep(mc, "  if(COURSE.key==='a7') mvG.delete('6');\n", "")
mc = rep(mc, "const isCode=/^([678ag]|2a)\\.\\d/i.test(mvQuery.trim());", "const isCode=/^[345]\\.\\d/.test(mvQuery.trim());")
mc = rep(mc, "Try a TEKS code (6.4B, A.5A) or a word like slope, percent, or integers.", "Try a TEKS code (3.4K, 5.3K) or a word like fraction, area, or decimal.")
mc = rep(mc, "search above by TEKS code or a word (slope, percent, integers)", "search above by TEKS code or a word (fraction, area, decimal)")
mc = rep(mc, "Open in By standard (lessons, ${/^(G|2A)\\./.test(code)?'Example items':'STAAR items'}) →", "Open in By standard (lessons, STAAR items) →")

# ---------- tail code ----------
t = tail
t = rep(t, "try{ localStorage.removeItem('teks678-secs'); }catch(e){}", "")
t = t.replace("'teks678-", "'eureka35-")
# lesson labels: topic letters
t = rep(t, "const lessonWhere = L => `Module ${L.m} · Topic ${L.t} · Lesson ${L.l}`;",
        "const TL = L => (MOD.get(L.m).letters||[])[L.t-1]||'';\nconst lessonWhere = L => `Module ${L.m} · Topic ${TL(L)} · Lesson ${L.l}`;\nconst lesShort = L => `M${L.m}·${TL(L)}·L${L.l}`;")
t = t.replace("M${L.m}·T${L.t}·L${L.l}", "${lesShort(L)}")
t = t.replace("M${X.m}·T${X.t}·L${X.l}", "${lesShort(X)}")
t = rep(t, "const subOf = L => (L.sub ? `<span class=\"sub\">— ${esc(L.sub)}</span>` : (L.g7?'<span class=\"src\">Grade 7 lesson · TEKS as listed on the IPC</span>':''))+(L.note?` <span class=\"src\">· ${esc(L.note)}</span>`:'');",
        "const subOf = L => (L.note?` <span class=\"src\">${esc(L.note)}</span>`:'');")
t = rep(t, "const MARK_NAMES={g6:{F:'Lesson focus standard',O:'Also addressed in the lesson',I:''},dflt:{F:'Fully covered (dot chart)',O:'Partially covered (dot chart)',I:'TEKS listed on the IPC (Grade 7 lesson)'}};",
        "const MARK_NAMES={dflt:{F:'Lesson TEKS on the weekly IPC',O:'Bundled standard on the weekly IPC',I:''}};")
# strands
t = re.sub(r"const names = window\.STRAND_NAMES = \{.*?\n  \};", "const names = window.STRAND_NAMES = STRAND_NAMES0;", t, flags=re.S)
t = rep(t, "return (COURSE.key==='g6'?ga-gb:gb-ga)||sa-sb;", "return ga-gb||sa-sb;")
# renderDetail wording
t = rep(t, "const g6=COURSE.key==='g6'; const parts=[]; if(n('F')) parts.push(`${n('F')} ${g6?'as focus standard':'fully covered'}`); if(n('O')) parts.push(`${n('O')} ${g6?'also addressed':'partially covered'}`);",
        "const parts=[]; if(n('F')) parts.push(`${n('F')} as lesson TEKS`); if(n('O')) parts.push(`${n('O')} as bundled standard`);")
t = rep(t, "html+=`<p class=\"empty\">No lesson in ${COURSE.name} carries ${s.code}${COURSE.key==='a7'&&s.code.startsWith('7.')?' — neither the Grade 8 dot chart nor the 7th Advanced IPC lists it for a lesson.':s.g7?' — the chart notes it is covered in the Accelerated Grade 7 course.':' on the dot chart.'}</p>`;",
        "html+=`<p class=\"empty\">No lesson in ${COURSE.name} lists ${s.code} on the weekly IPC.${ssModsFor(s.code)}</p>`;")
t = rep(t, "html+='<div class=\"perf\"><h4>Where and when it is taught</h4>';",
        "html+='<div class=\"perf\"><h4>Where and when it is taught</h4>'+(hits.length?`<p class=\"note\">Lesson TEKS come from the 2026-27 weekly IPCs. Where a Q3 weekly IPC is not posted yet, the lesson is paced from the 2026-27 Q3 calendar and its TEKS come from last year's (2025-26) Q3 weekly IPC for the same Eureka lesson.${ssModsFor(s.code)}</p>`:'');")
t = rep(t, "html+=`<button class=\"lesson\" data-id=\"${L.id}\"><i class=\"dot ${k}\" title=\"${MARK_NAME[k]}\"></i><span><span class=\"where\">${lessonWhere(L)} · ${esc(MOD.get(L.m).topics[L.t-1])}</span><br><b>${esc(L.title)}</b> ${subOf(L)}<span class=\"whenrow\">${paceTag(L.id)}</span></span></button>`;",
        "html+=`<button class=\"lesson\" data-id=\"${L.id}\"><i class=\"dot ${k}\" title=\"${MARK_NAME[k]}\"></i><span><span class=\"where\">${lessonWhere(L)} · ${esc(MOD.get(L.m).topics[L.t-1]||'')}</span><br><b>${esc(L.title)}</b> ${subOf(L)}<span class=\"whenrow\">${paceTag(L.id)}</span></span></button>`;")
t = t.replace("MOD.get(L.m).topics[L.t-1]", "(MOD.get(L.m).topics[L.t-1]||'')")
t = rep(t, "const COURSE_ORDER=['g6','a7','g8','a1ms','a1hs','a1hsadv','geo','geoadv','a2','a2adv'];", "const COURSE_ORDER=['g3','g4','g5'];")
# Spanish vocabulary
t = rep(t, "function vt(t,cls){ const st=t.includes('*'); return `<span class=\"vt ${cls||''}\" title=\"${st?'used on STAAR':''}\">${esc(t.replace(/\\*/g,''))}${st?'<sup>★</sup>':''}</span>`; }",
        "function vt(t,cls){ const st=t.includes('*'); return `<span class=\"vt ${cls||''}\" title=\"${st?(/sp/.test(cls||'')?'se usa en STAAR':'used on STAAR'):''}\">${esc(t.replace(/\\*/g,''))}${st?'<sup>★</sup>':''}</span>`; }")
t = rep(t, "function vocabText(code){ return vocabFor(code).map(b=>b.new.concat(b.prev).join(' ')).join(' ').replace(/\\*/g,''); }",
        "function vocabText(code){ return vocabFor(code).map(b=>b.new.concat(b.prev,b.sp?b.sp.new.concat(b.sp.prev):[]).join(' ')).join(' ').replace(/\\*/g,''); }")
t = rep(t, "let h='<div class=\"perf vocab\"><h4>Academic vocabulary</h4><p class=\"note\">lead4ward Academic Vocabulary, Math '+gName(gradeOf(code))+' — words essential for concept development (not a complete list).'+(/^(G|2A)\\./.test(code)?'':' ★ = used on STAAR.')+'</p>';",
        "let h='<div class=\"perf vocab\"><h4>Academic vocabulary · English and Spanish</h4><p class=\"note\">lead4ward Academic Vocabulary, Math '+gName(gradeOf(code))+' (English and Spanish editions) — words essential for concept development (not a complete list). ★ = used on STAAR.</p>';")
t = rep(t, "    h+=`<div class=\"vrow\"><span>Previously introduced</span><span>${b.prev.length?b.prev.map(t=>vt(t)).join(''):'<span class=\"qs\">none listed</span>'}</span></div>`;\n",
        "    h+=`<div class=\"vrow\"><span>Previously introduced</span><span>${b.prev.length?b.prev.map(t=>vt(t)).join(''):'<span class=\"qs\">none listed</span>'}</span></div>`;\n"
        "    if(b.sp){ h+=`<div class=\"vrow sp\"><span lang=\"es\">Nuevo en este grado</span><span lang=\"es\">${b.sp.new.length?b.sp.new.map(t=>vt(t,'new sp')).join(''):'<span class=\"qs\">—</span>'}</span></div>`;\n"
        "      h+=`<div class=\"vrow sp\"><span lang=\"es\">Introducido antes</span><span lang=\"es\">${b.sp.prev.length?b.sp.prev.map(t=>vt(t,'sp')).join(''):'<span class=\"qs\">—</span>'}</span></div>`; }\n")
# across courses wording
t = rep(t, "<h4>Across courses</h4><p class=\"note\">Standards in the same lead4ward scaffold clusters as ${code}, and where each course teaches them.</p>",
        "<h4>Across grades</h4><p class=\"note\">Standards in the same lead4ward scaffold clusters as ${code}, and where each grade teaches them in Eureka (Q1–Q3).</p>")
t = t.replace("'Following '+code+' across courses ✓':'Follow '+code+' across courses'", "'Following '+code+' across grades ✓':'Follow '+code+' across grades'")
t = rep(t, "<th>Course</th><th>Related standards in that course</th>", "<th>Grade</th><th>Related standards in that grade</th>")
t = rep(t, "'<span class=\"qs\">this course</span>'", "'<span class=\"qs\">this grade</span>'")
t = rep(t, "function gName(g){ return g==='A'?'Algebra I':g==='2A'?'Algebra II':g==='G'?'Geometry':'Grade '+g; }",
        "function gName(g){ return g==='K'?'Kindergarten':g==='A'?'Algebra I':g==='2A'?'Algebra II':g==='G'?'Geometry':'Grade '+g; }")
# vertical alignment range: K through two grades up
t = rep(t, "const gr0=gRank(g), lo=g==='6'?5:hs?6:gr0-2, hi=g==='6'?7:hs?11:8;", "const gr0=gRank(g), lo=0, hi=Math.min(gr0+2,8);")
t = rep(t, "— Grade ${lo} through ${hi===11?'Algebra II':'Grade '+hi} expectations in the same cluster.", "— Kindergarten through Grade ${hi} expectations in the same cluster.")
t = rep(t, "const rn=r=>r===11?'Algebra II':r===10?'Geometry':r===9?'Algebra I':'Grade '+r;", "const rn=r=>r===0?'Kindergarten':'Grade '+r;")
t = rep(t, "s.type==='NT'?'Not tested':''", "s.type==='NT'||s.type==='U'?'Not tested':''")
# vertical performance
t = rep(t, "const VP_TX='#008c84', VP_DS='#7a5af5', VP_BANDS=['6','7','8','A'];", "const VP_TX='#008c84', VP_DS='#7a5af5', VP_BANDS=['3','4','5'];")
t = re.sub(r"const other=D\.other\.filter\(g=>g!=='3'&&g!=='4'&&g!=='5'\);\n  h\+=`<p class=\"note vpcav\">.*?</p>`;",
           "h+=`<p class=\"note vpcav\">Each grade band is a different test, set of items, and group of students, so read this as <b>where the concept is hardest</b> along the progression, not as one cohort's growth. Averages are percent correct (full credit on 2-point items) across every related released item${yr==='both'?' from 2025 and 2026':' from '+yr}. Standards below Grade 3 in the same clusters have no STAAR items.</p>`;", t, flags=re.S)
# by lesson: module S&S line, Q3 note, lesson LO
t = rep(t, "    let html=`<summary><span>Module ${m.n}: ${esc(m.name)}</span><span class=\"n\">${lessons.length} lessons</span></summary>`;\n    m.topics.forEach((t,ti)=>{\n      html+=`<div class=\"topic\" data-m=\"${m.n}\" data-t=\"${ti+1}\"><h5>Topic ${ti+1}: ${esc(t)}</h5>`;",
        "    let html=`<summary><span>Module ${m.n}: ${esc(m.name)}</span><span class=\"n\">${lessons.length} lessons</span></summary>`+ssLine(m);\n    m.topics.forEach((t,ti)=>{\n      if(!lessons.some(L=>L.t===ti+1)) return;\n      html+=`<div class=\"topic\" data-m=\"${m.n}\" data-t=\"${ti+1}\"><h5>Topic ${(m.letters||[])[ti]||ti+1}: ${esc(t)}</h5>`;")
t = rep(t, "const marks=L.marks.length? L.marks.map(mkBtn).join('') : '<span class=\"mk none\">no TEKS listed</span>';",
        "const marks=L.marks.length? L.marks.map(mkBtn).join('') : noMarks(L);")
t = rep(t, "html+=`<div class=\"lrow\" id=\"les-${L.id}\" data-id=\"${L.id}\"><div class=\"t\"><b>${L.l}. ${esc(L.title)}</b>${tigLink(L.id)}<br><span>${esc(L.sub)}</span>",
        "html+=`<div class=\"lrow\" id=\"les-${L.id}\" data-id=\"${L.id}\"><div class=\"t\"><b>${L.l}. ${esc(L.title)}</b>${tigLink(L.id)}${L.note?`<span class=\"lo\">${esc(L.note)}</span>`:''}")
t = rep(t, "  host.querySelectorAll('.mk[data-code]').forEach(b=>b.addEventListener('click',()=>selectStd(b.dataset.code)));\n}\nfunction applyLessonFilter(){",
        "  host.querySelectorAll('.mk[data-code]').forEach(b=>b.addEventListener('click',()=>selectStd(b.dataset.code)));\n}\n"
        "function noMarks(L){ return L.q3?'<span class=\"mk q3\" title=\"Paced from the Q3 calendar; lesson TEKS come with the Q3 weekly IPC\">Q3 · TEKS on the weekly IPC when posted</span>':'<span class=\"mk none\">no TEKS listed</span>'; }\n"
        "function ssLine(m){ const c=x=>STD.has(x)?`<button class=\"mk ${STD.get(x).type}\" data-code=\"${x}\">${x}</button>`:`<span class=\"mk\">${x}</span>`; return `<div class=\"modss\">Scope &amp; Sequence TEKS · focus: ${(m.focus||[]).map(c).join(' ')||'—'}${(m.included||[]).length?` · included: ${m.included.map(c).join(' ')}`:''}${(m.omit||[]).length?` · omitted lessons: ${m.omit.join(', ')}`:''}${(m.after_staar||[]).length?` · taught after STAAR: ${m.after_staar.join(', ')}`:''}</div>`; }\n"
        "function ssModsFor(code){ const ms=DATA.modules.filter(m=>(m.focus||[]).includes(code)||(m.included||[]).includes(code)); return ms.length?` The Scope &amp; Sequence lists it for ${ms.map(m=>'Module '+m.n+((m.focus||[]).includes(code)?' (focus)':' (included)')).join(', ')}.`:''; }\n"
        "function applyLessonFilter(){")
t = rep(t, "html+=`<tr><th class=\"lab\" title=\"${esc(L.title)} — ${esc(L.sub)}\"><small>${L.t}.${L.l}</small><b>${esc(L.title)}</b></th>`;",
        "html+=`<tr><th class=\"lab\" title=\"${esc(L.title)}\"><small>${TL(L)}·${L.l}</small><b>${esc(L.title)}</b></th>`;")
t = rep(t, "const lessons=DATA.lessons.filter(L=>gridMods.has(L.m)&&(!lens||L.marks.some(m=>lens.fam.has(m[0]))));",
        "const lessons=DATA.lessons.filter(L=>gridMods.has(L.m)&&L.marks.length&&(!lens||L.marks.some(m=>lens.fam.has(m[0]))));")
# calendar: quarters without a header entry, Q4 note
t = rep(t, "const qd=PACE.cal.quarters[w.q]; html+=`<tr class=\"qhead\"><td colspan=\"6\">Quarter ${w.q} · ${fdr(qd.start,qd.end)}</td></tr>`;",
        "const qd=PACE.cal.quarters[w.q]; html+=`<tr class=\"qhead\"><td colspan=\"6\">Quarter ${w.q} · ${fdr(qd.start,qd.end)}${w.q===3?(COURSE.q3note||''):''}</td></tr>`;")
t = rep(t, "  $('cal').innerHTML=html+'</tbody>';",
        "  if(!calQ||calQ===4) html+=`<tr class=\"qhead\"><td colspan=\"6\">Quarter 4 · ${esc((COURSE.notes||[])[0]||'Eureka instruction ends in March; Q4 uses district-created materials.')}</td></tr>`;\n  $('cal').innerHTML=html+'</tbody>';")
t = rep(t, "else alert('Today is outside the 2026-27 IPC.');", "else showView('cal');")
# samples, help, foot
t = rep(t, "const SAMPLE={g6:'6.4B',a7:'8.5I',g8:'8.5I',a1ms:'A.5A',a1hs:'A.5A',a1hsadv:'A.5A',geo:'G.6D',geoadv:'G.6D',a2:'2A.4F',a2adv:'2A.4F'};",
        "const SAMPLE={g3:'3.4K',g4:'4.4H',g5:'5.3K'};")
i=t.find('const HELP=['); j=t.find('\nfunction helpTry'); assert i>0 and j>i
t = t[:i]+open('help.js').read()+t[j:]
t = re.sub(r"const FOOT=\{.*?\n\};\nfunction legendHTML\(\)\{.*?\n\}\nconst SUB=.*?\nconst TESTS=.*?\n",
           open('foot.js').read(), t, flags=re.S)
t = rep(t, "{ const hs=k==='geo'||k==='geoadv'||k==='a2'||k==='a2adv';", "{ const hs=false;")
t = rep(t, "'Statewide percent correct on each released STAAR item, by TEKS, with Dallas ISD results in purple (2026; Algebra I 2025 and 2026). Click a column header to sort; click a code to open it.'",
        "'Statewide percent correct on each released STAAR item (2025 and 2026), by TEKS. Click a column header to sort; click a code to open it.'")
t = rep(t, "$('pBelowWrap').style.display=hs?'none':'';", "$('pBelowWrap').style.display='none';")
t = rep(t, "$('f7wrap').style.display=(k==='g6'||k==='a7')?'':'none'; $('f7').checked=k==='a7';", "$('f7wrap').style.display='none'; $('f7').checked=false;")
t = t.replace("(g6|a7|g8|a1ms|a1hsadv|a1hs|geoadv|geo|a2adv|a2)", "(g3|g4|g5)")
t = rep(t, "if(!COURSES[ck]) ck=(hc.startsWith('8.')?'g8':hc.startsWith('A.')?'a1ms':hc.startsWith('G.')?'geo':hc.startsWith('2A.')?'a2adv':'g6');",
        "if(!COURSES[ck]) ck=(hc.startsWith('4.')?'g4':hc.startsWith('5.')?'g5':'g3');")
t = rep(t, "if(code.startsWith('7.') && !$('f7').checked){ $('f7').checked=true; applyStdFilters(); }", "")
t = rep(t, "if(!g7 && s.code.startsWith('7.')) show=false;", "")
t = rep(t, "if(here.some(x=>x.code.startsWith('7.'))&&$('f7wrap').style.display!=='none') $('f7').checked=true;", "")
t = rep(t, "const isCodeQ=q=>/^\\s*(2a|a|\\d{1,2})\\.\\d{0,2}[a-z]?\\s*$/i.test(q);", "const isCodeQ=q=>/^\\s*\\d{1,2}\\.\\d{0,2}[a-z]?\\s*$/i.test(q);")
t = rep(t, "const ref=g==='7'?", "const ref=false?")

t = rep(t, "<span><i class=\"kds\"></i>Dallas ISD average</span>", "")
t = rep(t, "`<span class=\"na\">${b.g==='7'?'No Dallas ISD students take Grade 7 STAAR':'no Dallas ISD data'}</span>`", "''")

t = rep(t, "$('courseSel').addEventListener('change',e=>{ const c=e.target.value; if(c!==COURSE.key){ const v=document.querySelector('.view.on').id.slice(5); loadCourse(c); showView(v); } });",
 "$('courseSel').addEventListener('change',e=>{ const c=e.target.value; if(c!==COURSE.key){ const v=document.querySelector('.view.on').id.slice(5); resetForGrade(); loadCourse(c,false); showView('std'); window.scrollTo(0,0); } });\n"
 "/* switching grade from the menu starts clean: no selected standard, lens, search, or Teaching moves selection carried over */\n"
 "function resetForGrade(){ sel=null; lens=null; query=''; $('q').value=''; QMODE='strict'; secState={code:null,open:{}}; lesMarked=null; mvSel=null; mvAnchor=null; mvQuery=''; mvBuiltFor=null; vpAll={}; document.querySelectorAll('#detail,#mvDetail').forEach(x=>x.innerHTML=''); }")

t = rep(t, "loadCourse(ck,false);\nif(STD.has(hc)) selectStd(hc,false);", "loadCourse(ck,false);\nshowView('std');\nif(STD.has(hc)) selectStd(hc,false);")

data = open('data.js').read()
moves = open('data_moves.js').read()
out = (head + '</style>\n</head>\n' + b + '<script>\n' + moves + moves_code_fix if False else None)
out = head + '</style>\n</head>\n' + b + '<script>\n' + moves + mc + '</script>\n<script>\n' + data + glue + t
open('out/index.html', 'w').write(out)
print('size', len(out)); print('FAILED:', *fails, sep='\n  ')

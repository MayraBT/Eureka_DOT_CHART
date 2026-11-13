import pdfplumber, re, json
FILES={3:'src/2b250086-IQ_Tool_-_3rd_2025-2026.pdf',4:'src/4840b1a6-IQ_Tool_Grade_4_-_2025-2026_All.pdf',5:'src/e9f09095-IQ_Tool_Grade_5_All_-_2025-2026.pdf'}
HDR=re.compile(r'^(\d+/\d+/\d+,|\d+:\d+|PM|AM|lead4ward|IQ|Tool|https://iq\.lead4ward\.com/createiq\.php|\d+/\d+)$')
def lines_of(words,tol=2.5):
    words=sorted(words,key=lambda w:(round(w['gy']),w['x0']))
    out=[]
    for w in words:
        if out and abs(out[-1]['gy']-w['gy'])<tol: out[-1]['w'].append(w)
        else: out.append({'gy':w['gy'],'w':[w]})
    for l in out:
        l['w'].sort(key=lambda w:w['x0']); l['text']=' '.join(w['text'] for w in l['w']); l['x0']=l['w'][0]['x0']; l['bottom']=max(w['gbottom'] for w in l['w'])
    return out
PERF={}; CROPS=[]
for g,f in FILES.items():
    pdf=pdfplumber.open(f); H=pdf.pages[0].height; W=pdf.pages[0].width
    allw=[]; zones=[]
    for pi,p in enumerate(pdf.pages):
        ws=p.extract_words(keep_blank_chars=False,use_text_flow=False)
        hdr=[w for w in ws if (w['top']<35 or w['bottom']>H-35) and HDR.match(w['text'])]
        ztop=max([w['bottom'] for w in hdr if w['top']<35] or [14])+3
        zbot=min([w['top'] for w in hdr if w['bottom']>H-35] or [H*0.945])-3
        zones.append((ztop,zbot))
        for w in ws:
            if w in hdr: continue
            w=dict(w); w['page']=pi; w['gy']=pi*H+w['top']; w['gbottom']=pi*H+w['bottom']; allw.append(w)
    # right bound: x0 of 'Data Analysis' panel
    dax=[w['x0'] for w in allw if w['text'] in ('Item','Points','Descriptive','Stimulus') and w['x0']>W*0.55]
    right=min(dax)-6 if dax else W*0.64
    L=lines_of(allw)
    # detect labels
    labels=[i for i,l in enumerate(L) if re.match(r'^(20\d\d)\s*–\s*Q(\d+)\b',l['text'])]
    code=rc=cluster=None
    events=[]  # header updates by line index
    cur={'code':None,'rc':None,'cluster':None}
    state_at={}
    for i,l in enumerate(L):
        t=l['text']
        m=re.search(r'Investigating the Question\s+(\d+\.\d+)\(([A-Z])\)\s+RC\s*(\d+)',t)
        if m: cur['code']=m.group(1)+m.group(2); cur['rc']=int(m.group(3))
        m=re.match(r'^(\d+\.\d+)\(([A-Z])\)\s+[a-z]',t)
        if m: cur['code']=m.group(1)+m.group(2)
        if ':' in t and l['x0']<right and not re.search(r'Correct|answer|\d\.\d+\(|^20\d\d',t) and len(t)<120 and re.match(r'^[A-Z][A-Za-z ,/\-]+: [A-Z]',t): cur['cluster']=t
        state_at[i]=dict(cur)
    for n,li in enumerate(labels):
        l=L[li]; m=re.match(r'^(20\d\d)\s*–\s*Q(\d+)',l['text']); year,q=int(m.group(1)),int(m.group(2))
        nxt=L[labels[n+1]]['gy'] if n+1<len(labels) else 1e9
        # end: first 'Correct Answer' line after label
        lim=labels[n+1] if n+1<len(labels) else len(L)
        endi=next((j for j in range(li+1,lim) if re.search(r'Correct Answer',L[j]['text']) and L[j]['x0']<right),None)
        endy=L[endi]['gy'] if endi is not None else min(nxt,len(zones)*H-1)
        if endi is None: print('NO END',g,year,q)
        seg=[x for x in L[li+1:] if x['gy']<min(nxt,endy+60)]
        rtext='\n'.join(' '.join(w['text'] for w in x['w'] if w['x0']>=right) for x in L[li:] if x['gy']<min(nxt,endy))
        ftext='\n'.join(x['text'] for x in seg)
        st=state_at[li]
        it={'year':year,'q':q}
        mt=re.search(r'Item Type\s+(.+)',rtext); it['itemType']=mt.group(1).strip() if mt else None
        mp=re.search(r'Points\s+(\d)',rtext); it['points']=int(mp.group(1)) if mp else None
        mc=re.search(r'Correct Answer\s*\((.*?)\)\s*(?:\^|$)',ftext,re.S) or re.search(r'Correct Answer\s*\((.*)\)',ftext)
        it['correct']=mc.group(1).replace('\n',' ').strip() if mc else None
        mh=re.search(r'highly chosen incorrect answer\s*\((.*?)\)',ftext)
        it['hot']=mh.group(1).strip() if mh else None
        it['rc']=st['rc']; it['cluster']=st['cluster']
        if it['itemType']=='Multiple Choice':
            ch=[];pct=None
            for x in rtext.split('\n'):
                mm=re.match(r'^([A-J])(\*?)\s*(\^?)\s*(\d+)?\s*$',x.strip())
                if mm:
                    ok=bool(mm.group(2)); ch.append({'c':mm.group(1),'ok':ok,'hot':mm.group(1)==it['hot']})
                    if ok and mm.group(4): pct=int(mm.group(4))
            it['choices']=ch; it['pct']=pct
        else:
            cr={}
            for k,lab in (('full','Full Credit'),('no','No Credit'),('partial','Partial Credit')):
                mm=re.search(lab+r'\s+(\d+)',rtext)
                if mm: cr[k]=int(mm.group(1))
            it['credit']=cr; it['pct']=cr.get('full')
        it['img']=f'items/g{g}_{year}_Q{q}.jpg'
        PERF.setdefault(st['code'],[]).append(it)
        # crop segments: from label bottom to endy-4 across pages
        y0=l['bottom']+3
        hdr_re=re.compile(r'(Investigating the Question|^\d+\.\d+\([A-Z]\)\s+[a-z]|^20\d\d\s*–\s*Q\d+|^[A-Z][A-Za-z ,/\-]+: [A-Z][A-Za-z ,/\-]+$)')
        stop=next((L[j]['gy'] for j in range((endi or li)+1,len(L)) if hdr_re.search(L[j]['text']) and L[j]['x0']<right),len(zones)*H-1)
        y1=stop-6
        masks=[(x['w'][0]['x0']-2,x['gy']-3,max(w['x1'] for w in x['w'] if w['x0']<right)+2,x['bottom']+2) for x in L[li+1:] if x['gy']<stop and (re.search(r'Correct Answer|highly chosen',x['text']) or x['text'].strip()=='*') and x['x0']<right]
        segs=[]
        p0=int(y0//H); p1=int(y1//H)
        for pg in range(p0,p1+1):
            zt,zb=zones[pg]
            a=max(y0-pg*H,zt); b=min(y1-pg*H,zb)
            if b-a>4: segs.append((pg,a,b))
        lefts=[w['x0'] for w in allw if y0<=w['gy']<=y1 and w['x1']<right]
        CROPS.append({'masks':masks,'g':g,'f':f,'year':year,'q':q,'left':max(min(lefts or [30])-8,0),'right':right,'segs':segs,'H':H,'W':W})
json.dump(PERF,open('perf.json','w'),indent=0,ensure_ascii=False)
json.dump(CROPS,open('crops.json','w'))
import collections
print('codes',len(PERF),'items',sum(len(v) for v in PERF.values()))
print(collections.Counter((c['g'],c['year']) for c in CROPS))
print([ (k,i['year'],i['q']) for k,v in PERF.items() for i in v if i['pct'] is None or not i['itemType'] or k is None])
print([ (k,i['year'],i['q'],i['correct']) for k,v in PERF.items() for i in v if i['itemType']=='Multiple Choice' and (len(i['choices'])!=4)])
print(collections.Counter(c['g'] for c in CROPS if len(c['segs'])>1))

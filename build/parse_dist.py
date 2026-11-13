"""Dallas ISD 2025-26 STAAR item analysis (SchoolCity, Assessment Level State) -> DIST, DIST_META."""
import zipfile, re, json
from xml.etree import ElementTree as ET
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def rows(path):
    z=zipfile.ZipFile(path)
    ss=[]
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.iter(NS+'si'):
        ss.append(''.join(t.text or '' for t in si.iter(NS+'t')))
    sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    out=[]
    for r in sh.iter(NS+'row'):
        vals={}
        for c in r.iter(NS+'c'):
            ref=c.get('r'); col=re.match(r'[A-Z]+',ref).group(0)
            v=c.find(NS+'v'); isv=c.find(NS+'is')
            if c.get('t')=='s' and v is not None: val=ss[int(v.text)]
            elif isv is not None: val=''.join(t.text or '' for t in isv.iter(NS+'t'))
            else: val=v.text if v is not None else None
            vals[col]=val
        out.append(vals)
    return out
DIST={}; META={}; checks=[]
perf=json.load(open('perf.json'))
for g in '345':
    R=rows(f'src/ia_g{g}.xlsx')
    flat=[' '.join(str(v) for v in r.values() if v) for r in R]
    n=int(re.search(r'Students Tested:\s*(\d+)',' '.join(flat)).group(1))
    avg=float(re.search(r'Avg\. % Correct:\s*([\d.]+)',' '.join(flat)).group(1))
    hdr=next(i for i,r in enumerate(R) if 'Item #' in r.values())
    cols={v:k for k,v in R[hdr].items() if v}
    for r in R[hdr+1:]:
        item=r.get(cols['Item #'])
        if not item or not str(item).strip().isdigit(): continue
        q=int(item); std=r.get(cols['Standard'],''); pct=float(r.get(cols['% Correct']))
        corr=(r.get(cols['Correct Answer']) or '').strip(); inc=r.get(cols['Incorrect/Partially Correct Answers']) or ''
        pts=int(float(r.get(cols['Points Possible'])))
        e={'p':round(pct)}
        if r.get(cols['Type'],'').strip()=='MC':
            wr=[(m.group(1),float(m.group(2))) for m in re.finditer(r'\b([A-J])\s*-\s*([\d.]+)%',inc)]
            if wr: e['w']=max(wr,key=lambda x:x[1])[0]
        elif pts==2:
            m=re.search(r'1 \(1pts\)\s*-\s*([\d.]+)%',inc)
            if m: e['part']=round(float(m.group(1)))
        code=re.sub(r'\((\w)\)',r'\1',std.split()[0]) if std else None
        DIST[f'{g}_2026_{q}']=e
        # match against the released item (Texas, IQ Tool)
        tx=[ (k,d) for k,v in perf.items() for d in v if k.startswith(g+'.') and d['year']==2026 and d['q']==q]
        txcodes=[k for k,_ in tx]
        checks.append((g,q,code,txcodes, tx[0][1]['points'] if tx else None, pts))
    META[f'{g}_2026']={'n':n,'avg':round(avg)}
bad=[c for c in checks if c[2] not in c[3] or c[4]!=c[5]]
print('items',len(DIST),'mismatches',bad)
json.dump({'DIST':DIST,'META':META},open('dist.json','w'))
print(META)

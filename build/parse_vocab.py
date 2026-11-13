import pdfplumber, re, json, sys
def parse(path):
    blocks=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            txt=p.extract_text() or ''
            lines=[l.strip() for l in txt.split('\n') if l.strip()]
            cluster=None
            for i,l in enumerate(lines):
                if re.search(r'\|\s*Grade \d|\|\s*Grado|Análisis|Analysis',l) and i+1<len(lines):
                    cluster=lines[i+1]; break
            tabs=p.extract_tables()
            if not tabs: continue
            t=max(tabs,key=len)
            cur=None
            for r in t:
                r=[(c or '').strip() for c in r]
                if not any(r): continue
                if r[0] and len(r)>3 and re.search(r'\d\.\d+\(',r[3] if len(r)>3 else ''):
                    cur={'cluster':cluster,'sub':r[0].replace('\n',' '),'codes':[re.sub(r'\((\w)\)',r'\1',c) for c in re.findall(r'\d+\.\d+\([A-Z]\)',r[3])],'new':[],'prev':[]}
                    blocks.append(cur)
                if not cur: continue
                for j,c in enumerate(r):
                    if j<6 or not c: continue
                    tgt=cur['new'] if j<=10 else cur['prev']
                    for w in c.split('\n'):
                        w=w.strip()
                        if w and w not in tgt: tgt.append(w)
    for b in blocks:
        b['prev']=[w for w in b['prev'] if w not in b['new']]
    return blocks
out={}
import glob
for g in '345':
    en=glob.glob(f'src/*Grade_{g}_-_Vocab.pdf')[0]; sp=glob.glob(f'src/*Grade_{g}_-_Vocab_SP.pdf')[0]
    out[g]={'en':parse(en),'sp':parse(sp)}
    print(g,len(out[g]['en']),len(out[g]['sp']))
json.dump(out,open('vocab.json','w'),ensure_ascii=False,indent=0)
for b in out['3']['en'][:4]: print(b)
for b in out['3']['sp'][:4]: print(b)

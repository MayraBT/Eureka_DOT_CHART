"""usage: split.py SRC.pdf G MODULE[,MODULE2]  -> out/G{g}_M{m}_L{nn}_TE.pdf ; prints ranges"""
import pypdf,re,sys,json,os
src,g,mods=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
r=pypdf.PdfReader(src)
# footer like "2 • 5 | 13 | Lesson 1:" -> module from "G • M"
lab=[]
for i,p in enumerate(r.pages):
    t=p.extract_text() or ''
    head=t.split('©')[0]
    m=None
    if 'Topic' not in head and 'Module Overview' not in head and 'Answer Key' not in t[:80]:
        m=re.search(r'Lesson (\d+)\b',head) or re.search(r'greatminds\.org/Texas\s*(?:\|\s*)?Lesson (\d+)\b',t[:600])
    mm=re.search(r'(?<![\d.])'+re.escape(g)+r' • (\d+)',t[:500])
    lab.append((mm.group(1) if mm else None, int(m.group(1)) if m else None))
runs={}
for i,(m,l) in enumerate(lab):
    if l is None or m not in mods: continue
    runs.setdefault((m,l),[]).append(i)
res={}
os.makedirs('out',exist_ok=True)
for (m,l),pages in sorted(runs.items(),key=lambda x:(int(x[0][0]),x[0][1])):
    # contiguous check
    cl=[[pages[0]]]
    for a,b in zip(pages,pages[1:]):
        if b-a<=3: cl[-1].append(b)
        else: cl.append([b])
    best=max(cl,key=len); gaps=[c for c in cl if c is not best]; pages=best
    w=pypdf.PdfWriter()
    for i in range(pages[0],pages[-1]+1): w.add_page(r.pages[i])
    name=f'G{g}_M{m}_L{l:02d}_TE.pdf'; w.compress_identical_objects() if hasattr(w,'compress_identical_objects') else None
    w.write('out/'+name)
    res[name]={'from':pages[0]+1,'to':pages[-1]+1,'gaps':len(gaps),'kb':os.path.getsize('out/'+name)//1024}
json.dump(res,open(f'ranges_G{g}_{"_".join(mods)}.json','w'),indent=0)
for k,v in res.items(): print(k,v)

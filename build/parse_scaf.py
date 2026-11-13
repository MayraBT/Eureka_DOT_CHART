import openpyxl, re, json, warnings, glob
warnings.filterwarnings('ignore')
files={3:'src/4e0dd492-teks_scaffold_math_gr_03.xlsx',4:'src/9a5f6328-teks_scaffold_math_gr_04.xlsx',5:'src/aef37774-teks_scaffold_math_gr_05.xlsx'}
SCAF=[]; TEKS={}; TYPE={}; STRAND={}
for g,f in files.items():
    wb=openpyxl.load_workbook(f,data_only=True)
    for ws in wb.worksheets[1:]:
        if ws.title.startswith('Process'): continue
        cluster=(ws.cell(1,1).value or ws.title).strip()
        sub=None; ses=[]
        rows=list(ws.iter_rows(values_only=True))
        for i,r in enumerate(rows):
            a,b=r[0],r[1]
            if i<4:
                if b and isinstance(r[0],str) and re.match(r'^\d+\.\d+$',r[0].strip()):
                    STRAND[r[0].strip()]=b.strip()
                continue
            c=r[2] if len(r)>2 else None; t=r[3] if len(r)>3 else None
            if b and not c and isinstance(b,str) and not re.match(r'^\s*[\dA-Z]+\.\d+\(',b):
                if b.strip().startswith('Connected'): continue
                if sub and ses: SCAF.append({'cluster':cluster,'sub':sub,'ses':ses,'src':g})
                sub=b.strip(); ses=[]; continue
            if isinstance(b,str) and b.strip()=='#': continue
            if isinstance(b,str) and re.match(r'^\s*[\dK]+\.\d+\(?[A-Z]\)?\b',b.strip()):
                code=re.sub(r'\((\w)\)',r'\1',b.strip().split()[0])
                text=' '.join(str(c).replace('\x81','').split()) if c else ''
                typ=(str(t).strip() if t else 'S')[:1]; typ='U' if typ=='N' else typ
                ses.append({'code':code,'text':text,'type':typ})
                gr=code.split('.')[0]
                if gr==str(g):
                    TEKS[code]=text; TYPE[code]=typ
        if sub and ses: SCAF.append({'cluster':cluster,'sub':sub,'ses':ses,'src':g})
json.dump({'SCAF':SCAF,'TEKS':TEKS,'TYPE':TYPE,'STRAND':STRAND},open('scaf.json','w'),ensure_ascii=False,indent=0)
print(len(SCAF),len(TEKS))
for g in '345':
    ks=sorted([k for k in TEKS if k.startswith(g+'.')],key=lambda k:(int(k.split('.')[1][:-1]),k[-1]))
    print(g,len(ks),' '.join(k+TYPE[k] for k in ks))
print(STRAND)
print(SCAF[0])

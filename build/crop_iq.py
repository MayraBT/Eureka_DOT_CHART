import json, subprocess, os
from PIL import Image
DPI=200; S=DPI/72
crops=json.load(open('crops.json'))
cache={}
def page(f,pg):
    k=(f,pg)
    if k not in cache:
        base=f'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/iq/{os.path.basename(f)[:8]}_{pg}'
        if not os.path.exists(base+'.png'):
            subprocess.run(['pdftoppm','-r',str(DPI),'-png','-singlefile','-f',str(pg+1),'-l',str(pg+1),f,base],check=True)
        cache.clear(); cache[k]=Image.open(base+'.png').convert('RGB')
    return cache[k]
done=set()
for c in sorted(crops,key=lambda c:(c['f'],c['segs'][0][0])):
    name=f"out/items/g{c['g']}_{c['year']}_Q{c['q']}.jpg"
    if name in done: continue
    parts=[]
    for pg,a,b in c['segs']:
        im=page(c['f'],pg)
        im=im.copy(); from PIL import ImageDraw; d=ImageDraw.Draw(im)
        for (mx0,my0,mx1,my1) in c['masks']:
            py0=my0-pg*c['H']; py1=my1-pg*c['H']
            if py1>0 and py0<c['H']: d.rectangle((mx0*S,py0*S,mx1*S,py1*S),fill='white')
        parts.append(im.crop((int(c['left']*S),int(a*S),int(c['right']*S),int(b*S))))
    W=max(p.width for p in parts); H=sum(p.height for p in parts)
    out=Image.new('RGB',(W,H),'white'); y=0
    for p in parts: out.paste(p,(0,y)); y+=p.height
    # trim white bottom/right
    import PIL.ImageOps as O
    bbox=O.invert(out.convert('L')).point(lambda v:255 if v>12 else 0).getbbox()
    if bbox: out=out.crop((0,0,min(W,bbox[2]+16),min(H,bbox[3]+16)))
    out.save(name,quality=82,optimize=True); done.add(name)
print(len(done))

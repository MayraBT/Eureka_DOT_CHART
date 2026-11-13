from PIL import Image
import numpy as np, glob, sys
def clean(path):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    g=a.mean(axis=2); H,W=g.shape
    dark=g<235
    # drop vertical rules: columns where >45% rows are non-white, scanning from both edges (within 40px)
    colfrac=dark.mean(axis=0)
    L=0
    for x in range(int(W*0.06)):
        if colfrac[x]>0.15: L=x+1
    R=W
    for x in range(int(W*0.86),W):
        if colfrac[x]>0.15: R=x; break
    # also drop the scrollbar-like gutter: any column band at the far right with sparse dots
    
    g=g[:,L:R]; a=a[:,L:R]; dark=g<235
    # collapse white horizontal runs > 50px to 24px
    rowdark=dark.sum(axis=1)>0
    keep=[]; run=0
    for y in range(len(rowdark)):
        if rowdark[y]: run=0; keep.append(y)
        else:
            run+=1
            if run<=24: keep.append(y)
    a=a[keep]
    # trim bbox
    d=(a.mean(axis=2)<235)
    ys=np.where(d.any(axis=1))[0]; xs=np.where(d.any(axis=0))[0]
    if len(ys)==0: return
    y0,y1=max(ys[0]-14,0),min(ys[-1]+14,a.shape[0]); x0,x1=max(xs[0]-14,0),min(xs[-1]+14,a.shape[1])
    out=Image.fromarray(a[y0:y1,x0:x1].astype('uint8'))
    out.save(path,quality=82,optimize=True)
for p in glob.glob('out/items/*.jpg'): clean(p)

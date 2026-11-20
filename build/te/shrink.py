"""shrink.py FILE.pdf [limit_bytes]: rasterize vector-heavy pages until the file is under the limit (default 3,000,000)."""
import pymupdf as fitz, sys, os, io
f=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 3_000_000
for dpi in (130,110,90,72):
    src=fitz.open(f); out=fitz.open()
    for p in src:
        heavy=len(p.get_drawings())>1500
        if heavy:
            pix=p.get_pixmap(dpi=dpi); img=pix.tobytes('jpeg',jpg_quality=72)
            np_=out.new_page(width=p.rect.width,height=p.rect.height); np_.insert_image(np_.rect,stream=img)
        else:
            out.insert_pdf(src,from_page=p.number,to_page=p.number)
    tmp=f+'.tmp'; out.save(tmp,garbage=4,deflate=True); s=os.path.getsize(tmp)
    if s<lim: os.replace(tmp,f); print(f,'ok',dpi,s); break
    os.remove(tmp)
else: print(f,'STILL TOO BIG')

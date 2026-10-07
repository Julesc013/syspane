"""Independent exact pixel-center reference. Production never imports this file."""
from fractions import Fraction as F
from pathlib import Path
import json,random,sys
def expected(sw,sh,w,h,mode,pixels):
    kx,ky=F(w,sw),F(h,sh)
    if mode!='stretch':kx=ky=(min if mode=='contain' else max)(kx,ky)
    left,top=(w-sw*kx)/2,(h-sh*ky)/2
    out=[]
    for y in range(h):
        for x in range(w):
            px,py=F(2*x+1,2),F(2*y+1,2)
            if not (left<=px<left+sw*kx and top<=py<top+sh*ky):out.extend([0]*4);continue
            sx=min(sw-1,max(F(0),(px-left)/kx-F(1,2)))
            sy=min(sh-1,max(F(0),(py-top)/ky-F(1,2)))
            ax,ay=sx.numerator//sx.denominator,sy.numerator//sy.denominator
            bx,by=min(sw-1,ax+1),min(sh-1,ay+1);fx,fy=sx-ax,sy-ay
            for c in range(4):
                v=sum(pixels[(yy*sw+xx)*4+c]*wx*wy for xx,wx in ((ax,1-fx),(bx,fx)) for yy,wy in ((ay,1-fy),(by,fy)))
                out.append((2*v.numerator+v.denominator)//(2*v.denominator))
    return out
def cases():
    rng=random.Random(92007);out=[]
    for i in range(180):
        sw,sh,w,h=[rng.randrange(1,10) for _ in range(4)];mode=('contain','cover','stretch')[i%3];pixels=[]
        for _ in range(sw*sh):
            alpha=rng.randrange(256);pixels.extend([rng.randrange(alpha+1) for _ in range(3)]+[alpha])
        out.append(dict(source=[sw,sh],target=[w,h],mode=mode,rgba=pixels,expected=expected(sw,sh,w,h,mode,pixels)))
    return out
path=Path(__file__).with_name('image-cases')/'fit.json'
data=json.dumps(cases(),separators=(',',':'))+'\n'
if '--check' in sys.argv:assert path.read_text()==data
else:path.parent.mkdir(exist_ok=True);path.write_text(data,encoding='utf-8',newline='\n')
print('180 independent rational fit cases')

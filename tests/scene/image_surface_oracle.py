"""Independent source samples and exact scene-image expectations; no production imports."""
from fractions import Fraction as F
from pathlib import Path
import json,sys
SAMPLES=[255,0,0,255,0,128,0,128,0,0,0,0,255,255,255,255]
def fit(w,h,mode):
    sx,sy=F(w,2),F(h,2)
    if mode!='stretch':sx=sy=(min if mode=='contain' else max)(sx,sy)
    left,top=(w-2*sx)/2,(h-2*sy)/2;out=[]
    for y in range(h):
        for x in range(w):
            px,py=F(2*x+1,2),F(2*y+1,2)
            if not(left<=px<left+2*sx and top<=py<top+2*sy):out.extend([0]*4);continue
            u=min(F(1),max(F(0),(px-left)/sx-F(1,2)));v=min(F(1),max(F(0),(py-top)/sy-F(1,2)))
            for c in range(4):
                q=SAMPLES[c]*(1-u)*(1-v)+SAMPLES[4+c]*u*(1-v)+SAMPLES[8+c]*(1-u)*v+SAMPLES[12+c]*u*v
                out.append((q.numerator*2+q.denominator)//(q.denominator*2))
    return out
def cases():return [dict(width=w,height=h,fit=mode,rgba=fit(w,h,mode)) for w,h in ((9,5),(18,10)) for mode in ('contain','cover','stretch')]
if __name__=='__main__':
    path=Path(__file__).with_name('image-cases')/'surface.json';data=json.dumps(cases(),separators=(',',':'))+'\n'
    if '--check' in sys.argv:assert path.read_text()==data
    else:path.write_text(data,encoding='utf-8',newline='\n')
    print('6 fixed scene-image pixel expectations')

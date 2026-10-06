"""Prepare fixed expectations using Python's exact rational arithmetic, not C++ geometry."""
from fractions import Fraction
from pathlib import Path
import json,random,struct,sys
ROOT=Path(__file__).resolve().parent/'chart-cases';ROOT.mkdir(exist_ok=True)
def real(bits):return {'f':f'{bits:016x}'}
def integer(n):return {'u':str(n)}
def exact(v):
    if 'u' in v:return Fraction(int(v['u']))
    return Fraction.from_float(struct.unpack('>d',bytes.fromhex(v['f']))[0])
def case(low,high,value,height):
    a,b,n=map(exact,(low,high,value));assert a<b
    n=max(a,min(n,b));q=(n-a)*(height-1)/(b-a)
    rounded=(2*q.numerator+q.denominator)//(2*q.denominator)
    return dict(low=low,high=high,value=value,height=height,y=height-1-rounded,clipped=int(exact(value)<a or exact(value)>b))
values=[integer(0),integer(1),integer(2**53),integer(2**53+1),integer(2**64-2),integer(2**64-1),
        real(1),real(0x8000000000000001),real(0x7fefffffffffffff),real(0xffefffffffffffff),real(0x3ff0000000000000)]
cases=[case(integer(2**64-3),integer(2**64-1),integer(2**64-2),120),
       case(real(0xffefffffffffffff),real(0x7fefffffffffffff),integer(0),120),
       case(real(0x8000000000000001),real(1),integer(0),120)]
r=random.Random(932417)
for _ in range(320):
    def number():
        if r.randrange(3)==0:return integer(r.getrandbits(64))
        return real((r.randrange(2)<<63)|(r.randrange(2047)<<52)|r.getrandbits(52))
    a,b,n=(r.choice(values) if r.randrange(3)==0 else number() for _ in range(3))
    if exact(a)==exact(b):continue
    if exact(a)>exact(b):a,b=b,a
    cases.append(case(a,b,n,r.choice((2,3,5,120,257,2048))))
data=json.dumps(cases,indent=2)+'\n';path=ROOT/'numeric.json'
if '--check' in sys.argv:assert path.read_text()==data
else:path.write_text(data,encoding='utf-8',newline='\n')
print(len(cases),'exact rational cases')

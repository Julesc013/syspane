from pathlib import Path
from datetime import datetime,timezone
import copy,json,hashlib,zipfile
r=Path(__file__).resolve().parents[2]
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
base=dict(selection=[40,40,120,80],area=[0,0,500,420],siblings=[dict(id='widget:second',box=[200,170,96,64]),dict(id='widget:third',box=[370,300,80,48])],origin=[0,0],spacing=8,threshold=6,grid=True,guides=False,resize=False,bypass=False,delta=[29,21])
cases=[]
def case(name,changes,delta,x=None,y=None):
    v=copy.deepcopy(base);v.update(changes);cases.append(dict(name=name,input=v,expected=dict(delta=delta,x=x,y=y)))
def guide(position,source='grid',target='',moving=0,anchor=0):return dict(position=position,source=source,target=target,moving=moving,anchor=anchor)
case('grid',{},[32,24],guide(72),guide(64))
case('zero-axis',dict(delta=[0,21]),[0,24],None,guide(64))
case('negative-tie',dict(selection=[-13,-13,120,80],delta=[1,1]),[-3,-3],guide(-16),guide(-16))
case('positive-tie',dict(delta=[4,4]),[8,8],guide(48),guide(48))
case('origin',dict(origin=[3,5]),[27,21],guide(67),guide(61))
case('fraction',dict(selection=[40.015625,40,120,80],delta=[29,21]),[31.984375,24],guide(72),guide(64))
case('resize',dict(resize=True,delta=[7,7]),[8,8],guide(168,moving=2),guide(128,moving=2))
case('invalid-size',dict(resize=True,delta=[-121,0]),[-121,0])
case('threshold',dict(spacing=32,delta=[7,0]),[7,0])
case('inclusive',dict(spacing=32,delta=[-2,0]),[-8,0],guide(32))
case('guides',dict(grid=False,guides=True,delta=[37,45]),[40,50],guide(200,'sibling','widget:second',2,0),guide(170,'sibling','widget:second',2,0))
case('priority',dict(grid=True,guides=True,delta=[38,0]),[40,0],guide(200,'sibling','widget:second',2,0))
case('area',dict(grid=False,guides=True,siblings=[],delta=[87,0]),[90,0],guide(250,'area','',2,1))
case('order',dict(grid=False,guides=True,delta=[38,0],siblings=[dict(id='z',box=[200,170,96,64]),dict(id='b',box=[196,170,96,64]),dict(id='a',box=[196,170,96,64])]),[36,0],guide(196,'sibling','a',2,0))
case('bypass',dict(bypass=True),[29,21])
case('disabled',dict(grid=False),[29,21])
case('union',dict(selection=[40,40,256,194]),[32,24],guide(72),guide(64))
authored=json.loads((r/'tests/editor/group-cases.json').read_text())['authored'];expected={}
for name,dx,dy,resize,multi in [('grid',32,24,False,False),('guides',40,50,False,False),('bypass',29,21,False,False),('resize',8,8,True,False),('multi',32,24,False,True),('keyboard',1,0,False,False)]:
    s=copy.deepcopy(authored['scene'])
    for w in s['widgets'][:2 if multi else 1]:
        b=w['layout']['base'];b['width' if resize else 'x']+=dx;b['height' if resize else 'y']+=dy
    expected[name]=s
value=dict(cases=cases,authored=authored,expected=expected,erase_ms=200,native_modes=['grid','guides','resize','multi','bypass','keyboard','escape','options','cancel','revoke','restart','wrong-commit','frozen-preview'])
write(r/'tests/editor/snap-cases.json',value)
d=r/'out/campaign/w-10-snap';d.mkdir();names=['tests/editor/snap-cases.json','spec/delivery/packages/w-10-snap.md'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for n in names:z.write(r/n,n)
write(d/'fixed-inputs.json',dict(frozen_at=datetime.now(timezone.utc).isoformat(),inputs={n:sha(r/n) for n in names},archive_sha256=sha(d/'fixed-inputs.zip')))
print('Frozen contract and literal snap outcomes before implementation.')

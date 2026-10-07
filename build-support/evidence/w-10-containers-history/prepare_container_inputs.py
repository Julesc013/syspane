from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign/w-10-containers';out.mkdir(exist_ok=True)
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
base=json.loads((r/'tests/editor/layout-authoring-cases.json').read_bytes())['authored'];base=copy.deepcopy(base)
s=base['scene'];s['widgets'][3]['layout']['base']['height']=360
flow={'kind':'flow','width':{'min':180,'preferred':180,'max':180},'height':{'min':80,'preferred':80,'max':80},'anchor':'start'}
for w in s['widgets'][:2]:w['layout']={'base':copy.deepcopy(flow)}
layouts={
 'stack-horizontal':{'base':{'kind':'stack','axis':'horizontal','gap_dip':20,'overflow':'diagnose'}},
 'stack-vertical':{'base':{'kind':'stack','axis':'vertical','gap_dip':20,'overflow':'diagnose'}},
 'grid':{'base':{'kind':'grid','columns':2,'gap_dip':20,'overflow':'diagnose'}},
 'canvas':{'base':{'kind':'canvas','width':400,'height':180,'overflow':'diagnose'}},
 'fixed':{'base':{'kind':'fixed','x':30,'y':40,'width':400,'height':200}},
 'responsive':{'base':{'kind':'stack','axis':'vertical','gap_dip':8,'overflow':'diagnose'},'breakpoints':[{'min_width_dip':400,'layout':{'kind':'stack','axis':'horizontal','gap_dip':20,'overflow':'diagnose'}}]}}
expected={}
for name,layout in layouts.items():
    scene=copy.deepcopy(s);scene['widgets'][3]['children']=['widget:new1']
    scene['widgets'].append(dict(id='widget:new1',kind='group',title='Container',display={'local_id':'D1'},layout=layout,bindings=[],priority='normal',content={},children=['widget:text','widget:second']))
    expected[name]=scene
geometry={'initial':[[20,20,180,80],[20,100,180,80]],'stack-horizontal':[[20,20,180,80],[220,20,180,80]],'stack-vertical':[[20,20,180,80],[20,120,180,80]],'grid':[[20,20,180,80],[260,20,180,80]],'canvas':[[20,20,180,80],[20,100,180,80]],'fixed':[[50,60,180,80],[50,140,180,80]],'responsive':[[20,20,180,80],[220,20,180,80]],'responsive-narrow':[[20,20,180,80],[20,108,180,80]]}
# Removing the fixed outer container intentionally removes its origin and clipping.
unwrapped=copy.deepcopy(s);unwrapped['roots']=['widget:text','widget:second','widget:image'];unwrapped['widgets'].pop()
# Nonadjacent wrapper order: A,C become one unit ahead of B, even with caller C,A.
nonadjacent=copy.deepcopy(s);third=copy.deepcopy(s['widgets'][1]);third.update(id='widget:third',title='Third pane',content={'body':'Third pane'})
nonadjacent['widgets'].insert(2,third);nonadjacent['widgets'][4]['children']=['widget:text','widget:second','widget:third']
nonadjacent_expected=copy.deepcopy(nonadjacent);nonadjacent_expected['widgets'][4]['children']=['widget:new1','widget:second']
wrapper=copy.deepcopy(expected['stack-horizontal']['widgets'][-1]);wrapper['children']=['widget:text','widget:third'];nonadjacent_expected['widgets'].append(wrapper)
write(r/'tests/editor/container-cases.json',dict(authored=base,layouts=layouts,expected=expected,geometry=geometry,unwrapped=unwrapped,nonadjacent=nonadjacent,nonadjacent_expected=nonadjacent_expected,erase_ms=200,native_cases=['stack-horizontal','stack-vertical','grid','canvas','fixed','responsive','unwrap','cancel-buffer','invalid','restart','revoke','topology','wrong-container','retain-container','frozen-preview']))
p=r/'spec/delivery/packages/w-10-containers.md';p.write_text(p.read_text().replace('2026-10-07T11:30:00Z',datetime.now(timezone.utc).isoformat()),encoding='utf-8',newline='\n')
paths=['spec/delivery/packages/w-10-containers.md','tests/editor/container-cases.json'];hashes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(out/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
write(out/'fixed-inputs.json',dict(inputs=hashes,archive_sha256=hashlib.sha256((out/'fixed-inputs.zip').read_bytes()).hexdigest()))
print('Frozen container contract, complete scenes and independent geometry.')

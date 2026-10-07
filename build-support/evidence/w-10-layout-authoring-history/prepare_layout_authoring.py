from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,re,zipfile
r=Path(__file__).resolve().parents[2];d=r/'out/campaign/w-10-layout-authoring';d.mkdir()
p=r/'spec/delivery/packages/w-10-layout-authoring.md';s=p.read_text();s=s.replace('2026-10-07T10:00:00Z',datetime.now(timezone.utc).isoformat());p.write_text(s,encoding='utf-8',newline='\n')
authored=copy.deepcopy(json.loads((r/'tests/editor/native-cases.json').read_text())['authored']);scene=authored['scene']
scene['roots']=['widget:group','widget:image'];scene['widgets'][0]['layout']['base'].update(x=20,y=20);scene['widgets'][1]['layout']['base'].update(x=250,y=20)
scene['widgets'].append(dict(id='widget:group',kind='group',title='Layout group',display={'local_id':'D1'},layout={'base':dict(kind='fixed',x=20,y=20,width=460,height=260)},priority='normal',bindings=[],content={},children=['widget:text','widget:second']))
def flow(anchor='start'):return dict(kind='flow',width=dict(min=32,preferred=180,max=32768),height=dict(min=16,preferred=80,max=32768),anchor=anchor)
layouts={'fixed':dict(kind='fixed',x=70,y=60,width=210,height=90),'canvas':dict(kind='canvas',width=460,height=260,overflow='diagnose'),'stack-horizontal':dict(kind='stack',axis='horizontal',gap_dip=20,overflow='diagnose'),'stack-vertical':dict(kind='stack',axis='vertical',gap_dip=20,overflow='scroll'),'grid':dict(kind='grid',columns=2,gap_dip=20,overflow='diagnose')}
for anchor in ('start','center','end','stretch'):layouts['flow-'+anchor]=flow(anchor)
expected={}
for name,layout in layouts.items():
    s=copy.deepcopy(scene);index=3 if name in ('canvas','stack-horizontal','stack-vertical','grid') else 0;s['widgets'][index]['layout']={'base':layout};expected[name]=s
    if name in ('stack-horizontal','stack-vertical','grid'):
        for w in s['widgets'][:2]:w['layout']={'base':flow('stretch' if name=='grid' else 'start')}
responsive={'base':copy.deepcopy(scene['widgets'][0]['layout']['base']),'breakpoints':[dict(min_width_dip=400,layout=dict(kind='fixed',x=80,y=60,width=220,height=90)),dict(min_width_dip=800,layout=flow('end'))]}
s=copy.deepcopy(scene);s['widgets'][0]['layout']=responsive;expected['breakpoints']=s
s=copy.deepcopy(expected['breakpoints']);s['widgets'][0]['layout']['breakpoints'][0]['layout'].update(x=110,y=80);expected['variant-move']=s
s=copy.deepcopy(expected['breakpoints']);s['widgets'][0]['layout']['breakpoints'][0]['layout'].update(width=240,height=100);expected['variant-resize']=s
s=copy.deepcopy(expected['breakpoints']);s['widgets'][1]['layout']['base']['x']=80;expected['variant-align']=s
s=copy.deepcopy(scene);s['widgets'][0]['priority']='essential';s['widgets'][3]['children']=['widget:second','widget:text'];expected['order-priority']=s
s=copy.deepcopy(scene)
for index in (0,1,3):s['widgets'][index]['display']={'role':'work'}
expected['display']=s
value=dict(authored=authored,layouts=layouts,responsive=responsive,expected=expected,erase_ms=200,
    geometry={'stack-horizontal':{'widget:text':[0,0,180,80],'widget:second':[200,0,180,80]},'stack-vertical':{'widget:text':[0,0,180,80],'widget:second':[0,100,180,80]},'grid':{'widget:text':[0,0,240,80],'widget:second':[260,0,240,80]},'breakpoints':{'widget:text':[100,80,220,90]},'variant-move':{'widget:text':[130,100,220,90]},'variant-resize':{'widget:text':[100,80,240,100]}},
    native_cases=['fixed','flow','canvas','stack-horizontal','stack-vertical','grid','breakpoints','variant-drag','variant-keyboard','variant-resize','variant-align','order-priority','display','invalid','cancel-buffer','revoke','topology','restart','wrong-layout','retain-layout','frozen-preview'])
p=r/'tests/editor/layout-authoring-cases.json';p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
names=['spec/delivery/packages/w-10-layout-authoring.md','tests/editor/layout-authoring-cases.json','tests/configuration/settings-content-fixture.json','tests/editor/native-cases.json','tests/editor/observation-cases.json','spec/contracts/layout.schema.json','spec/contracts/scene-v0.3.schema.json']
hashes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in names}
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for n in names:z.write(r/n,n)
(d/'fixed-inputs.json').write_text(json.dumps(dict(inputs=hashes,archive_sha256=hashlib.sha256((d/'fixed-inputs.zip').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n')
print('Frozen layout package, exact scenes and geometry before implementation.')

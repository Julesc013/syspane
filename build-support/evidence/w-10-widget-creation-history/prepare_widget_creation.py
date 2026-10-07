from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import json,hashlib,zipfile
r=Path.cwd();p=r/'spec/delivery/packages/w-10-widget-creation.md';s=p.read_text();assert s.count('@GENERATED@')==1;p.write_text(s.replace('@GENERATED@',datetime.now(timezone.utc).isoformat()),encoding='utf-8',newline='\n')
base=json.loads((r/'tests/editor/content-properties-cases.json').read_text());scene=base['authored']['scene'];expected={};objects={}
sizes=dict(text=[180,80],value=[240,100],status=[240,120],table=[420,180],chart=[400,240],image=[160,120],group=[320,240])
query=dict(kind='selector',scope=dict(kind='local_host'),entity_type='network.interface',mode='singleton',predicates=[],sort=[],limit=1,field='network.receive_bytes')
for kind,(width,height) in sizes.items():
 w=dict(id='widget:new1',kind=kind,title=kind.capitalize(),display=dict(local_id='D1'),layout=dict(base=dict(kind='fixed',x=20,y=20,width=width,height=height)),bindings=[],priority='normal',content={})
 if kind=='text':w['content']=dict(body='Text')
 if kind in ('value','status','chart'):w['bindings']=[deepcopy(query)]
 if kind=='table':
  w['bindings']=[{**deepcopy(query),'mode':'collection','limit':8,'field':field} for field in ('network.receive_bytes','network.transmit_bytes')];w['content']=dict(columns=[dict(label='Receive'),dict(label='Sent')])
 if kind=='chart':w['content']=dict(window_ms=60000,max_points=256,interpolation='linear',axis=dict(mode='auto',include_zero=True))
 if kind=='image':w['content']=dict(asset=base['gray_asset'],alt='Image',width_dip=160,height_dip=120,fit='contain')
 if kind=='group':w['children']=[]
 objects[kind]=w;s=deepcopy(scene);s['widgets'].append(w);s['roots'].append('widget:new1');expected[kind]=s
nested=deepcopy(expected['group']);child=deepcopy(objects['text']);child['id']='widget:new2';child['title']='Nested';child['content']['body']='Nested body';nested['widgets'][-1]['children']=['widget:new2'];nested['widgets'].append(child);expected['nested']=nested
cases=dict(authored=base['authored'],objects=objects,expected=expected,gray_asset=base['gray_asset'],erase_ms=200,native_modes=['text','value','status','table','chart','image','group','nested','buffers','invalid','cancel-buffer','cancel','restart','revoke','wrong-insert','frozen-preview','retain-create'])
p=r/'tests/editor/widget-creation-cases.json';assert not p.exists();p.write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
d=r/'out/campaign/w-10-widget-creation';d.mkdir();paths=['spec/delivery/packages/w-10-widget-creation.md','tests/editor/widget-creation-cases.json','tests/editor/content-properties-fixture.json'];inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'fixed-inputs.json').write_text(json.dumps(dict(inputs=inputs,archive_sha256=hashlib.sha256((d/'fixed-inputs.zip').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n');print(inputs)

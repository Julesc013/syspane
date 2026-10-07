from pathlib import Path
from copy import deepcopy
import hashlib,json,zipfile
r=Path.cwd();base=json.loads((r/'tests/editor/content-properties-cases.json').read_text());scene=base['authored']['scene'];expected={}
direct=dict(kind='direct',producer_id='P1',producer_epoch='E1',entity_id='nic:one',field='network.transmit_bytes')
persistent=dict(kind='persistent_pin',scope=dict(kind='registered_asset',asset_id='asset:remote'),namespace='network.adapter',key='Adapter\n\u03b1',entity_type='network.adapter',field='network.transmit_bytes')
legacy=dict(kind='unresolved_pin',source_schema_version='0.1.0',entity_id='nic:legacy',field='network.receive_bytes',reason='producer_context_required')
selector=dict(kind='selector',scope=dict(kind='current_session'),entity_type='network.adapter',mode='singleton',predicates=[dict(field='entity.display_name',op='ne',value='Ghost'),dict(field='network.receive_bytes',op='eq',value=9007199254740993)],sort=[dict(field='entity.display_name',direction='descending'),dict(field='entity.id',direction='ascending')],limit=7,field='network.transmit_bytes')
table=deepcopy(scene['widgets'][1]['bindings'][0]);table.update(predicates=[dict(field='entity.id',op='ne',value='nic:absent')],sort=[dict(field='entity.id',direction='descending')],limit=1)
descriptors=dict(direct=direct,persistent=persistent,legacy=legacy,selector=selector,table=table)
for name,descriptor in descriptors.items():
 s=deepcopy(scene)
 if name=='table':
  for n,b in enumerate(s['widgets'][1]['bindings']):s['widgets'][1]['bindings'][n]={**deepcopy(descriptor),'field':b['field']}
 else:s['widgets'][2]['bindings']=[descriptor]
 expected[name]=s
for name in ('field','empty','local'):
 s=deepcopy(scene)
 if name=='field':s['widgets'][2]['bindings'][0]['field']='network.transmit_bytes'
 if name=='empty':s['widgets'][2]['bindings'][0]['predicates']=[dict(field='entity.id',op='eq',value='nic:absent')]
 if name=='local':s['widgets'][2]['bindings']=[{**deepcopy(persistent),'scope':{'kind':'local_host'}}]
 expected[name]=s
cases=dict(authored=base['authored'],descriptors=descriptors,expected=expected,erase_ms=200,native_modes=['field','table','direct','persistent','selector','empty','invalid','cancel-buffer','cancel','restart','revoke','wrong-binding','frozen-preview','retain-binding'])
p=r/'tests/editor/binding-authoring-cases.json';assert not p.exists();p.write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
paths=['spec/delivery/packages/w-10-binding-authoring.md','tests/editor/binding-authoring-cases.json','tests/editor/content-properties-fixture.json']
d=r/'out/campaign/w-10-binding-authoring';d.mkdir();inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'fixed-inputs.json').write_text(json.dumps(dict(inputs=inputs),indent=2)+'\n');print(inputs)

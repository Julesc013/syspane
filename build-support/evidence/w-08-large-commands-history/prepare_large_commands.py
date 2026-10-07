from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, zipfile
r=Path(__file__).resolve().parents[2]
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def write(p,v):
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
cases=json.loads((r/'tests/editor/native-cases.json').read_bytes())
scene=cases['authored']['scene'];scene['extensions']['author.padding']=''
remaining=262140-len(encoded(scene));pattern='é"\\'
unit=len(encoded(pattern))-2
scene['extensions']['author.padding']=pattern*(remaining//unit)+'x'*(remaining%unit)
assert len(encoded(scene))==262140
moved=copy.deepcopy(scene);moved['widgets'][0]['layout']['base'].update(x=70.0,y=60.0)
assert len(encoded(moved))==262144
cases['moved_scene']=moved
cases['modes']=['drag','cancel','restart','revoke','wrong-commit'];cases['recovery_modes']=[]
cases['limits']={'scene_initial':262140,'scene_moved':262144,'command':327680,'frame_floor':328704,'ledger_bytes':16777216,'maximum_records':50,'retention_ms':600000}
write(r/'tests/configuration/large-command-cases.json',cases)
schema=json.loads((r/'spec/contracts/command-v0.4.schema.json').read_bytes())
schema['$id']=schema['$id'].replace('0.4.0','0.5.0');schema['title']='SysPane complete-scene command 0.5.0'
schema['properties']['schema_version']['const']='0.5.0';schema['required'].remove('content')
# Each scene-0.3 replacement needs an explicit immutable resource selection.
schema['allOf']=[{'if':{'properties':{'operations':{'contains':{'properties':{'op':{'const':'scene.replace'},'scene':{'properties':{'schema_version':{'const':'0.3.0'}},'required':['schema_version']}},'required':['op','scene']}}}},'then':{'required':['content']}}]
write(r/'spec/contracts/command-v0.5.schema.json',schema)
# Literal versioned examples are independent of implementation output.
valid=json.loads((r/'spec/fixtures/valid/command-content-scene.json').read_bytes());valid['schema_version']='0.5.0'
write(r/'spec/fixtures/valid/command-large-scene.json',valid)
invalid=copy.deepcopy(valid);invalid.pop('content');write(r/'spec/fixtures/invalid/command-large-no-content.json',invalid)
catalog=json.loads((r/'spec/fixtures/catalog.json').read_bytes())
for p,expected in [('valid/command-large-scene.json','valid'),('invalid/command-large-no-content.json','invalid')]:
    catalog['fixtures'].append({'path':'fixtures/'+p,'schema':'command-v0.5','expected':expected,'semantic':True,'reason':'' if expected=='valid' else 'Scene 0.3 replacement requires resource pins.'})
write(r/'spec/fixtures/catalog.json',catalog)
paths=['spec/delivery/packages/w-08-large-commands.md','tests/configuration/large-command-cases.json','spec/contracts/command-v0.5.schema.json','spec/fixtures/valid/command-large-scene.json','spec/fixtures/invalid/command-large-no-content.json']
out=r/'out/campaign/w-08-large-commands';out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(r/p,p)
write(out/'fixed-inputs.json',{'prepared_at':datetime.now(timezone.utc).isoformat(),'source_base':'c7c2f32489caec1c1cba143ec3c48cef707a86e5','inputs':{p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in paths},'archive_sha256':hashlib.sha256((out/'fixed-inputs.zip').read_bytes()).hexdigest(),'scene_canonical_sha256':hashlib.sha256(encoded(scene)).hexdigest(),'moved_canonical_sha256':hashlib.sha256(encoded(moved)).hexdigest()})
print('Frozen scenes, limits, schema and negative resource-selection example before implementation.')

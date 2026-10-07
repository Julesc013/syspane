from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign/w-10-visibility-admission';out.mkdir(exist_ok=True)
def read(n):return json.loads((r/n).read_bytes())
def write(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
scene=read('spec/contracts/scene-v0.4.schema.json');scene['$id']=scene['$id'].replace('/0.4.0/','/0.5.0/');scene['title']='SysPane authored visibility scene 0.5.0';scene['properties']['schema_version']['const']='0.5.0'
widget=scene['$defs']['widget'] if 'widget' in scene['$defs'] else scene['properties']['widgets']['items']
widget['properties']['visibility']={'$ref':'https://schemas.example.invalid/syspane/0.1.0/visibility.schema.json'}
write('spec/contracts/scene-v0.5.schema.json',scene)
command=read('spec/contracts/command-v0.6.schema.json');command['$id']=command['$id'].replace('/0.6.0/','/0.7.0/');command['title']='SysPane authored visibility command 0.7.0';command['properties']['schema_version']['const']='0.7.0'
op=next(x for x in command['properties']['operations']['items']['oneOf'] if x['properties']['op']['const']=='scene.replace');op['properties']['scene']['oneOf'].append({'$ref':scene['$id']})
command['allOf'][0]['if']['properties']['operations']['contains']['properties']['scene']['properties']['schema_version']['enum'].append('0.5.0')
write('spec/contracts/command-v0.7.schema.json',command)
base=read('tests/editor/native-cases.json')['authored'];rule=read('spec/fixtures/valid/visibility-counter.json')
conditional=copy.deepcopy(base['scene']);conditional['schema_version']='0.5.0';conditional['widgets'][0]['visibility']=rule
cleared=copy.deepcopy(conditional);del cleared['widgets'][0]['visibility']
locked=copy.deepcopy(conditional);locked['widgets'][0]['edit_locked']=True
multi=copy.deepcopy(conditional);multi['widgets'][1]['visibility']=rule
grouped=read('tests/editor/edit-lock-cases.json')['grouped'];grouped['schema_version']='0.5.0';grouped['widgets'][3].pop('edit_locked');grouped['widgets'][3]['visibility']=rule
cases={'authored':base,'rule':rule,'conditional':conditional,'cleared':cleared,'locked':locked,'multi':multi,'grouped':grouped,'faults':{'request':40,'selector_ready':40,'selected':41,'durable':41}}
write('tests/editor/visibility-admission-cases.json',cases)
q={'schema_version':'0.7.0','request_id':'visibility','expected_revision':'40','policy_generation':'7','intent':'commit','content':read('tests/configuration/settings-content-fixture.json')['selection'],'operations':[{'op':'scene.replace','scene':conditional}]}
fixtures=[('valid/scene-visibility','scene-v0.5',conditional),('valid/command-visibility','command-v0.7',q)]
for name,value in [('null',None),('collection',read('spec/fixtures/invalid/visibility-collection.json')),('coercion',read('spec/fixtures/invalid/visibility-coercion.json'))]:
 bad=copy.deepcopy(conditional);bad['widgets'][0]['visibility']=value;fixtures.append(('invalid/scene-visibility-'+name,'scene-v0.5',bad))
bad=copy.deepcopy(conditional);bad['schema_version']='0.4.0';fixtures.append(('invalid/scene-old-visibility','scene-v0.4',bad))
bad=copy.deepcopy(q);bad['schema_version']='0.6.0';fixtures.append(('invalid/command-old-visibility','command-v0.6',bad))
bad=copy.deepcopy(q);bad.pop('content');fixtures.append(('invalid/command-visibility-no-content','command-v0.7',bad))
catalog=read('spec/fixtures/catalog.json')
for name,schema,value in fixtures:
 write('spec/fixtures/'+name+'.json',value);catalog['fixtures'].append({'path':'fixtures/'+name+'.json','schema':schema,'expected':name.split('/')[0],'semantic':name.startswith('valid/'),'reason':'Versioned visibility authoring and admission boundary.'})
write('spec/fixtures/catalog.json',catalog)
paths=['spec/delivery/packages/w-10-visibility-admission.md','spec/contracts/scene-v0.5.schema.json','spec/contracts/command-v0.7.schema.json','tests/editor/visibility-admission-cases.json']+['spec/fixtures/'+n+'.json' for n,_,_ in fixtures]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(out/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
write('out/campaign/w-10-visibility-admission/fixed-inputs.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'inputs':{n:sha(r/n) for n in paths},'archive_sha256':sha(out/'fixed-inputs.zip')})
print('Frozen visibility admission package, schemas and exact expected scenes.')

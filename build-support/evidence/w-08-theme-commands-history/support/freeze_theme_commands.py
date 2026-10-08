from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,jsonschema,subprocess
from referencing import Registry,Resource
r=Path.cwd();now=datetime.now(timezone.utc).isoformat();sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'spec/delivery/packages/w-08-theme-commands.md';p.write_text(p.read_text().replace('FREEZE_TIMESTAMP',now),encoding='utf-8',newline='\n')
schema=json.loads((r/'spec/contracts/command-v0.7.schema.json').read_bytes());schema['$id']='https://schemas.example.invalid/syspane/0.8.0/command.schema.json';schema['title']='SysPane authored theme command 0.8.0';schema['properties']['schema_version']['const']='0.8.0'
pin=copy.deepcopy(schema['properties']['content']['properties']['package']);schema['properties']['content']={'$ref':'https://schemas.example.invalid/syspane/0.2.0/resource-selection.schema.json'}
font={'$ref':'https://schemas.example.invalid/syspane/0.2.0/theme.schema.json#/$defs/font'}
roles={'type':'object','maxProperties':4,'properties':{k:font for k in ('body','label','value','diagnostic')},'additionalProperties':False}
edit={'type':'object','properties':{'source':pin,'font':font,'font_roles':{'oneOf':[{'type':'null'},roles]}},'required':['source','font','font_roles'],'additionalProperties':False}
schema['properties']['theme_edit']={'oneOf':[{'type':'null'},edit]};schema['required']+=['content','theme_edit'];schema.pop('allOf')
write(r/'spec/contracts/command-v0.8.schema.json',schema)
f=json.loads((r/'tests/configuration/settings-content-fixture.json').read_bytes());fonts=json.loads((r/'tests/editor/theme-authoring-cases.json').read_bytes());overrides=json.loads((r/'tests/configuration/theme-override-cases.json').read_bytes())
candidate=copy.deepcopy(f['authored']);candidate['scene']['theme_id']=fonts['expected']['theme']['theme_id']
q=dict(schema_version='0.8.0',request_id='theme:edit',expected_revision='40',policy_generation='7',intent='commit',content=overrides['selection'],theme_edit=dict(source=f['themes']['theme:native'],font=fonts['candidate']['font'],font_roles=fonts['candidate']['font_roles']),operations=[dict(op='scene.replace',scene=candidate['scene'])])
keep=copy.deepcopy(q);keep.update(request_id='theme:keep',expected_revision='41',theme_edit=None,operations=[dict(op='settings.set',path='display.reduced_motion',value=True)])
reset=copy.deepcopy(q);reset.update(request_id='theme:reset',expected_revision='42',theme_edit=None,content=overrides['reset']);reset['operations'][0]['scene']=copy.deepcopy(f['authored']['scene']);reset['operations'][0]['scene']['revision']='42'
cases=dict(command=q,keep=keep,reset=reset,expected=candidate,artifact=fonts['expected'],selection=overrides['selection'],base_selection=overrides['reset'],base_manifests=overrides['base_manifests'],selected_manifests=overrides['selected_manifests'],faults={k:40 for k in ('created','request','resource_manifest:0','resource_asset:0','resource_index','resources_flushed','manifest','selector_ready')},features=['configuration.transactions','configuration.content','configuration.scene-content','configuration.large-commands','configuration.edit-locks','configuration.visibility','configuration.theme-overrides'])
cases['faults'].update(selected=41,durable=41)
write(r/'tests/configuration/theme-command-cases.json',cases)
fixtures={'valid/command-theme':q,'valid/command-theme-reset':reset}
for name,mutate in [('missing',lambda v:v.pop('theme_edit')),('source',lambda v:v['theme_edit']['source'].update(sha256='A'*64)),('color',lambda v:v['theme_edit'].update(tokens={})),('roles',lambda v:v['theme_edit']['font_roles'].update(unknown=v['theme_edit']['font'])),('selection',lambda v:v.update(content=f['selection']))]:
 v=copy.deepcopy(q);mutate(v);fixtures['invalid/command-theme-'+name]=v
schemas={v['$id']:v for p in (r/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_bytes())]}
registry=Registry().with_resources([(key,Resource.from_contents(value)) for key,value in schemas.items()])
validator=jsonschema.Draft202012Validator(schema,registry=registry)
catalog=json.loads((r/'spec/fixtures/catalog.json').read_bytes())
for name,v in fixtures.items():
 expected='valid' if name.startswith('valid/') else 'invalid';assert validator.is_valid(v)==(expected=='valid'),name
 path='fixtures/'+name+'.json';write(r/'spec'/path,v);catalog['fixtures'].append(dict(path=path,schema='command-v0.8',expected=expected,semantic=False,reason='' if expected=='valid' else 'Exact authored theme command fields and pins required.'))
write(r/'spec/fixtures/catalog.json',catalog)
names=['spec/delivery/packages/w-08-theme-commands.md','spec/contracts/command-v0.8.schema.json','tests/configuration/theme-command-cases.json','tests/configuration/theme-override-cases.json','tests/editor/theme-authoring-cases.json','tests/configuration/settings-content-fixture.json']+['spec/fixtures/'+n+'.json' for n in fixtures]
write(r/'out/campaign/w-08-theme-commands/fixed-inputs.json',dict(source_base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),at=now,independent_schema_validation='pass',derivation='Literal command/revision/interrupt outcomes built from prior independently frozen authored artifact and original preset bytes. Python JSON-schema validates structural fixtures before production changes.',inputs={n:sha((r/n).read_bytes()) for n in names}))
print('Frozen theme command contract, seven schema fixtures and literal outcomes.')

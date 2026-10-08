from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,jsonschema,subprocess
r=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
pin=copy.deepcopy(json.loads((r/'spec/contracts/command-v0.7.schema.json').read_bytes())['properties']['content']['properties']['package'])
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://schemas.example.invalid/syspane/0.2.0/resource-selection.schema.json','title':'SysPane theme resource selection 0.2','type':'object','properties':{'schema_version':{'const':'0.2.0'},'package':pin,'preset':pin,'theme_override':{'oneOf':[{'type':'null'},{'type':'object','properties':{'package':pin,'theme':pin},'required':['package','theme'],'additionalProperties':False}]}},'required':['schema_version','package','preset','theme_override'],'additionalProperties':False}
write(r/'spec/contracts/resource-selection-v0.2.schema.json',schema)
f=json.loads((r/'tests/configuration/settings-content-fixture.json').read_bytes());art=json.loads((r/'tests/editor/theme-authoring-cases.json').read_bytes())['expected']
selection=dict(schema_version='0.2.0',**f['selection'],theme_override=dict(package=art['package_pin'],theme=art['theme_pin']))
reset=dict(schema_version='0.2.0',**f['selection'],theme_override=None)
packages={sha(p['manifest'].encode()):p for p in f['packages']};base=set()
def visit(h):
 if h in base:return
 base.add(h)
 for dep in json.loads(packages[h]['manifest'])['dependencies']:visit(dep['sha256'])
visit(selection['package']['sha256'])
cases=dict(selection=selection,reset=reset,expected_theme=art['theme'],base_manifests=sorted(base),selected_manifests=sorted(base|{art['package_pin']['sha256']}),base_asset_sha256={sha(bytes.fromhex(h)):len(bytes.fromhex(h)) for k in base for h in packages[k]['assets_hex'].values()},image_refs=[w['content']['asset'] for w in f['authored']['scene']['widgets'] if w['kind']=='image'],replacements=70,capacity={'base_63_plus_override':64,'base_64_plus_override':'content.capacity','base_depth':8,'assets':1024,'asset_bytes':67108864})
write(r/'tests/configuration/theme-override-cases.json',cases)
fixtures={'valid/resource-selection-theme':selection,'valid/resource-selection-reset':reset}
bad=copy.deepcopy(selection);del bad['theme_override'];fixtures['invalid/resource-selection-missing']=bad
bad=copy.deepcopy(selection);bad['theme_override']['theme']['sha256']='A'*64;fixtures['invalid/resource-selection-digest']=bad
bad=copy.deepcopy(selection);bad['theme_override']=[bad['theme_override']];fixtures['invalid/resource-selection-many']=bad
bad=copy.deepcopy(selection);bad['schema_version']='0.1.0';fixtures['invalid/resource-selection-version']=bad
validator=jsonschema.Draft202012Validator(schema)
catalog=json.loads((r/'spec/fixtures/catalog.json').read_bytes())
for name,value in fixtures.items():
 expected='valid' if name.startswith('valid/') else 'invalid';assert validator.is_valid(value)==(expected=='valid')
 path='fixtures/'+name+'.json';write(r/'spec'/path,value);catalog['fixtures'].append(dict(path=path,schema='resource-selection-v0.2',expected=expected,semantic=False,reason='' if expected=='valid' else 'Exact versioned selection shape and pins required.'))
write(r/'spec/fixtures/catalog.json',catalog)
paths=['spec/delivery/packages/w-10-theme-overrides.md','spec/contracts/resource-selection-v0.2.schema.json','tests/configuration/theme-override-cases.json','tests/editor/theme-authoring-cases.json','tests/configuration/settings-content-fixture.json']+['spec/fixtures/'+n+'.json' for n in fixtures]
write(r/'out/campaign/w-10-theme-overrides/fixed-inputs.json',dict(source_base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),at=datetime.now(timezone.utc).isoformat(),independent_schema_validation='pass',derivation='Python traversal of exact pinned fixture manifests; existing independently frozen content/license artifact bytes; literal reset/replacement and capacity outcomes.',inputs={p:sha((r/p).read_bytes()) for p in paths}))
print('Frozen selection contract, six schema fixtures and exact closure expectations:',len(base),'base packages.')

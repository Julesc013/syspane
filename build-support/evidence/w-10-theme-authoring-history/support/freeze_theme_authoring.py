from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,jsonschema,subprocess
r=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest();raw=lambda j:json.dumps(j,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n'
f=json.loads((r/'tests/configuration/settings-content-fixture.json').read_bytes())
source=next(json.loads(bytes.fromhex(p['assets_hex']['theme.json'])) for p in f['packages'] if 'theme.json' in p['assets_hex'] and json.loads(bytes.fromhex(p['assets_hex']['theme.json']))['theme_id']=='theme:native')
font=lambda n,w=400,s='normal':dict(family='Noto Sans',size_dip=n,weight=w,style=s)
candidate=copy.deepcopy(source);candidate['schema_version']='0.2.0';candidate['font']=font(17.25,500);candidate['font_roles']={role:font(n,w,s) for role,n,w,s in [('body',19.5,400,'normal'),('label',14.5,700,'normal'),('value',32.5,800,'oblique'),('diagnostic',16.5,600,'italic')]}
seed=copy.deepcopy(candidate);seed.pop('theme_id');h=sha(('SysPane authored theme 1\n'+raw(seed)).encode());theme=copy.deepcopy(candidate);theme['theme_id']='theme:authored:'+h;asset=raw(theme)
manifest=dict(schema_version='0.1.0',package_id='package:authored-theme:'+h,version='0.1.0',kind='theme',license='MIT',dependencies=[],assets=[dict(path='theme.json',media_type='application/json',sha256=sha(asset.encode()),bytes=len(asset.encode()))],total_unpacked_bytes=len(asset.encode()),required_capabilities=['theme.typography'],optional_capabilities=[])
text=raw(manifest);expected=dict(theme=theme,asset=asset,manifest=text,package_pin=dict(id=manifest['package_id'],version='0.1.0',sha256=sha(text.encode())),theme_pin=dict(id=theme['theme_id'],version='0.1.0',sha256=sha(asset.encode())))
cases=dict(source=source,candidate=candidate,expected=expected,invalid_size=['',' 12','12 ','8.99','72.01','NaN','1e9999','1,5','12\n'],invalid_weight=['0','99','101','1000','0400','400.0','4e2','+400','400 '],invalid_style=['Normal','bold','',None],invalid_family=['',' Noto Sans','Noto Sans ','A,B','A\nB','A\u0085B'])
p=r/'tests/editor/theme-authoring-cases.json';p.write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for v in (candidate,theme):jsonschema.Draft202012Validator(json.loads((r/'spec/contracts/theme-v0.2.schema.json').read_bytes())).validate(v)
jsonschema.Draft202012Validator(json.loads((r/'spec/contracts/content-package.schema.json').read_bytes())).validate(manifest)
d=r/'out/campaign/w-10-theme-authoring';d.mkdir(exist_ok=True)
files=['spec/delivery/packages/w-10-theme-authoring.md','tests/editor/theme-authoring-cases.json']
(d/'fixed-inputs.json').write_text(json.dumps(dict(source_base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),at=datetime.now(timezone.utc).isoformat(),independent_schema_validation='pass',derivation='Python sorted compact UTF-8 JSON plus LF and hashlib SHA-256; fixed fractional numbers are exactly representable.',inputs={n:sha((r/n).read_bytes()) for n in files}),indent=2)+'\n',encoding='utf-8',newline='\n')
print('Independent authored-theme bytes and hashes frozen and schema-validated.')

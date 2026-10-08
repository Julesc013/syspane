from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,jsonschema
r=Path.cwd();d=r/'out/campaign/w-10-theme-authoring';p=r/'spec/delivery/packages/w-10-theme-authoring.md';f=r/'tests/editor/theme-authoring-cases.json'
assert not (d/'fixed-inputs-v2.json').exists()
for target in (p,f):(d/('original-'+target.name)).write_bytes(target.read_bytes())
s=p.read_text();s=s.replace('For a changed proposal, copy it and remove theme_id. Canonical bytes for this\nidentity seed are', 'For a changed proposal, copy it and remove theme_id. The identity seed is the object\n{license: the exact selected source package license, theme: that copy}. Canonical\nbytes for this seed are');s=s.replace('Different\nother authored data, including extensions, remains part of identity.','Different\nlicense metadata and other authored data, including extensions, remain part of identity.')
p.write_text(s,encoding='utf-8',newline='\n')
sha=lambda b:hashlib.sha256(b).hexdigest();raw=lambda j:json.dumps(j,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n'
v=json.loads(f.read_bytes());candidate=v['candidate']
def expected(license):
 seed=copy.deepcopy(candidate);seed.pop('theme_id');h=sha(('SysPane authored theme 1\n'+raw(dict(license=license,theme=seed))).encode());theme=copy.deepcopy(candidate);theme['theme_id']='theme:authored:'+h;asset=raw(theme)
 m=dict(schema_version='0.1.0',package_id='package:authored-theme:'+h,version='0.1.0',kind='theme',license=license,dependencies=[],assets=[dict(path='theme.json',media_type='application/json',sha256=sha(asset.encode()),bytes=len(asset.encode()))],total_unpacked_bytes=len(asset.encode()),required_capabilities=['theme.typography'],optional_capabilities=[]);manifest=raw(m)
 jsonschema.Draft202012Validator(json.loads((r/'spec/contracts/theme-v0.2.schema.json').read_bytes())).validate(theme);jsonschema.Draft202012Validator(json.loads((r/'spec/contracts/content-package.schema.json').read_bytes())).validate(m)
 return dict(theme=theme,asset=asset,manifest=manifest,package_pin=dict(id=m['package_id'],version='0.1.0',sha256=sha(manifest.encode())),theme_pin=dict(id=theme['theme_id'],version='0.1.0',sha256=sha(asset.encode())))
v['expected']=expected('MIT');v['expected_license']=expected('BSD-2-Clause');assert v['expected']['package_pin']['id']!=v['expected_license']['package_pin']['id'];f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
old=json.loads((d/'fixed-inputs.json').read_bytes());old['at']=datetime.now(timezone.utc).isoformat();old['inputs']={n:sha((r/n).read_bytes()) for n in old['inputs']};old['revision_reason']='Review identified different preserved licenses producing different manifests under the same package ID/version with the original theme-only seed. The revised canonical seed binds both license and theme. Independently derived MIT and BSD-2-Clause identities differ; both preserve license metadata and validate. Original contract/examples and earlier passing executions remain, without treating them as proof of the stronger requirement.';(d/'fixed-inputs-v2.json').write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Revised license-bound identity contract and two independent artifacts frozen before implementation change.')

from pathlib import Path
import copy,hashlib,json
r=Path.cwd();out=r/'out/campaign/w-10-theme-controls'
old=json.loads((out/'original-theme-controls-cases.json').read_bytes());new=json.loads((r/'tests/editor/theme-controls-cases.json').read_bytes());fixed=json.loads((out/'fixed-inputs.json').read_bytes());corrected=json.loads((out/'fixed-inputs-corrected.json').read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(out/'original-theme-controls-cases.json')==fixed['inputs']['tests/editor/theme-controls-cases.json']
for n,h in corrected['inputs'].items():assert sha(r/n)==h,n
for key in old:
 if key not in ('artifacts','scenes','selections'):assert old[key]==new[key],key
source=json.loads((r/'tests/editor/theme-authoring-cases.json').read_bytes());license_value=json.loads(source['expected']['manifest'])['license'];assert license_value=='MIT'
enc=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n'
hash_text=lambda s:hashlib.sha256(s.encode()).hexdigest()
for key,artifact in new['artifacts'].items():
 before=copy.deepcopy(old['artifacts'][key]['theme']);before['theme_id']=artifact['theme']['theme_id'];assert before==artifact['theme']
 theme=copy.deepcopy(artifact['theme']);theme.pop('theme_id');identity=hash_text('SysPane authored theme 1\n'+enc(dict(license=license_value,theme=theme)))
 assert artifact['theme']['theme_id']=='theme:authored:'+identity
 manifest=json.loads(artifact['manifest']);assert manifest['license']==license_value and artifact['asset']==enc(artifact['theme']) and artifact['manifest']==enc(manifest)
 assert manifest['assets'][0]['sha256']==hash_text(artifact['asset'])==artifact['theme_pin']['sha256'] and hash_text(artifact['manifest'])==artifact['package_pin']['sha256']
 scene=copy.deepcopy(old['scenes'][key]);scene['theme_id']=artifact['theme']['theme_id'];assert scene==new['scenes'][key]
 selection=copy.deepcopy(old['selections'][key]);selection['theme_override']=dict(package=artifact['package_pin'],theme=artifact['theme_pin']);assert selection==new['selections'][key]
print('Oracle correction audited: original freeze preserved; only license-derived artifact identities changed; fixed behavior/font examples unchanged.')

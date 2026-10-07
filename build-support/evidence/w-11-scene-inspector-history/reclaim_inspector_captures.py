from pathlib import Path
import hashlib,json,os,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence');e=r/'build-support/evidence';prefix='w-11-scene-inspector-'
assert os.geteuid()!=0 and b.resolve()==b
rows=json.loads((e/(prefix+'native-index.json')).read_text());removed=[]
for item in rows:
 if not (item['family'].endswith('-ERASURE') or item['family']=='IMAGE-DECODE'):continue
 zp=r/item['archive']['path'];assert hashlib.sha256(zp.read_bytes()).hexdigest()==item['archive']['sha256']
 folder=b/zp.stem;assert folder.resolve()==folder and folder.parent==b and (folder.name.startswith('surface-') or folder.name.startswith('image-'))
 assert hashlib.sha256((folder/'result.json').read_bytes()).hexdigest()==item['record_sha256']
 with zipfile.ZipFile(zp) as z:
  for name,digest in item['files'].items():
   if not name.endswith(('.rgb','.reply')):continue
   p=folder/name;assert not p.is_symlink() and p.resolve().is_relative_to(folder)
   if not p.exists():continue
   raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest and z.read(name)==raw
   removed.append({'path':str(p),'bytes':len(raw),'sha256':digest,'archive':item['archive'],'member':name});p.unlink()
rp=e/(prefix+'reclaimed.json');prior=json.loads(rp.read_text()) if rp.exists() else []
rp.write_text(json.dumps(prior+removed,indent=2)+'\n',encoding='utf-8');print('Released',sum(x['bytes'] for x in removed),'redundant raw bytes; all preserved and verified in native archives.')

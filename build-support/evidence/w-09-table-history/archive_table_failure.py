from pathlib import Path
import hashlib,json,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence').resolve()
p=(base/'surface-8dc9c747c071').resolve();assert p.parent==base and p.name=='surface-8dc9c747c071'
report=json.loads((p/'result.json').read_text());assert report['family']=='TABLE-ERASURE' and report['outcome']=='fail'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
e=r/'build-support/evidence/w-09-table-native';e.mkdir(exist_ok=True)
record=e/(p.name+'.json');record.write_bytes((p/'result.json').read_bytes());zp=e/(p.name+'.zip')
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for n,h in report['files'].items():
  file=(p/n).resolve();assert file.is_relative_to(p) and 'xauthority' not in n and sha(file)==h
  z.write(file,n)
 z.write(p/'result.json','result.json')
with zipfile.ZipFile(zp) as z:
 assert set(z.namelist())==set(report['files'])|{'result.json'}
 for n,h in report['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 removed={}
 for n,h in report['files'].items():
  file=(p/n).resolve()
  if file.suffix=='.rgb':
   assert file.is_relative_to(p) and file.is_file() and sha(file)==h
   removed[n]={'sha256':h,'bytes':file.stat().st_size};file.unlink()
v={'reason':'Release redundant raw failed-window captures after verifying their exact retained archive; keep original failure and all bytes recoverable.',
   'source_directory':str(p),'archive':{'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},'released_bytes':sum(x['bytes'] for x in removed.values()),'files':removed}
(r/'build-support/evidence/w-09-table-archive-reclamation.json').write_text(json.dumps(v,indent=2)+'\n')
print('Archived original failed capture; released',v['released_bytes'],'redundant native-cache bytes.')

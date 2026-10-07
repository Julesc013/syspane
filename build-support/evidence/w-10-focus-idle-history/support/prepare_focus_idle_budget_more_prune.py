from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();entries=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for prefix in ('w-10-widget-creation','w-10-native-editor'):
 index='build-support/evidence/'+prefix+'-attempts.json';raw=subprocess.check_output(['git','show','HEAD:'+index]);assert raw==(r/index).read_bytes()
 for row in json.loads(raw)['attempts']:
  saved=r/row['path'];folder=r/'out/campaign'/prefix/saved.parent.name
  if not folder.exists():continue
  assert folder.resolve().parent==r/'out/campaign'/prefix and not folder.is_symlink()
  files={}
  for p in folder.iterdir():
   assert p.is_file() and not p.is_symlink();rel=(saved.parent/p.name).relative_to(r).as_posix()
   assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel]);files[p.name]=sha(p.read_bytes())
  entries.append(dict(path=str(folder.resolve()),files=files,bytes=sum(p.stat().st_size for p in folder.iterdir())))
plan=r/'out/campaign/focus-idle-budget-more-prune-plan.json';assert not plan.exists();plan.write_text(json.dumps(dict(source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),entries=entries),indent=2)+'\n',encoding='utf-8',newline='\n')
print('Verified committed duplicates:',len(entries),'folders,',sum(x['bytes'] for x in entries),'bytes')

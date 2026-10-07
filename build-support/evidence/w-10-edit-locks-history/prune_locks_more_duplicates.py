from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and base.resolve()==base
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda path:subprocess.check_output(['git','-c','safe.directory='+str(r),'show','HEAD:'+path],cwd=r)
rows=[];seen=set()
for prefix in ('w-10-layout-authoring','w-10-native-observation','w-10-widget-creation','w-10-binding-authoring'):
 index='build-support/evidence/'+prefix+'-native-index.json';data=git(index);assert data==(r/index).read_bytes()
 for entry in json.loads(data):
  archive=entry['archive'];zp=r/archive['path'];assert sha(git(archive['path']))==sha(zp.read_bytes())==archive['sha256']
  folder=base/zp.stem
  if folder in seen or not folder.exists():continue
  seen.add(folder);assert folder.resolve().parent==base and not folder.is_symlink()
  files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if (p.is_file() or p.is_symlink()) and p.name!='xauthority'}
  if set(files)!=set(entry['files'])|set(entry.get('links',{})):continue
  with zipfile.ZipFile(zp) as z:
   for n,h in entry['files'].items():assert sha(files[n].read_bytes())==sha(z.read(n))==h
   for n,target in entry.get('links',{}).items():assert files[n].is_symlink() and os.readlink(files[n])==z.read(n).decode()==target
  rows.append(dict(path=str(folder),archive=archive,files=len(files),bytes=sum(p.lstat().st_size for p in files.values())))
assert rows
record=r/'out/campaign/locks-more-pruned-duplicates.json';assert not record.exists()
record.write_text(json.dumps(dict(source=subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),verified=rows),indent=2)+'\n')
for row in rows:
 p=Path(row['path']);assert p.resolve().parent==base and not p.is_symlink();shutil.rmtree(p)
print(json.dumps(dict(removed=len(rows),bytes=sum(row['bytes'] for row in rows),record=str(record))))

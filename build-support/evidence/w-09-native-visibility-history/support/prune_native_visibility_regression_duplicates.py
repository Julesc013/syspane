from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and base.resolve()==base
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda path:subprocess.check_output(['git','-c','safe.directory='+str(r),'show','HEAD:'+path],cwd=r)
candidates={}
for index in sorted((r/'build-support/evidence').glob('*-native-index.json')):
 if index.name.startswith('w-09-native-visibility-'):continue
 data=index.read_bytes();entries=json.loads(data)
 if not isinstance(entries,list):continue
 for entry in entries:
  if not isinstance(entry,dict) or 'archive' not in entry:continue
  folder=base/Path(entry['archive']['path']).stem
  if not folder.exists() or folder in candidates:continue
  assert folder.resolve().parent==base and not folder.is_symlink()
  files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if (p.is_file() or p.is_symlink()) and p.name!='xauthority'}
  if set(files)!=set(entry['files'])|set(entry.get('links',{})):continue
  candidates[folder]=(index,entry,files,sum(p.lstat().st_size for p in files.values()))
rows=[]
for folder,(index,entry,files,size) in sorted(candidates.items(),key=lambda q:-q[1][3]):
 assert git(index.relative_to(r).as_posix())==index.read_bytes()
 archive=entry['archive'];zp=r/archive['path']
 assert sha(git(archive['path']))==sha(zp.read_bytes())==archive['sha256']
 with zipfile.ZipFile(zp) as z:
  for n,h in entry['files'].items():assert sha(files[n].read_bytes())==sha(z.read(n))==h
  for n,target in entry.get('links',{}).items():assert files[n].is_symlink() and os.readlink(files[n])==z.read(n).decode()==target
 rows.append(dict(path=str(folder),archive=archive,files=len(files),bytes=size))
 if sum(x['bytes'] for x in rows)>=512*1024*1024:break
assert rows
record=r/'out/campaign/native-visibility-regression-pruned-duplicates.json';assert not record.exists()
record.write_text(json.dumps(dict(source=subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),verified=rows),indent=2)+'\n',encoding='utf-8')
for row in rows:
 p=Path(row['path']);assert p.resolve().parent==base and not p.is_symlink();shutil.rmtree(p)
print(json.dumps(dict(removed=len(rows),bytes=sum(row['bytes'] for row in rows),record=str(record))))

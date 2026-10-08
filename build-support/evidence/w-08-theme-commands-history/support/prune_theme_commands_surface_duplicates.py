from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and base.resolve()==base
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git','-c','safe.directory='+str(r),*args],cwd=r)
rows=[]
for name in ('surface-617d92a9104b','surface-eb50e27fc2e7','surface-63db8cacf945','surface-ce126e07c73c','surface-dca86458af42','surface-12d205270c01'):
 folder=base/name;archive='build-support/evidence/w-09-surface-native/'+name+'.zip';zp=r/archive
 assert folder.resolve().parent==base and not folder.is_symlink()
 assert git('show','HEAD:'+archive)==zp.read_bytes()
 files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
 entries={}
 with zipfile.ZipFile(zp) as z:
  assert set(files)-{'xauthority'}==set(z.namelist())
  for n in z.namelist():
   assert not files[n].is_symlink() and files[n].read_bytes()==z.read(n)
   entries[n]=sha(files[n].read_bytes())
 rows.append(dict(path=str(folder),archive=archive,archive_sha256=sha(zp.read_bytes()),files=entries,bytes=sum(p.lstat().st_size for p in files.values())))
record=r/'out/campaign/theme-commands-surface-pruned-duplicates.json';assert not record.exists()
record.write_text(json.dumps(dict(source=git('rev-parse','HEAD').decode().strip(),verified=rows),indent=2)+'\n')
for row in rows:
 p=Path(row['path']);assert p.resolve().parent==base and not p.is_symlink();shutil.rmtree(p)
print(json.dumps(dict(removed=len(rows),bytes=sum(x['bytes'] for x in rows))))

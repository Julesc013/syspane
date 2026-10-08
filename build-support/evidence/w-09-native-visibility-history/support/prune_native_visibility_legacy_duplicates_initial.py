from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and base.resolve()==base
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda path:subprocess.check_output(['git','-c','safe.directory='+str(r),'show','HEAD:'+path],cwd=r)
rows=[]
for zp in sorted((r/'build-support/evidence/w-09-table-native').glob('surface-*.zip')):
 folder=base/zp.stem
 if not folder.exists():continue
 assert folder.resolve().parent==base and not folder.is_symlink()
 archive=zp.relative_to(r).as_posix();assert git(archive)==zp.read_bytes()
 files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
 with zipfile.ZipFile(zp) as z:
  assert set(files)==set(z.namelist()),(zp.name,set(files)^set(z.namelist()))
  for n,p in files.items():assert not p.is_symlink() and p.read_bytes()==z.read(n),n
 rows.append(dict(path=str(folder),archive=dict(path=archive,sha256=sha(zp.read_bytes())),files=len(files),bytes=sum(p.stat().st_size for p in files.values())))
assert rows
record=r/'out/campaign/native-visibility-legacy-pruned-duplicates.json';assert not record.exists()
record.write_text(json.dumps(dict(source=subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),verified=rows),indent=2)+'\n',encoding='utf-8')
for row in rows:
 p=Path(row['path']);assert p.resolve().parent==base and not p.is_symlink();shutil.rmtree(p)
print(json.dumps(dict(removed=len(rows),bytes=sum(row['bytes'] for row in rows),record=str(record))))

from pathlib import Path
import hashlib,json,os,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');base=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');assert os.geteuid()!=0 and base.resolve()==base
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *args:subprocess.check_output(['git','-c','safe.directory='+str(r),*args],cwd=r)
archives={}
for n in git('ls-files','build-support/evidence/*-source-archives/*.zip').decode().splitlines():
 if Path(n).stem.startswith('GNOME-'):archives.setdefault(Path(n).stem,[]).append(n)
rows=[];seen=set();verified={}
for folder in sorted(base.glob('GNOME-*')):
 if not folder.is_dir() or folder.is_symlink() or folder.resolve().parent!=base:continue
 source=folder/'source-inputs.zip'
 if not source.is_file() or source.is_symlink():continue
 candidates=archives.get(folder.name,[]);data=source.read_bytes();digest=sha(data)
 target=next((n for n in candidates if sha((r/n).read_bytes())==digest),None)
 if not target:continue
 assert git('show','HEAD:'+target)==data
 verified[target]=digest
 rows.append(dict(path=str(source),archive=target,member=None,sha256=digest,bytes=len(data)))
 with zipfile.ZipFile(source) as z:
  members={sha(z.read(n)):n for n in z.namelist() if not n.endswith('/')}
  for part in ('data','schemas'):
   for p in (folder/part).rglob('*'):
    if not p.is_file() or p.is_symlink() or p.resolve()!=p or p in seen:continue
    data=p.read_bytes();h=sha(data)
    if h not in members:continue
    assert data==z.read(members[h]);seen.add(p);rows.append(dict(path=str(p),archive=target,member=members[h],sha256=h,bytes=len(data)))
record=r/'out/campaign/visibility-controls-gnome-source-pruned.json';assert rows and not record.exists()
result=dict(source=git('rev-parse','HEAD').decode().strip(),archives=verified,verified=rows,bytes=sum(x['bytes'] for x in rows),removed=0,scope='Only byte-identical source archives and copied source/schema files in completed owned GNOME laboratories; observations, journals, binaries and caches remain.')
def save():record.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
save()
for row in rows:
 p=Path(row['path']);assert p.is_relative_to(base) and p.resolve()==p and not p.is_symlink() and sha(p.read_bytes())==row['sha256'];p.unlink();result['removed']+=1
save();print(json.dumps(dict(removed=result['removed'],bytes=result['bytes'],archives=len(verified))))

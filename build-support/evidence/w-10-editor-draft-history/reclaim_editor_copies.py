from pathlib import Path
import hashlib,json,os,stat,subprocess,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and b.resolve()==b
git=['git','-c','safe.directory='+str(r),'-C',str(r)]
indices=subprocess.check_output([*git,'ls-files','build-support/evidence/*native-index.json'],text=True).splitlines()
removed=[];total=0;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for index in indices:
 if total>=80*1024*1024:break
 rows=json.loads(subprocess.check_output([*git,'show','HEAD:'+index]))
 if not isinstance(rows,list):continue
 for row in rows:
  if total>=80*1024*1024:break
  if 'archive' not in row or 'files' not in row:continue
  zp=r/row['archive']['path'];folder=b/zp.stem
  if not folder.exists() or folder.resolve()!=folder or folder.parent!=b:continue
  candidates=[]
  for n,digest in row['files'].items():
   if Path(n).is_absolute() or '..' in Path(n).parts:raise ValueError('unsafe archive member')
   p=folder/n
   if not p.exists() or p.is_symlink() or p.resolve()!=p or not p.is_file() or p.stat().st_size<1024*1024:continue
   if not p.resolve().is_relative_to(b):raise ValueError('outside native evidence root')
   candidates.append((n,p,digest))
  if not candidates:continue
  committed=subprocess.check_output([*git,'rev-parse','HEAD:'+row['archive']['path']],text=True).strip()
  assert subprocess.check_output([*git,'hash-object','--no-filters',str(zp)],text=True).strip()==committed
  assert sha(zp)==row['archive']['sha256']
  with zipfile.ZipFile(zp) as z:
   for n,p,digest in candidates:
    if total>=80*1024*1024:break
    data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=digest:continue
    assert z.read(n)==data
    removed.append(dict(path=str(p),bytes=len(data),sha256=digest,archive=row['archive'],member=n,index=index))
    p.unlink();total+=len(data)
path=r/'out/campaign/editor-native-reclamation.json'
assert not path.exists()
path.write_text(json.dumps(dict(source_base=subprocess.check_output([*git,'rev-parse','HEAD'],text=True).strip(),reason='Reclaim only byte-identical committed native evidence copies inside the resolved owned output root',reclaimed_bytes=total,copies=removed),indent=2)+'\n')
print('Reclaimed',total,'bytes in',len(removed),'verified committed duplicate files.')

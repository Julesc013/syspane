from pathlib import Path
import json,os
r=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');assert os.geteuid()!=0
groups={};files=[]
for base,dirs,names in os.walk(r):
 for n in names:
  p=Path(base)/n
  if p.is_symlink() or not p.is_file():continue
  s=p.stat();key=p.relative_to(r).parts[0];groups[key]=groups.get(key,0)+s.st_size
  if s.st_size>10000000:files.append(dict(path=p.relative_to(r).as_posix(),bytes=s.st_size,mtime=s.st_mtime))
print(json.dumps(dict(groups=sorted(groups.items(),key=lambda a:-a[1])[:20],files=sorted(files,key=lambda a:-a['mtime'])[:20]),indent=2))

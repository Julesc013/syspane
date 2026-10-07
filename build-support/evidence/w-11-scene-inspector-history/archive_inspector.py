from pathlib import Path
from datetime import datetime
import hashlib,json,os,stat,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and b.resolve()==b
prefix='w-11-scene-inspector-';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
attempts=[json.loads(p.read_text()) for p in (r/'out/campaign/w-11-scene-inspector').glob('*/result.json')]
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
d=e/(prefix+'native');d.mkdir(exist_ok=True)
records=[]
for p in sorted(b.glob('*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text())
 if p.parent.name.startswith('image-'):v['family']='IMAGE-DECODE'
 if v.get('family') not in ('SCENE-INSPECTOR','SCENE-CONTENT','SCENE-ERASURE','TABLE-ERASURE','CONTENT-ERASURE','CHART-ERASURE','IMAGE-ERASURE','CONTENT-COMMANDS','CONTENT-READER','RESOURCE-GENERATIONS','CONFIG-STORE','COMMAND-IPC','TRANSACTION-SUPERVISION','IMAGE-DECODE') or v.get('outcome')=='running':continue
 meta=d/(p.parent.name+'.index.json');zp=d/(p.parent.name+'.zip');rp=d/(p.parent.name+'.json')
 if meta.exists():
  item=json.loads(meta.read_text());assert sha(zp)==item['archive']['sha256'] and sha(p)==item['record_sha256'];records.append(item);continue
 files={};links={};modes={};names=sorted(v['files']) if 'files' in v else sorted(q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if q.is_file() or q.is_symlink())
 names=sorted(set(names)|{'result.json'})
 with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
  for n in names:
   assert not n.startswith('/') and '..' not in n.split('/') and 'xauthority' not in n
   q=p.parent/n;s=q.lstat();modes[n]=stat.S_IMODE(s.st_mode)
   if stat.S_ISLNK(s.st_mode):
    target=os.readlink(q);links[n]=target;info=zipfile.ZipInfo(n);info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,target)
   else:
    assert stat.S_ISREG(s.st_mode);files[n]=sha(q);z.write(q,n)
 changed={n:{'reported':h,'archived':files.get(n)} for n,h in v.get('files',{}).items() if files.get(n)!=h}
 if v['outcome']=='pass':assert not changed
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(files)|set(links)
  for n,h in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
  for n,target in links.items():assert z.read(n).decode()==target
 rp.write_bytes(p.read_bytes());item={'path':rp.relative_to(r).as_posix(),'sha256':sha(rp),'record_sha256':sha(p),'family':v['family'],'outcome':v['outcome'],
  'finished_mtime':p.stat().st_mtime,'archive':{'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},'files':files,'links':links,'modes':modes,'post_report_differences':changed}
 meta.write_text(json.dumps(item,indent=2)+'\n',encoding='utf-8');records.append(item)
flat=[p for p in b.iterdir() if p.is_file() and p.stat().st_mtime>=cutoff and (p.name.startswith('RECOVERY-01-') or p.name.startswith('failure-'))]
if flat:
 zp=d/'recovery-records.zip';files={}
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(flat):files[p.name]=sha(p);z.write(p,p.name)
 with zipfile.ZipFile(zp) as z:
  for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 records.append(dict(family='RECOVERY-01-records',archive=dict(path=zp.relative_to(r).as_posix(),sha256=sha(zp)),files=files))
(e/(prefix+'native-index.json')).write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('Archived and verified',len(records),'completed native records.')

from pathlib import Path
from datetime import datetime
import hashlib,json,os,stat,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence')
assert os.geteuid()!=0 and b.resolve()==b
prefix='w-09-visibility-composition-';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
attempts=[json.loads(p.read_text()) for p in (r/'out/campaign/w-09-visibility-composition').glob('*/result.json')]
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
d=e/(prefix+'native');d.mkdir(exist_ok=True)
records=[]
for p in sorted(b.glob('*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text())
 if p.parent.name.startswith('image-'):v['family']='IMAGE-DECODE'
 if v.get('family') not in ('VISIBILITY-ADMISSION','NATIVE-QUERY-DIAGNOSTIC','EDITOR-IDLE-DIAGNOSTIC','EDITOR-REFRESH','EDITOR-REFRESH-ANIMATION-DIAGNOSTIC','TEXT-RASTER','IMAGE-JOB','SCENE-SURFACE','SCENE-IMAGE','SCENE-CHART','SCENE-TABLE','SCENE-INSPECTOR-MODEL','EDITOR-LOCKS','EDITOR-CONTAINERS','EDITOR-LAYOUT','NATIVE-OBSERVATION','EDITOR-OBSERVATION','LARGE-COMMANDS-DIAGNOSTIC','EDITOR-WIDGET-CREATION','EDITOR-BINDING-AUTHORING','EDITOR-CONTENT-PROPERTIES','EDITOR-SNAP','EDITOR-GROUP','EDITOR-ARRANGE','LARGE-COMMANDS','EDITOR-FORM','SETTINGS-FORM','SCENE-INSPECTOR','SCENE-CONTENT','SCENE-ERASURE','TABLE-ERASURE','CONTENT-ERASURE','CHART-ERASURE','IMAGE-ERASURE','CONTENT-COMMANDS','CONTENT-READER','RESOURCE-GENERATIONS','CONFIG-STORE','COMMAND-IPC','TRANSACTION-SUPERVISION','IMAGE-DECODE') or v.get('outcome')=='running':continue
 meta=d/(p.parent.name+'.index.json');zp=d/(p.parent.name+'.zip');rp=d/(p.parent.name+'.json')
 if meta.exists():
  item=json.loads(meta.read_text());assert sha(zp)==item['archive']['sha256'] and sha(p)==item['record_sha256'];records.append(item);continue
 files={};links={};modes={};names=sorted(q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if (q.is_file() or q.is_symlink()) and q.name!='xauthority')
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
 if v['outcome'] in ('pass','observed'):assert not changed
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(files)|set(links)
  for n,h in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
  for n,target in links.items():assert z.read(n).decode()==target
 rp.write_bytes(p.read_bytes());item={'path':rp.relative_to(r).as_posix(),'sha256':sha(rp),'record_sha256':sha(p),'family':v['family'],'outcome':v['outcome'],
  'finished_mtime':p.stat().st_mtime,'archive':{'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},'files':files,'links':links,'modes':modes,'post_report_differences':changed}
 meta.write_text(json.dumps(item,indent=2)+'\n',encoding='utf-8');records.append(item)
for p in sorted(b.glob('EDITOR-EXIT-01-*.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());folder=p.with_suffix('');zp=d/(folder.name+'.zip');rp=d/p.name;meta=d/(folder.name+'.index.json')
 if meta.exists():
  item=json.loads(meta.read_text());assert sha(zp)==item['archive']['sha256'] and sha(p)==item['record_sha256'];records.append(item);continue
 files={};modes={}
 with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
  for q in sorted(folder.rglob('*')):
   if not q.is_file() or q.name=='xauthority':continue
   assert not q.is_symlink();n=q.relative_to(folder).as_posix();files[n]=sha(q);modes[n]=stat.S_IMODE(q.stat().st_mode);z.write(q,n)
  files['result.json']=sha(p);z.write(p,'result.json')
 with zipfile.ZipFile(zp) as z:
  for n,digest in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 rp.write_bytes(p.read_bytes());item={'path':rp.relative_to(r).as_posix(),'sha256':sha(rp),'record_sha256':sha(p),'family':'EDITOR-EXIT-01','outcome':v['result'],
  'finished_mtime':p.stat().st_mtime,'archive':{'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},'files':files,'links':{},'modes':modes,'post_report_differences':{}}
 meta.write_text(json.dumps(item,indent=2)+'\n',encoding='utf-8');records.append(item)
(e/(prefix+'native-index.json')).write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('Archived and verified',len(records),'completed native records.')

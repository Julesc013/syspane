from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-visibility-admission-';h=e/(prefix+'history');h.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='40f9e0fba3e223bb40d882bb199a3b4a6285f302'
attempts=[];out=r/'out/campaign'
for p in sorted((out/'w-10-visibility-admission').glob('*/result.json')):
 v=json.loads(p.read_bytes());assert v['source_base']==base;target=h/p.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
 assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
 if 'ctest_log_archive_sha256' in v:
  shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
 attempts.append(row)
def latest(profile,action):
 row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_bytes())
current=latest('linux-x64-gcc13','focus')[1]['source_inputs']
for n,digest in current.items():assert sha(r/n)==digest,n
final={};artifacts={}
for profile,count in [('linux-x64-gcc13',325),('windows-x64-gcc15',322),('windows-x86-v141-xp',319)]:
 final[profile]={}
 for action in ('build','test','portable')+(('locks','resources','focus') if profile.startswith('linux') else ()):
  row,v=latest(profile,action);assert not v['exit'] and not v['source_changed_during_execution'] and v['source_inputs']==current,(profile,action)
  cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))
  final[profile][action]=dict(record={k:row[k] for k in ('path','sha256')},cases=cases)
 command=['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/capture_lock_artifacts.py',profile] if profile.startswith('linux') else [str(r/'.venv/Scripts/python.exe'),'-X','utf8','out/campaign/capture_lock_artifacts.py',profile]
 artifacts[profile]=json.loads(subprocess.check_output(command,text=True))
 for action,row in final[profile].items():
  v=json.loads((r/row['record']['path']).read_bytes())
  if action!='build':assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
 assert len(final[profile]['test']['cases'])==59 and len(final[profile]['portable']['cases'])==count
assert len(final['linux-x64-gcc13']['focus']['cases'])==4 and len(final['linux-x64-gcc13']['resources']['cases'])==6
support={}
paths=[p for p in out.iterdir() if p.is_file() and ('visibility_admission' in p.name or 'visibility-admission' in p.name or p.name=='capture_lock_artifacts.py')]+list((out/'w-10-visibility-admission').glob('fixed-inputs.*'))
for p in paths:
 target=h/'support'/p.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);support[p.relative_to(r).as_posix()]=ref(target)
fixed=json.loads((out/'w-10-visibility-admission/fixed-inputs.json').read_bytes());archive=out/'w-10-visibility-admission/fixed-inputs.zip';assert sha(archive)==fixed['archive_sha256']
with zipfile.ZipFile(archive) as z:
 for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==sha(r/n)==digest
native=json.loads((e/(prefix+'native-index.json')).read_bytes());assert native
assert any(row['family']=='VISIBILITY-ADMISSION' and row['outcome']=='pass' for row in native)
for native_row in native:
 owners=[]
 for row in attempts:
  attempt=json.loads((r/row['path']).read_bytes())
  if datetime.fromisoformat(attempt['started_at']).timestamp()<=native_row['finished_mtime']<=datetime.fromisoformat(attempt['finished_at']).timestamp()+1:owners.append((row,attempt))
 assert len(owners)==1,(native_row['path'],len(owners))
 owner,attempt=owners[0];native_row['attempt']={k:owner[k] for k in ('path','sha256')};native_row['source_is_final']=attempt['source_inputs']==current
write(e/(prefix+'native-index.json'),native)
unchanged={}
for n in subprocess.check_output(['git','ls-files','spec/contracts/*.schema.json','spec/fixtures/*.json','spec/fixtures/**/*.json'],text=True).splitlines():
 if n=='spec/fixtures/catalog.json':continue
 data=subprocess.check_output(['git','show',base+':'+n]);assert data==(r/n).read_bytes(),n;unchanged[n]=sha(r/n)
old=json.loads(subprocess.check_output(['git','show',base+':spec/fixtures/catalog.json']));new=json.loads((r/'spec/fixtures/catalog.json').read_bytes());assert new['fixtures'][:len(old['fixtures'])]==old['fixtures']
write(e/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,final_runs=final,artifacts=artifacts,support=support,native_index=ref(e/(prefix+'native-index.json')),unchanged_old_contracts=unchanged,scope='Versioned authoring/durable admission and explicit renderer gate. Native conditional composition/controls and complete editions remain required. All failed attempts remain preserved.'))
print('Preserved',len(attempts),'attempts and',len(native),'native records; checked',len(unchanged),'unchanged old schema/fixture files.')

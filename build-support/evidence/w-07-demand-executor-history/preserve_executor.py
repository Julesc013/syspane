from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence'
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-07-demand-executor-';base='70df8f5419a7f06148460232c5d8cb3d2d432648'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'native_reports':[],
 'limitations':['Linux-only native executor; fixed wire source and typed policy, not installed controller or general demand selection.',
 'Full Linux run passed 124/125; only the new IPC observer failed. The corrected five-case family passes against the same binary. No single all-green full rerun is claimed.',
 'Original operational continuity records remain ignored; the public projection retains outcomes, counts and their original hashes.',
 'No other native platform, new GNOME desktop composition or complete release is qualified.']}
attempts=[]
for p in sorted((r/'out/campaign/w-07-demand-executor').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json')
 item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append((v,item))
 if v['profile']=='linux-x64-gcc13' and v['action']=='test':
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/125 Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==125 and [c['case'] for c in cases if c['outcome']=='fail']==['native.NATIVE-DEMAND-EXECUTOR']
  changed=[n for n,h in v['source_inputs'].items() if sha(r/n)!=h]
  assert changed==['tests/protocol/native_demand_executor.py'],changed
  record['full_linux_run']={'record':item,'cases':cases,'subsequent_changes':changed}
 if v['profile']=='linux-x64-gcc13' and v['action']=='oracle' and v['exit']==0:
  assert all(sha(r/n)==h for n,h in v['source_inputs'].items())
  record['corrected_native_run']=item;record['current_inputs']=v['source_inputs']
 if v['profile']=='windows-x64-gcc15' and v['action']=='focus':
  assert v['exit']==0 and '100% tests passed, 0 tests failed out of 11' in v['stdout'];record['windows_checks']=item
assert all(key in record for key in ('full_linux_run','corrected_native_run','windows_checks'))
for p in sorted((r/'out/campaign').glob('executor-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v,_ in attempts)
for pattern in ('NATIVE-COLLECTOR-*.json','NATIVE-DEMAND-EXECUTOR-*.json'):
 for p in sorted((b/'native-evidence').glob(pattern)):
  if '.private.' in p.name or p.stat().st_mtime<cutoff:continue
  v=json.loads(p.read_text());item=copy(p,e/(prefix+'native')/p.name)
  item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256'])
  record['native_reports'].append(item)
  if len(v['cases'])==5 and v.get('case')=='NATIVE-DEMAND-EXECUTOR' and v['outcome']=='pass':
   assert v['executable_sha256']==sha(b/'SysPane.CollectorProbe')
   assert v['oracle_sha256']==sha(r/'tests/protocol/native_demand_executor.py');record['final_native_report']=item
for p in sorted((b/'native-evidence').glob('consumer-continuity-*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());assert v['outcome']=='pass' and len(v['cases'])==5
 public={'family':v['family'],'outcome':v['outcome'],'artifact_sha256':v['artifact_sha256'],'private_original_sha256':sha(p),'cases':[]}
 for c in v['cases']:
  assert c['outcome']=='pass' and c['held_exits'] and all(c['cleanup_exits'].values())
  public['cases'].append({'case':c['case'],'outcome':c['outcome'],'held_exits':c['held_exits'],
   'source_samples':c['source_journal']['samples'],'consumer_journals':len(c['consumer_journals']),
   'independent_cleanup_exits':len(c['cleanup_exits'])})
 dest=e/(prefix+'native')/(p.parent.name+'.json');write(dest,public)
 record['native_reports'].append({'path':dest.relative_to(r).as_posix(),'sha256':sha(dest),'outcome':'pass','cases':5,'artifact_sha256':v['artifact_sha256']})
assert 'final_native_report' in record
record['artifacts']={n:{'sha256':sha(b/n),'bytes':(b/n).stat().st_size} for n in ('SysPane.CollectorProbe','libsyspane_demand.a')}
for n in ('executor_step.py','executor_flow.py','preserve_executor.py'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
write(e/(prefix+'attempts.json'),record)
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'public native reports; 124 full-run passes plus corrected native family verified.')

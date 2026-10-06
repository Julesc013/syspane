from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence'
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-07-session-demand-';base='e567a018d334506e42332dc7f44f9c911ac1d362'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'native_reports':[],
 'limitations':['Controller-selected immutable local requests; existing wire messages do not admit arbitrary consumer field selection.',
 'Historical-toolset tests execute on the modern Windows host only; no historical operating-system qualification.',
 'Raw operational continuity records remain ignored; public projections retain outcomes, counts and original private hashes.',
 'No installed controller/policy, new GNOME desktop composition, other native platform or complete release is qualified.']}
attempts=[]
for p in sorted((r/'out/campaign/w-07-session-demand').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json')
 item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append((v,item))
 if v['action']=='test':
  count={'linux-x64-gcc13':130,'windows-x64-gcc15':119,'windows-x86-v141-xp':108}[v['profile']]
  assert v['exit']==0 and f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases)
  assert all(sha(r/n)==h for n,h in v['source_inputs'].items())
  record['full_runs'][v['profile']]={'record':item,'cases':cases}
  if 'current_inputs' in record:assert record['current_inputs']==v['source_inputs']
  record['current_inputs']=v['source_inputs']
 if v['action']=='focus':
  assert v['exit']!=0 and 'out of 40' in v['stdout'] and 'native.NATIVE-COLLECTOR' in v['stdout']
  record['initial_failure']=item
assert len(record['full_runs'])==3 and 'initial_failure' in record
for p in sorted((r/'out/campaign').glob('session-demand-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v,_ in attempts)
for pattern in ('NATIVE-COLLECTOR-*.json','NATIVE-DEMAND-EXECUTOR-*.json'):
 for p in sorted((b/'native-evidence').glob(pattern)):
  if '.private.' in p.name or p.stat().st_mtime<cutoff:continue
  v=json.loads(p.read_text());item=copy(p,e/(prefix+'native')/p.name)
  item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256'])
  record['native_reports'].append(item)
  if v['outcome']=='pass' and v['executable_sha256']==sha(b/'SysPane.CollectorProbe'):
   record.setdefault('final_native_reports',[]).append(item)
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
assert sorted(c['cases'] for c in record['final_native_reports'])==[5,8]
record['artifacts']={}
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
for profile,root in roots.items():
 names=['syspane_demand_session_tests'+('' if profile.startswith('linux') else '.exe')]
 names+=['syspane_demand_sessions.lib'] if profile.endswith('xp') else ['libsyspane_demand_sessions.a']
 if profile.startswith('linux'):names+=['SysPane.CollectorProbe']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
record['historical_audit']=copy(r/'out/campaign/session-demand-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==15
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('session_demand_step.py','session_demand_flow.py','preserve_session_demand.py','audit_session_demand_legacy.py'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
write(e/(prefix+'attempts.json'),record)
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'public native reports; three complete suites pass.')

from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-08-content-';base='e349e782c210d48ddcc4cbfee47eadcf4e27a9a9';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'native_reports':[],
 'limitations':['Pinned preview and private Linux directory reading only. Durable resources, installed ownership, decoding, activation and non-Linux readers remain open.',
 'Historical-toolset execution on the modern Windows host and import audit do not qualify historical OS behavior.']}
attempts=[]
for p in sorted((r/'out/campaign/w-08-content-resolution').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test' and v['exit']==0 and not changed:
  count={'linux-x64-gcc13':164,'windows-x64-gcc15':148,'windows-x86-v141-xp':135}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases)
  record['full_runs'][v['profile']]={'record':item,'cases':cases}
  if 'current_inputs' in record:assert record['current_inputs']==v['source_inputs']
  record['current_inputs']=v['source_inputs']
assert len(record['full_runs'])==3
for p in sorted((r/'out/campaign').glob('content-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
for pattern,family,exe,oracle,count in [('configuration-*','CONFIG-STORE','SysPane.ConfigProbe','native_store.py',20),('commands-*','COMMAND-IPC','SysPane.CommandProbe','native_command.py',6),('reconciliation-*','RECONCILIATION','SysPane.CommandProbe','native_reconciliation.py',6),('supervision-*','TRANSACTION-SUPERVISION','SysPane.CommandProbe','native_supervision.py',7),('content-*','CONTENT-READER','SysPane.ContentProbe','native_content.py',17)]:
 for p in sorted((b/'native-evidence').glob(pattern+'/result.json')):
  if p.stat().st_mtime<cutoff:continue
  v=json.loads(p.read_text());assert v['family']==family;item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
  item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
  if v['outcome']=='pass' and v['executable_sha256']==sha(b/exe) and v['oracle_sha256']==sha(r/'tests/configuration'/oracle):
   assert len(v['cases'])==count;record['final_'+family]=item
 assert 'final_'+family in record
record['artifacts']={}
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
for profile,root in roots.items():
 names=['syspane_authored_tests'+('' if profile.startswith('linux') else '.exe')]
 names+=['syspane_authored.lib'] if profile.endswith('xp') else ['libsyspane_authored.a']
 if profile.startswith('linux'):names+=['SysPane.CommandProbe','SysPane.ConfigProbe','SysPane.ContentProbe','libsyspane_content_reader.a']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
record['historical_audit']=copy(r/'out/campaign/content-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==17
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('content_step.py','content_flow.py','preserve_content.py','audit_content_legacy.py'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native reports; three full runs match current inputs.')

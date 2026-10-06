from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-08-command-';base='1f3ff09aaaaeb2e362a3b46e34e59697765aec4b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'final_focus':{},'native_reports':[],
 'limitations':['Complete suites pass before five audit/profile/transport-document updates and a provenance-only timestamp correction; final affected checks pass with every current executable input; one later package timestamp correction is separately checked byte-for-byte. Compiled source and independent native oracles are unchanged after the full runs.',
 'Finite Linux IPC/thread/ext4 fixture only. Installed ownership, worker supervision, original-epoch wire reconciliation, assets, native controls and activation remain open.',
 'Historical-toolset execution on the modern Windows host and import audit do not qualify historical OS behavior.']}
correction=json.loads((r/'out/campaign/command-document-provenance.json').read_text())
allowed={correction['path'],'build-support/check_legacy_artifacts.py','build-support/targets/windows-x86-v141-xp.imports.json',
 'build-support/targets/windows-x86-v141-xp.json','build-support/targets/windows-x86-v141-xp.lock.json','spec/contracts/transport.md'}
attempts=[]
for p in sorted((r/'out/campaign/w-08-command').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test':
  count={'linux-x64-gcc13':147,'windows-x64-gcc15':134,'windows-x86-v141-xp':123}[v['profile']]
  assert v['exit']==0 and f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases) and set(changed)==allowed,changed
  record['full_runs'][v['profile']]={'record':item,'cases':cases,'subsequent_changes':changed}
 if v['action']=='focus' and v['exit']==0 and changed==[correction['path']]:
  with zipfile.ZipFile(zpath) as z:
   assert z.read(correction['path']).decode().replace(correction['old'],correction['new'])==(r/correction['path']).read_text()
  count={'linux-x64-gcc13':36,'windows-x64-gcc15':34,'windows-x86-v141-xp':36}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  record['final_focus'][v['profile']]={'record':item,'count':count}
  inputs={n:sha(r/n) for n in v['source_inputs']}
  if 'current_inputs' in record:assert record['current_inputs']==inputs
  record['current_inputs']=inputs
  record['post_check_provenance_correction']=correction
assert len(record['full_runs'])==len(record['final_focus'])==3
assert any(v['exit']!=0 and v['action']=='build' for v in attempts)
assert any(v['exit']!=0 and v['action']=='focus' for v in attempts)
for p in sorted((r/'out/campaign').glob('command-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
for pattern,family,exe,oracle,count in [('configuration-*','CONFIG-STORE','SysPane.ConfigProbe','native_store.py',20),('commands-*','COMMAND-IPC','SysPane.CommandProbe','native_command.py',6)]:
 for p in sorted((b/'native-evidence').glob(pattern+'/result.json')):
  if p.stat().st_mtime<cutoff:continue
  v=json.loads(p.read_text());assert v['family']==family;item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
  item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
  if v['outcome']=='pass' and v['executable_sha256']==sha(b/exe) and v['oracle_sha256']==sha(r/'tests/configuration'/oracle):
   assert len(v['cases'])==count;record['final_'+family]=item
assert 'final_COMMAND-IPC' in record and 'final_CONFIG-STORE' in record
record['artifacts']={}
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
for profile,root in roots.items():
 names=['syspane_command_session_tests'+('' if profile.startswith('linux') else '.exe')]
 names+=['syspane_async_commands.lib'] if profile.endswith('xp') else ['libsyspane_async_commands.a']
 if profile.startswith('linux'):names+=['SysPane.CommandProbe','SysPane.ConfigProbe']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
for source,name in [('command-legacy-audit.json','historical_audit'),('command-legacy-initial-failure.json','historical_initial_failure'),('command-runtime-docs.json','runtime_sources')]:
 record[name]=copy(r/'out/campaign'/source,e/(prefix+source.removeprefix('command-')))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==17
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('command_step.py','command_flow.py','preserve_command.py','audit_command_legacy.py','command_runtime_docs.py','command-runtime-docs-input.json','command-document-provenance.json'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native reports; full and final affected runs match declared inputs.')

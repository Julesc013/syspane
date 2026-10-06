from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-08-authored-';base='c2656732efb5f15f3b257e4508c7052154c503d7';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'final_focus':{},'native_reports':[],
 'limitations':['Shared authored state and finite Linux ext4 storage experiment; installed resource closure, asynchronous IPC commits/cancellation and public reconciliation messages remain open.',
 'Full suites pass before the final Linux-only guard-placement refinement and import/component metadata amendments. Final affected checks pass separately; all shared compiled code and prior native oracles remain unchanged.',
 'Historical PE/import audit initially failed on four undeclared event APIs. Documented XP APIs are now explicitly admitted; actual historical OS execution remains unqualified.',
 'No hardware power-cut, other filesystem, Windows/Mac storage, installed policy, visible activation or complete release qualification.']}
allowed={'build-support/components.json','build-support/targets/windows-x86-v141-xp.imports.json',
 'source/platform/generation_store_linux.cpp','source/application/configuration_probe.cpp','tests/configuration/native_store.py'}
attempts=[]
for p in sorted((r/'out/campaign/w-08-authored').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append((v,item))
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test':
  count={'linux-x64-gcc13':139,'windows-x64-gcc15':127,'windows-x86-v141-xp':116}[v['profile']]
  assert v['exit']==0 and f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases) and set(changed)==allowed,changed
  record['full_runs'][v['profile']]={'record':item,'cases':cases,'subsequent_changes':changed}
 if v['action']=='focus' and v['exit']==0 and not changed:
  count={'linux-x64-gcc13':11,'windows-x64-gcc15':10,'windows-x86-v141-xp':12}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  record['final_focus'][v['profile']]={'record':item,'count':count}
  if 'current_inputs' in record:assert record['current_inputs']==v['source_inputs']
  record['current_inputs']=v['source_inputs']
 if v['exit']!=0:
  assert v['action']=='focus' and 'forbidden dependency' in v['stdout'];record['initial_component_failure']=item
assert len(record['full_runs'])==len(record['final_focus'])==3 and 'initial_component_failure' in record
for p in sorted((r/'out/campaign').glob('authored-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v,_ in attempts)
for p in sorted((b/'native-evidence').glob('configuration-*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());assert v['outcome']=='pass';item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
 item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
 if v['executable_sha256']==sha(b/'SysPane.ConfigProbe') and v['oracle_sha256']==sha(r/'tests/configuration/native_store.py'):
  assert len(v['cases'])==20;record['final_native_report']=item
assert 'final_native_report' in record
record['artifacts']={};roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
for profile,root in roots.items():
 names=['syspane_authored_tests'+('' if profile.startswith('linux') else '.exe')]
 names+=['syspane_authored.lib'] if profile.endswith('xp') else ['libsyspane_authored.a']
 if profile.startswith('linux'):names+=['SysPane.ConfigProbe','libsyspane_generation_store.a']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
record['historical_audit']=copy(r/'out/campaign/authored-legacy-audit.json',e/(prefix+'legacy-audit.json'))
record['historical_initial_failure']=copy(r/'out/campaign/authored-legacy-initial-failure.json',e/(prefix+'legacy-initial-failure.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==16
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('authored_step.py','authored_flow.py','preserve_authored.py','audit_authored_legacy.py'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
write(e/(prefix+'attempts.json'),record)
print('Preserved',len(record['attempts']),'attempts,',len(record['native_reports']),'native reports, full-suite passes and final affected reruns.')

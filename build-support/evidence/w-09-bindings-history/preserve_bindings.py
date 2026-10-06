from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-09-bindings-';base='743da6cd75a342e53ba76492b9c312c69ddffa10';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 assert '.private.' not in p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'native_reports':[],
 'limitations':['Shared policy-bound authored bindings and geometry only. Native routing, measurement, raster drawing, editing, cache erasure and visible activation remain open.',
 'Historical-toolset execution on the modern Windows host and import audit do not qualify historical OS behavior.']}
attempts=[]
for p in sorted((r/'out/campaign/w-09-bindings').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test' and v['exit']==0 and not changed and v.get('test_artifact_sha256') and v.get('test_artifact_after_sha256')==v['test_artifact_sha256'] and not v.get('source_changed_during_execution'):
  count={'linux-x64-gcc13':220,'windows-x64-gcc15':202,'windows-x86-v141-xp':189}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases)
  record['full_runs'][v['profile']]={'record':item,'cases':cases}
  if 'current_inputs' in record:assert record['current_inputs']==v['source_inputs']
  record['current_inputs']=v['source_inputs']
assert len(record['full_runs'])==3
for profile in record['full_runs']:
 assert any(v['profile']==profile and v['action']=='build' and v['exit']==0 and
            v['source_inputs']==record['current_inputs'] and v.get('source_changed_during_execution')==[] for v in attempts)
for p in sorted((r/'out/campaign').glob('bindings-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
final_linux=json.loads((r/record['full_runs']['linux-x64-gcc13']['record']['path']).read_text())
final_start=datetime.fromisoformat(final_linux['started_at']).timestamp();final_end=datetime.fromisoformat(final_linux['finished_at']).timestamp()
for pattern,family,exe,oracle,count in [('configuration-*','CONFIG-STORE','SysPane.ConfigProbe','native_store.py',20),('commands-*','COMMAND-IPC','SysPane.CommandProbe','native_command.py',6),('reconciliation-*','RECONCILIATION','SysPane.CommandProbe','native_reconciliation.py',6),('supervision-*','TRANSACTION-SUPERVISION','SysPane.CommandProbe','native_supervision.py',7),('content-????????????','CONTENT-READER','SysPane.ContentProbe','native_content.py',17),('content-commands-*','CONTENT-COMMANDS','SysPane.CommandProbe','native_content_commands.py',9),('resources-*','RESOURCE-GENERATIONS','SysPane.ConfigProbe','native_resources.py',31)]:
 for p in sorted((b/'native-evidence').glob(pattern+'/result.json')):
  if p.stat().st_mtime<cutoff:continue
  v=json.loads(p.read_text());assert v['family']==family;item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
  item.update(outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
  if final_start<=p.stat().st_mtime<=final_end and v['outcome']=='pass' and v['executable_sha256']==sha(b/exe) and v['oracle_sha256']==sha(r/'tests/configuration'/oracle):
   assert len(v['cases'])==count;record['final_'+family]=item
 assert 'final_'+family in record
record['artifacts']={}
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
for profile,root in roots.items():
 names=['syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')]
 names+=['syspane_scene.lib'] if profile.endswith('xp') else ['libsyspane_scene.a']
 if profile.startswith('linux'):names+=['SysPane.CommandProbe','SysPane.ConfigProbe','SysPane.ContentProbe','libsyspane_content_reader.a']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
 v=json.loads((r/record['full_runs'][profile]['record']['path']).read_text());assert v['test_artifact_sha256']==sha(root/names[0])
record['historical_audit']=copy(r/'out/campaign/bindings-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==18
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('bindings_step.py','bindings_flow.py','bindings_full_campaign.py','preserve_bindings.py','audit_bindings_legacy.py',
          'finish_bindings_checks.py','finish_bindings_handoff.py','stage_bindings.py','bindings-allowed.json'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
record['retained_failures']=[a for a in record['attempts'] if a['exit']!=0]
assert record['retained_failures']
for name in ('bindings-budget-initial.json','bindings-runtime-revision.json','revise_bindings_runtime.py',
             'bindings-original.json','bindings-original.zip','bindings-content-timeout-review.json',
             'bindings-content-timeout.zip','record_bindings_content_timeout.py'):
 source=r/'out/campaign'/name;destination=e/(prefix+'history')/name
 item=copy(source,destination)
 if name.endswith('.json'):
  destination.write_text(json.dumps(json.loads(source.read_text()),indent=2)+'\n',encoding='utf-8',newline='\n')
  item.update(sha256=sha(destination),original_file_sha256=sha(source),normalization='JSON formatting/LF; original values retained')
 record['invocations'].append(item)
original=json.loads((r/'out/campaign/bindings-original.json').read_text());assert original['before_implementation'] is True
with zipfile.ZipFile(r/'out/campaign/bindings-original.zip') as z:
 assert set(z.namelist())==set(original['files'])
 for n,h in original['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
record['oracle_review']={'original_families':13,'final_families':17,
 'fixture_corrections':['Add existing accessibility disclosure grant; fail early on absent attachment.','Remove invalid snapshot producer_id; producer identity remains in the wire envelope.','Correct one misleading test indentation.'],
 'wire_contract_correction':'Original multi-source wire setup conflicts with existing telemetry entity/field uniqueness. Preserve failure; assert wire rejection and pending projection. Preserve original ambiguous row/selection expectations in BIND-MULTISOURCE using the existing typed retained DataView, which admits multiple sources.',
 'added_cases':['Typed retained multi-source ambiguity','Actual restart and latched clock fault','Signed binary64 comparison and missing-last sort','270 matches with 256 bounded output rows','Maximum Unicode predicate grammar above 32 KiB'],
 'contract_metadata_correction':'Original package generation timestamp corrected to actual archive observation; pin-mapping work charge and existing wire uniqueness clarified.'}
record['native_timeout_review']='One full run timed out at the unchanged 1-second CONTENT-COMMANDS receive check after correct worker replacement. Selected revision remained 40. Complete synthetic failure tree and logs preserved; isolated unchanged oracle subsequently passed. Cause remains undetermined; no deadline/assertion changed.'
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native reports; three full runs match final inputs and test executables.')

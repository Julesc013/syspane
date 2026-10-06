from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-09-text-';base='d79da0b9cf2077c85a505b5f5304cd59e7e7c247';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'native_reports':[],
 'limitations':['Native offscreen plain-text raster on Linux only; no current-policy cache owner, full scene composition, accessibility or host visibility qualification.','Historical-toolset execution takes place on the modern Windows host.']}
attempts=[]
for p in sorted((r/'out/campaign/w-09-text').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test' and v['exit']==0 and not changed and v.get('test_artifact_sha256') and v.get('test_artifact_after_sha256')==v['test_artifact_sha256'] and not v.get('source_changed_during_execution'):
  count={'linux-x64-gcc13':221,'windows-x64-gcc15':202,'windows-x86-v141-xp':189}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases)
  record['full_runs'][v['profile']]={'record':item,'cases':cases}
  if 'current_inputs' in record:assert record['current_inputs']==v['source_inputs']
  record['current_inputs']=v['source_inputs']
assert len(record['full_runs'])==3
for profile in record['full_runs']:
 assert any(v['profile']==profile and v['action']=='build' and v['exit']==0 and v['source_inputs']==record['current_inputs'] and v.get('source_changed_during_execution')==[] for v in attempts)
for p in sorted((r/'out/campaign').glob('text-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
final=json.loads((r/record['full_runs']['linux-x64-gcc13']['record']['path']).read_text())
start=datetime.fromisoformat(final['started_at']).timestamp();end=datetime.fromisoformat(final['finished_at']).timestamp()
for p in sorted((b/'native-evidence').glob('text-*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());assert v['family']=='TEXT-RASTER'
 item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
 zp=e/(prefix+'native')/(p.parent.name+'.zip')
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(p.parent.iterdir()):
   assert f.is_file();z.write(f,f.name)
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(v['files'])|{'result.json'}
  for n,h in v['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item.update(archive={'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
 if start<=p.stat().st_mtime<=end and v['outcome']=='pass':
  assert len(v['cases'])==27 and v['executable_sha256']==sha(b/'SysPane.TextProbe') and v['oracle_sha256']==sha(r/'tests/scene/native_text.py')
  assert v['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json');record['final_native']=item
assert 'final_native' in record
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
record['artifacts']={}
for profile,root in roots.items():
 names=['syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')]
 if profile.startswith('linux'):names+=['SysPane.TextProbe','libsyspane_native_text.a']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
 v=json.loads((r/record['full_runs'][profile]['record']['path']).read_text());assert v['test_artifact_sha256']==sha(root/names[0])
record['historical_audit']=copy(r/'out/campaign/text-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==18
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('text_step.py','text_flow.py','text_remaining_profiles.py','preserve_text.py','audit_text_legacy.py','finish_text_checks.py','finish_text_handoff.py','stage_text.py','text-allowed.json','text-original.json','text-original.zip'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
original=json.loads((r/'out/campaign/text-original.json').read_text());assert original['before_implementation']
with zipfile.ZipFile(r/'out/campaign/text-original.zip') as z:
 for n,h in original['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
record['retained_failures']=[a for a in record['attempts'] if a['exit']!=0]
assert record['retained_failures'] and any(x['outcome']=='fail' for x in record['native_reports'])
record['oracle_review']={'original_families':25,'final_families':27,'changes':'Added native malformed-UTF8 and color-font assertions; existing assertions unchanged. Color-font failure preserved and fixed by alpha coverage masking, without relaxing expectation. Added runtime identity checks before/after native test. Package corrected timestamp and made color-font semantics explicit.'}
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native archives; three full runs match final inputs.')

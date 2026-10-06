from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-09-surface-';base='d4eb38101cd144f00c84ec821c0c8cbe46ee781f';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'native_reports':[],
 'limitations':['Owned synthetic GTK/X11 scalar scene and AT-SPI name experiment only. Full widgets, installed ownership, native accessibility structure and behind-icons activation remain open.','Historical-toolset execution takes place on the modern Windows host.']}
attempts=[]
for p in sorted((r/'out/campaign/w-09-surface').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 changed=sorted(n for n,h in v['source_inputs'].items() if sha(r/n)!=h)
 if v['action']=='test' and v['exit']==0 and not v.get('source_changed_during_execution'):
  count={'linux-x64-gcc13':223,'windows-x64-gcc15':202,'windows-x86-v141-xp':189}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {count}' in v['stdout']
  cases=[{'case':name,'outcome':'pass' if status=='Passed' else 'fail'} for name,status in re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*(Passed|\*\*\*Failed)',v['stdout'])]
  assert len(cases)==count and all(c['outcome']=='pass' for c in cases)
  record['full_runs'][v['profile']]={'record':item,'cases':cases,'final_input_differences':changed}
 if v['action']=='oracle' and v['profile']=='linux-x64-gcc13' and v['exit']==0 and not changed and not v.get('source_changed_during_execution'):
  record['final_focus']=item;record['current_inputs']=v['source_inputs']
assert len(record['full_runs'])==3 and 'final_focus' in record
allowed_delta={'source/rendering/scene_surface.cpp','tests/scene/surface_tests.cpp'}
for profile,run in record['full_runs'].items():
 assert set(run['final_input_differences'])<=allowed_delta
 full=json.loads((r/run['record']['path']).read_text())
 assert any(v['profile']==profile and v['action']=='build' and v['exit']==0 and v['source_inputs']==full['source_inputs'] and not v.get('source_changed_during_execution') for v in attempts)
assert any(v['profile']=='linux-x64-gcc13' and v['action']=='build' and v['exit']==0 and v['source_inputs']==record['current_inputs'] and not v.get('source_changed_during_execution') for v in attempts)
for p in sorted((r/'out/campaign').glob('surface-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
final=json.loads((r/record['final_focus']['path']).read_text())
start=datetime.fromisoformat(final['started_at']).timestamp();end=datetime.fromisoformat(final['finished_at']).timestamp()
for p in sorted((b/'native-evidence').glob('surface-*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());assert v['family']=='SCENE-ERASURE'
 item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
 zp=e/(prefix+'native')/(p.parent.name+'.zip')
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
  for n,h in sorted(v['files'].items()):
   assert 'xauthority' not in n and not n.startswith('/') and '..' not in n.split('/')
   assert sha(p.parent/n)==h;z.write(p.parent/n,n)
  z.write(p,'result.json')
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(v['files'])|{'result.json'}
  for n,h in v['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item.update(archive={'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},outcome=v['outcome'],cases=len(v['cases']),artifact_sha256=v['executable_sha256']);record['native_reports'].append(item)
 if start<=p.stat().st_mtime<=end and v['outcome']=='pass':
  assert len(v['cases'])==3 and v['executable_sha256']==sha(b/'syspane_scene_surface_tests') and v['oracle_sha256']==sha(r/'tests/scene/native_surface.py')
  for mode in ('normal','ignore-pixels','ignore-accessible'):
   case=json.loads((p.parent/mode/'result.json').read_text())
   assert case['outcome']=='pass' and case['executable_sha256']==v['executable_sha256']
   assert case['text_probe_sha256']==sha(b/'SysPane.TextProbe') and case['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json')
   assert case['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')
   states=case['observations'];assert states
   if mode=='normal':
    assert {x['case'] for x in states}=={'INITIAL','REPLACE','REVOKE','STALE','REGRANT','FRESH','DISCONNECT'}
    for name in {x['case'] for x in states}:
     passed=[x for x in states if x['case']==name and x['pixels'] and x['accessible']]
     assert passed and passed[-1]['elapsed']<=(2 if name=='INITIAL' else .2)
   else:
    last=states[-1];assert last['case']=='REVOKE'
    assert not last['pixels' if mode=='ignore-pixels' else 'accessible']
  record['final_native']=item
assert 'final_native' in record
log=b/'Testing/Temporary/LastTest.log';raw=log.read_text();assert 'SURFACE-FAMILIES 22' in raw
record['final_native_ctest_log']=copy(log,e/(prefix+'native')/'focused-LastTest.log')
roots={'linux-x64-gcc13':b,'windows-x64-gcc15':r/'out/build/windows-x64-gcc15','windows-x86-v141-xp':r/'out/build/windows-x86-v141-xp/Release'}
record['artifacts']={}
for profile,root in roots.items():
 names=['syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')]
 if profile.startswith('linux'):names+=['SysPane.TextProbe','syspane_scene_surface_tests','libsyspane_scene_surface.a']
 record['artifacts'][profile]={n:{'sha256':sha(root/n),'bytes':(root/n).stat().st_size} for n in names}
 v=json.loads((r/record['full_runs'][profile]['record']['path']).read_text());assert v['test_artifact_sha256']==sha(root/names[0])
record['historical_audit']=copy(r/'out/campaign/surface-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['historical_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==18
for n,h in audit['verification_inputs'].items():assert sha(r/n)==h
for n in ('surface_step.py','surface_flow.py','surface_full_campaign.py','preserve_surface.py','audit_surface_legacy.py','finish_surface_checks.py','finish_surface_handoff.py','stage_surface.py','surface-allowed.json','surface-original.json','surface-original.zip'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
original=json.loads((r/'out/campaign/surface-original.json').read_text());assert original['before_implementation']
with zipfile.ZipFile(r/'out/campaign/surface-original.zip') as z:
 for n,h in original['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
record['retained_failures']=[a for a in record['attempts'] if a['exit']!=0]
assert record['retained_failures']
record['oracle_review']={'original_component_families':16,'final_component_families':22,'changes':'Original exact zero-age assertion exposed misuse of the rate interval helper; fix the shared binding and add a direct shared regression. Add scaled multi-display, alpha, pixel ceiling, forced policy, clear reentry and typed value cases. Native observer uses fixed expected strings and tightens timing to start at acknowledgement; 200 ms bound unchanged. Extend forced policy case to include true overriding authored false; preserve its failure and final focused correction.'}
record['qualification']='Three complete suites pass on their archived source revisions. A final Linux focused suite verifies the native-only forced-enable correction; declared full-run deltas are restricted to that source and its native test. All shared binding code and all other test inputs match.'
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native archives; three full runs plus final affected native checks are source-bound.')

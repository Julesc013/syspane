from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-09-table-';base='733234ef7e1b8a77f6139f3a9008e46949168af4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
 return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'native_reports':[],'configure_checks':{},'final_native':{}}
attempts=[]
for p in sorted((r/'out/campaign/w-09-table').glob('*/result.json')):
 v=json.loads(p.read_text());zpath=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zpath)==v['source_archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zpath,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item);attempts.append(v)
 current=all(sha(r/n)==h for n,h in v['source_inputs'].items()) and v.get('source_changed_during_execution')==[]
 if current and v['exit']==0:
  if v['action']=='configure':record['configure_checks'][v['profile']]=item
  if v['action']=='test':
   assert v['profile']=='linux-x64-gcc13' and '100% tests passed, 0 tests failed out of 225' in v['stdout']
   cases=re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*Passed',v['stdout']);assert len(cases)==225
   record['full_run']={'record':item,'cases':cases};record['current_inputs']=v['source_inputs'];full=v
assert 'full_run' in record and len(record['configure_checks'])==3
assert any(v['profile']=='linux-x64-gcc13' and v['action']=='build' and v['exit']==0 and v['source_inputs']==record['current_inputs'] for v in attempts)
for p in sorted((r/'out/campaign').glob('table-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
cutoff=min(datetime.fromisoformat(v['started_at']).timestamp() for v in attempts)
start=datetime.fromisoformat(full['started_at']).timestamp();end=datetime.fromisoformat(full['finished_at']).timestamp()
for p in sorted((b/'native-evidence').glob('surface-*/result.json')):
 if p.stat().st_mtime<cutoff:continue
 v=json.loads(p.read_text());assert v['family'] in ('SCENE-ERASURE','TABLE-ERASURE')
 zp=e/(prefix+'native')/(p.parent.name+'.zip');item=copy(p,e/(prefix+'native')/(p.parent.name+'.json'))
 if zp.exists():
  with zipfile.ZipFile(zp) as z:
   assert z.read('result.json')==p.read_bytes();actual={n:hashlib.sha256(z.read(n)).hexdigest() for n in v['files']}
 else:
  actual={}
  with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
   for n,h in sorted(v['files'].items()):
    assert 'xauthority' not in n and not n.startswith('/') and '..' not in n.split('/')
    actual[n]=sha(p.parent/n);z.write(p.parent/n,n)
   z.write(p,'result.json')
 changed={n:{'reported':v['files'][n],'archived':h} for n,h in actual.items() if v['files'][n]!=h}
 if v['outcome']=='pass':assert not changed
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(v['files'])|{'result.json'}
  for n,h in actual.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item.update(archive={'path':zp.relative_to(r).as_posix(),'sha256':sha(zp)},outcome=v['outcome'],family=v['family'],archived_files=actual,post_report_differences=changed)
 record['native_reports'].append(item)
 if start<=p.stat().st_mtime<=end and v['outcome']=='pass':
  assert len(v['cases'])==3 and v['executable_sha256']==sha(b/'syspane_scene_surface_tests') and v['oracle_sha256']==sha(r/'tests/scene/native_surface.py')
  with zipfile.ZipFile(zp) as z:
   for mode in ('normal','ignore-pixels','ignore-accessible'):
    case=json.loads(z.read(mode+'/result.json'));assert case['outcome']=='pass'
    assert case['text_probe_sha256']==sha(b/'SysPane.TextProbe') and case['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json') and case['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')
    states=case['observations'];assert states
    if mode=='normal':
     assert {x['case'] for x in states}=={'INITIAL','REPLACE','REVOKE','STALE','REGRANT','FRESH','DISCONNECT'}
     for name in {x['case'] for x in states}:assert any(x['case']==name and x['pixels'] and x['accessible'] and x['elapsed']<=(2 if name=='INITIAL' else .2) for x in states)
    else:
     last=states[-1];bad='pixels' if mode=='ignore-pixels' else 'accessible';assert last['case']=='REVOKE' and not last[bad] and last['accessible' if bad=='pixels' else 'pixels']
  record['final_native'][v['family']]=item
assert set(record['final_native'])=={'SCENE-ERASURE','TABLE-ERASURE'}
log=b/'Testing/Temporary/LastTest.log';raw=log.read_text();assert 'SURFACE-FAMILIES 22' in raw and 'TABLE-FAMILIES 16' in raw
logzip=e/(prefix+'native')/'full-LastTest.zip'
with zipfile.ZipFile(logzip,'w',zipfile.ZIP_DEFLATED) as z:z.write(log,'LastTest.log')
record['full_ctest_log']={'path':logzip.relative_to(r).as_posix(),'sha256':sha(logzip),'log_sha256':sha(log)}
record['artifacts']={n:{'sha256':sha(b/n),'bytes':(b/n).stat().st_size} for n in ('syspane_scene_tests','SysPane.TextProbe','syspane_scene_surface_tests','libsyspane_scene_surface.a')}
assert full['test_artifact_sha256']==full['test_artifact_after_sha256']==record['artifacts']['syspane_scene_tests']['sha256']
record['reclaimed_failure']= {'path':'build-support/evidence/w-09-table-archive-reclamation.json','sha256':sha(e/(prefix+'archive-reclamation.json'))}
for n in ('table_step.py','table_flow.py','table_full_campaign.py','preserve_table.py','archive_table_failure.py','finish_table_checks.py','finish_table_handoff.py','stage_table.py','table-allowed.json','table-original.json','table-original.zip'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
record['retained_failures']=[a for a in record['attempts'] if a['exit']!=0];assert record['retained_failures']
record['oracle_review']={'original_table_families':14,'final_table_families':16,'scalar_families':22,'changes':'Preserve original table failure. Add cell budget and rational-scale cases. Remove the invalid child cache-mask setting and preserve failed application-cache experiment; retain explicit cache clearing. Precompute references before stimuli without extending acknowledgement-based deadlines. Add owned process-group timeout cleanup and retain partial streams. No expected table/scalar value, grid rule or erasure criterion changed.'}
record['qualification']='Full Linux suite passes on final exact archived inputs. Both owned native experiments pass with negative controls. Windows configure/inventory checks only; no new Windows runtime qualification or installed/native accessibility-table claim.'
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts and',len(record['native_reports']),'native archives; full final Linux suite source-bound.')

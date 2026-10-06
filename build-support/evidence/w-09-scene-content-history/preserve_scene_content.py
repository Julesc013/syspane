from pathlib import Path
from datetime import datetime
import hashlib,json,re,shutil,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');e=r/'build-support/evidence';b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
prefix='w-09-scene-content-';base='36f203aeeaa3d7d70dee9cad2b2a68ad3c890954';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d);return {'path':d.relative_to(r).as_posix(),'sha256':sha(d)}
record={'source_base':base,'attempts':[],'invocations':[],'full_runs':{},'configure_checks':{},'build_checks':{},'final_native':{},'artifacts':{},'full_logs':{}}
current_inputs=None
for p in sorted((r/'out/campaign/w-09-scene-content').glob('*/result.json')):
 v=json.loads(p.read_text());zp=p.parent/'source-inputs.zip';assert v['source_base']==base and sha(zp)==v['source_archive_sha256']
 with zipfile.ZipFile(zp) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 item=copy(p,e/(prefix+'history')/p.parent.name/'result.json');item.update(profile=v['profile'],action=v['action'],exit=v['exit'],source_archive=copy(zp,e/(prefix+'history')/p.parent.name/'source-inputs.zip'))
 record['attempts'].append(item)
 current=all(sha(r/n)==h for n,h in v['source_inputs'].items()) and v.get('source_changed_during_execution')==[]
 if not current or v['exit']!=0:continue
 if v['action']=='configure':record['configure_checks'][v['profile']]=item
 if v['action']=='build':record['build_checks'][v['profile']]=item
 if v['action']=='test':
  expected={'linux-x64-gcc13':233,'windows-x64-gcc15':208,'windows-x86-v141-xp':195}[v['profile']]
  assert f'100% tests passed, 0 tests failed out of {expected}' in v['stdout']
  cases=re.findall(r'\d+/\d+ Test\s+#\d+: (\S+)\s+\.+\s*Passed',v['stdout']);assert len(cases)==expected
  assert all('configuration.SCENE-CONTENT-'+case in cases for case in ('SCHEMA','MIGRATION','RESOURCES','PREVIEW','TX','SESSION'))
  record['full_runs'][v['profile']]={'record':item,'cases':cases,'started_at':v['started_at'],'finished_at':v['finished_at']}
  if current_inputs is None:current_inputs=v['source_inputs']
  assert current_inputs==v['source_inputs']
assert len(record['full_runs'])==len(record['configure_checks'])==len(record['build_checks'])==3
record['current_inputs']=current_inputs
for p in sorted((r/'out/campaign').glob('scene-content-execution-*.json')):record['invocations'].append(copy(p,e/(prefix+'history')/p.name))
record['native_reports']=json.loads((e/(prefix+'native-index.json')).read_text())
full=record['full_runs']['linux-x64-gcc13'];start=datetime.fromisoformat(full['started_at']).timestamp();end=datetime.fromisoformat(full['finished_at']).timestamp()
for item in record['native_reports']:
 v=json.loads((r/item['path']).read_text());zp=r/item['archive']['path'];assert sha(zp)==item['archive']['sha256']
 with zipfile.ZipFile(zp) as z:
  for n,h in item['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 if not(start<=item['finished_mtime']<=end and v['outcome']=='pass'):continue
 if v['family']=='SCENE-CONTENT':
  assert len(v['cases'])==34 and v['executable_sha256']==sha(b/'SysPane.ConfigProbe') and v['oracle_sha256']==sha(r/'tests/configuration/native_scene_content.py')
 else:
  assert len(v['cases'])==3 and v['executable_sha256']==sha(b/'syspane_scene_surface_tests') and v['oracle_sha256']==sha(r/'tests/scene/native_surface.py')
  with zipfile.ZipFile(zp) as z:
   for mode in ('normal','ignore-pixels','ignore-accessible'):
    case=json.loads(z.read(mode+'/result.json'));assert case['outcome']=='pass'
    assert case['text_probe_sha256']==sha(b/'SysPane.TextProbe') and case['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json') and case['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')
    states=case['observations']
    if mode=='normal':
     assert {x['case'] for x in states}=={'INITIAL','REPLACE','REVOKE','STALE','REGRANT','FRESH','DISCONNECT'}
     for name in {x['case'] for x in states}:assert any(x['case']==name and x['pixels'] and x['accessible'] and x['elapsed']<=(2 if name=='INITIAL' else .2) for x in states)
    else:
     last=states[-1];bad='pixels' if mode=='ignore-pixels' else 'accessible';assert last['case']=='REVOKE' and not last[bad] and last['accessible' if bad=='pixels' else 'pixels']
 record['final_native'][v['family']]=item
assert set(record['final_native'])=={'SCENE-CONTENT','SCENE-ERASURE','TABLE-ERASURE','CONTENT-ERASURE'}
for profile,full in record['full_runs'].items():
 root=b if profile.startswith('linux') else r/'out/build'/profile
 binary_root=root/'Release' if profile.endswith('xp') else root
 suffix='' if profile.startswith('linux') else '.exe'
 names=['syspane_authored_tests'+suffix]
 if profile.startswith('linux'):names+=['SysPane.ConfigProbe','SysPane.TextProbe','syspane_scene_surface_tests','libsyspane_scene_surface.a']
 record['artifacts'][profile]={n:{'sha256':sha(binary_root/n),'bytes':(binary_root/n).stat().st_size} for n in names}
 attempt=json.loads((r/full['record']['path']).read_text());assert attempt['test_artifact_sha256']==attempt['test_artifact_after_sha256']==record['artifacts'][profile][names[0]]['sha256']
 log=root/'Testing/Temporary/LastTest.log';zp=e/(prefix+'native')/(profile+'-LastTest.zip')
 with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:z.write(log,'LastTest.log')
 record['full_logs'][profile]={'path':zp.relative_to(r).as_posix(),'sha256':sha(zp),'log_sha256':sha(log)}
 if profile.startswith('linux'):assert 'SURFACE-FAMILIES 22' in log.read_text() and 'TABLE-FAMILIES 17' in log.read_text()
record['legacy_audit']=copy(r/'out/campaign/scene-content-legacy-audit.json',e/(prefix+'legacy-audit.json'))
audit=json.loads((r/record['legacy_audit']['path']).read_text());assert audit['outcome']=='pass' and len(audit['artifacts'])==18
for n,row in audit['artifacts'].items():assert sha(r/'out/build/windows-x86-v141-xp/Release'/n)==row['sha256']
for n in ('scene_content_step.py','scene_content_flow.py','scene_content_full_campaign.py','scene_content_final_campaign.py','audit_scene_content_legacy.py','archive_scene_content_native.py','reclaim_scene_content_captures.py','preserve_scene_content.py','finish_scene_content_checks.py','finish_scene_content_handoff.py','stage_scene_content.py','scene-content-original.json','scene-content-original.zip'):
 record['invocations'].append(copy(r/'out/campaign'/n,e/(prefix+'history')/n))
record['retained_failures']=[a for a in record['attempts'] if a['exit']!=0]
record['reclaimed']={'path':(e/(prefix+'reclaimed.json')).relative_to(r).as_posix(),'sha256':sha(e/(prefix+'reclaimed.json'))}
record['oracle_review']='Original six shared families and 31 native storage cases retained. Add Unicode/control/line bounds, required-feature incompatibility, content-capability denial, required resource-bearing generations/initialization, native labels/body and erasure checks. Existing scalar/table expected values and acknowledgement-based deadlines remain unchanged. Historical migration diagnostics exposed a roots string from an ambiguous single-element initializer; explicit array construction restores the intended fixture without changing expected outcomes. The source-stability-rejected Windows attempt and all failing historical/native attempts remain preserved. Opaque image bytes test identity, not decoding.'
record['qualification']='Complete suites on three development profiles. Native content durability and synthetic text/label pixel/name evidence is Linux-only. Historical-toolset execution on modern Windows and PE/import checks do not qualify historical OS compatibility. All complete editions remain open.'
(e/(prefix+'attempts.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(record['attempts']),'attempts;',[(p,len(v['cases'])) for p,v in record['full_runs'].items()])

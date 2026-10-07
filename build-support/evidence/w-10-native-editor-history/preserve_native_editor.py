from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-10-native-editor-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='c225a32823682b904e624d295b694d233accb773'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-10-native-editor').glob('*/result.json')):
 v=json.loads(p.read_text());assert v['source_base']==base;target=history/p.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
 assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for name,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
 row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
 if 'ctest_log_archive_sha256' in v:
  shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
 attempts.append(row)
helpers=['native_editor_step.py','native_editor_flow.py','prepare_native_editor.py','prepare_native_build.py','prepare_editor_window.py','extract_private_text.py','archive_native_editor.py','preserve_native_editor.py','setup_native_editor_evidence.py','reclaim_native_prior.ps1','native-editor-prior-reclamation.json','native-editor-allocation.json']
for p in [*sorted((r/'out/campaign').glob('native-editor-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/native-editor-original').iterdir():shutil.copyfile(p,history/p.name)
final={};artifacts={};input_differences={}
def latest(profile,action):
 row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_text())
current=latest('linux-x64-gcc13','native')[1]['source_inputs']
def compatible(v):
 assert set(v['source_inputs'])==set(current)
 differences={n:dict(executed=h,current=current[n]) for n,h in v['source_inputs'].items() if h!=current[n]}
 assert set(differences)<= {'tests/editor/native_editor.py'},differences
 if differences:
  assert v['action'] in ('build','test')
  input_differences[v['profile']+'-'+v['action']]=dict(files=differences,reason='Only the independent native editor Python observer changed after this successful compile/portable suite. It is not a compiler input or invoked by the portable selection; final native execution uses the current observer.')
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
 row,v=latest(profile,'test');build,b=latest(profile,'build')
 assert not v['exit'] and not b['exit'] and not v['source_changed_during_execution'] and not b['source_changed_during_execution']
 compatible(v);compatible(b)
 cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))==69
 with zipfile.ZipFile(r/row['ctest_log']['path']) as z:
  data=z.read('LastTest.log');assert hashlib.sha256(data).hexdigest()==v['ctest_log_sha256']
  for case in cases:assert 'Test: '+case in data.decode()
 final[profile]=dict(record={k:row[k] for k in ('path','sha256')},build={k:build[k] for k in ('path','sha256')},cases=cases,log=row['ctest_log'])
 if profile.startswith('linux'):
  code="""from pathlib import Path
import hashlib,json
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');names=['syspane_editor_tests','syspane_editor_window','syspane_settings_window','SysPane.EditorExitProbe','syspane_scene_surface_tests','syspane_scene_inspector_tests','SysPane.TextProbe','SysPane.ImageWorker','libsyspane_editor_form.a','libsyspane_private_text.a']
print(json.dumps({n:{'sha256':hashlib.sha256((b/n).read_bytes()).hexdigest(),'bytes':(b/n).stat().st_size} for n in names}))"""
  artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
 else:
  binary_root=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
  names=['syspane_editor_tests.exe','syspane_settings_tests.exe','syspane_authored_tests.exe','syspane_command_session_tests.exe','syspane_protocol_tests.exe']
  artifacts[profile]={n:dict(sha256=sha(binary_root/n),bytes=(binary_root/n).stat().st_size) for n in names}
 assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
regressions={}
for action in ('native','oracle','exit','surface'):
 row,v=latest('linux-x64-gcc13',action);assert v['exit']==0 and not v['source_changed_during_execution'] and v['source_inputs']==current
 assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts['linux-x64-gcc13'][v['test_artifact']]['sha256']
 regressions[action]=dict(record={k:row[k] for k in ('path','sha256')},cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']),log=row['ctest_log'])
for name,digest in current.items():assert sha(r/name)==digest,('tested input changed',name)
native=json.loads((r/(prefix+'native-index.json')).read_text());final_native={}
families={'EDITOR-FORM':('syspane_editor_window','tests/editor/native_editor.py',20),'SETTINGS-FORM':('syspane_settings_window','tests/configuration/native_settings.py',18),
 'EDITOR-EXIT-01':('SysPane.EditorExitProbe','tests/desktop/native_editor_exit.py',9),'SCENE-INSPECTOR':('syspane_scene_inspector_tests','tests/scene/native_inspector.py',None),
 **{n+'-ERASURE':('syspane_scene_surface_tests','tests/scene/native_surface.py',None) for n in ('SCENE','TABLE','CONTENT','CHART','IMAGE')}}
for family,(artifact,oracle,count) in families.items():
 row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);report=json.loads((r/row['path']).read_text());assert row['outcome']=='pass'
 assert report['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'],family
 if family=='EDITOR-EXIT-01':assert report['source_inputs'][oracle]==sha(r/oracle)
 else:assert report['oracle_sha256']==sha(r/oracle),family
 cases=report['cases'];assert all(c.get('outcome',c.get('result'))=='pass' for c in cases)
 if count is not None:assert len(cases)==count
 if family=='EDITOR-FORM':
  assert [c['case'] for c in cases]==json.loads((r/'tests/editor/native-cases.json').read_text())['modes']+['recovery-'+m for m in json.loads((r/'tests/editor/native-cases.json').read_text())['recovery_modes']]
  assert report['exit_executable_sha256']==artifacts['linux-x64-gcc13']['SysPane.EditorExitProbe']['sha256']
  with zipfile.ZipFile(r/row['archive']['path']) as z:
   for case in cases:
    raw=z.read(case['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==case['record_sha256'];detail=json.loads(raw)
    assert detail['executable_sha256']==report['executable_sha256'] and detail['oracle_sha256']==report['oracle_sha256'] and detail['fixture_sha256']==sha(r/'tests/editor/native-cases.json')
    if case['case'] in ('frozen-preview','wrong-commit','retain'):assert case['fault_detected'] and detail['fault_detected']
 final_native[family]={**{k:row[k] for k in ('path','sha256')},'artifact':artifact,'oracle':oracle,'cases':len(cases)}
original=json.loads((history/'original.json').read_text());amendments={}
for n,digest in original.items():
 if sha(r/n)!=digest:
  assert n=='spec/delivery/packages/w-10-native-editor.md'
  amendments[n]=dict(original_sha256=digest,current_sha256=sha(r/n),reason='Clarify native duplicate selects new roots after the fixed structural oracle exposed deletion of the original. Expected scenes and resource fixture are unchanged.')
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,executed_input_differences=input_differences,attempts=attempts,final_runs=final,regressions=regressions,artifacts=artifacts,
 originals={'original':dict(record=ref(history/'original.json'),archive=ref(history/'original.zip'))},contract_refinements=amendments,native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,
 scope='69 affected checks on each development profile, actual Linux editor and independent recovery, existing settings/exit/renderer regressions. Private laboratories do not qualify installed editions or historical operating systems.'))
print('Preserved',len(attempts),'attempts;', {k:len(v['cases']) for k,v in regressions.items()},'native families',len(final_native))

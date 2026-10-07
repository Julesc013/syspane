from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();e=r/'build-support/evidence';prefix='w-10-focus-idle-';history=e/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='9c1757de6a8227b2a4235f8be7b727a9d3f55d7d'
attempts=[]
for p in sorted((r/'out/campaign/w-10-focus-idle').glob('*/result.json')):
 v=json.loads(p.read_bytes());assert v['source_base']==base;target=history/p.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
 assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
 if 'ctest_log_archive_sha256' in v:
  shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
 attempts.append(row)
def latest(profile,action):
 row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_bytes())
current=latest('linux-x64-gcc13','rendering')[1]['source_inputs']
for p,h in current.items():assert sha(r/p)==h
final={}
for profile,actions in [('linux-x64-gcc13',('build','portable','refresh','editors','rendering')),('windows-x64-gcc15',('configure','graph')),('windows-x86-v141-xp',('configure','graph'))]:
 final[profile]={}
 for action in actions:
  row,v=latest(profile,action);assert not v['source_changed_during_execution'] and v['source_inputs']==current
  assert bool(v['exit']) if action in ('editors','rendering') else not v['exit']
  final[profile][action]=dict(record={k:row[k] for k in ('path','sha256')},outcome='fail' if v['exit'] else 'pass',cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']))
artifacts={};graphs={}
for profile in final:
 command=['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/capture_lock_artifacts.py',profile] if profile.startswith('linux') else [str(r/'.venv/Scripts/python.exe'),'-X','utf8','out/campaign/capture_lock_artifacts.py',profile]
 artifacts[profile]=json.loads(subprocess.check_output(command,text=True))
 for action,row in final[profile].items():
  v=json.loads((r/row['record']['path']).read_bytes())
  if action not in ('build','configure'):assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
 if profile.startswith('windows'):
  old=json.loads((e/'w-10-edit-locks-attempts.json').read_bytes())['artifacts'][profile];assert artifacts[profile]==old
  p=r/'out/build'/profile/'component-graph.txt';content=p.read_text();assert 'syspane_editor_form|' not in content and 'syspane_editor_refresh_probe|' not in content
  target=history/(profile+'-component-graph.txt');shutil.copyfile(p,target);graphs[profile]=ref(target)
assert len(final['linux-x64-gcc13']['portable']['cases'])==311
assert len(final['linux-x64-gcc13']['editors']['cases'])==11
assert len(final['linux-x64-gcc13']['refresh']['cases'])==1
assert len(final['linux-x64-gcc13']['rendering']['cases'])==13
native=json.loads((e/(prefix+'native-index.json')).read_bytes());final_native={};failed_native={}
families={'EDITOR-LOCKS':('syspane_editor_window','tests/editor/native_edit_locks.py',7),'EDITOR-CONTAINERS':('syspane_editor_window','tests/editor/native_containers.py',16),'EDITOR-LAYOUT':('syspane_editor_window','tests/editor/native_layout_authoring.py',21),'EDITOR-OBSERVATION':('syspane_editor_window','tests/editor/native_observation_cases.py',7),'EDITOR-WIDGET-CREATION':('syspane_editor_window','tests/editor/native_widget_creation.py',17),'EDITOR-BINDING-AUTHORING':('syspane_editor_window','tests/editor/native_binding_authoring.py',15),'EDITOR-CONTENT-PROPERTIES':('syspane_editor_window','tests/editor/native_content_properties.py',15),'EDITOR-SNAP':('syspane_editor_window','tests/editor/native_snap.py',13),'EDITOR-GROUP':('syspane_editor_window','tests/editor/native_group.py',11),'EDITOR-ARRANGE':('syspane_editor_window','tests/editor/native_arrange.py',14),'LARGE-COMMANDS':('SysPane.CommandProbe','tests/configuration/native_large_commands.py',24),'EDITOR-FORM':('syspane_editor_window','tests/editor/native_editor.py',20),'EDITOR-REFRESH':('syspane_editor_window','tests/editor/native_refresh.py',3)}
for family,(artifact,oracle,count) in families.items():
 row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);v=json.loads((r/row['path']).read_bytes())
 if family=='EDITOR-BINDING-AUTHORING':
  assert v['outcome']=='fail';failed_native[family]={**{k:row[k] for k in ('path','sha256','archive')},'artifact':artifact,'oracle':oracle};continue
 assert v['outcome']=='pass'
 assert v['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'] and v['oracle_sha256']==sha(r/oracle)
 assert len(v['cases'])==count and all(c.get('outcome',c.get('result'))=='pass' for c in v['cases'])
 if family=='LARGE-COMMANDS':assert v['editor_executable_sha256']==artifacts['linux-x64-gcc13']['syspane_editor_window']['sha256']
 final_native[family]={**{k:row[k] for k in ('path','sha256','archive')},'artifact':artifact,'oracle':oracle,'cases':count}
assert sum(v['cases'] for v in final_native.values())==168
row=next(n for n in native if n['path'].endswith('inspector-adc740ac4250.json'));assert row['outcome']=='fail'
failed_native['SCENE-INSPECTOR']={**{k:row[k] for k in ('path','sha256','archive')},'artifact':'syspane_scene_inspector_tests','oracle':'tests/scene/native_inspector.py'}
old=json.loads((e/'w-10-edit-locks-attempts.json').read_bytes())['artifacts']['linux-x64-gcc13']
for name in ('syspane_scene_inspector_tests','syspane_scene_surface_tests','syspane_text_probe','SysPane.ImageWorker'):
 if name in old:assert artifacts['linux-x64-gcc13'][name]==old[name]
helpers=['editor_idle_probe.c','build_editor_idle_probe.py','run_editor_idle_probe.py','analyze_editor_idle_probe.py','freeze_focus_idle.py','register_refresh_probe.py','record_refresh_oracle_correction.py','refresh_animation_probe.cpp','run_refresh_animation_probe.py','inspect_focus_text_runtime.py','admit_focus_text_runtime.py','admit_focus_image_runtime.py','setup_focus_idle.py','setup_focus_idle_more_prune.py','setup_refresh_runs.py','optimize_refresh_runs.py','extend_refresh_runs.py','refresh_step_before_walk.py','refresh_step_after_walk.py','refresh_flow_before_actions.py','refresh_step.py','refresh_flow.py','setup_focus_archive.py','archive_focus_idle.py','preserve_focus_idle.py','capture_lock_artifacts.py']
helpers.extend(['setup_focus_checks.py','record_focus_remaining.py','inspect_focus_budget.py','prepare_focus_final_cleanup.py','setup_focus_budget_cleanup.py','setup_focus_budget_more_cleanup.py'])
helpers.extend(p.name for p in (r/'out/campaign').glob('*focus_idle*') if p.is_file() and p.name not in helpers)
support={}
paths=[*(r/'out/campaign'/n for n in helpers),*sorted((r/'out/campaign').glob('focus-idle-*.json')),*sorted((r/'out/campaign').glob('refresh-execution-*.json')),*sorted((r/'out/campaign/focus-idle').glob('*'))]
for p in paths:
 assert p.is_file(),p
 name=p.relative_to(r/'out/campaign');target=history/'support'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);support[p.relative_to(r).as_posix()]=ref(target)
for name in ('fixed-inputs','fixed-regression'):
 fixed=json.loads((r/'out/campaign/focus-idle'/(name+'.json')).read_bytes());archive=r/'out/campaign/focus-idle'/(name+'.zip');assert sha(archive)==fixed['archive_sha256']
 with zipfile.ZipFile(archive) as z:
  for n,h in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
correction=json.loads((r/'out/campaign/focus-idle/oracle-correction.json').read_bytes())
for n,h in correction['new'].items():assert sha(r/n)==h
fixed=json.loads((r/'out/campaign/focus-idle/fixed-inputs.json').read_bytes())
for n,h in fixed['inputs'].items():
 if n!='source/interfaces/editor_form_linux.cpp':assert sha(r/n)==h
assert sha(r/'tests/editor/refresh-cases.json')==correction['unchanged_fixture_sha256']
write(e/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,final_runs=final,artifacts=artifacts,configured_windows_graphs=graphs,native_index=ref(e/(prefix+'native-index.json')),final_native=final_native,failed_native=failed_native,support=support,scope='Linux editor refresh fairness and policy-erasure scheduling in the owned laboratory. Preserve all preceding failures and diagnostic arms. The complete editor regression fails at a binding tab-role query; its cause remains unresolved and this checkpoint is not fully qualified. Windows sources and executable bytes are unchanged; only configure/composition checks rerun there. Full editions and historical qualification remain open.'))
print('Preserved',len(attempts),'attempts,',len(native),'native archives and',len(support),'support records.')

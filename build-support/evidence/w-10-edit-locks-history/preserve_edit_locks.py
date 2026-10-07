from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-10-edit-locks-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='83da967d8a7311b8124c3beae304af103730eccd'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-10-edit-locks').glob('*/result.json')):
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
helpers=['prepare_edit_locks.py', 'implement_lock_versions.py', 'resume_lock_versions.py', 'implement_native_locks.py', 'register_edit_locks.py', 'complete_lock_native_fixture.py', 'setup_lock_runs.py', 'prepare_locks_prune.py', 'prune_locks_attempts.ps1', 'locks-prune-plan.json', 'locks-pruned-attempts.json', 'prune_locks_duplicates.py', 'locks-pruned-duplicates.json', 'prepare_locks_more_cleanup.py', 'prune_locks_more_duplicates.py', 'fix_lock_schema_identity.py', 'correct_lock_numeric_oracle.py', 'document_edit_locks.py', 'add_locks_portable.py', 'locks_step.py', 'locks_flow.py', 'setup_edit_locks_evidence.py', 'archive_edit_locks.py', 'preserve_edit_locks.py', 'finish_edit_locks_checks.py', 'finish_edit_locks.py', 'stage_edit_locks.py']
helpers.append('capture_lock_artifacts.py')
helpers.extend(['probe_locks_focus.py','probe_locks_focus_state.py'])
for p in [*sorted((r/'out/campaign').glob('locks-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
for n in ('fixed-inputs.json','fixed-inputs.zip','oracle-correction.json','schema-identity-failure.json','specctl-before-identity.py'):shutil.copyfile(r/'out/campaign/w-10-edit-locks'/n,history/n)
fixed=json.loads((history/'fixed-inputs.json').read_bytes())
assert sha(history/'fixed-inputs.zip')==fixed['archive_sha256']
with zipfile.ZipFile(history/'fixed-inputs.zip') as z:
    for n,h in fixed['inputs'].items():
        raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h
        correction=fixed.get('metadata_corrections',{}).get(n)
        if correction:
            assert n.endswith('.md') and raw.count(correction['old'].encode())==1
            assert (r/n).read_bytes()==raw.replace(correction['old'].encode(),correction['new'].encode()) and sha(r/n)==correction['sha256']
        else:assert sha(r/n)==h
def latest(profile,action):
    row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_bytes())
last=latest('linux-x64-gcc13','bindings')[1]['source_inputs']
current={n:sha(r/n) for n in last}
input_differences={}
def compatible(v):
    assert set(v['source_inputs'])==set(current)
    assert v['source_inputs']==current

final={};regressions={};artifacts={};graphs={};portable={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
    row,v=latest(profile,'test');build,b=latest(profile,'build')
    pr,pv=latest(profile,'portable');assert not pv['exit'] and not pv['source_changed_during_execution'];compatible(pv);portable[profile]=dict(record={k:pr[k] for k in ('path','sha256')},log=pr['ctest_log'],cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',pv['stdout']))
    assert portable[profile]['cases'] and len(portable[profile]['cases'])==len(set(portable[profile]['cases']))
    for record in (v,b):assert not record['exit'] and not record['source_changed_during_execution'];compatible(record)
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))==146
    final[profile]=dict(record={k:row[k] for k in ('path','sha256')},build={k:build[k] for k in ('path','sha256')},cases=cases,log=row['ctest_log'])
    if profile.startswith('linux'):
        code='from pathlib import Path; import hashlib,json; b=Path("/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13"); names=["syspane_large_command_tests","syspane_editor_tests","syspane_settings_tests","syspane_authored_tests","syspane_command_session_tests","syspane_protocol_tests","syspane_editor_window","syspane_settings_window","SysPane.CommandProbe","SysPane.ConfigProbe","SysPane.ContentProbe","SysPane.EditorExitProbe"]; print(json.dumps({n:{"sha256":hashlib.sha256((b/n).read_bytes()).hexdigest(),"bytes":(b/n).stat().st_size} for n in names}))'
        artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
    else:
        bdir=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
        graph=r/'out/build'/profile/'component-graph.txt';assert 'syspane_editor_form|' not in graph.read_text() and 'editor_form_linux.cpp' not in graph.read_text()
        saved=history/(profile+'-component-graph.txt');shutil.copyfile(graph,saved);graphs[profile]=ref(saved)
        artifacts[profile]={n+'.exe':dict(sha256=sha(bdir/(n+'.exe')),bytes=(bdir/(n+'.exe')).stat().st_size) for n in ('syspane_large_command_tests','syspane_editor_tests','syspane_settings_tests','syspane_authored_tests','syspane_command_session_tests','syspane_protocol_tests')}
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
for profile in final:
    command=['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/capture_lock_artifacts.py',profile] if profile.startswith('linux') else [str(r/'.venv/Scripts/python.exe'),'-X','utf8','out/campaign/capture_lock_artifacts.py',profile]
    full=json.loads(subprocess.check_output(command,text=True))
    for name,identity in artifacts[profile].items():assert full[name]==identity
    artifacts[profile]=full
    assert set(final[profile]['cases'])<=set(portable[profile]['cases']) and not any(n.startswith('native.') for n in portable[profile]['cases'])
    assert len(portable[profile]['cases'])=={'linux-x64-gcc13':311,'windows-x64-gcc15':308,'windows-x86-v141-xp':305}[profile]
for action in ('locks','containers','layout','calibration','creation','bindings','properties','snap','group','arrange','native','large'):
    row,v=latest('linux-x64-gcc13',action);assert (bool(v['exit']) if action=='large' else not v['exit']) and not v['source_changed_during_execution'];compatible(v)
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts['linux-x64-gcc13'][v['test_artifact']]['sha256']
    regressions[action]=dict(record={k:row[k] for k in ('path','sha256')},outcome='fail' if v['exit'] else 'pass',cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']),log=row['ctest_log'])
native=json.loads((r/(prefix+'native-index.json')).read_bytes());final_native={}
failed_native=next(n for n in native if n['path'].endswith('large-commands-046364558a9d.json'))
assert failed_native['outcome']=='fail'
with zipfile.ZipFile(r/failed_native['archive']['path']) as z:
    failure=json.loads(z.read('gui-revoke/result.json'));assert failure['outcome']=='fail' and failure['stage']=='SUBMIT'
    f=failure['focus_failure'];assert not f['focused'] and f['sensitive'] and f['process_exit'] is None and f['x_focus'] in f['owner_windows']
diagnostics=[]
for suffix,expected in [('locks-focus-diagnostic-150c081f8ac5.json',['pass','fail','pass']),('locks-focus-state-fdd8ba38b7d0.json',['pass']*6)]:
    row=next(n for n in native if n['path'].endswith(suffix));record=json.loads((r/row['path']).read_bytes())
    assert record['outcome']=='observed' and [c['result'] for c in record['cases']]==expected
    for p,digest in record['inputs'].items():
        assert sha(history/Path(p).name if p.startswith('out/campaign/') else r/p)==digest
    diagnostics.append({k:row[k] for k in ('path','sha256','archive')})
focus_path=r/(prefix+'focus.json')
failed_rerun=next(n for n in native if n['path'].endswith('large-commands-3fac26c3492c.json'));assert failed_rerun['outcome']=='fail'
with zipfile.ZipFile(r/failed_rerun['archive']['path']) as z:
    detail=json.loads(z.read('gui-drag/result.json'));assert detail['outcome']=='fail' and detail['focus_failure']['control']=='undo'
write(focus_path,dict(outcome='unresolved',original={k:failed_native[k] for k in ('path','sha256','archive')},diagnostics=diagnostics,unchanged_full_suite_rerun=regressions['large']['record'],failed_rerun={k:failed_rerun[k] for k in ('path','sha256','archive')},scope='Apply-focus failed in the original full suite and one of three unchanged reproductions. Six failure-only instrumented runs passed. The full-suite rerun failed at Undo focus. Native interaction reliability remains unresolved; the 24-case large-command matrix has not passed.',setup_note='The first diagnostic launcher exited before creating a native experiment because its helper import directory was wrong; tests/fault corrected that local launcher import.'))
families={'EDITOR-LOCKS':('syspane_editor_window','tests/editor/native_edit_locks.py',7),'EDITOR-CONTAINERS':('syspane_editor_window','tests/editor/native_containers.py',16),'EDITOR-LAYOUT':('syspane_editor_window','tests/editor/native_layout_authoring.py',21),'EDITOR-OBSERVATION':('syspane_editor_window','tests/editor/native_observation_cases.py',7),'EDITOR-WIDGET-CREATION':('syspane_editor_window','tests/editor/native_widget_creation.py',17),'EDITOR-BINDING-AUTHORING':('syspane_editor_window','tests/editor/native_binding_authoring.py',15),'EDITOR-CONTENT-PROPERTIES':('syspane_editor_window','tests/editor/native_content_properties.py',15),'EDITOR-SNAP':('syspane_editor_window','tests/editor/native_snap.py',13),'EDITOR-GROUP':('syspane_editor_window','tests/editor/native_group.py',11),'EDITOR-ARRANGE':('syspane_editor_window','tests/editor/native_arrange.py',14),'LARGE-COMMANDS':('SysPane.CommandProbe','tests/configuration/native_large_commands.py',24),'EDITOR-FORM':('syspane_editor_window','tests/editor/native_editor.py',20)}
for family,(artifact,oracle,count) in families.items():
    if family=='LARGE-COMMANDS':continue # Explicit failed regression above; never record it as passed.
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);v=json.loads((r/row['path']).read_bytes());assert row['outcome']=='pass'
    assert v['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'] and v['oracle_sha256']==sha(r/oracle)
    assert v['cases'] and all(c.get('outcome',c.get('result'))=='pass' for c in v['cases'])
    if count is not None:assert len(v['cases'])==count
    if family=='EDITOR-LOCKS':assert v['fixture_sha256']==sha(r/'tests/editor/edit-lock-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-CONTAINERS':assert v['preview_fixture_sha256']==sha(r/'tests/editor/container-preview-cases.json') and v['fixture_sha256']==sha(r/'tests/editor/container-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-LAYOUT':assert v['fixture_sha256']==sha(r/'tests/editor/layout-authoring-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-OBSERVATION':assert v['fixture_sha256']==sha(r/'tests/editor/observation-cases.json') and v['helper_sha256']==sha(r/'tests/editor/native_observation.py') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-WIDGET-CREATION':
        assert v['fixture_sha256']==sha(r/'tests/editor/widget-creation-cases.json') and v['resources_sha256']==sha(r/'tests/editor/content-properties-fixture.json') and v['content_harness_sha256']==sha(r/'tests/editor/native_content_properties.py') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-BINDING-AUTHORING':
        assert v['fixture_sha256']==sha(r/'tests/editor/binding-authoring-cases.json') and v['text_fixture_sha256']==sha(r/'tests/editor/binding-text-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py') and v['content_harness_sha256']==sha(r/'tests/editor/native_content_properties.py')
    if family=='EDITOR-CONTENT-PROPERTIES':
        assert v['fixture_sha256']==sha(r/'tests/editor/content-properties-cases.json') and v['resources_sha256']==sha(r/'tests/editor/content-properties-fixture.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-SNAP':
        assert v['fixture_sha256']==sha(r/'tests/editor/snap-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='EDITOR-GROUP':
        assert v['fixture_sha256']==sha(r/'tests/editor/group-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py') and v['overlap_fixture_sha256']==sha(r/'tests/editor/group-overlap-cases.json')
    if family=='EDITOR-ARRANGE':
        assert v['fixture_sha256']==sha(r/'tests/editor/arrange-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')
    if family=='LARGE-COMMANDS':
        assert v['fixture_sha256']==sha(r/'tests/configuration/large-command-cases.json')
        assert v['store_executable_sha256']==artifacts['linux-x64-gcc13']['SysPane.ConfigProbe']['sha256']
        assert v['editor_executable_sha256']==artifacts['linux-x64-gcc13']['syspane_editor_window']['sha256']
    final_native[family]={**{k:row[k] for k in ('path','sha256')},'artifact':artifact,'oracle':oracle,'cases':len(v['cases'])}
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,validation_attempts=[],oracle_corrections=[ref(history/'oracle-correction.json')],focus_investigation=ref(focus_path),executed_input_differences=input_differences,attempts=attempts,final_runs=final,portable_runs=portable,regressions=regressions,artifacts=artifacts,configured_windows_graphs=graphs,originals=dict(record=ref(history/'fixed-inputs.json'),archive=ref(history/'fixed-inputs.zip')),native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,scope='146 affected checks on each development profile and independent native edit locks, containers, layout, observation calibration, creation, binding, content, snap, group, arrange, editor and large-command/store/IPC cases. Intermittent Apply-focus, native Windows/historical qualification, installed ownership, complete authoring and all release gates remain open.'))
print('Preserved',len(attempts),'attempts and',len(native),'native archives.')

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-10-snap-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='01bea41e2123f69b1d71285b5ab944122efeace7'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-10-snap').glob('*/result.json')):
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
helpers=['prepare_snap.py','snap_step.py','snap_flow.py','document_snap.py','archive_snap.py','preserve_snap.py','finish_snap_checks.py','setup_snap_evidence.py','finish_snap.py','stage_snap.py']
for p in [*sorted((r/'out/campaign').glob('snap-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
for n in ('fixed-inputs.json','fixed-inputs.zip'):shutil.copyfile(r/'out/campaign/w-10-snap'/n,history/n)
fixed=json.loads((history/'fixed-inputs.json').read_bytes())
assert sha(history/'fixed-inputs.zip')==fixed['archive_sha256']
with zipfile.ZipFile(history/'fixed-inputs.zip') as z:
    for n,h in fixed['inputs'].items():assert sha(r/n)==hashlib.sha256(z.read(n)).hexdigest()==h
def latest(profile,action):
    row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_bytes())
last=latest('linux-x64-gcc13','snap')[1]['source_inputs']
current={n:sha(r/n) for n in last}
input_differences={}
def compatible(v):
    assert set(v['source_inputs'])==set(current)
    delta={n:dict(executed=h,current=current[n]) for n,h in v['source_inputs'].items() if h!=current[n]}
    for n in delta:
        assert n.endswith('.md') or (n=='tests/editor/native_snap.py' and v['action']!='snap') or (n=='tests/editor/native_editor.py' and v['action'] not in ('native','arrange','large')) or (v['profile'].startswith('windows') and n=='source/interfaces/editor_form_linux.cpp'),n
    if delta:input_differences[v['profile']+'-'+v['action']]=dict(files=delta,reason='Only documentation, explicitly listed independent native Python observers, or the Linux-only EditorForm changed. The Linux-only source is absent from Windows target graphs; Python observers are not compiler inputs or invoked by the referenced portable selection. Final affected native execution uses the current source and observers.')
final={};regressions={};artifacts={};graphs={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
    row,v=latest(profile,'test');build,b=latest(profile,'build')
    for record in (v,b):assert not record['exit'] and not record['source_changed_during_execution'];compatible(record)
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))==105
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
for action in ('snap','group','arrange','native','large'):
    row,v=latest('linux-x64-gcc13',action);assert not v['exit'] and not v['source_changed_during_execution'];compatible(v)
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts['linux-x64-gcc13'][v['test_artifact']]['sha256']
    regressions[action]=dict(record={k:row[k] for k in ('path','sha256')},cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']),log=row['ctest_log'])
native=json.loads((r/(prefix+'native-index.json')).read_bytes());final_native={}
families={'EDITOR-SNAP':('syspane_editor_window','tests/editor/native_snap.py',13),'EDITOR-GROUP':('syspane_editor_window','tests/editor/native_group.py',11),'EDITOR-ARRANGE':('syspane_editor_window','tests/editor/native_arrange.py',14),'LARGE-COMMANDS':('SysPane.CommandProbe','tests/configuration/native_large_commands.py',24),'EDITOR-FORM':('syspane_editor_window','tests/editor/native_editor.py',20)}
for family,(artifact,oracle,count) in families.items():
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);v=json.loads((r/row['path']).read_bytes());assert row['outcome']=='pass'
    assert v['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'] and v['oracle_sha256']==sha(r/oracle)
    assert v['cases'] and all(c.get('outcome',c.get('result'))=='pass' for c in v['cases'])
    if count is not None:assert len(v['cases'])==count
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
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,executed_input_differences=input_differences,attempts=attempts,final_runs=final,regressions=regressions,artifacts=artifacts,configured_windows_graphs=graphs,originals=dict(record=ref(history/'fixed-inputs.json'),archive=ref(history/'fixed-inputs.zip')),native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,scope='105 affected checks on each development profile and independent native snap, group, arrange, editor and large-command/store/IPC cases. Native Windows/historical qualification, installed ownership, complete authoring and all release gates remain open.'))
print('Preserved',len(attempts),'attempts and',len(native),'native archives.')

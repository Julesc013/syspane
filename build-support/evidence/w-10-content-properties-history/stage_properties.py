from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-content-properties-';hp='build-support/evidence/content-properties-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_bytes());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/properties-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode());subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
subprocess.run(['git','add','--renormalize','--',prefix+'history'],check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths)
cache={};digests={}
def content(p):
    if p not in cache:cache[p]=subprocess.check_output(['git','show',':'+p])
    return cache[p]
def check(p,digest):
    if p not in digests:digests[p]=hashlib.sha256(content(p)).hexdigest()
    assert digests[p]==digest,('staged identity differs',p)
def refs(v):
    if isinstance(v,dict):
        if 'path' in v and 'sha256' in v:check(v['path'],v['sha256'])
        for child in v.values():refs(child)
    elif isinstance(v,list):
        for child in v:refs(child)
index=json.loads(content(prefix+'attempts.json'));refs(index)
for row in index['configured_windows_graphs'].values():assert b'syspane_editor_form|' not in content(row['path']) and b'editor_form_linux.cpp' not in content(row['path'])
for n,digest in index['current_inputs'].items():check(n,digest)
for row in index['attempts']:
    v=json.loads(content(row['path']));assert v['source_base']==h['source_ref'] and v['exit']==row['exit']
    with zipfile.ZipFile(io.BytesIO(content(row['source_archive']['path']))) as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
    if 'ctest_log' in row:
        with zipfile.ZipFile(io.BytesIO(content(row['ctest_log']['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
def executed(row,profile,action):
    v=json.loads(content(row['path']));assert not v['exit'] and not v['source_changed_during_execution']
    delta={n:dict(executed=digest,current=index['current_inputs'][n]) for n,digest in v['source_inputs'].items() if index['current_inputs'][n]!=digest}
    if delta:assert delta==index['executed_input_differences'][profile+'-'+action]['files']
    for n in delta:assert n.endswith('.md') or (n=='tests/editor/native_arrange.py' and action!='arrange') or (profile.startswith('windows') and n=='source/interfaces/editor_form_linux.cpp')
    if action!='build':assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==index['artifacts'][profile][v['test_artifact']]['sha256']
for profile,final in index['final_runs'].items():
    for group,action in (('record','test'),('build','build')):executed(final[group],profile,action)
for action,row in index['regressions'].items():executed(row['record'],'linux-x64-gcc13',action)
original=index['originals'];fixed=json.loads(content(original['record']['path']))
with zipfile.ZipFile(io.BytesIO(content(original['archive']['path']))) as z:
    for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
    with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
        assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
        for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
        for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
        assert json.loads(z.read('result.json'))==json.loads(content(row['path']))
for family,row in index['final_native'].items():
    report=json.loads(content(row['path']));assert report['outcome']=='pass'
    assert report['executable_sha256']==index['artifacts']['linux-x64-gcc13'][row['artifact']]['sha256'];check(row['oracle'],report['oracle_sha256'])
    assert all(c.get('outcome',c.get('result'))=='pass' for c in report['cases']) and len(report['cases'])==row['cases']
    if family in ('EDITOR-CONTENT-PROPERTIES','EDITOR-SNAP','EDITOR-GROUP','EDITOR-ARRANGE','LARGE-COMMANDS','EDITOR-FORM'):
        archived=next(n for n in native if n['path']==row['path'])
        with zipfile.ZipFile(io.BytesIO(content(archived['archive']['path']))) as z:
            for case in report['cases']:
                if family=='LARGE-COMMANDS' and not case['case'].startswith('gui-'):continue
                raw=z.read(case['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==case['record_sha256'];detail=json.loads(raw)
                check('tests/configuration/large-command-cases.json' if family=='LARGE-COMMANDS' else 'tests/editor/content-properties-cases.json' if family=='EDITOR-CONTENT-PROPERTIES' else 'tests/editor/snap-cases.json' if family=='EDITOR-SNAP' else 'tests/editor/group-cases.json' if family=='EDITOR-GROUP' else 'tests/editor/arrange-cases.json' if family=='EDITOR-ARRANGE' else 'tests/editor/native-cases.json',detail['fixture_sha256'])
                check('tests/editor/native_content_properties.py' if family=='EDITOR-CONTENT-PROPERTIES' else 'tests/editor/native_snap.py' if family=='EDITOR-SNAP' else 'tests/editor/native_group.py' if family=='EDITOR-GROUP' else 'tests/editor/native_arrange.py' if family=='EDITOR-ARRANGE' else 'tests/editor/native_editor.py',detail['oracle_sha256'])
                if family in ('EDITOR-CONTENT-PROPERTIES','EDITOR-SNAP','EDITOR-GROUP','EDITOR-ARRANGE'):check('tests/editor/native_editor.py',detail['harness_sha256'])
                if family=='EDITOR-GROUP':check('tests/editor/group-overlap-cases.json',detail['overlap_fixture_sha256'])
                assert detail['executable_sha256']==index['artifacts']['linux-x64-gcc13']['syspane_editor_window']['sha256']
                if case['case'] in ('frozen-preview','wrong-group','wrong-commit','retain','gui-wrong-commit','wrong-content','retain-content'):assert case['fault_detected'] and detail['fault_detected']
verification=json.loads(content(prefix+'verification.json'));refs(verification);assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for group in ('tool_inputs','unchanged_old_contracts'):
    for n,digest in verification[group].items():check(n,digest)
for p in paths:
    if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value=dict(outcome='pass',staged_files=len(paths),verified_staged_file_hashes=len(digests),affected_runs={p:len(v['cases']) for p,v in index['final_runs'].items()},preserved_attempts=len(index['attempts']),native_archives=len(native),final_native_families=len(index['final_native']),unchanged_contract_fixture_files=len(verification['unchanged_old_contracts']),scope='Staged shared and native content properties, exact fixed inputs, original failures and successful native observations match their records. Full editions and remaining acceptance gates remain open.')
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass';jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')));(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))

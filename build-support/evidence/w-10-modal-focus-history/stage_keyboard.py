from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-modal-focus-';hp='build-support/evidence/keyboard-input-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_bytes());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
ps=r/'out/campaign/keyboard-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode());subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
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
for group in ('current_inputs','unchanged_source_contracts_fixtures'):
    for n,digest in index[group].items():check(n,digest)
for row in index['attempts']:
    v=json.loads(content(row['path']));assert v['source_base']==h['source_ref'] and v['exit']==row['exit']
    with zipfile.ZipFile(io.BytesIO(content(row['source_archive']['path']))) as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
    if 'ctest_log' in row:
        with zipfile.ZipFile(io.BytesIO(content(row['ctest_log']['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
expected={**index['current_inputs'],**{n:v['sha256'] for n,v in index['executed_helpers'].items()}}
for row in index['executed_helpers'].values():check(row['preserved_as']['path'],row['sha256'])
for row in index['final_runs'].values():
    v=json.loads(content(row['record']['path']));assert not v['exit'] and not v['source_changed_during_execution'];assert v['source_inputs']==expected
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==row['sha256']==index['artifacts'][row['artifact']]['sha256']
for original in index['originals']:
    fixed=json.loads(content(original['record']['path']))
    with zipfile.ZipFile(io.BytesIO(content(original['archive']['path']))) as z:
        for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
    with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
        assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
        for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
        for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
        assert json.loads(z.read('result.json'))==json.loads(content(row['path']))
upstream=json.loads(content(index['upstream']['record']['path']))
with zipfile.ZipFile(io.BytesIO(content(index['upstream']['archive']['path']))) as z:
    assert set(z.namelist())==set(upstream)
    for n,v in upstream.items():assert hashlib.sha256(z.read(n)).hexdigest()==v['sha256']
diagnostic_counts={};diagnostic_total=0
for row in index['diagnostics']:
    report=json.loads(content(row['path']));assert report['outcome']=='observed'
    helper,plan={'MODAL-FOCUS-DIAGNOSTIC':('modal_focus_probe.py','modal-focus-plan.json'),'MODAL-FOCUS-MINIMAL-DIAGNOSTIC':('modal_focus_probe_minimal.py','modal-focus-plan-v2.json'),'MODAL-FOCUS-ORDERED-DIAGNOSTIC':('modal_focus_probe_ordered.py','modal-focus-plan-v3.json')}[row['family']]
    check(prefix+'history/'+helper,report['probe_sha256']);check(prefix+'history/'+plan,report['plan_sha256'])
    original=json.loads(content(prefix+'history/'+plan))['original_source_archive']
    with zipfile.ZipFile(io.BytesIO(content(original))) as z:preserved_oracle=hashlib.sha256(z.read('tests/editor/native_layout_authoring.py')).hexdigest()
    diagnostic_counts[row['family']]={}
    archived=next(n for n in native if n['path']==row['path'])
    with zipfile.ZipFile(io.BytesIO(content(archived['archive']['path']))) as z:
        for case in report['cases']:
            raw=z.read(case['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==case['record_sha256']
            detail=json.loads(raw);assert detail['diagnostic']==case['diagnostic']
            assert detail['probe_sha256']==report['probe_sha256'] and detail['preserved_oracle_sha256']==preserved_oracle
            assert detail['executable_sha256']==index['artifacts']['syspane_editor_window']['sha256']
            counts=diagnostic_counts[row['family']];counts[case['diagnostic']]=counts.get(case['diagnostic'],0)+1;diagnostic_total+=1
            if row['family']=='MODAL-FOCUS-ORDERED-DIAGNOSTIC':
                if case['case'].endswith('-batched'):
                    assert case['diagnostic']=='observed_failure' and detail['stage']=='GROUP-FOCUS'
                    assert detail['focus_failure']['control']=='layout' and not detail['focus_failure']['focused']
                    trace=detail['input_trace'];at=detail['selection_observed']['at']
                    keys=[t['key'] for t in trace if 'key' in t and t['at']<at]
                    assert keys[-5:]==[65367,65360,65364,65364,65364]
                elif case['case'].endswith('-ordered'):assert case['diagnostic']=='ordered_pass'
assert diagnostic_total==24
assert diagnostic_counts['MODAL-FOCUS-ORDERED-DIAGNOSTIC']==dict(unchanged_pass_inconclusive=6,observed_failure=3,ordered_pass=3)
for family,row in index['final_native'].items():
    report=json.loads(content(row['path']));assert report['outcome']=='pass' and len(report['cases'])==row['cases']
    assert all(c.get('outcome',c.get('result'))=='pass' for c in report['cases'])
    archived=next(n for n in native if n['path']==row['path'])
    with zipfile.ZipFile(io.BytesIO(content(archived['archive']['path']))) as z:
        for case in report['cases']:
            if family=='LARGE-COMMANDS' and not case['case'].startswith('gui-'):continue
            raw=z.read(case['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==case['record_sha256'];detail=json.loads(raw)
            check('tests/editor/native_observation.py',detail['observation_helper_sha256'])
            assert detail['executable_sha256']==index['artifacts']['syspane_editor_window']['sha256']
            if case['case'] in ('wrong-layout','retain-layout','wrong-insert','retain-create','frozen-preview','wrong-group','wrong-commit','retain','gui-wrong-commit','wrong-content','retain-content','wrong-binding','retain-binding'):assert case['fault_detected'] and detail['fault_detected']
verification=json.loads(content(prefix+'verification.json'));refs(verification);assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for p in paths:
    if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value=dict(outcome='pass',staged_files=len(paths),verified_staged_file_hashes=len(digests),preserved_attempts=len(index['attempts']),native_archives=len(native),final_native_families=len(index['final_native']),final_native_cases=sum(x['cases'] for x in index['final_native'].values()),scope='Fixed expected scenes, ordered native input, preserved diagnostic failures and source/binary-bound native evidence. Specific layout-navigation cause established; earlier unrelated failures and full editions remain open.')
value.update(investigative_cases=diagnostic_total,diagnostic_outcomes=diagnostic_counts)
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass';jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')));(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))

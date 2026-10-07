from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-image-pipeline-';hp='build-support/evidence/image-pipeline-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_text());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/image-pipeline-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode())
subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
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
for n,digest in index['current_inputs'].items():check(n,digest)
for row in index['attempts']:
    v=json.loads(content(row['path']));assert v['source_base']==h['source_ref'] and v['exit']==row['exit']
    with zipfile.ZipFile(io.BytesIO(content(row['source_archive']['path']))) as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
    if 'ctest_log' in row:
        with zipfile.ZipFile(io.BytesIO(content(row['ctest_log']['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
for profile,final in index['final_runs'].items():
    for group in ('record','build'):
        v=json.loads(content(final[group]['path']));assert v['exit']==0 and v['source_inputs']==index['current_inputs'] and not v['source_changed_during_execution']
    v=json.loads(content(final['record']['path']));n='syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==index['artifacts'][profile][n]['sha256']
for name,original in index['originals'].items():
    inputs=json.loads(content(original['record']['path']))
    with zipfile.ZipFile(io.BytesIO(content(original['archive']['path']))) as z:
        assert set(z.namelist())==set(inputs)
        for n,digest in inputs.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
        if name=='fit-original':
            for n,digest in inputs.items():
                if n.startswith('tests/scene/'):check(n,digest)
        else:
            for n,digest in inputs.items():
                if n.startswith('tests/scene/image-cases/') and not n.endswith('native.json'):check(n,digest)
            n='tests/scene/image-cases/native.json';old=json.loads(z.read(n));current={c['name']:c for c in json.loads(content(n))}
            for c in old:assert c==current[c['name']],('original native expectation changed',c['name'])
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
    with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
        assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
        for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
        for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
        if 'path' in row:assert json.loads(z.read('result.json'))==json.loads(content(row['path']))
for family,row in index['final_native'].items():
    report=json.loads(content(row['path']));assert report['outcome']=='pass'
    artifact='SysPane.ImageWorker' if family=='IMAGE-DECODE' else 'SysPane.CommandProbe'
    key='worker_sha256' if family=='IMAGE-DECODE' else 'executable_sha256'
    assert report[key]==index['artifacts']['linux-x64-gcc13'][artifact]['sha256']
    if family=='IMAGE-DECODE':
        assert len(report['cases'])==54
        check('tests/scene/image_native.py',report['oracle_sha256']);assert all(c['outcome']=='pass' for c in report['cases'])
windows=index['windows_recovery']
with zipfile.ZipFile(io.BytesIO(content(windows['archive']['path']))) as z:
    assert set(z.namelist())==set(windows['files'])
    for n,digest in windows['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
    for n in windows['reports']:
        report=json.loads(z.read(n));assert report['outcome']=='pass' and report['executable_sha256']==index['artifacts']['windows-x64-gcc15']['SysPane.RecoveryProbe.exe']['sha256']
legacy=json.loads(content(prefix+'legacy-audit.json'));assert legacy['outcome']=='pass' and len(legacy['artifacts'])==18
for n,digest in legacy['verification_inputs'].items():check(n,digest)
check(prefix+'history/audit_image_pipeline_legacy.py',legacy['helper_sha256'])
verification=json.loads(content(prefix+'verification.json'));refs(verification)
assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for group in ('tool_inputs','unchanged_old_contracts'):
    for n,digest in verification[group].items():check(n,digest)
for p in paths:
    if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value={'outcome':'pass','staged_files':len(paths),'verified_staged_file_hashes':len(digests),'affected_runs':{p:len(v['cases']) for p,v in index['final_runs'].items()},
       'preserved_attempts':len(index['attempts']),'native_archives':len(native),'final_native_families':len(index['final_native']),
       'unchanged_contract_fixture_files':len(verification['unchanged_old_contracts']),
       'scope':'Staged source, fixed geometry/native oracles and attempt/reply archives match executed affected checks. Operational scene images, installed desktop, historical runtime and release qualification remain open.'}
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass'
jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')))
(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))

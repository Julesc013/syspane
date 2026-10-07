from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-image-pipeline-';hp='build-support/evidence/image-pipeline-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
shutil.copyfile(r/'out/campaign/image-pipeline-legacy-audit.json',r/(prefix+'legacy-audit.json'))
for name in ('finish_image_pipeline.py','finish_image_pipeline_checks.py','audit_image_pipeline_legacy.py','stage_image_pipeline.py','prepare_image_pipeline_checks.py','normalize_image_pipeline_inputs.py','image-input-normalization.json'):
    shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
jsonschema.validate(json.loads((r/'build-support/targets/linux-x64-gcc13.json').read_text()),json.loads((r/'spec/contracts/target-profile.schema.json').read_text()))
v['target_profile_schema_check']={'outcome':'pass','profile':{'path':'build-support/targets/linux-x64-gcc13.json','sha256':sha('build-support/targets/linux-x64-gcc13.json')},'schema':{'path':'spec/contracts/target-profile.schema.json','sha256':sha('spec/contracts/target-profile.schema.json')}}
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/scene/image_fit_oracle.py')};v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
    if not path.endswith('.json'):continue
    before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path)
    v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/native-chart-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Implement exact portable image orientation/fit, bounded isolated Linux PNG/JPEG/static-SVG decoding and nonblocking exact-child ownership before operational scene integration.',
    changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=[
        'Keep scene 0.3 image identities and existing document/wire contracts; operational image widgets remain explicitly unsupported pending resource, scene and policy integration.',
        'Use exact rational premultiplied bilinear contain/cover/stretch geometry and all eight EXIF orientations with independent Fraction expectations.',
        'Admit bounded static PNG/JPEG/SVG bytes before native decoding, remove unneeded compressed metadata and reject animation or external/embedded references.',
        'Pin installed Linux codecs/plugins, selected headers and kernel; require Landlock, seccomp and hard resource limits before parsing.',
        'Launch a held canonical worker ELF through Child with clean descriptors/environment; bound IPC and polling, enforce an independent owner deadline, require actual termination and permit one result take.',
        'Cancellation clears parent payloads, forbids later disclosure and retains exact-child cleanup ownership; scene admission and aggregate job/cache budgets remain the next boundary.',
        'Preserve original geometry/native expectations, the strict-compiler failed attempt and workspace-preflight rejection. Reclaim only verified archived duplicates without changing the 6 GiB allocation.',
        'Normalize two JSON files to repository LF rules without changing their values; repeat affected builds/checks against the exact final source bytes.'],
    checks=[
        {'name':f'Affected CTest runs: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'Linux decoder: 51 native media cases plus restriction, deadline and cancellation controls; child-supervision and Linux/Windows recovery regressions','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'18 historical PE/import/input artifact audits on the modern Windows host','outcome':'pass','evidence':prefix+'legacy-audit.json'},
        {'name':'180 fixed fit expectations; target/schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
        {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
        {'name':'Operational scene image identity/policy/erasure, Windows/Mac native images and historical OS qualification','outcome':'not_run','evidence':None}],
    next_step='Continue W-09 with resource/scene/policy-owned asynchronous ImageJob integration, aggregate job/cache/construction budgets and independent native image/alt-content erasure traces before enabling images. Complete native accessibility, localization, settings/editing, installed ownership/host activation and all five editions through the existing work graph.',
    limitations=[
        'The image pipeline is a prerequisite library/worker boundary. Operational SceneSurface image widgets remain disabled; decoding alone grants no disclosure authority.',
        'Native image decoding is qualified only in the pinned owned Linux development environment. The OS restrictions are not a general hostile-code sandbox claim.',
        'The static SVG/color profile is bounded and explicit; broader format/color-management features require additional contracts and evidence.',
        'Selected affected checks were run, not the full product suite. Original scene schemas/fixtures/wire contracts and prior evidence remain intact.',
        'Windows checks execute shared geometry and contemporary child recovery. Historical compiler execution and PE inspection occurred on modern Windows; historical Windows/Mac labs and platform floors remain unresolved.',
        'Two existing Windows symlink tool assertions remain skipped. W-09 and every full-edition release gate remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

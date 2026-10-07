from pathlib import Path
import hashlib,json,subprocess,sys,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-native-observation-';hp='build-support/evidence/native-observation-handoff.json';pending='--pending' in sys.argv
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not pending:
    v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
    unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
    schemas=json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout']);assert schemas['status']=='pass'
    v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
    budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
    index=json.loads((r/(prefix+'attempts.json')).read_bytes());assert sum(x['cases'] for x in index['final_native'].values())==136
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),objective='Distinguish unavailable native observations from absent text, state, interface and selection without weakening editor acceptance',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=['Preserve the package and original product inputs before investigation; freeze calibration expectations before execution.', 'Use explicit native wire replies, retain addresses only and bound read-only retries by existing deadlines.', 'Do not retry mutations, force held focus or widen the 200-ms erasure bound.', 'Preserve both diagnostic matrices and the stricter binding matrix failure; do not infer historical failure cause from later passing checks.', 'Keep production source/binaries and all five release tracks unchanged.'],
    checks=[dict(name='Seven observer calibrations and 129 fixed native regression cases',outcome='not_run' if pending else 'pass',evidence=prefix+'attempts.json'),dict(name='Historical intermittent live focus/interface cause',outcome='inconclusive',evidence=prefix+'native-index.json'),dict(name='Schema, fixtures, tooling and integrity',outcome='not_run' if pending else 'pass',evidence=prefix+'verification.json'),dict(name='Staged source/oracle/evidence identities',outcome='not_run',evidence=prefix+'staging.json'),dict(name='Complete native editions and historical/release qualification',outcome='not_run',evidence=None)],
    open_questions=['What caused the earlier intermittent native live focus/interface failures?', 'Which historical version/architecture floors and laboratories will qualify the complete editions?'],
    next_step='Close responsive/flow transforms and remaining property controls, then installed controller/catalog/policy ownership and scene-aligned entry/restoration. Preserve explicit X11/accessibility snapshots if focus failures recur; continue all five release tracks.',
    authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 objective; routine unprivileged work, commit and sync main.'],
    limitations=['Owned Linux ext4/Xvfb/D-Bus evidence is not installed editing, physical power-loss or historical qualification.', 'Historical focus-failure cause and convenience-API delay duration remain unproven.', 'Denied RPC service calibrates observer error handling, not product authorization policy.', 'Two existing Windows symlink tooling assertions remain skipped; no new Windows runtime checks were needed for this Linux observer-only correction.', 'Responsive/flow transforms, remaining properties, installed ownership, other adapters and all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and handoff.')

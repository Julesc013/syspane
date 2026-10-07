from pathlib import Path
import hashlib,json,subprocess,sys,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-modal-focus-';hp='build-support/evidence/keyboard-input-handoff.json';pending='--pending' in sys.argv
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not pending:
    v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
    unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
    schemas=json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout']);assert schemas['status']=='pass'
    v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
    budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
    index=json.loads((r/(prefix+'attempts.json')).read_bytes());assert sum(x['cases'] for x in index['final_native'].values())==157
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),objective='Acknowledge native keyboard navigation and activation before moving focus, with fixed acceptance outcomes',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=['Preserve the original keyboard oracle and three bounded diagnostic matrices, including failures and inconclusive passes.', 'Await each selected row/title within one three-second deadline and retain explicit focused-state assertions.', 'Restore keyboard button activation and await fixed aligned pixels before changing selection.', 'Keep production, product fixtures and all acceptance outcomes unchanged; do not generalize to unrelated historical failures.'],
    checks=[dict(name='157 native cases across ten fixed regression matrices',outcome='not_run' if pending else 'pass',evidence=prefix+'attempts.json'),dict(name='Specific layout input ordering experiment',outcome='not_run' if pending else 'pass',evidence=prefix+'native-index.json'),dict(name='Earlier unrelated live focus/interface causes',outcome='inconclusive',evidence=prefix+'native-index.json'),dict(name='Schema, fixtures, tooling and integrity',outcome='not_run' if pending else 'pass',evidence=prefix+'verification.json'),dict(name='Staged source/oracle/evidence identities',outcome='not_run',evidence=prefix+'staging.json'),dict(name='Complete native editions and historical/release qualification',outcome='not_run',evidence=None)],
    open_questions=['What caused the earlier intermittent native live focus/interface failures?', 'Which historical version/architecture floors and laboratories will qualify the complete editions?'],
    next_step='Close flow/container group transformations and remaining property controls, then installed controller/catalog/policy ownership and scene-aligned entry/restoration. Preserve explicit X11/accessibility snapshots if focus failures recur; continue all five release tracks.',
    authority_used=['user:foundation-native-campaign-2026-10-05','User-expanded complete SysPane 0.1.0 objective; routine unprivileged work, commit and sync main.'],
    limitations=['Owned Linux ext4/Xvfb/D-Bus evidence is not installed editing, physical power-loss or historical qualification.', 'The paired traces establish only this layout-navigation failure; earlier unrelated failures remain unproven.', 'An additional failed alignment run is retained; fixed pixels now acknowledge activation before focus moves.', 'Two existing Windows symlink tooling assertions remain skipped; no new Windows runtime checks were needed for this Linux oracle-only correction.', 'Flow/container group transformations, remaining properties, installed ownership, other adapters and all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and handoff.')

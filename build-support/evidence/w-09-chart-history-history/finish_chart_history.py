from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-chart-history-';hp='build-support/evidence/chart-history-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','out/campaign/audit_chart_history_legacy.py'],check=True)
shutil.copyfile(r/'out/campaign/chart-history-legacy-audit.json',r/(prefix+'legacy-audit.json'))
for name in ('finish_chart_history.py','finish_chart_history_checks.py','audit_chart_history_legacy.py','stage_chart_history.py'):
    shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')};v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
    if not path.endswith('.json'):continue
    before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path)
    v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/scene-content-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Implement bounded exact measured chart history, gaps, identity resets and latched chronology faults before native chart drawing.',
    changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=[
        'Keep the existing scene 0.3 settings and one shared scene library; no wire/schema change or native chart enablement.',
        'Observe every admitted singleton publication. Retain exact numeric types, original provenance and explicit continuity flags in a bounded inclusive measured window.',
        'Keep conflict/clock faults latched across pending selection. Invalid chronology cannot hide behind stale, retained or missing-current-clock state.',
        'Require the future native owner to authorize history-channel retention and clear on policy/resource/binding/lifetime changes.',
        'Archive the original interface, package and eleven families before production implementation, then preserve all three failing attempts and corrective changes.',
        'Run affected scene/dependency regressions on three toolsets, including Linux scalar/table components and historical PE controls; keep native chart and release qualification open.'],
    checks=[
        {'name':f'Affected CTest runs: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'18 historical PE/import/input artifact audits on the modern Windows host','outcome':'pass','evidence':prefix+'legacy-audit.json'},
        {'name':'Schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
        {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
        {'name':'Native chart geometry, history policy owner, accessibility and erasure','outcome':'not_run','evidence':None}],
    next_step='Close native chart axis/normalization/reduction, geometry and accessibility traces. Connect every-publication selector clock context, aggregate history budgets and explicit history-channel erasure in SceneSurface; run independent native pixels/accessibility fault controls. Continue image decoding, native editing/settings, installed ownership and all five editions.',
    limitations=[
        'This component is not an authorization engine or native renderer. Operational use requires the enclosing history-channel policy owner; chart painting remains disabled.',
        'Selected affected-component checks were run, not the full product suite. Prior comprehensive baseline evidence remains in its original records.',
        'Historical compiler execution and PE inspection occurred on modern Windows. No historical Windows or Mac OS X runtime qualification.',
        'Two existing Windows symlink tool assertions remain skipped. Historical/Mac lab and platform-floor questions remain unanswered.',
        'Previous native observer/content-command failure evidence and all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

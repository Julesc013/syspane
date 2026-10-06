from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-native-chart-';hp='build-support/evidence/native-chart-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
shutil.copyfile(r/'out/campaign/native-chart-legacy-audit.json',r/(prefix+'legacy-audit.json'))
for name in ('finish_native_chart.py','finish_native_chart_checks.py','audit_native_chart_legacy.py','stage_native_chart.py','prepare_native_chart_checks.py'):
    shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/scene/chart_plot_oracle.py')};v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
    if not path.endswith('.json'):continue
    before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path)
    v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/chart-history-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Implement exact portable chart geometry and policy-owned native Linux chart presentation with independently verified pixels, accessible point content and revocation.',
    changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=[
        'Keep existing scene 0.3 settings and shared scene/native rendering libraries; no wire/schema version change.',
        'Use exact binary64/uint64 projection, fixed one-pixel linear/step coverage and bounded mask union, with independent Fraction numeric expectations.',
        'SceneSurface owns authorized history retention, aggregate budgets and every-publication routing with current relevant producer clocks.',
        'Clear history on policy/resource/lifetime changes and expose discontinuities, truncation and latched faults through text and accessible point content.',
        'Preserve original oracles and all failures. Correct the pre-execution expiry fixture against the existing lease rule; expired attachments require fresh attachment/full state.',
        'Fix the failed unrelated-producer isolation case without changing relevant-selector incomplete-clock behavior.',
        'Keep the native observer deadline and deliberate old-pixel/name fault controls; archive raw captures before reclaiming duplicate output.',
        'Run affected shared checks on three toolsets and native Linux regressions. Keep installed desktop, historical runtime and complete-edition release gates open.'],
    checks=[
        {'name':f'Affected CTest runs: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'Linux chart/scalar/table/content external pixel and accessibility erasure; normal and two intentional fault controls each','outcome':'pass','evidence':prefix+'native-index.json'},
        {'name':'18 historical PE/import/input artifact audits on the modern Windows host','outcome':'pass','evidence':prefix+'legacy-audit.json'},
        {'name':'318 fixed numeric expectations; schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
        {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
        {'name':'Full native accessibility navigation, installed live chart and historical OS qualification','outcome':'not_run','evidence':None}],
    next_step='Continue W-09 with bounded pinned image decoding/rendering contracts, resource/policy ownership and independent native erasure traces. Complete native accessibility, localization, settings/editing, installed ownership/host activation and all five editions through the existing work graph.',
    limitations=[
        'Native charts were observed in owned Linux GTK/X11 windows on Xvfb/private D-Bus with public synthetic telemetry; no installed behind-icons, live-collector or Wayland qualification.',
        'Accessible names contain exact point/status data; complete native chart navigation/actions remain required.',
        'Selected affected checks were run, not the full product suite. Original scene schemas/fixtures/wire contracts and prior evidence remain intact.',
        'Windows checks execute shared geometry. Historical compiler execution and PE inspection occurred on modern Windows; historical Windows/Mac runtime labs and platform floors remain unresolved.',
        'Two existing Windows symlink tool assertions remain skipped. W-09 and every full-edition release gate remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-11-native-settings-';hp='build-support/evidence/native-settings-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_settings.py','finish_settings_checks.py','stage_settings.py'):
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
h=json.loads((r/'build-support/evidence/scene-inspector-handoff.json').read_text())
h.update(work_id='W-11',source_ref=index['source_base'],objective='Implement portable settings drafts and eleven native GTK controls through the shared transaction owner, preserving independently verified storage and current-policy results.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Continue W-11 using implemented authored/async/native-store prerequisites; retain full work-unit and edition completion gates.',
  'Generate initial native descriptor metadata from the canonical registry, preserving every existing ID, type, default, constraint and policy property.',
  'Keep coherent portable drafts, exact revisions and one active request; validate result scope/facts and reconcile original requests without resubmission.',
  'Use native search, controls, policy locks and explicit default/revert/reload actions; distinguish a built-in value from inheritance reset.',
  'Erase native authored values and held accessibility content on disclosure loss; prohibit implicit PRIMARY/CLIPBOARD publication before clipboard ownership is admitted.',
  'Preserve fixed expected values and the first native oracle; correct its concealed-result expectation with the original failed trace retained.',
  'Preserve callback delivery uncertainty and independently test a throw after enqueueing, followed by exact request retrieval.',
  'Require positive retained-value and premature-save fault detection and the unchanged 200 ms revocation deadline.',
  'Retain ordinary commands and the 6 GiB workspace allocation; reclaim only exact archived copies. A stalled read-only WSL Git comparison was interrupted before deletion and replaced with direct committed blob checks.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Eleven native settings modes and six existing native command/store families, with deliberate fault controls','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Fixed values, unchanged old contracts, schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed settings/editor, resource-aware routing, other native adapters and complete release qualification','outcome':'not_run','evidence':None}],
 next_step='Close and implement content-aware settings and W-10 native editor ownership against exact resource selections. Preserve independent preview/conflict/policy/cancel/undo/reconciliation outcomes, then connect installed scene/resource/policy/producer routing and native host activation. Keep other target tracks independent.',
 limitations=[
  'The GTK form is an embeddable component verified in owned Linux windows, not an installed settings application or complete edition.',
  'It currently emits resource-free command 0.2. Resource-backed installed scenes require existing content-aware command integration.',
  'Persistent layer reset, native editor, CLI/help, clipboard/export authority, full localization, human accessibility review and Windows/AppKit forms remain open.',
  'Native size/responsiveness limits and representative product performance remain unqualified.',
  'Affected checks were run, not the full product suite. Existing contract/schema/fixture JSON bytes remain unchanged.',
  'Both Windows suites ran on contemporary Windows; historical OS support, platform floors and labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. W-11 and every complete-edition release gate remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

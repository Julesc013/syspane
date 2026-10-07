from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-11-scene-inspector-';hp='build-support/evidence/scene-inspector-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_inspector.py','finish_inspector_checks.py','stage_inspector.py'):
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
h=json.loads((r/'build-support/evidence/scene-images-handoff.json').read_text())
h.update(work_id='W-11',source_ref=index['source_base'],objective='Expose exact policy-owned scene information in native Linux tree/table controls with stable scoped navigation and independently observed revocation.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Admit the initial W-11 inspector using implemented W-08/W-09 prerequisites; leave full work-unit and release completion open.',
  'Use a typed inspector audience on the existing SceneSurface, independent inspector/accessibility/history/resource grants, unchanged wire identity and the existing resource/image owner.',
  'Project exact typed chart points and authored hierarchy into bounded native rows keyed by full scoped identity, preserving selected objects, focused columns and user expansion.',
  'Snapshot summary information only on explicit request; clear native strings, stale references and snapshots on relevant authority/lifetime changes.',
  'Keep original expected content and fixtures unchanged; preserve pre-implementation package/expectations and the native runner/fixture before first execution.',
  'Correct plain-arrow expansion to the pinned GTK Shift-arrow binding with original failed key traces retained; preserve expected selection, disclosure and 200 ms revocation outcomes.',
  'Require positive retained-content and wrong-selection fault detection. Preserve the escaped invalid control and corrected real native selection path.',
  'Keep ordinary build/test commands and the unchanged 6 GiB workspace allocation; remove only hash-verified archived duplicates.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Seven independent inspector modes and five existing scene-erasure families, with deliberate fault controls','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Original fixed expected content; schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed controls, representative accessibility review, other native adapters and complete release qualification','outcome':'not_run','evidence':None}],
 next_step='Close and implement native settings/editing controls through the existing authored transaction API in W-11/W-10, preserving independent conflict/policy/cancellation/durable-result outcomes. Then connect installed scene/resource/policy/producer routing and native host activation; keep other target tracks independent.',
 limitations=[
  'The inspector is an embeddable GTK component verified in owned synthetic Linux windows, not an installed desktop edition or behind-icons placement.',
  'Settings/editing, clipboard/export authority, full localization, representative screen-reader review and Windows/Mac adapters remain open.',
  'Logical frame/model budgets do not qualify native allocation overhead, maximum-size responsiveness or product performance.',
  'Affected checks were run, not the full product suite. All prior contract/schema/fixture JSON bytes remain unchanged.',
  'Both Windows profile suites ran on contemporary Windows; no historical operating-system qualification follows. Platform floors and designated labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. W-11 and all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

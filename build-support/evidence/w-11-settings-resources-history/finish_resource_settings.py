from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-11-settings-resources-';hp='build-support/evidence/settings-resources-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_resource_settings.py','finish_resource_settings_checks.py','stage_resource_settings.py'):
 shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/configuration/settings_content_fixture.py')};v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
 if not path.endswith('.json'):continue
 before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path)
 v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/native-settings-handoff.json').read_text())
h.update(work_id='W-11',source_ref=index['source_base'],objective='Preserve exact resource selection, scene content and stored package bytes through native settings edits, policy transitions and restart.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Continue the existing W-11 draft/form with a trusted immutable resource context; keep the common transaction/storage owner authoritative.',
  'Use established settings-only command 0.3 for resource-bearing drafts, including unchanged scene 0.3; retain resource-free scene 0.2 compatibility.',
  'Resolve theme edits inside the admitted closure and preserve explicit scene overrides; no filesystem import or fallback from UI controls.',
  'Keep accepted/draft documents and resource snapshots together; reject malformed or dropped contexts atomically and retain unknown request identity.',
  'Enforce content.select and resource capabilities; erase local catalog/resource references on disclosure loss and require a fresh complete reload.',
  'Independently compare selected documents, resource indexes and every package/asset byte with unavailable import fallback; detect deliberately substituted selection.',
  'Preserve original literal values and assets before implementation; exact serialized pins were archived after draft edits began, before resource tests executed.',
  'Keep both initial failures: strict fixture indentation and a test-owned catalog reference. Correct the fixture without weakening warnings or release/erasure requirements.',
  'Keep the 6 GiB allocation and ordinary preflights; reclaim only 27 identical committed source-archive copies.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Eighteen independent native settings modes including resource persistence/restart and three deliberate controls','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Fixed resource generator, unchanged old contracts, schema/fixture/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Complete native editor, installed routing, other native adapters and complete release qualification','outcome':'not_run','evidence':None}],
 next_step='Close and implement W-10 shared editing draft/typed commands, undo/redo, previews, Apply/Cancel and conflict/reconciliation against exact resource selections. Connect a native interactive surface with keyboard alternatives and the existing independent escape owner, then installed scene/resource/policy/producer routing. Keep other target tracks independent.',
 limitations=[
  'The GTK controls remain embeddable owned-lab components, not an installed application or complete edition.',
  'The trusted host supplies the admitted catalog/selection. Preset/import UI, persistent inheritance reset, native editor and installed ownership remain required.',
  'Clipboard/export, full localization, representative human accessibility, maximum-size responsiveness and other native forms remain open.',
  'Existing scene/schema/fixture JSON bytes and release acceptance criteria remain unchanged; affected checks are not a full product qualification suite.',
  'Both Windows toolchain checks ran on contemporary Windows; historical version floors and designated labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. Every complete-edition release gate remains open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

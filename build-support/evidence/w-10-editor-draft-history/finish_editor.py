from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-editor-draft-';hp='build-support/evidence/editor-draft-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_editor.py','finish_editor_checks.py','stage_editor.py','reclaim_editor_copies.py','reclaim_editor_small_copies.py','reclaim_editor_smoke.ps1','editor-native-reclamation.json','editor-native-small-reclamation.json','editor-smoke-reclamation.json'):
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
h=json.loads((r/'build-support/evidence/settings-resources-handoff.json').read_text())
h.update(work_id='W-10',source_ref=index['source_base'],objective='Implement typed atomic scene drafts, stable selection, bounded undo/redo and resource-aware Apply using the existing transaction owner.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Compose the existing SettingsDraft transaction/resource/result owner; add only its private validated scene staging path.',
  'Keep typed editing operations local and emit one existing scene.replace with the appropriate command version.',
  'Preserve exact package/preset selection, scene identity, untouched extensions and parent-local monitor/layout intent.',
  'Prepare and preserve twelve full expected scenes independently before implementation; retain their exact bytes.',
  'Bound history at 64 entries and 8 MiB canonical scene/selection JSON; preserve the accepted baseline and recheck policy on undo/redo.',
  'Keep valid large local drafts intact when the existing 16 KiB command envelope rejects Apply; larger-scene transport remains required.',
  'Preserve the initial strict test-indentation compile failure and preflight build-reservation stop.',
  'Keep the 6 GiB allocation; reclaim only verified duplicate source/capture files and archived extracted smoke payloads from resolved owned roots.',
  'Use native settings only as regression evidence for the shared owner; no native editor qualification is claimed.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Eighteen existing independent native settings regression modes including deliberate controls','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Fixed resource generator, unchanged existing contracts/fixtures, schema/integrity checks and 58 tooling passes with two existing Windows skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Native editor, complete authoring/transport, installed routing, all platform editions and release qualification','outcome':'not_run','evidence':None}],
 next_step='Connect the shared editor draft to an ordinary native interactive surface with the existing independent escape owner before admission. Independently verify pixels, selection, mouse/keyboard operations, preview, Apply/Cancel, topology and native release. Close larger-scene wire support and remaining authoring contracts; continue installed desktop/resource/policy routing and independent platform tracks.',
 limitations=[
  'The editor draft creates no native surface and is not an installed application or complete edition.',
  'Current commands retain the 16 KiB ceiling despite the 256 KiB scene bound; oversized Apply rejects while preserving the local draft/history.',
  'Persistent lock/visibility/typography contracts, clipboard, snap/align/distribute controls, recovery drafts and complete property panels remain required.',
  'Native editing/independent escape integration, responsiveness/accessibility and Windows/AppKit adapters remain required.',
  'Both Windows toolchain suites ran on contemporary Windows; historical floors and designated labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. Every complete-edition release gate remains open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

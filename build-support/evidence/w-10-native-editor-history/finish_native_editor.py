from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-native-editor-';hp='build-support/evidence/native-editor-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_native_editor.py','finish_native_editor_checks.py','stage_native_editor.py'):
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
h=json.loads((r/'build-support/evidence/editor-draft-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Connect the shared scene draft to a native GTK editor, real persistence and independent escape, with external pixel/input/storage/disclosure checks.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Reuse EditorDraft, SceneSurface, the common asynchronous command owner and coherent resource store; create no parallel mutation path.',
  'Use resolved geometry and stable IDs for pointer/keyboard editing; resolve current geometry before accepting another queued key.',
  'Keep buffered property edits atomic and retain them across topology changes; select new roots after native duplication.',
  'Preserve original literal scenes, resource inputs, expected outputs and timing bounds; retain all compile/native/preflight failures.',
  'Extract the existing restricted native text control for both settings and editor, retaining no-export behavior and bounded input.',
  'Exercise the actual editor under the existing separate recovery owner, with parent lifetime across exec and admission before mapping.',
  'Keep complete editions, installed entry, remaining authoring controls and larger-scene transport as open gates.',
  'Raise the bounded development allocation to 7 GiB after a preserved reservation stop and verified duplicate reclamation; product budgets remain unchanged.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Twenty independent native editor/persistence/disclosure/recovery cases, including three deliberate faults','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Eighteen existing native settings modes, nine original exit cases, and eleven renderer/inspector/erasure CTest entries','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Fixed fixtures, unchanged existing contracts, schema/integrity checks and 58 tooling passes with two existing Windows skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed complete editors, all platform editions and release qualification','outcome':'not_run','evidence':None}],
 next_step='Close versioned larger-scene command support and remaining authoring/property contracts. Connect installed controller/catalog/policy ownership and scene-aligned desktop entry/restoration with independent escape before mapping. Continue native adapter and historical qualification tracks independently.',
 limitations=[
  'Owned Xvfb/DBus native component evidence does not qualify installed desktop editing or any complete edition.',
  'The 256 KiB local scene contract still exceeds the existing 16 KiB command ceiling; oversized Apply explicitly rejects with the draft retained.',
  'Snap/grid/guides, align/distribute, complete binding/content/theme/group panels, lock/visibility/typography and recovery drafts remain required.',
  'Maximum-size responsiveness, full localization, clipboard authority, representative accessibility and other native adapters remain unqualified.',
  'Both Windows toolchain suites ran on contemporary Windows; historical floors and designated labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. Every complete-edition release gate remains open.'])
assert len(index['regressions']['surface']['cases'])==11
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contracts/fixtures:',len(v['unchanged_old_contracts']))

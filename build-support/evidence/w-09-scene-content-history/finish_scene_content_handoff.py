from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-scene-content-';hp='build-support/evidence/scene-content-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
 if not path.endswith('.json') or path=='spec/fixtures/catalog.json':continue
 before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old schema/fixture changed',path)
 v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['full_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/table-handoff.json').read_text())
h.update(work_id='W-09',source_ref=index['source_base'],objective='Carry explicit versioned widget content through migration, resource validation, negotiated transactions, native coherent recovery and text/label presentation.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'Preserve every older schema and fixture byte. Scene 0.3 and command 0.4 introduce typed content and explicit version negotiation.',
 'Migrate by validated copy. Refuse to invent legacy image/chart meaning; preserve extensions and settings-only edits to new documents.',
 'Resolve images by exact manifest pin, asset path and digest inside the immutable closure. Require scene.content and current resource policy at publication/presentation.',
 'Treat chart settings and image bytes as authored content only. No native chart or decoder capability is claimed.',
 'Use bodies for visible/accessible text, labels for table headers and label-plus-field identity for accessible cells.',
 'Keep original six shared families and storage oracle archived; add Unicode/required-feature/capability cases and independent native presentation controls without weakening prior oracles.',
 'Preserve raw native evidence and source archives. Verify captured bytes before releasing redundant owned raw RGB files.',
 'Run complete development suites on three profiles, preserve historical-toolset limitations and leave all full editions open.'],
 checks=[
 {'name':f'Complete development suites: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Six shared content families, 34 native storage cases, 17 table and 22 scalar families; three native erasure experiments with deliberate fault controls','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'18 historical PE/import/input artifact audits; modern Windows execution only','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Schema/fixture/navigation/integrity checks; 58 passing tooling tests and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Final staged source inputs, original oracles, native archives, artifacts and old-contract identities','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Native chart/image rendering, full accessibility/editor/host integration and complete editions','outcome':'not_run','evidence':None}],
 next_step='Close bounded chart sampling/decimation, gap/epoch and native accessibility traces; implement native charts. Close decoder/reference/animation/resource budgets before image rendering. Continue native editing/settings, installed ownership, desktop integration/recovery and all five release tracks.',
 limitations=[
 'Native presentation and resource-recovery evidence is Linux-only. Synthetic owned GTK/X11/AT-SPI windows do not qualify behind-icons placement or installed ownership.',
 'Opaque bytes declared as PNG verify pinning and coherent resource storage, not media decoding. No chart or image renderer is enabled.',
 'Historical-toolset tests run on modern Windows; no Windows 9x, XP/7 or Mac OS X runtime compatibility claim.',
 'Existing observer/content-command timeout evidence remains preserved; subsequent passing runs do not diagnose or erase it.',
 'Two existing Windows symlink tool assertions remain skipped. Historical/Mac labs, platform floors and all release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Content handoff validated;',totals,'; old contracts unchanged:',len(v['unchanged_old_contracts']))

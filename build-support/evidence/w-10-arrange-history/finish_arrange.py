from pathlib import Path
import hashlib,json,subprocess,sys,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-arrange-';hp='build-support/evidence/arrange-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
pending='--pending' in sys.argv
if not pending:
 v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
 unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
 validation=json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout']);assert validation['status']=='pass'
 v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
 v['preserved_spec_failure']={'path':prefix+'history/arrange-verification-failure.json','sha256':sha(prefix+'history/arrange-verification-failure.json'),'reason':'The standalone specification disallows links escaping its bundle; repository evidence references were changed to explicit repository paths without changing validation rules.','original_document':{'path':prefix+'history/arrange-handoff-before-link-fix.md','sha256':sha(prefix+'history/arrange-handoff-before-link-fix.md')}}
 v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/configuration/settings_content_fixture.py')}
 v['unchanged_old_contracts']={}
 for p in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
  if not p.endswith('.json') or p=='spec/fixtures/catalog.json':continue
  before=subprocess.check_output(['git','show','HEAD:'+p]);assert before==(r/p).read_bytes(),('old contract changed',p);v['unchanged_old_contracts'][p]=hashlib.sha256(before).hexdigest()
 budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
 index=json.loads((r/(prefix+'attempts.json')).read_bytes());assert all(len(x['cases'])==94 for x in index['final_runs'].values())
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/large-commands-handoff.json').read_bytes())
h.update(work_id='W-10',source_ref='62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1',objective='Add deterministic fixed-base alignment and spacing to shared drafts and native controls, preserving exact independent geometry, pixel and storage evidence.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Keep existing scene, command, storage, policy and resource ownership; add typed in-process operations through EditorDraft.',
  'Freeze complete expected scenes before implementation; use 1/64-DIP arithmetic, ties away from zero, ceiling extents and exact untouched properties.',
  'Require disjoint siblings and equal authored display assignment; ownership order breaks stable-sort ties.',
  'Equal spacing preserves exact endpoints and rejects negative gaps; distribute integer remainders to the first gaps.',
  'Native controls recheck active fixed-base geometry and metric expansion before changing the shared draft.',
  'Use actual native controls, pixels and stored documents; detect frozen previews and deliberately altered commits.',
  'Apply each final native sensitivity state once so ordinary repaints preserve held keyboard activation; prove with a previously failing 160 ms held-key case.',
  'Preserve compiler, selection, accessibility-observer timeout and reference-frame failures; cache only stable control references and await independently observed initial painting without changing frozen behavior or deadlines.',
  'Keep remaining authoring, installed ownership, other native adapters, historical qualification and all complete-edition gates open.'],
 checks=[
  {'name':'94 affected CTest entries on each of three development toolchains','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'},
  {'name':'14 native arrangement cases, 20 native editor regressions and 24 complete-scene/storage/IPC cases','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'},
  {'name':'Schema/fixture and integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'not_run' if pending else 'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged source, original oracles, artifact and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed desktop editions, historical native qualification and full release acceptance','outcome':'not_run','evidence':None}],
 next_step='Close snap/grid/guides, grouping and remaining authoring/property contracts, then connect installed controller/catalog/policy ownership to scene-aligned entry/restoration with independent escape. Continue other native and historical qualification tracks independently.',
 limitations=[
  'Owned Linux ext4/Xvfb/DBus checks do not qualify installed desktop editing, physical power-loss durability or a complete edition.',
  'Responsive arrangement, snapping/grid/guides, grouping, binding/content/theme panels, locking/visibility/typography, clipboard authority and recovery drafts remain required.',
  'Full accessibility/localization/performance and other native adapters remain open.',
  'Both Windows toolchains ran on contemporary Windows; historical floors and designated native labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped; all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and sealed handoff; staged identity check remains.')

from pathlib import Path
import hashlib,json,subprocess,sys,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-content-properties-';hp='build-support/evidence/content-properties-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
pending='--pending' in sys.argv
if not pending:
    v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
    unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
    validation=json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout']);assert validation['status']=='pass'
    v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
    v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/configuration/settings_content_fixture.py')}
    v['unchanged_old_contracts']={}
    for p in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
        if not p.endswith('.json') or p=='spec/fixtures/catalog.json':continue
        before=subprocess.check_output(['git','show','HEAD:'+p]);assert before==(r/p).read_bytes(),('old contract changed',p);v['unchanged_old_contracts'][p]=hashlib.sha256(before).hexdigest()
    budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
    index=json.loads((r/(prefix+'attempts.json')).read_bytes());assert all(len(x['cases'])==111 for x in index['final_runs'].values())
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/snap-handoff.json').read_bytes())
h.update(work_id='W-10',source_ref='ce7731133431029d72d6d39f149d59f4663e66af',objective='Add bounded native content and scene-theme buffers through existing atomic draft, resource, policy and persistence owners',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Freeze full authored scenes, resource bytes/pins and expected content outcomes before production changes.',
  'Preserve original bindings when reordering table labels; keep complete original-column permutations.',
  'Project strict finite numeric input and serialize only the active chart-axis mode.',
  'Enumerate exact immutable resource choices; retain theme resolver and current-policy validation.',
  'Keep modal input outside authored history; apply one atomic batch, preserve no-op/cancel previews, and erase native text/choice models on policy/owner changes.',
  'Preserve compilation, fixture-channel, native observation and any product failures. Final native checks retain original expected scenes and independently observe actual inputs, pixels, accessibility and storage.',
  'Record the native laboratory display as 640x560 logical DIP at 3/4 scale; maintain telemetry heartbeats at 500 ms.',
  'Preserve the isolated held-focus failure and diagnostic-only passing rerun; construct the modal window only on explicit Content entry and rerun the complete native matrix. The original focus failure cause was not established.',
  'Free only verified duplicates of committed native evidence within the unchanged 7 GiB workspace budget.'],
 checks=[
  {'name':'111 affected CTest entries on each of three development toolchains','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'},
  {'name':'15 native content, 13 snapping, 11 grouping, 14 arrangement, 20 editor and 24 complete-scene/storage/IPC cases','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'},
  {'name':'Schema/fixture and integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'not_run' if pending else 'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged source, original oracles, artifact and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed desktop editions, historical native qualification and full release acceptance','outcome':'not_run','evidence':None}],
 next_step='Close binding authoring, non-text insertion, responsive/flow container transforms and remaining property contracts, then connect installed controller/catalog/policy ownership to scene-aligned entry/restoration with independent escape. Continue other native and historical qualification tracks independently.',
 limitations=[
  'Owned Linux ext4/Xvfb/DBus checks do not qualify installed desktop editing, physical power-loss durability or a complete edition.',
  'Responsive arrangement/container transforms, binding authoring and remaining property panels, lock/visibility/typography, clipboard authority and recovery drafts remain required.',
  'Full accessibility/localization/performance and other native adapters remain open.',
  'Both Windows toolchains ran on contemporary Windows; historical floors and designated native labs remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped; all complete-edition release gates remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and sealed handoff; staged identity check remains.')

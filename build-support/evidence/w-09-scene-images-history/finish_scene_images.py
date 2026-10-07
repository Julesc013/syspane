from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-scene-images-';hp='build-support/evidence/scene-images-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
shutil.copyfile(r/'out/campaign/scene-images-legacy-audit.json',r/(prefix+'legacy-audit.json'))
for name in ('finish_scene_images.py','finish_scene_images_checks.py','audit_scene_images_legacy.py','stage_scene_images.py','prepare_scene_images_staging.py','scene_images_external_flow.py'):
    shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
for p in (r/'out/campaign').glob('scene-images-external-*.json'):shutil.copyfile(p,r/(prefix+'history')/p.name)
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
jsonschema.validate(json.loads((r/'build-support/targets/linux-x64-gcc13.json').read_text()),json.loads((r/'spec/contracts/target-profile.schema.json').read_text()))
v['target_profile_schema_check']={'outcome':'pass','profile':{'path':'build-support/targets/linux-x64-gcc13.json','sha256':sha('build-support/targets/linux-x64-gcc13.json')},'schema':{'path':'spec/contracts/target-profile.schema.json','sha256':sha('spec/contracts/target-profile.schema.json')}}
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/scene/image_surface_oracle.py')};v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
    if not path.endswith('.json'):continue
    before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path)
    v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_text());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/image-pipeline-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Connect asynchronous native image decoding to immutable scene resources, current policy, bounded ownership and externally observed pixels/accessible names; honor the existing content digest ceiling in persistence.',
 changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
  'Keep existing scene, configuration, wire and resource identities; the application supplies the trusted worker executable separately from authored content.',
  'Resolve exact immutable package/path/digest references, share identical decodes, cap encoded admission/cache/construction separately and retain one running-or-stopping slot until actual reaping.',
  'Keep pending and failed image extents and explicit accessible status while other widgets and chart history update; apply exact fit/alpha/rational scaling to ready images.',
  'Invalidate caches, queues and even completed-unobserved results on policy/resource/scene/lifetime changes; drain cancellation nonblockingly after close.',
  'Latch whole-scene failures without retry storms and preserve terminal closed state if native clearing fails during decoded-capacity rejection.',
  'Repair content hashing to the already-declared 16 MiB ceiling using fixed blocks while preserving the separate 1 MiB document/request limit; verify large durable resource recovery.',
  'Preserve fixed pixel/digest expectations, original fixtures, failed attempts and explicit fixture/compiler corrections. Retain the 200 ms native revocation criterion and deliberate erasure faults.',
  'Use final artifacts to bind six earlier resource-family results whose executable and oracle identities remained unchanged by the later rendering-only correction; do not claim their entire earlier source snapshot is the final checkout.',
  'Reclaim only hash-verified archived duplicates under the unchanged 6 GiB workspace allocation.'],
 checks=[
  {'name':f'Affected CTest: Linux {totals["linux-x64-gcc13"]}, Windows {totals["windows-x64-gcc15"]}, historical-toolset host {totals["windows-x86-v141-xp"]}','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'Five external scene erasure families, six native content/configuration families including large-resource restart, decoder and child-supervision/regression evidence','outcome':'pass','evidence':prefix+'attempts.json'},
  {'name':'18 historical PE/import/input artifact audits on the modern Windows host','outcome':'pass','evidence':prefix+'legacy-audit.json'},
  {'name':'Six fixed image fit expectations; target/schema/fixture/navigation/integrity checks; 58 tooling passes and two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
  {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
  {'name':'Installed image routing, full native accessibility/editor/performance and historical OS/release qualification','outcome':'not_run','evidence':None}],
 next_step='Continue W-09 through the existing graph with full native accessibility/navigation and editing, then installed scene/resource/policy/producer routing and externally observed host activation. Preserve independent Windows, X11, Wayland, historical and Mac tracks and complete edition/package gates.',
 limitations=[
  'Native scene images are qualified in owned synthetic Linux component windows, not an installed behind-icons desktop edition.',
  'The application must supply the trusted pinned worker, current resource closure and policy. Other platform image adapters and installed ownership remain open.',
  'Logical payload budgets do not bound allocator/native-library overhead; maximum-size rendering responsiveness and product performance remain unqualified.',
  'Selected affected checks were run, not the full product suite. Original schema/fixture identities and earlier evidence remain unchanged.',
  'Windows tests cover shared behavior and contemporary child recovery. Historical compiler tests and PE inspection ran on modern Windows; historical Windows/Mac labs and platform floors remain unresolved.',
  'Two existing Windows symlink tooling assertions remain skipped. W-09 and every full-edition release gate remain open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h)
print('Handoff validated;',totals,'; unchanged contract/fixture files:',len(v['unchanged_old_contracts']))

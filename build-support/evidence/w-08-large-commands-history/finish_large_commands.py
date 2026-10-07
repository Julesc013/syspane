from pathlib import Path
import hashlib,json,shutil,subprocess,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-08-large-commands-';hp='build-support/evidence/large-commands-handoff.json'
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for name in ('finish_large_commands.py','stage_large_commands.py'):shutil.copyfile(r/'out/campaign'/name,r/(prefix+'history')/name)
v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
validation=json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout']);assert validation['status']=='pass'
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')}
v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/configuration/settings_content_fixture.py')}
v['unchanged_old_contracts']={}
for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
    if not path.endswith('.json') or path=='spec/fixtures/catalog.json':continue
    before=subprocess.check_output(['git','show','HEAD:'+path]);assert before==(r/path).read_bytes(),('old contract changed',path);v['unchanged_old_contracts'][path]=hashlib.sha256(before).hexdigest()
v['preserved_failure']={'path':prefix+'history/large-commands-verification-failure.json','sha256':sha(prefix+'history/large-commands-verification-failure.json'),'reason':'The schema-identity validator initially recognized only version suffixes 0.2/0.3/0.4; add 0.5 explicitly and rerun validation/tooling without changing the frozen schema.'}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
index=json.loads((r/(prefix+'attempts.json')).read_bytes());totals={p:len(x['cases']) for p,x in index['final_runs'].items()}
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
h=json.loads((r/'build-support/evidence/native-editor-handoff.json').read_bytes())
h.update(work_id='W-08',source_ref=index['source_base'],objective='Carry full authored scenes through negotiated commands, bounded admission, native Apply and coherent exact-request recovery.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
    decisions=[
        'Preserve command 0.2/0.3/0.4 and scene limits; add command 0.5, a 320 KiB body and independently validated wrapper headroom.',
        'Require exact document/features/frame negotiation and existing current-policy/resource authority before admission.',
        'Retain the 16 MiB ledger with original-body-plus-4-KiB reservation, exact replay and existing expiry; 50 maximum bodies fit.',
        'Use explicit draft/preset opt-in; never rewrite an unresolved request when reconnecting.',
        'Version Linux manifests to 0.3 and store the exact original request in a separately hashed private file; preserve old formats and coherent fallback.',
        'Freeze literal multibyte/escaped scenes and expected limits before implementation; preserve compiler, native observer and schema-tool failures.',
        'Observe actual stalled native worker state before cancellation, native process exit before replacement and independent scene bytes after commit.',
        'Keep installed ownership, remaining authoring, native adapters, historical qualification and complete editions open.'],
    checks=[
        {'name':'88 affected CTest entries on each of three development toolchains','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'24 native complete-scene cases: resource-free/resources, exact bytes, interrupted publication, corruption, IPC supervision and GTK','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'Six existing native storage/content/IPC families, 20 native editor cases and 18 settings cases','outcome':'pass','evidence':prefix+'attempts.json'},
        {'name':'Schema/fixture and integrity checks; 58 tooling tests passed, two existing Windows symlink skips','outcome':'pass','evidence':prefix+'verification.json'},
        {'name':'Final staged input and evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
        {'name':'Installed desktop editions, historical target qualification and full release acceptance','outcome':'not_run','evidence':None}],
    next_step='Close remaining authoring/property contracts and connect installed controller/catalog/policy ownership to scene-aligned editor entry/restoration, with independent escape before mapping. Continue other native adapter and historical qualification tracks independently.',
    limitations=[
        'Private Linux ext4/Xvfb/DBus experiments do not qualify installed desktop editing, power-loss durability or a complete edition.',
        'Snap/grid/guides, align/distribute, complete binding/content/theme/group panels, lock/visibility/typography, clipboard authority and recovery drafts remain required.',
        'Maximum-size performance qualification, representative accessibility/localization and Windows/AppKit adapters remain open.',
        'Both Windows toolchains were exercised on contemporary Windows; historical floors and native labs remain unresolved.',
        'Two existing Windows symlink tooling assertions remain skipped; every complete-edition release gate remains open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
print('Handoff validated;',totals,'; preserved old schema/fixture bytes:',len(v['unchanged_old_contracts']))

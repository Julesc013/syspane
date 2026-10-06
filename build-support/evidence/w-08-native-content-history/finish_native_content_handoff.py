from pathlib import Path
import hashlib,json,subprocess
import jsonschema
r=Path.cwd();prefix='build-support/evidence/w-08-native-content-';hp='build-support/evidence/native-content-handoff.json';sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((r/(prefix+'verification.json')).read_text());assert all(c['exit']==0 for c in v['checks'])
unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 58 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py')}
budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0
v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
index=json.loads((r/(prefix+'attempts.json')).read_text());assert len(index['full_runs'])==3
h=json.loads((r/'build-support/evidence/content-resolution-handoff.json').read_text())
h.update(source_ref=index['source_base'],objective='Compose retained content preparation with authenticated native commands and exact supervised controller replacement.',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=[
 'For the exact current content selection, resolve candidate resources solely from the retained original packages. Reload the store selection on every preparation.',
 'Resolve other selections solely from one configured import-loader result; never merge catalogs or fall back from invalid retained candidates.',
 'Add content-catalog 0.1 with bounded explicit package child basenames and no policy authority; use the existing private no-follow Linux reader on the transaction worker.',
 'Compose the resource provider with the existing AsyncCommands/Sessions/store/supervisor. Preserve command 0.3 negotiation, policy rechecks, framing, argument limits and transaction deadline.',
 'Forward explicit catalog or retained-only configuration to exact replacement children. Reconcile original outcomes and permit further edits without original imports.',
 'Observe resource-write and durable hangs independently; require exact SIGKILL/pidfd exit proof before accepting replacement, and preserve orphaned generations.',
 'Preserve native oracle failures. Correct a syntax boundary, admit the two existing external-SIGKILL observation orders and follow the existing policy-hidden receipt contract.',
 'Reclaim only duplicate ignored cached attempt directories after comparing every byte with unchanged committed evidence; preserve the audit.',
 'Keep W-08 and all five full release tracks open; installed ownership, decoding, native controls and visible activation remain required.'],
 checks=[
 {'name':'Initial native oracle syntax, signal observation ordering and policy receipt expectation failures','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Full suites: 170 Linux, 152 Windows, 139 historical-toolset entries on the modern host','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Nine supervised native content cases and existing resource/content/storage/command/reconciliation/supervision families','outcome':'pass','evidence':prefix+'attempts.json'},
 {'name':'Seventeen historical PE/header/import and actual linker-input audits','outcome':'pass','evidence':prefix+'legacy-audit.json'},
 {'name':'Specification/schema/generation/integrity and 56 passing tooling tests, two existing skips','outcome':'pass','evidence':prefix+'verification.json'},
 {'name':'Staged byte identity, archived attempts and native/artifact bindings','outcome':'pass','evidence':prefix+'staging.json'},
 {'name':'Installed ownership, media decoding, native controls and visible activation','outcome':'not_run','evidence':None},
 {'name':'Historical guest execution, non-Linux resource persistence and all complete native desktop releases','outcome':'not_run','evidence':None}],
 next_step='Close installed store/controller/policy ownership, admitted media preparation and native settings/direct editing with actual activation and recovery. Continue all five release tracks.',
 limitations=['Finite Linux IPC/ext4 native content composition and shared provider only. No installed product or release qualification.',
 'Native fixtures use typed laboratory policy/capability authority and explicit private catalogs. Archive discovery/import, media decoding and activation remain open.',
 'Complete configuration layers, resets, tombstones and three-way updates remain open. Command 0.3 retains its existing 16 KiB ceiling.',
 'Native process interruptions do not establish power-loss durability, arbitrary-filesystem support or visible activation.',
 'Historical-toolset execution on the modern Windows host does not qualify historical Windows behavior. Non-Linux native storage/supervision remains open.',
 'Two existing Windows symlink assertions remain skipped. No privileged operation, user desktop/VM operation or public release occurred.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_text()));write(hp,h);print('Native content handoff schema validated; workspace inspection passed.')

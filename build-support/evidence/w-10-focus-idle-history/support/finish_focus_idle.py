from pathlib import Path
import hashlib,json,subprocess,sys,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-focus-idle-';hp='build-support/evidence/focus-idle-handoff.json';pending='--pending' in sys.argv
sha=lambda p:hashlib.sha256((r/p).read_bytes()).hexdigest()
def write(p,v):(r/p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
if not pending:
 v=json.loads((r/(prefix+'verification.json')).read_bytes());assert all(c['exit']==0 for c in v['checks'])
 unit=next(c for c in v['checks'] if 'unittest' in c['command']);assert 'Ran 60 tests' in unit['stderr'] and 'OK (skipped=2)' in unit['stderr']
 assert json.loads(next(c for c in v['checks'] if '--schemas' in c['command'])['stdout'])['status']=='pass'
 v['sealed_specification']={'path':'spec/checksums.json','sha256':sha('spec/checksums.json')};v['tool_inputs']={p:sha(p) for p in ('spec/tools/specctl.py','spec/tools/tests/test_specctl.py','tests/configuration/settings_content_fixture.py','build-support/generate_authored_schemas.py')};v['unchanged_old_contracts']={}
 for p in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','spec/contracts','spec/fixtures'],text=True).splitlines():
  if not p.endswith('.json'):continue
  before=subprocess.check_output(['git','show','HEAD:'+p]);assert before==(r/p).read_bytes();v['unchanged_old_contracts'][p]=hashlib.sha256(before).hexdigest()
 budget=subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','inspect'],capture_output=True,text=True);assert budget.returncode==0;v['final_workspace_budget']=json.loads(budget.stdout);write(prefix+'verification.json',v)
 index=json.loads((r/(prefix+'attempts.json')).read_bytes());assert sum(x['cases'] for x in index['final_native'].values())==168 and index['final_runs']['linux-x64-gcc13']['editors']['outcome']=='fail'
files=subprocess.check_output(['git','diff','HEAD','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
old=json.loads((r/'build-support/evidence/edit-locks-handoff.json').read_bytes())
h=dict(schema_version='0.1.0',work_id='W-10',source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),objective='Repair native editor refresh starvation and preserve policy erasure with fixed independent acceptance',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=['Freeze original contracts/oracles and bounded regression inputs before production changes.', 'Distinguish real GTK focus, exported ATK focus and idle starvation with paired native evidence.', 'Yield optional refresh below normal idle; stop empty periodic redraw and scope immediate style transitions to editor widgets.', 'Preserve all original focus/erasure failures and the explicit auxiliary sampler correction.', 'Review and record externally updated Linux runtime identities without installing packages or changing acceptance.', 'Retain workspace bounds and all five complete-edition release tracks.'],
 checks=[{'name':name,'outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'} for name in ('311 Linux non-native checks','165 existing editor cases and three loaded/fault cases in passing matrices','13 passing native rendering checks on reviewed dependency identities','Two composition checks per Windows profile and unchanged Windows binaries')]+[
 {'name':'Complete 180-case existing editor regression','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Complete 15-check rendering regression','outcome':'fail','evidence':prefix+'attempts.json'},
 {'name':'Schema, fixture, tooling and integrity checks','outcome':'not_run' if pending else 'pass','evidence':prefix+'verification.json'},
 {'name':'Staged source/oracle/artifact/evidence identities','outcome':'not_run','evidence':prefix+'staging.json'},
 {'name':'Complete editions and historical/release qualification','outcome':'not_run','evidence':None}],
 open_questions=old['open_questions'],next_step='Investigate the preserved binding tab-role and inspector selected-row timeouts plus scene-image nonblocking-paint timing failure, then continue conditional visibility/typography, clipboard/recovery drafts and installed ownership; retain all five complete-edition gates.',authority_used=old['authority_used'],
 limitations=['The binding-authoring matrix failed at a libatspi tab-role query; its cause is unresolved and this checkpoint is not fully qualified.', 'Owned Linux Xvfb/D-Bus evidence does not qualify installed editing, historical platforms or complete editions.', 'The paired load experiment identifies a refresh scheduling defect; earlier unrelated interface/focus causes remain unproven.', 'Scoped immediate style changes preserve the erasure bound in this profile; broad accessibility/performance qualification remains required.', 'Windows product binaries are unchanged and product suites were not rerun; two existing tooling symlink assertions remain skipped.', 'Remaining authoring, installed ownership, other adapters and complete release gates stay open.'])
jsonschema.validate(h,json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()));write(hp,h)
if pending:write(prefix+'staging.json',{'outcome':'pending'})
print('Prepared pending handoff.' if pending else 'Verified results and sealed handoff.')

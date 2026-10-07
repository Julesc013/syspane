from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-visibility-';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
index=json.loads((e/(prefix+'attempts.json')).read_bytes());p=e/(prefix+'verification.json');v=json.loads(p.read_bytes());assert all(c['exit']==0 for c in v['checks'])
changes={n:sha(r/n) for n,h in index['current_inputs'].items() if sha(r/n)!=h}
allowed={'spec/contracts/index.md','spec/fixtures/invalid/index.md','spec/fixtures/valid/index.md','spec/experience/editor.md','spec/experience/scene-bindings.md'}
assert set(changes)==allowed
record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),initial_finalization=dict(exit=1,verifier_sha256=sha(r/'out/campaign/verify_visibility.py'),reason='The evidence finalizer omitted generated fixture navigation from its documentation-only allowlist.',unexpected_documentation_files=sorted(allowed-{'spec/contracts/index.md','spec/experience/editor.md','spec/experience/scene-bindings.md'})),resolution='Explicitly verify the five known documentation/navigation changes, retain all executable source/schema/fixture hashes, and preserve the original failed finalizer.',verified_documentation_changes=changes,outcome='pass')
write(e/(prefix+'finalization.json'),record)
v['tool_inputs']={x.relative_to(r).as_posix():sha(x) for x in (r/'spec/tools').rglob('*.py')}
v['final_workspace_budget']=json.loads(subprocess.check_output([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py'],text=True));assert v['final_workspace_budget']['status']=='pass'
v['post_test_documentation_updates']=changes;v['finalization_record']=dict(path='build-support/evidence/'+prefix+'finalization.json',sha256=sha(e/(prefix+'finalization.json')));write(p,v)
helper=r/'out/campaign/finalize_visibility_verification.py';target=e/(prefix+'history/support/finalize_visibility_verification.py');shutil.copyfile(helper,target);index['support'][helper.relative_to(r).as_posix()]=dict(path=target.relative_to(r).as_posix(),sha256=sha(target));write(e/(prefix+'attempts.json'),index)
print('Final verification passed; original documentation allowlist failure preserved.')

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
r=Path.cwd();python=str(r/'.venv/Scripts/python.exe');e=r/'build-support/evidence';p=e/'w-10-theme-controls-verification.json'
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
record=dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),checks=[],limitations=['Native font controls and durable preview/save/reopen are verified; installed ownership and full editions remain open.'])
def save():p.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
commands=[[python,'-X','utf8','spec/tools/specctl.py',*a] for a in [('generate',),('validate','--schemas'),('generate','--check')]]
commands += [[python,'-X','utf8','out/campaign/audit_theme_controls_correction.py']]
commands += [[python,'-X','utf8','tests/configuration/settings_content_fixture.py','--check'],[python,'-X','utf8','-m','unittest','discover','-s','spec/tools/tests','-v']]
commands += [[python,'-X','utf8','spec/tools/specctl.py',*a] for a in [('seal','--apply'),('verify-integrity',)]]
if '--refresh' in sys.argv:
 record=json.loads(p.read_bytes());commands=[[python,'-X','utf8','spec/tools/specctl.py',*a] for a in [('generate',),('validate','--schemas'),('generate','--check'),('seal','--apply'),('verify-integrity',)]]
for command in commands:
 for call in ([python,'-X','utf8','build-support/check_workspace_budget.py','--action','test'],command):
  started=datetime.now(timezone.utc).isoformat();v=subprocess.run(call,cwd=r,capture_output=True,text=True,encoding='utf-8',errors='replace')
  record['checks'].append(dict(command=call,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),exit=v.returncode,stdout=v.stdout,stderr=v.stderr));save()
  print(' '.join(call[3:]),'exit',v.returncode,flush=True)
  if v.returncode:print(v.stdout[-4000:],v.stderr[-2000:]);sys.exit(v.returncode)
record['tool_inputs']={x.relative_to(r).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in (r/'spec/tools').rglob('*.py')}
record['final_workspace_budget']=json.loads(subprocess.check_output([python,'-X','utf8','build-support/check_workspace_budget.py'],text=True));assert record['final_workspace_budget']['status']=='pass'
index=json.loads((e/'w-10-theme-controls-attempts.json').read_bytes());changes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n,h in index['current_inputs'].items() if hashlib.sha256((r/n).read_bytes()).hexdigest()!=h}
normal_path=e/'w-10-theme-controls-normalization.json';normal=json.loads(normal_path.read_bytes())
assert normal['outcome']=='pass' and normal['before_artifacts']==normal['after_artifacts']==index['artifacts']['linux-x64-gcc13']
assert normal['original_sha256']==index['current_inputs'][normal['source']]
assert changes.pop(normal['source'])==normal['normalized_sha256']
record['post_test_source_normalization']={'path':normal_path.relative_to(r).as_posix(),'sha256':hashlib.sha256(normal_path.read_bytes()).hexdigest()}
assert set(changes)<= {'spec/delivery/packages/w-10-theme-controls.md','spec/contracts/index.md','spec/experience/index.md','spec/experience/scene-bindings.md','spec/experience/editor.md','spec/experience/scene-theme.md','spec/contracts/transport.md','spec/fixtures/valid/index.md','spec/fixtures/invalid/index.md'},changes
record['post_test_documentation_updates']=changes;save()
print('Verification complete; documentation changes and the byte-identical executable normalization rebuild are audited.')

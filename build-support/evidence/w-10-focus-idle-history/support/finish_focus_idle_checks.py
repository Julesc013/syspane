from datetime import datetime,timezone
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];python=str(root/'.venv/Scripts/python.exe');evidence=root/'build-support/evidence';prefix='w-10-focus-idle-'
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();assert base=='9c1757de6a8227b2a4235f8be7b727a9d3f55d7d'
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
checks=[];record={'source_base':base,'recorded_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'limitations':['Specification checks do not qualify product behavior. Existing Windows symlink checks may be skipped.']}
commands=[[python,'-X','utf8','spec/tools/specctl.py',*args] for args in [('generate',),('validate','--schemas'),('generate','--check')]]
commands += [[python,'-X','utf8','tests/configuration/settings_content_fixture.py','--check']]
commands += [[python,'-X','utf8','-m','unittest','discover','-s','spec/tools/tests','-v']]
commands += [[python,'-X','utf8','spec/tools/specctl.py',*args] for args in [('seal','--apply'),('verify-integrity',)]]
if '--refresh' in sys.argv:
 record=json.loads((evidence/(prefix+'verification.json')).read_text());checks=record['checks']
 commands=[[python,'-X','utf8','spec/tools/specctl.py',*args] for args in [('generate',),('validate','--schemas'),('generate','--check'),('seal','--apply'),('verify-integrity',)]]
if '--handoff-only' in sys.argv:
 record=json.loads((evidence/(prefix+'verification.json')).read_text());checks=record['checks'];commands=[]
for command in commands:
 for call in ([python,'-X','utf8','build-support/check_workspace_budget.py','--action','test'],command):
  started=datetime.now(timezone.utc).isoformat();r=subprocess.run(call,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace')
  checks.append({'command':call,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});write(evidence/(prefix+'verification.json'),record)
  print(' '.join(call[3:]),'exit',r.returncode,flush=True)
  if r.returncode:print(r.stdout[-3000:],r.stderr[-1500:]);sys.exit(r.returncode)

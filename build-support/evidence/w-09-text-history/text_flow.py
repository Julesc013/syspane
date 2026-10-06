from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys,uuid
r=Path(__file__).resolve().parents[2];python=str(r/'.venv/Scripts/python.exe');profile=sys.argv[1]
path=r/'out/campaign'/('text-execution-'+profile+'-'+uuid.uuid4().hex[:10]+'.json');rows=[]
for step in sys.argv[2:] or ['configure','build','test']:
    command=['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/text_step.py',profile,step] if profile.startswith('linux') else [python,'-X','utf8','out/campaign/text_step.py',profile,step]
    for call in ([python,'-X','utf8','build-support/check_workspace_budget.py','--action','test' if step in ('test','focus','oracle') else 'build'],command):
        started=datetime.now(timezone.utc).isoformat();p=subprocess.run(call,cwd=r,capture_output=True,text=True,encoding='utf-8',errors='replace')
        rows.append({'step':step,'command':call,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        path.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n');print(p.stdout[-4500:],p.stderr[-2500:],flush=True)
        if p.returncode:sys.exit(p.returncode)
print('Flow:',path,flush=True)

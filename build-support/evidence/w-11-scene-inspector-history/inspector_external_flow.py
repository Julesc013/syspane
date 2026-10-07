from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys,uuid
r=Path.cwd();python=str(r/'.venv/Scripts/python.exe');rows=[]
p=r/'out/campaign'/('scene-inspector-external-'+uuid.uuid4().hex[:10]+'.json')
def run(command):
    started=datetime.now(timezone.utc).isoformat()
    result=subprocess.run(command,cwd=r,capture_output=True,text=True,encoding='utf-8',errors='replace')
    rows.append(dict(command=command,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),exit=result.returncode,stdout=result.stdout,stderr=result.stderr))
    p.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result.stdout[-5000:],result.stderr[-2000:],flush=True)
    return result.returncode
for step in sys.argv[1:] or ['oracle','scalar','table','content','chart','image']:
    assert step in ('oracle','scalar','table','content','chart','image')
    rc=run([python,'-X','utf8','out/campaign/inspector_flow.py','linux-x64-gcc13',step])
    # Preserve completed observations before removing only hash-verified redundant captures.
    for helper in ('archive_inspector.py','reclaim_inspector_captures.py'):
        archived=run(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/'+helper])
        if archived:sys.exit(archived)
    if rc:sys.exit(rc)
print('External flow:',p,flush=True)

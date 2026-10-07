from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
r=Path.cwd();p=r/'spec/tools/specctl.py';old=p.read_bytes();out=r/'out/campaign/w-10-edit-locks/schema-identity-failure.json';assert not out.exists()
command=[str(r/'.venv/Scripts/python.exe'),'-X','utf8','spec/tools/specctl.py','validate','--schemas'];run=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');assert run.returncode!=0 and 'unexpected schema identity: command-v0.6.schema.json' in run.stdout
out.write_text(json.dumps(dict(command=command,exit=run.returncode,stdout=run.stdout,stderr=run.stderr,recorded_at=datetime.now(timezone.utc).isoformat(),tool_before_sha256=hashlib.sha256(old).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n');(out.parent/'specctl-before-identity.py').write_bytes(old)
s=old.decode().replace(r'(0\.[2345])',r'(0\.[23456])');assert s!=old.decode();p.write_text(s,encoding='utf-8',newline='\n')

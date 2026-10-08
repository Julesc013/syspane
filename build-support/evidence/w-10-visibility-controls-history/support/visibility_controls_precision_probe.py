from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
r=Path(__file__).resolve().parents[2];out=r/'out/campaign';p=out/'visibility-controls-precision-probe.json'
record=dict(source_base=subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),started_at=datetime.now(timezone.utc).isoformat(),checks=[],inputs={})
for n in ('out/campaign/visibility_controls_precision_probe.cpp','source/third_party/nlohmann/json.hpp','source/interfaces/editor_visibility.cpp','source/interfaces/editor_draft.cpp','source/interfaces/settings_draft.cpp'):record['inputs'][n]=hashlib.sha256((r/n).read_bytes()).hexdigest()
for command in [['/usr/bin/g++-13','-std=c++17','-Wall','-Wextra','-Werror','-I'+str(r/'source/third_party'),str(out/'visibility_controls_precision_probe.cpp'),'-o',str(out/'visibility-controls-precision-probe')],[str(out/'visibility-controls-precision-probe')]]:
 v=subprocess.run(command,capture_output=True,text=True);record['checks'].append(dict(command=command,exit=v.returncode,stdout=v.stdout,stderr=v.stderr));p.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(v.stdout,v.stderr)
 if v.returncode:sys.exit(v.returncode)
record['executable_sha256']=hashlib.sha256((out/'visibility-controls-precision-probe').read_bytes()).hexdigest();record['finished_at']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')

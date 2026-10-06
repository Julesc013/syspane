from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'build-support'))
from check_legacy_artifacts import verify,build_inputs
b=r/'out/build/windows-x86-v141-xp';p=b/'Release/syspane_demand_tests.exe';data=p.read_bytes()
v={'outcome':'pass','profile':'windows-x86-v141-xp','artifact':{'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),**verify(data)},'build_inputs':build_inputs(b),
 'verification_inputs':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ('build-support/check_legacy_artifacts.py','build-support/targets/windows-x86-v141-xp.imports.json')},
 'qualification':'Historical-toolset PE/header/declared import closure; executed on the modern Windows host only. No XP, Windows 9x or old NT runtime qualification.'}
(r/'out/campaign/demand-legacy-audit.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n');print('Demand test PE/header/import audit passed; no guest runtime claim.')

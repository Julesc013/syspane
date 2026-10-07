from pathlib import Path
from datetime import datetime,timezone
import json,sys
r=Path('/mnt/d/Projects/SysPane/syspane');sys.path.insert(0,str(r/'build-support'))
from check_text_runtime import identify
old=json.loads((r/'build-support/text-runtime.json').read_bytes());new=identify()
delta=dict(packages_changed=old['packages']!=new['packages'],configuration_changed=old['font_configuration']!=new['font_configuration'],added={p:h for p,h in new['files'].items() if p not in old['files']},removed={p:h for p,h in old['files'].items() if p not in new['files']},changed={p:dict(expected=old['files'][p],actual=h) for p,h in new['files'].items() if p in old['files'] and old['files'][p]!=h})
out=r/'out/campaign/focus-idle/text-runtime-difference.json';assert not out.exists();out.write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),actual=new,difference=delta),indent=2)+'\n')
print(json.dumps(delta,indent=2))
if delta['packages_changed']:print(new['packages'])
if delta['configuration_changed']:
 print('NEW CONFIG LINES',set(new['font_configuration'].splitlines())-set(old['font_configuration'].splitlines()));print('REMOVED CONFIG LINES',set(old['font_configuration'].splitlines())-set(new['font_configuration'].splitlines()))

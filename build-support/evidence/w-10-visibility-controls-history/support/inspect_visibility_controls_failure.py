from pathlib import Path
import json
p=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence/visibility-controls-9e9f25ecb8c0/held-hide')
v=json.loads((p/'result.json').read_bytes());print('keys',list(v));print({k:x for k,x in v.items() if k not in ('native_observations','files') and len(str(x))<5000});print('files',[(q.name,q.stat().st_size) for q in p.iterdir() if q.is_file()])
for k,x in v.items():
 if isinstance(x,list) and len(str(x))>=5000:print('tail',k,x[-10:])

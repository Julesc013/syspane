from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign/w-10-containers'
v=json.loads((r/'tests/editor/container-cases.json').read_bytes());scene=copy.deepcopy(v['expected']['canvas']);scene['widgets'][-1]['layout']['base'].update(width=180,height=80)
p=r/'tests/editor/container-preview-cases.json';p.write_text(json.dumps(dict(native_cases=['overflow'],unavailable_scene=scene,repaired_scene=v['expected']['canvas'],required_status='Preview unavailable',forbidden_status='Not on this display'),indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'spec/delivery/packages/w-10-container-preview.md';p.write_text(p.read_text().replace('2026-10-07T12:10:00Z',datetime.now(timezone.utc).isoformat()),encoding='utf-8',newline='\n')
names=['tests/editor/container-preview-cases.json','spec/delivery/packages/w-10-container-preview.md'];inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in names}
with zipfile.ZipFile(out/'preview-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(r/n,n)
(out/'preview-inputs.json').write_text(json.dumps(dict(inputs=inputs,archive_sha256=hashlib.sha256((out/'preview-inputs.zip').read_bytes()).hexdigest(),before_production_sha256=hashlib.sha256((r/'source/interfaces/editor_form_linux.cpp').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n')
print('Frozen unavailable-preview case before production status correction.')

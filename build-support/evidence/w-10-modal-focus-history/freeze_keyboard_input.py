from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
r=Path.cwd();base=r/'out/campaign/w-10-modal-focus';base.mkdir(exist_ok=True)
p=r/'spec/delivery/packages/w-10-keyboard-input.md';s=p.read_text();assert '2026-10-07T11:00:00+00:00' in s;p.write_text(s.replace('2026-10-07T11:00:00+00:00',datetime.now(timezone.utc).isoformat()),encoding='utf-8',newline='\n')
names=['spec/delivery/packages/w-10-keyboard-input.md','tests/editor/layout-authoring-cases.json','tests/editor/observation-cases.json','tests/editor/native_observation.py','tests/editor/native_editor.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(base/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(r/n,n)
(base/'fixed-inputs.json').write_text(json.dumps(dict(inputs={n:sha(r/n) for n in names},archive_sha256=sha(base/'fixed-inputs.zip')),indent=2)+'\n',encoding='utf-8',newline='\n')

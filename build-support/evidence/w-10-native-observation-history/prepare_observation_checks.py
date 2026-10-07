from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
r=Path(__file__).resolve().parents[2];d=r/'out/campaign/w-10-native-observation';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('observation_step.py','observation_flow.py'):
    p=r/'out/campaign'/name;s=p.read_text().replace("'experiment',","'calibration','experiment',")
    if name=='observation_step.py':
        s=s.replace("command={'experiment':","command={'calibration':['ctest','--preset',profile,'-R','^native[.]EDITOR-OBSERVATION$','--output-on-failure'],'experiment':")
        s=s.replace("{'experiment':'syspane_editor_window'","{'calibration':'syspane_editor_window','experiment':'syspane_editor_window'")
        s=s.replace("if action in ('test',","if action in ('calibration','test',")
    p.write_text(s,encoding='utf-8',newline='\n')
with zipfile.ZipFile(d/'calibration-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(r/'tests/editor/observation-cases.json','tests/editor/observation-cases.json')
(d/'calibration-inputs.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),scope='Calibration expectations frozen before execution; product fixtures remain the earlier frozen originals.',inputs={'tests/editor/observation-cases.json':sha(r/'tests/editor/observation-cases.json')},archive_sha256=sha(d/'calibration-inputs.zip')),indent=2)+'\n',encoding='utf-8',newline='\n')
v=json.loads((d/'upstream.json').read_text());v['dbind.c']={'url':'https://raw.githubusercontent.com/GNOME/at-spi2-core/AT_SPI2_CORE_2_52_0/dbind/dbind.c','sha256':sha(d/'dbind.c')};(d/'upstream.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')

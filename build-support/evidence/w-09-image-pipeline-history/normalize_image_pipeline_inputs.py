from pathlib import Path
import hashlib,json
r=Path.cwd();rows=[]
for n in ('build-support/components.json','spec/delivery/work-units.json'):
    p=r/n;before=p.read_bytes();after=before.replace(b'\r\n',b'\n')
    assert json.loads(before)==json.loads(after)
    p.write_bytes(after);rows.append(dict(path=n,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),reason='Honor repository text eol=lf before final source-bound build/test and seal; JSON values unchanged.'))
(r/'out/campaign/image-input-normalization.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')

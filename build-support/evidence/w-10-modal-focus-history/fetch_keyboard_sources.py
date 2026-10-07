from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.request
p=Path('out/campaign/w-10-modal-focus');result={}
for name in ('gtkwidgetaccessible.c','gtkbuttonaccessible.c','gtkaccessibility.c','gtkbutton.c'):
    url='https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/'+('a11y/' if name!='gtkbutton.c' else '')+name
    raw=urllib.request.urlopen(url,timeout=30).read();assert b'GNU' in raw
    (p/name).write_bytes(raw);result[name]=dict(url=url,sha256=hashlib.sha256(raw).hexdigest(),retrieved_at=datetime.now(timezone.utc).isoformat(),scope='API implementation context; native traces establish observed failure')
(p/'upstream.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Recorded four upstream source identities.')

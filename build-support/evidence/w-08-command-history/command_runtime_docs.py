from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib,html,json,re,urllib.request
r=Path.cwd();names=json.loads((r/'out/campaign/command-runtime-docs-input.json').read_text())
def fetch(pair):
 header,name=pair;url=f'https://learn.microsoft.com/en-us/windows/win32/api/{header}/nf-{header}-{name.lower()}'
 try:
  with urllib.request.urlopen(url,timeout=20) as response:body=response.read();url=response.url
  text=body.decode();match=re.search(r'Minimum supported client.*?</tr>',text,re.S)
  assert match,'missing requirements'
  value=html.unescape(re.sub('<[^>]*>',' ',match[0]));value=' '.join(value.split())
  return {'name':name,'url':url,'requirements':value,'retrieved_sha256':hashlib.sha256(body).hexdigest()}
 except Exception as e:return {'name':name,'url':url,'error':repr(e)}
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,[(h,n) for h,ns in names.items() for n in ns]))
v={'recorded_at':datetime.now(timezone.utc).isoformat(),'sources':rows,'scope':'Official documented client floors only, not proof of guest exports or behavior.'}
(r/'out/campaign/command-runtime-docs.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for row in rows:print(row['name'],row.get('requirements',row.get('error')))

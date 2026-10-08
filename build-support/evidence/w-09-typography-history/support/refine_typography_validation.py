from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign/w-09-typography'
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'spec/contracts/theme-v0.2.schema.json';v=json.loads(p.read_bytes())
v['$defs']['font']['properties']['family']['pattern']='^[^ \\u0000-\\u001f\\u007f,](?:[^\\u0000-\\u001f\\u007f,]*[^ \\u0000-\\u001f\\u007f,])?$'
v['$defs']['font']['properties']['family']['description']='C1 controls U+0080..U+009F and UTF-8 byte length over 512 are semantic validation errors. ASCII controls, comma and edge spaces are structural errors.'
write(p,v)
old=json.loads((out/'fixed-inputs.json').read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(out/'fixed-inputs-v2.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in old['inputs']:z.write(r/n,n)
write(out/'fixed-inputs-v2.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'source_base':old['source_base'],'inputs':{n:sha(r/n) for n in old['inputs']},'archive_sha256':sha(out/'fixed-inputs-v2.zip'),'supersedes':'fixed-inputs.json','reason':'Before production edits, assign C1 rejection to explicit Unicode semantic validation; byte-based C++ regex cannot interpret Unicode character classes portably. Literal invalid-font expectations and required behavior are unchanged.'})
import jsonschema
s=jsonschema.Draft202012Validator(v);cases=json.loads((r/'tests/scene/typography-cases.json').read_bytes());s.validate(cases['theme'])
for f in cases['invalid_fonts']:
 bad={**cases['theme'],'font':f};invalid=bool(list(s.iter_errors(bad))) or any(128<=ord(c)<=159 for c in f.get('family',''))
 assert invalid,f
write(r/'out/campaign/typography-fixed-validation-v2.json',{'outcome':'pass','invalid_fonts':len(cases['invalid_fonts']),'schema_sha256':sha(p),'scope':'Independent structural validation plus explicit C1 scalar check before production changes; original freeze retained.'})
print('Preserved initial freeze and validated exact rejection expectations with explicit C1 semantics.')

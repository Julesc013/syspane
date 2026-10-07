from pathlib import Path
from copy import deepcopy
import json,hashlib,zipfile
r=Path.cwd();d=r/'out/campaign/w-10-binding-authoring'
v=json.loads((r/'tests/editor/binding-authoring-cases.json').read_text());scene=deepcopy(v['authored']['scene']);scene['widgets'][2]['bindings'][0]['predicates']=[dict(field='entity.id',op='eq',value='a\t\r\0\\"α')]
cases=dict(text=[dict(input='"a\\t\\r\\u0000\\\\\\\"α"',expected='a\t\r\0\\"α'),dict(input='"a\\\\tb"',expected='a\\tb'),dict(input='"\\ud83d\\ude00"',expected='😀')],invalid=['','null','false','12','[]','{}',' "a"','"a" ','"\\ud800"','"\\x00"'],expected=scene)
p=r/'tests/editor/binding-text-cases.json';assert not p.exists();p.write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
paths=['spec/delivery/packages/w-10-binding-text.md','tests/editor/binding-text-cases.json'];inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(d/'fixed-text-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'fixed-text-inputs.json').write_text(json.dumps(dict(inputs=inputs),indent=2)+'\n');print(inputs)

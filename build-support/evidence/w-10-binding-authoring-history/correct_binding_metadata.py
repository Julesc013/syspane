from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile
r=Path.cwd();d=r/'out/campaign/w-10-binding-authoring'
for stem in ('fixed-inputs','fixed-text-inputs'):
 p=d/(stem+'.json');v=json.loads(p.read_text());zp=p.with_suffix('.zip');stamp=datetime.fromtimestamp(zp.stat().st_mtime,timezone.utc).isoformat()
 with zipfile.ZipFile(zp) as z:
  for n,digest in v['inputs'].items():
   if not n.endswith('.md'):continue
   raw=z.read(n);old=b'2026-10-07T08:00:00Z';assert raw.count(old)==1 and (r/n).read_bytes()==raw
   current=raw.replace(old,stamp.encode());(r/n).write_bytes(current)
   v['metadata_corrections']={n:dict(old=old.decode(),new=stamp,sha256=hashlib.sha256(current).hexdigest(),reason='Replace a placeholder generated timestamp with the observed original freeze-archive completion time; all behavioral contract bytes remain unchanged.')}
 p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(stem,stamp)
for filename in ('preserve_bindings.py','stage_bindings.py'):
 p=r/'out/campaign'/filename;s=p.read_text()
 if filename.startswith('preserve'):
  old="    for n,h in fixed['inputs'].items():assert sha(r/n)==hashlib.sha256(z.read(n)).hexdigest()==h"
  new="""    for n,h in fixed['inputs'].items():
        raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h
        correction=fixed.get('metadata_corrections',{}).get(n)
        if correction:
            assert n.endswith('.md') and raw.count(correction['old'].encode())==1
            assert (r/n).read_bytes()==raw.replace(correction['old'].encode(),correction['new'].encode()) and sha(r/n)==correction['sha256']
        else:assert sha(r/n)==h"""
 else:
  old="    for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)"
  new="""    for n,digest in fixed['inputs'].items():
        raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==digest
        correction=fixed.get('metadata_corrections',{}).get(n)
        if correction:
            assert n.endswith('.md') and raw.count(correction['old'].encode())==1
            assert content(n)==raw.replace(correction['old'].encode(),correction['new'].encode());check(n,correction['sha256'])
        else:check(n,digest)"""
 assert old in s;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
p=r/'out/campaign/preserve_bindings.py';s=p.read_text().replace("helpers=['prepare_binding_authoring.py'","helpers=['correct_binding_metadata.py','prepare_binding_authoring.py'");p.write_text(s,encoding='utf-8',newline='\n')
p=r/'spec/delivery/current-state.md';s=p.read_text().replace('The latest [content-properties checkpoint]','The earlier [content-properties checkpoint]',1);p.write_text(s,encoding='utf-8',newline='\n')
p=r/'spec/delivery/binding-authoring-handoff.md';s=p.read_text().replace('Original descriptors, resource bytes, full expected scenes and supplemental text','Two placeholder generated timestamps were corrected to observed original archive\ncompletion times. The byte-exact original packages remain archived; only those\nmetadata strings differ, with explicit verification records.\n\nOriginal descriptors, resource bytes, full expected scenes and supplemental text',1);p.write_text(s,encoding='utf-8',newline='\n')

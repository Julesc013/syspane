from pathlib import Path
import hashlib,json,os
r=Path.cwd();out=r/'out/campaign';p=out/'refresh_step.py';old=p.read_bytes();saved=out/'refresh_step_before_walk.py';assert not saved.exists();saved.write_bytes(old)
last=json.loads((out/'w-10-focus-idle/linux-x64-gcc13-configure-4c4eaf0487/result.json').read_bytes())['source_inputs']
paths=[r/'CMakeLists.txt',r/'CMakePresets.json',r/'spec/delivery/packages/w-10-focus-idle.md']
for folder in ('source','tests','build-support','spec/contracts','spec/fixtures','spec/experience'):
 for base,dirs,files in os.walk(r/folder):
  dirs[:]=[d for d in dirs if d not in ('evidence','__pycache__')]
  paths.extend(Path(base)/n for n in files if (Path(base)/n).is_file())
current={q.relative_to(r).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in paths};assert current==last
s=old.decode().replace('import hashlib,json,subprocess','import hashlib,json,os,subprocess')
before="    paths.extend(p for p in (r/folder).rglob('*') if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts)"
after="    for base,dirs,files in os.walk(r/folder):\n        dirs[:]=[d for d in dirs if d not in ('evidence','__pycache__')]\n        paths.extend(Path(base)/n for n in files if (Path(base)/n).is_file())"
assert s.count(before)==1;s=s.replace(before,after);p.write_text(s,encoding='utf-8',newline='\n')
(out/'focus-idle/walk-equivalence.json').write_text(json.dumps(dict(outcome='pass',inputs=len(current),before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reference='linux-x64-gcc13-configure-4c4eaf0487'),indent=2)+'\n',encoding='utf-8',newline='\n')

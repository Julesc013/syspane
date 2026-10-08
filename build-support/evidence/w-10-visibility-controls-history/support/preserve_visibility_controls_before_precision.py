from pathlib import Path
import hashlib,io,json,shutil,subprocess,zipfile
r=Path.cwd();e=r/'build-support/evidence';h=e/'w-10-visibility-controls-history';h.mkdir(exist_ok=True);rows=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for p in sorted((r/'out/campaign/w-10-visibility-controls').glob('*/result.json')):
 v=json.loads(p.read_bytes());target=h/p.parent.name;target.mkdir(exist_ok=True)
 for n in ('result.json','source-inputs.zip','ctest-log.zip'):
  q=p.parent/n
  if q.exists():shutil.copyfile(q,target/n)
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,digest in v['source_inputs'].items():assert sha(z.read(n))==digest
 rows.append(dict(path=(target/'result.json').relative_to(r).as_posix(),sha256=sha((target/'result.json').read_bytes()),action=v['action'],exit=v['exit']))
p=e/'w-10-visibility-controls-before-precision.json';p.write_text(json.dumps(dict(source_base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),attempts=rows,scope='Raw completed control/regression evidence before the newly identified numeric-equality repair. Not a completed implementation or qualification claim; numeric regression and repair remain pending.'),indent=2)+'\n',encoding='utf-8',newline='\n')
paths=[p,'build-support/evidence/w-10-visibility-controls-native-index.json',e/'w-10-visibility-controls-native',h]
subprocess.run(['git','add','--',*map(str,paths)],check=True)
staged=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
assert all(n.startswith('build-support/evidence/w-10-visibility-controls-') for n in staged)
for n in staged:assert subprocess.check_output(['git','show',':'+n])==(r/n).read_bytes(),n
subprocess.run(['git','diff','--cached','--check'],check=True)
print('Verified',len(staged),'staged evidence files; production changes remain unstaged.')

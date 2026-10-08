from pathlib import Path
import hashlib,json,shutil,subprocess
r=Path.cwd();prefix='build-support/evidence/w-09-typography-';h=r/(prefix+'history');h.mkdir(exist_ok=True)
paths=[]
for record in sorted((r/'out/campaign/w-09-typography').glob('*/result.json')):
 v=json.loads(record.read_bytes());target=h/record.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip','ctest-log.zip'):
  p=record.parent/name
  if p.exists():
   q=target/name;shutil.copyfile(p,q);assert hashlib.sha256(q.read_bytes()).digest()==hashlib.sha256(p.read_bytes()).digest();paths.append(q.relative_to(r).as_posix())
paths += [p.relative_to(r).as_posix() for p in (r/(prefix+'native')).iterdir() if p.is_file()]+[prefix+'native-index.json']
for n in paths:assert n.startswith(prefix)
ps=r/'out/campaign/typography-raw-evidence-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode())
subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths)
for n in paths:assert subprocess.check_output(['git','show',':'+n])==(r/n).read_bytes(),n
subprocess.run(['git','diff','--cached','--check'],check=True)
print('Staged and verified',len(paths),'raw evidence files only; implementation remains uncommitted.')

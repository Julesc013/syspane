from pathlib import Path
import hashlib,json,os,sys
profile=sys.argv[1]
if profile=='linux-x64-gcc13':
 assert os.geteuid()!=0
 root=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
else:
 assert profile in ('windows-x64-gcc15','windows-x86-v141-xp')
 root=Path(__file__).resolve().parents[2]/'out/build'/profile
 if profile.endswith('xp'):root=root/'Release'
assert root.resolve()==root
result={}
for p in root.iterdir():
 if not p.is_file() or p.is_symlink():continue
 with p.open('rb') as stream:magic=stream.read(4)
 if magic[:2]==b'MZ' or magic==b'\x7fELF':result[p.name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
assert result
print(json.dumps(result,sort_keys=True))

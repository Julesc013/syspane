from pathlib import Path
import hashlib,json,os,shlex,subprocess
r=Path('/mnt/d/Projects/SysPane/syspane');out=r/'out/campaign/focus-idle';out.mkdir(exist_ok=True)
assert os.geteuid()!=0
source=r/'out/campaign/editor_idle_probe.c';target=out/'editor_idle_probe.so'
command=['gcc','-shared','-fPIC','-O0','-g','-Wall','-Wextra','-Werror',str(source),'-o',str(target),*shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0'],text=True)),'-ldl']
p=subprocess.run(command,capture_output=True,text=True)
v=dict(command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
if not p.returncode:v['binary_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
(out/'probe-build.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));raise SystemExit(p.returncode)

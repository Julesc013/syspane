from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shlex,subprocess,uuid
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');assert os.geteuid()!=0
d=r/'out/campaign/runtime-observation'/('image-poll-'+uuid.uuid4().hex[:12]);d.mkdir();source=r/'out/campaign/image_poll_probe.cpp';exe=d/'probe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lines=subprocess.check_output(['ninja','-C',str(b),'-t','commands','syspane_image_job_tests'],text=True).splitlines();compile=shlex.split(lines[0]);start=compile.index('-MD');compile=compile[:start]+[str(source),'-o',str(exe)]
link=shlex.split(lines[-1]);libs=[b/n for n in link if n.endswith('.a')];assert libs and all(p.is_file() for p in libs);compile += list(map(str,libs))
inputs=[source,r/'out/campaign/run_image_poll_probe.py',r/'source/scene/image.cpp',r/'source/rendering/image_job_linux.cpp',r/'tests/scene/image-cases/maximum.png',b/'SysPane.ImageWorker',*libs]
v=dict(outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),inputs={str(p):sha(p) for p in inputs},build_command=compile)
try:
 p=subprocess.run(compile,capture_output=True,text=True,timeout=60);v['build']=dict(exit=p.returncode,stdout=p.stdout,stderr=p.stderr);assert p.returncode==0,p.stderr
 v['executable_sha256']=sha(exe);p=subprocess.run([str(exe),str(b/'SysPane.ImageWorker'),str(r/'tests/scene/image-cases/maximum.png')],capture_output=True,text=True,timeout=30)
 v['execution']=dict(exit=p.returncode,stdout=p.stdout,stderr=p.stderr);assert p.returncode==0,p.stderr;v['trials']=json.loads(p.stdout);v['outcome']='observed'
finally:
 v['changed_inputs']=[str(p) for p in inputs if sha(p)!=v['inputs'][str(p)]];(d/'result.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(path=str(d/'result.json'),outcome=v['outcome'],trials=[dict(validate_ms=t['validate_ms'],fit_ms=t['fit_ms'],max_poll_ms=max(p['ms'] for p in t['polls']),final_poll_ms=t['polls'][-1]['ms']) for t in v.get('trials',[])])))

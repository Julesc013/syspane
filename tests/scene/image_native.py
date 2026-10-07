"""Independent worker protocol/pixel/failure oracle; owned public fixture data only."""
from pathlib import Path
import hashlib,json,os,signal,struct,subprocess,sys,time,uuid
worker=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()/('image-'+uuid.uuid4().hex[:12]);out.mkdir(parents=True)
root=Path(__file__).with_name('image-cases');records=[]
def record(v):records.append(v);(out/'result.json').write_text(json.dumps(dict(outcome='pending',worker_sha256=hashlib.sha256(worker.read_bytes()).hexdigest(),cases=records),indent=2)+'\n')
for case in json.loads((root/'native.json').read_text()):
    data=(root/case['name']).read_bytes();started=time.monotonic();p=subprocess.run([str(worker),case['media'],str(os.getpid())],input=struct.pack('>I',len(data))+data,capture_output=True,timeout=5,cwd=out)
    row=dict(case=case['name'],exit=p.returncode,elapsed=time.monotonic()-started,input_sha256=hashlib.sha256(data).hexdigest(),stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr=p.stderr.decode(errors='replace'),outcome='fail')
    if 'error' in case:ok=p.returncode!=0 and p.stdout==b'' and case['error'] in row['stderr']
    else:
        expected=bytes(case['solid'])*(case['size'][0]*case['size'][1]) if 'solid' in case else bytes(case['rgba'])
        ok=p.returncode==0 and p.stdout==b'SPIM0001'+struct.pack('>II',*case['size'])+expected
    row['outcome']='pass' if ok else 'fail';(out/(case['name']+'.reply')).write_bytes(p.stdout);record(row)
    if not ok:raise AssertionError(row)
p=subprocess.run([str(worker),'--check-sandbox',str(os.getpid())],capture_output=True,timeout=5,cwd=out)
record(dict(case='sandbox',exit=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode(),outcome='pass' if p.returncode==0 and p.stdout==b'sandbox.pass\n' else 'fail'));assert records[-1]['outcome']=='pass'
for mode in ('deadline','cancel'):
    started=time.monotonic();p=subprocess.Popen([str(worker),'image/png',str(os.getpid())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=out)
    try:
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            status=Path('/proc',str(p.pid),'status').read_text()
            if 'NoNewPrivs:\t1' in status and 'Seccomp:\t2' in status:break
            time.sleep(.01)
        assert 'NoNewPrivs:\t1' in status and 'Seccomp:\t2' in status
        limits=Path('/proc',str(p.pid),'limits').read_text();assert '268435456' in limits
        if mode=='cancel':p.kill()
        p.wait(timeout=4);elapsed=time.monotonic()-started
        expected=-signal.SIGKILL if mode=='cancel' else -signal.SIGALRM
        assert p.returncode==expected,(mode,p.returncode)
        if mode=='deadline':assert 2.8<=elapsed<=4
        record(dict(case=mode,exit=p.returncode,elapsed=elapsed,status=status,limits=limits,reaped=True,outcome='pass'))
    finally:
        if p.poll() is None:p.kill();p.wait(timeout=3)
        p.stdin.close();p.stdout.close();p.stderr.close()
v=json.loads((out/'result.json').read_text());v['outcome']='pass';v['oracle_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(out/'result.json').write_text(json.dumps(v,indent=2)+'\n');print('IMAGE-NATIVE pass',len(records),'cases',out)

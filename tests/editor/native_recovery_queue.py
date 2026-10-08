"""Observe coalesced native recovery I/O, exact files, grants and held child exit."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,select,signal,socket,struct,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'tests/editor/recovery-queue-cases.json').read_bytes())
RECORDS={k:v.encode() for k,v in json.loads((ROOT/CASES['source_records']).read_bytes())['records'].items()}
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def line(p):
    assert select.select([p.stdout],[],[],8)[0],'queue observation timeout'
    raw=p.stdout.readline();assert raw,'queue EOF';return json.loads(raw)

def main():
    exe,worker,fault,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:5]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('recovery-queue-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='RECOVERY-QUEUE',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),uid=os.geteuid(),kernel=list(os.uname()),filesystem='ext4',executable_sha256=sha(exe.read_bytes()),worker_sha256=sha(worker.read_bytes()),fault_worker_sha256=sha(fault.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),fixture_sha256=sha((ROOT/'tests/editor/recovery-queue-cases.json').read_bytes()),cases=[])
    inputs={};children=[];binding=dict(session='editor:1',profile='profile:primary',generation='4'*64,policy_revision='7')
    for name,raw in {**RECORDS,'intermediate':RECORDS['old']+b'\n','empty':b'','oversized':b'x'*(CASES['maximum_bytes']+1),'maximum':RECORDS['new']+b' '*(CASES['maximum_bytes']-len(RECORDS['new']))}.items():
        inputs[name]=folder/(name+'.input');write(inputs[name],raw)
    def root(name,initial='old'):
        p=folder/name;p.mkdir(mode=0o700)
        if initial is not None:write(p/'draft.json',RECORDS[initial])
        return p
    def bad(mode):
        path=folder/('worker-'+mode)
        if not path.exists():os.link(fault,path)
        return path
    def passed(name,**details):report['cases'].append(dict(case=name,outcome='pass',**details))
    def check(p,want):
        data=RECORDS.get(want,want) if want is not None else None
        assert (p/'draft.json').read_bytes()==data if data is not None else not (p/'draft.json').exists()
    class Owner:
        def __init__(self,p,program=worker,grants='rwe',good=True):
            self.p=p;self.events=[];self.proc=subprocess.Popen([str(exe),str(program),str(p),grants],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0);children.append(self)
            self.initial=line(self.proc);assert ('error' not in self.initial or not self.initial['error'])==good,self.initial
        def call(self,op,**kwargs):
            q=dict(op=op,**kwargs);self.proc.stdin.write(encoded(q)+b'\n');self.proc.stdin.flush();v=line(self.proc);self.events.append(dict(request=q,response=v))
            if op=='exit':return v
            assert v['elapsed_us']<100000,(op,'parent operation blocked',v['elapsed_us'])
            return v['reply']
        def drain(self,state='ready',limit=8):
            end=time.monotonic()+limit
            while time.monotonic()<end:
                v=self.call('poll')
                if v['state']==state and v['reaped']:return v
                assert v['state']!='unavailable' or state=='unavailable',v
                time.sleep(.005)
            raise AssertionError(('queue did not settle',v))
        def load(self,want='old'):
            self.drain();v=self.call('take');data=RECORDS.get(want,want) if want is not None else None
            assert v['operation']=='load' and v['ticket']=='1' and v['outcome']=='loaded' and v['binding']==binding
            assert v['bytes']==(len(data) if data is not None else None) and v['digest']==(sha(data) if data is not None else None) and v['sha256']==v['digest']
            if data is not None and len(data)<=65536:assert bytes.fromhex(v['hex'])==data
            assert self.call('take') is None;return v
        def held(self,ticket=None):
            end=time.monotonic()+3
            while time.monotonic()<end:
                v=self.call('poll');pid=v['process']
                if pid:
                    status=Path('/proc',str(pid),'status').read_text()
                    if '\nState:\tT' in status and (ticket is None or v['active']==ticket):
                        assert f'\nPPid:\t{self.proc.pid}\n' in status
                        fd=os.pidfd_open(pid,0);return v,fd
                assert v['state']!='unavailable',v;time.sleep(.005)
            raise AssertionError('worker did not stop at its named phase')
        def finish(self):
            if self.proc.poll() is None:
                assert self.call('exit')=={'exit':True};assert self.proc.wait(timeout=4)==0
            write(folder/(self.p.name+'-'+str(self.proc.pid)+'.events.json'),encoded(self.events))
            write(folder/(self.p.name+'-'+str(self.proc.pid)+'.stderr'),self.proc.stderr.read())
    try:
        for initial in ('old',None):
            p=root('load-'+str(initial),initial);q=Owner(p);q.load(initial);q.finish();check(p,initial);passed(p.name)
        p=root('maximum',None);write(p/'draft.json',inputs['maximum'].read_bytes());q=Owner(p);q.load(inputs['maximum'].read_bytes());assert q.call('replace',file=str(inputs['maximum']))=={'ticket':'2'};q.drain();v=q.call('take');assert v['outcome']=='durable' and v['digest']==sha(inputs['maximum'].read_bytes());check(p,inputs['maximum'].read_bytes());q.finish();passed(p.name)
        p=root('coalesce',None);q=Owner(p,bad('stop-pending_created'));q.load(None)
        assert q.call('replace',file=str(inputs['old']))=={'ticket':'2'};a,fd=q.held()
        assert q.call('replace',file=str(inputs['intermediate']))=={'ticket':'3'} and q.call('replace',file=str(inputs['new']))=={'ticket':'4'}
        v=q.call('status');assert v['active']=='2' and v['pending']=='4' and v['retained_bytes']==len(RECORDS['new'])
        signal.pidfd_send_signal(fd,signal.SIGCONT);b,fd2=q.held('4');assert b['active']=='4' and b['process']!=a['process'];check(p,'old')
        poller=select.poll();poller.register(fd,select.POLLIN);assert poller.poll(1000)
        signal.pidfd_send_signal(fd2,signal.SIGCONT);q.drain();v=q.call('take');assert v['ticket']=='4' and v['outcome']=='durable' and v['binding']==binding and v['digest']==sha(RECORDS['new']);check(p,'new');q.finish();os.close(fd);os.close(fd2);passed('coalesce',active=a,latest=b)
        p=root('retire-active');q=Owner(p,bad('stop-pending_created'));q.load();q.call('replace',file=str(inputs['new']));v,fd=q.held()
        q.call('replace',file=str(inputs['intermediate']));ticket=q.call('retire')['ticket'];assert ticket=='4'
        assert q.call('replace',file=str(inputs['old']))['error']=='recovery_queue.denied'
        assert q.call('status')['state']=='retiring';signal.pidfd_send_signal(fd,signal.SIGCONT);q.drain('retired');v=q.call('take');assert v['ticket']==ticket and v['outcome']=='durable' and v['digest'] is None;check(p,None);q.finish();os.close(fd);passed(p.name)
        p=root('retire-absent',None);q=Owner(p);q.load(None);q.call('retire');q.drain('retired');assert q.call('take')['outcome']=='durable';assert q.call('replace',file=str(inputs['new']))['error']=='recovery_queue.denied';q.finish();check(p,None);passed(p.name)
        p=root('changed-record');q=Owner(p);q.load();write(p/'draft.json',b'foreign');q.call('replace',file=str(inputs['new']));q.drain('unavailable');v=q.call('take');assert v['outcome']=='unchanged' and v['error']=='recovery_store.conflict';check(p,b'foreign');q.finish();passed(p.name,completion=v)
        for phase,want in [('pending_created','old'),('published','new')]:
            p=root('close-'+phase);q=Owner(p,bad('stop-'+phase));q.load();q.call('replace',file=str(inputs['new']));v,fd=q.held();q.call('replace',file=str(inputs['intermediate']))
            stopped=q.call('close');assert stopped['retained_bytes']==0 and stopped['pending']=='0';q.drain('closed');assert q.call('take') is None
            assert q.call('replace',file=str(inputs['old']))['error']=='recovery_queue.denied';poller=select.poll();poller.register(fd,select.POLLIN);assert poller.poll(1000);check(p,want);q.finish();os.close(fd);passed(p.name,held=v)
        p=root('drop-loaded-buffer');q=Owner(p);q.drain();assert q.call('status')['retained_bytes']==len(RECORDS['old']);q.call('close');assert q.call('status')['retained_bytes']==0 and q.call('take') is None;q.finish();check(p,'old');passed(p.name)
        for grants,operation in [('we',None),('re','replace'),('rw','retire')]:
            p=root('grant-'+grants);q=Owner(p,grants=grants,good=operation is not None)
            if operation is None:assert q.initial['error']=='recovery_queue.denied';assert q.proc.wait(timeout=3)==1
            else:q.load();assert q.call(operation,file=str(inputs['new']))['error']=='recovery_queue.denied'
            q.finish();check(p,'old');passed(p.name)
        p=root('bounds-and-thread');q=Owner(p);q.load()
        for name in ('empty','oversized'):assert q.call('replace',file=str(inputs[name]))['error']=='recovery_queue.size'
        assert q.call('wrong-thread')['error']=='recovery_queue.owner';q.finish();check(p,'old');passed(p.name)
        for name,raw in [('empty-record',b''),('opaque-bytes',b'\0\xff\xfeopaque\0')]:
            p=root(name,None);write(p/'draft.json',raw);q=Owner(p);q.load(raw)
            if raw:
                payload=folder/'opaque.input';write(payload,raw);q.call('replace',file=str(payload));q.drain();assert q.call('take')['digest']==sha(raw)
            q.call('retire');q.drain('retired');assert q.call('take')['outcome']=='durable';q.finish();check(p,None);passed(name)
        p=root('refused-before-grant');p.chmod(0o755);q=Owner(p);q.drain('unavailable');v=q.call('take');assert v['outcome']=='unchanged' and v['error']=='recovery_store.permissions';q.finish();p.chmod(0o700);check(p,'old');passed(p.name,completion=v,rejected_mode=0o755)
        for mode in ('stale-grant','forged-binding','forged-ticket','duplicate-result','trailing-result','oversized-reply','nonzero-after-result','hung-worker'):
            p=root('bad-'+mode,None);q=Owner(p,bad(mode));started=time.monotonic();v=q.drain('unavailable');done=q.call('take');assert done is not None and done['outcome']=='unchanged' and done['bytes'] is None
            if mode=='hung-worker':assert time.monotonic()-started>=CASES['deadline_ms']/1000 and v['error']=='recovery_queue.timeout'
            q.finish();check(p,None);passed(p.name,status=v,completion=done)
        for change in ('guard','binding','ticket','denial'):
            p=root('worker-grant-'+change);a,b=socket.socketpair();a.settimeout(8)
            child=subprocess.Popen([str(worker),str(os.getpid())],stdin=b,stdout=b,stderr=subprocess.PIPE,env={'LANG':'C.UTF-8'});b.close()
            def send(header,raw=b''):
                payload=encoded(header)+b'\0'+raw;a.sendall(struct.pack('!I',len(payload))+payload)
            def receive():
                def exact(n):
                    out=b''
                    while len(out)<n:
                        block=a.recv(n-len(out));assert block;out+=block
                    return out
                size=struct.unpack('!I',exact(4))[0];assert size<=CASES['frame_limit'];raw=exact(size);head,body=raw.split(b'\0',1);return json.loads(head),body
            try:
                request=dict(kind='request',binding=binding,ticket='2',operation='replace',root=str(p),expected=sha(RECORDS['old']));send(request,RECORDS['new']);grant,raw=receive();assert not raw and grant['kind']=='guard' and grant['guard']=='1'
                grant.update(kind='grant',allow=True)
                if change=='denial':grant['allow']=False
                elif change=='binding':grant['binding']=dict(binding,session='editor:stale')
                else:grant[change]='0'
                send(grant);result,raw=receive();assert result['outcome']=='unchanged' and result['error']=='recovery_store.denied' and not raw;assert child.wait(timeout=3)==0;check(p,'old');passed(p.name,result=result)
            finally:
                a.close()
                if child.poll() is None:child.kill();child.wait(timeout=3)
                write(folder/(p.name+'.stderr'),child.stderr.read())
        p=root('parent-death');q=Owner(p,bad('stop-pending_created'));q.load();q.call('replace',file=str(inputs['new']));v,fd=q.held();q.proc.kill();assert q.proc.wait(timeout=3)==-signal.SIGKILL
        poller=select.poll();poller.register(fd,select.POLLIN);assert poller.poll(3000),'worker survived native parent death';os.close(fd);check(p,'old');q.finish();passed(p.name,held=v,owner_exit=q.proc.returncode)
        p=root('wrong-bytes');detected=False
        try:check(p,'new')
        except AssertionError:detected=True
        assert detected;check(p,'old');passed(p.name,fault_detected=True)
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        for q in children:
            if q.proc.poll() is None:q.proc.kill();q.proc.wait(timeout=4)
            path=folder/(q.p.name+'-'+str(q.proc.pid)+'.events.json')
            if not path.exists():write(path,encoded(q.events))
        report['files']={p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file() and not p.is_symlink()}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()

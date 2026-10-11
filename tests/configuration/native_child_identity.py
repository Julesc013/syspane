"""Observe a real sealed image child, literal pixels and exact pidfd exit."""
from pathlib import Path
import fcntl,hashlib,json,os,select,signal,struct,subprocess,sys,time
from child_identity import observe_child_identity

def main():
    assert os.geteuid()!=0
    worker=Path(sys.argv[1]).resolve();raw=worker.read_bytes()
    sealed=os.memfd_create('syspane-image-worker',os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
    child=None;pidfd=None
    try:
        with os.fdopen(os.dup(sealed),'wb') as out:out.write(raw)
        fcntl.fcntl(sealed,fcntl.F_ADD_SEALS,15)
        assert fcntl.fcntl(sealed,fcntl.F_GET_SEALS)&15==15
        child=subprocess.Popen(['syspane-image-worker','image/png',str(os.getpid())],executable='/proc/self/fd/'+str(sealed),pass_fds=(sealed,),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pidfd=os.pidfd_open(child.pid);deadline=time.monotonic()+2;identity=None;attempts={}
        while identity is None:
            value=observe_child_identity(child.pid,pidfd,os.getpid());identity=value.record
            if identity is None:attempts[value.reason]=attempts.get(value.reason,0)+1
            assert time.monotonic()<deadline and child.poll() is None,'real child identity deadline'
            if identity is None:time.sleep(.001)
        assert identity['argv']==['syspane-image-worker','image/png',str(os.getpid())]
        if identity['sha256'] is not None:assert identity['sha256']==hashlib.sha256(raw).hexdigest()
        else:assert identity['image']=='sandboxed:syspane-image-worker'
        png=(Path(__file__).resolve().parents[1]/'scene/image-cases/rgba.png').read_bytes()
        output,error=child.communicate(struct.pack('!I',len(png))+png,timeout=3)
        assert child.returncode==0 and not error,(child.returncode,error)
        expected=b'SPIM0001'+struct.pack('!II',2,2)+bytes([255,0,0,255,0,128,0,128,0,0,0,0,255,255,255,255])
        assert output==expected,'literal sealed worker pixels'
        assert select.select([pidfd],[],[],0)[0],'real pidfd exit required'
        assert observe_child_identity(child.pid,pidfd,os.getpid()).record is None,'exited fd cannot supply live identity'
        print(json.dumps(dict(outcome='pass',worker_sha256=hashlib.sha256(raw).hexdigest(),observed=identity,unqualified=attempts,seals=15,literal_pixels=True,actual_pidfd_exit=True)))
    finally:
        if child and child.poll() is None:
            if pidfd is not None:signal.pidfd_send_signal(pidfd,signal.SIGKILL)
            else:child.kill()
            child.communicate(timeout=3)
        if pidfd is not None:os.close(pidfd)
        os.close(sealed)

if __name__=='__main__':main()

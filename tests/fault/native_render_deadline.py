"""Queued late health messages cannot override native render/health expiry."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import socket
import struct
import subprocess
import sys
import time
import uuid
import zipfile

ROOT=Path(__file__).resolve().parents[2]
clock=lambda:time.monotonic_ns()//1_000_000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def run(build):
    assert build.is_absolute() and build.resolve(strict=True)==build and build.stat().st_uid==os.getuid()
    binary=build/'SysPane.RecoveryProbe'; evidence=build/'native-evidence'
    workspace=evidence/('RENDER-DEADLINE-'+uuid.uuid4().hex); workspace.mkdir(mode=0o700)
    inputs={p.relative_to(ROOT).as_posix():sha(p) for folder in ('source','tests/fault','spec/contracts')
            for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    inputs.update({p:sha(ROOT/p) for p in ('CMakeLists.txt','build-support/components.json','build-support/targets/linux-x64-gcc13.json','spec/delivery/packages/w-25-gnome-render-watch.md')})
    archive=workspace/'source-inputs.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in inputs:z.write(ROOT/p,p)
    report={'family':'RENDER-DEADLINE','source_inputs':inputs,'source_archive':str(archive),'source_archive_sha256':sha(archive),
            'artifact':{'path':str(binary),'sha256':sha(binary)},'executed_at':datetime.now(timezone.utc).isoformat(),'cases':[]}
    runtime=Path.home()/'.cache/syspane/ipc-w24'
    assert runtime.resolve(strict=True)==runtime and runtime.stat().st_uid==os.getuid() and runtime.stat().st_mode&0o777==0o700
    for mode in ('late-progress','late-heartbeat','late-shutdown'):
        directory=runtime/('case-'+uuid.uuid4().hex[:12]);directory.mkdir(mode=0o700)
        endpoint=directory/'s';journal_path=workspace/(mode+'.jsonl');child=None;fd=None;client=None;stopped=False
        case={'mode':mode,'command':[str(binary),'render-watch',str(endpoint),str(journal_path)]};report['cases'].append(case)
        def journal():
            raw=journal_path.read_bytes() if journal_path.exists() else b''
            assert len(raw)<=65536
            return [json.loads(line) for line in raw.splitlines(keepends=True) if line.endswith(b'\n')]
        def wait_for(predicate,seconds=2):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                value=predicate()
                if value:return value
                time.sleep(.005)
            raise AssertionError('native deadline observer timeout')
        try:
            child=subprocess.Popen(case['command'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            fd=os.pidfd_open(child.pid);case['pid']=child.pid
            wait_for(lambda:endpoint.exists() and journal())
            assert endpoint.stat().st_uid==os.getuid() and endpoint.stat().st_mode&0o777==0o600
            client=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);client.settimeout(2);client.connect(str(endpoint))
            peer=struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert peer[0]==child.pid and peer[1]==os.getuid()
            case['peer_pid']=peer[0]
            def send(message):
                raw=json.dumps(message,separators=(',',':')).encode();assert len(raw)<=4096
                client.sendall(struct.pack('!I',len(raw))+raw)
            send({'type':'hello','body':{'wire_major':0,'wire_minor':1,'role':'desktop','producer_epoch':'test:render','max_frame_bytes':4096,
                'document_versions':[{'document':'recovery-health','version':'0.1.0'}],'required_features':['recovery.health','recovery.progress'],'optional_features':[]}})
            buffer=b'';welcome=None;challenge=None;handshake_deadline=time.monotonic()+2
            while challenge is None:
                assert time.monotonic()<handshake_deadline, 'handshake deadline'
                chunk=client.recv(4096);assert chunk, 'handshake EOF'
                buffer+=chunk
                while len(buffer)>=4:
                    size=struct.unpack('!I',buffer[:4])[0];assert 0<size<=4096
                    if len(buffer)<size+4:break
                    message=json.loads(buffer[4:4+size]);buffer=buffer[4+size:]
                    if message['type']=='welcome':welcome=message
                    elif message['type']=='render.challenge':challenge=message
            assert welcome and challenge['body']['generation']=='1'
            def message(kind,body):return {'type':kind,'body':body,'connection_id':welcome['connection_id'],'producer_epoch':welcome['producer_epoch']}
            send(message('heartbeat',{'sequence':'0'}))
            wait_for(lambda:any(r['event']=='heartbeat' and r['direction']=='received' for r in journal()))
            if mode=='late-heartbeat':
                send(message('render.progress',{'generation':'1'}))
                wait_for(lambda:any(r['event']=='progress' for r in journal()))
            assert not select.select([fd],[],[],0)[0]
            signal.pidfd_send_signal(fd,signal.SIGSTOP);stopped=True
            wait_for(lambda:Path(f'/proc/{child.pid}/stat').read_text().rsplit(')',1)[1].split()[0] in ('T','t'))
            case['stop_ms']=clock();before=journal()
            issue=next(r['issued_ms'] for r in before if r['event']=='challenge')
            heartbeat=next(r['observed_ms'] for r in reversed(before) if r['event']=='heartbeat' and r['direction']=='received')
            origin=heartbeat if mode=='late-heartbeat' else issue
            wait_for(lambda:clock()>=origin+3100,seconds=4)
            kind,body={'late-progress':('render.progress',{'generation':'1'}),'late-heartbeat':('heartbeat',{'sequence':'1'}),'late-shutdown':('shutdown',{'reason':'normal'})}[mode]
            send(message(kind,body));case['queued_ms']=clock()
            signal.pidfd_send_signal(fd,signal.SIGCONT);stopped=False;case['resume_ms']=clock()
            assert select.select([fd],[],[],2)[0], 'held watcher exit required'
            output,error=child.communicate(timeout=1);case.update(exit=child.returncode,pidfd_exit=True,exit_ms=clock())
            assert len(output)<=16384 and len(error)<=4096
            case.update(stdout=output.decode(),stderr=error.decode(),journal=journal())
            assert child.returncode==1, 'late shutdown cannot hide expiry'
            faults=[r for r in case['journal'] if r['event']=='fault']
            assert len(faults)==1, 'original latched deadline fault required'
            fault=faults[0];expected='health.expired' if mode=='late-heartbeat' else 'render.stalled'
            assert fault['reason']==expected and case['queued_ms']>=origin+3000
            assert case['resume_ms']<=fault['observed_ms']<=case['resume_ms']+200
            assert fault['completed']==int(mode=='late-heartbeat') and fault['pending']==(None if mode=='late-heartbeat' else 1)
            assert case['journal'][-1]==fault and not any(r['event']=='complete' for r in case['journal'])
            case['outcome']='pass'
        except Exception as error:
            case.update(outcome='fail',error=type(error).__name__+': '+str(error))
        finally:
            if fd is not None and stopped and not select.select([fd],[],[],0)[0]:signal.pidfd_send_signal(fd,signal.SIGCONT)
            if client:client.close()
            if child and child.poll() is None:
                if not select.select([fd],[],[],1)[0]:signal.pidfd_send_signal(fd,signal.SIGKILL)
                output,error=child.communicate(timeout=2);case.update(exit=child.returncode,cleanup_stdout=output.decode(),cleanup_stderr=error.decode())
            if fd is not None:os.close(fd)
            if endpoint.exists():
                assert endpoint.parent.resolve(strict=True)==directory and endpoint.is_socket() and endpoint.stat().st_uid==os.getuid()
                endpoint.unlink()
            directory.rmdir()
            case['cleanup']='owned child exited and endpoint removed'
    report['outcome']='pass' if all(c['outcome']=='pass' for c in report['cases']) else 'fail'
    path=workspace/'result.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(path);print([(r['mode'],r['outcome'],r.get('error')) for r in report['cases']])
    return 0 if report['outcome']=='pass' else 1


if __name__=='__main__':sys.exit(run(Path(sys.argv[1])))

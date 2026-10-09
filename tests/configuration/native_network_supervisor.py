"""Sealed installed service: exact child exit, replacement and guardian lifetime."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import select
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
import uuid
from native_network_service import Node, encoded, sha, linux_rows, verify_documents

def main():
    probe, evidence = map(lambda p: Path(p).resolve(), sys.argv[1:3]); build=probe.parent
    assert os.geteuid() and evidence.parent==build
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    folder=evidence/('network-supervisor-'+uuid.uuid4().hex[:8]); folder.mkdir(mode=0o700,parents=True)
    runtime=build.parent/('v-'+uuid.uuid4().hex[:6]); runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(family='NETWORK-SUPERVISOR',evidence=str(folder))))
    bundle=folder/'relocated'; bundle.mkdir()
    files={'bin/syspane':probe,'libexec/syspane/syspane-configuration-host':build/'syspane_frontend_helper_fixture',
           'libexec/syspane/syspane-image-worker':build/'SysPane.ImageWorker',
           'libexec/syspane/syspane-recovery-worker':build/'SysPane.RecoveryWorker',
           'share/syspane/helpers.json':build/'generated/frontend-fixture/helpers.json'}
    for name,source in files.items():
        dest=bundle/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644 if name.endswith('.json') else 0o755)
    record=dict(family='NETWORK-SUPERVISOR',outcome='fail',artifacts={k:sha(v) for k,v in files.items()},
                oracle=sha(Path(__file__)),cases=[],runs=[])
    def save(): (folder/'result.json').write_bytes(encoded(record))
    def passed(name,**facts): record['cases'].append(dict(case=name,outcome='pass',**facts));save()
    drivers=[]
    class Driver:
        def __init__(self):
            self.root=runtime/str(len(drivers));self.root.mkdir(mode=0o700)
            self.cwd=folder/str(len(drivers));self.cwd.mkdir(mode=0o700);(self.cwd/'policy').write_text('allow')
            self.events=[];self.pending=b'';self.handles={};self.error=(self.cwd/'stderr').open('wb')
            self.process=subprocess.Popen([str(bundle/'bin/syspane'),str(self.root),str(os.getpid())],cwd=self.cwd,
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.error,close_fds=True)
            drivers.append(self);record['runs'].append(dict(pid=self.process.pid,events=self.events))
        def pump(self):
            if select.select([self.process.stdout],[],[],.003)[0]:self.pending+=os.read(self.process.stdout.fileno(),65536)
            while b'\n' in self.pending:
                line,self.pending=self.pending.split(b'\n',1);value=json.loads(line);self.events.append(value)
                pid=value['pid']
                if pid and pid not in self.handles:
                    self.handles[pid]=os.pidfd_open(pid)
                if value['event']=='ready':
                    value['native_executable']=os.readlink('/proc/'+str(pid)+'/exe')
                    value['native_arguments']=Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')[:-1]
                    value['native_arguments']=[arg.decode() for arg in value['native_arguments']]
                    assert value['native_executable']=='/memfd:syspane-configuration-host (deleted)'
                    assert value['native_arguments']==['syspane-network-host','--network',str(self.process.pid)]
        def until(self,predicate,seconds=8):
            end=time.monotonic()+seconds
            while not predicate():
                assert time.monotonic()<end,'supervisor observation deadline'
                self.pump()
        def ready(self,count=1):
            self.until(lambda: len([e for e in self.events if e['event']=='ready'])>=count)
            return [e for e in self.events if e['event']=='ready'][count-1]
        def dead(self,pid):return bool(select.select([self.handles[pid]],[],[],0)[0])
        def collect(self,event):
            c=SimpleNamespace(folder=Path(event['endpoint']).parent,process=SimpleNamespace(pid=event['pid']),epoch=event['epoch'],data=None)
            c.message=lambda kind,body:dict(type=kind,body=body,connection_id='C',producer_epoch=c.epoch)
            before=linux_rows();lower=time.clock_gettime_ns(time.CLOCK_BOOTTIME);Node.connect(c);Node.subscribe(c)
            rows=[];sequence=0;last=0;end=time.monotonic()+5
            while len(rows)<2:
                assert time.monotonic()<end,'measured service publication deadline'
                self.pump();c.data.pump();assert not c.data.eof
                if time.monotonic()-last>=.4:
                    c.data.send(c.message('heartbeat',dict(sequence=str(sequence))));sequence+=1;last=time.monotonic()
                while c.data.messages:
                    value=c.data.messages.pop(0)
                    if value['type']=='snapshot':rows.append(dict(event='imported',body=json.dumps(value['body']),duplicate=False,now_ns=time.clock_gettime_ns(time.CLOCK_BOOTTIME)))
            after=linux_rows();upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            verify_documents(SimpleNamespace(lines=rows),before,after,lower,upper,'live')
            record['runs'][drivers.index(self)].setdefault('snapshots',[]).extend(rows);save();return c
        def close(self):
            self.process.stdin.write(b'close\n');self.process.stdin.flush();self.until(lambda:self.process.poll() is not None)
            self.pump();assert self.process.returncode==0 and not list(self.root.iterdir())
            assert all(self.dead(pid) for pid in self.handles)
        def dispose(self):
            if self.process.poll() is None:self.process.kill()
            self.process.wait(timeout=3)
            for pid,fd in self.handles.items():
                if not self.dead(pid):signal.pidfd_send_signal(fd,signal.SIGKILL)
                assert select.select([fd],[],[],3)[0];os.close(fd)
            self.process.stdin.close();self.process.stdout.close();self.error.close()
    try:
        d=Driver();first=d.ready()
        # A foreign PID cannot become the declared console, even with same uid/session.
        outsider=subprocess.run([sys.executable,'-c','import socket,sys; s=socket.socket(socket.AF_UNIX);s.connect(sys.argv[1]);s.settimeout(2);assert s.recv(1)==b""',first['endpoint']],capture_output=True,timeout=3)
        assert outsider.returncode==0;passed('WRONG-PID')
        c=d.collect(first);passed('SEALED-LIVE')
        signal.pidfd_send_signal(d.handles[first['pid']],signal.SIGKILL);second=d.ready(2)
        assert d.dead(first['pid']) and first['epoch']!=second['epoch'] and first['pid']!=second['pid']
        assert next(i for i,e in enumerate(d.events) if e['event']=='reaped')<next(i for i,e in enumerate(d.events) if e['event']=='launched' and e['pid']==second['pid'])
        c.data.socket.close();c=d.collect(second);passed('CRASH-RESTART')
        d.close();c.data.socket.close();passed('CLOSE-REAP-CLEANUP')
        d=Driver();first=d.ready();c=d.collect(first);d.process.kill();d.process.wait(timeout=2)
        assert select.select([d.handles[first['pid']]],[],[],2)[0];c.data.socket.close();passed('GUARDIAN-DEATH')
        record['outcome']='pass'
    except BaseException:record['error']=traceback.format_exc();raise
    finally:
        for d in drivers:d.dispose()
        save();print(json.dumps(dict(outcome=record['outcome'],cases=len(record['cases']),record=str(folder/'result.json'))))

if __name__=='__main__':main()

"""Independent peers and kernel counters for the production native consumer."""
from pathlib import Path
from types import SimpleNamespace
import copy,json,os,select,shutil,socket,struct,subprocess,sys,time,traceback,uuid
from native_network_service import Pipe,encoded,sha,linux_rows,verify_documents

ROOT=Path(__file__).resolve().parents[2]
def main():
    probe,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:3]);build=probe.parent
    assert os.geteuid() and evidence.parent==build
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    folder=evidence/('network-consumer-'+uuid.uuid4().hex[:8]);folder.mkdir(mode=0o700,parents=True)
    runtime=build.parent/('c-'+uuid.uuid4().hex[:6]);runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(family='NETWORK-CONSUMER',evidence=str(folder))))
    bundle=folder/'relocated';bundle.mkdir()
    files={'bin/syspane':probe,'libexec/syspane/syspane-configuration-host':build/'syspane_frontend_helper_fixture',
           'libexec/syspane/syspane-image-worker':build/'SysPane.ImageWorker',
           'libexec/syspane/syspane-recovery-worker':build/'SysPane.RecoveryWorker',
           'share/syspane/helpers.json':build/'generated/frontend-fixture/helpers.json'}
    for name,source in files.items():
        dest=bundle/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644 if name.endswith('.json') else 0o755)
    record=dict(family='NETWORK-CONSUMER',outcome='fail',artifacts={k:sha(v) for k,v in files.items()},
                oracle=sha(Path(__file__)),cases=[],runs=[])
    def save():(folder/'result.json').write_bytes(encoded(record))
    def passed(name,**facts):record['cases'].append(dict(case=name,outcome='pass',**facts));save()
    drivers=[]
    class Driver:
        def __init__(self,args=None):
            self.root=runtime/str(len(drivers));self.root.mkdir(mode=0o700)
            self.cwd=folder/str(len(drivers));self.cwd.mkdir(mode=0o700);(self.cwd/'policy').write_text('allow')
            self.events=[];self.pending=b'';self.handles={};self.error=(self.cwd/'stderr').open('wb')
            self.process=subprocess.Popen([str(bundle/'bin/syspane')]+(args or [str(self.root),'live']),cwd=self.cwd,
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.error,close_fds=True)
            drivers.append(self);record['runs'].append(dict(pid=self.process.pid,events=self.events))
        def pump(self):
            if select.select([self.process.stdout],[],[],.003)[0]:self.pending+=os.read(self.process.stdout.fileno(),65536)
            while b'\n' in self.pending:
                line,self.pending=self.pending.split(b'\n',1);v=json.loads(line);self.events.append(v)
                if v['event']=='ready' and v['pid'] not in self.handles:self.handles[v['pid']]=os.pidfd_open(v['pid'])
        def until(self,predicate,seconds=8):
            end=time.monotonic()+seconds
            while not predicate():
                assert time.monotonic()<end,'consumer observation deadline';self.pump()
        def frames(self):return [e for e in self.events if e['event']=='frame']
        def finish(self,code=0):
            self.until(lambda:self.process.poll() is not None);self.pump();assert self.process.returncode==code
        def close(self):
            self.process.stdin.write(b'close\n');self.process.stdin.flush();self.finish()
            assert not list(self.root.iterdir()) and all(select.select([fd],[],[],0)[0] for fd in self.handles.values())
        def dispose(self):
            if self.process.poll() is None:self.process.kill()
            self.process.wait(timeout=3)
            for fd in self.handles.values():assert select.select([fd],[],[],3)[0];os.close(fd)
            self.process.stdin.close();self.process.stdout.close();self.error.close()
    try:
        before=linux_rows();lower=time.clock_gettime_ns(time.CLOCK_BOOTTIME);d=Driver()
        d.until(lambda:len(d.frames())>=2);after=linux_rows();upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        rows=[]
        for f in d.frames():
            raw=json.loads(f['raw']);assert raw['producer_epoch']==f['epoch']
            assert int(f['receipt_ns'])<=int(f['clock_ns'])<=upper
            assert f['receipt_ms']<=f['clock_ms']<f['deadline'] and f['profile']==11 and f['generation']==4
            rows.append(dict(event='imported',body=json.dumps(raw['body']),duplicate=False,now_ns=int(f['receipt_ns'])))
        verify_documents(SimpleNamespace(lines=rows),before,after,lower,upper,'live');passed('LIVE');passed('RECEIPT')
        wrong=copy.deepcopy(rows);body=json.loads(wrong[0]['body']);body['snapshot']['observations'][0]['value']['data']=str(2**64-1);wrong[0]['body']=json.dumps(body)
        try:verify_documents(SimpleNamespace(lines=wrong),before,after,lower,upper,'live')
        except AssertionError:passed('ORACLE')
        else:raise AssertionError('wrong counter accepted')
        d.close();passed('CLOSE-REAP')
        d=Driver();d.until(lambda:bool(d.frames()));(d.cwd/'policy').write_text('deny')
        d.finish();assert any(e['event']=='reaped' and e['exit']==126 for e in d.events);passed('POLICY-WITHDRAWAL')
        # A separately implemented, native-authenticated peer supplies invalid
        # negotiations and impossible measurements to the same production client.
        for variant in ('valid','future','wrong-role','wrong-epoch','unsolicited-heartbeat','wrong-pid'):
            peer_root=runtime/('p-'+variant);peer_root.mkdir(mode=0o700);path=peer_root/'s'
            listener=socket.socket(socket.AF_UNIX);listener.bind(str(path));path.chmod(0o600);listener.listen(1);listener.settimeout(5)
            expected=os.getpid() if variant!='wrong-pid' else os.getpid()+1000000
            d=Driver(['--peer',str(path),str(expected),'native:test']);sock,_=listener.accept();sock.setblocking(True);pipe=Pipe(sock)
            end=time.monotonic()+5
            while not pipe.messages and not pipe.eof and d.process.poll() is None:
                assert time.monotonic()<end;pipe.pump();d.pump()
            if variant=='wrong-pid':d.finish(1);assert not d.frames();passed('WRONG-PID');sock.close();listener.close();continue
            offer=pipe.messages.pop(0);assert offer['type']=='hello' and offer['body']['role']=='console'
            pid,uid,_=struct.unpack('3i',sock.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==d.process.pid and uid==os.getuid()
            epoch='wrong' if variant=='wrong-epoch' else 'native:test'
            body=dict(offer['body'],role='desktop' if variant=='wrong-role' else 'console',producer_epoch=epoch,
                      required_features=[],optional_features=offer['body']['required_features'])
            pipe.send(dict(type='welcome',connection_id='C',producer_epoch=epoch,body=body))
            if variant not in ('wrong-role','wrong-epoch'):
                while not any(v['type']=='subscribe' for v in pipe.messages):
                    assert time.monotonic()<end;pipe.pump();d.pump()
                if variant=='unsolicited-heartbeat':pipe.send(dict(type='heartbeat',connection_id='C',producer_epoch=epoch,body=dict(sequence='18446744073709551615')))
                else:
                    value=json.loads((ROOT/'spec/fixtures/valid/telemetry-snapshot-v0.2.json').read_bytes())
                    value['connection_id']='C';value['producer_epoch']=epoch;value['body'].update(subscription_id='S',producer_id='producer:network',clock_id='linux.boottime')
                    snapshot=value['body']['snapshot'];snapshot['producer_epoch']=epoch;o=snapshot['observations'][0]
                    o.update(producer_epoch=epoch,field='network.receive_bytes',unit='byte',value=dict(kind='uint64',data='123'))
                    o['measured_at']=dict(clock_id='linux.boottime',nanoseconds=str(time.clock_gettime_ns(time.CLOCK_BOOTTIME)+(10**12 if variant=='future' else 0)))
                    raw=encoded(value);sock.sendall(struct.pack('!I',len(raw))+raw)
                    if variant=='valid':
                        d.until(lambda:bool(d.frames()));assert d.frames()[0]['raw'].encode()==raw;passed('ORIGINAL-BYTES');d.process.stdin.write(b'close\n');d.process.stdin.flush();d.finish();sock.close();listener.close();continue
            d.finish(1);assert not d.frames();passed(variant.upper());sock.close();listener.close()
        record['outcome']='pass'
    except BaseException:record['error']=traceback.format_exc();raise
    finally:
        for d in drivers:d.dispose()
        save();print(json.dumps(dict(outcome=record['outcome'],cases=len(record['cases']),record=str(folder/'result.json'))))
if __name__=='__main__':main()

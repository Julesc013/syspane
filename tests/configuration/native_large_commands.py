"""Independent full-scene bytes, native IPC, coherent recovery and GUI oracle."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,queue,select,signal,socket,struct,subprocess,sys,threading,time,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/editor'),str(ROOT/'tests/configuration')]
from native_editor import observe,launch_xvfb
from native_settings import check_resources
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
CASES=json.loads((ROOT/'tests/configuration/large-command-cases.json').read_bytes())
FIXTURE=json.loads((ROOT/'tests/configuration/settings-content-fixture.json').read_bytes())
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def accepted(v):assert v['outcome']=='accepted' and v['revision']=='41' and v['stored'] is True and v['durable'] is True and v['visible'] is False
def request(scene,revision='40',request_id='R'):
    return dict(schema_version='0.5.0',request_id=request_id,expected_revision=revision,policy_generation='7',intent='commit',content=FIXTURE['selection'],operations=[dict(op='scene.replace',scene=scene)])
def full_body(q):
    raw=encoded(q);assert len(raw)<=327680;return raw[:-1]+b' '*(327680-len(raw))+b'}'
def generation(directory,previous=False):
    pointer=json.loads((directory/('previous.json' if previous else 'current.json')).read_bytes());g=directory/pointer['generation']
    assert g.parent==directory and sha(g/'manifest.json')==pointer['manifest'];return g,json.loads((g/'manifest.json').read_bytes())
def receipt(directory,body,previous=False):
    g,m=generation(directory,previous)
    assert m['version']=='0.3.0' and set(m)=={'version','revision','settings','scene','identity','resources'}
    assert set(m['identity'])=={'principal','epoch','request','body_sha256'}
    assert (g/'request.json').read_bytes()==body and sha(g/'request.json')==m['identity']['body_sha256']
    assert len(body)<=327680 and len((g/'manifest.json').read_bytes())<=65536
    assert set(p.name for p in g.iterdir())=={'settings.json','scene.json','manifest.json','request.json','resources.json','resources'}
    for n in ('settings','scene'):assert sha(g/(n+'.json'))==m[n]
    if not previous:check_resources(directory,manifest_version='0.3.0')
    return g,m
class Store:
    def __init__(self,exe,folder):
        self.exe,self.folder=exe,folder;folder.mkdir(mode=0o700);self.path=folder/'store';self.path.mkdir(mode=0o700)
        self.imports=[];self.catalog=folder/'imports';self.catalog.mkdir(mode=0o700)
        for n,pkg in enumerate(FIXTURE['packages']):
            p=self.catalog/str(n);p.mkdir(mode=0o700);self.imports.append(p);write(p/'manifest.json',pkg['manifest'].encode())
            for name,raw in pkg['assets_hex'].items():
                dest=p/name;dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True);write(dest,bytes.fromhex(raw))
        write(self.catalog/'catalog.json',encoded(dict(schema_version='0.1.0',packages=[p.name for p in self.imports])))
        s=json.loads((ROOT/'spec/fixtures/valid/settings.json').read_bytes());v=json.loads((ROOT/'spec/fixtures/valid/scene-portable.json').read_bytes());s['revision']=v['revision']='39'
        write(folder/'settings.json',encoded(s));write(folder/'scene.json',encoded(v));self.call('init',folder/'settings.json',folder/'scene.json')
        initial=copy.deepcopy(CASES['authored']['scene']);initial['revision']='39';self.bootstrap=encoded(request(initial,'39','bootstrap'));write(folder/'bootstrap.json',self.bootstrap)
        result=self.call('content-commit',folder/'bootstrap.json','-',*self.imports)['result'];assert result['outcome']=='accepted' and result['revision']=='40'
        self.body=full_body(request(CASES['moved_scene']));write(folder/'command.json',self.body);self.inspect(40)
    def call(self,*args):
        result=subprocess.run([str(self.exe),str(self.path),*map(str,args)],capture_output=True,text=True,timeout=8)
        assert result.returncode==0,(args,result.returncode,result.stderr);return json.loads(result.stdout)
    def args(self,phase='-'):return [str(self.exe),str(self.path),'content-commit',str(self.folder/'command.json'),phase,*map(str,self.imports)]
    def commit(self,phase='-'):return self.call('content-commit',self.folder/'command.json',phase,*self.imports)['result']
    def inspect(self,revision,fallback=False):
        actual=self.call('read');scene=copy.deepcopy(CASES['moved_scene'] if revision==41 else CASES['authored']['scene']);settings=copy.deepcopy(CASES['authored']['settings'])
        scene['revision']=settings['revision']=str(revision)
        assert actual['settings']==settings and actual['scene']==scene and actual['recovered_previous']==fallback,'coherent documents differ'
        receipt(self.path,self.body if revision==41 else self.bootstrap,fallback)
        return actual
class Client:
    def __init__(self,ready,large=True):
        self.epoch=ready['epoch'];self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.settimeout(5);self.socket.connect(ready['endpoint'])
        assert struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==ready['pid']
        docs=[dict(document=n,version=v) for n,v in [('command','0.5.0'),('command-result','0.1.0'),('reconciliation-request','0.1.0'),('reconciliation-result','0.1.0')]]
        self.send('hello',dict(wire_major=0,wire_minor=1,role='console',producer_epoch='client',max_frame_bytes=328704,document_versions=docs,required_features=['configuration.transactions','result.reconcile'],optional_features=['configuration.content','configuration.scene-content','cancel','result.get']+(['configuration.large-commands'] if large else [])))
        assert self.receive()['type']=='welcome'
    def send(self,kind,value,raw=False):
        if raw:
            body=b'{"type":"command","connection_id":"C","producer_epoch":'+encoded(self.epoch)+b',"body":'+value+b'}'
        else:
            obj=dict(type=kind,body=value)
            if kind!='hello':obj.update(connection_id='C',producer_epoch=self.epoch)
            body=encoded(obj)
        assert len(body)<=328704;self.socket.sendall(struct.pack('!I',len(body))+body)
    def receive(self):
        def exact(n):
            b=b''
            while len(b)<n:
                item=self.socket.recv(n-len(b));assert item,'unexpected EOF';b+=item
            return b
        size=struct.unpack('!I',exact(4))[0];assert 0<size<=328704;v=json.loads(exact(size));assert v['connection_id']=='C' and v['producer_epoch']==self.epoch;return v
    def reconcile(self,epoch):
        q=dict(schema_version='0.1.0',query_id='Q',original_producer_epoch=epoch,request_id='R');self.send('result.reconcile',q);v=self.receive();assert v['type']=='result.reconciled' and all(v['body'][k]==x for k,x in q.items());return v['body']['result']
    def close(self):self.socket.close()
class Supervisor:
    def __init__(self,exe,store,scenario='normal',permission='allow'):
        runtime=Path.home()/'.cache/syspane/ipc-w24'/('large-'+uuid.uuid4().hex[:8]);runtime.mkdir(mode=0o700)
        self.events=queue.Queue();self.log=[];self.children={};self.clients=[]
        self.p=subprocess.Popen([str(exe),'content','-','supervisor',str(runtime),str(store),scenario,str(os.getpid()),permission],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        def collect():
            for line in self.p.stdout:
                v=json.loads(line);self.log.append(v);self.events.put(v)
        self.reader=threading.Thread(target=collect,daemon=True);self.reader.start()
    def event(self,name):
        end=time.monotonic()+9
        while time.monotonic()<end:
            try:v=self.events.get(timeout=.1)
            except queue.Empty:continue
            assert v.get('event')!='error',v
            if v.get('event')==name:return v
        raise AssertionError(('event timeout',name,self.log))
    def connect(self,large=True):
        ready=self.event('ready');self.children[ready['pid']]=os.pidfd_open(ready['pid']);client=Client(ready,large);self.clients.append(client);return ready,client
    def stop(self):
        for c in self.clients:c.close()
        self.p.stdin.write('stop\n');self.p.stdin.flush();assert self.p.wait(timeout=4)==0
    def close(self):
        for c in self.clients:c.close()
        if self.p.poll() is None:self.p.kill();self.p.wait(timeout=3)
        for fd in self.children.values():assert select.select([fd],[],[],3)[0];os.close(fd)
        self.reader.join(1);assert not self.reader.is_alive()
def native(exe,probe,folder,report):
    # The new receipt format also supports resource-free legacy scenes.
    bare=folder/'bare-scene';bare.mkdir(mode=0o700);directory=bare/'store';directory.mkdir(mode=0o700)
    settings=json.loads((ROOT/'spec/fixtures/valid/settings.json').read_bytes());scene=json.loads((ROOT/'spec/fixtures/valid/scene-portable.json').read_bytes())
    settings['revision']=scene['revision']='40';write(bare/'settings.json',encoded(settings));write(bare/'scene.json',encoded(scene))
    def call(*args):
        p=subprocess.run([str(probe),str(directory),*map(str,args)],capture_output=True,text=True,timeout=8);assert p.returncode==0,p.stderr;return json.loads(p.stdout)
    call('init',bare/'settings.json',bare/'scene.json')
    expected=copy.deepcopy(scene);expected['widgets'][0]['title']='Resource-free full scene';expected['extensions']={'author.padding':''}
    expected['extensions']['author.padding']='x'*(262144-len(encoded(expected)));assert len(encoded(expected))==262144
    q=request(expected);q.pop('content');body=full_body(q);write(bare/'command.json',body);accepted(call('commit',bare/'command.json')['result'])
    expected['revision']=settings['revision']='41';assert call('read')==dict(settings=settings,scene=expected,recovered_previous=False)
    g,m=generation(directory);assert m['version']=='0.3.0' and 'resources' not in m
    assert set(p.name for p in g.iterdir())=={'settings.json','scene.json','manifest.json','request.json'}
    assert set(m['identity'])=={'principal','epoch','request','body_sha256'} and sha(g/'request.json')==m['identity']['body_sha256'] and (g/'request.json').read_bytes()==body
    accepted(call('reconcile','E1','R')['result']);report['cases'].append(dict(case='bare-scene',outcome='pass'))
    for phase in ('request','manifest','selector_ready','selected','durable'):
        f=Store(probe,folder/('cut-'+phase));p=subprocess.Popen(f.args(phase),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            assert select.select([p.stdout],[],[],5)[0];assert json.loads(p.stdout.readline())==dict(transition=phase)
            end=time.monotonic()+3
            while time.monotonic()<end:
                stopped=os.waitid(os.P_PID,p.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                if stopped:break
                time.sleep(.005)
            assert stopped and stopped.si_status==signal.SIGSTOP;p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
            revision=41 if phase in ('selected','durable') else 40;f.inspect(revision);result=f.call('reconcile','E1','R')['result']
            if revision==41:accepted(result)
            else:assert result['outcome']=='unknown' and result['stored'] is None
            report['cases'].append(dict(case='cut-'+phase,outcome='pass',revision=revision))
        finally:
            if p.poll() is None:p.kill();p.wait(timeout=3)
    for fault in ('changed','missing','oversized','symlink','hardlink','foreign','substituted','revoke'):
        f=Store(probe,folder/fault)
        if fault=='revoke':assert f.commit('revoke')['outcome']=='conflict';f.inspect(40)
        else:
            accepted(f.commit());g,m=receipt(f.path,f.body);path=g/'request.json'
            if fault=='changed':write(path,f.body.replace(b'"request_id":"R"',b'"request_id":"S"'))
            elif fault=='missing':path.unlink()
            elif fault=='oversized':write(path,f.body+b' ')
            elif fault=='symlink':path.unlink();path.symlink_to(f.folder/'command.json')
            elif fault=='hardlink':(f.folder/'linked.json').hardlink_to(path)
            elif fault=='foreign':write(g/'foreign.json',b'{}')
            elif fault=='substituted':
                write(path,f.bootstrap);m['identity']['body_sha256']=sha(path);write(g/'manifest.json',encoded(m));pointer=json.loads((f.path/'current.json').read_bytes());pointer['manifest']=sha(g/'manifest.json');write(f.path/'current.json',encoded(pointer))
            f.inspect(40,True);assert f.call('reconcile','E1','R')['result']['outcome']=='unknown'
        report['cases'].append(dict(case=fault,outcome='pass'))
    for mode in ('ipc-save','ipc-unnegotiated','ipc-deny','ipc-cancel','ipc-durable'):
        f=Store(probe,folder/mode);owner=Supervisor(exe,f.path,'prepare' if mode=='ipc-cancel' else 'durable' if mode=='ipc-durable' else 'normal','deny' if mode=='ipc-deny' else 'allow')
        entry=dict(case=mode,outcome='fail');report['cases'].append(entry)
        try:
            ready,client=owner.connect(mode!='ipc-unnegotiated');original=ready['epoch'];client.send('command',f.body,True)
            if mode in ('ipc-unnegotiated','ipc-deny'):
                answer=client.receive()['body'];assert answer['error']['code']==('feature.unsupported' if mode=='ipc-unnegotiated' else 'policy.denied');revision=40
            elif mode in ('ipc-cancel','ipc-durable'):
                owner.event('armed')
                # A large body's validation can outlive arming. Observe the actual
                # non-owner thread's timed sleep in the deliberate hold before cancel.
                end=time.monotonic()+2;held=[]
                while time.monotonic()<end:
                    held=[dict(tid=int(t.name),wchan=(t/'wchan').read_text().strip()) for t in (Path('/proc')/str(ready['pid'])/'task').iterdir() if int(t.name)!=ready['pid']]
                    if any(t['wchan']=='hrtimer_nanosleep' for t in held):break
                    time.sleep(.005)
                assert any(t['wchan']=='hrtimer_nanosleep' for t in held),held;entry['held_worker']=held
                if mode=='ipc-durable':receipt(f.path,f.body)
                client.send('heartbeat',dict(sequence='1'));assert client.receive()['type']=='heartbeat'
                client.send('cancel' if mode=='ipc-cancel' else 'result.get',dict(request_id='R'));assert client.receive()['body']['outcome']=='unknown'
                fault=owner.event('fault');assert fault['reason']=='transaction.deadline';reaped=owner.event('reaped');assert reaped['pid']==ready['pid'] and select.select([owner.children[ready['pid']]],[],[],0)[0]
                ready,client=owner.connect();assert ready['epoch']!=original;result=client.reconcile(original)
                if mode=='ipc-durable':accepted(result);revision=41
                else:assert result['outcome']=='unknown' and result['stored'] is None;revision=40
            else:
                accepted(client.receive()['body']);owner.event('finished');client.send('command',f.body,True);accepted(client.receive()['body'])
                client.send('command',encoded(request(CASES['moved_scene'])),True);assert client.receive()['body']['error']['code']=='request.changed'
                signal.pidfd_send_signal(owner.children[ready['pid']],signal.SIGKILL);owner.event('fault');owner.event('reaped');assert select.select([owner.children[ready['pid']]],[],[],0)[0]
                ready,client=owner.connect();accepted(client.reconcile(original));revision=41
            owner.stop();f.inspect(revision);entry.update(outcome='pass',revision=revision)
        finally:owner.close();entry['events']=owner.log
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5],True);return
    exe,probe,editor,exit_exe,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:6]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('large-commands-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='LARGE-COMMANDS',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),executable_sha256=sha(exe),store_executable_sha256=sha(probe),editor_executable_sha256=sha(editor),fixture_sha256=sha(ROOT/'tests/configuration/large-command-cases.json'),cases=[]);server=None
    try:
        native(exe,probe,folder,report)
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['modes']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(editor),str(exit_exe),str(folder/('gui-'+mode)),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise AssertionError('GUI observer deadline')
            write(folder/(mode+'.stdout'),out);write(folder/(mode+'.stderr'),err);assert child.returncode==0,(mode,err.decode(errors='replace'))
            detail=json.loads((folder/('gui-'+mode)/'result.json').read_bytes());assert detail['outcome']=='pass'
            if mode=='wrong-commit':assert detail['fault_detected']
            g,m=generation(folder/('gui-'+mode)/'store');receipt(folder/('gui-'+mode)/'store',(g/'request.json').read_bytes())
            report['cases'].append(dict(case='gui-'+mode,outcome='pass',fault_detected=detail.get('fault_detected',False),record_sha256=sha(folder/('gui-'+mode)/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        # Symlink targets are archived as links by the evidence collector.
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='xauthority'}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()

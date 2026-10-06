"""Fixed native crash/restart reconciliation oracle using an independent socket client."""
from pathlib import Path
import copy,hashlib,json,os,queue,select,signal,socket,struct,subprocess,sys,threading,time,uuid,warnings
import jsonschema

exe,store_exe,repo,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:5])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(evidence).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('reconciliation-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
filesystem=subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip();assert filesystem=='ext4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'family':'RECONCILIATION','outcome':'running','filesystem':filesystem,'uid':os.geteuid(),'executable_sha256':sha(exe),
 'store_executable_sha256':sha(store_exe),'oracle_sha256':sha(Path(__file__)),'cases':[],
 'qualification':'Owned Linux IPC/ext4 process-crash experiment only. Full activation, installed ownership, worker supervision and other platforms remain open.'}
def save():(root/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
def validate(value,name):
    schema=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',DeprecationWarning)
        jsonschema.Draft202012Validator(schema,resolver=jsonschema.RefResolver.from_schema(schema,store=schemas)).validate(value)
settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text())
settings['revision']=scene['revision']='40';scene['widgets'][1]['layout']={'base':{'kind':'fixed','x':10,'y':20,'width':240,'height':80}}
for name,value in [('settings',settings),('scene',scene)]:
    p=root/(name+'.json');p.write_text(json.dumps(value));p.chmod(0o600)
def command(revision=40,x=20,request='R',policy=7):
    candidate=copy.deepcopy(scene);candidate['revision']=str(revision);candidate['widgets'][1]['layout']['base']['x']=x
    value={'schema_version':'0.2.0','request_id':request,'expected_revision':str(revision),'policy_generation':str(policy),'intent':'commit',
      'operations':[{'op':'scene.replace','scene':candidate}]};validate(value,'command-v0.2');return value
def initialize(directory):
    directory.mkdir(mode=0o700);p=subprocess.run([str(store_exe),str(directory),'init',str(root/'settings.json'),str(root/'scene.json')],capture_output=True,text=True,timeout=5)
    assert p.returncode==0,p.stderr
def files(directory):return {p.relative_to(directory).as_posix():sha(p) for p in directory.rglob('*') if p.is_file()}
def inspect(directory,revision,x,fallback=False):
    p=subprocess.run([str(store_exe),str(directory),'read'],capture_output=True,text=True,timeout=5);assert p.returncode==0,p.stderr
    documents=json.loads(p.stdout);expected_settings=copy.deepcopy(settings);expected_scene=copy.deepcopy(scene)
    expected_settings['revision']=expected_scene['revision']=str(revision);expected_scene['widgets'][1]['layout']['base']['x']=x
    assert documents=={'settings':expected_settings,'scene':expected_scene,'recovered_previous':fallback}
    pointer=json.loads((directory/('previous.json' if fallback else 'current.json')).read_text());generation=directory/pointer['generation']
    assert generation.parent==directory and sha(generation/'manifest.json')==pointer['manifest']
    manifest=json.loads((generation/'manifest.json').read_text());assert sha(generation/'settings.json')==manifest['settings'] and sha(generation/'scene.json')==manifest['scene']
    assert json.loads((generation/'settings.json').read_text())==expected_settings and json.loads((generation/'scene.json').read_text())==expected_scene
    validate(expected_settings,'settings');validate(expected_scene,'scene-v0.2')
class Server:
    def __init__(self,directory,case,epoch='E1',phase='plain',permission='allow'):
        self.epoch=epoch;self.events=queue.Queue();self.log=[];self.socket=None
        runtime=Path.home()/'.cache/syspane/ipc-w24'/('recon-'+uuid.uuid4().hex[:10]);runtime.mkdir(mode=0o700,parents=True)
        self.endpoint=str(runtime/'s')
        self.process=subprocess.Popen([str(exe),self.endpoint,str(directory),phase,str(os.getpid()),epoch,permission],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def collect():
            for line in self.process.stdout:
                try:v=json.loads(line)
                except ValueError:v={'event':'unparsed','text':line.strip()}
                self.log.append(v);self.events.put(v)
        self.reader=threading.Thread(target=collect,daemon=True);self.reader.start();case['processes'].append(self)
        self.ready=self.event('ready');assert self.ready['access_controls_verified'] is True
        self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.settimeout(1);self.socket.connect(self.endpoint)
        assert struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==self.process.pid
        assert self.event('authenticated')['peer_pid']==os.getpid()
        docs=[{'document':name,'version':version} for name,version in [('command','0.2.0'),('command-result','0.1.0'),('reconciliation-request','0.1.0'),('reconciliation-result','0.1.0')]]
        self.send('hello',{'wire_major':0,'wire_minor':1,'role':'console','producer_epoch':'client','max_frame_bytes':1048576,'document_versions':docs,
         'required_features':['configuration.transactions','result.reconcile'],'optional_features':['result.get','cancel']})
        assert self.receive()['type']=='welcome'
    def event(self,name):
        end=time.monotonic()+5
        while time.monotonic()<end:
            try:v=self.events.get(timeout=.1)
            except queue.Empty:continue
            assert v.get('event')!='error',v
            if v.get('event')==name:return v
        raise AssertionError(('event timeout',name,self.log))
    def send(self,kind,body):
        value={'type':kind,'body':body}
        if kind!='hello':value.update(connection_id='C',producer_epoch=self.epoch)
        b=json.dumps(value,separators=(',',':')).encode();self.socket.sendall(struct.pack('!I',len(b))+b)
    def receive(self):
        def exact(n):
            b=b''
            while len(b)<n:
                piece=self.socket.recv(n-len(b));assert piece,'unexpected EOF';b+=piece
            return b
        length=struct.unpack('!I',exact(4))[0];assert 0<length<=1048576
        value=json.loads(exact(length));assert value['connection_id']=='C' and value['producer_epoch']==self.epoch
        if value['type']=='result':validate(value['body'],'command-result')
        return value
    def reconcile(self,original='E1',request='R'):
        query={'schema_version':'0.1.0','query_id':'Q','original_producer_epoch':original,'request_id':request};self.send('result.reconcile',query)
        reply=self.receive();assert reply['type']=='result.reconciled';validate(reply['body'],'reconciliation-result')
        body=reply['body'];assert {k:body[k] for k in query}==query
        assert body['result']['request_id']==request and body['result']['producer_epoch']==self.epoch
        return body['result']
    def control(self,line):self.process.stdin.write(line+'\n');self.process.stdin.flush()
    def crash(self,phase):
        assert self.event('held')['phase']==phase
        end=time.monotonic()+3;stopped=None
        while time.monotonic()<end:
            stopped=os.waitid(os.P_PID,self.process.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
            if stopped:break
            time.sleep(.01)
        assert stopped and stopped.si_code==os.CLD_STOPPED and stopped.si_status==signal.SIGSTOP
        assert not select.select([self.socket],[],[],0)[0],'acknowledgement preceded injected crash'
        self.process.kill();assert self.process.wait(timeout=3)==-signal.SIGKILL
        self.socket.close();self.socket=None
    def close(self):
        if self.process.poll() is None:
            if self.socket:self.socket.close();self.socket=None;self.event('disconnected')
            self.control('stop');assert self.process.wait(timeout=5)==0
    def dispose(self):
        if self.socket:self.socket.close();self.socket=None
        if self.process.poll() is None:self.process.kill();self.process.wait(timeout=3)
        self.reader.join(1);assert not self.reader.is_alive();self.process.stdin.close();self.process.stdout.close()
        return {'pid':self.process.pid,'exit':self.process.returncode,'events':self.log}
def recovered(reply,revision=41):
    assert reply['outcome']=='accepted' and reply['revision']==str(revision) and reply['stored'] is True and reply['durable'] is True and reply['visible'] is False
    assert reply['activation'][0]['state']=='pending'
def run(name):
    case={'case':name,'outcome':'fail','processes':[]};directory=root/name;initialize(directory)
    try:
        phase='crash-before' if name=='BEFORE-PUBLISH' else ('preparing' if name=='LIVE-LOOKUP' else 'crash-durable')
        old=Server(directory,case,phase=phase);old.send('command',command())
        if name=='LIVE-LOOKUP':
            assert old.event('held')['phase']=='preparing';assert len(list((Path('/proc')/str(old.process.pid)/'task').iterdir()))>=2
            reply=old.reconcile();assert reply['outcome']=='unknown' and reply['error']['code']=='request.pending' and reply['stored'] is None
            old.send('heartbeat',{'sequence':'1'});assert old.receive()['type']=='heartbeat';old.control('release');old.event('joined');recovered(old.receive()['body']);recovered(old.reconcile());old.close()
            inspect(directory,41,20);case.update(outcome='pass',worker_observed=True,revision=41)
        else:
            old.crash(phase);revision=40 if name=='BEFORE-PUBLISH' else 41;x=10 if revision==40 else 20;inspect(directory,revision,x)
            if name=='FALLBACK':(directory/'current.json').write_bytes(b'corrupt-selector');revision=40;x=10
            before=files(directory);new=Server(directory,case,epoch='E2',permission='deny' if name=='POLICY-RESTART' else 'allow')
            assert new.ready['recovered_previous']==(name=='FALLBACK');reply=new.reconcile()
            if name in ('BEFORE-PUBLISH','POLICY-RESTART','FALLBACK'):
                assert reply['outcome']=='unknown' and reply['stored'] is None
                assert reply['error']['code']==('policy.denied' if name=='POLICY-RESTART' else 'request.reconcile')
            else:recovered(reply)
            assert files(directory)==before,'reconciliation changed the store'
            if name=='RETENTION-SCOPE':
                assert new.reconcile('E2')['outcome']=='unknown'
                new.send('command',command(41,30,'R',8));new.event('joined');recovered(new.receive()['body'],42)
                recovered(new.reconcile('E1'),41);recovered(new.reconcile('E2'),42)
                new.send('command',command(42,40,'S',8));new.event('joined');recovered(new.receive()['body'],43)
                before=files(directory);missing=new.reconcile('E1');assert missing['outcome']=='unknown' and missing['stored'] is None
                recovered(new.reconcile('E2'),42);assert files(directory)==before;revision=43;x=40
            new.close();inspect(directory,revision,x,name=='FALLBACK')
            if name=='FALLBACK':assert (directory/'current.json').read_bytes()==b'corrupt-selector'
            case.update(outcome='pass',stopped_then_killed=True,revision=revision,result=reply)
    finally:
        case['processes']=[p.dispose() for p in case['processes']];record['cases'].append(case);save()
try:
    for name in ('AFTER-DURABLE','BEFORE-PUBLISH','POLICY-RESTART','FALLBACK','RETENTION-SCOPE','LIVE-LOOKUP'):run(name)
    record['outcome']='pass';save();print(json.dumps({'outcome':'pass','cases':len(record['cases']),'report':str(root/'result.json')}))
except Exception as e:record.update(outcome='fail',error=repr(e));save();raise

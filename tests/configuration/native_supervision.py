"""Independent native transaction supervision oracle; never assumes a cancellation proves process exit."""
from pathlib import Path
import copy,hashlib,json,os,queue,select,signal,socket,struct,subprocess,sys,threading,time,uuid,warnings
import jsonschema

exe,store_exe,repo,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:5])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(evidence).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('supervision-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
filesystem=subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip();assert filesystem=='ext4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'family':'TRANSACTION-SUPERVISION','outcome':'running','filesystem':filesystem,'uid':os.geteuid(),'executable_sha256':sha(exe),
 'store_executable_sha256':sha(store_exe),'oracle_sha256':sha(Path(__file__)),'cases':[],
 'qualification':'Owned Linux supervisor/controller IPC/ext4 experiment only. Installed ownership, resource closure, activation and non-Linux supervision remain open.'}
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
class Client:
    def __init__(self,ready):
        self.epoch=ready['epoch'];self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.settimeout(1);self.socket.connect(ready['endpoint'])
        assert struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==ready['pid']
        docs=[{'document':n,'version':v} for n,v in [('command','0.2.0'),('command-result','0.1.0'),('reconciliation-request','0.1.0'),('reconciliation-result','0.1.0')]]
        self.send('hello',{'wire_major':0,'wire_minor':1,'role':'console','producer_epoch':'client','max_frame_bytes':1048576,'document_versions':docs,'required_features':['configuration.transactions','result.reconcile'],'optional_features':['result.get','cancel']})
        assert self.receive()['type']=='welcome'
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
    def reconcile(self,original,request='R'):
        query={'schema_version':'0.1.0','query_id':'Q','original_producer_epoch':original,'request_id':request};self.send('result.reconcile',query)
        reply=self.receive();assert reply['type']=='result.reconciled';validate(reply['body'],'reconciliation-result')
        body=reply['body'];assert {k:body[k] for k in query}==query and body['result']['producer_epoch']==self.epoch and body['result']['request_id']==request
        return body['result']
    def close(self):self.socket.close()
class Supervisor:
    def __init__(self,directory,scenario):
        self.events=queue.Queue();self.log=[];self.children={};self.clients=[]
        runtime=Path.home()/'.cache/syspane/ipc-w24'/('sup-'+uuid.uuid4().hex[:8]);runtime.mkdir(mode=0o700)
        self.process=subprocess.Popen([str(exe),'supervisor',str(runtime),str(directory),scenario,str(os.getpid()),'allow'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        def collect():
            for line in self.process.stdout:
                try:value=json.loads(line)
                except ValueError:value={'event':'unparsed','text':line.strip()}
                value['oracle_received_ms']=round(time.monotonic()*1000);self.log.append(value);self.events.put(value)
        self.reader=threading.Thread(target=collect,daemon=True);self.reader.start()
    def event(self,name,timeout=8):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            try:value=self.events.get(timeout=.1)
            except queue.Empty:continue
            assert value.get('event')!='error',value
            if value.get('event')==name:return value
        raise AssertionError(('event timeout',name,self.log))
    def connect(self):
        ready=self.event('ready');pid=ready['pid'];fd=os.pidfd_open(pid);self.children[pid]=fd
        assert int((Path('/proc')/str(pid)/'stat').read_text().split(')')[1].split()[1])==self.process.pid
        client=Client(ready);self.clients.append(client);return ready,client
    def worker(self,pid):
        end=time.monotonic()+2
        while time.monotonic()<end:
            if len(list((Path('/proc')/str(pid)/'task').iterdir()))>=2:return
            time.sleep(.01)
        raise AssertionError('actual transaction worker absent')
    def exited(self,pid,timeout=2):assert select.select([self.children[pid]],[],[],timeout)[0],'native process exit not observed'
    def stop(self):
        for c in self.clients:c.close()
        self.clients=[]
        self.process.stdin.write('stop\n');self.process.stdin.flush();assert self.process.wait(timeout=4)==0
        for pid in self.children:self.exited(pid)
    def dispose(self):
        for c in self.clients:c.close()
        if self.process.poll() is None:self.process.kill();self.process.wait(timeout=3)
        for pid,fd in self.children.items():
            self.exited(pid,3);os.close(fd)
        self.reader.join(1);assert not self.reader.is_alive();self.process.stdin.close();self.process.stdout.close()
        return {'pid':self.process.pid,'exit':self.process.returncode,'events':self.log}
def accepted(value,revision):
    assert value['outcome']=='accepted' and value['revision']==str(revision) and value['stored'] is True and value['durable'] is True and value['visible'] is False
    assert value['activation'][0]['state']=='pending'
def run(name):
    case={'case':name,'outcome':'fail'};directory=root/name;initialize(directory);supervisor=None
    try:
        scenario='normal' if name=='NORMAL' else ('durable' if name=='DURABLE-HANG' else ('repeat' if name=='CIRCUIT' else 'prepare'))
        supervisor=Supervisor(directory,scenario);ready,client=supervisor.connect();original=ready['epoch'];pid=ready['pid'];revision=40;x=10
        client.send('command',command());supervisor.event('armed')
        if name=='NORMAL':
            accepted(client.receive()['body'],41);supervisor.event('finished');client.send('command',command(41,30,'S'));supervisor.event('armed');accepted(client.receive()['body'],42);supervisor.event('finished')
            accepted(client.reconcile(original),41);revision=42;x=30;supervisor.stop()
        else:
            supervisor.worker(pid);client.send('heartbeat',{'sequence':'1'});assert client.receive()['type']=='heartbeat'
            client.send('result.get',{'request_id':'R'});pending=client.receive()['body'];assert pending['outcome']=='unknown' and pending['error']['code']=='request.pending'
            if name in ('GUARDIAN-DEATH','GUARDIAN-FREEZE'):
                if name=='GUARDIAN-DEATH':supervisor.process.kill();assert supervisor.process.wait(timeout=3)==-signal.SIGKILL
                else:
                    supervisor.process.send_signal(signal.SIGSTOP);end=time.monotonic()+2
                    while time.monotonic()<end:
                        stopped=os.waitid(os.P_PID,supervisor.process.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                        if stopped:break
                        time.sleep(.01)
                    assert stopped and stopped.si_code==os.CLD_STOPPED
                supervisor.exited(pid,5)
                if supervisor.process.poll() is None:supervisor.process.kill();supervisor.process.wait(timeout=3)
                case['independent_child_exit']=True
            else:
                if name=='CONTROLLER-FREEZE':signal.pidfd_send_signal(supervisor.children[pid],signal.SIGSTOP)
                attempts=4 if name=='CIRCUIT' else 1
                for attempt in range(attempts):
                    fault=supervisor.event('fault');assert fault['pid']==pid and fault['quarantined'] is True
                    assert fault['reason']==('supervisor.health_expired' if name=='CONTROLLER-FREEZE' else 'transaction.deadline'),fault
                    if name!='CONTROLLER-FREEZE':assert fault['heartbeats']>=2
                    reaped=supervisor.event('reaped');assert reaped['pid']==pid and reaped['signaled'] is True and reaped['code']==signal.SIGKILL;supervisor.exited(pid)
                    if name=='CIRCUIT' and attempt==3:
                        assert supervisor.event('circuit_open')['generations']==4;assert supervisor.process.wait(timeout=3)==0;break
                    next_ready,next_client=supervisor.connect();assert next_ready['epoch']!=client.epoch and next_ready['pid']!=pid
                    assert next(e for e in supervisor.log if e['event']=='launched' and e['pid']==next_ready['pid'])['oracle_received_ms']>=reaped['oracle_received_ms']
                    if name=='CIRCUIT':
                        client=next_client;pid=next_ready['pid'];client.send('command',command());supervisor.event('armed');supervisor.worker(pid)
                    else:
                        before=files(directory);reply=next_client.reconcile(original)
                        if name=='DURABLE-HANG':accepted(reply,41);revision=41;x=20
                        else:assert reply['outcome']=='unknown' and reply['stored'] is None and reply['error']['code']=='request.reconcile'
                        assert files(directory)==before;supervisor.stop()
        inspect(directory,revision,x);case.update(outcome='pass',revision=revision)
    finally:
        if supervisor:case['supervisor']=supervisor.dispose()
        record['cases'].append(case);save()
try:
    for name in ('NORMAL','PREPARE-HANG','DURABLE-HANG','CONTROLLER-FREEZE','GUARDIAN-DEATH','GUARDIAN-FREEZE','CIRCUIT'):run(name)
    record['outcome']='pass';save();print(json.dumps({'outcome':'pass','cases':len(record['cases']),'report':str(root/'result.json')}))
except Exception as e:record.update(outcome='fail',error=repr(e));save();raise

"""Independent native transaction supervision oracle; never assumes a cancellation proves process exit."""
from pathlib import Path
import copy,hashlib,json,os,queue,select,signal,socket,struct,subprocess,sys,threading,time,uuid,warnings
import jsonschema

exe,store_exe,repo,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:5])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(evidence).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('content-commands-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
filesystem=subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip();assert filesystem=='ext4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'family':'CONTENT-COMMANDS','outcome':'running','filesystem':filesystem,'uid':os.geteuid(),'executable_sha256':sha(exe),
 'store_executable_sha256':sha(store_exe),'oracle_sha256':sha(Path(__file__)),'cases':[],
 'qualification':'Owned Linux supervisor/controller IPC/ext4 experiment only. Installed ownership, media decoding, activation and non-Linux supervision remain open.'}
def save():(root/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
def validate(value,name):
    schema=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',DeprecationWarning)
        jsonschema.Draft202012Validator(schema,resolver=jsonschema.RefResolver.from_schema(schema,store=schemas)).validate(value)

encoded=lambda v:json.dumps(v,separators=(',',':')).encode()
sha_path=sha
sha=lambda b:hashlib.sha256(b).hexdigest()
valid=validate
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def store_run(directory,*args):
 p=subprocess.run([str(store_exe),str(directory),*map(str,args)],capture_output=True,text=True,timeout=8)
 assert p.returncode==0,(args,p.returncode,p.stderr)
 return json.loads(p.stdout)
def files(directory):return {p.relative_to(directory).as_posix():sha_path(p) for p in directory.rglob('*') if p.is_file()}
def fixture(name):
 d=root/name;d.mkdir(mode=0o700);store=d/'store';store.mkdir(mode=0o700);imports=d/'imports';imports.mkdir(mode=0o700)
 settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text())
 settings['revision']=scene['revision']='40';scene['widgets'][1]['layout']={'base':{'kind':'fixed','x':10,'y':20,'width':240,'height':80}}
 write(d/'settings.json',encoded(settings));write(d/'scene.json',encoded(scene));store_run(store,'init',d/'settings.json',d/'scene.json')
 paths=[];pins=[];docs=[];files={};theme=json.loads((repo/'spec/fixtures/valid/theme.json').read_text());theme['theme_id']='theme:custom'
 def package(kind,doc,deps,extras=None):
  p=imports/kind;p.mkdir(mode=0o700);assets={kind+'.json':encoded(doc)+b'\n',**(extras or {})};rows=[]
  for path,raw in assets.items():
   target=p/path
   if target.parent!=p:target.parent.mkdir(mode=0o700)
   write(target,raw);rows.append({'path':path,'media_type':'application/json' if path.endswith('.json') else 'image/png','sha256':sha(raw),'bytes':len(raw)})
   files['a-'+sha(raw)+'.bin']=raw
  m={'schema_version':'0.1.0','package_id':'package:'+kind,'version':'0.1.0','kind':kind,'license':'MIT','dependencies':deps,'assets':rows,
    'total_unpacked_bytes':sum(map(len,assets.values())),'required_capabilities':[],'optional_capabilities':[]}
  valid(m,'content-package');valid(doc,'scene-v0.2' if kind=='scene' else kind);mb=encoded(m)+b'\n';write(p/'manifest.json',mb);files['m-'+sha(mb)+'.json']=mb
  pins.append({'id':m['package_id'],'version':'0.1.0','sha256':sha(mb)});docs.append({'id':doc[kind+'_id'],'version':'0.1.0','sha256':sha(assets[kind+'.json'])});paths.append(p)
 package('theme',theme,[],{'images/pixel.png':b'opaque media bytes\x00unchanged'})
 authored=copy.deepcopy(scene);authored['revision']='3';authored['widgets'][1]['layout']['base']['x']=20;package('scene',authored,[])
 preset={'schema_version':'0.1.0','preset_id':'preset:custom','version':'0.1.0','parent':None,'scene':docs[1],'theme':docs[0],
  'settings':[{'path':'display.theme_id','value':'theme:custom'}],'required_capabilities':['scene.selector'],'optional_capabilities':[]}
 package('preset',preset,copy.deepcopy(pins));candidate=copy.deepcopy(authored);candidate['revision']='40';candidate['theme_id']='theme:custom'
 selection={'package':pins[2],'preset':docs[2]}
 q={'schema_version':'0.3.0','request_id':'R','expected_revision':'40','policy_generation':'7','intent':'commit','content':selection,
  'operations':[{'op':'scene.replace','scene':candidate},{'op':'settings.set','path':'display.theme_id','value':'theme:custom'}]}
 valid(q,'command-v0.3');write(d/'command.json',encoded(q))
 write(imports/'catalog.json',encoded({'schema_version':'0.1.0','packages':['theme','scene','preset']}))
 return {'directory':d,'store':store,'paths':paths,'files':files,'pins':pins,'theme':theme,'theme_pin':docs[0],'selection':selection,'command':q,'settings':settings,'scene':scene,'candidate':candidate}
def inspect(f,revision,x=20,fallback=False):
 value=store_run(f['store'],'read');settings=copy.deepcopy(f['settings']);scene=copy.deepcopy(f['candidate'] if revision>40 else f['scene']);settings['revision']=scene['revision']=str(revision)
 scene['widgets'][1]['layout']['base']['x']=x
 expected={'settings':settings,'scene':scene,'recovered_previous':fallback}
 if revision>40:
  settings['display']['theme_id']='theme:custom';expected['resources']={'selection':f['selection'],'theme':f['theme'],'theme_pin':f['theme_pin'],'packages':sorted(p['sha256'] for p in f['pins'])}
 assert value==expected,(value,expected)
 pointer=json.loads((f['store']/('previous.json' if fallback else 'current.json')).read_bytes());generation=f['store']/pointer['generation'];manifest=json.loads((generation/'manifest.json').read_bytes())
 assert sha((generation/'manifest.json').read_bytes())==pointer['manifest'] and sha((generation/'settings.json').read_bytes())==manifest['settings'] and sha((generation/'scene.json').read_bytes())==manifest['scene']
 if revision>40:
  assert manifest['version']=='0.2.0';index=json.loads((generation/'resources.json').read_bytes());assert sha((generation/'resources.json').read_bytes())==manifest['resources']
  assert index=={'version':'0.1.0','selection':f['selection'],'theme':f['theme_pin'],'packages':expected['resources']['packages']}
  assert {p.name:p.read_bytes() for p in (generation/'resources').iterdir()}==f['files']
  assert json.loads(manifest['identity']['body'])['content']==f['selection']
 return generation
class Client:
    def __init__(self,ready,content=True):
        self.epoch=ready['epoch'];self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.settimeout(1);self.socket.connect(ready['endpoint'])
        assert struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==ready['pid']
        docs=[{'document':n,'version':v} for n,v in [('command','0.3.0'),('command-result','0.1.0'),('reconciliation-request','0.1.0'),('reconciliation-result','0.1.0')]]
        self.send('hello',{'wire_major':0,'wire_minor':1,'role':'console','producer_epoch':'client','max_frame_bytes':1048576,'document_versions':docs,'required_features':['configuration.transactions','result.reconcile'],'optional_features':['result.get','cancel']+(['configuration.content'] if content else [])})
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
    def __init__(self,directory,scenario,catalog,permission="allow"):
        self.events=queue.Queue();self.log=[];self.children={};self.clients=[]
        runtime=Path.home()/'.cache/syspane/ipc-w24'/('sup-'+uuid.uuid4().hex[:8]);runtime.mkdir(mode=0o700)
        self.process=subprocess.Popen([str(exe),'content',str(catalog),'supervisor',str(runtime),str(directory),scenario,str(os.getpid()),permission],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
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
    def connect(self,content=True):
        ready=self.event('ready');pid=ready['pid'];fd=os.pidfd_open(pid);self.children[pid]=fd
        assert int((Path('/proc')/str(pid)/'stat').read_text().split(')')[1].split()[1])==self.process.pid
        client=Client(ready,content);self.clients.append(client);return ready,client
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
def command(f,revision=40,x=20,request='R'):
 q=copy.deepcopy(f['command']);q['request_id']=request;q['expected_revision']=q['operations'][0]['scene']['revision']=str(revision)
 q['operations'][0]['scene']['widgets'][1]['layout']['base']['x']=x;validate(q,'command-v0.3');return q
def commit(supervisor,client,q,revision):
 client.send('command',q);supervisor.event('armed');accepted(client.receive()['body'],revision);supervisor.event('finished')
def gone(f):
 (f['directory']/'imports').rename(f['directory']/'preserved-imports')
def selected(f):
 pointer=json.loads((f['store']/'current.json').read_bytes())
 return json.loads((f['store']/pointer['generation']/'scene.json').read_bytes())['revision']
def replacement(supervisor,client,ready,reason):
 fault=supervisor.event('fault');assert fault['pid']==ready['pid'] and fault['quarantined'] is True,fault
 # An external SIGKILL may be observed first by the pipe or by the child poll.
 assert fault['reason'] in ({'supervisor.child_exit','health.eof'} if reason=='supervisor.child_exit' else {reason}),fault
 if reason=='transaction.deadline':assert fault['heartbeats']>=2
 reaped=supervisor.event('reaped');assert reaped['pid']==ready['pid'] and reaped['signaled'] is True and reaped['code']==signal.SIGKILL;supervisor.exited(ready['pid'])
 next_ready,next_client=supervisor.connect();assert next_ready['epoch']!=client.epoch and next_ready['pid']!=ready['pid']
 assert next(e for e in supervisor.log if e['event']=='launched' and e['pid']==next_ready['pid'])['oracle_received_ms']>=reaped['oracle_received_ms']
 return next_ready,next_client
def run(name):
 case={'case':name,'outcome':'fail'};f=fixture(name);supervisor=None;logs=[]
 try:
  scenario={'PREPARE-HANG':'prepare','CANCEL-HANG':'prepare','RESOURCE-HANG':'resource','DURABLE-HANG':'durable'}.get(name,'normal')
  catalog=f['directory']/'imports';supervisor=Supervisor(f['store'],scenario,catalog);ready,client=supervisor.connect(name!='UNNEGOTIATED');original=ready['epoch']
  revision=40;x=10
  if name=='UNNEGOTIATED':
   before=files(f['store']);client.send('command',command(f));answer=client.receive()['body'];assert answer['error']['code']=='feature.unsupported'
   assert files(f['store'])==before
   client.close();time.sleep(.05);client=Client(ready);supervisor.clients.append(client)
   commit(supervisor,client,command(f),41);revision=41;x=20
  elif name=='CATALOG-REJECTION':
   before=files(f['store'])
   bad=[{'schema_version':'0.1.0','packages':['../outside']},{'schema_version':'0.1.0','packages':['theme'],'authority':'grant'},
        {'schema_version':'0.1.0','packages':['theme','Theme']}]
   for n,v in enumerate(bad):
    write(catalog/'catalog.json',encoded(v));client.send('command',command(f,request='bad'+str(n)));supervisor.event('armed')
    assert client.receive()['body']['outcome']=='invalid';supervisor.event('finished');assert files(f['store'])==before
   write(catalog/'catalog.json',encoded({'schema_version':'0.1.0','packages':['theme','scene','preset']}))
   commit(supervisor,client,command(f),41);write(catalog/'catalog.json',b'not json')
   commit(supervisor,client,command(f,41,30,'S'),42);revision=42;x=30
  elif name in ('NORMAL-RETAINED','POLICY-DENY','RETAINED-ONLY'):
   commit(supervisor,client,command(f),41);gone(f)
   if name=='NORMAL-RETAINED':
    commit(supervisor,client,command(f,41,30,'S'),42)
    signal.pidfd_send_signal(supervisor.children[ready['pid']],signal.SIGKILL)
    ready,client=replacement(supervisor,client,ready,'supervisor.child_exit')
    before=files(f['store']);accepted(client.reconcile(original),41);accepted(client.reconcile(original,'S'),42);assert files(f['store'])==before
    commit(supervisor,client,command(f,42,40,'T'),43);revision=43;x=40
   else:
    supervisor.stop();logs.append(supervisor.dispose());supervisor=None
    supervisor=Supervisor(f['store'],'normal','-', 'deny' if name=='POLICY-DENY' else 'allow');ready,client=supervisor.connect()
    if name=='POLICY-DENY':
     before=files(f['store']);hidden=client.reconcile(original)
     assert hidden['outcome']=='unknown' and hidden['error']['code']=='policy.denied' and all(hidden[k] is None for k in ('stored','durable','visible'))
     client.send('command',command(f,41,30,'S'));assert client.receive()['body']['outcome']=='denied';assert files(f['store'])==before;revision=41;x=20
    else:commit(supervisor,client,command(f,41,30,'S'),42);revision=42;x=30
  else:
   client.send('command',command(f));supervisor.event('armed');supervisor.worker(ready['pid'])
   # Observe the actual persistence boundary before acting on a process fault.
   if name in ('RESOURCE-HANG','DURABLE-HANG'):
    end=time.monotonic()+2;reached=False
    while time.monotonic()<end:
     reached=selected(f)=='41' if name=='DURABLE-HANG' else any(f['store'].glob('*/resources/m-*.json'))
     if reached:break
     time.sleep(.01)
    assert reached
    if name=='DURABLE-HANG':gone(f)
    else:assert selected(f)=='40'
   client.send('heartbeat',{'sequence':'1'});assert client.receive()['type']=='heartbeat'
   client.send('cancel' if name=='CANCEL-HANG' else 'result.get',{'request_id':'R'});pending=client.receive()['body']
   assert pending['outcome']=='unknown' and pending['error']['code']=='request.pending'
   assert not select.select([supervisor.children[ready['pid']]],[],[],0)[0]
   ready,client=replacement(supervisor,client,ready,'transaction.deadline')
   before=files(f['store']);reply=client.reconcile(original)
   if name=='DURABLE-HANG':accepted(reply,41);revision=41
   else:assert reply['outcome']=='unknown' and reply['stored'] is None and reply['error']['code']=='request.reconcile'
   assert files(f['store'])==before
   commit(supervisor,client,command(f,revision,30,'S'),revision+1);revision+=1;x=30
  supervisor.stop();inspect(f,revision,x);case.update(outcome='pass',revision=revision)
 finally:
  if supervisor:logs.append(supervisor.dispose())
  case['supervisors']=logs;record['cases'].append(case);save()
try:
 for name in ('NORMAL-RETAINED','PREPARE-HANG','CANCEL-HANG','RESOURCE-HANG','DURABLE-HANG','POLICY-DENY','RETAINED-ONLY','UNNEGOTIATED','CATALOG-REJECTION'):run(name)
 record['outcome']='pass';save();print(json.dumps({'outcome':'pass','cases':len(record['cases']),'report':str(root/'result.json')}))
except Exception as e:record.update(outcome='fail',error=repr(e));save();raise

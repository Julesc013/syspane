"""Independent socket client and stored-document oracle for finite command IPC."""
from pathlib import Path
import hashlib,json,os,queue,socket,struct,subprocess,sys,threading,time,uuid,warnings
import jsonschema

exe,store_exe,repo,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:5])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
root=evidence/('commands-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
assert str(root).startswith('/home/ir4runner/.cache/syspane/')
filesystem=subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip()
assert filesystem=='ext4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'family':'COMMAND-IPC','outcome':'running','filesystem':filesystem,'uid':os.geteuid(),
 'executable_sha256':sha(exe),'store_executable_sha256':sha(store_exe),'oracle_sha256':sha(Path(__file__)),
 'cases':[],'qualification':'Finite authenticated Linux ext4 experiment; installed owner, hard worker supervision, original-epoch wire reconciliation and visibility remain open.'}
def save():
    (root/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
def validate(value,name):
    schema=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',DeprecationWarning)
        jsonschema.Draft202012Validator(schema,resolver=jsonschema.RefResolver.from_schema(schema,store=schemas)).validate(value)
settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text())
settings['revision']=scene['revision']='40'
for name,value in [('settings',settings),('scene',scene)]:
    p=root/(name+'.json');p.write_text(json.dumps(value));p.chmod(0o600)
command={'schema_version':'0.2.0','request_id':'R','expected_revision':'40','policy_generation':'7','intent':'commit',
 'operations':[{'op':'settings.set','path':'sampling.resources_ms','value':1500}]}
hello={'type':'hello','body':{'wire_major':0,'wire_minor':1,'role':'console','producer_epoch':'client','max_frame_bytes':1048576,
 'document_versions':[{'document':'command','version':'0.2.0'},{'document':'command-result','version':'0.1.0'}],
 'required_features':['configuration.transactions'],'optional_features':['settings.preview','result.get','cancel']}}
def send(s,kind,body):
    v=hello if kind=='hello' else {'type':kind,'body':body,'connection_id':'C','producer_epoch':'E1'}
    b=json.dumps(v,separators=(',',':')).encode();s.sendall(struct.pack('!I',len(b))+b)
def receive(s):
    def exact(n):
        b=b''
        while len(b)<n:
            part=s.recv(n-len(b));assert part,'unexpected EOF';b+=part
        return b
    n=struct.unpack('!I',exact(4))[0];assert 0<n<=1048576
    v=json.loads(exact(n))
    if v['type']=='result':validate(v['body'],'command-result')
    return v
def run_case(name,phase='preparing',action='none',reconnect=False):
    case={'case':name,'outcome':'fail','events':[]};record['cases'].append(case);save()
    directory=root/name;directory.mkdir(mode=0o700)
    init=subprocess.run([str(store_exe),str(directory),'init',str(root/'settings.json'),str(root/'scene.json')],capture_output=True,text=True,timeout=5)
    assert init.returncode==0,init.stderr
    runtime=Path.home()/'.cache/syspane/ipc-w24'/('command-'+uuid.uuid4().hex[:10]);runtime.mkdir(mode=0o700,parents=True)
    endpoint=str(runtime/'s');events=queue.Queue()
    proc=subprocess.Popen([str(exe),endpoint,str(directory),phase,str(os.getpid())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    def collect():
        for line in proc.stdout:
            try:v=json.loads(line)
            except ValueError:v={'event':'unparsed','text':line.strip()}
            case['events'].append(v);events.put(v)
    reader=threading.Thread(target=collect,daemon=True);reader.start();s=None
    def event(name):
        end=time.monotonic()+5
        while time.monotonic()<end:
            try:v=events.get(timeout=.1)
            except queue.Empty:continue
            assert v.get('event')!='error',v
            if v.get('event')==name:return v
        raise AssertionError(('event timeout',name,case['events']))
    def control(value):proc.stdin.write(value+'\n');proc.stdin.flush()
    def connect():
        peer=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);peer.settimeout(1);peer.connect(endpoint)
        assert struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==proc.pid
        assert event('authenticated')['peer_pid']==os.getpid();send(peer,'hello',None);assert receive(peer)['type']=='welcome';return peer
    try:
        assert event('ready')['access_controls_verified'] is True;s=connect();send(s,'command',command)
        assert event('held')['phase']==phase
        tasks=list((Path('/proc')/str(proc.pid)/'task').iterdir());assert len(tasks)>=2
        send(s,'heartbeat',{'sequence':'1'});assert receive(s)=={'type':'heartbeat','body':{'sequence':'1'},'connection_id':'C','producer_epoch':'E1'}
        send(s,'result.get',{'request_id':'R'});pending=receive(s)['body'];assert pending['outcome']=='unknown' and pending['stored'] is None and pending['error']['code']=='request.pending'
        assert len(list((Path('/proc')/str(proc.pid)/'task').iterdir()))>=2
        if action=='cancel':
            send(s,'cancel',{'request_id':'R'});pending=receive(s)['body'];assert pending['outcome']=='unknown' and pending['durable'] is None
        elif action=='revoke':
            control('revoke');event('revoked');assert receive(s)['type']=='gap'
        if reconnect:s.close();s=None;event('disconnected')
        control('release');joined=event('joined');assert len(list((Path('/proc')/str(proc.pid)/'task').iterdir()))==1
        expected_revision=40 if phase=='preparing' and action in ('cancel','revoke') else 41
        assert joined['revision']==expected_revision
        if reconnect:s=connect()
        if reconnect or action=='revoke':send(s,'result.get',{'request_id':'R'})
        answer=receive(s)['body'];expected_outcome='unknown' if action=='revoke' else ('cancelled' if expected_revision==40 else 'accepted')
        assert answer['outcome']==expected_outcome,answer
        if action=='revoke':assert answer['error']['code']=='policy.denied' and answer['stored'] is None and answer['durable'] is None
        if expected_outcome=='accepted':
            assert answer['revision']=='41' and answer['stored'] is True and answer['durable'] is True and answer['visible'] is False and answer['activation'][0]['state']=='pending'
            send(s,'command',command);assert receive(s)['body']==answer
        s.close();s=None;event('disconnected');control('stop');assert proc.wait(timeout=5)==0;reader.join(1);assert not reader.is_alive()
        inspected=subprocess.run([str(store_exe),str(directory),'read'],capture_output=True,text=True,timeout=5);assert inspected.returncode==0,inspected.stderr
        documents=json.loads(inspected.stdout);expected_settings=json.loads(json.dumps(settings));expected_scene=json.loads(json.dumps(scene))
        expected_settings['revision']=expected_scene['revision']=str(expected_revision)
        if expected_revision==41:expected_settings['sampling']['resources_ms']=1500
        assert documents['settings']==expected_settings and documents['scene']==expected_scene
        validate(documents['settings'],'settings');validate(documents['scene'],'scene-v0.2')
        case.update(outcome='pass',revision=expected_revision,result=answer,worker_observed=True,worker_join_observed=True,native_exit=proc.returncode)
    finally:
        if s:s.close()
        if proc.poll() is None:proc.kill();proc.wait(timeout=3)
        reader.join(1);proc.stdin.close();proc.stdout.close();case['native_exit']=proc.returncode;save()
try:
    run_case('COMMIT');run_case('CANCEL-PREPARING',action='cancel');run_case('CANCEL-PERMITTED',phase='permitted',action='cancel')
    run_case('POLICY-PREPARING',action='revoke');run_case('POLICY-PERMITTED',phase='permitted',action='revoke')
    run_case('LOST-REPLY',reconnect=True)
    record['outcome']='pass';save();print(json.dumps({'outcome':'pass','cases':len(record['cases']),'report':str(root/'result.json')}))
except Exception as e:
    record.update(outcome='fail',error=repr(e));save();raise

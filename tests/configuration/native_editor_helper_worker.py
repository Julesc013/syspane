"""Observe bounded GUI handles while a distinct native worker is held or pumped."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import ctypes, hashlib, json, os, select, signal, stat, struct, subprocess, sys, time, traceback, uuid, zipfile, zlib
ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'tests/configuration/editor-helper-worker-cases.json').read_bytes())
PIXELS={x['name']:x for x in json.loads((ROOT/CASES['image_expectations']).read_bytes())}
RECORDS={k:v.encode() for k,v in json.loads((ROOT/CASES['recovery_records']).read_bytes())['records'].items()}
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
sha=lambda b:hashlib.sha256(b).hexdigest()
LIBC=ctypes.CDLL(None,use_errno=True);LIBC.ptrace.restype=ctypes.c_long;LIBC.ptrace.argtypes=[ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p,ctypes.c_void_p]
def trace(request,pid,data=0):
 if LIBC.ptrace(request,pid,None,data)==-1:raise OSError(ctypes.get_errno(),'ptrace '+str(request))
def write(p,b,mode=0o600):p.write_bytes(b);p.chmod(mode)
def pixels(value,expected):assert value==dict(width=expected['size'][0],height=expected['size'][1],rgba=expected['rgba']),('pixel mismatch',value,expected)
def file_bytes(path,expected):assert (path.read_bytes() if path.exists() else None)==expected,'recovery file mismatch'

def main(extension=None,definitions=None):
 global CASES
 if definitions is not None:
  CASES=json.loads(definitions.read_bytes())
  if 'cases' not in CASES:CASES['cases']=CASES['native']
 probe,config,image_worker,recovery_worker,record,evidence=[Path(x).resolve() for x in sys.argv[1:]]
 assert os.geteuid() and evidence.parent==probe.parent and json.loads((probe.parent/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
 prefix='rp-' if CASES['family']=='RECOVERY-PREPARATION' else 'ra-' if extension else 'ew-'
 folder=evidence/(prefix+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700,parents=True)
 assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
 names=['syspane-configuration-host','syspane-image-worker','syspane-recovery-worker'];helper_bytes=[p.read_bytes() for p in (config,image_worker,recovery_worker)]
 entries={'bin/syspane':probe.read_bytes(),'share/syspane/helpers.json':record.read_bytes(),**{'libexec/syspane/'+n:b for n,b in zip(names,helper_bytes)}}
 archive=folder/'editor-helper-worker-development.zip'
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(entries.items()):
   i=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));i.create_system=3;i.external_attr=(0o100644 if n.endswith('.json') else 0o100755)<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b)
 image=folder/'image';image.mkdir(mode=0o755)
 with zipfile.ZipFile(archive) as z:
  assert len(z.namelist())==5 and set(z.namelist())==set(entries)
  for n,b in entries.items():
   assert z.read(n)==b;p=image/n;p.parent.mkdir(mode=0o755,parents=True,exist_ok=True);write(p,b,z.getinfo(n).external_attr>>16&0o777)
 relocated=folder/'relocated image';image.rename(relocated);image=relocated;cwd=folder/'cwd';cwd.mkdir(mode=0o700)
 report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),uid=os.geteuid(),kernel=list(os.uname()),
  artifacts={p.name:sha(p.read_bytes()) for p in (probe,config,image_worker,recovery_worker,record)},package_sha256=sha(archive.read_bytes()),
  oracle_sha256=sha(Path(__file__).read_bytes()),fixture_sha256=sha((definitions or ROOT/'tests/configuration/editor-helper-worker-cases.json').read_bytes()),cases=[],runs=[],mutations=[])
 start=time.monotonic();deadline=start+CASES['family_timeout_seconds'];runs=[]
 def save():write(folder/'result.json',encoded(report))
 def left():
  value=deadline-time.monotonic();assert value>0,'case deadline';return min(value,5)
 @contextmanager
 def case(name):
  nonlocal deadline
  begin=time.monotonic();deadline=min(start+CASES['family_timeout_seconds'],begin+CASES['case_timeout_seconds']);signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-begin))
  try:
   yield
   assert time.monotonic()<deadline;report['cases'].append(dict(case=name,outcome='pass',seconds=time.monotonic()-begin));save()
  finally:signal.setitimer(signal.ITIMER_REAL,0)
 def record_root(name,data=RECORDS['old']):
  path=folder/name;path.mkdir(mode=0o700)
  if data is not None:write(path/'draft.json',data)
  return path
 inputs={}
 for name,raw in {**RECORDS,'middle':RECORDS['old']+b'\n','empty':b'','oversized':b'x'*8388609}.items():
  inputs[name]=folder/(name+'.input');write(inputs[name],raw)
 class Run:
  def __init__(self,hold=(),admission=None):
   self.hold=set(hold);self.pending=b'';self.images=set();self.recovery=False;self.surface=False;self.session=False;self.preparation=False;self.closed=False
   env=dict(os.environ,PATH='/nonexistent');env.pop('LD_PRELOAD',None);env.pop('LD_LIBRARY_PATH',None)
   self.proc=subprocess.Popen(['irrelevant-name',str(ROOT),*([str(admission)] if admission else [])],executable=str(image/'bin/syspane'),cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
   self.pidfd=os.pidfd_open(self.proc.pid);self.traced=set();self.children={};self.observed={};self.parent_threads=set();self.held=set();self.cleaning=False
   self.row=dict(pid=self.proc.pid,events=[],children=[]);report['runs'].append(self.row);runs.append(self)
   initial=self.receive();assert initial['event']=='ready',initial;self.row['initial']=initial
   assert initial['before_attach']=='helpers.unavailable' and initial['status']['attached']
   self.parent_threads={self.proc.pid,initial['worker']};assert len(self.parent_threads)==2
   for pid in self.parent_threads:trace(0x4206,pid,2|4|16);self.traced.add(pid)
  def tracing(self):
   for pid in list(self.traced):
    found,status=os.waitpid(pid,os.WNOHANG|0x40000000)
    if not found:continue
    if not os.WIFSTOPPED(status):
     self.traced.remove(pid)
     if pid==self.proc.pid:self.proc.returncode=os.waitstatus_to_exitcode(status)
     elif pid in self.observed:self.observed[pid]['exited']=True
     else:assert pid in self.parent_threads or self.cleaning,('helper exited before exec',pid,status)
     self.held.discard(pid)
     continue
    event=status>>16
    if event in (1,2):
     child=ctypes.c_ulong();trace(0x4201,pid,ctypes.addressof(child));self.traced.add(child.value);self.children[child.value]=os.pidfd_open(child.value)
    elif event==4:
     assert pid not in self.parent_threads;path=Path('/proc',str(pid),'exe');link=os.readlink(path);digest=sha(path.read_bytes())
     role=next((i for i,b in enumerate(helper_bytes) if sha(b)==digest),None);assert role is not None and link.startswith('/memfd:'+names[role])
     assert '\nPPid:\t'+str(self.proc.pid)+'\n' in Path('/proc',str(pid),'status').read_text()
     row=dict(pid=pid,role=role,executable=link,sha256=digest,held=role in self.hold);self.observed[pid]=row;self.row['children'].append(row)
     if role in self.hold:
      self.held.add(pid);assert '\nState:\tt (tracing stop)\n' in Path('/proc',str(pid),'status').read_text()
      row['hold_observation']='kernel exec stop before worker instructions'
     else:trace(17,pid);self.traced.remove(pid)
     save();continue
    trace(7,pid,0 if event or os.WSTOPSIG(status)==signal.SIGTRAP else os.WSTOPSIG(status))
  def receive(self):
   while b'\n' not in self.pending:
    self.tracing()
    if not select.select([self.proc.stdout],[],[],min(.005,left()))[0]:continue
    raw=os.read(self.proc.stdout.fileno(),65536);assert raw,('probe EOF',self.proc.returncode);self.pending+=raw;assert len(self.pending)<=65536
   raw,self.pending=self.pending.split(b'\n',1);return json.loads(raw)
  def call(self,op,**args):
   request=dict(op=op,**args);raw=encoded(request)+b'\n';assert self.proc.stdin.write(raw)==len(raw);self.proc.stdin.flush();v=self.receive()
   self.row['events'].append(dict(request=request,response=v));save();assert set(v)=={'reply','elapsed_us','task_calls'},v
   for call in v['task_calls']:assert call['elapsed_us']<CASES['gui_operation_limit_ms']*1000,(op,'task interface blocked',call)
   # The fixed bound covers the GUI-owned task interface. Consumer timings also
   # include existing document validation/rasterization; retain these separately
   # instead of presenting them as helper latency or qualifying installed UI.
   if op not in ('pump','quit','draft','draft-edit','draft-discard') and not op.startswith(('surface','session')):assert v['elapsed_us']<CASES['gui_operation_limit_ms']*1000,(op,'GUI blocked',v)
   out=v['reply']
   if op=='image' and 'id' in out:self.images.add(out['id'])
   if op=='image-drop' and out.get('dropped'):self.images.remove(args['id'])
   if op=='recovery' and 'state' in out:self.recovery=True
   if op=='recovery-drop':self.recovery=False
   if op=='surface' and out.get('created'):self.surface=True
   if op=='session' and out.get('created'):self.session=True
   if op=='surface-close' and out.get('stopped'):self.surface=False
   if op=='session-close' and out.get('stopped'):self.session=False
   if op=='prepare' and out.get('created'):self.preparation=True
   if op=='preparation-drop':self.preparation=False
   return out
  def pump(self):return self.call('pump')
  def image(self,name='rgba.png'):
   return self.call('image',media=PIXELS[name]['media'],file=str(ROOT/'tests/scene/image-cases'/name))['id']
  def observe(self,pid):
   while pid not in self.observed:self.tracing();left();time.sleep(.002)
   return self.children[pid]
  def exited(self,pid):
   fd=self.observe(pid);assert select.select([fd],[],[],left())[0],('helper survived',pid);self.observed[pid]['exited']=True
  def release(self,pid):
   fd=self.observe(pid)
   if pid in self.held:
    trace(17,pid);self.held.remove(pid);self.traced.remove(pid)
   self.observed[pid]['released']=True
  def drain(self,op,state,**args):
   while True:
    value=self.call(op,**args)
    if value['state']==state and value['reaped']:
     for pid in self.children:
      if select.select([self.children[pid]],[],[],0)[0]:self.observed[pid]['exited']=True
     return value
    assert value['state'] not in ('failed','unavailable') or value['state']==state,value
    self.pump();left();time.sleep(.002)
  def load(self,path,take=True,grants='rwe'):
   assert self.call('recovery',directory=str(path),grants=grants)['state']=='loading'
   assert self.call('replace',file=str(inputs['new']))=={'error':'recovery_queue.denied'}
   self.drain('recovery-poll','ready')
   if take:
    v=self.call('recovery-take');assert v['operation']=='load' and v['ticket']==1 and v['outcome']=='loaded' and v['bytes']==RECORDS['old'].decode() and v['digest']==sha(RECORDS['old'])
    assert v['context']==dict(session='editor:worker',profile='profile:primary',generation='4'*64,revision=7);assert self.call('recovery-take') is None
   file_bytes(path/'draft.json',RECORDS['old'])
  def finish(self,success=False):
   if self.closed:return
   try:
    if success:
     self.call('close')
     for id in list(self.images):self.call('image-drop',id=id)
     if self.recovery:self.call('recovery-drop')
     if self.preparation:self.call('preparation-drop')
     while self.surface or self.session or not self.call('status')['stopped']:
      if self.surface:self.call('surface-close')
      if self.session:self.call('session-close')
      self.pump();left()
     assert self.call('status')['images']==0 and self.call('status')['recovery']==0
     assert self.call('quit')=={'exit':True}
     while self.proc.returncode is None:self.tracing();left();time.sleep(.002)
     assert self.proc.returncode==0
   finally:
    self.cleaning=True
    if not select.select([self.pidfd],[],[],0)[0]:signal.pidfd_send_signal(self.pidfd,signal.SIGKILL)
    for pid,fd in self.children.items():
     if not select.select([fd],[],[],0)[0]:self.row.setdefault('forced_cleanup',[]).append(pid);signal.pidfd_send_signal(fd,signal.SIGKILL)
    until=time.monotonic()+5
    while self.traced:
     self.tracing();assert time.monotonic()<until,('trace cleanup deadline',self.traced);time.sleep(.002)
    for pid,fd in list(self.children.items()):
     assert select.select([fd],[],[],5)[0];os.close(fd)
     del self.children[pid]
     if pid in self.observed:self.observed[pid]['exited']=True
    if self.proc.returncode is None:self.proc.wait(timeout=5)
    os.close(self.pidfd);self.closed=True;self.row['exit']=self.proc.returncode;self.row['stderr']=self.proc.stderr.read().decode('utf-8','replace');save()
    if success:assert not self.row['stderr'] and not self.row.get('forced_cleanup'),self.row
  def __enter__(self):return self
  def __exit__(self,kind,value,tb):
   if kind is not None:self.row['failure']=''.join(traceback.format_exception(kind,value,tb));save()
   self.finish(kind is None)
 def alarm(*unused):raise TimeoutError('fixed worker case deadline')
 prior=signal.signal(signal.SIGALRM,alarm)
 try:
  if extension:
   extension(locals());assert [x['case'] for x in report['cases']]==CASES['cases'];report['outcome']='pass';return
  with case('ATTACH'):
   with Run() as q:assert q.call('status')==dict(attached=True,closing=False,stopped=False,images=0,recovery=0,bytes=0,processes=[])
  with case('GUI-WHILE-HELD'):
   with Run() as q:
    id=q.image();path=record_root('held');q.call('recovery',directory=str(path))
    time.sleep(.15);assert not q.children and q.call('image-poll',id=id)['pid']==0 and not q.call('image-poll',id=id)['reaped']
    assert q.call('recovery-poll')['state']=='loading';q.call('image-cancel',id=id);q.call('recovery-close')
    assert not q.call('image-poll',id=id)['reaped'] and not q.call('recovery-poll')['reaped'];q.pump()
    assert q.call('image-poll',id=id)['state']=='cancelled' and q.call('recovery-poll')['state']=='closed';assert not q.children;file_bytes(path/'draft.json',RECORDS['old'])
  with case('IMAGE-PIXELS'):
   with Run() as q:
    for name in CASES['images']:
     id=q.image(name);q.drain('image-poll','ready',id=id);pixels(q.call('image-take',id=id),PIXELS[name]);assert q.call('image-take',id=id)=={'error':'image.not_ready'};q.call('image-drop',id=id)
  with case('IMAGE-INPUTS'):
   with Run() as q:
    for media,file,code in [('wrong/type',inputs['old'],'image.media'),('image/png',inputs['empty'],'image.capacity'),('image/png',inputs['oversized'],'image.capacity')]:assert q.call('image',media=media,file=str(file))=={'error':code}
    assert q.call('status')['images']==0 and not q.children
  with case('IMAGE-CAPACITY'):
   with Run() as q:
    ids=[q.image() for _ in range(4)];assert q.call('status')['images']==4
    assert q.call('image',media='image/png',file=str(ROOT/'tests/scene/image-cases/rgba.png'))=={'error':'helpers.capacity'}
    assert not q.children
  with case('IMAGE-ORDER'):
   with Run(hold=(1,)) as q:
    ids=[q.image() for _ in range(4)];q.pump();first=[q.call('image-poll',id=id) for id in ids]
    assert all(s['pid'] for s in first[:2]) and all(s['pid']==0 for s in first[2:]);assert len(q.call('status')['processes'])==2
    for s in first[:2]:q.observe(s['pid'])
    q.pump();assert q.call('image-poll',id=ids[2])['pid']==0
    q.hold.clear()
    for s in first[:2]:q.release(s['pid'])
    for id in ids:q.drain('image-poll','ready',id=id);pixels(q.call('image-take',id=id),PIXELS['rgba.png'])
    assert len(q.row['children'])==4
  with case('QUEUED-CANCEL'):
   with Run() as q:
    id=q.image();q.call('image-cancel',id=id);assert q.call('image-take',id=id)=={'error':'image.not_ready'};q.pump();assert q.call('image-poll',id=id)['reaped'] and not q.children
  with case('ACTIVE-CANCEL'):
   with Run(hold=(1,)) as q:
    id=q.image();q.pump();s=q.call('image-poll',id=id);fd=q.observe(s['pid']);assert not s['reaped'] and not select.select([fd],[],[],0)[0]
    q.call('image-cancel',id=id);assert not q.call('image-poll',id=id)['reaped'];q.drain('image-poll','cancelled',id=id);q.exited(s['pid'])
  with case('RESULT-ERASURE'):
   with Run() as q:
    id=q.image();q.drain('image-poll','ready',id=id);assert q.call('status')['bytes']==16;q.call('image-cancel',id=id);assert q.call('status')['bytes']==0
    assert q.call('image-take',id=id)=={'error':'image.not_ready'};q.drain('image-poll','cancelled',id=id)
  with case('ABANDONED-SLOTS'):
   with Run() as q:
    ids=[q.image() for _ in range(4)]
    for id in ids:q.call('image-drop',id=id)
    assert q.call('status')['images']==4 and q.call('status')['bytes']==0
    assert q.call('image',media='image/png',file=str(ROOT/'tests/scene/image-cases/rgba.png'))=={'error':'helpers.capacity'}
    q.pump();assert q.call('status')['images']==0 and not q.children;id=q.image();q.drain('image-poll','ready',id=id)
  with case('RECOVERY-LOAD'):
   with Run() as q:
    path=record_root('load');q.load(path)
  with case('RECOVERY-COALESCE'):
   with Run() as q:
    path=record_root('coalesce');q.load(path)
    for ticket,name in [(2,'old'),(3,'middle'),(4,'new')]:assert q.call('replace',file=str(inputs[name]))=={'ticket':ticket}
    q.drain('recovery-poll','ready');v=q.call('recovery-take');assert v['ticket']==4 and v['operation']=='replace' and v['outcome']=='durable' and v['digest']==sha(RECORDS['new']);file_bytes(path/'draft.json',RECORDS['new'])
    q.hold={2};assert q.call('replace',file=str(inputs['old']))=={'ticket':5};q.pump();pid=q.call('recovery-poll')['pid'];q.observe(pid)
    for ticket,name in [(6,'new'),(7,'middle'),(8,'new')]:assert q.call('replace',file=str(inputs[name]))=={'ticket':ticket}
    assert q.call('recovery-take') is None;q.hold.clear();q.release(pid);q.drain('recovery-poll','ready');v=q.call('recovery-take');assert v['ticket']==8 and v['digest']==sha(RECORDS['new']);file_bytes(path/'draft.json',RECORDS['new'])
  with case('RECOVERY-RETIRE'):
   with Run() as q:
    path=record_root('retire');q.load(path);assert q.call('replace',file=str(inputs['new']))=={'ticket':2};assert q.call('retire')=={'ticket':3}
    assert q.call('replace',file=str(inputs['old']))=={'error':'recovery_queue.denied'};q.drain('recovery-poll','retired');v=q.call('recovery-take');assert v['ticket']==3 and v['operation']=='retire' and v['outcome']=='durable' and v['digest'] is None;file_bytes(path/'draft.json',None)
  with case('RECOVERY-DENIAL'):
   for grants,op in [('r','replace'),('rw','retire')]:
    with Run() as q:
     path=record_root('denied-'+grants);q.load(path,grants=grants);assert q.call(op,file=str(inputs['new']))=={'error':'recovery_queue.denied'};file_bytes(path/'draft.json',RECORDS['old'])
   with Run() as q:assert q.call('recovery',directory=str(path),grants='we')=={'error':'recovery_queue.denied'}
  with case('RECOVERY-CLOSE'):
   with Run() as q:
    path=record_root('close');q.load(path);q.hold={2};q.call('replace',file=str(inputs['new']));q.pump();pid=q.call('recovery-poll')['pid'];q.observe(pid)
    q.call('recovery-close');assert not q.call('recovery-poll')['reaped'];q.drain('recovery-poll','closed');q.exited(pid);assert q.call('recovery-take') is None;file_bytes(path/'draft.json',RECORDS['old'])
  with case('CONTEXT-ERASURE'):
   with Run() as q:
    path=record_root('erased');q.load(path,take=False);assert q.call('status')['bytes']==len(RECORDS['old']);q.call('recovery-close');assert q.call('recovery-take') is None
    q.drain('recovery-poll','closed');assert q.call('status')['bytes']==0;assert q.call('replace',file=str(inputs['new']))=={'error':'recovery_queue.denied'};file_bytes(path/'draft.json',RECORDS['old'])
  with case('INSTALLATION-CHANGE'):
   with Run() as q:
    path=image/'libexec/syspane'/names[0];raw=path.read_bytes();changed=raw+b'X';write(path,changed,0o755);write(folder/'changed-helper.z',zlib.compress(changed));s=path.lstat()
    report['mutations'].append(dict(path=str(path),sha256=sha(changed),bytes=len(changed),mode=s.st_mode,inode=s.st_ino,device=s.st_dev,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,blob='changed-helper.z'));save()
    try:
     id=q.image();s=q.drain('image-poll','failed',id=id);assert s['reason']=='installation.changed' and not q.children
     store=record_root('changed');q.call('recovery',directory=str(store));q.drain('recovery-poll','unavailable');v=q.call('recovery-take');assert v['outcome']=='unchanged' and v['bytes'] is None and not q.children;file_bytes(store/'draft.json',RECORDS['old'])
    finally:write(path,raw,0o755)
  with case('WRONG-THREAD'):
   with Run() as q:
    q.image();q.call('recovery',directory=str(record_root('thread')));assert q.call('wrong-thread')=={'errors':['helpers.owner']*3};assert not q.children
  with case('CLIENT-CLOSE'):
   with Run() as q:
    id=q.image();q.drain('image-poll','ready',id=id);path=record_root('client-close');q.load(path,take=False)
    q.call('close');assert q.call('image-take',id=id)=={'error':'image.not_ready'} and q.call('recovery-take') is None
    assert q.call('image',media='image/png',file=str(ROOT/'tests/scene/image-cases/rgba.png'))=={'error':'helpers.unavailable'}
    while not q.call('status')['stopped']:q.pump()
    assert q.call('status')['bytes']==0;file_bytes(path/'draft.json',RECORDS['old'])
  with case('CONSUMERS'):
   with Run() as q:
    q.call('surface');assert q.call('surface-paint')['state']=='loading'
    while True:
     q.pump();actual=q.call('surface-paint')
     if actual['state']=='ready':break
     left()
    expected=next(x for x in json.loads((ROOT/'tests/scene/image-cases/surface.json').read_bytes()) if x['width']==9 and x['height']==5 and x['fit']=='contain')
    assert actual['rgba']==expected['rgba'];assert q.call('surface-close')['stopped']
    fixture=json.loads((ROOT/'tests/editor/recovery-draft-cases.json').read_bytes());path=record_root('session',fixture['wire'].encode());q.call('session',directory=str(path))
    while True:
     actual=q.call('session-poll')
     if actual['state']=='offer':break
     q.pump();left()
    assert actual['restorable'] and not actual['editing'] and actual['scene']==fixture['authored']['scene']
    assert q.call('session-restore')=={'restored':True};actual=q.call('session-poll');assert actual['scene']==fixture['scene'] and actual['undo']==1;file_bytes(path/'draft.json',fixture['wire'].encode())
  with case('ORACLE'):
   failures=[];expected=PIXELS['rgba.png'];wrong=dict(width=2,height=2,rgba=list(expected['rgba']));wrong['rgba'][0]^=1
   for fn in (lambda:pixels(wrong,expected),lambda:file_bytes(folder/'load/draft.json',RECORDS['new'])):
    try:fn()
    except AssertionError as e:failures.append(str(e))
    else:raise AssertionError('wrong oracle passed')
   report['oracle_calibration']=failures;assert len(failures)==2
  assert [x['case'] for x in report['cases']]==CASES['cases'];report['outcome']='pass'
 except BaseException as e:report['error']=repr(e);report['traceback']=traceback.format_exc();raise
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,prior)
  for q in runs:q.finish()
  report['seconds']=time.monotonic()-start;report['finished_at']=datetime.now(timezone.utc).isoformat();report['files']={p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='result.json'};save();print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()

"""Independent directory/session oracles for the existing native helper owner."""
import copy,json,os
from pathlib import Path
import native_editor_helper_worker as harness

CASES_PATH=Path(__file__).with_name('recovery-admission-cases.json')
CASES=json.loads(CASES_PATH.read_bytes())

def exercise(env):
 Run,case,folder,report=(env[k] for k in ('Run','case','folder','report'))
 inputs=env['inputs'];records=harness.RECORDS
 report['extension_sha256']=harness.sha(Path(__file__).read_bytes())
 def fixture(name):
  base=folder/name;root=base/'syspane/state'/harness.sha(CASES['scope']['profile'].encode())/'recovery'
  root.mkdir(mode=0o700,parents=True)
  for p in (base,base/'syspane',base/'syspane/state',root.parent):p.chmod(0o700)
  harness.write(root/'draft.json',records['old'])
  a,b=root.parent.stat(),root.stat();scope=copy.deepcopy(CASES['scope'])
  directory=dict(path=str(root),uid=os.geteuid(),state_device=a.st_dev,state_inode=a.st_ino,recovery_device=b.st_dev,recovery_inode=b.st_ino)
  observation={k:v for k,v in scope.items() if k!='retain'}
  observation.update(generation=CASES['generation'],transfer=1,directory=directory)
  data=dict(location=dict(profile=scope['profile'],portable_root=str(base)),observation=observation,current=scope)
  file=folder/(name+'.admission.json');save(file,data);return root,file,data
 def save(file,data):harness.write(file,harness.encoded(data))
 def unchanged(root):harness.file_bytes(root/'draft.json',records['old'])
 def unavailable(q,root):
  q.call('recovery',directory=str(root));q.drain('recovery-poll','unavailable')
  assert q.call('recovery-take') is None and not q.children;unchanged(root)
 def withdrawn(q,root):
  q.drain('recovery-poll','closed');assert q.call('recovery-take') is None
  assert q.call('status')['bytes']==0
  assert q.call('replace',file=str(inputs['new']))=={'error':'recovery_queue.denied'}
  unchanged(root)
 with case('ADMITTED-FILES'):
  root,file,data=fixture('admitted')
  with Run(admission=file) as q:
   q.load(root);assert q.call('replace',file=str(inputs['new']))=={'ticket':2}
   q.drain('recovery-poll','ready');v=q.call('recovery-take')
   assert v['ticket']==2 and v['operation']=='replace' and v['outcome']=='durable' and v['digest']==harness.sha(records['new'])
   harness.file_bytes(root/'draft.json',records['new'])
   assert q.call('retire')=={'ticket':3};q.drain('recovery-poll','retired');v=q.call('recovery-take')
   assert v['ticket']==3 and v['operation']=='retire' and v['outcome']=='durable'
   harness.file_bytes(root/'draft.json',None)
 with case('SESSION-SCOPE'):
  for field in ('connection','epoch','profile','session','revision','policy_revision'):
   root,file,data=fixture('scope-'+field);old=data['current'][field];data['current'][field]=old+1 if isinstance(old,int) else old+':wrong';save(file,data)
   with Run(admission=file) as q:unavailable(q,root)
  for name,current in (('missing',None),('exception','invalid')):
   root,file,data=fixture('scope-'+name);data['current']=current;save(file,data)
   with Run(admission=file) as q:unavailable(q,root)
 with case('TASK-SCOPE'):
  for field,value in (('session','editor:wrong'),('profile','profile:wrong'),('generation','5'*64),('policy_revision',8),('grants','r')):
   root,file,data=fixture('task-'+field)
   with Run(admission=file) as q:
    q.call('recovery',directory=str(root),**{field:value});q.drain('recovery-poll','unavailable')
    assert q.call('recovery-take') is None and not q.children;unchanged(root)
  root,file,data=fixture('task-path');other=env['record_root']('other-task')
  with Run(admission=file) as q:unavailable(q,other)
  root,file,data=fixture('local-path');data['location']['portable_root']=str(folder/'unrelated');save(file,data)
  with Run(admission=file) as q:unavailable(q,root)
  root,file,data=fixture('digest');data['observation']['generation']='invalid';save(file,data)
  with Run(admission=file) as q:unavailable(q,root)
 with case('PERMISSIONS'):
  root,file,data=fixture('retention');data['current']['retain']=False;save(file,data)
  with Run(admission=file) as q:unavailable(q,root)
  root,file,data=fixture('erase-current');data['current']['erase']=False;save(file,data)
  with Run(admission=file) as q:
   q.load(root);q.call('retire');q.drain('recovery-poll','unavailable');unchanged(root)
   assert q.call('recovery-take') is None
  root,file,data=fixture('erase-original');data['observation']['erase']=False;save(file,data)
  with Run(admission=file) as q:
   q.load(root,grants='rw');assert q.call('retire')=={'error':'recovery_queue.denied'};unchanged(root)
 with case('DIRECTORY-IDENTITY'):
  for field in ('uid','state_device','state_inode','recovery_device','recovery_inode'):
   root,file,data=fixture('identity-'+field);data['observation']['directory'][field]+=1;save(file,data)
   with Run(admission=file) as q:unavailable(q,root)
 with case('DIRECTORY-REPLACEMENT'):
  for node in ('state','recovery'):
   root,file,data=fixture('replacement-'+node)
   with Run(admission=file) as q:
    q.load(root);selected=root.parent if node=='state' else root;moved=selected.with_name(selected.name+'-held');selected.rename(moved)
    selected.mkdir(mode=0o700)
    if node=='state':root.mkdir(mode=0o700)
    harness.write(root/'draft.json',records['new']);q.drain('recovery-poll','closed');assert q.call('recovery-take') is None
    harness.file_bytes(root/'draft.json',records['new']);unchanged(moved/'recovery' if node=='state' else moved)
    assert not (root/'.writer').exists()
 with case('NATIVE-PERMISSIONS'):
  for node in ('state','recovery','ancestor'):
   root,file,data=fixture('permission-'+node);selected=root.parent if node=='state' else root if node=='recovery' else root.parent.parent
   with Run(admission=file) as q:
    q.load(root);selected.chmod(0o777)
    try:withdrawn(q,root)
    finally:selected.chmod(0o700)
  root,file,data=fixture('symlink');moved=root.with_name('held');root.rename(moved);root.symlink_to(moved,target_is_directory=True)
  with Run(admission=file) as q:unavailable(q,root)
 with case('CHILD-SUBSTITUTION'):
  root,file,data=fixture('child-substitution')
  with Run(hold={2},admission=file) as q:
   q.call('recovery',directory=str(root));q.pump();pid=q.call('recovery-poll')['pid'];q.observe(pid);q.pump()
   # The request is already sent while the child is held before its first
   # instruction. Do not pump the parent until the child has refused the nodes.
   moved=root.with_name('held');root.rename(moved);root.mkdir(mode=0o700);harness.write(root/'draft.json',records['new'])
   q.release(pid);q.exited(pid)
   assert not (root/'.writer').exists() and not (moved/'.writer').exists()
   harness.file_bytes(root/'draft.json',records['new']);unchanged(moved)
   q.drain('recovery-poll','closed');assert q.call('recovery-take') is None
 with case('HELD-WITHDRAWAL'):
  root,file,data=fixture('held-withdrawal')
  with Run(admission=file) as q:
   q.load(root);q.hold={2};q.call('replace',file=str(inputs['new']));q.pump();pid=q.call('recovery-poll')['pid'];q.observe(pid)
   data['current']=None;save(file,data);withdrawn(q,root);q.exited(pid)
  root,file,data=fixture('staged-withdrawal')
  with Run(admission=file) as q:
   q.load(root);q.call('replace',file=str(inputs['new']))
   # The existing channel sends at most one queued grant per pump. Once the
   # pending record exists, withhold further pumping until authority is revoked.
   while not (root/'.pending').exists():q.pump();env['left']();harness.time.sleep(.002)
   while (root/'.pending').read_bytes()!=records['new']:env['left']();harness.time.sleep(.002)
   unchanged(root);pid=q.call('recovery-poll')['pid'];q.observe(pid)
   report['staged_withdrawal']=dict(pending_sha256=harness.sha((root/'.pending').read_bytes()),original_sha256=harness.sha((root/'draft.json').read_bytes()))
   data['current']=None;save(file,data);withdrawn(q,root);q.exited(pid)
   harness.file_bytes(root/'.pending',records['new'])
 with case('RESULT-WITHDRAWAL'):
  root,file,data=fixture('result-withdrawal')
  with Run(admission=file) as q:
   q.load(root,take=False);assert q.call('status')['bytes']==len(records['old'])
   data['current']=None;save(file,data);withdrawn(q,root)
 with case('NO-REVIVAL'):
  root,file,data=fixture('no-revival')
  with Run(admission=file) as q:
   q.load(root);data['current']=None;save(file,data);withdrawn(q,root)
   data['current']=copy.deepcopy(CASES['scope']);save(file,data);q.pump();assert q.call('recovery-poll')['state']=='closed'
   q.call('recovery-drop');q.call('recovery',directory=str(root));q.drain('recovery-poll','unavailable')
   assert q.call('recovery-take') is None;unchanged(root)
 with case('ORACLE'):
  try:harness.file_bytes(root/'draft.json',records['new'])
  except AssertionError as e:report['oracle_calibration']=str(e)
  else:raise AssertionError('wrong record oracle passed')

if __name__=='__main__':harness.main(exercise,CASES_PATH)

"""Fixed recovery bytes and file observations through the serialized native worker."""
import copy,json,time
from pathlib import Path
import native_editor_helper_worker as harness

CASES_PATH=harness.ROOT/'tests/editor/recovery-preparation-cases.json'

def exercise(env):
 Run,case,folder,report=(env[k] for k in ('Run','case','folder','report'))
 literal=json.loads((harness.ROOT/'tests/editor/recovery-draft-cases.json').read_bytes())
 raw=literal['wire'].encode();input_file=folder/'recovery.record';harness.write(input_file,raw)
 report['extension_sha256']=harness.sha(Path(__file__).read_bytes())
 report['recovery_fixture_sha256']=harness.sha((harness.ROOT/'tests/editor/recovery-draft-cases.json').read_bytes())
 def until(q,state):
  while True:
   value=q.call('session-poll')
   if value['state']==state:return value
   assert value['state']!='unavailable',value
   q.pump();env['left']();time.sleep(.002)
 def start(q,path):assert q.call('session',directory=str(path),asynchronous=True)=={'created':True}
 def held_offer(q,path):
  start(q,path)
  while True:
   value=q.call('session-poll')
   if value['preparations']==1:break
   assert value['state']=='loading',value
   q.pump();env['left']()
  assert value['state']=='loading' and not value['editing'] and not value['restorable'] and not value['may_apply']
  assert value['scene']==literal['authored']['scene'] and value['undo']==0
  return value
 def drain_preparation(q):
  while True:
   status=q.call('preparation-poll')
   if status['stopped']:return status
   q.pump();env['left']()
 def scene(actual,expected):assert actual==expected,'prepared scene mismatch'
 with case('HELD-PREPARATION'):
  path=env['record_root']('held-prepare',raw)
  with Run() as q:
   held=held_offer(q,path)
   for _ in range(5):assert q.call('session-poll')==held
   harness.file_bytes(path/'draft.json',raw)
   assert q.call('session-restore')=={'error':'recovery.unavailable'}
   actual=until(q,'offer');assert actual['restorable'] and not actual['editing']
 with case('PREPARED-OFFER'):
  path=env['record_root']('prepared-offer',raw)
  with Run() as q:
   start(q,path);assert until(q,'offer')['restorable']
   assert q.call('session-restore')=={'restored':True}
   actual=q.call('session-poll');assert actual['state']=='capturing' and not actual['may_apply'];scene(actual['scene'],literal['scene']);assert actual['undo']==1
   actual=until(q,'ready');assert actual['may_apply'];harness.file_bytes(path/'draft.json',raw)
 with case('PREPARED-CAPTURE'):
  path=env['record_root']('prepared-capture',None)
  with Run() as q:
   start(q,path);until(q,'ready');scene(q.call('draft-edit')['scene'],literal['scene'])
   pending=q.call('session-poll');assert pending['state']=='capturing' and not pending['may_apply'];harness.file_bytes(path/'draft.json',None)
   until(q,'ready');harness.file_bytes(path/'draft.json',raw)
   scene(q.call('draft-discard')['scene'],literal['authored']['scene']);until(q,'ready');harness.file_bytes(path/'draft.json',None)
 with case('PREPARATION-CANCEL'):
  with Run() as q:
   q.call('draft');assert q.call('prepare',file=str(input_file))=={'created':True}
   assert q.call('preparation-capacity')=={'error':'helpers.capacity'}
   status=q.call('preparation-poll');assert not status['ready'] and not status['stopped'] and status['handles']==1
   q.call('preparation-cancel');status=q.call('preparation-poll');assert status['stopped'] and not status['ready']
   assert q.call('preparation-take')=={'error':'recovery.not_ready'}
   assert q.call('preparation-drop')['handles']==0
   # Publish a result, then cancel before the GUI can consume it.
   q.call('prepare',file=str(input_file));assert drain_preparation(q)['ready'];q.call('preparation-cancel')
   assert q.call('preparation-take')=={'error':'recovery.not_ready'};q.call('preparation-drop')
   # Observe the live native computation before cancelling its delivery.
   q.call('prepare',file=str(input_file));q.call('pump-start')
   while True:
    status=q.call('preparation-poll')
    if status['running']:break
    assert not status['stopped'],'computation finished before running-state observation'
    env['left']()
   q.call('preparation-cancel');assert q.call('preparation-take')=={'error':'recovery.not_ready'}
   while q.call('worker-state')['busy']:env['left']();time.sleep(.002)
   status=q.call('preparation-poll');assert status['stopped'] and not status['ready'] and not status['running'];q.call('preparation-drop')
 with case('PREPARATION-ERASURE'):
  for action in ('session-invalidate','session-cancel','session-close'):
   path=env['record_root']('erase-'+action,raw)
   with Run() as q:
    held_offer(q,path);q.call(action)
    if q.session:
     q.pump();value=q.call('session-poll');assert not value['restorable'] and value['state']!='offer'
    harness.file_bytes(path/'draft.json',raw)
  path=env['record_root']('keep-proof',raw)
  with Run() as q:
   start(q,path);until(q,'offer');assert q.call('session-keep')=={'kept':True};q.pump();assert q.call('session-poll')['state']=='kept'
   assert q.call('session-restore')=={'error':'recovery.unavailable'};harness.file_bytes(path/'draft.json',raw)
  with Run() as q:
   q.call('draft');q.call('prepare',file=str(input_file));assert drain_preparation(q)['ready'];q.call('close')
   assert q.call('preparation-take')=={'error':'recovery.not_ready'};q.call('preparation-drop')
  for phase in ('loading','offer'):
   path=env['record_root']('closed-owner-'+phase,raw)
   with Run() as q:
    held_offer(q,path)
    if phase=='offer':assert until(q,'offer')['restorable']
    q.call('close')
    if phase=='offer':assert q.call('session-restore')=={'error':'recovery.unavailable'}
    q.pump();value=q.call('session-poll')
    assert value['state']=='unavailable' and not value['restorable'],('closed owner left recovery offered',phase,value)
    scene(value['scene'],literal['authored']['scene']);assert value['undo']==0
    assert q.call('session-restore')=={'error':'recovery.unavailable'};harness.file_bytes(path/'draft.json',raw)
 with case('COALESCED-CAPTURE'):
  path=env['record_root']('coalesced',None)
  with Run() as q:
   start(q,path);until(q,'ready');q.call('draft-edit',title='obsolete');q.call('session-poll')
   for _ in range(3):q.call('draft-edit');assert q.call('session-poll')['state']=='capturing'
   harness.file_bytes(path/'draft.json',None);actual=until(q,'ready');scene(actual['scene'],literal['scene']);harness.file_bytes(path/'draft.json',raw)
   # A clean latest draft retires the earlier durable record after preparation.
   q.call('draft-edit',title='obsolete-again');q.call('session-poll');q.call('draft-discard');until(q,'ready');harness.file_bytes(path/'draft.json',None)
 with case('INVALID-OFFER'):
  wrong=copy.deepcopy(literal['command']);wrong['expected_revision']='41';envelope=copy.deepcopy(literal['envelope']);envelope['command']=harness.encoded(wrong).decode()
  for name,data,action in (('malformed',b'{','session-keep'),('stale',harness.encoded(envelope),'session-discard')):
   path=env['record_root']('invalid-'+name,data)
   with Run() as q:
    start(q,path);value=until(q,'offer');assert not value['restorable'] and not value['editing'];scene(value['scene'],literal['authored']['scene'])
    assert q.call('session-restore')=={'error':'recovery.unavailable'};q.call(action)
    if action=='session-discard':until(q,'ready');harness.file_bytes(path/'draft.json',None)
    else:harness.file_bytes(path/'draft.json',data)
 with case('ORACLE'):
  path=env['record_root']('oracle',raw)
  with Run() as q:
   start(q,path);until(q,'offer');q.call('session-restore');actual=until(q,'ready');wrong=copy.deepcopy(literal['scene']);wrong['widgets'][0]['title']='wrong oracle'
   failures=[]
   for check in (lambda:scene(actual['scene'],wrong),lambda:harness.file_bytes(path/'draft.json',raw+b'\n')):
    try:check()
    except AssertionError as e:failures.append(str(e))
    else:raise AssertionError('wrong expected recovery passed')
   assert len(failures)==2;report['oracle_calibration']=failures

if __name__=='__main__':harness.main(exercise,CASES_PATH)

"""Fixed request task outcomes through the existing independently observed worker."""
import copy, itertools, json, os, time
from pathlib import Path
import native_editor_helper_worker as harness

CASES_PATH=Path(__file__).with_name('request-worker-cases.json')

def exercise(env):
 Run,case=env['Run'],env['case']
 fixture=json.loads((harness.ROOT/'tests/configuration/settings-content-fixture.json').read_bytes())
 scene=copy.deepcopy(fixture['authored']['scene']);scene['widgets'][0]['title']='Second'
 snapshot=dict(scene=scene,selection=[],undo=2,redo=0)
 def setup(q,large=False):assert q.call('history-fixture',large=large)=={'created':True}
 def status(q):return q.call('request-poll')
 def state(ready=False,stopped=False,running=False,error=''):return dict(ready=ready,stopped=stopped,running=running,error=error,handles=1)
 def create(q,intent='commit'):assert q.call('request-create',intent=intent)=={'created':True}
 def complete(q):q.pump();assert status(q)==state(ready=True,stopped=True)
 def take(q):assert q.call('request-take')=={'taken':True}
 def drop(q):assert q.call('request-drop')=={'dropped':True,'handles':0}
 def unchanged(q):assert q.call('history-snapshot')==snapshot and q.call('request-active')=={'active':False}
 def expected(intent='commit'):
  return dict(schema_version='0.5.0',request_id='request:native',expected_revision='40',policy_generation='7',intent=intent,
   operations=[dict(op='scene.replace',scene=scene)],content=fixture['selection'])
 def equal(actual,intent='commit'):
  assert set(actual)=={'ticket','epoch','request','command'} and actual['ticket']==1 and actual['epoch']=='E1' and actual['request']=='request:native',actual
  assert actual['command']==expected(intent),('command mismatch',actual)
 def running(q):
  create(q);q.call('pump-start')
  while True:
   s=status(q)
   if s['running']:break
   assert not s['stopped'],'computation finished before running-state observation'
   env['left']()
  tid=q.row['initial']['worker'];harness.trace(0x4207,tid)
  while True:
   found,event=os.waitpid(tid,os.WNOHANG|0x40000000)
   if found:assert os.WIFSTOPPED(event) and event>>16==128;break
   env['left']();time.sleep(.001)
  assert status(q)['running'],'computation finished before kernel stop'
  q.row.setdefault('request_running_witnesses',[]).append(dict(tid=tid,observation='running task and kernel interrupt stop'))
  return tid
 def release(q,tid):
  harness.trace(7,tid)
  while q.call('worker-state')['busy']:env['left']();time.sleep(.002)
 with case('HELD'):
  with Run() as q:
   setup(q);create(q)
   for _ in range(5):assert status(q)==state();unchanged(q)
   assert q.call('request-take')=={'error':'request.not_ready'}
   complete(q);take(q);unchanged(q);equal(q.call('request-adopt'));drop(q)
 with case('TRACE'):
  for intent in ('preview','commit'):
   with Run() as q:
    setup(q);create(q,intent);complete(q);take(q)
    assert q.call('request-take')=={'error':'request.not_ready'}
    unchanged(q);equal(q.call('request-adopt'),intent)
    assert q.call('request-active')=={'active':True};assert q.call('history-snapshot')==snapshot;drop(q)
 with case('CAPACITY'):
  with Run() as q:
   setup(q);create(q)
   for phase in ('queued','ready','taken'):
    if phase=='ready':complete(q)
    if phase=='taken':take(q)
    assert q.call('request-capacity')=={'error':'helpers.capacity'};unchanged(q)
   equal(q.call('request-adopt'));drop(q)
   assert q.call('request-reuse')=={'created':True};complete(q);drop(q)
 with case('INPUTS'):
  with Run() as q:
   setup(q);assert q.call('request-null')=={'error':'request.work'}
   assert q.call('request-unattached')=={'error':'helpers.unavailable'}
   assert q.call('request-consumed')=={'created':True};q.pump()
   assert status(q)==state(stopped=True,error='editor.request_consumed')
   assert q.call('request-take')=={'error':'request.not_ready'};unchanged(q);drop(q)
 with case('QUEUED-CANCEL'):
  with Run() as q:
   setup(q);create(q)
   for _ in range(2):assert q.call('request-cancel')=={'cancelled':True}
   assert status(q)==state(stopped=True,error='request.cancelled')
   assert q.call('request-take')=={'error':'request.not_ready'};q.pump();unchanged(q);drop(q)
 with case('READY-CANCEL'):
  with Run() as q:
   setup(q);create(q);complete(q);q.call('request-cancel')
   assert status(q)==state(stopped=True,error='request.cancelled')
   assert q.call('request-take')=={'error':'request.not_ready'};unchanged(q);drop(q)
 with case('RUNNING-CANCEL'):
  with Run() as q:
   setup(q,True);tid=running(q);q.call('request-cancel')
   assert status(q)==state(running=True,error='request.cancelled')
   assert q.call('request-take')=={'error':'request.not_ready'}
   assert q.call('request-capacity')=={'error':'helpers.capacity'}
   release(q,tid);assert status(q)==state(stopped=True,error='request.cancelled');drop(q)
 with case('DROP'):
  for phase in ('queued','ready','running'):
   with Run() as q:
    setup(q,phase=='running')
    if phase=='running':tid=running(q)
    else:
     create(q)
     if phase=='ready':complete(q)
    assert q.call('request-drop')==dict(dropped=True,handles=1 if phase=='running' else 0)
    if phase=='running':
     assert q.call('request-capacity')=={'error':'helpers.capacity'};release(q,tid)
    assert q.call('request-handles')=={'handles':0};create(q);complete(q);drop(q)
 with case('CLOSE'):
  for phase in ('queued','ready','running','worker-exit'):
   with Run() as q:
    setup(q,phase=='running')
    if phase=='running':tid=running(q)
    else:
     create(q)
     if phase=='ready':complete(q)
    if phase=='worker-exit':q.call('worker-exit')
    else:
     assert not q.call('close')['stopped']
     if phase=='running':assert not status(q)['stopped'];release(q,tid)
     else:q.pump()
    assert q.call('status')['stopped'] and status(q)['stopped'] and not status(q)['ready']
    assert q.call('request-take')=={'error':'request.not_ready'}
    assert q.call('request-capacity')=={'error':'helpers.unavailable'};drop(q)
 with case('STALE'):
  for phase in ('queued','ready','taken'):
   with Run() as q:
    setup(q);create(q)
    if phase!='queued':complete(q)
    if phase=='taken':take(q)
    assert q.call('history-select')=={'selected':True}
    if phase=='queued':complete(q)
    if phase!='taken':take(q)
    assert q.call('request-adopt')=={'error':'editor.request_stale'};unchanged(q);drop(q)
 with case('POLICY'):
  with Run() as q:
   setup(q);assert q.call('request-policy',deny=True)=={'changed':True};create(q);q.pump()
   assert status(q)==state(stopped=True,error='policy.denied');unchanged(q);drop(q)
  with Run() as q:
   setup(q);create(q);complete(q);take(q)
   q.call('request-policy',deny=True);q.call('request-policy',deny=False)
   assert q.call('request-adopt')=={'error':'editor.request_stale'};unchanged(q);drop(q)
 with case('COEXISTENCE'):
  for order in itertools.permutations(('request','history','recovery')):
   with Run() as q:
    setup(q)
    for kind in order:
     if kind=='request':create(q)
     elif kind=='history':assert q.call('history-create')=={'created':True}
     else:assert q.call('prepare',capture=True)=={'created':True}
    ready=set()
    for kind in order:
     q.pump();ready.add(kind)
     for name,op in [('request','request-poll'),('history','history-poll'),('recovery','preparation-poll')]:
      s=q.call(op);assert s==state(ready=name in ready,stopped=name in ready), (order,kind,name,s)
     unchanged(q)
    drop(q);q.call('history-drop');q.call('preparation-drop')
 with case('OWNER'):
  with Run() as q:
   setup(q);create(q);assert q.call('request-wrong-thread')=={'errors':['helpers.owner']*5}
   complete(q);take(q);equal(q.call('request-adopt'));drop(q)
 with case('ORACLE'):
  with Run() as q:
   setup(q);create(q);complete(q);take(q);actual=q.call('request-adopt');equal(actual)
   wrong=copy.deepcopy(actual);wrong['command']['expected_revision']='41'
   try:equal(wrong)
   except AssertionError:env['report']['oracle_calibration']='wrong literal revision rejected'
   else:raise AssertionError('wrong request expectation passed')
   drop(q)

if __name__=='__main__':harness.main(exercise,CASES_PATH)

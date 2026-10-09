"""Fixed history task outcomes observed through the existing native worker probe."""
import copy, json, os, time
from pathlib import Path
import native_editor_helper_worker as harness

CASES_PATH=Path(__file__).with_name('history-worker-cases.json')

def exercise(env):
 Run,case,folder=env['Run'],env['case'],env['folder']
 fixture=json.loads((harness.ROOT/'tests/editor/recovery-draft-cases.json').read_bytes())
 original=fixture['authored']['scene'];first=copy.deepcopy(original);second=copy.deepcopy(original)
 first['widgets'][0]['title']='First';second['widgets'][0]['title']='Second'
 def setup(q,large=False):assert q.call('history-fixture',large=large)=={'created':True}
 def expected(scene,selection,undo,redo):return dict(scene=scene,selection=selection,undo=undo,redo=redo)
 current=expected(second,[],2,0);once=expected(first,[],1,1);clean=expected(original,['widget:text'],0,2)
 def equal(actual,wanted):assert actual==wanted,('history snapshot mismatch',actual,wanted)
 def status(q):return q.call('history-poll')
 def create(q,forward=False):assert q.call('history-create',forward=forward)=={'created':True}
 def completed(q):
  q.pump();s=status(q);assert s==dict(ready=True,stopped=True,running=False,error='',handles=1),s
 def take(q):assert q.call('history-take')=={'taken':True}
 def drop(q):assert q.call('history-drop')=={'dropped':True,'handles':0}
 def running(q):
  create(q);q.call('pump-start')
  while True:
   s=status(q)
   if s['running']:break
   assert not s['stopped'],'computation finished before running-state observation'
   env['left']()
  # Stop the observed worker in the kernel, without adding a product test hook.
  tid=q.row['initial']['worker'];harness.trace(0x4207,tid)
  while True:
   found,event=os.waitpid(tid,os.WNOHANG|0x40000000)
   if found:assert os.WIFSTOPPED(event) and event>>16==128;break
   env['left']();time.sleep(.001)
  assert status(q)['running'],'computation finished before kernel stop'
  q.row.setdefault('history_running_witnesses',[]).append(dict(tid=tid,observation='running task and kernel interrupt stop'))
  return tid
 def release(q,tid):
  harness.trace(7,tid)
  while q.call('worker-state')['busy']:env['left']();time.sleep(.002)
 with case('HELD'):
  with Run() as q:
   setup(q);create(q);held=status(q)
   assert held==dict(ready=False,stopped=False,running=False,error='',handles=1)
   for _ in range(5):assert status(q)==held;equal(q.call('history-snapshot'),current)
   assert q.call('history-take')=={'error':'history.not_ready'}
   completed(q);take(q);equal(q.call('history-adopt'),once);drop(q)
 with case('TRACE'):
  with Run() as q:
   setup(q)
   for forward,wanted in ((False,once),(False,clean),(True,expected(first,['widget:text'],1,1)),(True,current)):
    create(q,forward);completed(q);take(q)
    assert q.call('history-take')=={'error':'history.not_ready'}
    equal(q.call('history-adopt'),wanted);drop(q)
   assert q.call('history-create',forward=True)=={'created':False}
 with case('CAPACITY'):
  with Run() as q:
   setup(q);create(q)
   for phase in ('queued','ready','taken'):
    if phase=='ready':completed(q)
    if phase=='taken':take(q)
    assert q.call('history-capacity')=={'error':'helpers.capacity'}
    equal(q.call('history-snapshot'),current)
   equal(q.call('history-adopt'),once);drop(q);create(q);completed(q);take(q);equal(q.call('history-adopt'),clean);drop(q)
 with case('INPUTS'):
  with Run() as q:
   setup(q);assert q.call('history-null')=={'error':'history.work'}
   assert q.call('history-consumed')=={'created':True};q.pump()
   assert status(q)==dict(ready=False,stopped=True,running=False,error='editor.history_consumed',handles=1)
   assert q.call('history-take')=={'error':'history.not_ready'};equal(q.call('history-snapshot'),current);drop(q)
 with case('QUEUED-CANCEL'):
  with Run() as q:
   setup(q);create(q)
   for _ in range(2):assert q.call('history-cancel')=={'cancelled':True}
   assert status(q)==dict(ready=False,stopped=True,running=False,error='history.cancelled',handles=1)
   assert q.call('history-take')=={'error':'history.not_ready'};q.pump();equal(q.call('history-snapshot'),current);drop(q)
 with case('READY-CANCEL'):
  with Run() as q:
   setup(q);create(q);completed(q);q.call('history-cancel')
   assert status(q)==dict(ready=False,stopped=True,running=False,error='history.cancelled',handles=1)
   assert q.call('history-take')=={'error':'history.not_ready'};equal(q.call('history-snapshot'),current);drop(q)
 with case('RUNNING-CANCEL'):
  with Run() as q:
   setup(q,True);tid=running(q);q.call('history-cancel')
   assert status(q)==dict(ready=False,stopped=False,running=True,error='history.cancelled',handles=1)
   assert q.call('history-take')=={'error':'history.not_ready'}
   assert q.call('history-capacity')=={'error':'helpers.capacity'}
   release(q,tid);assert status(q)==dict(ready=False,stopped=True,running=False,error='history.cancelled',handles=1);drop(q)
 with case('DROP'):
  for phase in ('queued','ready','running'):
   with Run() as q:
    setup(q,phase=='running')
    if phase=='running':tid=running(q)
    else:
     create(q)
     if phase=='ready':completed(q)
    assert q.call('history-drop')==dict(dropped=True,handles=1 if phase=='running' else 0)
    if phase=='running':
     assert q.call('history-capacity')=={'error':'helpers.capacity'};release(q,tid)
    assert q.call('history-handles')=={'handles':0};create(q);completed(q);drop(q)
 with case('CLOSE'):
  for phase in ('queued','ready','running','worker-exit'):
   with Run() as q:
    setup(q,phase=='running')
    if phase=='running':tid=running(q)
    else:
     create(q)
     if phase=='ready':completed(q)
    if phase=='worker-exit':q.call('worker-exit')
    else:
     assert not q.call('close')['stopped']
     if phase=='running':assert not status(q)['stopped'];release(q,tid)
     else:q.pump()
    assert q.call('status')['stopped'];assert status(q)['stopped'] and not status(q)['ready']
    assert q.call('history-take')=={'error':'history.not_ready'}
    assert q.call('history-capacity')=={'error':'helpers.unavailable'};drop(q)
 with case('STALE'):
  for phase in ('queued','ready','taken'):
   with Run() as q:
    setup(q);create(q)
    if phase!='queued':completed(q)
    if phase=='taken':take(q)
    assert q.call('history-select')=={'selected':True}
    if phase=='queued':completed(q)
    if phase!='taken':take(q)
    assert q.call('history-adopt')=={'error':'editor.history_stale'};equal(q.call('history-snapshot'),current);drop(q)
 with case('COEXISTENCE'):
  for first_kind in ('history','recovery'):
   with Run() as q:
    setup(q)
    if first_kind=='history':create(q)
    assert q.call('prepare',capture=True)=={'created':True}
    if first_kind=='recovery':create(q)
    q.pump();h=status(q);r=q.call('preparation-poll')
    assert h['ready']==(first_kind=='history') and r['ready']==(first_kind=='recovery')
    assert h['handles']==r['handles']==1
    q.pump();assert status(q)['ready'] and q.call('preparation-poll')['ready']
    recovery=q.call('preparation-take')
    if first_kind=='recovery':assert recovery=={'error':'recovery.prepared_stale'}
    else:
     record=json.loads(recovery['bytes']);command=json.loads(record['command'])
     assert command['operations']==[dict(op='scene.replace',scene=second)]
    take(q);equal(q.call('history-adopt'),once);drop(q);q.call('preparation-drop')
 with case('OWNER'):
  with Run() as q:
   setup(q);create(q);assert q.call('history-wrong-thread')=={'errors':['helpers.owner']*4}
   completed(q);take(q);equal(q.call('history-adopt'),once);drop(q)
 with case('ORACLE'):
  with Run() as q:
   setup(q);create(q);completed(q);take(q);actual=q.call('history-adopt')
   wrong=copy.deepcopy(once);wrong['scene']['widgets'][0]['title']='wrong oracle'
   try:equal(actual,wrong)
   except AssertionError:env['report']['oracle_calibration']='wrong literal scene rejected'
   else:raise AssertionError('wrong history expectation passed')
   drop(q)

if __name__=='__main__':harness.main(exercise,CASES_PATH)

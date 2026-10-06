"""Observe real network acquisition, bounded OS threads and obsolete-result rejection."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import sys
import time
import uuid
from native_ipc import Process, Harness, events
from native_network import linux_rows
from native_collector import route_sockets, verify_documents, verify_presentation

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/fault'))
from native_recovery import ObservedChild

def ipc_revocation(executable,record,private):
    _,root=Harness(executable).endpoint()
    for name in ('h','d'):(root/name).mkdir(mode=0o700)
    case={'case':'ipc-revoke-pending','outcome':'fail'};record['cases'].append(case)
    before=linux_rows();lower=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
    process=Process([str(executable),'supervisor',str(root),'revoke-pending'])
    child=None;tid=None;revoked=False;stopped=False
    try:
        deadline=time.monotonic()+10
        while True:
            assert time.monotonic()<deadline,'IPC revocation deadline'
            try:event=process.events.get(timeout=.1)
            except queue.Empty:
                if process.process.poll() is not None and not process.reader.is_alive():break
                continue
            kind=event.get('event')
            if kind=='spawned':
                assert child is None;child=ObservedChild(event['pid'])
            elif kind=='revoked':
                assert child is not None and event['pid']==child.pid and not child.exited(0)
                assert not event['payload'],'IPC projection removed while source task is pending'
                tasks=list(Path(f'/proc/{child.pid}/task').iterdir())
                workers=[int(path.name) for path in tasks if int(path.name)!=child.pid]
                assert len(tasks)==2 and len(workers)==1,'one live acquisition worker during revocation'
                tid=workers[0]
                assert Path(f'/proc/{child.pid}/task/{tid}').is_dir() and len(route_sockets(child.pid))==1,'revocation preceded native completion'
                revoked=True
            elif kind=='stopped':
                assert revoked and child.exited(2000) and event['os_confirmed'] and not event['forced']
                assert event['code']==0 and not event['signaled'];stopped=True
        assert process.finish(2)==0 and revoked and stopped and not events(process,'error')
        after=linux_rows();upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        compared=verify_documents(process,before,after,lower,upper,'revoke')
        fields=verify_presentation(process,lower,upper)
        assert len(events(process,'spawned'))==1,'no replacement source before exit'
        case.update(outcome='pass',rows_compared=compared,presentation_fields_compared=fields,
                    revocation_while_native_thread_alive=True,independent_child_exit=True,forced_stop=False)
    finally:
        process.stop();private.append({'mode':'ipc-revoke-pending','process':process.record(),'before':before,'lower':lower})
        if child:child.close()
        for name in ('h','d'):
            directory=root/name
            if not list(directory.iterdir()):directory.rmdir()
        if not list(root.iterdir()):root.rmdir()
        elif case['outcome']=='pass':raise AssertionError('owned endpoint cleanup')
        print('NATIVE-DEMAND-EXECUTOR.ipc-revoke-pending: '+case['outcome'],flush=True)

def verify(process,before,after,lower,upper,mode):
    assert before and set(before)==set(after),'stable independent inventory'
    samples=events(process,'sample')
    assert len(samples)==(2 if mode=='merge' else 1),'only current jobs publish'
    previous=None
    for number,event in enumerate(samples,1):
        assert event['recording']==(mode=='merge'),'recorder-only demand'
        doc=event['document'];assert doc['generation']==str(number) and doc['completeness']=='complete'
        entities={row['id']:row for row in doc['entities']}
        assert {row['identity']['native_index'] for row in entities.values()}==set(before)
        observations={(o['entity_id'],o['field']):o for o in doc['observations']}
        assert len(observations)==4*len(entities)
        for identity,entity in entities.items():
            index=entity['identity']['native_index']
            for direction in ('receive','transmit'):
                field='network.'+direction+'_bytes';counter=observations[identity,field];rate=observations[identity,field+'_per_second']
                assert counter['acquisition']=='success' and counter['value']['kind']=='uint64'
                value=int(counter['value']['data']);stamp=int(counter['measured_at']['nanoseconds'])
                assert before[index][direction]<=value<=after[index][direction],'independent counter bracket'
                assert lower<=stamp<=upper and counter['measured_at']['clock_id']=='linux.boottime','actual measurement time'
                if previous:
                    prior=previous[identity,field];elapsed=stamp-int(prior['measured_at']['nanoseconds']);delta=value-int(prior['value']['data'])
                    assert elapsed>0 and delta>=0 and rate['sample_interval_ns']==str(elapsed)
                    assert math.isclose(rate['value']['data'],float(Fraction(delta*1_000_000_000,elapsed)),rel_tol=4e-15,abs_tol=1e-9)
                else:assert rate['value'] is None and rate['acquisition']=='pending'
        previous=observations
    discarded=events(process,'discarded_candidate')
    assert len(discarded)==(0 if mode=='merge' else 1)
    if discarded:
        candidate=discarded[0]
        assert lower<=int(candidate['measured_ns'])<=upper
        assert {row['index'] for row in candidate['rows']}==set(before)
        for row in candidate['rows']:
            for direction in ('receive','transmit'):assert before[row['index']][direction]<=int(row[direction])<=after[row['index']][direction]
        assert candidate['ticket'] not in {event['ticket'] for event in samples},'obsolete real result not published'
    return len(samples),len(before)

def main():
    executable=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]).resolve();output.mkdir(parents=True,exist_ok=True)
    identity=uuid.uuid4().hex
    record={'case':'NATIVE-DEMAND-EXECUTOR','outcome':'fail','executed_at':datetime.now(timezone.utc).isoformat(),
            'executable_sha256':hashlib.sha256(executable.read_bytes()).hexdigest(),
            'oracle_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[]}
    private=[]
    try:
        for mode in ('merge','cancel','revoke','timeout'):
            case={'case':mode,'outcome':'fail'};record['cases'].append(case)
            before=linux_rows();lower=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            process=Process([str(executable),'demand-exercise',mode]);tid=None;joined=False;live=False;held=False;drained=False
            try:
                deadline=time.monotonic()+8
                while True:
                    assert time.monotonic()<deadline,'native case deadline'
                    try:event=process.events.get(timeout=.1)
                    except queue.Empty:
                        if process.process.poll() is not None and not process.reader.is_alive():break
                        continue
                    kind=event.get('event');pid=process.process.pid
                    if kind=='task_live':
                        tid=event['tid'];assert tid!=pid and event['pid']==pid
                        assert (Path(f'/proc/{pid}/task')/str(tid)).is_dir(),'native task exists'
                        assert len(list(Path(f'/proc/{pid}/task').iterdir()))==2,'one native worker'
                        assert len(route_sockets(pid))==1,'one actual watched source';live=True
                    elif kind=='slot_held':
                        assert live and event['tid']==tid and (Path(f'/proc/{pid}/task')/str(tid)).is_dir(),'cancel did not manufacture native exit'
                        assert event['cancelled']==(mode!='merge') and event['leases']==(0 if mode=='revoke' else 1)
                        assert len(list(Path(f'/proc/{pid}/task').iterdir()))==2,'no replacement thread while slot occupied';held=True
                    elif kind=='task_joined':
                        assert live and held and not (Path(f'/proc/{pid}/task')/str(tid)).exists(),'native join before release'
                        assert event['tid']==tid and event['accepted']==(mode=='merge');joined=True
                    elif kind=='sample':assert joined,'publication follows exact completion'
                    elif kind=='drained':
                        assert not route_sockets(pid) and len(list(Path(f'/proc/{pid}/task').iterdir()))==1,'final native resources released';drained=True
                assert process.finish(2)==0 and not events(process,'error')
                after=linux_rows();upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                count,rows=verify(process,before,after,lower,upper,mode)
                assert live and held and joined and drained
                case.update(outcome='pass',publications=count,interfaces_compared=rows,native_thread_observed=True,native_join_observed=True,final_watch_release_observed=True)
            finally:
                process.stop();private.append({'mode':mode,'process':process.record(),'before':before,'lower':lower})
                print('NATIVE-DEMAND-EXECUTOR.'+mode+': '+case['outcome'],flush=True)
        ipc_revocation(executable,record,private)
        record['outcome']='pass'
    except Exception as error:
        path=output/('NATIVE-DEMAND-EXECUTOR-'+identity+'.private.json')
        path.write_text(json.dumps({'exception':type(error).__name__,'reason':str(error),'attempts':private},indent=2)+'\n')
        record['private_failure']={'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        raise RuntimeError('native demand acceptance failed; inspect owned private evidence') from None
    finally:
        path=output/('NATIVE-DEMAND-EXECUTOR-'+identity+'.json')
        path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
        print('Native evidence: '+str(path),flush=True)

if __name__=='__main__':main()

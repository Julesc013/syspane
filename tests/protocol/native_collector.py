"""Independent native counter, time, process-exit and demand-release observations."""
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import stat
import sys
import time
import uuid
from native_ipc import Process,Harness,events
from native_network import linux_rows
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/fault'))
from native_recovery import ObservedChild

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def route_sockets(pid):
    sockets=set()
    for path in Path(f'/proc/{pid}/fd').iterdir():
        target=os.readlink(path)
        if target.startswith('socket:['):sockets.add(target[8:-1])
    rows=Path(f'/proc/{pid}/net/netlink').read_text().splitlines();columns=rows[0].split()
    return [row for row in (dict(zip(columns,line.split())) for line in rows[1:]) if row['Inode'] in sockets and row['Eth']=='0' and int(row['Groups'],16)&1]

def verify_documents(process,before,after,lower,upper,mode):
    imported=events(process,'imported');expected={'live':2,'failure':3,'replay':3,'hang':3,'crash':3,'unsubscribe':1,'revoke':1,'parent-loss':1}[mode]
    assert len(imported)==expected,'publication count'
    assert set(before)==set(after) and before,'stable independent inventory'
    previous={};bodies=[];row_count=0
    for event in imported:
        body=json.loads(event['body']);bodies.append(body);doc=body['snapshot'];epoch=doc['producer_epoch']
        assert body['producer_id']=='producer:network' and body['clock_id']=='linux.boottime','source/clock binding'
        assert doc['schema_version']=='0.2.0' and doc['completeness']=='complete','complete measured document'
        entities={entity['id']:entity for entity in doc['entities']}
        assert {entity['identity']['native_index'] for entity in entities.values()}==set(before),'entity coverage'
        observations={(o['entity_id'],o['field']):o for o in doc['observations']}
        assert len(observations)==4*len(entities)==len(doc['observations']),'field coverage'
        old=previous.get(epoch);duplicate=bool(event['duplicate'])
        if duplicate:
            assert old and event['body']==old['body'],'exact body replay'
        successful=all(o['acquisition']=='success' for o in doc['observations'] if o['field'].endswith('_bytes'))
        for identity,entity in entities.items():
            index=entity['identity']['native_index'];low,high=before[index],after[index]
            assert int(entity['identity']['native_type'])==low['native_type']==high['native_type'],'interface type'
            for direction,field in (('receive','network.receive_bytes'),('transmit','network.transmit_bytes')):
                counter=observations[(identity,field)];value=counter['value']['data']
                assert counter['value']['kind']=='uint64' and isinstance(value,str) and value==str(int(value)),'exact counter type'
                assert low[direction]<=int(value)<=high[direction]<=2**64-1,'independent counter bracket'
                stamp=int(counter['measured_at']['nanoseconds']);now=int(event['now_ns'])
                assert lower<=stamp<=now<=upper and now-stamp<3_000_000_000,'qualified sample age'
                rate=observations[(identity,field+'_per_second')]
                if not successful:
                    assert old and not duplicate,'failure needs earlier real sample'
                    old_doc=json.loads(old['body'])['snapshot'];old_obs={(o['entity_id'],o['field']):o for o in old_doc['observations']}
                    for candidate in (counter,rate):
                        prior=old_obs[(identity,candidate['field'])]
                        assert all(candidate[k]==prior[k] for k in ('value','measured_at','observed_at','sample_interval_ns')),'retained measurement'
                        assert candidate['acquisition']=='failed' and candidate['error']['code']=='network.acquisition_failed','reported source failure'
                        assert candidate['freshness']==('stale' if candidate['value'] is not None else 'unknown'),'failure freshness'
                elif duplicate:
                    pass
                elif old:
                    prior_doc=json.loads(old['body'])['snapshot'];prior_obs={(o['entity_id'],o['field']):o for o in prior_doc['observations']}
                    prior=prior_obs[(identity,field)];elapsed=stamp-int(prior['measured_at']['nanoseconds'])
                    delta=int(value)-int(prior['value']['data'])
                    assert elapsed>0 and delta>=0,'successful interval'
                    expected_rate=float(Fraction(delta*1_000_000_000,elapsed))
                    assert rate['acquisition']=='success' and rate['sample_interval_ns']==str(elapsed),'actual interval metadata'
                    assert math.isclose(rate['value']['data'],expected_rate,rel_tol=4e-15,abs_tol=1e-9),'independent rate calculation'
                    if mode=='failure':assert elapsed>=2_000_000_000,'failure gap interval'
                else:
                    assert rate['value'] is None and rate['measured_at'] is None and rate['acquisition']=='pending','first interval pending'
        if successful and not duplicate:previous[epoch]=event
        row_count+=len(entities)
    if mode=='replay':assert [e['duplicate'] for e in imported]==[False,True,False],'duplicate receipt'
    else:assert not any(e['duplicate'] for e in imported),'unexpected duplicate'
    if mode=='failure':assert [b['snapshot']['generation'] for b in bodies]==['1','2','3'],'failed state revision'
    if mode in ('hang','crash'):
        retained=events(process,'retained');assert len(retained)==1 and retained[0]['retained'],'failed source retained'
        assert retained[0]['snapshot']==bodies[0]['snapshot'],'retained age and epoch unchanged'
        assert bodies[0]['snapshot']['producer_epoch']!=bodies[1]['snapshot']['producer_epoch'],'replacement epoch'
    if mode=='revoke':assert len(events(process,'revoked'))==1 and not events(process,'revoked')[0]['payload'],'consumer policy erasure'
    return row_count

def main():
    executable,output=(Path(v).resolve() for v in sys.argv[1:3]);assert output.parent==executable.parent and output.name=='native-evidence'
    output.mkdir(exist_ok=True);identity=uuid.uuid4().hex[:12]
    report={'family':'NATIVE-COLLECTOR','outcome':'fail','executed_at':datetime.now(timezone.utc).isoformat(),'executable_sha256':sha(executable),'cases':[],
        'source_inputs':{path.relative_to(ROOT).as_posix():sha(path) for folder in ('source','tests/protocol','tests/fault') for path in (ROOT/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts},
        'qualification':'Real Linux collection and measured receipt under owned child supervision; typed policy and injected failures do not qualify installed policy, actual kernel faults or a desktop edition.',
        'disclosure':'Public outcomes/counts/timings only. Raw native documents and OS brackets remain in memory or owned ignored private failure evidence.'}
    for name in ('spec/delivery/packages/w-25-network-publication.md','spec/telemetry/metrics.json'):report['source_inputs'][name]=sha(ROOT/name)
    private=[]
    try:
        for mode in ('live','failure','replay','hang','crash','unsubscribe','revoke','parent-loss'):
            case={'case':'NATIVE-COLLECTOR.'+mode.upper(),'outcome':'fail'};report['cases'].append(case)
            _,owned=Harness(executable).endpoint();address=str(owned)
            for suffix in ('h','d'):(owned/suffix).mkdir(mode=0o700)
            process=None;observers={};socket_identities={};exited=[];released=False;registered=False
            start=time.monotonic();before=linux_rows();after=None;upper=None;lower=time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            try:
                process=Process([str(executable),'supervisor',address,mode])
                while time.monotonic()-start<35:
                    try:event=process.events.get(timeout=.1)
                    except queue.Empty:
                        if process.process.poll() is not None and not process.reader.is_alive():break
                        continue
                    name=event.get('event')
                    if name=='error':raise AssertionError('collector reported failure')
                    if name=='ready':
                        assert event['unprivileged'] and event['endpoint_controls'],'endpoint authority'
                        socket_identities={owned/suffix/'s':os.lstat(owned/suffix/'s') for suffix in ('h','d')}
                    elif name=='spawned':
                        assert all(observer.exited(0) for observer in observers.values()),'replacement before external exit proof'
                        observers[event['pid']]=ObservedChild(event['pid'])
                    elif name=='authenticated':assert event['pid']==event['health_peer']==event['data_peer'] and event['pid'] in observers,'both authenticated streams'
                    elif name=='imported' and mode in ('live','failure','replay','hang'):
                        assert len(route_sockets(event['pid']))==1,'live owned route subscription';registered=True
                    elif name=='stopped':
                        assert event['os_confirmed'] and observers[event['pid']].exited(2000),'external held child exit'
                        exited.append(event['pid'])
                    elif name=='demand_released':assert not route_sockets(event['pid']),'watch survived demand release';released=True
                    elif name=='parent_loss_ready':
                        process.stop();assert all(observer.exited(3000) for observer in observers.values()),'child survived parent loss';break
                assert process.finish(3)==( -9 if mode=='parent-loss' else 0),'owned parent exit'
                upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME);after=linux_rows()
                assert not events(process,'error'),'probe error'
                case['rows_compared']=verify_documents(process,before,after,lower,upper,mode)
                launches=events(process,'spawned');assert len(launches)==(2 if mode in ('hang','crash') else 1),'bounded launch count'
                assert len(observers)==len(launches) and all(observer.exited(0) for observer in observers.values()),'final independent child exit'
                if mode!='parent-loss':assert exited==[event['pid'] for event in launches],'stop ordering'
                if mode in ('unsubscribe','revoke'):assert released,'demand release observation'
                if mode=='hang':
                    fault=events(process,'fault');assert len(fault)==1 and 3000<=fault[0]['since_heartbeat_ms']<=4000,'independent expiry bound'
                    assert launches[1]['observed_ms']-fault[0]['observed_ms']>=1000 and events(process,'stopped')[0]['forced'],'restart backoff and native stop'
                    case['expiry_ms']=fault[0]['since_heartbeat_ms']
                if mode=='crash':
                    fault=events(process,'fault');assert len(fault)==1 and fault[0]['reason']=='child.crashed','observed process failure'
                    stopped=events(process,'stopped')[0]
                    assert stopped['code']==73 and not stopped['signaled'] and not stopped['forced'],'unforced crash exit'
                    assert launches[1]['observed_ms']-fault[0]['observed_ms']>=1000,'crash restart backoff'
                case.update(outcome='pass',launches=len(launches),independent_exits=len(observers),watch_registration_observed=registered,watch_release_observed=released,
                    elapsed_seconds=round(time.monotonic()-start,3))
                case['child_observations']=[{'pid':pid,'observer':'pidfd','observed_alive':True,'observed_exited':observer.exited(0)} for pid,observer in observers.items()]
                safe_events={'ready','spawned','authenticated','fault','stopped','demand_released','parent_loss_ready','complete'}
                safe_fields={'event','observed_ms','pid','attempt','epoch','health_peer','data_peer','code','signaled','forced','os_confirmed','launches',
                    'since_heartbeat_ms','backoff_ms','reason','endpoint_controls','unprivileged'}
                case['lifecycle']=[{key:value for key,value in event.items() if key in safe_fields} for event in process.lines if event.get('event') in safe_events]
            finally:
                if process:process.stop();private.append({'mode':mode,'process':process.record(),'before':before,'after':after,'lower_clock_ns':lower,'upper_clock_ns':upper})
                for observer in observers.values():observer.close()
                if mode=='parent-loss' and process and process.process.returncode==-9:
                    for path,original in socket_identities.items():
                        current=os.lstat(path)
                        assert path.parent.parent==owned and current.st_dev==original.st_dev and current.st_ino==original.st_ino and current.st_uid==os.geteuid() and stat.S_ISSOCK(current.st_mode),'owned abandoned socket identity'
                        path.unlink()
                for suffix in ('h','d'):
                    directory=owned/suffix
                    if not list(directory.iterdir()):directory.rmdir()
                if not list(owned.iterdir()):owned.rmdir()
                elif case['outcome']=='pass':raise AssertionError('owned endpoint cleanup')
                print(case['case']+': '+case['outcome'],flush=True)
        report['outcome']='pass'
    except Exception as error:
        failure=output/('NATIVE-COLLECTOR-'+identity+'.private.json')
        failure.write_text(json.dumps({'exception':type(error).__name__,'reason':str(error),'exchanges':private},indent=2)+'\n',encoding='utf-8')
        report['private_failure']={'filename':failure.name,'sha256':sha(failure),'scope':'owned ignored output only'}
        raise RuntimeError('native collector acceptance failed; inspect the owned private record') from None
    finally:
        path=output/('NATIVE-COLLECTOR-'+identity+'.json');path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print('Native evidence: '+str(path),flush=True)
if __name__=='__main__':main()

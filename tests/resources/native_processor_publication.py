"""Actual controller/worker/peer checks with independent proc/sysfs and integer math."""
from pathlib import Path
from fractions import Fraction
import copy
import hashlib
import json
import math
import os
import select
import sys
import time
import traceback
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/configuration'),str(ROOT/'tests/resources')]
from native_network_service import Node, encoded
from native_linux_processor import observation

FEATURES=['telemetry.snapshot','telemetry.measured-time','telemetry.monotonic-replay','telemetry.processor']
FIELDS=['linux.cpu.execution_percent','linux.cpu.interval_busy_ticks','linux.cpu.interval_total_ticks']
def documents(node):return [json.loads(v['body'])['snapshot'] for v in node.snapshots]
def cpu_fields(doc):return [v for v in doc['observations'] if v['source_id']=='provider:linux-processor']
def unique_current(node):
    values={}
    for doc in documents(node):
        rows=cpu_fields(doc)
        if rows and all(v['acquisition']=='success' for v in rows):values[int(rows[0]['measured_at']['nanoseconds'])]=doc
    return list(values.values())
def captures(node):
    path=node.folder/'processor-captures.jsonl'
    if not path.exists():return []
    raw=path.read_bytes();assert len(raw)<4194304
    return [json.loads(line) for line in raw.splitlines()]
def verify(before,after,raw,docs):
    assert before['online']==after['online'] and len(raw)>=3 and len(docs)>=2
    good=[v for v in raw if v['code']==0]
    for capture in good:
        assert capture['hz']==before['hz']==after['hz']
        assert [v['index'] for v in capture['rows']]==before['online']
        for row in capture['rows']:
            cpu=row['index'];assert {k:row[k] for k in ('package','core','peers')}==before['topology'][cpu]==after['topology'][cpu]
            for low,value,high in zip(before['counters'][cpu],row['accounting'],after['counters'][cpu]):assert low<=value<=high
    pairs=[]
    for a,b in zip(good,good[1:]):
        values={row['index']:[y-x for x,y in zip(old['accounting'],row['accounting'])] for old,row in zip(a['rows'],b['rows'])}
        if any(any(v<0 for v in delta) or sum(delta)==0 for delta in values.values()):continue
        pairs.append({cpu:(sum(delta[n] for n in (0,1,2,5,6)),sum(delta)) for cpu,delta in values.items()})
    assert len(pairs)>=len(docs)
    previous_stamp=None
    for doc,expected in zip(docs,pairs):
        entities={v['id']:v for v in doc['entities'] if v['kind'].startswith('processor.')}
        logical={int(v['identity']['kernel_cpu_index']):identity for identity,v in entities.items() if v['kind']=='processor.logical'}
        assert sorted(logical)==before['online'] and len(entities)==len(logical)+2
        rows=cpu_fields(doc);assert len(rows)==3*len(entities)
        fields={(v['entity_id'],v['field']):v for v in rows};assert len(fields)==len(rows)
        aggregate=(sum(v[0] for v in expected.values()),sum(v[1] for v in expected.values()))
        projection={logical[cpu]:ratio for cpu,ratio in expected.items()}
        projection.update({'processor:aggregate':aggregate,'processor:domain:linux-online':aggregate})
        stamp=int(rows[0]['measured_at']['nanoseconds']);interval=int(rows[0]['sample_interval_ns'])
        assert interval>0
        if previous_stamp is not None:assert stamp-previous_stamp==interval
        previous_stamp=stamp
        for entity,(busy,total) in projection.items():
            for field,wanted in zip(FIELDS,[float(Fraction(100*busy,total)),str(busy),str(total)]):
                row=fields[(entity,field)];assert row['acquisition']=='success' and row['freshness']=='current' and row['support']=='supported'
                assert row['generation']==doc['generation'] and row['sample_interval_ns']==str(interval) and row['measured_at']['nanoseconds']==str(stamp)
                assert row['value']['kind']==('number' if field==FIELDS[0] else 'uint64')
                if field==FIELDS[0]:assert math.isclose(row['value']['data'],wanted,rel_tol=4e-15,abs_tol=1e-12)
                else:assert row['value']['data']==wanted

def main():
    helper,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:]);build=helper.parent
    assert os.getuid()!=0 and evidence==build/'native-evidence' and json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    folder=evidence/('processor-publication-'+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700,parents=True)
    runtime=build.parent/('p-'+uuid.uuid4().hex[:8]);runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(family='PROCESSOR-PUBLICATION',evidence=str(folder))))
    nodes=[];record=dict(outcome='fail',helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),uid=os.getuid(),cases=[],runs=[])
    def save(): (folder/'result.json').write_bytes(encoded(record))
    def passed(name,**facts):record['cases'].append(dict(case=name,outcome='pass',**facts));save()
    def node(**files):
        n=Node(helper,runtime/str(len(nodes)),initial_files={'processor-record':'yes',**files});nodes.append(n)
        record['runs'].append(dict(pid=n.process.pid,epoch=n.epoch,root=str(n.folder),snapshots=n.snapshots));n.wait_ready();return n
    def pause(n,seconds):
        end=time.monotonic()+seconds
        while time.monotonic()<end:n.pump();time.sleep(.003)
    try:
        n=node();n.connect(features=FEATURES);pause(n,.25);assert not captures(n) and not n.snapshots;passed('NO-DEMAND');n.close()
        n=node();n.connect();n.subscribe();n.until(lambda:len(n.snapshots)>=2);assert not captures(n) and all(not cpu_fields(doc) for doc in documents(n));passed('NETWORK-ONLY');n.close()
        before=observation();n=node();n.connect(features=FEATURES);n.subscribe();n.until(lambda:len(unique_current(n))>=2,8);after=observation();raw=captures(n);docs=unique_current(n)
        verify(before,after,raw,docs);record['live']=dict(before=before,after=after,captures=raw,documents=docs);passed('LIVE',online_processors=len(before['online']))
        wrong=copy.deepcopy(docs);next(v for v in wrong[0]['observations'] if v['field']==FIELDS[1])['value']['data']='18446744073709551615'
        try:verify(before,after,raw,wrong)
        except AssertionError:passed('ORACLE-WRONG-DENOMINATOR')
        else:raise AssertionError('mutated denominator accepted')
        wrong=copy.deepcopy(docs);wrong[0]['entities']=[v for v in wrong[0]['entities'] if v['kind']!='processor.logical' or v['identity']['kernel_cpu_index']!='0']
        try:verify(before,after,raw,wrong)
        except AssertionError:passed('ORACLE-MISSING-CPU')
        else:raise AssertionError('missing logical CPU accepted')
        previous=cpu_fields(documents(n)[-1]);network_before=max(int(v['measured_at']['nanoseconds']) for doc in documents(n) for v in doc['observations'] if v['field']=='network.receive_bytes')
        (n.folder/'processor-mode').write_text('failure');n.until(lambda:any(cpu_fields(doc) and all(v['acquisition']=='failed' for v in cpu_fields(doc)) for doc in documents(n)),5)
        failed=next(cpu_fields(doc) for doc in reversed(documents(n)) if cpu_fields(doc) and all(v['acquisition']=='failed' for v in cpu_fields(doc)))
        for a,b in zip(previous,failed):
            for key in ('value','observed_at','measured_at','sample_interval_ns'):assert a[key]==b[key]
            assert b['freshness']=='stale' and b['error']['code']=='processor.failed'
        n.until(lambda:any(v['field']=='network.receive_bytes' and int(v['measured_at']['nanoseconds'])>network_before for doc in documents(n) for v in doc['observations']),3);passed('FAILURE-NETWORK-CONTINUES')
        marker=len(n.snapshots);(n.folder/'processor-mode').write_text('normal');n.until(lambda:any(cpu_fields(doc) and all(v['error'] and v['error']['code']=='processor.acquisition_gap' for v in cpu_fields(doc)) for doc in documents(n)[marker:]),4)
        n.until(lambda:len(unique_current(n))>=3,4);passed('GAP-RECOVERY')
        n.data.send(n.message('unsubscribe',dict(schema_version='0.2.0',subscription_id='S',clock_id='linux.boottime')));assert n.exit()==0;passed('UNSUBSCRIBE-STOP')
        n=node(**{'processor-policy':'deny'});n.connect(features=FEATURES);n.subscribe();n.until(lambda:bool(n.snapshots));assert not captures(n);rows=cpu_fields(documents(n)[-1]);assert len(rows)==6 and all(v['acquisition']=='disabled' and v['value'] is None for v in rows);passed('CPU-DENIED-NO-READ');n.close()
        n=node(**{'processor-network-policy':'deny'});n.connect(features=FEATURES);n.subscribe();n.until(lambda:bool(unique_current(n)),5);assert captures(n) and all(not any(v['kind']=='network.interface' for v in doc['entities']) for doc in documents(n));passed('CPU-INDEPENDENT-OF-NETWORK-DENIAL');n.close()
        n=node();n.connect(features=FEATURES);n.subscribe();n.until(lambda:bool(unique_current(n)),5);(n.folder/'processor-policy').write_text('deny');assert n.exit(timeout=3)==126;passed('CURRENT-POLICY-REVOKE')
        n=node(**{'processor-mode':'hold'});n.connect(features=FEATURES);n.subscribe();n.until(lambda:(n.folder/'processor-held').is_file(),3)
        n.data.send(n.message('unsubscribe',dict(schema_version='0.2.0',subscription_id='S',clock_id='linux.boottime')));start=time.monotonic();assert n.exit(timeout=3)==125;passed('UNCOOPERATIVE-STOP',elapsed_ms=(time.monotonic()-start)*1000)
        record['outcome']='pass'
    except BaseException:record['failure']=traceback.format_exc();raise
    finally:
        for n in nodes:
            record['runs'][nodes.index(n)]['captures']=captures(n);n.dispose()
        save();print(json.dumps(dict(outcome=record['outcome'],cases=len(record['cases']),record=str(folder/'result.json'))))

if __name__=='__main__':main()

"""Native receiver ownership and exact literal packets, without a GTK renderer."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def packet(generation,revision,ns):
    snapshot=dict(schema_version='0.2.0',producer_epoch='E1',generation=str(generation),captured_at='2026-10-06T00:00:01Z',entities=[],relationships=[],sources=[dict(id='provider:native-network',kind='native.network.counters',scope='host:local')],observations=[],completeness='complete')
    for index in range(1,65):
        entity=f'network:interface:{index}'
        snapshot['entities'].append(dict(id=entity,kind='network.interface',display_name=f'Network interface {index}',identity=dict(native_index=str(index),native_type='6'),generation=str(generation)))
        for field,unit,value in [('network.receive_bytes','byte','10'),('network.transmit_bytes','byte','7'),('network.receive_bytes_per_second','byte/second',None),('network.transmit_bytes_per_second','byte/second',None)]:
            available=value is not None
            snapshot['observations'].append(dict(schema_version='0.2.0',entity_id=entity,field=field,value=dict(kind='uint64',data=value) if available else None,unit=unit,origin='observed' if available else 'derived',support='supported',acquisition='success' if available else 'pending',freshness='current' if available else 'unknown',presence='present',source_id='provider:native-network',observed_at='2026-10-06T00:00:00Z' if available else None,attempted_at='2026-10-06T00:00:01Z',producer_epoch='E1',generation=str(generation),sample_interval_ns=None,error=None,measured_at=dict(clock_id='clock:1',nanoseconds=str(ns)) if available else None))
    return dict(type='snapshot',connection_id='D',producer_epoch='E1',body=dict(schema_version='0.2.0',subscription_id='S',producer_id='P1',record_id=f'sample:{generation}',policy_revision=str(revision),clock_id='clock:1',snapshot=snapshot))

exe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
folder=evidence/('gtk-history-producer-probe-'+uuid.uuid4().hex[:12]);folder.mkdir()
report=dict(started_at=datetime.now(timezone.utc).isoformat(),outcome='fail',scope='Native test producer/receiver ownership and literal complete packets; not GUI, desktop or release qualification',executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/gtk_history_producer.hpp')})
try:
    result=subprocess.run([str(exe),str(ROOT/'spec/fixtures/valid'),'PRODUCER-COLLECTOR'],capture_output=True,timeout=20)
    (folder/'stdout').write_bytes(result.stdout);(folder/'stderr').write_bytes(result.stderr)
    assert result.returncode==0,result.stderr;assert len(result.stdout)<=1024*1024
    value=json.loads(result.stdout)
    assert json.loads(value['first_wire'])==packet(1,7,0)
    assert json.loads(value['fresh_wire'])==packet(4099,9,21000000000)
    assert 0<value['first_receipt_ms']<=value['first_clock_ms']<=value['first_receipt_ms']+250 and value['fresh_clock_ns']==21000000000
    assert value['expired_clock_gap_ms']>250
    assert value['controls']==dict(busy_refused=True,old_mailbox_busy_refused=True,held_repeat_busy_refused=True,clock_gap_stale_refused=True,original_clock_lease=True,wrong_owner_refused=True,fresh_scope=True,held_close_accepted=0,invalid_accepted=1,invalid_stale_refused=True,accepted=2,receiver_owner=True,producer_stopped=True)
    report.update(outcome='pass',observed={k:v for k,v in value.items() if not k.endswith('_wire')},wire_sha256={k:sha(value[k].encode()) for k in ('first_wire','fresh_wire')},literal_entities=64,literal_observations=256)
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])

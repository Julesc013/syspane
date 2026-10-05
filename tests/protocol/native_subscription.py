"""Fixed external process oracles for the explicitly synthetic inventory stream."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid
from native_ipc import Process, Harness, events, native_identity

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    executable=Path(sys.argv[1]).resolve(); output=Path(sys.argv[2]).resolve()
    assert output.parent==executable.parent and output.name=='native-evidence'
    output.mkdir(exist_ok=True)
    report={'family':'NATIVE-SUB','outcome':'fail','executed_at':datetime.now(timezone.utc).isoformat(),
        'executable_sha256':sha(executable),'cases':[],
        'qualification':'Separate authenticated native processes exchange synthetic inventory only; no real collector, measured freshness, renderer, desktop or historical runtime qualification.',
        'source_inputs':{p.relative_to(ROOT).as_posix():sha(p) for directory in ('source','tests/protocol') for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}}
    for path in ('spec/fixtures/valid/snapshot.json','spec/delivery/packages/w-25-subscriptions.md'):
        report['source_inputs'][path]=sha(ROOT/path)
    try:
        for mode in ('journey','overflow','revoke','expiry','wrong-producer'):
            endpoint,owned=Harness(executable).endpoint(); processes=[]
            case={'case':'NATIVE-SUB.'+mode.upper(),'outcome':'fail'}; report['cases'].append(case); start=time.monotonic()
            try:
                server=Process([str(executable),'server',endpoint,mode,'0',str(ROOT/'spec/fixtures')]); processes.append(server)
                ready=server.event('ready'); assert ready['access_controls_verified'] and ready['unprivileged_context']
                client=Process([str(executable),'client',endpoint,mode,str(server.process.pid),str(ROOT/'spec/fixtures')]); processes.append(client)
                assert client.finish(15)==0 and server.finish(15)==0
                if mode!='journey': native_identity(server,client)
                else:
                    assert len(events(client,'authenticated'))==len(events(server,'authenticated'))==2
                    assert all(r['peer_pid']==server.process.pid and r['user_session_verified'] for r in events(client,'authenticated'))
                    assert all(r['peer_pid']==client.process.pid and r['user_session_verified'] for r in events(server,'authenticated'))
                imported=events(client,'imported')
                expected={'journey':['1','2','3','3','4'],'overflow':['18'],'revoke':['1'],'expiry':['1'],'wrong-producer':[]}[mode]
                assert [r['generation'] for r in imported]==expected
                assert all(r['payload'] and r['value']=='inventory-'+r['generation'] and not r['retained'] and not r['measured_tick'] for r in imported)
                closed=events(server,'closed'); assert len(closed)==(2 if mode=='journey' else 1) and all(r['demand']==0 for r in closed)
                reason={'expiry':'subscription.expired','wrong-producer':'telemetry.binding'}.get(mode,'peer.shutdown')
                assert all(r['reason']==reason for r in closed)
                if mode=='expiry':
                    assert 3000<=closed[0]['elapsed_ms']<6000 and events(client,'expired')[0]['retained']
                if mode=='revoke': assert events(client,'revoked')==[{'event':'revoked','payload':False}]
                if mode=='wrong-producer': assert events(client,'rejected')==[{'event':'rejected','payload':False}] and not events(server,'demand')
                payloads=[r['message'] for r in events(client,'reply')]
                if mode in ('overflow','revoke'):
                    gaps=[r for r in payloads if r['type']=='gap']; assert len(gaps)==1
                    assert gaps[0]['body']['reason']==('queue_overflow' if mode=='overflow' else 'policy_changed')
                if mode=='revoke': assert [r['type'] for r in payloads]==['welcome','snapshot','gap']
                case['outcome']='pass'
            except Exception as error:
                case['failure']=str(error); raise
            finally:
                for process in processes: process.stop()
                case['processes']=[process.record() for process in processes]; case['elapsed_seconds']=round(time.monotonic()-start,3)
                if owned is not None:
                    if list(owned.iterdir()): case['remaining_runtime_directory']=str(owned); raise AssertionError('owned socket cleanup failed')
                    owned.rmdir()
                print(case['case']+': '+case['outcome'],flush=True)
        report['outcome']='pass'
    finally:
        path=output/('NATIVE-SUB-'+uuid.uuid4().hex[:12]+'.json')
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n'); print('Native evidence: '+str(path),flush=True)
if __name__=='__main__':main()

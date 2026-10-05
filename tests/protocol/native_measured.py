"""Fixed external oracles for measured delivery; sender timestamps are immutable."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import uuid
from native_ipc import Process, Harness, events, native_identity

ROOT = Path(__file__).resolve().parents[2]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    executable, output = (Path(argument).resolve() for argument in sys.argv[1:3])
    assert output.parent == executable.parent and output.name == 'native-evidence'
    output.mkdir(exist_ok=True)
    report = {'family': 'NATIVE-MEASURED', 'outcome': 'fail', 'executed_at': datetime.now(timezone.utc).isoformat(),
        'executable_sha256': sha(executable), 'cases': [],
        'qualification': 'Synthetic measured values across authenticated native processes; no real collector, suspend, namespace migration, renderer or desktop qualification.',
        'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for directory in ('source', 'tests/protocol', 'tests/fault')
                          for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}}
    for path in ('spec/fixtures/valid/snapshot.json', 'spec/delivery/packages/w-25-measured-time.md'):
        report['source_inputs'][path] = sha(ROOT/path)
    domain = 'windows.interrupt-precise' if platform.system() == 'Windows' else 'linux.boottime'
    try:
        for mode in ('fresh', 'delayed', 'future'):
            endpoint, owned = Harness(executable).endpoint()
            processes = []
            case = {'case': 'NATIVE-MEASURED.'+mode.upper(), 'outcome': 'fail'}
            report['cases'].append(case)
            started = time.monotonic()
            try:
                server = Process([str(executable), 'server', endpoint, 'measured-'+mode, '0', str(ROOT/'spec/fixtures')])
                processes.append(server)
                ready = server.event('ready')
                assert ready['access_controls_verified'] and ready['unprivileged_context']
                client = Process([str(executable), 'client', endpoint, 'measured-'+mode, str(server.process.pid), str(ROOT/'spec/fixtures')])
                processes.append(client)
                assert client.finish(15) == 0 and server.finish(15) == 0
                native_identity(server, client)
                producer = events(server, 'producer_measurement')
                assert len(producer) == 1 and producer[0]['clock_id'] == domain
                produced = producer[0]
                assert int(produced['stamp'])-int(produced['sampled']) == (60_000_000_000 if mode == 'future' else 0)
                replies = [row['message'] for row in events(client, 'reply')]
                assert [row['type'] for row in replies] == ['welcome', 'snapshot']
                assert 'telemetry.measured-time' in replies[0]['body']['optional_features']
                body = replies[1]['body']
                assert body['schema_version'] == body['snapshot']['schema_version'] == '0.2.0' and body['clock_id'] == domain
                observation = body['snapshot']['observations'][0]
                assert observation['schema_version'] == '0.2.0'
                assert observation['measured_at'] == {'clock_id': domain, 'nanoseconds': produced['stamp']}
                imported, projections = events(client, 'imported'), events(client, 'measurement')
                if mode == 'future':
                    assert not imported and not projections
                    assert events(client, 'measurement_rejected') == [{'event': 'measurement_rejected', 'payload': False, 'alive': False}]
                else:
                    assert imported == [{'event': 'imported', 'generation': '1', 'payload': True, 'value': 'inventory-1', 'retained': False, 'measured_tick': True}]
                    assert len(projections) == 1
                    view = projections[0]
                    assert view['clock_id'] == domain and view['scope'] and view['stamp'] == produced['stamp']
                    age = int(view['now'])-int(view['stamp'])
                    ttl = 1_000_000_000 if mode == 'fresh' else 100_000_000
                    assert int(view['ttl']) == ttl and age >= 0
                    assert view['current'] == (mode == 'fresh') == (age < ttl)
                    case.update(age_nanoseconds=str(age), ttl_nanoseconds=str(ttl))
                closed = events(server, 'closed')
                assert len(closed) == 1 and closed[0]['demand'] == 0 and closed[0]['reason'] == 'peer.shutdown'
                assert not events(client, 'error') and not events(server, 'error')
                case['outcome'] = 'pass'
            except Exception as error:
                case['failure'] = str(error)
                raise
            finally:
                for process in processes: process.stop()
                case['processes'] = [process.record() for process in processes]
                case['elapsed_seconds'] = round(time.monotonic()-started, 3)
                if owned is not None:
                    if list(owned.iterdir()):
                        case['remaining_runtime_directory'] = str(owned)
                        raise AssertionError('owned socket cleanup failed')
                    owned.rmdir()
                print(case['case']+': '+case['outcome'], flush=True)
        report['outcome'] = 'pass'
    finally:
        path = output/('NATIVE-MEASURED-'+uuid.uuid4().hex[:12]+'.json')
        path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        print('Native evidence: '+str(path), flush=True)
if __name__ == '__main__': main()

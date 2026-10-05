"""Independent causal-bracket/peer-exit oracles; no measurement wire fields."""
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

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    executable = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    assert output.parent == executable.parent and output.name == 'native-evidence'
    output.mkdir(exist_ok=True)
    report = {'family': 'NATIVE-CLOCK', 'outcome': 'fail', 'executed_at': datetime.now(timezone.utc).isoformat(),
        'executable_sha256': sha(executable), 'cases': [],
        'qualification': 'Authenticated local process clock bracket and held-peer exit only; no measured telemetry, suspend/resume or namespace mismatch qualification.',
        'limitations': ['Native suspend/resume, namespace mismatch/change or denial, count overflow and regression were not induced.',
                       'API representation units do not establish clock accuracy, hardware resolution or real-time latency.',
                       'Existing 0.1 inventory documents still have no measured tick; no collector, freshness, rate, renderer or desktop qualification.'],
        'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for directory in ('source', 'tests/protocol')
                          for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}}
    for path in ('spec/fixtures/valid/snapshot.json', 'spec/delivery/packages/w-25-measurement-clock.md'):
        report['source_inputs'][path] = sha(ROOT/path)
    expected_domain, expected_unit = ('windows.interrupt-precise', 100) if platform.system() == 'Windows' else ('linux.boottime', 1)
    try:
        for mode in ('roundtrip', 'peer-exit'):
            endpoint, owned = Harness(executable).endpoint()
            processes = []
            case = {'case': 'NATIVE-CLOCK.'+mode.upper(), 'outcome': 'fail'}
            report['cases'].append(case)
            start = time.monotonic()
            try:
                server = Process([str(executable), 'server', endpoint, 'clock-'+mode, '0', str(ROOT/'spec/fixtures')])
                processes.append(server)
                ready = server.event('ready')
                assert ready['access_controls_verified'] and ready['unprivileged_context']
                client = Process([str(executable), 'client', endpoint, 'clock-'+mode, str(server.process.pid), str(ROOT/'spec/fixtures')])
                processes.append(client)
                assert client.finish(15) == 0 and server.finish(15) == 0
                native_identity(server, client)
                client_ticks, server_ticks = events(client, 'clock'), events(server, 'clock')
                assert [row['phase'] for row in client_ticks] == ['before', 'after']
                assert [row['phase'] for row in server_ticks] == ['middle']
                ordered = [client_ticks[0], server_ticks[0], client_ticks[1]]
                assert all(row['clock_id'] == expected_domain and row['representation_unit_ns'] == expected_unit for row in ordered)
                assert all(row['nanoseconds'].isascii() and row['nanoseconds'].isdecimal() for row in ordered)
                ticks = [int(row['nanoseconds']) for row in ordered]
                assert all(0 <= tick <= 2**64-1 and tick % expected_unit == 0 for tick in ticks)
                assert ticks[0] <= ticks[1] <= ticks[2], 'native causal bracket violated'
                imported = events(client, 'imported')
                assert imported == [{'event': 'imported', 'payload': True, 'generation': '1',
                                     'value': 'inventory-1', 'retained': False, 'measured_tick': False}]
                closed = events(server, 'closed')
                assert len(closed) == 1 and closed[0]['demand'] == 0 and closed[0]['reason'] == 'peer.shutdown'
                rejected = events(server, 'clock_rejected')
                assert [row['code'] for row in rejected] == (['clock.peer_exited', 'clock.unavailable'] if mode == 'peer-exit' else [])
                assert all(row['peer_pid'] == client.process.pid for row in rejected)
                assert not events(client, 'clock_rejected') and not events(server, 'error') and not events(client, 'error')
                case.update(outcome='pass', clock_id=expected_domain, representation_unit_ns=expected_unit,
                            bracket_nanoseconds=[str(tick) for tick in ticks], roundtrip_nanoseconds=str(ticks[2]-ticks[0]))
            except Exception as error:
                case['failure'] = str(error)
                raise
            finally:
                for process in processes:
                    process.stop()
                case['processes'] = [process.record() for process in processes]
                case['elapsed_seconds'] = round(time.monotonic()-start, 3)
                if owned is not None:
                    if list(owned.iterdir()):
                        case['remaining_runtime_directory'] = str(owned)
                        raise AssertionError('owned socket cleanup failed')
                    owned.rmdir()
                print(case['case']+': '+case['outcome'], flush=True)
        report['outcome'] = 'pass'
    finally:
        path = output/('NATIVE-CLOCK-'+uuid.uuid4().hex[:12]+'.json')
        path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        print('Native evidence: '+str(path), flush=True)

if __name__ == '__main__':
    main()

"""Fixed native fault cases with independent OS child-exit observations."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import select
import stat
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/protocol'))
from native_ipc import Process, events


class ObservedChild:
    def __init__(self, pid):
        self.pid = pid
        self.closed = False
        if os.name == 'nt':
            self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            self.kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
            self.kernel.OpenProcess.restype = ctypes.c_void_p
            self.kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            self.kernel.WaitForSingleObject.restype = ctypes.c_ulong
            self.kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            self.handle = self.kernel.OpenProcess(0x00100000, False, pid)
            assert self.handle, 'could not hold launched child identity'
        else:
            self.handle = os.pidfd_open(pid, 0)
            self.poller = select.poll()
            self.poller.register(self.handle, select.POLLIN)
        if self.exited(0):
            self.close()
            raise AssertionError('child exited before independent observation')

    def exited(self, milliseconds):
        if os.name == 'nt':
            result = self.kernel.WaitForSingleObject(self.handle, milliseconds)
            assert result in (0, 258), 'independent native wait failed'
            return result == 0
        return bool(self.poller.poll(milliseconds))

    def close(self):
        if not self.closed:
            if os.name == 'nt':
                self.kernel.CloseHandle(self.handle)
            else:
                os.close(self.handle)
            self.closed = True


def endpoint():
    tag = uuid.uuid4().hex
    if os.name == 'nt':
        return '\\\\.\\pipe\\SysPane.Dev.'+tag, None
    root = Path.home()/'.cache/syspane/recovery-w25'
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = root.lstat()
    assert stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and stat.S_IMODE(info.st_mode) == 0o700
    assert root.resolve() == root
    owned = root/('c-'+tag[:10])
    owned.mkdir(mode=0o700)
    return str(owned/'s'), owned


def verify(process, case, observations):
    rows = process.lines
    assert not events(process, 'error'), rows
    assert events(process, 'ready')[0]['unprivileged'] and events(process, 'ready')[0]['endpoint_controls']
    spawned, stopped = events(process, 'spawned'), events(process, 'stopped')
    authenticated = events(process, 'authenticated')
    for item in authenticated:
        assert item['peer_pid'] == item['pid'] and item['pid'] in observations
    if case == 'PARENT-LOSS':
        assert len(spawned) == 1 and len(authenticated) == 1
        return
    assert process.process.returncode == 0, rows
    assert len(spawned) == len(stopped) and all(item['os_confirmed'] for item in stopped)
    assert [item['pid'] for item in spawned] == [item['pid'] for item in stopped]
    # Holding identities means this assertion does not confuse PID reuse with exit.
    assert all(child.exited(0) for child in observations.values())
    for before, after in zip(stopped, spawned[1:]):
        assert rows.index(before) < rows.index(after), 'replacement announced before confirmed stop'
    faults = events(process, 'fault')
    for fault, replacement in zip(faults, spawned[1:]):
        assert replacement['observed_ms'] - fault['observed_ms'] >= fault['backoff_ms'], 'replacement bypassed backoff'
    if case == 'CHILD-GRACEFUL':
        assert len(spawned) == 1 and not faults
        assert len(events(process, 'heartbeat')) >= 3 and len(events(process, 'progress')) >= 2
        assert stopped[0]['code'] == 0 and not stopped[0]['forced']
    elif case in ('PRODUCER-HANG', 'RENDER-STALL'):
        assert len(spawned) == 2 and len(faults) == 1
        fault = faults[0]
        assert fault['alive'] is True
        field = 'since_heartbeat_ms' if case == 'PRODUCER-HANG' else 'since_challenge_ms'
        assert 3000 <= fault[field] <= 4000, fault
        assert fault['reason'] == ('producer.expired' if case == 'PRODUCER-HANG' else 'render.stalled')
        assert fault['backoff_ms'] == 1000
        if case == 'RENDER-STALL':
            assert fault['heartbeats'] >= 3 and fault['completions'] == 0
        else:
            assert fault['heartbeats'] == 2 and stopped[0]['forced'] is True
        assert stopped[1]['code'] == 0 and not stopped[1]['forced']
        assert events(process, 'complete')[0]['launches'] == 2
    elif case == 'CRASH-CIRCUIT':
        assert len(spawned) == 4 and len(faults) == 4
        assert all(item['code'] == 73 and not item['forced'] for item in stopped)
        assert [item['backoff_ms'] for item in faults] == [1000, 2000, 4000, 4000]
        assert events(process, 'circuit_open')[0]['launches'] == 4
        assert events(process, 'circuit_open')[0]['observed_ms_after_open'] >= 500
    elif case == 'QUARANTINE':
        assert len(spawned) == 2 and len(faults) == 1
        held = events(process, 'quarantined')
        assert len(held) == 1 and held[0]['child_alive'] and held[0]['start_denied'] and held[0]['reset_denied']
        assert held[0]['elapsed_ms'] >= 250
        assert stopped[-1]['code'] == 0
    elif case in ('ROLE-DENIAL', 'WRONG-EPOCH'):
        assert len(spawned) == 1 and len(faults) == 1 and not events(process, 'heartbeat') and not events(process, 'progress')
        rejected = events(process, 'rejected')[0]
        assert rejected['heartbeats'] == 0
        assert rejected['reason'] == ('handshake.role_denied' if case == 'ROLE-DENIAL' else 'health.identity')
    elif case == 'PROGRESS-DENIAL':
        assert len(spawned) == 1 and len(faults) == 1 and not events(process, 'progress')
        assert len(events(process, 'challenge')) == 1
        assert events(process, 'rejected')[0]['reason'] == 'health.progress_order'
    else:
        raise AssertionError('unknown oracle')


def scenario(executable, case, mode, evidence):
    address, owned = endpoint()
    journal = evidence/('failure-'+case+'-'+uuid.uuid4().hex[:12]+'.jsonl')
    command = [str(executable), 'supervisor', address, mode, str(journal)]
    process = Process(command)
    observers = {}
    record = {'case': 'RECOVERY-01.'+case, 'outcome': 'fail', 'command': command, 'child_observations': []}
    start = time.monotonic()
    try:
        while time.monotonic() - start < 45:
            try:
                item = process.events.get(timeout=.05)
                if item['event'] == 'spawned':
                    observers[item['pid']] = ObservedChild(item['pid'])
                    record['child_observations'].append({'pid': item['pid'], 'observed_alive': True})
                elif item['event'] == 'stopped':
                    assert observers[item['pid']].exited(1000), 'stop report preceded OS-observed exit'
                elif item['event'] == 'authenticated' and case == 'PARENT-LOSS':
                    assert item['pid'] in observers
                    killed = time.monotonic()
                    process.process.kill()  # Exact supervisor launched by this harness.
                    assert observers[item['pid']].exited(3000), 'parent death left child alive'
                    record['parent_loss_exit_ms'] = round((time.monotonic()-killed)*1000)
                    break
            except queue.Empty:
                if process.process.poll() is not None and not process.reader.is_alive():
                    break
        process.finish(timeout=3)
        verify(process, case, observers)
        raw = journal.read_bytes()
        assert raw.startswith(b'SYSPANE-FAILURES 0.1\n') and len(raw) <= 8192
        metadata = [json.loads(line) for line in raw.splitlines()[1:]]
        faults = events(process, 'fault')
        assert len(metadata) == len(faults) and all(row['stored'] for row in events(process, 'failure_recorded'))
        for fault, recorded in zip(faults, events(process, 'failure_recorded')):
            stopped = next(row for row in events(process, 'stopped') if row['pid'] == fault['pid'])
            assert process.lines.index(stopped) < process.lines.index(recorded), 'optional journal write preceded confirmed child cleanup'
        expected_reason = {'PRODUCER-HANG': 'producer_expired', 'RENDER-STALL': 'render_stalled', 'CRASH-CIRCUIT': 'crashed',
                           'QUARANTINE': 'operation_timeout', 'ROLE-DENIAL': 'protocol_rejected', 'WRONG-EPOCH': 'protocol_rejected', 'PROGRESS-DENIAL': 'protocol_rejected'}
        expected_role = 'desktop' if case in ('CHILD-GRACEFUL', 'RENDER-STALL', 'PROGRESS-DENIAL') else 'collector'
        for i, (row, fault) in enumerate(zip(metadata, faults)):
            assert set(row) == {'sequence', 'elapsed_ms', 'role', 'reason', 'stop_confirmed'}
            assert row['sequence'] == str(i+1) and row['role'] == expected_role and row['reason'] == expected_reason[case]
            assert row['stop_confirmed'] == (not fault['alive']) and 0 <= int(row['elapsed_ms']) <= 40000
        record['failure_metadata'] = {'record': journal.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'text': raw.decode('utf-8')}
        record['outcome'] = 'pass'
    except Exception as error:
        record['failure'] = str(error)
    finally:
        process.stop()
        for child in observers.values():
            ended = child.exited(3000)
            record['child_observations'][list(observers).index(child.pid)]['observed_exited'] = ended
            if not ended:
                record['outcome'] = 'fail'; record['failure'] = 'owned child remained alive after supervisor cleanup'
            child.close()
        record['process'] = process.record()
        record['elapsed_seconds'] = round(time.monotonic()-start, 3)
        if owned is not None:
            entries = list(owned.iterdir())
            # Parent-loss intentionally skips C++ listener cleanup. Delete only the
            # exact owned socket entry in this private case directory, never a tree.
            if case == 'PARENT-LOSS' and entries == [owned/'s']:
                info = entries[0].lstat()
                if stat.S_ISSOCK(info.st_mode) and info.st_uid == os.geteuid(): entries[0].unlink()
            if list(owned.iterdir()):
                record['outcome'] = 'fail'; record['failure'] = 'unexpected runtime entry preserved'
            else:
                owned.rmdir()
        print(json.dumps({'case': record['case'], 'outcome': record['outcome'], 'elapsed_seconds': record['elapsed_seconds']}), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    report = {'family': 'RECOVERY-01', 'outcome': 'fail', 'started_at': datetime.now(timezone.utc).isoformat(),
              'executable_sha256': hashlib.sha256(args.executable.read_bytes()).hexdigest(), 'cases': [],
              'qualification': 'Native synthetic child/health supervision only; no pixels, diagnostic entry, policy erasure or desktop support.'}
    inputs = ['source/application/recovery_probe.cpp', 'source/platform/child.hpp', 'source/platform/child_linux.cpp',
              'source/platform/child_windows.cpp', 'source/diagnostics/health_link.hpp', 'source/diagnostics/health_link.cpp',
              'source/protocol/wire.cpp', 'tests/fault/native_recovery.py', 'spec/delivery/packages/w-25-recovery.md']
    inputs += ['source/platform/failure_store.cpp', 'source/platform/failure_store.hpp', 'source/diagnostics/failure_history.cpp',
               'source/diagnostics/failure_history.hpp', 'spec/delivery/packages/w-25-failure-metadata.md']
    report['source_inputs'] = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    try:
        for case, mode in [('CHILD-GRACEFUL','graceful'), ('PRODUCER-HANG','producer-hang'), ('RENDER-STALL','render-stall'),
                           ('CRASH-CIRCUIT','crash-circuit'), ('QUARANTINE','quarantine'), ('PARENT-LOSS','parent-loss'),
                           ('ROLE-DENIAL','role-denial'), ('WRONG-EPOCH','wrong-epoch'), ('PROGRESS-DENIAL','progress-denial')]:
            args.evidence.mkdir(parents=True, exist_ok=True)
            report['cases'].append(scenario(args.executable.resolve(), case, mode, args.evidence.resolve()))
        if all(case['outcome'] == 'pass' for case in report['cases']): report['outcome'] = 'pass'
    except Exception as error:
        report['harness_error'] = str(error)
    args.evidence.mkdir(parents=True, exist_ok=True)
    destination = args.evidence/('RECOVERY-01-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.json')
    with destination.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(report, handle, indent=2); handle.write('\n')
    print('Native evidence: '+str(destination.resolve()), flush=True)
    return 0 if report['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

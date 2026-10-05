"""Exercise private native metadata files in one owned directory; retain every attempt."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]


def main():
    executable, evidence = (Path(p).resolve(strict=True) for p in sys.argv[1:3])
    if evidence.name != 'native-evidence' or evidence.parent != executable.parent or not (evidence.parent/'.syspane-owner.json').is_file():
        raise ValueError('owned build evidence directory required')
    token = uuid.uuid4().hex[:12]
    workspace = evidence/('failure-store-'+token)
    workspace.mkdir(mode=0o700)
    (workspace/'.syspane-owner.json').write_text('{"owner":"W-25 failure metadata"}\n', encoding='utf-8')
    report = {'family': 'FAILURE-STORE', 'outcome': 'fail', 'started_at': datetime.now(timezone.utc).isoformat(),
              'qualification': 'Native private advisory metadata files only; no product retention, protected policy or historical OS qualification.',
              'executable_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(), 'cases': [], 'attempts': [],
              'limitations': ['Owned synthetic files only; no protected machine policy or user configuration was opened or changed.',
                             'No power-loss durability, hostile same-user parent replacement or historical OS qualification.']}
    paths = ['source/platform/failure_store.cpp', 'source/platform/failure_store.hpp', 'source/diagnostics/failure_history.cpp',
             'source/diagnostics/failure_history.hpp', 'tests/fault/failure_store_tests.cpp', 'tests/fault/native_failure_store.py',
             'spec/delivery/packages/w-25-failure-metadata.md']
    report['source_inputs'] = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}

    def run(mode, path, code=0):
        command = [str(executable), mode, str(path)]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=5,
                                **({'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}))
        report['attempts'].append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        assert result.returncode == code and not result.stderr, report['attempts'][-1]
        return json.loads(result.stdout) if mode == 'read' else None

    def passed(name):
        report['cases'].append({'case': 'FAILURE-STORE.'+name, 'outcome': 'pass'})

    try:
        path = workspace/'failures-λ.jsonl'
        run('create', path)
        before = path.read_bytes()
        expected = [
            {'sequence': '1', 'elapsed_ms': '100', 'role': 'collector', 'reason': 'producer_expired', 'stop_confirmed': False},
            {'sequence': '2', 'elapsed_ms': '200', 'role': 'desktop', 'reason': 'render_stalled', 'stop_confirmed': True}]
        value = run('read', path)
        assert value == {'status': 'complete', 'trust': 'unverified_local_metadata', 'live_health': False, 'records': expected}
        assert before.startswith(b'SYSPANE-FAILURES 0.1\n') and b'\r' not in before
        passed('ROUNDTRIP-UNICODE')
        run('create', path, 73)
        assert path.read_bytes() == before
        passed('EXCLUSIVE')
        run('limit', workspace/'limit.jsonl')
        assert len(run('read', workspace/'limit.jsonl')['records']) == 16
        passed('CAPACITY')
        run('regression', workspace/'regression.jsonl')
        assert len(run('read', workspace/'regression.jsonl')['records']) == 1
        passed('REGRESSION-LATCH')
        run('live-read', workspace/'live.jsonl')
        passed('OPEN-WRITER-READ')
        path.write_bytes(before[:-7])
        value = run('read', path)
        assert value['status'] == 'incomplete' and value['records'] == expected[:1]
        path.write_bytes(before+b'{bad}\n')
        assert run('read', path)['status'] == 'invalid'
        passed('INTERRUPTED-INVALID')
        path.write_bytes(b'x'*8193)
        assert run('read', path)['status'] == 'unavailable'
        path.write_bytes(before)
        passed('OVERSIZE')
        link = workspace/'hardlink.jsonl'
        os.link(path, link)
        assert run('read', path)['status'] == run('read', link)['status'] == 'unavailable'
        passed('HARDLINK')
        assert run('read', workspace/'absent.jsonl')['status'] == 'absent'
        assert run('read', 'relative.jsonl')['status'] == 'unavailable'
        assert run('read', workspace)['status'] == 'unavailable'
        run('create', 'relative.jsonl', 73)
        passed('PATH-TYPE')
        if os.name != 'nt':
            private = workspace/'live.jsonl'
            assert private.stat().st_mode & 0o777 == 0o600
            private.chmod(0o644)
            assert run('read', private)['status'] == 'unavailable'
            private.chmod(0o600)
            symlink = workspace/'symlink.jsonl'
            symlink.symlink_to(private)
            assert run('read', symlink)['status'] == 'unavailable'
            run('create', symlink, 73)
            fifo = workspace/'fifo'
            os.mkfifo(fifo, 0o600)
            assert run('read', fifo)['status'] == 'unavailable'
            passed('POSIX-PERMISSIONS-LINK-FIFO')
        else:
            private = workspace/'live.jsonl'
            tool = Path(os.environ['SystemRoot'])/'System32/icacls.exe'
            command = [str(tool), str(private), '/grant', '*S-1-1-0:(R)']
            changed = subprocess.run(command, capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
            report['attempts'].append({'command': command, 'exit': changed.returncode, 'tool_sha256': hashlib.sha256(tool.read_bytes()).hexdigest(),
                                       'stdout': changed.stdout.decode(errors='replace'), 'stderr': changed.stderr.decode(errors='replace')})
            assert changed.returncode == 0 and run('read', private)['status'] == 'unavailable'
            passed('WINDOWS-PRIVATE-DACL')
            try:
                (workspace/'symlink.jsonl').symlink_to(private)
            except OSError as error:
                if error.winerror != 1314: raise
                report['limitations'].append('Windows symlink creation requires an unavailable privilege; reparse rejection case not executed.')
            else:
                assert run('read', workspace/'symlink.jsonl')['status'] == 'unavailable'
                run('create', workspace/'symlink.jsonl', 73)
                passed('WINDOWS-REPARSE')
        report['outcome'] = 'pass'
    except Exception as error:
        report['failure'] = type(error).__name__+': '+str(error)
    report['fixture_files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                               for p in workspace.iterdir() if p.is_file() and not p.is_symlink()}
    destination = evidence/('FAILURE-STORE-'+token+'.json')
    with destination.open('x', encoding='utf-8', newline='\n') as file:
        json.dump(report, file, indent=2); file.write('\n')
    print('Native evidence: '+str(destination))
    return 0 if report['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

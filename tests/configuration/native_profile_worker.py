"""Independent ext4/thread/process oracle for the real profile/command composition."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import os
import select
import signal
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/profile-worker-cases.json').read_bytes())
INITIAL = json.loads((ROOT/'tests/configuration/profile-startup-cases.json').read_bytes())
COMMAND = json.loads((ROOT/'tests/configuration/profile-startup-command-case.json').read_bytes())['command']
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    exe, startup, evidence = [Path(v).resolve() for v in sys.argv[1:4]]
    assert os.geteuid() != 0 and evidence.is_relative_to(exe.parent)
    folder = evidence/('profile-worker-'+uuid.uuid4().hex[:12])
    folder.mkdir(parents=True, mode=0o700)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    report = dict(family='PROFILE-WORKER', outcome='fail', uid=os.geteuid(), filesystem='ext4', kernel=list(os.uname()),
                  started_at=datetime.now(timezone.utc).isoformat(), artifacts={p.name: sha(p.read_bytes()) for p in (exe, startup)},
                  oracle_sha256=sha(Path(__file__).read_bytes()), cases=[], observations=[])

    def save():
        (folder/'result.json').write_bytes(encoded(report))

    def passed(name, **facts):
        assert name in CASES['cases'] and name not in [v['case'] for v in report['cases']]
        report['cases'].append(dict(case=name, outcome='pass', **facts)); save()

    def config(name, **extra):
        return dict(profile=CASES['profile'], root=str(folder/name), **extra)

    def args(v):
        p = folder/('input-'+uuid.uuid4().hex[:10]+'.json'); p.write_bytes(encoded(v)); p.chmod(0o600)
        return [str(exe), str(p)]

    def line(q):
        assert select.select([q.stdout], [], [], 5)[0], 'native observation timeout'
        raw = q.stdout.readline(); assert raw, 'native EOF'
        value = json.loads(raw); report['observations'].append(dict(pid=q.pid, value=value)); return value

    def send(q, op, **values):
        q.stdin.write(encoded(dict(op=op, **values))+b'\n'); q.stdin.flush(); return line(q)

    @contextmanager
    def held(v):
        q = subprocess.Popen(args(v), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        try:
            ready = line(q); assert ready['event'] == 'ready', ready
            yield q, ready
        finally:
            if q.poll() is None:
                try:
                    q.stdin.write(b'{"op":"exit"}\n'); q.stdin.flush(); q.wait(timeout=3)
                except (BrokenPipeError, subprocess.TimeoutExpired):
                    q.kill(); q.wait(timeout=3)
            (folder/('stderr-'+str(q.pid))).write_bytes(q.stderr.read())
            q.stdin.close(); q.stdout.close(); q.stderr.close()

    def tasks(q):
        return {int(p.name) for p in Path('/proc', str(q.pid), 'task').iterdir()}

    def body(index=0):
        v = copy.deepcopy(COMMAND); row = CASES['commands'][index]
        v['request_id'] = row['request_id']; v['expected_revision'] = row['expected_revision']
        v['operations'][0]['value'] = row['resources_ms']; return encoded(v).decode()

    def begin(q, ready, **values):
        started = send(q, 'start', **values); assert started['event'] == 'started', started
        executing = line(q); assert executing['event'] == 'executing'
        if values.get('hold', '-') != '-' or values.get('hold_exit'):
            event = line(q); assert event['event'] == 'held'
            assert {q.pid, ready['storage_tid'], executing['tid']} == tasks(q)
            assert len(tasks(q)) == 3
            assert event['tid'] == (executing['tid'] if event['phase'] == 'exit' else ready['storage_tid'])
        return executing['tid']

    def finish(q):
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            answer = send(q, 'finish')
            if not answer.get('pending'):
                assert not answer['wrong_thread'] and answer['joined_tid'] not in tasks(q)
                return answer
            time.sleep(.01)
        raise AssertionError('owned command worker did not finish')

    def store_root(v):
        return Path(v['root'])/'syspane/configuration'/sha(v['profile'].encode())/'generations'

    def inspect(v, revision='0', resources_ms=None):
        root = store_root(v); selector = json.loads((root/'current.json').read_bytes()); generation = root/selector['generation']
        raw = (generation/'manifest.json').read_bytes(); assert sha(raw) == selector['manifest']; manifest = json.loads(raw)
        expected = copy.deepcopy(INITIAL['documents']); expected['settings']['revision'] = expected['scene']['revision'] = revision
        if resources_ms is not None: expected['settings']['sampling']['resources_ms'] = resources_ms
        for name in ('settings', 'scene'):
            raw = (generation/(name+'.json')).read_bytes(); assert raw == encoded(expected[name]), (name, revision)
            assert sha(raw) == manifest[name]
        assert manifest['revision'] == revision
        raw = (generation/'resources.json').read_bytes(); assert sha(raw) == manifest['resources']; index = json.loads(raw)
        packages = {sha(p['manifest'].encode()): p for p in INITIAL['packages']}
        assert index == dict(version='0.1.0', selection=INITIAL['selection'], theme=INITIAL['theme_pin'], packages=sorted(packages))
        for key, package in packages.items():
            assert (generation/'resources'/('m-'+key+'.json')).read_bytes() == package['manifest'].encode()
            for asset in package['assets'].values():
                assert (generation/'resources'/('a-'+sha(asset.encode())+'.bin')).read_bytes() == asset.encode()
        if revision == '0':
            assert manifest['version'] == '0.5.0' and manifest['identity'] is None
        else:
            assert manifest['version'] == '0.3.0'
            command_index = int(revision)-1
            assert (generation/'request.json').read_bytes() == body(command_index).encode()
        return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}

    def competitor(v, good=False):
        command = args(v); q = subprocess.run([str(startup), command[1], 'open', '-', '-'], capture_output=True, timeout=5)
        result = json.loads(q.stdout)
        assert (q.returncode == 0) == good, result
        if not good: assert result['error'] == 'profile.busy'
        return result

    try:
        v = config('basic')
        with held(v) as (q, ready):
            assert ready['caller_tid'] == q.pid and ready['storage_tid'] != q.pid
            assert tasks(q) == {q.pid, ready['storage_tid']}
            assert ready['snapshot']['settings'] == INITIAL['documents']['settings']; inspect(v)
            passed('cold-start-thread-and-bytes', pid=q.pid, storage_tid=ready['storage_tid'])
            competitor(v)
            begin(q, ready, body=body(), hold_exit=True)
            inspect(v, '1', 1500)
            pending = send(q, 'query'); assert pending['outcome'] == 'unknown' and pending['error']['code'] == CASES['expected']['pending_code']
            assert pending['stored'] is None and send(q, 'finish') == {'pending': True}
            assert send(q, 'release-exit')['released']; first = finish(q)
            assert first['result']['outcome'] == 'accepted' and first['result']['revision'] == '1'
            passed('completion-before-exit-remains-pending')
            competitor(v); assert tasks(q) == {q.pid, ready['storage_tid']}
            passed('locks-held-between-commands')
            begin(q, ready, body=body(1)); second = finish(q)
            assert second['result']['outcome'] == 'accepted' and second['result']['revision'] == '2'
            before = inspect(v, '2', 2000)
            assert len(list(store_root(v).glob('g-*'))) == CASES['expected']['generations_after_two_commits']
            assert send(q, 'state')['receipts'] == 2
            passed('two-joined-command-workers')
            replay = send(q, 'start', body=body(1)); assert replay['event'] == 'immediate' and replay['result'] == second['result']
            assert before == inspect(v, '2', 2000); passed('exact-replay-no-extra-generation')

        v = config('policy-hold')
        with held(v) as (q, ready):
            begin(q, ready, kind='load', hold='policy')
            assert send(q, 'state') == {'error': CASES['expected']['concurrent_error']}
            assert send(q, 'close') == {'error': CASES['expected']['concurrent_error']}
            send(q, 'release'); answer = finish(q)
            assert answer['answer']['settings'] == INITIAL['documents']['settings']; inspect(v)
            passed('held-policy-concurrent-load-and-close')

        v = config('cancel')
        with held(v) as (q, ready):
            begin(q, ready, body=body(), hold='store.selector_ready')
            assert send(q, 'cancel')['error']['code'] == 'request.pending'; send(q, 'release')
            assert finish(q)['result']['outcome'] == 'cancelled'; inspect(v)
            passed('cancel-before-permit')

        v = config('guard')
        with held(v) as (q, _):
            facts = send(q, 'guard', body=body())
            assert facts['revision'] == 0 and facts['receipts'] == 0 and facts['absent'] and not facts['previous']
            assert facts['path'] == str(store_root(v)) and len(facts['generation']) == 64
            assert facts['nested_publish'] == facts['nested_close'] == CASES['expected']['recursive_error'] and facts['durable']
            inspect(v, '1', 1500); passed('guard-readback-and-recursive-refusal')
            try: inspect(v, '1', 2000)
            except AssertionError: passed('wrong-output-oracle-rejects')
            else: raise AssertionError('wrong output was accepted')

        v = config('reentry')
        with held(v) as (q, _):
            assert 'error' in send(q, 'reentry'); assert send(q, 'state')['error'] == 'profile_store.invalidated'; inspect(v)
            passed('policy-reentry-refuses')

        v = config('deny')
        with held(v) as (q, ready):
            begin(q, ready, body=body(), hold='store.selector_ready'); send(q, 'deny')
            concealed = send(q, 'query'); assert concealed['outcome'] == 'unknown' and concealed['stored'] is None
            send(q, 'release'); assert finish(q)['result']['outcome'] == 'unknown'; inspect(v)
            send(q, 'regrant'); assert send(q, 'state')['error'] == 'profile_store.invalidated'
            passed('policy-revocation-invalidates')

        v = config('failed', available=False)
        failed = subprocess.run(args(v), capture_output=True, timeout=5)
        assert failed.returncode == 1 and json.loads(failed.stdout)['error'] == 'profile_store.policy'
        assert not Path(v['root']).exists(); passed('startup-failure-joins')
        v = config('native', native=True)
        native = subprocess.run(args(v), capture_output=True, timeout=5)
        assert native.returncode == 1 and json.loads(native.stdout)['error'] == 'profile_store.policy'
        assert not Path(v['root']).exists(); passed('native-policy-default', available=False)

        v = config('close')
        with held(v) as (q, _):
            before = inspect(v); assert send(q, 'close') == {'closed': True}; assert tasks(q) == {q.pid}
            assert send(q, 'state') == {'error': CASES['expected']['closed_error']}
            assert send(q, 'close') == {'closed': True}; competitor(v, good=True)
            assert before == inspect(v); passed('close-reopen-and-closed-calls')

        for cut in CASES['cuts']:
            v = config('cut-'+cut['phase'].replace('.', '-'))
            with held(v) as (q, ready):
                begin(q, ready, body=body(), hold=cut['phase'])
                before = inspect(v, cut['revision'], 1500 if cut['revision'] == '1' else None)
                q.kill(); assert q.wait(timeout=3) == -signal.SIGKILL
                assert not Path('/proc', str(q.pid)).exists()
            with held(dict(v, epoch='E2')) as (q, _):
                recovered = send(q, 'reconcile')['result']; assert recovered['outcome'] == cut['outcome']
                if cut['revision'] == '1': assert recovered['revision'] == '1' and recovered['stored'] and recovered['durable']
                assert before == inspect(v, cut['revision'], 1500 if cut['revision'] == '1' else None)
            passed('cut-before-selection' if cut['revision'] == '0' else 'cut-after-durability', phase=cut['phase'], recovered=recovered)
        assert {v['case'] for v in report['cases']} == set(CASES['cases'])
        report['outcome'] = 'pass'
    except Exception:
        report['error'] = traceback.format_exc(); raise
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json', flush=True)


if __name__ == '__main__':
    main()

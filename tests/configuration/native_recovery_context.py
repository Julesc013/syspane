"""Compare native recovery admission with frozen documents, selector bytes and kernel nodes."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import copy, hashlib, json, os, select, signal, stat, subprocess, sys, time, uuid

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/configuration/recovery-context-cases.json'
CASES = json.loads(FIXTURE.read_bytes())
INITIAL = ROOT / CASES['initial_documents']
COMMAND = ROOT / CASES['commit']
DEFAULTS = json.loads(INITIAL.read_bytes())
TRACE = json.loads(COMMAND.read_bytes())
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()


def write(path, raw):
    path.write_bytes(raw)
    path.chmod(0o600)


def main():
    exe, evidence = [Path(v).resolve() for v in sys.argv[1:3]]
    assert os.geteuid() != 0 and evidence.is_relative_to(exe.parent)
    folder = evidence / ('recovery-context-' + uuid.uuid4().hex[:12])
    folder.mkdir(mode=0o700, parents=True)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    report = dict(family=CASES['family'], outcome='fail', uid=os.geteuid(), filesystem='ext4', kernel=list(os.uname()),
                  started_at=datetime.now(timezone.utc).isoformat(), artifact_sha256=sha(exe.read_bytes()),
                  inputs={p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in (Path(__file__), FIXTURE, INITIAL, COMMAND)},
                  cases=[], processes=[])
    buffers = {}
    deadline = time.monotonic() + CASES['case_timeout_seconds']
    packages = {sha(p['manifest'].encode()): p for p in DEFAULTS['packages']}
    body = encoded(TRACE['command']).decode()

    def save():
        write(folder / 'result.json', encoded(report))

    @contextmanager
    def case(name):
        nonlocal deadline
        deadline = time.monotonic() + CASES['case_timeout_seconds']
        started = time.monotonic()
        signal.alarm(CASES['case_timeout_seconds'])
        facts = {}
        try:
            yield facts
            elapsed = time.monotonic() - started
            assert elapsed <= CASES['case_timeout_seconds']
            report['cases'].append(dict(case=name, outcome='pass', elapsed_seconds=elapsed, **facts))
            save()
        finally:
            signal.alarm(0)

    def timeout(_signum, _frame):
        raise AssertionError('case deadline expired')

    signal.signal(signal.SIGALRM, timeout)

    def read(q):
        while b'\n' not in buffers[q.pid]:
            remaining = deadline - time.monotonic()
            assert remaining > 0 and select.select([q.stdout], [], [], remaining)[0], 'snapshot observation timeout'
            raw = os.read(q.stdout.fileno(), 65536)
            assert raw, ('snapshot EOF', q.poll())
            buffers[q.pid] += raw
            assert len(buffers[q.pid]) < 1024 * 1024
        raw, buffers[q.pid] = buffers[q.pid].split(b'\n', 1)
        return json.loads(raw)

    def send(q, op, **fields):
        q.stdin.write(encoded(dict(op=op, **fields)) + b'\n')
        q.stdin.flush()
        return read(q)

    def location(name, **fields):
        return dict(profile=CASES['profile'], root=str(folder / name), **fields)

    def state(v):
        return Path(v['root']) / 'syspane/state' / sha(v['profile'].encode())

    def generations(v):
        return Path(v['root']) / 'syspane/configuration' / sha(v['profile'].encode()) / 'generations'

    @contextmanager
    def held(v):
        config = folder / ('input-' + uuid.uuid4().hex[:10] + '.json')
        write(config, encoded(v))
        q = subprocess.Popen([str(exe), str(config)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        buffers[q.pid] = b''
        normal = False
        try:
            ready = read(q)
            assert ready['event'] == 'ready' and ready['pid'] == q.pid, ready
            yield q, ready
            q.stdin.write(b'{"op":"exit"}\n')
            q.stdin.flush()
            assert q.wait(timeout=min(3, max(.01, deadline-time.monotonic()))) == 0
            normal = True
        finally:
            if q.poll() is None:
                q.kill()
                q.wait(timeout=3)
            stderr = q.stderr.read()
            write(folder / ('stderr-' + str(q.pid)), stderr)
            report['processes'].append(dict(pid=q.pid, exit=q.returncode, normal_exit=normal, stderr_sha256=sha(stderr)))
            q.stdin.close(); q.stdout.close(); q.stderr.close()
            del buffers[q.pid]

    def documents(out, revision='0'):
        settings = copy.deepcopy(DEFAULTS['documents']['settings'])
        scene = copy.deepcopy(DEFAULTS['documents']['scene'])
        settings['revision'] = scene['revision'] = revision
        if revision == '1':
            settings['sampling']['resources_ms'] = TRACE['expected_resources_ms']
        assert out['settings'] == settings and out['scene'] == scene
        assert out['selection'] == DEFAULTS['selection'] and out['theme_pin'] == DEFAULTS['theme_pin']
        assert out['packages'] == packages and out['shared_resources'] is True

    def admission(out, v, revision='0', erase=True, permitted=True):
        documents(out, revision)
        if not permitted:
            assert out['recovery'] is None
            return
        nodes = []
        for path in (state(v), state(v) / 'recovery'):
            observed = path.lstat()
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            try:
                held_info = os.fstat(fd)
                assert (observed.st_dev, observed.st_ino) == (held_info.st_dev, held_info.st_ino)
                assert observed.st_uid == held_info.st_uid == os.geteuid() and stat.S_IMODE(held_info.st_mode) == 0o700
                nodes.append(held_info)
            finally:
                os.close(fd)
        parent, child = nodes
        assert out['recovery'] == dict(profile=v['profile'], path=str(state(v) / 'recovery'), uid=os.geteuid(),
            state_device=parent.st_dev, state_inode=parent.st_ino, recovery_device=child.st_dev, recovery_inode=child.st_ino,
            generation=sha((generations(v) / 'current.json').read_bytes()), policy_revision=CASES['policy_revision'], erase=erase)
        selector = json.loads((generations(v) / 'current.json').read_bytes())
        generation = generations(v) / selector['generation']
        manifest_raw = (generation / 'manifest.json').read_bytes()
        assert sha(manifest_raw) == selector['manifest']
        manifest = json.loads(manifest_raw)
        for name in ('settings', 'scene'):
            raw = (generation / (name + '.json')).read_bytes()
            assert raw == encoded(out[name]) and sha(raw) == manifest[name]

    def inventory(path):
        return {p.relative_to(path).as_posix(): (p.lstat().st_dev, p.lstat().st_ino, sha(p.read_bytes()))
                for p in path.rglob('*') if stat.S_ISREG(p.lstat().st_mode)}

    def rename(source, target):
        for path in (source, target):
            assert path.resolve().is_relative_to(folder.resolve()) and path.resolve() != folder.resolve()
        assert not target.exists()
        source.rename(target)

    try:
        with case('EXACT'):
            v = location('exact')
            with held(v) as (q, ready):
                admission(ready['snapshot'], v)
                admission(send(q, 'read'), v)
                first = ready['snapshot']['recovery']
        with case('REOPEN'):
            before = inventory(Path(v['root']))
            with held(v) as (_, ready):
                admission(ready['snapshot'], v)
                assert ready['snapshot']['recovery'] == first
            assert inventory(Path(v['root'])) == before
        with case('COMMIT'):
            with held(v) as (q, _):
                result = send(q, 'commit', body=body)
                assert result['result']['outcome'] == 'accepted'
                admission(result['snapshot'], v, '1')
                assert result['snapshot']['recovery']['generation'] != first['generation']
                committed = result['snapshot']['recovery']
            with held(v) as (_, ready):
                admission(ready['snapshot'], v, '1')
                assert ready['snapshot']['recovery'] == committed
        with case('DENIED'):
            for i, fields in enumerate(({'denied': ['editor.recovery']}, {'history': ['public']}, {'denied': ['projection.history']})):
                denied = location('denied-' + str(i), **fields)
                with held(denied) as (q, ready):
                    admission(ready['snapshot'], denied, permitted=False)
                    admission(send(q, 'read'), denied, permitted=False)
        with case('ERASE-DENIED'):
            denied = location('erase-denied', denied=['editor.recovery.erase'])
            with held(denied) as (q, ready):
                admission(ready['snapshot'], denied, erase=False)
                admission(send(q, 'read'), denied, erase=False)
        with case('ROLE'):
            role = location('role')
            with held(role) as (q, _):
                for auth, name, grants in ((False, 'console', ['console']), (True, 'console', []), (True, 'desktop', ['desktop']), (True, 'extension', ['console'])):
                    admission(send(q, 'authority', authenticated=auth, role=name, grants=grants), role, permitted=False)
                admission(send(q, 'read'), role)
        with case('CAPABILITY'):
            cap = location('capability', recovery_capability=False)
            with held(cap) as (q, ready):
                admission(ready['snapshot'], cap, permitted=False)
                admission(send(q, 'read'), cap, permitted=False)
        with case('POLICY-CHANGE'):
            for i, (op, fields) in enumerate((('deny', {}), ('profile-denied', {}), ('revision', {}), ('late-revision', {'at': 5}))):
                changed = location('policy-' + str(i))
                with held(changed) as (q, _):
                    before = inventory(Path(changed['root']))
                    assert send(q, op, **fields)['error'].startswith('profile')
                    assert send(q, 'regrant')['error'] == 'profile_store.invalidated'
                    assert inventory(Path(changed['root'])) == before
        for name, child in (('REPLACED-ROOT', False), ('REPLACED-RECOVERY', True)):
            with case(name):
                replacement = location(name.lower())
                with held(replacement) as (q, _):
                    path = state(replacement) / 'recovery' if child else state(replacement)
                    original = path.with_name(path.name + '-original')
                    before = inventory(path)
                    rename(path, original); path.mkdir(mode=0o700)
                    assert send(q, 'read')['error'].startswith('profile')
                    assert not list(path.iterdir()) and inventory(original) == before
                    rename(path, path.with_name(path.name + '-rejected')); rename(original, path)
                    assert send(q, 'read')['error'] == 'profile_store.invalidated'
                if not child:
                    marker = location('marker')
                    with held(marker) as (q, _):
                        path = state(marker) / '.owner.json'; raw = path.read_bytes()
                        write(path, b'{}')
                        assert send(q, 'read')['error'].startswith('profile')
                        write(path, raw)
                        assert send(q, 'read')['error'] == 'profile_store.invalidated'
        with case('FALLBACK'):
            broken = location('fallback')
            with held(broken) as (q, _):
                assert send(q, 'commit', body=body)['result']['outcome'] == 'accepted'
            write(generations(broken) / 'current.json', b'{}')
            before = inventory(Path(broken['root']))
            with held(broken) as (q, ready):
                admission(ready['snapshot'], broken, permitted=False)
                admission(send(q, 'read'), broken, permitted=False)
            assert inventory(Path(broken['root'])) == before
        with case('THREAD'):
            thread = location('thread')
            with held(thread) as (q, ready):
                assert ready['storage_tid'] == ready['caller_tid']
                result = send(q, 'thread')
                assert result['snapshot']['error'] == 'profile_store.thread'
                assert result['caller_tid'] != result['storage_tid'] and not result['wrong_thread']
                admission(send(q, 'read'), thread)
        with case('WORKER') as facts:
            worker = location('worker', worker=True)
            with held(worker) as (q, ready):
                assert ready['storage_tid'] != ready['caller_tid']
                admission(ready['snapshot'], worker)
                result = send(q, 'thread')
                admission(result['snapshot'], worker)
                assert result['caller_tid'] not in (ready['caller_tid'], result['storage_tid']) and not result['wrong_thread']
                event = send(q, 'hold', at=5)
                assert event == dict(event='held', tid=ready['storage_tid'], reads=5)
                assert send(q, 'read')['error'] == 'profile_worker.busy'
                result = send(q, 'release')
                admission(result['snapshot'], worker)
                assert not result['wrong_thread']
                facts['storage_tid'] = result['storage_tid']; facts['caller_tid'] = result['caller_tid']
                result = send(q, 'commit', body=body)
                assert result['result']['outcome'] == 'accepted'
                admission(result['snapshot'], worker, '1')
        with case('ORACLE') as facts:
            oracle = location('oracle')
            with held(oracle) as (_, ready):
                bad = copy.deepcopy(ready['snapshot']); bad['recovery']['generation'] = '0' * 64
                detected = False
                try:
                    admission(bad, oracle)
                except AssertionError:
                    detected = True
                assert detected
                facts['wrong_generation_detected'] = detected
        assert [c['case'] for c in report['cases']] == CASES['cases']
        assert all(p['normal_exit'] and p['exit'] == 0 for p in report['processes'])
        report['outcome'] = 'pass'
    except Exception as exc:
        report['error'] = repr(exc)
        raise
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['files'] = {p.relative_to(folder).as_posix(): sha(p.read_bytes()) for p in folder.rglob('*')
                           if stat.S_ISREG(p.lstat().st_mode) and p.name != 'result.json'}
        save()
        print(folder / 'result.json', report['outcome'], len(report['cases']))


if __name__ == '__main__':
    main()

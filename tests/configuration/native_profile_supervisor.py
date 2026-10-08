"""Independent clients, pidfds, clocks and exact stored bytes for the native supervisor."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import os
import select
import signal
import socket
import struct
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/profile-supervisor-cases.json').read_bytes())
INITIAL = json.loads((ROOT/'tests/configuration/profile-startup-cases.json').read_bytes())
COMMAND = json.loads((ROOT/'tests/configuration/profile-startup-command-case.json').read_bytes())['command']
encoded = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
sha = lambda value: hashlib.sha256(value).hexdigest()


def main():
    probe, evidence = [Path(p).resolve() for p in sys.argv[1:3]]
    assert os.geteuid() and evidence.parent == probe.parent
    assert json.loads((probe.parent/'.syspane-owner.json').read_bytes())['profile'] == 'linux-x64-gcc13'
    folder = evidence/('ps-'+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700, parents=True)
    # Explicitly inside the existing owned campaign: short Unix endpoints cannot
    # use the longer nested evidence path. Preserve this second owned root too.
    runtime = probe.parent.parent/('s-'+uuid.uuid4().hex[:8]); runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(family='PROFILE-SUPERVISOR', evidence=str(folder))))
    helper = runtime/'h'; os.link(probe, helper); fixture = runtime/'h.fixture'
    record = dict(family=CASES['family'], outcome='fail', uid=os.geteuid(), kernel=list(os.uname()),
                  artifact_sha256=sha(probe.read_bytes()), oracle_sha256=sha(Path(__file__).read_bytes()),
                  runtime_directory=str(runtime), started_at=datetime.now(timezone.utc).isoformat(), cases=[], runs=[])

    def save(): (folder/'result.json').write_bytes(encoded(record))

    def passed(name, **facts):
        assert name in CASES['cases'] and name not in [v['case'] for v in record['cases']]
        record['cases'].append(dict(case=name, outcome='pass', **facts)); save()

    def configure(**value):
        temporary = fixture.with_suffix('.tmp'); temporary.write_bytes(encoded(value)); os.replace(temporary, fixture)

    def inspect(data, revision='0', wrong=False):
        generations = data/'profile/syspane/configuration'/sha(CASES['profile'].encode())/'generations'
        selecting = json.loads((generations/'current.json').read_bytes()); current = generations/selecting['generation']
        raw = (current/'manifest.json').read_bytes(); assert sha(raw) == selecting['manifest']; manifest = json.loads(raw)
        documents = copy.deepcopy(INITIAL['documents']); documents['settings']['revision'] = documents['scene']['revision'] = revision
        if revision == '1': documents['settings']['sampling']['resources_ms'] = 1500
        if wrong: documents['settings']['sampling']['resources_ms'] = 9000
        for kind in ('settings', 'scene'):
            raw = (current/(kind+'.json')).read_bytes(); assert raw == encoded(documents[kind]) and sha(raw) == manifest[kind]
        assert manifest['revision'] == revision
        packages = {sha(p['manifest'].encode()): p for p in INITIAL['packages']}
        raw = (current/'resources.json').read_bytes(); assert sha(raw) == manifest['resources']
        assert json.loads(raw) == dict(version='0.1.0', selection=INITIAL['selection'], theme=INITIAL['theme_pin'], packages=sorted(packages))
        for key, package in packages.items():
            assert (current/'resources'/('m-'+key+'.json')).read_bytes() == package['manifest'].encode()
            for asset in package['assets'].values(): assert (current/'resources'/('a-'+sha(asset.encode())+'.bin')).read_bytes() == asset.encode()
        if revision == '0': assert manifest['version'] == '0.5.0' and manifest['identity'] is None
        else:
            assert manifest['version'] == '0.3.0' and (current/'request.json').read_bytes() == encoded(COMMAND)
            assert manifest['identity']['principal'] == 'linux:'+str(os.geteuid())+':'+str(os.getsid(0))
        return {p.relative_to(generations).as_posix(): sha(p.read_bytes()) for p in generations.rglob('*') if p.is_file()}

    class Driver:
        def __init__(self, mode='real', driver='normal', permissions=None, contents=False, **options):
            self.data = folder/('c'+str(len(record['runs']))); self.data.mkdir(mode=0o700)
            self.runtime = runtime/('r'+str(len(record['runs']))); self.runtime.mkdir(mode=0o700)
            assert len(str(self.runtime).encode()) <= 70
            if permissions is not None: self.runtime.chmod(permissions)
            if contents: (self.runtime/'keep').write_bytes(b'keep')
            configure(mode=mode, **options)
            self.stderr = (self.data/'stderr').open('wb'); self.events = []; self.pending = b''; self.pidfds = {}; self.eof = False
            self.process = subprocess.Popen([str(probe), str(helper), str(self.runtime), str(self.data/'profile'), str(os.getpid()), driver],
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr, close_fds=True)
            self.row = dict(parent=self.process.pid, mode=mode, events=self.events); record['runs'].append(self.row)

        def pump(self):
            if select.select([self.process.stdout], [], [], .01)[0]:
                more = os.read(self.process.stdout.fileno(), 65536); self.pending += more
                if not more: self.eof = True
            while b'\n' in self.pending:
                raw, self.pending = self.pending.split(b'\n', 1); value = json.loads(raw); value['received_at'] = time.monotonic()
                pid = value.get('pid', 0)
                if pid and pid not in self.pidfds:
                    try:
                        fd = os.pidfd_open(pid); self.pidfds[pid] = fd
                        status = Path('/proc', str(pid), 'status').read_text()
                        assert '\nPPid:\t'+str(self.process.pid)+'\n' in status
                    except ProcessLookupError: self.pidfds[pid] = None
                    except FileNotFoundError: pass
                if value['event'] == 'reaped':
                    fd = self.pidfds.get(pid)
                    assert (bool(select.select([fd], [], [], 0)[0]) if fd is not None else not Path('/proc', str(pid)).exists())
                    value['independently_exited'] = True
                self.events.append(value)
            save()

        def await_event(self, predicate, seconds=8):
            end = time.monotonic()+seconds
            while time.monotonic() < end:
                self.pump()
                for value in self.events:
                    if predicate(value): return value
                assert not self.eof or self.process.poll() is None, ((self.data/'stderr').read_bytes(), self.events)
            raise AssertionError(('independent observation timeout', self.events))

        def ready(self, generation=1):
            return self.await_event(lambda e: e['event'] == 'ready' and e['generation'] == generation)

        def command(self, value): self.process.stdin.write((value+'\n').encode()); self.process.stdin.flush()

        def close(self):
            if self.process.poll() is None:
                self.command('drain'); self.command('close')
                self.await_event(lambda e: e.get('state') == 'closed', 5)
                assert self.process.wait(timeout=2) == 0
            self.pump(); self.stderr.close(); self.row['exit'] = self.process.returncode
            for fd in self.pidfds.values():
                if fd is not None: os.close(fd)
            self.pidfds.clear(); save()

        def __enter__(self): return self
        def __exit__(self, *error):
            try: self.close()
            finally:
                if self.process.poll() is None: self.process.kill(); self.process.wait(timeout=3)

    class Client:
        def __init__(self, ready):
            self.epoch = ready['epoch']; self.socket = socket.socket(socket.AF_UNIX); self.socket.settimeout(4)
            self.socket.connect(ready['endpoint'])
            assert struct.unpack('3i', self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))[0] == ready['pid']
            docs = [dict(document=n, version=v) for n, v in [('command', '0.5.0'), ('command-result', '0.1.0'), ('reconciliation-request', '0.1.0'), ('reconciliation-result', '0.1.0')]]
            self.send('hello', dict(wire_major=0, wire_minor=1, role='console', producer_epoch='client', max_frame_bytes=328704,
                                   document_versions=docs, required_features=['configuration.transactions', 'result.reconcile'],
                                   optional_features=['configuration.content', 'configuration.scene-content', 'configuration.large-commands', 'cancel', 'result.get']))
            assert self.receive()['type'] == 'welcome'

        def send(self, kind, body):
            message = dict(type=kind, body=body)
            if kind != 'hello': message.update(connection_id='C', producer_epoch=self.epoch)
            raw = encoded(message); self.socket.sendall(struct.pack('!I', len(raw))+raw)

        def receive(self):
            def exact(n):
                data = b''
                while len(data) < n:
                    more = self.socket.recv(n-len(data)); assert more; data += more
                return data
            n = struct.unpack('!I', exact(4))[0]; assert 0 < n <= 328704; return json.loads(exact(n))

        def close(self): self.socket.close()

    try:
        with Driver() as d:
            first = d.ready(); c = Client(first); inspect(d.data)
            c.send('command', COMMAND); result = c.receive()['body']; assert result['outcome'] == 'accepted' and result['revision'] == '1'
            before = inspect(d.data, '1'); c.close(); d.close()
            assert d.events[-1]['exit'] == {'signaled': False, 'code': 0} and not list(d.runtime.iterdir()) and before == inspect(d.data, '1')
            passed('cold-start-real-commit-and-cooperative-close')
            try: inspect(d.data, '1', wrong=True)
            except AssertionError: passed('wrong-stored-output-oracle-rejected')
            else: raise AssertionError('wrong stored output accepted')
        with Driver(driver='preclose') as d:
            d.await_event(lambda e: e.get('state') == 'closed'); assert not any(e['event'] == 'launched' for e in d.events)
            passed('close-before-launch')
        with Driver(driver='wrongthread') as d:
            d.ready(); assert any(e['event'] == 'thread-refused' and e['count'] == 2 for e in d.events); passed('wrong-thread-refused')
        for mode, why, case, minimum in [('startup', 'startup_timeout', 'startup-timeout', 4900),
                                        ('heartbeat', 'health_expired', 'heartbeat-timeout', 2900),
                                        ('operation', 'operation_timeout', 'healthy-heartbeats-do-not-renew-operation', 4900)]:
            with Driver(mode) as d:
                fault = d.await_event(lambda e: e['event'] == 'fault'); assert fault['fault'] == 'supervisor.'+why and fault['state'] == 'quarantined'
                reference = next(e for e in d.events if e['event'] == ('armed' if mode == 'operation' else 'ready' if mode == 'heartbeat' else 'launched'))
                elapsed = fault['observed_ms']-reference['observed_ms']; assert minimum <= elapsed <= minimum+2100
                stopped = d.await_event(lambda e: e['event'] == 'reaped'); assert stopped['exit'] == {'signaled': True, 'code': 9}
                if mode == 'operation': assert int(Path(str(fixture)+'.beats').read_text()) >= 7
                passed(case, elapsed_ms=elapsed)
        for mode, why, case in [('epoch', 'epoch', 'wrong-epoch-refused'), ('malformed', 'protocol', 'malformed-health-refused'), ('stderr', 'stderr', 'stderr-bound')]:
            with Driver(mode) as d:
                fault = d.await_event(lambda e: e['event'] == 'fault'); assert fault['fault'] == 'supervisor.'+why
                d.await_event(lambda e: e['event'] == 'reaped'); assert not any(e['event'] == 'ready' for e in d.events); passed(case)
        with Driver('zero') as d:
            first = d.ready(); d.await_event(lambda e: e['event'] == 'reaped'); configure(mode='real')
            second = d.ready(2); assert first['epoch'] != second['epoch'] and first['pid'] != second['pid']
            c = Client(second); inspect(d.data); c.close(); passed('zero-exit-replaced-with-fresh-epoch')
        with Driver('zero') as d:
            circuit = d.await_event(lambda e: e.get('state') == 'circuit_open', 13)
            launched = [e for e in d.events if e['event'] == 'launched']; reaped = [e for e in d.events if e['event'] == 'reaped']
            assert len(launched) == len(reaped) == 4 and circuit['restarts'] == 3
            assert len([e for e in d.events if e['event'] == 'ready']) == 4
            for index, delay in enumerate((1000, 2000, 4000)):
                fault = next(e for e in d.events if e['event'] == 'fault' and e['generation'] == index+1)
                assert launched[index+1]['observed_ms']-fault['observed_ms'] >= delay
            passed('ready-does-not-reset-restart-circuit')
        with Driver('blocked-close') as d:
            ready = d.ready(); began = time.monotonic(); d.command('close')
            stopped = d.await_event(lambda e: e['event'] == 'reaped'); elapsed = time.monotonic()-began
            assert 1.95 <= elapsed <= 4 and stopped['exit'] == {'signaled': True, 'code': 9} and stopped['pid'] == ready['pid']
            passed('blocked-close-stops-exact-child', elapsed_seconds=elapsed)
        with Driver(phase='store.durable') as d:
            first = d.ready(); c = Client(first); c.send('command', COMMAND)
            d.await_event(lambda e: e['event'] == 'fault' and e['fault'] == 'supervisor.operation_timeout')
            before = inspect(d.data, '1'); c.close(); configure(mode='real'); second = d.ready(2); c = Client(second)
            c.send('result.reconcile', dict(schema_version='0.1.0', query_id='Q', original_producer_epoch=first['epoch'], request_id='R'))
            response = c.receive(); assert response['type'] == 'result.reconciled'
            answer = response['body']['result']; assert answer['outcome'] == 'accepted' and answer['durable'] and answer['revision'] == '1'
            assert before == inspect(d.data, '1'); c.close()
            passed('durable-lost-result-reconciles-without-repeat')
        with Driver() as d:
            first = d.ready(); c = Client(first); configure(mode='real', allow=False); c.send('result.get', dict(request_id='R'))
            stopped = d.await_event(lambda e: e['event'] == 'reaped'); assert stopped['exit'] == {'signaled': False, 'code': 126}
            assert c.socket.recv(4096) == b''; c.close(); configure(mode='real'); second = d.ready(2)
            assert first['epoch'] != second['epoch']; inspect(d.data); passed('policy-change-replaces-owner')
        for options in (dict(permissions=0o755), dict(contents=True)):
            with Driver(**options) as d:
                assert d.process.wait(timeout=3) == 2; d.pump(); assert not d.events
                if options.get('contents'): assert (d.runtime/'keep').read_bytes() == b'keep'
        passed('unsafe-runtime-refused')
        with Driver('blocked-close') as d:
            first = d.ready(); endpoint = Path(first['endpoint']); endpoint.unlink(); replacement = socket.socket(socket.AF_UNIX); replacement.bind(str(endpoint)); endpoint.chmod(0o600)
            identity = endpoint.stat().st_ino; d.command('close'); closed = d.await_event(lambda e: e.get('state') == 'closed')
            assert closed['fault'] == 'supervisor.cleanup' and endpoint.stat().st_ino == identity
            replacement.close(); passed('substituted-socket-preserved')
        with Driver() as d:
            first = d.ready(); fd = d.pidfds[first['pid']]; assert fd is not None
            d.process.kill(); assert d.process.wait(timeout=3) == -signal.SIGKILL
            assert select.select([fd], [], [], 3)[0]; passed('parent-death-stops-child')
        with Driver('flood', driver='hold-events') as d:
            fault = d.await_event(lambda e: e.get('fault') == 'supervisor.events')
            assert fault['state'] == 'quarantined' and not fault['endpoint']; d.command('drain')
            d.await_event(lambda e: e['event'] == 'reaped'); passed('undrained-events-stop-child')
        assert set(CASES['cases']) == {v['case'] for v in record['cases']}; record['outcome'] = 'pass'
    except BaseException:
        record['error'] = traceback.format_exc(); raise
    finally:
        record['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json')


if __name__ == '__main__': main()

"""Independent parent/client, kernel-lifetime and stored-byte oracle."""
from contextlib import contextmanager
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
import threading
import time
import traceback
import uuid
import warnings
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/profile-controller-cases.json').read_bytes())
INITIAL = json.loads((ROOT/'tests/configuration/profile-startup-cases.json').read_bytes())
COMMAND = json.loads((ROOT/'tests/configuration/profile-startup-command-case.json').read_bytes())['command']
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()


def command(index=0):
    v = copy.deepcopy(COMMAND)
    if index: v.update(request_id='R2', expected_revision='1'); v['operations'][0]['value'] = 2000
    return v


def packet(value):
    raw = encoded(value); return struct.pack('!I', len(raw))+raw


def wait_for(check, seconds=5):
    deadline = time.monotonic()+seconds
    while time.monotonic() < deadline:
        result = check()
        if result: return result
        time.sleep(.005)
    raise AssertionError('independent observation timeout')


def main():
    probe, production, startup, evidence = [Path(v).resolve() for v in sys.argv[1:5]]
    assert os.geteuid() and evidence.is_relative_to(probe.parent)
    folder = evidence/('pc-'+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700, parents=True)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    record = dict(family='PROFILE-CONTROLLER', outcome='fail', uid=os.geteuid(), filesystem='ext4', kernel=list(os.uname()),
                  started_at=datetime.now(timezone.utc).isoformat(), artifacts={p.name: sha(p.read_bytes()) for p in (probe, production, startup)},
                  oracle_sha256=sha(Path(__file__).read_bytes()), cases=[], children=[])
    schemas = {v['$id']: v for p in (ROOT/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_bytes())]}

    def validate(value, name):
        schema = json.loads((ROOT/'spec/contracts'/(name+'.schema.json')).read_bytes())
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            jsonschema.Draft202012Validator(schema, resolver=jsonschema.RefResolver.from_schema(schema, store=schemas)).validate(value)

    def save(): (folder/'result.json').write_bytes(encoded(record))

    def passed(name, **facts):
        assert name in CASES['cases'] and name not in [v['case'] for v in record['cases']]
        record['cases'].append(dict(case=name, outcome='pass', **facts)); save()

    def root(name):
        value = folder/name; value.mkdir(mode=0o700); return value

    def generations(data):
        return data/'profile/syspane/configuration'/sha(CASES['profile'].encode())/'generations'

    def inspect(data, revision='0', wrong=False):
        g = generations(data); selecting = json.loads((g/'current.json').read_bytes()); current = g/selecting['generation']
        raw = (current/'manifest.json').read_bytes(); assert sha(raw) == selecting['manifest']; manifest = json.loads(raw)
        documents = copy.deepcopy(INITIAL['documents']); documents['settings']['revision'] = documents['scene']['revision'] = revision
        if revision != '0': documents['settings']['sampling']['resources_ms'] = 1500 if revision == '1' else 2000
        if wrong: documents['settings']['sampling']['resources_ms'] = 9000
        for kind in ('settings', 'scene'):
            raw = (current/(kind+'.json')).read_bytes(); assert raw == encoded(documents[kind]); assert sha(raw) == manifest[kind]
        assert manifest['revision'] == revision
        raw = (current/'resources.json').read_bytes(); assert sha(raw) == manifest['resources']; resources = json.loads(raw)
        packages = {sha(p['manifest'].encode()): p for p in INITIAL['packages']}
        assert resources == dict(version='0.1.0', selection=INITIAL['selection'], theme=INITIAL['theme_pin'], packages=sorted(packages))
        for key, package in packages.items():
            assert (current/'resources'/('m-'+key+'.json')).read_bytes() == package['manifest'].encode()
            for asset in package['assets'].values(): assert (current/'resources'/('a-'+sha(asset.encode())+'.bin')).read_bytes() == asset.encode()
        if revision == '0': assert manifest['version'] == '0.5.0' and manifest['identity'] is None
        else:
            assert manifest['version'] == '0.3.0' and (current/'request.json').read_bytes() == encoded(command(int(revision)-1))
            assert manifest['identity']['principal'] == 'linux:'+str(os.geteuid())+':'+str(os.getsid(0))
        return {p.relative_to(g).as_posix(): sha(p.read_bytes()) for p in g.rglob('*') if p.is_file()}

    class Parent:
        def __init__(self, data, phase='-', epoch=None, native=False, patch=None, parent_pid=None, arm=True):
            self.data, self.epoch = data, epoch or CASES['epoch']; self.control = data/('policy-'+uuid.uuid4().hex[:8]); self.set_policy('allow')
            # The existing Unix adapter addresses the held directory via /proc/self/fd.
            self.socket_dir = folder/('i-'+uuid.uuid4().hex[:6]); self.socket_dir.mkdir(mode=0o700)
            self.endpoint = self.socket_dir/'s'; self.auto_arm = arm; self.ready = threading.Event(); self.stopped = threading.Event()
            self.lock = threading.Lock(); self.error = None; self.active = None; self.last_ticket = 0; self.events = []; self.requested = False
            self.a, child_socket = socket.socketpair(); self.a.setblocking(False); child_socket.setblocking(False)
            self.stderr_path = data/('stderr-'+uuid.uuid4().hex[:8]); self.stderr = self.stderr_path.open('wb')
            args = [str(production if native else probe), str(parent_pid or os.getpid())]
            if not native: args += [str(self.control), phase]
            env = dict(os.environ, SYSPANE_POLICY_FILE=str(self.control), SYSPANE_POLICY='allow')
            self.process = subprocess.Popen(args, stdin=child_socket, stdout=child_socket, stderr=self.stderr, close_fds=True, env=env)
            child_socket.close(); self.pidfd = os.pidfd_open(self.process.pid)
            self.started = time.monotonic(); self.row = dict(pid=self.process.pid, epoch=self.epoch, native=native, events=self.events)
            record['children'].append(self.row)
            bootstrap = dict(CASES['bootstrap'], producer_epoch=self.epoch, client_pid=str(os.getpid()), endpoint=str(self.endpoint), create=True,
                             profile=dict(id=CASES['profile'], home='', config_home='', data_home='', state_home='', portable_root=str(data/'profile')))
            if patch: bootstrap.update(patch)
            try: self.send_raw(bootstrap)
            except (BrokenPipeError, ConnectionResetError):
                assert parent_pid is not None and self.process.wait(timeout=1) == 2
            self.thread = threading.Thread(target=self.run); self.thread.start()

        def set_policy(self, mode):
            replacement = self.control.with_suffix('.tmp'); replacement.write_text(mode, encoding='utf-8'); os.replace(replacement, self.control)

        def send_raw(self, value):
            raw = packet(value); offset = 0; deadline = time.monotonic()+1
            with self.lock:
                while offset < len(raw):
                    assert time.monotonic() < deadline and select.select([], [self.a], [], .2)[1]
                    offset += self.a.send(raw[offset:])

        def send(self, kind, body):
            self.send_raw(dict(type=kind, body=body, connection_id='G', producer_epoch=self.epoch))

        def arm(self):
            assert self.active is not None
            self.send('transaction.armed', dict(ticket=str(self.active[0])))
            self.events.append(dict(event='armed', ticket=self.active[0], at=time.monotonic()))

        def kill(self, reason):
            if self.process.poll() is None:
                signal.pidfd_send_signal(self.pidfd, signal.SIGKILL)
                code = self.process.wait(timeout=3)
                self.events.append(dict(event='reaped', reason=reason, code=code, at=time.monotonic()))

        def run(self):
            pending = b''; last_sent = 0; sequence = 0; last_child = self.started
            try:
                while not self.stopped.is_set() and self.process.poll() is None:
                    now = time.monotonic()
                    if not self.requested:
                        if not self.ready.is_set() and now-self.started >= 5: self.kill('startup.deadline'); break
                        if self.active and now-self.active[1] >= 5: self.kill('operation.deadline'); break
                        if self.ready.is_set() and now-last_child >= 3: self.kill('health.deadline'); break
                    if self.ready.is_set() and not self.requested and now-last_sent >= .5:
                        self.send('heartbeat', dict(sequence=str(sequence))); sequence += 1; last_sent = now
                    if not select.select([self.a], [], [], .005)[0]: continue
                    raw = self.a.recv(4096)
                    if not raw: break
                    pending += raw
                    while len(pending) >= 4:
                        n = struct.unpack('!I', pending[:4])[0]; assert 0 < n <= 4096
                        if len(pending) < n+4: break
                        message = json.loads(pending[4:4+n]); pending = pending[4+n:]
                        kind = message['type']; self.events.append(dict(event=kind, body=message['body'], at=time.monotonic()))
                        if kind == 'hello':
                            assert not self.ready.is_set() and message['body']['producer_epoch'] == self.epoch
                            body = message['body']; assert set(body['required_features']) == {'recovery.health', 'recovery.transaction'}
                            self.send('welcome', body); last_child = time.monotonic(); self.ready.set()
                        else:
                            assert message['connection_id'] == 'G' and message['producer_epoch'] == self.epoch
                            if kind == 'heartbeat': last_child = time.monotonic()
                            elif kind == 'transaction.started':
                                ticket = int(message['body']['ticket']); assert self.active is None and ticket > self.last_ticket
                                self.active = (ticket, time.monotonic()); self.last_ticket = ticket
                                if self.auto_arm: self.arm()
                            elif kind == 'transaction.finished':
                                assert self.active and int(message['body']['ticket']) == self.active[0]
                                assert time.monotonic()-self.active[1] < 5; self.active = None
                            else: raise AssertionError(kind)
            except (BrokenPipeError, ConnectionResetError):
                try: self.process.wait(timeout=1)
                except subprocess.TimeoutExpired: self.error = traceback.format_exc()
            except Exception:
                if not self.requested and not self.stopped.is_set(): self.error = traceback.format_exc()

        def await_ready(self):
            wait_for(lambda: self.ready.is_set() or self.process.poll() is not None)
            assert self.ready.is_set() and self.process.poll() is None, (self.process.returncode, self.stderr_path.read_bytes(), self.error)

        def shutdown(self):
            self.requested = True; self.send('shutdown', dict(reason='normal'))
            code = self.process.wait(timeout=4); self.row['exit'] = code; return code

        def close(self):
            self.requested = True
            if self.process.poll() is None:
                try: self.shutdown()
                except (OSError, AssertionError, subprocess.TimeoutExpired): self.kill('fixture.cleanup')
            self.stopped.set(); self.thread.join(timeout=2); assert not self.thread.is_alive()
            self.a.close(); os.close(self.pidfd); self.stderr.close(); self.row['exit'] = self.process.returncode
            assert self.error is None, self.error

    @contextmanager
    def parent(data, **options):
        p = Parent(data, **options)
        try: yield p
        finally: p.close()

    class Client:
        def __init__(self, p, greeting=True):
            self.socket = socket.socket(socket.AF_UNIX); self.socket.settimeout(3); self.epoch = p.epoch
            # Long owned paths use exactly the native adapter's held-directory alias.
            fd = os.open(p.socket_dir, os.O_RDONLY|os.O_DIRECTORY)
            try: self.socket.connect('/proc/self/fd/'+str(fd)+'/s')
            finally: os.close(fd)
            assert struct.unpack('3i', self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))[0] == p.process.pid
            if greeting: self.hello(); assert self.receive()['type'] == 'welcome'
        def hello(self):
            docs = [dict(document=n, version=v) for n, v in [('command', '0.5.0'), ('command-result', '0.1.0'), ('reconciliation-request', '0.1.0'), ('reconciliation-result', '0.1.0')]]
            self.send('hello', dict(wire_major=0, wire_minor=1, role='console', producer_epoch='client', max_frame_bytes=328704,
                                   document_versions=docs, required_features=['configuration.transactions', 'result.reconcile'],
                                   optional_features=['configuration.content', 'configuration.scene-content', 'configuration.large-commands', 'cancel', 'result.get']))
        def send(self, kind, body):
            value = dict(type=kind, body=body)
            if kind != 'hello': value.update(connection_id='C', producer_epoch=self.epoch)
            self.socket.sendall(packet(value))
        def receive(self):
            def exact(n):
                data = b''
                while len(data) < n:
                    more = self.socket.recv(n-len(data)); assert more, 'client EOF'; data += more
                return data
            n = struct.unpack('!I', exact(4))[0]; assert 0 < n <= 328704; value = json.loads(exact(n))
            if value['type'] == 'result': validate(value['body'], 'command-result')
            if value['type'] == 'result.reconciled': validate(value['body'], 'reconciliation-result')
            return value
        def close(self): self.socket.close()

    try:
        data = root('basic')
        with parent(data) as p:
            p.await_ready(); c = Client(p); inspect(data); passed('cold-start-exact-profile')
            c.send('command', command()); first = c.receive()['body']; assert first['outcome'] == 'accepted' and first['revision'] == '1'; inspect(data, '1')
            c.send('command', command(1)); second = c.receive()['body']; assert second['outcome'] == 'accepted' and second['revision'] == '2'; before = inspect(data, '2')
            c.send('command', command(1)); assert c.receive()['body'] == second and before == inspect(data, '2')
            assert len(list(generations(data).glob('g-*'))) == 3; passed('sequential-commits-and-replay')
            c.close(); time.sleep(.05); c = Client(p); c.send('result.get', dict(request_id='R2')); assert c.receive()['body'] == second
            passed('disconnect-and-reconnect'); c.close(); assert p.shutdown() == 0
            assert not Path('/proc', str(p.process.pid)).exists(); assert before == inspect(data, '2')
            passed('cooperative-shutdown-releases-profile')
            try: inspect(data, '2', wrong=True)
            except AssertionError: passed('wrong-output-oracle-rejects')
            else: raise AssertionError('wrong bytes accepted')
        with parent(root('native'), native=True) as p:
            assert p.process.wait(timeout=5) == 2 and not (p.data/'profile').exists(); passed('production-policy-refuses-overrides')
        with parent(root('invalid'), patch={'policy': {'available': True}}) as p:
            assert p.process.wait(timeout=5) == 2 and not (p.data/'profile').exists(); passed('bootstrap-rejects-unknown-fields')
        with parent(root('parent'), parent_pid=os.getppid()) as p:
            assert p.process.wait(timeout=5) == 2 and not (p.data/'profile').exists(); passed('wrong-parent-refused')
        with parent(root('unarmed'), arm=False) as p:
            p.await_ready(); p.set_policy('wait'); c = Client(p, greeting=False); c.hello(); wait_for(lambda: p.active)
            assert not select.select([c.socket], [], [], .1)[0]
            assert len(list(Path('/proc', str(p.process.pid), 'task').iterdir())) == 2
            assert not Path(str(p.control)+'.policy-held').exists()
            p.arm(); p.auto_arm = True; wait_for(lambda: Path(str(p.control)+'.policy-held').exists())
            assert len(list(Path('/proc', str(p.process.pid), 'task').iterdir())) == 3
            Path(str(p.control)+'.policy-release').touch()
            assert c.receive()['type'] == 'welcome'; c.close(); passed('work-waits-for-independent-arm')
        with parent(root('cancel'), phase='store.selector_ready') as p:
            p.await_ready(); c = Client(p); c.send('command', command()); wait_for(lambda: Path(str(p.control)+'.held').exists())
            marker = json.loads(Path(str(p.control)+'.held').read_bytes()); assert marker['pid'] == p.process.pid and marker['tid'] != p.process.pid
            c.send('heartbeat', dict(sequence='1')); assert c.receive() == dict(type='heartbeat', body={'sequence': '1'}, connection_id='C', producer_epoch=p.epoch)
            c.send('cancel', dict(request_id='R')); pending = c.receive()['body']; assert pending['outcome'] == 'unknown' and pending['error']['code'] == 'request.pending'
            Path(str(p.control)+'.release').touch(); cancelled = c.receive()['body']; assert cancelled['outcome'] == 'cancelled'; inspect(p.data); c.close()
            passed('held-storage-heartbeat-and-cancel')
        for mode, name in [('deny', 'revoked-policy-prevents-disclosure'), ('drift', 'same-revision-policy-change')]:
            with parent(root(mode)) as p:
                p.await_ready(); c = Client(p); c.send('command', command()); assert c.receive()['body']['outcome'] == 'accepted'
                p.set_policy(mode); c.send('result.get', dict(request_id='R'))
                assert p.process.wait(timeout=4) == 126; assert c.socket.recv(4096) == b''; inspect(p.data, '1'); c.close(); passed(name)
        with parent(root('policy-hang')) as p:
            p.await_ready(); c = Client(p); p.set_policy('hang'); c.send('result.get', dict(request_id='R'))
            wait_for(lambda: Path(str(p.control)+'.policy-held').exists()); assert p.process.wait(timeout=7) == -signal.SIGKILL
            assert any(e.get('reason') == 'operation.deadline' for e in p.events); inspect(p.data); c.close(); passed('held-policy-expires-independent-watch')
        data = root('durable')
        with parent(data, phase='store.durable') as p:
            p.await_ready(); c = Client(p); c.send('command', command()); wait_for(lambda: Path(str(p.control)+'.held').exists())
            before = inspect(data, '1'); assert p.process.wait(timeout=7) == -signal.SIGKILL
            assert any(e.get('reason') == 'operation.deadline' for e in p.events); c.close()
        with parent(data, epoch=CASES['replacement_epoch']) as p:
            p.await_ready(); c = Client(p); c.send('result.reconcile', dict(schema_version='0.1.0', query_id='Q', original_producer_epoch=CASES['epoch'], request_id='R'))
            answer = c.receive()['body']['result']; assert answer['outcome'] == 'accepted' and answer['revision'] == '1' and answer['durable']
            assert before == inspect(data, '1'); c.close(); passed('durable-hang-restart-reconciliation')
        with parent(root('guardian-loss')) as p:
            p.await_ready(); c = Client(p); c.close(); p.requested = True; p.stopped.set(); p.thread.join(timeout=2)
            p.a.shutdown(socket.SHUT_RDWR); assert p.process.wait(timeout=4) == 124; passed('guardian-loss-exits')
        with parent(root('blocked-stop'), phase='store.selector_ready') as p:
            p.await_ready(); c = Client(p); c.send('command', command()); wait_for(lambda: Path(str(p.control)+'.held').exists())
            started = time.monotonic(); assert p.shutdown() == 125 and time.monotonic()-started < 3; inspect(p.data); c.close(); passed('blocked-shutdown-exits')
        with parent(root('foreign'), patch={'client_pid': str(os.getppid())}) as p:
            p.await_ready(); c = Client(p, greeting=False)
            try: c.hello(); assert c.socket.recv(4096) == b''
            except (BrokenPipeError, ConnectionResetError): pass
            assert p.process.poll() is None; inspect(p.data); c.close(); passed('foreign-client-refused')
        assert {v['case'] for v in record['cases']} == set(CASES['cases']); record['outcome'] = 'pass'
    except Exception:
        record['error'] = traceback.format_exc(); raise
    finally:
        record['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json', flush=True)


if __name__ == '__main__':
    main()

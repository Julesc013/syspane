"""Independent native profile-transfer, policy and coherent-resource oracle."""
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
DEFINITIONS = json.loads((ROOT/'tests/configuration/profile-projection-cases.json').read_bytes())
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


def main(extension=None, definitions=None):
    definitions = definitions or DEFINITIONS
    probe, production, startup, evidence = [Path(v).resolve() for v in sys.argv[1:5]]
    assert os.geteuid() and evidence.is_relative_to(probe.parent)
    folder = evidence/(('rt-' if extension else 'pp-')+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700, parents=True)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    record = dict(family=definitions['family'], outcome='fail', uid=os.geteuid(), filesystem='ext4', kernel=list(os.uname()),
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
        assert name in definitions['native'] and name not in [v['case'] for v in record['cases']]
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
            docs = [dict(document=n, version=v) for n, v in [('profile-request', '0.1.0'), ('profile-result', '0.1.0'), ('command', '0.5.0'), ('command-result', '0.1.0'), ('reconciliation-request', '0.1.0'), ('reconciliation-result', '0.1.0')]]
            self.send('hello', dict(wire_major=0, wire_minor=1, role='console', producer_epoch='client', max_frame_bytes=328704,
                                   document_versions=docs, required_features=['configuration.transactions', 'result.reconcile', 'configuration.profile'],
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
            if value['type'] == 'profile.chunk': validate(value['body'], 'profile-result-v0.2' if value['body']['schema_version']=='0.2.0' else 'profile-result')
            if value['type'] == 'result': validate(value['body'], 'command-result')
            if value['type'] == 'result.reconciled': validate(value['body'], 'reconciliation-result')
            return value
        def close(self): self.socket.close()


    def open_profile(client):
        client.send('profile.read', dict(schema_version='0.1.0', query_id='P0', op='open'))
        value = client.receive(); assert value['type'] == 'profile.chunk'; return value['body']

    def next_query(reply, query='Pnext'):
        part, offset = int(reply['part']), int(reply['offset'])+len(reply['hex'])//2
        if offset == int(reply['part_bytes']): part += 1; offset = 0
        return dict(schema_version='0.1.0', query_id=query, op='read', transfer_id=reply['transfer_id'], part=str(part), offset=str(offset))

    def expected_parts(revision):
        documents = copy.deepcopy(INITIAL['documents'])
        documents['settings']['revision'] = documents['scene']['revision'] = revision
        if revision == '1': documents['settings']['sampling']['resources_ms'] = 1500
        view = dict(revision='7', forced_settings=[], denied_capabilities=[], disclosure=[
            dict(channel=channel, allow_classifications=['operational','public','sensitive']) for channel in ['accessibility','inspector']])
        parts = [b'', encoded(documents['settings']), encoded(documents['scene']), encoded(view)]
        packages = []
        for package in sorted(INITIAL['packages'], key=lambda value: sha(value['manifest'].encode())):
            row = dict(manifest=str(len(parts)), assets=[]); parts.append(package['manifest'].encode())
            for path, raw in sorted(package['assets'].items()): row['assets'].append(dict(path=path, part=str(len(parts)))); parts.append(raw.encode())
            packages.append(row)
        parts[0] = encoded(dict(format='SysPane.ProfileImage', schema_version='0.1.0', revision=revision,
            selection=INITIAL['selection'], theme=INITIAL['theme_pin'], capabilities=sorted([
                'scene.selector','scene.content','scene.edit-locks','scene.visibility','theme.typography','configuration.theme-overrides']), packages=packages))
        return parts

    def download(client, revision='0', first=None, wrong=False):
        expected = expected_parts(revision); parts = [bytearray() for _ in expected]; chunks = []
        reply = first or open_profile(client); transfer = reply['transfer_id']; query = 'P0'; part = 0
        while True:
            assert reply['outcome'] == 'chunk' and reply['query_id'] == query and reply['transfer_id'] == transfer
            assert reply['revision'] == revision and reply['policy_generation'] == '7' and int(reply['part_count']) == len(expected)
            assert int(reply['part']) == part and int(reply['offset']) == len(parts[part]) and int(reply['part_bytes']) == len(expected[part])
            assert reply['sha256'] == sha(expected[part]); raw = bytes.fromhex(reply['hex'])
            assert len(raw) == min(4096,len(expected[part])-len(parts[part])) and raw.hex() == reply['hex']
            parts[part].extend(raw); chunks.append(dict(part=part, bytes=len(raw), sha256=sha(raw)))
            finished = len(parts[part]) == len(expected[part])
            assert reply['complete'] == (finished and part+1 == len(expected))
            if finished:
                assert bytes(parts[part]) == expected[part] and sha(parts[part]) == reply['sha256']
                part += 1
            if reply['complete']: break
            query = 'P'+str(len(chunks)); client.send('profile.read', next_query(reply,query)); message = client.receive()
            assert message['type'] == 'profile.chunk' and message['producer_epoch'] == client.epoch and message['connection_id'] == 'C'
            reply = message['body']
        if wrong: assert json.loads(parts[1])['sampling']['resources_ms'] == 9999
        record.setdefault('transfers',[]).append(dict(transfer_id=transfer, epoch=client.epoch, revision=revision, chunks=chunks,
            parts=[dict(bytes=len(raw), sha256=sha(raw)) for raw in parts])); save()
        return transfer

    try:
        if extension:
            extension(locals())
            assert set(definitions['native']) == {case['case'] for case in record['cases']}
            record['outcome'] = 'pass'
            return
        data = root('basic')
        with parent(data) as p:
            p.await_ready(); client = Client(p); download(client); inspect(data); passed('real-controller-exact-profile')
            first = open_profile(client); client.send('command', command()); result = client.receive()['body']
            assert result['outcome'] == 'accepted' and result['revision'] == '1'; inspect(data,'1')
            download(client,first=first); download(client,'1'); passed('commit-keeps-old-transfer-coherent')
            first = open_profile(client); client.close(); time.sleep(.05)
            client = Client(p); assert int(download(client,'1')) > int(first['transfer_id']); client.close()
            passed('native-disconnect-releases-transfer'); assert p.shutdown() == 0
        with parent(data,epoch=CASES['replacement_epoch']) as p:
            p.await_ready(); client = Client(p)
            old = dict(type='profile.read',body=next_query(first),connection_id='C',producer_epoch=CASES['epoch'])
            client.socket.sendall(packet(old)); assert client.socket.recv(4096) == b''; client.close(); time.sleep(.05)
            client = Client(p); download(client,'1'); inspect(data,'1'); client.close(); passed('reconnect-needs-new-transfer')
        for mode,name in [('deny','current-policy-before-disclosure'),('drift','same-revision-policy-invalidates')]:
            with parent(root(mode)) as p:
                p.await_ready(); client = Client(p); first = open_profile(client); p.set_policy(mode)
                client.send('profile.read',next_query(first)); assert p.process.wait(timeout=4) == 126
                assert client.socket.recv(4096) == b''; inspect(p.data); client.close(); passed(name)
        with parent(root('policy-hang')) as p:
            p.await_ready(); client = Client(p); first = open_profile(client); p.set_policy('hang')
            client.send('profile.read',next_query(first)); wait_for(lambda: Path(str(p.control)+'.policy-held').exists())
            assert p.process.wait(timeout=7) == -signal.SIGKILL and client.socket.recv(4096) == b''
            assert any(event.get('reason') == 'operation.deadline' for event in p.events)
            inspect(p.data); client.close(); passed('held-policy-deadline')
        assert set(DEFINITIONS['native']) == {case['case'] for case in record['cases']}
        record['outcome'] = 'pass'
    except Exception:
        record['error'] = traceback.format_exc(); raise
    finally:
        record['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json')


if __name__ == '__main__': main()

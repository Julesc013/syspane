"""Independent native peers, counters and process exits; operational records stay local."""
from pathlib import Path
from types import SimpleNamespace
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
sys.path.insert(0, str(ROOT/'tests/protocol'))
from native_collector import route_sockets, verify_documents
from native_network import linux_rows

def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

class Pipe:
    def __init__(self, sock): self.socket, self.pending, self.messages, self.eof = sock, b'', [], False
    def send(self, value):
        raw = encoded(value); self.socket.sendall(struct.pack('!I', len(raw))+raw)
    def pump(self):
        if not self.eof and select.select([self.socket], [], [], .001)[0]:
            try: more = self.socket.recv(65536)
            except ConnectionResetError: more = b''
            self.eof = not more; self.pending += more
        while len(self.pending) >= 4:
            size = struct.unpack('!I', self.pending[:4])[0]; assert 0 < size <= 1048576
            if len(self.pending) < 4+size: break
            raw, self.pending = self.pending[4:4+size], self.pending[4+size:]
            self.messages.append(json.loads(raw))

class Node:
    def __init__(self, helper, folder, mode='normal', policy='allow'):
        self.folder = folder; folder.mkdir(mode=0o700)
        (folder/'policy').write_text(policy); (folder/'network-mode').write_text(mode)
        self.epoch = 'network:test:'+uuid.uuid4().hex
        parent, child = socket.socketpair(); child.setblocking(False); self.health = Pipe(parent); self.data = None
        self.error = (folder/'stderr').open('wb')
        self.process = subprocess.Popen([str(helper), '--network', str(os.getpid())], cwd=folder,
                                        stdin=child, stdout=child, stderr=self.error, close_fds=True)
        child.close(); self.pidfd = os.pidfd_open(self.process.pid); self.sequence = 0; self.last = 0
        self.health.send(dict(format='SysPane.NetworkController', schema_version='0.1.0',
                              producer_epoch=self.epoch, client_pid=str(os.getpid()), endpoint=str(folder/'s')))
        self.ready = False; self.snapshots = []
    def message(self, kind, body, connection='C'):
        return dict(type=kind, body=body, connection_id=connection, producer_epoch=self.epoch)
    def pump(self, renew=True):
        self.health.pump()
        while self.health.messages:
            value = self.health.messages.pop(0)
            if value['type'] == 'hello':
                assert value['body']['role'] == 'collector' and value['body']['producer_epoch'] == self.epoch
                body = dict(value['body'], role='console')
                self.health.send(self.message('welcome', body, 'G')); self.ready = True
            else: assert value['type'] == 'heartbeat' and value['producer_epoch'] == self.epoch
        if self.ready and not self.health.eof and time.monotonic()-self.last >= .4:
            self.health.send(self.message('heartbeat', dict(sequence=str(self.sequence)), 'G'))
            if renew and self.data and not self.data.eof:
                self.data.send(self.message('heartbeat', dict(sequence=str(self.sequence))))
            self.sequence += 1; self.last = time.monotonic()
        if self.data:
            self.data.pump()
            while self.data.messages:
                value = self.data.messages.pop(0)
                if value['type'] == 'snapshot':
                    assert value['producer_epoch'] == self.epoch and value['connection_id'] == 'C'
                    self.snapshots.append(dict(event='imported', body=json.dumps(value['body']), duplicate=False,
                                               now_ns=time.clock_gettime_ns(time.CLOCK_BOOTTIME)))
                else: assert value['type'] in ('welcome', 'heartbeat', 'gap', 'shutdown')
    def until(self, predicate, timeout=5, renew=True):
        end = time.monotonic()+timeout
        while not predicate():
            assert time.monotonic() < end, 'native observation deadline'
            self.pump(renew); time.sleep(.003)
    def wait_ready(self):
        self.until(lambda: self.ready or self.process.poll() is not None)
        assert self.ready, 'network service entry did not establish guardian health'
    def connect(self, role='console', features=None):
        s = socket.socket(socket.AF_UNIX); s.connect(str(self.folder/'s')); self.data = Pipe(s)
        pid, uid, _ = struct.unpack('3i', s.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        assert pid == self.process.pid and uid == os.getuid()
        self.data.send(dict(type='hello', body=dict(wire_major=0, wire_minor=1, role=role,
            producer_epoch='consumer:test', max_frame_bytes=1048576,
            document_versions=[dict(document=k, version='0.2.0') for k in ('telemetry','snapshot','observation')],
            required_features=features or ['telemetry.snapshot','telemetry.measured-time'], optional_features=[])))
    def subscribe(self):
        self.data.send(self.message('subscribe', dict(schema_version='0.2.0', subscription_id='S',
            producer_id='producer:network', policy_revision='7', channel='inspector',
            classification='operational', clock_id='linux.boottime')))
    def exit(self, timeout=3, renew=True):
        self.until(lambda: bool(select.select([self.pidfd], [], [], 0)[0]), timeout, renew)
        return self.process.wait(timeout=1)
    def close(self):
        if self.process.poll() is None:
            self.health.send(self.message('shutdown', dict(reason='normal'), 'G'))
            assert self.exit() == 0
    def dispose(self):
        if self.process.poll() is None: self.process.kill()
        self.process.wait(timeout=3); self.health.socket.close(); self.error.close(); os.close(self.pidfd)
        if self.data: self.data.socket.close()

def main():
    helper, evidence = map(lambda p: Path(p).resolve(), sys.argv[1:3])
    assert os.geteuid() and evidence.parent == helper.parent
    assert json.loads((helper.parent/'.syspane-owner.json').read_bytes())['profile'] == 'linux-x64-gcc13'
    folder = evidence/('network-service-'+uuid.uuid4().hex[:8]); folder.mkdir(mode=0o700, parents=True)
    runtime = helper.parent.parent/('n-'+uuid.uuid4().hex[:6]); runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(evidence=str(folder), family='NETWORK-SERVICE')))
    record = dict(family='NETWORK-SERVICE', outcome='fail', source_base=subprocess.check_output(
        ['git','-c','safe.directory='+str(ROOT),'-C',str(ROOT),'rev-parse','HEAD'], text=True).strip(), artifact=sha(helper), oracle=sha(Path(__file__)),
        package=sha(ROOT/'spec/delivery/packages/w-25-network-service.md'), uid=os.getuid(), cases=[], runs=[])
    nodes = []
    def save(): (folder/'result.json').write_bytes(encoded(record))
    def passed(name, **facts): record['cases'].append(dict(case=name, outcome='pass', **facts)); save()
    def node(**options):
        n = Node(helper, runtime/str(len(nodes)), **options); nodes.append(n)
        record['runs'].append(dict(pid=n.process.pid, epoch=n.epoch, directory=str(n.folder), snapshots=n.snapshots))
        save(); n.wait_ready(); return n
    try:
        n = node(); n.connect(); end = time.monotonic()+.3; observed = invalidated = 0
        while time.monotonic() < end:
            n.pump()
            try: sockets = route_sockets(n.process.pid)
            except FileNotFoundError:
                # Native policy/clock checks open short-lived descriptors. Discard
                # an incomplete procfs observation within the original deadline.
                assert n.process.poll() is None; invalidated += 1; continue
            assert not sockets; observed += 1
        assert observed and not n.snapshots; passed('NO-DEMAND', observations=observed, invalidations=invalidated)
        before = linux_rows(); lower = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        n.subscribe(); n.until(lambda: len(n.snapshots) == 2)
        after = linux_rows(); upper = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        assert route_sockets(n.process.pid)
        verify_documents(SimpleNamespace(lines=n.snapshots), before, after, lower, upper, 'live'); passed('LIVE')
        wrong = copy.deepcopy(n.snapshots); body = json.loads(wrong[0]['body'])
        body['snapshot']['observations'][0]['value']['data'] = str(2**64-1); wrong[0]['body'] = json.dumps(body)
        try: verify_documents(SimpleNamespace(lines=wrong), before, after, lower, upper, 'live')
        except AssertionError: passed('ORACLE')
        else: raise AssertionError('wrong counter accepted')
        n.data.send(n.message('unsubscribe', dict(schema_version='0.2.0', subscription_id='S', clock_id='linux.boottime')))
        assert n.exit() == 0; passed('UNSUBSCRIBE')
        n = node(); n.connect(role='desktop'); assert n.exit() != 0 and not n.snapshots; passed('WRONG-ROLE')
        n = node(); n.connect(features=['settings.preview']); assert n.exit() != 0 and not n.snapshots; passed('CONFIGURATION-FEATURE')
        n = node(policy='no-disclosure'); n.connect(); n.subscribe()
        assert n.exit() != 0 and not n.snapshots; passed('DISCLOSURE')
        n = node(mode='hold'); n.connect(); n.subscribe(); n.until(lambda: (n.folder/'network-held').exists())
        changed = time.monotonic(); (n.folder/'policy').write_text('deny')
        assert n.exit(timeout=1) != 0 and not n.snapshots
        passed('POLICY-PENDING', elapsed=time.monotonic()-changed)
        n = node(mode='hold'); n.connect(); n.subscribe(); n.until(lambda: (n.folder/'network-held').exists())
        started = time.monotonic(); assert n.exit(timeout=3) != 0 and not n.snapshots
        passed('HUNG-READ', elapsed=time.monotonic()-started)
        n = node(); n.connect(); n.subscribe(); n.until(lambda: len(n.snapshots) >= 1)
        assert n.exit(timeout=4, renew=False) == 0; passed('DATA-LEASE')
        n = node(); n.close(); passed('CLOSE')
        n = node(mode='hold'); n.connect(); n.subscribe(); n.until(lambda: (n.folder/'network-held').exists())
        n.health.send(n.message('shutdown', dict(reason='normal'), 'G'))
        assert n.exit(timeout=3) != 0 and not n.snapshots; passed('CLOSE-HELD')
        n = node(); n.health.socket.close(); n.health.eof = True
        assert n.exit() != 0; passed('GUARDIAN-CHANNEL')
        record['outcome'] = 'pass'
    except BaseException:
        record['error'] = traceback.format_exc(); raise
    finally:
        for n in nodes:
            n.dispose()
            record['runs'][nodes.index(n)]['exit'] = n.process.returncode
        save(); print(json.dumps(dict(outcome=record['outcome'], cases=len(record['cases']), record=str(folder/'result.json'))))

if __name__ == '__main__': main()

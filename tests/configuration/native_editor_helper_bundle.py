"""Independent relocated-bundle, sealed-image, pixel and recovery-file oracle."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import errno
import ctypes
import fcntl
import hashlib
import importlib.util
import json
import os
import select
import signal
import stat
import struct
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/editor-helper-bundle-cases.json').read_bytes())
PIXELS = {v['name']: v for v in json.loads((ROOT/CASES['image_expectations']).read_bytes())}
RECORDS = {k: v.encode() for k, v in json.loads((ROOT/CASES['recovery_records']).read_bytes())['records'].items()}
BASE_IMPORTS = ['libc.so.6', 'libgcc_s.so.1', 'libm.so.6', 'libstdc++.so.6']
IMAGE_IMPORTS = ['libc.so.6', 'libgcc_s.so.1', 'libgdk_pixbuf-2.0.so.0', 'libglib-2.0.so.0', 'libgobject-2.0.so.0', 'libstdc++.so.6']
NAMES = ['syspane-configuration-host', 'syspane-image-worker', 'syspane-recovery-worker']
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()
LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.ptrace.restype = ctypes.c_long
LIBC.ptrace.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]


def ptrace(request, pid, data=0):
    result = LIBC.ptrace(request, pid, None, data)
    if result == -1: raise OSError(ctypes.get_errno(), 'native trace request '+str(request))
    return result


def write(path, raw, mode=0o600):
    path.write_bytes(raw)
    path.chmod(mode)


def check_pixels(actual, expected):
    assert actual == dict(width=expected['size'][0], height=expected['size'][1], rgba=expected['rgba']), ('pixel mismatch', actual, expected)


def check_file(path, expected):
    actual = path.read_bytes() if path.exists() else None
    assert actual == expected, ('file mismatch', sha(actual) if actual is not None else None, sha(expected) if expected is not None else None)


def main():
    probe, config, image_worker, recovery_worker, bundle_record, legacy_record, evidence = [Path(p).resolve() for p in sys.argv[1:]]
    helpers = [config, image_worker, recovery_worker]
    assert os.geteuid() and evidence.parent == probe.parent and all(p.parent == probe.parent for p in helpers)
    assert json.loads((probe.parent/'.syspane-owner.json').read_bytes())['profile'] == 'linux-x64-gcc13'
    folder = evidence/('eh-'+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700, parents=True)
    assert subprocess.check_output(['findmnt', '--target', str(folder), '--noheadings', '--output', 'FSTYPE'], text=True).strip() == 'ext4'
    raw_helpers = [p.read_bytes() for p in helpers]
    raw_record = bundle_record.read_bytes(); old_record = legacy_record.read_bytes()
    entries = {'bin/syspane': probe.read_bytes(), 'share/syspane/helpers.json': raw_record}
    entries.update({'libexec/syspane/'+name: raw for name, raw in zip(NAMES, raw_helpers)})
    image = folder/'image'; image.mkdir(mode=0o755)
    unrelated = folder/'cwd'; unrelated.mkdir(mode=0o700)
    mutations = folder/'mutations'; mutations.mkdir(mode=0o700)
    write(folder/'legacy-record.json', old_record)
    archive = folder/'syspane-editor-helper-development.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)); info.create_system = 3
            info.external_attr = (0o100644 if name.endswith('.json') else 0o100755)<<16
            info.compress_type = zipfile.ZIP_DEFLATED; z.writestr(info, raw)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == 5 and set(z.namelist()) == set(entries)
        for name, raw in entries.items():
            assert z.read(name) == raw
            path = image/name; path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            write(path, raw, z.getinfo(name).external_attr>>16 & 0o777)
    relocated = folder/'relocated image'; assert relocated.parent == image.parent == folder
    image.rename(relocated); image = relocated
    application = image/'bin/syspane'; installed = [image/'libexec/syspane'/name for name in NAMES]
    record = image/'share/syspane/helpers.json'
    baseline = {sha(raw): name for name, raw in entries.items()}
    started = time.monotonic(); deadline = started+CASES['family_timeout_seconds']
    report = dict(family=CASES['family'], outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
        uid=os.geteuid(), kernel=list(os.uname()), filesystem='ext4',
        payload='Five-file development test consumer; no installed editor or release qualification',
        artifacts={p.name: sha(p.read_bytes()) for p in [probe, *helpers, bundle_record]},
        package_sha256=sha(archive.read_bytes()), fixture_sha256=sha((ROOT/'tests/configuration/editor-helper-bundle-cases.json').read_bytes()),
        oracle_sha256=sha(Path(__file__).read_bytes()), cases=[], runs=[], snapshots=[])
    runs = []

    def save(): write(folder/'result.json', encoded(report))

    def capture(label):
        nodes = {}
        for path in [image, *sorted(image.rglob('*'))]:
            assert len(nodes) < 32
            s = path.lstat(); row = dict(mode=s.st_mode, uid=s.st_uid, gid=s.st_gid, device=s.st_dev,
                inode=s.st_ino, nlink=s.st_nlink, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)
            if stat.S_ISREG(s.st_mode):
                assert s.st_size <= 67108864
                raw = path.read_bytes(); digest = sha(raw); row.update(sha256=digest, bytes=len(raw))
                if digest in baseline: row['baseline_member'] = baseline[digest]
                else:
                    blob = mutations/(digest+'.z')
                    if not blob.exists(): write(blob, zlib.compress(raw))
                    assert sha(zlib.decompress(blob.read_bytes())) == digest
                    row['mutation_blob'] = blob.relative_to(folder).as_posix()
            elif stat.S_ISLNK(s.st_mode): row['target'] = os.readlink(path)
            else: assert stat.S_ISDIR(s.st_mode)
            nodes[path.relative_to(folder).as_posix()] = row
        report['snapshots'].append(dict(label=label, nodes=nodes)); save()

    @contextmanager
    def case(name):
        nonlocal deadline
        assert name in CASES['cases'] and name not in [v['case'] for v in report['cases']]
        begin = time.monotonic(); deadline = min(begin+CASES['case_timeout_seconds'], started+CASES['family_timeout_seconds'])
        signal.setitimer(signal.ITIMER_REAL, max(.001, deadline-begin))
        try:
            yield
            assert time.monotonic() <= deadline, name
            report['cases'].append(dict(case=name, outcome='pass', seconds=time.monotonic()-begin)); save()
        finally: signal.setitimer(signal.ITIMER_REAL, 0)

    def remaining():
        left = deadline-time.monotonic(); assert left > 0, 'case observation deadline'
        return min(left, 5)

    class Run:
        def __init__(self, mode='bundle', good=True):
            env = dict(os.environ, PATH='/nonexistent', SYSPANE_HELPER=str(unrelated/'evil'), SYSPANE_INSTALL_ROOT=str(unrelated))
            env.pop('LD_PRELOAD', None); env.pop('LD_LIBRARY_PATH', None)
            self.proc = subprocess.Popen(['unrelated-program', mode], executable=str(application), cwd=unrelated,
                env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
            self.pidfd = os.pidfd_open(self.proc.pid); self.children = {}; self.pending = b''; self.closed = False
            self.traced = set(); self.executed = {}
            self.row = dict(pid=self.proc.pid, mode=mode, events=[], children=[]); report['runs'].append(self.row); runs.append(self)
            self.initial = self.receive(); self.row['initial'] = self.initial
            assert (self.initial.get('event') == 'ready') == good, self.initial
            if good:
                assert self.initial['root'] == str(image)
                # Observe the kernel exec stop before the image worker disables
                # process inspection. This unprivileged parent tracer neither
                # changes worker code nor asks production to expose a test hook.
                ptrace(0x4206, self.proc.pid, 2 | 4 | 16)  # SEIZE: fork, vfork, exec
                self.traced.add(self.proc.pid)

        def trace(self):
            for pid in list(self.traced):
                found, status = os.waitpid(pid, os.WNOHANG | 0x40000000)  # __WALL
                if not found: continue
                if not os.WIFSTOPPED(status):
                    self.traced.remove(pid)
                    if pid == self.proc.pid: self.proc.returncode = os.waitstatus_to_exitcode(status)
                    else: raise AssertionError(('worker exited before observed exec', pid, status))
                    continue
                event = status >> 16
                if event in (1, 2):
                    child = ctypes.c_ulong(); ptrace(0x4201, pid, ctypes.addressof(child))
                    self.traced.add(child.value)
                    self.children[child.value] = os.pidfd_open(child.value)
                elif event == 4:
                    assert pid != self.proc.pid
                    path = Path('/proc', str(pid), 'exe'); link = os.readlink(path); digest = sha(path.read_bytes())
                    assert '\nPPid:\t'+str(self.proc.pid)+'\n' in Path('/proc', str(pid), 'status').read_text()
                    role = next((i for i, raw in enumerate(raw_helpers) if digest == sha(raw)), None)
                    assert role is not None and link.startswith('/memfd:'+NAMES[role]), (link, digest)
                    assert pid in self.children
                    row = dict(pid=pid, role=role, executable=link, sha256=digest, observation='kernel exec stop before worker containment')
                    self.executed[pid] = row; self.row['children'].append(row)
                    ptrace(17, pid); self.traced.remove(pid)  # DETACH before running helper instructions
                    continue
                ptrace(7, pid, 0 if event or os.WSTOPSIG(status) == signal.SIGTRAP else os.WSTOPSIG(status))

        def receive(self):
            while b'\n' not in self.pending:
                self.trace()
                if not select.select([self.proc.stdout], [], [], min(.005, remaining()))[0]: continue
                raw = os.read(self.proc.stdout.fileno(), 65536); assert raw, ('probe EOF', self.proc.poll())
                self.pending += raw; assert len(self.pending) <= 65536
            raw, self.pending = self.pending.split(b'\n', 1)
            return json.loads(raw)

        def call(self, op, **args):
            request = dict(op=op, **args); raw = encoded(request)+b'\n'; assert len(raw) <= 65536
            assert self.proc.stdin.write(raw) == len(raw); self.proc.stdin.flush()
            response = self.receive(); self.row['events'].append(dict(request=request, response=response)); return response

        def child(self, pid, role, inspect=True):
            while pid not in self.executed:
                self.trace(); remaining(); time.sleep(.002)
            assert pid > 0 and pid in self.executed and self.executed[pid]['role'] == role, (pid, role, self.executed)
            return self.children[pid]

        def exited(self, pid):
            assert select.select([self.children[pid]], [], [], remaining())[0], ('child survived', pid)
            for row in self.row['children']:
                if row['pid'] == pid: row['observed_exited'] = True

        def drain(self, op, state):
            while True:
                value = self.call(op)
                assert 'error' not in value or not value['error'] or state in ('unavailable', 'closed'), value
                if value['state'] == state and value['reaped']: return value
                assert value['state'] not in ('failed', 'unavailable') or value['state'] == state, value
                time.sleep(.002)

        def close(self, success=False):
            if self.closed: return
            try:
                if success and self.proc.poll() is None:
                    assert self.call('quit') == {'exit': True}
                    assert self.proc.wait(timeout=remaining()) == 0
            finally:
                if self.proc.poll() is None:
                    signal.pidfd_send_signal(self.pidfd, signal.SIGKILL); self.proc.wait(timeout=5)
                for pid, fd in self.children.items():
                    if not select.select([fd], [], [], 0)[0]:
                        self.row.setdefault('forced_cleanup', []).append(pid)
                        signal.pidfd_send_signal(fd, signal.SIGKILL)
                    if pid in self.traced:
                        # A failed exec observation can leave a ptrace stop before
                        # parent-death protection is armed. Reap that exact tracee.
                        os.waitpid(pid, 0x40000000); self.traced.remove(pid)
                    assert select.select([fd], [], [], 5)[0], ('child survived cleanup', pid)
                    os.close(fd)
                os.close(self.pidfd); self.closed = True
                self.row['exit'] = self.proc.returncode
                self.row['stderr'] = self.proc.stderr.read().decode('utf-8', 'replace')
                self.proc.stdin.close(); self.proc.stdout.close(); self.proc.stderr.close(); save()
                if success: assert not self.row['stderr'] and not self.row.get('forced_cleanup'), self.row

        def __enter__(self): return self
        def __exit__(self, kind, *rest): self.close(kind is None)

    def refused(code, mode='bundle'):
        with Run(mode, good=False) as run:
            assert run.initial == {'error': code}, run.initial
            assert run.proc.wait(timeout=remaining()) == 2

    @contextmanager
    def replacement(path, raw):
        old = path.read_bytes(); mode = path.stat().st_mode & 0o777
        try:
            write(path, raw, mode); capture('replace:'+path.name); yield
        finally: write(path, old, mode)

    def recovery_root(name):
        path = folder/name; path.mkdir(mode=0o700); write(path/'draft.json', RECORDS['old']); return path

    def recovery_child(run):
        state = run.call('recovery-poll'); assert state['pid'] > 0 and not state['reaped'], state
        run.child(state['pid'], 2); return state['pid']

    def loaded(run, path, expected):
        assert run.call('recovery', directory=str(path))['state'] == 'loading'
        pid = recovery_child(run); run.drain('recovery-poll', 'ready'); run.exited(pid)
        assert run.call('recovery-take') == dict(operation='load', outcome='loaded', error='', bytes=expected.decode(), digest=sha(expected), pending=False)
        assert run.call('recovery-take') is None; check_file(path/'draft.json', expected)

    def alarm(*unused): raise TimeoutError('fixed native case deadline')
    previous_alarm = signal.signal(signal.SIGALRM, alarm)
    try:
        with case('RELOCATE'):
            expected = dict(format='SysPane.Helpers', schema_version='0.2.0', target_profile='linux-x64-gcc13', product_version='0.0.1', helpers={})
            for role, name, raw in zip(CASES['roles'], NAMES, raw_helpers):
                expected['helpers'][role] = dict(path='libexec/syspane/'+name, sha256=sha(raw), bytes=str(len(raw)), imports=IMAGE_IMPORTS if role == 'image_worker' else BASE_IMPORTS)
            assert raw_record == encoded(expected)
            old = {k: v for k, v in expected.items() if k != 'helpers'}; old.update(schema_version='0.1.0', configuration_host=expected['helpers']['configuration_host'])
            assert old_record == encoded(old)
            module = importlib.util.spec_from_file_location('bundle_generator', ROOT/'source/build/generate_helper_identity.py')
            generator = importlib.util.module_from_spec(module); module.loader.exec_module(generator)
            generated, header = generator.generate(config, 'linux-x64-gcc13')
            old_header = ('#pragma once\n#include "installation_linux.hpp"\nnamespace syspane::platform {\ninline HelperExpectation built_helper_expectation(){return {"'+sha(old_record)+'","'+sha(raw_helpers[0])+'",'+str(len(raw_helpers[0]))+'};}\n}\n').encode()
            assert generated == old_record and header == old_header == (legacy_record.parent/'helper_identity.hpp').read_bytes()
            generated, header = generator.generate(config, 'linux-x64-gcc13', image_worker, recovery_worker)
            assert generated == raw_record and header == (bundle_record.parent/'bundle_identity.hpp').read_bytes()
            for image_arg, recovery_arg in [(image_worker, None), (None, recovery_worker), (config, recovery_worker), (image_worker, image_worker)]:
                try: generator.generate(config, 'linux-x64-gcc13', image_arg, recovery_arg)
                except ValueError: pass
                else: raise AssertionError('invalid generator input admitted')
            capture('baseline-relocated')
            with Run(): pass
        with case('SEALED-ROLES'):
            with Run() as run:
                assert [v['role'] for v in run.initial['roles']] == [0, 1, 2]
                for value in run.initial['roles']:
                    role = value['role']; path = Path('/proc', str(run.proc.pid), 'fd', str(value['fd']))
                    assert os.readlink(path).startswith('/memfd:'+NAMES[role])
                    assert value['seals'] & 15 == 15 and value['write'] == -1 and value['write_errno'] == errno.EPERM
                    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
                    try:
                        assert stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_size == len(raw_helpers[role])
                        assert fcntl.fcntl(fd, fcntl.F_GET_SEALS) & 15 == 15 and sha(path.read_bytes()) == sha(raw_helpers[role])
                        try: writable = os.open(path, os.O_WRONLY | os.O_CLOEXEC)
                        except OSError as exc: assert exc.errno == errno.EACCES
                        else:
                            os.close(writable); raise AssertionError('read-only sealed helper admitted external write access')
                    finally: os.close(fd)
        with case('IMAGE-PIXELS'):
            with Run() as run:
                for name in CASES['images']:
                    expected = PIXELS[name]; pid = run.call('image', media=expected['media'], file=str(ROOT/'tests/scene/image-cases'/name))['pid']
                    run.child(pid, 1); run.drain('image-poll', 'ready'); run.exited(pid); check_pixels(run.call('image-take'), expected)
        with case('IMAGE-INVALID'):
            with Run() as run:
                pid = run.call('image', media='image/png', file=str(ROOT/'tests/scene/image-cases'/CASES['invalid_image']))['pid']
                run.child(pid, 1); value = run.drain('image-poll', 'failed'); run.exited(pid)
                assert value['reason'] == 'image.decode' and run.call('image-take') == {'error': 'image.not_ready'}
                assert run.call('image-reset') == {'closed': True}
        with case('IMAGE-SANDBOX'):
            with Run() as run:
                pid = run.call('sandbox')['pid']; run.child(pid, 1, inspect=False)
                assert run.call('raw-finish') == dict(pid=pid, signaled=False, code=0, output=b'sandbox.pass\n'.hex(), stderr='')
                run.exited(pid)
        with case('RECOVERY'):
            path = recovery_root('recovery'); new = folder/'new.input'; write(new, RECORDS['new'])
            with Run() as run:
                loaded(run, path, RECORDS['old'])
                assert run.call('replace', file=str(new)) == {'ticket': 2}
                pid = recovery_child(run); run.drain('recovery-poll', 'ready'); run.exited(pid)
                assert run.call('recovery-take') == dict(operation='replace', outcome='durable', error='', bytes=None, digest=sha(RECORDS['new']), pending=False)
                check_file(path/'draft.json', RECORDS['new']); run.call('recovery-reset')
                loaded(run, path, RECORDS['new']); assert run.call('retire') == {'ticket': 2}
                pid = recovery_child(run); run.drain('recovery-poll', 'retired'); run.exited(pid)
                assert run.call('recovery-take') == dict(operation='retire', outcome='durable', error='', bytes=None, digest=None, pending=False)
                check_file(path/'draft.json', None)
                # SP-W10-RECOVERY-STORE retains the empty coordination lock.
                assert {p.name for p in path.iterdir()} == {'.writer'}
                check_file(path/'.writer', b''); lock = (path/'.writer').lstat()
                assert stat.S_ISREG(lock.st_mode) and stat.S_IMODE(lock.st_mode) == 0o600 and lock.st_nlink == 1 and lock.st_uid == os.geteuid()
                run.call('recovery-reset')
        with case('RECOVERY-CANCEL'):
            path = recovery_root('cancel')
            with Run() as run:
                run.call('recovery', directory=str(path)); pid = recovery_child(run); run.call('recovery-close')
                run.drain('recovery-poll', 'closed'); run.exited(pid); assert run.call('recovery-take') is None
                check_file(path/'draft.json', RECORDS['old']); run.call('recovery-reset')
        with case('MISSING-ROLES'):
            for path in installed:
                held = path.with_name(path.name+'.held'); path.rename(held)
                try: capture('missing:'+path.name); refused('installation.path')
                finally: held.rename(path)
        with case('MODIFIED-ROLES'):
            for path, raw in zip(installed, raw_helpers):
                changed = raw[:-1]+bytes([raw[-1]^1])
                with replacement(path, changed): refused('installation.helper_digest')
        with case('SWAPPED-ROLES'):
            for i, path in enumerate(installed):
                with replacement(path, raw_helpers[(i+1)%3]): refused('installation.size')
        with case('LINKED-ROLES'):
            for path in installed:
                held = path.with_name(path.name+'.held'); path.rename(held)
                try:
                    for kind in ('symbolic', 'hard'):
                        if kind == 'symbolic': path.symlink_to(held)
                        else: os.link(held, path)
                        try: capture(kind+':'+path.name); refused('installation.path')
                        finally: path.unlink()
                finally: held.rename(path)
        with case('UNSAFE-MODES'):
            for path in installed:
                for mode, error in [(0o777, 'installation.path'), (0o644, 'installation.executable_mode')]:
                    try: path.chmod(mode); capture('mode:'+path.name+':'+oct(mode)); refused(error)
                    finally: path.chmod(0o755)
        with case('MANIFEST'):
            documents = []
            for field, value in [('unknown', True), ('schema_version', '0.1.0'), ('target_profile', 'windows-x64-gcc15')]:
                doc = json.loads(raw_record); doc[field] = value; documents.append(encoded(doc))
            for role in CASES['roles']:
                doc = json.loads(raw_record); del doc['helpers'][role]; documents.append(encoded(doc))
            documents.append(b'{')
            for raw in documents:
                with replacement(record, raw): refused('installation.record_digest')
        with case('FORGED-CLOSURE'):
            for i, path in enumerate(installed):
                raw = raw_helpers[i][:-1]+bytes([raw_helpers[i][-1]^1]); doc = json.loads(raw_record)
                doc['helpers'][CASES['roles'][i]].update(sha256=sha(raw), bytes=str(len(raw)))
                with replacement(path, raw), replacement(record, encoded(doc)): refused('installation.record_digest')
        with case('ROLE-AND-THREAD'):
            with Run() as run:
                assert run.call('verify', role=999) == {'error': 'installation.helper_role'}
                assert run.call('verify', role=-1) == {'error': 'installation.helper_role'}
                assert run.call('thread') == {'refused': 3}
                assert 'fd' in run.call('verify', role=0)
            refused('installation.record_digest', 'legacy')
            with replacement(record, old_record):
                refused('installation.record_digest')
                with Run('legacy') as run:
                    assert len(run.initial['roles']) == 1 and 'fd' in run.call('verify', role=0)
                    for role in (1, 2): assert run.call('verify', role=role) == {'error': 'installation.helper_role'}
        with case('CROSS-ROLE-INVALIDATION'):
            for role in (1, 2):
                with Run() as run:
                    with replacement(installed[role], raw_helpers[role]+b'X'):
                        assert run.call('verify', role=0) == {'error': 'installation.changed'}
                    assert run.call('verify', role=0) == {'error': 'installation.invalidated'}
        with case('LAUNCH-AFTER-CHANGE'):
            with Run() as run:
                with replacement(installed[0], raw_helpers[0]+b'X'):
                    assert run.call('image', media='image/png', file=str(ROOT/'tests/scene/image-cases/rgba.png')) == {'error': 'installation.changed'}
                    assert not Path('/proc', str(run.proc.pid), 'task', str(run.proc.pid), 'children').read_text().strip()
            path = recovery_root('changed-recovery')
            with Run() as run:
                loaded(run, path, RECORDS['old'])
                with replacement(installed[0], raw_helpers[0]+b'X'):
                    assert run.call('replace', file=str(new)) == {'ticket': 2}
                    value = run.drain('recovery-poll', 'unavailable')
                    assert value['pid'] == 0 and value['error'] == 'recovery_queue.failure'
                    assert run.call('recovery-take') == dict(operation='replace', outcome='unknown', error='recovery_queue.failure', bytes=None, digest=None, pending=False)
                    assert run.call('verify', role=2) == {'error': 'installation.invalidated'}
                    assert not Path('/proc', str(run.proc.pid), 'task', str(run.proc.pid), 'children').read_text().strip()
                    check_file(path/'draft.json', RECORDS['old'])
                run.call('recovery-reset')
        with case('BORROWED-IMAGE'):
            with Run() as run:
                with replacement(installed[1], raw_helpers[2]):
                    pid = run.call('raw-image')['pid']; run.child(pid, 1)
                    value = run.call('raw-finish', file=str(ROOT/'tests/scene/image-cases/rgba.png')); run.exited(pid)
                    expected = PIXELS['rgba.png']; raw = b'SPIM0001'+struct.pack('!II', *expected['size'])+bytes(expected['rgba'])
                    assert value == dict(pid=pid, signaled=False, code=0, output=raw.hex(), stderr='')
                    assert run.call('verify', role=1) == {'error': 'installation.changed'}
        with case('PARENT-LOSS'):
            with Run() as run:
                pid = run.call('raw-image')['pid']; fd = run.child(pid, 1)
                while '\nSeccomp:\t2\n' not in Path('/proc', str(pid), 'status').read_text():
                    assert not select.select([fd], [], [], 0)[0]; remaining(); time.sleep(.002)
                assert not select.select([fd], [], [], 0)[0]
                signal.pidfd_send_signal(run.pidfd, signal.SIGKILL)
                assert run.proc.wait(timeout=remaining()) == -signal.SIGKILL; run.exited(pid)
        with case('ORACLE'):
            expected = PIXELS['rgba.png']; actual = dict(width=expected['size'][0], height=expected['size'][1], rgba=list(expected['rgba']))
            check_pixels(actual, expected); actual['rgba'][0] ^= 1
            faults = []
            for check in (lambda: check_pixels(actual, expected), lambda: check_file(folder/'cancel/draft.json', RECORDS['new'])):
                try: check()
                except AssertionError as exc: faults.append(repr(exc))
                else: raise AssertionError('incorrect oracle expectation passed')
            report['oracle_calibration'] = faults; assert len(faults) == 2
        assert [v['case'] for v in report['cases']] == CASES['cases']
        capture('restored-baseline'); report['outcome'] = 'pass'
    except BaseException as exc:
        report['error'] = repr(exc); report['traceback'] = traceback.format_exc(); raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0); signal.signal(signal.SIGALRM, previous_alarm)
        for run in runs: run.close()
        report['seconds'] = time.monotonic()-started; report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['files'] = {p.relative_to(folder).as_posix(): sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file() and not p.is_symlink() and p.name != 'result.json'}
        save(); print(folder/'result.json', report['outcome'])


if __name__ == '__main__': main()

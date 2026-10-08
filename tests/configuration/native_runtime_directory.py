"""Independent filesystem, lock and exact-child oracle for frontend runtime roots."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import select
import signal
import stat
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/runtime-directory-cases.json').read_bytes())
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    probe, helper, evidence = [Path(v).resolve() for v in sys.argv[1:4]]
    build = probe.parent
    assert os.geteuid() and helper.parent == build == evidence.parent
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile'] == 'linux-x64-gcc13'
    campaign = build.parent
    base = campaign/'R'
    marker = encoded(dict(format='SysPane.RuntimeDirectoryLab', schema_version='0.1.0', root=str(campaign)))
    if not base.exists():
        base.mkdir(mode=0o700)
        (base/'.owner.json').write_bytes(marker)
    assert not base.is_symlink() and base.stat().st_uid == os.geteuid() and stat.S_IMODE(base.stat().st_mode) == 0o700
    assert (base/'.owner.json').read_bytes() == marker and len(str(base).encode()) <= 50
    folder = evidence/('runtime-'+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700)
    report = dict(family=CASES['family'], outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
                  uid=os.geteuid(), kernel=list(os.uname()), runtime_base=str(base), cases=[], runs=[], snapshots=[],
                  oracle_sha256=sha(Path(__file__).read_bytes()), artifacts={p.name: sha(p.read_bytes()) for p in (probe, helper)})
    peers = []

    def save(): (folder/'result.json').write_bytes(encoded(report))

    def passed(case, **facts):
        assert case in CASES['cases'] and case not in [r['case'] for r in report['cases']]
        report['cases'].append(dict(case=case, outcome='pass', **facts)); save()

    def snapshot(path):
        nodes = {}
        for p in [path, *sorted(path.rglob('*'))]:
            assert len(nodes) < 128
            v = p.lstat(); row = dict(device=v.st_dev, inode=v.st_ino, mode=v.st_mode, uid=v.st_uid, nlink=v.st_nlink)
            if stat.S_ISREG(v.st_mode):
                assert v.st_size <= 4096
                raw = p.read_bytes(); row.update(bytes=len(raw), hex=raw.hex(), sha256=sha(raw))
            elif stat.S_ISLNK(v.st_mode): row['target'] = os.readlink(p)
            nodes[str(p)] = row
        report['snapshots'].append(nodes); save(); return nodes

    def empty_root(path):
        v = path.lstat()
        assert stat.S_ISDIR(v.st_mode) and v.st_uid == os.geteuid() and stat.S_IMODE(v.st_mode) == 0o700
        assert path.parent == base and re.fullmatch('sp-[0-9a-f]{16}', path.name) and len(str(path).encode()) <= 70
        assert not list(path.iterdir())
        return (v.st_dev, v.st_ino)

    class Peer:
        def __init__(self, selected=base, mask=0o077):
            self.process = subprocess.Popen([str(probe)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.pidfd = os.pidfd_open(self.process.pid); self.pending = b''; self.lines = []
            self.row = dict(pid=self.process.pid, base=str(selected), umask=mask, replies=self.lines)
            report['runs'].append(self.row); peers.append(self)
            self.send(dict(base=str(selected), umask=mask)); self.first = self.receive()
            self.path = Path(self.first['path']) if 'path' in self.first else None
            assert self.first['umask_unchanged']
        def send(self, value):
            self.process.stdin.write(encoded(value)+b'\n'); self.process.stdin.flush()
        def receive(self, timeout=8):
            stop = time.monotonic()+timeout
            while b'\n' not in self.pending:
                remaining = stop-time.monotonic(); assert remaining > 0, 'probe reply timeout'
                assert select.select([self.process.stdout], [], [], remaining)[0], 'probe reply timeout'
                raw = os.read(self.process.stdout.fileno(), 4096)
                assert raw, ('probe EOF', self.process.poll())
                self.pending += raw; assert len(self.pending) <= 8192
            raw, self.pending = self.pending.split(b'\n', 1); value = json.loads(raw)
            self.lines.append(value); save(); return value
        def call(self, op, **kw): self.send(dict(op=op, **kw)); return self.receive()
        def stopped(self, expected=0):
            assert self.process.wait(timeout=8) == expected
            assert select.select([self.pidfd], [], [], 0)[0]
            self.row.update(exit=self.process.returncode, stderr=self.process.stderr.read().decode())
            assert not self.row['stderr']; save()
        def close(self):
            if self.process.poll() is None: assert self.call('destroy') == {'event': 'destroyed'}
            self.stopped()

    def refusal(selected, error=None, mask=0o077):
        before = set(base.iterdir()); p = Peer(selected, mask)
        assert p.first['ok'] is False
        if error: assert p.first['error'] == error, p.first
        p.stopped()
        if mask == 0o077: assert set(base.iterdir()) == before
        return p

    try:
        p = Peer(); identity = empty_root(p.path); snapshot(p.path)
        assert p.call('cleanup') == {'ok': True} and not p.path.exists()
        assert p.call('cleanup') == {'ok': True}
        assert p.call('path')['error'] == 'runtime.closed'; p.close(); passed('CREATE', identity=identity)

        a, b = Peer(), Peer(); assert a.path != b.path and empty_root(a.path) != empty_root(b.path)
        assert a.call('cleanup')['ok']; empty_root(b.path); assert b.call('cleanup')['ok']; a.close(); b.close(); passed('PARALLEL')

        for value in ('', '/', 'relative', str(base)+'/', str(base)+'//x', str(base)+'/./x', str(base)+'/../x', '/'+('a'*50), str(base)+'\0'):
            refusal(value, 'runtime.path')
        passed('INPUT')

        saved = folder/'symlink-target'; assert saved.parent == folder and base.parent == campaign
        base.rename(saved); base.symlink_to(saved, target_is_directory=True)
        try:
            before = snapshot(saved); refusal(base, 'runtime.path'); assert snapshot(saved) == before
        finally: base.unlink(); saved.rename(base)
        passed('SYMLINK')

        base.chmod(0o750)
        try: refusal(base, 'runtime.permissions'); assert stat.S_IMODE(base.stat().st_mode) == 0o750
        finally: base.chmod(0o700)
        assert stat.S_IMODE(Path('/tmp').stat().st_mode) & 0o022
        refusal('/tmp', 'runtime.path')
        before = set(base.iterdir()); refusal(base, mask=0o777)
        for path in set(base.iterdir())-before:
            assert path.name.startswith('sp-') and stat.S_IMODE(path.stat().st_mode) == 0
            original = snapshot(path)
            # The failed product owner did not repair its node. After preserving
            # that fact, the independent lab restores read access for accounting
            # and verifies the exact orphan is empty; nothing is deleted.
            identity = (path.stat().st_dev, path.stat().st_ino)
            path.chmod(0o700)
            assert (path.stat().st_dev, path.stat().st_ino) == identity and not list(path.iterdir())
            report.setdefault('lab_access_restorations', []).append(dict(path=str(path), before=original, after=snapshot(path)))
        passed('PERMISSIONS')

        mounted = ROOT/'out'; before = set(mounted.iterdir()); refusal(mounted)
        assert set(mounted.iterdir()) == before
        passed('FILESYSTEM', observed_type=subprocess.check_output(['stat', '-f', '-c', '%T', mounted], text=True).strip())

        p = Peer(); fd = os.open(p.path, os.O_RDONLY | os.O_DIRECTORY); fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            assert p.call('cleanup')['error'] == 'runtime.busy'; empty_root(p.path)
            assert p.call('path')['path'] == str(p.path)
        finally: os.close(fd)
        assert p.call('cleanup')['ok']; p.close(); passed('BUSY')

        for kind in ('file', 'symlink', 'directory'):
            p = Peer(); foreign = p.path/'foreign'
            if kind == 'file': foreign.write_bytes(b'independent public fixture\n')
            elif kind == 'symlink': foreign.symlink_to(folder)
            else: foreign.mkdir(mode=0o700)
            before = snapshot(p.path); assert p.call('cleanup')['error'] == 'runtime.contents'
            assert snapshot(p.path) == before
            retained = folder/('foreign-'+kind); foreign.rename(retained)
            assert p.call('cleanup')['error'] == 'runtime.invalidated'; p.close(); snapshot(p.path)
        passed('CONTENTS')

        for kind in ('leaf', 'ancestor', 'mode'):
            p = Peer(); original = p.path; moved = folder/('replaced-'+kind)
            if kind == 'leaf': original.rename(moved); original.mkdir(mode=0o700)
            elif kind == 'ancestor': base.rename(moved); base.mkdir(mode=0o700)
            else: original.chmod(0o750)
            target = base if kind == 'ancestor' else original
            before = snapshot(target); assert p.call('path')['error'] == 'runtime.changed'; assert snapshot(target) == before
            if kind == 'leaf': original.rename(folder/'replacement-leaf'); moved.rename(original)
            elif kind == 'ancestor': base.rename(folder/'replacement-base'); moved.rename(base)
            else: original.chmod(0o700)
            assert p.call('cleanup')['error'] == 'runtime.invalidated'; p.close(); snapshot(original)
        passed('REPLACEMENT')

        p = Peer(); assert p.call('owner')['errors'] == ['runtime.owner', 'runtime.owner']
        empty_root(p.path); assert p.call('cleanup')['ok']; p.close(); passed('OWNER')

        a = Peer(); first = empty_root(a.path); a.close(); assert empty_root(a.path) == first
        b = Peer(); second = empty_root(b.path); os.kill(b.process.pid, signal.SIGKILL); b.stopped(-signal.SIGKILL)
        assert empty_root(b.path) == second
        c = Peer(); assert c.path not in (a.path, b.path); assert c.call('cleanup')['ok']; c.close()
        snapshot(a.path); snapshot(b.path); passed('ORPHAN')

        installed = folder/'helper'; installed.write_bytes(helper.read_bytes()); installed.chmod(0o700)
        for case, mode in (('SUPERVISOR', 'healthy'), ('FORCED', 'blocked-close')):
            (folder/'helper.fixture').write_bytes(encoded(dict(mode=mode)))
            p = Peer(); p.send(dict(op='supervise', helper=str(installed), profile=str(folder/('profile-'+case))))
            ready = p.receive(); assert ready['event'] == 'ready' and ready['cleanup'] == 'runtime.busy'
            child = os.pidfd_open(ready['pid']); assert not select.select([child], [], [], 0)[0]
            try:
                assert p.path.exists(); p.send(dict(op='proceed')); closed = p.receive()
                assert closed['event'] == 'closed' and closed['cleanup'] == 'runtime.busy'
                assert select.select([child], [], [], 1)[0], 'closed without independent native exit'
                assert closed['signaled'] == (case == 'FORCED') and closed['code'] == (9 if case == 'FORCED' else 0)
                if case == 'FORCED': assert 2000 <= closed['elapsed_ms'] < 6000
                assert p.receive() == {'event': 'retired'} and not p.path.exists()
                passed(case, pid=ready['pid'], exit=closed)
            finally: os.close(child)
            p.close()

        p = Peer(); (p.path/'must-survive').write_bytes(b'oracle control\n')
        detected = False
        try: empty_root(p.path)
        except AssertionError: detected = True
        assert detected; assert p.call('cleanup')['error'] == 'runtime.contents'; snapshot(p.path); p.close(); passed('ORACLE')
        assert set(CASES['cases']) == {r['case'] for r in report['cases']}
        report['outcome'] = 'pass'
    except Exception:
        report['failure'] = traceback.format_exc(); raise
    finally:
        for peer in peers:
            if peer.process.poll() is None:
                peer.process.kill(); peer.process.wait(timeout=8)
            peer.process.stdin.close(); peer.process.stdout.close(); peer.process.stderr.close(); os.close(peer.pidfd)
        report['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json', flush=True)


if __name__ == '__main__': main()

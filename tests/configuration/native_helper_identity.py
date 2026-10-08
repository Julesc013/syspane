"""Offline relocation, compiled-anchor, mutation and kernel-executable oracle."""
from datetime import datetime, timezone
from pathlib import Path
import errno
import hashlib
import json
import os
import select
import signal
import socket
import stat
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'tests/configuration/helper-identity-cases.json').read_bytes())
encoded = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    probe, helper, record_file, evidence = [Path(p).resolve() for p in sys.argv[1:5]]
    assert os.geteuid() and evidence.parent == probe.parent == helper.parent
    assert json.loads((probe.parent/'.syspane-owner.json').read_bytes())['profile'] == 'linux-x64-gcc13'
    folder = evidence/('hi-'+uuid.uuid4().hex[:10]); folder.mkdir(mode=0o700, parents=True)
    runtime = probe.parent.parent/('h-'+uuid.uuid4().hex[:8]); runtime.mkdir(mode=0o700)
    (runtime/'owner.json').write_bytes(encoded(dict(owner='HELPER-IDENTITY', evidence=str(folder))))
    private_runtime = runtime/'r'; private_runtime.mkdir(mode=0o700)
    image = folder/'image'; unrelated = folder/'cwd'; unrelated.mkdir(mode=0o700)
    expected_record = record_file.read_bytes(); document = json.loads(expected_record)
    helper_bytes, probe_bytes = helper.read_bytes(), probe.read_bytes()
    entries = {'bin/syspane': probe_bytes, 'libexec/syspane/syspane-configuration-host': helper_bytes,
               'share/syspane/helpers.json': expected_record,
               'README.txt': b'Local installation-identity experiment. bin/syspane is a test application. Not a desktop edition or public release.\n'}
    archive = folder/'syspane-0.0.1-linux-x64-gcc13-configuration-development.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)); info.create_system = 3
            info.external_attr = (0o100755 if name.startswith(('bin/', 'libexec/')) else 0o100644)<<16
            info.compress_type = zipfile.ZIP_DEFLATED; z.writestr(info, raw)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == set(entries) and len(z.namelist()) == 4
        for name in entries:
            raw = z.read(name); assert raw == entries[name]
            destination = image/name; destination.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            destination.write_bytes(raw); destination.chmod(z.getinfo(name).external_attr>>16 & 0o777)
    original = image; relocated = folder/'relocated image'
    assert original.resolve().parent == relocated.resolve().parent == folder
    original.rename(relocated); image = relocated
    application = image/'bin/syspane'; installed_helper = image/'libexec/syspane/syspane-configuration-host'; installed_record = image/'share/syspane/helpers.json'
    report = dict(family=CASES['family'], outcome='fail', started_at=datetime.now(timezone.utc).isoformat(),
                  uid=os.geteuid(), kernel=list(os.uname()), artifacts={probe.name: sha(probe_bytes), helper.name: sha(helper_bytes)},
                  expected_record_sha256=sha(expected_record), package_sha256=sha(archive.read_bytes()),
                  oracle_sha256=sha(Path(__file__).read_bytes()), runtime_directory=str(runtime), cases=[], runs=[])

    def save(): (folder/'result.json').write_bytes(encoded(report))

    def passed(name, **facts):
        assert name in CASES['cases'] and name not in [v['case'] for v in report['cases']]
        report['cases'].append(dict(case=name, outcome='pass', **facts)); save()

    baseline = {sha(raw): name for name, raw in entries.items()}
    mutations = folder/'mutations'; mutations.mkdir(mode=0o700)

    def capture():
        # Preserve exact inputs before cleanup restores the reusable test image.
        # Baseline bytes are already in the fixed archive; unique mutations have
        # separate compressed blobs. Native identities/modes are never normalized.
        nodes = {}
        for root in (image, folder/'moved image'):
            if not root.exists(): continue
            for path in [root, *sorted(root.rglob('*'))]:
                assert len(nodes) < 32
                info = path.lstat(); row = dict(mode=info.st_mode, uid=info.st_uid, gid=info.st_gid,
                    device=info.st_dev, inode=info.st_ino, nlink=info.st_nlink, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)
                if stat.S_ISREG(info.st_mode):
                    assert info.st_size <= 67108864
                    raw = path.read_bytes(); digest = sha(raw); row.update(sha256=digest, bytes=len(raw))
                    if digest in baseline: row['baseline_member'] = baseline[digest]
                    else:
                        blob = mutations/(digest+'.z')
                        if not blob.exists(): blob.write_bytes(zlib.compress(raw))
                        assert sha(zlib.decompress(blob.read_bytes())) == digest
                        row['mutation_blob'] = blob.relative_to(folder).as_posix()
                elif stat.S_ISLNK(info.st_mode): row['target'] = os.readlink(path)
                else: assert stat.S_ISDIR(info.st_mode)
                nodes[path.relative_to(folder).as_posix()] = row
        return nodes

    class Run:
        def __init__(self, mode='check', spoof=False):
            env = dict(os.environ, PATH='/nonexistent', SYSPANE_HELPER=str(unrelated/'evil'), SYSPANE_INSTALL_ROOT=str(unrelated))
            env.pop('LD_PRELOAD', None); env.pop('LD_LIBRARY_PATH', None)
            args = ['unrelated-program' if spoof else str(application), mode]
            if mode == 'supervisor': args += [str(private_runtime), str(folder/'profile')]
            self.process = subprocess.Popen(args, executable=str(application), cwd=unrelated, env=env,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            self.events = []; self.pending = b''; self.eof = False; self.children = {}
            self.row = dict(pid=self.process.pid, mode=mode, spoof=spoof, events=self.events, images=[capture()]); report['runs'].append(self.row)

        def pump(self):
            if select.select([self.process.stdout], [], [], .02)[0]:
                raw = os.read(self.process.stdout.fileno(), 65536); self.eof = not raw; self.pending += raw
            while b'\n' in self.pending:
                raw, self.pending = self.pending.split(b'\n', 1); self.events.append(json.loads(raw))
            save()

        def event(self, name, timeout=15):
            end = time.monotonic()+timeout
            while time.monotonic() < end:
                self.pump()
                for event in self.events:
                    if event['event'] == name: return event
                assert not self.eof, self.events
            raise AssertionError(('observation timeout', self.events))

        def send(self, text):
            self.row['images'].append(capture()); save()
            self.process.stdin.write((text+'\n').encode()); self.process.stdin.flush()

        def verified(self):
            value = self.event('verified')
            assert value['root'] == str(image) and value['record'] == sha(expected_record) and value['helper'] == sha(helper_bytes)
            assert value['bytes'] == len(helper_bytes) and value['seals'] & 15 == 15
            assert value['write'] == -1 and value['write_errno'] == errno.EPERM
            return value

        def observe_child(self):
            value = self.event('launched'); pid = value['pid']; fd = os.pidfd_open(pid); self.children[pid] = fd
            assert '\nPPid:\t'+str(self.process.pid)+'\n' in Path('/proc', str(pid), 'status').read_text()
            link = os.readlink('/proc/'+str(pid)+'/exe'); assert link.startswith('/memfd:syspane-configuration-host')
            actual = Path('/proc', str(pid), 'exe').read_bytes(); assert sha(actual) == sha(helper_bytes)
            self.row['observed_child'] = dict(pid=pid, executable=link, sha256=sha(actual)); save(); return pid, fd

        def finish_child(self):
            pid, fd = self.observe_child(); self.send('finish'); result = self.event('exited')
            assert result == dict(event='exited', pid=pid, signaled=False, code=2, stderr='controller.startup\n')
            assert select.select([fd], [], [], 0)[0]; return result

        def error(self, code):
            value = self.event('error'); assert value['code'] == code, value
            assert self.process.wait(timeout=2) == 2

        def __enter__(self): return self
        def __exit__(self, *error):
            try:
                if error[0] is None: self.row['exit'] = self.process.wait(timeout=3)
            finally:
                if self.process.poll() is None: self.process.kill(); self.process.wait(timeout=3)
                for fd in self.children.values():
                    assert select.select([fd], [], [], 3)[0]; os.close(fd)
                self.row['exit'] = self.process.returncode
                self.row['stderr'] = self.process.stderr.read().decode('utf-8', 'replace'); save()

    def refused(code, **options):
        with Run(**options) as run: run.error(code)

    def replace_file(path, raw, expected_error):
        before = path.read_bytes(); mode = path.stat().st_mode & 0o777
        try:
            path.write_bytes(raw); path.chmod(mode); refused(expected_error)
        finally: path.write_bytes(before); path.chmod(mode)

    try:
        assert document['configuration_host']['sha256'] == sha(helper_bytes) and document['configuration_host']['bytes'] == str(len(helper_bytes))
        with Run() as run: run.verified()
        passed('relocated-package-and-compiled-closure', package_sha256=sha(archive.read_bytes()))
        with Run(spoof=True) as run: run.verified()
        passed('cwd-argv-path-environment-ignored')
        with Run('hold') as run:
            run.verified(); run.send('launch'); run.finish_child()
        passed('immutable-helper-and-exact-native-execution')
        with Run('supervisor') as run:
            run.verified(); pid, fd = run.observe_child(); run.send('continue'); stopped = run.event('reaped')
            assert stopped['pid'] == pid and stopped['code'] == 2 and select.select([fd], [], [], 0)[0]
            run.event('closed'); assert not list(private_runtime.iterdir())
        passed('supervisor-uses-verified-helper')
        for path, case in [(installed_helper, 'missing-helper-refused'), (installed_record, 'missing-record-refused')]:
            temporary = path.with_name(path.name+'.held'); path.rename(temporary)
            try: refused('installation.path'); passed(case)
            finally: temporary.rename(path)
        changed = bytearray(helper_bytes); changed[-1] ^= 1
        replace_file(installed_helper, changed, 'installation.helper_digest'); passed('modified-helper-refused')
        replace_file(installed_record, expected_record+b' ', 'installation.record_digest'); passed('modified-record-refused')
        forged = json.loads(expected_record); forged['configuration_host']['sha256'] = sha(changed)
        installed_helper.write_bytes(changed)
        try: replace_file(installed_record, encoded(forged), 'installation.record_digest'); passed('self-consistent-forgery-refused')
        finally: installed_helper.write_bytes(helper_bytes)
        wrong = json.loads(expected_record); wrong['target_profile'] = 'windows-x64-gcc15'
        replace_file(installed_record, encoded(wrong), 'installation.record_digest'); passed('wrong-target-refused')
        temporary = installed_helper.with_name('held-helper'); installed_helper.rename(temporary)
        try:
            installed_helper.symlink_to(temporary); refused('installation.path'); passed('symlink-refused'); installed_helper.unlink()
            os.link(temporary, installed_helper); refused('installation.path'); passed('hardlink-refused'); installed_helper.unlink()
        finally:
            if installed_helper.is_symlink() or installed_helper.exists(): installed_helper.unlink()
            temporary.rename(installed_helper)
        for mode, reason in ((0o777, 'installation.path'), (0o4755, 'installation.path'),
                             (0o644, 'installation.executable_mode'), (0o401, 'installation.access')):
            installed_helper.chmod(mode)
            try: refused(reason)
            finally: installed_helper.chmod(0o755)
        passed('unsafe-modes-refused')
        image.chmod(0o777)
        try: refused('installation.path'); passed('unsafe-ancestor-refused')
        finally: image.chmod(0o755)
        with Run('hold') as run:
            run.verified(); old = application.with_name('old-syspane'); application.rename(old); application.write_bytes(b'replacement'); application.chmod(0o755)
            try: run.send('verify'); run.error('installation.executable_changed'); passed('current-executable-replacement-refused')
            finally: application.unlink(); old.rename(application)
        with Run('hold') as run:
            run.verified(); installed_helper.write_bytes(changed); run.send('verify-twice')
            assert run.event('invalidated')['code'] == 'installation.changed'; installed_helper.write_bytes(helper_bytes)
            run.send('again'); run.error('installation.invalidated'); passed('payload-change-invalidates-owner')
        with Run('hold') as run:
            run.verified(); moved = folder/'moved image'; assert moved.resolve().parent == image.resolve().parent == folder; image.rename(moved)
            try: run.send('verify'); run.error('installation.executable_changed'); passed('root-change-invalidates-owner')
            finally: moved.rename(image)
        with Run('hold') as run:
            run.verified(); installed_helper.write_bytes(probe_bytes)
            try: run.send('borrowed'); run.finish_child(); passed('sealed-descriptor-survives-disk-substitution')
            finally: installed_helper.write_bytes(helper_bytes)
        with Run('hold') as run:
            run.verified(); run.send('mutable'); run.error('child.program_seals'); passed('mutable-descriptor-refused')
        with Run('hold') as run:
            run.verified(); run.send('thread'); assert run.event('thread-refused')['count'] == 2; passed('wrong-thread-refused')
        with Run('hold') as run:
            run.verified(); run.send('launch'); pid, fd = run.observe_child(); run.process.kill(); assert run.process.wait(timeout=3) == -signal.SIGKILL
            assert select.select([fd], [], [], 3)[0]; passed('parent-death-stops-sealed-helper')
        assert set(CASES['cases']) == {v['case'] for v in report['cases']}; report['outcome'] = 'pass'
    except BaseException:
        report['error'] = traceback.format_exc(); raise
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat(); save(); print(folder/'result.json')


if __name__ == '__main__': main()

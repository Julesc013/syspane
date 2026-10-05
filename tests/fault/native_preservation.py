"""Independent byte/name/privacy oracle for native copies and native control bindings."""
from datetime import datetime, timezone
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from native_diagnostic import launch_xvfb

ROOT = Path(__file__).resolve().parents[2]
FLAGS = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private(path):
    if os.name != 'nt':
        assert path.stat().st_mode & 0o777 == 0o600
        return
    api = C.WinDLL('advapi32', use_last_error=True)
    kernel = C.WinDLL('kernel32', use_last_error=True)
    ptr = C.c_void_p
    owner, acl, sd = ptr(), ptr(), ptr()
    api.GetNamedSecurityInfoW.argtypes = [C.c_wchar_p, C.c_int, C.c_ulong, C.POINTER(ptr), ptr, C.POINTER(ptr), ptr, C.POINTER(ptr)]
    api.GetSecurityDescriptorControl.argtypes = [ptr, C.POINTER(C.c_ushort), C.POINTER(C.c_ulong)]
    api.GetAce.argtypes = [ptr, C.c_ulong, C.POINTER(ptr)]
    api.EqualSid.argtypes = [ptr, ptr]
    kernel.LocalFree.argtypes = [ptr]
    assert api.GetNamedSecurityInfoW(str(path), 1, 5, C.byref(owner), None, C.byref(acl), None, C.byref(sd)) == 0
    try:
        control, revision = C.c_ushort(), C.c_ulong()
        assert api.GetSecurityDescriptorControl(sd, C.byref(control), C.byref(revision)) and control.value & 0x1000
        # ACL header's AceCount; exactly the protected owner allow entry.
        assert acl.value and C.c_ushort.from_address(acl.value + 4).value == 1
        ace = ptr()
        assert api.GetAce(acl, 0, C.byref(ace)) and C.c_ubyte.from_address(ace.value).value == 0
        assert C.c_ulong.from_address(ace.value + 4).value == 0x1f01ff
        assert api.EqualSid(owner, ptr(ace.value + 8))
    finally:
        kernel.LocalFree(sd)


def main():
    executable, diagnostic, evidence = (Path(p).resolve(strict=True) for p in sys.argv[1:4])
    assert evidence.name == 'native-evidence' and evidence.parent == executable.parent == diagnostic.parent
    assert (evidence.parent/'.syspane-owner.json').is_file()
    token = uuid.uuid4().hex[:12]
    workspace = evidence/('preservation-'+token)
    workspace.mkdir(mode=0o700)
    (workspace/'.syspane-owner.json').write_text('{"owner":"W-25 preservation"}\n', encoding='utf-8')
    report = {'family': 'PRESERVE', 'outcome': 'fail', 'started_at': datetime.now(timezone.utc).isoformat(),
              'executable_sha256': sha(executable), 'diagnostic_sha256': sha(diagnostic), 'cases': [], 'attempts': [],
              'qualification': 'Native opaque file preservation and programmatic native UI binding under typed policy fixtures only.',
              'limitations': ['No installed positive policy deployment, power-loss durability, hostile same-user parent swapping, or external input/accessibility qualification.',
                             'Foreign-owner source rejection needs a separately admitted identity laboratory; no such source was created.',
                             'The owned NTFS/ext4 laboratories support no-replace publication; an unsupported-filesystem execution remains unqualified.']}
    paths = [p for folder in ('source/diagnostics', 'source/platform', 'source/interfaces', 'source/configuration', 'source/application')
             for p in (ROOT/folder).glob('*') if p.is_file()]
    paths += [Path(__file__), ROOT/'tests/fault/preservation_tests.cpp', ROOT/'tests/fault/native_diagnostic.py', ROOT/'spec/delivery/packages/w-25-preservation.md']
    report['source_inputs'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    env = dict(os.environ)
    server = None

    def run(mode, source, destination, expected='preserved', partial=False):
        command = [str(executable), mode, str(source), str(destination)]
        result = subprocess.run(command, capture_output=True, timeout=16, env=env, **FLAGS)
        report['attempts'].append({'command': command, 'exit': result.returncode,
                                   'stdout': result.stdout.decode('utf-8'), 'stderr': result.stderr.decode('utf-8')})
        assert result.returncode == 0, report['attempts'][-1]
        if mode.startswith('ui-'):
            assert result.stdout.strip() == b'ui: pass'
        else:
            assert not result.stderr and json.loads(result.stdout) == {'outcome': expected, 'partial': partial, 'durable': False}, report['attempts'][-1]

    def passed(name):
        report['cases'].append({'case': 'PRESERVE.'+name, 'outcome': 'pass'})

    try:
        source = workspace/'broken-λ.bin'
        contents = bytes(range(256))*512 + b'{malformed\xff\x00private fixture}'
        source.write_bytes(contents)
        source.chmod(0o600)
        output = workspace/'copy-λ.bin'
        run('copy', source, output)
        assert output.read_bytes() == source.read_bytes() == contents
        private(output)
        assert not Path(str(output)+'.partial').exists()
        passed('BINARY-UNICODE-PRIVATE')
        for length in range(1, 9):
            target = workspace/('n'*length)
            before = {p.name for p in workspace.iterdir()}
            run('copy', source, target)
            assert target.read_bytes() == contents and {p.name for p in workspace.iterdir()} == before | {target.name}
        passed('EXACT-NAMES')
        empty = workspace/'empty'
        empty.write_bytes(b'')
        run('copy', empty, workspace/'empty-copy')
        assert (workspace/'empty-copy').read_bytes() == b''
        passed('EMPTY')
        run('copy', source, output, 'conflict')
        partial = workspace/'existing.partial'
        partial.write_bytes(b'existing partial')
        run('copy', source, workspace/'existing', 'conflict')
        assert output.read_bytes() == contents and partial.read_bytes() == b'existing partial'
        passed('EXISTING-NAMES')
        for index, invalid in enumerate(('relative', workspace, workspace/'missing')):
            run('copy', invalid, workspace/f'invalid-{index}', 'invalid_path' if index == 0 else 'source_unavailable')
        run('copy', source, 'relative', 'invalid_path')
        passed('PATH-TYPE')
        for action in ('deny', 'cancel'):
            for phase in ('before-read', 'after-read', 'before-create', 'writing', 'verifying', 'before-publish'):
                target = workspace/(action+'-'+phase)
                staged = phase in ('writing', 'verifying', 'before-publish')
                run(action+'-'+phase, source, target, 'denied' if action == 'deny' else 'cancelled', staged)
                assert not target.exists() and Path(str(target)+'.partial').exists() == staged
                if staged: private(Path(str(target)+'.partial'))
                assert source.read_bytes() == contents
        passed('POLICY-CANCEL-PHASES')
        target = workspace/'race'
        run('race', source, target, 'conflict', True)
        assert target.read_bytes() == b'racing destination' and source.read_bytes() == contents
        assert Path(str(target)+'.partial').read_bytes() == contents
        passed('PUBLICATION-COLLISION')
        target = workspace/'race-partial'
        run('race-partial', source, target, 'conflict')
        assert not target.exists() and Path(str(target)+'.partial').read_bytes() == b'racing partial'
        passed('STAGING-COLLISION')
        if os.name == 'nt':
            run('writer', source, workspace/'writer-copy', 'source_unavailable')
            # Only the owned fixture's ACL is changed. Other users may read the source, never write it.
            tool = str(Path(os.environ['SystemRoot'])/'System32/icacls.exe')
            for access, expected in [('R', 'preserved'), ('W', 'source_unavailable')]:
                changed = subprocess.run([tool, str(output), '/grant:r', '*S-1-1-0:('+access+')'], capture_output=True, timeout=5, **FLAGS)
                report['attempts'].append({'tool': 'icacls owned source fixture', 'access': access, 'exit': changed.returncode})
                assert changed.returncode == 0
                run('copy', output, workspace/('rights-'+access), expected)
            passed('WRITER-SHARING-DACL')
        else:
            changed = workspace/'changed'
            changed.write_bytes(contents)
            run('change', changed, workspace/'changed-copy', 'source_changed', True)
            assert changed.read_bytes() == b'changed by fixture' and not (workspace/'changed-copy').exists()
            source.chmod(0o644)
            run('copy', source, workspace/'readers')
            source.chmod(0o666)
            run('copy', source, workspace/'writers', 'source_unavailable')
            source.chmod(0o600)
            fifo = workspace/'fifo'
            os.mkfifo(fifo, 0o600)
            run('copy', fifo, workspace/'fifo-copy', 'source_unavailable')
            passed('SOURCE-CHANGE-PERMISSIONS-FIFO')
        hard = workspace/'hard'
        os.link(source, hard)
        run('copy', hard, workspace/'hard-copy', 'source_unavailable')
        hard.unlink() # Exactly the fixture link created above; preserve original input.
        passed('HARDLINK')
        try:
            (workspace/'link').symlink_to(source)
        except OSError as error:
            if os.name != 'nt' or error.winerror != 1314: raise
            report['limitations'].append('Windows symlink creation privilege unavailable; source/dangling reparse cases not executed.')
        else:
            run('copy', workspace/'link', workspace/'link-copy', 'source_unavailable')
            (workspace/'dangling').symlink_to(workspace/'absent')
            run('copy', source, workspace/'dangling', 'conflict')
            passed('LEAF-LINKS')
        target = workspace/'killed'
        child = subprocess.Popen([str(executable), 'block', str(source), str(target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, **FLAGS)
        try:
            # Bounded observer via a reader thread; parent kills only this created process.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pending = pool.submit(child.stdout.readline)
                try: assert pending.result(timeout=5).strip() == b'checkpoint'
                finally:
                    child.kill()
                    child.wait(timeout=5)
            report['attempts'].append({'mode': 'external termination at second write', 'exit': child.returncode})
            assert not target.exists() and Path(str(target)+'.partial').read_bytes() == contents[:65536]
            assert source.read_bytes() == contents
            private(Path(str(target)+'.partial'))
        finally:
            if child.poll() is None: child.kill()
            child.communicate(timeout=5)
        passed('EXTERNAL-TERMINATION')
        # Real protected-policy entry: no policy fixture/override is admitted here.
        result = subprocess.run([str(diagnostic), '--preserve', str(source), str(workspace/'actual-copy')], capture_output=True, timeout=5, **FLAGS)
        report['attempts'].append({'mode': 'actual unavailable-policy CLI', 'exit': result.returncode, 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
        assert result.returncode == 77 and not result.stderr and json.loads(result.stdout) == {'outcome': 'denied', 'partial': False, 'durable': False}
        assert not (workspace/'actual-copy').exists() and not (workspace/'actual-copy.partial').exists() and source.read_bytes() == contents
        passed('REAL-CLI-DENIAL')
        if os.name != 'nt': server, env = launch_xvfb(workspace)
        for mode in ('ui-copy', 'ui-close', 'ui-revoke', 'ui-cancel'):
            target = workspace/mode
            started = time.monotonic()
            run(mode, source, target)
            elapsed = time.monotonic()-started
            assert elapsed < 8
            if mode == 'ui-copy': assert target.read_bytes() == contents
            else: assert not target.exists()
            passed(mode.upper())
        # Keep large fixture bytes bounded across repeated runs; record their identity before exact cleanup.
        large = workspace/'large'
        large.write_bytes(b'x'*(8*1024*1024))
        run('copy', large, workspace/'large-copy')
        assert sha(large) == sha(workspace/'large-copy')
        with large.open('ab') as file: file.write(b'x')
        run('copy', large, workspace/'oversize-copy', 'source_unavailable')
        report['large_fixtures'] = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in (large, workspace/'large-copy')}
        for p in (large, workspace/'large-copy'):
            assert p.parent == workspace and not p.is_symlink()
            p.unlink()
        passed('SIZE-BOUNDARY')
        report['outcome'] = 'pass'
    except Exception as error:
        report['failure'] = type(error).__name__+': '+str(error)
    finally:
        if server:
            server.terminate()
            try: server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill(); server.communicate(timeout=5)
        report['fixture_files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in workspace.iterdir()
                                   if p.is_file() and not p.is_symlink() and p.name != 'xauthority'}
        destination = evidence/('PRESERVE-'+token+'.json')
        with destination.open('x', encoding='utf-8', newline='\n') as file:
            json.dump(report, file, indent=2); file.write('\n')
        print('Native evidence: '+str(destination))
    return 0 if report['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""One bounded independent proc/pidfd sample; incomplete identity is never cached."""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import select


@dataclass(frozen=True)
class IdentitySample:
    record: dict | None = None
    reason: str = ''


def image_arguments(args, parent):
    return (len(args) == 3 and args[0] == b'syspane-image-worker' and
            args[1] in (b'image/png', b'image/jpeg', b'image/svg+xml') and
            args[2] == str(parent).encode())


def sample_identity(read_argv, read_executable, exited, parent):
    if exited(): return IdentitySample(reason='exited')
    try:
        before = read_argv()
        assert len(before) <= 4096, 'child identity command-line limit'
        if not before or not before.endswith(b'\0'):
            return IdentitySample(reason='incomplete_argv')
        args = before.split(b'\0')[:-1]
        if not args or not args[0]:return IdentitySample(reason='incomplete_argv')
        sandboxed = False
        try:
            target, digest = read_executable()
        except PermissionError:
            if exited(): return IdentitySample(reason='exited')
            target, digest = 'sandboxed:syspane-image-worker', None
            sandboxed = True
        if target is None: return IdentitySample(reason='unrelated')
        after = read_argv()
        assert len(after) <= 4096, 'child identity command-line limit'
        if before != after: return IdentitySample(reason='changing_argv')
        if exited(): return IdentitySample(reason='exited')
        if sandboxed or 'memfd:syspane-image-worker' in target:
            assert image_arguments(args, parent), ('invalid image child identity', args)
        return IdentitySample(record=dict(image=target, sha256=digest,
                                          argv=[v.decode() for v in args]))
    except (FileNotFoundError, ProcessLookupError):
        return IdentitySample(reason='disappeared')


def observe_child_identity(pid, fd, parent):
    root = Path('/proc', str(pid))
    def executable():
        path = root / 'exe'; target = os.readlink(path)
        if 'memfd:syspane-' not in target: return None, None
        return target, hashlib.sha256(path.read_bytes()).hexdigest()
    return sample_identity(lambda: (root / 'cmdline').read_bytes(), executable,
                           lambda: bool(select.select([fd], [], [], 0)[0]), parent)

"""Offline checks for the installed native introspection adapter build tools."""
import hashlib
from pathlib import Path

PINS = {
    '/usr/bin/gi-compile-repository': '2400af6ecb249f0a75367550e3e4de0ebb396bd25805a216b4c84101bfdff6b9',
    '/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0': '99bf0727e0ca4faf12ab09b753b3d03294562c29c559b970c4dad435f9ec2bc6',
    '/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0': '42467d0dbcc0a6c9e0a31f05a5944095504ce98f093c3fe0825f0a1533fa8207',
}

def verify():
    for path, digest in PINS.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise ValueError('native GJS clock dependency differs: ' + path)
    return dict(PINS)

if __name__ == '__main__':
    verify()
    print('native GJS clock build dependencies verified')

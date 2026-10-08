"""Offline checks for the installed native introspection adapter build tools."""
import hashlib
from pathlib import Path

PINS = {
    '/usr/bin/gi-compile-repository': '223a704d5ef6c0c860a630295b4cc061f376d14032833ab7c4aa4d7337155474',
    '/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0': '7a8981c2df678797438cc92f246402b81d185604623d12ab71c1ff1c2840e9fc',
    '/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0': '96ef9163aee942bdc09e6f4a1acd2fd6b178c03af824c569741440d63ac9f4f4',
}

def verify():
    for path, digest in PINS.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise ValueError('native GJS clock dependency differs: ' + path)
    return dict(PINS)

if __name__ == '__main__':
    verify()
    print('native GJS clock build dependencies verified')

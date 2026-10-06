"""One owned synthetic clock peer; never reads operational telemetry or a user bus."""
import ctypes
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import sys
import time

endpoint = Path(sys.argv[1])
mode = sys.argv[2]
workspace = Path(os.environ['HOME']).parent.resolve(strict=True)
assert workspace.name.startswith('GNOME-CLOCK-01-') and mode in ('normal', 'slow-ready')
assert endpoint.name == 's' and endpoint.parent.parent == Path('/home/ir4runner/.cache/syspane/ipc-w24')
info = endpoint.parent.stat()
assert endpoint.parent.resolve(strict=True) == endpoint.parent and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700
stopping = False
def stop(*_):
    global stopping
    stopping = True
signal.signal(signal.SIGTERM, stop)
parent = os.getppid()
assert parent > 1 and ctypes.CDLL(None, use_errno=True).prctl(1, signal.SIGTERM, 0, 0, 0) == 0
assert os.getppid() == parent
journal = (workspace/'clock-peer.jsonl').open('x', encoding='utf-8')
def record(event, **fields):
    raw = json.dumps(dict(event=event, pid=os.getpid(), parent=parent, session=os.getsid(0),
        at_ns=str(time.clock_gettime_ns(time.CLOCK_BOOTTIME)), **fields))+'\n'
    assert journal.tell()+len(raw.encode()) <= 65536
    journal.write(raw); journal.flush()
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client = None
try:
    server.bind(str(endpoint)); endpoint.chmod(0o600); server.listen(1)
    record('waiting')
    begin = time.monotonic()
    while mode == 'slow-ready' and not stopping and time.monotonic()-begin < .75:
        time.sleep(.01)
    if not stopping:
        print('ready', flush=True)
        while not stopping and time.monotonic()-begin < 20:
            if not client:
                if not select.select([server], [], [], .05)[0]:
                    continue
                client = server.accept()[0]
                data = bytearray()
            if select.select([client], [], [], .05)[0]:
                part = client.recv(65-len(data))
                if not part:
                    break
                data.extend(part)
                assert len(data) <= 64
                if data.endswith(b'\n'):
                    assert data == b'sample\n'
                    sample = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                    record('sample', sample_ns=str(sample))
                    client.sendall((str(sample)+'\n').encode())
                    # Exactly one sample; keep the authenticated native lifetime alive.
                    while not stopping and time.monotonic()-begin < 20:
                        if select.select([client], [], [], .05)[0]:
                            assert client.recv(1) == b''
                            stopping = True
                    break
    record('stopped')
finally:
    if client:
        client.close()
    server.close(); endpoint.unlink(); journal.close()

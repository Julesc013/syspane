"""Standalone native GJS clock qualification; no display, user bus or telemetry."""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'source/build'))
from prepare_gnome_lab import owned_build, inventory
from check_gjs_clock_dependencies import verify

SOURCES = ['CMakeLists.txt', 'source/build/components.json',
    'source/build/check_gjs_clock_dependencies.py', 'source/build/prepare_gnome_lab.py',
    'source/build/gnome-lab-packages.json', 'source/build/targets/linux-x64-gcc13.json',
    'source/platform/local_ipc.hpp', 'source/platform/local_ipc_linux.cpp',
    'source/desktop/gnome/native_clock.hpp', 'source/desktop/gnome/native_clock.cpp',
    'source/desktop/gnome/SysPaneClock-0.1.gir', 'tests/desktop/gjs_clock.js',
    'tests/desktop/native_gjs_clock.py', 'spec/delivery/packages/w-25-gjs-clock.md']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def receive(process):
    if not select.select([process.stdout], [], [], 5)[0]:
        raise AssertionError('native child response timeout')
    line = process.stdout.readline()
    if not line:
        raise AssertionError('native child exited before response')
    return json.loads(line)

def descriptors(pid):
    return {p.name: os.readlink(p) for p in Path(f'/proc/{pid}/fd').iterdir()}

def server(endpoint):
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(endpoint)
    os.chmod(endpoint, 0o600)
    listener.listen(8)
    held = []
    print(json.dumps({'event': 'listening'}), flush=True)
    while True:
        ready = select.select([listener, sys.stdin], [], [], 10)[0]
        if sys.stdin in ready:
            assert sys.stdin.read(1) == 'x'
            break
        if listener in ready:
            assert len(held) < 8
            held.append(listener.accept()[0])
        if not ready:
            raise AssertionError('server observer timeout')
    for item in held:
        item.close()
    listener.close()
    Path(endpoint).unlink()

def main():
    build = owned_build(Path(sys.argv[1]))
    output = build / 'native-evidence'
    output.mkdir(exist_ok=True)
    attempt = 'GJS-CLOCK-' + uuid.uuid4().hex
    report = {'family': 'GJS-CLOCK', 'outcome': 'fail', 'executed_at': datetime.now(timezone.utc).isoformat(),
        'source_inputs': {p: sha(ROOT/p) for p in SOURCES}, 'cases': [],
        'qualification': 'Standalone authenticated native GJS BOOTTIME only; no renderer age, suspend or namespace-change qualification.'}
    archive = output / (attempt + '-sources.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as bundle:
        for name in SOURCES:
            bundle.write(ROOT/name, name)
    report['source_archive_sha256'] = sha(archive)
    processes, sockets, handles, native = [], [], [], None
    runtime = Path.home()/'.cache/syspane/ipc-w24'
    assert runtime.resolve(strict=True) == runtime and runtime.stat().st_uid == os.getuid() and runtime.stat().st_mode & 0o777 == 0o700
    workspace = runtime / ('case-' + uuid.uuid4().hex)
    workspace.mkdir(mode=0o700)
    endpoint = str(workspace/'s')
    try:
        report['build_dependencies'] = verify()
        lab = build/'gnome-lab'
        identity = json.loads((lab/'identity.json').read_text())
        assert identity['lock_sha256'] == sha(ROOT/'source/build/gnome-lab-packages.json')
        assert identity['files'] == inventory(lab/'sysroot'), 'extracted GJS laboratory identity differs'
        executable = lab/'sysroot/usr/bin/gjs'
        report['artifacts'] = {str(p): sha(p) for p in [build/'libsyspane_gjs_clock.so', build/'SysPaneClock-0.1.typelib', executable, lab/'identity.json']}
        native = subprocess.Popen(['/usr/bin/python3', str(Path(__file__).resolve()), '--server', endpoint],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append(native)
        native_handle = os.pidfd_open(native.pid)
        handles.append(native_handle)
        assert receive(native) == {'event': 'listening'}
        blocking = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        blocking.connect(endpoint)
        sockets.append(blocking)
        sockets.extend([socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM), socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)])
        for item in sockets[1:]:
            item.setblocking(False)
        tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_listener.bind(('127.0.0.1', 0)); tcp_listener.listen(1)
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect(tcp_listener.getsockname()); tcp_client.setblocking(False)
        tcp_server = tcp_listener.accept()[0]
        sockets.extend([tcp_client, tcp_listener, tcp_server])
        regular = os.open('/dev/null', os.O_RDONLY | os.O_NONBLOCK)
        handles.append(regular)
        invalid = [blocking.fileno(), sockets[1].fileno(), sockets[2].fileno(), tcp_client.fileno(), regular]
        initial_flags = {fd: fcntl.fcntl(fd, fcntl.F_GETFL) for fd in invalid}
        env = {k: v for k, v in os.environ.items() if k not in ('DISPLAY','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','GI_TYPELIB_PATH','LD_LIBRARY_PATH')}
        lib = lab/'sysroot/usr/lib/x86_64-linux-gnu'
        env.update(LD_LIBRARY_PATH=str(build)+':'+str(lib),
            GI_TYPELIB_PATH=':'.join(map(str, [build, lib/'gjs/girepository-1.0', lib/'girepository-1.0'])))
        command = [str(executable), '-m', str(ROOT/'tests/desktop/gjs_clock.js'), endpoint, str(native.pid), json.dumps(invalid)]
        child = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, pass_fds=invalid)
        processes.append(child)
        child_handle = os.pidfd_open(child.pid)
        handles.append(child_handle)
        report['command'] = command
        ready = receive(child)
        assert ready == {'event': 'ready', 'codes': ['peer.handle','peer.process','peer.process'] + ['peer.socket']*5 + ['clock.closed']}
        assert all(fcntl.fcntl(fd, fcntl.F_GETFL) == flags for fd, flags in initial_flags.items())
        assert all(str(fd) in descriptors(child.pid) for fd in invalid)
        report['cases'].append({'case': 'GJS-CLOCK.REJECT', 'outcome': 'pass', 'observation': ready, 'borrowed_flags_unchanged': True})
        def ask(op):
            child.stdin.write(json.dumps({'op':op})+'\n'); child.stdin.flush()
            return receive(child)
        brackets = []
        for _ in range(16):
            before = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            response = ask('sample')
            after = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            value = response['value']
            assert response['event'] == 'sample' and isinstance(value, str) and value == str(int(value))
            assert 0 <= int(value) <= 2**64-1 and before <= int(value) <= after
            if brackets:
                assert int(value) >= int(brackets[-1][1])
            brackets.append([str(before), value, str(after)])
        report['cases'].append({'case': 'GJS-CLOCK.ROUNDTRIP', 'outcome': 'pass', 'brackets_ns': brackets})
        baseline = descriptors(child.pid)
        cycles = ask('cycles')
        assert cycles == {'event':'cycles', 'count':64}
        assert descriptors(child.pid) == baseline, 'native descriptors leaked during close cycles'
        assert not select.select([native_handle,child_handle], [], [], 0)[0]
        native.stdin.write('x'); native.stdin.flush()
        assert native.wait(timeout=5) == 0 and select.select([native_handle], [], [], 0)[0]
        response = ask('peer-exit')
        assert response == {'event':'peer-exit', 'codes':['clock.peer_exited','clock.unavailable']}
        report['cases'].append({'case':'GJS-CLOCK.PEER-EXIT','outcome':'pass','native_pid':native.pid,'native_exit':0,'pidfd_exit':True,'observation':response})
        assert ask('close') == {'event':'close','code':'clock.closed'}
        after_close = descriptors(child.pid)
        assert set(after_close) < set(baseline) and len(baseline)-len(after_close) == 4, 'owned clock/GIO descriptors were not released'
        assert all(after_close[fd] == baseline[fd] for fd in after_close)
        report['cases'].append({'case':'GJS-CLOCK.CLOSE','outcome':'pass','cycles':64,'baseline_descriptors':baseline,'after_close_descriptors':after_close})
        child.stdin.write('{"op":"exit"}\n'); child.stdin.flush()
        assert child.wait(timeout=5) == 0 and select.select([child_handle], [], [], 0)[0]
        report['outcome'] = 'pass'
    except Exception as error:
        report['failure'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        report['processes'] = []
        for process in processes:
            forced = process.poll() is None
            if forced:
                process.kill()
            process.wait(timeout=5)
            report['processes'].append({'pid':process.pid,'exit':process.returncode,'forced_cleanup':forced,
                'remaining_stdout':process.stdout.read(),'stderr':process.stderr.read()})
        for item in sockets:
            item.close()
        for handle in handles:
            os.close(handle)
        # Only this attempt's known socket; never recursively remove a directory.
        if Path(endpoint).is_socket():
            Path(endpoint).unlink()
        workspace.rmdir()
        path = output/(attempt+'.json')
        path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print('Native evidence: '+str(path), flush=True)
        print('GJS-CLOCK: '+report['outcome'], flush=True)

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--server':
        server(sys.argv[2])
    else:
        main()

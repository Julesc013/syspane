"""Independent executable/owned-window checks. No desktop capture or machine policy writes."""
import ctypes as C
import faulthandler
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import secrets
import struct
import socket
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = os.name == 'nt'
FLAGS = {'creationflags': subprocess.CREATE_NO_WINDOW} if WINDOWS else {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def close_windows(process):
    from ctypes import wintypes as W
    user = C.WinDLL('user32', use_last_error=True)
    callback_type = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    user.EnumWindows.argtypes = [callback_type, W.LPARAM]
    user.GetWindowThreadProcessId.argtypes = [W.HWND, C.POINTER(W.DWORD)]
    user.GetClassNameW.argtypes = [W.HWND, W.LPWSTR, C.c_int]
    user.GetWindowTextW.argtypes = [W.HWND, W.LPWSTR, C.c_int]
    user.PostMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
    user.PostMessageW.restype = W.BOOL
    found = []
    def inspect(window, _):
        pid = W.DWORD()
        user.GetWindowThreadProcessId(window, C.byref(pid))
        if pid.value == process.pid:
            title, kind = C.create_unicode_buffer(128), C.create_unicode_buffer(128)
            user.GetWindowTextW(window, title, len(title))
            user.GetClassNameW(window, kind, len(kind))
            if title.value == 'SysPane Diagnostic' and kind.value == 'SysPane.Diagnostic.Window':
                found.append(window)
        return True
    callback = callback_type(inspect)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and process.poll() is None:
        user.EnumWindows(callback, 0)
        if found:
            assert len(set(found)) == 1
            assert user.PostMessageW(found[0], 0x0010, 0, 0), 'native WM_CLOSE failed'
            return {'native_api': 'Win32 WM_CLOSE', 'pid_verified': True, 'title_verified': True, 'class_verified': True}
        time.sleep(.05)
    raise AssertionError('owned diagnostic native window was not found')

def close_x11(pid):
    x = C.CDLL('libX11.so.6')
    display_type, window_type, atom_type = C.c_void_p, C.c_ulong, C.c_ulong
    class ClassHint(C.Structure):
        _fields_ = [('res_name', C.c_void_p), ('res_class', C.c_void_p)]
    signatures = {
        'XOpenDisplay': ([C.c_char_p], display_type),
        'XDefaultRootWindow': ([display_type], window_type),
        'XInternAtom': ([display_type, C.c_char_p, C.c_int], atom_type),
        'XQueryTree': ([display_type, window_type, C.POINTER(window_type), C.POINTER(window_type), C.POINTER(C.POINTER(window_type)), C.POINTER(C.c_uint)], C.c_int),
        'XGetWindowProperty': ([display_type, window_type, atom_type, C.c_long, C.c_long, C.c_int, atom_type, C.POINTER(atom_type), C.POINTER(C.c_int), C.POINTER(C.c_ulong), C.POINTER(C.c_ulong), C.POINTER(C.c_void_p)], C.c_int),
        'XFetchName': ([display_type, window_type, C.POINTER(C.c_void_p)], C.c_int),
        'XGetClassHint': ([display_type, window_type, C.POINTER(ClassHint)], C.c_int),
        'XFree': ([C.c_void_p], C.c_int),
        'XSendEvent': ([display_type, window_type, C.c_int, C.c_long, C.c_void_p], C.c_int),
        'XFlush': ([display_type], C.c_int),
        'XCloseDisplay': ([display_type], C.c_int),
    }
    for name, (args, result) in signatures.items():
        getattr(x, name).argtypes, getattr(x, name).restype = args, result
    display = x.XOpenDisplay(None)
    assert display, 'X11 test display unavailable'
    try:
        pid_atom = x.XInternAtom(display, b'_NET_WM_PID', False)
        root = x.XDefaultRootWindow(display)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            returned_root, parent = window_type(), window_type()
            children, count = C.POINTER(window_type)(), C.c_uint()
            assert x.XQueryTree(display, root, C.byref(returned_root), C.byref(parent), C.byref(children), C.byref(count))
            try:
                for index in range(count.value):
                    window = children[index]
                    kind, form, length, remaining, data = atom_type(), C.c_int(), C.c_ulong(), C.c_ulong(), C.c_void_p()
                    status = x.XGetWindowProperty(display, window, pid_atom, 0, 1, False, 0, C.byref(kind), C.byref(form), C.byref(length), C.byref(remaining), C.byref(data))
                    try:
                        observed_pid = C.cast(data, C.POINTER(C.c_ulong))[0] if status == 0 and form.value == 32 and length.value == 1 and data else None
                    finally:
                        if data: x.XFree(data)
                    if observed_pid != pid:
                        continue
                    name = C.c_void_p()
                    assert x.XFetchName(display, window, C.byref(name))
                    try:
                        if C.string_at(name) != b'SysPane Diagnostic': continue
                    finally:
                        if name: x.XFree(name)
                    hint = ClassHint()
                    assert x.XGetClassHint(display, window, C.byref(hint))
                    try:
                        assert C.string_at(hint.res_name) == b'syspane-diag' and C.string_at(hint.res_class) == b'Syspane-diag', 'unexpected native GTK class'
                    finally:
                        if hint.res_name: x.XFree(hint.res_name)
                        if hint.res_class: x.XFree(hint.res_class)
                    class Data(C.Union):
                        _fields_ = [('b', C.c_char * 20), ('s', C.c_short * 10), ('l', C.c_long * 5)]
                    class Client(C.Structure):
                        _fields_ = [('type', C.c_int), ('serial', C.c_ulong), ('send_event', C.c_int), ('display', display_type), ('window', window_type), ('message_type', atom_type), ('format', C.c_int), ('data', Data)]
                    class Event(C.Union):
                        _fields_ = [('client', Client), ('pad', C.c_long * 24)]
                    event = Event()
                    event.client.type, event.client.display, event.client.window = 33, display, window
                    event.client.message_type = x.XInternAtom(display, b'WM_PROTOCOLS', False)
                    event.client.format = 32
                    event.client.data.l[0] = x.XInternAtom(display, b'WM_DELETE_WINDOW', False)
                    assert x.XSendEvent(display, window, False, 0, C.byref(event))
                    x.XFlush(display)
                    return {'native_api': 'GTK/X11 WM_DELETE_WINDOW', 'pid_verified': True, 'title_verified': True, 'class_verified': True}
            finally:
                if children: x.XFree(children)
            time.sleep(.05)
        raise AssertionError('owned diagnostic X11 window was not found')
    finally:
        x.XCloseDisplay(display)

def x11_observer(pid, environment, channel):
    os.environ.update(environment)
    try:
        channel.send({'result': close_x11(pid)})
    except Exception as error:
        channel.send({'error': type(error).__name__ + ': ' + str(error)})
    finally:
        channel.close()

def bounded_close_x11(process, environment):
    context = mp.get_context('spawn')
    receive, send = context.Pipe(duplex=False)
    observer = context.Process(target=x11_observer, args=(process.pid, {key: environment[key] for key in ('DISPLAY', 'XAUTHORITY', 'GDK_BACKEND')}, send))
    observer.start()
    send.close()
    try:
        if not receive.poll(6):
            raise TimeoutError('owned X11 observer exceeded six-second bound')
        result = receive.recv()
        if 'error' in result:
            raise AssertionError(result['error'])
        return result['result']
    finally:
        receive.close()
        if observer.is_alive(): observer.terminate()
        observer.join(2)
        if observer.is_alive():
            observer.kill()
            observer.join(2)

def launch_xvfb(workspace):
    # Cookie authorizes only this private test server; it is never printed or recorded.
    cookie = secrets.token_bytes(16)
    def field(value): return struct.pack('!H', len(value)) + value
    auth = workspace/'xauthority'
    with auth.open('xb') as file:
        file.write(struct.pack('!H', 65535) + field(b'') + field(b'') + field(b'MIT-MAGIC-COOKIE-1') + field(cookie))
    auth.chmod(0o600)
    number = str(30000 + secrets.randbelow(20000))
    if Path('/tmp/.X' + number + '-lock').exists() or Path('/tmp/.X11-unix/X' + number).exists():
        raise AssertionError('chosen test display already exists; refusing replacement')
    server = subprocess.Popen(['/usr/bin/Xvfb', ':' + number, '-nolisten', 'tcp', '-nolisten', 'unix', '-listen', 'local', '-noreset', '-auth', str(auth), '-screen', '0', '800x600x24'],
                              cwd=workspace, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and server.poll() is None:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
                probe.settimeout(.1)
                try: probe.connect('\0/tmp/.X11-unix/X' + number)
                except (ConnectionRefusedError, FileNotFoundError, TimeoutError):
                    time.sleep(.05)
                    continue
                peer_pid, _, _ = struct.unpack('3i', probe.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                if peer_pid != server.pid: raise AssertionError('test display peer is not the owned server')
                return server, {**os.environ, 'DISPLAY': ':' + number, 'XAUTHORITY': str(auth), 'GDK_BACKEND': 'x11'}
        raise TimeoutError('owned Xvfb startup exceeded five-second bound or exited')
    except Exception as error:
        if server.poll() is None: server.kill()
        _, diagnostic = server.communicate(timeout=5)
        raise AssertionError(str(error) + '; Xvfb: ' + diagnostic[:4096].decode('utf-8', errors='replace')) from error

def main():
    executable, output, profile = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
    assert output.parent == executable.parent and output.name == 'native-evidence'
    output.mkdir(exist_ok=True)
    token = uuid.uuid4().hex
    workspace = executable.parent / ('diagnostic-case-' + token)
    workspace.mkdir(mode=0o700)
    copied = workspace / executable.name
    shutil.copy2(executable, copied)
    report = {'family': 'DIAG-01', 'outcome': 'fail', 'executed_at': datetime.now(timezone.utc).isoformat(),
              'executable_sha256': sha(executable), 'profile': profile, 'cases': [],
              'qualification': 'Development diagnostic entry and hidden native close only; no pixels, protected-policy deployment or desktop/editor recovery qualification.',
              'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for directory in ('source/application', 'source/diagnostics', 'source/interfaces', 'source/platform', 'source/configuration') for p in sorted((ROOT/directory).glob('*')) if p.is_file()}}
    report['source_inputs']['tests/fault/native_diagnostic.py'] = sha(Path(__file__))
    report['source_inputs']['spec/delivery/packages/w-25-recovery.md'] = sha(ROOT/'spec/delivery/packages/w-25-recovery.md')
    attempts = []
    def run(*args, env=None):
        print('Diagnostic invocation: ' + ' '.join(args), flush=True)
        result = subprocess.run([str(copied), *args], cwd=workspace, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=5, **FLAGS)
        attempts.append({'arguments': list(args), 'exit': result.returncode, 'stdout': result.stdout.decode('utf-8'), 'stderr': result.stderr.decode('utf-8')})
        return result
    def case(name, action):
        print('Diagnostic case: ' + name, flush=True)
        start = time.monotonic()
        row = {'case': 'DIAG-01.' + name, 'outcome': 'fail'}
        report['cases'].append(row)
        try:
            extra = action()
            row.update(outcome='pass', **(extra or {}))
            print('Diagnostic pass: ' + name, flush=True)
        finally:
            row['elapsed_ms'] = round((time.monotonic() - start) * 1000)
    baseline = None
    try:
        def report_case():
            nonlocal baseline
            result = run('--report')
            assert result.returncode == 0, 'report denied/unavailable; preserve lab limitation without policy override'
            baseline = json.loads(result.stdout)
            expected = {'schema_version': '0.1.0', 'product': 'SysPane', 'component': 'diagnostic', 'build_version': '0.0.1', 'profile': profile,
                        'policy_state': baseline.get('policy_state'), 'recovery_controls': 'not_implemented'}
            assert baseline == expected and baseline['policy_state'] in ('available', 'unavailable')
            assert not result.stderr
            return {'policy_state': baseline['policy_state'], 'relocated': True}
        case('REPORT', report_case)
        def damaged():
            for name in ('scene.json', 'theme.json', 'history.json', 'policy.json'):
                (workspace/name).write_bytes(b'{broken\xff\x00"available":true,"secret":"must-not-appear"}')
            before = {p.name: sha(p) for p in workspace.iterdir() if p.is_file()}
            env = dict(os.environ, SYSPANE_POLICY=str(workspace/'policy.json'), SYSPANE_POLICY_JSON='{"available":true}')
            result = run('--report', env=env)
            assert result.returncode == 0 and json.loads(result.stdout) == baseline and not result.stderr
            assert before == {p.name: sha(p) for p in workspace.iterdir() if p.is_file()}
        case('DAMAGED', damaged)
        def arguments():
            for args in (('--unknown',), ('--report', '--inspect'), ('--policy', str(workspace/'policy.json')), ('--report', '--trusted')):
                result = run(*args)
                assert result.returncode == 64 and not result.stdout and result.stderr == b'diagnostic.arguments\n'
        case('ARGUMENTS', arguments)
        def native_close():
            env = dict(os.environ)
            server = None
            if not WINDOWS: server, env = launch_xvfb(workspace)
            process = None
            try:
                process = subprocess.Popen([str(copied), '--inspect-hidden'], cwd=workspace, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **FLAGS)
                result = close_windows(process) if WINDOWS else bounded_close_x11(process, env)
                stdout, stderr = process.communicate(timeout=5)
                result.update(exit=process.returncode, stdout=stdout.decode('utf-8'), stderr=stderr.decode('utf-8'))
                if server:
                    result['display_server'] = {'kind': 'owned authenticated Xvfb', 'sha256': sha(Path('/usr/bin/Xvfb')), 'pixels_captured': False}
                assert process.returncode == 0 and not stdout, result
                return result
            finally:
                if process and process.poll() is None:
                    process.kill() # Only the exact child created above.
                    process.communicate(timeout=5)
                if server:
                    server.terminate()
                    try: server.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        server.kill()
                        server.communicate(timeout=5)
        case('NATIVE-CLOSE', native_close)
        if not WINDOWS:
            def no_display():
                env = dict(os.environ, GDK_BACKEND='x11')
                env.pop('DISPLAY', None)
                env.pop('WAYLAND_DISPLAY', None)
                result = run('--report', env=env)
                assert result.returncode == 0 and json.loads(result.stdout) == baseline
                result = run('--inspect', env=env)
                assert result.returncode == 69 and not result.stdout and b'diagnostic.ui_unavailable' in result.stderr
            case('NO-DISPLAY', no_display)
        report['outcome'] = 'pass'
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        report['attempts'] = attempts
        path = output / ('DIAG-01-' + token + '.json')
        with path.open('x', encoding='utf-8', newline='\n') as file:
            json.dump(report, file, indent=2)
            file.write('\n')
        # Exact files in the uniquely created workspace only; no recursive deletion.
        for path_to_remove in workspace.iterdir():
            if path_to_remove.name not in {copied.name, 'scene.json', 'theme.json', 'history.json', 'policy.json', 'xauthority'} or path_to_remove.is_symlink():
                raise ValueError('unexpected diagnostic fixture; retain workspace')
            path_to_remove.unlink()
        workspace.rmdir()
        print('Native evidence: ' + str(path))
    return 0 if report['outcome'] == 'pass' else 1

if __name__ == '__main__':
    faulthandler.dump_traceback_later(10, repeat=True)
    sys.exit(main())

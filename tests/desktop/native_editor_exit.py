"""Owned X11 lifetime/input experiment; no user display, shell or authored document."""
import ctypes as C
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/fault'))
from native_diagnostic import launch_xvfb
from native_oracle import Display, Event

CASES = ('KEY-LIVE', 'KEY-FROZEN', 'BUTTON-FROZEN', 'LOCKS-FROZEN', 'DRAG-FROZEN', 'MAPPING-LOSS', 'OWNER-LOSS', 'EDITOR-CRASH', 'GRAB-CONFLICT')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def until(predicate, seconds=3):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.01)
    raise AssertionError('native observation deadline')


class Observer(Display):
    def __init__(self):
        super().__init__()
        p, i, w = C.c_void_p, C.c_int, C.c_ulong
        signatures = {
            'XSelectInput': ([p, w, C.c_long], i),
            'XPending': ([p], i), 'XNextEvent': ([p, C.c_void_p], i),
            'XKeysymToKeycode': ([p, w], C.c_ubyte),
            'XGrabKey': ([p, i, C.c_uint, w, i, i, i], i),
            'XUngrabKey': ([p, i, C.c_uint, w], i),
            'XQueryTree': ([p, w, C.POINTER(w), C.POINTER(w), C.POINTER(C.POINTER(w)), C.POINTER(C.c_uint)], i),
            'XSetInputFocus': ([p, w, i, w], i),
            'XGetGeometry': ([p, w, C.POINTER(w), C.POINTER(i), C.POINTER(i), C.POINTER(C.c_uint), C.POINTER(C.c_uint), C.POINTER(C.c_uint), C.POINTER(C.c_uint)], i),
            'XTranslateCoordinates': ([p, w, w, i, i, C.POINTER(i), C.POINTER(i), C.POINTER(w)], i),
            'XQueryPointer': ([p, w, C.POINTER(w), C.POINTER(w), C.POINTER(i), C.POINTER(i), C.POINTER(i), C.POINTER(i), C.POINTER(C.c_uint)], i),
            'XChangeKeyboardMapping': ([p, i, i, C.POINTER(w), i], i),
        }
        for name, (args, result) in signatures.items():
            getattr(self.x, name).argtypes, getattr(self.x, name).restype = args, result
        self.xt = C.CDLL('libXtst.so.6')
        for name, args in {
            'XTestFakeKeyEvent': [p, C.c_uint, i, w],
            'XTestFakeButtonEvent': [p, C.c_uint, i, w],
            'XTestFakeMotionEvent': [p, i, i, i, w],
        }.items():
            getattr(self.xt, name).argtypes, getattr(self.xt, name).restype = args, i
        self.errors = []
        self.error_type = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_void_p)
        self.error_callback = self.error_type(lambda _d, _e: self.errors.append('x_error') or 0)
        self.x.XSetErrorHandler.argtypes, self.x.XSetErrorHandler.restype = [self.error_type], C.c_void_p
        self.previous_error = self.x.XSetErrorHandler(self.error_callback)
        self.witness = self.x.XCreateSimpleWindow(self.handle, self.root, 50, 150, 400, 300, 0, 0, 0x116633)
        self.x.XSelectInput(self.handle, self.witness, 4)
        self.x.XMapRaised(self.handle, self.witness)
        self.sync()
        self.escape_code = self.x.XKeysymToKeycode(self.handle, 0xff1b)

    def sync(self):
        self.x.XSync(self.handle, False)

    def key(self, symbol, down):
        code = self.x.XKeysymToKeycode(self.handle, symbol)
        assert code and self.xt.XTestFakeKeyEvent(self.handle, code, down, 0)

    def chord(self, shifted=False):
        keys = [0xffe3, 0xffe9] + ([0xffe1] if shifted else []) + [0xff1b]
        for key in keys:
            self.key(key, True)
        for key in reversed(keys):
            self.key(key, False)
        self.sync()

    def click(self, x=100, y=200):
        assert self.xt.XTestFakeMotionEvent(self.handle, 0, x, y, 0)
        assert self.xt.XTestFakeButtonEvent(self.handle, 1, True, 0)
        assert self.xt.XTestFakeButtonEvent(self.handle, 1, False, 0)
        self.sync()

    def clicks(self):
        count = 0
        self.sync()
        while self.x.XPending(self.handle):
            event = Event()
            self.x.XNextEvent(self.handle, C.byref(event))
            if event.client.type == 4:
                count += 1
        return count

    def pixel(self):
        return self.capture(100, 200, 1, 1).hex()

    def windows(self, pid):
        root, parent = C.c_ulong(), C.c_ulong()
        children, count = C.POINTER(C.c_ulong)(), C.c_uint()
        assert self.x.XQueryTree(self.handle, self.root, C.byref(root), C.byref(parent), C.byref(children), C.byref(count))
        try:
            found = [children[n] for n in range(count.value) if self.property(children[n], '_NET_WM_PID') == [pid]]
            return found
        finally:
            if children:
                self.x.XFree(children)

    def child_window(self, pid):
        found = self.windows(pid)
        assert len(found) <= 1
        return found[0] if found else 0

    def input_state(self):
        root, child = C.c_ulong(), C.c_ulong()
        coordinates = [C.c_int() for _ in range(4)]
        state = C.c_uint()
        assert self.x.XQueryPointer(self.handle, self.root, C.byref(root), C.byref(child), *[C.byref(value) for value in coordinates], C.byref(state))
        return state.value

    def grab(self, expect=True):
        self.errors.clear()
        self.x.XGrabKey(self.handle, self.escape_code, 4 | 8, self.root, False, 1, 1)
        self.sync()
        assert (not self.errors) == expect, 'shortcut ownership mismatch'

    def recovery_button(self, pid):
        window = 0
        for candidate in self.windows(pid):
            name = C.c_void_p()
            if not self.x.XFetchName(self.handle, candidate, C.byref(name)):
                continue
            try:
                if C.string_at(name) == b'SysPane independent editor exit':
                    assert not window, 'ambiguous recovery control'
                    window = candidate
            finally:
                self.x.XFree(name)
        if not window:
            return None
        root, child = C.c_ulong(), C.c_ulong()
        x, y, rx, ry = C.c_int(), C.c_int(), C.c_int(), C.c_int()
        width, height, border, depth = (C.c_uint() for _ in range(4))
        assert self.x.XGetGeometry(self.handle, window, C.byref(root), C.byref(x), C.byref(y), C.byref(width), C.byref(height), C.byref(border), C.byref(depth))
        assert self.x.XTranslateCoordinates(self.handle, window, self.root, 0, 0, C.byref(rx), C.byref(ry), C.byref(child))
        name = C.c_void_p()
        assert self.x.XFetchName(self.handle, window, C.byref(name))
        try:
            assert C.string_at(name) == b'SysPane independent editor exit'
        finally:
            self.x.XFree(name)
        if not (100 <= width.value <= 800 and 20 <= height.value <= 100):
            return None
        return {'window': window, 'root_x': rx.value, 'root_y': ry.value, 'width': width.value, 'height': height.value}

    def ungrab(self):
        self.x.XUngrabKey(self.handle, self.escape_code, 1 << 15, self.root)
        self.sync()


def run_case(executable, name, workspace, row):
    server = process = observer = None
    child_fd = owner_fd = None
    stdout = workspace / 'owner.stdout'
    stderr = workspace / 'owner.stderr'
    try:
        server, environment = launch_xvfb(workspace)
        os.environ.update(environment)
        observer = Observer()
        row['baseline_pixel'] = observer.pixel()
        assert row['baseline_pixel'] == '116633'
        observer.click()
        assert observer.clicks() == 1
        if name == 'GRAB-CONFLICT':
            observer.grab()
        with stdout.open('xb') as out, stderr.open('xb') as err:
            process = subprocess.Popen([str(executable), '--owned-x11-lab'], env=environment, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        owner_fd = os.pidfd_open(process.pid)
        row['owner_pid'] = process.pid
        def events():
            return [json.loads(line) for line in stdout.read_text().splitlines() if line.endswith('}')]
        if name == 'GRAB-CONFLICT':
            assert process.wait(timeout=5) == 69
            assert stdout.read_bytes() == b'' and stderr.read_text().strip() == 'editor.shortcut_unavailable'
            assert observer.pixel() == '116633'
            observer.ungrab()
            row['admission'] = 'denied_before_child'
        else:
            until(lambda: any(item['event'] == 'child' for item in events()))
            child = next(item['value'] for item in events() if item['event'] == 'child')
            child_fd = os.pidfd_open(child)
            row['child_pid'] = child
            row['child_executable_sha256'] = sha(Path('/proc') / str(child) / 'exe')
            assert row['child_executable_sha256'] == sha(executable)
            status = (Path('/proc') / str(child) / 'status').read_text()
            assert int(next(line.split()[1] for line in status.splitlines() if line.startswith('PPid:'))) == process.pid
            row['parent_verified'] = True
            until(lambda: observer.child_window(child) and observer.pixel() == 'cc2233')
            window = observer.child_window(child)
            observer.x.XSetInputFocus(observer.handle, window, 2, 0)
            observer.sync()
            row['obstructed_pixel'] = observer.pixel()
            observer.clicks()
            observer.click()
            assert observer.clicks() == 0, 'candidate failed to obstruct underlying input'
            row['input_obstructed'] = True
            if name == 'BUTTON-FROZEN':
                until(lambda: observer.recovery_button(process.pid))
                row['native_button'] = observer.recovery_button(process.pid)
            if name == 'KEY-LIVE':
                observer.key(0xff1b, True)
                observer.key(0xff1b, False)
                observer.sync()
                time.sleep(.2)
                assert not select.select([child_fd], [], [], 0)[0]
                observer.chord(shifted=True)
                time.sleep(.2)
                assert not select.select([child_fd], [], [], 0)[0]
                row['ordinary_and_shifted_ignored'] = True
            if name == 'LOCKS-FROZEN':
                for key in (0xffe5, 0xff7f):
                    observer.key(key, True)
                    observer.key(key, False)
                observer.sync()
                row['lock_state'] = observer.input_state()
                assert row['lock_state'] & (2 | 16) == (2 | 16), 'Caps and Num Lock were not enabled'
            if 'FROZEN' in name:
                signal.pidfd_send_signal(child_fd, signal.SIGSTOP)
                until(lambda: '\nState:\tT' in (Path('/proc') / str(child) / 'status').read_text())
                row['stopped_before_stimulus'] = True
            if name == 'DRAG-FROZEN':
                assert observer.xt.XTestFakeButtonEvent(observer.handle, 1, True, 0)
                observer.sync()
                row['drag_state'] = observer.input_state()
                assert row['drag_state'] & 256, 'primary button was not held'
            started = time.monotonic_ns()
            row['stimulus_ns'] = started
            if name == 'OWNER-LOSS':
                signal.pidfd_send_signal(owner_fd, signal.SIGKILL)
            elif name == 'EDITOR-CRASH':
                signal.pidfd_send_signal(child_fd, signal.SIGKILL)
            elif name == 'BUTTON-FROZEN':
                button = row['native_button']
                observer.click(button['root_x'] + button['width'] // 2, button['root_y'] + button['height'] // 2)
            elif name == 'MAPPING-LOSS':
                replacement = (C.c_ulong * 1)(0xffc9)
                observer.x.XChangeKeyboardMapping(observer.handle, observer.escape_code, 1, replacement, 1)
                observer.sync()
            else:
                observer.chord()
            until(lambda: bool(select.select([child_fd], [], [], 0)[0]), 1.5)
            row['native_exit_ns'] = time.monotonic_ns()
            if name == 'DRAG-FROZEN':
                assert observer.xt.XTestFakeButtonEvent(observer.handle, 1, False, 0)
                observer.sync()
            until(lambda: observer.pixel() == '116633', 1.5)
            row['restored_pixel'] = observer.pixel()
            observer.clicks()
            observer.click()
            assert observer.clicks() == 1, 'underlying native input did not recover'
            row['input_restored_ns'] = time.monotonic_ns()
            assert 0 <= row['input_restored_ns'] - started <= 1_500_000_000
            result = process.wait(timeout=3)
            assert result == (-9 if name == 'OWNER-LOSS' else 69 if name == 'MAPPING-LOSS' else 0)
            if name != 'OWNER-LOSS':
                final = events()[-1]
                cooperative = name in ('KEY-LIVE', 'MAPPING-LOSS')
                assert final['event'] == ('child_exit' if cooperative else 'child_signal')
                assert final['value'] == (0 if cooperative else 9)
                assert not any(item['event'] in ('deadline', 'unconfirmed') for item in events())
                assert any(item['event'] == 'mapping_lost' for item in events()) == (name == 'MAPPING-LOSS')
                if 'FROZEN' in name:
                    assert any(item['event'] == 'force_stop' for item in events())
            assert not stderr.read_bytes(), 'unexpected native diagnostic'
        observer.grab()
        observer.ungrab()
        row['shortcut_released'] = True
        row['owner_events'] = events()
        row['result'] = 'pass'
    finally:
        if process and process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        if child_fd is not None:
            if not select.select([child_fd], [], [], 0)[0]:
                signal.pidfd_send_signal(child_fd, signal.SIGKILL)
            row['child_exit_at_cleanup'] = bool(select.select([child_fd], [], [], 2)[0])
            os.close(child_fd)
        if owner_fd is not None:
            os.close(owner_fd)
        if observer:
            observer.close()
        if server:
            server.terminate()
            try:
                server.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate(timeout=3)
            row['display_exit'] = server.returncode
        if stdout.exists():
            row['owner_stdout_sha256'] = sha(stdout)
        if stderr.exists():
            row['owner_stderr_sha256'] = sha(stderr)


def main():
    executable = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    if len(sys.argv) == 5 and sys.argv[3] == '--case':
        name = sys.argv[4]
        assert name in CASES
        row = {'case': name, 'result': 'fail'}
        try:
            run_case(executable, name, output, row)
        except Exception as error:
            row['error'] = type(error).__name__ + ': ' + str(error)
            row['traceback'] = traceback.format_exc()
        (output / 'result.json').write_text(json.dumps(row, indent=2) + '\n')
        return 0 if row['result'] == 'pass' else 1
    attempt = output / ('EDITOR-EXIT-01-' + uuid.uuid4().hex)
    attempt.mkdir(mode=0o700, parents=True)
    sources = ['tests/desktop/native_editor_exit.py', 'tests/desktop/native_oracle.py', 'tests/fault/native_diagnostic.py',
               'source/interfaces/editor_exit_x11.cpp', 'source/interfaces/editor_exit_x11.hpp', 'source/application/editor_exit_probe.cpp',
               'source/platform/child_linux.cpp', 'source/platform/child.hpp', 'spec/delivery/packages/w-25-editor-exit.md',
               'CMakeLists.txt', 'source/build/components.json', 'source/build/targets/linux-x64-gcc13.json']
    record = {'family': 'EDITOR-EXIT-01', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {path: sha(ROOT / path) for path in sources}, 'executable_sha256': sha(executable),
              'environment': {'uname': list(os.uname()), 'python': sys.version,
                  'runtime_files': {name: sha(Path(name)) for name in ['/usr/bin/Xvfb', '/usr/lib/x86_64-linux-gnu/libX11.so.6',
                      '/usr/lib/x86_64-linux-gnu/libXtst.so.6', '/usr/lib/x86_64-linux-gnu/libgtk-3.so.0']}},
              'cases': [], 'limitations': ['Owned Xvfb lifetime experiment; no real editor transactions, installed recovery or desktop qualification.']}
    for name in CASES:
        workspace = attempt / name
        workspace.mkdir(mode=0o700)
        try:
            command = [sys.executable, str(Path(__file__).resolve()), str(executable), str(workspace), '--case', name]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            assert os.getsid(process.pid) == process.pid and os.getpgid(process.pid) == process.pid
            try:
                out, err = process.communicate(timeout=25)
            except subprocess.TimeoutExpired:
                # The held, unreaped session leader still owns this private group.
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=3)
                raise
            path = workspace / 'result.json'
            row = json.loads(path.read_text()) if path.exists() else {'case': name, 'result': 'fail', 'error': 'observer did not produce evidence'}
            row['observer_exit'] = process.returncode
            if process.returncode or out or err:
                row['result'] = 'fail'
                row['observer_stdout'] = out.decode(errors='replace')[-2000:]
                row['observer_stderr'] = err.decode(errors='replace')[-2000:]
        except subprocess.TimeoutExpired:
            row = {'case': name, 'result': 'fail', 'error': 'observer exceeded 25-second bound'}
        record['cases'].append(row)
        attempt.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
        print(name, row['result'], row.get('error', ''), flush=True)
    record['result'] = 'pass' if all(row['result'] == 'pass' for row in record['cases']) else 'fail'
    attempt.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    print(attempt.with_suffix('.json'))
    return 0 if record['result'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())

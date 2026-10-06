"""Bounded read-only Windows shell topology; never captures or changes a desktop."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ['tests/desktop/windows_host_inventory.py',
           'tests/desktop/test_windows_host_inventory.py',
           'spec/delivery/packages/w-03-windows-investigation.md']
CLASSES = {'Progman', 'WorkerW', 'SHELLDLL_DefView', 'SysListView32'}


def classify(value):
    """Classify structural observation only; no attachment/visibility authority."""
    first, second = value['observations']
    if not first['shell'] and not second['shell']:
        return {'status': 'absent', 'icon_root': None, 'worker_roots': []}
    result = {'status': 'owner_unverified', 'icon_root': None, 'worker_roots': []}
    owner = value['owner']
    if not owner or not owner['image_matches_system_explorer'] or not owner['alive_after'] or owner['session'] != value['session']:
        return result
    if first != second:
        result['status'] = 'changed'
        return result
    nodes = first['windows']
    if not first['shell'] or not any(n['hwnd'] == first['shell'] and n['pid'] == owner['pid'] for n in nodes):
        result['status'] = 'changed'
        return result
    if any(n['pid'] != owner['pid'] for n in nodes):
        return result
    if len({n['hwnd'] for n in nodes}) != len(nodes) or any(n['class'] not in CLASSES for n in nodes):
        raise ValueError('Malformed native topology')
    roots = {n['hwnd']: n for n in nodes if n['parent'] is None and n['class'] in ('Progman', 'WorkerW')}
    views = [n for n in nodes if n['class'] == 'SHELLDLL_DefView']
    icons = [n for n in nodes if n['class'] == 'SysListView32']
    result['worker_roots'] = sorted(n['hwnd'] for n in roots.values() if n['class'] == 'WorkerW')
    result['status'] = 'incomplete'
    if len(views) > 1 or len(icons) > 1:
        result['status'] = 'ambiguous'
    elif len(views) == len(icons) == 1 and views[0]['parent'] in roots and icons[0]['parent'] == views[0]['hwnd']:
        result['status'] = 'observed'
        result['icon_root'] = views[0]['parent']
    return result


def observe():
    import ctypes as C
    from ctypes import wintypes as W
    if sys.platform != 'win32':
        raise RuntimeError('Native Windows execution required')
    user = C.WinDLL('user32', use_last_error=True)
    kernel = C.WinDLL('kernel32', use_last_error=True)
    callback_type = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)

    def api(library, name, restype, *args):
        call = getattr(library, name)
        call.restype, call.argtypes = restype, args
        return call

    shell_window = api(user, 'GetShellWindow', W.HWND)
    window_owner = api(user, 'GetWindowThreadProcessId', W.DWORD, W.HWND, C.POINTER(W.DWORD))
    window_class = api(user, 'GetClassNameW', C.c_int, W.HWND, W.LPWSTR, C.c_int)
    parent_window = api(user, 'GetAncestor', W.HWND, W.HWND, W.UINT)
    enum_windows = api(user, 'EnumWindows', W.BOOL, callback_type, W.LPARAM)
    enum_children = api(user, 'EnumChildWindows', W.BOOL, W.HWND, callback_type, W.LPARAM)
    open_process = api(kernel, 'OpenProcess', W.HANDLE, W.DWORD, W.BOOL, W.DWORD)
    close_handle = api(kernel, 'CloseHandle', W.BOOL, W.HANDLE)
    process_times = api(kernel, 'GetProcessTimes', W.BOOL, W.HANDLE, *([C.POINTER(W.FILETIME)] * 4))
    image_name = api(kernel, 'QueryFullProcessImageNameW', W.BOOL, W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD))
    process_session = api(kernel, 'ProcessIdToSessionId', W.BOOL, W.DWORD, C.POINTER(W.DWORD))
    wait = api(kernel, 'WaitForSingleObject', W.DWORD, W.HANDLE, W.DWORD)
    station = api(user, 'GetProcessWindowStation', W.HANDLE)
    thread_desktop = api(user, 'GetThreadDesktop', W.HANDLE, W.DWORD)
    thread_id = api(kernel, 'GetCurrentThreadId', W.DWORD)
    object_info = api(user, 'GetUserObjectInformationW', W.BOOL, W.HANDLE, C.c_int, W.LPVOID, W.DWORD, C.POINTER(W.DWORD))
    windows_directory = api(kernel, 'GetWindowsDirectoryW', W.UINT, W.LPWSTR, W.UINT)

    def require(success):
        if not success:
            raise C.WinError(C.get_last_error())

    def session(pid):
        value = W.DWORD()
        require(process_session(pid, C.byref(value)))
        return value.value

    def object_name(handle):
        if not handle:
            raise C.WinError(C.get_last_error())
        name, needed = C.create_unicode_buffer(256), W.DWORD()
        require(object_info(handle, 2, name, C.sizeof(name), C.byref(needed)))
        return name.value

    def window(hwnd, top):
        name, pid = C.create_unicode_buffer(256), W.DWORD()
        require(window_class(hwnd, name, len(name)))
        tid = window_owner(hwnd, C.byref(pid))
        require(tid)
        return {'hwnd': int(hwnd), 'class': name.value, 'pid': pid.value, 'thread': tid,
                'parent': None if top else int(parent_window(hwnd, 1) or 0)}

    def enumerate_with(function, visitor, limit, *prefix):
        count, errors = 0, []

        @callback_type
        def callback(hwnd, _):
            nonlocal count
            try:
                count += 1
                if count > limit:
                    raise ValueError('Native enumeration capacity')
                visitor(hwnd)
                return True
            except Exception as error:
                errors.append(error)
                return False

        C.set_last_error(0)
        result = function(*prefix, callback, 0)
        if errors:
            raise errors[0]
        # EnumChildWindows explicitly has no meaningful return value.
        if not prefix:
            require(result)
        return count

    own_session = session(os.getpid())
    initial_shell = int(shell_window() or 0)
    shell_pid = W.DWORD()
    if initial_shell:
        require(window_owner(initial_shell, C.byref(shell_pid)))
    process = None
    owner = None
    owner_error = None
    try:
        if initial_shell:
            process = open_process(0x1000 | 0x100000, False, shell_pid.value)
            if not process:
                owner_error = C.get_last_error()
            else:
                created, exited, system, used = (W.FILETIME() for _ in range(4))
                require(process_times(process, C.byref(created), C.byref(exited), C.byref(system), C.byref(used)))
                name, size = C.create_unicode_buffer(32768), W.DWORD(32768)
                require(image_name(process, 0, name, C.byref(size)))
                directory = C.create_unicode_buffer(32768)
                length = windows_directory(directory, len(directory))
                require(0 < length < len(directory))
                image = Path(name.value)
                expected = Path(directory.value) / 'explorer.exe'
                # QueryFullProcessImageNameW already returns the native full path.
                # Do not resolve/read an arbitrary custom shell executable.
                matches = image == expected.resolve(strict=True)
                owner = {'pid': shell_pid.value, 'creation_filetime': str((created.dwHighDateTime << 32) | created.dwLowDateTime),
                         'session': session(shell_pid.value), 'image_matches_system_explorer': matches,
                         'image': str(expected) if matches else None,
                         'image_sha256': sha(expected) if matches else None, 'alive_after': False}

        observations = []
        metrics = []
        for index in range(2):
            if index:
                time.sleep(.1)
            begin = time.monotonic_ns()
            roots = []

            def retain_root(hwnd):
                node = window(hwnd, True)
                if node['pid'] == shell_pid.value and node['class'] in ('Progman', 'WorkerW'):
                    roots.append(node)
                    if len(roots) > 32:
                        raise ValueError('Native root capacity')

            count = enumerate_with(enum_windows, retain_root, 4096)
            nodes = list(roots)
            descendants = []

            def retain_child(hwnd):
                node = window(hwnd, False)
                if node['class'] in ('SHELLDLL_DefView', 'SysListView32'):
                    nodes.append(node)

            for root in roots:
                descendants.append(enumerate_with(enum_children, retain_child, 512, root['hwnd']))
            observations.append({'shell': int(shell_window() or 0), 'windows': sorted(nodes, key=lambda n: n['hwnd'])})
            metrics.append({'begin_ns': begin, 'end_ns': time.monotonic_ns(), 'top_level_visited': count, 'descendants_visited': descendants})
        if owner:
            owner['alive_after'] = wait(process, 0) == 258  # WAIT_TIMEOUT: held process still live.
        value = {'version': 1, 'session': own_session, 'station': object_name(station()),
                 'desktop': object_name(thread_desktop(thread_id())),
                 'os': {'major': sys.getwindowsversion().major, 'minor': sys.getwindowsversion().minor,
                        'build': sys.getwindowsversion().build},
                 'owner': owner, 'owner_error': owner_error, 'observations': observations, 'intervals': metrics}
        value['decision'] = classify(value)
        return value
    finally:
        if process:
            require(close_handle(process))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.argv[1:] == ['--worker']:
        try:
            value = observe()
            raw = json.dumps(value)
            if len(raw.encode()) > 1024 * 1024:
                raise ValueError('Native report capacity')
            print(raw)
            return 0
        except Exception as error:
            print(json.dumps({'error': type(error).__name__ + ': ' + str(error)}))
            return 1
    if sys.argv[1:]:
        raise ValueError('No native arguments accepted except internal --worker')
    parent = (ROOT / 'out/campaign').resolve(strict=True)
    if parent != ROOT / 'out/campaign':
        raise ValueError('Owned output root required')
    work = parent / ('WINDOWS-HOST-INVENTORY-01-' + uuid.uuid4().hex)
    work.mkdir()
    archive = work / 'source-inputs.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for source in SOURCES:
            bundle.write(ROOT / source, source)
    command = [sys.executable, '-X', 'utf8', str(Path(__file__).resolve()), '--worker']
    report = {'family': 'WINDOWS-HOST-INVENTORY-01', 'started_at': datetime.now(timezone.utc).isoformat(),
              'source_base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {p: sha(ROOT / p) for p in SOURCES},
              'source_archive': {'path': str(archive), 'sha256': sha(archive)}, 'command': command,
              'python_sha256': sha(Path(sys.executable)), 'python_version': sys.version,
              'qualification': {'host': 'not_run', 'pixels': 'not_run', 'icon_input': 'not_run', 'shell_recovery': 'not_run'},
              'scope': 'Read-only native structural observation; no shell mutation, input, window titles or pixels.'}
    with (work / 'stdout.json').open('wb') as output, (work / 'stderr.txt').open('wb') as errors:
        child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=output, stderr=errors,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        report['child_pid'] = child.pid
        try:
            report['exit'] = child.wait(timeout=8)
        except subprocess.TimeoutExpired:
            child.kill()
            report['exit'] = child.wait(timeout=5)
            report['error'] = 'Native observer exceeded eight seconds'
    report['child_exit_confirmed'] = child.poll() is not None
    for name in ('stdout.json', 'stderr.txt'):
        path = work / name
        if path.stat().st_size > 1024 * 1024:
            report['error'] = 'Native output capacity exceeded'
    if not report.get('error'):
        try:
            report['native'] = json.loads((work / 'stdout.json').read_text(encoding='utf-8'))
            if report['exit'] == 0:
                if classify(report['native']) != report['native']['decision']:
                    raise ValueError('Native decision differs')
        except (ValueError, KeyError) as error:
            report['error'] = type(error).__name__ + ': ' + str(error)
    report['outputs'] = {name: {'sha256': sha(work / name), 'bytes': (work / name).stat().st_size} for name in ('stdout.json', 'stderr.txt')}
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report['outcome'] = 'observed' if report['exit'] == 0 and not report.get('error') else 'error'
    path = work / 'report.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(path)
    print(report['outcome'], report.get('native', {}).get('decision', {}).get('status', report.get('error', '')))
    return 0 if report['outcome'] == 'observed' else 1


if __name__ == '__main__':
    sys.exit(main())

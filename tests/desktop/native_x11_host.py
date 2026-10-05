"""Run bounded Openbox/PCManFM candidate investigations on an owned Xvfb server.

Exit zero means the investigation completed, not that its candidate conformed.
No inherited desktop is captured and no user shell/session is controlled.
"""
import argparse
import base64
import ctypes as C
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import re
import select
import signal
import subprocess
import sys
import time
import uuid
import zlib

from native_oracle import Display, ClassHint, launch_xvfb, sha, ROOT
from oracle import decode, evaluate, pack_frame, unpack_frame


def rgb_record(pixels):
    return {'bytes': len(pixels), 'sha256': hashlib.sha256(pixels).hexdigest(),
            'rgb_zlib_base64': base64.b64encode(zlib.compress(pixels)).decode('ascii')}


def fixture_identity(workspace):
    desktop = workspace / 'Desktop'
    names = sorted(p.name for p in desktop.iterdir())
    if names != ['Probe Folder', 'Second Folder'] or any((desktop / n).is_symlink() for n in names):
        raise ValueError('synthetic desktop fixture changed')
    if sorted(p.name for p in (desktop / 'Probe Folder').iterdir()) != ['Sentinel.txt'] or list((desktop / 'Second Folder').iterdir()):
        raise ValueError('synthetic folder contents changed')
    sentinel = desktop / 'Probe Folder/Sentinel.txt'
    if sentinel.is_symlink():
        raise ValueError('synthetic sentinel became a symlink')
    return {'folders': names, 'Probe Folder/Sentinel.txt': {'bytes': sentinel.stat().st_size, 'sha256': sha(sentinel)}}


class DesktopDisplay(Display):
    def __init__(self):
        super().__init__()
        p, w, i = C.c_void_p, C.c_ulong, C.c_int
        self.x.XGetInputFocus.argtypes = [p, C.POINTER(w), C.POINTER(i)]
        self.x.XTranslateCoordinates.argtypes = [p, w, w, i, i, C.POINTER(i), C.POINTER(i), C.POINTER(w)]
        self.x.XStringToKeysym.argtypes = [C.c_char_p]
        self.x.XStringToKeysym.restype = w
        self.x.XKeysymToKeycode.argtypes = [p, w]
        self.x.XKeysymToKeycode.restype = C.c_ubyte
        self.xtest = C.CDLL('libXtst.so.6')
        self.xtest.XTestFakeKeyEvent.argtypes = [p, C.c_uint, i, w]

    def native_class(self, window):
        hint = ClassHint()
        if not self.x.XGetClassHint(self.handle, window, C.byref(hint)):
            return None
        try:
            return [C.string_at(hint.name, min(len(C.string_at(hint.name)), 256)).decode('utf-8', errors='replace'),
                    C.string_at(hint.kind, min(len(C.string_at(hint.kind)), 256)).decode('utf-8', errors='replace')]
        finally:
            self.x.XFree(hint.name)
            self.x.XFree(hint.kind)

    def structure(self, candidate=0):
        focus, revert = C.c_ulong(), C.c_int()
        self.x.XGetInputFocus(self.handle, C.byref(focus), C.byref(revert))
        clients = self.property(self.root, '_NET_CLIENT_LIST_STACKING')
        return {'client_order_bottom_to_top': clients, 'focus': focus.value,
                'showing_desktop': self.property(self.root, '_NET_SHOWING_DESKTOP'),
                'active_window': self.property(self.root, '_NET_ACTIVE_WINDOW'),
                'candidate': candidate,
                'clients': [{'window': w, 'class': self.native_class(w),
                             'pid': self.property(w, '_NET_WM_PID'),
                             'type': self.property(w, '_NET_WM_WINDOW_TYPE')} for w in clients]}

    def reveal_key(self):
        keys = [self.x.XKeysymToKeycode(self.handle, self.x.XStringToKeysym(name))
                for name in (b'Super_L', b'd')]
        if not all(keys):
            raise RuntimeError('native reveal key map absent')
        for key, pressed in [(keys[0], True), (keys[1], True), (keys[1], False), (keys[0], False)]:
            if not self.xtest.XTestFakeKeyEvent(self.handle, key, pressed, 0):
                raise RuntimeError('XTEST key stimulus failed')
        self.x.XFlush(self.handle)


def observe(environment, channel, workspace, wallpaper_mode, icon_input=False, restart_window_manager=False):
    os.environ.update(environment)
    display = None
    try:
        display = DesktopDisplay()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if display.property(display.root, '_NET_SUPPORTING_WM_CHECK'):
                break
            time.sleep(.05)
        else:
            raise TimeoutError('window manager did not become ready')
        channel.send({'wm_ready': True})
        if channel.recv() != {'desktop_started': True}:
            raise ValueError('desktop startup sequence')
        deadline = time.monotonic() + 5
        desktop = None
        while time.monotonic() < deadline:
            state = display.structure()
            desktop = next((c['window'] for c in state['clients'] if c['class'] and c['class'][1] == 'Pcmanfm'), None)
            if desktop and state['showing_desktop'] == [0]:
                break
            time.sleep(.05)
        else:
            raise TimeoutError('native window/icon manager did not become ready: ' + str(state))
        time.sleep(.3)
        channel.send({'icon_manager_ready': True})
        if channel.recv() != {'wallpaper_setup_complete': True}:
            raise ValueError('wallpaper setup sequence')
        time.sleep(.3)
        baseline = display.capture()
        wallpaper = display.capture(600, 400, 128, 96)
        ppm = (workspace / 'wallpaper.ppm').read_bytes()
        header = b'P6\n800 600\n255\n'
        if not ppm.startswith(header) or len(ppm) != len(header) + 800*600*3:
            raise ValueError('configured PPM fixture shape')
        wallpaper_rgb = ppm[len(header):]
        expected_region = (bytes((48, 72, 96))*128*96 if wallpaper_mode == 'color' else
                           b''.join(wallpaper_rgb[(y*800+600)*3:(y*800+728)*3] for y in range(400, 496)))
        if wallpaper != expected_region:
            raise ValueError('configured wallpaper pixels do not match the independently read fixture')
        expected_background = bytes(channel for y in range(32, 128) for x in range(32, 160)
                                    for channel in ((48, 72, 96) if wallpaper_mode == 'color' or (x // 40 + y // 40) % 2
                                                    else (64, 88, 112)))
        icon_mask = [n for n in range(0, len(baseline), 3) if baseline[n:n+3] != expected_background[n:n+3]]
        if len(icon_mask) < 100:
            raise RuntimeError('known icon observation region has no sufficient icon content')
        channel.send({'ready': True, 'desktop_window': desktop, 'before': state,
                      'baseline_icon_region': rgb_record(baseline), 'wallpaper_region': rgb_record(wallpaper),
                      'baseline_desktop': rgb_record(display.capture(0, 0, 800, 600)),
                      'configured_wallpaper_rgb': rgb_record(wallpaper_rgb), 'wallpaper_fixture_display_verified': True})
        command = channel.recv()
        window, pid = command['window'], command['pid']
        display.verify(window, pid)
        time.sleep(.15)
        x, y, child = C.c_int(), C.c_int(), C.c_ulong()
        if not display.x.XTranslateCoordinates(display.handle, window, display.root, 0, 0, C.byref(x), C.byref(y), C.byref(child)):
            raise ValueError('candidate position unavailable')
        if (x.value, y.value) != (32, 32):
            raise ValueError('candidate not in fixed observation region: ' + str((x.value, y.value)))
        display.send(window, 1)
        time.sleep(.25)  # Record a missing baseline instead of hiding placement failure.
        start = time.monotonic_ns()
        now = lambda: (time.monotonic_ns() - start) // 1000
        trace = {'version': '0.1.0', 'start_us': 0, 'end_us': 2400000,
                 'stimuli': [{'at_us': 0, 'generation': 1}], 'frames': []}
        actions, structures = [], []
        schedule = [(300000, 'reveal'), (700000, 2), (1500000, 'restore'), (1800000, 3)]
        with (workspace / 'frames.jsonl').open('x', encoding='utf-8', newline='\n') as journal:
            def preserve(kind, value):
                journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
                journal.flush()
            preserve('interval', {'start_us': 0, 'end_us': trace['end_us']})
            preserve('stimulus', trace['stimuli'][0])
            next_capture = 0
            while now() < trace['end_us']:
                elapsed = now()
                if schedule and elapsed >= schedule[0][0]:
                    _, action = schedule.pop(0)
                    issued = now()
                    if isinstance(action, int):
                        display.send(window, action)
                        trace['stimuli'].append({'at_us': issued, 'generation': action})
                        preserve('stimulus', trace['stimuli'][-1])
                    else:
                        display.reveal_key()
                        actions.append({'at_us': issued, 'action': 'Openbox ToggleShowDesktop / W-d', 'intent': action})
                        preserve('action', actions[-1])
                if elapsed < next_capture:
                    time.sleep(min(.01, (next_capture - elapsed) / 1000000))
                    continue
                begin = now()
                pixels = display.capture()
                finish = now()
                if finish > trace['end_us']:
                    break
                frame = pack_frame(pixels, begin, finish)
                trace['frames'].append(frame)
                preserve('frame', frame)
                state = display.structure(window)
                state['at_us'] = now()
                structures.append(state)
                preserve('structure', state)
                next_capture = finish + 50000
        result = evaluate(trace)
        exposed = [s for s in structures if 500000 <= s['at_us'] < 1450000]
        restored = [s for s in structures if s['at_us'] >= 1750000]
        action_confirmed = bool(exposed and restored) and all(s['showing_desktop'] == [1] for s in exposed) and all(s['showing_desktop'] == [0] for s in restored)
        first_pixels = unpack_frame(trace['frames'][0])
        hidden_icon_pixels = sum(first_pixels[n:n+3] != baseline[n:n+3] for n in icon_mask)
        # Diagnostic fact, never substitute stacking/pixel equality for conformance.
        relation = []
        for s in structures:
            order = s['client_order_bottom_to_top']
            relation.append('above' if window in order and desktop in order and order.index(window) > order.index(desktop)
                            else 'below' if window in order and desktop in order else 'unavailable')
        input_result = {'outcome': 'not_run', 'steps': []}
        if icon_input:
            from x11_input import InputObserver
            import faulthandler
            with (workspace / 'input-timeout.log').open('x', encoding='utf-8') as timeout_log:
                faulthandler.dump_traceback_later(8, file=timeout_log)
                try:
                    inputs = InputObserver(display, command['manager_pid'], workspace, desktop)
                    try:
                        input_result = inputs.run(window, rgb_record)
                    finally:
                        inputs.close()
                finally:
                    faulthandler.cancel_dump_traceback_later()
        recovery_result = {'outcomes': {'manager_recovery': 'not_run'}}
        if restart_window_manager:
            from x11_recovery import observe_recovery
            recovery_result = observe_recovery(display, channel, workspace, command, baseline, icon_mask, wallpaper)
        channel.send({'trace': trace, 'observation': result, 'actions': actions, 'structures': structures,
                      'recovery_observation': recovery_result,
                      'input_observation': input_result,
                      'reveal_action_confirmed': action_confirmed, 'candidate_relative_to_icons': sorted(set(relation)),
                      'baseline_generation': decode(first_pixels), 'baseline_matches_icon_manager': first_pixels == baseline,
                      'icon_pixels': {'baseline_non_background': len(icon_mask), 'changed_under_candidate': hidden_icon_pixels,
                                      'scope': 'Fixed icon region, before native input; exact RGB comparison, no candidate-supplied image.'},
                      'wallpaper_pixels_unchanged_during': display.capture(600, 400, 128, 96) == wallpaper})
        display.send(window)
        if channel.recv() != {'candidate_exited': True}:
            raise RuntimeError('candidate exit not confirmed')
        time.sleep(.1)
        channel.send({'icon_region_restored': display.capture() == baseline,
                      'wallpaper_pixels_unchanged_after': display.capture(600, 400, 128, 96) == wallpaper,
                      'after': display.structure()})
    except Exception as error:
        channel.send({'error': type(error).__name__ + ': ' + str(error)})
    finally:
        if display:
            display.close()
        channel.close()


def configure(workspace, sysroot, rendering, wallpaper_mode):
    for name in ('config', 'data', 'cache', 'run', 'Desktop'):
        (workspace / name).mkdir(mode=0o700)
    (workspace / 'Desktop/Probe Folder').mkdir()
    (workspace / 'Desktop/Second Folder').mkdir()
    (workspace / 'Desktop/Probe Folder/Sentinel.txt').write_text('Synthetic native folder-open sentinel.\n', encoding='utf-8')
    config = workspace / 'config'
    (config / 'pcmanfm/syspane-lab').mkdir(parents=True)
    (config / 'gtk-3.0').mkdir()
    (config / 'gtk-3.0/settings.ini').write_text('[Settings]\ngtk-icon-theme-name=Adwaita\ngtk-theme-name=Adwaita\n', encoding='utf-8')
    (config / 'user-dirs.dirs').write_text(''.join('XDG_' + name + '_DIR="' + str(workspace / 'Desktop') + '"\n'
                                                for name in ('DESKTOP', 'DOCUMENTS', 'TEMPLATES', 'DOWNLOAD', 'MUSIC', 'PICTURES', 'VIDEOS', 'PUBLICSHARE')), encoding='utf-8')
    wallpaper = workspace / 'wallpaper.ppm'
    pixels = bytes(channel for y in range(600) for x in range(800)
                   for channel in ((48, 72, 96) if (x // 40 + y // 40) % 2 else (64, 88, 112)))
    wallpaper.write_bytes(b'P6\n800 600\n255\n' + pixels)
    desktop_config = config / 'pcmanfm/syspane-lab/desktop-items-0.conf'
    desktop_config.write_text('[*]\nwallpaper_mode=' + wallpaper_mode + '\nwallpaper_common=1\nwallpaper=' + str(wallpaper) +
                              '\ndesktop_bg=#304860\ndesktop_fg=#ffffff\ndesktop_shadow=#000000\ndesktop_font=Sans 10\n'
                              'show_wm_menu=0\nshow_documents=0\nshow_trash=0\nshow_mounts=0\nfolder=' + str(workspace / 'Desktop') + '\n', encoding='utf-8')
    (config / 'openbox.xml').write_text('''<?xml version="1.0"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
<theme><name>Clearlooks</name><keepBorder>no</keepBorder></theme><desktops><number>1</number></desktops>
<keyboard><keybind key="W-d"><action name="ToggleShowDesktop"/></keybind></keyboard>
<applications><application class="SysPaneOracleProbe"><decor>no</decor><focus>no</focus>
<position force="yes"><x>32</x><y>32</y></position></application></applications>
</openbox_config>
''', encoding='utf-8')
    # Native-cache paths exceed sockaddr_un's path ceiling. A unique abstract
    # address has EXTERNAL same-uid authentication and no filesystem socket.
    bus_address = 'unix:abstract=syspane-x11-' + uuid.uuid4().hex
    (config / 'bus.xml').write_text('<busconfig><type>session</type><listen>' + bus_address + '</listen>'
                                  '<policy context="default"><allow send_destination="*"/><allow receive_sender="*"/><allow own="*"/></policy></busconfig>', encoding='utf-8')
    environment = {'XDG_CONFIG_HOME': str(config), 'XDG_DATA_HOME': str(workspace / 'data'),
                   'XDG_CACHE_HOME': str(workspace / 'cache'), 'XDG_RUNTIME_DIR': str(workspace / 'run'),
                   'XDG_CONFIG_DIRS': str(sysroot / 'etc/xdg'),
                   'XDG_DATA_DIRS': str(sysroot / 'usr/share') + ':/usr/share',
                   'LD_LIBRARY_PATH': str(sysroot / 'usr/lib/x86_64-linux-gnu'),
                   'DBUS_SESSION_BUS_ADDRESS': bus_address, 'DBUS_SYSTEM_BUS_ADDRESS': 'unix:path=' + str(workspace / 'run/no-system-bus'),
                   'GIO_USE_VFS': 'local', 'GSETTINGS_BACKEND': 'memory', 'NO_AT_BRIDGE': '1',
                   'GTK_USE_PORTAL': '0', 'GDK_BACKEND': 'x11', 'GDK_RENDERING': rendering, 'LC_ALL': 'C.UTF-8'}
    return environment, [wallpaper, desktop_config]


def receive(channel, logs, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(p.stat().st_size > 1024**2 for p in logs):
            raise RuntimeError('lab process log exceeded 1 MiB budget')
        if channel.poll(.1):
            result = channel.recv()
            if 'error' in result:
                raise RuntimeError(result['error'])
            return result
    raise TimeoutError('bounded native observer timeout')


def run_case(build, sysroot, output, mode, rendering, wallpaper_mode, delayed_wallpaper=False, icon_input=False, restart_window_manager=False):
    workspace = output / ('x11-' + mode + '-' + uuid.uuid4().hex)
    workspace.mkdir(mode=0o700)
    row = {'candidate': mode, 'execution': 'failed', 'workspace': str(workspace.relative_to(build))}
    server = worker = channel = runtime_fd = None
    processes, logs, handles = [], [], []
    try:
        additions, preserved = configure(workspace, sysroot, rendering, 'color' if delayed_wallpaper else wallpaper_mode)
        server, environment = launch_xvfb(workspace)
        environment.update(additions)
        environment.pop('WAYLAND_DISPLAY', None)
        environment.pop('SESSION_MANAGER', None)
        if icon_input:
            runtime_fd = os.open(workspace / 'run', os.O_RDONLY | os.O_DIRECTORY)
            environment['XDG_RUNTIME_DIR'] = '/proc/' + str(os.getpid()) + '/fd/' + str(runtime_fd)
            environment.pop('NO_AT_BRIDGE', None)
            environment['AT_SPI_BUS_ADDRESS'] = environment['DBUS_SESSION_BUS_ADDRESS']
            environment['GTK_MODULES'] = 'atk-bridge'
        def launch(name, command, stdout=None):
            log = workspace / (name + '.log')
            handle = log.open('xb')
            handles.append(handle)
            logs.append(log)
            process = subprocess.Popen(command, cwd=workspace, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout if stdout is not None else handle, stderr=handle, start_new_session=True)
            processes.append((name, process))
            return process
        launch('bus', ['/usr/bin/dbus-daemon', '--nofork', '--nopidfile', '--nosyslog', '--config-file=' + str(workspace / 'config/bus.xml')])
        if icon_input:
            # Explicitly owned registry; no inherited accessibility service or activation.
            registry = launch('registry', ['/usr/libexec/at-spi2-registryd'])
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                ready = subprocess.run(['/usr/bin/gdbus', 'call', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
                                        '--dest', 'org.freedesktop.DBus', '--object-path', '/org/freedesktop/DBus',
                                        '--method', 'org.freedesktop.DBus.GetConnectionUnixProcessID', 'org.a11y.atspi.Registry'],
                                       env=environment, capture_output=True, text=True, timeout=1)
                if ready.returncode == 0 and ready.stdout.strip() == '(uint32 ' + str(registry.pid) + ',)':
                    row['registry_identity_confirmed'] = registry.pid
                    break
                time.sleep(.05)
            else:
                raise TimeoutError('owned accessibility registry did not acquire its bus name')
        wm_command = [str(sysroot / 'usr/bin/openbox'), '--config-file', str(workspace / 'config/openbox.xml')]
        wm = launch('openbox', wm_command)
        context = mp.get_context('spawn')
        channel, remote = context.Pipe()
        worker = context.Process(target=observe, args=(environment, remote, workspace, wallpaper_mode, icon_input, restart_window_manager))
        worker.start()
        remote.close()
        row.update(receive(channel, logs))
        manager = launch('pcmanfm', [str(sysroot / 'usr/bin/pcmanfm'), '--profile=syspane-lab', '--desktop'])
        channel.send({'desktop_started': True})
        row.update(receive(channel, logs))
        if delayed_wallpaper:
            setup = subprocess.run([str(sysroot / 'usr/bin/pcmanfm'), '--profile=syspane-lab',
                                    '--set-wallpaper=' + str(workspace / 'wallpaper.ppm'), '--wallpaper-mode=' + wallpaper_mode],
                                   cwd=workspace, env=environment, stdin=subprocess.DEVNULL, capture_output=True, timeout=3)
            row['wallpaper_setup'] = {'exit': setup.returncode, 'stdout': setup.stdout.decode('utf-8', errors='replace'),
                                      'stderr': setup.stderr.decode('utf-8', errors='replace')}
            if setup.returncode:
                raise RuntimeError('native wallpaper setup failed')
        channel.send({'wallpaper_setup_complete': True})
        row.update(receive(channel, logs))
        if any(process.poll() is not None for _, process in processes):
            raise RuntimeError('lab service exited before candidate startup')
        row['preserved_before'] = {p.relative_to(workspace).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in preserved}
        row['fixture_before'] = fixture_identity(workspace)
        candidate = launch('candidate', [str(build / 'SysPane.OracleProbe'), mode], subprocess.PIPE)
        bootstrap = b''
        deadline = time.monotonic() + 3
        while not bootstrap.endswith(b'\n') and len(bootstrap) < 256 and time.monotonic() < deadline:
            if select.select([candidate.stdout], [], [], .1)[0]:
                byte = os.read(candidate.stdout.fileno(), 1)
                if not byte:
                    break
                bootstrap += byte
        info = json.loads(bootstrap)
        if set(info) != {'window', 'pid', 'claims_visible'} or info['pid'] != candidate.pid:
            raise ValueError('candidate bootstrap identity')
        channel.send({**info, 'manager_pid': manager.pid, 'window_manager_pid': wm.pid})
        if restart_window_manager:
            request = receive(channel, logs)
            if request != {'restart_requested': 'openbox', 'pid': wm.pid} or wm.poll() is not None:
                raise ValueError('owned window-manager restart request')
            wm.kill()
            wm.wait(timeout=2)
            channel.send({'manager_stopped': wm.pid, 'exit': wm.returncode})
            if receive(channel, logs, 2) != {'exit_observed': wm.pid}:
                raise ValueError('independent window-manager exit acknowledgement')
            time.sleep(.4)
            replacement = launch('openbox-replacement', wm_command)
            channel.send({'replacement_started': replacement.pid})
        row.update(receive(channel, logs, 14 if icon_input else 8))
        candidate.wait(timeout=3)
        if candidate.returncode != 0:
            raise RuntimeError('candidate did not exit cleanly')
        channel.send({'candidate_exited': True})
        row.update(receive(channel, logs))
        row['preserved_after'] = {p.relative_to(workspace).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in preserved}
        row['fixture_after'] = fixture_identity(workspace)
        if row['fixture_before'] != row['fixture_after']:
            raise RuntimeError('synthetic folder fixture changed during native input')
        row['wallpaper_preservation'] = 'pass' if row['preserved_before'] == row['preserved_after'] and row['wallpaper_pixels_unchanged_during'] and row['wallpaper_pixels_unchanged_after'] else 'fail'
        row['wallpaper_preservation_scope'] = 'Configured solid color; file unchanged but not displayed' if wallpaper_mode == 'color' else 'Configured image file and observed wallpaper region'
        row['placement'] = 'fail' if row['icon_pixels']['changed_under_candidate'] or row['baseline_generation'] is None else 'inconclusive'
        row['icon_input'] = row['input_observation']['outcome']
        row['wall_conformant'] = False
        if not row['reveal_action_confirmed']:
            raise RuntimeError('named reveal/restore action not independently confirmed')
        if mode == 'live' and row['observation']['outcome'] != 'fail':
            raise RuntimeError('ordinary-window negative control did not fail reveal')
        if mode == 'live' and icon_input and (row['icon_input'] != 'fail' or
                [(s['step'], s['outcome']) for s in row['input_observation']['steps']] != [('baseline-clear', 'pass'), ('select', 'fail')]):
            raise RuntimeError('ordinary-window negative input control did not detect blocked selection')
        expected_stopped = {'candidate'} | ({'openbox'} if restart_window_manager else set())
        if any(process.poll() is not None for name, process in processes if name not in expected_stopped):
            raise RuntimeError('lab service exited before observations completed')
        row['execution'] = 'completed'
    except Exception as error:
        row['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if channel:
            channel.close()
        if worker:
            worker.join(.5)
            if worker.is_alive():
                worker.terminate()
                worker.join(2)
            if worker.is_alive():
                worker.kill()
                worker.join(2)
            row['observer_exit'] = worker.exitcode
        cleanup = []
        for name, process in reversed(processes):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
            cleanup.append({'process': name, 'pid': process.pid, 'exit': process.returncode})
        if server:
            server.terminate()
            try:
                server.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate(timeout=3)
            cleanup.append({'process': 'Xvfb', 'pid': server.pid, 'exit': server.returncode})
        row['cleanup'] = cleanup
        groups = {process.pid for _, process in processes}
        remaining = []
        for proc in Path('/proc').iterdir():
            if not proc.name.isdecimal():
                continue
            try:
                fields = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
                if int(fields[2]) in groups:
                    remaining.append(int(proc.name))
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
        row['remaining_owned_group_members'] = remaining
        for handle in handles:
            handle.close()
        if runtime_fd is not None:
            os.close(runtime_fd)
        auth = workspace / 'xauthority'
        if auth.exists() and not auth.is_symlink():
            auth.unlink()
        row['logs'] = {p.name: p.read_text(encoding='utf-8', errors='replace')[:16384] for p in logs}
        row['log_identity'] = {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in logs}
        journal = workspace / 'frames.jsonl'
        if journal.exists():
            row['capture_journal'] = {'path': str(journal.relative_to(build)), 'sha256': sha(journal), 'bytes': journal.stat().st_size}
        for name, key in (('input.jsonl', 'input_journal'), ('input-timeout.log', 'input_timeout'), ('recovery.jsonl', 'recovery_journal')):
            path = workspace / name
            if path.exists():
                if path.stat().st_size > 8 * 1024**2:
                    row['execution'] = 'failed'
                    row['error'] = 'native input journal exceeded 8 MiB budget'
                else:
                    row[key] = {'path': str(path.relative_to(build)), 'sha256': sha(path), 'bytes': path.stat().st_size,
                                'raw_utf8': path.read_text(encoding='utf-8')}
        if row.get('observer_exit') != 0 or remaining or any(p['exit'] is None for p in cleanup):
            row['execution'] = 'failed'
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_dir', type=Path)
    parser.add_argument('--gtk-rendering', choices=['similar', 'image'], default='similar', help='Record a separate GTK rendering laboratory variant')
    parser.add_argument('--wallpaper-mode', choices=['tile', 'color'], default='tile', help='Color is a diagnostic control, never file-wallpaper qualification')
    parser.add_argument('--delayed-wallpaper', action='store_true', help='Configure the synthetic image only after icon-manager initialization')
    parser.add_argument('--icon-input', action='store_true', help='Use native pointer input and an explicitly owned read-only accessibility observer')
    parser.add_argument('--restart-window-manager', action='store_true', help='Observe one owned Openbox crash/replacement after the reveal interval')
    args = parser.parse_args()
    if args.restart_window_manager and args.icon_input:
        parser.error('Combined input/recovery lifetime is not yet closed; run the independent experiments')
    build = args.build_dir.resolve(strict=True)
    if os.geteuid() == 0 or json.loads((build / '.syspane-owner.json').read_text())['profile'] != 'linux-x64-gcc13':
        raise ValueError('owned unprivileged Linux build required')
    lab = build / 'x11-lab'
    identity = json.loads((lab / 'identity.json').read_text(encoding='utf-8'))
    if identity['lock_sha256'] != sha(ROOT / 'build-support/x11-lab-packages.json'):
        raise ValueError('prepared lab lock changed')
    sysroot = lab / 'sysroot'
    for name, digest in identity['files'].items():
        if sha(sysroot / name) != digest:
            raise ValueError('prepared lab changed: ' + name)
    output = build / 'native-evidence'
    output.mkdir(exist_ok=True)
    inputs = [Path(__file__), ROOT / 'tests/desktop/native_oracle.py', ROOT / 'tests/desktop/oracle.py',
              ROOT / 'tests/fault/native_diagnostic.py', ROOT / 'source/diagnostics/oracle_probe_x11.cpp',
              ROOT / 'source/desktop/x11/desktop_candidate.cpp', ROOT / 'source/desktop/x11/desktop_candidate.hpp',
              ROOT / 'build-support/x11-lab-packages.json', ROOT / 'spec/delivery/packages/w-05-x11-investigation.md',
              ROOT / 'tests/desktop/x11_input.py', ROOT / 'build-support/x11-input-runtime.json',
              ROOT / 'build-support/record_x11_host.py', ROOT / 'tests/desktop/test_x11_record.py',
              ROOT / 'tests/desktop/x11_recovery.py', ROOT / 'spec/delivery/packages/w-05-shell-recovery.md',
              ROOT / 'build-support/x11-recovery-runtime.json', ROOT / 'tests/desktop/test_x11_recovery_record.py']
    report = {'family': 'X11-HOST-01', 'execution': 'failed', 'executed_at': datetime.now(timezone.utc).isoformat(),
              'profile': 'linux-x64-gcc13 / Openbox 3.6.1 / PCManFM 1.3.2 / owned Xvfb 800x600x24',
              'qualification': 'Bounded X11 candidate investigation; no production or other desktop support claim.',
              'gtk_rendering': args.gtk_rendering,
              'wallpaper_mode': args.wallpaper_mode,
              'delayed_wallpaper_setup': args.delayed_wallpaper,
              'icon_input_requested': args.icon_input,
              'window_manager_restart_requested': args.restart_window_manager,
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
              'artifact_sha256': sha(build / 'SysPane.OracleProbe'), 'lab_identity_sha256': sha(lab / 'identity.json'),
              'system_binaries': {str(p): sha(p) for p in [Path('/usr/bin/Xvfb'), Path('/usr/bin/dbus-daemon'), Path('/usr/lib/x86_64-linux-gnu/libXtst.so.6')]},
              'environment': {'uid': os.geteuid(), 'uname': list(platform.uname()), 'os_release_sha256': sha(Path('/etc/os-release'))},
              'cases': []}
    loader_environment = {**os.environ, 'LD_LIBRARY_PATH': str(sysroot / 'usr/lib/x86_64-linux-gnu')}
    binaries = [sysroot / 'usr/bin/openbox', sysroot / 'usr/bin/pcmanfm', build / 'SysPane.OracleProbe']
    if args.restart_window_manager:
        runtime = json.loads((ROOT / 'build-support/x11-recovery-runtime.json').read_text(encoding='utf-8'))
        versions = dict(line.split('\t') for line in subprocess.check_output(['dpkg-query', '-W', *runtime['packages']], text=True, timeout=3).splitlines())
        if versions != runtime['packages'] or any(sha(Path(p)) != digest for p, digest in runtime['files'].items()):
            raise ValueError('optional native recovery runtime differs from its pinned identity')
        report['recovery_runtime'] = runtime
        report['system_binaries'].update(runtime['files'])
        binaries.extend(Path(p) for p in runtime['files'])
    if args.icon_input:
        runtime = json.loads((ROOT / 'build-support/x11-input-runtime.json').read_text(encoding='utf-8'))
        versions = dict(line.split('\t') for line in subprocess.check_output(
            ['dpkg-query', '-W', *runtime['packages']], text=True, timeout=3).splitlines())
        if versions != runtime['packages'] or any(sha(Path(p)) != digest for p, digest in runtime['files'].items()):
            raise ValueError('optional native input runtime differs from its pinned identity')
        report['input_runtime'] = runtime
        report['system_binaries'].update(runtime['files'])
        binaries.extend(Path(p) for p in runtime['files'] if not p.endswith('.typelib'))
    dependencies = {}
    for binary in binaries:
        listing = subprocess.check_output(['ldd', str(binary)], env=loader_environment, text=True, timeout=5)
        if 'not found' in listing:
            raise ValueError('lab loader dependency missing: ' + listing)
        for name in re.findall(r'(?:=>\s+)?(/[^\s]+)\s+\(', listing):
            path = Path(name).resolve(strict=True)
            dependencies[str(path)] = sha(path)
    report['resolved_loader_files'] = dependencies
    try:
        for mode in ('live', 'desktop', 'desktop-below'):
            print('X11 host investigation:', mode, flush=True)
            row = run_case(build, sysroot, output, mode, args.gtk_rendering, args.wallpaper_mode, args.delayed_wallpaper, args.icon_input, args.restart_window_manager)
            report['cases'].append(row)
            print('Execution:', row['execution'], '; observation:', row.get('observation', {}).get('outcome'), flush=True)
            if row['execution'] != 'completed':
                break
        if len(report['cases']) == 3 and all(row['execution'] == 'completed' for row in report['cases']):
            report['execution'] = 'completed'
    finally:
        path = output / ('X11-HOST-01-' + uuid.uuid4().hex + '.json')
        with path.open('x', encoding='utf-8', newline='\n') as file:
            json.dump(report, file, indent=2)
            file.write('\n')
        print('Native evidence:', path, flush=True)
    return 0 if report['execution'] == 'completed' else 1


if __name__ == '__main__':
    sys.exit(main())

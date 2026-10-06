"""Bounded GNOME bootstrap on an authenticated owned Xvfb display, never a user session."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
import uuid
import zipfile

from native_oracle import Display, ROOT, launch_xvfb
from native_x11_host import DesktopDisplay, rgb_record
from x11_recovery import ResourceOwner, manager_identity
from oracle import evaluate, pack_frame

sys.path.insert(0, str(ROOT / 'build-support'))
from prepare_gnome_lab import owned_build, sha, inventory

SOURCES = ['tests/desktop/native_gnome_bootstrap.py', 'tests/desktop/native_oracle.py',
           'tests/desktop/native_x11_host.py', 'tests/desktop/x11_recovery.py',
           'tests/desktop/oracle.py', 'tests/fault/native_diagnostic.py',
           'build-support/prepare_gnome_lab.py', 'build-support/gnome-lab-packages.json',
           'spec/delivery/packages/w-05-gnome-investigation.md',
           'source/desktop/gnome/lab-marker/extension.js', 'source/desktop/gnome/lab-marker/metadata.json',
           'spec/delivery/packages/w-05-gnome-composition.md', 'tests/desktop/gnome_composition.py',
           'tests/desktop/fixtures/gnome-composition.json', 'tests/desktop/fixtures/gnome-composition-0.2.json',
           'build-support/record_gnome_host.py', 'spec/delivery/packages/w-05-gnome-reveal.md',
           'tests/desktop/gnome_reveal.py', 'tests/desktop/gnome_foreground.py',
           'tests/desktop/fixtures/gnome-reveal.json', 'tests/desktop/gnome_focus_baseline.py',
           'spec/delivery/packages/w-05-gnome-focus-baseline.md',
           'spec/delivery/packages/w-05-gnome-focus-trace.md',
           'spec/delivery/packages/w-05-gnome-input.md', 'tests/desktop/gnome_input.py',
           'tests/desktop/x11_input.py', 'build-support/x11-input-runtime.json',
           'build-support/x11-lab-packages.json', 'tests/desktop/gnome_wallpaper.py',
           'tests/desktop/fixtures/gnome-wallpaper.json', 'spec/delivery/packages/w-05-gnome-wallpaper.md',
           'tests/desktop/gnome_switcher.py', 'tests/desktop/gnome_switcher_app.py',
           'tests/desktop/fixtures/gnome-switcher.json', 'spec/delivery/packages/w-05-gnome-switcher.md',
           'tests/desktop/gnome_icon_recovery.py', 'spec/delivery/packages/w-05-gnome-icon-recovery.md',
           'tests/desktop/gnome_shell_recovery.py', 'spec/delivery/packages/w-05-gnome-shell-recovery.md',
           'tests/desktop/gnome_focus_integration.py', 'spec/delivery/packages/w-05-gnome-focus-integration.md',
           'tests/desktop/gnome_focus_scenarios.py', 'tests/desktop/gnome_focus_controls.py',
           'spec/delivery/packages/w-05-gnome-focus-scenarios.md',
           'tests/desktop/gnome_wallpaper_policy.py', 'build-support/gnome-policy-runtime.json',
           'build-support/prepare_gnome_policy.py', 'spec/delivery/packages/w-05-gnome-wallpaper-policy.md',
           'source/desktop/gnome/lab-marker/surfaceLease.js', 'tests/desktop/gnome_lease_producer.py',
           'tests/desktop/gnome_surface_lease.py', 'spec/delivery/packages/w-25-gnome-surface-lease.md',
           'source/desktop/gnome/lab-marker/networkCache.js', 'tests/desktop/gnome_network_relay.py',
           'tests/desktop/gnome_network_cache.py', 'spec/delivery/packages/w-25-native-network-cache.md',
           'tests/protocol/native_collector.py', 'tests/protocol/native_network.py', 'tests/protocol/native_ipc.py',
           'tests/fault/native_recovery.py', 'build-support/record_gnome_network_cache.py',
           'tests/desktop/test_gnome_network_cache_record.py',
           'source/desktop/gnome/lab-marker/clockExperiment.js', 'tests/desktop/gnome_clock_peer.py',
           'tests/desktop/gnome_clock_age.py', 'spec/delivery/packages/w-25-gnome-clock.md',
           'source/desktop/gnome/native_clock.cpp', 'source/desktop/gnome/native_clock.hpp',
           'source/desktop/gnome/SysPaneClock-0.1.gir', 'build-support/record_gnome_clock.py',
           'tests/desktop/test_gnome_clock_record.py']


def marker_trace(display, environment, sample=None, dismiss=True):
    if dismiss:
        key = display.x.XKeysymToKeycode(display.handle, display.x.XStringToKeysym(b'Escape'))
        if not key:
            raise ValueError('native Escape key unavailable')
        for pressed in (True, False):
            if not display.xtest.XTestFakeKeyEvent(display.handle, key, pressed, 0):
                raise ValueError('native overview-dismiss stimulus failed')
        display.x.XFlush(display.handle)
        time.sleep(.3)
    def issue(generation):
        command = ['/usr/bin/gdbus', 'call', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
                   '--dest', 'org.gnome.Shell', '--object-path', '/org/syspane/LabMarker',
                   '--method', 'org.syspane.LabMarker.SetGeneration', str(generation)]
        response = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=1)
        if response.returncode or response.stdout.strip() != '()':
            raise ValueError('laboratory marker stimulus failed: ' + response.stdout + response.stderr)
    issue(1)
    time.sleep(.25)
    background = display.capture(600, 400, 128, 96)
    trace = {'version': '0.1.0', 'start_us': 0, 'end_us': 2400000,
             'stimuli': [{'at_us': 0, 'generation': 1}], 'frames': []}
    started = time.monotonic_ns()
    now = lambda: (time.monotonic_ns() - started) // 1000
    next_frame, generation = 0, 2
    while now() < trace['end_us']:
        at = now()
        if generation <= 3 and at >= (generation - 1) * 800000:
            trace['stimuli'].append({'at_us': at, 'generation': generation})
            issue(generation)
            generation += 1
        if at >= next_frame and at < trace['end_us'] - 10000:
            before = now()
            pixels = display.capture(300, 200, 128, 96)
            after = now()
            if after <= trace['end_us']:
                frame = pack_frame(pixels, before, after)
                trace['frames'].append(frame)
                if sample:
                    sample(frame, now)
            next_frame += 50000
        time.sleep(.002)
    return {'trace': trace, 'evaluation': evaluate(trace), 'started_monotonic_ns': started,
            'background_before': rgb_record(background),
            'background_after': rgb_record(display.capture(600, 400, 128, 96)),
            'final_desktop': rgb_record(display.capture(0, 0, 800, 600))}


def observe(environment, pid, channel, marker, composition, foreground_pid=None, focus_baseline=None):
    os.environ.clear()
    os.environ.update(environment)
    display = None
    try:
        display = DesktopDisplay() if marker else Display()
        owner = ResourceOwner(display)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            manager = manager_identity(display, owner)
            if manager and manager['pid'] == [pid] and manager['self'] == [manager['window']]:
                break
            time.sleep(.05)
        else:
            raise TimeoutError('owned GNOME manager resource did not become ready')
        frames = []
        # A native WM resource alone can precede a fatal shell JS startup error.
        for delay in (0, 1, 4):
            time.sleep(delay)
            started = time.monotonic_ns()
            rgb = display.capture(0, 0, 800, 600)
            frames.append({'capture_started_ns': started, 'capture_finished_ns': time.monotonic_ns(),
                           'origin': 'display_server_root', 'pixels': rgb_record(rgb)})
            if manager_identity(display, owner) != manager:
                raise ValueError('manager disappeared or changed during bootstrap interval')
        result = {'outcome': 'pass', 'manager': manager, 'frames': frames}
        if composition:
            import gnome_composition
            workspace = Path(environment['HOME']).parent
            result['composition'] = gnome_composition.observe(display, environment, pid, workspace, marker_trace)
            if foreground_pid:
                import gnome_reveal
                result['reveal'] = gnome_reveal.observe(display, environment, foreground_pid, workspace, result['composition'])
        elif marker and not focus_baseline:
            result['marker'] = marker_trace(display, environment)
        if focus_baseline:
            import gnome_focus_baseline
            result['focus_baseline'] = gnome_focus_baseline.observe(display, environment, pid, foreground_pid,
                Path(environment['HOME']).parent, result.get('reveal'), result.get('composition'))
        if environment.get('SYSPANE_GNOME_CLOCK_AGE'):
            import gnome_clock_age
            result['clock_age'] = gnome_clock_age.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_NETWORK_CACHE'):
            import gnome_network_cache
            result['network_cache'] = gnome_network_cache.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_SURFACE_LEASE'):
            import gnome_surface_lease
            result['surface_lease'] = gnome_surface_lease.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_WALLPAPER_POLICY'):
            import gnome_wallpaper_policy
            result['wallpaper_policy'] = gnome_wallpaper_policy.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_FOCUS_SCENARIOS'):
            import gnome_focus_scenarios
            result['focus_scenarios'] = gnome_focus_scenarios.observe(display, environment,
                Path(environment['HOME']).parent, result['focus_baseline'], result['composition'], channel, marker_trace)
        elif environment.get('SYSPANE_GNOME_FOCUS_INTEGRATION'):
            import gnome_focus_integration
            result['focus_integration'] = gnome_focus_integration.observe(display, environment,
                Path(environment['HOME']).parent, result['focus_baseline'], result['composition'], pid, marker_trace)
        if environment.get('SYSPANE_GNOME_INPUT_CONTROL') and not (environment.get('SYSPANE_GNOME_ICON_RECOVERY') or environment.get('SYSPANE_GNOME_SHELL_RECOVERY') or environment.get('SYSPANE_GNOME_FOCUS_INTEGRATION')):
            import gnome_input
            result['icon_input'] = gnome_input.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_WALLPAPER_CONTROL'):
            import gnome_wallpaper
            result['wallpaper'] = gnome_wallpaper.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_SWITCHER_CONTROL'):
            import gnome_switcher
            result['switcher'] = gnome_switcher.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_ICON_RECOVERY'):
            import gnome_icon_recovery
            result['icon_recovery'] = gnome_icon_recovery.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace)
        if environment.get('SYSPANE_GNOME_SHELL_RECOVERY'):
            import gnome_shell_recovery
            result['shell_recovery'] = gnome_shell_recovery.observe(display, environment, pid,
                Path(environment['HOME']).parent, result['composition'], marker_trace, channel)
        channel.send(result)
    except Exception as error:
        channel.send({'outcome': 'fail', 'error': type(error).__name__ + ': ' + str(error)})
    finally:
        if display:
            display.close()
        channel.close()


def mapped_files(pid):
    paths = set()
    for row in Path(f'/proc/{pid}/maps').read_text().splitlines():
        fields = row.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith('/'):
            paths.add(fields[5])
    return {p: sha(Path(p)) for p in sorted(paths) if Path(p).is_file()}


def group_members(group):
    members = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == group and int(fields[3]) == group:
                members.append({'pid': int(path.name), 'state': fields[0]})
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return members


def run(build, marker=False, control='live', composition=None, reveal=None, focus_baseline=None, focus_trace=False, icon_input=None, wallpaper=None, switcher=None, icon_recovery=None, shell_recovery=None, focus_integration=None, focus_scenarios=None, wallpaper_policy=None, surface_lease=None, network_cache=None, clock_age=None):
    # Retain orphaned shell helpers for reaping; no service/session can adopt them.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'cannot retain descendant exit evidence')
    lab = build / 'gnome-lab'
    sysroot = lab / 'sysroot'
    identity = json.loads((lab / 'identity.json').read_text())
    if identity['lock_sha256'] != sha(ROOT / 'build-support/gnome-lab-packages.json') or identity['files'] != inventory(sysroot):
        raise ValueError('pinned GNOME runtime identity changed')
    evidence = build / 'native-evidence'
    evidence.mkdir(exist_ok=True)
    family = 'GNOME-REVEAL-01' if reveal else ('GNOME-COMPOSITION-01' if composition else ('GNOME-MARKER-01' if marker else 'GNOME-BOOTSTRAP-01'))
    if focus_baseline:
        family = 'GNOME-FOCUS-BASELINE-01'
    if icon_input:
        family = 'GNOME-INPUT-01'
    if wallpaper:
        family = 'GNOME-WALLPAPER-01'
    if switcher:
        family = 'GNOME-SWITCHER-01'
    if icon_recovery:
        family = 'GNOME-ICON-RECOVERY-01'
    if shell_recovery:
        family = 'GNOME-SHELL-RECOVERY-01'
    if focus_integration:
        family = 'GNOME-FOCUS-BASELINE-01'
    if wallpaper_policy:
        family = 'GNOME-WALLPAPER-POLICY-01'
    if surface_lease:
        family = 'GNOME-SURFACE-LEASE-01'
    if network_cache:
        family = 'GNOME-NETWORK-CACHE-01'
    if clock_age:
        family = 'GNOME-CLOCK-01'
    with_icons = bool(composition) or focus_baseline == 'ding'
    token = family + '-' + uuid.uuid4().hex
    workspace = build / token
    workspace.mkdir(mode=0o700)
    for name in ('home', 'config', 'data', 'cache', 'run', 'schemas'):
        (workspace / name).mkdir(mode=0o700)
    # Mutter's documented uninstalled-test fallback is relative to its CWD.
    # Resolve it to the exact extracted helper without changing /usr/libexec.
    # GNOME Shell changes CWD to its isolated HOME before initializing Mutter.
    (workspace / 'home/src/frames').mkdir(parents=True)
    (workspace / 'home/src/frames/mutter-x11-frames').symlink_to(sysroot / 'usr/libexec/mutter-x11-frames')
    report = {'family': family, 'outcome': 'fail',
              'marker_control': control if marker else None,
              'composition_control': composition,
              'reveal_control': reveal,
              'focus_baseline_mode': focus_baseline,
              'focus_trace': focus_trace,
              'icon_input_control': icon_input,
              'wallpaper_control': wallpaper,
              'switcher_control': switcher,
              'icon_recovery_control': icon_recovery,
              'shell_recovery_control': shell_recovery,
              'focus_integration_mode': focus_integration,
              'focus_scenarios_mode': focus_scenarios,
              'wallpaper_policy_control': wallpaper_policy,
              'surface_lease_control': surface_lease,
              'network_cache_control': network_cache,
              'clock_age_control': clock_age,
              'executed_at': datetime.now(timezone.utc).isoformat(),
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {p: sha(ROOT / p) for p in SOURCES},
              'workspace': str(workspace), 'lab_identity_sha256': sha(lab / 'identity.json'),
              'environment': {'uid': os.geteuid(), 'os_release_sha256': sha(Path('/etc/os-release'))},
              'system_binaries': {p: sha(Path(p)) for p in ['/usr/bin/Xvfb', '/usr/bin/dbus-daemon', '/usr/bin/glib-compile-schemas', '/usr/lib/x86_64-linux-gnu/libXRes.so.1']},
              'commands': [], 'cleanup': [],
              'qualification': 'Laboratory bootstrap and optional temporal marker only; icon composition, reveal, input, recovery, wallpaper policy, Wayland and product host qualification are not run.'}
    if composition:
        report['qualification'] = 'Selected solid-color DING composition experiment only; reveal, native input, image wallpaper/policy, recovery, Wayland and full product host qualification are not run.'
    if reveal:
        report['qualification'] = 'Configured GNOME Super+D reveal with one owned normal window and solid-color composition only; icon input, taskbar/task-switcher behavior, image wallpaper/policy, recovery, Wayland and full product qualification are not run.'
    if focus_baseline:
        report['qualification'] = 'Diagnostic native focus comparison only; completion is not a passed focus/reveal or product acceptance claim.'
    if icon_input:
        report['qualification'] = 'Selected owned GNOME/DING/PCManFM icon input and solid-color composition only; Show Desktop focus, taskbar, image wallpaper, recovery, other file managers and full product qualification remain open.'
    if wallpaper:
        report['qualification'] = 'Selected owned GNOME/DING single-display PNG file/settings/pixel preservation and live composition only; wallpaper policy, other image modes, Show Desktop focus, taskbar, recovery and full product qualification remain open.'
    if switcher:
        report['qualification'] = 'Selected owned GNOME/DING Alt+Tab and overview dash investigation only; other taskbars, Show Desktop focus, recovery and full product qualification remain open.'
    if icon_recovery:
        report['qualification'] = 'Selected owned DING exit/replacement, independent live composition and input on the replacement only; shell/compositor replacement, Show Desktop focus and full product qualification remain open.'
    if shell_recovery:
        report['qualification'] = 'Owned GNOME X11 shell/compositor replacement and bridge reattachment only; user session supervision, product continuity, Show Desktop focus and other profiles remain open.'
    if focus_integration:
        report['qualification'] = 'Optional event-bound native Show Desktop focus integration and declared guards only; default behavior, broader focus/session cases and complete product qualification remain open.'
    if focus_scenarios:
        report['qualification'] = 'Optional owned GNOME X11 multiple-window/modal focus, closed lifetime and workspace invalidation only; broader session/alternate triggers and complete host qualification remain open.'
    if wallpaper_policy:
        report['qualification'] = 'Native private dconf wallpaper locks and policy preservation only; protected deployment, image policy, live revocation and complete host qualification remain open.'
    if surface_lease:
        report['qualification'] = 'Independent public-marker native surface expiry/disconnect/retention and new epoch only; full telemetry, policy, supervisor and product qualification remain open.'
    if network_cache:
        report['qualification'] = 'Private retained real-network tile, native policy revision/erasure and owner loss only; live renderer clock, installed policy, general transport and product qualification remain open.'
        report['collector_build_record_sha256'] = sha(ROOT/'build-support/evidence/w-25-gjs-clock-linux-x64-gcc13.json')
    if clock_age:
        report['qualification'] = 'Owned asynchronous shell clock and public native age/expiry only; operational freshness, suspend and product qualification remain open.'
        record = ROOT/'build-support/evidence/w-25-gjs-clock-linux-x64-gcc13.json'
        expected = json.loads(record.read_text())
        for name in ['libsyspane_gjs_clock.so', 'SysPaneClock-0.1.typelib']:
            if sha(build/name) != expected['artifacts'][name]['sha256']:raise ValueError('tested native clock artifact differs')
        for name,digest in expected['source_inputs'].items():
            if name.startswith('source/') and Path(name).suffix in ('.cpp','.hpp','.gir') and sha(ROOT/name)!=digest:raise ValueError('tested clock source differs')
        report['clock_build_record_sha256'] = sha(record)
    archive = workspace / 'source-inputs.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as target:
        for name in SOURCES:
            target.write(ROOT / name, name)
    report['source_archive'] = {'path': str(archive), 'bytes': archive.stat().st_size, 'sha256': sha(archive)}
    clock_directory = None
    server = worker = None
    children, streams = [], []
    started = time.monotonic()
    try:
        server, inherited = launch_xvfb(workspace)
        bus = 'unix:abstract=syspane-gnome-' + uuid.uuid4().hex
        system_bus = 'unix:abstract=syspane-gnome-system-' + uuid.uuid4().hex
        environment = {'PATH': str(sysroot / 'usr/bin') + ':/usr/bin:/bin', 'LC_ALL': 'C.UTF-8',
                       'HOME': str(workspace / 'home'), 'USER': 'ir4runner',
                       'DISPLAY': inherited['DISPLAY'], 'XAUTHORITY': inherited['XAUTHORITY'],
                       'XDG_CONFIG_HOME': str(workspace / 'config'), 'XDG_DATA_HOME': str(workspace / 'data'),
                       'XDG_CACHE_HOME': str(workspace / 'cache'), 'XDG_RUNTIME_DIR': str(workspace / 'run'),
                       'XDG_CONFIG_DIRS': str(sysroot / 'etc/xdg'),
                       'XDG_DATA_DIRS': str(sysroot / 'usr/share') + ':/usr/share',
                       'XDG_CURRENT_DESKTOP': 'GNOME', 'XDG_SESSION_TYPE': 'x11',
                       'DBUS_SESSION_BUS_ADDRESS': bus, 'DBUS_SYSTEM_BUS_ADDRESS': system_bus,
                       'AT_SPI_BUS_ADDRESS': bus, 'NO_AT_BRIDGE': '1',
                       'GIO_USE_VFS': 'local', 'GSETTINGS_BACKEND': 'keyfile',
                       'GSETTINGS_SCHEMA_DIR': str(workspace / 'schemas'),
                       'GTK_USE_PORTAL': '0', 'GDK_BACKEND': 'x11', 'LIBGL_ALWAYS_SOFTWARE': '1',
                       'LD_LIBRARY_PATH': ':'.join(str(sysroot / p) for p in ('usr/lib/gnome-shell', 'usr/lib/x86_64-linux-gnu/mutter-14', 'usr/lib/x86_64-linux-gnu')),
                       'GI_TYPELIB_PATH': ':'.join(str(sysroot / p) for p in ('usr/lib/gnome-shell', 'usr/lib/x86_64-linux-gnu/mutter-14', 'usr/lib/x86_64-linux-gnu/gjs/girepository-1.0', 'usr/lib/x86_64-linux-gnu/girepository-1.0')),
                       'GNOME_SHELL_DATADIR': str(sysroot / 'usr/share/gnome-shell'),
                       'LIBGWEATHER_LOCATIONS_PATH': str(sysroot / 'usr/lib/x86_64-linux-gnu/libgweather-4/Locations.bin')}
        if clock_age:
            runtime = Path.home()/'.cache/syspane/ipc-w24'
            if runtime.resolve(strict=True)!=runtime or runtime.stat().st_uid!=os.getuid() or runtime.stat().st_mode & 0o777 != 0o700:raise ValueError('owned IPC root required')
            clock_directory = runtime/('case-'+uuid.uuid4().hex[:12]);clock_directory.mkdir(mode=0o700)
            environment.update(SYSPANE_GNOME_CLOCK_AGE=clock_age, SYSPANE_GNOME_CLOCK_SOCKET=str(clock_directory/'s'),
                SYSPANE_GNOME_CLOCK_HELPER=str(ROOT/'tests/desktop/gnome_clock_peer.py'))
            environment['LD_LIBRARY_PATH'] = str(build)+':'+environment['LD_LIBRARY_PATH']
            environment['GI_TYPELIB_PATH'] = str(build)+':'+environment['GI_TYPELIB_PATH']
        if surface_lease:
            environment['SYSPANE_GNOME_SURFACE_LEASE'] = surface_lease
        if network_cache:
            environment['SYSPANE_GNOME_NETWORK_CACHE'] = network_cache
        if marker:
            environment['SYSPANE_GNOME_MARKER_CONTROL'] = control
        if composition:
            environment['SYSPANE_GNOME_COMPOSITION'] = composition
        if reveal:
            environment['SYSPANE_GNOME_REVEAL'] = reveal
        if focus_baseline:
            environment['SYSPANE_GNOME_FOCUS_BASELINE'] = focus_baseline
            environment['SYSPANE_FOREGROUND_EVENTS'] = str(workspace / 'foreground-events.jsonl')
        if focus_trace:
            environment['MUTTER_DEBUG'] = 'focus,keybindings,window-state'
        if focus_integration or focus_scenarios:
            environment['SYSPANE_GNOME_FOCUS_INTEGRATION'] = focus_integration or ('restore' if focus_scenarios=='helper-exit' else focus_scenarios)
        if focus_scenarios:
            environment['SYSPANE_GNOME_FOCUS_SCENARIOS'] = focus_scenarios
        if wallpaper:
            environment['SYSPANE_GNOME_WALLPAPER_CONTROL'] = wallpaper
        if icon_recovery:
            environment['SYSPANE_GNOME_ICON_RECOVERY'] = icon_recovery
        if shell_recovery:
            environment['SYSPANE_GNOME_SHELL_RECOVERY'] = shell_recovery
        if switcher:
            import gnome_switcher
            input_runtime = json.loads((ROOT / 'build-support/x11-input-runtime.json').read_text())
            if any(sha(Path(p)) != expected for p, expected in input_runtime['files'].items()):
                raise ValueError('pinned accessibility runtime differs')
            report['input_runtime_files'] = input_runtime['files']
            environment.pop('NO_AT_BRIDGE')
            environment['GTK_MODULES'] = 'atk-bridge'
            environment['SYSPANE_GNOME_SWITCHER_CONTROL'] = switcher
            report['switcher_launchers'] = gnome_switcher.prepare(workspace)
        if icon_input:
            x11 = build / 'x11-lab'
            x11_identity = json.loads((x11 / 'identity.json').read_text())
            if x11_identity['lock_sha256'] != sha(ROOT / 'build-support/x11-lab-packages.json') or any(
                    sha(x11 / 'sysroot' / p) != expected for p, expected in x11_identity['files'].items()):
                raise ValueError('pinned folder runtime identity changed')
            report['folder_runtime_identity'] = {'path': str(x11 / 'identity.json'), 'sha256': sha(x11 / 'identity.json')}
            input_runtime = json.loads((ROOT / 'build-support/x11-input-runtime.json').read_text())
            if any(sha(Path(p)) != expected for p, expected in input_runtime['files'].items()):
                raise ValueError('pinned accessibility runtime differs')
            report['input_runtime_files'] = input_runtime['files']
            environment.pop('NO_AT_BRIDGE')
            environment['GTK_MODULES'] = 'atk-bridge'
            environment['SYSPANE_GNOME_INPUT_CONTROL'] = icon_input
            executable = str(x11 / 'sysroot/usr/bin/pcmanfm')
            environment['SYSPANE_GNOME_FOLDER_EXECUTABLE'] = executable
            applications = workspace / 'data/applications'
            applications.mkdir()
            launcher = ('[Desktop Entry]\nType=Application\nName=SysPane owned folder laboratory\n'
                        'Exec=/usr/bin/env LD_LIBRARY_PATH=' + str(x11 / 'sysroot/usr/lib/x86_64-linux-gnu') +
                        ' XDG_DATA_DIRS=' + str(x11 / 'sysroot/usr/share') + ':/usr/share ' + executable +
                        ' --new-win %U\nTerminal=false\nDBusActivatable=false\nMimeType=inode/directory;\n')
            (applications / 'syspane-owned-folder.desktop').write_text(launcher)
            (applications / 'mimeinfo.cache').write_text('[MIME Cache]\ninode/directory=syspane-owned-folder.desktop;\n')
            (workspace / 'config/mimeapps.list').write_text('[Default Applications]\ninode/directory=syspane-owned-folder.desktop;\n')
            report['folder_association'] = {'launcher': launcher, 'inputs': inventory(applications),
                                          'mimeapps_sha256': sha(workspace / 'config/mimeapps.list')}
        report['environment']['explicit'] = environment
        # Schema compilation is data-only and confined to this unique attempt.
        for folder in (Path('/usr/share/glib-2.0/schemas'), sysroot / 'usr/share/glib-2.0/schemas'):
            for source in folder.glob('*'):
                if source.suffix in ('.xml', '.override'):
                    (workspace / 'schemas' / source.name).write_bytes(source.read_bytes())
        command = ['/usr/bin/glib-compile-schemas', str(workspace / 'schemas')]
        compiled = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=5)
        report['commands'].append({'command': command, 'exit': compiled.returncode, 'stdout': compiled.stdout, 'stderr': compiled.stderr})
        compiled.check_returncode()
        report['schema_inputs'] = inventory(workspace / 'schemas')
        if marker:
            target = workspace / 'data/gnome-shell/extensions/syspane-lab-marker@syspane.invalid'
            if not focus_baseline or focus_baseline == 'candidate':
                shutil.copytree(ROOT / 'source/desktop/gnome/lab-marker', target)
            settings = [('org.gnome.shell', 'enabled-extensions', "['syspane-lab-marker@syspane.invalid']"),
                        ('org.gnome.desktop.interface', 'enable-animations', 'false'),
                        ('org.gnome.desktop.background', 'picture-uri', "''"),
                        ('org.gnome.desktop.background', 'picture-uri-dark', "''"),
                        ('org.gnome.desktop.background', 'picture-options', "'none'"),
                        ('org.gnome.desktop.background', 'primary-color', "'#304860'"),
                        ('org.gnome.desktop.background', 'color-shading-type', "'solid'")]
            if with_icons:
                import gnome_composition
                settings.extend(gnome_composition.prepare(workspace, sysroot))
                report['ding_inputs'] = inventory(workspace / 'data/gnome-shell/extensions/ding@rastersoft.com')
                report['fixture_inputs'] = {name: inventory(workspace / name) for name in ['home/Desktop', 'data/icons', 'config/gtk-3.0']}
                report['desktop_entries'] = sorted(p.relative_to(workspace / 'home/Desktop').as_posix()
                                                   for p in (workspace / 'home/Desktop').rglob('*'))
            if focus_baseline:
                from gnome_focus_baseline import MODES
                settings = [row for row in settings if row[:2] != ('org.gnome.shell', 'enabled-extensions')]
                settings.append(('org.gnome.shell', 'enabled-extensions', repr(MODES[focus_baseline])))
                extension_root = workspace / 'data/gnome-shell/extensions'
                report['enabled_extension_inputs'] = inventory(extension_root) if extension_root.exists() else {}
            if reveal or focus_baseline:
                from gnome_reveal import FIXTURE
                settings.append(('org.gnome.desktop.wm.keybindings', 'show-desktop', FIXTURE['binding']))
            if switcher:
                settings.extend([('org.gnome.shell','favorite-apps','[]'),
                                 ('org.gnome.desktop.interface','toolkit-accessibility','true'),
                                 ('org.gnome.desktop.wm.keybindings','switch-applications',"['<Alt>Tab']")])
            if focus_scenarios:
                settings.extend([('org.gnome.mutter','dynamic-workspaces','false'),
                                 ('org.gnome.desktop.wm.preferences','num-workspaces','2'),
                                 ('org.gnome.desktop.wm.keybindings','switch-to-workspace-1',"['<Control><Alt>1']"),
                                 ('org.gnome.desktop.wm.keybindings','switch-to-workspace-2',"['<Control><Alt>2']")])
            for schema, key, value in settings:
                command = ['/usr/bin/gsettings', 'set', schema, key, value]
                configured = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=2)
                report['commands'].append({'command': command, 'exit': configured.returncode,
                                           'stdout': configured.stdout, 'stderr': configured.stderr})
                configured.check_returncode()
        if wallpaper_policy:
            import gnome_wallpaper_policy
            report['wallpaper_policy_setup'] = gnome_wallpaper_policy.prepare(workspace, environment, build, wallpaper_policy)
        (workspace / 'bus.xml').write_text('<busconfig><type>session</type><listen>' + bus + '</listen>'
                                         '<policy context="default"><allow send_destination="*"/><allow receive_sender="*"/><allow own="*"/></policy></busconfig>')
        (workspace / 'system-bus.xml').write_text('<busconfig><type>system</type><listen>' + system_bus + '</listen>'
                                                '<policy context="default"><allow send_destination="*"/><allow receive_sender="*"/><allow own="*"/></policy></busconfig>')
        def launch(name, command):
            stream = (workspace / (name + '.log')).open('xb')
            streams.append(stream)
            process = subprocess.Popen(command, cwd=workspace, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            children.append((name, process))
            report['commands'].append({'command': command, 'pid': process.pid})
            return process
        launch('bus', ['/usr/bin/dbus-daemon', '--nofork', '--nopidfile', '--nosyslog', '--config-file=' + str(workspace / 'bus.xml')])
        launch('system-bus', ['/usr/bin/dbus-daemon', '--nofork', '--nopidfile', '--nosyslog', '--config-file=' + str(workspace / 'system-bus.xml')])
        # Explicit same-address call; this cannot discover or activate a user bus.
        for _ in range(20):
            ready = subprocess.run(['/usr/bin/gdbus', 'call', '--address', bus, '--dest', 'org.freedesktop.DBus',
                                    '--object-path', '/org/freedesktop/DBus', '--method', 'org.freedesktop.DBus.ListNames'],
                                   env=environment, capture_output=True, timeout=1)
            if ready.returncode == 0:
                break
            time.sleep(.05)
        else:
            raise TimeoutError('owned session bus unavailable')
        policy_writer = None
        if wallpaper_policy:
            policy_writer = launch('dconf-writer', ['/usr/libexec/dconf-service'])
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                ready = subprocess.run(['/usr/bin/gdbus', 'call', '--address', bus, '--dest', 'org.freedesktop.DBus',
                    '--object-path', '/org/freedesktop/DBus', '--method', 'org.freedesktop.DBus.GetConnectionUnixProcessID', 'ca.desrt.dconf'],
                    env=environment, capture_output=True, text=True, timeout=1)
                if ready.returncode == 0 and ready.stdout.strip() == '(uint32 ' + str(policy_writer.pid) + ',)':
                    report['wallpaper_policy_writer_pid'] = policy_writer.pid
                    break
                time.sleep(.05)
            else:
                raise TimeoutError('private dconf writer did not acquire its bus name')
        if icon_input or switcher:
            registry = launch('registry', ['/usr/libexec/at-spi2-registryd'])
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                ready = subprocess.run(['/usr/bin/gdbus', 'call', '--address', bus, '--dest', 'org.freedesktop.DBus',
                                        '--object-path', '/org/freedesktop/DBus', '--method',
                                        'org.freedesktop.DBus.GetConnectionUnixProcessID', 'org.a11y.atspi.Registry'],
                                       env=environment, capture_output=True, text=True, timeout=1)
                if ready.returncode == 0 and ready.stdout.strip() == '(uint32 ' + str(registry.pid) + ',)':
                    report['registry_pid'] = registry.pid
                    break
                time.sleep(.05)
            else:
                raise TimeoutError('owned accessibility registry did not acquire its bus name')
        network_relay = None
        if network_cache:
            network_relay = launch('network-relay', ['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_network_relay.py')])
            environment['SYSPANE_GNOME_NETWORK_PID'] = str(network_relay.pid)
            deadline = time.monotonic()+3
            while time.monotonic()<deadline:
                path=workspace/'network-relay.private.jsonl'
                if path.exists() and path.stat().st_size:break
                if network_relay.poll() is not None:raise ValueError('network relay exited at startup')
                time.sleep(.02)
            else:raise TimeoutError('network relay not ready')
            report['network_relay_mapped_files'] = mapped_files(network_relay.pid)
        lease_producers = {}
        if surface_lease:
            for role in ['first','second']:
                lease_producers[role] = launch('lease-'+role, ['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_lease_producer.py'),role])
            environment['SYSPANE_GNOME_LEASE_PIDS'] = json.dumps([p.pid for p in lease_producers.values()])
            deadline = time.monotonic()+3
            while time.monotonic()<deadline:
                if all((workspace/('lease-producer-'+role+'.jsonl')).exists() and (workspace/('lease-producer-'+role+'.jsonl')).stat().st_size for role in lease_producers):break
                time.sleep(.02)
            else:raise TimeoutError('retained lease fixtures not ready')
            report['lease_producer_mapped_files'] = {role:mapped_files(p.pid) for role,p in lease_producers.items()}
        shell = launch('shell', [str(sysroot / 'usr/bin/gnome-shell'), '--x11', '--mode=user'])
        foreground = launch('foreground', ['/usr/bin/python3', str(ROOT / 'tests/desktop/gnome_foreground.py')]) if reveal or focus_baseline else None
        switcher_apps = {}
        if switcher:
            for role in ['alpha','beta'] + (['fault'] if switcher=='ordinary-window' else []):
                switcher_apps[role] = launch('switcher-'+role, ['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_switcher_app.py'),role])
            environment['SYSPANE_GNOME_SWITCHER_PIDS'] = json.dumps({role:p.pid for role,p in switcher_apps.items()})
        context = mp.get_context('spawn')
        local, remote = context.Pipe(duplex=bool(shell_recovery or focus_scenarios))
        focus_helper = None
        recovery_parent = None
        if shell_recovery:
            from gnome_shell_recovery import Parent
            recovery_parent = Parent(shell, [str(sysroot / 'usr/bin/gnome-shell'), '--x11', '--mode=user'], launch, local, shell_recovery, report)
        worker = context.Process(target=observe, args=(environment, shell.pid, remote, marker, composition, foreground.pid if foreground else None, focus_baseline))
        worker.start()
        remote.close()
        while time.monotonic() - started < 40:
            if any(Path(stream.name).stat().st_size > 1024**2 for stream in streams):
                raise ValueError('laboratory log capacity exceeded')
            if local.poll(.05):
                message = local.recv()
                if focus_scenarios and message == {'focus_scenarios_request':'launch'}:
                    if focus_helper is not None:raise ValueError('focus helper launch already consumed')
                    received_ns = time.monotonic_ns()
                    focus_helper = launch('focus-controls', ['/usr/bin/python3', str(ROOT/'tests/desktop/gnome_focus_controls.py')])
                    reply = {'focus_scenarios_pid':focus_helper.pid}
                    local.send(reply)
                    report['focus_scenarios_parent'] = {'message':message,'received_ns':received_ns,'responded_ns':time.monotonic_ns(),'response':reply}
                    continue
                if recovery_parent and recovery_parent.receive(message):
                    continue
                report['observation'] = message
                if report['observation']['outcome'] != 'pass':
                    raise RuntimeError(report['observation']['error'])
                if not shell_recovery and shell.poll() is not None:
                    raise RuntimeError('shell exited during observation')
                report['mapped_files'] = report['observation']['shell_recovery']['old_shell_mapped_files'] if shell_recovery else mapped_files(shell.pid)
                if composition:
                    report['icon_manager_mapped_files'] = (report['observation']['shell_recovery']['old_icon_mapped_files'] if shell_recovery else
                                                          report['observation']['icon_recovery']['old_icon_mapped_files'] if icon_recovery else
                                                          mapped_files(report['observation']['composition']['icon_manager']['pid']))
                    report['outcome'] = report['observation']['composition']['outcome']
                elif not focus_baseline:
                    report['outcome'] = report['observation']['marker']['evaluation']['outcome'] if marker else 'pass'
                if reveal:
                    report['foreground_mapped_files'] = mapped_files(foreground.pid)
                    report['outcome'] = report['observation']['reveal']['evaluation']['outcome']
                if focus_baseline:
                    result = report['observation']['focus_baseline']
                    report['foreground_mapped_files'] = mapped_files(foreground.pid)
                    if result['icon_manager']:
                        report['icon_manager_mapped_files'] = mapped_files(result['icon_manager']['pid'])
                    report['outcome'] = 'pass'
                if icon_input and not (icon_recovery or shell_recovery or focus_integration):
                    report['outcome'] = report['observation']['icon_input']['outcome']
                    if report['observation']['icon_input'].get('error'):
                        report['error'] = report['observation']['icon_input']['error']
                if wallpaper:
                    report['outcome'] = report['observation']['wallpaper']['evaluation']['outcome']
                if switcher:
                    report['switcher_mapped_files'] = {role:mapped_files(p.pid) for role,p in switcher_apps.items()}
                    report['outcome'] = report['observation']['switcher']['outcome']
                if icon_recovery:
                    report['outcome'] = report['observation']['icon_recovery']['outcome']
                    if report['observation']['icon_recovery'].get('error'):
                        report['error'] = report['observation']['icon_recovery']['error']
                if shell_recovery:
                    report['outcome'] = report['observation']['shell_recovery']['outcome']
                    if report['observation']['shell_recovery'].get('error'):
                        report['error'] = report['observation']['shell_recovery']['error']
                if clock_age:
                    report['outcome'] = report['observation']['clock_age']['evaluation']['outcome']
                if network_cache:
                    if network_relay.poll() != (73 if network_cache=='owner-loss' else None):raise ValueError('retained network relay lifetime differs')
                    report['outcome'] = report['observation']['network_cache']['evaluation']['outcome']
                if surface_lease:
                    if lease_producers['first'].poll()!=73 or lease_producers['second'].poll() is not None:raise ValueError('retained producer lifecycle differs')
                    report['outcome'] = report['observation']['surface_lease']['evaluation']['outcome']
                if wallpaper_policy:
                    if policy_writer.poll() is not None:raise ValueError('private dconf writer exited')
                    report['wallpaper_policy_mapped_files'] = mapped_files(policy_writer.pid)
                    report['outcome'] = report['observation']['wallpaper_policy']['evaluation']['outcome']
                if focus_scenarios:
                    if focus_helper is None or focus_helper.poll() is not None:raise ValueError('retained focus helper not live')
                    report['focus_helper_mapped_files'] = mapped_files(focus_helper.pid)
                    report['outcome'] = report['observation']['focus_scenarios']['outcome']
                    if report['observation']['focus_scenarios'].get('error'):
                        report['error'] = report['observation']['focus_scenarios']['error']
                if focus_integration:
                    report['outcome'] = report['observation']['focus_integration']['outcome']
                    if report['observation']['focus_integration'].get('error'):
                        report['error'] = report['observation']['focus_integration']['error']
                break
            if shell.poll() is not None and not (recovery_parent and recovery_parent.armed):
                raise RuntimeError('shell exited during bootstrap: ' + str(shell.returncode))
            if not worker.is_alive():
                raise RuntimeError('observer exited without a report')
        else:
            raise TimeoutError('bounded GNOME bootstrap deadline')
    except Exception as error:
        report['outcome'] = 'fail'
        report['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if worker:
            worker.join(2)
            if worker.is_alive():
                worker.terminate()
            worker.join(2)
            if worker.is_alive():
                worker.kill()
                worker.join(2)
            report['cleanup'].append({'process': 'observer', 'pid': worker.pid, 'exit': worker.exitcode})
        for name, process in reversed(children):
            # Each retained child owns a fresh session/group; never signal a user group.
            before = group_members(process.pid)
            if before:
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                try:
                    while os.waitpid(-process.pid, os.WNOHANG)[0]:
                        pass
                except ChildProcessError:
                    pass
                remaining = group_members(process.pid)
                if not remaining:
                    break
                os.killpg(process.pid, signal.SIGKILL)
                time.sleep(.02)
            else:
                report['outcome'] = 'fail'
                report['error'] = 'owned process group did not stop'
            report['cleanup'].append({'process': name, 'pid': process.pid, 'exit': process.returncode,
                                      'members_before_stop': before, 'members_after_stop': remaining})
        if clock_directory is not None:
            if list(clock_directory.iterdir()):
                report['outcome']='fail';report['error']='clock endpoint cleanup incomplete'
            else:clock_directory.rmdir()
        for stream in streams:
            stream.close()
        report['logs'] = {p.name: p.read_text(errors='replace')[:1048576] for p in workspace.glob('*.log')}
        if focus_trace:
            path = workspace / 'shell.log'
            if path.exists():
                report['native_focus_log'] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}
                if path.stat().st_size > 1048576:
                    report['outcome'] = 'fail'
                    report['error'] = 'native focus log capacity exceeded'
        journal = workspace / 'composition.jsonl'
        if journal.exists():
            report['composition_journal'] = {'path': str(journal), 'bytes': journal.stat().st_size, 'sha256': sha(journal)}
        journal = workspace / 'reveal.jsonl'
        if journal.exists():
            report['reveal_journal'] = {'path': str(journal), 'bytes': journal.stat().st_size, 'sha256': sha(journal)}
        if focus_baseline:
            for key, name in [('focus_journal', 'focus-baseline.jsonl'), ('foreground_events', 'foreground-events.jsonl')]:
                path = workspace / name
                if path.exists():
                    report[key] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}
            extension_root = workspace / 'data/gnome-shell/extensions'
            report['enabled_extension_inputs_after'] = inventory(extension_root) if extension_root.exists() else {}
        if clock_age:
            report['clock_artifacts'] = {p.name:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in workspace.glob('clock-*.json*')}
        if network_cache:
            report['network_private_artifacts'] = {p.name:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in workspace.glob('network-*.private.*')}
        if surface_lease:
            for key,name in [('surface_lease_journal','surface-lease.jsonl'),('lease_first_journal','lease-producer-first.jsonl'),('lease_second_journal','lease-producer-second.jsonl')]:
                path = workspace/name
                if path.exists():report[key] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
        if wallpaper_policy:
            path = workspace/'wallpaper-policy.jsonl'
            if path.exists():report['wallpaper_policy_journal'] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
            report['wallpaper_policy_inputs_after'] = inventory(workspace/'wallpaper-policy')
        if focus_scenarios:
            for key,name in [('focus_scenarios_journal','focus-scenarios.jsonl'),('focus_control_events','focus-control-events.jsonl')]:
                path = workspace/name
                if path.exists():report[key] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
        if focus_integration:
            path = workspace/'focus-integration.jsonl'
            if path.exists():
                report['focus_integration_journal'] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
        if icon_input:
            path = workspace / 'input.jsonl'
            if path.exists():
                report['input_journal'] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}
            if (workspace / 'config/mimeapps.list').exists():
                report['folder_association_after'] = {'inputs': inventory(workspace / 'data/applications'),
                                                     'mimeapps_sha256': sha(workspace / 'config/mimeapps.list')}
        if wallpaper:
            path = workspace / 'wallpaper.jsonl'
            if path.exists():
                report['wallpaper_journal'] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}
            report['wallpaper_artifacts'] = {p.name: {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                                              for p in workspace.glob('wallpaper*.png')}
        if switcher:
            path = workspace / 'switcher.jsonl'
            if path.exists():
                report['switcher_journal'] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
            report['switcher_launcher_inputs_after'] = inventory(workspace/'data/applications')
        if icon_recovery:
            path = workspace/'icon-recovery.jsonl'
            if path.exists():
                report['icon_recovery_journal'] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
        if shell_recovery:
            path = workspace/'shell-recovery.jsonl'
            if path.exists():
                report['shell_recovery_journal'] = {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
        if with_icons:
            report['fixture_after'] = {name: inventory(workspace / name) for name in ['home/Desktop', 'data/icons', 'config/gtk-3.0']}
            report['desktop_entries_after'] = sorted(p.relative_to(workspace / 'home/Desktop').as_posix()
                                                     for p in (workspace / 'home/Desktop').rglob('*'))
        if server:
            if server.poll() is None:
                server.terminate()
            try:
                stdout, stderr = server.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                server.kill()
                stdout, stderr = server.communicate(timeout=2)
            report['cleanup'].append({'process': 'Xvfb', 'pid': server.pid, 'exit': server.returncode})
            report['logs']['Xvfb'] = (stdout + stderr).decode(errors='replace')[:1048576]
        report['elapsed_ms'] = round((time.monotonic() - started) * 1000)
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        path = evidence / (token + '.json')
        path.write_text(json.dumps(report, indent=2) + '\n')
        print(path)
        print(report['outcome'], report.get('error', 'owned shell and requested observations completed'))
    return 0 if report['outcome'] == 'pass' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_dir', type=Path)
    parser.add_argument('--marker', action='store_true', help='Observe three changing generations through the trusted shell bridge')
    parser.add_argument('--marker-control', choices=('live', 'hidden', 'frozen'), default='live')
    parser.add_argument('--composition', choices=('live', 'above-icons', 'below-wallpaper'))
    parser.add_argument('--reveal', choices=('live', 'no-action', 'transient-blank'))
    parser.add_argument('--focus-baseline', choices=('shell', 'ding', 'candidate'))
    parser.add_argument('--focus-trace', action='store_true')
    parser.add_argument('--icon-input', choices=('live', 'block-pointer', 'no-selection'))
    parser.add_argument('--wallpaper', choices=('live', 'replace-file', 'redirect-setting', 'cover-wallpaper'))
    parser.add_argument('--switcher', choices=('live','ordinary-window','no-switcher'))
    parser.add_argument('--icon-recovery', choices=('live','frozen-surface','no-stop'))
    parser.add_argument('--shell-recovery', choices=('live','no-reattach','no-restart'))
    parser.add_argument('--focus-integration', choices=('observe','restore'))
    parser.add_argument('--focus-scenarios', choices=('observe','restore','helper-exit'))
    parser.add_argument('--wallpaper-policy', choices=('locked','unlocked','replace-policy'))
    parser.add_argument('--surface-lease', choices=('live','ignore-expiry','disconnect'))
    parser.add_argument('--network-cache', choices=('live','ignore-clear','wrong-value','owner-loss'))
    parser.add_argument('--clock-age', choices=('live','freeze-age','ignore-expiry','peer-exit','pending-disable','wrong-peer'))
    args = parser.parse_args()
    if args.clock_age:
        if any([args.marker,args.composition,args.reveal,args.focus_baseline,args.focus_trace,args.icon_input,args.wallpaper,args.switcher,args.icon_recovery,args.shell_recovery,args.focus_integration,args.focus_scenarios,args.wallpaper_policy,args.surface_lease,args.network_cache]) or args.marker_control != 'live':
            parser.error('--clock-age owns its same-session peer and live composition')
        args.composition = 'live'
    if args.network_cache:
        if any([args.marker,args.composition,args.reveal,args.focus_baseline,args.focus_trace,args.icon_input,args.wallpaper,args.switcher,args.icon_recovery,args.shell_recovery,args.focus_integration,args.focus_scenarios,args.wallpaper_policy,args.surface_lease]) or args.marker_control != 'live':
            parser.error('--network-cache owns its retained relay and live composition')
        args.composition = 'live'
    if args.surface_lease:
        if any([args.marker,args.composition,args.reveal,args.focus_baseline,args.focus_trace,args.icon_input,args.wallpaper,args.switcher,args.icon_recovery,args.shell_recovery,args.focus_integration,args.focus_scenarios,args.wallpaper_policy]) or args.marker_control != 'live':
            parser.error('--surface-lease owns its retained fixtures and live composition')
        args.composition = 'live'
    if args.wallpaper_policy:
        if any([args.marker,args.composition,args.reveal,args.focus_baseline,args.focus_trace,args.icon_input,args.wallpaper,args.switcher,args.icon_recovery,args.shell_recovery,args.focus_integration,args.focus_scenarios]) or args.marker_control != 'live':
            parser.error('--wallpaper-policy owns its private backend and live composition')
        args.composition = 'live'
    if args.focus_scenarios:
        if any([args.marker,args.composition,args.reveal,args.focus_baseline,args.focus_trace,args.icon_input,args.wallpaper,args.switcher,args.icon_recovery,args.shell_recovery,args.focus_integration]) or args.marker_control != 'live':
            parser.error('--focus-scenarios owns its untraced candidate baseline and workspace setup')
        args.focus_baseline = 'candidate'
    if args.focus_trace and not args.focus_baseline:
        parser.error('--focus-trace requires --focus-baseline')
    if args.focus_integration and (args.focus_baseline != 'candidate' or args.focus_trace):
        parser.error('--focus-integration requires the untraced candidate focus baseline')
    if args.focus_integration:
        if args.icon_input:
            parser.error('--focus-integration owns its native input setup')
        args.icon_input = 'live'
    if args.shell_recovery:
        if args.marker or args.composition or args.reveal or args.focus_baseline or args.focus_trace or args.icon_input or args.wallpaper or args.switcher or args.icon_recovery or args.marker_control != 'live':
            parser.error('--shell-recovery owns the live composition and native input setup')
        args.composition = 'live'
        args.icon_input = 'live'
    if args.icon_recovery:
        if args.marker or args.composition or args.reveal or args.focus_baseline or args.focus_trace or args.icon_input or args.wallpaper or args.switcher or args.marker_control != 'live':
            parser.error('--icon-recovery owns the live composition and native input setup')
        args.composition = 'live'
        args.icon_input = 'live'
    if args.switcher:
        if args.marker or args.composition or args.reveal or args.focus_baseline or args.focus_trace or args.icon_input or args.wallpaper or args.marker_control != 'live':
            parser.error('--switcher owns the live composition prerequisite')
        args.composition = 'live'
    if args.wallpaper:
        if args.marker or args.composition or args.reveal or args.focus_baseline or args.focus_trace or args.icon_input or args.marker_control != 'live':
            parser.error('--wallpaper owns the live composition prerequisite')
        args.composition = 'live'
    if args.icon_input and not (args.icon_recovery or args.shell_recovery or args.focus_integration):
        if args.marker or args.composition or args.reveal or args.focus_baseline or args.focus_trace or args.marker_control != 'live':
            parser.error('--icon-input owns the live composition prerequisite')
        args.composition = 'live'
    if args.focus_baseline:
        if args.marker or args.composition or args.reveal or args.marker_control != 'live':
            parser.error('--focus-baseline owns its marker/composition/reveal selection')
        args.marker = True
        if args.focus_baseline == 'candidate':
            args.reveal = 'live'
    if args.reveal:
        if args.marker_control != 'live' or args.composition not in (None, 'live'):
            parser.error('reveal requires live composition')
        args.composition = 'live'
    if args.composition and args.marker_control != 'live':
        parser.error('composition uses its own above/below controls')
    if not args.marker and args.marker_control != 'live':
        parser.error('--marker-control requires --marker')
    sys.exit(run(owned_build(args.build_dir), args.marker or bool(args.composition), args.marker_control, args.composition, args.reveal, args.focus_baseline, args.focus_trace, args.icon_input, args.wallpaper, args.switcher, args.icon_recovery, args.shell_recovery, args.focus_integration, args.focus_scenarios, args.wallpaper_policy, args.surface_lease, args.network_cache, args.clock_age))

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
           'build-support/record_gnome_host.py']


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


def observe(environment, pid, channel, marker, composition):
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
        elif marker:
            result['marker'] = marker_trace(display, environment)
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


def run(build, marker=False, control='live', composition=None):
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
    family = 'GNOME-COMPOSITION-01' if composition else ('GNOME-MARKER-01' if marker else 'GNOME-BOOTSTRAP-01')
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
    archive = workspace / 'source-inputs.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as target:
        for name in SOURCES:
            target.write(ROOT / name, name)
    report['source_archive'] = {'path': str(archive), 'bytes': archive.stat().st_size, 'sha256': sha(archive)}
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
        if marker:
            environment['SYSPANE_GNOME_MARKER_CONTROL'] = control
        if composition:
            environment['SYSPANE_GNOME_COMPOSITION'] = composition
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
            shutil.copytree(ROOT / 'source/desktop/gnome/lab-marker', target)
            settings = [('org.gnome.shell', 'enabled-extensions', "['syspane-lab-marker@syspane.invalid']"),
                        ('org.gnome.desktop.interface', 'enable-animations', 'false'),
                        ('org.gnome.desktop.background', 'picture-uri', "''"),
                        ('org.gnome.desktop.background', 'picture-uri-dark', "''"),
                        ('org.gnome.desktop.background', 'picture-options', "'none'"),
                        ('org.gnome.desktop.background', 'primary-color', "'#304860'"),
                        ('org.gnome.desktop.background', 'color-shading-type', "'solid'")]
            if composition:
                import gnome_composition
                settings.extend(gnome_composition.prepare(workspace, sysroot))
                report['ding_inputs'] = inventory(workspace / 'data/gnome-shell/extensions/ding@rastersoft.com')
                report['fixture_inputs'] = {name: inventory(workspace / name) for name in ['home/Desktop', 'data/icons', 'config/gtk-3.0']}
                report['desktop_entries'] = sorted(p.relative_to(workspace / 'home/Desktop').as_posix()
                                                   for p in (workspace / 'home/Desktop').rglob('*'))
            for schema, key, value in settings:
                command = ['/usr/bin/gsettings', 'set', schema, key, value]
                configured = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=2)
                report['commands'].append({'command': command, 'exit': configured.returncode,
                                           'stdout': configured.stdout, 'stderr': configured.stderr})
                configured.check_returncode()
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
        shell = launch('shell', [str(sysroot / 'usr/bin/gnome-shell'), '--x11', '--mode=user'])
        context = mp.get_context('spawn')
        local, remote = context.Pipe(duplex=False)
        worker = context.Process(target=observe, args=(environment, shell.pid, remote, marker, composition))
        worker.start()
        remote.close()
        while time.monotonic() - started < 40:
            if any(Path(stream.name).stat().st_size > 1024**2 for stream in streams):
                raise ValueError('laboratory log capacity exceeded')
            if local.poll(.05):
                report['observation'] = local.recv()
                if report['observation']['outcome'] != 'pass':
                    raise RuntimeError(report['observation']['error'])
                if shell.poll() is not None:
                    raise RuntimeError('shell exited during observation')
                report['mapped_files'] = mapped_files(shell.pid)
                if composition:
                    report['icon_manager_mapped_files'] = mapped_files(report['observation']['composition']['icon_manager']['pid'])
                    report['outcome'] = report['observation']['composition']['outcome']
                else:
                    report['outcome'] = report['observation']['marker']['evaluation']['outcome'] if marker else 'pass'
                break
            if shell.poll() is not None:
                raise RuntimeError('shell exited during bootstrap: ' + str(shell.returncode))
            if not worker.is_alive():
                raise RuntimeError('observer exited without a report')
        else:
            raise TimeoutError('bounded GNOME bootstrap deadline')
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if worker:
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
        for stream in streams:
            stream.close()
        report['logs'] = {p.name: p.read_text(errors='replace')[:1048576] for p in workspace.glob('*.log')}
        journal = workspace / 'composition.jsonl'
        if journal.exists():
            report['composition_journal'] = {'path': str(journal), 'bytes': journal.stat().st_size, 'sha256': sha(journal)}
        if composition:
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
    args = parser.parse_args()
    if args.composition and args.marker_control != 'live':
        parser.error('composition uses its own above/below controls')
    if not args.marker and args.marker_control != 'live':
        parser.error('--marker-control requires --marker')
    sys.exit(run(owned_build(args.build_dir), args.marker or bool(args.composition), args.marker_control, args.composition))

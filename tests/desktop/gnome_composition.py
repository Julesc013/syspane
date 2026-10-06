"""Real DING fixture and independent root-pixel composition observations."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import struct
import subprocess
import time
import zlib

from native_oracle import ROOT
from native_x11_host import rgb_record
from x11_recovery import ResourceOwner

FIXTURE_PATH = ROOT / 'tests/desktop/fixtures/gnome-composition-0.2.json'
FIXTURE = json.loads(FIXTURE_PATH.read_text())
BACKGROUND_KEYS = ['picture-uri', 'picture-uri-dark', 'picture-options', 'primary-color', 'color-shading-type']


def png_icon():
    size, colors = FIXTURE['icon_size'], FIXTURE['icon_quadrants']
    rows = b''.join(b'\0' + bytes(c for x in range(size) for c in colors[(y >= size // 2) * 2 + (x >= size // 2)])
                    for y in range(size))
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')


def prepare(workspace, sysroot):
    desktop = workspace / 'home/Desktop'
    (desktop / FIXTURE['folder']).mkdir(parents=True)
    (desktop / FIXTURE['folder'] / 'Sentinel.txt').write_text(FIXTURE['sentinel'])
    (workspace / 'config/user-dirs.dirs').write_text('XDG_DESKTOP_DIR="' + str(desktop) + '"\n')
    (workspace / 'config/gtk-3.0').mkdir()
    (workspace / 'config/gtk-3.0/settings.ini').write_text('[Settings]\ngtk-icon-theme-name=SysPaneFixture\ngtk-font-name=Sans 10\n')
    theme = workspace / 'data/icons/SysPaneFixture'
    (theme / '64x64/places').mkdir(parents=True)
    (theme / 'index.theme').write_text('[Icon Theme]\nName=SysPaneFixture\nComment=Owned synthetic folder fixture\n'
                                     'Inherits=Adwaita\nDirectories=64x64/places\n\n'
                                     '[64x64/places]\nSize=64\nType=Fixed\nContext=Places\n')
    (theme / '64x64/places/folder.png').write_bytes(png_icon())
    target = workspace / 'data/gnome-shell/extensions/ding@rastersoft.com'
    shutil.copytree(sysroot / 'usr/share/gnome-shell/extensions/ding@rastersoft.com', target)
    return [('org.gnome.shell', 'enabled-extensions', "['ding@rastersoft.com', 'syspane-lab-marker@syspane.invalid']"),
            ('org.gnome.desktop.interface', 'icon-theme', "'SysPaneFixture'"),
            ('org.gnome.shell.extensions.ding', 'show-home', 'false'),
            ('org.gnome.shell.extensions.ding', 'show-trash', 'false'),
            ('org.gnome.shell.extensions.ding', 'show-volumes', 'false'),
            ('org.gnome.shell.extensions.ding', 'show-network-volumes', 'false'),
            ('org.gnome.shell.extensions.ding', 'keep-arranged', 'false'),
            ('org.gnome.shell.extensions.ding', 'keep-stacked', 'false'),
            ('org.gnome.shell.extensions.ding', 'start-corner', "'top-left'")]


def settings(environment):
    result = {}
    for key in BACKGROUND_KEYS:
        value = subprocess.run(['/usr/bin/gsettings', 'get', 'org.gnome.desktop.background', key],
                               env=environment, capture_output=True, text=True, timeout=1, check=True)
        if len(value.stdout) > 1024 or value.stderr:
            raise ValueError('background setting observation invalid')
        result[key] = value.stdout.strip()
    return result


def bind_icon_window(display, shell_pid, workspace):
    owner = ResourceOwner(display)
    script = str(workspace / 'data/gnome-shell/extensions/ding@rastersoft.com/app/ding.js')
    matches = []
    for window in display.property(display.root, '_NET_CLIENT_LIST_STACKING'):
        binding = owner.pid(window)
        if not binding:
            continue
        pid, base, mask = binding
        try:
            path = Path(f'/proc/{pid}')
            raw = (path / 'cmdline').read_bytes()
            if len(raw) > 16384:
                raise ValueError('native command line capacity')
            arguments = [x.decode() for x in raw.rstrip(b'\0').split(b'\0')]
            if script not in arguments:
                continue
            stat = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(stat[2]) != shell_pid or int(stat[3]) != shell_pid:
                raise ValueError('icon process outside retained shell group/session')
            if display.atom('_NET_WM_WINDOW_TYPE_DESKTOP') not in display.property(window, '_NET_WM_WINDOW_TYPE'):
                raise ValueError('icon manager window lacks native desktop type')
            matches.append({'window': window, 'pid': pid, 'pid_origin': 'XResQueryClientIds',
                            'resource_base': base, 'resource_mask': mask, 'arguments': arguments,
                            'process_group': int(stat[2]), 'session': int(stat[3]), 'start_ticks': int(stat[19]),
                            'executable': str((path / 'exe').resolve(strict=True))})
        except (FileNotFoundError, ProcessLookupError):
            continue
    if len(matches) > 1:
        raise ValueError('ambiguous icon-manager window')
    return matches[0] if matches else None


def masks(baseline, calibrations=None):
    colors = [bytes(c) for c in FIXTURE['icon_quadrants']]
    pixels = [baseline[n:n+3] for n in range(0, len(baseline), 3)]
    anchors = [[n for n, p in enumerate(pixels) if p == color] for color in colors]
    clean = [n for n, p in enumerate(pixels) if p == bytes(FIXTURE['background_rgb'])]
    if calibrations is not None:
        if len(calibrations) != 2 or any(len(data) != len(baseline) for data in calibrations):
            raise ValueError('independent transparency calibration shape')
        anchors = [[n for n in group if all(data[n*3:n*3+3] == colors[index] for data in calibrations)]
                   for index, group in enumerate(anchors)]
        clean = [n for n in clean if all(data[n*3:n*3+3] == bytes(color)
                 for data, color in zip(calibrations, FIXTURE['transparency_backgrounds']))]
    if any(len(a) < FIXTURE['minimum_pixels_per_quadrant'] for a in anchors) or len(clean) < FIXTURE['minimum_clean_pixels']:
        raise ValueError('native fixture anchors unavailable: ' + str([len(a) for a in anchors]) + '; clean=' + str(len(clean)))
    return anchors, clean


def judge_samples(baseline, samples, calibrations):
    anchors, clean = masks(baseline, calibrations)
    color = bytes(FIXTURE['overlap_rgb'])
    checked = []
    last_end, max_gap, max_duration = 0, 0, 0
    for row in samples:
        # Raw decode is imported from the independent evidence helper, never painter code.
        from record_gnome_host import rgb
        data = rgb(row['pixels'], FIXTURE['overlap'][2] * FIXTURE['overlap'][3] * 3)
        begin, end = row['marker_start_us'], row['end_us']
        if not last_end <= begin <= row['start_us'] <= end <= 2400000:
            raise ValueError('composition capture order')
        max_gap, max_duration = max(max_gap, begin - last_end), max(max_duration, end - begin)
        last_end = end
        checked.append({'at_us': begin,
                        'icons': all(data[n*3:n*3+3] == baseline[n*3:n*3+3] for group in anchors for n in group),
                        'rectangle': all(data[n*3:n*3+3] == color for n in clean)})
    max_gap = max(max_gap, 2400000 - last_end)
    if len(samples) < 3 or max_gap > 150000 or max_duration > 50000:
        raise ValueError('composition capture coverage incomplete')
    return {'icons': 'pass' if all(r['icons'] for r in checked) else 'fail',
            'rectangle': 'pass' if all(r['rectangle'] for r in checked) else 'fail',
            'anchor_counts': [len(a) for a in anchors], 'clean_count': len(clean),
            'max_gap_us': max_gap, 'max_capture_us': max_duration, 'samples': checked}


def observe(display, environment, shell_pid, workspace, trace_function):
    journal = (workspace / 'composition.jsonl').open('x', encoding='utf-8', newline='\n')
    count, descriptor = 0, None
    def preserve(kind, value):
        nonlocal count
        count += 1
        if count > 160:
            raise ValueError('composition journal record capacity')
        journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
        journal.flush()
        if journal.tell() > 8 * 1024**2:
            raise ValueError('composition journal byte capacity')
    try:
        key = display.x.XKeysymToKeycode(display.handle, display.x.XStringToKeysym(b'Escape'))
        if not key:
            raise ValueError('native Escape unavailable')
        for pressed in (True, False):
            if not display.xtest.XTestFakeKeyEvent(display.handle, key, pressed, 0):
                raise ValueError('native Escape failed')
        display.x.XFlush(display.handle)
        time.sleep(.3)
        preserve('initial_desktop', rgb_record(display.capture(0, 0, 800, 600)))
        deadline = time.monotonic() + 5
        last_error = 'icon window absent'
        while time.monotonic() < deadline:
            owner = bind_icon_window(display, shell_pid, workspace)
            if owner:
                baseline = display.capture(*FIXTURE['overlap'])
                try:
                    masks(baseline)
                    break
                except ValueError as error:
                    last_error = str(error)
            time.sleep(.05)
        else:
            preserve('failed_desktop', rgb_record(display.capture(0, 0, 800, 600)))
            raise TimeoutError('DING prerequisite: ' + last_error)
        descriptor = os.pidfd_open(owner['pid'])
        poller = select.poll()
        poller.register(descriptor, select.POLLIN)
        if poller.poll(0):
            raise ValueError('icon manager exited before observation')
        result = {'version': '0.2.0', 'fixture_sha256': hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
                  'control': environment['SYSPANE_GNOME_COMPOSITION'], 'icon_manager': owner,
                  'baseline': [], 'calibrations': [], 'overlap_samples': []}
        preserve('identity', {k: v for k, v in result.items() if k not in ('baseline', 'overlap_samples', 'calibrations')})
        calibration_pixels = []
        for color in FIXTURE['transparency_backgrounds'] + [FIXTURE['background_rgb']]:
            value = "'#" + ''.join(f'{c:02x}' for c in color) + "'"
            subprocess.run(['/usr/bin/gsettings', 'set', 'org.gnome.desktop.background', 'primary-color', value],
                           env=environment, capture_output=True, timeout=1, check=True)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                witness = display.capture(*FIXTURE['background_witness'])
                if witness == bytes(color) * (128 * 96):
                    break
                time.sleep(.05)
            else:
                raise TimeoutError('independent calibration background did not become visible')
            frames = []
            for index in range(3):
                if index:
                    time.sleep(.1)
                at = time.monotonic_ns()
                pixels = display.capture(*FIXTURE['overlap'])
                row = {'started_ns': at, 'finished_ns': time.monotonic_ns(), 'pixels': rgb_record(pixels)}
                frames.append(row)
                preserve('calibration_frame', {'background': color, 'frame': row})
                if index and pixels != first_pixels:
                    raise ValueError('native calibration frame changed')
                first_pixels = pixels
            result['calibrations'].append({'background': color, 'background_witness': rgb_record(witness), 'frames': frames})
            if color != FIXTURE['background_rgb']:
                calibration_pixels.append(first_pixels)
            else:
                baseline = first_pixels
        result['background_settings_before'] = settings(environment)
        masks(baseline, calibration_pixels)
        for index in range(3):
            if index:
                time.sleep(.1)
            at = time.monotonic_ns()
            pixels = display.capture(*FIXTURE['overlap'])
            row = {'started_ns': at, 'finished_ns': time.monotonic_ns(), 'pixels': rgb_record(pixels)}
            result['baseline'].append(row)
            preserve('baseline', row)
            if pixels != baseline:
                raise ValueError('native icon baseline is unstable')
        response = subprocess.run(['/usr/bin/gdbus', 'call', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
                                   '--dest', 'org.gnome.Shell', '--object-path', '/org/syspane/LabMarker',
                                   '--method', 'org.syspane.LabMarker.SetSceneEnabled', 'true'],
                                  env=environment, capture_output=True, text=True, timeout=1, check=True)
        if response.stdout.strip() != '()':
            raise ValueError('scene enable reply')
        result['scene_enabled_ns'] = time.monotonic_ns()
        preserve('scene_enabled', {'reply': response.stdout.strip(), 'at_ns': result['scene_enabled_ns']})
        def sample(frame, now):
            started = now()
            pixels = display.capture(*FIXTURE['overlap'])
            row = {'marker_start_us': frame['start_us'], 'start_us': started,
                   'end_us': now(), 'pixels': rgb_record(pixels)}
            result['overlap_samples'].append(row)
            preserve('sample', {'marker': frame, 'overlap': row})
            if poller.poll(0):
                raise ValueError('icon manager exited during trace')
        result['marker'] = trace_function(display, environment, sample=sample, dismiss=False)
        result['background_settings_after'] = settings(environment)
        if result['background_settings_before'] != result['background_settings_after']:
            raise ValueError('background settings changed during composition')
        if bind_icon_window(display, shell_pid, workspace) != owner or poller.poll(0):
            raise ValueError('icon manager lifetime changed')
        result['evaluation'] = judge_samples(baseline, result['overlap_samples'], calibration_pixels)
        results = [result['marker']['evaluation']['outcome'], result['evaluation']['icons'], result['evaluation']['rectangle']]
        result['outcome'] = 'pass' if all(x == 'pass' for x in results) else 'fail'
        preserve('completed', {'outcome': result['outcome'], 'evaluation': result['evaluation'],
                               'background_settings_after': result['background_settings_after']})
        return result
    except Exception as error:
        preserve('error', {'message': type(error).__name__ + ': ' + str(error)})
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        journal.close()

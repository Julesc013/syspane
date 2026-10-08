"""Native dconf wallpaper locks on the explicitly owned GNOME laboratory."""
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time

from native_oracle import ROOT
from native_x11_host import rgb_record
from gnome_composition import FIXTURE, judge_samples, bind_icon_window
from gnome_wallpaper import file_pair, settings, parse_settings
from oracle import evaluate

CONTROLS = ['locked', 'unlocked', 'replace-policy']
KEYS = ['picture-uri', 'picture-uri-dark', 'picture-options']
DEFAULTS = "[org/gnome/desktop/background]\npicture-uri=''\npicture-uri-dark=''\npicture-options='none'\n"
LOCKS = ''.join('/org/gnome/desktop/background/' + key + '\n' for key in KEYS)


def prepare(workspace, environment, build, mode):
    from prepare_gnome_lab import inventory, sha
    runtime = build / 'gnome-policy-runtime'
    lock_path = ROOT / 'source/build/gnome-policy-runtime.json'
    lock = json.loads(lock_path.read_text())
    identity = json.loads((runtime / 'identity.json').read_text())
    if identity['lock_sha256'] != sha(lock_path) or identity['files'] != inventory(runtime / 'sysroot'):
        raise ValueError('pinned policy CLI identity differs')
    if any(sha(Path(p)) != digest for p, digest in lock['system_files'].items()):
        raise ValueError('pinned native dconf files differ')
    root = workspace / 'wallpaper-policy'
    root.mkdir(mode=0o700)
    source = root / 'policy.d'
    source.mkdir()
    (source / 'defaults').write_text(DEFAULTS)
    (source / 'locks').mkdir()
    (source / 'locks/keys').write_text('' if mode == 'unlocked' else LOCKS)
    user_source = root / 'user.d'
    user_source.mkdir()
    (user_source / 'initial').write_bytes((workspace / 'config/glib-2.0/settings/keyfile').read_bytes())
    (workspace / 'config/dconf').mkdir()
    commands = []
    for target, inputs in [(root / 'policy', source), (workspace / 'config/dconf/user', user_source)]:
        command = [str(runtime / 'sysroot/usr/bin/dconf'), 'compile', str(target), str(inputs)]
        response = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=2)
        commands.append({'command': command, 'exit': response.returncode, 'stdout': response.stdout, 'stderr': response.stderr})
        response.check_returncode()
    profile = root / 'profile'
    profile.write_text('user-db:user\nfile-db:' + str(root / 'policy') + '\n')
    (root / 'policy').chmod(0o444)
    profile.chmod(0o444)
    (root / 'sentinel').write_text('owned URI write control\n')
    environment['GSETTINGS_BACKEND'] = 'dconf'
    environment['DCONF_PROFILE'] = str(profile)
    environment['SYSPANE_GNOME_WALLPAPER_POLICY'] = mode
    return {'lock_sha256': sha(lock_path), 'runtime_identity_sha256': sha(runtime / 'identity.json'),
            'system_files': lock['system_files'], 'commands': commands, 'inputs': inventory(root)}


def command(environment, arguments):
    call = ['/usr/bin/gsettings', *arguments]
    started = time.monotonic_ns()
    response = subprocess.run(call, env=environment, capture_output=True, text=True, timeout=2)
    if len(response.stdout.encode()) + len(response.stderr.encode()) > 8192:
        raise ValueError('native settings command capacity')
    return {'command': call, 'started_ns': started, 'finished_ns': time.monotonic_ns(),
            'exit': response.returncode, 'stdout': response.stdout, 'stderr': response.stderr}


def writable(environment):
    return {key: command(environment, ['writable', 'org.gnome.desktop.background', key]) for key in KEYS}


def judge(result, composition):
    from record_gnome_host import rgb
    mode = result['control']
    if mode not in CONTROLS:
        raise ValueError('wallpaper policy mode')
    marker = result['marker']
    mark = evaluate(marker['trace'])
    if marker['evaluation'] != mark or marker['trace']['end_us'] != 2400000 or [s['generation'] for s in marker['trace']['stimuli']] != [1, 2, 3]:
        raise ValueError('original policy marker oracle differs')
    samples = result['samples']
    if len(samples) != len(marker['trace']['frames']):
        raise ValueError('missing paired policy observations')
    captures, checks = [], []
    background = bytes(FIXTURE['background_rgb']) * 128 * 96
    for frame, row in zip(marker['trace']['frames'], samples):
        if not frame['start_us'] <= frame['end_us'] <= row['start_us'] <= row['files_started_us'] <= row['end_us']:
            raise ValueError('paired policy observation order')
        captures.append({'marker_start_us': frame['start_us'], 'start_us': row['start_us'], 'end_us': row['end_us'], 'pixels': row['overlap']})
        checks.append({'at_us': frame['start_us'], 'end_us': row['end_us'],
                       'files': row['files'] == result['files_before'],
                       'background': rgb(row['background'], len(background)) == background})
    calibration = [rgb(s['frames'][0]['pixels'], 180 * 220 * 3) for s in composition['calibrations']]
    comp = judge_samples(calibration[2], captures, calibration[:2])
    records = [r for phase in ['writable_before', 'writable_after'] for r in result[phase].values()]
    locks = all(r['exit'] == 0 and r['stdout'] == 'false\n' and not r['stderr'] for r in records)
    initial = parse_settings(result['settings_before']['stdout'])
    settings_ok = all(parse_settings(result[p]['stdout']) == initial for p in ['settings_after_write', 'settings_after'])
    files = all(c['files'] for c in checks) and result['files_after'] == result['files_before']
    pixels = all(c['background'] for c in checks) and all(rgb(marker[p], len(background)) == background for p in ['background_before', 'background_after'])
    write_denied = result['write']['exit'] != 0
    return {'marker': mark, 'composition': comp, 'locks': 'pass' if locks and write_denied else 'fail',
            'settings': 'pass' if settings_ok else 'fail', 'files': 'pass' if files else 'fail',
            'background': 'pass' if pixels else 'fail', 'checks': checks,
            'outcome': 'pass' if locks and write_denied and settings_ok and files and pixels and mark['outcome'] == comp['icons'] == comp['rectangle'] == 'pass' else 'fail'}


def observe(display, environment, shell_pid, workspace, composition, trace_function):
    root = workspace / 'wallpaper-policy'
    journal = (workspace / 'wallpaper-policy.jsonl').open('x', encoding='utf-8', newline='\n')
    descriptors = {}
    icon = None
    count = 0
    def preserve(kind, value):
        nonlocal count
        count += 1
        if count > 180:
            raise ValueError('policy journal record capacity')
        journal.write(json.dumps({'kind': kind, 'value': value}, separators=(',', ':')) + '\n')
        journal.flush()
        if journal.tell() > 8 * 1024**2:
            raise ValueError('policy journal capacity')
    def snapshots():
        result = {name: file_pair(root / name, descriptor) for name, descriptor in descriptors.items()}
        if any(pair['path']['bytes'] > 65536 or pair['held']['bytes'] > 65536 for pair in result.values()):
            raise ValueError('policy file capacity')
        return result
    try:
        if composition['outcome'] != 'pass':
            raise ValueError('live composition prerequisite')
        mode = environment['SYSPANE_GNOME_WALLPAPER_POLICY']
        for name in ['profile', 'policy']:
            descriptors[name] = os.open(root / name, os.O_RDONLY | os.O_NOFOLLOW)
        owner = composition['icon_manager']
        icon = os.pidfd_open(owner['pid'])
        poller = select.poll()
        poller.register(icon, select.POLLIN)
        result = {'version': '0.1.0', 'control': mode, 'icon_manager': owner,
                  'files_before': snapshots(), 'settings_before': settings(environment),
                  'writable_before': writable(environment), 'samples': [], 'faults': []}
        preserve('initial', {k: v for k, v in result.items() if k not in ['samples', 'faults']})
        result['writer_get_before'] = command(environment, ['get', 'org.gnome.desktop.interface', 'clock-show-seconds'])
        target = 'false' if result['writer_get_before']['stdout'] == 'true\n' else 'true'
        result['writer_set'] = command(environment, ['set', 'org.gnome.desktop.interface', 'clock-show-seconds', target])
        result['writer_get_after'] = command(environment, ['get', 'org.gnome.desktop.interface', 'clock-show-seconds'])
        if result['writer_set']['exit'] or result['writer_get_after']['stdout'] != target + '\n':
            raise ValueError('private dconf writer unavailable')
        result['write'] = command(environment, ['set', 'org.gnome.desktop.background', 'picture-uri', repr((root / 'sentinel').as_uri())])
        result['settings_after_write'] = settings(environment)
        preserve('writes', {k: result[k] for k in ['writer_get_before', 'writer_set', 'writer_get_after', 'write', 'settings_after_write']})
        def sample(frame, now):
            if mode == 'replace-policy' and not result['faults'] and now() >= 1000000:
                fault = {'kind': mode, 'start_us': now()}
                replacement = root / 'replacement'
                with replacement.open('xb') as stream:
                    stream.write(os.pread(descriptors['policy'], 65536, 0))
                    stream.flush()
                    os.fsync(stream.fileno())
                replacement.chmod(0o444)
                os.replace(replacement, root / 'policy')
                fault['end_us'] = now()
                result['faults'].append(fault)
                preserve('fault', fault)
            row = {'start_us': now(), 'overlap': rgb_record(display.capture(*FIXTURE['overlap'])),
                   'background': rgb_record(display.capture(600, 400, 128, 96))}
            row['files_started_us'] = now()
            row['files'] = snapshots()
            row['end_us'] = now()
            result['samples'].append(row)
            preserve('sample', {'marker': frame, 'observation': row})
            if poller.poll(0):
                raise ValueError('icon manager exited during policy observation')
        result['marker'] = trace_function(display, environment, sample=sample, dismiss=False)
        result['files_after'] = snapshots()
        result['settings_after'] = settings(environment)
        result['writable_after'] = writable(environment)
        if poller.poll(0) or bind_icon_window(display, shell_pid, workspace) != owner:
            raise ValueError('native icon owner changed')
        result['evaluation'] = judge(result, composition)
        preserve('completed', {k: v for k, v in result.items() if k != 'samples'})
        return result
    except Exception as error:
        preserve('error', {'message': type(error).__name__ + ': ' + str(error)})
        raise
    finally:
        for descriptor in [*descriptors.values(), icon]:
            if descriptor is not None:
                os.close(descriptor)
        journal.close()

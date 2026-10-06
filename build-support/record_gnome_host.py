"""Recompute the owned GNOME marker calibration from source-bound native records."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/desktop'))
from oracle import evaluate


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rgb(value, size):
    if set(value) != {'bytes', 'sha256', 'rgb_zlib_base64'} or value['bytes'] != size:
        raise ValueError('RGB record shape')
    encoded = value['rgb_zlib_base64']
    if len(encoded) > size * 2:
        raise ValueError('RGB encoded capacity')
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(encoded, validate=True), size + 1)
    if len(raw) != size or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or digest(raw) != value['sha256']:
        raise ValueError('RGB record content')
    return raw


def validate_runtime(value, build, family, prefix, shell_exit=None):
    if value['family'] != family or value.get('error'):
        raise ValueError('completed native record required')
    workspace = Path(value['workspace']).resolve(strict=True)
    if workspace.parent != build or not workspace.name.startswith(prefix):
        raise ValueError('owned workspace required')
    archive = Path(value['source_archive']['path']).resolve(strict=True)
    if archive.parent != workspace or archive.name != 'source-inputs.zip':
        raise ValueError('source archive path')
    archive_bytes = archive.read_bytes()
    if len(archive_bytes) != value['source_archive']['bytes'] or digest(archive_bytes) != value['source_archive']['sha256']:
        raise ValueError('source archive identity')
    with zipfile.ZipFile(archive) as source:
        if set(source.namelist()) != set(value['source_inputs']) or len(source.namelist()) != len(value['source_inputs']):
            raise ValueError('source archive members')
        for name, expected in value['source_inputs'].items():
            if digest(source.read(name)) != expected:
                raise ValueError('source archive byte identity')
    identity = build / 'gnome-lab/identity.json'
    if digest(identity.read_bytes()) != value['lab_identity_sha256']:
        raise ValueError('runtime identity')
    observation = value['observation']
    if observation['outcome'] != 'pass':
        raise ValueError('native observation incomplete')
    controlled = family == 'GNOME-CONTROLLER-RECOVERY-01'
    if controlled:
        from record_gnome_controller_recovery import controller_lifetimes
        raw, _ = controller_lifetimes(value, build)
        identities = [raw['identities']['old_shell']]
        if raw['mode'] != 'revoke':
            identities.append(raw['identities']['new_shell'])
        shell = [{'pid': row['pid'], 'command': row['arguments']} for row in identities]
    else:
        shell = [c for c in value['commands'] if c['command'][0].endswith('/usr/bin/gnome-shell')]
    recovering = shell_exit is not None
    if recovering and (family != 'GNOME-SHELL-RECOVERY-01' or shell_exit.get('event') != 'shell-exit' or
                       shell_exit.get('observer') != 'pidfd' or shell_exit.get('readable') is not True):
        raise ValueError('only explicit shell recovery admits independently observed shell exit')
    expected_shells = (1 if raw['mode'] == 'revoke' else 2) if controlled else (1 if not recovering or value['shell_recovery_control'] == 'no-restart' else 2)
    if len(shell) != expected_shells or (recovering and shell_exit['pid'] != shell[0]['pid']):
        raise ValueError('shell command identity')
    if len(shell) == 2 and (shell[1]['command'] != shell[0]['command'] or shell[1]['pid'] == shell[0]['pid']):
        raise ValueError('replacement must use identical command and distinct native child')
    manager = observation['manager']
    if manager['pid'] != [shell[0]['pid']] or manager['self'] != [manager['window']] or manager['pid_origin'] != 'XResQueryClientIds' or manager['window'] & ~manager['resource_mask'] != manager['resource_base']:
        raise ValueError('native manager binding')
    environment = value['environment']['explicit']
    for key, directory in [('HOME', 'home'), ('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'), ('XDG_RUNTIME_DIR', 'run')]:
        if environment[key] != str(workspace / directory):
            raise ValueError('owned environment differs')
    phases = ['bus', 'system-bus', 'controller', 'observer', 'Xvfb'] if controlled else ['bus', 'system-bus', 'shell', 'observer', 'Xvfb'] + (['shell-replacement'] if len(shell) == 2 else [])
    for phase in phases:
        rows = [r for r in value['cleanup'] if r['process'] == phase]
        expected_exit = -9 if phase == 'shell' and recovering else 0
        if len(rows) != 1 or rows[0]['exit'] != expected_exit or rows[0].get('members_after_stop', []):
            raise ValueError('owned process exit unconfirmed')
    frames = observation['frames']
    if len(frames) != 3:
        raise ValueError('bootstrap frame count')
    previous = 0
    for frame in frames:
        if frame['origin'] != 'display_server_root' or not previous <= frame['capture_started_ns'] <= frame['capture_finished_ns']:
            raise ValueError('bootstrap capture provenance/time')
        rgb(frame['pixels'], 800 * 600 * 3)
        previous = frame['capture_finished_ns']
    return observation


def validate(value, build):
    observation = validate_runtime(value, build, 'GNOME-MARKER-01', 'GNOME-MARKER-01-')
    control = value['marker_control']
    if control not in {'live', 'hidden', 'frozen'} or value['environment']['explicit']['SYSPANE_GNOME_MARKER_CONTROL'] != control:
        raise ValueError('control identity/environment')
    marker = observation['marker']
    result = evaluate(marker['trace'])
    if marker['evaluation'] != result or value['outcome'] != result['outcome']:
        raise ValueError('claimed marker result differs from raw evidence')
    if marker['trace']['end_us'] != 2400000 or [s['generation'] for s in marker['trace']['stimuli']] != [1, 2, 3]:
        raise ValueError('marker scenario changed')
    if any(reason.startswith('capture.') for reason in result['uncertainty']):
        raise ValueError('capture coverage cannot calibrate a control')
    expected = 'pass' if control == 'live' else 'fail'
    if result['outcome'] != expected:
        raise ValueError('control produced an unexpected result')
    if control == 'hidden' and 'marker.absent_or_invalid' not in result['failures']:
        raise ValueError('hidden control did not expose absence')
    if control == 'frozen' and ('generation.deadline' not in result['failures'] or result['observed_generations'] != ['1']):
        raise ValueError('frozen control did not expose stale generation')
    background = rgb(marker['background_before'], 128 * 96 * 3)
    if background != bytes((48, 72, 96)) * 128 * 96 or rgb(marker['background_after'], len(background)) != background:
        raise ValueError('synthetic background witness changed')
    rgb(marker['final_desktop'], 800 * 600 * 3)
    return {'control': control, 'candidate_outcome': result['outcome'], 'expected_outcome': expected,
            'failures': result['failures'], 'uncertainty': result['uncertainty'],
            'samples': result['samples'], 'max_gap_us': result['max_gap_us'],
            'max_capture_us': result['max_capture_us'], 'observed_generations': result['observed_generations'],
            'background_witness': 'unchanged exact synthetic color', 'process_cleanup': 'confirmed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--reports', nargs=3, required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    results, identities = [], []
    for path in args.reports:
        path = path.resolve(strict=True)
        if path.parent != build / 'native-evidence' or path.stat().st_size > 16 * 1024**2:
            raise ValueError('owned bounded native report required')
        raw = path.read_bytes()
        value = json.loads(raw)
        results.append(validate(value, build))
        identities.append({'path': str(path), 'sha256': digest(raw), 'source_base': value['source_base'],
                           'source_inputs': value['source_inputs']})
    if sorted(r['control'] for r in results) != ['frozen', 'hidden', 'live'] or any(r['source_inputs'] != identities[0]['source_inputs'] for r in identities):
        raise ValueError('three controls must use identical source inputs')
    for path, expected in identities[0]['source_inputs'].items():
        if digest((ROOT / path).read_bytes()) != expected:
            raise ValueError('current source differs from calibration: ' + path)
    output = args.output.resolve()
    if output.parent != build / 'native-evidence':
        raise ValueError('output must be an owned evidence record')
    record = {'version': '0.1.0', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'outcome': 'pass', 'scope': 'GNOME 46 owned bootstrap and temporal marker calibration',
              'reports': identities, 'results': results,
              'recorder_inputs': {p: digest((ROOT / p).read_bytes()) for p in ['build-support/record_gnome_host.py', 'tests/desktop/oracle.py']},
              'not_run': ['icon composition', 'native reveal', 'input routing', 'wallpaper policy', 'shell recovery', 'Wayland', 'product desktop qualification']}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record['results'], indent=2))


if __name__ == '__main__':
    main()

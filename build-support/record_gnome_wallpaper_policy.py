"""Verify native wallpaper locks separately from settings, policy files and pixels."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest, rgb
from record_gnome_composition import validate as composition
from record_gnome_focus import raw_file
from record_gnome_wallpaper import SETTINGS_KEYS
from prepare_gnome_lab import inventory, sha
from gnome_wallpaper_policy import CONTROLS, KEYS, DEFAULTS, LOCKS, judge
from gnome_wallpaper import parse_settings


def validate(value, build):
    if composition(value, build, family='GNOME-WALLPAPER-POLICY-01', outer_outcome=False)['outcome'] != 'pass':
        raise ValueError('live policy composition prerequisite')
    result = value['observation']['wallpaper_policy']
    mode = result['control']
    workspace = Path(value['workspace'])
    root = workspace / 'wallpaper-policy'
    env = value['environment']['explicit']
    if result['version'] != '0.1.0' or mode not in CONTROLS or value['wallpaper_policy_control'] != mode or env.get('SYSPANE_GNOME_WALLPAPER_POLICY') != mode:
        raise ValueError('policy control identity')
    if env['GSETTINGS_BACKEND'] != 'dconf' or env.get('DCONF_PROFILE') != str(root / 'profile'):
        raise ValueError('owned native dconf profile required')
    setup = value['wallpaper_policy_setup']
    runtime = build / 'gnome-policy-runtime'
    lock_path = ROOT / 'build-support/gnome-policy-runtime.json'
    lock = json.loads(lock_path.read_text())
    if setup['lock_sha256'] != sha(lock_path) or setup['runtime_identity_sha256'] != sha(runtime / 'identity.json') or setup['system_files'] != lock['system_files']:
        raise ValueError('policy runtime provenance differs')
    if any(sha(Path(p)) != h for p, h in setup['system_files'].items()):
        raise ValueError('current native policy runtime differs')
    if json.loads((runtime / 'identity.json').read_text())['files'] != inventory(runtime / 'sysroot'):
        raise ValueError('compiled policy tool identity differs')
    inputs = setup['inputs']
    expected = {'policy.d/defaults': DEFAULTS.encode(), 'policy.d/locks/keys': ('' if mode == 'unlocked' else LOCKS).encode(),
                'profile': ('user-db:user\nfile-db:' + str(root / 'policy') + '\n').encode(),
                'sentinel': b'owned URI write control\n'}
    if set(inputs) != {*expected, 'policy', 'user.d/initial'} or inputs != value['wallpaper_policy_inputs_after'] or inventory(root) != inputs:
        raise ValueError('private policy setup/artifact set differs')
    for name, data in expected.items():
        if (root / name).read_bytes() != data or inputs[name] != {'bytes': len(data), 'sha256': digest(data)}:
            raise ValueError('native profile/default/locks bytes differ')
    commands = setup['commands']
    calls = [[str(runtime / 'sysroot/usr/bin/dconf'), 'compile', str(target), str(source)] for target, source in
             [(root / 'policy', root / 'policy.d'), (workspace / 'config/dconf/user', root / 'user.d')]]
    if len(commands) != 2 or any(r != {'command': call, 'exit': 0, 'stdout': '', 'stderr': ''} for r, call in zip(commands, calls)):
        raise ValueError('native compile recipe/result differs')
    writer = [r for r in value['commands'] if r['command'] == ['/usr/libexec/dconf-service']]
    cleanup = [r for r in value['cleanup'] if r['process'] == 'dconf-writer']
    if len(writer) != 1 or len(cleanup) != 1 or writer[0]['pid'] != value['wallpaper_policy_writer_pid'] or cleanup[0]['pid'] != writer[0]['pid'] or cleanup[0]['exit'] != 0 or cleanup[0]['members_after_stop']:
        raise ValueError('private native writer ownership/cleanup differs')
    if not any(r['pid'] == writer[0]['pid'] and r['state'] != 'Z' for r in cleanup[0]['members_before_stop']):
        raise ValueError('native writer not retained')
    mapped = value['wallpaper_policy_mapped_files']
    if mapped.get('/usr/libexec/dconf-service') != lock['system_files']['/usr/libexec/dconf-service']:
        raise ValueError('native writer mapped executable differs')
    if result['icon_manager'] != value['observation']['composition']['icon_manager']:
        raise ValueError('native icon lifetime differs')
    before = result['files_before']
    if set(before) != {'profile', 'policy'}:
        raise ValueError('policy identity set differs')
    for name, pair in before.items():
        old = pair['path']
        if pair['held'] != old or old['mode'] != 0o444 or old['uid'] != value['environment']['uid'] or old['links'] != 1 or not 0 < old['bytes'] <= 65536 or old['bytes'] != inputs[name]['bytes'] or old['sha256'] != inputs[name]['sha256']:
            raise ValueError('initial policy file identity differs')
    initial = parse_settings(result['settings_before']['stdout'])
    required = {'picture-uri': "''", 'picture-uri-dark': "''", 'picture-options': "'none'", 'primary-color': "'#304860'", 'color-shading-type': "'solid'"}
    if set(initial) != SETTINGS_KEYS or any(initial[k] != v for k, v in required.items()):
        raise ValueError('complete native background baseline differs')
    target_uri = repr((root / 'sentinel').as_uri())
    after = {**initial, 'picture-uri': target_uri} if mode == 'unlocked' else initial
    for key, expected_values in [('settings_before', initial), ('settings_after_write', after), ('settings_after', after)]:
        raw = parse_settings(result[key]['stdout'])
        if raw != expected_values or result[key]['values'] != raw:
            raise ValueError('native background settings differ from control')
    previous = value['observation']['composition']['marker']['started_monotonic_ns'] + 2400000000
    def check_command(row, call, code, stdout, stderr=''):
        nonlocal previous
        if row['command'] != ['/usr/bin/gsettings', *call] or row['exit'] != code or row['stdout'] != stdout or row['stderr'] != stderr:
            raise ValueError('native policy command/result differs')
        if not previous <= row['started_ns'] <= row['finished_ns'] <= row['started_ns'] + 2000000000:
            raise ValueError('native policy command order/bound differs')
        previous = row['finished_ns']
    for phase in ['writable_before', 'writable_after']:
        if set(result[phase]) != set(KEYS):
            raise ValueError('native writability keys incomplete')
        if phase == 'writable_after':
            previous = result['marker']['started_monotonic_ns'] + 2400000000
        for key in KEYS:
            check_command(result[phase][key], ['writable', 'org.gnome.desktop.background', key], 0, 'true\n' if mode == 'unlocked' else 'false\n')
        if phase == 'writable_before':
            prior = result['writer_get_before']['stdout']
            if prior not in ['true\n', 'false\n']:
                raise ValueError('native writer baseline missing')
            target = 'false' if prior == 'true\n' else 'true'
            check_command(result['writer_get_before'], ['get', 'org.gnome.desktop.interface', 'clock-show-seconds'], 0, prior)
            check_command(result['writer_set'], ['set', 'org.gnome.desktop.interface', 'clock-show-seconds', target], 0, '')
            check_command(result['writer_get_after'], ['get', 'org.gnome.desktop.interface', 'clock-show-seconds'], 0, target + '\n')
            check_command(result['write'], ['set', 'org.gnome.desktop.background', 'picture-uri', target_uri], 0 if mode == 'unlocked' else 1, '', '' if mode == 'unlocked' else 'The key is not writable\n')
            if previous >= result['marker']['started_monotonic_ns']:
                raise ValueError('policy write must precede measured interval')
    actual = judge(result, value['observation']['composition'])
    if result['evaluation'] != actual or value['outcome'] != actual['outcome']:
        raise ValueError('native policy claim differs from raw evidence')
    required = {'locks': 'fail' if mode == 'unlocked' else 'pass', 'settings': 'fail' if mode == 'unlocked' else 'pass',
                'files': 'fail' if mode == 'replace-policy' else 'pass', 'background': 'pass'}
    if any(actual[k] != v for k, v in required.items()) or actual['marker']['outcome'] != actual['composition']['icons'] or actual['marker']['outcome'] != actual['composition']['rectangle'] or actual['marker']['outcome'] != 'pass':
        raise ValueError('policy control is not isolated to intended dimension')
    for stimulus, scheduled in zip(result['marker']['trace']['stimuli'], [0, 800000, 1600000]):
        if not scheduled <= stimulus['at_us'] <= scheduled + 50000:
            raise ValueError('policy marker schedule differs')
    faults = result['faults']
    if len(faults) != (1 if mode == 'replace-policy' else 0):
        raise ValueError('policy fault count')
    if faults:
        fault = faults[0]
        if fault['kind'] != mode or not 1000000 <= fault['start_us'] <= 1050000 or not fault['start_us'] <= fault['end_us'] <= fault['start_us'] + 50000:
            raise ValueError('native policy replacement scheduling differs')
        earlier = [r for r in actual['checks'] if r['end_us'] < fault['start_us']]
        later = [row for row, check in zip(result['samples'], actual['checks']) if check['at_us'] >= fault['end_us'] + 200000]
        if len(earlier) < 3 or not all(c['files'] for c in earlier) or len(later) < 3:
            raise ValueError('native replacement transition coverage')
        old = before['policy']['held']
        stable = ['device', 'mode', 'uid', 'bytes', 'sha256']
        for row in later + [{'files': result['files_after']}]:
            pair = row['files']['policy']
            if row['files']['profile'] != before['profile'] or any(pair['held'][k] != old[k] or pair['path'][k] != old[k] for k in stable) or pair['held']['inode'] != old['inode'] or pair['held']['mtime_ns'] != old['mtime_ns'] or pair['held']['links'] != 0 or pair['path']['inode'] == old['inode'] or pair['path']['links'] != 1:
                raise ValueError('identical-byte native replacement lifetime differs')
    records = [json.loads(line) for line in raw_file(value, 'wallpaper_policy_journal', workspace, 'wallpaper-policy.jsonl', 8 * 1024**2).splitlines()]
    expected_records = [{'kind': 'initial', 'value': {k: result[k] for k in ['version', 'control', 'icon_manager', 'files_before', 'settings_before', 'writable_before']}},
                        {'kind': 'writes', 'value': {k: result[k] for k in ['writer_get_before', 'writer_set', 'writer_get_after', 'write', 'settings_after_write']}}]
    fault_added = False
    for frame, row in zip(result['marker']['trace']['frames'], result['samples']):
        if faults and not fault_added and row['start_us'] >= faults[0]['end_us']:
            expected_records.append({'kind': 'fault', 'value': faults[0]})
            fault_added = True
        expected_records.append({'kind': 'sample', 'value': {'marker': frame, 'observation': row}})
    expected_records.append({'kind': 'completed', 'value': {k: v for k, v in result.items() if k != 'samples'}})
    if records != expected_records or len(records) > 180:
        raise ValueError('native policy raw journal differs')
    return {'control': mode, 'outcome': actual['outcome'], **required, 'marker': 'pass', 'icons': 'pass',
            'samples': len(result['samples']), 'max_gap_us': actual['composition']['max_gap_us'],
            'max_observation_us': actual['composition']['max_capture_us'], 'cleanup': 'confirmed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--reports', required=True, nargs=3, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    results, identities = [], []
    for path in args.reports:
        path = path.resolve(strict=True)
        if path.parent != build / 'native-evidence' or path.stat().st_size > 16 * 1024**2:
            raise ValueError('owned bounded policy report required')
        raw = path.read_bytes()
        value = json.loads(raw)
        results.append(validate(value, build))
        identities.append({'path': str(path), 'sha256': digest(raw), 'source_base': value['source_base'], 'source_inputs': value['source_inputs'],
                           'runtime': [value['lab_identity_sha256'], value['wallpaper_policy_setup']['runtime_identity_sha256'], value['environment']['uid']]})
    if sorted(r['control'] for r in results) != sorted(CONTROLS) or any(r['source_inputs'] != identities[0]['source_inputs'] or r['runtime'] != identities[0]['runtime'] for r in identities):
        raise ValueError('three source/runtime-identical controls required')
    if any(digest((ROOT / p).read_bytes()) != h for p, h in identities[0]['source_inputs'].items()):
        raise ValueError('current native source differs')
    output = args.output.resolve()
    if output.parent != build / 'native-evidence':
        raise ValueError('owned output required')
    scripts = ['build-support/record_gnome_wallpaper_policy.py', 'build-support/record_gnome_composition.py', 'build-support/record_gnome_host.py',
               'build-support/record_gnome_focus.py', 'build-support/record_gnome_wallpaper.py', 'build-support/prepare_gnome_lab.py',
               'tests/desktop/gnome_wallpaper_policy.py', 'tests/desktop/gnome_wallpaper.py', 'tests/desktop/gnome_composition.py', 'tests/desktop/oracle.py']
    record = {'version': '0.1.0', 'recorded_at': datetime.now(timezone.utc).isoformat(), 'outcome': 'pass',
              'scope': 'Named native dconf wallpaper locks, policy identity and live composition on the owned solid-color X11 fixture',
              'reports': identities, 'results': results, 'recorder_inputs': {p: digest((ROOT / p).read_bytes()) for p in scripts},
              'not_run': ['protected deployment', 'locked image wallpaper', 'live organization-policy updates', 'disclosure revocation', 'other profiles', 'full host qualification']}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
